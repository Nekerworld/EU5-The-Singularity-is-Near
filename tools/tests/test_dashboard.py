"""Registry boundary tests for extensible dashboard generation."""
import copy
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_dashboard import build, validate_registry, check_provider_links


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads(pdx.read_text(pdx.MOD_ROOT/'ui/dashboard_registry.json'))

    def test_later_era_can_extend_existing_domain_without_gui_edits(self):
        data=copy.deepcopy(self.data)
        new=copy.deepcopy(data['modules'][0]['metrics'][0])
        new.update(id='test_space_output',variable='tsin_test_space_output',tabs=['economy'])
        new['title']={'english':'Orbital output','korean':'궤도 산출'}
        data['modules'].append({'id':'space_test','metrics':[new]})
        generated=build(data)
        self.assertIn('tsin_ui_card_test_space_output',generated['in_game/gui/tsin_dashboard.gui'])
        self.assertIn('tsin_ui_format_test_space_output',generated['in_game/common/customizable_localization/tsin_dashboard_formatters.txt'])

    def test_registered_metric_without_backend_is_rejected(self):
        data=copy.deepcopy(self.data)
        new=copy.deepcopy(data['modules'][0]['metrics'][0])
        new.update(id='orphaned_metric',variable='tsin_missing_metric_provider',tabs=['economy'])
        data['modules'].append({'id':'orphan_test','metrics':[new]})
        errors=check_provider_links(data,pdx.MOD_ROOT)
        self.assertTrue(any('orphaned_metric' in e and 'no cached variable provider' in e for e in errors))

    def test_duplicate_and_unknown_domain_are_rejected(self):
        data=copy.deepcopy(self.data)
        data['modules'][0]['metrics'].append(copy.deepcopy(data['modules'][0]['metrics'][0]))
        with self.assertRaises(ValueError): validate_registry(data)
        data=copy.deepcopy(self.data)
        data['modules'][0]['metrics'][0]['tabs']=['missing_domain']
        with self.assertRaises(ValueError): validate_registry(data)

    def test_hover_scans_and_ambiguous_shortcuts_are_rejected(self):
        data=copy.deepcopy(self.data)
        data['modules'][0]['statuses'][0]['condition']='any_country = { always = yes }'
        with self.assertRaises(ValueError): validate_registry(data)
        data=copy.deepcopy(self.data)
        data['modules'][0]['shortcuts'][0]['map_mode']='political'
        with self.assertRaises(ValueError): validate_registry(data)

    def test_shared_frontend_and_non_destructive_migration(self):
        generated=build(self.data)
        common=generated['in_game/gui/tsin_dashboard_common.gui']
        self.assertIn('type tsin_ui_compact_strip',common)
        self.assertIn('type tsin_gdp_history_tooltip',common)
        controller=generated['in_game/gui/tsin_dashboard.gui']
        self.assertIn('tsin_dashboard_dock',controller)
        self.assertNotIn('sakuya_',controller)
        metadata=generated['in_game/common/scripted_effects/tsin_dashboard_core_effects.txt']
        self.assertNotIn('remove_variable',metadata)
        self.assertIn('var:tsin_dashboard_data_version < 1',metadata)

    def test_every_metric_has_a_card_and_both_localizations(self):
        generated=build(self.data)
        metrics,_,_=validate_registry(self.data)
        for metric in metrics:
            self.assertIn('type tsin_ui_card_'+metric['id'],generated['in_game/gui/tsin_dashboard_common.gui'])
            for lang in ['english','korean']:
                self.assertIn('TSIN_UI_METRIC_'+metric['id'].upper()+':',generated[f'main_menu/localization/{lang}/tsin_dashboard_l_{lang}.yml'])

if __name__=='__main__': unittest.main()
