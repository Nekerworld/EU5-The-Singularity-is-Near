"""Bounded factual newspaper archive; reporting never repeats gameplay effects."""
from pathlib import Path
import sys,argparse,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx
ARTICLES={10:('국제 규격 논의에 참여','Participation in international standards','국가가 도량형·철도·산업 부품·전기 설비 가운데 한 분야의 규격을 선택했습니다. 다른 분야의 독자 규격은 그대로 유지할 수 있습니다.','The government has chosen a standard in one field of measures, railways, industrial parts or electrical equipment. Independent choices in other fields remain possible.'),20:('굴뚝 아래에서 온 청원','Petition beneath the chimneys','산업 도시 주민들이 여러 해 지속된 매연에 대해 관청에 청원했습니다. 여과 설비 지원 여부를 둘러싼 논의가 이어지고 있습니다.','Residents of an industrial town have petitioned the authorities after years of smoke exposure. Debate continues over support for emission filters.'),21:('콜레라 발생 보고','Cholera outbreak reported','도시에서 콜레라 발생이 보고되었습니다. 방역 당국은 위생 개선과 감염 대응에 나서고 있습니다.','A city has reported a cholera outbreak. Public health authorities are responding to infection and sanitation needs.'),30:('지방 설비 정비 지원 집행','District maintenance support paid','정부가 산업 지방의 시설 정비에 자금을 집행했습니다. 설비 상태를 유지하는 지원과 새로운 기술을 도입하는 현대화 투자는 구분됩니다.','The treasury has funded maintenance in an industrial district. Keeping equipment in working order is distinct from investing in newer technology.'),40:('기업 이자 연체 장기화','Corporate interest arrears persist','기업 신용 또는 회사채의 이자 지급 지연이 반년 이상 이어졌습니다. 금융권은 유동성 부족과 채무 상환 능력을 주시하고 있습니다.','Interest arrears on corporate credit or bonds have continued for at least half a year. Financial institutions are watching liquidity and repayment capacity.')}

def registry_module():
 return {'id':'newspapers','shortcuts':[{'id':'read_newspaper','tab':'society','title':{'korean':'신문·최근 기사 열람','english':'Read newspaper archive'},'generic_action':'tsin_read_newspaper'}]}

