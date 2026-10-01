"""Builds Rise Client from the Eaglercraft 26.2 single-file offline build.

    .venv/bin/python gen_textures.py   # (re)generate the theme
    python3 build.py                   # -> dist/RiseClient.html

Steps: re-skin assets.epk with theme/, inject src/rise.js before the boot
script, make the boot wait for Rise's pre-boot options pass, and re-brand the
HTML loading screen.
"""
import base64, os, re, struct, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
from epk import read_epk, write_epk

BASE = os.path.join(ROOT, 'ref', 'wispcraft-26.2.html')
THEME = os.path.join(ROOT, 'theme')
OUT = os.path.join(ROOT, 'dist', 'RadioClient.html')
LINE = 262144  # base64 line length used by the page's chunked decoder


def b64_lines(data):
    s = base64.b64encode(data).decode('ascii')
    return '\n' + '\n'.join(s[i:i + LINE] for i in range(0, len(s), LINE)) + '\n'


def theme_files():
    out = {}
    for dp, _, fns in os.walk(THEME):
        for fn in fns:
            full = os.path.join(dp, fn)
            out[os.path.relpath(full, THEME).replace(os.sep, '/')] = open(full, 'rb').read()
    return out


LANG = {
    'credits_and_attribution.button.credits': 'Mods',
}
FAST_START = True  # swap 1562 recipe-unlock advancements for one that unlocks everything
# Unifont covers every script (7.7 MB of hex) and the game parses it twice on each
# start (default + uniform fonts). Keep Latin/Greek/Cyrillic, punctuation, symbols,
# arrows, box drawing and full-width forms; other scripts show as boxes.
UNIFONT_KEEP = [(0x0000, 0x0600), (0x1D00, 0x2C00), (0x2C60, 0x2C80), (0xA720, 0xA800),
                (0xFB00, 0xFB50), (0xFE00, 0xFE70), (0xFF00, 0x10000)]


def trim_unifont(zbytes):
    import io, zipfile
    src = zipfile.ZipFile(io.BytesIO(zbytes))
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            data = src.read(info)
            if info.filename.endswith('.hex'):
                keep = [line for line in data.decode('ascii').splitlines()
                        if any(a <= int(line.split(':', 1)[0], 16) < b for a, b in UNIFONT_KEEP)]
                data = ('\n'.join(keep) + '\n').encode('ascii')
            dst.writestr(info.filename, data)
    return out.getvalue()



def radio_tint_container_png(data):
    """Recolor grayscale container/inventory panels into Radio's dark-crimson palette."""
    import io
    from PIL import Image
    image = Image.open(io.BytesIO(data)).convert('RGBA')
    pixels = image.load()
    ramp = [
        (0.00, (9, 6, 8)),
        (0.38, (18, 13, 16)),
        (0.68, (28, 16, 21)),
        (0.88, (81, 33, 44)),
        (0.97, (242, 217, 173)),
    ]
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]
            if a == 0:
                continue
            mx, mn = max(r, g, b), min(r, g, b)
            saturation = 0 if mx == 0 else (mx - mn) / mx
            # Preserve colorful icons and item artwork; recolor only neutral GUI pixels.
            if saturation > 0.22:
                continue
            value = mx / 255
            left = ramp[0][1]
            for i in range(1, len(ramp)):
                stop, right = ramp[i]
                if value <= stop:
                    low = ramp[i - 1][0]
                    t = (value - low) / max(0.001, stop - low)
                    color = tuple(round(left[j] + (right[j] - left[j]) * t) for j in range(3))
                    pixels[x, y] = color + (a,)
                    break
                left = right
            else:
                pixels[x, y] = ramp[-1][1] + (a,)
    out = io.BytesIO()
    image.save(out, format='PNG', optimize=True)
    return out.getvalue()

