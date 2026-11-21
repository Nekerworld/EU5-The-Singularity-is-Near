# V 트랙 인게임 확인 목록 (완료 아님)

플레이 전에는 어떤 항목도 완료로 쓰지 않는다.

## V 공통 / V1
- 정책 `country_modifier`의 `allow_female_cabinet = yes`가 내각 후보 UI에 즉시 반영되는지
- 하렘 법 `allow_female_cabinet = no`와 참정권 정책 `yes`가 동시에 걸릴 때 병합 규칙
- `block_female_cabinet`이 `allow`보다 우선하는지
- 법 해금 직후 엔진이 기본 정책을 자동 선택하는지 (모든 새 법은 첫 정책을 기본으로 두고 `add_policy`로 지정)

## V3 농노제 폐지
- `TRY_INJECT:serfdom_vs_free_subjects`의 `allow`가 도중에 거짓이 되면 값이 사라지는지, 보정치도 같이 사라지는지
- 값이 없는 나라에서 바닐라 법·의회·반란이 `societal_value:serfdom_vs_free_subjects`를 읽을 때 `error.log` 오류가 나는지
- `add_country_modifier` + `months = -1`이 세이브 로드 후에도 유지되는지 (`add_country_modifier_forever`는 미확인이라 쓰지 않음)
- 월간 종결 이벤트가 나라당 1회만 뜨는지, `tsin_flavor.20`과 이중으로 뜨지 않는지
- 재농노화 정책·의제가 폐지 후 막히는지

## V2 / V4
- 해군 이념 모디파이어가 함대 유지비·봉쇄·전통에 실제로 붙는지
- `administrative` 범주에 경찰 법을 추가했을 때 정부 화면 정렬에 문제가 없는지
- 보건 법의 `global_disease_resistance`가 콜레라 공중보건 신호(≥0.1)를 의도치 않게 켜지 않는지

## V1/V2/V4 구현 뒤 사용자 확인 필요 (코드 검증 완료, 인게임 미확인)

구현 위치: `era_7/in_game/common/laws/tsin_women_rights_law.txt`, `tsin_naval_ideology_law.txt`, `tsin_police_health_laws.txt`. 법안 분야 180은 `tools/gen_bill_events.py`가 만든다. 정적 검사는 `tools/tests/test_v_track_laws.py`. 아래는 모두 사용자 확인 필요다.

### V1 여성권
- 사용자 확인 필요: `tsin_universal_education_advance`의 `unlock_law`로 법이 열린 직후, 엔진이 첫 정책(`tsin_women_no_rights_policy`)을 기본으로 고르는지. 못 고르면 해금 이벤트에서 `add_policy`가 필요하다.
- 사용자 확인 필요: 정책 `allow`의 변수 조건(`has_variable = tsin_womens_suffrage`, `var:... >= N`)이 정책 툴팁과 법안 선택지 `trigger`(생성기 복사본) 양쪽에서 변수가 없는 나라에서도 오류 없이 거짓으로 읽히는지.
- 사용자 확인 필요: 노동 단계가 요구하는 공장법 이상(`tsin_factory_acts_policy` 또는 `tsin_labor_protection_policy`)이 `tsin_labor_law`가 해금되지 않은 나라에서 단순히 거짓이 되는지.
- 사용자 확인 필요: `tsin_enact_policy_effect`의 `add_policy`가 `allow`(순차·운동 조건)를 무시하는지. 법안 제도가 꺼져 있으면 `tsin_table_bill_effect`가 바로 시행하므로, 무시한다면 단계를 건너뛸 수 있다.
- 사용자 확인 필요: 정책을 되돌릴 때(참정권 → 재산권 등) 이미 임명된 여성 내각원이 유지되는지. 이 법은 되돌리기를 막지 않는다(기본 정책을 포함해 모든 정책이 법안으로 열려 있다).
- 사용자 확인 필요: `tsin_society.70` 선택지 a는 법안 상정으로 바꾸면서 운동 −20을 뺐다(통과 시점에 단계 조건 50이 유지되어야 하므로). 이후 운동은 정책의 `has_policy` 감소 항(재산권 −1, 노동 −1, 참정권 −3)으로 줄어든다. 법안을 상정할 단계가 없는 나라(이미 참정권 단계이거나 법이 없는 나라)는 예전처럼 운동 −20만 적용한다.
- 장군·통치자 개방(`allow_female_leader`, `gender_equality`)은 이번 범위에 넣지 않았다.

