"""Execute the generated numeric subset, not a second copy of its formulae."""
from pathlib import Path
import sys
import unittest
from decimal import Decimal as D
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_finance_ledger import build, EXTRA_TABS
from test_capital_markets import parse, get


class LedgerFixture:
    def __init__(self):
        self.modifiers=set()
        files=build()
        def blocks(s):return {b.key:parse(b.text[b.text.index('{')+1:-1]) for b in pdx.top_level_blocks(s)}
        self.values=blocks(files['in_game/common/script_values/tsin_finance_ledger_values.txt'])
        self.effects=blocks(files['in_game/common/scripted_effects/tsin_finance_ledger_effects.txt'])
        self.actions=blocks(files['in_game/common/scripted_guis/tsin_finance_ledger_guis.txt'])
        self.state={'gold':D(1000),'tsin_gold_cost_1':D(100),'tsin_company_count':D(1),'estate':D(0)}
        self.run(self.effects['tsin_ledger_init_effect'])

    def num(self,value):
        if isinstance(value,list):
            n=D(0)
            for key,_,v in value:
                if key=='save_temporary_value_as':
                    self.state['scope:'+get(v,'name')]=self.num(get(v,'value'))
                    continue
                if key=='if':
                    if self.valid(get(v,'limit')):n=self.num([('value','=',str(n))]+[r for r in v if r[0]!='limit'])
                    continue
                x=self.num(v)
                if key=='value':n=x
                elif key=='add':n+=x
                elif key=='subtract':n-=x
                elif key=='multiply':n*=x
                elif key=='divide':n/=x
                elif key=='min':n=max(n,x)
                elif key=='max':n=min(n,x)
                else:raise AssertionError(key)
            return n
        value=value.removeprefix('root.')
        if value=='estate_gold':return self.state['estate']
        if value in self.values:return self.num(self.values[value])
        try:return D(value)
        except Exception:return self.state.get(value.removeprefix('var:').removeprefix('root.'),D(0))

    def valid(self,rows):
        def term(k,op,v):
            if k=='NOT':return not self.valid(v)
            if k=='AND':return self.valid(v)
            if k=='OR':return any(term(*r) for r in v)
            if k=='has_variable':return v in self.state
            if k=='is_ai':return False
            if k=='country_has_estate':return True
            if k=='has_policy':return False
            if k=='any_estate':return self.valid(v)
            a,b=self.num(k),self.num(v)
            return {'=':a==b,'<':a<b,'>':a>b,'>=':a>=b,'<=':a<=b}[op]
        return all(term(*r) for r in rows)

    def run(self,rows):
        previous_if=False
        for key,_,value in rows:
            if key=='if':
                previous_if=self.valid(get(value,'limit'))
                if previous_if:self.run([r for r in value if r[0]!='limit'])
            elif key=='else':
                if not previous_if:self.run(value)
            elif key=='set_variable':
                if isinstance(value,str):self.state[value]=D(1)
                else:self.state[get(value,'name')]=self.num(next((v for k,_,v in value if k=='value'),'1'))
            elif key=='change_variable':
                name=get(value,'name');op,v=next((k,v) for k,_,v in value if k!='name');x=self.num(v)
                self.state[name]={'add':lambda a:a+x,'subtract':lambda a:a-x,'multiply':lambda a:a*x,'divide':lambda a:a/x}[op](self.state[name])
            elif key=='remove_variable':self.state.pop(value,None)
            elif key=='remove_country_modifier':self.modifiers.discard(value)
            elif key=='add_country_modifier':self.modifiers.add(get(value,'modifier'))
            elif key=='add_gold':self.state['gold']+=self.num(value)
            elif key=='add_gold_to_estate':self.state['estate']+=self.num(get(value,'value'))
            elif key in self.effects:self.run(self.effects[key])
            else:raise AssertionError('Unsupported effect '+key)

    def action(self,name):
        body=self.actions['tsin_ledger_'+name]
        if not self.valid(get(body,'is_valid')):return False
        self.run(get(body,'effect'));return True

    def total(self):
        return sum(self.state.get(k,D(0)) for k in ['gold','estate','tsin_reserve','tsin_bank_cash','tsin_firm_cash','tsin_pension','tsin_insurance'])


class FinanceLedgerTests(unittest.TestCase):
    def test_legacy_initialization_does_not_endow_or_reset_balances(self):
        f=LedgerFixture();f.state['tsin_bank_cash']=D(123)
        f.run(f.effects['tsin_ledger_init_effect']);self.assertEqual(f.total(),1123)
        self.assertEqual(f.state['tsin_bank_cash'],123)

    def test_funded_lending_repayment_and_interest_conserve_cash(self):
        f=LedgerFixture();self.assertTrue(f.action('bank'));self.assertTrue(f.action('lend'))
        self.assertEqual(f.state['tsin_firm_debt'],100)
        f.run(f.effects['tsin_ledger_month_effect']);self.assertGreater(f.state['tsin_interest_paid'],0)
        self.assertTrue(f.action('repay'));self.assertEqual(f.total(),1000)
        self.assertGreater(f.state['tsin_firm_debt'],0) # interest has consumed part of repayment cash

    def test_zero_liquidity_cannot_create_a_loan_or_dividend(self):
        f=LedgerFixture();self.assertFalse(f.action('lend'));self.assertFalse(f.action('dividend'))
        self.assertEqual(f.total(),1000)

    def test_denominations_never_multiply_actual_assets(self):
        f=LedgerFixture();f.action('devalue');self.assertEqual(f.state['tsin_fx'],D('1.10'))
        f.state['tsin_fx']=D(100);f.state.pop('tsin_reform_cooldown');f.action('redenominate')
        self.assertEqual(f.state['tsin_fx'],10);self.assertEqual(f.total(),1000)

    def test_pension_exhaustion_stops_without_negative_funds(self):
        f=LedgerFixture();f.action('pension');f.action('pension_on')
        for _ in range(30):f.run(f.effects['tsin_ledger_month_effect'])
        self.assertEqual(f.state['tsin_pension'],0);self.assertEqual(f.state['estate'],100)
        self.assertEqual(f.total(),1000)

    def test_insurance_cannot_repeat_claim_within_same_arrears_episode(self):
        f=LedgerFixture();f.action('insurance');f.state['tsin_firm_debt']=D(1000000)
        for _ in range(20):f.run(f.effects['tsin_ledger_month_effect'])
        self.assertEqual(f.state['tsin_insurance'],75);self.assertEqual(f.total(),1000)

    def test_every_new_panel_and_action_has_ui_wiring(self):
        self.modifiers=set()
        files=build();ui=files['in_game/gui/tsin_finance_ledger.gui']
        for _,tab in EXTRA_TABS:self.assertIn('type '+tab+'_panel',ui)
        fixture=LedgerFixture()
        for action in fixture.actions:self.assertIn("GetScriptedGui('"+action+"').Execute",ui)
        self.assertNotIn('every_owned_location',str(files));self.assertNotIn('GetTotalDebt',str(files))


if __name__=='__main__':unittest.main()
