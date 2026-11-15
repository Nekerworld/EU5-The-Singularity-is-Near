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

def compatibility():
    from compat_scan import playset_mods
    _,mods=playset_mods(None)
    roots=[pdx.game_root()]+mods+[pdx.MOD_ROOT]
    flags={}
    for root in roots:
        for p in sorted((root/'in_game/common/building_types').glob('*.txt')):
            if p.name=='zzzzzz_tsin_city_building_ranks.txt':continue
            for b in pdx.top_level_blocks(pdx.read_text(p)):
                mode,_,name=b.key.partition(':')
                name=name if name else mode
                if ':' not in b.key or mode in ('REPLACE','TRY_REPLACE','REPLACE_OR_CREATE'):
                    flags[name]=[bool(re.search(r'(?m)^\s*city\s*=\s*yes\b',b.text)),bool(re.search(r'(?m)^\s*megalopolis\s*=\s*yes\b',b.text))]
    out=['# Generated rank permissions only; no third-party building definitions are copied.']
    for key,(city,metro) in sorted(flags.items()):
        if city or metro:
            entries=[]
            if city:entries.append('tsin_large_city = yes')
            if metro:entries.append('tsin_megalopolis = yes')
            out.append('TRY_INJECT:'+key+' = { '+' '.join(entries)+' }')
    return '\n'.join(out)+'\n'

def rewrite_rank_checks(text):
    for old,new in [('city','tsin_is_city_or_large_city'),('megalopolis','tsin_is_metropolis_or_megalopolis')]:
        text=re.sub(r'(?<![\w.])location_rank\s*(?:\?=|=)\s*location_rank:'+old+r'\b',new+' = yes',text)
    return text

def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args()
    outputs={'in_game/common/building_types/zzzzzz_tsin_city_building_ranks.txt':compatibility(),
     'in_game/common/scripted_triggers/tsin_city_ranks.txt': '''tsin_is_city_or_large_city = {
 OR = { location_rank ?= location_rank:city location_rank ?= location_rank:tsin_large_city }
}
tsin_is_metropolis_or_megalopolis = {
 OR = { location_rank ?= location_rank:megalopolis location_rank ?= location_rank:tsin_megalopolis }
}
'''}
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
