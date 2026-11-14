"""Generate per-object TRY_REPLACE patches that carry vanilla age-6 checks into age 7.

Vanilla content written as `current_age = age_6_revolutions` switches off when
age 7 starts, and `NOT/NOR = { current_age = age_6_revolutions }` (meaning "an
early age") switches back on. Every top-level object containing such a check
is copied from the installed game, rewritten, and emitted as TRY_REPLACE
(REPLACE for events) under in_game/... or main_menu/... with a zzz_tsin_age7_
file prefix.

Rewrites (code only, comments untouched):
  in_game : current_age = age_6_revolutions -> current_age_or_later = { age = age_6_revolutions }
  main_menu: current_age = age_6_revolutions -> OR = { current_age = age_6_revolutions current_age = age_7_industrialization }
  any     : birth_age = age:age_6_revolutions -> OR = { birth_age = age:age_6_revolutions birth_age = age:age_7_industrialization }
  switch = { trigger = current_age ... age_6_revolutions = { X } } -> adds age_7_industrialization = { X }

Re-run after every game patch:  python tools/gen_age7_patches.py
Report: tools/out/age7_patch_report.md
"""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pdx  # noqa: E402

AGE6 = "age_6_revolutions"
AGE7 = "age_7_industrialization"
PREFIX = "zzz_tsin_age7_"

SCAN_DIRS = ["in_game/common", "in_game/events", "main_menu/common"]

# Files handled by hand or that only *assign* an age (not check it).
EXCLUDED_FILES = {
    "in_game/common/scripted_triggers/game_triggers.txt",  # tsin_age_triggers.txt
    "in_game/common/age/00_default.txt",
}
EXCLUDED_DIRS = {
    "in_game/common/age",
    "in_game/common/advances",
    "in_game/common/institution",
    "in_game/common/unit_types",
    "in_game/common/prices",
}
# Objects deliberately left age-6 only. key -> reason
EXCLUDED_OBJECTS: dict[str, str] = {}

RE_CUR = re.compile(r"current_age\s*=\s*" + AGE6 + r"\b")
RE_BIRTH = re.compile(r"birth_age\s*=\s*age:" + AGE6 + r"\b")
RE_SWITCH = re.compile(r"switch\s*=\s*\{\s*trigger\s*=\s*current_age\b")
RE_BRANCH = re.compile(r"\b" + AGE6 + r"\s*=\s*\{")


def rel(p: Path, root: Path) -> str:
    return p.relative_to(root).as_posix()


def rewrite_code(text: str, main_menu: bool) -> str:
    """Apply regex rewrites to code parts only (not comments)."""
    out_lines = []
    for line in text.split("\n"):
        mask = pdx.code_mask(line)
        cut = next((i for i, m in enumerate(mask) if not m), len(line))
        code, comment = line[:cut], line[cut:]
        if main_menu:
            code = RE_CUR.sub(f"OR = {{ current_age = {AGE6} current_age = {AGE7} }}", code)
        else:
            code = RE_CUR.sub(f"current_age_or_later = {{ age = {AGE6} }}", code)
        code = RE_BIRTH.sub(f"OR = {{ birth_age = age:{AGE6} birth_age = age:{AGE7} }}", code)
        out_lines.append(code + comment)
    return "\n".join(out_lines)


def add_switch_branches(text: str) -> tuple[str, int]:
    """Duplicate age_6 branches of `switch = { trigger = current_age }` as age_7."""
    count = 0
    while True:
        clean = pdx.strip_comments(text)
        done = True
        for sm in RE_SWITCH.finditer(clean):
            open_idx = clean.index("{", sm.start())
            close_idx = pdx.matching_brace(clean, open_idx)
            body = clean[open_idx:close_idx]
            if re.search(r"\b" + AGE7 + r"\s*=", body):
                continue
            bm = RE_BRANCH.search(body)
            if not bm:
                continue
            b_start = open_idx + bm.start()
            b_open = open_idx + bm.end() - 1
            b_close = pdx.matching_brace(clean, b_open)
            branch = text[b_start:b_close + 1]
            line_start = text.rfind("\n", 0, b_start) + 1
            indent = text[line_start:b_start]
            new_branch = AGE7 + branch[len(AGE6):]
            text = text[:b_close + 1] + "\n" + indent + new_branch + text[b_close + 1:]
            count += 1
            done = False
            break
        if done:
            return text, count


