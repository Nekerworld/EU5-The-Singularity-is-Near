"""Funded pilot legal entities. Legacy pooled accounts and contracts remain separate."""
import pdx
FIELDS=('owner','kind','status','cash','units','public_units','claims','debt','missed','audit_until','audit_paid','losses','revenue')
LOAN_FIELDS=('lender','borrower','principal','rate','maturity','next_coupon','missed','status')
def r(field,ident='scope:tsin_le_id'):return f'"global_variable_map(tsin_le_{field}|{ident})"'
def w(field,value,ident='scope:tsin_le_id'):return f'add_to_global_variable_map = {{ name = tsin_le_{field} key = {ident} value = {value} }}'
def lr(field):return f'"global_variable_map(tsin_le_loan_{field}|scope:tsin_le_loan_id)"'
def lw(field,value):return f'add_to_global_variable_map = {{ name = tsin_le_loan_{field} key = scope:tsin_le_loan_id value = {value} }}'
VIEW=[('ID','선택 법인 ID','Selected legal entity ID','tsin_le_view_id'),('KIND','종류: 1 은행 / 2 기업','Kind: 1 bank / 2 company','tsin_le_view_kind'),('CASH','별도 법인 현금','Separate entity cash','tsin_le_view_cash'),('CLAIMS','별도 법인 대출자산','Entity loan receivables','tsin_le_view_claims'),('DEBT','별도 법인 원금채무','Entity principal debt','tsin_le_view_debt'),('NET','별도 법인 순자산','Entity net assets','tsin_le_view_net'),('PUBLIC','별도 법인 국가 지분(%)','Entity public equity (%)','tsin_le_view_public'),('MISSED','별도 법인 최장 연체 개월','Entity longest arrears (months)','tsin_le_view_missed'),('YEAR','법인 조회 기준 연도','Entity inspection year','tsin_le_view_year')]
def register(fields,action,loc):
 for key,ko,en,var in VIEW:fields.append(('ENTITY_'+key,en,ko,var));loc('ENTITY_'+key,en,ko)
 for kind,name in [(1,'bank'),(2,'company')]:
  for public in (False,True):
   cap='tsin_can_use_banking = yes'+(' tsin_company_count > 0' if kind==2 else '')
   funding='gold >= tsin_ledger_lot NOT = { has_policy = policy:tsin_laissez_faire_policy }' if public else 'any_estate = { estate_type = estate_type:burghers_estate estate_gold >= root.tsin_ledger_lot }'
   primary='tsin_le_primary_'+name
   gate=f'''{cap} {funding} OR = {{ NOT = {{ has_variable = {primary} }}
    NOT = {{ {r('owner','var:'+primary)} ?= root }} {r('status','var:'+primary)} != 1 }}'''
   action(f'entity_create_{name}_{"public" if public else "private"}',f'Charter a {"public" if public else "private"} pilot {name}',('국영' if public else '민간')+' 시범 '+('은행' if kind==1 else '기업')+' 법인 출자',gate,f'tsin_le_create_effect = {{ KIND = {kind} PUBLIC = {"yes" if public else "no"} PRIMARY = {primary} }}','BANK')
 action('entity_next','Inspect next owned legal entity','다음 보유 법인 조회','has_global_variable = tsin_le_next_id','tsin_le_inspect_next_effect = yes','BANK')
 action('entity_audit','Pay selected entity audit','선택 법인 유료 감사','tsin_le_selected_owned = yes tsin_le_selected_audit_allowed = yes','tsin_le_audit_effect = yes','BANK')
 action('entity_private_equity','Fund selected entity with private equity','선택 법인 민간 유상증자','tsin_le_selected_owned = yes any_estate = { estate_type = estate_type:burghers_estate estate_gold >= root.tsin_ledger_lot }','tsin_le_equity_effect = { PUBLIC = no }','BANK')
 action('entity_public_equity','Subscribe selected entity public equity','선택 법인 국고 유상증자','tsin_le_selected_owned = yes gold >= tsin_ledger_lot NOT = { has_policy = policy:tsin_laissez_faire_policy }','tsin_le_equity_effect = { PUBLIC = yes }','BANK')
 action('entity_contract','Place funded contract with selected company','선택 기업에 유상 계약 발주','tsin_le_selected_owned = yes '+r('kind','var:tsin_le_selected')+' = 2 gold >= tsin_ledger_lot NOT = { has_policy = policy:tsin_laissez_faire_policy }','tsin_le_paid_contract_effect = yes','BANK')
 action('entity_lend','Issue a 36-month pilot entity loan','시범 법인 간 36개월 대출','tsin_le_can_lend = yes','tsin_le_lend_effect = yes','BANK')
 action('entity_repay','Repay selected company principal','선택 기업 원금 상환','tsin_le_selected_owned = yes '+r('debt','var:tsin_le_selected')+' > 0 '+r('cash','var:tsin_le_selected')+' > 0','tsin_le_repay_selected_effect = yes','BANK')
 action('entity_liquidate','Liquidate insolvent selected company','선택 부실 기업 청산','tsin_le_selected_owned = yes '+r('kind','var:tsin_le_selected')+' = 2 '+r('missed','var:tsin_le_selected')+' >= 12 '+r('cash','var:tsin_le_selected')+' < '+r('debt','var:tsin_le_selected'),'tsin_le_liquidate_selected_effect = yes','BANK')
 loc('ENTITY_NOTE','Pilot legal entities hold newly paid-in cash under permanent IDs. They do not receive arbitrary shares of legacy pooled assets or debts and are excluded from the old firm-type counts. One active pilot bank and company can be chartered per country; inherited entities are preserved. Inspection is a dated snapshot. Equity subscription creates ownership; a paid public contract creates revenue, not government equity. Liquidation distributes available cash pro rata, writes off unpaid claims once and closes the company. These pilots are financial accounts, not autonomous production or full corporate simulation.',
 '시범 법인은 새로 납입한 현금을 영구 ID로 보관합니다. 기존 합산 자산·채무를 임의 배분하지 않으며 기존 기업 유형별 개수에 중복 합산하지 않습니다. 국가마다 가동 시범 은행·기업 한 곳씩 출자할 수 있고 합병으로 받은 법인은 보존합니다. 조회는 기준일의 스냅샷입니다. 유상증자는 지분을 만들지만 유상 공공계약은 기업 수입이며 국가 지분이 아닙니다. 청산은 가용 현금을 채권액에 비례해 지급하고 미지급 채권을 한 번 상각한 뒤 기업을 닫습니다. 이 법인은 재무 계정 시제품이며 자율 생산·완전한 기업 모형이 아닙니다.')

