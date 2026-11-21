from pathlib import Path
import json,re,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_era_skeleton import build,validate

class EraScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.root=pdx.MOD_ROOT
        self.data=json.loads(pdx.read_text(self.root/'data/eras.json'))

    def test_future_eras_keep_baseline_rules_and_do_not_add_content(self):
        outputs=build(self.root,self.data)
        baseline=pdx.top_level_blocks(pdx.read_text(self.root/'in_game/common/age/tsin_age_7.txt'))[0].text
        expected=baseline[baseline.index('{'):]
        future=pdx.top_level_blocks(outputs['in_game/common/age/zz_tsin_future_ages.txt'])
        self.assertEqual([b.key for b in future],[r['id'] for r in self.data['eras'][1:]])
        for block,row in zip(future,self.data['eras'][1:]):
            body=block.text[block.text.index('{'):]
            body=re.sub(r'\byear\s*=\s*'+str(row['start_year'])+r'\b','year = 1837',body,count=1)
            self.assertEqual(body,expected)
        self.assertFalse(any(k.startswith(('in_game/events/','in_game/common/advances/','in_game/common/institution/')) for k in outputs))

    def test_later_age_bridge_includes_exactly_the_right_eras(self):
        outputs=build(self.root,self.data)
        text=outputs['in_game/common/scripted_triggers/tsin_age_triggers.txt']
        blocks={b.key.split(':')[-1]:b.text for b in pdx.top_level_blocks(text)}
        eras=[(5,'age_5_absolutism'),(6,'age_6_revolutions')]+[(r['number'],r['id']) for r in self.data['eras']]
        for number,id in eras:
            actual=set(re.findall(r'\bcurrent_age\s*=\s*(\w+)',blocks['current_later_'+id+'_trigger']))
            self.assertEqual(actual,{key for n,key in eras if n>=number})

    def test_placeholder_assets_are_exact_copies(self):
        outputs=build(self.root,self.data)
        for row in self.data['eras'][1:]:
            for sub in ['icons/age','illustrations/advances']:
                original=(self.root/f'main_menu/gfx/interface/{sub}/age_7_industrialization.dds').read_bytes()
                self.assertEqual(outputs[f'main_menu/gfx/interface/{sub}/{row["id"]}.dds'],original)

    def test_invalid_timeline_is_rejected(self):
        self.data['eras'][2]['start_year']=1900
        with self.assertRaises(ValueError):validate(self.data)

if __name__=='__main__':unittest.main()
