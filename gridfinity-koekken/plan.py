"""
Planen for de to køkkenskuffer. Ret her og kør `python3 generate.py` igen.

Skuffe: 51 cm bred x 52,5 cm dyb, maks. 6 cm høj  ->  12 x 12 enheder (504 x 504 mm).
Højder: 7 enheder = 49 mm (+ basepladen ≈ 50-52 mm i alt, under de 60 mm).
        Bestikrum er 6 enheder = 42 mm, så det er nemmere at få fat i tingene.

pos = (x fra venstre, y fra bagkanten) i enheder. Bagenden (y=0) er inde i skabet,
forenden (y=12) er ud mod dig.
"""
from gridfinity import BinSpec, KnifeTray

# Hvor langt et stykke din printer kan printe. 6 = 251,5 mm (Bambu/Prusa XL/256 mm-plader).
# Sæt til 5 (209,5 mm) for Prusa MK3/MK4 (250x210) eller Ender 3 (220x220).
MAX_PRINT_UNITS = 6

DRAWER_UNITS = (12, 12)

BESTIK = [
    BinSpec("knivbakke", 4, 9, 7, pos=(0, 0), knife=KnifeTray(),
            label="Køkkenknive op til 33 cm (10 skrå slidser, spidser bagud)"),
    BinSpec("redskaber", 2, 9, 7, pos=(4, 0),
            label="Piskeris, ostehøvl, grillspyd, lange paletknive"),
    BinSpec("vaerktoej", 3, 3, 7, pos=(0, 9),
            label="Hvidløgspresser, rivejern, pizzahjul, proptrækker, te-si"),
    BinSpec("maaleskeer", 3, 3, 7, pos=(3, 9),
            label="Måleskeer, små dimser"),
    # Bagerst: lang bakke på tværs til de store skeer (21 cm) og serveringsbestik
    BinSpec("store-skeer", 6, 2, 6, pos=(6, 0), front_notch=True,
            label="Store skeer (21 cm) og serveringsbestik, ligger på tværs (248 x 80 mm)"),
    # Små rum (80 x 164 mm) til det korte bestik
    BinSpec("teskeer", 2, 4, 6, pos=(6, 2), front_notch=True, label="Teskeer"),
    BinSpec("boernebestik", 2, 4, 6, pos=(8, 2), front_notch=True, label="Børnebestik"),
    BinSpec("kagegafler", 2, 4, 6, pos=(10, 2), front_notch=True,
            label="Kagegafler, dessertskeer"),
    # Forrest: det der bruges mest (80 x 248 mm, spiseknive på 24 cm kan ligge fladt)
    BinSpec("gafler", 2, 6, 6, pos=(6, 6), front_notch=True, label="Gafler"),
    BinSpec("knive-spisepinde", 2, 6, 6, pos=(8, 6), front_notch=True, dividers_x=(27.0,),
            notch_x=1.6 + 27 + 26, notch_radius=12,
            label="Venstre stribe: spisepinde (26 x 248 mm) · højre: spiseknive (53 x 248 mm)"),
    BinSpec("skeer", 2, 6, 6, pos=(10, 6), front_notch=True, label="Spiseskeer"),
]

# ISTAD-æskerne er 29,5 / 23 / 19 cm lange og 7,5 cm brede -> 2 enheder brede (80 mm indv.)
RULLER = [
    BinSpec("ruller", 8, 3, 7, pos=(0, 0),
            label="Sølvpapir + film, 31 cm æsker side om side (indv. 332 x 122 mm)"),
    BinSpec("papir-taendstikker", 4, 5, 7, pos=(8, 0), dividers_y=(130.0,),
            label="Bagerst: mellemlægspapir 15 x 12,5 cm (164 x 130 mm) · forrest: tændstikker, snor (164 x 73 mm)"),
    BinSpec("fryseposer-store", 8, 2, 7, pos=(0, 3),
            label="ISTAD 29,5 cm (indv. 332 x 80 mm)"),
    BinSpec("fryseposer-mellem", 6, 2, 7, pos=(0, 5),
            label="ISTAD 23 cm (indv. 248 x 80 mm)"),
    BinSpec("lange-ting", 6, 2, 7, pos=(6, 5),
            label="Poser på rulle, trægafler, sugerør, sushi-måtte (indv. 248 x 80 mm)"),
    BinSpec("fryseposer-smaa", 5, 2, 7, pos=(0, 7),
            label="ISTAD 19 cm (indv. 206 x 80 mm)"),
    BinSpec("smaating", 4, 2, 7, pos=(5, 7),
            label="Tandstikker, barberblade, fødselsdagslys"),
    BinSpec("elastikker", 3, 2, 7, pos=(9, 7),
            label="Elastikker (løse, uden pap-æske)"),
    BinSpec("termometre", 4, 3, 7, pos=(0, 9),
            label="Stegetermometer, trådtermometer (indv. 164 x 122 mm)"),
    BinSpec("ringe", 3, 3, 7, pos=(4, 9),
            label="Gummiringe og plastringe til glas"),
    BinSpec("poseklemmer", 5, 3, 7, pos=(7, 9),
            label="Alle poseklemmer (indv. 206 x 122 mm)"),
]

DRAWERS = {
    "skuffe1-bestik": BESTIK,
    "skuffe2-ruller-poser": RULLER,
}
