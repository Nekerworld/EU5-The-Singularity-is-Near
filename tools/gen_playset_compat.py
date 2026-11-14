"""Generate a local-only compatibility mod that carries the age 7 extension over the mods of a playset.

Usage:
  python tools/gen_playset_compat.py                   active playset in playsets.json
  python tools/gen_playset_compat.py --playset "NAME"
  python tools/gen_playset_compat.py --mods 3765374050 3610840019

The main mod's zzz_tsin_age7_* patches are copies of vanilla. When a playset mod changes one of those
objects, the vanilla-based patch wipes that change (docs/compat.md). For every object the playset
defines, this tool takes the definition that would win without this mod, applies the same rewrites as
tools/gen_age7_patches.py and writes it to a separate local mod whose files sort after zzz_tsin_age7_*:

  replace  objects the main mod re-defines, playset objects that still check age 6, and playset objects
           that check a vanilla building replaced in age 7 (university -> tsin_research_university, ...)
  on_action  on_actions merge by key across files, so a file that needs those rewrites is copied whole
           to the same path (file override) instead of replacing the key
  inject   DLC and playset INJECT blocks into objects replaced above, replayed afterwards
  age      playset injects of AI privilege limits into age 6, carried over to age 7
  text     TEXT_PATCHES: small edits of named playset objects (setting ranges that end before 1837)
  gui      GUI_FIXES: winning .gui files that call data functions the game removed or renamed
  manual   tools/compat_manual/<profile>/{in_game,main_menu} copied over the generated files

Each playset gets its own output mod (PROFILES), so two playsets never share one generated patch.
The output contains other authors' content. It is for the user's own playset only: never upload it.
Output: <mod folder>/<profile folder>/   Report: tools/out/playset_compat_report_<profile>.md
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
    AGE6, AGE7, BILL_LAWS, EXCLUDED_DIRS, EXCLUDED_FILES, PREFIX as MAIN_PREFIX, RE_B_HAS, RE_B_LEVEL,
    RE_B_TOTAL, RE_B_TYPE, SCAN_DIRS, add_bill_locks, add_switch_branches, collect_dlc_injects, needs_patch,
    referenced_locals, rewrite_buildings, rewrite_code,
)

COMPAT_BASE = "The Singularity Is Near - Playset Compat"
ID_BASE = "chris.the_singularity_is_near_playset_compat"
# playset name -> (output mod folder, mod id). Other playsets get "<COMPAT_BASE> - <playset>".
PROFILES = {
    "The Singularity is Near": (COMPAT_BASE, ID_BASE),
}
MANUAL_ROOT = pdx.MOD_ROOT / "tools" / "compat_manual"
REPLACE_PREFIX = "zzzz_tsin_compat_"
INJECT_FILE = "zzzzz_tsin_compat_injections.txt"
AGE_FILE = "in_game/common/age/zzzzz_tsin_compat_age7_estates.txt"
GENERATED_DIRS = ["in_game", "main_menu"]
ON_ACTION_DB = "in_game/common/on_action"
FULL_MODES = ("", "REPLACE", "TRY_REPLACE", "REPLACE_OR_CREATE")
AI_PRIVILEGE_KEYS = ("max_ai_privilege_per_estate", "min_ai_privilege_per_estate")
RE_BUILDING_REF = re.compile("|".join(r.pattern for r in (RE_B_LEVEL, RE_B_HAS, RE_B_TYPE, RE_B_TOTAL)))


@dataclass
class TextPatch:
    db: str
    name: str
    pattern: str
    repl: str
    reason: str


# Objects whose numbers stop before age 7. Each pattern must match exactly once, otherwise the patch is
# skipped and reported (the source mod changed).
TEXT_PATCHES = [
    # AI Army & Manpower Overhaul: the CMF "last year" setting can only be set up to 1837 (default 1737 stays).
    TextPatch("in_game/common/scripted_effects", "aamo_register_cmf_mod",
              r"(setting_id\s*=\s*end_year\b[^{}]*?max_value\s*=\s*)1837\b", r"\g<1>2337",
              "AAMO 종료 연도 설정 상한 1837 → 2337(기본값 1737과 사용자 설정은 그대로)"),
]

# Data functions removed or renamed by the game: (pattern, replacement, reason). Applied to every .gui file
# that wins in the playset (main mod included); the fixed copy is written to the same path.
GUI_FIXES = [
    (r'visible\s*=\s*"\[UniqueContentItem\.IsReligiousOrderSetup\]"', "visible = no",
     "1.4에서 없어진 UniqueContentItem.IsReligiousOrderSetup(종교 기사단 설정 카드 숨김)"),
    (r"UniqueContentItem\.IsReligiousOrderSetup\b", "UniqueContentItem.IsCalling",
     "1.4에서 없어진 UniqueContentItem.IsReligiousOrderSetup(Or 목록에서 중복 항목으로 대체)"),
    (r"\bWillRunOutOfFoodStochpile\b", "WillRunOutOfFoodStockpile",
     "바닐라에서 이름이 바뀐 Market.WillRunOutOfFoodStockpile"),
]


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
    """Parse only files that check age 6 or a replaced building, inject, or define an object named in `wanted`."""
    relevant = re.compile(r"age_6_revolutions|INJECT:|" + RE_BUILDING_REF.pattern
                          + r"|\b(?:" + "|".join(map(re.escape, sorted(wanted))) + r")\b")
    effective: dict[str, tuple[int, Path]] = {}
    for i, root in enumerate(roots):
        for p in pdx.iter_script_files(root, SCAN_DIRS):
            effective[p.relative_to(root).as_posix()] = (i, p)  # later mod replaces an equal path
    names = [mod_name(r) for r in roots]
    defs: dict[tuple[str, str], list[Def]] = defaultdict(list)
    injects: dict[tuple[str, str], list[Def]] = defaultdict(list)
    for rel, (i, p) in sorted(effective.items()):
        if rel in EXCLUDED_FILES or any(rel.startswith(d + "/") for d in EXCLUDED_DIRS):
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


def text_patch_for(key: tuple[str, str]) -> TextPatch | None:
    return next((t for t in TEXT_PATCHES if (t.db, t.name) == key), None)


def building_refs(d: Def) -> int:
    """Replaced-building checks in the block and the file-local triggers/effects it uses."""
    code = pdx.strip_comments(d.block.text)
    blocks = [d.block.text] + [d.src.local_defs[k].text for k in referenced_locals(code, d.src.local_defs)]
    return sum(rewrite_buildings(b)[1] for b in blocks)


def patch_reasons(d: Def, key: tuple[str, str], restores: bool) -> tuple[list[str], str]:
    """Why `d` must be rewritten, and a warning when a text patch no longer applies."""
    reasons = ["본 모드 패치가 지우던 정의 복원"] if restores else []
    local_defs = d.src.local_defs
    code = pdx.strip_comments(d.block.text)
    if needs_patch(code) or any(needs_patch(pdx.strip_comments(local_defs[k].text))
                                for k in referenced_locals(code, local_defs)):
        reasons.append("제6시대 검사 연장")
    n_buildings = building_refs(d)
    if n_buildings:
        reasons.append(f"대체 건물 조건 {n_buildings}곳")
    patch = text_patch_for(key)
    if patch and len(re.findall(patch.pattern, d.block.text)) == 1:
        reasons.append(patch.reason)
    elif patch:
        return reasons, f"- **경고** `{key[1]}`: 텍스트 패치 대상이 바뀌어 적용하지 않음({patch.reason})"
    return reasons, ""


def file_override(src: SourceFile, patched: list[Def]) -> str:
    """The whole source file with `patched` blocks rewritten, for databases that merge by key (on_action)."""
    edits: dict[int, tuple[int, str]] = {}
    for d in patched:
        body, _, _, locals_out = rewritten(d, "")
        edits[d.block.start] = (d.block.end, body)
        for k, t in locals_out.items():
            edits[src.local_defs[k].start] = (src.local_defs[k].end, t)
    text = src.text
    for start in sorted(edits, reverse=True):
        end, new = edits[start]
        text = text[:start] + new + text[end:]
    return text


def rewritten(d: Def, op: str) -> tuple[str, list[str], list[str], dict[str, str]]:
    """Rewritten block plus the namespaces, @variables and file-local blocks it needs.

    Same rewrites as the main mod's zzz_tsin_age7_* patches: age 6 checks, replaced buildings, bill locks."""
    main_menu = d.rel.startswith("main_menu/")
    local_defs = d.src.local_defs
    code = pdx.strip_comments(d.block.text)
    locals_out = {k: rewrite_buildings(rewrite_code(local_defs[k].text, main_menu))[0]
                  for k in referenced_locals(code, local_defs)}
    body = d.block.text[len(d.block.key):]  # "= { ... }" without the original prefix
    body, _ = add_switch_branches(d.name + body)
    body = rewrite_code(body, main_menu)
    body, _ = rewrite_buildings(body)
    if db_of(d.rel) == "in_game/common/laws" and d.name in BILL_LAWS and op in FULL_MODES:
        body, _ = add_bill_locks(body)
    patch = text_patch_for((db_of(d.rel), d.name))
    if patch:
        body = re.sub(patch.pattern, patch.repl, body)
    variables = d.src.variables
    used_vars = [f"{v} = {variables[v]}" for v in variables if re.search(re.escape(v) + r"\b", code)]
    return (f"{op}:" if op else "") + body, d.src.namespaces, used_vars, locals_out


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


