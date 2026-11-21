"""Deploy era sources to EU5 paths. --check is read-only; --register adds new sources.

Edit era_7/{in_game,main_menu}/..., then run this before launching the game.
Generators using pdx.write_text_bom/write_bytes deploy their own outputs too.
"""
import argparse,json
from pathlib import Path
import era_layout as layout


def register(root):
    config=json.loads((root/'data/content_modules.json').read_text(encoding='utf-8-sig'))
    # Validate all additions before changing any manifest or ignore file.
    changes=[]
    known=layout.entries(root)
    claimed={r.casefold() for r in known}
    for module in config['modules']:
        folder=layout.safe_path(root,module['folder'])
        path=folder/'manifest.json'
        manifest=json.loads(path.read_text(encoding='utf-8-sig'))
        for sub in sorted(layout.RUNTIME_ROOTS):
            for source in sorted((folder/sub).rglob('*')):
                if not source.is_file():continue
                rel=source.relative_to(folder).as_posix()
                if rel in manifest['files']:continue
                layout.safe_path(folder,rel)
                runtime=layout.safe_path(root,rel)
                if runtime.exists() or rel.casefold() in claimed:
                    raise ValueError(f'new era source conflicts with existing global/runtime file: {rel}')
                manifest['files'][rel]='new-era-content'
                claimed.add(rel.casefold())
        manifest['files']=dict(sorted(manifest['files'].items()))
        changes.append((path,manifest))
    for path,manifest in changes:path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    layout.entries.cache_clear()
    layout.update_ignore(root)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--check',action='store_true')
    p.add_argument('--register',action='store_true')
    args=p.parse_args()
    if args.check and args.register:p.error('--check cannot register files')
    if args.register:register(layout.ROOT)
    count=0 if args.check else layout.sync()
    errors=layout.check()
    for error in errors:print('ERROR',error)
    print(f'{len(layout.entries())} era files; {count} deployed; {len(errors)} errors')
    return bool(errors)


if __name__=='__main__':raise SystemExit(main())
