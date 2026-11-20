import re, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdx

ROOT = pdx.MOD_ROOT


class SocialPoliticsTests(unittest.TestCase):
    def setUp(self):
        self.values = pdx.read_text(ROOT / 'in_game/common/script_values/tsin_legislation_values.txt')

    def test_pressure_reads_only_yearly_movement_values(self):
        m = re.search(r'tsin_bill_social_pressure = \{(.*?)\n\}', self.values, re.S)
        self.assertIsNotNone(m)
        body = m.group(1)
        self.assertIn('var:tsin_socialism', body)
        self.assertIn('var:tsin_womens_suffrage', body)
        self.assertNotIn('tsin_social_', body)  # manual survey outputs must not drive politics

    def test_pressure_is_capped_and_non_negative(self):
        body = re.search(r'tsin_bill_social_pressure = \{(.*?)\n\}', self.values, re.S).group(1)
        self.assertIn('min = 0', body)
        self.assertIn('max = 0.05', body)

    def test_term_applies_only_to_reform_bills(self):
        m = re.search(r'desc = tsin_bill_factor_social\s*value = tsin_bill_social_pressure', self.values)
        self.assertIsNotNone(m)
        before = self.values[:m.start()]
        block_start = before.rfind('if = {')
        self.assertIn('tsin_bill_reform_policy_trigger = yes', self.values[block_start:m.start()])

    def test_formula_stays_bounded(self):
        self.assertIn('min = 0.05', self.values)
        self.assertIn('max = 0.85', self.values)

    def test_factor_localized_in_both_languages(self):
        for lang in ('english', 'korean'):
            loc = pdx.read_text(ROOT / f'main_menu/localization/{lang}/tsin_m7_leg_l_{lang}.yml')
            self.assertIn('\n tsin_bill_factor_social: ', loc, lang)


if __name__ == '__main__':
    unittest.main()
