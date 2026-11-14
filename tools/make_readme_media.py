"""Charts and banner for README.md, written to readme_media/.

  python tools/make_readme_media.py

Counts, advances per branch, factory margins and the population target curve are read from the mod files.
Values that live inside scripts (timeline years, acceleration tiers, bill odds) are copied here with their source.
Rerun after content changes and check the numbers quoted in README.md.
"""
from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
from PIL import Image  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit  # noqa: E402
import pdx  # noqa: E402

MOD = pdx.MOD_ROOT
OUT = MOD / "readme_media"

INK = "#2b2620"
PAPER = "#f7f2e8"
GRID = "#d9cfbd"
ACCENT = "#2f6b4f"      # age VII green (thumbnail medallion)
GOLD = "#b8892b"
RED = "#a23b2a"
BLUE = "#2f5a8a"
GREY = "#8a8170"


def setup_font() -> None:
    fonts = Path("C:/Windows/Fonts")
    for name in ("malgun.ttf", "malgunbd.ttf"):
        if (fonts / name).exists():
            font_manager.fontManager.addfont(str(fonts / name))
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams.update({
        "axes.unicode_minus": False,
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "axes.edgecolor": GREY,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 11,
    })


def save(fig, name: str) -> None:
    OUT.mkdir(exist_ok=True)
    fig.savefig(OUT / name, dpi=150, bbox_inches="tight", facecolor=PAPER)
    plt.close(fig)
    print(f"wrote readme_media/{name}")


def korean_loc() -> dict[str, str]:
    out: dict[str, str] = {}
    for p in (MOD / "main_menu/localization/korean").glob("*.yml"):
        for m in re.finditer(r'^\s+([\w.\-]+):\d*\s*"(.*)"\s*$', p.read_text(encoding="utf-8-sig"), re.M):
            out[m.group(1)] = m.group(2)
    return out


def mod_keys(folder: str, prefixes=("tsin_", "age_7", "a_tsin_", "n_tsin_", "pa_tsin_", "hint_tsin_")) -> list[str]:
    keys = []
    base = MOD / folder
    for p in sorted(base.rglob("*.txt")) if base.exists() else []:
        if p.name.startswith("zzz_"):
            continue
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            if not b.local_kind and ":" not in b.key and b.key.startswith(prefixes):
                keys.append(b.key)
    return keys


def mod_event_count() -> int:
    n = 0
    for p in (MOD / "in_game/events").rglob("tsin_*.txt"):
        n += len(re.findall(r"(?m)^tsin_\w+\.\d+\s*=\s*\{", pdx.strip_comments(pdx.read_text(p))))
    return n


def map_mode_count() -> int:
    n = 0
    for p in (MOD / "in_game/gfx/map/map_modes").rglob("*.txt"):
        n += len(re.findall(r"(?m)^tsin_\w+\s*=\s*\{", pdx.strip_comments(pdx.read_text(p))))
    return n


# ---------------------------------------------------------------- banner

