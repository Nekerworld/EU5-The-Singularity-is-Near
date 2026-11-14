"""Cross-file UI and execution wiring checks for TSIN.

Unlike syntax/reference checks, these reject defined features without a usable
entry point. The game remains necessary for layout and runtime validation.
"""
from __future__ import annotations
import re
from pathlib import Path
import pdx


def group_ids(text: str) -> dict[str, set[int]]:
    result: dict[str, set[int]] = {}
    for category, number in re.findall(r"GetMapModeGroupFromCategory\('([^']+)', '\(int32\)(\d+)'\)", text):
        result.setdefault(category, set()).add(int(number))
    return result


def check(root: Path, game: Path, hud: Path | None = None) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    counts: dict[str, int] = {}
    # A disaster/situation key is also its dynamically loaded GUI filename.
    for database, panel in [('disasters', 'disaster'), ('situations', 'situation')]:
        count = 0
        for p in sorted((root / 'in_game/common' / database).glob('*.txt')):
            for b in pdx.top_level_blocks(pdx.read_text(p)):
                if not b.key.startswith('tsin_'):
                    continue
                count += 1
                rel = Path('in_game/gui/panels') / panel / (b.key + '.gui')
                provider = next((r / rel for r in [root, game] if (r / rel).exists()), None)
                if provider is None:
                    errors.append(f'integration: {b.key}: missing panel {rel.as_posix()}')
                elif not any(x.key == panel + '_panel' for x in pdx.top_level_blocks(pdx.read_text(provider))):
                    errors.append(f'integration: {b.key}: panel must instantiate {panel}_panel')
        counts[database + '_panels'] = count
    native = game / 'in_game/gui/hud_bot.gui'
    ui_files = [native] + ([hud] if hud is not None and hud != native else [])
    maps = 0
    for p in sorted((root / 'in_game/gfx/map/map_modes').glob('*.txt')):
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            if not b.key.startswith('tsin_'):
                continue
            maps += 1
            category = re.search(r'\bcategory\s*=\s*(\w+)', b.text)
            index = re.search(r'\bindex\s*=\s*(\d+)', b.text)
            if category is None or index is None:
                errors.append(f'integration: {b.key}: missing category/index')
                continue
            for ui in ui_files:
                visible = group_ids(pdx.read_text(ui))
                if int(index[1]) not in visible.get(category[1], set()):
                    errors.append(f'integration: {b.key}: {category[1]} group {index[1]} is not displayed by {ui}')
    counts['map_modes'] = maps
    # Detect missing on_action callbacks, including callbacks buried in lists.
    definitions = set()
    action_bodies = []
    for p in sorted((root / 'in_game/common/on_action').glob('*.txt')):
        for block in pdx.top_level_blocks(pdx.read_text(p)):
            definitions.add(block.key)
            action_bodies.append(block.text)
    called = set()
    # Hooks merge across files: do not discard earlier on_actions lists.
    for body in action_bodies:
        for group in re.finditer(r'\bon_actions\s*=\s*\{([^{}]*)\}', pdx.strip_comments(body)):
            called.update(re.findall(r'\btsin_\w+\b', group[1]))
    for name in sorted(called - definitions):
        errors.append(f'integration: missing on_action callback {name}')
    counts['on_action_callbacks'] = len(called)
    # A localized literal label must not accidentally become a data-system call.
    bad_label = re.compile(r'\[TSIN\s+[^\]]*\]', re.I)
    count = 0
    for p in sorted((root / 'main_menu/localization').rglob('*.yml')):
        text = pdx.read_text(p)
        for line in text.splitlines():
            if line.lstrip().startswith('#'):
                continue
            if bad_label.search(line):
                errors.append(f'integration: {p.name}: literal TSIN label uses dynamic localization brackets')
        count += 1
    counts['localization_files'] = count
    registry = root / 'ui/dashboard_registry.json'
    if registry.exists():
        try:
            import json
            from gen_dashboard import build, validate_registry, check_provider_links
            data = json.loads(pdx.read_text(registry))
            metrics, statuses, shortcuts = validate_registry(data)
            counts.update(dashboard_metrics=len(metrics), dashboard_statuses=len(statuses), dashboard_shortcuts=len(shortcuts))
            for rel, expected in build(data).items():
                p = root / rel
                if not p.exists() or pdx.read_text(p) != expected:
                    errors.append(f'integration: generated dashboard file is outdated: {rel}')
            errors.extend('integration: dashboard ' + message for message in check_provider_links(data, root))
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f'integration: invalid dashboard registry: {exc}')
    return errors, counts


if __name__ == '__main__':
    errors, counts = check(pdx.MOD_ROOT, pdx.game_root())
    for message in errors:
        print('ERROR', message)
    print(counts)
    print(f'{len(errors)} integration errors')
    raise SystemExit(bool(errors))
