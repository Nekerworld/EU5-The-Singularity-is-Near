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

## tsin_scramble_for_colonies (식민지 쟁탈전)

- 파일: `in_game/common/situations/tsin_scramble_for_colonies.txt`, 참여 조건 `in_game/common/scripted_triggers/tsin_situation_triggers.txt`, 이벤트 `in_game/events/tsin_scramble.txt`, 수정자 `main_menu/common/static_modifiers/tsin_scramble_modifiers.txt`, GUI `in_game/gui/panels/situation/tsin_scramble_for_colonies.gui`, 힌트 `hint_tsin_scramble_for_colonies`.
- 시작: 1870년 이후, 참여 조건(`tsin_scramble_participant_trigger`: 종속국 아님, 산업자본주의 수용, 왕국·제국 등급 또는 황제)을 만족하는 나라가 4개 이상, 한 판에 한 번(`tsin_scramble_happened`).
- 참여국 등급 조건은 바닐라 `cb_imperialism`의 `create_enabled`와 같게 맞췄다. 모드가 `zzz_tsin_age7_imperialism.txt`로 이 전쟁명분을 7시대에도 쓸 수 있게 했으므로, 쟁탈전 참여국은 식민과 제국주의 전쟁 두 경로로 땅을 넓힌다.
- 시작 시 참여국에 `tsin_scramble_colonial_drive`(식민 범위 +25%, 식민 이주 +25%, 식민 유지 효율 +10%)와 `tsin_scramble.1`.
- 10년째: 식민 회의 `tsin_scramble.2` 한 번. 세력권 수용(땅 차지 적대감 -15%, 화해 쪽 가치관) 또는 모든 권리 주장(식민 범위 +25%, 받는 적대감 +10%, 호전 쪽 가치관).
- 매달 참여국마다 약 0.4% 확률로 `tsin_scramble.3` 식민지 저항(금 2배 비용 또는 이주 -20% 감쇠 수정자).
- 30년 뒤 종료: 수정자 제거와 `tsin_scramble.10`.
- 지도: 참여국 영토는 높음, 주인 없는 땅은 중간 색.

사용자 확인 필요: `has_owner = no`와 `is_ownable = yes`를 지역 툴팁·지도 색에서 함께 쓰는 동작, `antagonism_taking_land_giving_modifier`의 부호 의미(음수가 적대감 감소인지), 상황 GUI 연결.

## 국민의 봄 `tsin_springtime_of_nations` (M4)

| 항목 | 내용 |
|---|---|
| 파일 | `in_game/common/situations/tsin_springtime_of_nations.txt`, 이벤트 `in_game/events/tsin_springtime.txt`, 보정치 `main_menu/common/static_modifiers/tsin_springtime_modifiers.txt` |
| 시작 | 제7시대 이후, 바닐라 `the_revolution`이 진행 중이 아님, `tsin_springtime_unrest_trigger`(자유주의 ≥ 50, 민족주의 ≥ 50, 사회주의 ≥ 40 중 하나)를 만족하는 나라 3곳 이상. 한 번만(전역 변수 `tsin_springtime_happened`). 월 확률 `monthly_spawn_chance_low` |
| 시작 효과 | 조건을 만족하는 나라에 `tsin_springtime_barricades`(왕실 권력 -10%, 월간 통제력 -0.01, 시민 불만)와 `tsin_springtime.1` |
| 진행 | 대상국마다 매달 약 3% 확률로 `tsin_springtime.2`(시가전: 협상 금 -2·자유주의 -5 / 진압 안정도 -·자유주의 +5) |
| 끝 | 3년 뒤. `tsin_springtime.10`이 첫 선택에 따라 갈린다: 헌법(자유주의 -10) / 진압(자유주의 +10, 사회주의 +5) / 관망(효과 없음) |
| 첫 선택 `.1` | 헌법(자유주의 -30, 민족주의 -10, `tsin_springtime_constitution` 감쇠, 귀족 불만, 자유주의 쪽) / 진압(`tsin_springtime_reaction`, 안정도 -, 귀족 만족) / 관망 |
| 바닐라 관계 | `the_revolution`은 `current_age = age_6_revolutions`에서만 시작하므로 겹치지 않지만, 제7시대 진입 직후 아직 진행 중일 수 있어 `NOT = { is_situation_active = situation:the_revolution }`을 둔다 |
| 그림 | `the_revolution`의 색상만 바꾼 임시 그림 |

사용자 확인 필요: 상황 화면 GUI(`in_game/gui/panels/situation/tsin_springtime_of_nations.gui`)가 열리는지, 대상국이 한 곳도 없을 때 지도 색이 기본색으로 나오는지.
