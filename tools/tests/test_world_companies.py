import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_world_companies import build
from gen_dashboard import build as dashboard
class WorldCompanyTests(unittest.TestCase):
 def test_world_is_read_only_by_explicit_survey(self):
  b=build();s=b['in_game/common/scripted_effects/tsin_world_companies.txt'];blocks={x.key:x.text for x in pdx.top_level_blocks(s)}
  self.assertEqual(blocks['tsin_world_company_survey_effect'].count('every_country ='),1)
  self.assertNotIn('every_country',blocks['tsin_world_company_project_page_effect'])
  self.assertNotIn('every_owned_location',s)
  self.assertFalse(any('/on_action/' in p for p in b))
  self.assertIn('ai_tick = never',b['in_game/common/generic_actions/tsin_world_companies.txt'])
 def test_snapshots_are_owned_and_missing_values_remain_marked(self):
  s=build()['in_game/common/scripted_effects/tsin_world_companies.txt']
  self.assertIn('every_in_list = { variable = tsin_wcs_rows',s)
  self.assertIn('clear_variable_list = tsin_wcs_rows',s)
  self.assertIn('global_var:tsin_wcs_next_id add = 1',s)
  self.assertNotIn('clear_global_variable_map',s)
  self.assertIn('name = tsin_wcs_cash_known',s)
  self.assertIn('has_variable = tsin_firm_cash',s)
  self.assertIn('has_variable = tsin_stock_ui_stats_year',s)
 def test_both_ui_entries_and_window_are_registered(self):
  b=build();registration=b['in_game/gui/scripted_widgets/tsin_world_companies.txt']
  self.assertIn('gui/tsin_world_companies.gui = tsin_world_company_window',registration)
  d=json.loads(pdx.read_text(pdx.MOD_ROOT/'ui/dashboard_registry.json'))
  s=dashboard(d)['in_game/gui/tsin_dashboard.gui']
  self.assertIn("GetVariableSystem.Set('tsin_ui_world_companies_open', 'yes')",s)
  stock=pdx.read_text(pdx.MOD_ROOT/'in_game/gui/tsin_stock_market.gui')
  self.assertIn('TSIN_CAP_WORLD_COMPANIES',stock)
  self.assertLess(stock.index('TSIN_CAP_WORLD_COMPANIES'),stock.index('TSIN_CAP_GENERIC'))
  ui=b['in_game/gui/tsin_world_companies.gui']
  self.assertIn('scrollwidget',ui)
  self.assertNotIn('every_country',ui)
class WorldCompanyCooldownTests(unittest.TestCase):
 def test_cooldown_guard_is_in_generic_action_and_row_reset_stays_in_effect(self):
  import gen_world_companies as g
  a=g.build()['in_game/common/generic_actions/tsin_world_companies.txt']
  self.assertIn('allow = { NOT = { has_variable = tsin_wcs_survey_cooldown } }',a)
  self.assertIn('days = 1',a)
  s=g.build()['in_game/common/scripted_effects/tsin_world_companies.txt']
  self.assertLess(s.index('tsin_world_company_survey_effect = {'), s.index('remove_from_global_variable_map'))
if __name__=='__main__':unittest.main()
