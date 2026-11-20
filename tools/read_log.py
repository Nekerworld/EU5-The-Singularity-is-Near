"""Read the always-on TSIN mod log and print a short report (docs/mod_log.md).

Usage: python tools/read_log.py [--logs DIR] [--debug FILE] [--error FILE] [--out FILE] [--rows N] [--all]
  --logs   folder with debug.log / error.log / game.log (default: the game's logs folder)
  --debug  read this debug.log instead (e.g. a copy the user sends)
  --error  read this error.log instead
  --out    also write the report to this file (default tools/out/mod_log_report.md)
  --rows   how many snapshot rows to print (default 24; --all prints every row)

The report has: a verdict line, a format probe (did the numbers survive debug_log?), PASS/WARN/FAIL checks,
hook counts (which features the player actually used), the snapshot series, and this mod's script errors.
CHECKS / HOOKS / rules come from tools/gen_mod_log.py, so the reader always matches what the game writes.
"""
import argparse
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_mod_log as spec

LOGS = Path.home() / "Documents" / "Paradox Interactive" / "Europa Universalis V" / "logs"
OUT = Path(__file__).resolve().parent / "out" / "mod_log_report.md"
HEAD = re.compile(r"^\[(\d\d:\d\d:\d\d)\]\[([^\]]+)\]: (.*)$")
MOD = re.compile(r"tsin_|TSIN|zzz_tsin|age_7_industrialization", re.I)
CHECK_KO = {c[0]: c[1] for c in spec.CHECKS}
HOOK_KO = dict(spec.HOOKS)


def read_lines(path):
    if not path or not Path(path).exists():
        return None
    return Path(path).read_text(encoding="utf-8", errors="replace").splitlines()


def fields(payload):
    out = OrderedDict()
    for part in payload.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k] = v
    return out


def parse_debug(lines):
    """Events in file order: ('hb'|'chk'|'hook'|'snap'|'fmt', time, fields). Plus loc errors and other mod debug_log lines."""
    events, loc_errors, failed, other = [], [], [], []
    for ln in lines:
        m = HEAD.match(ln)
        if not m:
            continue
        t, src, msg = m.groups()
        if "FetchData failed for" in msg:
            failed.append(msg.split("for", 1)[1].strip().strip("'"))
            continue
        if "Data error in loc string" in msg:
            key = re.search(r"'([^']+)'", msg)
            loc_errors.append((t, key.group(1) if key else "?", list(failed)))
            failed = []
            continue
        if "Promote '" in msg:
            continue
        if f"{spec.PREFIX};" in msg:
            f = fields(msg.split(f"{spec.PREFIX};", 1)[1])
            events.append((f.get("k", "?"), t, f))
        elif "jomini_effect_impl.cpp:479" in src and MOD.search(msg):
            other.append((t, msg))
    return events, loc_errors, other


def parse_errors(lines):
    """Blocks of 'Script system error!' / other multi-line errors, kept when they mention this mod."""
    blocks, cur = [], None
    for ln in lines:
        m = HEAD.match(ln)
        if m:
            if cur:
                blocks.append(cur)
            cur = {"time": m.group(1), "src": m.group(2), "head": m.group(3), "body": []}
        elif cur is not None and ln.strip():
            cur["body"].append(ln.strip())
    if cur:
        blocks.append(cur)
    return blocks


def classify(text):
    low = text.lower()
    if "not being set" in low or "unset scope" in low or "invalid left side" in low:
        return "미설정 변수 읽기"
    if "localization" in low or "loc string" in low or "missing loc" in low:
        return "현지화"
    if "unexpected token" in low or "parse" in low or "unknown" in low:
        return "문법·알 수 없는 이름"
    return "기타"


def heartbeats(events):
    """Group events into heartbeats: each starts at k=hb and owns the chk/snap/fmt lines until the next hb."""
    beats, hooks, cur = [], [], None
    for kind, t, f in events:
        if kind == "hb":
            cur = {"time": t, "chk": {}, "snap": None, "fmt": None, "hooks_before": len(hooks)}
            beats.append(cur)
        elif kind == "chk" and cur is not None:
            cur["chk"][f.get("id")] = f.get("v") == "1"
        elif kind == "snap" and cur is not None:
            cur["snap"] = f
        elif kind == "fmt" and cur is not None:
            cur["fmt"] = f
        elif kind == "hook":
            hooks.append((t, f.get("id"), len(beats)))
    return beats, hooks


