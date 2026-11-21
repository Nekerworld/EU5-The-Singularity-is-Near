import re, sys, tempfile, unittest, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdx
import gen_mod_log as spec
import read_log

ROOT = pdx.MOD_ROOT


def hb(time, **checks):
    """One heartbeat as the game would write it (checks default to the healthy values)."""
    rows = [f'[{time}][jomini_effect_impl.cpp:479]: common/scripted_effects/tsin_mod_log_effects.txt:5: TSIN_LOG;k=hb;schema={spec.SCHEMA}']
    for cid, _ko, _t in spec.CHECKS:
        v = checks.get(cid, 0)
        rows.append(f'[{time}][jomini_effect_impl.cpp:479]: common/scripted_effects/tsin_mod_log_effects.txt:9: TSIN_LOG;k=chk;id={cid};v={int(v)}')
    rows.append(f'[{time}][jomini_effect_impl.cpp:479]: x:1: TSIN_LOG;k=fmt;global=1850;global_name=France;root=;this=;scope=;player=')
    snap = 'date=1850.3;country=France;' + ';'.join(f'{m[0]}=1' for m in spec.METRICS)
    rows.append(f'[{time}][jomini_effect_impl.cpp:479]: x:1: TSIN_LOG;k=snap;{snap}')
    return rows


def hook(time, hid):
    return f'[{time}][jomini_effect_impl.cpp:479]: x:1: TSIN_LOG;k=hook;id={hid}'


def report(lines, errors=None):
    with tempfile.TemporaryDirectory() as d:
        dp = Path(d) / 'debug.log'
        dp.write_text('\n'.join(lines), encoding='utf-8')
        ep = None
        if errors is not None:
            ep = Path(d) / 'error.log'
            ep.write_text('\n'.join(errors), encoding='utf-8')
        args = argparse.Namespace(debug=dp, error=ep, rows=24, all=False)
        return read_log.build_report(args)


class GeneratedLogTests(unittest.TestCase):
    def test_deployed_files_match_generator(self):
        for rel, text in spec.build().items():
            self.assertEqual(pdx.read_text(ROOT / rel), text, rel)

    def test_every_log_key_has_localization_in_both_languages(self):
        keys = set(re.findall(r'debug_log = (tsin_log_\w+)', spec.effect_text()))
        for lang in ('english', 'korean'):
            loc = pdx.read_text(ROOT / f'main_menu/localization/{lang}/tsin_mod_log_l_{lang}.yml')
            for key in keys:
                self.assertIn(f'\n {key}: ', loc, key)

    def test_hooks_used_by_generators_are_all_declared(self):
        used = set()
        for p in (ROOT / 'in_game').rglob('*.txt'):
            used |= set(re.findall(r'debug_log = tsin_log_hook_(\w+)', pdx.read_text(p)))
        used |= set(re.findall(r'tsin_log_hook_(\w+)', (ROOT / 'era_7/in_game/common/scripted_effects/tsin_company_generated_effects.txt').read_text(encoding='utf-8-sig')))
        declared = {h for h, _ in spec.HOOKS} | {'heartbeat'}
        self.assertEqual(used - declared, set())
        self.assertEqual({h for h, _ in spec.HOOKS} - used, set(), 'declared hook that no script writes')

    def test_log_lines_use_global_variables_not_root(self):
        loc = pdx.read_text(ROOT / 'main_menu/localization/english/tsin_mod_log_l_english.yml')
        snap = next(l for l in loc.splitlines() if l.startswith(' tsin_log_snapshot_line'))
        self.assertNotIn('ROOT.', snap)
        self.assertIn("GetGlobalVariable('tsin_log_gdp')", snap)

    def test_checks_are_fixed_text_without_interpolation(self):
        loc = pdx.read_text(ROOT / 'main_menu/localization/english/tsin_mod_log_l_english.yml')
        for line in loc.splitlines():
            if line.startswith((' tsin_log_chk_', ' tsin_log_hook_')):
                self.assertNotIn('[', line)

    def test_session_and_monthly_on_actions_are_wired(self):
        t = pdx.read_text(ROOT / 'in_game/common/on_action/tsin_mod_log.txt')
        self.assertIn('monthly_country_pulse = { on_actions = { tsin_log_monthly_pulse } }', t)
        self.assertIn('on_game_started_after_lobby = { on_actions = { tsin_log_session_pulse } }', t)
        self.assertIn('tsin_log_session_effect = yes', t)
        self.assertIn('is_ai = no', t)
        # Old hand-wired pulse must not remain (would double-fire monthly).
        main = pdx.read_text(ROOT / 'in_game/common/on_action/tsin_on_actions.txt')
        self.assertNotIn('tsin_log_monthly_pulse', main)

    def test_session_hook_is_declared_and_written(self):
        self.assertIn(('session_start', '세션 시작 점검(로비 종료·세이브 로드 직후)'), spec.HOOKS)
        self.assertIn('debug_log = tsin_log_hook_session_start', spec.effect_text())
        self.assertEqual(spec.SCHEMA, 3)

    def test_metric_variables_are_guarded_before_reading(self):
        text = spec.effect_text()
        for mid, _ko, expr, cond, _dec in spec.METRICS:
            if expr.startswith(('var:', 'global_var:')):
                self.assertIsNotNone(cond, mid)
                self.assertIn(f'limit = {{ {cond} }}', text)


