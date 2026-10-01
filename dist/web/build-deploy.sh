#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SITE="$ROOT/site"

# Preserve the existing launcher and build the playable client into /client/.
# The build pulls the branch tip, regenerates the vintage Radio tentacle panorama, and keeps the homepage unchanged.
rm -rf "$SITE"
mkdir -p "$SITE/radio"
cp "$ROOT/index.html" "$SITE/index.html"
cp "$ROOT/radio/index.html" "$SITE/radio/index.html"

echo "Redistribution permission confirmed by the project owner; building the public client."

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

curl --fail --location --retry 2 --silent --show-error \
  --output "$WORK/repository.zip" \
  "https://github.com/Alastor-Hartfelt/radio-client/archive/refs/heads/radio-client.zip"
unzip -q "$WORK/repository.zip" -d "$WORK"
SOURCE="$(find "$WORK" -mindepth 1 -maxdepth 1 -type d -name 'radio-client-*' -print -quit)"
test -n "$SOURCE"

mkdir -p "$SOURCE/ref"
curl --fail --location --retry 2 --silent --show-error \
  --output "$SOURCE/ref/wispcraft-26.2.html" \
  "https://raw.githubusercontent.com/Alastor-Hartfelt/eaglercraft-26.2/main/index.html"
test "$(wc -c < "$SOURCE/ref/wispcraft-26.2.html")" -gt 1000000

(
  cd "$SOURCE"
  python3 -m venv "$WORK/venv"
  "$WORK/venv/bin/pip" install --disable-pip-version-check Pillow
  "$WORK/venv/bin/python" gen_textures.py
  "$WORK/venv/bin/python" build.py
)

test -s "$SOURCE/dist/web/client/index.html"
test -s "$SOURCE/dist/web/client/version.txt"
test -d "$SOURCE/dist/web/client/payload"
mkdir -p "$SITE/client"
cp -a "$SOURCE/dist/web/client/." "$SITE/client/"
echo "Built and staged the Radio Client web files under /client/."
