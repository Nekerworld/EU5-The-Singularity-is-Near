"""Icon-led stock panel shared by vanilla and Glorp economy views."""
import json
from gen_capital_markets import all_companies


def extend(result):
    rows=all_companies();labels={'english':{},'korean':{}}
    def loc(key,en,ko):
        key='TSIN_CAP_'+key
        labels['english'][key]=en;labels['korean'][key]=ko
        return key
    def var(name):return f"GetPlayer.MakeScope.GetVariable('{name}')"
    def val(name):return var(name)+'.GetValue'
    def isset(name):return var(name)+'.IsSet'
    def gui(name):return f"GetScriptedGui('{name}').IsValid(GuiScope.SetRoot(GetPlayer.MakeScope).End)"
    def button(label,action,enabled=None,width=140):
        return '\n'.join([f'button_regular = {{ size = {{ {width} 28 }}',f'enabled = "[{enabled}]"' if enabled else '',
            f'action_tooltip = {{ title = "{label}" on_action = "[{action}]" }}',
            f'text_single = {{ size = {{ {width-8} 26 }} parentanchor = center align = center|nobaseline fontsize = 12 autoresize = no fontsize_min = 9 text = "{label}" }}','}'])
    loc('INDEX','Company index','기업·주가 지수');loc('COUNT','Firms','기업 수');loc('LIMIT','Company capacity','기업 한도')
    loc('PRIVATE','Private entry · no policy cap','민간 자율 진입 · 정책상 무제한')
    loc('PUBLIC','Public founding / licensed entry','국가 투자·인가 진입')
    loc('LAW','Economic regime','기업 경제체제');loc('FOUND','Found / expand','설립·확장');loc('HQ','Headquarters','본사')
    loc('PRICE','Share / business valuation index','주가·기업 평가 지수');loc('ASSETS','Business base · cached','영업 기반 · 집계치')
    loc('VALUE','Estimated company value','기업 가치 추정치');loc('COST','Public investment cost','국가 투자 비용')
    loc('FORM_HELP','Requires technology/year/country conditions, a non-laissez-faire regime, treasury and spare capacity. Private firms instead spend burgher capital automatically.','기술·연도·국가 조건, 자유방임 이외 체제, 국고와 한도 여유가 필요합니다. 자유방임 기업은 시민 자금으로 자동 진입합니다.')
    loc('GENERIC','Merchant houses and generic businesses','상단과 일반 기업');loc('NATIONAL','Historical national organizations','국가 고유 기업·상인 조직');loc('INDUSTRIAL','Industrial companies','산업 기업')
    loc('CHART_NOTE','Oldest → newest observations. Quarterly, with gaps while the exchange is closed. This is an index, not treasury gold.','과거 → 최근 관측값. 통상 분기별이며 거래소 폐쇄 시 간격이 늘어납니다. 국고 금액이 아닌 지수입니다.')
    loc('NO_HISTORY','No recorded stock observations yet. Found a company, then wait for its quarterly update.','아직 주가 관측 기록이 없습니다. 기업 설립 후 분기 갱신부터 기록됩니다.')
    loc('HELP','Groups can contain multiple private firms. Historical names are unique. Early merchant organizations are an abstraction, not a claim that medieval joint-stock exchanges existed. Values use cached business bases.','일반 업종에는 여러 민간 기업이 속할 수 있고 역사적 고유 조직은 하나입니다. 초기 상단의 지수는 기업 평가의 추상화이며 중세에 현대 주식거래소가 존재했다는 뜻은 아닙니다. 가치는 저장된 영업 기반을 사용합니다.')
    loc('RISK','Risk diagnostics','금융 위험 진단')
    loc('CAPACITY','Estimated sustainable business base','추정 적정 기업 수')
    loc('ENTRY_STREAK','Consecutive quarters of excessive entry (crash threshold: 3)','과잉 진입 연속 분기 (붕괴 기준 3)')
    loc('SUPPLY_STREAK','Consecutive quarters of severe excess supply (crash threshold: 4)','심각한 과잉공급 연속 분기 (붕괴 기준 4)')
    loc('RISK_HELP','Oversupply: at least two sampled capital-market goods with supply >=150% of demand and price <=65% of reference for four quarters. Excess-entry bubbles: firms >150% of estimated business capacity for three quarters, at least six firms. World contagion needs additional 1900+ multi-market thresholds.','과잉공급: 수도 시장 표본 중 상품 2종 이상이 수요 대비 공급 150%·기준가 65% 이하로 4분기 지속. 과잉 진입: 기업 6개 이상이고 추정 영업 기반의 150%를 초과한 상태가 3분기 지속. 세계 전염에는 1900년 이후의 다국가·다시장 조건이 추가로 필요합니다.')
    loc('MISSING','—','—')
    ui=['# GENERATED icon-led capital market. Economy entry points are generated separately.',
        'types TSINStockMarket { type tsin_stock_panel = vbox { using = layoutpolicy_expanding using = bg_main_inner_alt using = window_main_tabs_margin_alt datacontext = "[GetPlayer]" spacing = 6',
        # The graph stays above the scrollable company list, matching the economy balance view.
        'widget = { size = { 530 260 } using = bg_text_mask_container_dark_brown',
        'vbox = { position = { 8 6 } spacing = 5',
        'hbox = { spacing = 8 icon = { size = { 25 25 } texture = "gfx/interface/icons/map_modes/tsin_corporations.dds" }',
        'text_single = { fontsize = 14 text = "TSIN_CAP_INDEX" }',
        f'text_single = {{ visible = "[{isset("tsin_stock_index")}]" fontsize = 20 text = "[{val("tsin_stock_index")}|1]" }}',
        f'text_single = {{ visible = "[Not({isset("tsin_stock_index")})]" text = "TSIN_CAP_MISSING" }}','}',
        'widget = { size = { 510 180 }']
    for y in [5,45,85,125,165]:
        ui += [f'icon = {{ position = {{ 0 {y} }} size = {{ 510 1 }} texture = "gfx/interface/textures/tsin_solid_white.dds" alpha = 0.12 alwaystransparent = yes }}']
    peak="GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('tsin_stock_ui_peak')"
    def height(i):return f"Subtract_float('(float)165', Multiply_float(Divide_float(FixedPointToFloat({val('tsin_index_h'+str(i))}), FixedPointToFloat({peak})), '(float)155'))"
    # Native line widgets require engine-owned point-list glue. Draw a sampled
    # connected line with ordinary icon rectangles and the native ToVector2f
    # binding instead of inventing a dynamic array API. No world data is read.
    for j in range(7):
        a,b=7-j,6-j
        def interpolate(t):
            return f"Add_float(Multiply_float({height(a)}, '(float){1-t:g}'), Multiply_float({height(b)}, '(float){t:g}'))"
        for step in range(8):
            x=j*72+step*9;ya,yb=interpolate(step/8),interpolate((step+1)/8)
            common=f'visible = "[And({isset("tsin_index_h"+str(a))}, {isset("tsin_index_h"+str(b))})]" texture = "gfx/interface/textures/tsin_solid_white.dds" color = {{ 0.25 0.85 0.42 1 }} alwaystransparent = yes'
            ui += [f'''icon = {{ {common} position = "[ToVector2f('(float){x}', {ya})]" size = {{ 10 2 }} }}''',
                f'''icon = {{ {common} position = "[ToVector2f('(float){x+9}', Min_float({ya}, {yb}))]"
size = "[ToVector2f('(float)2', Add_float(Subtract_float(Max_float({ya}, {yb}), Min_float({ya}, {yb})), '(float)2'))]" }}''']
    for j in range(8):
        i=7-j
        ui += [f'''icon = {{ visible = "[{isset('tsin_index_h'+str(i))}]" position = "[ToVector2f('(float){j*72}', {height(i)})]"
size = {{ 4 4 }} texture = "gfx/interface/textures/tsin_solid_white.dds" color = {{ 0.25 0.85 0.42 1 }}
tooltip = "[{val('tsin_index_h'+str(i))}|1]" }}''']
    ui += [f'text_single = {{ visible = "[Not({isset("tsin_index_h0")})]" maximumsize = {{ 490 -1 }} multiline = yes text = "TSIN_CAP_NO_HISTORY" }}',
        '}', 'text_single = { maximumsize = { 510 -1 } multiline = yes fontsize = 10 text = "TSIN_CAP_CHART_NOTE" }','}','}',
        'hbox = { spacing = 8 icon = { size = { 24 24 } texture = "gfx/interface/icons/map_modes/tsin_corporations.dds" }',
        'text_single = { text = "TSIN_CAP_COUNT" }',
        'text_single = { text = "[GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue(\'tsin_company_count\')|0]" }',
        f'text_single = {{ visible = "[{gui("tsin_capital_is_private")}]" text = "∞" tooltip = "TSIN_CAP_PRIVATE" }}',
        f'text_single = {{ visible = "[Not({gui("tsin_capital_is_private")})]" text = "/ [GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue(\'tsin_company_limit\')|0]" tooltip = "TSIN_CAP_LIMIT" }}','}',
        'hbox = { spacing = 6',button('TSIN_CAP_LAW',"OpenLateralView('laws')"),
        'text_single = { alwaystransparent = no text = "TSIN_CAP_RISK" tooltip = "TSIN_CAP_RISK_HELP" }','}',
        'hbox = { spacing = 10',
        'text_single = { text = "[GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue(\'tsin_sustainable_firms\')|1]" tooltip = "TSIN_CAP_CAPACITY" }',
        f'text_single = {{ visible = "[{isset("tsin_entry_risk_quarters")}]" text = "[{val("tsin_entry_risk_quarters")}|0] / 3" tooltip = "TSIN_CAP_ENTRY_STREAK" }}',
        f'text_single = {{ visible = "[{isset("tsin_stress_quarters")}]" text = "[{val("tsin_stress_quarters")}|0] / 4" tooltip = "TSIN_CAP_SUPPLY_STREAK" }}','}',
        'scrollarea = { using = layoutpolicy_expanding scrollbarpolicy_horizontal = always_off scrollbar_vertical = { using = Scrollbar_Vertical } scrollwidget = { vbox = { spacing = 8']
    industrial_en=['Steel company','Machinery company','Textile company','Chemical company','Railway company','Farm machinery company']
    industrial_ko=['강철 회사','기계 회사','직물 회사','화학 회사','철도 회사','농기계 회사']
    for kind in ['generic','national','industrial']:
        ui += [f'text_single = {{ fontsize = 17 text = "TSIN_CAP_{kind.upper()}" }}']
        for row in [r for r in rows if r['kind']==kind]:
            c=row['id'];cost=row.get('cost',2)
            if kind=='industrial':
                k=[r['id'] for r in rows if r['kind']=='industrial'].index(c)
                en,ko=industrial_en[k],industrial_ko[k]
            else:en,ko=row['english'],row['korean']
            title=loc('COMPANY_'+c.upper(),en,ko)
            price=val('tsin_stock_'+c)
            quantity=f"GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue('tsin_firm_number_{c}')"
            assets=val('tsin_stock_ui_levels_'+c)
            value=f'Multiply_CFixedPoint(Multiply_CFixedPoint({price}, {assets}), {quantity})'
            ui += [f'vbox = {{ visible = "[{gui("tsin_capital_visible_"+c)}]" using = bg_paper_card margin = {{ 7 7 }} spacing = 4',
                f'hbox = {{ spacing = 8 icon = {{ size = {{ 36 36 }} texture = "gfx/interface/icons/trade_goods/icon_goods_{row["icon"]}.dds" }}',
                f'text_single = {{ size = {{ 350 30 }} autoresize = no fontsize = 16 fontsize_min = 11 text = "{title}" }}','}',
                f'hbox = {{ visible = "[{gui("tsin_capital_listed_"+c)}]" spacing = 12',
                'icon = { size = { 20 20 } texture = "gfx/interface/icons/map_modes/tsin_corporations.dds" tooltip = "TSIN_CAP_COUNT" }',
                f'text_single = {{ text = "[{quantity}|0]" tooltip = "TSIN_CAP_COUNT" }}',
                'icon = { size = { 20 20 } texture = "gfx/interface/icons/map_modes/tax_base.dds" tooltip = "TSIN_CAP_PRICE" }',
                f'text_single = {{ text = "[{price}|1]" tooltip = "TSIN_CAP_PRICE" }}',
                'icon = { size = { 20 20 } texture = "gfx/interface/icons/map_modes/tsin_gdp_per_capita.dds" tooltip = "TSIN_CAP_VALUE" }',
                f'text_single = {{ text = "[{value}|1L]" tooltip = "TSIN_CAP_VALUE" }}','}',
                'hbox = { spacing = 6',
                button('TSIN_CAP_FOUND',f"GetScriptedGui('tsin_capital_form_{c}').Execute(GuiScope.SetRoot(GetPlayer.MakeScope).End)",gui('tsin_capital_form_'+c)),
                f'text_single = {{ text = "[GuiScope.SetRoot(GetPlayer.MakeScope).ScriptValue(\'tsin_gold_cost_{cost}\')|1] @gold!" tooltip = "TSIN_CAP_FORM_HELP" }}',
                f'widget = {{ size = {{ 145 28 }} datacontext = "[{var("tsin_hq_"+c)}.GetLocation]"',
                button('TSIN_CAP_HQ','ShowLocation(Location.Self)','Location.IsValid'),'}','}','}']
    ui += ['text_single = { maximumsize = { 510 -1 } multiline = yes fontsize = 11 text = "TSIN_CAP_HELP" }','}','}','}','}','}']
    result['in_game/gui/tsin_stock_market.gui']='\n'.join(ui)+'\n'
    s=result['in_game/common/scripted_guis/tsin_stock_market_guis.txt']
    s=s.replace('effect = { tsin_dashboard_age7_migrate_effect = yes }','effect = { tsin_capital_policy_init_effect = yes tsin_init_existing_companies_effect = yes tsin_dashboard_age7_migrate_effect = yes tsin_capital_cache_effect = yes }')
    result['in_game/common/scripted_guis/tsin_stock_market_guis.txt']=s
    for lang in labels:
        path=f'main_menu/localization/{lang}/tsin_stock_ui_l_{lang}.yml'
        result[path]+='\n'.join(' '+key+': '+json.dumps(value,ensure_ascii=False) for key,value in labels[lang].items())+'\n'
    return result
