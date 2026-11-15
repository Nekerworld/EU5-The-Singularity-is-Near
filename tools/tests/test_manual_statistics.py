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
 def test_button_and_metric_wiring(self):
  d=json.loads(pdx.read_text(pdx.MOD_ROOT/'ui/dashboard_registry.json'));b=dashboard(d)
  self.assertIn("GetGenericAction('tsin_survey_world')",b['in_game/gui/tsin_dashboard.gui'])
  self.assertIn('TSIN_UI_MANUAL',b['main_menu/localization/korean/tsin_dashboard_l_korean.yml'])
  self.assertFalse(check_provider_links(d,pdx.MOD_ROOT))
  for m in registry_module()['metrics']:self.assertEqual(m['frequency'],'manual')
if __name__=='__main__':unittest.main()
