#!/usr/bin/env python3
"""Genera YoHoHo.sb3: el juego YoHoHo.io (battle royale pirata) hecho con bloques de Scratch."""
import sys, os, io, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from sb3lib import *
import sb3lib
import assets as A
import gamedata as G

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "YoHoHo.sb3")

stage = Target("Stage", True)
stage.add_costume("ocean", A.solid_png(480, 360, (19, 171, 176, 255)), "png", 240, 180)
T = Target("Pirata")      # sprite único (oculto): simula, dibuja con lápiz y gestiona los menús
T.visible = False

# ----------------------------------------------------------------- disfraces
CI = {}            # nombre -> índice (1-based)
CPX = {}           # nombre -> (ancho, alto) en px


def addc(name, data, rcx=None, rcy=None, res=1, ext="png"):
    im = Image.open(io.BytesIO(data))
    w, h = im.size
    if rcx is None: rcx = w / res / 2 * res
    if rcy is None: rcy = h / 2
    idx = T.add_costume(name, data, ext, rcx, rcy, res)
    CI[name] = idx; CPX[name] = (w, h)
    return idx


NSKIN = 35
geo = A.skin_geometry()
addc("blank", A.solid_png(2, 2, (0, 0, 0, 0)))
B0 = len(T.costumes) + 1
for n in range(1, NSKIN + 1): addc(f"b{n}", A.body_png(n))
R0 = len(T.costumes) + 1
for n in range(1, NSKIN + 1): addc(f"r{n}", A.body_red_png(n))
W0 = len(T.costumes) + 1
for n in range(1, NSKIN + 1):
    d, cx, cy = A.weapon_png(n, False); addc(f"w{n}", d, cx, cy)
M0 = len(T.costumes) + 1
for n in range(1, NSKIN + 1):
    d, cx, cy = A.weapon_png(n, True); addc(f"m{n}", d, cx, cy)

# monedas, cofre, calavera


def fu(name, w, K=A.KD):
    im = A.fit_units(name, w, K)
    return A.png(im)


COIN0 = len(T.costumes) + 1
addc("coin_s", fu("coins_s", 0.4)); addc("coin_m", fu("coins_m", 0.6)); addc("coin_b", fu("coins_b", 0.8))
addc("chest", fu("chest", 0.9)); addc("dead", fu("dead", 1.0))

# decorado (variantes) -> índice
DEC = {}
for fam, variants in G.DECOR_VARIANTS.items():
    DEC[fam] = []
    for v in variants:
        DEC[fam].append(addc(v, fu(v, G.DECOR_W[fam])))
addc("temple", fu("temple", 7.5)); addc("ship", fu("large-ship", 6.0))
for h in ("house1", "house2"):
    addc(f"{h}-b", fu(f"{h}-b", G.DECOR_W[h])); addc(f"{h}-t", fu(f"{h}-t", G.DECOR_W[h]))
