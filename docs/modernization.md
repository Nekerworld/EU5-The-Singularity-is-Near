# 방어적 근대화 (0.7)

상황 `tsin_defensive_modernization`은 탄지마트·메이지 유신·양무운동·무함마드 알리형 개혁을 나라 태그 없이 **개항 압력**(`var:tsin_treaty_ports_opened`) 기준으로 묶습니다. 기존 지역 이벤트 `tsin_flavor.10`(포함)과 `tsin_flavor.30`(근대화 칙령)을 단계 이벤트로 흡수했습니다.

## 단계

| 단계 | 이벤트 | 조건 | 결과 |
|---|---|---|---|
| 개항 압력 | `tsin_flavor.10` 협상 개항, 또는 조약항 강화 | 지역 이벤트(풍미 예산 사용) | `var:tsin_treaty_ports_opened` |
| 상황 시작 | — | 1840년 이후, 개항 압력을 받은 나라가 있음 | 한 판에 한 번 |
| 1. 근대화 칙령 | `tsin_flavor.30` | 개항 압력, 거부 쿨다운·좌절·성공 아님 | 국가 개편 또는 자강: 단계 1, 3년 대기. 거부: 10년 뒤 다시 옴, 두 번째 거부는 좌절 |
| 2. 구세력의 반동 | `tsin_modernization.10` | 단계 1, 대기 끝 | 진압(안정도·귀족 불만, 신식 군대 10년, 5년 대기) / 매수(6개월 세입, 8년 대기) → 단계 2. 굴복 → 좌절 |
| 3. 성공 | `tsin_modernization.20` | 단계 2, 대기 끝, 공장 1곳 이상, 안정도 0 이상 | `tsin_modernized`, 근대 국가 30년 |
| 3. 좌절 | `tsin_modernization.30` | 반동 굴복 또는 두 번째 거부 | 좌절된 근대화 15년, 20년 뒤 칙령 다시 가능 |
| 종료 | — | 1880년 이후 진행 중인 나라가 없음, 또는 1900년 | — |

- 단계 이벤트는 `on_action` `tsin_modernization_yearly_pulse`(개항 압력을 받고 끝나지 않은 나라만, 연 25%)에서 나오며 풍미 예산을 쓰지 않습니다. `tsin_flavor.30`은 `tsin_flavor_yearly_pulse`에서 빠졌습니다.
- 칙령 선택지의 기존 보정치(`tsin_flavor_reorganization_edict`, `tsin_flavor_self_strengthening`)는 그대로입니다.
- 근대화 개혁 임무 팩 `tsin_modernization`은 그대로 개항 압력으로 열립니다.

## 보정치

| 키 | 효과 |
|---|---|
| `tsin_modernization_new_army` | 규율 +3%, 공장 건설 효율 +5% |
| `tsin_modernized_state` | 연구 속도 +10%, 내각 효율 +5%, 생산 효율 +3% |
| `tsin_failed_modernization` | 연구 속도 −5%, 상인 힘 −5% |

## 사용자 확인 필요

- 상황 패널·지도 색·힌트 표시.
- 이미 `tsin_flavor_reform_edict_done`이 있는 0.6 세이브의 나라는 단계 변수가 없어 반동·성공 단계로 가지 않습니다(세이브 이전 할 일에서 처리).
