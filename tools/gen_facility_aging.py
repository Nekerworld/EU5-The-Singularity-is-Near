"""Province facility bundles: five-to-seven-year inspections, wear separate from modernization."""
from pathlib import Path
import sys,argparse,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx
GROUPS={
 'industry':('산업','Industry',['tsin_machine_tools_advance','tsin_electric_motor_advance','tsin_motor_transport_advance'],None),
 'transport':('교통','Transport',['tsin_steel_rolling_stock_advance','tsin_telegraph_telephone_advance','tsin_motor_transport_advance'],['tsin_railway_station','tsin_steam_metro','tsin_electric_metro','tsin_motor_transport_depot']),
 'public':('공공설비','Public services',['tsin_urban_planning_advance','tsin_modern_sewerage_advance','tsin_distribution_grid_advance'],['tsin_telegraph_office','tsin_telephone_office','tsin_public_school','tsin_research_university','tsin_cold_storage','tsin_electric_cold_storage','tsin_electric_lighting','tsin_distribution_substation','tsin_water_treatment_works','tsin_environment_inspectorate','hospital'])}

def selector():return '''select_trigger = {
 looking_for_a = province source = actor target_flag = target_province name = "choose_province"
 column = { data = name }
 visible = { owner ?= scope:actor has_variable = tsin_facility_registered }
 enabled = { NOT = { any_location_in_province = { NOT = { controller ?= scope:actor } } } }
}'''

def registry_module():
 shortcuts=[{'id':'facility_'+k,'tab':'economy','title':{'korean':ko,'english':en},'generic_action':'tsin_facility_'+k} for k,ko,en in [('budget_on','지방 설비 정비 지원 예산 켜기','Enable district maintenance support'),('budget_off','지방 설비 정비 지원 예산 끄기','Disable district maintenance support'),('inspect','지방 설비 상태 조사','Inspect district facilities')]]
 for group,(ko,en,_,_) in GROUPS.items():
  for op,ok,oe in [('repair','보수','Repair'),('modernize','현대화','Modernize')]:shortcuts.append({'id':f'facility_{op}_{group}','tab':'economy','title':{'korean':ko+' 설비 '+ok,'english':oe+' '+en.lower()},'generic_action':f'tsin_facility_{op}_{group}'})
 return {'id':'facility_aging','shortcuts':shortcuts,'metrics':[{'id':f'facility_report_{g}_{f}','variable':f'tsin_facility_report_{g}_{f}','title':{'korean':ko+' — '+fk,'english':en+' — '+fe},'tabs':['economy'],'unit':'number','frequency':'manual','description':{'korean':'설비 조사 버튼으로 읽은 지방 묶음의 추정치입니다. 가동 산업 지방만 등록하며 실제 상태는 5~7년마다 갱신합니다. 나이는 규모 가중 추정, 마모는 0~100, 기술 격차는 국가의 활용 가능 기술 대비 단계 차이입니다.','english':'Province-bundle estimate read by Inspect. Only operating industrial districts are registered. Conditions update every 5–7 years; age is size-weighted, wear 0–100, gap relative to available national technology.'}} for g,(ko,en,_,_) in GROUPS.items() for f,fk,fe in [('age','추정 시설 연령','Estimated age'),('wear','마모 지수','Wear index'),('gap','기술 격차','Technology gap'),('size','시설 규모','Facility scale'),('year','상태 기준 연도','Condition reference year')]]}

