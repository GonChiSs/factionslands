"""Constructores procedurales de edificios (voxel) por facción.

Cada edificio ocupa una celda de 16x16 (x,z) y hasta 28 de alto.  y=2 es la capa de suelo (hierba);
y=0..1 son tierra para que la plantilla "entierre" los cimientos.  Sur = +z (fachada y puerta).
"""
import random

F = 2            # capa de suelo
CELL = 16
HEIGHT = 28


def pick(opt, rng):
    return rng.choice(opt) if isinstance(opt, (list, tuple)) else opt


class Vol:
    def __init__(self, sx=CELL, sy=HEIGHT, sz=CELL):
        self.sx, self.sy, self.sz = sx, sy, sz
        self.b = {}
        self.ents = []

    def set(self, x, y, z, st):
        if 0 <= x < self.sx and 0 <= y < self.sy and 0 <= z < self.sz:
            self.b[(x, y, z)] = st

    def has(self, x, y, z):
        return (x, y, z) in self.b

    def fill(self, x0, y0, z0, x1, y1, z1, st, rng=None):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.set(x, y, z, pick(st, rng) if rng else st)

    def ent(self, x, y, z, eid):
        self.ents.append((x, y, z, eid, 0))


def log(pal, axis="y"):
    return f"{pal['frame']}[axis={axis}]"


def door(v, x, z, pal, facing="south"):
    d = pal["door"]
    v.set(x, F + 1, z, f"{d}[facing={facing},half=lower,hinge=left,open=false]")
    v.set(x, F + 2, z, f"{d}[facing={facing},half=upper,hinge=left,open=false]")


def lantern(v, x, y, z, hanging=False):
    v.set(x, y, z, f"minecraft:lantern[hanging={'true' if hanging else 'false'}]")


def lamp_post(v, pal, x, z, h=3):
    for y in range(F + 1, F + 1 + h):
        v.set(x, y, z, pal["fence"])
    lantern(v, x, F + 1 + h, z)


def ground(v, pal, rng):
    v.fill(0, 0, 0, v.sx - 1, 1, v.sz - 1, "minecraft:dirt")
    v.fill(0, F, 0, v.sx - 1, F, v.sz - 1, pal["ground"])


def scatter(v, pal, rng, p=0.10):
    for x in range(v.sx):
        for z in range(v.sz):
            if v.b.get((x, F, z)) == pal["ground"] and not v.has(x, F + 1, z) and rng.random() < p:
                v.set(x, F + 1, z, pick(pal["flora"], rng))


def walls(v, pal, rng, x0, z0, w, d, h, open_front=False, windows=True, floor=True, y0=F):
    x1, z1 = x0 + w - 1, z0 + d - 1
    if floor:
        v.fill(x0, y0, z0, x1, y0, z1, pal["floor"], rng)
    for y in range(y0 + 1, y0 + h + 1):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if not (x in (x0, x1) or z in (z0, z1)):
                    continue
                if open_front and z == z1 and x not in (x0, x1):
                    continue
                corner = x in (x0, x1) and z in (z0, z1)
                if corner:
                    st = log(pal)
                elif y == y0 + 1:
                    st = pick(pal["base"], rng)
                else:
                    st = pick(pal["wall"], rng)
                v.set(x, y, z, st)
    # viga superior
    for x in range(x0, x1 + 1):
        for z in (z0, z1):
            if not (open_front and z == z1 and x not in (x0, x1)):
                v.set(x, y0 + h, z, log(pal, "x") if x not in (x0, x1) else log(pal))
    for z in range(z0 + 1, z1):
        for x in (x0, x1):
            v.set(x, y0 + h, z, log(pal, "z"))
    dx = x0 + w // 2
    if windows and h >= 3:
        wy = y0 + 2
        for z in range(z0 + 2, z1 - 1, 3):
            for x in (x0, x1):
                v.set(x, wy, z, pal["glass"])
        for x in range(x0 + 2, x1 - 1, 3):
            if abs(x - dx) > 1 or open_front:
                v.set(x, wy, z0, pal["glass"])
                if not open_front:
                    v.set(x, wy, z1, pal["glass"])
    if not open_front:
        door(v, dx, z1, pal)
        v.set(dx, y0 + 1, z1 + 1, pal["step"]) if z1 + 1 < v.sz else None
    return x1, z1


