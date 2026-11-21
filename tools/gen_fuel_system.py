"""H3: national fuel stockpile (var:tsin_fuel_stockpile), consumption and depletion penalties.

Vanilla supply, railways and the TSIN motor depot / capital airfield are untouched.
Fuel is a country variable: filled each month by a small baseline plus a capped purchase of
tsin_oil from the capital market (global variable tsin_h_fuel_market_off disables buying),
drained by armored/motorized regiments and by last month's active aircraft (H4). At war the
consumption weight is higher. Low fuel slows armor; empty fuel also cuts armor power.
Gate: age VIII + tsin_motor_transport_advance, so age VII saves are untouched.
All numbers are placeholders; every behavior is 사용자 확인 필요 (docs/h0_engine_probes.md).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h_track_common as common  # noqa: E402

ERA = 'era_8'
START_FUEL = 50
OIL_TO_FUEL = 5
MAX_BUY = 6

MODS = [
    ('tsin_fuel_low', 'Low fuel', '연료 부족 임박',
     'National fuel reserves are below 20% of capacity. Armored and motorized units slow down.', '국가 연료 비축이 저장 용량의 20% 미만입니다. 기갑·차량화 부대가 느려집니다.',
     {'army_movement_speed': -0.10, 'army_heavy_cavalry_power': -0.05}),
    ('tsin_fuel_depleted', 'Fuel depleted', '연료 고갈',
     'The fuel reserve ran dry. Armored and motorized units crawl and fight poorly.', '연료 비축이 바닥났습니다. 기갑·차량화 부대의 이동과 전투력이 크게 떨어집니다.',
     {'army_movement_speed': -0.40, 'army_heavy_cavalry_power': -0.30, 'army_light_cavalry_power': -0.20,
      'army_heavy_infantry_power': -0.05, 'discipline': -0.05}),
]


def script_values():
    return '''# H3 fuel flows (country scope). Placeholder numbers: docs/military_hybrid_h_track.md.
# Storage: base 100 + 120 per oil storage level + 60 per motor depot level + 40 per airbase level.
tsin_fuel_capacity = {
	value = 100
	add = { value = total_effective_building_levels:tsin_oil_storage multiply = 120 }
	add = { value = total_effective_building_levels:tsin_motor_transport_depot multiply = 60 }
	add = { value = total_effective_building_levels:tsin_airbase multiply = 40 }
}

# Wartime consumption is weighted 2.0, peacetime 0.3.
tsin_fuel_war_factor = {
	value = 2
	if = { limit = { at_war = no } multiply = 0.15 }
}

# Armored units burn 0.6 per regiment-month (before the war factor), motorized units 0.25.
tsin_fuel_ground_use = {
	value = var:tsin_h_n_armored
	multiply = 0.6
	add = { value = var:tsin_h_n_motorized multiply = 0.25 }
}

# Last month's active aircraft (written by the H4 air operations), 0.15 each.
tsin_fuel_air_use = {
	value = 0
	if = {
		limit = { has_variable = tsin_air_active_aircraft }
		add = { value = var:tsin_air_active_aircraft multiply = 0.15 }
	}
}

tsin_fuel_use = {
	value = tsin_fuel_ground_use
	add = tsin_fuel_air_use
	multiply = tsin_fuel_war_factor
}

# Domestic synthetic/coal-derived fuel placeholder plus depot throughput.
tsin_fuel_baseline_inflow = {
	value = 1.5
	add = { value = total_effective_building_levels:tsin_motor_transport_depot multiply = 0.5 }
}
'''


def effects():
    return f'''# H3: national fuel. Scope: country.
tsin_h3_fuel_init_effect = {{
	set_variable = {{ name = tsin_h3_init value = 1 }}
	set_variable = {{ name = tsin_fuel_stockpile value = {START_FUEL} }}
	set_variable = {{ name = tsin_fuel_state value = 0 }}
}}

# Console switches: `effect tsin_h_fuel_market_off_effect = yes` stops market purchases (H0 probe fallback), `..._on_effect` resumes.
tsin_h_fuel_market_off_effect = {{ set_global_variable = tsin_h_fuel_market_off }}
tsin_h_fuel_market_on_effect = {{ if = {{ limit = {{ has_global_variable = tsin_h_fuel_market_off }} remove_global_variable = tsin_h_fuel_market_off }} }}

# Buy up to {MAX_BUY} tsin_oil a month from the capital market; observed stock change is what counts.
# 사용자 확인 필요: buy_goods_from_market in a monthly pulse (price spikes, market access, AI distortion).
tsin_h3_fuel_market_effect = {{
	if = {{
		limit = {{
			exists = capital
			NOT = {{ has_global_variable = tsin_h_fuel_market_off }}
			var:tsin_fuel_stockpile < tsin_fuel_capacity
		}}
		set_variable = {{ name = tsin_fuel_room value = {{ value = tsin_fuel_capacity subtract = var:tsin_fuel_stockpile }} }}
		save_scope_as = tsin_fuel_operator
		capital = {{
			set_variable = {{ name = tsin_fuel_observed value = 0 }}
			if = {{
				limit = {{
					exists = market
					"market.market_price(goods:tsin_oil)" > 0
					"market.stockpile_in_market(goods:tsin_oil)" > 0
				}}
				save_scope_as = tsin_fuel_site
				set_variable = {{ name = tsin_fuel_before value = "market.stockpile_in_market(goods:tsin_oil)" }}
				set_variable = {{
					name = tsin_fuel_quantity
					value = {{
						value = {MAX_BUY}
						max = "market.stockpile_in_market(goods:tsin_oil)"
						max = {{ value = scope:tsin_fuel_operator.var:tsin_fuel_room divide = {OIL_TO_FUEL} }}
						max = {{ value = scope:tsin_fuel_operator.gold multiply = 0.02 divide = "market.market_price(goods:tsin_oil)" }}
						min = 0
					}}
				}}
				if = {{
					limit = {{ var:tsin_fuel_quantity > 0 }}
					scope:tsin_fuel_operator = {{
						buy_goods_from_market = {{
							market = scope:tsin_fuel_site.market
							goods = goods:tsin_oil
							amount = scope:tsin_fuel_site.var:tsin_fuel_quantity
						}}
					}}
					set_variable = {{
						name = tsin_fuel_observed
						value = {{ value = var:tsin_fuel_before subtract = "market.stockpile_in_market(goods:tsin_oil)" max = var:tsin_fuel_quantity min = 0 }}
					}}
				}}
			}}
		}}
		change_variable = {{ name = tsin_fuel_stockpile add = {{ value = capital.var:tsin_fuel_observed multiply = {OIL_TO_FUEL} }} }}
	}}
}}

# State: 0 normal, 1 low (<20% of capacity), 2 depleted (consumption exceeded the reserve this month).
tsin_h3_fuel_monthly_effect = {{
	if = {{ limit = {{ NOT = {{ has_variable = tsin_h3_init }} }} tsin_h3_fuel_init_effect = yes }}
	tsin_h_count_units_effect = yes
	change_variable = {{ name = tsin_fuel_stockpile add = tsin_fuel_baseline_inflow }}
	tsin_h3_fuel_market_effect = yes
	change_variable = {{ name = tsin_fuel_stockpile subtract = tsin_fuel_use }}
	if = {{
		limit = {{ var:tsin_fuel_stockpile < 0 }}
		set_variable = {{ name = tsin_fuel_stockpile value = 0 }}
		set_variable = {{ name = tsin_fuel_state value = 2 }}
	}}
	else_if = {{
		limit = {{ var:tsin_fuel_stockpile < {{ value = tsin_fuel_capacity multiply = 0.2 }} }}
		set_variable = {{ name = tsin_fuel_state value = 1 }}
	}}
	else = {{ set_variable = {{ name = tsin_fuel_state value = 0 }} }}
	if = {{
		limit = {{ var:tsin_fuel_stockpile > tsin_fuel_capacity }}
		set_variable = {{ name = tsin_fuel_stockpile value = tsin_fuel_capacity }}
	}}
	tsin_h3_fuel_penalty_effect = yes
}}

# Penalties go on armies that contain armored or motorized regiments; modifiers are renewed monthly (31 days)
# and removed on recovery. add_unit_modifier on armies is 사용자 확인 필요.
tsin_h3_fuel_penalty_effect = {{
	if = {{
		limit = {{ var:tsin_fuel_state = 2 }}
		every_army = {{
			limit = {{ any_sub_unit = {{ tsin_h_unit_fuel_user_trigger = yes }} }}
			if = {{ limit = {{ has_unit_modifier = tsin_fuel_low }} remove_unit_modifier = tsin_fuel_low }}
			add_unit_modifier = {{ modifier = tsin_fuel_depleted days = 31 mode = add_and_extend }}
		}}
		set_variable = {{ name = tsin_fuel_penalty_on value = 1 }}
	}}
	else_if = {{
		limit = {{ var:tsin_fuel_state = 1 }}
		every_army = {{
			limit = {{ any_sub_unit = {{ tsin_h_unit_fuel_user_trigger = yes }} }}
			if = {{ limit = {{ has_unit_modifier = tsin_fuel_depleted }} remove_unit_modifier = tsin_fuel_depleted }}
			add_unit_modifier = {{ modifier = tsin_fuel_low days = 31 mode = add_and_extend }}
		}}
		set_variable = {{ name = tsin_fuel_penalty_on value = 1 }}
	}}
	else_if = {{
		limit = {{ has_variable = tsin_fuel_penalty_on }}
		every_army = {{
			if = {{ limit = {{ has_unit_modifier = tsin_fuel_low }} remove_unit_modifier = tsin_fuel_low }}
			if = {{ limit = {{ has_unit_modifier = tsin_fuel_depleted }} remove_unit_modifier = tsin_fuel_depleted }}
		}}
		remove_variable = tsin_fuel_penalty_on
	}}
}}
'''


def on_actions():
    return '''# H3: monthly fuel pulse. Gated by age VIII and tsin_motor_transport_advance.
monthly_country_pulse = {
	on_actions = { tsin_h3_fuel_monthly }
}

tsin_h3_fuel_monthly = {
	trigger = { tsin_h_fuel_gate_trigger = yes }
	effect = { tsin_h3_fuel_monthly_effect = yes }
}
'''


def static_modifiers():
    out = ['# H3 fuel penalties (unit category). 사용자 확인 필요.']
    for key, _, _, _, _, mods in MODS:
        body = '\n'.join(f'\t{m} = {v}' for m, v in mods.items())
        out.append(f'{key} = {{\n\tgame_data = {{ category = unit }}\n{body}\n}}')
    return '\n\n'.join(out) + '\n'


def build():
    loc = common.Loc()
    for key, en, ko, den, dko, _ in MODS:
        loc.raw('STATIC_MODIFIER_NAME_' + key, en, ko)
        loc.raw('STATIC_MODIFIER_DESC_' + key, den, dko)
    out = {
        f'{ERA}/in_game/common/script_values/zzz_tsin_h3_fuel_values.txt': script_values(),
        f'{ERA}/in_game/common/scripted_effects/zzz_tsin_h3_fuel_effects.txt': effects(),
        f'{ERA}/in_game/common/on_action/zzz_tsin_h3_fuel_on_actions.txt': on_actions(),
        f'{ERA}/main_menu/common/static_modifiers/zzz_tsin_h3_fuel_modifiers.txt': static_modifiers(),
    }
    out.update(loc.files(ERA, 'tsin_h3_fuel'))
    return {k: common.tidy(v) for k, v in out.items()}


def main(argv=None):
    return common.run('H3 fuel system', build(), argv)


if __name__ == '__main__':
    raise SystemExit(main())
