# H0 엔진 실험 — 8시대 이후 HOI4 하이브리드 군사(H축)

**상태: H0는 아직 한 번도 실행하지 않았다. H1~H5는 모두 `사용자 확인 필요`다.** 계획(`8시대_이후_hoi4_하이브리드_군사_계획`)은 H0 확인 전에는 본 구현에 들어가지 말라고 했지만, 시험할 수 있도록 데이터와 스크립트를 먼저 만들었다. 이 문서의 실험은 모두 게임에서 직접 해 봐야 한다. 구현 설명과 숫자는 `docs/military_hybrid_h_track.md`.

## 진행 상태

| 단계 | 구현(코드·데이터) | 정적 검사 | 인게임 확인 |
|---|---|---|---|
| H0 엔진 실험 | 해당 없음 (아래 5개 실험) | - | **사용자 확인 필요** |
| H1 군수·비축 | 작성함 (`tools/gen_military_stockpile.py`) | 통과 | **사용자 확인 필요** |
| H2 편제·훈련 | 작성함 (`tools/gen_modern_training.py`) | 통과 | **사용자 확인 필요** |
| H3 연료 | 작성함 (`tools/gen_fuel_system.py`) | 통과 | **사용자 확인 필요** |
| H4 공군 | 작성함 (`tools/gen_airforce_hybrid.py`) | 통과 | **사용자 확인 필요** |
| H5 UI·문서·시험 | 문서·회귀 시험만. **UI(`unit_overview`/위젯)는 미구현** | 통과 | **사용자 확인 필요** |

정적 검사는 `tools/tests/test_h_track_military.py`와 `tools/validate.py`다. 둘 다 엔진 동작을 증명하지 않는다.

## 확인 방법 공통

H축에는 아직 전용 화면이 없다. 확인은 (1) 디버그 변수 보기(가능한 경우), (2) 월간 로그(`docs/mod_log.md`), (3) 효과 툴팁·건물·유닛 화면, (4) `error.log`로 한다. 변수 이름 목록은 `docs/military_hybrid_h_track.md`의 "변수" 표.

## H0 실험 5개

### P1. `set_production_method`가 건물 스코프에서 동작하는가
- 이유: 군수공장의 생산 라인(PM) 전환과 라인 효율(`var:tsin_line_eff_*`) 감소를 연결하려면 필요하다. 현재는 PM 전환을 감지하지 않으며 `tsin_h_retool_*_effect`를 수동으로만 부를 수 있다.
- 시험: 소화기 공장(`tsin_small_arms_works`)을 짓고 `rifle_line`/`automatic_line` 두 PM을 UI로 바꿔 보고, 스크립트로 `set_production_method`를 호출해 본다. `PRODUCTION_METHOD_AUTO_SWITCH_MARGIN`(자동 전환)과 충돌하는지 본다.
- 기대: UI 전환이 자동 전환으로 되돌려지지 않는다.
- 실패 시: 라인 효율 감소는 쓰지 않는다(`tsin_h_line_recover_effect`는 무해).

### P2. `buy_goods_from_market`를 월간 펄스에서 매월 실행해도 되는가
- 이유: H3 연료가 수도 시장에서 `tsin_oil`을 최대 6개씩 산다(`tsin_h3_fuel_market_effect`). 기존 저장고(`tsin_strategic_storage`)와 같은 구조(관측 재고 차이만 반영)다.
- 시험: 석유 유전이 있는 시장(`tsin_prospect_for_oil` 결단)과 없는 시장에서 100개월 이상 돌려, 석유 가격 급등·AI 무역 왜곡·시장 접근 차단·금 이중 차감이 있는지 본다.
- 실패 시: 콘솔로 `effect tsin_h_fuel_market_off_effect = yes`(전역 변수 `tsin_h_fuel_market_off`)를 실행하면 구매가 멈추고 기본 유입만 남는다. 다시 켜려면 `tsin_h_fuel_market_on_effect`.

### P3. `in_battle` 주기와 `unit_location` 내 `every_unit_in_location` 접근
- 이유: H4 근접항공지원은 월간 펄스에서 목표 지방의 지점별 `every_unit_in_location`을 돈다(전투 주기 `in_battle`은 쓰지 않는다). 전투 중 부대만(`in_combat = yes`) 피해를 주는지, 장군 없는 부대도 포함되는지 모른다.
- 시험: 전쟁 중 `tsin_air_target_cas`로 전투가 벌어지는 지방을 지정하고 한 달 뒤 적 부대 강도/사기 변화를 본다. `in_battle`(`_hardcoded.txt` 629행)은 확인용으로만 따로 로그를 남겨 본다.
- 또 확인: `on_battle_won`/`on_battle_lost`에서 `scope:lost_land_units`가 해당 쪽 손실인지(H1 장비 손실이 이 값을 쓴다). 승자는 승리 쪽 손실, 패자는 패배 쪽 손실로 가정했다.

