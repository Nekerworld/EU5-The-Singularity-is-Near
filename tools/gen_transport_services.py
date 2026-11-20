"""Independent road/rail service hubs over preserved native links; no claimed second routing graph."""
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx
# key, era, parent, name KO/EN, family, predecessor, workers, upkeep, benefit
ROWS=[
 ('macadam',7,'modern_road_advance','마카담 도로 관리소','Macadam road service hub','road',None,'0.04','stone = 0.05 tools = 0.02','0.01'),
 ('tarmac',8,'tsin_motor_transport_advance','타르 마카담 도로 관리소','Tar-macadam road service hub','road','macadam','0.06','stone = 0.05 tsin_oil = 0.02 tools = 0.03','0.02'),
 ('asphalt',8,'tsin_tarmac_services_advance','아스팔트·콘크리트 도로 관리소','Asphalt/concrete road service hub','road','tarmac','0.08','stone = 0.08 tsin_oil = 0.03 tools = 0.04','0.03'),
 ('modern_road',9,'tsin_asphalt_services_advance','현대식 도로 관리소','Modern road service hub','road','asphalt','0.12','stone = 0.08 tsin_oil = 0.04 steel = 0.04 tools = 0.05','0.04'),
 ('double_track',7,'tsin_steel_rolling_stock_advance','복선철도 운용 거점','Double-track railway service hub','freight',None,'0.10','coal = 0.10 steel = 0.05 tools = 0.03 tsin_engines = 0.03','0.02'),
 ('heavy_freight',8,'tsin_double_track_services_advance','중량화물 철도 운용 거점','Heavy-freight railway service hub','freight','double_track','0.15','tsin_oil = 0.08 tsin_electricity = 0.15 steel = 0.08 tools = 0.05 tsin_engines = 0.05','0.04'),
 ('high_speed',9,'tsin_heavy_freight_services_advance','고속철도 여객 거점','High-speed passenger rail hub','passenger',None,'0.15','tsin_electricity = 0.30 steel = 0.05 tools = 0.08','0.03'),
 ('modern_rail',10,'tsin_high_speed_services_advance','현대식 철도 통합관제','Modern railway passenger control hub','passenger','high_speed','0.20','tsin_electricity = 0.40 steel = 0.05 tools = 0.10 copper = 0.05','0.05'),
 ('highway',8,'tsin_asphalt_services_advance','고속도로 교차·관리 거점','Highway interchange and service hub','highway',None,'0.20','tsin_oil = 0.10 steel = 0.05 tools = 0.10','0.02'),
 ('mature_metro',9,'tsin_high_speed_services_advance','성숙 지하철·광역급행 거점','Mature metro and urban express hub','metro',None,'0.15','tsin_electricity = 0.35 tools = 0.15 tsin_engines = 0.05','0.07'),
]
AGES={7:'age_7_industrialization',8:'age_8_world_wars',9:'age_9_atomic',10:'age_10_information'}
def key(name):return 'tsin_'+name+'_services'
def registry_module():
 return {'id':'transport_services','shortcuts':[{'id':'transport_buildings','tab':'economy','title':{'korean':'도로·철도 거점 건설','english':'Build road and railway service hubs'},'view':'buildings'}]}

