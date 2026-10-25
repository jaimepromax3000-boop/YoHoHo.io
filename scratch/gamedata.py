"""Tablas del juego original (yohoho.js) usadas para la versión de Scratch."""
import re, os, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- tablas por skin (índice 1..35), De>=11 (valores por defecto del cliente)
HP = [0, 102, 114, 126, 138, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345, 360, 375, 390, 405,
      420, 435, 450, 465, 480, 495, 510, 525, 540, 555, 570, 585, 600]
DMG = [0, 34, 38, 42, 46, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150,
       155, 160, 165, 170, 175, 180, 185, 190, 195, 200]
PRICE = [0, 100, 150, 200, 250, 300, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 11000, 13000,
         15000, 17000, 20000, 22000, 24000, 26000, 28000, 31000, 34000, 37000, 40000, 43000, 48000, 53000, 58000, 63000, 68000]
SKIN_LEVEL = [0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7]
XP = [0, 140, 700, 2100, 4400, 7600, 13500, 1000000]
ISLANDS = ["", "Tortuga", "Beach", "Easter", "Wreck", "Aztec", "Volcano", "Village"]
MAPSIZE = [10, 50, 50, 60, 70, 80, 90, 100]          # tamaño del mapa por nivel
BOT_HP = [0, 100, 150, 200, 250, 300, 350, 400]
BOT_DMG = [0, 34, 50, 67, 84, 100, 117, 134]
BOT_SKINS = {1: [1, 2, 3, 4, 5], 2: [4, 5, 6, 7, 8, 9], 3: [9, 10, 11, 12, 13, 14], 4: [14, 15, 16, 17, 18, 19],
             5: [19, 20, 21, 22, 23, 24], 6: [24, 25, 26, 27, 28, 29], 7: [29, 30, 31, 32, 33, 34, 35]}
# fracciones de bots por nivel: agresivos (x), cargan (k), cazadores (M)
FR_X = [0, 0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
FR_K = [0, 0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5]
FR_M = [0, 0, 0, 0, 0, 0.05, 0.05, 0.05]
ATK_B = [0, 0.9, 0.9, 0.8, 0.9, 1.0, 1.0, 1.0]
ATK_T = [0, 1.1, 1.1, 1.0, 1.1, 1.2, 1.2, 1.2]
# radio de la tormenta (fracción del mapa), espera y duración de cada paso (segundos)
STORM_R = [0.75, 0.5, 0.375, 0.25, 0.125, 0.0625, 0.03125, 0.015625]
STORM_DELAY = [0, 15, 15, 15, 15, 15, 15, 15]
STORM_DUR = [0, 10, 10, 10, 10, 10, 10, 10]
QUOTES = ["Shiver me timbers!", "Dead men tell no tales...", "No prey, no pay...", "Sink me!"]
YOUTUBERS = ["PewDiePie", "VanossGaming", "markiplier", "jacksepticeye", "DanTDM", "H2ODelirious", "SSunee", "kwebbelkop",
             "Guava Juice", "JellyYT", "Reaction Time", "Daithi", "JeromeASF", "Enes Batur", "DashieGames", "Lachlan",
             "ArcadeGo", "Moo", "Jumbo", "ZerkaaPlays", "Daz Games", "LazarBeam", "Vikksta", "PUMBA", "TARGET", "Sirius",
             "Entak", "MrMEOLA", "Smash", "Godzilla", "Tempest", "Enigma", "Slith", "NATION", "CookieGuy", "La Flame"]

# arrays de decorado por isla (rama del cliente para De!=15/16): (costume, cantidad, capa, margen)
# capa 0 = debajo de los jugadores, 1 = encima
DECOR = {
    1: [("rocks", 99, 0, "r"), ("palms2", 19, 1, "r")],
    2: [("shells", 199, 0, "0"), ("palms2", 9, 1, "0"), ("palms2", 9, 1, "r")],
    3: [("palms", 19, 1, "r"), ("stonehead", 19, 0, "r")],
    4: [("crabs", 39, 0, "0"), ("debris", 39, 0, "0"), ("bush", 99, 0, "0")],
    5: [("palms", 249, 1, "r"), ("bush", 499, 0, "0"), ("ruins", 29, 0, "0")],
    6: [("vsplash", 49, 0, "0"), ("bush", 199, 0, "0"), ("palms", 24, 1, "r"), ("palms3", 99, 1, "r")],
    7: [("rocks", 99, 0, "r"), ("bush", 199, 0, "0"), ("palms", 99, 1, "r")],
}
# ancho en unidades de mundo de cada familia de decorado (variantes -1/-2/-3 incluidas)
DECOR_W = {"rocks": 0.45, "shells": 0.45, "palms": 3.6, "palms2": 3.6, "palms3": 3.6, "bush": 1.2, "ruins": 3.0,
           "stonehead": 1.8, "crabs": 0.9, "debris": 1.5, "vsplash": 3.0, "temple": 7.5, "ship": 6.0,
           "house1": 3.6, "house2": 4.5}
DECOR_VARIANTS = {"rocks": ["rocks"], "shells": ["shells"], "palms": ["palms-1", "palms-2"],
                  "palms2": ["palms2-1", "palms2-2"], "palms3": ["palms3-1", "palms3-2"],
                  "bush": ["bush-1", "bush-2"], "ruins": ["ruins-1", "ruins-2", "ruins-3"],
                  "stonehead": ["stonehead"], "crabs": ["crabs"], "debris": ["debris"], "vsplash": ["vsplash"]}


def load_names(n=270, seed=7):
    rnd = random.Random(seed)
    names = []
    with open(os.path.join(ROOT, "ndata"), encoding="utf8", errors="ignore") as f:
        for line in f:
            s = line.strip()
            if 2 <= len(s) <= 14 and re.fullmatch(r"[A-Za-z0-9 ._\-!]+", s):
                names.append(s)
    names = list(dict.fromkeys(names))
    rnd.shuffle(names)
    names = names[:n] + YOUTUBERS
    rnd.shuffle(names)
    return names
