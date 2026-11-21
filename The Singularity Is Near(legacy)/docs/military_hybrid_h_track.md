# 8시대 이후 HOI4 하이브리드 군사 (H축)

대상: 8시대 대전(`age_8_world_wars`)과 9시대 이후. 바닐라 육군 이동·스택·AI 모집·식량 보급과 TSIN 철도·자동차 거점은 그대로 두고, 그 위에 군수 비축, 현대 편제, 연료, 공군을 얹는다. 전선·전투계획·장갑/관통 공식은 만들지 않았다.

**모든 항목이 `사용자 확인 필요`다.** 엔진 실험(H0)은 하지 않았다: `docs/h0_engine_probes.md`. 숫자는 모두 자리표시이며 균형을 맞추지 않았다.

## 생성기와 실행 순서

| 단계 | 생성기 | 주 산출 (원본은 `era_8`, 일부 `era_9`) |
|---|---|---|
| 공통 | `tools/h_track_common.py` | 쓰기·`--check`·era_8/era_9 매니페스트 등록. 다른 시대 원본은 등록하지 않는다 |
| H1 | `tools/gen_military_stockpile.py` | 발전 2, 공장 4(소화기·지원 화포·기갑 차량·항공기), 게이트 트리거, 비축 값·효과, 월간/전투 on_action, 부족 수정자 3 |
| H2 | `tools/gen_modern_training.py` | 유닛 능력 `tsin_modern_field_drill`, 8시대 템플릿 6, 8시대 유닛 6, 9시대 유닛 2, 발전 7+2, 유닛 역할 트리거 |
| H3 | `tools/gen_fuel_system.py` | 연료 값·효과, 월간 on_action, 연료 수정자 2 |
| H4 | `tools/gen_airforce_hybrid.py` | 발전 4, 지역 비행장·대공포대, 항공기 4종 비축, 일반 행동 5, 전시 월간 작전 효과 |

모두 `python -B tools/gen_*.py`로 쓰고(`--check`로 읽기 전용 비교), 한 번에 돌리면 된다. 쓰고 나면 era 매니페스트 등록과 실행 미러 동기화(`era_layout.sync`)를 한다. 같은 일을 `python -B tools/sync_eras.py --register`로도 할 수 있다. H1의 트리거·효과는 H2 유닛 역할 트리거, H4 발전 ID를 참조하므로 네 생성기를 모두 실행해야 게임에서 오류가 나지 않는다.

## 새 ID (중복 검사를 마침: era_7/8/9와 `in_game` 전체)

- 발전(8시대): `tsin_mass_production_arms_advance`, `tsin_armored_vehicle_industry_advance`, `tsin_modern_field_drill_advance`, `tsin_armored_cars_advance`, `tsin_tank_warfare_advance`, `tsin_airborne_infantry_advance`, `tsin_mechanized_infantry_advance`, `tsin_self_propelled_artillery_advance`, `tsin_motor_supply_column_advance`, `tsin_aircraft_industry_advance`, `tsin_regional_airbase_advance`, `tsin_anti_aircraft_advance`, `tsin_air_operations_advance`
- 발전(9시대): `tsin_main_battle_tank_advance`, `tsin_rocket_artillery_advance`
- 건물: `tsin_small_arms_works`, `tsin_support_artillery_works`, `tsin_armored_vehicle_works`, `tsin_aircraft_works`, `tsin_airbase`, `tsin_anti_air_battery`
- 유닛: 8시대 `a_tsin_armored_car_recon`(경기병), `a_tsin_tank_battalion`(중기병), `a_tsin_mountain_paratroopers`(경보병), `a_tsin_mechanized_infantry`(중보병), `a_tsin_self_propelled_battery`(포병), `a_tsin_motor_supply_column`(보조). 9시대 `a_tsin_main_battle_tank`, `a_tsin_rocket_artillery_battery`
- 새 재화는 만들지 않았다. 기존 `firearms`, `cannons`, `tsin_engines`, `steel`, `tsin_oil`, `tsin_rubber`, `tsin_explosives` 등을 쓴다(모든 재화는 각종 수정자 정의를 요구하므로 신규 재화는 보류).
- **보존**: `tsin_capital_airfield`, `tsin_motor_transport_depot`, `tsin_powered_flight_advance`, `tsin_aerial_observation_advance`, `tsin_motor_supply_columns_advance`는 건드리지 않았다. H축은 이들을 읽기만 한다(수도 비행장 단계 → 항공 수용 한도, 자동차 거점 → 연료 저장·유입).

