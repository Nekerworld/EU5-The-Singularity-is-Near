"""Static regression checks for the H-track (HOI4 hybrid military, age VIII+).

These prove generator reproducibility, ID safety, gating and wiring only. They do not prove any
engine behavior: see docs/h0_engine_probes.md (사용자 확인 필요).
"""
from pathlib import Path
import json
import re
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdx
import h_track_common as common
import gen_military_stockpile as h1
import gen_modern_training as h2
import gen_fuel_system as h3
import gen_airforce_hybrid as h4
import gen_age8_transport_military as age8

ROOT = pdx.MOD_ROOT
GENERATORS = [(h1, True), (h2, True), (h3, False), (h4, True)]


def all_outputs():
    out = {}
    for module, has_assets in GENERATORS:
        out.update(module.build())
        if has_assets:
            out.update(module.assets())
    return out


def text_outputs():
    return {k: v for k, v in all_outputs().items() if isinstance(v, str)}


def blocks(text):
    return {b.key: b.text for b in pdx.top_level_blocks(text)}


def balanced(text):
    depth = 0
    for ch in pdx.strip_comments(text):
        depth += {'{': 1, '}': -1}.get(ch, 0)
        if depth < 0:
            return False
    return depth == 0


def keys_in(directory):
    """Top-level keys under in_game/common/<directory> in the runtime tree and every era source, with file paths."""
    found = {}
    bases = [ROOT / 'in_game/common' / directory] + [ROOT / era / 'in_game/common' / directory for era in ['era_7', 'era_8', 'era_9', 'era_10']]
    for base in bases:
        if not base.exists():
            continue
        for path in base.rglob('*.txt'):
            for b in pdx.top_level_blocks(path.read_text(encoding='utf-8-sig', errors='replace')):
                found.setdefault(b.key, []).append(path.relative_to(ROOT).as_posix())
    return found


class GeneratorWiringTests(unittest.TestCase):
    def test_generators_are_reproducible_and_mirrored(self):
        bad = common.mismatches(all_outputs())
        self.assertEqual(bad, [])

    def test_every_output_is_registered_in_its_era_manifest(self):
        for key in all_outputs():
            era, rel = key.split('/', 1)
            manifest = json.loads((ROOT / era / 'manifest.json').read_text(encoding='utf-8-sig'))['files']
            self.assertIn(rel, manifest, key)
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_braces_are_balanced_and_files_have_bom(self):
        for key, text in text_outputs().items():
            if key.endswith('.txt'):
                self.assertTrue(balanced(text), key)
            data = (ROOT / key).read_bytes()
            self.assertTrue(data.startswith(b'\xef\xbb\xbf'), key)

    def test_check_flag_is_read_only_and_clean(self):
        for module, _ in GENERATORS:
            self.assertEqual(module.main(['--check']), False, module.__name__)


