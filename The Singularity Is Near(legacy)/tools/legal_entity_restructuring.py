"""Paid secondary equity acquisition and domestic wholly-public company reorganization."""
def r(*args):
 from legal_entities import r as read
 return read(*args)
def w(*args):
 from legal_entities import w as write
 return write(*args)
def lr(*args):
 from legal_entities import lr as read
 return read(*args)
def lw(*args):
 from legal_entities import lw as write
 return write(*args)
FIELDS=[('STATUS','Status: 1 active / 2 liquidated / 3 merged','상태: 1 가동 / 2 청산 / 3 합병','tsin_le_view_status'),('MERGED','Surviving entity ID','합병 후 존속 법인 ID','tsin_le_view_merged_into'),('LOSSES','Entity creditor write-offs','법인 채권 상각 손실','tsin_le_view_losses'),('AUDIT_LEFT','Entity audit months remaining','법인 감사 잔여 개월','tsin_le_view_audit_left')]
def register(action,loc):
 s='var:tsin_le_selected';p='var:tsin_le_primary_company'
 net='{ value = '+r('cash',s)+' add = '+r('claims',s)+' subtract = '+r('debt',s)+' }'
 price='{ value = '+net+' multiply = { value = 1 subtract = { value = '+r('public_units',s)+' divide = { value = '+r('units',s)+' min = 1 } } min = 0 max = 1 } }'
 buy=f'''tsin_le_selected_owned = yes tsin_can_use_capital_markets = yes
 NOT = {{ has_policy = policy:tsin_laissez_faire_policy }} country_has_estate = estate_type:burghers_estate
 {r('units',s)} > 0 {r('public_units',s)} < {r('units',s)}
 {r('cash',s)} >= {{ value = {r('debt',s)} subtract = {r('claims',s)} add = 0.01 }}
 gold >= {price}'''
 merge=f'''tsin_le_selected_owned = yes tsin_can_use_capital_markets = yes
 has_variable = tsin_le_primary_company var:tsin_le_selected != var:tsin_le_primary_company
 NOT = {{ has_policy = policy:tsin_laissez_faire_policy }} NOT = {{ has_variable = tsin_le_merger_cooldown }}
 {r('kind',s)} = 2 {r('kind',p)} = 2 {r('status',p)} = 1 {r('owner',p)} ?= root
 {r('merger_phase',s)} = 0
 {r('units',s)} > 0 {r('units',p)} > 0
 {r('public_units',s)} >= {r('units',s)} {r('public_units',p)} >= {r('units',p)}
 gold >= {{ value = tsin_ledger_lot multiply = 0.05 min = 0.01 }}'''
 action('entity_buyout','Buy remaining private equity at book NAV','선택 법인 민간 지분 유상 매입',buy,'tsin_le_buyout_effect = yes','BANK')
 action('entity_merge','Merge public company into primary company','완전 국영 기업을 기본 기업에 통합',merge,'tsin_le_merge_effect = yes','BANK')
 close=f'''tsin_le_selected_owned = yes {r('claims',s)} = 0 {r('debt',s)} = 0
 OR = {{ {r('public_units',s)} >= {r('units',s)} country_has_estate = estate_type:burghers_estate }}'''
 action('entity_close','Close debt-free entity and return remaining capital','무채무 법인 종료·잔여 현금 반환',close,'tsin_le_close_solvent_effect = yes','BANK')
 # R08: liquidity (arrears) but positive net assets only. Loan IDs are kept; principal is not written down here.
 restructure=f'''tsin_le_selected_owned = yes {r('kind',s)} = 2 {r('missed',s)} >= 1 {r('debt',s)} < {{ value = {r('cash',s)} add = {r('claims',s)} }} NOT = {{ has_policy = policy:tsin_laissez_faire_policy }}'''
 action('entity_restructure','Restructure arrears loans of selected company (IDs kept, maturity +24 months, rate halved)','선택 기업 연체 대출 재조정 (ID 유지, 만기 +24개월, 금리 절반)',restructure,'tsin_le_restructure_loans_effect = yes','BANK')
 # R08: secured by verified loan receivables the company holds; 50% of the receivables, capped by primary bank cash.
 bank='var:tsin_le_primary_bank'
 emergency=f'''tsin_le_selected_owned = yes {r('kind',s)} = 2 {r('missed',s)} >= 1 {r('claims',s)} >= 0.02 has_variable = tsin_le_primary_bank {r('owner',bank)} ?= root {r('cash',bank)} >= 0.01 NOT = {{ has_policy = policy:tsin_laissez_faire_policy }} {r('debt',s)} < {{ value = {r('cash',s)} add = {r('claims',s)} }}'''
 action('entity_emergency_loan','Emergency loan secured by verified loan receivables (50% of receivables)','대출채권 담보 긴급대출 (채권의 50%, 은행 현금 한도)',emergency,'tsin_le_emergency_loan_effect = yes','BANK')
 loc('ENTITY_RESTRUCTURE_NOTE','Buying existing private equity pays burgher owners at positive book NAV; it adds no company cash and is not a recapitalization. Merger is limited to two wholly state-owned companies in the same country, costs 5% of one transaction lot (minimum 0.01), preserves every loan ID/rate/maturity and closes the absorbed ID. It neither transfers factories nor merges private owners without compensation. A merge marker prevents repeated processing; engine-wide rollback is not guaranteed.',
 '기존 민간 지분의 유상 매입은 양의 장부 순자산 기준으로 시민 소유주에게 지급하며 회사 현금을 늘리지 않습니다. 통합은 같은 나라의 완전 국영 기업끼리만 가능하며 거래 단위의 5%(최소0.01두캇)를 지불합니다. 모든 대출 ID·금리·만기를 보존하고 흡수 법인 ID를 닫습니다. 실제 공장을 옮기거나 민간 소유주를 무상 합병하지 않습니다. 처리 표식으로 중복을 막지만 엔진 전체의 원자적 롤백을 보장하지 않습니다.')
 return buy,merge,close
