"""Only explicit native actions request reports. No annual/monthly report hook."""
from pathlib import Path
import argparse,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx

FIELDS=[
 ('year','조사 연도','Survey year','number'),('month','조사 월','Survey month','number'),
 ('population','국내 조사 인구','Surveyed population','compact'),
 ('locations','국내 조사 지점','Surveyed locations','number'),
 ('urban','국내 시가화 지점','Surveyed urban locations','number'),
 ('buildings','국내 건물 레벨 합계','Surveyed building levels','number'),
 ('companies','국내 기업 수','Surveyed firms','number'),
 ('gdp','국내 추정 GDP 원자료','Reported estimated GDP','compact'),
 ('world_year','세계 조사 연도','World survey year','number'),
 ('world_month','세계 조사 월','World survey month','number'),
 ('world_countries','세계 조사 국가 수','Countries surveyed','number'),
 ('world_population','세계 조사 인구','Surveyed world population','compact'),
 ('world_companies','세계 기업 수 합계','Surveyed world firms','number'),
 ('world_known_gdp','GDP 자료 보유국 수','Countries with GDP data','number'),
 ('world_gdp','자료 보유국 추정 GDP 합계','Available estimated GDP total','compact')]

def registry_module():
    return {'id':'manual_surveys','metrics':[
       {'id':'report_'+key,'variable':'tsin_report_'+key,'title':{'korean':ko,'english':en},
        'tabs':['overview'],'unit':unit,'frequency':'manual',
        'description':{'korean':'조사 버튼을 누른 시점의 보고서입니다. GDP·기업 원자료는 기존 장부의 마지막 계산값이며 보고서 기준일과 다를 수 있습니다.',
         'english':'Snapshot requested by the survey button. GDP and firm sources retain their existing ledger update dates.'}}
       for key,ko,en,unit in FIELDS],
       'shortcuts':[{'id':'survey_'+kind,'tab':'overview','title':{'korean':ko,'english':en},'generic_action':'tsin_survey_'+kind}
        for kind,ko,en in [('domestic','국내 통계 조사','Survey domestic statistics'),('world','세계 통계 조사','Survey world statistics')]]}

def build():
    actions=[]
    for kind in ['domestic','world']:
        actions.append(f'''tsin_survey_{kind} = {{
 type = owncountry
 show_message = no
 ai_tick = never
 automation_tick = never
 price = price:tsin_survey_price
 effect = {{ scope:actor = {{ tsin_survey_{kind}_effect = yes }} }}
}}''')
    effects='''tsin_survey_domestic_effect = {
 save_scope_as = tsin_survey_requestor
 set_variable = { name = tsin_report_year value = current_year }
 set_variable = { name = tsin_report_month value = current_month }
 set_variable = { name = tsin_report_population value = { value = total_population multiply = 1000 } }
 set_variable = { name = tsin_report_companies value = tsin_company_count }
 remove_variable = tsin_report_gdp
 if = { limit = { has_variable = tsin_gdp } set_variable = { name = tsin_report_gdp value = var:tsin_gdp } }
 set_variable = { name = tsin_report_locations value = 0 }
 set_variable = { name = tsin_report_urban value = 0 }
 set_variable = { name = tsin_report_buildings value = 0 }
 every_owned_location = {
  save_temporary_scope_value_as = { name = tsin_survey_buildings value = total_building_levels }
  scope:tsin_survey_requestor = {
   change_variable = { name = tsin_report_locations add = 1 }
   change_variable = { name = tsin_report_buildings add = scope:tsin_survey_buildings }
  }
  if = { limit = { NOT = { location_rank ?= location_rank:rural_settlement } }
   scope:tsin_survey_requestor = { change_variable = { name = tsin_report_urban add = 1 } }
  }
 }
}
tsin_survey_world_effect = {
 save_scope_as = tsin_survey_requestor
 set_variable = { name = tsin_report_world_year value = current_year }
 set_variable = { name = tsin_report_world_month value = current_month }
 set_variable = { name = tsin_report_world_countries value = 0 }
 set_variable = { name = tsin_report_world_population value = 0 }
 set_variable = { name = tsin_report_world_companies value = 0 }
 set_variable = { name = tsin_report_world_known_gdp value = 0 }
 set_variable = { name = tsin_report_world_gdp value = 0 }
 every_country = {
  limit = { is_real_country = yes exists = capital }
  save_temporary_scope_value_as = { name = tsin_survey_population value = { value = total_population multiply = 1000 } }
  save_temporary_scope_value_as = { name = tsin_survey_companies value = tsin_company_count }
  scope:tsin_survey_requestor = {
   change_variable = { name = tsin_report_world_countries add = 1 }
   change_variable = { name = tsin_report_world_population add = scope:tsin_survey_population }
   change_variable = { name = tsin_report_world_companies add = scope:tsin_survey_companies }
  }
  if = { limit = { has_variable = tsin_gdp }
   save_temporary_scope_value_as = { name = tsin_survey_gdp value = var:tsin_gdp }
   scope:tsin_survey_requestor = {
    change_variable = { name = tsin_report_world_known_gdp add = 1 }
    change_variable = { name = tsin_report_world_gdp add = scope:tsin_survey_gdp }
   }
  }
 }
}
'''
    outputs={'in_game/common/generic_actions/tsin_manual_surveys.txt':'\n'.join(actions)+'\n',
      'in_game/common/prices/tsin_manual_surveys.txt':'tsin_survey_price = { gold = 0 }\n',
      'in_game/common/scripted_effects/tsin_manual_surveys.txt':effects}
    for lang in ['english','korean']:
        rows=[]
        for kind,ko,en in [('domestic','국내 통계 조사','Survey domestic statistics'),('world','세계 통계 조사','Survey world statistics')]:
            title=ko if lang=='korean' else en
            desc='지금 한 번 집계하여 TSIN 국가 통계의 보고서를 갱신합니다. 이후 자동 재계산하지 않습니다.' if lang=='korean' else 'Request one snapshot in TSIN national statistics. No automatic recalculation follows.'
            rows.extend([f' tsin_survey_{kind}: "{title}"',f' tsin_survey_{kind}_desc: "{desc}"'])
        outputs[f'main_menu/localization/{lang}/tsin_manual_surveys_l_{lang}.yml']='l_'+lang+':\n'+'\n'.join(rows)+'\n'
    return outputs

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args();failures=[]
    for rel,text in build().items():
        p=pdx.MOD_ROOT/rel
        if args.check:
            if not p.exists() or pdx.read_text(p)!=text:failures.append(rel)
        else:pdx.write_text_bom(p,text)
    print('Manual statistics:',len(failures),'differences')
    return bool(failures)
if __name__=='__main__':raise SystemExit(main())
