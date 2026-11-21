import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_standardization import build,DOMAINS
class StandardizationTests(unittest.TestCase):
 def test_choices_are_independent_and_revision_is_paid(self):
  outputs=build();s=outputs['in_game/common/generic_actions/tsin_standardization.txt']
  blocks={b.key:b.text for b in pdx.top_level_blocks(s)}
  for domain,(_,_,_,choices) in DOMAINS.items():
   for n,_,_,cost,_ in choices:
    b=blocks[f'tsin_standards_{domain}_{n}']
    self.assertIn(f'name = tsin_standard_{domain} value = {n}',b)
    for other in set(DOMAINS)-{domain}:
     self.assertNotIn(f'name = tsin_standard_{other} value',b)
    self.assertIn('years = 5',b)
    self.assertIn(f'gold = {cost}',outputs['in_game/common/prices/tsin_standardization.txt'])
 def test_attendance_alone_does_not_form_convention(self):
  b=build();trigger=b['in_game/common/scripted_triggers/tsin_standardization.txt']
  self.assertNotIn('participants',trigger)
  for d in DOMAINS:self.assertIn(f'global_var:tsin_standards_common_{d} >= 2',trigger)
  s=b['in_game/common/scripted_effects/tsin_standardization.txt']
  self.assertEqual(s.count('every_country ='),1)
  self.assertIn('exists = capital num_locations > 0',s)
  situation=b['in_game/common/situations/tsin_standardization.txt']
  self.assertIn('tsin_standards_common_agreement = no',situation)
 def test_every_policy_has_real_situation_panel_button(self):
  b=build();ui=b['in_game/gui/panels/situation/tsin_standardization.gui']
  for d,(_,_,_,choices) in DOMAINS.items():
   for n,*_ in choices:self.assertIn(f"GetGenericAction('tsin_standards_{d}_{n}')",ui)
  self.assertIn('PerformGenericAction(GenericAction.Self)',ui)
  self.assertNotIn('add_road',b['in_game/common/generic_actions/tsin_standardization.txt'])
if __name__=='__main__':unittest.main()
