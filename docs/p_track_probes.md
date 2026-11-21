# P축(포병 예비대) 미확인 엔진 질문

구현일 2026-11-21. 구현한 것: 새 진형 `tsin_artillery_reserve`, 1~6시대 포병 템플릿 6개 교체. **아래 항목은 모두 게임을 실행해 확인하지 않았다(사용자 확인 필요).** 정적 검사는 `tools/tests/test_artillery_reserve.py`.

참고한 원본(설치된 1.4.x): `in_game/common/unit_formation_preference/army.txt`, `readme.txt`, `in_game/common/unit_types/00_age_templates_land.txt`, `unit_types/readme.txt`.

## A. 진형 파일
| # | 질문 | 현재 가정 | 확인 방법 |
|---|---|---|---|
| A1 | 모드가 새 키를 담은 새 파일을 추가하면 진형 선택 목록에 나오는가 | 나온다(바닐라가 한 파일에 2개를 두는 구조로 볼 때 키 단위 등록) | 육군 진형 창 목록 |
| A2 | `default = yes`가 바닐라 `balanced_army`에만 남아 새 진형이 기본값을 빼앗지 않는가 | `default = no`이므로 안전 | 새 군대 생성 시 기본 진형 |
| A3 | `reserves` 안에 `army_artillery`와 `army_auxiliary`를 둘 다 두고 가중치 100을 같이 쓰면 둘 다 예비대에 들어가는가 | 바닐라 `100 = army_auxiliary`와 같은 형식이라 동작 | 포병+보급 부대 편성 |
| A4 | 포병 수가 예비대 한도를 넘거나 전선 슬롯이 비면 엔진이 포병을 전선에 두는가 (슬롯 없는 카테고리를 어떻게 처리하는가) | 예비대에만 남음 | 보병 소수 + 포병 다수 군대 |
| A5 | 예비대 부대는 전투에서 포격(`artillery_barrage`)·`strength_damage_done`을 발휘하는가, 아니면 전선 교체용으로만 대기하는가 | 모름. 대기만 하면 보상 `strength_damage_done`은 의미 없음 | 전투 로그 비교 |
| A6 | `max_frontage`가 비어 있는 카테고리 때문에 줄어드는가 | 좌·중·우 값을 바닐라와 같게 둠(1.25) | 전선 폭 표시 |
| A7 | 진형 아이콘이 지정 없이 `_default.dds`로 나오는가, 이름 키(`tsin_artillery_reserve`)가 그대로 아이콘 파일명으로 쓰이는가 | 빈 아이콘 가능 | 진형 창 |
| A8 | 설명 문구의 `[ShowUnitCategoryName('army_artillery')]`와 `[center|e]` 표기가 바닐라처럼 풀리는가 | 바닐라 한국어/영어 설명과 같은 표기 | 툴팁 |
| A9 | AI도 이 진형을 쓰는가(AI 선택 규칙) | 쓰지 않음(플레이어 선택) | 관찰 |

## B. 템플릿 교체
| # | 질문 | 현재 가정 | 확인 방법 |
|---|---|---|---|
| B1 | `unit_types`에서 `TRY_REPLACE:a_age_N_..._artillery = { ... }`가 지원되는가 (`docs/overrides.md`의 근거는 다른 `common` 폴더 사례) | 지원됨. 안 되면 오류 없이 건너뛰고 효과 없음 | 유닛 화면 전투력, error.log |
| B2 | 파일 이름 `zzz_`가 바닐라 `00_age_templates_land.txt`보다 늦게 읽혀 교체되는가 | 그렇다 | 같은 확인 |
| B3 | `copy_from`으로 템플릿을 받는 바닐라 유닛(`a_houfnice`, `a_falconet`, `a_chambered_cannon`, `a_royal_mortar`, `a_flying_battery`, 고유 포병 `a_hwacha`, `a_cetbang_cannon`, `a_red_cannon`, `a_byz_helepolis_cannon_unit`, `a_tupchi`)이 교체된 값을 받는가 | 해석 시점이 모든 파일 로드 후라 받는다 | 각 유닛 화면 |
| B4 | `copy_from` 뒤 `combat_power`가 절대값인가 가산값인가 (`a_byz_helepolis_cannon_unit`은 0.25를 따로 지정) | 절대값은 아니고 가산(`docs/military.md`의 같은 미확인 사항) | 해당 유닛 전투력 |
| B5 | 템플릿에 새로 넣은 `strength_damage_done`이 파생 유닛의 자체 `strength_damage_done`(예: `a_hwacha` 0.2, `a_tupchi` 0.2)과 합산되는가 덮어쓰는가 | 합산 | 유닛 툴팁 |
| B6 | `strength_damage_done`이 유닛 템플릿 값으로 읽히는가(사용 예는 고유 유닛에 있음, 템플릿은 없음) | 읽힘 | 유닛 설명 |
| B7 | 보상 공식 `0.25 × (원본 CP ÷ 새 CP − 1)`(0.38/0.69/1.0/0.79/0.51/0.53)이 적절한 크기인가. 3시대는 1.0(+100%)이라 과할 수 있음 | **자리표시값**, 실제 균형은 전투 시험 후 조정 | 전투 비교 |
| B8 | 전투력은 낮추고 `bombard_efficiency`·`artillery_barrage`는 그대로 둔 것이 공성에서 원래와 같은 결과를 내는가 | 같다(전투력은 공성에 쓰이지 않는다고 봄) | 같은 요새 공성 비교 |
| B9 | 포병 전투력이 낮아지면 지휘관·정찰 합산(군대 전체 전투력 표시, AI 군사력 평가)이 어긋나는가 | 영향 작음 | AI 군대 규모 관찰 |
| B10 | 템플릿 필드 중 원본에 있는데 내가 빠뜨린 것은 없는가 (`maintenance_demand` 등 포병 템플릿엔 없음) | 없음 | 게임 버전 갱신 시 diff |

## C. 7시대
| # | 질문 | 현재 처리 |
|---|---|---|
| C1 | 7시대 포병 템플릿 `a_age_7_industrialization_artillery`(전투력 9.5, 포격 11, 요새 효율 0.40)와 파생 유닛(`a_tsin_breech_loading_battery`, `a_tsin_quick_firing_battery` 등)은 이번에 **바꾸지 않았다.** 1~6시대 포병이 낮아져 6→7시대 포병 전투력 비(2.4→9.5)가 커졌다. 보병은 3.0→3.75이다 | 확인만 했다. 7시대도 보병보다 높으므로 같은 규칙을 적용할지 사용자가 정한다 |
| C2 | 7시대는 포병이 예비대에 있어도 되는가(진형 선택은 시대 구분이 없음) | 시대 구분 없음 |

## D. 모드 호환·운영
- 다른 모드가 `army.txt`의 `balanced_army`를 덮어쓰거나 같은 포병 템플릿을 `TRY_REPLACE`하면 나중에 로드된 쪽이 이긴다(사용자 확인 필요, 호환 스캔은 `python tools/compat_scan.py`).
- 게임 패치 후: `00_age_templates_land.txt`의 1~6시대 포병 값(원본 CP 2/3/4/5/5.5/7.5)과 `army.txt` 진형 형식이 바뀌었는지 diff한다. 시험 파일의 "원본 값" 상수가 틀리면 테스트가 실패한다.