def banner() -> None:
    thumb = Image.open(MOD / ".metadata/thumbnail.png").convert("RGB")
    fig = plt.figure(figsize=(16, 5), dpi=100)
    fig.patch.set_facecolor("#1d2a24")
    ax_img = fig.add_axes([0, 0, 5 / 16, 1])
    ax_img.imshow(thumb)
    ax_img.axis("off")
    ax = fig.add_axes([5 / 16, 0, 11 / 16, 1])
    ax.set_facecolor("#1d2a24")
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.06, 0.70, "The Singularity is Near", fontsize=46, color="#f3e7c9", weight="bold", va="center")
    ax.text(0.06, 0.50, "특이점이 온다  ·  Europa Universalis V 제7시대 「산업」 1837–1900",
            fontsize=21, color="#d8c79d", va="center")
    ax.text(0.06, 0.32, "1836년에 끝나던 게임을 산업 혁명의 한가운데로 이어 갑니다.",
            fontsize=16, color="#c9d6cc", va="center")
    ax.text(0.06, 0.18, "증기 기관에서 별까지 — 장기 프로젝트의 첫 시대", fontsize=14, color="#9fb3a6", va="center")
    fig.savefig(OUT / "banner.png", dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("wrote readme_media/banner.png")


# ---------------------------------------------------------------- timelines

# Vanilla in_game/common/age/*.txt `year`; age VII from in_game/common/age/tsin_age_7.txt.
AGES = [
    ("전통", 1337, 1342), ("르네상스", 1342, 1437), ("대항해", 1437, 1537), ("개혁", 1537, 1637),
    ("절대주의", 1637, 1737), ("혁명", 1737, 1837),
]


def ages_timeline() -> None:
    fig, ax = plt.subplots(figsize=(13, 3.2))
    ax.grid(False)
    for i, (name, a, b) in enumerate(AGES):
        ax.barh(0, b - a, left=a, color="#cbbf9f" if i % 2 else "#bfb08c", edgecolor=PAPER, height=0.6)
        if b - a > 30:
            ax.text((a + b) / 2, 0, f"{name}\n{a}", ha="center", va="center", fontsize=10)
    ax.barh(0, 63, left=1837, color=ACCENT, edgecolor=PAPER, height=0.6)
    ax.text(1868.5, 0, "산업\n1837–1900", ha="center", va="center", fontsize=10, color="white", weight="bold")
    ax.barh(0, 60, left=1900, color=ACCENT, alpha=0.35, edgecolor=PAPER, height=0.6)
    ax.text(1930, 0, "제7시대 계속\n→ 2337", ha="center", va="center", fontsize=9, color=INK)
    ax.axvline(1836.99, color=RED, lw=2, ls="--")
    ax.annotate("바닐라 종료일\n1836.12.31", xy=(1837, 0.32), xytext=(1700, 0.62), fontsize=10, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED))
    ax.annotate("이 모드의 종료일 2337.12.31", xy=(1960, -0.32), xytext=(1843, -0.72), fontsize=10, color=ACCENT,
                arrowprops=dict(arrowstyle="->", color=ACCENT))
    ax.set_xlim(1330, 1965)
    ax.set_ylim(-0.85, 0.85)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_title("바닐라 여섯 시대 뒤에 일곱 번째 시대를 잇습니다", loc="left", fontsize=13, weight="bold")
    save(fig, "ages_timeline.png")


# (label, kind, earliest start, latest end, note). Years from in_game/common/situations, disasters and
# institution can_start/can_end (current_year and years_since_situation_start conditions).
AGE7_EVENTS = [
    ("콜레라 대유행", "재난", 1837, 1880, "1875년까지 시작 가능, 한 번에 최대 약 5년"),
    ("방어적 근대화", "상황", 1840, 1900, "1840년부터, 늦어도 1900년 종료"),
    ("대이주", "상황", 1845, 1890, "1845년부터, 최대 40년"),
    ("민족 통일", "상황", 1848, 1900, "1848년부터, 1871년 이후 성공 판정"),
    ("대불황", "상황", 1865, 1893, "1865년부터, 8~20년"),
    ("전기화 (제도)", "제도", 1870, 1900, "1870년 이후 발생, 1875년 베를린"),
    ("식민지 쟁탈전", "상황", 1870, 1900, "1870년부터, 30년"),
    ("곡물 침공", "상황", 1873, 1893, "1873년부터, 5~15년"),
]
KIND_COLOR = {"재난": RED, "상황": BLUE, "제도": ACCENT}


def age7_timeline() -> None:
    fig, ax = plt.subplots(figsize=(13, 5.2))
    rows = list(reversed(AGE7_EVENTS))
    for y, (label, kind, a, b, note) in enumerate(rows):
        c = KIND_COLOR[kind]
        ax.barh(y, b - a, left=a, color=c, alpha=0.22, height=0.62, edgecolor=c)
        ax.plot([a], [y], marker="o", color=c, ms=8)
        ax.text(b + 1, y, note, va="center", fontsize=9.5, color=GREY)
    ax.set_yticks(range(len(rows)), [f"{r[0]}  [{r[1]}]" for r in rows])
    ax.axvline(1837, color=ACCENT, lw=1.5, ls="--")
    ax.text(1837.5, -0.75, "제7시대 시작 1837", color=ACCENT, fontsize=9.5)
    ax.set_ylim(-0.9, len(rows) - 0.5)
    ax.set_xlim(1835, 1935)
    ax.set_xticks(range(1840, 1910, 10))
    ax.set_title("제7시대에 일어날 수 있는 일 (● 가장 이른 시작, 막대 = 진행 가능 기간)", loc="left",
                 fontsize=13, weight="bold")
    ax.grid(axis="y", visible=False)
    save(fig, "age7_timeline.png")


