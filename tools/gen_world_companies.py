"""Explicit world company snapshots. Filtering/sorting/page projection never scans live countries."""
from pathlib import Path
import sys,argparse,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx
from gen_capital_markets import all_companies
PAGE=12
BASE_FIELDS=['country','count','industrial','generic','national','cash','cash_known','proxy','proxy_known','source_year']

def r(field,key='this'):return f'"global_variable_map(tsin_wcs_{field}|{key})"'
def w(field,value):return f'add_to_global_variable_map = {{ name = tsin_wcs_{field} key = scope:tsin_wcs_row value = {value} }}'
def registry_module():return {'id':'world_companies','metrics':[{'id':'world_company_cash','variable':'tsin_wcs_total_cash','title':{'korean':'세계 조사 기업 부문 현금 합계','english':'Surveyed world corporate cash'},'tabs':['finance'],'unit':'compact','frequency':'manual','description':{'korean':'세계 기업 조사 버튼으로 수집한 국가 기업 운영 현금의 합계입니다. 현금 장부가 없는 국가는 포함하지 않으며 기업 유형별로 임의 배분하지 않습니다.','english':'Country corporate cash summed by the world company survey. Excludes countries without cash ledgers; not arbitrarily allocated across company types.'}}],'shortcuts':[{'id':'world_companies','tab':'finance','title':{'korean':'세계 기업 통계 창','english':'World company statistics'},'open_variable':'tsin_ui_world_companies_open'}]}

