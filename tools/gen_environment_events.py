"""R05: eight more environment events and one shared yearly popup budget (docs/environment_events.md).

Every major environment popup of a country (pollution petition, water petition, chemical spill and the eight here)
shares one budget: at most one popup per country per calendar year, stored in tsin_env_popup_year.
Events never read weather data; the smog event uses the sustained-exposure counter instead.
"""
from pathlib import Path
import sys, argparse, json
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pdx
from gen_pollution import HEAVY, types

BUDGET = 'tsin_env_popup_available_trigger = yes'

# site: location-scope condition. country: country-scope condition (may be empty).
# cost: gold for option a (0 = free). site_fx: applied to the chosen site when a is taken.
# root_fx: applied to the country when a is taken. decline_fx: applied to the site when b is taken.
EVENTS = [
    dict(n=1, outcome='negative', country='has_variable = tsin_water_petition_cooldown',
         site='var:tsin_pollution_water >= 60 var:tsin_pollution_water_bad_years >= 3 NOT = { has_variable = tsin_water_emergency_services }',
         cost=300, site_fx='set_variable = { name = tsin_water_emergency_services years = 5 }', root_fx='', decline_fx=''),
    dict(n=2, outcome='negative', country='',
         site='tsin_is_polluting_mine = yes var:tsin_pollution_air >= 40',
         cost=200, site_fx='set_variable = { name = tsin_pollution_filters years = 5 }', root_fx='', decline_fx=''),
    dict(n=3, outcome='negative', country='',
         site='var:tsin_pollution_air >= 50 any_buildings_in_location = { building_type = building_type:tsin_steam_metro is_opened = yes }',
         cost=250, site_fx='set_variable = { name = tsin_pollution_filters years = 10 }', root_fx='', decline_fx=''),
    dict(n=4, outcome='negative', country='',
         site='var:tsin_pollution_air >= 70 var:tsin_pollution_bad_years >= 3',
         cost=150, site_fx='set_variable = { name = tsin_pollution_filters years = 3 }', root_fx='', decline_fx=''),
    dict(n=5, outcome='neutral', country='var:tsin_pollution_high_share >= 15',
         site='var:tsin_pollution_water >= 40',
         cost=120, site_fx='set_variable = { name = tsin_water_emergency_services years = 3 }', root_fx='', decline_fx=''),
    dict(n=6, outcome='negative', country='',
         site='has_variable = tsin_pollution_filters var:tsin_pollution_air >= 40',
         cost=80, site_fx='set_variable = { name = tsin_pollution_filters years = 5 }', root_fx='',
         decline_fx='remove_variable = tsin_pollution_filters'),
    dict(n=7, outcome='neutral', country='',
         site='var:tsin_pollution_air >= 70 var:tsin_pollution_bad_years >= 3 any_buildings_in_location = { ' + types(HEAVY) + ' is_opened = yes }',
         cost=400, site_fx='set_variable = { name = tsin_pollution_filters years = 10 }', root_fx='', decline_fx=''),
    dict(n=8, outcome='positive', country='has_variable = tsin_env_peak_high_share var:tsin_pollution_high_share < 5 NOT = { has_variable = tsin_envx_clear_done }',
         site='has_variable = tsin_pollution_year var:tsin_pollution_air <= 25',
         cost=0, site_fx='', root_fx='add_prestige = 5', decline_fx=''),
]

