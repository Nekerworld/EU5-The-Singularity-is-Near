"""Only explicit native actions request reports. No annual/monthly report hook.

Snapshots are written only by the two survey actions. Opening or paging the comparison window
reads stored rows and never starts a survey. Rows are keyed by a dense country id, so paging is a
range of ids rather than a scan of live countries.
"""
from pathlib import Path
import argparse,sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx

KEY_BASE=100000  # history key = country id * KEY_BASE + survey serial
PAGE=10          # countries per list page
HISTORY=12       # kept snapshots per country and for the world survey
SLOTS=4          # countries in the comparison table

FIELDS=[
 ('year','조사 연도','Survey year','number'),('month','조사 월','Survey month','number'),
 ('population','국내 조사 인구','Surveyed population','compact'),
 ('locations','국내 조사 지점','Surveyed locations','number'),
 ('urban','국내 시가화 지점','Surveyed urban locations','number'),
 ('buildings','국내 건물 레벨 합계','Surveyed building levels','number'),
 ('companies','국내 기업 수','Surveyed firms','number'),
 ('gdp','국내 추정 GDP 원자료','Reported estimated GDP','compact'),
 ('world_year','세계 조사 연도','World survey year','number'),
 ('world_month','세계 조사 월','World survey month','number'),
 ('world_countries','세계 조사 국가 수','Countries surveyed','number'),
 ('world_population','세계 조사 인구','Surveyed world population','compact'),
 ('world_companies','세계 기업 수 합계','Surveyed world firms','number'),
 ('world_known_gdp','GDP 자료 보유국 수','Countries with GDP data','number'),
 ('world_gdp','자료 보유국 추정 GDP 합계','Available estimated GDP total','compact')]

# Country snapshot values, written from the requester's report variables.
DOM_FIELDS=[('serial','var:tsin_cmp_count'),('year','var:tsin_report_year'),('month','var:tsin_report_month'),
 ('population','var:tsin_report_population'),('locations','var:tsin_report_locations'),('urban','var:tsin_report_urban'),
 ('buildings','var:tsin_report_buildings'),('companies','var:tsin_report_companies')]
DOM_READ=[f for f,_ in DOM_FIELDS]+['gdp','gdp_known']
WORLD_FIELDS=[('year','var:tsin_report_world_year'),('month','var:tsin_report_world_month'),
 ('countries','var:tsin_report_world_countries'),('population','var:tsin_report_world_population'),
 ('companies','var:tsin_report_world_companies'),('known_gdp','var:tsin_report_world_known_gdp'),('gdp','var:tsin_report_world_gdp')]

def gdel(name,key): return f'remove_from_global_variable_map = {{ name = {name} key = {key} }}'
def gput(name,key,value): return f'{gdel(name,key)} add_to_global_variable_map = {{ name = {name} key = {key} value = {value} }}'

def registry_module():
    return {'id':'manual_surveys','metrics':[
       {'id':'report_'+key,'variable':'tsin_report_'+key,'title':{'korean':ko,'english':en},
        'tabs':['overview'],'unit':unit,'frequency':'manual',
        'description':{'korean':'조사 버튼을 누른 시점의 보고서입니다. GDP·기업 원자료는 기존 장부의 마지막 계산값이며 보고서 기준일과 다를 수 있습니다.',
         'english':'Snapshot requested by the survey button. GDP and firm sources retain their existing ledger update dates.'}}
       for key,ko,en,unit in FIELDS],
       'shortcuts':[{'id':'survey_'+kind,'tab':'overview','title':{'korean':ko,'english':en},'generic_action':'tsin_survey_'+kind}
        for kind,ko,en in [('domestic','국내 통계 조사','Survey domestic statistics'),('world','세계 통계 조사','Survey world statistics')]]
       +[{'id':'country_compare','tab':'overview','title':{'korean':'국가 비교·이력 창','english':'Country comparison and history'},'open_variable':'tsin_ui_country_compare_open'}]}

