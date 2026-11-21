import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_distribution_grid import build
class DistributionGridTests(unittest.TestCase):
 def test_equipment_is_separate_from_market_supply(self):
  b=build();v=b['in_game/common/script_values/tsin_distribution_grid.txt']
  access=next(x.text for x in pdx.top_level_blocks(v) if x.key=='tsin_power_access_index')
  self.assertNotIn('goods_supply',access)
  self.assertNotIn('power_ratio',access)
  self.assertIn('max = 1',access)
  self.assertNotIn('produced =',b['in_game/common/building_types/tsin_distribution_grid.txt'])
 def test_refrigeration_bonus_requires_both_operating_facilities(self):
  b=build();v=b['in_game/common/script_values/tsin_distribution_grid.txt']
  scale=next(x.text for x in pdx.top_level_blocks(v) if x.key=='tsin_grid_refrigeration_scale')
  self.assertEqual(scale.count('building_employed_amount > 0'),2)
  self.assertIn('multiply = tsin_location_power_ratio',scale)
  auto=b['in_game/common/auto_modifiers/tsin_distribution_grid.txt']
  self.assertIn('tsin_electric_cold_storage',auto)
  self.assertNotIn('raw_material',auto);self.assertNotIn('output_modifier',auto)
 def test_map_and_research_remain_connected(self):
  s=pdx.read_text(pdx.MOD_ROOT/'in_game/gfx/map/map_modes/tsin_map_modes.txt')
  modes={b.key for b in pdx.top_level_blocks(s)}
  self.assertIn('tsin_electrification',modes);self.assertIn('tsin_power_access',modes)
  advances=pdx.read_text(pdx.MOD_ROOT/'in_game/common/advances/tsin_06_electrification.txt')
  self.assertIn('unlock_building = tsin_distribution_substation',advances)
if __name__=='__main__':unittest.main()
