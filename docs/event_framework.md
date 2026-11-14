# 이벤트 공통 틀

## 네임스페이스

| 네임스페이스 | 파일 | 단계 | 내용 |
|---|---|---|---|
| `tsin_system` | `in_game/events/tsin_system.txt` | M1 | 숨김 초기화·이전, 시대 시작 안내, 제도 등장 알림 |
| `tsin_institution` | `in_game/events/tsin_institution.txt` | M3~M5 | 첫 수용국, 수용 시 반발·지지 |
| `tsin_economy` | `in_game/events/tsin_economy.txt` | M2~M3 | 공장, 원료, 금융 |
| `tsin_invention` | `in_game/events/tsin_invention.txt` | M3·M5 | 발명 플레이버 |
| `tsin_abolition` | `in_game/events/tsin_abolition.txt` | M4 | 노예무역 금지, 해방 (예산 제외) |
| `tsin_springtime` | `in_game/events/tsin_springtime.txt` | M4 | 국민의 봄 상황 (예산 제외) |
| `tsin_exhibition` | `in_game/events/tsin_exhibition.txt` | M5 | 만국박람회 상황 (예산 제외) |
| `tsin_military` | `in_game/events/tsin_military.txt` | M6 | 군사 플레이버 (`tsin_military_yearly_pulse`, 확률 20%) |
| `tsin_art` | `in_game/events/tsin_art.txt` | M6 | 예술 플레이버 (`tsin_art_yearly_pulse`, 확률 15%) |
| `tsin_expedition` | `in_game/events/tsin_expedition.txt` | M6 | 탐험 결과 (탐험이 호출, 예산 제외) |
| `tsin_hunger` | `in_game/events/tsin_hunger.txt` | M4 | 대기근 재난 (예산 제외) |
| `tsin_society` | `in_game/events/tsin_society.txt` | M4 | 참정권, 노동, 교육, 보건 (`tsin_society_flavor_pulse`, 매년 25%, 예산 사용) |
| `tsin_military` | `in_game/events/tsin_military.txt` | M6 | 군사 기술, 여론 |
| `tsin_flavor` | `in_game/events/tsin_flavor.txt` | M6 | 지역 플레이버 (`tsin_flavor_yearly_pulse`, 확률 15%, 태그 조건 금지) |

- 이벤트 ID는 `<네임스페이스>.<번호>`. 번호는 군 안에서 10 단위로 묶는다(예: 공장 10~19, 원료 20~29).
- 현지화 키는 `<id>.title`, `<id>.desc`, `<id>.a`, `<id>.b` …. 툴팁은 `<id>.a.tt`.
- 숨김 이벤트는 `title = empty_text`, `desc = empty_text`, `hidden = yes`.

## 빈도 예산

국가당 1년에 받는 `tsin_` 플레이버 이벤트 수를 `tsin_flavor_events_per_year`로 제한한다. 값은 게임 규칙 `tsin_flavor_event_frequency`(`main_menu/common/game_rules/tsin_game_rules.txt`)가 정한다: 보통 3(기본), 적게 1, 많이 5, 끔 0. 끔이면 예산 조건이 항상 거짓이 되어 플레이버 이벤트가 하나도 나오지 않는다. 상황·재난·탐험이 직접 부르는 이벤트와 시스템 알림은 예산 밖이라 영향을 받지 않는다. 사용자 확인 필요: 새 게임 설정의 게임 규칙 화면에 "산업 시대 플레이버 이벤트"와 "전기화 시기"가 보이는지, 스크립트 값 안의 `has_game_rule`이 동작하는지("끔"으로 10년 진행해 `tsin_` 플레이버 이벤트가 0개인지).

| 요소 | 위치 |
|---|---|
| 상한 값 | `in_game/common/script_values/tsin_event_values.txt` |
| 조건 `tsin_flavor_budget_available_trigger = yes` | `in_game/common/scripted_triggers/tsin_event_triggers.txt` |
| 소비 `tsin_spend_flavor_budget_effect = yes` | `in_game/common/scripted_effects/tsin_event_effects.txt` |
| 매년 초기화 | `tsin_yearly_country_pulse`의 `effect` (`tsin_on_actions.txt`) |

플레이버 이벤트는 반드시 다음 두 줄을 가진다.

```
trigger = { ... tsin_flavor_budget_available_trigger = yes }
immediate = { tsin_spend_flavor_budget_effect = yes ... }
```

시스템 알림(`tsin_system`)과 상황·재난이 직접 부르는 이벤트는 예산에서 뺀다.

## 발생 방식

