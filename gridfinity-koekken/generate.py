#!/usr/bin/env python3
"""Genererer STL-filer, layout-tegning (SVG) og oversigt ud fra plan.py.

Brug:  python3 generate.py            (alle skuffer)
       python3 generate.py --max 5    (kortere segmenter til 220/250 mm-plader)
       python3 generate.py --only knivbakke
"""
import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plan  # noqa: E402
from gridfinity import PITCH, build_bin, build_tray, export_stl, split  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PLA_DENSITY = 1.24  # g/cm3


def validate_layout(name, bins, drawer_units):
    grid = {}
    for b in bins:
        for i in range(b.units_x):
            for j in range(b.units_y):
                c = (b.pos[0] + i, b.pos[1] + j)
                if c[0] >= drawer_units[0] or c[1] >= drawer_units[1]:
                    raise SystemExit(f"{name}: '{b.name}' stikker ud af skuffen ved {c}")
                if c in grid:
                    raise SystemExit(f"{name}: '{b.name}' overlapper '{grid[c]}' ved {c}")
                grid[c] = b.name
    free = drawer_units[0] * drawer_units[1] - len(grid)
    return free


def layout_svg(drawers, drawer_units, path):
    s = 1.0  # px pr. mm
    pad, gap_between = 40, 60
    dw, dh = drawer_units[0] * PITCH * s, drawer_units[1] * PITCH * s
    total_w = pad * 2 + len(drawers) * dw + (len(drawers) - 1) * gap_between
    total_h = pad * 2 + dh + 55
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_w}" height="{total_h}" '
           f'viewBox="0 0 {total_w} {total_h}" font-family="Helvetica, Arial, sans-serif">',
           '<rect width="100%" height="100%" fill="#faf8f3"/>']
    palette = ["#cfe3f5", "#f5e2c8", "#d9f0d3", "#f3d4e1", "#e9dcf5", "#fff3b8", "#d2eff0", "#f2d9c8"]
    for di, (dname, bins) in enumerate(drawers.items()):
        ox = pad + di * (dw + gap_between)
        oy = pad + 24
        out.append(f'<text x="{ox}" y="{oy - 8}" font-size="16" font-weight="bold">{dname}'
                   f'  ·  {drawer_units[0]}×{drawer_units[1]} enheder, bagkant øverst</text>')
        out.append(f'<rect x="{ox}" y="{oy}" width="{dw}" height="{dh}" fill="#e8e1d3" stroke="#6b5d45" stroke-width="2"/>')
        for gx in range(drawer_units[0] + 1):
            out.append(f'<line x1="{ox + gx * PITCH * s}" y1="{oy}" x2="{ox + gx * PITCH * s}" y2="{oy + dh}" stroke="#c9bfae" stroke-width="0.5"/>')
        for gy in range(drawer_units[1] + 1):
            out.append(f'<line x1="{ox}" y1="{oy + gy * PITCH * s}" x2="{ox + dw}" y2="{oy + gy * PITCH * s}" stroke="#c9bfae" stroke-width="0.5"/>')
        for bi, b in enumerate(bins):
            x = ox + b.pos[0] * PITCH * s + 1
            y = oy + b.pos[1] * PITCH * s + 1
            w = b.W * s - 1
            h = b.L * s - 1
            out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{palette[bi % len(palette)]}" stroke="#3b3b3b" stroke-width="1.2"/>')
            for dx in b.dividers_x:
                out.append(f'<line x1="{x + (b.wall + dx) * s}" y1="{y + 2}" x2="{x + (b.wall + dx) * s}" y2="{y + h - 2}" stroke="#3b3b3b" stroke-width="1.2"/>')
            for dy in b.dividers_y:
                out.append(f'<line x1="{x + 2}" y1="{y + (b.wall + dy) * s}" x2="{x + w - 2}" y2="{y + (b.wall + dy) * s}" stroke="#3b3b3b" stroke-width="1.2"/>')
            for (wx0, wy0, wx1, wy1) in b.walls:
                out.append(f'<rect x="{x + (b.wall + wx0) * s}" y="{y + (b.wall + wy0) * s}" width="{(wx1 - wx0) * s}" height="{(wy1 - wy0) * s}" fill="#3b3b3b"/>')
            for (rx0, rx1, ry0, ry1, _z) in b.rails:
                out.append(f'<rect x="{x + (b.wall + rx0) * s}" y="{y + (b.wall + ry0) * s}" width="{(rx1 - rx0) * s}" height="{(ry1 - ry0) * s}" fill="none" stroke="#3b3b3b" stroke-width="1" stroke-dasharray="3 3"/>')
            if b.knife is not None:
                k = b.knife
                iw = b.W - 2 * b.wall
                for ry in k.back_ribs:
                    out.append(f'<line x1="{x + b.wall * s}" y1="{y + (b.wall + ry) * s}" x2="{x + (b.wall + iw) * s}" y2="{y + (b.wall + ry) * s}" stroke="#3b3b3b" stroke-width="2" stroke-dasharray="4 3"/>')
                fy = y + (b.wall + min(k.box_y0, k.field_y0)) * s
                out.append(f'<line x1="{x + (b.wall + k.front_x_from) * s}" y1="{fy}" x2="{x + (b.wall + k.front_x_from) * s}" y2="{y + h - 2}" stroke="#3b3b3b" stroke-width="2"/>')
                out.append(f'<line x1="{x + (b.wall + k.front_x_from) * s}" y1="{y + (b.wall + k.box_y0) * s}" x2="{x + w - 2}" y2="{y + (b.wall + k.box_y0) * s}" stroke="#3b3b3b" stroke-width="2"/>')
                for fd in (k.field_y0,) + tuple(k.field_dividers):
                    out.append(f'<line x1="{x + 2}" y1="{y + (b.wall + fd) * s}" x2="{x + (b.wall + k.front_x_from) * s}" y2="{y + (b.wall + fd) * s}" stroke="#3b3b3b" stroke-width="2"/>')
            if b.front_notch:
                for nx in (list(b.notch_xs) or [b.W / 2]):
                    out.append(f'<path d="M {x + nx * s - 10} {y + h} a 10 10 0 0 0 20 0" fill="#faf8f3" stroke="#3b3b3b" stroke-width="1"/>')
            cx, cy = x + w / 2, y + h / 2
            fs = 11 if min(w, h) > 70 else 9
            out.append(f'<text x="{cx}" y="{cy - 2}" font-size="{fs}" text-anchor="middle" font-weight="bold">{b.name}</text>')
            out.append(f'<text x="{cx}" y="{cy + 11}" font-size="{fs - 2}" text-anchor="middle" fill="#444">{b.units_x}×{b.units_y}×{b.units_z}u</text>')
        out.append(f'<rect x="{ox}" y="{oy + dh}" width="{dw}" height="{22.5 * s}" fill="#d9c7a0" stroke="#333" stroke-width="1"/>')
        out.append(f'<text x="{ox + dw / 2}" y="{oy + dh + 15}" font-size="9" text-anchor="middle">kanal 22 × 503 mm (spisepinde · sugerør · grillspyd)</text>')
        out.append(f'<text x="{ox + dw / 2}" y="{oy + dh + 40}" font-size="12" text-anchor="middle" fill="#444">▼ forkant (mod dig) ▼</text>')
    out.append('</svg>')
    with open(path, "w") as f:
        f.write("\n".join(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=plan.MAX_PRINT_UNITS, help="maks. segmentlængde i enheder")
    ap.add_argument("--only", default=None, help="kun bakker hvis navn indeholder dette")
    ap.add_argument("--out", default=os.path.join(HERE, "stl"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    rows = []
    for dname, bins in plan.DRAWERS.items():
        free = validate_layout(dname, bins, plan.DRAWER_UNITS)
        print(f"\n== {dname}: {len(bins)} bakker, {free} ledige enheder")
        for b in bins:
            if args.only and args.only not in b.name:
                continue
            t0 = time.time()
            m = build_bin(b)
            parts = split(b, m, b.max_units or args.max)
            for pname, pm, dims in parts:
                info = export_stl(pm, os.path.join(args.out, f"{dname}__{pname}.stl"))
                grams = info["volume_cm3"] * PLA_DENSITY
                rows.append((dname, b, pname, dims, info, grams))
                flag = "" if info["watertight"] else "  !! IKKE VANDTÆT"
                print(f"  {pname:28s} {dims[0]}x{dims[1]}x{b.units_z}u  "
                      f"{info['size_mm'][0]:6.1f} x {info['size_mm'][1]:6.1f} x {info['size_mm'][2]:4.1f} mm  "
                      f"{info['volume_cm3']:6.1f} cm3 ≈ {grams:4.0f} g{flag}")
            print(f"    ({time.time() - t0:.1f} s)")

    for t in getattr(plan, "EXTRA", []):
        if args.only and args.only not in t.name:
            continue
        info = export_stl(build_tray(t), os.path.join(args.out, f"indsats__{t.name}.stl"))
        grams = info["volume_cm3"] * PLA_DENSITY
        rows.append(("loese-indsatser", t, t.name, ("-", "-"), info, grams))
        print(f"  {t.name:28s} indsats  {info['size_mm'][0]:6.1f} x {info['size_mm'][1]:6.1f} x {info['size_mm'][2]:4.1f} mm  "
              f"{info['volume_cm3']:6.1f} cm3 ≈ {grams:4.0f} g")

    for name, builder, label in getattr(plan, "EXTRA_BUILD", []):
        if args.only and args.only not in name:
            continue
        info = export_stl(builder(), os.path.join(args.out, f"indsats__{name}.stl"))
        grams = info["volume_cm3"] * PLA_DENSITY
        class _L:  # minimal objekt til printlisten
            pass
        obj = _L(); obj.label = label
        rows.append(("loese-indsatser", obj, name, ("-", "-"), info, grams))
        print(f"  {name:28s} indsats  {info['size_mm'][0]:6.1f} x {info['size_mm'][1]:6.1f} x {info['size_mm'][2]:4.1f} mm  "
              f"{info['volume_cm3']:6.1f} cm3 ≈ {grams:4.0f} g" + ("" if info["watertight"] else "  !! IKKE VANDTÆT"))

    layout_svg(plan.DRAWERS, plan.DRAWER_UNITS, os.path.join(HERE, "layout.svg"))

    # Oversigt til README
    with open(os.path.join(HERE, "printliste.md"), "w") as f:
        f.write("# Printliste\n\n")
        f.write(f"Genereret med `MAX_PRINT_UNITS = {args.max}` "
                f"(længste stykke {args.max * PITCH - 0.5:.1f} mm).\n\n")
        total = 0.0
        cur = None
        for dname, b, pname, dims, info, grams in rows:
            if dname != cur:
                cur = dname
                f.write(f"\n## {dname}\n\n| Fil | Enheder | Mål (mm) | Indvendigt (mm) | Volumen | ≈ PLA | Indhold |\n|---|---|---|---|---|---|---|\n")
            if hasattr(b, "inner"):
                iw, il, idp = b.inner
                f.write(f"| `{dname}__{pname}.stl` | {dims[0]}×{dims[1]}×{b.units_z} | "
                        f"{info['size_mm'][0]} × {info['size_mm'][1]} × {info['size_mm'][2]} | "
                        f"{iw:.0f} × {il:.0f} × {idp:.0f} (hel bakke) | {info['volume_cm3']} cm³ | {grams:.0f} g | {b.label} |\n")
            else:
                f.write(f"| `indsats__{pname}.stl` | – | "
                        f"{info['size_mm'][0]} × {info['size_mm'][1]} × {info['size_mm'][2]} | – | {info['volume_cm3']} cm³ | {grams:.0f} g | {b.label} |\n")
            total += grams
        f.write(f"\n**I alt ca. {total:.0f} g PLA** ({len(rows)} dele, massivt regnet; "
                "reelt forbrug er typisk 10-20 % mindre afhængigt af bund-infill).\n")
    print(f"\nSkrev {len(rows)} STL-filer til {args.out}, layout.svg og printliste.md")


if __name__ == "__main__":
    main()
