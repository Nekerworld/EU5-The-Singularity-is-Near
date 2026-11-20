import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import legal_entities as le
from legal_entity_restructuring import extend_outputs  # noqa: F401  (import check)


class RestructureR08Tests(unittest.TestCase):
    def setUp(self):
        self.b = le.build()
        self.effects = self.b['in_game/common/scripted_effects/tsin_legal_entities.txt']

    def block(self, name):
        start = self.effects.index(name + ' = {')
        depth = 0
        for i in range(start, len(self.effects)):
            c = self.effects[i]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return self.effects[start:i + 1]
        self.fail('unterminated ' + name)

    def test_restructure_keeps_loan_ids_and_only_changes_terms(self):
        body = self.block('tsin_le_restructure_loans_effect')
        self.assertNotIn('add_to_global_variable_list', body)  # no new loan record
        self.assertNotIn('global_var:tsin_le_next_loan', body)
        self.assertIn('tsin_le_loan_maturity', body)
        self.assertIn('tsin_le_loan_rate', body)
        self.assertIn('multiply = 0.5', body)
        self.assertIn('add = 24', body)
        self.assertNotIn('tsin_le_loan_principal', body)  # principal is not written down here

    def test_emergency_loan_is_secured_and_capped(self):
        body = self.block('tsin_le_emergency_loan_effect')
        self.assertIn('multiply = 0.5', body)
        self.assertIn('max = ', body)
        self.assertIn('tsin_active_entity_loans', body)
        self.assertIn('tsin_le_loan_lender', body)
        self.assertIn('tsin_le_loan_principal', body)

    def test_emergency_gate_is_liquidity_not_solvency(self):
        gate = self.b['in_game/common/scripted_effects/tsin_legal_entities.txt']
        self.assertIn('tsin_le_missed', gate)
        self.assertIn('policy:tsin_laissez_faire_policy', gate)

    def test_existing_buyout_still_present(self):
        self.assertIn('tsin_le_buyout_effect = {', self.effects)


if __name__ == '__main__':
    unittest.main()
