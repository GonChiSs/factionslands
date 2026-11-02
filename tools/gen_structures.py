"""Genera, para cada facción: 20 edificios (+4 talleres para humanos) como plantillas NBT,
un pueblo compuesto con todos ellos y los datos de worldgen (jigsaw, structure_set, tags de bioma).

uso: python3 -I tools/gen_structures.py
"""
import os, sys, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import builders as B
from builders import Vol, F, CELL, HEIGHT, BUILDERS, WORKSHOPS
import nbtw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "src/main/resources/data/factionlands")
MOD = "factionlands"

W = lambda c: f"minecraft:{c}"
PAL = {
    "troll": dict(
        style="troll", ground=W("grass_block"), path=W("mossy_cobblestone"), lane=W("coarse_dirt"),
        base=[W("mossy_stone_bricks"), W("mossy_cobblestone"), W("stone_bricks")],
        wall=[W("mossy_stone_bricks"), W("mossy_cobblestone"), W("dark_oak_planks")],
        frame=W("dark_oak_log"), plank=W("dark_oak_planks"), floor=W("dark_oak_planks"),
        roof=W("moss_block"), eave=W("dark_oak_planks"), roof2=None,
        roof_deco=[W("oak_leaves[persistent=true]"), W("moss_carpet"), W("fern")],
        glass=W("iron_bars"), door=W("dark_oak_door"), fence=W("dark_oak_fence"), gate=W("dark_oak_fence_gate"),
        slab=W("dark_oak_slab"), stair=W("dark_oak_stairs"), step=W("mossy_cobblestone"), stone=W("mossy_cobblestone"),
        chimney=W("mossy_stone_bricks"), crate=W("barrel[facing=up]"),
        banner=[W("green_wool"), W("green_wool")], awning=[W("brown_wool"), W("green_wool")],
        tower=[W("mossy_stone_bricks"), W("mossy_cobblestone"), W("stone_bricks"), W("cobblestone")], tower_cap=False,
        flora=[W("fern"), W("short_grass"), W("short_grass"), W("oak_leaves[persistent=true]")],
        leaves=[W("oak_leaves[persistent=true]")]),
    "knight": dict(
        style="knight", ground=W("grass_block"), path=W("cobblestone"), lane=W("cobblestone"),
        base=[W("stone_bricks"), W("stone_bricks"), W("cobblestone")],
        wall=[W("stone_bricks"), W("stone_bricks"), W("cracked_stone_bricks")],
        frame=W("dark_oak_log"), plank=W("spruce_planks"), floor=W("spruce_planks"),
        roof=W("blue_wool"), eave=W("stone_bricks"), roof2=None, roof_deco=None,
        glass=W("glass_pane"), door=W("spruce_door"), fence=W("dark_oak_fence"), gate=W("dark_oak_fence_gate"),
        slab=W("spruce_slab"), stair=W("spruce_stairs"), step=W("stone_bricks"), stone=W("stone_bricks"),
        chimney=W("stone_bricks"), crate=W("barrel[facing=up]"),
        banner=[W("blue_wool"), W("white_wool")], awning=[W("blue_wool"), W("white_wool")],
        tower=[W("stone_bricks"), W("stone_bricks"), W("cracked_stone_bricks"), W("mossy_stone_bricks")], tower_cap=True,
        flora=[W("short_grass"), W("cornflower"), W("lily_of_the_valley"), W("short_grass")],
        leaves=[W("oak_leaves[persistent=true]")]),
    "elf": dict(
        style="elf", ground=W("grass_block"), path=W("dirt_path"), lane=W("dirt_path"),
        base=[W("birch_planks"), W("stripped_birch_log[axis=y]")],
        wall=[W("birch_planks"), W("birch_planks"), W("stripped_birch_log[axis=y]")],
        frame=W("birch_log"), plank=W("birch_planks"), floor=W("birch_planks"),
        roof=W("birch_planks"), eave=None, roof2=None, roof_deco=None,
        glass=W("glass_pane"), door=W("birch_door"), fence=W("birch_fence"), gate=W("birch_fence_gate"),
        slab=W("birch_slab"), stair=W("birch_stairs"), step=W("birch_planks"), stone=W("mossy_cobblestone"),
        chimney=W("mossy_stone_bricks"), crate=W("barrel[facing=up]"),
        banner=[W("green_wool"), W("white_wool")], awning=[W("orange_wool"), W("yellow_wool"), W("red_wool")],
        tower=[W("birch_log[axis=y]"), W("birch_planks"), W("stripped_birch_log[axis=y]")], tower_cap=False,
        flora=[W("fern"), W("short_grass"), W("orange_tulip"), W("red_tulip"), W("azure_bluet")],
        leaves=[W("red_wool"), W("orange_wool"), W("yellow_wool"), W("orange_wool")]),
    "dwarf": dict(
        style="dwarf", ground=W("grass_block"), path=W("polished_andesite"), lane=W("cobblestone"),
        base=[W("deepslate_bricks"), W("polished_blackstone_bricks"), W("cracked_deepslate_bricks")],
        wall=[W("deepslate_bricks"), W("polished_deepslate"), W("deepslate_tiles")],
        frame=W("spruce_log"), plank=W("spruce_planks"), floor=W("spruce_planks"),
        roof=W("deepslate_tiles"), eave=W("oxidized_cut_copper"), roof2=W("cut_copper"), roof_deco=None,
        glass=W("glass_pane"), door=W("spruce_door"), fence=W("spruce_fence"), gate=W("spruce_fence_gate"),
        slab=W("spruce_slab"), stair=W("spruce_stairs"), step=W("deepslate_bricks"), stone=W("deepslate_bricks"),
        chimney=W("deepslate_bricks"), crate=W("barrel[facing=up]"),
        banner=[W("orange_wool"), W("orange_wool")], awning=[W("orange_terracotta"), W("oxidized_cut_copper")],
        tower=[W("deepslate_bricks")] * 6 + [W("polished_blackstone_bricks")] * 2 + [W("cut_copper")], tower_cap=True,
        flora=[W("short_grass"), W("fern")], leaves=[W("oak_leaves[persistent=true]")]),
    "human": dict(
        style="human", ground=W("grass_block"), path=W("dirt_path"), lane=W("dirt_path"),
        base=[W("cobblestone"), W("stone_bricks"), W("mossy_cobblestone")],
        wall=[W("smooth_quartz")],
        frame=W("dark_oak_log"), plank=W("spruce_planks"), floor=W("spruce_planks"),
        roof=W("bricks"), eave=None, roof2=W("red_terracotta"), roof_deco=None,
        glass=W("glass_pane"), door=W("spruce_door"), fence=W("dark_oak_fence"), gate=W("dark_oak_fence_gate"),
        slab=W("spruce_slab"), stair=W("spruce_stairs"), step=W("cobblestone"), stone=W("cobblestone"),
        chimney=W("cobblestone"), crate=W("barrel[facing=up]"),
        banner=[W("white_wool"), W("red_wool")], awning=[W("white_wool"), W("red_wool")],
        tower=[W("stone_bricks"), W("cobblestone"), W("stone_bricks")], tower_cap=False,
        flora=[W("short_grass"), W("poppy"), W("dandelion"), W("short_grass"), W("oxeye_daisy")],
        leaves=[W("oak_leaves[persistent=true]")]),
}

