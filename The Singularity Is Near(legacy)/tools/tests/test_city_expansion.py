import sys,unittest,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_rgo_rank_balance import build
from gen_city_expansion import rewrite_rank_checks

class CityExpansionTests(unittest.TestCase):
 def test_order_and_legacy_identity(self):
  s=build()['in_game/common/location_ranks/00_default.txt']
  b=pdx.top_level_blocks(s)
  self.assertEqual([x.key for x in b],['tsin_megalopolis','megalopolis','tsin_large_city','city','town','rural_settlement'])
  ranks={x.key:x.text for x in b}
  for k in ['megalopolis','tsin_megalopolis']:
   self.assertNotIn('is_capital = yes',ranks[k]);self.assertNotIn('is_market_center = yes',ranks[k]);self.assertNotIn('is_subject = no',ranks[k])
  self.assertIn('population >= 400.000',ranks['megalopolis'])
  for x in ['population >= 1000','development >= 50','location_potential_tax_base >= 50','max_rank = yes']:
   self.assertIn(x,ranks['tsin_megalopolis'])
  self.assertNotIn('max_rank = yes',ranks['megalopolis'])
  self.assertIn('population >= 100',ranks['tsin_large_city'])
 def test_rank_expansion_is_idempotent_and_not_recursive(self):
  s='location_rank = location_rank:city location_rank ?= location_rank:megalopolis'
  t=rewrite_rank_checks(s)
  self.assertEqual(rewrite_rank_checks(t),t)
  self.assertIn('tsin_is_city_or_large_city = yes',t)
  self.assertIn('tsin_is_metropolis_or_megalopolis = yes',t)
  self.assertEqual(rewrite_rank_checks('scope:other.location_rank = location_rank:city'),'scope:other.location_rank = location_rank:city')
 def test_current_storage_buildings_have_expanded_permissions(self):
  s=pdx.read_text(pdx.MOD_ROOT/'in_game/common/building_types/zzzzzz_tsin_city_building_ranks.txt')
  for k in ['tsin_cold_storage','tsin_electric_cold_storage','tsin_public_school','tsin_railway_station']:
   b=next(x.text for x in pdx.top_level_blocks(s) if x.key=='TRY_INJECT:'+k)
   self.assertIn('tsin_large_city = yes',b);self.assertIn('tsin_megalopolis = yes',b)
if __name__=='__main__':unittest.main()
