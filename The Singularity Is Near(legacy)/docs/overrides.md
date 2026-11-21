# 바닐라 덮어쓰기 기록

## 1. 방식 (관문 I)
| 방식 | 사용처 | 이유 |
|---|---|---|
| `TRY_REPLACE:key = { 전체 }` | common 데이터(전쟁명분, 재난, 상황, 법, 의회 안건·의제, 특권, 예술, 원정, 임무, 스크립트 트리거·값, 언어) | 객체 하나만 바꾼다. 원본이 사라져도 오류가 나지 않는다 |
| `event.id = { 전체 }` (같은 id 재정의) | 이벤트 | 파일 상단에 `namespace` 재선언. 2026-11-14 error.log에서 이벤트 관리자가 `REPLACE:ns.1`을 접두어로 처리하지 않고 `REPLACE:ns` 네임스페이스의 새 이벤트로 읽은 것을 확인해(이름공간 미정의·중복 id 오류 125건) 접두어를 뺐다. 같은 id를 나중 파일에서 다시 정의하면 "Duplicated event ID" 오류가 남고, 다른 모드(Historical Tweaks, REAI)처럼 나중 정의가 쓰인다고 본다(사용자 확인 필요) |
| `TRY_INJECT:key = { 필드 }` | 필드 추가만 필요한 경우 | V3 농노제 값 `serfdom_vs_free_subjects`에 `allow`만 얹을 때 사용(`era_7/.../zzz_tsin_serfdom_abolition.txt`). 그 밖은 블록 필드 병합 규칙이 확인되지 않아 전체 교체를 쓴다(**사용자 확인 필요**: `allow`가 도중에 거짓이 되면 값·보정치가 사라지는지) |
| 같은 이름 파일로 전체 덮어쓰기 | **사용하지 않음** | 객체 단위 방식으로 모두 해결 가능 |
| defines 키 단위 파일 | `loading_screen/common/defines/zzz_tsin_defines.txt` | defines는 키 단위로 병합된다. `zzz_` 접두어로 다른 defines 파일보다 뒤에 정렬되어 나중에 적용된다 (docs/load_order.md) |

**근거:** 바닐라 DLC와 창작마당 모드 3,354건의 사용 사례(`docs/age_hardcoding.md` 1-3).
**확인:** 실제 로드는 관문 I 시험으로 확인한다(사용자 확인 필요).
- 시험 대상 1: 트리거 `current_later_age_6_revolutions_trigger`
- 시험 대상 2: 전쟁명분 `cb_imperialism`
- 확인 방법: 로그 오류가 없는지, 제7시대 진입 후 툴팁이 정상인지.

## 2. 자동 생성 덮어쓰기
- 생성기: `tools/gen_age7_patches.py`
- 기준 원본: 설치된 EU5 1.4.x (2026-11-14)
- 범위: 117개 객체, 42개 파일(`zzz_tsin_age7_*.txt`). 목록은 `tools/out/age7_patch_report.md`에 있다.
- 바꾸는 내용(그 밖의 내용은 원본 그대로 복사한다):
  - 제6시대 검사를 "제6시대 이후"로 넓힌다.
  - 대체 건물 참조: 옛 건물 id를 묻는 조건이 7시대 업그레이드 id도 받도록 한다. 생성하는 모든 객체에 적용하고, 그 밖에 `BUILDING_TARGETS`의 21개 객체(학교·항구 조건, 엘리트 교육법, 문해율 임무, 수도회, 비잔틴 마을 권리, `building.1/.2`, 산업화 이벤트)를 추가로 생성한다. 목록과 이유는 `docs/replaced_buildings.md`.
  - 확률 입법: 바닐라 `press_law`, `education_masses_law`, `immigration_law`, `slavery_laws`(`BILL_LAWS`)의 정책마다 `allow`에 `tsin_policy_enactable_trigger = yes`를 넣는다(`docs/legislation.md`).
  - 대학 수 `total_effective_building_levels:university`는 `tsin_total_university_levels`(두 대학의 합, `tsin_replaced_building_values.txt`)로 바꾼다.
- DLC 주입 재적용: DLC 폴더(`game/dlc/*`)의 `INJECT:`가 대상 객체에 있으면, 우리 `TRY_REPLACE` 바로 뒤에 같은 블록을 다시 넣는다. 현재 3건(`education_elites_law`, `distribution_of_power_law`, `royal_court_customs_law`, 모두 D009). DLC 파일이 모드보다 먼저 읽힌다는 전제다. DLC 정책이 두 번 보이거나 사라지지 않는지 확인이 필요하다(**사용자 확인 필요**).
- **게임 패치 후 할 일:** `python tools/gen_age7_patches.py`를 다시 실행하고 `git diff`로 변경을 확인한다. 바닐라 객체 내용이 바뀌었는데 다시 생성하지 않으면, 옛 버전으로 되돌리는 셈이 된다.

