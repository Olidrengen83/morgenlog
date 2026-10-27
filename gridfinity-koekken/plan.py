"""
Planen for de to køkkenskuffer. Ret her og kør `python3 generate.py` igen.

Skuffe: 51 cm bred x 52,5 cm dyb, maks. 6 cm høj  ->  12 x 12 enheder (504 x 504 mm).
Højder: 7 enheder = 49 mm (+ basepladen ≈ 50-52 mm i alt, under de 60 mm).
        Bestikrum er 6 enheder = 42 mm, så det er nemmere at få fat i tingene.

pos = (x fra venstre, y fra bagkanten) i enheder. Bagenden (y=0) er inde i skabet,
forenden (y=12) er ud mod dig.
"""
from gridfinity import BinSpec, KnifeTray, TraySpec

# Hvor langt et stykke din printer kan printe. 6 = 251,5 mm (Bambu/Prusa XL/256 mm-plader).
# Sæt til 5 (209,5 mm) for Prusa MK3/MK4 (250x210) eller Ender 3 (220x220).
MAX_PRINT_UNITS = 6

DRAWER_UNITS = (12, 12)

# --- Skuffe 1: bestik -------------------------------------------------------
# Alle bakker 8 enheder = 56 mm (skeleton-baseplade, så ca. 57 mm i alt).
# Vægge og skillevægge 1,26 mm (3 linjer på P1S).
H = 8
W_IN6 = 6 * 42 - 0.5 - 2 * 1.26          # 248,98 mm indvendigt i en 6-bred bakke
C4 = (W_IN6 - 3 * 1.26) / 4              # 61,3 mm (bruges ikke længere til bestik-lang)
W_IN3 = 3 * 42 - 0.5 - 2 * 1.26          # 122,98 mm indvendigt i en 3-bred bakke
C2 = (W_IN3 - 1.26) / 2                  # 60,9 mm: to rum i en 3x6 (som testbakken)
C3 = (W_IN6 - 2 * 1.26) / 3              # 82,15 mm: tre tværrum i den korte bakke
KORT_L = 165.0                           # længde på tværrummene til kort bestik
W_IN3D = 3 * 42 - 0.5 - 2 * 1.26         # 122,98 mm indvendig dybde i en 6x3
C2K = (W_IN3D - 1.26) / 2                # 60,86 mm: to tværrum i dybden

BESTIK = [
    # Fordeling bagerst (x = 20, 45, 70, 95, 120, 145): 33 · 31 · 31 · 25 · 22 · 22 cm.
    # Forrest (x = 68, 83, 98 … 158): 18 · 18 · 21 · 21 · 21 · 21 · 21 cm.
    # De to 18 cm ligger foran de to 31 cm (31 + 18 = 49 cm), steakknivene foran 25/22/22.
    BinSpec("knivbakke", 4, 12, H, pos=(0, 0),
            knife=KnifeTray(front_x0=68.0),
            label="13 knive i to rækker (6 lange bagerst, 7 korte forrest) + to småtingsrum 59 x 80 mm forrest tv. (Bamix-skær m.m.)"),
    # Brødkniven på 39 cm ligger langs venstre væg og går gennem en slids i skillevæggen.
    BinSpec("redskaber", 2, 12, H, pos=(4, 0), dividers_y=(250.0,),
            divider_slots=((250.0, 9.0, 4.0),), max_units=4,
            label="To rum i fuld højde 81 x 249: piskeris, ostehøvl, lange redskaber · hvidløgspresser, rivejern, proptrækker. Brødkniv 39 cm langs venstre væg gennem slids"),
    # bestik-lang som to 3x6-bakker: "-a" er identisk med testbakken (allerede printet).
    BinSpec("bestik-lang-a", 3, 6, H, pos=(6, 0),
            dividers_x=(C2 + 0.63,), front_notch=True, notch_radius=12,
            notch_xs=(1.26 + C2 / 2, 1.26 + C2 + 1.26 + C2 / 2),
            label="To rum 61 x 249: spiseknive, gafler (= testbakken)"),
    BinSpec("bestik-lang-b", 3, 6, H, pos=(9, 0),
            dividers_x=(C2 + 0.63,), front_notch=True, notch_radius=12,
            notch_xs=(1.26 + C2 / 2, 1.26 + C2 + 1.26 + C2 / 2),
            label="To rum 61 x 249: spiseskeer (også 21 cm), lange teskeer"),
    # bestik-kort som to 6x3-bakker (P1S' udelukkelseszone forhindrer 251 x 251 mm dele).
    # Hver: to tværrum 165 x 61 mm (kort bestik) + et rum 83 x 123 mm.
    BinSpec("bestik-kort-a", 6, 3, H, pos=(6, 6),
            dividers_x=(KORT_L + 0.63,),
            walls=((0.0, C2K, KORT_L, C2K + 1.26),),
            label="Bagerst: teskeer (165 x 61) · kagegafler (165 x 61) · måleskeer (83 x 123)"),
    BinSpec("bestik-kort-b", 6, 3, H, pos=(6, 9),
            dividers_x=(KORT_L + 0.63,),
            walls=((0.0, C2K, KORT_L, C2K + 1.26),),
            label="Forrest: børnebestik (165 x 61) · frit/dessertskeer (165 x 61) · pizzahjul, te-si, småværktøj (83 x 123)"),
]