class IdSafetyTests(unittest.TestCase):
    NEW_ADVANCES = [a[0] for a in h2.ADVANCES_08 + h2.ADVANCES_09 + h4.ADVANCES] + ['tsin_mass_production_arms_advance', 'tsin_armored_vehicle_industry_advance']
    NEW_BUILDINGS = list(h1.WORKS) + list(h4.BUILDINGS)
    NEW_UNITS = [u[0] for u in common.UNITS_08 + common.UNITS_09]

    def test_new_ids_are_defined_exactly_once(self):
        for directory, ids in [('advances', self.NEW_ADVANCES), ('building_types', self.NEW_BUILDINGS), ('unit_types', self.NEW_UNITS)]:
            found = keys_in(directory)
            for ident in ids:
                files = {f.split('/', 1)[1] if f.startswith('era_') else f for f in found.get(ident, [])}
                self.assertEqual(len(files), 1, (ident, found.get(ident)))

    def test_age8_templates_do_not_collide_with_existing_templates(self):
        found = keys_in('unit_types')
        for key in h2.TEMPLATES:
            files = {f.split('/', 1)[1] if f.startswith('era_') else f for f in found.get('a_age_8_world_wars_' + key, [])}
            self.assertEqual(len(files), 1, key)

    def test_age8_transport_ids_are_preserved(self):
        built = age8.build()
        buildings = blocks(built['in_game/common/building_types/tsin_age8_transport_buildings.txt'])
        self.assertIn('tsin_capital_airfield', buildings)
        self.assertIn('tsin_motor_transport_depot', buildings)
        advances = blocks(built['in_game/common/advances/zz_tsin_08_transport_military.txt'])
        for ident in ['tsin_powered_flight_advance', 'tsin_aerial_observation_advance', 'tsin_motor_supply_columns_advance', 'tsin_motor_transport_advance']:
            self.assertIn(ident, advances)
        # The H track must not rewrite those definitions.
        for key, text in text_outputs().items():
            if key.endswith('.txt'):
                for ident in blocks(text):
                    self.assertNotIn(ident, ['tsin_capital_airfield', 'tsin_motor_transport_depot', 'tsin_powered_flight_advance', 'tsin_aerial_observation_advance'])
        # The on-disk airfield source still equals the age VIII generator output.
        source = ROOT / 'era_8/in_game/common/building_types/tsin_age8_transport_buildings.txt'
        self.assertEqual(source.read_bytes(), common.encode(built['in_game/common/building_types/tsin_age8_transport_buildings.txt']))

    def test_all_h_advance_parents_exist_and_are_ordered(self):
        all_adv = keys_in('advances')
        for key, text in text_outputs().items():
            if '/advances/' not in key:
                continue
            for aid, body in blocks(text).items():
                for parent in re.findall(r'requires = (\w+)', body):
                    self.assertIn(parent, all_adv, (aid, parent))
        # File name order: H advance files sort after the files they depend on.
        self.assertGreater('zzz_tsin_08_h1', 'zz_tsin_08_transport_military')
        self.assertGreater('zzz_tsin_08_h4', 'zzz_tsin_08_h1')

    def test_no_new_market_goods_or_vanilla_overwrite_prefixes(self):
        for key, text in text_outputs().items():
            self.assertNotIn('/goods/', key)
            for k in blocks(text):
                self.assertFalse(re.match(r'(TRY_)?(REPLACE|INJECT)', k), (key, k))


class GatingTests(unittest.TestCase):
    def setUp(self):
        self.out = text_outputs()

    def test_gate_triggers_require_age8_and_an_advance(self):
        triggers = blocks(self.out['era_8/in_game/common/scripted_triggers/zzz_tsin_h1_gates.txt'])
        self.assertIn('current_later_age_8_world_wars_trigger = yes', triggers['tsin_h_age8_trigger'])
        for gate, advance in [('tsin_h_stockpile_gate_trigger', 'tsin_mass_production_arms_advance'),
                              ('tsin_h_fuel_gate_trigger', 'tsin_motor_transport_advance'),
                              ('tsin_h_air_gate_trigger', 'tsin_aircraft_industry_advance')]:
            self.assertIn('tsin_h_age8_trigger = yes', triggers[gate])
            self.assertIn('has_advance = ' + advance, triggers[gate])

    def test_monthly_actions_are_gated_and_age7_is_never_named(self):
        for name, gate in [('zzz_tsin_h1_stockpile_on_actions.txt', 'tsin_h_stockpile_gate_trigger'),
                           ('zzz_tsin_h3_fuel_on_actions.txt', 'tsin_h_fuel_gate_trigger'),
                           ('zzz_tsin_h4_air_on_actions.txt', 'tsin_h_air_gate_trigger')]:
            text = self.out['era_8/in_game/common/on_action/' + name]
            self.assertIn('trigger = { ' + gate + ' = yes }', text)
            self.assertIn('monthly_country_pulse = {', text)
        for key, text in self.out.items():
            if '/on_action/' in key or '/scripted_effects/' in key or '/script_values/' in key:
                self.assertNotIn('age_7_industrialization', text, key)

    def test_battle_hooks_only_subtract_when_initialized(self):
        text = self.out['era_8/in_game/common/on_action/zzz_tsin_h1_stockpile_on_actions.txt']
        self.assertEqual(text.count('tsin_h_stockpile_gate_trigger = yes has_variable = tsin_h_init'), 2)
        self.assertIn('on_battle_won = {', text)
        self.assertIn('on_battle_lost = {', text)

    def test_air_operations_run_only_at_war(self):
        text = self.out['era_8/in_game/common/scripted_effects/zzz_tsin_h4_air_effects.txt']
        monthly = blocks(text)['tsin_h4_air_monthly_effect']
        self.assertIn('limit = { at_war = yes }', monthly)
        self.assertIn('tsin_h4_war_ops_effect = yes', monthly)
        ops_calls = [k for k, v in blocks(text).items() if 'tsin_h4_war_ops_effect = yes' in v]
        self.assertEqual(ops_calls, ['tsin_h4_air_monthly_effect'])

    def test_no_army_deletion_anywhere(self):
        banned = ['destroy_unit', 'destroy_army', 'disband', 'add_subunit', 'create_sub_unit', 'remove_advance', 'change_unit_owner', 'set_unit_size']
        for key, text in self.out.items():
            clean = pdx.strip_comments(text)
            for word in banned:
                self.assertNotIn(word, clean, (key, word))


