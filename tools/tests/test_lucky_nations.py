from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_lucky_nations import build
from gen_historical_progression import build as diagnostics
from test_capital_markets import parse


class SafetyFixture:
    """Evaluate the generated *trigger subset* against adversarial ownership maps.

    This does not emulate formation or prove engine runtime behavior.
    Unknown clauses fail the test instead of silently passing.
    """
    def __init__(self):
        self.candidate=self.country('candidate')
        self.foreign=self.country('foreign')
        self.human=self.country('human',False)
        self.subject=self.country('subject',True,self.human)
        self.countries=[self.candidate,self.foreign,self.human,self.subject]
        self.locations={name:dict(owner=self.candidate,controller=self.candidate,is_capital=False) for name in ['moscow','novgorod','tver','vladimir']}
        self.year=1720;self.rules={'tsin_lucky_nations_force'}
        self.definitions={}
        for rel,text in {**diagnostics(),**build()}.items():
            if '/scripted_triggers/' in rel:
                for block in pdx.top_level_blocks(text):
                    self.definitions[block.key]=parse(block.text[block.text.index('{')+1:-1])
    @staticmethod
    def country(name,ai=True,overlord=None):
        return dict(name=name,is_ai=ai,top_overlord=overlord,is_subject=False,is_junior_partner=False,
                    culture={'has_culture_group':'culture_group:russian_group'},num_locations=10,at_war=False,enemies=[])
    def resolve(self,key,obj,prev):
        if key=='yes':return True
        if key=='no':return False
        if key=='prev':return prev
        if key=='this':return obj
        if key=='current_year':return self.year
        if key=='scope:tsin_lucky_candidate':return self.candidate
        if key=='tsin_lucky_russia_outgoing_count':return sum(loc['owner'] is obj for loc in self.locations.values())
        if key.startswith('location:'):
            name,*attrs=key[9:].split('.')
            value=self.locations[name]
            for attr in attrs:value=value.get(attr)
            return value
        try:return float(key)
        except ValueError:return obj.get(key,key)
    def evaluate(self,rows,obj,prev=None):
        def term(row):
            key,op,value=row
            if key=='OR':return any(term(r) for r in value)
            if key=='AND':return all(term(r) for r in value)
            if key=='NOT':return not all(term(r) for r in value)
            if key=='trigger_if':
                guard=next(v for k,o,v in value if k=='limit')
                return not self.evaluate(guard,obj,prev) or self.evaluate([r for r in value if r[0]!='limit'],obj,prev)
            if key in self.definitions:
                answer=self.evaluate(self.definitions[key],obj,prev)
                return answer==(value=='yes')
            if key=='any_country':return any(self.evaluate(value,country,obj) for country in self.countries)
            if key=='has_variable':return value in obj
            if key=='has_game_rule':return value in self.rules
            if key=='country_exists':return False # Russia is absent in these fixtures.
            if key=='owns':return self.locations[value[9:]]['owner'] is obj
            if key=='is_at_war_with':return self.resolve(value,obj,prev) in obj['enemies']
            if isinstance(value,list):
                target=self.resolve(key,obj,prev)
                if not isinstance(target,dict):return False
                return self.evaluate(value,target,obj)
            actual=self.resolve(key,obj,prev)
            expected=self.resolve(value,obj,prev)
            if op in ('=','?='):
                return actual is expected if isinstance(actual,dict) or isinstance(expected,dict) else actual==expected
            if op=='>':return actual>expected
            if op=='>=':return actual>=expected
            if op=='<':return actual<expected
            raise AssertionError('Unsupported safety clause '+str(row))
        return all(term(row) for row in rows)
    def allowed(self):return self.evaluate(self.definitions['tsin_lucky_russia_force_trigger'],self.candidate)


class LuckyNationTests(unittest.TestCase):
    def test_each_human_owned_or_occupied_required_city_vetoes_whole_formation(self):
        for city in ['moscow','novgorod','tver','vladimir']:
            for field in ['owner','controller']:
                for country in ['human','subject']:
                    f=SafetyFixture();f.locations[city][field]=getattr(f,country)
                    self.assertFalse(f.allowed(),(city,field,country))
        self.assertTrue(SafetyFixture().allowed())

    def test_assisted_mode_capitals_wars_and_collective_depletion_block_transfers(self):
        f=SafetyFixture();f.rules={'tsin_lucky_nations_assisted'};self.assertFalse(f.allowed())
        f=SafetyFixture();f.year=1699;self.assertFalse(f.allowed())
        f=SafetyFixture();f.candidate['at_war']=True;self.assertFalse(f.allowed())
        f=SafetyFixture();f.candidate['enemies']=[f.human];f.human['enemies']=[f.candidate];self.assertFalse(f.allowed())
        f=SafetyFixture();f.locations['tver'].update(owner=f.foreign,controller=f.foreign,is_capital=True);self.assertFalse(f.allowed())
        f=SafetyFixture()
        for name,loc in f.locations.items():
            if name!='moscow':loc.update(owner=f.foreign,controller=f.foreign)
        f.foreign['num_locations']=3
        self.assertFalse(f.allowed(),'Three outgoing cities cannot consume a three-location owner')
        f.foreign['num_locations']=4
        self.assertTrue(f.allowed())

    def test_ownership_effect_rechecks_full_guard_and_does_not_edit_hex(self):
        files=build();effects=files['in_game/common/scripted_effects/tsin_lucky_nations_effects.txt']
        block=next(b.text for b in pdx.top_level_blocks(effects) if b.key=='tsin_lucky_russia_form_effect')
        self.assertLess(block.index('tsin_lucky_russia_force_trigger = yes'),block.index('change_location_owner'))
        self.assertNotIn('annex_country',effects)
        self.assertNotIn('declare_war',effects)
        self.assertNotIn('modifier = hex_',effects)
        self.assertNotIn('set_variable = hex_',effects)
        actions=files['in_game/common/on_action/tsin_lucky_nations_on_actions.txt']
        self.assertIn('current_year > global_var:tsin_lucky_review_year',actions)
        self.assertIn('on_join_war',actions)
