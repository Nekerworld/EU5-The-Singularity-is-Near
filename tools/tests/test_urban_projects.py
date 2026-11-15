import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_urban_projects import build,STAGES
from gen_dashboard import build as dashboard
class UrbanProjectTests(unittest.TestCase):
 def test_paid_and_ordered_without_slot_requirement(self):
  b=build();s=b['in_game/common/generic_actions/tsin_urban_projects.txt']
  self.assertIn('NOT = { has_variable = tsin_urban_project_stage }',s)
  for n,cost,months,slots,*_ in STAGES:
   self.assertIn(f'tsin_urban_project_{n}_price = {{ gold = {cost} }}',b['in_game/common/prices/tsin_urban_projects.txt'])
   self.assertIn(f'add = {months}',s)
   self.assertIn(f'free_building_levels = {slots}',b['main_menu/common/static_modifiers/tsin_urban_projects.txt'])
  self.assertNotIn('has_building',s)
  self.assertEqual(s.count('NOT = { has_variable = tsin_urban_project_pending }'),6)
 def test_completion_is_once_and_only_pending_list_is_reviewed(self):
  b=build();s=b['in_game/common/scripted_effects/tsin_urban_projects.txt']
  self.assertIn('every_in_global_list = { variable = tsin_urban_project_sites',s)
  self.assertIn('remove_list_global_variable',s)
  self.assertIn('remove_variable = tsin_urban_project_pending',s)
  self.assertEqual(s.count('NOT = { has_location_modifier = tsin_urban_project_'),3)
  self.assertNotIn('every_owned_location',s);self.assertNotIn('every_country',s)
 def test_dashboard_buttons_execute_native_action(self):
  d=json.loads(pdx.read_text(pdx.MOD_ROOT/'ui/dashboard_registry.json'))
  s=dashboard(d)['in_game/gui/tsin_dashboard.gui']
  for n in [1,2,3]:self.assertIn(f"GetGenericAction('tsin_urban_project_{n}')",s)
  self.assertIn('PerformGenericAction(GenericAction.Self)',s)
if __name__=='__main__':unittest.main()