class ReaderTests(unittest.TestCase):
    def test_empty_log_is_a_clear_failure(self):
        r = report(['[03:00:00][x.cpp:1]: nothing'])
        self.assertIn('**FAIL** 모드 로그가 한 줄도 없음', r)

    def test_healthy_run_passes_without_fail(self):
        lines = [hook('03:00:50', 'session_start')]
        lines += hb('03:01:00', age7=1, capital_tech=1, exchange_open=1, stock_market=1)
        lines += [hook('03:01:30', 'survey_domestic')]
        lines += hb('03:02:00', age7=1, capital_tech=1, exchange_open=1, stock_market=1, report_domestic=1)
        r = report(lines)
        self.assertNotIn('**FAIL**', r)
        self.assertIn('**PASS** 세션 시작 점검(로비 종료·세이브 로드 직후) (1회)', r)
        self.assertIn('**PASS** 국내 통계 조사 실행 (1회)', r)
        self.assertIn('거래소 표식', r)

    def test_stock_flag_without_exchange_fails(self):
        r = report(hb('03:01:00', stock_market=1, exchange_open=0, capital_tech=0))
        self.assertIn('**FAIL** 증권거래소 보유 표식 → 거래소 개설 가능 불일치', r)

    def test_hook_without_following_state_fails(self):
        lines = hb('03:01:00') + [hook('03:01:30', 'cmp_record_domestic')] + hb('03:02:00', cmp_registry=0)
        r = report(lines)
        self.assertIn('**FAIL** 국가 비교: 국내 기록 저장 뒤', r)

    def test_unfinished_hook_is_marked_unverified_not_passed(self):
        r = report(hb('03:01:00') + [hook('03:01:30', 'survey_world')])
        self.assertIn('**미검증** 세계 통계 조사 실행 (1회)', r)

    def test_blocked_hook_is_failure(self):
        r = report(hb('03:01:00') + [hook('03:01:10', 'survey_world_blocked')])
        self.assertIn('**FAIL** 세계 조사: 쿨다운 때문에 효과가 거부됨', r)

    def test_format_probe_reports_which_variant_works(self):
        r = report(hb('03:01:00'))
        self.assertIn('| [GetGlobalVariable(...)] — 스냅샷이 쓰는 방식 | 작동 | 1850 |', r)
        self.assertIn('| [ROOT.ScriptValue(...)] — 기존 TSIN_ECON/TSIN_OBS 방식 | 비어 있음(실패) |', r)

    def test_failed_global_read_is_called_out_and_alternative_named(self):
        lines = hb('03:01:00')
        lines = [l.replace('global=1850', 'global=').replace('this=;', 'this=7;') for l in lines]
        lines.append("[03:01:00][pdx_data_localize_helper.cpp:315]: FetchData failed for 'GetGlobalVariable('tsin_log_year').GetValue'")
        lines.append("[03:01:00][pdx_data_localize.cpp:207]: Data error in loc string 'tsin_log_snapshot_line'")
        r = report(lines)
        self.assertIn('**전역 변수 방식이 실패했다.**', r)
        self.assertIn('대신 작동한 방식: this', r)
        self.assertIn('**WARN** 로그 문구의 값 읽기 실패', r)

    def test_mod_script_errors_are_grouped_and_other_errors_are_counted_apart(self):
        err = ['[03:38:23][jomini_script_system.cpp:256]: Script system error!',
               "  Error: Failed to fetch variable for 'tsin_x' due to not being set",
               '  Script location: common/disasters/tsin_a.txt:17', '',
               '[03:38:24][jomini_script_system.cpp:256]: Script system error!',
               '  Error: Invalid left side during comparison \'var:other_mod\'',
               '  Script location: common/laws/other.txt:3', '']
        r = report(hb('03:01:00'), err)
        self.assertIn('common/disasters/tsin_a.txt:17', r)
        self.assertNotIn('other.txt', r)
        self.assertIn('무관 1건', r)

    def test_snapshot_rows_are_truncated_but_all_prints_everything(self):
        lines = []
        for i in range(40):
            lines += hb(f'03:{i:02d}:00')
        short = report(lines)
        self.assertIn('| … | … |', short)


if __name__ == '__main__':
    unittest.main()