# disposición del pueblo (4 columnas); orden de lectura de izquierda a derecha, de norte a sur
LAYOUT = [
    ["spire", "gate", "wall", "watchpost"],
    ["stable", "farm", "storehouse", "market"],
    ["house_large", "hall", "plaza", "house_small"],
    ["workshop", "forge", "campfire", "well"],
    ["barracks", "tower", "keep", "guildhall"],
]
LAYOUT_WORKSHOPS = ["ws_mill", "ws_sawmill", "ws_press", "ws_assembler"]

BIOMES = {
    "troll": ["minecraft:swamp", "minecraft:mangrove_swamp", "minecraft:dark_forest"],
    "knight": ["minecraft:plains", "minecraft:meadow", "minecraft:sunflower_plains"],
    "elf": ["minecraft:birch_forest", "minecraft:old_growth_birch_forest", "minecraft:flower_forest"],
    "dwarf": ["minecraft:grove", "minecraft:snowy_slopes", "minecraft:windswept_hills", "minecraft:windswept_forest", "minecraft:stony_peaks"],
    "human": ["minecraft:forest", "minecraft:plains", "minecraft:taiga", "minecraft:savanna"],
}
SALTS = {"troll": 1160227, "knight": 2271883, "elf": 3350591, "dwarf": 4463021, "human": 5578907}


def jwrite(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=2)