class StockpileTests(unittest.TestCase):
    def setUp(self):
        self.effects = h1.effects()
        self.values = h1.script_values()

    def test_four_stockpiles_lines_and_monthly_pulse(self):
        for c in h1.CATEGORIES:
            k = c['key']
            self.assertIn(f'name = tsin_eq_{k}_stockpile value = {c["start"]}', self.effects)
            self.assertIn(f'tsin_line_eff_{k}', self.effects)
            self.assertIn(f'tsin_eq_{k}_production', self.values)
            self.assertIn(f'total_effective_building_levels:{c["works"]}', self.values)
        self.assertIn('tsin_h1_stockpile_monthly_effect', self.effects)

    def test_works_make_real_goods_with_positive_margin_and_use_mill_template(self):
        text = h1.build()['era_8/in_game/common/building_types/zzz_tsin_08_h1_arsenals.txt']
        works = blocks(text)
        self.assertEqual(set(works), set(h1.WORKS))
        for ident, body in works.items():
            self.assertIn('is_mill = yes', body)
            self.assertIn('construction_demand = tsin_factory_construction', body)
            self.assertIn('tsin_large_city = yes', body)
            self.assertEqual(body.count('category = mills_input'), 2)
        for works_id, lines in h1.WORKS.items():
            good = h1.WORKS_GOOD[works_id]
            for pm, icon, inputs in lines:
                cost = sum(h1.PRICES[g] * v for g, v in inputs.items())
                m = re.search(rf'{pm} = \{{.*?output = ([0-9.]+)', text, re.S)
                self.assertTrue(m, pm)
                self.assertGreaterEqual(float(m.group(1)) * h1.PRICES[good], cost)
                for g in inputs:
                    self.assertIn(g, h1.PRICES)

    def test_vanilla_and_mod_goods_exist(self):
        mod_goods = set(blocks(pdx.read_text(ROOT / 'in_game/common/goods/tsin_goods.txt')))
        vanilla = {'firearms', 'cannons', 'steel', 'coal', 'tools', 'copper', 'lumber', 'iron', 'leather', 'glass'}
        for g in set(h1.PRICES):
            self.assertTrue(g in mod_goods or g in vanilla, g)

    def test_shortage_modifiers_are_unit_category_and_applied_when_negative(self):
        text = h1.static_modifiers()
        mods = blocks(text)
        for key, *_ in h1.SHORTAGE_MODIFIERS:
            self.assertIn('category = unit', mods[key])
            self.assertIn(f'modifier = {key} days = 31 mode = add_and_extend', self.effects)
            self.assertIn(f'remove_unit_modifier = {key}', self.effects)
        for k in ['small_arms', 'support_artillery', 'armored_vehicles']:
            self.assertIn(f'var:tsin_eq_{k}_stockpile < 0', self.effects)
        self.assertIn('at_war = yes', self.effects)

    def test_losses_use_battle_scope_values_and_are_floor_clamped(self):
        self.assertIn('scope:lost_land_units', self.effects)
        self.assertIn('tsin_eq_battle_loss_effect', self.effects)
        self.assertEqual(self.effects.count('value = tsin_eq_stockpile_floor'), 3 + 4)

    def test_flows_are_bounded(self):
        self.assertIn('tsin_eq_stockpile_cap = 600', self.values)
        self.assertIn('tsin_eq_stockpile_floor = -300', self.values)
        self.assertIn('tsin_h_war_factor', self.values)
        # Peacetime is cheaper than war, and the free reserve never covers the full demand.
        self.assertIn('multiply = 0.4', self.values)
        self.assertIn('multiply = 0.3 }', self.values)


