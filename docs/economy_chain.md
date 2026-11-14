# 산업 경제 수직 순환 (M2)

상태: **스크립트 작성 완료, 가격·수익 변화는 사용자 확인 필요**

## 순환 구조

```
철·석탄 ─→ 제강소(바닐라) ─→ 강철 ─┐
철·석탄·도구 ───────────────────────┼─→ 기계 공장 ─→ 기관 ─┬─→ 기계화 방직 공장(증기 동력 슬롯) ─→ 직물 ─→ 인구 수요(cloth)
구리·목재 / 구리·유리 ──────────────┘                     ├─→ 제7시대 함선 건조·수리 수요
                                                          └─→ 제7시대 공장 건설 수요(tsin_factory_construction)
```

| 단계 | 객체 | 파일 |
|---|---|---|
| 상품 | `tsin_engines` (가격 6, 운송비 1, 인구 수요 없음 — 강철과 같은 중간재) | `in_game/common/goods/tsin_goods.txt` |
| 색 | `goods_tsin_engines` | `main_menu/common/named_colors/tsin_colors.txt` |
| 상품별 보정치 10종 | `can_extract_`, `ban_exports_of_`, `ban_imports_of_`, `local_/global_..._output_modifier`, `..._establishment_speed`, `global_..._pop_demand`, `..._impacts_inflation`, `..._used_for_minting` | `main_menu/common/modifier_type_definitions/tsin_goods_modifier_types.txt`, `modifier_icons/tsin_goods_modifier_icons.txt` (`tools/goods_modifiers.py steel tsin_engines`로 생성) |
| 생산 | `tsin_machine_works` | `in_game/common/building_types/tsin_industrial_buildings.txt` |
| 소비(제조업 1종) | `tsin_mechanized_textile_mill` | 같은 파일 |
| 함선 수요 | `tsin_*_7_construction/repair`에 기관 추가 | `in_game/common/goods_demand/tsin_navy_demands.txt` |
| 건설 수요 | `tsin_factory_construction` (도구 0.6, 석조 3.5, 강철 0.5, 기관 0.2) | `in_game/common/goods_demand/tsin_construction_demands.txt` |
| 소비 수요 | `tsin_mass_society_advance`에 `global_cloth_pop_demand = 0.1` | `in_game/common/advances/tsin_0_age_of_industrialization.txt` |
| 산업 장려 | `tsin_machinery` (기관) | `in_game/common/industry_types/tsin_industries.txt` |
| 해금 | `tsin_machine_works_advance` → `tsin_steel_frame_engines_advance`, `tsin_mechanized_textile_mill_advance` | `in_game/common/advances/tsin_2_building_unlocks.txt` |

## goods_demand 연결 방식

바닐라 `goods_demand`에는 시대별 블록이 없다. 인구 수요는 `pop_demands.txt`의 `pop_demand`와 상품의 `demand_add`로 정해지고, 시대 차이는 기술 보정치(`global_<상품>_pop_demand`)와 시대별 함선·유닛 수요 객체로 생긴다. 그래서 제7시대 연결은 다음 세 경로로 했다.

1. 제7시대 함선 수요 객체(이미 M1에서 시대 표에 연결)에 기관을 넣었다.
2. 제7시대 공장 건물의 건설 수요에 기관과 강철을 넣었다.
3. 대중사회 기술이 직물 인구 수요를 10% 올린다.

## 수익 기준

바닐라 공장은 산출 가치 ≈ 투입 비용 × 1.35(`mills_profit_margin`)이다.

| 건물·방식 조합 | 투입 비용 | 산출 가치 | 고용 |
|---|---|---|---|
| 제강소(바닐라) | 14.8 | 20.0 | 0.25 |
| 기계 공장: 주철 틀 + 구리 부속 | 13.35 | 18.0 | 0.25 |
| 기계 공장: 강철 틀 + 유리 계기 | 13.85 | 19.98 | 0.25 |
| 직물 방직소(바닐라, 목화) | 8.89 | 12.0 | 0.25 |
| 기계화 방직 공장: 목화 + 증기 | 16.5 | 22.26 | 0.15 |
| 기계화 방직 공장: 목화 + 수력 | 13.95 | 18.81 | 0.15 |

