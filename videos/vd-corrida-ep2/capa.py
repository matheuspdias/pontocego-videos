"""Capa do TikTok · A última corrida · Ep. 2 (essencial entre y 260 e 1660)."""
from engine import *
VERTICAL = True
from ilustrado import *
from pov import *
import pov

STYLE = "ilustrado"
TOM = "misterioso"


def capa(c, t):
    estrada_noite(c, 0, 0.0, fim=lambda c, t, hz: portao_cemiterio(c, t, W / 2, hz + 420, 0.95, abertura=1.0))
    c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.45); c.fill()
    celular_mao(c, 0, tela_pix(aviso="Conta encerrada em 2006", t_aviso=0), y=1150, s=0.82)
    for s, col, y, sz in (("PIX DE QUEM", (1, 1, 1), 300, 110), ("MORREU HÁ", (1, 1, 1), 420, 110), ("20 ANOS", (1.0, 0.80, 0.36), 560, 140)):
        c.select_font_face(FONTE); c.set_font_size(sz); e = c.text_extents(s)
        pov._contorno(c, s, W / 2 - e.x_advance / 2, y, sz, col)
    selo_ep(c, "EP. 2", x=60, y=118)
    c.select_font_face(FONTE); c.set_font_size(40); s = "VOCÊ DECIDE O FINAL"
    e = c.text_extents(s); c.move_to(W / 2 - e.x_advance / 2, 1640); rgb(c, (0.98, 0.95, 0.88)); c.show_text(s)


SCENES = [(0, 999, capa)]
