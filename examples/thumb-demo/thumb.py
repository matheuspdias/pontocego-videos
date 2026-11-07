"""Modelo de thumbnail no estilo ilustrado (uma por tom). Rodar da raiz: python examples/thumb-demo/thumb.py"""
import sys, os
sys.path.insert(0, os.getcwd())
from engine import *
from ilustrado import *

OUT = os.path.dirname(os.path.abspath(__file__))


def normal(c, t):  # descoberta: porto ensolarado, naus, rosto surpreso
    cena_porto(c, t, "tarde")
    thumb_close(c, t, 400, 1560, 2.4, "shocked", "point_ru", 0.8)
    thumb_texto(c, ["A PESTE", "CHEGOU"], 1280, 330, 190)
    thumb_selo(c, "1347", 1300, 880, 70)


def misterioso(c, t):  # desaparecimento: mar à noite, navio vazio
    cena_mar(c, t, "noite", navio="nau")
    nevoa_i(c, t, 760, 0.35)
    thumb_close(c, t, 400, 1560, 2.4, "worried", "think", 0.8)
    thumb_texto(c, ["ONDE ESTÁ", "A TRIPULAÇÃO?"], 1250, 150, 150)
    thumb_selo(c, "NUNCA ENCONTRADA", 1260, 900, 54)


def sombrio(c, t):  # terror: casa abandonada, janela acesa, vulto
    cena_casa_abandonada(c, t, "sombrio")
    silhueta(c, t, 1580, 870, 0.5, 0.95)
    thumb_close(c, t, 400, 1560, 2.4, "shocked", "point_r", 0.8)
    thumb_texto(c, ["NINGUÉM", "SAIU VIVO"], 1230, 40, 160, cores=[(0.98, 0.96, 0.90), (0.95, 0.28, 0.20)])


for nome, fn in (("normal", normal), ("misterioso", misterioso), ("sombrio", sombrio)):
    print(salvar_thumb(lambda c, t, fn=fn: fn(c, t), f"{OUT}/thumb_{nome}.png", tom=nome))
