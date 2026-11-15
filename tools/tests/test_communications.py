import sys,unittest
from pathlib import Path
from decimal import Decimal as D
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_communications import build,transform_aggregate,registry_module
from gen_dashboard import build as dashboard
from test_finance_ledger import LedgerFixture
from test_capital_markets import parse,get
class CommunicationsTests(unittest.TestCase):
 def test_fractional_staffing_and_real_upkeep(self):
  files=build();s=files['in_game/common/script_values/tsin_communications.txt']
  self.assertEqual(s.count('controller ?= owner'),2)
  self.assertEqual(s.count('is_opened = yes is_lacking_goods = no'),2)
  blocks={b.key:parse(b.text[b.text.index('{')+1:-1]) for b in pdx.top_level_blocks(s)}
  f=LedgerFixture();f.state.update(building_employed_amount=D(25),building_employment_size_amount=D(50))
  for name in ('telegraph','telephone'):
   loop=get(get(blocks['tsin_'+name+'_staff_scale'],'if'),'every_buildings_in_location')
   self.assertEqual(f.num(get(loop,'add')),D('0.5'))
  buildings=files['in_game/common/building_types/tsin_communications.txt']
  self.assertIn('tsin_electricity = 0.05',buildings);self.assertIn('employment_size = 0.02',buildings)
  self.assertNotIn('produced =',buildings)
 def test_whole_population_denominator_caps_and_unknown(self):
  f=LedgerFixture();s=build()['in_game/common/scripted_effects/tsin_communications.txt']
  f.effects.update({b.key:parse(b.text[b.text.index('{')+1:-1]) for b in pdx.top_level_blocks(s)})
  original=f.valid
  f.valid=lambda rows:all(True if k=='has_advance' else original([(k,op,v)]) for k,op,v in rows)
  f.state.update(total_population=D(100),tsin_telegraph_weighted_pop=D(25),tsin_telephone_weighted_pop=D(200),current_year=D(1890))
  f.run(f.effects['tsin_communications_finish_country_effect'])
  self.assertEqual(f.state['tsin_telegraph_coverage'],D(25));self.assertEqual(f.state['tsin_telephone_coverage'],D(100))
  f.state['total_population']=D(0);f.run(f.effects['tsin_communications_finish_country_effect'])
  self.assertNotIn('tsin_telegraph_coverage',f.state)
 def test_actual_annual_hook_and_ui_without_extra_world_scan(self):
  s=pdx.read_text(pdx.MOD_ROOT/'in_game/common/scripted_effects/tsin_aggregate_effects.txt')
  self.assertEqual(transform_aggregate(s),s);self.assertEqual(s.count('every_owned_location ='),1)
  self.assertEqual(s.count('tsin_communications_location_effect = yes'),1)
  import json
  data=json.loads(pdx.read_text(pdx.MOD_ROOT/'ui/dashboard_registry.json'));out=dashboard(data)
  self.assertIn('tsin_communications_finish_country_effect = yes',out['in_game/common/scripted_effects/tsin_dashboard_core_effects.txt'])
  self.assertIn('communications_telegraph',str(data));self.assertNotIn('every_country',str(build()))
if __name__=='__main__':unittest.main()