def build():
 rows=all_companies();fields=BASE_FIELDS+['company_'+c['id'] for c in rows]
 filters=[(0,'전체','All',None),(1,'산업 기업','Industrial','industrial'),(2,'전근대·일반 기업','Generic businesses','generic'),(3,'국가 고유 기업','National organizations','national')]+[(10+i,'$STATIC_MODIFIER_NAME_tsin_company_'+c['id']+'$','$STATIC_MODIFIER_NAME_tsin_company_'+c['id']+'$','company_'+c['id']) for i,c in enumerate(rows)]
 values=['tsin_wcs_page_display = { value = 1 if = { limit = { has_variable = tsin_wcs_page } add = var:tsin_wcs_page } }\n'];fx=['''tsin_world_company_survey_effect = {
 save_scope_as = tsin_wcs_reader
 every_in_list = { variable = tsin_wcs_rows
  save_temporary_scope_value_as = { name = tsin_wcs_row value = this }
''']
 fx+=[' '+f'remove_from_global_variable_map = {{ name = tsin_wcs_{field} key = scope:tsin_wcs_row }}\n' for field in fields]
 fx.append(''' }
 clear_variable_list = tsin_wcs_rows
 if = { limit = { NOT = { has_global_variable = tsin_wcs_next_id } } set_global_variable = { name = tsin_wcs_next_id value = 0 } }
 set_variable = { name = tsin_wcs_survey_year value = current_year }
 set_variable = { name = tsin_wcs_survey_month value = current_month }
 set_variable = { name = tsin_wcs_total_countries value = 0 }
 set_variable = { name = tsin_wcs_total_firms value = 0 }
 set_variable = { name = tsin_wcs_total_cash value = 0 }
 set_variable = { name = tsin_wcs_cash_countries value = 0 }
 every_country = { limit = { is_real_country = yes exists = capital tsin_company_count > 0 }
  save_scope_as = tsin_wcs_country
  set_global_variable = { name = tsin_wcs_next_id value = { value = global_var:tsin_wcs_next_id add = 1 } }
  save_temporary_scope_value_as = { name = tsin_wcs_row value = global_var:tsin_wcs_next_id }
''')
 defaults={'country':'this','count':'tsin_company_count','industrial':'tsin_wcs_industrial_count','generic':'tsin_wcs_generic_count','national':'tsin_wcs_national_count','cash':'0','cash_known':'0','proxy':'0','proxy_known':'0','source_year':'0'}
 fx += ['  '+w(field,value)+'\n' for field,value in defaults.items()]
 for c in rows:fx.append('  '+w('company_'+c['id'],'tsin_firm_number_'+c['id'])+'\n')
 fx.append('''  if = { limit = { has_variable = tsin_firm_cash }
'''+w('cash','var:tsin_firm_cash')+'\n'+w('cash_known','1')+'''
   save_temporary_scope_value_as = { name = tsin_wcs_cash value = var:tsin_firm_cash }
   scope:tsin_wcs_reader = { change_variable = { name = tsin_wcs_total_cash add = scope:tsin_wcs_cash } change_variable = { name = tsin_wcs_cash_countries add = 1 } }
  }
  if = { limit = { has_variable = tsin_statistics_company_value has_variable = tsin_stock_ui_stats_year }
'''+w('proxy','var:tsin_statistics_company_value')+'\n'+w('proxy_known','1')+'\n'+w('source_year','var:tsin_stock_ui_stats_year')+'''
  }
  save_temporary_scope_value_as = { name = tsin_wcs_count value = tsin_company_count }
  scope:tsin_wcs_reader = {
   add_to_variable_list = { name = tsin_wcs_rows target = scope:tsin_wcs_row }
   change_variable = { name = tsin_wcs_total_countries add = 1 }
   change_variable = { name = tsin_wcs_total_firms add = scope:tsin_wcs_count }
  }
 }
 if = { limit = { NOT = { has_variable = tsin_wcs_filter } } set_variable = { name = tsin_wcs_filter value = 0 } }
 if = { limit = { NOT = { has_variable = tsin_wcs_sort } } set_variable = { name = tsin_wcs_sort value = 0 } }
 set_variable = { name = tsin_wcs_page value = 0 }
 tsin_world_company_project_page_effect = yes
}
tsin_world_company_project_page_effect = {
 save_scope_as = tsin_wcs_reader
 set_variable = { name = tsin_wcs_matches value = 0 }
 set_variable = { name = tsin_wcs_slot value = 0 }
 set_local_variable = { name = tsin_wcs_offset value = { value = var:tsin_wcs_page multiply = 12 } }
''')
 for slot in range(1,PAGE+1):
  for field in ['country','count','cash','cash_known','proxy','proxy_known','source_year']:
   fx.append(f' remove_variable = tsin_wcs_display_{slot}_{field}\n')
 fx.append(''' clear_list = tsin_wcs_sort_rows
 every_in_list = { variable = tsin_wcs_rows add_to_list = tsin_wcs_sort_rows }
 ordered_in_list = {
  list = tsin_wcs_sort_rows limit = { tsin_wcs_selected_count > 0 }
  order_by = tsin_wcs_sort_value max = 100000
  save_temporary_scope_value_as = { name = tsin_wcs_row value = this }
  save_temporary_scope_value_as = { name = tsin_wcs_display_count value = tsin_wcs_selected_count }
  scope:tsin_wcs_reader = {
   change_variable = { name = tsin_wcs_matches add = 1 }
   if = { limit = { var:tsin_wcs_matches > local_var:tsin_wcs_offset var:tsin_wcs_slot < 12 }
    change_variable = { name = tsin_wcs_slot add = 1 }
''')
 for slot in range(1,PAGE+1):
  fx.append(f'    if = {{ limit = {{ var:tsin_wcs_slot = {slot} }}\n')
  for field in ['country','count','cash','cash_known','proxy','proxy_known','source_year']:
   value='scope:tsin_wcs_display_count' if field=='count' else r(field,'scope:tsin_wcs_row')
   fx.append(f'     set_variable = {{ name = tsin_wcs_display_{slot}_{field} value = {value} }}\n')
  fx.append('    }\n')
 fx.append('''   }
  }
 }
 clear_list = tsin_wcs_sort_rows
}
''')
 for kind in ['industrial','generic','national']:
  values.append(f'tsin_wcs_{kind}_count = {{ value = 0\n'+''.join(' add = tsin_firm_number_'+c['id']+'\n' for c in rows if c['kind']==kind)+'}\n')
 selected='tsin_wcs_selected_count = { value = 0\n'
 for code,ko,en,field in filters:selected+=f' if = {{ limit = {{ scope:tsin_wcs_reader = {{ var:tsin_wcs_filter = {code} }} }} value = {r(field or "count")} }}\n'
 values.append(selected+'}\n')
 values.append(f'''tsin_wcs_sort_value = {{
 value = tsin_wcs_selected_count
 if = {{ limit = {{ scope:tsin_wcs_reader = {{ var:tsin_wcs_sort = 1 }} }} value = {r('cash')} }}
 if = {{ limit = {{ scope:tsin_wcs_reader = {{ var:tsin_wcs_sort = 2 }} }} value = {r('proxy')} }}
}}
''')
 guis=[];loc={'english':{},'korean':{}};custom=[]
 def label(key,ko,en):loc['korean'][key]=ko;loc['english'][key]=en
 def script(key,valid,effect):guis.append(f'{key} = {{ scope = country is_shown = {{ always = yes }} is_valid = {{ {valid} }} effect = {{ {effect} }} }}\n')
 script('tsin_wcs_prev','has_variable = tsin_wcs_survey_year var:tsin_wcs_page > 0','change_variable = { name = tsin_wcs_page add = -1 } tsin_world_company_project_page_effect = yes')
 script('tsin_wcs_next','has_variable = tsin_wcs_survey_year var:tsin_wcs_matches > { value = var:tsin_wcs_page add = 1 multiply = 12 }','change_variable = { name = tsin_wcs_page add = 1 } tsin_world_company_project_page_effect = yes')
 for code,ko,en,field in filters:
  key='tsin_wcs_filter_'+str(code);script(key,'has_variable = tsin_wcs_survey_year',f'set_variable = {{ name = tsin_wcs_filter value = {code} }} set_variable = {{ name = tsin_wcs_page value = 0 }} tsin_world_company_project_page_effect = yes');label(key,ko,en)
 for code,ko,en in [(0,'기업 수순','Sort by firms'),(1,'국가 기업 현금순','Sort by country corporate cash'),(2,'국가 평가 지표순','Sort by country valuation proxy')]:
  key='tsin_wcs_sort_'+str(code);script(key,'has_variable = tsin_wcs_survey_year',f'set_variable = {{ name = tsin_wcs_sort value = {code} }} set_variable = {{ name = tsin_wcs_page value = 0 }} tsin_world_company_project_page_effect = yes');label(key,ko,en)
 def button(key,scripted,width=145):return f'''button_regular = {{ size = {{ {width} 28 }} enabled = "[GetScriptedGui('{scripted}').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
 action_tooltip = {{ title = "{key}" on_action = "[GetScriptedGui('{scripted}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" }}
 text_single = {{ size = {{ {width-6} 26 }} parentanchor = center autoresize = no fontsize = 12 fontsize_min = 8 text = "{key}" }}
}}'''
 ui=['''window = {
 name = "tsin_world_company_window" layer = topbar parentanchor = center widgetanchor = center
 size = { 1000 900 } movable = yes allow_outside = yes datacontext = "[GetPlayer]"
 visible = "[And(GetPlayer.IsValid, GetVariableSystem.Exists('tsin_ui_world_companies_open'))]"
 widget = { size = { 100% 100% } using = bg_window_default_alt }
 widget = { parentanchor = right position = { -8 8 } size = { 40 40 } button_close_alt = { blockoverride "close_on_action" { on_action = "[GetVariableSystem.Clear('tsin_ui_world_companies_open')]" } } }
 vbox = { position = { 20 18 } spacing = 5
 text_single = { fontsize = 22 text = "TSIN_WCS_TITLE" }
 text_multi = { maximumsize = { 945 -1 } fontsize = 12 text = "TSIN_WCS_HELP" }
 hbox = { spacing = 10
 widget = { size = { 200 30 } datacontext = "[GetGenericAction('tsin_survey_world_companies')]"
 button_regular = { size = { 200 30 } action_tooltip = { title = "tsin_survey_world_companies" on_action = "[PerformGenericAction(GenericAction.Self)]" }
 text_single = { size = { 194 28 } parentanchor = center text = "tsin_survey_world_companies" } }
 }
 text_single = { text = "TSIN_WCS_DATE" }
 }
 hbox = { spacing = 5
''']
 for code,ko,en,field in filters[:4]:ui.append(button('tsin_wcs_filter_'+str(code),'tsin_wcs_filter_'+str(code),180))
 ui+=['}','scrollarea = { size = { 950 100 }','scrollbarpolicy_horizontal = always_off','scrollbarpolicy_vertical = as_needed','scrollwidget = {','vbox = { spacing = 3']
 for start in range(4,len(filters),5):
  ui.append('hbox = { spacing = 4')
  for code,ko,en,field in filters[start:start+5]:ui.append(button('tsin_wcs_filter_'+str(code),'tsin_wcs_filter_'+str(code),180))
  ui.append('}')
 ui+=['} } }','hbox = { spacing = 5']
 for code in range(3):ui.append(button('tsin_wcs_sort_'+str(code),'tsin_wcs_sort_'+str(code),220))
 ui+=['}','text_single = { text = "TSIN_WCS_TOTALS" fontsize = 12 }','text_single = { text = "TSIN_WCS_FILTER_CURRENT" fontsize = 12 }','scrollarea = { size = { 950 410 } scrollbarpolicy_horizontal = always_off scrollbarpolicy_vertical = as_needed scrollwidget = { vbox = { spacing = 4','hbox = { spacing = 5']
 for key,width in [('COUNTRY',240),('COUNT',90),('CASH',175),('PROXY',175),('SOURCE',100)]:ui.append(f'text_single = {{ size = {{ {width} 24 }} fontsize = 13 text = "TSIN_WCS_{key}" }}')
 ui.append('}')
 for slot in range(1,PAGE+1):
  prefix='tsin_wcs_display_'+str(slot)+'_'
  ui.append(f'''hbox = {{ spacing = 5 visible = "[GetPlayer.MakeScope.GetVariable('{prefix}country').IsSet]"
 widget = {{ size = {{ 240 23 }} datacontext = "[GetPlayer.MakeScope.GetVariable('{prefix}country').GetCountry]"
 text_single = {{ size = {{ 235 22 }} autoresize = no fontsize = 13 fontsize_min = 10 text = "[Country.GetName]" tooltipwidget = {{ using = CountryTooltip }} }} }}
 text_single = {{ size = {{ 90 23 }} text = "[GetPlayer.MakeScope.GetVariable('{prefix}count').GetValue|0]" }}
 text_single = {{ size = {{ 175 23 }} text = "[GetPlayer.Custom('tsin_wcs_fmt_{slot}_cash')]" }}
 text_single = {{ size = {{ 175 23 }} text = "[GetPlayer.Custom('tsin_wcs_fmt_{slot}_proxy')]" }}
 text_single = {{ size = {{ 100 23 }} text = "[GetPlayer.MakeScope.GetVariable('{prefix}source_year').GetValue|0]" }}
}}''')
  for field in ['cash','proxy']:
   variable=prefix+field;name=f'tsin_wcs_fmt_{slot}_{field}';custom.append(f'{name} = {{ type = country random_valid = no\n text = {{ trigger = {{ var:{variable}_known = 0 }} localization_key = TSIN_WCS_MISSING }}\n')
   for suffix,cut,div in [('T',1000000000000,1000000000000),('B',1000000000,1000000000),('M',1000000,1000000),('K',1000,1000),('BASE',0,1)]:
    key=f'TSIN_WCS_FMT_{slot}_{field.upper()}_{suffix}'
    if cut:custom.append(f' text = {{ trigger = {{ var:{variable} >= {cut} }} localization_key = {key} }}\n')
    else:custom.append(f' text = {{ localization_key = {key} }}\n')
    getter=f"GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('tsin_wcs_fmt_{slot}_{field}_{suffix.lower()}')"
    label(key,f'[{getter}|1]'+('' if suffix=='BASE' else suffix),f'[{getter}|1]'+('' if suffix=='BASE' else suffix))
    values.append(f'tsin_wcs_fmt_{slot}_{field}_{suffix.lower()} = {{ value = var:{variable} divide = {div} }}\n')
   custom.append('}\n')
 ui+=['hbox = { spacing = 8',button('TSIN_WCS_PREV','tsin_wcs_prev'),button('TSIN_WCS_NEXT','tsin_wcs_next'),'text_single = { text = "TSIN_WCS_PAGE" }','}','} } }','} }']
 custom.append('tsin_wcs_filter_name = { type = country random_valid = no\n'+''.join(f' text = {{ trigger = {{ var:tsin_wcs_filter = {code} }} localization_key = tsin_wcs_filter_{code} }}\n' for code,_,_,_ in filters)+' text = { localization_key = tsin_wcs_filter_0 }\n}\n')
 label('TSIN_WCS_FILTER_CURRENT',"현재 필터: [GetPlayer.Custom('tsin_wcs_filter_name')] — 전체 조사 기업 현금 [GetPlayer.Custom('tsin_ui_format_world_company_cash')]","Current filter: [GetPlayer.Custom('tsin_wcs_filter_name')] — all-survey corporate cash [GetPlayer.Custom('tsin_ui_format_world_company_cash')]")
 label('TSIN_WCS_TITLE','세계 기업 통계','World company statistics')
 label('TSIN_WCS_HELP','조사 버튼만 세계 자료를 갱신합니다. 필터·정렬·페이지는 저장된 결과만 읽습니다. 기업 수는 선택한 유형, 현금은 국가 기업의 운영 자금(은행·연금 제외), 평가 지표는 국가 기업 부문 전체입니다. 평가 지표는 주가×영업 기반의 추정 단위이며 두캇이나 실제 시가총액이 아닙니다. 0년/—는 자료 없음입니다.','Only Survey refreshes world data. Filters, sorting and pages use the snapshot. Firm counts follow the filter; cash is national operating-company cash (excluding bank and pension funds); valuation covers the national corporate sector. Valuation is a stock-price × business-base proxy, not gold or actual market capitalization. Year 0 / — means unavailable.')
 label('tsin_survey_world_companies','세계 기업 자료 조사','Survey world companies')
 label('tsin_survey_world_companies_desc','실재하는 기업 보유국의 기업 유형·수·기업 부문 현금과 마지막 평가 자료를 한 번 수집합니다. 자동 재조사는 하지 않습니다.','Request one snapshot of real company-owning countries, company types/counts, corporate-sector cash and last valuation cache. No automatic resurvey.')
 label('TSIN_WCS_DATE',"조사: [GetPlayer.MakeScope.GetVariable('tsin_wcs_survey_year').GetValue|0].[GetPlayer.MakeScope.GetVariable('tsin_wcs_survey_month').GetValue|0]", "Survey: [GetPlayer.MakeScope.GetVariable('tsin_wcs_survey_year').GetValue|0].[GetPlayer.MakeScope.GetVariable('tsin_wcs_survey_month').GetValue|0]")
 label('TSIN_WCS_TOTALS',"전체 조사: [GetPlayer.MakeScope.GetVariable('tsin_wcs_total_countries').GetValue|0]개국 / 기업 [GetPlayer.MakeScope.GetVariable('tsin_wcs_total_firms').GetValue|0]개. 현금 장부 보유국 [GetPlayer.MakeScope.GetVariable('tsin_wcs_cash_countries').GetValue|0]개.","All surveyed: [GetPlayer.MakeScope.GetVariable('tsin_wcs_total_countries').GetValue|0] countries / [GetPlayer.MakeScope.GetVariable('tsin_wcs_total_firms').GetValue|0] firms. [GetPlayer.MakeScope.GetVariable('tsin_wcs_cash_countries').GetValue|0] countries with cash ledgers.")
 for key,ko,en in [('COUNTRY','국가','Country'),('COUNT','기업 수','Firms'),('CASH','국가 기업 운영 현금','National operating cash'),('PROXY','국가 기업 평가 지표','National valuation proxy'),('SOURCE','평가 기준 연도','Valuation year'),('PREV','이전','Previous'),('NEXT','다음','Next'),('MISSING','—','—')]:label('TSIN_WCS_'+key,ko,en)
 label('TSIN_WCS_PAGE',"페이지: [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('tsin_wcs_page_display')|0] / 해당 국가 [GetPlayer.MakeScope.GetVariable('tsin_wcs_matches').GetValue|0]", "Page: [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('tsin_wcs_page_display')|0] / matching countries [GetPlayer.MakeScope.GetVariable('tsin_wcs_matches').GetValue|0]")
 outputs={'in_game/common/scripted_effects/tsin_world_companies.txt':'\n'.join(fx),'in_game/common/script_values/tsin_world_companies.txt':'\n'.join(values),'in_game/common/scripted_guis/tsin_world_companies.txt':'\n'.join(guis),'in_game/common/customizable_localization/tsin_world_companies.txt':'\n'.join(custom),'in_game/common/generic_actions/tsin_world_companies.txt':'''tsin_survey_world_companies = {
  type = owncountry price = price:tsin_world_company_survey_price show_message = no
  ai_tick = never automation_tick = never
  # Checked before the survey effect, which clears the stored rows first. A refused request keeps the snapshot.
  allow = { NOT = { has_variable = tsin_wcs_survey_cooldown } }
  effect = { scope:actor = { if = { limit = { NOT = { has_variable = tsin_wcs_survey_cooldown } } set_variable = { name = tsin_wcs_survey_cooldown value = yes days = 1 } tsin_world_company_survey_effect = yes } } }
}
''','in_game/common/prices/tsin_world_companies.txt':'tsin_world_company_survey_price = { gold = 0 }\n','in_game/gui/tsin_world_companies.gui':'\n'.join(ui)+'\n','in_game/gui/scripted_widgets/tsin_world_companies.txt':'gui/tsin_world_companies.gui = tsin_world_company_window\n'}
 for lang,labels in loc.items():outputs[f'main_menu/localization/{lang}/tsin_world_companies_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {k}: '+json.dumps(v,ensure_ascii=False)+'\n' for k,v in labels.items())
 return outputs

