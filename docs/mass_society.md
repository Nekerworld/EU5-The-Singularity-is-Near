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

## 노예제 폐지

노예제 자체는 바닐라 `slavery_laws`(`slavery_allowed` / `slavery_outlawed`, 제6시대 `slave_trade_act_advance`가 연다)를 그대로 쓴다. 모드는 그 앞 단계와 뒤처리를 더한다.

| 요소 | 위치 | 내용 |
|---|---|---|
| `tsin_slave_trade_law` 노예무역 | `in_game/common/laws/tsin_abolition_laws.txt` | `tsin_steam_age_advance`가 연다. 노예제가 폐지되면 사라진다. 용인 / 금지(노예 상품 수출입 금지, 인도주의 쪽) |
| 폐지 운동 `tsin_abolitionism` | 국가 변수, `scripted_effects/tsin_movement_effects.txt` | 노예제가 있는 나라에서 매년 `tsin_abolitionism_yearly_growth`만큼 늘고 0~100으로 묶인다 |
| 의제 `pa_tsin_abolish_slavery` | `parliament_agendas/tsin_parliament_agendas.txt` (성직자) | 운동 ≥ 50일 때 상정, 통과하면 `slavery_outlawed` 시행 |
| 이벤트 `tsin_abolition.1~.4` | `in_game/events/tsin_abolition.txt` | 청원, 해방 방식, 도제 기간, 노예 요새 |
| 해방 효과 `tsin_emancipate_all_slaves_effect` | `scripted_effects/tsin_movement_effects.txt` | 자기 나라 노예 인구를 모두 농민으로 바꾼다 |

연간 증가량(`script_values/tsin_movement_values.txt`): 기본 1, 대중사회 시대관 수용 +2, 대중 통신 기술 +2, `free_press` +2, 노예무역 금지 정책 +1, 인도주의 값 > 25 +1, 노예 인구 10% 초과 -2, 폐지론자 탄압 수정자 -4.

해방은 노예 인구를 지우지 않고 농민으로 바꾼다. 노예 상품(`slaves_goods`) 교역은 노예무역 금지 정책과 바닐라 규칙에 맡긴다.

### 운동 틀

바닐라 `common/movements`는 `religion` 또는 `culture`를 반드시 지정해야 해서 이념 운동을 표현할 수 없다. 그래서 운동은 국가 변수(0~100)로 만들고, `tsin_yearly_country_pulse`가 매년 `tsin_update_movements_effect`를 불러 갱신한다. 다른 운동은 같은 파일에 증가량 값과 갱신 블록을 더한다.

사용자 확인 필요:
- 국가 범위에서 `every_pop = { limit = { owner = root ... } change_pop_type = ... }`가 모든 노예 인구에 적용되는지.
- `add_policy`로 바닐라 `slavery_outlawed`와 모드 정책을 시행할 수 있는지.
- `change_variable`의 `add`에 스크립트 값을 넣을 수 있는지, `clamp_variable`이 동작하는지.
- 노예무역 금지 정책의 수출입 금지 보정치가 실제로 노예 교역을 막는지.

## 의회 의제, 특권, 정부 개혁

빅토리아식 "정부 청원"은 계층별 의회 의제로 근사한다. 의제는 M4 법률의 정책을 직접 바꾼다.

| 의제 | 계층 | 상정 조건 | 통과 효과 |
|---|---|---|---|
| `pa_tsin_factory_acts` 공장법 제정 | 평민 | 노동 규제 없음 정책 | 공장법 정책 시행 (대중 통신 기술이 있으면 확률 2배) |
| `pa_tsin_restore_landlord_rights` 지주 권리 회복 | 귀족 | 유상 해방 정책 | 농노제 유지 정책, 농노제 쪽 이동 |
| `pa_tsin_railway_charters` 철도 회사 특허 | 시민 | 철도망 기술, 철도 국유화 개혁 없음 | 10년 철도 비용 -10%, 시민 만족 |
| `pa_tsin_restore_concordat` 정교 협약 회복 | 성직자 | 정교 분리 정책 | 정교 협약 정책, 영성주의 쪽 이동 |

곡물법 의제(M3)와 노예제 폐지 의제(위)도 같은 파일에 있다.

계층 특권 (`in_game/common/estate_privileges/tsin_age7_privileges.txt`, 모두 제7시대 이후):

| 특권 | 계층 | 효과 |
|---|---|---|
| `tsin_chambers_of_commerce` 상공회의소 | 시민 | 공장 건설 효율 +10%, 금권정 쪽 |
| `tsin_officer_corps_monopoly` 장교단 독점 | 귀족 | 육군 사기 +5%, 귀족정 쪽 |
| `tsin_church_school_network` 교회 학교망 | 성직자 (정교 분리 아님) | 월간 문해율 +0.01, 영성주의 쪽 |
| `tsin_mutual_aid_societies` 공제 조합 | 평민 (노동 운동 기술 필요) | 기대 수명 +1, 공동체 쪽 |

