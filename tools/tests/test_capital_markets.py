from pathlib import Path
import re,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_capital_markets import build,all_companies
from gen_historical_finance_bridge import build as history,TARGETS,patch_event


def parse(text):
    tokens=re.findall(r'>=|<=|!=|\?=|[{}=<>]|[^\s{}=<>?]+',pdx.strip_comments(text))
    def body(i):
        rows=[]
        while i<len(tokens) and tokens[i]!='}':
            key,op=tokens[i:i+2];i+=2
            if tokens[i]=='{':value,i=body(i+1)
            else:value=tokens[i];i+=1
            rows.append((key,op,value))
        return rows,i+1
    return body(0)[0]


def predicate(rows,context):
    def number(value):
        if isinstance(value,list):
            n=0
            for k,_,v in value:
                x=number(v)
                if k=='value':n=x
                elif k=='multiply':n*=x
                elif k=='add':n+=x
                else:raise AssertionError('unsupported numeric operation '+k)
            return n
        try:return float(value)
        except ValueError:return context.get(value,0)
    def term(row):
        key,op,value=row
        if key=='OR':return any(term(r) for r in value)
        if key=='AND':return predicate(value,context)
        if key=='NOT':return not predicate(value,context)
        if key in ('has_variable','has_global_variable'):return value in context.get('flags',set())
        if key=='has_policy':return value in context.get('policies',set())
        if key=='is_situation_active':return value in context.get('situations',set())
        a,b=number(key),number(value)
        return {'=':a==b,'>':a>b,'<':a<b,'>=':a>=b,'<=':a<=b}[op]
    return all(term(r) for r in rows)


def get(rows,key):return next(v for k,op,v in rows if k==key)


