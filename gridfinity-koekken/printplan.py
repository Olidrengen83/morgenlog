#!/usr/bin/env python3
"""Printplan for skuffe 1 paa Bambu P1S (256 x 256 mm, udelukkelseszone forrest tv. ca. 18 x 28 mm).
Skriver én 3MF pr. plade med delene placeret uden om zonen, plus én fil med alle dele."""
import os
import numpy as np, trimesh
HERE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(HERE, "stl"); OUT = os.path.join(STL, "print"); os.makedirs(OUT, exist_ok=True)
BED = 256.0

def part(name, x, y, rot=0, roty=0):
    """Placerer delens nederste venstre hjoerne i (x, y) paa pladen; rot drejer om z, roty om y (laegger delen paa siden)."""
    m = trimesh.load(os.path.join(STL, name + ".stl"))
    if roty:
        m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(roty), [0, 1, 0]))
    if rot:
        m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(rot), [0, 0, 1]))
    m.apply_translation(-m.bounds[0]); m.apply_translation([x, y, 0])
    assert m.bounds[1][0] <= BED and (m.bounds[1][1] <= BED or y >= BED), f"{name} udenfor pladen: {m.bounds[1][:2]}"
    assert not (m.bounds[0][0] < 18 and m.bounds[0][1] < 28), f"{name} rammer udelukkelseszonen"
    return name, m

PLADER = {
    "skuffe1-plade-1": [part("skuffe1-bestik__knivbakke-a", 86, 2), part("skuffe1-bestik__redskaber-a", 1, 86)],
    "skuffe1-plade-2": [part("skuffe1-bestik__knivbakke-b", 86, 2), part("skuffe1-bestik__redskaber-c", 1, 86)],  # a og b er printet
    "skuffe1-plade-3": [part("skuffe1-bestik__bestik-kort-a", 2, 129), part("skuffe1-bestik__redskaber-b", 20, 32, rot=90)],
    "skuffe1-plade-4": [part("skuffe1-bestik__bestik-kort-b", 2, 129)],
    # kanalerne printes liggende paa bagvaeggen (drejet 90 grader om y), saa taendernes profil og bolthullet bliver paene
    "skuffe1-plade-5": [part("skuffe1-bestik__bestik-lang-b", 128.5, 2), part("indsats__kanal-a", 18.5, 2, roty=90), part("indsats__kanal-b", 73.5, 2, roty=90)],
    # kun kanalerne (begge skuffer bruger samme sæt): print denne plade én gang pr. skuffe
    "kanaler": [part("indsats__kanal-a", 40, 2, roty=90), part("indsats__kanal-b", 130, 2, roty=90)],
}
UDELADT = "bestik-lang-a (identisk med testbakken, allerede printet); redskaber-a og -b er printet; kun endestykket c (med bane til steakknivene) er på plade 2"

# --- Skuffe 2 ---------------------------------------------------------------
# Mønster: en 4x4 (167,5) bagerst tv. + en 2x6 (83,5 x 251,5) th., eller blandede 2x4/4x2.
S2 = "skuffe2-ruller-poser__"
X0, XR, YB = 1.0, 170.5, 87.5      # venstre kant, hoejre kolonne, bagerste raekke (fri af zonen forrest tv.)
PLADER2 = {
    "skuffe2-plade-1": [part(S2 + "ruller-a", X0, YB), part(S2 + "lange-ting", XR, 2),
                        part(S2 + "elastikker", 20, 1), part(S2 + "frit-1x2", 64, 1)],
    "skuffe2-plade-2": [part(S2 + "ruller-b", X0, YB), part(S2 + "istad-mellem", XR, 2)],
    "skuffe2-plade-3": [part(S2 + "mellemlaegspapir", X0, YB), part(S2 + "istad-smaa", XR, 2)],
    "skuffe2-plade-4": [part(S2 + "istad-store-a", X0, YB), part(S2 + "termometre", 86.5, 1),
                        part(S2 + "istad-store-b", 172, 1), part(S2 + "pynt", 86.5, 171)],
    "skuffe2-plade-5": [part(S2 + "poseklemmer", X0, YB), part(S2 + "frit-4x2", 86.5, 1), part(S2 + "smaating", 86.5, 86.5)],
}


def check(plade, parts):
    """Ingen overlap (mindst 1,5 mm luft) mellem delene paa en plade."""
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            (na, a), (nb, b) = parts[i], parts[j]
            sep_x = max(a.bounds[0][0] - b.bounds[1][0], b.bounds[0][0] - a.bounds[1][0])
            sep_y = max(a.bounds[0][1] - b.bounds[1][1], b.bounds[0][1] - a.bounds[1][1])
            assert max(sep_x, sep_y) >= 1.5, f"{plade}: {na} og {nb} ligger for taet ({max(sep_x, sep_y):.1f} mm)"


def write_set(plader, samlet_navn, ekstra=()):
    alle = trimesh.Scene(); rows = []
    for plade, parts in plader.items():
        check(plade, parts)
        sc = trimesh.Scene()
        for n, m in parts:
            sc.add_geometry(m, node_name=n, geom_name=n); alle.add_geometry(m.copy(), node_name=n, geom_name=n)
        sc.export(os.path.join(OUT, plade + ".3mf"))
        rows.append((plade, [n.split("__")[1] for n, _ in parts], sum(m.volume for _, m in parts) / 1000))
        print(plade, rows[-1][1])
    for n, m in ekstra:
        alle.add_geometry(m, node_name=n, geom_name=n)
    alle.export(os.path.join(OUT, samlet_navn + ".3mf"))
    return rows


_, m_a = part("skuffe1-bestik__bestik-lang-a", 2, 300)
kanal = PLADER.pop("kanaler")
rows1 = write_set(PLADER, "skuffe1-bestik-alle-dele", ekstra=[("skuffe1-bestik__bestik-lang-a", m_a)])
write_set({"kanaler": kanal}, "kanaler")
rows2 = write_set(PLADER2, "skuffe2-alle-dele")

with open(os.path.join(HERE, "printplan.md"), "w") as f:
    f.write("# Printplan\n\nBambu P1S. Delene er placeret uden om udelukkelseszonen forrest til venstre, så pladefilerne kan "
            "slices direkte. Forslag: 0,2 mm lag, 3 vægge, 15 % infill, ingen støtte, ingen brim.\n")
    for titel, rows, samlet in (("Skuffe 1 (bestik)", rows1, "skuffe1-bestik-alle-dele"), ("Skuffe 2 (ruller og poser)", rows2, "skuffe2-alle-dele")):
        f.write(f"\n## {titel}\n\n| Plade | Dele | Volumen (massivt) |\n|---|---|---|\n")
        for plade, names, vol in rows:
            f.write(f"| `stl/print/{plade}.3mf` | {', '.join(names)} | {vol:.0f} cm³ |\n")
        f.write(f"\nAlle dele i én fil: `stl/print/{samlet}.3mf`.\n")
    f.write("\n## Kanaler\n\n`stl/print/kanaler.3mf` har de to kanaler liggende på siden. Samme sæt til begge skuffer: print den én gang pr. skuffe.\n"
            f"\n**Skuffe 1, udeladt af pladerne:** {UDELADT}.\n")
print("skrev", OUT, "og printplan.md")
