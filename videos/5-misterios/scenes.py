"""5 mistérios que nunca foram resolvidos — Ponto Cego (lista em contagem regressiva).
Narração: Pedro Lima - Serious (HeyGen / ElevenLabs v4), 7 blocos com 1 s de silêncio entre eles.
Cada cena trabalha em tempo LOCAL do seu bloco (u = t - O[n]); B(n, x) converte para tempo absoluto.
Durações e offsets: videos/5-misterios/tempos.py (palavra a palavra em ts/bN.txt).
"""
import importlib.util, os
from engine import *

THEME = "classico"
SFX_OFF = True

_spec = importlib.util.spec_from_file_location("tempos5", os.path.join(os.path.dirname(os.path.abspath(__file__)), "tempos.py"))
_tm = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_tm)
O = _tm.offsets()


def B(n, x):
    return O[n] + x


def K(o, keys):
    """desloca keyframes (tempo local -> absoluto)"""
    return [(k + o, v) for k, v in keys]


class Cx:
    """atalhos de uma cena em tempo local"""
    def __init__(self, c, t, n):
        self.c, self.t, self.o = c, t, O[n]
        self.u = t - self.o

    def sh(self, t0, x, y, fn, **kw):
        if "t1" in kw and kw["t1"] is not None:
            kw["t1"] += self.o
        show(self.c, self.t, t0 + self.o, x, y, fn, **kw)

    def tw(self, t0, s, x, y, size=46, col=INK, **kw):
        typewrite(self.c, self.t, t0 + self.o, s, x, y, size, col, **kw)

    def hist(self, poses, exprs, appear=None, x=300, y=1010, s=0.95, **kw):
        historiador(self.c, self.t, x, y, s, K(self.o, poses), K(self.o, exprs),
                    appear=None if appear is None else appear + self.o, look=1, **kw)

    def fig(self, fn, x, y, s, poses, exprs, appear=None, **kw):
        fn(self.c, self.t, x, y, s, K(self.o, poses), K(self.o, exprs),
           appear=None if appear is None else appear + self.o, **kw)

    def p(self, t0, d=0.5):
        return ease_out(prog(self.u, t0, d))


def nope(c, lab, size=44):
    """rótulo com um X vermelho pequeno à esquerda"""
    w = text_w(c, lab, size, TYPE)
    text(c, lab, 20, 0, size, TYPE, INK)
    c.save(); c.translate(-w / 2 - 20, 0); big_x(c, size * 0.45, RED, 8); c.restore()


def x_over(X, t0, x, y, s=70):
    X.sh(t0, x, y, lambda c: big_x(c, s, RED, 14), anim="stamp")


def night(c, t, ymax=620, n=80, moon_at=None):
    stars(c, t, n, ymax)
    if moon_at:
        c.save(); c.translate(*moon_at); moon(c, 55); c.restore()


def ground(c, y=960, col=(0.07, 0.08, 0.10)):
    c.rectangle(0, y, W, H - y); rgb(c, col); c.fill()
    line(c, 0, y, W, y, 3, (0.25, 0.25, 0.28))


def rank_scene(X, n, ttl, sub, extra=None, col=AMBER):
    c, t = X.c, X.t
    night(c, t, 1080, 110)
    if extra:
        extra(c, t)
    X.sh(0.0, 960, 430, lambda c: rank_card(c, n, ttl, sub, col), anim="fade", d=0.8)
    fog(c, t, 960, 0.08)


# ====================================================================== BLOCO 1 — abertura
def a01(c, t):  # 0 - 6.6
    X = Cx(c, t, 1)
    night(c, t, 700, 90, (1560, 190))
    ground(c, 960)
    X.sh(0.3, 1150, 380, lambda c: stitle(c, "Existem histórias que terminam.", 0, 0, 56, INK), anim="up")
    X.sh(2.84, 1150, 520, lambda c: stitle(c, "E histórias que simplesmente param.", 0, 0, 56, AMBER, AMBER), anim="up")
    X.hist([(0, "stand"), (2.8, "think")], [(0, "neutral"), (2.8, "think")], appear=0.1)
    fog(c, t, 960, 0.08)


def teaser_frame(c, fn, lab):
    rrect(c, -230, -190, 460, 380, 10); fs(c, (0.10, 0.11, 0.13), 5)
    c.save(); c.rectangle(-222, -182, 444, 300); c.clip(); fn(c); c.restore()
    line(c, -222, 118, 222, 118, 3, INK)
    text(c, lab, 0, 152, 30, TYPE, AMBER)


def a02(c, t):  # 6.6 - 22.2 três prévias
    X = Cx(c, t, 1)
    night(c, t, 1080, 60)
    u = X.u
    X.sh(6.8, 560, 420, lambda c: teaser_frame(c, lambda c: (at(-60, 40, sc(axe, s=0.7))(c), at(90, 20, sc(letter, 5, 160, 210, False))(c),
                                                             text(c, "INFERNO", 90, -60, 26, TYPE, RED)), "uma carta do inferno"))
    X.sh(11.2, 1360, 420, lambda c: teaser_frame(c, lambda c: (signal_wave(c, t, 400, 8, 150 if u > 12.5 else 0, 0.5, 0.06, ICE, 4),
                                                               text(c, "72 s", 150, -120, 34, TYPE, ICE)), "72 segundos do espaço"))
    if u > 14.9:
        X.sh(14.95, 1360, 420, lambda c: big_x(c, 70, RED, 12), anim="stamp")
    X.sh(16.88, 960, 800, lambda c: teaser_frame(c, lambda c: (night(c, t, 300, 30), at(-90, -70, sc(b727, s=0.3))(c),
                                                               at(80, 60, lambda c: (parachute(c, t, open_=1.0), person(c, t, 0, 30, 0.22, [(0, "arms_up")], [(0, "neutral")], col=(0.15, 0.15, 0.18))))(c)),
                                                       "um salto no escuro"), s=0.9)
    X.hist([(0, "stand"), (6.8, "point_r"), (11.3, "think"), (17.0, "present")], [(0, "neutral"), (14.9, "worried")], x=200, s=0.85)


def a03(c, t):  # 22.2 - 28.5 fazenda
    X = Cx(c, t, 1)
    night(c, t, 650, 90, (1600, 170))
    c.save(); c.translate(1080, 920); farmhouse(c, t, attic=X.p(25.9, 1.0), w=820); c.restore()
    snow(c, t, 60, 30, 0.5)
    c.rectangle(0, 920, W, 160); rgb(c, (0.70, 0.74, 0.80), 0.18); c.fill()
    c.save(); c.translate(1600, 1020); footprints(c, 7, -70, -10, t, 22.6 + O[1], (0.55, 0.60, 0.70)); c.restore()
    X.sh(26.0, 1080, 240, lambda c: caption_box(c, "alguém vivia escondido?", 42), anim="up")
    X.hist([(0, "stand"), (25.9, "point_ru")], [(0, "worried")], x=260, s=0.85)
    fog(c, t, 960, 0.07)


def a04(c, t):  # 28.5 - 34.6 Brasil
    X = Cx(c, t, 1)
    night(c, t, 700, 90)
    c.save(); c.translate(1180, 1000); morro(c, 1500, 380, (0.08, 0.12, 0.10)); c.restore()
    X.sh(28.7, 1180, 230, lambda c: (glow(c, 0, 0, 380, (0.30, 0.65, 0.40), 0.14), stitle(c, "AQUI NO BRASIL", 0, 0, 84, INK)), anim="fade", d=0.9)
    X.sh(30.0, 1180, 520, lambda c: big_q(c, 200, AMBER), anim="pop")
    X.sh(32.0, 1180, 900, lambda c: caption_box(c, "até hoje, ninguém sabe explicar", 40), anim="up")
    X.hist([(0, "stand"), (32.0, "shrug")], [(0, "think"), (33.2, "worried")], x=300)
    fog(c, t, 980, 0.08)


def a05(c, t):  # 34.6 - fim do bloco (46.2) título + contagem
    X = Cx(c, t, 1)
    night(c, t, 1080, 120)
    X.sh(35.0, 960, 250, lambda c: (text(c, "CINCO MISTÉRIOS", 0, -70, 54, TYPE, AMBER),
                                    stitle(c, "QUE NUNCA FORAM RESOLVIDOS", 0, 20, 78, INK, AMBER)), anim="fade", d=1.0)
    for i, n in enumerate((5, 4, 3, 2, 1)):
        t0 = 38.9 + i * 0.25
        x = 520 + i * 220
        hot = n == 1 and X.u > 43.0
        X.sh(t0, x, 640, lambda c, n=n, hot=hot: (circle(c, 0, 0, 80, (0.10, 0.10, 0.12), 5, RED if hot else INK),
                                                  glow(c, 0, 0, 200, RED, 0.35) if hot else None,
                                                  text(c, str(n), 0, -4, 96, SERIF, RED if hot else INK)))
    X.sh(41.6, 960, 860, lambda c: caption_box(c, "quanto mais perto do número um, mais estranho fica", 38), anim="up")
    fog(c, t, 980, 0.08)


# ====================================================================== BLOCO 2 — Nº 5 Homem do Machado
def b2_01(c, t):  # 0 - 4.8
    X = Cx(c, t, 2)
    rank_scene(X, 5, "O Homem do Machado", "Nova Orleans  •  1918-1919",
               extra=lambda c, t: (c.save(), c.translate(1640, 860), sc(axe, s=0.9)(c), c.restore()))


def b2_02(c, t):  # 4.8 - 17.9 jornal + carta
    X = Cx(c, t, 2)
    X.sh(5.0, 1050, 420, lambda c: newspaper(c, "CARTA DO", "assassino promete voltar"), s=1.5, anim="drop")
    X.sh(10.8, 1560, 300, lambda c: (clock(c, X.t * 0.5), text(c, "quando?", 0, 130, 38, TYPE, AMBER)), s=0.8)
    X.sh(14.4, 1450, 820, lambda c: caption_box(c, "e como sobreviver", 44), anim="up")
    X.hist([(0, "stand"), (5.0, "present"), (10.8, "think")], [(0, "worried"), (14.4, "shocked")])
    fog(c, t, 980, 0.06)


def city(c, t, lit=0.2, y=960):
    for i in range(9):
        x = 120 + i * 230
        c.save(); c.translate(x, y); townhouse(c, 210, 280 + (i % 3) * 30, lit=lit, seed=i); c.restore()
    for i in range(4):
        c.save(); c.translate(240 + i * 480, y); gas_lamp(c, t, 230); c.restore()
    ground(c, y)


def b2_03(c, t):  # 17.9 - 31.8 cidade, Maggio
    X = Cx(c, t, 2)
    night(c, t, 600, 60, (1680, 140))
    city(c, t, 0.1, 980)
    X.tw(17.9, "Nova Orleans, EUA", 960, 110, 46, INK)
    X.sh(20.0, 960, 210, lambda c: date_stamp(c, "MAIO DE 1918", 54, RED), anim="stamp")
    if X.u > 22.3:
        c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.45 * X.p(22.3, 0.8)); c.fill()
        X.sh(22.4, 1000, 1000, lambda c: (townhouse(c, 320, 420, lit=0.0, seed=3), hl(c, "MERCEARIA", 0, -230, 34)), s=1.0, anim="fade")
        X.sh(25.9, 1000, 420, lambda c: hl(c, "Joseph e Catherine Maggio", 0, 0, 46), anim="up")
        X.sh(30.4, 1520, 560, lambda c: (at(-50, 0, lambda c: candle(c, X.t))(c), at(50, 0, lambda c: candle(c, X.t + 1))(c)), anim="fade")
    X.hist([(0, "stand"), (22.4, "point_r")], [(0, "neutral"), (28.4, "sad")], x=280)
    fog(c, t, 1000, 0.06)


