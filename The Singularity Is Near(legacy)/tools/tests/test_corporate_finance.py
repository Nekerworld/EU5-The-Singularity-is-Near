from pathlib import Path
import sys,unittest
from decimal import Decimal as D
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_finance_ledger import LedgerFixture


class CorporateFinanceTests(unittest.TestCase):
    def test_subscriptions_are_funded_and_public_units_are_diluted(self):
        f=LedgerFixture();f.state['estate']=D(200);wealth=f.total()
        self.assertTrue(f.action('public_equity'));self.assertEqual(f.state['tsin_public_shares'],10)
        self.assertEqual(f.state['tsin_issued_shares'],110)
        f.state.pop('tsin_equity_cooldown');self.assertTrue(f.action('private_equity'))
        self.assertEqual(f.state['tsin_issued_shares'],120);self.assertEqual(f.state['tsin_public_shares'],10)
        self.assertEqual(f.total(),wealth)

    def test_dividends_split_one_payment_and_respect_all_creditors(self):
        f=LedgerFixture();f.action('public_equity');wealth=f.total()
        f.state['tsin_bond_principal']=D(1);self.assertFalse(f.action('dividend'))
        f.state['tsin_bond_principal']=D(0);f.state['tsin_foreign_liability_local']=D(1);self.assertFalse(f.action('dividend'))
        f.state['tsin_foreign_liability_local']=D(0);self.assertTrue(f.action('dividend'))
        self.assertEqual(f.state['tsin_firm_cash'],0);self.assertGreater(f.state['estate'],0)
        self.assertAlmostEqual(f.total(),wealth,places=20)

    def test_bond_proceeds_interest_and_maturity_use_cash_not_indices(self):
        f=LedgerFixture();f.state['estate']=D(100);wealth=f.total()
        self.assertTrue(f.action('bond'));self.assertEqual(f.state['tsin_bond_principal'],100)
        f.run(f.effects['tsin_ledger_month_effect']);self.assertGreater(f.state['tsin_bond_interest_paid'],0)
        self.assertEqual(f.state['tsin_bond_principal'],100)
        f.state.pop('tsin_bond_maturity');f.run(f.effects['tsin_ledger_month_effect'])
        self.assertGreater(f.state['tsin_bond_principal'],0);self.assertEqual(f.state['tsin_firm_cash'],0)
        self.assertAlmostEqual(f.total(),wealth,places=20)

    def test_paygo_contribution_and_benefit_are_one_transfer_chain(self):
        f=LedgerFixture();self.assertTrue(f.action('paygo_on'))
        f.run(f.effects['tsin_ledger_month_effect']);self.assertEqual(f.state['gold'],995)
        self.assertEqual(f.state['estate'],5);self.assertEqual(f.state['tsin_pension'],0)
        self.assertEqual(f.total(),1000)
        f.state['gold']=D(0);f.run(f.effects['tsin_ledger_month_effect'])
        self.assertEqual(f.state['tsin_pension_shortfall'],1);self.assertEqual(f.state['gold'],0)

    def test_bond_arrears_cannot_reset_insurance_claim_every_month(self):
        f=LedgerFixture();f.action('insurance');f.state['tsin_bond_principal']=D(1000000)
        for _ in range(20):f.run(f.effects['tsin_ledger_month_effect'])
        self.assertEqual(f.state['tsin_insurance'],75);self.assertEqual(f.total(),1000)


if __name__=='__main__':unittest.main()
