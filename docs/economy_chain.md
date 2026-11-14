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

## 사용자 확인 필요

- 기관 공급이 부족할 때 기관 가격이 오르고, 기계화 방직 공장의 증기 동력 방식 수익이 떨어지는지
- 기계 공장이 강철 가격 상승에 반응해 주철 틀로 돌아가는지(AI·자동 선택이 있는 경우)
- 함선 건조 시 기관 수요가 시장에 잡히는지
- 산업 장려 화면에 `tsin_machinery`가 제7시대 이후에만 보이는지
