"""Extend the annual pollution pass without changing urban GDP/education denominators."""
import pdx

def refine_registry(module):
    for m in module['metrics']:
        m['title']['korean']=m['title']['korean'].replace('조사 도시','조사 지역')
        m['title']['english']=m['title']['english'].replace('Surveyed urban','Surveyed location')
        m['description']={'korean':'연간 조사 지역의 인구 가중 추정치입니다. 도시와 산업 시대의 광산을 포함하며 농촌 전체의 통계는 아닙니다. 발전 연료·도시간 교통 배출은 제외합니다.', 'english':'Annual population-weighted estimate for surveyed locations: urban areas and industrial-era mines, not every rural location. Excludes generation fuel and intercity transport emissions.'}
    for field,ko,en in [('water_exposure','조사 지역 인구 가중 수질 노출','Surveyed water exposure'),('water_high_share','조사 지역 수질 고위험 인구(%)','Surveyed high water exposure (%)')]:
        module['metrics'].append({'id':'pollution_'+field,'variable':'tsin_pollution_'+field,'title':{'korean':ko,'english':en},'tabs':['society'],'unit':'number','frequency':'annual','description':{'korean':'같은 연간 조사 지역 인구를 분모로 한 수질 지수입니다. 굴뚝 매연과 별도로 처리합니다.','english':'Water index using the same surveyed-location population denominator, separate from chimney emissions.'}})
    return module

def refine_pollution(outputs):
    outputs=dict(outputs)
    path='in_game/common/scripted_effects/tsin_pollution.txt';fx=outputs[path]
    if '# ENVIRONMENT_EXTENSION' in fx:return outputs
    fx='# ENVIRONMENT_EXTENSION\n'+fx
    fx=fx.replace(' set_variable = { name = tsin_pollution_raw_water value = 0 }',' set_variable = { name = tsin_pollution_raw_water value = 0 }\n set_variable = { name = tsin_pollution_treatment_capacity value = 0 }\n set_variable = { name = tsin_pollution_inspection_capacity value = 0 }',1)
    tick=next(b for b in pdx.top_level_blocks(fx) if b.key=='tsin_pollution_location_tick_effect')
    children=pdx.top_level_blocks(tick.text[tick.text.index('{')+1:-1]);buildings=next(b for b in children if b.key=='every_buildings_in_location')
    extra='''
  if = { limit = { building_type = building_type:tsin_water_treatment_works building_employment_size_amount > 0 is_lacking_goods = no }
   save_temporary_scope_value_as = { name = tsin_environment_capacity value = { value = building_employed_amount divide = building_employment_size_amount min = 0 max = 1 multiply = building_level } }
   scope:tsin_pollution_site = { change_variable = { name = tsin_pollution_treatment_capacity add = scope:tsin_environment_capacity } }
  }
  if = { limit = { building_type = building_type:tsin_environment_inspectorate building_employment_size_amount > 0 is_lacking_goods = no }
   save_temporary_scope_value_as = { name = tsin_environment_capacity value = { value = building_employed_amount divide = building_employment_size_amount min = 0 max = 1 } }
   scope:tsin_pollution_site = { change_variable = { name = tsin_pollution_inspection_capacity add = scope:tsin_environment_capacity } }
  }
'''
    fx=fx.replace(buildings.text,buildings.text[:-1]+extra+'}\n'+''' if = { limit = { tsin_is_polluting_mine = yes raw_material_output > 0 }
  change_variable = { name = tsin_pollution_raw_air add = { value = raw_material_output multiply = 0.08 } }
  change_variable = { name = tsin_pollution_raw_water add = { value = raw_material_output multiply = 0.10 } }
 }
''',1)
    fx=fx.replace(' set_variable = { name = tsin_pollution_year value = current_year }',''' set_variable = { name = tsin_pollution_year value = current_year }
 if = { limit = { var:tsin_pollution_water >= 60 }
  if = { limit = { NOT = { has_variable = tsin_pollution_water_bad_years } } set_variable = { name = tsin_pollution_water_bad_years value = 0 } }
  change_variable = { name = tsin_pollution_water_bad_years add = 1 }
 } else = { set_variable = { name = tsin_pollution_water_bad_years value = 0 } }
''',1)
    fx=fx.replace(' owner = { change_variable = { name = tsin_pollution_weighted add = scope:tsin_pollution_weighted } }',''' save_temporary_scope_value_as = { name = tsin_pollution_water_weighted value = { value = var:tsin_pollution_water multiply = population } }
 owner = {
  change_variable = { name = tsin_pollution_weighted add = scope:tsin_pollution_weighted }
  change_variable = { name = tsin_pollution_water_weighted add = scope:tsin_pollution_water_weighted }
  change_variable = { name = tsin_pollution_surveyed_pop add = scope:tsin_pollution_population }
 }
 if = { limit = { var:tsin_pollution_water >= 60 } owner = { change_variable = { name = tsin_pollution_water_high_pop add = scope:tsin_pollution_population } } }
''',1)
    fx=fx.replace('var:tsin_agg_urban_pop','var:tsin_pollution_surveyed_pop')
    finish=next(b for b in pdx.top_level_blocks(fx) if b.key=='tsin_pollution_finish_country_effect')
    fx=fx.replace(finish.text,finish.text[:-1]+' tsin_environment_finish_country_effect = yes\n}',1)
    outputs[path]="\n".join(line.rstrip() for line in fx.splitlines())+"\n"
    path='in_game/common/script_values/tsin_pollution.txt';s=outputs[path]
    replacements={
     'tsin_pollution_air_target':'''tsin_pollution_air_target = {
 value = var:tsin_pollution_raw_air
 if = { limit = { has_variable = tsin_pollution_filters } multiply = 0.65 }
 multiply = tsin_environment_air_retention
 min = 0 max = 100
}''',
     'tsin_pollution_water_target':'''tsin_pollution_water_target = {
 value = var:tsin_pollution_raw_water
 multiply = { value = 1 subtract = { value = var:tsin_pollution_treatment_capacity multiply = 0.30 } min = 0.40 max = 1 }
 multiply = tsin_environment_water_retention
 if = { limit = { has_variable = tsin_water_emergency_services } multiply = 0.85 }
 min = 0 max = 100
}'''}
    for b in pdx.top_level_blocks(s):
        if b.key in replacements:s=s.replace(b.text,replacements[b.key],1)
    outputs[path]=s
    for lang in ['korean','english']:
        path=f'main_menu/localization/{lang}/tsin_pollution_l_{lang}.yml'
        s=outputs[path].replace('발전소·채굴·교통 배출 미포함.','광산 RGO 산출·산업 고용 기반. 발전 연료·도시간 교통 배출 미포함.').replace('excludes power, extraction and transport.','includes mine output and industrial employment; excludes generation fuel and intercity transport.')
        outputs[path]=s
    return outputs

