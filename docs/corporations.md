# 기업과 주식시장 (0.7)

현재 공용 기업·법·위기 규칙은 [capital_markets.md](capital_markets.md)가 기준입니다. 아래 목록은 기존 산업 기업 6종의 상세 설명이며, 전체 유형은 초기 조직 14종을 합쳐 20종입니다.

기업 결단 6종(강철·기계·직물·화학·철도·농기계)과 기업 값·효과는 `tools/gen_company_decisions.py`가 만듭니다.

- 결단: `in_game/common/decisions/tsin_company_decisions.txt`
- 값: `in_game/common/script_values/tsin_company_generated_values.txt`
- 효과: `in_game/common/scripted_effects/tsin_company_generated_effects.txt`

손으로 쓰는 부분은 `tsin_company_values.txt`(상한), `tsin_company_effects.txt`(무작위 보행, 지수, 주가 이벤트, 특허장 회수, 세계 지수), `tsin_charter_decisions.txt`, `in_game/events/tsin_corporate.txt`입니다.

기업은 국가 보정치 `tsin_company_<종류>`입니다. 기업 한도는 공용 기업·자본시장 체제에서 정합니다. 자유방임은 정책상 무제한이며, 다른 체제는 한도를 적용합니다. 같은 일반 업종에 여러 기업이 있을 수 있습니다.

| 기업 | 기술 | 가격 기준 재화 | 회사 건물 |
|---|---|---|---|
| 강철 | `tsin_bessemer_process_advance` | 강철 | `steel_mill`, `iron_mill`, `tsin_automated_iron_mill` |
| 기계 | `tsin_machine_works_advance` | `tsin_engines` | `tsin_machine_works` |
| 직물 | `tsin_mechanized_textile_mill_advance` | 직물 | `textile_mill`, `tsin_mechanized_textile_mill`, `fine_cloth_mill`, `tsin_automated_fine_cloth_mill` |
| 화학 | `tsin_improved_fertilizer_advance` | `tsin_fertilizer` | `tsin_fertilizer_plant`, `tsin_nitrogen_fixation_plant`, `tsin_explosives_plant` |
| 철도 | `tsin_railway_network_advance` | 강철 | `tsin_railway_station` |
| 농기계 | `tsin_mechanical_reaper_advance` | `tsin_farm_machinery` | `tsin_farm_machinery_works` |

목록은 생성기의 `COMPANIES`가 기준입니다.

## 본사와 주가

- 설립 때 `tsin_found_company_<c>_effect`가 회사 건물 레벨이 가장 높은 소유 위치를 본사(`var:tsin_hq_<c>`)로 정하고, 주가 `var:tsin_stock_<c>` = 100, `var:tsin_has_stock_market`을 둡니다.
- 기업 가치 `tsin_company_value_<c>` = 주가 × 회사 건물 레벨 × 해당 업종의 기업 수. 합계 `tsin_company_total_value`.
- 이전 세이브의 기업(주가 변수 없음)은 첫 분기 펄스에서 `tsin_init_existing_companies_effect`로 본사와 주가를 받습니다.

## 분기 갱신 (`tsin_stock_monthly_pulse`)

월간 국가 펄스에서 `tsin_stock_timer`(3개월)가 없을 때만 돕니다. 기업이 0개가 되면 주식시장을 해산합니다.

1. 기업마다 상승 확률 `tsin_stock_up`을 수도 시장의 재화 가격으로 정합니다: 기준가의 130% 초과 0.7, 110% 초과 0.6, 70% 미만 0.3, 90% 미만 0.4, 나머지 0.5.
2. `tsin_stock_random_walk_effect`가 보정합니다.
   - 금융 공황 −0.15, 불황 공황 −0.2, 불황 침체 −0.1, 주가 폭락 −0.1, 노동 불만 60 이상 −0.05, 비리 은폐 −0.03.
   - 고등교육률 20 이상 +0.05, 투기 과열 +0.1, 투자 특허장 +0.05.
   - 회장 행정 70 이상 +0.05, 50 미만 −0.03.
   - 0.2~0.8로 자릅니다.
