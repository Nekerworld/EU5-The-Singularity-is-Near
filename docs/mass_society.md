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

## 법률 (`in_game/common/laws/tsin_society_laws.txt`)

교육·언론·이민·노예제는 바닐라 법률(`education_masses_law`의 `secular_education`, `press_law`의 `free_press`, `immigration_law`, `slavery_laws`의 `slavery_outlawed`)이 이미 있으므로 새로 만들지 않았다. 바닐라 법을 덮어쓰지 않는다.

| 법률 | 여는 기술 | 정책 (조건) |
|---|---|---|
| `tsin_labor_law` 노동법 | `tsin_labor_movement_advance` | 규제 없음(생산 효율 +, 평민 불만, 시민 만족) / 공장법(노동자 문해율, 평민 만족, 인도주의 쪽) / 노동 보호(사회 보험 기술 필요; 생산 효율 -, 평민 크게 만족, 시민 불만, 공동체 쪽) |
| `tsin_welfare_law` 복지법 | `tsin_social_insurance_advance` | 자선 구호(성직자 만족) / 구빈법(세수 효율 소폭 -, 기대 수명 +1) / 사회 보험(세수 효율 -, 평민 만족, 기대 수명 +2) |
| `tsin_taxation_law` 직접세 | `tsin_mass_society_advance` | 간접세 / 소득세(세수 효율 +, 시민 불만) / 누진세(대중 통신 기술 필요; 세수 효율 ++, 귀족·시민 불만, 평민 만족) |
| `tsin_assembly_law` 결사·집회법 | `tsin_mass_communication_advance` | 집회 금지(왕실 권력 +, 절대주의 쪽) / 허가제 / 결사의 자유(노동 운동 기술 필요; 왕실 권력 -, 자유주의 쪽) |
| `tsin_land_reform_law` 토지 개혁 | `tsin_mass_society_advance` | 농노제 유지 / 유상 해방(도시 이주 +, 자유민 쪽) / 완전 해방(귀족 권력 -, 귀족 크게 불만, 평민 크게 만족, 도시 이주 ++) |
| `tsin_church_state_law` 교회와 국가 | `tsin_universal_education_advance` | 국교 / 정교 협약(문해율 +5) / 정교 분리(성직자 권력 -, 성직자 크게 불만, 문해율 +5, 인도주의 쪽) |

사용자 확인 필요: 법률을 처음 열었을 때 어느 정책이 기본으로 잡히는지(바닐라처럼 첫 정책인지), 정책 `allow`의 `has_advance`가 동작하는지.
