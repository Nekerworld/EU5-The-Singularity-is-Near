"""Finance navigation built around the native credit controller, not a new engine view."""
import json
import re
import pdx
from gen_finance_ledger import EXTRA_TABS

CREDIT = 'in_game/gui/credit.gui'
STOCK = "LateralView.Vars.HasValue('subtab', 'tsin_stocks')"
OVERVIEW = "LateralView.Vars.HasValue('subtab', 'tsin_finance_overview')"
FINANCE = f"Or(IsLateralViewOpened('credit'), And(IsLateralViewOpened('economy'), {STOCK}))"
EXTRA = "Or(" + "LateralView.Vars.HasValue('subtab', 'tsin_money'), Or(LateralView.Vars.HasValue('subtab', 'tsin_bank'), LateralView.Vars.HasValue('subtab', 'tsin_funds')))"
NATIVE_CREDIT = f'Not(Or({STOCK}, Or({OVERVIEW}, {EXTRA})))'


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
    extra += ''.join(f'\t\t{subtab}_panel = {{ visible = "[LateralView.Vars.HasValue(\'subtab\', \'{subtab}\')]" }}\n' for _, subtab in EXTRA_TABS)
    content = content.replace(anchor, extra + '\n\t\tvbox = {\n' + f'\t\t\tvisible = "[{NATIVE_CREDIT}]"\n\t\t\tusing = layoutpolicy_expanding', 1)
    return text[:opening + 1] + content + text[end:]


ICON_GLOW = (
    'glow = { name = "drop_shadow" glow_radius = 3 '
    'color = { 0.0 0.0 0.0 1.0 } alpha = 0.3 }'
)


def icon_metric(label, value, icon, tooltip=None, *, localize_value=False):
    """Vanilla-style two-line metric row used on the credit overview."""
    tip = f'\ntooltip = "{tooltip}"\ntagtooltip_enabled = yes' if tooltip else ''
    value_line = f'text = "{value}"' if localize_value else f'raw_text = "{value}"'
    return '\n'.join([
        'icon_text_2rows = {',
        f'blockoverride "icon_setup" {{ texture = "{icon}" {ICON_GLOW} }}',
        'blockoverride "top_text_setup" {',
        f'text = "{label}"',
        'default_format = "#explanation_link_overview"',
        '}',
        'blockoverride "bottom_text_setup" {',
        value_line,
        '}',
        tip,
        '}',
    ])


def var_metric(label, variable, icon, fmt='1', missing='TSIN_FINANCE_MISSING'):
    """Metric whose value comes from a country variable, with a missing fallback."""
    var = f"GetPlayer.MakeScope.GetVariable('{variable}')"
    return '\n'.join([
        f'vbox = {{ visible = "[{var}.IsSet]"',
        icon_metric(label, f'[{var}.GetValue|{fmt}]', icon),
        '}',
        f'vbox = {{ visible = "[Not({var}.IsSet)]"',
        icon_metric(label, missing, icon, localize_value=True),
        '}',
    ])


def paper_card(title, body_lines, tooltip=None):
    tip = []
    if tooltip:
        tip = [f'tooltip = "{tooltip}"', 'tagtooltip_enabled = yes']
    return '\n'.join([
        'vbox = {',
        'layoutpolicy_horizontal = expanding',
        'using = bg_paper_card',
        'using = bg_cabinet_card_frame',
        'margin = { 10 8 }',
        'spacing = 6',
        *tip,
        'text_single = {',
        'autoresize = yes',
        'fontsize = 15',
        f'text = "{title}"',
        'default_format = "#yellow_titles"',
        'using = Font_Type_Headers',
        '}',
        *body_lines,
        '}',
    ])