def transform_aggregate(s):
    if '# Environment extension:' in s:return '\n'.join(line.rstrip() for line in s.splitlines())+'\n'
    root=next(b for b in pdx.top_level_blocks(s) if b.key=='tsin_annual_country_aggregate_effect')
    children=pdx.top_level_blocks(root.text[root.text.index('{')+1:-1]);loop=next(b for b in children if b.key=='every_owned_location')
    inner=loop.text[loop.text.index('{')+1:-1];limit=next(b for b in pdx.top_level_blocks(inner) if b.key=='limit')
    urban=limit.text[limit.text.index('{')+1:-1]
    remainder=inner[:limit.start]+inner[limit.end:]
    remainder=remainder.replace('\t\ttsin_pollution_location_tick_effect = yes','',1)
    replacement='''every_owned_location = {
  # Environment extension: retain the original urban-only GDP/education/labor body.
  limit = { OR = {
'''+urban+'''
   tsin_is_polluting_mine = yes has_variable = tsin_pollution_year
  } }
  tsin_pollution_location_tick_effect = yes
  if = { limit = {
'''+urban+'\n }\n'+remainder+'\n }\n}'
    s=s.replace(loop.text,replacement,1)
    s=s.replace('set_variable = { name = tsin_pollution_weighted value = 0 }','''set_variable = { name = tsin_pollution_weighted value = 0 }
 set_variable = { name = tsin_pollution_surveyed_pop value = 0 }
 set_variable = { name = tsin_pollution_water_weighted value = 0 }
 set_variable = { name = tsin_pollution_water_high_pop value = 0 }''',1)
    return '\n'.join(line.rstrip() for line in s.splitlines())+'\n'
