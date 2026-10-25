# Gridfinity-indsatser til køkkenskufferne

Printbare skuffeindsatser (bakker uden stable-læbe) til to køkkenskuffer på
**51 × 52,5 cm, maks. 6 cm høje**, oven på den Gridfinity-baseplade der allerede
er printet. Alt er genereret fra `plan.py`, så mål og inddeling kan rettes og
STL-filerne laves igen på få sekunder.

![Layout](preview/layout.png)

| | |
|---|---|
| ![Skuffe 1](preview/skuffe1-bestik.png) | ![Skuffe 2](preview/skuffe2-ruller-poser.png) |

## Hvad er lavet

* **`stl/`** – 22 færdige STL-filer (12 til bestikskuffen, 10 til rulle/pose-skuffen). Se `printliste.md`.
* **`plan.py`** – selve planen: hvilke bakker, hvor store, hvor de står, skillevægge, knivbakke-parametre.
* **`gridfinity.py`** – lille Gridfinity-bibliotek (fodprofil 0,8 / 1,8 / 2,15 mm, 42 mm pitch, 4 mm hjørner).
* **`generate.py`** – laver STL, `layout.svg` og `printliste.md`. **`preview.py`** laver PNG-billederne.

## Forudsætninger (tjek disse først)

1. **Basepladen er 12 × 12 enheder** (504 × 504 mm). Der er 6 mm til overs i bredden og 21 mm i dybden.
   Hvis din baseplade er anderledes, ret `DRAWER_UNITS` i `plan.py`.
2. **Højde.** Bakkerne er 7 enheder = 49 mm (bestikrummene 6 enheder = 42 mm). Oven på en
   almindelig baseplade giver det ca. 50–52 mm i alt, altså under de 60 mm. Gå ikke op på 8 enheder (56 mm +).
3. **Printerplade.** `MAX_PRINT_UNITS = 6` deler lange bakker i stykker på højst 251,5 mm
   (passer på 256 mm-plader som Bambu X1/P1/A1). Har du en Prusa MK3/MK4 (250 × 210) eller
   Ender 3 (220 × 220), så sæt den til **5** (209,5 mm) og kør `python3 generate.py` igen.
   Delte bakker (`-a`, `-b`) har åbne ender mod hinanden og låses sammen af basepladen.

### Mål jeg har skønnet ud fra billederne – mål efter, før du printer

| Ting | Skal kunne være i | Bakke |
|---|---|---|
| Længste køkkenkniv (samlet længde) | ≤ 374 mm | `knivbakke` 4×9 |
| Bagepapir- og folie-æsker | ≤ 500 mm lange, to æsker ≤ 122 mm tilsammen i bredden | `ruller` 3×12 |
| ISTAD-æsker (grøn og rød) | ≤ 248 × 122 mm, ≤ 43 mm høje | `fryseposer-store/-smaa` 6×3 |
| Mellemlægspapir-æske (12 × 14,5 cm ark) | ≤ 152 × 164 mm | `papir-klemmer`, venstre rum |
| Poser på rulle, trægafler, sugerør, sushi-måtte | ≤ 248 mm lange | `lange-ting` 6×2 |
| Stegetermometer | ≤ 164 mm | `termometre` 3×4 |
| Ringe til glas | ≤ 122 mm i diameter | `ringe` 3×3 |

Passer noget ikke, så ret tallene i `plan.py` (fx `dividers_x=(152.0,)` eller `units_y`).

## Skuffe 1 – bestik

Bagkanten er øverst på tegningen; forkanten (mod dig) nederst.

* **Knivbakke 4×9** til venstre: 10 skrå slidser (25° hældning, 15 mm deling) i tre ribber.
  Spidserne vender bagud, så du altid griber i et håndtag. Den forreste ribbe har kun slidser i
  hver anden plads, så håndtagene forskydes og ikke ligger oven i hinanden. Trin-ribber forrest
  løfter håndtagene, så de er nemme at tage. Ret `KnifeTray(slots=…, pitch=…, lean_deg=…)` i `plan.py`.
* **Redskaber 2×9** (80 × 374 mm indvendigt): piskeris, ostehøvl, grillspyd, spisepinde og de
  lange sorte redskaber der i dag ligger løst i siden.
* **Værktøj 3×3** og **Måleskeer 3×3** forrest til venstre: hvidløgspresser, rivejern, pizzahjul,
  proptrækker, te-si, måleskeer.
* **Seks bestikrum 2×6** (80 × 248 mm indvendigt, 42 mm høje med greb-hak i forkanten).
  Forrest det der bruges mest: **gafler, spiseknive, spiseskeer**. Bagved **teskeer,
  børnebestik/dessert, servering/blandet**. Spiseknive på 24 cm kan ligge fladt.

## Skuffe 2 – ruller, poser og småting

* **Ruller 3×12** langs venstre side (122 × 500 mm indvendigt): bagepapir og folie/film side om side.
  Så lang at selv en 45 cm-æske kan være der.
* **Fryseposer store 6×3** og **Fryseposer små 6×3**: de to ISTAD-æsker.
* **Lange ting 6×2**: poser på rulle, trægafler, papirsugerør, sushi-måtte og den lille ISTAD 0,4 L-æske.
* **Papir | klemmer 6×4** med skillevæg: mellemlægspapir-æsken til venstre (152 mm), alle
  poseklemmer til højre (94 mm).
* Højre kolonne: **Ringe 3×3**, **Elastikker 3×3** (smid pap-æsken ud, hæld elastikkerne løst i,
  snoren kan ligge ovenpå), **Termometre 3×4** (plus tændstikker), **Småting 3×2**
  (tandstikker, barberblade, fødselsdagslys).
* Gaveposerne med gule blade og festtingene hører nok ikke til i køkkenskuffen – der er ikke sat plads af til dem.

## Print

* PLA eller PETG, 0,2 mm lag, 3 perimetre, 10–15 % infill, ingen support (filerne står rigtigt).
  Bunden er massiv i modellen, så sliceren fylder den med infill; vægten i `printliste.md` er regnet
  massivt og er derfor i overkanten (ca. 4,2 kg i alt for det hele).
* Vægge er 1,6 mm, gulvet 6 mm over fodens bund. Alt kan vaskes i hånden; PETG tåler opvaskemaskine bedre.
* Print de små 3×3-bakker først og tjek at de passer i din baseplade, før du printer de store.

## Generér igen

```bash
pip install manifold3d trimesh numpy matplotlib
python3 generate.py            # STL + layout.svg + printliste.md
python3 generate.py --max 5    # kortere stykker til 250/220 mm-plader
python3 generate.py --only knivbakke
python3 preview.py             # PNG-billeder i preview/
```