class CapitalMarketTests(unittest.TestCase):
    def setUp(self):
        self.files=build()
        self.effects={b.key.split(':')[-1]:parse(b.text[b.text.index('{')+1:-1]) for b in pdx.top_level_blocks(self.files['in_game/common/scripted_effects/zzzz_tsin_capital_effects.txt'])}

    def test_early_and_industrial_goods_and_art_are_real(self):
        rows=all_companies()
        self.assertEqual(len(rows),20)
        self.assertEqual(sum(r['kind']=='industrial' for r in rows),6)
        goods={b.key for root in [pdx.game_root(),pdx.MOD_ROOT] for p in (root/'in_game/common/goods').glob('*.txt') for b in pdx.top_level_blocks(pdx.read_text(p))}
        for row in rows:
            self.assertIn(row['good'],goods)
            for icon in [f'icons/trade_goods/icon_goods_{row["icon"]}.dds',f'icons/trade_goods/illustrations/icon_goods_{row["icon"]}.dds']:
                self.assertTrue(any((base/'main_menu/gfx/interface'/icon).exists() for base in [pdx.game_root(),pdx.MOD_ROOT]),icon)

    def test_private_regime_has_no_policy_cap_but_public_regimes_do(self):
        source=self.files['in_game/common/scripted_triggers/tsin_capital_triggers.txt']
        block=next(b for b in pdx.top_level_blocks(source) if b.key=='tsin_company_has_room_trigger')
        rule=parse(block.text[block.text.index('{')+1:-1])
        context={'tsin_company_count':10000,'tsin_company_limit':3,'policies':set()}
        self.assertFalse(predicate(rule,context))
        context['policies']={'policy:tsin_laissez_faire_policy'}
        self.assertTrue(predicate(rule,context))
        context.update(tsin_company_count=2,policies=set())
        self.assertTrue(predicate(rule,context))

    def test_local_crash_requires_sustained_evidence_and_respects_cooldown(self):
        limit=get(get(self.effects['tsin_stock_market_events_effect'],'if'),'limit')
        context={'var:tsin_entry_risk_quarters':2,'var:tsin_stress_quarters':3,'flags':set()}
        self.assertFalse(predicate(limit,context))
        context['var:tsin_entry_risk_quarters']=3
        self.assertTrue(predicate(limit,context))
        context['flags']={'tsin_local_crash_cooldown'}
        self.assertFalse(predicate(limit,context))
        context.update(flags=set(),**{'var:tsin_entry_risk_quarters':0,'var:tsin_stress_quarters':4})
        self.assertTrue(predicate(limit,context))
        raw=str(self.effects['tsin_stock_market_events_effect'])
        self.assertNotIn('random',raw)

    def test_global_crisis_never_starts_before_1900_and_needs_multiple_markets(self):
        outer=get(self.effects['tsin_systemic_finance_check_effect'],'if')
        gate=get(outer,'limit')
        self.assertFalse(predicate(gate,{'current_year':1899,'flags':set()}))
        self.assertTrue(predicate(gate,{'current_year':1900,'flags':set()}))
        ready=next(v for k,_,v in outer if k=='if' and 'tsin_systemic_crisis_cooldown' in str(v))
        limit=get(ready,'limit')
        ctx={'global_var:tsin_finance_countries':10,'global_var:tsin_stressed_countries':5,'global_var:tsin_stressed_markets':3,'flags':set()}
        self.assertTrue(predicate(limit,ctx))
        ctx['global_var:tsin_stressed_markets']=2
        self.assertFalse(predicate(limit,ctx))
        situation=self.files['in_game/common/situations/tsin_global_depression.txt']
        self.assertIn('on_ended =',situation)
        self.assertNotIn('on_end =',situation)
        ctx.update({'global_var:tsin_stressed_markets':3,'global_var:tsin_finance_countries':20})
        self.assertFalse(predicate(limit,ctx)) # 5/20 is below 35%.
        ctx.update({'global_var:tsin_finance_countries':10,'flags':{'tsin_systemic_crisis_cooldown'}})
        self.assertFalse(predicate(limit,ctx))

    def test_private_entry_is_estate_funded_and_scans_are_bounded(self):
        private=str(self.effects['tsin_private_company_entry_effect'])
        self.assertIn('estate_gold',private)
        self.assertIn('add_gold_to_estate',private)
        self.assertNotIn('change_gold_effect',private)
        self.assertNotIn('tsin_company_limit',private)
        whole=self.files['in_game/common/scripted_effects/zzzz_tsin_capital_effects.txt']
        self.assertNotIn('every_owned_location',whole)
        self.assertIn('name = tsin_market_stress_sample_timer months = 2',whole)
        hooks=self.files['in_game/common/on_action/tsin_capital_on_actions.txt']
        self.assertIn('name = tsin_capital_timer months = 3',hooks)
        self.assertIn('has_variable = tsin_stock_timer',hooks)

    def test_mississippi_local_cleanup_helper_is_carried_with_event(self):
        files=history()
        fra=files['in_game/events/DHE/zzzz_tsin_finance_flavor_fra.txt']
        definitions={b.key:b for b in pdx.top_level_blocks(fra)}
        self.assertEqual(definitions['remove_law_bank_modifiers'].local_kind,'scripted_effect')
        self.assertIn('remove_law_bank_modifiers',definitions['flavor_fra.511'].text)

    def test_historical_choices_and_costs_are_preserved(self):
        for key,(rel,company,factor) in TARGETS.items():
            source=pdx.read_text(pdx.game_root()/'in_game/events'/rel)
            original=next(b.text for b in pdx.top_level_blocks(source) if b.key==key)
            patched=patch_event(source,key,company,factor)
            restored=re.sub(r'\s*tsin_historic_finance_\w+_effect = \{ FACTOR = [\d.]+ \}\s*','',patched)
            self.assertEqual(re.sub(r'\s+','',restored),re.sub(r'\s+','',original))
            self.assertEqual(patched.count('tsin_historic_finance_'),original.count('option = {'))

    def test_three_standalone_windows_have_unique_engine_registrations(self):
        reg=pdx.read_text(pdx.MOD_ROOT/'in_game/gui/scripted_widgets/tsin_windows.txt')
        rows=re.findall(r'gui/(\S+)\s*=\s*(\w+)',reg)
        self.assertEqual(len(rows),3)
        self.assertEqual(len({r[0] for r in rows}),3)
        for path,name in rows:
            text=pdx.read_text(pdx.MOD_ROOT/'in_game/gui'/path)
            self.assertIn('name = "'+name+'"',text)
            self.assertIn('layer = topbar',text)


if __name__=='__main__':unittest.main()
