"""Finance navigation built around the native credit controller, not a new engine view."""
import json
import re
import pdx

CREDIT = 'in_game/gui/credit.gui'
STOCK = "LateralView.Vars.HasValue('subtab', 'tsin_stocks')"
OVERVIEW = "LateralView.Vars.HasValue('subtab', 'tsin_finance_overview')"
FINANCE = f"Or(IsLateralViewOpened('credit'), And(IsLateralViewOpened('economy'), {STOCK}))"
NATIVE_CREDIT = f'Not(Or({STOCK}, {OVERVIEW}))'


def patch_tabs(text):
    anchor = 'template economy_main_tabs {'
    if text.count(anchor) != 1 or 'TSIN_FINANCE_TAB' in text:
        raise ValueError('economy tabs changed or already patched')
    opening = text.index('{', text.index(anchor))
    end = pdx.matching_brace(pdx.strip_comments(text), opening)
    body = text[opening + 1:end]
    for old in ["[OpenLateralView('economy')]", "[OpenLateralView('credit')]", 'text = "lateralview_credit_entry_name"']:
        if body.count(old) != 1:
            raise ValueError('native economy/credit entry changed: ' + old)
    body = body.replace("[IsLateralViewOpened('economy')]", f"[And(IsLateralViewOpened('economy'), Not({STOCK}))]")
    body = body.replace("[Not(IsLateralViewOpened('economy'))]", f"[Not(And(IsLateralViewOpened('economy'), Not({STOCK})))]")
    body = body.replace("[OpenLateralView('economy')]", "[OpenLateralViewWithParams('economy', 'subtab = balance')]")
    body = body.replace("IsLateralViewOpened('credit')", FINANCE)
    body = body.replace("[OpenLateralView('credit')]", "[OpenLateralViewWithParams('credit', 'subtab = tsin_finance_overview')]")
    body = body.replace('text = "lateralview_credit_entry_name"', 'text = "TSIN_FINANCE_TAB"')
    body, count = re.subn(r'tooltipwidget\s*=\s*\{\s*using\s*=\s*SubTabCreditTooltip\s*\}', 'tooltip = "TSIN_FINANCE_HELP"', body)
    if count != 1:
        raise ValueError('native credit tooltip changed')
    return text[:opening + 1] + body + text[end:]


def panel_body(text):
    anchor = 'blockoverride "panel_content" {'
    if text.count(anchor) != 1:
        raise ValueError('expected exactly one panel_content')
    opening = text.index('{', text.index(anchor))
    end = pdx.matching_brace(pdx.strip_comments(text), opening)
    content = text[opening + 1:end]
    if content.count('using = economy_main_tabs') != 1:
        raise ValueError('native economy tab connection changed')
    return opening, end, content


def patch_economy(text):
    opening, end, content = panel_body(text)
    anchor = '\n\t\tvbox = {\n\t\t\tusing = layoutpolicy_expanding'
    if content.count(anchor) != 1 or 'tsin_stock_panel = {' in content:
        raise ValueError('economy body changed or already patched')
    extra = f'\n\t\ttsin_finance_tabs = {{ visible = "[{STOCK}]" }}\n\t\ttsin_stock_panel = {{ visible = "[{STOCK}]" }}\n'
    content = content.replace(anchor, extra + '\n\t\tvbox = {\n' + f'\t\t\tvisible = "[Not({STOCK})]"\n\t\t\tusing = layoutpolicy_expanding', 1)
    return text[:opening + 1] + content + text[end:]


def patch_credit(text):
    opening, end, content = panel_body(text)
    anchor = '\n\t\tvbox = {\n\t\t\tusing = layoutpolicy_expanding'
    if content.count(anchor) != 1 or 'tsin_finance_tabs = {' in content:
        raise ValueError('credit body changed or already patched')
    extra = '\n\t\ttsin_finance_tabs = {}\n'
    extra += f'\t\ttsin_finance_overview = {{ visible = "[{OVERVIEW}]" }}\n'
    extra += f'\t\ttsin_stock_panel = {{ visible = "[{STOCK}]" }}\n'
    content = content.replace(anchor, extra + '\n\t\tvbox = {\n' + f'\t\t\tvisible = "[{NATIVE_CREDIT}]"\n\t\t\tusing = layoutpolicy_expanding', 1)
    return text[:opening + 1] + content + text[end:]


