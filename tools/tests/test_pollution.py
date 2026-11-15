import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_pollution import build,HEAVY,CHEMICAL,LIGHT
from gen_dashboard import build as dashboard
class PollutionTests(unittest.TestCase):
 def test_only_open_employed_sources_no_double_count(self):
  s=build()['in_game/common/scripted_effects/tsin_pollution.txt']
  self.assertIn('limit = { is_opened = yes building_employed_amount > 0 }',s)
  self.assertEqual(len(HEAVY+CHEMICAL+LIGHT),len(set(HEAVY+CHEMICAL+LIGHT)))
  self.assertNotIn('tsin_power_station',s)
  self.assertNotIn('every_owned_location',s)
  self.assertNotIn('add_pop_size',s)
 def test_single_existing_pass_and_separate_water_abatement(self):
  s=pdx.read_text(pdx.MOD_ROOT/'in_game/common/scripted_effects/tsin_aggregate_effects.txt')
  self.assertEqual(s.count('tsin_pollution_location_tick_effect = yes'),1)
  self.assertEqual(s.count('tsin_pollution_finish_country_effect = yes'),1)
  v=build()['in_game/common/script_values/tsin_pollution.txt']
  water=next(b.text for b in pdx.top_level_blocks(v) if b.key=='tsin_pollution_water_target')
  self.assertNotIn('filters',water)
  self.assertIn('max = 100',water)
 def test_entry_map_labels_and_cached_display(self):
  d=json.loads(pdx.read_text(pdx.MOD_ROOT/'ui/dashboard_registry.json'))
  s=dashboard(d)['in_game/gui/tsin_dashboard.gui']
  self.assertIn("GetGenericAction('tsin_pollution_filter')",s)
  for lang in ['english','korean']:
   loc=build()[f'main_menu/localization/{lang}/tsin_pollution_l_{lang}.yml']
   self.assertIn('mapmode_tsin_pollution_name:',loc)
   self.assertIn('MAPMODE_TSIN_POLLUTION:',loc)
  maps=pdx.read_text(pdx.MOD_ROOT/'in_game/gfx/map/map_modes/tsin_map_modes.txt')
  b=next(b.text for b in pdx.top_level_blocks(maps) if b.key=='tsin_pollution')
  self.assertIn('category = economy',b)
  self.assertIn('index = 3',b)
  self.assertNotIn('every_buildings',b)
if __name__=='__main__':unittest.main()
