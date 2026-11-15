import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_city_expansion import scalar_fields,permission_metadata,permission_patch,RANK_TRIGGERS
from gen_urban_projects import build as projects
from gen_metropolitan_regions import build as metros
class CityPermissionTests(unittest.TestCase):
 def test_inline_fields_are_read_but_nested_and_quoted_fields_are_not(self):
  f=scalar_fields('x = { category = infrastructure town = yes city = yes megalopolis = yes potential = { city = no } note = "city = no" }')
  self.assertEqual(f['city'],'yes');self.assertEqual(f['megalopolis'],'yes')
  self.assertNotIn('city',scalar_fields('x = { potential = { city = yes } note = "city = yes" }'))
  source=pdx.read_text(pdx.MOD_ROOT/'in_game/common/building_types/tsin_age8_transport_buildings.txt')
  patch=permission_patch(permission_metadata([source]))
  self.assertIn('TRY_INJECT:tsin_motor_transport_depot = { tsin_large_city = yes tsin_megalopolis = yes }',patch)
 def test_injections_inheritance_and_explicit_new_rank_restrictions_survive(self):
  flags=permission_metadata(['base = { city = yes megalopolis = no } child = { copy_from = "base" }','TRY_INJECT:child = { city = no }','x = { city = yes tsin_large_city = no }'])
  patch=permission_patch(flags)
  self.assertIn('TRY_INJECT:child = { tsin_large_city = no tsin_megalopolis = no }',patch)
  self.assertNotIn('TRY_INJECT:x',patch)
  self.assertEqual(permission_patch(permission_metadata(['x = { }'])), '# Generated rank permissions only; no third-party building definitions are copied.\n')
 def test_our_project_and_hub_conditions_include_all_new_city_ranks(self):
  self.assertIn('tsin_is_city_location =',RANK_TRIGGERS)
  self.assertIn('tsin_is_city_or_large_city = yes',RANK_TRIGGERS)
  self.assertIn('tsin_is_metropolis_or_megalopolis = yes',RANK_TRIGGERS)
  self.assertIn('tsin_is_urban_location = yes',projects()['in_game/common/generic_actions/tsin_urban_projects.txt'])
  self.assertIn('tsin_is_city_location = yes',metros()['in_game/common/generic_actions/tsin_metropolitan_regions.txt'])
if __name__=='__main__':unittest.main()
