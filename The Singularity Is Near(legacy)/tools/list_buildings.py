"""List vanilla building types matching a field, e.g. `python tools/list_buildings.py is_mill yes`."""
import re
import sys

from pdx import game_root, read_text, strip_comments, top_level_blocks


def main() -> int:
    field, value = sys.argv[1], sys.argv[2]
    pat = re.compile(rf"\b{re.escape(field)}\s*=\s*{re.escape(value)}\b")
    for p in sorted((game_root() / "in_game/common/building_types").glob("*.txt")):
        text = strip_comments(read_text(p))
        for b in top_level_blocks(text):
            if pat.search(b.text):
                pm = re.search(r"\bpop_type\s*=\s*(\w+)", b.text)
                emp = re.search(r"\bemployment_size\s*=\s*([\w.]+)", b.text)
                print(f"{p.name}\t{b.key}\tpop={pm.group(1) if pm else '-'}\temp={emp.group(1) if emp else '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
