"""Integration regressions: preserve all upstream widgets and unit boundaries."""
from pathlib import Path
import re
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdx
from gen_glorp_stats_compat import patched_files, GLORP_REL, LEFT_REL


class GlorpStatsTests(unittest.TestCase):
    def test_no_upstream_widgets_removed(self):
        source = pdx.workshop_root() / '3812518640'
        if not (source / GLORP_REL).exists():
            self.skipTest('Glorp workshop source is unavailable')
        patched = patched_files(source)
        for rel, generated in patched.items():
            restored = generated.split('\n', 1)[1]
            restored = restored.replace('                        tsin_glorp_stats_rows = {}\n', '')
            for a, b in [('size = { 450 150 }', 'size = { 450 90 }'),
                         ('maximumsize = { 515 150 }', 'maximumsize = { 515 90 }'),
                         ('size = { 515 150 }', 'size = { 515 90 }'),
                         ('position = { 20 273 }', 'position = { 20 213 }')]:
                restored = restored.replace(a, b)
            self.assertEqual(restored, pdx.read_text(source / rel), rel)

    def test_display_unit_boundaries(self):
        text = pdx.read_text(pdx.MOD_ROOT / 'in_game/common/customizable_localization/tsin_stats_display.txt')
        for block in pdx.top_level_blocks(text):
            self.assertIn('random_valid = no', block.text)
            limits = re.findall(r'var:\w+ >= (\d+).*?localization_key = (\w+)', block.text, re.S)
            self.assertEqual([int(n) for n, _ in limits], [10**12, 10**9, 10**6, 10**3])
            for number, expected in [(999, 'BASE'), (1000, 'K'), (999999, 'K'), (10**6, 'M'), (10**9, 'B'), (10**12, 'T')]:
                selected = next((key.rsplit('_', 1)[1] for n, key in limits if number >= int(n)), 'BASE')
                self.assertEqual(selected, expected)

if __name__ == '__main__':
    unittest.main()
