import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdx  # noqa: E402
from gen_bill_events import CATEGORIES, blocks, inner  # noqa: E402

ROOT = pdx.MOD_ROOT
LOCK = 'tsin_policy_enactable_trigger = yes'
WOMEN = ['tsin_women_no_rights_policy', 'tsin_women_property_policy', 'tsin_women_labor_policy', 'tsin_women_suffrage_policy']
NAVAL = ['tsin_naval_coastal_defense_policy', 'tsin_naval_jeune_ecole_policy', 'tsin_naval_gunboat_diplomacy_policy', 'tsin_naval_blue_water_policy']
POLICE = ['tsin_police_night_watch_policy', 'tsin_police_city_police_policy', 'tsin_police_national_police_policy', 'tsin_police_political_police_policy']
HEALTH = ['tsin_health_laissez_faire_policy', 'tsin_health_quarantine_policy', 'tsin_health_board_policy']


def era(rel: str) -> str:
    return pdx.strip_comments(pdx.read_text(ROOT / 'era_7' / rel))


def law(file_rel: str, name: str) -> dict:
    """{policy: block text} of a law (reserved keys excluded)."""
    top = blocks(era(file_rel))
    return {k: v for k, v in blocks(inner(top[name])).items() if k not in ('potential', 'allow')}


def parts(policy_text: str) -> dict:
    return blocks(inner(policy_text))


class WomenRightsTests(unittest.TestCase):
    def setUp(self):
        self.file = 'in_game/common/laws/tsin_women_rights_law.txt'
        self.pol = law(self.file, 'tsin_women_rights_law')

    def test_law_category_and_policy_ids_in_order(self):
        self.assertIn('law_category = socioeconomic', era(self.file))
        self.assertEqual(list(self.pol), WOMEN)  # first policy is the default

    def test_every_policy_uses_bill_lock(self):
        for key, text in self.pol.items():
            self.assertIn(LOCK, parts(text)['allow'], key)

    def test_sequential_allow_with_movement_thresholds(self):
        expect = {
            'tsin_women_property_policy': ('tsin_women_no_rights_policy', 20),
            'tsin_women_labor_policy': ('tsin_women_property_policy', 35),
            'tsin_women_suffrage_policy': ('tsin_women_labor_policy', 50),
        }
        for key, (prev, need) in expect.items():
            allow = parts(self.pol[key])['allow']
            self.assertIn(f'has_policy = policy:{prev}', allow, key)
            self.assertIn(f'var:tsin_womens_suffrage >= {need}', allow, key)
        # the default stage has no prerequisite
        self.assertNotIn('has_policy', parts(self.pol['tsin_women_no_rights_policy'])['allow'])

    def test_labor_stage_needs_factory_acts_or_better(self):
        allow = parts(self.pol['tsin_women_labor_policy'])['allow']
        self.assertIn('has_policy = policy:tsin_factory_acts_policy', allow)
        self.assertIn('has_policy = policy:tsin_labor_protection_policy', allow)

    def test_only_suffrage_opens_the_cabinet(self):
        for key, text in self.pol.items():
            mod = parts(text)['country_modifier']
            if key == 'tsin_women_suffrage_policy':
                self.assertRegex(mod, r'allow_female_cabinet\s*=\s*yes')
            else:
                self.assertNotIn('allow_female_cabinet', mod, key)
        self.assertNotIn('allow_female_leader', era(self.file))

    def test_estate_preferences_present(self):
        for key, text in self.pol.items():
            self.assertIn('estate_preferences', parts(text), key)

    def test_labor_law_exists_with_referenced_policies(self):
        society = era('in_game/common/laws/tsin_society_laws.txt')
        for p in ('tsin_factory_acts_policy', 'tsin_labor_protection_policy'):
            self.assertIn(p + ' = {', society)

    def test_movement_decreases_with_policy(self):
        values = pdx.read_text(ROOT / 'in_game/common/script_values/tsin_movement_values.txt')
        body = re.search(r'tsin_womens_suffrage_yearly_growth = \{(.*?)\n\}\n', values, re.S).group(1)
        for policy, amount in (('tsin_women_property_policy', 1), ('tsin_women_labor_policy', 1), ('tsin_women_suffrage_policy', 3)):
            self.assertRegex(body, rf'has_policy = policy:{policy} \}}\s*subtract = {amount}\b')

    def test_society_70_tables_a_bill(self):
        events = era('in_game/events/tsin_society.txt')
        start = events.index('tsin_society.70 = {')
        body = events[start:events.index('tsin_society.80 = {')]
        self.assertIn('tsin_table_bill_effect', body)
        self.assertIn('BONUS = 0.15', body)
        for p in WOMEN[1:]:
            self.assertIn(f'POLICY = policy:{p}', body)
        self.assertNotIn('add_policy', body)

    def test_unlocked_by_universal_education(self):
        adv = era('in_game/common/advances/tsin_05_mass_society.txt')
        block = blocks(adv)['tsin_universal_education_advance']
        self.assertIn('unlock_law = tsin_women_rights_law', block)


