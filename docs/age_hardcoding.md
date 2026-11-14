# 제6시대 하드코딩 전수 조사 (EU5 1.4.x 기준)

조사 대상: 설치된 바닐라 `game/in_game`, `game/main_menu`의 `*.txt`, `*.gui`.
조사 방법: `age_6_revolutions`, `age_5_absolutism`, `current_age`, `birth_age`, `switch = { trigger = current_age }`를 검색하고 객체 단위로 분류했다.
자동 결과: `python tools/gen_age7_patches.py` 실행 시 `tools/out/age7_patch_report.md`에 객체 목록이 다시 만들어진다. 게임 패치 후에는 반드시 다시 실행한다.

## 1. 핵심 발견

### 1-1. 시대 트리거가 제6시대를 마지막으로 가정한다
`in_game/common/scripted_triggers/game_triggers.txt`

- `current_later_age_5_absolutism_trigger`는 `OR = { age_5, age_6 }`이다. 제7시대에서 거짓이 된다.
- `current_later_age_6_revolutions_trigger`는 `current_age = age_6_revolutions`이다. 제7시대에서 거짓이 된다.
- 제2~4시대 트리거는 `NOT = { current_age = 이전 시대 }` 사슬이라 제7시대에도 참이다.
- `current_age_or_later = { age = X }`는 `current_later_$age$_trigger`를 부른다. 그래서 위 두 트리거만 고치면 `current_age_or_later`를 쓰는 바닐라 코드(결정, 형성 국가, 평화 조약, 상황 트리거, 플레이버 결정 등)는 모두 정상 동작한다.
- 처리: `in_game/common/scripted_triggers/tsin_age_triggers.txt`에서 두 트리거를 `TRY_REPLACE`하고 `current_later_age_7_industrialization_trigger`를 추가한다. (m1-triggers)

### 1-2. 역방향 위험: 초기 시대 콘텐츠가 되살아난다
`NOT = { current_age = age_6_revolutions }`나 `NOR = { current_age = age_5_absolutism current_age = age_6_revolutions }`는 "초기 시대 전용"이라는 뜻이다. 제7시대에서는 이 조건이 다시 참이 되어 중세·근세 의회 안건, 일본 문화 이벤트, 성유물 원정, 일부 예술 작품이 다시 나타난다. 단순히 "제6시대 전용이 꺼지는" 문제보다 눈에 잘 띄지 않으므로 같은 생성기로 함께 처리한다.

### 1-3. 객체 단위 덮어쓰기가 가능하다 (관문 I 사전 조사)
EU5는 Jomini의 `INJECT:`, `REPLACE:`, `TRY_INJECT:`, `TRY_REPLACE:`, `INJECT_OR_CREATE:`, `REPLACE_OR_CREATE:` 접두어를 지원한다.

- 바닐라 DLC: `INJECT:historical_characters_accessories`, `INJECT_OR_CREATE:headwear`.
- 창작마당 모드 3,354건: building_types, script_values, advances, goods, casus_belli(`TRY_REPLACE:cb_timurs_conquests`), disasters(`TRY_REPLACE:revolution_disaster`), parliament_issues, scripted_triggers(`REPLACE:`), age(`TRY_INJECT:age_1_traditions`), institution, laws, situations, 이벤트(`REPLACE:black_death.1003`, 파일 상단에 `namespace` 재선언).
- 결론: 파일 전체 덮어쓰기는 필요 없다. 바닐라 객체는 `TRY_REPLACE:`(없으면 조용히 건너뜀)로, 이벤트는 `REPLACE:`로 교체한다. 실제 게임 로드 확인은 관문 I 시험에서 한다. (사용자 확인 필요)

## 2. 분류

### 2-1. 연장 (자동 생성 패치 92개 객체, 33개 파일)
생성기 `tools/gen_age7_patches.py`가 바닐라 객체를 복사해 다음처럼 바꾼다.

| 원래 코드 | in_game 치환 | main_menu 치환 |
|---|---|---|
| `current_age = age_6_revolutions` | `current_age_or_later = { age = age_6_revolutions }` | `OR = { current_age = age_6_revolutions current_age = age_7_industrialization }` |
| `birth_age = age:age_6_revolutions` | `OR = { ... age_6 ... age_7 }` | 같음 |
| `switch = { trigger = current_age ... age_6_revolutions = { X } }` | `age_7_industrialization = { X }` 가지 추가 | 같음 |

`main_menu`는 `in_game`의 스크립트 트리거를 볼 수 없을 수 있어 `OR`로 직접 쓴다. 제8시대 이후를 추가할 때는 `in_game` 쪽은 트리거만 고치면 되고, `main_menu` 쪽은 생성기 치환식만 바꾸면 된다.

