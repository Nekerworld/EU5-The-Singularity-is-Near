import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gen_facility_aging import build


class FacilityOperationTests(unittest.TestCase):
    def setUp(self):
        self.b = build()
        self.auto = self.b['in_game/common/auto_modifiers/tsin_facility_aging.txt']

    def test_industry_penalty_skips_spill_shutdown(self):
        # Industry wear/gap blocks must carry the spill guard; other bundles must not.
        blocks = {}
        current = None
        for line in self.auto.splitlines():
            if line and not line.startswith(' ') and line.endswith('= { category = location type = location'):
                current = line.split(' ')[0]
                blocks[current] = ''
            if current:
                blocks[current] += line + '\n'
        industry = {k: v for k, v in blocks.items() if k.startswith('tsin_facility_industry_')}
        self.assertEqual(len(industry), 2)
        for block in industry.values():
            self.assertIn('NOT = { has_variable = tsin_spill_shutdown }', block)
        for k, block in blocks.items():
            if not k.startswith('tsin_facility_industry_'):
                self.assertNotIn('tsin_spill_shutdown', block)

    def test_age_is_not_a_modifier(self):
        # Age never feeds a location modifier; only wear and technology gap do.
        self.assertNotIn('tsin_facility_industry_age', self.auto)
        self.assertNotIn('_age_scale', self.auto)

    def test_subsidy_and_limit_text_present(self):
        for lang in ['korean', 'english']:
            text = self.b[f'main_menu/localization/{lang}/tsin_facility_aging_l_{lang}.yml']
            self.assertIn('subsidy' if lang == 'english' else '정부 지원금', text)


if __name__ == '__main__':
    unittest.main()
