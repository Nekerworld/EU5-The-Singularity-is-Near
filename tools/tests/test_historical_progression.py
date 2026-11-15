from pathlib import Path
import json
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_historical_progression import build


class HistoricalProgressionTests(unittest.TestCase):
    def test_review_never_mutates_ownership_cash_or_native_hex_state(self):
        files = build()
        effects = files['in_game/common/scripted_effects/tsin_historical_progression_effects.txt']
        for token in ['change_location_owner', 'annex_country', 'form_country', 'add_gold', 'remove_country', 'declare_war', 'set_variable = hex_']:
            self.assertNotIn(token, effects)
        self.assertIn('years = 1', effects)
        self.assertNotIn('monthly_country_pulse', '\n'.join(files.values()))

    def test_player_protection_includes_top_overlord_and_each_city_controller(self):
        files=build()
        triggers=files['in_game/common/scripted_triggers/tsin_historical_progression_triggers.txt']
        self.assertIn('top_overlord ?= { is_ai = no }',triggers)
        data=json.loads((pdx.MOD_ROOT/'data/historical_progression.json').read_text())
        for loc in data['russia']['protected_locations']:
            self.assertIn(f'location:{loc} = {{ OR = {{ owner ?= {{ tsin_history_human_realm = yes }} controller ?= {{ tsin_history_human_realm = yes }} }} }}',triggers)
        for guard in ['is_capital = no','is_port = no','is_market_center = no','controller = owner','at_war = no']:
            self.assertIn(guard,triggers)

    def test_report_localization_has_real_newline_escapes(self):
        files=build()
        for lang in ['english','korean']:
            text=files[f'main_menu/localization/{lang}/tsin_history_review_l_{lang}.yml']
            self.assertNotIn('\\\\n',text)
            self.assertIn('\\n',text)
            self.assertIn('tsin_history_review.1.desc:',text)
