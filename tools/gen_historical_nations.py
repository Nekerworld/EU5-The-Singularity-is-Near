"""Generate protected historical formation paths from explicit regional data."""
import argparse
import json
import re
import pdx


def registry():
    data=json.loads((pdx.MOD_ROOT/'data/historical_nations.json').read_text(encoding='utf-8'))
    ids=[r['id'] for r in data['nations']]
    tags=[r['tag'] for r in data['nations']]
    if len(set(ids))!=len(ids) or len(set(tags))!=len(tags):raise ValueError('duplicate historical role/tag')
    geography=pdx.read_text(pdx.game_root()/'in_game/map_data/definitions.txt')
    for r in data['nations']:
        if not (r['start'] <= r['fallback'] < r['end']):raise ValueError('invalid timeline '+r['id'])
        if not r['cores'] or len(r['cores'])!=len(set(r['cores'])):raise ValueError('invalid core set')
        for location in r['cores']:
            if not re.search(r'\b'+re.escape(location)+r'\b',geography):raise ValueError('unknown location '+location)
        for region in r['regions']:
            if not re.search(r'\b'+re.escape(region)+r'\s*=\s*\{',geography):raise ValueError('unknown region '+region)
        if r['id']=='britain' and set(r['regions'])!={'great_britain_region','ireland_region'}:raise ValueError('Britain must stay within Britain and Ireland')
    return data['nations']


