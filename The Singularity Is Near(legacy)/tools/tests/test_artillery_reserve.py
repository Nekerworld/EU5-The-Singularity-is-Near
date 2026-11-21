"""P-track (artillery reserves) static checks. Engine behaviour is NOT verified here (docs/p_track_probes.md)."""
from pathlib import Path
import re
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdx
from test_capital_markets import parse, get


def scalars(block_text):
    """Depth-1 `key = value` pairs of one block (tolerates bare tokens such as `gfx_tags = { heavy_tag }`)."""
    inner = pdx.strip_comments(block_text).split('{', 1)[1].rsplit('}', 1)[0]
    out, depth = [], 0
    for line in re.sub(r'([{}])', r'\n\1\n', inner).splitlines():
        line = line.strip()
        if line == '}':
            depth -= 1
        elif line == '{':
            depth += 1
        elif depth == 0 and '=' in line:
            k, _, v = line.partition('=')
            out.append((k.strip(), '=', v.strip()))
    return out


AGES = ['age_1_traditions', 'age_2_renaissance', 'age_3_discovery',
        'age_4_reformation', 'age_5_absolutism', 'age_6_revolutions']
# Vanilla 1.4.x values (00_age_templates_land.txt). Used for the "unchanged" checks and the formula check.
VANILLA_CP = dict(zip(AGES, [2, 3, 4, 5, 5.5, 7.5]))
VANILLA_BOMBARD = dict(zip(AGES, [0.1, 0.125, 0.15, 0.20, 0.25, 0.30]))
VANILLA_BARRAGE = dict(zip(AGES, [1, 3, 4, 5, 7, 9]))
VANILLA_MAX_STRENGTH = dict(zip(AGES, [0.1, 0.2, 0.6, 0.8, 1.0, 1.2]))
FRONT = ['left', 'center', 'right']

FORMATION = pdx.MOD_ROOT / 'in_game/common/unit_formation_preference/tsin_artillery_reserve.txt'
TEMPLATES = pdx.MOD_ROOT / 'in_game/common/unit_types/zzz_tsin_artillery_reserve_templates.txt'


def vanilla_templates():
    path = pdx.game_root() / 'in_game/common/unit_types/00_age_templates_land.txt'
    if not path.exists():
        return None
    return {b.key: scalars(b.text) for b in pdx.top_level_blocks(pdx.read_text(path))}


def load_templates():
    blocks = pdx.top_level_blocks(pdx.read_text(TEMPLATES))
    return {b.key.split(':')[-1]: (b.key, scalars(b.text)) for b in blocks}


