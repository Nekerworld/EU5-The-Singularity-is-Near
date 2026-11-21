"""Generate era VIII–XII scaffolds; no advances, institutions or events.

The economic/default fields temporarily match age VII. Artwork is an unmodified
placeholder copy. Edit data/eras.json for the timeline; --check never writes.
"""
from pathlib import Path
import argparse
import json
import re
import pdx

REGISTRY='data/eras.json'


def validate(data):
    rows=data['eras']
    if [r['number'] for r in rows] != list(range(7,13)):
        raise ValueError('The scaffold must retain contiguous stable era numbers 7–12')
    if len({r['id'] for r in rows})!=len(rows):
        raise ValueError('Duplicate era IDs')
    if any(not re.fullmatch(r'age_\d+_[a-z_]+',r['id']) for r in rows):
        raise ValueError('Invalid era ID')
    if [r['start_year'] for r in rows] != sorted({r['start_year'] for r in rows}):
        raise ValueError('Era start years must be unique and ascending')
    if rows[0]['id']!='age_7_industrialization' or rows[0]['start_year']!=1837:
        raise ValueError('Keep the existing age VII identity')
    for r in rows:
        if set(r['name']) != {'english','korean'} or set(r['concept']) != {'english','korean'}:
            raise ValueError('Missing era localization')
    return rows


def build(root, data):
    rows=validate(data)
    baseline=pdx.read_text(root/'in_game/common/age/tsin_age_7.txt')
    blocks=pdx.top_level_blocks(baseline)
    assert len(blocks)==1 and blocks[0].key==rows[0]['id']
    baseline=blocks[0].text
    future=['# GENERATED era scaffolds. Temporary age-VII defaults; no new gameplay content.']
    loc={lang:[f'l_{lang}:'] for lang in ['english','korean']}
    result={}
    for row in rows[1:]:
        b=baseline.replace(rows[0]['id'],row['id'],1)
        b,n=re.subn(r'\byear\s*=\s*1837\b','year = '+str(row['start_year']),b,count=1)
        assert n==1
        future += [f'# Era {row["number"]}: {row["start_year"]} onward. Shared age scaffold; gameplay content is defined separately.',b]
        for lang in loc:
            name=row['name'][lang]
            note=' Era scaffold only; dedicated technologies, institutions and events are not implemented.' if lang=='english' else ' 현재 시대 뼈대만 등록되어 있으며 전용 기술·시대관·이벤트는 구현되지 않았습니다.'
            if row.get('implementation')=='partial':
                note=' Agricultural, transport and military transition content is implemented. Dedicated institutions and larger political systems remain under development.' if lang=='english' else ' 농업·운송·군사 전환 콘텐츠를 구현했습니다. 전용 시대관과 본격적인 정치 체계는 개발 예정입니다.'
            note=row.get('implementation_note',{}).get(lang,note)
            values={row['id']:name,row['id']+'_desc':row['concept'][lang]+note,
                    'age_format_'+row['id']:(f'Age of ${row["id"]}$' if lang=='english' else f'${row["id"]}$의 시대')}
            for key,value in values.items():loc[lang].append(f' {key}: {json.dumps(value,ensure_ascii=False)}')
        for sub in ['icons/age','illustrations/advances']:
            rel=f'main_menu/gfx/interface/{sub}/{row["id"]}.dds'
            result[rel]=pdx.read_bytes(root/f'main_menu/gfx/interface/{sub}/{rows[0]["id"]}.dds')
    result['in_game/common/age/zz_tsin_future_ages.txt']='\n\n'.join(future)+'\n'
    old=pdx.read_text(root/'in_game/common/scripted_triggers/tsin_age_triggers.txt')
    marker='# Age 7 specialization choices'
    assert old.count(marker)==1
    tail=old[old.index(marker):]
    tail=tail.replace('# its ten choices at once; the others open when the paired institution is embraced (docs/tech_tree_age7.md).', '# its branches subject to prerequisites; other specializations open after the paired institution is embraced.')
    all_ages=[(5,'age_5_absolutism'),(6,'age_6_revolutions')]+[(r['number'],r['id']) for r in rows]
    triggers=['# GENERATED late-era continuity bridge. Other helpers below remain hand-maintained.']
    for number,id in all_ages:
        prefix='TRY_REPLACE:' if number in [5,6] else ''
        triggers += [f'{prefix}current_later_{id}_trigger = {{','\tcustom_tooltip = {',f'\t\ttext = current_age_at_least_{number}_tt','\t\tOR = {']
        triggers += [f'\t\t\tcurrent_age = {other}' for n,other in all_ages if n>=number]
        triggers += ['\t\t}','\t}','}']
    result['in_game/common/scripted_triggers/tsin_age_triggers.txt']='\n'.join(triggers)+'\n\n'+tail
    for row in rows[1:]:
        for lang in loc:
            # Prefer $age_format_$ over ShowAgeName — loading tips / early GUI can show ERROR for Show*.
            value=f"Current [age|e] is $age_format_{row['id']}$ or later" if lang=='english' else f"현재 [age|e]가 $age_format_{row['id']}$ 또는 그 이후임"
            loc[lang].append(f' current_age_at_least_{row["number"]}_tt: {json.dumps(value,ensure_ascii=False)}')
    for lang,lines in loc.items(): result[f'main_menu/localization/{lang}/tsin_future_ages_l_{lang}.yml']='\n'.join(lines)+'\n'
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    output=build(pdx.MOD_ROOT,json.loads(pdx.read_text(pdx.MOD_ROOT/REGISTRY)))
    errors=[]
    for rel,data in output.items():
        p=pdx.MOD_ROOT/rel
        if args.check:
            if not p.exists() or (p.read_bytes()!=data if isinstance(data,bytes) else pdx.read_text(p)!=data): errors.append(rel)
        else:
            p.parent.mkdir(parents=True,exist_ok=True)
            if isinstance(data,bytes):pdx.write_bytes(p,data)
            else:pdx.write_text_bom(p,data)
    for rel in errors:print('OUTDATED',rel)
    print(f'{len(output)} generated era files; {len(errors)} mismatches')
    return bool(errors)


if __name__=='__main__':raise SystemExit(main())
