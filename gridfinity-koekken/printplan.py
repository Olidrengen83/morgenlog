#!/usr/bin/env python3
"""Samler alle dele til skuffe 1 (undtagen den allerede printede bestik-lang-a) i én 3MF.
Bambu Studio arrangerer dem selv paa plader (Arrange / Auto-arrange)."""
import os
import trimesh
HERE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(HERE, "stl"); OUT = os.path.join(STL, "print"); os.makedirs(OUT, exist_ok=True)

DELE = ["skuffe1-bestik__knivbakke-a", "skuffe1-bestik__knivbakke-b",
        "skuffe1-bestik__redskaber-a", "skuffe1-bestik__redskaber-b",
        "skuffe1-bestik__bestik-kort", "skuffe1-bestik__bestik-lang-b",
        "indsats__kanal-a", "indsats__kanal-b"]
UDELADT = "skuffe1-bestik__bestik-lang-a (identisk med testbakken, allerede printet)"

scene = trimesh.Scene(); x = 0.0; vol = 0.0
for n in DELE:
    m = trimesh.load(os.path.join(STL, n + ".stl"))
    m.apply_translation(-m.bounds[0]); m.apply_translation([x, 0, 0])
    scene.add_geometry(m, node_name=n, geom_name=n)
    x += m.extents[0] + 5; vol += m.volume / 1000
path = os.path.join(OUT, "skuffe1-bestik-alle-dele.3mf")
scene.export(path)
with open(os.path.join(HERE, "printplan.md"), "w") as f:
    f.write("# Printplan, skuffe 1 (bestik)\n\n"
            f"Alle dele ligger i én fil: `stl/print/skuffe1-bestik-alle-dele.3mf` ({len(DELE)} dele, {vol:.0f} cm³ massivt regnet).\n\n"
            "1. Importér filen i Bambu Studio (P1S, 256 × 256 mm).\n"
            "2. Tryk Arrange (A) med lille afstand (2–3 mm), så fordeler den delene på plader. Det kan lade sig gøre på 4 plader:\n"
            "   bestik-kort alene · knivbakke-a + redskaber-a · knivbakke-b + redskaber-b · bestik-lang-b + kanal-a + kanal-b.\n"
            "3. Forslag: 0,2 mm lag, 3 vægge, 15 % infill, ingen støtte, ingen brim.\n\n"
            f"Udeladt: {UDELADT}.\n")
print("skrev", path, "og printplan.md;", len(DELE), "dele")
