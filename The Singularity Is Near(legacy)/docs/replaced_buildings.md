# 대체 건물 참조

7시대 업그레이드 건물은 `obsolete = <바닐라 건물>`로 옛 건물을 대체한다. 업그레이드된 지점에는 옛 건물 id가 남지 않으므로, 옛 id를 직접 묻는 바닐라 조건은 그 지점을 "건물 없음"으로 본다. 이 문서는 그런 참조를 모두 찾아 분류하고, 어떻게 처리할지 적는다.

조사 방법: 바닐라 `in_game`, `main_menu`의 `.txt`를 정적으로 검색했다(`building_types`, `goods_demand`, 현지화, GUI, 주석 제외). 2026-11 기준 바닐라 빌드다.

## 대체 관계

| 바닐라 건물 | 대체 건물 | 정의 파일 |
|---|---|---|
| `university` 대학 | `tsin_research_university` 연구 대학 | `tsin_education_buildings.txt` |
| `naval_base` 해군 기지 | `tsin_steam_port` 증기선 항만 | `tsin_infrastructure_buildings.txt` |
| `aqueduct_system` 수도교 | `tsin_waterworks` 상하수도 | `tsin_infrastructure_buildings.txt` |
| `provincial_chancery` 지방 상서원 | `tsin_prefecture` 도청 | `tsin_infrastructure_buildings.txt` |
| `textile_mill` 직물 공장 | `tsin_mechanized_textile_mill` | `tsin_industrial_buildings.txt` |
| `lumber_mill` 제재소 | `tsin_steam_sawmill` | `tsin_extraction_buildings.txt` |
| `iron_mill`, `glass_mill`, `paper_mill`, `furniture_mill`, `printing_mill`, `fine_cloth_mill` | `tsin_automated_*` | `tsin_automation_buildings.txt` |

계획 문서는 증기선 부두를 `dock`의 업그레이드로 적었다. 실제로는 바닐라 항구 사슬(`dock → dry_dock → shipyard → grand_shipyard → naval_base`)의 끝인 `naval_base`를 대체한다(`docs/infrastructure.md`). 그래서 `dock` 참조는 영향이 없고, `naval_base` 참조를 대신 조사했다.

모드 안의 연쇄 대체(`tsin_tenement → tsin_model_dwellings`, `tsin_fertilized_fields → tsin_mechanized_farm`, `tsin_fertilizer_plant → tsin_nitrogen_fixation_plant`)는 모드 스크립트에서 이미 두 id를 함께 센다.

## 참조 수

| 바닐라 건물 | 파일 | 참조 | 그중 국가별 역사 이벤트(DHE) |
|---|---|---|---|
| `university` | 62 | 202 | 32개 파일 112곳 |
| `naval_base` | 7 | 14 | 2개 파일 2곳 |
| `textile_mill` | 4 | 19 | 1개 파일 8곳 |
| `printing_mill` | 5 | 14 | 3개 파일 12곳 |
| `fine_cloth_mill` | 4 | 12 | 0 |
| `aqueduct_system` | 4 | 8 | 1개 파일 1곳 |
| `lumber_mill` | 2 | 5 | 0 |
| `iron_mill`, `glass_mill`, `paper_mill`, `furniture_mill` | 각 1 | 각 1 | 0 |
| `provincial_chancery` | 0 | 0 | 0 |

`iron_mill` 등 4종은 해금 기술(`1_building_unlocks.txt`)에만 나온다. 수가 계획 문서(대학 44개 파일 124곳)보다 많은 것은 `building_type:university` 형태와 `building_events.txt`의 인라인 트리거까지 셌기 때문이다.

## 분류

### 가. 7시대에도 상시 작동하는 시스템 참조: 보정한다

업그레이드 id를 OR로 더한다. 옛 건물을 짓는 효과는 그대로 두고, 그 앞의 "건물 없음" 조건이 업그레이드도 세게 해서 업그레이드된 지점에 옛 건물을 다시 짓지 않게 막는다.

- 처리: `tools/gen_age7_patches.py`의 `BUILDING_TARGETS`가 원본을 복사해 고친 뒤 `TRY_REPLACE`(이벤트는 접두어 없이 같은 id로 재정의)로 낸다(`zzz_tsin_age7_*.txt`). 게임 패치 뒤에는 생성기만 다시 돌리면 된다.
- 기록: `docs/overrides.md` 2절.
- 엘리트 교육법에는 D009 DLC가 `INJECT`로 넣은 정책이 있다. 생성기가 그 블록을 교체 뒤에 다시 넣는다.
- 바꾸는 꼴:
  - `has_building_with_at_least_one_level = 옛 id` → `OR = { 옛 id, 새 id }`
  - `has_building = building_type:옛 id` → 같은 OR
  - `OR` 안의 `building_type = building_type:옛 id` → 두 id 모두(문해율 임무의 인쇄 공장)
  - `total_effective_building_levels:university` → `tsin_total_university_levels`