### V2 해군 이념
- 사용자 확인 필요: `potential`을 `num_of_ports > 0` 또는 `has_law = tsin_naval_ideology_law`로 쓴 형식이 바닐라 `maritime_law`(`has_law = maritime_law`)와 같은지, 즉 모드 법에서도 `has_law`가 `law:` 접두 없이 통하는지.
- 사용자 확인 필요: `unlock_law = tsin_naval_ideology_law`를 `tsin_steamship_lines`에 둔 해금 방식. 바닐라 `maritime_law`에는 `unlock_law`가 없다.
- 사용자 확인 필요: 쓴 모디파이어(`navy_light_ship_maintenance_cost_modifier`, `blockade_efficiency`, `ship_capture_chance`, `own_coast_naval_combat_bonus`, `trade_range_modifier`, `merchant_power_from_maritime_modifier`, `monthly_prestige`, `expected_navy_size_modifier`, `monthly_navy_tradition`, `navy_maintenance_efficiency`)가 `error.log` 오류 없이 붙는지. 모두 바닐라 법이 이미 쓰는 이름이다.
- 사용자 확인 필요: 청년학파의 "대형 함선 불이익"은 대형 함선 전용 모디파이어 이름을 찾지 못해 귀족 만족 소폭 감소로 대신했다.
- 사용자 확인 필요: `allow`의 `OR = { has_advance ... }`와 두 `has_advance`의 AND가 군사 법 정책에서 문제없이 동작하는지(바닐라 군사법은 이 형식을 쓰지 않는 정책이 많다).
- 이 법은 법안 시스템 대상이 아니다. `CATEGORIES`, `tsin_bill_law_policy_trigger`, `tsin_bill_reform_policy_trigger`에 넣지 않았다.

### V4 경찰·보건
- 사용자 확인 필요: 경찰 법 정책 이름(`tsin_police_night_watch_policy` 등)과 보건 정책 이름(`tsin_health_laissez_faire_policy`, `tsin_health_quarantine_policy`, `tsin_health_board_policy`)은 계획에 확정된 ID가 없어 구현 때 정했다. 바꾸려면 법 파일, 현지화, 테스트, 생성기 출력을 함께 고쳐야 한다.
- 사용자 확인 필요: 경찰 정책 해금 기술 조건(국가 경찰: `tsin_mass_communication_advance`, 정치 경찰: `tsin_national_census_advance`)과 보건청의 `tsin_antiseptic_surgery_advance`는 구현 때 정한 값이며 계획의 수치가 아니다.
- 사용자 확인 필요: 보건 법이 `global_disease_resistance`를 쓰지 않아 콜레라 신호(≥0.1)를 건드리지 않지만, `global_life_expectancy`가 다른 판정에 쓰이는지는 확인하지 않았다.
- 사용자 확인 필요: 정치 경찰과 자유주의·여성 참정권 운동(`tsin_update_movements_effect`)의 연결은 이번에 만들지 않았다(운동 성장 값은 변경 없음).
- 사용자 확인 필요: `administrative` 범주에 모드 법을 추가했을 때 정부 화면의 정렬과 `tsin_police_law_CATEGORY` 현지화 키 사용.
- 경찰은 `tsin_bill_reform_policy_trigger`에 넣지 않았다(질서 쪽 정책이라 개혁 압력을 받지 않음). 보건의 위생·검역과 보건청은 개혁 정책으로 넣었다.

### 법안 분야 180
- 사용자 확인 필요: `tsin_legislation.100`의 선택지 수(분야 8개)와 이벤트 UI 표시, `c180` 현지화.
- 사용자 확인 필요: 생성기가 법 파일을 읽는 글롭을 `tsin_*_laws.txt`에서 `tsin_*_law.txt`까지 넓혔다. `tsin_company_regime_law.txt`도 이제 읽히지만 분야에는 들어 있지 않다.