def record_domestic_effect():
    L=['tsin_cmp_record_domestic_effect = {',
     ' if = { limit = { NOT = { has_global_variable = tsin_cmp_next_id } } set_global_variable = { name = tsin_cmp_next_id value = 0 } }',
     ' if = { limit = { NOT = { has_variable = tsin_cmp_id } }',
     '  set_global_variable = { name = tsin_cmp_next_id value = { value = global_var:tsin_cmp_next_id add = 1 } }',
     '  set_variable = { name = tsin_cmp_id value = global_var:tsin_cmp_next_id }',
     ' }',
     ' if = { limit = { NOT = { has_variable = tsin_cmp_count } } set_variable = { name = tsin_cmp_count value = 0 } }',
     ' change_variable = { name = tsin_cmp_count add = 1 }',
     ' save_temporary_scope_value_as = { name = tsin_cmp_row value = var:tsin_cmp_id }',
     f' save_temporary_scope_value_as = {{ name = tsin_cmph_key value = {{ value = var:tsin_cmp_id multiply = {KEY_BASE} add = var:tsin_cmp_count }} }}',
     f' if = {{ limit = {{ var:tsin_cmp_count > {HISTORY} }}',
     f'  save_temporary_scope_value_as = {{ name = tsin_cmph_old value = {{ value = var:tsin_cmp_id multiply = {KEY_BASE} add = var:tsin_cmp_count subtract = {HISTORY} }} }}']
    L+=[f'  {gdel("tsin_cmph_"+f,"scope:tsin_cmph_old")}' for f in DOM_READ]
    L.append(' }')
    L+=[f' {gput("tsin_cmph_"+f,"scope:tsin_cmph_key",src)}' for f,src in DOM_FIELDS]
    L+=[' if = { limit = { has_variable = tsin_report_gdp }',
     '  '+gput('tsin_cmph_gdp','scope:tsin_cmph_key','var:tsin_report_gdp'),
     '  '+gput('tsin_cmph_gdp_known','scope:tsin_cmph_key','1'),
     ' }',
     ' else = {',
     '  '+gput('tsin_cmph_gdp','scope:tsin_cmph_key','0'),
     '  '+gput('tsin_cmph_gdp_known','scope:tsin_cmph_key','0'),
     ' }',
     ' '+gput('tsin_cmp_country','scope:tsin_cmp_row','this'),
     ' '+gput('tsin_cmp_latest','scope:tsin_cmp_row','var:tsin_cmp_count'),
     ' tsin_cmp_project_effect = yes',
     '}']
    return '\n'.join(L)+'\n'

def record_world_effect():
    L=['tsin_cmpw_record_effect = {',
     ' if = { limit = { NOT = { has_global_variable = tsin_cmpw_serial } } set_global_variable = { name = tsin_cmpw_serial value = 0 } }',
     ' set_global_variable = { name = tsin_cmpw_serial value = { value = global_var:tsin_cmpw_serial add = 1 } }',
     ' save_temporary_scope_value_as = { name = tsin_cmpw_key value = global_var:tsin_cmpw_serial }',
     f' if = {{ limit = {{ global_var:tsin_cmpw_serial > {HISTORY} }}',
     f'  save_temporary_scope_value_as = {{ name = tsin_cmpw_old value = {{ value = global_var:tsin_cmpw_serial subtract = {HISTORY} }} }}']
    L+=[f'  {gdel("tsin_cmpw_"+f,"scope:tsin_cmpw_old")}' for f,_ in WORLD_FIELDS]
    L.append(' }')
    L+=[f' {gput("tsin_cmpw_"+f,"scope:tsin_cmpw_key",src)}' for f,src in WORLD_FIELDS]
    L+=[' tsin_cmp_project_effect = yes','}']
    return '\n'.join(L)+'\n'

# Viewing: reads stored maps into display variables of the player. No survey, no every_country.
def _row(P,V):
    L=[f' remove_variable = {P}_country',
       f' save_temporary_scope_value_as = {{ name = {P}_pid value = var:{V} }}',
       f' set_variable = {{ name = {P}_serial value = "global_variable_map(tsin_cmp_latest|scope:{P}_pid)" }}',
       f' save_temporary_scope_value_as = {{ name = {P}_key value = {{ value = scope:{P}_pid multiply = {KEY_BASE} add = var:{P}_serial }} }}']
    L+=[f' set_variable = {{ name = {P}_{f} value = "global_variable_map(tsin_cmph_{f}|scope:{P}_key)" }}' for f in DOM_READ if f!='serial']
    L.append(f' if = {{ limit = {{ var:{V} > 0 }} set_variable = {{ name = {P}_country value = "global_variable_map(tsin_cmp_country|scope:{P}_pid)" }} }}')
    return L

