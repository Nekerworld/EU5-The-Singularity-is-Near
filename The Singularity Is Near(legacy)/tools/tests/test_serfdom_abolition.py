import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdx


class SerfdomAbolitionTests(unittest.TestCase):
    def test_try_inject_allow_only(self):
        p = pdx.MOD_ROOT / 'era_7/in_game/common/societal_values/zzz_tsin_serfdom_abolition.txt'
        text = pdx.read_text(p)
        self.assertIn('TRY_INJECT:serfdom_vs_free_subjects', text)
        self.assertIn('has_variable = tsin_serfdom_abolished', text)
        self.assertNotIn('TRY_REPLACE:serfdom_vs_free_subjects', text)

    def test_retained_policy_blocked_after_abolition(self):
        text = pdx.read_text(pdx.MOD_ROOT / 'era_7/in_game/common/laws/tsin_society_laws.txt')
        # The retained policy allow block must mention abolition.
        start = text.index('tsin_serfdom_retained_policy')
        block = text[start:start + 400]
        self.assertIn('tsin_serfdom_abolished', block)

    def test_parliament_agenda_blocked(self):
        text = pdx.read_text(pdx.MOD_ROOT / 'era_7/in_game/common/parliament_agendas/tsin_parliament_agendas.txt')
        start = text.index('pa_tsin_restore_landlord_rights')
        block = text[start:start + 500]
        self.assertIn('tsin_serfdom_abolished', block)

    def test_events_and_effects_exist(self):
        events = pdx.read_text(pdx.MOD_ROOT / 'era_7/in_game/events/tsin_serfdom.txt')
        for n in (1, 2, 3):
            self.assertIn(f'tsin_serfdom.{n} =', events)
        effects = pdx.read_text(pdx.MOD_ROOT / 'era_7/in_game/common/scripted_effects/tsin_serfdom_abolition.txt')
        for name in ['tsin_serfdom_abolish_redeemed_effect', 'tsin_serfdom_abolish_landless_effect', 'tsin_serfdom_abolish_full_effect']:
            self.assertIn(name, effects)

    def test_flavor20_shares_abolition_effects(self):
        text = pdx.read_text(pdx.MOD_ROOT / 'era_7/in_game/events/tsin_flavor.txt')
        start = text.index('tsin_flavor.20 =')
        block = text[start:start + 2500]
        self.assertIn('tsin_serfdom_abolish_redeemed_effect', block)
        self.assertIn('tsin_serfdom_abolish_landless_effect', block)

    def test_permanent_modifiers_defined(self):
        text = pdx.read_text(pdx.MOD_ROOT / 'era_7/main_menu/common/static_modifiers/tsin_land_reform_modifiers.txt')
        for key in ['tsin_land_reform_redeemed', 'tsin_land_reform_landless', 'tsin_land_reform_full']:
            self.assertIn(key, text)


if __name__ == '__main__':
    unittest.main()
