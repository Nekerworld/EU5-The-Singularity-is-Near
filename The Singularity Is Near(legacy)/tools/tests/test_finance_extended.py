from pathlib import Path
import sys,unittest
from decimal import Decimal as D
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_finance_ledger import build
from test_finance_ledger import LedgerFixture


class ExtendedFinanceTests(unittest.TestCase):
    def test_deposits_and_winding_down_settle_existing_cash_only(self):
        f=LedgerFixture();f.state['estate']=D(200);wealth=f.total()
        f.action('bank');self.assertTrue(f.action('open_bank'))
        f.run(f.effects['tsin_bank_quarter_effect'])
        self.assertEqual(f.state['tsin_deposits'],10)
        self.assertEqual(f.state['estate'],190);self.assertEqual(f.total(),wealth)
        f.action('stop_deposits');f.run(f.effects['tsin_bank_quarter_effect'])
        self.assertEqual(f.state['tsin_deposits'],0);self.assertEqual(f.state['estate'],200)
        self.assertEqual(f.total(),wealth)

    def test_reserve_facility_is_a_repayable_transfer(self):
        f=LedgerFixture();f.action('reserve');f.state['tsin_withdrawal_due']=D(50)
        self.assertTrue(f.action('liquidity'));self.assertEqual(f.state['tsin_liquidity_debt'],100)
        self.assertEqual(f.state['tsin_reserve'],0);self.assertEqual(f.total(),1000)
        f.action('liquidity_repay');self.assertEqual(f.state['tsin_liquidity_debt'],0)
        self.assertEqual(f.state['tsin_reserve'],100);self.assertEqual(f.total(),1000)

    def test_bank_cannot_lend_its_minimum_deposit_reserve(self):
        f=LedgerFixture();f.action('bank');f.state['tsin_deposits']=D(100)
        self.assertFalse(f.action('lend'))
        f.state['tsin_bank_cash']=D(120);self.assertTrue(f.action('lend'))
        self.assertEqual(f.state['tsin_bank_cash'],20)

    def test_unpaid_withdrawals_are_bounded_and_repaid_after_recovery(self):
        f=LedgerFixture();f.state.update(tsin_bank_open=D(1),tsin_deposits=D(100),tsin_bank_cash=D(5),tsin_arrears=D(6))
        f.run(f.effects['tsin_bank_quarter_effect'])
        self.assertEqual(f.state['tsin_deposits'],95);self.assertEqual(f.state['tsin_withdrawal_due'],35)
        self.assertEqual(f.state['tsin_bank_cash'],0)
        f.state.update(tsin_arrears=D(0),tsin_bank_cash=D(50))
        f.run(f.effects['tsin_bank_quarter_effect'])
        self.assertEqual(f.state['tsin_withdrawal_due'],0)
        self.assertGreaterEqual(f.state['tsin_bank_cash'],0)

    def test_borrower_currency_revaluation_changes_claims_without_cash(self):
        f=LedgerFixture();f.state.update(tsin_foreign_local_principal=D(100),tsin_foreign_principal=D(100))
        f.state['scope:tsin_foreign_partner.var:tsin_fx']=D(2)
        self.assertEqual(f.num('tsin_foreign_current_value'),50)
        self.assertEqual(f.total(),1000)
        f.state['scope:tsin_foreign_partner.var:tsin_firm_cash']=D(20)
        f.state['tsin_foreign_principal']=D(50)
        self.assertEqual(f.num('tsin_foreign_principal_payment'),20)
        f.state['tsin_tx']=D(20)
        self.assertEqual(f.num('tsin_foreign_local_payment'),40)

    def test_resolved_borrower_and_extended_gui_links_are_defined(self):
        files=build();effects=files['in_game/common/scripted_effects/tsin_finance_ledger_effects.txt']
        self.assertIn('var:tsin_foreign_partner ?= { num_locations > 0',effects)
        self.assertIn('change_variable = { name = tsin_bank_losses add = var:tsin_foreign_principal }',effects)
        self.assertIn('change_variable = { name = tsin_foreign_liability_local subtract = scope:tsin_foreign_lender.var:tsin_tx_local }',effects)
        self.assertIn('scrollwidget',files['in_game/gui/tsin_finance_ledger.gui'])
        self.assertIn('GetScriptedGui(\'tsin_ledger_foreign\').Execute',files['in_game/gui/tsin_finance_ledger.gui'])
        self.assertIn('has_variable = tsin_convertibility_suspended',files['in_game/common/scripted_guis/tsin_finance_ledger_guis.txt'])


if __name__=='__main__':unittest.main()