## 게이트 (7시대 세이브 불변)

`zzz_tsin_h1_gates.txt`: `tsin_h_age8_trigger`(= `current_later_age_8_world_wars_trigger`), `tsin_h_stockpile_gate_trigger`(+`tsin_mass_production_arms_advance`), `tsin_h_fuel_gate_trigger`(+`tsin_motor_transport_advance`), `tsin_h_air_gate_trigger`(+`tsin_aircraft_industry_advance`). 월간 on_action은 모두 이 게이트를 `trigger`에 둔다. 전투 손실 훅은 게이트와 `tsin_h_init`가 있을 때만 차감한다. 공군 작전은 추가로 `at_war = yes`일 때만 돈다.

## 변수

| 이름 | 범위 | 의미 |
|---|---|---|
| `tsin_h_init`, `tsin_h3_init`, `tsin_h4_init` | 국가 | 단계별 초기화 완료 |
| `tsin_h_n_infantry/_artillery/_armored/_motorized` | 국가 | 연대 역할별 수(월 1회 갱신, `tsin_h_count_stamp`) |
| `tsin_eq_small_arms/_support_artillery/_armored_vehicles/_aircraft_stockpile` | 국가 | 장비 비축(시작 60/30/20/0, 상한 600, 하한 -300). 항공기는 분배 전 풀 |
| `tsin_line_eff_*` | 국가 | 생산 라인 효율 0~1(회복 +0.05/월) |
| `tsin_h_short_*` | 국가 | 부족 수정자 적용 중 표시 |
| `tsin_fuel_stockpile`, `tsin_fuel_state` | 국가 | 연료(시작 50), 상태 0 정상/1 부족 임박/2 고갈 |
| `tsin_fuel_penalty_on` | 국가 | 연료 수정자 적용 중 표시 |
| `tsin_air_fighter/_cas/_bomber/_transport_stockpile` | 국가 | 항공기 4종 비축 |
| `tsin_air_target_superiority/_cas/_bombing/_supply` | 국가 | 지정한 지방(스코프 값) |
| `tsin_air_active_aircraft`, `tsin_air_enemy_fighters`, `tsin_air_superiority_index` | 국가 | 이번 달 출격 항공기, 교전 중인 적 전투기, 제공권 지수 -1~1 |
| `tsin_h_fuel_market_off` | 전역 | 있으면 연료 시장 구매 중지 |

## H1 군수·비축

- 공장 4종은 밀(`is_mill`) 형식이며 두 가지 생산 라인(PM)이 있고 기존 재화를 만든다: 소화기=`firearms`, 지원 화포=`cannons`, 기갑 차량·항공기=`tsin_engines`. 투입재 가치의 1.15배를 산출해 AI가 손익으로 지을 수 있다(바닐라 밀과 같은 방식, 생성기가 계산).
- 월간 정산(`tsin_h1_stockpile_monthly_effect`): 비축 += 공장 단계 × 단계당 수율(8/4/3/2) × `tsin_line_eff_*` + 기본 예비(수요 기준의 30%) − 수요. 수요 = 연대 수 × 단가(소화기 0.12/보병, 화포 0.30/포병, 기갑 0.40/기갑 + 0.15/차량화) × 전시 가중(평시 0.4). 상·하한을 넘으면 자른다.
- 전투 손실: `on_battle_won`/`on_battle_lost`에서 각 쪽이 `scope:lost_land_units`(병사 수) × 계수(소화기 0.004, 화포 0.0005, 기갑 0.0008)를 차감한다.
- 부족: 비축 < 0이고 (전시이거나 -150 미만)이면 군대에 정적 수정자(`tsin_eq_shortage_small_arms/_support_artillery/_armored_vehicles`, 31일 갱신)를 붙이고 회복하면 제거한다. 보병 전투력 -15%·규율 -5%·보충 -25%, 포병 -20%, 기갑 -20%·이속 -10% 등이다.
- PM 전환 감지는 없다. `tsin_h_retool_*_effect`(효율 0.5로 감소)는 수동 호출용이다(P1).
- AI: 모든 새 유닛은 `buildable = yes`, 공장은 시장 산출이 있어 AI가 건설한다. 장비 비축 자체는 AI가 직접 관리하지 않는다.

## H2 편제·훈련