def b2_04(c, t):  # 31.8 - 44.1 porta dos fundos
    X = Cx(c, t, 2)
    ground(c, 980)
    c.save(); c.translate(1000, 980); door(c, panel_out=X.u > 37.9, w=260, h=470); c.restore()
    if X.u > 36.0:
        k = X.p(36.0, 1.6)
        X.sh(36.0, 1340 - k * 120, 600, lambda c: sc(chisel, s=1.2)(c), anim="fade")
    if X.u > 39.6:
        glow(c, 1000, 760, 200, (0, 0, 0), 0.5)
        c.save(); c.translate(1150, 1040); footprints(c, 6, 80, 0, t, 39.7 + O[2], (0.35, 0.36, 0.40)); c.restore()
    X.sh(32.0, 1520, 220, lambda c: caption_box(c, "um padrão que se repetiria", 40), anim="up")
    X.sh(42.3, 1520, 360, lambda c: (caption_box(c, "nada foi roubado", 44)), anim="up")
    X.sh(42.6, 1600, 560, lambda c: (sc(coin, s=0.8)(c), at(90, 10, sc(bills, 2, s=0.6))(c)), anim="pop")
    X.hist([(0, "stand"), (36.0, "point_r"), (42.3, "shrug")], [(0, "worried")], x=300)
    fog(c, t, 1000, 0.06)


def b2_05(c, t):  # 44.1 - 65.0 a série de ataques
    X = Cx(c, t, 2)
    night(c, t, 400, 50)
    y0 = 520
    p = X.p(44.2, 15.0)
    line(c, 180, y0, 180 + 1560 * p, y0, 5, INK)
    marks = [(44.2, "JUN 1918", "outra mercearia", 400), (47.3, "AGO 1918", "mais vítimas", 820), (49.4, "MAR 1919", "Gretna", 1340)]
    for t0, d, lab, x in marks:
        X.sh(t0, x, y0, lambda c, d=d, lab=lab: (circle(c, 0, 0, 16, RED, 4), text(c, d, 0, -70, 40, TYPE, AMBER),
                                                text(c, lab, 0, 70, 38, HAND, INK)))
    X.sh(54.2, 1340, 760, lambda c: caption_box(c, "uma família inteira atacada", 38), anim="up")
    X.sh(58.9, 960, 240, lambda c: (glow(c, 0, 0, 260, RED, 0.18), sc(axe, s=0.9)(c)), anim="drop")
    X.sh(61.8, 1600, 220, lambda c: (house(c, False, (0.40, 0.36, 0.30)), at(0, -10, sc(axe, s=0.25))(c),
                                     text(c, "da própria casa", 0, 110, 34, HAND, INK)), anim="pop")
    X.hist([(0, "stand"), (49.4, "point_r"), (58.9, "head")], [(0, "worried"), (58.9, "shocked")], x=180, s=0.85)


def b2_06(c, t):  # 65.0 - 76.3 pânico + 13/03/1919
    X = Cx(c, t, 2)
    night(c, t, 600, 60)
    city(c, t, 0.9, 980)
    for i, x in enumerate((350, 810, 1270)):
        X.fig(person, x, 980, 0.6, [(0, "stand")], [(0, "worried")], appear=66.9 + i * 0.3, col=(0.35, 0.33, 0.30), fid=10 + i)
    X.sh(65.1, 960, 160, lambda c: caption_box(c, "a cidade em pânico", 44), anim="up", t1=70.0)
    X.sh(70.4, 960, 160, lambda c: date_stamp(c, "13 DE MARÇO DE 1919", 54, RED), anim="stamp")
    X.sh(74.2, 1500, 420, lambda c: newspaper(c, "A CARTA", "publicada nos jornais"), s=1.0, anim="drop")
    fog(c, t, 1000, 0.07)


def b2_07(c, t):  # 76.3 - 83.2 carta do inferno
    X = Cx(c, t, 2)
    glow(c, 1050, 560, 600, RED, 0.08 + 0.06 * X.p(81.8, 0.6))
    X.sh(76.4, 1050, 560, lambda c: letter(c, 8, 520, 680, True), anim="up", d=0.7)
    X.tw(77.6, "O Homem do Machado", 1050, 960, 40, INK)
    if X.u > 81.8:
        flames_k = X.p(81.8, 0.6)
        c.save(); c.translate(1050, 175); c.scale(1.4, 0.8)
        c.push_group(); flames(c, t, 260, 120); c.pop_group_to_source(); c.paint_with_alpha(0.6 * flames_k); c.restore()
    X.tw(81.85, "Inferno, 13 de março de 1919", 1050, 310, 44, RED, cps=30)
    X.hist([(0, "stand"), (77.0, "present")], [(0, "worried"), (81.85, "shocked")], x=320)


def b2_08(c, t):  # 83.2 - 100.3 demônio, 00h15, jazz
    X = Cx(c, t, 2)
    night(c, t, 700, 70)
    X.sh(83.3, 1250, 160, lambda c: stitle(c, "\"um espírito, um demônio\"", 0, 0, 54, INK, RED), anim="up")
    X.sh(88.3, 900, 470, lambda c: (sc(clock, 0, s=1.1)(c), text(c, "terça-feira", 0, 150, 38, TYPE, AMBER)), anim="pop")
    X.sh(92.4, 900, 720, lambda c: date_stamp(c, "00h15", 60, RED), anim="stamp")
    if X.u > 95.7:
        X.sh(95.8, 1480, 470, lambda c: (glow(c, 0, 0, 300, AMBER, 0.22), trumpet(c)), anim="pop")
        music_notes(c, t, 1700, 620, 5)
        X.sh(98.3, 1480, 720, lambda c: stitle(c, "JAZZ", 0, 0, 110, AMBER, AMBER), anim="stamp")
        X.sh(96.4, 1480, 880, lambda c: caption_box(c, "casas com jazz seriam poupadas", 38), anim="up")
    X.hist([(0, "stand"), (88.3, "point_r"), (95.8, "present")], [(0, "worried"), (95.8, "think")], x=300)
    fog(c, t, 1000, 0.06)


def b2_09(c, t):  # 100.3 - 111.4 noite do jazz
    X = Cx(c, t, 2)
    night(c, t, 600, 70, (1700, 150))
    city(c, t, 1.0, 980)
    for i, x in enumerate((350, 1040, 1500)):
        X.fig(person, x, 980, 0.7, [(0, "stand"), (101.0, "hold")], [(0, "happy")], appear=103.1 + i * 0.4,
              col=(0.55, 0.20, 0.20) if i % 2 else (0.25, 0.30, 0.50), fid=20 + i,
              prop=("r", lambda c, tt: (c.save(), c.rotate(-0.3), c.scale(0.45, 0.45), trumpet(c), c.restore())))
        music_notes(c, t + i, x, 700, 4)
    X.sh(100.4, 960, 150, lambda c: caption_box(c, "Nova Orleans não dormiu", 44), anim="up")
    X.sh(108.5, 960, 270, lambda c: (caption_box(c, "ninguém foi atacado", 44)), anim="up")
    fog(c, t, 1000, 0.05)


def b2_10(c, t):  # 111.4 - 134.9 dúvidas, suspeitos
    X = Cx(c, t, 2)
    X.sh(111.5, 520, 330, lambda c: (letter(c, 6, 300, 380, True), at(130, -150, lambda c: big_q(c, 90, AMBER))(c)), anim="fade")
    X.sh(112.9, 520, 600, lambda c: text(c, "o assassino... ou um oportunista?", 0, 0, 34, HAND, INK), anim="fade")
    for i in range(3):
        x = 1050 + i * 230
        X.fig(person, x, 560, 0.75, [(0, "stand")], [(0, "worried")], appear=117.5 + i * 0.25, col=(0.30, 0.30, 0.34), fid=30 + i)
    X.sh(119.4, 1280, 640, lambda c: date_stamp(c, "SOLTOS", 44, AMBER), anim="stamp")
    X.sh(120.2, 1280, 800, lambda c: (sc(gavel, s=0.8)(c), text(c, "família condenada", 0, 110, 36, HAND, INK)), anim="pop")
    X.sh(123.5, 1280, 960, lambda c: caption_box(c, "a testemunha tinha mentido", 38), anim="up")
    X.sh(125.8, 520, 820, lambda c: (folder(c, "SUSPEITOS", True)), s=0.9, anim="drop")
    X.sh(128.4, 520, 1000, lambda c: text(c, "nada provado", 0, 0, 40, TYPE, RED), anim="fade")
    if X.u > 129.5:
        c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.7 * X.p(129.5, 0.5)); c.fill()
        X.sh(129.7, 960, 480, lambda c: (text(c, "ÚLTIMO ATAQUE", 0, -70, 44, TYPE, AMBER), date_stamp(c, "OUTUBRO DE 1919", 64, RED)), anim="stamp")


def b2_11(c, t):  # 134.9 - 148.4 ele parou
    X = Cx(c, t, 2)
    night(c, t, 700, 80)
    city(c, t, 0.05, 1000)
    fade = 1 - X.p(143.0, 2.0)
    if fade > 0.01:
        c.push_group()
        person(c, t, 1300, 1000, 1.1, [(0, "stand")], [(0, "neutral")], col=(0.06, 0.06, 0.07), fid=40, hat="fedora", hat_col=(0.06, 0.06, 0.07))
        c.save(); c.translate(1380, 860); c.rotate(0.3); sc(axe, s=0.5)(c); c.restore()
        c.pop_group_to_source(); c.paint_with_alpha(0.85 * fade)
    X.sh(138.1, 960, 140, lambda c: stitle(c, "Nunca foi pego.", 0, 0, 70, INK, RED), anim="up")
    for i, (lab, t0) in enumerate((("preso", 139.5), ("morto", 140.6), ("confessou", 141.9))):
        X.sh(t0, 560 + i * 400, 300, lambda c, lab=lab: nope(c, lab, 44), anim="pop")
    X.sh(145.5, 1300, 760, lambda c: (tombstone(c, "?")), anim="fade", d=1.0)
    X.hist([(0, "stand"), (143.0, "think")], [(0, "worried"), (145.5, "sad")], x=280)
    fog(c, t, 1000, 0.09)


def b2_12(c, t):  # 148.4 - fim (156.5) transição p/ o espaço
    X = Cx(c, t, 2)
    night(c, t, 1080, 140)
    X.sh(148.5, 1150, 300, lambda c: caption_box(c, "se esse já é estranho...", 46), anim="up")
    if X.u > 152.8:
        k = X.p(152.8, 2.0)
        for r in range(4):
            rr = 60 + ((X.u * 120 + r * 90) % 360)
            c.new_sub_path(); c.arc(1500, 200, rr, 0.3, 2.6); rgb(c, ICE, 0.5 * k * (1 - rr / 420)); c.set_line_width(4); c.stroke()
        X.sh(153.4, 1150, 560, lambda c: stitle(c, "...o próximo nem veio da Terra", 0, 0, 56, ICE, ICE), anim="up")
    X.hist([(0, "stand"), (152.8, "point_ru")], [(0, "think"), (152.8, "shocked")], x=320)


