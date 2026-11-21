"""Conservative AI exclave sales with actual settlement and strategic retention."""
import argparse,json
import pdx
from gen_historical_nations import registry


def build():
    cores=sorted({x for r in registry() for x in r['cores']}|{'moscow','novgorod','tver','vladimir'})
    protected=' '.join('this = location:'+x for x in cores)
    triggers=f'''tsin_border_sale_location = {{
tsin_history_border_shortlist = yes
owner = {{ is_subject = no NOT = {{ has_variable = hex_key }}
NOT = {{ has_primary_or_accepted_culture = prev.dominant_culture }} }}
NOT = {{ is_core_of = owner }}
NOT = {{ has_building = building_type:castle }}
NOT = {{ has_building = building_type:fortress }}
NOT = {{ OR = {{ {protected} }} }}
}}
tsin_border_sale_buyer = {{
tsin_history_ai_realm = yes is_subject = no at_war = no
NOT = {{ this = scope:tsin_border_seller }}
NOT = {{ has_variable = hex_key }}
has_primary_or_accepted_culture = scope:tsin_border_location.dominant_culture
gold >= scope:tsin_border_seller.var:tsin_border_price
}}
tsin_border_sale_transaction = {{
NOT = {{ has_game_rule = tsin_border_trade_off }}
exists = scope:tsin_border_seller exists = scope:tsin_border_buyer exists = scope:tsin_border_location
scope:tsin_border_seller = {{ tsin_history_ai_realm = yes is_subject = no at_war = no num_locations > 1 NOT = {{ has_variable = hex_key }} }}
scope:tsin_border_buyer = {{ tsin_border_sale_buyer = yes }}
scope:tsin_border_location = {{
tsin_border_sale_location = yes owner = scope:tsin_border_seller
any_neighbor_location = {{
owner ?= scope:tsin_border_buyer controller = owner
is_connected_to = owner.capital
}} }}
}}
'''
    effects='''tsin_border_sale_settle_effect = {
# Recheck the full contract before any money or location moves.
if = { limit = { tsin_border_sale_transaction = yes }
scope:tsin_border_buyer = { add_gold = { value = scope:tsin_border_seller.var:tsin_border_price multiply = -1 } }
scope:tsin_border_seller = {
add_gold = var:tsin_border_price
set_variable = { name = tsin_border_sale_cooldown years = 10 }
}
scope:tsin_border_location = { change_location_owner = scope:tsin_border_buyer }
}
}
tsin_border_sale_review_effect = {
save_scope_as = tsin_border_seller
# At most one sampled location and one completed sale per decade per seller.
set_variable = { name = tsin_border_review_cooldown years = 10 }
random_owned_location = {
limit = { tsin_border_sale_location = yes }
save_scope_as = tsin_border_location
owner = { set_variable = { name = tsin_border_price value = prev.tsin_border_sale_price } }
random_neighbor_location = {
limit = { controller = owner is_connected_to = owner.capital owner ?= { tsin_border_sale_buyer = yes } }
owner = { save_scope_as = tsin_border_buyer }
}
if = { limit = { exists = scope:tsin_border_buyer } tsin_border_sale_settle_effect = yes }
}
remove_variable = tsin_border_price
}
'''
    actions='''yearly_country_pulse = { on_actions = { tsin_border_trade_yearly } }
tsin_border_trade_yearly = {
trigger = { current_year >= 1700 NOT = { has_game_rule = tsin_border_trade_off } tsin_history_ai_realm = yes
is_subject = no at_war = no num_locations > 1
NOT = { has_variable = hex_key }
NOT = { has_variable = tsin_border_review_cooldown }
NOT = { has_variable = tsin_border_sale_cooldown } }
effect = { tsin_border_sale_review_effect = yes }
}
'''
    rules='''tsin_border_trade = {
default = tsin_border_trade_on
tsin_border_trade_on = { flag = general_rule }
tsin_border_trade_off = { flag = general_rule }
}
'''
    en={'tsin_border_trade':'TSIN AI exclave trade','tsin_border_trade_desc':'At most one sale per AI seller per decade. Only unimportant, disconnected rural inland locations of unaccepted culture; capitals, forts, cores, mineral centers, historical formation cities and all human realms are excluded. Saved HEX roles do not participate. Actual cash settlement, never a free transfer.', 'tsin_border_trade_on':'Conservative cash sales','tsin_border_trade_on_desc':'Enable strategically filtered AI-only sales with immediate revalidation.','tsin_border_trade_off':'Disabled','tsin_border_trade_off_desc':'No scripted exclave sales.'}
    ko={'tsin_border_trade':'TSIN AI 월경지 거래','tsin_border_trade_desc':'AI 매도국당 10년에 최대 한 곳입니다. 비수용 문화의 내륙 농촌 월경지만 대상으로 수도·요새·코어·광물 중심지·역사 형성 지점·모든 인간 세력권을 제외합니다. HEX 역할 보유국은 참여하지 않습니다. 실제 두캇으로 결제하며 무료 양도하지 않습니다.','tsin_border_trade_on':'보수적인 유상 매각','tsin_border_trade_on_desc':'전략적 조건을 검사하고 결제 직전 재검사하는 AI 전용 거래입니다.','tsin_border_trade_off':'끔','tsin_border_trade_off_desc':'스크립트 월경지 매각을 실행하지 않습니다.'}
    files={'in_game/common/scripted_triggers/tsin_border_trade_triggers.txt':triggers,'in_game/common/scripted_effects/tsin_border_trade_effects.txt':effects,'in_game/common/on_action/tsin_border_trade_on_actions.txt':actions,'in_game/common/script_values/tsin_border_trade_values.txt':'tsin_border_sale_price = { value = population multiply = 20 add = 10 min = 10 max = 1000 }\n','main_menu/common/game_rules/tsin_border_trade_rules.txt':rules}
    for lang,entries in [('english',en),('korean',ko)]:files[f'main_menu/localization/{lang}/tsin_border_trade_l_{lang}.yml']='l_'+lang+':\n'+'\n'.join(' '+k+': '+json.dumps(v,ensure_ascii=False) for k,v in entries.items())+'\n'
    return files


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');args=p.parse_args();bad=[]
    for rel,text in build().items():
        path=pdx.MOD_ROOT/rel
        if args.check:
            if not path.exists() or pdx.read_text(path)!=text:bad.append(rel)
        else:pdx.write_text_bom(path,text)
    print(f'Border trade: {len(bad)} mismatches')
    for rel in bad:print(rel)
    return bool(bad)


if __name__=='__main__':raise SystemExit(main())
