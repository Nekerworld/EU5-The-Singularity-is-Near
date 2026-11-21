import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_manual_statistics import build,registry_module
from gen_dashboard import build as dashboard,check_provider_links
class ManualStatisticsTests(unittest.TestCase):
 def test_reports_have_no_background_schedule(self):
  b=build();self.assertFalse(any('/on_action/' in p for p in b))
  actions=b['in_game/common/generic_actions/tsin_manual_surveys.txt']
  self.assertEqual(actions.count('ai_tick = never'),2)
  self.assertEqual(actions.count('automation_tick = never'),2)
  for p in (pdx.MOD_ROOT/'in_game/common/on_action').glob('*.txt'):
   self.assertNotIn('tsin_survey_',pdx.read_text(p))
 def test_world_coverage_is_explicit_and_snapshots_reset(self):
  s=build()['in_game/common/scripted_effects/tsin_manual_surveys.txt']
  self.assertIn('has_variable = tsin_gdp',s)
  self.assertIn('tsin_report_world_known_gdp',s)
  self.assertIn('remove_variable = tsin_report_gdp',s)
  self.assertEqual(s.count('every_country ='),1)
  self.assertEqual(s.count('every_owned_location ='),1)
  self.assertIn('name = tsin_report_world_gdp value = 0',s)
 def test_one_survey_per_kind_per_day_checked_before_effect(self):
  a=build()['in_game/common/generic_actions/tsin_manual_surveys.txt']
  for kind in ('domestic','world'):
   self.assertIn('allow = { NOT = { has_variable = tsin_survey_'+kind+'_cooldown } }',a)
   self.assertIn('set_variable = { name = tsin_survey_'+kind+'_cooldown value = yes days = 1 }',a)
 def test_button_and_metric_wiring(self):
  d=json.loads(pdx.read_text(pdx.MOD_ROOT/'ui/dashboard_registry.json'));b=dashboard(d)
  self.assertIn("GetGenericAction('tsin_survey_world')",b['in_game/gui/tsin_dashboard.gui'])
  self.assertIn('TSIN_UI_MANUAL',b['main_menu/localization/korean/tsin_dashboard_l_korean.yml'])
  self.assertFalse(check_provider_links(d,pdx.MOD_ROOT))
  for m in registry_module()['metrics']:self.assertEqual(m['frequency'],'manual')
class CountryCompareTests(unittest.TestCase):
 def test_viewing_never_starts_a_survey(self):
  b=build();proj=b['in_game/common/scripted_effects/tsin_country_compare.txt']
  self.assertNotIn('every_country',proj)
  self.assertNotIn('every_owned_location',proj)
  self.assertNotIn('tsin_survey_domestic_effect',proj)
  self.assertNotIn('tsin_survey_world_effect',proj)
  self.assertNotIn('tsin_cmp_record_',proj)
  gui=b['in_game/gui/tsin_country_compare.gui']
  self.assertNotIn('tsin_survey_',gui)
  self.assertNotIn('GetGenericAction',gui)
 def test_history_keeps_latest_twelve_per_country_and_world(self):
  s=build()['in_game/common/scripted_effects/tsin_manual_surveys.txt']
  self.assertIn('var:tsin_cmp_count > 12',s)
  self.assertIn('subtract = 12',s)
  self.assertIn('multiply = 100000',s)
  self.assertIn('global_var:tsin_cmpw_serial > 12',s)
  self.assertIn('tsin_cmp_record_domestic_effect = yes',s)
  self.assertIn('tsin_cmpw_record_effect = yes',s)
  self.assertEqual(s.count('every_country ='),1)
 def test_paging_uses_dense_ids_without_scanning(self):
  proj=build()['in_game/common/scripted_effects/tsin_country_compare.txt']
  self.assertIn('var:tsin_cmp_page multiply = 10',proj)
  self.assertIn('var:tsin_cmp_r1_id > global_var:tsin_cmp_next_id',proj)
  self.assertNotIn('every_in_global_list',proj)
 def test_empty_rows_skip_map_lookup(self):
  proj=build()['in_game/common/scripted_effects/tsin_country_compare.txt']
  self.assertIn('if = { limit = { var:tsin_cmp_r2_id > 0 }',proj)
  self.assertIn('if = { limit = { has_global_variable = tsin_cmpw_serial global_var:tsin_cmpw_serial > 0 }',proj)
  # Empty slots zero fields instead of reading none/any map values.
  self.assertIn('else = {\n  set_variable = { name = tsin_cmp_r2_serial value = 0 }',proj)
 def test_window_and_buttons_are_registered(self):
  b=build();gui=b['in_game/gui/tsin_country_compare.gui'];sg=b['in_game/common/scripted_guis/tsin_country_compare.txt']
  self.assertIn('tsin_country_compare_window',gui)
  self.assertIn('scrollbar_vertical = { using = Scrollbar_Vertical }',gui)
  self.assertNotIn('scrollbarpolicy_vertical',gui)
  for key in ('tsin_cmp_prev','tsin_cmp_next','tsin_cmp_clear','tsin_cmp_add_10','tsin_cmp_detail_10'):
   self.assertIn(key+' = {',sg)
  d=registry_module();self.assertIn('country_compare',[s['id'] for s in d['shortcuts']])
  self.assertEqual(d['shortcuts'][-1]['open_variable'],'tsin_ui_country_compare_open')
if __name__=='__main__':unittest.main()
