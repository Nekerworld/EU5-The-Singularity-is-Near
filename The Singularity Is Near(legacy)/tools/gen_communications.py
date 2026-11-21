"""Operating telegraph/telephone hubs; one existing annual urban survey, no routing graph."""
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx

def registry_module():
 return {'id':'communications','annual_effect':'tsin_communications_finish_country_effect','metrics':[
  {'id':'communications_'+key,'variable':'tsin_'+key+'_coverage','title':{'korean':kr+' 설비 노출','english':en+' equipment exposure'},'tabs':['research','society'],'unit':'percent_points','frequency':'annual',
   'description':{'korean':'연간 도시 조사에서 정상 가동·실제 고용 비율로 가중한 지점 인구 / 국가 전체 인구입니다. 가입자 수나 모든 농촌·전국 배선 연결률이 아닙니다. 점령·휴업·투입 부족은 제외하며 원격 POP을 이동시키지 않습니다.','english':'Population in annually surveyed urban locations weighted by operating, staffed equipment / total national population. Not subscribers, rural coverage or wired connectivity. Occupied, closed or input-starved sites do not count; no POP relocation.'}}
  for key,kr,en in [('telegraph','전신','Telegraph'),('telephone','전화','Telephone')]]}

def transform_aggregate(s):
 if 'tsin_communications_location_effect = yes' in s:return s
 s=s.replace('tsin_annual_country_aggregate_effect = {','tsin_annual_country_aggregate_effect = {\n set_variable = { name = tsin_telegraph_weighted_pop value = 0 }\n set_variable = { name = tsin_telephone_weighted_pop value = 0 }',1)
 s=s.replace('set_local_variable = { name = tsin_agg_l_pop value = population }','tsin_communications_location_effect = yes\n\t\tset_local_variable = { name = tsin_agg_l_pop value = population }',1)
 return s

def build():
 labels={};buildings=[];values=[];effects=['tsin_communications_location_effect = {'];custom=[]
 for name,ko,en,staff,inputs in [('telegraph','전신국','Telegraph office','0.02','copper = 0.03 paper = 0.03 tools = 0.01'),('telephone','전화 교환국','Telephone exchange','0.05','copper = 0.05 tools = 0.02 tsin_electricity = 0.05')]:
  key='tsin_'+name+'_office'
  gate='has_advance = tsin_telegraph_telephone_advance'+(' has_advance = tsin_electric_motor_advance' if name=='telephone' else '')
  buildings.append(f'''{key} = {{
 audio_tier = 2 is_foreign = no forbidden_for_estates = yes
 pop_type = burghers employment_size = {staff} max_levels = 1 category = infrastructure_category
 town = yes city = yes megalopolis = yes tsin_large_city = yes tsin_megalopolis = yes
 build_time = infrastructure_build_time construction_demand = tsin_infrastructure_construction
 country_potential = {{ {gate} }}
 ai_construct_weight = {{ value = 0 if = {{ limit = {{ population >= 100 owner ?= {{ gold >= 500 }} }} add = 20 }} }}
 unique_production_methods = {{
  {key}_maintenance = {{
   icon_type = goods icon = copper
   {inputs} category = building_maintenance
  }}
 }}
}}''')
  values.append(f'''tsin_{name}_staff_scale = {{
 value = 0
 if = {{ limit = {{ controller ?= owner }}
  every_buildings_in_location = {{
   limit = {{ building_type = building_type:{key} is_opened = yes is_lacking_goods = no building_employment_size_amount > 0 }}
   add = {{ value = building_employed_amount divide = building_employment_size_amount }}
  }}
 }}
 min = 0 max = 1
}}''')
  effects.append(f'''set_local_variable = {{ name = tsin_{name}_weighted_here value = {{ value = tsin_{name}_staff_scale multiply = population }} }}
 owner = {{ change_variable = {{ name = tsin_{name}_weighted_pop add = local_var:tsin_{name}_weighted_here }} }}''')
  labels[key]=(ko,en);labels[key+'_maintenance']=(ko+' 운영',en+' operation')
  labels[key+'_desc']=(ko+'은 해당 지점의 설비 노출 지수를 실제 고용/정원 비율로 높입니다. 전국 배선·가입자·즉시 정보 전송을 뜻하지 않으며 휴업·투입 부족·적국 점령 시 집계하지 않습니다. 전신과 전화는 서로 보완하는 별도 시설입니다.',en+' raises the local equipment exposure index according to effective staffing. This is not a national wiring or subscriber count. Closed, input-starved or enemy-controlled sites do not count. Telegraph and telephone hubs coexist as complementary services.')
 effects.append('}')
 effects.append('''tsin_communications_finish_country_effect = {
 if = { limit = { has_advance = tsin_telegraph_telephone_advance total_population > 0 }
  set_variable = { name = tsin_telegraph_coverage value = { value = var:tsin_telegraph_weighted_pop divide = total_population multiply = 100 min = 0 max = 100 } }
  set_variable = { name = tsin_telephone_coverage value = { value = var:tsin_telephone_weighted_pop divide = total_population multiply = 100 min = 0 max = 100 } }
  set_variable = { name = tsin_communications_year value = current_year }
 } else = { remove_variable = tsin_telegraph_coverage remove_variable = tsin_telephone_coverage remove_variable = tsin_communications_year }
}
''')
 values.append('''tsin_communications_research_scale = {
 value = var:tsin_telegraph_coverage add = var:tsin_telephone_coverage divide = 200 min = 0 max = 1
}
''')
 auto='''tsin_communications_research = {
 potential_trigger = { has_variable = tsin_communications_year }
 scales_with = tsin_communications_research_scale research_speed_modifier = 0.05
}
'''
 labels['AUTO_MODIFIER_NAME_tsin_communications_research']=('전신·전화 정보 교류','Telegraph and telephone information exchange')
 out={'in_game/common/building_types/tsin_communications.txt':'\n'.join(buildings),'in_game/common/script_values/tsin_communications.txt':'\n'.join(values),'in_game/common/scripted_effects/tsin_communications.txt':'\n'.join(effects),'in_game/common/auto_modifiers/tsin_communications.txt':auto}
 for lang,i in [('korean',0),('english',1)]:out[f'main_menu/localization/{lang}/tsin_communications_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {key}: '+json.dumps(v[i],ensure_ascii=False)+'\n' for key,v in labels.items())
 return {k:v.rstrip()+'\n' for k,v in out.items()}

