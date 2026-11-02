#!/usr/bin/env bash
# Prueba de humo en servidor real: arranca Minecraft 26.3 + el mod con ./gradlew runServer,
# invoca los 40 mobs, carga las 109 plantillas .nbt, genera las 5 aldeas y deja pelear a unos cuantos.
# Escribe run/server.log y un resumen; sale con código != 0 si algo falla.
set -u
cd "$(dirname "$0")/.."
FACTIONS="troll knight elf dwarf human"
ROLES="leader lumberjack mason smith warrior archer scout mystic"
LOG=run/server.log
rm -rf run && mkdir -p run
echo "eula=true" > run/eula.txt
cat > run/server.properties <<'EOP'
online-mode=false
level-type=minecraft\:flat
generator-settings={"biome":"minecraft:plains","layers":[{"block":"minecraft:bedrock","height":1},{"block":"minecraft:dirt","height":2},{"block":"minecraft:grass_block","height":1}],"structure_overrides":[]}
spawn-protection=0
view-distance=6
simulation-distance=6
pause-when-empty-seconds=-1
difficulty=normal
EOP

rm -f run/in && mkfifo run/in
exec 3<>run/in                      # mantiene la tubería abierta para escribir comandos
./gradlew runServer --no-daemon < run/in > "$LOG" 2>&1 &
GPID=$!

for i in $(seq 1 120); do            # espera a "Done (x s)!" (máx. 10 min)
  grep -q 'Done (' "$LOG" && break
  kill -0 $GPID 2>/dev/null || break
  sleep 5
done
if ! grep -q 'Done (' "$LOG"; then
  echo "!! el servidor no llegó a arrancar"; tail -n 80 "$LOG"; exit 2
fi
echo "servidor arrancado"

send() { echo "$1" >&3; sleep 0.25; }
send "forceload add 0 0 48 48"
sleep 3
for f in $FACTIONS; do for r in $ROLES; do send "summon factionlands:${f}_${r} 8 -60 8"; done; done
send "say ==PLANTILLAS=="
send "forceload add 336 336 464 464"; sleep 10
for f in $FACTIONS; do
  send "place template factionlands:${f}/village 400 -60 400"
  for p in src/main/resources/data/factionlands/structure/$f/buildings/*.nbt; do
    n=$(basename "$p" .nbt); send "place template factionlands:${f}/buildings/${n} 400 -60 400"
  done
done
send "say ==ALDEAS=="
i=0; for f in $FACTIONS; do i=$((i+1)); x=$((i*300))
  send "forceload add $((x-90)) -390 $((x+90)) -210"; sleep 8
  send "place structure factionlands:${f}_village $x -60 -300"; sleep 5
  send "execute positioned $x -60 -300 if entity @e[type=factionlands:${f}_leader,distance=..130]"
  send "execute positioned $x -60 -300 as @e[type=factionlands:${f}_warrior,distance=..130,limit=1] run data get entity @s equipment"
done
send "say ==COMBATE=="
send "summon factionlands:troll_warrior 24 -60 24"
send "summon factionlands:human_archer 30 -60 24"
send "summon factionlands:knight_warrior 27 -60 30"
send "summon factionlands:elf_mystic 28 -60 26"
sleep 20
send "execute if entity @e[type=factionlands:human_archer]"
send "execute if entity @e[type=factionlands:troll_warrior]"
send "say ==FIN=="
sleep 3
send "stop"
for i in $(seq 1 24); do kill -0 $GPID 2>/dev/null || break; sleep 5; done
kill $GPID 2>/dev/null; exec 3>&-

echo "================ RESUMEN ================"
echo "Summoned:        $(grep -c 'Summoned new' "$LOG") (esperado 44)"
echo "Plantillas:      $(grep -c 'Loaded template' "$LOG") (esperado 109)"
echo "Aldeas:          $(grep -c 'Generated structure' "$LOG") (esperado 5)"
echo "---- líneas sospechosas:"
grep -E "ERROR|Exception|Unable|Failed|Unknown|Invalid|Incorrect|Expected|Couldn't|Could not|crash|Missing|No such|\bat com\.factionlands" "$LOG" | grep -v "Stopping" | cut -c1-260 | sort | uniq -c | sort -rn | head -50
echo "---- respuestas a los comandos (agrupadas):"
grep -E "System chat|\[Server\]" "$LOG" | sed -E 's/^\[[0-9:]+\] \[[^]]*\] \(Minecraft\) //' | sort | uniq -c | sort -rn | cut -c1-200 | head -40
echo "---- respuestas de combate:"
sed -n '/==COMBATE==/,/==FIN==/p' "$LOG" | cut -c1-200 | tail -n 12
echo "::group::server.log desde el arranque"; sed -n '/Done (/,$p' "$LOG" | cut -c1-220 | head -500; echo "::endgroup::"
S=$(grep -c 'Summoned new' "$LOG"); T=$(grep -c 'Loaded template' "$LOG"); A=$(grep -c 'Generated structure' "$LOG")
[ "$S" -ge 44 ] && [ "$T" -ge 109 ] && [ "$A" -ge 5 ] && ! grep -qE "Exception|crash report|Encountered an unexpected exception" "$LOG"
