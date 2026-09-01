# Vægplade til lampe – SKÅDIS-ophæng

3D-printbar plade der hænges på et IKEA SKÅDIS pegboard, og som en lampe
med klassiske nøglehulsudskæringer ("omvendt lollipop") kan hænges på.

## Filer

- `lampe-vaegplade-skadis.scad` – parametrisk kilde (OpenSCAD). Justér mål her.
- `lampe-vaegplade-skadis.stl` – klar til slicing med standardmålene.

## Mål (standard)

| Del | Mål |
|---|---|
| Plade | 100 × 60 × 6 mm |
| Skruehoveder, cc-afstand | **78 mm** |
| Skruehoved: hals / hoved | Ø4,2 × 4 mm / Ø8 × 2,5 mm |
| SKÅDIS-kroge | 4 stk. i 40 mm grid, passer 5 × 15 mm-hullerne |

Tjek din lampes nøglehuller inden print: halsen (Ø4,2) skal kunne glide i
den smalle slids, og hovedet (Ø8) skal kunne gå gennem det store hul.
Passer det ikke, ret `peg_shaft_d` / `peg_head_d` / `peg_shaft_l` i
`.scad`-filen og eksportér en ny STL.

## Print

- Orientering: pladen **lodret på underkanten** (som den hænger på væggen).
- Supports: **til** – behøves kun under krogenes nedadvendte læber.
- Brim anbefales. PETG eller PLA, 4+ perimetre for stærke kroge.

## Montering

1. Sæt de fire kroge ind i SKÅDIS-hullerne og skub pladen helt i bund.
2. Lad pladen glide nedad, så læberne griber bag boardet.
3. Hæng lampen på de to skruehoveder med nøglehullerne og træk den nedad.
