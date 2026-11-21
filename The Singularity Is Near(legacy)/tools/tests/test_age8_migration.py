from pathlib import Path
import hashlib,json,re,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx,era_layout


class AgeEightMigrationTests(unittest.TestCase):
    def test_research_ids_prerequisites_and_effects_survive_migration(self):
        data=json.loads((pdx.MOD_ROOT/'data/age8_advance_migration.json').read_text(encoding='utf-8'))
        old={b.key:b.text for b in pdx.top_level_blocks(pdx.read_text(pdx.MOD_ROOT/data['source']))}
        new={b.key:b.text for b in pdx.top_level_blocks(pdx.read_text(pdx.MOD_ROOT/data['destination']))}
        self.assertEqual(set(new),set(data['retained_ids'])|set(data['new_ids']))
        for id,expected in data['kept_era7'].items():
            normalized=re.sub(r'\s+','',pdx.strip_comments(old[id]))
            self.assertEqual(hashlib.sha256(normalized.encode()).hexdigest(),expected)
        for id,expected in data['retained_ids'].items():
            self.assertNotIn(id,old);self.assertIn('age = age_8_world_wars',new[id])
            restored=new[id].replace('age = age_8_world_wars','age = age_7_industrialization')
            normalized=re.sub(r'\s+','',pdx.strip_comments(restored))
            self.assertEqual(hashlib.sha256(normalized.encode()).hexdigest(),expected)
        source,runtime,_=era_layout.entries()[data['destination']]
        self.assertEqual(source,pdx.MOD_ROOT/'era_8'/data['destination'])
        self.assertEqual(source.read_bytes(),runtime.read_bytes())


if __name__=='__main__':unittest.main()
