import sys,unittest
from pathlib import Path
from decimal import Decimal as D
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx,finance_regulation as reg,finance_contracts
from test_finance_contracts import ContractFixture
from gen_finance_ledger import build

class FinanceRegulationTests(unittest.TestCase):
 def test_law_never_gates_existing_servicing(self):
  for name in ('repay','liquidity_repay','release','bond_writeoff','stop_deposits'):
   self.assertEqual(reg.guard(name,'always = yes'),'always = yes')
  s=finance_contracts.build()['in_game/common/scripted_effects/tsin_finance_contract_effects.txt']
  service=next(b.text for b in pdx.top_level_blocks(s) if b.key=='tsin_contract_service_one_effect')
  self.assertNotIn('audit',service);self.assertNotIn('underwriting',service)
 def test_audit_spends_real_cash_once_and_cannot_certify_unfunded(self):
  f=ContractFixture();c=f.country(tsin_bank_cash=D(100),tsin_firm_cash=D(50),tsin_deposits=D(0),tsin_liquidity_debt=D(0))
  f.effect('tsin_paid_bank_audit_effect',c)
  self.assertEqual(c['tsin_bank_cash'],D(99));self.assertIn('tsin_bank_audit_valid',c)
  f.effect('tsin_paid_bank_audit_effect',c);self.assertEqual(c['tsin_bank_cash'],D(99))
  f.effect('tsin_paid_firm_audit_effect',c);self.assertEqual(c['tsin_firm_cash'],D(49))
  c['tsin_firm_cash']=D(0);c.pop('tsin_firm_audit_valid')
  f.effect('tsin_paid_firm_audit_effect',c);self.assertNotIn('tsin_firm_audit_valid',c)
 def test_new_loan_blocked_by_audit_while_old_repayment_is_preserved(self):
  f=ContractFixture();c=f.country(tsin_bank_cash=D(500),tsin_firm_cash=D(500),tsin_deposits=D(0),tsin_liquidity_debt=D(0),policies={'tsin_bank_prudential_policy','tsin_disclosure_audited_policy'})
  f.effect('tsin_contract_lend_facility_effect',c);self.assertEqual(c['tsin_firm_debt'],D(0))
  f.effect('tsin_paid_bank_audit_effect',c);f.effect('tsin_paid_firm_audit_effect',c)
  f.effect('tsin_contract_lend_facility_effect',c);self.assertEqual(c['tsin_firm_debt'],D(100))
  c.pop('tsin_bank_audit_valid');c.pop('tsin_firm_audit_valid')
  f.effect('tsin_contract_repay_facility_effect',c);self.assertEqual(c['tsin_firm_debt'],D(0))
 def test_grant_conserves_gold_and_adds_no_debt_or_equity(self):
  f=ContractFixture();c=f.country(gold=D(300),tsin_bank_cash=D(0),tsin_deposits=D(150),tsin_liquidity_debt=D(0))
  f.effect('tsin_bank_loss_grant_effect',c)
  self.assertEqual(c['gold'],D(50));self.assertEqual(c['tsin_bank_cash'],D(250));self.assertEqual(c['tsin_deposits'],D(150))
  f.effect('tsin_bank_loss_grant_effect',c);self.assertEqual(c['gold'],D(50))
 def test_ratio_and_actual_ui_and_bill_registration(self):
  f=ContractFixture();c=f.country(tsin_deposits=D(1000),tsin_liquidity_debt=D(0))
  for policy,expected in [(None,300),('tsin_bank_free_policy',200),('tsin_bank_prudential_policy',400),('tsin_bank_strict_policy',500)]:
   c['policies']={policy} if policy else set()
   self.assertEqual(f.scope('tsin_bank_lending_cash_required'),D(expected))
  gui=build()['in_game/gui/tsin_finance_ledger.gui']
  for key in ('audit_bank','audit_firm','bank_loss_grant'):self.assertIn("tsin_ledger_"+key,gui)
  self.assertIn("tsin_bank_audit_status",gui)
  bills=pdx.read_text(pdx.MOD_ROOT/'in_game/events/tsin_legislation_bills.txt')
  self.assertIn('tsin_bank_strict_policy',bills);self.assertIn('tsin_disclosure_audited_policy',bills)
if __name__=='__main__':unittest.main()
