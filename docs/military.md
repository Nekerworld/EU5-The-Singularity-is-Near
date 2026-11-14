# 제7시대 군사 (M6)

## 기술 9개

`in_game/common/advances/tsin_7_military.txt`. 뿌리는 공통 해금 `tsin_reserve_system_advance`(예비군 제도)다. 0.7부터 `for = mil`을 지웠다. 바닐라처럼 `for`는 특화 선택지에만 쓰고, 유닛 해금은 행정·외교 특화 나라도 연구할 수 있다(`docs/tech_tree_age7.md`). 0.7에서 늘어난 기술과 유닛은 아래 "0.7 추가" 절에 있다.

| 기술 | 선행 | 효과 |
|---|---|---|
| 뇌관식 소총 | 예비군 제도 | `a_tsin_line_riflemen` 해금, 군사 전술 +0.25 |
| 강선 | 뇌관식 소총 | `a_tsin_rifle_skirmishers` 해금, 경보병 전력 +10% |
| 후장포 | 강선 | `a_tsin_breech_loading_battery` 해금, 포병 전력 +10% |
| 연발총 | 강선 | `a_tsin_mounted_rifles` 해금, 중보병 전력 +10% |
| 수동 기관총 | 연발총, 후장포 | 중보병 +10%, 경보병 +5%, 육군 사기 +5% |
| 참모본부 | 뇌관식 소총 | 규율 +5%, 연대 보충 속도 +10% |
| 철갑함 | 예비군 제도 | `n_tsin_ironclad` 해금 |
| 모니터함 | 철갑함 | `n_tsin_monitor` 해금 |
| 어뢰 | 철갑함 | `n_tsin_torpedo_boat` 해금, 경함 전력 +10% |

### 0.7 추가: 군사 일반 10개와 유닛 해금 10개
일반 기술(같은 파일): 근대 전술(전투 속도 +10%), 철도 동원(이동 +10%, 모집 +20%, 철도망 교차 선행), 야전 축성(군사 전술 +0.25), 징병 예비(인력 +25%), 공성 공학(공성 +0.2), 강습 교리(강습 +0.2), 강선 공성포(요새 대상 포병 +1), 해군 포술(해군 사기 +0.2), 증기 수리(해상 수리 +1%), 군 의학(인구 손실 -5%).

유닛 해금(시대 전반과 후반에 상위 유닛이 한 번 더 나오는 바닐라 흐름):

| 기술 | 선행 | 유닛 | 시기(선도국) |
|---|---|---|---|
| 창기병 | 뇌관식 소총 | `a_tsin_lancers` 중기병 | 전반 |
| 철도 보급대 | 철도 동원 | `a_tsin_railway_supply_corps` 보조 | 1860년대 |
| 맥심 기관총 | 수동 기관총, 베서머 | `a_tsin_machine_gun_detachment` 보조 | 1880년대 |
| 무연 화약 | 연발총, 다이너마이트 | `a_tsin_bolt_action_infantry` 중보병 | 1880년대 |
| 엽병 | 무연 화약 | `a_tsin_jaegers` 경보병 | 후반 |
| 속사포 | 맥심 기관총, 무연 화약, 평로법 | `a_tsin_quick_firing_battery` 포병 | 1890년대 |
| 증기 수송선 | 예비군 제도 | `n_tsin_steam_transport` 수송 | 전반 |
| 방호 순양함 | 모니터함, 베서머 | `n_tsin_protected_cruiser` 경함 | 1880년대 |
| 구축함 | 어뢰, 방호 순양함 | `n_tsin_destroyer` 경함 | 1890년대 |
| 전노급 전함 | 방호 순양함, 해군 포술, 평로법 | `n_tsin_pre_dreadnought` 중함 | 1890년대 |

후반 유닛은 연도 조건 없이 긴 선행 사슬과 강철 교차 선행으로 늦춘다. 물자는 `tsin_army_demands.txt`의 0.7 절(무연 화약 보병은 폭약 소모, 전노급 전함은 전기 소모)이다.

## 유닛

`in_game/common/unit_types/tsin_age7_units.txt`. 제7시대 템플릿(`tsin_age_templates.txt`)을 `copy_from`으로 받는다. 바닐라 `n_ship_of_the_line`(`movement_speed = -1`, `hull_size = 20`)처럼 `copy_from` 뒤의 능력치는 템플릿에 더하는 값으로 썼다.

