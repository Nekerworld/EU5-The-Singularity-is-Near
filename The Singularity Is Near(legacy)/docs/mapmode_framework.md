# 지도 모드 공통 틀

## 파일

| 파일 | 내용 |
|---|---|
| `in_game/gfx/map/map_modes/tsin_map_modes.txt` | 모든 `tsin_` 지도 모드 정의. 맨 위에 `@tsin_*` 변수 |
| `in_game/common/script_values/tsin_map_values.txt` | 위치 스코프(`root = location`) 값 |
| `main_menu/gfx/interface/icons/map_modes/<모드>.dds` | 메뉴 아이콘 (검증기가 존재 여부를 검사) |
| `main_menu/localization/*/tsin_core_l_*.yml` | 이름, 설명, 범례 |

`@` 변수는 파일 안에서만 보인다. 바닐라 `map_modes.txt`의 `@data_*`, `@flatmap_*`를 쓸 수 없으므로 같은 값을 `@tsin_*`로 다시 적어 두었다. 바닐라 값이 바뀌면 함께 고친다.

## 공통 규칙

- **범주와 표시 그룹:** 바닐라 `category`를 사용한다. `index`는 정렬 순서가 아니라 UI가 요청하는 그룹 번호다. 현재 기본 UI와 Good Interface가 모두 표시하는 그룹에 맞춰 TSIN은 `economy = 3`, `population = 1`, `demography = 3`을 사용한다. 90 이상의 번호는 UI 표시 그룹에서 빠지므로 사용하지 않는다. 카테고리 또는 UI를 변경하면 `hud_bot.gui`의 `GetMapModeGroupFromCategory` 호출과 대조한다.
- **색:** `define:NMapColors|...`만 쓴다. 색맹 설정과 바닐라 색감을 그대로 따르기 위해서다.
  - 연속 값: `lerp = { min_color = MAP_COLOR_LOW max_color = MAP_COLOR_HIGH factor = {...} }`
  - 단계 값: `MAP_COLOR_LOW` → `MAP_COLOR_MID` → `MAP_COLOR_HIGH` → `MAP_COLOR_MAX`
  - 부족·경고: `MAP_COLOR_MIN`
- **소유 없는 지점:** `limit = { has_owner = yes }` 밖은 색을 칠하지 않는다.
- **갱신:** `color_refresh_counters = { Month LocationOwnerChanged }`가 기본이다. `Day`는 쓰지 않는다.
- **성능:** `map_color` 안에서 전 세계나 국가 전체를 순회하지 않는다. 지점 자신의 값, 미리 계산한 변수, 엔진 값만 읽는다.
- **범례:** 색마다 `legend_key = { desc = "LEGEND_KEY_TSIN_<...>" color = ... }`.
- **표시:** `use_fow = no`, `flatmap_behaviour = Always`, `force_brown_in_flatmap = only_in_rg_colorblind_mode` (바닐라 데이터 지도 모드와 같음).

## 현지화 키

| 키 | 예 |
|---|---|
| `mapmode_<모드>_name` | `mapmode_tsin_industrialization_name: "산업화"` |
| `MAPMODE_<모드 대문자>` | `"#T $mapmode_<모드>_name$#!\n설명"` (바닐라 형식) |
| `LEGEND_KEY_TSIN_<항목>` | 범례 문구 |

## 위치 값

| 값 | 의미 |
|---|---|
| `tsin_location_vanilla_mill_levels` | 바닐라 공장 단계(`is_mill = yes`) 18종의 레벨 합 |
| `tsin_location_mill_levels` | 위 값 + 모드 공장 단계(`tsin_machine_works`, `tsin_mechanized_textile_mill`, `tsin_fertilizer_plant`, `tsin_explosives_plant`). 모드 공장은 추가될 때 덧붙인다 |
| `tsin_location_industrial_jobs` | 공장 일자리 수(인구 규모 단위). 일반 공장 레벨 × `mills_employment` + 기계화 공장 레벨 × `tsin_mechanized_mill_employment` |
| `tsin_location_industrial_share` | 공장 일자리 ÷ `population`, 0~1 |
| `tsin_map_industrial_share_saturation` | 산업화 지도 모드가 최대 색이 되는 공장 일자리 비중(0.25) |