def profile(label: str) -> tuple[str, str, str]:
    """(output folder, mod id, slug) of a playset."""
    slug = re.sub(r"[^A-Za-z0-9]+", "_", label).strip("_").lower()
    folder, mod_id = PROFILES.get(label, (f"{COMPAT_BASE} - {label}", f"{ID_BASE}_{slug}"))
    return folder, mod_id, slug


def write_metadata(root: Path, folder: str, mod_id: str, label: str) -> None:
    meta = {
        "name": folder,
        "id": mod_id,
        "version": json.loads(pdx.read_text(pdx.MOD_ROOT / ".metadata" / "metadata.json"))["version"],
        "game_id": "eu5",
        "supported_game_version": "1.4.*",
        "short_description": f"LOCAL ONLY. Generated age 7 compatibility patch for the playset '{label}'. Contains other mods' content: do not upload.",
        "tags": ["Fixes"],
        "relationships": [],
        "game_custom_data": {},
    }
    (root / ".metadata").mkdir(parents=True, exist_ok=True)
    (root / ".metadata" / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    (root / "README.txt").write_text(
        "Generated by The Singularity Is Near/tools/gen_playset_compat.py.\n"
        f"Playset: {label}. Load it last, right after The Singularity Is Near.\n"
        "Local only: it contains content of other workshop mods. Do not upload it.\n"
        "Re-run the tool after changing the playset or updating mods. Hand-written patches belong in\n"
        "The Singularity Is Near/tools/compat_manual/<profile>/, not here: this folder is rebuilt.\n",
        encoding="utf-8")


def age7_estate_injects(roots: list[Path], names: list[str]) -> tuple[list[tuple[str, str]], list[str]]:
    """Playset injects of AI privilege limits into age 6, re-targeted at age 7 for estates age 7 lacks."""
    age7 = pdx.strip_comments(pdx.read_text(pdx.MOD_ROOT / "in_game/common/age/tsin_age_7.txt"))
    known: set[str] = set()
    for key in AI_PRIVILEGE_KEYS:
        m = re.search(key + r"\s*=\s*\{([^{}]*)\}", age7)
        if m:
            known.update(re.findall(r"(\w+)\s*=", m.group(1)))
    effective: dict[str, tuple[int, Path]] = {}
    for i, root in enumerate(roots):
        for p in sorted((root / "in_game/common/age").glob("*.txt")):
            effective[p.name] = (i, p)
    out: list[tuple[str, str]] = []
    notes: list[str] = []
    for name, (i, p) in sorted(effective.items()):
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            mode, target = split_mode(b.key)
            if target != AGE6 or mode not in ("INJECT", "TRY_INJECT"):
                continue
            clean = pdx.strip_comments(b.text)
            parts = []
            for c in pdx.top_level_blocks(clean[clean.index("{") + 1:clean.rindex("}")]):
                if c.key not in AI_PRIVILEGE_KEYS:
                    notes.append(f"{names[i]} `{name}`: `{c.key}`은 제7시대로 옮기지 않음(수동 검토)")
                    continue
                values = [(e, v) for e, v in re.findall(r"(\w+)\s*=\s*(-?[\d.]+)", c.text) if e not in known]
                if values:
                    parts.append(f"\t{c.key} = {{\n" + "".join(f"\t\t{e} = {v}\n" for e, v in values) + "\t}")
            if parts:
                out.append((f"{names[i]}: in_game/common/age/{name}",
                            f"TRY_INJECT:{AGE7} = {{\n" + "\n".join(parts) + "\n}"))
    return out, notes


def gui_fixes(roots: list[Path]) -> tuple[dict[str, str], list[str]]:
    """{gui rel path: fixed text} for winning .gui files that call removed data functions."""
    effective: dict[str, Path] = {}
    for root in roots + [pdx.MOD_ROOT]:
        for sub in GENERATED_DIRS:
            for p in sorted((root / sub).rglob("*.gui")):
                effective[p.relative_to(root).as_posix()] = p
    out: dict[str, str] = {}
    notes: list[str] = []
    for rel, p in sorted(effective.items()):
        text = pdx.read_text(p)
        reasons = []
        for pattern, repl, reason in GUI_FIXES:
            text, n = re.subn(pattern, repl, text)
            if n:
                reasons.append(f"{reason} {n}곳")
        if reasons:
            out[rel] = text
            owner = mod_name(next(r for r in roots + [pdx.MOD_ROOT] if p.is_relative_to(r)))
            notes.append(f"- `{rel}` ← {owner}: {', '.join(reasons)}")
    return out, notes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--playset")
    ap.add_argument("--mods", nargs="*")
    ap.add_argument("--dry-run", action="store_true", help="write the report only")
    args = ap.parse_args()
    if args.mods:
        label = "mods " + " ".join(args.mods)
        roots = [Path(m) if Path(m).is_dir() else pdx.workshop_root() / m for m in args.mods]
    else:
        label, roots = playset_mods(args.playset)
    folder, mod_id, slug = profile(label)
    compat_root = pdx.MOD_ROOT.parent / folder
    roots = [r for r in roots if r.exists() and r.resolve() != pdx.MOD_ROOT.resolve()
             and not r.name.startswith(COMPAT_BASE)]
    names = [mod_name(r) for r in roots]

    replaced_by_main, main_own = main_mod_objects()
    defs, injects = collect(roots, {name for _, name in replaced_by_main} | {t.name for t in TEXT_PATCHES})

    replace_items: dict[str, list] = defaultdict(list)  # source rel -> items
    on_action_files: dict[str, list[Def]] = defaultdict(list)  # source rel -> blocks to rewrite
    replace_notes: dict[str, set[str]] = defaultdict(set)
    replaced: set[tuple[str, str]] = set()
    counts: dict[str, int] = defaultdict(int)
    report = [f"# 플레이셋 호환 패치: {label}", "", f"모드 {len(roots)}개, 출력 `{compat_root}`", "", "## 교체", ""]
    for key in sorted(defs):
        if key[0] == ON_ACTION_DB:
            for d in defs[key]:
                reasons, warning = patch_reasons(d, key, False)
                report += [warning] if warning else []
                if reasons:
                    on_action_files[d.rel].append(d)
                    report.append(f"- `{key[1]}` ({key[0]}) ← {d.mod_name} `{d.rel}`: {', '.join(reasons)} "
                                  f"(on_action은 키별로 병합되므로 파일 전체를 같은 경로로 덮어씀)")
            continue
        if key in main_own:
            report.append(f"- `{key[1]}` ({key[0]}): 본 모드가 의도적으로 바꾸는 객체라 건드리지 않음")
            continue
        winner = max(defs[key], key=lambda d: d.order)
        reasons, warning = patch_reasons(winner, key, key in replaced_by_main)
        report += [warning] if warning else []
        if not reasons:
            continue
        op = "" if key[0] == "in_game/events" else "TRY_REPLACE"
        replace_items[winner.rel].append(rewritten(winner, op))
        replace_notes[winner.rel].add(winner.mod_name)
        replaced.add(key)
        for r in reasons:
            counts["대체 건물 조건" if r.startswith("대체 건물") else r] += 1
        report.append(f"- `{key[1]}` ({key[0]}) ← {winner.mod_name} `{winner.rel}`: {', '.join(reasons)}")

    inject_items: dict[str, list] = defaultdict(list)  # db -> items
    inject_notes: dict[str, set[str]] = defaultdict(set)
    report += ["", "## 다시 적용한 주입", ""]
    dlc_injects = collect_dlc_injects(pdx.game_root())
    n_dlc = 0
    for key in sorted(replaced):
        if key[0] == "in_game/events":
            continue
        for dlc_rel, text in dlc_injects.get(key, []):
            inject_items[key[0]].append((text, [], [], {}))
            inject_notes[key[0]].add(f"DLC: {dlc_rel}")
            report.append(f"- `{key[1]}` ← DLC `{dlc_rel}`")
            n_dlc += 1
    for key in sorted(injects):
        if key not in replaced and key not in replaced_by_main:
            continue
        for d in sorted(injects[key], key=lambda d: d.order):
            inject_items[key[0]].append(rewritten(d, d.mode))
            inject_notes[key[0]].add(f"{d.mod_name}: {d.rel}")
            report.append(f"- `{d.mode}:{key[1]}` ← {d.mod_name} `{d.rel}`")

    age_items, age_notes = age7_estate_injects(roots, names)
    report += ["", "## 제7시대 계층 AI 특권 한도", ""]
    report += [f"- {src}: 제6시대 값을 제7시대에 이어 붙임" for src, _ in age_items] + [f"- {n}" for n in age_notes]

    gui_items, gui_notes = gui_fixes(roots)
    report += ["", "## GUI 데이터 함수 수정", ""] + (gui_notes or ["- 없음"])

    manual = MANUAL_ROOT / slug
    manual_files = sorted(p for sub in GENERATED_DIRS if (manual / sub).exists()
                          for p in (manual / sub).rglob("*") if p.is_file())
    report += ["", "## 수동 패치", "", f"`tools/compat_manual/{slug}/`: {len(manual_files)}개 파일"]
    report += [f"- `{p.relative_to(manual).as_posix()}`" for p in manual_files]

    n_inject = sum(len(v) for v in inject_items.values())
    summary = (f"교체 {len(replaced)}개(" + ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
               + f"), on_action 파일 {len(on_action_files)}개({sum(map(len, on_action_files.values()))}블록), "
               f"주입 {n_inject}개(DLC {n_dlc}), 시대 계층 주입 {len(age_items)}개, GUI 수정 {len(gui_items)}개, "
               f"수동 파일 {len(manual_files)}개")
    report.insert(4, summary)

    if not args.dry_run:
        for sub in GENERATED_DIRS:
            if (compat_root / sub).exists():
                shutil.rmtree(compat_root / sub)
        for rel, items in replace_items.items():
            out = compat_root / Path(rel).parent / f"{REPLACE_PREFIX}{Path(rel).stem}.txt"
            write_file(out, [f"from {', '.join(sorted(replace_notes[rel]))}: {rel}"], items)
        for db, items in inject_items.items():
            write_file(compat_root / db / INJECT_FILE, sorted(inject_notes[db]), items)
        for rel, patched in on_action_files.items():
            note = (f"# GENERATED by tools/gen_playset_compat.py: {patched[0].mod_name} {rel} with age 7 rewrites. "
                    "Local use only, do not upload.\n")
            pdx.write_text_bom(compat_root / rel, note + file_override(patched[0].src, patched))
        if age_items:
            write_file(compat_root / AGE_FILE, [src for src, _ in age_items], [(t, [], [], {}) for _, t in age_items])
        for rel, text in gui_items.items():
            pdx.write_text_bom(compat_root / rel, text)
        for p in manual_files:
            dest = compat_root / p.relative_to(manual)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
        # Regenerate the optional Glorp stats integration after other GUI/manual patches.
        glorp_source = next((r for r in reversed(roots) if (r / "in_game/gui/glorp.gui").exists()), None)
        if glorp_source is not None:
            from gen_glorp_stats_compat import generate as generate_glorp_stats
            generate_glorp_stats(glorp_source, compat_root)
            from gen_stock_market_ui import generate_compat as generate_stock_ui
            generate_stock_ui(glorp_source, compat_root)
        write_metadata(compat_root, folder, mod_id, label)

    out_report = pdx.MOD_ROOT / "tools" / "out" / f"playset_compat_report_{slug}.md"
    out_report.parent.mkdir(parents=True, exist_ok=True)
    out_report.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(summary)
    print(f"compat mod: {compat_root}{' (dry run, not written)' if args.dry_run else ''}")
    print(f"report: {out_report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
