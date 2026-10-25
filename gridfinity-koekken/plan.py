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
C4 = (W_IN6 - 3 * 1.26) / 4              # 61,3 mm: fire rum i forreste bakke
C3 = (W_IN6 - 2 * 1.26) / 3              # 82,15 mm: tre tværrum i bageste bakke
STORE_SKEER_B = 75.0                     # bredde på rummet til 21 cm-skeerne

BESTIK = [
    # Fordeling bagerst (x = 20, 45, 70, 95, 120, 145): 33 · 31 · 31 · 25 · 22 · 22 cm.
    # Forrest (x = 68, 83, 98 … 158): 18 · 18 · 21 · 21 · 21 · 21 · 21 cm.
    # De to 18 cm ligger foran de to 31 cm (31 + 18 = 49 cm), steakknivene foran 25/22/22.
    BinSpec("knivbakke", 4, 12, H, pos=(0, 0),
            knife=KnifeTray(front_x0=68.0),
            label="13 knive i to rækker (6 lange bagerst, 7 korte forrest) + to småtingsrum 59 x 80 mm forrest tv. (Bamix-skær m.m.)"),
    # Brødkniven på 39 cm ligger langs venstre væg og går gennem en slids i første skillevæg.
    BinSpec("redskaber", 2, 12, H, pos=(4, 0), dividers_y=(200.0, 400.0),
            divider_slots=((200.0, 9.0, 4.0),),
            label="Tre rum i fuld højde: 81 x 199 (piskeris, ostehøvl, spyd), 81 x 199 (værktøj), 81 x 100 (måleskeer). Brødkniv 39 cm langs venstre væg gennem slids i skillevæg 1"),
    BinSpec("bestik-kort", 6, 6, H, pos=(6, 6),
            dividers_x=(STORE_SKEER_B + 0.63,),
            walls=((STORE_SKEER_B + 1.26, C3, W_IN6, C3 + 1.26),
                   (STORE_SKEER_B + 1.26, 2 * C3 + 1.26, W_IN6, 2 * C3 + 2.52)),
            label="Tv.: store skeer 21 cm (75 x 249) · th. tre tværrum 172 x 82: teskeer, børnebestik, kagegafler"),
    BinSpec("bestik-lang", 6, 6, H, pos=(6, 0),
            dividers_x=(C4 + 0.63, 2 * C4 + 1.89, 3 * C4 + 3.15),
            rails=((3 * C4 + 3.78, W_IN6, 0.0, W_IN6, 22.0),),
            front_notch=True, notch_radius=12,
            notch_xs=tuple(1.26 + C4 / 2 + i * (C4 + 1.26) for i in range(4)),
            label="Fire rum 61 x 249: spiseknive, gafler, spiseskeer, spisepinde (nederst) med løs indsats til lange teskeer ovenpå"),
]

# Løse indsatser uden Gridfinity-fod
EXTRA = [
    TraySpec("teske-indsats", width=C4 - 0.8, length=W_IN6 - 0.8, height=56 - 22,
             label="Øverste lag i rum 4 i bestik-lang: lange teskeer. Hviler på lister 22 mm over bunden, spisepinde nedenunder"),
]

# --- Skuffe 2: ruller, poser og småting ------------------------------------
# Prioritet: det daglige forrest eller i kolonner, hvor æskens ende griber ved forkanten.
# ISTAD-æskerne (29,5 / 23 / 19 x 7,5 cm) ligger på langs i 2 enheder brede kolonner.
RULLER = [
    BinSpec("pynt-ringe", 4, 4, H, pos=(0, 0),
            label="BAGERST, sjældent: ringe til glas, fødselsdagsflag, parasoller, lys (164 x 164 mm)"),
    BinSpec("ruller", 4, 8, H, pos=(0, 4),
            label="Film, sølvpapir, cellofan og fryseposer på rulle på langs (164 x 332 mm) – gribes i forkanten"),
    BinSpec("termometre", 2, 4, H, pos=(4, 0),
            label="Bagerst: stegetermometer, trådtermometer, snor (80 x 164 mm)"),
    BinSpec("istad-store", 2, 8, H, pos=(4, 4),
            label="ISTAD 29,5 cm på langs (80 x 332 mm)"),
    BinSpec("lange-ting", 2, 6, H, pos=(6, 0),
            label="Bagerst: trægafler, papirsugerør, sushi-måtte (80 x 248 mm)"),
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
