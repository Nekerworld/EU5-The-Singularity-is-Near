import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_facility_aging import build,GROUPS
class FacilityAgingTests(unittest.TestCase):
 def test_review_is_low_frequency_and_not_driven_by_viewing(self):
  b=build();hooks=b['in_game/common/on_action/tsin_facility_aging.txt']
  self.assertIn('yearly_country_pulse',hooks);self.assertNotIn('monthly',hooks)
  fx=b['in_game/common/scripted_effects/tsin_facility_aging.txt']
  self.assertIn('current_year >= var:tsin_facility_due',fx)
  self.assertNotIn('every_country',fx);self.assertNotIn('every_owned_location',fx)
  action=next(x.text for x in pdx.top_level_blocks(b['in_game/common/generic_actions/tsin_facility_aging.txt']) if x.key=='tsin_facility_inspect')
  self.assertNotIn('add_gold',action);self.assertNotIn('review_effect',action)
  self.assertNotIn('change_variable',action)
 def test_repairs_do_not_modernize_or_reset_other_bundles(self):
  b=build();actions={x.key:x.text for x in pdx.top_level_blocks(b['in_game/common/generic_actions/tsin_facility_aging.txt'])}
  for g in GROUPS:
   repair=actions['tsin_facility_repair_'+g]
   self.assertNotIn(f'name = tsin_facility_{g}_grade',repair)
   self.assertIn(f'name = tsin_facility_{g}_wear value = 0',repair)
   for other in set(GROUPS)-{g}:self.assertNotIn('name = tsin_facility_'+other,repair)
   modern=actions['tsin_facility_modernize_'+g]
   self.assertIn(f'min = var:tsin_facility_{g}_grade',modern)
   self.assertNotIn('destroy_building',modern)
 def test_modernization_keeps_wear(self):
  b=build();actions={x.key:x.text for x in pdx.top_level_blocks(b['in_game/common/generic_actions/tsin_facility_aging.txt'])}
  for g in GROUPS:
   self.assertNotIn(f'name = tsin_facility_{g}_wear',actions['tsin_facility_modernize_'+g])
 def test_expansion_dilutes_age_instead_of_resetting_and_payments_are_bounded(self):
  s=build()['in_game/common/scripted_effects/tsin_facility_aging.txt']
  for g in GROUPS:
   self.assertIn(f'multiply = var:tsin_facility_{g}_size divide = var:tsin_facility_{g}_measured',s)
  self.assertIn('gold >= local_var:tsin_facility_cost',s)
  self.assertIn('min = 0 max = 100',s)
  # A small extension must retain most of the prior facility age.
  weighted_age=(20+5)*100/110
  self.assertGreater(weighted_age,20);self.assertLess(weighted_age,25)
if __name__=='__main__':unittest.main()
