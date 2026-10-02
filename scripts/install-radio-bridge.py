#!/usr/bin/env python3
"""Install the Radio Client 26.2 JavaScript bridge into a generated Eagler source tree.

This is deliberately a post-decompile source step: generated Minecraft sources are
never committed to the Radio Client repository.
"""
from pathlib import Path
import argparse
import shutil

HERE = Path(__file__).resolve().parent.parent
BRIDGE = HERE / "engine-patch" / "RadioOptionsBridge.java"

def find_java_root(workspace: Path) -> Path:
    candidates = [
        workspace / "game" / "src" / "main" / "java",
        workspace / "src" / "main" / "java",
    ]
    for root in candidates:
        if (root / "net" / "minecraft").is_dir():
            return root
    raise SystemExit("Could not find generated Java source root")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace", type=Path, help="generated 26.2/Eagler workspace")
    args = ap.parse_args()
    workspace = args.workspace.resolve()
    java_root = find_java_root(workspace)
    client = java_root / "net" / "minecraft" / "client"
    minecraft = client / "Minecraft.java"
    target = client / "RadioOptionsBridge.java"
    if not minecraft.is_file():
        raise SystemExit(f"Missing generated source: {minecraft}")
    if not BRIDGE.is_file():
        raise SystemExit(f"Missing bridge source: {BRIDGE}")
    source = minecraft.read_text(encoding="utf-8")
    marker = "RadioOptionsBridge.install();"
    if marker not in source:
        anchor = "this.options.save();"
        if anchor not in source:
            raise SystemExit("Minecraft.java has no expected this.options.save(); anchor")
        source = source.replace(anchor, anchor + "\n\t\tRadioOptionsBridge.install();", 1)
        minecraft.write_text(source, encoding="utf-8")
        print(f"patched {minecraft}")
    else:
        print(f"already patched {minecraft}")
    shutil.copy2(BRIDGE, target)
    print(f"installed {target}")

if __name__ == "__main__":
    main()
