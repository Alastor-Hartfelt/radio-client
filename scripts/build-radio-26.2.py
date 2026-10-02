#!/usr/bin/env python3
"""Build Radio Client from an authorized local Minecraft 26.2 JAR.

This is intentionally a local build helper: the vanilla JAR, generated/decompiled
sources, and resulting client HTML never need to be committed to GitHub.

The helper:
  1. reconstructs the authenticated Eagler 26.2 workspace,
  2. installs RadioOptionsBridge into the generated Java sources,
  3. builds the standalone 26.2 browser client,
  4. feeds that client into the normal Radio Client HTML/theme pipeline.

The setup directory is the portable Eaglercraft 26.2 u1 setup package.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise SystemExit(f"Missing {label}: {path}")
    return path


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("\n[Radio build] $ " + " ".join(str(x) for x in cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--jar", type=Path, required=True,
                    help="authorized local Minecraft 26.2 client JAR")
    ap.add_argument("--setup", type=Path, required=True,
                    help="Eaglercraft 26.2 u1 portable setup directory")
    ap.add_argument("--java17", type=Path, required=True,
                    help="Java 17 executable used by the patcher/decompile stage")
    ap.add_argument("--java25", type=Path, required=True,
                    help="Java 25 executable used by the final MC/TeaVM build")
    ap.add_argument("--node", type=Path, default=None,
                    help="Node executable (defaults to PATH)")
    ap.add_argument("--npm", type=Path, default=None,
                    help="npm launcher/CLI (defaults to PATH)")
    ap.add_argument("--workspace", type=Path, default=ROOT / ".radio-26.2-workspace",
                    help="temporary generated workspace (default: .radio-26.2-workspace)")
    ap.add_argument("--standalone", type=Path,
                    default=ROOT / ".radio-26.2-standalone.html",
                    help="temporary standalone HTML output")
    ap.add_argument("--keep-workspace", action="store_true",
                    help="keep the generated/decompiled workspace after a successful build")
    args = ap.parse_args()

    setup = args.setup.resolve()
    jar = require_file(args.jar.resolve(), "Minecraft 26.2 JAR")
    patcher = require_file(setup / "eagler-patcher", "eagler-patcher")
    bundle = require_file(setup / "source-patch-bundle.zip", "source patch bundle")
    vineflower = require_file(setup / "inputs" / "vineflower-1.12.0.jar", "Vineflower")
    skeleton = require_file(setup / "project-skeleton-v5-teavm-runtime-verified.zip",
                            "project skeleton")
    sounds = require_file(setup / "inputs" / "sounds.epk", "sounds.epk")
    music = require_file(setup / "inputs" / "music.epk", "music.epk")
    resource_overlay = setup / "inputs" / "resource-overlay-normal.zip"

    node = str(args.node.resolve()) if args.node else (shutil.which("node") or "")
    npm = str(args.npm.resolve()) if args.npm else (shutil.which("npm") or "")
    if not node:
        raise SystemExit("Node was not found; pass --node /path/to/node")
    if not npm:
        raise SystemExit("npm was not found; pass --npm /path/to/npm")

    # The portable kit publishes these authenticated input hashes alongside the
    # files, so the wrapper does not invent or silently trust replacement inputs.
    def hash_from_file(name: str) -> str:
        p = setup / "inputs" / name
        return require_file(p, name).read_text(encoding="utf-8").strip().split()[0]

    sounds_sha = hash_from_file("sounds.epk.sha256")
    music_sha = hash_from_file("music.epk.sha256")
    bundle_sha = sha256(bundle)
    skeleton_sha = sha256(skeleton)
    overlay_sha = sha256(resource_overlay) if resource_overlay.is_file() else None

    workspace = args.workspace.resolve()
    standalone = args.standalone.resolve()
    if workspace.exists():
        raise SystemExit(
            f"Workspace already exists: {workspace}\n"
            "Use a new path or remove it after confirming it contains no work you need."
        )
    if standalone.exists():
        raise SystemExit(f"Standalone output already exists: {standalone}")

    create = [
        str(patcher), "create-dev",
        "--jar", str(jar),
        "--output", str(workspace),
        "--vineflower", str(vineflower),
        "--java17", str(args.java17.resolve()),
        "--patch-bundle", str(bundle),
        "--expected-bundle-sha256", bundle_sha,
        "--project-skeleton", str(skeleton),
        "--expected-skeleton-sha256", skeleton_sha,
    ]
    if overlay_sha:
        create += [
            "--resource-overlay", str(resource_overlay),
            "--expected-resource-overlay-sha256", overlay_sha,
            "--external-resource-root", str(setup / "inputs"),
        ]
    run(create)

    run([
        sys.executable, str(ROOT / "scripts" / "install-radio-bridge.py"),
        str(workspace),
    ])

    build = [
        str(patcher), "build-standalone",
        "--jar", str(jar),
        "--output", str(workspace),
        "--vineflower", str(vineflower),
        "--java17", str(args.java17.resolve()),
        "--java25", str(args.java25.resolve()),
        "--node", node,
        "--npm", npm,
        "--patch-bundle", str(bundle),
        "--expected-bundle-sha256", bundle_sha,
        "--project-skeleton", str(skeleton),
        "--expected-skeleton-sha256", skeleton_sha,
        "--sounds-epk", str(sounds),
        "--expected-sounds-epk-sha256", sounds_sha,
        "--music-epk", str(music),
        "--expected-music-epk-sha256", music_sha,
        "--standalone-output", str(standalone),
        "--reuse-project",
    ]
    if overlay_sha:
        build += [
            "--resource-overlay", str(resource_overlay),
            "--expected-resource-overlay-sha256", overlay_sha,
            "--external-resource-root", str(setup / "inputs"),
        ]
    run(build)

    ref = ROOT / "ref" / "wispcraft-26.2.html"
    ref.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(standalone, ref)
    print(f"\n[Radio build] 26.2 engine ready: {ref}")
    run([sys.executable, str(ROOT / "build.py")], cwd=ROOT)

    if not args.keep_workspace:
        shutil.rmtree(workspace)
    standalone.unlink(missing_ok=True)
    print("\n[Radio build] Done. The normal Radio build output is in dist/.")


if __name__ == "__main__":
    main()