- A안: 바닐라 `UnitTemplate`과 진형은 그대로. 8시대 템플릿 `a_age_8_world_wars_*` 6종(숨김, 7시대 사다리 다음 단계)을 만들고 새 유닛이 `copy_from`한다. 유닛 능력치는 7시대와 같이 `copy_from` 뒤 가산으로 가정한다(미확인).
- 6병과 대응: 경기병→장갑차 정찰대, 중기병→전차 대대, 경보병→산악·공정 보병, 중보병→기계화 보병, 포병→자주포 포대(9시대 로켓 포병), 보조→차량화 수송대. 9시대 주력 전차는 전차 대대를, 로켓 포병은 자주포를 `copy_from`한다.
- 건조/유지 재화는 `tsin_age8_h2_land_demands.txt`, `tsin_age9_h2_land_demands.txt`에 있다(총기·화포·엔진·석유·고무 등).
- 현대식 야전 훈련: `drill_army` 패턴. 경험 +3.5(바닐라 2.5), 유지 효율 -40%(-25%), 사기 -90%(동일), `cancel_on_combat`·이동·공성·지휘관 없음에서 해제. 소화기 비축이 음수이면 시작할 수 없다. 별도 장비 소모 가중은 유지비 효율 감소로만 대신한다.

## H3 연료

- 저장 한도 = 100 + 석유 저장고 120/단계 + 자동차 거점 60/단계 + 지역 비행장 40/단계.
- 유입: 기본 1.5 + 자동차 거점 0.5/단계 + 수도 시장에서 `tsin_oil` 최대 6개 구매(1 오일 = 5 연료, 국고 2%·시장 재고·남은 용량 한도, 관측한 재고 감소분만 반영).
- 소비: (기갑 연대 × 0.6 + 차량화 연대 × 0.25 + 전월 출격 항공기 × 0.15) × 전시 2.0(평시 0.3).
- 상태 2(고갈)이면 기갑·차량화 연대가 든 군대에 `tsin_fuel_depleted`(이속 -40%, 기갑 전투력 -30%·-20%, 중보병 -5%, 규율 -5%). 상태 1(저장의 20% 미만)이면 `tsin_fuel_low`. 상태 2에서는 공군 출격 효과가 멈춘다.

## H4 공군

- 항공기 공장 산출(풀)을 월 최대 20대씩 전투기 35%·근접지원기 30%·폭격기 15%·수송기 20%로 나눈다(수용 한도 이내).
- 임무 배정: 일반 행동 `tsin_air_target_superiority/_cas/_bombing/_supply`가 지방을 고르고, `tsin_air_recall`이 모두 지운다. 가격 0. Area 타게팅은 쓰지 않았다(P4).
- 전시 월간 작전(`at_war = yes`만): 제공권 지수 = (아군 전투기 − 교전 중 적 전투기) / (합 + 1). > 0.15이면 목표 지방의 아군에 `tsin_air_superiority_bonus`, < -0.15이면 `tsin_air_inferiority_penalty`. CAS는 전투 중 적 부대에 `damage_unit_percent` 0~3%(대공포 있으면 0~1.5%)와 사기 피해, 월 3% 손실. 전략 폭격은 적 소유 지점당 12%(대공포 5%)로 건물 1단계 파괴와 번영 감소, 공수는 포위된 아군에 식량 5~10%.
- AI: 전시에 전투 중인 첫 군대의 지방을 제공권·CAS·공수 목표로 자동 지정한다. 폭격은 자동 지정이 없다.
- 시설: 지역 비행장(수용 +12, 최대 3단계), 대공포대(최대 3단계). 레이더는 이번에 만들지 않았다.

## 남은 일 (이번 구현에 없음)

- **H0 실험 5개 전부** (`docs/h0_engine_probes.md`).
- **H5 UI**: `unit_overview.gui`·위젯·대시보드 지표. 비축·연료·공군 상태를 보여 주는 화면이 없다.
- Area 타게팅·지도 색칠, 레이더, 요새 `add_breach`/`change_garrison_size`, PM 전환에 따른 라인 효율 감소 자동 연결.
- 균형: 모든 수치가 자리표시. 장기 AI 관찰(틱 비용, AI 연료/비축 붕괴)이 필요하다.
- 8시대 전용 국가 변수 읽기: 7시대에서 8시대로 넘어갈 때의 세이브 이행은 확인하지 않았다.
