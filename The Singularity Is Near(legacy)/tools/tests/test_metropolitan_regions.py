import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_metropolitan_regions import build
from gen_dashboard import build as dashboard
class MetropolitanTests(unittest.TestCase):
 def test_province_batch_excludes_foreign_existing_and_unconnected(self):
  s=build()['in_game/common/generic_actions/tsin_metropolitan_regions.txt']
  self.assertIn('looking_for_a = province',s)
  self.assertIn('every_location_in_province',s)
  self.assertIn('NOT = { has_variable = tsin_metro_hub }',s)
  self.assertIn('has_road_to = scope:metro_hub',s)
  self.assertIn('owner ?= scope:actor',s)
  self.assertGreaterEqual(s.count('var:tsin_metro_members < 24'),3)
 def test_no_world_scan_and_no_retain_effect_on_foreign_owner(self):
  b=build();s=b['in_game/common/scripted_effects/tsin_metropolitan_regions.txt']
  self.assertNotIn('every_country',s);self.assertNotIn('every_owned_location',s)
  self.assertIn('every_in_global_list = { variable = tsin_metro_member_sites',s)
  self.assertIn('remove_list_global_variable',s)
  auto=b['in_game/common/auto_modifiers/tsin_metropolitan_regions.txt']
  self.assertIn('owner ?= var:tsin_metro_hub.owner',auto)
  self.assertIn('scales_with = tsin_metro_link_scale',auto)
  self.assertNotIn('add_pop_size',s)
 def test_all_entry_buttons_wired(self):
  d=json.loads(pdx.read_text(pdx.MOD_ROOT/'ui/dashboard_registry.json'));s=dashboard(d)['in_game/gui/tsin_dashboard.gui']
  for suffix in ['create','expand','leave','review']:
   self.assertIn("GetGenericAction('tsin_metro_"+suffix+"')",s)
if __name__=='__main__':unittest.main()