def integrate():
 p=pdx.MOD_ROOT/'in_game/common/scripted_effects/tsin_aggregate_effects.txt';pdx.write_text_bom(p,transform_aggregate(pdx.read_text(p)))
 p=pdx.MOD_ROOT/'in_game/common/advances/tsin_06_electrification.txt';s=pdx.read_text(p)
 for advance,key in [('tsin_telegraph_telephone_advance','tsin_telegraph_office'),('tsin_electric_motor_advance','tsin_telephone_office')]:
  line='unlock_building = '+key
  if line not in s:
   b=next(b for b in pdx.top_level_blocks(s) if b.key==advance);s=s[:b.start]+b.text.replace('{','{\n\t'+line,1)+s[b.end:]
 pdx.write_text_bom(p,s)
 p=pdx.MOD_ROOT/'ui/dashboard_registry.json';d=json.loads(pdx.read_text(p));d['modules']=[m for m in d['modules'] if m['id']!='communications']+[registry_module()];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 p=pdx.MOD_ROOT/'tools/gen_facility_aging.py';s=p.read_text(encoding='utf-8')
 if "'tsin_telegraph_office'" not in s:s=s.replace("'tsin_public_school','tsin_research_university'","'tsin_telegraph_office','tsin_telephone_office','tsin_public_school','tsin_research_university'",1);p.write_text(s,encoding='utf-8')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();bad=[]
 for rel,text in build().items():
  p=pdx.MOD_ROOT/rel
  if a.check:
   if not p.exists() or pdx.read_text(p)!=text:bad.append(rel)
  elif '/building_types/' in rel and not p.exists():
   source=pdx.MOD_ROOT/'era_7'/rel;source.parent.mkdir(parents=True,exist_ok=True);source.write_text(text,encoding='utf-8-sig')
  else:pdx.write_text_bom(p,text)
 if not a.check:
  import sync_eras,era_layout
  sync_eras.register(pdx.MOD_ROOT);era_layout.sync(pdx.MOD_ROOT)
  for name,icon in [('telegraph','tsin_railway_station'),('telephone','tsin_electric_lighting')]:
   p=pdx.MOD_ROOT/f'era_7/main_menu/gfx/interface/icons/buildings/tsin_{name}_office.dds'
   if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(pdx.read_bytes(pdx.MOD_ROOT/f'main_menu/gfx/interface/icons/buildings/{icon}.dds'))
  sync_eras.register(pdx.MOD_ROOT);era_layout.sync(pdx.MOD_ROOT)
  integrate()
 print('Communications:',len(bad),'differences');return bool(bad)
if __name__=='__main__':raise SystemExit(main())
