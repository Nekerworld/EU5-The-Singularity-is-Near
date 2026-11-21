import re
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdx
from gen_rgo_rank_balance import build, rank_text, RANK_RGO
from era_layout import entries


class NativeCholeraTests(unittest.TestCase):
    def test_registered_disease_and_mirrors(self):
        rel = 'in_game/common/diseases/tsin_cholera.txt'
        source, mirror, _ = entries()[rel]
        self.assertEqual(source.read_bytes(), mirror.read_bytes())
        text = pdx.read_text(mirror)
        blocks = pdx.top_level_blocks(text)
        self.assertEqual([x.key for x in blocks], ['tsin_cholera_disease'])
        self.assertIn('monthly_spawn_chance = { value = 0 }', text)
        self.assertIn('mortality_rate = { 0.02 0.04 }', text)
        self.assertIn('has_building_with_at_least_one_level = tsin_waterworks', text)

    def test_no_double_population_damage_or_reset_of_legacy_progress(self):
        text = pdx.read_text(pdx.MOD_ROOT / 'in_game/events/tsin_cholera.txt')
        outbreak = next(x.text for x in pdx.top_level_blocks(text) if x.key == 'tsin_cholera.2')
        self.assertNotIn('add_pop_size', outbreak)
        self.assertNotIn('every_pop', outbreak)
        self.assertIn('tsin_cholera_seed_native_outbreak = yes', outbreak)
        disaster = pdx.read_text(pdx.MOD_ROOT / 'in_game/common/disasters/tsin_cholera.txt')
        self.assertNotIn('global_population_growth', disaster)
        monthly = disaster[disaster.index('on_monthly ='):disaster.index('on_end =')]
        self.assertIn('NOT = { has_variable = tsin_cholera_native_initialized }', monthly)
        self.assertNotIn('name = tsin_cholera_progress value = 0', monthly)

    def test_seed_limited_and_does_not_overwrite_existing_infection(self):
        text = pdx.read_text(pdx.MOD_ROOT / 'in_game/common/scripted_effects/tsin_cholera_disease_effects.txt')
        self.assertIn('var:tsin_cholera_outbreaks < tsin_cholera_max_outbreaks', text)
        self.assertEqual(text.count('NOT = { disease_has_outbreak_here = disease:tsin_cholera_disease }'), 2)
        self.assertIn('disease_outbreak = disease:tsin_cholera_disease.original_outbreak', text)
        self.assertIn('spawn_disease = { disease = disease:tsin_cholera_disease value = 0.1 }', text)


class RgoRankBalanceTests(unittest.TestCase):
    def test_native_rules_other_than_rgo_are_preserved(self):
        original = (pdx.game_root() / 'in_game/common/location_ranks/00_default.txt').read_text(encoding='utf-8-sig')
        before = {b.key:b.text for b in pdx.top_level_blocks(original)}
        after = {b.key:b.text for b in pdx.top_level_blocks(rank_text(original))}
        def normalized(text):
            text = re.sub(r'local_max_rgo_size_modifier\s*=\s*[-\d.]+', '', pdx.strip_comments(text))
            return re.sub(r'\s+', '', text)
        self.assertEqual(set(before), set(after))
        for rank in before:
            self.assertEqual(normalized(before[rank]), normalized(after[rank]), rank)

    def test_rank_bonuses_and_population_boundary(self):
        outputs = build()
        text = outputs['in_game/common/location_ranks/00_default.txt']
        ranks = {b.key:b.text for b in pdx.top_level_blocks(text)}
        for rank, value in RANK_RGO.items():
            found = re.findall(r'local_max_rgo_size_modifier\s*=\s*([-\d.]+)', ranks[rank])
            self.assertEqual(found, [f'{value:.2f}'] if value else [], rank)
        auto = outputs['in_game/common/auto_modifiers/tsin_rgo_rank_balance.txt']
        self.assertIn('type = location', auto)
        self.assertIn('location_rank ?= location_rank:city', auto)
        self.assertIn('population >= 100', auto)
        self.assertIn('local_max_rgo_size_modifier = -0.10', auto)
        # Scope exclusion matters: populous rural/town/metropolis locations must not lose 10%.
        for rank in RANK_RGO:
            for pop in (5, 30, 99.99, 100, 400, 1000):
                bonus = RANK_RGO[rank] - (0.10 if rank == 'city' and pop >= 100 else 0)
                expected = {'rural_settlement':.75,'town':.5,'city':.2 if pop >= 100 else .3,'megalopolis':0}[rank]
                self.assertAlmostEqual(bonus, expected)

    def test_no_extra_country_or_world_pulse_and_no_mining_grant(self):
        outputs = build()
        self.assertFalse(any('/on_action/' in path for path in outputs))
        joined = '\n'.join(outputs.values())
        self.assertNotIn('add_location_modifier', joined)
        self.assertNotIn('every_owned_location', joined)
        self.assertNotIn('chris_mining_town', joined)


if __name__ == '__main__':
    unittest.main()
