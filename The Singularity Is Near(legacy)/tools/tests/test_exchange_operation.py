import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import finance_capabilities as fc
from gen_capital_markets import build as capital_build

class ExchangeOperationTests(unittest.TestCase):
 def test_new_public_offerings_wait_for_capital_markets_tech(self):
  self.assertEqual(fc.GATES['public_equity'],'tsin_can_use_capital_markets')
  # Existing banking-side actions and vanilla-style loans keep their own gates.
  self.assertEqual(fc.GATES['private_equity'],'tsin_can_use_banking')
  self.assertEqual(fc.GATES['lend'],'tsin_can_use_banking')

 def test_exchange_trigger_is_shared_and_defined(self):
  self.assertIn('tsin_exchange_can_open_trigger = { tsin_can_use_capital_markets = yes }',fc.TRIGGERS)
  self.assertIn('has_embraced_institution = institution:tsin_industrial_capitalism',fc.TRIGGERS)
  self.assertIn('has_advance = stock_exchange_advance',fc.TRIGGERS)

 def test_stock_flag_is_only_written_when_exchange_can_open(self):
  z=capital_build()['in_game/common/scripted_effects/zzzz_tsin_capital_effects.txt']
  self.assertNotIn('\nset_variable = tsin_has_stock_market\n',z)
  self.assertIn('if = { limit = { tsin_exchange_can_open_trigger = yes } set_variable = tsin_has_stock_market',z)
  self.assertIn('else = { if = { limit = { is_ai = no } debug_log = tsin_log_hook_listing_exchange_blocked } }',z)
  # Dissolution still clears the flag; listings are not cancelled by a missing technology.
  self.assertIn('remove_variable = tsin_has_stock_market',z)

 def test_national_index_publishes_only_with_exchange(self):
  z=capital_build()['in_game/common/scripted_effects/zzzz_tsin_capital_effects.txt']
  self.assertIn('if = { limit = { tsin_company_count > 0 tsin_exchange_can_open_trigger = yes } set_variable = { name = tsin_stock_index value = tsin_stock_index_value } }',z)
  self.assertIn('else_if = { limit = { has_variable = tsin_stock_index NOT = { tsin_exchange_can_open_trigger = yes } } remove_variable = tsin_stock_index }',z)

if __name__=='__main__':unittest.main()
