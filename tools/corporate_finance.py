"""Equity subscriptions and a single funded private bond per country aggregate."""

VARIABLES=['tsin_bond_losses','tsin_public_shares','tsin_bond_principal','tsin_bond_interest_paid','tsin_bond_arrears','tsin_pension_shortfall']


def register(fields,action,loc):
    for key,en,ko,var in [
        ('SHARES','Issued ownership units','발행 소유 지분','tsin_issued_shares'),
        ('PUBLIC_SHARES','Publicly held units','국가 보유 지분','tsin_public_shares'),
        ('BOND_LOSSES','Private bond write-offs','민간 회사채 상각 손실','tsin_bond_losses'),
        ('BONDS','Company bonds = private claims','회사채 원금 = 민간 채권','tsin_bond_principal'),
        ('BOND_ARREARS','Bond missed-interest months','회사채 이자 미지급 개월','tsin_bond_arrears'),
        ('PENSION_GAP','Pay-as-you-go missed contributions','부과방식 미납 개월','tsin_pension_shortfall'),
    ]:fields.append((key,en,ko,var));loc(key,en,ko)
    private='any_estate = { estate_type = estate_type:burghers_estate estate_gold >= root.tsin_ledger_lot }'
    public='NOT = { has_policy = policy:tsin_laissez_faire_policy }'
    action('private_equity','Invite private equity','민간 유상증자 모집',f'tsin_company_count > 0 {private} {public} NOT = {{ has_variable = tsin_equity_cooldown }}','tsin_private_equity_effect = yes','BANK')
    action('public_equity','Subscribe public equity','국가 지분 출자',f'tsin_company_count > 0 gold >= tsin_ledger_lot {public} NOT = {{ has_variable = tsin_equity_cooldown }}','add_gold = { value = tsin_ledger_lot multiply = -1 } change_variable = { name = tsin_firm_cash add = tsin_ledger_lot } change_variable = { name = tsin_public_shares add = 10 } change_variable = { name = tsin_issued_shares add = 10 } set_variable = { name = tsin_equity_cooldown years = 1 }','BANK')
    action('bond','Place a funded private bond','민간 회사채 발행',f'tsin_company_count > 0 var:tsin_bond_principal = 0 {private} {public} NOT = {{ has_variable = tsin_bond_issue_cooldown }}','tsin_corporate_bond_issue_effect = yes','BANK')
    action('bond_writeoff','Restructure defaulted bond','부실 회사채 조정','var:tsin_bond_principal > 0 var:tsin_bond_arrears >= 12 NOT = { has_variable = tsin_bond_writeoff_cooldown }','if = { limit = { has_variable = tsin_contract_managed } tsin_contract_adjust_private_effect = { KIND = 3 LOSS = yes AMOUNT = { value = var:tsin_bond_principal multiply = 0.25 } } set_variable = { name = tsin_bond_writeoff_cooldown years = 3 } } else = { set_variable = { name = tsin_tx value = { value = var:tsin_bond_principal multiply = 0.25 } } change_variable = { name = tsin_bond_principal subtract = var:tsin_tx } change_variable = { name = tsin_bond_losses add = var:tsin_tx } remove_variable = tsin_tx set_variable = { name = tsin_bond_writeoff_cooldown years = 3 } }','BANK')
    action('paygo_on','Enable pay-as-you-go funding','부과방식 국고 납입 시작','NOT = { has_variable = tsin_pension_paygo }','set_variable = tsin_pension_paygo set_variable = tsin_pension_active','FUNDS')
    action('paygo_off','Stop pay-as-you-go funding','부과방식 국고 납입 중단','has_variable = tsin_pension_paygo','remove_variable = tsin_pension_paygo','FUNDS')


VALUES='''
tsin_dividend_public = { value = tsin_ledger_lot multiply = var:tsin_public_shares divide = var:tsin_issued_shares min = 0 max = tsin_ledger_lot }
tsin_dividend_private = { value = tsin_ledger_lot subtract = tsin_dividend_public min = 0 }
tsin_bond_interest_due = { value = var:tsin_bond_principal divide = 300 }
tsin_bond_interest_payment = { value = tsin_bond_interest_due max = var:tsin_firm_cash min = 0 }
tsin_bond_repayment = { value = var:tsin_bond_principal max = var:tsin_firm_cash min = 0 }
tsin_pension_contribution = { value = tsin_ledger_lot multiply = 0.05 }
'''

