# 백과사전과 힌트

## 백과사전 개념

처음 하는 사람이 모드의 모든 요소를 백과사전에서 찾아갈 수 있게, 가이드 하나와 분야별 허브 넷 아래에 항목을 묶었다. 바닐라처럼 `family`로 계층을 만들고(가이드 → 허브 → 항목), 다른 문구에서는 `[tsin_treaty_port_concept|e]`처럼 링크한다. 개념은 모두 76개다.

| 정의 파일 (`main_menu/common/game_concepts/`) | 내용 |
|---|---|
| `tsin_concepts.txt` | 가이드 `tsin_singularity_concept`(별칭 `tsin_mod_guide`), 허브 4개, M6·0.7에서 만든 기존 항목 |
| `tsin_concepts_core.txt` | 시대, 제도, 발전, 군사, 제6시대 연속성, 대체 건물, 게임 규칙 |
| `tsin_concepts_economy.txt` | 재화, 공장, 개축, 화학, 채굴, 철도, 기반 시설, 석유·고무, 관세 동맹 |
| `tsin_concepts_society.txt` | 노동 불만, 주거, 도시화, 학교, 공중보건, 계층 특권, 사회 발전, 사회 이벤트, 사회 보정치 |
| `tsin_concepts_politics.txt` | 법률, 법안 심의, 의회 안건, 노예제 폐지, 정부 개혁, 금본위제, 특허장, 회장, 트러스트 |
| `tsin_concepts_world.txt` | 상황 8종, 재난 4종, 임무, 원정, 열강, 개척지, 문화·과학, 다음 시대, 지도 모드, 힌트, 이벤트 |

현지화 `game_concept_<키>`, `game_concept_<키>_desc`는 분야별 파일 `main_menu/localization/<언어>/tsin_concepts_<core|economy|society|politics|world>_l_<언어>.yml`에 있다. 가이드와 시간 압축·인구 조절기는 `core`에 있다. 설명에 쓴 수치는 스크립트 값을 따르므로 스크립트를 바꾸면 해당 항목도 고친다.

모드 객체(건물, 재화, 발전, 법, 정책, 결단, 내각 행동, 상황, 재난, 게임 규칙 등)의 `_desc`에는 관련 항목 링크를 달았다. 바닐라 개념(`[estates|e]`, `[market|e]` 등)도 같은 방식으로 링크한다.

`tools/validate.py` 검사: 개념마다 영어·한국어 이름과 설명, `gfx/interface/icons/<texture>.dds` 파일, 존재하는 `family`. 모드 현지화의 모든 `[x|e]` 링크가 바닐라나 모드 개념(별칭 포함)인지. 재화의 `_desc`. 현지화 값이 한 줄을 넘지 않는지.