# ---------------------------------------------------------------- population governor

def target_multiplier(year: float) -> float:
    """Mirror of in_game/common/script_values/tsin_tempo_values.txt `tsin_pop_target_multiplier`."""
    if year < 1900:
        v = 1 + max(0.0, (year - 1837) * 0.6 / 63)
    elif year < 1950:
        v = 1 + 0.6 + (year - 1900) * 0.016
    elif year < 2000:
        v = 1 + 1.4 + (year - 1950) * 0.062
    else:
        v = 1 + 4.5 + (year - 2000) * 0.015
    return min(v, 7.0)


# Rough world population over 1837 (~1.1 billion): 1900 ~1.65, 1950 ~2.5, 2000 ~6.1, 2025 ~8.2 billion.
HISTORY = [(1837, 1.0), (1900, 1.5), (1950, 2.3), (2000, 5.5), (2025, 7.4)]


def population_governor() -> None:
    years = list(range(1837, 2201))
    t = [target_multiplier(y) for y in years]
    b1 = [min(v * 1.1, 7) for v in t]
    b2 = [min(v * 1.25, 7) for v in t]
    fig, ax = plt.subplots(figsize=(12, 5.6))
    ax.fill_between(years, 0, t, color=ACCENT, alpha=0.12, label="제동 없음 (목표 이하)")
    ax.fill_between(years, t, b1, color=GOLD, alpha=0.20, label="1단계 제동 (목표의 100~110%)")
    ax.fill_between(years, b1, b2, color="#c9772f", alpha=0.25, label="2단계 제동 (110~125%)")
    ax.fill_between(years, b2, 9.5, color=RED, alpha=0.12, label="3단계 제동 (125% 이상 또는 ×7 초과)")
    ax.plot(years, t, color=ACCENT, lw=2.5, label="목표 배율 (1837년 세계 인구 = 1)")
    ax.axhline(7, color=RED, lw=1.5, ls="--")
    ax.text(2195, 7.12, "절대 상한 ×7: 넘으면 무조건 3단계", ha="right", color=RED, fontsize=10)
    hx, hy = zip(*HISTORY)
    ax.plot(hx, hy, "o", color=INK, ms=6, label="실제 역사 (대략)")
    ax.set_xlim(1837, 2200)
    ax.set_ylim(0, 9.5)
    ax.set_ylabel("1837년 대비 세계 인구 배율")
    ax.set_title("세계 인구 조절기: 시대가 빨라져도 인구는 역사 곡선을 따라갑니다", loc="left", fontsize=13,
                 weight="bold")
    ax.legend(loc="lower right", fontsize=9.5, frameon=True, facecolor=PAPER, edgecolor=GRID)
    save(fig, "population_governor.png")


# ---------------------------------------------------------------- time compression

# tsin_age_7.txt modifier block + main_menu/common/static_modifiers/tsin_tempo_modifiers.txt.
AGE_BASE = {"연구 속도": 10, "건설 속도": 10, "승급 속도": 20, "생산 효율": 0}
TIERS = [
    {"연구 속도": 5, "건설 속도": 5, "승급 속도": 10, "생산 효율": 0},
    {"연구 속도": 10, "건설 속도": 10, "승급 속도": 20, "생산 효율": 3},
    {"연구 속도": 15, "건설 속도": 15, "승급 속도": 30, "생산 효율": 5},
]


