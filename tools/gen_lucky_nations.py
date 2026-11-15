"""Russian lucky-nation pilot with opt-in territorial fallback and human-realm veto."""
import argparse
import json
import pdx


def build():
    config = json.loads((pdx.MOD_ROOT/'data/historical_progression.json').read_text(encoding='utf-8'))['russia']
    start, fallback, end = [config[k] for k in ['support_start','fallback_start','support_end']]
    cores = config['protected_locations']
    ownership = '\n'.join(f'owns = location:{loc}' for loc in cores)
    transferable = '\n'.join(f'''location:{loc} = {{ OR = {{
owner ?= scope:tsin_lucky_candidate
AND = {{
    controller = owner
    is_capital = no
    owner ?= {{ tsin_history_ai_realm = yes at_war = no num_locations > 1 }}
}}
}} }}''' for loc in cores)
    # Per-owner safeguard counts *all* outgoing locations before any transfer. This
    # prevents four individually harmless checks from fully consuming one owner.
    depletion = '\n'.join(f'''location:{loc}.owner ?= {{
    trigger_if = {{
        limit = {{ NOT = {{ this = scope:tsin_lucky_candidate }} }}
        num_locations > tsin_lucky_russia_outgoing_count
    }}
}}''' for loc in cores)
    outgoing = '\n'.join(f'if = {{ limit = {{ owns = location:{loc} }} add = 1 }}' for loc in cores)
    moves = '\n'.join(f'location:{loc} = {{ if = {{ limit = {{ NOT = {{ owner ?= scope:tsin_lucky_candidate }} }} change_location_owner = scope:tsin_lucky_candidate }} }}' for loc in cores)
    triggers = f'''# GENERATED. Shared human protection lives in gen_historical_progression.py.
tsin_lucky_russia_candidate_trigger = {{
    tsin_history_ai_realm = yes
    is_subject = no
    is_junior_partner = no
    culture = {{ has_culture_group = culture_group:russian_group }}
    num_locations > 1
    OR = {{ {' '.join('owns = location:'+x for x in cores)} }}
}}
tsin_lucky_human_war_trigger = {{
    any_country = {{ tsin_history_human_realm = yes is_at_war_with = prev }}
}}
tsin_lucky_russia_campaign_trigger = {{
    current_year >= {start}
    current_year < {end}
    NOT = {{ has_game_rule = tsin_lucky_nations_off }}
    NOT = {{ country_exists = c:RUS }}
    NOT = {{ tsin_history_russia_player_blocked = yes }}
}}
tsin_lucky_russia_force_trigger = {{
    tsin_lucky_russia_campaign_trigger = yes
    has_game_rule = tsin_lucky_nations_force
    current_year >= {fallback}
    tsin_lucky_russia_candidate_trigger = yes
    at_war = no
    NOT = {{ tsin_lucky_human_war_trigger = yes }}
{transferable}
{depletion}
}}
'''
    values = 'tsin_lucky_russia_outgoing_count = { value = 0\n' + outgoing + '\n}\n'
    modifiers = '''tsin_lucky_russia_support = {
    game_data = { category = country }
    land_morale_modifier = 0.20
    discipline = 0.10
    global_manpower_modifier = 0.30
    siege_ability = 0.20
}
tsin_lucky_russia_support_strong = {
    game_data = { category = country }
    land_morale_modifier = 0.30
    discipline = 0.15
    global_manpower_modifier = 0.50
    siege_ability = 0.25
}
'''
    effects = f'''# GENERATED. Coordinator runs once per world year, not once per country.
tsin_lucky_remove_support_effect = {{
    remove_country_modifier = tsin_lucky_russia_support
    remove_country_modifier = tsin_lucky_russia_support_strong
}}
tsin_lucky_cleanup_effect = {{
    every_country = {{
        limit = {{ has_variable = tsin_lucky_support_years }}
        if = {{
            limit = {{ OR = {{
                NOT = {{ tsin_lucky_russia_campaign_trigger = yes }}
                NOT = {{ tsin_lucky_russia_candidate_trigger = yes }}
                tsin_lucky_human_war_trigger = yes
            }} }}
            tsin_lucky_remove_support_effect = yes
        }}
    }}
}}
tsin_lucky_russia_form_effect = {{
    save_scope_as = tsin_lucky_candidate
    # Re-check the complete transaction immediately before *any* ownership change.
    if = {{
        limit = {{ tsin_lucky_russia_force_trigger = yes }}
{moves}
        form_country = formable_country:RUS_f
        if = {{
            limit = {{ tag = RUS }}
            tsin_lucky_remove_support_effect = yes
            set_global_variable = {{ name = tsin_lucky_russia_formed_year value = current_year }}
            debug_log = tsin_lucky_russia_formed_log
        }}
    }}
}}
tsin_lucky_russia_year_effect = {{
    set_global_variable = {{ name = tsin_lucky_review_year value = current_year }}
    # Remove the previous year's support first: only the newly selected actor gets it.
    every_country = {{ limit = {{ has_variable = tsin_lucky_support_years }} tsin_lucky_remove_support_effect = yes }}
    if = {{
        limit = {{ tsin_lucky_russia_campaign_trigger = yes }}
        # Before 1700, a saved HEX role means this actor is left to HEX. The marker
        # is a conservative compatibility hint, not proof of current mod activation.
        if = {{
            limit = {{ c:MOS ?= {{ tsin_lucky_russia_candidate_trigger = yes }} }}
            c:MOS = {{ save_scope_as = tsin_lucky_candidate }}
        }}
        else_if = {{
            limit = {{ location:moscow.owner ?= {{ tsin_lucky_russia_candidate_trigger = yes }} }}
            location:moscow.owner = {{ save_scope_as = tsin_lucky_candidate }}
        }}
        else = {{
            ordered_country = {{
                limit = {{ tsin_lucky_russia_candidate_trigger = yes }}
                order_by = num_locations max = 1
                save_scope_as = tsin_lucky_candidate
            }}
        }}
        if = {{
            limit = {{ exists = scope:tsin_lucky_candidate }}
            scope:tsin_lucky_candidate = {{
                if = {{
                    limit = {{
                        NOT = {{ tsin_lucky_human_war_trigger = yes }}
                        NOT = {{ AND = {{ current_year < {fallback} has_variable = hex_key }} }}
                    }}
                    if = {{ limit = {{ NOT = {{ has_variable = tsin_lucky_support_years }} }} set_variable = {{ name = tsin_lucky_support_years value = 0 }} }}
                    change_variable = {{ name = tsin_lucky_support_years add = 1 }}
                    if = {{ limit = {{ var:tsin_lucky_support_years >= 15 }} add_country_modifier = {{ modifier = tsin_lucky_russia_support_strong years = 2 mode = replace }} }}
                    else = {{ add_country_modifier = {{ modifier = tsin_lucky_russia_support years = 2 mode = replace }} }}
                    # No land needs to move if the native core cities already belong to us.
                    if = {{
                        limit = {{ {ownership} }}
                        form_country = formable_country:RUS_f
                        tsin_lucky_remove_support_effect = yes
                    }}
                    else_if = {{
                        limit = {{ tsin_lucky_russia_force_trigger = yes }}
                        trigger_event_non_silently = tsin_lucky_russia.1
                    }}
                }}
            }}
        }}
    }}
}}
'''
    on_actions = f'''yearly_country_pulse = {{ on_actions = {{ tsin_lucky_yearly }} }}
on_war_declared = {{ on_actions = {{ tsin_lucky_cleanup }} }}
on_join_war = {{ on_actions = {{ tsin_lucky_cleanup }} }}
on_new_country_formed = {{ on_actions = {{ tsin_lucky_cleanup }} }}
on_took_location_in_peace_treaty = {{ on_actions = {{ tsin_lucky_cleanup }} }}
tsin_lucky_cleanup = {{ effect = {{ tsin_lucky_cleanup_effect = yes }} }}
tsin_lucky_yearly = {{
    trigger = {{
        current_year >= {start}
        current_year <= {end}
        OR = {{ NOT = {{ has_global_variable = tsin_lucky_review_year }} current_year > global_var:tsin_lucky_review_year }}
    }}
    effect = {{ tsin_lucky_russia_year_effect = yes }}
}}
'''
    rules = '''tsin_lucky_nations = {
    default = tsin_lucky_nations_assisted
    tsin_lucky_nations_assisted = { flag = general_rule }
    tsin_lucky_nations_force = { flag = general_rule }
    tsin_lucky_nations_off = { flag = general_rule }
}
'''
    events = '''namespace = tsin_lucky_russia
tsin_lucky_russia.1 = {
    type = country_event
    title = tsin_lucky_russia.1.title
    desc = tsin_lucky_russia.1.desc
    outcome = neutral
    illustration_tags = { 10 = exterior 10 = regular }
    trigger = { is_ai = yes }
    immediate = { tsin_lucky_russia_form_effect = yes }
    option = { name = tsin_lucky_russia.1.a }
}
'''
    en = {
        'tsin_lucky_nations':'TSIN historical lucky nations',
        'tsin_lucky_nations_desc':'Historical formation paths including Russia, Britain and Ireland, Germany, Italy and colonial successors. Human ownership or control of any required core blocks the entire path. Assisted mode never transfers land. Each saved HEX actor is left to HEX until its fallback year.',
        'tsin_lucky_nations_assisted':'Assisted formation',
        'tsin_lucky_nations_assisted_desc':'Support eligible historical AI roles; form only after they own the required core cities. No land transfers or forced colonial independence. Also the legacy-save default.',
        'tsin_lucky_nations_force':'Assistance and territorial fallback',
        'tsin_lucky_nations_force_desc':'After each path-specific fallback year, permit protected peacetime core transfers and independence from AI overlords. Capitals, human realms, occupied land and transfers that eliminate an owner are excluded.',
        'tsin_lucky_nations_off':'Disabled', 'tsin_lucky_nations_off_desc':'No historical-role support or scripted formation; existing TSIN support is removed on review.',
        'tsin_lucky_russia_support':'Russian consolidation support',
        'tsin_lucky_russia_support_desc':'Temporary support for delayed Russian consolidation. Ends at formation, human conflict, protected human city control or the end of the pilot period.',
        'tsin_lucky_russia_support_strong':'Intensified Russian consolidation support',
        'tsin_lucky_russia_support_strong_desc':'Stronger temporary support after fifteen assisted annual reviews. Not permanent national luck.',
        'tsin_lucky_russia.1.title':'The Russian consolidation',
        'tsin_lucky_russia.1.desc':'A delayed consolidation is being resolved under the historical progression rules. Human ownership and control, wars, capitals and surviving owners are checked again before any transfer.',
        'tsin_lucky_russia.1.a':'A new Russian state.',
        'tsin_lucky_russia_formed_log':'TSIN_LUCKY_RUSSIA formed by [ROOT.GetCountry.GetName]',
    }
    ko = {
        'tsin_lucky_nations':'TSIN 역사적 럭키네이션',
        'tsin_lucky_nations_desc':'러시아·영국(브리튼 제도와 아일랜드)·독일·이탈리아·식민 후계국 등의 역사적 형성 경로입니다. 필수 지점 하나라도 인간 세력권이 소유·점령하면 전체 경로를 막습니다. 지원 모드는 영토를 이전하지 않으며 HEX 역할 보유국은 각 보완 연도까지 HEX에 맡깁니다.',
        'tsin_lucky_nations_assisted':'형성 지원',
        'tsin_lucky_nations_assisted_desc':'역할별 AI를 지원하고 필수 지점을 모두 소유하면 형성합니다. 영토 이전·식민지 강제 독립은 없습니다. 기존 세이브의 기본 동작입니다.',
        'tsin_lucky_nations_force':'지원 및 영토 보완',
        'tsin_lucky_nations_force_desc':'각 경로의 보완 연도 이후 평화 시 핵심 지점 이전·AI 식민지 독립을 허용합니다. 수도·인간 세력권·점령지·소유국이 사라지는 이전은 제외합니다.',
        'tsin_lucky_nations_off':'끔','tsin_lucky_nations_off_desc':'역사 국가 지원과 스크립트 형성을 끕니다. 기존 TSIN 지원은 점검 시 제거합니다.',
        'tsin_lucky_russia_support':'러시아 통합 지원',
        'tsin_lucky_russia_support_desc':'지연된 러시아 통합을 위한 임시 지원입니다. 형성·인간과의 전쟁·인간의 보호 도시 소유나 점령·시제품 기간 종료 시 정리합니다.',
        'tsin_lucky_russia_support_strong':'러시아 통합 집중 지원',
        'tsin_lucky_russia_support_strong_desc':'지원 연간 점검 15회 이후의 강화된 임시 지원입니다. 영구적인 국가 특혜가 아닙니다.',
        'tsin_lucky_russia.1.title':'러시아의 통합',
        'tsin_lucky_russia.1.desc':'역사 진행 규칙에 따라 지연된 통합을 처리합니다. 이전 직전에 인간의 소유·점령, 전쟁, 수도, 이전 이후 소유국의 존속을 다시 확인합니다.',
        'tsin_lucky_russia.1.a':'새로운 러시아 국가로.',
        'tsin_lucky_russia_formed_log':'TSIN_LUCKY_RUSSIA (러시아 형성) [ROOT.GetCountry.GetName]',
    }
    for labels in (en, ko):
        for modifier in ['tsin_lucky_russia_support', 'tsin_lucky_russia_support_strong']:
            labels['STATIC_MODIFIER_NAME_' + modifier] = labels.pop(modifier)
            labels['STATIC_MODIFIER_DESC_' + modifier] = labels.pop(modifier + '_desc')
    files = {
        'in_game/common/scripted_triggers/tsin_lucky_nations_triggers.txt':triggers,
        'in_game/common/script_values/tsin_lucky_nations_values.txt':values,
        'in_game/common/scripted_effects/tsin_lucky_nations_effects.txt':effects,
        'in_game/common/on_action/tsin_lucky_nations_on_actions.txt':on_actions,
        'in_game/events/tsin_lucky_russia.txt':events,
        'main_menu/common/static_modifiers/tsin_lucky_nations_modifiers.txt':modifiers,
        'main_menu/common/game_rules/tsin_lucky_nations_rules.txt':rules,
    }
    for lang,entries in [('english',en),('korean',ko)]:
        files[f'main_menu/localization/{lang}/tsin_lucky_nations_l_{lang}.yml']='l_'+lang+':\n'+'\n'.join(' '+k+': '+json.dumps(v,ensure_ascii=False) for k,v in entries.items())+'\n'
    return files


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args();bad=[]
    for rel,text in build().items():
        path=pdx.MOD_ROOT/rel
        if args.check:
            if not path.exists() or pdx.read_text(path)!=text:bad.append(rel)
        else:pdx.write_text_bom(path,text)
    print(f'Lucky nations: {len(bad)} mismatches')
    for rel in bad:print(rel)
    return bool(bad)


if __name__=='__main__':raise SystemExit(main())
