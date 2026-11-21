import sys,unittest,json
from pathlib import Path
from decimal import Decimal as D
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_social_bases import build,transform_survey
from gen_manual_statistics import build as survey
from test_capital_markets import parse
from test_finance_contracts import ContractFixture
class SocialBaseTests(unittest.TestCase):
 def fixture(self):
  f=ContractFixture()
  for rel,s in build().items():
   blocks={b.key:parse(b.text[b.text.index('{')+1:-1]) for b in pdx.top_level_blocks(s)}
   if '/script_values/' in rel:f.values.update(blocks)
   else:f.effects.update(blocks)
  return f
 def test_known_sources_are_bounded_nonexclusive_and_never_move_assets(self):
  f=self.fixture();c=f.country(total_population=D(100),tsin_social_burghers=D(20),tsin_social_factory_jobs=D(30),tsin_secondary_education=D(50),tsin_higher_education=D(10),tsin_public_shares=D(25),tsin_issued_shares=D(100),tsin_statistics_year=D(1849),gold=D(300),tsin_firm_cash=D(100))
  f.effect('tsin_social_bases_finish_effect',c)
  for key,expected in [('capital','.15'),('workers','.30'),('intellectual','.10'),('clerical','.10'),('technical','.03')]:self.assertEqual(c['tsin_social_'+key],D(expected))
  self.assertEqual(c['gold'],D(300));self.assertEqual(c['tsin_firm_cash'],D(100));self.assertEqual(c['tsin_social_education_year'],D(1849))
 def test_unknown_and_zero_population_clear_old_results(self):
  f=self.fixture();c=f.country(total_population=D(100),tsin_social_burghers=D(20),tsin_social_factory_jobs=D(30))
  f.effect('tsin_social_bases_finish_effect',c)
  for key in ('capital','intellectual','clerical','technical','education_year'):self.assertNotIn('tsin_social_'+key,c)
  c['total_population']=D(0);f.effect('tsin_social_bases_finish_effect',c);self.assertNotIn('tsin_social_workers',c)
 def test_only_manual_request_reuses_one_existing_location_pass(self):
  s=survey()['in_game/common/scripted_effects/tsin_manual_surveys.txt']
  self.assertEqual(transform_survey(s),s);self.assertEqual(s.count('tsin_social_bases_finish_effect = yes'),1)
  self.assertEqual(s.count('every_owned_location ='),1);self.assertEqual(s.count('every_country ='),1)
  for p in (pdx.MOD_ROOT/'in_game/common/on_action').glob('*.txt'):self.assertNotIn('tsin_social_',pdx.read_text(p))
  d=json.loads(pdx.read_text(pdx.MOD_ROOT/'ui/dashboard_registry.json'));module=next(m for m in d['modules'] if m['id']=='social_bases')
  self.assertNotIn('annual_effect',module)
  for m in module['metrics']:self.assertEqual(m['frequency'],'manual')
if __name__=='__main__':unittest.main()
