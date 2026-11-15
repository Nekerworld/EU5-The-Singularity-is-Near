# 제7시대 역사 사건 — 첫 제작분

F2는 기존 경제 패널을 유지한다. 이번 역사 제작분은 GUI와 독립적인 연간 사건이다.

1837~1899년 제7시대 국가에 새 사건 24개를 제공한다. 국가별 사건열 상태를 저장하며 다른 나라가 먼저 봤다고 전 세계에서 사라지지 않는다. 기존 콜레라·기근·통일·불황 사건을 복제하지 않았다.

| 사건열 | ID | 역사적 배경·자료 | 추가 조건 |
|---|---|---|---|
| 편지를 보내기 전에부터 4단계 | 1, 2, 3, 4 | [1840년 배경](https://postalmuseum.si.edu/exhibition/international-philately-europe-northern-europe/great-britain) | `도시 보유` |
| 실험실에서 나온 보라색부터 4단계 | 5, 6, 7, 8 | [1856년 배경](https://collection.sciencemuseumgroup.org.uk/people/ap17271) | `has_advance = tsin_synthetic_dyes_advance` |
| 주머니에 박은 리벳부터 4단계 | 9, 10, 11, 12 | [1873년 배경](https://www.levistrauss.com/levis-history/) | `has_embraced_institution = institution:tsin_industrial_capitalism` |
| 움직이는 사진부터 4단계 | 13, 14, 15, 16 | [1895년 배경](https://www.institut-lumiere.org/le-cinematographe-lumiere) | `has_embraced_institution = institution:tsin_electrification` |

| 단발 소재 | ID | 배경 자료 |
|---|---|---|
| 큰 종에 생긴 균열 | 17 | [1858년 배경](https://www.parliament.uk/about/living-heritage/building/palace/big-ben/building-clock-tower/constructing-the-most-accurate-clock-in-the-world/) |
| 돌이 되었다는 거인 | 18 | [1869년 배경](https://brucemuseum.org/discover/the-cardiff-giant/) |
| 비둘기가 나르는 편지 | 19 | [1870년 배경](https://postalmuseum.si.edu/object/npm_0.260305.10.36.3) |
| 자동차와 속도 제한 | 20 | [1896년 배경](https://nationalmotormuseum.org.uk/help-centre/motoring-firsts/who-was-the-first-person-to-be-charged-for-a-speeding-office/) |
| 고통 없는 수술 시연 | 21 | [1846년 배경](https://pmc.ncbi.nlm.nih.gov/articles/PMC10431558/) |
| 하늘과 전신선 | 22 | [1859년 배경](https://www.nesdis.noaa.gov/about/k-12-education/space-weather/what-was-the-carrington-event) |
| 기계에서 나오는 목소리 | 23 | [1877년 배경](https://www.si.edu/spotlight/phones) |
| 광견병 연구실에서 온 보고 | 24 | [1885년 배경](https://www.pasteur.fr/en/about-us/our-dna/history) |

## 발생·선택·균형

- 국가에 도시가 있고 연도·시대·기술 조건을 만족할 때 추첨한다. 기술은 이미 연구한 지식의 활용·시연으로 설명하며 이벤트가 무료 연구 완료를 제공하지 않는다.
- 별도 **TSIN 추가 역사 사건** 규칙에서 기본 연 1회·고밀도 연 2회·끔을 선택한다. 기존 풍미 예산 3/5와 분리되어 있고, 후보가 없으면 발생하지 않는다. 이 첫 제작분만으로 장기 목표 800~1,200개 또는 바닐라 대비 3~5배를 달성했다고 주장하지 않는다.
- 동일 사건열은 한 해에 한 단계만 진행한다. 유료 선택은 `tsin_gold_cost_2`를 확인하고 같은 규모의 `change_gold_effect`를 사용한다. 중단 선택은 무료이며 해당 국가의 사건열을 종료한다.
- 성공의 작은 공공 실무 보정은 3년 만료·replace로 갱신하며 연구 1%·내각 효율 2%를 중복 누적하지 않는다. 영구 국가 보너스·무한 금·새 재앙·전쟁·영토 이전은 없다.
- 1900년부터 새 추첨을 중단하고 일시 보정은 정상 만료한다. 이 제작분에 장기 전쟁·재앙은 없어 다음 시대의 강제 종전이나 별도 청산이 없다.
- 역사 특정 사례는 배경 설명이고 인게임 사건은 현지 도입·검토·일반형이다. 모든 나라에 똑같은 영국 우표·카디프 유물을 실제로 생성하는 구현은 아니다.
- 각 연간 추첨에서 도시 조건을 먼저 한 번 확인하고 사건별 반복 지점 순회를 하지 않는다. 전 세계·모든 팝을 이벤트마다 스캔하지 않는다.

## 원본·검증

자료와 고정 ID는 `data/historical_events_wave1.json`, 생성기는 `tools/gen_historical_events_wave1.py`다. 게임 파일 여섯 개는 `era_7/manifest.json`에 등록된 원본과 기존 엔진 경로의 실행용 파일로 관리한다. 생성기에 `--check`를 사용하고 `tools/sync_eras.py --check`로 이행을 검사한다.

사건 ID/상태·중단·유료 선택·연간 진행 제한·기간·기술·manifest 등록을 회귀 검사한다. 실제 후보 필터·AI 선택·팝업 빈도·저장/로드·게임에서 읽은 텍스트는 인게임 검증 대기다.
