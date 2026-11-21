"""Authoring modules mapped to the fixed EU5 runtime folders.

No engine mount-path extension is assumed. Only manifest-listed files resolve
to era sources; shared files and external compatibility mods stay untouched.
"""
from functools import lru_cache
from pathlib import Path, PurePosixPath
import json

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_ROOTS = {'in_game', 'main_menu', 'loading_screen'}
IGNORE_START = '# BEGIN GENERATED ERA RUNTIME FILES'
IGNORE_END = '# END GENERATED ERA RUNTIME FILES'


def safe_path(root, relative):
    rel = PurePosixPath(relative)
    if rel.is_absolute() or not rel.parts or any(p in ('..', '.') or ':' in p or '\\' in p for p in rel.parts):
        raise ValueError(f'invalid module path: {relative}')
    target = root.joinpath(*rel.parts)
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'path escapes module root: {relative}')
    return target


@lru_cache(maxsize=16)
def entries(root=ROOT):
    root = Path(root)
    registry = root / 'data/content_modules.json'
    if not registry.exists():
        return {}
    config = json.loads(registry.read_text(encoding='utf-8-sig'))
    if config.get('schema_version') != 1:
        raise ValueError('unsupported content module registry')
    result = {}
    for module in config['modules']:
        folder = safe_path(root, module['folder'])
        manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8-sig'))
        if manifest.get('schema_version') != 1:
            raise ValueError('unsupported era manifest')
        for relative, category in manifest['files'].items():
            if PurePosixPath(relative).parts[0] not in RUNTIME_ROOTS:
                raise ValueError(f'not an EU5 runtime path: {relative}')
            runtime = safe_path(root, relative)
            source = safe_path(folder, relative)
            if relative.casefold() in {r.casefold() for r in result}:
                raise ValueError(f'overlapping era files: {relative}')
            result[relative] = (source, runtime, category)
    return result


def source_path(path, root=ROOT):
    path, root = Path(path), Path(root)
    try:
        rel = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path
    row = entries(root).get(rel)
    return row[0] if row else path


def write_bytes(path, data, root=ROOT):
    """Generators write canonical content and its runtime mirror together."""
    path, root = Path(path), Path(root)
    source = source_path(path, root)
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes(data)
    if source != path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    else:
        # Also handle a generator explicitly passed an era source path.
        for original, runtime, _ in entries(root).values():
            if source.resolve() == original.resolve():
                runtime.parent.mkdir(parents=True, exist_ok=True)
                runtime.write_bytes(data)
                break


def ignore_block(root=ROOT):
    return IGNORE_START + '\n' + '\n'.join('/'+rel for rel in sorted(entries(root))) + '\n' + IGNORE_END


def check(root=ROOT):
    root = Path(root)
    problems = []
    rows = entries(root)
    if not rows:
        return problems
    for relative, (source, runtime, _) in rows.items():
        if not source.is_file():
            problems.append(f'missing era source: {source.relative_to(root)}')
        elif not runtime.is_file() or runtime.read_bytes() != source.read_bytes():
            problems.append(f'outdated runtime mirror: {relative}; run tools/sync_eras.py')
    config = json.loads((root / 'data/content_modules.json').read_text(encoding='utf-8-sig'))
    declared = {source.resolve() for source, _, _ in rows.values()}
    for module in config['modules']:
        folder = safe_path(root, module['folder'])
        for sub in RUNTIME_ROOTS:
            for p in (folder / sub).rglob('*'):
                if p.is_file() and p.resolve() not in declared:
                    problems.append(f'unregistered era source: {p.relative_to(root)}; use sync_eras.py --register')
    ignore = (root / '.gitignore').read_text(encoding='utf-8-sig') if (root / '.gitignore').exists() else ''
    if ignore_block(root) not in ignore:
        problems.append('era runtime .gitignore list is outdated')
    return problems


def sync(root=ROOT):
    root = Path(root)
    rows = entries(root)
    # Validate every source before any runtime write.
    missing = [str(p) for p, _, _ in rows.values() if not p.is_file()]
    if missing:
        raise ValueError('missing era sources: '+', '.join(missing))
    count = 0
    for source, runtime, _ in rows.values():
        data = source.read_bytes()
        if not runtime.exists() or runtime.read_bytes() != data:
            runtime.parent.mkdir(parents=True, exist_ok=True)
            runtime.write_bytes(data)
            count += 1
    return count


def update_ignore(root=ROOT):
    root = Path(root)
    path = root / '.gitignore'
    text = path.read_text(encoding='utf-8-sig') if path.exists() else ''
    block = ignore_block(root)
    if IGNORE_START in text:
        start, end = text.index(IGNORE_START), text.index(IGNORE_END)+len(IGNORE_END)
        text = text[:start]+block+text[end:]
    else:
        text = text.rstrip()+'\n\n'+block+'\n'
    path.write_text(text, encoding='utf-8', newline='\n')
