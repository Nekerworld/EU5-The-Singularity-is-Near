"""Static checks for The Singularity is Near. The game itself is the final judge; this
catches the cheap mistakes before a launch.

  python tools/validate.py              all checks
  python tools/validate.py --fix-bom    add missing UTF-8 BOMs first
  python tools/validate.py --prefix-scan
  python tools/validate.py --compat     objects we replace that workshop mods also touch

Checks:
  bom      every .txt/.yml under in_game/main_menu/loading_screen starts with a UTF-8 BOM
  braces   balanced braces per file
  keys     each `key = value` key inside mod objects is known: a modifier type, or a key that
           vanilla uses somewhere in the same database folder, or defined by the mod
  refs     institution:/goods:/religion:/government_reform:/policy:/... references and
           requires/has_advance/unlock_*/copy_from/unit/*_demand point at objects that exist (vanilla or mod)
  buildings  employment_size/build_time/max_levels/price are numbers or script values, and
           unique production method inputs are goods
  gfx      advance icons, event images, institution and map mode art exist (vanilla, DLC or mod)
  loc      tsin_ objects and event title/desc/option keys have english and korean entries
  order    requires/obsolete/copy_from point at objects read earlier (file name order)
  events   event-level outcome = positive/negative/neutral, no REPLACE: prefix, known illustration tags
  concepts mod encyclopedia entries have loc, icon and a known family; [x|e] links name a concept
Exit code 1 if any error.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pdx  # noqa: E402

MOD = pdx.MOD_ROOT
GAME = pdx.game_root()
CONTENT_ROOTS = ["in_game", "main_menu", "loading_screen"]
BOM = b"\xef\xbb\xbf"

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def rel(p: Path) -> str:
    return p.relative_to(MOD).as_posix()


def mod_files(suffixes=(".txt", ".yml")) -> list[Path]:
    out = []
    for r in CONTENT_ROOTS:
        base = MOD / r
        if base.exists():
            out += [p for p in base.rglob("*") if p.suffix in suffixes and p.is_file()]
    return sorted(out)


# ---------------------------------------------------------------- bom / braces

def check_bom(fix: bool) -> None:
    for p in mod_files():
        data = p.read_bytes()
        if not data.startswith(BOM):
            if fix:
                p.write_bytes(BOM + data)
            else:
                err(f"bom: {rel(p)} has no UTF-8 BOM (run --fix-bom)")


def check_braces() -> None:
    for p in mod_files((".txt",)):
        clean = pdx.strip_comments(pdx.read_text(p))
        depth = 0
        in_str = False
        for i, c in enumerate(clean):
            if c == '"':
                in_str = not in_str
            elif in_str:
                continue
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth < 0:
                    err(f"braces: {rel(p)} extra '}}' at line {clean.count(chr(10), 0, i) + 1}")
                    break
        if depth > 0:
            err(f"braces: {rel(p)} has {depth} unclosed '{{'")


# ---------------------------------------------------------------- databases

KEY_LINE = re.compile(r"(?<![\w:.@$])([A-Za-z_][A-Za-z0-9_]*)\s*(?:=|<|>|<=|>=|\?=)")
_db_cache: dict[str, set[str]] = {}
_vocab_cache: dict[str, set[str]] = {}


def db_keys(rel_dir: str) -> set[str]:
    """Top-level object keys in vanilla + mod for a database folder."""
    if rel_dir in _db_cache:
        return _db_cache[rel_dir]
    keys: set[str] = set()
    for root in (GAME, MOD):
        base = root / rel_dir
        if not base.exists():
            continue
        for p in base.rglob("*.txt"):
            for b in pdx.top_level_blocks(pdx.read_text(p)):
                k = b.key.split(":", 1)[1] if ":" in b.key and b.key.split(":", 1)[0].isupper() or b.key.startswith("TRY_") else b.key
                keys.add(k)
            for m in re.finditer(r"^([A-Za-z0-9_]+)\s*=\s*[^{\s]", pdx.strip_comments(pdx.read_text(p)), re.M):
                keys.add(m.group(1))
    _db_cache[rel_dir] = keys
    return keys


def vocab(rel_dir: str) -> set[str]:
    """Every key vanilla uses anywhere inside the database folder."""
    if rel_dir in _vocab_cache:
        return _vocab_cache[rel_dir]
    words: set[str] = set()
    base = GAME / rel_dir
    if base.exists():
        for p in base.rglob("*.txt"):
            words.update(KEY_LINE.findall(pdx.strip_comments(pdx.read_text(p))))
    _vocab_cache[rel_dir] = words
    return words


def modifier_types() -> set[str]:
    out: set[str] = set()
    for root in (GAME, MOD):
        base = root / "main_menu/common/modifier_type_definitions"
        if base.exists():
            for p in base.glob("*.txt"):
                out.update(b.key for b in pdx.top_level_blocks(pdx.read_text(p)))
    return out


def global_vocab() -> set[str]:
    """Trigger/effect/iterator names used anywhere in vanilla scripts (broad allow-list)."""
    if "__global__" in _vocab_cache:
        return _vocab_cache["__global__"]
    words: set[str] = set()
    for d in ["in_game/common", "in_game/events", "main_menu/common", "in_game/gfx/map/map_modes"]:
        base = GAME / d
        for p in base.rglob("*.txt"):
            words.update(KEY_LINE.findall(pdx.strip_comments(pdx.read_text(p))))
    _vocab_cache["__global__"] = words
    return words


def db_dir_of(p: Path) -> str:
    parts = p.relative_to(MOD).parts
    if parts[0] in ("in_game", "main_menu") and len(parts) > 2 and parts[1] == "common":
        return "/".join(parts[:3])
    if parts[0] == "in_game" and parts[1] == "events":
        return "in_game/events"
    return "/".join(parts[:-1])


def mod_defined_names() -> set[str]:
    names: set[str] = set()
    for p in mod_files((".txt",)):
        text = pdx.read_text(p)
        for b in pdx.top_level_blocks(text):
            names.add(b.key.split(":", 1)[-1])
        names.update(re.findall(r"\$([A-Za-z_]+)\$", text))
    return names


# Effects documented in eu5.exe help strings (tools/exe_strings.py) that no vanilla script uses.
ENGINE_KEYS = {"debug_log", "change_global_variable", "age_preference"}


def check_keys() -> None:
    mods = modifier_types()
    gv = global_vocab() | ENGINE_KEYS
    mine = mod_defined_names()
    for p in mod_files((".txt",)):
        if p.name.startswith("zzz_tsin_age7_"):
            continue  # vanilla copies
        d = db_dir_of(p)
        if d.endswith("named_colors"):
            continue
        known = vocab(d) | mods | gv | mine
        clean = pdx.strip_comments(pdx.read_text(p))
        for blk in pdx.top_level_blocks(clean):
            inner = blk.text[blk.text.index("{") + 1:-1]
            for k in set(KEY_LINE.findall(inner)):
                if k not in known and not k.startswith(("tsin_", "scope", "var", "local_var")):
                    err(f"keys: {rel(p)} [{blk.key}] unknown key '{k}'")


REF_PREFIX = {
    "institution": "in_game/common/institution",
    "goods": "in_game/common/goods",
    "building_type": "in_game/common/building_types",
    "age": "in_game/common/age",
    "situation": "in_game/common/situations",
    "disaster_type": "in_game/common/disasters",
    "law": "in_game/common/laws",
    "estate_type": "in_game/common/estates",
    "location_rank": "in_game/common/location_ranks",
    "pop_type": "in_game/common/pop_types",
    "movement": "in_game/common/movements",
    "parliament_issue": "in_game/common/parliament_issues",
    "unit_type": "in_game/common/unit_types",
    "societal_value": "in_game/common/societal_values",
    "government_type": "in_game/common/government_types",
    "government_reform": "in_game/common/government_reforms",
    "religion": "in_game/common/religions",
    "religion_group": "in_game/common/religion_groups",
    "culture": "in_game/common/cultures",
    "culture_group": "in_game/common/culture_groups",
    "estate_privilege": "in_game/common/estate_privileges",
    "parliament_type": "in_game/common/parliament_types",
    "international_organization": "in_game/common/international_organizations",
    "casus_belli": "in_game/common/casus_belli",
    "road_type": "in_game/common/road_types",
    "country_rank": "in_game/common/country_ranks",
}
REF_FIELD = {
    "requires": "in_game/common/advances",
    "in_tree_of": "in_game/common/advances",
    "unlock_building": "in_game/common/building_types",
    "unlock_levy": "in_game/common/levies",
    "unlock_unit": "in_game/common/unit_types",
    "unlock_law": "in_game/common/laws",
    "unlock_production_method": "in_game/common/production_methods",
    "unlock_government_reform": "in_game/common/government_reforms",
    "unlock_casus_belli": "in_game/common/casus_belli",
    "copy_from": "in_game/common/unit_types",
    "unit": "in_game/common/unit_types",
    "obsolete": "in_game/common/building_types",
    "maintenance_demand": "in_game/common/goods_demand",
    "construction_demand": "in_game/common/goods_demand",
    "repair_demand": "in_game/common/goods_demand",
    "produced": "in_game/common/goods",
    "age": "in_game/common/age",
    "has_advance": "in_game/common/advances",
}


_unique_pm_cache: set[str] = set()


def unique_pm_names() -> set[str]:
    """Production methods defined inline in building_types (unique_production_methods)."""
    if not _unique_pm_cache:
        for root in (GAME, MOD):
            base = root / "in_game/common/building_types"
            for p in base.rglob("*.txt") if base.exists() else []:
                clean = pdx.strip_comments(pdx.read_text(p))
                _unique_pm_cache.update(re.findall(r"(\w+)\s*=\s*\{\s*icon_type\b", clean))
    return _unique_pm_cache


def check_tsin_names() -> None:
    """Every tsin_ token used in script must be defined somewhere in the mod."""
    known: set[str] = set()
    texts: dict[Path, str] = {}
    for p in mod_files((".txt",)):
        clean = pdx.strip_comments(pdx.read_text(p))
        texts[p] = clean
        known.update(re.findall(r"(?m)^\s*(tsin_[\w.]+)\s*=\s*\{", clean))
        known.update(re.findall(r"(?m)^@?(tsin_\w+)\s*=", clean))
        known.update(re.findall(r"\b(?:set_variable|set_global_variable|save_scope_as|save_temporary_scope_as)\s*=\s*(tsin_\w+)", clean))
        known.update(re.findall(r"\bname\s*=\s*(tsin_\w+)", clean))
        known.update(re.findall(r"\bVAR\s*=\s*(tsin_\w+)", clean))  # tsin_movement_tick_effect sets $VAR$
    loc = loc_keys("english")
    for p, clean in texts.items():
        unquoted = re.sub(r'"[^"\n]*"', '""', clean)
        loc_refs = set(re.findall(r"\b(?:custom_tooltip|text|desc|title|debug_log)\s*=\s*(tsin_\w+)", unquoted))
        for tok in set(re.findall(r"\b(tsin_\w+(?:\.\d+)?)", unquoted)):
            if tok in known or (tok in loc_refs and tok in loc):
                continue
            err(f"names: {rel(p)} uses '{tok}' which no mod file defines")


_policy_cache: set[str] = set()


def policy_names() -> set[str]:
    """Policies are the block children of each law."""
    if not _policy_cache:
        for root in (GAME, MOD):
            base = root / "in_game/common/laws"
            for p in base.rglob("*.txt") if base.exists() else []:
                for law in pdx.top_level_blocks(pdx.read_text(p)):
                    body = law.text[law.text.find("{") + 1:law.text.rfind("}")]
                    _policy_cache.update(b.key for b in pdx.top_level_blocks(body))
    return _policy_cache


def check_refs() -> None:
    for p in mod_files((".txt",)):
        if p.name.startswith("zzz_tsin_age7_"):
            continue
        clean = pdx.strip_comments(pdx.read_text(p))
        for m in re.finditer(r"\b(" + "|".join(REF_PREFIX) + r"):([A-Za-z0-9_]+)", clean):
            kind, name = m.groups()
            if name not in db_keys(REF_PREFIX[kind]):
                err(f"refs: {rel(p)} {kind}:{name} not found")
        for name in re.findall(r"policy:([A-Za-z0-9_]+)", clean):
            if name not in policy_names():
                err(f"refs: {rel(p)} policy:{name} not found")
        for m in re.finditer(r"\b(" + "|".join(REF_FIELD) + r')\s*=\s*"?([A-Za-z0-9_]+)"?', clean):
            field, name = m.groups()
            d = REF_FIELD[field]
            if field == "age" and "unit_types" not in rel(p) and "advances" not in rel(p) and "institution" not in rel(p):
                continue
            if field in ("unit",) and "levies" not in rel(p):
                continue
            if field == "produced" and "building_types" not in rel(p) and "production_methods" not in rel(p):
                continue
            if name in ("yes", "no"):
                continue
            if field == "unlock_production_method" and name in unique_pm_names():
                continue
            if name not in db_keys(d):
                err(f"refs: {rel(p)} {field} = {name} not found in {d}")


BUILDING_VALUE_FIELDS = ("employment_size", "build_time", "max_levels", "price")
PM_META_KEYS = {"icon_type", "icon", "category", "produced", "output", "potential", "allow", "no_upkeep",
                "is_slave_pm", "debug_max_profit"}


def script_value_names() -> set[str]:
    return db_keys("in_game/common/script_values") | db_keys("main_menu/common/script_values")


def check_buildings() -> None:
    """Mod buildings: level/size fields name a number or a script value; production method inputs are goods."""
    values = script_value_names()
    goods = db_keys("in_game/common/goods")
    for p in mod_files((".txt",)):
        r = rel(p)
        if "building_types" not in r or p.name.startswith("zzz_"):
            continue
        clean = pdx.strip_comments(pdx.read_text(p))
        for blk in pdx.top_level_blocks(clean):
            inner = blk.text[blk.text.index("{") + 1:-1]
            flat = flatten_blocks(inner)
            for field in BUILDING_VALUE_FIELDS:
                for v in re.findall(rf"(?m)^\s*{field}\s*=\s*([A-Za-z0-9_.\-]+)", flat):
                    if not re.fullmatch(r"-?[\d.]+", v) and v not in values:
                        err(f"buildings: {r} [{blk.key}] {field} = {v} is not a script value")
            um = re.search(r"\bunique_production_methods\s*=\s*\{", inner)
            if not um:
                continue
            depth, i = 1, um.end()
            while depth and i < len(inner):
                depth += {"{": 1, "}": -1}.get(inner[i], 0)
                i += 1
            for pm in pdx.top_level_blocks(inner[um.end():i - 1]):
                body = flatten_blocks(pm.text[pm.text.index("{") + 1:-1])
                for k in re.findall(r"(?m)^\s*([a-z][a-z0-9_]*)\s*=\s*[^{\s]", body):
                    if k not in PM_META_KEYS and k not in goods:
                        err(f"buildings: {r} [{blk.key}.{pm.key}] '{k}' is not a goods")


_modifier_names: set[str] = set()


def engine_modifier_names() -> set[str]:
    """Modifier types the engine names in vanilla localisation, plus modifier_type_definitions."""
    if not _modifier_names:
        base = GAME / "main_menu/localization/english"
        for p in base.rglob("*.yml"):
            _modifier_names.update(re.findall(r"MODIFIER_TYPE_NAME_([a-z0-9_]+)", p.read_text(encoding="utf-8-sig", errors="replace")))
        _modifier_names.update(modifier_types())
    return _modifier_names


MODIFIER_BLOCK = re.compile(r"\b(modifier|raw_modifier|country_modifier|location_modifier|capital_country_modifier|"
                            r"modifier_while_progressing|owner_modifier|province_modifier)\s*=\s*\{")
MODIFIER_DIRS = ("common/advances", "common/age", "common/building_types", "common/government_reforms",
                 "common/estate_privileges", "common/laws", "common/static_modifiers", "common/international_organizations")


ADVANCE_FIELDS = {"age", "icon", "requires", "government", "country_type", "allow", "potential", "for", "depth",
                  "ai_weight", "allow_children", "in_tree_of", "research_cost"}


def mod_goods() -> set[str]:
    return {k for k in db_keys("in_game/common/goods")}


def is_modifier_name(k: str, names: set[str]) -> bool:
    if k in names:
        return True
    # goods-generated modifiers exist for mod goods too (global_tsin_electricity_output_modifier)
    m = re.match(r"(?:global|local)_(\w+?)_(?:output_modifier|pop_demand)$", k) or re.match(r"can_extract_(\w+)$", k)
    return bool(m and m.group(1) in mod_goods())


def flatten_blocks(text: str) -> str:
    """Collapse nested { } blocks to a placeholder so only depth-1 keys remain."""
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r"\{[^{}]*\}", "BLOCK", text)
    return text


def check_modifiers() -> None:
    """Keys inside modifier blocks must be modifier types the engine knows (catches typos in new content)."""
    names = engine_modifier_names()
    for p in mod_files((".txt",)):
        r = rel(p)
        if p.name.startswith("zzz_") or not any(d in r for d in MODIFIER_DIRS):
            continue
        clean = pdx.strip_comments(pdx.read_text(p))
        blocks: list[str] = []
        if "static_modifiers" in r:
            blocks = [b.text[b.text.index("{") + 1:-1] for b in pdx.top_level_blocks(clean)]
        if "common/advances" in r:
            for b in pdx.top_level_blocks(clean):
                inner = flatten_blocks(b.text[b.text.index("{") + 1:-1])
                for k in re.findall(r"(?m)^\s*([a-z][a-z0-9_]*)\s*=\s*[^{\s]", inner):
                    if k not in ADVANCE_FIELDS and not k.startswith("unlock_") and not is_modifier_name(k, names):
                        err(f"modifiers: {r} [{b.key}] unknown advance modifier '{k}'")
        for m in MODIFIER_BLOCK.finditer(clean):
            depth, i = 1, m.end()
            while depth and i < len(clean):
                depth += {"{": 1, "}": -1}.get(clean[i], 0)
                i += 1
            blocks.append(clean[m.end():i - 1])
        for inner in blocks:
            flat = flatten_blocks(inner)
            for k in re.findall(r"(?m)^\s*([a-z][a-z0-9_]*)\s*=\s*[^{\s]", flat):
                if not is_modifier_name(k, names) and k not in ("game_data", "category", "decaying", "potential_trigger"):
                    err(f"modifiers: {r} unknown modifier type '{k}'")


# ---------------------------------------------------------------- gfx

def gfx_exists(rel_path: str) -> bool:
    roots = [GAME / "main_menu", GAME / "in_game", MOD / "main_menu", MOD / "in_game"]
    roots += [d / sub for d in (GAME / "dlc").glob("*") for sub in ("main_menu", "in_game")]
    return any((r / rel_path).exists() for r in roots)


def check_gfx() -> None:
    for p in mod_files((".txt",)):
        if p.name.startswith("zzz_tsin_age7_"):
            continue
        r = rel(p)
        clean = pdx.strip_comments(pdx.read_text(p))
        if "common/advances" in r:
            for icon in re.findall(r"\bicon\s*=\s*(\w+)", clean):
                if not gfx_exists(f"gfx/interface/advance/{icon}.dds"):
                    err(f"gfx: {r} advance icon {icon} has no gfx/interface/advance/{icon}.dds")
        for path in re.findall(r'\bimage\s*=\s*"([^"]+)"', clean):
            if not gfx_exists(path):
                err(f"gfx: {r} image {path} not found")
        if "common/institution" in r:
            for b in pdx.top_level_blocks(clean):
                for sub in ("icons/institutions", "illustrations/institutions"):
                    if not gfx_exists(f"gfx/interface/{sub}/{b.key}.dds"):
                        err(f"gfx: institution {b.key} has no gfx/interface/{sub}/{b.key}.dds")
        if "map_modes" in r:
            for b in pdx.top_level_blocks(clean):
                if b.key.startswith("@"):
                    continue
                if not gfx_exists(f"gfx/interface/icons/map_modes/{b.key}.dds"):
                    err(f"gfx: map mode {b.key} has no gfx/interface/icons/map_modes/{b.key}.dds")
        if "common/building_types" in r:
            for b in pdx.top_level_blocks(clean):
                if not gfx_exists(f"gfx/interface/icons/buildings/{b.key}.dds"):
                    err(f"gfx: building {b.key} has no gfx/interface/icons/buildings/{b.key}.dds")
            for kind, icon in re.findall(r"\bicon_type\s*=\s*(\w+)\s+icon\s*=\s*(\w+)", clean):
                path = {
                    "goods": f"gfx/interface/icons/trade_goods/icon_goods_{icon}.dds",
                    "building_type": f"gfx/interface/icons/buildings/{icon}.dds",
                }.get(kind)
                if path and not gfx_exists(path):
                    err(f"gfx: {r} production method icon {kind}/{icon} has no {path}")
        if "common/industry_types" in r:
            for b in pdx.top_level_blocks(clean):
                if not gfx_exists(f"gfx/interface/icons/industry_types/{b.key}.dds"):
                    err(f"gfx: industry type {b.key} has no gfx/interface/icons/industry_types/{b.key}.dds")
        if "common/goods/" in r:
            for b in pdx.top_level_blocks(clean):
                for path in (f"gfx/interface/icons/trade_goods/icon_goods_{b.key}.dds",
                             f"gfx/interface/icons/trade_goods/illustrations/icon_goods_{b.key}.dds"):
                    if not gfx_exists(path):
                        err(f"gfx: goods {b.key} has no {path}")
        if "common/modifier_icons" in r:
            for path in re.findall(r'"(gfx/[^"]+\.dds)"', clean):
                if not gfx_exists(path):
                    err(f"gfx: {r} modifier icon {path} not found")


# ---------------------------------------------------------------- localisation

LOC_LINE = re.compile(r'^\s+([A-Za-z0-9_.\-]+):\d*\s*"', re.M)


def loc_keys(lang: str) -> set[str]:
    keys: set[str] = set()
    for root in (GAME, MOD):
        base = root / "main_menu/localization" / lang
        if base.exists():
            for p in base.rglob("*.yml"):
                keys.update(LOC_LINE.findall(p.read_text(encoding="utf-8-sig", errors="replace")))
    return keys


LOC_DBS = {
    "in_game/common/institution": ["{k}", "{k}_desc"],
    "in_game/common/advances": ["{k}", "{k}_desc"],
    "in_game/common/goods": ["{k}"],
    "in_game/common/building_types": ["{k}", "{k}_desc"],
    "in_game/common/industry_types": ["{k}", "{k}_desc"],
    "main_menu/common/static_modifiers": ["STATIC_MODIFIER_NAME_{k}"],
    "in_game/common/situations": ["{k}", "{k}_desc"],
    "in_game/common/disasters": ["{k}", "{k}_desc"],
    "in_game/common/laws": ["{k}", "{k}_desc"],
    "in_game/common/movements": ["{k}", "{k}_desc"],
    "in_game/common/cabinet_actions": ["{k}", "{k}_desc"],
    "in_game/common/decisions": ["{k}.title", "{k}.desc"],
    "in_game/common/parliament_issues": ["{k}", "{k}_desc"],
    "in_game/common/parliament_agendas": ["{k}", "{k}_desc"],
    "in_game/common/estate_privileges": ["{k}", "{k}_desc"],
    "in_game/common/casus_belli": ["{k}", "{k}_desc"],
    "in_game/common/missions": ["{k}", "{k}_DESCRIPTION"],
    "in_game/common/government_reforms": ["{k}", "{k}_desc"],
    "in_game/common/age": ["{k}", "{k}_desc", "age_format_{k}"],
}


def check_loc() -> None:
    langs = {lang: loc_keys(lang) for lang in ("english", "korean")}
    # file format
    for p in (MOD / "main_menu/localization").rglob("*.yml") if (MOD / "main_menu/localization").exists() else []:
        lang = p.parent.name
        first = p.read_text(encoding="utf-8-sig", errors="replace").split("\n", 1)[0].strip()
        if first != f"l_{lang}:":
            err(f"loc: {rel(p)} first line should be 'l_{lang}:'")
        if not p.name.endswith(f"_l_{lang}.yml"):
            err(f"loc: {rel(p)} name should end with _l_{lang}.yml")
    needed: list[tuple[str, str]] = []
    for d, pats in LOC_DBS.items():
        base = MOD / d
        if not base.exists():
            continue
        for p in base.rglob("*.txt"):
            if p.name.startswith("zzz_tsin_age7_"):
                continue
            for b in pdx.top_level_blocks(pdx.read_text(p)):
                if b.local_kind or ":" in b.key or not (b.key.startswith("tsin_") or b.key.startswith("age_7")):
                    continue
                for pat in pats:
                    needed.append((pat.format(k=b.key), rel(p)))
    # events
    ev = MOD / "in_game/events"
    if ev.exists():
        for p in ev.rglob("tsin_*.txt"):
            clean = pdx.strip_comments(pdx.read_text(p))
            for k in re.findall(r"\b(?:title|desc|name)\s*=\s*([A-Za-z0-9_.]+)", clean):
                if "." in k and k.startswith("tsin_"):
                    needed.append((k, rel(p)))
    # map modes: name, description, legend and tooltip keys
    mm = MOD / "in_game/gfx/map/map_modes"
    if mm.exists():
        for p in mm.rglob("*.txt"):
            clean = pdx.strip_comments(pdx.read_text(p))
            for b in pdx.top_level_blocks(clean):
                if b.key.startswith("@"):
                    continue
                needed.append((f"mapmode_{b.key}_name", rel(p)))
                needed.append((f"MAPMODE_{b.key.upper()}", rel(p)))
                for k in re.findall(r'\bdesc\s*=\s*"?([A-Z0-9_]+)"?', b.text):
                    needed.append((k, rel(p)))
                tt = re.search(r"\btooltip_key\s*=\s*\{", b.text)
                if tt:
                    inner = b.text[tt.end():]
                    depth, i = 1, 0
                    while depth and i < len(inner):
                        depth += {"{": 1, "}": -1}.get(inner[i], 0)
                        i += 1
                    for k in re.findall(r"\bvalue\s*=\s*([A-Z][A-Z0-9_]+)\b", inner[:i]):
                        needed.append((k, rel(p)))
    for key, where in needed:
        for lang, keys in langs.items():
            if key not in keys:
                err(f"loc: missing {lang} '{key}' ({where})")


# ---------------------------------------------------------------- scans

RE_CONCEPT_LINK = re.compile(r"\[(?:Concept\(\s*'(\w+)'[^\]]*|(\w+))\|[eE]\]")


def concept_names(root: Path) -> tuple[dict[str, str], set[str]]:
    """({concept key: block text}, keys and aliases) of the game_concepts in root."""
    blocks: dict[str, str] = {}
    names: set[str] = set()
    base = root / "main_menu/common/game_concepts"
    for p in sorted(base.glob("*.txt")) if base.exists() else []:
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            blocks[b.key] = b.text
            names.add(b.key)
            m = re.search(r"\balias\s*=\s*\{([^{}]*)\}", pdx.strip_comments(b.text))
            if m:
                names.update(m.group(1).split())
    return blocks, names


def check_concepts() -> None:
    """Mod concepts have english/korean name and desc, an icon and a known family; every [x|e] link
    in mod localization names a concept (vanilla or mod, key or alias)."""
    vanilla_blocks, vanilla_names = concept_names(GAME)
    mod_blocks, mod_names = concept_names(MOD)
    known = vanilla_names | mod_names
    langs = {lang: loc_keys(lang) for lang in ("english", "korean")}
    for k, text in mod_blocks.items():
        clean = pdx.strip_comments(text)
        for lang, keys in langs.items():
            for loc in (f"game_concept_{k}", f"game_concept_{k}_desc"):
                if loc not in keys:
                    err(f"concept: missing {lang} '{loc}'")
        tex = re.search(r'\btexture\s*=\s*"([^"]+)"', clean)
        if not tex:
            err(f"concept: {k} has no texture")
        elif not gfx_exists(f"gfx/interface/icons/{tex.group(1)}.dds"):
            err(f"concept: {k} texture gfx/interface/icons/{tex.group(1)}.dds not found")
        fam = re.search(r"\bfamily\s*=\s*(\w+)", clean)
        if fam and fam.group(1) not in vanilla_blocks and fam.group(1) not in mod_blocks:
            err(f"concept: {k} family {fam.group(1)} is not a concept")
    base = MOD / "main_menu/localization"
    for p in sorted(base.rglob("*.yml")) if base.exists() else []:
        text = p.read_text(encoding="utf-8-sig", errors="replace")
        for m in RE_CONCEPT_LINK.finditer(text):
            name = m.group(1) or m.group(2)
            if name not in known:
                err(f"concept: {rel(p)} links [{name}|e], which is not a concept or alias")


LOAD_ORDER_REFS = {
    "in_game/common/advances": "requires",
    "in_game/common/building_types": "obsolete",
    "in_game/common/unit_types": "copy_from",
}
EVENT_OUTCOMES = {"positive", "negative", "neutral"}


def depth1(block_text: str) -> str:
    """Text of a block at its first nesting level only."""
    c = pdx.strip_comments(block_text)
    inner = c[c.index("{") + 1:c.rindex("}")]
    depth, out = 0, []
    for ch in inner:
        if ch == "{":
            depth += 1
        if depth == 0:
            out.append(ch)
        if ch == "}":
            depth -= 1
    return "".join(out)


def check_load_order() -> None:
    """References the game resolves while reading: the target must be read earlier (file name order)."""
    for d, field in LOAD_ORDER_REFS.items():
        files = sorted((MOD / d).glob("*.txt"), key=lambda p: p.name)
        pos: dict[str, tuple[int, int, str]] = {}
        parsed = []
        for fi, p in enumerate(files):
            blocks = pdx.top_level_blocks(pdx.read_text(p))
            parsed.append((fi, p, blocks))
            for b in blocks:
                pos[b.key] = (fi, b.start, p.name)
        for fi, p, blocks in parsed:
            for b in blocks:
                for m in re.finditer(rf"\b{field}\s*=\s*(\w+)", pdx.strip_comments(b.text)):
                    target = pos.get(m.group(1))
                    if target and (target[0], target[1]) > (fi, b.start):
                        err(f"load order: {rel(p)} {b.key} {field} = {m.group(1)} is defined later "
                            f"({target[2]}); the reference is dropped")


def illustration_tags() -> set[str]:
    tags: set[str] = set()
    for p in (GAME / "in_game/events").rglob("*.txt"):
        for m in re.finditer(r"illustration_tags\s*=\s*\{([^{}]*)\}", pdx.read_text(p)):
            tags.update(re.findall(r"=\s*(\w+)", m.group(1)))
    return tags


def check_events() -> None:
    """Event-level `outcome`, no database prefixes on event ids, known illustration tags."""
    tags = illustration_tags()
    for p in sorted((MOD / "in_game/events").rglob("*.txt")):
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            if b.local_kind or not re.match(r"^[\w:]+\.\d+$", b.key):
                continue
            if ":" in b.key:
                err(f"event: {rel(p)} {b.key}: events take no REPLACE:/INJECT: prefix (redefine the id instead)")
            top = depth1(b.text)
            m = re.search(r"\boutcome\s*=\s*(\w+)", top)
            if not m:
                err(f"event: {rel(p)} {b.key} has no outcome (positive/negative/neutral)")
            elif m.group(1) not in EVENT_OUTCOMES:
                err(f"event: {rel(p)} {b.key} outcome = {m.group(1)} (positive/negative/neutral)")
            for t in re.findall(r"illustration_tags\s*=\s*\{([^{}]*)\}", pdx.strip_comments(b.text)):
                for tag in re.findall(r"=\s*(\w+)", t):
                    if tags and tag not in tags:
                        err(f"event: {rel(p)} {b.key} unknown illustration tag {tag}")


def prefix_scan() -> None:
    ws = pdx.workshop_root()
    pat = re.compile(r"\b(tsin_\w+|age_7_industrialization)\b")
    hits = defaultdict(set)
    for p in ws.rglob("*"):
        if p.suffix not in (".txt", ".yml", ".gui") or not p.is_file():
            continue
        for m in pat.findall(p.read_text(encoding="utf-8-sig", errors="ignore")):
            hits[p.relative_to(ws).parts[0]].add(m)
    if hits:
        for mod_id, names in sorted(hits.items()):
            warn(f"prefix: workshop {mod_id} uses {sorted(names)[:5]}")
    print(f"prefix scan: {len(hits)} workshop mods use tsin_/age_7 names")


def compat_scan() -> None:
    mine = set()
    for p in mod_files((".txt",)):
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            if b.key.startswith(("TRY_REPLACE:", "REPLACE:", "TRY_INJECT:", "INJECT:")):
                mine.add(b.key.split(":", 1)[1])
    ws = pdx.workshop_root()
    touched = defaultdict(set)
    for p in ws.rglob("*.txt"):
        try:
            blocks = pdx.top_level_blocks(pdx.read_text(p))
        except Exception:  # noqa: BLE001
            continue
        for b in blocks:
            name = b.key.split(":", 1)[-1]
            if name in mine:
                touched[name].add(p.relative_to(ws).parts[0])
    for name, mods in sorted(touched.items()):
        warn(f"compat: {name} also defined/replaced by workshop {sorted(mods)}")
    print(f"compat scan: {len(touched)} of {len(mine)} replaced objects are also touched by workshop mods")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix-bom", action="store_true")
    ap.add_argument("--prefix-scan", action="store_true")
    ap.add_argument("--compat", action="store_true")
    ap.add_argument("--skip", default="", help="comma list: bom,braces,keys,refs,names,gfx,loc,order,events,concepts")
    a = ap.parse_args()
    skip = set(filter(None, a.skip.split(",")))
    if a.prefix_scan:
        prefix_scan()
    elif a.compat:
        compat_scan()
    else:
        if "bom" not in skip:
            check_bom(a.fix_bom)
        if "braces" not in skip:
            check_braces()
        if "keys" not in skip:
            check_keys()
        if "refs" not in skip:
            check_refs()
        if "modifiers" not in skip:
            check_modifiers()
        if "buildings" not in skip:
            check_buildings()
        if "names" not in skip:
            check_tsin_names()
        if "gfx" not in skip:
            check_gfx()
        if "loc" not in skip:
            check_loc()
        if "order" not in skip:
            check_load_order()
        if "events" not in skip:
            check_events()
        if "concepts" not in skip:
            check_concepts()
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