def build():
 out={};autos=[];values=[];labels={};buildings={};advances={}
 for name,era,parent,ko,en,family,previous,workers,upkeep,bonus in ROWS:
  k=key(name);tech=k+'_advance'
  parents=[parent]
  if family=='road' and previous and key(previous)+'_advance' not in parents:parents.append(key(previous)+'_advance')
  if name=='heavy_freight':parents.append('tsin_motor_transport_advance')
  if family in ('passenger','metro'):parents.append('tsin_distribution_grid_advance')
  if name=='mature_metro':parents.append('tsin_electric_motor_advance')
  advances.setdefault(era,[]).append(f'''{tech} = {{
 age = {AGES[era]} icon = {'modern_road_advance' if family in ('road','highway') else 'railroad_advance'}
 {chr(10).join('requires = '+p for p in parents)}
 allow = {{ has_embraced_institution = institution:tsin_industrial_capitalism }}
 unlock_building = {k} ai_weight = {{ add = 10 }}
}}''')
  # Native connectivity is shared; these hubs do not create or replace a road_type.
  if family in ('road','highway'):
   connected='OR = { is_capital = yes has_road_to = owner.capital }'
  elif family in ('freight','passenger'):
   connected='has_building_with_at_least_one_level = tsin_railway_station OR = { is_capital = yes has_road_of_type_to = { target = owner.capital type = road_type:railroad } }'
  else:connected='always = yes'
  popgate='population >= 400' if family in ('highway','metro') else 'population >= 100' if family=='passenger' else 'population >= 30' if family=='road' else 'tsin_location_industrial_jobs > 0'
  extra=''
  if family=='highway':extra='OR = { has_building_with_at_least_one_level = tsin_asphalt_services has_building_with_at_least_one_level = tsin_modern_road_services }'
  # Entry needs the electric metro, or later levels of this hub once it stands (the electric metro becomes obsolete).
  if family=='metro':extra=f'OR = {{ has_building_with_at_least_one_level = tsin_electric_metro has_building_with_at_least_one_level = {k} }}'
  higher=[key(n) for n,e,p,kk,ee,ff,pp,*_ in ROWS if ff==family and pp==name]
  # Descendant checks prevent rebuilding an obsolete lower-grade hub.
  frontier=list(higher)
  while frontier:
   parent_key=frontier.pop()
   for n,e,p,kk,ee,ff,pp,*_ in ROWS:
    if pp and key(pp)==parent_key and key(n) not in higher:higher.append(key(n));frontier.append(key(n))
  lower_gate=' '.join('NOT = { has_building_with_at_least_one_level = '+h+' }' for h in higher)
  obsolete='obsolete = '+key(previous) if previous else 'obsolete = tsin_electric_metro' if family=='metro' else ''
  ranks='city = yes megalopolis = yes tsin_large_city = yes tsin_megalopolis = yes'+(' town = yes' if family in ('road','freight') else '')
  buildings.setdefault(era,[]).append(f'''{k} = {{
 audio_tier = 3 is_foreign = no forbidden_for_estates = yes
 pop_type = laborers employment_size = {workers} max_levels = {3 if family=='metro' else 1}
 category = infrastructure_category {ranks}
 build_time = infrastructure_build_time construction_demand = {'tsin_factory_construction' if family in ('highway','passenger','metro') else 'tsin_infrastructure_construction'}
 country_potential = {{ has_advance = {tech} }}
 location_potential = {{ {popgate} {connected} {extra} {lower_gate} }}
 {obsolete}
 ai_construct_weight = {{ value = 0 if = {{ limit = {{ owner ?= {{ gold >= {3000 if family in ('highway','passenger','metro') else 1500} }} {popgate} }} add = {5 if family in ('highway','passenger','metro') else 10} }} }}
 unique_production_methods = {{
  {k}_maintenance = {{
   icon_type = goods icon = tools {upkeep} category = building_maintenance
  }}
 }}
}}''')
  values.append(f'''{k}_staff_scale = {{
 value = 0
 every_buildings_in_location = {{ limit = {{ building_type = building_type:{k} is_opened = yes is_lacking_goods = no building_employment_size_amount > 0 }}
  add = {{ value = building_employed_amount divide = building_employment_size_amount min = 0 max = 1{' multiply = building_level' if family=='metro' else ''} }}
 }}
 min = 0 max = {3 if family=='metro' else 1}
}}''')
  effect=('local_population_capacity_modifier' if family in ('passenger','metro') else 'local_market_access')+' = '+bonus
  autos.append(f'''{k}_operation = {{
 category = location type = location
 potential_trigger = {{ controller ?= owner has_building_with_at_least_one_level = {k} {connected} }}
 scales_with = {k}_staff_scale {effect}
}}''')
  note_ko='바닐라 도로·철도를 보존하는 거점 시설입니다. 별도 선로·도로를 지도에 그리거나 실제 부대·교역 이동 경로를 바꾸지 않습니다. '
  note_en='A service hub over preserved native roads/railways. Does not draw a separate network or alter native army/trade routing. '
  if family in ('freight','passenger'):note_ko+='기존 철도역과 수도 철도 연결이 필요합니다. ';note_en+='Requires an existing station and a native rail connection to the capital. '
  if name=='heavy_freight':note_ko+='전기·디젤을 같은 현대화 단계로 묶으며 석유와 전력을 함께 쓰는 혼합 견인 유지비입니다. ';note_en+='Electric/diesel traction is one modernization package with explicit mixed oil/electricity upkeep. '
  if family=='passenger':note_ko+='화물 거점을 대체하지 않습니다. ';note_en+='Does not replace freight services. '
  if family=='metro':note_ko+='인구40만 이상에서 전기 지하철을 대체합니다. ';note_en+='Replaces electric metro in locations of at least 400,000 people. '
  note_ko+='휴업·투입 부족·적국 점령 시 보정이 없고, 부분 고용에 비례합니다. 단절되어도 시설은 철거하지 않습니다.'
  note_en+='Benefits require operation, inputs and owner control, and scale with effective staffing. Disconnection preserves the facility.'
  labels[k]=(ko,en);labels[k+'_desc']=(note_ko,note_en);labels[k+'_maintenance']=(ko+' 유지',en+' upkeep');labels[tech]=(ko+' 기술',en+' engineering');labels[tech+'_desc']=(note_ko,note_en);labels['AUTO_MODIFIER_NAME_'+k+'_operation']=(ko+' 운용',en+' operation')
 for era,texts in buildings.items():out[f'in_game/common/building_types/zz_tsin_transport_services_{era:02d}.txt']='\n'.join(texts)
 for era,texts in advances.items():out[f'in_game/common/advances/zz_tsin_transport_services_{era:02d}.txt']='\n'.join(texts)
 out['in_game/common/script_values/tsin_transport_services.txt']='\n'.join(values)
 out['in_game/common/auto_modifiers/tsin_transport_services.txt']='\n'.join(autos)
 for lang,i in [('korean',0),('english',1)]:out[f'main_menu/localization/{lang}/tsin_transport_services_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {k}: '+json.dumps(v[i],ensure_ascii=False)+'\n' for k,v in labels.items())
 return {k:'\n'.join(line.rstrip() for line in v.splitlines()).rstrip()+'\n' for k,v in out.items()}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();bad=[]
 if not a.check:
  p=pdx.MOD_ROOT/'data/content_modules.json';config=json.loads(pdx.read_text(p))
  for era in (9,10):
   folder=pdx.MOD_ROOT/f'era_{era}';folder.mkdir(exist_ok=True)
   if not (folder/'manifest.json').exists():(folder/'manifest.json').write_text(json.dumps({'schema_version':1,'files':{}},indent=2)+'\n',encoding='utf-8')
   if not any(m['id']==f'era_{era}' for m in config['modules']):config['modules'].append({'id':f'era_{era}','folder':f'era_{era}','era':era})
  p.write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
 for rel,text in build().items():
  p=pdx.MOD_ROOT/rel
  if a.check:
   if not p.exists() or pdx.read_text(p)!=text:bad.append(rel)
  elif '/building_types/' in rel or '/advances/' in rel:
   era=int(Path(rel).stem.rsplit('_',1)[-1]);source=pdx.MOD_ROOT/f'era_{era}'/rel;source.parent.mkdir(parents=True,exist_ok=True);source.write_text(text,encoding='utf-8-sig')
  else:pdx.write_text_bom(p,text)
 if not a.check:
  import sync_eras,era_layout
  for name,era,*_ in ROWS:
   icon=pdx.MOD_ROOT/f'era_{era}/main_menu/gfx/interface/icons/buildings/{key(name)}.dds';icon.parent.mkdir(parents=True,exist_ok=True)
   if not icon.exists():icon.write_bytes(pdx.read_bytes(pdx.MOD_ROOT/'main_menu/gfx/interface/icons/buildings/tsin_railway_station.dds'))
  sync_eras.register(pdx.MOD_ROOT);era_layout.sync(pdx.MOD_ROOT)
  p=pdx.MOD_ROOT/'ui/dashboard_registry.json';d=json.loads(pdx.read_text(p));d['modules']=[m for m in d['modules'] if m['id']!='transport_services']+[registry_module()];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  p=pdx.MOD_ROOT/'tools/gen_facility_aging.py';s=p.read_text(encoding='utf-8')
  if "'tsin_macadam_services'" not in s:s=s.replace("['tsin_railway_station','tsin_steam_metro'","["+','.join(repr(key(row[0])) for row in ROWS)+",'tsin_railway_station','tsin_steam_metro'",1);p.write_text(s,encoding='utf-8')
 print('Transport service hubs:',len(bad),'differences');return bool(bad)
if __name__=='__main__':raise SystemExit(main())
