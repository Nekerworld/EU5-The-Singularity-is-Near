"""Always-on mod log: self-checks, action hooks and a numeric snapshot written with debug_log (docs/mod_log.md).

Why the numbers travel through global variables: debug_log localizes its text without ROOT ("Promote 'ROOT'
returned nullptr"), so [ROOT.ScriptValue(..)] fields came out empty. Fixed text always works, so every yes/no
fact is a fixed line. Numbers are copied to global variables first and read with [GetGlobalVariable(..)].
Whether that read works in the log is verified by the TSIN_LOG;k=fmt probe line (사용자 확인 필요).

A full check block is written when the game finishes the lobby (new game or continue) and again every month,
so opening the game once is enough — the player does not have to wait for a month change or click every feature.

tools/read_log.py reads CHECKS / HOOKS / RULES from here, so the game and the reader never drift apart.
"""
from pathlib import Path
import sys, argparse
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pdx

SCHEMA = 2

# (id, 한국어 설명, trigger). Player-country scope. Written at session start and every month.
CHECKS = [
    ('age7', '제7시대 이후', 'current_age_or_later = { age = age_7_industrialization }'),
    ('age8', '제8시대 이후', 'current_later_age_8_world_wars_trigger = yes'),
    ('age9', '제9시대 이후', 'current_age_or_later = { age = age_9_atomic }'),
    ('world_init', '세계 초기화(tsin_version)', 'has_global_variable = tsin_version'),
    ('gdp_ledger', '연간 GDP 장부 작성', 'has_variable = tsin_gdp'),
    ('gdp_history', 'GDP 이력 시작', 'has_variable = tsin_gdp_history_year'),
    ('dashboard', '통계 대시보드 연도', 'has_variable = tsin_statistics_year'),
    ('capital_tech', '자본시장 기술 사용 가능', 'tsin_can_use_capital_markets = yes'),
    ('exchange_open', '거래소 개설 가능', 'tsin_exchange_can_open_trigger = yes'),
    ('stock_market', '증권거래소 보유 표식', 'has_variable = tsin_has_stock_market'),
    ('has_companies', '기업 1개 이상', 'tsin_company_count > 0'),
    ('report_domestic', '국내 조사 보고서 존재', 'has_variable = tsin_report_year'),
    ('report_world', '세계 조사 보고서 존재', 'has_variable = tsin_report_world_population'),
    ('world_company_survey', '세계 기업 조사 자료 존재', 'has_variable = tsin_wcs_survey_year'),
    ('cmp_registry', '국가 비교 등록 번호 보유', 'has_variable = tsin_cmp_id'),
    ('cmp_view', '국가 비교 창 변수 준비', 'has_variable = tsin_cmp_page'),
    ('cmp_world_history', '세계 비교 이력 존재', 'has_global_variable = tsin_cmpw_serial'),
    ('rule_bill_system', '게임 규칙: 법안 체계 켬', 'has_game_rule = tsin_bill_system_on'),
    ('rule_pop_governor', '게임 규칙: 인구 조절 켬', 'has_game_rule = tsin_population_governor_on'),
    ('rule_economy_log', '게임 규칙: 경제 통계 기록 켬', 'has_game_rule = tsin_economy_log_on'),
    ('rule_observer_log', '게임 규칙: 관찰 측정 기록 켬', 'has_game_rule = tsin_observer_log_on'),
    # V track (state only — no click required)
    ('women_law', '여성권 법 보유', 'has_law = tsin_women_rights_law'),
    ('women_suffrage', '여성 참정권 정책 시행', 'has_policy = policy:tsin_women_suffrage_policy'),
    ('naval_law', '해군 이념 법 보유', 'has_law = tsin_naval_ideology_law'),
    ('police_law', '경찰 법 보유', 'has_law = tsin_police_law'),
    ('health_law', '공중보건 법 보유', 'has_law = tsin_public_health_law'),
    ('serfdom_abolished', '농노제 폐지 완료', 'has_variable = tsin_serfdom_abolished'),
    # R07 / R09 / R10 state
    ('metro_enabled', '도시권 체계 활성', 'has_global_variable = tsin_metro_regions_enabled'),
    ('facility_aging', '노후 설비 체계 활성', 'has_global_variable = tsin_facility_aging_enabled'),
    ('press_open', '정기간행물 가능', 'tsin_has_periodical_press = yes'),
    # H track gates / stockpiles
    ('h_stockpile_gate', 'H1 군수 비축 게이트', 'tsin_h_stockpile_gate_trigger = yes'),
    ('h_fuel_gate', 'H3 연료 게이트', 'tsin_h_fuel_gate_trigger = yes'),
    ('h_air_gate', 'H4 공군 게이트', 'tsin_h_air_gate_trigger = yes'),
    ('h_eq_ready', 'H1 소화기 비축 변수', 'has_variable = tsin_eq_small_arms_stockpile'),
    ('h_fuel_ready', 'H3 연료 비축 변수', 'has_variable = tsin_fuel_stockpile'),
    ('h_air_ready', 'H4 전투기 비축 변수', 'has_variable = tsin_air_fighter_stockpile'),
]

