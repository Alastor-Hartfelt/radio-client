"""Generates the Radio Client theme: logo, buttons, widgets, vintage occult panorama,
loading-screen logo and menu backgrounds. Output: theme/<asset path>.

Run with the local venv:  .venv/bin/python gen_textures.py
"""
import colorsys, json, math, os, random
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'theme')
GUI = 'assets/minecraft/textures/gui/'

# Radio Client palette: near-black, crimson, and warm cream.
BG = (9, 6, 8)
CYAN = (243, 38, 62)       # Radio red accent
VIOLET = (164, 13, 41)     # deep crimson gradient stop
INK = (18, 13, 16)


def radioize(img):
    """Shift the old blue/cyan Rise artwork into Radio's crimson palette."""
    rgba = img.convert('RGBA')
    px = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            # Recolor cyan/blue pixels only; preserve neutral grays, black, and whites.
            if s > 0.16 and 0.42 <= h <= 0.75:
                rr, gg, bb = colorsys.hsv_to_rgb(0.985, max(0.35, s), v)
                px[x, y] = (int(rr * 255), int(gg * 255), int(bb * 255), a)
    return rgba


def save(img, path):
    img = radioize(img)
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    img.save(full, optimize=True)


def save_text(text, path):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(text)


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


def grad_h(w, h, c0, c1, alpha=255):
    im = Image.new('RGBA', (w, h))
    px = im.load()
    for x in range(w):
        c = lerp(c0, c1, x / max(1, w - 1))
        for y in range(h):
            px[x, y] = c + (alpha,)
    return im


# ---------------------------------------------------------------- pixel font
FONT = {
    'R': ["1111.", "1...1", "1...1", "1111.", "1.1..", "1..1.", "1...1"],
    'I': ["11111", "..1..", "..1..", "..1..", "..1..", "..1..", "11111"],
    'S': [".1111", "1....", "1....", ".111.", "....1", "....1", "1111."],
    'E': ["11111", "1....", "1....", "1111.", "1....", "1....", "11111"],
    'A': ["..1..", ".1.1.", "1...1", "11111", "1...1", "1...1", "1...1"],
    'D': ["1111.", "1...1", "1...1", "1...1", "1...1", "1...1", "1111."],
    'O': [".111.", "1...1", "1...1", "1...1", "1...1", "1...1", ".111."],
    'C': [".1111", "1....", "1....", "1....", "1....", "1....", ".1111"],
    'L': ["1....", "1....", "1....", "1....", "1....", "1....", "11111"],
    'N': ["1...1", "11..1", "1.1.1", "1..11", "1...1", "1...1", "1...1"],
    'T': ["11111", "..1..", "..1..", "..1..", "..1..", "..1..", "..1.."],
    ' ': [".....", ".....", ".....", ".....", ".....", ".....", "....."],
}


def glyph_mask(text, cell, gap_cells=1):
    """Returns an L-mode mask of the text drawn in the block font."""
    cols = sum(5 + gap_cells for _ in text) - gap_cells
    w, h = cols * cell, 7 * cell
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    x0 = 0
    for ch in text:
        g = FONT[ch]
        for r, row in enumerate(g):
            for c, v in enumerate(row):
                if v == '1':
                    d.rectangle([x0 + c * cell, r * cell, x0 + (c + 1) * cell - 1, (r + 1) * cell - 1], fill=255)
        x0 += (5 + gap_cells) * cell
    return m


def wordmark(text, cell, depth, outline, gap_cells=1):
    """Chunky 3D wordmark: gradient face, dark extrusion, black outline."""
    m = glyph_mask(text, cell, gap_cells)
    w, h = m.size
    pad = outline + depth + 2
    W, H = w + pad * 2, h + pad * 2
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    # outline + extrusion silhouette
    sil = Image.new('L', (W, H), 0)
    for k in range(depth + 1):
        sil.paste(255, (pad + k, pad + k), m)
    sil = sil.filter(ImageFilter.MaxFilter(outline * 2 + 1))
    img.paste((2, 12, 24, 255), (0, 0), sil)
    # extrusion (dark violet steps)
    for k in range(depth, 0, -1):
        c = lerp((6, 70, 110), (3, 34, 64), k / depth)
        img.paste(c + (255,), (pad + k, pad + k), m)
    # face: vertical cyan -> violet gradient with a highlight band
    face = Image.new('RGBA', (w, h))
    fp = face.load()
    for y in range(h):
        t = y / (h - 1)
        c = lerp(CYAN, VIOLET, t)
        if t < 0.12:
            c = lerp((215, 255, 250), c, t / 0.12)
        for x in range(w):
            fp[x, y] = c + (255,)
    img.paste(face, (pad, pad), m)
    # pixel bevel: lighter top-left edge of every cell block
    inner = m.filter(ImageFilter.MinFilter(3))
    edge = Image.eval(Image.composite(Image.new('L', m.size, 0), m, inner), lambda v: v)
    hl = Image.new('RGBA', (w, h), (255, 255, 255, 70))
    img.paste(hl, (pad, pad), edge)
    return img