class TrainingAndUnitTests(unittest.TestCase):
    def setUp(self):
        self.out = h2.build()

    def test_six_categories_map_to_unit_templates(self):
        keys = {u[2] for u in common.UNITS_08}
        self.assertEqual(keys, {'light_cavalry', 'heavy_cavalry', 'light_infantry', 'heavy_infantry', 'artillery', 'auxiliary'})
        self.assertEqual(len(common.UNITS_08), 6)
        self.assertEqual(len(common.UNITS_09), 2)

    def test_units_are_buildable_have_demands_and_ages(self):
        units = blocks(self.out['era_8/in_game/common/unit_types/zzz_tsin_08_h2_b_units.txt'])
        units9 = blocks(self.out['era_9/in_game/common/unit_types/zzz_tsin_09_h2_units.txt'])
        demands = blocks(self.out['era_8/in_game/common/goods_demand/tsin_age8_h2_land_demands.txt'])
        demands9 = blocks(self.out['era_9/in_game/common/goods_demand/tsin_age9_h2_land_demands.txt'])
        templates = blocks(self.out['era_8/in_game/common/unit_types/zzz_tsin_08_h2_a_templates.txt'])
        self.assertEqual(set(units), {u[0] for u in common.UNITS_08})
        self.assertEqual(set(units9), {u[0] for u in common.UNITS_09})
        for table, pool in [(units, demands), (units9, demands9)]:
            for uid, body in table.items():
                self.assertIn('buildable = yes', body, uid)
                for field in ['construction_demand', 'maintenance_demand']:
                    name = re.search(field + r' = (\w+)', body).group(1)
                    self.assertIn(name, pool, (uid, name))
        for uid, body in units.items():
            self.assertIn(re.search(r'copy_from = (\w+)', body).group(1), templates, uid)
        for uid, body in units9.items():
            self.assertIn('age = "age_9_atomic"', body)
            self.assertIn(re.search(r'copy_from = (\w+)', body).group(1), units, uid)
        for body in templates.values():
            self.assertIn('age = "age_8_world_wars"', body)
            self.assertIn('buildable = no', body)

    def test_unit_demand_goods_exist(self):
        goods = set(blocks(pdx.read_text(ROOT / 'in_game/common/goods/tsin_goods.txt'))) | {'firearms', 'cannons', 'steel', 'tools', 'copper', 'leather'}
        for table in [h2.UNIT_DATA_08, h2.UNIT_DATA_09]:
            for _, (_, _, cons, maint) in table.items():
                for g in list(cons) + list(maint):
                    self.assertIn(g, goods)

    def test_every_unit_has_an_unlocking_advance_and_role_trigger(self):
        advances = {}
        for key in ['era_8/in_game/common/advances/zzz_tsin_08_h2_training_units.txt', 'era_9/in_game/common/advances/zzz_tsin_09_h2_units.txt']:
            advances.update(blocks(self.out[key]))
        for uid, role, _, adv in common.UNITS_08 + common.UNITS_09:
            self.assertIn(f'unlock_unit = {uid}', advances[adv], uid)
        triggers = self.out['era_8/in_game/common/scripted_triggers/zzz_tsin_h2_unit_triggers.txt']
        for uid, role, _, _ in common.UNITS_08 + common.UNITS_09:
            body = blocks(triggers)['tsin_h_unit_' + role + '_trigger'] if role != 'infantry' else ''
            if role != 'infantry':
                self.assertIn(f'unit_type:{uid}', body, uid)

    def test_drill_ability_follows_vanilla_drill_army_with_stronger_effects(self):
        text = self.out['era_8/in_game/common/unit_abilities/tsin_modern_field_drill.txt']
        for needle in ['toggle = yes', 'army_only = yes', 'cancel_on_combat = yes', 'cancel_on_move = yes',
                       'force_army_maintenance = yes', 'has_commander = yes', 'in_combat = yes', 'ai_will_do']:
            self.assertIn(needle, text)
        vanilla = pdx.game_root() / 'in_game/common/unit_abilities/drill_army.txt'
        if vanilla.exists():
            ref = vanilla.read_text(encoding='utf-8-sig')
            xp = lambda s: float(re.search(r'monthly_experience_gain = ([0-9.]+)', s).group(1))
            self.assertGreater(xp(text), xp(ref))
        advance = blocks(self.out['era_8/in_game/common/advances/zzz_tsin_08_h2_training_units.txt'])['tsin_modern_field_drill_advance']
        self.assertIn('unlock_ability = tsin_modern_field_drill', advance)


