"""International standardization: independent national choices, bounded yearly readiness check."""
from pathlib import Path
import sys,argparse,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx
DOMAINS={
 'measure':('도량형','Measures','tsin_industrial_capitalism_advance',[(1,'공통 단위','Common units',150,'global_merchant_capacity_modifier = 0.02'),(2,'기존 단위와 병용','Dual units',75,'global_merchant_capacity_modifier = 0.01'),(3,'독자 단위 유지','Keep domestic units',0,'')]),
 'gauge':('철도 규격','Rail standards','tsin_steel_rolling_stock_advance',[(1,'권고 규격 채택','Adopt recommended standard',200,'build_railroad_cost_modifier = -0.03'),(2,'기존 규격·환적 호환','Keep gauge with interchange',100,'build_railroad_cost_modifier = -0.01'),(3,'독자 철도 규격','Keep domestic rail standard',0,'')]),
 'parts':('산업 부품','Industrial parts','tsin_engineering_education_advance',[(1,'공통 부품 규격','Common parts',150,'research_speed_modifier = 0.02'),(3,'국내 부품 규격','Domestic parts',0,'research_speed_modifier = 0.01')]),
 'electric':('전기 설비','Electrical equipment','tsin_distribution_grid_advance',[(1,'상호접속 권고 규격','Interconnection standard',200,'global_tsin_electricity_output_modifier = 0.03'),(2,'변환 설비와 병용','Compatibility converters',100,'global_tsin_electricity_output_modifier = 0.02'),(3,'독자 전기 규격','Domestic electrical standard',0,'')])}

def registry_module():
 return {'id':'standardization','shortcuts':[{'id':'standards_host','tab':'research','title':{'korean':'국제 표준화 회의 개최','english':'Host standards conference'},'generic_action':'tsin_standards_host'}]+[{'id':f'standards_{d}_{n}','tab':'research','title':{'korean':ko+' — '+name,'english':en+' — '+ename},'generic_action':f'tsin_standards_{d}_{n}'} for d,(ko,en,tech,choices) in DOMAINS.items() for n,name,ename,cost,effect in choices], 'metrics':[{'id':'standard_'+d,'variable':'tsin_standard_'+d,'title':{'korean':ko+' 선택','english':en+' choice'},'tabs':['research'],'unit':'number','frequency':'event','description':{'korean':'0=미선택, 1=공통 규격, 2=병용·호환, 3=독자 유지. 분야별 선택은 독립적입니다. 실제 모든 노선·단위를 강제 변경하지 않습니다.','english':'0=undecided, 1=common, 2=dual/compatible, 3=domestic. Domains are independent; does not forcibly rebuild every network.'}} for d,(ko,en,tech,choices) in DOMAINS.items()]}