| 분류 | 객체 | 판단 |
|---|---|---|
| 전쟁명분 | `cb_imperialism`, `cb_nationalist` | 19세기 핵심이므로 연장 |
| 재난 | `revolution_disaster`, `revolutionary_chaos`, `aspiration_for_liberty`, `court_and_country`, `decline_of_empire`(switch 가지 추가) | 연장. 1848년형 물결은 별도 상황 `tsin_springtime_of_nations`가 담당 |
| 상황 | `the_revolution`, `colonial_revolution` | 연장. 1837년까지 혁명·독립이 일어나지 않은 대체 역사에서도 가능해야 한다 |
| 법 | `recruitment_law`, `battle_leadership_law`, `royal_court_customs_law`, `legitimization_of_power_law`, `distribution_of_power_law`, `jakun_gusa` | 연장. 정책이 시대별로 갈라져 있어 연장하지 않으면 제7시대에 고를 정책이 사라진다 |
| 의회 안건·의제 | 귀족·성직자·시민·농민 내각 지원, `grant_city_rights`, 확장 안건 11개, `pa_*` 4개 | 연장 (초기 시대 전용 안건은 계속 꺼진 상태 유지) |
| 특권·예술·원정 | `autonomous_kadiluks`, `motet`, `symphony`, `relic_expedition` | 연장 |
| 임무·값 | `generic_capital_economy`, `crusade_jihad_age_dampener` | 연장 |
| 언어·초상 | `english_language`(birth_age), `portrait_late_trigger` | 제7시대 출생 인물이 후기 복식·방언을 쓰도록 연장 |
| 문장 | `coa_def_absolutism_age_5_trigger`, `coa_def_revolutions_age_6_trigger` | 연장 (혁명기 문장 양식 유지) |
| 이벤트 | `societal_values` 34개, `culture_japan` 5개, `parliaments` 3개, `random_event` 2개, `colonial_nation.4`, `cultural_event.2` | 연장. `parliaments.txt`의 파일 지역 `scripted_trigger is_revolutionary_issue`는 패치 파일에 함께 복사 |

예외 목록은 생성기의 `EXCLUDED_OBJECTS`에 이유와 함께 적는다. 현재 비어 있다.

### 2-2. 유지 (바꾸지 않음)
- `government_reforms`의 `age = age_6_revolutions` 22개: readme상 "이 시대부터 사용 가능"이므로 제7시대에도 유효하다.
- `advances`, `institution`의 `age =`: 소속 시대 지정이다.
- 유닛 `copy_from = a_age_6_revolutions_*`: 제6시대 유닛은 제7시대에도 그대로 존재한다. 신형은 제7시대 템플릿으로 따로 만든다.
- `main_menu/gfx/portraits/portrait_modifiers/01_beards.txt`의 birth_age: gfx 데이터라 객체 교체 지원이 불확실하다. 외형만의 문제이므로 보류한다.
- `flag_definitions`의 `coa_def_revolutions_age_6_trigger`: 트리거 쪽 패치로 해결된다.

### 2-3. 추가 (제7시대용 행이 필요)
| 항목 | 바닐라 위치 | 모드 파일 | 할 일 |
|---|---|---|---|
| 건설 가격 | `prices/01_buildings.txt:96,119` | `in_game/common/prices/tsin_buildings.txt` | `p_building_age_7_industrialization`, `p_expensive_building_age_7_industrialization` |
| 가격 수정자 정의 | `main_menu/common/modifier_type_definitions/00_modifier_types.txt:5412,5460` | `main_menu/common/modifier_type_definitions/tsin_modifier_types.txt` | `*_cost_modifier` 2개 |
| 가격 수정자 아이콘 | `main_menu/common/modifier_icons/00_modifier_icons.txt:2694,2713` | `main_menu/common/modifier_icons/tsin_modifier_icons.txt` | 2개 |
| 육군 템플릿 | `unit_types/00_age_templates_land.txt:404~` | `in_game/common/unit_types/tsin_age_templates.txt` | `a_age_7_industrialization_*` 6종 |
| 해군 템플릿 | `unit_types/00_age_templates_navy.txt:345~410` | 같은 파일 | `n_age_7_industrialization_*` 4종 |
| 징집병 | `levies/00_revolutions_levies.txt` | `in_game/common/levies/tsin_industrial_levies.txt` | 징집병은 전투력 최고값으로 고르므로 제7시대 징집병이 제6시대(`a_conscripts`, `a_gendarmerie`)보다 강해야 한다. `unlock_levy`로 해금 |
| 시대 트리거 | `game_triggers.txt:62~108` | `tsin_age_triggers.txt` | 1-1 참조 |

## 3. 제7시대 이후 확장 시 체크리스트
1. `current_later_age_7_industrialization_trigger`를 제8시대까지 포함하도록 고친다.
2. 생성기에 `AGE7` 대신 "마지막 이전 시대" 목록을 넣어 제7시대 전용 검사도 연장한다.
3. 가격·템플릿·징집병 표에 새 행을 추가한다.
4. 이 문서를 다시 생성하고 비교한다.