def _hist_row(k):
    P=f'tsin_cmp_h{k}'
    L=[f' set_variable = {{ name = {P}_serial value = {{ value = var:tsin_cmp_d_serial subtract = {k} min = 0 }} }}',
       f' save_temporary_scope_value_as = {{ name = {P}_key value = {{ value = scope:tsin_cmp_d_pid multiply = {KEY_BASE} add = var:{P}_serial }} }}']
    L+=[f' set_variable = {{ name = {P}_{f} value = "global_variable_map(tsin_cmph_{f}|scope:{P}_key)" }}' for f in DOM_READ if f!='serial']
    return L

def _world_row(k):
    P=f'tsin_cmp_w{k}'
    L=[f' set_variable = {{ name = {P}_serial value = {{ value = global_var:tsin_cmpw_serial subtract = {k} min = 0 }} }}',
       f' save_temporary_scope_value_as = {{ name = {P}_key value = var:{P}_serial }}']
    L+=[f' set_variable = {{ name = {P}_{f} value = "global_variable_map(tsin_cmpw_{f}|scope:{P}_key)" }}' for f,_ in WORLD_FIELDS]
    return L

def project_effect():
    L=['tsin_cmp_project_effect = {',
     ' if = { limit = { NOT = { has_global_variable = tsin_cmp_next_id } } set_global_variable = { name = tsin_cmp_next_id value = 0 } }',
     ' if = { limit = { NOT = { has_variable = tsin_cmp_page } } set_variable = { name = tsin_cmp_page value = 0 } }',
     ' if = { limit = { NOT = { has_variable = tsin_cmp_detail } } set_variable = { name = tsin_cmp_detail value = 0 } }']
    for s in range(1,SLOTS+1):
        L.append(f' if = {{ limit = {{ NOT = {{ has_variable = tsin_cmp_slot_{s} }} }} set_variable = {{ name = tsin_cmp_slot_{s} value = 0 }} }}')
    for i in range(1,PAGE+1):
        L.append(f' set_variable = {{ name = tsin_cmp_r{i}_id value = {{ value = var:tsin_cmp_page multiply = {PAGE} add = {i} }} }}')
        L.append(f' if = {{ limit = {{ var:tsin_cmp_r{i}_id > global_var:tsin_cmp_next_id }} set_variable = {{ name = tsin_cmp_r{i}_id value = 0 }} }}')
    for i in range(1,PAGE+1): L+=_row(f'tsin_cmp_r{i}',f'tsin_cmp_r{i}_id')
    for s in range(1,SLOTS+1): L+=_row(f'tsin_cmp_c{s}',f'tsin_cmp_slot_{s}')
    L+=_row('tsin_cmp_d','tsin_cmp_detail')
    for k in range(HISTORY): L+=_hist_row(k)
    for k in range(HISTORY): L+=_world_row(k)
    L.append('}')
    return '\n'.join(L)+'\n'

