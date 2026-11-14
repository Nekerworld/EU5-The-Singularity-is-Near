# 빅토리아 3 레퍼런스 대응표

**사용 원칙:** 설계 참고용이다. 문구, 아이콘, 수치, 데이터 파일은 복사하지 않는다. 모든 수치는 `docs/balance_targets.md`의 EU5 기준으로 새로 정한다.

**출처** (2026-11 조사, 위키 직접 접근은 500 오류라 검색 발췌로 확인):
- 공식 위키: Technology, Building, Goods, Profession, Ideology, Journal, Decision
- 개발 일지: #5 Production Methods, #10 Infrastructure, #71 Autonomous Investment, #92·#147 Companies
- 기술 이름 목록은 2022년 커뮤니티 요약이 출처다. 구현 전에 이름과 시대를 다시 확인한다.

**범위:** 빅토리아 3의 1~3시대(약 1836~1900)만 쓴다. 4시대 이후(내연기관, 라디오, 전기 철도)는 제8시대로 넘긴다.

## 1. 경제
| 빅토리아 3 개념 | EU5 대응 지점 | 채택 방식 | 할 일 |
|---|---|---|---|
| 생산 방식: 기본/정제 | 건물 `unique_production_methods` | 슬롯 안의 대체 방식(투입재 차이) | m2-pm-slot-test |
| 생산 방식: 자동화 | 고용이 건물마다 고정이라 직접 표현 불가 | `obsolete` 사슬의 상위 건물(고용 감소, 도구·기관 투입) | m2-automation-tier |
| 생산 방식: 소유 | 건물 `estate` 필드와 계층 자율 건설 | 경제 법률로 국가·계층 건설 비중 조정 | m3-investment, m4-laws |
| 처리량, 규모의 경제 | `global_production_efficiency`, 건물 단계 출력 | 기술 보정치 | m3-advances |
| 투자 풀, 자율 투자 | 계층 건설, 고용 체계 `capitalism` | 국가 변수 `tsin_investment_pool` 근사 | m3-investment |
| 기업 | 국가 보정치 | 결정 "산업 기업 설립"(유지비와 보유 상한) | m3-company-decision |
| 인프라와 시장 접근도 | `railroad` 도로, `market_access` 지도 모드 | 철도 비용·효과 기술, 강철 건설 수요 | m3-railway-market |
| 지역 비교역 상품(전력) | EU5 상품은 모두 교역됨 | 관문 G에서 위치 보정치 방식과 비교 | m5-power-model |
| 생활수준 소비 순환 | 인구 수요, 시대 `goods_demand` | 제7시대 블록에서 신규 소비재 수요 | m2-vertical-chain |

**신규 상품 우선순위:** 기관(M2) > 비료·폭약(M3) > 고무·석유(M3, 선택) > 전기 부품(M5). 통조림·가공식품은 M4에서 소비재로 검토한다.

## 2. 인구와 사회
| 빅토리아 3 개념 | EU5 대응 | 채택 방식 | 할 일 |
|---|---|---|---|
| 15개 직업과 자격 | 인구 종류 8개 | 시민 = 자본가·상점주, 노동자 = 공장 노동자로 근사. 문해율을 숙련 조건으로 사용. 신규 인구 종류는 만들지 않음 | m2, m4 |
| 생활수준, 급진성 | 인구 만족도, 계층 만족도 | 위치 값이 노출될 때만 지도 모드 | m4-mapmode-sol-radicalism |
| 대이민 | 바닐라 이주(`on_action/migrations.txt`) | 기근·임금 격차 보정치 | m4-disaster-hunger |
| 보건 | 바닐라 질병(콜레라) | 공중위생 기술, 하수도 이벤트 | m4-advances, m4-events-society |

## 3. 정치
| 빅토리아 3 개념 | EU5 대응 | 채택 방식 | 할 일 |
|---|---|---|---|
| 이익집단, 이념 | 계층, 특권, 의회 안건, 사회 가치 축 | 제7시대 의회 안건과 특권 | m4-parliament-reforms |
| 정치 운동, 선동가 | `movements`(확산 모델) | 자유주의·민족주의·노동·사회주의·여성 참정권 운동 5종 | m4-movements |
| 법률 범주 | `laws` | 경제 체제, 노동, 교육, 복지, 조세, 언론, 이민 | m4-laws |
| 노예제 법률 | 바닐라 노예 인구·상품·무역 이벤트 | 폐지 법률과 운동 | m4-abolition |
| 주 단위 칙령 | 내각 행동 | 산업 장려, 철도 계획 | m3-cabinet-actions |

## 4. 저널 항목 → 상황, 재난, 임무, 결정
| 빅토리아 3 | EU5 형태 | ID | 할 일 |
|---|---|---|---|
| 국민의 봄 | 상황 | `tsin_springtime_of_nations` | m4-situation-springtime |
| 대기근 | 재난 | `tsin_great_hunger` | m4-disaster-hunger |
| 곡물법 | 의회 안건과 이벤트 연쇄 | `tsin_repeal_corn_laws` | m3-corn-laws |
| 철도 붐, 공장으로 | 일반 임무 팩 | `tsin_industrialization_missions` | m3-missions |
| 근대화(메이지형) | 상태 조건 임무 | `tsin_modernization` | m6-modernization |
| 만국박람회 | 결정과 상황 | `tsin_world_exhibition` | m5-world-exhibition |
| 아프리카 분할 | 상황 | `tsin_scramble_for_colonies` | m3-situation-scramble |
| 장기 불황 | 상황 | `tsin_long_depression` | m3-situation-depression |
| 예술 후원 | `artist_work` | 낭만주의·사실주의·사진 | m6-art |
| 탐험 | `expedition_types` | 나일 수원, 극지 | m6-expeditions |

## 5. 외교와 군사
| 빅토리아 3 | EU5 대응 | 채택 방식 | 할 일 |
|---|---|---|---|
| 관세 동맹 | 국제기구 | 조사 후 결정(선택) | m3-customs-union |
| 불평등 조약, 조약항 | 강화 조약 | "조약항 개항" 조항 | m6-treaty-ports |
| 외교 놀이 | 없음 | 제외 | - |
| 1~3시대 군사 기술 | 유닛과 기술 | 뇌관식·강선 소총, 후장포, 철갑함, 참모본부 | m6-military |

## 6. 기술 후보 → 시대관
- **산업자본주의(M3):** 베서머 제강, 공작기계, 기계화 작업장, 집약 농업과 비료, 통조림, 화학 염료, 다이너마이트, 증권거래소·중앙은행
- **대중사회(M4):** 도시계획과 하수도, 대중 언론, 노동운동, 공교육, 민족주의, 사회주의 초기, 사진·사실주의, 제약
- **전기화(M5):** 전신, 발전기, 전화, 백열등, 전기 도금. 빅토리아 3에서 전기는 3시대 후반이므로 시대관 발생을 1870년대 이후로 늦춘다(m5-spawn-timing).
- **중복 금지:** 제6시대 `hot_blast_furnace`, `coal_improvements_revolutions`, `railroad_advance`, 운하 기술은 다시 만들지 않는다.
