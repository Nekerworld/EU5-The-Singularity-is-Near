# 백과사전과 힌트 (M6)

## 백과사전 개념

파일: `main_menu/common/game_concepts/tsin_concepts.txt`. 현지화 `game_concept_<키>`, `game_concept_<키>_desc`는 `tsin_m6_l_*.yml`에 있다. 다른 문구에서는 `[tsin_treaty_port_concept|e]`처럼 링크한다.

| 키 | 이름 | 아이콘 | 설명하는 것 |
|---|---|---|---|
| `tsin_electric_power_concept` | 전력 | 전력 지도 모드 아이콘 | 발전소, 세 소비처, 부족 시 생산 감소, 전력 지도 모드 |
| `tsin_industrial_investment_concept` | 산업 투자 | 산업 투자 지도 모드 아이콘 | 계층 자율 건설, 산업 투자법 세 정책 |
| `tsin_movements_concept` | 정치 운동 | 급진성 지도 모드 아이콘 | 운동 6종(0~100), 성장과 감소, 60 이상 선동, 급진성 |
| `tsin_treaty_port_concept` | 조약항 | 바닐라 시장 접근성 | 조약항 강화 조약, 30년 효과, 근대화 개혁 임무 |
| `tsin_industrial_age_situations` | 산업 시대의 상황 | 바닐라 상황 | 제7시대 상황 4종 목록 |

전력과 정치 운동은 `shown_in_loading_screen = yes`로 불러오기 화면 팁에도 나온다.

## 힌트

파일: `in_game/common/scriptable_hints/tsin_hints.txt`. 힌트는 화면마다 자주 평가되므로 국가 단위의 싼 조건만 쓴다(지점 순회 금지).

| 힌트 | 보이는 조건 | 연결 개념 |
|---|---|---|
| `hint_tsin_long_depression` 외 상황 3종 | 상황 진행 중 | - |
| `hint_tsin_electric_power` | 발전기 기술 연구, 발전소 0단계(`total_effective_building_levels:tsin_power_station < 1`) | 전력 |
| `hint_tsin_unequal_treaty` | `tsin_unequal_treaty` 보정치 있음 | 조약항 |
| `hint_tsin_radical_movements` | `var:tsin_radicalism >= 60` | 정치 운동 |

현지화는 바닐라 힌트처럼 `hint_<키>`, `_hint_text`, `_diplomatic`, `_administrative`, `_military`를 쓴다.

사용자 확인 필요:
- 백과사전에서 다섯 항목이 검색되고 아이콘이 보이는지.
- 문구 속 `[tsin_..._concept|e]` 링크가 툴팁으로 열리는지.
- 세 힌트가 조건을 만족할 때 힌트 목록에 나타나고, 조건이 풀리면 사라지는지.
