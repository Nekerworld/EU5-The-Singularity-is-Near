import json, unittest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdx
from gen_treaties import build, load, registry_module


class TreatyRegistryTests(unittest.TestCase):
    def test_articles_and_presets_cover_plan(self):
        data = load()
        ids = {a['id'] for a in data['articles']}
        for need in (
            'alliance', 'defensive_pact', 'mutual_tariff_exempt', 'investment_rights',
            'tsin_fx_peg', 'tsin_unequal_open', 'tsin_harmonize_standards',
            'tsin_lend_lease_eq', 'tsin_pollution_compact', 'tsin_colonial_sphere',
        ):
            self.assertIn(need, ids)
        presets = {p['id']: p['articles'] for p in data['presets']}
        self.assertIn('knowledge_share', presets['modernize'])
        self.assertIn('tsin_fx_peg', presets['finance'])
        self.assertIn('tsin_lend_lease_fuel', presets['lend_lease'])
        self.assertEqual(presets['revise'], ['tsin_revise_unequal'])

    def test_generated_wiring(self):
        out = build()
        effects = out['in_game/common/scripted_effects/tsin_treaties.txt']
        self.assertIn('tsin_tr_month_effect', effects)
        self.assertIn('tsin_tr_break_selected_effect', effects)
        self.assertIn('tsin_tr_renegotiate_selected_effect', effects)
        self.assertIn('tsin_tr_succession_effect', effects)
        self.assertNotIn('tsin_tr_withdraw_selected_effect', effects)
        self.assertIn('create_relation', effects)
        self.assertIn('tsin_add_opening_pressure_effect', effects)
        on_action = out['in_game/common/on_action/tsin_treaties_on_actions.txt']
        self.assertIn('tsin_tr_global_monthly', on_action)
        self.assertIn('tsin_contract_calendar_month', on_action)
        rels = out['in_game/common/scripted_relations/tsin_treaty_relations.txt']
        self.assertIn('visible = { always = no }', rels)
        gui = out['in_game/gui/tsin_treaties.gui']
        self.assertIn('tsin_treaties_window', gui)
        self.assertIn('scrollbar_vertical = { using = Scrollbar_Vertical }', gui)
        self.assertIn('tsin_tr_renegotiate', gui)
        self.assertEqual(
            out['in_game/gui/scripted_widgets/tsin_treaties.txt'].strip(),
            'gui/tsin_treaties.gui = tsin_treaties_window',
        )
        interaction = out['in_game/common/country_interactions/tsin_negotiate_treaty.txt']
        self.assertIn('tsin_negotiate_treaty', interaction)
        self.assertIn('ai_tick = never', interaction)

    def test_dashboard_shortcut_and_check(self):
        mod = registry_module()
        self.assertEqual(mod['shortcuts'][0]['open_variable'], 'tsin_ui_treaties_open')
        dash = json.loads(pdx.read_text(pdx.MOD_ROOT / 'ui/dashboard_registry.json'))
        shortcuts = []
        for m in dash['modules']:
            shortcuts.extend(s['id'] for s in m.get('shortcuts', []))
        self.assertIn('treaties', shortcuts)
        from gen_dashboard import build as build_dash
        gui = build_dash(dash)['in_game/gui/tsin_dashboard.gui']
        self.assertIn("GetVariableSystem.Set('tsin_ui_treaties_open', 'yes')", gui)

    def test_succession_hook(self):
        from finance_succession import build as build_succ
        text = build_succ()['in_game/common/scripted_effects/tsin_finance_succession_effects.txt']
        self.assertIn('tsin_tr_succession_effect = yes', text)


if __name__ == '__main__':
    unittest.main()
