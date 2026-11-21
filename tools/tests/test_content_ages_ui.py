"""Content-tab / age-7+ GUI patches."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdx
import gen_content_ages_ui as g


class ContentAgesUiTest(unittest.TestCase):
    def test_build_patches_vanilla_anchors(self):
        files = g.build()
        decisions = files[g.DECISIONS]
        technology = files[g.TECHNOLOGY]
        advances = files[g.ADVANCES]

        self.assertIn('TSIN: ages 7+ browser', decisions)
        self.assertNotIn('TSIN_CONTENT_AGES_HEADER', decisions)
        self.assertNotIn('TSIN_CONTENT_AGES_HELP', decisions)
        self.assertIn('AdvancesLateralView.GetAges', decisions)
        self.assertIn('GetUniqueContentCategories', decisions)
        self.assertIn(g.AGE7_PLUS, decisions)

        self.assertIn('age tabs fill', technology)
        self.assertIn('TechnologyLateralView.SelectAge(Age.Self)', technology)
        self.assertIn('using = layoutpolicy_expanding', technology)
        self.assertNotIn('minimumsize = { 140 36 }', technology)
        self.assertNotIn('header_secondary_tabs = {', technology.split('age tabs fill', 1)[1][:800])

        self.assertIn(g.AGE7_PLUS, advances)
        self.assertIn('GetUniqueAdvancesForAge(Age.Self)', advances)

        for lang in ('english', 'korean'):
            key = f'main_menu/localization/{lang}/tsin_content_ages_l_{lang}.yml'
            self.assertIn(key, files)
            self.assertNotIn('TSIN_CONTENT_AGES_HEADER', files[key])

    def test_check_matches_written_files(self):
        files = g.build()
        for rel, text in files.items():
            path = pdx.MOD_ROOT / rel
            self.assertTrue(path.exists(), rel)
            self.assertEqual(pdx.read_text(path), text, rel)


if __name__ == '__main__':
    unittest.main()