# (id, 한국어 설명). Fixed one-line hooks.
HOOKS = [
    ('session_start', '세션 시작 점검(로비 종료·세이브 로드 직후)'),
    ('survey_domestic', '국내 통계 조사 실행'),
    ('survey_domestic_blocked', '국내 조사: 쿨다운 때문에 효과가 거부됨(버튼 allow가 뚫린 경우)'),
    ('survey_world', '세계 통계 조사 실행'),
    ('survey_world_blocked', '세계 조사: 쿨다운 때문에 효과가 거부됨'),
    ('survey_world_companies', '세계 기업 자료 조사 실행'),
    ('survey_world_companies_blocked', '세계 기업 조사: 쿨다운 때문에 효과가 거부됨'),
    ('cmp_record_domestic', '국가 비교: 국내 기록 저장'),
    ('cmp_record_world', '국가 비교: 세계 기록 저장'),
    ('cmp_page', '국가 비교: 쪽 이동'),
    ('cmp_add', '국가 비교: 비교 칸에 추가'),
    ('cmp_detail', '국가 비교: 이력 보기'),
    ('cmp_clear', '국가 비교: 비우기'),
    ('listing_exchange_open', '기업 상장: 거래소 표식 부여(거래소 개설 가능 상태)'),
    ('listing_exchange_blocked', '기업 상장: 거래소 표식 거부(자본시장 기술 없음)'),
]

# 훅 직후 다음 점검에서 기대하는 값. 어긋나면 FAIL. session_start는 상태 점검만 하므로 기대값 없음.
HOOK_EXPECT = {
    'survey_domestic': ('report_domestic', 1),
    'survey_world': ('report_world', 1),
    'survey_world_companies': ('world_company_survey', 1),
    'cmp_record_domestic': ('cmp_registry', 1),
    'cmp_record_world': ('cmp_world_history', 1),
}

IMPLIES = [
    ('stock_market', 'exchange_open', '거래소 표식이 있는데 개설 조건이 거짓입니다. 옛 세이브의 잔여일 수 있습니다'),
    ('exchange_open', 'capital_tech', '거래소 개설 가능인데 자본시장 기술이 없습니다. 트리거 정의 불일치'),
    ('women_suffrage', 'women_law', '참정권 정책인데 여성권 법이 없습니다'),
    ('h_eq_ready', 'h_stockpile_gate', '비축 변수가 있는데 H1 게이트가 거짓입니다'),
    ('h_fuel_ready', 'h_fuel_gate', '연료 변수가 있는데 H3 게이트가 거짓입니다'),
    ('h_air_ready', 'h_air_gate', '항공기 변수가 있는데 H4 게이트가 거짓입니다'),
]

SHOULD_NOT_FIRE = ['survey_domestic_blocked', 'survey_world_blocked', 'survey_world_companies_blocked']

