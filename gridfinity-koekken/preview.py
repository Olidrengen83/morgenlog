#!/usr/bin/env python3
"""Laver PNG-forhåndsvisninger (3D) af hver skuffe med alle bakker på plads."""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plan  # noqa: E402
from gridfinity import PITCH, build_bin, to_trimesh  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "preview")
os.makedirs(OUT, exist_ok=True)

COLORS = ["#8fb8de", "#e8c48a", "#9fd39a", "#e7a3bf", "#c3aee6", "#f0e07a", "#8fd6d8", "#e8b89a"]


def render_drawer(name, bins, views, fname, figsize=(18, 9)):
    fig = plt.figure(figsize=figsize)
    for vi, (el, az) in enumerate(views):
        ax = fig.add_subplot(1, len(views), vi + 1, projection="3d")
        for bi, b in enumerate(bins):
            tm = to_trimesh(build_bin(b))
            v = tm.vertices + np.array([b.pos[0] * PITCH, -(b.pos[1] * PITCH) - b.L, 0])
            ax.plot_trisurf(v[:, 0], v[:, 1], tm.faces, v[:, 2], color=COLORS[bi % len(COLORS)],
                            edgecolor="none", shade=True, alpha=1.0)
        W, D = plan.DRAWER_UNITS[0] * PITCH, plan.DRAWER_UNITS[1] * PITCH
        ax.set_xlim(0, W); ax.set_ylim(-D, 0); ax.set_zlim(0, 120)
        ax.set_box_aspect((W, D, 120))
        ax.view_init(el, az)
        ax.set_axis_off()
    fig.suptitle(f"{name}  (forkanten nederst / nærmest)", fontsize=14)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, fname), dpi=110)
    plt.close(fig)


def render_single(b, fname):
    tm = to_trimesh(build_bin(b))
    fig = plt.figure(figsize=(14, 7))
    for vi, (el, az) in enumerate([(40, -55), (25, 30)]):
        ax = fig.add_subplot(1, 2, vi + 1, projection="3d")
        ax.plot_trisurf(tm.vertices[:, 0], tm.vertices[:, 1], tm.faces, tm.vertices[:, 2],
                        color="#b9c7d6", edgecolor="#333", linewidth=0.08, shade=True)
        ax.set_box_aspect((b.W, b.L, max(b.H, 60)))
        ax.view_init(el, az); ax.set_axis_off()
    fig.suptitle(f"{b.name}: {b.units_x}×{b.units_y}×{b.units_z} enheder", fontsize=13)
    plt.tight_layout(); plt.savefig(os.path.join(OUT, fname), dpi=110); plt.close(fig)


