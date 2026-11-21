import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import era_layout as layout
from sync_eras import register


class EraLayoutTests(unittest.TestCase):
    def fixture(self,root):
        rel='in_game/common/advances/tsin_test.txt'
        (root/'data').mkdir()
        (root/'data/content_modules.json').write_text(json.dumps({'schema_version':1,'modules':[{'folder':'era_7','era':7}]}),encoding='utf-8')
        source=root/'era_7'/rel
        source.parent.mkdir(parents=True)
        source.write_bytes(b'\xef\xbb\xbftsin_test = { age = age_7_industrialization }\n')
        (root/'era_7/manifest.json').write_text(json.dumps({'schema_version':1,'files':{rel:'advances'}}),encoding='utf-8')
        layout.entries.cache_clear()
        layout.update_ignore(root)
        return rel,source,root/rel

    def tearDown(self):layout.entries.cache_clear()

    def test_clean_checkout_deploys_exact_bytes_and_reports_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            rel,source,runtime=self.fixture(root)
            self.assertTrue(any('outdated runtime mirror' in s for s in layout.check(root)))
            self.assertEqual(layout.sync(root),1)
            self.assertEqual(layout.check(root),[])
            self.assertEqual(runtime.read_bytes(),source.read_bytes())
            self.assertEqual(layout.sync(root),0)
            runtime.write_text('unintended runtime edit',encoding='utf-8')
            self.assertTrue(any(rel in s for s in layout.check(root)))
            layout.sync(root)
            self.assertEqual(runtime.read_bytes(),source.read_bytes())

    def test_generator_writes_source_and_mirror_but_leaves_shared_external_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'mod'; root.mkdir()
            rel,source,runtime=self.fixture(root)
            layout.write_bytes(runtime,b'new content',root)
            self.assertEqual(source.read_bytes(),b'new content')
            self.assertEqual(runtime.read_bytes(),b'new content')
            layout.write_bytes(source,b'direct source edit',root)
            self.assertEqual(runtime.read_bytes(),b'direct source edit')
            shared=root/'in_game/gui/tsin_dashboard.gui'
            external=Path(tmp)/'compat/in_game/gui/test.gui'
            for path in [shared,external]:
                self.assertEqual(layout.source_path(path,root),path)
                layout.write_bytes(path,b'global',root)
                self.assertEqual(path.read_bytes(),b'global')
            self.assertFalse((root/'era_7/in_game/gui/tsin_dashboard.gui').exists())

    def test_new_sources_require_registration_and_cannot_overwrite_shared_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.fixture(root)
            new=root/'era_7/in_game/common/advances/tsin_new.txt'
            new.write_text('tsin_new = {}',encoding='utf-8')
            self.assertTrue(any('unregistered' in s for s in layout.check(root)))
            register(root)
            layout.sync(root)
            self.assertEqual(layout.check(root),[])
            collision=root/'era_7/in_game/gui/tsin_dashboard.gui'
            collision.parent.mkdir(parents=True)
            collision.write_text('should not replace',encoding='utf-8')
            shared=root/'in_game/gui/tsin_dashboard.gui'
            shared.parent.mkdir(parents=True)
            shared.write_text('original shared UI',encoding='utf-8')
            with self.assertRaises(ValueError):register(root)
            self.assertEqual(shared.read_text(encoding='utf-8'),'original shared UI')

    def test_unsafe_paths_and_multiple_era_ownership_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            rel,_,_=self.fixture(root)
            for path in ['../escape','C:/outside','in_game/../outside','in_game\\outside']:
                with self.assertRaises(ValueError):layout.safe_path(root,path)
            (root/'era_8').mkdir()
            (root/'era_8/manifest.json').write_text(json.dumps({'schema_version':1,'files':{rel:'duplicate'}}),encoding='utf-8')
            (root/'data/content_modules.json').write_text(json.dumps({'schema_version':1,'modules':[{'folder':'era_7'},{'folder':'era_8'}]}),encoding='utf-8')
            layout.entries.cache_clear()
            with self.assertRaises(ValueError):layout.entries(root)


if __name__=='__main__':unittest.main()
