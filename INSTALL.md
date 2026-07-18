# Deep Dark Everywhere (Minecraft 1.21.4)

Continuous Deep Dark at the vanilla deep layer (`depth` 1.1), with ancient cities dense enough that they often touch. Surface and mid-depth caves (lush / dripstone) stay vanilla.

## Install

1. Use **Java Edition 1.21.4**.
2. Create a **new world** (worldgen only applies to chunks generated with the pack).
3. On the world creation screen, open **Data Packs**, add this folder (or a zip of it), and move it to **Selected**.
4. Cycle world types once back to **Default** if the Overworld override does not apply on first try (known vanilla quirk).
5. Create the world.

Existing worlds: only newly generated chunks are affected.

## What it changes

| File | Effect |
|------|--------|
| `data/minecraft/dimension/overworld.json` | Replaces hardcoded Overworld multi-noise preset with an explicit list: every surface climate point is twinned at depth `1.1` as `minecraft:deep_dark`. |
| `data/minecraft/worldgen/structure_set/ancient_cities.json` | `spacing` 12 / `separation` 2 (vanilla was 24 / 8). |

Ancient cities still generate at their vanilla height (start Y −27 / floor ~−51).

## In-game checks

After a **server restart** (required when the zip changes):

```
/datapack list
/locate structure minecraft:ancient_city
/locate biome minecraft:deep_dark
```

Cities generate around **Y −51** on a ~10-chunk grid. **Already-generated chunks will not change** — teleport thousands of blocks into unexplored terrain (or wipe `world/region`) before judging.

On an existing Paper world, the continuous deep-dark *biome* override may not apply until you create a new world; city placement (structure set + biome tag) still works in new chunks.

## Rebuild Overworld biomes (optional)

Requires the 1.21.4 biome-parameter dump under `tools/`:

```bash
# Download server jar + run reports (once)
cd tools
curl -L -o server-1.21.4.jar "https://piston-data.mojang.com/v1/objects/4707d00eb834b446575d89a61a11b5d548d8c001/server.jar"
java -DbundlerMainClass=net.minecraft.data.Main -jar server-1.21.4.jar --reports --output generated-reports-1.21.4

# Rebuild dimension JSON
cd ..
python3 tools/build_overworld_dimension.py
```

## Performance

Dense cities are generation-heavy. If chunk gen stutters, raise `spacing` in `ancient_cities.json` (e.g. to `14`) while keeping low `separation`.

## Deploy to sandbox

Copy `.env.example` → `.env` (gitignored) and run:

```bash
./tools/deploy.sh
```

That zips the pack into `dist/DeepDarkEverywhere.zip` and uploads it via SFTP to `DEPLOY_REMOTE_PATH` on the sandbox. Use the OpenSSH key path in `.env` (not the `.ppk`); a converted sibling lives next to the PuTTY key.
