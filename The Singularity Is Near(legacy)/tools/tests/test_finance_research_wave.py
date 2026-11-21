import sys,json,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_dashboard import build as dashboard

class FinanceOverviewCapacityTests(unittest.TestCase):
 def setUp(self):
  self.gui=pdx.read_text(pdx.MOD_ROOT/'in_game/gui/tsin_finance.gui')
  self.loc=pdx.read_text(pdx.MOD_ROOT/'main_menu/localization/korean/tsin_finance_l_korean.yml')

 def test_borrowing_capacity_is_reported_as_no_data_not_income(self):
  self.assertIn('text = "TSIN_FINANCE_CAPACITY_NA"',self.gui)
  self.assertIn('TSIN_FINANCE_CAPACITY:',self.loc)
  # The capacity row must not be fed from annual or monthly income figures.
  capacity_line=[l for l in self.gui.splitlines() if 'TSIN_FINANCE_CAPACITY_NA' in l][0]
  self.assertNotIn('tax_trade',capacity_line)
  self.assertNotIn('GetVariable',capacity_line)

 def test_treasury_row_is_cash_and_separate_from_capacity(self):
  self.assertIn('국고 현금 · 두캇',self.loc)
  self.assertIn('TSIN_FINANCE_CAPACITY_NOTE',self.gui)
  self.assertIn('준비금·은행·연금·GDP는 국고 현금에 더하지 않습니다',self.loc)

class ResearchExplanationTests(unittest.TestCase):
 def test_research_help_describes_existing_multipliers_only(self):
  d=json.loads(pdx.read_text(pdx.MOD_ROOT/'ui/dashboard_registry.json'))
  loc=dashboard(d)['main_menu/localization/korean/tsin_dashboard_l_korean.yml']
  help_line=[l for l in loc.splitlines() if 'RESEARCH_HELP' in l][0]
  for needle in ('2·5·9·15%','자유 언론 ×1.2','국가 언론 ×0.5','검열 ×0.75','최대 18%','새 연구 슬롯'):
   self.assertIn(needle,help_line)

 def test_education_source_year_is_shown_on_research_tab(self):
  d=json.loads(pdx.read_text(pdx.MOD_ROOT/'ui/dashboard_registry.json'))
  metric=[m for m in next(x for x in d['modules'] if x['id']=='social_bases')['metrics'] if m['id']=='social_education_year'][0]
  self.assertIn('research',metric['tabs'])

if __name__=='__main__':unittest.main()