# ====================================================================== BLOCO 3 — Nº 4 Sinal Wow!
def b3_01(c, t):  # 0 - 4.3
    X = Cx(c, t, 3)
    rank_scene(X, 4, "O Sinal Wow!", "Ohio, EUA  •  1977", col=ICE,
               extra=lambda c, t: (c.save(), c.translate(1600, 860), signal_wave(c, t, 360, 6, 120, 0.5, 0.07, ICE, 4), c.restore()))


def b3_02(c, t):  # 4.3 - 15.3 pulso chegando
    X = Cx(c, t, 3)
    night(c, t, 1080, 160)
    c.save(); c.translate(1500, 1250); circle(c, 0, 0, 420, (0.12, 0.20, 0.30), 6); c.restore()
    glow(c, 1500, 900, 300, (0.4, 0.6, 1.0), 0.10)
    k = clamp01((X.u - 4.4) / 7.2)
    if 0 < k < 1:
        x, y = 200 + k * 1250, 150 + k * 650
        glow(c, x, y, 120, ICE, 0.5)
        circle(c, x, y, 10, (0.9, 0.95, 1.0), 0)
    X.sh(4.5, 520, 820, lambda c: (text(c, "%02d" % min(72, int(max(0, X.u - 4.4) / 7.2 * 72)), 0, 0, 120, TYPE, ICE),
                                   text(c, "segundos", 0, 90, 36, TYPE, INK)), anim="fade")
    X.sh(12.4, 1100, 260, lambda c: caption_box(c, "e nunca mais", 46), anim="up")


def b3_03(c, t):  # 15.3 - 27.9 Big Ear
    X = Cx(c, t, 3)
    night(c, t, 600, 90)
    ground(c, 900, (0.07, 0.09, 0.07))
    X.sh(17.4, 1080, 880, lambda c: big_ear(c, 1500), s=1.0, anim="fade", d=1.0)
    X.tw(15.3, "Ohio, EUA", 960, 110, 46, INK)
    X.sh(19.1, 960, 200, lambda c: caption_box(c, "Universidade Estadual de Ohio", 40), anim="up")
    X.sh(24.2, 1080, 380, lambda c: hl(c, "BIG EAR", 0, 0, 64), anim="stamp")
    X.sh(26.0, 1080, 490, lambda c: text(c, "\"o Grande Ouvido\"", 0, 0, 40, HAND, AMBER), anim="fade")
    X.hist([(0, "stand"), (17.4, "point_r")], [(0, "neutral"), (24.2, "happy")], x=220, s=0.8, y=1040)
    fog(c, t, 980, 0.05)


def b3_04(c, t):  # 27.9 - 38.9 a Terra gira
    X = Cx(c, t, 3)
    c.save(); c.translate(-(X.u * 18) % W, 0)
    for dx in (0, W):
        c.save(); c.translate(dx, 0); stars(c, t, 120, 700); c.restore()
    c.restore()
    ground(c, 900, (0.07, 0.09, 0.07))
    c.save(); c.translate(1000, 880); big_ear(c, 1500); c.restore()
    X.sh(29.4, 1000, 990, lambda c: caption_box(c, "do tamanho de uns 3 campos de futebol", 38), anim="up")
    X.sh(34.9, 1000, 160, lambda c: (text(c, "o céu passa por cima", 0, 0, 44, HAND, ICE),
                                     arrow(c, 260, 0, 420, 0, ICE, 5, 0.0)), anim="fade")


def b3_05(c, t):  # 38.9 - 55.3 impressora
    X = Cx(c, t, 3)
    X.sh(39.0, 1250, 230, lambda c: caption_box(c, "busca por sinais de vida inteligente", 40), anim="up")
    scroll = max(0, X.u - 45.7) * 40
    X.sh(45.8, 1250, 640, lambda c: printout(c, t, 520, 640, scroll), anim="up")
    X.sh(50.5, 1700, 520, lambda c: text(c, "ruído", 0, 0, 52, TYPE, INK), anim="fade")
    X.sh(52.3, 1700, 620, lambda c: text(c, "nada especial", 0, 0, 38, HAND, INK), anim="fade")
    X.hist([(0, "stand"), (45.8, "present")], [(0, "neutral"), (50.5, "think")], x=380)
    fog(c, t, 1000, 0.05)


def b3_06(c, t):  # 55.3 - 72.8 15/08/1977 e Ehman
    X = Cx(c, t, 3)
    X.sh(55.3, 960, 140, lambda c: date_stamp(c, "15 DE AGOSTO DE 1977", 54, RED), anim="stamp")
    X.sh(61.3, 960, 260, lambda c: caption_box(c, "ninguém viu na hora", 40), anim="up")
    if X.u > 63.2:
        c.rectangle(500, 860, 920, 26); fs(c, (0.30, 0.22, 0.15), 4)
        glow(c, 1300, 700, 260, AMBER, 0.25)
        X.fig(person, 900, 1000, 1.0, [(0, "stand"), (64.0, "hold")], [(0, "think"), (69.6, "shocked")], appear=63.3,
              col=(0.35, 0.40, 0.50), fid=50, glasses=True)
        X.sh(64.3, 1180, 700, lambda c: printout(c, t, 300, 360, 0, size=18, rows=12), anim="fade")
        X.sh(64.8, 900, 420, lambda c: hl(c, "Jerry Ehman", 0, 0, 46), anim="up")
        X.sh(69.7, 1550, 520, lambda c: (caption_box(c, "6 caracteres", 40)), anim="up")


def b3_07(c, t):  # 72.8 - 91.9 6EQUJ5 -> Wow!
    X = Cx(c, t, 3)
    times = [72.77, 73.52, 74.24, 74.96, 75.68, 76.48]
    nshow = sum(1 for x in times if X.u >= x)
    hi = X.u > 84.4
    c.save(); c.translate(600, 560); c.scale(1.35, 1.35); printout(c, t, 520, 640, 0, wow=nshow, highlight=hi); c.restore()
    if hi:
        p = X.p(84.4, 1.4)
        c.save(); c.translate(600 - 0.20 * 520 * 1.35 / 0.75 + 52, 560 + 20); c.scale(0.55, 1.0)
        c.new_sub_path(); c.arc(0, 0, 230, -1.6, -1.6 + p * 6.4); c.restore()
        rgb(c, RED); c.set_line_width(7); c.stroke()
    if X.u > 77.5:
        k = X.p(77.5, 3.0)
        c.save(); c.translate(1380, 520)
        line(c, -320, 0, 320, 0, 2, (0.4, 0.4, 0.45))
        signal_wave(c, t, 640, 6, 240 * k, 0.5, 0.08, ICE, 5)
        text(c, "intensidade", -250, 60, 28, TYPE, INK, align="l")
        c.restore()
    if X.u > 90.7:
        X.sh(90.72, 1380, 160, lambda c: (glow(c, 0, 0, 200, RED, 0.25), text(c, "Wow!", 0, 0, 120, HAND, RED)), anim="stamp", rot=-0.12)
    X.sh(87.7, 1380, 860, lambda c: caption_box(c, "uma única palavra na margem", 38), anim="up")


def b3_08(c, t):  # 91.9 - 112.2 frequência, hidrogênio, Sagitário
    X = Cx(c, t, 3)
    night(c, t, 1080, 100)
    X.sh(92.0, 960, 140, lambda c: caption_box(c, "a frequência", 46), anim="up")
    X.sh(96.4, 560, 520, lambda c: (sc(hydrogen, t, s=1.2)(c), text(c, "1420 MHz", 0, 180, 60, TYPE, ICE)), anim="pop")
    X.sh(100.0, 560, 820, lambda c: text(c, "hidrogênio: o elemento mais comum", 0, 0, 36, HAND, INK), anim="fade")
    X.sh(103.2, 1380, 470, lambda c: (radio_tower(c, t), text(c, "\"chamar atenção\"", 0, 170, 40, HAND, AMBER)), anim="pop")
    if X.u > 108.6:
        c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.97 * X.p(108.6, 0.6)); c.fill()
        night(c, t, 1080, 140)
        X.sh(109.4, 960, 520, lambda c: sc(sagittarius, t, s=1.8)(c), anim="fade", d=1.0)
        X.sh(110.9, 960, 900, lambda c: hl(c, "constelação de Sagitário", 0, 0, 46), anim="up")


def b3_09(c, t):  # 112.2 - 123.2 nunca se repetiu
    X = Cx(c, t, 3)
    night(c, t, 600, 90)
    ground(c, 900, (0.07, 0.09, 0.07))
    c.save(); c.translate(1100, 880); c.scale(0.7, 0.7); big_ear(c, 1500); c.restore()
    c.save(); c.translate(1100, 300)
    rrect(c, -380, -150, 760, 300, 10); fs(c, (0.06, 0.08, 0.10), 4)
    signal_wave(c, t, 680, 10, 0, flat=False, col=(0.4, 0.6, 0.7))
    c.restore()
    for i, t0 in enumerate((112.3, 115.9, 117.0)):
        X.sh(t0, 1700, 140 + i * 70, lambda c, i=i: text(c, ("de novo", "e de novo", "outros telescópios")[i], 0, 0, 36, HAND, INK), anim="fade")
    X.sh(120.4, 1100, 560, lambda c: stitle(c, "NADA", 0, 0, 110, RED), anim="stamp")
    X.sh(121.1, 1100, 690, lambda c: caption_box(c, "o sinal nunca se repetiu", 40), anim="up")
    X.hist([(0, "think")], [(0, "think"), (120.4, "sad")], x=260, s=0.85)


def b3_10(c, t):  # 123.2 - 145.9 hipóteses
    X = Cx(c, t, 3)
    night(c, t, 1080, 90)
    X.sh(123.2, 960, 120, lambda c: stitle(c, "Hipóteses", 0, 0, 70, INK, AMBER), anim="up")
    X.sh(125.1, 600, 260, lambda c: date_stamp(c, "2024", 50, AMBER), anim="stamp")
    if X.u > 127.0:
        fl = X.p(131.5, 0.4) * (1 - X.p(132.6, 3.0) * 0.6)
        X.sh(127.0, 760, 560, lambda c: h_cloud(c, t, X.p(131.5, 0.8)), anim="fade", d=1.0)
        X.sh(131.6, 360, 560, lambda c: magnetar(c, t, fl), s=0.8, anim="fade")
        X.sh(133.2, 560, 820, lambda c: text(c, "estrela extremamente magnética", 0, 0, 34, HAND, INK), anim="fade")
    X.sh(135.1, 1380, 260, lambda c: date_stamp(c, "2025", 50, AMBER), anim="stamp")
    if X.u > 136.5:
        k = X.p(138.5, 2.0)
        c.save(); c.translate(1380, 600)
        line(c, -280, 0, 280, 0, 2, (0.4, 0.4, 0.45))
        signal_wave(c, t, 560, 5, 150 + 120 * k, 0.5, 0.08, ICE, 5)
        c.restore()
        X.sh(139.3, 1380, 760, lambda c: text(c, "ainda mais forte", 0, 0, 40, HAND, ICE), anim="fade")
    X.sh(142.6, 960, 920, lambda c: date_stamp(c, "NÃO CONFIRMADO", 56, RED), anim="stamp")


