"""Prévia de estilo — Passo Dyatlov (sem narração, ~30 s).
Narração imaginada:
(0:00) O Mistério do Passo Dyatlov.
(0:05) Em fevereiro de 1959, nove jovens partiram para uma expedição nos Montes Urais.
(0:11) Semanas depois, as equipes de busca encontraram a barraca... rasgada por dentro.
(0:17) Pegadas levavam montanha abaixo. Ninguém estava vestido para quase 30 graus negativos.
(0:23) Os arquivos foram lacrados. O que aconteceu naquela noite?
"""
from engine import *


def night(c, t, moon_xy=(1560, 200)):
    stars(c, t)
    c.save(); c.translate(*moon_xy); moon(c, 60); c.restore()


def s01(c, t):  # abertura
    night(c, t)
    c.save(); c.translate(960, 900); mountains(c, 2100, 520); c.restore()
    fog(c, t, 860, 0.09)
    snow(c, t, 90, 30, 0.6)
    show(c, t, 0.4, 960, 300, lambda c: (text(c, "O MISTÉRIO DO", 0, -70, 44, TYPE, AMBER),
                                         stitle(c, "PASSO DYATLOV", 0, 10, 110, INK, AMBER)), anim="fade", d=1.2)
    historiador(c, t, 330, 1010, 1.0, [(0, "stand"), (1.6, "present")], [(0, "neutral"), (1.6, "think")], appear=1.2, look=1)


def s02(c, t):  # fevereiro de 1959, nove jovens
    night(c, t, (300, 170))
    c.save(); c.translate(960, 820); mountains(c, 2200, 420, col=(0.20, 0.23, 0.30)); c.restore()
    show(c, t, 5.2, 960, 130, lambda c: date_stamp(c, "FEVEREIRO DE 1959", 52, RED), anim="stamp")
    typewrite(c, t, 6.0, "Montes Urais  •  União Soviética", 960, 230, 40, INK)
    cols = [RED, BLUE, GREEN, AMBER, PURPLE, ORANGE, RED, BLUE, GREEN]
    walk = (t - 7.0) * 55 if t > 7.0 else 0
    for i in range(9):
        hiker(c, t, 200 + i * 135 + walk, 1010, 0.62, [(0, "run")], [(0, "neutral")], col=cols[i], fid=10 + i,
              appear=7.0 + i * 0.15)
    show(c, t, 8.6, 1600, 560, lambda c: caption_box(c, "9 excursionistas", 44), anim="up")
    snow(c, t, 110, 60, 0.7)
    fog(c, t, 960, 0.06)


def s03(c, t):  # barraca rasgada por dentro
    night(c, t, (1700, 150))
    c.save(); c.translate(960, 960); mountains(c, 2400, 300, col=(0.18, 0.21, 0.27)); c.restore()
    c.rectangle(0, 870, W, H - 870); rgb(c, (0.80, 0.84, 0.90)); c.fill()
    show(c, t, 11.2, 1020, 800, sc(tent, True, s=1.35), anim="fade", d=0.8)
    show(c, t, 13.6, 1110, 700, sc(magnifier, s=0.9), anim="pop")
    show(c, t, 14.3, 1020, 170, lambda c: hl(c, "rasgada por DENTRO", 0, 0, 56), anim="up")
    historiador(c, t, 360, 1010, 1.0, [(0, "stand"), (13.4, "point_r")], [(0, "neutral"), (13.4, "shocked")],
                appear=11.4, look=1)
    snow(c, t, 70, 20, 0.5)
    fog(c, t, 900, 0.07)


def s04(c, t):  # pegadas e -30 °C
    night(c, t, (250, 160))
    c.rectangle(0, 700, W, H - 700); rgb(c, (0.78, 0.82, 0.88)); c.fill()
    for x, h in ((1500, 320), (1640, 260), (1760, 360), (1850, 280)):
        c.save(); c.translate(x, 720); pine(c, h); c.restore()
    c.save(); c.translate(200, 820); footprints(c, 15, 85, 12, t, 17.2); c.restore()
    show(c, t, 17.2, 640, 560, lambda c: caption_box(c, "pegadas montanha abaixo", 42), anim="up")
    show(c, t, 19.6, 1250, 380, sc(thermometer, "-30 °C", 0.1, s=1.1), anim="pop")
    show(c, t, 20.6, 640, 660, lambda c: caption_box(c, "sem casacos, alguns descalços", 42), anim="up")
    snow(c, t, 220, 160, 0.85)
    fog(c, t, 820, 0.08)


def s05(c, t):  # arquivos lacrados / pergunta
    def q(c):
        big_q(c, 120, AMBER)
    items = [(-300, -40, sc(photo, lambda c: sc(tent, True, s=0.45)(c), caption="a barraca", s=0.8)),
             (0, 60, sc(folder, "LACRADO", s=0.65)),
             (300, -40, sc(photo, lambda c: sc(mountains, 400, 120)(c), caption="Kholat Syakhl", s=0.8))]
    show(c, t, 23.1, 1100, 540, lambda c: evidence_board(c, t, 23.6, items, 920, 560), anim="fade", d=0.6)
    show(c, t, 25.4, 1100, 160, lambda c: stitle(c, "O que aconteceu naquela noite?", 0, 0, 64, INK, AMBER), anim="up", d=0.8)
    historiador(c, t, 330, 1010, 1.0, [(0, "stand"), (23.2, "think")], [(0, "think")], appear=23.0, look=1)
    show(c, t, 26.5, 1700, 560, sc(big_q, 160, AMBER), anim="pop")
    fog(c, t, 980, 0.07)


SCENES = [(0.0, 5.0, s01), (5.0, 11.0, s02), (11.0, 17.0, s03), (17.0, 23.0, s04), (23.0, 999.0, s05)]

# sons extras (além dos automáticos): impacto na abertura, rajadas de vento, batidas de coração no suspense
SFX = [(0.4, "boom"), (11.0, "gust"), (17.3, "gust"), (19.6, "impact"), (25.3, "heartbeat"), (26.3, "heartbeat"), (27.3, "heartbeat")]
