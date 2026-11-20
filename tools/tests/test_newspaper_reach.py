import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gen_newspapers import build


class NewspaperReachTests(unittest.TestCase):
    def setUp(self):
        self.b = build()

    def test_press_stage_value_counts_owned_press_techs(self):
        values = self.b['in_game/common/script_values/tsin_newspapers.txt']
        self.assertIn('tsin_news_press_tier = {', values)
        for tech in ['printing_press_advance', 'tsin_popular_press_advance', 'tsin_mass_communication_advance']:
            self.assertIn(f'has_advance = {tech}', values)

    def test_reach_hides_slots_beyond_stage(self):
        custom = self.b['in_game/common/customizable_localization/tsin_newspapers.txt']
        # Slots 3-4 are hidden below periodical stage, slot 5 below mass stage.
        self.assertIn('tsin_news_press_tier < 2', custom)
        self.assertIn('tsin_news_press_tier < 3', custom)
        self.assertEqual(custom.count('tsin_news_press_tier < 2'), 3)  # slots 3, 4 and 5 below periodical stage
        self.assertEqual(custom.count('tsin_news_press_tier < 3'), 1)

    def test_records_are_not_discarded(self):
        effects = self.b['in_game/common/scripted_effects/tsin_newspapers.txt']
        # Shifting remains over six slots; reach affects display only.
        self.assertIn('tsin_news_5_type', effects)
        self.assertNotIn('remove_variable = tsin_news_0_type', effects)

    def test_no_broadcast_or_free_title(self):
        text = ' '.join(self.b[k] for k in self.b if k.endswith('.yml'))
        for banned in ['broadcast', 'radio', 'digital', 'free text']:
            self.assertNotIn(banned, text.lower())

    def test_read_action_does_not_rerun_effects(self):
        generic = self.b['in_game/common/generic_actions/tsin_newspapers.txt']
        self.assertIn('trigger_event_non_silently = tsin_news.1', generic)
        self.assertNotIn('tsin_news_record_effect', generic)
        self.assertNotIn('tsin_news_publication_effect', generic)


if __name__ == '__main__':
    unittest.main()