3. 폭 3%(4), 6%(3), 10%(2), 15%(1) 가운데 하나를 고르고, 상승 확률로 오르내립니다. 주가는 10~1000.
4. 종합지수 `var:tsin_stock_index` = 회사 건물 레벨 + 1로 가중한 주가 평균.
5. 주가 이벤트를 판정한 뒤 이력 `tsin_index_h0`(최신)~`h7`에 넣습니다. 이력 평균 `tsin_stock_index_history_mean`.
6. 회장이 없거나 죽었으면 `tsin_corporate.10`.

세계 지수 `global_var:tsin_world_stock_index`는 해마다 처음 도는 나라의 연간 펄스(`tsin_update_world_stock_index_effect`)에서 주식시장이 있는 나라 지수의 평균으로 계산합니다.

## 구형 주가 이벤트와 현재 자동 판정

현재 `tsin_stock_market_events_effect`는 공용 위기 규칙으로 교체됩니다. 아래 140·150 이벤트는 구형 콘텐츠를 설명하는 참고용이며, 기존 분기별 12% 무작위 폭락 경로는 자동 호출하지 않습니다. 현재 자동 위기는 국지적 `tsin_finance.1`과 1900년 이후 `tsin_global_depression` 조건을 사용합니다. 정확한 임계치와 재발 대기시간은 [capital_markets.md](capital_markets.md)를 참고하세요.

- `tsin_economy.140` 투기 과열: 이력 4개 이상, 지수 > 이력 평균 × 1.5, 과열·폭락 아님, 8년 쿨다운.
  - 그대로 둔다(투기 과열 2년, 시민 만족 +) / 할인율 인상(주가 ×0.9, 안정도 +).
- `tsin_economy.150` 증시 폭락: 투기 과열 중 분기마다 12%, 또는 지수 < 이력 평균 × 0.6. 5년 쿨다운.
  - 즉시: 투기 과열 제거, 주가 ×0.7, 주가 폭락 3년, `global_var:tsin_market_crash_recent` 3년.
  - 은행 구제(금 −3배, 은행 구제) / 약한 회사는 망하게 둔다(금융 공황, `tsin_economy.50`과 같은 보정치) / 거래소 폐쇄(1년 동안 주가 갱신 중지).
- 장기 불황(`tsin_long_depression`)은 최근 폭락이 있으면 1865년 대신 1850년부터 시작할 수 있습니다.

## 특허장 (`tsin_charter_decisions.txt`)

독점·투자·산업 확장 특허장은 주식시장이 있어야 보이고, 동시에 `tsin_charter_limit`(1, 증권 거래소 +1)개까지 둡니다. 기업 해산은 모든 특허장을 거둡니다.

| 결단 | 조건 | 효과 |
|---|---|---|
| `tsin_grant_colonial_charter_decision` 식민 특허 회사 | 7시대, 기업 1개 이상, 식민지 쟁탈전 참여(`tsin_scramble_colonial_drive`), 금 3배 | 금 −3배, 안정도 −, `var:tsin_charter_colonial`, 식민 특허 회사(식민 특허장 비용 −25%, 식민 유지 효율 +10%, 식민 이주 +15%, 영구) |
| `tsin_charter_monopoly_decision` 독점 | 독점 금지법 아님, 금 3배 | 생산 효율 +3%, 시민 힘 +10%, 농민 목표 만족 −5%, 주가 ×1.1 |
| `tsin_charter_investment_decision` 투자 | 금 3배 | 공장 건설 효율 +10%, 이자 −0.5%, 주가 상승 확률 +0.05 |
| `tsin_charter_expansion_decision` 산업 확장 | 증권 거래소, 금 4배 | 기업 상한 +1, 시민 힘 +5%, 건물 유지 효율 −1% |
| `tsin_revoke_charters_decision` 회수 | 특허장 1개 이상 | 세 특허장 회수, 주가 ×0.95. AI는 독점 금지법 아래 독점 특허장이 있을 때만 |

식민 특허 회사의 원주민 저항은 아직 수정자로 나타낼 수단이 없어, 부여 때 안정도 손실과 툴팁으로만 보입니다.

## 회장 (`tsin_corporate`)

