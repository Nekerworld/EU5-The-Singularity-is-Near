"""Six-rank urban ladder, preserving the legacy megalopolis ID at 400k."""
import re
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pdx

def replace_block_field(text,key,value):
    pattern=rf'(?m)^(\s*){re.escape(key)}\s*=\s*[^\n{{]+$'
    return re.sub(pattern,lambda m:f'{m[1]}{key} = {value}',text,count=1)

def expand_ranks(text):
    blocks={b.key:b.text for b in pdx.top_level_blocks(text)}
    metro=blocks['megalopolis']
    for condition in ['is_market_center = yes','is_capital = yes','owner ?= { is_subject = no }']:
        metro=metro.replace('\n\t\t'+condition,'')
    metro=metro.replace('\n\tmax_rank = yes','')
    metro=metro.replace('upgrade_from = city','upgrade_from = tsin_large_city')
    large=blocks['city'].replace('city = {','tsin_large_city = {',1)
    large=large.replace('upgrade_from = town','upgrade_from = city')
    large=large.replace('population >= 30','population >= 100')
    large=replace_block_field(large,'local_max_rgo_size_modifier','0.20')
    large=replace_block_field(large,'free_building_levels','150')
    large=replace_block_field(large,'local_population_capacity','200')
    mega=metro.replace('megalopolis = {','tsin_megalopolis = {',1)
    mega=mega.replace('upgrade_from = tsin_large_city','upgrade_from = megalopolis')
    mega=mega.replace('population >= 400.000','population >= 1000\n\t\tdevelopment >= 50\n\t\tlocation_potential_tax_base >= 50')
    mega=replace_block_field(mega,'free_building_levels','300')
    mega=replace_block_field(mega,'local_population_capacity','800')
    mega=replace_block_field(mega,'tier','5')
    mega=mega.replace('\n\tshow_in_label = yes','\n\tmax_rank = yes\n\tshow_in_label = yes')
    ordered=[mega,metro,large,blocks['city'],blocks['town'],blocks['rural_settlement']]
    return '# Generated urban ladder; legacy IDs retained. Rank order is highest first.\n'+'\n\n'.join(ordered)+'\n'

RANK_FIELDS=('city','megalopolis','tsin_large_city','tsin_megalopolis')

def scalar_fields(text):
    """Top-level scalar fields only: inline syntax is valid; nested triggers are not permissions."""
    body=text[text.index('{')+1:-1]
    tokens=[];depth=0
    for m in re.finditer(r'"(?:\\.|[^"\\])*"|\#[^\n]*|[{}=]|[^\s{}=]+',body):
        token=m[0]
        if token.startswith('#'):continue
        if token=='{':depth+=1
        elif token=='}':depth-=1
        elif depth==0:tokens.append(token)
    return {tokens[i]:tokens[i+2] for i in range(len(tokens)-2) if tokens[i+1]=='='}

def permission_metadata(sources):
    nodes={}
    for text in sources:
        for block in pdx.top_level_blocks(text):
            if block.local_kind or block.key.startswith('@'):continue
            mode,sep,name=block.key.partition(':')
            if not sep:name,mode=mode,''
            fields=scalar_fields(block.text)
            rank={k:fields[k]=='yes' for k in RANK_FIELDS if fields.get(k) in ('yes','no')}
            full=mode in ('','REPLACE','TRY_REPLACE','REPLACE_OR_CREATE')
            inject=mode in ('INJECT','TRY_INJECT','INJECT_OR_CREATE')
            if full:nodes[name]={'fields':rank,'parent':fields.get('copy_from','').strip(chr(34)).split(':')[-1]}
            elif inject:
                if name not in nodes and mode!='INJECT_OR_CREATE':continue
                node=nodes.setdefault(name,{'fields':{},'parent':''});node['fields'].update(rank)
                if 'copy_from' in fields:node['parent']=fields['copy_from'].strip(chr(34)).split(':')[-1]
    resolved={}
    def resolve(name,seen):
        if name in resolved:return resolved[name]
        if name in seen:raise ValueError('recursive building copy_from: '+name)
        node=nodes[name];parent=node['parent']
        inherited=resolve(parent,seen|{name}).copy() if parent in nodes else {}
        inherited.update(node['fields']);resolved[name]=inherited;return inherited
    for name in nodes:resolve(name,set())
    return resolved

def permission_patch(flags):
    out=['# Generated rank permissions only; no third-party building definitions are copied.']
    for key,fields in sorted(flags.items()):
        entries=[]
        for old,new in [('city','tsin_large_city'),('megalopolis','tsin_megalopolis')]:
            # Explicit new-rank choices win. Otherwise mirror old-rank permissions, including no.
            if old in fields and new not in fields:entries.append(new+' = '+('yes' if fields.get(old,False) else 'no'))
        if entries:out.append('TRY_INJECT:'+key+' = { '+' '.join(entries)+' }')
    return '\n'.join(out)+'\n'

def compatibility():
    from compat_scan import playset_mods
    _,mods=playset_mods(None)
    roots=[pdx.game_root()]+mods
    if not any(r.resolve()==pdx.MOD_ROOT.resolve() for r in mods):roots.append(pdx.MOD_ROOT)
    # Equal paths are overwritten by playset order. Surviving files load by filename, across mods.
    files={}
    for root in roots:
        for p in (root/'in_game/common/building_types').glob('*.txt'):
            if p.name=='zzzzzz_tsin_city_building_ranks.txt':continue
            files[p.name.casefold()]=p
    sources=[pdx.read_text(p) for _,p in sorted(files.items())]
    return permission_patch(permission_metadata(sources))


def rewrite_rank_checks(text):
    for old,new in [('city','tsin_is_city_or_large_city'),('megalopolis','tsin_is_metropolis_or_megalopolis')]:
        text=re.sub(r'(?<![\w.])location_rank\s*(?:\?=|=)\s*location_rank:'+old+r'\b',new+' = yes',text)
    return text

RANK_TRIGGERS = 'tsin_is_city_or_large_city = {\n OR = { location_rank ?= location_rank:city location_rank ?= location_rank:tsin_large_city }\n}\ntsin_is_metropolis_or_megalopolis = {\n OR = { location_rank ?= location_rank:megalopolis location_rank ?= location_rank:tsin_megalopolis }\n}\ntsin_is_city_location = {\n OR = { is_city = yes tsin_is_city_or_large_city = yes tsin_is_metropolis_or_megalopolis = yes }\n}\ntsin_is_urban_location = {\n OR = { tsin_is_city_location = yes location_rank ?= location_rank:town }\n}\n'

def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    outputs={'in_game/common/building_types/zzzzzz_tsin_city_building_ranks.txt':compatibility(),
     'in_game/common/scripted_triggers/tsin_city_ranks.txt': RANK_TRIGGERS}
    for lang,names in {'korean':['메트로폴리스','대도시','메갈로폴리스'],'english':['Metropolis','Large City','Megalopolis']}.items():
        outputs[f'main_menu/localization/{lang}/tsin_city_expansion_l_{lang}.yml']='l_'+lang+':\n'+''.join(f' {key}: "{value}"\n' for key,value in zip(['megalopolis','tsin_large_city','tsin_megalopolis'],names))
    mismatches=[]
    for rel,text in outputs.items():
        p=pdx.MOD_ROOT/rel
        if args.check:
            if not p.exists() or pdx.read_text(p)!=text:mismatches.append(rel)
        else:pdx.write_text_bom(p,text)
    print('City expansion:',len(outputs),'files;',len(mismatches),'differences')
    return bool(mismatches)
if __name__=='__main__':raise SystemExit(main())
