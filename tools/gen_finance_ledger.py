"""Funded aggregate finance accounts; native ducats remain the settlement unit.

No native loan interest is charged here. Firm and bank accounts cover only the
additional TSIN facility. All money transfers debit an existing source first.
"""
import argparse
import json
import pdx
import finance_extended as extended
import corporate_finance as corporate
import finance_capabilities as capabilities
import finance_regulation as regulation

EXTRA_TABS = [('MONEY', 'tsin_money'), ('BANK', 'tsin_bank'), ('FUNDS', 'tsin_funds')]


def build():
    labels = {'english': {}, 'korean': {}}
    def loc(key, en, ko):
        key = 'TSIN_LEDGER_' + key
        labels['english'][key] = en
        labels['korean'][key] = ko
        return key
    loc('MONEY', 'Currency', '통화정책')
    loc('BANK', 'Banks · firms', '은행·기업금융')
    loc('FUNDS', 'Insurance · pensions', '보험·연금')
    loc('TECH_HELP', 'New banking requires Banking; securities require Stock Exchange; monetary policy requires Central Bank; insurance and pensions require their respective technologies. Existing account records, repayments and wind-down remain available.', '신규 은행업은 은행업, 증권 발행은 증권거래소, 통화정책은 중앙은행, 보험·연금은 해당 기술을 요구합니다. 기존 장부 조회·상환·영업 정리는 계속 가능합니다.')
    loc('NOTE', 'All accounts settle in reference ducats. Currency conversion is a display overlay; native trade and loans retain their original units. These are funded aggregate accounts, not population bank accounts. Reserve cash is escrow, not newly mined bullion. Firm income below is paid contracts, not estimated GDP or stock valuations.', '모든 장부는 기준 두캇으로 결제됩니다. 통화 환산은 표시 체계이며 기존 교역·대출의 단위는 유지됩니다. 기금은 실제 자금을 출연한 통합 장부입니다. 준비금은 별도 보관한 현금이며 광물 금 생산량이 아닙니다. 기업 수입은 실제 지급된 계약금으로 GDP·주가 추정치에서 현금을 생성하지 않습니다.')
    fields = [
        ('FX', 'Local units / reference ducat', '기준 두캇당 자국 화폐 단위', 'tsin_fx'),
        ('LOCAL', 'Treasury in local units', '자국 단위 국고', 'tsin_local_treasury'),
        ('RATE', 'New credit annual rate (%)', '신규 신용 계약 연 금리 (%)', 'tsin_rate'),
        ('RESERVE', 'Monetary reserve escrow', '통화 준비 현금', 'tsin_reserve'),
        ('LIQUID', 'Bank cash', '은행 현금', 'tsin_bank_cash'),
        ('LOANS', 'Bank loans = company principal', '은행 대출자산 = 기업 원금채무', 'tsin_firm_debt'),
        ('FIRM', 'Company cash', '기업 현금', 'tsin_firm_cash'),
        ('INTEREST', 'Last monthly interest paid', '최근 월 실제 이자 지급', 'tsin_interest_paid'),
        ('ARREARS', 'Missed-interest months', '이자 미지급 연속 개월', 'tsin_arrears'),
        ('INSURANCE', 'Insurance reserve', '보험 준비기금', 'tsin_insurance'),
        ('PENSION', 'Funded pension cash', '적립 연금 기금', 'tsin_pension'),
        ('BENEFITS', 'Last pension payment', '최근 월 연금 급여', 'tsin_pension_paid'),
    ]
    for key, en, ko, _ in fields: loc(key, en, ko)
    actions = []
    def action(id, en, ko, valid, effect, tab):
        label = loc(id.upper(), en, ko)
        actions.append((id, label, regulation.guard(id, capabilities.guard(id, valid)), effect, tab))
    extended.register(fields, action, loc)
    corporate.register(fields, action, loc)
    regulation.register(fields, action, loc)
    init = 'tsin_ledger_init_effect = yes\n'
    no_lf = 'NOT = { has_policy = policy:tsin_laissez_faire_policy }'
    cost = 'gold >= tsin_ledger_lot'
    debit = 'add_gold = { value = tsin_ledger_lot multiply = -1 }'
    for id, en, ko, var, tab in [
        ('reserve', 'Set aside reserve', '준비 현금 적립', 'tsin_reserve', 'MONEY'),
        ('bank', 'Capitalize bank', '은행 출자', 'tsin_bank_cash', 'BANK'),
        ('insurance', 'Fund insurance', '보험기금 출연', 'tsin_insurance', 'FUNDS'),
        ('pension', 'Contribute pension', '연금 출연', 'tsin_pension', 'FUNDS'),
    ]:
        action(id, en, ko, cost, f'{debit} change_variable = {{ name = {var} add = tsin_ledger_lot }}', tab)
    action('release', 'Release reserve', '준비 현금 인출', 'has_variable = tsin_reserve var:tsin_reserve >= tsin_ledger_lot', 'change_variable = { name = tsin_reserve subtract = tsin_ledger_lot } add_gold = tsin_ledger_lot', 'MONEY')
    action('rate_up', 'Rate +1 point', '금리 +1%p', 'var:tsin_rate < 20', 'change_variable = { name = tsin_rate add = 1 }', 'MONEY')
    action('rate_down', 'Rate -1 point', '금리 -1%p', 'var:tsin_rate > 0', 'change_variable = { name = tsin_rate subtract = 1 }', 'MONEY')
    action('devalue', 'Devalue 10%', '10% 평가절하', 'NOT = { has_variable = tsin_reform_cooldown } var:tsin_fx < 1000 OR = { NOT = { has_policy = policy:tsin_gold_standard_policy } has_variable = tsin_convertibility_suspended }', 'change_variable = { name = tsin_fx multiply = 1.10 } set_variable = { name = tsin_reform_cooldown months = 12 }', 'MONEY')
    action('redenominate', 'Redenominate 10:1', '10:1 화폐개혁', 'NOT = { has_variable = tsin_reform_cooldown } var:tsin_fx >= 10', 'tsin_currency_redenomination_effect = yes', 'MONEY')
    action('contract', 'Place paid company contract', '기업에 유상 계약 발주', f'{cost} tsin_company_count > 0 {no_lf}', f'{debit} change_variable = {{ name = tsin_firm_cash add = tsin_ledger_lot }}', 'BANK')
    action('lend', 'Issue funded company loan', '기업 대출 실행', f'var:tsin_bank_cash >= tsin_bank_lending_cash_required tsin_bank_net_worth >= 0 tsin_company_count > 0 {no_lf}', 'tsin_ledger_lend_effect = yes', 'BANK')
    action('repay', 'Repay company principal', '기업 원금 상환', 'var:tsin_firm_cash > 0 var:tsin_firm_debt > 0', 'tsin_ledger_repay_effect = yes', 'BANK')
    action('dividend', 'Distribute cash dividend', '현금 배당 지급', f'var:tsin_firm_cash >= tsin_ledger_lot var:tsin_firm_debt <= 0 var:tsin_bond_principal <= 0 var:tsin_foreign_liability_local <= 0 country_has_estate = estate_type:burghers_estate {no_lf}', 'tsin_corporate_dividend_effect = yes', 'BANK')
    # Claims are paid automatically once per observed, persistent cash-stress episode.
    action('pension_on', 'Enable monthly benefits', '매월 급여 지급 시작', 'country_has_estate = estate_type:peasants_estate NOT = { has_variable = tsin_pension_active } var:tsin_pension > 0', 'set_variable = tsin_pension_active', 'FUNDS')
    action('pension_off', 'Suspend future benefits', '향후 급여 지급 중단', 'has_variable = tsin_pension_active', 'remove_variable = tsin_pension_active', 'FUNDS')
    for key, en, ko in [
        ('REFORM_NOTE', 'Reforms change denomination only: they do not multiply treasury, reserves, native inflation or debt. This facility rate applies solely to TSIN company loans, not existing sovereign contracts.', '화폐개혁·평가절하는 표시 환산만 변경하며 국고·준비금·기존 부채를 늘리지 않습니다. 이 금리는 TSIN 기업 대출에만 적용되며 기존 국가 대출을 중복 청구하지 않습니다.'),
        ('FUND_NOTE', 'Pension benefits pay the peasant estate from existing funds, with no age-cohort estimate. Insurance pays at most 25% of its reserve after six consecutive missed-interest months, once per episode. Both stop at available cash.', '연금은 적립금에서 농민 계층에 지급하며 실제 고령 인구를 추정하지 않습니다. 보험은 이자 미지급 6개월 지속 시 준비기금의 최대 25%를 해당 연체기에 한 번만 지급합니다. 가용 기금 이상으로 지급하지 않습니다.'),
    ]: loc(key, en, ko)
    variables = ['tsin_reserve', 'tsin_bank_cash', 'tsin_firm_cash', 'tsin_firm_debt', 'tsin_arrears', 'tsin_insurance', 'tsin_pension', 'tsin_pension_paid', 'tsin_interest_paid']
    variables += extended.VARIABLES + corporate.VARIABLES + ['tsin_bank_audit_paid', 'tsin_firm_audit_paid']
    effects = ['# GENERATED funded accounts; missing legacy variables initialize without endowments.', 'tsin_ledger_init_effect = {']
    for var, default in [(v, 0) for v in variables] + [('tsin_fx', 1), ('tsin_rate', 4), ('tsin_issued_shares', 100)]:
        effects.append(f'if = {{ limit = {{ NOT = {{ has_variable = {var} }} }} set_variable = {{ name = {var} value = {default} }} }}')
    effects += ['set_variable = { name = tsin_ledger_version value = 2 }', '}', '''
tsin_ledger_lend_effect = {
 if = { limit = { has_global_variable = tsin_contracts_enabled } tsin_contract_lend_facility_effect = yes }
 else = { tsin_ledger_lend_effect_legacy = yes }
}
tsin_ledger_lend_effect_legacy = {
    if = { limit = { tsin_bank_underwriting_allowed = yes tsin_firm_disclosure_allowed = yes var:tsin_bank_cash >= tsin_bank_lending_cash_required tsin_bank_net_worth >= 0 tsin_company_count > 0 }
        change_variable = { name = tsin_bank_cash subtract = tsin_ledger_lot }
        change_variable = { name = tsin_firm_cash add = tsin_ledger_lot }
        change_variable = { name = tsin_firm_debt add = tsin_ledger_lot }
    }
}
tsin_ledger_repay_effect = {
 if = { limit = { has_global_variable = tsin_contracts_enabled } tsin_contract_repay_facility_effect = yes }
 else = { tsin_ledger_repay_effect_legacy = yes }
}
tsin_ledger_repay_effect_legacy = {
    set_variable = { name = tsin_tx value = tsin_ledger_repayment }
    change_variable = { name = tsin_firm_cash subtract = var:tsin_tx }
    change_variable = { name = tsin_bank_cash add = var:tsin_tx }
    change_variable = { name = tsin_firm_debt subtract = var:tsin_tx }
    remove_variable = tsin_tx
}
tsin_ledger_month_effect = {
    tsin_ledger_init_effect = yes
    tsin_bank_optional_month_effect = yes
    tsin_corporate_finance_month_effect = yes
    if = { limit = { NOT = { has_variable = tsin_contract_managed } }
    set_variable = { name = tsin_interest_paid value = tsin_ledger_interest_payment }
    change_variable = { name = tsin_firm_cash subtract = var:tsin_interest_paid }
    change_variable = { name = tsin_bank_cash add = var:tsin_interest_paid }
    if = { limit = { var:tsin_interest_paid < tsin_ledger_interest_due }
        change_variable = { name = tsin_arrears add = 1 }
    }
    else = {
        set_variable = { name = tsin_arrears value = 0 }
        if = { limit = { var:tsin_bond_arrears = 0 } remove_variable = tsin_insurance_claimed }
    }
    }
    if = { limit = { var:tsin_arrears = 0 var:tsin_bond_arrears = 0 } remove_variable = tsin_insurance_claimed }
    if = { limit = { OR = { var:tsin_arrears >= 6 var:tsin_bond_arrears >= 6 } NOT = { has_variable = tsin_insurance_claimed } var:tsin_insurance > 0 }
        set_variable = { name = tsin_tx value = tsin_ledger_claim }
        change_variable = { name = tsin_insurance subtract = var:tsin_tx }
        change_variable = { name = tsin_firm_cash add = var:tsin_tx }
        set_variable = tsin_insurance_claimed
        remove_variable = tsin_tx
    }
    set_variable = { name = tsin_pension_paid value = 0 }
    if = { limit = { has_variable = tsin_pension_active country_has_estate = estate_type:peasants_estate var:tsin_pension > 0 }
        set_variable = { name = tsin_pension_paid value = tsin_ledger_benefit }
        change_variable = { name = tsin_pension subtract = var:tsin_pension_paid }
        add_gold_to_estate = { estate_type = estate_type:peasants_estate value = var:tsin_pension_paid }
    }
    if = { limit = { is_ai = yes }
        if = { limit = { has_policy = policy:tsin_laissez_faire_policy tsin_company_count > 0
            any_estate = { estate_type = estate_type:burghers_estate estate_gold >= root.tsin_ledger_lot }
            var:tsin_firm_cash < tsin_ledger_lot }
            add_gold_to_estate = { estate_type = estate_type:burghers_estate value = { value = tsin_ledger_lot multiply = -1 } }
            change_variable = { name = tsin_firm_cash add = tsin_ledger_lot }
        }
        if = { limit = { var:tsin_firm_cash > 0 var:tsin_firm_debt > 0 } tsin_ledger_repay_effect = yes }
    }
}
''']
    effects.append(extended.EFFECTS)
    effects.append(corporate.EFFECTS)
    values = '''tsin_ledger_lot = { value = tsin_gold_cost_1 min = 1 }
tsin_local_treasury = { value = gold multiply = var:tsin_fx }
tsin_ledger_repayment = { value = var:tsin_firm_cash max = var:tsin_firm_debt min = 0 }
tsin_ledger_interest_due = { value = var:tsin_firm_debt multiply = var:tsin_rate divide = 1200 }
tsin_ledger_interest_payment = { value = tsin_ledger_interest_due max = var:tsin_firm_cash min = 0 }
tsin_ledger_benefit = { value = tsin_ledger_lot multiply = 0.05 max = var:tsin_pension min = 0 }
tsin_ledger_claim = { value = var:tsin_insurance multiply = 0.25 max = tsin_ledger_lot min = 0 }
'''
    values += extended.VALUES + corporate.VALUES
    guis = []
    ui = ['types TSINLedger {']
    field_tabs = {'MONEY': ['FX', 'LOCAL', 'RATE', 'RESERVE'], 'BANK': ['LIQUID', 'LOANS', 'FIRM', 'INTEREST', 'ARREARS', 'DEPOSITS', 'WITHDRAWALS', 'LIQUIDITY', 'FOREIGN', 'FOREIGN_LOCAL', 'FOREIGN_OWED', 'LOSSES', 'SHARES', 'PUBLIC_SHARES', 'BONDS', 'BOND_ARREARS', 'BOND_LOSSES', 'UNKNOWN_MATURITY', 'UNKNOWN_ID', 'BANK_AUDIT_PAID', 'FIRM_AUDIT_PAID'], 'FUNDS': ['INSURANCE', 'PENSION', 'BENEFITS', 'PENSION_GAP']}
    for name, subtab in EXTRA_TABS:
        ui += [f'type {subtab}_panel = scrollarea {{ using = layoutpolicy_expanding scrollbarpolicy_horizontal = always_off scrollbar_vertical = {{ using = Scrollbar_Vertical }} scrollwidget = {{ vbox = {{ using = layoutpolicy_expanding using = bg_main_inner_alt using = window_main_tabs_margin_alt spacing = 8', f'text_single = {{ fontsize = 22 text = "TSIN_LEDGER_{name}" }}', 'text_single = { maximumsize = { 520 -1 } multiline = yes text = "TSIN_LEDGER_TECH_HELP" }']
        if name == 'BANK':
            ui += ["text_single = { text = \"[GetPlayer.Custom('tsin_bank_audit_status')]\" }", "text_single = { text = \"[GetPlayer.Custom('tsin_firm_audit_status')]\" }"]
        for key, _, _, var in fields:
            if key not in field_tabs[name]: continue
            # Script values initialize only on monthly tick or explicit action, never on render.
            expression = f"GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('{var}')|2L" if key == 'LOCAL' else f"GetPlayer.MakeScope.GetVariable('{var}').GetValue|2L"
            ui += [f'hbox = {{ spacing = 8 text_single = {{ size = {{ 330 26 }} text = "TSIN_LEDGER_{key}" }} text_single = {{ text = "[{expression}]" }} }}']
        for id, label, valid, effect, tab in actions:
            if tab != name: continue
            ui += [f'''button_regular = {{ size = {{ 480 28 }}
enabled = "[GetScriptedGui('tsin_ledger_{id}').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
action_tooltip = {{ title = "{label}" on_action = "[GetScriptedGui('tsin_ledger_{id}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" }}
text_single = {{ parentanchor = center align = center text = "{label}" }} }}''']
        note = 'REFORM_NOTE' if name == 'MONEY' else 'FUND_NOTE' if name == 'FUNDS' else 'BANK_NOTE'
        if name == 'BANK': ui += ['text_single = { maximumsize = { 520 -1 } multiline = yes text = "TSIN_LEDGER_AUDIT_NOTE" }']
        ui += [f'text_single = {{ maximumsize = {{ 520 -1 }} multiline = yes text = "TSIN_LEDGER_{note}" }}', '} } }']
    ui += ['}']
    for id, label, valid, effect, _ in actions:
        # The same guard is checked at execution, not only the GUI enabled state.
        guis.append(f'tsin_ledger_{id} = {{ scope = country is_shown = {{ always = yes }} is_valid = {{ {valid} }} effect = {{ {init} if = {{ limit = {{ {valid} }} {effect} }} }} }}')
    result = {
        'in_game/common/scripted_effects/tsin_finance_ledger_effects.txt': '\n'.join(effects),
        'in_game/common/script_values/tsin_finance_ledger_values.txt': values,
        'in_game/common/scripted_guis/tsin_finance_ledger_guis.txt': '\n'.join(guis),
        'in_game/common/on_action/tsin_finance_ledger_on_actions.txt': '''monthly_country_pulse = { on_actions = { tsin_finance_ledger_monthly } }
yearly_country_pulse = { on_actions = { tsin_ai_finance_yearly } }
tsin_ai_finance_yearly = { trigger = { is_ai = yes current_year >= 1600 tsin_company_count > 0 } effect = { tsin_ai_finance_year_effect = yes } }
tsin_finance_ledger_monthly = { trigger = { num_locations > 0 OR = { is_ai = no tsin_company_count > 0 has_variable = tsin_ledger_version } } effect = { tsin_ledger_month_effect = yes } }
''',
        'in_game/gui/tsin_finance_ledger.gui': '\n'.join(ui),
    }
    result['in_game/common/scripted_triggers/tsin_finance_extended_triggers.txt'] = extended.TRIGGERS
    result['main_menu/common/static_modifiers/tsin_finance_extended_modifiers.txt'] = extended.MODIFIERS
    loc('UNIT', 'Accounting currency: [GetPlayer.Custom(\'tsin_currency_name\')]', '표시 화폐: [GetPlayer.Custom(\'tsin_currency_name\')]')
    loc('CURRENCY_LOCAL', 'National accounting unit', '국가 환산 단위')
    currency = ['tsin_currency_name = { type = country']
    for tags, code, en, ko in [(['ENG','SCO','GBR'],'GBP','Pound sterling','파운드 스털링'),(['FRA'],'FRF','Franc','프랑'),(['PRU','GER'],'DEM','Mark / thaler accounting unit','마르크·탈러 환산 단위'),(['RUS','MOS'],'RUB','Ruble','루블'),(['JAP'],'JPY','Yen / ryo accounting unit','엔·료 환산 단위'),(['CHI','TQG','MCH'],'TAEL','Silver tael','은량'),(['MUG'],'INR','Rupee','루피'),(['USA'],'USD','Dollar','달러'),(['MEX','XAR','XCZ','XCO','XPE','XBO','XUY'],'PESO','Peso','페소'),(['XBR'],'BRL','Real','헤알')]:
        loc('CURRENCY_'+code,en,ko)
        currency.append('text = { trigger = { OR = { '+' '.join('tag = '+t for t in tags)+' } } localization_key = TSIN_LEDGER_CURRENCY_'+code+' }')
    currency.append('text = { fallback = yes localization_key = TSIN_LEDGER_CURRENCY_LOCAL } }')
    result['in_game/common/customizable_localization/tsin_currency_names.txt'] = '\n'.join(currency)
    result['in_game/gui/tsin_finance_ledger.gui'] = result['in_game/gui/tsin_finance_ledger.gui'].replace('text_single = { fontsize = 22 text = "TSIN_LEDGER_MONEY" }','text_single = { fontsize = 22 text = "TSIN_LEDGER_MONEY" }\ntext_single = { text = "TSIN_LEDGER_UNIT" }')
    loc('CONTRACTION_NAME','Bank credit contraction','은행 신용 위축')
    loc('CONTRACTION_DESC','Unpaid depositor withdrawals persisted for four quarterly reviews. Restore liquidity and settle claims to recover.','예금 인출 미지급이 4회 분기 점검 동안 지속되었습니다. 유동성을 확보하고 인출 채권을 결제하면 회복됩니다.')
    loc('SUSPENSION_NAME','Suspended gold convertibility','금 태환 정지')
    loc('SUSPENSION_DESC','Temporarily suspended convertibility brings inflationary pressure and a native borrowing premium.','일시적인 태환 정지로 물가 압력과 기본 차입 금리 가산이 발생합니다.')
    for lang in labels:
        labels[lang]['STATIC_MODIFIER_NAME_tsin_convertibility_suspension'] = labels[lang].pop('TSIN_LEDGER_SUSPENSION_NAME')
        labels[lang]['STATIC_MODIFIER_DESC_tsin_convertibility_suspension'] = labels[lang].pop('TSIN_LEDGER_SUSPENSION_DESC')
        labels[lang]['STATIC_MODIFIER_NAME_tsin_bank_credit_contraction'] = labels[lang].pop('TSIN_LEDGER_CONTRACTION_NAME')
        labels[lang]['STATIC_MODIFIER_DESC_tsin_bank_credit_contraction'] = labels[lang].pop('TSIN_LEDGER_CONTRACTION_DESC')
    for lang, entries in labels.items():
        result[f'main_menu/localization/{lang}/tsin_finance_ledger_l_{lang}.yml'] = 'l_'+lang+':\n'+'\n'.join(' '+k+': '+json.dumps(v,ensure_ascii=False) for k,v in entries.items())+'\n'
    result.update(regulation.build())
    return capabilities.add_outputs({k: '\n'.join(line.rstrip() for line in v.splitlines())+'\n' for k,v in result.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    bad = []
    for rel, text in build().items():
        path = pdx.MOD_ROOT/rel
        if args.check:
            if not path.exists() or pdx.read_text(path) != text: bad.append(rel)
        else: pdx.write_text_bom(path, text)
    print(f'Finance ledger: {len(bad)} mismatches')
    for rel in bad: print(rel)
    return bool(bad)


if __name__ == '__main__': raise SystemExit(main())
