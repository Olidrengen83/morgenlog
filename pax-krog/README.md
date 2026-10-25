# Krog til PAX-skuffefront

En krog, der hænges over den øverste kant af en Komplement-skuffefront (17 mm),
så børnenes tøj fra i dag kan hænge klar til i morgen.

## Filer

| Fil | Hvad |
|---|---|
| `pax_krog.stl` | Klar til slicer. 55,8 × 35,2 × 25 mm, ca. 14 g PLA. |
| `pax_krog.scad` | Parametrisk OpenSCAD-udgave, ret målene øverst. |
| `lav_krog.py` | Python-udgave der har lavet STL'en (shapely + trimesh). |
| `pax_krog_profil.png` | Tværsnit med fronten tegnet ind. |
| `pax_krog_3d.png` | 3D-visning. |

## Sådan er den tænkt

- Slidsen er 17,4 mm: 17 mm front + 0,4 mm luft. Sidder den for løst, sæt `SLOER`
  til 0,2. Sidder den for stramt, 0,6.
- Benet på forsiden er 32 mm, benet inde i skuffen 18 mm. Det inderste ben er kort,
  så det ikke rammer tøjet i skuffen.
- Krogen rager 30 mm ud og hælder let opad, så tøjet glider ind mod fronten.
  Spidsen er 16 mm høj og læner lidt indad, så bukser og trøjer ikke hopper af.
- Oven på fronten ligger 3,2 mm plast. Tjek at der er mindst 4 mm luft mellem
  skuffefrontens overkant og hylden over, ellers kan skuffen ikke lukkes.

## Print

- Læg den **på siden** (det er sådan STL'en er orienteret). Så ligger lagene langs
  krogen, og den knækker ikke i hjørnet.
- 3 vægge (perimeters), 25–40 % infill, lag 0,2 mm. PLA eller PETG; PETG tåler lidt
  mere bøjning hvis slidsen er stram.
- Ingen support nødvendig.
- Sæt evt. et stykke filt eller en strimmel tape på indersiden af det forreste ben,
  hvis du er bange for mærker i lakken.
