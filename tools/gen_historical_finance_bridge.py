"""Connect existing vanilla financial events to the shared stock model.

The original events, triggers, choices and costs are retained. Local playset
adapters can be built from winning workshop event definitions without vendoring
those definitions into the main repository.
"""
from pathlib import Path
import argparse,re
import pdx

TARGETS={
    'flavor_hol.6':('DHE/flavor_hol.txt','merchant_house',0.75),
    'flavor_eng.215':('DHE/flavor_ENG.txt','south_sea',0.75),
    'flavor_fra.509':('DHE/flavor_FRA.txt','merchant_bank',1.0),
    'flavor_fra.511':('DHE/flavor_FRA.txt','mississippi',0.7),
}
REL='in_game/events/DHE/zzzz_tsin_finance_history.txt'


def patch_event(text,key,company,factor):
    block=next(b for b in pdx.top_level_blocks(text) if b.key==key)
    original=block.text
    assert 'tsin_historic_' not in original,'already patched historical event'
    children=pdx.top_level_blocks(original[original.index('{')+1:-1])
    result=original
    for option in [b for b in children if b.key=='option']:
        body=option.text[:-1]+f'\n tsin_historic_finance_{company}_effect = {{ FACTOR = {factor} }}\n}}'
        result=result.replace(option.text,body,1)
    return result


def build(roots=None):
    from gen_age7_patches import referenced_locals
    roots=roots or [pdx.game_root()]
    sources={}
    for root in roots:
        for p in sorted((root/'in_game/events').rglob('*.txt')):
            if p.name.startswith('zzzz_tsin_finance_'):continue
            text=pdx.read_text(p)
            if not any(key in text for key in TARGETS):continue
            for block in pdx.top_level_blocks(text):
                if block.key in TARGETS:sources[block.key]=text
    groups={ns:dict(variables={},helpers={},events=[]) for ns in sorted({k.split('.')[0] for k in TARGETS})}
    for key,(_,company,factor) in TARGETS.items():
        if key not in sources:raise ValueError('Missing historical event '+key)
        text=sources[key]
        group=groups[key.split('.')[0]]
        patched=patch_event(text,key,company,factor)
        local={b.key:b for b in pdx.top_level_blocks(text) if b.local_kind}
        needed=referenced_locals(pdx.strip_comments(patched),local)
        for name in needed:
            helper=local[name].text
            if name in group['helpers'] and group['helpers'][name]!=helper:
                raise ValueError('Conflicting historical local helper '+name)
            group['helpers'][name]=helper
        variables=pdx.file_variables(text)
        pending=re.findall(r'@[A-Za-z0-9_]+',pdx.strip_comments(patched+'\n'+'\n'.join(local[n].text for n in needed)))
        while pending:
            name=pending.pop()
            if name not in variables:raise ValueError('Missing historical file variable '+name)
            value=variables[name]
            if name in group['variables']:
                if group['variables'][name]!=value:raise ValueError('Conflicting historical file variable '+name)
                continue
            group['variables'][name]=value
            pending.extend(re.findall(r'@[A-Za-z0-9_]+',value))
        group['events'].append(patched)
    out={}
    for ns,group in groups.items():
        parts=['# GENERATED: original historical events plus a local stock-market link.','namespace = '+ns]
        parts.extend(name+' = '+value for name,value in group['variables'].items())
        parts.extend(group['helpers'].values())
        parts.extend(group['events'])
        out[f'in_game/events/DHE/zzzz_tsin_finance_{ns}.txt']='\n\n'.join(parts)+'\n'
    return {rel:'\n'.join(re.sub(r'^[ \t]+', lambda m:m[0].expandtabs(4), line).rstrip() for line in text.splitlines())+'\n' for rel,text in out.items()}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--playset',action='store_true');args=p.parse_args()
    roots=None;output=pdx.MOD_ROOT
    if args.playset:
        from compat_scan import playset_mods
        _,mods=playset_mods(None)
        roots=[pdx.game_root()]+[r for r in mods if not r.name.startswith('The Singularity')]
        output=pdx.MOD_ROOT.parent/'The Singularity Is Near - Playset Compat'
    bad=[]
    legacy=output/REL
    if legacy.exists():
        if args.check:bad.append(REL+' (obsolete combined namespace file)')
        else:
            assert pdx.read_text(legacy).startswith('# GENERATED: original historical events')
            legacy.unlink()
    for rel,text in build(roots).items():
        if args.check:
            if not (output/rel).exists() or pdx.read_text(output/rel)!=text:bad.append(rel)
        else:pdx.write_text_bom(output/rel,text)
    print(f'4 historical financial events; {len(bad)} mismatches')
    return bool(bad)


if __name__=='__main__':raise SystemExit(main())