def build():
 values=[];autos=[];actions=[];labels={}
 fx=['''tsin_facility_register_location_effect = {
 province = {
  if = { limit = { NOT = { has_variable = tsin_facility_registered } }
   set_variable = tsin_facility_registered
   save_scope_as = tsin_facility_district
   tsin_facility_measure_effect = yes
''']
 for group,(ko,en,techs,buildings) in GROUPS.items():
  size='value = tsin_location_mill_levels' if buildings is None else 'value = 0\n'+'\n'.join(f' add = "location_building_level(building_type:{b})"' for b in buildings)
  values.append(f'tsin_facility_{group}_location_size = {{ {size}\n}}\n')
  values.append(f'tsin_facility_{group}_technology = {{ value = 0\n'+''.join(f' if = {{ limit = {{ owner ?= {{ has_advance = {tech} }} }} value = {n} }}\n' for n,tech in enumerate(techs,1))+'}\n')
  values.append(f'''tsin_facility_{group}_gap = {{ value = tsin_facility_{group}_technology subtract = var:tsin_facility_{group}_grade min = 0 }}
tsin_facility_{group}_price_factor = {{ value = var:tsin_facility_{group}_size divide = 25 min = 1 }}
tsin_facility_{group}_wear_scale = {{ value = province.var:tsin_facility_{group}_wear subtract = 50 divide = 50 min = 0 max = 1 }}
tsin_facility_{group}_gap_scale = {{ value = province.tsin_facility_{group}_gap divide = 3 min = 0 max = 1 }}
''')
  fx.append(f'''   set_variable = {{ name = tsin_facility_{group}_size value = var:tsin_facility_{group}_measured }}
   set_variable = {{ name = tsin_facility_{group}_age value = 0 }}
   set_variable = {{ name = tsin_facility_{group}_wear value = 0 }}
   # Unknown legacy installation date: neutral observation baseline, no bonus or free replacement.
   set_variable = {{ name = tsin_facility_{group}_grade value = tsin_facility_{group}_technology }}
   set_variable = {{ name = tsin_facility_{group}_year value = current_year }}
''')
  penalty={'industry':'local_mills_build_buildings_efficiency = -0.02','transport':'local_market_access = -0.02','public':'local_population_capacity_modifier = -0.03'}[group]
  for state in ['wear','gap']:
   key=f'tsin_facility_{group}_{state}'
   autos.append(f'''{key} = {{ category = location type = location
 potential_trigger = {{ controller ?= owner tsin_facility_{group}_location_size > 0 province = {{ has_variable = tsin_facility_registered }} }}
 scales_with = tsin_facility_{group}_{state}_scale
 {penalty}
}}
''')
   labels['AUTO_MODIFIER_NAME_'+key]=(ko+(' 설비 마모' if state=='wear' else ' 설비 기술 격차'),en+(' wear' if state=='wear' else ' obsolescence'))
  for operation,opko,open_,cost in [('repair','보수','Repair',100),('modernize','현대화','Modernize',300)]:
   key=f'tsin_facility_{operation}_{group}'
   condition=f'var:tsin_facility_{group}_wear > 0' if operation=='repair' else f'OR = {{ tsin_facility_{group}_gap > 0 var:tsin_facility_{group}_age >= 15 }}'
   gate=f'owner ?= scope:actor var:tsin_facility_{group}_size > 0 {condition} NOT = {{ any_location_in_province = {{ NOT = {{ controller ?= scope:actor }} }} }}'
   body=f'''set_variable = {{ name = tsin_facility_{group}_age value = {{ value = var:tsin_facility_{group}_age add = {{ value = current_year subtract = var:tsin_facility_{group}_year }} }} }}
set_variable = {{ name = tsin_facility_{group}_year value = current_year }}
set_variable = {{ name = tsin_facility_{group}_wear value = 0 }}'''
   if operation=='modernize':body+=f'\nset_variable = {{ name = tsin_facility_{group}_grade value = {{ value = tsin_facility_{group}_technology min = var:tsin_facility_{group}_grade }} }}\nset_variable = {{ name = tsin_facility_{group}_age value = 0 }}'
   actions.append(f'''{key} = {{
 type = owncountry price = price:tsin_facility_{operation}_price show_message = no
 price_modifier = {{ value = 1 if = {{ limit = {{ exists = scope:target_province }} value = scope:target_province.tsin_facility_{group}_price_factor }} }}
 ai_tick = never automation_tick = never
 allow = {{ trigger_if = {{ limit = {{ exists = scope:target_province }} scope:target_province = {{ {gate} }} }} }}
 {selector()}
 effect = {{ scope:target_province = {{ if = {{ limit = {{ {gate} }} {body} }} }} }}
}}
''')
   labels[key]=(ko+' 설비 '+opko,open_+' '+en.lower()+' facilities')
   labels[key+'_desc']=(f'등록 지방을 선택합니다. 비용 {cost}두캇 × max(해당 시설 규모/25, 1). 보수는 마모만 회복하고 현대화는 해당 묶음의 연령·국가 기술 대비 설비 기준을 갱신합니다. 다른 묶음을 초기화하지 않습니다.',f'Choose a registered province. Cost {cost} gold × max(bundle scale/25, 1). Repair restores condition only; modernization refreshes age and technology baseline for this bundle, without resetting other bundles.')
 fx.append('''   tsin_facility_schedule_review_effect = yes
   add_to_global_variable_list = { name = tsin_facility_districts target = this }
   set_global_variable = tsin_facility_aging_enabled
  }
 }
}
tsin_facility_schedule_review_effect = {
 set_variable = { name = tsin_facility_due value = { value = current_year add = 5 } }
 random_list = {
  1 = { }
  1 = { change_variable = { name = tsin_facility_due add = 1 } }
  1 = { change_variable = { name = tsin_facility_due add = 2 } }
 }
}
tsin_facility_measure_effect = {
''')
 for group in GROUPS:fx.append(f' set_variable = {{ name = tsin_facility_{group}_measured value = 0 }}\n')
 fx.append(' every_location_in_province = {\n')
 for group in GROUPS:fx.append(f''' save_temporary_scope_value_as = {{ name = tsin_facility_{group}_size value = tsin_facility_{group}_location_size }}
 scope:tsin_facility_district = {{ change_variable = {{ name = tsin_facility_{group}_measured add = scope:tsin_facility_{group}_size }} }}
''')
 fx.append(' }\n}\ntsin_facility_review_effect = {\n set_global_variable = { name = tsin_facility_review_year value = current_year }\n every_in_global_list = { variable = tsin_facility_districts\n  if = { limit = { exists = owner current_year >= var:tsin_facility_due }\n   save_scope_as = tsin_facility_district\n   tsin_facility_measure_effect = yes\n')
 for group in GROUPS:
  fx.append(f'''   set_local_variable = {{ name = tsin_facility_elapsed value = {{ value = current_year subtract = var:tsin_facility_{group}_year min = 0 }} }}
   change_variable = {{ name = tsin_facility_{group}_age add = local_var:tsin_facility_elapsed }}
   if = {{ limit = {{ var:tsin_facility_{group}_measured > var:tsin_facility_{group}_size var:tsin_facility_{group}_measured > 0 }}
    set_variable = {{ name = tsin_facility_{group}_age value = {{ value = var:tsin_facility_{group}_age multiply = var:tsin_facility_{group}_size divide = var:tsin_facility_{group}_measured }} }}
   }}
   set_local_variable = {{ name = tsin_facility_cost value = {{ value = var:tsin_facility_{group}_measured multiply = local_var:tsin_facility_elapsed multiply = 0.25 }} }}
   if = {{ limit = {{ var:tsin_facility_{group}_measured > 0 }}
    if = {{ limit = {{ local_var:tsin_facility_cost > 0 owner ?= {{ gold >= local_var:tsin_facility_cost OR = {{ has_variable = tsin_facility_support_budget AND = {{ is_ai = yes gold >= {{ value = local_var:tsin_facility_cost multiply = 4 }} }} }} }} NOT = {{ any_location_in_province = {{ NOT = {{ controller ?= owner }} }} }} }}
     owner = {{
      if = {{ limit = {{ OR = {{ NOT = {{ has_variable = tsin_facility_paid_year }} current_year > var:tsin_facility_paid_year }} }}
       set_variable = {{ name = tsin_facility_paid_year value = current_year }}
       set_variable = {{ name = tsin_facility_paid_amount value = 0 }}
      }}
      change_variable = {{ name = tsin_facility_paid_amount add = local_var:tsin_facility_cost }}
      add_gold = {{ value = local_var:tsin_facility_cost multiply = -1 }}
      tsin_news_record_effect = {{ TYPE = 30 PRIORITY = 1 }}
     }}
     set_variable = {{ name = tsin_facility_{group}_wear value = {{ value = var:tsin_facility_{group}_wear subtract = {{ value = local_var:tsin_facility_elapsed multiply = 3 }} min = 0 max = 100 }} }}
    }} else = {{ set_variable = {{ name = tsin_facility_{group}_wear value = {{ value = var:tsin_facility_{group}_wear add = {{ value = local_var:tsin_facility_elapsed multiply = 2 }} min = 0 max = 100 }} }} }}
   }} else = {{
    set_variable = {{ name = tsin_facility_{group}_wear value = 0 }}
    set_variable = {{ name = tsin_facility_{group}_age value = 0 }}
   }}
   set_variable = {{ name = tsin_facility_{group}_size value = var:tsin_facility_{group}_measured }}
   set_variable = {{ name = tsin_facility_{group}_year value = current_year }}
''')
 fx.append('   tsin_facility_schedule_review_effect = yes\n  }\n }\n}\n')
 for state,ko,en,body in [('on','켜기','Enable','set_variable = { name = tsin_facility_support_budget value = 1 }'),('off','끄기','Disable','remove_variable = tsin_facility_support_budget')]:
  key='tsin_facility_budget_'+state
  actions.append(f'{key} = {{ type = owncountry price = price:tsin_facility_control_price show_message = no ai_tick = never automation_tick = never effect = {{ scope:actor = {{ {body} }} }} }}\n')
  labels[key]=('지방 설비 정비 지원 예산 '+ko,en+' district maintenance support')
  labels[key+'_desc']=('등록 산업 지방의 5~7년 검사 때 시설 규모 × 경과 연수 × 0.25두캇을 묶음별로 지불해 마모를 회복합니다. 국고가 부족하면 지불하지 않고 마모가 진행됩니다. 플레이어는 기본 꺼짐이고 AI는 비용 4배 이상의 현금이 있을 때만 지원합니다. 기존 건물 재화 유지비와 별도의 정부 정비 지원입니다. 기술 현대화는 자동으로 하지 않습니다.','At 5–7-year inspections, pay bundle scale × elapsed years × 0.25 gold to restore condition. If unaffordable, do not pay and wear advances. Off by default for players; AI supports maintenance only with at least four times the cost in cash. Separate government engineering support, not a replacement for native building upkeep. Does not modernize technology.')
 inspector=[]
 for group in GROUPS:
  for field in ['age','wear','size','year']:
   inspector.append(f'set_variable = {{ name = tsin_facility_report_{group}_{field} value = scope:target_province.var:tsin_facility_{group}_{field} }}')
  inspector.append(f'set_variable = {{ name = tsin_facility_report_{group}_gap value = scope:target_province.tsin_facility_{group}_gap }}')
 actions.append('tsin_facility_inspect = { type = owncountry price = price:tsin_facility_control_price show_message = no ai_tick = never automation_tick = never\n'+selector()+'\n effect = { scope:actor = { '+'\n'.join(inspector)+' } }\n}\n')
 labels['tsin_facility_inspect']=('지방 설비 상태 조사','Inspect district facilities')
 labels['tsin_facility_inspect_desc']=('등록된 산업 지방을 선택해 마지막 검사 상태를 TSIN 경제 보고서에 표시합니다. 열람은 마모 진행·보수·현대화·추가 지출을 실행하지 않습니다.','Choose a registered industrial province to copy its last inspection into TSIN economic reports. Viewing does not advance wear, repair, modernize or spend money.')
 outputs={'in_game/common/script_values/tsin_facility_aging.txt':'\n'.join(values),'in_game/common/auto_modifiers/tsin_facility_aging.txt':'\n'.join(autos),'in_game/common/scripted_effects/tsin_facility_aging.txt':'\n'.join(fx),'in_game/common/generic_actions/tsin_facility_aging.txt':'\n'.join(actions),'in_game/common/prices/tsin_facility_aging.txt':'tsin_facility_repair_price = { gold = 100 }\ntsin_facility_modernize_price = { gold = 300 }\ntsin_facility_control_price = { gold = 0 }\n','in_game/common/on_action/tsin_facility_aging.txt':'''yearly_country_pulse = { on_actions = { tsin_facility_annual_check } }
tsin_facility_annual_check = {
 trigger = { has_global_variable = tsin_facility_aging_enabled OR = { NOT = { has_global_variable = tsin_facility_review_year } current_year > global_var:tsin_facility_review_year } }
 effect = { tsin_facility_review_effect = yes }
}
'''}
 for lang,i in [('korean',0),('english',1)]:outputs[f'main_menu/localization/{lang}/tsin_facility_aging_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {k}: '+json.dumps(v[i],ensure_ascii=False)+'\n' for k,v in labels.items())
 return outputs

