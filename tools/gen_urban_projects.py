"""Paid location projects: no slot prerequisite and no monthly world scan."""
import argparse,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx

STAGES=[(1,300,6,25,'tsin_industrial_capitalism_advance','산업부지 정비','Industrial Site Preparation'),
        (2,600,12,50,'tsin_urban_planning_advance','도시 구획 확장','Urban District Expansion'),
        (3,1200,18,75,'tsin_engineering_education_advance','고밀도 개발','High-density Development')]

def build():
    actions=[];prices=[];modifiers=[];branches=[]
    loc={'english':{},'korean':{}}
    for n,cost,months,slots,advance,ko,en in STAGES:
        key=f'tsin_urban_project_{n}'
        previous='NOT = { has_variable = tsin_urban_project_stage }' if n==1 else f'var:tsin_urban_project_stage = {n-1}'
        gate=f'''owner ?= scope:actor
controller ?= scope:actor
tsin_is_urban_location = yes
NOT = {{ has_variable = tsin_urban_project_pending }}
{previous}'''
        actions.append(f'''{key} = {{
 type = owncountry
 show_message = yes
 ai_tick = monthly
 ai_tick_frequency = 12
 automation_tick = never
 price = price:{key}_price
 potential = {{ scope:actor = {{ has_advance = {advance} }} }}
 allow = {{ scope:actor = {{ has_advance = {advance} }}
 trigger_if = {{ limit = {{ exists = scope:target_location }} scope:target_location = {{ {gate} }} }} }}
 select_trigger = {{
  looking_for_a = location
  source = actor
  target_flag = target_location
  name = "choose_location"
  column = {{ data = name }}
  column = {{ data = population }}
  visible = {{ owner ?= scope:actor tsin_is_urban_location = yes }}
  enabled = {{ {gate} }}
 }}
 effect = {{
  scope:target_location = {{
   set_variable = {{ name = tsin_urban_project_pending value = {n} }}
   set_variable = {{ name = tsin_urban_project_due value = {{ value = tsin_urban_calendar_month add = {months} }} }}
   add_to_global_variable_list = {{ name = tsin_urban_project_sites target = this }}
   add_location_modifier = {{ modifier = tsin_urban_project_underway months = {months+1} }}
  }}
  set_global_variable = tsin_urban_projects_enabled
 }}
 ai_will_do = {{
  value = 0
  if = {{ limit = {{ scope:actor = {{ gold >= {cost*4} }}
   scope:target_location = {{ total_building_levels >= {{ value = modifier:free_building_levels multiply = 0.8 }} }} }}
   add = 10
  }}
 }}
}}''')
        prices.append(f'{key}_price = {{ gold = {cost} }}')
        modifiers.append(f'{key}_completed = {{ game_data = {{ category = location }} free_building_levels = {slots} }}')
        branches.append(f'''if = {{ limit = {{ var:tsin_urban_project_pending = {n} }}
 if = {{ limit = {{ NOT = {{ has_location_modifier = {key}_completed }} }}
  add_location_modifier = {{ modifier = {key}_completed }}
 }}
 set_variable = {{ name = tsin_urban_project_stage value = {n} }}
}}''')
        for lang,title in [('korean',ko),('english',en)]:
            desc=(f'지점을 선택하여 {cost}두캇을 투자합니다. {months}개월 후 지원 건물 레벨이 {slots} 증가합니다. 건물 슬롯을 소비하지 않습니다.' if lang=='korean' else f'Choose a location and invest {cost} ducats. After {months} months, supported building levels increase by {slots}. Uses no building slot.')
            loc[lang].update({key:title,key+'_desc':desc,'STATIC_MODIFIER_NAME_'+key+'_completed':title})
    for lang in loc:
        loc[lang]['STATIC_MODIFIER_NAME_tsin_urban_project_underway']='도시 수용력 확장 공사' if lang=='korean' else 'Urban Expansion Works'
    effects='''tsin_urban_project_review_effect = {
 set_global_variable = { name = tsin_urban_projects_review_month value = tsin_urban_calendar_month }
 clear_list = tsin_urban_project_review
 every_in_global_list = { variable = tsin_urban_project_sites add_to_list = tsin_urban_project_review }
 every_in_list = { list = tsin_urban_project_review
  if = { limit = { has_variable = tsin_urban_project_pending var:tsin_urban_project_due <= tsin_urban_calendar_month }
'''+ '\n'.join(branches)+'''
   remove_variable = tsin_urban_project_pending
   remove_variable = tsin_urban_project_due
   remove_location_modifier = tsin_urban_project_underway
   remove_list_global_variable = { name = tsin_urban_project_sites target = this }
  }
 }
 clear_list = tsin_urban_project_review
}
'''
    outputs={
      'in_game/common/generic_actions/tsin_urban_projects.txt':'\n\n'.join(actions)+'\n',
      'in_game/common/prices/tsin_urban_projects.txt':'\n'.join(prices)+'\n',
      'main_menu/common/static_modifiers/tsin_urban_projects.txt':'\n'.join(modifiers)+'\ntsin_urban_project_underway = { game_data = { category = location } }\n',
      'in_game/common/scripted_effects/tsin_urban_projects.txt':effects,
      'in_game/common/script_values/tsin_urban_projects.txt':'tsin_urban_calendar_month = { value = current_year multiply = 12 add = current_month }\n',
      'in_game/common/on_action/tsin_urban_projects.txt':'''monthly_country_pulse = { on_actions = { tsin_urban_project_global_review } }
tsin_urban_project_global_review = {
 trigger = { has_global_variable = tsin_urban_projects_enabled
  OR = { NOT = { has_global_variable = tsin_urban_projects_review_month }
   tsin_urban_calendar_month > global_var:tsin_urban_projects_review_month }
 }
 effect = { tsin_urban_project_review_effect = yes }
}
'''}
    for lang,rows in loc.items():
        outputs[f'main_menu/localization/{lang}/tsin_urban_projects_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {k}: "{v}"\n' for k,v in rows.items())
    return outputs

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    failures=[]
    for rel,text in build().items():
        p=pdx.MOD_ROOT/rel
        if args.check:
            if not p.exists() or pdx.read_text(p)!=text:failures.append(rel)
        else:pdx.write_text_bom(p,text)
    print('Urban projects:',len(failures),'differences')
    return bool(failures)
if __name__=='__main__':raise SystemExit(main())