def actions_effect():
    L=[]
    L.append('tsin_cmp_prev_effect = { if = { limit = { var:tsin_cmp_page > 0 } change_variable = { name = tsin_cmp_page add = -1 } } tsin_cmp_project_effect = yes }')
    L.append('tsin_cmp_next_effect = { change_variable = { name = tsin_cmp_page add = 1 } tsin_cmp_project_effect = yes }')
    for i in range(1,PAGE+1):
        body=[]
        for s in range(1,SLOTS+1):
            conds=[f'var:tsin_cmp_slot_{s} = 0',f'var:tsin_cmp_r{i}_id > 0']+[f'NOT = {{ var:tsin_cmp_slot_{p} = var:tsin_cmp_r{i}_id }}' for p in range(1,s)]
            body.append(f' if = {{ limit = {{ {" ".join(conds)} }} set_variable = {{ name = tsin_cmp_slot_{s} value = var:tsin_cmp_r{i}_id }} }}')
        L.append(f'tsin_cmp_add_{i}_effect = {{\n'+'\n'.join(body)+'\n tsin_cmp_project_effect = yes\n}')
        L.append(f'tsin_cmp_detail_{i}_effect = {{ set_variable = {{ name = tsin_cmp_detail value = var:tsin_cmp_r{i}_id }} tsin_cmp_project_effect = yes }}')
    L.append('tsin_cmp_clear_effect = { '+' '.join(f'set_variable = {{ name = tsin_cmp_slot_{s} value = 0 }}' for s in range(1,SLOTS+1))+' set_variable = { name = tsin_cmp_detail value = 0 } tsin_cmp_project_effect = yes }')
    return '# GENERATED by tools/gen_manual_statistics.py\n'+'\n'.join(L)+'\n'

def _script(key,valid,effect):
    return f'{key} = {{ scope = country is_shown = {{ always = yes }} is_valid = {{ {valid} }} effect = {{ {effect} }} }}\n'

def scripted_guis():
    g=[]
    g.append(_script('tsin_cmp_prev','has_variable = tsin_cmp_page var:tsin_cmp_page > 0','tsin_cmp_prev_effect = yes'))
    g.append(_script('tsin_cmp_next','has_variable = tsin_cmp_page has_global_variable = tsin_cmp_next_id global_var:tsin_cmp_next_id > { value = var:tsin_cmp_page add = 1 multiply = %d }'%PAGE,'tsin_cmp_next_effect = yes'))
    g.append(_script('tsin_cmp_clear','has_variable = tsin_cmp_page','tsin_cmp_clear_effect = yes'))
    for i in range(1,PAGE+1):
        g.append(_script(f'tsin_cmp_add_{i}',f'has_variable = tsin_cmp_r{i}_country',f'tsin_cmp_add_{i}_effect = yes'))
        g.append(_script(f'tsin_cmp_detail_{i}',f'has_variable = tsin_cmp_r{i}_country',f'tsin_cmp_detail_{i}_effect = yes'))
    return ''.join(g)

# ---- window -------------------------------------------------------------------------------
def _v(name): return f"GetPlayer.MakeScope.GetVariable('{name}')"
def _num(name,w): return f'text_single = {{ size = {{ {w} 22 }} autoresize = no fontsize = 12 text = "[{_v(name)}.GetValue|0]" }}'
def _date(p,w): return f'text_single = {{ size = {{ {w} 22 }} autoresize = no fontsize = 12 text = "[{_v(p+"_year")}.GetValue|0].[{_v(p+"_month")}.GetValue|0]" }}'
def _name(p,w):
    return (f'hbox = {{ visible = "[{_v(p+"_country")}.IsSet]" widget = {{ size = {{ {w} 22 }} datacontext = "[{_v(p+"_country")}.GetCountry]" '
            f'text_single = {{ size = {{ {w-4} 22 }} autoresize = no fontsize = 12 fontsize_min = 8 text = "[Country.GetName]" }} }} }}')
def _lbl(key,w): return f'text_single = {{ size = {{ {w} 22 }} autoresize = no fontsize = 12 fontsize_min = 8 text = "{key}" }}'
def _btn(key,scripted,width):
    return f'''button_regular = {{ size = {{ {width} 26 }} enabled = "[GetScriptedGui('{scripted}').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"
 action_tooltip = {{ title = "{key}" on_action = "[GetScriptedGui('{scripted}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]" }}
 text_single = {{ size = {{ {width-6} 24 }} parentanchor = center autoresize = no fontsize = 12 fontsize_min = 8 text = "{key}" }}
}}'''