def integrate():
 p=pdx.MOD_ROOT/'in_game/common/scripted_effects/tsin_aggregate_effects.txt';s=pdx.read_text(p)
 if 'tsin_facility_register_location_effect = yes' not in s:
  s=s.replace('\t\ttsin_pollution_location_tick_effect = yes','\t\ttsin_pollution_location_tick_effect = yes\n\t\tif = { limit = { var:tsin_pollution_raw_air > 0 tsin_location_industrial_jobs > 0 } tsin_facility_register_location_effect = yes }',1);pdx.write_text_bom(p,s)
 module=registry_module()
 for key,variable,ko,en in [('budget','tsin_facility_support_budget','지방 정비 지원 예산(1=켜짐)','District support budget (1=on)'),('paid','tsin_facility_paid_amount','마지막 지원 연도 지출','Support spending in last funding year'),('paid_year','tsin_facility_paid_year','마지막 정비 지원 연도','Last maintenance funding year')]:
  module['metrics'].append({'id':'facility_'+key,'variable':variable,'title':{'korean':ko,'english':en},'tabs':['economy'],'unit':'number','frequency':'event','description':{'korean':'실제 정비 지원 결제 때 갱신하는 장부입니다. 정기 통계 조사를 추가하지 않습니다. 비용은 검사 시 국고에서 지급하며 현대화 비용과 별개입니다.','english':'Ledger updated when maintenance support is actually paid. No periodic statistics survey. Paid from treasury at inspections, separate from modernization.'}})
 p=pdx.MOD_ROOT/'ui/dashboard_registry.json';d=json.loads(pdx.read_text(p));d['modules']=[m for m in d['modules'] if m['id']!='facility_aging']+[module];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();bad=[]
 for rel,text in build().items():
  p=pdx.MOD_ROOT/rel
  if a.check:
   if not p.exists() or pdx.read_text(p)!=text:bad.append(rel)
  else:pdx.write_text_bom(p,text)
 if not a.check:integrate()
 print('Facility aging:',len(bad),'differences');return bool(bad)
if __name__=='__main__':raise SystemExit(main())
