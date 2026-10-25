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
    """Knivbakke med to rækker lodrette slidser. Spidser mod y=0 (bagenden).

    Bagerste række: lange knive, spids mod bagvæggen, holdt af `back_ribs`.
    Forreste række: korte knive, spids bagud, holdt af `front_ribs` (kun fra
    `front_x_from` og ud til højre væg). Til venstre for den forreste række er
    der et frit felt (x < front_x_from, y > field_y0), delt af tværvægge ved
    `field_dividers`. Alle x/y er indvendige mål fra venstre/bageste væg.
    """
    back_slots: int = 6
    back_pitch: float = 25.0
    back_x0: float = 20.0
    back_ribs: Tuple[float, ...] = (45.0, 120.0, 195.0)
    front_slots: int = 7
    front_pitch: float = 15.0
    front_x0: float = 70.0
    front_ribs: Tuple[float, ...] = (350.0, 430.0)
    front_x_from: float = 62.0
    field_y0: float = 338.0
    field_dividers: Tuple[float, ...] = (419.0,)
    slot_width: float = 4.0
    slot_bottom: float = 1.0        # slidsbund over gulvet
    rib_thickness: float = 3.0


@dataclass
class BinSpec:
    name: str
    units_x: int
    units_y: int
    units_z: int = 7
    wall: float = 1.26            # 3 linjer à 0,42 mm
    floor_top: float = 6.0            # gulvets overside (z)
    divider_t: float = 1.26
    dividers_y: Tuple[float, ...] = ()   # y-positioner (indvendigt, fra bagvæg)
    dividers_x: Tuple[float, ...] = ()   # x-positioner (indvendigt, fra venstre væg)
    divider_height: Optional[float] = None  # None = fuld højde
    front_notch: bool = False
    notch_radius: float = 14.0
    notch_x: Optional[float] = None   # hakkets centrum (x); None = midt på bakken
    notch_xs: Tuple[float, ...] = ()  # flere hak (x-centre, udvendige koordinater)
    walls: Tuple[Tuple[float, float, float, float], ...] = ()  # fritstående vægge (x0,y0,x1,y1) indv.
    rails: Tuple[Tuple[float, float, float, float, float], ...] = ()  # (x0,x1,y0,y1,z_top) lister
    divider_slots: Tuple[Tuple[float, float, float], ...] = ()  # (y-skillevæg, x-centrum, bredde): lodret slids i skillevæg
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

    for (y, xc, sw) in spec.divider_slots:
        m = m - Manifold.cube((sw, t + 2, H)).translate((wall + xc - sw / 2, wall + y - t / 2 - 1, spec.floor_top + 1.0))
        m = m - (Manifold.cylinder(t + 2, sw / 2, sw / 2, 16).rotate((-90, 0, 0))
                 .translate((wall + xc, wall + y - t / 2 - 1, spec.floor_top + 1.0)))

    # Fritstående vægge (fuld højde) og lister til løse indsatser
    for (x0, y0, x1, y1) in spec.walls:
        m = m + Manifold.cube((x1 - x0, y1 - y0, H - spec.floor_top + 0.5)).translate(
            (wall + x0, wall + y0, spec.floor_top - 0.5))
    for (x0, x1, y0, y1, zt) in spec.rails:
        for xa in (x0, x1 - 3.0):
            m = m + Manifold.cube((3.0, y1 - y0, 2.0)).translate((wall + xa, wall + y0, zt - 2.0))

    # Knivbakke-features
    if spec.knife is not None:
        m = m + _knife_features(spec)

    # Greb-hak i forvæggen
    if spec.front_notch:
        r = min(spec.notch_radius, (W - 2 * wall) / 2 - 6)
        cyl = Manifold.cylinder(wall + 4, r, r, SEGMENTS).rotate((-90, 0, 0))
        xs = list(spec.notch_xs) or [W / 2 if spec.notch_x is None else spec.notch_x]
        for nx in xs:
            m = m - cyl.translate((nx, L - wall - 2, H))
    return m


