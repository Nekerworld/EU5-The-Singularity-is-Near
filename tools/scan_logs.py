"""Summarise game log lines that mention this mod's files or objects.

Usage: python tools/scan_logs.py [--all]
  --all  also print every error line, not only mod-related ones
"""
import re
import sys
from collections import Counter
from pathlib import Path

LOGS = Path.home() / "Documents" / "Paradox Interactive" / "Europa Universalis V" / "logs"
FILES = ["error.log", "game.log", "debug.log"]
MOD_PATTERN = re.compile(r"tsin_|age_7_industrialization|The Singularity Is Near|zzz_tsin", re.I)


def main() -> int:
    show_all = "--all" in sys.argv
    for name in FILES:
        path = LOGS / name
        if not path.exists():
            print(f"== {name}: (missing)")
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        hits = [ln for ln in lines if MOD_PATTERN.search(ln)]
        print(f"== {name}: {len(lines)} lines, {len(hits)} mention the mod")
        # collapse timestamps so repeated messages are counted together
        counts = Counter(re.sub(r"^\[[^\]]*\]\s*", "", ln) for ln in (lines if show_all and name == "error.log" else hits))
        for msg, n in counts.most_common(60):
            print(f"  {n:>4} x {msg[:400]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