METRICS = [
    ('gdp', '추정 GDP', 'var:tsin_gdp', 'has_variable = tsin_gdp', 0),
    ('gdp_pc', '1인당 GDP', 'var:tsin_gdp_per_capita', 'has_variable = tsin_gdp_per_capita', 2),
    ('pop', '인구(천 명)', 'total_population', None, 1),
    ('companies', '기업 수', 'tsin_company_count', None, 0),
    ('gold', '국고(두캇)', 'gold', None, 0),
    ('cmp_count', '비교 기록 수', 'var:tsin_cmp_count', 'has_variable = tsin_cmp_count', 0),
    ('wgdp_max', '세계 1인당 GDP 최고', 'global_var:tsin_world_gdp_pc_max', 'has_global_variable = tsin_world_gdp_pc_max', 2),
    ('cmp_next', '비교 등록 번호 총수', 'global_var:tsin_cmp_next_id', 'has_global_variable = tsin_cmp_next_id', 0),
    ('cmpw_serial', '세계 비교 이력 수', 'global_var:tsin_cmpw_serial', 'has_global_variable = tsin_cmpw_serial', 0),
    ('socialism', '사회주의 운동', 'var:tsin_socialism', 'has_variable = tsin_socialism', 1),
    ('suffrage_move', '여성 참정권 운동', 'var:tsin_womens_suffrage', 'has_variable = tsin_womens_suffrage', 1),
    ('press_tier', '언론 도달 단계(0~3)', 'tsin_news_press_tier', None, 0),
    ('metro_hubs', '도시권 중심 수', 'var:tsin_metro_hubs', 'has_variable = tsin_metro_hubs', 0),
    ('metro_sites', '도시권 구성 지점 수', 'var:tsin_metro_sites', 'has_variable = tsin_metro_sites', 0),
    ('eq_arms', '소화기 비축', 'var:tsin_eq_small_arms_stockpile', 'has_variable = tsin_eq_small_arms_stockpile', 0),
    ('eq_arty', '지원포 비축', 'var:tsin_eq_support_artillery_stockpile', 'has_variable = tsin_eq_support_artillery_stockpile', 0),
    ('eq_armor', '장갑차 비축', 'var:tsin_eq_armored_vehicles_stockpile', 'has_variable = tsin_eq_armored_vehicles_stockpile', 0),
    ('eq_air', '항공기 풀 비축', 'var:tsin_eq_aircraft_stockpile', 'has_variable = tsin_eq_aircraft_stockpile', 0),
    ('fuel', '연료 비축', 'var:tsin_fuel_stockpile', 'has_variable = tsin_fuel_stockpile', 0),
    ('air_fighter', '전투기 비축', 'var:tsin_air_fighter_stockpile', 'has_variable = tsin_air_fighter_stockpile', 0),
]

PREFIX = 'TSIN_LOG'
UNSET = -1


def effect_text():
    t = ['# GENERATED by tools/gen_mod_log.py (docs/mod_log.md). Always-on log; read it with tools/read_log.py.',
         '',
         '# Scope: country (player). Full check block — session start and monthly pulse both call this.',
         'tsin_log_heartbeat_effect = {',
         '\tdebug_log = tsin_log_hook_heartbeat']
    for cid, _ko, trig in CHECKS:
        t += ['\tif = {', f'\t\tlimit = {{ {trig} }}', f'\t\tdebug_log = tsin_log_chk_{cid}_1', '\t}',
              f'\telse = {{ debug_log = tsin_log_chk_{cid}_0 }}']
    t += ['\ttsin_log_snapshot_effect = yes', '}', '',
          '# Scope: country. Lobby/load path: marks the session then runs the same check block.',
          'tsin_log_session_effect = {',
          '\tdebug_log = tsin_log_hook_session_start',
          '\ttsin_log_heartbeat_effect = yes',
          '}', '',
          '# Scope: country. Copies the numbers to global variables, because the log text cannot read ROOT.',
          'tsin_log_snapshot_effect = {',
          '\tset_global_variable = { name = tsin_log_year value = current_year }',
          '\tset_global_variable = { name = tsin_log_month value = current_month }',
          '\tset_global_variable = { name = tsin_log_country value = this }',
          '\tset_variable = { name = tsin_log_probe_pv value = 7 }']
    for mid, _ko, expr, cond, _dec in METRICS:
        t.append(f'\tset_global_variable = {{ name = tsin_log_{mid} value = {UNSET} }}')
        if cond:
            t.append(f'\tif = {{ limit = {{ {cond} }} set_global_variable = {{ name = tsin_log_{mid} value = {expr} }} }}')
        else:
            t.append(f'\tset_global_variable = {{ name = tsin_log_{mid} value = {expr} }}')
    t += ['\tdebug_log = tsin_log_format_probe', '\tdebug_log = tsin_log_snapshot_line', '}', '']
    return '\n'.join(t)


