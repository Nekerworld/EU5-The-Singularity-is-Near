"""Charts and banner for README.md, written to readme_media/.

  python tools/make_readme_media.py

Common systems are shown before era content. Counts, eras, population targets and
acceleration bonuses are read from the source-aware mod layout. Calendar examples
are guarded against script changes; legislation is a fixed-probability illustration.
Use --output DIR for review without replacing the committed images.
"""
from __future__ import annotations

import math
import json
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


def content_files(folder, pattern='*.txt'):
    """Enumerate logical paths once, including era sources in a fresh checkout."""
    import fnmatch
    from era_layout import entries
    found = {p.relative_to(MOD).as_posix() for p in (MOD/folder).rglob(pattern) if p.is_file()}
    prefix=folder.rstrip('/')+'/'
    found.update(rel for rel in entries(MOD) if rel.startswith(prefix) and fnmatch.fnmatch(Path(rel).name,pattern))
    return [MOD/rel for rel in sorted(found)]


def era_rows():
    return json.loads(pdx.read_text(MOD/'data/eras.json'))['eras']


def end_year():
    text=pdx.read_text(MOD/'loading_screen/common/defines/zzz_tsin_defines.txt')
    return int(re.search(r'END_DATE\s*=\s*"?(\d{4})',text)[1])


def era7_count(folder):
    from era_layout import entries
    prefix=folder.rstrip('/')+'/'
    return sum(len([b for b in pdx.top_level_blocks(pdx.read_text(source)) if not b.local_kind and ':' not in b.key and b.key.startswith(('tsin_', 'age_7', 'a_tsin_', 'n_tsin_', 'pa_tsin_', 'hint_tsin_'))])
        for rel,(source,_,_) in entries(MOD).items() if source.is_relative_to(MOD/'era_7') and rel.startswith(prefix) and rel.endswith('.txt'))


def inventory():
    dashboard=json.loads(pdx.read_text(MOD/'ui/dashboard_registry.json'))
    ops=json.loads(pdx.read_text(MOD/'ui/operational_alerts.json'))
    from gen_company_decisions import COMPANIES
    return {
        'global': {'관리 탭':len(dashboard['tabs']),
            '공용 지표':sum(len(m.get('metrics',[])) for m in dashboard['modules']),
            '운영 경고':len(ops['rules']), '지도 모드':map_mode_count(),
            '힌트':len(mod_keys('in_game/common/scriptable_hints')),
            '백과사전':len(mod_keys('main_menu/common/game_concepts')),
            '게임 규칙':len(mod_keys('main_menu/common/game_rules')),'초기 기업 유형':len(json.loads(pdx.read_text(MOD/'data/early_companies.json'))['companies']),'기업 경제체제':5},
        'era_7': {label:era7_count(folder) for label,folder in [
            ('발전','in_game/common/advances'),('건물','in_game/common/building_types'),
            ('유닛','in_game/common/unit_types'),('법','in_game/common/laws'),
            ('상황','in_game/common/situations'),('재난','in_game/common/disasters'),
            ('재화','in_game/common/goods'),('제도','in_game/common/institution')]} | {'기업':len(COMPANIES)},
        'all_events':mod_event_count(),
        'eras':[{k:r[k] for k in ['number','id','start_year','implementation']} for r in era_rows()],
        'end_year':end_year(),
    }


def scalar(body,key,default=0):
    match=re.search(r'(?m)^\s*'+re.escape(key)+r'\s*=\s*(-?[\d.]+)\s*(?:#.*)?$',body)
    return float(match[1]) if match else default


def assignments(body):
    """Small ordered reader for the population curve's numeric subset."""
    text=pdx.strip_comments(body)
    pos=0
    while pos<len(text):
        match=re.match(r'\s*(\w+)\s*=\s*',text[pos:])
        if not match:
            if not text[pos:].strip():return
            raise ValueError('Unsupported curve syntax near '+text[pos:pos+50])
        key=match[1]; pos+=match.end()
        if text[pos]=='{':
            end=pdx.matching_brace(text,pos)
            value=text[pos+1:end];pos=end+1
        else:
            atom=re.match(r'[^\s{}]+',text[pos:]);value=atom[0];pos+=atom.end()
        yield key,value


