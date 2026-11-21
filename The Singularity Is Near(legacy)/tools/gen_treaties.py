"""Generate TSIN multi-article bilateral treaties (draft window + ledger).

Treaty rows live in global_variable_map; vanilla effects use hidden scripted_relations
created on accept. TSIN articles adjust mod variables on apply/monthly pulse.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pdx

REGISTRY = 'ui/treaties.json'
PAGE = 8
_map_tmp = 0


def r(field, key='scope:tsin_tr_id'):
    return f'"global_variable_map(tsin_tr_{field}|{key})"'


def put(field, value, key='scope:tsin_tr_id'):
    global _map_tmp
    value = str(value).strip()
    if value.startswith('{'):
        _map_tmp += 1
        tmp = f'tsin_tr_map_tmp_{_map_tmp}'
        return (f'save_temporary_scope_value_as = {{ name = {tmp} value = {value} }} '
                f'add_to_global_variable_map = {{ name = tsin_tr_{field} key = {key} value = scope:{tmp} }}')
    return f'add_to_global_variable_map = {{ name = tsin_tr_{field} key = {key} value = {value} }}'


def load():
    return json.loads(pdx.read_text(pdx.MOD_ROOT / REGISTRY))


def registry_module():
    return {
        'id': 'treaties',
        'shortcuts': [{
            'id': 'treaties',
            'tab': 'overview',
            'title': {'korean': '양자 조약 창', 'english': 'Bilateral treaties'},
            'open_variable': 'tsin_ui_treaties_open',
            'open_scripted_gui': 'tsin_tr_init_window',
        }],
    }


# Hidden relations that carry engine switches; not offered in vanilla diplo lists.
RELATION_SPECS = {
    'alliance': '''tsin_tr_rel_alliance = {
 type = diplomacy relation_type = mutual uses_diplo_capacity = mutual
 block_when_at_war = yes break_on_war = yes break_on_becoming_subject = yes
 annulled_by_peace_treaty = yes disallow_war = yes military_access = yes fleet_basing_rights = yes
 lifts_fog_of_war = yes called_in_defensively = mutual called_in_offensively = mutual
 offer_visible = { always = no } request_visible = { always = no }
 cancel_visible = { always = no } break_visible = { always = no }
 visible = { always = no }
}''',
    'defensive_pact': '''tsin_tr_rel_defensive_pact = {
 type = diplomacy relation_type = mutual uses_diplo_capacity = mutual
 block_when_at_war = yes break_on_war = yes break_on_becoming_subject = yes
 annulled_by_peace_treaty = yes disallow_war = yes called_in_defensively = mutual
 offer_visible = { always = no } request_visible = { always = no }
 cancel_visible = { always = no } break_visible = { always = no }
 visible = { always = no }
}''',
    'non_aggression': '''tsin_tr_rel_non_aggression = {
 type = diplomacy relation_type = mutual
 block_when_at_war = yes break_on_war = yes annulled_by_peace_treaty = yes
 disallow_war = yes
 offer_visible = { always = no } request_visible = { always = no }
 cancel_visible = { always = no } break_visible = { always = no }
 visible = { always = no }
}''',
    'guarantee': '''tsin_tr_rel_guarantee = {
 type = diplomacy relation_type = oneway uses_diplo_capacity = giving
 block_when_at_war = yes break_on_war = yes break_on_becoming_subject = yes
 annulled_by_peace_treaty = yes called_in_defensively = giving
 offer_visible = { always = no } request_visible = { always = no }
 cancel_visible = { always = no } break_visible = { always = no }
 visible = { always = no }
}''',
    'military_access': '''tsin_tr_rel_military_access = {
 type = diplomacy relation_type = oneway block_when_at_war = yes break_on_war = yes
 annulled_by_peace_treaty = yes military_access = yes
 offer_visible = { always = no } request_visible = { always = no }
 cancel_visible = { always = no } break_visible = { always = no }
 visible = { always = no }
}''',
    'fleet_basing': '''tsin_tr_rel_fleet_basing = {
 type = diplomacy relation_type = oneway block_when_at_war = yes break_on_war = yes
 annulled_by_peace_treaty = yes fleet_basing_rights = yes
 offer_visible = { always = no } request_visible = { always = no }
 cancel_visible = { always = no } break_visible = { always = no }
 visible = { always = no }
}''',
    'food_access': '''tsin_tr_rel_food_access = {
 type = diplomacy relation_type = oneway block_when_at_war = yes break_on_war = yes
 annulled_by_peace_treaty = yes food_access = yes
 offer_visible = { always = no } request_visible = { always = no }
 cancel_visible = { always = no } break_visible = { always = no }
 visible = { always = no }
}''',
    'knowledge_share': '''tsin_tr_rel_knowledge_share = {
 type = diplomacy relation_type = mutual break_on_war = yes
 institution_spread_to_first = 0.05 institution_spread_to_second = 0.05
 offer_visible = { always = no } request_visible = { always = no }
 cancel_visible = { always = no } break_visible = { always = no }
 visible = { always = no }
}''',
    'anti_piracy': '''tsin_tr_rel_anti_piracy = {
 type = diplomacy relation_type = mutual break_on_war = yes
 offer_visible = { always = no } request_visible = { always = no }
 cancel_visible = { always = no } break_visible = { always = no }
 visible = { always = no }
}''',
    'tariff_exempt': '''tsin_tr_rel_tariff_exempt = {
 type = diplomacy relation_type = oneway break_on_war = yes
 is_exempt_from_import_tariff = yes
 offer_visible = { always = no } request_visible = { always = no }
 cancel_visible = { always = no } break_visible = { always = no }
 visible = { always = no }
}''',
    'trade_access': '''tsin_tr_rel_trade_access = {
 type = diplomacy relation_type = oneway break_on_war = yes
 offer_visible = { always = no } request_visible = { always = no }
 cancel_visible = { always = no } break_visible = { always = no }
 visible = { always = no }
}''',
    'sound_toll_exempt': '''tsin_tr_rel_sound_toll_exempt = {
 type = diplomacy relation_type = oneway break_on_war = yes
 is_exempt_from_sound_toll = yes
 offer_visible = { always = no } request_visible = { always = no }
 cancel_visible = { always = no } break_visible = { always = no }
 visible = { always = no }
}''',
    'lift_trade_protection': '''tsin_tr_rel_lift_trade_protection = {
 type = diplomacy relation_type = mutual break_on_war = yes
 lifts_trade_protection = yes
 offer_visible = { always = no } request_visible = { always = no }
 cancel_visible = { always = no } break_visible = { always = no }
 visible = { always = no }
}''',
    'divert_trade': '''tsin_tr_rel_divert_trade = {
 type = diplomacy relation_type = oneway break_on_war = yes
 trade_to_first = 0.15
 offer_visible = { always = no } request_visible = { always = no }
 cancel_visible = { always = no } break_visible = { always = no }
 visible = { always = no }
}''',
    'block_foreign_buildings': '''tsin_tr_rel_block_foreign_buildings = {
 type = diplomacy relation_type = oneway break_on_war = yes
 block_building = yes
 offer_visible = { always = no } request_visible = { always = no }
 cancel_visible = { always = no } break_visible = { always = no }
 visible = { always = no }
}''',
    'investment_rights': '''tsin_tr_rel_investment_rights = {
 type = diplomacy relation_type = oneway break_on_war = yes
 offer_visible = { always = no } request_visible = { always = no }
 cancel_visible = { always = no } break_visible = { always = no }
 visible = { always = no }
}''',
}


def _create_rel(rel_key, first, second):
    return (f'if = {{ limit = {{ NOR = {{ '
            f'giving_scripted_relation = {{ type = relation_type:tsin_tr_rel_{rel_key} target = {second} }} '
            f'receiving_scripted_relation = {{ type = relation_type:tsin_tr_rel_{rel_key} target = {second} }} '
            f'has_mutual_scripted_relation = {{ type = relation_type:tsin_tr_rel_{rel_key} target = {second} }} }} }} '
            f'create_relation = {{ first = {first} second = {second} type = relation_type:tsin_tr_rel_{rel_key} }} }}')


def _remove_rel(rel_key, a, b):
    return (f'remove_relation = {{ first = {a} second = {b} type = relation_type:tsin_tr_rel_{rel_key} }} '
            f'remove_relation = {{ first = {b} second = {a} type = relation_type:tsin_tr_rel_{rel_key} }}')


def effects(data):
    global _map_tmp
    _map_tmp = 0
    arts = data['articles']
    lines = ['# GENERATED by tools/gen_treaties.py']

    # Draft helpers
    lines.append('tsin_tr_draft_clear_effect = {')
    lines.append(' remove_variable = tsin_tr_draft_partner')
    for a in arts:
        lines.append(f' set_variable = {{ name = tsin_tr_draft_{a["id"]} value = 0 }}')
        if a['kind'] == 'directional':
            lines.append(f' set_variable = {{ name = tsin_tr_draft_dir_{a["id"]} value = 1 }}')
    lines.append(' set_variable = { name = tsin_tr_draft_binding value = 10 }')
    lines.append(' set_variable = { name = tsin_tr_draft_gold_month value = 0 }')
    lines.append(' set_variable = { name = tsin_tr_draft_gold_lump value = 0 }')
    lines.append(' set_variable = { name = tsin_tr_draft_score value = 0 }')
    lines.append(' remove_variable = tsin_tr_renegotiate_id')
    lines.append('}')

    lines.append('tsin_tr_draft_init_effect = {')
    lines.append(' if = { limit = { NOT = { has_variable = tsin_tr_draft_binding } } tsin_tr_draft_clear_effect = yes }')
    lines.append(' tsin_tr_score_effect = yes')
    lines.append('}')

    for a in arts:
        aid = a['id']
        lines.append(f'tsin_tr_toggle_{aid}_effect = {{')
        lines.append(f' if = {{ limit = {{ var:tsin_tr_draft_{aid} = 0 }} set_variable = {{ name = tsin_tr_draft_{aid} value = 1 }} }}')
        lines.append(f' else = {{ set_variable = {{ name = tsin_tr_draft_{aid} value = 0 }} }}')
        for ex in a.get('exclusive', []):
            lines.append(f' if = {{ limit = {{ var:tsin_tr_draft_{aid} = 1 }} set_variable = {{ name = tsin_tr_draft_{ex} value = 0 }} }}')
        lines.append(' tsin_tr_score_effect = yes')
        lines.append('}')
        if a['kind'] == 'directional':
            lines.append(f'tsin_tr_flip_dir_{aid}_effect = {{')
            lines.append(f' if = {{ limit = {{ var:tsin_tr_draft_dir_{aid} = 1 }} set_variable = {{ name = tsin_tr_draft_dir_{aid} value = 2 }} }}')
            lines.append(f' else = {{ set_variable = {{ name = tsin_tr_draft_dir_{aid} value = 1 }} }}')
            lines.append(' tsin_tr_score_effect = yes')
            lines.append('}')

    for years in data['binding_years']:
        lines.append(f'tsin_tr_set_binding_{years}_effect = {{ set_variable = {{ name = tsin_tr_draft_binding value = {years} }} tsin_tr_score_effect = yes }}')
    for g in data['gold_month_steps']:
        lines.append(f'tsin_tr_set_gold_month_{g}_effect = {{ set_variable = {{ name = tsin_tr_draft_gold_month value = {g} }} tsin_tr_score_effect = yes }}')
    for g in data['gold_lump_steps']:
        lines.append(f'tsin_tr_set_gold_lump_{g}_effect = {{ set_variable = {{ name = tsin_tr_draft_gold_lump value = {g} }} tsin_tr_score_effect = yes }}')

    for p in data['presets']:
        lines.append(f'tsin_tr_preset_{p["id"]}_effect = {{')
        for a in arts:
            on = 1 if a['id'] in p['articles'] else 0
            lines.append(f' set_variable = {{ name = tsin_tr_draft_{a["id"]} value = {on} }}')
            if a['kind'] == 'directional':
                dir_val = 1
                raw = p.get('dirs', {}).get(a['id'])
                if raw == 'mutual' or raw == 2:
                    dir_val = 1  # mutual access approximated as a→b; flip in UI if needed
                elif raw == 'reverse' or raw == 2:
                    dir_val = 2
                lines.append(f' set_variable = {{ name = tsin_tr_draft_dir_{a["id"]} value = {dir_val} }}')
        lines.append(' tsin_tr_score_effect = yes')
        lines.append('}')

    # AI acceptance score cache on proposer
    lines.append('tsin_tr_score_effect = {')
    lines.append(' set_variable = { name = tsin_tr_draft_score value = 10 }')
    lines.append(' if = { limit = { has_variable = tsin_tr_draft_partner }')
    lines.append('  var:tsin_tr_draft_partner = {')
    lines.append('   save_temporary_scope_value_as = { name = tsin_tr_opinion value = "opinion(prev)" }')
    lines.append('  }')
    lines.append('  change_variable = { name = tsin_tr_draft_score add = { value = scope:tsin_tr_opinion divide = 10 } }')
    lines.append(' }')
    for a in arts:
        lines.append(f' if = {{ limit = {{ var:tsin_tr_draft_{a["id"]} = 1 }} change_variable = {{ name = tsin_tr_draft_score add = {a["accept"]} }} }}')
    lines.append(' if = { limit = { var:tsin_tr_draft_gold_month > 0 } change_variable = { name = tsin_tr_draft_score add = { value = var:tsin_tr_draft_gold_month multiply = -0.4 } } }')
    lines.append(' if = { limit = { var:tsin_tr_draft_gold_lump > 0 } change_variable = { name = tsin_tr_draft_score add = { value = var:tsin_tr_draft_gold_lump multiply = -0.05 } } }')
    lines.append('}')

    # Allocate + write ledger from draft (root = proposer = party_a, partner = party_b)
    lines.append('tsin_tr_allocate_effect = {')
    lines.append(' if = { limit = { NOT = { has_global_variable = tsin_tr_next_id } } set_global_variable = { name = tsin_tr_next_id value = 0 } }')
    lines.append(' set_global_variable = { name = tsin_tr_next_id value = { value = global_var:tsin_tr_next_id add = 1 } }')
    lines.append(' save_temporary_scope_value_as = { name = tsin_tr_id value = global_var:tsin_tr_next_id }')
    lines.append(' add_to_global_variable_list = { name = tsin_active_treaties target = scope:tsin_tr_id }')
    lines.append('}')

    lines.append('tsin_tr_write_draft_row_effect = {')
    lines.append(' tsin_tr_allocate_effect = yes')
    lines.append(put('party_a', 'root'))
    lines.append(put('party_b', 'var:tsin_tr_draft_partner'))
    lines.append(put('status', '1'))
    lines.append(put('binding_until', '{ value = current_year multiply = 12 add = current_month add = { value = var:tsin_tr_draft_binding multiply = 12 } }'))
    lines.append(put('gold_month', 'var:tsin_tr_draft_gold_month'))
    lines.append(put('gold_lump', 'var:tsin_tr_draft_gold_lump'))
    lines.append(put('inactive_a', '0'))
    lines.append(put('inactive_b', '0'))
    for a in arts:
        lines.append(put(f'art_{a["id"]}', f'var:tsin_tr_draft_{a["id"]}'))
        if a['kind'] == 'directional':
            lines.append(put(f'dir_{a["id"]}', f'var:tsin_tr_draft_dir_{a["id"]}'))
    lines.append('}')

    # Apply engine relations + immediate effects for current treaty id (scopes party_a/b already saved)
    lines.append('tsin_tr_apply_row_effect = {')
    lines.append(f' save_temporary_scope_value_as = {{ name = tsin_tr_party_a_ref value = {r("party_a")} }}')
    lines.append(f' save_temporary_scope_value_as = {{ name = tsin_tr_party_b_ref value = {r("party_b")} }}')
    # Mutual relation articles
    for key in ('alliance', 'defensive_pact', 'non_aggression', 'knowledge_share', 'anti_piracy', 'lift_trade_protection'):
        lines.append(f' if = {{ limit = {{ {r("art_"+key)} = 1 }}')
        lines.append(f'  {r("party_a")} = {{ {_create_rel(key, "this", "scope:tsin_tr_party_b_ref")} }}')
        lines.append(' }')
    # mutual tariff both ways via vanilla-compatible hidden one-way
    lines.append(f' if = {{ limit = {{ {r("art_mutual_tariff_exempt")} = 1 }}')
    lines.append(f'  {r("party_a")} = {{ {_create_rel("tariff_exempt", "this", "scope:tsin_tr_party_b_ref")} }}')
    lines.append(f'  {r("party_b")} = {{ {_create_rel("tariff_exempt", "this", "scope:tsin_tr_party_a_ref")} }}')
    lines.append(' }')
    # Directional: dir=1 means party_a gives to party_b (first=giver for oneway receiving rights)
    for key in ('guarantee', 'military_access', 'fleet_basing', 'food_access', 'tariff_exempt', 'trade_access',
                'sound_toll_exempt', 'divert_trade', 'block_foreign_buildings', 'investment_rights'):
        lines.append(f' if = {{ limit = {{ {r("art_"+key)} = 1 {r("dir_"+key)} = 1 }}')
        lines.append(f'  {r("party_a")} = {{ {_create_rel(key, "this", "scope:tsin_tr_party_b_ref")} }}')
        lines.append(' }')
        lines.append(f' if = {{ limit = {{ {r("art_"+key)} = 1 {r("dir_"+key)} = 2 }}')
        lines.append(f'  {r("party_b")} = {{ {_create_rel(key, "this", "scope:tsin_tr_party_a_ref")} }}')
        lines.append(' }')
    # Immediate lump gold: dir 1 = a pays b
    lines.append(f' if = {{ limit = {{ {r("art_lump_gold")} = 1 {r("gold_lump")} > 0 }}')
    lines.append(f'  if = {{ limit = {{ {r("dir_lump_gold")} = 1 }}')
    lines.append(f'   {r("party_a")} = {{ add_gold = {{ value = {r("gold_lump")} multiply = -1 }} }}')
    lines.append(f'   {r("party_b")} = {{ add_gold = {r("gold_lump")} }}')
    lines.append('  } else = {')
    lines.append(f'   {r("party_b")} = {{ add_gold = {{ value = {r("gold_lump")} multiply = -1 }} }}')
    lines.append(f'   {r("party_a")} = {{ add_gold = {r("gold_lump")} }}')
    lines.append('  }')
    lines.append(' }')
    # Location cession / treaty port approximations
    lines.append(f' if = {{ limit = {{ {r("art_location_cession")} = 1 }}')
    lines.append(f'  if = {{ limit = {{ {r("dir_location_cession")} = 1 }}')
    lines.append(f'   {r("party_a")} = {{ ordered_owned_location = {{ order_by = total_population max = 1 limit = {{ NOT = {{ is_capital = yes }} }} change_location_owner = scope:tsin_tr_party_b_ref }} }}')
    lines.append('  } else = {')
    lines.append(f'   {r("party_b")} = {{ ordered_owned_location = {{ order_by = total_population max = 1 limit = {{ NOT = {{ is_capital = yes }} }} change_location_owner = scope:tsin_tr_party_a_ref }} }}')
    lines.append('  }')
    lines.append(' }')
    lines.append(f' if = {{ limit = {{ OR = {{ {r("art_treaty_port")} = 1 {r("art_tsin_unequal_open")} = 1 }} }}')
    lines.append(f'  if = {{ limit = {{ OR = {{ AND = {{ {r("art_treaty_port")} = 1 {r("dir_treaty_port")} = 1 }} AND = {{ {r("art_tsin_unequal_open")} = 1 {r("dir_tsin_unequal_open")} = 1 }} }} }}')
    lines.append(f'   {r("party_b")} = {{ ordered_owned_location = {{ order_by = total_population max = 1 limit = {{ is_port = yes }} set_variable = {{ name = tsin_treaty_port_of value = scope:tsin_tr_party_a_ref years = 30 }} add_location_modifier = {{ modifier = tsin_treaty_port years = 30 }} }} }}')
    lines.append(f'   {r("party_b")} = {{ add_country_modifier = {{ modifier = tsin_unequal_treaty years = 30 }} tsin_add_opening_pressure_effect = yes }}')
    lines.append('  } else = {')
    lines.append(f'   {r("party_a")} = {{ ordered_owned_location = {{ order_by = total_population max = 1 limit = {{ is_port = yes }} set_variable = {{ name = tsin_treaty_port_of value = scope:tsin_tr_party_b_ref years = 30 }} add_location_modifier = {{ modifier = tsin_treaty_port years = 30 }} }} }}')
    lines.append(f'   {r("party_a")} = {{ add_country_modifier = {{ modifier = tsin_unequal_treaty years = 30 }} tsin_add_opening_pressure_effect = yes }}')
    lines.append('  }')
    lines.append(' }')
    # TSIN immediate
    lines.append(f' if = {{ limit = {{ {r("art_tsin_revise_unequal")} = 1 }}')
    lines.append(f'  if = {{ limit = {{ OR = {{ {r("party_a")} = {{ has_variable = tsin_modernized }} {r("party_b")} = {{ has_variable = tsin_modernized }} }} }}')
    lines.append(f'   {r("party_a")} = {{ remove_country_modifier = tsin_unequal_treaty }}')
    lines.append(f'   {r("party_b")} = {{ remove_country_modifier = tsin_unequal_treaty }}')
    lines.append('  }')
    lines.append(' }')
    lines.append(f' if = {{ limit = {{ {r("art_tsin_table_bill")} = 1 }}')
    lines.append(f'  if = {{ limit = {{ {r("dir_tsin_table_bill")} = 1 }} {r("party_b")} = {{ set_variable = {{ name = tsin_treaty_bill_promise value = 1 }} }} }}')
    lines.append(f'  else = {{ {r("party_a")} = {{ set_variable = {{ name = tsin_treaty_bill_promise value = 1 }} }} }}')
    lines.append(' }')
    lines.append(f' if = {{ limit = {{ {r("art_tsin_airbase_rights")} = 1 }}')
    lines.append(f'  if = {{ limit = {{ {r("dir_tsin_airbase_rights")} = 1 }}')
    lines.append(f'   {r("party_b")} = {{ set_variable = {{ name = tsin_tr_airbase_bonus value = 5 }} set_variable = {{ name = tsin_tr_fuel_bonus value = 20 }} }}')
    lines.append('  } else = {')
    lines.append(f'   {r("party_a")} = {{ set_variable = {{ name = tsin_tr_airbase_bonus value = 5 }} set_variable = {{ name = tsin_tr_fuel_bonus value = 20 }} }}')
    lines.append('  }')
    lines.append(' }')
    lines.append(f' if = {{ limit = {{ {r("art_tsin_border_sale")} = 1 }}')
    lines.append(f'  if = {{ limit = {{ {r("dir_tsin_border_sale")} = 1 }}')
    lines.append(f'   {r("party_a")} = {{ ordered_owned_location = {{ order_by = total_population max = 1 limit = {{ NOT = {{ is_capital = yes }} }} set_variable = {{ name = tsin_border_sale_marker value = 1 years = 5 }} change_location_owner = scope:tsin_tr_party_b_ref }} }}')
    lines.append(f'   {r("party_b")} = {{ add_gold = {{ value = -100 }} }} {r("party_a")} = {{ add_gold = 100 }}')
    lines.append('  } else = {')
    lines.append(f'   {r("party_b")} = {{ ordered_owned_location = {{ order_by = total_population max = 1 limit = {{ NOT = {{ is_capital = yes }} }} set_variable = {{ name = tsin_border_sale_marker value = 1 years = 5 }} change_location_owner = scope:tsin_tr_party_a_ref }} }}')
    lines.append(f'   {r("party_a")} = {{ add_gold = {{ value = -100 }} }} {r("party_b")} = {{ add_gold = 100 }}')
    lines.append('  }')
    lines.append(' }')
    lines.append(f' if = {{ limit = {{ {r("art_tsin_debt_restructure")} = 1 }}')
    lines.append('  # Soften bilateral TSIN finance contracts between the parties.')
    lines.append('  every_in_global_list = { variable = tsin_active_contracts')
    lines.append('   save_temporary_scope_value_as = { name = tsin_contract_id value = this }')
    lines.append('   if = { limit = {')
    lines.append('    OR = {')
    lines.append('     AND = { "global_variable_map(tsin_fc_lender|scope:tsin_contract_id)" ?= scope:tsin_tr_party_a_ref "global_variable_map(tsin_fc_borrower|scope:tsin_contract_id)" ?= scope:tsin_tr_party_b_ref }')
    lines.append('     AND = { "global_variable_map(tsin_fc_lender|scope:tsin_contract_id)" ?= scope:tsin_tr_party_b_ref "global_variable_map(tsin_fc_borrower|scope:tsin_contract_id)" ?= scope:tsin_tr_party_a_ref }')
    lines.append('    }')
    lines.append('   }')
    lines.append('    save_temporary_scope_value_as = { name = tsin_fc_map_tmp_tr value = { value = "global_variable_map(tsin_fc_maturity|scope:tsin_contract_id)" add = 24 } }')
    lines.append('    add_to_global_variable_map = { name = tsin_fc_maturity key = scope:tsin_contract_id value = scope:tsin_fc_map_tmp_tr }')
    lines.append('    save_temporary_scope_value_as = { name = tsin_fc_map_tmp_tr2 value = { value = "global_variable_map(tsin_fc_rate|scope:tsin_contract_id)" multiply = 0.5 min = 0 } }')
    lines.append('    add_to_global_variable_map = { name = tsin_fc_rate key = scope:tsin_contract_id value = scope:tsin_fc_map_tmp_tr2 }')
    lines.append('    add_to_global_variable_map = { name = tsin_fc_missed key = scope:tsin_contract_id value = 0 }')
    lines.append('   }')
    lines.append('  }')
    lines.append(' }')
    lines.append(f' if = {{ limit = {{ {r("art_tsin_harmonize_standards")} = 1 }}')
    lines.append(f'  if = {{ limit = {{ {r("dir_tsin_harmonize_standards")} = 1 }}')
    lines.append(f'   {r("party_a")} = {{ save_temporary_scope_value_as = {{ name = tsin_tr_std_m value = var:tsin_standard_measure }} save_temporary_scope_value_as = {{ name = tsin_tr_std_g value = var:tsin_standard_gauge }} save_temporary_scope_value_as = {{ name = tsin_tr_std_p value = var:tsin_standard_parts }} save_temporary_scope_value_as = {{ name = tsin_tr_std_e value = var:tsin_standard_electric }} }}')
    lines.append(f'   {r("party_b")} = {{ set_variable = {{ name = tsin_standard_measure value = scope:tsin_tr_std_m }} set_variable = {{ name = tsin_standard_gauge value = scope:tsin_tr_std_g }} set_variable = {{ name = tsin_standard_parts value = scope:tsin_tr_std_p }} set_variable = {{ name = tsin_standard_electric value = scope:tsin_tr_std_e }} }}')
    lines.append('  } else = {')
    lines.append(f'   {r("party_b")} = {{ save_temporary_scope_value_as = {{ name = tsin_tr_std_m value = var:tsin_standard_measure }} save_temporary_scope_value_as = {{ name = tsin_tr_std_g value = var:tsin_standard_gauge }} save_temporary_scope_value_as = {{ name = tsin_tr_std_p value = var:tsin_standard_parts }} save_temporary_scope_value_as = {{ name = tsin_tr_std_e value = var:tsin_standard_electric }} }}')
    lines.append(f'   {r("party_a")} = {{ set_variable = {{ name = tsin_standard_measure value = scope:tsin_tr_std_m }} set_variable = {{ name = tsin_standard_gauge value = scope:tsin_tr_std_g }} set_variable = {{ name = tsin_standard_parts value = scope:tsin_tr_std_p }} set_variable = {{ name = tsin_standard_electric value = scope:tsin_tr_std_e }} }}')
    lines.append('  }')
    lines.append(' }')
    # Flags for ongoing TSIN articles
    for flag in ('tsin_fx_peg', 'tsin_reserve_swap', 'tsin_capital_market_access', 'tsin_strategic_storage',
                 'tsin_power_corridor', 'tsin_rail_telegraph_concession', 'tsin_academic_mission',
                 'tsin_exhibition_pavilion', 'tsin_lend_lease_eq', 'tsin_lend_lease_fuel', 'tsin_airbase_rights',
                 'tsin_pollution_compact', 'tsin_labor_migration', 'tsin_colonial_sphere', 'tsin_bilateral_credit',
                 'monthly_gold', 'monthly_favors', 'goods_quota', 'foreign_credit', 'earn_obligation'):
        lines.append(f' if = {{ limit = {{ {r("art_"+flag)} = 1 }}')
        lines.append(f'  {r("party_a")} = {{ set_variable = {{ name = tsin_tr_flag_{flag} value = 1 }} }}')
        lines.append(f'  {r("party_b")} = {{ set_variable = {{ name = tsin_tr_flag_{flag} value = 1 }} }}')
        lines.append(' }')
    lines.append(f' if = {{ limit = {{ {r("art_call_obligation")} = 1 }}')
    lines.append(f'  {r("party_a")} = {{ add_favors = {{ target = scope:tsin_tr_party_b_ref value = -1 }} }}')
    lines.append(' }')
    lines.append(f' if = {{ limit = {{ {r("art_non_aggression")} = 1 }}')
    lines.append(f'  {r("party_a")} = {{ add_truce_with = {{ target = scope:tsin_tr_party_b_ref years = 5 mutual = yes }} }}')
    lines.append(' }')
    lines.append('}')

    lines.append('tsin_tr_remove_row_relations_effect = {')
    lines.append(f' save_temporary_scope_value_as = {{ name = tsin_tr_party_a_ref value = {r("party_a")} }}')
    lines.append(f' save_temporary_scope_value_as = {{ name = tsin_tr_party_b_ref value = {r("party_b")} }}')
    for key in RELATION_SPECS:
        lines.append(f' {r("party_a")} = {{ {_remove_rel(key, "this", "scope:tsin_tr_party_b_ref")} }}')
    lines.append('}')

    lines.append('tsin_tr_accept_draft_effect = {')
    lines.append(' if = { limit = { has_variable = tsin_tr_draft_partner var:tsin_tr_draft_partner = { num_locations > 0 } }')
    lines.append('  if = { limit = { has_variable = tsin_tr_renegotiate_id }')
    lines.append('   save_temporary_scope_value_as = { name = tsin_tr_id value = var:tsin_tr_renegotiate_id }')
    lines.append(f'   save_temporary_scope_value_as = {{ name = tsin_tr_party_a_ref value = {r("party_a")} }}')
    lines.append(f'   save_temporary_scope_value_as = {{ name = tsin_tr_party_b_ref value = {r("party_b")} }}')
    lines.append('   tsin_tr_remove_row_relations_effect = yes')
    lines.append(put('status', '4'))
    lines.append('   remove_variable = tsin_tr_renegotiate_id')
    lines.append('  }')
    lines.append('  tsin_tr_write_draft_row_effect = yes')
    lines.append('  tsin_tr_apply_row_effect = yes')
    lines.append('  set_variable = { name = tsin_tr_last_id value = scope:tsin_tr_id }')
    lines.append('  tsin_tr_project_page_effect = yes')
    lines.append('  tsin_tr_draft_clear_effect = yes')
    lines.append('  debug_log = tsin_log_hook_tr_accept')
    lines.append(' }')
    lines.append('}')

    lines.append('tsin_tr_send_offer_effect = {')
    lines.append(' tsin_tr_score_effect = yes')
    lines.append(' debug_log = tsin_log_hook_tr_send')
    lines.append(' if = { limit = { has_variable = tsin_tr_draft_partner }')
    lines.append('  if = { limit = { var:tsin_tr_draft_partner = { is_ai = no } }')
    # Player partner: stash offer on partner and notify via variable
    lines.append('   var:tsin_tr_draft_partner = {')
    lines.append('    set_variable = { name = tsin_tr_incoming_from value = prev }')
    lines.append('    set_variable = { name = tsin_tr_incoming_score value = prev.var:tsin_tr_draft_score }')
    lines.append('   }')
    lines.append('   # Copy draft article flags onto partner for review')
    for a in arts:
        lines.append(f'   var:tsin_tr_draft_partner = {{ set_variable = {{ name = tsin_tr_incoming_{a["id"]} value = prev.var:tsin_tr_draft_{a["id"]} }} }}')
    lines.append('  } else = {')
    lines.append('   # AI: accept if score >= 30, reject if <= 0, else coin-flip via score threshold 15')
    lines.append('   if = { limit = { var:tsin_tr_draft_score >= 30 } tsin_tr_accept_draft_effect = yes }')
    lines.append('   else_if = { limit = { var:tsin_tr_draft_score > 0 var:tsin_tr_draft_score >= 15 } tsin_tr_accept_draft_effect = yes }')
    lines.append('   else = { tsin_tr_draft_clear_effect = yes }')
    lines.append('  }')
    lines.append(' }')
    lines.append('}')

    lines.append('tsin_tr_accept_incoming_effect = {')
    lines.append(' if = { limit = { has_variable = tsin_tr_incoming_from }')
    lines.append('  set_variable = { name = tsin_tr_draft_partner value = var:tsin_tr_incoming_from }')
    for a in arts:
        lines.append(f'  set_variable = {{ name = tsin_tr_draft_{a["id"]} value = var:tsin_tr_incoming_{a["id"]} }}')
    lines.append('  set_variable = { name = tsin_tr_draft_binding value = 10 }')
    lines.append('  set_variable = { name = tsin_tr_draft_gold_month value = 0 }')
    lines.append('  set_variable = { name = tsin_tr_draft_gold_lump value = 0 }')
    lines.append('  tsin_tr_accept_draft_effect = yes')
    lines.append('  remove_variable = tsin_tr_incoming_from')
    lines.append('  debug_log = tsin_log_hook_tr_accept_incoming')
    lines.append(' }')
    lines.append('}')

    lines.append('tsin_tr_reject_incoming_effect = { remove_variable = tsin_tr_incoming_from debug_log = tsin_log_hook_tr_reject_incoming }')

    lines.append('tsin_tr_month_effect = {')
    lines.append(' debug_log = tsin_log_hook_tr_month')
    lines.append(' set_global_variable = { name = tsin_tr_review_month value = { value = current_year multiply = 12 add = current_month } }')
    lines.append(' save_scope_as = tsin_tr_coordinator')
    lines.append(' every_in_global_list = { variable = tsin_active_treaties add_to_list = tsin_tr_month_rows }')
    lines.append(' every_in_list = { list = tsin_tr_month_rows')
    lines.append('  save_temporary_scope_value_as = { name = tsin_tr_id value = this }')
    lines.append('  scope:tsin_tr_coordinator = {')
    lines.append(f'   if = {{ limit = {{ {r("status")} = 1 }}')
    lines.append(f'    save_temporary_scope_value_as = {{ name = tsin_tr_party_a_ref value = {r("party_a")} }}')
    lines.append(f'    save_temporary_scope_value_as = {{ name = tsin_tr_party_b_ref value = {r("party_b")} }}')
    lines.append(f'    save_temporary_scope_value_as = {{ name = tsin_tr_bind value = {r("binding_until")} }}')
    lines.append('    save_temporary_scope_value_as = { name = tsin_tr_now value = { value = current_year multiply = 12 add = current_month } }')
    # monthly gold
    lines.append(f'    if = {{ limit = {{ {r("art_monthly_gold")} = 1 {r("gold_month")} > 0 {r("inactive_a")} = 0 {r("inactive_b")} = 0 }}')
    lines.append(f'     if = {{ limit = {{ {r("dir_monthly_gold")} = 1 }}')
    lines.append(f'      if = {{ limit = {{ scope:tsin_tr_party_a_ref = {{ gold >= {r("gold_month")} }} }}')
    lines.append(f'       scope:tsin_tr_party_a_ref = {{ add_gold = {{ value = {r("gold_month")} multiply = -1 }} }}')
    lines.append(f'       scope:tsin_tr_party_b_ref = {{ add_gold = {r("gold_month")} }}')
    lines.append(f'       {put("inactive_a", "0")}')
    lines.append('      } else = {')
    lines.append(f'       {put("inactive_a", "1")}')
    lines.append('      }')
    lines.append('     } else = {')
    lines.append(f'      if = {{ limit = {{ scope:tsin_tr_party_b_ref = {{ gold >= {r("gold_month")} }} }}')
    lines.append(f'       scope:tsin_tr_party_b_ref = {{ add_gold = {{ value = {r("gold_month")} multiply = -1 }} }}')
    lines.append(f'       scope:tsin_tr_party_a_ref = {{ add_gold = {r("gold_month")} }}')
    lines.append(f'       {put("inactive_b", "0")}')
    lines.append('      } else = {')
    lines.append(f'       {put("inactive_b", "1")}')
    lines.append('      }')
    lines.append('     }')
    lines.append('    }')
    # fx peg
    lines.append(f'    if = {{ limit = {{ {r("art_tsin_fx_peg")} = 1 }}')
    lines.append(f'     if = {{ limit = {{ {r("dir_tsin_fx_peg")} = 1 scope:tsin_tr_party_a_ref = {{ has_variable = tsin_fx }} }}')
    lines.append('      scope:tsin_tr_party_a_ref = { save_temporary_scope_value_as = { name = tsin_tr_fx value = var:tsin_fx } }')
    lines.append('      scope:tsin_tr_party_b_ref = { set_variable = { name = tsin_fx value = scope:tsin_tr_fx } }')
    lines.append('     }')
    lines.append(f'     if = {{ limit = {{ {r("dir_tsin_fx_peg")} = 2 scope:tsin_tr_party_b_ref = {{ has_variable = tsin_fx }} }}')
    lines.append('      scope:tsin_tr_party_b_ref = { save_temporary_scope_value_as = { name = tsin_tr_fx value = var:tsin_fx } }')
    lines.append('      scope:tsin_tr_party_a_ref = { set_variable = { name = tsin_fx value = scope:tsin_tr_fx } }')
    lines.append('     }')
    lines.append('    }')
    # lend-lease equipment (small monthly transfer if stocks exist)
    lines.append(f'    if = {{ limit = {{ {r("art_tsin_lend_lease_eq")} = 1 }}')
    lines.append(f'     if = {{ limit = {{ {r("dir_tsin_lend_lease_eq")} = 1 scope:tsin_tr_party_a_ref = {{ has_variable = tsin_eq_small_arms_stockpile var:tsin_eq_small_arms_stockpile >= 10 }} }}')
    lines.append('      scope:tsin_tr_party_a_ref = { change_variable = { name = tsin_eq_small_arms_stockpile subtract = 10 } }')
    lines.append('      scope:tsin_tr_party_b_ref = { if = { limit = { has_variable = tsin_eq_small_arms_stockpile } change_variable = { name = tsin_eq_small_arms_stockpile add = 10 } } else = { set_variable = { name = tsin_eq_small_arms_stockpile value = 10 } } }')
    lines.append('     }')
    lines.append('    }')
    lines.append(f'    if = {{ limit = {{ {r("art_tsin_lend_lease_fuel")} = 1 }}')
    lines.append(f'     if = {{ limit = {{ {r("dir_tsin_lend_lease_fuel")} = 1 scope:tsin_tr_party_a_ref = {{ has_variable = tsin_fuel_stockpile var:tsin_fuel_stockpile >= 20 }} }}')
    lines.append('      scope:tsin_tr_party_a_ref = { change_variable = { name = tsin_fuel_stockpile subtract = 20 } }')
    lines.append('      scope:tsin_tr_party_b_ref = { if = { limit = { has_variable = tsin_fuel_stockpile } change_variable = { name = tsin_fuel_stockpile add = 20 } } else = { set_variable = { name = tsin_fuel_stockpile value = 20 } } }')
    lines.append('     }')
    lines.append('    }')
    lines.append(f'    if = {{ limit = {{ {r("art_monthly_favors")} = 1 }}')
    lines.append(f'     if = {{ limit = {{ {r("dir_monthly_favors")} = 1 }} scope:tsin_tr_party_a_ref = {{ add_favors = {{ target = scope:tsin_tr_party_b_ref value = 1 }} }} }}')
    lines.append(f'     else = {{ scope:tsin_tr_party_b_ref = {{ add_favors = {{ target = scope:tsin_tr_party_a_ref value = 1 }} }} }}')
    lines.append('    }')
    lines.append(f'    if = {{ limit = {{ {r("art_tsin_rail_telegraph_concession")} = 1 }}')
    lines.append(f'     if = {{ limit = {{ {r("dir_tsin_rail_telegraph_concession")} = 1 scope:tsin_tr_party_b_ref = {{ has_variable = tsin_firm_cash var:tsin_firm_cash >= 5 }} }}')
    lines.append('      scope:tsin_tr_party_b_ref = { change_variable = { name = tsin_firm_cash subtract = 5 } }')
    lines.append('      scope:tsin_tr_party_a_ref = { if = { limit = { has_variable = tsin_firm_cash } change_variable = { name = tsin_firm_cash add = 5 } } else = { set_variable = { name = tsin_firm_cash value = 5 } } }')
    lines.append('     }')
    lines.append('    }')
    lines.append(f'    if = {{ limit = {{ {r("art_tsin_power_corridor")} = 1 }}')
    lines.append('     scope:tsin_tr_party_a_ref = { if = { limit = { has_variable = tsin_power_access_index } change_variable = { name = tsin_power_access_index add = 1 } } else = { set_variable = { name = tsin_power_access_index value = 1 } } }')
    lines.append('     scope:tsin_tr_party_b_ref = { if = { limit = { has_variable = tsin_power_access_index } change_variable = { name = tsin_power_access_index add = 1 } } else = { set_variable = { name = tsin_power_access_index value = 1 } } }')
    lines.append('    }')
    lines.append(f'    if = {{ limit = {{ {r("art_tsin_academic_mission")} = 1 }}')
    lines.append(f'     if = {{ limit = {{ {r("dir_tsin_academic_mission")} = 1 }}')
    lines.append('      scope:tsin_tr_party_a_ref = { if = { limit = { has_variable = tsin_knowledge_exchange } change_variable = { name = tsin_knowledge_exchange add = 1 } } else = { set_variable = { name = tsin_knowledge_exchange value = 1 } } }')
    lines.append('      scope:tsin_tr_party_b_ref = { add_prestige = 1 }')
    lines.append('     }')
    lines.append('    }')
    lines.append(f'    if = {{ limit = {{ {r("art_tsin_pollution_compact")} = 1 }}')
    lines.append('     scope:tsin_tr_party_a_ref = { if = { limit = { has_variable = tsin_pollution_filter_timer } change_variable = { name = tsin_pollution_filter_timer add = 1 } } else = { set_variable = { name = tsin_pollution_filter_timer value = 1 } } }')
    lines.append('     scope:tsin_tr_party_b_ref = { if = { limit = { has_variable = tsin_pollution_filter_timer } change_variable = { name = tsin_pollution_filter_timer add = 1 } } else = { set_variable = { name = tsin_pollution_filter_timer value = 1 } } }')
    lines.append('    }')
    lines.append(f'    if = {{ limit = {{ {r("art_tsin_labor_migration")} = 1 }}')
    lines.append(f'     if = {{ limit = {{ {r("dir_tsin_labor_migration")} = 1 }}')
    lines.append('      scope:tsin_tr_party_b_ref = { if = { limit = { has_variable = tsin_migration_attraction } change_variable = { name = tsin_migration_attraction add = 1 } } else = { set_variable = { name = tsin_migration_attraction value = 1 } } }')
    lines.append('     }')
    lines.append('    }')
    lines.append(f'    if = {{ limit = {{ {r("art_tsin_strategic_storage")} = 1 {r("inactive_a")} = 0 }}')
    lines.append(f'     if = {{ limit = {{ {r("dir_tsin_strategic_storage")} = 1 }}')
    lines.append('      scope:tsin_tr_party_a_ref = {')
    lines.append('       every_in_global_list = { variable = tsin_storage_sites')
    lines.append('        limit = { owner ?= prev has_variable = tsin_storage_amount var:tsin_storage_amount >= 10 }')
    lines.append('        change_variable = { name = tsin_storage_amount subtract = 10 }')
    lines.append('        set_variable = tsin_storage_emergency')
    lines.append('        prev = { set_variable = { name = tsin_tr_storage_transfer value = 10 } }')
    lines.append('       }')
    lines.append('      }')
    lines.append('      if = { limit = { scope:tsin_tr_party_a_ref = { has_variable = tsin_tr_storage_transfer } }')
    lines.append('       scope:tsin_tr_party_b_ref = { add_gold = 5 }')
    lines.append('       scope:tsin_tr_party_a_ref = { remove_variable = tsin_tr_storage_transfer }')
    lines.append('      }')
    lines.append('     }')
    lines.append('    }')
    # expire after binding; free withdraw after status 2
    lines.append('    if = { limit = { scope:tsin_tr_now >= scope:tsin_tr_bind }')
    lines.append(f'     {put("status", "2")}')
    lines.append(f'     if = {{ limit = {{ {r("art_earn_obligation")} = 1 }}')
    lines.append('      scope:tsin_tr_party_a_ref = { add_favors = { target = scope:tsin_tr_party_b_ref value = 1 } }')
    lines.append('     }')
    lines.append('     tsin_tr_remove_row_relations_effect = yes')
    lines.append('    }')
    lines.append('   }')
    lines.append('  }')
    lines.append(' }')
    lines.append(' clear_list = tsin_tr_month_rows')
    lines.append('}')

    # Page projection
    lines.append('tsin_tr_project_page_effect = {')
    lines.append(' save_scope_as = tsin_tr_reader')
    lines.append(' if = { limit = { NOT = { has_variable = tsin_tr_page } } set_variable = { name = tsin_tr_page value = 0 } }')
    lines.append(' set_variable = { name = tsin_tr_matches value = 0 }')
    lines.append(' set_variable = { name = tsin_tr_slot value = 0 }')
    lines.append(f' save_temporary_scope_value_as = {{ name = tsin_tr_offset_tmp value = {{ value = var:tsin_tr_page multiply = {PAGE} }} }}')
    lines.append(' set_variable = { name = tsin_tr_offset value = scope:tsin_tr_offset_tmp }')
    for slot in range(1, PAGE + 1):
        for field in ('id', 'partner', 'status', 'binding', 'score'):
            lines.append(f' remove_variable = tsin_tr_row_{slot}_{field}')
    lines.append(' every_in_global_list = { variable = tsin_active_treaties')
    lines.append('  save_temporary_scope_value_as = { name = tsin_tr_id value = this }')
    lines.append(f'  if = {{ limit = {{ OR = {{ {r("party_a")} ?= scope:tsin_tr_reader {r("party_b")} ?= scope:tsin_tr_reader }} {r("status")} > 0 }}')
    lines.append('   scope:tsin_tr_reader = {')
    lines.append('    change_variable = { name = tsin_tr_matches add = 1 }')
    lines.append(f'    if = {{ limit = {{ var:tsin_tr_matches > var:tsin_tr_offset var:tsin_tr_slot < {PAGE} }}')
    lines.append('     change_variable = { name = tsin_tr_slot add = 1 }')
    for slot in range(1, PAGE + 1):
        lines.append(f'     if = {{ limit = {{ var:tsin_tr_slot = {slot} }}')
        lines.append(f'      set_variable = {{ name = tsin_tr_row_{slot}_id value = scope:tsin_tr_id }}')
        lines.append(f'      set_variable = {{ name = tsin_tr_row_{slot}_status value = {r("status")} }}')
        lines.append(f'      set_variable = {{ name = tsin_tr_row_{slot}_binding value = {r("binding_until")} }}')
        lines.append(f'      if = {{ limit = {{ {r("party_a")} ?= this }} set_variable = {{ name = tsin_tr_row_{slot}_partner value = {r("party_b")} }} }}')
        lines.append(f'      else = {{ set_variable = {{ name = tsin_tr_row_{slot}_partner value = {r("party_a")} }} }}')
        lines.append('     }')
    lines.append('    }')
    lines.append('   }')
    lines.append('  }')
    lines.append(' }')
    lines.append('}')

    lines.append('tsin_tr_prev_page_effect = { if = { limit = { var:tsin_tr_page > 0 } change_variable = { name = tsin_tr_page add = -1 } } tsin_tr_project_page_effect = yes }')
    lines.append('tsin_tr_next_page_effect = { change_variable = { name = tsin_tr_page add = 1 } tsin_tr_project_page_effect = yes }')
    for slot in range(1, PAGE + 1):
        lines.append(f'tsin_tr_select_{slot}_effect = {{ if = {{ limit = {{ has_variable = tsin_tr_row_{slot}_id }} set_variable = {{ name = tsin_tr_selected value = var:tsin_tr_row_{slot}_id }} }} }}')

    lines.append('tsin_tr_break_selected_effect = {')
    lines.append(' if = { limit = { has_variable = tsin_tr_selected }')
    lines.append('  save_temporary_scope_value_as = { name = tsin_tr_id value = var:tsin_tr_selected }')
    lines.append(f'  if = {{ limit = {{ OR = {{ {r("status")} = 1 {r("status")} = 2 }} }}')
    lines.append(f'   save_temporary_scope_value_as = {{ name = tsin_tr_party_a_ref value = {r("party_a")} }}')
    lines.append(f'   save_temporary_scope_value_as = {{ name = tsin_tr_party_b_ref value = {r("party_b")} }}')
    lines.append(f'   save_temporary_scope_value_as = {{ name = tsin_tr_bind value = {r("binding_until")} }}')
    lines.append('   save_temporary_scope_value_as = { name = tsin_tr_now value = { value = current_year multiply = 12 add = current_month } }')
    lines.append(f'   if = {{ limit = {{ {r("status")} = 1 scope:tsin_tr_now < scope:tsin_tr_bind }}')
    lines.append('    scope:tsin_tr_party_a_ref = { add_opinion = { target = scope:tsin_tr_party_b_ref modifier = tsin_tr_broken_treaty } add_truce_with = { target = scope:tsin_tr_party_b_ref years = 5 mutual = yes } }')
    lines.append('    scope:tsin_tr_party_b_ref = { add_casus_belli = { target = scope:tsin_tr_party_a_ref type = casus_belli:tsin_tr_broken_treaty_cb } }')
    lines.append('   }')
    lines.append('   tsin_tr_remove_row_relations_effect = yes')
    lines.append(put('status', '3'))
    lines.append('   debug_log = tsin_log_hook_tr_break')
    lines.append('  }')
    lines.append('  tsin_tr_project_page_effect = yes')
    lines.append(' }')
    lines.append('}')

    lines.append('tsin_tr_renegotiate_selected_effect = {')
    lines.append(' if = { limit = { has_variable = tsin_tr_selected }')
    lines.append('  save_temporary_scope_value_as = { name = tsin_tr_id value = var:tsin_tr_selected }')
    lines.append(f'  if = {{ limit = {{ OR = {{ {r("status")} = 1 {r("status")} = 2 }} }}')
    lines.append('   tsin_tr_draft_clear_effect = yes')
    lines.append(f'   if = {{ limit = {{ {r("party_a")} ?= root }} set_variable = {{ name = tsin_tr_draft_partner value = {r("party_b")} }} }}')
    lines.append(f'   else = {{ set_variable = {{ name = tsin_tr_draft_partner value = {r("party_a")} }} }}')
    lines.append('   set_variable = { name = tsin_tr_renegotiate_id value = scope:tsin_tr_id }')
    lines.append('   debug_log = tsin_log_hook_tr_renegotiate')
    for a in arts:
        if a.get('immediate'):
            lines.append(f'   set_variable = {{ name = tsin_tr_draft_{a["id"]} value = 0 }}')
        else:
            lines.append(f'   set_variable = {{ name = tsin_tr_draft_{a["id"]} value = {r("art_"+a["id"])} }}')
            if a['kind'] == 'directional':
                lines.append(f'   set_variable = {{ name = tsin_tr_draft_dir_{a["id"]} value = {r("dir_"+a["id"])} }}')
    lines.append(f'   set_variable = {{ name = tsin_tr_draft_gold_month value = {r("gold_month")} }}')
    lines.append('   set_variable = { name = tsin_tr_draft_gold_lump value = 0 }')
    lines.append('   tsin_tr_score_effect = yes')
    lines.append('  }')
    lines.append(' }')
    lines.append('}')

    lines.append('tsin_tr_open_with_partner_effect = {')
    lines.append(' tsin_tr_draft_clear_effect = yes')
    lines.append(' set_variable = { name = tsin_tr_draft_partner value = scope:recipient }')
    lines.append(' remove_variable = tsin_tr_renegotiate_id')
    lines.append(' tsin_tr_score_effect = yes')
    lines.append(' tsin_tr_project_page_effect = yes')
    lines.append(' debug_log = tsin_log_hook_tr_open_partner')
    lines.append('}')

    lines.append('tsin_tr_open_effect = {')
    lines.append(' tsin_tr_draft_init_effect = yes')
    lines.append(' tsin_tr_project_page_effect = yes')
    lines.append('}')

    lines.append('tsin_tr_succession_effect = {')
    lines.append(' save_scope_as = tsin_tr_coordinator')
    lines.append(' every_in_global_list = { variable = tsin_active_treaties')
    lines.append('  save_temporary_scope_value_as = { name = tsin_tr_id value = this }')
    lines.append('  scope:tsin_tr_coordinator = {')
    lines.append(f'   if = {{ limit = {{ {r("party_a")} ?= scope:tsin_annex_target }} {put("party_a", "scope:tsin_annex_recipient")} }}')
    lines.append(f'   if = {{ limit = {{ {r("party_b")} ?= scope:tsin_annex_target }} {put("party_b", "scope:tsin_annex_recipient")} }}')
    lines.append('  }')
    lines.append(' }')
    lines.append('}')

    return '\n'.join(lines) + '\n'


def on_actions():
    return '''monthly_country_pulse = { on_actions = { tsin_tr_global_monthly } }
tsin_tr_global_monthly = {
 trigger = {
  has_global_variable = tsin_tr_next_id
  OR = {
   NOT = { has_global_variable = tsin_tr_review_month }
   tsin_contract_calendar_month > global_var:tsin_tr_review_month
  }
 }
 effect = { tsin_tr_month_effect = yes }
}
'''


def scripted_guis(data):
    g = ['# GENERATED by tools/gen_treaties.py']
    def sg(key, valid, effect):
        g.append(f'{key} = {{ scope = country is_shown = {{ always = yes }} is_valid = {{ {valid} }} effect = {{ {effect} }} }}')
    sg('tsin_tr_open', 'is_ai = no', 'tsin_tr_open_effect = yes')
    sg('tsin_tr_init_window', 'is_ai = no', 'tsin_tr_draft_init_effect = yes tsin_tr_project_page_effect = yes')
    sg('tsin_tr_send', 'is_ai = no has_variable = tsin_tr_draft_partner', 'tsin_tr_send_offer_effect = yes')
    sg('tsin_tr_clear', 'is_ai = no', 'tsin_tr_draft_clear_effect = yes')
    sg('tsin_tr_accept_incoming', 'is_ai = no has_variable = tsin_tr_incoming_from', 'tsin_tr_accept_incoming_effect = yes')
    sg('tsin_tr_reject_incoming', 'is_ai = no has_variable = tsin_tr_incoming_from', 'tsin_tr_reject_incoming_effect = yes')
    sg('tsin_tr_break', 'is_ai = no has_variable = tsin_tr_selected', 'tsin_tr_break_selected_effect = yes')
    sg('tsin_tr_renegotiate', 'is_ai = no has_variable = tsin_tr_selected', 'tsin_tr_renegotiate_selected_effect = yes')
    sg('tsin_tr_prev', 'is_ai = no has_variable = tsin_tr_page var:tsin_tr_page > 0', 'tsin_tr_prev_page_effect = yes')
    sg('tsin_tr_next', 'is_ai = no', 'tsin_tr_next_page_effect = yes')
    for a in data['articles']:
        sg(f'tsin_tr_toggle_{a["id"]}', 'is_ai = no', f'tsin_tr_toggle_{a["id"]}_effect = yes')
        if a['kind'] == 'directional':
            sg(f'tsin_tr_flip_{a["id"]}', f'is_ai = no var:tsin_tr_draft_{a["id"]} = 1', f'tsin_tr_flip_dir_{a["id"]}_effect = yes')
    for y in data['binding_years']:
        sg(f'tsin_tr_bind_{y}', 'is_ai = no', f'tsin_tr_set_binding_{y}_effect = yes')
    for v in data['gold_month_steps']:
        sg(f'tsin_tr_gm_{v}', 'is_ai = no', f'tsin_tr_set_gold_month_{v}_effect = yes')
    for v in data['gold_lump_steps']:
        sg(f'tsin_tr_gl_{v}', 'is_ai = no', f'tsin_tr_set_gold_lump_{v}_effect = yes')
    for p in data['presets']:
        sg(f'tsin_tr_preset_{p["id"]}', 'is_ai = no has_variable = tsin_tr_draft_partner', f'tsin_tr_preset_{p["id"]}_effect = yes')
    for slot in range(1, PAGE + 1):
        sg(f'tsin_tr_select_{slot}', f'is_ai = no has_variable = tsin_tr_row_{slot}_id', f'tsin_tr_select_{slot}_effect = yes')
    return '\n'.join(g) + '\n'


def country_interaction():
    return '''tsin_negotiate_treaty = {
 type = diplomacy
 category = CATEGORY_FRIENDLY_ACTIONS
 ai_tick = never
 potential = { always = yes }
 allow = {
  scope:actor = { is_ai = no has_limited_diplomacy = no }
  scope:recipient = { exists = capital NOT = { this = scope:actor } }
 }
 select_trigger = {
  looking_for_a = country
  target_flag = recipient
  name = "TSIN_TR_CHOOSE_PARTNER"
  visible = {
   exists = capital
   within_diplomatic_range = scope:actor
   NOT = { this = scope:actor }
  }
 }
 effect = {
  scope:actor = { tsin_tr_open_with_partner_effect = yes }
 }
}
'''


def casus_belli():
    return '''# Granted only by treaty early-withdrawal; not manually created.
tsin_tr_broken_treaty_cb = {
	speed = 8
	create_visible = { always = no }
	create_enabled = { always = no }
	war_goal_type = take_capital
	ai_will_do = {
		add = { desc = "BASE" value = 20 }
	}
}
'''


def opinion_modifier():
    return '''tsin_tr_broken_treaty = {
	value = -50
	yearly_decay = 5
}
'''


def _btn(key, scripted, width):
    return (
        f'button_regular = {{ size = {{ {width} 36 }} '
        f'enabled = "[GetScriptedGui(\'{scripted}\').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" '
        f'action_tooltip = {{ title = "{key}" on_action = "[GetScriptedGui(\'{scripted}\').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" }} '
        f'text_single = {{ size = {{ {width-6} 32 }} parentanchor = center autoresize = no maximumsize = {{ {width-6} 32 }} '
        f'fontsize = 12 fontsize_min = 9 align = center|nobaseline elide = right text = "{key}" }} }}'
    )


def gui(data):
    v = lambda n: f"GetPlayer.MakeScope.GetVariable('{n}')"
    ui = []
    ui.append('''window = {
 name = "tsin_treaties_window" layer = topbar parentanchor = center widgetanchor = center
 size = { 1100 920 } movable = yes allow_outside = yes datacontext = "[GetPlayer]"
 visible = "[And(GetPlayer.IsValid, Or(GetVariableSystem.Exists('tsin_ui_treaties_open'), Or(GetPlayer.MakeScope.GetVariable('tsin_tr_draft_partner').IsSet, GetPlayer.MakeScope.GetVariable('tsin_tr_incoming_from').IsSet)))]"
 widget = { size = { 100% 100% } using = bg_window_default_alt
 widget = { parentanchor = right position = { -5 5 } size = { 40 40 } ui_direction_button_holder_right = {}
  button_close_alt = { blockoverride "close_on_action" {
   on_action = "[GetVariableSystem.Clear('tsin_ui_treaties_open')]"
   on_action = "[GetScriptedGui('tsin_tr_clear').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
  } } }
 vbox = { using = window_margin_alt spacing = 6
 window_header_alt = { blockoverride "header_text" { text = "TSIN_TR_TITLE" } }
 text_multi = { maximumsize = { 1040 -1 } fontsize = 13 text = "TSIN_TR_HELP" }
 text_single = { visible = "[GetPlayer.MakeScope.GetVariable('tsin_tr_draft_partner').IsSet]" fontsize = 14 text = "TSIN_TR_PARTNER" }
 text_single = { visible = "[GetPlayer.MakeScope.GetVariable('tsin_tr_incoming_from').IsSet]" fontsize = 14 text = "TSIN_TR_INCOMING" }
 hbox = { spacing = 8''')
    ui.append(_btn('TSIN_TR_ACCEPT_IN', 'tsin_tr_accept_incoming', 200))
    ui.append(_btn('TSIN_TR_REJECT_IN', 'tsin_tr_reject_incoming', 200))
    ui.append('}')
    ui.append(f'text_single = {{ fontsize = 14 text = "TSIN_TR_SCORE" }}')
    ui.append('hbox = { spacing = 6')
    ui.append(_btn('TSIN_TR_SEND', 'tsin_tr_send', 160))
    ui.append(_btn('TSIN_TR_CLEAR', 'tsin_tr_clear', 140))
    ui.append(_btn('TSIN_TR_RENEG', 'tsin_tr_renegotiate', 160))
    ui.append(_btn('TSIN_TR_BREAK', 'tsin_tr_break', 180))
    ui.append('}')
    ui.append('text_single = { fontsize = 16 text = "TSIN_TR_PRESETS" }')
    ui.append('hbox = { spacing = 6')
    for p in data['presets'][:5]:
        ui.append(_btn(f'TSIN_TR_PRESET_{p["id"].upper()}', f'tsin_tr_preset_{p["id"]}', 150))
    ui.append('}')
    ui.append('hbox = { spacing = 6')
    for p in data['presets'][5:]:
        ui.append(_btn(f'TSIN_TR_PRESET_{p["id"].upper()}', f'tsin_tr_preset_{p["id"]}', 150))
    ui.append('}')
    ui.append('text_single = { fontsize = 16 text = "TSIN_TR_BINDING" }')
    ui.append('hbox = { spacing = 6')
    for y in data['binding_years']:
        ui.append(_btn(f'TSIN_TR_BIND_{y}', f'tsin_tr_bind_{y}', 80))
    ui.append('}')
    ui.append('text_single = { fontsize = 16 text = "TSIN_TR_GOLD_MONTH" }')
    ui.append('hbox = { spacing = 4')
    for g in data['gold_month_steps']:
        ui.append(_btn(f'TSIN_TR_GM_{g}', f'tsin_tr_gm_{g}', 70))
    ui.append('}')
    ui.append('text_single = { fontsize = 16 text = "TSIN_TR_GOLD_LUMP" }')
    ui.append('hbox = { spacing = 4')
    for g in data['gold_lump_steps']:
        ui.append(_btn(f'TSIN_TR_GL_{g}', f'tsin_tr_gl_{g}', 70))
    ui.append('}')
    ui.append('''scrollarea = { size = { 1060 420 } scrollbarpolicy_horizontal = always_off
 scrollbar_vertical = { using = Scrollbar_Vertical }
 scrollwidget = { vbox = { spacing = 8 margin = { 8 6 }''')
    by_cat = {}
    for a in data['articles']:
        by_cat.setdefault(a['category'], []).append(a)
    cat_title = {c['id']: c for c in data['categories']}
    for cid, arts in by_cat.items():
        title = cat_title.get(cid, {'english': cid})
        ui.append(f'text_single = {{ fontsize = 15 text = "TSIN_TR_CAT_{cid.upper()}" }}')
        # rows of toggles
        row = []
        for a in arts:
            row.append(a)
            if len(row) == 3:
                ui.append('hbox = { spacing = 6')
                for x in row:
                    ui.append(_btn(f'TSIN_TR_ART_{x["id"].upper()}', f'tsin_tr_toggle_{x["id"]}', 240))
                    if x['kind'] == 'directional':
                        ui.append(_btn(f'TSIN_TR_DIR_{x["id"].upper()}', f'tsin_tr_flip_{x["id"]}', 90))
                ui.append('}')
                row = []
        if row:
            ui.append('hbox = { spacing = 6')
            for x in row:
                ui.append(_btn(f'TSIN_TR_ART_{x["id"].upper()}', f'tsin_tr_toggle_{x["id"]}', 240))
                if x['kind'] == 'directional':
                    ui.append(_btn(f'TSIN_TR_DIR_{x["id"].upper()}', f'tsin_tr_flip_{x["id"]}', 90))
            ui.append('}')
    ui.append('} } }')
    ui.append('text_single = { fontsize = 16 text = "TSIN_TR_ACTIVE" }')
    ui.append('hbox = { spacing = 8')
    ui.append(_btn('TSIN_TR_PREV', 'tsin_tr_prev', 120))
    ui.append(_btn('TSIN_TR_NEXT', 'tsin_tr_next', 120))
    ui.append('}')
    for slot in range(1, PAGE + 1):
        ui.append(
            f'hbox = {{ spacing = 6 visible = "[{v(f"tsin_tr_row_{slot}_id")}.IsSet]" '
            f'widget = {{ size = {{ 280 26 }} datacontext = "[{v(f"tsin_tr_row_{slot}_partner")}.GetCountry]" '
            f'text_single = {{ size = {{ 270 26 }} autoresize = no fontsize = 13 text = "[Country.GetName]" }} }} '
            f'text_single = {{ size = {{ 80 26 }} fontsize = 13 text = "[{v(f"tsin_tr_row_{slot}_status")}.GetValue|0]" }} '
            f'text_single = {{ size = {{ 120 26 }} fontsize = 13 text = "[{v(f"tsin_tr_row_{slot}_binding")}.GetValue|0]" }} '
            + _btn(f'TSIN_TR_SEL_{slot}', f'tsin_tr_select_{slot}', 100) + ' }'
        )
    ui.append('} } }')
    return '\n'.join(ui) + '\n'


def localization(data):
    en, ko = {}, {}
    def both(k, e, ktxt):
        en[k] = e
        ko[k] = ktxt
    both('TSIN_TR_TITLE', 'Bilateral treaties', '양자 조약')
    both('TSIN_TR_HELP', 'Pick a partner via Negotiate Treaty, toggle articles, set binding and gold, then Send. AI accepts when the score is high enough. Hide buttons flip directional giver.', '외교 행동 「조약 협상」으로 상대를 고른 뒤 조항·구속기간·금을 설정하고 보내십시오. AI는 수락 점수가 충분하면 수락합니다. 방향 버튼으로 제공/수혜를 바꿉니다.')
    both('TSIN_TR_INCOMING', 'Incoming treaty offer', '수신된 조약 제안')
    both('TSIN_TR_SCORE', "Acceptance score: [GetPlayer.MakeScope.GetVariable('tsin_tr_draft_score').GetValue|0]", "수락 점수: [GetPlayer.MakeScope.GetVariable('tsin_tr_draft_score').GetValue|0]")
    both('TSIN_TR_SEND', 'Send offer', '제안 보내기')
    both('TSIN_TR_CLEAR', 'Clear draft', '초안 비우기')
    both('TSIN_TR_RENEG', 'Renegotiate selected', '선택 조약 재협상')
    both('TSIN_TR_BREAK', 'Withdraw selected', '선택 조약 파기')
    both('TSIN_TR_ACCEPT_IN', 'Accept offer', '제안 수락')
    both('TSIN_TR_REJECT_IN', 'Reject offer', '제안 거절')
    both('TSIN_TR_PRESETS', 'Packages', '패키지')
    both('TSIN_TR_BINDING', 'Binding years', '구속 기간(년)')
    both('TSIN_TR_GOLD_MONTH', 'Monthly gold', '월간 금')
    both('TSIN_TR_GOLD_LUMP', 'Lump-sum gold', '일시금')
    both('TSIN_TR_ACTIVE', 'Your treaties', '보유 조약')
    both('TSIN_TR_PREV', 'Prev', '이전')
    both('TSIN_TR_NEXT', 'Next', '다음')
    both('TSIN_TR_CHOOSE_PARTNER', 'Choose treaty partner', '조약 상대 선택')
    both('TSIN_TR_PARTNER', "Partner selected. Toggle articles and Send.", "상대가 선택되었습니다. 조항을 고른 뒤 보내십시오.")
    both('tsin_negotiate_treaty', 'Negotiate multi-article treaty', '다조항 조약 협상')
    both('tsin_negotiate_treaty_desc', 'Select this country as partner and open the TSIN multi-article treaty draft.', '이 국가를 조약 상대로 고르고 다조항 초안 창을 엽니다.')
    both('tsin_tr_broken_treaty_cb', 'Broken Treaty', '조약 파기')
    both('tsin_tr_broken_treaty', 'Broken Treaty', '조약 파기')
    for c in data['categories']:
        both(f'TSIN_TR_CAT_{c["id"].upper()}', c['english'], c['korean'])
    for a in data['articles']:
        both(f'TSIN_TR_ART_{a["id"].upper()}', a['english'], a['korean'])
        if a['kind'] == 'directional':
            both(f'TSIN_TR_DIR_{a["id"].upper()}', 'Dir', '방향')
    for y in data['binding_years']:
        both(f'TSIN_TR_BIND_{y}', str(y), str(y))
    for g in data['gold_month_steps']:
        both(f'TSIN_TR_GM_{g}', str(g), str(g))
    for g in data['gold_lump_steps']:
        both(f'TSIN_TR_GL_{g}', str(g), str(g))
    for p in data['presets']:
        both(f'TSIN_TR_PRESET_{p["id"].upper()}', p['english'], p['korean'])
    for slot in range(1, PAGE + 1):
        both(f'TSIN_TR_SEL_{slot}', 'Select', '선택')
    return en, ko


def build():
    data = load()
    en, ko = localization(data)
    out = {
        'in_game/common/scripted_effects/tsin_treaties.txt': effects(data),
        'in_game/common/scripted_guis/tsin_treaties.txt': scripted_guis(data),
        'in_game/common/on_action/tsin_treaties_on_actions.txt': on_actions(),
        'in_game/common/scripted_relations/tsin_treaty_relations.txt': '\n\n'.join(RELATION_SPECS.values()) + '\n',
        'in_game/common/country_interactions/tsin_negotiate_treaty.txt': country_interaction(),
        'in_game/common/casus_belli/tsin_treaty_cb.txt': casus_belli(),
        'in_game/common/biases/tsin_treaty_opinions.txt': opinion_modifier(),
        'in_game/gui/tsin_treaties.gui': gui(data),
        'in_game/gui/scripted_widgets/tsin_treaties.txt': 'gui/tsin_treaties.gui = tsin_treaties_window\n',
        'main_menu/localization/english/tsin_treaties_l_english.yml': 'l_english:\n' + ''.join(f' {k}: {json.dumps(v, ensure_ascii=False)}\n' for k, v in en.items()),
        'main_menu/localization/korean/tsin_treaties_l_korean.yml': 'l_korean:\n' + ''.join(f' {k}: {json.dumps(v, ensure_ascii=False)}\n' for k, v in ko.items()),
    }
    return out


def sync_dashboard():
    path = pdx.MOD_ROOT / 'ui/dashboard_registry.json'
    data = json.loads(pdx.read_text(path))
    modules = [m for m in data.get('modules', []) if m.get('id') != 'treaties']
    # Prefer attaching the treaties shortcut onto manual_surveys if present.
    found = False
    for m in modules:
        if m.get('id') == 'manual_surveys':
            shortcuts = [s for s in m.get('shortcuts', []) if s.get('id') != 'treaties']
            shortcuts.append(registry_module()['shortcuts'][0])
            m['shortcuts'] = shortcuts
            found = True
            break
    if not found:
        modules.append(registry_module())
    data['modules'] = modules
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    output = build()
    bad = []
    for rel, text in output.items():
        path = pdx.MOD_ROOT / rel
        if args.check:
            if not path.exists() or pdx.read_text(path) != text:
                bad.append(rel)
        else:
            pdx.write_text_bom(path, text)
    if not args.check:
        sync_dashboard()
    print(f'Treaties: {len(output)} files; {len(bad)} mismatches')
    for rel in bad:
        print(rel)
    return bool(bad)


if __name__ == '__main__':
    raise SystemExit(main())