`location_building_level(building_type:X)` 함수형 값은 바닐라 `attribute_columns/05_location.txt`에서 쓰는 형식이다. 스크립트 값의 `add`에서 동작하는지는 **사용자 확인 필요**(M2 시험 절차서). `employment_size`의 1은 1000명이고 `population`도 같은 단위라고 가정했다(**사용자 확인 필요**: 공장 1레벨 지점의 툴팁 비중이 실제 고용/인구와 맞는지).

## 현재 지도 모드

| 키 | 범주 | 단계 | 상태 |
|---|---|---|---|
| `tsin_industrial_institutions` | demography | M1 | 관문 H 시험용 겸 제7시대 제도 확산 |
| `tsin_industrialization` | economy | M2 | 공장 일자리 비중 그라데이션, 툴팁 `TSIN_INDUSTRIALIZATION_MAPMODE_TT` |
| `tsin_industrial_investment` | economy | M3 | 외국 소유 건물(`num_foreign_buildings`)과 소유국의 투자 정책으로 5단계 |
| `tsin_urbanization` | population | M4 | 시민+노동자 비중 그라데이션(50%에서 최대), 도시·대도시는 최대색 |
| `tsin_labor_unrest` | population | M4 | 최근 파업 지점(위치 변수) → 공장 지점은 소유국 노동 운동 세기 → 공장 없음 |
| `tsin_radicalism` | population | M4 | 소유국 최강 운동 × 지점 불만 |
| `tsin_electrification` | economy | M5 | 지점이 속한 시장의 전력 충족률: 충분(최대) → 부족(낮음~높음 그라데이션) → 미연결(최소) |
| `tsin_education` | population | 0.7 | 소유국 고등교육률, 연구 대학 지점 강조 (`docs/education.md`) |
| `tsin_automation` | economy | 0.7 | 자동화 공장 비중(중간~최대) → 자동화 없는 공장(낮음) → 공장 없음(최소) |
| `tsin_industrial_siting` | economy | 0.7 | 입지 점수: 시장 접근도 × 0.4 + 석탄·철광 0.25 + 철도역 0.2 + 도시 등급 0.15 |
| `tsin_infrastructure` | economy | 0.7 | 철도역·상하수도·증기선 항만·도시 조명망·도청 개수 ÷ 5 |
| `tsin_labor_conditions` | population | 0.7 | 공장 지점의 `tsin_location_labor_conditions`. 0.3 미만은 최소색, 공장 없는 지점은 칠하지 않음 |
| `tsin_housing` | population | 0.7 | 모범 주택(최대) → 연립주택(높음) → 과밀(최소) → 수용력 대비 인구 그라데이션 |
| `tsin_gdp_per_capita` | economy | 0.7 | 소유국 1인당 추정 GDP ÷ 지난해 세계 최고값(`global_var:tsin_world_gdp_pc_max`) |
| `tsin_corporations` | economy | 0.7 | 소유국 기업 본사(최대) → 기업 건물 레벨(10레벨에서 높음) → 없음 |
| `tsin_agriculture` | demography | 0.7 | 기계화 농장(최대) → 시장 식량 부족(최소) → 농업 단계 60% + 1인당 식량 잉여 40% |

## 산업 투자 지도 모드의 범위

계획은 "국가·계층별 투자 집중도"였지만, 바닐라 스크립트에서 읽을 수 있는 소유 정보는 나라 단위뿐이다.

- 읽을 수 있음: 지점 트리거 `num_foreign_buildings`, `any_foreign_buildings_in_location`, 건물 트리거 `is_building_owned_by = <나라>`.
- 찾지 못함: 건물을 어느 계층(귀족, 시민, 성직자, 왕실)이 소유하는지 읽는 트리거나 값. 그래서 계층별 투자는 표시하지 않는다.

색: 외국 소유 건물이 있는 공업 지점(최대) → 외국 소유 건물만 있는 지점(높음) → 소유국이 `tsin_state_industry_policy`인 공업 지점(중간) → 그 밖의 공업 지점(낮음) → 공장 없음(최소).

사용자 확인 필요: `num_foreign_buildings`를 지도 모드 `map_color`의 `limit`에서 써도 되는지, `has_policy = policy:tsin_state_industry_policy`가 모드 정책에 동작하는지.

## 대중사회 지도 모드 (M4)

위치 값은 `in_game/common/script_values/tsin_society_map_values.txt`에 있다. 모두 지점 자신과 소유국 변수만 읽는다.

