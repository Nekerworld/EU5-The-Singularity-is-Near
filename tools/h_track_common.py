"""Shared helpers for the H-track (HOI4 hybrid military, age VIII and later) generators.

Outputs are keyed 'era_N/<runtime path>' and written to the era authoring source,
then mirrored to the fixed EU5 runtime folder. Registration is limited to the
modules this track owns (era_8 and era_9) so parallel work in other eras is not touched.

All H-track content is unverified in game (docs/h0_engine_probes.md): 사용자 확인 필요.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pdx  # noqa: E402
import era_layout  # noqa: E402

ROOT = pdx.MOD_ROOT
H_MODULES = ('era_8', 'era_9')
BOM = '\ufeff'

# Land units added by H2. role -> used by triggers, counters and fuel/equipment demand.
# (id, role, parent template key, age, unlocking advance)
UNITS_08 = [
    ('a_tsin_armored_car_recon', 'armored', 'light_cavalry', 'tsin_armored_cars_advance'),
    ('a_tsin_tank_battalion', 'armored', 'heavy_cavalry', 'tsin_tank_warfare_advance'),
    ('a_tsin_mountain_paratroopers', 'infantry', 'light_infantry', 'tsin_airborne_infantry_advance'),
    ('a_tsin_mechanized_infantry', 'motorized', 'heavy_infantry', 'tsin_mechanized_infantry_advance'),
    ('a_tsin_self_propelled_battery', 'motorized', 'artillery', 'tsin_self_propelled_artillery_advance'),
    ('a_tsin_motor_supply_column', 'motorized', 'auxiliary', 'tsin_motor_supply_column_advance'),
]
UNITS_09 = [
    ('a_tsin_main_battle_tank', 'armored', 'a_tsin_tank_battalion', 'tsin_main_battle_tank_advance'),
    ('a_tsin_rocket_artillery_battery', 'motorized', 'a_tsin_self_propelled_battery', 'tsin_rocket_artillery_advance'),
]


class Loc:
    """Collects english/korean localization entries."""

    def __init__(self):
        self.entries = {'english': {}, 'korean': {}}

    def add(self, key, en, ko, en_desc=None, ko_desc=None):
        self.entries['english'][key] = en
        self.entries['korean'][key] = ko
        if en_desc is not None:
            self.entries['english'][key + '_desc'] = en_desc
            self.entries['korean'][key + '_desc'] = ko_desc if ko_desc is not None else en_desc

    def raw(self, key, en, ko):
        self.entries['english'][key] = en
        self.entries['korean'][key] = ko

    def files(self, era, name):
        out = {}
        for lang, entries in self.entries.items():
            body = ''.join(' ' + k + ': ' + json.dumps(v, ensure_ascii=False) + '\n' for k, v in entries.items())
            out[f'{era}/main_menu/localization/{lang}/{name}_l_{lang}.yml'] = 'l_' + lang + ':\n' + body
        return out


def tidy(text):
    return '\n'.join(line.rstrip() for line in text.replace('\r\n', '\n').splitlines()).strip('\n') + '\n'


def encode(value):
    if isinstance(value, bytes):
        return value
    return (BOM + value).encode('utf-8')


def building_asset(era, new, old):
    """Placeholder building art reused from an existing mod icon."""
    rel = f'main_menu/gfx/interface/icons/buildings/{new}.dds'
    source = ROOT / f'main_menu/gfx/interface/icons/buildings/{old}.dds'
    return f'{era}/{rel}', pdx.read_bytes(source)


def register(modules=H_MODULES):
    """Add unregistered sources of the given modules to their manifests (limited sync_eras --register)."""
    config = json.loads((ROOT / 'data/content_modules.json').read_text(encoding='utf-8-sig'))
    known = era_layout.entries(ROOT)
    claimed = {r.casefold() for r in known}
    changes = []
    for module in config['modules']:
        if module['id'] not in modules:
            continue
        folder = era_layout.safe_path(ROOT, module['folder'])
        path = folder / 'manifest.json'
        manifest = json.loads(path.read_text(encoding='utf-8-sig'))
        changed = False
        for sub in sorted(era_layout.RUNTIME_ROOTS):
            for source in sorted((folder / sub).rglob('*')):
                if not source.is_file():
                    continue
                rel = source.relative_to(folder).as_posix()
                if rel in manifest['files']:
                    continue
                runtime = era_layout.safe_path(ROOT, rel)
                if runtime.exists() or rel.casefold() in claimed:
                    raise ValueError(f'new era source conflicts with existing global/runtime file: {rel}')
                manifest['files'][rel] = 'new-era-content'
                claimed.add(rel.casefold())
                changed = True
        if changed:
            manifest['files'] = dict(sorted(manifest['files'].items()))
            changes.append((path, manifest))
    for path, manifest in changes:
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    era_layout.entries.cache_clear()
    era_layout.update_ignore(ROOT)


def mismatches(outputs):
    bad = []
    for key, value in outputs.items():
        era, rel = key.split('/', 1)
        data = encode(value)
        source = ROOT / key
        runtime = ROOT / rel
        if not source.is_file() or source.read_bytes() != data:
            bad.append(key)
        elif not runtime.is_file() or runtime.read_bytes() != data:
            bad.append(rel + ' (runtime mirror)')
    return bad


def write(outputs):
    for key, value in outputs.items():
        path = ROOT / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encode(value))
    register()
    era_layout.sync(ROOT)


def run(label, outputs, argv=None):
    parser = argparse.ArgumentParser(description=label)
    parser.add_argument('--check', action='store_true', help='read-only: compare with sources and runtime mirrors')
    args = parser.parse_args(argv)
    if args.check:
        bad = mismatches(outputs)
    else:
        write(outputs)
        bad = mismatches(outputs)
    print(f'{label}: {len(outputs)} files, {len(bad)} mismatches')
    for item in bad:
        print(item)
    return bool(bad)
