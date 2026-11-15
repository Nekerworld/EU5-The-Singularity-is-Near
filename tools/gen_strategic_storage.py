"""Zero-job state storage: physical market transactions, bounded monthly registered-site service."""
from pathlib import Path
import sys,argparse,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx
GOODS=[(1,'tsin_oil','석유','Oil','tsin_oil_storage','tsin_oil_refining_advance'),(2,'coal','석탄','Coal','tsin_strategic_storage','tsin_industrial_capitalism_advance'),(3,'steel','강철','Steel','tsin_strategic_storage','tsin_industrial_capitalism_advance')]

def registry_module():
    return {'id':'strategic_storage','shortcuts':[{'id':'storage_'+k,'tab':'economy','title':{'korean':ko,'english':en},'generic_action':'tsin_storage_'+k} for k,ko,en in [('oil','석유 비축 자동운전 설정','Configure oil reserve'),('coal','석탄 비축 자동운전 설정','Configure coal reserve'),('steel','강철 비축 자동운전 설정','Configure steel reserve'),('pause','저장고 자동운전 정지','Pause reserve automation'),('resume','저장고 자동운전 재개','Resume reserve automation'),('release','저장고 비상 방출 예약','Request emergency release'),('inspect','선택 저장고 조사','Inspect reserve site')]],'metrics':[{'id':'storage_report_'+key,'variable':'tsin_storage_report_'+key,'title':{'korean':ko,'english':en},'tabs':['economy'],'unit':'number','frequency':'manual','description':{'korean':'저장고 조사 버튼으로 선택한 지점의 마지막 상태를 읽습니다. 종류 1=석유, 2=석탄, 3=강철. 상태 0=대기, 1=매입, 2=매도, 9=정지, 99=검사 실패입니다.','english':'Snapshot of the site selected with Inspect. Kind 1=oil, 2=coal, 3=steel. State 0=idle, 1=buy, 2=sell, 9=paused, 99=verification failed.'}} for key,ko,en in [('amount','선택 저장고 수량','Inspected reserve quantity'),('capacity','선택 저장고 용량','Inspected reserve capacity'),('kind','선택 저장고 재화 종류','Inspected reserve good'),('state','선택 저장고 운영 상태','Inspected reserve state'),('year','저장고 조사 연도','Reserve survey year'),('month','저장고 조사 월','Reserve survey month')]]}

def selector(gate):return ''' select_trigger = {
 looking_for_a = location source = actor target_flag = target_location name = "choose_location"
 column = { data = name }
 visible = { owner ?= scope:actor '''+gate+''' }
 enabled = { controller ?= scope:actor }
 }
'''

