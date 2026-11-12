"""Capa do TikTok · A última corrida · Parte 1 (modelo capa_serie)."""
from engine import *
VERTICAL = True
from ilustrado import *
from pov import *

STYLE = "ilustrado"
TOM = "misterioso"


def capa(c, t):
    def fundo(c):
        def fora(c, t):
            estrada_noite(c, t, 0.0, fim=lambda c, t, hz: portao_cemiterio(c, t, W / 2, hz + 300, 0.8))
            nevoa_i(c, t, 900, 0.5, seed=2)
        c.save(); c.translate(W / 2, 980); c.scale(1.55, 1.55); c.translate(-W / 2, -345)
        carro_pov(c, 0, fora, retrovisor=banco_tras(False, True, olhos=True), balanco=False, volante=False)
        c.restore()
    capa_serie(c, "A ÚLTIMA CORRIDA", 1, ["O PASSAGEIRO", "QUE NÃO EMBARCOU"], fundo=fundo)


SCENES = [(0, 999, capa)]