def b3_11(c, t):  # 145.9 - 157.8 uma vez só
    X = Cx(c, t, 3)
    night(c, t, 1080, 140)
    ground(c, 980)
    k = clamp01((X.u - 150.0) / 5.0)
    if 0 < k < 1:
        x = 200 + k * 1600
        glow(c, x, 280, 140, ICE, 0.55 * math.sin(k * math.pi))
        circle(c, x, 280, 9, (0.95, 0.97, 1.0), 0)
    X.sh(152.4, 1150, 520, lambda c: stitle(c, "uma vez só", 0, 0, 70, INK, ICE), anim="up")
    X.sh(154.6, 1150, 650, lambda c: text(c, "e quando percebemos, já tinha passado", 0, 0, 40, HAND, INK), anim="fade")
    X.hist([(0, "stand"), (150.0, "point_ru"), (154.6, "stand")], [(0, "think"), (154.6, "sad")], x=420, y=980)
    fog(c, t, 1000, 0.07)


def b3_12(c, t):  # 157.8 - fim transição p/ Cooper
    X = Cx(c, t, 3)
    night(c, t, 1080, 120, (1650, 170))
    k = clamp01((X.u - 157.9) / 7.0)
    c.save(); c.translate(-200 + k * 1700, 300); c.scale(0.5, 0.5); b727(c, t, stair=0.9); c.restore()
    if X.u > 159.9:
        d = X.p(159.9, 4.0)
        c.save(); c.translate(700 + d * 200, 420 + d * 420); c.scale(0.8, 0.8)
        parachute(c, t, open_=clamp01(d * 2))
        person(c, t, 0, 30, 0.6, [(0, "arms_up")], [(0, "neutral")], col=(0.15, 0.15, 0.18), fid=60)
        c.restore()
        for i in range(8):
            bx = 900 + i * 90 + math.sin(t * 2 + i) * 30
            by = 500 + ((X.u - 160 + i * 0.5) * 120) % 500
            c.save(); c.translate(bx, by); c.rotate(math.sin(t * 3 + i)); c.scale(0.25, 0.25); bill(c); c.restore()
    X.sh(161.6, 1300, 1010, lambda c: caption_box(c, "com US$ 200 mil amarrados ao corpo", 40), anim="up")


# ====================================================================== BLOCO 4 — Nº 3 D. B. Cooper
COOPER = dict(col=(0.92, 0.92, 0.90), coat=(0.14, 0.14, 0.16), hair="tuft", fid=70)


def b4_01(c, t):  # 0 - 4.3
    X = Cx(c, t, 4)
    rank_scene(X, 3, "D. B. Cooper", "EUA  •  1971",
               extra=lambda c, t: (c.save(), c.translate(1620, 900), c.scale(0.7, 0.7), parachute(c, t), c.restore()))


def b4_02(c, t):  # 4.3 - 14.8
    X = Cx(c, t, 4)
    night(c, t, 1080, 120, (1650, 160))
    c.save(); c.translate(-100 + X.u * 90, 260); c.scale(0.6, 0.6); b727(c, t, stair=1.0); c.restore()
    if X.u > 7.6:
        d = X.p(7.6, 5.0)
        c.save(); c.translate(600 + d * 150, 400 + d * 380); c.scale(0.9, 0.9)
        parachute(c, t, open_=clamp01(d * 2.5))
        c.push_group(); person(c, t, 0, 30, 0.6, [(0, "arms_up")], [(0, "neutral")], **COOPER); c.pop_group_to_source(); c.paint_with_alpha(1 - X.p(12.0, 1.5))
        c.restore()
    X.sh(4.4, 1350, 540, lambda c: caption_box(c, "sequestro  >  resgate  >  salto", 40), anim="up")
    X.sh(10.7, 1350, 660, lambda c: stitle(c, "nunca encontrado", 0, 0, 56, INK, RED), anim="up")
    X.sh(12.2, 1350, 760, lambda c: text(c, "nem vivo, nem morto", 0, 0, 40, HAND, AMBER), anim="fade")
    c.rectangle(0, 1000, W, 80); rgb(c, (0.06, 0.09, 0.07)); c.fill()
    for i in range(16):
        c.save(); c.translate(60 + i * 125, 1060); pine(c, 140 + (i % 3) * 30, (0.10, 0.17, 0.13)); c.restore()


def b4_03(c, t):  # 14.8 - 35.6 aeroporto de Portland
    X = Cx(c, t, 4)
    X.sh(14.9, 960, 110, lambda c: date_stamp(c, "24 DE NOVEMBRO DE 1971", 52, RED), anim="stamp")
    X.tw(18.3, "véspera do Dia de Ação de Graças", 960, 200, 36, AMBER)
    X.tw(20.5, "Aeroporto de Portland, Oregon", 960, 280, 40, INK)
    c.rectangle(1050, 700, 600, 300); fs(c, (0.25, 0.22, 0.20), 5)
    text(c, "NORTHWEST ORIENT", 1260, 665, 34, TYPE, RED)
    X.fig(person, 1560, 1000, 0.85, [(0, "stand")], [(0, "neutral")], col=(0.30, 0.40, 0.60), fid=71, hair="long")
    X.fig(person, 800, 1010, 1.05, [(0, "stand"), (31.8, "hold")], [(0, "neutral")], appear=23.1,
          col=(0.92, 0.92, 0.90), coat=(0.14, 0.14, 0.16), fid=70)
    X.sh(28.2, 1500, 480, lambda c: (rrect(c, -230, -80, 460, 160, 8), fs(c, PARCH, 4),
                                     text(c, "PORTLAND  >  SEATTLE", 0, -30, 34, TYPE, DARKTXT),
                                     text(c, "VOO 305  •  SÓ IDA", 0, 25, 30, TYPE, BLOOD)), anim="pop")
    X.sh(31.8, 560, 620, lambda c: sc(bills, 3, s=0.7)(c), anim="pop")
    X.sh(33.5, 800, 420, lambda c: hl(c, "\"Dan Cooper\"", 0, 0, 52), anim="up")
    X.hist([(0, "stand")], [(0, "neutral"), (33.5, "think")], x=200, s=0.8)


def cabin(c):
    c.rectangle(0, 0, W, H); rgb(c, (0.11, 0.11, 0.13)); c.fill()
    for i in range(7):
        x = 120 + i * 260
        rrect(c, x, 260, 120, 80, 40); fs(c, (0.06, 0.09, 0.14), 4)
    for i in range(6):
        x = 200 + i * 300
        rrect(c, x, 620, 140, 300, 18); fs(c, (0.25, 0.30, 0.42), 5)
    line(c, 0, 960, W, 960, 3)


def b4_04(c, t):  # 35.6 - 51.5 bilhete
    X = Cx(c, t, 4)
    cabin(c)
    X.fig(person, 700, 980, 1.1, [(0, "stand"), (37.2, "present"), (44.9, "stand")], [(0, "neutral"), (47.2, "angry")], **COOPER)
    X.fig(person, 1250, 980, 1.05, [(0, "stand"), (37.4, "hold"), (40.5, "stand"), (47.3, "head")],
          [(0, "happy"), (40.5, "neutral"), (47.3, "shocked")], col=(0.30, 0.40, 0.60), fid=71, hair="long")
    if 37.2 < X.u < 40.6:
        X.sh(37.2, 1000, 620, lambda c: (rrect(c, -60, -40, 120, 80, 4), fs(c, PARCH, 3)), anim="pop")
    X.sh(39.3, 1250, 210, lambda c: hl(c, "comissária Florence Schaffner", 0, 0, 40), anim="up", t1=46.8)
    X.sh(41.2, 1500, 400, lambda c: text(c, "\"um passageiro dando em cima\"", 0, 0, 34, HAND, INK), anim="fade", t1=46.0)
    if X.u > 47.1:
        X.sh(47.2, 760, 300, lambda c: (speech(c, 700, 190, 60, 150), text(c, "Eu tenho uma bomba.", 0, 0, 56, SERIF, RED)), anim="pop")


def b4_05(c, t):  # 51.5 - 61.4 maleta e exigências
    X = Cx(c, t, 4)
    X.sh(51.6, 600, 600, lambda c: briefcase(c, True, True), s=1.4, anim="pop")
    X.sh(55.9, 1350, 300, lambda c: (sc(money_bag, "US$", s=1.0)(c), text(c, "200 mil", 0, 170, 52, SERIF, AMBER)), anim="drop")
    for i in range(4):
        X.sh(58.5 + i * 0.25, 1180 + i * 120, 760, lambda c: sc(parachute, t, s=0.35)(c), anim="pop")
    X.sh(59.8, 1360, 920, lambda c: text(c, "4 paraquedas  •  em Seattle", 0, 0, 40, TYPE, INK), anim="fade")


def b4_06(c, t):  # 61.4 - 78.0 Seattle, dinheiro, nova rota
    X = Cx(c, t, 4)
    night(c, t, 600, 60)
    ground(c, 880, (0.10, 0.10, 0.12))
    c.set_dash([30, 25]); line(c, 0, 940, W, 940, 4, LYELLOW); c.set_dash([])
    c.save(); c.translate(760, 800); c.scale(1.1, 1.1); b727(c, t); c.restore()
    X.sh(61.5, 960, 120, lambda c: caption_box(c, "Seattle, começo da noite", 44), anim="up")
    X.sh(64.1, 1560, 340, lambda c: (sc(bill_stack, 0, "20", s=1.0)(c), text(c, "números de série anotados", 0, 110, 32, HAND, INK)), anim="pop", t1=72.5)
    for i in range(5):
        X.fig(person, 1300 + i * 110, 1000, 0.55, [(0, "stand"), (69.8, "run")], [(0, "worried")], appear=69.9 + i * 0.15,
              col=(0.4 + 0.1 * (i % 3), 0.35, 0.3), fid=80 + i)
    if X.u > 72.7:
        c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.95 * X.p(72.7, 0.5)); c.fill()
        pts = {"Seattle": (700, 250), "Reno": (820, 600), "Cidade do México": (1300, 960)}
        p = X.p(73.0, 3.0)
        c.set_dash([16, 12])
        line(c, 700, 250, 700 + 120 * min(1, p * 2), 250 + 350 * min(1, p * 2), 5, AMBER)
        if p > 0.5:
            q = (p - 0.5) * 2
            line(c, 820, 600, 820 + 480 * q, 600 + 360 * q, 5, AMBER)
        c.set_dash([])
        for k, (x, y) in pts.items():
            circle(c, x, y, 12, AMBER, 4)
            text(c, k, x + 30, y, 38, TYPE, INK, align="l")
        X.sh(76.3, 1300, 450, lambda c: caption_box(c, "parada em Reno para abastecer", 38), anim="up")


