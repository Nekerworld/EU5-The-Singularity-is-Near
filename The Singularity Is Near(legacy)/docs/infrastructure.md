# 기반 시설 업그레이드 (0.7)

주거는 `docs/housing.md`, 교육 정원은 `docs/education.md`, 대체 건물 참조는 `docs/replaced_buildings.md`에 적는다.

## 업그레이드와 신규 칸

| 건물 | 대체 | 해금 | 요점 |
|---|---|---|---|
| `tsin_waterworks` 상하수도 | `aqueduct_system` | 근대 하수도 | 모든 읍·도시. 질병 저항 +0.15, 수용력 +5%, 식량 약간, 번영 |
| `tsin_steam_port` 증기선 항만 | `naval_base` | 증기 상선대 | 동시 건조 14, 수병, 항만 적합도 0.35, 시장 접근 +0.05, 이주 매력 |
| `tsin_prefecture` 도청 | `provincial_chancery` | 전문 관료제 | 개혁 조건 없이 핵심 영토에 건설. 문해 상한, 반란 문턱 −0.1, 최대 통제 +0.05 |
| `tsin_public_school` 공립 중등학교(신규) | 없음 | 보편 교육 | 과정 3단계(보통·실업·종합), 레벨 상한 `tsin_public_school_max_level` |
| `research university` | `university` | 교육 항목 | `docs/education.md` |

- 계획 문서는 증기선 부두를 `dock`의 업그레이드로 적었다. 바닐라에 이미 `dock → dry_dock → shipyard → grand_shipyard → naval_base` 사슬이 있고, `obsolete`가 겹치면 업그레이드 경로가 갈라진다. 그래서 사슬의 끝인 `naval_base`를 대체한다.
- `aqueduct_system`의 수도 보정치(정통성·공화정 전통·신앙)는 상하수도에 옮기지 않았다. 로마·콘스탄티노폴리스 등 네 곳에서 업그레이드하면 그 보정치를 잃는다.
- 공립 중등학교 레벨: 기본 1, 도시 +1, 대도시 +2, 직업 교육 +1, 선택 발전 국민 교육 +1.
- 건설 수요 `tsin_infrastructure_construction`: 석조 3, 도구 0.3, 강철 0.3, 엔진 0.05(상하수도).

## 기존 건물 확장

- 조명망 `tsin_electric_lighting`: 키는 그대로 두고 표시 이름을 "도시 조명망"으로 바꿨다.
  - 신규 기술 가스 조명(도시 계획 뒤)이 건물을 해금하고, 생산 방식 `tsin_electric_lighting_gas`(석탄 0.4, 도구 0.05)로 시작한다.
  - 전기 조명 기술은 이제 건물이 아니라 전기 생산 방식(`tsin_electric_lighting_maintenance`, 기존 키)을 해금한다. 기존 세이브의 건물은 전기 방식을 그대로 쓴다.
- 철도역 `tsin_railway_station`: 최대 2레벨(강철 차량 기술로 +1). 레벨당 시장 접근 +0.075(2레벨 합 0.15, 전에는 1레벨 0.1).
  - 전신·전화 기술이 `tsin_railway_station_telegraph`(석탄·엔진 절약, 전기 0.01)를 해금한다.

## 사용자 확인 필요

- 수도교 체계가 있는 지점에서 상하수도 업그레이드 버튼이 뜨는지, 없는 지점에서도 새로 지을 수 있는지.
- 증기선 항만이 해군 기지 업그레이드로 나타나는지, AI가 항구마다 무리하게 짓지 않는지.
- 도청이 지방 상서원 업그레이드로 동작하고, 개혁이 없는 나라에서 건설 버튼이 뜨는지.
- 조명망의 가스 방식이 기본 선택되는지.
