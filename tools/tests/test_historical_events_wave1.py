from pathlib import Path
import json,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_historical_events_wave1 import build


class HistoricalEventWaveTests(unittest.TestCase):
    def test_twenty_four_stable_events_and_six_era_sources_registered(self):
        files=build()
        text=files['in_game/events/tsin_history_wave1.txt']
        blocks=[b for b in pdx.top_level_blocks(text) if b.key.startswith('tsin_history_wave1.')]
        self.assertEqual(len(blocks),24)
        self.assertEqual({b.key for b in blocks},{'tsin_history_wave1.'+str(i) for i in range(1,25)})
        manifest=json.loads((pdx.MOD_ROOT/'era_7/manifest.json').read_text())['files']
        for rel in files:self.assertIn(rel,manifest)

    def test_choices_have_affordability_and_a_free_terminal_exit(self):
        text=build()['in_game/events/tsin_history_wave1.txt']
        for block in pdx.top_level_blocks(text):
            if not block.key.startswith('tsin_history_wave1.'):continue
            self.assertIn('name = '+block.key+'.b',block.text)
            self.assertIn('_stage value = 99',block.text)
            if 'change_gold_effect' in block.text:self.assertIn('gold >= tsin_gold_cost_2',block.text)
            self.assertIn('NOT = { has_game_rule = tsin_historical_events_off }',block.text)
            self.assertIn('current_year < ',block.text)

    def test_chain_has_no_same_year_advance_or_unbounded_delayed_queue(self):
        text=build()['in_game/events/tsin_history_wave1.txt']
        for chain in ['postage','dyes','workwear','cinema']:
            self.assertEqual(text.count(f'current_year > var:tsin_hist1_{chain}_year'),3)
            self.assertIn(f'NOT = {{ has_variable = tsin_hist1_{chain}_stage }}',text)
        self.assertNotIn('days =',text)
        self.assertNotIn('every_country',text)
        self.assertNotIn('tsin_flavor_events_this_year',text)
        self.assertNotIn('months = -1',text)
        self.assertIn('mode = replace',text)

    def test_technology_and_date_conditions_exclude_anachronistic_events(self):
        data=json.loads((pdx.MOD_ROOT/'data/historical_events_wave1.json').read_text(encoding='utf-8'))
        solos={r['id']:r for r in data['singles']}
        self.assertEqual(solos['aurora']['end_year'],1862)
        self.assertIn('tsin_internal_combustion_advance',solos['motor']['gate'])
        self.assertEqual(solos['pigeon']['gate'],'at_war = yes')
        for chain in data['chains']:
            self.assertEqual(len(chain['stages']),4)
            self.assertTrue(chain['source'].startswith('https://'))
