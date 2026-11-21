"""Movable right-side bill card. Reads the existing bill; never rolls or advances it."""
from pathlib import Path
import sys,argparse,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx
ESTATES=[('nobles_estate','귀족','Nobility'),('clergy_estate','성직자','Clergy'),('burghers_estate','시민','Burghers'),('peasants_estate','농민','Peasants'),('crown_estate','왕실','Crown')]

def registry_module():return {'id':'legislation_sidebar','shortcuts':[{'id':'bill_sidebar','tab':'crises','title':{'korean':'입법 현황 카드 표시','english':'Show legislation status card'},'open_variable':'tsin_ui_bill_sidebar_open'}]}

def build():
 effects='''# Waiting-end month metadata only. Original expiring timer still controls actual readings.
tsin_bill_schedule_sidebar_metadata_effect = {
 set_variable = { name = tsin_bill_wait_year value = current_year }
 set_variable = { name = tsin_bill_wait_month value = { value = current_month add = 3 } }
 if = { limit = { var:tsin_bill_wait_month > 12 }
  change_variable = { name = tsin_bill_wait_month add = -12 }
  change_variable = { name = tsin_bill_wait_year add = 1 }
 }
}
'''
 values=[];custom=[];loc={'english':{},'korean':{}}
 def label(key,ko,en):loc['korean'][key]=ko;loc['english'][key]=en
 for estate,ko,en in ESTATES:
  values.append(f'tsin_bill_sidebar_power_{estate} = {{ value = "estate_power(estate_type:{estate})" }}\n')
  custom.append(f'''tsin_bill_sidebar_{estate} = {{ type = country random_valid = no
 text = {{ trigger = {{ has_variable = tsin_bill_policy tsin_bill_preferred_by_trigger = {{ ESTATE = {estate} }} }} localization_key = TSIN_BILL_SIDE_{estate.upper()}_SUPPORT }}
 text = {{ trigger = {{ has_variable = tsin_bill_policy tsin_bill_opposed_by_trigger = {{ ESTATE = {estate} }} }} localization_key = TSIN_BILL_SIDE_{estate.upper()}_OPPOSE }}
 text = {{ localization_key = TSIN_BILL_SIDE_{estate.upper()}_NEUTRAL }}
}}
''')
  power=f"[GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('tsin_bill_sidebar_power_{estate}')|%0]"
  for suffix,k,e,color in [('SUPPORT','지지','supports','G'),('OPPOSE','반대','opposes','R'),('NEUTRAL','중립','neutral','V')]:label('TSIN_BILL_SIDE_'+estate.upper()+'_'+suffix,f'#{color} {ko} — {k}#! · {power}',f'#{color} {en} — {e}#! · {power}')
 ui=['''window = {
 name = "tsin_bill_sidebar" layer = topbar parentanchor = right|top widgetanchor = right|top
 position = { -440 220 } movable = yes allow_outside = yes datacontext = "[GetPlayer]"
 size = "[ToVector2f('(float)360', Select_float(GetVariableSystem.Exists('tsin_ui_bill_sidebar_expanded'), '(float)420', '(float)84'))]"
 visible = "[And(GetPlayer.IsValid, And(GetPlayer.MakeScope.GetVariable('tsin_bill_policy').IsSet, Or(Not(GetVariableSystem.Exists('tsin_ui_bill_sidebar_closed')), GetVariableSystem.Exists('tsin_ui_bill_sidebar_open'))))]"
 widget = { size = { 100% 100% } using = bg_window_default_alt
 widget = { parentanchor = right position = { -5 5 } size = { 36 36 } ui_direction_button_holder_right = {} button_close_alt = { blockoverride "close_on_action" {
 on_action = "[GetVariableSystem.Set('tsin_ui_bill_sidebar_closed', 'yes')]"
 on_action = "[GetVariableSystem.Clear('tsin_ui_bill_sidebar_open')]"
 } } }
 vbox = { using = window_margin_alt spacing = 6
 button_regular = { size = { 300 40 } action_tooltip = { title = "TSIN_BILL_SIDE_TITLE" on_action = "[GetVariableSystem.Toggle('tsin_ui_bill_sidebar_expanded')]" }
 text_single = { size = { 292 36 } parentanchor = center autoresize = no maximumsize = { 292 36 } fontsize = 14 fontsize_min = 10 align = center|nobaseline elide = right text = "TSIN_BILL_SIDE_TITLE" }
 }
 text_single = { size = { 320 28 } autoresize = no fontsize = 15 fontsize_min = 11 text = "[GetPlayer.MakeScope.GetVariable('tsin_bill_policy').GetPolicy.GetNameWithNoTooltip]" }
 vbox = { visible = "[GetVariableSystem.Exists('tsin_ui_bill_sidebar_expanded')]" using = bg_main_inner_alt margin = { 8 6 } spacing = 6
 text_single = { fontsize = 15 text = "TSIN_BILL_SIDE_CHANCE" tooltip = "TSIN_BILL_SIDE_CHANCE_HELP" }
 text_single = { fontsize = 14 text = "TSIN_BILL_SIDE_COUNTS" }
 text_single = { visible = "[GetPlayer.MakeScope.GetVariable('tsin_bill_wait_year').IsSet]" fontsize = 14 text = "TSIN_BILL_SIDE_DUE" tooltip = "TSIN_BILL_SIDE_DUE_HELP" }
 text_single = { visible = "[Not(GetPlayer.MakeScope.GetVariable('tsin_bill_wait_year').IsSet)]" fontsize = 14 text = "TSIN_BILL_SIDE_UNKNOWN_DUE" }
''']
 for estate,ko,en in ESTATES:ui.append(f'text_single = {{ fontsize = 14 text = "[GetPlayer.Custom(\'tsin_bill_sidebar_{estate}\')]" }}')
 ui+=['''text_multi = { maximumsize = { 320 -1 } fontsize = 12 text = "TSIN_BILL_SIDE_HELP" }
button_regular = { size = { 168 40 } action_tooltip = { title = "TSIN_BILL_SIDE_LAWS" on_action = "[OpenLateralView('laws')]" }
 text_single = { size = { 160 36 } parentanchor = center autoresize = no maximumsize = { 160 36 } fontsize = 14 fontsize_min = 10 align = center|nobaseline elide = right text = "TSIN_BILL_SIDE_LAWS" }
}
} } } }
''']
 label('TSIN_BILL_SIDE_TITLE',"입법 현황 · 성공 [GetPlayer.MakeScope.GetVariable('tsin_bill_successes').GetValue|0]/3", "Legislation · readings [GetPlayer.MakeScope.GetVariable('tsin_bill_successes').GetValue|0]/3")
 label('TSIN_BILL_SIDE_CHANCE',"다음 심의 성공 [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('tsin_bill_success_chance')|%0]", "Next reading success [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('tsin_bill_success_chance')|%0]")
 label('TSIN_BILL_SIDE_CHANCE_HELP','다음 한 차례 심의가 성공할 확률입니다. 최종 법안 통과 확률이 아닙니다. 계층 권력·선호, 사회 운동, 입법 효율과 논쟁 보너스를 반영합니다.','Chance of success in the next single reading, not the final enactment probability. Reflects estate power/preferences, movements, legislative efficiency and debate bonuses.')
 label('TSIN_BILL_SIDE_COUNTS',"성공 [GetPlayer.MakeScope.GetVariable('tsin_bill_successes').GetValue|0]/3 · 정체 [GetPlayer.MakeScope.GetVariable('tsin_bill_stalls').GetValue|0]/3", "Successes [GetPlayer.MakeScope.GetVariable('tsin_bill_successes').GetValue|0]/3 · stalls [GetPlayer.MakeScope.GetVariable('tsin_bill_stalls').GetValue|0]/3")
 label('TSIN_BILL_SIDE_DUE',"심의 대기 종료: [GetPlayer.MakeScope.GetVariable('tsin_bill_wait_year').GetValue|0].[GetPlayer.MakeScope.GetVariable('tsin_bill_wait_month').GetValue|0]", "Reading wait ends: [GetPlayer.MakeScope.GetVariable('tsin_bill_wait_year').GetValue|0].[GetPlayer.MakeScope.GetVariable('tsin_bill_wait_month').GetValue|0]")
 label('TSIN_BILL_SIDE_DUE_HELP','원래 3개월 대기의 종료 연월입니다. 실제 심의는 대기가 끝난 뒤 정기 심의 시점에 진행됩니다. 카드를 열거나 호버해도 심의가 추가되지 않습니다.','Month when the original three-month wait ends. The actual reading follows at its regular scheduled check. Opening or hovering the card adds no reading.')
 label('TSIN_BILL_SIDE_UNKNOWN_DUE','기존 법안: 대기 종료 자료 없음','Legacy bill: wait-end date unavailable')
 label('TSIN_BILL_SIDE_HELP','성공 3회면 통과, 정체 3회면 폐기됩니다. 계층 옆 숫자는 영향력입니다. 제목으로 접고 펼칠 수 있고 카드를 이동할 수 있습니다. 닫은 카드는 TSIN 위기·정책에서 다시 엽니다.','Three successes pass the bill; three stalls abandon it. Estate figures are their power. Click the title to collapse/expand; drag to reposition. Reopen a closed card from TSIN Crises & policies.')
 label('TSIN_BILL_SIDE_LAWS','법률 화면 열기','Open laws')
 outputs={'in_game/common/scripted_effects/tsin_bill_sidebar.txt':effects,'in_game/common/script_values/tsin_bill_sidebar.txt':'\n'.join(values),'in_game/common/customizable_localization/tsin_bill_sidebar.txt':'\n'.join(custom),'in_game/gui/tsin_bill_sidebar.gui':'\n'.join(ui),'in_game/gui/scripted_widgets/tsin_bill_sidebar.txt':'gui/tsin_bill_sidebar.gui = tsin_bill_sidebar\n'}
 for lang,labels in loc.items():outputs[f'main_menu/localization/{lang}/tsin_bill_sidebar_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {k}: '+json.dumps(v,ensure_ascii=False)+'\n' for k,v in labels.items())
 return outputs

