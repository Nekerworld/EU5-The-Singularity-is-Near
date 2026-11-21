from pathlib import Path
from decimal import Decimal as D
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from test_finance_contracts import ContractFixture
from finance_succession import BALANCES


class FinanceSuccessionTests(unittest.TestCase):
    def pair(self):
        f=ContractFixture();a=f.country(gold=D(100));b=f.country(gold=D(70))
        for country,scale in [(a,1),(b,2)]:
            for i,field in enumerate(BALANCES):country[field]=D((i+1)*scale)
        return f,a,b

    def test_state_cash_private_assets_and_liabilities_transfer_together_once(self):
        f,a,b=self.pair();sums={k:a[k]+b[k] for k in BALANCES};cash=a['gold']+b['gold']
        f.annex('prepare',a,b)
        self.assertEqual(a['gold'],100);self.assertEqual(b['gold'],0)
        self.assertEqual(a['tsin_bank_cash'],2)
        f.annex('prepare',a,b) # repeated prepare must not erase escrow
        b['num_locations']=D(0)
        f.annex('finish',a,b);f.annex('finish',a,b)
        self.assertEqual(a['gold'],cash)
        self.assertEqual(a['tsin_finance_annex_commits'],1)
        for field,total in sums.items():
            self.assertEqual(a[field],total,field)
            self.assertEqual(b[field],0,field)
        self.assertFalse(f.lists['tsin_annex_pending'])

    def test_native_sovereign_debt_and_lender_claim_retain_same_loan_and_terms(self):
        f,a,b=self.pair();c=f.country()
        borrowed=f.native_loan(b,c,177,7,31)
        lent=f.native_loan(c,b,81,3,9)
        f.annex('prepare',a,b)
        self.assertIs(borrowed['borrower'],a);self.assertIs(lent['owner'],a)
        b['num_locations']=D(0);f.annex('finish',a,b)
        self.assertEqual((borrowed['remaining_debt'],borrowed['rate'],borrowed['months']),(177,7,31))
        self.assertEqual((lent['remaining_debt'],lent['rate'],lent['months']),(81,3,9))
        self.assertEqual(len(f.native_loans),2)
        self.assertFalse(f.lists['tsin_annex_native_loans'])

    def test_cancelled_preparation_restores_escrow_and_native_roles_without_account_copy(self):
        f,a,b=self.pair();c=f.country();loan=f.native_loan(b,c)
        before={k:(a[k],b[k]) for k in BALANCES}
        f.annex('prepare',a,b)
        f.annex('finish',a,b) # target still owns land: abort our preparation
        self.assertEqual((a['gold'],b['gold']),(100,70));self.assertIs(loan['borrower'],b)
        for k,values in before.items():self.assertEqual((a[k],b[k]),values,k)

    def test_missed_post_callback_can_commit_or_restore_on_next_month(self):
        for was_annexed in [False,True]:
            f,a,b=self.pair();f.annex('prepare',a,b)
            if was_annexed:b['num_locations']=D(0)
            f.month+=1;f.effect('tsin_finance_annex_recover_effect',a)
            self.assertEqual(a['gold'],170 if was_annexed else 100)
            self.assertEqual(b['gold'],0 if was_annexed else 70)
            f.effect('tsin_finance_annex_recover_effect',a)
            self.assertEqual(a['gold'],170 if was_annexed else 100)

    def test_negative_treasury_is_not_forgiven(self):
        f,a,b=self.pair();b['gold']=D(-35)
        f.annex('prepare',a,b);b['num_locations']=D(0);f.annex('finish',a,b)
        self.assertEqual(a['gold'],65)

    def test_inherited_foreign_contracts_keep_rates_dates_currency_and_counterparties(self):
        f=ContractFixture();a=f.country(tsin_bank_cash=D(600));b=f.country(tsin_bank_cash=D(600),tsin_rate=D(9));c=f.country(eligible=True,tsin_fx=D(2))
        f.effect('tsin_contract_open_foreign_effect',a,MONTHS='12',PREMIUM='0')
        f.effect('tsin_contract_open_foreign_effect',b,MONTHS='60',PREMIUM='2')
        before=[dict(f.row(i)) for i in [1,2]]
        f.annex('prepare',a,b);b['num_locations']=D(0);f.annex('finish',a,b)
        for i,old in zip([1,2],before):
            new=f.row(i)
            for field in ['rate','maturity','principal','next_coupon','period','missed','currency']:self.assertEqual(new[field],old[field],field)
            self.assertIs(new['lender'],a);self.assertIs(new['borrower'],c)
        self.assertEqual(a['tsin_foreign_contract_count'],2)
        f.annex('prepare',a,c);c['num_locations']=D(0);c.pop('tsin_fx');f.annex('finish',a,c)
        for i in [1,2]:
            self.assertIs(f.row(i)['borrower'],a)
            self.assertEqual(f.row(i)['fx'],2)
            self.assertEqual(f.row(i)['currency_live'],0)

    def test_domestic_rates_and_old_bond_timer_do_not_merge_into_recipient_terms(self):
        f=ContractFixture();a=f.country(tsin_firm_debt=D(50),tsin_rate=D(3));b=f.country(tsin_firm_debt=D(80),tsin_rate=D(11),tsin_bond_principal=D(30),tsin_bond_maturity=D(1))
        f.annex('prepare',a,b)
        rows=[f.row(i) for i in f.lists['tsin_active_contracts']]
        self.assertEqual(sorted(row['rate'] for row in rows if row['kind']==2),[3,11])
        b['num_locations']=D(0);f.annex('finish',a,b)
        self.assertEqual(a['tsin_firm_debt'],130);self.assertEqual(a['tsin_bond_principal'],30)
        row=next(f.row(i) for i in f.lists['tsin_active_contracts'] if f.row(i)['kind']==3)
        self.assertIs(row['timer_origin'],b);self.assertEqual(row['maturity_mode'],1)
        self.assertIn('tsin_bond_maturity',b)

    def test_lost_legacy_expiry_is_reported_not_replaced_with_a_fabricated_date(self):
        f=ContractFixture();a=f.country();b=f.country(tsin_bond_principal=D(30),tsin_bond_maturity=D(1))
        f.annex('prepare',a,b);b['num_locations']=D(0);b.pop('tsin_bond_maturity')
        f.annex('finish',a,b)
        self.assertEqual(f.row(1)['maturity_mode'],2)
        self.assertEqual(a['tsin_unknown_legacy_maturities'],1)
        self.assertEqual(a['tsin_bond_principal'],30)

    def test_nested_preparations_use_distinct_native_loan_snapshots(self):
        f=ContractFixture();a=f.country();b=f.country();c=f.country();d=f.country()
        loan=f.native_loan(b,d)
        f.annex('prepare',a,b);b['num_locations']=D(0) # intentionally suppress B's post hook
        f.annex('prepare',c,a)
        self.assertEqual(len(f.lists['tsin_annex_native_loans']),2)
        a['num_locations']=D(0);f.annex('finish',c,a)
        f.month+=1;f.effect('tsin_finance_annex_recover_effect',c)
        self.assertIs(loan['borrower'],c)
        self.assertFalse(f.lists['tsin_annex_pending'])
        self.assertFalse(f.lists['tsin_annex_native_loans'])

    def test_closing_inherited_bank_does_not_force_all_recipient_deposits_to_close(self):
        f=ContractFixture();a=f.country(tsin_deposits=D(100),tsin_withdrawal_due=D(0),tsin_bank_open=D(1))
        b=f.country(tsin_deposits=D(80),tsin_withdrawal_due=D(10),tsin_bank_winding_down=D(1))
        f.annex('prepare',a,b);b['num_locations']=D(0);f.annex('finish',a,b)
        self.assertEqual(a['tsin_deposits'],180)
        self.assertEqual(a['tsin_withdrawal_due'],80)
        self.assertIn('tsin_bank_open',a)
        self.assertNotIn('tsin_bank_winding_down',a)

    def test_internalized_credit_remains_a_bank_claim_and_company_liability(self):
        f=ContractFixture();a=f.country(tsin_bank_cash=D(300));b=f.country(eligible=True)
        f.effect('tsin_contract_open_foreign_effect',a,MONTHS='60',PREMIUM='0')
        f.annex('prepare',a,b);b['num_locations']=D(0);f.annex('finish',a,b)
        f.month+=3;f.effect('tsin_contract_month_effect',a)
        self.assertEqual(f.row(1)['principal'],100)
        self.assertEqual(a['tsin_bank_cash'],201)
        self.assertEqual(a['tsin_firm_cash'],99)
        self.assertEqual(a['tsin_foreign_liability_local'],100)

    def test_unknown_legacy_maturity_can_only_be_repaired_explicitly_by_its_borrower(self):
        f=ContractFixture();a=f.country();b=f.country(tsin_bond_principal=D(30),tsin_bond_maturity=D(1));other=f.country()
        f.annex('prepare',a,b);b['num_locations']=D(0);b.pop('tsin_bond_maturity');f.annex('finish',a,b)
        self.assertEqual(a['tsin_unknown_maturity_contract_id'],1)
        f.effect('tsin_contract_restore_legacy_maturity_effect',other,ID='1',YEAR='1852',MONTH='7')
        self.assertEqual(f.row(1)['maturity_mode'],2)
        f.effect('tsin_contract_restore_legacy_maturity_effect',a,ID='1',YEAR='1852',MONTH='13')
        self.assertEqual(f.row(1)['maturity_mode'],2)
        cash=a['gold']+a['tsin_firm_cash']+a['tsin_bank_cash']
        f.effect('tsin_contract_restore_legacy_maturity_effect',a,ID='1',YEAR='1852',MONTH='7')
        self.assertEqual(f.row(1)['maturity_mode'],0)
        self.assertEqual(f.row(1)['maturity'],1852*12+7)
        self.assertEqual(a['tsin_unknown_legacy_maturities'],0)
        self.assertEqual(a['gold']+a['tsin_firm_cash']+a['tsin_bank_cash'],cash)


if __name__=='__main__':unittest.main()
