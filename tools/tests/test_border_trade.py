from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_border_trade import build
from gen_ai_direction import build as direction,geography
from gen_historical_nations import registry
from test_capital_markets import parse,get
from test_lucky_nations import SafetyFixture


class TradeFixture(SafetyFixture):
    def __init__(self):
        super().__init__();self.seller=self.foreign;self.buyer=self.candidate
        self.seller.update(culture={'has_culture_group':'foreign'},**{'var:tsin_border_price':100,'has_primary_or_accepted_culture':False})
        self.buyer.update(gold=100,has_primary_or_accepted_culture=True)
        self.location=dict(owner=self.seller,controller=self.seller,neighbors=[],is_capital=False)
        self.neighbor=dict(owner=self.buyer,controller=self.buyer,is_connected_to=True)
        self.location['neighbors']=[self.neighbor]
        self.rules=set()
        for rel,text in build().items():
            if '/scripted_triggers/' in rel:
                for block in pdx.top_level_blocks(text):self.definitions[block.key]=parse(block.text[block.text.index('{')+1:-1])
    def resolve(self,key,obj,prev):
        if key.startswith('scope:'):
            name,*attrs=key.split('.')
            target={'scope:tsin_border_seller':self.seller,'scope:tsin_border_buyer':self.buyer,'scope:tsin_border_location':self.location}.get(name)
            if target is not None:
                for attr in attrs:target=target.get(attr)
                return target
        return super().resolve(key,obj,prev)
    def evaluate(self,rows,obj,prev=None):
        remaining=[]
        for key,op,value in rows:
            if key=='tsin_border_sale_location':
                # Strategic shortlist is tested separately; this fixture isolates
                # settlement races without emulating native geography/culture.
                if obj.get('eligible',True)!=(value=='yes'):return False
            elif key=='any_neighbor_location':
                if not any(self.evaluate(value,loc,obj) for loc in obj['neighbors']):return False
            elif key=='exists':
                if self.resolve(value,obj,prev) is None:return False
            elif key=='has_variable':
                if value not in obj:return False
            elif key=='has_primary_or_accepted_culture':
                if not obj.get(key,False):return False
            elif key=='is_connected_to':
                if not obj.get('is_connected_to',False):return False
            else:remaining.append((key,op,value))
        return super().evaluate(remaining,obj,prev)
    def allowed(self):return self.evaluate(self.definitions['tsin_border_sale_transaction'],self.seller)


class BorderTradeTests(unittest.TestCase):
    def test_settlement_requires_current_cash_owner_connection_and_ai_realms(self):
        f=TradeFixture();self.assertTrue(f.allowed())
        f.buyer['gold']=99;self.assertFalse(f.allowed());f.buyer['gold']=100
        f.location['owner']=f.human;self.assertFalse(f.allowed());f.location['owner']=f.seller
        f.buyer['is_ai']=False;self.assertFalse(f.allowed());f.buyer['is_ai']=True
        f.seller['top_overlord']=f.human;self.assertFalse(f.allowed());f.seller['top_overlord']=None
        f.neighbor['is_connected_to']=False;self.assertFalse(f.allowed());f.neighbor['is_connected_to']=True
        f.seller['hex_key']=1;self.assertFalse(f.allowed());f.seller.pop('hex_key')
        f.rules={'tsin_border_trade_off'};self.assertFalse(f.allowed())

    def test_strategic_retention_and_debit_credit_order_are_explicit(self):
        files=build();triggers=files['in_game/common/scripted_triggers/tsin_border_trade_triggers.txt']
        for text in ['is_core_of = owner','building_type:castle','building_type:fortress','has_primary_or_accepted_culture','has_variable = hex_key']:
            self.assertIn(text,triggers)
        for row in registry():
            for core in row['cores']:self.assertIn('this = location:'+core,triggers)
        effects=files['in_game/common/scripted_effects/tsin_border_trade_effects.txt']
        self.assertLess(effects.index('tsin_border_sale_transaction = yes'),effects.index('add_gold'))
        self.assertLess(effects.index('multiply = -1'),effects.index('add_gold = var:tsin_border_price'))
        self.assertLess(effects.index('add_gold = var:tsin_border_price'),effects.index('change_location_owner'))
        self.assertIn('name = tsin_border_review_cooldown years = 10',effects)

    def test_british_preferences_exclude_overseas_and_human_areas(self):
        files=direction();effects=files['in_game/common/scripted_effects/tsin_historical_direction_effects.txt']
        blocks=parse(effects)
        review=get(blocks,'tsin_direction_review_effect')
        britain=next(v for k,_,v in review if k=='if' and ('tag','=', 'GBR') in get(v,'limit'))
        _,areas=geography()
        selected=[k[5:] for k,_,v in britain if k.startswith('area:')]
        self.assertTrue(selected)
        self.assertTrue(all(areas[a] in {'great_britain_region','ireland_region'} for a in selected))
        self.assertIn('tsin_history_human_realm',str(britain))
        self.assertIn('NOT = { has_variable = hex_key }',files['in_game/common/on_action/tsin_historical_direction_on_actions.txt'])


if __name__=='__main__':unittest.main()
