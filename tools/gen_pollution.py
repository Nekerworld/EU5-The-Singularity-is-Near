"""Employment-based urban pollution; piggybacks the existing annual aggregate pass."""
from pathlib import Path
import sys,argparse,json,re
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx

HEAVY=['tsin_steam_metro','iron_mill','steel_mill','cannons_factory','firearms_factory','weapon_factory','tsin_automated_iron_mill','tsin_machine_works','tsin_farm_machinery_works']
CHEMICAL=['dyes_mill','tannery_mill','putrefaction_mill','tsin_fertilizer_plant','tsin_explosives_plant','tsin_nitrogen_fixation_plant']
LIGHT=['brewery_mill','printing_mill','textile_mill','fine_cloth_mill','furniture_mill','glass_mill','distiller_mill','naval_supplies_mill','paper_mill','pottery_mill','tsin_mechanized_textile_mill','tsin_automated_glass_mill','tsin_automated_paper_mill','tsin_automated_furniture_mill','tsin_automated_printing_mill','tsin_automated_fine_cloth_mill']

def types(names):return 'OR = { '+' '.join('building_type = building_type:'+n for n in names)+' }'

def registry_module():
    return {'id':'pollution','metrics':[{'id':'pollution_'+k,'variable':'tsin_pollution_'+k,'title':{'korean':ko,'english':en},'tabs':['society'],'unit':'number','frequency':'annual','description':{'korean':'기존 연간 도시 집계에서 계산한 산업 고용 기반 추정치입니다. 발전소·채굴·교통 배출은 아직 포함하지 않습니다.','english':'Annual urban industrial-employment estimate. Power generation, extraction and transport emissions are not yet included.'}} for k,ko,en in [('exposure','조사 도시 인구 가중 대기 노출','Surveyed urban air exposure'),('high_share','조사 도시 고위험 인구 비율(%)','Surveyed urban high exposure (%)'),('year','공해 조사 연도','Pollution survey year')]],'shortcuts':[{'id':'pollution_map','tab':'society','title':{'korean':'산업 공해 지도','english':'Industrial pollution map'},'map_mode':'tsin_pollution'},{'id':'pollution_filter','tab':'society','title':{'korean':'지역 여과 설비 지원','english':'Fund local emission filters'},'generic_action':'tsin_pollution_filter'}]}

