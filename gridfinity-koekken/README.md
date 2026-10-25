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

* **`stl/`** – printklare STL-filer (7 dele til bestikskuffen inkl. den løse teske-indsats, 13 til rulle/pose-skuffen). Se `printliste.md`.
* **`plan.py`** – selve planen: hvilke bakker, hvor store, hvor de står, skillevægge, knivbakke-parametre.
* **`gridfinity.py`** – lille Gridfinity-bibliotek (fodprofil 0,8 / 1,8 / 2,15 mm, 42 mm pitch, 4 mm hjørner).
* **`generate.py`** – laver STL, `layout.svg` og `printliste.md`. **`preview.py`** laver PNG-billederne.

## Forudsætninger

1. **Basepladen er 12 × 12 enheder** (504 × 504 mm) af skeleton-typen, så bakkerne står reelt på skuffebunden.
   Hvis din baseplade er anderledes, ret `DRAWER_UNITS` i `plan.py`.
2. **Højde.** Bestikskuffens bakker er 8 enheder = 56 mm, ca. 57 mm i alt. Knivene står lodret og den
   bredeste klinge (santoku, 45 mm) ender i ca. 53 mm. Alt under de 60 mm.
3. **Printer: Bambu P1S** (256 × 256 mm). `MAX_PRINT_UNITS = 6` deler lange bakker i stykker på højst 251,5 mm.
   Delte bakker (`-a`, `-b`) har åbne ender mod hinanden og låses sammen af basepladen.
4. **Vægge** er 1,26 mm = 3 linjer à 0,42 mm, både ydervægge og skillevægge. Stift nok til 56 mm høje vægge, og
   tyndere end det bliver svajende på de lange stræk.

### Mål der er lagt til grund (bestikskuffen)

| Ting | Mål | Plads |
|---|---|---|
| Køkkenknive | 33 · 31 · 31 · 25 · 22 · 22 cm (lange) og 5 × 21 + 2 × 18 cm (korte) | knivbakke 4×12, 500 mm indvendigt |
| Santoku-klinge, ryg til æg | 45 mm | lodret slids, bund 7 mm over skuffebunden |
| Bamix-skær | ø36 mm, 4 stk. | småtingsrum 59 × 80 mm forrest i knivbakken |
| Store skeer | 21 cm | rum 75 × 249 mm |
| Spisepinde og lange teskeer | ca. 24 cm | rum 61 × 249 mm i to lag |
| Spiseknive, gafler, spiseskeer | 1,5 enhed brede | rum 61 × 249 mm |
| Teskeer, børnebestik, kagegafler | korte | tværrum 172 × 82 mm |

## Skuffe 1 – bestik

Fire bakker. Bagkanten er øverst på tegningen; forkanten (mod dig) nederst. De to 6×6-bakker har samme
fodaftryk og kan byttes om når som helst, uden nyt print. Prioriteten er udnyttelse, ikke udseende:
alle rum er i fuld højde, og alt der kan deles med en skillevæg i stedet for to bakkevægge, er det.

* **Knivbakke 4×12** (164 × 500 mm indvendigt), printes i to halvdele.
  * Bagerst: tre ribber med 6 lodrette slidser i 25 mm deling til de lange knive, spidserne mod bagvæggen.
    33, 31 og 31 cm i venstre side, 22, 25 og 22 cm i højre.
  * Forrest: to ribber med 7 slidser i 15 mm deling, skubbet mod højre, til de fem steakknive og to urteknive.
    Spidserne vender bagud og ligger bag håndtagene på 22/25 cm-knivene.
  * Forrest til venstre, foran de lange knives håndtag: to småtingsrum på 59 × 80 mm. Bamix-skærene i det ene,
    det andet frit.
  * Slidserne er 4 mm brede med rund bund 7 mm over skuffebunden. Ret `KnifeTray(...)` i `plan.py`.
* **Redskaber 2×12** (81 × 500 mm indvendigt), printes i to halvdele, tre rum i fuld højde:
  199 mm (piskeris, ostehøvl, grillspyd, lange redskaber), 199 mm (hvidløgspresser, rivejern, pizzahjul, proptrækker)
  og 100 mm (måleskeer, småting).
* **Bestik-lang 6×6** (bagerst): fire rum på 61 × 249 mm med greb-hak: spiseknive, gafler, spiseskeer og
  spisepinde. Spisepinde-rummet har to lister 22 mm over bunden, og den løse **teske-indsats** (60 × 248 × 34 mm)
  hviler på dem med de lange teskeer, mens spisepindene ligger nedenunder. Indsatsen har greb-hak i begge ender.
* **Bestik-kort 6×6** (forrest): til venstre et rum på 75 × 249 mm til de store skeer på 21 cm. Til højre tre tværrum på
  172 × 82 mm til teskeer, børnebestik og kagegafler.

## Skuffe 2 – ruller, poser og småting (foreløbig plan, revideres)

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
* Vægge er 1,26 mm, gulvet 6 mm over fodens bund. Alt kan vaskes i hånden; PETG tåler opvaskemaskine bedre.
* Print de små 3×3-bakker først og tjek at de passer i din baseplade, før du printer de store.

## Generér igen

```bash
pip install manifold3d trimesh numpy matplotlib
python3 generate.py            # STL + layout.svg + printliste.md
python3 generate.py --max 5    # kortere stykker til 250/220 mm-plader
python3 generate.py --only knivbakke
python3 preview.py             # PNG-billeder i preview/
```
