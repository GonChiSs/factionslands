"""Iconos 16x16 de los estandartes de civilización (uno por facción), con los colores de cada huevo.
uso: python3 -I tools/gen_icons.py"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src/main/resources/assets/factionlands/textures/item")
EGG = dict(troll=(0x6F8A5E, 0x8A5A2E), knight=(0x2F4FA8, 0xC9C9CF), elf=(0x4E7A32, 0xEDE4C8),
           dwarf=(0xC9531C, 0x3C3C44), human=(0x9C3B2F, 0xD9C7A3))
WOOD, WOOD_HI, GOLD = (0x5E4121), (0x7C5A30), (0xE0B83A)

EMBLEM = dict(
    troll=["X...X", "X...X", ".X.X.", ".X.X.", "..X.."],      # colmillos
    knight=["..X..", "..X..", "XXXXX", "..X..", "..X.."],     # cruz
    elf=["..X..", ".XXX.", "XXXXX", ".XXX.", "..X.."],        # hoja / diamante
    dwarf=["XXX..", "XXXX.", "..X..", "..X..", "..X.."],      # martillo
    human=[".XXX.", "X...X", "X...X", "X...X", ".XXX."],      # sol / escudo redondo
)


def rgb(v):
    return ((v >> 16) & 255, (v >> 8) & 255, v & 255)


def shade(c, f):
    return tuple(max(0, min(255, int(x * f))) for x in c)


def banner(f):
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    px = img.load()
    c0, c1 = rgb(EGG[f][0]), rgb(EGG[f][1])
    for y in range(1, 16):                         # mástil
        px[3, y] = rgb(WOOD) + (255,)
    px[3, 0] = rgb(GOLD) + (255,); px[2, 0] = px[4, 0] = shade(rgb(GOLD), 0.8) + (255,)
    for x in range(3, 14):                         # barra de la que cuelga
        px[x, 1] = rgb(WOOD_HI) + (255,)
    for y in range(2, 13):                         # tela con cola de golondrina
        for x in range(4, 14):
            if y == 11 and not (x <= 7 or x >= 10):
                continue
            if y == 12 and not (x <= 5 or x >= 12):
                continue
            c = c0 if (x % 2 == 0) else shade(c0, 0.93)
            if y == 2 or x in (4, 13):
                c = shade(c0, 0.72)
            px[x, y] = c + (255,)
    for ey, row in enumerate(EMBLEM[f]):           # emblema 5x5
        for ex, ch in enumerate(row):
            if ch == "X":
                px[6 + ex, 4 + ey] = c1 + (255,)
    return img


os.makedirs(OUT, exist_ok=True)
for f in EGG:
    banner(f).save(os.path.join(OUT, f"{f}_civilization.png"))
print("iconos escritos en", OUT)
