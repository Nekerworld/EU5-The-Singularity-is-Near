# 확률 기반 입법

대중사회를 수용하고 의회가 있는 나라는 법 정책을 "법안"으로만 바꾼다. 바닐라 의회 판정(지지 50% 기준)은 그대로 두고, 정책 시행 앞에 법안 심의 단계를 하나 더 둔다.

## 활성 조건

`tsin_bill_system_active_trigger`(country):

- 게임 규칙 `tsin_bill_system`이 켬(기본값).
- `institution:tsin_mass_society` 수용.
- `has_parliament = yes`.

조건이 하나라도 거짓이면 정책을 바닐라처럼 바로 바꾼다. 법안이 걸린 채 조건이 거짓이 되면(의회 해산 등) 다음 심의 때 법안을 지운다.

## 대상 법과 잠금

| 법 | 출처 | 잠금 방식 |
|---|---|---|
| `tsin_labor_law`, `tsin_welfare_law`, `tsin_taxation_law`, `tsin_assembly_law`, `tsin_land_reform_law`, `tsin_church_state_law` | 모드 `tsin_society_laws.txt` | 각 정책 `allow`에 직접 넣음 |
| `tsin_industrial_investment_law`, `tsin_trust_law`, `tsin_frontier_land_law`, `tsin_slave_trade_law`, `tsin_monetary_standard_law` | 모드 | 같음 |
| `tsin_women_rights_law`(`tsin_women_rights_law.txt`), `tsin_police_law`, `tsin_public_health_law`(`tsin_police_health_laws.txt`) | 모드(V 트랙) | 같음. 법안 분야 180(가족·치안·보건) |
| `press_law`, `education_masses_law`, `immigration_law`, `slavery_laws` | 바닐라 `01_common.txt` | `tools/gen_age7_patches.py`의 `BILL_LAWS`가 원본을 복사해 정책마다 잠금을 넣고 `TRY_REPLACE`로 낸다 |

- 잠금은 `tsin_policy_enactable_trigger`다. 법안 제도가 꺼져 있거나 `tsin_enact_policy_effect`가 실행 중일 때(`tsin_enacting_policy` 변수)만 참이다. 툴팁은 "의회에서 법안으로 통과되어야 한다"이다.
- 금본위제 법 `tsin_monetary_standard_law`(`tsin_monetary_laws.txt`)도 같은 잠금을 쓰고, 법안 분야 120(조세·화폐·결사)에 들어 있다.
- 바닐라 법을 `INJECT`로 고치지 않은 이유: 정책은 법 블록 안의 하위 블록이라, `INJECT`가 기존 정책의 `allow`까지 병합하는지 확인되지 않았다. 대신 원본 전체를 생성기로 복사한다(`docs/overrides.md` 2절). D009 DLC는 이 네 법에 정책을 주입하지 않는다.

## 법안 상태 (국가 변수)

| 변수 | 뜻 |
|---|---|
| `tsin_bill_policy` | 심의 중인 정책(정책 범위 값) |
| `tsin_bill_successes` | 통과한 심의 수, 3이면 통과 |
| `tsin_bill_stalls` | 막힌 심의 수, 3이면 폐기 |
| `tsin_bill_bonus` | 논쟁 보너스, −0.3~0.3 |
| `tsin_bill_check_timer` | 3개월 시한 변수, 끝나면 다음 심의 |
| `tsin_bill_cooldown` | 폐기·철회 뒤 2년 시한 변수 |

## 흐름

1. 결단 `tsin_propose_bill_decision` → `tsin_legislation.100`(분야 선택) → `.110~.170`(정책 선택). 정책 선택지는 생성기 `tools/gen_bill_events.py`가 만든다. 선택지마다 그 정책의 `potential`과 `allow`(잠금 제외)를 그대로 옮겨서, 지금 시행할 수 있는 정책만 보인다.
2. `tsin_table_bill_effect = { POLICY = policy:X BONUS = N }`가 법안을 건다. 이미 걸린 법안은 바뀐다. 법안 제도가 꺼져 있으면 바로 시행한다.
3. `monthly_country_pulse` → `tsin_bill_monthly_pulse`: 법안이 있고 시한 변수가 끝난 나라만 `tsin_bill_reading_effect`를 돈다.
4. 심의 한 번: `tsin_bill_success_chance`로 굴려 성공 또는 정체를 1 더한다. 성공 3번이면 `.2`(통과, `tsin_enact_policy_effect`로 시행), 정체 3번이면 `.3`(폐기, 2년 쿨다운). 그 밖에는 25% 확률로 논쟁 이벤트 하나.
5. 결단 `tsin_withdraw_bill_decision`으로 언제든 철회할 수 있다(2년 쿨다운).