def roof(v, pal, rng, x0, z0, w, d, ytop, ov=1, along="x"):
    style = pal["style"]
    if style == "elf":
        v.fill(x0 - 1, ytop + 1, z0 - 1, x0 + w, ytop + 1, z0 + d, pal["plank"])
        canopy(v, pal, rng, x0 + (w - 1) / 2, z0 + (d - 1) / 2, w / 2 + 2.2, d / 2 + 2.2, ytop + 2, 3.2)
        return
    n = 0
    if along == "x":
        za, zb, xa, xb = z0 - ov, z0 + d - 1 + ov, x0 - ov, x0 + w - 1 + ov
        i = 0
        while za + i <= zb - i:
            y = ytop + 1 + i
            st = pal["roof"]
            if i == 0 and pal.get("eave"):
                st = pal["eave"]
            elif i % 3 == 2 and pal.get("roof2"):
                st = pal["roof2"]
            v.fill(xa, y, za + i, xb, y, zb - i, st, rng)
            top = (y, za + i, zb - i)
            i += 1
        ytop_roof = top[0]
        if pal.get("roof_deco"):
            for x in range(xa, xb + 1):
                for z in range(top[1], top[2] + 1):
                    if rng.random() < 0.18:
                        v.set(x, ytop_roof + 1, z, pick(pal["roof_deco"], rng))
    else:
        xa, xb, za, zb = x0 - ov, x0 + w - 1 + ov, z0 - ov, z0 + d - 1 + ov
        i = 0
        while xa + i <= xb - i:
            y = ytop + 1 + i
            st = pal["roof"] if (i % 3 != 2 or not pal.get("roof2")) else pal["roof2"]
            v.fill(xa + i, y, za, xb - i, y, zb, st, rng)
            i += 1


def pyramid(v, pal, rng, x0, z0, w, d, ytop, mat=None):
    """tejado piramidal escalonado (torres)."""
    mat = mat or pal["roof"]
    for i in range(8):
        xa, xb, za, zb = x0 - 1 + i, x0 + w - i, z0 - 1 + i, z0 + d - i
        if xa > xb or za > zb:
            break
        v.fill(xa, ytop + 1 + i, za, xb, ytop + 1 + i, zb, mat, rng)


def canopy(v, pal, rng, cx, cz, rx, rz, y0, ry):
    for x in range(v.sx):
        for z in range(v.sz):
            for y in range(int(y0), int(y0 + ry) + 1):
                dx, dz, dy = (x - cx) / rx, (z - cz) / rz, (y - y0) / ry
                if dx * dx + dz * dz + dy * dy <= 1.0 and rng.random() < 0.93:
                    v.set(x, y, z, pick(pal["leaves"], rng))


def chimney(v, pal, x, z, ytop, extra=3):
    for y in range(F + 1, ytop + extra + 1):
        v.set(x, y, z, pal["chimney"])
    v.set(x, ytop + extra + 1, z, "minecraft:campfire[lit=true,signal_fire=false]")


def bed(v, x, z, color="red", facing="east"):
    dx = {"east": 1, "west": -1, "south": 0, "north": 0}[facing]
    dz = {"south": 1, "north": -1, "east": 0, "west": 0}[facing]
    v.set(x, F + 1, z, f"minecraft:{color}_bed[facing={facing},part=foot]")
    v.set(x + dx, F + 1, z + dz, f"minecraft:{color}_bed[facing={facing},part=head]")


def table(v, pal, x, z):
    v.set(x, F + 1, z, pal["fence"])
    v.set(x, F + 2, z, pal["slab"])


def chest(v, x, z, facing="south"):
    v.set(x, F + 1, z, f"minecraft:chest[facing={facing},type=single]")


def barrel(v, x, z):
    v.set(x, F + 1, z, "minecraft:barrel[facing=up]")


def banner(v, pal, x, y, z, h=3):
    for i in range(h):
        v.set(x, y - i, z, pal["banner"][0] if i < h - 1 else pal["banner"][-1])


def stairs(pal, facing, half="bottom"):
    return f"{pal['stair']}[facing={facing},half={half}]"


# ───────────────────────────── edificios ─────────────────────────────

def b_hall(v, pal, rng, fac):
    x0, z0, w, d, h = 1, 2, 14, 12, 5
    x1, z1 = walls(v, pal, rng, x0, z0, w, d, h)
    roof(v, pal, rng, x0, z0, w, d, F + h)
    for x in (3, 5, 7):
        table(v, pal, x + 2, 6); table(v, pal, x + 2, 8)
    chest(v, 2, 3, "south"); barrel(v, 3, 3); barrel(v, 13, 3)
    for x in (4, 8, 12):
        lantern(v, x, F + h - 1, 7, hanging=True)
    banner(v, pal, 5, F + 4, z1 + 1); banner(v, pal, 10, F + 4, z1 + 1)
    chimney(v, pal, x1, 4, F + h + 1, 3)
    for z in (z1 + 2,):
        lamp_post(v, pal, 3, z); lamp_post(v, pal, 12, z)
    v.ent(7, F + 1, 7, f"{fac}_leader")


def b_house_small(v, pal, rng, fac):
    x0, z0, w, d, h = 4, 4, 8, 8, 4
    x1, z1 = walls(v, pal, rng, x0, z0, w, d, h)
    roof(v, pal, rng, x0, z0, w, d, F + h, along="z" if rng.random() < 0.3 else "x")
    bed(v, 5, 6, "red"); chest(v, 10, 5); table(v, pal, 9, 9)
    lantern(v, 8, F + h - 1, 8, hanging=True)
    chimney(v, pal, x0 + 1, z0 + 1, F + h + 2, 2) if pal["style"] != "elf" else None
    lamp_post(v, pal, x0 - 1, z1 + 2)
    v.ent(8, F + 1, 7, f"{fac}_lumberjack")


