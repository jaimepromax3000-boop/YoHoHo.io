"""Genera los disfraces (PNG) del proyecto Scratch a partir de los gráficos del juego original."""
import io, json, os, math, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "img")
KB = 120      # px por unidad de mundo para cuerpos y armas
KD = 100      # px por unidad de mundo para decorado

_frames = {}
for suf in ["", "2", "3", "4"]:
    j = json.load(open(f"{IMG}/spritesheet4-{suf}.json"))
    im = Image.open(f"{IMG}/spritesheet4-{suf}.png").convert("RGBA")
    for k, v in j["frames"].items():
        f = v["frame"]
        _frames[k] = im.crop((f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"]))


def frame(name): return _frames[name].copy()


def png(im):
    b = io.BytesIO(); im.save(b, "PNG", optimize=True); return b.getvalue()


def fit_units(name, width_units, K):
    im = frame(name)
    w = max(1, round(width_units * K)); h = max(1, round(im.height * w / im.width))
    return im.resize((w, h), Image.LANCZOS)


# anchors del arma (fracción de ancho, fracción de alto) tomados de yohoho.js (kt)
ANCHOR = {i: (59 / 115, 49 / 427) for i in range(1, 36)}
ANCHOR.update({10: (59 / 115, 58 / 427), 11: (59 / 115, 67 / 477), 12: (59 / 115, 87 / 449), 13: (59 / 115, 123 / 447),
               16: (59 / 115, 123 / 539), 17: (59 / 115, 137 / 554), 18: (59 / 115, 155 / 600), 20: (59 / 115, 84 / 485),
               21: (59 / 115, 213 / 589), 22: (59 / 115, 69 / 423), 23: (59 / 115, 215 / 581), 24: (59 / 115, 131 / 455),
               25: (59 / 115, 112 / 481), 26: (108 / 204, 160 / 492), 27: (59 / 115, 142 / 527), 28: (59 / 115, 100 / 497),
               29: (59 / 115, 59 / 415), 30: (59 / 115, 139 / 462), 31: (59 / 115, 199 / 713), 32: (59 / 115, 83 / 449),
               33: (59 / 115, 141 / 544), 34: (59 / 115, 160 / 487), 35: (59 / 115, 152 / 600)})
# polígono de golpe (fracciones x,y) -> caja
POLY = {i: [0.3, 0.3, 0.3, 0.95, 0.7, 0.95, 0.7, 0.3] for i in range(1, 36)}
POLY[7] = [0.15, 0.3, 0.35, 0.95, 0.95, 0.95, 0.7, 0.3]
POLY[14] = [0.25, 0.3, 0.4, 0.95, 0.95, 0.95, 0.7, 0.3]
POLY[15] = [0.3, 0.3, 0.4, 0.98, 0.9, 0.98, 0.7, 0.3]
for i in range(16, 36): POLY[i] = [0.3, 0.3, 0.3, 0.99, 0.7, 0.99, 0.7, 0.3]


def skin_geometry():
    """Parámetros por skin: ancho cuerpo (u), alto cuerpo (u), largo arma (u), ancho arma (u),
    factor de mano, tramo y semiancho de golpe."""
    out = {}
    for n in range(1, 36):
        b, w = frame(f"p{n}c"), frame(f"p{n}w")
        bw, bh = b.width / 278 * 0.6, b.height / 278 * 0.6
        wl = w.height / 427 * 0.96
        ww = w.width / w.height * wl
        hf = 0.3367 * min(b.width, b.height) / b.height
        ax, ay = ANCHOR[n]
        xs, ys = POLY[n][0::2], POLY[n][1::2]
        s0, s1 = (min(ys) - ay) * wl, (max(ys) - ay) * wl
        hw = (max(xs) - min(xs)) / 2 * ww
        out[n] = dict(bw=bw, bh=bh, wl=wl, ww=ww, hf=hf, s0=s0, s1=s1, hw=hw, ax=ax, ay=ay)
    return out


def body_png(n):
    b = frame(f"p{n}c")
    f = 0.6 * KB / 278
    return png(b.resize((max(1, round(b.width * f)), max(1, round(b.height * f))), Image.LANCZOS))


def body_red_png(n):
    """Cuerpo teñido de rojo (destello al recibir daño)."""
    b = frame(f"p{n}c")
    f = 0.6 * KB / 278
    im = b.resize((max(1, round(b.width * f)), max(1, round(b.height * f))), Image.LANCZOS)
    r, g, bl, a = im.split()
    zero = g.point(lambda p: 0)
    return png(Image.merge("RGBA", (r, zero, zero, a)))


def weapon_png(n, mirrored=False):
    w = frame(f"p{n}w")
    f = 0.96 * KB / 427
    im = w.resize((max(1, round(w.width * f)), max(1, round(w.height * f))), Image.LANCZOS)
    ax, ay = ANCHOR[n]
    cx, cy = ax * im.width, ay * im.height
    if mirrored:
        im = im.transpose(Image.FLIP_LEFT_RIGHT); cx = im.width - cx
    return png(im), cx, cy


# ---------------------------------------------------------------- fuentes
FONT = ImageFont.truetype(f"{ROOT}/fonts/nunito-bold.ttf", 112)
GH = 168   # alto de celda de glifo (px reales; el disfraz se marca con resolución 2)


def glyph_sets():
    """Devuelve {set: [(png, ancho_px)]} para ASCII 32..126 y la lista de avances."""
    sets = {}
    adv = [FONT.getlength(chr(c)) for c in range(32, 127)]
    styles = {"W": ((255, 255, 255, 255), (20, 40, 60, 230), 6),
              "D": ((68, 68, 68, 255), None, 0),
              "R": ((255, 31, 33, 255), (255, 255, 255, 255), 6),
              "Y": ((255, 205, 40, 255), (90, 50, 0, 255), 6)}
    for key, (fill, stroke, sw) in styles.items():
        lst = []
        for c in range(32, 127):
            a = adv[c - 32]; wpx = max(2, 2 * (int(round(a / 2)) + 5))
            im = Image.new("RGBA", (wpx, GH), (0, 0, 0, 0))
            if c != 32:
                d = ImageDraw.Draw(im)
                if stroke:
                    d.text((wpx / 2 - a / 2, 24), chr(c), font=FONT, fill=fill, stroke_width=sw, stroke_fill=stroke)
                else:
                    d.text((wpx / 2 - a / 2, 24), chr(c), font=FONT, fill=fill)
            lst.append((png(im), wpx))
        sets[key] = lst
    return sets, adv


# ---------------------------------------------------------------- UI
def ui_title():
    im = Image.new("RGBA", (960, 720), (20, 24, 40, 255))
    ban = Image.open(f"{IMG}/banner1024x512.jpg").convert("RGBA").resize((960, 480), Image.LANCZOS)
    im.paste(ban, (0, 0))
    d = ImageDraw.Draw(im)
    for y in range(480, 720):
        d.line([(0, y), (960, y)], fill=(40 - (y - 480) // 12, 28, 18, 255))
    d.rectangle([0, 480, 960, 486], fill=(255, 150, 20, 255))
    f = ImageFont.truetype(f"{ROOT}/fonts/nunito-bold.ttf", 26)
    fs = ImageFont.truetype(f"{ROOT}/fonts/nunito-regular.ttf", 22)
    d.text((480, 512), "Ahoy, matey! Ye have been marooned on a tropical island", font=f, fill=(255, 235, 200), anchor="mm")
    d.text((480, 546), "with other pirates... Only one will survive and plunder the booty.", font=f, fill=(255, 235, 200), anchor="mm")
    d.text((480, 580), "Mouse / WASD to move  -  Click / SPACE to attack  -  Hold to make a dash attack", font=fs, fill=(210, 190, 160), anchor="mm")
    return png(im.resize((480, 360), Image.LANCZOS)) if False else png(im)


def rrect(size, fill, outline=None, r=18, w=3):
    size = (size[0] * 2, size[1] * 2); r *= 2; w *= 2          # 2x: se marcan con bitmapResolution 2
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], r, fill=fill, outline=outline, width=w)
    return im


def ui_button(text, w, h, fill, outline):
    im = rrect((w, h), fill, outline, r=h // 3, w=4)
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(f"{ROOT}/fonts/nunito-bold.ttf", int(h * 0.5) * 2)
    d.text((w, h + 2), text, font=f, fill=(255, 255, 255), anchor="mm", stroke_width=4, stroke_fill=(60, 30, 0))
    return png(im)


def ui_panel(w, h):
    im = rrect((w, h), (255, 248, 230, 245), (120, 70, 20, 255), r=26, w=5)
    return png(im)


def ui_namebox():
    im = rrect((300, 52), (255, 255, 255, 255), (150, 100, 40, 255), r=14, w=4)
    return png(im)


def ui_card(locked=False, selected=False):
    fill = (255, 248, 230, 255) if not locked else (190, 190, 190, 255)
    out = (255, 150, 20, 255) if selected else (120, 70, 20, 255)
    return png(rrect((112, 120), fill, out, r=16, w=6 if selected else 3))


def icon(name, px):
    im = frame(name)
    return png(im.resize((px, px), Image.LANCZOS))


def tile_images():
    g = Image.open(f"{IMG}/04g.jpg").convert("RGBA").resize((108, 108), Image.LANCZOS)
    sand = Image.new("RGBA", (108, 108), (244, 218, 176, 255))
    return png(g), png(sand)


def bar_images():
    # marco y relleno rojo de la barra de vida (box9 / box9filled teñidas)
    def tint(name, a):
        im = frame(name)
        r = Image.new("RGBA", im.size, (255, 31, 33, 255))
        al = im.split()[3].point(lambda p: int(p * a))
        r.putalpha(al)
        return r
    return png(tint("box9", 1.0).resize((128, 21))), png(tint("box9filled", 0.5).resize((128, 21)))


def minimap_png(level, size=180):
    """Minimapa: océano alrededor, arena en el borde y hierba al centro."""
    im = Image.new("RGBA", (size, size), (19, 171, 176, 255))
    m = int(size * 1.5 / 53)
    d = ImageDraw.Draw(im)
    d.rectangle([m, m, size - m, size - m], fill=(244, 218, 176, 255))
    r = {2: 0.4, 9: 0.2}.get(level, 3 * 0.5 / 50) * (size - 2 * m)
    if level != 4:
        d.rectangle([m + r, m + r, size - m - r, size - m - r], fill=(147, 188, 33, 255))
    return png(im)


def circle_png(px, color, alpha=255):
    im = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([1, 1, px - 2, px - 2], fill=color + (alpha,))
    return png(im)


def solid_png(w, h, color):
    return png(Image.new("RGBA", (w, h), color))


def pet_png(i):
    p = frame(f"pet-{i}")
    w = round(0.54 * KB)
    return png(p.resize((w, max(1, round(p.height * w / p.width))), Image.LANCZOS))


def heart_png():
    h = frame("heart")
    r = Image.new("RGBA", h.size, (255, 90, 130, 255))
    r.putalpha(h.split()[3])
    w = round(0.22 * KB)
    return png(r.resize((w, max(1, round(h.height * w / h.width))), Image.LANCZOS))
