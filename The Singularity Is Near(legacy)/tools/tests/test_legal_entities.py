import sys,unittest
from pathlib import Path
from decimal import Decimal as D
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx,legal_entities as le
from gen_finance_ledger import build as ledger
from test_finance_contracts import ContractFixture
from test_capital_markets import parse,get
class LegalEntityFixture(ContractFixture):
 def __init__(self):
  super().__init__()
  for rel,text in le.build().items():
   if '/scripted_effects/' not in rel and '/scripted_triggers/' not in rel:continue
   blocks={b.key:parse(b.text[b.text.index('{')+1:-1]) for b in pdx.top_level_blocks(text)}
   if '/scripted_effects/' in rel:self.effects.update(blocks)
   if '/scripted_triggers/' in rel:self.triggers.update(blocks)
  self.actions={b.key:parse(b.text[b.text.index('{')+1:-1]) for b in pdx.top_level_blocks(ledger()['in_game/common/scripted_guis/tsin_finance_ledger_guis.txt'])}
 def action(self,name,c):
  self.state=self.root=c;self.saved={};self.temp_lists={}
  body=self.actions['tsin_ledger_entity_'+name]
  if not self.valid(get(body,'is_valid')):return False
  self.run(get(body,'effect'));return True
 def valid(self,rows):
  base=super().valid
  def term(row):
   k,op,v=row
   if isinstance(v,list) and op in ('>','<','>=','<='):
    a,b=self.scope(k),self.num(v)
    return {'>':lambda:a>b,'<':lambda:a<b,'>=':lambda:a>=b,'<=':lambda:a<=b}[op]()
   return base([row])
  return all(term(row) for row in rows)
 def cash(self):return sum(self.maps.get('tsin_le_cash',{}).values(),D(0))+sum(c['gold']+c['estate']+c['tsin_bank_cash']+c['tsin_firm_cash'] for c in self.countries)
