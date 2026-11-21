# 관찰 실행 절차서 (밸런스 측정)

`docs/balance_targets.md`의 2~6절과 8절을 AI만 도는 실행 한 번으로 측정한다. 이 문서의 결과는 모두 **사용자 확인 필요**다. 에이전트는 게임을 실행할 수 없어 정적 검사와 보고서 도구 시험(가짜 로그)만 했다.

## 측정 기록기

| 구성 | 위치 |
|---|---|
| 켜는 조건 | 게임 규칙 "관찰 측정 기록" = 켬, 또는 `-debug_mode`로 실행 (`tsin_observer_logging_trigger`) |
| 기록 시점 | 나라별 연간 맥동 중 그해 처음 도는 나라가 한 줄을 쓴다. 전역 변수 `tsin_obs_logged_recently`(360일)로 1년에 한 번만 쓴다 |
| 기록 효과 | `tsin_observer_log_snapshot_effect` → `debug_log = tsin_observer_log_line` (`in_game/common/on_action/tsin_on_actions.txt`) |
| 지표 | `in_game/common/script_values/tsin_observer_values.txt` → 전역 `tsin_obslog_*` 복사 후 `[GetGlobalVariable(...)]`로 기록 |
| 보고서 | `python tools/observer_report.py [--csv docs/results/observer_<날짜>.csv]` |

`debug_log`는 ROOT를 못 읽으므로(프랑스 1달 플레이 error.log) 숫자를 전역 변수로 옮긴 뒤 찍는다(**사용자 확인 필요**: 값이 채워진 `TSIN_OBS` 줄).

규칙이 꺼져 있고 `-debug_mode`도 아니면 맥동 조건 첫 줄에서 멈추므로 일반 플레이 비용은 없다. 켜져 있을 때도 1년에 한 번 전 세계를 20회 남짓 순회할 뿐이다.

로그 한 줄의 형식:

```
TSIN_OBS;year=1850;countries=…;gp=…;ic_known=…;ic_emb=…;…;flavor=…
```

| 키 | 뜻 |
|---|---|
| `year` | 기록한 해 |
| `countries` / `gp` | 존재하는 나라 수 / 열강 수 |
| `ic_known` / `ic_emb` / `ic_emb_gp` | 산업자본주의를 아는 나라 / 수용국 / 수용한 열강 |
| `ms_known` / `ms_emb` | 대중사회를 아는 나라 / 수용국 |
| `el_known` / `el_emb` / `el_emb_gp` | 전기화를 아는 나라 / 수용국 / 수용한 열강 |
| `non_eu` | 수도가 유럽 밖이면서 제7시대 제도를 하나 이상 수용한 나라 |
| `pop` | 세계 인구 합 |
| `gp_income` / `gp_army` / `gp_adv` | 열강의 월 수입(교역+세금) 합 / 군대 규모 합 / 평균 연구 기술 수 |
| `steel` / `engines` | 열강 수도 시장의 강철·기관 가격을 기본가로 나눈 값의 평균 |
| `sit` | 진행 중인 상황. 일의 자리 국민의 봄, 십의 자리 장기 불황, 백의 자리 식민지 분할, 천의 자리 만국박람회 |
| `hunger` | 대기근 재난을 겪은 나라 수 |
| `flavor` | 지난 기록 뒤 전 세계에서 나온 `tsin_` 플레이버 이벤트 수(예산을 쓴 이벤트) |

## 준비

1. 플레이셋: 이 모드만 켠다(호환 시험은 따로 한다).
2. Steam 실행 옵션에 `-debug_mode`를 넣는다. 기존 세이브에서도 기록기가 켜진다.
3. 시작점은 둘 중 하나를 고른다.
   - 1827년 근처 세이브가 있으면 그것을 쓴다(제7시대 진입 10년 전부터 기준값을 남긴다).
   - 없으면 새 게임에서 게임 규칙 "관찰 측정 기록"을 켜고 시작한다. 1837년까지 오래 걸리므로 콘솔 `change_date 1830`을 써도 되지만 결과 파일에 그 사실을 적는다.