EFFECTS='''
tsin_private_equity_effect = {
if = { limit = { any_estate = { estate_type = estate_type:burghers_estate estate_gold >= root.tsin_ledger_lot } NOT = { has_variable = tsin_equity_cooldown } }
add_gold_to_estate = { estate_type = estate_type:burghers_estate value = { value = tsin_ledger_lot multiply = -1 } }
change_variable = { name = tsin_firm_cash add = tsin_ledger_lot }
change_variable = { name = tsin_issued_shares add = 10 }
set_variable = { name = tsin_equity_cooldown years = 1 }
}
}
tsin_corporate_dividend_effect = {
if = { limit = { var:tsin_firm_cash >= tsin_ledger_lot var:tsin_firm_debt <= 0 var:tsin_bond_principal <= 0 var:tsin_foreign_liability_local <= 0 }
set_variable = { name = tsin_tx_public value = tsin_dividend_public }
set_variable = { name = tsin_tx_private value = tsin_dividend_private }
change_variable = { name = tsin_firm_cash subtract = tsin_ledger_lot }
add_gold = var:tsin_tx_public
add_gold_to_estate = { estate_type = estate_type:burghers_estate value = var:tsin_tx_private }
remove_variable = tsin_tx_public remove_variable = tsin_tx_private
}
}
tsin_corporate_bond_issue_effect = {
 if = { limit = { has_global_variable = tsin_contracts_enabled } tsin_contract_issue_bond_effect = yes }
 else = { tsin_corporate_bond_issue_effect_legacy = yes }
}
tsin_corporate_bond_issue_effect_legacy = {
if = { limit = { var:tsin_bond_principal = 0 NOT = { has_variable = tsin_bond_issue_cooldown }
any_estate = { estate_type = estate_type:burghers_estate estate_gold >= root.tsin_ledger_lot } }
add_gold_to_estate = { estate_type = estate_type:burghers_estate value = { value = tsin_ledger_lot multiply = -1 } }
change_variable = { name = tsin_firm_cash add = tsin_ledger_lot }
set_variable = { name = tsin_bond_principal value = tsin_ledger_lot }
set_variable = { name = tsin_bond_maturity months = 36 }
set_variable = { name = tsin_bond_issue_cooldown years = 4 }
}
}
tsin_corporate_finance_month_effect = {
if = { limit = { has_variable = tsin_pension_paygo }
if = { limit = { gold >= tsin_pension_contribution }
add_gold = { value = tsin_pension_contribution multiply = -1 }
change_variable = { name = tsin_pension add = tsin_pension_contribution }
set_variable = { name = tsin_pension_shortfall value = 0 }
}
else = { change_variable = { name = tsin_pension_shortfall add = 1 } }
}
if = { limit = { NOT = { has_variable = tsin_contract_managed } }
if = { limit = { country_has_estate = estate_type:burghers_estate var:tsin_bond_principal > 0 }
set_variable = { name = tsin_bond_interest_paid value = tsin_bond_interest_payment }
change_variable = { name = tsin_firm_cash subtract = var:tsin_bond_interest_paid }
add_gold_to_estate = { estate_type = estate_type:burghers_estate value = var:tsin_bond_interest_paid }
if = { limit = { var:tsin_bond_interest_paid < tsin_bond_interest_due } change_variable = { name = tsin_bond_arrears add = 1 } }
else = { set_variable = { name = tsin_bond_arrears value = 0 } }
if = { limit = { NOT = { has_variable = tsin_bond_maturity } }
set_variable = { name = tsin_tx value = tsin_bond_repayment }
change_variable = { name = tsin_firm_cash subtract = var:tsin_tx }
change_variable = { name = tsin_bond_principal subtract = var:tsin_tx }
add_gold_to_estate = { estate_type = estate_type:burghers_estate value = var:tsin_tx }
remove_variable = tsin_tx
}
}
}
if = { limit = { var:tsin_bond_principal <= 0 } set_variable = { name = tsin_bond_arrears value = 0 } set_variable = { name = tsin_bond_interest_paid value = 0 } }
if = { limit = { has_policy = policy:tsin_laissez_faire_policy tsin_company_count > 0 }
if = { limit = { var:tsin_firm_cash < tsin_ledger_lot NOT = { has_variable = tsin_equity_cooldown } } tsin_private_equity_effect = yes }
if = { limit = { var:tsin_firm_cash >= { value = tsin_ledger_lot multiply = 2 } country_has_estate = estate_type:burghers_estate }
tsin_corporate_dividend_effect = yes
}
}
}
'''