def verdicts(beats, hooks, loc_errors):
    res = []  # (level, title, detail)

    def add(level, title, detail=""):
        res.append((level, title, detail))

    if not beats:
        add("FAIL", "모드 로그가 한 줄도 없음",
            "플레이어 월간 펄스(tsin_log_monthly_pulse)가 한 번도 돌지 않았다. 게임에서 최소 한 달을 진행했는지, 모드가 활성인지, "
            "플레이어가 AI가 아닌 나라인지(is_ai = no) 확인한다. 옵서버 모드라면 이 로그는 비어 있는 것이 정상일 수 있다.")
        return res
    # 1) implications
    for a, b, why in spec.IMPLIES:
        bad = [i for i, bt in enumerate(beats) if bt["chk"].get(a) and bt["chk"].get(b) is False]
        if bad:
            add("FAIL", f"{CHECK_KO.get(a, a)} → {CHECK_KO.get(b, b)} 불일치", f"{len(bad)}회/{len(beats)}회 점검. {why}.")
        else:
            seen = any(bt["chk"].get(a) for bt in beats)
            add("PASS" if seen else "미검증", f"{CHECK_KO.get(a, a)} → {CHECK_KO.get(b, b)}",
                "" if seen else f"'{CHECK_KO.get(a, a)}' 상태가 한 번도 참이 아니어서 조건을 검증하지 못했다.")
    # 2) hook then expected state
    for hid, (cid, want) in spec.HOOK_EXPECT.items():
        fired = [h for h in hooks if h[1] == hid]
        if not fired:
            add("미검증", f"{HOOK_KO[hid]}", "플레이 중 실행되지 않음 — 기능을 한 번 눌러 보면 검증된다.")
            continue
        outcomes = []
        for t, _id, nbeats in fired:
            nxt = next((bt for bt in beats[nbeats:] if cid in bt["chk"]), None)
            outcomes.append(None if nxt is None else (nxt["chk"][cid] == bool(want)))
        if any(o is False for o in outcomes):
            add("FAIL", f"{HOOK_KO[hid]} 뒤 '{CHECK_KO[cid]}' 거짓", f"{outcomes.count(False)}회 어긋남(총 {len(fired)}회 실행).")
        elif all(o is None for o in outcomes):
            add("미검증", f"{HOOK_KO[hid]} ({len(fired)}회)", "다음 월간 점검이 아직 없어 결과를 확인하지 못했다. 한 달 더 진행한다.")
        else:
            add("PASS", f"{HOOK_KO[hid]} ({len(fired)}회)", f"직후 점검에서 '{CHECK_KO[cid]}' 확인됨.")
    # 3) hooks that must never fire
    for hid in spec.SHOULD_NOT_FIRE:
        n = sum(1 for h in hooks if h[1] == hid)
        if n:
            add("FAIL", HOOK_KO[hid], f"{n}회 발생. 버튼 allow 조건과 효과 내부 조건이 어긋난다.")
    # 4) GDP ledger should appear within a year of age 7
    tail = 0
    for bt in beats:
        tail = tail + 1 if bt["chk"].get("age7") and bt["chk"].get("gdp_ledger") is False else 0
    if tail >= 13:
        add("WARN", "제7시대인데 GDP 장부가 1년 넘게 없음", f"연속 {tail}회 점검에서 tsin_gdp 없음. 연간 집계(tsin_annual_country_aggregate_effect)가 도는지 확인.")
    # 5) loc interpolation
    mine = [e for e in loc_errors if e[1].startswith("tsin_log_")]
    if mine:
        keys = Counter(e[1] for e in mine)
        failed = sorted({x for e in mine for x in e[2]})
        add("WARN", "로그 문구의 값 읽기 실패",
            "; ".join(f"{k} x{n}" for k, n in keys.items()) + ". 실패한 식: " + (", ".join(failed[:8]) or "(기록 없음)"))
    # 6) pure information
    for cid, ko in CHECK_KO.items():
        vals = [bt["chk"].get(cid) for bt in beats if cid in bt["chk"]]
        if vals and not any(vals) and cid not in {a for a, _b, _w in spec.IMPLIES} and not cid.startswith("rule_"):
            add("정보", f"'{ko}' 한 번도 참이 아님", "기능이 아직 열리지 않았거나(정상), 조건이 어긋난 것. 해당 기능을 켠 상태에서 다시 확인.")
    return res


