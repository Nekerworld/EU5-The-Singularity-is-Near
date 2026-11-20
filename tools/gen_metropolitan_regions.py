"""Location-backed metropolitan regions: province selection, bounded cached links, one role per core,
a management summary read from quarterly review, and per-site bulk projects (docs/metropolitan_regions.md)."""
from pathlib import Path
import sys, argparse, json
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pdx

# (key, korean, english, core condition, modifier, value). The role bonus goes to the core location only.
ROLES = [
    (1, 'commerce', '상업·행정 중심', 'Commerce and administration', 'total_building_levels >= 3',
     'local_max_control', 0.02),
    (2, 'residential', '주거 중심', 'Residential core', 'population >= 150',
     'local_population_capacity_modifier', 0.03),
    (3, 'port', '항만 중심', 'Port core', 'is_coastal = yes',
     'local_trade_center_power', 0.02),
    (4, 'industrial', '산업 중심', 'Industrial core', 'tsin_location_industrial_jobs >= 1000',
     'local_mills_build_buildings_efficiency', 0.03),
]
BULK_STAGES = [1, 2, 3]
STAGE_COST = {1: 300, 2: 600, 3: 1200}
STAGE_ADVANCE = {1: 'tsin_industrial_capitalism_advance', 2: 'tsin_urban_planning_advance', 3: 'tsin_engineering_education_advance'}


def _role_actions():
    out = []
    for k, key, _ko, _en, cond, _mod, _v in ROLES:
        out.append(f'''tsin_metro_role_{key} = {{
 type = owncountry price = price:tsin_metro_review_price show_message = no
 ai_tick = never automation_tick = never
 select_trigger = {{
  looking_for_a = location source = actor target_flag = metro_core name = "choose_metro_core"
  column = {{ data = name }}
  visible = {{ owner ?= scope:actor has_variable = tsin_metro_core }}
  enabled = {{ owner ?= scope:actor has_variable = tsin_metro_core {cond} }}
 }}
 effect = {{ scope:metro_core = {{ set_variable = {{ name = tsin_metro_role value = {k} }} }} }}
}}
''')
    return '\n'.join(out)


def _bulk_actions():
    out = []
    for n in BULK_STAGES:
        cost = STAGE_COST[n]
        out.append(f'''tsin_metro_bulk_{n} = {{
 type = owncountry price = price:tsin_metro_review_price show_message = yes
 ai_tick = never automation_tick = never
 potential = {{ scope:actor = {{ has_advance = {STAGE_ADVANCE[n]} }} }}
 select_trigger = {{
  looking_for_a = location source = actor target_flag = metro_core name = "choose_metro_core"
  column = {{ data = name }}
  visible = {{ owner ?= scope:actor has_variable = tsin_metro_core }}
  enabled = {{ owner ?= scope:actor has_variable = tsin_metro_core }}
 }}
 effect = {{
  # Each site is checked again when it is reached: owner, controller, technology, stage, cash and no pending project.
  every_in_global_list = {{ variable = tsin_metro_member_sites
   limit = {{
    var:tsin_metro_hub ?= scope:metro_core
    owner ?= scope:actor controller ?= scope:actor
    tsin_urban_project_gate_{n}_trigger = yes
    scope:actor = {{ gold >= {cost} }}
   }}
   scope:actor = {{ add_gold = -{cost} }}
   tsin_urban_project_start_{n}_effect = yes
  }}
 }}
}}
''')
    return '\n'.join(out)


def _role_modifiers():
    out = []
    for _k, key, _ko, _en, _cond, mod, value in ROLES:
        out.append(f'''tsin_metro_role_{key}_modifier = {{
 category = location type = location
 potential_trigger = {{ has_variable = tsin_metro_core has_variable = tsin_metro_role var:tsin_metro_role = {_k} }}
 {mod} = {value}
}}
''')
    return '\n'.join(out)


