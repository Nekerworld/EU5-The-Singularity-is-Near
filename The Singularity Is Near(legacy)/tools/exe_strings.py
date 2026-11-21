"""Print printable strings near a token in the game executable (engine doc lookup)."""
import re
import sys

from pdx import game_root

EXE = game_root().parent / "binaries" / "eu5.exe"


def main() -> int:
    tokens = sys.argv[1:]
    data = EXE.read_bytes()
    for token in tokens:
        for m in re.finditer(re.escape(token.encode()), data):
            lo, hi = max(0, m.start() - 600), m.end() + 600
            chunk = data[lo:hi]
            strings = [s.decode("ascii", "replace") for s in re.findall(rb"[\x20-\x7e]{4,}", chunk)]
            print(f"== {token} @ {m.start():#x}")
            for s in strings:
                print("   ", s[:300])
    return 0


if __name__ == "__main__":
    sys.exit(main())
