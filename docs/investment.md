# 투자 풀 근사 (M3)

상태: **스크립트 작성 완료, 효과는 사용자 확인 필요**

빅토리아 3의 투자 풀(소유 인구가 배당 일부를 재투자)은 EU5에 없다. EU5에서 가장 가까운 장치는 다음 세 가지다.

1. **계층 자율 건설:** 계층(estate)은 자기 돈으로 건물을 짓는다. 건물에 `forbidden_for_estates = yes`가 없으면 계층이 지을 수 있다. 모드의 공장(`tsin_machine_works`, `tsin_mechanized_textile_mill`, `tsin_fertilizer_plant`, `tsin_explosives_plant`)과 철도역에는 이 금지를 넣지 않았다.
2. **계층 건설 비용 보정치:** 바닐라 `small_estate_building_cost_modifier`, `expensive_estate_building_cost_modifier`, `burghers_estate_allowed_to_build_roads`, `burghers_estate_allowed_to_build_rgo`.
3. **고용 체계:** 바닐라 `capitalism`은 잠재 수익이 높은 건물부터 인력을 채운다(`employment_systems/00_default.txt`).

## 산업 투자법 `tsin_industrial_investment_law`

`tsin_industrial_capitalism_advance`가 `unlock_law`로 해금한다(바닐라 `press_law`와 같은 방식). 파일: `in_game/common/laws/tsin_economic_laws.txt`.

| 정책 | 국가 건설 | 계층 건설 | 그 밖 | 선호 계층 |
|---|---|---|---|---|
| 국가 주도 산업화 | 공장 건설 효율 +10% | 소형 +10%, 대형 +25% 비용 | 절대주의 쪽으로 약하게 이동 | 왕실 |
| 혼합 투자 | 공장 건설 효율 +5% | 변화 없음 | 시민 계층 도로 건설 허용 | 왕실, 시민 |
| 민간 기업 주도 | 변화 없음 | 소형·대형 -15% 비용 | 시민 계층 도로·원자재 건물 건설 허용, 자본 경제 쪽으로 이동. **고용 체계가 `capitalism`이어야 채택 가능** | 시민 |

## 사용자 확인 필요

- `has_employment_system = employment_system:capitalism` 문법(바닐라에는 `has_employment_system = root` 형태만 있다)
- 정책에 따라 계층이 공장을 짓는 빈도가 실제로 달라지는지(관찰 모드 100년 비교, `docs/balance_targets.md`)
- 법이 사회경제 범주에 표시되는지
