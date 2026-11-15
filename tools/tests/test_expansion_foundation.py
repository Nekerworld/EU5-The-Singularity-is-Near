import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx

class ExpansionFoundationTests(unittest.TestCase):
 def test_exchange_reuses_education_without_parallel_progress(self):
  s=pdx.read_text(pdx.MOD_ROOT/'in_game/common/script_values/tsin_knowledge_exchange.txt')
  self.assertIn('tsin_country_higher_education >= 30',s)
  self.assertIn('tsin_country_secondary_education >= 70',s)
  self.assertIn('has_policy = policy:state_press_only',s)
  self.assertNotIn('every_country',s)
  a=pdx.read_text(pdx.MOD_ROOT/'in_game/common/auto_modifiers/tsin_knowledge_exchange.txt')
  self.assertIn('scales_with = tsin_knowledge_exchange_bonus',a)
  self.assertIn('research_speed_modifier = 1',a)
  self.assertNotIn('research_advance',a)
 def test_cold_storage_upgrades_share_storage_not_new_food_output(self):
  for name in ['tsin_cold_storage','tsin_electric_cold_storage']:
   s=pdx.read_text(pdx.MOD_ROOT/('in_game/common/building_types/'+name+'.txt'))
   self.assertIn('is_market_center = yes',s)
   self.assertIn('local_food_preservation_efficiency_modifier',s)
   self.assertNotIn('produced =',s)
   self.assertNotIn('global_food_decay',s)
   self.assertIn('max_levels = 2',s)
  s=pdx.read_text(pdx.MOD_ROOT/'in_game/common/building_types/tsin_electric_cold_storage.txt')
  self.assertIn('obsolete = tsin_cold_storage',s)
  self.assertIn('tsin_electricity = 0.15',s)
 def test_both_cold_facilities_have_research_unlocks_and_localization(self):
  for building,advance in [('tsin_cold_storage','tsin_08_agricultural_revolution.txt'),('tsin_electric_cold_storage','tsin_06_electrification.txt')]:
   self.assertIn('unlock_building = '+building,pdx.read_text(pdx.MOD_ROOT/('in_game/common/advances/'+advance)))
   for lang in ['english','korean']:
    loc=pdx.read_text(pdx.MOD_ROOT/f'main_menu/localization/{lang}/tsin_expansion_cold_l_{lang}.yml')
    self.assertIn(building+':',loc)
if __name__=='__main__':unittest.main()
