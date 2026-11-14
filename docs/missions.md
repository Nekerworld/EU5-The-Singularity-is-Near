# 임무 팩

## `tsin_industrialization` 산업 국가로 (M3)

파일: `in_game/common/missions/tsin_industrialization_missions.txt`, 보상 `main_menu/common/static_modifiers/tsin_mission_modifiers.txt`, 삽화 `gfx/interface/illustrations/missions/tsin_industrialization.dds`(바닐라 `generic_capital_economy`에서 색만 바꾼 임시 그림).

바닐라 `generic_*_mission_pack.txt` 구조를 따른다. 제7시대 이후, 읍·도시가 1곳 이상인 국가에 보이고, 반복하지 않는다. 국가 태그 조건은 없다.

| 과제 | 선행 | 조건 | 보상(기간 보정치) |
|---|---|---|---|
| 농장에서 공장으로 | - | 공장 지점 3곳(`tsin_has_factories_trigger`) | 공장 건설 효율 +10% |
| 기계를 만드는 기계 | 농장에서 공장으로 | 기계 공장 1곳 | 기관 생산 +10% |
| 도시의 성장 | 농장에서 공장으로 | 읍·도시 4곳(`num_of_non_rural >= 4`) | 도시 이주 매력 +25% |
| 첫 철도 | 농장에서 공장으로 | 수도와 철도로 이어진 지점 1곳 | 철도 건설비 -15% |
| 철도 붐 | 첫 철도 | 철도역 3곳(`total_effective_building_levels:tsin_railway_station`) | 철도 건설비 -10%, 공장 건설 효율 +5% |
| 산업 국가 (최종) | 기계·도시·철도 붐 | 공장 지점 8곳 | 생산 효율 +3% (긴 기간) |

## 사용자 확인 필요

- 임무 선택 화면에 제7시대 이후에만 나타나는지
- 과제 아이콘(기술 아이콘 재사용)과 삽화가 표시되는지
- `num_of_non_rural >= 4`가 작은 나라에 너무 어렵지 않은지