def b_storehouse(v, pal, rng, fac):
    x0, z0, w, d, h = 2, 3, 12, 10, 4
    for x in (x0, x0 + w - 1):
        for z in (z0, z0 + d - 1):
            for y in range(F + 1, F + h + 1):
                v.set(x, y, z, log(pal))
    v.fill(x0, F, z0, x0 + w - 1, F, z0 + d - 1, pal["floor"], rng)
    for x in range(x0, x0 + w):
        for z in (z0, z0 + d - 1):
            v.set(x, F + h, z, log(pal, "x"))
    for z in range(z0, z0 + d):
        for x in (x0, x0 + w - 1):
            v.set(x, F + h, z, log(pal, "z"))
    roof(v, pal, rng, x0, z0, w, d, F + h)
    for i in range(4):
        v.set(3 + i, F + 1, 4, "minecraft:hay_block[axis=y]"); v.set(3 + i, F + 2, 4, "minecraft:hay_block[axis=y]")
    for i in range(3):
        barrel(v, 11 + i, 4); chest(v, 3 + i * 2, 11, "north")
    for x in (6, 9):
        v.set(x, F + 1, 8, pal["crate"])
    lantern(v, 8, F + h - 1, 7, hanging=True)
    lamp_post(v, pal, 1, 13)
    v.ent(8, F + 1, 7, f"{fac}_mason")


def b_campfire(v, pal, rng, fac):
    cx, cz = 7, 7
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            if max(abs(dx), abs(dz)) == 2 and (abs(dx) + abs(dz)) < 4:
                v.set(cx + dx, F + 1, cz + dz, pal["stone"])
    v.set(cx, F + 1, cz, "minecraft:campfire[lit=true]")
    for k, (dx, dz, fc) in enumerate(((0, -4, "south"), (0, 4, "north"), (-4, 0, "east"), (4, 0, "west"))):
        for s in (-1, 0, 1):
            x, z = (cx + dx + (s if dz else 0)), (cz + dz + (s if dx else 0))
            v.set(x, F + 1, z, stairs(pal, fc))
    for (x, z) in ((1, 1), (14, 1), (1, 14), (14, 14)):
        lamp_post(v, pal, x, z, 3)
    v.ent(cx + 2, F + 1, cz + 3, f"{fac}_scout")


def b_house_large(v, pal, rng, fac):
    x0, z0, w, d, h = 2, 3, 12, 10, 7
    x1, z1 = walls(v, pal, rng, x0, z0, w, d, h)
    v.fill(x0 + 1, F + 4, z0 + 1, x1 - 1, F + 4, z1 - 1, pal["floor"], rng)       # planta alta
    v.fill(x0 + 1, F + 4, z0 + 1, x0 + 1, F + 4, z0 + 3, "minecraft:air")           # hueco de escalera
    for i in range(3):
        v.set(x0 + 1, F + 1 + i, z0 + 1 + i, stairs(pal, "south"))
    for y in (F + 5,):
        for z in range(z0 + 2, z1 - 1, 3):
            for x in (x0, x1):
                v.set(x, y, z, pal["glass"])
    roof(v, pal, rng, x0, z0, w, d, F + h)
    bed(v, 5, 5, "blue"); bed(v, 9, 5, "red"); chest(v, 12, 11, "north"); table(v, pal, 8, 9)
    lantern(v, 8, F + 3, 8, hanging=True)
    chimney(v, pal, x1, z0 + 1, F + h + 1, 2) if pal["style"] != "elf" else None
    v.ent(8, F + 1, 8, f"{fac}_warrior")


def b_workshop(v, pal, rng, fac):
    x0, z0, w, d, h = 2, 3, 12, 10, 4
    x1, z1 = walls(v, pal, rng, x0, z0, w, d, h, open_front=True, windows=False)
    roof(v, pal, rng, x0, z0, w, d, F + h)
    v.set(4, F + 1, 4, "minecraft:crafting_table"); v.set(5, F + 1, 4, "minecraft:smithing_table")
    v.set(7, F + 1, 4, "minecraft:grindstone[face=floor,facing=north]")
    v.set(9, F + 1, 4, "minecraft:anvil[facing=east]"); v.set(11, F + 1, 4, "minecraft:loom[facing=south]")
    table(v, pal, 6, 8); table(v, pal, 10, 8)
    barrel(v, 12, 11); barrel(v, 3, 11)
    for x in range(x0 + 1, x1):
        v.set(x, F + h - 1, z1, pal["awning"][x % 2]) if h > 3 else None
    lantern(v, 7, F + h - 1, 6, hanging=True)
    lamp_post(v, pal, 1, 13); lamp_post(v, pal, 14, 13)
    v.ent(7, F + 1, 7, f"{fac}_smith")


