"""Build placeholder age-7 and institution DDS files by recolouring vanilla art.

Final art should replace these files (same paths, same size/format):
  icons/age/age_7_industrialization.dds              256x256 (vanilla DXT5)
  illustrations/advances/age_7_industrialization.dds 1080x440 (vanilla DXT1)
Placeholders are written as uncompressed 32-bit DDS.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pdx  # noqa: E402

SRC = pdx.game_root() / "main_menu/gfx/interface"
DST = pdx.MOD_ROOT / "main_menu/gfx/interface"
PREVIEW = pdx.MOD_ROOT / "tools/out"


def tint(im: Image.Image, light: tuple[int, int, int]) -> Image.Image:
    rgba = im.convert("RGBA")
    alpha = rgba.getchannel("A")
    gray = ImageOps.grayscale(rgba)
    col = ImageOps.colorize(gray, black=(20, 18, 16), white=light, mid=(110, 95, 80))
    col = ImageEnhance.Contrast(col).enhance(1.15).convert("RGBA")
    col.putalpha(alpha)
    return col


def save_uncompressed_dds(im: Image.Image, path: Path) -> None:
    """32-bit BGRA DDS without mipmaps (Pillow's BC encoder segfaults on 1080-wide images)."""
    im = im.convert("RGBA")
    w, h = im.size
    header = struct.pack(
        "<4s7I44x13I",
        b"DDS ", 124,
        0x1 | 0x2 | 0x4 | 0x8 | 0x1000,  # caps|height|width|pitch|pixelformat
        h, w, w * 4, 0, 1,
        32, 0x41, 0, 32,  # pixel format: size, RGB|ALPHAPIXELS, fourcc, bitcount
        0x00FF0000, 0x0000FF00, 0x000000FF, 0xFF000000,
        0x1000, 0, 0, 0, 0,  # caps: texture
    )
    r, g, b, a = im.split()
    data = Image.merge("RGBA", (b, g, r, a)).tobytes()
    path.write_bytes(header + data)


def roman_vii(icon: Image.Image) -> Image.Image:
    """Turn the vanilla "VI" medallion into "VII" by squeezing V and I and repeating I."""
    top, bottom = 52, 208
    v = icon.crop((30, top, 156, bottom))
    i = icon.crop((158, top, 222, bottom))
    out = icon.copy()
    x = 34
    v2 = v.resize((96, bottom - top), Image.LANCZOS)
    i2 = i.resize((44, bottom - top), Image.LANCZOS)
    for part in (v2, i2, i2):
        out.paste(part, (x, top))
        x += part.width + 2
    return out


def hue_shift(im: Image.Image, degrees: int) -> Image.Image:
    rgba = im.convert("RGBA")
    alpha = rgba.getchannel("A")
    h, s, v = rgba.convert("RGB").convert("HSV").split()
    shift = int(degrees / 360 * 255)
    h = h.point(lambda x: (x + shift) % 256)
    out = Image.merge("HSV", (h, s, v)).convert("RGBA")
    out.putalpha(alpha)
    return out


# (vanilla source, mod target, recolour)
INSTITUTIONS = [
    ("industrialization", "tsin_industrial_capitalism", 200),
    ("printing_press", "tsin_mass_society", 120),
    ("scientific_revolution", "tsin_electrification", 60),
]

# Goods, modifier-type, building and map mode placeholders: (vanilla source, mod target, hue shift)
EXTRA = [
    ("icons/trade_goods/icon_goods_steel.dds", "icons/trade_goods/icon_goods_tsin_engines.dds", 30),
    ("icons/trade_goods/illustrations/icon_goods_steel.dds", "icons/trade_goods/illustrations/icon_goods_tsin_engines.dds", 30),
    ("icons/modifier_types/steel_positive.dds", "icons/modifier_types/tsin_engines_positive.dds", 30),
    ("icons/modifier_types/steel_negative.dds", "icons/modifier_types/tsin_engines_negative.dds", 30),
    ("icons/modifier_types/global_steel_pop_demand.dds", "icons/modifier_types/global_tsin_engines_pop_demand.dds", 30),
    ("icons/modifier_types/steel_impacts_inflation.dds", "icons/modifier_types/tsin_engines_impacts_inflation.dds", 30),
    ("icons/buildings/steel_mill.dds", "icons/buildings/tsin_machine_works.dds", 30),
    ("icons/buildings/textile_mill.dds", "icons/buildings/tsin_mechanized_textile_mill.dds", 200),
    ("icons/map_modes/building_based.dds", "icons/map_modes/tsin_industrialization.dds", 30),
    ("icons/map_modes/net_building_profit.dds", "icons/map_modes/tsin_industrial_investment.dds", 200),
    ("icons/international_organizations/defensive_league.dds", "icons/international_organizations/tsin_customs_union.dds", 120),
    ("illustrations/international_organization_types/defensive_league.dds", "illustrations/international_organization_types/tsin_customs_union.dds", 120),
    ("icons/industry_types/crafts.dds", "icons/industry_types/tsin_machinery.dds", 30),
    ("icons/buildings/dyes_mill.dds", "icons/buildings/tsin_fertilizer_plant.dds", 90),
    ("icons/buildings/cannons_factory.dds", "icons/buildings/tsin_explosives_plant.dds", 330),
    ("icons/buildings/windmill.dds", "icons/buildings/tsin_fertilized_fields.dds", 90),
    ("icons/buildings/local_smelters.dds", "icons/buildings/tsin_blasting_works.dds", 330),
    ("icons/buildings/bridge_infrastructure.dds", "icons/buildings/tsin_railway_station.dds", 30),
    ("illustrations/missions/generic_capital_economy.dds", "illustrations/missions/tsin_industrialization.dds", 30),
    ("icons/situations/little_ice_age.dds", "icons/situations/tsin_long_depression.dds", 150),
    ("illustrations/situation/little_ice_age.dds", "illustrations/situation/tsin_long_depression.dds", 150),
    ("icons/situations/colonial_revolution.dds", "icons/situations/tsin_scramble_for_colonies.dds", 60),
    ("illustrations/situation/colonial_revolution.dds", "illustrations/situation/tsin_scramble_for_colonies.dds", 60),
    ("icons/situations/the_revolution.dds", "icons/situations/tsin_springtime_of_nations.dds", 90),
    ("illustrations/situation/the_revolution.dds", "illustrations/situation/tsin_springtime_of_nations.dds", 90),
    ("icons/government_reforms/illustrations/the_combination_act.dds", "icons/government_reforms/illustrations/tsin_factory_inspectorate.dds", 120),
    ("icons/government_reforms/illustrations/bureaucratized_administration.dds", "icons/government_reforms/illustrations/tsin_civil_service_examinations.dds", 120),
    ("icons/government_reforms/illustrations/mass_levy_system.dds", "icons/government_reforms/illustrations/tsin_universal_conscription.dds", 120),
    ("icons/government_reforms/illustrations/production_quota_bureaus.dds", "icons/government_reforms/illustrations/tsin_railway_nationalization.dds", 120),
    ("icons/privileges/formal_guilds.dds", "icons/privileges/tsin_chambers_of_commerce.dds", 120),
    ("icons/privileges/nobles_offensive_military_doctrine.dds", "icons/privileges/tsin_officer_corps_monopoly.dds", 120),
    ("icons/privileges/appoint_ecclesiastical_offices.dds", "icons/privileges/tsin_church_school_network.dds", 120),
    ("icons/privileges/peasants_free_peasantry.dds", "icons/privileges/tsin_mutual_aid_societies.dds", 120),
]

for _good, _src, _deg in (("tsin_fertilizer", "saltpeter", 90), ("tsin_explosives", "saltpeter", 330), ("tsin_rubber", "fiber_crops", 60), ("tsin_oil", "tar", 240)):
    EXTRA += [
        (f"icons/trade_goods/icon_goods_{_src}.dds", f"icons/trade_goods/icon_goods_{_good}.dds", _deg),
        (f"icons/trade_goods/illustrations/icon_goods_{_src}.dds", f"icons/trade_goods/illustrations/icon_goods_{_good}.dds", _deg),
        (f"icons/modifier_types/{_src}_positive.dds", f"icons/modifier_types/{_good}_positive.dds", _deg),
        (f"icons/modifier_types/{_src}_negative.dds", f"icons/modifier_types/{_good}_negative.dds", _deg),
        ("icons/modifier_types/global_steel_pop_demand.dds", f"icons/modifier_types/global_{_good}_pop_demand.dds", _deg),
        (f"icons/modifier_types/{_src}_impacts_inflation.dds", f"icons/modifier_types/{_good}_impacts_inflation.dds", _deg),
    ]


def main() -> int:
    jobs = [
        ("icons/age/age_6_revolutions.dds", "icons/age/age_7_industrialization.dds", (235, 190, 130)),
        ("illustrations/advances/age_6_revolutions.dds", "illustrations/advances/age_7_industrialization.dds", (210, 200, 185)),
    ]
    for src, dst, deg in INSTITUTIONS:
        jobs.append((f"icons/institutions/{src}.dds", f"icons/institutions/{dst}.dds", deg))
        jobs.append((f"illustrations/institutions/{src}.dds", f"illustrations/institutions/{dst}.dds", deg))
    jobs.append(("icons/map_modes/institution.dds", "icons/map_modes/tsin_industrial_institutions.dds", 200))
    jobs.extend(EXTRA)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    for src, dst, recolour in jobs:
        source = Image.open(SRC / src)
        im = hue_shift(source, recolour) if isinstance(recolour, int) else tint(source, recolour)
        if "icons/age" in dst:
            im = roman_vii(im)
        out = DST / dst
        out.parent.mkdir(parents=True, exist_ok=True)
        save_uncompressed_dds(im, out)
        check = Image.open(out)
        print(dst, check.size, check.mode)
        check.convert("RGBA").save(PREVIEW / (out.stem + "_" + out.parent.name + ".png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
