"""Manual estimates for five modern social bases, without new POPs or wealth duplication."""
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx
GROUPS=[('capital','기업·민간 소유 연계 기반','Business/private-ownership base'),('workers','공장 고용 연계 기반','Factory-employment base'),('intellectual','고등교육 연계 기반','Higher-education base'),('clerical','중등교육 시민 연계 기반','Secondary-educated burgher base'),('technical','고등교육·산업 연계 기반','Higher-education/industry base')]
def registry_module():
 return {'id':'social_bases','shortcuts':[{'id':'social_bases_survey','tab':'society','title':{'korean':'사회 구성 기반 조사','english':'Survey social bases'},'generic_action':'tsin_survey_domestic'}], 'metrics':[
 {'id':'social_'+key,'variable':'tsin_social_'+key,'title':{'korean':ko,'english':en},'tabs':['society'],'unit':'fraction','frequency':'manual','description':{'korean':'국내 통계 조사 버튼으로만 계산하는 서로 겹칠 수 있는 사회 기반 지표입니다. 실제 계급 인구·정치 영향력·합이100%인 구성비가 아닙니다. 기업=시민 비중×민간 지분비(장부 필요), 노동=공장 일자리/인구, 지식=고등교육률, 사무=시민 비중×중등교육률, 기술=공장 비중×고등교육률. 교육·지분은 기존 장부의 마지막 값이며 국고·인구·자산을 옮기지 않습니다.','english':'Explicit domestic-survey estimates, which may overlap. Not actual class populations, political power or shares summing to 100%. Business=burgher share × private ownership (ledger required); workers=factory jobs/population; intellectual=higher education; clerical=burgher share × secondary education; technical=factory share × higher education. Education/equity retain their source ledger dates. No population, wealth or treasury transfers.'}}
 for key,ko,en in GROUPS]+[{'id':'social_survey_year','variable':'tsin_social_year','title':{'korean':'사회 기반 조사 연도','english':'Social-base survey year'},'tabs':['society'],'unit':'number','frequency':'manual','description':{'korean':'마지막으로 국내 통계 조사를 요청한 연도입니다.','english':'Year of the last explicit domestic survey.'}},{'id':'social_education_year','variable':'tsin_social_education_year','title':{'korean':'사용한 교육 원자료 연도','english':'Education source year used'},'tabs':['society'],'unit':'number','frequency':'manual','description':{'korean':'교육 캐시의 원자료 기준 연도입니다. 조사 연도와 다를 수 있으며 미상이면 —입니다.','english':'Source year of cached education, possibly different from the survey year. Unknown is shown as —.'}}]}

def transform_survey(s):
 if 'tsin_social_bases_finish_effect = yes' in s:return s
 b=next(b for b in pdx.top_level_blocks(s) if b.key=='tsin_survey_domestic_effect')
 text=b.text.replace('save_scope_as = tsin_survey_requestor','save_scope_as = tsin_survey_requestor\n set_variable = { name = tsin_social_burghers value = 0 }\n set_variable = { name = tsin_social_factory_jobs value = 0 }',1)
 text=text.replace(' every_owned_location = {',''' every_owned_location = {
  save_temporary_scope_value_as = { name = tsin_social_burghers_here value = num_pop_type:burghers }
  save_temporary_scope_value_as = { name = tsin_social_factory_jobs_here value = tsin_location_industrial_jobs }
  scope:tsin_survey_requestor = {
   change_variable = { name = tsin_social_burghers add = scope:tsin_social_burghers_here }
   change_variable = { name = tsin_social_factory_jobs add = scope:tsin_social_factory_jobs_here }
  }''',1)
 text=text[:-1]+' tsin_social_bases_finish_effect = yes\n}'
 return s[:b.start]+text+s[b.end:]

def build():
 values='''tsin_social_burgher_share = { value = var:tsin_social_burghers divide = total_population min = 0 max = 1 }
tsin_social_factory_share = { value = var:tsin_social_factory_jobs divide = total_population min = 0 max = 1 }
tsin_social_private_share = { value = 1 subtract = { value = var:tsin_public_shares divide = var:tsin_issued_shares } min = 0 max = 1 }
'''
 fx='''tsin_social_bases_finish_effect = {
 remove_variable = tsin_social_capital remove_variable = tsin_social_workers
 remove_variable = tsin_social_intellectual remove_variable = tsin_social_clerical remove_variable = tsin_social_technical
 remove_variable = tsin_social_education_year
 set_variable = { name = tsin_social_year value = current_year }
 if = { limit = { total_population > 0 }
  set_variable = { name = tsin_social_workers value = tsin_social_factory_share }
  if = { limit = { tsin_company_count = 0 } set_variable = { name = tsin_social_capital value = 0 } }
  else_if = { limit = { has_variable = tsin_ledger_version var:tsin_issued_shares > 0 }
   set_variable = { name = tsin_social_capital value = { value = tsin_social_burgher_share multiply = tsin_social_private_share } }
  }
  if = { limit = { has_variable = tsin_higher_education }
   set_variable = { name = tsin_social_intellectual value = { value = var:tsin_higher_education divide = 100 min = 0 max = 1 } }
   set_variable = { name = tsin_social_technical value = { value = tsin_social_factory_share multiply = var:tsin_social_intellectual } }
  }
  if = { limit = { has_variable = tsin_secondary_education }
   set_variable = { name = tsin_social_clerical value = { value = var:tsin_secondary_education divide = 100 min = 0 max = 1 multiply = tsin_social_burgher_share } }
  }
  if = { limit = { has_variable = tsin_statistics_year OR = { has_variable = tsin_secondary_education has_variable = tsin_higher_education } }
   set_variable = { name = tsin_social_education_year value = var:tsin_statistics_year }
  }
 }
}
'''
 return {'in_game/common/script_values/tsin_social_bases.txt':values,'in_game/common/scripted_effects/tsin_social_bases.txt':fx}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();bad=[]
 for rel,text in build().items():
  p=pdx.MOD_ROOT/rel
  if a.check:
   if not p.exists() or pdx.read_text(p)!=text:bad.append(rel)
  else:pdx.write_text_bom(p,text)
 if not a.check:
  p=pdx.MOD_ROOT/'tools/gen_manual_statistics.py';s=p.read_text(encoding='utf-8')
  if 'from gen_social_bases import transform_survey' not in s:
   s=s.replace('    outputs={','    from gen_social_bases import transform_survey\n    effects=transform_survey(effects)\n    outputs={',1);p.write_text(s,encoding='utf-8')
  p=pdx.MOD_ROOT/'ui/dashboard_registry.json';d=json.loads(pdx.read_text(p));d['modules']=[m for m in d['modules'] if m['id']!='social_bases']+[registry_module()];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Social bases:',len(bad),'differences');return bool(bad)
if __name__=='__main__':raise SystemExit(main())