def render_layout(fname):
    import matplotlib.patches as mpatches
    n = len(plan.DRAWERS)
    fig, axes = plt.subplots(1, n, figsize=(8.5 * n, 9))
    if n == 1:
        axes = [axes]
    W, D = plan.DRAWER_UNITS[0] * PITCH, plan.DRAWER_UNITS[1] * PITCH
    for ax, (dname, bins) in zip(axes, plan.DRAWERS.items()):
        ax.add_patch(mpatches.Rectangle((0, 0), W, D, fc="#e8e1d3", ec="#6b5d45", lw=2))
        for g in range(plan.DRAWER_UNITS[0] + 1):
            ax.plot([g * PITCH] * 2, [0, D], color="#c9bfae", lw=0.5)
        for g in range(plan.DRAWER_UNITS[1] + 1):
            ax.plot([0, W], [g * PITCH] * 2, color="#c9bfae", lw=0.5)
        for bi, b in enumerate(bins):
            x, y = b.pos[0] * PITCH + 0.25, D - (b.pos[1] * PITCH + 0.25) - b.L
            ax.add_patch(mpatches.FancyBboxPatch((x, y), b.W, b.L, boxstyle="round,pad=0,rounding_size=4",
                                                 fc=COLORS[bi % len(COLORS)], ec="#333", lw=1.2))
            iwb = b.W - 2 * b.wall
            for dx in b.dividers_x:
                ax.plot([x + b.wall + iwb - dx] * 2, [y + 2, y + b.L - 2], color="#333", lw=1.5)
            for dy in b.dividers_y:
                ax.plot([x + 2, x + b.W - 2], [y + b.L - b.wall - dy] * 2, color="#333", lw=1.5)
            for (wx0, wy0, wx1, wy1) in b.walls:
                ax.add_patch(mpatches.Rectangle((x + b.wall + iwb - wx1, y + b.L - b.wall - wy1), wx1 - wx0, wy1 - wy0, fc="#333", ec="none"))
            for (rx0, rx1, ry0, ry1, _z) in b.rails:
                ax.add_patch(mpatches.Rectangle((x + b.wall + iwb - rx1, y + b.L - b.wall - ry1), rx1 - rx0, ry1 - ry0, fc="none", ec="#333", lw=1, ls=":"))
            if b.knife is not None:
                k = b.knife; iw = iwb
                sgn = -1 if b.mirror_x else 1   # spejlet bakke + spejlet visning = som lokalt
                def X(lx):  # lokal x -> tegning (set oppefra)
                    return x + b.wall + (lx if b.mirror_x else iw - lx)
                for ry in k.back_ribs:
                    ax.plot([x + b.wall, x + b.wall + iw], [y + b.L - b.wall - ry] * 2, color="#333", lw=2, ls="--")
                fx = X(k.front_x_from)
                ax.plot([fx, fx], [y, y + b.L - b.wall - min(k.box_y0, k.field_y0)], color="#333", lw=2)
                ax.plot([fx, X(iw)], [y + b.L - b.wall - k.box_y0] * 2, color="#333", lw=2)
                for fd in (k.field_y0,) + tuple(k.field_dividers):
                    ax.plot([X(0), fx], [y + b.L - b.wall - fd] * 2, color="#333", lw=2)
            if b.front_notch:
                for nx in (list(b.notch_xs) or [b.W / 2]):
                    ax.add_patch(mpatches.Wedge((x + b.W - nx, y), 10, 0, 180, fc="#faf8f3", ec="#333", lw=1))
            fs = 10 if min(b.W, b.L) > 100 else 8
            ax.text(x + b.W / 2, y + b.L / 2 + 6, b.name, ha="center", va="center", fontsize=fs, fontweight="bold")
            ax.text(x + b.W / 2, y + b.L / 2 - 8, f"{b.units_x}×{b.units_y}×{b.units_z}u", ha="center", va="center", fontsize=fs - 2, color="#333")
        # kanal på basepladens 22,5 mm-stribe forrest
        ax.add_patch(mpatches.Rectangle((0, -22.5), W, 22.5, fc="#d9c7a0", ec="#333", lw=1.2))
        ax.text(W / 2, -11, "kanal 22 × 503 mm: spisepinde · sugerør · grillspyd (åben mod skuffefronten)", ha="center", va="center", fontsize=8)
        ax.set_xlim(-10, W + 10); ax.set_ylim(-55, D + 10); ax.set_aspect("equal"); ax.set_axis_off()
        ax.set_title(f"{dname}  ·  {plan.DRAWER_UNITS[0]}×{plan.DRAWER_UNITS[1]} enheder (set oppefra, bagkant øverst)", fontsize=13)
        ax.text(W / 2, -42, "▼ forkant (mod dig) ▼", ha="center", fontsize=11, color="#444")
    plt.tight_layout(); fig.subplots_adjust(top=0.94)
    plt.savefig(os.path.join(OUT, fname), dpi=100); plt.close(fig)


if __name__ == "__main__":
    render_layout("layout.png")
    for dname, bins in plan.DRAWERS.items():
        render_drawer(dname, bins, [(55, -70), (88, -90)], f"{dname}.png")
    notch_done = False
    for b in plan.BESTIK + plan.RULLER:
        if b.front_notch and not (b.knife or b.dividers_x or b.dividers_y):
            if notch_done:
                continue  # én bestikbakke er nok som eksempel
            notch_done = True
        if b.knife or b.dividers_x or b.dividers_y or b.front_notch:
            render_single(b, f"bakke-{b.name}.png")
    print("skrev previews til", OUT)
