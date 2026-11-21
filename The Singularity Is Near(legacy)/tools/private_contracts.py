"""Private loan/bond tranches use the same persistent contract rows as foreign credit."""
import pdx
from finance_contracts import read as r, put as w


def replace_block(text,name,replacement):
    block=next(b for b in pdx.top_level_blocks(text) if b.key==name)
    return text.replace(block.text,replacement,1)


def row(kind,principal,rate,maturity,mode='0'):
    values={'lender':'scope:tsin_fc_lender','borrower':'scope:tsin_fc_borrower','currency':'scope:tsin_fc_borrower','currency_live':'0','fx':'1','principal':principal,'rate':rate,'maturity':maturity,'next_coupon':'{ value = tsin_contract_calendar_month add = 1 }','period':'1','missed':'0','kind':str(kind),'maturity_mode':mode,'timer_origin':'scope:tsin_fc_borrower'}
    return '\n'.join(w(k,v) for k,v in values.items())


def triggers():
    return f'''tsin_contract_mature_trigger = {{
 OR = {{
  AND = {{ {r('maturity_mode')} = 0 {r('maturity')} >= 0 tsin_contract_calendar_month >= {r('maturity')} }}
  AND = {{ {r('maturity_mode')} = 1 {r('timer_origin')} ?= {{ NOT = {{ has_variable = tsin_bond_maturity }} }} }}
 }}
}}
'''