def patch_assets(epk_bytes):
    import json
    meta, files, _ = read_epk(epk_bytes)
    theme = theme_files()
    seen = set()
    out = []
    recipes, dropped = [], 0
    for t, n, d in files:
        if t == 'FILE' and n.startswith('data/minecraft/recipe/') and n.endswith('.json'):
            recipes.append('minecraft:' + n[len('data/minecraft/recipe/'):-5])
        if FAST_START and t == 'FILE' and n.startswith('data/minecraft/advancement/recipes/'):
            dropped += 1
            continue
        if t == 'FILE' and n in theme:
            d = theme[n]; seen.add(n)
        elif t == 'FILE' and n.startswith('assets/minecraft/textures/gui/container/') and n.endswith('.png'):
            d = radio_tint_container_png(d)
        if t == 'FILE' and n == 'assets/minecraft/font/unifont.zip':
            before = len(d); d = trim_unifont(d)
            print('unifont: %.1f MB -> %.2f MB' % (before / 1e6, len(d) / 1e6))
        if t == 'FILE' and n == 'assets/minecraft/lang/en_us.json':
            lang = json.loads(d)
            lang.update(LANG)
            d = json.dumps(lang, ensure_ascii=False, indent=1).encode('utf-8')
        out.append((t, n, d))
    # NOTE: no .mcfunction files — datapack functions crash world loading in this port
    # ("CompletableFuture observed before completion"), so Clear Lag lives in rise.js.
    if FAST_START:
        adv = {"criteria": {"tick": {"trigger": "minecraft:tick"}}, "rewards": {"recipes": sorted(recipes)}}
        out.append(('FILE', 'data/minecraft/advancement/rise_all_recipes.json', json.dumps(adv).encode()))
        print('fast start: dropped %d recipe advancements, 1 grants %d recipes' % (dropped, len(recipes)))
    for n, d in sorted(theme.items()):
        if n not in seen:
            out.append(('FILE', n, d))
    meta['count'] = len(out)  # the header count includes HEAD entries
    print('theme: %d replaced, %d added' % (len(seen), len(theme) - len(seen)))
    return write_epk(meta, out)


def data_uri_png(path):
    return 'data:image/png;base64,' + base64.b64encode(open(path, 'rb').read()).decode()


def data_uri_image(path):
    ext = os.path.splitext(path)[1].lower()
    mime = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png'}.get(ext)
    if mime is None:
        raise ValueError('Unsupported image type: ' + ext)
    return 'data:' + mime + ';base64,' + base64.b64encode(open(path, 'rb').read()).decode()