- 날짜가 아니라 상태(제도 수용, 건물 규모, 문해율, 법)로 조건을 건다. 국가 태그를 필수 조건으로 쓰지 않는다.
- 각 군은 자기 on_action을 만들어 바닐라 맥동(`yearly_country_pulse`, `biyearly_country_pulse` 등)에 `on_actions = { ... }`로 붙인다. 묶음 안에서는 `random_events = { 10 = id ... chance_to_happen = N }`를 쓴다(바닐라 `country_four_yearly.txt`와 같은 형식).
- 맥동 on_action의 `trigger`에 `current_age_or_later = { age = age_7_industrialization }`을 둬서 이전 시대 국가에서는 평가 비용이 들지 않게 한다.

## 삽화 (`illustration_tags`)

바닐라 이벤트가 쓰는 태그는 장소(`interior`, `exterior`, `regular`)와 분위기(`happy`, `angry`, `armed`)다. 새 그림을 만들지 않고 다음처럼 조합한다.

| 이벤트 성격 | 태그 |
|---|---|
| 공장·작업장·사무실 | `10 = interior` `10 = regular` |
| 도시·철도·항구 | `10 = exterior` `10 = regular` |
| 사고, 파업, 폭동 | `10 = exterior` `10 = angry` |
| 박람회, 개통식, 축하 | `10 = exterior` `10 = happy` |
| 군사 | `10 = exterior` `10 = armed` |
| 의회·내각 | `10 = interior` `10 = angry` 또는 `10 = happy` |

제도 관련 이벤트는 `image = "gfx/interface/illustrations/institutions/<제도>.dds"`를 쓴다.

## AI 가중치 기본값

바닐라 형식 `ai_chance = { factor = N modifier = { factor = M <조건> } }`를 쓴다.

| 선택지 성격 | 기본 `factor` | 보정 |
|---|---|---|
| 안전한 기본 선택 | 10 | — |
| 돈을 쓰는 투자 | 5 | 금고가 부족하면 `factor = 0` |
| 안정·만족도를 깎는 선택 | 3 | 안정도가 낮으면 `factor = 0` |
| 위험한 도박 | 1 | — |

## 현재 이벤트