| 값 | 의미 |
|---|---|
| `tsin_location_urban_share` | (`num_pop_type:burghers` + `num_pop_type:laborers`) ÷ `population` |
| `tsin_location_labor_pressure` | 소유국 `tsin_labor_unionism` ÷ 100 |
| `tsin_location_radicalism` | 소유국 `tsin_radicalism` ÷ 100 × (1.5 − `average_satisfaction`), 최대 1 |

- **도시화:** 계획의 "도시 인구 비율 또는 도시 등급 대비 인구" 가운데 인구 비율을 택했다. EU5에는 도시 인구라는 값이 따로 없어서, 농업 밖에서 일하는 시민·노동자 비중으로 근사했다. 도시 등급은 `location_rank`로 따로 칠한다.
- **노동 불안:** 위치 변수 `tsin_labor_unrest`(1 인정, 2 중재, 3 진압)를 `tsin_society.20` 파업 이벤트가 그 공장 지점에, `tsin_springtime.2`의 진압 선택이 수도에 5년 동안 남긴다. 변수가 없는 공장 지점은 소유국 노동 운동 세기로 칠한다.
- **급진성:** `tsin_update_movements_effect`가 매년 여섯 운동 가운데 가장 큰 값을 국가 변수 `tsin_radicalism`에 담는다. 바닐라 `movements`는 종교·문화 운동이라 이념 확산을 담을 수 없어(`docs/mass_society.md`), 그 지도 모드를 쓰지 않았다.
- **생활수준:** 바닐라 `satisfaction` 지도 모드(범주 population, `color_mode = satisfaction`)가 이미 지점 만족도를 보여 주므로 따로 만들지 않았다. 급진성 설명에 바닐라 지도 모드를 안내한다.

사용자 확인 필요: 스크립트 값의 `owner.var:` 읽기가 지도 모드에서 동작하는지(바닐라 `rise_of_the_ottomans` 이벤트에 같은 형식이 있음), `average_satisfaction`이 0~1 범위인지, 이벤트로 지점에 `years`가 붙은 변수를 둘 수 있는지.

## 전력 지도 모드 (M5)

위치 값은 `in_game/common/script_values/tsin_power_map_values.txt`에 있다. 전력은 시장 상품이라(`docs/gate_g.md`) 지점의 `market`에서 바닐라 시장 값 `goods_supply_in_market`, `goods_demand_in_market`를 읽는다. 바닐라 법(`01_common.txt`)이 `capital.market` 안에서 같은 값을 쓴다.

| 값 | 의미 |
|---|---|
| `tsin_location_power_supply` | 시장의 `tsin_electricity` 공급 |
| `tsin_location_power_demand` | 시장의 `tsin_electricity` 수요 |
| `tsin_location_power_ratio` | 공급 ÷ 수요, 최대 1. 수요가 없으면 1 |

색은 계획의 3색 범례를 따른다. 수요가 있는데 충족률이 1보다 작으면 부족(충족률로 낮음~높음 그라데이션), 공급이 있으면 충분, 둘 다 없으면 미연결이다.

사용자 확인 필요: 스크립트 값 안에서 `market ?= { add = "goods_supply_in_market(goods:tsin_electricity)" }` 형식이 값을 돌려주는지(바닐라 `byz_values.txt`가 `capital ?= { market ?= { ... } }` 범위 전환을 씀), 지점 범위에서 `market` 연결이 동작하는지.

## 0.7 지도 모드

위치 값은 `tsin_map_values.txt` 끝(0.7 절)과 생성 파일 `tsin_company_generated_values.txt`(`tsin_location_owner_company_levels`, `tsin_location_company_hq`)에 있다.

- 1인당 GDP의 기준값 `global_var:tsin_world_gdp_pc_max`는 `tsin_update_world_gdp_effect`가 1년에 한 번(`tsin_tempo_yearly_pulse`, 360일 시한 전역 변수) 모든 나라를 돌아 정한다.
- 농업 모드의 식량 잉여는 바닐라 `market_food_balance` 지도 모드와 같은 식(`market.market_monthly_food_balance ÷ market.market_population`)이다.
- 노동 불안 모드 툴팁에 소유국 노동 불만(`tsin_location_owner_labor_grievance`)을 더했다.

사용자 확인 필요: 지점 범위에서 `this = owner.var:tsin_hq_<기업>` 비교(본사 판정), `raw_material = goods:coal`을 스크립트 값 `limit`에서 쓰는 것, `market ?= { market_population > 0 }` 조건, 입지·GDP 색 분포가 지도에서 구분될 만큼 퍼지는지.
