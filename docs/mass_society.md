# 대중사회 (M4)

## 기술 (`in_game/common/advances/tsin_5_mass_society.txt`)

뿌리는 `tsin_mass_society_advance`(대중사회 시대관 수용 필요). 기술은 법률을 열기만 하고, 시행은 의회와 계층에 맡긴다.

| 기술 | 선행 | 효과 |
|---|---|---|
| `tsin_urban_planning_advance` 도시 계획 | 뿌리 | 인구 수용력 +10%, 비농촌 이주 매력 +0.25 |
| `tsin_modern_sewerage_advance` 근대 하수도 | 도시 계획 | 질병 저항 +0.1, 기대 수명 +3 |
| `tsin_mass_consumption_advance` 대중 소비 | 도시 계획 | 가구·종이 주민 수요 +10%, 시민 목표 만족도 소폭 + |
| `tsin_universal_education_advance` 보통 교육 | 뿌리 | 최대 문해율 +10, 월간 문해율 +0.02 |
| `tsin_vocational_education_advance` 직업 교육 | 보통 교육 | 노동자 최대 문해율 +10, 생산 효율 소폭 + |
| `tsin_mass_communication_advance` 대중 통신 | 뿌리 | 월간 문해율 +0.01, 내각 효율 +5% |
| `tsin_labor_movement_advance` 노동 운동 | 뿌리 | 인구 승급 속도 +0.05 |
| `tsin_social_insurance_advance` 사회 보험 | 노동 운동, 대중 통신 | 기대 수명 +2, 평민 목표 만족도 소폭 + |

사용자 확인 필요: `global_pop_promotion_speed`의 단위(바닐라 사용례가 -0.05와 0.001뿐이라 0.05가 큰 값일 수 있음).