def window_gui():
    ui=['''window = {
 name = "tsin_country_compare_window" layer = topbar parentanchor = center widgetanchor = center
 size = { 1000 900 } movable = yes allow_outside = yes datacontext = "[GetPlayer]"
 visible = "[And(GetPlayer.IsValid, GetVariableSystem.Exists('tsin_ui_country_compare_open'))]"
 widget = { size = { 100% 100% } using = bg_window_default_alt }
 widget = { parentanchor = right position = { -8 8 } size = { 40 40 } button_close_alt = { blockoverride "close_on_action" { on_action = "[GetVariableSystem.Clear('tsin_ui_country_compare_open')]" } } }
 vbox = { position = { 20 18 } spacing = 5
 text_single = { fontsize = 22 text = "TSIN_CMP_TITLE" }
 text_multi = { maximumsize = { 945 -1 } fontsize = 12 text = "TSIN_CMP_HELP" }
 text_single = { visible = "[Not(GetPlayer.MakeScope.GetVariable('tsin_cmp_page').IsSet)]" fontsize = 12 text = "TSIN_CMP_EMPTY" }
 scrollarea = { size = { 950 800 } scrollbarpolicy_horizontal = always_off scrollbarpolicy_vertical = as_needed
 visible = "[GetPlayer.MakeScope.GetVariable('tsin_cmp_page').IsSet]"
 scrollwidget = { vbox = { spacing = 4''']
    ui.append('text_single = { fontsize = 16 text = "TSIN_CMP_LIST" }')
    ui.append('hbox = { spacing = 5 '+_btn('tsin_cmp_prev','tsin_cmp_prev',120)+' '+_btn('tsin_cmp_next','tsin_cmp_next',120)+' '+_btn('tsin_cmp_clear','tsin_cmp_clear',160)+' }')
    ui.append('hbox = { spacing = 5 '+_lbl('TSIN_CMP_COL_COUNTRY',200)+_lbl('TSIN_CMP_COL_SERIAL',60)+_lbl('TSIN_CMP_COL_DATE',100)+_lbl('TSIN_CMP_COL_POP',140)+_lbl('TSIN_CMP_COL_GDP',150)+_lbl('TSIN_CMP_COL_FIRMS',70)+'}')
    for i in range(1,PAGE+1):
        p=f'tsin_cmp_r{i}'
        ui.append(f'hbox = {{ spacing = 5 visible = "[{_v(p+"_country")}.IsSet]" '+_name(p,200)+' '+_num(p+'_serial',60)+' '+_date(p,100)+' '+_num(p+'_population',140)+' '+_num(p+'_gdp',150)+' '+_num(p+'_companies',70)+' '+_btn(f'tsin_cmp_add_{i}',f'tsin_cmp_add_{i}',100)+' '+_btn(f'tsin_cmp_detail_{i}',f'tsin_cmp_detail_{i}',100)+' }')
    ui.append('text_single = { fontsize = 16 text = "TSIN_CMP_COMPARE" }')
    ui.append('hbox = { spacing = 5 '+_lbl('TSIN_CMP_COL_ITEM',150)+''.join(_lbl(f'TSIN_CMP_SLOT_{s}',200) for s in range(1,SLOTS+1))+'}')
    rows=[('TSIN_CMP_COL_COUNTRY','name',None),('TSIN_CMP_COL_SERIAL','serial',None),('TSIN_CMP_COL_DATE','date',None),
          ('TSIN_CMP_COL_POP','num','population'),('TSIN_CMP_COL_LOC','num','locations'),('TSIN_CMP_COL_URBAN','num','urban'),
          ('TSIN_CMP_COL_BLD','num','buildings'),('TSIN_CMP_COL_FIRMS','num','companies'),('TSIN_CMP_COL_GDP','num','gdp')]
    for label,kind,field in rows:
        cells=[]
        for s in range(1,SLOTS+1):
            p=f'tsin_cmp_c{s}'
            if kind=='name': cells.append(_name(p,200))
            elif kind=='date': cells.append(_date(p,200))
            elif kind=='serial': cells.append(_num(p+'_serial',200))
            else: cells.append(_num(f'{p}_{field}',200))
        ui.append('hbox = { spacing = 5 '+_lbl(label,150)+' '+' '.join(cells)+' }')
    ui.append('text_single = { fontsize = 16 text = "TSIN_CMP_HISTORY" }')
    ui.append('hbox = { spacing = 5 '+_lbl('TSIN_CMP_DETAIL_OF',150)+' '+_name('tsin_cmp_d',240)+' }')
    ui.append('hbox = { spacing = 5 '+_lbl('TSIN_CMP_COL_SERIAL',60)+_lbl('TSIN_CMP_COL_DATE',100)+_lbl('TSIN_CMP_COL_POP',140)+_lbl('TSIN_CMP_COL_LOC',110)+_lbl('TSIN_CMP_COL_BLD',110)+_lbl('TSIN_CMP_COL_FIRMS',90)+_lbl('TSIN_CMP_COL_GDP',170)+'}')
    for k in range(HISTORY):
        p=f'tsin_cmp_h{k}'
        ui.append('hbox = { spacing = 5 '+_num(p+'_serial',60)+' '+_date(p,100)+' '+_num(p+'_population',140)+' '+_num(p+'_locations',110)+' '+_num(p+'_buildings',110)+' '+_num(p+'_companies',90)+' '+_num(p+'_gdp',170)+' }')
    ui.append('text_single = { fontsize = 16 text = "TSIN_CMP_WORLD" }')
    ui.append('hbox = { spacing = 5 '+_lbl('TSIN_CMP_COL_SERIAL',60)+_lbl('TSIN_CMP_COL_DATE',100)+_lbl('TSIN_CMP_COL_WCOUNTRIES',110)+_lbl('TSIN_CMP_COL_WPOP',140)+_lbl('TSIN_CMP_COL_FIRMS',90)+_lbl('TSIN_CMP_COL_WKNOWN',110)+_lbl('TSIN_CMP_COL_WGDP',170)+'}')
    for k in range(HISTORY):
        p=f'tsin_cmp_w{k}'
        ui.append('hbox = { spacing = 5 '+_num(p+'_serial',60)+' '+_date(p,100)+' '+_num(p+'_countries',110)+' '+_num(p+'_population',140)+' '+_num(p+'_companies',90)+' '+_num(p+'_known_gdp',110)+' '+_num(p+'_gdp',170)+' }')
    ui.append('text_single = { fontsize = 11 text = "TSIN_CMP_ZERO_NOTE" }')
    ui.append('} } }')
    ui.append('}')
    ui.append('}')
    return '\n'.join(ui)+'\n'

