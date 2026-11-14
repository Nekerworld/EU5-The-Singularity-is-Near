"""Regression cases for missing panels and invisible map groups."""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from integration_checks import check

class IntegrationTests(unittest.TestCase):
    def test_missing_panel_and_out_of_range_group(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'mod'
            game = Path(temp) / 'game'
            def put(base, rel, text):
                p = base / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(text, encoding='utf-8')
            put(root, 'in_game/common/disasters/test.txt', 'tsin_test = { }')
            put(game, 'in_game/gui/hud_bot.gui', "[GetMapModeGroupFromCategory('population', '(int32)1')]")
            put(root, 'in_game/gfx/map/map_modes/test.txt', 'tsin_test = { category = population index = 93 }')
            errors, _ = check(root, game)
            self.assertEqual(len(errors), 2)
            self.assertTrue(any('missing panel' in x for x in errors))
            self.assertTrue(any('not displayed' in x for x in errors))
            put(root, 'in_game/gui/panels/disaster/tsin_test.gui', 'disaster_panel = { }')
            put(root, 'in_game/gfx/map/map_modes/test.txt', 'tsin_test = { category = population index = 1 }')
            self.assertEqual(check(root, game)[0], [])
            put(root, 'in_game/common/on_action/test.txt', 'yearly_country_pulse = { on_actions = { tsin_missing } }')
            put(root, 'main_menu/localization/korean/test.yml', 'l_korean:\n tsin_label: "[TSIN 디버그]"')
            errors, _ = check(root, game)
            self.assertEqual(len(errors), 2)
            self.assertTrue(any('callback' in x for x in errors))
            self.assertTrue(any('brackets' in x for x in errors))

if __name__ == '__main__':
    unittest.main()
