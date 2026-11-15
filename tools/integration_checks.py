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


def gui_structure_errors(text: str) -> list[str]:
    """Check GUI braces outside comments/strings, including escaped quotes."""
    clean = pdx.strip_comments(text)
    depth = 0
    quoted = escaped = False
    for i, char in enumerate(clean):
        if escaped:
            escaped = False
            continue
        if quoted and char == '\\':
            escaped = True
            continue
        if char == '"':
            quoted = not quoted
        elif not quoted:
            if char == '{': depth += 1
            elif char == '}':
                depth -= 1
                if depth < 0:
                    return [f'extra closing brace at line {clean.count(chr(10), 0, i)+1}']
    result = []
    if quoted: result.append('unclosed GUI string')
    if depth: result.append(f'{depth} unclosed GUI braces')
    return result


def check(root: Path, game: Path, hud: Path | None = None) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    from era_layout import check as check_era_layout
    errors.extend('integration: '+message for message in check_era_layout(root))
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
    era_registry = root / 'data/eras.json'
    if era_registry.exists():
        try:
            import json
            from gen_era_skeleton import build as build_eras, validate as validate_eras
            data = json.loads(pdx.read_text(era_registry))
            rows = validate_eras(data)
            counts.update(registered_mod_eras=len(rows), future_era_scaffolds=len(rows)-1)
            for rel, expected in build_eras(root, data).items():
                p = root / rel
                actual = (p.read_bytes() if isinstance(expected, bytes) else pdx.read_text(p)) if p.exists() else None
                if actual != expected:
                    errors.append(f'integration: generated era scaffold is outdated: {rel}')
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f'integration: invalid era registry: {exc}')
    operational_registry = root / 'ui/operational_alerts.json'
    if operational_registry.exists():
        try:
            import json
            from gen_operational_alerts import build as build_ops, validate as validate_ops
            data = json.loads(pdx.read_text(operational_registry))
            rules = validate_ops(data)
            counts['operational_warning_types'] = len(rules)
            native_alerts = {b.key for p in (game / 'in_game/common/alert_descriptions').glob('*.txt') for b in pdx.top_level_blocks(pdx.read_text(p))}
            for rule in rules:
                for alert in re.findall(r'is_alert_triggered\s*=\s*(\w+)', rule['condition']):
                    if alert not in native_alerts:
                        errors.append(f'integration: unknown native operational alert {alert}')
            for rel, expected in build_ops(data).items():
                p = root / rel
                if not p.exists() or pdx.read_text(p) != expected:
                    errors.append(f'integration: generated operational file is outdated: {rel}')
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f'integration: invalid operational registry: {exc}')
    if (root / 'tools/gen_stock_market_ui.py').exists():
        from gen_stock_market_ui import build as build_stock_ui
        try:
            generated = build_stock_ui(game)
            for rel, expected in generated.items():
                target = root / rel
                if not target.exists() or pdx.read_text(target) != expected:
                    errors.append(f'integration: stock economy entry or generated file is outdated: {rel}')
            counts['stock_company_cards'] = 6
        except ValueError as exc:
            errors.append(f'integration: stock economy integration: {exc}')
    # GUI syntax matters even when the scripted databases themselves are valid.
    for path in (root / 'in_game/gui').rglob('tsin_*.gui'):
        errors.extend(f'integration: {path.relative_to(root)}: {message}'
                      for message in gui_structure_errors(pdx.read_text(path)))
        for texture in re.findall(r'\btexture\s*=\s*"(gfx/[^"\[\]]+\.dds)"', pdx.read_text(path)):
            if not any((base / area / texture).is_file()
                       for base in [root, game] for area in ['main_menu', 'in_game', 'loading_screen']):
                errors.append(f'integration: missing GUI texture {texture} in {path.name}')
    # A top-level custom window must be explicitly instantiated by the engine.
    registrations = {}
    for p in (root / 'in_game/gui/scripted_widgets').glob('*.txt'):
        for path, window in re.findall(r'(?m)^\s*(gui/[^\s=]+)\s*=\s*(tsin_\w+)', pdx.read_text(p)):
            registrations[window] = path
    for p in (root / 'in_game/gui').glob('tsin_*.gui'):
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            if b.key != 'window': continue
            name = re.search(r'\bname\s*=\s*"(tsin_\w+)"', b.text)
            if name and registrations.get(name[1]) != 'gui/'+p.name:
                errors.append('integration: unregistered standalone window '+name[1])
    if (root / 'data/early_companies.json').exists():
        from gen_capital_markets import build as build_capital, all_companies
        for rel, expected in build_capital().items():
            if not (root / rel).exists() or pdx.read_text(root / rel) != expected:
                errors.append('integration: outdated capital-market file '+rel)
        counts['stock_company_cards'] = len(all_companies())
        from gen_historical_finance_bridge import build as build_history
        for rel, expected in build_history().items():
            if not (root / rel).exists() or pdx.read_text(root / rel) != expected:
                errors.append('integration: outdated historical finance bridge '+rel)

    # New history modules must be checked by the standard validator and release gate too.
    from importlib import import_module
    for generator in ['gen_historical_progression', 'gen_lucky_nations', 'gen_historical_events_wave1', 'gen_finance_ledger', 'gen_historical_nations', 'gen_border_trade', 'gen_ai_direction', 'gen_historical_restorations', 'gen_historical_events_wave2', 'gen_age8_transport_military']:
        if (root / ('tools/' + generator + '.py')).exists():
            try:
                module = import_module(generator)
                generated = module.build()
                if hasattr(module, 'assets'):
                    generated.update(module.assets())
                for rel, expected in generated.items():
                    target = root / rel
                    if not target.exists() or (pdx.read_bytes(target) if isinstance(expected, bytes) else pdx.read_text(target)) != expected:
                        errors.append('integration: outdated historical module ' + rel)
            except (ValueError, KeyError, TypeError) as exc:
                errors.append('integration: invalid historical module ' + generator + ': ' + str(exc))

    return errors, counts


if __name__ == '__main__':
    errors, counts = check(pdx.MOD_ROOT, pdx.game_root())
    for message in errors:
        print('ERROR', message)
    print(counts)
    print(f'{len(errors)} integration errors')
    raise SystemExit(bool(errors))