| ID | 내용 | 조건 | 선택지(경제 / 정치 / 진행) |
|---|---|---|---|
| `tsin_economy.10` | 공장 사고 | 공장 단계 건물 1곳 이상 | 보상금(금 -2, 평민 만족) / 안전 규정(지점 생산 효율 -5%, 불안 감소) / 무시(지점 불안, 평민 불만) |
| `tsin_economy.20` | 원료 부족 | 공장 지점 2곳 이상 | 수입(금 -3) / 감산(생산 효율 -5%, 2년) / 대체 원료(효율 -2%, 공장 건설 효율 +5%, 시민 불만) |
| `tsin_economy.30` | 숙련공 부족 | 공장 지점 3곳 이상, 기술 학교 없음 | 기술 학교(금 -4, 노동자 문해율 상한·효율) / 외국인 기술자(금 -2, 효율 +5% 감쇠, 시민 불만) / 도제(효율 -3%, 3년) |
| `tsin_economy.40` | 공장 확장 제안 | 공장 단계 건물 1곳 이상 | 국가 투자(금 -4, 지점 공장 건설·생산 효율) / 민간 자본(지점 공장 건설 효율, 시민 만족) / 보류 |
| `tsin_economy.50` | 금융 공황 | `tsin_stock_exchange_advance` 연구, 공황·구제 수정자 없음 | 은행 구제(금 -3, `tsin_bank_rescue`) / 금 태환 정지(인플레이션) / 방치(`tsin_financial_panic` 감쇠, 시민 불만) |
| `tsin_economy.60` | 철도 투기 열풍 (나라당 한 번) | `tsin_railway_network_advance` 연구 | 방임(5년 철도 비용 -25%, 건설 시간 -20%, 끝나면 `.61` 대기) / 인가제(철도 비용 -10%) |
| `tsin_economy.61` | 철도 거품 붕괴 | `.60` 방임 후 열풍 수정자 만료 | 국가 인수(금 -3, 인가제 수정자) / 투자자 손실(철도 비용 +20% 감쇠, 시민 불만) |
| `tsin_economy.70` | 산업 스파이 | 산업자본주의 수용, 공작 기계 미연구, 연구한 나라 존재 | 도면 복제(금 -2, 연구 속도 +5%) / 기술자 고용(금 -2, 연구 속도·공장 건설 감쇠, 시민 불만) / 자체 개발 |
| `tsin_economy.80` | 고무 붐 (나라당 한 번) | 1870년 이후, 산업자본주의 기술, 열대 밀림 농촌 지역 보유 | 특허권(최대 3곳 고무로 전환, 고무 생산 +25%, 해당 지점 불안·통제 감소) / 국가 감독(금 -2, 1곳 전환) / 숲 보존 |
| `tsin_corn_laws.1` | 반곡물법 연맹 | 제7시대, 곡물법 미폐지, 자유무역 값 < 90 | 지지(자유무역 쪽 이동, 시민 만족, 귀족 불만) / 집회 금지(귀족 만족, 시민 불만, 안정도 -) / 방관(자유무역 쪽 약간) |
| `tsin_corn_laws.2` | 곡물법 폐지 후속 (의제 `pa_tsin_repeal_corn_laws` 통과 시) | - | 지주 보상(금 -3, 귀족 만족 감쇠 보정) / 시장에 맡김(귀족 불만, 시민 만족) |
| `tsin_corn_laws.3` | 빵 폭동 | 곡물 관세 보호 중 | 곡물 수입(금 -2, 평민 만족) / 질서 회복(평민 목표 만족 -10% 감쇠) / 관세 중단(보호 해제, 귀족 불만) |
| `tsin_invention.10` | 베서머 전로 (나라당 한 번) | `tsin_bessemer_process_advance` 연구 | 사용권 판매(강철 +10%, 시민 만족) / 국영 제강소(금 -3, 강철 +10%, 철도 비용 -10%) |
| `tsin_invention.20` | 다이너마이트 (나라당 한 번) | `tsin_dynamite_advance` 연구 | 새 광산(석탄 +10%, 철 +5%) / 철도 터널(금 -2, 도로 건설 시간 -15%, 철도 비용 -10%) / 사용 제한(안정도 +) |
| `tsin_invention.30` | 냉동선 (나라당 한 번) | 1875년 이후, `tsin_machine_tools_advance` 연구, 해안 도시 보유 | 냉동육(금 -2, 가축 +15%) / 냉장 어선단(금 -2, 생선 +15%) / 해운 회사에 맡김 |
| `tsin_invention.40` | 발전기 (나라당 한 번) | `tsin_dynamo_advance` 연구 | 민간 전기 회사(전력 산출 +10%, 시민 만족) / 국영 발전 사업(금 -3, 전력 +10%, 구리 +10%) |
| `tsin_invention.50` | 전화 (나라당 한 번) | `tsin_telegraph_telephone_advance` 연구 | 국영 전화망(금 -2, 내각 효율 +5%) / 민간 전화 회사(상인 힘 +0.1, 시민 만족) |
| `tsin_invention.60` | 백열등 (나라당 한 번) | `tsin_electric_lighting_advance` 연구 | 야간 조업(생산 효율 +2%, 평민 불만) / 열람실 조명(금 -2, 최대 문해율 +2) |
| `tsin_invention.70` | 수도의 전등 (나라당 한 번) | 백열등 이벤트 뒤, 수도가 도시·대도시 | 시영 전등(금 -3, 수도 불안 -0.05, 이주 매력 +0.1) / 민간 특허(수도 이주 매력 +0.1, 시민 만족) / 가스등 유지 |
| `tsin_abolition.1` | 폐지론자 청원 (나라당 한 번) | 노예제 존재, 폐지 운동 ≥ 40 | 수용(운동 +10, 성직자 만족, 귀족 불만) / 해군 단속(노예무역 금지 정책 시행, 통치자 `protecting_against_slave_trade`, 시민 불만) / 탄압(운동 -20, `tsin_abolitionists_suppressed`, 안정도 -) |
| `tsin_abolition.2` | 해방 | 제7시대, `slavery_outlawed`, 노예 인구 남음 | 즉시 해방(귀족·시민 불만, `tsin_emancipation_shock` 감쇠) / 보상 해방(금 -4) / 도제 기간(6년 뒤 `.3`) |
| `tsin_abolition.3` | 도제 기간의 끝 | `.2` 도제 선택 후 수정자 만료 | 모든 노예 해방 |
| `tsin_abolition.4` | 해안의 노예 요새 (10년마다) | 노예무역 금지 또는 노예제 폐지, `slave_center` 보유 | 처리(바닐라 `slave_trade.5` 호출) / 묵인(안정도 -) |
| `tsin_springtime.1` | 바리케이드 (상황 시작) | 상황 대상국 | 헌법 / 진압 / 관망 (docs/situations.md) |
| `tsin_springtime.2` | 수도의 시가전 | 상황 대상국, 월 약 3% | 협상(금 -2, 자유주의 -5) / 진압(안정도 -, 자유주의 +5) |
| `tsin_springtime.10` | 봄의 끝 | 상황 종료 | 첫 선택에 따라 한 선택지만 보임 |
| `tsin_exhibition.1` | 박람회 개막 | 만국박람회 시작, 개최국 | 기계관(생산 효율 +2%, 시민 만족) / 과학 궁전(연구 +5%, 최대 문해율 +2) / 국가의 영광(위신, 안정도) |
| `tsin_exhibition.10` | 박람회 폐막 | 만국박람회 끝, 개최국 | 위신 큰 보너스 |
| `tsin_military.10` | 후장식 소총 (나라당 한 번) | `tsin_rifling_advance` 연구 | 전군 재무장(금 -3, 보병 전력 +10%) / 머스킷 개조(중보병 +5%) / 옛 교범(귀족 만족) |
| `tsin_military.20` | 철갑함의 등장 (나라당 한 번) | `tsin_ironclad_advance` 연구, 해안 지점 보유 | 건조 계획(금 -4, 중함 +10%) / 연안 방어(갤리 +15%) / 관망 |
| `tsin_military.30` | 종군 기자 (10년 쿨다운) | 전쟁 중, `tsin_telegraph_telephone_advance` 연구 | 검열(안정도 +, 자유주의 +5) / 애국 언론(육군 사기 +5%, 민족주의 +5) / 자유 보도(전쟁 피로 +1, 자유주의 -5, 시민 만족) |
| `tsin_art.10` | 낭만주의 (나라당 한 번) | 제7시대 | 민족 시인 후원(문화 영향력 +10%, 민족주의 +5) / 고전 취향(귀족 만족) |
| `tsin_art.20` | 사실주의 (나라당 한 번) | 1850년 이후, 도시 보유 | 빈민가 소설 허용(문화 영향력 +5%, 최대 문해율 +2, 노동 운동 +5) / 금서(성직자 만족, 자유주의 +5) |
| `tsin_art.30` | 사진술 (나라당 한 번) | 1840년 이후 | 사진 측량(금 -2, 내각 효율 +3%, 월 위신 +0.05) / 사진관에 맡김(시민 만족) |
| `tsin_flavor.10` | 항구의 포함 (나라당 한 번) | 1840년 이후, 공장 없음, 기술 수 상위 8국 밖, 읍 이상 항구 보유 | 협상 개항(개항 압력 +1, 상인 힘 +5%, 최대 관세 -5%, 시민 만족) / 거부(위신 +5, 귀족 만족, 민족주의 +5) |
| `tsin_flavor.20` | 농노 해방 (나라당 한 번) | 1845년 이후, 귀족 농노 특권 또는 농노제 쪽 사회 가치 < -20 | 토지와 함께 해방(특권 철회, 자유 쪽 +20, 귀족 불만, 평민 만족, 도시 이주 +10%, 원자재 -5%) / 토지 없이 해방(특권 철회, 자유 쪽 +10, 평민 불만, 시민 만족, 도시 이주 +25%, 원자재 -10%) / 유지(농노 쪽 +5, 귀족 만족, 평민 불만, 자유주의 +5) |
| `tsin_flavor.30` | 근대화 칙령 (나라당 한 번) | 개항 압력 있음(`var:tsin_treaty_ports_opened`) | 국가 개편(안정도 -, 성직자 불만, 연구 +5%, 내각 효율 +5%, 자유주의 +5) / 자강(귀족 만족, 공장 건설 효율 +10%, 규율 +2%) / 거부(위신 +5, 성직자 만족, 민족주의 +5) |
| `tsin_expedition.1` | 나일강의 수원 | 나일강 탐험이 세계 최초로 부간다 도착 | 군주 이름(위신 +15) / 지리학회(위신 +10, `tsin_expedition_geographical_society` 20년) |
| `tsin_expedition.10` | 북서항로 발견 | 북서항로 탐험 종료, 35% | 위신 +15, `tsin_expedition_geographic_fame` 20년 |
| `tsin_expedition.11` | 얼음에 막혀 돌아오다 | 북서항로 탐험 종료, 65% 또는 이미 발견됨 | 위신 +5 |
| `tsin_expedition.20` | 극점 도달 | 극지 탐험 종료, 30% | 위신 +15, `tsin_expedition_geographic_fame` 20년 |
| `tsin_expedition.21` | 유빙의 승리 | 극지 탐험 종료, 70% 또는 이미 도달함 | 위신 +5 |
| `tsin_hunger.1` | 들판의 병충해 (나라당 한 번) | 매년 2%, 평민 인구 60% 초과 | 3년 `tsin_crop_blight` |
| `tsin_hunger.2` | 기근 (재난 시작) | - | 곡물 수입(금 -4) / 수출 지속(평민 불만, 민족주의 +15) / 공공 사업(금 -2, 안정도 -) |
| `tsin_hunger.3` | 이민선 | 재난 중 | 떠나게 둠(대이민 감쇠) / 식민지 뱃삯(금 -2, 더 긴 대이민) |
| `tsin_hunger.4` | 퇴거와 식량 폭동 | 재난 중 | 소작농 편 / 지주 편(민족주의 +5) |
| `tsin_hunger.10` | 기근 이후 | 재난 종료 | 안정도 + / 농업 개혁(금 -3, 식량 +5%) |
| `tsin_society.10` | 인민헌장 (20년마다) | 의회 있음, 자유주의 ≥ 40 | 의회 논의(자유주의 -10, 귀족 불만, 자유주의 쪽) / 기각(자유주의 +5, 시민 불만) / 체포(자유주의 -15, 사회주의 +5, 안정도 -) |
| `tsin_society.20` | 파업 | 노동 운동 ≥ 40, 공장 지점 보유 | 노조 인정(노동 운동 -15, 평민 만족, 시민 불만) / 진압(`tsin_strike_broken` 감쇠, 노동 운동 +10, 사회주의 +5) / 중재(금 -2, 노동 운동 -5) |
| `tsin_society.30` | 공교육법 (나라당 한 번) | 보통 교육 기술 | 공립 학교(금 -3, 문해율, 성직자 불만) / 교회에 맡김(성직자 만족) |
| `tsin_society.40` | 사회 보험 | 사회 보험 기술, 사회주의 ≥ 30, 사회 보험 정책 아님 | 정책 시행(사회주의 -20) / 자선(사회주의 +5, 시민 만족) |
| `tsin_society.50` | 공장의 아이들 | 노동 규제 없음 정책, 공장 지점 2곳 이상 | 공장법 정책 시행(인도주의 쪽) / 방치(노동 운동 +5, 시민 만족) |
| `tsin_society.60` | 빈민가의 전염병 | 바닐라 발진티푸스 또는 인플루엔자 발생 중 | 하수도(근대 하수도 기술 필요, 금 -3, 두 질병 저항, 기대 수명 +1) / 격리(2년) / 나쁜 공기설 |
| `tsin_society.70` | 여성에게 투표권을 (15년마다) | 여성 참정권 ≥ 50 | 지방 투표권(운동 -20, 성직자 불만, 인도주의 쪽) / 거부(운동 +5, 성직자 만족) |

