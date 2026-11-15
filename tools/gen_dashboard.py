"""Generate the era-independent TSIN dashboard from ui/dashboard_registry.json.

--check verifies committed outputs without writing. Generated UI only reads
country caches and cheap scripted predicates; game actions remain in native views.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
import pdx

REGISTRY = 'ui/dashboard_registry.json'
LANGUAGES = ('english', 'korean')
SAFE_ID = re.compile(r'^[a-z][a-z0-9_]*$')
UNITS = {'number', 'compact', 'percent_points', 'fraction'}


def validate_registry(data):
    if not isinstance(data.get('schema_version'), int) or data['schema_version'] < 1:
        raise ValueError('schema_version must be a positive integer')
    tabs = [t['id'] for t in data['tabs']]
    if not tabs or len(tabs) > 6 or len(tabs) != len(set(tabs)):
        raise ValueError('Use 1–6 unique stable top-level tabs; expand eras within tabs')
    if 'overview' not in tabs:
        raise ValueError('The stable overview entry point cannot be removed')
    metrics, statuses, shortcuts = [], [], []
    for module in data['modules']:
        for hook in ['annual_effect','migration_effect']:
            if hook in module and not SAFE_ID.fullmatch(module[hook]):
                raise ValueError('module: invalid provider effect')
        metrics += module.get('metrics', [])
        statuses += module.get('statuses', [])
        shortcuts += module.get('shortcuts', [])
    for kind, entries in [('tab', data['tabs']), ('metric', metrics), ('status', statuses), ('shortcut', shortcuts), ('module', data['modules']), ('history', data.get('histories', []))]:
        ids = [e['id'] for e in entries]
        if len(ids) != len(set(ids)) or any(not SAFE_ID.fullmatch(x) for x in ids):
            raise ValueError(f'{kind}: invalid or duplicate ID')
    for entry in metrics + statuses + shortcuts + data['tabs']:
        if set(entry['title']) != set(LANGUAGES):
            raise ValueError(f'{entry["id"]}: both localized titles are required')
    for metric in metrics:
        if metric['unit'] not in UNITS or not SAFE_ID.fullmatch(metric['variable']):
            raise ValueError(f'{metric["id"]}: unsupported unit/variable')
        if metric['frequency'] not in {'annual','quarterly','monthly','event'}:
            raise ValueError(f'{metric["id"]}: unsupported update frequency')
        if not set(metric['tabs']) <= set(tabs):
            raise ValueError(f'{metric["id"]}: unknown tab')
    for entry in statuses + shortcuts:
        if entry['tab'] not in tabs:
            raise ValueError(f'{entry["id"]}: unknown tab')
    for entry in shortcuts:
        if ('view' in entry) == ('map_mode' in entry):
            raise ValueError('shortcut must have exactly one native view or map target')
        target=entry.get('view',entry.get('map_mode'))
        if not SAFE_ID.fullmatch(target):
            raise ValueError('shortcut: invalid target')
    for entry in statuses:
        if re.search(r'\b(?:any_country|every_country|random_country|every_location|any_owned_location|every_owned_location)\b',entry['condition']):
            raise ValueError('UI predicates must read cheap cached conditions, not scan the world/locations')
    ids = {m['id'] for m in metrics}
    if 'gdp' not in ids or not any(h['id']=='gdp' for h in data.get('histories',[])):
        raise ValueError('Keep the stable GDP metric/history used by existing frontend adapters')
    if not set(data.get('compact_metrics', [])) <= ids or len(data.get('compact_metrics', [])) > 8:
        raise ValueError('compact_metrics must reference up to eight registered metrics')
    for history in data.get('histories', []):
        if history['id'] not in ids or history['tab'] not in tabs:
            raise ValueError('history must reference an existing metric and tab')
        if not 1 <= history['samples'] <= 10:
            raise ValueError('history samples must be 1–10; provide a backend recorder separately')
        for field in ['value_prefix', 'year_prefix', 'peak_variable', 'backend_effect']:
            if not SAFE_ID.fullmatch(history[field]):
                raise ValueError('history: invalid provider ID')
    return metrics, statuses, shortcuts


def check_provider_links(data, root):
    """Catch registries with valid UI but no calculation/history provider."""
    files=list((root/'in_game/common').rglob('*.txt'))
    bodies=[pdx.strip_comments(pdx.read_text(p)) for p in files]
    text='\n'.join(bodies)
    variables=set(re.findall(r'\bname\s*=\s*(tsin_\w+)',text))
    variables.update(re.findall(r'\bVAR\s*=\s*(tsin_\w+)',text))
    effects={b.key for p in (root/'in_game/common/scripted_effects').glob('*.txt') for b in pdx.top_level_blocks(pdx.read_text(p))}
    errors=[]
    metrics,_,_=validate_registry(data)
    for metric in metrics:
        if metric['variable'] not in variables:
            errors.append(f'metric {metric["id"]}: no cached variable provider for {metric["variable"]}')
    providers=[]
    for module in data['modules']:
        providers += [module[k] for k in ['annual_effect','migration_effect'] if k in module]
    for history in data.get('histories',[]):
        providers.append(history['backend_effect'])
        for variable in [history['peak_variable']]+[prefix+str(i) for prefix in [history['value_prefix'],history['year_prefix']] for i in range(history['samples'])]:
            if variable not in variables: errors.append(f'history {history["id"]}: no provider for {variable}')
    for provider in providers:
        if provider not in effects:
            errors.append(f'undefined provider effect {provider}')
        elif not re.search(r'\b'+re.escape(provider)+r'\s*=\s*yes\b',text):
            errors.append(f'unscheduled provider effect {provider}')
    return errors


def build(data):
    metrics, statuses, shortcuts = validate_registry(data)
    by_id = {m['id']: m for m in metrics}
    loc = {language: {} for language in LANGUAGES}
    def localized(key, en, ko):
        loc['english'][key] = en
        loc['korean'][key] = ko
        return key
    def title(kind, entry):
        key = f'TSIN_UI_{kind}_{entry["id"].upper()}'
        return localized(key, entry['title']['english'], entry['title']['korean'])
    def variable(name):
        return f"GetPlayer.MakeScope.GetVariable('{name}')"
    def is_set(name):
        return variable(name) + '.IsSet'
    def gate(id):
        return f"GetScriptedGui('tsin_ui_check_{id}').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)"
    def action_button(key, actions, width=130):
        return '\n'.join(['button_regular = {', f'    size = {{ {width} 30 }}', '    action_tooltip = {', f'        title = "{key}"'] + [f'        on_action = "[{a}]"' for a in actions] + ['    }', f'    text_single = {{ size = {{ {width-8} 28 }} parentanchor = center autoresize = no fontsize = 13 fontsize_min = 10 align = center|nobaseline text = "{key}" }}', '}'])
    open_var = 'tsin_ui_dashboard_open'
    tab_var = 'tsin_ui_dashboard_tab'
    def open_tab(id):
        return [f"GetVariableSystem.Set('{open_var}', 'yes')", f"GetVariableSystem.Set('{tab_var}', '{id}')"]
    def selected(id):
        return f"GetVariableSystem.HasValue('{tab_var}', '{id}')"
    labels = {
        'TITLE': ('TSIN · Civilization management', 'TSIN · 문명 관리'),
        'OPEN': ('TSIN management', 'TSIN 관리'),
        'DOCK': ('Shortcuts', '바로가기'),
        'MISSING': ('—', '—'),
        'ANNUAL': ('Updated annually', '연간 갱신'),
        'QUARTERLY': ('Updated quarterly', '분기 갱신'),
        'MONTHLY': ('Updated monthly', '월간 갱신'),
        'EVENT': ('Updated by events', '이벤트 발생 시 갱신'),
        'DATE': ('Annual aggregate year', '연간 통계 기준 연도'),
        'NO_DATE': ('Not recorded yet', '아직 기록되지 않음'),
        'NO_CRISIS': ('No registered crisis or bill is active.', '등록된 위기나 심의 중인 법안이 없습니다.'),
        'UNAVAILABLE': ('Not yet collected or not applicable. A dash is not a zero.', '미집계 또는 적용 대상이 아닙니다. —는 0을 의미하지 않습니다.'),
        'ACTIVE': ('Active', '진행 중'),
        'MET': ('Requirement met', '조건 충족'),
        'NOT_MET': ('Requirement not met', '조건 미충족'),
        'GUIDE': ('Read-only cached statistics. Use the linked native views for actions and their normal costs and requirements.', '저장된 통계를 표시합니다. 행동은 연결된 기본 화면에서 기존 조건과 비용에 따라 실행합니다.'),
        'SOCIETY_HELP': ('Education approaches its targets annually. Targets are constrained by literacy, lower education, capacity and policy. Movement values use a 0–100 scale.', '교육률은 매년 목표치에 접근합니다. 목표는 문해율·하위 교육·시설 정원·정책의 제한을 받습니다. 사회운동은 0~100 척도입니다.'),
        'ECONOMY_HELP': ('Annual output and industry aggregates. Inspect individual goods and construction in the economy screen; the dashboard does not scan all locations on hover.', '연간 산출·산업 집계입니다. 개별 상품과 건설은 경제 화면에서 확인하십시오. 호버 시 전국 지점을 재집계하지 않습니다.'),
        'FINANCE_HELP': ('Company totals are annual snapshots. Existing stock prices update quarterly. Founding, charters and dissolution retain their existing decisions and costs.', '기업 수·상한·가치 합계는 연간 집계이며 기존 주가는 분기 갱신됩니다. 기업 설립·특허장·해산은 기존 결단과 비용을 유지합니다.'),
        'RESEARCH_HELP': ('Institution acceptance opens a technology root; it does not grant the technology. Native technologies show prerequisites and individual unlocks.', '시대관 수용은 뿌리 기술의 연구 조건을 엽니다. 기술 자체를 지급하지 않습니다. 선행 관계와 개별 해금은 기본 기술 화면에서 확인하십시오.'),
        'HISTORY_NOTE': ('Oldest observation first; shared scale. Only recorded observations are shown, with no reconstructed past. K=1,000 · M=1,000,000 · B=1,000,000,000 · T=1,000,000,000,000.', '오래된 관측치부터 같은 척도로 비교합니다. 기록한 관측치만 표시하며 과거를 복원하지 않습니다. K=천 · M=백만 · B=십억 · T=조.'),
    }
    for key, (en, ko) in labels.items(): localized('TSIN_UI_' + key, en, ko)
    for tab in data['tabs']: title('TAB', tab)
    custom = []
    def formatter(id, var):
        custom.extend([f'tsin_ui_format_{id} = {{', '\ttype = country', '\trandom_valid = no', '\ttext = {', f'\t\ttrigger = {{ NOT = {{ has_variable = {var} }} }}', '\t\tlocalization_key = TSIN_UI_MISSING', '\t}'])
        for suffix, divisor in [('T',10**12),('B',10**9),('M',10**6),('K',10**3),('',1)]:
            key = f'TSIN_UI_NUMBER_{id.upper()}_{suffix or "BASE"}'
            custom.extend(['\ttext = {'])
            if suffix: custom.append(f'\t\ttrigger = {{ var:{var} >= {divisor} }}')
            custom.extend([f'\t\tlocalization_key = {key}', '\t}'])
            getter = variable(var) + '.GetValue'
            value = f"[Divide_CFixedPoint({getter}, '(CFixedPoint){divisor}')|1]{suffix}" if suffix else f'[{getter}|{3 if id == "gdp_per_capita" else 0}]'
            localized(key,value,value)
        custom.append('}')
    # All frontends use these shared generated metric formatters.
    for m in metrics:
        if m['unit'] == 'compact': formatter(m['id'],m['variable'])
    def value_widget(m, small=False):
        size = 14 if small else 22
        if m['id']=='company_limit':
            free="GetScriptedGui('tsin_capital_is_private').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)"
            return f"""text_single = {{ visible = "[{free}]" fontsize = {size} text = "∞" }}
