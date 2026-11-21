# 배포 절차

## 버전 규칙

`.metadata/metadata.json`의 `version`은 `MAJOR.MINOR.PATCH` 형식이다.

| 자리 | 올리는 경우 | 예 |
|---|---|---|
| MAJOR | 진행 중인 세이브를 깨는 변경. 객체 키 삭제·이름 변경, 변수 의미 변경, 시대 구조 변경 | 제8시대 추가, `tsin_engines` 이름 변경 |
| MINOR | 세이브를 깨지 않는 콘텐츠 추가 | 새 이벤트, 새 기술, 새 지도 모드 |
| PATCH | 버그 수정, 밸런스 수치, 현지화, 게임 패치 대응 | 가격 조정, 오타 |

- 1.0.0 전까지는 MINOR가 개발 단계(M1~M6)를 따른다. 0.6.0은 M6 완성판 후보다. 사용자 시험(`docs/tests/`)을 통과하면 1.0.0으로 올린다.
- 1.0.0 전에는 MINOR 변경도 세이브를 깰 수 있다. 창작마당 설명에 그렇게 적는다.
- 세이브 이전용 전역 변수 `tsin_version`(`tsin_system.1`, `tsin_on_new_age_global`)은 모드 버전과 별개인 정수다. 세이브 이전 로직이 필요한 변경을 할 때만 올린다. 현재 3이다(2: 0.7 세계 인구 기준값, 3: 0.7 방어적 근대화 단계). 이전은 `tsin_system.3`이 한 번 한다.
- `supported_game_version`은 시험한 게임 버전의 `MAJOR.MINOR.*`로 둔다. 현재 `1.4.*`다.
- 버전을 올릴 때마다 `docs/changelog.md` 맨 위에 같은 버전의 항목을 쓴다.

## 배포 순서

1. `python tools/validate.py --fix-bom`과 `python tools/audit.py`에 오류가 없어야 한다.
2. `docs/changelog.md` 맨 위 항목과 `metadata.json`의 `version`을 맞춘다.
3. 썸네일 `.metadata/thumbnail.png`(512×512, 1MB 이하)를 확인한다. 임시 그림은 `python tools/make_placeholder_art.py --thumbnail`로 다시 만든다.
4. `python tools/build_release.py`를 실행한다.
   - 1번과 3번을 다시 검사한 뒤, `in_game`, `main_menu`, `loading_screen`과 `.metadata`의 `metadata.json`, `thumbnail.png`만 `tools/out/release/The Singularity Is Near/`에 복사한다.
   - `docs/`, `tools/`, `.git`, `README.md`, `.gitignore`는 빠진다.
5. 업로드한다(사용자 확인 필요).
   - 게임 업로더에는 제외 목록이 없다. 그래서 개발 폴더가 아니라 4번의 복사본을 올린다.
   - 업로더가 모드 폴더 안의 모드만 보여 주면, 복사본을 잠시 `Documents/Paradox Interactive/Europa Universalis V/mod/` 아래로 옮겨 올린다. 올린 뒤에는 다시 뺀다.
   - 같은 `id`를 가진 모드가 둘 있으면 실행기가 헷갈리므로, 업로드하는 동안 개발 폴더 모드는 플레이셋에서 끈다.
6. 업로더가 복사본의 `metadata.json`에 창작마당 id 같은 키를 써 넣으면, 다음 `build_release.py` 실행이 그 키를 알려 준다. 그 키를 개발 폴더의 `.metadata/metadata.json`에 옮겨 적는다.
7. 창작마당 설명은 `docs/workshop_description.md`, 변경 메모는 `docs/changelog.md`의 해당 버전 항목을 붙인다.
8. `git tag v<버전>`을 달고 원격 저장소에 올린다.

## 게임 패치 대응 체크리스트

EU5가 업데이트되면 순서대로 확인한다.

1. 게임을 이 모드만 켜고 메인 메뉴까지 실행한 뒤 `python tools/scan_logs.py`로 오류를 본다.
2. `python tools/gen_age7_patches.py`로 제7시대 연장 패치를 다시 만든다. `git diff`로 바닐라 변경이 반영됐는지 본다(`docs/overrides.md` 2절).
3. `docs/overrides.md` 3절의 손으로 쓴 덮어쓰기 원본 위치(`game_triggers.txt`, `00_defines.txt`, `special_construction_demands.txt`)를 새 바닐라와 비교한다.
4. `python tools/validate.py`를 실행한다. 사라진 보정치 종류, 바닐라 참조(`goods:`, `building_type:`, `religion:`, `government_reform:`, `policy:`, `has_advance` 등), 그림 경로를 잡아낸다.
5. `python tools/audit.py`를 실행한다. 바닐라 재화 가격이 바뀌면 건물 이윤율 검사(산출 가치 ÷ 투입 비용 1.25~1.5)가 경고를 낸다.
6. 새 바닐라 시대 하드코딩이 생겼는지 `docs/age_hardcoding.md`의 검색을 다시 돌린다.
7. `NGame.END_DATE`가 그대로 바뀌는지 본다. 새 게임에서 1837년 이후에도 진행되는지 확인한다.
8. `python tools/compat_scan.py`로 플레이셋 충돌을 다시 본다.
9. M1 시험 절차서의 시험 0과 관문 A(`docs/tests/m1_test_guide.md`)를 다시 한다.
10. `supported_game_version`을 새 버전으로 바꾸고 PATCH를 올린다.

## 세이브 호환 안내

창작마당 설명과 변경 메모에 다음을 적는다.

- **모드를 켠 채 진행한 세이브에서 모드를 끄면 안 된다.** 세이브에 제7시대, 새 재화(기관, 전력 등), 새 건물, 새 제도가 들어 있다. 모드 없이 불러오면 로드에 실패하거나 시장과 건물이 깨진다.
- 진행 중인 세이브에 모드를 새로 켜는 것은 1837년 전 세이브를 권한다. 1837년이 되면 일반 새 게임과 같이 제7시대로 넘어간다.
- 1837년 이후 세이브에서 켜면 다음 연간 맥동에서 이전 처리(`tsin_yearly_country_pulse`의 `tsin_system.1`)가 전역 변수만 설정한다. 그 세이브가 제7시대로 넘어가는지와 시대 시작 이벤트가 뜨는지는 **사용자 확인 필요**다.
- 1.0.0 전에는 업데이트가 진행 중인 세이브를 깰 수 있다. MAJOR가 바뀌는 업데이트도 마찬가지다.

## 시대별 원본과 배포

제7시대 편집 원본은 `era_7/`이며 실행용 사본은 manifest에 적힌 기존 게임 경로에 생성합니다. 저장소를 받은 직후나 수동 편집 후 `python tools/sync_eras.py`를 실행합니다. `build_release.py`도 검사 전에 동기화하며 `--skip-checks`로 생략되지 않습니다. 업로드 사본은 `in_game`·`main_menu`·`loading_screen`만 포함하고 `era_7` 원본·manifest·도구를 중복 배포하지 않습니다.
