"""Thumbnails de A Colônia Perdida de Roanoke (estilo ilustrado, tom misterioso).
Rodar da raiz: python videos/colonia-roanoke/thumb/thumb.py"""
import sys, os
sys.path.insert(0, os.getcwd())
from engine import *
from ilustrado import *

OUT = os.path.dirname(os.path.abspath(__file__))


def a(c, t):  # o poste CROATOAN na paliçada, ao entardecer
    cena_ilha(c, t, "crepusculo", agua=False, seed=57)
    palicada_i(c, t, 700, 1950, 900, 300, portao=1500, seed=7)
    poste_entalhado(c, t, 1560, 1000, 760, 190, "CROATOAN")
    rglow(c, 1560, 600, 360, (1.0, 0.85, 0.5), 0.3)
    nevoa_i(c, t, 940, 0.3)
    thumb_close(c, t, 380, 1560, 2.4, "shocked", "point_r", 0.8)
    thumb_texto(c, ["115", "SUMIRAM"], 1010, 120, 170, alinhamento="c")
    thumb_selo(c, "1590", 1000, 560, 64)


def b(c, t):  # a palavra no poste ocupando o quadro
    cena_ilha(c, t, "noite", agua=True, seed=87)
    poste_entalhado(c, t, 1600, 1060, 960, 230, "CROATOAN")
    rglow(c, 1600, 560, 420, (1.0, 0.85, 0.5), 0.28)
    nevoa_i(c, t, 940, 0.35)
    thumb_close(c, t, 380, 1560, 2.4, "worried", "think", 0.8)
    thumb_texto(c, ["SÓ RESTOU", "UMA PALAVRA"], 960, 120, 140, cores=[(0.98, 0.96, 0.90), (1.0, 0.80, 0.40)])
    thumb_selo(c, "115 PESSOAS SUMIRAM", 960, 900, 50)


for nome, fn in (("roanoke_thumb_A", a), ("roanoke_thumb_B", b)):
    print(salvar_thumb(lambda c, t, fn=fn: fn(c, t), f"{OUT}/{nome}.png", tom="misterioso"))
