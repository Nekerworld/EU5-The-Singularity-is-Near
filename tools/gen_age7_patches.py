"""Generate per-object TRY_REPLACE patches that carry vanilla age-6 checks into age 7.

Vanilla content written as `current_age = age_6_revolutions` switches off when
age 7 starts, and `NOT/NOR = { current_age = age_6_revolutions }` (meaning "an
early age") switches back on. Every top-level object containing such a check
is copied from the installed game, rewritten, and emitted as TRY_REPLACE
under in_game/... or main_menu/... with a zzz_tsin_age7_ file prefix.
Events take no prefix: the event manager reads `REPLACE:ns.1` as a new event id
in a namespace "REPLACE:ns". An event is overridden by defining the same id in a
file loaded later (error.log then reports "Duplicated event ID", as for other mods).

Rewrites (code only, comments untouched):
  in_game : current_age = age_6_revolutions -> current_age_or_later = { age = age_6_revolutions }
  main_menu: current_age = age_6_revolutions -> OR = { current_age = age_6_revolutions current_age = age_7_industrialization }
  any     : birth_age = age:age_6_revolutions -> OR = { birth_age = age:age_6_revolutions birth_age = age:age_7_industrialization }
  switch = { trigger = current_age ... age_6_revolutions = { X } } -> adds age_7_industrialization = { X }

Replaced buildings (docs/replaced_buildings.md): every emitted object, plus the
objects in BUILDING_TARGETS, also accepts the age VII upgrade of a vanilla
building (`obsolete = <old>`):
  has_building_with_at_least_one_level = old -> OR = { ... = old ... = new }
  has_building = building_type:old            -> OR = { ... :old ... :new }
  building_type = building_type:old (in an OR) -> both ids
  total_effective_building_levels:university  -> tsin_total_university_levels

DLC `INJECT:` blocks into an emitted object are re-applied after the
replacement so the DLC content is not lost.

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

# vanilla building -> age VII upgrade with `obsolete = <vanilla>`
BUILDING_UPGRADES = {
    "university": "tsin_research_university",
    "naval_base": "tsin_steam_port",
    "aqueduct_system": "tsin_waterworks",
    "provincial_chancery": "tsin_prefecture",
    "textile_mill": "tsin_mechanized_textile_mill",
    "lumber_mill": "tsin_steam_sawmill",
    "iron_mill": "tsin_automated_iron_mill",
    "glass_mill": "tsin_automated_glass_mill",
    "paper_mill": "tsin_automated_paper_mill",
    "furniture_mill": "tsin_automated_furniture_mill",
    "printing_mill": "tsin_automated_printing_mill",
    "fine_cloth_mill": "tsin_automated_fine_cloth_mill",
}
# country-scope script values that sum a vanilla building and its upgrade (tsin_replaced_building_values.txt)
BUILDING_LEVEL_VALUES = {"university": "tsin_total_university_levels"}
# Objects still active in age VII that reference a replaced building (docs/replaced_buildings.md, group A).
BUILDING_TARGETS: dict[str, set[str]] = {
    "in_game/common/scripted_triggers/location_triggers.txt": {"has_dock_infrastructure"},
    "in_game/common/scripted_triggers/unit_triggers.txt": {
        "unit_ship_of_the_line_location_trigger", "unit_war_galleon_location_trigger"},
    "in_game/common/laws/01_common.txt": {
        "education_elites_law", "press_law", "education_masses_law", "immigration_law", "slavery_laws"},
    "in_game/common/estate_privileges/clergy_estate.txt": {"clergy_lecture_oaths"},
    "in_game/common/parliament_issues/05_burghers_estate_parliament_issues.txt": {
        "sponsor_a_university", "expand_docks", "expand_dry_docks", "expand_shipyards",
        "expand_grand_shipyards", "expand_naval_bases"},
    "in_game/common/missions/generic_progress_and_literacy_mission_pack.txt": {"progress_and_literacy"},
    "in_game/common/religious_order_callings/00_monastic.txt": {"scholars_calling"},
    "in_game/common/religious_order_zeal_modifiers/00_catholic.txt": {"zeal_seat_of_learning"},
    "in_game/common/town_rights/byzantine_greek_roman.txt": {"scholai_literacy_rights"},
    "in_game/events/economy/building_events.txt": {"building.1", "building.2"},
    "in_game/events/economy/industrialization_events.txt": {
        "industrialization_events.10", "industrialization_events.13",
        "industrialization_events.15", "industrialization_events.22"},
}

# Vanilla laws decided by bills (docs/legislation.md): every policy gets the bill lock in its allow.
BILL_LAWS = {"press_law", "education_masses_law", "immigration_law", "slavery_laws"}
BILL_LOCK = "tsin_policy_enactable_trigger = yes"

_OLD = "|".join(BUILDING_UPGRADES)
RE_B_LEVEL = re.compile(r"(?<![\w])has_building_with_at_least_one_level\s*=\s*(" + _OLD + r")(?![\w])")
RE_B_HAS = re.compile(r"(?<![\w])has_building\s*=\s*building_type:(" + _OLD + r")(?![\w])")
RE_B_TYPE = re.compile(r"(?<![\w])building_type\s*=\s*building_type:(" + _OLD + r")(?![\w])")
RE_B_TOTAL = re.compile(r"(?<![\w])total_effective_building_levels:(" + "|".join(BUILDING_LEVEL_VALUES) + r")(?![\w])")
RE_OPEN_KEY = re.compile(r"([A-Za-z0-9_:.@]+)\s*=\s*$")

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
        from gen_city_expansion import rewrite_rank_checks
        code = rewrite_rank_checks(code)
        out_lines.append(code + comment)
    return "\n".join(out_lines)


def enclosing_key(clean: str, pos: int) -> str:
    """Key of the innermost `key = {` block that contains position `pos`."""
    depth = 0
    for k in range(pos - 1, -1, -1):
        c = clean[k]
        if c == "}":
            depth += 1
        elif c == "{":
            if depth == 0:
                m = RE_OPEN_KEY.search(clean, 0, k)
                return m.group(1) if m else ""
            depth -= 1
    return ""


def rewrite_buildings(text: str) -> tuple[str, int]:
    """Make checks for a replaced vanilla building also accept its upgrade (code only)."""
    clean = pdx.strip_comments(text)
    edits: list[tuple[int, int, str]] = []
    for m in RE_B_LEVEL.finditer(clean):
        old = m.group(1)
        new = BUILDING_UPGRADES[old]
        edits.append((m.start(), m.end(), f"OR = {{ has_building_with_at_least_one_level = {old} "
                                          f"has_building_with_at_least_one_level = {new} }}"))
    for m in RE_B_HAS.finditer(clean):
        old = m.group(1)
        new = BUILDING_UPGRADES[old]
        edits.append((m.start(), m.end(), f"OR = {{ has_building = building_type:{old} "
                                          f"has_building = building_type:{new} }}"))
    for m in RE_B_TYPE.finditer(clean):
        if enclosing_key(clean, m.start()) != "OR":
            continue  # effect parameter (construct_building etc.), not a trigger
        old = m.group(1)
        edits.append((m.start(), m.end(), f"building_type = building_type:{old} "
                                          f"building_type = building_type:{BUILDING_UPGRADES[old]}"))
    for m in RE_B_TOTAL.finditer(clean):
        edits.append((m.start(), m.end(), BUILDING_LEVEL_VALUES[m.group(1)]))
    for start, end, repl in sorted(edits, reverse=True):
        text = text[:start] + repl + text[end:]
    return text, len(edits)


def add_bill_locks(text: str) -> tuple[str, int]:
    """Put the bill lock into the allow of every policy of a law block `law = { ... }`."""
    clean = pdx.strip_comments(text)
    law_open = clean.index("{")
    inserts: list[tuple[int, str]] = []
    for blk in pdx.top_level_blocks(clean[law_open + 1:pdx.matching_brace(clean, law_open)]):
        if blk.key in ("potential", "allow"):
            continue
        p_open = law_open + 1 + blk.start + blk.text.index("{")
        p_close = pdx.matching_brace(clean, p_open)
        allow = next((b for b in pdx.top_level_blocks(clean[p_open + 1:p_close]) if b.key == "allow"), None)
        if allow:
            a_open = p_open + 1 + allow.start + allow.text.index("{")
            inserts.append((a_open + 1, f" {BILL_LOCK} "))
        else:
            inserts.append((p_open + 1, f"\n\t\tallow = {{ {BILL_LOCK} }}"))
    for pos, s in sorted(inserts, reverse=True):
        text = text[:pos] + s + text[pos:]
    return text, len(inserts)


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


def collect_dlc_injects(game: Path) -> dict[tuple[str, str], list[tuple[str, str]]]:
    """(vanilla dir, object key) -> [(dlc file, `INJECT:key = {...}` text)] for every DLC folder."""
    out: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    dlc_root = game / "dlc"
    if not dlc_root.exists():
        return out
    for dlc in sorted(p for p in dlc_root.iterdir() if p.is_dir()):
        for path in pdx.iter_script_files(dlc, SCAN_DIRS):
            r = rel(path, dlc)
            for blk in pdx.top_level_blocks(pdx.read_text(path)):
                m = re.match(r"(?:TRY_)?INJECT:(.+)$", blk.key)
                if m:
                    out[(Path(r).parent.as_posix(), m.group(1))].append((rel(path, game), blk.text))
    return out


def main() -> int:
    game = pdx.game_root()
    mod = pdx.MOD_ROOT
    if not game.exists():
        print(f"game not found: {game} (set TSIN_GAME)")
        return 1

    # clear previous output
    for database in SCAN_DIRS:
        for old in (mod / database).rglob(f"{PREFIX}*.txt"):
            old.unlink()

    dlc_injects = collect_dlc_injects(game)
    report: dict[str, list[str]] = defaultdict(list)
    total = 0
    for path in pdx.iter_script_files(game, SCAN_DIRS):
        r = rel(path, game)
        if r in EXCLUDED_FILES or any(r.startswith(d + "/") for d in EXCLUDED_DIRS):
            continue
        text = pdx.read_text(path)
        targets = BUILDING_TARGETS.get(r, set())
        if AGE6 not in text and not targets:
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
            if not (blk.key in targets or needs_patch(code)
                    or any(needs_patch(pdx.strip_comments(local_defs[k].text)) for k in used_locals)):
                continue
            n_building = 0
            for k in used_locals:
                local_text, n = rewrite_buildings(rewrite_code(local_defs[k].text, main_menu))
                out_locals[k] = local_text
                n_building += n
            if blk.key in EXCLUDED_OBJECTS:
                report[r].append(f"- `{blk.key}` 제외: {EXCLUDED_OBJECTS[blk.key]}")
                continue
            new_text, n_switch = add_switch_branches(blk.text)
            new_text = rewrite_code(new_text, main_menu)
            new_text, n = rewrite_buildings(new_text)
            n_building += n
            n_locks = 0
            if blk.key in BILL_LAWS:
                new_text, n_locks = add_bill_locks(new_text)
            if not is_event:
                new_text = f"TRY_REPLACE:{new_text}"
            injects = [] if is_event else dlc_injects.get((Path(r).parent.as_posix(), blk.key), [])
            for dlc_rel, inject_text in injects:
                new_text += f"\n\n# re-applied from {dlc_rel}\n{inject_text}"
            used_vars = [v for v in variables if re.search(re.escape(v) + r"\b", code)]
            out_blocks.append((blk.key, new_text, used_vars))
            kinds = []
            if RE_CUR.search(code):
                kinds.append("current_age")
            if RE_BIRTH.search(code):
                kinds.append("birth_age")
            if n_switch:
                kinds.append(f"switch+{n_switch}")
            if n_building:
                kinds.append(f"buildings+{n_building}")
            if n_locks:
                kinds.append(f"bill_locks+{n_locks}")
            if injects:
                kinds.append(f"dlc_inject+{len(injects)}")
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