### P4. `generic_actions`의 Area 타게팅과 지도 색칠
- 이유: 계획은 `looking_for_a = area`를 쓰려 했지만 이 모드 어디에도 쓴 사례가 없다. 그래서 **지방(`looking_for_a = province`)** 타게팅으로 구현했다(`zzz_tsin_h4_air_missions.txt`에 주석).
- 시험: 항공 임무 5종이 목록에 뜨는지, 지방 선택 창이 열리는지, `enabled` 조건이 맞는지. Area로 바꿨을 때 `looking_for_a = area` + `interaction_source_list`가 되는지와 `map_mode` 색칠.
- 지도 색칠은 미구현이다.

### P5. `unit_overview.gui` 확장 방식
- 미구현이다. `military_main_tabs`의 `subtab` 추가와 `scripted_widgets` 플로팅 창 중 어느 쪽이 충돌이 적은지 아직 고르지 않았다. 대시보드 레지스트리(`ui/dashboard_registry.json`)에 읽기 전용 지표를 얹는 방법도 후보다. 이번 단계에서는 공유 GUI를 건드리지 않았다.

## H1~H4 개별 확인 목록 (모두 사용자 확인 필요)

### 데이터 로딩
- 게임 시작 시 `error.log`에 `tsin_small_arms_works` 등 새 건물, `a_tsin_*` 유닛, `a_age_8_world_wars_*` 템플릿, `tsin_modern_field_drill` 능력, `tsin_air_target_*` 일반 행동 관련 오류가 없는지.
- 7시대 세이브를 로드해 월/연 진행 시 H축 변수(`tsin_h_init` 등)가 생기지 않는지(8시대 + 해당 발전이 없으면 효과가 실행되지 않아야 한다).

### H1 군수·비축
- 8시대에서 `tsin_mass_production_arms_advance` 연구 후 소화기·지원 화포 공장, `tsin_armored_vehicle_industry_advance` 후 기갑 차량 공장을 지을 수 있는지. 공장이 실제로 총기/화포/엔진을 시장에 공급하고 AI가 지는지.
- 월간 `tsin_eq_*_stockpile` 변화가 공장 단계, 연대 수, 전시/평시 가중치와 맞는지. 시작 비축 60/30/20/0, 상한 600, 하한 -300.
- 비축이 음수일 때 전시 또는 -150 미만이면 군대에 `tsin_eq_shortage_*` 수정자가 붙고 회복 시 사라지는지.
- 전투 후 `scope:lost_land_units` 만큼 비축이 줄어드는지(P3).
- `army_light_infantry_power` 등 국가 범주 수정자 이름이 유닛 범주 정적 수정자에서 적용되는지.

### H2 편제·훈련
- `a_tsin_*` 6종이 해금 후 모집 목록에 보이고(`buildable = yes`, `hide = no`) AI도 모집하는지. 템플릿에서 `copy_from` 뒤 능력치가 가산되는지(7시대 문서와 같은 질문).
- 6개 병과가 바닐라 유닛 범주(경기병/중기병/경보병/중보병/포병/보조)로 분류되는지.
- 현대식 야전 훈련(`tsin_modern_field_drill`)이 `tsin_modern_field_drill_advance` 후 유닛 능력 목록에 보이고, 켜면 경험 +3.5, 유지비 효율 -40%, 사기 -90%가 적용되며 전투·이동·공성 시 자동 해제되는지.
- 9시대 주력 전차·로켓 포병이 8시대 유닛을 상속하는지.

### H3 연료
- 국가 변수 `tsin_fuel_stockpile`이 시작 50, 상한(기본 100 + 석유 저장고 120/단계 + 자동차 거점 60/단계 + 비행장 40/단계)을 따르는지.
- 석유가 시장에 없을 때 기갑 유닛 보유 시 연료가 0으로 내려가 `tsin_fuel_depleted`(이속 -40%, 기갑 전투력 -30%) 상태가 되는지, 20% 미만이면 `tsin_fuel_low`인지.
- 평시에는 소비가 전시의 15%인지.

### H4 공군
- 항공기 공장 → 항공기 풀 → 전투기/근접지원기/폭격기/수송기 분배(35/30/15/20%), 수용 한도(기본 6 + 수도 비행장 10 + 지역 비행장 12/단계).
- `tsin_capital_airfield` ID와 `tsin_powered_flight_advance`/`tsin_aerial_observation_advance`가 그대로이고 기존 세이브 연구가 보존되는지.
- 5개 일반 행동에서 지방을 지정하면 전시 월간 펄스가 제공권 지수(`tsin_air_superiority_index`), CAS 피해, 전략 폭격(지점당 12%, 대공포 5%로 건물 1단계 파괴), 공수 보급(포위 중 식량 +5~10%)을 적용하는지.
- AI가 전투 중인 지방을 자동 지정하는지(제공권·CAS·공수). 폭격은 AI 자동 지정 없음.
- 과도한 건물 파괴, 폭격이 아군 지점을 때리지 않는지(적국 소유 지점만 대상).

## 순서
P1~P4 → H1 → H2 → H3 → H4. 위 실험으로 막히는 항목은 해당 단계의 효과를 끄거나(전역 변수/게이트) 계획을 바꾼다.
