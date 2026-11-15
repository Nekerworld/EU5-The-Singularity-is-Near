"""Concrete age-VIII continuations: battleships, motor logistics and aviation support.

Existing seven-era IDs and units are not replaced. Air power is ground support
through a capital facility and doctrine, not an invented native air-unit layer.
"""
import argparse,json
from pathlib import Path
import pdx


def build():
    loc={'english':{},'korean':{}}
    def label(id,en,ko,en_desc,ko_desc):
        loc['english'][id]=en;loc['korean'][id]=ko
        loc['english'][id+'_desc']=en_desc;loc['korean'][id+'_desc']=ko_desc
    advances=[]
    rows=[
        ('tsin_dreadnoughts_advance','military_tactics_advance_6',['tsin_pre_dreadnought_advance','tsin_naval_gunnery_advance'],'tsin_industrial_capitalism','unlock_unit = n_tsin_dreadnought',
         'All-big-gun battleships','노급 전함','Concentrate heavy guns and armor in a new coal-fired battleship design. Existing pre-dreadnoughts remain available.','중포와 장갑을 집중한 석탄 연료 전함을 설계합니다. 기존 전노급 전함도 계속 운용할 수 있습니다.'),
        ('tsin_oil_fired_battleships_advance','kor_gunpowder_engines',['tsin_dreadnoughts_advance','tsin_internal_combustion_advance'],'tsin_electrification','unlock_unit = n_tsin_oil_fired_dreadnought',
         'Oil-fired capital ships','중유 연료 주력함','An oil-fired design trades access to petroleum for speed and greater hull strength. It has its own construction and maintenance demands.','석유 공급을 전제로 속력과 선체를 강화한 전함입니다. 별도의 건조·유지 재화를 소비합니다.'),
        ('tsin_motor_transport_advance','kor_gunpowder_engines',['tsin_internal_combustion_advance'],'tsin_industrial_capitalism','unlock_building = tsin_motor_transport_depot',
         'Motor transport','자동차 운송','Establish motor depots supported by engines, oil and rubber for urban distribution and food storage.','엔진·석유·고무를 소비하는 자동차 물류 거점으로 도시 유통과 식량 저장을 지원합니다.'),
        ('tsin_motor_supply_columns_advance','army_country_movement_speed_advance',['tsin_motor_transport_advance','tsin_railway_mobilization_advance'],'tsin_industrial_capitalism','army_movement_speed = 0.05',
         'Motor supply columns','자동차 보급대','Coordinate road transport with railway mobilization to improve the movement of existing armies.','도로 운송과 철도 동원을 연계하여 기존 육군의 이동을 개선합니다.'),
        ('tsin_powered_flight_advance','scientific_revolution_advance',['tsin_internal_combustion_advance','tsin_practical_electrical_engineering_advance'],'tsin_electrification','unlock_building = tsin_capital_airfield',
         'Powered flight','동력 비행','Develop a capital aviation facility that consumes industrial supplies and assists army coordination.','산업 재화를 소비하며 육군의 지휘·연락을 지원하는 수도 항공 시설을 개발합니다.'),
        ('tsin_aerial_observation_advance','army_country_movement_speed_advance',['tsin_powered_flight_advance','tsin_general_staff_advance'],'tsin_electrification','combat_speed_modifier = 0.05',
         'Aerial observation doctrine','항공 관측 교리','Integrate aerial reports into staff planning and the coordination of existing ground battles.','항공 관측 보고를 참모부 계획과 기존 지상전의 지휘에 통합합니다.'),
    ]
    for id,icon,parents,institution,effect,en,ko,en_desc,ko_desc in rows:
        advances.append(f'''{id} = {{
age = age_8_world_wars
icon = {icon}
{''.join('requires = '+parent+chr(10) for parent in parents)}allow = {{ has_embraced_institution = institution:{institution} }}
{effect}
ai_weight = {{ add = 25 }}
}}''')
        label(id,en,ko,en_desc,ko_desc)
    units='''n_tsin_dreadnought = {
copy_from = n_tsin_pre_dreadnought
age = age_8_world_wars
buildable = yes
# Unit numeric stats are additive after copy_from. These are increments.
hull_size = 20
cannons = 20
movement_speed = 0.50
construction_demand = tsin_dreadnought_construction
maintenance_demand = tsin_dreadnought_maintenance
repair_demand = tsin_dreadnought_repair
}
n_tsin_oil_fired_dreadnought = {
copy_from = n_tsin_pre_dreadnought
age = age_8_world_wars
buildable = yes
# Same parent avoids adding another complete ship on top of the coal variant.
hull_size = 30
cannons = 25
movement_speed = 1
construction_demand = tsin_oil_dreadnought_construction
maintenance_demand = tsin_oil_dreadnought_maintenance
repair_demand = tsin_oil_dreadnought_repair
}
'''
    label('n_tsin_dreadnought','Dreadnought','노급 전함','A coal-fired all-big-gun battleship.','석탄 연료를 사용하는 중포 중심 전함입니다.')
    label('n_tsin_oil_fired_dreadnought','Oil-fired dreadnought','중유 연료 노급 전함','A faster capital ship requiring an oil supply.','석유 공급을 필요로 하는 고속 주력함입니다.')
    demands='''tsin_dreadnought_construction = {
steel = 14 tsin_engines = 4 cannons = 25 tools = 3 naval_supplies = 2 lumber = 20
category = ship_construction
}
tsin_dreadnought_maintenance = {
coal = 2 naval_supplies = 1.20 cannons = 2 liquor = 0.10 salt = 0.10
category = ship_maintenance
}
tsin_dreadnought_repair = {
steel = 2 tsin_engines = 0.40 tools = 0.50 naval_supplies = 0.40 lumber = 3
category = ship_repair
}
tsin_oil_dreadnought_construction = {
steel = 16 tsin_engines = 5 cannons = 28 tools = 3 naval_supplies = 2 lumber = 15 tsin_oil = 1
category = ship_construction
}
tsin_oil_dreadnought_maintenance = {
tsin_oil = 1.20 coal = 0.50 naval_supplies = 1.20 cannons = 2 liquor = 0.10 salt = 0.10
category = ship_maintenance
}
tsin_oil_dreadnought_repair = {
steel = 2.50 tsin_engines = 0.50 tools = 0.50 naval_supplies = 0.40 lumber = 2 tsin_oil = 0.10
category = ship_repair
}
'''
    buildings='''tsin_motor_transport_depot = {
audio_tier = 6 is_foreign = no forbidden_for_estates = yes pop_type = laborers
max_levels = 1 employment_size = generic_peasant_building_employment
category = infrastructure_category town = yes city = yes megalopolis = yes
build_time = infrastructure_build_time graphical_tags = { factory_large }
unique_production_methods = {
tsin_motor_depot_maintenance = {
icon_type = goods icon = tsin_engines
tsin_engines = 0.10 tsin_oil = 0.20 tsin_rubber = 0.10 tools = 0.05
category = building_maintenance
} }
construction_demand = tsin_factory_construction
modifier = { local_food_capacity = 1000 local_migration_attraction = 0.05 }
}
tsin_capital_airfield = {
audio_tier = 6 is_foreign = no forbidden_for_estates = yes pop_type = laborers
max_levels = 1 employment_size = generic_peasant_building_employment
category = infrastructure_category city = yes megalopolis = yes
potential = { is_capital = yes }
build_time = infrastructure_build_time graphical_tags = { factory_large }
unique_production_methods = {
tsin_airfield_maintenance = {
icon_type = goods icon = tsin_engines
tsin_engines = 0.10 tsin_oil = 0.20 tsin_rubber = 0.10 tools = 0.10
category = building_maintenance
} }
construction_demand = tsin_factory_construction
capital_country_modifier = { army_movement_speed = 0.02 }
}
'''
    label('tsin_motor_transport_depot','Motor transport depot','자동차 물류 거점','An urban depot consuming engines, oil and rubber, with increased food storage and migration attraction.','엔진·석유·고무를 소비하는 도시 물류 거점입니다. 식량 저장량과 이주 유인을 늘립니다.')
    label('tsin_capital_airfield','Capital aviation facility','수도 항공 시설','A single capital facility supports army coordination. Its industrial artwork and inherited ground-support mechanics are provisional.','수도에 건설하는 단일 항공 시설이 육군의 연락을 지원합니다. 산업 시설 그림과 지상군 지원 방식으로 표현합니다.')
    label('tsin_motor_depot_maintenance','Motor transport service','자동차 물류 운영','Maintain engines, fuel and rubber supplies.','엔진·연료·고무를 공급하여 물류 거점을 운영합니다.')
    label('tsin_airfield_maintenance','Aviation ground service','항공 지상 지원','Maintain aircraft engines, fuel and workshop supplies.','항공 엔진·연료·정비 재화를 공급합니다.')
    for id,en,ko in [('tsin_dreadnought_construction','Dreadnought construction','노급 전함 건조'),('tsin_dreadnought_maintenance','Dreadnought upkeep','노급 전함 유지'),('tsin_dreadnought_repair','Dreadnought repair','노급 전함 수리'),('tsin_oil_dreadnought_construction','Oil-fired dreadnought construction','중유 전함 건조'),('tsin_oil_dreadnought_maintenance','Oil-fired dreadnought upkeep','중유 전함 유지'),('tsin_oil_dreadnought_repair','Oil-fired dreadnought repair','중유 전함 수리')]:label(id,en,ko,en,ko)
    result={
        'in_game/common/advances/zz_tsin_08_transport_military.txt':'\n\n'.join(advances),
        'in_game/common/unit_types/zz_tsin_08_capital_ships.txt':units,
        'in_game/common/goods_demand/tsin_age8_capital_ship_demands.txt':demands,
        'in_game/common/building_types/tsin_age8_transport_buildings.txt':buildings,
    }
    for lang,entries in loc.items():result[f'main_menu/localization/{lang}/tsin_age8_transport_military_l_{lang}.yml']='l_'+lang+':\n'+'\n'.join(' '+k+': '+json.dumps(v,ensure_ascii=False) for k,v in entries.items())
    return {k:'\n'.join(line.rstrip() for line in v.splitlines())+'\n' for k,v in result.items()}


def assets():
    return {f'main_menu/gfx/interface/icons/buildings/{new}.dds':pdx.read_bytes(pdx.MOD_ROOT/f'main_menu/gfx/interface/icons/buildings/{old}.dds')
            for new,old in [('tsin_motor_transport_depot','tsin_power_station'),('tsin_capital_airfield','tsin_machine_works')]}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    result={**build(),**assets()};bad=[]
    for rel,value in result.items():
        path=pdx.MOD_ROOT/'era_8'/rel
        expected=value if isinstance(value,bytes) else value.encode('utf-8-sig')
        if args.check:
            if not path.exists() or (pdx.read_bytes(pdx.MOD_ROOT/rel)!=value if isinstance(value,bytes) else pdx.read_text(pdx.MOD_ROOT/rel)!=value):bad.append(rel)
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(expected)
    if not args.check:
        import sync_eras,era_layout
        sync_eras.register(pdx.MOD_ROOT);era_layout.sync(pdx.MOD_ROOT)
    print(f'Age VIII transport and military: {len(result)} files, {len(bad)} mismatches')
    for rel in bad:print(rel)
    return bool(bad)


if __name__=='__main__':raise SystemExit(main())