# volcán partido en 4 cuartos (tope de tamaño de sprite en Scratch)
vol = A.frame("volcano")
vw = 12.0 * 50; vh = vw * vol.height / vol.width
vol = vol.resize((round(vw), round(vh)), Image.LANCZOS)
VOL = []
for qy in range(2):
    for qx in range(2):
        q = vol.crop((qx * vol.width // 2, qy * vol.height // 2, (qx + 1) * vol.width // 2, (qy + 1) * vol.height // 2))
        VOL.append(addc(f"vol{qx}{qy}", A.png(q)))
VOL_QW, VOL_QH = vol.width / 2 / 50, vol.height / 2 / 50     # en unidades de mundo

# suelo
g_png, s_png = A.tile_images()
addc("tile_grass", g_png); addc("tile_sand", s_png)
for lv in range(1, 8): addc(f"mini{lv}", A.minimap_png(lv))
PET0 = len(T.costumes) + 1
for i in range(1, 10): addc(f"pet{i}", A.pet_png(i))
addc("heart", A.heart_png())
addc("tab_chars_on", A.ui_button("Characters", 110, 30, (255, 140, 0, 255), (140, 70, 0, 255)), res=2)
addc("tab_chars_off", A.ui_button("Characters", 110, 30, (150, 90, 40, 255), (70, 40, 10, 255)), res=2)
addc("tab_pets_on", A.ui_button("Pets", 80, 30, (255, 140, 0, 255), (140, 70, 0, 255)), res=2)
addc("tab_pets_off", A.ui_button("Pets", 80, 30, (150, 90, 40, 255), (70, 40, 10, 255)), res=2)
addc("btn_up", A.ui_button(" ", 230, 30, (255, 140, 0, 255), (140, 70, 0, 255)), res=2)
addc("btn_up_off", A.ui_button(" ", 230, 30, (150, 150, 150, 255), (90, 90, 90, 255)), res=2)
addc("dot_white", A.circle_png(40, (255, 255, 255))); addc("dot_red", A.circle_png(40, (255, 31, 33)))
bar_frame, bar_fill = A.bar_images()
addc("bar_frame", bar_frame); addc("bar_fill", bar_fill)
for nm in ("icon-fog-1", "icon-fog-2", "icon-player", "icon-kill"): addc(nm, A.icon(nm, 64))
addc("icon-coin", A.icon("coins_m", 64))

# interfaz
addc("title", A.ui_title(), res=2)
addc("btn_play", A.ui_button("Play", 200, 56, (255, 140, 0, 255), (140, 70, 0, 255)), res=2)
addc("btn_chars", A.ui_button("Characters", 170, 44, (60, 140, 200, 255), (20, 60, 100, 255)), res=2)
addc("btn_cont", A.ui_button("Continue", 180, 48, (255, 140, 0, 255), (140, 70, 0, 255)), res=2)
addc("btn_back", A.ui_button("Back", 110, 40, (150, 90, 40, 255), (70, 40, 10, 255)), res=2)
addc("namebox", A.ui_namebox(), res=2)
addc("panel_end", A.ui_panel(380, 300), res=2)
addc("panel_skin", A.ui_panel(470, 340), res=2)
addc("card", A.ui_card(), res=2); addc("card_locked", A.ui_card(True), res=2); addc("card_sel", A.ui_card(False, True), res=2)
addc("dim", A.solid_png(4, 4, (0, 0, 0, 120)))
addc("pbar_bg", A.solid_png(40, 6, (90, 60, 30, 255))); addc("pbar_fg", A.solid_png(40, 6, (255, 140, 0, 255)))

# fuentes (ASCII 32..126)
sets, adv = A.glyph_sets()
GBASE = {}
for key in "WDRY":
    GBASE[key] = len(T.costumes)        # costume index = base + (ascii - 31)
    for c, (data, wpx) in zip(range(32, 127), sets[key]):
        addc(key + chr(c), data, res=2)
GADV = [round(a / 2, 2) for a in adv]    # avance por glifo en px lógicos (índice ascii-32)
SZ_GLYPH = 56.0                          # tamaño de fuente en px de los glifos
print("costumes:", len(T.costumes), file=sys.stderr)

# ------------------------------------------------------------- constantes
N_MAX = 80           # jugadores por partida: tú + 79 bots
NPLAYERS = 80
POOL = 3000          # monedas máx
DECOR_MAX = 1000
DEAD_MAX = 40
NE = 0.3
PPU0 = 480 / 9.0
KBODY = A.KB
TURN = 11.25         # grados/tick (h = PI/16)
SWING = 360 * 0.2 / (2 * math.pi)   # I = 0.2 rad
R = 0.0


# ================================================================ datos en listas
def lst(name, vals): P.lst(name, vals)


def Lg(n, i): return l_get(n, i)
def Ls(n, i, v): return l_set(n, i, v)


def padz(a, n=N_MAX): return list(a) + [0] * (n - len(a))


ENT_LISTS = ["ex", "ey", "erot", "etrot", "esc", "ehp", "emhp", "edmg", "efood", "efuel", "eatk", "eatkl", "ewrot", "ewst",
             "ekt", "ekd", "eskin", "edead", "emov", "echg", "ecc", "ead", "eadt", "ekills", "ekt2", "ekrow", "efog",
             "ekiller", "elv", "ept", "etgt", "ehx", "ehy", "eux", "euy", "elast", "eflash", "epet", "epx", "epy", "eprot", "eptop", "epdir", "epheal"]
for n in ENT_LISTS: lst(n, [0] * N_MAX)
lst("ename", [""] * N_MAX)
lst("cx", [0] * POOL); lst("cy", [0] * POOL); lst("cv", [0] * POOL); lst("cnx", [0] * POOL)
lst("cellhead", []); lst("cfree", [])
lst("chx", [0] * 12); lst("chy", [0] * 12); lst("cha", [0] * 12)
for n in ("dx", "dy", "dc", "dl", "dm", "de", "dh"): lst(n, [])
lst("mx", [0] * DEAD_MAX); lst("my", [0] * DEAD_MAX); lst("mw", [0] * DEAD_MAX); lst("mt", [0] * DEAD_MAX); lst("md", [0] * DEAD_MAX)
# tablas por skin (índice = nº de skin)
lst("sk_hp", G.HP[1:36]); lst("sk_dmg", G.DMG[1:36]); lst("sk_price", G.PRICE[1:36]); lst("sk_lvl", G.SKIN_LEVEL[1:36])
lst("sk_bw", [round(geo[n]["bw"], 4) for n in range(1, 36)])
lst("sk_bh", [round(geo[n]["bh"], 4) for n in range(1, 36)])
lst("sk_wl", [round(geo[n]["wl"], 4) for n in range(1, 36)])
lst("sk_hf", [round(geo[n]["hf"], 4) for n in range(1, 36)])
lst("sk_s0", [round(geo[n]["s0"], 4) for n in range(1, 36)])
lst("sk_s1", [round(geo[n]["s1"], 4) for n in range(1, 36)])
lst("sk_hw", [round(geo[n]["hw"], 4) for n in range(1, 36)])
lst("sk_px", [max(CPX[f"b{n}"]) for n in range(1, 36)])
lst("owned", [1] + [0] * 34)
lst("powned", [0] * 9); lst("pet_price", G.PET_PRICE[1:]); lst("pet_up", G.PET_UP); lst("pet_ia", G.PET_IA); lst("pet_bot", G.PET_BOT)
lst("pet_px", [max(CPX[f"pet{i}"]) for i in range(1, 10)])
for n in ("gx", "gy", "gr", "gs", "gk"): lst("g_" + n[1], [0] * 80)
lst("g_t", [-1000] * 80)
lst("xpt", G.XP)
lst("mapsz", G.MAPSIZE); lst("bot_hp", G.BOT_HP); lst("bot_dmg", G.BOT_DMG)
lst("fr_x", G.FR_X); lst("fr_k", G.FR_K); lst("fr_m", G.FR_M); lst("atk_b", G.ATK_B); lst("atk_t", G.ATK_T)
flat_bs, off, cnt = [], [0], [0]
for lv in range(1, 8):
    off.append(len(flat_bs) + 1); cnt.append(len(G.BOT_SKINS[lv])); flat_bs += G.BOT_SKINS[lv]
lst("bs_all", flat_bs); lst("bs_off", off); lst("bs_cnt", cnt)
lst("st_r", G.STORM_R); lst("st_delay", G.STORM_DELAY); lst("st_dur", G.STORM_DUR)
lst("gadv", GADV)
lst("names", G.load_names())
lst("quotes", G.QUOTES); lst("islands", G.ISLANDS)
# altura (unidades de mundo) de cada disfraz de decorado, por índice de disfraz
cuh = [0] * len(T.costumes)
for nme, idx in CI.items():
    cuh[idx - 1] = round(CPX[nme][1] / A.KD, 4)
lst("cuh", cuh)
lst("cuw", [round(CPX[n][0] / A.KD, 4) if True else 0 for n in [t["name"] for t in T.costumes]])

for name, init in [("state", 0), ("tick", 0), ("acc", 0), ("lastT", 0), ("N", 50), ("alive", 50), ("ie", 50), ("lvl", 1),
                   ("camx", 25), ("camy", 25), ("PPU", PPU0), ("follow", 1), ("ret", 0), ("myskin", 1), ("coins", 0), ("xp", 0),
                   ("username", "You"), ("mdown", 0), ("pdown", 0), ("endT", 0), ("rank", 1), ("resTxt", ""), ("resKiller", ""),
                   ("myPet", 0), ("plevel", 0), ("petTab", 0), ("npets", 0), ("gptr", 0), ("surv", 0), ("zx", 25), ("zy", 25), ("zr", 0), ("zT", 0), ("zPh", 1), ("zStep", 0), ("zmx", 25), ("zmy", 25), ("zer", 0),
                   ("zdx", 0), ("zdy", 0), ("zdr", 0), ("dbg", 0), ("won", 0), ("gainXP", 0), ("gainCoins", 0), ("tstart", 0),
                   ("msg1", ""), ("msg1T", 0), ("msg2", ""), ("msg2T", 0), ("msg3", ""), ("msg3T", 0), ("upN", 0), ("upT", -999),
                   ("quote", ""), ("lvlBefore", 1), ("sel", 0), ("toast", ""), ("toastT", 0), ("kbd", 0), ("bB", 0.9), ("bT", 1.1),
                   ("botHP", 100), ("botDMG", 34), ("nDecor", 0), ("nCoins", 0), ("nn", 0), ("nnd", 0), ("bc", 0), ("bcd", 0)]:
    P.var(name, init)
for n in ["pI", "pb", "ptx", "pty", "pm", "i", "j", "k", "gx", "gy", "gx0", "gy0", "gx1", "gy1", "cell", "c", "pv", "nx", "r2", "sx", "sy", "tx", "ty", "ta", "tb",
          "hx", "hy", "ux", "uy", "pa", "dd", "dist", "dmg", "hf", "wl", "wlj", "ss", "sc", "sj", "hh", "ww", "zoom", "halfW", "halfH",
          "off", "px", "py", "cnt", "idx", "wi", "cs", "ch", "lo", "hi", "tw", "txs", "scl", "pct", "sz", "yy", "tlen", "ci", "nm",
          "qx", "qy", "vv", "vis", "mg", "decr", "pos", "tries", "okp", "cc", "ang", "rdy", "tmp", "tmp2", "ldr", "dsk", "dh2", "ex1", "ey1",
          "x2", "y2", "bw1", "pwr", "txtc", "al", "txtx", "tset", "ttxt", "talign", "tpct", "tx0", "tchar", "tn", "fk", "kn", "rr", "gg", "bb",
          "ddx", "ddy", "st", "sgn", "fpx", "fpy", "ffy", "fl", "frr", "xl", "xr", "wyl", "dyw", "hs", "nsc", "osc", "kills", "foodv", "tt"]:
    P.var(n, 0)

v = V
NEH = NE


def ceilf(x): return mathop("ceiling", x)


def MAX(a, b): return emax(a, b)
def MIN(a, b): return emin(a, b)
def tick_(): return v("tick")


def proc(name, params, body):
    p = define(name, params, body)
    T.procs.append(p)
    return p


# ================================================================ utilidades matemáticas
proc("ang2", ["dy", "dx"], [
    If(eq(arg("dx"), 0),
       [If(arg("dy") > 0, [setv("ret", 90)], [If(arg("dy") < 0, [setv("ret", -90)], [setv("ret", 0)])])],
       [setv("ret", atan(arg("dy") / arg("dx"))),
        If(arg("dx") < 0, [If(arg("dy") < 0, [chgv("ret", -180)], [chgv("ret", 180)])])])])

proc("adiff", ["a", "b"], [setv("ret", ((arg("a") - arg("b") + 180) % 360) - 180)])

# distancia punto (px,py) a segmento (ax,ay)-(bx,by)  -> ret
proc("segdist", ["px", "py", "ax", "ay", "bx", "by"], [
    setv("ddx", arg("bx") - arg("ax")), setv("ddy", arg("by") - arg("ay")),
    setv("tmp", v("ddx") * v("ddx") + v("ddy") * v("ddy")),
    If(v("tmp") > 0,
       [setv("tmp2", ((arg("px") - arg("ax")) * v("ddx") + (arg("py") - arg("ay")) * v("ddy")) / v("tmp")),
        If(v("tmp2") < 0, [setv("tmp2", 0)]), If(v("tmp2") > 1, [setv("tmp2", 1)])],
       [setv("tmp2", 0)]),
    setv("ret", sqrt((arg("px") - (arg("ax") + v("tmp2") * v("ddx"))) * (arg("px") - (arg("ax") + v("tmp2") * v("ddx"))) +
                     (arg("py") - (arg("ay") + v("tmp2") * v("ddy"))) * (arg("py") - (arg("ay") + v("tmp2") * v("ddy"))))),
])

# ¿se cortan los segmentos (a-b) y (c-d)?  -> ret 1/0
proc("segx", ["ax", "ay", "bx", "by", "cx2", "cy2", "dx2", "dy2"], [
    setv("tmp", (arg("dy2") - arg("cy2")) * (arg("bx") - arg("ax")) - (arg("dx2") - arg("cx2")) * (arg("by") - arg("ay"))),
    setv("ret", 0),
    If(ne(v("tmp"), 0), [
        setv("tmp2", ((arg("dx2") - arg("cx2")) * (arg("ay") - arg("cy2")) - (arg("dy2") - arg("cy2")) * (arg("ax") - arg("cx2"))) / v("tmp")),
        setv("pv", ((arg("bx") - arg("ax")) * (arg("ay") - arg("cy2")) - (arg("by") - arg("ay")) * (arg("ax") - arg("cx2"))) / v("tmp")),
        If((v("tmp2") >= 0) & (v("tmp2") <= 1) & (v("pv") >= 0) & (v("pv") <= 1), [setv("ret", 1)])])])

# ================================================================ tamaño (por monedas comidas)
CQ = 10     # C del cliente: pasos de tamaño
proc("setscale", ["e"], [
    setv("nsc", Lg("efood", arg("e")) / 5000),
    If(v("nsc") < 1,
       [setv("tmp", (1 - v("nsc")) * (1 - v("nsc")) * (1 - v("nsc")) + 9 * (1 - v("nsc")) * (1 - v("nsc")) * v("nsc") +
             9 * v("nsc") * v("nsc") * (1 - v("nsc")) + 3 * v("nsc") * v("nsc") * v("nsc")),
        setv("nsc", 1 + floor((v("tmp") - 1) / (2 / CQ)) * (2 / CQ))],
       [setv("nsc", 3)]),
    If(eq(arg("e"), 1), [
        If(v("nsc") > Lg("esc", 1), [
            If(tick_() - v("upT") < 60, [chgv("upN", 1)], [setv("upN", 1)]),
            setv("upT", tick_()), setv("msg2", join("Size UP +", v("upN"))), setv("msg2T", 120)])]),
    Ls("esc", arg("e"), v("nsc")),
])

# ================================================================ monedas
proc("addcoin", ["x", "y", "val"], [
    If(l_len("cfree") > 0,
       [setv("c", l_get("cfree", l_len("cfree"))), l_del("cfree", l_len("cfree"))],
       [setv("c", v("nCoins") + 1), If(v("c") > POOL, [setv("c", 0)], [setv("nCoins", v("c"))])]),
    If(v("c") > 0, [
        Ls("cx", v("c"), arg("x")), Ls("cy", v("c"), arg("y")), Ls("cv", v("c"), arg("val")),
        setv("cell", floor(arg("x")) * v("ie") + floor(arg("y")) + 1),
        Ls("cnx", v("c"), Lg("cellhead", v("cell"))), Ls("cellhead", v("cell"), v("c"))]),
])

proc("dropfood", ["x", "y", "tot"], [
    setv("foodv", arg("tot")),
    Until(v("foodv") < 1, [
        If(v("foodv") > 100, [setv("tmp", 50)],
           [If(v("foodv") > 50, [setv("tmp", 25)], [setv("tmp", MIN(v("foodv"), 5))])]),
        setv("ang", rnd(0, 359)), setv("tmp2", rnd(30, 90) / 100),
        setv("px", clamp(arg("x") + cos(v("ang")) * v("tmp2"), 0.2, v("ie") - 0.2)),
        setv("py", clamp(arg("y") + sin(v("ang")) * v("tmp2"), 0.2, v("ie") - 0.2)),
        call("addcoin", v("px"), v("py"), v("tmp")),
        chgv("foodv", -v("tmp")),
    ]),
])

# ================================================================ zona segura (tormenta)
proc("safedir", ["e"], [   # ret=1 si el rumbo de e lleva a (o está en) la zona segura
    setv("dd", (Lg("ex", arg("e")) - v("zx")) * (Lg("ex", arg("e")) - v("zx")) + (Lg("ey", arg("e")) - v("zy")) * (Lg("ey", arg("e")) - v("zy"))),
    If(v("dd") <= v("zr") * v("zr"), [setv("ret", 1)], [
        setv("dist", sqrt(v("dd"))),
        call("ang2", v("zy") - Lg("ey", arg("e")), v("zx") - Lg("ex", arg("e"))),
        setv("ta", v("ret")),
        setv("tb", asin(MIN(1, v("zr") / v("dist")))),
        If(v("tb") > 45, [setv("tb", 45)]),
        call("adiff", Lg("etrot", arg("e")), v("ta")),
        If(fabs(v("ret")) < v("tb"), [setv("ret", 1)], [setv("ret", 0)])])])

# ================================================================ ataque
proc("startattack", ["e"], [
    call("adiff", Lg("etrot", arg("e")), Lg("erot", arg("e"))),
    If((Lg("eatk", arg("e")) > 0) | (fabs(v("ret")) > TURN),
       [Ls("ept", arg("e"), 1)],
       [Ls("eatk", arg("e"), 1), Ls("eatkl", arg("e"), 10), Ls("ept", arg("e"), 0)])])

# ================================================================ nearest enemy / coin
proc("nearest", ["e"], [     # nn = índice del enemigo vivo más cercano (<=12u), nnd = dist^2
    setv("nn", 0), setv("nnd", 99999), setv("j", 0),
    Repeat(v("N"), [chgv("j", 1),
        If((ne(v("j"), arg("e"))) & eq(Lg("edead", v("j")), 0), [
            setv("tmp", Lg("ex", v("j")) - Lg("ex", arg("e"))), setv("tmp2", Lg("ey", v("j")) - Lg("ey", arg("e"))),
            If((fabs(v("tmp")) < 12) & (fabs(v("tmp2")) < 12), [
                setv("dd", v("tmp") * v("tmp") + v("tmp2") * v("tmp2")),
                If(v("dd") < v("nnd"), [setv("nnd", v("dd")), setv("nn", v("j"))])])])])])

proc("nearcoin", ["e"], [    # bc = moneda más cercana en una caja de ±4 celdas
    setv("bc", 0), setv("bcd", 99999),
    setv("gx0", floor(Lg("ex", arg("e")))), setv("gy0", floor(Lg("ey", arg("e")))),
    setv("gx", v("gx0") - 5),
    Repeat(9, [chgv("gx", 1), setv("gy", v("gy0") - 5),
        Repeat(9, [chgv("gy", 1),
            If((v("gx") >= 0) & (v("gx") < v("ie")) & (v("gy") >= 0) & (v("gy") < v("ie")), [
                setv("c", Lg("cellhead", v("gx") * v("ie") + v("gy") + 1)),
                Until(eq(v("c"), 0), [
                    setv("dd", (Lg("cx", v("c")) - Lg("ex", arg("e"))) * (Lg("cx", v("c")) - Lg("ex", arg("e"))) +
                         (Lg("cy", v("c")) - Lg("ey", arg("e"))) * (Lg("cy", v("c")) - Lg("ey", arg("e")))),
                    If(v("dd") < v("bcd"), [setv("bcd", v("dd")), setv("bc", v("c"))]),
                    setv("c", Lg("cnx", v("c")))])])])])])

# ================================================================ IA de los bots (cada 8 ticks)
proc("ai", ["e"], [
    If(tick_() - Lg("eadt", arg("e")) > 180, [
        Ls("eadt", arg("e"), tick_()), Ls("ead", arg("e"), rnd(v("bB") * 100, v("bT") * 100) / 100)]),
    setv("nn", 0),
    If((eq(Lg("elv", arg("e")), 2)) & eq(Lg("edead", 1), 0) & (tick_() > 600), [
        call("ang2", Lg("ey", 1) - Lg("ey", arg("e")), Lg("ex", 1) - Lg("ex", arg("e"))),
        Ls("etrot", arg("e"), v("ret"))],
       [If((eq(Lg("elv", arg("e")), 1)) & (tick_() > 600), [
            call("nearest", arg("e")),
            If(v("nn") > 0, [call("ang2", Lg("ey", v("nn")) - Lg("ey", arg("e")), Lg("ex", v("nn")) - Lg("ex", arg("e"))),
                             Ls("etrot", arg("e"), v("ret"))])],
           [If(((Lg("ex", arg("e")) - v("zx")) * (Lg("ex", arg("e")) - v("zx")) +
                (Lg("ey", arg("e")) - v("zy")) * (Lg("ey", arg("e")) - v("zy"))) <= v("zr") * v("zr"), [
                call("nearcoin", arg("e")),
                If(v("bc") > 0, [
                    If(ne(Lg("etgt", arg("e")), v("bc")), [
                        call("ang2", Lg("cy", v("bc")) - Lg("ey", arg("e")), Lg("cx", v("bc")) - Lg("ex", arg("e"))),
                        Ls("etrot", arg("e"), v("ret") + rnd(-1125, 1125) / 100)]),
                    Ls("etgt", arg("e"), v("bc"))],
                   [call("safedir", arg("e")),
                    If((rnd(1, 10) < 2) | eq(v("ret"), 0), [
                        Ls("etrot", arg("e"), rnd(0, 359)), call("safedir", arg("e")),
                        Repeat(12, [
                            If(eq(v("ret"), 0), [Ls("etrot", arg("e"), rnd(0, 359)), call("safedir", arg("e"))])])],
                       [If(((Lg("ex", arg("e")) <= 2 * NE) & (cos(Lg("etrot", arg("e"))) < 0)) |
                           ((Lg("ey", arg("e")) <= 2 * NE) & (sin(Lg("etrot", arg("e"))) < 0)) |
                           ((Lg("ex", arg("e")) >= v("ie") - 2 * NE) & (cos(Lg("etrot", arg("e"))) > 0)) |
                           ((Lg("ey", arg("e")) >= v("ie") - 2 * NE) & (sin(Lg("etrot", arg("e"))) > 0)),
                           [Ls("etrot", arg("e"), rnd(0, 359))],
                           [Ls("etrot", arg("e"), Lg("etrot", arg("e")) + rnd(-1125, 1125) / 100)])])])],
               [Ls("etrot", arg("e"), rnd(0, 359)), call("safedir", arg("e")),
                Repeat(12, [If(eq(v("ret"), 0), [Ls("etrot", arg("e"), rnd(0, 359)), call("safedir", arg("e"))])])])])]),
    # cargar el ataque
    If(Lg("ecc", arg("e")) > 0, [
        If((Lg("echg", arg("e")) > 0) & (Lg("efuel", arg("e")) >= 80) & (rnd(1, 10) < 2),
           [Ls("echg", arg("e"), 0), call("startattack", arg("e"))],
           [If(eq(Lg("echg", arg("e")), 0) & (rnd(1, 10) < 2), [Ls("echg", arg("e"), 1)])])]),
    # ¿hay alguien a tiro?
    If(eq(Lg("eatk", arg("e")), 0), [
        call("nearest", arg("e")),
        If(v("nn") > 0, [
            If((ne(v("nn"), 1)) | eq(Lg("edead", 1), 0), [
                If(sqrt(v("nnd")) < Lg("ead", arg("e")) * (
                    Lg("sk_bw", Lg("eskin", v("nn"))) * Lg("esc", v("nn")) / 2 + Lg("sk_bw", Lg("eskin", arg("e"))) * Lg("esc", arg("e")) / 2 +
                    Lg("sk_wl", Lg("eskin", arg("e"))) * Lg("esc", arg("e")) * (1 - 27 / 205)), [
                    Ls("echg", arg("e"), 0), call("startattack", arg("e"))])])])]),
])

# ================================================================ comer monedas
proc("eatcoins", ["e"], [
    setv("r2", (0.6 * Lg("esc", arg("e"))) * (0.6 * Lg("esc", arg("e")))),
    setv("gx0", floor(Lg("ex", arg("e")))), setv("gy0", floor(Lg("ey", arg("e")))),
    setv("gx", v("gx0") - 2),
    Repeat(3, [chgv("gx", 1), setv("gy", v("gy0") - 2),
        Repeat(3, [chgv("gy", 1),
            If((v("gx") >= 0) & (v("gx") < v("ie")) & (v("gy") >= 0) & (v("gy") < v("ie")), [
                setv("cell", v("gx") * v("ie") + v("gy") + 1),
                setv("c", Lg("cellhead", v("cell"))), setv("pv", 0),
                Until(eq(v("c"), 0), [
                    setv("nx", Lg("cnx", v("c"))),
                    If(((Lg("cx", v("c")) - Lg("ex", arg("e"))) * (Lg("cx", v("c")) - Lg("ex", arg("e"))) +
                        (Lg("cy", v("c")) - Lg("ey", arg("e"))) * (Lg("cy", v("c")) - Lg("ey", arg("e")))) < v("r2"), [
                        If(eq(v("pv"), 0), [Ls("cellhead", v("cell"), v("nx"))], [Ls("cnx", v("pv"), v("nx"))]),
                        Ls("efood", arg("e"), Lg("efood", arg("e")) + Lg("cv", v("c"))),
                        Ls("cv", v("c"), 0), l_add("cfree", v("c")),
                        call("setscale", arg("e"))],
                       [setv("pv", v("c"))]),
                    setv("c", v("nx"))])])])])])

# ================================================================ geometría del arma
proc("geom", ["e"], [
    setv("pa", Lg("erot", arg("e")) + Lg("ewrot", arg("e"))),
    setv("sk", Lg("eskin", arg("e"))),
    Ls("ehx", arg("e"), Lg("ex", arg("e")) + cos(v("pa")) * Lg("sk_hf", v("sk")) * Lg("esc", arg("e"))),
    Ls("ehy", arg("e"), Lg("ey", arg("e")) + sin(v("pa")) * Lg("sk_hf", v("sk")) * Lg("esc", arg("e"))),
    setv("pa", v("pa") + 225),
    Ls("eux", arg("e"), -sin(v("pa"))), Ls("euy", arg("e"), cos(v("pa"))),
])
P.var("sk", 0); P.var("ti", 0); pass

# ================================================================ un tick de un jugador/bot
proc("move", ["e"], [
    # knockback
    If((Lg("ekt", arg("e")) > -1000) & (tick_() - Lg("ekt", arg("e")) > 10), [Ls("ekt", arg("e"), -1000)]),
    If(Lg("ekt", arg("e")) > -1000, [
        Ls("ex", arg("e"), Lg("ex", arg("e")) + (1 / 60) * 5 * Lg("esc", arg("e")) * cos(Lg("ekd", arg("e")))),
        Ls("ey", arg("e"), Lg("ey", arg("e")) + (1 / 60) * 5 * Lg("esc", arg("e")) * sin(Lg("ekd", arg("e"))))],
       [If(Lg("eatk", arg("e")) > 0, [
            If((Lg("efuel", arg("e")) / 100 > 0.2) & ((10 - Lg("eatkl", arg("e"))) / 10 <= Lg("efuel", arg("e")) / 100), [
                Ls("ex", arg("e"), Lg("ex", arg("e")) + (1 / 60) * 10 * cos(Lg("erot", arg("e")))),
                Ls("ey", arg("e"), Lg("ey", arg("e")) + (1 / 60) * 10 * sin(Lg("erot", arg("e")))),
                If(tick_() - Lg("elast", arg("e")) >= 2, [call("addghost", arg("e")), Ls("elast", arg("e"), tick_())])])],
           [If(Lg("emov", arg("e")) > 0, [
                Ls("ex", arg("e"), Lg("ex", arg("e")) + (1 / 60) * 2.5 * cos(Lg("erot", arg("e")))),
                Ls("ey", arg("e"), Lg("ey", arg("e")) + (1 / 60) * 2.5 * sin(Lg("erot", arg("e"))))])])]),
    Ls("ex", arg("e"), clamp(Lg("ex", arg("e")), NE, v("ie") - NE)),
    Ls("ey", arg("e"), clamp(Lg("ey", arg("e")), NE, v("ie") - NE)),
    If((eq(Lg("eatk", arg("e")), 0)) & (Lg("echg", arg("e")) > 0), [Ls("efuel", arg("e"), MIN(100, Lg("efuel", arg("e")) + 2))]),
    If(Lg("eatk", arg("e")) > 0, [
        Ls("eatkl", arg("e"), Lg("eatkl", arg("e")) - 1),
        If(Lg("eatkl", arg("e")) < 0, [
            Ls("eatk", arg("e"), 0), Ls("ewst", arg("e"), 1 - Lg("ewst", arg("e"))), Ls("efuel", arg("e"), 0)],
           [If(Lg("ewst", arg("e")) > 0, [Ls("ewrot", arg("e"), Lg("ewrot", arg("e")) + SWING)],
               [Ls("ewrot", arg("e"), Lg("ewrot", arg("e")) - SWING)])])]),
    If(eq(Lg("eatk", arg("e")), 0), [
        call("adiff", Lg("etrot", arg("e")), Lg("erot", arg("e"))),
        If(fabs(v("ret")) > 0.0001, [Ls("erot", arg("e"), Lg("erot", arg("e")) + clamp(v("ret"), -TURN, TURN))])]),
    If((eq(Lg("eatk", arg("e")), 0)) & (Lg("ept", arg("e")) > 0), [call("startattack", arg("e"))]),
])

# ================================================================ muerte
proc("die", ["e", "killer"], [
    setv("rr", v("alive")),
    Ls("edead", arg("e"), 1), Ls("ekiller", arg("e"), arg("killer")),
    # marca de calavera
    setv("k", (v("tick") % DEAD_MAX) + 1),
    Ls("mx", v("k"), Lg("ex", arg("e"))), Ls("my", v("k"), Lg("ey", arg("e"))), Ls("md", v("k"), Lg("erot", arg("e"))),
    Ls("mw", v("k"), Lg("sk_bw", Lg("eskin", arg("e"))) * Lg("esc", arg("e"))), Ls("mt", v("k"), 300),
    setv("alive", v("alive") - 1),
    If((eq(v("rr"), 2)) & eq(arg("killer"), 1) & ne(arg("e"), 1),
       [Ls("efood", 1, Lg("efood", 1) + Lg("efood", arg("e"))), call("setscale", 1)],
       [call("dropfood", Lg("ex", arg("e")), Lg("ey", arg("e")), Lg("efood", arg("e")))]),
    If(ne(arg("e"), 1), [Ls("ex", arg("e"), -9999), Ls("ey", arg("e"), -9999)]),
    If(eq(v("follow"), arg("e")), [
        If((arg("killer") > 0) & ne(arg("killer"), arg("e")), [If(eq(Lg("edead", arg("killer")), 0), [setv("follow", arg("killer"))])])]),
    If(eq(arg("e"), 1), [
        setv("rank", v("rr")), setv("won", 0), setv("endT", 60), setv("surv", v("tick")),
        If(arg("killer") > 0, [
            setv("resKiller", Lg("ename", arg("killer"))),
            setv("resTxt", join("Ye have been killed by ", Lg("ename", arg("killer"))))],
           [setv("resTxt", "Ye died in the toxic storm")])]),
    If((eq(v("alive"), 1)) & eq(Lg("edead", 1), 0), [
        setv("won", 1), setv("rank", 1), setv("endT", 30), setv("surv", v("tick")), setv("resTxt", "Yo ho ho! They all feed the fish!")]),
])

# ================================================================ combate: ¿golpea i a j?
proc("hitpass", [], [
    setv("i", 0),
    Repeat(v("N"), [chgv("i", 1),
        If(eq(Lg("edead", v("i")), 0) & (Lg("eatk", v("i")) > 0), [
            setv("sk", Lg("eskin", v("i"))),
            setv("wl", Lg("sk_wl", v("sk")) * Lg("esc", v("i"))),
            setv("sj", Lg("esc", v("i"))),
            # segmento del arma de i
            setv("ex1", Lg("ehx", v("i")) + Lg("eux", v("i")) * Lg("sk_s0", v("sk")) * v("sj")),
            setv("ey1", Lg("ehy", v("i")) + Lg("euy", v("i")) * Lg("sk_s0", v("sk")) * v("sj")),
            setv("x2", Lg("ehx", v("i")) + Lg("eux", v("i")) * Lg("sk_s1", v("sk")) * v("sj")),
            setv("y2", Lg("ehy", v("i")) + Lg("euy", v("i")) * Lg("sk_s1", v("sk")) * v("sj")),
            setv("hw", Lg("sk_hw", v("sk")) * v("sj")),
            setv("j", 0),
            Repeat(v("N"), [chgv("j", 1),
                If(ne(v("j"), v("i")) & eq(Lg("edead", v("j")), 0) & eq(Lg("edead", v("i")), 0) &
                   (tick_() - Lg("ekt", v("j")) > 10), [
                    setv("hh", NE * Lg("esc", v("j")) + Lg("sk_wl", Lg("eskin", v("j"))) * Lg("esc", v("j")) + NE * v("sj") + v("wl")),
                    If((fabs(Lg("ex", v("i")) - Lg("ex", v("j"))) <= v("hh")) & (fabs(Lg("ey", v("i")) - Lg("ey", v("j"))) <= v("hh")), [
                        call("segdist", Lg("ex", v("j")), Lg("ey", v("j")), v("ex1"), v("ey1"), v("x2"), v("y2")),
                        If(v("ret") < NE * 0.8 * Lg("esc", v("j")) + v("hw"), [
                            setv("dmg", MAX(Lg("edmg", v("i")), Lg("efuel", v("i")) * Lg("edmg", v("i")) / 34)),
                            Ls("ehp", v("j"), Lg("ehp", v("j")) - v("dmg")),
                            If(Lg("ehp", v("j")) > 0, [
                                Ls("ekt", v("j"), tick_()), Ls("eflash", v("j"), 30),
                                call("ang2", Lg("ey", v("j")) - Lg("ey", v("i")), Lg("ex", v("j")) - Lg("ex", v("i"))),
                                Ls("ekd", v("j"), v("ret"))],
                               [
                                Ls("ekills", v("i"), Lg("ekills", v("i")) + 1),
                                If(tick_() - Lg("ekt2", v("i")) < 180, [Ls("ekrow", v("i"), Lg("ekrow", v("i")) + 1)], [Ls("ekrow", v("i"), 1)]),
                                Ls("ekt2", v("i"), tick_()),
                                If(eq(v("i"), 1), [
                                    setv("kn", Lg("ekrow", 1)),
                                    If(eq(v("kn"), 1), [setv("msg1", join(join("You killed ", Lg("ename", v("j"))), "!"))],
                                       [If(eq(v("kn"), 2), [setv("msg1", "Double Kill!")],
                                           [If(eq(v("kn"), 3), [setv("msg1", "Triple Kill!")],
                                               [If(eq(v("kn"), 4), [setv("msg1", "x4 Epic Kill!")],
                                                   [If(eq(v("kn"), 5), [setv("msg1", "x5 Insane Kill!")],
                                                       [If(eq(v("kn"), 6), [setv("msg1", "x6 Legendary Kill!")],
                                                           [setv("msg1", join(join("x", v("kn")), " Supernatural Kill!!!"))])])])])])]),
                                    setv("msg1T", 120)]),
                                call("die", v("j"), v("i"))])]),
                        # choque de armas
                        If(eq(Lg("edead", v("j")), 0) & ((eq(Lg("eatk", v("j")), 0)) | (v("j") > v("i"))), [
                            setv("sk", Lg("eskin", v("j"))),
                            call("segx", v("ex1"), v("ey1"), v("x2"), v("y2"),
                                 Lg("ehx", v("j")) + Lg("eux", v("j")) * Lg("sk_s0", v("sk")) * Lg("esc", v("j")),
                                 Lg("ehy", v("j")) + Lg("euy", v("j")) * Lg("sk_s0", v("sk")) * Lg("esc", v("j")),
                                 Lg("ehx", v("j")) + Lg("eux", v("j")) * Lg("sk_s1", v("sk")) * Lg("esc", v("j")),
                                 Lg("ehy", v("j")) + Lg("euy", v("j")) * Lg("sk_s1", v("sk")) * Lg("esc", v("j"))),
                            If(eq(v("ret"), 1), [
                                call("ang2", Lg("ey", v("i")) - Lg("ey", v("j")), Lg("ex", v("i")) - Lg("ex", v("j"))),
                                Ls("ekt", v("i"), tick_()), Ls("ekd", v("i"), v("ret")),
                                Ls("ekt", v("j"), tick_()), Ls("ekd", v("j"), v("ret") + 180)])])])])]),
            # cofres
            setv("k", 0),
            Repeat(10, [chgv("k", 1),
                If(Lg("cha", v("k")) > 0, [
                    If((fabs(Lg("chx", v("k")) - Lg("ex", v("i"))) < 2.2 + v("wl")) & (fabs(Lg("chy", v("k")) - Lg("ey", v("i"))) < 2.2 + v("wl")), [
                        call("segdist", Lg("chx", v("k")), Lg("chy", v("k")), v("ex1"), v("ey1"), v("x2"), v("y2")),
                        If(v("ret") < 0.4 + v("hw"), [
                            Ls("cha", v("k"), 0),
                            call("dropfood", Lg("chx", v("k")), Lg("chy", v("k")), 100)])])])])])])])

# ================================================================ tormenta
proc("announce", [], [
    If(v("tick") > 0, [
        If(eq(v("zPh"), 1), [setv("msg3", "Poison gas is advancing")],
           [setv("msg3", join(join("Poison gas advances in ", ceilf(v("zT"))), " seconds"))]),
        setv("msg3T", 190)])])


proc("storm", [], [
    chgv("zT", -1 / 60),
    If(v("zT") > 0, [
        If(eq(v("zPh"), 1), [chgv("zx", v("zdx")), chgv("zy", v("zdy")), chgv("zr", -v("zdr"))])],
       [If(v("zT") > -1000, [
            If(eq(v("zPh"), 1), [
                If(v("zStep") < 8, [
                    setv("zr", Lg("st_r", v("zStep") + 1) * v("ie")),
                    If(eq(v("zStep"), 0), [setv("zx", v("ie") / 2), setv("zy", v("ie") / 2)],
                       [setv("zx", v("zmx")), setv("zy", v("zmy"))]),
                    If(v("zStep") < 7,
                       [chgv("zStep", 1), setv("zT", Lg("st_delay", v("zStep") + 1))],
                       [setv("zT", -99999999)]),
                    setv("zer", Lg("st_r", v("zStep") + 1) * v("ie")),
                    setv("dd", v("zr") - v("zer")),
                    setv("ang", rnd(0, 359)), setv("tmp", rnd(0, 10000) / 10000 * v("dd")),
                    setv("zmx", v("zx") + cos(v("ang")) * v("tmp")), setv("zmy", v("zy") + sin(v("ang")) * v("tmp")),
                    If(Lg("st_dur", v("zStep") + 1) > 0, [
                        setv("zdx", (v("zmx") - v("zx")) / Lg("st_dur", v("zStep") + 1) / 60),
                        setv("zdy", (v("zmy") - v("zy")) / Lg("st_dur", v("zStep") + 1) / 60),
                        setv("zdr", (v("zr") - v("zer")) / Lg("st_dur", v("zStep") + 1) / 60)],
                       [setv("zdx", 0), setv("zdy", 0), setv("zdr", 0)])],
                   [setv("zdr", 0), setv("zdx", 0), setv("zdy", 0)])],
               [setv("zT", Lg("st_dur", v("zStep") + 1))]),
            setv("zPh", 1 - v("zPh")),
            call("announce")])])])

# ================================================================ tick de simulación
proc("simtick", [], [
    chgv("tick", 1),
    call("storm"),
    If(eq(v("tick") % 8, 0), [
        setv("i", 1),
        Repeat(v("N") - 1, [chgv("i", 1), If(eq(Lg("edead", v("i")), 0), [call("ai", v("i"))])])]),
    setv("i", 0),
    Repeat(v("N"), [chgv("i", 1),
        If(eq(Lg("edead", v("i")), 0), [
            call("move", v("i")),
            If(Lg("eflash", v("i")) > 0, [Ls("eflash", v("i"), Lg("eflash", v("i")) - 1)]),
            call("eatcoins", v("i")),
            # tormenta
            If(((Lg("ex", v("i")) - v("zx")) * (Lg("ex", v("i")) - v("zx")) + (Lg("ey", v("i")) - v("zy")) * (Lg("ey", v("i")) - v("zy"))) > v("zr") * v("zr"), [
                If(Lg("efog", v("i")) > 0, [
                    If(tick_() - Lg("efog", v("i")) > 180, [
                        Ls("efog", v("i"), tick_()), Ls("eflash", v("i"), 30), Ls("ehp", v("i"), Lg("ehp", v("i")) - 0.1 * Lg("emhp", v("i")))])],
                   [Ls("efog", v("i"), tick_())])],
               [Ls("efog", v("i"), 0)]),
            If(Lg("ehp", v("i")) <= 0, [call("die", v("i"), 0)], [call("geom", v("i"))])])]),
    call("hitpass"),
    setv("i", 0),
    Repeat(v("N"), [chgv("i", 1), If(Lg("epet", v("i")) > 0, [call("petstep", v("i"))])]),
    If(v("msg1T") > 0, [chgv("msg1T", -1)]), If(v("msg2T") > 0, [chgv("msg2T", -1)]), If(v("msg3T") > 0, [chgv("msg3T", -1)]),
    setv("i", 0),
    Repeat(DEAD_MAX, [chgv("i", 1), If(Lg("mt", v("i")) > 0, [Ls("mt", v("i"), Lg("mt", v("i")) - 1)])]),
])

# ================================================================ partida nueva
proc("randpos", ["clr"], [   # px,py aleatorio lejos de otros jugadores (clr = distancia mínima)
    setv("tries", 0), setv("okp", 0),
    Until(eq(v("okp"), 1), [
        chgv("tries", 1),
        setv("px", rnd(NE * 100, (v("ie") - NE) * 100) / 100), setv("py", rnd(NE * 100, (v("ie") - NE) * 100) / 100),
        setv("okp", 1),
        If(v("tries") < 60, [
            setv("cc", 0),
            Repeat(v("N"), [chgv("cc", 1),
                If(Lg("ehp", v("cc")) > 0, [
                    If(((Lg("ex", v("cc")) - v("px")) * (Lg("ex", v("cc")) - v("px")) + (Lg("ey", v("cc")) - v("py")) * (Lg("ey", v("cc")) - v("py"))) < arg("clr") * arg("clr"), [setv("okp", 0)])])])],
           [setv("okp", 1)])])])


def decor_items():
    """Bloques que generan el decorado de la isla (según el nivel)."""
    blocks = []
    for lv in range(1, 8):
        body = []
        mrg_r = "0.4*ie" if lv == 2 else "1.5"
        for fam, count, layer, mrg in G.DECOR[lv]:
            variants = G.DECOR_VARIANTS[fam]
            first = CI[variants[0]]
            w = G.DECOR_W[fam]
            m = (v("ie") * 0.4 if lv == 2 else 1.5) if mrg == "r" else 0
            body.append(Repeat(count, [
                chgv("nDecor", 1),
                setv("ci", first + rnd(1, len(variants)) - 1),
                l_add("dc", v("ci")),
                setv("tw", Lg("cuw", v("ci"))), setv("tmp", Lg("cuh", v("ci"))),
                l_add("dx", m + rnd(0, 10000) / 10000 * (v("ie") - v("tw") - 2 * m) + v("tw") / 2),
                l_add("dy", m + rnd(0, 10000) / 10000 * (v("ie") - v("tmp") - 2 * m) + v("tmp") / 2),
                l_add("dl", layer), l_add("dm", 1), l_add("dh", 0),
                l_add("de", MAX(v("tw"), v("tmp")) / 2 + 0.2)]))
        if lv == 4:   # barco encallado
            body += [chgv("nDecor", 1), l_add("dc", CI["ship"]), setv("tmp", Lg("cuh", CI["ship"])),
                     l_add("dx", 1.5 + 3), l_add("dy", v("ie") - 1.5 - v("tmp") / 2),
                     l_add("dl", 0), l_add("dm", 1), l_add("dh", 0), l_add("de", 4)]
        if lv == 5:   # templo
            body += [chgv("nDecor", 1), l_add("dc", CI["temple"]),
                     l_add("dx", v("ie") / 2), l_add("dy", v("ie") / 2),
                     l_add("dl", 0), l_add("dm", 1), l_add("dh", 0), l_add("de", 5)]
        if lv == 6:   # volcán (4 cuartos)
            for q, (qx, qy) in enumerate([(0, 0), (1, 0), (0, 1), (1, 1)]):
                cxo = (qx - 0.5) * VOL_QW; cyo = (qy - 0.5) * VOL_QH
                body += [chgv("nDecor", 1), l_add("dc", VOL[qy * 2 + qx]),
                         l_add("dx", v("ie") / 2 - 0.42 * 12 + 6 + cxo),
                         l_add("dy", v("ie") / 2 - 0.4 * (12 * 1098 / 1024) + (12 * 1098 / 1024) / 2 + cyo),
                         l_add("dl", 0), l_add("dm", 2.03), l_add("dh", 0), l_add("de", 4.5)]
        if lv == 7:   # casas con tejado que se desvanece
            body.append(Repeat(39, [
                setv("tmp2", rnd(1, 2)),
                setv("ci", CI["house1-b"] + (v("tmp2") - 1) * 2),
                setv("tw", Lg("cuw", v("ci"))), setv("tmp", Lg("cuh", v("ci"))),
                setv("px", 1.5 + rnd(0, 10000) / 10000 * (v("ie") - v("tw") - 3) + v("tw") / 2),
                setv("py", 1.5 + rnd(0, 10000) / 10000 * (v("ie") - v("tmp") - 3) + v("tmp") / 2),
                chgv("nDecor", 1), l_add("dc", v("ci")), l_add("dx", v("px")), l_add("dy", v("py")),
                l_add("dl", 0), l_add("dm", 1), l_add("dh", 0), l_add("de", MAX(v("tw"), v("tmp")) / 2 + 0.2),
                chgv("nDecor", 1), l_add("dc", v("ci") + 1), l_add("dx", v("px")), l_add("dy", v("py")),
                l_add("dl", 1), l_add("dm", 1), l_add("dh", 1), l_add("de", MAX(v("tw"), v("tmp")) / 2 + 0.2)]))
        blocks.append(If(eq(v("lvl"), lv), body))
    return blocks


proc("newgame", [], [
    # nivel según la experiencia
    setv("lvl", 1),
    Until(v("xp") < Lg("xpt", v("lvl") + 1), [chgv("lvl", 1)]),
    setv("ie", Lg("mapsz", v("lvl") + 1)), setv("N", NPLAYERS), setv("alive", v("N")),
    setv("botHP", Lg("bot_hp", v("lvl") + 1)), setv("botDMG", Lg("bot_dmg", v("lvl") + 1)),
    setv("bB", Lg("atk_b", v("lvl") + 1)), setv("bT", Lg("atk_t", v("lvl") + 1)),
    setv("tick", 0), setv("won", 0), setv("endT", 0), setv("follow", 1), setv("upT", -999),
    setv("msg1T", 0), setv("msg2T", 0), setv("msg3T", 0),
    setv("zStep", 0), setv("zPh", 1), setv("zT", 0), setv("zr", 0), setv("zx", v("ie") / 2), setv("zy", v("ie") / 2),
    setv("zmx", v("ie") / 2), setv("zmy", v("ie") / 2), setv("zdx", 0), setv("zdy", 0), setv("zdr", 0), setv("zer", 0),
    setv("nDecor", 0), setv("nCoins", 0), setv("i", 0), setv("mdown", 0), setv("pdown", 0),
    l_clear("cfree"), l_clear("cellhead"),
    Repeat(v("ie") * v("ie"), [l_add("cellhead", 0)]),
    setv("i", 0),
    Repeat(DEAD_MAX, [chgv("i", 1), Ls("mt", v("i"), 0)]),
    # decorado
    *[l_clear(n) for n in ("dx", "dy", "dc", "dl", "dm", "de", "dh")],
    *decor_items(),
    # limpiar jugadores
    setv("i", 0),
    Repeat(N_MAX, [chgv("i", 1)] + [Ls(n, v("i"), 0) for n in ENT_LISTS if n not in ("ekt",)] + [Ls("ekt", v("i"), -1000), Ls("edead", v("i"), 1)]),
    # bots 2..N
    setv("i", 1),
    Repeat(v("N") - 1, [
        chgv("i", 1),
        Ls("edead", v("i"), 0),
        Ls("eskin", v("i"), Lg("bs_all", Lg("bs_off", v("lvl") + 1) + rnd(1, Lg("bs_cnt", v("lvl") + 1)) - 1)),
        call("randpos", 3),
        Ls("ex", v("i"), v("px")), Ls("ey", v("i"), v("py")),
        Ls("ehp", v("i"), v("botHP")), Ls("emhp", v("i"), v("botHP")), Ls("edmg", v("i"), v("botDMG")),
        Ls("erot", v("i"), rnd(0, 359)), Ls("etrot", v("i"), Lg("erot", v("i"))),
        Ls("efood", v("i"), floor(5000 / v("N"))), Ls("emov", v("i"), 1), Ls("ewrot", v("i"), 90),
        Ls("ekt2", v("i"), -9999), Ls("eadt", v("i"), -9999),
        Ls("ename", v("i"), Lg("names", rnd(1, l_len("names")))),
        If(v("i") <= 1 + v("N") * Lg("fr_x", v("lvl") + 1), [Ls("elv", v("i"), 1)]),
        If(v("i") <= 1 + v("N") * Lg("fr_m", v("lvl") + 1), [Ls("elv", v("i"), 2)]),
        If(v("i") <= 1 + v("N") * Lg("fr_k", v("lvl") + 1), [Ls("ecc", v("i"), 1)]),
        call("setscale", v("i")), call("geom", v("i")),
    ]),
    # jugador
    Ls("edead", 1, 0), Ls("eskin", 1, v("myskin")), Ls("emhp", 1, Lg("sk_hp", v("myskin"))),
    Ls("edmg", 1, Lg("sk_dmg", v("myskin"))), call("randpos", 6), Ls("ex", 1, v("px")), Ls("ey", 1, v("py")),
    Ls("ehp", 1, Lg("sk_hp", v("myskin"))),
    Ls("erot", 1, rnd(0, 359)), Ls("etrot", 1, Lg("erot", 1)), Ls("efood", 1, 0), Ls("ewrot", 1, 90), Ls("ename", 1, v("username")),
    Ls("esc", 1, 1), Ls("ekt2", 1, -9999),
    call("geom", 1),
    # mascotas: la del jugador y, a veces, la de los bots (a partir de la isla 2)
    If((v("myPet") > 0) & (Lg("powned", v("myPet")) > 0), [Ls("epet", 1, v("myPet")), call("petspawn", 1)]),
    If(v("lvl") >= 2, [
        setv("i", 1),
        Repeat(v("N") - 1, [chgv("i", 1),
            If(rnd(1, 100) <= Lg("pet_bot", v("lvl") + 1), [Ls("epet", v("i"), rnd(1, 9)), call("petspawn", v("i"))])])]),
    setv("i", 0), setv("gptr", 0),
    Repeat(80, [chgv("i", 1), Ls("g_t", v("i"), -1000)]),
    # monedas y cofres
    setv("i", 0),
    Repeat(400, [call("addcoin", rnd(NE * 100, (v("ie") - NE) * 100) / 100, rnd(NE * 100, (v("ie") - NE) * 100) / 100, 5)]),
    setv("i", 0),
    Repeat(10, [chgv("i", 1), call("randpos", 4), Ls("chx", v("i"), v("px")), Ls("chy", v("i"), v("py")), Ls("cha", v("i"), 1)]),
    setv("tstart", v("tick")),
])


# ================================================================ dibujado
def ghost(p): return S("looks_seteffectto", {"VALUE": p}, {"EFFECT": ["GHOST", None]})


def clear_effects(): return S("looks_cleargraphiceffects")


proc("stampw", ["x", "y", "cst", "mult", "dir"], [
    goto((arg("x") - v("camx")) * v("PPU"), (v("camy") - arg("y")) * v("PPU")),
    costume(arg("cst")), size_to(v("PPU") * arg("mult")), direction(arg("dir")), stamp()])

TILE_PCT = 2 / 108 * 100 * 1.02


def stamp_ui(name, x, y, pct=100, dirn=90):
    return [goto(x, y), costume(CI[name]), size_to(pct), direction(dirn), stamp()]


# ---- texto con las fuentes del juego. align: 0 izq, 1 centro, 2 der
proc("text", ["pfx", "base", "str", "x", "y", "pct", "align"], [
    setv("tw", 0), setv("tn", strlen(arg("str"))), setv("ti", 0),
    Repeat(v("tn"), [chgv("ti", 1),
        costume(join(arg("pfx"), letter(v("ti"), arg("str")))),
        chgv("tw", Lg("gadv", costume_number() - arg("base")))]),
    size_to(arg("pct")),
    setv("tx0", arg("x") - v("tw") * arg("pct") / 100 * arg("align") / 2),
    setv("ti", 0),
    Repeat(v("tn"), [chgv("ti", 1),
        costume(join(arg("pfx"), letter(v("ti"), arg("str")))),
        setv("tchar", Lg("gadv", costume_number() - arg("base")) * arg("pct") / 100),
        goto(v("tx0") + v("tchar") / 2, arg("y")), direction(90), stamp(),
        chgv("tx0", v("tchar"))]),
])


def text(set_, s, x, y, pct, align=1):
    return call("text", set_, GBASE[set_], s, x, y, pct, align)


proc("drawground", [], [
    setv("halfW", 240 / v("PPU")), setv("halfH", 180 / v("PPU")),
    setv("gx0", MAX(0, floor((v("camx") - v("halfW")) / 2))), setv("gx1", MIN(v("ie") / 2 - 1, floor((v("camx") + v("halfW")) / 2))),
    setv("gy0", MAX(0, floor((v("camy") - v("halfH")) / 2))), setv("gy1", MIN(v("ie") / 2 - 1, floor((v("camy") + v("halfH")) / 2))),
    If(eq(v("lvl"), 2), [setv("mg", v("ie") * 0.4)], [setv("mg", 1.5)]),
    size_to(v("PPU") * TILE_PCT), direction(90),
    setv("gx", v("gx0") - 1),
    Repeat(v("gx1") - v("gx0") + 1, [chgv("gx", 1), setv("gy", v("gy0") - 1),
        Repeat(v("gy1") - v("gy0") + 1, [chgv("gy", 1),
            setv("tx", v("gx") * 2 + 1), setv("ty", v("gy") * 2 + 1),
            If(ne(v("lvl"), 4) & (v("tx") >= v("mg")) & (v("tx") <= v("ie") - v("mg")) & (v("ty") >= v("mg")) & (v("ty") <= v("ie") - v("mg")),
               [costume(CI["tile_grass"])], [costume(CI["tile_sand"])]),
            goto((v("tx") - v("camx")) * v("PPU"), (v("camy") - v("ty")) * v("PPU")), stamp()])])])

proc("drawdecor", ["layer"], [
    setv("k", 0),
    Repeat(v("nDecor"), [chgv("k", 1),
        If(eq(Lg("dl", v("k")), arg("layer")), [
            If((fabs(Lg("dx", v("k")) - v("camx")) < v("halfW") + Lg("de", v("k"))) &
               (fabs(Lg("dy", v("k")) - v("camy")) < v("halfH") + Lg("de", v("k"))), [
                setv("vis", 1),
                If(eq(Lg("dh", v("k")), 1), [        # tejado: se desvanece si el jugador está debajo
                    If(((Lg("dx", v("k")) - Lg("ex", v("follow"))) * (Lg("dx", v("k")) - Lg("ex", v("follow"))) +
                        (Lg("dy", v("k")) - Lg("ey", v("follow"))) * (Lg("dy", v("k")) - Lg("ey", v("follow")))) <
                       (Lg("de", v("k")) - 0.2) * (Lg("de", v("k")) - 0.2), [setv("vis", 0)])]),
                If(eq(v("vis"), 1), [call("stampw", Lg("dx", v("k")), Lg("dy", v("k")), Lg("dc", v("k")), Lg("dm", v("k")), 90)])])])])])

proc("drawcoins", [], [
    setv("gx0", MAX(0, floor(v("camx") - v("halfW") - 0.5))), setv("gx1", MIN(v("ie") - 1, floor(v("camx") + v("halfW") + 0.5))),
    setv("gy0", MAX(0, floor(v("camy") - v("halfH") - 0.5))), setv("gy1", MIN(v("ie") - 1, floor(v("camy") + v("halfH") + 0.5))),
    # calaveras
    setv("k", 0),
    Repeat(DEAD_MAX, [chgv("k", 1),
        If(Lg("mt", v("k")) > 0, [
            setv("tmp", 1 - Lg("mt", v("k")) / 300),
            ghost(100 * v("tmp") * v("tmp") * v("tmp") * v("tmp") * v("tmp")),
            call("stampw", Lg("mx", v("k")), Lg("my", v("k")), CI["dead"], Lg("mw", v("k")), Lg("md", v("k")) + 90),
            clear_effects()])]),
    size_to(v("PPU")), direction(90),
    setv("gx", v("gx0") - 1),
    Repeat(v("gx1") - v("gx0") + 1, [chgv("gx", 1), setv("gy", v("gy0") - 1),
        Repeat(v("gy1") - v("gy0") + 1, [chgv("gy", 1),
            setv("c", Lg("cellhead", v("gx") * v("ie") + v("gy") + 1)),
            Until(eq(v("c"), 0), [
                If(Lg("cv", v("c")) >= 50, [costume(CI["coin_b"])],
                   [If(Lg("cv", v("c")) >= 25, [costume(CI["coin_m"])], [costume(CI["coin_s"])])]),
                goto((Lg("cx", v("c")) - v("camx")) * v("PPU"), (v("camy") - Lg("cy", v("c"))) * v("PPU")), stamp(),
                setv("c", Lg("cnx", v("c")))])])]),
    # cofres
    setv("k", 0),
    Repeat(10, [chgv("k", 1),
        If((Lg("cha", v("k")) > 0) & (fabs(Lg("chx", v("k")) - v("camx")) < v("halfW") + 1) & (fabs(Lg("chy", v("k")) - v("camy")) < v("halfH") + 1), [
            call("stampw", Lg("chx", v("k")), Lg("chy", v("k")), CI["chest"], 1, 90)])]),
])

# pase 0 nombres, 1 barras de vida, 2 armas, 3 cuerpos
proc("drawents", ["pass"], [
    setv("i", 0),
    Repeat(v("N"), [chgv("i", 1),
        If(eq(Lg("edead", v("i")), 0) &
           (fabs(Lg("ex", v("i")) - v("camx")) < v("halfW") + 1.5 + 2.2 * Lg("esc", v("i"))) &
           (fabs(Lg("ey", v("i")) - v("camy")) < v("halfH") + 1.5 + 2.2 * Lg("esc", v("i"))), [
            setv("sk", Lg("eskin", v("i"))), setv("sc", Lg("esc", v("i"))),
            setv("hh", Lg("sk_bh", v("sk")) * v("sc")),
            If(eq(arg("pass"), 0), [
                If(ne(v("i"), 1) | (v("tick") < 300), [
                    text("D", Lg("ename", v("i")), (Lg("ex", v("i")) - v("camx")) * v("PPU"),
                         (v("camy") - Lg("ey", v("i")) + v("hh") / 2 + NE + 0.1) * v("PPU"), 22, 1)])]),
            If(eq(arg("pass"), 1), [
                setv("ww", 0.5486 * v("sc")), setv("al", 0.09 * v("sc")),
                setv("tx", (Lg("ex", v("i")) - v("camx")) * v("PPU")),
                setv("ty", (v("camy") - Lg("ey", v("i")) - v("hh") / 2 - 1.5 * v("al")) * v("PPU")),
                pen_color("#ff1f21"), pen_transp(50), pen_size(v("al") * v("PPU")),
                setv("tmp", (Lg("ehp", v("i")) / Lg("emhp", v("i"))) * v("ww") * v("PPU")),
                If(v("tmp") > 0, [
                    setv("tmp2", v("al") * v("PPU") / 2),
                    goto(v("tx") - v("ww") * v("PPU") / 2 + v("tmp2"), v("ty")), pen_down(),
                    goto(v("tx") - v("ww") * v("PPU") / 2 + MAX(v("tmp") - v("tmp2"), v("tmp2")), v("ty")), pen_up()]),
                goto(v("tx"), v("ty")), costume(CI["bar_frame"]), size_to(v("ww") * v("PPU") / 128 * 100), direction(90), stamp()]),
            If(eq(arg("pass"), 2), [
                If(Lg("efuel", v("i")) >= 15, [      # brillo azul del arma cargada
                    pen_color("#2c7dff"), pen_transp(70 - 20 * Lg("efuel", v("i")) / 100),
                    pen_size((3 + Lg("efuel", v("i")) / 100 * (7 + rnd(0, 3))) * v("sc") * v("PPU") / 53),
                    goto((Lg("ehx", v("i")) + Lg("eux", v("i")) * Lg("sk_s0", v("sk")) * v("sc") - v("camx")) * v("PPU"),
                         (v("camy") - Lg("ehy", v("i")) - Lg("euy", v("i")) * Lg("sk_s0", v("sk")) * v("sc")) * v("PPU")), pen_down(),
                    goto((Lg("ehx", v("i")) + Lg("eux", v("i")) * Lg("sk_s1", v("sk")) * v("sc") - v("camx")) * v("PPU"),
                         (v("camy") - Lg("ehy", v("i")) - Lg("euy", v("i")) * Lg("sk_s1", v("sk")) * v("sc")) * v("PPU")), pen_up()]),
                If(eq(Lg("ewst", v("i")), 0), [setv("ci", M0 - 1 + v("sk"))], [setv("ci", W0 - 1 + v("sk"))]),
                call("stampw", Lg("ehx", v("i")), Lg("ehy", v("i")), v("ci"), v("sc") * 100 / KBODY, Lg("erot", v("i")) + Lg("ewrot", v("i")) - 45)]),
            If(eq(arg("pass"), 3), [
                call("stampw", Lg("ex", v("i")), Lg("ey", v("i")), B0 - 1 + v("sk"), v("sc") * 100 / KBODY, 90 + Lg("erot", v("i"))),
                If(Lg("eflash", v("i")) > 0, [
                    ghost(100 - 100 * Lg("eflash", v("i")) / 30),
                    call("stampw", Lg("ex", v("i")), Lg("ey", v("i")), R0 - 1 + v("sk"), v("sc") * 100 / KBODY, 90 + Lg("erot", v("i"))),
                    clear_effects()])])])])])

proc("drawfog", [], [
    # ¿el círculo seguro cubre toda la pantalla / no la toca?
    setv("tx", clamp(v("zx"), v("camx") - v("halfW"), v("camx") + v("halfW"))),
    setv("ty", clamp(v("zy"), v("camy") - v("halfH"), v("camy") + v("halfH"))),
    setv("dd", (v("tx") - v("zx")) * (v("tx") - v("zx")) + (v("ty") - v("zy")) * (v("ty") - v("zy"))),
    pen_color("#ff0000"), pen_transp(40),
    If(v("dd") >= v("zr") * v("zr"), [
        pen_size(1200), goto(0, 0), pen_down(), pen_up()],
       [setv("cnt", 0),
        If(((v("camx") - v("halfW") - v("zx")) * (v("camx") - v("halfW") - v("zx")) + (v("camy") - v("halfH") - v("zy")) * (v("camy") - v("halfH") - v("zy"))) <= v("zr") * v("zr"), [chgv("cnt", 1)]),
        If(((v("camx") + v("halfW") - v("zx")) * (v("camx") + v("halfW") - v("zx")) + (v("camy") - v("halfH") - v("zy")) * (v("camy") - v("halfH") - v("zy"))) <= v("zr") * v("zr"), [chgv("cnt", 1)]),
        If(((v("camx") - v("halfW") - v("zx")) * (v("camx") - v("halfW") - v("zx")) + (v("camy") + v("halfH") - v("zy")) * (v("camy") + v("halfH") - v("zy"))) <= v("zr") * v("zr"), [chgv("cnt", 1)]),
        If(((v("camx") + v("halfW") - v("zx")) * (v("camx") + v("halfW") - v("zx")) + (v("camy") + v("halfH") - v("zy")) * (v("camy") + v("halfH") - v("zy"))) <= v("zr") * v("zr"), [chgv("cnt", 1)]),
        If(v("cnt") < 4, [
            pen_size(5), setv("fk", 0),
            Repeat(72, [
                setv("ty", 177.5 - 5 * v("fk")),                       # y de pantalla del centro de la franja
                setv("dyw", v("camy") - v("ty") / v("PPU") - v("zy")),
                If(fabs(v("dyw")) < v("zr"), [
                    setv("tmp", sqrt(v("zr") * v("zr") - v("dyw") * v("dyw"))),
                    setv("xl", (v("zx") - v("tmp") - v("camx")) * v("PPU")), setv("xr", (v("zx") + v("tmp") - v("camx")) * v("PPU")),
                    If(v("xl") > -237, [goto(-246, v("ty")), pen_down(), goto(MIN(v("xl"), 246) - 2.5, v("ty")), pen_up()]),
                    If(v("xr") < 237, [goto(MAX(v("xr"), -246) + 2.5, v("ty")), pen_down(), goto(246, v("ty")), pen_up()])],
                   [goto(-246, v("ty")), pen_down(), goto(246, v("ty")), pen_up()]),
                chgv("fk", 1)])])]),
])


# ---- HUD y minimapa
MM_X, MM_Y, MM_S = 191.4, 131.4, 90.0


proc("mmpt", ["wx", "wy"], [      # mundo -> minimapa (tx,ty), recortado a la caja
    setv("tx", clamp(MM_X - MM_S / 2 + (arg("wx") + 1.5) * (MM_S / (v("ie") + 3)), MM_X - MM_S / 2, MM_X + MM_S / 2)),
    setv("ty", clamp(MM_Y + MM_S / 2 - (arg("wy") + 1.5) * (MM_S / (v("ie") + 3)), MM_Y - MM_S / 2, MM_Y + MM_S / 2))])


def ring(cx_, cy_, rad):
    """Círculo de 20 segmentos en el minimapa."""
    return [setv("ang", 0), call("mmpt", cx_ + rad, cy_), goto(v("tx"), v("ty")), pen_down(),
            Repeat(20, [chgv("ang", 18), call("mmpt", cx_ + rad * cos(v("ang")), cy_ + rad * sin(v("ang"))), goto(v("tx"), v("ty"))]),
            pen_up()]


def clocktxt():
    return [setv("tmp", ceilf(v("zT"))), If(v("tmp") < 0, [setv("tmp", 0)]),
            If(v("tmp") > 9, [setv("txtc", join("0:", v("tmp")))], [setv("txtc", join("0:0", v("tmp")))])]


proc("drawhud", [], [
    stamp_ui("icon-coin", -227, 167, 28),
    text("W", floor(Lg("efood", 1)), -214, 167, 25, 0),
    # minimapa
    goto(MM_X, MM_Y), costume(CI["mini1"] - 1 + v("lvl")), size_to(50), direction(90), stamp(),
    pen_size(1.5), pen_color("#ff1f21"), pen_transp(0),
    ring(v("zx"), v("zy"), v("zr")),
    pen_color("#ffffff"),
    If(v("zStep") < 7, [ring(v("zmx"), v("zmy"), v("zer"))]),
    call("mmpt", Lg("ex", v("follow")), Lg("ey", v("follow"))),
    goto(v("tx"), v("ty")), costume(CI["dot_white"]), size_to(12), direction(90), stamp(),
    # fila inferior: tormenta, jugadores, bajas
    goto(147, 74),
    If(eq(v("zPh"), 0), [costume(CI["icon-fog-1"])], [costume(CI["icon-fog-2"])]),
    size_to(19), stamp(),
    clocktxt(),
    text("W", v("txtc"), 155, 74, 20, 0),
    goto(188, 74), costume(CI["icon-player"]), size_to(19), stamp(),
    text("W", v("alive"), 196, 74, 20, 0),
    goto(218, 74), costume(CI["icon-kill"]), size_to(19), stamp(),
    text("W", Lg("ekills", 1), 226, 74, 20, 0),
    # mensajes
    If(v("msg1T") > 0, [
        setv("tmp", 1 - v("msg1T") / 120), ghost(v("tmp") * v("tmp") * 100),
        text("R", v("msg1"), 0, 108 + 36 * v("tmp"), 32, 1), clear_effects()]),
    If(v("msg2T") > 0, [
        setv("tmp", 1 - v("msg2T") / 120), ghost(v("tmp") * v("tmp") * 100),
        text("W", v("msg2"), 0, 36 + 36 * v("tmp"), 32, 1), clear_effects()]),
    If(v("msg3T") > 0, [text("W", v("msg3"), 0, 166, 26, 1)]),
])


# ================================================================ nivel por experiencia
proc("xp2lvl", ["x"], [
    setv("tmp", 1), Until(arg("x") < Lg("xpt", v("tmp") + 1), [chgv("tmp", 1)]), setv("ret", v("tmp"))])

# nombre: solo caracteres que existen en la fuente (máx. 14)
proc("setname", ["s"], [
    setv("tn", strlen(arg("s"))), setv("ti", 0), setv("nm", ""),
    Until((v("ti") >= v("tn")) | (strlen(v("nm")) >= 14), [
        chgv("ti", 1),
        costume(CI["blank"]), costume(join("D", letter(v("ti"), arg("s")))),
        If(ne(costume_number(), CI["blank"]), [setv("nm", join(v("nm"), letter(v("ti"), arg("s"))))])]),
    If(eq(strlen(v("nm")), 0), [setv("nm", "You")]),
    setv("username", v("nm"))])


def press():
    """Detecta pulsación (flanco) del ratón. Deja 1 en 'pressed' durante este fotograma."""
    return [setv("pressed", 0), If(mouse_down() & eq(v("mdown"), 0), [setv("pressed", 1)]),
            If(mouse_down(), [setv("mdown", 1)], [setv("mdown", 0)])]


P.var("pressed", 0); P.var("nowT", 0); P.var("nticks", 0)


def inbox(cx_, cy_, hw_, hh_):
    return (fabs(mouse_x() - cx_) < hw_) & (fabs(mouse_y() - cy_) < hh_)


proc("preview", ["x", "y", "skin", "px"], [    # cuerpo + arma del skin (como en la portada original)
    setv("pct", arg("px") * 100 / Lg("sk_px", arg("skin"))),
    goto(arg("x") + arg("px") * 0.25, arg("y") - arg("px") * 0.2), costume(M0 - 1 + arg("skin")),
    size_to(v("pct") * 1.0), direction(150), stamp(),
    goto(arg("x"), arg("y")), costume(B0 - 1 + arg("skin")), size_to(v("pct")), direction(90), stamp()])


proc("menuframe", [], [
    pen_clear(),
    stamp_ui("title", 0, 0, 100),
    # isla y botín
    stamp_ui("icon-coin", -214, -166, 28),
    text("W", floor(v("coins")), -204, -166, 28, 0),
    text("W", join("Island: ", Lg("islands", v("lvl") + 1)), 150, -140, 22, 1),
    call("preview", -190, -138, v("myskin"), 34),
    stamp_ui("namebox", 0, -132, 62),
    text("D", v("username"), 0, -132, 34, 1),
    stamp_ui("btn_play", 0, -164, 50),
    stamp_ui("btn_chars", 150, -164, 50),
    *press(),
    If(v("pressed") > 0, [
        If(inbox(0, -132, 95, 17), [
            ask("What's yer name?"), call("setname", answer()), setv("mdown", 1)]),
        If(inbox(0, -164, 55, 15), [
            call("newgame"), setv("state", 1), setv("lastT", timer()), setv("acc", 0),
            If(mouse_down() | key_pressed("space"), [setv("pdown", 1)], [setv("pdown", 0)])]),
        If(inbox(150, -164, 45, 13), [setv("state", 3), setv("toastT", 0)])]),
])

# ---- selección de personaje y mascota
def kfmt(price_expr, x, y, pct):
    return If(price_expr >= 1000, [text("D", join(price_expr / 1000, "k"), x, y, pct, 1)], [text("D", price_expr, x, y, pct, 1)])


proc("skinsframe", [], [
    pen_clear(),
    pen_color("#13abb0"), pen_transp(0), pen_size(1200), goto(0, 0), pen_down(), pen_up(),
    stamp_ui("panel_skin", 0, 6, 100),
    # pestañas
    If(eq(v("petTab"), 0), [stamp_ui("tab_chars_on", -95, 160, 100)], [stamp_ui("tab_chars_off", -95, 160, 100)]),
    If(v("lvl") >= 2, [If(eq(v("petTab"), 1), [stamp_ui("tab_pets_on", 15, 160, 100)], [stamp_ui("tab_pets_off", 15, 160, 100)])]),
    stamp_ui("icon-coin", 120, 160, 28),
    text("D", floor(v("coins")), 132, 160, 30, 0),
    If(eq(v("petTab"), 0), [
        setv("k", 0),
        Repeat(35, [chgv("k", 1),
            setv("qx", (v("k") - 1) % 7), setv("qy", floor((v("k") - 1) / 7)),
            setv("tx", -186 + v("qx") * 62), setv("ty", 118 - v("qy") * 56),
            If(eq(v("k"), v("myskin")), [costume(CI["card_sel"])],
               [If(Lg("owned", v("k")) > 0, [costume(CI["card"])], [costume(CI["card_locked"])])]),
            goto(v("tx"), v("ty")), size_to(46), direction(90), stamp(),
            goto(v("tx"), v("ty") + 6), costume(B0 - 1 + v("k")),
            size_to(32 * 100 / Lg("sk_px", v("k"))), stamp(),
            If(Lg("owned", v("k")) > 0, [],
               [If(Lg("sk_lvl", v("k")) > v("lvl"),
                   [text("D", join("Isl. ", Lg("sk_lvl", v("k"))), v("tx"), v("ty") - 21, 15, 1)],
                   [kfmt(Lg("sk_price", v("k")), v("tx"), v("ty") - 21, 17)])])])],
       [   # ---- mascotas
        setv("k", 0),
        Repeat(9, [chgv("k", 1),
            setv("qx", (v("k") - 1) % 5), setv("qy", floor((v("k") - 1) / 5)),
            setv("tx", -124 + v("qx") * 62), setv("ty", 108 - v("qy") * 62),
            If(eq(v("k"), v("myPet")), [costume(CI["card_sel"])],
               [If(Lg("powned", v("k")) > 0, [costume(CI["card"])], [costume(CI["card_locked"])])]),
            goto(v("tx"), v("ty")), size_to(46), direction(90), stamp(),
            goto(v("tx"), v("ty") + 6), costume(PET0 - 1 + v("k")),
            size_to(34 * 100 / Lg("pet_px", v("k"))), stamp(),
            If(eq(Lg("powned", v("k")), 0), [kfmt(Lg("pet_price", v("k")), v("tx"), v("ty") - 21, 17)])]),
        # regeneración y mejora
        setv("tmp", 0), If(v("myPet") > 0, [setv("tmp", 11 + 2 * v("plevel"))]),
        text("D", join(join("Your pet regenerates: ", v("tmp")), " Health Points/s"), 0, -2, 24, 1),
        # estado del botón de mejora: 0 no disponible, 1 disponible, 2 al máximo
        setv("tmp2", 1),
        If(v("plevel") + 1 >= 15, [setv("tmp2", 2)],
           [If((v("npets") < 1) | (v("lvl") < Lg("pet_ia", v("plevel") + 2)), [setv("tmp2", 0)])]),
        If(eq(v("tmp2"), 1), [
            If(v("coins") >= Lg("pet_up", v("plevel") + 2), [stamp_ui("btn_up", 0, -32, 100)], [stamp_ui("btn_up_off", 0, -32, 100)]),
            text("W", join("Upgrade for ", Lg("pet_up", v("plevel") + 2)), 0, -32, 26, 1)],
           [stamp_ui("btn_up_off", 0, -32, 100),
            If(eq(v("tmp2"), 2), [text("W", "Fully upgraded", 0, -32, 26, 1)], [text("W", "Upgrade Not Available", 0, -32, 26, 1)])]),
        text("D", "Heals you when it is next to you", 0, -62, 20, 1)]),
    If(v("toastT") > 0, [chgv("toastT", -1), text("R", v("toast"), 0, -131, 28, 1)]),
    stamp_ui("btn_back", 0, -153, 45),
    *press(),
    If(v("pressed") > 0, [
        If(inbox(0, -153, 28, 11), [setv("state", 0)]),
        If(inbox(-95, 160, 55, 15), [setv("petTab", 0)]),
        If(inbox(15, 160, 40, 15) & (v("lvl") >= 2), [setv("petTab", 1)]),
        If(eq(v("petTab"), 0), [
          If((mouse_x() > -217) & (mouse_x() < 217) & (mouse_y() < 146) & (mouse_y() > -134), [
            setv("qx", floor((mouse_x() + 186 + 31) / 62)), setv("qy", floor((118 + 28 - mouse_y()) / 56)),
            setv("k", v("qy") * 7 + v("qx") + 1),
            If((v("qx") >= 0) & (v("qx") < 7) & (v("qy") >= 0) & (v("k") >= 1) & (v("k") <= 35), [
                If(Lg("owned", v("k")) > 0, [setv("myskin", v("k"))],
                   [If(Lg("sk_lvl", v("k")) > v("lvl"),
                       [setv("toast", join(join("Reach the ", Lg("islands", Lg("sk_lvl", v("k")) + 1)), " island")), setv("toastT", 120)],
                       [If(v("coins") < Lg("sk_price", v("k")),
                           [setv("toast", "You don't own enough coins"), setv("toastT", 120)],
                           [chgv("coins", -Lg("sk_price", v("k"))), Ls("owned", v("k"), 1), setv("myskin", v("k"))])])])])])],
          [ # mascotas: elegir/comprar y mejorar
            setv("qx", floor((mouse_x() + 124 + 31) / 62)), setv("qy", floor((108 + 31 - mouse_y()) / 62)),
            setv("k", v("qy") * 5 + v("qx") + 1),
            If((v("qx") >= 0) & (v("qx") < 5) & (v("qy") >= 0) & (v("qy") < 2) & (v("k") >= 1) & (v("k") <= 9) & (mouse_y() > 15), [
                If(Lg("powned", v("k")) > 0, [setv("myPet", v("k"))],
                   [If(v("coins") < Lg("pet_price", v("k")),
                       [setv("toast", "You don't own enough coins to unlock this pet"), setv("toastT", 120)],
                       [chgv("coins", -Lg("pet_price", v("k"))), Ls("powned", v("k"), 1), chgv("npets", 1), setv("myPet", v("k"))])])]),
            If(inbox(0, -32, 115, 15) & eq(v("tmp2"), 1) & (v("coins") >= Lg("pet_up", v("plevel") + 2)), [
                chgv("coins", -Lg("pet_up", v("plevel") + 2)), chgv("plevel", 1)]),
            If(inbox(0, -32, 115, 15) & eq(v("tmp2"), 1) & (v("coins") < Lg("pet_up", v("plevel") + 2)), [
                setv("toast", "You don't own enough coins to upgrade your pet"), setv("toastT", 120)])])]),
])


# ---- pantalla final
def timefmt():
    return [setv("tmp", floor(v("surv") / 3600)), setv("tmp2", floor((v("surv") / 60) % 60)),
            If(v("tmp") > 1, [setv("txtc", join(join(join(v("tmp"), " mins "), v("tmp2")), "s"))],
               [If(eq(v("tmp"), 1), [setv("txtc", join(join("1 min ", v("tmp2")), "s"))], [setv("txtc", join(v("tmp2"), "s"))])])]


proc("openend", [], [
    setv("state", 2),
    setv("lvlBefore", v("lvl")),
    setv("gainCoins", floor(Lg("efood", 1))),
    setv("gainXP", 140 * (1 - (v("rank") - 1) / v("N"))),
    chgv("coins", v("gainCoins")), chgv("xp", v("gainXP")),
    setv("quote", Lg("quotes", rnd(1, 4))),
])


proc("endframe", [], [
    pen_color("#000000"), pen_transp(55), pen_size(1200), goto(0, 0), pen_down(), pen_up(),
    stamp_ui("panel_end", 0, 0, 100),
    text("D", join(join('"', v("quote")), '"'), 0, 122, 26, 1),
    text("D", v("resTxt"), 0, 96, 30, 1),
    timefmt(),
    text("D", join("Ye survived ", v("txtc")), 0, 68, 28, 1),
    text("D", join("and placed #", v("rank")), 0, 48, 28, 1),
    text("D", join(join("Ye killed ", Lg("ekills", 1)), " scallywag(s)"), 0, 28, 28, 1),
    text("D", join(join("and plundered ", v("gainCoins")), " coins"), 0, 8, 28, 1),
    text("D", join("Yer booty is now ", floor(v("coins"))), 0, -16, 30, 1),
    # barra de nivel
    call("xp2lvl", v("xp")), setv("lvl", v("ret")),
    pen_size(10), pen_transp(0), pen_color("#8a5a28"), goto(-95, -48), pen_down(), goto(95, -48), pen_up(),
    setv("tmp", (v("xp") - Lg("xpt", v("lvl"))) / (Lg("xpt", v("lvl") + 1) - Lg("xpt", v("lvl")))),
    If(v("lvl") >= 7, [setv("tmp", 1)]),
    pen_color("#ff9a1a"), goto(-95, -48), pen_down(), goto(-95 + 190 * MAX(0.001, v("tmp")), -48), pen_up(),
    text("D", join("Level: ", Lg("islands", v("lvl") + 1)), 0, -66, 24, 1),
    If(v("lvl") > v("lvlBefore"), [text("R", join(join("Level up! Welcome to ", Lg("islands", v("lvl") + 1)), "!"), 0, -84, 26, 1)]),
    stamp_ui("btn_cont", 0, -118, 60),
    *press(),
    If((v("pressed") > 0) & inbox(0, -118, 54, 15), [setv("state", 0)]),
])

# ================================================================ dibujar el mundo + fotograma de juego
proc("render", [], [
    If(eq(Lg("edead", v("follow")), 1), [If(ne(v("follow"), 1), [setv("follow", 1)])]),
    setv("camx", Lg("ex", v("follow"))), setv("camy", Lg("ey", v("follow"))),
    setv("zoom", 1 + 0.2 * (Lg("esc", v("follow")) - 1)),
    setv("PPU", PPU0 / v("zoom")),
    pen_clear(),
    call("drawground"),
    call("drawdecor", 0),
    call("drawghosts"),
    call("drawcoins"),
    call("drawents", 0), call("drawents", 1), call("drawpets", 0), call("drawents", 2), call("drawents", 3),
    call("drawpets", 1),
    call("drawdecor", 1),
    call("drawfog"),
    call("drawhud"),
])


proc("playerinput", [], [
    # teclado (WASD / flechas)
    setv("tx", 0), setv("ty", 0),
    If(key_pressed("w") | key_pressed("up arrow"), [chgv("ty", -1)]),
    If(key_pressed("s") | key_pressed("down arrow"), [chgv("ty", 1)]),
    If(key_pressed("a") | key_pressed("left arrow"), [chgv("tx", -1)]),
    If(key_pressed("d") | key_pressed("right arrow"), [chgv("tx", 1)]),
    If((ne(v("tx"), 0)) | (ne(v("ty"), 0)),
       [call("ang2", v("ty"), v("tx")), Ls("etrot", 1, v("ret")), Ls("emov", 1, 1)],
       [setv("dist", sqrt(mouse_x() * mouse_x() + mouse_y() * mouse_y())),
        If(v("dist") < 20, [Ls("emov", 1, 0)],
           [call("ang2", -mouse_y(), mouse_x()), Ls("etrot", 1, v("ret")), Ls("emov", 1, 1)])]),
    # ataque: mantener = cargar, soltar = atacar (dash)
    setv("tmp", 0), If(mouse_down() | key_pressed("space"), [setv("tmp", 1)]),
    If((v("tmp") > 0) & eq(v("pdown"), 0), [Ls("echg", 1, 1)]),
    If(eq(v("tmp"), 0) & (v("pdown") > 0), [Ls("echg", 1, 0), call("startattack", 1)]),
    setv("pdown", v("tmp")),
])

proc("endcheck", [], [
    If(v("endT") > 0, [chgv("endT", -1), If(eq(v("endT"), 0), [call("openend")])])])

proc("gameframe", [], [
    setv("acc", v("acc") + (v("nowT") - v("lastT")) * 60),
    setv("cnt", floor(v("acc"))), setv("acc", v("acc") - v("cnt")),
    If(v("cnt") > 5, [setv("cnt", 5)]),
    If(v("dbg") > 0, [setv("cnt", v("dbg"))]),
    setv("nticks", v("cnt")),
    If((eq(v("state"), 1)) & eq(Lg("edead", 1), 0), [call("playerinput")]),
    Repeat(v("nticks"), [call("simtick"), call("endcheck")]),
    call("render"),
    If(eq(v("state"), 2), [call("endframe")]),
])


# ================================================================ estela del dash
proc("addghost", ["e"], [
    setv("gptr", (v("gptr") % 80) + 1),
    Ls("g_x", v("gptr"), Lg("ex", arg("e"))), Ls("g_y", v("gptr"), Lg("ey", arg("e"))),
    Ls("g_r", v("gptr"), Lg("erot", arg("e"))), Ls("g_s", v("gptr"), Lg("esc", arg("e"))),
    Ls("g_k", v("gptr"), Lg("eskin", arg("e"))), Ls("g_t", v("gptr"), tick_())])

proc("drawghosts", [], [
    setv("k", 0),
    Repeat(80, [chgv("k", 1),
        If(tick_() - Lg("g_t", v("k")) < 40, [
            If((fabs(Lg("g_x", v("k")) - v("camx")) < v("halfW") + 1.5) & (fabs(Lg("g_y", v("k")) - v("camy")) < v("halfH") + 1.5), [
                ghost(100 - 50 * (1 - (tick_() - Lg("g_t", v("k"))) / 40)),
                call("stampw", Lg("g_x", v("k")), Lg("g_y", v("k")), B0 - 1 + Lg("g_k", v("k")), Lg("g_s", v("k")) * 100 / KBODY, 90 + Lg("g_r", v("k"))),
                clear_effects()])])])])

# ================================================================ mascotas
proc("petspawn", ["e"], [
    setv("ang", rnd(0, 359)),
    Ls("epx", arg("e"), Lg("ex", arg("e")) + cos(v("ang")) * NE * 18), Ls("epy", arg("e"), Lg("ey", arg("e")) + sin(v("ang")) * NE * 18),
    Ls("eprot", arg("e"), v("ang") + 180), Ls("eptop", arg("e"), rnd(0, 359)),
    If(rnd(0, 1) < 1, [Ls("epdir", arg("e"), -1)], [Ls("epdir", arg("e"), 1)]),
    Ls("epheal", arg("e"), -1000)])

def If_expr_heal(e):
    """1 si el dueño está herido, 3 si no (radio de reposo de la mascota)."""
    return 3 - 2 * (Lg("ehp", e) < Lg("emhp", e))


proc("petstep", ["e"], [
    If(eq(Lg("edead", arg("e")), 0) & (v("alive") > 1), [
        setv("pI", sqrt((Lg("ex", arg("e")) - Lg("epx", arg("e"))) * (Lg("ex", arg("e")) - Lg("epx", arg("e"))) +
                        (Lg("ey", arg("e")) - Lg("epy", arg("e"))) * (Lg("ey", arg("e")) - Lg("epy", arg("e"))))),
        setv("pb", 2.5),
        If(Lg("emov", arg("e")) > 0, [
            If(v("pI") < 6 * NE, [setv("pb", v("pb") * (0.4 + (v("pI") / (6 * NE)) * 0.6))]),
            If(v("pI") > 8 * NE, [setv("pb", v("pb") * 1.2)])]),
        If((v("pI") < 2 * NE) & (Lg("ehp", arg("e")) < Lg("emhp", arg("e"))), [setv("pb", 0.4 * 2.5)]),
        setv("ptx", Lg("ex", arg("e"))), setv("pty", Lg("ey", arg("e"))),
        If(Lg("ehp", arg("e")) >= Lg("emhp", arg("e")), [
            setv("pm", 4 * NE),
            If(eq(v("tick") % 300, 0), [If(rnd(0, 1) < 1, [Ls("epdir", arg("e"), -1)], [Ls("epdir", arg("e"), 1)])]),
            Ls("eptop", arg("e"), Lg("eptop", arg("e")) + (v("pb") / v("pm") / 60) * Lg("epdir", arg("e")) * 57.29578),
            setv("ptx", v("ptx") + cos(Lg("eptop", arg("e"))) * v("pm")),
            setv("pty", v("pty") + sin(Lg("eptop", arg("e"))) * v("pm"))]),
        If(v("pI") > NE * If_expr_heal(arg("e")), [
            call("ang2", v("pty") - Lg("epy", arg("e")), v("ptx") - Lg("epx", arg("e"))),
            call("adiff", v("ret"), Lg("eprot", arg("e"))),
            Ls("eprot", arg("e"), Lg("eprot", arg("e")) + clamp(v("ret"), -TURN, TURN))]),
        If((v("pI") < NE) & (Lg("ehp", arg("e")) < Lg("emhp", arg("e"))) & eq(Lg("efog", arg("e")), 0), [
            Ls("ehp", arg("e"), MIN(Lg("emhp", arg("e")), Lg("ehp", arg("e")) + (11 + 2 * v("plevel")) / 60)),
            Ls("epheal", arg("e"), tick_())])],
       [setv("pb", 2.5)]),
    Ls("epx", arg("e"), Lg("epx", arg("e")) + cos(Lg("eprot", arg("e"))) * v("pb") / 60),
    Ls("epy", arg("e"), Lg("epy", arg("e")) + sin(Lg("eprot", arg("e"))) * v("pb") / 60),
])


proc("drawpets", ["layer"], [
    setv("i", 0),
    Repeat(v("N"), [chgv("i", 1),
        If(Lg("epet", v("i")) > 0, [
            setv("tmp", 1),
            If((eq(Lg("epet", v("i")), 3)) | eq(Lg("epet", v("i")), 4) | eq(Lg("epet", v("i")), 5) | eq(Lg("epet", v("i")), 8), [setv("tmp", 0)]),
            If(eq(v("tmp"), arg("layer")) &
               (fabs(Lg("epx", v("i")) - v("camx")) < v("halfW") + 1.5) & (fabs(Lg("epy", v("i")) - v("camy")) < v("halfH") + 1.5), [
                call("stampw", Lg("epx", v("i")), Lg("epy", v("i")), PET0 - 1 + Lg("epet", v("i")), 100 / KBODY, 90 + Lg("eprot", v("i"))),
                If(tick_() - Lg("epheal", v("i")) < 24, [          # corazones mientras cura
                    ghost((tick_() - Lg("epheal", v("i"))) * 100 / 24),
                    call("stampw", Lg("epx", v("i")) + 0.15 * sin(tick_() * 30), Lg("epy", v("i")) - 0.25 - (tick_() - Lg("epheal", v("i"))) * 0.035,
                         CI["heart"], 100 / KBODY, 90),
                    clear_effects()])])])])])

# ================================================================ guion principal
T.on_flag([
    setv("state", 0), setv("lastT", timer()), setv("acc", 0), setv("mdown", 0),
    call("xp2lvl", v("xp")), setv("lvl", v("ret")),
    hide(), pen_clear(),
    Forever([
        setv("nowT", timer()),
        If(eq(v("state"), 0), [call("menuframe")]),
        If(eq(v("state"), 3), [call("skinsframe")]),
        If((eq(v("state"), 1)) | eq(v("state"), 2), [call("gameframe")]),
        setv("lastT", v("nowT")),
    ]),
])

TW = {"framerate": 60, "runtimeOptions": {"maxClones": 300, "miscLimits": False, "fencing": False},
      "interpolation": False, "turbo": False, "hq": True, "width": 480, "height": 360}
project = write_sb3(OUT, stage, [T], tw_config=TW)
import zipfile
print("OK", OUT, os.path.getsize(OUT) // 1024, "KB", len(project["targets"][1]["blocks"]), "bloques", file=sys.stderr)
