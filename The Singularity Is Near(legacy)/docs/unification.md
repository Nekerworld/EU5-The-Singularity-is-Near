# 민족 통일 (0.7)

상황 `tsin_national_unification`은 7시대의 민족 통일 흐름을 나라 태그 없이 **문화 집단** 기준으로 다룹니다.

## 흐름

| 단계 | 조건 | 결과 |
|---|---|---|
| 시작 | 1848년 이후, 민족주의(`var:tsin_nationalism`) 30 이상인 독립국이 있음 | 전역 변수 `tsin_national_unification_happened` (한 판에 한 번) |
| 선도국 제안 `tsin_unification.1` | 후보(독립, 평화, 민족주의 30 이상)이고, 같은 문화 집단의 다른 독립국이 2개 이상, 그중 인구가 더 큰 나라가 없고 이미 선도국인 나라도 없음 | 수락: `tsin_unifier`, 보정치 `tsin_unification_drive`, 전쟁 명분 사용 가능. 거절: 10년간 `tsin_unification_declined` |
| 국민 투표 `tsin_unification.10` → `.11` | 선도국, 해마다 15% | 인구가 더 작은 비강대국 동족 국가 하나에 제안. 수락하면 `annex_country_diplomatically`로 합병(`.12`), 거부하면 10년간 다시 제안할 수 없음(`.13`) |
| 통일 전쟁 | `cb_tsin_national_unification` | 선도국이 동족 독립국에게 사용. 전쟁 목표 `take_province_nationalist`, 같은 문화 집단이 다수인 주 |
| 통일 선포 `tsin_unification.20` | 선도국 주변에 같은 문화 집단의 독립국이 하나도 남지 않음 | `tsin_unified_nation`, 보정치 `tsin_national_unity` 20년, 안정도, 민족주의 −20 |
| 종료 | 1871년 이후 통일국이 있고 선도국이 남지 않음, 또는 1900년 | 선도국·보정치·동족 표시 변수 정리 |

- 연간 점검은 `on_action` `tsin_unification_yearly_pulse`에서 선도국과 후보 나라만 실행합니다(`tsin_unification_check_effect`).
- 동족 표시 `tsin_unification_kin`(2년)은 상황 지도 색과 툴팁에 쓰입니다.
- 바닐라 형성 국가(독일·이탈리아 등)는 그대로 둡니다. 통일 선포 뒤에 바닐라 결정의 조건을 채우면 형성할 수 있다고 툴팁으로 안내합니다.

## 보정치

| 키 | 효과 |
|---|---|
| `tsin_unification_drive` | 통합 속도 +10%, 외교 범위 +10% |
| `tsin_national_unity` | 통합 속도 +25%, 생산 효율 +2% |

## 사용자 확인 필요

- `has_shared_culture_group = root.culture`의 인자 형식(문화 범위 트리거, 실행 파일에는 있으나 바닐라 사용 예 없음).
- `annex_country_diplomatically`가 이벤트 안에서 AI·플레이어 모두에게 정상 동작하는지, 합병 직후 `.12` 이벤트가 선도국에게 도착하는지.
- 저장된 범위(`scope:tsin_unifier`)가 `.10` → `.11`로 넘어가는지.
- `total_population < root.total_population` 비교 형식.
- 상황 패널·힌트·전쟁 명분 표시.