def b_well(v, pal, rng, fac):
    cx = cz = 7
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            if max(abs(dx), abs(dz)) == 2:
                v.set(cx + dx, F, cz + dz, pal["stone"]); v.set(cx + dx, F + 1, cz + dz, pal["stone"])
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            v.set(cx + dx, F, cz + dz, "minecraft:water")
    for (dx, dz) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
        for y in range(F + 2, F + 5):
            v.set(cx + dx, y, cz + dz, pal["fence"] if y < F + 4 else log(pal))
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            if max(abs(dx), abs(dz)) == 2 and abs(dx) + abs(dz) != 4:
                v.set(cx + dx, F + 4, cz + dz, log(pal, "x" if abs(dz) == 2 else "z"))
    roof(v, pal, rng, cx - 2, cz - 2, 5, 5, F + 4, ov=1) if pal["style"] != "elf" else v.fill(cx - 3, F + 5, cz - 3, cx + 3, F + 5, cz + 3, pal["plank"])
    for y in (F + 4, F + 3):
        v.set(cx, y, cz, "minecraft:chain[axis=y]")
    barrel(v, cx + 3, cz + 3)
    v.ent(cx + 3, F + 1, cz - 3, f"{fac}_mystic")


def b_farm(v, pal, rng, fac):
    x0, z0, x1, z1 = 1, 2, 14, 13
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            edge = x in (x0, x1) or z in (z0, z1)
            if edge:
                v.set(x, F + 1, z, pal["fence"])
            else:
                if x == 7 or x == 8:
                    v.set(x, F, z, "minecraft:water") if x == 7 else None
                    if x == 8:
                        v.set(x, F, z, pal["path"])
                else:
                    v.set(x, F, z, "minecraft:farmland[moisture=7]")
                    crop = ["minecraft:wheat[age=7]", "minecraft:carrots[age=7]", "minecraft:potatoes[age=7]"][(z // 3) % 3]
                    v.set(x, F + 1, z, crop)
    v.set(7, F + 1, z1, f"{pal['gate']}[facing=south,open=false]")
    v.set(8, F + 1, z1, f"{pal['gate']}[facing=south,open=false]")
    for (x, z) in ((0, 1), (15, 1), (0, 14), (15, 14)):
        lamp_post(v, pal, x, z, 2)
    v.set(7, F + 2, 2, "minecraft:carved_pumpkin[facing=south]")
    v.ent(8, F + 1, 7, f"{fac}_lumberjack")


def b_forge(v, pal, rng, fac):
    x0, z0, w, d, h = 2, 3, 11, 9, 4
    x1, z1 = walls(v, pal, rng, x0, z0, w, d, h, open_front=True, windows=False)
    roof(v, pal, rng, x0, z0, w, d, F + h)
    v.set(4, F + 1, 4, "minecraft:blast_furnace[facing=south,lit=true]"); v.set(5, F + 1, 4, "minecraft:furnace[facing=south,lit=true]")
    v.set(6, F + 1, 4, "minecraft:furnace[facing=south,lit=true]")
    v.set(8, F + 1, 4, "minecraft:lava_cauldron"); v.set(9, F + 1, 4, "minecraft:water_cauldron[level=3]")
    v.set(5, F + 1, 8, "minecraft:anvil[facing=east]"); v.set(9, F + 1, 8, "minecraft:smithing_table")
    v.set(11, F + 1, 8, "minecraft:grindstone[face=floor,facing=north]")
    barrel(v, 3, 6)
    chimney(v, pal, x1 + 1, z0 + 1, F + h + 1, 3)
    for x in range(x0, x1 + 1):
        v.set(x, F + h - 1, z1, "minecraft:iron_bars") if x % 2 == 0 else None
    lantern(v, 8, F + h - 1, 7, hanging=True)
    lamp_post(v, pal, 1, 13)
    v.ent(7, F + 1, 7, f"{fac}_smith")


def b_barracks(v, pal, rng, fac):
    x0, z0, w, d, h = 1, 4, 14, 8, 4
    x1, z1 = walls(v, pal, rng, x0, z0, w, d, h)
    roof(v, pal, rng, x0, z0, w, d, F + h)
    for i in range(4):
        bed(v, 3 + i * 3, 5, "blue", "south") if False else v.set(3 + i * 3, F + 1, 5, f"minecraft:red_bed[facing=south,part=head]")
        v.set(3 + i * 3, F + 1, 6, "minecraft:red_bed[facing=south,part=foot]")
    for i in range(3):
        chest(v, 3 + i * 4, 10, "north")
    v.set(13, F + 1, 8, "minecraft:grindstone[face=floor,facing=north]")
    lantern(v, 5, F + h - 1, 8, hanging=True); lantern(v, 10, F + h - 1, 8, hanging=True)
    banner(v, pal, 3, F + 4, z1 + 1); banner(v, pal, 12, F + 4, z1 + 1)
    chimney(v, pal, x1, z0 + 1, F + h + 1, 2) if pal["style"] != "elf" else None
    v.ent(7, F + 1, 8, f"{fac}_warrior"); v.ent(9, F + 1, 8, f"{fac}_warrior")


def b_tower(v, pal, rng, fac, x0=4, z0=4, w=8, d=8, h=12, cap=True):
    x1, z1 = x0 + w - 1, z0 + d - 1
    v.fill(x0, F, z0, x1, F, z1, pal["floor"], rng)
    for y in range(F + 1, F + h + 1):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if x in (x0, x1) or z in (z0, z1):
                    v.set(x, y, z, pick(pal["base"], rng) if y < F + 3 else pick(pal["tower"], rng))
    for z in (z0 + 3, z0 + 4):
        v.set(x0, F + 5, z, "minecraft:iron_bars"); v.set(x1, F + 5, z, "minecraft:iron_bars")
        v.set(x0, F + 9, z, "minecraft:iron_bars"); v.set(x1, F + 9, z, "minecraft:iron_bars")
    door(v, x0 + w // 2, z1, pal)
    for y in range(F + 1, F + h + 1):
        v.set(x0 + 1, y, z0 + 1, f"minecraft:ladder[facing=south]")
    v.fill(x0, F + h, z0, x1, F + h, z1, pal["floor"], rng)
    v.set(x0 + 1, F + h, z0 + 1, "minecraft:air")
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if (x in (x0, x1) or z in (z0, z1)) and (x + z) % 2 == 0:
                v.set(x, F + h + 1, z, pick(pal["tower"], rng))
    for (x, z) in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
        lantern(v, x, F + h + 2, z)
    if cap and pal.get("tower_cap"):
        for (x, z) in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
            for y in range(F + h + 2, F + h + 5):
                v.set(x, y, z, log(pal)) if (x, y, z) not in v.b else None
        pyramid(v, pal, rng, x0, z0, w, d, F + h + 4)
    if pal["style"] == "elf":
        canopy(v, pal, rng, x0 + (w - 1) / 2, z0 + (d - 1) / 2, w / 2 + 1.5, d / 2 + 1.5, F + h + 3, 2.6)
    v.ent(x0 + 3, F + h + 1, z0 + 3, f"{fac}_archer")


def b_market(v, pal, rng, fac):
    def stall(xa, za, w=4, d=3):
        for (x, z) in ((xa, za), (xa + w - 1, za), (xa, za + d - 1), (xa + w - 1, za + d - 1)):
            for y in range(F + 1, F + 4):
                v.set(x, y, z, pal["fence"] if y < F + 3 else log(pal))
        for x in range(xa, xa + w):
            for z in range(za, za + d):
                v.set(x, F + 4, z, pal["awning"][(x + z) % len(pal["awning"])])
        for x in range(xa + 1, xa + w - 1):
            v.set(x, F + 1, za, pal["fence"]); v.set(x, F + 2, za, pal["slab"])
        barrel(v, xa + 1, za + 1); v.set(xa + 2, F + 1, za + 1, pal["crate"])
        lantern(v, xa + 1, F + 3, za + 2, hanging=True)
    stall(1, 2); stall(6, 2); stall(11, 2); stall(3, 9); stall(9, 9)
    v.ent(8, F + 1, 7, f"{fac}_lumberjack")


def b_gate(v, pal, rng, fac):
    for x in range(16):
        for z in (6, 7, 8):
            for y in range(F + 1, F + 7):
                v.set(x, y, z, pick(pal["tower"], rng) if y > F + 1 else pick(pal["base"], rng))
    for x in range(16):
        for z in (6, 8):
            if x % 2 == 0:
                v.set(x, F + 7, z, pick(pal["tower"], rng))
    for x in range(6, 10):
        for y in range(F + 1, F + 5):
            for z in (6, 7, 8):
                v.set(x, y, z, "minecraft:air")
        for y in range(F + 1, F + 5):
            v.set(x, y, 7, "minecraft:iron_bars")
    for (xa, xb) in ((0, 3), (12, 15)):
        for x in range(xa, xb + 1):
            for z in range(5, 10):
                for y in range(F + 1, F + 9):
                    if x in (xa, xb) or z in (5, 9):
                        v.set(x, y, z, pick(pal["tower"], rng))
        for x in range(xa, xb + 1):
            for z in range(5, 10):
                if (x + z) % 2 == 0 and (x in (xa, xb) or z in (5, 9)):
                    v.set(x, F + 9, z, pick(pal["tower"], rng))
        lantern(v, xa + 1, F + 9, 7) if False else None
    banner(v, pal, 5, F + 6, 9); banner(v, pal, 10, F + 6, 9)
    for (x, z) in ((5, 11), (10, 11)):
        lamp_post(v, pal, x, z, 3)
    v.ent(7, F + 1, 10, f"{fac}_warrior"); v.ent(9, F + 1, 10, f"{fac}_warrior")


def b_guildhall(v, pal, rng, fac):
    x0, z0, w, d, h = 2, 3, 12, 10, 5
    x1, z1 = walls(v, pal, rng, x0, z0, w, d, h)
    for z in range(z0 + 2, z1 - 1, 3):
        for x in (x0, x1):
            v.set(x, F + 3, z, pal["glass"])
    roof(v, pal, rng, x0, z0, w, d, F + h)
    for x in range(4, 12):
        v.set(x, F + 1, 4, "minecraft:bookshelf"); v.set(x, F + 2, 4, "minecraft:bookshelf")
    v.set(8, F + 1, 8, "minecraft:lectern[facing=north]"); table(v, pal, 5, 8); table(v, pal, 11, 8)
    lantern(v, 8, F + h - 1, 6, hanging=True)
    banner(v, pal, 6, F + 5, z1 + 1); banner(v, pal, 9, F + 5, z1 + 1)
    for i in range(3):
        v.set(7 + i, F + 1, z1 + 2, stairs(pal, "north"))
    lamp_post(v, pal, 3, z1 + 2); lamp_post(v, pal, 12, z1 + 2)
    chimney(v, pal, x1, z0 + 1, F + h + 1, 2) if pal["style"] != "elf" else None
    v.ent(8, F + 1, 7, f"{fac}_mason")


def b_stable(v, pal, rng, fac):
    x0, z0, w, d, h = 1, 3, 14, 10, 4
    for x in (x0, x0 + w - 1, 7):
        for z in (z0, z0 + d - 1):
            for y in range(F + 1, F + h + 1):
                v.set(x, y, z, log(pal))
    for x in range(x0, x0 + w):
        for z in (z0, z0 + d - 1):
            v.set(x, F + h, z, log(pal, "x"))
    for z in range(z0, z0 + d):
        for x in (x0, x0 + w - 1):
            v.set(x, F + h, z, log(pal, "z"))
    roof(v, pal, rng, x0, z0, w, d, F + h)
    for x in range(x0, x0 + w):
        v.set(x, F + 1, z0 + d - 1, pal["fence"]) if x not in (7, 8) else None
    for z in range(z0 + 1, z0 + d - 1):
        v.set(7, F + 1, z, pal["fence"]) if z != 6 else None
    for x in (2, 12):
        v.set(x, F + 1, 4, "minecraft:hay_block[axis=y]"); v.set(x + 1, F + 1, 4, "minecraft:hay_block[axis=y]")
    v.set(4, F + 1, 4, "minecraft:water_cauldron[level=3]"); v.set(10, F + 1, 4, "minecraft:water_cauldron[level=3]")
    lantern(v, 4, F + h - 1, 8, hanging=True); lantern(v, 11, F + h - 1, 8, hanging=True)
    v.ent(4, F + 1, 7, "minecraft:horse"); v.ent(11, F + 1, 7, "minecraft:horse")
    v.ent(8, F + 1, 11, f"{fac}_lumberjack")


def b_watchpost(v, pal, rng, fac):
    x0, z0, w, d = 5, 5, 6, 6
    x1, z1 = x0 + w - 1, z0 + d - 1
    if pal["style"] in ("knight", "dwarf", "troll"):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                for y in range(F + 1, F + 4):
                    v.set(x, y, z, pick(pal["base"], rng))
        v.set(x0 + w // 2, F + 1, z1, "minecraft:air"); v.set(x0 + w // 2, F + 2, z1, "minecraft:air")
        base_y = F + 3
    else:
        base_y = F
    top = base_y + 4
    for (x, z) in ((x0, z0), (x1, z0), (x0, z1), (x1, z1)):
        for y in range(base_y + 1, top + 4):
            v.set(x, y, z, log(pal))
    v.fill(x0, top, z0, x1, top, z1, pal["floor"], rng)
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            if x in (x0, x1) or z in (z0, z1):
                v.set(x, top + 1, z, pal["fence"]) if not (x in (x0, x1) and z in (z0, z1)) else None
    roof(v, pal, rng, x0, z0, w, d, top + 3, ov=1)
    for y in range(base_y + 1, top + 1):
        v.set(x0 + 1, y, z1, "minecraft:ladder[facing=east]")
    lantern(v, x0 + 2, top + 3, z0 + 2, hanging=True)
    v.ent(x0 + 2, top + 1, z0 + 2, f"{fac}_scout")


def b_keep(v, pal, rng, fac):
    x0, z0, w, d, h = 3, 3, 10, 10, 9
    walls(v, pal, rng, x0, z0, w, d, h, windows=True)
    for x in range(x0, x0 + w):
        for z in range(z0, z0 + d):
            if (x in (x0, x0 + w - 1) or z in (z0, z0 + d - 1)) and (x + z) % 2 == 0:
                v.set(x, F + h + 1, z, pick(pal["tower"], rng))
    v.fill(x0 + 1, F + h, z0 + 1, x0 + w - 2, F + h, z0 + d - 2, pal["floor"], rng)
    for y in range(F + 1, F + 5):
        for (x, z) in ((6, 5), (7, 5), (8, 5), (9, 5)):
            pass
    for (xa, za) in ((0, 0), (13, 0), (0, 13), (13, 13)):
        for x in range(xa, xa + 3):
            for z in range(za, za + 3):
                for y in range(F + 1, F + 12):
                    if x in (xa, xa + 2) or z in (za, za + 2):
                        v.set(x, y, z, pick(pal["tower"], rng))
                v.set(x, F + 12, z, pal["floor"])
        for x in range(xa, xa + 3):
            for z in range(za, za + 3):
                if (x + z) % 2 == 0 and (x in (xa, xa + 2) or z in (za, za + 2)):
                    v.set(x, F + 13, z, pick(pal["tower"], rng))
        if pal.get("tower_cap"):
            pyramid(v, pal, rng, xa, za, 3, 3, F + 13)
    for x in range(3, 13):
        v.set(x, F + 1, 3, "minecraft:air") if False else None
    for dx in range(-2, 3):
        v.set(7 + dx, F + 1, 13, pal["step"]) if False else None
    for i in range(3):
        v.set(6 + i, F + 1, 14, stairs(pal, "north"))
    for y in range(F + 1, F + 8):
        v.set(7, y, 12, "minecraft:ladder[facing=north]") if False else None
    banner(v, pal, 6, F + 7, 13); banner(v, pal, 9, F + 7, 13)
    table(v, pal, 7, 8); table(v, pal, 9, 8)
    lantern(v, 8, F + 6, 8, hanging=True)
    v.ent(8, F + 1, 7, f"{fac}_warrior"); v.ent(8, F + 1, 10, f"{fac}_leader")


def b_plaza(v, pal, rng, fac):
    for x in range(16):
        for z in range(16):
            if (x + z) % 5 == 0 or (x * 3 + z) % 7 == 0:
                v.set(x, F, z, pick(pal["base"], rng))
            else:
                v.set(x, F, z, pal["path"])
    cx = cz = 7
    for dx in range(-1, 3):
        for dz in range(-1, 3):
            v.set(cx + dx, F + 1, cz + dz, pick(pal["base"], rng))
    for y in range(F + 2, F + 9):
        v.set(cx, y, cz, pick(pal["tower"], rng)); v.set(cx + 1, y, cz, pick(pal["tower"], rng))
        v.set(cx, y, cz + 1, pick(pal["tower"], rng)); v.set(cx + 1, y, cz + 1, pick(pal["tower"], rng)) if y < F + 4 else None
    if pal["style"] == "elf":
        canopy(v, pal, rng, cx + 0.5, cz + 0.5, 4, 4, F + 8, 3)
    lantern(v, cx, F + 9, cz)
    for dz, fc in ((-4, "south"), (5, "north")):
        for s in range(-1, 3):
            v.set(cx + s, F + 1, cz + dz, stairs(pal, fc))
    for (x, z) in ((1, 1), (14, 1), (1, 14), (14, 14)):
        v.set(x, F + 1, z, pal["stone"]); v.set(x, F + 2, z, "minecraft:campfire[lit=true]")
    v.ent(cx + 3, F + 1, cz + 3, f"{fac}_mystic")


def b_spire(v, pal, rng, fac):
    for x in range(3, 13):
        for z in range(3, 13):
            hgt = max(0, 3 - int(((x - 7.5) ** 2 + (z - 7.5) ** 2) ** 0.5 * 0.55)) + rng.randint(0, 1)
            for y in range(F + 1, F + 1 + hgt):
                v.set(x, y, z, pick(pal["base"], rng))
    b_tower(v, pal, rng, fac, x0=5, z0=5, w=6, d=6, h=18, cap=True)


def b_wall(v, pal, rng, fac):
    for x in range(16):
        for z in (6, 7, 8):
            for y in range(F + 1, F + 7):
                v.set(x, y, z, pick(pal["base"], rng) if y == F + 1 else pick(pal["tower"], rng))
    for x in range(16):
        for z in (6, 8):
            if x % 2 == 0:
                v.set(x, F + 7, z, pick(pal["tower"], rng))
    for x in range(16):
        v.set(x, F + 6, 7, pal["floor"])
    for (xa, xb) in ((0, 3), (12, 15)):
        for x in range(xa, xb + 1):
            for z in range(5, 10):
                for y in range(F + 1, F + 10):
                    if x in (xa, xb) or z in (5, 9):
                        v.set(x, y, z, pick(pal["tower"], rng))
        for x in range(xa, xb + 1):
            for z in range(5, 10):
                if (x + z) % 2 == 0 and (x in (xa, xb) or z in (5, 9)):
                    v.set(x, F + 10, z, pick(pal["tower"], rng))
        if pal.get("tower_cap"):
            pyramid(v, pal, rng, xa, 5, 4, 5, F + 10)
    for x in range(5, 11):
        for y in range(F + 3, F + 6):
            v.set(x, y, 7, "minecraft:iron_bars") if x % 2 == 0 else None
    banner(v, pal, 6, F + 6, 9); banner(v, pal, 10, F + 6, 9)
    lantern(v, 5, F + 7, 7); lantern(v, 10, F + 7, 7)
    v.ent(7, F + 7, 7, f"{fac}_archer"); v.ent(9, F + 7, 7, f"{fac}_warrior")


# ───── cuatro talleres industriales (estilo Create, solo con bloques vanilla) ─────

def _axle(v, x0, x1, y, z, pal):
    for x in range(x0, x1 + 1):
        v.set(x, y, z, "minecraft:stripped_spruce_log[axis=x]")


def b_ws_mill(v, pal, rng, fac):
    x0, z0, w, d, h = 6, 3, 9, 9, 4
    walls(v, pal, rng, x0, z0, w, d, h, windows=False)
    roof(v, pal, rng, x0, z0, w, d, F + h)
    cx, cy, cz = 4, F + 4, 7
    for a in range(0, 360, 30):                 # rueda hidráulica en el plano y-z
        import math
        r = 3
        y = int(round(cy + r * math.sin(math.radians(a)))); z = int(round(cz + r * math.cos(math.radians(a))))
        v.set(cx, y, z, pal["plank"]); v.set(cx + 1, y, z, pal["plank"])
    for k in range(1, 3):
        for (dy, dz) in ((k, 0), (-k, 0), (0, k), (0, -k)):
            v.set(cx, cy + dy, cz + dz, log(pal, "x"))
    v.set(cx, cy, cz, "minecraft:stripped_spruce_log[axis=x]")
    _axle(v, cx + 1, x0, cy, cz, pal)
    for z in range(0, 16):
        v.set(2, F, z, "minecraft:water") if 0 <= z < 16 else None
        v.set(3, F, z, "minecraft:water")
    v.set(10, F + 1, 7, "minecraft:grindstone[face=floor,facing=north]")
    for i in range(3):
        v.set(8 + i, F + 1, 5, "minecraft:hay_block[axis=y]")
    barrel(v, 12, 10)
    v.ent(9, F + 1, 8, f"{fac}_lumberjack")


def b_ws_sawmill(v, pal, rng, fac):
    x0, z0, w, d, h = 1, 3, 14, 10, 4
    for x in (x0, x0 + w - 1, 8):
        for z in (z0, z0 + d - 1):
            for y in range(F + 1, F + h + 1):
                v.set(x, y, z, log(pal))
    v.fill(x0, F, z0, x0 + w - 1, F, z0 + d - 1, pal["base"][0])
    roof(v, pal, rng, x0, z0, w, d, F + h)
    _axle(v, 2, 13, F + 3, 4, pal)
    for x in (4, 9):
        v.set(x, F + 2, 4, "minecraft:iron_trapdoor[facing=south,half=bottom,open=true]")
        v.set(x, F + 1, 4, pal["stone"])
    for x in range(4, 12):
        v.set(x, F + 1, 8, "minecraft:stripped_oak_log[axis=x]")
    for x in (3, 4, 5):
        v.set(x, F + 1, 11, "minecraft:oak_planks"); v.set(x, F + 2, 11, "minecraft:oak_planks")
    for i in range(4):
        v.set(11 + (i % 2), F + 1 + i // 2, 11, "minecraft:oak_log[axis=x]")
    lantern(v, 6, F + h - 1, 6, hanging=True)
    v.ent(7, F + 1, 7, f"{fac}_lumberjack")


def b_ws_press(v, pal, rng, fac):
    x0, z0, w, d, h = 2, 3, 12, 10, 4
    walls(v, pal, rng, x0, z0, w, d, h, open_front=True, windows=False)
    roof(v, pal, rng, x0, z0, w, d, F + h)
    for (x, z) in ((5, 5), (9, 5)):
        for y in range(F + 1, F + 4):
            v.set(x, y, z, "minecraft:iron_block" if y == F + 3 else "minecraft:stripped_spruce_log[axis=y]")
        v.set(x, F + 1, z, "minecraft:anvil[facing=east]") if x == 9 else None
    v.set(5, F + 1, 5, "minecraft:iron_block")
    v.set(7, F + 1, 8, "minecraft:cauldron"); v.set(10, F + 1, 8, "minecraft:hopper[facing=down]")
    barrel(v, 3, 11); barrel(v, 12, 11); chest(v, 7, 11, "north")
    _axle(v, 3, 12, F + 3, 4, pal)
    chimney(v, pal, 13, 4, F + h + 1, 3)
    v.ent(8, F + 1, 7, f"{fac}_smith")


def b_ws_assembler(v, pal, rng, fac):
    x0, z0, w, d, h = 1, 3, 14, 10, 4
    walls(v, pal, rng, x0, z0, w, d, h, open_front=True, windows=False)
    roof(v, pal, rng, x0, z0, w, d, F + h)
    for i in range(5):
        x = 3 + i * 2
        v.set(x, F + 1, 6, "minecraft:chest[facing=south,type=single]")
        v.set(x, F + 3, 6, "minecraft:hopper[facing=down]")
        v.set(x, F + 2, 6, "minecraft:iron_trapdoor[facing=south,half=bottom,open=false]")
    _axle(v, 2, 13, F + 3, 4, pal)
    for x in range(3, 13):
        v.set(x, F + 1, 8, "minecraft:smooth_stone_slab")
    v.set(3, F + 1, 10, "minecraft:crafting_table"); v.set(12, F + 1, 10, "minecraft:smithing_table")
    lantern(v, 7, F + h - 1, 8, hanging=True)
    v.ent(7, F + 1, 9, f"{fac}_mason")


BUILDERS = [
    ("hall", b_hall), ("house_small", b_house_small), ("storehouse", b_storehouse), ("campfire", b_campfire),
    ("house_large", b_house_large), ("workshop", b_workshop), ("well", b_well), ("farm", b_farm),
    ("forge", b_forge), ("barracks", b_barracks), ("tower", b_tower), ("market", b_market),
    ("gate", b_gate), ("guildhall", b_guildhall), ("stable", b_stable), ("watchpost", b_watchpost),
    ("keep", b_keep), ("plaza", b_plaza), ("spire", b_spire), ("wall", b_wall),
]
WORKSHOPS = [("ws_mill", b_ws_mill), ("ws_sawmill", b_ws_sawmill), ("ws_press", b_ws_press), ("ws_assembler", b_ws_assembler)]