def max_y(v):
    return max((y for (_, y, _) in v.b), default=F)


def make_building(fac, name, fn):
    pal = PAL[fac]
    rng = random.Random(f"{fac}-{name}")
    v = Vol()
    B.ground(v, pal, rng)
    fn(v, pal, rng, fac)
    B.scatter(v, pal, rng)
    return v


def clear_air(v, ytop):
    for x in range(v.sx):
        for z in range(v.sz):
            for y in range(F + 1, ytop + 1):
                if (x, y, z) not in v.b:
                    v.b[(x, y, z)] = "minecraft:air"


def write_nbt(path, v, size=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    size = size or (v.sx, v.sy, v.sz)
    with open(path, "wb") as fh:
        fh.write(nbtw.structure_nbt(size, v.b, v.ents))


def main():
    stats = {}
    for fac in PAL:
        pal = PAL[fac]
        built = {}
        todo = list(BUILDERS) + (list(WORKSHOPS) if fac == "human" else [])
        for name, fn in todo:
            v = make_building(fac, name, fn)
            top = max([max_y(v)] + [e[1] + 2 for e in v.ents]) + 1
            clear_air(v, top)
            sizey = top + 1
            v.sy = sizey
            write_nbt(os.path.join(DATA, "structure", fac, "buildings", f"{name}.nbt"), v, (CELL, sizey, CELL))
            built[name] = (v, top)

        # ── pueblo compuesto ──
        rows = [r[:] for r in LAYOUT] + ([LAYOUT_WORKSHOPS[:]] if fac == "human" else [])
        cols, nrows, M, P = 4, len(rows), 2, CELL + 2
        sx, sz = M * 2 + cols * P - 2, M * 2 + nrows * P - 2
        sy = max(t for (_, t) in built.values()) + 2
        town = Vol(sx, sy, sz)
        rng = random.Random(f"{fac}-village")
        town.fill(0, 0, 0, sx - 1, 1, sz - 1, "minecraft:dirt")
        town.fill(0, F, 0, sx - 1, F, sz - 1, pal["lane"])
        town.fill(0, F + 1, 0, sx - 1, F + 4, sz - 1, "minecraft:air")
        for r, row in enumerate(rows):
            for c, name in enumerate(row):
                v, top = built[name]
                ox, oz = M + c * P, M + r * P
                for (x, y, z), st in v.b.items():
                    town.set(ox + x, y, oz + z, st)
                for (x, y, z, eid, rot) in v.ents:
                    town.ents.append((ox + x, y, oz + z, eid, rot))
        for r in range(nrows):
            for c in range(cols):
                B.lamp_post(town, pal, M + c * P + CELL, M + r * P + CELL, 3)
        write_nbt(os.path.join(DATA, "structure", fac, "village.nbt"), town)
        stats[fac] = dict(buildings=len(built), size=(sx, sy, sz), blocks=len(town.b), entities=len(town.ents))

        # ── worldgen ──
        jwrite(os.path.join(DATA, "worldgen/template_pool", fac, "start.json"), {
            "fallback": "minecraft:empty",
            "elements": [{"weight": 1, "element": {
                "element_type": "minecraft:single_pool_element",
                "location": f"{MOD}:{fac}/village", "processors": "minecraft:empty", "projection": "rigid"}}]})
        jwrite(os.path.join(DATA, "worldgen/structure", f"{fac}_village.json"), {
            "type": "minecraft:jigsaw",
            "biomes": f"#{MOD}:has_structure/{fac}_village",
            "step": "surface_structures",
            "spawn_overrides": {},
            "terrain_adaptation": "beard_thin",
            "start_pool": f"{MOD}:{fac}/start",
            "size": 1,
            "start_height": {"absolute": -3},
            "project_start_to_heightmap": "WORLD_SURFACE_WG",
            "max_distance_from_center": 80,
            "use_expansion_hack": False})
        jwrite(os.path.join(DATA, "worldgen/structure_set", f"{fac}_village.json"), {
            "structures": [{"structure": f"{MOD}:{fac}_village", "weight": 1}],
            "placement": {"type": "minecraft:random_spread", "spacing": 36, "separation": 14, "salt": SALTS[fac]}})
        jwrite(os.path.join(DATA, "tags/worldgen/biome/has_structure", f"{fac}_village.json"),
               {"replace": False, "values": BIOMES[fac]})
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