| 유닛 | 템플릿 | 템플릿 대비 | 물자 |
|---|---|---|---|
| 전열 소총병 | 중보병 | 없음 | 바닐라 `rifle_infantry_*` |
| 소총 산병 | 경보병 | 주도권 +5, 측면 +0.25 | 바닐라 `rifle_infantry_*` |
| 후장포대 | 포병 | 전투력 +1.5, 포격 +2 | `tsin_breech_artillery_*`(강철, 폭약 포탄) |
| 기마 소총병 | 경기병 | 전투력 +0.5, 주도권 +3 | `tsin_repeater_construction`, 바닐라 `heavy_cavalry_maintenance` |
| 철갑함 | 중함 | 선체 +40, 포 +20, 속도 -1 | `tsin_ironclad_*`(강철 25, 기관 4, 석탄 유지) |
| 모니터함 | 갤리(연안) | 선체 +23, 포 +28, 속도 -1 | `tsin_monitor_*` |
| 어뢰정 | 경함 | 선체 -12, 포 +6, 속도 +4 | `tsin_torpedo_boat_*`(폭약) |

물자 정의는 `in_game/common/goods_demand/tsin_army_demands.txt`. 그림은 바닐라 `unit_illustrations`의 시대별 일반 그림(6시대)으로 대체된다.

사용자 확인 필요:
- `copy_from` 뒤 능력치가 정말 더해지는지(유닛 화면에서 철갑함 선체가 템플릿 80 + 40 = 120인지). 덮어쓰기라면 수치를 절댓값으로 바꾼다.
- 해금 전에는 모집 목록에 보이지 않고, 해금 뒤에는 모집할 수 있는지(템플릿의 `hide = yes`, `buildable = no`가 복사되는지).
- 유닛 그림이 빈칸 없이 나오는지.

# 제7시대 예술 (M6)

바닐라 `symphony`와 `motet`의 시대 조건은 자동 생성 덮어쓰기(`in_game/common/artist_work/zzz_tsin_age7_00_default.txt`)가 이미 "제6시대 이후"로 넓혔다. 그래서 제7시대에도 교향곡은 계속 나오고 모테트는 나오지 않는다.

새 작품 종류는 `in_game/common/artist_work/tsin_artist_work.txt`에 있고, 모두 제7시대 이후에만 나온다.

| 작품 | 예술가 | 가치 | 전통 배수 | 영향력 배수 | 바닐라 비교 |
|---|---|---|---|---|---|
| `tsin_romantic_painting` 낭만주의 회화 | 화가 | 350 | 1.4 | 1.0 | 회화 300 |
| `tsin_photograph` 사진 | 화가 | 120 | 0.5 | 1.2 | 세밀화 150 |
| `tsin_opera` 오페라 | 작곡가 | 500 | 0.8 | 2.0 | 교향곡 600 |
| `tsin_realist_novel` 사실주의 소설 | 작가 | 400 | 0.4 | 2.2 | 소설 350 |

이름은 바닐라 회화·소설과 같은 `$ADJECTIVE|U$ $FIRST_NOUN|U$` 형식을 쓴다. 그림은 바닐라 작품 그림의 색상을 돌린 임시 그림이다.

예술 이벤트 `tsin_art.10~30`(낭만주의, 사실주의, 사진술)은 `docs/event_framework.md`에 있다.

사용자 확인 필요: 새 작품 종류가 실제로 만들어지는지(예술가가 작품 종류를 고르는 방식이 `allow`만 보는지), 작품 이름이 `_name` 키로 나오는지, 그림이 작품 창에 보이는지.

# 제7시대 탐험 (M6)

`in_game/common/expedition_types/tsin_expeditions.txt`. 세 탐험 모두 제7시대 이후, 전쟁 중이 아닐 때, 탐험가가 있을 때만 시작할 수 있다. 경로는 정적 경유지만 쓰고 귀환 구간(`returns_home`)은 없다.