def build():
 triggers='''tsin_has_periodical_press = { OR = { has_advance = printing_press_advance has_advance = tsin_popular_press_advance has_advance = tsin_mass_communication_advance } }
'''
 effects=['''# Country scope; metadata-only record of an event which already happened.
tsin_news_record_effect = {
 if = { limit = { is_ai = no tsin_has_periodical_press = yes
  NOT = { AND = { var:tsin_news_0_type = $TYPE$ var:tsin_news_0_year = current_year } }
 }
''']
 for slot in range(5,0,-1):
  for field in ['type','year','month']:
   effects.append(f'''  if = {{ limit = {{ has_variable = tsin_news_{slot-1}_{field} }} set_variable = {{ name = tsin_news_{slot}_{field} value = var:tsin_news_{slot-1}_{field} }} }}
  else = {{ remove_variable = tsin_news_{slot}_{field} }}
''')
 effects+=['''  set_variable = { name = tsin_news_0_type value = $TYPE$ }
  set_variable = { name = tsin_news_0_year value = current_year }
  set_variable = { name = tsin_news_0_month value = current_month }
  if = { limit = { $PRIORITY$ >= 2 } set_variable = tsin_news_pending_popup }
 }
}
tsin_news_publication_effect = {
 set_variable = { name = tsin_news_issue_year value = current_year }
 if = { limit = { NOT = { has_variable = tsin_news_issue_number } } set_variable = { name = tsin_news_issue_number value = 0 } }
 change_variable = { name = tsin_news_issue_number add = 1 }
 if = { limit = { OR = { var:tsin_arrears >= 6 var:tsin_bond_arrears >= 6 } NOT = { has_variable = tsin_news_financial_arrears_covered } }
  set_variable = tsin_news_financial_arrears_covered
  tsin_news_record_effect = { TYPE = 40 PRIORITY = 2 }
 }
 else_if = { limit = { NOT = { OR = { var:tsin_arrears >= 6 var:tsin_bond_arrears >= 6 } } } remove_variable = tsin_news_financial_arrears_covered }
 if = { limit = { has_variable = tsin_news_pending_popup OR = { NOT = { has_variable = tsin_news_popup_year } current_year > var:tsin_news_popup_year } }
  set_variable = { name = tsin_news_popup_year value = current_year }
  remove_variable = tsin_news_pending_popup
  trigger_event_non_silently = tsin_news.1
 }
}
''']
 # Priority comparison uses a temporary numeric value so expansion cannot create an invalid literal trigger key.
 effects[-1]=effects[-1].replace('if = { limit = { $PRIORITY$ >= 2 }','set_local_variable = { name = tsin_news_priority value = $PRIORITY$ }\n  if = { limit = { local_var:tsin_news_priority >= 2 }')
 values=[];custom=[];loc={'english':{},'korean':{}}
 for slot in range(6):
  custom.append(f'tsin_news_line_{slot} = {{ type = country random_valid = no\n')
  for code,(ko,en,kbody,ebody) in ARTICLES.items():
   key=f'TSIN_NEWS_LINE_{slot}_{code}'
   custom.append(f' text = {{ trigger = {{ var:tsin_news_{slot}_type = {code} }} localization_key = {key} }}\n')
   for lang,title,body in [('korean',ko,kbody),('english',en,ebody)]:
    loc[lang][key]=f"#T [ROOT.ScriptValue('tsin_news_{slot}_year')|0].[ROOT.ScriptValue('tsin_news_{slot}_month')|0] — {title}#!\n{body}"
  custom.append(' text = { localization_key = '+('TSIN_NEWS_EMPTY' if slot==0 else 'TSIN_NEWS_EMPTY_LINE')+' }\n}\n')
  for field in ['year','month']:values.append(f'tsin_news_{slot}_{field} = {{ value = 0 if = {{ limit = {{ has_variable = tsin_news_{slot}_{field} }} value = var:tsin_news_{slot}_{field} }} }}\n')
 for lang in loc:
  ko=lang=='korean'
  loc[lang].update({'tsin_read_newspaper':'신문·최근 기사 열람' if ko else 'Read newspaper archive','tsin_read_newspaper_desc':'인쇄술 이후 최근 기사 최대 6건을 읽습니다. 실제로 발생한 사건의 기록이며 열람으로 원래의 비용·효과·확률 판정을 다시 실행하지 않습니다. 주요호 팝업은 연 1회 이내입니다.' if ko else 'Read up to six recent factual articles after printing. Reading never repeats the original costs, effects or random rolls. Major-issue popups occur at most once a year.','tsin_news.1.title':'[ROOT.GetCountry.GetName] 공보' if ko else '[ROOT.GetCountry.GetName] Gazette','tsin_news.1.desc':'\n\n'.join(f"[ROOT.GetCountry.Custom('tsin_news_line_{slot}')]" for slot in range(6)),'tsin_news.1.a':'신문을 접는다' if ko else 'Put down the paper','TSIN_NEWS_EMPTY_LINE':'','TSIN_NEWS_EMPTY':'아직 등록된 기사가 없습니다.' if ko else 'No recorded article yet.'})
 outputs={'in_game/common/scripted_triggers/tsin_newspapers.txt':triggers,'in_game/common/scripted_effects/tsin_newspapers.txt':'\n'.join(effects),'in_game/common/script_values/tsin_newspapers.txt':'\n'.join(values),'in_game/common/customizable_localization/tsin_newspapers.txt':'\n'.join(custom),'in_game/common/generic_actions/tsin_newspapers.txt':'''tsin_read_newspaper = {
 type = owncountry price = price:tsin_newspaper_read_price show_message = no
 ai_tick = never automation_tick = never
 potential = { scope:actor = { tsin_has_periodical_press = yes } }
 effect = { scope:actor = { trigger_event_non_silently = tsin_news.1 } }
}
''','in_game/common/prices/tsin_newspapers.txt':'tsin_newspaper_read_price = { gold = 0 }\n','in_game/common/on_action/tsin_newspapers.txt':'''yearly_country_pulse = { on_actions = { tsin_newspaper_annual_publication } }
tsin_newspaper_annual_publication = {
 trigger = { is_ai = no tsin_has_periodical_press = yes OR = { NOT = { has_variable = tsin_news_issue_year } current_year > var:tsin_news_issue_year } }
 effect = { tsin_news_publication_effect = yes }
}
''','in_game/events/tsin_newspapers.txt':'''namespace = tsin_news
tsin_news.1 = {
 type = country_event title = tsin_news.1.title desc = tsin_news.1.desc outcome = neutral
 illustration_tags = { 10 = interior 10 = regular }
 option = { name = tsin_news.1.a ai_chance = { factor = 1 } }
}
'''}
 for lang,labels in loc.items():outputs[f'main_menu/localization/{lang}/tsin_newspapers_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {k}: '+json.dumps(v,ensure_ascii=False)+'\n' for k,v in labels.items())
 return outputs