def _registry_module():
    return {'id': 'metro_regions', 'shortcuts': [
        {'id': 'metro_review', 'tab': 'society', 'title': {'korean': '도시권 연결 재검사', 'english': 'Review metropolitan connections'},
         'generic_action': 'tsin_metro_review'}],
        'metrics': [
            {'id': 'metro_sites', 'variable': 'tsin_metro_sites', 'title': {'korean': '도시권 구성 지점 수', 'english': 'Metropolitan member locations'},
             'tabs': ['society'], 'unit': 'number', 'frequency': 'manual',
             'description': {'korean': '분기 검토가 마지막으로 센 구성 지점 수입니다. 실제 인구나 식량을 공유하지 않습니다.',
                             'english': 'Member locations counted by the last quarterly review. Population and food are not shared.'}},
            {'id': 'metro_broken', 'variable': 'tsin_metro_broken', 'title': {'korean': '단절된 구성 지점 수', 'english': 'Disconnected member locations'},
             'tabs': ['society'], 'unit': 'number', 'frequency': 'manual',
             'description': {'korean': '마지막 검토에서 중심과 도로로 이어지지 않은 구성 지점 수입니다.',
                             'english': 'Member locations without a road link to their core at the last review.'}},
            {'id': 'metro_hubs', 'variable': 'tsin_metro_hubs', 'title': {'korean': '도시권 중심 수', 'english': 'Metropolitan cores'},
             'tabs': ['society'], 'unit': 'number', 'frequency': 'manual',
             'description': {'korean': '지정한 도시권 중심의 수입니다. 중심 하나는 역할 하나만 가질 수 있습니다.',
                             'english': 'Number of designated cores. Each core has one role.'}}]}


