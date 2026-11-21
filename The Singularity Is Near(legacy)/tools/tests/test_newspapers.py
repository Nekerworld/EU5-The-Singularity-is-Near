import sys,unittest,re
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_newspapers import build
class NewspaperTests(unittest.TestCase):
 def test_archive_is_bounded_and_shifted_before_new_record(self):
  s=build()['in_game/common/scripted_effects/tsin_newspapers.txt']
  slots={int(x) for x in re.findall(r'name = tsin_news_(\d+)_type',s)}
  self.assertEqual(slots,set(range(6)))
  positions=[s.index('name = tsin_news_'+str(i)+'_type') for i in range(5,-1,-1)]
  self.assertEqual(positions,sorted(positions))
  self.assertNotIn('every_country',s);self.assertNotIn('every_owned_location',s)
 def test_reader_and_article_event_cannot_repeat_gameplay(self):
  b=build();reader=b['in_game/common/generic_actions/tsin_newspapers.txt'];event=b['in_game/events/tsin_newspapers.txt']
  for text in [reader,event]:
   for forbidden in ['add_gold','change_variable','spawn_disease','add_country_modifier','random_list']:
    self.assertNotIn(forbidden,text)
  self.assertIn('tsin_has_periodical_press = yes',reader)
  fx=b['in_game/common/scripted_effects/tsin_newspapers.txt']
  self.assertIn('current_year > var:tsin_news_popup_year',fx)
 def test_actual_sources_and_persistent_generator_hooks_are_connected(self):
  for rel in ['tools/gen_standardization.py','tools/gen_pollution.py','tools/gen_facility_aging.py','in_game/common/scripted_effects/tsin_cholera_disease_effects.txt']:
   self.assertIn('tsin_news_record_effect',pdx.read_text(pdx.MOD_ROOT/rel))
  fx=build()['in_game/common/scripted_effects/tsin_newspapers.txt']
  self.assertIn('var:tsin_arrears >= 6',fx)
  self.assertIn('var:tsin_bond_arrears >= 6',fx)
  self.assertIn('NOT = { has_variable = tsin_news_financial_arrears_covered }',fx)
if __name__=='__main__':unittest.main()
