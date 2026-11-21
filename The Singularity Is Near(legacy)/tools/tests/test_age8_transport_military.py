from pathlib import Path
import json,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx,era_layout
from gen_age8_transport_military import build,assets
from test_capital_markets import parse,get


class AgeEightTransportMilitaryTests(unittest.TestCase):
    def setUp(self):self.files=build()

    def test_six_advances_extend_existing_research_with_confirmed_institutions(self):
        text=self.files['in_game/common/advances/zz_tsin_08_transport_military.txt']
        blocks=pdx.top_level_blocks(text)
        self.assertEqual(len(blocks),6)
        existing={b.key for p in (pdx.MOD_ROOT/'era_7/in_game/common/advances').glob('*.txt') for b in pdx.top_level_blocks(pdx.read_text(p))}
        seen=set(existing)
        for block in blocks:
            body=parse(block.text[block.text.index('{')+1:-1])
            self.assertEqual(get(body,'age'),'age_8_world_wars')
            parents=[v for k,_,v in body if k=='requires']
            self.assertTrue(parents)
            self.assertTrue(all(v in seen for v in parents),(block.key,parents))
            self.assertIn('institution:tsin_',block.text)
            seen.add(block.key)
        self.assertNotIn('in_game/common/institution/',str(self.files.keys()))

    def test_battleship_variants_have_distinct_real_fuel_demands(self):
        units=self.files['in_game/common/unit_types/zz_tsin_08_capital_ships.txt']
        blocks={b.key:parse(b.text[b.text.index('{')+1:-1]) for b in pdx.top_level_blocks(units)}
        coal=blocks['n_tsin_dreadnought'];oil=blocks['n_tsin_oil_fired_dreadnought']
        self.assertEqual(get(coal,'copy_from'),'n_tsin_pre_dreadnought')
        self.assertEqual(get(oil,'copy_from'),'n_tsin_pre_dreadnought')
        for unit in [coal,oil]:self.assertEqual(get(unit,'age'),'age_8_world_wars')
        # Values are increments under the engine copy_from rules.
        self.assertEqual(float(get(coal,'hull_size')),20)
        self.assertEqual(float(get(oil,'hull_size')),30)
        self.assertLessEqual(float(get(oil,'cannons')),25)
        self.assertGreater(float(get(oil,'movement_speed')),float(get(coal,'movement_speed')))
        demands={b.key:parse(b.text[b.text.index('{')+1:-1]) for b in pdx.top_level_blocks(self.files['in_game/common/goods_demand/tsin_age8_capital_ship_demands.txt'])}
        for unit in [coal,oil]:
            for field in ['construction_demand','maintenance_demand','repair_demand']:self.assertIn(get(unit,field),demands)
        self.assertGreater(float(get(demands[get(oil,'maintenance_demand')],'tsin_oil')),0)
        self.assertFalse(any(k=='tsin_oil' for k,_,v in demands[get(coal,'maintenance_demand')]))

    def test_single_capital_airfield_is_ground_support_with_paid_inputs(self):
        text=self.files['in_game/common/building_types/tsin_age8_transport_buildings.txt']
        blocks={b.key:b.text for b in pdx.top_level_blocks(text)}
        airfield=blocks['tsin_capital_airfield']
        self.assertIn('potential = { is_capital = yes }',airfield)
        self.assertIn('max_levels = 1',airfield)
        self.assertIn('capital_country_modifier',airfield)
        for building in blocks.values():
            self.assertIn('construction_demand = tsin_factory_construction',building)
            self.assertIn('category = building_maintenance',building)
            self.assertIn('tsin_oil = ',building);self.assertIn('tsin_rubber = ',building)
        self.assertNotIn('air_unit',str(self.files))
        for action in ['destroy_army','destroy_unit','disband','remove_advance','every_country']:
            self.assertNotIn(action,str(self.files))

    def test_all_sources_assets_and_runtime_mirrors_are_connected(self):
        outputs={**self.files,**assets()}
        manifest=json.loads((pdx.MOD_ROOT/'era_8/manifest.json').read_text())['files']
        for rel,value in outputs.items():
            self.assertIn(rel,manifest)
            source,runtime,_=era_layout.entries()[rel]
            self.assertEqual(source,pdx.MOD_ROOT/'era_8'/rel)
            self.assertEqual(source.read_bytes(),runtime.read_bytes())
        self.assertEqual(len(assets()),2)


if __name__=='__main__':unittest.main()
