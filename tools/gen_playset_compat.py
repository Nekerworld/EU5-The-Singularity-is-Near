"""Generate a local-only compatibility mod that carries the age 7 extension over the mods of a playset.

Usage:
  python tools/gen_playset_compat.py                   active playset in playsets.json
  python tools/gen_playset_compat.py --playset "NAME"
  python tools/gen_playset_compat.py --mods 3765374050 3610840019

The main mod's zzz_tsin_age7_* patches are copies of vanilla. When a playset mod changes one of those
objects, the vanilla-based patch wipes that change (docs/compat.md). For every object the playset
defines, this tool takes the definition that would win without this mod, applies the same rewrites as
tools/gen_age7_patches.py and writes it to a separate local mod whose files sort after zzz_tsin_age7_*:

  replace  objects the main mod re-defines, and playset objects that still check age 6
  inject   TRY_INJECT/INJECT blocks of playset mods into objects replaced above, replayed afterwards

The output contains other authors' content. It is for the user's own playset only: never upload it.
Output: <mod folder>/The Singularity Is Near - Playset Compat/   Report: tools/out/playset_compat_report.md
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pdx  # noqa: E402
from compat_scan import playset_mods, split_mode  # noqa: E402
from gen_age7_patches import (  # noqa: E402
    AGE6, EXCLUDED_DIRS, EXCLUDED_FILES, PREFIX as MAIN_PREFIX, SCAN_DIRS,
    add_switch_branches, needs_patch, referenced_locals, rewrite_code,
)

COMPAT_NAME = "The Singularity Is Near - Playset Compat"
COMPAT_ID = "chris.the_singularity_is_near_playset_compat"
COMPAT_ROOT = pdx.MOD_ROOT.parent / COMPAT_NAME
REPLACE_PREFIX = "zzzz_tsin_compat_"
INJECT_FILE = "zzzzz_tsin_compat_injections.txt"
GENERATED_DIRS = ["in_game", "main_menu"]
# on_action blocks merge across files; replacing one would drop every other mod's hooks.
SKIP_DIRS = {"in_game/common/on_action"}
FULL_MODES = ("", "REPLACE", "TRY_REPLACE", "REPLACE_OR_CREATE")


@dataclass
class SourceFile:
    rel: str
    text: str
    local_defs: dict[str, pdx.Block]  # file-local scripted triggers/effects
    variables: dict[str, str]
    namespaces: list[str]


@dataclass
class Def:
    mod_index: int
    mod_name: str
    rel: str
    mode: str
    name: str
    block: pdx.Block
    src: SourceFile

    @property
    def order(self) -> tuple[str, int]:
        """Folder files load in file-name order; equal names fall back to the mod list."""
        return Path(self.rel).name.lower(), self.mod_index


def db_of(rel: str) -> str:
    parts = rel.split("/")
    return "in_game/events" if parts[:2] == ["in_game", "events"] else "/".join(parts[:3])


def mod_name(root: Path) -> str:
    meta = root / ".metadata" / "metadata.json"
    try:
        return json.loads(pdx.read_text(meta)).get("name") or root.name
    except (OSError, json.JSONDecodeError):
        return root.name


def main_mod_objects() -> tuple[set[tuple[str, str]], set[tuple[str, str]]]:
    """(vanilla copies in zzz_tsin_age7_* files, every other object the main mod defines or replaces)."""
    copies, own = set(), set()
    for p in pdx.iter_script_files(pdx.MOD_ROOT, SCAN_DIRS):
        rel = p.relative_to(pdx.MOD_ROOT).as_posix()
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            if b.local_kind:
                continue
            key = (db_of(rel), split_mode(b.key)[1])
            (copies if p.name.startswith(MAIN_PREFIX) else own).add(key)
    return copies, own


def collect(roots: list[Path], wanted: set[str]) -> tuple[dict, dict]:
    """Parse only files that check age 6, inject, or define an object named in `wanted`."""
    relevant = re.compile(r"age_6_revolutions|INJECT:|\b(?:" + "|".join(map(re.escape, sorted(wanted))) + r")\b")
    effective: dict[str, tuple[int, Path]] = {}
    for i, root in enumerate(roots):
        for p in pdx.iter_script_files(root, SCAN_DIRS):
            effective[p.relative_to(root).as_posix()] = (i, p)  # later mod replaces an equal path
    names = [mod_name(r) for r in roots]
    defs: dict[tuple[str, str], list[Def]] = defaultdict(list)
    injects: dict[tuple[str, str], list[Def]] = defaultdict(list)
    for rel, (i, p) in sorted(effective.items()):
        if rel in EXCLUDED_FILES or any(rel.startswith(d + "/") for d in EXCLUDED_DIRS | SKIP_DIRS):
            continue
        text = pdx.read_text(p)
        if not relevant.search(text):
            continue
        try:
            blocks = pdx.top_level_blocks(text)
        except Exception:  # noqa: BLE001
            continue
        src = SourceFile(rel, text, {b.key: b for b in blocks if b.local_kind}, pdx.file_variables(text),
                         pdx.namespaces(text) if rel.startswith("in_game/events/") else [])
        for b in blocks:
            if b.local_kind:
                continue
            mode, name = split_mode(b.key)
            d = Def(i, names[i], rel, mode, name, b, src)
            (defs if mode in FULL_MODES else injects)[(db_of(rel), name)].append(d)
    return defs, injects


def rewritten(d: Def, op: str) -> tuple[str, list[str], list[str], dict[str, str]]:
    """Rewritten block plus the namespaces, @variables and file-local blocks it needs."""
    main_menu = d.rel.startswith("main_menu/")
    local_defs = d.src.local_defs
    code = pdx.strip_comments(d.block.text)
    locals_out = {k: rewrite_code(local_defs[k].text, main_menu) for k in referenced_locals(code, local_defs)}
    body = d.block.text[len(d.block.key):]  # "= { ... }" without the original prefix
    body, _ = add_switch_branches(d.name + body)
    body = rewrite_code(body, main_menu)
    variables = d.src.variables
    used_vars = [f"{v} = {variables[v]}" for v in variables if re.search(re.escape(v) + r"\b", code)]
    return f"{op}:{body}", d.src.namespaces, used_vars, locals_out


def write_file(path: Path, source_note: list[str], items: list[tuple[str, list[str], list[str], dict[str, str]]]) -> None:
    header = [f"# GENERATED by tools/gen_playset_compat.py (The Singularity Is Near). Local use only, do not upload."]
    header += [f"# {n}" for n in source_note] + [""]
    namespaces = sorted({n for _, ns, _, _ in items for n in ns})
    variables = sorted({v for _, _, vs, _ in items for v in vs})
    local_blocks: dict[str, str] = {}
    for _, _, _, loc in items:
        local_blocks.update(loc)
    header += [f"namespace = {n}" for n in namespaces]
    header += variables
    body = "\n\n".join(list(local_blocks.values()) + [t for t, _, _, _ in items])
    pdx.write_text_bom(path, "\n".join(header) + "\n\n" + body + "\n")


def write_metadata(label: str) -> None:
    meta = {
        "name": COMPAT_NAME,
        "id": COMPAT_ID,
        "version": json.loads(pdx.read_text(pdx.MOD_ROOT / ".metadata" / "metadata.json"))["version"],
        "game_id": "eu5",
        "supported_game_version": "1.4.*",
        "short_description": f"LOCAL ONLY. Generated age 7 compatibility patch for the playset '{label}'. Contains other mods' content: do not upload.",
        "tags": ["Fixes"],
        "relationships": [],
        "game_custom_data": {},
    }
    (COMPAT_ROOT / ".metadata").mkdir(parents=True, exist_ok=True)
    (COMPAT_ROOT / ".metadata" / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (COMPAT_ROOT / "README.txt").write_text(
        "Generated by The Singularity Is Near/tools/gen_playset_compat.py.\n"
        "Local only: it contains content of other workshop mods. Do not upload it.\n"
        "Enable it together with The Singularity Is Near; re-run the tool after changing the playset or updating mods.\n",
        encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--playset")
    ap.add_argument("--mods", nargs="*")
    args = ap.parse_args()
    if args.mods:
        label = "mods " + " ".join(args.mods)
        roots = [Path(m) if Path(m).is_dir() else pdx.workshop_root() / m for m in args.mods]
    else:
        label, roots = playset_mods(args.playset)
    skip = {pdx.MOD_ROOT.resolve(), COMPAT_ROOT.resolve()}
    roots = [r for r in roots if r.exists() and r.resolve() not in skip]

    replaced_by_main, main_own = main_mod_objects()
    defs, injects = collect(roots, {name for _, name in replaced_by_main})

    replace_items: dict[str, list] = defaultdict(list)  # source rel -> items
    replace_notes: dict[str, set[str]] = defaultdict(set)
    replaced: set[tuple[str, str]] = set()
    report = [f"# 플레이셋 호환 패치: {label}", "", f"모드 {len(roots)}개, 출력 `{COMPAT_ROOT}`", "", "## 교체", ""]
    for key in sorted(defs):
        if key in main_own:
            report.append(f"- `{key[1]}` ({key[0]}): 본 모드가 의도적으로 바꾸는 객체라 건드리지 않음")
            continue
        winner = max(defs[key], key=lambda d: d.order)
        if key not in replaced_by_main:
            if AGE6 not in winner.src.text:
                continue
            local_defs = winner.src.local_defs
            code = pdx.strip_comments(winner.block.text)
            if not (needs_patch(code) or any(needs_patch(pdx.strip_comments(local_defs[k].text))
                                             for k in referenced_locals(code, local_defs))):
                continue
        op = "REPLACE" if key[0] == "in_game/events" else "TRY_REPLACE"
        replace_items[winner.rel].append(rewritten(winner, op))
        replace_notes[winner.rel].add(winner.mod_name)
        replaced.add(key)
        why = "본 모드 패치가 지우던 정의 복원" if key in replaced_by_main else "제6시대 검사 연장"
        report.append(f"- `{key[1]}` ({key[0]}) ← {winner.mod_name} `{winner.rel}`: {why}")

    inject_items: dict[str, list] = defaultdict(list)  # db -> items
    inject_notes: dict[str, set[str]] = defaultdict(set)
    report += ["", "## 다시 적용한 주입", ""]
    for key in sorted(injects):
        if key not in replaced and key not in replaced_by_main:
            continue
        for d in sorted(injects[key], key=lambda d: d.order):
            inject_items[key[0]].append(rewritten(d, d.mode))
            inject_notes[key[0]].add(f"{d.mod_name}: {d.rel}")
            report.append(f"- `{d.mode}:{key[1]}` ← {d.mod_name} `{d.rel}`")

    for sub in GENERATED_DIRS:
        if (COMPAT_ROOT / sub).exists():
            shutil.rmtree(COMPAT_ROOT / sub)
    for rel, items in replace_items.items():
        out = COMPAT_ROOT / Path(rel).parent / f"{REPLACE_PREFIX}{Path(rel).stem}.txt"
        write_file(out, [f"from {', '.join(sorted(replace_notes[rel]))}: {rel}"], items)
    for db, items in inject_items.items():
        write_file(COMPAT_ROOT / db / INJECT_FILE, sorted(inject_notes[db]), items)
    write_metadata(label)

    n_inject = sum(len(v) for v in inject_items.values())
    report.insert(4, f"교체 {len(replaced)}개, 주입 {n_inject}개")
    out_report = pdx.MOD_ROOT / "tools" / "out" / "playset_compat_report.md"
    out_report.parent.mkdir(parents=True, exist_ok=True)
    out_report.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"replaced {len(replaced)} objects in {len(replace_items)} files, re-applied {n_inject} injections")
    print(f"compat mod: {COMPAT_ROOT}")
    print(f"report: {out_report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
