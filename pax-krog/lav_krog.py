"""Generer STL + SVG-forhåndsvisning af en krog, der hænger over en PAX-skuffefront.

Kør:  python3 lav_krog.py            (alle mål i mm, kan ændres herunder)
"""
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
import trimesh

# ---- Mål (mm) ---------------------------------------------------------------
FRONT      = 17.0   # skuffefrontens tykkelse
SLOER      = 0.4    # luft i slidsen (17.4 mm indvendigt). PLA: 0.3–0.5
VAEG       = 3.2    # godstykkelse i klemmen (top + begge ben)
BEN_UDE    = 32.0   # hvor langt benet går ned ad forsiden
BEN_INDE   = 18.0   # hvor langt benet går ned inde i skuffen
ARM_T      = 4.0    # krogarmens tykkelse
RAEK       = 30.0   # hvor langt krogen rager ud fra forsiden
STIG       = 5.0    # armen hælder let opad (så tøjet glider ind mod fronten)
SPIDS_H    = 16.0   # spidsens højde over armen
SPIDS_LAEN = 2.0    # spidsen læner ind mod skuffen
GUSSET     = 12.0   # forstærkning i hjørnet mellem ben og arm
BREDDE     = 25.0   # krogens bredde langs fronten
RUND       = 1.0    # afrunding af udvendige hjørner
# ------------------------------------------------------------------------------

def profil():
    slids = FRONT + SLOER
    top   = Polygon([(-VAEG, 0), (slids + VAEG, 0), (slids + VAEG, VAEG), (-VAEG, VAEG)])
    ude   = Polygon([(-VAEG, -BEN_UDE), (0, -BEN_UDE), (0, VAEG), (-VAEG, VAEG)])
    inde  = Polygon([(slids, -BEN_INDE), (slids + VAEG, -BEN_INDE),
                     (slids + VAEG, VAEG), (slids, VAEG)])
    klemme = unary_union([top, ude, inde]).buffer(-RUND).buffer(RUND, join_style=1)

    y0 = -BEN_UDE + ARM_T / 2                      # armens midterlinje ved benet
    p0 = (-VAEG + 0.5, y0)                         # starter lige inde i benet
    p1 = (-VAEG - RAEK, y0 + STIG)
    p2 = (p1[0] + SPIDS_LAEN, p1[1] + SPIDS_H)
    arm   = LineString([p0, p1]).buffer(ARM_T / 2, cap_style=2)   # flade ender
    knae  = Point(p1).buffer(ARM_T / 2)
    spids = LineString([p1, p2]).buffer(ARM_T / 2, cap_style=2)
    top_s = Point(p2).buffer(ARM_T / 2)
    # forstærkning: trekant der følger armens underside (hældning STIG/RAEK)
    gus   = Polygon([(-VAEG, -BEN_UDE + GUSSET), (-VAEG, -BEN_UDE),
                     (-VAEG - GUSSET, -BEN_UDE + GUSSET * STIG / RAEK + 1.0)])
    return unary_union([klemme, arm, knae, spids, top_s, gus]).buffer(0)

def svg(poly, sti):
    minx, miny, maxx, maxy = poly.bounds
    pad = 6
    w, h = maxx - minx + 2 * pad, maxy - miny + 2 * pad
    s = 8  # px per mm
    def pts(ring):
        return " ".join(f"{(x - minx + pad) * s:.1f},{(maxy - y + pad) * s:.1f}" for x, y in ring.coords)
    front = (f'<rect x="{(0 - minx + pad) * s}" y="{(maxy - 0 + pad) * s - 0}" '
             f'width="{FRONT * s}" height="{(BEN_UDE + 20) * s}" fill="#d9c7a8" stroke="#8a7a5c"/>')
    body = f'<path d="M{pts(poly.exterior)}Z ' + " ".join("M" + pts(i) + "Z" for i in poly.interiors) + \
           '" fill="#4a7fb5" fill-rule="evenodd" stroke="#1d3d5c" stroke-width="2"/>'
    txt = (f'<text x="{(0 - minx + pad) * s + 4}" y="{(maxy + pad) * s + 70}" font-family="sans-serif" '
           f'font-size="22" fill="#5c4d33">front {FRONT:g} mm</text>')
    open(sti, "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w * s}" height="{h * s}" '
        f'viewBox="0 0 {w * s} {h * s}" style="background:#fff">'
        f'<rect width="100%" height="100%" fill="#ffffff"/>{front}{body}{txt}</svg>')

def iso_svg(m, sti):
    import numpy as np
    v = m.vertices.copy(); f = m.faces
    def rot(a, ax):
        c, s_ = np.cos(a), np.sin(a)
        R = {"x": [[1,0,0],[0,c,-s_],[0,s_,c]], "y": [[c,0,s_],[0,1,0],[-s_,0,c]], "z": [[c,-s_,0],[s_,c,0],[0,0,1]]}[ax]
        return np.array(R)
    R = rot(np.radians(22), "x") @ rot(np.radians(-35), "y")   # skråt forfra og lidt oppefra
    v = v @ R.T
    n = m.face_normals @ R.T
    light = np.array([0.3, -0.5, 0.8]); light /= np.linalg.norm(light)
    order = np.argsort(v[f].mean(axis=1)[:, 2])         # langt væk først
    minx, miny = v[:, 0].min(), v[:, 1].min(); S = 7; pad = 8
    W = (v[:, 0].max() - minx + 2 * pad) * S; H = (v[:, 1].max() - miny + 2 * pad) * S
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}"><rect width="100%" height="100%" fill="#fff"/>']
    for i in order:
        if n[i][2] <= 0: continue
        sh = 0.45 + 0.55 * max(0.0, float(n[i] @ light))
        col = f"rgb({int(74*sh)},{int(127*sh)},{int(181*sh)})"
        pts = " ".join(f"{(x-minx+pad)*S:.1f},{H-(y-miny+pad)*S:.1f}" for x, y, _ in v[f[i]])
        out.append(f'<polygon points="{pts}" fill="{col}" stroke="{col}" stroke-width="0.6"/>')
    out.append("</svg>"); open(sti, "w").write("".join(out))

if __name__ == "__main__":
    p = profil()
    m = trimesh.creation.extrude_polygon(p, BREDDE)
    assert m.is_watertight, "mesh ikke tæt"
    m.export("pax_krog.stl")
    svg(p, "pax_krog_profil.svg")
    iso_svg(m, "pax_krog_3d.svg")
    minx, miny, maxx, maxy = p.bounds
    print(f"STL: {maxx-minx:.1f} x {maxy-miny:.1f} x {BREDDE:g} mm, volumen {m.volume/1000:.1f} cm³, "
          f"vægt ca. {m.volume/1000*1.24:.0f} g i PLA")