LABELS={
 'TSIN_CMP_TITLE':('국가 비교·이력','Country comparison and history'),
 'TSIN_CMP_HELP':('저장된 국내·세계 조사 스냅샷만 읽습니다. 페이지 이동, 비교 추가, 이력 보기는 조사를 새로 실행하지 않습니다. 국가별·세계 조사 이력은 최근 12회만 보관합니다. 목록은 조사를 한 번이라도 실행한 국가만 표시합니다.','Reads stored domestic and world survey snapshots only. Paging, adding to comparison and viewing history never start a survey. Each country and the world survey keep the latest 12 surveys. The list shows only countries that have surveyed at least once.'),
 'TSIN_CMP_EMPTY':('아직 저장된 조사가 없습니다. 국내 통계 조사나 세계 통계 조사를 실행하면 기록됩니다.','No stored surveys yet. Run a domestic or world statistics survey to record one.'),
 'TSIN_CMP_LIST':('조사된 국가 목록','Surveyed countries'),
 'TSIN_CMP_COMPARE':('비교 (최대 4개국, 최신 스냅샷)','Comparison (up to 4 countries, latest snapshot)'),
 'TSIN_CMP_HISTORY':('국내 조사 이력 (최근 12회, 회차 순)','Domestic survey history (latest 12, newest first)'),
 'TSIN_CMP_WORLD':('세계 조사 이력 (최근 12회, 회차 순)','World survey history (latest 12, newest first)'),
 'TSIN_CMP_DETAIL_OF':('이력 대상 국가','History for'),
 'TSIN_CMP_ZERO_NOTE':('0은 자료 없음을 뜻합니다. GDP는 조사 당시 장부가 없었으면 0입니다.','0 means no data. GDP is 0 when no ledger existed at survey time.'),
 'TSIN_CMP_PAGE':('페이지 이동','Page'),
 'TSIN_CMP_SLOT_1':('비교 1','Compare 1'),'TSIN_CMP_SLOT_2':('비교 2','Compare 2'),'TSIN_CMP_SLOT_3':('비교 3','Compare 3'),'TSIN_CMP_SLOT_4':('비교 4','Compare 4'),
 'TSIN_CMP_COL_ITEM':('항목','Item'),
 'TSIN_CMP_COL_COUNTRY':('국가','Country'),
 'TSIN_CMP_COL_SERIAL':('회차','Survey no.'),
 'TSIN_CMP_COL_DATE':('조사 연.월','Survey year.month'),
 'TSIN_CMP_COL_POP':('국내 조사 인구','Surveyed population'),
 'TSIN_CMP_COL_LOC':('조사 지점','Surveyed locations'),
 'TSIN_CMP_COL_URBAN':('시가화 지점','Urban locations'),
 'TSIN_CMP_COL_BLD':('건물 레벨 합계','Building levels'),
 'TSIN_CMP_COL_FIRMS':('기업 수','Firms'),
 'TSIN_CMP_COL_GDP':('추정 GDP 원자료','Estimated GDP source'),
 'TSIN_CMP_COL_WCOUNTRIES':('조사 국가 수','Countries surveyed'),
 'TSIN_CMP_COL_WPOP':('세계 조사 인구','World surveyed population'),
 'TSIN_CMP_COL_WKNOWN':('GDP 보유국 수','Countries with GDP'),
 'TSIN_CMP_COL_WGDP':('자료 보유국 GDP 합계','Available GDP total'),
 'tsin_cmp_prev':('이전','Previous'),'tsin_cmp_next':('다음','Next'),'tsin_cmp_clear':('비교·이력 지우기','Clear comparison and history'),
}
for i in range(1,PAGE+1):
    LABELS[f'tsin_cmp_add_{i}']=('비교 추가','Add to comparison'); LABELS[f'tsin_cmp_detail_{i}']=('이력 보기','View history')