def b4_07(c, t):  # 78.0 - 97.8 escada traseira
    X = Cx(c, t, 4)
    night(c, t, 1080, 120)
    st = X.p(81.8, 2.0)
    bump = math.sin(max(0, X.u - 93.7) * 18) * 8 * max(0, 1 - (X.u - 93.7) / 1.2) if X.u > 93.7 else 0
    c.save(); c.translate(1000, 470); c.rotate(-bump * 0.004); c.scale(1.6, 1.6); b727(c, t, stair=st); c.restore()
    X.sh(78.1, 960, 120, lambda c: caption_box(c, "as ordens", 44), anim="up", t1=93.4)
    X.sh(79.9, 960, 820, lambda c: text(c, "baixo  •  devagar  •  escada aberta", 0, 0, 44, TYPE, AMBER), anim="fade")
    X.sh(84.0, 960, 940, lambda c: text(c, "o 727 tinha uma escada na cauda", 0, 0, 36, HAND, INK), anim="fade")
    if X.u > 89.0:
        on = int(X.u * 3) % 2 == 0
        X.sh(89.0, 1600, 200, lambda c: (circle(c, 0, 0, 30, AMBER if on else (0.3, 0.25, 0.1), 5),
                                         glow(c, 0, 0, 120, AMBER, 0.4) if on else None, text(c, "~20h", 0, 70, 36, TYPE, INK)), anim="pop")
    X.sh(93.8, 960, 120, lambda c: text(c, "um tranco na cauda", 0, 0, 40, HAND, RED), anim="fade")


def b4_08(c, t):  # 97.8 - 113.3 cabine vazia, chuva, floresta
    X = Cx(c, t, 4)
    if X.u < 101.2:
        cabin(c)
        X.sh(98.0, 960, 430, lambda c: stitle(c, "VAZIA", 0, 0, 110, INK, RED), anim="stamp")
        X.sh(98.6, 960, 140, lambda c: caption_box(c, "pouso em Reno", 44), anim="up")
        return
    night(c, t, 300, 30)
    rnd = random.Random(int(t * 20))
    for _ in range(90):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        line(c, x, y, x - 14, y + 40, 2, (0.55, 0.62, 0.72))
    c.rectangle(0, 900, W, 180); rgb(c, (0.05, 0.08, 0.06)); c.fill()
    for i in range(18):
        c.save(); c.translate(40 + i * 110, 1000 + (i % 2) * 30); pine(c, 200 + (i % 4) * 40, (0.08, 0.15, 0.11)); c.restore()
    d = X.p(108.4, 4.5)
    c.save(); c.translate(1300 - d * 300, 160 + d * 560); c.rotate(d * 6)
    person(c, t, 0, 0, 0.5, [(0, "arms_up")], [(0, "neutral")], **COOPER); c.restore()
    X.sh(101.3, 600, 150, lambda c: caption_box(c, "chuva, vento forte", 42), anim="up")
    X.sh(105.2, 600, 260, lambda c: text(c, "sudoeste do estado de Washington", 0, 0, 36, HAND, INK), anim="fade")
    X.sh(110.6, 600, 400, lambda c: date_stamp(c, "~300 km/h", 52, AMBER), anim="stamp")


def b4_09(c, t):  # 113.3 - 128.3 nada encontrado / nome errado / gravata
    X = Cx(c, t, 4)
    night(c, t, 500, 50)
    c.rectangle(0, 700, W, 380); rgb(c, (0.05, 0.08, 0.06)); c.fill()
    for i in range(18):
        c.save(); c.translate(40 + i * 110, 800 + (i % 2) * 30); pine(c, 200 + (i % 4) * 40, (0.08, 0.15, 0.11)); c.restore()
    X.sh(113.3, 960, 120, lambda c: caption_box(c, "muitos acreditam que ele não sobreviveu", 40), anim="up", t1=121.0)
    for i, (lab, t0) in enumerate((("corpo", 116.5), ("paraquedas", 118.4), ("maleta", 119.7))):
        X.sh(t0, 560 + i * 400, 330, lambda c, lab=lab: nope(c, lab, 48), anim="pop", t1=121.0)
    if X.u > 121.1:
        c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.7 * X.p(121.1, 0.5)); c.fill()
        X.sh(121.3, 700, 470, lambda c: newspaper(c, "D. B. COOPER", "o nome que a imprensa errou"), s=1.5, anim="drop")
        X.sh(125.5, 1450, 520, lambda c: (sc(clip_tie, s=1.4)(c), text(c, "deixada na poltrona", 0, 300, 36, HAND, INK)), anim="pop")
        glow(c, 1450, 520, 260, AMBER, 0.10 * X.p(125.5))


def b4_10(c, t):  # 128.3 - 141.8 FBI
    X = Cx(c, t, 4)
    X.sh(128.4, 560, 560, lambda c: folder(c, "FBI", True), s=1.5, anim="drop")
    X.sh(129.0, 560, 900, lambda c: text(c, "45 anos  •  centenas de suspeitos", 0, 0, 38, TYPE, INK), anim="fade")
    for i in range(6):
        X.sh(130.2 + i * 0.2, 1100 + (i % 3) * 230, 300 + (i // 3) * 300,
             lambda c: photo(c, lambda c: (circle(c, 0, -10, 45, (0.15, 0.15, 0.17), 4), text(c, "?", 0, -10, 60, SERIF, AMBER)), 180, 210), anim="pop")
    X.sh(132.0, 1330, 900, lambda c: date_stamp(c, "2016: INVESTIGAÇÃO ENCERRADA", 40, RED), anim="stamp")
    X.sh(138.5, 960, 1010, lambda c: caption_box(c, "e então...", 40), anim="up")


def b4_11(c, t):  # 141.8 - 171.9 Tena Bar
    X = Cx(c, t, 4)
    night(c, t, 500, 60)
    c.rectangle(0, 560, W, 260); rgb(c, (0.06, 0.10, 0.15)); c.fill()                         # rio
    for i in range(10):
        x = (i * 220 + X.u * 30) % (W + 200) - 100
        line(c, x, 620 + (i % 3) * 50, x + 90, 620 + (i % 3) * 50, 3, (0.25, 0.35, 0.45))
    c.move_to(0, 820); c.curve_to(600, 780, 1300, 800, W, 760); c.line_to(W, H); c.line_to(0, H); c.close_path()
    fs(c, (0.40, 0.34, 0.24), 4)                                                                # praia
    X.sh(141.9, 960, 110, lambda c: date_stamp(c, "FEVEREIRO DE 1980", 52, RED), anim="stamp")
    X.tw(148.4, "Rio Columbia  •  Tena Bar", 960, 210, 40, ICE)
    X.fig(person, 700, 960, 0.75, [(0, "stand"), (146.8, "hold")], [(0, "happy"), (151.2, "shocked")], appear=144.2,
          col=(0.70, 0.35, 0.25), fid=90)
    X.sh(145.9, 700, 330, lambda c: hl(c, "Brian Ingram, 8 anos", 0, 0, 40), anim="up", t1=158.5)
    X.sh(151.3, 1120, 930, lambda c: sc(bill_stack, 0.9, "20", s=1.0)(c), anim="pop")
    X.sh(152.0, 1330, 990, lambda c: sc(bill_stack, 0.7, "20", s=0.8)(c), anim="pop")
    X.sh(155.5, 1450, 480, lambda c: stitle(c, "US$ 5.800", 0, 0, 80, AMBER, AMBER), anim="stamp")
    X.sh(159.0, 1450, 610, lambda c: (text(c, "números de série batem", 0, 0, 38, TYPE, INK), at(260, 0, sc(check_icon, 26))(c)), anim="fade")
    if X.u > 163.4:
        c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.95 * X.p(163.4, 0.5)); c.fill()
        X.sh(163.5, 560, 560, lambda c: (donut(c, 0.029, 220, 70, AMBER), text(c, "achado", 0, -20, 36, TYPE, AMBER),
                                         text(c, "3%", 0, 30, 44, SERIF, INK)), anim="pop")
        X.sh(164.6, 1300, 480, lambda c: stitle(c, "o resto nunca apareceu", 0, 0, 52, INK, RED), anim="up")
        X.sh(166.5, 1300, 680, lambda c: sc(big_q, 150, AMBER)(c), anim="pop")


def b4_12(c, t):  # 171.9 - fim transição p/ Hinterkaifeck
    X = Cx(c, t, 4)
    night(c, t, 650, 90, (1600, 170))
    c.save(); c.translate(1100, 930); farmhouse(c, t, attic=X.p(178.1, 1.0), w=780); c.restore()
    snow(c, t, 50, 30, 0.5)
    c.rectangle(0, 930, W, 150); rgb(c, (0.70, 0.74, 0.80), 0.18); c.fill()
    X.sh(172.0, 960, 140, lambda c: caption_box(c, "alguém que não sumiu", 44), anim="up")
    X.sh(178.1, 960, 250, lambda c: stitle(c, "alguém que ficou", 0, 0, 60, INK, AMBER), anim="up")
    fog(c, t, 980, 0.08)


# ====================================================================== BLOCO 5 — Nº 2 Hinterkaifeck
def b5_01(c, t):
    X = Cx(c, t, 5)
    rank_scene(X, 2, "Hinterkaifeck", "Baviera, Alemanha  •  1922",
               extra=lambda c, t: (c.save(), c.translate(1600, 1000), c.scale(0.45, 0.45), farmhouse(c, t, attic=1.0), c.restore()))


def snowfield(c, t, y=930, n=50):
    night(c, t, 650, 90, (1600, 170))
    snow(c, t, n, 30, 0.5)
    c.rectangle(0, y, W, H - y); rgb(c, (0.70, 0.74, 0.80), 0.18); c.fill()


def forest_edge(c, x0=0, n=5, y=930):
    for i in range(n):
        c.save(); c.translate(x0 + 60 + i * 95, y + (i % 2) * 20); pine(c, 260 + (i % 3) * 50, (0.10, 0.17, 0.14)); c.restore()


FAM = [("Andreas, 63", 23.2, (0.40, 0.34, 0.26), "tuft", 1.0), ("Cäzilia", 27.15, (0.36, 0.28, 0.32), "long", 0.95),
       ("Viktoria", 28.68, (0.30, 0.34, 0.44), "long", 0.95), ("Cäzilia, 7", 32.6, (0.60, 0.40, 0.30), "long", 0.6),
       ("Josef, 2", 34.6, (0.45, 0.55, 0.65), "tuft", 0.42)]


def b5_02(c, t):  # 4.3 - 12.6 pegadas
    X = Cx(c, t, 5)
    snowfield(c, t)
    forest_edge(c, 0, 5)
    c.save(); c.translate(1400, 930); farmhouse(c, t, attic=0.0, w=700); c.restore()
    c.save(); c.translate(480, 1010); footprints(c, 10, 75, -6, t, 4.5 + O[5], (0.55, 0.60, 0.70)); c.restore()
    X.sh(10.0, 960, 160, lambda c: caption_box(c, "e não encontrar ninguém", 46), anim="up")


