import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_urban_transit import build
class UrbanTransitTests(unittest.TestCase):
 def test_pilot_cannot_stack_and_electric_replaces_it(self):
  s=build()['in_game/common/building_types/tsin_urban_transit.txt']
  b={b.key:b.text for b in pdx.top_level_blocks(s)}
  self.assertIn('max_levels = 1',b['tsin_steam_metro'])
  self.assertIn('obsolete = tsin_steam_metro',b['tsin_electric_metro'])
  self.assertIn('local_population_capacity_modifier = 0.01',b['tsin_steam_metro'])
  self.assertIn('local_population_capacity_modifier = 0.05',b['tsin_electric_metro'])
  self.assertNotIn('add_road',s)
 def test_station_disconnection_retains_assets_without_unconditional_bonus(self):
  s=pdx.read_text(pdx.MOD_ROOT/'in_game/common/building_types/tsin_railway_buildings.txt')
  b=next(b for b in pdx.top_level_blocks(s) if b.key=='tsin_railway_station')
  nested={x.key for x in pdx.top_level_blocks(b.text[b.text.index('{')+1:-1])}
  self.assertNotIn('remove_if',nested);self.assertNotIn('modifier',nested)
  a=pdx.read_text(pdx.MOD_ROOT/'in_game/common/auto_modifiers/tsin_railway_connection.txt')
  self.assertIn('controller ?= owner',a)
  self.assertIn('type = road_type:railroad',a)
 def test_research_and_assets_connected(self):
  for key,rel in [('tsin_steam_metro','tsin_03_industrial_capitalism.txt'),('tsin_electric_metro','tsin_06_electrification.txt')]:
   self.assertIn('unlock_building = '+key,pdx.read_text(pdx.MOD_ROOT/'in_game/common/advances'/rel))
   self.assertTrue(pdx.content_path(pdx.MOD_ROOT/f'main_menu/gfx/interface/icons/buildings/{key}.dds').exists())
if __name__=='__main__':unittest.main()
