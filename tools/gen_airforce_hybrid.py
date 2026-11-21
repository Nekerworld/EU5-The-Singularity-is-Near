"""H4: hybrid air force - regional airbases, anti-air, four aircraft stockpiles and wartime area operations.

Preserved: building tsin_capital_airfield, advances tsin_powered_flight_advance and
tsin_aerial_observation_advance (not edited here; the airfield only adds to air capacity).
Added: tsin_aircraft_industry_advance (unlocks the H1 aircraft works), tsin_regional_airbase_advance
(tsin_airbase), tsin_anti_aircraft_advance (tsin_anti_air_battery), tsin_air_operations_advance.
No radar building in this slice (listed as remaining work in docs/military_hybrid_h_track.md).

Aircraft pool (H1 var:tsin_eq_aircraft_stockpile) is split monthly into fighter / close air support /
bomber / transport stockpiles up to airbase capacity. Wartime monthly operations (only at_war = yes
countries) use province targets chosen with generic_actions. Area targeting: looking_for_a = area is
not used anywhere else in this mod, so province targeting is used (Area is 사용자 확인 필요).
Conservative placeholders; all behavior is 사용자 확인 필요 (docs/h0_engine_probes.md).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h_track_common as common  # noqa: E402

ERA = 'era_8'
TYPES = [('fighter', 'Fighters', '전투기', 0.35), ('cas', 'Close air support aircraft', '근접지원기', 0.30),
         ('bomber', 'Bombers', '폭격기', 0.15), ('transport', 'Transport aircraft', '수송기', 0.20)]
MISSIONS = [  # key, aircraft stock, enemy-only target, en, ko
    ('superiority', 'fighter', False, 'Air superiority', '제공권'),
    ('cas', 'cas', True, 'Close air support', '근접항공지원'),
    ('bombing', 'bomber', True, 'Strategic bombing', '전략 폭격'),
    ('supply', 'transport', False, 'Air supply', '공수 보급'),
]

ADVANCES = [
    ('tsin_aircraft_industry_advance', 'scientific_revolution_advance',
     ['tsin_powered_flight_advance', 'tsin_mass_production_arms_advance'], 'tsin_electrification',
     ['unlock_building = tsin_aircraft_works'],
     'Aircraft industry', '항공기 산업',
     'Series production of airframes and engines. Unlocks the aircraft works; its output fills the national aircraft pool.',
     '기체와 엔진의 양산 체제입니다. 항공기 공장을 해금하며 산출은 국가 항공기 풀에 쌓입니다.'),
    ('tsin_regional_airbase_advance', 'scientific_revolution_advance',
     ['tsin_aircraft_industry_advance'], 'tsin_electrification',
     ['unlock_building = tsin_airbase'],
     'Regional airbases', '지역 비행장',
     'Airbases outside the capital raise the number of aircraft the country can keep.', '수도 밖의 비행장으로 보유할 수 있는 항공기 수를 늘립니다.'),
    ('tsin_anti_aircraft_advance', 'military_tactics_advance_6',
     ['tsin_aircraft_industry_advance'], 'tsin_industrial_capitalism',
     ['unlock_building = tsin_anti_air_battery'],
     'Anti-aircraft artillery', '대공포',
     'Guns and searchlights protect a location: attackers lose aircraft and do less damage.', '대공포와 탐조등이 지역을 지킵니다. 공격 항공기는 손실이 늘고 피해가 줄어듭니다.'),
    ('tsin_air_operations_advance', 'army_country_movement_speed_advance',
     ['tsin_regional_airbase_advance', 'tsin_aerial_observation_advance'], 'tsin_electrification',
     ['military_tactics = 0.1'],
     'Air operations', '항공 작전',
     'Joint air-ground planning. Allows assigning air superiority, close support, strategic bombing and air supply to provinces.',
     '공지 합동 계획입니다. 제공권·근접지원·전략 폭격·공수 보급 임무를 지방에 배정할 수 있습니다.'),
]

BUILDINGS = {
    'tsin_airbase': dict(advance='tsin_regional_airbase_advance', maintenance={'tsin_engines': 0.08, 'tsin_oil': 0.15, 'tsin_rubber': 0.05, 'tools': 0.08},
                         icon='tsin_engines', art='tsin_capital_airfield',
                         en='Regional airbase', ko='지역 비행장',
                         en_desc='Each level adds room for 12 aircraft and fuel storage. Needs engines, oil, rubber and tools.',
                         ko_desc='단계마다 항공기 12대의 수용 한도와 연료 저장고가 늘어납니다. 엔진·석유·고무·도구가 필요합니다.'),
    'tsin_anti_air_battery': dict(advance='tsin_anti_aircraft_advance', maintenance={'cannons': 0.10, 'tsin_explosives': 0.05, 'steel': 0.05, 'tools': 0.05},
                                  icon='cannons', art='tsin_blasting_works',
                                  en='Anti-aircraft battery', ko='대공포대',
                                  en_desc='Enemy aircraft over this location suffer extra losses and deal less damage. Needs cannons, explosives, steel and tools.',
                                  ko_desc='이 지역 상공의 적 항공기는 손실이 늘고 피해가 줄어듭니다. 화포·폭약·강철·도구가 필요합니다.'),
}


def advances():
    out = ['# H4 (HOI4 hybrid military). tsin_capital_airfield / tsin_powered_flight_advance / tsin_aerial_observation_advance are preserved elsewhere.',
           '# 사용자 확인 필요: untested in game.']
    for aid, icon, parents, inst, effects_, *_ in ADVANCES:
        req = ''.join(f'\trequires = {p}\n' for p in parents)
        eff = ''.join(f'\t{e}\n' for e in effects_)
        out.append(f'{aid} = {{\n\tage = age_8_world_wars\n\ticon = {icon}\n\n{req}\tallow = {{ has_embraced_institution = institution:{inst} }}\n\n{eff}\tai_weight = {{ add = 15 }}\n}}')
    return '\n\n'.join(out) + '\n'


def buildings():
    out = ['# H4 regional airbase and anti-air stubs. Same infrastructure pattern as tsin_capital_airfield.']
    for bid, d in BUILDINGS.items():
        maint = ' '.join(f'{g} = {v}' for g, v in d['maintenance'].items())
        out.append(f'''{bid} = {{
	audio_tier = 6
	is_foreign = no
	forbidden_for_estates = yes
	pop_type = laborers
	max_levels = 3
	employment_size = generic_peasant_building_employment
	category = infrastructure_category
	town = yes
	city = yes
	megalopolis = yes
	tsin_large_city = yes
	tsin_megalopolis = yes
	country_potential = {{ has_advance = {d['advance']} }}
	build_time = infrastructure_build_time
	graphical_tags = {{ factory_large }}
	unique_production_methods = {{
		{bid}_maintenance = {{
			icon_type = goods
			icon = {d['icon']}
			{maint}
			category = building_maintenance
		}}
	}}
	construction_demand = tsin_factory_construction
}}''')
    return '\n\n'.join(out) + '\n'


def script_values():
    return '''# H4 air capacity (country scope). Capital airfield level +10 (ID preserved), each airbase level +12.
tsin_air_capacity = {
	value = 6
	add = { value = total_effective_building_levels:tsin_capital_airfield multiply = 10 }
	add = { value = total_effective_building_levels:tsin_airbase multiply = 12 }
	if = { limit = { has_variable = tsin_tr_airbase_bonus } add = var:tsin_tr_airbase_bonus }
}

tsin_air_total = {
	value = var:tsin_air_fighter_stockpile
	add = var:tsin_air_cas_stockpile
	add = var:tsin_air_bomber_stockpile
	add = var:tsin_air_transport_stockpile
}
'''


def triggers():
    return '''# Fuel must not be depleted for sorties (H3 state 2 = depleted).
tsin_h4_sorties_possible_trigger = {
	OR = {
		NOT = { has_variable = tsin_fuel_state }
		var:tsin_fuel_state < 2
	}
}
'''


def effects():
    out = ['# H4: aircraft stockpiles and wartime operations. Scope: country. All numbers are placeholders.']
    init = ['tsin_h4_init_effect = {', '\tset_variable = { name = tsin_h4_init value = 1 }']
    for k, *_ in TYPES:
        init.append(f'\tset_variable = {{ name = tsin_air_{k}_stockpile value = 0 }}')
    init += ['\tset_variable = { name = tsin_air_active_aircraft value = 0 }',
             '\tset_variable = { name = tsin_air_enemy_fighters value = 0 }',
             '\tset_variable = { name = tsin_air_superiority_index value = 0 }', '}']
    out.append('\n'.join(init))
    dist = ['# Split up to 20 pooled aircraft a month into the four types while there is airbase room.',
            'tsin_h4_distribute_effect = {',
            '\tif = {',
            '\t\tlimit = { var:tsin_eq_aircraft_stockpile >= 4 tsin_air_total < tsin_air_capacity }',
            '\t\tset_variable = { name = tsin_air_batch value = { value = var:tsin_eq_aircraft_stockpile max = 20 } }']
    for k, _, _, share in TYPES:
        dist.append(f'\t\tchange_variable = {{ name = tsin_air_{k}_stockpile add = {{ value = var:tsin_air_batch multiply = {share} }} }}')
    dist += ['\t\tchange_variable = { name = tsin_eq_aircraft_stockpile subtract = var:tsin_air_batch }', '\t}', '}']
    out.append('\n'.join(dist))
    out.append('''tsin_h4_clear_targets_effect = {
	if = { limit = { has_variable = tsin_air_target_superiority } remove_variable = tsin_air_target_superiority }
	if = { limit = { has_variable = tsin_air_target_cas } remove_variable = tsin_air_target_cas }
	if = { limit = { has_variable = tsin_air_target_bombing } remove_variable = tsin_air_target_bombing }
	if = { limit = { has_variable = tsin_air_target_supply } remove_variable = tsin_air_target_supply }
}

# AI: the first army in combat picks the province for superiority, close support and air supply.
tsin_h4_ai_assign_effect = {
	random_army = {
		limit = { in_combat = yes }
		unit_location = { save_scope_as = tsin_air_ai_location }
	}
	if = {
		limit = { exists = scope:tsin_air_ai_location }
		set_variable = { name = tsin_air_target_superiority value = scope:tsin_air_ai_location.province }
		set_variable = { name = tsin_air_target_cas value = scope:tsin_air_ai_location.province }
		set_variable = { name = tsin_air_target_supply value = scope:tsin_air_ai_location.province }
	}
	else = { tsin_h4_clear_targets_effect = yes }
}''')
    out.append('''# Mission 1: air superiority. Index in -1..1 from own and enemy fighters; units in the target province get +/- modifiers.
tsin_h4_superiority_effect = {
	if = {
		limit = { has_variable = tsin_air_target_superiority var:tsin_air_fighter_stockpile > 0 tsin_h4_sorties_possible_trigger = yes }
		change_variable = { name = tsin_air_active_aircraft add = var:tsin_air_fighter_stockpile }
		set_variable = {
			name = tsin_air_superiority_index
			value = {
				value = var:tsin_air_fighter_stockpile
				subtract = var:tsin_air_enemy_fighters
				divide = { value = var:tsin_air_fighter_stockpile add = var:tsin_air_enemy_fighters add = 1 }
			}
		}
		var:tsin_air_target_superiority = {
			every_location_in_province = {
				every_unit_in_location = {
					limit = { owner ?= scope:tsin_air_owner }
					if = {
						limit = { scope:tsin_air_owner.var:tsin_air_superiority_index > 0.15 }
						add_unit_modifier = { modifier = tsin_air_superiority_bonus days = 31 mode = add_and_extend }
					}
					else_if = {
						limit = { scope:tsin_air_owner.var:tsin_air_superiority_index < -0.15 }
						add_unit_modifier = { modifier = tsin_air_inferiority_penalty days = 31 mode = add_and_extend }
					}
				}
			}
		}
		# Air combat losses: 3% of own fighters plus 2% of the enemy fighters.
		change_variable = {
			name = tsin_air_fighter_stockpile
			subtract = { value = var:tsin_air_enemy_fighters multiply = 0.02 add = { value = var:tsin_air_fighter_stockpile multiply = 0.03 } }
		}
		if = { limit = { var:tsin_air_fighter_stockpile < 0 } set_variable = { name = tsin_air_fighter_stockpile value = 0 } }
	}
}

# Mission 2: close air support. Damages enemy units that are in combat in the target province; anti-air halves it.
tsin_h4_cas_effect = {
	if = {
		limit = { has_variable = tsin_air_target_cas var:tsin_air_cas_stockpile >= 4 tsin_h4_sorties_possible_trigger = yes }
		change_variable = { name = tsin_air_active_aircraft add = var:tsin_air_cas_stockpile }
		var:tsin_air_target_cas = {
			every_location_in_province = {
				if = {
					limit = { has_building_with_at_least_one_level = tsin_anti_air_battery }
					scope:tsin_air_owner = { change_variable = { name = tsin_air_cas_stockpile subtract = 1 } }
					every_unit_in_location = {
						limit = { in_combat = yes owner ?= { is_at_war_with = scope:tsin_air_owner } }
						damage_unit_percent = { 0 0.015 }
						damage_unit_morale_percent = { 0.01 0.03 }
					}
				}
				else = {
					every_unit_in_location = {
						limit = { in_combat = yes owner ?= { is_at_war_with = scope:tsin_air_owner } }
						damage_unit_percent = { 0 0.03 }
						damage_unit_morale_percent = { 0.02 0.06 }
					}
				}
			}
		}
		# Sortie losses 3% a month.
		change_variable = { name = tsin_air_cas_stockpile subtract = { value = var:tsin_air_cas_stockpile multiply = 0.03 } }
		if = { limit = { var:tsin_air_cas_stockpile < 0 } set_variable = { name = tsin_air_cas_stockpile value = 0 } }
	}
}

# Mission 3: strategic bombing. Small chance per enemy location to knock down one building level; anti-air lowers it and costs bombers.
# change_garrison_size / add_breach for sieges are not wired (names unverified).
tsin_h4_bombing_effect = {
	if = {
		limit = { has_variable = tsin_air_target_bombing var:tsin_air_bomber_stockpile >= 6 tsin_h4_sorties_possible_trigger = yes }
		change_variable = { name = tsin_air_active_aircraft add = var:tsin_air_bomber_stockpile }
		var:tsin_air_target_bombing = {
			every_location_in_province = {
				limit = { owner ?= { is_at_war_with = scope:tsin_air_owner } }
				if = {
					limit = { has_building_with_at_least_one_level = tsin_anti_air_battery }
					scope:tsin_air_owner = { change_variable = { name = tsin_air_bomber_stockpile subtract = 2 } }
					random = {
						chance = 5
						tsin_h4_bomb_location_effect = yes
					}
				}
				else = {
					random = {
						chance = 12
						tsin_h4_bomb_location_effect = yes
					}
				}
			}
		}
		# Bomber losses: 3% plus 1% of the enemy fighters.
		change_variable = {
			name = tsin_air_bomber_stockpile
			subtract = { value = var:tsin_air_enemy_fighters multiply = 0.01 add = { value = var:tsin_air_bomber_stockpile multiply = 0.03 } }
		}
		if = { limit = { var:tsin_air_bomber_stockpile < 0 } set_variable = { name = tsin_air_bomber_stockpile value = 0 } }
	}
}

# Location scope.
tsin_h4_bomb_location_effect = {
	ordered_buildings_in_location = {
		order_by = building_level
		max = 1
		location = { minor_destroy_building_levels_in_location = yes }
	}
	change_prosperity = prosperity_weak_penalty
}

# Mission 4: air supply. Own armies besieged in the target province get food.
tsin_h4_supply_effect = {
	if = {
		limit = { has_variable = tsin_air_target_supply var:tsin_air_transport_stockpile >= 3 tsin_h4_sorties_possible_trigger = yes }
		change_variable = { name = tsin_air_active_aircraft add = var:tsin_air_transport_stockpile }
		var:tsin_air_target_supply = {
			every_location_in_province = {
				every_unit_in_location = {
					limit = { owner ?= scope:tsin_air_owner in_siege = yes }
					add_food_percentage = { 0.05 0.10 }
				}
			}
		}
		change_variable = { name = tsin_air_transport_stockpile subtract = { value = var:tsin_air_transport_stockpile multiply = 0.02 } }
		if = { limit = { var:tsin_air_transport_stockpile < 0 } set_variable = { name = tsin_air_transport_stockpile value = 0 } }
	}
}

# Wartime operations. Only countries at war reach this effect.
tsin_h4_war_ops_effect = {
	save_scope_as = tsin_air_owner
	if = { limit = { is_ai = yes } tsin_h4_ai_assign_effect = yes }
	set_variable = { name = tsin_air_active_aircraft value = 0 }
	set_variable = { name = tsin_air_enemy_fighters value = 0 }
	every_current_war = {
		every_war_participant = {
			limit = { is_at_war_with = scope:tsin_air_owner has_variable = tsin_air_fighter_stockpile }
			save_temporary_scope_value_as = { name = tsin_air_enemy_value value = var:tsin_air_fighter_stockpile }
			scope:tsin_air_owner = { change_variable = { name = tsin_air_enemy_fighters add = scope:tsin_air_enemy_value } }
		}
	}
	tsin_h4_superiority_effect = yes
	tsin_h4_cas_effect = yes
	tsin_h4_bombing_effect = yes
	tsin_h4_supply_effect = yes
}

tsin_h4_air_monthly_effect = {
	if = { limit = { NOT = { has_variable = tsin_h4_init } } tsin_h4_init_effect = yes }
	tsin_h4_distribute_effect = yes
	if = {
		limit = { at_war = yes }
		tsin_h4_war_ops_effect = yes
	}
	else_if = {
		limit = { OR = { has_variable = tsin_air_target_superiority has_variable = tsin_air_target_cas has_variable = tsin_air_target_bombing has_variable = tsin_air_target_supply } }
		tsin_h4_clear_targets_effect = yes
		set_variable = { name = tsin_air_active_aircraft value = 0 }
	}
}''')
    return '\n\n'.join(out) + '\n'


def on_actions():
    return '''# H4: monthly air pulse. Gated by age VIII and tsin_aircraft_industry_advance; operations run only while at war.
monthly_country_pulse = {
	on_actions = { tsin_h4_air_monthly }
}

tsin_h4_air_monthly = {
	trigger = { tsin_h_air_gate_trigger = yes }
	effect = { tsin_h4_air_monthly_effect = yes }
}
'''


def generic_actions():
    out = ['# H4 air mission assignment. Province targeting: the area selector type is not used elsewhere in this mod (Area targeting: 사용자 확인 필요).',
           '# Price is zero; missions run in the monthly air pulse and only while at war.']
    for key, stock, enemy, en, ko in MISSIONS:
        if enemy:
            visible = 'any_location_in_province = { OR = { owner ?= { is_at_war_with = scope:actor } controller ?= { is_at_war_with = scope:actor } } }'
        else:
            visible = 'any_location_in_province = { controller ?= scope:actor }'
        out.append(f'''tsin_air_target_{key} = {{
	type = owncountry
	price = price:tsin_air_order_price
	show_message = no
	ai_tick = never
	automation_tick = never
	potential = {{ scope:actor = {{ has_advance = tsin_air_operations_advance }} }}
	allow = {{ scope:actor = {{ has_variable = tsin_h4_init tsin_h_air_gate_trigger = yes }} }}
	select_trigger = {{
		looking_for_a = province source = actor target_flag = target_province name = "choose_province"
		column = {{ data = name }}
		visible = {{ {visible} }}
		enabled = {{ any_location_in_province = {{ always = yes }} }}
	}}
	effect = {{
		scope:actor = {{ set_variable = {{ name = tsin_air_target_{key} value = scope:target_province }} }}
	}}
}}''')
    out.append('''tsin_air_recall = {
	type = owncountry
	price = price:tsin_air_order_price
	show_message = no
	ai_tick = never
	automation_tick = never
	potential = { scope:actor = { has_advance = tsin_air_operations_advance } }
	allow = { scope:actor = { has_variable = tsin_h4_init } }
	effect = {
		scope:actor = { tsin_h4_clear_targets_effect = yes }
	}
}''')
    return '\n\n'.join(out) + '\n'


MODS = [
    ('tsin_air_superiority_bonus', 'Air superiority', '제공권 우세', 'Friendly fighters control the sky above this army.', '아군 전투기가 이 군대 상공을 장악했습니다.',
     {'army_movement_speed': 0.05, 'discipline': 0.03}),
    ('tsin_air_inferiority_penalty', 'Enemy air superiority', '제공권 열세', 'Enemy fighters control the sky above this army.', '적 전투기가 이 군대 상공을 장악했습니다.',
     {'army_movement_speed': -0.05, 'discipline': -0.03}),
]


def static_modifiers():
    out = ['# H4 air superiority modifiers (unit category). 사용자 확인 필요.']
    for key, _, _, _, _, mods in MODS:
        body = '\n'.join(f'\t{m} = {v}' for m, v in mods.items())
        out.append(f'{key} = {{\n\tgame_data = {{ category = unit }}\n{body}\n}}')
    return '\n\n'.join(out) + '\n'


def localization():
    loc = common.Loc()
    for aid, _, _, _, _, en, ko, den, dko in ADVANCES:
        loc.add(aid, en, ko, den, dko)
    for bid, d in BUILDINGS.items():
        loc.add(bid, d['en'], d['ko'], d['en_desc'], d['ko_desc'])
        loc.add(f'{bid}_maintenance', d['en'] + ' service', d['ko'] + ' 운영', d['en'] + ' upkeep.', d['ko'] + ' 유지입니다.')
    for key, stock, enemy, en, ko in MISSIONS:
        scope_text_en = 'an enemy-held' if enemy else 'a friendly'
        scope_text_ko = '적이 점령한' if enemy else '아군'
        loc.add(f'tsin_air_target_{key}', f'Assign air mission: {en}', f'항공 임무 지정: {ko}',
                f'Choose {scope_text_en} province for the {en.lower()} mission. Runs monthly while at war, using the matching aircraft stockpile.',
                f'{scope_text_ko} 지방을 골라 {ko} 임무를 배정합니다. 전시에 매월 해당 항공기 비축으로 수행합니다.')
    loc.add('tsin_air_recall', 'Recall all air missions', '항공 임무 전체 회수', 'Clears every assigned air mission target.', '배정한 모든 항공 임무 목표를 지웁니다.')
    for key, en, ko, den, dko, _ in MODS:
        loc.raw('STATIC_MODIFIER_NAME_' + key, en, ko)
        loc.raw('STATIC_MODIFIER_DESC_' + key, den, dko)
    return loc


def build():
    out = {
        f'{ERA}/in_game/common/advances/zzz_tsin_08_h4_airforce.txt': advances(),
        f'{ERA}/in_game/common/building_types/zzz_tsin_08_h4_air_buildings.txt': buildings(),
        f'{ERA}/in_game/common/script_values/zzz_tsin_h4_air_values.txt': script_values(),
        f'{ERA}/in_game/common/scripted_triggers/zzz_tsin_h4_air_triggers.txt': triggers(),
        f'{ERA}/in_game/common/scripted_effects/zzz_tsin_h4_air_effects.txt': effects(),
        f'{ERA}/in_game/common/on_action/zzz_tsin_h4_air_on_actions.txt': on_actions(),
        f'{ERA}/in_game/common/generic_actions/zzz_tsin_h4_air_missions.txt': generic_actions(),
        f'{ERA}/in_game/common/prices/zzz_tsin_h4_air_prices.txt': 'tsin_air_order_price = { gold = 0 }\n',
        f'{ERA}/main_menu/common/static_modifiers/zzz_tsin_h4_air_modifiers.txt': static_modifiers(),
    }
    out.update(localization().files(ERA, 'tsin_h4_airforce'))
    return {k: common.tidy(v) for k, v in out.items()}


def assets():
    return dict(common.building_asset(ERA, bid, d['art']) for bid, d in BUILDINGS.items())


def main(argv=None):
    return common.run('H4 airforce hybrid', {**build(), **assets()}, argv)


if __name__ == '__main__':
    raise SystemExit(main())