class NavalTests(unittest.TestCase):
    def setUp(self):
        self.file = 'in_game/common/laws/tsin_naval_ideology_law.txt'
        self.text = era(self.file)
        self.pol = law(self.file, 'tsin_naval_ideology_law')

    def test_military_with_ports_and_no_bill_trigger(self):
        self.assertIn('law_category = military', self.text)
        self.assertIn('num_of_ports > 0', self.text)
        self.assertNotIn('tsin_policy_enactable_trigger', self.text)

    def test_policies_and_years(self):
        self.assertEqual(list(self.pol), NAVAL)
        for key, text in self.pol.items():
            p = parts(text)
            self.assertIn('estate_preferences', p, key)
            self.assertIn('years = 2', text, key)

    def test_not_a_bill_law(self):
        for _, _, laws in CATEGORIES:
            self.assertNotIn('tsin_naval_ideology_law', laws)
        triggers = pdx.read_text(ROOT / 'in_game/common/scripted_triggers/tsin_legislation_triggers.txt')
        self.assertNotIn('tsin_naval_ideology_law', triggers)

    def test_unlocked_by_steamship_lines(self):
        block = blocks(era('in_game/common/advances/tsin_04_choices.txt'))['tsin_steamship_lines']
        self.assertIn('unlock_law = tsin_naval_ideology_law', block)


class PoliceHealthTests(unittest.TestCase):
    def setUp(self):
        self.file = 'in_game/common/laws/tsin_police_health_laws.txt'
        self.text = era(self.file)
        top = blocks(self.text)
        self.police = {k: v for k, v in blocks(inner(top['tsin_police_law'])).items() if k not in ('potential', 'allow')}
        self.health = {k: v for k, v in blocks(inner(top['tsin_public_health_law'])).items() if k not in ('potential', 'allow')}

    def test_categories(self):
        top = blocks(self.text)
        self.assertIn('law_category = administrative', top['tsin_police_law'])
        self.assertIn('law_category = socioeconomic', top['tsin_public_health_law'])

    def test_policy_ids_in_order(self):
        self.assertEqual(list(self.police), POLICE)
        self.assertEqual(list(self.health), HEALTH)

    def test_all_policies_use_bill_lock(self):
        for key, text in {**self.police, **self.health}.items():
            self.assertIn(LOCK, parts(text)['allow'], key)

    def test_health_avoids_cholera_signal(self):
        self.assertNotIn('global_disease_resistance', self.text)

    def test_unlock_advances(self):
        self.assertIn('unlock_law = tsin_police_law', blocks(era('in_game/common/advances/tsin_04_choices.txt'))['tsin_modern_police'])
        self.assertIn('unlock_law = tsin_public_health_law', blocks(era('in_game/common/advances/tsin_05_mass_society.txt'))['tsin_modern_sewerage_advance'])


