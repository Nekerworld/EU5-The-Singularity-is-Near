"""City-internal transit: weak steam pilot, electric upgrade; preserve railway assets."""
from pathlib import Path
import sys,argparse,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx

def build():
    buildings=[]
    for key,electric in [('tsin_steam_metro',False),('tsin_electric_metro',True)]:
        maximum=3 if electric else 1
        goods='tsin_electricity = 0.2 tools = 0.1 tsin_engines = 0.05' if electric else 'coal = 0.3 tools = 0.1 tsin_engines = 0.05'
        buildings.append(f'''{key} = {{
 audio_tier = 3 is_foreign = no pop_type = laborers forbidden_for_estates = yes
 employment_size = 0.1 max_levels = {maximum}
 category = infrastructure_category
 city = yes megalopolis = yes tsin_large_city = yes tsin_megalopolis = yes
 build_time = infrastructure_build_time
 construction_demand = tsin_factory_construction
 location_potential = {{ population >= 100 }}
 {'obsolete = tsin_steam_metro' if electric else ''}
 unique_production_methods = {{
  {key}_maintenance = {{ icon_type = goods icon = {'tsin_electricity' if electric else 'coal'}
   {goods}
   category = building_maintenance
  }}
 }}
 modifier = {{ local_population_capacity_modifier = {'0.05' if electric else '0.01'} }}
}}
''')
    outputs={'in_game/common/building_types/tsin_urban_transit.txt':'# City capacity only: does not create intercity railway connectivity.\n'+'\n'.join(buildings)}
    labels={'tsin_steam_metro':('증기 지하철 시범선','Steam metro pilot'),'tsin_electric_metro':('전기 지하철','Electric metro'),'tsin_steam_metro_desc':('인구 10만 이상 도시의 고비용 시범선입니다. 최대 1단계, 지역 수용력 +1%로 전기 지하철 1단계의 20% 효율입니다. 도시간 철도를 연결하지 않습니다. 시범선 제한은 게임 밸런스입니다.','A costly pilot in a city of at least 100,000. One level adds 1% local capacity, 20% of one electric metro level. Does not connect intercity railways. The pilot limit is a game-balance choice.'),'tsin_electric_metro_desc':('인구 10만 이상 도시의 전력 기반 교통시설입니다. 단계당 지역 수용력 +5%, 최대 3단계입니다. 증기 시범선을 대체하며 별도 도시 간 철도 연결을 만들지 않습니다.','Electric urban transit for cities of at least 100,000. Adds 5% local capacity per level, up to three. Replaces the steam pilot without creating intercity railway links.'),'AUTO_MODIFIER_NAME_tsin_connected_railway_station':('수도 연결 철도역','Capital-connected railway station')}
    for key in ['tsin_steam_metro','tsin_electric_metro']:labels[key+'_maintenance']=labels[key]
    for lang,i in [('korean',0),('english',1)]:outputs[f'main_menu/localization/{lang}/tsin_urban_transit_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {k}: '+json.dumps(v[i],ensure_ascii=False)+'\n' for k,v in labels.items())
    return {k: ''.join(line.rstrip()+chr(10) for line in v.splitlines()) for k,v in outputs.items()}

def integrate():
    # Existing track IDs and station assets remain. Disconnection disables benefits instead of deleting assets.
    p=pdx.MOD_ROOT/'in_game/common/building_types/tsin_railway_buildings.txt';s=pdx.read_text(p)
    b=next(b for b in pdx.top_level_blocks(s) if b.key=='tsin_railway_station')
    # Nested blocks are parsed from the definition body.
    nested=pdx.top_level_blocks(b.text[b.text.index('{')+1:-1])
    for key in ['remove_if','modifier']:
        target=next((n for n in nested if n.key==key),None)
        if target:s=s.replace(target.text,'# '+key+' moved to cached-free connection modifier; assets are retained.',1)
    pdx.write_text_bom(p,s)
    pdx.write_text_bom(pdx.MOD_ROOT/'in_game/common/auto_modifiers/tsin_railway_connection.txt','''tsin_connected_railway_station = {
 category = location type = location
 potential_trigger = {
  has_building_with_at_least_one_level = tsin_railway_station
  controller ?= owner
  OR = { is_capital = yes has_road_of_type_to = { target = owner.capital type = road_type:railroad } }
 }
 scales_with = "location_building_level(building_type:tsin_railway_station)"
 local_market_access = 0.075
}
''')
    for rel,advance,key in [('tsin_03_industrial_capitalism.txt','tsin_railway_networks_advance','tsin_steam_metro'),('tsin_06_electrification.txt','tsin_electric_motor_advance','tsin_electric_metro')]:
        p=pdx.MOD_ROOT/'in_game/common/advances'/rel;s=pdx.read_text(p)
        if 'unlock_building = '+key not in s:
            if advance not in [b.key for b in pdx.top_level_blocks(s)]:
                # Follow the actual railway station parent rather than guessing its spelling.
                advance=next(b.key for b in pdx.top_level_blocks(s) if 'unlock_building = tsin_railway_station' in b.text)
            b=next(b for b in pdx.top_level_blocks(s) if b.key==advance)
            s=s[:b.start]+b.text.replace('{','{\n\tunlock_building = '+key,1)+s[b.end:]
            pdx.write_text_bom(p,s)
    # Steam transit emits locally; electric consumption has no duplicate local fuel emissions.
    import gen_pollution
    p=pdx.MOD_ROOT/'tools/gen_pollution.py';s=p.read_text(encoding='utf-8')
    if "'tsin_steam_metro'" not in s:
        s=s.replace("HEAVY=['iron_mill'","HEAVY=['tsin_steam_metro','iron_mill'",1)
        p.write_text(s,encoding='utf-8')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();bad=[]
    for rel,text in build().items():
        p=pdx.MOD_ROOT/rel
        if a.check:
            if not p.exists() or pdx.read_text(p)!=text:bad.append(rel)
        else:
            source=pdx.content_path(p)
            if not p.exists() and source==p:
                source=pdx.MOD_ROOT/'era_7'/rel;source.parent.mkdir(parents=True,exist_ok=True);source.write_text(text,encoding='utf-8-sig')
            else:pdx.write_text_bom(p,text)
    if not a.check:
        import sync_eras,era_layout
        sync_eras.register(pdx.MOD_ROOT);era_layout.sync(pdx.MOD_ROOT)
        integrate()
        for key in ['tsin_steam_metro','tsin_electric_metro']:
            p=pdx.MOD_ROOT/f'main_menu/gfx/interface/icons/buildings/{key}.dds'
            if not p.exists():
                source=pdx.MOD_ROOT/'era_7'/p.relative_to(pdx.MOD_ROOT)
                source.parent.mkdir(parents=True,exist_ok=True)
                source.write_bytes(pdx.read_bytes(pdx.MOD_ROOT/'main_menu/gfx/interface/icons/buildings/tsin_railway_station.dds'))
        sync_eras.register(pdx.MOD_ROOT);era_layout.sync(pdx.MOD_ROOT)
    print('Urban transit:',len(bad),'differences');return bool(bad)
if __name__=='__main__':raise SystemExit(main())