## 화학 공업: 비료와 폭약 (M3)

```
초석·백반·석탄 / 생선·가축·석탄 ─→ 비료 공장 ─→ 비료 ─→ 시비 농지(곡물 RGO 강화) ─→ 원자재 산출 +15%, 식량
초석·석탄·목재 / 초석·가축·백반 ─→ 폭약 공장 ─→ 폭약 ─→ 발파 채굴장(광물 RGO 강화) ─→ 원자재 산출 +15%
```

| 단계 | 객체 | 파일 |
|---|---|---|
| 상품 | `tsin_fertilizer` (가격 2.5), `tsin_explosives` (가격 5), 둘 다 인구 수요 없음 | `in_game/common/goods/tsin_goods.txt` |
| 상품별 보정치 | `python tools/goods_modifiers.py` 인자 없이 실행하면 모드 상품 전체를 다시 생성 | `tsin_goods_modifier_types.txt`, `tsin_goods_modifier_icons.txt` |
| 생산 | `tsin_fertilizer_plant`, `tsin_explosives_plant` (공장, 슬롯 1개에 방식 2개) | `in_game/common/building_types/tsin_chemical_buildings.txt` |
| 소비 | `tsin_fertilized_fields`, `tsin_blasting_works` (바닐라 `windmill`·`local_smelters`와 같은 `rgo_enhancement_category`, 최대 1레벨) | 같은 파일 |
| 해금 | `tsin_improved_fertilizer_advance` → `tsin_dynamite_advance` | `in_game/common/advances/tsin_3_industrial_capitalism.txt` |

바닐라 RGO는 투입재가 없으므로, 농업·광업과의 연결은 바닐라 풍차·현지 제련소 방식을 따랐다. 유지 방식이 비료·폭약을 소비하고, 건물 보정치가 원자재 산출을 올린다.

| 건물·방식 | 투입 비용 | 산출 가치 |
|---|---|---|
| 비료 공장: 광물 비료 | 13.5 | 18.25 |
| 비료 공장: 유기 비료 | 13.5 | 18.25 |
| 폭약 공장: 흑색화약 | 12.25 | 15.0 (일부러 낮은 이윤) |
| 폭약 공장: 니트로글리세린 | 12.5 | 16.85 |
| 시비 농지 유지 | 0.31 (비료 0.1, 도구 0.02) | 산출 없음, 보정치 |
| 발파 채굴장 유지 | 0.31 (폭약 0.05, 도구 0.02) | 산출 없음, 보정치 |

## 철도와 시장 접근도 (M3)

바닐라 `railroad` 도로 유형(제6시대 `railroad_advance`가 해금)을 그대로 쓴다. 바닐라에는 국가 단위 시장 접근도 보정치가 없고 `local_market_access`(지역 단위)만 있으므로, 철도역 건물로 연결했다.

| 객체 | 내용 | 파일 |
|---|---|---|
| `tsin_railway_network_advance` | `railroad_advance`와 산업자본주의 뿌리 기술 필요. 철도역 해금, 철도 건설비 -10% | `tsin_3_industrial_capitalism.txt` |
| `tsin_steel_rolling_stock_advance` | 철도 건설비 -20%, 도로 건설 시간 -20% | 같은 파일 |
| `tsin_railway_station` | 수도 또는 수도와 철도(`has_road_of_type_to`)로 이어진 도시. `local_market_access` +10%. 유지: 석탄 0.1, 도구 0.05, 기관 0.03. 연결이 끊기면 철거(바닐라 `local_governor`의 `remove_if` 방식) | `in_game/common/building_types/tsin_railway_buildings.txt` |
| 철도 건설·유지 수요 | 바닐라 값에 석탄 0.5·도구 0.25(건설), 석탄 0.01(유지) 추가. 제6시대에도 지을 수 있도록 제7시대 상품은 넣지 않았다 | `in_game/common/goods_demand/tsin_railroad_demands.txt` (`docs/overrides.md`) |

## 자동화 업그레이드 (0.7)