# (title, desc, option a, option b) as (korean, english) pairs.
TEXT = {
    1: (('검게 변한 하천', 'The river turned black'),
        ('정화 청원 이후에도 하천 오염이 이어져 강변 주민들이 다시 항의하고 있습니다. 임시 정화 서비스는 물의 위험을 낮추지만 처리시설을 대신하지는 못합니다.',
         'Pollution continues after the earlier petition and riverside residents protest again. Temporary purification lowers the water risk but does not replace treatment works.'),
        ('정화 사업에 300두캇을 쓴다', 'Spend 300 gold on purification'), ('이번에는 조치하지 않는다', 'Take no action this time')),
    2: (('광산 분진', 'Mine dust'),
        ('광산 주변 주민들이 분진과 갱내 배출을 호소합니다. 분진 억제 설비는 노출을 줄이지만 광산 산출은 줄이지 않습니다.',
         'Residents near the mines complain of dust and pit discharge. Dust suppression lowers exposure but does not reduce mine output.'),
        ('분진 억제 설비에 200두캇을 쓴다', 'Spend 200 gold on dust suppression'), ('지금은 두고 본다', 'Wait and see')),
    3: (('지하철 환기 문제', 'Metro ventilation'),
        ('증기 지하철의 연기가 승강장과 인근 거리에 고입니다. 환기 설비로 노출을 줄일 수 있습니다.',
         'Steam metro smoke hangs over the platforms and nearby streets. Ventilation equipment can reduce exposure.'),
        ('환기 설비에 250두캇을 쓴다', 'Spend 250 gold on ventilation'), ('운행을 그대로 유지한다', 'Keep service unchanged')),
    4: (('공업 도시의 연무', 'Industrial smog'),
        ('고농도 매연이 여러 해 이어져 도시가 뒤덮였습니다. 게임에는 기상 자료가 없어 고노출이 지속된 기간을 연무의 지표로 씁니다. 대기 경보는 배출을 잠시 줄입니다.',
         'High smoke levels have persisted for years. The game has no weather data, so sustained high exposure stands in for smog. An air alert reduces emissions for a while.'),
        ('대기 경보와 연무 통제에 150두캇을 쓴다', 'Spend 150 gold on an air alert and smog control'), ('경보를 발령하지 않는다', 'Issue no alert')),
    5: (('산업 위생 조사단', 'Industrial hygiene commission'),
        ('의사와 공무원으로 구성된 조사단이 공장 지구의 식수와 배수로를 점검하려 합니다. 임시 점검은 수질 위험을 3년간 낮추지만 하수도 투자를 대신하지 않습니다.',
         'A commission of doctors and officials proposes inspecting drinking water and drains in the factory districts. Inspections lower water risk for three years but do not replace sewerage.'),
        ('조사단 파견에 120두캇을 쓴다', 'Spend 120 gold on the commission'), ('조사단을 보내지 않는다', 'Send no commission')),
    6: (('여과 설비의 운영비', 'Filter running costs'),
        ('지원으로 설치된 여과 설비에 운영비가 다시 필요해졌습니다. 운영비를 내면 설비가 5년 더 유지되고, 중단하면 설비가 철거되어 배출이 원래대로 돌아갑니다.',
         'Installed filters need running costs again. Paying keeps them for five more years; stopping removes them and emissions return to their previous level.'),
        ('운영비 80두캇을 내고 5년 더 유지한다', 'Pay 80 gold and keep the filters for five years'), ('설비를 철거한다', 'Remove the filters')),
    7: (('공장 이전 논쟁', 'Relocation debate'),
        ('공해가 심한 공장을 도시 밖으로 옮기자는 논쟁이 벌어졌습니다. 이 게임은 건물을 옮기지 않으므로, 옮기는 대신 설비 전환을 지원합니다.',
         'A debate over moving the worst polluting works out of town. Buildings cannot move in this game, so the response is a conversion grant instead.'),
        ('설비 전환에 400두캇을 지원한다', 'Grant 400 gold for conversion'), ('논쟁을 그대로 둔다', 'Leave the debate unresolved')),
    8: (('맑아진 하늘', 'Clearer skies'),
        ('오랜 매연 끝에 도시의 하늘이 맑아졌습니다. 시민들은 정화 사업을 기념합니다.',
         'After long years of smoke the city sky has cleared. Citizens celebrate the clean-up.'),
        ('기념식을 연다 (위신 +5)', 'Hold a celebration (+5 prestige)'), ('과거를 잊지 않는다', 'Remember the past')),
}


