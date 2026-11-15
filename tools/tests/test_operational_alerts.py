from pathlib import Path
import copy,json,re,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_operational_alerts import build,validate
from gen_dashboard import build as dashboard


class OperationalTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(pdx.read_text(pdx.MOD_ROOT/'ui/operational_alerts.json'))

    def test_only_operational_warning_types(self):
        rules=validate(self.data)
        self.assertEqual(len(rules),22)
        self.assertFalse(any(re.search(r'has_active_disaster|is_situation_active',r['condition']) for r in rules))
        bad=copy.deepcopy(self.data)
        bad['rules'][0]['condition']='has_active_disaster = disaster_type:tsin_cholera'
        with self.assertRaises(ValueError):validate(bad)

    def test_player_scans_are_bounded_and_not_client_alert_driven(self):
        generated=build(self.data)
        hook=generated['in_game/common/on_action/tsin_operational_on_actions.txt']
        self.assertIn('is_ai = no',hook)
        self.assertIn('NOT = { has_variable = tsin_ops_scan_timer }',hook)
        effects=generated['in_game/common/scripted_effects/tsin_operational_effects.txt']
        self.assertEqual(effects.count('every_owned_location ='),1)
        self.assertEqual(effects.count('every_buildings_in_location ='),1)
        self.assertIn('is_in_list = tsin_ops_seen_markets',effects)
        self.assertEqual(effects.count('clear_list = tsin_ops_seen_markets'),2)
        self.assertNotIn('every_country',effects)
        self.assertNotIn('is_alert_triggered',effects)
        self.assertIn('has_variable = tsin_ops_persistence_timer',effects)
        self.assertIn('name = tsin_ops_persistence_timer months = 3',effects)

        self.assertNotIn('every_owned_location',generated['in_game/gui/tsin_operational.gui'])

    def test_badge_and_rows_share_hidden_rule_conditions(self):
        ui=build(self.data)['in_game/gui/tsin_operational.gui']
        for rule in self.data['rules']:
            self.assertIn("tsin_ops_hide_"+rule['id'],ui)
            self.assertIn("GetScriptedGui('tsin_ops_check_"+rule['id']+"')",ui)
        self.assertIn('TSIN_OPS_EMPTY',ui)
        self.assertIn('TSIN_OPS_RESTORE',ui)
        self.assertIn('ShowMarket(Market.Self)',ui)
        self.assertIn('Market.IsValid',ui)
        self.assertNotIn('AlertEntry.SetMuted',ui)


    def test_existing_tsin_button_is_kept(self):
        data=json.loads(pdx.read_text(pdx.MOD_ROOT/'ui/dashboard_registry.json'))
        ui=dashboard(data)['in_game/gui/tsin_dashboard_dock.gui']
        self.assertEqual(ui.count('tsin_ops_button = {}'),1)
        self.assertIn("GetVariableSystem.Toggle('tsin_ui_dashboard_open')",ui)
        self.assertIn("GetVariableSystem.Toggle('tsin_ui_dock_expanded')",ui)

    def test_unknown_native_alert_is_detectable(self):
        defs={b.key for p in (pdx.game_root()/'in_game/common/alert_descriptions').glob('*.txt') for b in pdx.top_level_blocks(pdx.read_text(p))}
        for rule in self.data['rules']:
            for id in re.findall(r'is_alert_triggered\s*=\s*(\w+)',rule['condition']):self.assertIn(id,defs)

    def test_scan_ready_after_all_counters_and_reference_thresholds(self):
        fx=build(self.data)['in_game/common/scripted_effects/tsin_operational_effects.txt']
        main=next(b for b in pdx.top_level_blocks(fx) if b.key=='tsin_ops_scan_effect')
        self.assertLess(main.text.index('every_owned_location'),main.text.index('name = tsin_ops_ready'))
        market=next(b for b in pdx.top_level_blocks(fx) if b.key=='tsin_ops_scan_market_effect')
        for good in self.data['goods']:
            threshold=good['base_price']*self.data['high_price_ratio']
            self.assertIn(f'"market_price(goods:{good["id"]})" >= {threshold:g}',market.text)

if __name__=='__main__':unittest.main()