def extend_effects(text):
    text=text.replace('limit = { has_variable = tsin_foreign_partner } tsin_contract_migrate_legacy_effect', 'limit = { has_variable = tsin_ledger_version NOT = { has_variable = tsin_contract_managed } } tsin_contract_migrate_legacy_effect')
    block=next(b for b in pdx.top_level_blocks(text) if b.key=='tsin_contract_migrate_legacy_effect')
    text=text.replace(block.text,block.text[:-1]+' tsin_contract_migrate_private_effect = yes\n}',1)
    text=text.replace('tsin_contract_init_effect = yes\n set_global_variable', 'tsin_contract_init_effect = yes\n set_global_variable',1)
    block=next(b for b in pdx.top_level_blocks(text) if b.key=='tsin_contract_allocate_effect')
    text=text.replace(block.text,block.text[:-1]+w('maturity_mode','0')+'\n'+w('timer_origin','scope:tsin_fc_borrower')+'\n}',1)
    service=f'''tsin_contract_service_one_effect = {{
 tsin_contract_bind_effect = yes
 if = {{ limit = {{ scope:tsin_fc_lender ?= {{ num_locations > 0 }} scope:tsin_fc_borrower ?= {{ num_locations > 0 }}
 {r('fx')} > 0 tsin_contract_calendar_month >= {r('next_coupon')}
 OR = {{ {r('kind')} != 3 scope:tsin_fc_lender ?= {{ country_has_estate = estate_type:burghers_estate }} }} }}
 save_temporary_scope_value_as = {{ name = tsin_fc_due value = tsin_contract_interest_due }}
 save_temporary_scope_value_as = {{ name = tsin_fc_paid value = {{ value = scope:tsin_fc_due max = scope:tsin_fc_borrower.var:tsin_firm_cash min = 0 }} }}
 scope:tsin_fc_borrower = {{ change_variable = {{ name = tsin_firm_cash subtract = scope:tsin_fc_paid }} }}
 if = {{ limit = {{ {r('kind')} = 3 }}
  scope:tsin_fc_lender = {{ add_gold_to_estate = {{ estate_type = estate_type:burghers_estate value = scope:tsin_fc_paid }} }}
  scope:tsin_fc_borrower = {{ change_variable = {{ name = tsin_bond_interest_paid add = scope:tsin_fc_paid }} }}
 }}
 else = {{
  scope:tsin_fc_lender = {{ change_variable = {{ name = tsin_bank_cash add = scope:tsin_fc_paid }} }}
  if = {{ limit = {{ {r('kind')} = 2 }} scope:tsin_fc_borrower = {{ change_variable = {{ name = tsin_interest_paid add = scope:tsin_fc_paid }} }} }}
 }}
 if = {{ limit = {{ scope:tsin_fc_paid < scope:tsin_fc_due }} {w('missed','{ value = '+r('missed')+' add = 1 }')} }}
 else = {{ {w('missed','0')} }}
 {w('next_coupon','{ value = tsin_contract_calendar_month add = '+r('period')+' }')}
 if = {{ limit = {{ tsin_contract_mature_trigger = yes }}
  save_temporary_scope_value_as = {{ name = tsin_fc_principal_paid value = {{ value = tsin_contract_reference_principal max = scope:tsin_fc_borrower.var:tsin_firm_cash min = 0 }} }}
  scope:tsin_fc_borrower = {{ change_variable = {{ name = tsin_firm_cash subtract = scope:tsin_fc_principal_paid }} }}
  if = {{ limit = {{ {r('kind')} = 3 }} scope:tsin_fc_lender = {{ add_gold_to_estate = {{ estate_type = estate_type:burghers_estate value = scope:tsin_fc_principal_paid }} }} }}
  else = {{ scope:tsin_fc_lender = {{ change_variable = {{ name = tsin_bank_cash add = scope:tsin_fc_principal_paid }} }} }}
  {w('principal','{ value = '+r('principal')+' subtract = { value = scope:tsin_fc_principal_paid multiply = '+r('fx')+' } min = 0 }')}
 }}
 if = {{ limit = {{ {r('kind')} = 1 {r('missed')} >= 12 {r('principal')} > 0 }}
  scope:tsin_fc_lender = {{ change_variable = {{ name = tsin_bank_losses add = tsin_contract_reference_principal }} }}
  {w('principal','0')}
 }}
 if = {{ limit = {{ {r('principal')} <= 0 }} tsin_contract_forget_effect = yes }}
 }}
}}
'''
    text=replace_block(text,'tsin_contract_service_one_effect',service)
    refresh=f'''tsin_contract_refresh_effect = {{
 every_country = {{ limit = {{ has_variable = tsin_contract_managed }}
  set_variable = {{ name = tsin_foreign_principal value = 0 }}
  set_variable = {{ name = tsin_foreign_liability_local value = 0 }}
  set_variable = {{ name = tsin_foreign_contract_count value = 0 }}
  set_variable = {{ name = tsin_firm_debt value = 0 }}
  set_variable = {{ name = tsin_bond_principal value = 0 }}
  set_variable = {{ name = tsin_arrears value = 0 }}
  set_variable = {{ name = tsin_bond_arrears value = 0 }}
  set_variable = {{ name = tsin_unknown_legacy_maturities value = 0 }}
  set_variable = {{ name = tsin_unknown_maturity_contract_id value = 0 }}
 }}
 save_scope_as = tsin_contract_coordinator
 every_in_global_list = {{ variable = tsin_active_contracts
  save_temporary_scope_value_as = {{ name = tsin_contract_id value = this }}
  scope:tsin_contract_coordinator = {{
   tsin_contract_bind_effect = yes
   if = {{ limit = {{ {r('kind')} = 1 }}
    scope:tsin_fc_lender ?= {{ change_variable = {{ name = tsin_foreign_principal add = tsin_contract_reference_principal }} change_variable = {{ name = tsin_foreign_contract_count add = 1 }} }}
    scope:tsin_fc_borrower ?= {{ change_variable = {{ name = tsin_foreign_liability_local add = {{ value = tsin_contract_reference_principal multiply = var:tsin_fx }} }} }}
   }}
   if = {{ limit = {{ {r('kind')} = 2 }}
    scope:tsin_fc_borrower ?= {{
     change_variable = {{ name = tsin_firm_debt add = tsin_contract_reference_principal }}
     set_variable = {{ name = tsin_arrears value = {{ value = var:tsin_arrears min = {r('missed')} }} }}
    }}
   }}
   if = {{ limit = {{ {r('kind')} = 3 }}
    scope:tsin_fc_borrower ?= {{
     change_variable = {{ name = tsin_bond_principal add = tsin_contract_reference_principal }}
     if = {{ limit = {{ {r('maturity_mode')} = 2 }} change_variable = {{ name = tsin_unknown_legacy_maturities add = 1 }} set_variable = {{ name = tsin_unknown_maturity_contract_id value = scope:tsin_contract_id }} }}
     set_variable = {{ name = tsin_bond_arrears value = {{ value = var:tsin_bond_arrears min = {r('missed')} }} }}
    }}
   }}
  }}
 }}
}}
'''
    text=replace_block(text,'tsin_contract_refresh_effect',refresh)
    text=text.replace(' set_global_variable = { name = tsin_contract_review_month', ''' every_country = { limit = { has_variable = tsin_contract_managed }
  set_variable = { name = tsin_interest_paid value = 0 }
  set_variable = { name = tsin_bond_interest_paid value = 0 }
 }
 set_global_variable = { name = tsin_contract_review_month''',1)
    return text+'\n'+effects()


