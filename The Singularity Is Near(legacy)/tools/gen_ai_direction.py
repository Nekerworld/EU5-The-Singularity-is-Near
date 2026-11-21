"""Regional AI priorities; isolated from HEX and protected human areas."""
import argparse,json,re
import pdx
from gen_historical_nations import registry


def geography():
    text=pdx.strip_comments(pdx.read_text(pdx.game_root()/'in_game/map_data/definitions.txt'))
    tokens=re.findall(r'[A-Za-z_0-9]+|[={} ]',text);tokens=[t for t in tokens if t!=' ']
    locations={};areas={};stack=[];i=0
    while i<len(tokens):
        token=tokens[i]
        if i+2<len(tokens) and tokens[i+1:i+3]==['=','{']:
            stack.append(token);i+=3;continue
        if token=='}':
            if stack:stack.pop()
        elif token not in ['{','=']:
            a=next((x for x in reversed(stack) if x.endswith('_area')),None)
            r=next((x for x in reversed(stack) if x.endswith('_region')),None)
            if a and r:locations[token]=a;areas[a]=r
        i+=1
    return locations,areas


def build():
    locations,areas=geography();roles=[]
    for row in registry():
        selected=sorted(a for a,r in areas.items() if r in row['regions'] and 'sea_zone' not in a) if row['id']=='britain' else sorted({locations[c] for c in row['cores']})
        roles.append(dict(id=row['id'],tag=row['tag'],areas=selected,start=row['start'],end=row['end']))
    # Preservation and recovery, never forced recreation or inherited maximum borders.
    for id,tag,city in [('russia','RUS','moscow'),('france','FRA','paris'),('ottomans','TUR','edirne'),('iran','IRA','isfahan'),('siam','SIA','ayodhya'),('ethiopia','ETH','aksum')]:
        if city in locations:roles.append(dict(id=id,tag=tag,areas=[locations[city]],start=1500,end=1945))
    chosen=sorted({a for row in roles for a in row['areas']});preferences=[]
    for a in chosen:preferences.append(f'tsin_priority_{a} = {{ preference_type = conquest modifier = 3 area = {a} }}')
    cleanup=' '.join('remove_area_preference = tsin_priority_'+a for a in chosen)
    effects=['tsin_direction_cleanup_effect = { '+cleanup+' }','tsin_direction_review_effect = { tsin_direction_cleanup_effect = yes save_scope_as = tsin_direction_actor']
    for row in roles:
        effects.append(f'if = {{ limit = {{ tag = {row["tag"]} current_year >= {row["start"]} current_year < {row["end"]} }}')
        for a in row['areas']:
            effects.append(f'''area:{a} = {{
if = {{ limit = {{ NOT = {{ any_location_in_area = {{ OR = {{ owner ?= {{ tsin_history_human_realm = yes }} controller ?= {{ tsin_history_human_realm = yes }} }} }} }} }}
scope:tsin_direction_actor = {{
if = {{ limit = {{ "conquer_area_preference(prev)" <= 1 "conquer_area_preference(prev)" >= 1 }} add_area_preference = tsin_priority_{a} }}
}} }} }}''')
        effects.append('}')
    effects.append('}')
    tags=' '.join('tag = '+r['tag'] for r in roles)
    actions=f'''yearly_country_pulse = {{ on_actions = {{ tsin_direction_yearly }} }}
tsin_direction_yearly = {{
trigger = {{ current_year >= 1500 current_year <= 1945 OR = {{ OR = {{ {tags} }} has_variable = tsin_direction_reviewed }} }}
effect = {{
if = {{ limit = {{ tsin_history_ai_realm = yes NOT = {{ has_game_rule = tsin_lucky_nations_off }}
NOT = {{ has_variable = hex_key }} NOT = {{ tsin_lucky_human_war_trigger = yes }} }}
tsin_direction_review_effect = yes set_variable = tsin_direction_reviewed
}}
else = {{ tsin_direction_cleanup_effect = yes remove_variable = tsin_direction_reviewed }}
}} }}
'''
    return {'in_game/common/area_preferences/tsin_historical_priorities.txt':'\n'.join(preferences)+'\n','in_game/common/scripted_effects/tsin_historical_direction_effects.txt':'\n'.join(effects)+'\n','in_game/common/on_action/tsin_historical_direction_on_actions.txt':actions}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args();bad=[]
    for rel,text in build().items():
        path=pdx.MOD_ROOT/rel
        if args.check:
            if not path.exists() or pdx.read_text(path)!=text:bad.append(rel)
        else:pdx.write_text_bom(path,text)
    print(f'Historical AI direction: {len(bad)} mismatches')
    for rel in bad:print(rel)
    return bool(bad)


if __name__=='__main__':raise SystemExit(main())