| 파일 | 키 | 한국어 이름 | family | 불러오기 화면 |
|---|---|---|---|---|
| `tsin_concepts.txt` | `tsin_singularity_concept` | The Singularity is Near | - | 예 |
| `tsin_concepts.txt` | `tsin_industrial_economy_concept` | 산업 경제 | `tsin_singularity_concept` |  |
| `tsin_concepts.txt` | `tsin_industrial_society_concept` | 산업 사회 | `tsin_singularity_concept` |  |
| `tsin_concepts.txt` | `tsin_mass_politics_concept` | 대중 정치와 금융 | `tsin_singularity_concept` |  |
| `tsin_concepts.txt` | `tsin_industrial_world_concept` | 산업 시대의 세계 | `tsin_singularity_concept` |  |
| `tsin_concepts.txt` | `tsin_time_compression_concept` | 시간 압축 | `tsin_singularity_concept` | 예 |
| `tsin_concepts.txt` | `tsin_population_governor_concept` | 인구 조절기 | `tsin_singularity_concept` |  |
| `tsin_concepts.txt` | `tsin_electric_power_concept` | 전력 | `tsin_industrial_economy_concept` | 예 |
| `tsin_concepts.txt` | `tsin_industrial_investment_concept` | 산업 투자 | `tsin_industrial_economy_concept` |  |
| `tsin_concepts.txt` | `tsin_agricultural_revolution_concept` | 농업 혁명 | `tsin_industrial_economy_concept` |  |
| `tsin_concepts.txt` | `tsin_automation_concept` | 자동화 | `tsin_industrial_economy_concept` |  |
| `tsin_concepts.txt` | `tsin_movements_concept` | 정치 운동 | `tsin_industrial_society_concept` | 예 |
| `tsin_concepts.txt` | `tsin_education_ladder_concept` | 교육 단계 | `tsin_industrial_society_concept` | 예 |
| `tsin_concepts.txt` | `tsin_labor_conditions_concept` | 노동 조건 | `tsin_industrial_society_concept` | 예 |
| `tsin_concepts.txt` | `tsin_bills_concept` | 법안 | `tsin_mass_politics_concept` | 예 |
| `tsin_concepts.txt` | `tsin_corporations_concept` | 기업 | `tsin_mass_politics_concept` |  |
| `tsin_concepts.txt` | `tsin_stock_index_concept` | 주가 종합지수 | `tsin_mass_politics_concept` |  |
| `tsin_concepts.txt` | `tsin_estimated_gdp_concept` | 추정 GDP | `tsin_mass_politics_concept` |  |
| `tsin_concepts.txt` | `tsin_treaty_port_concept` | 조약항 | `tsin_industrial_world_concept` |  |
| `tsin_concepts.txt` | `tsin_industrial_age_situations` | 산업 시대의 상황 | `tsin_industrial_world_concept` |  |
| `tsin_concepts_core.txt` | `tsin_age_of_industry_concept` | 산업 시대 | `tsin_singularity_concept` |  |
| `tsin_concepts_core.txt` | `tsin_industrial_institutions_concept` | 산업 시대의 제도 | `tsin_singularity_concept` | 예 |
| `tsin_concepts_core.txt` | `tsin_age7_advances_concept` | 산업 시대의 발전 | `tsin_singularity_concept` |  |
| `tsin_concepts_core.txt` | `tsin_age7_military_concept` | 산업 시대의 전쟁 | `tsin_singularity_concept` |  |
| `tsin_concepts_core.txt` | `tsin_age6_continuity_concept` | 혁명 시대의 유산 | `tsin_singularity_concept` |  |
| `tsin_concepts_core.txt` | `tsin_replaced_buildings_concept` | 대체되는 건물 | `tsin_singularity_concept` |  |
| `tsin_concepts_core.txt` | `tsin_game_rules_concept` | 산업 시대 게임 규칙 | `tsin_singularity_concept` |  |
| `tsin_concepts_economy.txt` | `tsin_new_goods_concept` | 산업 재화 | `tsin_industrial_economy_concept` |  |
| `tsin_concepts_economy.txt` | `tsin_factories_concept` | 산업 공장 | `tsin_industrial_economy_concept` |  |
| `tsin_concepts_economy.txt` | `tsin_building_upgrades_concept` | 건물 개축 | `tsin_industrial_economy_concept` |  |
| `tsin_concepts_economy.txt` | `tsin_chemical_industry_concept` | 화학 공업 | `tsin_industrial_economy_concept` |  |
| `tsin_concepts_economy.txt` | `tsin_extraction_tiers_concept` | 광업과 임업 | `tsin_industrial_economy_concept` |  |
| `tsin_concepts_economy.txt` | `tsin_railways_concept` | 철도 | `tsin_industrial_economy_concept` | 예 |
| `tsin_concepts_economy.txt` | `tsin_infrastructure_concept` | 근대 기반 시설 | `tsin_industrial_economy_concept` |  |
| `tsin_concepts_economy.txt` | `tsin_oil_prospecting_concept` | 석유와 고무 | `tsin_industrial_economy_concept` |  |
| `tsin_concepts_economy.txt` | `tsin_customs_union_concept` | 관세 동맹 | `tsin_industrial_economy_concept` |  |
| `tsin_concepts_politics.txt` | `tsin_social_laws_concept` | 산업 시대의 법률 | `tsin_mass_politics_concept` |  |
| `tsin_concepts_politics.txt` | `tsin_bill_readings_concept` | 법안 심의와 논쟁 | `tsin_mass_politics_concept` |  |
| `tsin_concepts_politics.txt` | `tsin_industrial_agendas_concept` | 산업 시대의 의회 안건 | `tsin_mass_politics_concept` |  |
| `tsin_concepts_politics.txt` | `tsin_abolition_concept` | 노예제 폐지 | `tsin_mass_politics_concept` |  |
| `tsin_concepts_politics.txt` | `tsin_government_reforms_concept` | 산업 시대의 정부 개혁 | `tsin_mass_politics_concept` |  |
| `tsin_concepts_politics.txt` | `tsin_gold_standard_concept` | 금본위제 | `tsin_mass_politics_concept` |  |
| `tsin_concepts_politics.txt` | `tsin_company_charters_concept` | 기업 특허장 | `tsin_mass_politics_concept` |  |
| `tsin_concepts_politics.txt` | `tsin_chairman_concept` | 기업 회장 | `tsin_mass_politics_concept` |  |
| `tsin_concepts_politics.txt` | `tsin_trusts_concept` | 트러스트와 독점 금지 | `tsin_mass_politics_concept` |  |
| `tsin_concepts_society.txt` | `tsin_labor_grievance_concept` | 노동 불만 | `tsin_industrial_society_concept` |  |
| `tsin_concepts_society.txt` | `tsin_housing_concept` | 주거와 과밀 | `tsin_industrial_society_concept` |  |
| `tsin_concepts_society.txt` | `tsin_urbanization_concept` | 도시화 | `tsin_industrial_society_concept` |  |
| `tsin_concepts_society.txt` | `tsin_schools_and_universities_concept` | 학교와 대학 | `tsin_industrial_society_concept` |  |
| `tsin_concepts_society.txt` | `tsin_public_health_concept` | 공중보건 | `tsin_industrial_society_concept` |  |
| `tsin_concepts_society.txt` | `tsin_estate_privileges_concept` | 산업 시대의 특권과 요구 | `tsin_industrial_society_concept` |  |
| `tsin_concepts_society.txt` | `tsin_society_advances_concept` | 대중사회 발전 | `tsin_industrial_society_concept` |  |
| `tsin_concepts_society.txt` | `tsin_working_class_events_concept` | 사회 이벤트 | `tsin_industrial_society_concept` |  |
| `tsin_concepts_society.txt` | `tsin_social_modifiers_concept` | 사회 보정치 | `tsin_industrial_society_concept` |  |
| `tsin_concepts_world.txt` | `tsin_long_depression_concept` | 대불황 | `tsin_industrial_age_situations` |  |
| `tsin_concepts_world.txt` | `tsin_grain_invasion_concept` | 곡물 침공 | `tsin_industrial_age_situations` |  |
| `tsin_concepts_world.txt` | `tsin_great_migration_concept` | 대이주 | `tsin_industrial_age_situations` |  |
| `tsin_concepts_world.txt` | `tsin_springtime_of_nations_concept` | 국민의 봄 | `tsin_industrial_age_situations` |  |
| `tsin_concepts_world.txt` | `tsin_national_unification_concept` | 민족 통일 | `tsin_industrial_age_situations` |  |
| `tsin_concepts_world.txt` | `tsin_defensive_modernization_concept` | 방어적 근대화 | `tsin_industrial_age_situations` |  |
| `tsin_concepts_world.txt` | `tsin_scramble_for_colonies_concept` | 식민지 쟁탈전 | `tsin_industrial_age_situations` |  |
| `tsin_concepts_world.txt` | `tsin_world_exhibition_concept` | 만국박람회 | `tsin_industrial_age_situations` |  |
| `tsin_concepts_world.txt` | `tsin_industrial_disasters_concept` | 산업 시대의 재난 | `tsin_industrial_world_concept` |  |
| `tsin_concepts_world.txt` | `tsin_cholera_concept` | 콜레라 대유행 | `tsin_industrial_disasters_concept` |  |
| `tsin_concepts_world.txt` | `tsin_great_hunger_concept` | 대기근 | `tsin_industrial_disasters_concept` |  |
| `tsin_concepts_world.txt` | `tsin_millenarian_rebellion_concept` | 천년왕국 대반란 | `tsin_industrial_disasters_concept` |  |
| `tsin_concepts_world.txt` | `tsin_secession_crisis_concept` | 연방 분열 위기 | `tsin_industrial_disasters_concept` |  |
| `tsin_concepts_world.txt` | `tsin_industrial_missions_concept` | 산업 시대의 임무 | `tsin_industrial_world_concept` |  |
| `tsin_concepts_world.txt` | `tsin_expeditions_concept` | 산업 시대의 원정 | `tsin_industrial_world_concept` |  |
| `tsin_concepts_world.txt` | `tsin_great_power_politics_concept` | 열강 협조 체제 | `tsin_industrial_world_concept` |  |
| `tsin_concepts_world.txt` | `tsin_frontier_concept` | 골드러시와 개척지 | `tsin_industrial_world_concept` |  |
| `tsin_concepts_world.txt` | `tsin_culture_science_concept` | 문화와 과학 | `tsin_industrial_world_concept` |  |
| `tsin_concepts_world.txt` | `tsin_late_century_concept` | 다음 시대의 씨앗 | `tsin_industrial_world_concept` |  |
| `tsin_concepts_world.txt` | `tsin_map_modes_concept` | 산업 시대의 지도 모드 | `tsin_industrial_world_concept` | 예 |
| `tsin_concepts_world.txt` | `tsin_hints_concept` | 산업 시대의 힌트 | `tsin_industrial_world_concept` |  |
| `tsin_concepts_world.txt` | `tsin_flavor_events_concept` | 산업 시대의 이벤트 | `tsin_industrial_world_concept` |  |

