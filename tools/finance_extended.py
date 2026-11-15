"""Optional deposits and bilateral, borrower-currency business credit.

These accounts are separate from native sovereign credit. Foreign principal is
stored in borrower local units; revaluation changes claims, not cash balances.
"""

VARIABLES = ['tsin_foreign_delinquency','tsin_deposits','tsin_withdrawal_due','tsin_liquidity_debt','tsin_foreign_principal','tsin_foreign_local_principal','tsin_foreign_liability_local','tsin_foreign_age','tsin_bank_losses','tsin_bank_stress','tsin_foreign_interest_paid']


def register(fields, action, loc):
    for key,en,ko,var in [
        ('FOREIGN_OWED','Foreign principal · local units','외채 원금 · 자국 단위','tsin_foreign_liability_local'),
        ('DEPOSITS','Burgher deposit claims','시민 예금채권','tsin_deposits'),
        ('WITHDRAWALS','Unpaid withdrawal requests','미지급 인출 요구','tsin_withdrawal_due'),
        ('LIQUIDITY','Reserve facility principal','준비금 유동성 차입','tsin_liquidity_debt'),
        ('FOREIGN','Foreign credit · reference value','해외 신용자산 · 기준가액','tsin_foreign_principal'),
        ('FOREIGN_LOCAL','Foreign credit · borrower units','해외 신용자산 · 차입국 단위','tsin_foreign_local_principal'),
        ('LOSSES','Cumulative credit write-offs','누적 신용 상각','tsin_bank_losses'),
    ]:
        fields.append((key,en,ko,var));loc(key,en,ko)
    action('suspend_gold','Suspend convertibility','태환 일시 정지','has_policy = policy:tsin_gold_standard_policy NOT = { has_variable = tsin_convertibility_suspended }','set_variable = { name = tsin_convertibility_suspended years = 5 } add_country_modifier = { modifier = tsin_convertibility_suspension years = 5 mode = replace } add_prestige = -10','MONEY')
    action('open_bank','Open deposit bank','예금은행 영업 개시','var:tsin_bank_cash >= tsin_ledger_lot NOT = { has_variable = tsin_bank_open }','set_variable = tsin_bank_open','BANK')
    action('stop_deposits','Close new deposits','신규 예금 중단','has_variable = tsin_bank_open','remove_variable = tsin_bank_open set_variable = tsin_bank_winding_down','BANK')
    action('liquidity','Provide reserve liquidity','준비 현금으로 유동성 대출','var:tsin_reserve >= tsin_ledger_lot var:tsin_withdrawal_due > 0','change_variable = { name = tsin_reserve subtract = tsin_ledger_lot } change_variable = { name = tsin_bank_cash add = tsin_ledger_lot } change_variable = { name = tsin_liquidity_debt add = tsin_ledger_lot }','BANK')
    action('liquidity_repay','Repay reserve facility','준비금 대출 상환','var:tsin_bank_cash > 0 var:tsin_liquidity_debt > 0','set_variable = { name = tsin_tx value = tsin_liquidity_repayment } change_variable = { name = tsin_bank_cash subtract = var:tsin_tx } change_variable = { name = tsin_reserve add = var:tsin_tx } change_variable = { name = tsin_liquidity_debt subtract = var:tsin_tx } remove_variable = tsin_tx','BANK')
    action('writeoff','Restructure distressed business loan','부실 기업 채무 조정','var:tsin_arrears >= 12 var:tsin_firm_debt > 0 NOT = { has_variable = tsin_writeoff_cooldown }','set_variable = { name = tsin_tx value = tsin_credit_writeoff } change_variable = { name = tsin_firm_debt subtract = var:tsin_tx } change_variable = { name = tsin_bank_losses add = var:tsin_tx } remove_variable = tsin_tx set_variable = { name = tsin_writeoff_cooldown years = 3 }','BANK')
    action('foreign','Fund one overseas credit contract','해외 기업 신용 계약 체결','var:tsin_bank_cash >= tsin_ledger_lot NOT = { has_variable = tsin_foreign_partner } NOT = { has_variable = tsin_foreign_cooldown } current_year >= 1600 any_country = { tsin_foreign_recipient_trigger = yes }','tsin_foreign_open_effect = yes','BANK')
    loc('BANK_NOTE','Deposit banking is opt-in. Deposits debit burgher cash and create bank liabilities. Withdrawals retain unpaid claims; reserve lending must be repaid. Overseas credit selects one independent AI with a funded company cash account. Principal is denominated in borrower currency: devaluation reduces its reference value. No native foreign-exchange settlement or sovereign-loan replacement is implied.','예금 영업은 별도로 개시해야 합니다. 예금은 시민 현금을 차감하고 은행의 채무로 기록하며 미지급 인출은 채권으로 남습니다. 준비금 대출은 상환해야 합니다. 해외 신용은 독립 AI의 기업 현금 계정을 대상으로 한 건만 체결합니다. 원금은 차입국 화폐로 표시하므로 평가절하 시 기준 가액이 줄어듭니다. 기존 국가 대출과는 별도 계약입니다.')