바닐라 공장 6종을 제자리에서 개축(`obsolete`)한다. 건물마다 원래 재화 1종만 내고, 생산 방식은 "증기 동력 → 전동기" 기술 단계 둘뿐이다. 원료 비율은 바닐라 공장 방식을 그대로 따르고, 산출 가치 = 투입 비용 × 1.35가 되게 맞췄다. 고용은 `tsin_mechanized_mill_employment`(0.15, 바닐라 0.25).

| 업그레이드 | 바닐라 원본 | 재화 | 증기(산출 6) 투입 | 전동기(산출 7) 투입 | 해금 |
|---|---|---|---|---|---|
| `tsin_automated_iron_mill` | `iron_mill` | 도구 | 13.33 | 15.55 | `tsin_interchangeable_parts_advance` |
| `tsin_automated_furniture_mill` | `furniture_mill` | 가구 | 13.34 | 15.55 | 같음 |
| `tsin_automated_paper_mill` | `paper_mill`(목재 펄프) | 종이 | 8.89 | 10.37 | `tsin_continuous_process_advance` |
| `tsin_automated_glass_mill` | `glass_mill` | 유리 | 13.33 | 15.55 | 같음 |
| `tsin_automated_printing_mill` | `printing_mill` | 서적 | 13.33 | 15.55 | `tsin_rotary_press_advance` |
| `tsin_automated_fine_cloth_mill` | `fine_cloth_mill` | 고급 직물 | 26.67 | 31.11 | `tsin_power_jacquard_advance` |

- 증기 단계의 동력: 기관 0.15, 석탄 0.5. 전동기 단계의 동력: 전력 0.8, 기관 0.05. 전동기 단계는 모두 `tsin_electric_motor_advance`가 연다.
- 산출 1단위당 원료는 바닐라보다 7~34% 적다(종이가 가장 크게 준다).
- 자동화 공장은 `tsin_location_automated_mill_levels`로 묶여 공장 일자리(`tsin_location_industrial_jobs`)와 산업화 지도 모드에 들어간다.
- 정의: `in_game/common/building_types/tsin_automation_buildings.txt`. 해금 기술: `tsin_2_building_unlocks.txt`.

### 시장 접근도 상한 `tsin_automation_max_level`

바닐라 `mills_max_level`은 시장 접근도가 0.75 미만이면 (접근도 + 0.25)를 곱한다. 자동화 공장은 산출이 커서 시장이 필요하므로 같은 조건에서 한 번 더 곱한다. 예: 접근도 0.5인 도시는 바닐라 공장 상한이 75%, 자동화 공장 상한은 약 56%이다. 철도역(`local_market_access` +10%)이 접근도를 0.75 위로 올리면 감소가 사라지므로, 철도망이 자동화의 전제 조건 역할을 한다. 정의: `in_game/common/script_values/tsin_building_caps.txt`.

## 채굴 단계 (0.7)

- `tsin_blasting_works`: `tsin_deep_coal_mining_advance`가 최대 레벨을 1 → 2로 올리고(`tsin_blasting_works_max_level`), 증기 양수 방식 `tsin_blasting_works_steam_pumping`(폭약 0.03, 석탄 0.05, 기관 0.005, 유지비 0.28)을 연다. 기존 유지 방식(0.31)도 남는다. 심부 탄광 기술은 이제 다이너마이트 기술도 선행으로 요구한다.
- `tsin_steam_sawmill`: 바닐라 `lumber_mill`을 개축한다. 증기 톱(도구 0.4, 석탄 0.3, 기관 0.033 → 목재 1.6) → 전기 톱(도구 0.4, 전력 0.3, 기관 0.025 → 목재 1.8). 바닐라 제재소(도구 0.417 → 목재 1)와 같은 `rural_profit_margin` 1.2배이다. 고용 0.6(바닐라 1.0). 해금 `tsin_steam_sawmill_advance`, 전기 톱은 `tsin_electric_motor_advance`. 정의: `tsin_extraction_buildings.txt`.

## 사용자 확인 필요

