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

0.7 곁가지 과제(최종 과제의 선행은 아님):

| 과제 | 선행 | 조건 | 보상(기간 보정치) |
|---|---|---|---|
| 자동화 공장 | 기계를 만드는 기계 | 자동화 업그레이드 공장 지점 3곳 | 생산 효율 +2%, 공장 건설 효율 +5% |
| 과밀 해소 | 도시의 성장 | 연립주택·모범 주택 지점 3곳, 수도가 과밀(80%) 아님 | 인구 수용력 +3%, 농민 만족 목표 + |
| 첫 법안 통과 | 도시의 성장 | `var:tsin_bills_passed` 1 이상(`tsin_pass_bill_effect`가 셈) | 정책 변경 비용 −10%, 내각 효율 +2% |
| 강세장 | 기계를 만드는 기계 | 국가 주가 종합지수 150 | 대출 이자 −0.5%p, 시민 권력 +5% |
| 기계화 농업 | 농장에서 공장으로 | 기계화 농장 합계 10레벨 | 월간 식량 +5%, 농기계 생산 +10% |

## 사용자 확인 필요

- 임무 선택 화면에 제7시대 이후에만 나타나는지
- 과제 아이콘(기술 아이콘 재사용)과 삽화가 표시되는지
- `num_of_non_rural >= 4`가 작은 나라에 너무 어렵지 않은지
- `any_owned_location` 안의 `count >= 3`과 위치 스크립트 값 비교(`tsin_location_automated_mill_levels > 0`)가 과제 조건에서 동작하는지
- 법안 제도가 꺼진 나라(의회 없음, 게임 규칙 끔)는 첫 법안 통과 과제를 끝낼 수 없다. 곁가지라 최종 과제는 막지 않는다

## `tsin_modernization` 근대화 개혁 (M6, 선택)

파일: `in_game/common/missions/tsin_modernization_missions.txt`, 보상 `main_menu/common/static_modifiers/tsin_mission_modifiers.txt`, 삽화 `gfx/interface/illustrations/missions/tsin_modernization.dds`(바닐라 `generic_progress_and_literacy`에서 색만 바꾼 임시 그림).

국가 태그 대신 "개항 압력"과 "비산업국"이라는 상태로 열린다. 제7시대 이후 다음 중 하나이면 보이고, 반복하지 않는다.
- 조약항 강화 조약 또는 `tsin_flavor.10` 협상 개항으로 항구를 연 적이 있음(`var:tsin_treaty_ports_opened`).
- 1850년 이후에도 공장 지점이 하나도 없음.

| 과제 | 선행 | 조건 | 보상(기간 보정치) |
|---|---|---|---|
| 외국인 고문 | - | 증기의 시대 연구 | 연구 속도 +5% |
| 군제 개혁 | 외국인 고문 | 뇌관식 소총 연구 | 규율 +3%, 육군 사기 +5% |
| 국영 공창 | 외국인 고문 | 공장 지점 1곳 | 공장 건설 효율 +10% |
| 근대 학교 | 외국인 고문 | 대중사회 연구 | 최대 문해율 +3, 제도 확산 +5% |
| 철도와 전신 | 국영 공창 | 수도와 철도로 이어진 지점 1곳 | 철도 건설비 -15% |
| 조약 개정 (최종) | 군제·학교·철도 | 공장 지점 3곳, 평화 | `tsin_unequal_treaty` 제거, 외교 평판 +1, 연구 속도 +3% (긴 기간) |

사용자 확인 필요:
- 임무를 고른 뒤 첫 공장을 지어 "공장 없음" 조건이 거짓이 되어도 진행 중인 임무가 사라지지 않는지(`visible`을 진행 중에도 다시 검사하는지).
- 대중사회 연구가 비산업국에 너무 늦게 열려 근대 학교 과제가 사실상 막히지 않는지.
