"""Valida las plantillas NBT (releyéndolas con nbtlib) y renderiza una vista isométrica de control.
uso: python3 -I tools/preview_structures.py <faccion> <salida.png>   |   --validate"""
import os, sys, glob
import nbtlib
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "src/main/resources/data/factionlands/structure")

COL = [("blue_wool", (40, 62, 160)), ("red_wool", (170, 45, 40)), ("orange_wool", (225, 120, 25)), ("yellow_wool", (240, 190, 30)),
       ("white_wool", (235, 235, 235)), ("green_wool", (80, 110, 40)), ("brown_wool", (115, 75, 40)),
       ("oxidized_cut_copper", (70, 160, 135)), ("copper", (190, 110, 70)), ("orange_terracotta", (160, 85, 40)),
       ("red_terracotta", (150, 65, 50)), ("mossy", (95, 125, 85)), ("moss_block", (90, 115, 45)), ("leaves", (50, 115, 45)),
       ("deepslate", (62, 62, 68)), ("blackstone", (40, 36, 44)), ("stone_bricks", (128, 128, 128)), ("bricks", (150, 100, 85)), ("cobblestone", (118, 118, 118)),
       ("stone", (128, 128, 128)), ("grass_block", (95, 150, 60)), ("dirt_path", (160, 130, 75)), ("coarse_dirt", (120, 85, 55)),
       ("dirt", (125, 90, 58)), ("farmland", (95, 60, 35)), ("wheat", (215, 190, 60)), ("carrots", (230, 130, 30)), ("potatoes", (180, 170, 70)),
       ("dark_oak", (70, 45, 22)), ("spruce", (110, 80, 48)), ("birch", (195, 180, 125)), ("oak", (160, 128, 78)),
       ("water", (50, 100, 210)), ("glass", (190, 220, 230)), ("lantern", (255, 205, 110)), ("campfire", (255, 140, 40)),
       ("hay", (205, 170, 40)), ("barrel", (110, 82, 45)), ("chest", (140, 100, 40)), ("iron", (185, 185, 190)),
       ("quartz", (235, 230, 220)), ("fern", (60, 120, 50)), ("grass", (80, 140, 55)), ("bed", (170, 40, 45)),
       ("bookshelf", (120, 90, 55)), ("anvil", (60, 60, 60)), ("furnace", (110, 110, 110)), ("lava", (255, 120, 20)),
       ("pumpkin", (210, 120, 20)), ("ladder", (130, 95, 50)), ("chain", (70, 70, 80)), ("tulip", (220, 90, 60)),
       ("cornflower", (70, 90, 220)), ("poppy", (200, 40, 40)), ("dandelion", (240, 220, 50)), ("daisy", (240, 240, 240)),
       ("bluet", (180, 200, 240)), ("lily", (240, 240, 240)), ("table", (140, 100, 60)), ("grindstone", (140, 140, 145)),
       ("hopper", (80, 80, 85)), ("cauldron", (60, 60, 65)), ("lectern", (150, 110, 60)), ("loom", (150, 120, 80)),
       ("andesite", (140, 140, 140)), ("stone_slab", (150, 150, 150)), ("smooth", (150, 150, 150))]


def color(name):
    n = name.replace("minecraft:", "")
    for k, c in COL:
        if k in n:
            return c
    return (200, 0, 200)


def load(path):
    nbt = nbtlib.load(path)
    size = [int(i) for i in nbt["size"]]
    pal = []
    for p in nbt["palette"]:
        props = {str(k): str(v) for k, v in p.get("Properties", {}).items()}
        pal.append((str(p["Name"]), props))
    blocks = {}
    for b in nbt["blocks"]:
        x, y, z = [int(i) for i in b["pos"]]
        assert 0 <= x < size[0] and 0 <= y < size[1] and 0 <= z < size[2], (path, x, y, z, size)
        idx = int(b["state"]); assert 0 <= idx < len(pal)
        blocks[(x, y, z)] = pal[idx]
    ents = []
    for e in nbt["entities"]:
        x, y, z = [int(i) for i in e["blockPos"]]
        assert 0 <= x < size[0] and 0 <= y < size[1] and 0 <= z < size[2], (path, "entity", x, y, z, size)
        ents.append((x, y, z, str(e["nbt"]["id"])))
    assert int(nbt["DataVersion"]) == 3955
    return size, blocks, ents


def render(blocks, size, s=5):
    sx, sy, sz = size
    W, H = (sx + sz) * s + 4, (sx + sz) * s // 2 + sy * s + 8
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox = sz * s + 2
    for y in range(sy):
        for z in range(sz - 1, -1, -1):
            for x in range(sx):
                b = blocks.get((x, y, z))
                if not b or b[0] == "minecraft:air":
                    continue
                c = color(b[0])
                px = ox + (x - z) * s
                py = (x + z) * s // 2 + (sy - y) * s
                top = [(px, py), (px + s, py + s // 2), (px, py + s), (px - s, py + s // 2)]
                lf = [(px - s, py + s // 2), (px, py + s), (px, py + s + s), (px - s, py + s // 2 + s)]
                rt = [(px, py + s), (px + s, py + s // 2), (px + s, py + s // 2 + s), (px, py + s + s)]
                sh = lambda f: tuple(min(255, int(v * f)) for v in c)
                d.polygon(top, fill=sh(1.1)); d.polygon(lf, fill=sh(0.8)); d.polygon(rt, fill=sh(0.62))
    return im


def main():
    if sys.argv[1] == "--validate":
        n = 0
        for p in sorted(glob.glob(os.path.join(DATA, "**/*.nbt"), recursive=True)):
            size, blocks, ents = load(p); n += 1
        print("NBT válidos:", n)
        return
    fac, out = sys.argv[1], sys.argv[2]
    files = sorted(glob.glob(os.path.join(DATA, fac, "buildings", "*.nbt")))
    ims = []
    order = ["hall", "house_small", "storehouse", "campfire", "house_large", "workshop", "well", "farm", "forge", "barracks",
             "tower", "market", "gate", "guildhall", "stable", "watchpost", "keep", "plaza", "spire", "wall"]
    for n in order:
        size, blocks, ents = load(os.path.join(DATA, fac, "buildings", n + ".nbt"))
        ims.append(render(blocks, size))
    cw, ch = max(i.width for i in ims), max(i.height for i in ims)
    sheet = Image.new("RGB", (cw * 4, ch * 5), (150, 165, 190))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 4) * cw, (i // 4) * ch), im)
    sheet.save(out)


main()