def _knife_features(spec: BinSpec) -> Manifold:
    k = spec.knife
    W, L, H = spec.W, spec.L, spec.H
    wall, fz = spec.wall, spec.floor_top
    iw, il = W - 2 * wall, L - 2 * wall
    parts = []

    def rib_with_slots(x_from, x_to, y, xs):
        rib = Manifold.cube((x_to - x_from + 0.4, k.rib_thickness, H - fz + 0.5)).translate(
            (wall + x_from - 0.2, wall + y, fz - 0.5))
        zb = fz + k.slot_bottom + k.slot_width / 2
        for xs_ in xs:
            cutter = Manifold.cube((k.slot_width, k.rib_thickness + 2, H)).translate(
                (wall + xs_ - k.slot_width / 2, wall + y - 1, zb))
            rnd = (Manifold.cylinder(k.rib_thickness + 2, k.slot_width / 2, k.slot_width / 2, 16)
                   .rotate((-90, 0, 0)).translate((wall + xs_, wall + y - 1, zb)))
            rib = rib - cutter - rnd
        return rib

    back_xs = [k.back_x0 + i * k.back_pitch for i in range(k.back_slots)]
    front_xs = [k.front_x0 + i * k.front_pitch for i in range(k.front_slots)]
    if back_xs[-1] + 6 > iw or front_xs[-1] + 6 > iw or front_xs[0] - k.slot_width < k.front_x_from:
        raise ValueError(f"{spec.name}: slidserne passer ikke i {iw:.0f} mm indvendig bredde")
    for y in k.back_ribs:
        parts.append(rib_with_slots(0, iw, y, back_xs))
    for y in k.front_ribs:
        parts.append(rib_with_slots(k.front_x_from, iw, y, front_xs))
    # Det frie felt: langsgående væg + tværvægge
    t = k.rib_thickness
    parts.append(Manifold.cube((t, il - k.field_y0 + t + 0.2, H - fz + 0.5)).translate(
        (wall + k.front_x_from - t, wall + k.field_y0 - t, fz - 0.5)))
    for y in (k.field_y0,) + tuple(k.field_dividers):
        parts.append(Manifold.cube((k.front_x_from + 0.4, t, H - fz + 0.5)).translate(
            (wall - 0.2, wall + y - t, fz - 0.5)))
    return Manifold.batch_boolean(parts, __import__("manifold3d").OpType.Add)


@dataclass
class TraySpec:
    """Løs indsats (simpel kasse uden Gridfinity-fod), fx øverste lag i et rum."""
    name: str
    width: float
    length: float
    height: float
    wall: float = 1.26
    floor: float = 1.26
    end_notch_radius: float = 10.0
    label: str = ""


def build_tray(t: TraySpec) -> Manifold:
    outer = _slab(_rrect(t.width, t.length, 2.0), 0, t.height)
    inner = _slab(_rrect(t.width - 2 * t.wall, t.length - 2 * t.wall, 1.0), t.floor, t.height + 1
                  ).translate((t.wall, t.wall, 0))
    m = outer - inner
    if t.end_notch_radius > 0:
        r = t.end_notch_radius
        cyl = Manifold.cylinder(t.wall + 4, r, r, SEGMENTS).rotate((-90, 0, 0))
        m = m - cyl.translate((t.width / 2, -2, t.height)) - cyl.translate((t.width / 2, t.length - t.wall - 2, t.height))
    return m


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
    import trimesh
    tm = to_trimesh(m)
    tm.export(path)
    reloaded = trimesh.load(path)   # tjek som sliceren ser filen
    bb = m.bounding_box()
    return {
        "path": path,
        "size_mm": (round(bb[3] - bb[0], 1), round(bb[4] - bb[1], 1), round(bb[5] - bb[2], 1)),
        "volume_cm3": round(m.volume() / 1000, 1),
        "watertight": bool(tm.is_watertight and reloaded.is_watertight),
        "triangles": int(len(tm.faces)),
    }