def integrate():
 # Hook generator sources, then regenerate their normal outputs; no fragile patch only in generated files.
 p=pdx.MOD_ROOT/'tools/gen_standardization.py';s=p.read_text(encoding='utf-8')
 if 'tsin_news_record_effect' not in s:
  s=s.replace('   {count_change}\n','   {count_change}\n   tsin_news_record_effect = {{ TYPE = 10 PRIORITY = 1 }}\n');p.write_text(s,encoding='utf-8')
 p=pdx.MOD_ROOT/'tools/gen_pollution.py';s=p.read_text(encoding='utf-8')
 if 'tsin_news_record_effect' not in s:
  s=s.replace(' type = country_event title = tsin_pollution.1.title desc = tsin_pollution.1.desc outcome = neutral',' type = country_event title = tsin_pollution.1.title desc = tsin_pollution.1.desc outcome = neutral\n immediate = { tsin_news_record_effect = { TYPE = 20 PRIORITY = 1 } }');p.write_text(s,encoding='utf-8')
 p=pdx.MOD_ROOT/'tools/gen_facility_aging.py';s=p.read_text(encoding='utf-8')
 if 'tsin_news_record_effect' not in s:
  s=s.replace('      add_gold = {{ value = local_var:tsin_facility_cost multiply = -1 }}','      add_gold = {{ value = local_var:tsin_facility_cost multiply = -1 }}\n      tsin_news_record_effect = {{ TYPE = 30 PRIORITY = 1 }}');p.write_text(s,encoding='utf-8')
 p=pdx.MOD_ROOT/'in_game/common/scripted_effects/tsin_cholera_disease_effects.txt';s=pdx.read_text(p)
 if 'tsin_news_record_effect' not in s:
  s=s.replace('\t\tchange_variable = { name = tsin_cholera_outbreaks add = 1 }','\t\tchange_variable = { name = tsin_cholera_outbreaks add = 1 }\n\t\ttsin_news_record_effect = { TYPE = 21 PRIORITY = 2 }',1);pdx.write_text_bom(p,s)
 p=pdx.MOD_ROOT/'ui/dashboard_registry.json';d=json.loads(pdx.read_text(p));d['modules']=[m for m in d['modules'] if m['id']!='newspapers']+[registry_module()];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();bad=[]
 for rel,text in build().items():
  p=pdx.MOD_ROOT/rel
  if a.check:
   if not p.exists() or pdx.read_text(p)!=text:bad.append(rel)
  else:pdx.write_text_bom(p,text)
 if not a.check:integrate()
 print('Newspapers:',len(bad),'differences');return bool(bad)
if __name__=='__main__':raise SystemExit(main())
