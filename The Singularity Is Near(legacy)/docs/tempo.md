# 시간 압축과 상한 (0.7)

## 1. 원칙
- 하루 틱은 엔진에 고정되어 있어 건드리지 않는다(사용자 결정으로 제외).
- 대신 **같은 시간에 더 큰 변화**가 일어나게 한다. 연구, 건설, 승급, 이주, 제도 확산을 빠르게 하고, 산업화가 진행된 나라일수록 더 빨라진다(가속 단계).
- 빨라진 만큼 **겹겹의 상한**을 둔다. 21세기 지구 인구가 1조가 되는 일은 막아야 한다.

## 2. 변화량 확대
| 장치 | 위치 | 값 |
|---|---|---|
| 제7시대 보정치 | `in_game/common/age/tsin_age_7.txt` | 연구 속도 +10%, 건설 속도 +10%, 승급 속도 +20%, 이주 속도 +25%, 제도 확산 +20% |
| 산업 가속 1단계 | 정적 보정치 `tsin_industrial_acceleration_1` | 연구 +5%, 건설 +5%, 승급 +10% |
| 산업 가속 2단계 | `tsin_industrial_acceleration_2` | 연구 +10%, 건설 +10%, 승급 +20%, 생산 효율 +3% |
| 산업 가속 3단계 | `tsin_industrial_acceleration_3` | 연구 +15%, 건설 +15%, 승급 +30%, 생산 효율 +5% |
| 산업 인구 붐 | `tsin_industrial_population_boom` | 가속 2단계 이상이고 조절기 제동 0단계일 때만 인구 증가 +0.0002 |

가속 점수(매년, `tsin_acceleration_points`):
- 제7시대 제도 수용 1개마다 1점(최대 3).
- 공장 일자리 비중(`tsin_factory_share`, 연간 집계) 0.08 이상 1점, 0.2 이상 1점 더.
- 표준시 채택 결단 1점.
  - `tsin_standard_time_decision`(`in_game/common/decisions/tsin_civic_decisions.txt`). 보임: 철도망 기술. 조건: 전신(`tsin_telegraph_telephone_advance`, 철도역 전신 단계 해금), 철도역 3곳, 중등교육률 10 이상, 금 2배.
  - 효과: 금 −2배, `var:tsin_standard_time`, 표준시 보정치(생산 효율 +2%, 내각 효율 +3%, 영구), 농민 만족 −.
  - 공장이 있으면 `tsin_working_class.10` 공장 시계 이벤트가 나올 수 있다(봉인 / 시간은 돈이다).
- 단계: 2점 이상 1단계, 3점 이상 2단계, 5점 이상 3단계.

## 3. 상한 장치
1. **세계 인구 조절기** (`tsin_update_world_governor_effect`, 1년에 한 번, 관찰 기록기와 같은 전역 변수 패턴):
   - 제7시대 첫해 세계 인구를 `tsin_world_pop_base`에 저장한다(합계는 `tsin_obs_world_population`).
   - 목표 배율 `tsin_pop_target_multiplier`(연도별 직선 보간): 1837년 ×1.0, 1900년 ×1.6, 1950년 ×2.4, 2000년 ×5.5, 2100년 이후 ×7.0.
   - 비율 `tsin_world_pop_ratio` = 세계 인구 ÷ (기준값 × 목표 배율).
   - 제동 단계 `tsin_population_brake`: 비율 1.0 미만 0단계, 1.0 이상 1단계, 1.1 이상 2단계, 1.25 이상 3단계. 기준값의 7배를 넘으면 무조건 3단계(절대 상한).
   - 각국 연간 맥동이 단계에 맞는 `tsin_population_brake_1~3`(인구 증가 −, 식량 소비 +, 수용력 −)을 건다.
   - 게임 규칙 `tsin_population_governor`를 끄면 제동이 걸리지 않는다(시험·비교용).
