"""Print modifier type definitions and icons for a new good, mirroring a vanilla template good.

Vanilla defines ten modifier types per good (can_extract_X, ban_exports_of_X, ...).
Usage: python tools/goods_modifiers.py <template_good> <new_good>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pdx  # noqa: E402

COMMON = pdx.game_root() / "main_menu/common"


def blocks_for(path: Path, good: str) -> list[str]:
    text = pdx.read_text(path)
    out = []
    for b in pdx.top_level_blocks(pdx.strip_comments(text)):
        if re.search(rf"(^|_){good}(_|$)", b.key):
            out.append(b.text)
    return out


def main() -> int:
    template, new = sys.argv[1], sys.argv[2]
    for sub in ("modifier_type_definitions/00_modifier_types.txt", "modifier_icons/00_modifier_icons.txt"):
        print(f"# ---- {sub}")
        for text in blocks_for(COMMON / sub, template):
            print(re.sub(rf"(?<![a-z]){template}(?![a-z])", new, text))
            print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
