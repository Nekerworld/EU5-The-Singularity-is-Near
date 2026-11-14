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


def main() -> int:
    jobs = [
        ("icons/age/age_6_revolutions.dds", "icons/age/age_7_industrialization.dds", (235, 190, 130)),
        ("illustrations/advances/age_6_revolutions.dds", "illustrations/advances/age_7_industrialization.dds", (210, 200, 185)),
    ]
    for src, dst, deg in INSTITUTIONS:
        jobs.append((f"icons/institutions/{src}.dds", f"icons/institutions/{dst}.dds", deg))
        jobs.append((f"illustrations/institutions/{src}.dds", f"illustrations/institutions/{dst}.dds", deg))
    jobs.append(("icons/map_modes/institution.dds", "icons/map_modes/tsin_industrial_institutions.dds", 200))
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
