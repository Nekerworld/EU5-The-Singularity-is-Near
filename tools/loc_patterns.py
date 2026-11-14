"""Show which localization keys vanilla defines for the first objects of each database."""
import re
import sys

from pdx import game_root, read_text, top_level_blocks

DBS = [
    "in_game/common/situations", "in_game/common/disasters", "in_game/common/laws",
    "in_game/common/movements", "in_game/common/cabinet_actions", "in_game/common/decisions",
    "in_game/common/parliament_issues", "in_game/common/parliament_agendas",
    "in_game/common/government_reforms", "in_game/common/building_types", "in_game/common/goods",
    "in_game/common/missions", "in_game/common/game_rules", "main_menu/common/game_rules",
    "in_game/common/estate_privileges", "in_game/common/casus_belli",
]


def main() -> int:
    root = game_root()
    loc_text = "\n".join(read_text(p) for p in (root / "main_menu/localization/english").rglob("*.yml"))
    for d in DBS:
        base = root / d
        if not base.exists():
            print(f"{d}: (missing)")
            continue
        keys = []
        for p in sorted(base.glob("*.txt"))[:3]:
            keys += [b.key for b in top_level_blocks(read_text(p)) if not b.key.startswith("@")][:2]
        print(f"== {d}")
        for k in keys[:3]:
            found = sorted(set(re.findall(rf"^\s*({re.escape(k)}[\w.]*):", loc_text, re.M)))
            print(f"   {k}: {found[:8]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