def _country_limit(e):
    parts = [BUDGET, 'is_ai = no']
    if e['country']:
        parts.append(e['country'])
    parts.append(f"any_owned_location = {{ {e['site']} }}")
    return ' '.join(parts)


def _event(e):
    n = e['n']
    lines = [f'tsin_envx.{n} = {{',
             '\ttype = country_event',
             f'\ttitle = tsin_envx.{n}.title',
             f'\tdesc = tsin_envx.{n}.desc',
             f"\toutcome = {e['outcome']}",
             '\tillustration_tags = { 10 = interior 10 = regular }',
             '',
             '\ttrigger = {',
             f'\t\t{_country_limit(e)}',
             '\t}',
             '',
             '\timmediate = {',
             '\t\ttsin_env_popup_claim_effect = yes']
    if n == 8:
        lines.append('\t\tset_variable = { name = tsin_envx_clear_done }')
    else:
        lines.append(f"\t\trandom_owned_location = {{ limit = {{ {e['site']} }} save_scope_as = tsin_envx_site }}")
    lines.append('\t}')
    lines.append('')
    # option a
    cost = e['cost']
    lines += [f'\toption = {{', f'\t\tname = tsin_envx.{n}.a']
    if cost:
        lines.append(f'\t\ttrigger = {{ gold >= {cost} }}')
        lines.append(f'\t\tadd_gold = -{cost}')
    if e['site_fx']:
        lines.append(f"\t\tscope:tsin_envx_site = {{ {e['site_fx']} }}")
    if e['root_fx']:
        lines.append(f"\t\t{e['root_fx']}")
    if n == 8:
        lines.append('\t\tset_variable = { name = tsin_envx_clear_done }')
    lines += ['\t\tai_chance = { factor = 3 }', '\t}', '']
    # option b
    lines += [f'\toption = {{', f'\t\tname = tsin_envx.{n}.b']
    if e['decline_fx']:
        lines.append(f"\t\tscope:tsin_envx_site = {{ {e['decline_fx']} }}")
    lines += ['\t\tai_chance = { factor = 1 }', '\t}', '}', '']
    return '\n'.join(lines)


def build_events():
    head = ('namespace = tsin_envx\n\n'
            '# Environment events (docs/environment_events.md). Fired from tsin_envx_yearly_pulse (on_action/tsin_on_actions.txt).\n'
            '# Each claims the shared yearly popup budget in immediate; the trigger refuses a second popup in the same year.\n\n')
    return head + '\n'.join(_event(e) for e in EVENTS)


def build_triggers():
    return ('# Country scope. At most one major environment popup per country per year: pollution and water petitions,\n'
            '# chemical spills and tsin_envx events share this budget.\n'
            'tsin_env_popup_available_trigger = {\n'
            '\tOR = {\n'
            '\t\tNOT = { has_variable = tsin_env_popup_year }\n'
            '\t\tcurrent_year > var:tsin_env_popup_year\n'
            '\t}\n'
            '}\n')


def build_effects():
    return ('# Country scope. Records that this year\'s popup budget is used.\n'
            'tsin_env_popup_claim_effect = {\n'
            '\tset_variable = { name = tsin_env_popup_year value = current_year }\n'
            '}\n')


def build_loc(lang):
    idx = 0 if lang == 'korean' else 1
    rows = []
    for e in EVENTS:
        n = e['n']
        title, desc, a, b = TEXT[n]
        rows += [(f'tsin_envx.{n}.title', title[idx]), (f'tsin_envx.{n}.desc', desc[idx]),
                 (f'tsin_envx.{n}.a', a[idx]), (f'tsin_envx.{n}.b', b[idx])]
    return 'l_' + lang + ':\n' + ''.join(f' {k}: {json.dumps(v, ensure_ascii=False)}\n' for k, v in rows)


