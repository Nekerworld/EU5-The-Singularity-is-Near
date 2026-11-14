# 호환 스캔 (M6)

## 도구

```
python tools/compat_scan.py                      # 활성 플레이셋 (playsets.json)
python tools/compat_scan.py --playset "이름"
python tools/compat_scan.py --mods 3620382806    # 창작마당 id 또는 모드 폴더
```

- 결과: `tools/out/compat_<플레이셋>.md` (git에 넣지 않는 생성물)
- 비교 항목:
  - 같은 상대 경로 파일
  - 같은 데이터베이스 폴더(`common/<db>`, `events`)의 같은 최상위 키
  - 같은 defines 키
  - 같은 영어 현지화 키
- `named_colors`는 `colors` 블록이 병합되므로 안의 색 이름끼리만 비교한다.
- 판정 규칙(사용자 확인 필요):
  - 같은 경로 파일은 모드 목록에서 뒤에 있는 모드가 이긴다.
  - 서로 다른 파일의 객체는 한 폴더 안에서 파일 이름순으로 읽힌다고 본다(`docs/load_order.md`). 그래서 `zzz_tsin_age7_*` 패치는 대부분의 다른 모드 파일보다 뒤에 읽힌다.
  - on_action은 `on_actions` 목록이 병합된다. 이 모드는 바닐라 on_action에 목록만 더하므로 겹쳐도 공존한다.
- 기존 `python tools/validate.py --compat`은 설치된 창작마당 전체에서 `TRY_REPLACE` 대상만 찾는다. 이 도구는 실제 플레이셋 기준이다.

## 결과 (2026-11-14)

### Ad Astra (3620382806, v1.62)

- 겹침 4건, 모두 on_action(`on_new_age`, `on_new_age_global`, `on_institution_embraced`, `yearly_country_pulse`) 목록 병합이다.
- Ad Astra의 시대 조건은 제1~5시대 검사뿐이다. 제7시대에서 꺼지는 콘텐츠가 없다.
- 경로, defines, 현지화 충돌은 없다.

**결정: 별도 호환 모듈을 만들지 않는다.** 두 모드는 함께 켜도 서로의 객체를 지우지 않는다. Ad Astra가 업데이트되면 `--mods 3620382806`으로 다시 스캔하고, 객체 충돌이 생길 때만 모듈 범위를 다시 정한다.

### 사용자 플레이셋 "1.3 complete enhancement" (88개, 이 모드는 아직 목록에 없음)

- 26개 모드와 겹친다. 그중 18개는 on_action 목록 병합뿐이라 문제가 없다.
- 경로, defines, 현지화 충돌은 없다.
- 이 모드의 객체는 모두 `tsin_` 접두어이므로, 실제 충돌은 모두 제7시대 연장 패치(`zzz_tsin_age7_*`, `docs/continuity.md`)가 다시 정의하는 바닐라 객체에서 생긴다.

| 모드 | 겹치는 객체 | 결과 | 영향 |
|---|---|---|---|
| Estates Combined (3765374050) | 이벤트 44개(`societal_values.*` 34개, `parliaments.5/9/23`, `culture_japan.10/16~19`, `random_event.26/108`), 의회 의제 4개(`pa_rethink_*`, `pa_reduce_*`), `portrait_late_trigger` | 우리 정의(바닐라 기준 복사본)가 적용되어 상대 변경이 사라짐 | 가장 큼. 그 모드의 계층 이벤트 수정이 이 객체들에서만 바닐라로 돌아간다 |
| Historical Tweaks (3603092142), Legacy of Timur (3604169106) | `distribution_of_power_law`에 `TRY_INJECT`한 정책 | 상대 주입이 우리 `TRY_REPLACE`보다 먼저 읽혀 사라질 수 있음 | 특정 국가(`ABL`) 전용 정책 1개 |
| Formable Nations Reworked (3599977147) | `recruitment_law`에 `INJECT`한 정책 | 같음 | 형성 국가 전용 정책 1개 |
| Character Namelist Project (3610840019), Oikoumenē (3721193233) | `english_language` | 우리 정의가 적용되어 상대의 이름 목록이 사라짐 | 잉글랜드 문화 인물 이름 |
| Italia Overhaul (3692195005) | `coa_def_absolutism_age_5_trigger`, `coa_def_revolutions_age_6_trigger` | 우리 정의가 적용됨 | 문장(紋章) 표시 조건만 |
| 역사적 영토 확장 AI (3827499481) | `revolution_disaster`, `revolutionary_chaos` | 우리 정의가 적용됨 | 그 모드의 혁명 재난 수정이 사라짐(이전부터 `docs/overrides.md`에 기록) |

### 0.7 재스캔 (2026-11-14)