def main():
    html = open(BASE, 'r', encoding='utf-8').read()

    # 1. assets payload
    m = re.search(r'(<script type="application/octet-stream" id="eag-inline-assets" data-size=")(\d+)(">)(.*?)(</script>)', html, re.S)
    old_size = int(m.group(2))
    epk = base64.b64decode(re.sub(r'\s', '', m.group(4)))
    assert len(epk) == old_size
    new_epk = patch_assets(epk)
    html = html[:m.start()] + m.group(1) + str(len(new_epk)) + m.group(3) + b64_lines(new_epk) + m.group(5) + html[m.end():]
    n = html.count('var size = %d;' % old_size)
    assert n == 1, 'server bootstrap asset size marker not found (%d)' % n
    html = html.replace('var size = %d;' % old_size, 'var size = %d;' % len(new_epk))

    # 2. boot waits for Rise's pre-boot pass
    boot = '\t\t(async () => {\n\t\t\ttry {\n\t\t\t\twindow.__eagPrepareInlineAssets();'
    assert html.count(boot) == 1, 'boot script anchor not found'
    html = html.replace(boot, '\t\t(async () => {\n\t\t\ttry {\n\t\t\t\tawait (window.__risePreboot || null);\n\t\t\t\twindow.__eagPrepareInlineAssets();')

    # 3. inject rise.js (with its build-time data) right before the (deferred) module boot script
    import json
    ex = os.path.join(ROOT, 'theme_extra')
    rise = open(os.path.join(ROOT, 'src', 'rise.js'), encoding='utf-8').read()
    bp_path = os.path.join(ROOT, '..', 'BlueprintMod', 'blueprint.js')
    if os.path.isfile(bp_path):
        bp = open(bp_path, encoding='utf-8').read()
        a = 'btn.style.display = locked ? "none" : "";'
        assert a in bp, 'BlueprintMod lock-button anchor not found'
        bp = bp.replace(a, 'btn.style.display = "none";')  # opened from the Rise Mods menu instead
        a = '  function boot() {'
        assert a in bp, 'BlueprintMod boot anchor not found'
        bp = bp.replace(a, '  window.__blueprintMod.open = function () { panel.hidden = false; renderPanel(); };\n' + a)
    else:
        # BlueprintMod is an optional sibling dependency, not tracked in this repository.
        # Leave the rest of the client build usable and show a notice if its menu item is clicked.
        bp = ''
        print('BlueprintMod not found; blueprint feature will be unavailable in this build')
    rise = (rise.replace('%TITLE_ART%', base64.b64encode(open(os.path.join(ex, '8FAF8718-6A05-40EF-BDED-47FE7500021A.png'), 'rb').read()).decode())
                .replace('%GLYPHS%', open(os.path.join(ex, 'glyphs.json')).read())
                .replace('%FONT%', base64.b64encode(open(os.path.join(ex, 'rise-font.ttf'), 'rb').read()).decode())
                .replace('%PACKS%', open(os.path.join(ex, 'packs.json')).read())
                .replace('%PREVIEWS%', open(os.path.join(ex, 'previews.json')).read())
                .replace('%SKINS%', open(os.path.join(ex, 'skins.json')).read())
                .replace('%BLUEPRINT%', json.dumps(bp).replace('</', '<\\/')))
    assert '</script' not in rise.lower()
    anchor = '<script type="module">'
    assert html.count(anchor) == 1
    html = html.replace(anchor, '<script type="text/javascript">\n' + rise + '\n</script>\n\t' + anchor)

    # 4. Radio branding: title, favicon, and the RADIO wordmark on the black loading stage.
    html = html.replace('<title>Eaglercraft 26.2 0.6-dev</title>', '<title>Radio Client</title>', 1)
    icon = data_uri_png(os.path.join(ROOT, 'theme_extra', 'icon.png'))
    # Accept an icon link regardless of attribute order, quote style, or whether
    # the source icon is inline or a URL. Replace only the first favicon link.
    icon_link = r"<link\b(?=[^>]*\brel=['\"](?:shortcut\s+)?icon['\"])[^>]*>"
    html, icon_count = re.subn(icon_link,
                  lambda _: '<link rel="icon" type="image/png" href="' + icon + '">', html, count=1, flags=re.I)
    assert icon_count == 1, 'favicon link not found'
    stage = data_uri_png(os.path.join(ROOT, 'theme_extra', 'boot_logo.png'))
    style = ('#loading_screen.minecraft-stage{background:#000!important}'
             '#mojang_stage{background-image:url("' + stage + '")!important;'
             'background-repeat:no-repeat!important;background-position:center!important;'
             'background-size:contain!important}'
             '#mojang_stage .half{background-image:none!important}')
    html = html.replace('</head>', '<style>' + style + '</style>\n</head>', 1)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w', encoding='utf-8').write(html)
    print('wrote %s (%.1f MB)' % (OUT, os.path.getsize(OUT) / 1e6))
    import hashlib
    make_web(html, hashlib.sha1(html.encode('utf-8')).hexdigest()[:12])


# ---------------------------------------------------------------- web build
WEB = os.path.join(ROOT, 'dist', 'web', 'client')

WASM_FETCH = r'''  (function () {
    var pf = window.fetch;
    window.fetch = function (input, init) {
      var url = typeof input === "string" ? input : (input && input.url) || String(input);
      var clean = url.split("?")[0].split("#")[0].split("/").pop();
      var rw = window.__riseWasm && window.__riseWasm(clean, function () { return pf(input, init); });
      return rw || pf(input, init);
    };
  })();
'''
WORKER_ASSETS = ('\t\t\t\t\tif (window.__riseAssetBlobURL && typeof window.__eaglerWasmServerWorkerBootstrapURL === "string") {'
                 ' try { const rob = await (await fetch(window.__eaglerWasmServerWorkerBootstrapURL)).blob();'
                 ' window.__eaglerWasmServerWorkerBootstrapURL = URL.createObjectURL(new Blob(["self.__riseAssetURL=" + JSON.stringify(window.__riseAssetBlobURL) + ";\\n", rob], { type: "text/javascript" }));'
                 ' } catch (e) { window.__log.push("W:[Rise] worker asset blob: " + e); } }\n')