def b5_03(c, t):  # 12.6 - 36.6 a fazenda e a família
    X = Cx(c, t, 5)
    snowfield(c, t, 980)
    X.tw(12.7, "Baviera, Alemanha", 960, 100, 44, INK)
    X.sh(14.5, 960, 190, lambda c: date_stamp(c, "1922", 54, RED), anim="stamp", t1=22.8)
    if X.u < 22.9:
        X.sh(16.5, 1000, 900, lambda c: farmhouse(c, t, w=820), anim="fade", d=0.8)
        X.sh(17.0, 1000, 360, lambda c: hl(c, "HINTERKAIFECK", 0, 0, 52), anim="up")
        X.sh(19.8, 1000, 470, lambda c: caption_box(c, "perto de Waidhofen  •  ~70 km de Munique", 38), anim="up")
    else:
        X.sh(23.0, 960, 200, lambda c: stitle(c, "a família Gruber", 0, 0, 60, INK, AMBER), anim="up")
        for i, (lab, t0, col, hair, sc_) in enumerate(FAM):
            x = 380 + i * 300
            X.fig(person, x, 960, sc_, [(0, "stand")], [(0, "neutral")], appear=t0, col=col, hair=hair, fid=200 + i,
                  mustache=(i == 0))
            X.sh(t0 + 0.2, x, 1030, T(lab, 34, INK), anim="fade")
        X.sh(30.2, 980, 1066, T("(viúva)", 26, AMBER), anim="fade")


def b5_04(c, t):  # 36.6 - 46.2 a empregada foi embora
    X = Cx(c, t, 5)
    snowfield(c, t)
    c.save(); c.translate(900, 930); farmhouse(c, t, attic=0.25 + 0.15 * math.sin(t * 3) if X.u > 41.8 else 0.0, w=760); c.restore()
    k = X.p(37.4, 4.0)
    X.fig(person, 1450 + k * 300, 1000, 0.8, [(0, "stand"), (37.4, "run")], [(0, "worried")], col=(0.50, 0.40, 0.45), hair="long", fid=210)
    X.sh(36.7, 960, 120, lambda c: caption_box(c, "meses antes, a empregada foi embora", 40), anim="up")
    X.sh(42.0, 650, 330, lambda c: text(c, "barulhos no sótão?", 0, 0, 40, HAND, AMBER), anim="fade")
    X.sh(44.4, 960, 230, lambda c: text(c, "\"a casa é assombrada\"", 0, 0, 40, HAND, INK), anim="fade")


def b5_05(c, t):  # 46.2 - 62.4 pegadas até a porta, passos no sótão
    X = Cx(c, t, 5)
    snowfield(c, t)
    forest_edge(c, 0, 5)
    c.save(); c.translate(1300, 930); farmhouse(c, t, attic=X.p(59.2, 0.6) * (0.6 + 0.4 * math.sin(t * 6)), w=760); c.restore()
    X.sh(46.3, 960, 110, lambda c: date_stamp(c, "MARÇO DE 1922", 54, RED), anim="stamp")
    X.sh(51.0, 960, 220, lambda c: hl(c, "Andreas contou aos vizinhos", 0, 0, 40), anim="up")
    c.save(); c.translate(500, 1010); footprints(c, 9, 70, -2, t, 53.3 + O[5], (0.55, 0.60, 0.70)); c.restore()
    X.sh(57.8, 1300, 1040, lambda c: text(c, "fechadura quebrada", 0, 0, 34, HAND, RED), anim="fade")
    X.sh(59.3, 1080, 420, lambda c: stitle(c, "passos no sótão", 0, 0, 52, AMBER, AMBER), anim="up")


def b5_06(c, t):  # 62.4 - 75.3 sótão vazio, chave, jornal
    X = Cx(c, t, 5)
    poly(c, [(0, 1080), (960, 120), (1920, 1080)]); fs(c, (0.14, 0.11, 0.09), 6)
    for k in range(5):
        y = 300 + k * 160
        line(c, 960 - (y - 120) * 1.0, y, 960 + (y - 120) * 1.0, y, 6, (0.30, 0.22, 0.15))
    glow(c, 700, 760, 320, AMBER, 0.22)
    X.fig(person, 700, 1000, 0.95, [(0, "hold")], [(0, "worried"), (64.4, "shocked")], col=(0.40, 0.34, 0.26), fid=200, mustache=True,
          prop=("r", lambda c, tt: lantern(c, tt, 0.6)))
    X.sh(64.5, 1200, 520, lambda c: stitle(c, "ninguém", 0, 0, 64, INK), anim="fade")
    if X.u > 65.9:
        c.rectangle(0, 0, W, H); rgb(c, (0.03, 0.03, 0.04), 0.99 * X.p(65.9, 0.5)); c.fill()
        X.sh(66.0, 500, 450, lambda c: (old_key(c), at(0, 120, T("uma chave sumiu", 38))(c)), anim="pop")
        X.sh(68.2, 1300, 440, lambda c: newspaper(c, "MUNIQUE", "jornal que ninguém ali comprava"), s=1.3, anim="drop")
        X.sh(73.0, 960, 900, lambda c: nope(c, "não chamou a polícia", 44), anim="up")


def b5_07(c, t):  # 75.3 - 82.7 a nova empregada
    X = Cx(c, t, 5)
    snowfield(c, t)
    c.save(); c.translate(1250, 930); farmhouse(c, t, w=760); c.restore()
    X.sh(75.4, 960, 110, lambda c: date_stamp(c, "31 DE MARÇO DE 1922", 54, RED), anim="stamp")
    k = X.p(77.0, 3.0)
    X.fig(person, 300 + k * 450, 1000, 0.9, [(0, "run"), (80.0, "stand")], [(0, "neutral")], appear=76.8,
          col=(0.55, 0.42, 0.40), hair="long", fid=211)
    X.sh(78.7, 600, 330, lambda c: hl(c, "Maria Baumgartner", 0, 0, 42), anim="up")
    X.sh(80.0, 1650, 380, lambda c: (sc(hourglass, t, s=0.6)(c), at(0, 110, T("uma única tarde", 36, AMBER))(c)), anim="pop")


def b5_08(c, t):  # 82.7 - 91.6 a noite
    X = Cx(c, t, 5)
    night(c, t, 1080, 70)
    for i in range(6):
        x = 460 + i * 200
        out_t = 83.9 + i * 0.25
        if X.u < out_t:
            c.save(); c.translate(x, 560); candle(c, t + i); c.restore()
        else:
            c.save(); c.translate(x, 560); c.push_group(); candle(c, 0); c.pop_group_to_source(); c.paint_with_alpha(0.25); c.restore()
            if X.u < out_t + 2.5:
                smoke(c, t, x, 480, 160, 0.18 * (1 - (X.u - out_t) / 2.5), seed=i)
    X.sh(82.8, 960, 180, lambda c: stitle(c, "Naquela noite", 0, 0, 64, INK, RED), anim="fade")
    X.sh(86.7, 760, 830, lambda c: caption_box(c, "4 no celeiro", 40), anim="up")
    X.sh(88.7, 1220, 830, lambda c: caption_box(c, "2 dentro de casa", 40), anim="up")


def b5_09(c, t):  # 91.6 - 110.4 alguém ficou
    X = Cx(c, t, 5)
    snowfield(c, t)
    c.save(); c.translate(1300, 930); farmhouse(c, t, attic=0.4, w=760, smoke_on=X.u > 101.2); c.restore()
    X.sh(91.7, 600, 150, lambda c: date_stamp(c, "4 DIAS DEPOIS", 54, RED), anim="stamp")
    X.sh(98.3, 600, 280, lambda c: caption_box(c, "a parte mais perturbadora", 40), anim="up")
    X.sh(101.3, 600, 400, lambda c: stitle(c, "alguém continuou lá", 0, 0, 54, AMBER, AMBER), anim="up")
    items = [(104.4, "gado alimentado"), (106.2, "pão comido"), (108.4, "carne cortada")]
    for i, (t0, lab) in enumerate(items):
        X.sh(t0, 420, 560 + i * 110, lambda c, lab=lab: (sc(check_icon, 22)(c), text(c, lab, 40, 0, 40, TYPE, INK, align="l")), anim="left")
    X.sh(106.4, 760, 670, lambda c: sc(bread, s=0.5)(c), anim="pop")


def b5_10(c, t):  # 110.4 - 118.2 a lanterna
    X = Cx(c, t, 5)
    snowfield(c, t)
    c.save(); c.translate(1250, 930); farmhouse(c, t, w=760, smoke_on=True); c.restore()
    k = X.p(110.5, 4.0)
    X.fig(person, 200 + k * 380, 1000, 0.85, [(0, "run"), (114.6, "head")], [(0, "neutral"), (115.3, "shocked")],
          col=(0.35, 0.38, 0.30), fid=212)
    X.sh(110.6, 960, 140, lambda c: caption_box(c, "um homem que passou por ali", 40), anim="up")
    X.sh(113.5, 1050, 340, lambda c: text(c, "fumaça na chaminé", 0, 0, 38, HAND, INK), anim="fade")
    if X.u > 115.3:
        a = X.p(115.3, 0.4) * (1 - 0.5 * X.p(116.5, 1.5))
        glow(c, 1000, 820, 700, (1.0, 0.92, 0.70), 0.75 * a)
        glow(c, 1000, 820, 200, (1.0, 1.0, 0.95), 0.9 * a)


def b5_11(c, t):  # 118.2 - 140.7 investigação
    X = Cx(c, t, 5)
    X.sh(118.3, 420, 500, lambda c: folder(c, "INTERROGATÓRIOS", True), s=1.2, anim="drop")
    X.sh(121.0, 960, 560, lambda c: (glow(c, 0, -60, 220, RED, 0.12), mattock(c)), s=1.1, anim="pop")
    X.sh(123.4, 960, 860, lambda c: text(c, "escondido no sótão", 0, 0, 38, HAND, INK), anim="fade")
    X.sh(125.0, 960, 940, lambda c: text(c, "achado na demolição, 1923", 0, 0, 34, TYPE, AMBER), anim="fade")
    X.sh(128.3, 1480, 300, lambda c: date_stamp(c, "1955: CASO ENCERRADO", 44, RED), anim="stamp")
    X.sh(133.7, 1480, 480, lambda c: date_stamp(c, "2007", 48, AMBER), anim="stamp")
    for i in range(3):
        X.fig(person, 1330 + i * 150, 900, 0.55, [(0, "stand"), (137.0, "think")], [(0, "think")], appear=134.8 + i * 0.2,
              col=(0.25, 0.30, 0.45), fid=220 + i, hat="pilot")
    X.sh(139.0, 1480, 1010, lambda c: nope(c, "nenhum nome", 40), anim="up")


def b5_12(c, t):  # 140.7 - 156.0 a pergunta
    X = Cx(c, t, 5)
    snowfield(c, t)
    c.save(); c.translate(1250, 930); farmhouse(c, t, attic=0.6 + 0.3 * math.sin(t * 2), w=760); c.restore()
    X.sh(140.8, 960, 110, lambda c: caption_box(c, "a pergunta que ninguém responde", 42), anim="up")
    for i, (t0, lab) in enumerate(((144.1, "os passos no sótão"), (145.6, "as pegadas na neve"), (147.3, "a chave que sumiu"))):
        X.sh(t0, 640, 260 + i * 80, lambda c, lab=lab: text(c, lab, 0, 0, 40, HAND, INK), anim="left", t1=148.8)
    X.sh(149.0, 960, 300, lambda c: stitle(c, "Quanto tempo alguém viveu ali?", 0, 0, 58, INK, AMBER), anim="up")
    X.hist([(0, "stand"), (144.1, "think"), (149.0, "point_r")], [(0, "worried"), (149.0, "think")], x=260)
    fog(c, t, 980, 0.08)


