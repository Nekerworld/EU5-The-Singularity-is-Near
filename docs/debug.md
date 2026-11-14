# 개발용 도구

## 숨김 결단 (`in_game/common/decisions/tsin_debug_decisions.txt`)

세 결단 모두 `potential = { debug_only = yes }`이다. 콘솔에서 `debug_mode`를 켜야만 보이므로 배포판에서 따로 지울 필요가 없다.

| 결단 | 효과 |
|---|---|
| `tsin_debug_rerun_init_decision` | 전역 변수 `tsin_version`, `tsin_migrated_save`를 지우고 `tsin_system.1`을 다시 실행 |
| `tsin_debug_reset_notices_decision` | 자국의 `tsin_notified_*` 변수를 지워 제도 등장 알림을 다시 받게 함 |
| `tsin_debug_institution_progress_decision` | 수도에 제7시대 제도 3종의 진척도를 25씩 추가 (이미 등장한 제도만 의미 있음) |

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