def acceleration() -> None:
    labels = list(AGE_BASE)
    states = ["가속 없음", "가속 1단계\n(2점)", "가속 2단계\n(3점)", "가속 3단계\n(5점)"]
    colors = ["#cbbf9f", GOLD, "#c9772f", ACCENT]
    fig, ax = plt.subplots(figsize=(12, 5))
    w = 0.2
    for i, state in enumerate(states):
        vals = [AGE_BASE[k] + (TIERS[i - 1][k] if i else 0) for k in labels]
        xs = [j + (i - 1.5) * w for j in range(len(labels))]
        bars = ax.bar(xs, vals, width=w, color=colors[i], label=state.replace("\n", " "))
        for x, v in zip(xs, vals):
            ax.text(x, v + 0.6, f"+{v}%", ha="center", fontsize=9)
    ax.set_xticks(range(len(labels)), labels)
    ax.set_ylabel("제7시대 보정치 + 산업 가속 (%)")
    ax.set_ylim(0, 56)
    ax.legend(frameon=False, ncol=4, loc="upper left")
    ax.set_title("시간 압축: 산업화한 나라일수록 한 해에 더 많은 일이 일어납니다", loc="left", fontsize=13,
                 weight="bold")
    ax.grid(axis="x", visible=False)
    save(fig, "acceleration.png")


# ---------------------------------------------------------------- advances

BRANCHES = [
    ("tsin_00_age_of_industrialization", "뿌리 (증기 시대·제도)"),
    ("tsin_01_common_unlocks", "공통 해금"),
    ("tsin_02_building_unlocks", "건물 해금"),
    ("tsin_03_industrial_capitalism", "산업자본주의"),
    ("tsin_03a_automation_unlocks", "자동화"),
    ("tsin_04_choices", "특화 선택지"),
    ("tsin_05_mass_society", "대중사회"),
    ("tsin_06_electrification", "전기화"),
    ("tsin_07_military", "군사"),
    ("tsin_08_agricultural_revolution", "농업 혁명"),
    ("tsin_09_general", "행정·외교 일반"),
    ("tsin_10_government_religion", "정부 유형·종교"),
]


def advances() -> int:
    counts = []
    for stem, label in BRANCHES:
        p = MOD / "in_game/common/advances" / f"{stem}.txt"
        n = sum(1 for b in pdx.top_level_blocks(pdx.read_text(p)) if not b.local_kind and ":" not in b.key)
        counts.append((label, n))
    total = sum(n for _, n in counts)
    fig, ax = plt.subplots(figsize=(11, 5.4))
    labels, ns = zip(*reversed(counts))
    ax.barh(labels, ns, color=ACCENT)
    for y, n in enumerate(ns):
        ax.text(n + 0.4, y, str(n), va="center", fontsize=10)
    ax.set_xlabel("발전 수")
    ax.set_title(f"제7시대 발전 {total}개 (바닐라 제6시대 일반 발전 약 174개)", loc="left", fontsize=13,
                 weight="bold")
    ax.grid(axis="y", visible=False)
    save(fig, "advances.png")
    return total


# ---------------------------------------------------------------- legislation

def pass_probability(p: float) -> float:
    """Three successful readings before three stalls (docs/legislation.md)."""
    return sum(math.comb(2 + k, k) * p ** 3 * (1 - p) ** k for k in range(3))


def bills() -> None:
    xs = [i / 100 for i in range(5, 86)]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot([x * 100 for x in xs], [pass_probability(x) * 100 for x in xs], color=BLUE, lw=2.5)
    for p, label in [(0.35, "기본 35%"), (0.5, "50%"), (0.7, "70%")]:
        y = pass_probability(p) * 100
        ax.plot(p * 100, y, "o", color=INK)
        ax.annotate(f"{label} → 통과 {y:.0f}%", (p * 100, y), xytext=(8, -14), textcoords="offset points",
                    fontsize=10)
    ax.set_xlabel("심의 한 번의 성공 확률 (%) — 5~85%로 묶임")
    ax.set_ylabel("법안 통과 확률 (%)")
    ax.set_ylim(0, 100)
    ax.set_title("확률 입법: 3번 성공하면 통과, 3번 막히면 폐기", loc="left", fontsize=13, weight="bold")
    save(fig, "bill_pass_chance.png")


# ---------------------------------------------------------------- factory margins