def build():
    out = {
        'in_game/events/tsin_environment_events.txt': build_events(),
        'in_game/common/scripted_triggers/tsin_environment_events.txt': build_triggers(),
        'in_game/common/scripted_effects/tsin_environment_events.txt': build_effects(),
    }
    for lang in ('korean', 'english'):
        out[f'main_menu/localization/{lang}/tsin_environment_events_l_{lang}.yml'] = build_loc(lang)
    return out


PULSE = '''# root = country. Environment popups (docs/environment_events.md). Records the peak of high exposure, then at most one popup a year.
tsin_envx_yearly_pulse = {
	trigger = {
		is_ai = no
	}
	effect = {
		if = {
			limit = { has_variable = tsin_pollution_high_share var:tsin_pollution_high_share >= 20 }
			set_variable = tsin_env_peak_high_share
		}
	}
	random_events = {
''' + ''.join(f'\t\t10 = tsin_envx.{n}\n' for n in range(1, 9)) + '''
		chance_to_happen = 15
	}
}

'''


def integrate():
    # Existing popups claim the same budget. Their source generators hold the trigger text.
    p = pdx.MOD_ROOT / 'tools/gen_pollution.py'
    s = p.read_text(encoding='utf-8')
    old = 'NOT = { has_variable = tsin_pollution_petition_cooldown } var:tsin_pollution_high_share >= 10 }'
    if 'tsin_env_popup_available_trigger' not in s:
        if s.count(old) != 1:
            raise RuntimeError('pollution petition trigger not found')
        s = s.replace(old, 'NOT = { has_variable = tsin_pollution_petition_cooldown } var:tsin_pollution_high_share >= 10 tsin_env_popup_available_trigger = yes }')
        s = s.replace('   trigger_event_non_silently = tsin_pollution.1', '   tsin_env_popup_claim_effect = yes\n   trigger_event_non_silently = tsin_pollution.1', 1)
        p.write_text(s, encoding='utf-8')
    p = pdx.MOD_ROOT / 'tools/gen_environment.py'
    s = p.read_text(encoding='utf-8')
    old = 'if = { limit = { is_ai = no var:tsin_pollution_water_high_share >= 10 NOT = { has_variable = tsin_water_petition_cooldown } }'
    if 'tsin_env_popup_available_trigger' not in s:
        if s.count(old) != 1:
            raise RuntimeError('water petition trigger not found')
        s = s.replace(old, old.replace('is_ai = no ', 'is_ai = no tsin_env_popup_available_trigger = yes '))
        s = s.replace('   trigger_event_non_silently = tsin_environment.1', '   tsin_env_popup_claim_effect = yes\n   trigger_event_non_silently = tsin_environment.1', 1)
        p.write_text(s, encoding='utf-8')
    p = pdx.MOD_ROOT / 'tools/gen_industrial_safety.py'
    s = p.read_text(encoding='utf-8')
    if 'tsin_env_popup_available_trigger' not in s:
        old = '  NOT = {{ has_variable = tsin_spill_district_cooldown }}'
        if s.count(old) != 1:
            raise RuntimeError('spill cooldown line not found')
        s = s.replace(old, old + '\n  owner ?= {{ tsin_env_popup_available_trigger = yes }}')
        s = s.replace('    trigger_event_non_silently = tsin_industrial_safety.1', '    tsin_env_popup_claim_effect = yes\n    trigger_event_non_silently = tsin_industrial_safety.1', 1)
        p.write_text(s, encoding='utf-8')
    p = pdx.MOD_ROOT / 'in_game/common/on_action/tsin_on_actions.txt'
    s = p.read_text(encoding='utf-8')
    if 'tsin_envx_yearly_pulse' not in s:
        s = s.replace('\t\ttsin_society_yearly_pulse\n', '\t\ttsin_society_yearly_pulse\n\t\ttsin_envx_yearly_pulse\n', 1)
        s = s.replace('# root = country. Factory flavor events;', PULSE + '# root = country. Factory flavor events;', 1)
        p.write_text(s, encoding='utf-8')


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
    print('Environment events:', len(bad), 'differences')
    return bool(bad)


if __name__ == '__main__':
    raise SystemExit(main())
