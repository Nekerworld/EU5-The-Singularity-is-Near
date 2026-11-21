"""Bank supervision and paid disclosure. Existing contracts are never gated."""
import json

def guard(action_id, valid):
    if action_id in ('lend','foreign','foreign_long'):
        valid = 'tsin_bank_underwriting_allowed = yes '+valid
    if action_id in ('lend','bond','private_equity','public_equity'):
        valid = 'tsin_firm_disclosure_allowed = yes '+valid
    return valid

def register(fields,action,loc):
    for key,en,ko,var in [
        ('BANK_AUDIT_PAID','Last bank audit payment','최근 은행 감사 비용','tsin_bank_audit_paid'),
        ('FIRM_AUDIT_PAID','Last corporate audit payment','최근 기업 공시 감사 비용','tsin_firm_audit_paid')]:
        fields.append((key,en,ko,var));loc(key,en,ko)
    action('audit_bank','Commission a bank audit (12 months)','은행 감사 의뢰 (12개월)',
           'tsin_can_use_banking = yes NOT = { has_variable = tsin_bank_audit_valid } tsin_bank_assets > 0 var:tsin_bank_cash >= tsin_bank_audit_cost',
           'tsin_paid_bank_audit_effect = yes','BANK')
    action('audit_firm','Commission corporate disclosure (12 months)','기업 공시 감사 의뢰 (12개월)',
           'tsin_can_use_capital_markets = yes tsin_company_count > 0 NOT = { has_variable = tsin_firm_audit_valid } var:tsin_firm_cash >= tsin_firm_audit_cost',
           'tsin_paid_firm_audit_effect = yes','BANK')
    action('bank_loss_grant','Cover bank capital shortfall (fiscal grant)','은행 자본 결손 보전 (국고 보조금)',
           'tsin_bank_net_worth < 0 gold >= tsin_bank_loss_grant NOT = { has_variable = tsin_bank_grant_cooldown }',
           'tsin_bank_loss_grant_effect = yes','BANK')
    loc('AUDIT_NOTE','Prudential/strict supervision requires a paid bank audit for new lending. Mandatory disclosure requires a paid corporate audit for new loans, bonds and equity. Audits last 12 months; bank cash pays 1% of bank assets and company cash pays 1% of one transaction lot (minimum 0.01). Existing interest, repayment, withdrawal and winding-down remain available. Government loss support is a grant, not a loan or ownership stake.',
        '건전성·엄격 감독에서는 신규 대출에 유료 은행 감사가 필요합니다. 의무 공시에서는 신규 대출·회사채·증자에 기업 감사가 필요합니다. 유효기간은 12개월이며 은행은 자산의 1%, 기업은 거래 단위의 1%(최소 0.01두캇)를 각자 현금에서 지불합니다. 기존 이자·원금·예금 인출·영업 정리는 유지됩니다. 결손 보전은 상환 청구권·국가 지분이 없는 보조금입니다.')

