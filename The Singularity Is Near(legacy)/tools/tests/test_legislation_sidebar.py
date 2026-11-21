import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pdx
from gen_legislation_sidebar import build
class LegislationSidebarTests(unittest.TestCase):
 def test_opening_and_hovering_cannot_advance_or_reroll_bill(self):
  b=build();ui=b['in_game/gui/tsin_bill_sidebar.gui']
  for forbidden in ['tsin_bill_reading_effect','tsin_table_bill_effect','Execute(','random_list','trigger_event']:
   self.assertNotIn(forbidden,ui)
  self.assertIn("ScriptValue('tsin_bill_success_chance')",b['main_menu/localization/korean/tsin_bill_sidebar_l_korean.yml'])
  self.assertIn('GetPolicy.GetNameWithNoTooltip',ui)
  self.assertFalse(any('/on_action/' in p for p in b))
 def test_metadata_is_attached_to_original_schedule_not_new_timer(self):
  s=pdx.read_text(pdx.MOD_ROOT/'in_game/common/scripted_effects/tsin_legislation_effects.txt')
  self.assertEqual(s.count('set_variable = { name = tsin_bill_check_timer months = 3 }'),2)
  self.assertEqual(s.count('tsin_bill_schedule_sidebar_metadata_effect = yes'),2)
  helper=build()['in_game/common/scripted_effects/tsin_bill_sidebar.txt']
  self.assertNotIn('check_timer',helper);self.assertNotIn('random',helper)
  self.assertIn('var:tsin_bill_wait_month > 12',helper)
  self.assertIn('name = tsin_bill_wait_year add = 1',helper)
  self.assertIn('remove_variable = tsin_bill_wait_year',s)
 def test_native_outliner_is_not_replaced_and_close_only_hides_card(self):
  b=build()
  self.assertFalse(any('outliner' in p or 'hud_' in p for p in b))
  self.assertIn('gui/tsin_bill_sidebar.gui = tsin_bill_sidebar',b['in_game/gui/scripted_widgets/tsin_bill_sidebar.txt'])
  ui=b['in_game/gui/tsin_bill_sidebar.gui']
  self.assertIn('Select_float(',ui)
  self.assertIn("GetVariableSystem.Set('tsin_ui_bill_sidebar_closed'",ui)
  self.assertNotIn('tsin_clear_bill_effect',ui)
if __name__=='__main__':unittest.main()