def radio_wordmark(text, cell, depth, outline, gap_cells=1):
    """Radio Client wordmark with the O rendered as a tiny analog tuning dial."""
    art = wordmark(text, cell=cell, depth=depth, outline=outline, gap_cells=gap_cells)
    if 'O' not in text:
        return art
    from PIL import ImageDraw
    pad = outline + depth + 2
    ox = pad + text.index('O') * (5 + gap_cells) * cell
    oy = pad
    cx, cy = ox + 2.5 * cell, oy + 3.5 * cell
    d = ImageDraw.Draw(art)
    # A warm ivory dial face, red center, and a tuning needle make the O distinct
    # while keeping the chunky pixel lettering legible at Minecraft's logo scale.
    inset = max(2, cell // 2)
    box = (int(ox + inset), int(oy + inset), int(ox + 5 * cell - inset), int(oy + 7 * cell - inset))
    d.ellipse(box, fill=(18, 13, 16, 255), outline=(242, 217, 173, 255), width=max(2, cell // 5))
    for angle in (-145, -115, -85, -55, -25):
        import math
        rad = math.radians(angle)
        r1, r2 = cell * 1.15, cell * 1.45
        x1, y1 = cx + math.cos(rad) * r1, cy + math.sin(rad) * r1
        x2, y2 = cx + math.cos(rad) * r2, cy + math.sin(rad) * r2
        d.line((x1, y1, x2, y2), fill=(242, 217, 173, 255), width=max(1, cell // 7))
    d.line((cx, cy, cx + cell * 0.9, cy - cell * 1.15), fill=(243, 38, 62, 255), width=max(2, cell // 4))
    r = max(2, cell // 4)
    d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(242, 217, 173, 255))
    return art


def fit_into(canvas_size, art, area, align='center'):
    cw, ch = canvas_size
    ax, ay, aw, ah = area
    s = min(aw / art.width, ah / art.height)
    art = art.resize((max(1, int(art.width * s)), max(1, int(art.height * s))), Image.NEAREST)
    im = Image.new('RGBA', canvas_size, (0, 0, 0, 0))
    x = ax + (aw - art.width) // 2
    y = ay + (ah - art.height) // 2
    im.alpha_composite(art, (x, y))
    return im


# ---------------------------------------------------------------- logos
def make_logo():
    # Title logo: 1024x256 texture, the game shows the top 176 rows (44/64).
    art = radio_wordmark('RADIO', cell=18, depth=8, outline=5)
    save(fit_into((1024, 256), art, (262, 2, 500, 172)), GUI + 'title/minecraft.png')
    save(fit_into((1024, 256), art, (262, 2, 500, 172)), GUI + 'title/minceraft.png')
    # Edition strip: 512x64 texture, shown region is 392x56 from the left.
    ed = wordmark('CLIENT', cell=8, depth=3, outline=3, gap_cells=1)
    save(fit_into((512, 64), ed, (40, 2, 312, 54)), GUI + 'title/edition.png')


def make_loading_logo():
    # The game expects a white logo split across two halves of mojangstudios.png.
    # Keep the radio dial's center transparent and draw its tuning marks in white.
    art = radio_wordmark('RADIO CLIENT', cell=9, depth=3, outline=2)
    alpha = art.getchannel('A')
    white = Image.new('RGBA', art.size, (255, 255, 255, 0))
    white.putalpha(alpha)
    from PIL import ImageDraw
    d = ImageDraw.Draw(white)
    cell, gap_cells, outline, depth = 9, 1, 2, 3
    pad = outline + depth + 2
    ox = pad + 'RADIO CLIENT'.index('O') * (5 + gap_cells) * cell
    oy = pad
    cx, cy = ox + 2.5 * cell, oy + 3.5 * cell
    inset = max(2, cell // 2)
    box = (int(ox + inset), int(oy + inset), int(ox + 5 * cell - inset), int(oy + 7 * cell - inset))
    d.ellipse(box, fill=(255, 255, 255, 0), outline=(255, 255, 255, 255), width=2)
    d.line((cx, cy, cx + cell * 0.9, cy - cell * 1.15), fill=(255, 255, 255, 255), width=2)
    r = 2
    d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(255, 255, 255, 255))
    strip = fit_into((1024, 256), white, (40, 60, 944, 136))
    tex = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
    tex.paste(strip.crop((0, 0, 512, 256)), (0, 0))
    tex.paste(strip.crop((512, 0, 1024, 256)), (0, 256))
    save(tex, GUI + 'title/mojangstudios.png')


# ---------------------------------------------------------------- widgets
def rounded_box(w, h, fill, border, r=2, border2=None):
    """Pixel-rounded box with a 1px border (and optional inner glow line)."""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    px = im.load()
    for y in range(h):
        for x in range(w):
            # cut corners (radius r in pixels)
            dx = min(x, w - 1 - x)
            dy = min(y, h - 1 - y)
            if dx + dy < r:
                continue
            on_edge = dx == 0 or dy == 0 or dx + dy == r
            if on_edge:
                px[x, y] = border
            elif border2 and (dx == 1 or dy == 1 or dx + dy == r + 1):
                px[x, y] = border2
            else:
                px[x, y] = fill
    return im


def button_face(w, h, top, bottom, border, glow=None, r=2):
    im = rounded_box(w, h, (0, 0, 0, 0), border, r, glow)
    px = im.load()
    for y in range(h):
        c = lerp(top, bottom, y / max(1, h - 1))
        for x in range(w):
            if px[x, y] == (0, 0, 0, 0):
                dx = min(x, w - 1 - x)
                dy = min(y, h - 1 - y)
                if dx + dy >= r:
                    px[x, y] = c
    return im


def accent_underline(im, alpha=255):
    """Crimson gradient line along the bottom inner edge (Radio hover accent)."""
    w, h = im.size
    line = grad_h(w - 6, 1, CYAN, VIOLET, alpha)
    im.alpha_composite(line, (3, h - 2))
    return im


def nine(path, w, h, border):
    save_text(json.dumps({"gui": {"scaling": {"type": "nine_slice", "width": w, "height": h,
                                             "border": border}}}, indent=4), path + '.mcmeta')


def shine_frames(base, n=14):
    """Frames of a soft white highlight sweeping left->right across a button."""
    w, h = base.size
    frames = []
    for i in range(n):
        f = base.copy()
        cx = -30 + (w + 60) * i / (n - 1)
        glow = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        gp = glow.load()
        bp = base.load()
        for x in range(w):
            # diagonal band, 26px wide, soft falloff
            for y in range(h):
                d = abs((x - cx) - (y - h / 2) * 0.6)
                a = max(0.0, 1 - d / 13)
                if a > 0 and bp[x, y][3] > 0:
                    gp[x, y] = (210, 255, 250, int(90 * a * a))
        f.alpha_composite(glow)
        frames.append(f)
    return frames


def animated(path, frames, w, h, border, timeline):
    """Save a vertical frame strip + mcmeta with animation and nine-slice scaling."""
    strip = Image.new('RGBA', (w, h * len(frames)), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        strip.alpha_composite(f, (0, i * h))
    save(strip, path)
    save_text(json.dumps({
        "animation": {"frametime": 1, "interpolate": False, "width": w, "height": h, "frames": timeline},
        "gui": {"scaling": {"type": "nine_slice", "width": w, "height": h, "border": border}},
    }, indent=4), path + '.mcmeta')


# Radio palette for widgets: dark oxblood surfaces, crimson hover, warm-cream edge.
OCEAN_TOP = (95, 14, 30)
OCEAN_BOT = (28, 8, 13)
EDGE = (120, 39, 53, 255)
HOVER_TOP = (243, 38, 62)
HOVER_BOT = (130, 12, 35)
HOVER_EDGE = (242, 217, 173, 255)


def make_widgets():
    W = GUI + 'sprites/widget/'
    # buttons (200x20): dark oxblood face, muted crimson rim
    b = button_face(200, 20, OCEAN_TOP + (235,), OCEAN_BOT + (235,), EDGE, (255, 255, 255, 30))
    save(b, W + 'button.png'); nine(W + 'button.png', 200, 20, 4)
    # hover: brighter crimson with a warm highlight sweep (plays while hovered)
    bh = button_face(200, 20, HOVER_TOP + (245,), HOVER_BOT + (245,), HOVER_EDGE, (255, 255, 255, 60))
    bh.alpha_composite(grad_h(194, 1, (255, 224, 205), (242, 217, 173), 120), (3, 2))
    fr = shine_frames(bh)
    timeline = [{"index": 0, "time": 6}] + list(range(1, len(fr))) + [{"index": 0, "time": 24}]
    animated(W + 'button_highlighted.png', fr, 200, 20, 4, timeline)
    bd = button_face(200, 20, (24, 9, 14, 180), (14, 7, 10, 180), (65, 24, 34, 255))
    save(bd, W + 'button_disabled.png'); nine(W + 'button_disabled.png', 200, 20, 4)
    # sliders
    s = button_face(200, 20, (16, 8, 12, 225), (29, 10, 16, 225), (105, 31, 46, 255))
    save(s, W + 'slider.png'); nine(W + 'slider.png', 200, 20, 4)
    sh = button_face(200, 20, (35, 10, 17, 235), (55, 12, 24, 235), HOVER_EDGE)
    save(sh, W + 'slider_highlighted.png'); nine(W + 'slider_highlighted.png', 200, 20, 4)
    hb = {"left": 2, "top": 2, "right": 2, "bottom": 3}
    handle = button_face(8, 20, (243, 38, 62, 255), (130, 12, 35, 255), (242, 217, 173, 255), r=1)
    save(handle, W + 'slider_handle.png'); nine(W + 'slider_handle.png', 8, 20, hb)
    handle_h = button_face(8, 20, (255, 137, 149, 255), (243, 38, 62, 255), (255, 255, 255, 255), r=1)
    save(handle_h, W + 'slider_handle_highlighted.png'); nine(W + 'slider_handle_highlighted.png', 8, 20, hb)
    # text fields
    tf = button_face(200, 20, (12, 7, 10, 240), (12, 7, 10, 240), (105, 31, 46, 255), r=2)
    save(tf, W + 'text_field.png'); nine(W + 'text_field.png', 200, 20, 3)
    tfh = button_face(200, 20, (20, 8, 13, 245), (20, 8, 13, 245), HOVER_EDGE, r=2)
    save(tfh, W + 'text_field_highlighted.png'); nine(W + 'text_field_highlighted.png', 200, 20, 3)
    # tabs (130x24, bottom border 0)
    tb = {"left": 3, "top": 3, "right": 3, "bottom": 0}
    def tab(top, bottom, border, underline):
        im = button_face(130, 28, top, bottom, border).crop((0, 0, 130, 24))
        if underline:
            im.alpha_composite(grad_h(124, 2, CYAN, VIOLET), (3, 22))
        return im
    save(tab((38, 11, 19, 210), (24, 8, 13, 210), (105, 31, 46, 255), False), W + 'tab.png'); nine(W + 'tab.png', 130, 24, tb)
    save(tab((85, 17, 32, 235), (42, 10, 18, 235), (90, 220, 230, 255), False), W + 'tab_highlighted.png'); nine(W + 'tab_highlighted.png', 130, 24, tb)
    save(tab((125, 22, 39, 245), (65, 13, 25, 245), HOVER_EDGE, True), W + 'tab_selected.png'); nine(W + 'tab_selected.png', 130, 24, tb)
    save(tab((165, 29, 46, 250), (95, 14, 30, 250), (230, 255, 252, 255), True), W + 'tab_selected_highlighted.png'); nine(W + 'tab_selected_highlighted.png', 130, 24, tb)
    # checkboxes (20x20)
    def check(selected, hover):
        border = HOVER_EDGE if hover else EDGE
        im = button_face(20, 20, (24, 8, 13, 240), (15, 7, 10, 240), border, r=2)
        if selected:
            inner = button_face(12, 12, CYAN + (255,), VIOLET + (255,), (220, 255, 250, 255), r=1)
            im.alpha_composite(inner, (4, 4))
        return im
    save(check(False, False), W + 'checkbox.png')
    save(check(False, True), W + 'checkbox_highlighted.png')
    save(check(True, False), W + 'checkbox_selected.png')
    save(check(True, True), W + 'checkbox_selected_highlighted.png')
    # scroller (6x32)
    save(button_face(6, 32, CYAN + (255,), VIOLET + (255,), (210, 255, 250, 255), r=1), W + 'scroller.png')
    nine(W + 'scroller.png', 6, 32, 1)
    save(button_face(6, 32, (14, 7, 10, 210), (14, 7, 10, 210), (55, 18, 27, 255), r=1), W + 'scroller_background.png')
    nine(W + 'scroller_background.png', 6, 32, 1)


def make_backgrounds():
    # Menu backgrounds are tiled over the blurred crimson panorama.
    save(Image.new('RGBA', (16, 16), (14, 7, 10, 140)), GUI + 'menu_background.png')
    save(Image.new('RGBA', (16, 16), (14, 7, 10, 110)), GUI + 'inworld_menu_background.png')
    save(Image.new('RGBA', (16, 16), (20, 7, 12, 170)), GUI + 'menu_list_background.png')
    save(Image.new('RGBA', (16, 16), (20, 7, 12, 130)), GUI + 'inworld_menu_list_background.png')
    for name in ('header_separator', 'footer_separator', 'inworld_header_separator', 'inworld_footer_separator'):
        im = Image.new('RGBA', (32, 2), (0, 0, 0, 0))
        im.alpha_composite(grad_h(32, 1, CYAN, VIOLET, 210), (0, 0 if 'header' in name else 1))
        im.alpha_composite(Image.new('RGBA', (32, 1), (0, 0, 0, 150)), (0, 1 if 'header' in name else 0))
        save(im, GUI + name + '.png')


def make_panorama():
    """Generate an original vintage-radio occult panorama for the Radio title screen.

    The four side faces are crops from one continuous crimson city scene, so the
    art feels like a single environment rather than the old Rise Client backdrop.
    The logo and clickable Minecraft menu buttons remain separate game UI assets.
    """
    S = 256
    W, H = S * 4, S
    DEEP = (5, 4, 7)
    INK = (10, 5, 9)
    CRIMSON = (220, 13, 42)
    RED = (145, 8, 29)
    CREAM = (242, 217, 173)

    scene = Image.new('RGB', (W, H), DEEP)
    px = scene.load()
    # Smoky broadcast-hour sky. A gentle periodic horizontal glow avoids a
    # conspicuous brightness jump where the four side faces meet.
    for y in range(H):
        t = y / (H - 1)
        if t < 0.58:
            base = lerp((10, 5, 10), (48, 8, 22), t / 0.58)
        else:
            base = lerp((48, 8, 22), (7, 4, 8), (t - 0.58) / 0.42)
        for x in range(W):
            glow = (math.sin((x / W) * math.pi * 2 - 0.8) + 1) * 0.5
            haze = max(0, 1 - abs(y - 110) / 95) * glow
            px[x, y] = (
                min(255, int(base[0] + 33 * haze)),
                min(255, int(base[1] + 3 * haze)),
                min(255, int(base[2] + 8 * haze)),
            )

    # A red broadcast moon and diffuse halo, kept to the right of the central UI.
    halo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hd.ellipse((690, 7, 916, 233), fill=(205, 8, 39, 28))
    hd.ellipse((724, 25, 884, 185), fill=(239, 13, 48, 38))
    halo = halo.filter(ImageFilter.GaussianBlur(24))
    scene = Image.alpha_composite(scene.convert('RGBA'), halo)
    d = ImageDraw.Draw(scene)
    d.ellipse((755, 38, 855, 138), fill=(125, 5, 26, 220), outline=(230, 21, 52, 210), width=2)
    d.ellipse((767, 50, 843, 126), outline=(220, 13, 42, 170), width=2)
    # A minimal radio-wave sigil inside the moon.
    d.arc((780, 63, 830, 113), 205, 335, fill=(242, 217, 173, 180), width=2)
    d.arc((790, 73, 820, 103), 205, 335, fill=(242, 217, 173, 180), width=2)
    d.ellipse((802, 85, 808, 91), fill=CREAM + (210,))

    # Gothic industrial skyline, with warm red windows and thin antenna spires.
    rnd = random.Random(2602)
    x = 0
    while x < W:
        bw = rnd.randint(24, 68)
        top = rnd.randint(133, 190)
        d.rectangle((x, top, x + bw, H), fill=(8, 4, 8, 255), outline=(55, 7, 19, 255), width=1)
        if rnd.random() < 0.46:
            cx = x + bw // 2
            d.polygon([(cx - 5, top), (cx, top - rnd.randint(8, 24)), (cx + 5, top)], fill=(12, 4, 9, 255))
            d.line((cx, top - 23, cx, top - 34), fill=(173, 8, 34, 220), width=1)
            d.ellipse((cx - 2, top - 37, cx + 2, top - 33), fill=(243, 38, 62, 230))
        for wy in range(top + 8, H - 8, 13):
            for wx in range(x + 5, x + bw - 4, 10):
                if rnd.random() < 0.33:
                    d.rectangle((wx, wy, wx + 3, wy + 5), fill=(160, 11, 35, rnd.randint(110, 220)))
        x += bw + rnd.randint(3, 9)

    # Tall radio mast beneath the moon, with a little "ON AIR" sign.
    d.line((803, 136, 803, 217), fill=(5, 4, 7, 255), width=5)
    d.line((803, 137, 775, 216), fill=(5, 4, 7, 255), width=3)
    d.line((803, 137, 831, 216), fill=(5, 4, 7, 255), width=3)
    d.line((784, 183, 822, 183), fill=(5, 4, 7, 255), width=3)
    d.line((789, 168, 817, 168), fill=(5, 4, 7, 255), width=2)
    d.ellipse((797, 129, 809, 141), fill=(8, 4, 8, 255), outline=CRIMSON + (255,), width=2)
    d.ellipse((801, 133, 805, 137), fill=CRIMSON + (255,))
    d.polygon([(837, 180), (893, 166), (893, 187), (837, 201)], fill=(14, 5, 10, 255), outline=CRIMSON + (255,))
    d.text((845, 177), "ON AIR", fill=(243, 38, 62, 255))

    # Draw tentacles as ink-black, red-rimmed curves. No character silhouette:
    # only the magical, eye-studded tendrils framing the menu like living cables.
    def bezier(p0, p1, p2, p3, steps=90):
        pts = []
        for i in range(steps + 1):
            t = i / steps
            u = 1 - t
            pts.append((
                round(u*u*u*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t*t*t*p3[0]),
                round(u*u*u*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t*t*t*p3[1]),
            ))
        return pts

    paths = [
        ((-35, 75), (80, -35), (165, 158), (282, 28), 23),
        ((165, -28), (280, 88), (310, 188), (425, 110), 17),
        ((475, -35), (525, 88), (680, -10), (735, 62), 21),
        ((895, -30), (790, 55), (945, 112), (1060, 42), 24),
        ((-40, 206), (95, 135), (130, 286), (280, 222), 26),
        ((255, 276), (390, 184), (450, 280), (575, 222), 18),
        ((585, 275), (700, 173), (785, 283), (885, 218), 24),
        ((860, 244), (940, 176), (990, 218), (1065, 150), 20),
    ]
    for p0, p1, p2, p3, width in paths:
        pts = bezier(p0, p1, p2, p3)
        d.line(pts, fill=(113, 5, 26, 255), width=width + 5, joint='curve')
        d.line(pts, fill=(5, 4, 7, 255), width=width, joint='curve')
        # Tiny crimson edge glints give the ink forms an old screen-print finish.
        d.line(pts[::4], fill=(174, 7, 32, 180), width=2, joint='curve')

    # Distinct eye motifs embedded in the tentacles.
    eyes = [
        (84, 73, 22, 9), (228, 42, 18, 7), (525, 38, 20, 8),
        (681, 221, 23, 9), (933, 82, 22, 9), (146, 221, 18, 7),
        (406, 235, 18, 7), (980, 194, 20, 8),
    ]
    for cx, cy, ew, eh in eyes:
        d.ellipse((cx-ew, cy-eh, cx+ew, cy+eh), fill=(4, 3, 6, 255), outline=CRIMSON + (255,), width=2)
        d.ellipse((cx-ew*0.36, cy-eh*0.72, cx+ew*0.36, cy+eh*0.72), fill=(230, 15, 45, 255))
        d.ellipse((cx-2, cy-eh*0.45, cx+2, cy+eh*0.45), fill=(4, 3, 6, 255))

    # Antique tabletop radio in the far-left scene, deliberately away from the
    # logo/button column. Its tuning dial echoes the O in the Radio wordmark.
    d.rounded_rectangle((38, 151, 246, 243), radius=8, fill=(7, 4, 7, 255), outline=(170, 10, 34, 255), width=3)
    d.rectangle((48, 163, 142, 231), fill=(14, 7, 11, 255), outline=(75, 12, 27, 255), width=2)
    for yy in range(170, 225, 7):
        d.line((54, yy, 135, yy), fill=(90, 9, 26, 210), width=1)
    d.ellipse((155, 166, 231, 239), fill=(9, 5, 9, 255), outline=(211, 17, 45, 255), width=3)
    d.ellipse((164, 175, 222, 233), outline=CREAM + (220,), width=2)
    d.ellipse((176, 187, 210, 221), outline=(150, 10, 34, 255), width=2)
    d.line((193, 204, 207, 187), fill=CREAM + (255,), width=2)
    d.ellipse((189, 200, 197, 208), fill=CRIMSON + (255,))
    d.line((61, 153, 61, 138), fill=(6, 4, 7, 255), width=3)
    d.line((61, 138, 82, 130), fill=CRIMSON + (255,), width=2)
    # Tiny credit etched along the lower edge, as requested.
    d.text((30, 239), "written by o_xer", fill=(243, 38, 62, 255))

    # Light scanlines and restrained print grain create a vintage broadcast feel.
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for yy in range(0, H, 4):
        od.line((0, yy, W, yy), fill=(0, 0, 0, 35), width=1)
    for _ in range(1800):
        gx, gy = rnd.randrange(W), rnd.randrange(H)
        v = rnd.choice((30, 50, 70, 95))
        od.point((gx, gy), fill=(255, 30, 55, v))
    scene = Image.alpha_composite(scene, overlay)
    scene = scene.convert('RGB').filter(ImageFilter.GaussianBlur(0.25))

    # Four connected side faces from one scene, plus a matching crimson sky/abyss.
    for face in range(4):
        im = scene.crop((face * S, 0, (face + 1) * S, S))
        save(im, GUI + 'title/background/panorama_%d.png' % face)

    # Up face: an antique broadcast halo seen through smoky crimson clouds.
    up = Image.new('RGBA', (S, S), (10, 5, 10, 255))
    up_px = up.load()
    for y in range(S):
        for x in range(S):
            dx, dy = (x - 128) / 128, (y - 128) / 128
            t = min(1, math.sqrt(dx * dx + dy * dy))
            up_px[x, y] = lerp((105, 7, 27), (5, 4, 7), t) + (255,)
    ud = ImageDraw.Draw(up)
    ud.ellipse((54, 54, 202, 202), outline=(198, 12, 41, 180), width=3)
    ud.ellipse((76, 76, 180, 180), outline=(242, 217, 173, 95), width=1)
    for a in range(0, 360, 15):
        rad = math.radians(a)
        x1, y1 = 128 + math.cos(rad)*68, 128 + math.sin(rad)*68
        x2, y2 = 128 + math.cos(rad)*76, 128 + math.sin(rad)*76
        ud.line((x1, y1, x2, y2), fill=(243, 38, 62, 170), width=2)
    save(up, GUI + 'title/background/panorama_4.png')

    # Down face: near-black broadcast static, with faint red signal rings.
    down = Image.new('RGBA', (S, S), (5, 4, 7, 255))
    dd = ImageDraw.Draw(down)
    for radius, alpha in ((40, 45), (72, 35), (104, 25)):
        dd.ellipse((128-radius, 128-radius, 128+radius, 128+radius),
                   outline=(170, 7, 33, alpha), width=2)
    for _ in range(180):
        xx, yy = rnd.randrange(S), rnd.randrange(S)
        dd.point((xx, yy), fill=(150, 8, 34, rnd.randint(20, 75)))
    save(down, GUI + 'title/background/panorama_5.png')
    save(Image.new('RGBA', (1, 1), (0, 0, 0, 0)), GUI + 'title/background/panorama_overlay.png')

SPLASHES = """Now with observers!
Railguns approved!
Flying machines fly!
Stasis chambers work!
Crimson-style settings!
Right Shift for Radio!
Runs on a Chromebook!
LAN worlds for the class!
Quasi-connectivity intact!
Bubble columns bubble!
Zero-tick ready!
Tune in and grind!
26.2 in a browser!
Built for 4GB of RAM!
Also try redstone!
Slime blocks stick!
Observers observe!
Piston timing: Java!
Now 100% more Radio!
Chunk loading, but faster!
"""


def main():
    make_logo()
    make_loading_logo()
    make_widgets()
    make_backgrounds()
    make_panorama()
    save_text(SPLASHES, 'assets/minecraft/texts/splashes.txt')
    n = sum(len(f) for _, _, f in os.walk(OUT))
    print('theme files:', n)


if __name__ == '__main__':
    main()


def make_extras():
    """Generate the loading-stage Radio Client lockup and matching favicon."""
    ex = os.path.join(ROOT, 'theme_extra')
    os.makedirs(ex, exist_ok=True)

    # Keep the analog-dial wordmark, but give the loading screen the little
    # vintage broadcast-tower emblem that now anchors Radio Client's identity.
    radio = radio_wordmark('RADIO', cell=10, depth=4, outline=3)
    client = wordmark('CLIENT', cell=7, depth=3, outline=3)
    word_w = max(radio.width, client.width)
    word_h = radio.height + client.height - 7
    word = Image.new('RGBA', (word_w, word_h), (0, 0, 0, 0))
    word.alpha_composite(radio, ((word_w - radio.width) // 2, 0))
    word.alpha_composite(client, ((word_w - client.width) // 2, radio.height - 7))

    # Transparent emblem canvas. The red broadcast arcs and warm-cream mast
    # echo the Lucide-style radio tower mark, redrawn to fit the pixel logo.
    emblem = Image.new('RGBA', (156, 174), (0, 0, 0, 0))
    glow = Image.new('RGBA', emblem.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.arc((16, 4, 140, 128), 205, 335, fill=(243, 38, 62, 150), width=8)
    gd.arc((31, 18, 125, 112), 205, 335, fill=(243, 38, 62, 170), width=7)
    gd.arc((48, 33, 108, 93), 205, 335, fill=(242, 217, 173, 170), width=5)
    glow = glow.filter(ImageFilter.GaussianBlur(5))
    emblem.alpha_composite(glow)
    ed = ImageDraw.Draw(emblem)
    crimson = (243, 38, 62, 255)
    deep = (76, 6, 23, 255)
    cream = (242, 217, 173, 255)
    # Signal arcs, with a dark under-stroke for a printed, vintage look.
    for box, width in [((16, 4, 140, 128), 5), ((31, 18, 125, 112), 5), ((48, 33, 108, 93), 4)]:
        ed.arc(box, 205, 335, fill=deep, width=width + 3)
        ed.arc(box, 205, 335, fill=crimson if width != 4 else cream, width=width)
    # Tall mast and crossed feet, with black/crimson shadow then ivory highlight.
    ed.line((78, 67, 47, 157), fill=deep, width=13)
    ed.line((78, 67, 109, 157), fill=deep, width=13)
    ed.line((47, 157, 109, 157), fill=deep, width=13)
    ed.line((78, 67, 47, 157), fill=cream, width=5)
    ed.line((78, 67, 109, 157), fill=cream, width=5)
    ed.line((47, 157, 109, 157), fill=crimson, width=5)
    ed.line((60, 119, 96, 119), fill=deep, width=10)
    ed.line((60, 119, 96, 119), fill=crimson, width=4)
    ed.ellipse((68, 56, 88, 76), fill=deep, outline=crimson, width=3)
    ed.ellipse((73, 61, 83, 71), fill=cream)
    # Tiny base plate gives the mark a deliberate, old radio-station insignia feel.
    ed.rounded_rectangle((36, 159, 120, 170), radius=3, fill=deep, outline=crimson, width=2)
    ed.line((45, 164, 111, 164), fill=cream, width=1)

    gap = 28
    total_w = emblem.width + gap + word.width
    total_h = max(emblem.height, word.height)
    lockup = Image.new('RGBA', (total_w, total_h), (0, 0, 0, 0))
    lockup.alpha_composite(emblem, (0, (total_h - emblem.height) // 2))
    lockup.alpha_composite(word, (emblem.width + gap, (total_h - word.height) // 2))
    fit_into((1024, 256), lockup, (55, 12, 914, 232)).save(
        os.path.join(ex, 'boot_logo.png'), optimize=True)

    # Keep the small favicon aligned with the same radio identity.
    r = radio_wordmark('R', cell=8, depth=3, outline=3)
    fit_into((64, 64), r, (2, 2, 60, 60)).save(os.path.join(ex, 'icon.png'), optimize=True)

make_extras()
