"""Turn TSIN_ECON log lines (game rule tsin_economy_log = on) into CSV, a ranking and an HTML chart page.

Usage: python tools/econ_report.py [--log PATH] [--csv OUT.csv] [--html OUT.html] [--year YEAR] [--top N]
  --log   read this file instead of the game's debug.log/game.log/error.log
  --csv   write every (country, year) row as CSV
  --html  write a self-contained HTML page with time series (GDP, GDP per capita, stock index) and a ranking
  --year  ranking year (default: last logged year)
  --top   countries in the ranking and charts (default 10, by GDP in the ranking year)

docs/economic_statistics.md describes the estimate and the line format.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from observer_report import FILES, LOGS, num  # noqa: E402

LINE = re.compile(r"TSIN_ECON;(.*)")
KEYS = ["gdp", "gdp_pc", "growth", "pop", "index", "grievance", "sec", "high", "fac", "lit"]
CHARTS = [("gdp", "추정 GDP"), ("gdp_pc", "1인당 GDP"), ("index", "주가 종합지수"), ("sec", "중등교육률")]


def read_rows(paths: list[Path]) -> list[dict]:
    """One row per (country, year); a later line for the same pair replaces an earlier one (snapshots)."""
    rows: dict[tuple[str, int], dict] = {}
    for path in paths:
        if not path.exists():
            continue
        for ln in path.read_text(encoding="utf-8", errors="replace").splitlines():
            m = LINE.search(ln)
            if not m:
                continue
            row: dict = {}
            for part in m.group(1).split(";"):
                if "=" not in part:
                    continue
                key, value = part.split("=", 1)
                key = key.strip()
                row[key] = value.strip() if key == "name" else num(value)
            if "name" not in row or row.get("year") != row.get("year"):
                continue
            row["year"] = int(row["year"])
            rows[(row["name"], row["year"])] = row
    return sorted(rows.values(), key=lambda r: (r["year"], r["name"]))


def ranking(rows: list[dict], year: int, top: int) -> list[dict]:
    at = [r for r in rows if r["year"] == year]
    return sorted(at, key=lambda r: -r.get("gdp", 0))[:top]


def write_csv(rows: list[dict], out: Path) -> None:
    with out.open("w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=["name", "year"] + KEYS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def write_html(rows: list[dict], names: list[str], ranked: list[dict], year: int, out: Path) -> None:
    years = sorted({r["year"] for r in rows})
    series = {}
    for key, _ in CHARTS:
        series[key] = {n: [next((r.get(key) for r in rows if r["name"] == n and r["year"] == y), None)
                           for y in years] for n in names}
    data = json.dumps({"years": years, "series": series, "charts": CHARTS}, ensure_ascii=False)
    table = "".join(
        f"<tr><td>{i}</td><td>{html.escape(r['name'])}</td><td>{r.get('gdp', 0):,.0f}</td>"
        f"<td>{r.get('gdp_pc', 0):.3f}</td><td>{r.get('growth', 0):.2f}%</td><td>{r.get('index', 0):.1f}</td>"
        f"<td>{r.get('sec', 0):.1f}</td><td>{r.get('high', 0):.1f}</td><td>{r.get('fac', 0):.3f}</td></tr>"
        for i, r in enumerate(ranked, 1))
    page = f"""<!doctype html><html lang="ko"><meta charset="utf-8"><title>TSIN 경제 보고서</title>
<style>body{{font-family:sans-serif;margin:24px;background:#fafafa}}canvas{{background:#fff;border:1px solid #ccc;margin:8px 0}}
table{{border-collapse:collapse}}td,th{{border:1px solid #ccc;padding:4px 8px;text-align:right}}td:nth-child(2){{text-align:left}}</style>
<h1>TSIN 경제 보고서</h1><p>{years[0]}~{years[-1]}년, 상위 {len(names)}개국 (순위 기준 {year}년 추정 GDP)</p>
<h2>{year}년 순위</h2><table><tr><th>#</th><th>나라</th><th>GDP</th><th>1인당</th><th>성장률</th><th>지수</th>
<th>중등</th><th>고등</th><th>공장 비중</th></tr>{table}</table><div id="charts"></div>
<script>const D={data};const C=["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"];
for(const [key,label] of D.charts){{const h=document.createElement("h2");h.textContent=label;charts.appendChild(h);
const cv=document.createElement("canvas");cv.width=900;cv.height=320;charts.appendChild(cv);const g=cv.getContext("2d");
const all=Object.values(D.series[key]).flat().filter(v=>v!=null);const mx=Math.max(1e-9,...all);const n=D.years.length;
const X=i=>50+i*(830/Math.max(1,n-1)),Y=v=>300-v/mx*280;g.fillText(mx.toFixed(2),4,24);g.fillText(D.years[0],46,316);
g.fillText(D.years[n-1],850,316);let k=0;for(const [name,vals] of Object.entries(D.series[key])){{g.strokeStyle=C[k%C.length];
g.beginPath();let on=false;vals.forEach((v,i)=>{{if(v==null){{on=false;return}}on?g.lineTo(X(i),Y(v)):g.moveTo(X(i),Y(v));on=true}});
g.stroke();g.fillStyle=C[k%C.length];g.fillText(name,60+(k%5)*170,12+Math.floor(k/5)*12);k++}}}}</script></html>"""
    out.write_text(page, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", type=Path)
    ap.add_argument("--csv", type=Path)
    ap.add_argument("--html", type=Path)
    ap.add_argument("--year", type=int)
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()

    rows = read_rows([args.log] if args.log else [LOGS / f for f in FILES])
    if not rows:
        print("TSIN_ECON 줄이 없다. 게임 규칙 '경제 통계 기록'을 켜고 한 해 이상 진행했는지 확인한다.")
        return 1
    years = sorted({r["year"] for r in rows})
    year = args.year if args.year in years else years[-1]
    ranked = ranking(rows, year, args.top)
    print(f"기록: {years[0]}~{years[-1]}년, {len({r['name'] for r in rows})}개국, {len(rows)}줄")
    print(f"\n{year}년 추정 GDP 순위")
    for i, r in enumerate(ranked, 1):
        print(f"  {i:2}. {r['name']}: GDP {r.get('gdp', 0):,.0f}, 1인당 {r.get('gdp_pc', 0):.3f}, "
              f"성장 {r.get('growth', 0):.2f}%, 지수 {r.get('index', 0):.1f}")
    pcs = sorted(r.get("gdp_pc", 0) for r in rows if r["year"] == year and r.get("gdp_pc", 0) > 0)
    if len(pcs) >= 2:
        print(f"\n{year}년 1인당 GDP 최고/최저 배율(기록된 {len(pcs)}개국): {pcs[-1] / pcs[0]:.2f}배 "
              f"(docs/balance_targets.md: 1900년 산업국/농업국 3~5배)")
    if args.csv:
        write_csv(rows, args.csv)
        print(f"CSV: {args.csv}")
    if args.html:
        write_html(rows, [r["name"] for r in ranked], ranked, year, args.html)
        print(f"HTML: {args.html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