def fmt_probe(beats):
    lines = []
    last = next((bt["fmt"] for bt in reversed(beats) if bt["fmt"]), None)
    if last is None:
        return ["format probe 줄 없음"], None
    names = [("global", "[GetGlobalVariable(...)] — 스냅샷이 쓰는 방식"), ("global_name", "[GetGlobalVariable(...).GetCountry.Name]"),
             ("root", "[ROOT.ScriptValue(...)] — 기존 TSIN_ECON/TSIN_OBS 방식"), ("this", "[THIS.ScriptValue(...)]"),
             ("scope", "[SCOPE.ScriptValue(...)]"), ("player", "[GetPlayer.MakeScope.GetVariable(...)]")]
    ok = {}
    for key, label in names:
        v = last.get(key, "")
        ok[key] = bool(v.strip())
        lines.append(f"| {label} | {'작동' if ok[key] else '비어 있음(실패)'} | {v or '-'} |")
    return lines, ok


def snap_rows(beats, limit):
    rows = [(bt["time"], bt["snap"]) for bt in beats if bt["snap"]]
    if not rows:
        return ["(스냅샷 줄 없음)"]
    keys = [m[0] for m in spec.METRICS]
    out = ["| 실시간 | 게임 날짜 | 나라 | " + " | ".join(m[1] for m in spec.METRICS) + " |",
           "|---|---|---|" + "---|" * len(spec.METRICS)]
    chosen = rows if limit is None or len(rows) <= limit else rows[: limit // 2] + [None] + rows[-(limit - limit // 2):]
    for r in chosen:
        if r is None:
            out.append("| … | … | … |" + " … |" * len(keys))
            continue
        t, s = r
        out.append(f"| {t} | {s.get('date', '') or '?'} | {s.get('country', '') or '?'} | " + " | ".join(s.get(k, "") or "?" for k in keys) + " |")
    return out


def timeline(beats):
    """When did each check change value (first value, then every flip)."""
    out = []
    for cid, ko, _t in spec.CHECKS:
        seq = [(i, bt["chk"][cid], (bt["snap"] or {}).get("date", "")) for i, bt in enumerate(beats) if cid in bt["chk"]]
        if not seq:
            continue
        parts = [f"{'켜짐' if seq[0][1] else '꺼짐'}({seq[0][2] or '#%d' % (seq[0][0] + 1)})"]
        for prev, cur in zip(seq, seq[1:]):
            if prev[1] != cur[1]:
                parts.append(f"{'켜짐' if cur[1] else '꺼짐'}({cur[2] or '#%d' % (cur[0] + 1)})")
        out.append(f"| {ko} | {' → '.join(parts)} | {'참' if seq[-1][1] else '거짓'} |")
    return out


def error_report(blocks):
    mine, others = [], 0
    for b in blocks:
        text = " ".join([b["head"]] + b["body"])
        if MOD.search(text):
            err = next((x for x in b["body"] if x.startswith("Error:")), b["head"])
            loc = next((x for x in b["body"] if x.startswith("Script location:")), "")
            mine.append((err, loc.replace("Script location:", "").strip(), b["time"]))
        else:
            others += 1
    cnt = Counter((e, l) for e, l, _t in mine)
    first = {}
    for e, l, t in mine:
        first.setdefault((e, l), t)
    return cnt, first, others


def build_report(args):
    dlines = read_lines(args.debug or LOGS / "debug.log")
    elines = read_lines(args.error or LOGS / "error.log")
    out = []
    w = out.append
    w("# TSIN 모드 로그 보고서\n")
    if dlines is None:
        w("debug.log 를 찾지 못했다. `--logs` 또는 `--debug` 로 경로를 지정한다.")
        return "\n".join(out) + "\n"
    events, loc_errors, other = parse_debug(dlines)
    beats, hooks = heartbeats(events)
    res = verdicts(beats, hooks, loc_errors)
    levels = Counter(r[0] for r in res)
    blocks = parse_errors(elines) if elines else []
    ecnt, efirst, eothers = error_report(blocks)
    w(f"- debug.log {len(dlines)}줄, TSIN_LOG {len(events)}줄(월간 점검 {len(beats)}회, 훅 {len(hooks)}회)")
    w(f"- 판정: FAIL {levels['FAIL']} · WARN {levels['WARN']} · PASS {levels['PASS']} · 미검증 {levels['미검증']} · 정보 {levels['정보']}")
    w(f"- error.log: 이 모드 관련 {sum(ecnt.values())}건(종류 {len(ecnt)}), 무관 {eothers}건\n")
    w("## 1. 판정\n")
    order = {"FAIL": 0, "WARN": 1, "PASS": 2, "미검증": 3, "정보": 4}
    for lvl, title, detail in sorted(res, key=lambda r: order[r[0]]):
        w(f"- **{lvl}** {title}" + (f" — {detail}" if detail else ""))
    if not res:
        w("- (판정할 내용 없음)")
    w("\n## 2. 로그 문구 형식 점검 (숫자가 로그에 찍히는가)\n")
    w("| 방식 | 결과 | 값 |\n|---|---|---|")
    rows, ok = fmt_probe(beats)
    out.extend(rows)
    if ok is not None:
        if ok.get("global"):
            w("\n전역 변수 방식이 작동한다. 스냅샷 숫자를 그대로 믿어도 된다.")
        else:
            alt = [k for k in ("root", "this", "scope", "player") if ok.get(k)]
            w("\n**전역 변수 방식이 실패했다.** 숫자 칸은 비어 있다." + (f" 대신 작동한 방식: {', '.join(alt)} → 이 방식으로 스냅샷 문구를 바꿔야 한다." if alt else " 다른 방식도 모두 실패 — 점검 줄(PASS/FAIL)과 훅 줄만 신뢰한다."))
    w("\n## 3. 사용한 기능 (훅)\n")
    hc = Counter(h[1] for h in hooks)
    w("| 훅 | 설명 | 횟수 | 마지막 실시간 |\n|---|---|---|---|")
    for hid, ko in spec.HOOKS:
        last = max((h[0] for h in hooks if h[1] == hid), default="-")
        w(f"| {hid} | {ko} | {hc.get(hid, 0)} | {last} |")
    w("\n## 4. 점검 항목의 변화\n")
    w("| 점검 | 변화 | 마지막 |\n|---|---|---|")
    out.extend(timeline(beats))
    w("\n## 5. 스냅샷\n")
    out.extend(snap_rows(beats, None if args.all else args.rows))
    w("\n## 6. 이 모드의 다른 debug_log 줄\n")
    if other:
        kinds = Counter(re.sub(r"^\S+:\d+:\s*", "", m)[:60] for _t, m in other)
        for text, n in kinds.most_common(12):
            empty = ";" in text and re.search(r"=;", text)
            w(f"- {n}회: `{text}`" + (" — **값이 비어 있다(옛 ROOT 방식)**" if empty else ""))
        empties = [m for _t, m in other if re.search(r"=(;|$)", m)]
        if empties:
            w(f"\n값이 빈 줄 {len(empties)}건. TSIN_OBS/TSIN_ECON 은 아직 옛 방식이라 비어 있는 것이 정상이다.")
    else:
        w("- 없음")
    w("\n## 7. error.log (이 모드 관련)\n")
    if elines is None:
        w("- error.log 없음")
    elif not ecnt:
        w("- 이 모드와 관련된 오류가 없다.")
    else:
        w("| 횟수 | 분류 | 오류 | 위치 | 처음 |\n|---|---|---|---|---|")
        for (e, l), n in ecnt.most_common(40):
            w(f"| {n} | {classify(e)} | {e[:140]} | {l} | {efirst[(e, l)]} |")
    return "\n".join(out) + "\n"


def main():
    global LOGS
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--logs", type=Path, default=LOGS)
    ap.add_argument("--debug", type=Path)
    ap.add_argument("--error", type=Path)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--rows", type=int, default=24)
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()
    LOGS = args.logs
    report = build_report(args)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(report)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
