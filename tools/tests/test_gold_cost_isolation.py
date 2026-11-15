from pathlib import Path
import sys,unittest
from decimal import Decimal as D
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from test_finance_ledger import LedgerFixture
from test_capital_markets import parse
from gen_capital_markets import build


class NativeCostFixture(LedgerFixture):
    def __init__(self):
        super().__init__()
        for rel in ['in_game/common/script_values/zzzz_tsin_capital_values.txt','in_game/common/script_values/tsin_event_values.txt']:
            text=pdx.read_text(pdx.MOD_ROOT/rel)
            for b in pdx.top_level_blocks(text):self.values[b.key.split(':')[-1]]=parse(b.text[b.text.index('{')+1:-1])
        native=pdx.read_text(pdx.game_root()/'in_game/common/script_values/scaled_gold.txt')
        body=next(b.text for b in pdx.top_level_blocks(native) if b.key=='scaled_gold_for_effect')
        self.values['native_cost']=parse(body[body.index('{')+1:-1])
        self.state.pop('tsin_gold_cost_1',None)
    def valid(self,rows):
        for key,op,value in rows:
            if key=='exists':
                if value not in self.state:return False
            elif not super().valid([(key,op,value)]):return False
        return True


class GoldCostIsolationTests(unittest.TestCase):
    def test_positive_costs_match_native_expenses_and_ignore_stale_signed_scale(self):
        f=NativeCostFixture()
        for wealth,base in [(0,0),(10,100),(1000,10000),(1000000,1000000),(-100,-100)]:
            f.state.update(capital_wealth=D(wealth),country_economical_base=D(base))
            for n in [1,2,3,4]:
                f.state['scope:scale']=D(-n);actual=abs(f.num('native_cost'))
                self.assertEqual(f.num('tsin_gold_cost_'+str(n)),actual,(wealth,base,n))
                self.assertGreaterEqual(f.num('tsin_gold_cost_'+str(n)),n)
                f.state['scope:scale']=D(10)
                self.assertEqual(f.num('tsin_gold_cost_'+str(n)),actual)

    def test_generated_cost_unit_has_no_temporary_value_dependencies(self):
        text=build()['in_game/common/script_values/zzzz_tsin_capital_values.txt']
        blocks={b.key:b.text for b in pdx.top_level_blocks(text)}
        self.assertIn('tsin_gold_cost_unit',blocks)
        self.assertNotIn('scope:scale',blocks['tsin_gold_cost_unit'])
        self.assertNotIn('save_temporary',blocks['tsin_gold_cost_unit'])


if __name__=='__main__':unittest.main()
