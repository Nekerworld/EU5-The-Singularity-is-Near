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

## 사용자 확인 필요

- `has_road_of_type_to`가 철도 경로 전체를 따라가는지(바닐라 `flavor_mug.txt`의 라호르→쿨나 예시로 보아 경로 검사로 추정), 수도 외 도시에서 철도역이 지어지고 연결이 끊기면 철거되는지
- `TRY_REPLACE`로 바꾼 철도 건설 수요가 건설 화면에 석탄·도구로 표시되는지
- 비료·폭약이 부족할 때 시비 농지·발파 채굴장의 보정치가 약해지는지. 약해지지 않는다면 비료·폭약은 유지비일 뿐이고, 수요 연결은 시장 가격으로만 작동한다.
- 발파 채굴장이 금·은 광산에도 지어지는지, 화폐 주조에 이상이 없는지
- 기관 공급이 부족할 때 기관 가격이 오르고, 기계화 방직 공장의 증기 동력 방식 수익이 떨어지는지
- 기계 공장이 강철 가격 상승에 반응해 주철 틀로 돌아가는지(AI·자동 선택이 있는 경우)
- 함선 건조 시 기관 수요가 시장에 잡히는지
- 산업 장려 화면에 `tsin_machinery`가 제7시대 이후에만 보이는지
