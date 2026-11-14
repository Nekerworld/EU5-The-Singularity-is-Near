"""Collision scan between this mod and the mods of a launcher playset.

Usage:
  python tools/compat_scan.py                      active playset in playsets.json
  python tools/compat_scan.py --playset "NAME"     a named playset
  python tools/compat_scan.py --mods 3620382806    given workshop ids (or mod folders)

Reports, per other mod:
  path    same relative file path (the later-loaded file replaces the other whole)
  object  same top-level key in the same database folder (common/<db>, events)
  define  same NGame/NCountry... key in loading_screen/common/defines
  loc     same localization key (english)
Equal paths are decided by the mod list (this mod assumed last, docs/load_order.md); different files of one
folder load in file-name order, so most object collisions are decided by file names, not the mod list.
Writes tools/out/compat_<label>.md.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pdx  # noqa: E402

PLAYSETS = Path.home() / "Documents" / "Paradox Interactive" / "Europa Universalis V" / "playsets.json"
OUT = pdx.MOD_ROOT / "tools" / "out"
PREFIXES = ("TRY_REPLACE:", "REPLACE_OR_CREATE:", "REPLACE:", "TRY_INJECT:", "INJECT_OR_CREATE:", "INJECT:")
SCAN_EXT = {".txt", ".yml", ".gui", ".dds", ".png", ".shader", ".fxh", ".asset", ".mesh"}
LOC_KEY = re.compile(r"^\s+([A-Za-z0-9_.\-]+):\d*\s*\"", re.M)
DEFINE_BLOCK = re.compile(r"^\s*(N[A-Za-z]+)\s*=\s*\{", re.M)
DEFINE_KEY = re.compile(r"^\s*([A-Z][A-Z0-9_]+)\s*=", re.M)


def split_mode(key: str) -> tuple[str, str]:
    for p in PREFIXES:
        if key.startswith(p):
            return p[:-1], key[len(p):]
    return "", key


def db_dir(rel: tuple[str, ...]) -> str | None:
    if len(rel) > 3 and rel[1] == "common":
        return "/".join(rel[:3])
    if len(rel) > 2 and rel[0] == "in_game" and rel[1] == "events":
        return "in_game/events"
    return None


class ModIndex:
    def __init__(self, root: Path):
        self.root = root
        self.name = root.name
        meta = root / ".metadata" / "metadata.json"
        if meta.exists():
            try:
                self.name = json.loads(pdx.read_text(meta)).get("name") or root.name
            except json.JSONDecodeError:
                pass
        self.paths: set[str] = set()
        self.objects: dict[tuple[str, str], tuple[str, str]] = {}  # (db, name) -> (mode, file)
        self.defines: dict[str, str] = {}
        self.loc: dict[str, str] = {}
        for p in root.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in SCAN_EXT:
                continue
            rel = p.relative_to(root).parts
            if rel[0].startswith(".") or rel[0] in ("docs", "tools", "repo"):
                continue
            rel_s = "/".join(rel)
            self.paths.add(rel_s.lower())
            if p.suffix == ".txt":
                self._index_txt(p, rel, rel_s)
            elif p.suffix == ".yml" and "english" in rel:
                for k in LOC_KEY.findall(pdx.read_text(p)):
                    self.loc.setdefault(k, rel_s)

    def _index_txt(self, p: Path, rel: tuple[str, ...], rel_s: str) -> None:
        text = pdx.read_text(p)
        if rel[:3] == ("loading_screen", "common", "defines"):
            clean = pdx.strip_comments(text)
            for m in DEFINE_BLOCK.finditer(clean):
                close = pdx.matching_brace(clean, clean.index("{", m.start()))
                for k in DEFINE_KEY.findall(clean[m.end():close]):
                    self.defines[f"{m.group(1)}.{k}"] = rel_s
            return
        d = db_dir(rel)
        if not d:
            return
        try:
            blocks = pdx.top_level_blocks(text)
        except Exception:  # noqa: BLE001
            return
        for b in blocks:
            if b.local_kind:
                continue
            if d.endswith("named_colors") and b.key == "colors":
                # container block: entries from every file merge, only equal color names collide
                inner = pdx.strip_comments(b.text)[b.text.index("{") + 1:-1]
                for color in re.findall(r"(?m)^\s*([A-Za-z0-9_]+)\s*=", inner):
                    self.objects[(d, color)] = ("", rel_s)
                continue
            mode, name = split_mode(b.key)
            self.objects[(d, name)] = (mode, rel_s)


def playset_mods(name: str | None) -> tuple[str, list[Path]]:
    data = json.loads(PLAYSETS.read_text(encoding="utf-8-sig"))
    sets = data.get("playsets", [])
    chosen = next((s for s in sets if (s.get("name") == name if name else s.get("isActive"))), None)
    if not chosen:
        sys.exit(f"playset not found: {name or '(active)'}")
    mods = [Path(m["path"]) for m in chosen.get("orderedListMods", []) if m.get("isEnabled", True)]
    return chosen["name"], mods


def judge_object(db: str, mine: str, my_file: str, theirs: str, their_file: str) -> str:
    """Files of one folder load in file-name order across all mods; the mod list only breaks equal paths."""
    if db.endswith("/on_action") and not mine:
        return "on_action 목록 병합: 공존 (우리 블록은 on_actions 목록만 더함)"
    my_name, their_name = Path(my_file).name.lower(), Path(their_file).name.lower()
    later = "우리" if my_name >= their_name else "상대"
    full = ("", "REPLACE", "TRY_REPLACE", "REPLACE_OR_CREATE")
    if mine in full and theirs in full:
        return f"둘 다 전체 정의: 파일 이름순으로 뒤인 {later} 정의만 적용" + (", 상대 변경은 사라짐" if later == "우리" else ", 우리 제7시대 패치가 사라짐")
    if mine in full:
        if later == "우리":
            return "상대 주입이 우리 전체 정의보다 먼저 읽혀 사라질 수 있음(사용자 확인 필요)"
        return "상대 주입이 우리 전체 정의 뒤에 읽혀 함께 적용됨"
    if theirs in full:
        return "우리 주입이 상대 정의에 적용됨" if later == "우리" else "상대 전체 정의가 뒤에 읽혀 우리 주입이 사라질 수 있음(사용자 확인 필요)"
    return "둘 다 주입: 보통 공존"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--playset")
    ap.add_argument("--mods", nargs="*")
    args = ap.parse_args()

    if args.mods:
        label = "mods_" + "_".join(Path(m).name for m in args.mods)
        roots = [Path(m) if Path(m).is_dir() else pdx.workshop_root() / m for m in args.mods]
    else:
        label, roots = playset_mods(args.playset)
    me_root = pdx.MOD_ROOT.resolve()
    roots = [r for r in roots if r.exists() and r.resolve() != me_root]

    me = ModIndex(pdx.MOD_ROOT)
    lines = [f"# 호환 스캔: {label}", "",
             f"대상 {len(roots)}개 모드. 이 모드를 목록 맨 뒤에 둔다고 가정한다(`docs/load_order.md`).", ""]
    summary = []
    for order, root in enumerate(roots):
        other = ModIndex(root)
        paths = sorted(me.paths & other.paths)
        objs = sorted(set(me.objects) & set(other.objects))
        defs = sorted(set(me.defines) & set(other.defines))
        locs = sorted(set(me.loc) & set(other.loc))
        if not (paths or objs or defs or locs):
            continue
        summary.append((other.name, root.name, len(paths), len(objs), len(defs), len(locs)))
        lines += [f"## {other.name} (`{root.name}`, 플레이셋 {order + 1}번째)", ""]
        for p in paths:
            lines.append(f"- 경로: `{p}` — 이 모드 파일이 통째로 대신함")
        for key in objs:
            mm, mf = me.objects[key]
            tm, tf = other.objects[key]
            lines.append(f"- 객체: `{key[0]}` `{key[1]}` (우리 `{mf}` {mm or '정의'}, 상대 `{tf}` {tm or '정의'}) — {judge_object(key[0], mm, mf, tm, tf)}")
        for k in defs:
            lines.append(f"- define: `{k}` (상대 `{other.defines[k]}`) — 파일 이름 정렬상 나중 파일이 이김")
        if locs:
            shown = ", ".join(f"`{k}`" for k in locs[:15])
            lines.append(f"- 현지화 키 {len(locs)}개: {shown}{' …' if len(locs) > 15 else ''}")
        lines.append("")
    lines.insert(4, "| 모드 | id | 경로 | 객체 | define | 현지화 |")
    lines.insert(5, "|---|---|---|---|---|---|")
    for i, row in enumerate(summary):
        lines.insert(6 + i, "| " + " | ".join(str(x) for x in row) + " |")
    lines.insert(6 + len(summary), "")
    if not summary:
        lines.append("충돌 없음.")
    OUT.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", label)[:60]
    out = OUT / f"compat_{safe}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(summary)} of {len(roots)} mods overlap with this mod -> {out}")
    for row in summary:
        print(f"  {row[0][:40]:40} {row[1]:>12}  path {row[2]:>3}  obj {row[3]:>3}  def {row[4]:>2}  loc {row[5]:>3}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
