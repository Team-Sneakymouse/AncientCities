#!/usr/bin/env python3
"""Build Overworld dimension + world presets: deep_dark everywhere at depth 1.1."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VANILLA_PARAMS = (
    ROOT
    / "tools"
    / "generated-reports-1.21.4"
    / "reports"
    / "biome_parameters"
    / "minecraft"
    / "overworld.json"
)
DATA = ROOT / "data" / "minecraft"
DEEP_DEPTH = 1.1

VANILLA_PRESETS = {
    "normal": ROOT / "tools/generated-1.21.4/data/minecraft/worldgen/world_preset/normal.json",
    "large_biomes": ROOT
    / "tools/generated-1.21.4/data/minecraft/worldgen/world_preset/large_biomes.json",
    "amplified": ROOT / "tools/generated-1.21.4/data/minecraft/worldgen/world_preset/amplified.json",
}


def is_surface_depth(depth) -> bool:
    return depth == 0.0 or depth == 0


def build_biomes() -> list:
    with VANILLA_PARAMS.open() as f:
        vanilla = json.load(f)

    biomes = []
    surface_twins = []
    removed_deep_dark = 0

    for entry in vanilla["biomes"]:
        biome = entry["biome"]
        params = entry["parameters"]
        depth = params["depth"]

        if biome == "minecraft:deep_dark":
            removed_deep_dark += 1
            continue

        biomes.append(entry)

        if is_surface_depth(depth):
            twin_params = dict(params)
            twin_params["depth"] = DEEP_DEPTH
            surface_twins.append(
                {
                    "biome": "minecraft:deep_dark",
                    "parameters": twin_params,
                }
            )

    biomes.extend(surface_twins)
    print(f"  kept vanilla points (minus deep_dark): {len(biomes) - len(surface_twins)}")
    print(f"  removed vanilla deep_dark points: {removed_deep_dark}")
    print(f"  added deep_dark twins at depth {DEEP_DEPTH}: {len(surface_twins)}")
    print(f"  total biome points: {len(biomes)}")
    return biomes


def overworld_generator(biomes: list) -> dict:
    return {
        "type": "minecraft:noise",
        "settings": "minecraft:overworld",
        "biome_source": {
            "type": "minecraft:multi_noise",
            "biomes": biomes,
        },
    }


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"Wrote {path}")


def main() -> None:
    print("Building biome list...")
    biomes = build_biomes()
    ow_gen = overworld_generator(biomes)

    write_json(
        DATA / "dimension" / "overworld.json",
        {
            "type": "minecraft:overworld",
            "generator": ow_gen,
        },
    )

    for name, vanilla_path in VANILLA_PRESETS.items():
        with vanilla_path.open() as f:
            preset = json.load(f)
        preset["dimensions"]["minecraft:overworld"] = {
            "type": "minecraft:overworld",
            "generator": ow_gen,
        }
        write_json(DATA / "worldgen" / "world_preset" / f"{name}.json", preset)


if __name__ == "__main__":
    main()