def integrate():
 p=pdx.MOD_ROOT/'in_game/common/scripted_effects/tsin_legislation_effects.txt';s=pdx.read_text(p)
 if 'tsin_bill_schedule_sidebar_metadata_effect = yes' not in s:
  timer='set_variable = { name = tsin_bill_check_timer months = 3 }'
  s=s.replace(timer,timer+'\n\t\ttsin_bill_schedule_sidebar_metadata_effect = yes')
  s=s.replace('\tremove_variable = tsin_bill_check_timer','\tremove_variable = tsin_bill_check_timer\n\tremove_variable = tsin_bill_wait_year\n\tremove_variable = tsin_bill_wait_month')
  pdx.write_text_bom(p,s)
 p=pdx.MOD_ROOT/'ui/dashboard_registry.json';d=json.loads(pdx.read_text(p));d['modules']=[m for m in d['modules'] if m['id']!='legislation_sidebar']+[registry_module()];p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();bad=[]
 for rel,text in build().items():
  p=pdx.MOD_ROOT/rel
  if a.check:
   if not p.exists() or pdx.read_text(p)!=text:bad.append(rel)
  else:pdx.write_text_bom(p,text)
 if not a.check:integrate()
 print('Bill sidebar:',len(bad),'differences');return bool(bad)
if __name__=='__main__':raise SystemExit(main())
