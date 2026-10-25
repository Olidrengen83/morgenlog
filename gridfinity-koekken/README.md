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

* **`stl/`** – 26 færdige STL-filer (13 til bestikskuffen, 13 til rulle/pose-skuffen). Se `printliste.md`.
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

### Mål der er lagt til grund

Opmålte (fra dig) og skønnede mål. Ret i `plan.py`, hvis noget ikke passer.

| Ting | Mål | Skal kunne være i | Bakke |
|---|---|---|---|
| Længste køkkenkniv | 33 cm | ≤ 374 mm | `knivbakke` 4×9 |
| Store skeer | 21 cm | ≤ 248 mm | `store-skeer` 6×2 og `skeer` 2×6 |
| Sølvpapir- og film-æsker | 31 cm | ≤ 332 mm lange, to æsker ≤ 122 mm tilsammen i bredden (skøn: mål bredden) | `ruller` 8×3 |
| ISTAD stor / mellem / lille | 29,5 / 23 / 19 × 7,5 cm | ≤ 332 / 248 / 206 × 80 mm | `fryseposer-store/-mellem/-smaa` |
| Mellemlægspapir-æske | 15 × 12,5 cm | ≤ 164 × 130 mm | `papir-taendstikker`, bagerste rum |
| Poser på rulle, trægafler, sugerør, sushi-måtte | skøn ≤ 24 cm | ≤ 248 mm | `lange-ting` 6×2 |
| Stegetermometer | skøn ≤ 16 cm | ≤ 164 mm | `termometre` 4×3 |
| Ringe til glas | skøn ≤ 12 cm | ≤ 122 mm i diameter | `ringe` 3×3 |

Æskernes højde skal være under 43 mm for at ligge under kanten (de må stikke op til ca. 55 mm i alt).

## Skuffe 1 – bestik

Bagkanten er øverst på tegningen; forkanten (mod dig) nederst.

* **Knivbakke 4×9** til venstre: 10 skrå slidser (25° hældning, 15 mm deling) i tre ribber.
  Spidserne vender bagud, så du altid griber i et håndtag. Den forreste ribbe har kun slidser i
  hver anden plads, så håndtagene forskydes og ikke ligger oven i hinanden. Trin-ribber forrest
  løfter håndtagene, så de er nemme at tage. Ret `KnifeTray(slots=…, pitch=…, lean_deg=…)` i `plan.py`.
* **Redskaber 2×9** (80 × 374 mm indvendigt): piskeris, ostehøvl, grillspyd og de
  lange sorte redskaber der i dag ligger løst i siden.
* **Værktøj 3×3** og **Måleskeer 3×3** forrest til venstre: hvidløgspresser, rivejern, pizzahjul,
  proptrækker, te-si, måleskeer.
* **Store skeer 6×2** bagerst på tværs (248 × 80 mm): skeerne på 21 cm og serveringsbestik.
* **Teskeer, børnebestik, kagegafler 2×4** (80 × 164 mm): korte rum til det korte bestik.
* **Gafler, spiseknive, spiseskeer 2×6** forrest (80 × 248 mm). Knivrummet har en skillevæg på langs,
  så der er en smal stribe på 26 × 248 mm til **spisepinde** og 53 mm til knivene. Alle bestikrum er 42 mm høje med greb-hak i forkanten.

## Skuffe 2 – ruller, poser og småting

* **Ruller 8×3** bagerst (332 × 122 mm indvendigt): sølvpapir og film side om side.
* **Papir | tændstikker 4×5** bagerst til højre med skillevæg: mellemlægspapiret i det bageste rum
  (164 × 130 mm), tændstikker og snor i det forreste (164 × 73 mm).
* **Fryseposer store 8×2, mellem 6×2, små 5×2**: én bakke pr. ISTAD-æske, alle 80 mm brede.
* **Lange ting 6×2**: poser på rulle, trægafler, papirsugerør, sushi-måtte.
* **Småting 4×2** (tandstikker, barberblade, fødselsdagslys) og **Elastikker 3×2** (smid pap-æsken ud).
* Forrest: **Termometre 4×3**, **Ringe 3×3** og **Poseklemmer 5×3** (206 × 122 mm til alle klemmerne).
* Gaveposerne med gule blade og festtingene hører nok ikke til i køkkenskuffen – der er ikke sat plads af til dem.

## Print

* PLA eller PETG, 0,2 mm lag, 3 perimetre, 10–15 % infill, ingen support (filerne står rigtigt).
  Bunden er massiv i modellen, så sliceren fylder den med infill; vægten i `printliste.md` er regnet
  massivt og er derfor i overkanten (se totalen nederst i `printliste.md`).
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