def build():
    fx='''# Scope: location, called only from the existing annual urban aggregate.
tsin_pollution_location_tick_effect = {
 save_scope_as = tsin_pollution_site
 set_variable = { name = tsin_pollution_raw_air value = 0 }
 set_variable = { name = tsin_pollution_raw_water value = 0 }
 every_buildings_in_location = {
  limit = { is_opened = yes building_employed_amount > 0 }
'''
    for names,air,water in [(HEAVY,6,1),(CHEMICAL,4,6),(LIGHT,2,1)]:
        fx+='''  if = { limit = { %s }
   save_temporary_scope_value_as = { name = tsin_pollution_employed value = building_employed_amount }
   scope:tsin_pollution_site = {
    change_variable = { name = tsin_pollution_raw_air add = { value = scope:tsin_pollution_employed multiply = %s } }
    change_variable = { name = tsin_pollution_raw_water add = { value = scope:tsin_pollution_employed multiply = %s } }
   }
  }
'''%(types(names),air,water)
    fx+=''' }
 if = { limit = { NOT = { has_variable = tsin_pollution_air } } set_variable = { name = tsin_pollution_air value = 0 } }
 if = { limit = { NOT = { has_variable = tsin_pollution_water } } set_variable = { name = tsin_pollution_water value = 0 } }
 set_variable = { name = tsin_pollution_air_previous value = var:tsin_pollution_air }
 set_variable = { name = tsin_pollution_water_previous value = var:tsin_pollution_water }
 set_variable = { name = tsin_pollution_air value = { value = var:tsin_pollution_air multiply = 0.4 add = { value = tsin_pollution_air_target multiply = 0.6 } min = 0 max = 100 } }
 set_variable = { name = tsin_pollution_water value = { value = var:tsin_pollution_water multiply = 0.4 add = { value = tsin_pollution_water_target multiply = 0.6 } min = 0 max = 100 } }
 set_variable = { name = tsin_pollution_year value = current_year }
 if = { limit = { var:tsin_pollution_air >= 60 }
  if = { limit = { NOT = { has_variable = tsin_pollution_bad_years } } set_variable = { name = tsin_pollution_bad_years value = 0 } }
  change_variable = { name = tsin_pollution_bad_years add = 1 }
 } else = { set_variable = { name = tsin_pollution_bad_years value = 0 } }
 save_temporary_scope_value_as = { name = tsin_pollution_weighted value = { value = var:tsin_pollution_air multiply = population } }
 save_temporary_scope_value_as = { name = tsin_pollution_population value = population }
 owner = { change_variable = { name = tsin_pollution_weighted add = scope:tsin_pollution_weighted } }
 if = { limit = { var:tsin_pollution_air >= 60 } owner = { change_variable = { name = tsin_pollution_high_pop add = scope:tsin_pollution_population } } }
}
tsin_pollution_finish_country_effect = {
 set_variable = { name = tsin_pollution_year value = current_year }
 set_variable = { name = tsin_pollution_exposure value = 0 }
 set_variable = { name = tsin_pollution_high_share value = 0 }
 if = { limit = { var:tsin_agg_urban_pop > 0 }
  set_variable = { name = tsin_pollution_exposure value = { value = var:tsin_pollution_weighted divide = var:tsin_agg_urban_pop } }
  set_variable = { name = tsin_pollution_high_share value = { value = var:tsin_pollution_high_pop divide = var:tsin_agg_urban_pop multiply = 100 } }
 }
 if = { limit = { is_ai = no NOT = { has_variable = tsin_pollution_petition_cooldown } var:tsin_pollution_high_share >= 10 }
  random_owned_location = { limit = { var:tsin_pollution_bad_years >= 2 } save_scope_as = tsin_pollution_petition_site }
  if = { limit = { exists = scope:tsin_pollution_petition_site }
   set_variable = { name = tsin_pollution_petition_cooldown years = 8 }
   trigger_event_non_silently = tsin_pollution.1
  }
 }
}
'''
    values='''# Game indices, not real pollutant concentrations. No scans in map getters.
tsin_pollution_air_target = {
 value = var:tsin_pollution_raw_air
 if = { limit = { has_variable = tsin_pollution_filters } multiply = 0.65 }
 min = 0 max = 100
}
tsin_pollution_water_target = { value = var:tsin_pollution_raw_water min = 0 max = 100 }
tsin_pollution_map_air = { value = 0 if = { limit = { has_variable = tsin_pollution_year } value = var:tsin_pollution_air } }
tsin_pollution_map_water = { value = 0 if = { limit = { has_variable = tsin_pollution_year } value = var:tsin_pollution_water } }
tsin_pollution_map_emissions = { value = 0 if = { limit = { has_variable = tsin_pollution_year } value = var:tsin_pollution_raw_air } }
tsin_pollution_map_year = { value = 0 if = { limit = { has_variable = tsin_pollution_year } value = var:tsin_pollution_year } }
tsin_pollution_map_factor = { value = tsin_pollution_map_air divide = 100 }
'''
    auto='''tsin_pollution_air_exposure = {
 category = location type = location
 potential_trigger = { has_variable = tsin_pollution_air var:tsin_pollution_air > 0 }
 scales_with = tsin_pollution_map_factor
 local_migration_attraction = -0.1
}
'''
    actions='''tsin_pollution_filter = {
 type = owncountry price = price:tsin_pollution_filter_price show_message = no
 ai_tick = monthly ai_tick_frequency = 12 automation_tick = never
 potential = { scope:actor = { has_advance = tsin_urban_planning_advance } }
 ai_prerequisite = { gold >= 1200 }
 select_trigger = {
  looking_for_a = location source = actor target_flag = target_location name = "choose_location"
  column = { data = name }
  visible = { owner ?= scope:actor has_variable = tsin_pollution_year var:tsin_pollution_air >= 20 }
  enabled = { controller ?= scope:actor NOT = { has_variable = tsin_pollution_filters } }
 }
 effect = { scope:target_location = { set_variable = { name = tsin_pollution_filters years = 10 } } }
 ai_will_do = { value = 10 }
}
'''
    events='''namespace = tsin_pollution
tsin_pollution.1 = {
 type = country_event title = tsin_pollution.1.title desc = tsin_pollution.1.desc outcome = neutral
 illustration_tags = { 10 = interior 10 = regular }
 option = { name = tsin_pollution.1.a trigger = { gold >= 300 }
  add_gold = -300
  scope:tsin_pollution_petition_site = { set_variable = { name = tsin_pollution_filters years = 10 } }
  ai_chance = { factor = 3 }
 }
 option = { name = tsin_pollution.1.b ai_chance = { factor = 1 } }
}
'''
    outputs={'in_game/common/scripted_effects/tsin_pollution.txt':fx,'in_game/common/script_values/tsin_pollution.txt':values,'in_game/common/auto_modifiers/tsin_pollution.txt':auto,'in_game/common/generic_actions/tsin_pollution.txt':actions,'in_game/common/prices/tsin_pollution.txt':'tsin_pollution_filter_price = { gold = 300 }\n','in_game/events/tsin_pollution.txt':events}
    labels={'tsin_pollution':('산업 공해','Industrial pollution'),'tsin_pollution_desc':('연간 산업 공해 추정. 미측정 지역은 회색입니다.','Annual industrial pollution estimates. Unmeasured locations are grey.'),'tsin_pollution_filter':('지역 여과 설비 지원','Fund local emission filters'),'tsin_pollution_filter_desc':('300두캇으로 10년간 산업 대기 배출 추정치를 35% 낮춥니다. 수질 오염·기존 누적 공해는 즉시 없어지지 않습니다.','Pay 300 gold for 10 years of 35% lower estimated industrial air emissions. Does not erase water risk or accumulated pollution.'),'AUTO_MODIFIER_NAME_tsin_pollution_air_exposure':('산업 공해 노출','Industrial pollution exposure'),'TSIN_POLLUTION_MAPMODE_TT':("[ROOT.GetLocation.GetName]: 대기 [ROOT.ScriptValue('tsin_pollution_map_air')|1]/100, 수질 위험 [ROOT.ScriptValue('tsin_pollution_map_water')|1]/100, 대기 원배출 추정 [ROOT.ScriptValue('tsin_pollution_map_emissions')|1]. 조사 연도 [ROOT.ScriptValue('tsin_pollution_map_year')|0] (0=미측정). 산업 실제 고용 기반 연간 캐시. 발전소·채굴·교통 배출 미포함.","[ROOT.GetLocation.GetName]: air [ROOT.ScriptValue('tsin_pollution_map_air')|1]/100, water risk [ROOT.ScriptValue('tsin_pollution_map_water')|1]/100, estimated raw air emissions [ROOT.ScriptValue('tsin_pollution_map_emissions')|1]. Survey year [ROOT.ScriptValue('tsin_pollution_map_year')|0] (0=unmeasured). Annual industrial employment cache; excludes power, extraction and transport."),'LEGEND_KEY_TSIN_POLLUTION_HIGH':('고공해','High pollution'),'LEGEND_KEY_TSIN_POLLUTION_LOW':('저공해','Low pollution'),'LEGEND_KEY_TSIN_POLLUTION_UNKNOWN':('미측정','Unmeasured'),'tsin_pollution.1.title':('굴뚝 아래의 청원','A petition beneath the chimneys'),'tsin_pollution.1.desc':('산업 도시의 매연 노출이 여러 해 지속되면서 주민들이 여과 설비 지원을 청원했습니다. 지원은 배출을 줄이지만 쌓인 공해를 즉시 제거하지는 못합니다.','After years of industrial smoke exposure, residents petition for emission filters. Support reduces emissions; accumulated pollution clears gradually.'),'tsin_pollution.1.a':('여과 설비에 300두캇을 지원한다','Fund filters for 300 gold'),'tsin_pollution.1.b':('추가 지원은 하지 않는다','Decline additional funding')}
    labels['mapmode_tsin_pollution_name']=labels['tsin_pollution']
    labels['MAPMODE_TSIN_POLLUTION']=labels['tsin_pollution_desc']
    for lang,i in [('korean',0),('english',1)]:outputs[f'main_menu/localization/{lang}/tsin_pollution_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {k}: '+json.dumps(v[i],ensure_ascii=False)+'\n' for k,v in labels.items())
    return outputs

