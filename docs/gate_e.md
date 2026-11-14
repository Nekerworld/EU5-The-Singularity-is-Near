# 관문 E — 다중 생산 방식 슬롯과 자동화 단계

상태: **스크립트 작성 완료, 게임 내 동작은 사용자 확인 필요**

## 질문

1. 건물 하나에 생산 방식 슬롯을 여러 개 둘 수 있는가
2. 슬롯 안에서 대체 생산 방식(기본/정제)을 고를 수 있는가
3. 기술로 특정 생산 방식만 잠그고 풀 수 있는가
4. 자동화를 `obsolete` 연쇄(상위 건물 단계)로 근사할 수 있는가

## 바닐라 근거

| 질문 | 바닐라 예 | 위치 |
|---|---|---|
| 1 다중 슬롯 | `cannon_workshop`: `unique_production_methods` 블록 2개(재질, 탄약). 길드 건물은 "기본"·"강화" 2슬롯 | `building_types/production_cannons.txt`, 현지화 `cannon_workshop_slot_0/1`, `fine_cloth_guild_slot_0/1` |
| 2 슬롯 내 대체 | `textile_mill`: 한 슬롯에 목화·양모·섬유 작물 3방식 | `building_types/pure_one_level_productions.txt` |
| 3 방식 잠금 | `paper_wood_pulp_maintenance`는 건물 안 고유 방식이지만 기술 `paper_guild_wood_pulp_maintenance_advance`의 `unlock_production_method`로 풀린다 | `advances/3_production_method_unlocks.txt` |
| 4 상위 단계 | `textile_mill`의 `obsolete = cloth_manufactory`. 인터페이스 문구 `BUILDING_UPGRADE_ONE`("...에서 개축"), define `ESTABLISHMENT_UPGRADE_TRANSFER_FRACTION = 0.5` | `building_types/readme.txt`, `interfaces_l_english.yml`, `00_defines.txt` |

슬롯 이름 현지화 키는 `<건물>_slot_<번호>`이다.

## 시험 건물

`in_game/common/building_types/tsin_industrial_buildings.txt`

### `tsin_machine_works` (기계 공장) — 질문 1~3

| 슬롯 | 방식 | 투입 | 산출(기관) | 비고 |
|---|---|---|---|---|
| 0 틀 | `tsin_machine_works_iron_frame` | 철 2.25, 석탄 1.5, 도구 0.75 | 2.7 | 기본 |
| 0 틀 | `tsin_machine_works_steel_frame` | 강철 1.8, 석탄 1.0, 도구 0.5 | 3.0 | 정제, `tsin_steel_frame_engines_advance`로 해금 |
| 1 부속 | `tsin_machine_works_copper_fittings` | 구리 0.3, 목재 0.3 | 0.3 | 기본 |
| 1 부속 | `tsin_machine_works_glass_gauges` | 구리 0.2, 유리 0.25 | 0.33 | 정제 |

### `tsin_mechanized_textile_mill` (기계화 방직 공장) — 질문 4

- `obsolete = textile_mill`. 연쇄: `cloth_manufactory` → `textile_mill` → `tsin_mechanized_textile_mill`
- 고용 `tsin_mechanized_mill_employment = 0.15` (바닐라 `mills_employment = 0.25`)
- 슬롯 0 원료(목화·양모·섬유 작물), 슬롯 1 동력(증기: 기관·석탄·도구 / 수력: 목재·도구)

## 수치 기준

바닐라 공장은 산출 가치 ≈ 투입 비용 × (1 + `mills_profit_margin` 0.35)이다(예: 제강소 투입 14.8 → 강철 4개 = 20). 시험 건물도 이 비율을 따르고, 정제 방식은 약 1.45배로 조금 높게 잡았다. 각 방식의 계산은 파일 주석에 적었다.

## 확인 방법

`docs/tests/m2_test_guide.md`의 관문 E 항목을 따른다.

## 미확인 위험

- 슬롯마다 `produced`가 같은 상품일 때 산출이 합산되는지(바닐라 `cannon_workshop`이 같은 방식이므로 합산으로 추정)
- `obsolete` 대상이 제6시대 건물일 때, 제7시대 기술만으로 개축 경로가 열리는지
- 고유 방식에 `unlock_production_method`를 걸면 기술 전에는 선택지가 잠겨 보이는지