def build():
    actions=[]
    for kind in ['domestic','world']:
        # One survey per kind per day. The same condition guards the button (allow) and the effect entry,
        # so a refused request changes no variable and keeps the previous snapshot.
        actions.append(f'''tsin_survey_{kind} = {{
 type = owncountry
 show_message = no
 ai_tick = never
 automation_tick = never
 price = price:tsin_survey_price
 allow = {{ NOT = {{ has_variable = tsin_survey_{kind}_cooldown }} }}
 effect = {{ scope:actor = {{ if = {{ limit = {{ NOT = {{ has_variable = tsin_survey_{kind}_cooldown }} }} set_variable = {{ name = tsin_survey_{kind}_cooldown value = yes days = 1 }} tsin_survey_{kind}_effect = yes }} }} }}
}}''')
    effects='''tsin_survey_domestic_effect = {
 save_scope_as = tsin_survey_requestor
 set_variable = { name = tsin_report_year value = current_year }
 set_variable = { name = tsin_report_month value = current_month }
 set_variable = { name = tsin_report_population value = { value = total_population multiply = 1000 } }
 set_variable = { name = tsin_report_companies value = tsin_company_count }
 remove_variable = tsin_report_gdp
 if = { limit = { has_variable = tsin_gdp } set_variable = { name = tsin_report_gdp value = var:tsin_gdp } }
 set_variable = { name = tsin_report_locations value = 0 }
 set_variable = { name = tsin_report_urban value = 0 }
 set_variable = { name = tsin_report_buildings value = 0 }
 every_owned_location = {
  save_temporary_scope_value_as = { name = tsin_survey_buildings value = total_building_levels }
  scope:tsin_survey_requestor = {
   change_variable = { name = tsin_report_locations add = 1 }
   change_variable = { name = tsin_report_buildings add = scope:tsin_survey_buildings }
  }
  if = { limit = { NOT = { location_rank ?= location_rank:rural_settlement } }
   scope:tsin_survey_requestor = { change_variable = { name = tsin_report_urban add = 1 } }
  }
 }
}
tsin_survey_world_effect = {
 save_scope_as = tsin_survey_requestor
 set_variable = { name = tsin_report_world_year value = current_year }
 set_variable = { name = tsin_report_world_month value = current_month }
 set_variable = { name = tsin_report_world_countries value = 0 }
 set_variable = { name = tsin_report_world_population value = 0 }
 set_variable = { name = tsin_report_world_companies value = 0 }
 set_variable = { name = tsin_report_world_known_gdp value = 0 }
 set_variable = { name = tsin_report_world_gdp value = 0 }
 every_country = {
  limit = { is_real_country = yes exists = capital }
  save_temporary_scope_value_as = { name = tsin_survey_population value = { value = total_population multiply = 1000 } }
  save_temporary_scope_value_as = { name = tsin_survey_companies value = tsin_company_count }
  scope:tsin_survey_requestor = {
   change_variable = { name = tsin_report_world_countries add = 1 }
   change_variable = { name = tsin_report_world_population add = scope:tsin_survey_population }
   change_variable = { name = tsin_report_world_companies add = scope:tsin_survey_companies }
  }
  if = { limit = { has_variable = tsin_gdp }
   save_temporary_scope_value_as = { name = tsin_survey_gdp value = var:tsin_gdp }
   scope:tsin_survey_requestor = {
    change_variable = { name = tsin_report_world_known_gdp add = 1 }
    change_variable = { name = tsin_report_world_gdp add = scope:tsin_survey_gdp }
   }
  }
 }
 tsin_cmpw_record_effect = yes
}
'''
    from gen_social_bases import transform_survey
    effects=effects.replace('}\ntsin_survey_world_effect',' tsin_cmp_record_domestic_effect = yes\n}\ntsin_survey_world_effect',1)
    effects=effects.rstrip()+'\n'+record_domestic_effect()+record_world_effect()
    effects=transform_survey(effects)
    outputs={'in_game/common/generic_actions/tsin_manual_surveys.txt':'\n'.join(actions)+'\n',
      'in_game/common/prices/tsin_manual_surveys.txt':'tsin_survey_price = { gold = 0 }\n',
      'in_game/common/scripted_effects/tsin_manual_surveys.txt':effects,
      'in_game/common/scripted_effects/tsin_country_compare.txt':project_effect()+actions_effect(),
      'in_game/common/scripted_guis/tsin_country_compare.txt':scripted_guis(),
      'in_game/gui/tsin_country_compare.gui':window_gui(),
      'in_game/gui/scripted_widgets/tsin_country_compare.txt':'gui/tsin_country_compare.gui = tsin_country_compare_window\n'}
    for lang in ['english','korean']:
        rows=[]
        for kind,ko,en in [('domestic','국내 통계 조사','Survey domestic statistics'),('world','세계 통계 조사','Survey world statistics')]:
            title=ko if lang=='korean' else en
            desc='지금 한 번 집계하여 TSIN 국가 통계의 보고서를 갱신합니다. 이후 자동 재계산하지 않습니다.' if lang=='korean' else 'Request one snapshot in TSIN national statistics. No automatic recalculation follows.'
            rows.extend([f' tsin_survey_{kind}: "{title}"',f' tsin_survey_{kind}_desc: "{desc}"'])
        outputs[f'main_menu/localization/{lang}/tsin_manual_surveys_l_{lang}.yml']='l_'+lang+':\n'+'\n'.join(rows)+'\n'
        idx=0 if lang=='korean' else 1
        outputs[f'main_menu/localization/{lang}/tsin_country_compare_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {k}: {json.dumps(v[idx],ensure_ascii=False)}\n' for k,v in LABELS.items())
    return outputs

def integrate():
    # Replace the module in place so the registry order does not change.
    p=pdx.MOD_ROOT/'ui/dashboard_registry.json';d=json.loads(pdx.read_text(p))
    d['modules']=[registry_module() if m['id']=='manual_surveys' else m for m in d['modules']]
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args();failures=[]
    for rel,text in build().items():
        p=pdx.MOD_ROOT/rel
        if args.check:
            if not p.exists() or pdx.read_text(p)!=text:failures.append(rel)
        else:pdx.write_text_bom(p,text)
    if not args.check:integrate()
    print('Manual statistics:',len(failures),'differences')
    return bool(failures)
if __name__=='__main__':raise SystemExit(main())
