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
| `tsin_society` | `in_game/events/tsin_society.txt` | M4 | 참정권, 노동, 보건 |
| `tsin_military` | `in_game/events/tsin_military.txt` | M6 | 군사 기술, 여론 |
| `tsin_flavor` | `in_game/events/tsin_flavor.txt` | M6 이후 | 지역 플레이버 (태그 조건 금지) |

- 이벤트 ID는 `<네임스페이스>.<번호>`. 번호는 군 안에서 10 단위로 묶는다(예: 공장 10~19, 원료 20~29).
- 현지화 키는 `<id>.title`, `<id>.desc`, `<id>.a`, `<id>.b` …. 툴팁은 `<id>.a.tt`.
- 숨김 이벤트는 `title = empty_text`, `desc = empty_text`, `hidden = yes`.

## 빈도 예산

국가당 1년에 받는 `tsin_` 플레이버 이벤트 수를 `tsin_flavor_events_per_year`(현재 3)로 제한한다.

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
| `tsin_abolition.1` | 폐지론자 청원 (나라당 한 번) | 노예제 존재, 폐지 운동 ≥ 40 | 수용(운동 +10, 성직자 만족, 귀족 불만) / 해군 단속(노예무역 금지 정책 시행, 통치자 `protecting_against_slave_trade`, 시민 불만) / 탄압(운동 -20, `tsin_abolitionists_suppressed`, 안정도 -) |
| `tsin_abolition.2` | 해방 | 제7시대, `slavery_outlawed`, 노예 인구 남음 | 즉시 해방(귀족·시민 불만, `tsin_emancipation_shock` 감쇠) / 보상 해방(금 -4) / 도제 기간(6년 뒤 `.3`) |
| `tsin_abolition.3` | 도제 기간의 끝 | `.2` 도제 선택 후 수정자 만료 | 모든 노예 해방 |
| `tsin_abolition.4` | 해안의 노예 요새 (10년마다) | 노예무역 금지 또는 노예제 폐지, `slave_center` 보유 | 처리(바닐라 `slave_trade.5` 호출) / 묵인(안정도 -) |
| `tsin_springtime.1` | 바리케이드 (상황 시작) | 상황 대상국 | 헌법 / 진압 / 관망 (docs/situations.md) |
| `tsin_springtime.2` | 수도의 시가전 | 상황 대상국, 월 약 3% | 협상(금 -2, 자유주의 -5) / 진압(안정도 -, 자유주의 +5) |
| `tsin_springtime.10` | 봄의 끝 | 상황 종료 | 첫 선택에 따라 한 선택지만 보임 |

곡물법 의회 의제(`in_game/common/parliament_agendas/tsin_parliament_agendas.txt`): 시민 계층의 `pa_tsin_repeal_corn_laws`와 귀족 계층의 `pa_tsin_protect_grain`. 둘 중 하나의 영구 보정치(`tsin_corn_laws_repealed` / `tsin_corn_laws_protection`)만 남고, `mercantilism_vs_free_trade` 축을 조금 움직인다. 사회 가치 값이 자기 쪽이면 의제 확률이 10에서 20으로 오른다. 사용자 확인 필요: 의회 화면에 두 의제가 제7시대 이후에만 나오는지.

경제 이벤트는 `tsin_economy_yearly_pulse`(매년, `chance_to_happen = 25`)에서 고른다. 공장 판정은 검증된 바닐라 트리거 `has_building_with_at_least_one_level`로 만든 `tsin_location_has_factory_trigger`를 쓴다(`scripted_triggers/tsin_economy_triggers.txt`). AI의 금고 판정은 `gold < tsin_gold_cost_N`(`script_values/tsin_event_values.txt`)이다.

## 선택지 원칙

- 기술을 무상으로 주지 않는다(`add_advance` 같은 효과 금지).
- 선택지마다 경제, 정치(계층 만족도, 안정도), 진행(제도 진척, 건물) 사이의 교환이 있어야 한다.
- 효과 크기는 바닐라 스크립트 값(`institution_progress_*`, `*_mild_bonus` 등)을 우선 쓴다.
