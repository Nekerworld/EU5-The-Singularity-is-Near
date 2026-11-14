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
  refs     institution:/goods:/... references and requires/unlock_*/copy_from/unit/*_demand
           point at objects that exist (vanilla or mod)
  gfx      advance icons, event images, institution and map mode art exist (vanilla, DLC or mod)
  loc      tsin_ objects and event title/desc/option keys have english and korean entries
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
ENGINE_KEYS = {"debug_log", "change_global_variable"}


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


def check_refs() -> None:
    for p in mod_files((".txt",)):
        if p.name.startswith("zzz_tsin_age7_"):
            continue
        clean = pdx.strip_comments(pdx.read_text(p))
        for m in re.finditer(r"\b(" + "|".join(REF_PREFIX) + r"):([A-Za-z0-9_]+)", clean):
            kind, name = m.groups()
            if name not in db_keys(REF_PREFIX[kind]):
                err(f"refs: {rel(p)} {kind}:{name} not found")
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
    ap.add_argument("--skip", default="", help="comma list: bom,braces,keys,refs,names,gfx,loc")
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
        if "names" not in skip:
            check_tsin_names()
        if "gfx" not in skip:
            check_gfx()
        if "loc" not in skip:
            check_loc()
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
