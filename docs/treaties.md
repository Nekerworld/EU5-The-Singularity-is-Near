# 양자 다조항 조약

모드 레이어로 Vic3형 조항 묶음 협상을 근사한다. 바닐라 외교 C++ 장바구니·다자 조약·시장 완전 병합은 없다.

## 진입

- 외교 행동 `tsin_negotiate_treaty`(상대 선택 → 초안 상대 시드)
- 대시보드 개요 단축키「양자 조약 창」(`tsin_ui_treaties_open`)
- 창: `in_game/gui/tsin_treaties.gui` / 원장·효과: `tools/gen_treaties.py` + `ui/treaties.json`

## 수명주기

| 상태 | 의미 |
|---|---|
| 1 | 활성(구속 중) |
| 2 | 만료(관계 해제, 자유 파기) |
| 3 | 파기 |
| 4 | 재협상으로 대체됨 |

구속 5/10/15/25/99년. 조기 파기 시 반감 `tsin_tr_broken_treaty`, 5년 휴전, 상대에게 CB `tsin_tr_broken_treaty_cb`. 재협상은 즉시 조항을 빼고 초안에 다시 올린 뒤, 수락 시 구 행을 4로 닫고 새 행을 쓴다. 합병 승계는 `tsin_finance_annex_commit_effect` → `tsin_tr_succession_effect`.

## 공통 조항 (숨김 `scripted_relations`)

상호: 동맹·방위(상호배타)·불가침·지식공유·해적단속·상호관세면제·무역보호 해제  
단방향: 통행·정박·식량·보장·교역접근·관세/해협세 면제·무역전환·외국건물금지↔투자권·월간 금/호의·상품쿼터·해외신용  
즉시: 일시금·거점 할양·조약항·호의 소모/적립

엔진 스위치는 `create_relation`/`remove_relation`으로만 켠다(`visible = no`).

## TSIN 조항

| id | 연결 |
|---|---|
| `tsin_bilateral_credit` / `tsin_fx_peg` / `tsin_reserve_swap` / `tsin_debt_restructure` / `tsin_capital_market_access` | 금융 계약·환율·준비금 플래그·만기연장 |
| `tsin_unequal_open` / `tsin_revise_unequal` / `tsin_strategic_storage` / `tsin_border_sale` | 조약항·개항압력·저장고 우선방출·월경지 유상(근사) |
| `tsin_harmonize_standards` / `tsin_power_corridor` / `tsin_rail_telegraph_concession` | 규격 동조·송전 지수·기업현금 배당 |
| `tsin_academic_mission` / `tsin_exhibition_pavilion` / `tsin_table_bill` | 지식교환·박람회 플래그·법안 상정 약속 변수 |
| `tsin_lend_lease_eq` / `tsin_lend_lease_fuel` / `tsin_airbase_rights` | 비축 이전·`tsin_tr_airbase_bonus`/`tsin_tr_fuel_bonus` |
| `tsin_pollution_compact` / `tsin_labor_migration` / `tsin_colonial_sphere` | 필터 타이머·이주 매력·식민 마찰 플래그 |

패키지: 방위·통상·투자·보호·불평등·근대화·금융 안정·랜드리스·개정.

## 한계

- `goods_quota`·전략비축은 시장/저장고 완전 이전이 아니라 플래그·비상방출·금 근사
- 관세 관계 출처 구분 불가(관세동맹과 충돌 가능)
- 법인 다국적 지분·외국건물 실소유·물리 전력망 없음
- 랜드리스·비행장 보너스는 H게이트/비축·연료 해금 후에만 체감
- 거점 할양·조약항·월경지는 `ordered_owned_location` 근사(플레이어 지정 UI 없음)
- AI는 패키지·플레이어 초안 점수만 수락(≥30 확실, ≥15 허용), 자유 탐색 제안 없음

사용자 확인 필요:
- 외교 목록에 `tsin_negotiate_treaty`가 보이는지, 선택 후 창이 뜨는지(GUI `Or`는 2인자만 — 중첩 `Or`로 수정함)
- 대시보드「양자 조약 창」단축키로 창이 열리는지
- 숨김 relation이 통행·관세·동맹 호출에 실제로 반영되는지
- AI 수락 점수·월간 금/랜드리스/페그·조기 파기 CB가 기대한지
- 재협상·파기 목록이 동작하는지
