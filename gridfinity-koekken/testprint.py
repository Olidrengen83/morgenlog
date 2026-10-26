#!/usr/bin/env python3
"""Hurtig testbakke: 3x6 enheder med skillevaeg i midten = to rum paa 61 x 249 mm,
som i den rigtige bestikbakke. Lav hoejde for kort printtid.

Brug:  python3 testprint.py            (4 enheder = 28 mm hoej)
       python3 testprint.py --full     (8 enheder = 56 mm, som den rigtige)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gridfinity import BinSpec, build_bin, export_stl, to_trimesh  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
full = "--full" in sys.argv
h = 8 if full else 4
inner = 3 * 42 - 0.5 - 2 * 1.26          # 122,98 mm
c = (inner - 1.26) / 2                   # 60,86 mm pr. rum
spec = BinSpec(f"test-bestik-3x6-{h}u", 3, 6, h,
               dividers_x=(c + 0.63,),
               front_notch=True, notch_radius=12,
               notch_xs=(1.26 + c / 2, 1.26 + c + 1.26 + c / 2))
m = build_bin(spec)
out = os.path.join(HERE, "stl", "test")
os.makedirs(out, exist_ok=True)
info = export_stl(m, os.path.join(out, spec.name + ".stl"))
tm = to_trimesh(m)
tm.export(os.path.join(out, spec.name + ".3mf"))
print(f"{spec.name}: {info['size_mm']} mm, to rum a {c:.1f} x {inner and (6*42-0.5-2*1.26):.0f} mm, "
      f"{info['volume_cm3']} cm3, vandtaet={info['watertight']}")
print("skrev", out)
