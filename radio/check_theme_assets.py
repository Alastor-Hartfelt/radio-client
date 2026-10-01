#!/usr/bin/env python3
"""Smoke-check the generated Radio Client theme assets.

This verifies that the expected branded textures are generated, have the
Minecraft dimensions we target, and contain visible crimson/cream artwork.
It does not replace a real in-browser visual test.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "theme"

EXPECTED = {
    "assets/minecraft/textures/gui/title/minecraft.png": (1024, 256),
    "assets/minecraft/textures/gui/title/minceraft.png": (1024, 256),
    "assets/minecraft/textures/gui/title/mojangstudios.png": (512, 512),
    "assets/minecraft/textures/gui/title/background/panorama_0.png": (256, 256),
    "assets/minecraft/textures/gui/sprites/widget/button.png": (200, 20),
    "assets/minecraft/textures/gui/sprites/widget/button_highlighted.png": (200, 280),
}

def fail(message):
    raise SystemExit("Radio theme check FAILED: " + message)

images = {}
for relative, dimensions in EXPECTED.items():
    path = THEME / relative
    if not path.is_file() or path.stat().st_size == 0:
        fail("missing generated asset: " + relative)
    with Image.open(path) as source:
        if source.size != dimensions:
            fail(f"{relative}: expected {dimensions}, got {source.size}")
        images[relative] = source.convert("RGBA").copy()

for relative in ("theme_extra/boot_logo.png", "theme_extra/icon.png"):
    path = ROOT / relative
    if not path.is_file() or path.stat().st_size == 0:
        fail("missing generated asset: " + relative)

def count_pixels(image, predicate):
    return sum(1 for r, g, b, a in image.getdata()
               if a > 32 and predicate(r, g, b))

logo = images["assets/minecraft/textures/gui/title/minecraft.png"]
crimson = count_pixels(logo, lambda r, g, b: r > 140 and r > g * 1.5 and r > b * 1.2)
cream = count_pixels(logo, lambda r, g, b: r > 180 and g > 130 and b > 80 and r > g > b)
if crimson < 80:
    fail(f"title logo has too few visible crimson pixels ({crimson})")
if cream < 20:
    fail(f"title logo has too few visible warm-cream pixels ({cream})")

panorama = images["assets/minecraft/textures/gui/title/background/panorama_0.png"]
red_signal = count_pixels(panorama, lambda r, g, b: r > b * 1.5 and r > g * 1.15 and r > 20)
if red_signal < 500:
    fail(f"panorama does not look sufficiently crimson ({red_signal} signal pixels)")

print("Radio theme check passed:")
print(f"  {len(EXPECTED)} generated texture files exist with expected dimensions")
print(f"  title logo: {crimson} crimson pixels, {cream} warm-cream pixels")
print(f"  panorama: {red_signal} crimson signal pixels")
print("  boot logo and favicon exist")
print("  Note: real in-browser rendering still needs manual visual confirmation")