- 사용자 플레이셋: 91개 중 43개와 겹친다. 늘어난 수는 로컬 호환 패치 모드(`The Singularity Is Near - Playset Compat`, 겹침 56건, 의도한 것)와 그 모드가 다시 정의하는 객체가 두 번 잡힌 것이다. 위 표 밖의 새 객체 충돌은 없다.
- Ad Astra: 겹침 5건. 0.7에서 `monthly_country_pulse` 목록 병합 1건이 늘었다. 객체 충돌은 없다.
- Modern Times (3792511867, 참고만 하고 함께 켜지 않는 모드): `yearly_country_pulse` 목록 병합과 define `NGame.END_DATE`(상대 2050.12.31, 우리 2337.12.31) 2건. 우리 `zzz_tsin_defines.txt`가 파일 이름순으로 뒤에 읽혀 우리 값이 적용될 것으로 본다(사용자 확인 필요). 0.7에서 가져온 콘텐츠는 모두 `tsin_` 이름으로 다시 썼으므로 함께 켜도 객체가 겹치지 않는다. 두 모드의 콘텐츠가 함께 돌아가며 비슷한 이벤트·건물이 겹치는 것은 권장하지 않는다.
- 0.7에서 손으로 쓴 덮어쓰기는 늘지 않았다(`docs/overrides.md` 3절 그대로). 자동 생성 패치는 117개 객체, 42개 파일이다.

## 대응 방침

1. **지금 할 수 있는 것:** 위 모드를 함께 쓰면 이 표의 객체에서 상대 모드의 변경이 사라진다는 점을 창작마당 설명(`docs/release.md`)에 적는다. 게임이 깨지지는 않는다.
2. **이 모드를 빼면 생기는 손실:** 위 객체는 제7시대 연장 패치 대상이다. 상대 쪽이 이기게 하면 그 객체만 제7시대에 "제6시대가 아님"으로 판정된다(예: 해당 사회 가치관 이벤트가 1837년 뒤에 안 뜸).
3. **개인 플레이셋용 호환 패치 모드:** 아래 "플레이셋 호환 패치" 절. 다른 모드의 내용을 복사하므로 창작마당에는 올리지 않는다.
4. **사용자 확인 필요:**
   - `TRY_REPLACE`보다 먼저 읽힌 `INJECT`가 실제로 사라지는지. Formable Nations Reworked를 켜고 해당 형성 국가의 징병법 정책 목록을 확인한다.
   - 이벤트 `REPLACE:`의 실제 우선순위. Estates Combined를 켜고 `societal_values.2100` 등의 내용이 어느 쪽인지 확인한다.

## 플레이셋 호환 패치 (로컬 전용)

```
python tools/gen_playset_compat.py                   # 활성 플레이셋
python tools/gen_playset_compat.py --playset "이름"
python tools/gen_playset_compat.py --playset "이름" --dry-run   # 보고서만
```

- 출력: 플레이셋마다 따로 만든다(`PROFILES`). 두 플레이셋이 한 패치를 같이 쓰면 다른 플레이셋 기준으로 만든 교체가 섞인다.

| 플레이셋 | 출력 폴더(`Documents/.../mod/`) | 모드 id |
|---|---|---|
| The Singularity is Near | `The Singularity Is Near - Playset Compat` | `chris.the_singularity_is_near_playset_compat` |
| 그 밖의 플레이셋 | `The Singularity Is Near - Playset Compat - <플레이셋 이름>` | `chris.the_singularity_is_near_playset_compat_<슬러그>` |

  - 개발 폴더와 git 밖에 있다. 다른 모드의 내용이 들어 있으므로 **업로드 금지**다.
  - 다시 생성하면 `in_game/`, `main_menu/`를 지우고 새로 쓴다. 손으로 쓴 패치는 출력 폴더가 아니라 `tools/compat_manual/<슬러그>/{in_game,main_menu}/`에 두면 생성 뒤에 같은 경로로 복사된다(슬러그: 플레이셋 이름의 영숫자 외 문자를 `_`로 바꾼 소문자, 예 `the_singularity_is_near`).
- 보고서: `tools/out/playset_compat_report_<슬러그>.md`
- 생성 방식:
  - 플레이셋 모드의 객체마다, 이 모드가 없을 때 이길 정의를 고른다. 같은 경로는 목록 뒤 모드, 다른 파일은 파일 이름순으로 정한다.
  - 그 정의에 `gen_age7_patches.py`와 같은 변환을 적용한다: 제6시대 검사 연장, 대체 건물 조건(`university` → `tsin_research_university` 등, 조건만 바꾸고 건설 효과는 그대로), `BILL_LAWS`의 의회 안건 잠금.
  - 교체 파일은 `zzzz_tsin_compat_*`, 주입 파일은 `zzzzz_tsin_compat_injections.txt`로 쓴다. 이름순으로 본 모드의 `zzz_tsin_age7_*`보다 뒤에 읽힌다.
- 교체 대상:
  - 본 모드의 `zzz_tsin_age7_*`가 바닐라 복사본으로 지우던 객체. 상대 모드 정의를 복원하면서 제7시대 연장도 유지한다.
  - 플레이셋 모드의 객체 가운데 제6시대 검사가 있는 것(AI 모드의 시대별 값 등).
  - 플레이셋 모드의 객체 가운데 제7시대에 대체되는 바닐라 건물을 검사하는 것(More Unique Bureaucracies 관료제, Historical National Missions 임무·이벤트, Estates Combined 이벤트).
  - `TEXT_PATCHES`: 이름을 지정한 객체의 작은 수정. 지금은 AAMO CMF 설정 `end_year`의 상한 1837 → 2337 하나다. 기본값 1737과 이미 저장된 설정값은 바꾸지 않는다. 대상 문자열이 정확히 한 번 나오지 않으면 적용하지 않고 보고서에 경고를 남긴다.
