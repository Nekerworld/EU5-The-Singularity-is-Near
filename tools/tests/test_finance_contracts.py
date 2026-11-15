"""Execute generated map/list effects with identity-preserving country scopes."""
from pathlib import Path
from decimal import Decimal as D
import re,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
import finance_contracts as contracts
from test_capital_markets import parse,get


class Entity(dict):
    __hash__ = object.__hash__
    def __eq__(self, other):return self is other
    def __ne__(self, other):return self is not other


class ContractFixture:
    def __init__(self):
        self.globals={};self.maps={};self.lists={};self.saved={};self.temp_lists={}
        self.native_loans=[];self.countries=[];self.state=None;self.previous=None;self.root=None
        self.year=D(1850);self.month=D(1)
        files=contracts.build()
        def blocks(text):return {b.key:parse(b.text[b.text.index('{')+1:-1]) for b in pdx.top_level_blocks(text)}
        self.effects=blocks(files['in_game/common/scripted_effects/tsin_finance_contract_effects.txt'])
        from finance_succession import build as succession
        self.effects.update(blocks(succession()['in_game/common/scripted_effects/tsin_finance_succession_effects.txt']))
        self.values=blocks(files['in_game/common/script_values/tsin_finance_contract_values.txt'])
        self.triggers=blocks(files['in_game/common/scripted_triggers/tsin_finance_contract_triggers.txt'])
        from gen_finance_ledger import build as ledger
        self.values.update(blocks(ledger()['in_game/common/script_values/tsin_finance_ledger_values.txt']))

    def country(self,**values):
        data=Entity({k:D(0) for k in ['gold','tsin_bank_cash','tsin_firm_cash','tsin_foreign_principal','tsin_foreign_local_principal','tsin_foreign_liability_local','tsin_bank_losses','tsin_foreign_contract_count','tsin_firm_debt','tsin_bond_principal','tsin_arrears','tsin_bond_arrears','tsin_interest_paid','tsin_bond_interest_paid','tsin_bond_losses']})
        data.update(tsin_fx=D(1),tsin_rate=D(4),tsin_ledger_lot=D(100),tsin_bank_lending_cash_required=D(100),tsin_bank_net_worth=D(100),num_locations=D(5),tsin_ledger_version=D(2))
        data.update(estate=D(1000),tsin_company_count=D(1),tsin_gold_cost_1=D(100))
        data.update(values);self.countries.append(data)
        if self.state is None:self.state=self.root=data
        return data

    def scope(self,value):
        text=value.strip('"')
        match=re.fullmatch(r'global_variable_map\((\w+)\|(.+)\)',text)
        if match:return self.maps.get(match[1],{}).get(self.scope(match[2]),D(0))
        if text.startswith('global_var:'):return self.globals.get(text[11:],D(0))
        if text in ['this','prev','root']:return {'this':self.state,'prev':self.previous,'root':self.root}[text]
        if text.startswith('scope:'):
            base,_,field=text[6:].partition('.')
            obj=self.saved.get(base)
            if not field:return obj
            return obj.get(field.removeprefix('var:'),D(0)) if isinstance(obj,dict) else D(0)
        if text.startswith('root.'):
            return self.root.get(text[5:].removeprefix('var:'),D(0))
        if text.startswith('var:'):return self.state.get(text[4:],D(0))
        if text=='estate_gold':return self.state['estate']
        if text=='current_year':return self.year
        if text=='current_month':return self.month
        if text in self.values:return self.num(self.values[text])
        try:return D(text)
        except Exception:
            if text in self.state:return self.state[text]
            raise AssertionError('Unsupported value '+text)

    def num(self,value):
        if not isinstance(value,list):return self.scope(value)
        n=D(0)
        for key,_,v in value:
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

    def valid(self,rows):
        def term(k,op,v):
            if k=='NOT':return not self.valid(v)
            if k=='AND':return self.valid(v)
            if k=='OR':return any(term(*r) for r in v)
            if k=='always':return v=='yes'
            if k=='country_has_estate':return self.state.get('has_burghers',True)
            if k=='estate_type':return v=='estate_type:burghers_estate'
            if k=='any_estate':return self.valid(v)
            if k in self.triggers:return self.valid(self.triggers[k])
            if k=='exists':return isinstance(self.scope(v),dict)
            if k=='is_target_in_global_variable_list':return self.scope(get(v,'target')) in self.lists.get(get(v,'name'),[])
            if k=='any_in_global_list':
                return any(self.enter(x,lambda:self.valid([r for r in v if r[0]!='variable'])) for x in self.lists.get(get(v,'variable'),[]))
            if k=='has_variable':return v in self.state
            if k=='has_global_variable_map':return v in self.maps
            if k=='has_global_variable':return v in self.globals
            if k=='tsin_foreign_recipient_trigger':return self.state is not self.saved.get('tsin_fc_lender') and self.state.get('eligible',False)
            if isinstance(v,list):
                obj=self.scope(k)
                return isinstance(obj,dict) and self.enter(obj,lambda:self.valid(v))
            a,b=self.scope(k),self.scope(v)
            if op in ['=','?=']:
                return a is b if isinstance(a,dict) or isinstance(b,dict) else a==b
            return {'!=':lambda:a!=b,'>':lambda:a>b,'<':lambda:a<b,'>=':lambda:a>=b,'<=':lambda:a<=b}[op]()
        return all(term(*r) for r in rows)

    def enter(self,obj,fn):
        old,prior=self.state,self.previous;self.state,self.previous=obj,old
        try:return fn()
        finally:self.state,self.previous=old,prior

    def run(self,rows,params=None):
        if params:
            def subst(value):
                if isinstance(value,list):return [(k,op,subst(v)) for k,op,v in value]
                if value.startswith('$') and value.endswith('$') and value[1:-1] in params:return params[value[1:-1]]
                for k,v in params.items():
                    if isinstance(v,str):value=value.replace('$'+k+'$',v)
                return value
            rows=subst(rows)
        previous_if=False
        for k,op,v in rows:
            if k=='if':
                previous_if=self.valid(get(v,'limit'))
                if previous_if:self.run([r for r in v if r[0]!='limit'])
            elif k=='else_if':
                if not previous_if:
                    previous_if=self.valid(get(v,'limit'))
                    if previous_if:self.run([r for r in v if r[0]!='limit'])
            elif k=='else':
                if not previous_if:self.run(v)
            elif k in ['set_global_variable','set_variable']:
                store=self.globals if k.startswith('set_global') else self.state
                if isinstance(v,str):store[v]=D(1)
                else:store[get(v,'name')]=self.num(next((val for key,_,val in v if key=='value'),'1'))
            elif k=='change_variable':
                name=get(v,'name');operation,val=next((key,val) for key,_,val in v if key!='name');x=self.num(val)
                store=self.state;old=store.get(name,D(0))
                store[name]={'add':lambda:old+x,'subtract':lambda:old-x,'divide':lambda:old/x,'multiply':lambda:old*x}[operation]()
            elif k=='add_gold':self.state['gold']+=self.num(v)
            elif k=='change_loan_borrower':self.state['borrower']=self.scope(v)
            elif k=='change_loan_owner':self.state['owner']=self.scope(v)
            elif k in ['every_loan','every_loan_lent_to_country']:
                selected=[loan for loan in self.native_loans if loan['borrower' if k=='every_loan' else 'owner'] is self.state]
                for loan in selected:
                    self.enter(loan,lambda:self.run([r for r in v if r[0]!='limit']) if self.valid(get(v,'limit')) else None)
            elif k=='add_gold_to_estate':self.state['estate']+=self.num(get(v,'value'))
            elif k=='remove_variable':self.state.pop(v,None)
            elif k=='save_scope_as':self.saved[v]=self.state
            elif k=='save_temporary_scope_value_as':self.saved[get(v,'name')]=self.num(get(v,'value'))
            elif k=='add_to_global_variable_map':self.maps.setdefault(get(v,'name'),{})[self.scope(get(v,'key'))]=self.num(get(v,'value'))
            elif k=='remove_from_global_variable_map':self.maps.get(get(v,'name'),{}).pop(self.scope(get(v,'key')),None)
            elif k=='add_to_global_variable_list':self.lists.setdefault(get(v,'name'),[]).append(self.scope(get(v,'target')))
            elif k=='remove_list_global_variable':self.lists[get(v,'name')].remove(self.scope(get(v,'target')))
            elif k=='add_to_list':self.temp_lists.setdefault(v,[]).append(self.state)
            elif k in ['every_in_global_list','every_in_list']:
                items=self.lists.get(get(v,'variable'),[]) if k=='every_in_global_list' else self.temp_lists.get(get(v,'list'),[])
                for item in list(items):self.enter(item,lambda:self.run([r for r in v if r[0] not in ['variable','list']]))
            elif k in ['every_country','ordered_country']:
                selected=[]
                for country in self.countries:
                    if self.enter(country,lambda:self.valid(get(v,'limit'))):selected.append(country)
                if k=='ordered_country':selected=sorted(selected,key=lambda c:c.get(get(v,'order_by'),0),reverse=True)[:int(self.num(get(v,'max'))) ]
                for country in selected:self.enter(country,lambda:self.run([r for r in v if r[0] not in ['limit','order_by','max']]))
            elif k=='tsin_ledger_init_effect':
                self.state.setdefault('tsin_ledger_version',D(2))
                for key in ['tsin_reserve','tsin_bank_cash','tsin_firm_cash','tsin_insurance','tsin_pension','tsin_deposits','tsin_withdrawal_due','tsin_liquidity_debt','tsin_public_shares','tsin_issued_shares','tsin_bank_losses','tsin_bond_losses']:self.state.setdefault(key,D(0))
            elif k in self.effects:self.run(self.effects[k],dict((key,val) for key,_,val in v) if isinstance(v,list) else None)
            elif isinstance(v,list) and (k.startswith('scope:') or k.startswith('var:') or k.startswith('"global_variable_map')):
                obj=self.scope(k)
                if isinstance(obj,dict):self.enter(obj,lambda:self.run(v))
                elif op!='?=':raise AssertionError('Invalid required scope '+k)
            else:raise AssertionError('Unsupported effect '+k)

    def effect(self,name,country=None,**params):
        self.temp_lists={}
        self.saved={}
        if country is not None:self.state=self.root=country
        self.run(self.effects[name],params)

    def annex(self,phase,recipient,target):
        self.temp_lists={};self.saved={'target':target}
        self.state=self.root=recipient
        self.run(self.effects['tsin_finance_annex_'+phase+'_effect'])

    def native_loan(self,borrower,owner,amount=100,rate=4,months=22):
        loan=Entity(borrower=borrower,owner=owner,remaining_debt=D(amount),rate=D(rate),months=D(months))
        self.native_loans.append(loan);return loan

    def row(self,id):return {f:self.maps['tsin_fc_'+f][D(id)] for f in contracts.FIELDS}


