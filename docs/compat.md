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

## 대응 방침

1. **지금 할 수 있는 것:** 위 모드를 함께 쓰면 이 표의 객체에서 상대 모드의 변경이 사라진다는 점을 창작마당 설명(`docs/release.md`)에 적는다. 게임이 깨지지는 않는다.
2. **이 모드를 빼면 생기는 손실:** 위 객체는 제7시대 연장 패치 대상이다. 상대 쪽이 이기게 하면 그 객체만 제7시대에 "제6시대가 아님"으로 판정된다(예: 해당 사회 가치관 이벤트가 1837년 뒤에 안 뜸).
3. **호환 패치 후보 (구현하지 않음):**
   - `tools/gen_age7_patches.py`가 바닐라 대신 플레이셋에서 최종 적용되는 정의(예: Estates Combined의 이벤트)를 원본으로 삼아 패치를 생성하게 한다.
   - 결과는 별도 로컬 모드로 내보낸다.
   - 다른 모드의 내용을 복사해 배포하게 되므로, 이 패치는 사용자 개인 플레이셋용으로만 쓴다. 창작마당에는 올리지 않는다.
4. **사용자 확인 필요:**
   - `TRY_REPLACE`보다 먼저 읽힌 `INJECT`가 실제로 사라지는지. Formable Nations Reworked를 켜고 해당 형성 국가의 징병법 정책 목록을 확인한다.
   - 이벤트 `REPLACE:`의 실제 우선순위. Estates Combined를 켜고 `societal_values.2100` 등의 내용이 어느 쪽인지 확인한다.
