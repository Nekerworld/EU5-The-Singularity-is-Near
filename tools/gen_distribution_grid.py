"""E1 local distribution assets, separate accessibility map and refrigeration bonus."""
from pathlib import Path
import sys,argparse,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx

def registry_module():
 return {'id':'distribution_grid','shortcuts':[{'id':'distribution_map','tab':'economy','title':{'korean':'전기 접근성 지도','english':'Electricity accessibility map'},'map_mode':'tsin_power_access'}]}

def build():
 building='''# Grid equipment, not a generator or independent electricity market.
tsin_distribution_substation = {
 audio_tier = 3 is_foreign = no pop_type = laborers forbidden_for_estates = yes
 employment_size = 0.02 max_levels = 3 category = infrastructure_category
 town = yes city = yes megalopolis = yes tsin_large_city = yes tsin_megalopolis = yes
 build_time = infrastructure_build_time construction_demand = tsin_infrastructure_construction
 country_potential = { has_advance = tsin_distribution_grid_advance }
 unique_production_methods = {
  tsin_distribution_substation_maintenance = {
   icon_type = goods icon = copper
   copper = 0.05 tools = 0.02 tsin_electricity = 0.02 category = building_maintenance
  }
 }
}
'''
 values='''# An equipment-coverage index, never additional physical electricity supply.
tsin_power_access_known = {
 value = 0
 if = { limit = { OR = { owner ?= { has_advance = tsin_distribution_grid_advance } has_building_with_at_least_one_level = tsin_distribution_substation has_building_with_at_least_one_level = tsin_power_station } } value = 1 }
}
tsin_power_access_index = {
 value = 0
 if = { limit = { tsin_power_access_known = 1 }
  value = 0.1
  add = { value = "location_building_level(building_type:tsin_distribution_substation)" multiply = 0.3 }
  max = 1
 }
}
tsin_grid_refrigeration_scale = {
 value = 0
 if = { limit = { any_buildings_in_location = { building_type = building_type:tsin_distribution_substation is_opened = yes building_employed_amount > 0 is_lacking_goods = no } any_buildings_in_location = { building_type = building_type:tsin_electric_cold_storage is_opened = yes building_employed_amount > 0 is_lacking_goods = no } }
  value = "location_building_level(building_type:tsin_electric_cold_storage)"
  multiply = tsin_power_access_index
  multiply = tsin_location_power_ratio
 }
}
'''
 auto='''tsin_grid_refrigeration = {
 category = location type = location
 potential_trigger = { has_building_with_at_least_one_level = tsin_electric_cold_storage controller ?= owner tsin_grid_refrigeration_scale > 0 }
 scales_with = tsin_grid_refrigeration_scale
 local_food_preservation_efficiency_modifier = 0.02
}
'''
 labels={'tsin_distribution_substation':(' 지역 배전 변전소'.strip(),'Local distribution substation'),'tsin_distribution_substation_maintenance':('배전 변전소 유지','Substation maintenance'),'tsin_distribution_substation_desc':('전기 접근성의 설비 지수에 단계당 30%p를 더합니다. 최대 3단계입니다. 실제로 가동되는 설비는 같은 지점의 전기 냉동 보관소 보존 효율을 최대 단계당 2%p 추가 지원합니다. 시장 전력을 새로 생산하거나 미연결 공장의 소비를 차단하지 않습니다.','Adds 30 percentage points of equipment coverage per level, up to three. An operating station adds up to 2pp preservation per electric cold-storage level in this location. Does not generate electricity or prohibit unconnected factories from buying it.'),'AUTO_MODIFIER_NAME_tsin_grid_refrigeration':('배전망 연계 냉동 보관','Grid-assisted refrigerated storage'),'mapmode_tsin_power_access_name':('전기 접근성','Electricity accessibility'),'MAPMODE_TSIN_POWER_ACCESS':('지역 배전 설비 보급 지수입니다. 시장 수급비와 다르며 미측정 지역은 회색입니다.','Local distribution equipment coverage. Separate from market supply adequacy. Unknown locations are grey.'),'TSIN_POWER_ACCESS_TT':("[ROOT.GetLocation.GetName]: 설비 지수 [ROOT.ScriptValue('tsin_power_access_index')|%0]. 소규모 설비 기반 10% + 변전소 단계당 30%p. 시장 전력 공급 [ROOT.ScriptValue('tsin_location_power_supply')|1], 수요 [ROOT.ScriptValue('tsin_location_power_demand')|1]. 설비 수준의 실시간 조회이며 별도 송전 회랑·전력 실물량이 아닙니다.","[ROOT.GetLocation.GetName]: equipment coverage [ROOT.ScriptValue('tsin_power_access_index')|%0]. Small-system base 10% + 30pp/substation level. Market supply [ROOT.ScriptValue('tsin_location_power_supply')|1], demand [ROOT.ScriptValue('tsin_location_power_demand')|1]. Live equipment query; does not represent a separate transmission corridor or physical electricity quantity."),'LEGEND_TSIN_POWER_ACCESS_HIGH':('배전 설비 보급','Distribution equipment coverage'),'LEGEND_TSIN_POWER_ACCESS_LOW':('소규모 설비','Small-scale equipment'),'LEGEND_TSIN_POWER_ACCESS_UNKNOWN':('자료 없음','Unknown')}
 outputs={'in_game/common/building_types/tsin_distribution_grid.txt':building,'in_game/common/script_values/tsin_distribution_grid.txt':values,'in_game/common/auto_modifiers/tsin_distribution_grid.txt':auto}
 for lang,i in [('korean',0),('english',1)]:outputs[f'main_menu/localization/{lang}/tsin_distribution_grid_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {k}: '+json.dumps(v[i],ensure_ascii=False)+'\n' for k,v in labels.items())
 return outputs