class FuelTests(unittest.TestCase):
    def setUp(self):
        self.effects = h3.effects()
        self.values = h3.script_values()

    def test_fuel_variable_fill_use_and_goods(self):
        self.assertIn('var:tsin_fuel_stockpile', self.effects)
        self.assertIn('goods:tsin_oil', self.effects)
        self.assertIn('tsin_oil', blocks(pdx.read_text(ROOT / 'in_game/common/goods/tsin_goods.txt')))
        self.assertIn('buy_goods_from_market', self.effects)
        self.assertIn('tsin_fuel_baseline_inflow', self.values)
        for needle in ['tsin_h_n_armored', 'tsin_h_n_motorized', 'tsin_air_active_aircraft', 'at_war = no']:
            self.assertIn(needle, self.values)

    def test_market_buy_is_bounded_and_switchable(self):
        self.assertIn('has_global_variable = tsin_h_fuel_market_off', self.effects)
        self.assertIn('tsin_h_fuel_market_off_effect', self.effects)
        self.assertIn('max = "market.stockpile_in_market(goods:tsin_oil)"', self.effects)
        self.assertIn('multiply = 0.02', self.effects)
        self.assertNotIn('add_gold', self.effects)
        self.assertEqual(self.effects.count('buy_goods_from_market ='), 1)

    def test_depletion_penalties_use_unit_modifiers_on_fuel_users_only(self):
        mods = blocks(h3.static_modifiers())
        self.assertIn('army_movement_speed = -0.4', mods['tsin_fuel_depleted'])
        self.assertLess(float(re.search(r'army_movement_speed = (-[0-9.]+)', mods['tsin_fuel_low']).group(1)),
                        0)
        self.assertGreater(abs(float(re.search(r'army_movement_speed = (-[0-9.]+)', mods['tsin_fuel_depleted']).group(1))),
                           abs(float(re.search(r'army_movement_speed = (-[0-9.]+)', mods['tsin_fuel_low']).group(1))))
        self.assertIn('tsin_h_unit_fuel_user_trigger = yes', self.effects)
        self.assertEqual(self.effects.count('add_unit_modifier ='), 2)
        self.assertIn('remove_variable = tsin_fuel_penalty_on', self.effects)

    def test_capacity_reads_existing_buildings(self):
        for building in ['tsin_oil_storage', 'tsin_motor_transport_depot', 'tsin_airbase']:
            self.assertIn(f'total_effective_building_levels:{building}', self.values)