| 탐험 | 경로 | 비용 | 조건 | 결과 |
|---|---|---|---|---|
| `tsin_source_of_the_nile_expedition` 나일강 수원 | 가장 가까운 항구 → 바가모요 → 우지지 → 부간다 → 곤도코로 (육·해) | 금 ×2 | 아무도 수원을 찾지 않음, 한 나라 한 번 | 부간다 첫 도착 시 `tsin_expedition.1`, 완주 시 위신 +10과 `tsin_expedition_geographic_fame` |
| `tsin_northwest_passage_expedition` 북서항로 | 비농촌 항구 → 고트호브 → 이칼루이트 (바다) | 금 ×3 | 비농촌 항구 보유, 아무도 항로를 찾지 않음 | 35% 발견(`.10`), 65% 귀환(`.11`), 반복 가능 |
| `tsin_polar_expedition` 북극점 | 비농촌 항구 → 함메르페스트 → 바렌츠해 (바다) | 금 ×3 | 1870년 이후, 철갑함 기술, 아무도 극점에 이르지 않음 | 30% 도달(`.20`), 70% 귀환(`.21`), 반복 가능 |

북극 안쪽(`arctic_archipelago`, `utqiagvik`)은 지도에서 지나갈 수 없는 곳이다. 그래서 북서항로와 북극점 탐험은 얼음 가장자리까지 항해한 뒤 `on_end`에서 확률로 결과를 정한다. 세계 최초 여부는 전역 변수(`tsin_nile_source_found`, `tsin_northwest_passage_found`, `tsin_pole_reached`)로 판정한다. 실패하면(`on_fail`) 위신 -5.

보정치(`main_menu/common/static_modifiers/tsin_expedition_modifiers.txt`):

| 보정치 | 효과 |
|---|---|
| `tsin_expedition_geographic_fame` 지리학적 명성 | 외교 평판 +1, 월 위신 +0.05 |
| `tsin_expedition_geographical_society` 왕립 지리학회 | 연구 속도 +3%, 문화 영향력 +5% |

사용자 확인 필요:
- 탐험 창에 세 탐험이 보이고 시작되는지, 비용이 빠지는지.
- 나일강 탐험대가 바가모요에서 내륙 경로(`travel_mode = both`)로 곤도코로까지 가는지.
- 북서항로·북극점 탐험이 마지막 경유지에서 끝나며 결과 이벤트가 뜨는지.
- AI가 탐험을 실제로 보내는지(`utility` 5/3/2).

# 제7시대 조약항 (M6)

강화 조약 `tsin_open_treaty_port`(`in_game/common/peace_treaties/tsin_treaty_port.txt`). 제7시대 이후, 승전국의 연구한 기술 수가 패전국보다 많을 때만 요구할 수 있다. 국가 태그 조건은 없다.

- 대상: 패전국의 수도가 아닌 항구 지점 중 농촌 정착지가 아닌 곳(읍 이상), 아직 조약항이 아닌 곳. 같은 지점의 할양과는 함께 요구할 수 없다(`are_targets_exclusive`).
- 전쟁 점수: 기본 10 + 지점 강화 비용의 절반, 최대 40.
- 반감: `antagonism_tsin_treaty_port`(요새 해체와 같은 값 1, 매년 2 감소, `in_game/common/biases/tsin_opinion_io.txt`).
- AI 희망도: 기본 5, 반란국 상대는 0.

효과(모두 30년):

| 대상 | 보정치 | 효과 |
|---|---|---|
| 개항 지점 | `tsin_treaty_port` 조약항 | 시장 접근도 +10%, 이주 매력 +0.25, 최대 통제 -10%, 불안 +0.25 |
| 패전국 | `tsin_unequal_treaty` 불평등 조약 | 최대 관세 -5%, 월 위신 -0.05 |
| 승전국 | `tsin_treaty_port_concessions` 조약항 이권 | 상인 힘 +5% |

지점에는 `var:tsin_treaty_port_of`(승전국, 30년), 패전국에는 개항 횟수 `var:tsin_treaty_ports_opened`가 남는다. 근대화 개혁 임무 팩(`tsin_modernization`)과 근대화 칙령 이벤트(`tsin_flavor.30`)가 이 횟수를 "개항 압력"으로 쓴다. 공통 효과는 `tsin_add_opening_pressure_effect`(`scripted_effects/tsin_event_effects.txt`)이고, 지역 이벤트 `tsin_flavor.10`에서 협상 개항을 골라도 1 오른다.

사용자 확인 필요:
- 강화 협상 화면의 기타 항목에 "조약항 개항"이 보이고, 지점 선택 목록이 뜨는지.
- `num_of_advances_researched`를 다른 나라 값과 비교하는 조건이 실제로 동작하는지(동작하지 않으면 항목이 아예 안 보인다).
- 조약 체결 뒤 지점 보정치와 양국 보정치가 붙는지.