def referenced_locals(code: str, local_defs: dict) -> list[str]:
    """File-local scripted triggers/effects used by `code`, transitively, in definition order."""
    found: set[str] = set()
    pending = [code]
    while pending:
        c = pending.pop()
        for name, blk in local_defs.items():
            if name not in found and re.search(r"\b" + re.escape(name) + r"\b", c):
                found.add(name)
                pending.append(pdx.strip_comments(blk.text))
    return [k for k in local_defs if k in found]


def needs_patch(code: str) -> bool:
    if RE_CUR.search(code) or RE_BIRTH.search(code):
        return True
    for sm in RE_SWITCH.finditer(code):
        open_idx = code.index("{", sm.start())
        body = code[open_idx:pdx.matching_brace(code, open_idx)]
        if RE_BRANCH.search(body) and not re.search(r"\b" + AGE7 + r"\s*=", body):
            return True
    return False


def main() -> int:
    game = pdx.game_root()
    mod = pdx.MOD_ROOT
    if not game.exists():
        print(f"game not found: {game} (set TSIN_GAME)")
        return 1

    # clear previous output
    for old in mod.rglob(f"{PREFIX}*.txt"):
        old.unlink()

    report: dict[str, list[str]] = defaultdict(list)
    total = 0
    for path in pdx.iter_script_files(game, SCAN_DIRS):
        r = rel(path, game)
        if r in EXCLUDED_FILES or any(r.startswith(d + "/") for d in EXCLUDED_DIRS):
            continue
        text = pdx.read_text(path)
        if AGE6 not in text:
            continue
        is_event = r.startswith("in_game/events/")
        main_menu = r.startswith("main_menu/")
        variables = pdx.file_variables(text)
        blocks = pdx.top_level_blocks(text)
        local_defs = {b.key: b for b in blocks if b.local_kind}
        out_blocks = []
        out_locals: dict[str, str] = {}
        for blk in blocks:
            if blk.local_kind or blk.key.startswith(("INJECT:", "REPLACE:", "TRY_")):
                continue
            code = pdx.strip_comments(blk.text)
            used_locals = referenced_locals(code, local_defs)
            if not (needs_patch(code) or any(needs_patch(pdx.strip_comments(local_defs[k].text)) for k in used_locals)):
                continue
            for k in used_locals:
                out_locals[k] = rewrite_code(local_defs[k].text, main_menu)
            if blk.key in EXCLUDED_OBJECTS:
                report[r].append(f"- `{blk.key}` 제외: {EXCLUDED_OBJECTS[blk.key]}")
                continue
            new_text, n_switch = add_switch_branches(blk.text)
            new_text = rewrite_code(new_text, main_menu)
            op = "REPLACE" if is_event else "TRY_REPLACE"
            new_text = f"{op}:{new_text}"
            used_vars = [v for v in variables if re.search(re.escape(v) + r"\b", code)]
            out_blocks.append((blk.key, new_text, used_vars))
            kinds = []
            if RE_CUR.search(code):
                kinds.append("current_age")
            if RE_BIRTH.search(code):
                kinds.append("birth_age")
            if n_switch:
                kinds.append(f"switch+{n_switch}")
            report[r].append(f"- `{blk.key}` ({', '.join(kinds)})")
        if not out_blocks:
            continue
        header = [
            f"# GENERATED by tools/gen_age7_patches.py from vanilla {r}",
            "# Do not edit by hand; re-run the generator after a game patch.",
            "",
        ]
        if is_event:
            header += [f"namespace = {ns}" for ns in pdx.namespaces(text)] + [""]
        needed_vars = sorted({v for _, _, vs in out_blocks for v in vs})
        if needed_vars:
            header += [f"{v} = {variables[v]}" for v in needed_vars] + [""]
        header.append("")
        body = "\n\n".join(list(out_locals.values()) + [t for _, t, _ in out_blocks])
        out_path = mod / Path(r).parent / f"{PREFIX}{path.stem}.txt"
        pdx.write_text_bom(out_path, "\n".join(header) + body + "\n")
        total += len(out_blocks)

    out_dir = mod / "tools" / "out"
    lines = [f"# age7 patch report ({total} objects)", ""]
    for r in sorted(report):
        lines.append(f"## {r}")
        lines.extend(report[r])
        lines.append("")
    pdx.write_text_bom(out_dir / "age7_patch_report.md", "\n".join(lines))
    print(f"patched objects: {total}, files: {len(report)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
