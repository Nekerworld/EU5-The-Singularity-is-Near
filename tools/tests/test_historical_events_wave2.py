from pathlib import Path
import json,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_historical_events_wave2 import build
from test_capital_markets import parse,predicate


class HistoricalSecondWaveTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((pdx.MOD_ROOT/'data/historical_events_wave2.json').read_text(encoding='utf-8'))
        self.files=build();self.events=self.files['in_game/events/tsin_history_wave2.txt']

    def test_six_chains_and_forty_three_unique_events_are_registered(self):
        keys=[b.key for b in pdx.top_level_blocks(self.events)]
        self.assertEqual(len(keys),43);self.assertEqual(len(set(keys)),43)
        self.assertEqual(len(self.data['chains']),6)
        manifest=json.loads((pdx.MOD_ROOT/'era_7/manifest.json').read_text())['files']
        self.assertTrue(all(rel in manifest for rel in self.files))

    def test_zero_risk_does_not_start_financial_chain_even_when_caches_exist(self):
        gate=next(c['gate'] for c in self.data['chains'] if c['id']=='boom')
        context={'tsin_company_count':5,'var:tsin_entry_risk_quarters':0,'var:tsin_stress_quarters':0,'flags':{'tsin_entry_risk_quarters','tsin_stress_quarters'}}
        self.assertFalse(predicate(parse(gate),context))
        context['var:tsin_stress_quarters']=1;self.assertTrue(predicate(parse(gate),context))

    def test_followups_are_bounded_and_do_not_fake_factory_or_army_state(self):
        for chain in self.data['chains']:
            self.assertEqual(self.events.count('current_year > var:tsin_hist2_'+chain['id']+'_year'),len(chain['stages'])-1)
        strike=next(c for c in self.data['chains'] if c['id']=='strike')
        self.assertIn('building_employed_amount > 0',strike['gate'])
        self.assertIn('is_opened = yes',strike['gate'])
        self.assertIn('army_size > 0',next(c['gate'] for c in self.data['chains'] if c['id']=='military'))
        self.assertNotIn('declare_war',str(self.files));self.assertNotIn('destroy_army',str(self.files))
        self.assertNotIn('research_advance',self.events)

    def test_visits_and_waterworks_use_actual_recorded_targets_and_can_end(self):
        effects=self.files['in_game/common/scripted_effects/tsin_history_wave2_effects.txt']
        hooks=self.files['in_game/common/on_action/tsin_history_wave2_on_actions.txt']
        self.assertIn('NOT = { has_variable = tsin_hist2_visit_origin }',effects)
        self.assertIn('has_building_with_at_least_one_level = tsin_machine_works',effects)
        self.assertIn('has_variable = tsin_hist2_mission_accepted',self.events)
        self.assertIn('var:tsin_hist2_stink_location ?= { owner = root has_building_with_at_least_one_level = tsin_waterworks }',self.events)
        self.assertIn('tsin_hist2_partners_review',hooks)
        self.assertIn('tsin_hist2_boundary_cleanup_effect = yes',hooks)
        self.assertIn('current_year >= 1900',hooks)
        self.assertNotIn('change_variable = { name = tsin_entry_risk_quarters',self.events)
        self.assertNotIn('tsin_capital_risk_effect = yes',self.events)

    def test_two_normal_four_dense_draws_are_player_only(self):
        hooks=self.files['in_game/common/on_action/tsin_history_wave2_on_actions.txt']
        callbacks=[b.text for b in pdx.top_level_blocks(hooks) if b.key.startswith('tsin_history2_draw_')]
        self.assertEqual(len(callbacks),4)
        self.assertEqual(sum('has_game_rule = tsin_historical_events_dense' in b for b in callbacks),2)
        self.assertTrue(all('is_ai = no' in b for b in callbacks))
        self.assertNotIn('monthly_country_pulse',hooks)


if __name__=='__main__':unittest.main()
