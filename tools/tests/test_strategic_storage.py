import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_strategic_storage import build
from gen_dashboard import build as dashboard
class StrategicStorageTests(unittest.TestCase):
 def test_zero_jobs_and_no_fictitious_output(self):
  s=build()['in_game/common/building_types/tsin_strategic_storage.txt']
  self.assertEqual(s.count('employment_size = 0 '),2)
  self.assertNotIn('produced =',s)
  self.assertNotIn('output =',s)
  self.assertIn('always_add_demands = yes',s)
 def test_quantity_bounds_and_native_cash_only(self):
  s=build()['in_game/common/scripted_effects/tsin_strategic_storage.txt']
  for good in ['tsin_oil','coal','steel']:
   self.assertIn(f'max = "market.stockpile_in_market(goods:{good})"',s)
   self.assertNotIn(f'min = "market.stockpile_in_market(goods:{good})"',s)
  self.assertEqual(s.count('buy_goods_from_market ='),3)
  self.assertEqual(s.count('sell_goods_to_market ='),3)
  self.assertNotIn('add_gold',s)
  self.assertNotIn('every_owned_location',s)
  self.assertIn('subtract = local_var:tsin_storage_quantity',s)
  self.assertIn('remove_variable = tsin_storage_active',s)
  self.assertIn('tsin_storage_error_observed',s)
 def test_occupied_no_capital_and_legacy_stock_are_protected(self):
  b=build();s=b['in_game/common/scripted_effects/tsin_strategic_storage.txt']
  self.assertIn('controller ?= owner',s)
  self.assertIn('owner = { exists = capital }',s)
  a=b['in_game/common/generic_actions/tsin_strategic_storage.txt']
  self.assertGreaterEqual(a.count('var:tsin_storage_amount = 0'),3)
  self.assertIn('NOT = { has_variable = tsin_storage_error }',a)
  d=json.loads(pdx.read_text(pdx.MOD_ROOT/'ui/dashboard_registry.json'))
  gui=dashboard(d)['in_game/gui/tsin_dashboard.gui']
  for key in ['oil','coal','steel','pause','resume','release','inspect']:
   self.assertIn("GetGenericAction('tsin_storage_"+key+"')",gui)
if __name__=='__main__':unittest.main()
