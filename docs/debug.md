# 개발용 도구

## 숨김 결단 (`in_game/common/decisions/tsin_debug_decisions.txt`)

세 결단 모두 `potential = { debug_only = yes }`이다. 콘솔에서 `debug_mode`를 켜야만 보이므로 배포판에서 따로 지울 필요가 없다.

| 결단 | 효과 |
|---|---|
| `tsin_debug_rerun_init_decision` | 전역 변수 `tsin_version`, `tsin_migrated_save`를 지우고 `tsin_system.1`을 다시 실행 |
| `tsin_debug_reset_notices_decision` | 자국의 `tsin_notified_*` 변수를 지워 제도 등장 알림을 다시 받게 함 |
| `tsin_debug_institution_progress_decision` | 수도에 제7시대 제도 3종의 진척도를 25씩 추가 (이미 등장한 제도만 의미 있음) |

M2 경제 시험용 결단(`tsin_debug_economy_decisions.txt`, 역시 `debug_only`). 기술은 주지 않는다.

| 결단 | 효과 |
|---|---|
| `tsin_debug_build_factories_decision` | 수도에 `tsin_machine_works`, `textile_mill` 즉시 건설 |
| `tsin_debug_upgrade_textile_decision` | 수도에 `tsin_mechanized_textile_mill` 즉시 건설(개축 경로 확인) |
| `tsin_debug_engines_shortage_decision` / `_glut_decision` | 수도 시장 기관 공급 `market_goods_extreme_loss` / `_gain` |
| `tsin_debug_economy_events_a_decision` / `_b_decision` | 예산 초기화 후 `tsin_economy.10`·`.20` / `.30`·`.40` 실행 |

## 관찰 측정 기록기

게임 규칙 "관찰 측정 기록"(`tsin_observer_log`, 기본 끔)을 켜거나 `-debug_mode`로 실행하면 1년에 한 번 `TSIN_OBS;...` 줄을 로그에 쓴다. `python tools/observer_report.py`가 그 줄을 모아 `docs/balance_targets.md`와 비교한다. 절차는 `docs/tests/observer_run.md`.

## 콘솔 명령 (엔진 내장)

시대 변경과 제도 등장은 스크립트 효과로 할 수 없다. 대신 게임 실행 파일에 들어 있는 콘솔 명령을 쓴다. 아래 명령 이름과 인자는 `tools/exe_strings.py`로 `eu5.exe`의 도움말 문자열에서 확인했다. 실제 동작은 **사용자 확인 필요**.

| 목적 | 명령 |
|---|---|
| 제7시대 강제 진입 | `change_age age_7_industrialization` |
| 날짜 이동 | `change_date 1837` |
| 제도 강제 등장 | `spawn_institution tsin_industrial_capitalism manchester` |
| | `spawn_institution tsin_mass_society paris` |
| | `spawn_institution tsin_electrification berlin` |
| 제도 진척 추가 | `add_institution_progress tsin_industrial_capitalism manchester 50` |
| 지도 모드 툴팁 누락 점검 | `mapmode_report` |
| 아이콘 툴팁 누락 점검 | `icon_report` |

## 권장 시험 순서

1. `debug_mode`
2. `change_date 1837` 후 며칠 진행하거나 `change_age age_7_industrialization`
3. 시대 시작 안내(`tsin_system.2`)와 바닐라 `ages_of_eu.1`이 뜨는지 확인
4. `spawn_institution ...`으로 제도를 등장시키고 다음 해 1월 알림(`tsin_system.10~12`)을 확인
5. 지도 모드 `산업 시대 제도`에서 색이 바뀌는지 확인