VALUES = '''
tsin_bank_assets = { value = var:tsin_bank_cash add = var:tsin_firm_debt add = var:tsin_foreign_principal }
tsin_bank_liabilities = { value = var:tsin_deposits add = var:tsin_liquidity_debt }
tsin_bank_net_worth = { value = tsin_bank_assets subtract = tsin_bank_liabilities }
tsin_bank_lending_cash_required = { value = tsin_ledger_lot add = { value = var:tsin_deposits multiply = 0.20 } }
tsin_deposit_request = { value = tsin_ledger_lot multiply = 0.10 }
tsin_withdrawal_request = { value = var:tsin_deposits multiply = 0.40 min = var:tsin_withdrawal_due max = var:tsin_deposits if = { limit = { has_variable = tsin_bank_winding_down } value = var:tsin_deposits } min = 0 }
tsin_withdrawal_payment = { value = var:tsin_withdrawal_due max = var:tsin_bank_cash max = var:tsin_deposits min = 0 }
tsin_liquidity_repayment = { value = var:tsin_liquidity_debt max = var:tsin_bank_cash min = 0 }
tsin_credit_writeoff = { value = var:tsin_firm_debt multiply = 0.25 min = 0 }
tsin_foreign_current_value = { value = var:tsin_foreign_local_principal divide = scope:tsin_foreign_partner.var:tsin_fx }
tsin_foreign_interest_due = { value = var:tsin_foreign_principal multiply = 0.01 }
tsin_foreign_interest_payment = { value = tsin_foreign_interest_due max = scope:tsin_foreign_partner.var:tsin_firm_cash min = 0 }
tsin_foreign_principal_payment = { value = var:tsin_foreign_principal max = scope:tsin_foreign_partner.var:tsin_firm_cash min = 0 }
tsin_foreign_local_payment = { value = var:tsin_tx multiply = scope:tsin_foreign_partner.var:tsin_fx }
'''

TRIGGERS = '''tsin_foreign_recipient_trigger = {
tsin_history_ai_realm = yes is_subject = no at_war = no
NOT = { this = root } tsin_company_count > 0 has_variable = tsin_ledger_version
has_variable = tsin_fx var:tsin_fx > 0 var:tsin_arrears = 0
}
'''