def integrate():
 p=pdx.MOD_ROOT/'in_game/common/advances/tsin_06_electrification.txt';s=pdx.read_text(p)
 if 'unlock_building = tsin_distribution_substation' not in s:
  b=next(b for b in pdx.top_level_blocks(s) if b.key=='tsin_distribution_grid_advance');s=s[:b.start]+b.text.replace('{','{\n\tunlock_building = tsin_distribution_substation',1)+s[b.end:];pdx.write_text_bom(p,s)
 p=pdx.MOD_ROOT/'in_game/gfx/map/map_modes/tsin_map_modes.txt';s=pdx.read_text(p)
 if not any(b.key=='tsin_power_access' for b in pdx.top_level_blocks(s)):
  b=next(b.text for b in pdx.top_level_blocks(s) if b.key=='tsin_electrification');tail=b[b.index('\tsmall_map_names ='):]
  header='''tsin_power_access = {
 map_color = { if = { limit = { tsin_power_access_known = 1 }
  lerp = { min_color = define:NMapColors|MAP_COLOR_LOW max_color = define:NMapColors|MAP_COLOR_MAX factor = tsin_power_access_index }
 } }
 tooltip_key = { value = TSIN_POWER_ACCESS_TT }
 legend_key = { desc = "LEGEND_TSIN_POWER_ACCESS_HIGH" color = define:NMapColors|MAP_COLOR_MAX }
 legend_key = { desc = "LEGEND_TSIN_POWER_ACCESS_LOW" color = define:NMapColors|MAP_COLOR_LOW }
 legend_key = { desc = "LEGEND_TSIN_POWER_ACCESS_UNKNOWN" color = define:NMapColors|MAP_COLOR_MIN }
'''
  pdx.write_text_bom(p,s+'\n'+header+tail+'\n')
 p=pdx.MOD_ROOT/'ui/dashboard_registry.json';d=json.loads(pdx.read_text(p));d['modules']=[m for m in d['modules'] if m['id']!='distribution_grid']+[registry_module()];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();bad=[]
 for rel,text in build().items():
  p=pdx.MOD_ROOT/rel
  if a.check:
   if not p.exists() or pdx.read_text(p)!=text:bad.append(rel)
  elif rel=='in_game/common/building_types/tsin_distribution_grid.txt' and not p.exists():
   source=pdx.MOD_ROOT/'era_7'/rel;source.parent.mkdir(parents=True,exist_ok=True);source.write_text(text,encoding='utf-8-sig')
  else:pdx.write_text_bom(p,text)
 if not a.check:
  import sync_eras,era_layout
  sync_eras.register(pdx.MOD_ROOT);era_layout.sync(pdx.MOD_ROOT)
  for rel,source in [('main_menu/gfx/interface/icons/buildings/tsin_distribution_substation.dds','main_menu/gfx/interface/icons/buildings/tsin_power_station.dds')]:
   p=pdx.MOD_ROOT/'era_7'/rel
   if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(pdx.read_bytes(pdx.MOD_ROOT/source))
  sync_eras.register(pdx.MOD_ROOT);era_layout.sync(pdx.MOD_ROOT)
  p=pdx.MOD_ROOT/'main_menu/gfx/interface/icons/map_modes/tsin_power_access.dds'
  if not p.exists():pdx.write_bytes(p,pdx.read_bytes(pdx.MOD_ROOT/'main_menu/gfx/interface/icons/map_modes/tsin_electrification.dds'))
  integrate()
 print('Distribution grid:',len(bad),'differences');return bool(bad)
if __name__=='__main__':raise SystemExit(main())