class AirForceTests(unittest.TestCase):
    def setUp(self):
        self.out = h4.build()
        self.effects = h4.effects()

    def test_four_aircraft_stockpiles_and_capital_airfield_capacity(self):
        for k, *_ in h4.TYPES:
            self.assertIn(f'tsin_air_{k}_stockpile', self.effects)
        self.assertAlmostEqual(sum(t[3] for t in h4.TYPES), 1.0)
        values = h4.script_values()
        self.assertIn('total_effective_building_levels:tsin_capital_airfield', values)
        self.assertIn('total_effective_building_levels:tsin_airbase', values)
        self.assertNotIn('tsin_capital_airfield = {', h4.buildings())

    def test_province_targeting_is_used_and_area_not_used_elsewhere(self):
        actions = self.out['era_8/in_game/common/generic_actions/zzz_tsin_h4_air_missions.txt']
        self.assertIn('looking_for_a = province', actions)
        self.assertNotIn('looking_for_a = area', actions)
        self.assertIn('사용자 확인 필요', actions)
        mod_text = ''
        for p in (ROOT / 'in_game/common/generic_actions').glob('*.txt'):
            if 'h4_air' not in p.name:
                mod_text += p.read_text(encoding='utf-8-sig')
        self.assertNotIn('looking_for_a = area', mod_text)
        self.assertEqual(len(blocks(actions)), 5)
        for key, *_ in h4.MISSIONS:
            self.assertIn('tsin_air_target_' + key, blocks(actions))

    def test_missions_use_only_conservative_effects(self):
        for needle in ['damage_unit_percent = { 0 0.03 }', 'damage_unit_percent = { 0 0.015 }', 'add_food_percentage = { 0.05 0.10 }',
                       'chance = 12', 'chance = 5', 'minor_destroy_building_levels_in_location', 'add_unit_modifier']:
            self.assertIn(needle, self.effects)
        self.assertNotIn('major_destroy_building_levels_in_location', self.effects)
        # Strategic bombing only hits locations owned by an enemy at war.
        bombing = blocks(self.effects)['tsin_h4_bombing_effect']
        self.assertIn('limit = { owner ?= { is_at_war_with = scope:tsin_air_owner } }', bombing)
        cas = blocks(self.effects)['tsin_h4_cas_effect']
        self.assertGreaterEqual(cas.count('owner ?= { is_at_war_with = scope:tsin_air_owner }'), 2)
        for mission in ['tsin_h4_superiority_effect', 'tsin_h4_cas_effect', 'tsin_h4_bombing_effect', 'tsin_h4_supply_effect']:
            self.assertIn('tsin_h4_sorties_possible_trigger = yes', blocks(self.effects)[mission])

    def test_air_buildings_and_advances(self):
        text = self.out['era_8/in_game/common/building_types/zzz_tsin_08_h4_air_buildings.txt']
        built = blocks(text)
        self.assertEqual(set(built), {'tsin_airbase', 'tsin_anti_air_battery'})
        for body in built.values():
            self.assertIn('construction_demand = tsin_factory_construction', body)
            self.assertIn('category = building_maintenance', body)
            self.assertIn('tsin_large_city = yes', body)
        adv = blocks(self.out['era_8/in_game/common/advances/zzz_tsin_08_h4_airforce.txt'])
        self.assertIn('tsin_powered_flight_advance', adv['tsin_aircraft_industry_advance'])
        self.assertIn('tsin_aerial_observation_advance', adv['tsin_air_operations_advance'])
        self.assertIn('unlock_building = tsin_aircraft_works', adv['tsin_aircraft_industry_advance'])

    def test_pool_distribution_is_bounded_by_capacity(self):
        dist = blocks(self.effects)['tsin_h4_distribute_effect']
        self.assertIn('tsin_air_total < tsin_air_capacity', dist)
        self.assertIn('max = 20', dist)
        self.assertIn('subtract = var:tsin_air_batch', dist)

    def test_ai_assignment_targets_army_in_combat_and_clears_when_none(self):
        ai = blocks(self.effects)['tsin_h4_ai_assign_effect']
        self.assertIn('in_combat = yes', ai)
        self.assertIn('tsin_h4_clear_targets_effect = yes', ai)