class ArtilleryReserveTests(unittest.TestCase):
    def setUp(self):
        self.new = load_templates()
        self.vanilla = vanilla_templates()

    # --- formation -------------------------------------------------------
    def test_formation_is_new_non_default_and_front_has_no_artillery(self):
        blocks = pdx.top_level_blocks(pdx.read_text(FORMATION))
        self.assertEqual([b.key for b in blocks], ['tsin_artillery_reserve'])
        body = parse(blocks[0].text[blocks[0].text.index('{') + 1:-1])
        self.assertEqual(get(body, 'default'), 'no')
        self.assertEqual(get(body, 'army'), 'yes')
        for slot in FRONT:
            cats = [v for k, _, v in get(body, slot) if k.isdigit()]
            self.assertTrue(cats, slot)
            self.assertNotIn('army_artillery', cats, slot)
            self.assertNotIn('army_auxiliary', cats, slot)
        reserve = [v for k, _, v in get(body, 'reserves') if k.isdigit()]
        self.assertIn('army_artillery', reserve)

    def test_front_slots_match_vanilla_balanced_minus_artillery(self):
        van_path = pdx.game_root() / 'in_game/common/unit_formation_preference/army.txt'
        if not van_path.exists():
            self.skipTest('game install not found')
        van = {b.key: parse(b.text[b.text.index('{') + 1:-1]) for b in pdx.top_level_blocks(pdx.read_text(van_path))}
        mine = parse(pdx.top_level_blocks(pdx.read_text(FORMATION))[0].text.split('{', 1)[1].rsplit('}', 1)[0])
        for slot in FRONT:
            expect = [(k, v) for k, _, v in get(van['balanced_army'], slot) if k.isdigit() and v != 'army_artillery']
            got = [(k, v) for k, _, v in get(mine, slot) if k.isdigit()]
            self.assertEqual(got, expect, slot)
            self.assertEqual(get(get(mine, slot), 'max_frontage'), get(get(van['balanced_army'], slot), 'max_frontage'))

    def test_vanilla_army_formation_file_is_not_overridden(self):
        self.assertFalse((pdx.MOD_ROOT / 'in_game/common/unit_formation_preference/army.txt').exists())

    # --- templates ---------------------------------------------------------
    def test_all_six_age_templates_replaced_with_try_replace(self):
        self.assertEqual(sorted(self.new), sorted(f'a_{a}_artillery' for a in AGES))
        for key, (full, _) in self.new.items():
            self.assertEqual(full, 'TRY_REPLACE:' + key)

    def test_age7_templates_and_derived_units_are_not_touched(self):
        self.assertFalse(any('age_7' in k for k in self.new))
        text = pdx.read_text(TEMPLATES)
        for unit in ['a_houfnice', 'a_falconet', 'a_chambered_cannon', 'a_royal_mortar', 'a_flying_battery',
                     'a_tsin_breech_loading_battery', 'a_tsin_quick_firing_battery']:
            self.assertNotIn(unit + ' =', text)

    def test_artillery_cp_below_same_age_infantry_and_cavalry(self):
        if self.vanilla is None:
            self.skipTest('game install not found')
        for age in AGES:
            cp = float(get(self.new[f'a_{age}_artillery'][1], 'combat_power'))
            for cls in ['light_infantry', 'heavy_infantry', 'light_cavalry', 'heavy_cavalry']:
                other = float(get(self.vanilla[f'a_{age}_{cls}'], 'combat_power'))
                self.assertLess(cp, other, f'{age} artillery cp {cp} >= {cls} {other}')
            self.assertLess(cp, VANILLA_CP[age])

    def test_barrage_bombard_and_other_fields_unchanged_from_vanilla(self):
        for age in AGES:
            body = self.new[f'a_{age}_artillery'][1]
            self.assertEqual(float(get(body, 'bombard_efficiency')), VANILLA_BOMBARD[age], age)
            self.assertEqual(float(get(body, 'artillery_barrage')), VANILLA_BARRAGE[age], age)
            self.assertEqual(float(get(body, 'max_strength')), VANILLA_MAX_STRENGTH[age], age)
            self.assertEqual(get(body, 'category'), 'army_artillery')
            self.assertEqual(get(body, 'age'), f'"{age}"')
            if self.vanilla is not None:
                van = self.vanilla[f'a_{age}_artillery']
                for field in ['bombard_efficiency', 'artillery_barrage', 'max_strength']:
                    self.assertEqual(float(get(body, field)), float(get(van, field)), f'{age}.{field}')
                for field in ['category', 'age']:
                    self.assertEqual(get(body, field), get(van, field), f'{age}.{field}')
                self.assertEqual(float(get(van, 'combat_power')), VANILLA_CP[age], age)

    def test_damage_compensation_is_placeholder_formula(self):
        for age in AGES:
            body = self.new[f'a_{age}_artillery'][1]
            cp = float(get(body, 'combat_power'))
            bonus = float(get(body, 'strength_damage_done'))
            self.assertGreater(bonus, 0)
            self.assertLessEqual(bonus, 1.0)
            self.assertAlmostEqual(bonus, round(0.25 * (VANILLA_CP[age] / cp - 1), 2), places=2)
        self.assertIn('PLACEHOLDER', pdx.read_text(TEMPLATES).upper())

    def test_age7_artillery_values_unchanged_for_verification_only(self):
        # Age VII template is outside this track; record the current values so a silent edit is caught.
        text = pdx.read_text(pdx.MOD_ROOT / 'in_game/common/unit_types/tsin_00_age_templates.txt')
        block = next(b for b in pdx.top_level_blocks(text) if b.key == 'a_age_7_industrialization_artillery')
        body = scalars(block.text)
        self.assertEqual(float(get(body, 'combat_power')), 9.5)
        self.assertEqual(float(get(body, 'bombard_efficiency')), 0.40)
        self.assertEqual(float(get(body, 'artillery_barrage')), 11)


if __name__ == '__main__':
    unittest.main()
