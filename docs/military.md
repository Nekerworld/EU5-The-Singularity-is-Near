# 제7시대 군사 (M6)

## 기술 9개

`in_game/common/advances/tsin_7_military.txt`. 뿌리는 공통 해금 `tsin_reserve_system_advance`(예비군 제도)다. 모두 `for = mil`.

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