- on_action: 키별로 여러 파일이 병합되므로 키를 교체하지 않는다. 변환이 필요한 블록이 있는 파일은 같은 상대 경로로 파일 전체를 복사해 덮어쓰고, 그 블록만 바꾼다. 다른 파일의 같은 on_action 연결은 그대로 병합된다.
- 주입 재적용: 교체한 객체에 들어가던 DLC와 다른 모드의 `INJECT`/`TRY_INJECT`를 교체 뒤에 다시 넣는다(DLC 먼저).
- 시대 계층 한도: 플레이셋 모드가 `age_6_revolutions`에 주입한 `max/min_ai_privilege_per_estate` 가운데 `tsin_age_7.txt`에 없는 계층을 `TRY_INJECT:age_7_industrialization`으로 옮긴다(`in_game/common/age/zzzzz_tsin_compat_age7_estates.txt`). 그 밖의 시대 키는 보고서에 수동 검토로 남긴다.
- 건드리지 않는 것:
  - 본 모드가 의도적으로 바꾸는 객체(손으로 쓴 덮어쓰기, `tsin_` 객체)
  - `gen_age7_patches.py`가 제외하는 폴더(시대, 기술, 제도, 유닛, 가격). 시대는 위 계층 한도만 예외다.
  - UI(`.gui`), 셰이더, 지도 로케이터. 자동 병합 대상이 아니다.

### 결과 (2026-11-14)

- **The Singularity is Near (52개, 생성 대상 50개):** 교체 170개(본 모드가 지우던 정의 복원 53, 제6시대 검사 연장 72, 대체 건물 조건 98, AAMO 텍스트 패치 1, 겹치는 것 포함), on_action 파일 3개(AAMO, Historical Figure Traits, Cash & Cold Steel), 주입 1개(Legacy of Timur `distribution_of_power_law`), 시대 계층 주입 3개(Estates Combined의 `jewish_estate`, `laborers_estate`, `soldiers_estate`). 예전 88/92개 플레이셋 기준으로 남아 있던 관료제·언어 교체와 Formable Nations Reworked 주입은 사라졌다.
- **1.3 complete enhancement (92개):** 별도 폴더 `The Singularity Is Near - Playset Compat - 1.3 complete enhancement`로 다시 생성했다. 교체 315개, on_action 파일 3개, 주입 3개(DLC `education_elites_law` 1개, Legacy of Timur, Formable Nations Reworked `recruitment_law`), 시대 계층 주입 3개.
  - 실행기의 이 플레이셋은 아직 예전 폴더(`The Singularity Is Near - Playset Compat`)를 가리킨다. 새 폴더로 바꿔 넣어야 한다(사용자 작업).

### 쓰는 법

1. 실행기에서 플레이셋에 **The Singularity is Near**와 그 플레이셋의 compat 모드를 넣는다. 둘 다 목록 맨 뒤, compat이 마지막이다.
2. 플레이셋의 모드를 추가·제거하거나 창작마당 모드가 업데이트되면 `python tools/gen_playset_compat.py --playset "이름"`을 다시 실행한다.
3. 본 모드의 `gen_age7_patches.py`를 다시 돌린 뒤에도 이 도구를 다시 실행한다.

### 자동으로 하지 않는 것

- UI `.gui` 병합: 같은 GUI 파일을 여러 모드가 바꾸면 마지막 하나만 적용된다. 손으로 합친 파일은 `tools/compat_manual/<슬러그>/`에 둔다.
- 셰이더·지도 로케이터: 보류(승인되지 않음).
- 플레이셋 로드 순서 변경: 사용자가 실행기에서 정한다.
- AAMO 기본 종료 연도(1737)와 제7시대 유닛 가격: 밸런스 결정이라 그대로 둔다. CMF 메뉴에서 2337까지 올릴 수 있다.

### 사용자 확인 필요

- Estates Combined를 켠 상태에서 `societal_values.2100` 등이 그 모드의 내용인지, 1837년 뒤에도 뜨는지
- on_action 파일 덮어쓰기: AAMO 함대 생성, Historical Figure Traits 업적(빈 대학), Cash & Cold Steel 낡은 전쟁 명분 정리가 제7시대에도 도는지
- 이미 CMF 설정을 저장한 세이브에서 AAMO `end_year` 슬라이더 상한이 2337로 바뀌는지
- Estates Combined 계층(노동자·군인·유대인)의 AI 특권 한도 주입이 제7시대에 적용되는지(같은 키를 여러 번 주입했을 때 병합되는지)
- Historical National Missions·More Unique Bureaucracies에서 대학을 연구 대학으로 올린 뒤 조건이 충족되는지
- 로그(`python tools/scan_logs.py`)에 `zzzz_tsin_compat_` 파일 관련 오류가 없는지
