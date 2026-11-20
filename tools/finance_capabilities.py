"""Technology permissions at player/AI entry points; servicing remains available."""
TRIGGERS = '''tsin_can_use_banking = { OR = { has_advance = banking_advance has_advance = tsin_stock_exchange_advance } }
tsin_can_use_capital_markets = { OR = { has_advance = stock_exchange_advance has_advance = tsin_stock_exchange_advance } }
# Exchange operation: founding and the monthly init set tsin_has_stock_market only while this holds. Existing listings are never cancelled by it.
tsin_exchange_can_open_trigger = { tsin_can_use_capital_markets = yes }
tsin_can_use_monetary_policy = { OR = { has_advance = central_bank_advance has_advance = tsin_central_banking } }
tsin_can_use_insurance = { OR = { has_advance = insurance_companies has_advance = tsin_social_insurance_advance } }
tsin_can_use_pensions = { has_advance = tsin_social_insurance_advance }
tsin_can_fund_bank = { OR = { tsin_can_use_banking = yes has_variable = tsin_bank_open has_variable = tsin_bank_winding_down } }
tsin_can_fund_insurance = { OR = { tsin_can_use_insurance = yes var:tsin_insurance > 0 } }
tsin_can_fund_pension = { OR = { tsin_can_use_pensions = yes has_variable = tsin_pension_active var:tsin_pension > 0 } }
'''

GATES={
 'reserve':'tsin_can_use_monetary_policy',
 'rate_up':'tsin_can_use_monetary_policy','rate_down':'tsin_can_use_monetary_policy',
 'devalue':'tsin_can_use_monetary_policy','redenominate':'tsin_can_use_monetary_policy',
 'suspend_gold':'tsin_can_use_monetary_policy',
 'bank':'tsin_can_fund_bank','open_bank':'tsin_can_use_banking','lend':'tsin_can_use_banking',
 'foreign':'tsin_can_use_capital_markets','foreign_long':'tsin_can_use_capital_markets',
 'private_equity':'tsin_can_use_banking','public_equity':'tsin_can_use_capital_markets',
 'bond':'tsin_can_use_capital_markets',
 'insurance':'tsin_can_fund_insurance','pension':'tsin_can_fund_pension',
 'pension_on':'tsin_can_use_pensions','paygo_on':'tsin_can_use_pensions',
}

def guard(action_id,valid):
    capability=GATES.get(action_id)
    return (capability+' = yes '+valid) if capability else valid

def add_outputs(outputs):
    outputs['in_game/common/scripted_triggers/tsin_finance_capabilities.txt']=TRIGGERS
    return outputs
