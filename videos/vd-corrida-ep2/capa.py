"""Capa do TikTok · A última corrida · Parte 2 (modelo capa_serie)."""
from engine import *
VERTICAL = True
from ilustrado import *
from pov import *

STYLE = "ilustrado"
TOM = "misterioso"


def capa(c, t):
    fundo = lambda c: estrada_noite(c, 0, 0.0, fim=lambda c, t, hz: portao_cemiterio(c, t, W / 2, hz + 420, 0.95, abertura=1.0))
    destaque = lambda c: celular_mao(c, 0, tela_pix(aviso="Conta encerrada em 2006", t_aviso=-1), y=1330, s=0.62)
    capa_serie(c, "A ÚLTIMA CORRIDA", 2, ["PIX DE QUEM", "MORREU HÁ 20 ANOS"], fundo=fundo, destaque=destaque)


SCENES = [(0, 999, capa)]
