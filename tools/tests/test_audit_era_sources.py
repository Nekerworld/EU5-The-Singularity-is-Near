from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import audit
import pdx


class AuditEraSourceTests(unittest.TestCase):
    def test_registered_zz_advances_are_read_even_without_deployed_runtime(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'data').mkdir()
            era=root/'era_8'; era.mkdir()
            rel='in_game/common/advances/zz_tsin_08_agriculture.txt'
            (root/'data/content_modules.json').write_text(json.dumps({'schema_version':1,'modules':[{'folder':'era_8'}]}))
            (era/'manifest.json').write_text(json.dumps({'schema_version':1,'files':{rel:'new-era-content'}}))
            source=era/rel;source.parent.mkdir(parents=True);source.write_text('tsin_farming = { unlock_production_method = tsin_ammonia }')
            with patch.object(audit,'MOD',root):
                paths=audit.own_files('in_game/common/advances')
            self.assertEqual(paths,[root/rel])
            from era_layout import source_path
            self.assertEqual(pdx.read_text(source_path(paths[0],root)),source.read_text())
            self.assertFalse((root/rel).exists())

    def test_migrated_ammonia_unlock_is_in_actual_audit_inventory(self):
        texts='\n'.join(pdx.read_text(p) for p in audit.own_files('in_game/common/advances'))
        self.assertIn('unlock_production_method = tsin_nitrogen_fixation_ammonia',texts)


if __name__=='__main__':unittest.main()
