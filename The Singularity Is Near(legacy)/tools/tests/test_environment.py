import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_environment import build
from gen_pollution import build as pollution
from environment_extension import transform_aggregate
from gen_bill_events import law_policies
class EnvironmentTests(unittest.TestCase):
 def test_rural_mines_do_not_enter_urban_education_gdp_or_labor(self):
  s=pdx.read_text(pdx.MOD_ROOT/'in_game/common/scripted_effects/tsin_aggregate_effects.txt')
  root=next(b for b in pdx.top_level_blocks(s) if b.key=='tsin_annual_country_aggregate_effect')
  loop=next(b for b in pdx.top_level_blocks(root.text[root.text.index('{')+1:-1]) if b.key=='every_owned_location')
  inner=loop.text[loop.text.index('{')+1:-1];blocks=pdx.top_level_blocks(inner)
  urban=next(b for b in blocks if b.key=='if')
  guard=next(b.text for b in pdx.top_level_blocks(urban.text[urban.text.index('{')+1:-1]) if b.key=='limit')
  self.assertNotIn('tsin_is_polluting_mine',guard)
  self.assertIn('name = tsin_agg_urban_pop',urban.text)
  outside=inner[:urban.start]+inner[urban.end:]
  self.assertNotIn('name = tsin_agg_urban_pop',outside)
  self.assertEqual(s.count('every_owned_location ='),1)
  self.assertEqual(s.count('tsin_pollution_location_tick_effect = yes'),1)
  self.assertEqual(transform_aggregate(s),s)
 def test_real_staffing_and_real_rgo_output_drive_sources_and_treatment(self):
  s=pollution()['in_game/common/scripted_effects/tsin_pollution.txt']
  self.assertIn('tsin_is_polluting_mine = yes raw_material_output > 0',s)
  self.assertIn('divide = building_employment_size_amount',s)
  self.assertIn('name = tsin_pollution_treatment_capacity value = 0',s)
  self.assertIn('name = tsin_pollution_inspection_capacity value = 0',s)
  self.assertNotIn('raw_material_output_modifier',s)
  self.assertIn('is_mining_rgo = yes',build()['in_game/common/scripted_triggers/tsin_environment.txt'])
 def test_water_treatment_does_not_filter_smoke_and_no_sample_is_not_clean(self):
  v=pollution()['in_game/common/script_values/tsin_pollution.txt']
  air=next(b.text for b in pdx.top_level_blocks(v) if b.key=='tsin_pollution_air_target')
  self.assertNotIn('treatment_capacity',air)
  fx=build()['in_game/common/scripted_effects/tsin_environment.txt']
  self.assertIn('remove_variable = tsin_pollution_exposure',fx)
  self.assertIn('remove_variable = tsin_pollution_water_exposure',fx)
  self.assertIn('divide = var:tsin_pollution_surveyed_pop',fx)
  self.assertNotIn('tsin_agg_urban_pop',fx)
 def test_policy_technology_survives_bill_lock_removal(self):
  law=build()['in_game/common/laws/tsin_environment_laws.txt']
  policies=law_policies(next(b.text for b in pdx.top_level_blocks(law) if b.key=='tsin_environment_law'))
  strict=next(allow for key,pot,allow in policies if key=='tsin_environment_standards_policy')
  self.assertIn('has_advance = tsin_modern_sewerage_advance',strict)
  self.assertNotIn('tsin_policy_enactable_trigger',strict)
  for key,pot,allow in policies:self.assertIn(key,pdx.read_text(pdx.MOD_ROOT/'in_game/events/tsin_legislation_bills.txt'))
 def test_changed_ownership_cannot_receive_funded_response(self):
  s=build()['in_game/events/tsin_environment.txt']
  self.assertGreaterEqual(s.count('owner ?= root controller ?= root'),2)
  air=pollution()['in_game/events/tsin_pollution.txt']
  self.assertGreaterEqual(air.count('owner ?= root controller ?= root'),2)
if __name__=='__main__':unittest.main()
