# 이름 규칙과 충돌 검사

## 접두어
- 모드가 새로 만드는 모든 객체, 파일, 현지화 키, 변수, 플래그는 `tsin_`으로 시작한다.
- 예외: 시대 ID는 `age_7_industrialization`이다. 바닐라 시대 트리거가 `current_later_$age$_trigger` 형식이라 `age_N_이름`을 따라야 한다.
  - 같은 이유로 시대 행 이름도 바닐라 형식을 따른다: `p_building_age_7_industrialization`, `a_age_7_industrialization_*`, `n_age_7_industrialization_*`.
- 자동 생성 패치 파일: `zzz_tsin_age7_<원본 파일명>.txt` (`tools/gen_age7_patches.py`).
- 손으로 쓴 바닐라 객체 교체: `tsin_` 파일 안에서 `TRY_REPLACE:`/`TRY_INJECT:`를 쓰고 `docs/overrides.md`에 기록한다.

## 충돌 검사 결과 (2026-11-14)
- 바닐라(`game/` 전체 `*.txt`, `*.yml`, `*.gui`): `tsin_`, `age_7` 일치 0건.
- 구독한 창작마당 모드 121개: 실제 식별자 충돌 0건.
  - 문자열 일부만 겹치는 거짓 양성: `3766375743`의 `tv_wonder_display_image_7_desc`, `3830305546`의 `splatsin_desc`.
- 재검사: `python tools/validate.py --prefix-scan`

## 파일·키 형식
- 스크립트 `.txt`: UTF-8 BOM, 탭 들여쓰기.
- 현지화: `main_menu/localization/<언어>/tsin_<주제>_l_<언어>.yml`, UTF-8 BOM, 첫 줄 `l_<언어>:`.
- 이벤트 네임스페이스: `tsin_industry`, `tsin_society`, `tsin_electric`, `tsin_military`, `tsin_system`, `tsin_flavor`.
- 지도 모드: `tsin_mm_<이름>`.
- 변수: `tsin_<대상>_<의미>` (예: `tsin_investment_pool`).