text_single = {{ visible = "[Not({free})]" fontsize = {size} text = "[{variable(m['variable'])}.GetValue|0]" }}"""

        if m['unit'] == 'compact':
            return f'text_single = {{ fontsize = {size} text = "[Player.Custom(\'tsin_ui_format_{m["id"]}\')]" }}'
        fmt = '1%' if m['unit']=='fraction' else '1'
        suffix = '%' if m['unit']=='percent_points' else ''
        expr = variable(m['variable'])+'.GetValue'
        return f'''text_single = {{ visible = "[{is_set(m['variable'])}]" fontsize = {size} text = "[{expr}|{fmt}]{suffix}" }}
text_single = {{ visible = "[Not({is_set(m['variable'])})]" fontsize = {size} text = "TSIN_UI_MISSING" }}'''
    common = ['# GENERATED by tools/gen_dashboard.py; edit ui/dashboard_registry.json.', 'types TSINDashboardCommon {']
    for m in metrics:
        key = title('METRIC',m)
        desc = f'TSIN_UI_HELP_{m["id"].upper()}'
        for lang in LANGUAGES:
            loc[lang][desc] = m.get('description',{}).get(lang,'') or loc[lang]['TSIN_UI_UNAVAILABLE']
        common += [f'type tsin_ui_card_{m["id"]} = vbox {{', 'size = { 258 75 }', 'spacing = 3', 'datacontext = "[Player]"',
                   f'tooltip = "{desc}"',f'text_single = {{ fontsize = 13 text = "{key}" }}',value_widget(m),
                   f'text_single = {{ fontsize = 10 text = "TSIN_UI_{m["frequency"].upper()}" }}','}']
    for history in data.get('histories',[]):
        id=history['id']; m=by_id[id]
        common += [f'type tsin_ui_history_{id} = vbox {{', 'spacing = 4',f'text_single = {{ fontsize = 16 text = "TSIN_UI_METRIC_{id.upper()}" }}']
        for i in reversed(range(history['samples'])):
            var=history['value_prefix']+str(i); year=history['year_prefix']+str(i)
            formatter(f'{id}_sample_{i}',var)
            common += ['hbox = {','spacing = 8',f'visible = "[{is_set(year)}]"',
                       f'text_single = {{ size = {{ 48 20 }} text = "[{variable(year)}.GetValue|0]" }}',
                       'progressbar = { size = { 230 12 } min = 0 max = 1 using = progressbar_bar_small',
                       f'value = "[Divide_float(FixedPointToFloat({variable(var)}.GetValue), Max_float(FixedPointToFloat({variable(history["peak_variable"])}.GetValue), \'(float)1\'))]" }}',
                       f'text_single = {{ size = {{ 105 20 }} text = "[Player.Custom(\'tsin_ui_format_{id}_sample_{i}\')]" }}','}']
        common += ['text_single = { maximumsize = { 430 -1 } multiline = yes text = "TSIN_UI_HISTORY_NOTE" }','}']
    # Stable compatibility alias for pre-existing Glorp tooltip callers.
    common += ['type tsin_gdp_history_tooltip = SimpleContextualTooltipType {', 'blockoverride "title_icon" {}',
               'blockoverride "title_text" { text = "TSIN_UI_METRIC_GDP" }',
               'blockoverride "tooltip_content" { tsin_ui_history_gdp = {} }','}']
    common += ['type tsin_ui_compact_strip = vbox {','size = { 430 60 }','margin_left = 15','spacing = 0']
    compact=data.get('compact_metrics',[])
    for offset in range(0,len(compact),4):
        common += ['hbox = { spacing = 4']
        for id in compact[offset:offset+4]:
            m=by_id[id]
            icons = {
                'gdp':'map_modes/tax_base', 'gdp_per_capita':'map_modes/tsin_gdp_per_capita',
                'secondary':'buildings/tsin_public_school', 'higher':'buildings/tsin_research_university',
                'growth':'map_modes/tsin_urbanization', 'industry':'map_modes/tsin_industrialization',
                'labor':'map_modes/tsin_labor_unrest', 'stock':'map_modes/tsin_corporations'}
            tip='tsin_ui_compact_tip_'+id
            common += [f'hbox = {{ size = {{ 100 30 }} spacing = 3 datacontext = "[Player]" alwaystransparent = no',
                f'icon = {{ size = {{ 25 25 }} texture = "gfx/interface/icons/{icons[id]}.dds" }}',value_widget(m,True),
                'tooltipwidget = { '+('tsin_gdp_history_tooltip' if id=='gdp' else tip)+' = {} }','}']
        common += ['}']
    common += ['}']
    for id in compact:
        if id=='gdp':continue
        m=by_id[id]
        common += [f'type tsin_ui_compact_tip_{id} = SimpleContextualTooltipType {{',
            'blockoverride "title_icon" {}',f'blockoverride "title_text" {{ text = "TSIN_UI_METRIC_{id.upper()}" }}',
            'blockoverride "tooltip_content" { vbox = { spacing = 5',value_widget(m),
            f'text_single = {{ maximumsize = {{ 420 -1 }} multiline = yes text = "TSIN_UI_HELP_{id.upper()}" }}',
            f'text_single = {{ text = "TSIN_UI_{m["frequency"].upper()}" }}','} } }']
    common += ['}']
    guis=['# GENERATED read-only predicates; no gameplay effects.']
    for s in statuses:
        guis += [f'tsin_ui_check_{s["id"]} = {{','scope = country','is_shown = { always = yes }',f'is_valid = {{ {s["condition"]} }}','}']
        title('STATUS',s)
        key='TSIN_UI_STATUS_HELP_'+s['id'].upper()
        localized(key,s['description']['english'],s['description']['korean'])
    crises=[s for s in statuses if s['tab']=='crises']
    guis += ['tsin_ui_check_no_crises = {','scope = country','is_shown = { always = yes }','is_valid = { NOT = { OR = {']+[s['condition'] for s in crises]+['} } }','}']
    ui=['# GENERATED by tools/gen_dashboard.py; independent of Glorp and Cheat Menu.', 'window = {','name = "tsin_dashboard_dock"','layer = topbar','parentanchor = left|bottom','widgetanchor = left|bottom','position = { 16 -110 }','size = { 420 110 }','movable = yes','allow_outside = yes','visible = "[GetPlayer.IsValid]"','datacontext = "[GetPlayer]"','vbox = { spacing = 4','hbox = { spacing = 4',
        action_button('TSIN_UI_OPEN',[f"GetVariableSystem.Toggle('{open_var}')",f"GetVariableSystem.Set('{tab_var}', 'overview')"],150),
        'tsin_ops_button = {}',
        action_button('TSIN_UI_DOCK',["GetVariableSystem.Toggle('tsin_ui_dock_expanded')"],150),'}',
        'vbox = { visible = "[GetVariableSystem.Exists(\'tsin_ui_dock_expanded\')]" spacing = 3']
    for offset in range(0,len(data['tabs']),3):
        ui += ['hbox = { spacing = 3']
        for tab in data['tabs'][offset:offset+3]: ui.append(action_button('TSIN_UI_TAB_'+tab['id'].upper(),open_tab(tab['id']),100))
        ui += ['}']
    ui += ['}','}','}', 'window = {','name = "tsin_dashboard_window"','layer = topbar','parentanchor = center','widgetanchor = center','size = { 900 660 }','movable = yes','allow_outside = yes','datacontext = "[GetPlayer]"',f'visible = "[And(GetPlayer.IsValid, GetVariableSystem.Exists(\'{open_var}\'))]"','widget = { size = { 100% 100% } using = bg_window_default_alt }',
           'widget = { parentanchor = right position = { -8 8 } size = { 40 40 } button_close_alt = { blockoverride "close_on_action" {',f'on_action = "[GetVariableSystem.Clear(\'{open_var}\')]"','} } }',
           'vbox = { position = { 24 20 } spacing = 10','text_single = { fontsize = 22 text = "TSIN_UI_TITLE" }',
           'hbox = { spacing = 8','text_single = { text = "TSIN_UI_DATE" }',
           f'text_single = {{ visible = "[{is_set("tsin_statistics_year")}]" text = "[{variable("tsin_statistics_year")}.GetValue|0]" }}',
           f'text_single = {{ visible = "[Not({is_set("tsin_statistics_year")} )]" text = "TSIN_UI_NO_DATE" }}','}', 'hbox = { spacing = 4']
    for tab in data['tabs']: ui.append(action_button('TSIN_UI_TAB_'+tab['id'].upper(),open_tab(tab['id']),136))
    ui += ['}', 'text_single = { maximumsize = { 840 -1 } multiline = yes fontsize = 12 text = "TSIN_UI_GUIDE" }',
           'scrollarea = { size = { 850 450 } scrollbarpolicy_horizontal = always_off scrollbar_vertical = { using = Scrollbar_Vertical } scrollwidget = { vbox = { spacing = 8']
    for tab in data['tabs']:
        id=tab['id']; ui += [f'vbox = {{ visible = "[{selected(id)}]" spacing = 10']
        help_key={'society':'SOCIETY_HELP','economy':'ECONOMY_HELP','finance':'FINANCE_HELP','research':'RESEARCH_HELP'}.get(id)
        if help_key: ui += [f'text_single = {{ maximumsize = {{ 820 -1 }} multiline = yes text = "TSIN_UI_{help_key}" }}']
        subset=[m for m in metrics if id in m['tabs']]
        for offset in range(0,len(subset),3):
            ui += ['hbox = { spacing = 12']+[f'tsin_ui_card_{m["id"]} = {{}}' for m in subset[offset:offset+3]]+['}']
        for h in data.get('histories',[]):
            if h['tab']==id: ui += [f'tsin_ui_history_{h["id"]} = {{}}']
        for s in statuses:
            if s['tab']!=id: continue
            visible = f'visible = "[{gate(s["id"])}]"' if id=='crises' else ''
            ui += ['vbox = { spacing = 3',visible,f'text_single = {{ fontsize = 16 text = "TSIN_UI_STATUS_{s["id"].upper()}" }}',
                   f'text_single = {{ visible = "[{gate(s["id"])}]" text = "TSIN_UI_{"ACTIVE" if id=="crises" else "MET"}" }}']
            if id!='crises': ui += [f'text_single = {{ visible = "[Not({gate(s["id"])})]" text = "TSIN_UI_NOT_MET" }}']
            ui += [f'text_single = {{ maximumsize = {{ 800 -1 }} multiline = yes fontsize = 12 text = "TSIN_UI_STATUS_HELP_{s["id"].upper()}" }}','}']
        if id=='crises': ui += [f'text_single = {{ visible = "[{gate("no_crises")}]" text = "TSIN_UI_NO_CRISIS" }}']
        for s in shortcuts:
            if s['tab']!=id: continue
            key=title('LINK',s)
            close=f"GetVariableSystem.Clear('{open_var}')"
            if 'view' in s: ui.append(action_button(key,[f"OpenLateralView('{s['view']}')",close],220))
            else:
                ui += [f'widget = {{ size = {{ 220 30 }} datacontext = "[GetMapMode(\'{s["map_mode"]}\')]"',action_button(key,['MapMode.SetMapMode',close],220),'}']
        ui += ['}']
    ui += ['} } }','}','}']
    version=data['schema_version']
    effects=['# GENERATED dashboard metadata. Calculation providers belong to era modules.',
             'tsin_dashboard_migrate_effect = {',
             'if = { limit = { NOT = { has_variable = tsin_dashboard_data_version } } set_variable = { name = tsin_dashboard_data_version value = 0 } }',
             f'if = {{ limit = {{ var:tsin_dashboard_data_version < {version} }}']
    for module in data['modules']:
        if 'migration_effect' in module: effects.append(module['migration_effect']+' = yes')
    effects += [f'set_variable = {{ name = tsin_dashboard_data_version value = {version} }}','}','}',
                'tsin_dashboard_update_effect = {','tsin_dashboard_migrate_effect = yes',
                'set_variable = { name = tsin_statistics_year value = current_year }',
                'set_variable = { name = tsin_statistics_population value = total_population }']
    for module in data['modules']:
        if 'annual_effect' in module:
            effects.append(f'if = {{ limit = {{ {module.get("update_trigger","always = yes")} }} {module["annual_effect"]} = yes }}')
    effects += ['}']
    hooks=f'''# GENERATED lightweight migration for existing saves; no forced recomputation.
monthly_country_pulse = {{ on_actions = {{ tsin_dashboard_migration_pulse }} }}
tsin_dashboard_migration_pulse = {{
    trigger = {{
        has_variable = tsin_gdp
        OR = {{
            NOT = {{ has_variable = tsin_dashboard_data_version }}
            var:tsin_dashboard_data_version < {version}
        }}
    }}
    effect = {{ tsin_dashboard_migrate_effect = yes }}
}}
'''
    output={
        'in_game/gui/tsin_dashboard_common.gui':'\n'.join(common)+'\n',
        'in_game/gui/tsin_dashboard.gui':'\n'.join(ui)+'\n',
        'in_game/common/scripted_guis/tsin_dashboard_predicates.txt':'\n'.join(guis)+'\n',
        'in_game/common/customizable_localization/tsin_dashboard_formatters.txt':'\n'.join(custom)+'\n',
        'in_game/common/scripted_effects/tsin_dashboard_core_effects.txt':'\n'.join(effects)+'\n',
        'in_game/common/on_action/tsin_dashboard_on_actions.txt':hooks,
    }
    windows=pdx.top_level_blocks(output['in_game/gui/tsin_dashboard.gui'])
    assert len(windows)==2 and all(w.key=='window' for w in windows)
    output['in_game/gui/tsin_dashboard_dock.gui']='# GENERATED registered dock.\n'+windows[0].text+'\n'
    output['in_game/gui/tsin_dashboard.gui']='# GENERATED registered management window.\n'+windows[1].text+'\n'
    output['in_game/gui/scripted_widgets/tsin_windows.txt']='\n'.join([
        'gui/tsin_dashboard_dock.gui = tsin_dashboard_dock',
        'gui/tsin_dashboard.gui = tsin_dashboard_window',
        'gui/tsin_operational.gui = tsin_ops_window'])+'\n'
    for lang,values in loc.items():
        output[f'main_menu/localization/{lang}/tsin_dashboard_l_{lang}.yml'] = f'l_{lang}:\n'+''.join(f' {key}: {json.dumps(value,ensure_ascii=False)}\n' for key,value in values.items())
    return output


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    data=json.loads(pdx.read_text(pdx.MOD_ROOT/REGISTRY))
    result=build(data)
    mismatches=[]
    for rel,text in result.items():
        p=pdx.MOD_ROOT/rel
        if args.check:
            if not p.exists() or pdx.read_text(p)!=text: mismatches.append(rel)
        else: pdx.write_text_bom(p,text)
    for rel in mismatches: print('OUTDATED',rel)
    print(f'{len(result)} generated files; {len(mismatches)} mismatches')
    return bool(mismatches)


if __name__=='__main__':
    raise SystemExit(main())
