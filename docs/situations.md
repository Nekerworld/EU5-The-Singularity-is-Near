# 모드 상황(situation)

바닐라 상황의 제7시대 연속성은 `docs/continuity.md`에 있다. 이 문서는 모드가 새로 만든 상황을 다룬다.

새 상황 하나에 필요한 파일(바닐라 구조):

| 파일 | 내용 |
|---|---|
| `in_game/common/situations/<key>.txt` | 정의 |
| `in_game/gui/panels/situation/<key>.gui` | 상황 화면. `situation_panel`을 쓴다(바닐라 `readme.txt`) |
| `in_game/common/scriptable_hints/tsin_hints.txt` | `hint_tag` 힌트 |
| `gfx/interface/icons/situations/<key>.dds`, `gfx/interface/illustrations/situation/<key>.dds` | 아이콘·삽화 (`tools/make_placeholder_art.py`) |
| 현지화 | `<key>`, `<key>_desc`, 결말 이름, 지도 툴팁, `hint_<key>`·`_hint_text`·플레이 방식별 문구 |

힌트 목록의 아이콘은 바닐라 `hints_lateralview.gui`에 힌트 이름별로 박혀 있어, 모드 힌트에는 아이콘이 없다. 바닐라 GUI를 덮어쓰지 않기 위해 그대로 둔다.

## `tsin_long_depression` 대불황 (M3)

| 항목 | 내용 |
|---|---|
| 발생 | 1865년 이후, 산업자본주의를 수용한 국가가 6개 이상, 한 번만(`tsin_long_depression_happened`). 조건이 맞으면 매달 1% |
| 참여 | 산업자본주의를 수용한 국가 |
| 1단계 공황(0~2년) | `tsin_depression_panic`: 공장 건설 효율 -25%, 생산 효율 -5%, 은행 이자 +1%, 평민·시민 목표 만족 -5% |
| 2단계 불황(2년~) | `tsin_depression_slump`: 공장 건설 효율 -15%, 생산 효율 -3%, 평민 목표 만족 -2.5% |
| 국가별 회복 | `tsin_depression.3` 회복 정책: 관세 인상(관세 상한 +10%, 중상주의 쪽 이동) 또는 공공사업(금 -4). 불황을 지우고 `tsin_depression_recovered`(공장 건설 효율 +5%)를 준다 |
| 결말 | 8년 이후 불황 국가가 없으면 "회복", 아니면 20년에 "긴 불황의 끝" |
| 이벤트 | `.1` 공황 시작(은행 구제 / 방치 / 화폐 발행), `.2` 은행 도산, `.3` 회복 정책, `.10` 종료. 상황 이벤트라 연간 플레이버 예산을 쓰지 않는다 |
| 지도 | 공황 HIGH, 불황 MID, 회복 LOW |

### 사용자 확인 필요

- 모드 GUI 파일이 상황 화면에 연결되는지(파일 이름 규칙 추정), 화면이 비지 않는지
- `years_since_situation_start`에 따른 단계 전환과 두 결말
- 매달 `every_country`가 성능에 주는 영향(`docs/perf_baseline.md` 절차)
