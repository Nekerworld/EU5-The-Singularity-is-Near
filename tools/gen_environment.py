"""Water treatment, staffed environmental enforcement and mine-aware survey coverage."""
from pathlib import Path
import sys,argparse,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx
from environment_extension import transform_aggregate

def registry_module():return {'id':'environment','shortcuts':[{'id':'water_pollution_map','tab':'society','title':{'korean':'수질 오염 지도','english':'Water pollution map'},'map_mode':'tsin_water_pollution'},{'id':'environment_laws','tab':'society','title':{'korean':'환경법·법률 화면','english':'Environmental laws'},'view':'laws'}],'metrics':[{'id':'pollution_sample_population','variable':'tsin_pollution_surveyed_people','title':{'korean':'공해 조사 지역 인구','english':'Pollution survey population'},'tabs':['society'],'unit':'compact','frequency':'annual','description':{'korean':'도시와 산업 시대 광산·이전에 조사한 지역의 인구입니다. 농촌 전체를 대표하지 않습니다. 표본이 없으면 노출 지수를 자료 없음으로 표시합니다.','english':'Population in urban areas, industrial-era mines and previously surveyed locations. Not all rural areas. Exposure indices are unavailable if there is no sample.'}}]}

def build():
 buildings='''tsin_water_treatment_works = {
 audio_tier = 3 is_foreign = no forbidden_for_estates = yes pop_type = laborers
 employment_size = 0.05 max_levels = 2 category = infrastructure_category
 rural_settlement = yes town = yes city = yes megalopolis = yes tsin_large_city = yes tsin_megalopolis = yes
 build_time = infrastructure_build_time construction_demand = tsin_infrastructure_construction
 country_potential = { has_advance = tsin_modern_sewerage_advance }
 location_potential = { OR = { population >= 30 tsin_location_mill_levels > 0 tsin_is_polluting_mine = yes } }
 ai_construct_weight = { value = 0 if = { limit = { var:tsin_pollution_water >= 40 } add = 50 } }
 unique_production_methods = {
  tsin_water_treatment_steam = {
   icon_type = goods icon = coal coal = 0.15 tools = 0.05 tsin_engines = 0.02 category = building_maintenance
  }
  tsin_water_treatment_electric = {
   icon_type = goods icon = tsin_electricity tsin_electricity = 0.10 tools = 0.05 category = building_maintenance
  }
 }
}
tsin_environment_inspectorate = {
 audio_tier = 2 is_foreign = no forbidden_for_estates = yes pop_type = burghers
 employment_size = 0.02 max_levels = 1 category = infrastructure_category
 rural_settlement = yes town = yes city = yes megalopolis = yes tsin_large_city = yes tsin_megalopolis = yes
 build_time = infrastructure_build_time construction_demand = tsin_infrastructure_construction
 country_potential = { OR = { has_policy = policy:tsin_environment_inspections_policy has_policy = policy:tsin_environment_standards_policy } }
 location_potential = { OR = { population >= 30 tsin_location_mill_levels > 0 tsin_is_polluting_mine = yes } }
 ai_construct_weight = { value = 0 if = { limit = { OR = { var:tsin_pollution_air >= 40 var:tsin_pollution_water >= 40 } } add = 40 } }
 unique_production_methods = {
  tsin_environment_inspectorate_maintenance = {
   icon_type = goods icon = paper paper = 0.03 tools = 0.02 category = building_maintenance
  }
 }
}
'''
 law='''tsin_environment_law = {
 law_category = socioeconomic
 potential = { has_advance = tsin_urban_planning_advance }
 tsin_environment_unregulated_policy = {
  allow = { tsin_policy_enactable_trigger = yes }
  years = 5 estate_preferences = { burghers_estate nobles_estate }
 }
 tsin_environment_inspections_policy = {
  allow = { tsin_policy_enactable_trigger = yes }
  years = 5 estate_preferences = { crown_estate }
 }
 tsin_environment_standards_policy = {
  allow = { has_advance = tsin_modern_sewerage_advance tsin_policy_enactable_trigger = yes }
  years = 5 estate_preferences = { peasants_estate clergy_estate }
 }
}
'''
 values='''tsin_environment_inspection_scale = { value = var:tsin_pollution_inspection_capacity min = 0 max = 1 }
tsin_environment_air_retention = {
 value = 1
 if = { limit = { controller ?= owner owner ?= { has_policy = policy:tsin_environment_standards_policy } }
  subtract = { value = tsin_environment_inspection_scale multiply = 0.20 }
 } else_if = { limit = { controller ?= owner owner ?= { has_policy = policy:tsin_environment_inspections_policy } }
  subtract = { value = tsin_environment_inspection_scale multiply = 0.10 }
 }
 min = 0.80 max = 1
}
tsin_environment_water_retention = {
 value = 1
 if = { limit = { controller ?= owner owner ?= { has_policy = policy:tsin_environment_standards_policy } }
  subtract = { value = tsin_environment_inspection_scale multiply = 0.10 }
 } else_if = { limit = { controller ?= owner owner ?= { has_policy = policy:tsin_environment_inspections_policy } }
  subtract = { value = tsin_environment_inspection_scale multiply = 0.05 }
 }
 min = 0.90 max = 1
}
tsin_water_pollution_factor = { value = tsin_pollution_map_water divide = 100 min = 0 max = 1 }
'''
 effects='''tsin_environment_finish_country_effect = {
 set_variable = { name = tsin_pollution_surveyed_people value = { value = var:tsin_pollution_surveyed_pop multiply = 1000 } }
 set_variable = { name = tsin_pollution_water_exposure value = 0 }
 set_variable = { name = tsin_pollution_water_high_share value = 0 }
 if = { limit = { var:tsin_pollution_surveyed_pop > 0 }
  set_variable = { name = tsin_pollution_water_exposure value = { value = var:tsin_pollution_water_weighted divide = var:tsin_pollution_surveyed_pop } }
  set_variable = { name = tsin_pollution_water_high_share value = { value = var:tsin_pollution_water_high_pop divide = var:tsin_pollution_surveyed_pop multiply = 100 } }
 } else = {
  remove_variable = tsin_pollution_exposure remove_variable = tsin_pollution_high_share
  remove_variable = tsin_pollution_water_exposure remove_variable = tsin_pollution_water_high_share
 }
 if = { limit = { is_ai = no var:tsin_pollution_water_high_share >= 10 NOT = { has_variable = tsin_water_petition_cooldown } }
  random_owned_location = { limit = { var:tsin_pollution_water_bad_years >= 2 population > 0 } save_scope_as = tsin_water_petition_site }
  if = { limit = { exists = scope:tsin_water_petition_site }
   set_variable = { name = tsin_water_petition_cooldown years = 8 }
   trigger_event_non_silently = tsin_environment.1
  }
 }
}
'''
 events='''namespace = tsin_environment
tsin_environment.1 = {
 type = country_event title = tsin_environment.1.title desc = tsin_environment.1.desc outcome = neutral
 illustration_tags = { 10 = interior 10 = regular }
 immediate = { tsin_news_record_effect = { TYPE = 22 PRIORITY = 1 } }
 option = { name = tsin_environment.1.a trigger = { gold >= 250 scope:tsin_water_petition_site ?= { owner ?= root controller ?= root } }
  if = { limit = { gold >= 250 scope:tsin_water_petition_site ?= { owner ?= root controller ?= root } }
   add_gold = -250
   scope:tsin_water_petition_site = { set_variable = { name = tsin_water_emergency_services years = 5 } }
  }
  ai_chance = { factor = 3 }
 }
 option = { name = tsin_environment.1.b ai_chance = { factor = 1 } }
}
'''
 labels={
 'tsin_water_treatment_works':('폐수 처리시설','Wastewater treatment works'),
 'tsin_water_treatment_works_desc':('실제 가동·고용 수준에 따라 산업·광산 수질 오염원 추정치를 낮춥니다. 정상 가동 1단계당 30%, 최대 60% 저감입니다. 대기 매연을 제거하지 않으며 기존 오염은 연간 조사마다 점차 줄어듭니다.','Reduces estimated industrial/mine water pollution in proportion to effective staffing. Up to 30% per fully operating level, 60% maximum. Does not remove smoke; existing pollution clears gradually at annual reviews.'),
 'tsin_water_treatment_steam':('증기 펌프 처리시설','Steam-pump treatment'),
 'tsin_water_treatment_electric':('전동 펌프 처리시설','Electric-pump treatment'),
 'tsin_environment_inspectorate':('환경 감독소','Environmental inspectorate'),
 'tsin_environment_inspectorate_desc':('환경법을 현장에서 집행합니다. 고용·투입재가 갖춰진 비율만큼 집행하며 감독소나 인력이 없으면 법만으로 배출이 줄지 않습니다. 최대 효과: 검사법 대기 10%·수질 5%, 배출기준법 대기 20%·수질 10% 저감.','Enforces environmental law in proportion to staffing and inputs. Law alone does not reduce emissions without inspectors. Maximum reduction: inspections 10% air / 5% water; standards 20% air / 10% water.'),
 'tsin_environment_inspectorate_maintenance':('환경 감독소 유지','Inspectorate maintenance'),
 'tsin_environment_law':('환경 감독과 배출 규제','Environmental supervision and emissions'),
 'tsin_environment_law_desc':('실제 감독소를 통한 집행과 환경 설비 투자를 정합니다. 법률의 채택은 모든 시설을 즉시 개조하거나 기존 오염을 없애지 않습니다.','Controls enforcement through staffed inspectorates and environmental investment. Enactment neither retrofits every facility nor erases accumulated pollution.'),
 'tsin_environment_unregulated_policy':('자율 처리','Unregulated disposal'),
 'tsin_environment_unregulated_policy_desc':('환경 감독소의 규제 효과가 없습니다. 처리시설과 별도 여과 지원은 계속 이용할 수 있습니다.','No regulatory inspectorate effect. Treatment facilities and separate filter support remain available.'),
 'tsin_environment_inspections_policy':('공해 검사 제도','Pollution inspections'),
 'tsin_environment_inspections_policy_desc':('감독소의 실효 인력 비율에 따라 대기 최대 10%, 수질 최대 5%의 오염원 감축을 유도합니다.','Staffed inspectorates support up to 10% air and 5% water source reductions.'),
 'tsin_environment_standards_policy':('배출 기준과 감독','Emission standards and supervision'),
 'tsin_environment_standards_policy_desc':('감독소의 실효 인력 비율에 따라 대기 최대 20%, 수질 최대 10%의 오염원 감축을 유도합니다.','Staffed inspectorates support up to 20% air and 10% water source reductions.'),
 'AUTO_MODIFIER_NAME_tsin_water_pollution_health':('수질 오염 노출','Water pollution exposure'),
 'mapmode_tsin_water_pollution_name':('수질 오염','Water pollution'),
 'MAPMODE_TSIN_WATER_POLLUTION':('도시·광산의 연간 수질 오염 위험 지수입니다. 실제 농도 단위가 아니며 미조사 농촌을 깨끗하다고 판정하지 않습니다.','Annual urban/mine water-risk index, not a real concentration unit. Unmeasured rural areas are not classified as clean.'),
 'LEGEND_TSIN_WATER_HIGH':('높은 수질 위험','High water risk'),
 'LEGEND_TSIN_WATER_LOW':('낮은 수질 위험','Low water risk'),
 'LEGEND_TSIN_WATER_UNKNOWN':('자료 없음','Unmeasured'),
 'tsin_environment.1.title':('하천에 대한 주민 청원','A petition over polluted water'),
 'tsin_environment.1.desc':('오염된 물에 대한 주민 민원이 여러 해 이어졌습니다. 당국은 임시 정화 서비스를 조달할 수 있지만 장기적인 개선에는 처리시설과 현장 감독이 필요합니다.','Complaints about polluted water have continued for years. Temporary purification services can be procured, while lasting improvement requires treatment works and local supervision.'),
 'tsin_environment.1.a':('250두캇으로 정화 서비스를 조달한다','Procure purification services for 250 gold'),
 'tsin_environment.1.b':('추가 예산을 배정하지 않는다','Allocate no additional funding')}
 outputs={'in_game/common/building_types/tsin_environment_buildings.txt':buildings,'in_game/common/laws/tsin_environment_laws.txt':law,'in_game/common/script_values/tsin_environment.txt':values,'in_game/common/scripted_effects/tsin_environment.txt':effects,'in_game/events/tsin_environment.txt':events,'in_game/common/scripted_triggers/tsin_environment.txt':'''tsin_is_polluting_mine = { current_age_or_later = { age = age_7_industrialization } is_mining_rgo = yes }
''','in_game/common/auto_modifiers/tsin_environment.txt':'''tsin_water_pollution_health = { category = location type = location
 potential_trigger = { has_variable = tsin_pollution_water var:tsin_pollution_water > 0 }
 scales_with = tsin_water_pollution_factor
 local_disease_resistance = -0.05
}
'''}
 for lang,i in [('korean',0),('english',1)]:outputs[f'main_menu/localization/{lang}/tsin_environment_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {k}: '+json.dumps(v[i],ensure_ascii=False)+'\n' for k,v in labels.items())
 return outputs

