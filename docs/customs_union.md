# 관세 동맹 (M3 조사, 선택)

## 조사 결과

바닐라 국제기구(`in_game/common/international_organizations`, readme)에는 시장을 하나로 합치는 속성이 없다. 쓸 수 있는 것은 다음과 같다.

| 수단 | 위치 | 쓸모 |
|---|---|---|
| `tariff_exemption` 관계 | `scripted_relations/tariff_exemption.txt` | `is_exempt_from_import_tariff = yes`. 일방향(첫째 = 관세를 면제해 주는 시장 소유국, 둘째 = 면제받는 나라) |
| `create_relation` / `remove_relation` | 바닐라 이벤트(`rise_of_the_ottomans.txt`, `wokou_events.txt`) | 스크립트로 관계를 맺고 끊는다 |
| `giving_scripted_relation` / `receiving_scripted_relation` | 바닐라 트리거 | 이미 맺은 관계를 확인 |
| 국제기구 `modifier`, `leader_modifier` | readme | 회원국 보정치 (`max_tariff`, `global_merchant_power` 등) |
| `on_joined`, `on_left` | readme | 가입·탈퇴 때 효과 |
| `trade_access` 관계 | `scripted_relations/trade_access.txt` | 시장 없는 나라에게 교역 접근을 준다. 관세 동맹에는 쓰지 않았다 |

시장 병합(빅토리아 3의 관세 동맹처럼 시장 하나로 합치기)은 스크립트로 할 방법을 찾지 못했다. 그래서 "회원국끼리 서로 수입 관세 면제"로 근사한다.

## 구현

| 파일 | 내용 |
|---|---|
| `in_game/common/international_organizations/tsin_customs_union.txt` | 국제기구 유형 `tsin_customs_union` |
| `in_game/common/scripted_effects/tsin_customs_union_effects.txt` | `tsin_add_mutual_tariff_exemption_effect`, `tsin_remove_mutual_tariff_exemption_effect` (`PARTNER` 인자) |
| `in_game/common/biases/tsin_opinion_io.txt` | `io_opinion_tsin_customs_union` (+10) |
| `main_menu/gfx/interface/icons/international_organizations/tsin_customs_union.dds`, `illustrations/international_organization_types/tsin_customs_union.dds` | 바닐라 방어 동맹 그림의 색조를 바꾼 임시 그림 |

- 창설: 제7시대 이후, 종속국 아님, 시장 보유, 산업자본주의 수용.
- 가입: 종속국·반란국 아님, 다른 관세 동맹에 속하지 않음, 회원국과 경쟁·적대·조약 차단 관계 없음.
- 가입 시 기존 모든 회원국과 양방향 `tariff_exemption`을 만들고, 탈퇴 시 지운다.
- 회원 보정치: 최대 관세 -5%, 상인 영향력 +5%. 맹주: 상인 영향력 +10%. 맹주는 점수 방식으로 10년마다 바뀐다.
- 외교 역량 비용: 회원 수 × 0.25.
- 전쟁: 회원끼리 전쟁하면 공격·방어 측 모두 축출. 경쟁국이 생기면 자동 탈퇴.

## 한계

- 탈퇴하면 가입 전에 따로 맺은 관세 면제도 지워진다(관계 출처를 구분할 수 없음). 현지화 힌트로 알린다.
- 회원이 많아지면 관계 수가 회원 수의 제곱에 비례해 늘어난다. 성능 측정 대상(`docs/perf_baseline.md`).

사용자 확인 필요:
- 새 국제기구 유형이 창설 외교 행동 목록에 자동으로 나타나는지.
- `create_relation`으로 만든 `tariff_exemption`이 외교 화면과 관세 계산에 반영되는지.
- `on_left`가 축출·자동 탈퇴·해산 때도 실행되는지(해산 때 남은 회원의 관계가 남을 수 있음).
- `diplomatic_status_*` 키처럼 엔진이 국제기구 유형마다 찾는 현지화 키가 더 있는지(오류 로그 확인).