TRIGGERS='''tsin_bank_underwriting_allowed = {
 NOT = { has_variable = tsin_bank_winding_down }
 OR = {
  NOT = { OR = { has_policy = policy:tsin_bank_prudential_policy has_policy = policy:tsin_bank_strict_policy } }
  has_variable = tsin_bank_audit_valid
 }
}
tsin_firm_disclosure_allowed = {
 OR = { NOT = { has_policy = policy:tsin_disclosure_audited_policy } has_variable = tsin_firm_audit_valid }
}
'''
VALUES='''tsin_bank_reserve_ratio = {
 value = 0.20
 if = { limit = { has_policy = policy:tsin_bank_free_policy } value = 0.10 }
 else_if = { limit = { has_policy = policy:tsin_bank_prudential_policy } value = 0.30 }
 else_if = { limit = { has_policy = policy:tsin_bank_strict_policy } value = 0.40 }
}
tsin_bank_audit_cost = { value = tsin_bank_assets multiply = 0.01 min = 0.01 }
tsin_firm_audit_cost = { value = tsin_ledger_lot multiply = 0.01 min = 0.01 }
tsin_bank_loss_grant = { value = tsin_bank_net_worth multiply = -1 min = 0 add = tsin_ledger_lot }
'''
EFFECTS='''tsin_paid_bank_audit_effect = {
 if = { limit = { tsin_can_use_banking = yes NOT = { has_variable = tsin_bank_audit_valid } tsin_bank_assets > 0 var:tsin_bank_cash >= tsin_bank_audit_cost }
  set_variable = { name = tsin_bank_audit_paid value = tsin_bank_audit_cost }
  change_variable = { name = tsin_bank_cash subtract = var:tsin_bank_audit_paid }
  set_variable = { name = tsin_bank_audit_valid months = 12 }
 }
}
tsin_paid_firm_audit_effect = {
 if = { limit = { tsin_can_use_capital_markets = yes tsin_company_count > 0 NOT = { has_variable = tsin_firm_audit_valid } var:tsin_firm_cash >= tsin_firm_audit_cost }
  set_variable = { name = tsin_firm_audit_paid value = tsin_firm_audit_cost }
  change_variable = { name = tsin_firm_cash subtract = var:tsin_firm_audit_paid }
  set_variable = { name = tsin_firm_audit_valid months = 12 }
 }
}
tsin_bank_loss_grant_effect = {
 if = { limit = { tsin_bank_net_worth < 0 gold >= tsin_bank_loss_grant NOT = { has_variable = tsin_bank_grant_cooldown } }
  save_temporary_scope_value_as = { name = tsin_grant_amount value = tsin_bank_loss_grant }
  add_gold = { value = scope:tsin_grant_amount multiply = -1 }
  change_variable = { name = tsin_bank_cash add = scope:tsin_grant_amount }
  set_variable = { name = tsin_bank_grant_cooldown years = 5 }
 }
}
tsin_finance_regulation_ai_effect = {
 if = { limit = { OR = { has_policy = policy:tsin_bank_prudential_policy has_policy = policy:tsin_bank_strict_policy } var:tsin_bank_cash >= { value = tsin_bank_lending_cash_required add = tsin_bank_audit_cost } tsin_bank_net_worth >= tsin_bank_audit_cost }
  tsin_paid_bank_audit_effect = yes
 }
 if = { limit = { has_policy = policy:tsin_disclosure_audited_policy var:tsin_firm_cash >= { value = tsin_ledger_lot add = tsin_firm_audit_cost } }
  tsin_paid_firm_audit_effect = yes
 }
}
tsin_bank_distress_review_effect = {
 if = { limit = { is_ai = no tsin_bank_net_worth < 0 var:tsin_deposits > 0 NOT = { has_variable = tsin_bank_distress_news_cooldown } }
  set_variable = { name = tsin_bank_distress_news_cooldown years = 10 }
  trigger_event_non_silently = tsin_finance_regulation.1
 }
}
'''

