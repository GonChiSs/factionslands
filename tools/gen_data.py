"""Genera lang (en/es) y las definiciones de ítem de los huevos de aparición (26.x: assets/<ns>/items/*.json).
uso: python3 -I tools/gen_data.py"""
import os, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "src/main/resources/assets/factionlands")
FACTIONS = ["troll", "knight", "elf", "dwarf", "human"]
ROLES = ["leader", "lumberjack", "mason", "smith", "warrior", "archer", "scout", "mystic"]

# colores del huevo (RGB): (fondo, manchas) — tomados de la paleta de cada lámina
EGG = dict(troll=(0x6F8A5E, 0x8A5A2E), knight=(0x2F4FA8, 0xC9C9CF), elf=(0x4E7A32, 0xEDE4C8),
           dwarf=(0xC9531C, 0x3C3C44), human=(0x9C3B2F, 0xD9C7A3))

EN_F = dict(troll="Troll", knight="Knight", elf="Elf", dwarf="Dwarf", human="Human")
ES_F = dict(troll="trol", knight="caballero", elf="elfo", dwarf="enano", human="humano")
EN_R = dict(leader="Leader", lumberjack="Lumberjack", mason="Mason", smith="Smith", warrior="Warrior",
            archer="Archer", scout="Scout", mystic="Mystic")
ES_R = dict(leader="Líder", lumberjack="Leñador", mason="Albañil", smith="Herrero", warrior="Guerrero",
            archer="Arquero", scout="Explorador", mystic="Místico")
EN_D = dict(leader="Our people will endure.", lumberjack="Timber doesn't fell itself.", mason="Stone remembers everything.",
            smith="The forge never sleeps.", warrior="Stay behind me.", archer="I have my eye on the treeline.",
            scout="The road ahead is quiet... for now.", mystic="Let me tend to those wounds.")
ES_D = dict(leader="Nuestro pueblo perdurará.", lumberjack="La madera no se tala sola.", mason="La piedra lo recuerda todo.",
            smith="La forja nunca duerme.", warrior="Quédate detrás de mí.", archer="Vigilo la linde del bosque.",
            scout="El camino está tranquilo... por ahora.", mystic="Déjame curar esas heridas.")


ES_P = dict(troll="trols", knight="caballeros", elf="elfos", dwarf="enanos", human="humanos")


def lang(en):
    F, R, D = (EN_F, EN_R, EN_D) if en else (ES_F, ES_R, ES_D)
    out = {"dialog.factionlands.chat": "<%s> %s"}
    for f in FACTIONS:
        for r in ROLES:
            name = f"{F[f]} {R[r]}" if en else f"{R[r]} {F[f]}"
            out[f"entity.factionlands.{f}_{r}"] = name
            out[f"item.factionlands.{f}_{r}_spawn_egg"] = name + (" Spawn Egg" if en else " (huevo de aparición)")
    for r in ROLES:
        out[f"dialog.factionlands.{r}"] = D[r]
    # pestaña creativa, estandartes de civilización y mensajes
    out["itemGroup.factionlands.main"] = "Factionlands"
    for f in FACTIONS:
        out[f"item.factionlands.{f}_civilization"] = f"{EN_F[f]} Civilization" if en else f"Civilización de {ES_P[f]}"
    if en:
        out["item.factionlands.civilization.tooltip"] = "Right-click the ground to found a full village."
        out["item.factionlands.civilization.tooltip2"] = "Levels about 75x110 blocks and faces the way you look."
        out["message.factionlands.civilization_founded"] = "%s founded!"
        out["message.factionlands.civilization_unloaded"] = "Part of the area isn't loaded yet. Stand closer to the spot and try again."
        out["message.factionlands.civilization_height"] = "Not enough vertical space here."
        out["message.factionlands.civilization_missing"] = "Village template not found."
    else:
        out["item.factionlands.civilization.tooltip"] = "Clic derecho en el suelo para fundar una aldea completa."
        out["item.factionlands.civilization.tooltip2"] = "Aplana unos 75x110 bloques y mira hacia donde miras."
        out["message.factionlands.civilization_founded"] = "¡%s fundada!"
        out["message.factionlands.civilization_unloaded"] = "Parte de la zona aún no está cargada. Acércate al lugar e inténtalo de nuevo."
        out["message.factionlands.civilization_height"] = "No hay altura suficiente aquí."
        out["message.factionlands.civilization_missing"] = "No se encontró la plantilla de la aldea."
    return out


os.makedirs(os.path.join(ASSETS, "lang"), exist_ok=True)
for name, en in (("en_us", True), ("es_es", False)):
    with open(os.path.join(ASSETS, "lang", name + ".json"), "w", encoding="utf-8") as fh:
        json.dump(lang(en), fh, indent=2, ensure_ascii=False)

idir = os.path.join(ASSETS, "items")
os.makedirs(idir, exist_ok=True)
for f in FACTIONS:
    for r in ROLES:
        c0, c1 = EGG[f]
        with open(os.path.join(idir, f"{f}_{r}_spawn_egg.json"), "w") as fh:
            json.dump({"model": {"type": "minecraft:model", "model": "minecraft:item/template_spawn_egg",
                                 "tints": [{"type": "minecraft:constant", "value": c0},
                                           {"type": "minecraft:constant", "value": c1}]}}, fh, indent=2)
mdir = os.path.join(ASSETS, "models", "item")
os.makedirs(mdir, exist_ok=True)
for f in FACTIONS:   # estandartes de civilización: definición de ítem + modelo plano con su icono
    with open(os.path.join(idir, f"{f}_civilization.json"), "w") as fh:
        json.dump({"model": {"type": "minecraft:model", "model": f"factionlands:item/{f}_civilization"}}, fh, indent=2)
    with open(os.path.join(mdir, f"{f}_civilization.json"), "w") as fh:
        json.dump({"parent": "minecraft:item/generated", "textures": {"layer0": f"factionlands:item/{f}_civilization"}}, fh, indent=2)
print("lang + items escritos")
