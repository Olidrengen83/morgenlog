#!/usr/bin/env python3
"""Printplan for skuffe 1 paa Bambu P1S (256 x 256 mm, udelukkelseszone forrest tv. ca. 18 x 28 mm).
Skriver én 3MF pr. plade med delene placeret uden om zonen, plus én fil med alle dele."""
import os
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(HERE, "stl"); OUT = os.path.join(STL, "print"); os.makedirs(OUT, exist_ok=True)
BED = 256.0

def part(name, x, y, rot=0):
    """Placerer delens nederste venstre hjoerne i (x, y) paa pladen; rot=90 drejer den om z."""
    m = trimesh.load(os.path.join(STL, name + ".stl"))
    if rot:
        m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(rot), [0, 0, 1]))
    m.apply_translation(-m.bounds[0]); m.apply_translation([x, y, 0])
    assert m.bounds[1][0] <= BED and m.bounds[1][1] <= BED, f"{name} udenfor pladen: {m.bounds[1][:2]}"
    assert not (m.bounds[0][0] < 18 and m.bounds[0][1] < 28), f"{name} rammer udelukkelseszonen"
    return name, m

PLADER = {
    "skuffe1-plade-1": [part("skuffe1-bestik__knivbakke-a", 86, 2), part("skuffe1-bestik__redskaber-a", 1, 86)],
    "skuffe1-plade-2": [part("skuffe1-bestik__knivbakke-b", 86, 2), part("skuffe1-bestik__redskaber-b", 1, 86)],
    "skuffe1-plade-3": [part("skuffe1-bestik__bestik-kort-a", 2, 129), part("skuffe1-bestik__redskaber-c", 20, 32, rot=90)],
    "skuffe1-plade-4": [part("skuffe1-bestik__bestik-kort-b", 2, 129)],
    "skuffe1-plade-5": [part("skuffe1-bestik__bestik-lang-b", 128, 2), part("indsats__kanal-a", 22, 2), part("indsats__kanal-b", 46, 2)],
}
UDELADT = "bestik-lang-a (identisk med testbakken, allerede printet)"

alle = trimesh.Scene(); rows = []
for plade, parts in PLADER.items():
    sc = trimesh.Scene()
    for n, m in parts:
        sc.add_geometry(m, node_name=n, geom_name=n); alle.add_geometry(m.copy(), node_name=n, geom_name=n)
    sc.export(os.path.join(OUT, plade + ".3mf"))
    rows.append((plade, [n.split("__")[1] for n, _ in parts], sum(m.volume for _, m in parts) / 1000))
    print(plade, rows[-1][1])
alle.export(os.path.join(OUT, "skuffe1-bestik-alle-dele.3mf"))

with open(os.path.join(HERE, "printplan.md"), "w") as f:
    f.write("# Printplan, skuffe 1 (bestik)\n\nBambu P1S. Delene er placeret uden om udelukkelseszonen forrest til venstre, "
            "så filerne kan slices direkte. Forslag: 0,2 mm lag, 3 vægge, 15 % infill, ingen støtte, ingen brim.\n\n"
            "| Plade | Dele | Volumen (massivt) |\n|---|---|---|\n")
    for plade, names, vol in rows:
        f.write(f"| `stl/print/{plade}.3mf` | {', '.join(names)} | {vol:.0f} cm³ |\n")
    f.write(f"\n`stl/print/skuffe1-bestik-alle-dele.3mf` har alle {sum(len(p) for p in PLADER.values())} dele i én fil, "
            "hvis du hellere vil arrangere selv.\n\n"
            f"**Udeladt:** {UDELADT}.\n\n"
            "Fem plader er minimum: zonen gør, at ingen del kan være over ca. 238 mm i begge retninger, og to 6×3-bakker "
            "kan ikke dele plade uden at den forreste rammer zonen.\n")
print("skrev", OUT, "og printplan.md")