def build(game=None):
    game = game or pdx.game_root()
    labels = {language: {} for language in ['english', 'korean']}

    def loc(key, en, ko):
        name = 'TSIN_FINANCE_' + key
        labels['english'][name] = en
        labels['korean'][name] = ko
        return name

    loc('TAB', 'Finance', '금융')
    loc('HELP', 'Financial overview, companies and the existing loan and bond controls.', '금융 현황·증시·기존 대출 및 채권 기능을 확인합니다.')
    loc('OVERVIEW', 'Overview', '현황')
    loc('STOCKS', 'Stocks', '증시')
    loc('CREDIT', 'Credit', '신용')
    loc('TREASURY', 'Treasury · reference ducats', '국고 · 기준 두캇')
    loc('DEBT', 'Outstanding principal', '차입 원금')
    loc('COST', 'Monthly loan payments', '월간 차입 지급액')
    loc('INFLATION', 'Inflation', '인플레이션')
    loc('FIRMS', 'Established firms', '설립 기업 수')
    loc('ENTRY', 'Excess-entry streak · quarters / 3', '과잉 진입 연속 분기 / 3')
    loc('SUPPLY', 'Severe oversupply streak · quarters / 4', '심각한 과잉공급 연속 분기 / 4')
    loc('MISSING', 'No sample recorded', '미관측')
    loc('NOTE', 'Treasury and debt are native accounts; the stock panel uses valuation indices. Streaks are stored quarterly observations, not a complete bank solvency or liquidity model. Use Credit for existing loans, bonds, repayments and bankruptcy.', '국고와 부채는 게임의 실제 장부이며 증시는 평가 지수입니다. 위험 지속치는 저장된 분기 관측값으로 은행의 지급 능력·유동성 전체를 나타내지 않습니다. 대출·채권·상환·파산은 신용에서 조작합니다.')
    ui = ['# GENERATED by tools/finance_ui.py through gen_stock_market_ui.py.', 'types TSINFinance {',
          'type tsin_finance_tabs = header_secondary_tabs { blockoverride "content" {']
    for name, predicate, subtab in [('OVERVIEW', OVERVIEW, 'tsin_finance_overview'), ('STOCKS', STOCK, 'tsin_stocks'), ('CREDIT', NATIVE_CREDIT, 'credit')]:
        ui += ['button_secondary_tab_alt = { using = layoutpolicy_expanding',
               f'down = "[{predicate}]"', f'blockoverride "text" {{ text = "TSIN_FINANCE_{name}" }}',
               'blockoverride "on_action_left" {',
               'on_action = "[GetScriptedGui(\'tsin_stock_ui_seed\').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]"' if name == 'STOCKS' else '',
               f'on_action = "[OpenLateralViewWithParams(\'credit\', \'subtab = {subtab}\')]"', '}', '}']
    ui += ['} }', 'type tsin_finance_overview = vbox { using = layoutpolicy_expanding using = bg_main_inner_alt using = window_main_tabs_margin_alt spacing = 10',
           'text_single = { fontsize = 22 text = "TSIN_FINANCE_TAB" }']
    values = [('TREASURY', "GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('tsin_finance_treasury')|1L"),
              ('DEBT', 'Player.GetEconomy.GetTotalDebt|1L'), ('COST', 'CreditLateralView.GetTotalLoansTakenMonthlyCost|2'),
              ('INFLATION', "GetPlayer.GetFixedPointCurrencyValue('inflation')|2%"),
              ('FIRMS', "GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('tsin_company_count')|0")]
    for name, value in values:
        ui += [f'hbox = {{ spacing = 12 text_single = {{ size = {{ 300 26 }} text = "TSIN_FINANCE_{name}" }} text_single = {{ text = "[{value}]" }} }}']
    for name, variable in [('ENTRY', 'tsin_entry_risk_quarters'), ('SUPPLY', 'tsin_stress_quarters')]:
        var = f"GetPlayer.MakeScope.GetVariable('{variable}')"
        ui += [f'hbox = {{ spacing = 12 text_single = {{ size = {{ 300 26 }} text = "TSIN_FINANCE_{name}" }}',
               f'text_single = {{ visible = "[{var}.IsSet]" text = "[{var}.GetValue|0]" }}',
               f'text_single = {{ visible = "[Not({var}.IsSet)]" text = "TSIN_FINANCE_MISSING" }}', '}']
    ui += ['text_single = { maximumsize = { 520 -1 } multiline = yes text = "TSIN_FINANCE_NOTE" }', '}', '}']
    result = {CREDIT: '# GENERATED finance host; native credit content and controller retained.\n' + patch_credit(pdx.read_text(game / CREDIT)),
              'in_game/gui/tsin_finance.gui': '\n'.join(ui) + '\n',
              'in_game/common/script_values/tsin_finance_values.txt': 'tsin_finance_treasury = { value = gold }\n'}
    for language, entries in labels.items():
        result[f'main_menu/localization/{language}/tsin_finance_l_{language}.yml'] = 'l_' + language + ':\n' + '\n'.join(' ' + key + ': ' + json.dumps(value, ensure_ascii=False) for key, value in entries.items()) + '\n'
    return result
