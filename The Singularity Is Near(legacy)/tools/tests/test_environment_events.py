import re, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdx
import gen_environment_events as ev

ROOT = pdx.MOD_ROOT


class EnvironmentEventTests(unittest.TestCase):
    def test_deployed_files_match_generator(self):
        for rel, text in ev.build().items():
            if rel.startswith('in_game/'):
                self.assertEqual(pdx.read_text(ROOT / rel), text, rel)

    def test_eight_events_each_claim_budget_and_have_two_options(self):
        text = pdx.read_text(ROOT / 'in_game/events/tsin_environment_events.txt')
        for n in range(1, 9):
            block = re.search(rf'tsin_envx\.{n} = \{{(.*?)\n\}}', text, re.S).group(1)
            self.assertIn('tsin_env_popup_claim_effect = yes', block, n)
            self.assertIn('tsin_env_popup_available_trigger = yes', block, n)
            self.assertEqual(block.count('option = {'), 2, n)
            self.assertIn('is_ai = no', block, n)

    def test_shared_budget_covers_all_existing_popups(self):
        for rel, event in [('tools/gen_pollution.py', 'tsin_pollution.1'), ('tools/gen_environment.py', 'tsin_environment.1'),
                           ('tools/gen_industrial_safety.py', 'tsin_industrial_safety.1')]:
            src = pdx.read_text(ROOT / rel)
            self.assertIn('tsin_env_popup_available_trigger = yes', src, rel)
            self.assertIn('tsin_env_popup_claim_effect = yes', src, rel)
            self.assertIn(event, src)

    def test_budget_is_one_per_calendar_year(self):
        trig = pdx.read_text(ROOT / 'in_game/common/scripted_triggers/tsin_environment_events.txt')
        self.assertIn('current_year > var:tsin_env_popup_year', trig)
        self.assertIn('NOT = { has_variable = tsin_env_popup_year }', trig)

    def test_pulse_is_wired_and_gated_for_players(self):
        on = pdx.read_text(ROOT / 'in_game/common/on_action/tsin_on_actions.txt')
        self.assertIn('\t\ttsin_envx_yearly_pulse\n', on)
        self.assertRegex(on, r'tsin_envx_yearly_pulse = \{\s*trigger = \{\s*is_ai = no')

    def test_localization_has_all_event_keys_in_both_languages(self):
        for lang in ('korean', 'english'):
            loc = pdx.read_text(ROOT / f'main_menu/localization/{lang}/tsin_environment_events_l_{lang}.yml')
            for n in range(1, 9):
                for suffix in ('title', 'desc', 'a', 'b'):
                    self.assertIn(f'\n tsin_envx.{n}.{suffix}: ', loc, (lang, n, suffix))

    def test_smog_event_does_not_read_weather(self):
        text = pdx.read_text(ROOT / 'in_game/events/tsin_environment_events.txt')
        self.assertNotRegex(text.lower(), r'weather|rain|wind')
        self.assertIn('tsin_pollution_bad_years', text)

    def test_no_forbidden_shortcuts(self):
        text = pdx.read_text(ROOT / 'in_game/events/tsin_environment_events.txt')
        self.assertNotIn('add_advance', text)
        self.assertNotIn('has_tag', text)

    def test_relocation_is_converted_not_moved(self):
        loc = pdx.read_text(ROOT / 'main_menu/localization/english/tsin_environment_events_l_english.yml')
        self.assertIn('conversion', loc.lower())
        self.assertNotIn('move the factory', loc.lower())


if __name__ == '__main__':
    unittest.main()