def build():
 selected='var:tsin_le_selected'
 triggers=f'''tsin_le_selected_owned = {{ has_variable = tsin_le_selected {r('owner',selected)} ?= root {r('status',selected)} = 1 }}
tsin_le_selected_audit_allowed = {{
 {r('audit_until',selected)} <= tsin_contract_calendar_month
 {r('cash',selected)} >= {{ value = {r('cash',selected)} add = {r('claims',selected)} multiply = 0.01 min = 0.01 }}
}}
tsin_le_can_lend = {{
 tsin_can_use_banking = yes has_variable = tsin_le_primary_bank has_variable = tsin_le_primary_company
 {r('owner','var:tsin_le_primary_bank')} ?= root {r('owner','var:tsin_le_primary_company')} ?= root
 {r('status','var:tsin_le_primary_bank')} = 1 {r('status','var:tsin_le_primary_company')} = 1
 {r('cash','var:tsin_le_primary_bank')} >= tsin_ledger_lot {r('missed','var:tsin_le_primary_company')} = 0
 {r('cash','var:tsin_le_primary_company')} >= {r('debt','var:tsin_le_primary_company')}
 OR = {{ NOT = {{ OR = {{ has_policy = policy:tsin_bank_prudential_policy has_policy = policy:tsin_bank_strict_policy }} }}
  {r('audit_until','var:tsin_le_primary_bank')} > tsin_contract_calendar_month }}
 OR = {{ NOT = {{ has_policy = policy:tsin_disclosure_audited_policy }}
  {r('audit_until','var:tsin_le_primary_company')} > tsin_contract_calendar_month }}
}}
'''
 e=['''# Global ID maps are authoritative; country variables only select and display.
tsin_le_create_effect = {
 # Called only inside the ledger action's funding, technology and ownership guards.
 if = { limit = { NOT = { has_global_variable = tsin_le_next_id } } set_global_variable = { name = tsin_le_next_id value = 0 } }
 set_global_variable = { name = tsin_le_next_id value = { value = global_var:tsin_le_next_id add = 1 } }
 save_temporary_scope_value_as = { name = tsin_le_id value = global_var:tsin_le_next_id }
 add_to_global_variable_list = { name = tsin_legal_entities target = scope:tsin_le_id }
 set_variable = { name = $PRIMARY$ value = scope:tsin_le_id }
 set_variable = { name = tsin_le_selected value = scope:tsin_le_id }
''',w('owner','this'),w('kind','$KIND$'),w('status','1'),w('cash','tsin_ledger_lot'),w('units','100')]
 for field in FIELDS:
  if field not in ('owner','kind','status','cash','units'):e.append(w(field,'0'))
 e += [f'''if = {{ limit = {{ always = $PUBLIC$ }}
 add_gold = {{ value = tsin_ledger_lot multiply = -1 }} {w('public_units','100')}
}} else = {{ add_gold_to_estate = {{ estate_type = estate_type:burghers_estate value = {{ value = tsin_ledger_lot multiply = -1 }} }} }}
tsin_le_inspect_selected_effect = yes
}}
tsin_le_refresh_totals_effect = {{
 save_scope_as = tsin_le_coordinator
 every_in_global_list = {{ variable = tsin_legal_entities
  save_temporary_scope_value_as = {{ name = tsin_le_id value = this }}
  scope:tsin_le_coordinator = {{ {w('claims','0')} {w('debt','0')} {w('missed','0')} }}
 }}
 every_in_global_list = {{ variable = tsin_active_entity_loans
  save_temporary_scope_value_as = {{ name = tsin_le_loan_id value = this }}
  scope:tsin_le_coordinator = {{
   save_temporary_scope_value_as = {{ name = tsin_le_lender value = {lr('lender')} }}
   save_temporary_scope_value_as = {{ name = tsin_le_borrower value = {lr('borrower')} }}
   {w('claims','{ value = '+r('claims','scope:tsin_le_lender')+' add = '+lr('principal')+' }','scope:tsin_le_lender')}
   {w('debt','{ value = '+r('debt','scope:tsin_le_borrower')+' add = '+lr('principal')+' }','scope:tsin_le_borrower')}
   {w('missed','{ value = '+r('missed','scope:tsin_le_borrower')+' min = '+lr('missed')+' }','scope:tsin_le_borrower')}
  }}
 }}
}}
tsin_le_lend_effect = {{
 if = {{ limit = {{ tsin_le_can_lend = yes }}
 if = {{ limit = {{ NOT = {{ has_global_variable = tsin_le_next_loan }} }} set_global_variable = {{ name = tsin_le_next_loan value = 0 }} }}
 set_global_variable = {{ name = tsin_le_next_loan value = {{ value = global_var:tsin_le_next_loan add = 1 }} }}
 save_temporary_scope_value_as = {{ name = tsin_le_loan_id value = global_var:tsin_le_next_loan }}
 add_to_global_variable_list = {{ name = tsin_active_entity_loans target = scope:tsin_le_loan_id }}
 {lw('lender','var:tsin_le_primary_bank')} {lw('borrower','var:tsin_le_primary_company')}
 {lw('principal','tsin_ledger_lot')} {lw('rate','var:tsin_rate')}
 {lw('maturity','{ value = tsin_contract_calendar_month add = 36 }')} {lw('next_coupon','{ value = tsin_contract_calendar_month add = 1 }')}
 {lw('missed','0')} {lw('status','1')}
 {w('cash','{ value = '+r('cash','var:tsin_le_primary_bank')+' subtract = tsin_ledger_lot }','var:tsin_le_primary_bank')}
 {w('cash','{ value = '+r('cash','var:tsin_le_primary_company')+' add = tsin_ledger_lot }','var:tsin_le_primary_company')}
 tsin_le_refresh_totals_effect = yes tsin_le_inspect_selected_effect = yes
 }}
}}
tsin_le_close_loan_if_paid_effect = {{
 if = {{ limit = {{ {lr('principal')} <= 0 }}
  {lw('status','2')}
  remove_list_global_variable = {{ name = tsin_active_entity_loans target = scope:tsin_le_loan_id }}
 }}
}}
tsin_le_pay_principal_effect = {{
 save_temporary_scope_value_as = {{ name = tsin_le_lender value = {lr('lender')} }}
 save_temporary_scope_value_as = {{ name = tsin_le_borrower value = {lr('borrower')} }}
 save_temporary_scope_value_as = {{ name = tsin_le_payment value = {{ value = {r('cash','scope:tsin_le_borrower')} max = {lr('principal')} min = 0 }} }}
 {w('cash','{ value = '+r('cash','scope:tsin_le_borrower')+' subtract = scope:tsin_le_payment }','scope:tsin_le_borrower')}
 {w('cash','{ value = '+r('cash','scope:tsin_le_lender')+' add = scope:tsin_le_payment }','scope:tsin_le_lender')}
 {lw('principal','{ value = '+lr('principal')+' subtract = scope:tsin_le_payment min = 0 }')}
 tsin_le_close_loan_if_paid_effect = yes
}}
tsin_le_month_effect = {{
 set_global_variable = {{ name = tsin_le_review_month value = tsin_contract_calendar_month }}
 save_scope_as = tsin_le_coordinator
 every_in_global_list = {{ variable = tsin_active_entity_loans add_to_list = tsin_le_month_loans }}
 every_in_list = {{ list = tsin_le_month_loans
  save_temporary_scope_value_as = {{ name = tsin_le_loan_id value = this }}
  scope:tsin_le_coordinator = {{
   save_temporary_scope_value_as = {{ name = tsin_le_lender value = {lr('lender')} }}
   save_temporary_scope_value_as = {{ name = tsin_le_borrower value = {lr('borrower')} }}
   if = {{ limit = {{ {lr('status')} = 1 tsin_contract_calendar_month >= {lr('next_coupon')}
    {r('owner','scope:tsin_le_lender')} ?= {{ num_locations > 0 }} {r('owner','scope:tsin_le_borrower')} ?= {{ num_locations > 0 }} }}
    save_temporary_scope_value_as = {{ name = tsin_le_due value = {{ value = {lr('principal')} multiply = {lr('rate')} divide = 1200 }} }}
    save_temporary_scope_value_as = {{ name = tsin_le_payment value = {{ value = scope:tsin_le_due max = {r('cash','scope:tsin_le_borrower')} min = 0 }} }}
    {w('cash','{ value = '+r('cash','scope:tsin_le_borrower')+' subtract = scope:tsin_le_payment }','scope:tsin_le_borrower')}
    {w('cash','{ value = '+r('cash','scope:tsin_le_lender')+' add = scope:tsin_le_payment }','scope:tsin_le_lender')}
    save_temporary_scope_value_as = {{ name = tsin_le_unpaid value = 0 }}
    if = {{ limit = {{ scope:tsin_le_payment < scope:tsin_le_due }} save_temporary_scope_value_as = {{ name = tsin_le_unpaid value = 1 }} }}
    if = {{ limit = {{ tsin_contract_calendar_month >= {lr('maturity')} }}
     if = {{ limit = {{ {lr('principal')} > {r('cash','scope:tsin_le_borrower')} }} save_temporary_scope_value_as = {{ name = tsin_le_unpaid value = 1 }} }}
     tsin_le_pay_principal_effect = yes
    }}
    if = {{ limit = {{ scope:tsin_le_unpaid = 1 }} {lw('missed','{ value = '+lr('missed')+' add = 1 }')} }}
    else = {{ {lw('missed','0')} }}
    {lw('next_coupon','{ value = tsin_contract_calendar_month add = 1 }')}
   }}
  }}
 }}
 tsin_le_refresh_totals_effect = yes
}}
tsin_le_repay_selected_effect = {{
 if = {{ limit = {{ tsin_le_selected_owned = yes }}
 save_scope_as = tsin_le_coordinator
 every_in_global_list = {{ variable = tsin_active_entity_loans add_to_list = tsin_le_repay_loans }}
 every_in_list = {{ list = tsin_le_repay_loans
  save_temporary_scope_value_as = {{ name = tsin_le_loan_id value = this }}
  scope:tsin_le_coordinator = {{ if = {{ limit = {{ {lr('borrower')} = var:tsin_le_selected }} tsin_le_pay_principal_effect = yes }} }}
 }}
 tsin_le_refresh_totals_effect = yes tsin_le_inspect_selected_effect = yes
 }}
}}
tsin_le_equity_effect = {{
 if = {{ limit = {{ tsin_le_selected_owned = yes }}
 save_temporary_scope_value_as = {{ name = tsin_le_id value = var:tsin_le_selected }}
 save_temporary_scope_value_as = {{ name = tsin_le_net value = {{ value = {r('cash')} add = {r('claims')} subtract = {r('debt')} }} }}
 if = {{ limit = {{ scope:tsin_le_net <= 0 }} {w('units','0')} {w('public_units','0')} save_temporary_scope_value_as = {{ name = tsin_le_new_units value = 100 }} }}
 else = {{ save_temporary_scope_value_as = {{ name = tsin_le_new_units value = {{ value = tsin_ledger_lot multiply = {r('units')} divide = scope:tsin_le_net }} }} }}
 if = {{ limit = {{ always = $PUBLIC$ }}
  add_gold = {{ value = tsin_ledger_lot multiply = -1 }}
  {w('public_units','{ value = '+r('public_units')+' add = scope:tsin_le_new_units }')}
 }} else = {{ add_gold_to_estate = {{ estate_type = estate_type:burghers_estate value = {{ value = tsin_ledger_lot multiply = -1 }} }} }}
 {w('units','{ value = '+r('units')+' add = scope:tsin_le_new_units }')}
 {w('cash','{ value = '+r('cash')+' add = tsin_ledger_lot }')}
 tsin_le_inspect_selected_effect = yes
 }}
}}
tsin_le_paid_contract_effect = {{
 if = {{ limit = {{ tsin_le_selected_owned = yes {r('kind',selected)} = 2 gold >= tsin_ledger_lot NOT = {{ has_policy = policy:tsin_laissez_faire_policy }} }}
  add_gold = {{ value = tsin_ledger_lot multiply = -1 }}
  {w('cash','{ value = '+r('cash',selected)+' add = tsin_ledger_lot }',selected)}
  {w('revenue','{ value = '+r('revenue',selected)+' add = tsin_ledger_lot }',selected)}
  tsin_le_inspect_selected_effect = yes
 }}
}}
tsin_le_audit_effect = {{
 if = {{ limit = {{ tsin_le_selected_owned = yes tsin_le_selected_audit_allowed = yes }}
 save_temporary_scope_value_as = {{ name = tsin_le_id value = var:tsin_le_selected }}
 save_temporary_scope_value_as = {{ name = tsin_le_fee value = {{ value = {r('cash')} add = {r('claims')} multiply = 0.01 min = 0.01 }} }}
 {w('cash','{ value = '+r('cash')+' subtract = scope:tsin_le_fee }')} {w('audit_paid','scope:tsin_le_fee')}
 {w('audit_until','{ value = tsin_contract_calendar_month add = 12 }')}
 tsin_le_inspect_selected_effect = yes
 }}
}}
''']
 e.append(f'''tsin_le_liquidate_selected_effect = {{
 if = {{ limit = {{ tsin_le_selected_owned = yes {r('kind',selected)} = 2 {r('missed',selected)} >= 12 {r('cash',selected)} < {r('debt',selected)} }}
 save_scope_as = tsin_le_coordinator
 save_temporary_scope_value_as = {{ name = tsin_le_estate_cash value = {r('cash',selected)} }}
 save_temporary_scope_value_as = {{ name = tsin_le_estate_debt value = {r('debt',selected)} }}
 every_in_global_list = {{ variable = tsin_active_entity_loans add_to_list = tsin_le_liquidation_loans }}
 every_in_list = {{ list = tsin_le_liquidation_loans
  save_temporary_scope_value_as = {{ name = tsin_le_loan_id value = this }}
  scope:tsin_le_coordinator = {{ if = {{ limit = {{ {lr('borrower')} = var:tsin_le_selected }}
   save_temporary_scope_value_as = {{ name = tsin_le_lender value = {lr('lender')} }}
   save_temporary_scope_value_as = {{ name = tsin_le_payment value = {{ value = scope:tsin_le_estate_cash multiply = {lr('principal')} divide = scope:tsin_le_estate_debt max = {r('cash',selected)} min = 0 }} }}
   {w('cash','{ value = '+r('cash',selected)+' subtract = scope:tsin_le_payment }',selected)}
   {w('cash','{ value = '+r('cash','scope:tsin_le_lender')+' add = scope:tsin_le_payment }','scope:tsin_le_lender')}
   {w('losses','{ value = '+r('losses','scope:tsin_le_lender')+' add = { value = '+lr('principal')+' subtract = scope:tsin_le_payment min = 0 } }','scope:tsin_le_lender')}
   {lw('principal','0')} {lw('status','3')}
   remove_list_global_variable = {{ name = tsin_active_entity_loans target = scope:tsin_le_loan_id }}
  }} }}
 }}
 {w('status','2',selected)}
 tsin_le_refresh_totals_effect = yes tsin_le_inspect_selected_effect = yes
 }}
}}
tsin_le_inspect_selected_effect = {{
 if = {{ limit = {{ has_variable = tsin_le_selected {r('owner',selected)} ?= root }}
 save_temporary_scope_value_as = {{ name = tsin_le_id value = var:tsin_le_selected }}
''')
 for field in ('id','kind','cash','claims','debt','missed'):
  val='scope:tsin_le_id' if field=='id' else r(field)
  e.append(f'set_variable = {{ name = tsin_le_view_{field} value = {val} }}')
 e += [f'''set_variable = {{ name = tsin_le_view_net value = {{ value = {r('cash')} add = {r('claims')} subtract = {r('debt')} }} }}
set_variable = {{ name = tsin_le_view_public value = {{ value = {r('public_units')} divide = {{ value = {r('units')} min = 1 }} multiply = 100 }} }}
set_variable = {{ name = tsin_le_view_year value = current_year }}
 }}
}}
tsin_le_inspect_next_effect = {{
 save_scope_as = tsin_le_coordinator
 set_variable = {{ name = tsin_le_next_selected value = 0 }}
 every_in_global_list = {{ variable = tsin_legal_entities
  save_temporary_scope_value_as = {{ name = tsin_le_id value = this }}
  scope:tsin_le_coordinator = {{ if = {{ limit = {{ {r('owner')} ?= root
   OR = {{ NOT = {{ has_variable = tsin_le_selected }} scope:tsin_le_id > var:tsin_le_selected }}
   OR = {{ var:tsin_le_next_selected = 0 scope:tsin_le_id < var:tsin_le_next_selected }} }}
   set_variable = {{ name = tsin_le_next_selected value = scope:tsin_le_id }}
  }} }}
 }}
 if = {{ limit = {{ var:tsin_le_next_selected = 0 }}
  every_in_global_list = {{ variable = tsin_legal_entities
   save_temporary_scope_value_as = {{ name = tsin_le_id value = this }}
   scope:tsin_le_coordinator = {{ if = {{ limit = {{ {r('owner')} ?= root OR = {{ var:tsin_le_next_selected = 0 scope:tsin_le_id < var:tsin_le_next_selected }} }}
    set_variable = {{ name = tsin_le_next_selected value = scope:tsin_le_id }}
   }} }}
  }}
 }}
 if = {{ limit = {{ var:tsin_le_next_selected > 0 }} set_variable = {{ name = tsin_le_selected value = var:tsin_le_next_selected }} tsin_le_inspect_selected_effect = yes }}
}}
tsin_le_succession_effect = {{
 # Called inside the existing annex commit before the journal is cleared. No cash copy.
 save_scope_as = tsin_le_coordinator
 every_in_global_list = {{ variable = tsin_legal_entities
  save_temporary_scope_value_as = {{ name = tsin_le_id value = this }}
  scope:tsin_le_coordinator = {{ if = {{ limit = {{ {r('owner')} ?= scope:tsin_annex_target }}
   {w('owner','scope:tsin_annex_recipient')}
   if = {{ limit = {{ {r('status')} = 1 {r('kind')} = 1 NOT = {{ has_variable = tsin_le_primary_bank }} }} set_variable = {{ name = tsin_le_primary_bank value = scope:tsin_le_id }} }}
   if = {{ limit = {{ {r('status')} = 1 {r('kind')} = 2 NOT = {{ has_variable = tsin_le_primary_company }} }} set_variable = {{ name = tsin_le_primary_company value = scope:tsin_le_id }} }}
  }} }}
 }}
}}
''']
 hooks='''monthly_country_pulse = { on_actions = { tsin_le_global_monthly } }
tsin_le_global_monthly = {
 trigger = { has_global_variable = tsin_le_next_id OR = { NOT = { has_global_variable = tsin_le_review_month } tsin_contract_calendar_month > global_var:tsin_le_review_month } }
 effect = { tsin_le_month_effect = yes }
}
'''
 effects='\n'.join(e)+'\n'
 funding='''OR = {
 AND = { always = $PUBLIC$ gold >= tsin_ledger_lot NOT = { has_policy = policy:tsin_laissez_faire_policy } }
 AND = { NOT = { always = $PUBLIC$ } any_estate = { estate_type = estate_type:burghers_estate estate_gold >= root.tsin_ledger_lot } }
}'''
 # Recheck the actual funding source before any counter, map or share write.
 for name in ('tsin_le_create_effect','tsin_le_equity_effect'):
  b=next(b for b in pdx.top_level_blocks(effects) if b.key==name)
  body=b.text[b.text.index('{')+1:-1]
  effects=effects.replace(b.text,name+' = {\n if = { limit = { '+funding+' }\n'+body+'\n }\n}',1)
 return {'in_game/common/scripted_effects/tsin_legal_entities.txt':effects.rstrip()+'\n','in_game/common/scripted_triggers/tsin_legal_entities.txt':triggers,'in_game/common/on_action/tsin_legal_entities.txt':hooks}