class ContractTests(unittest.TestCase):
    def setup_credit(self):
        f=ContractFixture();lender=f.country(tsin_bank_cash=D(1000));borrower=f.country(eligible=True)
        return f,lender,borrower

    def test_multiple_contracts_keep_distinct_rates_and_maturity_without_endowment(self):
        f,l,b=self.setup_credit();initial=l['tsin_bank_cash']+b['tsin_firm_cash']
        f.effect('tsin_contract_open_foreign_effect',l,MONTHS='12',PREMIUM='0')
        l.pop('tsin_foreign_cooldown');l['tsin_rate']=D(6)
        f.effect('tsin_contract_open_foreign_effect',l,MONTHS='60',PREMIUM='2')
        self.assertEqual([f.row(i)['rate'] for i in [1,2]],[4,8])
        self.assertEqual(f.row(2)['maturity']-f.row(1)['maturity'],48)
        self.assertEqual(l['tsin_bank_cash']+b['tsin_firm_cash'],initial)
        self.assertEqual(l['tsin_foreign_contract_count'],2)
        self.assertEqual(b['tsin_foreign_liability_local'],200)
        f.month=D(4);f.effect('tsin_contract_month_effect',l)
        self.assertEqual(l['tsin_bank_cash'],803)
        self.assertEqual(b['tsin_firm_cash'],197)
        f.effect('tsin_contract_month_effect',l)
        self.assertEqual(l['tsin_bank_cash'],803)

    def test_maturity_repayment_closes_only_that_contract(self):
        f,l,b=self.setup_credit()
        for term in ['12','60']:
            l.pop('tsin_foreign_cooldown',None)
            f.effect('tsin_contract_open_foreign_effect',l,MONTHS=term,PREMIUM='0')
        f.year+=1;b['tsin_firm_cash']=D(400)
        before=l['tsin_bank_cash']+b['tsin_firm_cash']
        f.effect('tsin_contract_month_effect',l)
        self.assertEqual(f.lists['tsin_active_contracts'],[2])
        self.assertEqual(f.row(2)['principal'],100)
        self.assertEqual(l['tsin_bank_cash']+b['tsin_firm_cash'],before)

    def test_legacy_migration_is_idempotent_and_preserves_principal_age_and_arrears(self):
        f,l,b=self.setup_credit()
        l.update(tsin_foreign_partner=b,tsin_foreign_local_principal=D(120),tsin_foreign_age=D(2),tsin_foreign_delinquency=D(3))
        before=l['tsin_bank_cash']+b['tsin_firm_cash']
        f.effect('tsin_contract_migrate_all_effect',l);f.effect('tsin_contract_migrate_all_effect',l)
        row=f.row(1)
        self.assertEqual(row['principal'],120);self.assertEqual(row['missed'],3)
        self.assertEqual(row['maturity'],f.year*12+f.month+6)
        self.assertEqual(f.lists['tsin_active_contracts'],[1])
        self.assertEqual(l['tsin_bank_cash']+b['tsin_firm_cash'],before)

    def test_currency_revaluation_and_redenomination_preserve_cash_and_real_claim(self):
        f,l,b=self.setup_credit();f.effect('tsin_contract_open_foreign_effect',l,MONTHS='60',PREMIUM='0')
        b['tsin_fx']=D(2);f.effect('tsin_contract_refresh_effect',l)
        self.assertEqual(l['tsin_foreign_principal'],50)
        b['tsin_fx']/=10
        before=l['tsin_bank_cash']+b['tsin_firm_cash']
        f.effect('tsin_contract_redenominate_effect',b)
        self.assertEqual(f.row(1)['principal'],10)
        self.assertEqual(l['tsin_foreign_principal'],50)
        self.assertEqual(l['tsin_bank_cash']+b['tsin_firm_cash'],before)

    def test_private_facilities_keep_each_origination_rate_and_repay_actual_cash(self):
        f=ContractFixture();c=f.country(tsin_bank_cash=D(400),tsin_rate=D(3))
        f.effect('tsin_contract_lend_facility_effect',c)
        c['tsin_rate']=D(9)
        f.effect('tsin_contract_lend_facility_effect',c)
        self.assertEqual([f.row(i)['rate'] for i in [1,2]],[3,9])
        f.month=D(2);f.effect('tsin_contract_month_effect',c)
        self.assertEqual(c['tsin_interest_paid'],1)
        self.assertEqual(c['tsin_bank_cash']+c['tsin_firm_cash'],400)
        f.effect('tsin_contract_repay_facility_effect',c)
        self.assertEqual(c['tsin_firm_debt'],1)
        self.assertEqual(c['tsin_firm_cash'],0)
        self.assertEqual(c['tsin_bank_cash'],400)

    def test_bond_maturity_and_estate_claim_survive_as_distinct_contract(self):
        f=ContractFixture();c=f.country()
        total=c['estate']+c['tsin_firm_cash']
        f.effect('tsin_contract_issue_bond_effect',c)
        self.assertEqual(f.row(1)['kind'],3)
        self.assertEqual(f.row(1)['maturity'],f.year*12+f.month+36)
        self.assertEqual(c['tsin_bond_principal'],100)
        self.assertEqual(c['estate']+c['tsin_firm_cash'],total)
        f.month+=1;f.effect('tsin_contract_month_effect',c)
        self.assertEqual(c['tsin_bond_interest_paid'],D(100)/300)
        self.assertEqual(c['estate']+c['tsin_firm_cash'],total)

    def test_legacy_bond_keeps_original_expiry_marker_without_resetting_36_months(self):
        f=ContractFixture();c=f.country(tsin_bond_principal=D(70),tsin_bond_maturity=D(1),tsin_firm_cash=D(100))
        f.effect('tsin_contract_migrate_all_effect',c)
        self.assertEqual(f.row(1)['maturity_mode'],1)
        self.assertIs(f.row(1)['timer_origin'],c)
        self.assertEqual(c['tsin_bond_maturity'],1)
        f.month+=1;f.effect('tsin_contract_month_effect',c)
        self.assertEqual(c['tsin_bond_principal'],70)
        c.pop('tsin_bond_maturity');f.month+=1;f.effect('tsin_contract_month_effect',c)
        self.assertEqual(c['tsin_bond_principal'],0)

    def test_private_writeoff_reduces_authoritative_principal_without_creating_cash(self):
        f=ContractFixture();c=f.country(tsin_bank_cash=D(300))
        f.effect('tsin_contract_lend_facility_effect',c)
        before=c['tsin_bank_cash']+c['tsin_firm_cash']
        f.effect('tsin_contract_adjust_private_effect',c,KIND='2',LOSS='yes',AMOUNT=[('value','=','25')])
        self.assertEqual(c['tsin_firm_debt'],75)
        self.assertEqual(c['tsin_bank_losses'],25)
        self.assertEqual(c['tsin_bank_cash']+c['tsin_firm_cash'],before)


if __name__=='__main__':unittest.main()
