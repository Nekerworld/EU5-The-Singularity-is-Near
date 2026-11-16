from pathlib import Path
import sys,unittest
from decimal import Decimal as D
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_legal_entities import LegalEntityFixture
class EntityRestructuringTests(unittest.TestCase):
 def test_secondary_buyout_pays_owners_and_never_injects_company_cash(self):
  f=LegalEntityFixture();c=f.country(gold=D(1000),estate=D(1000))
  self.assertTrue(f.action('create_company_private',c));firm=c['tsin_le_primary_company'];wealth=f.cash()
  self.assertTrue(f.action('buyout',c))
  self.assertEqual(c['gold'],D(900));self.assertEqual(c['estate'],D(1000))
  self.assertEqual(f.maps['tsin_le_cash'][firm],D(100));self.assertEqual(f.maps['tsin_le_public_units'][firm],D(100))
  self.assertEqual(f.cash(),wealth);self.assertFalse(f.action('buyout',c))
 def pair(self):
  f=LegalEntityFixture();a=f.country(gold=D(1000),estate=D(1000));b=f.country(gold=D(1000),estate=D(1000))
  for c,rate in [(a,4),(b,7)]:
   c['tsin_rate']=D(rate);self.assertTrue(f.action('create_bank_public',c));self.assertTrue(f.action('create_company_public',c));self.assertTrue(f.action('lend',c))
  target=b['tsin_le_primary_company'];survivor=a['tsin_le_primary_company']
  f.annex('prepare',a,b);b['num_locations']=D(0);f.annex('finish',a,b)
  a['tsin_le_selected']=target
  return f,a,target,survivor
 def test_public_reorganization_preserves_ids_terms_cash_and_liabilities(self):
  f,c,target,survivor=self.pair()
  rates=dict(f.maps['tsin_le_loan_rate']);maturities=dict(f.maps['tsin_le_loan_maturity']);principals=dict(f.maps['tsin_le_loan_principal']);wealth=f.cash()
  self.assertTrue(f.action('merge',c))
  self.assertEqual(f.maps['tsin_le_cash'][survivor],D(400));self.assertEqual(f.maps['tsin_le_cash'][target],D(0))
  self.assertEqual(f.maps['tsin_le_debt'][survivor],D(200));self.assertEqual(f.maps['tsin_le_debt'][target],D(0))
  self.assertEqual(f.maps['tsin_le_status'][target],D(3));self.assertEqual(f.maps['tsin_le_merged_into'][target],survivor)
  self.assertEqual(f.maps['tsin_le_loan_rate'],rates);self.assertEqual(f.maps['tsin_le_loan_maturity'],maturities);self.assertEqual(f.maps['tsin_le_loan_principal'],principals)
  self.assertTrue(all(owner==survivor for owner in f.maps['tsin_le_loan_borrower'].values()))
  self.assertEqual(f.cash(),wealth-D(5));self.assertFalse(f.action('merge',c));self.assertEqual(f.cash(),wealth-D(5))
 def test_private_ownership_or_partial_processing_prevents_merge(self):
  f,c,target,survivor=self.pair();wealth=f.cash()
  f.maps['tsin_le_public_units'][target]=D(50);self.assertFalse(f.action('merge',c))
  f.maps['tsin_le_public_units'][target]=D(100);f.maps['tsin_le_merger_phase'][target]=D(1)
  self.assertFalse(f.action('merge',c));self.assertEqual(f.cash(),wealth)
 def test_debt_free_closure_returns_actual_cash_by_ownership_once(self):
  f=LegalEntityFixture();c=f.country(gold=D(1000),estate=D(1000))
  self.assertTrue(f.action('create_company_private',c));self.assertTrue(f.action('public_equity',c))
  firm=c['tsin_le_primary_company'];wealth=f.cash()
  self.assertTrue(f.action('close',c))
  self.assertEqual(c['gold'],D(1000));self.assertEqual(c['estate'],D(1000));self.assertEqual(f.maps['tsin_le_cash'][firm],D(0))
  self.assertFalse(f.action('close',c));self.assertEqual(f.cash(),wealth)
 def test_outstanding_debt_or_lender_claim_prevents_capital_withdrawal(self):
  f,c,target,survivor=self.pair()
  self.assertFalse(f.action('close',c))
  c['tsin_le_selected']=c['tsin_le_primary_bank'];self.assertFalse(f.action('close',c))
if __name__=='__main__':unittest.main()
