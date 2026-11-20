import sys,unittest,json
from pathlib import Path
from decimal import Decimal as D
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_transport_services import build,ROWS,key
from test_capital_markets import parse,get
from test_finance_ledger import LedgerFixture
class TransportServiceTests(unittest.TestCase):
 def test_preserves_native_lines_and_cargo_during_passenger_upgrade(self):
  b=build();self.assertFalse(any('/road_types/' in p for p in b))
  buildings='\n'.join(s for p,s in b.items() if '/building_types/' in p)
  blocks={x.key:x.text for x in pdx.top_level_blocks(buildings)}
  self.assertNotIn('obsolete = tsin_railway_station',buildings)
  self.assertNotIn('remove_if',buildings)
  self.assertIn('obsolete = tsin_double_track_services',blocks['tsin_heavy_freight_services'])
  self.assertNotIn('obsolete',blocks['tsin_high_speed_services'])
  self.assertIn('obsolete = tsin_high_speed_services',blocks['tsin_modern_rail_services'])
  self.assertNotIn('obsolete = tsin_heavy_freight_services',buildings)
  self.assertIn('tsin_oil = 0.08 tsin_electricity = 0.15',buildings)
 def test_operating_partial_staffing_and_no_rgo_bonus(self):
  b=build();s=b['in_game/common/script_values/tsin_transport_services.txt']
  blocks={x.key:parse(x.text[x.text.index('{')+1:-1]) for x in pdx.top_level_blocks(s)}
  f=LedgerFixture();f.state.update(building_employed_amount=D(25),building_employment_size_amount=D(100),building_level=D(2))
  for row in ROWS:
   k=key(row[0]);loop=get(blocks[k+'_staff_scale'],'every_buildings_in_location')
   self.assertIn(('is_opened','=','yes'),get(loop,'limit'));self.assertIn(('is_lacking_goods','=','no'),get(loop,'limit'))
   self.assertEqual(f.num(get(loop,'add')),D('0.50') if row[5]=='metro' else D('0.25'))
  auto=b['in_game/common/auto_modifiers/tsin_transport_services.txt']
  self.assertEqual(auto.count('controller ?= owner'),len(ROWS))
  self.assertIn('has_road_of_type_to',auto);self.assertNotIn('raw_material',auto)
 def test_road_tiers_are_exclusive_but_independent_of_rail(self):
  buildings='\n'.join(s for p,s in build().items() if '/building_types/' in p)
  road=next(b.text for b in pdx.top_level_blocks(buildings) if b.key=='tsin_macadam_services')
  for name in ('tarmac','asphalt','modern_road'):self.assertIn('NOT = { has_building_with_at_least_one_level = '+key(name)+' }',road)
  self.assertNotIn('NOT = { has_building_with_at_least_one_level = tsin_heavy_freight_services',road)
 def test_mature_metro_allows_later_levels_after_electric_metro_obsolete(self):
  buildings='\n'.join(s for p,s in build().items() if '/building_types/' in p)
  block=next(b.text for b in pdx.top_level_blocks(buildings) if b.key==key('mature_metro'))
  self.assertIn('has_building_with_at_least_one_level = tsin_electric_metro',block)
  self.assertIn('has_building_with_at_least_one_level = '+key('mature_metro'),block)
  self.assertIn('OR = {',block)
 def test_future_sources_and_actual_build_entry(self):
  b=build()
  for era in (7,8,9,10):
   manifest=json.loads((pdx.MOD_ROOT/f'era_{era}/manifest.json').read_text(encoding='utf-8-sig'))
   for rel in [f'in_game/common/advances/zz_tsin_transport_services_{era:02d}.txt',f'in_game/common/building_types/zz_tsin_transport_services_{era:02d}.txt']:
    self.assertIn(rel,manifest['files']);self.assertEqual(pdx.read_text(pdx.MOD_ROOT/rel),b[rel])
  gui=pdx.read_text(pdx.MOD_ROOT/'in_game/gui/tsin_dashboard.gui')
  self.assertIn('TSIN_UI_LINK_TRANSPORT_BUILDINGS',gui);self.assertIn("OpenLateralView('buildings')",gui)
if __name__=='__main__':unittest.main()
