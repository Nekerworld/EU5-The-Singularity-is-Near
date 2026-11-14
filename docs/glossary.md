# 용어집 (게임 내 한국어 현지화 기준)

게임 안 문구는 바닐라 한국어 현지화(`main_menu/localization/korean`)의 공식 번역을 따른다.
- 계획서와 문서에서는 편의상 "시대관", "기술"이라고 썼지만, **게임 안에서는 "제도", "발전"이라고 쓴다.**
- 현지화에서 개념을 가리킬 때는 바닐라처럼 `[institution|e]`, `[advance|e]` 같은 개념 링크를 쓴다. 그러면 용어가 자동으로 맞춰진다.

## 1. 핵심 개념
| 개념 키 | 영어 | 공식 한국어 | 계획서 표기 |
|---|---|---|---|
| age | Age | 시대 | 시대 |
| institution | Institution | **제도** | 시대관 |
| advance | Advance | **발전** | 기술 |
| decision | Decision | **결단** | 결정 |
| pop | Pop | **팝** | 인구 |
| goods | Goods | **재화** | 상품 |
| estate | Estate | 계층 | 계층 |
| privilege | Privilege | 특권 | 특권 |
| law | Law | 법률 | 법률 |
| parliament | Parliament | 의회 | 의회 |
| situation | Situation | 상황 | 상황 |
| disaster | Disaster | 재난 | 재난 |
| mission | Mission | 임무 | 임무 |
| movement | Movement | 운동 | 운동 |
| cabinet | Cabinet | 내각 | 내각 |
| casus_belli | Casus Belli | 전쟁 명분 | 전쟁명분 |
| societal_value | Societal Value | 사회 가치관 | 사회 가치 |
| production_method | Production Method | 생산 방식 | 생산 방식 |
| building | Building | 건물 | 건물 |
| market | Market | 시장 | 시장 |
| literacy | Literacy | 문해력 | 문해율 |
| hegemon | Hegemon | 패권 국가 | 패권국 |
| great_power | Great Power | 열강 | 강대국 |
| levy | Levy | 징집군 | 징집병 |
| expedition | Expedition | 원정 | 탐험 |
| international_organization | International Organization | 국가 간 조직체 | 국제기구 |
| location / province / area | Location / Province / Area | 지점 / 지방 / 권역 | 위치 / 지방 / 지역 |
| control | Control | 지배 | 통제력 |
| proximity | Proximity | 근접도 | 근접도 |
| stability / prestige | Stability / Prestige | 안정도 / 위상 | 안정 / 위신 |
| rgo | RGO | 자원 채집 시설 | 원자재 생산 |
| bureaucracy | Bureaucracy | 관료 조직 | 관료제 |
| subject | Subject | 종속국 | 속국 |

## 2. 팝 종류
귀족(nobles), 성직자(clergy), **도시민**(burghers, 계획서의 "시민"), 노동자(laborers), 병사(soldiers), 농민(peasants), 부족민(tribesmen), 노예(slaves)

## 3. 시대 이름
| ID | 영어 | 한국어 | 형식 키 |
|---|---|---|---|
| age_5_absolutism | Absolutism | 절대주의 | `age_format_*` = "$이름$ 시대" / "Age of $name$" |
| age_6_revolutions | Revolutions | 혁명 | |
| **age_7_industrialization** | **Industry** | **산업** | "산업 시대" / "Age of Industry" |

제6시대 제도 `industrialization`의 이름이 이미 "산업화"(Industrialization)이므로, 제7시대는 "산업"(Industry)으로 구분한다.

## 4. 제7시대 고유 용어
| ID | 영어 | 한국어 |
|---|---|---|
| tsin_industrial_capitalism | Industrial Capitalism | 산업자본주의 |
| tsin_mass_society | Mass Society | 대중사회 |
| tsin_electrification | Electrification | 전기화 |
| tsin_engines | Engines | 기관 |
| tsin_fertilizer | Fertilizer | 비료 |
| tsin_explosives | Explosives | 폭약 |
| tsin_electrical_parts | Electrical Parts | 전기 부품 |
| tsin_long_depression | The Long Depression | 장기 불황 |
| tsin_springtime_of_nations | Springtime of Nations | 국민의 봄 |
| tsin_great_hunger | The Great Hunger | 대기근 |
| tsin_scramble_for_colonies | Scramble for Colonies | 식민지 쟁탈전 |
| tsin_world_exhibition | World Exhibition | 만국박람회 |

## 5. 바닐라 건물 이름 (사슬 참조)
직물 공방(cloth_manufactory) → 직물 방직소(textile_mill), 제철소(iron_mill), 제강소(steel_mill). 신규 상위 건물 이름은 이 어조를 따른다(예: 역직기 방직소, 기계 공작소, 베서머 제강소).

## 6. 문체
- 설명문은 바닐라처럼 "~합니다"체를 쓴다.
- 수치·보정치 이름은 바닐라 수정자 현지화를 재사용하고 새로 쓰지 않는다.
- 현지화 파일은 UTF-8 BOM으로 저장하고, 첫 줄은 `l_korean:`, 키는 공백 1칸 들여쓰기 `key: "값"` 형식이다.