def b5_13(c, t):  # 156.0 - fim: rumo ao Brasil
    X = Cx(c, t, 5)
    hill_bg(c, t, 1080, dusk=True)
    X.sh(156.2, 960, 180, lambda c: stitle(c, "O número um", 0, 0, 64, INK, RED), anim="up")
    X.sh(159.3, 960, 320, lambda c: stitle(c, "aconteceu no Brasil", 0, 0, 70, AMBER, AMBER), anim="up")
    X.sh(161.6, 960, 460, lambda c: caption_box(c, "Niterói  •  agosto", 40), anim="up")
    fog(c, t, 1000, 0.08)


# ====================================================================== BLOCO 6 — Nº 1 Máscaras de chumbo
SUIT1 = dict(col=(0.88, 0.88, 0.86), coat=(0.24, 0.24, 0.28), hair="tuft", fid=100)
SUIT2 = dict(col=(0.88, 0.88, 0.86), coat=(0.32, 0.27, 0.22), hair="spiky", fid=101)


def hill_bg(c, t, y=1000, col=(0.08, 0.12, 0.10), dusk=False):
    if dusk:
        g = cairo.LinearGradient(0, 0, 0, y)
        g.add_color_stop_rgb(0, 0.06, 0.07, 0.12); g.add_color_stop_rgb(1, 0.22, 0.12, 0.10)
        c.rectangle(0, 0, W, y); c.set_source(g); c.fill()
    else:
        stars(c, t, 80, 600)
    c.save(); c.translate(960, y); morro(c, 2300, 520, col); c.restore()


def b6_01(c, t):  # 0 - 4.1
    X = Cx(c, t, 6)
    rank_scene(X, 1, "As máscaras de chumbo", "Niterói, Brasil  •  1966", col=RED,
               extra=lambda c, t: (c.save(), c.translate(1620, 900), c.scale(0.8, 0.8), lead_mask(c), c.restore()))


def b6_02(c, t):  # 4.1 - 18.6 gancho
    X = Cx(c, t, 6)
    hill_bg(c, t, 1080, dusk=True)
    X.sh(4.2, 960, 160, lambda c: caption_box(c, "dois homens, lado a lado, no alto de um morro", 40), anim="up")
    X.sh(8.1, 640, 540, lambda c: (raincoat(c), at(0, -100, sc(clip_tie, (0.20, 0.18, 0.30), s=0.35))(c)), s=0.9, anim="pop")
    X.sh(8.2, 640, 760, lambda c: text(c, "de terno", 0, 0, 40, HAND, INK), anim="fade")
    X.sh(9.2, 1280, 500, lambda c: (glow(c, 0, 0, 260, RED, 0.12), lead_mask(c)), s=1.2, anim="pop")
    X.sh(9.8, 1280, 680, lambda c: text(c, "máscaras de chumbo", 0, 0, 40, HAND, INK), anim="fade")
    X.sh(12.1, 960, 960, lambda c: (rrect(c, -360, -60, 720, 120, 6), fs(c, PARCH, 4),
                                    text(c, "16:30 ... 18:30 ... aguardar sinal ...", 0, 0, 34, HAND, DARKTXT)), anim="up")
    fog(c, t, 1000, 0.07)


def b6_03(c, t):  # 18.6 - 39.9 quem eram
    X = Cx(c, t, 6)
    X.sh(18.7, 960, 110, lambda c: date_stamp(c, "AGOSTO DE 1966", 54, RED), anim="stamp")
    if X.u < 32.9:
        X.fig(person, 720, 960, 1.0, [(0, "stand"), (24.6, "hold")], [(0, "neutral")], appear=21.6, **SUIT1)
        X.fig(person, 1200, 960, 1.0, [(0, "stand"), (24.6, "hold")], [(0, "neutral")], appear=23.0, **SUIT2)
    X.sh(21.7, 720, 300, lambda c: hl(c, "Manoel Pereira da Cruz", 0, 0, 38), anim="up", t1=32.3)
    X.sh(23.1, 1200, 380, lambda c: hl(c, "Miguel José Viana", 0, 0, 38), anim="up", t1=32.3)
    X.sh(24.6, 960, 620, lambda c: (sc(monitor, lambda c: signal_wave(c, t, 300, 6, 60, 0.5, 0.1, LGREEN, 3), 300, 190, s=0.8)(c)), anim="pop", t1=32.3)
    X.sh(25.3, 960, 1035, lambda c: text(c, "técnicos em eletrônica, ~30 anos", 0, 0, 36, TYPE, INK), anim="fade", t1=32.3)
    if X.u > 29.2:
        c.rectangle(0, 180, W, 900); rgb(c, (0.05, 0.06, 0.07), 1.0 * X.p(32.3, 0.5)); c.fill()
    if X.u > 32.4:
        p = X.p(37.8, 2.0)
        cx, cy, nx, ny = 1500, 380, 560, 820
        c.set_dash([16, 12]); line(c, cx, cy, cx + (nx - cx) * p, cy + (ny - cy) * p, 5, AMBER); c.set_dash([])
        for (x, y, lab) in ((cx, cy, "Campos dos Goytacazes"), (nx, ny, "Niterói")):
            circle(c, x, y, 14, AMBER, 4); text(c, lab, x, y + 50, 38, TYPE, INK)
        X.sh(32.5, 960, 600, lambda c: caption_box(c, "17 de agosto: \"comprar material de trabalho\"", 38), anim="up")


def b6_04(c, t):  # 39.9 - 57.6 compras, nervosismo
    X = Cx(c, t, 6)
    ground(c, 980)
    X.sh(40.9, 420, 560, lambda c: (raincoat(c), at(70, 30, sc(raincoat, (0.60, 0.55, 0.34), s=0.9))(c)), s=0.9, anim="pop")
    X.sh(41.4, 420, 820, lambda c: text(c, "capas de chuva", 0, 0, 38, HAND, INK), anim="fade")
    X.sh(43.9, 820, 600, lambda c: water_bottle(c), s=1.1, anim="pop")
    X.sh(44.4, 820, 820, lambda c: text(c, "1 garrafa de água", 0, 0, 38, HAND, INK), anim="fade")
    X.fig(person, 1250, 980, 0.95, [(0, "stand")], [(0, "neutral")], appear=45.8, col=(0.70, 0.35, 0.35), hair="long", fid=102)
    X.fig(person, 1620, 980, 1.0, [(0, "stand"), (50.9, "hold")], [(0, "neutral"), (48.6, "worried")], appear=48.5, **SUIT2)
    if X.u > 50.9:
        X.sh(50.9, 1620, 430, lambda c: sc(clock, X.t * 2, s=0.7)(c), anim="pop")
        sweat_k = int(X.u * 3) % 2
        c.save(); c.translate(1690, 720 - sweat_k * 6); sweat(c, 12); c.restore()
    X.sh(48.6, 1420, 200, lambda c: caption_box(c, "\"muito nervoso\"", 40), anim="up")
    if X.u > 53.6:
        c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.96 * X.p(53.6, 0.6)); c.fill()
        c.save(); c.translate(960, 1080); morro(c, 2000, 640, (0.08, 0.12, 0.10)); c.restore()
        X.sh(55.3, 960, 300, lambda c: stitle(c, "Morro do Vintém", 0, 0, 70, INK, AMBER), anim="up")


def b6_05(c, t):  # 57.6 - 79.3 a descoberta
    X = Cx(c, t, 6)
    hill_bg(c, t, 1080)
    X.sh(57.7, 960, 110, lambda c: date_stamp(c, "20 DE AGOSTO DE 1966", 52, RED), anim="stamp", t1=69.3)
    X.sh(59.4, 1300, 320, lambda c: kite(c, X.t), anim="pop", t1=69.3)
    X.fig(person, 1050, 600, 0.6, [(0, "stand"), (61.3, "shrug")], [(0, "happy"), (61.3, "shocked")], appear=59.3, col=(0.30, 0.50, 0.40), fid=103)
    X.sh(63.4, 560, 300, lambda c: caption_box(c, "cerca de 1 dia para chegar ao local", 38), anim="up", t1=69.3)
    if X.u > 69.4:
        c.rectangle(0, 0, W, H); rgb(c, (0.03, 0.04, 0.03), 0.98 * X.p(69.4, 0.6)); c.fill()
        rnd = random.Random(5)
        for _ in range(140):
            x = rnd.uniform(0, W); y = rnd.uniform(700, 1080)
            line(c, x, y, x + rnd.uniform(-10, 10), y - rnd.uniform(20, 50), 3, (0.25, 0.36, 0.24))
        X.sh(69.6, 960, 160, lambda c: caption_box(c, "lado a lado, sobre o mato", 42), anim="up")
        X.sh(72.7, 600, 560, lambda c: (raincoat(c), at(0, -100, sc(clip_tie, (0.20, 0.18, 0.30), s=0.35))(c)), s=0.8, anim="fade")
        X.sh(75.0, 1250, 520, lambda c: (glow(c, 0, 0, 280, RED, 0.12), lead_mask(c)), s=1.4, anim="pop")
        X.sh(77.0, 1250, 760, lambda c: text(c, "chumbo, feitas à mão", 0, 0, 42, HAND, INK), anim="fade")


def b6_06(c, t):  # 79.3 - 90.3 evidências
    X = Cx(c, t, 6)
    X.sh(79.4, 520, 160, lambda c: nope(c, "sinais de luta", 44), anim="pop")
    X.sh(80.9, 1400, 160, lambda c: nope(c, "ferimentos graves", 44), anim="pop")
    X.sh(82.6, 480, 600, lambda c: water_bottle(c, True), s=1.1, anim="pop")
    X.sh(83.4, 480, 820, lambda c: text(c, "garrafa vazia", 0, 0, 36, HAND, INK), anim="fade")
    X.sh(85.4, 960, 620, lambda c: (rrect(c, -150, -80, 300, 160, 14), fs(c, (0.70, 0.74, 0.80), 5),
                                    line(c, -150, 0, 150, 0, 3, (0.5, 0.55, 0.6))), anim="pop")
    X.sh(85.9, 960, 820, lambda c: text(c, "toalhas molhadas", 0, 0, 36, HAND, INK), anim="fade")
    X.sh(87.3, 1450, 600, lambda c: notebook(c), anim="pop")
    X.sh(88.5, 1450, 860, lambda c: text(c, "um bilhete", 0, 0, 40, HAND, AMBER), anim="fade")


def b6_07(c, t):  # 90.3 - 103.6 o bilhete
    X = Cx(c, t, 6)
    c.save(); c.translate(960, 560); c.scale(2.6, 2.4); notebook(c); c.restore()
    lines = [(91.72, "16:30  estar no local determinado"), (95.18, "18:30  ingerir cápsulas"),
             (98.13, "após efeito, proteger metais"), (100.7, "aguardar sinal"), (102.08, "máscara")]
    for i, (t0, s) in enumerate(lines):
        X.tw(t0, s, 600, 270 + i * 120, 52, (0.12, 0.12, 0.30), align="l", font=HAND, cps=26)
    X.sh(90.4, 960, 1020, lambda c: caption_box(c, "transcrição do bilhete encontrado", 32), anim="up")