def factory_margins() -> None:
    prices = audit.goods_prices()
    loc = korean_loc()
    rows = []
    for p in audit.own_files("in_game/common/building_types"):
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            if ":" in b.key:
                continue
            for group in audit.child_blocks(b.text, "unique_production_methods"):
                for pm in audit.inner_blocks(group):
                    clean = pdx.strip_comments(pm.text)
                    produced = re.search(r"\bproduced\s*=\s*(\w+)", clean)
                    output = re.search(r"\boutput\s*=\s*([\d.]+)", clean)
                    if not produced or not output or "mills_profit_margin" not in clean:
                        continue
                    cost = sum(float(q) * prices[g] for g, q in re.findall(r"(?m)^\s*(\w+)\s*=\s*([\d.]+)\s*$", clean)
                               if g in prices)
                    if cost <= 0 or produced.group(1) not in prices:
                        continue
                    ratio = float(output.group(1)) * prices[produced.group(1)] / cost
                    rows.append((f"{loc.get(b.key, b.key)} · {loc.get(pm.key, pm.key)}", ratio))
    rows.sort(key=lambda r: r[1])
    fig, ax = plt.subplots(figsize=(11, 0.26 * len(rows) + 1.6))
    ax.axvspan(1.25, 1.5, color=ACCENT, alpha=0.10)
    ax.axvline(1.35, color=ACCENT, ls="--", lw=1.2)
    ax.text(1.352, len(rows) - 0.3, "바닐라 공장 1.35", color=ACCENT, fontsize=9)
    ax.barh([r[0] for r in rows], [r[1] for r in rows], color=[GOLD if r[1] < 1.25 else BLUE for r in rows])
    ax.set_xlim(1.0, 1.6)
    ax.set_xlabel("산출 가치 ÷ 투입 비용 (기본 시장 가격)")
    ax.set_title("모드 공장의 이윤율 — 바닐라 공장(1.35)에 맞춤, 흑색화약만 일부러 낮게", loc="left", fontsize=13,
                 weight="bold")
    ax.tick_params(axis="y", labelsize=8.5)
    ax.grid(axis="y", visible=False)
    save(fig, "factory_margins.png")


# ---------------------------------------------------------------- content counts

def content_counts(advance_total: int) -> None:
    items = [
        ("발전", advance_total),
        ("이벤트", mod_event_count()),
        ("백과사전 항목", len(mod_keys("main_menu/common/game_concepts"))),
        ("결단", len([k for k in mod_keys("in_game/common/decisions") if "_debug_" not in k])),
        ("건물", len(mod_keys("in_game/common/building_types"))),
        ("유닛", len(mod_keys("in_game/common/unit_types"))),
        ("지도 모드", map_mode_count()),
        ("힌트", len(mod_keys("in_game/common/scriptable_hints"))),
        ("법", len(mod_keys("in_game/common/laws"))),
        ("의회 의제", len(mod_keys("in_game/common/parliament_agendas"))),
        ("상황", len(mod_keys("in_game/common/situations"))),
        ("재화", len(mod_keys("in_game/common/goods"))),
        ("정부 개혁", len(mod_keys("in_game/common/government_reforms"))),
        ("게임 규칙", len(mod_keys("main_menu/common/game_rules"))),
        ("계층 특권", len(mod_keys("in_game/common/estate_privileges"))),
        ("재난", len(mod_keys("in_game/common/disasters"))),
        ("내각 행동", len(mod_keys("in_game/common/cabinet_actions"))),
        ("제도", len(mod_keys("in_game/common/institution"))),
    ]
    items.sort(key=lambda r: r[1])
    fig, ax = plt.subplots(figsize=(11, 6.4))
    labels, ns = zip(*items)
    ax.barh(labels, ns, color=[ACCENT if n >= 50 else BLUE if n >= 10 else GOLD for n in ns])
    for y, n in enumerate(ns):
        ax.text(n + 1.5, y, str(n), va="center", fontsize=10)
    ax.set_xlabel("개수")
    ax.set_title("모드가 더하는 것 한눈에 보기", loc="left", fontsize=13, weight="bold")
    ax.grid(axis="y", visible=False)
    save(fig, "content_counts.png")
    for label, n in sorted(items, key=lambda r: -r[1]):
        print(f"  {label}: {n}")


def main() -> int:
    setup_font()
    OUT.mkdir(exist_ok=True)
    banner()
    ages_timeline()
    age7_timeline()
    population_governor()
    acceleration()
    total = advances()
    bills()
    factory_margins()
    content_counts(total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
