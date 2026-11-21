"""Minimal Paradox (Jomini) script helpers used by the TSIN tools.

Only what the tools need: comment-aware scanning, top-level block extraction
and brace matching. This is not a full parser.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_GAME = r"C:\Program Files (x86)\Steam\steamapps\common\Europa Universalis V\game"
DEFAULT_WORKSHOP = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\3450310"

MOD_ROOT = Path(__file__).resolve().parent.parent


def game_root() -> Path:
    return Path(os.environ.get("TSIN_GAME", DEFAULT_GAME))


def workshop_root() -> Path:
    return Path(os.environ.get("TSIN_WORKSHOP", DEFAULT_WORKSHOP))


def content_path(path: Path) -> Path:
    """Resolve a game-relative path to its era-owned authoring source, if registered."""
    from era_layout import source_path
    return source_path(path, MOD_ROOT)


def read_bytes(path: Path) -> bytes:
    return content_path(path).read_bytes()


def read_text(path: Path) -> str:
    return content_path(path).read_text(encoding="utf-8-sig", errors="replace")


def write_bytes(path: Path, data: bytes) -> None:
    from era_layout import write_bytes as write_content
    write_content(path, data, MOD_ROOT)


def write_text_bom(path: Path, text: str) -> None:
    write_bytes(path, text.replace('\r\n', '\n').encode('utf-8-sig'))


def code_mask(text: str) -> list[bool]:
    """True for characters that are code (not inside a # comment)."""
    mask = [True] * len(text)
    in_str = False
    in_comment = False
    for i, ch in enumerate(text):
        if in_comment:
            if ch == "\n":
                in_comment = False
            else:
                mask[i] = False
            continue
        if ch == '"':
            in_str = not in_str
        elif ch == "#" and not in_str:
            in_comment = True
            mask[i] = False
        elif ch == "\n":
            in_str = False
    return mask


def strip_comments(text: str) -> str:
    mask = code_mask(text)
    return "".join(c if m else ("\n" if c == "\n" else " ") for c, m in zip(text, mask))


@dataclass
class Block:
    key: str
    start: int  # index of first char of key
    end: int  # index after closing brace
    text: str  # full original text "key = { ... }"
    local_kind: str = ""  # "scripted_trigger"/"scripted_effect" for file-local definitions


_KEY_RE = re.compile(r"(?:(scripted_trigger|scripted_effect)\s+)?([A-Za-z0-9_@:.\-]+)\s*=\s*\{")


def top_level_blocks(text: str) -> list[Block]:
    """Return top-level `key = { ... }` blocks (comments ignored)."""
    clean = strip_comments(text)
    blocks: list[Block] = []
    depth = 0
    i = 0
    n = len(clean)
    while i < n:
        ch = clean[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif depth == 0 and not ch.isspace():
            m = _KEY_RE.match(clean, i)
            if m:
                open_idx = m.end() - 1
                close_idx = matching_brace(clean, open_idx)
                if close_idx < 0:
                    break
                blocks.append(Block(m.group(2), i, close_idx + 1, text[i:close_idx + 1], m.group(1) or ""))
                i = close_idx + 1
                continue
            # skip a non-block token line (e.g. namespace = x, @var = 1)
            j = clean.find("\n", i)
            i = n if j < 0 else j
            continue
        i += 1
    return blocks


def matching_brace(clean: str, open_idx: int) -> int:
    depth = 0
    in_str = False
    for k in range(open_idx, len(clean)):
        c = clean[k]
        if c == '"':
            in_str = not in_str
        elif in_str:
            continue
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return k
    return -1


_VAR_RE = re.compile(r"^\s*(@[A-Za-z0-9_]+)\s*=\s*([^\n#]+)", re.M)
_NS_RE = re.compile(r"^\s*namespace\s*=\s*([A-Za-z0-9_]+)", re.M)


def file_variables(text: str) -> dict[str, str]:
    return {m.group(1): m.group(2).strip() for m in _VAR_RE.finditer(strip_comments(text))}


def namespaces(text: str) -> list[str]:
    return _NS_RE.findall(strip_comments(text))


def iter_script_files(root: Path, rel_dirs: list[str], suffix: str = ".txt"):
    for rel in rel_dirs:
        base = root / rel
        if not base.exists():
            continue
        for p in sorted(base.rglob(f"*{suffix}")):
            yield p