## 힌트

파일: `in_game/common/scriptable_hints/tsin_hints.txt`. 힌트는 화면마다 자주 평가되므로 국가 단위의 싼 조건만 쓴다(지점 순회 금지).

| 힌트 | 보이는 조건 | 연결 개념 |
|---|---|---|
| `hint_tsin_long_depression` 외 상황 3종 | 상황 진행 중 | - |
| `hint_tsin_electric_power` | 발전기 기술 연구, 발전소 0단계(`total_effective_building_levels:tsin_power_station < 1`) | 전력 |
| `hint_tsin_unequal_treaty` | `tsin_unequal_treaty` 보정치 있음 | 조약항 |
| `hint_tsin_radical_movements` | `var:tsin_radicalism >= 60` | 정치 운동 |
| `hint_tsin_grain_invasion` 외 상황 3종(0.7) | 상황 진행 중 | - |
| `hint_tsin_labor_grievance` | `var:tsin_labor_grievance >= 50` | 노동 조건 |
| `hint_tsin_first_bill` | 법안 제도 활성, 아직 통과한 법안 없음(`var:tsin_bills_passed`) | 법안 |
| `hint_tsin_stock_crash` | `tsin_stock_crash` 보정치 있음 | 주가 종합지수 |

현지화는 바닐라 힌트처럼 `hint_<키>`, `_hint_text`, `_diplomatic`, `_administrative`, `_military`를 쓴다.

사용자 확인 필요:
- 백과사전에서 가이드와 허브 아래에 항목이 계층으로 보이고, 아이콘이 보이는지.
- 개념 설명 안의 `Show...Name` 함수(결단, 정책, 법, 상황, 국제기구, 지도 모드 이름)와 `$...$` 치환이 이름으로 보이는지. 한국어에서 시대 이름이 겹치지 않는지.
- `shown_in_loading_screen = yes`인 개념의 **첫 문단**에는 `ShowAgeName`/`Show*Name`을 쓰지 않는다. 로딩 중 DB가 없어 `ERROR`로 보인다. 시대는 `$age_format_...$`, 그 외는 `$키$`로 쓴다.
- 문구 속 `[tsin_..._concept|e]` 링크가 툴팁으로 열리는지.
- 세 힌트가 조건을 만족할 때 힌트 목록에 나타나고, 조건이 풀리면 사라지는지.