def b6_08(c, t):  # 103.6 - 118.4 perguntas e necrópsia
    X = Cx(c, t, 6)
    for i, (s, t0) in enumerate((("cápsulas?", 103.7), ("sinal?", 104.7), ("metais?", 105.6))):
        X.sh(t0, 480 + i * 480, 220, lambda c, s=s: (big_q(c, 90, AMBER), text(c, s, 0, 120, 44, TYPE, INK)), anim="pop")
    X.sh(107.9, 640, 700, lambda c: folder(c, "NECRÓPSIA", True), s=1.3, anim="drop")
    X.sh(113.2, 1350, 620, lambda c: nope(c, "exame toxicológico", 44), anim="pop")
    X.sh(115.5, 1350, 840, lambda c: date_stamp(c, "CAUSA DA MORTE: INDETERMINADA", 40, RED), anim="stamp")


def b6_09(c, t):  # 118.4 - 134.5 teorias
    X = Cx(c, t, 6)
    hill_bg(c, t, 1080)
    if X.u > 120.2:
        lit_window_lights(c, t, 1200, 230, 3)
    X.fig(person, 360, 1060, 0.9, [(0, "stand"), (120.3, "point_ru")], [(0, "shocked")], appear=120.2, col=(0.55, 0.45, 0.65), hair="long", fid=104)
    X.sh(118.4, 960, 100, lambda c: caption_box(c, "as teorias", 44), anim="up", t1=127.5)
    X.sh(121.3, 1290, 450, lambda c: text(c, "luzes vermelhas e alaranjadas no céu", 0, 0, 38, HAND, INK), anim="fade", t1=127.5)
    if X.u > 127.7:
        c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.93 * X.p(127.7, 0.5)); c.fill()

        def theory(c, ttl, sub, col):
            rrect(c, -330, -150, 660, 300, 14); fs(c, FILL, 5)
            text(c, ttl, 0, -60, 34, TYPE, col); text(c, sub, 0, 30, 48, SERIF, INK)
        X.sh(127.8, 560, 520, lambda c: theory(c, "TEORIA 1", "encontro com o céu", ICE), anim="left")
        X.sh(131.5, 1360, 520, lambda c: theory(c, "TEORIA 2", "crime disfarçado", RED), anim="right")


def b6_10(c, t):  # 134.5 - 154.4 o grupo espiritualista
    X = Cx(c, t, 6)
    X.fig(person, 360, 1000, 1.0, [(0, "stand"), (134.6, "present")], [(0, "neutral")], appear=134.5, col=(0.40, 0.45, 0.40), fid=105)
    X.sh(134.6, 360, 380, lambda c: hl(c, "relato de um amigo", 0, 0, 40), anim="up")
    X.sh(137.2, 1150, 230, lambda c: caption_box(c, "grupo espiritualista", 44), anim="up")
    X.sh(138.8, 900, 450, lambda c: (candle(c, X.t), at(160, 0, lambda c: candle(c, X.t + 1))(c)), anim="fade")
    X.sh(140.3, 1450, 430, lambda c: (sc(magnetar, X.t, 0.0, s=0.4)(c), text(c, "contato com espíritos ou outros mundos", 0, 140, 30, HAND, INK)), anim="fade")
    X.sh(142.4, 1150, 700, lambda c: text(c, "alguma substância", 0, 0, 40, TYPE, AMBER), anim="fade")
    X.sh(144.6, 860, 900, lambda c: (book(c, "", BLOOD), at(140, 0, lambda c: book(c, "", (0.25, 0.30, 0.45)))(c),
                                      at(330, -10, sc(lead_mask, s=0.45))(c)), anim="pop", s=0.8)
    X.sh(149.5, 1560, 830, lambda c: caption_box(c, "a explicação mais citada", 38), anim="up")
    X.sh(152.0, 1560, 960, lambda c: date_stamp(c, "NUNCA COMPROVADA", 46, RED), anim="stamp")


def b6_11(c, t):  # 154.4 - 164.7 arquivado
    X = Cx(c, t, 6)
    X.sh(154.5, 520, 560, lambda c: folder(c, "ARQUIVADO", True), s=1.5, anim="drop")
    X.sh(157.0, 1350, 220, lambda c: stitle(c, "quase 60 anos depois", 0, 0, 56, INK, AMBER), anim="up")
    for i, (s, t0) in enumerate((("o que tomaram?", 159.6), ("quem marcou o horário?", 160.8), ("que sinal esperavam?", 162.4))):
        X.sh(t0, 1350, 440 + i * 150, lambda c, s=s: text(c, s, 0, 0, 46, HAND, INK), anim="left")


def b6_12(c, t):  # 164.7 - fim
    X = Cx(c, t, 6)
    hill_bg(c, t, 1080, dusk=True)
    X.sh(167.9, 1450, 260, lambda c: (sc(clock, 0, s=0.8)(c), text(c, "18:30", 0, 120, 44, TYPE, AMBER)), anim="fade")
    X.sh(171.3, 1100, 760, lambda c: (lead_mask(c), at(300, 20, sc(lead_mask, s=0.95))(c)), s=0.7, anim="fade", d=1.2)
    if X.u > 174.9:
        X.sh(174.95, 960, 160, lambda c: stitle(c, "E esperaram.", 0, 0, 72, INK, RED), anim="fade", d=1.0)
    X.hist([(0, "stand"), (167.9, "think")], [(0, "sad")], x=300, y=1060)
    fog(c, t, 1000, 0.09)


# ====================================================================== BLOCO 7 — fechamento
ICONS5 = [(5, lambda c: sc(axe, s=0.6)(c)), (4, lambda c: signal_wave(c, 0, 200, 5, 80, 0.5, 0.1, ICE, 4)),
          (3, lambda c: sc(parachute, 0, s=0.5)(c)), (2, lambda c: sc(farmhouse, 0, 1.0, s=0.22)(c)), (1, lambda c: sc(lead_mask, s=0.6)(c))]


def b7_01(c, t):  # 0 - 19.4 recapitulação
    X = Cx(c, t, 7)
    night(c, t, 1080, 100)
    X.sh(0.2, 960, 130, lambda c: stitle(c, "Cinco casos", 0, 0, 72, INK, AMBER), anim="up")
    times = [1.72, 4.0, 6.4, 9.12, 11.76]
    for i, ((n, fn), t0) in enumerate(zip(ICONS5, times)):
        x = 240 + i * 360
        X.sh(t0, x, 520, lambda c, n=n, fn=fn: (rrect(c, -150, -190, 300, 380, 12), fs(c, FILL, 4), at(0, 0, fn)(c),
                                                text(c, "Nº %d" % n, 0, 150, 38, SERIF, AMBER)), anim="pop")
    X.sh(15.5, 960, 900, lambda c: date_stamp(c, "NENHUMA RESPOSTA OFICIAL", 50, RED), anim="stamp")


def b7_02(c, t):  # 19.4 - fim
    X = Cx(c, t, 7)
    night(c, t, 700, 80)
    X.hist([(0, "stand"), (19.4, "present"), (31.5, "wave"), (35.9, "stand")], [(0, "think"), (21.3, "happy")], x=380, s=1.05)
    X.sh(21.3, 1150, 170, lambda c: stitle(c, "Qual é o mais assustador?", 0, 0, 58, INK, AMBER), anim="up")
    X.sh(24.0, 1150, 400, lambda c: (speech(c, 760, 150, -260, 140), text(c, "qual merece um vídeo só dele?", 0, 0, 40, HAND, INK)))
    X.sh(27.2, 1150, 560, lambda c: text(c, "comente aqui embaixo", 0, 0, 38, TYPE, AMBER), anim="fade")
    X.sh(31.6, 1150, 700, lambda c: sc(subscribe_btn, X.u > 33.4, s=0.9)(c))
    X.sh(34.4, 1480, 700, lambda c: sc(bell, s=0.8)(c), rot=math.sin(t * 18) * 0.2 * max(0, 1 - (X.u - 34.4)))
    X.sh(37.6, 1150, 920, lambda c: (text(c, "PONTO CEGO", 0, 0, 80, SERIF, INK), line(c, -300, 55, 300, 55, 3, AMBER)), anim="fade", d=1.2)
    fog(c, t, 1000, 0.07)


# ====================================================================== cronograma
_LOCAL = [
    (1, [(0.0, a01), (6.6, a02), (22.2, a03), (28.5, a04), (34.6, a05)]),
    (2, [(0.0, b2_01), (4.8, b2_02), (17.9, b2_03), (31.8, b2_04), (44.1, b2_05), (65.0, b2_06), (76.3, b2_07),
         (83.2, b2_08), (100.3, b2_09), (111.4, b2_10), (134.9, b2_11), (148.4, b2_12)]),
    (3, [(0.0, b3_01), (4.3, b3_02), (15.3, b3_03), (27.9, b3_04), (38.9, b3_05), (55.3, b3_06), (72.8, b3_07),
         (91.9, b3_08), (112.2, b3_09), (123.2, b3_10), (145.9, b3_11), (157.8, b3_12)]),
    (4, [(0.0, b4_01), (4.3, b4_02), (14.8, b4_03), (35.6, b4_04), (51.5, b4_05), (61.4, b4_06), (78.0, b4_07),
         (97.8, b4_08), (113.3, b4_09), (128.3, b4_10), (141.8, b4_11), (171.9, b4_12)]),
    (5, [(0.0, b5_01), (4.3, b5_02), (12.6, b5_03), (36.6, b5_04), (46.2, b5_05), (62.4, b5_06), (75.3, b5_07),
         (82.7, b5_08), (91.6, b5_09), (110.4, b5_10), (118.2, b5_11), (140.7, b5_12), (156.0, b5_13)]),
    (6, [(0.0, b6_01), (4.1, b6_02), (18.6, b6_03), (39.9, b6_04), (57.6, b6_05), (79.3, b6_06), (90.3, b6_07),
         (103.6, b6_08), (118.4, b6_09), (134.5, b6_10), (154.4, b6_11), (164.7, b6_12)]),
    (7, [(0.0, b7_01), (19.4, b7_02)]),
]


def _build():
    flat = []
    for n, lst in _LOCAL:
        for a, fn in lst:
            flat.append((B(n, a) if a > 0 else (O[n] - (0.0 if n == 1 else 1.0) * 0), fn))
    out = []
    for i, (a, fn) in enumerate(flat):
        b = flat[i + 1][0] if i + 1 < len(flat) else 999.0
        out.append((round(a, 3), round(b, 3), fn))
    return out


SCENES = _build()

SFX = [(B(1, 28.6), "boom"), (B(1, 41.6), "heartbeat"),
       (B(2, 0.1), "boom"), (B(2, 81.85), "boom"), (B(2, 108.5), "bell"), (B(2, 138.1), "heartbeat"),
       (B(3, 0.1), "boom"), (B(3, 90.72), "boom"), (B(3, 120.4), "tum"),
       (B(4, 0.1), "boom"), (B(4, 47.2), "heartbeat"), (B(4, 98.0), "boom"), (B(4, 155.5), "tum"),
       (B(5, 0.1), "boom"), (B(5, 59.2), "heartbeat"), (B(5, 82.8), "bell"), (B(5, 101.3), "boom"),
       (B(6, 0.1), "boom"), (B(6, 91.7), "heartbeat"), (B(6, 115.5), "tum"), (B(6, 174.95), "bell"),
       (B(7, 37.6), "boom")]
