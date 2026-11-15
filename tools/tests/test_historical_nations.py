from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_historical_nations import build,registry
from test_capital_markets import parse
from test_lucky_nations import SafetyFixture


class NationFixture(SafetyFixture):
    def __init__(self,row):
        super().__init__();self.row=row
        self.locations={name:dict(owner=self.candidate,controller=self.candidate,is_capital=False,is_historical_capital=False) for name in row['cores']}
        self.candidate.update(num_locations=30,tag='ACT',**{'capital.region':'region:'+row['regions'][0],'religion.group':'religion_group:muslim','government_type':'government_type:monarchy'})
        self.candidate['culture']={'has_culture_group':'culture_group:'+row['groups'][0]}
        self.year=row['fallback']
        for rel,text in build().items():
            if '/scripted_triggers/' in rel:
                for b in pdx.top_level_blocks(text):self.definitions[b.key]=parse(b.text[b.text.index('{')+1:-1])
    def resolve(self,key,obj,prev):
        if key=='scope:tsin_nation_'+self.row['id']+'_candidate':return self.candidate
        if key=='tsin_nation_'+self.row['id']+'_outgoing':return sum(loc['owner'] is obj for loc in self.locations.values())
        return super().resolve(key,obj,prev)
    def allowed(self):return self.evaluate(self.definitions['tsin_nation_'+self.row['id']+'_force'],self.candidate)


class HistoricalNationTests(unittest.TestCase):
    def test_every_path_vetoes_each_human_or_subject_city_owner_and_controller(self):
        for row in registry():
            f=NationFixture(row);self.assertTrue(f.allowed(),row['id'])
            for core in row['cores']:
                for field in ['owner','controller']:
                    for realm in ['human','subject']:
                        loc=f.locations[core];old=loc[field];loc[field]=getattr(f,realm)
                        self.assertFalse(f.allowed(),(row['id'],core,field,realm));loc[field]=old

    def test_no_transfer_for_assisted_mode_wars_capitals_or_depleted_owners(self):
        for row in registry():
            f=NationFixture(row);f.rules={'tsin_lucky_nations_assisted'};self.assertFalse(f.allowed())
            f.rules={'tsin_lucky_nations_force'};f.candidate['at_war']=True;self.assertFalse(f.allowed());f.candidate['at_war']=False
            for loc in f.locations.values():loc.update(owner=f.foreign,controller=f.foreign)
            # Retain one core so the actor is still a valid consolidation candidate.
            first=next(iter(f.locations.values()));first.update(owner=f.candidate,controller=f.candidate)
            foreign=[loc for loc in f.locations.values() if loc['owner'] is f.foreign]
            if foreign:
                f.foreign['num_locations']=len(foreign);self.assertFalse(f.allowed())
                f.foreign['num_locations']=len(foreign)+1;self.assertTrue(f.allowed())
                foreign[0]['is_capital']=True;self.assertFalse(f.allowed())

    def test_britain_is_limited_to_isles_and_ireland_and_tags_do_not_collide(self):
        rows=registry();britain=next(r for r in rows if r['id']=='britain')
        self.assertEqual(set(britain['regions']),{'great_britain_region','ireland_region'})
        self.assertEqual(set(britain['cores']),{'london','edinburgh','dublin'})
        south=[r for r in rows if r.get('custom') and r['id']!='qing']
        self.assertTrue(all(r['tag'] not in {'BRA','ARG','PRU'} for r in south))
        self.assertTrue(all(r.get('colonial') and r['groups']==['iberian_group'] for r in south))
        self.assertEqual(next(r['tag'] for r in rows if r['id']=='romania'),'RMN')

    def test_force_effect_guards_precede_mutation_and_one_world_review_per_year(self):
        files=build();effects=files['in_game/common/scripted_effects/tsin_historical_nations_effects.txt']
        blocks={b.key:b.text for b in pdx.top_level_blocks(effects)}
        for row in registry():
            prefix='tsin_nation_'+row['id'];body=blocks[prefix+'_form']
            self.assertLess(body.index(prefix+'_force = yes'),body.index('change_location_owner'))
        self.assertNotIn('annex_country',effects);self.assertNotIn('declare_war',effects)
        hooks=files['in_game/common/on_action/tsin_historical_nations_on_actions.txt']
        self.assertIn('current_year > global_var:tsin_nations_review_year',hooks)
        self.assertNotIn('monthly',hooks)


if __name__=='__main__':unittest.main()