## 3. 손으로 쓴 덮어쓰기
| 파일 | 객체 | 원본 위치 | 이유 |
|---|---|---|---|
| `in_game/common/scripted_triggers/tsin_age_triggers.txt` | `current_later_age_5_absolutism_trigger`, `current_later_age_6_revolutions_trigger` | `game_triggers.txt:89-104` | 제7시대에도 "제5·6시대 이후"가 참이 되도록 |
| `loading_screen/common/defines/zzz_tsin_defines.txt` | `NGame.END_DATE` | `00_defines.txt:3` | 종료일 연장 |
| `in_game/common/goods_demand/tsin_railroad_demands.txt` | `build_railroad_demand`, `maintain_railroad_demand` | `special_construction_demands.txt:66-79` | 철도 건설·유지에 석탄·도구 추가(M3). 패치 후 원본 값이 바뀌었는지 확인 |
| `in_game/common/unit_types/zzz_tsin_artillery_reserve_templates.txt` | `a_age_1_traditions_artillery` ~ `a_age_6_revolutions_artillery` 6개 | `unit_types/00_age_templates_land.txt` (1.4.x) | P축(포병 예비대). `TRY_REPLACE:`로 전체 교체. `combat_power`를 같은 시대 보병 아래로 낮추고 `strength_damage_done`을 임시 공식으로 보상. `max_strength`·`bombard_efficiency`·`artillery_barrage`는 원본과 같음. 7시대 템플릿은 건드리지 않음. 패치 후 원본 값 재확인 |
| `era_7/.../societal_values/zzz_tsin_serfdom_abolition.txt` (sync → `in_game/...`) | `TRY_INJECT:serfdom_vs_free_subjects` | 바닐라 `serfdom_vs_free_subjects` | V3: 폐지 후 값 축을 끄는 `allow`만 주입. 전체 `TRY_REPLACE`는 쓰지 않음 |
| `in_game/gui/decisions_lateralview.gui` · `technology_lateralview.gui` · `advances_lateralview.gui` | CONTENT 시대 브라우저 · 기술 시대 탭 스크롤 · 고유발전 시대 행 | 바닐라 동명 GUI | 제7–12시대가 콘텐츠/기술 UI에 보이도록. 생성기 `tools/gen_content_ages_ui.py`. 패치 후 재생성 |
| `in_game/gui/credit.gui` · `in_game/gui/ingame_topbar.gui` | 금융 하위탭 호스트 · `@left_panel_width` 570→780 | 바닐라 동명 GUI | 금융(현황·증시·신용·통화·은행·기금) 패널이 겹치지 않도록 좌측 창을 넓히고 `credit`에 TSIN 패널을 주입. 생성기 `tools/finance_ui.py` → `gen_stock_market_ui.py`. 네이티브 대출/채권 본문은 유지. 패치 후 재생성 |

(새 항목은 이 표에 추가한다.)

### 3-1. 새 파일(덮어쓰기 아님): 포병 예비대 진형
- `in_game/common/unit_formation_preference/tsin_artillery_reserve.txt`의 `tsin_artillery_reserve`(`default = no`). 바닐라 `army.txt`(`balanced_army`가 기본)는 **덮어쓰지 않는다**. 좌·중·우에서 `army_artillery`를 빼고 `reserves`에 `army_artillery`와 `army_auxiliary`를 둔다.
- 이름과 설명은 `tsin_artillery_reserve_l_*.yml`(영어·한국어). 아이콘은 지정하지 않음(바닐라 `_default.dds` 사용 여부는 사용자 확인 필요).
- 템플릿 6개를 `TRY_REPLACE:`로 교체하는 방식이 `unit_types`에서 실제로 적용되는지, 파생 유닛(`a_houfnice`, `a_falconet` 등 `copy_from`)이 바뀐 값을 받는지는 **사용자 확인 필요**(`docs/p_track_probes.md`).

## 4. 다른 모드와의 충돌
- 창작마당 3631410954 "EU5 National Ideas"는 `00_defines.txt` 전체를 덮어쓴다. `END_DATE`는 바닐라와 같은 값이다. 우리 파일은 이름 정렬상 뒤에 적용되므로 영향이 없을 것으로 본다(사용자 확인 필요, `docs/load_order.md`).
- 창작마당 3792511867 "Modern Times"도 `END_DATE`를 2050.12.31로 바꾼다(`01_mt_defines.txt`). 우리 `zzz_` 파일이 뒤에 읽혀 2337.12.31이 적용될 것으로 본다(사용자 확인 필요, 0.7 재스캔은 `docs/compat.md`).
- 같은 객체를 `TRY_REPLACE`하는 다른 모드가 있으면 나중에 로드된 쪽이 이긴다.
  - 확인된 예: 3827499481(`revolution_disaster`, `revolutionary_chaos`), 3604169106(전쟁명분 일부)
  - 호환 스캔: `python tools/validate.py --compat` (설치된 창작마당 전체), `python tools/compat_scan.py` (실제 플레이셋, 결과와 방침은 `docs/compat.md`)

- H축(8시대+ 군수·연료·공군)은 바닐라 파일을 덮어쓰지 않는다. 새 ID만 추가한다.
- 이름이 `zzz_tsin_h*`/`tsin_*`인 on_action 파일이 `monthly_country_pulse`, `on_battle_won`, `on_battle_lost`의 `on_actions` 목록에 항목을 더한다. 병합되는지는 **사용자 확인 필요**다(월간 훅은 이미 쓰는 방식, 전투 훅은 H0 실험 P3에서 확인). 병합되지 않으면 H 효과만 안 돌고 다른 기능은 영향이 없다.
- 상세는 `docs/h0_engine_probes.md`, `docs/military_hybrid_h_track.md`.
