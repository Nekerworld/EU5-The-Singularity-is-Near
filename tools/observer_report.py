"""Turn TSIN_OBS log lines (game rule tsin_observer_log = on) into a table and check docs/balance_targets.md.

Usage: python tools/observer_report.py [--log PATH] [--csv OUT.csv]
  --log  read this file instead of the game's debug.log/game.log/error.log
  --csv  also write every logged year as CSV
"""
import argparse
import csv
import re
import sys
from pathlib import Path

LOGS = Path.home() / "Documents" / "Paradox Interactive" / "Europa Universalis V" / "logs"
FILES = ["debug.log", "game.log", "error.log"]
LINE = re.compile(r"TSIN_OBS;(.*)")
SITUATIONS = [("tsin_springtime_of_nations", 1), ("tsin_long_depression", 10),
              ("tsin_scramble_for_colonies", 100), ("tsin_world_exhibition", 1000)]


def num(text: str) -> float:
    text = re.sub(r"[^0-9.,KMk+\-]", "", text).replace(",", "")
    scale = 1.0
    if text[-1:] in ("K", "k"):
        scale, text = 1e3, text[:-1]
    elif text[-1:] == "M":
        scale, text = 1e6, text[:-1]
    try:
        return float(text) * scale
    except ValueError:
        return float("nan")


def read_rows(paths: list[Path]) -> list[dict]:
    by_year: dict[int, dict] = {}
    for path in paths:
        if not path.exists():
            continue
        for ln in path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = LINE.search(ln)
            if not m:
                continue
            row = {}
            for part in m.group(1).split(";"):
                if "=" in part:
                    key, value = part.split("=", 1)
                    row[key.strip()] = num(value)
            if row.get("year") == row.get("year"):
                by_year[int(row["year"])] = row
    return [by_year[y] for y in sorted(by_year)]


def first_year(rows, cond):
    for r in rows:
        if cond(r):
            return int(r["year"])
    return None


def at_year(rows, year):
    best = None
    for r in rows:
        if r["year"] <= year:
            best = r
    return best


def check(label, value, lo, hi, unit=""):
    if value is None:
        print(f"  [없음] {label}: 기록 없음")
        return
    ok = (lo is None or value >= lo) and (hi is None or value <= hi)
    rng = f"{'' if lo is None else lo}~{'' if hi is None else hi}"
    print(f"  [{'통과' if ok else '벗어남'}] {label}: {value}{unit} (허용 {rng}{unit})")


def ratio(rows, key, y0, y1):
    a, b = at_year(rows, y0), at_year(rows, y1)
    if not a or not b or not a.get(key):
        return None
    return round(b[key] / a[key], 2)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", type=Path)
    ap.add_argument("--csv", type=Path)
    args = ap.parse_args()

    rows = read_rows([args.log] if args.log else [LOGS / f for f in FILES])
    if not rows:
        print("TSIN_OBS 줄이 없다. 게임 규칙 '관찰 측정 기록'을 켜고 관찰 실행을 했는지 확인한다.")
        return 1
    print(f"기록된 해: {int(rows[0]['year'])}~{int(rows[-1]['year'])} ({len(rows)}줄)")

    if args.csv:
        keys = list(rows[-1].keys())
        with args.csv.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        print(f"CSV: {args.csv}")

    print("\n시기 목표")
    check("산업자본주의 발생", first_year(rows, lambda r: r.get("ic_known", 0) > 0), 1837, 1860)
    check("산업자본주의 첫 수용", first_year(rows, lambda r: r.get("ic_emb", 0) > 0), 1845, 1865)
    check("열강 절반 산업자본주의 수용",
          first_year(rows, lambda r: r.get("gp", 0) > 0 and r.get("ic_emb_gp", 0) * 2 >= r["gp"]), 1865, 1890)
    check("대중사회 발생", first_year(rows, lambda r: r.get("ms_known", 0) > 0), 1840, 1870)
    check("전기화 발생", first_year(rows, lambda r: r.get("el_known", 0) > 0), 1870, None)
    check("열강 1개국 이상 전기화 수용", first_year(rows, lambda r: r.get("el_emb_gp", 0) > 0), 1885, 1900)
    sit_ranges = {"tsin_springtime_of_nations": (1840, 1865), "tsin_long_depression": (1860, 1890)}
    for name, digit in SITUATIONS:
        active = [int(r["year"]) for r in rows if int(r.get("sit", 0)) // digit % 10 > 0]
        starts = sum(1 for i, r in enumerate(rows)
                     if int(r.get("sit", 0)) // digit % 10 > 0
                     and (i == 0 or int(rows[i - 1].get("sit", 0)) // digit % 10 == 0))
        if name in sit_ranges:
            check(f"{name} 시작", active[0] if active else None, *sit_ranges[name])
        if name == "tsin_world_exhibition":
            print(f"  [참고] {name} 개최 횟수: {starts} (5년 쿨다운 뒤 반복 개최 설계)")
        else:
            print(f"  [{'통과' if starts <= 1 else '벗어남'}] {name} 시작 횟수: {starts} (1회 이하)")

    print("\n경제·인구 목표")
    bad_steel = [int(r["year"]) for r in rows if r["year"] >= 1837 and not 0.7 <= r.get("steel", 1) <= 2.0]
    print(f"  [{'통과' if not bad_steel else '벗어남'}] 열강 수도 시장 강철 가격 비율 0.7~2.0 밖인 해: {bad_steel[:20]}")
    check("열강 수입 1837→1900 배수 (상위 10개국 대용)", ratio(rows, "gp_income", 1837, 1900), 2, 5, "배")
    pop = ratio(rows, "pop", 1837, 1900)
    check("세계 인구 1837→1900 증가율", None if pop is None else round((pop - 1) * 100), 40, 80, "%")
    r1900 = at_year(rows, 1900)
    check("1900 유럽 밖 수용국", None if not r1900 else int(r1900.get("non_eu", 0)), 3, None, "개국")

    print("\n이벤트 예산")
    per_country = [r["flavor"] / r["countries"] for r in rows if r.get("countries") and r["year"] >= 1837]
    if per_country:
        print(f"  국가당 연평균 플레이버 이벤트: {sum(per_country) / len(per_country):.2f} (플레이어 목표 4 이하, AI 포함 평균은 참고값)")

    print("\n1900년 이후 안정성 (연 증가율 5% 이하)")
    for key, label in [("pop", "세계 인구"), ("gp_income", "열강 수입"), ("gp_army", "열강 군대"),
                       ("steel", "강철 가격 비율")]:
        a, b = at_year(rows, 1900), at_year(rows, 1950)
        if not a or not b or b["year"] <= a["year"] or not a.get(key):
            print(f"  [없음] {label}: 1900~1950 기록 부족")
            continue
        years = b["year"] - a["year"]
        growth = (b[key] / a[key]) ** (1 / years) - 1 if b[key] > 0 else -1
        check(f"{label} {int(a['year'])}→{int(b['year'])} 연평균 증가율", round(growth * 100, 2), None, 5, "%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
