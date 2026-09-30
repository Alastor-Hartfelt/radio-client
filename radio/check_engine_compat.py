#!/usr/bin/env python3
"""Read-only compatibility probe for Radio's existing single-file HTML patcher.

This does not modify the input or claim that a passing result proves the game
will launch. It checks the literal anchors currently required by build.py.
"""
import re
import sys
from pathlib import Path

if len(sys.argv) != 2:
    raise SystemExit("Usage: python radio/check_engine_compat.py path/to/index.html")

path = Path(sys.argv[1])
if not path.is_file():
    raise SystemExit(f"Input file not found: {path}")

size = path.stat().st_size
print(f"Input: {path.name} ({size:,} bytes)")
html = path.read_text(encoding="utf-8", errors="replace")

checks = []
payload = re.search(
    r'<script type="application/octet-stream" id="eag-inline-assets" data-size="(\d+)">(.*?)</script>',
    html,
    re.S,
)
checks.append(("inline assets payload block", payload is not None))

if payload:
    declared_size = int(payload.group(1))
    encoded = re.sub(r"\s", "", payload.group(2))
    import base64
    try:
        decoded_size = len(base64.b64decode(encoded, validate=True))
        payload_size_ok = decoded_size == declared_size
    except Exception:
        decoded_size = -1
        payload_size_ok = False
    checks.append(("inline assets base64 matches declared data-size", payload_size_ok))
    size_anchor = f"var size = {declared_size};"
    checks.append(("single bootstrap size marker", html.count(size_anchor) == 1))
else:
    decoded_size = -1
    checks.append(("single bootstrap size marker", False))

boot = '\t\t(async () => {\n\t\t\ttry {\n\t\t\t\twindow.__eagPrepareInlineAssets();'
checks.extend([
    ("exact pre-boot anchor", html.count(boot) == 1),
    ('one <script type="module"> anchor', html.count('<script type="module">') == 1),
    ("expected Eaglercraft title", '<title>Eaglercraft 26.2 0.6-dev</title>' in html),
    ("expected inline icon pattern", re.search(r'<link rel="icon" type="image/png" href="data:image/png;base64,[^"]*">', html) is not None),
    ("sync payload decoder anchor", html.count("  function decodePayload(id) {\n") == 1),
    ("async payload decoder anchor", html.count("  function decodePayloadAsync(id) {\n") == 1),
    ("inline WASM release anchor", html.count("  window.__eagReleaseInlineWasm = function () {") == 1),
    ("WASM worker runtime anchor", html.count('\t\t\t\t\twindow.__eaglerWasmRuntimeURL = null;\n') == 1),
    ("server worker bootstrap anchor", html.count("window.__eaglerWasmServerWorkerBootstrapURL = URL.createObjectURL(new Blob([\n") == 1),
    ("worker asset-buffer anchor", html.count("if (assetBuffer) return assetBuffer;\\n") == 1),
])

for label, ok in checks:
    print(f'{"PASS" if ok else "FAIL"}  {label}')
print(f"\nSummary: {sum(ok for _, ok in checks)}/{len(checks)} checks passed")
print(f"Decoded inline asset bytes: {decoded_size:,}" if decoded_size >= 0 else "Decoded inline asset bytes: unavailable")
if not all(ok for _, ok in checks):
    print("\nThis HTML does not match every current build.py anchor. Do not run the full patcher unchanged.")
    raise SystemExit(1)
print("\nAnchor compatibility only; this does NOT prove a full build or browser launch will succeed.")
