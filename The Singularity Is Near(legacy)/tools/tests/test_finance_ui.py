from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdx
from finance_ui import build, patch_credit, patch_tabs, STOCK, OVERVIEW, NATIVE_CREDIT, CREDIT, EXTRA_TABS


class FinanceUITests(unittest.TestCase):
    def test_native_credit_actions_and_entire_original_body_survive(self):
        original = pdx.read_text(pdx.game_root() / CREDIT)
        patched = patch_credit(original)
        injected = '\n\t\ttsin_finance_tabs = {}\n'
        injected += f'\t\ttsin_finance_overview = {{ visible = "[{OVERVIEW}]" }}\n'
        injected += f'\t\ttsin_stock_panel = {{ visible = "[{STOCK}]" }}\n'
        injected += ''.join(f'\t\t{subtab}_panel = {{ visible = "[LateralView.Vars.HasValue(\'subtab\', \'{subtab}\')]" }}\n' for _, subtab in EXTRA_TABS)
        restored = patched.replace(injected, '').replace(f'\t\t\tvisible = "[{NATIVE_CREDIT}]"\n', '')
        self.assertEqual(restored, original)
        for method in ['OnDeclareBankruptcy', 'OnRepayLoan', 'OnSellBonds', 'OnRedeemBond']:
            self.assertEqual(patched.count(method), original.count(method))

    def test_primary_has_five_buttons_and_no_separate_stock_button(self):
        text = pdx.read_text(pdx.game_root() / 'in_game/gui/economy_lateralview.gui')
        patched = patch_tabs(text)
        start = patched.index('template economy_main_tabs {')
        opening = patched.index('{', start)
        end = pdx.matching_brace(pdx.strip_comments(patched), opening)
        tabs = patched[opening:end]
        self.assertEqual(tabs.count('button_main_tab_alt = {'), 5)
        self.assertNotIn('TSIN_STOCK_TAB', tabs)
        self.assertIn("IsLateralViewOpened('credit')", tabs)
        self.assertIn('TSIN_FINANCE_TAB', tabs)

    def test_existing_unparameterized_credit_defaults_to_native_content(self):
        files = build()
        credit = files[CREDIT]
        self.assertIn(f'visible = "[{NATIVE_CREDIT}]"', credit)
        ui = files['in_game/gui/tsin_finance.gui']
        self.assertIn("subtab = credit", ui)
        self.assertIn("subtab = tsin_stocks", ui)
        self.assertIn("subtab = tsin_finance_overview", ui)
        self.assertIn('blockoverride "tab_text"', ui)
        self.assertIn('action_tooltip = {', ui)
        self.assertIn('title = "OPEN_TAB"', ui)
        self.assertNotIn('blockoverride "text"', ui)
        self.assertNotIn('on_action_left', ui)
        self.assertIn('icon_text_2rows', ui)
        self.assertIn('bg_paper_card', ui)
        self.assertIn('TSIN_FINANCE_SECTION_TREASURY', ui)
        self.assertIn('TSIN_FINANCE_SECTION_DEBT', ui)
        self.assertIn('TSIN_FINANCE_SECTION_PULSE', ui)
        self.assertIn('size = { 400 60 }', ui)
        self.assertIn('TSIN_FINANCE_OVERVIEW_HINT', ui)
        self.assertIn('TSIN_FINANCE_CREDIT_HINT', ui)
        self.assertIn('tagtooltip_enabled = yes', ui)
        self.assertIn('@left_panel_width = 780', files['in_game/gui/ingame_topbar.gui'])
        self.assertNotIn('EconomyView.', ui)
        self.assertNotIn('change_variable', ui)
        self.assertNotIn('every_owned_location', ui)
        self.assertNotIn('TSIN_FINANCE_PENSION', ui)

    def test_repatch_and_unknown_credit_layout_are_rejected(self):
        original = pdx.read_text(pdx.game_root() / CREDIT)
        with self.assertRaises(ValueError):
            patch_credit(patch_credit(original))
        with self.assertRaises(ValueError):
            patch_credit(original.replace('using = economy_main_tabs', 'using = renamed'))