def build():
    rows=registry();triggers=[];effects=[];values=[];formables=[];events=['namespace = tsin_nations'];en={};ko={}
    def loc(k,e,h):en[k]=e;ko[k]=h
    for number,row in enumerate(rows,1):
        id=row['id'];tag=row['tag'];cores=row['cores'];prefix='tsin_nation_'+id
        candidate='scope:'+prefix+'_candidate'
        guards=' '.join(f'location:{x} = {{ OR = {{ owner ?= {{ tsin_history_human_realm = yes }} controller ?= {{ tsin_history_human_realm = yes }} }} }}' for x in cores)
        # Capital and culture constrain colonial roles, so European colonizers and
        # surviving indigenous civilizations cannot be renamed as new republics.
        capitals=' '.join('capital.region = region:'+x for x in row['regions'])
        own_one=' '.join('owns = location:'+x for x in cores)
        own_one += ' ' + ' '.join('tag = '+x for x in row.get('preferred',[]))
        independence='OR = { is_subject = no is_subject_type = colonial_nation }' if row.get('colonial') else 'is_subject = no is_junior_partner = no'
        culture='OR = { '+' '.join('culture = { has_culture_group = culture_group:'+g+' }' for g in row['groups'])+' }'
        complete=' '.join('owns = location:'+x for x in cores)
        exists=f'country_exists = c:{tag}' if id!='austria_hungary' else 'any_country = { has_variable = tsin_austria_hungary_formed }'
        excluded=' '.join('tag = '+other['tag'] for other in rows if other['tag']!=tag)
        if id=='austria_hungary':excluded=excluded.replace('tag = HAB','')
        native_extra=row.get('extra','')
        if id=='britain':
            native_extra += ' trigger_if = { limit = { country_exists = c:GBR } tag = GBR }'
            exists='c:GBR ?= { '+' '.join('owns = location:'+x for x in cores)+' }'
        triggers += [f'''{prefix}_blocked = {{ OR = {{ {guards} }} }}
{prefix}_campaign = {{
current_year >= {row['start']} current_year < {row['end']}
NOT = {{ has_game_rule = tsin_lucky_nations_off }}
NOT = {{ {exists} }}
NOT = {{ {prefix}_blocked = yes }}
}}
{prefix}_candidate = {{
tsin_history_ai_realm = yes {independence}
num_locations >= {row['minimum_locations']}
{culture}
OR = {{ {capitals} }}
OR = {{ {own_one} }}
NOT = {{ OR = {{ {excluded} }} }}
{native_extra}
}}
{prefix}_force = {{
{prefix}_campaign = yes {prefix}_candidate = yes
has_game_rule = tsin_lucky_nations_force current_year >= {row['fallback']}
at_war = no NOT = {{ tsin_lucky_human_war_trigger = yes }}
''']
        for core in cores:
            triggers += [f'''location:{core} = {{ OR = {{ owner ?= {candidate}
AND = {{ controller = owner is_capital = no is_historical_capital = no
owner ?= {{ tsin_history_ai_realm = yes at_war = no num_locations > {prefix}_outgoing }} }} }} }}''',
            ]
        triggers+=['}']
        # Count *all* outgoing core cities from each owner before the first move.
        values += [f'{prefix}_outgoing = {{ value = 0 '+' '.join(f'if = {{ limit = {{ owns = location:{x} }} add = 1 }}' for x in cores)+' }']
        form=f'form_country = formable_country:{prefix}_f' if id!='austria_hungary' else '''
set_variable = tsin_austria_hungary_formed
change_country_name = tsin_austria_hungary_name
change_country_adjective = tsin_austria_hungary_adjective
if = { limit = { NOT = { has_variable = tsin_dual_monarchy } }
set_variable = tsin_dual_monarchy
add_country_modifier = { modifier = tsin_dual_monarchy months = -1 }
location:buda.dominant_culture ?= { save_scope_as = tsin_ah_culture }
if = { limit = { exists = scope:tsin_ah_culture } add_accepted_culture = scope:tsin_ah_culture }
}
'''
        if id=='britain':form='if = { limit = { NOT = { tag = GBR } } '+form+' }'
        if id=='qing':form+='\nchange_country_name = QNG change_country_adjective = QNG_ADJ change_country_color = map_QNG'
        independence_effect='if = { limit = { is_subject_type = colonial_nation } overlord = { cancel_subject = prev } }' if row.get('colonial') else ''
        moves='\n'.join(f'location:{x} = {{ if = {{ limit = {{ NOT = {{ owner ?= {candidate} }} }} change_location_owner = {candidate} }} }}' for x in cores)
        effects += [f'''{prefix}_form = {{
# Execute once under fresh guards. Colonies only leave an AI overlord in force mode.
if = {{ limit = {{ {prefix}_force = yes }} {independence_effect}
{moves}
{form}
remove_country_modifier = tsin_nation_support
remove_country_modifier = tsin_nation_support_strong
debug_log = {prefix}_log
}}
}}
{prefix}_review = {{
if = {{ limit = {{ {prefix}_campaign = yes }}
''']
        # Prefer the historical actor if eligible, then core owners, then largest.
        selectors=[]
        for preferred in row.get('preferred',[]):selectors.append(('c:'+preferred,True))
        selectors += [('location:'+core+'.owner',True) for core in cores]
        for idx,(scope,_) in enumerate(selectors):
            effects += [('if' if idx==0 else 'else_if')+f' = {{ limit = {{ {scope} ?= {{ {prefix}_candidate = yes }} }} {scope} = {{ save_scope_as = {prefix}_candidate }} }}']
        effects += [f'else = {{ ordered_country = {{ limit = {{ {prefix}_candidate = yes }} order_by = num_locations max = 1 save_scope_as = {prefix}_candidate }} }}',f'''if = {{ limit = {{ exists = {candidate} }}
{candidate} = {{
if = {{ limit = {{ NOT = {{ tsin_lucky_human_war_trigger = yes }}
NOT = {{ AND = {{ has_variable = hex_key current_year < {row['fallback']} }} }} }}
if = {{ limit = {{ OR = {{ NOT = {{ has_variable = tsin_nation_role }} NOT = {{ var:tsin_nation_role = {number} }} }} }}
set_variable = {{ name = tsin_nation_role value = {number} }}
set_variable = {{ name = tsin_nation_support_years value = 0 }} }}
change_variable = {{ name = tsin_nation_support_years add = 1 }}
if = {{ limit = {{ var:tsin_nation_support_years >= 15 }} add_country_modifier = {{ modifier = tsin_nation_support_strong years = 2 mode = replace }} }}
else = {{ add_country_modifier = {{ modifier = tsin_nation_support years = 2 mode = replace }} }}
if = {{ limit = {{ is_subject = no at_war = no {complete} }}
{form}
remove_country_modifier = tsin_nation_support remove_country_modifier = tsin_nation_support_strong
}}
else_if = {{ limit = {{ {prefix}_force = yes }} trigger_event_non_silently = tsin_nations.{number} }}
}}
}}
}}
}}
}}''']
        if id!='austria_hungary':
            formables += [f'''{prefix}_f = {{ level = {row.get('level',3)} required_locations_fraction = 0 rule = historical
potential = {{ always = no }} # Only the guarded progression coordinator may form this variant.
allow = {{ {prefix}_candidate = yes {complete} }}
name = {row.get('name_key',tag)} adjective = {row.get('adj_key',tag+'_ADJ')}
tag = {tag} flag = {row.get('flag',tag)} color = {row.get('color','map_'+tag)}
regions = {{ {' '.join(row['regions'])} }}
form_effect = {{ }}
}}''']
        events += [f'''tsin_nations.{number} = {{ type = country_event
title = tsin_nations.{number}.title desc = tsin_nations.{number}.desc outcome = neutral
illustration_tags = {{ 10 = regular 10 = exterior }}
trigger = {{ {prefix}_candidate = yes }}
immediate = {{ save_scope_as = {prefix}_candidate {prefix}_form = yes }}
option = {{ name = tsin_nations.{number}.a }}
}}''']
        loc(f'tsin_nations.{number}.title',row['name']['english']+' consolidation',row['name']['korean']+'의 성립')
        loc(f'tsin_nations.{number}.desc','The historical progression rules offer a delayed formation. Protected human realms, peace, capitals and the continued existence of transferring owners are rechecked before changing any core city. This grants core cities only, never the full historical empire.','역사 진행 규칙에 따라 지연된 국가 성립을 처리합니다. 핵심 지점을 이전하기 직전 인간 세력권·평화·수도·기존 소유국의 존속을 재검사합니다. 핵심 지점만 대상으로 하며 역사상 최대 영토를 지급하지 않습니다.')
        loc(f'tsin_nations.{number}.a','A new political settlement.','새로운 정치 질서로.')
        loc(prefix+'_log','TSIN historical consolidation: '+row['name']['english'],'TSIN 역사적 국가 성립: '+row['name']['korean'])
        if row.get('custom'):
            loc(tag,row['name']['english'],row['name']['korean']);loc(tag+'_ADJ',row['name']['english'],row['name']['korean'])
    loc('tsin_austria_hungary_name','Austria-Hungary','오스트리아-헝가리')
    loc('tsin_austria_hungary_adjective','Austro-Hungarian','오스트리아-헝가리')
    for id,e,k in [('tsin_nation_support','Delayed national consolidation','지연된 국가 통합 지원'),('tsin_nation_support_strong','Intensified national consolidation','국가 통합 집중 지원')]:
        loc('STATIC_MODIFIER_NAME_'+id,e,k);loc('STATIC_MODIFIER_DESC_'+id,'Temporary, non-stacking assistance for an AI historical role. Removed on the next review; never helps it fight human realms.','역사적 국가 역할을 위한 중첩되지 않는 AI 임시 지원입니다. 다음 점검에서 재심사하며 인간 세력권과의 전쟁에는 지원하지 않습니다.')
    effects += ['''tsin_nations_cleanup_effect = {
every_country = { limit = { has_variable = tsin_nation_role }
remove_country_modifier = tsin_nation_support remove_country_modifier = tsin_nation_support_strong
}
}
tsin_nations_year_effect = {
set_global_variable = { name = tsin_nations_review_year value = current_year }
tsin_nations_cleanup_effect = yes
''']+['tsin_nation_'+r['id']+'_review = yes' for r in rows]+['}']
    modifiers='''tsin_nation_support = { game_data = { category = country } land_morale_modifier = 0.15 discipline = 0.05 global_manpower_modifier = 0.20 siege_ability = 0.10 }
tsin_nation_support_strong = { game_data = { category = country } land_morale_modifier = 0.25 discipline = 0.10 global_manpower_modifier = 0.35 siege_ability = 0.20 }
'''
    actions='''yearly_country_pulse = { on_actions = { tsin_nations_yearly } }
on_war_declared = { on_actions = { tsin_nations_cleanup } }
on_join_war = { on_actions = { tsin_nations_cleanup } }
tsin_nations_cleanup = { effect = { tsin_nations_cleanup_effect = yes } }
tsin_nations_yearly = {
trigger = { current_year >= 1500 current_year <= 1945
OR = { NOT = { has_global_variable = tsin_nations_review_year } current_year > global_var:tsin_nations_review_year } }
effect = { tsin_nations_year_effect = yes }
}
'''
    result={
        'in_game/common/scripted_triggers/tsin_historical_nations_triggers.txt':'\n'.join(triggers),
        'in_game/common/scripted_effects/tsin_historical_nations_effects.txt':'\n'.join(effects),
        'in_game/common/script_values/tsin_historical_nations_values.txt':'\n'.join(values),
        'in_game/common/formable_countries/tsin_historical_nations.txt':'\n'.join(formables),
        'in_game/common/on_action/tsin_historical_nations_on_actions.txt':actions,
        'in_game/events/tsin_historical_nations.txt':'\n'.join(events),
        'main_menu/common/static_modifiers/tsin_historical_nations_modifiers.txt':modifiers,
    }
    for lang,entries in [('english',en),('korean',ko)]:result[f'main_menu/localization/{lang}/tsin_historical_nations_l_{lang}.yml']='l_'+lang+':\n'+'\n'.join(' '+k+': '+json.dumps(v,ensure_ascii=False) for k,v in entries.items())
    return {k:'\n'.join(line.rstrip() for line in v.splitlines())+'\n' for k,v in result.items()}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args();bad=[]
    for rel,text in build().items():
        path=pdx.MOD_ROOT/rel
        if args.check:
            if not path.exists() or pdx.read_text(path)!=text:bad.append(rel)
        else:pdx.write_text_bom(path,text)
    print(f'Historical nations: {len(bad)} mismatches')
    for rel in bad:print(rel)
    return bool(bad)


if __name__=='__main__':raise SystemExit(main())