def values_text():
    return ('# GENERATED by tools/gen_mod_log.py. Constant read by the TSIN_LOG format probe (ROOT / THIS / SCOPE variants).\n'
            'tsin_log_probe_sv = { value = 7 }\n')


def on_action_text():
    # on_game_started_after_lobby fires after country selection / save load (workshop mods confirm).
    # Monthly pulse remains for longer play sessions. 사용자 확인 필요: after_lobby on continue saves.
    return '''# GENERATED by tools/gen_mod_log.py (docs/mod_log.md).

monthly_country_pulse = { on_actions = { tsin_log_monthly_pulse } }

# After lobby: new game and continue. Root is none; walk player countries.
on_game_started_after_lobby = { on_actions = { tsin_log_session_pulse } }

tsin_log_monthly_pulse = {
	trigger = { is_ai = no }
	effect = { tsin_log_heartbeat_effect = yes }
}

tsin_log_session_pulse = {
	effect = {
		every_country = {
			limit = { is_ai = no }
			tsin_log_session_effect = yes
		}
	}
}
'''


def _g(name, dec=0):
    return f"[GetGlobalVariable('tsin_log_{name}').GetValue|{dec}]"


def loc_rows():
    rows = []
    rows.append(f' tsin_log_hook_heartbeat: "{PREFIX};k=hb;schema={SCHEMA}"')
    for cid, _k, _t in CHECKS:
        for v in (0, 1):
            rows.append(f' tsin_log_chk_{cid}_{v}: "{PREFIX};k=chk;id={cid};v={v}"')
    for hid, _k in HOOKS:
        rows.append(f' tsin_log_hook_{hid}: "{PREFIX};k=hook;id={hid}"')
    snap = [f"{PREFIX};k=snap", f"date={_g('year')}.{_g('month')}",
            "country=[GetGlobalVariable('tsin_log_country').GetCountry.GetNameWithNoTooltip]"]
    snap += [f"{mid}={_g(mid, dec)}" for mid, _ko, _e, _c, dec in METRICS]
    rows.append(f' tsin_log_snapshot_line: "{";".join(snap)}"')
    probe = [f"{PREFIX};k=fmt",
             f"global={_g('year')}",
             "global_name=[GetGlobalVariable('tsin_log_country').GetCountry.GetNameWithNoTooltip]",
             "root=[ROOT.ScriptValue('tsin_log_probe_sv')|0]",
             "this=[THIS.ScriptValue('tsin_log_probe_sv')|0]",
             "scope=[SCOPE.ScriptValue('tsin_log_probe_sv')|0]",
             "player=[GetPlayer.MakeScope.GetVariable('tsin_log_probe_pv').GetValue|0]"]
    rows.append(f' tsin_log_format_probe: "{";".join(probe)}"')
    return rows


def build():
    out = {
        'in_game/common/scripted_effects/tsin_mod_log_effects.txt': effect_text(),
        'in_game/common/script_values/tsin_mod_log_values.txt': values_text(),
        'in_game/common/on_action/tsin_mod_log.txt': on_action_text(),
    }
    for lang in ('english', 'korean'):
        out[f'main_menu/localization/{lang}/tsin_mod_log_l_{lang}.yml'] = f'l_{lang}:\n' + '\n'.join(loc_rows()) + '\n'
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    failures = []
    for rel, text in build().items():
        p = pdx.MOD_ROOT / rel
        if args.check:
            if not p.exists() or pdx.read_text(p) != text:
                failures.append(rel)
        else:
            pdx.write_text_bom(p, text)
    print('Mod log:', len(failures), 'differences')
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