def make_web(html, version):
    """Split the payload <script> nodes into payload/<id>.bin files."""
    import hashlib, shutil, json
    if os.path.isdir(os.path.join(WEB, 'payload')):
        shutil.rmtree(os.path.join(WEB, 'payload'))
    os.makedirs(os.path.join(WEB, 'payload'))
    ids, total, sizes = [], 0, {}
    pat = re.compile(r'(<script type="application/octet-stream" id="([^"]+)" data-size="(\d+)">)(.*?)(</script>)', re.S)

    def repl(m):
        nonlocal total
        pid = m.group(2)
        if pid == 'eag-inline-decoder':   # tiny, needed synchronously at parse time
            return m.group(0)
        data = base64.b64decode(re.sub(r'\s', '', m.group(4)))
        assert len(data) == int(m.group(3)), pid
        open(os.path.join(WEB, 'payload', pid + '.bin'), 'wb').write(data)
        ids.append(pid); total += len(data); sizes[pid] = len(data)
        return m.group(1) + m.group(5)
    html = pat.sub(repl, html)

    # decoders: prefer the downloaded bytes
    a = '  function decodePayload(id) {\n'
    assert html.count(a) == 1
    html = html.replace(a, a + '    if (window.__riseBin && window.__riseBin[id]) { var rb = window.__riseBin[id]; delete window.__riseBin[id]; return rb; }\n')
    a = '  function decodePayloadAsync(id) {\n'
    assert html.count(a) == 1
    html = html.replace(a, a + '    if (window.__riseBin && window.__riseBin[id]) { var ra = window.__riseBin[id]; delete window.__riseBin[id]; return Promise.resolve(ra.buffer); }\n')
    # the three .wasm images come from Rise's cache, ready to compile (see web-loader.js)
    a = '  window.__eagReleaseInlineWasm = function () {'
    assert html.count(a) == 1
    html = html.replace(a, WASM_FETCH + a)
    # the world thread reads its assets from a blob in memory instead of the network
    a = '\t\t\t\t\twindow.__eaglerWasmRuntimeURL = null;\n'
    assert html.count(a) == 1
    html = html.replace(a, a + WORKER_ASSETS)
    # the server worker gets assets by (cached) sync XHR instead of an embedded base64 copy
    a = 'window.__eaglerWasmServerWorkerBootstrapURL = URL.createObjectURL(new Blob([\n'
    assert html.count(a) == 1
    html = html.replace(a, a + '    "self.__riseAssetURL=self.__riseAssetURL||" + JSON.stringify(new URL("payload/eag-inline-assets.bin?v=%s", location.href).href) + ";\\n",\n' % version)
    html = html.replace('serverAssetNode ? serverAssetNode.textContent : ""', '""', 1)
    a = 'if (assetBuffer) return assetBuffer;\\n'
    assert html.count(a) == 1
    html = html.replace(a, a + "    if (self.__riseAssetURL) { var rx = new OriginalXHR(); rx.open('GET', self.__riseAssetURL, false); rx.responseType = 'arraybuffer'; rx.send(); if (rx.status !== 200) throw new Error('Rise: asset download failed ' + rx.status); assetBuffer = rx.response; encoded = ''; return assetBuffer; }\\n")

    loader = open(os.path.join(ROOT, 'src', 'web-loader.js'), encoding='utf-8').read()
    loader = loader.replace('%VERSION%', version).replace('%IDS%', repr(ids).replace("'", '"')).replace('%TOTAL%', str(total)).replace('%SIZES%', json.dumps(sizes))
    head = '<head>'
    i = html.index(head) + len(head)
    html = html[:i] + '<script type="text/javascript">\n' + loader + '\n</script>' + html[i:]
    open(os.path.join(WEB, 'index.html'), 'w', encoding='utf-8').write(html)
    open(os.path.join(WEB, 'version.txt'), 'w').write(version)
    print('web build: index.html %.1f MB + %d payloads %.1f MB' % (
        os.path.getsize(os.path.join(WEB, 'index.html')) / 1e6, len(ids), total / 1e6))


if __name__ == '__main__':
    main()
