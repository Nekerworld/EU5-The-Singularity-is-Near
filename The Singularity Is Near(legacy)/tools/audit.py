"""Release audit for The Singularity is Near: AI weights, localization parity, building economics, costly scopes.

  python tools/audit.py          print the report; exit code 1 if any error

Checks:
  ai     tsin advances that unlock content have ai_weight, tsin decisions have ai_will_do, every option of a
         visible tsin event with two or more options has ai_chance
  loc    each tsin_*_l_english.yml has a korean twin with the same keys and the same
         $refs$/[links]; korean values identical to english are reported as untranslated
  buildings  production methods marked debug_max_profit = mills_profit_margin earn output value /
         input cost within PROFIT_RANGE at default prices; buildings outside LEGACY_MULTI_GOOD produce one
         good, and every production method but the base one is unlocked by an advance
  perf   world-wide scans (any_/every_/random_country, any_/every_location) inside yearly or
         monthly country pulses and scriptable hints, which run per country or per frame
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pdx  # noqa: E402

MOD = pdx.MOD_ROOT
errors: list[str] = []
warnings: list[str] = []


def rel(p: Path) -> str:
    return str(p.relative_to(MOD)).replace("\\", "/")


def own_files(folder: str) -> list[Path]:
    base = MOD / folder
    from era_layout import entries
    files = set(base.glob("*.txt")) if base.exists() else set()
    files.update(MOD / rel for rel in entries(MOD)
                 if Path(rel).parent == Path(folder) and rel.endswith('.txt'))
    return sorted(p for p in files if p.name.startswith(("tsin_", "zz_tsin_")))


def child_blocks(block_text: str, key: str) -> list[str]:
    """Direct `key = { ... }` children of a block (depth 1 only)."""
    clean = pdx.strip_comments(block_text)
    body_start = clean.find("{") + 1
    out = []
    depth = 0
    i = body_start
    pat = re.compile(rf"{re.escape(key)}\s*=\s*\{{")
    while i < len(clean):
        c = clean[i]
        if c == "{":
            depth += 1
        elif c == "}":
            if depth == 0:
                break
            depth -= 1
        elif depth == 0:
            m = pat.match(clean, i)
            if m and (i == 0 or not (clean[i - 1].isalnum() or clean[i - 1] == "_")):
                close = pdx.matching_brace(clean, m.end() - 1)
                out.append(clean[i:close + 1])
                i = close + 1
                continue
        i += 1
    return out


def check_ai() -> None:
    # Vanilla weights only ~5% of advances, so only advances that unlock something must carry one.
    for p in own_files("in_game/common/advances"):
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            text = pdx.strip_comments(b.text)
            if re.search(r"\bunlock_\w+", text) and "ai_weight" not in text:
                errors.append(f"ai: {rel(p)}: advance {b.key} unlocks content but has no ai_weight")
    for p in own_files("in_game/common/decisions"):
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            if "ai_will_do" not in pdx.strip_comments(b.text):
                errors.append(f"ai: {rel(p)}: decision {b.key} has no ai_will_do")
    for p in sorted((MOD / "in_game/events").glob("tsin_*.txt")):
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            if "." not in b.key:
                continue
            clean = pdx.strip_comments(b.text)
            if re.search(r"\bhidden\s*=\s*yes", clean):
                continue
            options = child_blocks(b.text, "option")
            if len(options) < 2 or all(child_blocks(o, "trigger") for o in options):
                continue
            for n, opt in enumerate(options, 1):
                if "ai_chance" not in opt:
                    name = re.search(r"\bname\s*=\s*(\S+)", opt)
                    errors.append(f"ai: {rel(p)}: {b.key} option {name.group(1) if name else n} has no ai_chance")


_LOC_RE = re.compile(r'^\s+([A-Za-z0-9_.\-]+):\d*\s+"(.*)"\s*$')
# Data functions and $refs$ must match; concept links ([x|e]) may differ in number between languages.
_TOKEN_RE = re.compile(r"\$[A-Za-z0-9_]+(?:\|[A-Za-z0-9]+)?\$|\[[^\]|]*\([^\]]*\)[^\]]*\]")
_LANGUAGE_ONLY = {"$mapmode_common_start$"}


def load_loc(path: Path) -> dict[str, str]:
    out = {}
    for line in pdx.read_text(path).splitlines():
        m = _LOC_RE.match(line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def check_loc() -> None:
    en_dir = MOD / "main_menu/localization/english"
    ko_dir = MOD / "main_menu/localization/korean"
    for en_path in sorted(en_dir.glob("tsin_*_l_english.yml")):
        ko_path = ko_dir / en_path.name.replace("_l_english", "_l_korean")
        if not ko_path.exists():
            errors.append(f"loc: {rel(en_path)} has no korean twin")
            continue
        en, ko = load_loc(en_path), load_loc(ko_path)
        for k in sorted(en.keys() - ko.keys()):
            errors.append(f"loc: {k} missing in {rel(ko_path)}")
        for k in sorted(ko.keys() - en.keys()):
            errors.append(f"loc: {k} missing in {rel(en_path)}")
        for k in sorted(en.keys() & ko.keys()):
            e, o = en[k], ko[k]
            en_tokens = sorted(t for t in _TOKEN_RE.findall(e) if t not in _LANGUAGE_ONLY)
            ko_tokens = sorted(t for t in _TOKEN_RE.findall(o) if t not in _LANGUAGE_ONLY)
            if en_tokens != ko_tokens:
                warnings.append(f"loc: {k}: data functions or $refs$ differ between english and korean")
            words = re.sub(_TOKEN_RE, "", e)
            reference_only = re.fullmatch(r"[A-Z0-9_]+|\[[A-Za-z0-9_]+\|e\]", e)
            machine_read = k.endswith("_log_line")  # parsed by tools/observer_report.py, same in every language
            if e == o and not reference_only and not machine_read and re.search(r"[A-Za-z]{3,}", words):
                warnings.append(f"loc: {k}: korean text is identical to english (untranslated?)")


_WORLD_SCAN = re.compile(r"\b(any_country|every_country|random_country|ordered_country|any_location|every_location|random_location)\s*=")
_PULSES = ("yearly_country_pulse", "monthly_country_pulse", "quarterly_country_pulse", "biyearly_country_pulse")


def check_perf() -> None:
    on_action = MOD / "in_game/common/on_action/tsin_on_actions.txt"
    blocks = {b.key: b for b in pdx.top_level_blocks(pdx.read_text(on_action))}
    pulse_children: set[str] = set()
    for pulse in _PULSES:
        if pulse in blocks:
            pulse_children.update(re.findall(r"\b(tsin_\w+)", pdx.strip_comments(blocks[pulse].text)))
    events = {}
    for p in sorted((MOD / "in_game/events").glob("tsin_*.txt")):
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            events[b.key] = (p, b)
    for name in sorted(pulse_children):
        b = blocks.get(name)
        if not b:
            continue
        text = pdx.strip_comments(b.text)
        for m in _WORLD_SCAN.finditer(text):
            warnings.append(f"perf: on_action {name} (country pulse) scans the world with {m.group(1)}")
        for ev in re.findall(r"\b(tsin_\w+\.\d+)", text):
            if ev in events:
                p, eb = events[ev]
                trig = child_blocks(eb.text, "trigger")
                for m in _WORLD_SCAN.finditer(trig[0] if trig else ""):
                    warnings.append(f"perf: {ev} trigger (country pulse) scans the world with {m.group(1)}")
    for p in own_files("in_game/common/scriptable_hints"):
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            text = pdx.strip_comments(b.text)
            for m in re.finditer(r"\b(any_\w*location|every_\w*location|any_country|every_country)\s*=", text):
                warnings.append(f"perf: hint {b.key} (evaluated per frame) iterates with {m.group(1)}")


PROFIT_RANGE = (1.25, 1.5)
# Built before the one-good, tech-tier rule (0.7): alternative-input slots, documented in docs/economy_chain.md.
LEGACY_ALTERNATIVE_PMS = {"tsin_machine_works", "tsin_mechanized_textile_mill", "tsin_fertilizer_plant",
                          "tsin_explosives_plant"}
PROFIT_EXCEPTIONS = {"tsin_explosives_black_powder"}  # deliberately lower margin than nitroglycerin


def goods_prices() -> dict[str, float]:
    prices: dict[str, float] = {}
    for root in (pdx.game_root(), MOD):
        base = root / "in_game/common/goods"
        for p in sorted(base.glob("*.txt")) if base.exists() else []:
            for b in pdx.top_level_blocks(pdx.read_text(p)):
                m = re.search(r"\bdefault_market_price\s*=\s*([\d.]+)", pdx.strip_comments(b.text))
                if m:
                    prices[b.key.split(":", 1)[-1]] = float(m.group(1))
    return prices


def inner_blocks(block_text: str) -> list:
    body = block_text[block_text.find("{") + 1:block_text.rfind("}")]
    return pdx.top_level_blocks(body)


def check_buildings() -> None:
    prices = goods_prices()
    unlocked: set[str] = set()
    for p in own_files("in_game/common/advances"):
        unlocked.update(re.findall(r"\bunlock_production_method\s*=\s*(\w+)", pdx.strip_comments(pdx.read_text(p))))
    for p in own_files("in_game/common/building_types"):
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            if ":" in b.key:
                continue
            producing = []
            for group in child_blocks(b.text, "unique_production_methods"):
                for pm in inner_blocks(group):
                    clean = pdx.strip_comments(pm.text)
                    produced = re.search(r"\bproduced\s*=\s*(\w+)", clean)
                    output = re.search(r"\boutput\s*=\s*([\d.]+)", clean)
                    if not produced or not output:
                        continue
                    producing.append((pm.key, produced.group(1)))
                    if "mills_profit_margin" not in clean or pm.key in PROFIT_EXCEPTIONS:
                        continue
                    cost = sum(float(q) * prices[g] for g, q in re.findall(r"(?m)^\s*(\w+)\s*=\s*([\d.]+)\s*$", clean)
                               if g in prices)
                    if produced.group(1) not in prices or cost <= 0:
                        continue
                    ratio = float(output.group(1)) * prices[produced.group(1)] / cost
                    if not PROFIT_RANGE[0] <= ratio <= PROFIT_RANGE[1]:
                        warnings.append(f"buildings: {rel(p)}: {b.key}/{pm.key} earns {ratio:.2f}x its input cost "
                                        f"(expected {PROFIT_RANGE[0]}-{PROFIT_RANGE[1]})")
            if not producing or b.key in LEGACY_ALTERNATIVE_PMS:
                continue
            goods = sorted({g for _, g in producing})
            if len(goods) > 1:
                warnings.append(f"buildings: {rel(p)}: {b.key} produces {len(goods)} goods ({', '.join(goods)})")
            base = [pm for pm, _ in producing if pm not in unlocked]
            if len(base) > 1:
                warnings.append(f"buildings: {rel(p)}: {b.key} has {len(base)} production methods no advance unlocks "
                                f"({', '.join(base)}); tiers should be tech steps")


def main() -> int:
    check_ai()
    check_loc()
    check_buildings()
    check_perf()
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
