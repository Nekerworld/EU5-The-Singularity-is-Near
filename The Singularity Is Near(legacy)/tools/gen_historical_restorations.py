"""Strict opt-in restoration when no independent historical actor survives."""
import argparse,json
import pdx
from gen_historical_nations import registry


def roles():
    rows=[dict(id='russia',tag='RUS',cores=['moscow','novgorod','tver','vladimir'],groups=['russian_group'],fallback=1700,end=1837,formable='RUS_f',name={'english':'Russia','korean':'러시아'})]
    for r in registry():
        if r['id'] in ['austria_hungary','qing']:continue
        rows.append(dict(r,formable='tsin_nation_'+r['id']+'_f'))
    return rows


def build():
    triggers=[];values=[];effects=[];en={};ko={}
    for r in roles():
        id=r['id'];p='tsin_restore_'+id;centre=r['cores'][0]
        candidate='tsin_lucky_russia_candidate_trigger' if id=='russia' else 'tsin_nation_'+id+'_candidate'
        blocked='tsin_history_russia_player_blocked' if id=='russia' else 'tsin_nation_'+id+'_blocked'
        culture='OR = { '+' '.join('has_culture_group = culture_group:'+g for g in r['groups'])+' }'
        local_culture=f'dominant_culture ?= {{ {culture} }}' if not r.get('colonial') else f'owner = {{ culture = {{ {culture} }} }}'
        if id=='mughals':local_culture += ' dominant_religion.group = religion_group:muslim'
        triggers += [f'''{p}_trigger = {{
has_game_rule = tsin_lucky_nations_force
current_year >= {r['fallback']} current_year < {r['end']}
OR = {{ NOT = {{ has_global_variable = {p}_count }} global_var:{p}_count < 2 }}
OR = {{ NOT = {{ has_global_variable = {p}_next }} current_year >= global_var:{p}_next }}
NOT = {{ country_exists = c:{r['tag']} }} NOT = {{ {blocked} = yes }}
NOT = {{ any_country = {{ {candidate} = yes }} }}
location:{centre} = {{ {local_culture} }}
''']
        for core in r['cores']:
            triggers += [f'''location:{core} = {{
is_ownable = yes population > 0 is_capital = no controller = owner
owner ?= {{ tsin_history_ai_realm = yes at_war = no num_locations > {p}_outgoing
NOT = {{ tsin_lucky_human_war_trigger = yes }} }}
}}''']
        triggers+=['}']
        values.append(f'{p}_outgoing = {{ value = 0 '+' '.join(f'if = {{ limit = {{ owns = location:{c} }} add = 1 }}' for c in r['cores'])+' }')
        child='scope:'+p+'_country'
        effects += [f'''{p}_effect = {{
# Full guard must pass before creating a country, moving a city, or transferring gold.
if = {{ limit = {{ {p}_trigger = yes }}
if = {{ limit = {{ NOT = {{ has_global_variable = {p}_count }} }} set_global_variable = {{ name = {p}_count value = 0 }} }}
change_global_variable = {{ name = {p}_count add = 1 }}
set_global_variable = {{ name = {p}_next value = tsin_restoration_next_year }}
location:{centre} = {{
save_scope_as = {p}_centre
owner = {{ save_scope_as = {p}_sponsor }}
create_country_from_location = {{
save_scope_as = {p}_country
set_capital = scope:{p}_centre
change_culture = {'scope:'+p+'_sponsor.culture' if r.get('colonial') else 'scope:'+p+'_centre.dominant_culture'}
change_religion = {'scope:'+p+'_sponsor.religion' if r.get('colonial') else 'scope:'+p+'_centre.dominant_religion'}
change_government_type = government_type:{'republic' if r.get('colonial') else 'monarchy'}
# Do not inherit an unfinanced treasury endowment from engine defaults.
add_gold = {{ value = gold multiply = -1 }}
}}
}}
''']
        for core in r['cores']:
            effects.append(f'location:{core} = {{ if = {{ limit = {{ NOT = {{ owner ?= {child} }} }} change_location_owner = {child} change_location_controller = {child} }} }}')
        for core in r['cores']:
            effects.append(f'''location:{core}.province_definition = {{ every_location_in_province_definition = {{
limit = {{ owner ?= scope:{p}_sponsor controller = owner is_capital = no is_historical_capital = no
owner = {{ tsin_history_ai_realm = yes at_war = no num_locations > 1 }} }}
change_location_owner = {child} change_location_controller = {child}
}} }}''')
        effects += [f'''{child} = {{
form_country = formable_country:{r['formable']}
add_country_modifier = {{ modifier = tsin_restored_nation_support years = 5 mode = replace }}
set_variable = {{ name = tsin_restored_year value = current_year }}
debug_log = {p}_log
}}
}}
}}''']
        en[p+'_log']='TSIN protected restoration: '+r['name']['english'];ko[p+'_log']='TSIN 보호 조건을 통과한 국가 복원: '+r['name']['korean']
    effects+=['tsin_restoration_year_effect = { set_global_variable = { name = tsin_restoration_year value = current_year }']+[f'tsin_restore_{r["id"]}_effect = yes' for r in roles()]+['}']
    effects+=['''tsin_restoration_cleanup_effect = {
every_country = { limit = { has_country_modifier = tsin_restored_nation_support
OR = { tsin_history_human_realm = yes tsin_lucky_human_war_trigger = yes has_game_rule = tsin_lucky_nations_off } }
remove_country_modifier = tsin_restored_nation_support }
}''']
    actions='''yearly_country_pulse = { on_actions = { tsin_restoration_yearly } }
on_war_declared = { on_actions = { tsin_restoration_cleanup } }
on_join_war = { on_actions = { tsin_restoration_cleanup } }
tsin_restoration_cleanup = { effect = { tsin_restoration_cleanup_effect = yes } }
tsin_restoration_yearly = { trigger = { current_year >= 1500 current_year <= 1945
OR = { NOT = { has_global_variable = tsin_restoration_year } current_year > global_var:tsin_restoration_year } }
effect = { tsin_restoration_cleanup_effect = yes
if = { limit = { has_game_rule = tsin_lucky_nations_force } tsin_restoration_year_effect = yes }
else = { set_global_variable = { name = tsin_restoration_year value = current_year } }
} }
'''
    en.update(STATIC_MODIFIER_NAME_tsin_restored_nation_support='Restored national administration',STATIC_MODIFIER_DESC_tsin_restored_nation_support='Five years of temporary support after a protected restoration. Removed against human realms; never permanent luck.')
    ko.update(STATIC_MODIFIER_NAME_tsin_restored_nation_support='복원 국가의 행정 정비',STATIC_MODIFIER_DESC_tsin_restored_nation_support='보호 조건을 통과해 복원된 국가의 5년 임시 지원입니다. 인간 세력권과 싸우면 제거되며 영구 특혜가 아닙니다.')
    result={'in_game/common/scripted_triggers/tsin_restoration_triggers.txt':'\n'.join(triggers),'in_game/common/scripted_effects/tsin_restoration_effects.txt':'\n'.join(effects),'in_game/common/script_values/tsin_restoration_values.txt':'\n'.join(values)+'\ntsin_restoration_next_year = { value = current_year add = 50 }','in_game/common/on_action/tsin_restoration_on_actions.txt':actions,'main_menu/common/static_modifiers/tsin_restoration_modifiers.txt':'tsin_restored_nation_support = { game_data = { category = country } land_morale_modifier = 0.20 discipline = 0.10 global_manpower_modifier = 0.30 }\n'}
    for lang,entries in [('english',en),('korean',ko)]:result[f'main_menu/localization/{lang}/tsin_restoration_l_{lang}.yml']='l_'+lang+':\n'+'\n'.join(' '+k+': '+json.dumps(v,ensure_ascii=False) for k,v in entries.items())
    return {k:'\n'.join(line.rstrip() for line in v.splitlines())+'\n' for k,v in result.items()}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args();bad=[]
    for rel,text in build().items():
        path=pdx.MOD_ROOT/rel
        if args.check:
            if not path.exists() or pdx.read_text(path)!=text:bad.append(rel)
        else:pdx.write_text_bom(path,text)
    print(f'Historical restorations: {len(bad)} mismatches')
    for rel in bad:print(rel)
    return bool(bad)


if __name__=='__main__':raise SystemExit(main())