def help_icon(tooltip_key):
    return '\n'.join([
        'button_regular = {',
        'size = { 28 28 }',
        f'tooltip = "{tooltip_key}"',
        'tagtooltip_enabled = yes',
        'text_single = {',
        'size = { 24 24 }',
        'parentanchor = center',
        'autoresize = no',
        'align = center|nobaseline',
        'fontsize = 14',
        'raw_text = "?"',
        '}',
        '}',
    ])


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
    loc('SECTION_TREASURY', 'Treasury', '국고')
    loc('SECTION_DEBT', 'Debt & credit', '부채·신용')
    loc('SECTION_PULSE', 'Economy pulse', '경기 지표')
    loc('TREASURY', 'Treasury cash · ducats', '국고 현금 · 두캇')
    loc('CAPACITY', 'Borrowing capacity', '차입 여력')
    loc('CAPACITY_NA', 'No data. The native borrowing-limit query is not confirmed, so annual income is not used as lendable capacity.', '자료 없음. 네이티브 차입 한도 조회가 확인되지 않아 연간 수입을 대출 가능액으로 쓰지 않습니다.')
    loc('CAPACITY_NOTE', 'Treasury cash and borrowing capacity are separate figures. Reserves, banks, pensions and GDP are not added to treasury cash.', '국고 현금과 차입 여력은 별개의 수치입니다. 준비금·은행·연금·GDP는 국고 현금에 더하지 않습니다.')
    loc('DEBT', 'Outstanding principal', '차입 원금')
    loc('COST', 'Monthly loan payments', '월간 차입 지급액')
    loc('INFLATION', 'Inflation', '인플레이션')
    loc('FIRMS', 'Established firms', '설립 기업 수')
    loc('ENTRY', 'Excess-entry streak · quarters / 3', '과잉 진입 연속 분기 / 3')
    loc('SUPPLY', 'Severe oversupply streak · quarters / 4', '심각한 과잉공급 연속 분기 / 4')
    loc('MISSING', '—', '—')
    loc('BOND_PRINCIPAL', 'Bonds · outstanding principal', '국채 · 잔여 원금')
    loc('DUE_12', 'Loans due in 1–12 months', '향후 1~12개월 만기 대출')
    loc('DUE_NOW', 'Loans at/past maturity', '만기 도래·경과 대출')
    loc('TAX_TRADE_ANNUAL', 'Tax/trade income · annualized', '조세·교역 수입 · 연율 환산')
    loc('DEBT_INCOME_RATIO', 'Debt / annualized income · %', '부채 / 연율 수입 · %')
    loc('PROFILE_NOTE', 'Debt profile: monthly snapshot in reference ducats, excluding TSIN company loans. Bonds are separated from dated loans. At/past maturity does not itself mean default: native renewal and settlement still apply. Annualized income is current monthly tax and trade income × 12, not recorded annual revenue. A missing ratio means no positive income sample.', '부채 요약은 매월 관측한 기준 두캇 값이며 TSIN 기업 대출은 제외합니다. 국채는 만기 대출과 구분합니다. 만기 경과가 곧 채무불이행을 뜻하지 않으며 기본 차환·결제 규칙을 따릅니다. 연율 수입은 현재 월 조세·교역 수입×12로 실제 연간 결산이 아닙니다. 양수 수입 표본이 없으면 비율은 미관측으로 표시합니다.')
    loc('NOTE', 'Treasury and debt are native accounts; the stock panel uses valuation indices. Streaks are stored quarterly observations, not a complete bank solvency or liquidity model. Use Credit for existing loans, bonds, repayments and bankruptcy.', '국고와 부채는 게임의 실제 장부이며 증시는 평가 지수입니다. 위험 지속치는 저장된 분기 관측값으로 은행의 지급 능력·유동성 전체를 나타내지 않습니다. 대출·채권·상환·파산은 신용에서 조작합니다.')
    for name, _ in EXTRA_TABS:
        for lang in labels:
            labels[lang]['TSIN_FINANCE_'+name] = {'MONEY': ('Currency', '통화'), 'BANK': ('Banks', '은행'), 'FUNDS': ('Funds', '기금')}[name][0 if lang == 'english' else 1]

    loc('OVERVIEW_HINT', 'Treasury, debt profile and economy pulse at a glance. Hover cards for notes.', '국고·부채 요약·경기 지표를 한눈에 봅니다. 카드에 마우스를 올리면 설명이 나옵니다.')
    loc('CREDIT_HINT', 'Native loans received and lent, bonds, repayment and bankruptcy.', '받은 대출·빌려준 대출·국채·상환·파산은 이 탭의 기본 대출 화면입니다.')
    ui = [
        '# GENERATED by tools/finance_ui.py through gen_stock_market_ui.py.',
        'types TSINFinance {',
        'type tsin_finance_tabs = vbox {',
        'layoutpolicy_horizontal = expanding',
        'spacing = 6',
        'margin = { 6 4 }',
        # Prominent centered Overview entry
        'hbox = {',
        'layoutpolicy_horizontal = expanding',
        'expand = {}',
        'button_regular = {',
        'size = { 400 60 }',
        'down = "[%s]"' % OVERVIEW,
        'tooltip = "TSIN_FINANCE_OVERVIEW_HINT"',
        'tagtooltip_enabled = yes',
        'action_tooltip = {',
        'title = "TSIN_FINANCE_OVERVIEW"',
        "on_action = \"[OpenLateralViewWithParams('credit', 'subtab = tsin_finance_overview')]\"",
        '}',
        'text_single = {',
        'size = { 390 56 }',
        'parentanchor = center',
        'autoresize = no',
        'maximumsize = { 390 56 }',
        'fontsize = 22',
        'fontsize_min = 16',
        'align = center|nobaseline',
        'elide = right',
        'text = "TSIN_FINANCE_OVERVIEW"',
        'using = Font_Type_Headers',
        '}',
        '}',
        'expand = {}',
        '}',
        'header_secondary_tabs = {',
        'blockoverride "content" {',
    ]
    tab_defs = [
        ('STOCKS', STOCK, 'tsin_stocks'),
        ('CREDIT', NATIVE_CREDIT, 'credit'),
    ] + [(name, f"LateralView.Vars.HasValue('subtab', '{tab}')", tab) for name, tab in EXTRA_TABS]
    for name, predicate, subtab in tab_defs:
        tip = 'TSIN_FINANCE_CREDIT_HINT' if name == 'CREDIT' else 'OPEN_TAB'
        ui += [
            'button_secondary_tab_alt = {',
            'using = layoutpolicy_expanding',
            'tooltip_enabled = no',
            f'down = "[{predicate}]"',
            f'blockoverride "tab_text" {{ text = "TSIN_FINANCE_{name}" }}',
            'action_tooltip = {',
            f'title = "{tip}"',
        ]
        if name == 'STOCKS':
            ui.append(
                "on_action = \"[GetScriptedGui('tsin_stock_ui_seed')"
                ".Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)]\""
            )
        ui += [
            f"on_action = \"[OpenLateralViewWithParams('credit', 'subtab = {subtab}')]\"",
            '}',
            '}',
        ]
    ui += ['}', '}', '}']

    gold = 'gfx/interface/icons/resources/gold.dds'
    debt_icon = 'gfx/interface/icons/flat_icons/balance/debt.dds'
    loan_icon = 'gfx/interface/icons/flat_icons/balance/loan.dds'
    interest_icon = 'gfx/interface/icons/flat_icons/balance/interest.dds'
    bond_icon = 'gfx/interface/icons/flat_icons/balance/government_bond.dds'
    inflation_icon = 'gfx/interface/icons/flat_icons/balance/inflation.dds'
    trade_icon = 'gfx/interface/icons/flat_icons/balance/trade.dds'
    firm_icon = 'gfx/interface/icons/map_modes/tsin_corporations.dds'
    risk_icon = 'gfx/interface/icons/flat_icons/balance/efficiency.dds'

    treasury_card = paper_card('TSIN_FINANCE_SECTION_TREASURY', [
        icon_metric(
            'TSIN_FINANCE_TREASURY',
            "[GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('tsin_finance_treasury')|1L]@gold!",
            gold,
            'TSIN_FINANCE_CAPACITY_NOTE',
        ),
        icon_metric(
            'TSIN_FINANCE_CAPACITY',
            'TSIN_FINANCE_CAPACITY_NA',
            loan_icon,
            'TSIN_FINANCE_CAPACITY_NA',
            localize_value=True,
        ),
    ], tooltip='TSIN_FINANCE_CAPACITY_NOTE')
    debt_card = paper_card('TSIN_FINANCE_SECTION_DEBT', [
        icon_metric('TSIN_FINANCE_DEBT', '[Player.GetEconomy.GetTotalDebt|1L]@gold!', debt_icon, 'TSIN_FINANCE_PROFILE_NOTE'),
        icon_metric('TSIN_FINANCE_COST', '[CreditLateralView.GetTotalLoansTakenMonthlyCost|2]@gold!', interest_icon),
        var_metric('TSIN_FINANCE_BOND_PRINCIPAL', 'tsin_native_bond_principal', bond_icon),
        var_metric('TSIN_FINANCE_DUE_12', 'tsin_native_due_12', loan_icon),
        var_metric('TSIN_FINANCE_DUE_NOW', 'tsin_native_due_now', loan_icon),
        var_metric('TSIN_FINANCE_TAX_TRADE_ANNUAL', 'tsin_native_tax_trade_annual', trade_icon),
        var_metric('TSIN_FINANCE_DEBT_INCOME_RATIO', 'tsin_native_debt_income_ratio', risk_icon),
    ], tooltip='TSIN_FINANCE_PROFILE_NOTE')
    pulse_card = paper_card('TSIN_FINANCE_SECTION_PULSE', [
        icon_metric(
            'TSIN_FINANCE_INFLATION',
            "[GetPlayer.GetFixedPointCurrencyValue('inflation')|2%]",
            inflation_icon,
        ),
        icon_metric(
            'TSIN_FINANCE_FIRMS',
            "[GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('tsin_company_count')|0]",
            firm_icon,
        ),
        var_metric('TSIN_FINANCE_ENTRY', 'tsin_entry_risk_quarters', risk_icon, fmt='0'),
        var_metric('TSIN_FINANCE_SUPPLY', 'tsin_stress_quarters', risk_icon, fmt='0'),
    ], tooltip='TSIN_FINANCE_NOTE')

    ui += [
        'type tsin_finance_overview = scrollarea {',
        'using = layoutpolicy_expanding',
        'scrollbarpolicy_horizontal = always_off',
        'autoresizescrollarea = no',
        'scrollbar_vertical = { using = Scrollbar_Vertical }',
        'scrollwidget = {',
        'vbox = {',
        'using = layoutpolicy_expanding',
        'using = bg_secondary_inner_alt',
        'using = bg_secondary_inner_image_alt',
        'blockoverride "image" { texture = "gfx/interface/economy/bg_credit.dds" }',
        'margin = { 10 12 }',
        'spacing = 12',
        'hbox = {',
        'layoutpolicy_horizontal = expanding',
        'spacing = 10',
        f'icon = {{ size = {{ 36 36 }} texture = "{gold}" }}',
        'text_single = {',
        'autoresize = yes',
        'fontsize = 22',
        'text = "TSIN_FINANCE_TAB"',
        'using = Font_Type_Headers',
        'default_format = "#yellow_titles"',
        '}',
        'expand = {}',
        help_icon('TSIN_FINANCE_NOTE'),
        '}',
        'hbox = {',
        'layoutpolicy_horizontal = expanding',
        'spacing = 8',
        treasury_card,
        pulse_card,
        '}',
        debt_card,
        '}',
        '}',
        '}',
        '}',
    ]

    topbar = pdx.read_text(game / 'in_game/gui/ingame_topbar.gui')
    if topbar.count('@left_panel_width = 570') != 1:
        raise ValueError('left panel width anchor missing or duplicated')
    topbar = topbar.replace('@left_panel_width = 570', '@left_panel_width = 780', 1)

    result = {
        CREDIT: '# GENERATED finance host; native credit content and controller retained.\n'
        + patch_credit(pdx.read_text(game / CREDIT)),
        'in_game/gui/tsin_finance.gui': '\n'.join(ui) + '\n',
        'in_game/common/script_values/tsin_finance_values.txt': 'tsin_finance_treasury = { value = gold }\n',
        'in_game/gui/ingame_topbar.gui': (
            '# GENERATED finance UI: wider left lateral panel for readable finance tabs.\n' + topbar
        ),
    }
    for language, entries in labels.items():
        result[f'main_menu/localization/{language}/tsin_finance_l_{language}.yml'] = (
            'l_' + language + ':\n'
            + '\n'.join(' ' + key + ': ' + json.dumps(value, ensure_ascii=False) for key, value in entries.items())
            + '\n'
        )
    return result