| 객체 | 파일 | 옛 id | 영향 |
|---|---|---|---|
| `has_dock_infrastructure` | `scripted_triggers/location_triggers.txt` | `naval_base` | 증기선 항만만 있는 항구가 항만 시설 없음으로 보인다 |
| `unit_ship_of_the_line_location_trigger`, `unit_war_galleon_location_trigger` | `scripted_triggers/unit_triggers.txt` | `naval_base` | 증기선 항만에서 전열함, 전투 갤리온을 못 짓는다 |
| `education_elites_law` | `laws/01_common.txt` | `university` | 대학을 모두 업그레이드하면 엘리트 교육법을 채택할 수 없다 |
| `clergy_lecture_oaths` | `estate_privileges/clergy_estate.txt` | `university` | 같은 이유로 특권이 사라진다 |
| `sponsor_a_university` | `parliament_issues/05_burghers_estate_parliament_issues.txt` | `university` | 연구 대학이 있는 지점에 옛 대학을 또 지으려 한다 |
| `expand_docks` ~ `expand_naval_bases` | 같은 파일 | `naval_base` | 증기선 항만 지점에 하위 항구 건물이나 해군 기지를 또 지으려 한다 |
| `progress_and_literacy` 임무 팩 | `missions/generic_progress_and_literacy_mission_pack.txt` | `university`, `printing_mill` | 대학 수 목표와 인쇄 공장 목표가 업그레이드 뒤 줄어든다 |
| `scholars_calling` | `religious_order_callings/00_monastic.txt` | `university` | 가톨릭 학자 수도회 조건 |
| `zeal_seat_of_learning` | `religious_order_zeal_modifiers/00_catholic.txt` | `university` | 가톨릭 수도회 열의 보정치 |
| `scholai_literacy_rights` | `town_rights/byzantine_greek_roman.txt` | `university` | 비잔틴 마을 권리 |
| `building.1`, `building.2` | `events/economy/building_events.txt` | `university` | `.1`이 연구 대학이 있는 주에 옛 대학을 새로 세운다 |
| `industrialization_events.10`, `.13`, `.15`, `.22` | `events/economy/industrialization_events.txt` | `textile_mill`, `fine_cloth_mill` | `.10`이 기계화 직물 공장 지점에 옛 직물 공장을 또 짓는다 |

모드 자체 참조도 같은 기준으로 고친다. `parliaments.5`는 생성 대상이라 생성기가 함께 고치고, 나머지 둘은 손으로 고쳤다.

| 객체 | 파일 | 옛 id |
|---|---|---|
| `parliaments.5` | `events/government/zzz_tsin_age7_parliaments.txt` | `university` |
| `tsin_industrial_capitalism_plausible_location` | `scripted_triggers/tsin_institution_triggers.txt` | `textile_mill`, `iron_mill` |
| `tsin_electrification_plausible_location` | 같은 파일 | `university` |

모드의 공장 집계(`tsin_location_has_factory_trigger`, `tsin_location_vanilla_mill_levels`와 `tsin_location_automated_mill_levels`)와 대학 정원(`tsin_location_university_levels`)은 이미 두 id를 함께 센다.

### 나. 7시대에도 일어날 수 있는 일반 이벤트: 기록만 하고 대체 이벤트로 보충한다

조건에서 옛 대학이나 해군 기지가 있는 지점만 고른다. 업그레이드된 지점에서는 이벤트가 빠질 뿐 오작동하지는 않는다. 빠진 몫은 `tsin_civic.10~.120` 대체 이벤트가 채운다.

- `parliaments.18`, `innovativeness_events.7`, `church_aspects.7`, `cultural_event.14`
- `grand_tour_events.28`, `generic_mission_events.18`, `imperial_examination_events.7`
- `industrialization_events.16`(`naval_base`)
- `eng_factory_working_conditions_decision`, `eng_royal_society_decision`(잉글랜드 결정)

`church_aspects.7`은 옛 대학을 짓는 선택지가 있다. 조건이 "대학 없음"을 묻기 때문에, 연구 대학이 있는 지점에서도 고를 수 있다. 바닐라 결과가 사소해 기록만 한다.

### 다. 1837년 이전 역사 내용: 기록만 한다

- 국가별 역사 이벤트(DHE): ARA, BOH, BYZ, CAS, DLH, ENG, FRA, GEN, HAB, HUN, KOR, MAM, MEI, MOS, PIS, RUS, SCO, SWE, VEN, arm, bav, brapru, dan, hol, kie, mlo, pal, plc, pol, por, teu, tim.
- 문화와 종교 이벤트: `culture_greek.10`, `italian_renaissance_culture.28`, `iberian_culture.29`, `latinization_vs_hellenization.5`, `hellenism_religion.3`, `orthodox_flavor.101`, `black_death.103`, `reformation.14`.
- 종교개혁 상황 `reformation`, 칼뱅주의·루터주의 운동 확산 계수.
- 바닐라 제도 발생지 트리거(`renaissance_plausible_location` 등 4종). 1837년이면 모두 퍼져 있다.
- 포르투갈 국가 법 `por_estudo_geral_law`.

