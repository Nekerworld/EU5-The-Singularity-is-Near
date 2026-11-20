"""Rare chemical spills at neglected sites; no duplicate mortality or world scans."""
from pathlib import Path
import sys,json,argparse
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx
from gen_pollution import CHEMICAL,types

def build():
 chemical=types(CHEMICAL)
 fx=f'''# Province scope, only after the existing 5–7-year facility inspection.
tsin_industrial_safety_review_effect = {{
 owner ?= {{ save_scope_as = tsin_safety_owner }}
 if = {{ limit = {{
  var:tsin_facility_industry_size > 0 var:tsin_facility_industry_wear >= 90 var:tsin_facility_industry_age >= 20
  NOT = {{ has_variable = tsin_spill_district_cooldown }}
  owner ?= {{ tsin_env_popup_available_trigger = yes }}
  owner ?= {{ NOT = {{ has_variable = tsin_spill_country_cooldown }} }}
  NOT = {{ any_location_in_province = {{ OR = {{ NOT = {{ owner ?= scope:tsin_safety_owner }} NOT = {{ controller ?= scope:tsin_safety_owner }} }} }} }}
  any_location_in_province = {{ owner ?= scope:tsin_safety_owner controller ?= owner var:tsin_pollution_water >= 60
   any_buildings_in_location = {{ {chemical} is_opened = yes building_employed_amount > 0 }}
  }}
 }}
 random = {{ chance = 10
  random_location_in_province = {{ limit = {{ owner ?= scope:tsin_safety_owner controller ?= owner var:tsin_pollution_water >= 60
   any_buildings_in_location = {{ {chemical} is_opened = yes building_employed_amount > 0 }}
  }}
   save_scope_as = tsin_spill_site
   remove_variable = tsin_spill_remediation_paid
   set_variable = {{ name = tsin_spill_shutdown months = 6 }}
   set_variable = {{ name = tsin_spill_soil years = 10 }}
   province = {{ save_scope_as = tsin_spill_district set_variable = {{ name = tsin_spill_district_cooldown years = 20 }} }}
   owner = {{
    set_variable = {{ name = tsin_spill_country_cooldown years = 10 }}
    tsin_news_record_effect = {{ TYPE = 31 PRIORITY = 1 }}
    tsin_env_popup_claim_effect = yes
    trigger_event_non_silently = tsin_industrial_safety.1
   }}
  }}
 }}
 }}
}}
'''
 gate='scope:tsin_spill_site ?= { owner ?= root controller ?= root has_variable = tsin_spill_shutdown NOT = { has_variable = tsin_spill_remediation_paid } } scope:tsin_spill_district ?= { owner ?= root NOT = { any_location_in_province = { NOT = { controller ?= root } } } } gold >= scope:tsin_spill_district.tsin_spill_remediation_cost'
 event='''namespace = tsin_industrial_safety
tsin_industrial_safety.1 = {
 type = country_event outcome = negative
 title = tsin_industrial_safety.1.title desc = tsin_industrial_safety.1.desc
 illustration_tags = { 10 = interior 10 = regular }
 option = { name = tsin_industrial_safety.1.a
  trigger = { GATE }
  if = { limit = { GATE }
   add_gold = { value = scope:tsin_spill_district.tsin_spill_remediation_cost multiply = -1 }
   scope:tsin_spill_site = {
    set_variable = { name = tsin_spill_remediation_paid years = 10 }
    set_variable = { name = tsin_spill_shutdown months = 3 }
    set_variable = { name = tsin_spill_soil years = 3 }
   }
   scope:tsin_spill_district = { set_variable = { name = tsin_facility_industry_wear value = 0 } }
  }
  ai_chance = { factor = 3 }
 }
 option = { name = tsin_industrial_safety.1.b ai_chance = { factor = 1 } }
}
'''.replace('GATE',gate)
 auto='''tsin_chemical_spill_shutdown = {
 category = location type = location
 potential_trigger = { has_variable = tsin_spill_shutdown }
 local_mills_build_buildings_efficiency = -0.10
}
tsin_chemical_spill_soil = {
 category = location type = location
 potential_trigger = { has_variable = tsin_spill_soil }
 local_food_production_mult = -0.05
}
'''
 labels={
 'tsin_industrial_safety.1.title':('[tsin_spill_site.GetName]의 화학 설비 유출 사고','Chemical spill in [tsin_spill_site.GetName]'),
 'tsin_industrial_safety.1.desc':('장기간 정비되지 않은 산업 지방의 가동 화학 설비에서 유출 사고가 보고되었습니다. 고령·마모90 이상·높은 수질 오염이 겹쳤을 때만 드물게 발생합니다. 사고 지점에는 6개월 제분소·공장 건설 효율 -10%, 10년 지역 식량 생산 -5%가 적용됩니다. 사망자·POP 삭제·추가 질병 피해는 별도로 계산하지 않습니다. 긴급 복구비는 200두캇 × max(지방 산업 규모/25, 1)이며, 지급하면 산업 마모를 보수하고 사고 제한을 3개월·토양 후유증을 3년으로 단축합니다. 기술·시설 연령은 현대화하지 않습니다.','An operating chemical works in a long-neglected industrial district has reported a spill. Such incidents are rare and require old facilities, wear of at least 90 and high water pollution. The affected location receives -10% mill/factory construction efficiency for six months and -5% local food production for ten years. No additional deaths, POP deletion or disease damage are simulated. Emergency work costs 200 ducats × max(district industry scale/25, 1), repairs industrial wear and reduces the restrictions to three months and soil effects to three years. It does not modernize technology or reset facility age.'),
 'tsin_industrial_safety.1.a':('긴급 보수·토양 정화에 국고를 투입한다','Fund emergency repair and soil remediation'),
 'tsin_industrial_safety.1.b':('추가 지원 없이 점진적 회복을 기다린다','Allow gradual recovery without additional support'),
 'AUTO_MODIFIER_NAME_tsin_chemical_spill_shutdown':('화학 사고 현장 안전 작업','Chemical-incident safety work'),
 'AUTO_MODIFIER_NAME_tsin_chemical_spill_soil':('화학 유출의 토양 후유증','Soil effects of a chemical spill')}
 out={'in_game/common/scripted_effects/tsin_industrial_safety.txt':fx,'in_game/events/tsin_industrial_safety.txt':event,'in_game/common/auto_modifiers/tsin_industrial_safety.txt':auto,'in_game/common/script_values/tsin_industrial_safety.txt':'tsin_spill_remediation_cost = { value = tsin_facility_industry_price_factor multiply = 200 }\n'}
 for lang,i in [('korean',0),('english',1)]:out[f'main_menu/localization/{lang}/tsin_industrial_safety_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {k}: '+json.dumps(v[i],ensure_ascii=False)+'\n' for k,v in labels.items())
 return {k:v.rstrip()+'\n' for k,v in out.items()}