def build():
    choose_hub = '''select_trigger = {
 looking_for_a = location source = actor target_flag = metro_hub name = "choose_location"
 column = { data = name }
 visible = { owner ?= scope:actor has_variable = tsin_metro_core }
}'''
    join = '''owner ?= scope:actor
controller ?= scope:actor
NOT = { has_variable = tsin_metro_hub }
has_road_to = scope:metro_hub
any_neighbor_location = { has_variable = tsin_metro_hub var:tsin_metro_hub ?= scope:metro_hub }'''
    actions = '''tsin_metro_create = {
 type = owncountry price = price:tsin_metro_create_price show_message = no
 ai_tick = monthly ai_tick_frequency = 12 automation_tick = never
 potential = { scope:actor = { has_advance = tsin_urban_planning_advance } }
 ai_prerequisite = { gold >= 1200 NOT = { has_variable = tsin_ai_metro_created } }
 select_trigger = {
  looking_for_a = location source = actor target_flag = target_location name = "choose_location"
  column = { data = name } column = { data = population }
  visible = { owner ?= scope:actor tsin_is_city_location = yes population >= 100 }
  enabled = { controller ?= scope:actor NOT = { has_variable = tsin_metro_hub } }
 }
 effect = {
  scope:target_location = {
   set_variable = tsin_metro_core
   set_variable = { name = tsin_metro_hub value = this }
   set_variable = { name = tsin_metro_members value = 1 }
  }
  scope:actor = { set_variable = tsin_ai_metro_created }
  scope:actor = { if = { limit = { NOT = { has_variable = tsin_metro_hubs } } set_variable = { name = tsin_metro_hubs value = 0 } } change_variable = { name = tsin_metro_hubs add = 1 } }
 }
 ai_will_do = { value = 5 }
}
tsin_metro_expand = {
 type = owncountry price = price:tsin_metro_expand_price show_message = no
 ai_tick = monthly ai_tick_frequency = 12 automation_tick = never
 potential = { scope:actor = { has_advance = tsin_urban_planning_advance } }
 ai_prerequisite = { gold >= 800 has_variable = tsin_ai_metro_created }
''' + choose_hub + '''
 select_trigger = {
  looking_for_a = province source = actor target_flag = metro_province name = "choose_province"
  column = { data = name }
  visible = { any_location_in_province = { owner ?= scope:actor } }
  enabled = { scope:metro_hub = { var:tsin_metro_members < 24 }
   any_location_in_province = { ''' + join + ''' }
  }
 }
 effect = {
  scope:metro_province = {
   every_location_in_province = {
    limit = { ''' + join + ''' scope:metro_hub = { var:tsin_metro_members < 24 } }
    if = { limit = { scope:metro_hub = { var:tsin_metro_members < 24 } }
    set_variable = { name = tsin_metro_hub value = scope:metro_hub }
    set_variable = { name = tsin_metro_connected value = 1 }
    add_to_global_variable_list = { name = tsin_metro_member_sites target = this }
    scope:metro_hub = { change_variable = { name = tsin_metro_members add = 1 } }
    }
   }
  }
  set_global_variable = tsin_metro_regions_enabled
 }
 ai_will_do = { value = 5 }
}
tsin_metro_leave = {
 type = owncountry price = price:tsin_metro_review_price show_message = no
 ai_tick = never automation_tick = never
 select_trigger = {
  looking_for_a = location source = actor target_flag = target_location name = "choose_location"
  column = { data = name }
  visible = { owner ?= scope:actor has_variable = tsin_metro_hub NOT = { has_variable = tsin_metro_core } }
 }
 effect = { scope:target_location = { tsin_metro_detach_effect = yes } }
}
tsin_metro_review = {
 type = owncountry price = price:tsin_metro_review_price show_message = no
 ai_tick = never automation_tick = never
 effect = { tsin_metro_review_effect = yes }
}
''' + _role_actions() + _bulk_actions()

    effects = '''tsin_metro_detach_effect = {
 var:tsin_metro_hub ?= {
  if = { limit = { var:tsin_metro_members > 1 } change_variable = { name = tsin_metro_members subtract = 1 } }
 }
 remove_variable = tsin_metro_hub
 remove_variable = tsin_metro_connected
 remove_list_global_variable = { name = tsin_metro_member_sites target = this }
}
tsin_metro_review_effect = {
 set_global_variable = { name = tsin_metro_review_month value = tsin_urban_calendar_month }
 if = { limit = { NOT = { has_global_variable = tsin_metro_review_serial } } set_global_variable = { name = tsin_metro_review_serial value = 0 } }
 change_global_variable = { name = tsin_metro_review_serial add = 1 }
 clear_list = tsin_metro_review_sites
 every_in_global_list = { variable = tsin_metro_member_sites add_to_list = tsin_metro_review_sites }
 every_in_list = { list = tsin_metro_review_sites
  if = { limit = { NOT = { owner ?= var:tsin_metro_hub.owner } }
   tsin_metro_detach_effect = yes
  }
  else = {
   set_variable = { name = tsin_metro_connected value = 0 }
   if = { limit = { controller ?= owner has_road_to = var:tsin_metro_hub
    var:tsin_metro_hub ?= { has_variable = tsin_metro_core controller ?= owner } }
    set_variable = { name = tsin_metro_connected value = 1 }
   }
   # Management summary (read by the dashboard). Counters are reset per owner on the first counted site of each review
   # serial, so no world-wide country scan is needed. Countries with no member left keep their last value until
   # they own a site again; the dashboard description says the values are as of the last review.
   owner = {
    if = { limit = { NOT = { var:tsin_metro_review_seen = global_var:tsin_metro_review_serial } }
     set_variable = { name = tsin_metro_review_seen value = global_var:tsin_metro_review_serial }
     set_variable = { name = tsin_metro_sites value = 0 }
     set_variable = { name = tsin_metro_broken value = 0 }
    }
    change_variable = { name = tsin_metro_sites add = 1 }
   }
   if = { limit = { var:tsin_metro_connected = 0 } owner = { change_variable = { name = tsin_metro_broken add = 1 } } }
  }
 }
 clear_list = tsin_metro_review_sites
}
'''
    auto = '''tsin_metro_core = {
 category = location type = location
 potential_trigger = { has_variable = tsin_metro_core population >= 100 controller ?= owner }
 local_trade_center_power = 0.02
 local_max_control = 0.02
}
tsin_metro_linked = {
 category = location type = location
 scales_with = tsin_metro_link_scale
 potential_trigger = {
  has_variable = tsin_metro_hub has_variable = tsin_metro_connected var:tsin_metro_connected = 1
  owner ?= var:tsin_metro_hub.owner controller ?= owner
 }
 local_population_capacity_modifier = 0.03
 local_construction_speed = 0.02
}
''' + _role_modifiers()
    outputs = {
        'in_game/common/generic_actions/tsin_metropolitan_regions.txt': actions,
        'in_game/common/script_values/tsin_metropolitan_regions.txt': '''tsin_metro_link_scale = {
 value = 1
 if = { limit = { var:tsin_metro_hub ?= { var:tsin_metro_members > 12 } } multiply = 0.75 }
 if = { limit = { var:tsin_metro_hub ?= { var:tsin_metro_members > 20 } } multiply = 0.8 }
}
''',
        'in_game/common/scripted_effects/tsin_metropolitan_regions.txt': effects,
        'in_game/common/auto_modifiers/tsin_metropolitan_regions.txt': auto,
        'in_game/common/prices/tsin_metropolitan_regions.txt': 'tsin_metro_create_price = { gold = 300 }\ntsin_metro_expand_price = { gold = 200 }\ntsin_metro_review_price = { gold = 0 }\n',
        'in_game/common/on_action/tsin_metropolitan_regions.txt': '''monthly_country_pulse = { on_actions = { tsin_metro_quarterly_review } }
tsin_metro_quarterly_review = {
 trigger = { has_global_variable = tsin_metro_regions_enabled
  OR = { current_month = 1 current_month = 4 current_month = 7 current_month = 10 }
  OR = { NOT = { has_global_variable = tsin_metro_review_month } tsin_urban_calendar_month > global_var:tsin_metro_review_month }
 }
 effect = { tsin_metro_review_effect = yes }
}
''',
    }
    labels = {'tsin_metro_create': ('도시권 중심 지정', 'Designate metropolitan core'),
              'tsin_metro_expand': ('도시권에 지방 편입', 'Add province to metropolitan region'),
              'tsin_metro_leave': ('지점을 도시권에서 제외', 'Remove metropolitan member'),
              'tsin_metro_review': ('도시권 연결 재검사', 'Review metropolitan connections'),
              'AUTO_MODIFIER_NAME_tsin_metro_core': ('도시권 중심', 'Metropolitan core'),
              'AUTO_MODIFIER_NAME_tsin_metro_linked': ('도시권 연계', 'Metropolitan connection')}
    for k, key, ko, en, _c, _m, _v in ROLES:
        labels[f'tsin_metro_role_{key}'] = (ko, en)
        labels[f'AUTO_MODIFIER_NAME_tsin_metro_role_{key}_modifier'] = (ko + ' 보너스', en + ' bonus')
    for n in BULK_STAGES:
        labels[f'tsin_metro_bulk_{n}'] = (f'도시권 일괄 사업 {n}단계', f'Metropolitan project stage {n}')
    for lang, i in [('korean', 0), ('english', 1)]:
        lines = [f' {k}: "{v[i]}"' for k, v in labels.items()]
        desc = ('중심도시 10만 이상. 같은 국가의 도로 연결 지점만 최대 24곳까지 묶습니다. 지방 선택 시 조건에 맞는 지점만 편입됩니다. 연결은 분기별 또는 수동으로 재검사하며 실제 인구·식량·노동력을 공유하지 않습니다. 중심은 역할 하나를 고를 수 있고(시설 조건 필요), 역할 보너스는 중심 지점에만 적용됩니다. 일괄 사업은 지점마다 소유·기술·단계·자금을 다시 검사하고, 조건을 못 맞춘 지점은 건너뜁니다.'
                if i == 0 else
                'Core population 100,000. Up to 24 same-country connected locations. Province selection adds eligible locations only. Connections are reviewed quarterly or manually. Does not transfer population, food or labor. A core may pick one role (facility condition needed); role bonuses apply to the core only. Bulk projects recheck owner, technology, stage and cash per site and skip any site that fails.')
        lines += [f' {k}_desc: "{desc}"' for k in labels if k.startswith('tsin_metro_')]
        outputs[f'main_menu/localization/{lang}/tsin_metropolitan_regions_l_{lang}.yml'] = 'l_' + lang + ':\n' + '\n'.join(lines) + '\n'
    return outputs


def integrate():
    # Replace the module in place so the registry order does not change.
    p = pdx.MOD_ROOT / 'ui/dashboard_registry.json'
    d = json.loads(pdx.read_text(p))
    mods = d['modules']
    if any(m['id'] == 'metro_regions' for m in mods):
        d['modules'] = [_registry_module() if m['id'] == 'metro_regions' else m for m in mods]
    else:
        d['modules'] = mods + [_registry_module()]
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    bad = []
    for rel, text in build().items():
        p = pdx.MOD_ROOT / rel
        if a.check:
            if not p.exists() or pdx.read_text(p) != text:
                bad.append(rel)
        else:
            pdx.write_text_bom(p, text)
    if not a.check:
        integrate()
    print('Metropolitan regions:', len(bad), 'differences')
    return bool(bad)


if __name__ == '__main__':
    raise SystemExit(main())
