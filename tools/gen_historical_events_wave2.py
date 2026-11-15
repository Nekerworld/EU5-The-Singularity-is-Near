"""Six stateful, player-focused chains from the reviewed historical plan."""
import argparse,json
import pdx


def build():
    chains=json.loads((pdx.MOD_ROOT/'data/historical_events_wave2.json').read_text(encoding='utf-8'))['chains']
    events=['namespace = tsin_history2'];labels={'english':{},'korean':{}};candidates=[];cleanup=[]
    def loc(k,en,ko):labels['english'][k]=en;labels['korean'][k]=ko
    for chain in chains:
        id=chain['id'];p='tsin_hist2_'+id;stages=chain['stages']
        cleanup.append(f'if = {{ limit = {{ has_variable = {p}_stage var:{p}_stage < 99 }} set_variable = {{ name = {p}_stage value = 99 }} }}')
        for i,row in enumerate(stages):
            eid=chain['base']+i;event='tsin_history2.'+str(eid);candidates.append(event)
            gate=f'NOT = {{ has_variable = {p}_stage }} {chain["gate"]}' if i==0 else f'has_variable = {p}_stage var:{p}_stage = {i} current_year > var:{p}_year'
            if id=='mission' and i>0:gate+=' var:tsin_hist2_mission_partner ?= { num_locations > 0 at_war = no }'
            if id=='mission' and i==1:gate+=' has_variable = tsin_hist2_mission_accepted'
            if id=='pig' and i>0:gate+=' var:tsin_hist2_pig_partner ?= { num_locations > 0 at_war = no }'
            if id=='stink' and i==len(stages)-1:gate+=' var:tsin_hist2_stink_location ?= { owner = root has_building_with_at_least_one_level = tsin_waterworks }'
            following=99 if i==len(stages)-1 else i+1
            def option(letter):
                paid=row.get('paid_'+letter,False)
                compensation = id=='pig' and (row.get('end_'+letter,False) or following==99) and letter=='a'
                end=row.get('end_'+letter,False) or following==99
                stage=99 if end else following
                effect=row.get('effect_'+letter,'')
                result=[f'option = {{ name = {event}.{letter}', 'trigger = { gold >= tsin_gold_cost_1 }' if paid or compensation else '', 'change_gold_effect = { scale = -1 }' if paid else '', f'hidden_effect = {{ set_variable = {{ name = {p}_stage value = {stage} }} }}']
                if end and letter=='a':result.append(f'add_country_modifier = {{ modifier = tsin_history2_{chain["reward"]} years = 3 mode = replace }}')
                result.append(effect)
                if id in ['strike','military'] and letter=='b' and not end:
                    result.append('change_variable = { name = tsin_labor_grievance add = 3 } if = { limit = { var:tsin_labor_grievance > 100 } set_variable = { name = tsin_labor_grievance value = 100 } }')
                if id in ['strike','military'] and letter=='a' and end:
                    result.append('change_variable = { name = tsin_labor_grievance subtract = 5 } if = { limit = { var:tsin_labor_grievance < 0 } set_variable = { name = tsin_labor_grievance value = 0 } }')
                if id=='pig' and end and letter=='a':
                    result.append('if = { limit = { var:tsin_hist2_pig_partner ?= { num_locations > 0 } } set_variable = { name = tsin_hist2_compensation value = tsin_gold_cost_1 } if = { limit = { gold >= var:tsin_hist2_compensation } add_gold = { value = var:tsin_hist2_compensation multiply = -1 } var:tsin_hist2_pig_partner = { add_gold = root.var:tsin_hist2_compensation } } remove_variable = tsin_hist2_compensation }')
                if id=='mission' and i==0 and letter=='a':result.append('tsin_hist2_mission_invite_effect = yes')
                if paid or compensation:
                    result = result[:2] + ['if = { limit = { gold >= tsin_gold_cost_1 }'] + result[2:] + ['}', f'else = {{ hidden_effect = {{ set_variable = {{ name = {p}_stage value = 99 }} }} }}']
                result+=['ai_chance = { factor = '+('4' if letter=='a' else '1')+' }','}']
                return '\n'.join(result)
            initial=''
            if i==0:
                if id in ['strike','military']:initial='if = { limit = { NOT = { has_variable = tsin_labor_grievance } } set_variable = { name = tsin_labor_grievance value = 0 } }'
                if id=='stink':initial='capital = { root = { set_variable = { name = tsin_hist2_stink_location value = prev } } }'
                if id=='pig':initial='random_neighbor_country = { limit = { is_ai = yes at_war = no num_locations > 0 } root = { set_variable = { name = tsin_hist2_pig_partner value = prev } } }'
            events.append(f'''{event} = {{ type = country_event
title = {event}.title desc = {event}.desc outcome = neutral
illustration_tags = {{ 10 = interior 10 = regular }}
trigger = {{ is_ai = no current_age = age_7_industrialization current_year >= {chain['year']} current_year < 1900
NOT = {{ has_game_rule = tsin_historical_events_off }} {gate} }}
immediate = {{ set_variable = {{ name = {p}_year value = current_year }} {initial} }}
{option('a')}
{option('b')}
}}''')
            for lang,index in [('english',0),('korean',1)]:
                for key in ['title','desc','a','b']:labels[lang][event+'.'+key]=row[key][index]
    # One pending visitor per host prevents another nation's request overwriting it.
    effects='''tsin_hist2_mission_invite_effect = {
save_scope_as = tsin_hist2_visitor
ordered_country = {
limit = { is_ai = yes at_war = no num_locations > 0 NOT = { this = root }
has_advance = tsin_industrial_capitalism_advance
any_owned_location = { has_building_with_at_least_one_level = tsin_machine_works }
NOT = { has_variable = tsin_hist2_visit_origin } }
order_by = num_locations max = 1
save_scope_as = tsin_hist2_host
set_variable = { name = tsin_hist2_visit_origin value = scope:tsin_hist2_visitor }
scope:tsin_hist2_visitor = { set_variable = { name = tsin_hist2_mission_partner value = scope:tsin_hist2_host } }
trigger_event_non_silently = tsin_history2.99
}
}
tsin_hist2_boundary_cleanup_effect = {
'''+ '\n'.join(cleanup)+'''
remove_variable = tsin_hist2_mission_partner remove_variable = tsin_hist2_mission_accepted
remove_variable = tsin_hist2_visit_origin remove_variable = tsin_hist2_pig_partner remove_variable = tsin_hist2_stink_location
}
'''
    events+=['''tsin_history2.99 = { type = country_event title = tsin_history2.99.title desc = tsin_history2.99.desc outcome = neutral
illustration_tags = { 10 = interior 10 = regular }
trigger = { has_variable = tsin_hist2_visit_origin var:tsin_hist2_visit_origin ?= { num_locations > 0 } }
option = { name = tsin_history2.99.a
var:tsin_hist2_visit_origin = { set_variable = tsin_hist2_mission_accepted }
remove_variable = tsin_hist2_visit_origin ai_chance = { factor = 4 } }
option = { name = tsin_history2.99.b
var:tsin_hist2_visit_origin = { set_variable = { name = tsin_hist2_mission_stage value = 99 } trigger_event_non_silently = tsin_history2.100 }
remove_variable = tsin_hist2_visit_origin ai_chance = { factor = 1 } }
}
tsin_history2.100 = { type = country_event title = tsin_history2.100.title desc = tsin_history2.100.desc outcome = neutral
illustration_tags = { 10 = interior 10 = regular }
immediate = { remove_variable = tsin_hist2_mission_partner }
option = { name = tsin_history2.100.a }
}''']
    for k,en,ko in [
        ('99.title','A visiting delegation','시찰단의 방문 요청'),('99.desc','Another government asks to inspect our industrial institutions. We may welcome the delegation or decline its proposed itinerary.','다른 정부가 우리 산업 제도와 시설을 시찰하고자 합니다. 시찰단의 일정을 수락할지 거절할지 결정해야 합니다.'),('99.a','Admit a limited delegation.','제한된 시찰단을 받아들여라.'),('99.b','Decline this visit.','이번 방문은 거절하라.'),('100.title','The visit is suspended','시찰 일정의 중단'),('100.desc','The planned visit cannot proceed. The delegation will return before committing further funds.','예정한 방문을 진행할 수 없게 되었습니다. 시찰단은 추가 비용이 발생하기 전에 귀환할 것입니다.'),('100.a','Bring the delegation home.','시찰단을 귀환시켜라.')]:loc('tsin_history2.'+k,en,ko)
    pool='\n'.join('10 = '+event for event in candidates)
    callbacks=[]
    for slot in range(4):
        callbacks.append(f'''tsin_history2_draw_{slot} = {{ trigger = {{ is_ai = no current_year >= 1837 current_year < 1900 current_age = age_7_industrialization
NOT = {{ has_game_rule = tsin_historical_events_off }} {'has_game_rule = tsin_historical_events_dense' if slot>=2 else ''} }}
random_events = {{ chance_to_happen = 100
{pool}
}} }}''')
    actions='yearly_country_pulse = { on_actions = { '+' '.join('tsin_history2_draw_'+str(i) for i in range(4))+' tsin_hist2_partners_review tsin_hist2_cleanup } }\n'+'\n'.join(callbacks)+'''
tsin_hist2_partners_review = { trigger = { is_ai = no current_year >= 1837 current_year < 1900 }
effect = {
if = { limit = { has_variable = tsin_hist2_stink_stage var:tsin_hist2_stink_stage >= 1 var:tsin_hist2_stink_stage < 99
NOT = { var:tsin_hist2_stink_location ?= { owner = root } } }
set_variable = { name = tsin_hist2_stink_stage value = 99 } remove_variable = tsin_hist2_stink_location }
if = { limit = { has_variable = tsin_hist2_mission_stage var:tsin_hist2_mission_stage >= 1 var:tsin_hist2_mission_stage < 99
NOT = { var:tsin_hist2_mission_partner ?= { num_locations > 0 at_war = no } } }
set_variable = { name = tsin_hist2_mission_stage value = 99 } trigger_event_non_silently = tsin_history2.100 }
if = { limit = { has_variable = tsin_hist2_pig_stage var:tsin_hist2_pig_stage >= 1 var:tsin_hist2_pig_stage < 99
NOT = { var:tsin_hist2_pig_partner ?= { num_locations > 0 at_war = no } } }
set_variable = { name = tsin_hist2_pig_stage value = 99 } remove_variable = tsin_hist2_pig_partner }
} }
tsin_hist2_cleanup = { trigger = { is_ai = no current_year >= 1900 } effect = { tsin_hist2_boundary_cleanup_effect = yes } }
'''
    modifiers=[]
    for id,en,ko,effect in [
        ('labor','Negotiated workplace settlement','합의된 작업장 개선','country_cabinet_efficiency = 0.02'),
        ('military','Audited military administration','군정 장부 정비','discipline = 0.02'),
        ('civic','Verified water administration','검증된 물 관리','global_disease_resistance = 0.02'),
        ('diplomacy','Practiced border mediation','국경 중재 경험','diplomatic_reputation = 1'),
        ('finance','Corporate disclosure review','기업 공시 점검','country_cabinet_efficiency = 0.02'),
        ('study','Applied study mission reports','시찰 보고의 활용','research_speed_modifier = 0.03'),
    ]:
        modifiers.append(f'tsin_history2_{id} = {{ game_data = {{ category = country }} {effect} }}')
        loc('STATIC_MODIFIER_NAME_tsin_history2_'+id,en,ko);loc('STATIC_MODIFIER_DESC_tsin_history2_'+id,'A temporary, non-stacking result of a completed historical chain.','완료한 역사 사건열의 중첩되지 않는 임시 결과입니다.')
    result={'in_game/events/tsin_history_wave2.txt':'\n'.join(events),'in_game/common/scripted_effects/tsin_history_wave2_effects.txt':effects,'in_game/common/on_action/tsin_history_wave2_on_actions.txt':actions,'main_menu/common/static_modifiers/tsin_history_wave2_modifiers.txt':'\n'.join(modifiers)}
    for lang,entries in labels.items():result[f'main_menu/localization/{lang}/tsin_history_wave2_l_{lang}.yml']='l_'+lang+':\n'+'\n'.join(' '+k+': '+json.dumps(v,ensure_ascii=False) for k,v in entries.items())
    return {k:'\n'.join(line.rstrip() for line in v.splitlines())+'\n' for k,v in result.items()}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args();bad=[]
    for rel,text in build().items():
        path=pdx.MOD_ROOT/rel
        if args.check:
            if not path.exists() or pdx.read_text(path)!=text:bad.append(rel)
        else:pdx.write_text_bom(path,text)
    print(f'Historical wave 2: {len(bad)} mismatches')
    for rel in bad:print(rel)
    return bool(bad)


if __name__=='__main__':raise SystemExit(main())
