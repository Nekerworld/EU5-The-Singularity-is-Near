from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_stock_market_ui import build,patch_economy,patch_tabs,compat_files,ECONOMY,GLORP_TABS,STOCK
from gen_company_decisions import COMPANIES,HISTORY


class StockMarketUITests(unittest.TestCase):
    def test_economy_body_preserved_and_balance_returns(self):
        source=pdx.read_text(pdx.game_root()/ECONOMY)
        patched=patch_economy(source)
        inserted=f'\n\t\ttsin_stock_panel = {{ visible = "[{STOCK}]" }}\n'
        restored=patched.replace(inserted,'').replace(f'\t\t\tvisible = "[Not({STOCK})]"\n','')
        self.assertEqual(restored,source)
        tabs=patch_tabs(source)
        self.assertIn("subtab = balance",tabs)
        self.assertIn("subtab = tsin_stocks",tabs)
        self.assertIn("GetScriptedGui('tsin_stock_ui_seed').Execute",tabs)
        self.assertIn(f"[And(IsLateralViewOpened('economy'), Not({STOCK}))]",tabs)
        for action in ["OpenLateralView('credit')","OpenLateralView('trade_policies')","subtab = markets","subtab = trades"]:
            self.assertIn(action,tabs)

    def test_guards_reject_changed_layout_and_duplicate_patch(self):
        source=pdx.read_text(pdx.game_root()/ECONOMY)
        with self.assertRaises(ValueError):patch_tabs('template renamed {}')
        with self.assertRaises(ValueError):patch_economy(source.replace('using = economy_main_tabs','using = changed'))
        with self.assertRaises(ValueError):patch_tabs(patch_tabs(source))

    def test_data_is_existing_history_and_bounded_company_cache(self):
        files=build()
        ui=files['in_game/gui/tsin_stock_market.gui']
        for i in range(HISTORY):self.assertIn(f"GetVariable('tsin_index_h{i}')",ui)
        guis=files['in_game/common/scripted_guis/tsin_stock_market_guis.txt']
        cache=pdx.read_text(pdx.MOD_ROOT/'in_game/common/scripted_effects/tsin_dashboard_age7_effects.txt')
        for c,*_ in COMPANIES:
            self.assertIn(f'has_country_modifier = tsin_company_{c}',guis)
            self.assertIn(f'tsin_stock_ui_levels_{c} value = tsin_company_levels_{c}',cache)
            self.assertIn(f"GetVariable('tsin_hq_{c}').GetLocation",ui)
        self.assertIn('tsin_dashboard_age7_migrate_effect = yes',guis)
        self.assertIn('tsin_industrialization_statistics_version < 2',cache)
        self.assertIn('ShowLocation(Location.Self)',ui)
        self.assertIn('Location.IsValid',ui)
        self.assertNotIn('every_owned_location',ui)
        self.assertNotIn('total_effective_building_levels',ui)
        self.assertNotIn('trigger_event',guis)

    def test_glorp_connects_both_separate_files(self):
        source=pdx.workshop_root()/'3812518640'
        if not (source/GLORP_TABS).exists():self.skipTest('Glorp not installed')
        files=compat_files(source)
        self.assertEqual(set(files),{ECONOMY,GLORP_TABS})
        self.assertIn('tsin_stock_panel = {',files[ECONOMY])
        self.assertIn('using = economy_main_tabs',files[ECONOMY])
        self.assertIn("subtab = tsin_stocks",files[GLORP_TABS])
        self.assertIn("subtab = balance",files[GLORP_TABS])


if __name__=='__main__':unittest.main()