- `tsin_corporate.10` 새 회장: 시민 신분 인물을 만들고(`create_character`, 35~55세, 행정 40~90) `var:tsin_chairman`에 둡니다. 이사회 선택 인정(시민 만족 +) / 국가 감독관(안정도 +, 시민 만족 −, 주가 ×0.95).
- `.20`~`.60`은 `tsin_corporate_yearly_pulse`(살아 있는 회장, 경제 풍미 묶음, 15%)에서 나옵니다.
  - `.20` 작위 요구(한 번): 작위(위신 +, 시민 +, 귀족 −) / 거절(시민 −).
  - `.30` 차관: 금 +3배와 기업 차관 10년(이자 +0.5%) / 거절(안정도 +).
  - `.40` 대학 강좌 기부(대학급 건물): 기부 강좌 20년 / 세금(금 +2배, 시민 −).
  - `.50` 뇌물 추문(15년 쿨다운, 주가 ×0.9): 기소(회장 해임, 안정도 +, 시민 −) / 은폐(정치 영향력 −, 비리 은폐 5년).
  - `.60` 의회 진출(의회 필요, 한 번): 기업 로비 20년 / 거부(시민 −, 농민 +).

## 증권 보고서

`tsin_stock_report_decision`(플레이어, 주식시장)이 `tsin_corporate.100`을 띄웁니다. 기업별 주가, 종합지수와 2년 평균, 세계 지수, 기업 가치 합계를 보여 줍니다. 경제 화면의 **주식** 탭에서도 지수와 기업 현황을 확인할 수 있습니다. 자세한 연결 구조는 `docs/stock_market_ui.md`를 참고하세요.

## 트러스트와 독점 금지

- 법 `tsin_trust_law`(사회경제 범주, `tsin_mass_politics_advance`에서 해금):
  - `tsin_trusts_tolerated_policy` 트러스트 묵인: 생산 효율 소폭 +, 시민 만족 +. 시민 선호.
  - `tsin_antitrust_policy` 독점 금지법: 농민 만족 +, 시민 만족 −, 기업 상한 −1, 노동 불만 목표 −3. 농민·성직자 선호.
- 이벤트 `tsin_economy.160` 트러스트 문제(1880년 이후, 기업 2개 이상, 독점 금지법 아님, 15년에 한 번, 경제 풍미 묶음): 트러스트 해체(독점 금지법 시행, 트러스트 해체 5년, 노동 불만 −5) / 기업 편(시민 만족, 노동 불만 +5, 사회주의 +3).
- 이 법은 법안 대상입니다(`docs/legislation.md`).

## 사용자 확인 필요

- `create_colonial_charter_cost_modifier`의 체감.
- 기업 상한이 정책 변경으로 줄 때 이미 있는 기업이 상한을 넘으면 새로 세울 수만 없고 기존 기업은 남습니다.
- `ordered_owned_location`의 `order_by`에 위치 스크립트 값을 쓴 본사 선정, 위치를 변수에 저장하는 동작.
- `capital.market = { "market_price(goods:X)" > ... }` 비교가 기대대로 도는지.
- `random = { chance = { value = var:... multiply = 100 } }`, `change_variable`의 `multiply = { 스크립트 값 }`.
- 인물을 변수에 저장한 뒤 `var:tsin_chairman = { is_alive = yes }`, `adm >=` 판정과 이벤트 현지화 `[tsin_chairman.GetName]`.
- `create_character`가 `create_in_limbo` 없이 그 나라에 인물을 만드는지(바닐라 `banking.txt`와 같은 방식).
- 분기 펄스의 비용(기업이 있는 나라만, 3개월마다).


## 공용 기업·GUI 업데이트

초기 조직 14종과 산업 기업 6종을 공용 회계로 연결했습니다. 자유방임·기업 한도·국지 및 세계 금융위기, 창 생성 등록과 새 주식 선 그래프의 현재 동작은 [capital_markets.md](capital_markets.md)를 기준으로 합니다. 기존 본문의 산업 기업 6종과 연간 통계 설명은 원래 7시대 구현 범위를 나타내며, 기업 회계는 현재 분기 갱신입니다.
