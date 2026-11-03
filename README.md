# Factionlands (Fabric · Minecraft 26.3)

Cinco facciones —**trols, caballeros, elfos, enanos y humanos**— con ocho roles cada una (líder, leñador, albañil,
herrero, guerrero, arquero, explorador y místico): **40 habitantes**. Cada facción genera su **aldea** en el mundo
(20 edificios por facción; los humanos añaden 4 talleres industriales).

## Compilar el `.jar`

Requiere **Java 25**.

```
./gradlew build          # Linux / macOS
gradlew.bat build        # Windows
```

El mod queda en `build/libs/factionlands-0.1.0.jar` (no uses el `-sources.jar`). Va en la carpeta `mods` junto con
**Fabric Loader ≥ 0.20.1** y **Fabric API 0.165.0+26.3**.

Sin Java en local: sube el proyecto a un repositorio de GitHub; el flujo `.github/workflows/build.yml` compila y deja
el `.jar` como artefacto descargable en la pestaña *Actions*.

## Probarlo en el juego

- Pestaña creativa **Factionlands**: una fila por facción (trols, caballeros, elfos, enanos, humanos) con el
  **estandarte de civilización** y los 8 huevos de aparición (líder, leñador, albañil, herrero, guerrero, arquero,
  explorador, místico). Los huevos ya no están en la pestaña vanilla de huevos.
- **Estandarte de civilización**: clic derecho en el suelo y aparece la aldea completa de esa facción (con sus
  habitantes), orientada hacia donde miras. Despeja árboles y colinas en unos 75×110 bloques y rellena los huecos.
  Necesita que el terreno esté cargado (colócate cerca del punto). En supervivencia se gasta; en creativo no.
- Lo mismo por comando (nivel de operador): `/factionlands civilization <troll|knight|elf|dwarf|human>` en tu posición.
- Aldeas: `/place structure factionlands:troll_village` (también `knight_village`, `elf_village`, `dwarf_village`, `human_village`).
- Aparecen solas en biomas afines: trols en pantano y bosque oscuro, caballeros en llanura, elfos en abedulares,
  enanos en montaña y humanos en bosque, llanura, taiga y sabana.
- Los edificios sueltos están en `data/factionlands/structure/<facción>/buildings/*.nbt` (úsalos con bloques de estructura).
- Configuración en `config/factionlands.json`: guerra de trols, trols hostiles al jugador y radio de patrulla.

## Qué es fiel a las láminas y qué no

| Parte | Estado |
|---|---|
| Colores y siluetas de los 40 habitantes | Skins muestreadas píxel a píxel de las láminas (`tools/gen_textures.py`) |
| Proporciones por raza | Tamaño por atributo `SCALE`: trol 1.30, caballero 1.05, elfo 0.95, enano 0.85, humano 1.00 |
| Modelo 3D | **Humanoide vanilla**: sin cuernos, capas ni armas esculpidas en 3D; las armas son ítems vanilla aproximados |
| Edificios | Aproximaciones procedurales con la paleta de cada facción (`tools/builders.py`), no copias bloque a bloque |
| Talleres con engranajes | Estáticos |
| Comportamiento | Combate, arqueros, curación del místico, ayuda entre aliados, trols vs. resto. **Los trabajos de leñador/albañil/herrero no están implementados** |

Para acercarte al 100%: modelos propios en Blockbench (una `ModelLayerRegistry` por raza) y reconstruir los edificios
a mano sobre estos como base.

## Regenerar texturas y estructuras

Copia las láminas en `tools/reference/` con estos nombres: `chars_{troll,knight,elf,dwarf,human}.png` y
`buildings_{…}.png`. Después:

```
pip install pillow nbtlib numpy
python3 -I tools/gen_textures.py     # 40 skins
python3 -I tools/gen_structures.py   # 109 plantillas NBT + datos de worldgen
python3 -I tools/gen_data.py         # lang y definiciones de los huevos
python3 -I tools/preview_structures.py --validate
```

## Si el primer build da errores

Este código se escribió contra la API de 26.3 **sin poder compilarlo** (el entorno donde se creó no llega a los
repositorios Maven). Las firmas se contrastaron con la documentación de Fabric 26.2 y las guías de migración de
NeoForge, pero estos son los puntos que más probablemente necesiten un retoque:

1. `FactionRenderer` — genéricos de `HumanoidMobRenderer` y ruta de `HumanoidRenderState`.
2. `FactionEntity` — `setHomeTo`, `EntityType.ARROW.create(level, EntitySpawnReason)`, `player.sendSystemMessage`,
   la lambda `(target, level) ->` de `NearestAttackableTargetGoal` y `getHurtSound`/`getDeathSound`.
3. `worldgen/structure/*.json` — `max_distance_from_center` (en 1.21.9 pasó a poder ser `{horizontal, vertical}`).
4. Las plantillas NBT llevan `DataVersion` de 1.21.1 (3955): el juego las actualiza al cargar con el DataFixer.

Pega el error de Gradle y se corrige en el sitio.