4. `Documents/Paradox Interactive/Europa Universalis V/logs/`의 이전 로그는 게임이 새로 실행될 때 덮어써진다. 측정 중에는 게임을 다시 켜지 않는다.

## 실행

1. 콘솔 `observe`로 관찰 모드로 바꾸고 최고 속도로 진행한다.
2. 자동 실행을 원하면 실행 파일 도움말에 있는 명령줄 옵션을 쓴다(사용자 확인 필요).
   - `-loadsavehandsoff <세이브 이름>`: 세이브를 불러와 관찰 모드로 진행
   - `-timed_handsoff <개월>`: 정해진 개월 수만큼 진행 (1827→1950이면 1476)
   - `-handsoff_save_at_dates "1837|1850|1875|1900|1950"`: 지정한 날짜에 세이브
3. 1950년까지 진행한다. 중간에 멈췄다면 그때까지의 로그로도 보고서를 낼 수 있다.

## 판정

```
python tools/observer_report.py --csv docs/results/observer_<날짜>.csv
python tools/scan_logs.py
```

1. `observer_report.py`가 시기, 경제·인구, 따라잡기, 이벤트 예산, 1900년 이후 안정성을 `balance_targets.md`의 허용 범위와 비교해 `[통과]`/`[벗어남]`으로 표시한다.
2. `TSIN_OBS` 줄이 하나도 없으면 다음 순서로 확인한다.
   - `scan_logs.py`에서 `debug_log` 또는 `tsin_obs_` 관련 오류가 있는지
   - `debug.log` 대신 `game.log`에 기록됐는지 (보고서는 세 로그 파일을 모두 읽는다)
   - 줄은 있는데 값이 `[ROOT.ScriptValue(...)]` 그대로 나오면 데이터 함수가 로그에서 풀리지 않는 것이다. 그 경우 결과 파일에 적고 수동 측정(아래)으로 바꾼다.
3. 로그로 잴 수 없는 항목은 세이브(`-handsoff_save_at_dates`)를 열어 직접 본다.
   - 1900년 산업자본주의 수용국 수도 권역의 상위 단계 공장
   - `tsin_engines` 생산국 수(시장 화면)
   - 산업국 도시 인구 비중(도시화 지도 모드)
   - 대기근 재난국의 인구 손실률
   - 근대화 임무를 시작한 나라가 30년 안에 산업자본주의를 수용했는지

## 결과 기록

`docs/results/observer_<날짜>.md`에 아래 표를 채운다. 게임 버전, 모드 버전(`.metadata/metadata.json`의 `version`), 시작 세이브, 진행 구간을 함께 적는다.

| 목표 | 허용 범위 | 측정값 | 판정 | 조정 후보 |
|---|---|---|---|---|
| 산업자본주의 발생 | 1837~1860 | | | `tsin_age_7_institutions.txt`의 `can_spawn`·진척 속도 |
| 첫 수용국 | 1845~1865 | | | 제도 확산·수용 비용 |
| 열강 절반 수용 | 1865~1890 | | | 같음 |
| 대중사회 발생 | 1840~1870 | | | 같음 |
| 전기화 발생 | 1870 이후 | | | 같음, 게임 규칙 "전기화 시기" |
| 열강 전기화 수용 | 1885~1900 | | | 같음 |
| 국민의 봄 | 1840~1865, 1회 | | | `tsin_springtime_of_nations.txt`의 `monthly_spawn_chance` |
| 장기 불황 | 1860~1890, 1회 | | | `tsin_long_depression.txt` |
| 강철 가격 비율 | 0.7~2.0 | | | 공장 생산량, `goods_demand` |
| 열강 수입 1837→1900 | 2~5배 | | | 공장 산출, 세금 보정치 |
| 세계 인구 1837→1900 | +40~80% | | | 인구 성장 보정치, 대기근 빈도 |
| 유럽 밖 수용국(1900) | 3개국 이상 | | | 근대화 임무, 박람회 기술 확산 |
| 1900~1950 연 증가율 | 5% 이하 | | | `docs/continuity.md`의 1900년 이후 처리 |