def integrate():
    p=pdx.MOD_ROOT/'in_game/common/scripted_effects/tsin_aggregate_effects.txt';s=pdx.read_text(p)
    if 'tsin_pollution_location_tick_effect = yes' not in s:
        s=s.replace('\tset_variable = { name = tsin_agg_urban_pop value = 0 }','\tset_variable = { name = tsin_pollution_weighted value = 0 }\n\tset_variable = { name = tsin_pollution_high_pop value = 0 }\n\tset_variable = { name = tsin_agg_urban_pop value = 0 }',1)
        s=s.replace('\t\tset_local_variable = { name = tsin_agg_l_pop value = population }','\t\ttsin_pollution_location_tick_effect = yes\n\t\tset_local_variable = { name = tsin_agg_l_pop value = population }',1)
        s=s.replace('\ttsin_update_education_effect = yes','\ttsin_pollution_finish_country_effect = yes\n\ttsin_update_education_effect = yes',1)
        pdx.write_text_bom(p,s)
    p=pdx.MOD_ROOT/'in_game/gfx/map/map_modes/tsin_map_modes.txt';s=pdx.read_text(p)
    if not any(b.key=='tsin_pollution' for b in pdx.top_level_blocks(s)):
        template=next(b.text for b in pdx.top_level_blocks(s) if b.key=='tsin_electrification')
        tail=template[template.index('\tsmall_map_names ='):]
        header='''tsin_pollution = {
 map_color = {
  if = { limit = { has_variable = tsin_pollution_year } lerp = { min_color = define:NMapColors|MAP_COLOR_LOW max_color = define:NMapColors|MAP_COLOR_MAX factor = tsin_pollution_map_factor } }
 }
 tooltip_key = { value = TSIN_POLLUTION_MAPMODE_TT }
 legend_key = { desc = "LEGEND_KEY_TSIN_POLLUTION_HIGH" color = define:NMapColors|MAP_COLOR_MAX }
 legend_key = { desc = "LEGEND_KEY_TSIN_POLLUTION_LOW" color = define:NMapColors|MAP_COLOR_LOW }
 legend_key = { desc = "LEGEND_KEY_TSIN_POLLUTION_UNKNOWN" color = define:NMapColors|MAP_COLOR_MIN }
'''
        pdx.write_text_bom(p,s+'\n'+header+tail+'\n')
    p=pdx.MOD_ROOT/'ui/dashboard_registry.json';d=json.loads(pdx.read_text(p));d['modules']=[m for m in d['modules'] if m['id']!='pollution']+[registry_module()];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    icon=pdx.MOD_ROOT/'main_menu/gfx/interface/icons/map_modes/tsin_pollution.dds'
    if not icon.exists():pdx.write_bytes(icon,pdx.read_bytes(pdx.MOD_ROOT/'main_menu/gfx/interface/icons/map_modes/tsin_industrialization.dds'))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();bad=[]
    for rel,text in build().items():
        p=pdx.MOD_ROOT/rel
        if a.check:
            if not p.exists() or pdx.read_text(p)!=text:bad.append(rel)
        else:pdx.write_text_bom(p,text)
    if not a.check:integrate()
    print('Pollution:',len(bad),'differences');return bool(bad)
if __name__=='__main__':raise SystemExit(main())