곡물법 의회 의제(`in_game/common/parliament_agendas/tsin_parliament_agendas.txt`): 시민 계층의 `pa_tsin_repeal_corn_laws`와 귀족 계층의 `pa_tsin_protect_grain`. 둘 중 하나의 영구 보정치(`tsin_corn_laws_repealed` / `tsin_corn_laws_protection`)만 남고, `mercantilism_vs_free_trade` 축을 조금 움직인다. 사회 가치 값이 자기 쪽이면 의제 확률이 10에서 20으로 오른다. 사용자 확인 필요: 의회 화면에 두 의제가 제7시대 이후에만 나오는지.

경제 이벤트는 `tsin_economy_yearly_pulse`(매년, `chance_to_happen = 25`)에서 고른다. 공장 판정은 검증된 바닐라 트리거 `has_building_with_at_least_one_level`로 만든 `tsin_location_has_factory_trigger`를 쓴다(`scripted_triggers/tsin_economy_triggers.txt`). AI의 금고 판정은 `gold < tsin_gold_cost_N`(`script_values/tsin_event_values.txt`)이다.

## 선택지 원칙

- 기술을 무상으로 주지 않는다(`add_advance` 같은 효과 금지).
- 선택지마다 경제, 정치(계층 만족도, 안정도), 진행(제도 진척, 건물) 사이의 교환이 있어야 한다.
- 효과 크기는 바닐라 스크립트 값(`institution_progress_*`, `*_mild_bonus` 등)을 우선 쓴다.

바닐라에는 콜레라 질병이 없다. `tsin_society.60`은 도시 위생과 관련된 바닐라 발진티푸스·인플루엔자에 연결했다. 새 질병을 만들려면 `local_<질병>_impact_modifier` 같은 보정치 형식도 함께 정의해야 하므로 이번 단계에서는 하지 않았다.
