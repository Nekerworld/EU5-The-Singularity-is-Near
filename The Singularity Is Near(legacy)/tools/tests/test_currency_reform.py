from pathlib import Path
from decimal import Decimal as D
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_finance_ledger import LedgerFixture
from test_capital_markets import get


class DenominationFixture(LedgerFixture):
    """Shared generated-script interpreter with multiple country ledgers."""
    pass


class CurrencyReformTests(unittest.TestCase):
    def test_reform_rebases_every_matching_creditor_and_keeps_real_debt(self):
        f=DenominationFixture();borrower=f.state
        borrower.update(tsin_fx=D(100),tsin_foreign_liability_local=D(3000))
        other_borrower={'tsin_fx':D(20)}
        lenders=[{'tsin_foreign_partner':borrower,'tsin_foreign_local_principal':D(1000),'tsin_foreign_principal':D(10),'tsin_bank_cash':D(50)},
                 {'tsin_foreign_partner':borrower,'tsin_foreign_local_principal':D(2000),'tsin_foreign_principal':D(20),'tsin_bank_cash':D(80)}]
        unrelated={'tsin_foreign_partner':other_borrower,'tsin_foreign_local_principal':D(500),'tsin_foreign_principal':D(25),'tsin_bank_cash':D(90)}
        f.countries=[borrower,*lenders,other_borrower,unrelated]
        old_wealth=f.total();old_value=sum(c['tsin_foreign_local_principal']/borrower['tsin_fx'] for c in lenders)
        self.assertTrue(f.action('redenominate'))
        self.assertEqual(borrower['tsin_fx'],10);self.assertEqual(borrower['tsin_foreign_liability_local'],300)
        self.assertEqual([c['tsin_foreign_local_principal'] for c in lenders],[D(100),D(200)])
        self.assertEqual(sum(c['tsin_foreign_local_principal']/borrower['tsin_fx'] for c in lenders),old_value)
        self.assertEqual(sum(c['tsin_foreign_principal'] for c in lenders),old_value)
        self.assertEqual(unrelated['tsin_foreign_local_principal'],500)
        self.assertEqual([c['tsin_bank_cash'] for c in lenders],[D(50),D(80)])
        self.assertEqual(f.total(),old_wealth)

    def test_devaluation_keeps_local_notional_and_reform_stays_throttled(self):
        f=DenominationFixture();f.state.update(tsin_fx=D(100),tsin_foreign_liability_local=D(1000))
        self.assertTrue(f.action('devalue'));self.assertEqual(f.state['tsin_foreign_liability_local'],1000)
        self.assertEqual(f.state['tsin_fx'],D('110.00'))
        self.assertFalse(f.action('redenominate'))


if __name__=='__main__':unittest.main()