def build():
    laws=['# Existing saves retain the old 20% ratio and no compulsory audit unless a new policy is adopted.']
    entries={}
    for law,title,ko,potential,policies in [
      ('tsin_bank_supervision_law','Bank supervision','은행 감독','tsin_can_use_banking = yes',[
       ('tsin_bank_customary_policy','Customary banking','관행적 은행 감독','', 'burghers_estate','Retains the existing 20% cash reserve for new loans.','신규 대출에 기존 20% 현금 준비 기준을 유지합니다.'),
       ('tsin_bank_free_policy','Free banking','자유 은행업','', 'burghers_estate nobles_estate','New loans retain a 10% deposit cash reserve.','신규 대출 시 예금의 10% 현금 준비를 남깁니다.'),
       ('tsin_bank_prudential_policy','Prudential supervision','건전성 감독','', 'crown_estate','New loans require 30% deposit reserves and a paid annual audit.','신규 대출에 예금 준비 30%와 유료 연간 감사를 요구합니다.'),
       ('tsin_bank_strict_policy','Strict supervision','엄격한 은행 감독','tsin_can_use_monetary_policy = yes','peasants_estate clergy_estate','New loans require 40% deposit reserves and a paid annual audit.','신규 대출에 예금 준비 40%와 유료 연간 감사를 요구합니다.')]),
      ('tsin_corporate_disclosure_law','Corporate disclosure','기업 정보 공개','tsin_can_use_capital_markets = yes',[
       ('tsin_disclosure_customary_policy','Voluntary disclosure','자율 공시','','burghers_estate nobles_estate','No additional audit condition for new finance.','신규 금융에 추가 감사 조건을 두지 않습니다.'),
       ('tsin_disclosure_audited_policy','Audited public accounts','감사받은 의무 공시','','crown_estate peasants_estate','New credit, bond issues and equity require a paid annual corporate audit. Existing claims continue to be serviced.','신규 신용·회사채·증자에 유료 연간 감사를 요구합니다. 기존 채권의 지급은 계속됩니다.')])]:
        laws.append(f'{law} = {{ law_category = socioeconomic potential = {{ {potential} }}')
        entries[law]=(ko,title);entries[law+'_desc']=(ko+' 제도를 정합니다.',title+' rules.')
        for key,en,kr,gate,estates,desc,kdesc in policies:
            laws.append(f'{key} = {{ allow = {{ {gate} tsin_policy_enactable_trigger = yes }} years = 5 estate_preferences = {{ {estates} }} }}')
            entries[key]=(kr,en);entries[key+'_desc']=(kdesc,desc)
        laws.append('}')
    event='''namespace = tsin_finance_regulation
tsin_finance_regulation.1 = {
 type = country_event outcome = negative
 title = tsin_finance_regulation.1.title desc = tsin_finance_regulation.1.desc
 illustration_tags = { 10 = interior 10 = regular }
 option = { name = tsin_finance_regulation.1.a
  trigger = { tsin_bank_net_worth < 0 gold >= tsin_bank_loss_grant NOT = { has_variable = tsin_bank_grant_cooldown } }
  tsin_bank_loss_grant_effect = yes
  ai_chance = { factor = 0 }
 }
 option = { name = tsin_finance_regulation.1.b
  if = { limit = { tsin_bank_net_worth < 0 }
   remove_variable = tsin_bank_open set_variable = tsin_bank_winding_down
  }
  ai_chance = { factor = 1 }
 }
 option = { name = tsin_finance_regulation.1.c ai_chance = { factor = 5 } }
}
'''
    entries.update({
      'tsin_finance_regulation.1.title':('예금 은행의 자본 결손','Deposit-bank capital shortfall'),
      'tsin_finance_regulation.1.desc':('은행의 장부 자산이 예금·준비금 대출 채무보다 적습니다. 단순 현금 부족과 다른 자본 결손입니다. 국고 보조금은 현재 결손과 거래 단위 한 번을 실제 국고에서 지급하며 국가 지분이나 상환 채권을 만들지 않습니다. 영업 정리는 신규 대출·예금을 중단하지만 기존 자산·채무·인출 청구권을 보존합니다. 이 사건만으로 세계 공황은 시작하지 않습니다.','Recorded bank assets are below deposit and reserve-facility liabilities. This is a capital shortfall, not merely a cash shortage. Fiscal support pays the actual shortfall plus one transaction lot; it creates neither state equity nor a repayment claim. Wind-down stops new loans and deposits while preserving assets, debts and withdrawal claims. This event does not start a global depression.'),
      'tsin_finance_regulation.1.a':('국고에서 결손 보조금을 지급한다','Pay a fiscal loss-covering grant'),
      'tsin_finance_regulation.1.b':('신규 영업을 중지하고 기존 채권을 정리한다','Wind down new business; preserve existing claims'),
      'tsin_finance_regulation.1.c':('추가 조치 없이 장부를 계속 관찰한다','Continue observing without additional action')})
    custom=[]
    for name,kr,en in [('bank','은행','Bank'),('firm','기업','Corporate')]:
        for state,ko_desc,en_desc in [('valid','유효 (유료 감사 후 12개월)','valid (12 months from payment)'),('missing','미완료 또는 만료','not completed or expired')]:
            entries[f'TSIN_{name.upper()}_AUDIT_{state.upper()}']=(kr+' 감사: '+ko_desc,en+' audit: '+en_desc)
        custom.append(f'''tsin_{name}_audit_status = {{ type = country
 text = {{ trigger = {{ has_variable = tsin_{name}_audit_valid }} localization_key = TSIN_{name.upper()}_AUDIT_VALID }}
 text = {{ fallback = yes localization_key = TSIN_{name.upper()}_AUDIT_MISSING }}
}}''')
    out={'in_game/common/laws/tsin_finance_regulation_laws.txt':'\n'.join(laws),
      'in_game/common/customizable_localization/tsin_finance_regulation.txt':'\n'.join(custom),
      'in_game/common/scripted_triggers/tsin_finance_regulation.txt':TRIGGERS,
      'in_game/common/script_values/tsin_finance_regulation.txt':VALUES,
      'in_game/common/scripted_effects/tsin_finance_regulation.txt':EFFECTS,
      'in_game/events/tsin_finance_regulation.txt':event}
    for lang,i in [('korean',0),('english',1)]:
        out[f'main_menu/localization/{lang}/tsin_finance_regulation_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {key}: '+json.dumps(val[i],ensure_ascii=False)+'\n' for key,val in entries.items())
    return {k:v.rstrip()+'\n' for k,v in out.items()}
