#!/usr/bin/env python3
"""Plantegning med navne paa indholdet i hvert rum -> preview/plan-med-navne.png"""
import os, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plan
from gridfinity import PITCH

HERE = os.path.dirname(os.path.abspath(__file__))
W = plan.DRAWER_UNITS[0] * PITCH; D = plan.DRAWER_UNITS[1] * PITCH
C4, C3, SK, C2 = plan.C4, plan.C3, plan.SMAA_KOL, plan.C2
IN6, IN3 = plan.W_IN6, plan.W_IN3

# Rum pr. bakke: (x0, y0, x1, y1 i mm indvendigt fra bagkant/venstre, tekst)
ROOMS = {
    "knivbakke": [
        (0, 0, 165, 335, "KNIVE, LANGE\nfra venstre: 33 · 31 · 31 · 25 · 22 · 22 cm\nspidser mod bagvæg, 6 lodrette slidser"),
        (62, 290, 165, 500, "KNIVE, KORTE\n18 · 18 · 21 · 21 · 21 · 21 · 21 cm\n(urteknivene foran de to 31 cm)"),
        (0, 338, 59, 419, "Bamix-skær"),
        (0, 419, 59, 500, "frit\n(knivsliber,\nproptrækker)"),
    ],
    "redskaber": [
        (0, 0, 81, 250, "Piskeris, ostehøvl,\nlange redskaber\n\nBrødkniv 39 cm\nlangs venstre væg"),
        (0, 250, 81, 500, "Hvidløgspresser,\nrivejern, dåseåbner,\nproptrækker"),
    ],
    "bestik-lang-a": [(0, 0, C2, IN6, "Spiseknive"), (C2 + 1.26, 0, IN3, IN6, "Gafler")],
    "bestik-lang-b": [(0, 0, C2, IN6, "Spiseskeer\n(også 21 cm)"), (C2 + 1.26, 0, IN3, IN6, "Lange\nteskeer")],
    "bestik-kort": [
        (0, 0, SK, IN6, "Måleskeer,\npizzahjul, te-si,\nsmåværktøj"),
        (SK + 1.26, 0, IN6, C3, "Teskeer"),
        (SK + 1.26, C3 + 1.26, IN6, 2 * C3 + 1.26, "Børnebestik"),
        (SK + 1.26, 2 * C3 + 2.52, IN6, IN6, "Kagegafler"),
    ],
    "pynt": [(0, 0, 165, 81, "Flag, parasoller, kagelys")],
    "frit-4x2": [(0, 0, 165, 81, "frit (reserve)")],
    "ruller": [(0, 0, 165, 333, "Film · sølvpapir ·\ncellofan · fryseposer\npå rulle\n(gribes ved forkanten)")],
    "termometre": [(0, 0, 81, 165, "Termometre,\nsnor")],
    "istad-store": [(0, 0, 81, 333, "ISTAD\n29,5 cm")],
    "lange-ting": [(0, 0, 81, 249, "Trægafler,\nsushi-måtte")],
    "istad-mellem": [(0, 0, 81, 249, "ISTAD\n23 cm")],
    "smaating": [(0, 0, 80, 81, "Tandstikker,\nbarberblade"), (81.3, 0, 165, 81, "Tændstikker,\nkagelys")],
    "istad-smaa": [(0, 0, 81, 249, "ISTAD\n19 cm")],
    "poseklemmer": [(0, 0, 81, 165, "Poseklemmer\n(alle tre str.)")],
    "elastikker": [(0, 0, 39, 81, "Elas-\ntikker")],
    "frit-1x2": [(0, 0, 39, 81, "frit\n(snor)")],
    "mellemlaegspapir": [(0, 0, 165, 165, "MELLEMLÆGSPAPIR\n+ tændstikker")],
}
KANAL = {"skuffe1-bestik": "KANAL: spisepinde · grillspyd", "skuffe2-ruller-poser": "KANAL: sugerør"}
FILL = ["#cfe3f5", "#f5e2c8", "#d9f0d3", "#f3d4e1", "#e9dcf5", "#fff3b8", "#d2eff0", "#f2d9c8"]

fig, axes = plt.subplots(1, 2, figsize=(19, 10.5))
for ax, (dname, bins) in zip(axes, plan.DRAWERS.items()):
    ax.add_patch(mp.Rectangle((0, -22.5), W, D + 22.5, fc="#eee8dc", ec="#6b5d45", lw=2))
    for bi, b in enumerate(bins):
        x = b.pos[0] * PITCH + 0.25; ytop = D - b.pos[1] * PITCH - 0.25   # ytop = bagkant af bakken
        ax.add_patch(mp.FancyBboxPatch((x, ytop - b.L), b.W, b.L, boxstyle="round,pad=0,rounding_size=4",
                                       fc=FILL[bi % len(FILL)], ec="#333", lw=1.4))
        for (x0, y0, x1, y1, txt) in ROOMS.get(b.name, []):
            rx, ry = x + b.wall + x0, ytop - b.wall - y1
            rw, rh = x1 - x0, y1 - y0
            ax.add_patch(mp.Rectangle((rx, ry), rw, rh, fc="none", ec="#333", lw=0.9, ls="--"))
            fs = 9 if min(rw, rh) >= 60 else 7.5
            ax.text(rx + rw / 2, ry + rh / 2, txt, ha="center", va="center", fontsize=fs, linespacing=1.15)
        ax.text(x + b.W - 3, ytop - b.L + 3, f"{b.name} {b.units_x}×{b.units_y}", ha="right", va="bottom", fontsize=6, color="#555")
    ax.add_patch(mp.Rectangle((0, -22.5), W, 22.5, fc="#d9c7a0", ec="#333", lw=1.2))
    ax.text(W / 2, -11, KANAL[dname], ha="center", va="center", fontsize=9, fontweight="bold")
    ax.text(W / 2, D + 8, "▲ bagkant", ha="center", fontsize=10, color="#444")
    ax.text(W / 2, -36, "▼ forkant (mod dig) ▼", ha="center", fontsize=11, color="#444")
    ax.set_title(dname, fontsize=14)
    ax.set_xlim(-8, W + 8); ax.set_ylim(-48, D + 20); ax.set_aspect("equal"); ax.set_axis_off()
plt.tight_layout(); fig.subplots_adjust(top=0.95)
out = os.path.join(HERE, "preview", "plan-med-navne.png")
plt.savefig(out, dpi=110); print("skrev", out)