class LegalEntityTests(unittest.TestCase):
 def seed(self):
  f=LegalEntityFixture();c=f.country(gold=D(1000),estate=D(1000))
  self.assertTrue(f.action('create_bank_private',c));self.assertTrue(f.action('create_company_private',c))
  return f,c,c['tsin_le_primary_bank'],c['tsin_le_primary_company']
 def test_new_cash_only_and_duplicate_charter_rejected(self):
  f,c,bank,firm=self.seed()
  self.assertEqual(c['estate'],D(800));self.assertEqual(f.cash(),D(2000))
  self.assertEqual(f.maps['tsin_le_cash'][bank],D(100));self.assertEqual(f.maps['tsin_le_cash'][firm],D(100))
  self.assertEqual(c['tsin_bank_cash'],D(0));self.assertEqual(c['tsin_firm_cash'],D(0))
  self.assertFalse(f.action('create_bank_private',c));self.assertEqual(f.cash(),D(2000))
 def test_fixed_contract_terms_pay_once_and_repayment_survives_audit_lock(self):
  f,c,bank,firm=self.seed();wealth=f.cash()
  self.assertTrue(f.action('lend',c));self.assertEqual(f.maps['tsin_le_debt'][firm],D(100))
  loan=next(iter(f.maps['tsin_le_loan_principal']));self.assertEqual(f.maps['tsin_le_loan_rate'][loan],D(4))
  c['tsin_rate']=D(18);f.month=D(2);f.effect('tsin_le_month_effect',c)
  paid=f.maps['tsin_le_cash'][bank];self.assertEqual(paid,D(100)/D(300))
  f.effect('tsin_le_month_effect',c);self.assertEqual(f.maps['tsin_le_cash'][bank],paid)
  c['policies']={'tsin_bank_prudential_policy','tsin_disclosure_audited_policy'}
  self.assertFalse(f.action('lend',c));self.assertTrue(f.action('repay',c))
  self.assertEqual(f.maps['tsin_le_debt'][firm],D(0));self.assertEqual(f.cash(),wealth)
 def test_public_equity_dilutes_private_owners_but_contract_revenue_does_not(self):
  f,c,bank,firm=self.seed();wealth=f.cash()
  self.assertTrue(f.action('public_equity',c))
  self.assertEqual(f.maps['tsin_le_units'][firm],D(200));self.assertEqual(f.maps['tsin_le_public_units'][firm],D(100))
  self.assertTrue(f.action('contract',c));self.assertEqual(f.maps['tsin_le_cash'][firm],D(300))
  self.assertEqual(f.maps['tsin_le_units'][firm],D(200));self.assertEqual(f.cash(),wealth)
 def test_zero_rate_overdue_principal_accumulates_and_liquidation_is_once(self):
  f,c,bank,firm=self.seed();c['tsin_rate']=D(0)
  self.assertTrue(f.action('lend',c));loan=next(iter(f.maps['tsin_le_loan_principal']))
  # A distressed fixture after a documented operating loss; liquidation must not invent money.
  f.maps['tsin_le_cash'][firm]=D(25)
  f.year=D(1853)
  for m in range(1,13):f.month=D(m);f.effect('tsin_le_month_effect',c)
  self.assertEqual(f.maps['tsin_le_loan_missed'][loan],D(12))
  wealth=f.cash();self.assertTrue(f.action('liquidate',c))
  self.assertEqual(f.maps['tsin_le_cash'][bank],D(25));self.assertEqual(f.maps['tsin_le_losses'][bank],D(75))
  self.assertEqual(f.maps['tsin_le_debt'][firm],D(0));self.assertEqual(f.maps['tsin_le_status'][firm],D(2))
  self.assertFalse(f.action('liquidate',c));self.assertEqual(f.cash(),wealth)
 def test_liquidation_distributes_cash_pro_rata_between_multiple_claims(self):
  f,c,bank,firm=self.seed();self.assertTrue(f.action('lend',c))
  # Add a second funded bank through another country, then attach its distinct claim.
  d=f.country(gold=D(1000),estate=D(1000));self.assertTrue(f.action('create_bank_private',d));bank2=d['tsin_le_primary_bank']
  f.state=f.root=c;c['tsin_le_primary_bank']=bank2
  f.maps['tsin_le_owner'][bank2]=c
  self.assertTrue(f.action('lend',c))
  f.maps['tsin_le_cash'][firm]=D(40)
  for loan in f.lists['tsin_active_entity_loans']:f.maps['tsin_le_loan_missed'][loan]=D(12)
  f.effect('tsin_le_refresh_totals_effect',c);wealth=f.cash()
  self.assertTrue(f.action('liquidate',c))
  self.assertEqual(f.maps['tsin_le_cash'][bank],D(20));self.assertEqual(f.maps['tsin_le_cash'][bank2],D(20))
  self.assertEqual(f.maps['tsin_le_losses'][bank],D(80));self.assertEqual(f.maps['tsin_le_losses'][bank2],D(80))
  self.assertEqual(f.cash(),wealth)
 def test_annexation_preserves_entity_ids_cash_contracts_and_private_shares(self):
  f,target,bank,firm=self.seed();self.assertTrue(f.action('lend',target))
  recipient=f.country(gold=D(100),estate=D(1000));self.assertTrue(f.action('create_bank_private',recipient))
  oldcash=dict(f.maps['tsin_le_cash']);oldunits=dict(f.maps['tsin_le_units']);oldloans=dict(f.maps['tsin_le_loan_principal'])
  f.annex('prepare',recipient,target);self.assertIs(f.maps['tsin_le_owner'][bank],target)
  target['num_locations']=D(0);f.annex('finish',recipient,target);f.annex('finish',recipient,target)
  self.assertIs(f.maps['tsin_le_owner'][bank],recipient);self.assertIs(f.maps['tsin_le_owner'][firm],recipient)
  self.assertEqual(f.maps['tsin_le_cash'],oldcash);self.assertEqual(f.maps['tsin_le_units'],oldunits);self.assertEqual(f.maps['tsin_le_loan_principal'],oldloans)
 def test_own_entity_audit_pays_real_cash_and_does_not_reuse_legacy_certificate(self):
  f,c,bank,firm=self.seed();c['policies']={'tsin_bank_prudential_policy','tsin_disclosure_audited_policy'};c['tsin_bank_audit_valid']=D(1);c['tsin_firm_audit_valid']=D(1)
  self.assertFalse(f.action('lend',c));self.assertTrue(f.action('audit',c));self.assertFalse(f.action('audit',c))
  self.assertTrue(f.action('next',c));self.assertTrue(f.action('audit',c))
  self.assertEqual(f.maps['tsin_le_cash'][bank],D(99));self.assertEqual(f.maps['tsin_le_cash'][firm],D(99))
  # Lend 100 needs 100 actual cash, so a bank audit alone cannot manufacture liquidity.
  self.assertFalse(f.action('lend',c))
  self.assertTrue(f.action('private_equity',c));self.assertTrue(f.action('lend',c))
 def test_unfunded_or_foreign_selection_cannot_be_paid_from_treasury(self):
  f,c,bank,firm=self.seed();c['gold']=D(0);c['estate']=D(0)
  self.assertFalse(f.action('public_equity',c));self.assertFalse(f.action('private_equity',c));self.assertFalse(f.action('contract',c))
  d=f.country();f.maps['tsin_le_owner'][firm]=d;c['gold']=D(1000);c['estate']=D(1000)
  self.assertFalse(f.action('audit',c));self.assertFalse(f.action('public_equity',c));self.assertFalse(f.action('contract',c))
 def test_helper_cannot_create_a_half_funded_entity_and_aborted_annex_keeps_owner(self):
  f,c,bank,firm=self.seed();c['gold']=D(0);c['estate']=D(0)
  count=f.globals['tsin_le_next_id'];cash=dict(f.maps['tsin_le_cash'])
  f.effect('tsin_le_create_effect',c,KIND='1',PUBLIC='yes',PRIMARY='tsin_le_primary_bank')
  self.assertEqual(f.globals['tsin_le_next_id'],count);self.assertEqual(f.maps['tsin_le_cash'],cash)
  recipient=f.country();f.annex('prepare',recipient,c);f.annex('finish',recipient,c)
  self.assertIs(f.maps['tsin_le_owner'][bank],c);self.assertEqual(f.maps['tsin_le_cash'],cash)
 def test_complex_map_values_are_staged_before_write(self):
  text=le.build()['in_game/common/scripted_effects/tsin_legal_entities.txt']
  self.assertNotRegex(text,r'add_to_global_variable_map\s*=\s*\{[^{}]*value\s*=\s*\{')
  self.assertIn('save_temporary_scope_value_as = { name = tsin_le_map_tmp_',text)
if __name__=='__main__':unittest.main()
