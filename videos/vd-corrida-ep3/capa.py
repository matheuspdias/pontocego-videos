"""Capa do TikTok · A última corrida · Parte 3 (modelo capa_serie)."""
from engine import *
VERTICAL = True
from ilustrado import *
from pov import *

STYLE = "ilustrado"
TOM = "misterioso"


def capa(c, t):
    quem = dict(SENHOR); quem["olhos"] = "brancos"
    fundo = lambda c: porta_dentro(c, 0, fresta=0.9, pes=True)
    def _olho(c, quem):
        c.save(); c.rectangle(0, 940, W, 740); c.clip()
        olho_magico(c, 0, lambda c, tt: rua_fora(c, tt, quem=quem), foco=(650, 560), zoom=2.0, cy=1300, r=340)
        c.restore()
    capa_serie(c, "A ÚLTIMA CORRIDA", 3, ["ELE VEIO", "ATÉ A MINHA PORTA"], fundo=fundo, destaque=lambda c: _olho(c, quem))


SCENES = [(0, 999, capa)]