## 성공 확률 `tsin_bill_success_chance`

0.05~0.85로 묶는다. 항목마다 `desc`가 있어 툴팁에 내역이 보인다.

| 항목 | 값 |
|---|---|
| 기본 | 0.35 |
| 계층 지지 | 법안 정책을 선호하는 계층: 계층 권력 × 0.4 |
| 계층 반대 | 같은 법의 다른 정책을 선호하는 계층: 계층 권력 × −0.3 |
| 노동 개혁(노동·복지·결사 법의 개혁 정책) | (노동 불만 + 노동조합 운동) ÷ 400, 최대 0.2 |
| 노예제 폐지(노예무역 단속, 노예제 금지) | 폐지 운동 ÷ 400, 최대 0.2 |
| 그 밖의 개혁 정책 | 자유주의 운동 ÷ 500, 최대 0.15 |
| 공화정 | 0.05 |
| 입법 효율 | `modifier:legislative_efficiency` × 0.5 |
| 논쟁 | `tsin_bill_bonus` |

개혁 정책 목록은 `tsin_bill_reform_policy_trigger`에 있다. 반대쪽 정책(예: 규제 없는 노동)은 운동 보너스를 받지 않는다.

## 논쟁 이벤트 `tsin_legislation.*`

| ID | 내용 | 선택지 |
|---|---|---|
| `.2` | 통과 | 공포 |
| `.3` | 폐기 | — |
| `.10` | 위원회 수정안 | 수용(+0.15, 정치 영향력 −5) / 거부(−0.05) |
| `.20` | 당론 강행 | 강행(+0.2, 안정도 −7) / 자유 투표 |
| `.30` | 여론전 | 선전(금화, +0.1) / 하지 않음 |
| `.40` | 철회 요구 | 철회(쿨다운, 안정도 +2.5) / 유지(−0.1) |

## 다른 콘텐츠와의 연결

- 이벤트 선택지와 의회 의제의 정책 시행은 법안 상정으로 바꿨다. 이벤트는 보너스 0.15, 의회 의제(이미 의회 표결을 거침)는 0.25로 시작한다.
  - 이벤트: `tsin_abolition.1`, `tsin_culture.20`, `tsin_economy.160`, `tsin_society.40`, `tsin_society.50`.
  - 의제: `tsin_parliament_agendas.txt`의 6건.
- 예외: 분리 위기 `tsin_secession.20`의 노예 해방은 전쟁 결과라 `tsin_enact_policy_effect`로 바로 시행한다.
- 의회 안건 `tsin_legislative_session`(입법 회기): 법안이 걸려 있을 때만 고를 수 있다. 통과하면 심의 성공 1회와 +0.1, 실패하면 −0.1.
- 바닐라 의제 `pa_change_policy`는 `add_policy`를 직접 쓴다. 잠금을 거치지 않으므로 그대로 둔다.

## AI

- 결단 가중치 5, 대중 운동이 강하면(`tsin_bill_reform_pressure_trigger`) 20.
- 정책 선택지: 기본 5. 정책을 선호하는 계층의 권력이 0.25 이상이면 계층마다 +10. 개혁 정책이고 운동이 강하면 +10.
- 철회 결단은 쓰지 않는다. 논쟁 이벤트는 기본 가중치 표(`docs/event_framework.md`)를 따른다.

## 사용자 확인 필요

- 정책 `allow`가 거짓이어도 이미 시행 중인 정책이 유지되는지, `add_policy` 효과가 `allow`를 무시하는지(무시하지 않아도 `tsin_enact_policy_effect`가 변수를 세워 통과시킨다).
- 국가 변수에 정책 범위(`policy:X`)를 담고 `add_policy = var:tsin_bill_policy`로 시행할 수 있는지.
- `any_possible_policy`가 아직 해금되지 않은 법의 정책을 빼는지.
- 이벤트 현지화의 `[tsin_bill.GetName]`(바닐라 `artist_events.42`와 같은 방식)이 정책 이름을 보이는지.
- 법 해금 직후 정책이 비어 있을 때 엔진이 기본 정책을 자동으로 고르는지. 고르지 못하면 법안으로 첫 정책을 정해야 한다.
- 의회 안건 `tsin_legislative_session`이 의회 안건 목록에 나타나는지.