### 라. 영향 없음

- 해금 기술(`1_building_unlocks.txt`, `0_age_of_traditions.txt`).
- 시작 배치(`main_menu/setup/1337/07_cities_and_buildings.txt`).
- 수도교 유지비 생산 방식의 아이콘 이름.

### 확인 대상

- `cc_setup_new_town`(`scripted_effects/country_effects.txt`): 식민 특허 회사가 새 도시를 세울 때 `lumber_mill`을 1레벨 짓는다. 증기 제재소가 해금된 뒤에도 옛 제재소가 지어지는지, 지어진 뒤 업그레이드할 수 있는지 확인이 필요하다. 지어지더라도 업그레이드 경로가 있으므로 보정하지 않는다. **사용자 확인 필요.**
- 엔진이 `obsolete`를 어떻게 다루는지(옛 건물을 지을 수 없게 막는지, 효과로는 지을 수 있는지). **사용자 확인 필요.**

## 대체 이벤트 `tsin_civic`

바닐라 이벤트가 업그레이드된 지점을 건너뛰는 만큼, 업그레이드 id를 직접 묻는 이벤트를 따로 둔다. 파일은 `in_game/events/tsin_civic.txt`, 보정치는 `tsin_civic_modifiers.txt`다. `tsin_civic_yearly_pulse`(매년 12%)가 부르고 플레이버 예산을 쓴다.

| ID | 건물 | 내용 | 조건 | 반복 |
|---|---|---|---|---|
| `.10` | 연구 대학 | 훔볼트식 대학 개혁: 교육 자유(연구 속도, 제도 확산) 또는 국가 교과 과정(내각 효율, 승급) | 연구 대학 보유 | 한 번 |
| `.20` | 연구 대학 | 실험실 폭발: 안전 규정(금화) 또는 지역 불안 | 실험 과학 기술 | 25년 |
| `.30` | 연구 대학 | 학생 시위: 휴교(안정도) 또는 대화(바닐라 `student_protests` 5년) | 대중사회 수용 | 20년 |
| `.40` | 연구 대학 | 여성 입학: 허용(최대 문해율, 연구 속도) 또는 분리 | 1865년 이후 | 한 번 |
| `.50` | 연구 대학 | 국제 학술상: 위신 또는 연구소(금화, 연구 속도) | 공학 교육 기술, 연구 대학 3레벨 이상 | 15년 |
| `.60` | 증기선 항만 | 정기 기선 항로: 우편 보조금(시장 접근, 이주 매력) 또는 시민 계층 만족 | 증기선 항만 보유 | 한 번 |
| `.70` | 증기선 항만 | 항만 파업: 임금 인상(금화, 조합 운동) 또는 대체 인력(지역 불안) | 노동조합 운동 20 이상 | 15년 |
| `.80` | 증기선 항만 | 이민선: 식민지 이주 보조 또는 이민 항구 | 과밀한 항만 지점 | 20년 |
| `.90` | 상하수도 | 대악취: 수도에 상하수도를 반값에 짓거나 지역 불안 5년 | 근대 하수도 기술, 수도가 도시 이상이고 상하수도 없음 | 한 번 |
| `.100` | 상하수도 | 펌프 손잡이 조사: 수인성 전염 이론(금화, 전염병 저항, 기대 수명) | 상하수도 보유 | 한 번 |
| `.110` | 도청 | 도시 자치 논쟁: 선출 시의회 또는 도지사 중앙 집권 | 도청 보유 | 30년 |
| `.120` | 자동화 공장 | 첫 무인 공정 시연: 위신과 시범 공장 또는 노동 불만 감소 | 자동화 공장 보유 | 한 번 |

사용자 확인 필요: `.90`의 `construct_building`이 비용 절반으로 건설을 시작하는지, `.30`이 바닐라 `student_protests` 보정치를 그대로 붙이는지.

## 공용 트리거

`in_game/common/scripted_triggers/tsin_replaced_building_triggers.txt`(location 범위):

- `tsin_has_university_tier_trigger`: `university` 또는 `tsin_research_university`.
- `tsin_has_port_tier_trigger`: `naval_base` 또는 `tsin_steam_port`.
- `tsin_has_waterworks_tier_trigger`: `aqueduct_system` 또는 `tsin_waterworks`.
- `tsin_has_chancery_tier_trigger`: `provincial_chancery` 또는 `tsin_prefecture`.
- `tsin_has_textile_tier_trigger`: `textile_mill`, `fine_cloth_mill` 또는 그 업그레이드.
- `tsin_has_printing_tier_trigger`: `printing_mill` 또는 `tsin_automated_printing_mill`.

country 범위의 대학 수는 연간 집계값 `tsin_country_university_levels`(두 대학 건물 레벨 합)가 이미 있다. 바닐라 조건을 고칠 때는 집계 시점과 무관하게 즉시 반영되도록 `total_effective_building_levels:university`와 `total_effective_building_levels:tsin_research_university`를 직접 더한다.