class LocalizationAndDocsTests(unittest.TestCase):
    def keys(self, era, lang):
        found = set()
        folder = ROOT / era / 'main_menu/localization' / lang
        for p in folder.glob('tsin_h*_l_*.yml'):
            for line in p.read_text(encoding='utf-8-sig').splitlines()[1:]:
                m = re.match(r'\s*([A-Za-z0-9_.]+):', line)
                if m:
                    found.add(m.group(1))
        return found

    def test_english_and_korean_exist_for_every_object(self):
        needed = {'era_8': set(), 'era_9': set()}
        for ident in IdSafetyTests.NEW_ADVANCES:
            era = 'era_9' if ident in ('tsin_main_battle_tank_advance', 'tsin_rocket_artillery_advance') else 'era_8'
            needed[era] |= {ident, ident + '_desc'}
        for ident in IdSafetyTests.NEW_BUILDINGS:
            needed['era_8'] |= {ident, ident + '_desc'}
        for ident in IdSafetyTests.NEW_UNITS:
            era = 'era_9' if ident in ('a_tsin_main_battle_tank', 'a_tsin_rocket_artillery_battery') else 'era_8'
            needed[era] |= {ident, ident + '_desc'}
        needed['era_8'] |= {'tsin_modern_field_drill', 'tsin_modern_field_drill_desc', 'tsin_modern_field_drill_cta', 'tsin_air_recall'}
        needed['era_8'] |= {'tsin_air_target_' + m[0] for m in h4.MISSIONS} | {'tsin_air_target_' + m[0] + '_desc' for m in h4.MISSIONS}
        for key, *_ in h1.SHORTAGE_MODIFIERS + h3.MODS + h4.MODS:
            needed['era_8'] |= {'STATIC_MODIFIER_NAME_' + key}
        for pms in h1.WORKS.values():
            for pm, *_ in pms:
                needed['era_8'].add(pm)
        for era, items in needed.items():
            for lang in ['english', 'korean']:
                missing = items - self.keys(era, lang)
                self.assertFalse(missing, (era, lang, sorted(missing)))

    def test_korean_text_contains_hangul(self):
        for key, text in text_outputs().items():
            if key.endswith('_l_korean.yml'):
                self.assertRegex(text, '[가-힣]')

    def test_h0_probe_doc_marks_every_stage_unverified(self):
        text = (ROOT / 'docs/h0_engine_probes.md').read_text(encoding='utf-8')
        for stage in ['H0', 'H1', 'H2', 'H3', 'H4', 'H5']:
            row = [line for line in text.splitlines() if line.startswith(f'| {stage} ')]
            self.assertTrue(row, stage)
            self.assertIn('사용자 확인 필요', row[0], stage)
        for probe in ['P1.', 'P2.', 'P3.', 'P4.', 'P5.']:
            self.assertIn(probe, text)

    def test_design_doc_lists_all_new_ids(self):
        text = (ROOT / 'docs/military_hybrid_h_track.md').read_text(encoding='utf-8')
        for ident in IdSafetyTests.NEW_ADVANCES + IdSafetyTests.NEW_BUILDINGS + IdSafetyTests.NEW_UNITS:
            self.assertIn(ident, text, ident)


if __name__ == '__main__':
    unittest.main()