2. **국가 제동** `tsin_population_pressure`: 한 나라의 연간 인구 증가율이 3%를 넘으면 1년간 인구 증가 −, 이주 유출 +.
3. **수용력 합계 상한**: 모드가 주는 인구 수용력 보정치의 합을 아래 표로 관리하고 바닐라 대비 +80% 이내로 둔다.
4. **인구 변천** `tsin_demographic_transition_1/2`: 평균 문해력과 도시화가 높은 나라는 출생이 줄어 증가세가 꺾인다.
5. **배출구**: 콜레라 대유행 재난, 대이주 상황.
   - 콜레라 `tsin_cholera`(`in_game/common/disasters/tsin_cholera.txt`):
     - 시작: 1830~1875년, 7시대, 다른 재난 없음, 20년 쿨다운. 현대식 상하수도(`tsin_waterworks`) 없이 과밀한 도시·마을이 2곳 이상이어야 한다. 옛 수도교는 막지 못한다.
     - 진행: 매달 `var:tsin_cholera_progress` +1. 수도에 상하수도가 있으면 +1, `global_disease_resistance` 0.1 이상(공중보건 운동 내각 행동의 신호)이면 +1. 60이면 끝난다(치료 없이 5년, 다 갖추면 약 20개월).
     - 손실: 발병 이벤트 `tsin_cholera.2`가 가장 큰 위험 도시 한 곳의 인구를 3% 줄인다(임시 병원은 1.5%). 대유행 한 번에 최대 6회다.
     - 재난 보정치: 인구 증가 −0.001, 도시 월 번영 −0.005, 이주 속도 +10%.
     - 이벤트: `.1` 시작(검역 / 교역 유지 −6 진행), `.3` 펌프 손잡이(+12 진행, 위생학 20년), `.10` 종료(하수도 운동 15년).
     - 그림은 바닐라 대역병 그림을 재채색한 임시 그림이다(`tools/make_placeholder_art.py`).
     - 사용자 확인 필요: 재난의 `on_monthly`에서 변수를 바꾸는 동작, `modifier:global_disease_resistance` 판정, 모든 인구에 `add_pop_size` 음수를 줄 때의 실제 손실.
   - 대이주 `tsin_great_migration`(`in_game/common/situations/tsin_great_migration.txt`):
     - 시작: 1845년 이후, 보내는 나라 2개국 이상. 한 번만 일어난다.
     - 보내는 나라(`tsin_migration_push_trigger`): 독립국 가운데 과밀한 지점이 3곳 이상이거나, 대기근·콜레라 재난, 곡물 위기를 겪는 나라. 이민 행렬(이주 속도 +20%, 식민 이주 +25%, 이주 매력 −10%).
     - 받는 나라(`tsin_migration_pull_trigger`): 수도가 아메리카나 오세아니아에 있고 보내는 나라가 아닌 나라. 이민자의 나라(이주 매력 +25%, 인구 수용력 +2%).
     - 구성원은 해마다 한 번(`global_var:tsin_migration_refresh`) 다시 정한다. 처음 보낼 때 `tsin_migration.1`(송금 / 이민 제한), 처음 받을 때 `.2`(열린 문 / 토박이 우선법)가 나온다.
     - 끝: 시작 10년 뒤 보내는 나라가 없거나, 40년이 지나면 끝난다.
     - 사용자 확인 필요: 바닐라 이주 보정치가 나라 사이(대륙 사이) 이주를 실제로 움직이는지. 움직이지 않으면 보내는 나라의 인구 압력만 줄어든다.

### 수용력 보정치 합계표
| 출처 | 보정치 | 값 |
|---|---|---|
| `tsin_urban_planning_advance` | `global_population_capacity_modifier` | +0.10 |
| 상하수도 `tsin_waterworks` | `local_population_capacity_modifier` | 지점 +0.15 |
| 노동자 연립주택 `tsin_tenement` / 모범 주택 | `local_population_capacity_modifier` | 지점 +0.10 / +0.20 |
| 도시 개조 내각 행동 `tsin_urban_renewal` | `local_population_capacity_modifier` | 지방 +0.05(행동 중에만) |
| 냉동 운송·집약 농업 | 식량 용량(수용력 아님) | — |
| **합계** | | **전역 +0.10 + 도시 지점 최대 +0.40 → 도시 지점 기준 약 +50%, 목표 +80% 이내** |

## 4. 측정
- 관찰 지표: `pop_ratio`(세계 인구 ÷ 목표), `brake`(제동 단계), `accel3`(가속 3단계 나라 수).
- `docs/long_run.md`의 "연 5% 이하" 점검과 함께 본다. 게임 안 동작은 모두 사용자 확인 필요이다.
