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

- **범주와 순서:** 바닐라 `category`(`economy`, `population`, `demography` 등)에 넣고 `index`는 90 이상을 써서 바닐라 항목 뒤에 붙인다.
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
| `tsin_location_mill_levels` | 위 값 + 모드 공장 단계(`tsin_machine_works`, `tsin_mechanized_textile_mill`). 모드 공장은 추가될 때 덧붙인다 |
| `tsin_location_industrial_jobs` | 공장 일자리 수(인구 규모 단위). 일반 공장 레벨 × `mills_employment` + 기계화 공장 레벨 × `tsin_mechanized_mill_employment` |
| `tsin_location_industrial_share` | 공장 일자리 ÷ `population`, 0~1 |
| `tsin_map_industrial_share_saturation` | 산업화 지도 모드가 최대 색이 되는 공장 일자리 비중(0.25) |

`location_building_level(building_type:X)` 함수형 값은 바닐라 `attribute_columns/05_location.txt`에서 쓰는 형식이다. 스크립트 값의 `add`에서 동작하는지는 **사용자 확인 필요**(M2 시험 절차서). `employment_size`의 1은 1000명이고 `population`도 같은 단위라고 가정했다(**사용자 확인 필요**: 공장 1레벨 지점의 툴팁 비중이 실제 고용/인구와 맞는지).

## 현재 지도 모드

| 키 | 범주 | 단계 | 상태 |
|---|---|---|---|
| `tsin_industrial_institutions` | demography | M1 | 관문 H 시험용 겸 제7시대 제도 확산 |
| `tsin_industrialization` | economy | M2 | 공장 일자리 비중 그라데이션, 툴팁 `TSIN_INDUSTRIALIZATION_MAPMODE_TT` |
