#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SITE="$ROOT/site"
CLIENT="$ROOT/client"

# Stage the tested client from this commit, including its patched Wasm engine.
test -s "$CLIENT/index.html"
test -s "$CLIENT/version.txt"
for payload in assets mesh-wasm-br server-wasm-br sounds wasm-br; do
  test -s "$CLIENT/payload/eag-inline-$payload.bin"
done

rm -rf "$SITE"
mkdir -p "$SITE/radio" "$SITE/client"
cp "$ROOT/index.html" "$ROOT/launch.html" "$SITE/"
cp "$ROOT/radio/index.html" "$SITE/radio/index.html"
cp -a "$CLIENT/." "$SITE/client/"
echo "Staged Radio Client build $(cat "$CLIENT/version.txt") under /client/."
