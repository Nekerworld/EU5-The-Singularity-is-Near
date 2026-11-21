# 제7시대 콘텐츠 원본

이 폴더가 제7시대 콘텐츠의 편집 원본입니다. 기술·시대관·시대 규칙·건물·재화·산업·부대·법·개혁·기업 및 역사 사건·상황·재앙과 그 패널·전용 현지화·이미지를 관리합니다. 제7시대에 도입되어 이후 시대에도 이어지는 콘텐츠도 여기 소속입니다.

## 편집과 실행

EU5의 실행 경로는 `in_game`, `main_menu`, `loading_screen`입니다. `era_7/in_game/...`를 엔진의 새로운 마운트 경로로 등록하는 방식은 쓰지 않습니다. 아래 명령이 원본 파일을 기존 엔진 경로로 바이트 그대로 배치합니다. 파일명·객체 ID·이벤트 ID·네임스페이스·그림의 가상 경로·기존 덮어쓰기 순서는 유지됩니다. GUI의 동적 패널 파일명과 Glorp 호환 파일도 이전 실행 경로를 계속 사용합니다.

```powershell
python tools/sync_eras.py
python tools/validate.py
```

게임을 켜기 전에 원본을 편집한 뒤 동기화하세요. 실행용 파일은 백업이 아닌 빌드 산출물이며 Git에서 제외됩니다. 실행용 파일만 직접 고치면 동기화 시 원본으로 덮어씁니다. `python tools/sync_eras.py --check`와 표준 검증기가 원본 누락·실행용 파일 불일치·미등록 파일을 오류로 보고합니다. 저장소를 새로 받았을 때도 먼저 동기화해야 합니다. 배포 생성기는 검증 생략 옵션을 사용해도 먼저 동기화하고 실행 폴더만 배포합니다.

새 파일은 `era_7/in_game/...` 또는 `era_7/main_menu/...`에 만든 뒤 `python tools/sync_eras.py --register`로 등록·배치합니다. 기존 전역 파일과 경로가 충돌하면 덮어쓰지 않고 중단합니다. 파일을 제거하거나 실행 경로를 바꾸는 작업은 manifest와 이전 실행용 파일도 함께 정리해야 합니다. 동기화는 파일을 자동 삭제하지 않습니다.

`tools/pdx.py`의 `content_path`·`read_text`·`read_bytes`는 등록된 실행 경로를 이곳의 원본으로 해석합니다. `write_text_bom`·`write_bytes`는 원본과 실행용 파일에 함께 씁니다. 기업·법안·이미지 생성기를 포함한 기존 생성기도 이 경로를 사용합니다. 도구의 문서나 코드에 적힌 기존 `in_game/...` 경로는 게임상의 실행 경로를 뜻합니다. 실제 편집 파일은 `manifest.json`에서 대응되는 경로를 찾으세요.

## 기존 경로에 남긴 항목

- 공용 TSIN 관리 창, 현황 버튼, 주식 탭, Glorp 연결 및 해당 GUI 생성기·현지화.
- GDP·교육·인구·사회운동·집계·시간 가속 등 여러 시대가 사용할 계산 체계와 지도 모드·지도 아이콘.
- 공통 on_action 진입점, 초기화/세이브 마이그레이션, 공통 이벤트·법안 처리·게임 규칙·디버그·관측 및 로그 도구.
- 바닐라/DLC 객체를 이후 시대에도 유지하는 `zzz_tsin_age7_*` 호환 패치, 건물 대체 및 시대 비교 헬퍼.
- 제8~12시대 뼈대, 전체 시대 등록표, 공용 백과사전과 공용/전용 문구가 함께 있는 현지화 파일.

공용 파일에 남아 있는 제7시대 콜백/헬퍼 호출은 연결 코드이므로 이동하지 않았습니다. 예를 들어 공통 on_action은 같은 ID로 이곳의 콘텐츠를 호출하고, 공용 UI는 여기의 기업 데이터를 표시합니다. 공용 개념/현지화 파일도 무리하게 쪼개지 않아 기존 중복 정의 및 파일 간 순서를 바꾸지 않았습니다.

## 목록과 확장

`manifest.json`은 각 원본의 게임상 상대 경로와 분류를 기록합니다. 등록은 `data/content_modules.json`이 관리합니다. 향후 `era_8` 등을 같은 방식으로 등록할 수 있으며 서로 같은 실행 경로를 소유하면 검증이 중단합니다. 다른 시대 소유의 공용 파일을 복사해 중복 정의하지 마세요.

이번 정리는 게임 콘텐츠의 바이트를 바꾸지 않았습니다. 기존 세이브에서 참조하는 객체 ID도 유지했습니다. 정적 검증과 기존 파일 해시는 경로 보존을 확인하지만, 실제 실행 확인을 대신하지는 않습니다.

| 분류 | 파일 수 |
|---|---:|
| age-definition | 1 |
| era7-advances | 12 |
| era7-age-art | 2 |
| era7-art | 118 |
| era7-artist_work | 1 |
| era7-biases | 2 |
| era7-building-and-goods-data | 3 |
| era7-building_types | 10 |
| era7-cabinet_actions | 2 |
| era7-casus_belli | 1 |
| era7-decisions | 7 |
| era7-disasters | 4 |
| era7-effects | 7 |
| era7-estate_privileges | 1 |
| era7-events | 27 |
| era7-expedition_types | 1 |
| era7-goods | 1 |
| era7-goods_demand | 4 |
| era7-government_reforms | 1 |
| era7-industry_types | 1 |
| era7-institution | 1 |
| era7-international_organizations | 1 |
| era7-laws | 6 |
| era7-levies | 1 |
| era7-localization | 60 |
| era7-missions | 2 |
| era7-modifiers | 31 |
| era7-panels | 12 |
| era7-parliament_agendas | 1 |
| era7-parliament_issues | 1 |
| era7-peace_treaties | 1 |
| era7-prices | 1 |
| era7-scripted_geography | 1 |
| era7-situations | 8 |
| era7-triggers | 5 |
| era7-unit_types | 2 |
| era7-values | 8 |
