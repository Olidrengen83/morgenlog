"""
Lille, selvstændigt Gridfinity-bibliotek bygget på manifold3d.

Laver skuffeindsatser (bakker uden stable-læbe) der passer i en standard
Gridfinity-baseplade (42 mm pitch). Alt er i millimeter.

Koordinater for en bakke:
  x = bredde (0 .. W),  y = længde (0 .. L),  z = højde (0 = bund af fod).
  Bagenden er y = 0, forenden (mod brugeren) er y = L.

Størrelsen angives i enheder (1 enhed = 42 mm). En bakke på n enheder er
n*42 - 0.5 mm udvendigt. Højde er u * 7 mm (uden stable-læbe).

Særlige features:
  * dividers_y: skillevægge på tværs (ved y-position fra bakkens bagkant)
  * dividers_x: skillevægge på langs (ved x-position fra bakkens venstre kant)
  * front_notch: halvrundt greb-hak i forvæggen (y = L)
  * knife=KnifeTray(...): knivbakke med skrå slidser og håndtagsrampe
  * split(): skærer en lang bakke i segmenter der passer på printerpladen
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Tuple

from manifold3d import CrossSection, JoinType, Manifold

# --- Gridfinity-konstanter --------------------------------------------------
PITCH = 42.0            # mm pr. enhed
GAP = 0.5               # luft mellem bakker (udvendig = n*PITCH - GAP)
CELL = PITCH - GAP      # 41.5 mm: topbredde af én fodcelle
R_OUTER = 4.0           # hjørneradius udvendigt (øverst på foden og på kroppen)
BASE_C1 = 0.8           # nederste 45°-affasning
BASE_V = 1.8            # lodret stykke
BASE_C2 = 2.15          # øverste 45°-affasning
BASE_H = BASE_C1 + BASE_V + BASE_C2   # 4.75 mm
UNIT_H = 7.0            # mm pr. højdeenhed

SEGMENTS = 32           # rundings-opløsning


def _rrect(w: float, h: float, r: float) -> CrossSection:
    """Afrundet rektangel med nederste venstre hjørne i (0,0)."""
    r = max(min(r, w / 2 - 1e-6, h / 2 - 1e-6), 0.0)
    if r <= 1e-6:
        return CrossSection.square((w, h))
    core = CrossSection.square((w - 2 * r, h - 2 * r)).translate((r, r))
    return core.offset(r, JoinType.Round, 2.0, SEGMENTS)


def _slab(cs: CrossSection, z0: float, z1: float) -> Manifold:
    return cs.extrude(z1 - z0).translate((0, 0, z0))


def base_cell() -> Manifold:
    """Én Gridfinity-fodcelle (41.5 mm top), hjørne i (0,0,0)."""
    w3, r3 = CELL, R_OUTER
    w2, r2 = w3 - 2 * BASE_C2, r3 - BASE_C2
    w1, r1 = w2 - 2 * BASE_C1, r2 - BASE_C1
    eps = 0.01
    def centered(w, r, z):
        return _slab(_rrect(w, w, r), z, z + eps).translate(((w3 - w) / 2, (w3 - w) / 2, 0))
    lower = Manifold.batch_hull([centered(w1, r1, 0), centered(w2, r2, BASE_C1 - eps)])
    middle = _slab(_rrect(w2, w2, r2), BASE_C1, BASE_C1 + BASE_V).translate(
        ((w3 - w2) / 2, (w3 - w2) / 2, 0))
    upper = Manifold.batch_hull([centered(w2, r2, BASE_C1 + BASE_V),
                                 centered(w3, r3, BASE_H - eps)])
    return lower + middle + upper


_CELL_CACHE: Optional[Manifold] = None


def _cell() -> Manifold:
    global _CELL_CACHE
    if _CELL_CACHE is None:
        _CELL_CACHE = base_cell()
    return _CELL_CACHE


@dataclass
class KnifeTray:
    """Parametre for knivbakke. Knivspidser mod y=0 (bagenden)."""
    slots: int = 10
    pitch: float = 15.0          # mm mellem slidser
    slot_width: float = 5.0      # bredde af slids (knivryg + luft)
    lean_deg: float = 25.0       # hældning af klingen fra lodret
    rib_thickness: float = 3.0
    rib_positions: Tuple[float, ...] = (45.0, 120.0, 195.0)  # y fra bagvæg (indvendigt)
    stagger: bool = True         # første ribbe kun med slidser i hver anden -> forskudte håndtag
    rest_start: float = 250.0    # håndtagsrampe starter her (indvendig y)
    rest_h0: float = 8.0         # rampehøjde over gulv ved start
    rest_h1: float = 20.0        # rampehøjde over gulv ved forenden
    rest_step: float = 22.0      # afstand mellem trin-ribber i rampen


@dataclass
class BinSpec:
    name: str
    units_x: int
    units_y: int
    units_z: int = 7
    wall: float = 1.6
    floor_top: float = 6.0            # gulvets overside (z)
    divider_t: float = 1.2
    dividers_y: Tuple[float, ...] = ()   # y-positioner (indvendigt, fra bagvæg)
    dividers_x: Tuple[float, ...] = ()   # x-positioner (indvendigt, fra venstre væg)
    divider_height: Optional[float] = None  # None = fuld højde
    front_notch: bool = False
    notch_radius: float = 14.0
    knife: Optional[KnifeTray] = None
    label: str = ""                   # fritekst til plan/README
    pos: Tuple[int, int] = (0, 0)     # placering i skuffen (enheder, x fra venstre, y fra bagkant)

    # --- afledte mål ---
    @property
    def W(self) -> float:
        return self.units_x * PITCH - GAP

    @property
    def L(self) -> float:
        return self.units_y * PITCH - GAP

    @property
    def H(self) -> float:
        return self.units_z * UNIT_H

    @property
    def inner(self) -> Tuple[float, float, float]:
        """Indvendige mål (bredde, længde, dybde)."""
        return (self.W - 2 * self.wall, self.L - 2 * self.wall, self.H - self.floor_top)


def _bases(spec: BinSpec) -> Manifold:
    cells = []
    for i in range(spec.units_x):
        for j in range(spec.units_y):
            cells.append(_cell().translate((i * PITCH, j * PITCH, 0)))
    return Manifold.batch_boolean(cells, __import__("manifold3d").OpType.Add)


def build_bin(spec: BinSpec) -> Manifold:
    """Hele bakken (usplittet) med hjørne i (0,0,0)."""
    W, L, H = spec.W, spec.L, spec.H
    wall = spec.wall
    body = _slab(_rrect(W, L, R_OUTER), BASE_H - 0.01, H)
    cavity = _slab(_rrect(W - 2 * wall, L - 2 * wall, R_OUTER - wall),
                   spec.floor_top, H + 1).translate((wall, wall, 0))
    m = _bases(spec) + body - cavity

    # Skillevægge
    dh = H if spec.divider_height is None else min(H, spec.floor_top + spec.divider_height)
    t = spec.divider_t
    for y in spec.dividers_y:
        m = m + Manifold.cube((W - 2 * wall + 0.4, t, dh - spec.floor_top + 0.5)).translate(
            (wall - 0.2, wall + y - t / 2, spec.floor_top - 0.5))
    for x in spec.dividers_x:
        m = m + Manifold.cube((t, L - 2 * wall + 0.4, dh - spec.floor_top + 0.5)).translate(
            (wall + x - t / 2, wall - 0.2, spec.floor_top - 0.5))

    # Knivbakke-features
    if spec.knife is not None:
        m = m + _knife_features(spec)

    # Greb-hak i forvæggen
    if spec.front_notch:
        r = min(spec.notch_radius, (W - 2 * wall) / 2 - 6)
        cyl = Manifold.cylinder(wall + 4, r, r, SEGMENTS).rotate((-90, 0, 0))
        m = m - cyl.translate((W / 2, L - wall - 2, H))
    return m


def _knife_features(spec: BinSpec) -> Manifold:
    k = spec.knife
    W, L, H = spec.W, spec.L, spec.H
    wall, fz = spec.wall, spec.floor_top
    iw = W - 2 * wall
    span = (k.slots - 1) * k.pitch
    # Klingen hælder mod +x: toppen af en 45 mm klinge flytter sig lean-afhængigt.
    lateral = 45.0 * math.sin(math.radians(k.lean_deg))
    x0 = wall + max(4.0, (iw - span - lateral) / 2)
    if x0 + span + lateral + 2 > W - wall:
        raise ValueError(
            f"{spec.name}: {k.slots} slidser à {k.pitch} mm med {k.lean_deg}° hældning "
            f"passer ikke i {iw:.0f} mm indvendig bredde")

    parts = []
    # Ribber med slidser
    for ri, y in enumerate(k.rib_positions):
        rib = Manifold.cube((iw + 0.4, k.rib_thickness, H - fz + 0.5)).translate(
            (wall - 0.2, wall + y, fz - 0.5))
        for s in range(k.slots):
            if k.stagger and ri == 0 and s % 2 == 1:
                continue  # ulige knive stopper mod første ribbe -> forskudte håndtag
            xs = x0 + s * k.pitch
            zb = fz + 3.0
            cutter = (Manifold.cube((k.slot_width, k.rib_thickness + 2, 80))
                      .translate((-k.slot_width / 2, 0, 0))
                      .rotate((0, k.lean_deg, 0))
                      .translate((xs, wall + y - 1, zb)))
            # Afrundet bund i slidsen så ryggen hviler blødt
            rnd = (Manifold.cylinder(k.rib_thickness + 2, k.slot_width / 2, k.slot_width / 2, 16)
                   .rotate((-90, 0, 0))
                   .translate((xs, wall + y - 1, zb)))
            rib = rib - cutter - rnd
        parts.append(rib)
    # Håndtagsrampe: trin-ribber (lette at printe) med stigende højde mod forenden
    y0 = wall + k.rest_start
    y1 = L - wall
    n = max(2, int((y1 - y0) // k.rest_step))
    for i in range(n):
        yy = y0 + i * (y1 - y0 - k.rib_thickness) / (n - 1)
        hh = k.rest_h0 + (k.rest_h1 - k.rest_h0) * i / (n - 1)
        parts.append(Manifold.cube((iw + 0.4, k.rib_thickness, hh + 0.5)).translate(
            (wall - 0.2, yy, fz - 0.5)))
    return Manifold.batch_boolean(parts, __import__("manifold3d").OpType.Add)


# --- Opdeling til printerpladen ---------------------------------------------

def plan_cuts(units: int, max_units: int) -> List[int]:
    """Deler `units` i så få, så ens segmenter som muligt (hver <= max_units)."""
    if units <= max_units:
        return [units]
    n = math.ceil(units / max_units)
    base, extra = divmod(units, n)
    return [base + (1 if i < extra else 0) for i in range(n)]


def split(spec: BinSpec, m: Manifold, max_units: int, kerf: float = 0.4
          ) -> List[Tuple[str, Manifold, Tuple[int, int]]]:
    """Returnerer [(navn, manifold, (enheder_x, enheder_y)), ...].

    Skærer midt i 0.5 mm-mellemrummet mellem fodceller, med `kerf` luft, så
    segmenterne kan stå helt op ad hinanden i basepladen. Skæres langs den
    længste akse først; derefter langs den anden hvis nødvendigt.
    """
    pieces = [(spec.name, m, (spec.units_x, spec.units_y), (0, 0))]
    for axis in (1, 0):  # y først, så x
        new = []
        for name, piece, (ux, uy), (ox, oy) in pieces:
            units = uy if axis == 1 else ux
            segs = plan_cuts(units, max_units)
            if len(segs) == 1:
                new.append((name, piece, (ux, uy), (ox, oy)))
                continue
            bb = piece.bounding_box()
            start = 0
            for si, seg in enumerate(segs):
                lo = start * PITCH - (GAP / 2) + (kerf / 2 if si > 0 else 0)
                hi = (start + seg) * PITCH - (GAP / 2) - (kerf / 2 if si < len(segs) - 1 else 0)
                if axis == 1:
                    box = Manifold.cube((bb[3] - bb[0] + 2, hi - lo, bb[5] - bb[2] + 2)).translate(
                        (bb[0] - 1, lo, bb[2] - 1))
                    sub = (piece ^ box).translate((0, -(start * PITCH), 0))
                    dims = (ux, seg)
                else:
                    box = Manifold.cube((hi - lo, bb[4] - bb[1] + 2, bb[5] - bb[2] + 2)).translate(
                        (lo, bb[1] - 1, bb[2] - 1))
                    sub = (piece ^ box).translate((-(start * PITCH), 0, 0))
                    dims = (seg, uy)
                tag = ("abcdefgh"[si] if axis == 1 else str(si + 1))
                new.append((f"{name}-{tag}", sub, dims, (ox, oy)))
                start += seg
        pieces = new
    return [(n, p, d) for n, p, d, _ in pieces]


def to_trimesh(m: Manifold):
    import numpy as np
    import trimesh
    mesh = m.to_mesh()
    verts = np.asarray(mesh.vert_properties)[:, :3]
    faces = np.asarray(mesh.tri_verts)
    return trimesh.Trimesh(vertices=verts, faces=faces, process=False)


def export_stl(m: Manifold, path: str) -> dict:
    tm = to_trimesh(m)
    tm.export(path)
    bb = m.bounding_box()
    return {
        "path": path,
        "size_mm": (round(bb[3] - bb[0], 1), round(bb[4] - bb[1], 1), round(bb[5] - bb[2], 1)),
        "volume_cm3": round(m.volume() / 1000, 1),
        "watertight": bool(tm.is_watertight),
        "triangles": int(len(tm.faces)),
    }
