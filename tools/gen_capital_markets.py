"""Cross-era companies, economic regimes and evidence-gated financial crises.

Industrial sector definitions remain in era_7; shared accounting is extended with
TRY_REPLACE objects. No arbitrary country-wide random crash roll is used.
"""
import argparse,json,re
from pathlib import Path
import pdx
from gen_company_decisions import COMPANIES as INDUSTRIAL

CATALOG='data/early_companies.json'
FREE='tsin_laissez_faire_policy'


def catalog():
    return json.loads(pdx.read_text(pdx.MOD_ROOT/CATALOG))['companies']


def all_companies():
    rows=[]
    for c,advance,image,good,buildings in INDUSTRIAL:
        rows.append(dict(id=c,kind='industrial',good=good,icon=image,year=1837,
            condition=f'has_advance = {advance}',buildings=buildings,cost=4))
    return rows+catalog()


def build():
    rows=all_companies(); early=catalog();out={};loc={'english':{},'korean':{}}
    def label(key,en,ko):
        for lang,text in [('english',en),('korean',ko)]:loc[lang][key]=text
    def block(key,body):return f'{key} = {{\n{body}\n}}\n'
    def policy():return f'has_policy = policy:{FREE}'
    # Eligibility and quantities are bounded, read-only checks.
    triggers=[];values=[block('tsin_gold_cost_unit','value = 1\nadd = { value = capital_wealth multiply = 0.20 }\nadd = { value = country_economical_base multiply = 0.05 }\nmin = 1\nmax = 5000'),block('tsin_gold_cost_1','value = tsin_gold_cost_unit')];effects=[];guis=[];decisions=[];mods=[]
    law=['tsin_company_regime_law = { law_category = socioeconomic potential = { always = yes }']
    regimes=[('traditionalism',1337,2,'Traditionalism','전통주의'),('mercantilism',1450,3,'Mercantilism','중상주의'),
        ('interventionism',1600,5,'Interventionism','간섭주의'),('laissez_faire',1750,0,'Laissez-faire','자유방임주의'),
        ('state_capitalism',1800,7,'State capitalism','국가자본주의')]
    label('tsin_company_regime_law','Company and capital-market regime','기업·자본시장 체제')
    label('tsin_company_regime_law_desc','Controls company entry and private investment; industrial investment policy remains separate.','기업 진입과 민간 투자를 정합니다. 기존 산업 투자법은 별도로 유지됩니다.')
    label('tsin_company_regime_law_CATEGORY','Socioeconomic','사회경제')
    for id,year,limit,en,ko in regimes:
        law += [f'tsin_{id}_policy = {{ allow = {{ current_year >= {year} }} years = 5 estate_preferences = {{ '+('burghers_estate' if id=='laissez_faire' else 'crown_estate')+' } }']
        label(f'tsin_{id}_policy',en,ko)
        label(f'tsin_{id}_policy_desc',
            'Private firms use burgher capital and enter autonomously. There is no policy firm cap; persistent over-entry can create a bubble.' if not limit else f'Public founding and expansion are allowed; base company capacity {limit}, plus industrial-era additions.',
            '시민 계층의 자금으로 민간 기업이 자율적으로 진입합니다. 정책상 기업 수 상한은 없으며, 영업 기반을 지속적으로 넘는 과잉 진입은 버블을 일으킬 수 있습니다.' if not limit else f'국가의 기업 설립·확장이 가능합니다. 기본 기업 한도 {limit}개에 산업 시대의 추가 한도를 더합니다.')
    law+=['}'];out['in_game/common/laws/tsin_company_regime_law.txt']='\n'.join(law)+'\n'
    triggers += [block('tsin_company_is_private_trigger',policy()),block('tsin_company_has_room_trigger',f'OR = {{ {policy()} tsin_company_count < tsin_company_limit }}')]
    values += [block('TRY_REPLACE:tsin_company_limit','value = 2\n'+ '\n'.join(f'if = {{ limit = {{ has_policy = policy:tsin_{id}_policy }} value = {limit or 1000000} }}' for id,_,limit,_,_ in regimes)+'''
if = { limit = { has_advance = tsin_stock_exchange_advance } add = 1 }
if = { limit = { has_variable = tsin_charter_expansion } add = 1 }
if = { limit = { has_policy = policy:tsin_antitrust_policy NOT = { has_policy = policy:tsin_laissez_faire_policy } } subtract = 1 }
min = 1''')]
    values += [block('tsin_sustainable_firms','value = num_locations\ndivide = 8\nadd = 2\nif = { limit = { has_variable = tsin_factory_share } add = { value = var:tsin_factory_share multiply = 20 } }\nmin = 3')]
    # Each sector/name is a group; private generic groups may contain many firms.
    for row in rows:
        c=row['id'];cost=row.get('cost',2);unique=row.get('kind')=='national'
        hq=f'tsin_found_company_{c}_effect = yes' if row['kind']=='industrial' else 'capital ?= { root = { set_variable = { name = tsin_hq_'+c+' value = prev } } }'
        condition=f"current_year >= {row['year']} "+row.get('condition','')
        triggers += [block(f'tsin_company_eligible_{c}_trigger',condition)]
        values += [block(f'tsin_firm_number_{c}',f'''value = 0
if = {{ limit = {{ has_country_modifier = tsin_company_{c} }}
    value = 1
    if = {{ limit = {{ has_variable = tsin_firms_{c} }} value = var:tsin_firms_{c} }}
}}''')]
        if row['kind']!='industrial':
            values += [block(f'tsin_company_levels_{c}','value = num_locations\ndivide = 6\nmin = 1')]
            label(f'STATIC_MODIFIER_NAME_tsin_company_{c}',row['english'],row['korean'])
            label(f'STATIC_MODIFIER_DESC_tsin_company_{c}',row['description_en'],row['description_ko'])
            mods += [block(f'tsin_company_{c}','game_data = { category = country }\n'+row['modifier'])]
        firm=f'tsin_firm_number_{c}'
        effects += [block(f'tsin_capital_form_{c}_effect',f'''
if = {{ limit = {{ NOT = {{ has_country_modifier = tsin_company_{c} }} }}
    add_country_modifier = {{ modifier = tsin_company_{c} months = -1 }}
    set_variable = {{ name = tsin_firms_{c} value = 0 }}
    set_variable = {{ name = tsin_stock_{c} value = 100 }}
    {hq}
}}
if = {{ limit = {{ NOT = {{ has_variable = tsin_firms_{c} }} }} set_variable = {{ name = tsin_firms_{c} value = 1 }} }}
change_variable = {{ name = tsin_firms_{c} add = 1 }}
if = {{ limit = {{ tsin_exchange_can_open_trigger = yes }} set_variable = tsin_has_stock_market }}
''')]
        # Unique historical company names cannot be duplicated within the same country.
        unique_allow=f'NOT = {{ has_country_modifier = tsin_company_{c} }}' if unique else ''
        valid=f'tsin_company_eligible_{c}_trigger = yes NOT = {{ {policy()} }} tsin_company_has_room_trigger = yes gold >= tsin_gold_cost_{cost} {unique_allow}'
        guis += [block(f'tsin_capital_form_{c}',f'scope = country is_shown = {{ always = yes }} is_valid = {{ {valid} }} effect = {{ change_gold_effect = {{ scale = -{cost} }} tsin_capital_form_{c}_effect = yes tsin_capital_cache_effect = yes }}'),
            block(f'tsin_capital_visible_{c}',f'scope = country is_shown = {{ always = yes }} is_valid = {{ OR = {{ has_country_modifier = tsin_company_{c} tsin_company_eligible_{c}_trigger = yes }} }}'),
            block(f'tsin_capital_listed_{c}',f'scope = country is_shown = {{ always = yes }} is_valid = {{ has_country_modifier = tsin_company_{c} }}')]
        if row['kind']!='industrial':
            key=f'tsin_found_{c}_company_decision'
            decisions += [block(key,f'''decision_category = economy_decisions
image = "gfx/interface/icons/trade_goods/illustrations/icon_goods_{row['icon']}.dds"
potential = {{ tsin_company_eligible_{c}_trigger = yes NOT = {{ {policy()} }} {unique_allow} }}
allow = {{ {valid} }}
ai_will_do = {{ value = 10 }}
option = {{ name = {key}.a ai_chance = {{ value = 100 }} effect = {{ change_gold_effect = {{ scale = -2 }} tsin_capital_form_{c}_effect = yes tsin_capital_cache_effect = yes }} }}''')]
            label(key+'.title','Found / expand '+row['english'],row['korean']+' 설립·확장')
            label(key+'.desc',row['description_en']+' Requires company capacity and a non-laissez-faire regime.',row['description_ko']+' 자유방임 이외의 체제에서 기업 한도와 비용 조건을 충족해야 합니다.')
            label(key+'.a','Invest in the company','기업에 투자한다')
    values += [block('TRY_REPLACE:tsin_company_count','value = 0\n'+'\n'.join('add = tsin_firm_number_'+r['id'] for r in rows))]
    values += [block('TRY_REPLACE:tsin_location_company_hq','value = 0\n'+'\n'.join(f'if = {{ limit = {{ owner ?= {{ has_variable = tsin_hq_{r["id"]} }} this = owner.var:tsin_hq_{r["id"]} }} value = 1 }}' for r in rows))]
    weight='\n'.join(f'if = {{ limit = {{ tsin_firm_number_{r["id"]} > 0 has_variable = tsin_stock_{r["id"]} }} add = {{ value = tsin_company_levels_{r["id"]} add = 1 multiply = tsin_firm_number_{r["id"]} }} }}' for r in rows)
    values += [block('TRY_REPLACE:tsin_stock_index_weight','value = 0\n'+weight)]
    terms='\n'.join(f'if = {{ limit = {{ tsin_firm_number_{r["id"]} > 0 has_variable = tsin_stock_{r["id"]} }} add = {{ value = tsin_company_levels_{r["id"]} add = 1 multiply = tsin_firm_number_{r["id"]} multiply = var:tsin_stock_{r["id"]} }} }}' for r in rows)
    values += [block('TRY_REPLACE:tsin_stock_index_value','value = 0\n'+terms+'\nif = { limit = { tsin_stock_index_weight > 0 } divide = tsin_stock_index_weight }')]
    values += [block('TRY_REPLACE:tsin_company_total_value','value = 0\n'+ '\n'.join(f'if = {{ limit = {{ tsin_firm_number_{r["id"]} > 0 has_variable = tsin_stock_{r["id"]} }} add = {{ value = tsin_company_levels_{r["id"]} multiply = tsin_firm_number_{r["id"]} multiply = var:tsin_stock_{r["id"]} }} }}' for r in rows))]
    cache='''if = { limit = { tsin_company_count > 0 } set_variable = { name = tsin_stock_index value = tsin_stock_index_value } }
set_variable = { name = tsin_statistics_company_count value = tsin_company_count }
set_variable = { name = tsin_statistics_company_limit value = tsin_company_limit }
set_variable = { name = tsin_statistics_company_value value = tsin_company_total_value }
set_variable = { name = tsin_stock_ui_stats_year value = current_year }
'''
    cache+='\n'.join(f'set_variable = {{ name = tsin_stock_ui_levels_{r["id"]} value = tsin_company_levels_{r["id"]} }}' for r in rows)
    effects += [block('tsin_capital_cache_effect',cache)]
    for c in ['merchant_house','south_sea','merchant_bank','mississippi']:
        effects += [block(f'tsin_historic_finance_{c}_effect',f'''if = {{ limit = {{ NOT = {{ has_country_modifier = tsin_company_{c} }} tsin_company_eligible_{c}_trigger = yes tsin_company_has_room_trigger = yes }}
tsin_capital_form_{c}_effect = yes
}}
if = {{ limit = {{ tsin_company_count > 0 }}
tsin_scale_stocks_effect = {{ FACTOR = $FACTOR$ }}
{'' if c=='merchant_bank' else 'set_variable = { name = tsin_local_crash_cooldown years = 10 }'}
tsin_capital_cache_effect = yes
}}''')]
    init='\n'.join(f'''if = {{ limit = {{ has_country_modifier = tsin_company_{r['id']} }}
if = {{ limit = {{ NOT = {{ has_variable = tsin_stock_{r['id']} }} }} set_variable = {{ name = tsin_stock_{r['id']} value = 100 }} }}
if = {{ limit = {{ NOT = {{ has_variable = tsin_firms_{r['id']} }} }} set_variable = {{ name = tsin_firms_{r['id']} value = 1 }} }}
if = {{ limit = {{ NOT = {{ has_variable = tsin_hq_{r['id']} }} }} capital ?= {{ root = {{ set_variable = {{ name = tsin_hq_{r['id']} value = prev }} }} }} }}
if = {{ limit = {{ tsin_exchange_can_open_trigger = yes }} set_variable = tsin_has_stock_market }}
}}''' for r in rows)
    effects += [block('TRY_REPLACE:tsin_init_existing_companies_effect',init)]
    dissolve='\n'.join(f'''if = {{ limit = {{ has_country_modifier = tsin_company_{r['id']} }} remove_country_modifier = tsin_company_{r['id']} }}
remove_variable = tsin_firms_{r['id']}
remove_variable = tsin_stock_{r['id']}
remove_variable = tsin_hq_{r['id']}''' for r in rows)
    dissolve+='\ntsin_revoke_company_charters_effect = yes\nremove_variable = tsin_has_stock_market\nremove_variable = tsin_stock_index\nremove_variable = tsin_chairman\nif = { limit = { has_variable = tsin_charter_colonial } remove_variable = tsin_charter_colonial remove_country_modifier = tsin_charter_colonial_company }\n'
    dissolve+='\n'.join('remove_variable = tsin_index_h'+str(i) for i in range(8))
    dissolve+='\ntsin_capital_cache_effect = yes\n'
    effects += [block('TRY_REPLACE:tsin_dissolve_all_companies_effect',dissolve)]
    scale='\n'.join(f'if = {{ limit = {{ has_variable = tsin_stock_{r["id"]} }} change_variable = {{ name = tsin_stock_{r["id"]} multiply = $FACTOR$ }} clamp_variable = {{ name = tsin_stock_{r["id"]} min = 10 max = 1000 }} }}' for r in rows)
    effects += [block('TRY_REPLACE:tsin_scale_stocks_effect',scale+'\nif = { limit = { tsin_company_count > 0 } set_variable = { name = tsin_stock_index value = tsin_stock_index_value } }')]
    private=[];update=[]
    for r in rows:
        c=r['id'];good=r['good'];unique=r['kind']=='national'
        private += [f'''if = {{ limit = {{ {policy()} tsin_company_eligible_{c}_trigger = yes
NOT = {{ has_country_modifier = tsin_local_bubble_crash }}
{'NOT = { has_country_modifier = tsin_company_'+c+' }' if unique else ''}
any_estate = {{ estate_type = estate_type:burghers_estate estate_gold >= root.tsin_gold_cost_1 }}
capital ?= {{ market ?= {{ "goods_demand_in_market(goods:{good})" > 0 "market_price(goods:{good})" >= {{ value = "default_price(goods:{good})" multiply = 0.9 }} }} }} }}
random = {{ chance = 15
add_gold_to_estate = {{ estate_type = estate_type:burghers_estate value = {{ value = tsin_gold_cost_1 multiply = -1 }} }}
tsin_capital_form_{c}_effect = yes
}} }}''']
        update += [f'''if = {{ limit = {{ has_country_modifier = tsin_company_{c} }}
set_variable = {{ name = tsin_stock_up value = 0.5 }}
if = {{ limit = {{ capital ?= {{ market ?= {{ "market_price(goods:{good})" > {{ value = "default_price(goods:{good})" multiply = 1.1 }} }} }} }} change_variable = {{ name = tsin_stock_up add = 0.1 }} }}
if = {{ limit = {{ capital ?= {{ market ?= {{ "market_price(goods:{good})" < {{ value = "default_price(goods:{good})" multiply = 0.8 }} }} }} }} change_variable = {{ name = tsin_stock_up subtract = 0.15 }}
if = {{ limit = {{ {policy()} tsin_firm_number_{c} > 1 }} change_variable = {{ name = tsin_firms_{c} subtract = 1 }} }} }}
tsin_stock_random_walk_effect = {{ STOCK = tsin_stock_{c} }}
}}''']
    effects += [block('tsin_private_company_entry_effect','\n'.join(private))]
    effects += [block('TRY_REPLACE:tsin_update_stocks_effect','\n'.join(update)+'''
set_variable = { name = tsin_stock_index value = tsin_stock_index_value }
tsin_shift_stock_history_effect = yes
tsin_capital_cache_effect = yes''')]
    # A capital-market sample is bounded: one capital market, ten goods, no owned-location scan.
    oversupply=[]
    for good in ['cloth','paper','iron','steel','tools','coal','tsin_engines','tsin_fertilizer','tsin_oil','tsin_rubber']:
        oversupply += [f'''if = {{ limit = {{ "goods_demand_in_market(goods:{good})" > 0
"goods_supply_in_market(goods:{good})" >= {{ value = "goods_demand_in_market(goods:{good})" multiply = 1.5 }}
"market_price(goods:{good})" <= {{ value = "default_price(goods:{good})" multiply = 0.65 }} }}
root = {{ change_variable = {{ name = tsin_oversupplied_goods add = 1 }} }} }}''']
    risk='''set_variable = { name = tsin_oversupplied_goods value = 0 }
capital ?= { market ?= {
'''+ '\n'.join(oversupply)+'''
} }
if = { limit = { NOT = { has_variable = tsin_stress_quarters } } set_variable = { name = tsin_stress_quarters value = 0 } }
if = { limit = { tsin_company_count > 0 var:tsin_oversupplied_goods >= 2 } change_variable = { name = tsin_stress_quarters add = 1 } }
else = { set_variable = { name = tsin_stress_quarters value = 0 } }
if = { limit = { NOT = { has_variable = tsin_entry_risk_quarters } } set_variable = { name = tsin_entry_risk_quarters value = 0 } }
if = { limit = { has_policy = policy:tsin_laissez_faire_policy tsin_company_count >= 6 tsin_company_count > { value = tsin_sustainable_firms multiply = 1.5 } }
change_variable = { name = tsin_entry_risk_quarters add = 1 } }
else = { set_variable = { name = tsin_entry_risk_quarters value = 0 } }
set_variable = { name = tsin_finance_recent months = 4 }
'''
    effects += [block('tsin_capital_risk_effect',risk)]
    effects += [block('TRY_REPLACE:tsin_stock_market_events_effect','''
if = { limit = { NOT = { has_variable = tsin_local_crash_cooldown }
OR = { var:tsin_entry_risk_quarters >= 3 var:tsin_stress_quarters >= 4 } }
tsin_local_bubble_burst_effect = yes
}
''')]
    trim='\n'.join(f'if = {{ limit = {{ tsin_firm_number_{r["id"]} > 1 }} change_variable = {{ name = tsin_firms_{r["id"]} subtract = 1 }} }}' for r in rows)
    effects += [block('tsin_local_bubble_burst_effect','''set_variable = { name = tsin_local_crash_cooldown years = 10 }
tsin_scale_stocks_effect = { FACTOR = 0.75 }
add_country_modifier = { modifier = tsin_local_bubble_crash years = 2 }
set_variable = { name = tsin_entry_risk_quarters value = 0 }
'''+trim+'''
if = { limit = { is_ai = no } trigger_event_non_silently = tsin_finance.1 }
''')]
    # Aggregate only periodically. Require several independently stressed capital markets.
    world='''if = { limit = { current_year >= 1900 NOT = { has_global_variable = tsin_systemic_scan_timer } }
set_global_variable = { name = tsin_systemic_scan_timer months = 3 }
remove_global_variable = tsin_systemic_ready
set_global_variable = { name = tsin_stressed_countries value = 0 }
set_global_variable = { name = tsin_finance_countries value = 0 }
set_global_variable = { name = tsin_stressed_markets value = 0 }
every_country = { limit = { has_variable = tsin_finance_recent has_variable = tsin_factory_share var:tsin_factory_share >= 0.1 tsin_company_count > 0 }
change_global_variable = { name = tsin_finance_countries add = 1 }
if = { limit = { has_variable = tsin_stress_quarters var:tsin_stress_quarters >= 4 }
change_global_variable = { name = tsin_stressed_countries add = 1 }
capital ?= { market ?= { if = { limit = { NOT = { has_variable = tsin_market_stress_sample_timer } }
set_variable = { name = tsin_market_stress_sample_timer months = 2 }
change_global_variable = { name = tsin_stressed_markets add = 1 }
} } }
} }
if = { limit = { global_var:tsin_finance_countries >= 8 global_var:tsin_stressed_countries >= 5 global_var:tsin_stressed_markets >= 3
global_var:tsin_stressed_countries >= { value = global_var:tsin_finance_countries multiply = 0.35 }
NOT = { has_global_variable = tsin_systemic_crisis_cooldown }
NOT = { is_situation_active = situation:tsin_long_depression }
NOT = { has_global_variable = tsin_systemic_active } }
set_global_variable = { name = tsin_systemic_ready months = 3 }
}
}'''
    effects += [block('tsin_systemic_finance_check_effect',world)]
    regimes_check=' '.join(f'has_policy = policy:tsin_{id}_policy' for id,*_ in regimes)
    bootstrap=f'if = {{ limit = {{ NOT = {{ OR = {{ {regimes_check} }} }} }} change_policy = policy:tsin_traditionalism_policy }}'
    effects += [block('tsin_capital_policy_init_effect',bootstrap)]
    hooks=f'''monthly_country_pulse = {{ on_actions = {{ tsin_capital_monthly_pulse }} }}
tsin_capital_monthly_pulse = {{ trigger = {{ num_locations > 0 NOT = {{ has_variable = tsin_capital_timer }} }}
effect = {{ set_variable = {{ name = tsin_capital_timer months = 3 }}
{bootstrap}
tsin_init_existing_companies_effect = yes
tsin_private_company_entry_effect = yes
if = {{ limit = {{ tsin_company_count > 0 }}
tsin_capital_risk_effect = yes
tsin_stock_market_events_effect = yes
}}
if = {{ limit = {{ tsin_company_count > 0 NOT = {{ has_variable = tsin_stock_timer }} }}
set_variable = {{ name = tsin_stock_timer months = 3 }}
tsin_update_stocks_effect = yes
}}
tsin_capital_cache_effect = yes
if = {{ limit = {{ current_age_or_later = {{ age = age_7_industrialization }} tsin_company_count > 0 tsin_has_chairman_trigger = no }} trigger_event_non_silently = tsin_corporate.10 }}
tsin_systemic_finance_check_effect = yes
}} }}'''
    out['in_game/common/on_action/tsin_capital_on_actions.txt']=hooks+'\n'
    guis += [block('tsin_capital_is_private',f'scope = country is_shown = {{ always = yes }} is_valid = {{ {policy()} }}'),
        block('tsin_capital_refresh','scope = country is_shown = { always = yes } is_valid = { is_ai = no } effect = { tsin_init_existing_companies_effect = yes tsin_capital_cache_effect = yes }')]
    out['in_game/common/scripted_triggers/tsin_capital_triggers.txt']='\n'.join(triggers)
    out['in_game/common/script_values/zzzz_tsin_capital_values.txt']='\n'.join(values)
    out['in_game/common/scripted_effects/zzzz_tsin_capital_effects.txt']='\n'.join(effects)
    out['in_game/common/scripted_guis/tsin_capital_guis.txt']='\n'.join(guis)
    out['in_game/common/decisions/tsin_early_company_decisions.txt']='\n'.join(decisions)
    mods += [block('tsin_local_bubble_crash','game_data = { category = country }\nglobal_production_efficiency = -0.03\nbank_interest = 0.005'),
        block('tsin_systemic_depression','game_data = { category = country }\nglobal_production_efficiency = -0.12\nglobal_construction_speed = -0.15\nbank_interest = 0.015\nburghers_estate_target_satisfaction = -0.1'),
        block('tsin_systemic_trade_slump','game_data = { category = country }\nglobal_production_efficiency = -0.03')]
    for id,en,ko in [('tsin_local_bubble_crash','Local bubble collapse','국지적 버블 붕괴'),('tsin_systemic_depression','Systemic depression','세계 대공황'),('tsin_systemic_trade_slump','Global trade slump','세계 교역 침체')]:
        label('STATIC_MODIFIER_NAME_'+id,en,ko)
        label('STATIC_MODIFIER_DESC_'+id,'Financial contraction caused by observed market stress.','실제 시장 스트레스 조건으로 발생한 금융 수축입니다.')
    out['main_menu/common/static_modifiers/tsin_capital_modifiers.txt']='\n'.join(mods)
    out['in_game/common/situations/tsin_global_depression.txt']='''tsin_global_depression = {
monthly_spawn_chance = 100
can_start = { current_year >= 1900 has_global_variable = tsin_systemic_ready NOT = { has_global_variable = tsin_systemic_active } NOT = { is_situation_active = situation:tsin_long_depression } }
visible = { always = yes }
outcome = { name = tsin_global_depression_recovery trigger = { situation:tsin_global_depression = { years_since_situation_start > 2 } global_var:tsin_stressed_countries < 3 } }
outcome = { name = tsin_global_depression_timeout trigger = { situation:tsin_global_depression = { years_since_situation_start > 6 } } }
on_start = {
remove_global_variable = tsin_systemic_ready
set_global_variable = tsin_systemic_active
set_global_variable = { name = tsin_systemic_crisis_cooldown years = 25 }
every_country = { limit = { num_locations > 0 }
if = { limit = { has_variable = tsin_factory_share var:tsin_factory_share >= 0.1 }
add_country_modifier = { modifier = tsin_systemic_depression months = -1 }
set_variable = { name = tsin_financial_radicalization value = 15 years = 15 }
} else = { add_country_modifier = { modifier = tsin_systemic_trade_slump months = -1 } }
} }
on_ended = { remove_global_variable = tsin_systemic_active
every_country = { remove_country_modifier = tsin_systemic_depression remove_country_modifier = tsin_systemic_trade_slump }
}
}'''
    out['in_game/gui/panels/situation/tsin_global_depression.gui']='''situation_panel = {
blockoverride "situation_subheader_content" { text_single = { maximumsize = { 530 -1 } multiline = yes text = "TSIN_SYSTEMIC_GUIDE" } }
blockoverride "situation_panel_outcome_hint" {}
blockoverride "situation_panel_main_content" {}
}'''
    out['in_game/events/tsin_finance.txt']='''namespace = tsin_finance
tsin_finance.1 = { type = country_event title = tsin_finance.1.title desc = tsin_finance.1.desc outcome = negative
illustration_tags = { 10 = interior 10 = angry }
option = { name = tsin_finance.1.a }
}'''
    label('tsin_global_depression','Global Depression','세계 대공황')
    label('tsin_global_depression_desc','A sustained surplus of goods, depressed prices and financial contraction in several independent markets have transmitted a global crisis.','여러 독립 시장에서 지속된 상품 과잉공급·가격 폭락·금융 수축이 세계 위기로 전염되었습니다.')
    label('tsin_global_depression_recovery','Market recovery','시장 회복')
    label('tsin_global_depression_timeout','The contraction recedes','침체의 소멸')
    label('TSIN_SYSTEMIC_GUIDE','Requires 1900+, at least eight industrial financial economies; five stressed countries in at least three markets; four bad quarterly samples with two oversupplied, deeply discounted goods each. Minimum two years, maximum six, and a 25-year start cooldown.','1900년 이후 산업·금융 국가 8곳 이상 중 5곳 이상, 독립 시장 3곳 이상이 필요합니다. 각 국가에서 수요 대비 공급 150%·기준가 65% 이하인 상품 2종 이상이 4분기 지속되어야 합니다. 최소 2년·최대 6년, 시작 간격은 최소 25년입니다.')
    label('tsin_finance.1.title','Local company bubble bursts','기업 버블의 국지적 붕괴')
    label('tsin_finance.1.desc','Company entry persistently exceeded its business base, or four successive quarterly observations showed severe excess supply and depressed prices. Weak private firms consolidate and valuations fall. This event does not transmit a global crisis by itself.','기업 수가 영업 기반을 지속적으로 초과했거나 심한 과잉공급과 저가가 네 차례 연속 분기 관측되었습니다. 취약한 민간 기업이 정리되고 기업 가치가 재평가됩니다. 이 사건만으로 세계 위기가 전파되지는 않습니다.')
    label('tsin_finance.1.a','Let the market consolidate.','시장의 정리를 지켜본다.')
    for lang,labels in loc.items():out[f'main_menu/localization/{lang}/tsin_capital_l_{lang}.yml']='l_'+lang+':\n'+'\n'.join(' '+k+': '+json.dumps(v,ensure_ascii=False) for k,v in labels.items())+'\n'
    return {rel:'\n'.join(line.rstrip() for line in text.splitlines())+'\n' for rel,text in out.items()}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    files=build();bad=[]
    for rel,text in files.items():
        path=pdx.MOD_ROOT/rel
        if args.check:
            if not path.exists() or pdx.read_text(path)!=text:bad.append(rel)
        else:pdx.write_text_bom(path,text)
    print(f'{len(files)} capital-market files; {len(bad)} mismatches')
    for rel in bad:print(rel)
    return bool(bad)


if __name__=='__main__':raise SystemExit(main())