def integrate():
 p=pdx.MOD_ROOT/'tools/gen_pollution.py';s=p.read_text(encoding='utf-8')
 if 'environment_extension' not in s:
  s=s.replace('def registry_module():','def _base_registry_module():',1)
  s=s.replace('def build():','def registry_module():\n    from environment_extension import refine_registry\n    return refine_registry(_base_registry_module())\n\ndef build():',1)
  s=s.replace('    return outputs','    from environment_extension import refine_pollution\n    return refine_pollution(outputs)',1)
  p.write_text(s,encoding='utf-8')
 p=pdx.MOD_ROOT/'in_game/common/scripted_effects/tsin_aggregate_effects.txt';s=pdx.read_text(p);pdx.write_text_bom(p,transform_aggregate(s))
 p=pdx.MOD_ROOT/'in_game/common/scripted_triggers/tsin_legislation_triggers.txt';s=pdx.read_text(p)
 if 'this = law:tsin_environment_law' not in s:s=s.replace('this = law:tsin_trust_law','this = law:tsin_trust_law\n\t\t\tthis = law:tsin_environment_law',1);pdx.write_text_bom(p,s)
 p=pdx.MOD_ROOT/'tools/gen_bill_events.py';s=p.read_text(encoding='utf-8')
 if '"tsin_environment_law"' not in s:s=s.replace('["tsin_industrial_investment_law", "tsin_trust_law"]','["tsin_industrial_investment_law", "tsin_trust_law", "tsin_environment_law"]',1);p.write_text(s,encoding='utf-8')
 p=pdx.MOD_ROOT/'tools/gen_facility_aging.py';s=p.read_text(encoding='utf-8')
 if "'tsin_water_treatment_works'" not in s:s=s.replace("'tsin_distribution_substation','hospital'","'tsin_distribution_substation','tsin_water_treatment_works','tsin_environment_inspectorate','hospital'",1);p.write_text(s,encoding='utf-8')
 p=pdx.MOD_ROOT/'tools/gen_newspapers.py';s=p.read_text(encoding='utf-8')
 if '22:' not in s:
  article=('오염된 물에 대한 청원','Petition over polluted water','주민들이 수년간 이어진 수질 오염에 대해 청원했습니다. 당국은 임시 정화 서비스와 장기 시설 투자를 검토하고 있습니다.','Residents have petitioned over persistent water pollution. The authorities are considering temporary purification and long-term investment.')
  s=s.replace('ARTICLES={10:','ARTICLES={22:'+repr(article)+',10:',1);p.write_text(s,encoding='utf-8')
 for rel,advance,line in [('tsin_05_mass_society.txt','tsin_modern_sewerage_advance','unlock_building = tsin_water_treatment_works'),('tsin_05_mass_society.txt','tsin_urban_planning_advance','unlock_building = tsin_environment_inspectorate'),('tsin_06_electrification.txt','tsin_electric_motor_advance','unlock_production_method = tsin_water_treatment_electric')]:
  p=pdx.MOD_ROOT/'in_game/common/advances'/rel;s=pdx.read_text(p)
  if line not in s:
   b=next(b for b in pdx.top_level_blocks(s) if b.key==advance);s=s[:b.start]+b.text.replace('{','{\n\t'+line,1)+s[b.end:];pdx.write_text_bom(p,s)
 p=pdx.MOD_ROOT/'in_game/gfx/map/map_modes/tsin_map_modes.txt';s=pdx.read_text(p)
 if not any(b.key=='tsin_water_pollution' for b in pdx.top_level_blocks(s)):
  template=next(b.text for b in pdx.top_level_blocks(s) if b.key=='tsin_electrification');tail=template[template.index('\tsmall_map_names ='):]
  head='''tsin_water_pollution = {
 map_color = { if = { limit = { has_variable = tsin_pollution_year }
  lerp = { min_color = define:NMapColors|MAP_COLOR_LOW max_color = define:NMapColors|MAP_COLOR_MAX factor = tsin_water_pollution_factor }
 } else = { value = define:NMapColors|DEFAULT_COLOR } }
 tooltip_key = { value = TSIN_POLLUTION_MAPMODE_TT }
 legend_key = { desc = "LEGEND_TSIN_WATER_HIGH" color = define:NMapColors|MAP_COLOR_MAX }
 legend_key = { desc = "LEGEND_TSIN_WATER_LOW" color = define:NMapColors|MAP_COLOR_LOW }
 legend_key = { desc = "LEGEND_TSIN_WATER_UNKNOWN" color = define:NMapColors|DEFAULT_COLOR }
''';pdx.write_text_bom(p,s+'\n'+head+tail+'\n')
 p=pdx.MOD_ROOT/'ui/dashboard_registry.json';d=json.loads(pdx.read_text(p));d['modules']=[m for m in d['modules'] if m['id']!='environment']+[registry_module()];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();bad=[]
 for rel,text in build().items():
  p=pdx.MOD_ROOT/rel
  if a.check:
   if not p.exists() or pdx.read_text(p)!=text:bad.append(rel)
  elif rel.startswith('in_game/common/building_types/') and not p.exists():
   source=pdx.MOD_ROOT/'era_7'/rel;source.parent.mkdir(parents=True,exist_ok=True);source.write_text(text,encoding='utf-8-sig')
  else:pdx.write_text_bom(p,text)
 if not a.check:
  import sync_eras,era_layout
  sync_eras.register(pdx.MOD_ROOT);era_layout.sync(pdx.MOD_ROOT)
  for key,source in [('tsin_water_treatment_works',pdx.game_root()/'main_menu/gfx/interface/icons/buildings/hospital.dds'),('tsin_environment_inspectorate',pdx.content_path(pdx.MOD_ROOT/'main_menu/gfx/interface/icons/buildings/tsin_public_school.dds'))]:
   p=pdx.MOD_ROOT/f'era_7/main_menu/gfx/interface/icons/buildings/{key}.dds'
   if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(source.read_bytes())
  sync_eras.register(pdx.MOD_ROOT);era_layout.sync(pdx.MOD_ROOT)
  p=pdx.MOD_ROOT/'main_menu/gfx/interface/icons/map_modes/tsin_water_pollution.dds'
  if not p.exists():pdx.write_bytes(p,pdx.read_bytes(pdx.MOD_ROOT/'main_menu/gfx/interface/icons/map_modes/tsin_pollution.dds'))
  integrate()
 print('Environment:',len(bad),'differences');return bool(bad)
if __name__=='__main__':raise SystemExit(main())
