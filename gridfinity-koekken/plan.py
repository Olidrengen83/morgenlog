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
            label="Køkkenknive (10 skrå slidser, spidser bagud)"),
    BinSpec("redskaber", 2, 9, 7, pos=(4, 0),
            label="Piskeris, ostehøvl, grillspyd, spisepinde, lange paletknive"),
    BinSpec("vaerktoej", 3, 3, 7, pos=(0, 9),
            label="Hvidløgspresser, rivejern, pizzahjul, proptrækker, te-si"),
    BinSpec("maaleskeer", 3, 3, 7, pos=(3, 9),
            label="Måleskeer, små dimser"),
    # Bagerste række bestik (2 x 6 enheder = 80 x 248 mm indvendigt)
    BinSpec("teskeer", 2, 6, 6, pos=(6, 0), front_notch=True, label="Teskeer"),
    BinSpec("boernebestik", 2, 6, 6, pos=(8, 0), front_notch=True,
            label="Børnebestik, dessertknive, træ-spatler"),
    BinSpec("servering", 2, 6, 6, pos=(10, 0), front_notch=True,
            label="Serveringsskeer, blandet bestik"),
    # Forreste række bestik (det der bruges mest, nærmest dig)
    BinSpec("gafler", 2, 6, 6, pos=(6, 6), front_notch=True, label="Gafler"),
    BinSpec("knive", 2, 6, 6, pos=(8, 6), front_notch=True, label="Spiseknive"),
    BinSpec("skeer", 2, 6, 6, pos=(10, 6), front_notch=True, label="Spiseskeer"),
]

RULLER = [
    BinSpec("ruller", 3, 12, 7, pos=(0, 0),
            label="Bagepapir + folie/film (to æsker side om side, indv. 122 x 500 mm)"),
    BinSpec("fryseposer-store", 6, 3, 7, pos=(3, 0),
            label="ISTAD fryseposer 4,5 / 6 L (grøn æske)"),
    BinSpec("ringe", 3, 3, 7, pos=(9, 0),
            label="Gummiringe og plastringe til glas"),
    BinSpec("fryseposer-smaa", 6, 3, 7, pos=(3, 3),
            label="ISTAD fryseposer 1 / 2 L (rød æske)"),
    BinSpec("elastikker", 3, 3, 7, pos=(9, 3),
            label="Elastikker (løse, uden pap-æske) + snor"),
    BinSpec("lange-ting", 6, 2, 7, pos=(3, 6),
            label="Poser på rulle, trægafler, sugerør, sushi-måtte, ISTAD 0,4 L"),
    BinSpec("termometre", 3, 4, 7, pos=(9, 6),
            label="Stegetermometer, trådtermometer, tændstikker"),
    BinSpec("papir-klemmer", 6, 4, 7, pos=(3, 8), dividers_x=(152.0,),
            label="Venstre: mellemlægspapir (152 x 164 mm) · højre: poseklemmer (94 x 164 mm)"),
    BinSpec("smaating", 3, 2, 7, pos=(9, 10),
            label="Tandstikker, barberblade, fødselsdagslys"),
]

DRAWERS = {
    "skuffe1-bestik": BESTIK,
    "skuffe2-ruller-poser": RULLER,
}
