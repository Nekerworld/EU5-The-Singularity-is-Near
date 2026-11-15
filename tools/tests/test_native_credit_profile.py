"""Execute the generated debt report against dated loans and perpetual bonds."""
from pathlib import Path
from decimal import Decimal as D
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdx
from test_finance_ledger import LedgerFixture
from test_capital_markets import parse, get
from gen_native_credit_profile import build, EFFECT
import finance_ui


class ProfileFixture(LedgerFixture):
    def __init__(self):
        self.state = {'gold': D(450), 'total_debt': D(1000), 'monthly_income_trade_and_tax': D(20)}
        self.country = self.state
        self.previous = None
        self.values = {}
        self.saved = {}
        self.effects = {}
        self.loans = []
        self.visits = 0
        self.rows = parse(EFFECT[EFFECT.index('{')+1:EFFECT.rindex('}')])

    def loan(self, amount, months, bond=False, borrower=None):
        item = {'remaining_debt': D(amount), 'months_left': D(months), 'is_bond': bond, 'borrower': self.country if borrower is None else borrower}
        self.loans.append(item)
        return item

    def num(self, value):
        if isinstance(value, str) and value.startswith('prev.'):
            return self.previous[value[5:]]
        return super().num(value)

    def valid(self, rows):
        for key, op, value in rows:
            if key == 'borrower':
                if self.state['borrower'] is not self.saved[value.removeprefix('scope:')]: return False
            elif key == 'is_bond':
                if self.state[key] != (value == 'yes'): return False
            elif not super().valid([(key, op, value)]): return False
        return True

    def run(self, rows):
        previous_if = False
        for key, op, value in rows:
            if key == 'if':
                previous_if = self.valid(get(value, 'limit'))
                if previous_if: self.run([r for r in value if r[0] != 'limit'])
            elif key == 'else':
                if not previous_if: self.run(value)
            elif key == 'every_loan':
                original = self.state
                for loan in self.loans:
                    self.visits += 1
                    self.state = loan
                    if self.valid(get(value, 'limit')): self.run([r for r in value if r[0] != 'limit'])
                self.state = original
            elif key.startswith('scope:'):
                original, prior = self.state, self.previous
                self.previous = original
                self.state = self.saved[key[6:]]
                self.run(value)
                self.state, self.previous = original, prior
            else: super().run([(key, op, value)])

    def sample(self): self.run(self.rows)


class NativeCreditProfileTests(unittest.TestCase):
    def test_boundaries_bonds_and_lent_loans_are_separated_without_contract_changes(self):
        f = ProfileFixture()
        for amount, months in [(10, -1), (20, 0), (30, 1), (40, 12), (50, 13)]: f.loan(amount, months)
        f.loan(60, 0, bond=True)
        f.loan(999, 1, borrower={})  # lender's asset must not become borrower debt
        f.loan(0, 0)
        before = [dict(x) for x in f.loans]
        f.sample()
        self.assertEqual(f.country['tsin_native_due_now'], 30)
        self.assertEqual(f.country['tsin_native_due_12'], 70)
        self.assertEqual(f.country['tsin_native_bond_principal'], 60)
        self.assertEqual(f.country['tsin_native_tax_trade_annual'], 240)
        self.assertEqual(f.country['tsin_native_debt_income_ratio'], D(1000)/240*100)
        self.assertEqual(f.country['gold'], 450)
        self.assertEqual(f.loans, before)
        self.assertNotIn('tsin_firm_debt', f.country)

    def test_repeated_sample_clears_stale_values_and_nonpositive_income_has_no_ratio(self):
        f = ProfileFixture(); f.loan(70, 2); f.sample(); f.sample()
        self.assertEqual(f.country['tsin_native_due_12'], 70)
        for income in [0, -2]:
            f.country['monthly_income_trade_and_tax'] = D(income)
            f.sample()
            self.assertNotIn('tsin_native_debt_income_ratio', f.country)
            self.assertEqual(f.country['tsin_native_tax_trade_annual'], 0)
        f.country['total_debt'] = D(0); f.visits = 0; f.sample()
        self.assertEqual(f.visits, 0)
        self.assertEqual(f.country['tsin_native_due_12'], 0)
        self.assertEqual(f.country['tsin_native_bond_principal'], 0)

    def test_read_only_monthly_profile_and_ui_are_connected(self):
        files = build()
        hook = files['in_game/common/on_action/tsin_native_credit_profile.txt']
        self.assertIn('monthly_country_pulse', hook)
        self.assertIn('is_ai = no', hook)
        for forbidden in ['every_country', 'every_owned_location', 'add_gold', 'give_loan', 'change_loan', 'tsin_firm_debt']:
            self.assertNotIn(forbidden, EFFECT)
        gui = finance_ui.build()['in_game/gui/tsin_finance.gui']
        for variable in ['tsin_native_bond_principal', 'tsin_native_due_12', 'tsin_native_due_now', 'tsin_native_debt_income_ratio']:
            self.assertIn(variable, gui)
        self.assertNotIn('every_loan', gui)
        for rel, expected in files.items(): self.assertEqual(pdx.read_text(pdx.MOD_ROOT/rel), expected)


if __name__ == '__main__': unittest.main()
