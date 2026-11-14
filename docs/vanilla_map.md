# 바닐라 산업 콘텐츠 대응표 (EU5 1.4.x)

제7시대 콘텐츠는 바닐라에 이미 있는 것을 먼저 쓰고, 없는 것만 추가한다. 이 표는 그 판단 근거다.

## 1. 상품 (`in_game/common/goods`)
| 분류 | 바닐라 상품 | 제7시대 활용 |
|---|---|---|
| 원자재 | coal, iron, copper, tin, lead, saltpeter, sand, clay, stone, lumber, fiber_crops, dyes, mercury 등 35종 | coal·iron을 산업 핵심 투입재로 격상 |
| 플랜테이션 | cotton, sugar, tobacco | cotton 수요 증가(방직) |
| 생산품 | tar, naval_supplies, firearms, cannons, weaponry, glass, **steel**, cloth, fine_cloth, liquor, beer, paper, books, leather, **tools**, masonry, pottery, furniture 등 21종 | steel·tools를 기관·철도·기계의 투입재로 사용 |
| 식량 | wheat, maize, rice, potato, livestock 등 15종 | 비료로 생산량 보강, 대기근 재난의 대상 |

**핵심 공백:**
- `steel`에 바닐라 주석 "Late Game Steel - Needs a purpose. How about railroads?"가 달려 있다. 현재 소비처는 대포·화기·도구·무기 생산의 일부 방식과 건설 수요뿐이다. 제7시대는 강철 수요(기관, 철도, 철골 건물)를 만든다.
- 증기기관, 기계, 비료, 폭약, 전기 설비에 해당하는 상품이 없다. 계획 상품은 다음과 같다.
  - 필수: `tsin_engines` (M2)
  - 선택: `tsin_fertilizer`, `tsin_explosives` (M3), `tsin_rubber`, `tsin_oil` (M3)
  - 전력: `tsin_electrical_parts`. 전력 자체를 상품으로 둘지는 관문 G에서 정한다.

## 2. 건물 (`in_game/common/building_types`)
제조업 건물은 4단계 `obsolete` 사슬을 따른다: 길드(burghers) → 작업장(burghers) → 매뉴팩처(burghers) → 공장·제분소(laborers, `is_mill = yes`).

| 산업 | 바닐라 사슬의 마지막 단계 | 제7시대 추가 단계(자동화 근사) |
|---|---|---|
| 도구 | `iron_foundry` → `iron_mill` | `tsin_machine_works` (기계·기관) |
| 직물 | `cloth_manufactory` → `textile_mill` | `tsin_power_loom_mill` |
| 종이 | `paper_mill` | `tsin_rotary_paper_mill`(선택) |
| 유리 | `glass_mill` | (보류) |
| 대포 | `cannons_factory` | `tsin_rifled_artillery_works`(M6) |
| 화기 | `firearms_factory` | `tsin_breechloader_factory`(M6) |
| 무기 | `weapon_factory` | (보류) |
| 초석 | `putrefaction_mill` | `tsin_chemical_works`(비료·폭약, M3) |
| 강철 | `steel_mill`(단일 단계, iron 2.963 + coal 2.963 → steel 4) | `tsin_bessemer_steelworks` |

**공장 공통 값:**
- `employment_size = mills_employment`, `max_levels = mills_max_level`, `build_time = mills_build_time`
- `construction_demand = mill_construction`, `category = basic_industry_category | consumer_goods_category`
- `custom_tags = { lategame_manufactory }`

**생산 방식:** 건물 안의 `unique_production_methods = { pm = { 투입재 = 양 produced = 상품 output = 4 category = mills_input } }` 구조다.
- 고용 규모와 인구 종류는 건물마다 고정이다. 그래서 "같은 건물의 자동화 방식"으로 노동자를 줄일 수 없다. 자동화는 더 높은 단계의 건물로 근사한다(m2-automation-tier).
- 여러 생산 방식 슬롯이 실제로 동작하는지는 관문 E에서 시험한다.

## 3. 기술 (`in_game/common/advances`, 제6시대 약 130개)
- 산업 관련 제6시대 기술: `industrialization_advance`(`depth = 0`, 시대관 수용 시 해금), `hot_blast_furnace`, `cupola_smelting`, `coal_improvements_revolutions`, `rotherham_plough`, `urbanization`, `joint_stock_companies`, `insurance_companies`, `the_gold_standard`, `road_advance_2`
- 제분소 해금: `*_mill_advance` 16개, `weapon_factory_advance`, `firearms_factory_advance`, `gun_factory_advance`
- 도로: `railroad_advance`(`3_road_unlocks.txt`). 철도 도로 종류 `railroad`가 이미 있다. 제7시대는 철도를 새로 만들지 않고 효과·비용·시장 접근도를 강화한다(m3-railway-market).
- 운하: `suez_canal_advance`, `panama_canal_advance`와 `decisions/canal_construction.txt`가 이미 있다. 제7시대 기술이 조건을 앞당기거나 비용을 낮추는 방식으로 연결한다.

## 4. 시대관 (`institution/age_6_revolutions_institutions.txt`)
`enlightenment`, `industrialization`, `levee_en_masse`.

- 구조: `age`, `location`(대체 발생지), `can_spawn`(게임 규칙 3종 분기), `promote_chance`, `spread_*`(후기용 `_late` 값)
- `can_spawn`의 "plausible" 분기는 `scripted_triggers/institution_triggers.txt`의 `*_plausible_location`을 쓴다.
  - 예: `industrialization_plausible_location`은 manufactories 보유, 유럽·북아프리카, burghers 20 초과, 건물 레벨 120 초과, 자본 경제 가치를 요구한다.
- 제7시대 시대관 3개는 같은 구조를 따르고, `tsin_*_plausible_location` 트리거를 만든다.
  - `tsin_industrial_capitalism`: industrialization을 전제로 함
  - `tsin_mass_society`: enlightenment와 문해율을 전제로 함
  - `tsin_electrification`: tsin_industrial_capitalism을 전제로 함

## 5. 인구·고용·도로
- 인구 종류 8개(nobles, clergy, burghers, laborers, soldiers, peasants, tribesmen, slaves)는 하드코딩 가능성이 있어 새로 만들지 않는다. 빅토리아 3의 직업군은 기존 인구 종류와 수정자로 근사한다(`docs/vic3_reference.md`).
- 고용 체계: equality, first_come_first_serve, capitalism과 그 변형 3개. 제7시대 경제 법률은 이 체계와 수정자를 조합한다.
- 도로: gravel_road, paved_road, modern_road, railroad.

## 6. 그 밖의 연결점
| 시스템 | 바닐라 위치 | 제7시대 연결 |
|---|---|---|
| 사회 가치 | `societal_values` | 자유무역/중상주의, 농노제/자유민, 절대주의/자유주의 축을 운동·법률이 움직인다 |
| 상황 | `situations` | `tsin_great_depression`, `tsin_scramble_for_colonies`, `tsin_springtime_of_nations` 추가 |
| 운동 | `movements` | 노동·자유주의·민족주의·폐지·참정권 운동 5종 |
| 내각 행동 | `cabinet_actions` | 산업 진흥, 철도 계획 |
| 원정 | `expedition_types` | 극지·아프리카 내륙 탐험 |
| 국제기구 | `international_organizations` | 관세 동맹 조사(선택) |
| 패권국 | `hegemons` + 시대 `hegemons_allowed` | 제7시대도 허용 |