def effects():
    out=['''tsin_contract_migrate_private_effect = {
 if = { limit = { NOT = { has_variable = tsin_contract_managed } }
 save_scope_as = tsin_fc_lender save_scope_as = tsin_fc_borrower
 if = { limit = { var:tsin_firm_debt > 0 }
  tsin_contract_allocate_effect = yes
''',row(2,'var:tsin_firm_debt','var:tsin_rate','-1'),w('missed','var:tsin_arrears'),'''
 }
 if = { limit = { var:tsin_bond_principal > 0 }
  tsin_contract_allocate_effect = yes
''',row(3,'var:tsin_bond_principal','4','0','1'),w('missed','var:tsin_bond_arrears'),'''
 }
 set_variable = tsin_contract_managed
 }
}
tsin_contract_lend_facility_effect = {
 tsin_contract_migrate_legacy_effect = yes
 if = { limit = { tsin_bank_underwriting_allowed = yes tsin_firm_disclosure_allowed = yes var:tsin_bank_cash >= tsin_bank_lending_cash_required tsin_bank_net_worth >= 0 tsin_company_count > 0 }
 save_scope_as = tsin_fc_lender save_scope_as = tsin_fc_borrower
 tsin_contract_allocate_effect = yes
''',row(2,'tsin_ledger_lot','var:tsin_rate','-1'),'''
 change_variable = { name = tsin_bank_cash subtract = tsin_ledger_lot }
 change_variable = { name = tsin_firm_cash add = tsin_ledger_lot }
 }
 tsin_contract_refresh_effect = yes
}
tsin_contract_issue_bond_effect = {
 tsin_contract_migrate_legacy_effect = yes
 if = { limit = { tsin_firm_disclosure_allowed = yes var:tsin_bond_principal = 0 NOT = { has_variable = tsin_bond_issue_cooldown }
 any_estate = { estate_type = estate_type:burghers_estate estate_gold >= root.tsin_ledger_lot } }
 save_scope_as = tsin_fc_lender save_scope_as = tsin_fc_borrower
 tsin_contract_allocate_effect = yes
''',row(3,'tsin_ledger_lot','4','{ value = tsin_contract_calendar_month add = 36 }'),'''
 add_gold_to_estate = { estate_type = estate_type:burghers_estate value = { value = tsin_ledger_lot multiply = -1 } }
 change_variable = { name = tsin_firm_cash add = tsin_ledger_lot }
 set_variable = { name = tsin_bond_issue_cooldown years = 4 }
 }
 tsin_contract_refresh_effect = yes
}
''',f'''tsin_contract_adjust_private_effect = {{
 save_scope_as = tsin_fc_repay_actor save_scope_as = tsin_contract_coordinator
 save_temporary_scope_value_as = {{ name = tsin_fc_adjust_left value = $AMOUNT$ }}
 every_in_global_list = {{ variable = tsin_active_contracts add_to_list = tsin_fc_adjust_ids }}
 every_in_list = {{ list = tsin_fc_adjust_ids
 save_temporary_scope_value_as = {{ name = tsin_contract_id value = this }}
 scope:tsin_contract_coordinator = {{
 if = {{ limit = {{ {r('kind')} = $KIND$ {r('borrower')} ?= scope:tsin_fc_repay_actor scope:tsin_fc_adjust_left > 0 }}
 tsin_contract_bind_effect = yes
 save_temporary_scope_value_as = {{ name = tsin_fc_adjust_amount value = {{ value = scope:tsin_fc_adjust_left max = tsin_contract_reference_principal min = 0 }} }}
 if = {{ limit = {{ NOT = {{ always = $LOSS$ }} }}
  scope:tsin_fc_borrower = {{ change_variable = {{ name = tsin_firm_cash subtract = scope:tsin_fc_adjust_amount }} }}
  if = {{ limit = {{ {r('kind')} = 3 }} scope:tsin_fc_lender = {{ add_gold_to_estate = {{ estate_type = estate_type:burghers_estate value = scope:tsin_fc_adjust_amount }} }} }}
  else = {{ scope:tsin_fc_lender = {{ change_variable = {{ name = tsin_bank_cash add = scope:tsin_fc_adjust_amount }} }} }}
 }}
 else = {{
  if = {{ limit = {{ {r('kind')} = 3 }} scope:tsin_fc_borrower = {{ change_variable = {{ name = tsin_bond_losses add = scope:tsin_fc_adjust_amount }} }} }}
  else = {{ scope:tsin_fc_lender = {{ change_variable = {{ name = tsin_bank_losses add = scope:tsin_fc_adjust_amount }} }} }}
 }}
 {w('principal','{ value = '+r('principal')+' subtract = { value = scope:tsin_fc_adjust_amount multiply = '+r('fx')+' } min = 0 }')}
 save_temporary_scope_value_as = {{ name = tsin_fc_adjust_left value = {{ value = scope:tsin_fc_adjust_left subtract = scope:tsin_fc_adjust_amount min = 0 }} }}
 if = {{ limit = {{ {r('principal')} <= 0 }} tsin_contract_forget_effect = yes }}
 }}
 }}
 }}
 tsin_contract_refresh_effect = yes
}}
tsin_contract_repay_facility_effect = {{
 tsin_contract_adjust_private_effect = {{ KIND = 2 LOSS = no AMOUNT = tsin_ledger_repayment }}
}}
''']
    out += [f"""# Explicit repair only: caller must supply a verified original date.
tsin_contract_restore_legacy_maturity_effect = {{
 save_scope_as = tsin_fc_restore_actor
 save_temporary_scope_value_as = {{ name = tsin_contract_id value = $ID$ }}
 save_temporary_scope_value_as = {{ name = tsin_fc_restore_year value = $YEAR$ }}
 save_temporary_scope_value_as = {{ name = tsin_fc_restore_month value = $MONTH$ }}
 if = {{ limit = {{ {r('kind')} = 3 {r('maturity_mode')} = 2
 {r('borrower')} ?= scope:tsin_fc_restore_actor
 scope:tsin_fc_restore_year >= 1337 scope:tsin_fc_restore_year <= 2337
 scope:tsin_fc_restore_month >= 1 scope:tsin_fc_restore_month <= 12 }}
 {w('maturity','{ value = scope:tsin_fc_restore_year multiply = 12 add = scope:tsin_fc_restore_month }')}
 {w('maturity_mode','0')}
 tsin_contract_refresh_effect = yes
 }}
}}
"""]
    return '\n'.join(out)
