"""Thumbnails de Kaspar Hauser (estilo ilustrado, tom misterioso).
Rodar da raiz: python videos/kaspar-hauser/thumb/thumb.py"""
import sys, os
sys.path.insert(0, os.getcwd())
from engine import *
from ilustrado import *

OUT = os.path.dirname(os.path.abspath(__file__))


def a(c, t):  # o rapaz no quarto escuro, com o cavalinho de madeira
    cela_baixa(c, t, "noite", feixe=1.0, teto=300)
    rglow(c, 1450, 700, 420, (1.0, 0.85, 0.55), 0.25)
    boneco(c, t, 1450, 1000, 1.25, poses=((0, "slump"),), exprs=((0, "worried"),), look=-0.3, fid=7,
           **dict(KASPAR, chapeu=None))
    c.save(); c.translate(1770, 990); cavalinho_i(c, 0.85); c.restore()
    thumb_close(c, t, 380, 1560, 2.4, "shocked", "point_r", 0.8)
    thumb_texto(c, ["16 ANOS", "NO ESCURO"], 1170, 130, 150, cores=[(0.98, 0.96, 0.90), (1.0, 0.80, 0.40)])
    thumb_selo(c, "QUEM ERA ELE?", 1050, 470, 56)


def b(c, t):  # o bilhete em escrita de espelho
    luz("vela")
    interior(c, t, "madeira", "madeira", "reta", jx=1750, raio=False)
    c.save(); c.translate(1300, 640); c.rotate(0.05); c.scale(1.05, 1.05)
    bilhete_espelho(c, t, ["Hauser vai poder contar", "como eu sou e de onde venho.", "Meu nome:  M. L. Ö."], w=860, size=56, espelho=1.0)
    c.restore()
    c.save(); c.translate(1720, 920); bolsa_seda(c, 1.1); c.restore()
    rglow(c, 1300, 640, 500, (1.0, 0.85, 0.55), 0.18)
    thumb_close(c, t, 380, 1560, 2.4, "shocked", "point_r", 0.8)
    thumb_texto(c, ["ESCRITO AO", "CONTRÁRIO"], 1200, 120, 140, cores=[(0.98, 0.96, 0.90), (1.0, 0.80, 0.40)])


for nome, fn in (("kaspar_thumb_A", a), ("kaspar_thumb_B", b)):
    print(salvar_thumb(lambda c, t, fn=fn: fn(c, t), f"{OUT}/{nome}.png", tom="misterioso"))
