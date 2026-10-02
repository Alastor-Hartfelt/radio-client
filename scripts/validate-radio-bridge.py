#!/usr/bin/env python3
"""Validate that the Radio 26.2 bridge targets the real 26.2 client API.

This does not compile the game. It uses javap against an authorized local
26.2 client JAR to catch bridge/API drift before the expensive TeaVM build.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "engine-patch" / "RadioOptionsBridge.java"

OPTION_METHODS = [
    "renderDistance", "simulationDistance", "framerateLimit", "gamma",
    "guiScale", "enableVsync", "bobView", "toggleSprint", "toggleCrouch",
    "ambientOcclusion", "cloudRange", "weatherRadius", "entityShadows",
    "cutoutLeaves", "improvedTransparency", "vignette",
    "menuBackgroundBlurriness", "mipmapLevels", "biomeBlendRadius",
    "rawMouseInput", "showAutosaveIndicator", "reducedDebugInfo",
    "damageTiltStrength", "fovEffectScale", "screenEffectScale",
    "hideLightningFlash",
]

def javap(jar: Path, cls: str) -> str:
    p = subprocess.run(
        ["javap", "-classpath", str(jar), "-p", cls],
        text=True, capture_output=True,
    )
    if p.returncode:
        raise SystemExit(p.stderr.strip() or f"javap failed for {cls}")
    return p.stdout

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jar", type=Path, required=True)
    ap.add_argument("--workspace", type=Path)
    args = ap.parse_args()

    jar = args.jar.resolve()
    if not jar.is_file():
        raise SystemExit(f"Missing 26.2 JAR: {jar}")
    bridge = BRIDGE.read_text(encoding="utf-8")

    options = javap(jar, "net.minecraft.client.Options")
    missing = [m for m in OPTION_METHODS
               if not re.search(r"\b" + re.escape(m) + r"\(\);", options)]
    if missing:
        raise SystemExit("Options API drift: missing " + ", ".join(missing))

    minecraft = javap(jar, "net.minecraft.client.Minecraft")
    if not re.search(r"\bpublic static net\.minecraft\.client\.Minecraft getInstance\(\);", minecraft):
        raise SystemExit("Minecraft.getInstance() is missing")
    if not re.search(r"\bpublic java\.util\.concurrent\.CompletableFuture<java\.lang\.Void> reloadResourcePacks\(\);", minecraft):
        raise SystemExit("Minecraft.reloadResourcePacks() is missing")

    required = ["RadioOptionsBridge.install();", "this.options.save();"]
    if args.workspace:
        src = args.workspace.resolve() / "game" / "src" / "main" / "java" / "net" / "minecraft" / "client" / "Minecraft.java"
        if not src.is_file():
            src = args.workspace.resolve() / "src" / "main" / "java" / "net" / "minecraft" / "client" / "Minecraft.java"
        if not src.is_file():
            raise SystemExit(f"Generated Minecraft.java not found under {args.workspace}")
        generated = src.read_text(encoding="utf-8")
        required = ["this.options.save();", "RadioOptionsBridge.install();"]
        if any(x not in generated for x in required):
            raise SystemExit("Generated Minecraft.java is missing the bridge hookup")
        if generated.count("RadioOptionsBridge.install();") != 1:
            raise SystemExit("Generated Minecraft.java contains duplicate bridge hookups")

    if "globalThis.Radio26Options" not in bridge or "javaMethods.get" not in bridge:
        raise SystemExit("RadioOptionsBridge is missing its TeaVM browser seam")

    print("Radio 26.2 bridge validation passed.")
    print(f"Validated {len(OPTION_METHODS)} Options methods plus Minecraft.getInstance/reloadResourcePacks.")

if __name__ == "__main__":
    main()