# Kanal på basepladens 22,5 mm-stribe forrest i skuffen: to lukkede, separate rum à 251,5 mm.
# Forvæggen har et aflangt hul til håndtagets bolthoved (ø10, 37 mm over bunden, 209 mm fra hver side).
# Kanalen er 2 x 251,5 = 503 mm i en 510 mm skuffe, så bolten sidder 205,5 mm fra kanalens yderende.
# Striben er 4,25 mm høj, så boltens centrum er 32,75 mm over kanalens underside.
# Under bunden sidder en tand pr. celle (42 mm deling) med stribens 2:1-profil: 19,5 mm bred i bunden,
# 3,4 mm høj, 33 mm bred ved kanalens bund (rillen er 20,5 mm nederst og 35 mm øverst).
KANAL_W, KANAL_H, KANAL_L = 22.0, 50.0, 251.5
BOLT_Y, BOLT_Z = 209.0 - (510.0 - 2 * KANAL_L) / 2, 37.0 - 4.25
TAND_Y0 = 24.0 - (510.0 - 2 * KANAL_L) / 2          # 20,5 mm: første tand fra kanalens yderende
TAENDER_A = tuple((TAND_Y0 + i * 42.0, 2.0, 19.0, 19.5, 3.4) for i in range(6))
TAENDER_B = tuple((KANAL_L - y, x0, x1, wy, h) for (y, x0, x1, wy, h) in TAENDER_A)
EXTRA = [
    TraySpec("kanal-a", width=KANAL_W, length=KANAL_L, height=KANAL_H, floor=2.0, end_notch_radius=0,
             x0_slots=((BOLT_Y, BOLT_Z, 16.0, 26.0),), teeth=TAENDER_A,
             label="Forreste kanal, venstre, lukket rum med hul til bolthoved og profilerede tænder (spisepinde / grillspyd)"),
    TraySpec("kanal-b", width=KANAL_W, length=KANAL_L, height=KANAL_H, floor=2.0, end_notch_radius=0,
             x0_slots=((KANAL_L - BOLT_Y, BOLT_Z, 16.0, 26.0),), teeth=TAENDER_B,
             label="Forreste kanal, højre, lukket rum. Print to sæt: ét til hver skuffe"),
]

# --- Skuffe 2: ruller, poser og småting ------------------------------------
# Prioritet: det daglige forrest eller i kolonner, hvor æskens ende griber ved forkanten.
# ISTAD-æskerne (29,5 / 23 / 19 x 7,5 cm) ligger på langs i 2 enheder brede kolonner.
RULLER = [
    BinSpec("pynt", 4, 2, H, pos=(0, 0),
            label="BAGERST, sjældent: fødselsdagsflag, parasoller, kagelys (164 x 80 mm)"),
    BinSpec("frit-4x2", 4, 2, H, pos=(0, 2),
            label="Frit rum 164 x 80 mm bagerst (reserve, fx fyrfadslys eller servietringe)"),
    BinSpec("ruller", 4, 8, H, pos=(0, 4),
            label="Film, sølvpapir, cellofan og fryseposer på rulle på langs (164 x 332 mm) – gribes i forkanten"),
    BinSpec("termometre", 2, 4, H, pos=(4, 0),
            label="Bagerst: stegetermometer, trådtermometer, snor (80 x 164 mm)"),
    BinSpec("istad-store", 2, 8, H, pos=(4, 4),
            label="ISTAD 29,5 cm på langs (80 x 332 mm)"),
    BinSpec("lange-ting", 2, 6, H, pos=(6, 0),
            label="Bagerst: trægafler, sushi-måtte, poser på rulle (80 x 248 mm). Sugerør ligger i kanalen forrest"),
    BinSpec("istad-mellem", 2, 6, H, pos=(6, 6),
            label="ISTAD 23 cm på langs (80 x 248 mm)"),
    BinSpec("smaating", 4, 2, H, pos=(8, 0), dividers_x=(81.0,),
            label="Bagerst, to rum 80 x 80: tandstikker + barberblade · tændstikker + fødselsdagslys"),
    BinSpec("istad-smaa", 2, 6, H, pos=(8, 2),
            label="ISTAD 19 cm på langs (80 x 248 mm), ender bag papiret"),
    BinSpec("poseklemmer", 2, 4, H, pos=(10, 2),
            label="Alle poseklemmer (13,5 / 10,5 / 5 cm) i ét rum 80 x 164 mm, fuld højde"),
    BinSpec("elastikker", 1, 2, H, pos=(10, 6),
            label="Elastikker, løse (37 x 80 mm)"),
    BinSpec("frit-1x2", 1, 2, H, pos=(11, 6),
            label="Frit smalt rum 37 x 80 mm (fx tændstikæske, snor, blyant)"),
    BinSpec("mellemlaegspapir", 4, 4, H, pos=(8, 8),
            label="FORREST: mellemlægspapir 15 x 12,5 cm (164 x 164 mm), plads til tændstikker ved siden af"),
]

DRAWERS = {
    "skuffe1-bestik": BESTIK,
    "skuffe2-ruller-poser": RULLER,
}