시대 고유 정부 개혁 (`in_game/common/government_reforms/tsin_age7_reforms.txt`, `age = age_7_industrialization`, 시행 2년):

| 개혁 | 조건 | 효과 |
|---|---|---|
| `tsin_factory_inspectorate` 공장 감독관 | 노동 운동 기술 | 생산 효율 -1%, 평민 만족, 노동자 최대 문해율 +5, 공동체 쪽 |
| `tsin_civil_service_examinations` 공무원 시험제 | 보통 교육 기술 | 내각 효율 +10%, 월간 통제력 +0.01, 귀족 불만, 중앙집권 쪽 |
| `tsin_universal_conscription` 국민 개병제 | — | 인력 +15%, 보충 속도 +5%, 평민 불만, 양 중시 쪽 |
| `tsin_railway_nationalization` 철도 국유화 | 철도망 기술 | 철도 비용 -15%, 시민 불만, 중앙집권 쪽 |

그림은 바닐라 개혁·특권 아이콘의 색상만 바꾼 임시 그림이다(`tools/make_placeholder_art.py`).

사용자 확인 필요:
- 정부 개혁 화면의 시대 열에 제7시대 개혁 4개가 나오는지(`gui/government_reform_per_age.gui`가 새 시대를 자동으로 그리는지).
- 의제의 `add_policy`가 같은 법의 기존 정책을 바꾸는지.
- 특권 목록에 제7시대 이후에만 새 특권이 나오는지.

## 운동 5종

노예제 폐지 운동과 같은 틀(국가 변수 0~100, 매년 `tsin_update_movements_effect`)을 쓴다. 운동 하나의 처리는 `tsin_movement_tick_effect = { VAR GROWTH AGITATION }`가 맡는다. 값이 60 이상이 되면 선동 보정치가 붙고, 50 아래로 떨어지면 떨어진다(오르내림 반복 방지).

| 변수 | 운동 | 연간 증가 (`script_values/tsin_movement_values.txt`) | 요구가 충족되면 | 선동 보정치 (≥ 60) |
|---|---|---|---|---|
| `tsin_liberalism` | 자유주의 | 기본 1, 대중사회 시대관 +1, `free_press` +1, 자유주의 값 > 25 +1, 집회 금지 +1 | 결사의 자유 정책 -4 | 시민 목표 만족 -5%, 자유주의 쪽 |
| `tsin_nationalism` | 민족주의 | 기본 1, 대중 통신 +1, 속국 +2, 호전 값 < -25 +1, 독립국 -1 | (없음, 상황·전쟁명분이 쓴다) | 인력 +5%, 호전 쪽 |
| `tsin_labor_unionism` | 노동 운동 | 노동 운동 기술 +2, 공장 지점 5곳 이상 +2, 노동 규제 없음 +1 | 공장법 -2, 노동 보호 -4, 집회 금지 -1 | 평민 목표 만족 -5%, 생산 효율 -2% |
| `tsin_socialism` | 사회주의 | 기본 -1, 노동 운동 ≥ 50 +3, 공동체 값 > 25 +1, 노동 규제 없음 +1, 집회 금지 +1 | 사회 보험 정책 -3 | 평민 -5%, 시민 -2.5%, 공동체 쪽 |
| `tsin_womens_suffrage` | 여성 참정권 | 보통 교육 +1, 대중 통신 +1, 인도주의 값 > 25 +1, 집회 금지 -1 | (제7시대에는 충족 법 없음) | 시민 -2.5%, 인도주의 쪽 |

집회 금지는 자유주의·사회주의를 키우고 노동 운동·여성 참정권은 누른다(지하화). 사회적 가치 축 방향은 `00_default.txt` 기준이다. `belligerent_vs_conciliatory`는 왼쪽이 호전이므로 민족주의 조건은 `< -25`로 썼다.

법률 요구 연결 (의회 의제):
- `pa_tsin_freedom_of_association` (시민): 자유주의 ≥ 50, 결사의 자유 정책 시행, 자유주의 -20.
- `pa_tsin_social_insurance` (평민): 사회주의 ≥ 40 또는 노동 운동 ≥ 60, 사회 보험 정책 시행, 사회주의 -20.
- `pa_tsin_factory_acts`: 노동 운동 ≥ 50이면 확률 +10.

운동 값은 국민의 봄 상황, 사회 이벤트, 급진성 지도 모드가 읽는다. 사용자 확인 필요:
- 스크립트 효과 매개변수(`$VAR$`)를 `var:$VAR$` 비교와 `has_variable`에 넣을 수 있는지.
- `any_owned_location = { count >= 5 ... }`가 국가 범위 스크립트 값의 `limit`에서 동작하는지.