- 자동화 공장이 건물 화면에서 바닐라 공장의 개축 대상으로 보이는지, 개축 뒤 레벨이 유지되는지
- `tsin_automation_max_level`의 설명 줄(`TSIN_BUILDING_LEVEL_AUTOMATION_MARKET_ACCESS`)이 상한 툴팁에 보이는지
- 발파 채굴장의 건물 보정치(원자재 산출 +15%)가 레벨마다 쌓이는지. 쌓이지 않으면 2레벨은 일자리만 늘린다
- 증기 제재소가 `rgo_building_category`에서 바닐라 제재소처럼 목재를 내는지
- `has_road_of_type_to`가 철도 경로 전체를 따라가는지(바닐라 `flavor_mug.txt`의 라호르→쿨나 예시로 보아 경로 검사로 추정), 수도 외 도시에서 철도역이 지어지고 연결이 끊기면 철거되는지
- `TRY_REPLACE`로 바꾼 철도 건설 수요가 건설 화면에 석탄·도구로 표시되는지
- 비료·폭약이 부족할 때 시비 농지·발파 채굴장의 보정치가 약해지는지. 약해지지 않는다면 비료·폭약은 유지비일 뿐이고, 수요 연결은 시장 가격으로만 작동한다.
- 발파 채굴장이 금·은 광산에도 지어지는지, 화폐 주조에 이상이 없는지
- 기관 공급이 부족할 때 기관 가격이 오르고, 기계화 방직 공장의 증기 동력 방식 수익이 떨어지는지
- 기계 공장이 강철 가격 상승에 반응해 주철 틀로 돌아가는지(AI·자동 선택이 있는 경우)
- 함선 건조 시 기관 수요가 시장에 잡히는지
- 산업 장려 화면에 `tsin_machinery`가 제7시대 이후에만 보이는지

## 고무와 석유 (M3, 선택)

- 상품: `tsin_rubber`(채집, 가격 4, `location_potential`은 열대 밀림), `tsin_oil`(채굴, 가격 4, 운송비 1.5). 시작 시 어느 지역도 이 원자재를 갖지 않는다.
- 채취 권한: `can_extract_tsin_rubber`는 `tsin_industrial_capitalism_advance`, `can_extract_tsin_oil`은 `tsin_machine_tools_advance`가 준다(바닐라 원자재도 `can_extract_X`가 있어야 RGO가 돈다).
- 공급:
  - 고무: 이벤트 `tsin_economy.80` 고무 붐이 열대 밀림 농촌 지역(`tsin_potential_rubber_location_trigger`)의 원자재를 `change_raw_material = goods:tsin_rubber`로 바꾼다. 특허권은 최대 3곳과 강제 노동 지점 수정자, 국가 감독은 1곳.
  - 석유: 결정 `tsin_prospect_for_oil`이 바닐라 `prospect_for_coal`과 같은 방식으로 `scripted_geography:tsin_potential_oil`(바쿠, 왈라키아, 갈리치아, 펜실베이니아, 수마트라, 버마 등 19세기 유전 지역)의 한 곳을 유전으로 바꾼다. 비용은 바닐라 `coal_prospecting_cost`.
- 수요: 주민 수요는 넣지 않았다(1337년부터 공급 없는 수요가 생기지 않게). 7시대 생산 방식으로만 쓴다.
  - `tsin_machine_works` 둘째 칸 `tsin_machine_works_oil_lubrication`: 구리 0.2, 석유 0.15 → 기관 0.27(0.7에서 0.33 → 0.27, 이윤율 1.65 → 1.35).
  - `tsin_mechanized_textile_mill` 둘째 칸 `tsin_mechanized_rubber_belts`: 기관 0.3, 석탄 0.5, 고무 0.1, 공구 0.1 → 직물 1.75.
- 그림: 고무는 바닐라 `fiber_crops`, 석유는 `tar` 아이콘의 색조를 바꾼 임시 그림.

사용자 확인 필요: `change_raw_material`이 상품의 `location_potential`과 어긋날 때의 동작, 수요가 생산 방식뿐일 때 고무·석유 가격이 안정되는지, 시추 결정 AI가 적절히 쓰는지.
