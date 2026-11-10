"""Capa do TikTok · A última corrida · Ep. 1 (o perfil corta em 3:4: o essencial fica entre y 260 e 1660)."""
from engine import *
VERTICAL = True
from ilustrado import *
from pov import *

STYLE = "ilustrado"
TOM = "misterioso"


def capa(c, t):
    def fora(c, t):
        estrada_noite(c, t, 0.0, fim=lambda c, t, hz: portao_cemiterio(c, t, W / 2, hz + 300, 0.8))
        nevoa_i(c, t, 900, 0.5, seed=2)
    c.save(); c.translate(W / 2, 330); c.scale(1.55, 1.55); c.translate(-W / 2, -345)
    carro_pov(c, t, fora, retrovisor=banco_tras(False, True, olhos=True), balanco=False, volante=False)
    c.restore()
    c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.25); c.fill()
    for k, (s, col, y) in enumerate((("O PASSAGEIRO", (1, 1, 1), 930), ("QUE NÃO", (1, 1, 1), 1050), ("EMBARCOU", (1.0, 0.80, 0.36), 1180))):
        sz = 118
        e = (lambda: (c.select_font_face(FONTE), c.set_font_size(sz), c.text_extents(s))[2])()
        _contorno = __import__("pov")._contorno
        _contorno(c, s, W / 2 - e.x_advance / 2, y, sz, col)
    selo_ep(c, "EP. 1", x=W / 2 - 70, y=1350)
    c.select_font_face(FONTE); c.set_font_size(44)
    s = "VOCÊ DECIDE O FINAL"
    e = c.text_extents(s); c.move_to(W / 2 - e.x_advance / 2, 1480); rgb(c, (0.98, 0.95, 0.88)); c.show_text(s)
    c.set_font_size(34); s = "PONTO CEGO"
    e = c.text_extents(s); c.move_to(W / 2 - e.x_advance / 2, 1600); rgb(c, (0.98, 0.80, 0.36), 0.9); c.show_text(s)


SCENES = [(0, 999, capa)]