def integrate():
 p=pdx.MOD_ROOT/'tools/gen_facility_aging.py';s=p.read_text(encoding='utf-8')
 if 'tsin_industrial_safety_review_effect = yes' not in s:
  old="fx.append('   tsin_facility_schedule_review_effect = yes\\n  }\\n }\\n}\\n')"
  new="fx.append('   tsin_industrial_safety_review_effect = yes\\n   tsin_facility_schedule_review_effect = yes\\n  }\\n }\\n}\\n')"
  if old not in s:raise RuntimeError('Inspection hook missing')
  p.write_text(s.replace(old,new,1),encoding='utf-8')
 p=pdx.MOD_ROOT/'tools/gen_newspapers.py';s=p.read_text(encoding='utf-8')
 if '31:' not in s:
  article=('화학 설비 유출 사고','Chemical works spill','정비가 오랫동안 지연된 화학 설비에서 유출 사고가 보고되었습니다. 현장 안전 작업과 토양 복구 비용을 둘러싸고 대응이 진행됩니다.','A long-neglected chemical works has reported a spill. Safety work and soil remediation are under consideration.')
  p.write_text(s.replace('ARTICLES={','ARTICLES={31:'+repr(article)+',',1),encoding='utf-8')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();bad=[]
 for rel,text in build().items():
  p=pdx.MOD_ROOT/rel
  if a.check:
   if not p.exists() or pdx.read_text(p)!=text:bad.append(rel)
  else:pdx.write_text_bom(p,text)
 if not a.check:integrate()
 print('Industrial safety:',len(bad),'differences');return bool(bad)
if __name__=='__main__':raise SystemExit(main())
