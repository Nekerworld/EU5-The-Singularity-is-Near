# 바닐라 덮어쓰기 기록

## 1. 방식 (관문 I)
| 방식 | 사용처 | 이유 |
|---|---|---|
| `TRY_REPLACE:key = { 전체 }` | common 데이터(전쟁명분, 재난, 상황, 법, 의회 안건·의제, 특권, 예술, 원정, 임무, 스크립트 트리거·값, 언어) | 객체 하나만 바꾼다. 원본이 사라져도 오류가 나지 않는다 |
| `REPLACE:event.id = { 전체 }` | 이벤트 | 창작마당 선례(`REPLACE:black_death.1003`). 파일 상단에 `namespace` 재선언 |
| `TRY_INJECT:key = { 필드 }` | 필드 추가만 필요한 경우 | 미사용(블록 필드 병합 규칙이 확인되지 않아 전체 교체를 쓴다) |
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
- 범위: 92개 객체, 33개 파일(`zzz_tsin_age7_*.txt`). 목록은 `tools/out/age7_patch_report.md`에 있다.
- 바꾸는 내용: 제6시대 검사를 "제6시대 이후"로 넓히는 것뿐이다. 그 밖의 내용은 원본 그대로 복사한다.
- **게임 패치 후 할 일:** `python tools/gen_age7_patches.py`를 다시 실행하고 `git diff`로 변경을 확인한다. 바닐라 객체 내용이 바뀌었는데 다시 생성하지 않으면, 옛 버전으로 되돌리는 셈이 된다.

## 3. 손으로 쓴 덮어쓰기
| 파일 | 객체 | 원본 위치 | 이유 |
|---|---|---|---|
| `in_game/common/scripted_triggers/tsin_age_triggers.txt` | `current_later_age_5_absolutism_trigger`, `current_later_age_6_revolutions_trigger` | `game_triggers.txt:89-104` | 제7시대에도 "제5·6시대 이후"가 참이 되도록 |
| `loading_screen/common/defines/zzz_tsin_defines.txt` | `NGame.END_DATE` | `00_defines.txt:3` | 종료일 연장 |
| `in_game/common/goods_demand/tsin_railroad_demands.txt` | `build_railroad_demand`, `maintain_railroad_demand` | `special_construction_demands.txt:66-79` | 철도 건설·유지에 석탄·도구 추가(M3). 패치 후 원본 값이 바뀌었는지 확인 |

(새 항목은 이 표에 추가한다.)

## 4. 다른 모드와의 충돌
- 창작마당 3631410954 "EU5 National Ideas"는 `00_defines.txt` 전체를 덮어쓴다. `END_DATE`는 바닐라와 같은 값이다. 우리 파일은 이름 정렬상 뒤에 적용되므로 영향이 없을 것으로 본다(사용자 확인 필요, `docs/load_order.md`).
- 같은 객체를 `TRY_REPLACE`하는 다른 모드가 있으면 나중에 로드된 쪽이 이긴다.
  - 확인된 예: 3827499481(`revolution_disaster`, `revolutionary_chaos`), 3604169106(전쟁명분 일부)
  - 호환 스캔: `python tools/validate.py --compat` (설치된 창작마당 전체), `python tools/compat_scan.py` (실제 플레이셋, 결과와 방침은 `docs/compat.md`)
