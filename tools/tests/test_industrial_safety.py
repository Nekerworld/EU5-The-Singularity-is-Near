import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_industrial_safety import build
from gen_facility_aging import build as aging
class IndustrialSafetyTests(unittest.TestCase):
 def test_rare_actual_risk_and_existing_inspection_only(self):
  s=build()['in_game/common/scripted_effects/tsin_industrial_safety.txt']
  for gate in ('industry_wear >= 90','industry_age >= 20','tsin_pollution_water >= 60','building_employed_amount > 0','is_opened = yes','chance = 10','years = 20','years = 10'):
   self.assertIn(gate,s)
  self.assertGreaterEqual(s.count('owner ?= scope:tsin_safety_owner'),2)
  self.assertNotIn('every_country',s);self.assertNotIn('every_owned_location',s)
  hooks=aging()['in_game/common/scripted_effects/tsin_facility_aging.txt']
  self.assertEqual(hooks.count('tsin_industrial_safety_review_effect = yes'),1)
  self.assertLess(hooks.index('name = tsin_facility_industry_year value = current_year',hooks.index('tsin_facility_review_effect =')),hooks.index('tsin_industrial_safety_review_effect = yes'))
 def test_recovery_checks_current_ownership_and_cash_and_preserves_age(self):
  s=build()['in_game/events/tsin_industrial_safety.txt']
  self.assertGreaterEqual(s.count('owner ?= root controller ?= root'),2)
  self.assertGreaterEqual(s.count('gold >= scope:tsin_spill_district.tsin_spill_remediation_cost'),2)
  self.assertEqual(s.count('add_gold ='),1)
  self.assertIn('months = 3',s);self.assertIn('years = 3',s)
  self.assertNotIn('industry_age value',s);self.assertNotIn('industry_grade value',s)
 def test_no_population_death_or_mineral_rgo_change(self):
  b=build();s=str(b)
  for effect in ('kill_pop','change_pop','population_growth','local_raw_material_size','raw_material_output_modifier','local_disease_resistance'):
   self.assertNotIn(effect,s)
  auto=b['in_game/common/auto_modifiers/tsin_industrial_safety.txt']
  self.assertIn('has_variable = tsin_spill_soil',auto)
  self.assertIn('local_food_production_mult = -0.05',auto)
  self.assertNotIn('on_action',str(b.keys()))
if __name__=='__main__':unittest.main()
