"""Stage an upload copy of the mod without docs/, tools/, .git and other development files.

Usage: python tools/build_release.py [--dest DIR] [--skip-checks]
  --dest         target folder (default tools/out/release/The Singularity Is Near)
  --skip-checks  do not run validate.py and audit.py first

The game's uploader has no ignore list, so the workshop item is uploaded from this staged copy
(docs/release.md). Keys that the uploader wrote into the staged metadata.json (for example a
workshop id) are kept and reported so they can be copied back into .metadata/metadata.json.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pdx  # noqa: E402

ROOT = pdx.MOD_ROOT
GAME_DIRS = ["in_game", "main_menu", "loading_screen"]
METADATA_FILES = ["metadata.json", "thumbnail.png"]
CHANGELOG = ROOT / "docs" / "changelog.md"
MAX_THUMBNAIL_BYTES = 1024 * 1024


def run_checks() -> bool:
    ok = True
    for script in ("validate.py", "audit.py"):
        res = subprocess.run([sys.executable, str(ROOT / "tools" / script)], cwd=ROOT,
                             capture_output=True, text=True, encoding="utf-8", errors="replace")
        last = (res.stdout.strip().splitlines() or ["(no output)"])[-1]
        print(f"{script}: {last}")
        ok &= res.returncode == 0
    return ok


def check_release_files(meta: dict) -> list[str]:
    problems = []
    version = meta.get("version", "")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        problems.append(f"metadata version '{version}' is not MAJOR.MINOR.PATCH")
    if CHANGELOG.exists():
        top = re.search(r"^## (\d+\.\d+\.\d+)", CHANGELOG.read_text(encoding="utf-8"), re.M)
        if not top or top.group(1) != version:
            problems.append(f"docs/changelog.md top entry {top.group(1) if top else '(none)'} != metadata {version}")
    else:
        problems.append("docs/changelog.md is missing")
    thumb = ROOT / ".metadata" / "thumbnail.png"
    if not thumb.exists():
        problems.append(".metadata/thumbnail.png is missing")
    elif thumb.stat().st_size > MAX_THUMBNAIL_BYTES:
        problems.append(f"thumbnail.png is {thumb.stat().st_size // 1024} KB (keep it under 1 MB)")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", type=Path, default=ROOT / "tools" / "out" / "release" / "The Singularity Is Near")
    ap.add_argument("--skip-checks", action="store_true")
    args = ap.parse_args()
    dest: Path = args.dest.resolve()
    root, out_dir = ROOT.resolve(), (ROOT / "tools" / "out").resolve()
    if dest == root or (root in dest.parents and out_dir not in dest.parents):
        sys.exit("refusing to stage inside the mod folder (only tools/out/ is allowed)")

    # Source modules must be deployed even when --skip-checks is requested.
    from era_layout import sync as sync_eras, check as check_eras
    deployed = sync_eras(ROOT)
    layout_errors = check_eras(ROOT)
    if layout_errors:
        for message in layout_errors: print('PROBLEM', message)
        return 1
    print(f'era runtime files refreshed: {deployed}')
    meta = json.loads((ROOT / ".metadata" / "metadata.json").read_text(encoding="utf-8-sig"))
    problems = check_release_files(meta)
    if not args.skip_checks and not run_checks():
        problems.append("validate.py or audit.py reported errors")
    for p in problems:
        print("PROBLEM", p)
    if problems:
        return 1

    kept = {}
    old_meta = dest / ".metadata" / "metadata.json"
    if old_meta.exists():
        old = json.loads(old_meta.read_text(encoding="utf-8-sig"))
        kept = {k: v for k, v in old.items() if k not in meta}
        if kept:
            print(f"keeping uploader keys from the staged metadata: {sorted(kept)} - copy them into .metadata/metadata.json")
    for sub in GAME_DIRS + [".metadata"]:
        if (dest / sub).exists():
            shutil.rmtree(dest / sub)
    for sub in GAME_DIRS:
        if (ROOT / sub).exists():
            shutil.copytree(ROOT / sub, dest / sub)
    (dest / ".metadata").mkdir(parents=True, exist_ok=True)
    for name in METADATA_FILES:
        shutil.copy2(ROOT / ".metadata" / name, dest / ".metadata" / name)
    if kept:
        merged = {**meta, **kept}
        (dest / ".metadata" / "metadata.json").write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    files = [p for p in dest.rglob("*") if p.is_file()]
    size = sum(p.stat().st_size for p in files)
    left_out = sorted(p.name for p in ROOT.iterdir() if p.name not in GAME_DIRS + [".metadata"])
    print(f"staged {meta['name']} {meta['version']}: {len(files)} files, {size / 1e6:.1f} MB -> {dest}")
    print(f"left out: {', '.join(left_out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