def integrate():
 p=pdx.MOD_ROOT/'ui/dashboard_registry.json';d=json.loads(pdx.read_text(p));d['modules']=[m for m in d['modules'] if m['id']!='world_companies']+[registry_module()];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 p=pdx.MOD_ROOT/'tools/gen_dashboard.py';s=p.read_text(encoding='utf-8')
 if "'open_variable'" not in s:
  s=s.replace("('view','map_mode','generic_action')","('view','map_mode','generic_action','open_variable')")
  s=s.replace("entry.get('generic_action')))","entry.get('generic_action',entry.get('open_variable'))))")
  s=s.replace("            elif 'generic_action' in s:","            elif 'open_variable' in s:\n                ui.append(action_button(key,[f\"GetVariableSystem.Set('{s['open_variable']}', 'yes')\",close],220))\n            elif 'generic_action' in s:")
  p.write_text(s,encoding='utf-8')
 p=pdx.MOD_ROOT/'tools/capital_market_ui.py';s=p.read_text(encoding='utf-8')
 if 'TSIN_CAP_WORLD_COMPANIES' not in s:
  s=s.replace("    loc('INDEX'", "    loc('WORLD_COMPANIES','World company statistics','세계 기업 통계')\n    loc('INDEX'",1)
  s=s.replace("    ui += ['text_single = { maximumsize", "    ui += [button('TSIN_CAP_WORLD_COMPANIES',\"GetVariableSystem.Set('tsin_ui_world_companies_open', 'yes')\",width=220)]\n    ui += ['text_single = { maximumsize",1)
  p.write_text(s,encoding='utf-8')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();bad=[]
 for rel,text in build().items():
  p=pdx.MOD_ROOT/rel
  if a.check:
   if not p.exists() or pdx.read_text(p)!=text:bad.append(rel)
  else:pdx.write_text_bom(p,text)
 if not a.check:integrate()
 print('World companies:',len(bad),'differences');return bool(bad)
if __name__=='__main__':raise SystemExit(main())