EFFECTS = '''
tsin_foreign_open_effect = {
save_scope_as = tsin_foreign_lender
if = { limit = { var:tsin_bank_cash >= tsin_bank_lending_cash_required tsin_bank_net_worth >= 0
NOT = { has_variable = tsin_foreign_partner } NOT = { has_variable = tsin_foreign_cooldown } }
ordered_country = {
limit = { tsin_foreign_recipient_trigger = yes }
order_by = num_locations max = 1
tsin_ledger_init_effect = yes
save_scope_as = tsin_foreign_partner
scope:tsin_foreign_lender = {
set_variable = { name = tsin_foreign_partner value = scope:tsin_foreign_partner }
set_variable = { name = tsin_foreign_principal value = tsin_ledger_lot }
set_variable = { name = tsin_foreign_local_principal value = { value = tsin_ledger_lot multiply = scope:tsin_foreign_partner.var:tsin_fx } }
change_variable = { name = tsin_bank_cash subtract = var:tsin_foreign_principal }
set_variable = { name = tsin_foreign_age value = 0 }
set_variable = { name = tsin_foreign_delinquency value = 0 }
set_variable = { name = tsin_foreign_cooldown years = 3 }
}
change_variable = { name = tsin_firm_cash add = scope:tsin_foreign_lender.var:tsin_foreign_principal }
change_variable = { name = tsin_foreign_liability_local add = scope:tsin_foreign_lender.var:tsin_foreign_local_principal }
}
}
}
tsin_foreign_service_effect = {
save_scope_as = tsin_foreign_lender
if = { limit = { var:tsin_foreign_partner ?= { num_locations > 0 has_variable = tsin_fx var:tsin_fx > 0 } }
var:tsin_foreign_partner = { save_scope_as = tsin_foreign_partner }
set_variable = { name = tsin_foreign_principal value = tsin_foreign_current_value }
set_variable = { name = tsin_foreign_interest_paid value = tsin_foreign_interest_payment }
change_variable = { name = tsin_bank_cash add = var:tsin_foreign_interest_paid }
scope:tsin_foreign_partner = { change_variable = { name = tsin_firm_cash subtract = scope:tsin_foreign_lender.var:tsin_foreign_interest_paid } }
if = { limit = { var:tsin_foreign_interest_paid < tsin_foreign_interest_due } change_variable = { name = tsin_foreign_delinquency add = 1 } }
else = { set_variable = { name = tsin_foreign_delinquency value = 0 } }
change_variable = { name = tsin_foreign_age add = 1 }
if = { limit = { var:tsin_foreign_age >= 4 }
set_variable = { name = tsin_tx value = tsin_foreign_principal_payment }
set_variable = { name = tsin_tx_local value = tsin_foreign_local_payment }
change_variable = { name = tsin_bank_cash add = var:tsin_tx }
scope:tsin_foreign_partner = {
change_variable = { name = tsin_firm_cash subtract = scope:tsin_foreign_lender.var:tsin_tx }
change_variable = { name = tsin_foreign_liability_local subtract = scope:tsin_foreign_lender.var:tsin_tx_local }
}
change_variable = { name = tsin_foreign_local_principal subtract = var:tsin_tx_local }
change_variable = { name = tsin_foreign_principal subtract = var:tsin_tx }
remove_variable = tsin_tx remove_variable = tsin_tx_local
if = { limit = { var:tsin_foreign_local_principal <= 0 }
set_variable = { name = tsin_foreign_principal value = 0 }
set_variable = { name = tsin_foreign_local_principal value = 0 }
remove_variable = tsin_foreign_partner
}
}
if = { limit = { var:tsin_foreign_delinquency >= 12 var:tsin_foreign_principal > 0 }
scope:tsin_foreign_partner = { change_variable = { name = tsin_foreign_liability_local subtract = scope:tsin_foreign_lender.var:tsin_foreign_local_principal } }
change_variable = { name = tsin_bank_losses add = var:tsin_foreign_principal }
set_variable = { name = tsin_foreign_principal value = 0 }
set_variable = { name = tsin_foreign_local_principal value = 0 }
remove_variable = tsin_foreign_partner
}
}
else = {
# A vanished borrower is a loss, not a treasury payout or an endless stale link.
change_variable = { name = tsin_bank_losses add = var:tsin_foreign_principal }
set_variable = { name = tsin_foreign_principal value = 0 }
set_variable = { name = tsin_foreign_local_principal value = 0 }
remove_variable = tsin_foreign_partner
}
}
tsin_bank_quarter_effect = {
if = { limit = { has_variable = tsin_foreign_partner } tsin_foreign_service_effect = yes }
if = { limit = { country_has_estate = estate_type:burghers_estate }
if = { limit = { has_variable = tsin_bank_open var:tsin_arrears = 0 var:tsin_bank_stress = 0 tsin_bank_net_worth >= 0
any_estate = { estate_type = estate_type:burghers_estate estate_gold >= root.tsin_deposit_request } }
add_gold_to_estate = { estate_type = estate_type:burghers_estate value = { value = tsin_deposit_request multiply = -1 } }
change_variable = { name = tsin_bank_cash add = tsin_deposit_request }
change_variable = { name = tsin_deposits add = tsin_deposit_request }
}
if = { limit = { var:tsin_deposits > 0 OR = { var:tsin_withdrawal_due > 0 var:tsin_arrears >= 6 has_variable = tsin_bank_winding_down
AND = { has_variable = tsin_stress_quarters var:tsin_stress_quarters >= 4 } } }
set_variable = { name = tsin_withdrawal_due value = tsin_withdrawal_request }
set_variable = { name = tsin_tx value = tsin_withdrawal_payment }
change_variable = { name = tsin_bank_cash subtract = var:tsin_tx }
change_variable = { name = tsin_deposits subtract = var:tsin_tx }
change_variable = { name = tsin_withdrawal_due subtract = var:tsin_tx }
add_gold_to_estate = { estate_type = estate_type:burghers_estate value = var:tsin_tx }
remove_variable = tsin_tx
}
}
if = { limit = { OR = { var:tsin_withdrawal_due > 0 tsin_bank_net_worth < 0 } } change_variable = { name = tsin_bank_stress add = 1 } }
else = { set_variable = { name = tsin_bank_stress value = 0 } }
if = { limit = { var:tsin_bank_stress >= 4 }
add_country_modifier = { modifier = tsin_bank_credit_contraction months = 4 mode = replace }
}
else = { remove_country_modifier = tsin_bank_credit_contraction }
if = { limit = { var:tsin_deposits <= 0 } remove_variable = tsin_bank_winding_down }
}
tsin_ai_finance_year_effect = {
tsin_ledger_init_effect = yes
if = { limit = { OR = { NOT = { has_variable = tsin_bank_open } tsin_bank_net_worth < 0 } NOT = { has_variable = tsin_bank_winding_down } gold >= { value = tsin_ledger_lot multiply = 5 } }
add_gold = { value = tsin_ledger_lot multiply = -1 }
change_variable = { name = tsin_bank_cash add = tsin_ledger_lot } set_variable = tsin_bank_open
}
if = { limit = { var:tsin_bank_cash >= tsin_bank_lending_cash_required tsin_company_count > 0 var:tsin_arrears = 0 var:tsin_firm_cash < tsin_ledger_lot } tsin_ledger_lend_effect = yes }
}
tsin_bank_optional_month_effect = {
if = { limit = { OR = { has_variable = tsin_bank_open has_variable = tsin_bank_winding_down has_variable = tsin_foreign_partner } NOT = { has_variable = tsin_bank_quarter_timer } }
set_variable = { name = tsin_bank_quarter_timer months = 3 }
tsin_bank_quarter_effect = yes
}
}
'''

MODIFIERS = '''tsin_convertibility_suspension = { game_data = { category = country } monthly_inflation = 0.01 bank_interest = 0.01 }
tsin_bank_credit_contraction = {
game_data = { category = country }
global_construction_speed = -0.10
global_production_efficiency = -0.05
}
'''