class BillSystemTests(unittest.TestCase):
    def test_category_180(self):
        cat = {c[0]: c for c in CATEGORIES}
        self.assertIn(180, cat)
        self.assertEqual(cat[180][2], ['tsin_women_rights_law', 'tsin_police_law', 'tsin_public_health_law'])
        self.assertEqual(sorted(cat), [110, 120, 130, 140, 150, 160, 170, 180])

    def test_reform_trigger_lists_new_reforms(self):
        text = pdx.read_text(ROOT / 'in_game/common/scripted_triggers/tsin_legislation_triggers.txt')
        body = text[text.index('tsin_bill_reform_policy_trigger = {'):text.index('tsin_bill_reform_pressure_trigger = {')]
        for p in ('tsin_women_property_policy', 'tsin_women_labor_policy', 'tsin_women_suffrage_policy',
                  'tsin_health_quarantine_policy', 'tsin_health_board_policy'):
            self.assertIn(f'this = policy:{p}', body)
        self.assertNotIn('tsin_naval', body)

    def test_bill_law_trigger_lists_new_laws(self):
        text = pdx.read_text(ROOT / 'in_game/common/scripted_triggers/tsin_legislation_triggers.txt')
        body = text[text.index('tsin_bill_law_policy_trigger = {'):text.index('tsin_bill_labor_policy_trigger = {')]
        for law_key in ('tsin_women_rights_law', 'tsin_police_law', 'tsin_public_health_law'):
            self.assertIn(f'this = law:{law_key}', body)

    def test_generated_events_offer_new_policies_without_lock(self):
        events = era('in_game/events/tsin_legislation_bills.txt')
        self.assertIn('name = tsin_legislation.100.c180', events)
        self.assertIn('tsin_legislation.180 = {', events)
        for p in WOMEN + POLICE + HEALTH:
            self.assertIn(f'tsin_table_bill_effect = {{ POLICY = policy:{p} BONUS = 0 }}', events, p)
        for p in NAVAL:
            self.assertNotIn(p, events)
        self.assertNotIn('tsin_policy_enactable_trigger', events)

    def test_generated_suffrage_option_copies_thresholds(self):
        events = era('in_game/events/tsin_legislation_bills.txt')
        start = events.index('name = tsin_women_suffrage_policy')
        option = events[start:events.index('ai_chance', start)]
        self.assertIn('var:tsin_womens_suffrage >= 50', option)
        self.assertIn('has_policy = policy:tsin_women_labor_policy', option)


class LocalizationTests(unittest.TestCase):
    def test_keys_in_both_languages(self):
        keys = WOMEN + NAVAL + POLICE + HEALTH + ['tsin_women_rights_law', 'tsin_naval_ideology_law', 'tsin_police_law', 'tsin_public_health_law']
        for lang in ('korean', 'english'):
            names = ''
            for f in (ROOT / 'era_7/main_menu/localization' / lang).glob('*.yml'):
                names += pdx.read_text(f)
            for key in keys:
                self.assertRegex(names, rf'(?m)^ {key}: ', f'{lang} {key}')
                self.assertRegex(names, rf'(?m)^ {key}_desc: ', f'{lang} {key}_desc')
            leg = pdx.read_text(ROOT / f'main_menu/localization/{lang}/tsin_m7_leg_l_{lang}.yml')
            for key in ('tsin_legislation.100.c180', 'tsin_legislation.180.title', 'tsin_legislation.180.desc', 'tsin_legislation.180.z'):
                self.assertRegex(leg, rf'(?m)^ {re.escape(key)}: ', f'{lang} {key}')

    def test_no_duplicate_keys_across_v_files(self):
        for lang in ('korean', 'english'):
            seen = {}
            for f in sorted((ROOT / 'era_7/main_menu/localization' / lang).glob('*.yml')):
                if 'tsin_v_' not in f.name:
                    continue
                for key in re.findall(r'(?m)^ (\w+):', pdx.read_text(f)):
                    self.assertNotIn(key, seen, f'{key} in {f.name} and {seen.get(key)}')
                    seen[key] = f.name


if __name__ == '__main__':
    unittest.main()
