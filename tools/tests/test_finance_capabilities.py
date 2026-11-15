import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
import finance_capabilities as caps
from gen_finance_ledger import build
class FinanceCapabilityTests(unittest.TestCase):
 def test_legacy_service_is_not_locked_by_research(self):
  for key in ['repay','release','stop_deposits','liquidity_repay','pension_off','paygo_off','writeoff','bond_writeoff','contract','dividend']:
   self.assertEqual(caps.guard(key,'gold > 0'),'gold > 0')
 def test_new_operations_recheck_permission_on_execution(self):
  b=build();s=b['in_game/common/scripted_guis/tsin_finance_ledger_guis.txt']
  for key,cap in caps.GATES.items():
   part=next(x.text for x in pdx.top_level_blocks(s) if x.key=='tsin_ledger_'+key)
   self.assertGreaterEqual(part.count(cap+' = yes'),2,key)
  self.assertIn('has_advance = central_bank_advance',caps.TRIGGERS)
  self.assertIn('has_advance = stock_exchange_advance',caps.TRIGGERS)
 def test_unknown_maturity_fields_reach_actual_ui(self):
  s=build()['in_game/gui/tsin_finance_ledger.gui']
  self.assertIn('TSIN_LEDGER_UNKNOWN_MATURITY',s)
  self.assertIn('TSIN_LEDGER_UNKNOWN_ID',s)
  self.assertIn('TSIN_LEDGER_TECH_HELP',s)
if __name__=='__main__':unittest.main()
