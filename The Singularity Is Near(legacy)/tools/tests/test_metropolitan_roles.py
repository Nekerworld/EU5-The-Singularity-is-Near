import sys, unittest, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdx
from gen_metropolitan_regions import build, ROLES, BULK_STAGES
from gen_urban_projects import build as urban_build


class MetropolitanRoleTests(unittest.TestCase):
    def setUp(self):
        self.b = build()
        self.actions = self.b['in_game/common/generic_actions/tsin_metropolitan_regions.txt']
        self.effects = self.b['in_game/common/scripted_effects/tsin_metropolitan_regions.txt']
        self.auto = self.b['in_game/common/auto_modifiers/tsin_metropolitan_regions.txt']

    def test_one_role_action_per_role_only_for_core(self):
        for k, key, *_ in ROLES:
            block = f'tsin_metro_role_{key} = {{'
            self.assertIn(block, self.actions)
            self.assertIn('has_variable = tsin_metro_core', self.actions)
            self.assertIn(f'set_variable = {{ name = tsin_metro_role value = {k} }}', self.actions)
        # Role bonus only on the core (potential requires the role to be set on that location).
        for _, key, *_ in ROLES:
            self.assertIn(f'tsin_metro_role_{key}_modifier', self.auto)
        self.assertIn('has_variable = tsin_metro_role var:tsin_metro_role', self.auto)

    def test_role_needs_facility_or_population_condition(self):
        self.assertIn('total_building_levels >= 3', self.actions)
        self.assertIn('population >= 150', self.actions)
        self.assertIn('is_coastal = yes', self.actions)
        self.assertIn('tsin_location_industrial_jobs >= 1000', self.actions)

    def test_bulk_actions_recheck_per_site(self):
        for n in BULK_STAGES:
            self.assertIn(f'tsin_metro_bulk_{n} = {{', self.actions)
            self.assertIn(f'tsin_urban_project_gate_{n}_trigger = yes', self.actions)
            self.assertIn(f'tsin_urban_project_start_{n}_effect = yes', self.actions)
        self.assertIn('owner ?= scope:actor controller ?= scope:actor', self.actions)
        self.assertIn('var:tsin_metro_hub ?= scope:metro_core', self.actions)

    def test_bulk_cash_is_checked_before_charging(self):
        self.assertIn('scope:actor = { gold >= 300 }', self.actions)
        self.assertIn('scope:actor = { add_gold = -300 }', self.actions)

    def test_counters_and_hub_count_are_set(self):
        self.assertIn('tsin_metro_hubs', self.actions)
        self.assertIn('tsin_metro_sites', self.effects)
        self.assertIn('tsin_metro_broken', self.effects)
        self.assertIn('tsin_metro_review_serial', self.effects)
        self.assertNotIn('every_country', self.effects)

    def test_registry_module_present_with_metrics(self):
        from gen_metropolitan_regions import _registry_module
        m = _registry_module()
        ids = {x['id'] for x in m['metrics']}
        self.assertEqual(ids, {'metro_sites', 'metro_broken', 'metro_hubs'})
        for metric in m['metrics']:
            self.assertEqual(metric['frequency'], 'manual')
            self.assertIn('korean', metric['title'])
            self.assertIn('english', metric['title'])

    def test_localization_covers_every_new_key(self):
        for lang in ['korean', 'english']:
            text = self.b[f'main_menu/localization/{lang}/tsin_metropolitan_regions_l_{lang}.yml']
            for key in [f'tsin_metro_role_{k}' for _, k, *_ in ROLES] + [f'tsin_metro_bulk_{n}' for n in BULK_STAGES]:
                self.assertIn(f' {key}:', text)


class UrbanGateTests(unittest.TestCase):
    def test_urban_gate_and_start_outputs(self):
        b = urban_build()
        trig = b['in_game/common/scripted_triggers/tsin_urban_projects.txt']
        eff = b['in_game/common/scripted_effects/tsin_urban_projects.txt']
        for n in [1, 2, 3]:
            self.assertIn(f'tsin_urban_project_gate_{n}_trigger = {{', trig)
            self.assertIn(f'tsin_urban_project_start_{n}_effect = {{', eff)
        self.assertIn('tsin_is_urban_location = yes', trig)
        self.assertIn('NOT = { has_variable = tsin_urban_project_pending }', trig)


if __name__ == '__main__':
    unittest.main()
