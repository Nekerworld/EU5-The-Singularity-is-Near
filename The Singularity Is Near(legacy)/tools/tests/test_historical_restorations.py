from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_historical_restorations import build,roles
from gen_historical_nations import build as formations
from test_capital_markets import parse
from test_lucky_nations import SafetyFixture


class RestorationFixture(SafetyFixture):
    def __init__(self,row):
        super().__init__();self.row=row;self.year=row['fallback']
        self.locations={c:dict(owner=self.foreign,controller=self.foreign,is_ownable=True,population=1,is_capital=False,is_historical_capital=False,dominant_culture={'has_culture_group':'culture_group:'+row['groups'][0]}) for c in row['cores']}
        for loc in self.locations.values():loc['dominant_religion.group']='religion_group:muslim'
        self.foreign['culture']={'has_culture_group':'culture_group:'+('german_group' if row['id']=='russia' else row['groups'][0])}
        self.foreign['num_locations']=len(row['cores'])+1
        for rel,text in {**formations(),**build()}.items():
            if '/scripted_triggers/' in rel:
                for b in pdx.top_level_blocks(text):self.definitions[b.key]=parse(b.text[b.text.index('{')+1:-1])
    def resolve(self,key,obj,prev):
        if key=='tsin_restore_'+self.row['id']+'_outgoing':return sum(loc['owner'] is obj for loc in self.locations.values())
        return super().resolve(key,obj,prev)
    def allowed(self):return self.evaluate(self.definitions['tsin_restore_'+self.row['id']+'_trigger'],self.candidate)


class HistoricalRestorationTests(unittest.TestCase):
    def test_restoration_requires_absent_actors_and_protected_peaceful_core(self):
        for row in roles():
            f=RestorationFixture(row);self.assertTrue(f.allowed(),row['id'])
            for core in row['cores']:
                loc=f.locations[core]
                for field in ['owner','controller']:
                    for realm in [f.human,f.subject]:
                        original=loc[field];loc[field]=realm;self.assertFalse(f.allowed(),(row['id'],core,field));loc[field]=original
            next(iter(f.locations.values()))['is_historical_capital']=True;self.assertTrue(f.allowed(),'Historical core capitals may be restored after annexation')
            f.globals={'tsin_restore_'+row['id']+'_count':2};self.assertFalse(f.allowed())
            f.globals={'tsin_restore_'+row['id']+'_next':f.year+1};self.assertFalse(f.allowed());f.globals={}
            f.foreign['num_locations']=len(row['cores']);self.assertFalse(f.allowed())
            f.foreign['num_locations']=len(row['cores'])+1
            next(iter(f.locations.values()))['is_capital']=True;self.assertFalse(f.allowed())

    def test_restoration_never_runs_under_assistance_mode_or_before_fallback(self):
        for row in roles():
            f=RestorationFixture(row);f.rules={'tsin_lucky_nations_assisted'};self.assertFalse(f.allowed())
            f.rules={'tsin_lucky_nations_force'};f.year=row['fallback']-1;self.assertFalse(f.allowed())

    def test_creation_and_optional_province_moves_are_guarded_and_non_annexing(self):
        files=build();effects=files['in_game/common/scripted_effects/tsin_restoration_effects.txt']
        blocks={b.key:b.text for b in pdx.top_level_blocks(effects)}
        for row in roles():
            p='tsin_restore_'+row['id'];body=blocks[p+'_effect']
            self.assertLess(body.index(p+'_trigger = yes'),body.index('create_country_from_location'))
            self.assertIn('owner ?= scope:'+p+'_sponsor controller = owner is_capital = no',body)
            self.assertIn('num_locations > 1',body)
            self.assertIn('years = 5 mode = replace',body)
        self.assertNotIn('annex_country',effects);self.assertNotIn('destroy_army',effects)
        self.assertNotIn('declare_war',effects)


if __name__=='__main__':unittest.main()