def build():
 labels={};prices=['tsin_standards_host_price = { gold = 500 }'];autos=[];actions=[]
 actions.append('''tsin_standards_host = {
 type = owncountry price = price:tsin_standards_host_price show_message = no
 ai_tick = monthly ai_tick_frequency = 12 automation_tick = never
 potential = { NOT = { has_global_variable = tsin_standards_pending } NOT = { has_global_variable = tsin_standards_cooldown } NOT = { is_situation_active = situation:tsin_standardization } }
 allow = { global_var:tsin_standards_industrial_countries >= 3 scope:actor = { has_advance = tsin_engineering_education_advance at_war = no var:tsin_factory_share >= 0.1 tsin_country_secondary_education >= 20 exists = capital } }
 ai_prerequisite = { gold >= 2500 }
 effect = {
  set_global_variable = tsin_standards_pending
  set_global_variable = { name = tsin_standards_host_country value = scope:actor }
 }
 ai_will_do = { value = 20 }
}
''')
 for d,(ko,en,tech,choices) in DOMAINS.items():
  for n,name,ename,cost,bonus in choices:
   key=f'tsin_standards_{d}_{n}';prices.append(f'{key}_price = {{ gold = {cost} }}')
   gate=f'''has_advance = {tech}
 NOT = {{ has_variable = tsin_standard_{d}_cooldown }}
 NOT = {{ var:tsin_standard_{d} = {n} }}'''
   count_change=f'if = {{ limit = {{ var:tsin_standard_{d} = 1 global_var:tsin_standards_common_{d} > 0 }} change_global_variable = {{ name = tsin_standards_common_{d} add = -1 }} }}'
   if n==1:count_change+=f' change_global_variable = {{ name = tsin_standards_common_{d} add = 1 }}'
   actions.append(f'''{key} = {{
 type = owncountry price = price:{key}_price show_message = no
 ai_tick = monthly ai_tick_frequency = 12 automation_tick = never
 potential = {{ OR = {{ is_situation_active = situation:tsin_standardization has_global_variable = tsin_standards_formed }} scope:actor = {{ has_advance = {tech} }} }}
 allow = {{ scope:actor = {{ {gate} }} }}
 ai_prerequisite = {{ gold >= {max(cost*4,100)} NOT = {{ has_variable = tsin_standard_{d} }} }}
 effect = {{ scope:actor = {{
  if = {{ limit = {{ {gate} }}
   {count_change}
   tsin_news_record_effect = {{ TYPE = 10 PRIORITY = 1 }}
   set_variable = {{ name = tsin_standard_{d} value = {n} }}
   set_variable = {{ name = tsin_standard_{d}_cooldown years = 5 }}
   if = {{ limit = {{ NOT = {{ has_variable = tsin_standards_participant }} }}
    set_variable = tsin_standards_participant
    change_global_variable = {{ name = tsin_standards_participants add = 1 }}
   }}
  }}
 }} }}
 ai_will_do = {{ value = {25 if n==1 else 10} }}
}}
''')
   if bonus:autos.append(f'''{key} = {{
 potential_trigger = {{ var:tsin_standard_{d} = {n} }}
 {bonus}
}}
''')
   labels[key]=(ko+' — '+name,en+' — '+ename)
   labels[key+'_desc']=('이 분야만 선택하며 다른 규격은 바꾸지 않습니다. 선택 후 5년간 재변경할 수 없습니다. 기존 시설을 즉시 개궤·재건하거나 네이티브 운행을 금지하지 않습니다. 전기 효과는 설비 규격화의 생산 보정이며 별도 전력망 연결이 아닙니다.','Change this domain only, with a five-year revision cooldown. Does not instantly regauge/rebuild facilities or ban native operation. Electrical bonuses represent equipment standardization, not a separate connected power grid.')
   if bonus:labels['AUTO_MODIFIER_NAME_'+key]=labels[key]
 effects='tsin_standards_readiness_effect = {\n set_global_variable = { name = tsin_standards_review_year value = current_year }\n set_global_variable = { name = tsin_standards_industrial_countries value = 0 }\n'
 for domain in DOMAINS:effects+=f' set_global_variable = {{ name = tsin_standards_common_{domain} value = 0 }}\n'
 effects+=' every_country = { limit = { exists = capital num_locations > 0 }\n if = { limit = { has_variable = tsin_factory_share var:tsin_factory_share >= 0.05 tsin_country_secondary_education >= 10 capital = { market_access >= 0.5 } } change_global_variable = { name = tsin_standards_industrial_countries add = 1 } }\n'
 for domain in DOMAINS:effects+=f' if = {{ limit = {{ var:tsin_standard_{domain} = 1 }} change_global_variable = {{ name = tsin_standards_common_{domain} add = 1 }} }}\n'
 effects+=' }\n}\n'
 situation='''tsin_standardization = {
 monthly_spawn_chance = 100
 can_start = { has_global_variable = tsin_standards_pending }
 visible = { exists = capital num_locations > 0 }
 on_start = {
  tsin_standards_readiness_effect = yes
  remove_global_variable = tsin_standards_pending
  set_global_variable = { name = tsin_standards_participants value = 0 }
  every_country = { limit = { exists = capital num_locations > 0 has_variable = tsin_standards_participant } change_global_variable = { name = tsin_standards_participants add = 1 } }
 }
 outcome = { name = tsin_standards_agreement trigger = { situation:tsin_standardization = { years_since_situation_start >= 3 } tsin_standards_common_agreement = yes } }
 outcome = { name = tsin_standards_no_agreement trigger = { situation:tsin_standardization = { years_since_situation_start >= 3 } tsin_standards_common_agreement = no } }
 on_ended = {
  set_global_variable = { name = tsin_standards_cooldown years = 25 }
  if = { limit = { tsin_standards_common_agreement = yes } set_global_variable = tsin_standards_formed }
 }
 map_color = {
  if = { limit = { owner ?= { has_variable = tsin_standards_participant } } value = define:NMapColors|MAP_COLOR_MAX }
  else = { value = define:NMapColors|DEFAULT_COLOR }
 }
 legend_key = { desc = "tsin_standards_participants_legend" color = define:NMapColors|MAP_COLOR_MAX }
}
'''
 panel=['situation_panel = {',' blockoverride "situation_subheader_content" {}',' blockoverride "situation_panel_main_content" {',' vbox = { spacing = 8 layoutpolicy_horizontal = expanding',' text_multi = { text = "TSIN_STANDARDS_HELP" fontsize = 15 layoutpolicy_horizontal = expanding }']
 for d,(ko,en,tech,choices) in DOMAINS.items():
  panel.append(f' text_single = {{ text = "TSIN_STANDARD_{d.upper()}" fontsize = 16 }}')
  panel.append(' hbox = { spacing = 4')
  for n,name,ename,cost,bonus in choices:
   key=f'tsin_standards_{d}_{n}';panel.append(f'''widget = {{ size = {{ 160 34 }} datacontext = "[GetGenericAction('{key}')]"
 button_regular = {{ size = {{ 160 34 }}
  action_tooltip = {{ title = "{key}" on_action = "[PerformGenericAction(GenericAction.Self)]" }}
  text_single = {{ size = {{ 154 30 }} parentanchor = center autoresize = no fontsize = 12 fontsize_min = 8 text = "{key}" }}
 }}
}}''')
  panel.append(' }')
  labels['TSIN_STANDARD_'+d.upper()]=(ko+f": [GetPlayer.MakeScope.GetVariable('tsin_standard_{d}').GetValue|0]",en+f": [GetPlayer.MakeScope.GetVariable('tsin_standard_{d}').GetValue|0]")
 panel+=[' }',' }','}']
 labels.update({'tsin_standardization':('국제 표준화 논의','International standardization'),'tsin_standardization_desc':('산업국들이 도량형·철도·부품·전기 설비의 호환을 논의합니다. 분야별 독자 규격도 유지할 수 있습니다.','Industrial states discuss measures, rail, parts and electrical compatibility. Domestic standards can be retained separately.'),'tsin_standards_host':('국제 표준화 회의 개최','Host international standards conference'),'tsin_standards_host_desc':('산업·교육·시장 접근 조건을 갖춘 3개국 이상이 필요합니다. 주최국은 공학 교육·공장 비중 10%·중등교육 20%를 갖추고 평화 상태여야 합니다. 비용 500두캇, 회의 3년, 세계 개최 간격 25년입니다.','Requires at least three industrial states meeting education and market-access criteria. The host needs engineering education, 10% factory share, 20% secondary education and peace. Costs 500 gold; conference lasts three years, followed by a 25-year global cooldown.'),'tsin_standards_agreement':('분야별 협약 성립','Sectoral conventions agreed'),'tsin_standards_no_agreement':('합의 없는 폐회','Conference closed without agreement'),'tsin_standards_participants_legend':('규격 선택 참가국','Countries choosing standards'),'TSIN_STANDARDS_HELP':('0=미선택, 1=공통, 2=병용·호환, 3=독자 규격. 한 분야 선택은 다른 분야를 강제하지 않습니다. 회의 폐막도 세계 시설의 일괄 교체를 뜻하지 않습니다.','0=undecided, 1=common, 2=dual/compatible, 3=domestic. Choices are independent. Closing the conference does not replace the world’s facilities.')})
 outputs={'in_game/common/generic_actions/tsin_standardization.txt':'\n'.join(actions),'in_game/common/prices/tsin_standardization.txt':'\n'.join(prices)+'\n','in_game/common/auto_modifiers/tsin_standardization.txt':'\n'.join(autos),'in_game/common/scripted_effects/tsin_standardization.txt':effects,'in_game/common/situations/tsin_standardization.txt':situation,'in_game/gui/panels/situation/tsin_standardization.gui':'\n'.join(panel)+'\n','in_game/common/on_action/tsin_standardization.txt':'''yearly_country_pulse = { on_actions = { tsin_standards_annual_readiness } }
tsin_standards_annual_readiness = {
 trigger = { current_age_or_later = { age = age_7_industrialization }
  OR = { NOT = { has_global_variable = tsin_standards_review_year } current_year > global_var:tsin_standards_review_year }
 }
 effect = { tsin_standards_readiness_effect = yes }
}
'''}
 outputs['in_game/common/scripted_triggers/tsin_standardization.txt']='tsin_standards_common_agreement = { OR = { '+ ' '.join(f'global_var:tsin_standards_common_{d} >= 2' for d in DOMAINS)+' } }\n'
 for lang,i in [('korean',0),('english',1)]:outputs[f'main_menu/localization/{lang}/tsin_standardization_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {k}: '+json.dumps(v[i],ensure_ascii=False)+'\n' for k,v in labels.items())
 return outputs

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();bad=[]
 for rel,text in build().items():
  p=pdx.MOD_ROOT/rel
  if a.check:
   if not p.exists() or pdx.read_text(p)!=text:bad.append(rel)
  else:pdx.write_text_bom(p,text)
 if not a.check:
  p=pdx.MOD_ROOT/'ui/dashboard_registry.json';d=json.loads(pdx.read_text(p));d['modules']=[m for m in d['modules'] if m['id']!='standardization']+[registry_module()];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  for kind in ['icons/situations','illustrations/situation']:
   p=pdx.MOD_ROOT/f'main_menu/gfx/interface/{kind}/tsin_standardization.dds'
   if not p.exists():pdx.write_bytes(p,pdx.read_bytes(pdx.MOD_ROOT/f'main_menu/gfx/interface/{kind}/tsin_world_exhibition.dds'))
 print('Standardization:',len(bad),'differences');return bool(bad)
if __name__=='__main__':raise SystemExit(main())