def extend_outputs(outputs):
 gates=[]
 register(lambda ident,en,ko,gate,effect,tab:gates.append(gate),lambda *args:None)
 buy,merge,close,restructure,emergency=gates;s='var:tsin_le_selected';p='var:tsin_le_primary_company';bank='var:tsin_le_primary_bank'
 e2=f'''tsin_le_restructure_loans_effect = {{
 if = {{ limit = {{ {restructure} }}
 save_scope_as = tsin_le_coordinator
 every_in_global_list = {{ variable = tsin_active_entity_loans add_to_list = tsin_le_restructure_list }}
 every_in_list = {{ list = tsin_le_restructure_list
  save_temporary_scope_value_as = {{ name = tsin_le_loan_id value = this }}
  scope:tsin_le_coordinator = {{ if = {{ limit = {{ {lr('borrower')} = var:tsin_le_selected {lr('status')} = 1 }}
   {lw('maturity','{ value = '+lr('maturity')+' add = 24 }')}
   {lw('rate','{ value = '+lr('rate')+' multiply = 0.5 min = 0 }')}
   {lw('missed','0')}
  }} }}
 }}
 tsin_le_refresh_totals_effect = yes tsin_le_inspect_selected_effect = yes
 }}
}}
tsin_le_emergency_loan_effect = {{
 if = {{ limit = {{ {emergency} }}
 save_temporary_scope_value_as = {{ name = tsin_le_emergency_amount value = {{ value = {r('claims',s)} multiply = 0.5 max = {r('cash',bank)} }} }}
 if = {{ limit = {{ scope:tsin_le_emergency_amount >= 0.01 }}
  if = {{ limit = {{ NOT = {{ has_global_variable = tsin_le_next_loan }} }} set_global_variable = {{ name = tsin_le_next_loan value = 0 }} }}
  set_global_variable = {{ name = tsin_le_next_loan value = {{ value = global_var:tsin_le_next_loan add = 1 }} }}
  save_temporary_scope_value_as = {{ name = tsin_le_loan_id value = global_var:tsin_le_next_loan }}
  add_to_global_variable_list = {{ name = tsin_active_entity_loans target = scope:tsin_le_loan_id }}
  {lw('lender',bank)} {lw('borrower',s)}
  {lw('principal','scope:tsin_le_emergency_amount')} {lw('rate','var:tsin_rate')}
  {lw('maturity','{ value = tsin_contract_calendar_month add = 12 }')} {lw('next_coupon','{ value = tsin_contract_calendar_month add = 1 }')}
  {lw('missed','0')} {lw('status','1')}
  {w('cash','{ value = '+r('cash',bank)+' subtract = scope:tsin_le_emergency_amount }',bank)}
  {w('cash','{ value = '+r('cash',s)+' add = scope:tsin_le_emergency_amount }',s)}
  tsin_le_refresh_totals_effect = yes tsin_le_inspect_selected_effect = yes
 }}
 }}
}}
'''
 s='var:tsin_le_selected';p='var:tsin_le_primary_company'
 e=f'''tsin_le_buyout_effect = {{
 if = {{ limit = {{ {buy} }}
 save_temporary_scope_value_as = {{ name = tsin_le_buyout_price value = {{ value = {r('cash',s)} add = {r('claims',s)} subtract = {r('debt',s)} multiply = {{ value = 1 subtract = {{ value = {r('public_units',s)} divide = {r('units',s)} }} min = 0 max = 1 }} }} }}
 add_gold = {{ value = scope:tsin_le_buyout_price multiply = -1 }}
 add_gold_to_estate = {{ estate_type = estate_type:burghers_estate value = scope:tsin_le_buyout_price }}
 {w('public_units',r('units',s),s)}
 tsin_le_inspect_selected_effect = yes
 }}
}}
tsin_le_merge_effect = {{
 if = {{ limit = {{ {merge} }}
 # One synchronous reorganization; retain the absorbed ID as a closed audit record.
 {w('merger_source_cash',r('cash',s),s)} {w('merger_survivor_cash',r('cash',p),s)}
 {w('merger_source_units',r('units',s),s)} {w('merger_survivor_units',r('units',p),s)}
 {w('merged_into',p,s)} {w('merger_phase','1',s)}
 add_gold = {{ value = tsin_ledger_lot multiply = -0.05 max = -0.01 }}
 {w('cash','{ value = '+r('cash',p)+' add = '+r('cash',s)+' }',p)}
 {w('cash','0',s)}
 {w('units','{ value = '+r('units',p)+' add = '+r('units',s)+' }',p)}
 {w('public_units',r('units',p),p)}
 {w('units','0',s)} {w('public_units','0',s)}
 {w('merger_phase','2',s)}
 save_scope_as = tsin_le_coordinator
 every_in_global_list = {{ variable = tsin_active_entity_loans
  save_temporary_scope_value_as = {{ name = tsin_le_loan_id value = this }}
  scope:tsin_le_coordinator = {{
   if = {{ limit = {{ {lr('borrower')} = var:tsin_le_selected }} {lw('borrower',p)} }}
   if = {{ limit = {{ {lr('lender')} = var:tsin_le_selected }} {lw('lender',p)} }}
  }}
 }}
 {w('status','3',s)} {w('merger_phase','3',s)}
 set_variable = {{ name = tsin_le_merger_cooldown months = 12 }}
 tsin_le_refresh_totals_effect = yes tsin_le_inspect_selected_effect = yes
 }}
}}
tsin_le_close_solvent_effect = {{
 if = {{ limit = {{ {close} }}
  save_temporary_scope_value_as = {{ name = tsin_le_closing_cash value = {r('cash',s)} }}
  save_temporary_scope_value_as = {{ name = tsin_le_closing_public value = {{ value = scope:tsin_le_closing_cash multiply = {r('public_units',s)} divide = {{ value = {r('units',s)} min = 1 }} min = 0 max = scope:tsin_le_closing_cash }} }}
  {w('cash','0',s)} {w('status','2',s)}
  add_gold = scope:tsin_le_closing_public
  if = {{ limit = {{ scope:tsin_le_closing_cash > scope:tsin_le_closing_public }}
   add_gold_to_estate = {{ estate_type = estate_type:burghers_estate value = {{ value = scope:tsin_le_closing_cash subtract = scope:tsin_le_closing_public }} }}
  }}
  {w('units','0',s)} {w('public_units','0',s)}
  tsin_le_inspect_selected_effect = yes
 }}
}}
'''
 outputs=dict(outputs)
 outputs['in_game/common/scripted_effects/tsin_legal_entities.txt']+=e.rstrip()+'\n'+e2.rstrip()+'\n'
 return outputs
