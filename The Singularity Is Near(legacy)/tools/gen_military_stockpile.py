"""H1: armament works, national equipment stockpiles and shortage modifiers (age VIII+).

Four national stockpiles are country variables (small arms, support artillery,
armored vehicles, aircraft pool). They are fed monthly by building levels of four
new works (which also make real market goods so the AI builds them) and drained
by regiment counts and battle losses. A negative stockpile applies unit modifiers.

No new market goods are introduced: firearms, cannons and tsin_engines are reused.
Everything is gated by age VIII and the matching advance, so age VII saves are untouched.
All numbers are placeholders and every behavior is 사용자 확인 필요 (docs/h0_engine_probes.md).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h_track_common as common  # noqa: E402

ERA = 'era_8'
PRICES = {'iron': 3, 'coal': 2, 'tools': 3, 'steel': 5, 'copper': 3, 'lumber': 1.5, 'glass': 3,
          'tsin_engines': 6, 'tsin_oil': 4, 'tsin_rubber': 4, 'tsin_explosives': 5,
          'firearms': 3, 'cannons': 4}
MARGIN = 1.15

# key, stockpile variable, works id, output good, per-level monthly accrual, start stock, counter driving demand
CATEGORIES = [
    dict(key='small_arms', works='tsin_small_arms_works', good='firearms', rate=8, start=60, loss=0.004,
         en='Small arms', ko='소화기'),
    dict(key='support_artillery', works='tsin_support_artillery_works', good='cannons', rate=4, start=30, loss=0.0005,
         en='Support artillery', ko='지원 화포'),
    dict(key='armored_vehicles', works='tsin_armored_vehicle_works', good='tsin_engines', rate=3, start=20, loss=0.0008,
         en='Armored vehicles', ko='기갑 차량'),
    dict(key='aircraft', works='tsin_aircraft_works', good='tsin_engines', rate=2, start=0, loss=0.0,
         en='Aircraft pool', ko='항공기 풀'),
]
STOCK_CAP = 600
STOCK_FLOOR = -300

# works id -> two alternative production methods: (pm id, icon, inputs)
WORKS = {
    'tsin_small_arms_works': [
        ('tsin_small_arms_works_rifle_line', 'steel', {'steel': 1.2, 'coal': 1.0, 'tools': 0.5, 'tsin_explosives': 0.1}),
        ('tsin_small_arms_works_automatic_line', 'tools', {'steel': 1.5, 'coal': 1.0, 'tools': 0.6, 'copper': 0.3, 'tsin_engines': 0.1}),
    ],
    'tsin_support_artillery_works': [
        ('tsin_support_artillery_works_howitzer_line', 'cannons', {'steel': 1.6, 'coal': 1.0, 'tools': 0.5, 'tsin_explosives': 0.3}),
        ('tsin_support_artillery_works_rocket_line', 'tsin_explosives', {'steel': 1.2, 'tsin_explosives': 0.6, 'tools': 0.4, 'tsin_engines': 0.1}),
    ],
    'tsin_armored_vehicle_works': [
        ('tsin_armored_vehicle_works_tank_line', 'steel', {'steel': 2.0, 'tsin_engines': 0.5, 'tsin_oil': 0.2, 'cannons': 0.3, 'tools': 0.4}),
        ('tsin_armored_vehicle_works_truck_line', 'tsin_rubber', {'steel': 1.2, 'tsin_engines': 0.4, 'tsin_rubber': 0.3, 'tsin_oil': 0.15, 'tools': 0.3}),
    ],
    'tsin_aircraft_works': [
        ('tsin_aircraft_works_fighter_line', 'tsin_engines', {'lumber': 0.8, 'steel': 0.6, 'tsin_engines': 0.5, 'copper': 0.2, 'tools': 0.3, 'tsin_oil': 0.1}),
        ('tsin_aircraft_works_heavy_airframe_line', 'steel', {'lumber': 0.4, 'steel': 1.2, 'tsin_engines': 0.7, 'copper': 0.3, 'tsin_rubber': 0.2, 'tsin_oil': 0.15}),
    ],
}
WORKS_GOOD = {c['works']: c['good'] for c in CATEGORIES}
WORKS_UNLOCK = {  # works -> advance
    'tsin_small_arms_works': 'tsin_mass_production_arms_advance',
    'tsin_support_artillery_works': 'tsin_mass_production_arms_advance',
    'tsin_armored_vehicle_works': 'tsin_armored_vehicle_industry_advance',
    'tsin_aircraft_works': 'tsin_aircraft_industry_advance',  # defined by gen_airforce_hybrid
}
WORKS_ICON = {'tsin_small_arms_works': 'tsin_machine_works', 'tsin_support_artillery_works': 'tsin_blasting_works',
              'tsin_armored_vehicle_works': 'tsin_power_station', 'tsin_aircraft_works': 'tsin_capital_airfield'}
WORKS_NAMES = {
    'tsin_small_arms_works': ('Small arms works', '소화기 공장', 'Mass-produces rifles, machine guns and ammunition. Each level adds to the national small arms stockpile every month and sells firearms on the market.', '소총·기관총·탄약을 대량 생산합니다. 매월 단계마다 국가 소화기 비축이 늘고 시장에 총기를 공급합니다.'),
    'tsin_support_artillery_works': ('Support artillery works', '지원 화포 공장', 'Produces howitzers, mortars and rockets. Each level adds to the national support artillery stockpile every month and sells cannons on the market.', '곡사포·박격포·로켓을 생산합니다. 매월 단계마다 국가 지원 화포 비축이 늘고 시장에 화포를 공급합니다.'),
    'tsin_armored_vehicle_works': ('Armored vehicle works', '기갑 차량 공장', 'Builds tanks, armored cars and trucks. Each level adds to the national armored vehicle stockpile every month and burns oil.', '전차·장갑차·트럭을 만듭니다. 매월 단계마다 국가 기갑 차량 비축이 늘고 석유를 소비합니다.'),
    'tsin_aircraft_works': ('Aircraft works', '항공기 공장', 'Assembles airframes and engines. Each level adds to the national aircraft pool every month, which is then split into fighters, close support, bombers and transports.', '기체와 엔진을 조립합니다. 매월 단계마다 국가 항공기 풀이 늘고 전투기·근접지원기·폭격기·수송기로 나뉩니다.'),
}


def pm_text(pm, icon, inputs, good):
    cost = sum(PRICES[g] * v for g, v in inputs.items())
    output = round(cost * MARGIN / PRICES[good], 2)
    lines = ['\t\t# inputs %.2f gold -> %s %.2f' % (cost, good, output),
             f'\t\t{pm} = {{', '\t\t\ticon_type = goods', f'\t\t\ticon = {icon}']
    lines += [f'\t\t\t{g} = {v}' for g, v in inputs.items()]
    lines += [f'\t\t\tproduced = {good}', f'\t\t\toutput = {output}', '',
              '\t\t\tdebug_max_profit = mills_profit_margin', '\t\t\tcategory = mills_input', '\t\t}']
    return '\n'.join(lines)


def building_text(works):
    pms = '\n\n'.join(pm_text(pm, icon, inputs, WORKS_GOOD[works]) for pm, icon, inputs in WORKS[works])
    return f'''{works} = {{
	audio_tier = 6
	is_foreign = no
	pop_type = laborers
	is_mill = yes
	max_levels = mills_max_level
	startup_ramp_target = mills_startup_ramp_target

	employment_size = mills_employment

	category = basic_industry_category
	town = yes
	city = yes
	megalopolis = yes
	tsin_large_city = yes
	tsin_megalopolis = yes

	build_time = mills_build_time
	graphical_tags = {{ factory_large }}

	# Two alternative production lines. Switching the line is not read by the stockpile (H0 probe: set_production_method).
	unique_production_methods = {{
{pms}
	}}

	construction_demand = tsin_factory_construction
}}
'''


def advances():
    return '''# H1 (HOI4 hybrid military). 사용자 확인 필요: all research, buildings and unlocks are untested in game.
tsin_mass_production_arms_advance = {
	age = age_8_world_wars
	icon = military_tactics_advance_6

	requires = tsin_general_staff_advance
	requires = tsin_internal_combustion_advance
	allow = { has_embraced_institution = institution:tsin_industrial_capitalism }

	unlock_building = tsin_small_arms_works
	unlock_building = tsin_support_artillery_works
	ai_weight = { add = 25 }
}

tsin_armored_vehicle_industry_advance = {
	age = age_8_world_wars
	icon = kor_gunpowder_engines

	requires = tsin_mass_production_arms_advance
	requires = tsin_motor_transport_advance
	allow = { has_embraced_institution = institution:tsin_industrial_capitalism }

	unlock_building = tsin_armored_vehicle_works
	ai_weight = { add = 20 }
}
'''


def triggers():
    return '''# H1/H3/H4 shared gates. Everything in the H-track is behind age VIII plus an advance, so age VII saves are untouched.
tsin_h_age8_trigger = {
	current_later_age_8_world_wars_trigger = yes
}

tsin_h_stockpile_gate_trigger = {
	tsin_h_age8_trigger = yes
	has_advance = tsin_mass_production_arms_advance
}

tsin_h_fuel_gate_trigger = {
	tsin_h_age8_trigger = yes
	has_advance = tsin_motor_transport_advance
}

tsin_h_air_gate_trigger = {
	tsin_h_age8_trigger = yes
	has_advance = tsin_aircraft_industry_advance
}
'''


def script_values():
    out = ['# H1 stockpile flows. Country scope. Numbers are placeholders (docs/military_hybrid_h_track.md).',
           'tsin_eq_stockpile_cap = %d' % STOCK_CAP,
           'tsin_eq_stockpile_floor = %d' % STOCK_FLOOR,
           '',
           '# Wartime factor: peacetime upkeep is 40% of wartime upkeep.',
           'tsin_h_war_factor = {', '\tvalue = 1', '\tif = { limit = { at_war = no } multiply = 0.4 }', '}', '']
    for c in CATEGORIES:
        k = c['key']
        out += [f'tsin_eq_{k}_production = {{',
                f'\tvalue = total_effective_building_levels:{c["works"]}',
                f'\tmultiply = {c["rate"]}',
                f'\tmultiply = var:tsin_line_eff_{k}', '}', '']
    out += ['# Demand before the war factor: infantry/artillery regiments, armored (heavy) and motorized (light) vehicles.',
            'tsin_eq_small_arms_demand_base = { value = var:tsin_h_n_infantry multiply = 0.12 }',
            'tsin_eq_support_artillery_demand_base = { value = var:tsin_h_n_artillery multiply = 0.30 }',
            'tsin_eq_armored_vehicles_demand_base = {',
            '\tvalue = var:tsin_h_n_armored multiply = 0.40',
            '\tadd = { value = var:tsin_h_n_motorized multiply = 0.15 }', '}',
            'tsin_eq_aircraft_demand_base = 0', '']
    for c in CATEGORIES:
        k = c['key']
        out += [f'tsin_eq_{k}_demand = {{ value = tsin_eq_{k}_demand_base multiply = tsin_h_war_factor }}',
                f'# A free national reserve (legacy conscript stock) covers 30% of the base demand.',
                f'tsin_eq_{k}_baseline = {{ value = tsin_eq_{k}_demand_base multiply = 0.3 }}', '']
    return '\n'.join(out) + '\n'


def effects():
    cats = CATEGORIES
    out = ['# H1: national equipment stockpiles. Scope: country.']
    # initialisation
    init = ['tsin_h_init_effect = {',
            '\tset_variable = { name = tsin_h_init value = 1 }',
            '\tset_variable = { name = tsin_h_n_infantry value = 0 }',
            '\tset_variable = { name = tsin_h_n_artillery value = 0 }',
            '\tset_variable = { name = tsin_h_n_armored value = 0 }',
            '\tset_variable = { name = tsin_h_n_motorized value = 0 }']
    for c in cats:
        init.append(f'\tset_variable = {{ name = tsin_eq_{c["key"]}_stockpile value = {c["start"]} }}')
        init.append(f'\tset_variable = {{ name = tsin_line_eff_{c["key"]} value = 1 }}')
    init.append('}')
    out.append('\n'.join(init))
    # unit counter (once per calendar month per country)
    out.append('''# Counts regiments by role once per month (other H modules reuse the counters).
tsin_h_count_units_effect = {
	if = {
		limit = {
			OR = {
				NOT = { has_variable = tsin_h_count_stamp }
				tsin_urban_calendar_month > var:tsin_h_count_stamp
			}
		}
		set_variable = { name = tsin_h_count_stamp value = tsin_urban_calendar_month }
		set_variable = { name = tsin_h_n_infantry value = 0 }
		set_variable = { name = tsin_h_n_artillery value = 0 }
		set_variable = { name = tsin_h_n_armored value = 0 }
		set_variable = { name = tsin_h_n_motorized value = 0 }
		save_scope_as = tsin_h_country
		every_army = {
			every_sub_unit = {
				limit = { tsin_h_unit_infantry_trigger = yes }
				scope:tsin_h_country = { change_variable = { name = tsin_h_n_infantry add = 1 } }
			}
			every_sub_unit = {
				limit = { tsin_h_unit_artillery_trigger = yes }
				scope:tsin_h_country = { change_variable = { name = tsin_h_n_artillery add = 1 } }
			}
			every_sub_unit = {
				limit = { tsin_h_unit_armored_trigger = yes }
				scope:tsin_h_country = { change_variable = { name = tsin_h_n_armored add = 1 } }
			}
			every_sub_unit = {
				limit = { tsin_h_unit_motorized_trigger = yes }
				scope:tsin_h_country = { change_variable = { name = tsin_h_n_motorized add = 1 } }
			}
		}
	}
}''')
    # line efficiency recovery and retool helpers
    rec = ['# Line efficiency drops after a retool and recovers 5 points a month.', 'tsin_h_line_recover_effect = {']
    for c in cats:
        k = c['key']
        rec.append(f'\tif = {{ limit = {{ var:tsin_line_eff_{k} < 1 }} change_variable = {{ name = tsin_line_eff_{k} add = 0.05 }} if = {{ limit = {{ var:tsin_line_eff_{k} > 1 }} set_variable = {{ name = tsin_line_eff_{k} value = 1 }} }} }}')
    rec.append('}')
    out.append('\n'.join(rec))
    for c in cats:
        k = c['key']
        out.append(f'# Call after a production line change for {k}. Not hooked to production method switches yet (H0 probe).\n'
                   f'tsin_h_retool_{k}_effect = {{ if = {{ limit = {{ var:tsin_line_eff_{k} > 0.5 }} set_variable = {{ name = tsin_line_eff_{k} value = 0.5 }} }} }}')
    # monthly accrual
    mon = ['# Monthly accrual: production + reserve - demand, clamped to the cap/floor.', 'tsin_h1_stockpile_monthly_effect = {',
           '\tif = { limit = { NOT = { has_variable = tsin_h_init } } tsin_h_init_effect = yes }',
           '\ttsin_h_count_units_effect = yes']
    for c in cats:
        k = c['key']
        mon += [f'\tchange_variable = {{ name = tsin_eq_{k}_stockpile add = tsin_eq_{k}_production }}',
                f'\tchange_variable = {{ name = tsin_eq_{k}_stockpile add = tsin_eq_{k}_baseline }}',
                f'\tchange_variable = {{ name = tsin_eq_{k}_stockpile subtract = tsin_eq_{k}_demand }}',
                f'\tif = {{ limit = {{ var:tsin_eq_{k}_stockpile > tsin_eq_stockpile_cap }} set_variable = {{ name = tsin_eq_{k}_stockpile value = tsin_eq_stockpile_cap }} }}',
                f'\tif = {{ limit = {{ var:tsin_eq_{k}_stockpile < tsin_eq_stockpile_floor }} set_variable = {{ name = tsin_eq_{k}_stockpile value = tsin_eq_stockpile_floor }} }}']
    mon += ['\ttsin_h_line_recover_effect = yes', '\ttsin_h_apply_shortage_effect = yes', '}']
    out.append('\n'.join(mon))
    # shortage modifiers
    short = ['# Shortage: a negative stockpile puts a unit modifier on armies while at war or when the deficit is deep.',
             '# add_and_extend with 31 days is renewed every month; the modifier is removed when the stock recovers.',
             'tsin_h_apply_shortage_effect = {']
    spec = [('small_arms', 'tsin_eq_shortage_small_arms', ''),
            ('support_artillery', 'tsin_eq_shortage_support_artillery', ''),
            ('armored_vehicles', 'tsin_eq_shortage_armored_vehicles', 'limit = { any_sub_unit = { tsin_h_unit_fuel_user_trigger = yes } }')]
    for k, mod, lim in spec:
        short += [f'\tif = {{',
                  f'\t\tlimit = {{ var:tsin_eq_{k}_stockpile < 0 OR = {{ at_war = yes var:tsin_eq_{k}_stockpile < -150 }} }}',
                  f'\t\tevery_army = {{ {lim} add_unit_modifier = {{ modifier = {mod} days = 31 mode = add_and_extend }} }}',
                  f'\t\tset_variable = {{ name = tsin_h_short_{k} value = 1 }}',
                  '\t}',
                  f'\telse_if = {{',
                  f'\t\tlimit = {{ has_variable = tsin_h_short_{k} }}',
                  f'\t\tevery_army = {{ remove_unit_modifier = {mod} }}',
                  f'\t\tremove_variable = tsin_h_short_{k}',
                  '\t}']
    short.append('}')
    out.append('\n'.join(short))
    # battle losses
    loss = ['# Battle losses: scope:lost_land_units is soldiers lost (on_battle_won / on_battle_lost, root = actor unit).',
            '# Each side subtracts its own losses. Whether lost_land_units is the actor\'s own loss is 사용자 확인 필요.',
            'tsin_eq_battle_loss_effect = {',
            '\tif = { limit = { exists = scope:lost_land_units } ']
    for c in cats:
        if c['loss'] > 0:
            loss.append(f'\t\tchange_variable = {{ name = tsin_eq_{c["key"]}_stockpile subtract = {{ value = scope:lost_land_units multiply = {c["loss"]} }} }}')
            loss.append(f'\t\tif = {{ limit = {{ var:tsin_eq_{c["key"]}_stockpile < tsin_eq_stockpile_floor }} set_variable = {{ name = tsin_eq_{c["key"]}_stockpile value = tsin_eq_stockpile_floor }} }}')
    loss += ['\t}', '}']
    out.append('\n'.join(loss))
    return '\n\n'.join(out) + '\n'


def on_actions():
    return '''# H1: monthly stockpile pulse and battle-loss hooks. Gated by age VIII and tsin_mass_production_arms_advance.
monthly_country_pulse = {
	on_actions = { tsin_h1_stockpile_monthly }
}

on_battle_won = {
	on_actions = { tsin_h1_battle_won }
}

on_battle_lost = {
	on_actions = { tsin_h1_battle_lost }
}

tsin_h1_stockpile_monthly = {
	trigger = { tsin_h_stockpile_gate_trigger = yes }
	effect = { tsin_h1_stockpile_monthly_effect = yes }
}

# root = actor (winning unit), scope:actor.owner = winner
tsin_h1_battle_won = {
	effect = {
		scope:actor.owner ?= {
			if = { limit = { tsin_h_stockpile_gate_trigger = yes has_variable = tsin_h_init } tsin_eq_battle_loss_effect = yes }
		}
	}
}

# root = actor (losing unit), scope:actor.owner = loser
tsin_h1_battle_lost = {
	effect = {
		scope:actor.owner ?= {
			if = { limit = { tsin_h_stockpile_gate_trigger = yes has_variable = tsin_h_init } tsin_eq_battle_loss_effect = yes }
		}
	}
}
'''


SHORTAGE_MODIFIERS = [
    ('tsin_eq_shortage_small_arms', 'Small arms shortage', '소화기 부족',
     'The small arms stockpile is exhausted. Infantry fight and reinforce poorly.', '소화기 비축이 바닥났습니다. 보병의 전투력과 보충 속도가 떨어집니다.',
     {'army_light_infantry_power': -0.15, 'army_heavy_infantry_power': -0.15, 'discipline': -0.05, 'regiment_reinforcement_speed': -0.25}),
    ('tsin_eq_shortage_support_artillery', 'Support artillery shortage', '지원 화포 부족',
     'The support artillery stockpile is exhausted. Guns lack shells and replacement barrels.', '지원 화포 비축이 바닥났습니다. 포탄과 교체 포신이 모자랍니다.',
     {'army_artillery_power': -0.20, 'regiment_reinforcement_speed': -0.15}),
    ('tsin_eq_shortage_armored_vehicles', 'Armored vehicle shortage', '기갑 차량 부족',
     'The armored vehicle stockpile is exhausted. Spare parts and replacements are missing.', '기갑 차량 비축이 바닥났습니다. 예비 부품과 보충 차량이 없습니다.',
     {'army_heavy_cavalry_power': -0.20, 'army_light_cavalry_power': -0.20, 'army_movement_speed': -0.10, 'regiment_reinforcement_speed': -0.15}),
]


def static_modifiers():
    out = ['# H1 shortage modifiers (unit category). 사용자 확인 필요: add_unit_modifier on armies, modifier names in unit scope.']
    for key, _, _, _, _, mods in SHORTAGE_MODIFIERS:
        body = '\n'.join(f'\t{m} = {v}' for m, v in mods.items())
        out.append(f'{key} = {{\n\tgame_data = {{ category = unit }}\n{body}\n}}')
    return '\n\n'.join(out) + '\n'


def localization():
    loc = common.Loc()
    loc.add('tsin_mass_production_arms_advance', 'Mass-production armament', '군수 대량생산',
            'Standardized parts and assembly lines allow small arms and support artillery works. National equipment stockpiles start to matter in wartime.',
            '표준 부품과 조립 라인으로 소화기·지원 화포 공장을 세웁니다. 전시에는 국가 장비 비축이 중요해집니다.')
    loc.add('tsin_armored_vehicle_industry_advance', 'Armored vehicle industry', '기갑 차량 산업',
            'Engine, steel and oil supplies are organized into an armored vehicle works.', '엔진·강철·석유 공급을 묶어 기갑 차량 공장을 세웁니다.')
    for works, (en, ko, den, dko) in WORKS_NAMES.items():
        loc.add(works, en, ko, den, dko)
    for key, en, ko, den, dko, _ in SHORTAGE_MODIFIERS:
        loc.raw('STATIC_MODIFIER_NAME_' + key, en, ko)
        loc.raw('STATIC_MODIFIER_DESC_' + key, den, dko)
    return loc


KO_LINES = {  # production method labels
    'tsin_small_arms_works_rifle_line': ('Rifle line', '소총 라인'),
    'tsin_small_arms_works_automatic_line': ('Automatic weapons line', '자동화기 라인'),
    'tsin_support_artillery_works_howitzer_line': ('Howitzer line', '곡사포 라인'),
    'tsin_support_artillery_works_rocket_line': ('Rocket line', '로켓 라인'),
    'tsin_armored_vehicle_works_tank_line': ('Tank line', '전차 라인'),
    'tsin_armored_vehicle_works_truck_line': ('Truck and armored car line', '트럭·장갑차 라인'),
    'tsin_aircraft_works_fighter_line': ('Fighter line', '전투기 라인'),
    'tsin_aircraft_works_heavy_airframe_line': ('Heavy airframe line', '대형 기체 라인'),
}


def build():
    loc = localization()
    for pm, (en, ko) in KO_LINES.items():
        loc.add(pm, en, ko, en + ' of the works.', ko + '입니다.')
    out = {
        f'{ERA}/in_game/common/advances/zzz_tsin_08_h1_military_industry.txt': advances(),
        f'{ERA}/in_game/common/building_types/zzz_tsin_08_h1_arsenals.txt':
            '# H1 armament works (mill style: they also produce market goods so the AI builds them).\n' + '\n'.join(building_text(w) for w in WORKS),
        f'{ERA}/in_game/common/scripted_triggers/zzz_tsin_h1_gates.txt': triggers(),
        f'{ERA}/in_game/common/script_values/zzz_tsin_h1_stockpile_values.txt': script_values(),
        f'{ERA}/in_game/common/scripted_effects/zzz_tsin_h1_stockpile_effects.txt': effects(),
        f'{ERA}/in_game/common/on_action/zzz_tsin_h1_stockpile_on_actions.txt': on_actions(),
        f'{ERA}/main_menu/common/static_modifiers/zzz_tsin_h1_shortage_modifiers.txt': static_modifiers(),
    }
    out.update(loc.files(ERA, 'tsin_h1_stockpile'))
    return {k: common.tidy(v) for k, v in out.items()}


def assets():
    return dict(common.building_asset(ERA, works, old) for works, old in WORKS_ICON.items())


def main(argv=None):
    return common.run('H1 military stockpile', {**build(), **assets()}, argv)


if __name__ == '__main__':
    raise SystemExit(main())
