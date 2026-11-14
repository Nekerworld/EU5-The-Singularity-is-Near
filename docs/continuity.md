# 바닐라 시대 연속성 (M1b)

제7시대에 들어가도 바닐라의 19세기 성격 콘텐츠(제국주의, 민족주의, 혁명, 의회)가 꺼지지 않게 하는 처리 기록이다. 게임 안 동작은 모두 **사용자 확인 필요**다.

## 처리 방식

1. **트리거 두 개 수정** (`in_game/common/scripted_triggers/tsin_age_triggers.txt`): `current_later_age_5_absolutism_trigger`, `current_later_age_6_revolutions_trigger`가 제7시대도 포함한다. 바닐라에서 `current_age_or_later = { age = ... }`를 쓰는 곳(결단, 형성 국가, 평화 조약, 상황 등)은 자동으로 연장된다.
2. **정확한 시대 비교 자동 패치** (`tools/gen_age7_patches.py`): 바닐라가 `current_age = age_6_revolutions`처럼 제6시대와 정확히 같은지를 보는 곳을 찾아 `current_age_or_later`로 바꾼 객체를 `zzz_tsin_age7_*.txt`로 덮어쓴다. `switch = { trigger = current_age }`에는 제7시대 분기를 추가한다. 결과 목록은 `tools/out/age7_patch_report.md`(92개 객체, 33개 파일)에 있다.
3. 바닐라가 바뀌면 `python tools/gen_age7_patches.py`를 다시 실행해 패치를 새로 만든다.

## 전쟁명분과 형성 국가 (m1b-cb-formables)

| 대상 | 처리 | 근거 |
|---|---|---|
| `cb_imperialism` | 자동 패치 | 바닐라 `imperialism.txt:9,18`이 `current_age = age_6_revolutions` |
| `cb_nationalist` | 자동 패치 | 바닐라 `nationalist.txt:7,10` |
| 형성 국가 전체 | 처리 불필요 | `00_formable_countries.txt`는 `current_age_or_later`와 "이 시대 이전" 조건만 쓴다. 1번 트리거 수정으로 제7시대에도 동작한다 |
| 독일(`GER_f`), 이탈리아(`ITA_f`) | 처리 불필요 | 시대 조건이 없다. 문화 집단과 영토(이탈리아는 밀라노·피렌체·나폴리) 조건만 있다 |
| 벨기에(`BEL_f`) 등 제6시대 이후 형성 국가 | 처리 불필요 | `current_age_or_later = { age = age_6_revolutions }` |

## 재난과 상황 (m1b-disasters-situations)

| 대상 | 종류 | 처리 |
|---|---|---|
| `revolution_disaster`, `revolutionary_chaos`, `aspiration_for_liberty`, `court_and_country` | 재난 | 자동 패치 (`current_age`) |
| `decline_of_empire` | 재난 | 자동 패치 (`switch`에 제7시대 분기 추가, 제6시대 값 사용) |
| `the_revolution`, `colonial_revolution` | 상황 | 자동 패치 |
| 날짜로 묶인 상황·재난 | — | 1800년 이후 날짜 조건이 없다(`current_year`, 날짜 상수 검색). 연장할 것이 없다 |

## 의회, 법, 특권 등 (m1b-parliament-laws)

| 분류 | 자동 패치 객체 |
|---|---|
| 의회 의제 | `pa_rethink_army_academy`, `pa_rethink_navy_academy`, `pa_reduce_land_recruitment`, `pa_reduce_naval_recruitment` |
| 의회 안건 | 계층별 내각 지원 4종, `support_nobles_art`, `grant_city_rights`, 확장 안건 11종 (`promote_industrial_workshops` 등) |
| 법 | `royal_court_customs_law`, `legitimization_of_power_law`, `recruitment_law`, `battle_leadership_law`, `distribution_of_power_law`, `jakun_gusa` |
| 특권 | `autonomous_kadiluks` |
| 기타 | 예술 작품(`motet`, `symphony`), 탐험(`relic_expedition`), 임무(`generic_capital_economy`), 언어(`english_language`), 성전 값, 초상화·문장 트리거 |
| 이벤트 | 46개 (`societal_values.*` 35개, `parliaments.*`, `culture_japan.*`, `random_event.*` 등) |

## 시대의 얼굴 (m1b-age-face)

| 항목 | 처리 | 파일 |
|---|---|---|
| 시대 시작 이벤트 | 바닐라 `ages_of_eu.1`이 모든 시대 공통이다(`on_new_age`). 행정·외교·군사 선호 선택이 그대로 뜬다. 이 모드는 안내 이벤트 `tsin_system.2`만 덧붙인다 | `in_game/events/tsin_system.txt` |
| 패권국 | 바닐라 패권국 5종에는 시대 조건이 없다. 시대 블록의 `hegemons_allowed = yes`로 제7시대에도 유지 | `in_game/common/age/tsin_age_7.txt` |
| 승리 카드 | 시대 블록 `victory_card`에 제6시대와 같은 구조로 지정 | 같은 파일 |
| 시대 선택 발전 | 바닐라 `4_choices_*`처럼 행정·외교·군사 10개씩, 총 30개. 효과 키와 크기는 바닐라 선택 발전에서 쓰는 것만 골랐다 | `in_game/common/advances/tsin_4_choices.txt` |
| 공통 해금 골격 | 예비군 제도(징집군 2종 해금), 요새 한도, 보급 한도. 모두 `tsin_steam_age_advance` 뒤에 연결 | `in_game/common/advances/tsin_1_common_unlocks.txt` |
| 실제 유닛 해금 | 제7시대 유닛 템플릿만 있고 실제 유닛은 M6(`m6-military`)에서 추가한다. 그 전까지 제7시대 군대는 제6시대 유닛을 쓴다 | — |

## 덮어쓰기 위험

- 자동 패치 파일은 바닐라 객체 전체를 다시 정의한다. 같은 객체를 바꾸는 다른 모드와는 나중에 로드된 쪽만 적용된다 (`docs/overrides.md`, `docs/load_order.md`).
- 이 모드가 지면 해당 객체는 제7시대에 바닐라처럼 "제6시대 아님"으로 판정된다. 예: 제국주의 전쟁명분이 사라진다. 게임이 깨지지는 않는다.

## 사용자 확인 항목

- 제7시대에 제국주의·민족주의 전쟁명분이 보이는가 (`docs/tests/m1_test_guide.md`의 관문 I).
- 제7시대에 의회가 있는 국가에서 의회 안건 목록이 비지 않는가.
- 혁명 상황이 제6시대에 시작됐다면 제7시대로 넘어가도 끝나지 않고 이어지는가.