def build():
    buildings=[];actions=[];labels={}
    for key,ko,en,advance in [('tsin_oil_storage','석유 저장고','Oil reserve tanks','tsin_oil_refining_advance'),('tsin_strategic_storage','전략자원 비축고','Strategic reserve depot','tsin_industrial_capitalism_advance')]:
        buildings.append(f'''{key} = {{
 audio_tier = 2 is_foreign = no forbidden_for_estates = yes pop_type = laborers
 employment_size = 0 max_levels = 3 always_add_demands = yes
 category = infrastructure_category
 town = yes city = yes megalopolis = yes tsin_large_city = yes tsin_megalopolis = yes
 build_time = infrastructure_build_time construction_demand = tsin_infrastructure_construction
 country_potential = {{ has_advance = {advance} }}
 location_potential = {{ is_market_center = yes }}
 unique_production_methods = {{
  {key}_maintenance = {{
   icon_type = goods icon = tools tools = 0.02 category = building_maintenance
  }}
 }}
}}
''')
        labels[key]=(ko,en);labels[key+'_maintenance']=(ko+' 유지',en+' maintenance')
        labels[key+'_desc']=('고용 0. 단계당 저장 용량 100, 월 최대 10을 실제 시장에서 입출고합니다. 관리 창에서 재화와 자동운전을 설정해야 합니다. 저장 재화는 일반 생산 방식으로 복제하지 않습니다.','Zero jobs. Capacity 100 per level; physical transactions up to 10 per month. Configure a good and automation in TSIN management. No commodity production method duplicates reserves.')
    for kind,good,ko,en,building,advance in GOODS:
        gate=f'has_building_with_at_least_one_level = {building} OR = {{ NOT = {{ has_variable = tsin_storage_amount }} var:tsin_storage_amount = 0 }} NOT = {{ has_variable = tsin_storage_error }}'
        effect=f'''scope:target_location = {{
 if = {{ limit = {{ owner ?= scope:actor controller ?= scope:actor {gate} scope:actor = {{ has_advance = {advance} }} }}
 if = {{ limit = {{ NOT = {{ has_variable = tsin_storage_registered }} }}
  add_to_global_variable_list = {{ name = tsin_storage_sites target = this }}
  set_variable = tsin_storage_registered
 }}
 set_variable = {{ name = tsin_storage_kind value = {kind} }}
 set_variable = {{ name = tsin_storage_amount value = 0 }}
 set_variable = {{ name = tsin_storage_state value = 0 }}
 set_variable = tsin_storage_active
}}
}}
set_global_variable = tsin_storage_enabled'''
        actions.append(f'''tsin_storage_{en.lower()} = {{
 type = owncountry price = price:tsin_storage_control_price show_message = no
 ai_tick = never automation_tick = never
 potential = {{ scope:actor = {{ has_advance = {advance} }} }}
'''+selector(gate)+f' effect = {{ {effect} }}\n}}\n')
        labels['tsin_storage_'+en.lower()]=(ko+' 비축 자동운전 설정','Configure '+en.lower()+' reserve automation')
    controls={'pause':'''remove_variable = tsin_storage_active set_variable = { name = tsin_storage_state value = 9 }''','resume':'''if = { limit = { NOT = { has_variable = tsin_storage_error } } set_variable = tsin_storage_active set_variable = { name = tsin_storage_state value = 0 } }''','release':'''if = { limit = { NOT = { has_variable = tsin_storage_error } } set_variable = tsin_storage_emergency set_variable = tsin_storage_active }''','inspect':'''owner = {
 set_variable = { name = tsin_storage_report_amount value = scope:target_location.var:tsin_storage_amount }
 set_variable = { name = tsin_storage_report_capacity value = scope:target_location.tsin_storage_capacity }
 set_variable = { name = tsin_storage_report_kind value = scope:target_location.var:tsin_storage_kind }
 set_variable = { name = tsin_storage_report_state value = scope:target_location.var:tsin_storage_state }
 set_variable = { name = tsin_storage_report_year value = current_year }
 set_variable = { name = tsin_storage_report_month value = current_month }
}'''}
    for key,body in controls.items():
        actions.append('tsin_storage_'+key+' = { type = owncountry price = price:tsin_storage_control_price show_message = no ai_tick = never automation_tick = never\n'+selector('has_variable = tsin_storage_registered')+' effect = { scope:target_location = { if = { limit = { owner ?= scope:actor controller ?= scope:actor } '+body+' } } }\n}\n')
    for key,ko,en in [('pause','停止 비축 자동운전','Pause reserve automation'),('resume','비축 자동운전 재개','Resume reserve automation'),('release','비상 방출 예약','Schedule emergency release'),('inspect','선택 저장고 조사','Inspect selected reserve')]:labels['tsin_storage_'+key]=(ko.replace('停止','정지'),en)
    for key in [k for k in labels if k.startswith('tsin_storage_')]:labels[key+'_desc']=('정부 관리 저장고의 운전을 설정합니다. 기준가 85% 이하 매입, 115% 이상 방출, 중간에는 대기합니다. 월 10·국고의 5% 이내 매입, 최소 비축 25%를 유지합니다. 비상 방출은 하한을 무시해 다음 월에 1회 처리합니다. 검사 실패 후에는 자동운전을 재개할 수 없습니다.','Configure a government reserve. Buy below 85% of base price, sell above 115%, otherwise wait. Buy up to 10/month and 5% of treasury; retain 25% capacity. Emergency releases bypass the floor once next month. Verification failures lock automation.')
    capacity='''tsin_storage_capacity = { value = 0
 if = { limit = { var:tsin_storage_kind = 1 } value = "location_building_level(building_type:tsin_oil_storage)" }
 else_if = { limit = { OR = { var:tsin_storage_kind = 2 var:tsin_storage_kind = 3 } } value = "location_building_level(building_type:tsin_strategic_storage)" }
 multiply = 100
}
'''
    effects='''# Native buy/sell effects charge/credit gold themselves. Never debit the purchase a second time.
tsin_storage_review_effect = {
 set_global_variable = { name = tsin_storage_review_month value = tsin_urban_calendar_month }
 clear_list = tsin_storage_review_sites
 every_in_global_list = { variable = tsin_storage_sites add_to_list = tsin_storage_review_sites }
 every_in_list = { list = tsin_storage_review_sites
  if = { limit = { has_owner = yes controller ?= owner has_variable = tsin_storage_active NOT = { has_variable = tsin_storage_error } owner = { exists = capital } }
   save_scope_as = tsin_storage_site
   owner = { save_scope_as = tsin_storage_operator }
   tsin_storage_site_tick_effect = yes
  }
 }
 clear_list = tsin_storage_review_sites
}
tsin_storage_site_tick_effect = {
'''
    for kind,good,ko,en,building,advance in GOODS:
        # Static goods references avoid unsupported dynamic commodity parameters.
        price=f'"market.market_price(goods:{good})"';base=f'"market.default_price(goods:{good})"';stock=f'"market.stockpile_in_market(goods:{good})"'
        effects+=f''' if = {{ limit = {{ var:tsin_storage_kind = {kind} exists = market {base} > 0 }}
  set_local_variable = {{ name = tsin_storage_ratio value = {{ value = {price} divide = {base} }} }}
  set_local_variable = {{ name = tsin_storage_before value = {stock} }}
  if = {{ limit = {{
   tsin_storage_capacity > var:tsin_storage_amount
   OR = {{ local_var:tsin_storage_ratio <= 0.85 AND = {{ var:tsin_storage_state = 1 local_var:tsin_storage_ratio < 0.95 }} }}
   NOT = {{ has_variable = tsin_storage_emergency }}
   {price} > 0 {stock} > 0
  }}
   set_local_variable = {{ name = tsin_storage_quantity value = {{ value = tsin_storage_capacity subtract = var:tsin_storage_amount max = 10 max = {stock} max = {{ value = owner.gold multiply = 0.05 divide = {price} }} min = 0 }} }}
   if = {{ limit = {{ local_var:tsin_storage_quantity > 0 }}
    scope:tsin_storage_operator = {{ buy_goods_from_market = {{ market = scope:tsin_storage_site.market goods = goods:{good} amount = local_var:tsin_storage_quantity }} }}
    set_local_variable = {{ name = tsin_storage_observed value = {{ value = local_var:tsin_storage_before subtract = {stock} min = 0 }} }}
    change_variable = {{ name = tsin_storage_amount add = {{ value = local_var:tsin_storage_observed max = local_var:tsin_storage_quantity }} }}
    set_variable = {{ name = tsin_storage_state value = 1 }}
    tsin_storage_verify_effect = yes
   }}
  }}
  else_if = {{ limit = {{ var:tsin_storage_amount > 0
   OR = {{ has_variable = tsin_storage_emergency local_var:tsin_storage_ratio >= 1.15 AND = {{ var:tsin_storage_state = 2 local_var:tsin_storage_ratio > 1.05 }} }}
  }}
   set_local_variable = {{ name = tsin_storage_floor value = {{ value = tsin_storage_capacity multiply = 0.25 }} }}
   if = {{ limit = {{ has_variable = tsin_storage_emergency }} set_local_variable = {{ name = tsin_storage_floor value = 0 }} }}
   set_local_variable = {{ name = tsin_storage_quantity value = {{ value = var:tsin_storage_amount subtract = local_var:tsin_storage_floor min = 0 max = 10 }} }}
   if = {{ limit = {{ local_var:tsin_storage_quantity > 0 }}
    # Reserve the quantity before execution; a failed verification cannot sell it twice.
    change_variable = {{ name = tsin_storage_amount subtract = local_var:tsin_storage_quantity }}
    scope:tsin_storage_operator = {{ sell_goods_to_market = {{ market = scope:tsin_storage_site.market goods = goods:{good} amount = local_var:tsin_storage_quantity }} }}
    set_local_variable = {{ name = tsin_storage_observed value = {{ value = {stock} subtract = local_var:tsin_storage_before min = 0 }} }}
    set_variable = {{ name = tsin_storage_state value = 2 }}
    tsin_storage_verify_effect = yes
   }}
   remove_variable = tsin_storage_emergency
  }}
  else = {{ set_variable = {{ name = tsin_storage_state value = 0 }} }}
 }}
'''
    effects+='''}
tsin_storage_verify_effect = {
 # These two values preserve the unresolved transaction for manual diagnosis.
 if = { limit = { OR = {
  local_var:tsin_storage_observed < { value = local_var:tsin_storage_quantity subtract = 0.01 }
  local_var:tsin_storage_observed > { value = local_var:tsin_storage_quantity add = 0.01 }
 } }
  set_variable = tsin_storage_error
  set_variable = { name = tsin_storage_error_requested value = local_var:tsin_storage_quantity }
  set_variable = { name = tsin_storage_error_observed value = local_var:tsin_storage_observed }
  remove_variable = tsin_storage_active
  set_variable = { name = tsin_storage_state value = 99 }
 }
}
'''
    outputs={'in_game/common/building_types/tsin_strategic_storage.txt':'\n'.join(buildings),'in_game/common/generic_actions/tsin_strategic_storage.txt':'\n'.join(actions),'in_game/common/script_values/tsin_strategic_storage.txt':capacity,'in_game/common/scripted_effects/tsin_strategic_storage.txt':effects,'in_game/common/prices/tsin_strategic_storage.txt':'tsin_storage_control_price = { gold = 0 }\n','in_game/common/on_action/tsin_strategic_storage.txt':'''monthly_country_pulse = { on_actions = { tsin_storage_monthly_service } }
tsin_storage_monthly_service = {
 trigger = { has_global_variable = tsin_storage_enabled
  OR = { NOT = { has_global_variable = tsin_storage_review_month } tsin_urban_calendar_month > global_var:tsin_storage_review_month }
 }
 effect = { tsin_storage_review_effect = yes }
}
'''}
    for lang,i in [('korean',0),('english',1)]:outputs[f'main_menu/localization/{lang}/tsin_strategic_storage_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {k}: '+json.dumps(v[i],ensure_ascii=False)+'\n' for k,v in labels.items())
    return outputs

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();bad=[]
    for rel,text in build().items():
        p=pdx.MOD_ROOT/rel
        if a.check:
            if not p.exists() or pdx.read_text(p)!=text:bad.append(rel)
        else:
            if rel=='in_game/common/building_types/tsin_strategic_storage.txt' and pdx.content_path(p)==p and not p.exists():
                source=pdx.MOD_ROOT/'era_7'/rel;source.parent.mkdir(parents=True,exist_ok=True);source.write_text(text,encoding='utf-8-sig')
            else:pdx.write_text_bom(p,text)
    if not a.check:
        import sync_eras,era_layout
        sync_eras.register(pdx.MOD_ROOT);era_layout.sync(pdx.MOD_ROOT)
        p=pdx.MOD_ROOT/'ui/dashboard_registry.json';d=json.loads(pdx.read_text(p));d['modules']=[m for m in d['modules'] if m['id']!='strategic_storage']+[registry_module()];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        for key in ['tsin_oil_storage','tsin_strategic_storage']:
            p=pdx.MOD_ROOT/f'main_menu/gfx/interface/icons/buildings/{key}.dds'
            if not p.exists():
                source=pdx.MOD_ROOT/'era_7'/p.relative_to(pdx.MOD_ROOT);source.parent.mkdir(parents=True,exist_ok=True)
                source.write_bytes((pdx.game_root()/'main_menu/gfx/interface/icons/buildings/granary.dds').read_bytes())
        sync_eras.register(pdx.MOD_ROOT);era_layout.sync(pdx.MOD_ROOT)
        for rel,advance,building in [('tsin_03_industrial_capitalism.txt','tsin_oil_refining_advance','tsin_oil_storage'),('tsin_00_age_of_industrialization.txt','tsin_industrial_capitalism_advance','tsin_strategic_storage')]:
            p=pdx.MOD_ROOT/'in_game/common/advances'/rel;s=pdx.read_text(p)
            if 'unlock_building = '+building not in s:
                b=next(b for b in pdx.top_level_blocks(s) if b.key==advance);s=s[:b.start]+b.text.replace('{','{\n\tunlock_building = '+building,1)+s[b.end:];pdx.write_text_bom(p,s)
    print('Strategic storage:',len(bad),'differences');return bool(bad)
if __name__=='__main__':raise SystemExit(main())
