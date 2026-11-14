# 추정 GDP와 경제 통계 (0.7)

엔진에는 GDP 값이 없어서, 연간 집계 순회(`tsin_annual_country_aggregate_effect`, `docs/labor.md`)가 끝날 때 `tsin_update_gdp_effect`가 추정합니다. 순회를 따로 늘리지 않습니다.

## 계산 (`in_game/common/script_values/tsin_gdp_values.txt`)

```
GDP = (도시·마을 세원 합 × 10 + 교역·세금 월수입 × 12 × 4 + 총인구 × 0.4) × 생산성
생산성 = 1 + 중등교육률 / 200 + 고등교육률 / 100
```

- 세원 합 `var:tsin_agg_tax_base`: 집계 순회가 이미 도는 도시·마을 지점의 `location_tax_base`를 더합니다. 시골 지점은 순회에 넣지 않고, 자급 생산 항(총인구 × 0.4)으로 대신합니다.
- 계수는 `tsin_gdp_tax_base_factor`, `tsin_gdp_income_factor`, `tsin_gdp_subsistence_per_pop`입니다.
- 저장하는 변수:
  - `var:tsin_gdp`
  - `var:tsin_gdp_per_capita` = GDP ÷ `total_population`
  - `var:tsin_gdp_growth` = 지난해 대비 %
  - `var:tsin_gdp_prev`
- 읽기용 값 `tsin_gdp`, `tsin_gdp_per_capita`, `tsin_gdp_growth`는 첫 집계 전에는 0입니다. 위치용 `tsin_location_gdp_per_capita`(지도 모드)도 있습니다.

단위는 두캇 환산 추정치일 뿐이라 절댓값보다 나라 사이 비교와 추세에 씁니다.

## 보고서와 로그

- 결단 `tsin_economy_snapshot_decision`(플레이어, 첫 집계 뒤)은 `tsin_system.30` 경제 통계 보고서를 띄웁니다. 보고서에는 GDP, 1인당, 성장률, 공장 노동자 비중, 주가 지수가 나옵니다.
- 게임 규칙 `tsin_economy_log`(기본 끔)를 켜면, 대상 나라가 매년 집계 끝에 `debug_log`로 한 줄을 남깁니다. 대상은 플레이어, 열강, 주식시장이 있는 나라입니다(`tsin_economy_log_target_trigger`).
  - 줄 형식: `TSIN_ECON;name=..;year=..;gdp=..;gdp_pc=..;growth=..;pop=..;index=..;grievance=..;sec=..;high=..;fac=..;lit=..`
  - 같은 규칙이 켜져 있으면, 스냅샷 결단은 대상 나라 전체가 지금 한 줄씩 남기게 합니다(나라마다 숨은 이벤트 `tsin_system.31`).
- 계획의 "인구 상위" 대상은 인구 순위를 비교하는 트리거가 없어서, 주식시장이 있는 나라와 국가 통계국을 둔 나라로 대신했습니다.

## 국가 통계국 개혁

- `tsin_national_statistics_bureau`(`in_game/common/government_reforms/tsin_age7_reforms.txt`).
- 행정 선택지 기술 `tsin_statistical_bureau`가 해금합니다(`unlock_government_reform`과 `allow`의 `has_advance`). 새 기술은 만들지 않았습니다.
- 효과: 정책 변경 비용 −15%, 정책 설정 비용 −10%, 내각 효율 +3%, 월 통제 +0.005.
- 이 개혁이 있으면 `tsin_system.30` 보고서가 자세한 판(`tsin_system.30.desc_bureau`)으로 바뀝니다. 인구, 생산성 배율, 교육 3단, 노동 불만, 주가 2년 평균·세계 지수, 기업 가치가 더해집니다.
- 이 개혁을 둔 나라는 `TSIN_ECON` 로그 대상이 됩니다.

## 외부 도구 `tools/econ_report.py`

```
python tools/econ_report.py [--log PATH] [--csv OUT.csv] [--html OUT.html] [--year YEAR] [--top N]
```

- 로그 파일(`debug.log`, `game.log`, `error.log`)의 `TSIN_ECON` 줄을 (나라, 해)마다 한 줄로 모읍니다. 숫자 파서는 `observer_report.py`의 것을 씁니다.
- 출력:
  - 순위 연도의 GDP 상위 N개국.
  - 1인당 GDP 최고/최저 배율. 균형 목표는 1900년 산업국/농업국 3~5배입니다.
  - CSV.
  - 외부 라이브러리 없는 HTML. GDP, 1인당 GDP, 주가 지수, 중등교육률의 시계열 그래프와 순위표가 들어갑니다.

## 사용자 확인 필요

- `location_tax_base`와 `monthly_income_trade_and_tax`의 실제 크기. 이 크기에 따라 세 항의 비중이 맞는지 봐야 합니다.
- `total_population`의 단위(1인당 값의 크기).
- `debug_log`가 디버그 모드가 아닐 때도 기록되는지. 이벤트 현지화의 `[ROOT.GetCountry.GetName]`가 로그 줄에서 풀리는지.
- 성장률이 첫 해와 영토 변화 때 크게 튀는 정도.

## 금본위제

법 `tsin_monetary_standard_law`(사회경제 분야, `in_game/common/laws/tsin_monetary_laws.txt`)는 바닐라 6시대 기술 `the_gold_standard`가 있어야 보인다.

| 정책 | 효과 |
|---|---|
| `tsin_bimetallism_policy`(복본위제) | 월 인플레이션 +0.0005, 농민 만족 목표 +, 농민이 선호 |
| `tsin_gold_standard_policy`(금본위제) | 월 인플레이션 −0.002, 대출 이자 −0.005, 금 산출 +25%, 시민 만족 목표 +, 농민 만족 목표 −, 시행 2년 |

- 의회가 있는 대중사회 국가에서는 법안으로만 바꾼다(법안 분야 120).
- 금본위제 국가는 주가가 덜 흔들린다. `tsin_stock_random_walk_effect`의 보폭 분포가 6/3/1(3·6·10%)로 좁아진다. 다른 나라는 4/3/2/1(3·6·10·15%)이다.
- 장기 불황(`tsin_long_depression`)이 시작될 때 금본위제 국가는 `tsin_gold_standard_deflation`을 5년 받는다.

사용자 확인 필요: 바닐라 기술을 쓰는 법 `potential`이 법 화면에 제대로 나오는지, `monthly_inflation` 값 크기가 체감상 적절한지.
