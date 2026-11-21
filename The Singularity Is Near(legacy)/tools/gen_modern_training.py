"""H2: modern field drill ability, age VIII/IX six-category land units and their templates.

Vanilla UnitTemplate and drill_army are kept; the ability is patterned on drill_army.
Six categories map onto the existing unit categories (A plan): recon armor (light cavalry),
tanks (heavy cavalry), mountain/paratroopers (light infantry), mechanized infantry (heavy
infantry), self-propelled/rocket artillery (artillery), motor transport (auxiliary).
Search result before adding: no age VIII/IX land unit existed in era_8/era_9 or in_game.
All units are buildable = yes so the AI can recruit them. 사용자 확인 필요 (docs/h0_engine_probes.md).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h_track_common as common  # noqa: E402
import pdx  # noqa: E402

E8, E9 = 'era_8', 'era_9'

# Age VIII templates (absolute values, like the age VII ladder in tsin_00_age_templates.txt).
TEMPLATES = {
    'light_infantry': ('a_light_infantry', {'max_strength': 4.0, 'combat_power': 4.5}),
    'heavy_infantry': ('a_heavy_infantry', {'max_strength': 4.0, 'combat_power': 4.5}),
    'light_cavalry': ('a_light_cavalry', {'max_strength': 1.4, 'combat_power': 4.0}),
    'heavy_cavalry': ('a_heavy_cavalry', {'max_strength': 1.4, 'combat_power': 4.0}),
    'auxiliary': (None, {'category': 'army_auxiliary', 'max_strength': 0.3, 'combat_power': 0.35}),
    'artillery': (None, {'category': 'army_artillery', 'max_strength': 2.0, 'combat_power': 11.5,
                         'bombard_efficiency': 0.50, 'artillery_barrage': 13}),
}

# id -> (stat increments after copy_from, gfx_tags or None, construction goods, maintenance goods)
UNIT_DATA_08 = {
    'a_tsin_armored_car_recon': (
        {'initiative': 6, 'combat_power': 0.5, 'movement_speed': 1.5}, None,
        {'tsin_engines': 0.8, 'steel': 0.6, 'tsin_rubber': 0.2, 'firearms': 0.3},
        {'tsin_oil': 0.10, 'tsin_rubber': 0.05, 'firearms': 0.20}),
    'a_tsin_tank_battalion': (
        {'combat_power': 3.0, 'initiative': 2, 'movement_speed': 0.5}, None,
        {'steel': 2.0, 'tsin_engines': 1.0, 'cannons': 1.0, 'tools': 0.4},
        {'tsin_oil': 0.30, 'steel': 0.05, 'cannons': 0.20}),
    'a_tsin_mountain_paratroopers': (
        {'initiative': 4, 'flanking_ability': 0.3, 'combat_power': 0.5}, 'rifle_tag light_tag',
        {'firearms': 1.5, 'tools': 0.2, 'leather': 0.2},
        {'firearms': 0.50, 'tsin_explosives': 0.05}),
    'a_tsin_mechanized_infantry': (
        {'combat_power': 1.0, 'movement_speed': 1.0}, 'rifle_tag medium_tag',
        {'firearms': 1.2, 'tsin_engines': 0.5, 'steel': 0.5, 'tsin_rubber': 0.2},
        {'firearms': 0.40, 'tsin_oil': 0.15}),
    'a_tsin_self_propelled_battery': (
        {'combat_power': 1.5, 'artillery_barrage': 3, 'movement_speed': 1.0}, None,
        {'cannons': 1.8, 'steel': 1.5, 'tsin_engines': 0.8},
        {'cannons': 0.60, 'tsin_explosives': 0.30, 'tsin_oil': 0.15}),
    'a_tsin_motor_supply_column': (
        {'movement_speed': 1.5}, None,
        {'tsin_engines': 0.6, 'steel': 0.3, 'tsin_rubber': 0.3},
        {'tsin_oil': 0.20, 'tsin_rubber': 0.05}),
}
UNIT_DATA_09 = {
    'a_tsin_main_battle_tank': (
        {'combat_power': 2.0, 'initiative': 1, 'movement_speed': 0.5}, None,
        {'steel': 2.5, 'tsin_engines': 1.4, 'cannons': 1.2, 'tools': 0.5, 'copper': 0.3},
        {'tsin_oil': 0.35, 'steel': 0.05, 'cannons': 0.25}),
    'a_tsin_rocket_artillery_battery': (
        {'artillery_barrage': 4, 'bombard_efficiency': 0.05, 'combat_power': 1.0}, None,
        {'cannons': 1.2, 'tsin_explosives': 1.2, 'steel': 1.2, 'tsin_engines': 0.8},
        {'cannons': 0.40, 'tsin_explosives': 0.50, 'tsin_oil': 0.15}),
}

ADVANCES_08 = [
    # id, icon, parents, institution, effect, en, ko, en_desc, ko_desc
    ('tsin_modern_field_drill_advance', 'drill_army_advance',
     ['tsin_general_staff_advance', 'tsin_mass_production_arms_advance'], 'tsin_industrial_capitalism',
     'unlock_ability = tsin_modern_field_drill',
     'Modern field drill', '현대식 야전 훈련',
     'Combined-arms exercises with live ammunition. Unlocks the Modern Field Drill order for armies.',
     '실탄과 차량을 쓰는 합동 훈련입니다. 군대에 현대식 야전 훈련 명령을 해금합니다.'),
    ('tsin_armored_cars_advance', 'army_country_movement_speed_advance',
     ['tsin_motor_supply_columns_advance', 'tsin_mass_production_arms_advance'], 'tsin_industrial_capitalism',
     'unlock_unit = a_tsin_armored_car_recon',
     'Armored cars', '장갑차 정찰',
     'Armored cars take over the reconnaissance role of light cavalry.', '장갑차가 경기병의 정찰 역할을 대신합니다.'),
    ('tsin_tank_warfare_advance', 'military_tactics_advance_6',
     ['tsin_armored_cars_advance', 'tsin_armored_vehicle_industry_advance'], 'tsin_industrial_capitalism',
     'unlock_unit = a_tsin_tank_battalion',
     'Tank warfare', '전차전',
     'Tank battalions replace heavy cavalry as the shock arm. They burn oil and consume armored vehicle stocks.',
     '전차 대대가 중기병을 대신하는 돌파 병종이 됩니다. 석유와 기갑 차량 비축을 소비합니다.'),
    ('tsin_airborne_infantry_advance', 'scientific_revolution_advance',
     ['tsin_powered_flight_advance', 'tsin_mass_production_arms_advance'], 'tsin_electrification',
     'unlock_unit = a_tsin_mountain_paratroopers',
     'Mountain and airborne infantry', '산악·공정 보병',
     'Elite light infantry trained for mountains and air landings.', '산악전과 공중 강하를 훈련한 정예 경보병입니다.'),
    ('tsin_mechanized_infantry_advance', 'army_country_movement_speed_advance',
     ['tsin_motor_supply_columns_advance', 'tsin_armored_vehicle_industry_advance'], 'tsin_industrial_capitalism',
     'unlock_unit = a_tsin_mechanized_infantry',
     'Mechanized infantry', '기계화 보병',
     'Heavy infantry carried by trucks and half-tracks. Needs fuel.', '트럭과 반궤도 차량에 탑승하는 중보병입니다. 연료가 필요합니다.'),
    ('tsin_self_propelled_artillery_advance', 'kor_gunpowder_engines',
     ['tsin_tank_warfare_advance', 'tsin_mechanized_infantry_advance'], 'tsin_industrial_capitalism',
     'unlock_unit = a_tsin_self_propelled_battery',
     'Self-propelled artillery', '자주포',
     'Guns mounted on tracked chassis keep pace with the armored columns.', '궤도 차체에 포를 얹어 기갑 부대와 함께 이동합니다.'),
    ('tsin_motor_supply_column_advance', 'army_country_movement_speed_advance',
     ['tsin_motor_supply_columns_advance'], 'tsin_industrial_capitalism',
     'unlock_unit = a_tsin_motor_supply_column',
     'Motor transport companies', '차량화 수송대',
     'Truck companies replace wagon trains. They need fuel and rubber.', '트럭 수송대가 마차 수송대를 대신합니다. 연료와 고무가 필요합니다.'),
]
ADVANCES_09 = [
    ('tsin_main_battle_tank_advance', 'military_tactics_advance_6',
     ['tsin_tank_warfare_advance', 'tsin_mechanized_infantry_advance'], 'tsin_industrial_capitalism',
     'unlock_unit = a_tsin_main_battle_tank',
     'Main battle tank', '주력 전차',
     'A balanced tank with better armor and engines replaces the early tank battalion.', '장갑과 엔진이 개선된 범용 전차가 초기 전차 대대를 대신합니다.'),
    ('tsin_rocket_artillery_advance', 'kor_gunpowder_engines',
     ['tsin_self_propelled_artillery_advance', 'tsin_aircraft_industry_advance'], 'tsin_industrial_capitalism',
     'unlock_unit = a_tsin_rocket_artillery_battery',
     'Rocket artillery', '로켓 포병',
     'Truck-mounted rocket batteries deliver a heavy barrage.', '트럭에 실은 로켓 포대가 강력한 일제 사격을 가합니다.'),
]

UNIT_TEXT = {
    'a_tsin_armored_car_recon': ('Armored car recon', '장갑차 정찰대', 'Fast reconnaissance unit in the light cavalry category.', '경기병 범주의 고속 정찰 부대입니다.'),
    'a_tsin_tank_battalion': ('Tank battalion', '전차 대대', 'Shock unit in the heavy cavalry category. Needs oil and cannons.', '중기병 범주의 돌파 부대입니다. 석유와 화포가 필요합니다.'),
    'a_tsin_mountain_paratroopers': ('Mountain and airborne infantry', '산악·공정 보병', 'Elite light infantry with high initiative.', '주도권이 높은 정예 경보병입니다.'),
    'a_tsin_mechanized_infantry': ('Mechanized infantry', '기계화 보병', 'Motorized heavy infantry. Needs firearms and oil.', '차량화된 중보병입니다. 총기와 석유가 필요합니다.'),
    'a_tsin_self_propelled_battery': ('Self-propelled battery', '자주포 포대', 'Mobile artillery with a stronger barrage.', '기동력을 갖춘 강력한 포병입니다.'),
    'a_tsin_motor_supply_column': ('Motor supply column', '차량화 수송대', 'Auxiliary truck column that needs oil and rubber.', '석유와 고무가 필요한 보조 트럭 수송대입니다.'),
    'a_tsin_main_battle_tank': ('Main battle tank', '주력 전차', 'Late tank that improves on the tank battalion.', '전차 대대보다 개량된 후기 전차입니다.'),
    'a_tsin_rocket_artillery_battery': ('Rocket artillery battery', '로켓 포병 포대', 'Truck-mounted rocket launchers.', '트럭에 실은 로켓 발사기입니다.'),
}


def fmt(v):
    return ('%g' % v)


def templates():
    out = ['# Age VIII land templates (H2), continuing tsin_00_age_templates.txt. Hidden; real units copy_from them.']
    for key, (base, stats) in TEMPLATES.items():
        lines = [f'a_age_8_world_wars_{key} = {{']
        if base:
            lines.append(f'\tcopy_from = {base}')
        lines += ['\thide = yes', '\tbuildable = no']
        for k, v in stats.items():
            lines.append(f'\t{k} = {v}' if isinstance(v, str) else f'\t{k} = {fmt(v)}')
        lines += ['\tage = "age_8_world_wars"', '}']
        out.append('\n'.join(lines))
    return '\n\n'.join(out) + '\n'


def unit_block(uid, parent, age, data, demand_prefix):
    stats, tags, _, _ = data
    lines = [f'{uid} = {{', f'\tcopy_from = {parent}', '\tbuildable = yes', '\thide = no']
    if age:
        lines.append(f'\tage = "{age}"')
    lines += [f'\t{k} = {fmt(v)}' for k, v in stats.items()]
    lines += ['', f'\tmaintenance_demand = {demand_prefix}_maintenance', f'\tconstruction_demand = {demand_prefix}_construction']
    if tags:
        lines += ['', f'\tgfx_tags = {{ {tags} }}']
    lines.append('}')
    return '\n'.join(lines)


def demand_name(uid):
    return uid.replace('a_tsin_', 'tsin_h2_')


def units_08():
    out = ['# Age VIII land units (H2). Stats after copy_from are increments (same convention as tsin_age7_units.txt; 사용자 확인 필요).']
    for uid, role, key, adv in common.UNITS_08:
        out.append(unit_block(uid, f'a_age_8_world_wars_{key}', None, UNIT_DATA_08[uid], demand_name(uid)))
    return '\n\n'.join(out) + '\n'


def units_09():
    out = ['# Age IX land units (H2): improvements of the age VIII units. Increments after copy_from.']
    for uid, role, parent, adv in common.UNITS_09:
        out.append(unit_block(uid, parent, 'age_9_atomic', UNIT_DATA_09[uid], demand_name(uid)))
    return '\n\n'.join(out) + '\n'


def demands(table, header):
    out = [header]
    for uid, data in table.items():
        _, _, cons, maint = data
        d = demand_name(uid)
        out.append(f'{d}_construction = {{\n' + ''.join(f'\t{g} = {v}\n' for g, v in cons.items()) + '\tcategory = regiment_construction\n}')
        out.append(f'{d}_maintenance = {{\n' + ''.join(f'\t{g} = {v}\n' for g, v in maint.items()) + '\tcategory = regiment_maintenance\n}')
    return '\n\n'.join(out) + '\n'


def advance_blocks(rows, age):
    out = []
    for aid, icon, parents, inst, effect, *_ in rows:
        req = ''.join(f'\trequires = {p}\n' for p in parents)
        out.append(f'{aid} = {{\n\tage = {age}\n\ticon = {icon}\n\n{req}\tallow = {{ has_embraced_institution = institution:{inst} }}\n\n\t{effect}\n\tai_weight = {{ add = 15 }}\n}}')
    return '\n\n'.join(out) + '\n'


def unit_triggers():
    def types(role):
        ids = [u[0] for u in common.UNITS_08 + common.UNITS_09 if u[1] == role]
        return '\n'.join(f'\t\tsub_unit_type = unit_type:{i}' for i in ids)
    return f'''# H2 unit role sets (sub_unit scope). Used by the H1 counters and the H3 fuel penalties.
tsin_h_unit_infantry_trigger = {{
	OR = {{
		sub_unit_category = sub_unit_category:army_light_infantry
		sub_unit_category = sub_unit_category:army_heavy_infantry
	}}
}}

tsin_h_unit_artillery_trigger = {{
	sub_unit_category = sub_unit_category:army_artillery
}}

# Heavy armor: tanks and armored cars.
tsin_h_unit_armored_trigger = {{
	OR = {{
{types('armored')}
	}}
}}

# Motorized units: mechanized infantry, self-propelled/rocket artillery, motor transport.
tsin_h_unit_motorized_trigger = {{
	OR = {{
{types('motorized')}
	}}
}}

tsin_h_unit_fuel_user_trigger = {{
	OR = {{
		tsin_h_unit_armored_trigger = yes
		tsin_h_unit_motorized_trigger = yes
	}}
}}
'''


def ability():
    return '''# H2: modern field drill, patterned on vanilla drill_army (unlocked by tsin_modern_field_drill_advance).
# More experience than drill_army, bigger upkeep and morale cost; ends at the first combat, move or siege.
tsin_modern_field_drill = {
	duration = -1
	toggle = yes
	army_only = yes
	cancel_on_combat = yes
	cancel_on_combat_end = yes
	cancel_on_move = yes
	animation_gfx_override = 1

	map = yes

	allow = {
		has_only_prisoners = no
		is_army = yes
		in_combat = no
		is_moving = no
		is_exiled = no
		in_siege = no
		has_commander = yes
		# Needs a non-negative small arms stockpile once the H1 system has started (사용자 확인 필요).
		owner = {
			OR = {
				NOT = { has_variable = tsin_h_init }
				var:tsin_eq_small_arms_stockpile >= 0
			}
		}
	}

	modifier = {
		monthly_experience_gain = 3.5
		force_army_maintenance = yes
		army_maintenance_efficiency = -0.40
		land_morale_modifier = -0.9
	}

	finished_when = {
		OR = {
			in_combat = yes
			is_moving = yes
			is_exiled = yes
			in_siege = yes
			has_commander = no
		}
	}

	ai_will_do = {
		value = -1
	}

	ai_will_revoke = {
		value = 1
	}
}
'''


def localization(table_advances, units, era_name):
    loc = common.Loc()
    for aid, _, _, _, _, en, ko, en_desc, ko_desc in table_advances:
        loc.add(aid, en, ko, en_desc, ko_desc)
    for uid in units:
        en, ko, en_desc, ko_desc = UNIT_TEXT[uid]
        loc.add(uid, en, ko, en_desc, ko_desc)
    return loc


def build():
    out = {
        f'{E8}/in_game/common/advances/zzz_tsin_08_h2_training_units.txt':
            '# H2 (HOI4 hybrid military). 사용자 확인 필요: all advances, units and the drill ability are untested in game.\n' + advance_blocks(ADVANCES_08, 'age_8_world_wars'),
        f'{E8}/in_game/common/unit_types/zzz_tsin_08_h2_a_templates.txt': templates(),
        f'{E8}/in_game/common/unit_types/zzz_tsin_08_h2_b_units.txt': units_08(),
        f'{E8}/in_game/common/goods_demand/tsin_age8_h2_land_demands.txt':
            demands(UNIT_DATA_08, '# Age VIII land unit goods (H2). Existing goods only: firearms, cannons, steel, engines, oil, rubber.'),
        f'{E8}/in_game/common/scripted_triggers/zzz_tsin_h2_unit_triggers.txt': unit_triggers(),
        f'{E8}/in_game/common/unit_abilities/tsin_modern_field_drill.txt': ability(),
        f'{E9}/in_game/common/advances/zzz_tsin_09_h2_units.txt':
            '# H2 age IX unit advances (HOI4 hybrid military). 사용자 확인 필요.\n' + advance_blocks(ADVANCES_09, 'age_9_atomic'),
        f'{E9}/in_game/common/unit_types/zzz_tsin_09_h2_units.txt': units_09(),
        f'{E9}/in_game/common/goods_demand/tsin_age9_h2_land_demands.txt':
            demands(UNIT_DATA_09, '# Age IX land unit goods (H2).'),
    }
    loc8 = localization(ADVANCES_08, [u[0] for u in common.UNITS_08], E8)
    loc8.add('tsin_modern_field_drill', 'Modern Field Drill', '현대식 야전 훈련',
             'Combined-arms exercises raise experience far faster than drilling, at the price of heavy upkeep and lower morale. Ends when the army fights, moves or besieges.',
             '합동 훈련으로 일반 훈련보다 훨씬 빨리 경험을 쌓지만 유지비가 크고 사기가 떨어집니다. 전투·이동·공성이 시작되면 끝납니다.')
    loc8.raw('tsin_modern_field_drill_cta', 'Click to start the modern field drill.', '클릭하여 현대식 야전 훈련을 시작합니다.')
    out.update(loc8.files(E8, 'tsin_h2_training'))
    out.update(localization(ADVANCES_09, [u[0] for u in common.UNITS_09], E9).files(E9, 'tsin_h2_age9'))
    return {k: common.tidy(v) for k, v in out.items()}


def assets():
    rel = 'main_menu/gfx/interface/icons/unit_ability/tsin_modern_field_drill.dds'
    existing = common.ROOT / E8 / rel
    game = pdx.game_root() / 'main_menu/gfx/interface/icons/unit_ability/drill_army.dds'
    if existing.is_file():
        data = existing.read_bytes()
    else:
        data = game.read_bytes()
    return {f'{E8}/{rel}': data}


def main(argv=None):
    return common.run('H2 modern training and units', {**build(), **assets()}, argv)


if __name__ == '__main__':
    raise SystemExit(main())