def global_overview():
    data=inventory()['global']
    cards=[('공통 운영 화면',f"TSIN 관리 {data['관리 탭']}개 탭 · 현황 {data['운영 경고']}종\n경제 → 금융 하위 6탭 · Glorp 연결"),
        ('국가 통계',f"공용 지표 {data['공용 지표']}개 · GDP K / M / B / T\nGDP 10개 연간 관측 · 주가 8개 분기 관측"),
        ('지도와 안내',f"지도 모드 {data['지도 모드']}종 · 힌트 {data['힌트']}개\n백과사전 {data['백과사전']}개 · 한/영 현지화"),
        ('성장과 인구 조절','산업 가속 · 세계 인구 목표 곡선\n국가 성장 제동 · 인구 변천'),
        ('시대 연속성과 호환','바닐라 후반기 콘텐츠의 조건 연장\n기존 세이브 연결 · 플레이셋별 호환 패치'),
        ('후속 시대 확장','공용 UI와 통계를 다음 시대에서도 사용\nVIII 농업·함선·물류 연결 / IX–XII 뼈대')]
    fig,ax=plt.subplots(figsize=(13,6.6));ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
    for i,(title,body) in enumerate(cards):
        x=.015+(i%2)*.5;y=.69-(i//2)*.31
        ax.add_patch(FancyBboxPatch((x,y),.46,.26,boxstyle='round,pad=0.012',linewidth=1,edgecolor=GRID,facecolor='white'))
        ax.text(x+.02,y+.193,title,fontsize=16,color=ACCENT,weight='bold')
        ax.text(x+.02,y+.115,body,fontsize=12,va='top',linespacing=1.7)
    ax.set_title('전역 변경사항 · 여러 시대가 공유하는 체계',loc='left',fontsize=17,weight='bold',pad=15)
    fig.text(.10,.01,'전역은 코드의 공통 범위입니다. 실제 작동 시점은 시대·제도·국가 조건에 따라 다릅니다.',fontsize=10,color=GREY)
    save(fig,'global_overview.png')



def korean_loc() -> dict[str, str]:
    out: dict[str, str] = {}
    for p in content_files("main_menu/localization/korean", "*.yml"):
        for m in re.finditer(r'^\s+([\w.\-]+):\d*\s*"(.*)"\s*$', pdx.read_text(p), re.M):
            out[m.group(1)] = m.group(2)
    return out


def mod_keys(folder: str, prefixes=("tsin_", "age_7", "a_tsin_", "n_tsin_", "pa_tsin_", "hint_tsin_")) -> list[str]:
    keys = []
    base = MOD / folder
    for p in content_files(folder):
        if p.name.startswith("zzz_"):
            continue
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            if not b.local_kind and ":" not in b.key and b.key.startswith(prefixes):
                keys.append(b.key)
    return keys


def mod_event_count() -> int:
    n = 0
    for p in content_files("in_game/events", "tsin_*.txt"):
        n += len(re.findall(r"(?m)^tsin_\w+\.\d+\s*=\s*\{", pdx.strip_comments(pdx.read_text(p))))
    return n


def map_mode_count() -> int:
    n = 0
    for p in content_files("in_game/gfx/map/map_modes"):
        n += len(re.findall(r"(?m)^tsin_\w+\s*=\s*\{", pdx.strip_comments(pdx.read_text(p))))
    return n


# ---------------------------------------------------------------- banner

def banner():
    fig=plt.figure(figsize=(16,5),dpi=100)
    fig.patch.set_facecolor('#1d2a24')
    ax_img=fig.add_axes([0,0,0.30,1]);ax_img.imshow(Image.open(MOD/'.metadata/thumbnail.png').convert('RGB'));ax_img.axis('off')
    ax=fig.add_axes([0.30,0,0.70,1]);ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
    ax.text(.055,.76,'The Singularity is Near',fontsize=37,color='#f3e7c9',weight='bold',va='center')
    ax.text(.055,.58,'특이점이 온다 · Europa Universalis V',fontsize=22,color='#d8c79d')
    ax.text(.055,.41,'공통 운영 체계 위에 시대별 콘텐츠를 이어 갑니다',fontsize=19,color='#e0e6df')
    ax.text(.055,.25,'VII 산업: 콘텐츠  |  VIII: 부분 구현  |  IX–XII: 뼈대',fontsize=17,color='#b7ccbe')
    ax.text(.055,.12,f'종료일 {end_year()}.12.31 · 개발 빌드 / 인게임 검증 중',fontsize=14,color='#9fb3a6')
    fig.savefig(OUT/'banner.png',dpi=100,facecolor=fig.get_facecolor());plt.close(fig)
    print('wrote readme_media/banner.png')


# ---------------------------------------------------------------- timelines

# Vanilla in_game/common/age/*.txt `year`; age VII from in_game/common/age/tsin_age_7.txt.


def ages_timeline():
    rows=era_rows()
    fig,ax=plt.subplots(figsize=(13,5.9));ax.axis('off');ax.set_xlim(0,1);ax.set_ylim(0,1)
    for i,row in enumerate(rows):
        x=.015+(i%3)*.335;y=.53-(i//3)*.43
        active=row['implementation']=='content';color=ACCENT if active else BLUE
        ax.add_patch(FancyBboxPatch((x,y),.30,.33,boxstyle='round,pad=.012',edgecolor=color,facecolor='#e6eee7' if active else '#e9eef4'))
        ending=rows[i+1]['start_year'] if i+1<len(rows) else end_year()
        ax.text(x+.015,y+.245,f"{row['number']:02d}  {row['name']['korean']}",fontsize=19,weight='bold',color=color)
        ax.text(x+.015,y+.16,f"{row['start_year']}–{ending}",fontsize=17)
        ax.text(x+.015,y+.07,'콘텐츠 구현 · 검증 중' if active else ('농업·군사·물류 부분 구현' if row['implementation']=='partial' else '시대 뼈대만 등록'),fontsize=12,color=color)
    fig.text(.10,.97,'각 시대별 변경사항 · 7시대 콘텐츠 / 8시대 부분 구현 / 9–12시대 뼈대',fontsize=16,weight='bold')
    fig.text(.10,.92,f'바닐라 I–VI 뒤에 연결 · 모드 종료일 {end_year()}.12.31',fontsize=12,color=GREY)
    fig.text(.10,.035,'등록된 시작 연도 기준 · 칸 너비는 기간과 무관 · 2200년은 장기 목표이며 종료일이 아닙니다.',fontsize=10,color=GREY)
    save(fig,'ages_timeline.png')


# Selected year gates are checked against situation, disaster and institution definitions.
# Dots indicate calendar thresholds, not guaranteed spawn or end dates.
KIND_COLOR = {"재난": RED, "상황": BLUE, "제도": ACCENT}


def age7_timeline():
    rows=[('콜레라 대유행','재난',1837,'1875년까지 시작 가능 · 과밀/위생 조건'),
        ('방어적 근대화','상황',1840,'개항 압력 등 추가 조건'),
        ('대이주','상황',1845,'과밀·기근 등 이주 압력 조건'),
        ('민족 통일','상황',1848,'문화권·통일 운동 조건'),
        ('대불황','상황',1865,'금융 충격이 있으면 1850년부터'),
        ('전기화','제도',1870,'역사적 규칙의 베를린 발생은 1875년부터'),
        ('식민지 쟁탈전','상황',1870,'열강 수 등 추가 조건'),
        ('곡물 침공','상황',1873,'증기 상선 기술의 보급 조건')]
    # Guard the displayed year gates against script changes.
    paths=['common/disasters/tsin_cholera.txt','common/situations/tsin_defensive_modernization.txt',
        'common/situations/tsin_great_migration.txt','common/situations/tsin_national_unification.txt',
        'common/situations/tsin_long_depression.txt','common/institution/tsin_age_7_institutions.txt',
        'common/situations/tsin_scramble_for_colonies.txt','common/situations/tsin_grain_invasion.txt']
    for row,rel in zip(rows,paths):
        code=pdx.strip_comments(pdx.read_text(MOD/'in_game'/rel))
        assert str(row[2] if row[2]!=1837 else 1830) in code,(rel,'year gate changed')
    fig,ax=plt.subplots(figsize=(13,5.5))
    for y,(label,kind,year,note) in enumerate(reversed(rows)):
        ax.plot([1837,1900],[y,y],color=GRID,lw=1)
        ax.plot(year,y,'o',color=KIND_COLOR[kind],ms=9)
        ax.text(1903,y,note,fontsize=10,va='center',color=GREY)
        if label=='대불황':
            ax.plot(1850,y,'o',mfc=PAPER,mec=BLUE,ms=8)
    ax.set_yticks(range(len(rows)),[f'{r[0]} [{r[1]}]' for r in reversed(rows)])
    ax.set_xlim(1833,1942);ax.set_ylim(-.7,len(rows)-.4);ax.set_xticks([1840,1860,1880,1900]);ax.grid(axis='y',visible=False)
    ax.set_title('제7시대 · 일부 상황과 제도의 연도 문턱',loc='left',fontsize=15,weight='bold')
    fig.text(.12,.005,'점은 연도 조건의 문턱입니다. 발생 보장·종료 연도·지속 기간을 뜻하지 않습니다. 대불황의 빈 점은 조건부 조기 시작입니다.',fontsize=10,color=GREY)
    save(fig,'age7_timeline.png')


# ---------------------------------------------------------------- population governor

def target_multiplier(year):
    text=pdx.read_text(MOD/'in_game/common/script_values/tsin_tempo_values.txt')
    block=next(b.text for b in pdx.top_level_blocks(text) if b.key=='tsin_pop_target_multiplier')
    cap=scalar(text,'tsin_pop_absolute_cap_multiplier')
    def resolve(value):
        if value=='current_year':return year
        if value=='tsin_pop_absolute_cap_multiplier':return cap
        if re.fullmatch(r'-?[\d.]+',value):return float(value)
        return evaluate(value)
    def evaluate(body,initial=0):
        result=initial; chosen=False
        for key,value in assignments(body):
            if key in ('if','else_if','else'):
                children=list(assignments(value))
                limits=[v for k,v in children if k=='limit']
                allowed=not limits or year<int(re.fullmatch(r'\s*current_year\s*<\s*(\d+)\s*',limits[0])[1])
                if not chosen and allowed:
                    result=evaluate(value,result);chosen=True
            elif key=='limit':continue
            elif key=='value':result=resolve(value)
            elif key=='add':result+=resolve(value)
            elif key=='subtract':result-=resolve(value)
            elif key=='multiply':result*=resolve(value)
            elif key=='divide':result/=resolve(value)
            elif key=='min':result=max(result,resolve(value))
            elif key=='max':result=min(result,resolve(value))
            else:raise ValueError('Unsupported curve operator '+key)
        return result
    return evaluate(block[block.index('{')+1:-1])





def population_governor():
    years=list(range(1837,end_year()+1));t=[target_multiplier(y) for y in years]
    code=pdx.read_text(MOD/'in_game/common/script_values/tsin_tempo_values.txt');cap=scalar(code,'tsin_pop_absolute_cap_multiplier')
    assert all(abs(target_multiplier(y)-v)<1e-8 for y,v in [(1837,1),(1900,1.6),(1950,2.4),(2000,5.5),(2100,7)])
    b1=[min(v*1.1,cap) for v in t];b2=[min(v*1.25,cap) for v in t]
    fig,ax=plt.subplots(figsize=(12,5.8))
    for low,high,color,label in [(0,t,ACCENT,'목표 미만: 제동 없음'),(t,b1,GOLD,'목표의 100–110%: 1단계'),(b1,b2,'#c9772f','110–125%: 2단계'),(b2,9,RED,'125% 이상 또는 절대 상한: 3단계')]:
        ax.fill_between(years,low,high,color=color,alpha=.14,label=label)
    ax.plot(years,t,color=ACCENT,lw=2.5,label='스크립트의 목표 배율');ax.axhline(cap,color=RED,ls='--',lw=1.2)
    ax.text(end_year()-5,cap+.16,f'절대 상한 ×{cap:g} 이상이면 3단계',ha='right',color=RED,fontsize=10)
    ax.set_xlim(1837,end_year());ax.set_ylim(0,9);ax.set_ylabel('1837년 기준 세계 인구 배율')
    ax.set_title('전역 성장 조절 · 세계 인구 목표 곡선 (7시대 이후 작동)',loc='left',fontsize=14,weight='bold')
    ax.legend(loc='lower right',fontsize=9.5,facecolor=PAPER,edgecolor=GRID)
    fig.text(.10,.005,'실제 인구 예측이 아닌 게임 규칙입니다. 1·2단계는 빠르게 성장하는 국가에, 3단계는 전체 국가에 적용합니다.',fontsize=10,color=GREY)
    save(fig,'population_governor.png')


# ---------------------------------------------------------------- time compression

# tsin_age_7.txt modifier block + main_menu/common/static_modifiers/tsin_tempo_modifiers.txt.


def acceleration():
    keys={'연구 속도':'research_speed_modifier','건설 속도':'global_construction_speed','승급 속도':'global_pop_promotion_speed_modifier','생산 효율':'global_production_efficiency'}
    base=pdx.read_text(MOD/'in_game/common/age/tsin_age_7.txt')
    mods={b.key:b.text for b in pdx.top_level_blocks(pdx.read_text(MOD/'main_menu/common/static_modifiers/tsin_tempo_modifiers.txt'))}
    states=['가속 없음','1단계 · 2점','2단계 · 3점','3단계 · 5점']
    fig,ax=plt.subplots(figsize=(12,5));w=.2
    for i,(state,color) in enumerate(zip(states,['#cbbf9f',GOLD,'#c9772f',ACCENT])):
        values=[100*(scalar(base,key)+(scalar(mods[f'tsin_industrial_acceleration_{i}'],key) if i else 0)) for key in keys.values()]
        xs=[j+(i-1.5)*w for j in range(len(keys))];ax.bar(xs,values,width=w,color=color,label=state)
        for x,v in zip(xs,values):ax.text(x,v+.6,f'+{v:g}%',ha='center',fontsize=9)
    ax.set_xticks(range(len(keys)),list(keys));ax.set_ylim(0,57);ax.set_ylabel('제7시대 기본 보정 + 산업 가속 (%)')
    ax.legend(frameon=False,ncol=4,loc='upper left');ax.grid(axis='x',visible=False)
    ax.set_title('공통 가속 체계 · 제7시대에서의 보정 합계',loc='left',fontsize=14,weight='bold');save(fig,'acceleration.png')


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
    ax.set_title(f"제7시대 발전 {total}개 · 파일별 분포", loc="left", fontsize=13,
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
    ax.set_title("제7시대 입법 · 성공 3번과 정체 3번 중 무엇이 먼저인가", loc="left", fontsize=13, weight="bold")
    fig.subplots_adjust(bottom=.20)
    fig.text(.10,.005,"각 심의의 성공 확률이 고정된 이론값입니다. 실제 플레이에서는 계층·논쟁·정책에 따라 확률이 달라집니다.",fontsize=10,color=GREY)
    save(fig, "bill_pass_chance.png")


# ---------------------------------------------------------------- factory margins

def factory_margins() -> None:
    prices = audit.goods_prices()
    for p in content_files('in_game/common/goods'):
        for b in pdx.top_level_blocks(pdx.read_text(p)):
            value=scalar(b.text,'default_market_price',None)
            if value is not None:prices[b.key]=value
    loc = korean_loc()
    rows = []
    for p in content_files("in_game/common/building_types"):
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
    ax.set_title("제7시대 생산 방식 · 기본 가격에서의 산출 / 투입재 비율", loc="left", fontsize=13,
                 weight="bold")
    ax.tick_params(axis="y", labelsize=8.5)
    ax.grid(axis="y", visible=False)
    fig.text(.10,.005,"투입재와 산출물의 기준 가격만 비교합니다. 임금·건물 유지비·실제 시장 가격을 포함한 순이익이 아닙니다.",fontsize=9,color=GREY)
    save(fig, "factory_margins.png")


# ---------------------------------------------------------------- content counts

def content_counts(advance_total):
    data=inventory();assert data['era_7']['발전']==advance_total
    fig,axes=plt.subplots(1,2,figsize=(13,6.2))
    for ax,(scope,title,color) in zip(axes,[('global','전역 · 공통 체계',BLUE),('era_7','제7시대 · 콘텐츠',ACCENT)]):
        rows=sorted(data[scope].items(),key=lambda r:r[1]);labels,counts=zip(*rows)
        ax.barh(labels,counts,color=color,height=.64)
        for y,n in enumerate(counts):ax.text(n+max(counts)*.018,y,str(n),va='center',fontsize=10)
        ax.set_xlim(0,max(counts)*1.16);ax.set_xlabel('정의 수');ax.set_title(title,loc='left',fontsize=16,weight='bold');ax.grid(axis='y',visible=False)
    fig.subplots_adjust(wspace=.42,bottom=.16)
    fig.text(.10,.005,'서로 다른 종류의 정의를 셉니다. 양쪽 가로축 눈금은 독립적이며, 이벤트와 호환 패치의 수는 포함하지 않습니다.',fontsize=10,color=GREY)
    save(fig,'content_counts.png')
    (OUT/'content_inventory.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(data,ensure_ascii=False))


def main():
    import argparse
    global OUT
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.output:OUT=args.output.resolve()
    setup_font();OUT.mkdir(parents=True,exist_ok=True)
    banner();global_overview();population_governor();acceleration();ages_timeline()
    total=advances();bills();factory_margins();age7_timeline();content_counts(total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
