"""O Manuscrito Voynich — Ponto Cego.
Narração: Pedro Lima - Serious (HeyGen / ElevenLabs v4), 4 blocos com 1 s de silêncio entre eles (~751,3 s).
Tempos absolutos (já com os offsets dos blocos): transcricao.txt e palavras.json.
tw("palavra", depois_de) devolve o início da primeira palavra que começa com esse texto depois do tempo dado.
Objetos do manuscrito (páginas, escrita, plantas, zodíaco, piscinas, rosetas) ficam no engine.py (seção Voynich).
"""
import json
import os
import unicodedata

from engine import *

THEME = "classico"

_D = os.path.dirname(os.path.abspath(__file__))
_WORDS = json.load(open(os.path.join(_D, "palavras.json"), encoding="utf-8"))


def _norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(ch for ch in s if ch.isalnum() and not unicodedata.combining(ch))


_TW = {}


def tw(prefix, after=0.0):
    key = (prefix, after)
    if key not in _TW:
        p = _norm(prefix)
        for w in _WORDS:
            if w["t0"] >= after - 0.01 and _norm(w["w"]).startswith(p):
                _TW[key] = w["t0"]
                break
        else:
            raise KeyError(f"palavra não encontrada: {prefix} depois de {after}")
    return _TW[key]


# ------------------------------------------------------------------ mapas (lon, lat)
EUR = make_proj(-11, 35, 36, 60, box=(60, 40, 1860, 1040))
CEN = make_proj(3, 26, 39, 54, box=(140, 90, 1780, 1030))
ITA = make_proj(6, 19.5, 37, 47.5, box=(140, 90, 1780, 1030))
PRAGA = (14.42, 50.09)
ROMA = (12.50, 41.90)
FRASCATI = (12.68, 41.81)
VILNIUS = (25.28, 54.69)
LONDRES = (-0.13, 51.51)
EUROPE = ["europe", "britain", "ireland", "nw_africa", "sardinia_sicily"]

# ------------------------------------------------------------------ figurinos
VOYNICH = dict(shirt=(0.86, 0.86, 0.82), coat=(0.18, 0.18, 0.22), glasses=True, mustache=True, hair="tuft")
PADRE = dict(coat=(0.10, 0.10, 0.12), hat="skullcap", hair=None, shirt=None)
MARCI = dict(coat=(0.30, 0.24, 0.32), hat="skullcap", hair=None, mustache=True, shirt=None)
KIRCHER = dict(coat=(0.10, 0.10, 0.12), hat="skullcap", hat_col=(0.06, 0.06, 0.08), hair=None, shirt=None)
RODOLFO = dict(shirt=(0.50, 0.12, 0.18), coat=(0.22, 0.10, 0.12), hat="crown", mustache=True, hair=None)
BACON = dict(coat=(0.42, 0.30, 0.20), hat="hood", hat_col=(0.42, 0.30, 0.20), hair=None, shirt=None)
DEE = dict(coat=(0.12, 0.12, 0.14), hat="skullcap", mustache=True, hair=None, shirt=None)
KELLEY = dict(coat=(0.32, 0.22, 0.14), hat="hood", hat_col=(0.32, 0.22, 0.14), hair=None, shirt=None)
BARESCH = dict(coat=(0.28, 0.32, 0.26), hat="skullcap", hat_col=(0.30, 0.20, 0.14), mustache=True, hair=None, shirt=None)
NEWBOLD = dict(shirt=(0.86, 0.86, 0.82), coat=(0.20, 0.20, 0.24), glasses=True, mustache=True, hair="tuft")
MANLY = dict(shirt=(0.86, 0.86, 0.82), coat=(0.34, 0.26, 0.20), hair="tuft", mustache=True)
ETHEL = dict(shirt=(0.30, 0.24, 0.36), hair="long")
KRAUS = dict(shirt=(0.86, 0.86, 0.82), coat=(0.16, 0.18, 0.26), glasses=True, hair=None)
FRIEDMAN = dict(shirt=(0.86, 0.86, 0.82), coat=(0.24, 0.24, 0.28), glasses=True, mustache=True, hair="tuft")
GUZY = dict(shirt=(0.36, 0.42, 0.52), glasses=True)
DAVIS = dict(shirt=(0.30, 0.46, 0.52), hair="long", glasses=True)
RUGG = dict(shirt=(0.42, 0.36, 0.30), glasses=True, hair=None)
ESCRIBA = dict(coat=PARCH2, hat="hood", hat_col=PARCH2, hair=None, shirt=None)
SABIO = dict(shirt=(0.80, 0.80, 0.76), coat=(0.20, 0.22, 0.26), hair="tuft")


# ------------------------------------------------------------------ helpers
def HIST(c, t, poses, exprs, appear=None, x=290, y=1010, s=0.95, **kw):
    historiador(c, t, x, y, s, poses, exprs, appear=appear, look=1, **kw)


def faded(c, a, fn):
    if a <= 0.001:
        return
    if a >= 0.999:
        fn(c); return
    c.push_group(); fn(c); c.pop_group_to_source(); c.paint_with_alpha(a)


def fig(c, t, x, y, s, poses=((0, "stand"),), exprs=((0, "neutral"),), alpha=1.0, **kw):
    faded(c, alpha, lambda c: figure(c, t, x, y, s, poses=poses, exprs=exprs, **kw))


def fade_in(t, t0, d=0.8):
    return clamp01((t - t0) / d)


def fade_out(t, t0, d=0.8):
    return 1 - clamp01((t - t0) / d)


def put(c, x, y, fn, s=1.0, a=1.0):
    faded(c, a, lambda c: (c.save(), c.translate(x, y), c.scale(s, s), fn(c), c.restore()))


def night(c, t, horizon=760, moon_xy=(1620, 170)):
    stars(c, t, 80, horizon - 60)
    if moon_xy:
        c.save(); c.translate(*moon_xy); moon(c, 50); c.restore()
        glow(c, moon_xy[0], moon_xy[1], 220, LYELLOW, 0.10)


def ground(c, y=880, col=(0.16, 0.15, 0.16)):
    c.rectangle(0, y, W, H - y); rgb(c, col); c.fill()
    line(c, 0, y, W, y, 4, (0.34, 0.32, 0.32))


def shelves(c, t, a=1.0, x0=0, x1=W):
    """parede de estantes antigas"""
    def f(c):
        rnd = random.Random(4)
        for r in range(4):
            y = 140 + r * 200
            line(c, x0, y + 150, x1, y + 150, 8, (0.30, 0.22, 0.14))
            x = x0 + 20
            while x < x1 - 40:
                bw = rnd.randint(22, 40); bh = rnd.randint(100, 145)
                col = rnd.choice([(0.36, 0.20, 0.14), (0.26, 0.22, 0.16), (0.40, 0.32, 0.20), (0.20, 0.18, 0.22), (0.46, 0.38, 0.26)])
                c.rectangle(x, y + 150 - bh, bw, bh); rgb(c, col); c.fill_preserve(); rgb(c, (0.08, 0.06, 0.05)); c.set_line_width(2); c.stroke()
                x += bw + rnd.randint(1, 4)
    faded(c, a * 0.55, f)


def lectern_book(c, t, x=1150, y=900, opened=True, s=1.0, left="text", right="herbal", seed=1):
    c.save(); c.translate(x, y); c.scale(s, s)
    poly(c, [(-60, 0), (60, 0), (40, -300), (-40, -300)]); fs(c, (0.30, 0.20, 0.12), 5)
    poly(c, [(-300, -300), (300, -300), (330, -380), (-330, -380)]); fs(c, (0.36, 0.24, 0.14), 5)
    c.restore()
    if opened:
        put(c, x, y - 560 * s, lambda c: manuscript_spread(c, left, right, t, 1.0, 0.52, seed=seed), s)
    else:
        put(c, x, y - 560 * s, lambda c: (c.rotate(-0.06), closed_codex(c, 0.75, True, t)), s)


def theory_card(c, n, title_s, icon=None, crossed=0.0, dim=False, w=330, h=420, sub=None):
    rrect(c, -w / 2, -h / 2, w, h, 14); fs(c, (0.13, 0.11, 0.09), 5, PARCH2 if not dim else LGRAY)
    text(c, n, 0, -h / 2 + 44, 32, TYPE, AMBER)
    text(c, title_s, 0, -h / 2 + 96, 38 if len(title_s) < 12 else 30, SERIF, INK if not dim else GRAY)
    if sub:
        text(c, sub, 0, h / 2 - 36, 26, TYPE, GRAY)
    if icon:
        c.save(); c.translate(0, 60); icon(c); c.restore()
    if crossed > 0:
        c.save(); c.scale(crossed, crossed); big_x(c, 120, RED, 14); c.restore()


def counter_text(c, t, t0, n, x, y, size=120, col=INK, d=1.4, prefix="", suffix="", sep=True):
    if t < t0:
        return
    v = int(round(n * ease_out(prog(t, t0, d))))
    s = f"{v:,}".replace(",", ".") if sep else str(v)
    text(c, f"{prefix}{s}{suffix}", x, y, size, SERIF, col)


def x_over(c, t, t0, x, y, s=70):
    show(c, t, t0, x, y, lambda c: big_x(c, s, RED, 14), anim="stamp")


def label_under(fn, s, dy=110, size=32, col=INK):
    return group(fn, at(0, dy, T(s, size, col)))


def cross_icon(c, col=INK):
    line(c, 0, -70, 0, 70, 12, col); line(c, -45, -30, 45, -30, 12, col)


def crown_icon(c):
    poly(c, [(-60, 30), (-70, -40), (-30, -5), (0, -55), (30, -5), (70, -40), (60, 30)]); fs(c, GOLD, 5)
    circle(c, 0, 10, 9, RED, 3)


def lock_icon(c):
    c.new_sub_path(); c.arc(0, -30, 40, math.pi, 2 * math.pi); rgb(c, INK); c.set_line_width(12); c.stroke()
    rrect(c, -60, -30, 120, 100, 12); fs(c, GOLD_D, 5)
    circle(c, 0, 10, 12, (0.10, 0.08, 0.06), 0); c.rectangle(-5, 10, 10, 30); rgb(c, (0.10, 0.08, 0.06)); c.fill()


def bubble_icon(c):
    rrect(c, -80, -60, 160, 100, 30); fs(c, FILL, 6)
    poly(c, [(-30, 38), (-55, 80), (5, 38)]); fs(c, FILL, 6)
    for k in range(3):
        c.save(); c.translate(-50 + k * 40, -2); vword(c, "ol", 22, INK); c.restore()


def gear_icon(c, t=0):
    c.save(); c.rotate(t * 0.4)
    for k in range(8):
        c.save(); c.rotate(k * math.pi / 4); c.rectangle(-14, -78, 28, 26); rgb(c, LGRAY); c.fill_preserve(); fs(c, None, 4); c.restore()
    circle(c, 0, 0, 58, LGRAY, 5); circle(c, 0, 0, 20, (0.10, 0.10, 0.12), 4)
    c.restore()


def mask_icon(c):
    c.move_to(-70, -50); c.curve_to(-70, 60, -20, 80, 0, 80); c.curve_to(20, 80, 70, 60, 70, -50)
    c.curve_to(30, -30, -30, -30, -70, -50); c.close_path(); fs(c, (0.86, 0.84, 0.78), 5)
    ellipse(c, -30, -5, 16, 10); rgb(c, (0.06, 0.06, 0.08)); c.fill()
    ellipse(c, 30, -5, 16, 10); rgb(c, (0.06, 0.06, 0.08)); c.fill()
    c.new_sub_path(); c.arc(0, 30, 24, 0.3, math.pi - 0.3); rgb(c, (0.06, 0.06, 0.08)); c.set_line_width(5); c.stroke()


def card_icon(i, t=0):
    return [lambda c: (c.scale(0.8, 0.8), lock_icon(c)), lambda c: (c.scale(0.8, 0.8), bubble_icon(c)),
            lambda c: (c.scale(0.8, 0.8), gear_icon(c, t)), lambda c: (c.scale(0.8, 0.8), mask_icon(c))][i]


CARDS = [("1", "CÓDIGO"), ("2", "LÍNGUA REAL"), ("3", "LÍNGUA ARTIFICIAL"), ("4", "FARSA")]


def cards_row(c, t, active, t0=0, y=600):
    """os quatro caminhos: fileira pequena no alto (o ativo aceso) e o cartão ativo grande à esquerda"""
    for i, (n, ttl) in enumerate(CARDS):
        put(c, 1000 + i * 190, 190, lambda c, n=n, ttl=ttl, i=i: theory_card(c, n, ttl, card_icon(i, t), dim=(i != active), w=260, h=320),
            0.5, 1.0 if i == active else 0.7)
    n, ttl = CARDS[active]
    show(c, t, t0, 800, y, lambda c: theory_card(c, n, ttl, card_icon(active, t), w=380, h=460), anim="up")


def microscope(c):
    rrect(c, -90, -16, 180, 32, 8); fs(c, DGRAY, 5)
    c.move_to(-40, -16); c.curve_to(-90, -120, -40, -220, 10, -230); rgb(c, INK); c.set_line_width(22); c.stroke()
    c.move_to(-40, -16); c.curve_to(-90, -120, -40, -220, 10, -230); rgb(c, LGRAY); c.set_line_width(14); c.stroke()
    c.save(); c.translate(30, -200); c.rotate(-0.35)
    rrect(c, -22, -130, 44, 170, 10); fs(c, (0.70, 0.60, 0.36), 5)
    rrect(c, -14, 40, 28, 40, 6); fs(c, DGRAY, 4)
    c.restore()
    rrect(c, -10, -90, 110, 16, 4); fs(c, LGRAY, 4)


def glyph_zoom(c, t, word="qokedy", h=120, ticks=0.0, cracks=0.0):
    """palavra do manuscrito em close sobre pergaminho, com traços minúsculos ou rachaduras"""
    w = vword_w(word, h) + 120
    rrect(c, -w / 2, -h * 1.2, w, h * 1.9, 16); fs(c, VELLUM, 5, (0.50, 0.40, 0.26))
    c.save(); c.translate(-w / 2 + 60, h * 0.25); vword(c, word, h, VINK, lw=h * 0.07)
    rnd = random.Random(9)
    if ticks > 0:
        for k in range(int(60 * ticks)):
            x, y = rnd.uniform(0, w - 120), rnd.uniform(-h * 0.9, 0)
            line(c, x, y, x + rnd.uniform(-5, 5), y + rnd.uniform(3, 8), 2, (0.65, 0.20, 0.16))
    if cracks > 0:
        for k in range(int(26 * cracks)):
            x, y = rnd.uniform(0, w - 120), rnd.uniform(-h * 0.9, 0)
            c.move_to(x, y)
            for j in range(4):
                x += rnd.uniform(-8, 8); y += rnd.uniform(2, 7); c.line_to(x, y)
            rgb(c, VELLUM); c.set_line_width(2.4); c.stroke()
    c.restore()


def scribe_desk(c, t, x, lit=1.0, seed=1):
    """escriba encapuzado diante de uma mesa inclinada com vela"""
    c.save(); c.translate(x, 0)
    poly(c, [(40, 900), (60, 900), (60, 760), (40, 760)]); fs(c, (0.30, 0.20, 0.12), 3)
    poly(c, [(-40, 760), (170, 760), (190, 720), (-20, 720)]); fs(c, (0.36, 0.24, 0.14), 4)
    poly(c, [(-10, 752), (160, 752), (176, 724), (6, 724)]); fs(c, VELLUM, 3, (0.50, 0.40, 0.26))
    for k in range(3):
        line(c, 20 + k * 5, 744 - k * 9, 150 + k * 5 - (k % 2) * 30, 744 - k * 9, 2, VINK)
    if lit > 0.02:
        glow(c, 160, 640, 220 * lit, AMBER, 0.30 * lit)
        put(c, 160, 700, lambda c: (c.scale(0.45, 0.45), candle(c, t)), 1.0, lit)
    c.restore()
    figure(c, t, x - 60, 900, 0.62, poses=[(0, "hold")], exprs=[(0, "think")], fid=40 + seed, **ESCRIBA)


def glyph_rain(c, t, a=0.18, seed=3):
    """linhas de escrita ao fundo da tela"""
    def f(c):
        for r in range(9):
            vline(c, 80 + (r % 2) * 60, 120 + r * 110, 1760, 30, seed + r, (0.55, 0.46, 0.32))
    faded(c, a, f)


# ================================================================== BLOCO 1
def s01(c, t):  # 0.0 - 16.4  um livro que ninguém consegue ler
    shelves(c, t, 1.0)
    opened = t > tw("ninguém", 3) + 0.4
    lectern_book(c, t, 1150, 1090, opened, 1.0, "text", "text", 3)
    if not opened:
        glow(c, 1150, 520, 300, AMBER, 0.10)
    show(c, t, 0.3, 1150, 110, T("guardado numa biblioteca dos Estados Unidos", 36), anim="fade", t1=tw("ninguém", 3) - 0.2)
    show(c, t, tw("ninguém", 3), 1150, 110, lambda c: stitle(c, "NINGUÉM NO MUNDO CONSEGUE LER", 0, 0, 56, AMBER, AMBER), anim="up")
    show(c, t, tw("Não", 6), 1150, 200, T("não é uma língua esquecida", 36), anim="fade", t1=12.2)
    show(c, t, tw("Não", 8.3), 1150, 250, T("não é um alfabeto antigo", 36), anim="fade", t1=12.2)
    show(c, t, tw("escrita", 12), 1150, 220, lambda c: hl(c, "uma escrita que não se parece com nenhuma outra", 0, 0, 38), anim="up")
    fog(c, t, 960, 0.06)
    HIST(c, t, [(0, "stand"), (4.0, "point_r"), (12.5, "think")], [(0, "neutral"), (4.0, "worried"), (12.5, "think")], appear=0.4, x=260)


def s02(c, t):  # 16.4 - 37.9  240 páginas, letra elegante, desenhos
    shelves(c, t, 0.6)
    if t < tw("Plantas", 26):
        L, R = "text", "text"
    elif t < tw("Mapas", 29):
        L, R = "text", "herbal"
    elif t < tw("pequenas", 31):
        L, R = "zodiac", "herbal"
    else:
        L, R = "zodiac", "bath"
    put(c, 1150, 560, lambda c: manuscript_spread(c, L, R, t, 1.0, 0.72, seed=11), 1.0)
    counter_text(c, t, 16.7, 240, 1150, 105, 80, AMBER, 1.2, prefix="~ ", suffix=" PÁGINAS DE PERGAMINHO", sep=False)
    if tw("letra", 20) < t < tw("desenhos", 26) + 0.2:
        a = fade_in(t, tw("letra", 20)) * fade_out(t, tw("desenhos", 26) - 0.3)
        put(c, 1150, 980, lambda c: (caption_box(c, " " * 40, 44, 900), c.translate(-330, 18), vline(c, 0, 0, 660, 40, 21, INK)), 1.0, a)
    for t0, s, x, y in ((tw("Plantas", 26), "plantas que nenhum botânico reconhece", 1420, 990),
                        (tw("Mapas", 29), "mapas de estrelas", 880, 990),
                        (tw("pequenas", 31), "mulheres em piscinas verdes", 1420, 990)):
        nxt = {tw("Plantas", 26): tw("Mapas", 29), tw("Mapas", 29): tw("pequenas", 31), tw("pequenas", 31): 99}[t0]
        show(c, t, t0, x, y, lambda c, s=s: hl(c, s, 0, 0, 32), anim="up", t1=nxt - 0.1 if nxt < 99 else None)
    fog(c, t, 980, 0.05)
    HIST(c, t, [(0, "present"), (24.9, "point_r")], [(0, "neutral"), (31.7, "shocked")], x=200, s=0.85)


def s03(c, t):  # 37.9 - 54.1  quase 600 anos; passou de mão em mão; ninguém leu uma frase
    shelves(c, t, 0.35)
    show(c, t, 38.1, 1150, 150, lambda c: date_stamp(c, "QUASE 600 ANOS", 58, AMBER), anim="stamp")
    items = ((tw("alquimistas", 42), "alquimistas", lambda c: flask(c, (0.40, 0.70, 0.50), 150), 60),
             (tw("jesuítas", 43.5), "jesuítas", lambda c: cross_icon(c), 0),
             (tw("imperador", 45), "um imperador?", lambda c: crown_icon(c), 0),
             (tw("decifradores", 47), "decifradores de códigos", lambda c: (c.scale(0.42, 0.42), cipher_machine(c, t)), 0))
    for i, (t0, s, fn, dy) in enumerate(items):
        x = 690 + i * 330
        show(c, t, t0, x, 470 + dy, fn, anim="pop")
        show(c, t, t0 + 0.1, x, 620, T(s, 30), anim="fade")
        if i:
            if t > t0:
                arrow(c, x - 250, 470, x - 90, 470, PARCH2, 5, 0.0, 18)
    show(c, t, tw("Ninguém", 50), 1150, 820, lambda c: stitle(c, "NENHUMA FRASE LIDA", 0, 0, 70, RED, BLOOD), anim="stamp")
    fog(c, t, 960, 0.05)
    HIST(c, t, [(0, "stand"), (41.0, "present"), (50.8, "shrug")], [(0, "think"), (50.8, "worried")], x=250)


def s04(c, t):  # 54.1 - 59.9  título
    night(c, t, 760, moon_xy=(1650, 160))
    put(c, 1500, 560, lambda c: (c.rotate(-0.06), closed_codex(c, 1.05, True, t)), 1.0, fade_in(t, 54.2, 1.0))
    show(c, t, 54.3, 760, 360, T("esta é a história do", 44), anim="fade")
    show(c, t, tw("Manuscrito", 55), 760, 490, lambda c: stitle(c, "MANUSCRITO", 0, 0, 104, AMBER, AMBER), anim="up")
    show(c, t, tw("Voynich", 55.5), 760, 620, lambda c: stitle(c, "VOYNICH", 0, 0, 120, AMBER, None), anim="up")
    show(c, t, tw("livro", 56.8), 760, 760, T("o livro mais misterioso do mundo", 44, INK), anim="fade")
    fog(c, t, 960, 0.08)


def s05(c, t):  # 59.9 - 72.4  Beinecke, Yale, MS 408; pequeno; cabe numa bolsa
    night(c, t, 780, moon_xy=(1680, 140))
    small = tw("pequeno", 66)
    if t < small:
        ground(c, 900)
        put(c, 1150, 900, lambda c: beinecke(c, 1.0, t), 1.0, fade_in(t, 60.0, 0.8))
        show(c, t, tw("Biblioteca", 60.5), 1150, 120, lambda c: hl(c, "BIBLIOTECA BEINECKE — UNIVERSIDADE YALE", 0, 0, 40), anim="up")
        show(c, t, tw("número", 64), 1150, 260, lambda c: date_stamp(c, "MS 408", 60, AMBER), anim="stamp")
    else:
        put(c, 1050, 560, lambda c: (c.rotate(-0.04), closed_codex(c, 1.1, False, t)), 1.0)
        show(c, t, tw("vinte", 67), 790, 330, lambda c: ruler_cm(c, 460, 23, ""), anim="fade")
        show(c, t, tw("vinte", 67), 700, 560, T("23 cm", 36, AMBER), anim="fade")
        if t > tw("dezesseis", 69):
            p = ease_out(prog(t, tw("dezesseis", 69), 0.6))
            line(c, 885, 830, 885 + 340 * p, 830, 5, AMBER)
            show(c, t, tw("dezesseis", 69), 1055, 880, T("16 cm", 36, AMBER), anim="fade")
        show(c, t, tw("Cabe", 70.5), 1520, 880, sc(handbag, s=1.1), anim="pop")
        show(c, t, tw("pequeno", 66), 1150, 120, lambda c: stitle(c, "É PEQUENO", 0, 0, 60, INK), anim="up")
    fog(c, t, 960, 0.05)
    HIST(c, t, [(0, "point_r"), (66.6, "present")], [(0, "neutral"), (70.9, "happy")], x=260)


def composite_plant(c, t, t0):
    """raiz de uma planta + flor de outra, coladas"""
    p = ease_out(prog(t, t0, 1.2))
    c.save(); c.rectangle(-200, -110, 400, 400); c.clip(); c.translate(-160 * (1 - p), 0); vplant(c, 21, 1.0); c.restore()
    c.save(); c.rectangle(-200, -420, 400, 310); c.clip(); c.translate(160 * (1 - p), 0); vplant(c, 8, 1.0); c.restore()
    if p > 0.95:
        c.set_dash([10, 8]); line(c, -120, -110, 120, -110, 3, RED); c.set_dash([])


def s06(c, t):  # 72.4 - 98.6  seis partes; herbário; plantas não identificadas; montadas
    shelves(c, t, 0.3)
    herb = tw("parece", 77)
    if t < herb:
        kinds = ("herbal", "zodiac", "bath", "rosette", "pharma", "text")
        names = ("plantas", "astros", "banhos", "rosetas", "farmácia", "receitas")
        show(c, t, 72.6, 1150, 150, lambda c: stitle(c, "SEIS PARTES", 0, 0, 70, AMBER, AMBER), anim="up")
        for i, (k, nm) in enumerate(zip(kinds, names)):
            x = 620 + i * 215
            show(c, t, 74.0 + i * 0.25, x, 540, lambda c, k=k, i=i: manuscript_page(c, k, 520, 700, i + 1, t), s=0.36, anim="pop")
            show(c, t, 74.1 + i * 0.25, x, 720, T(nm, 28), anim="fade")
    else:
        put(c, 1000, 540, lambda c: manuscript_page(c, "herbal", 520, 700, 5, t), 1.12)
        show(c, t, herb, 1000, 90, lambda c: hl(c, "HERBÁRIO", 0, 0, 46), anim="up")
        show(c, t, tw("raiz", 83.5), 1000, 1010, T("raiz, folhas e flor... e texto em volta", 32), anim="fade", t1=87.3)
        show(c, t, tw("nenhuma", 88.5), 1460, 380, lambda c: big_q(c, 160), anim="pop", t1=tw("Algumas", 90.9) - 0.2)
        show(c, t, tw("identificada", 89.9), 1000, 1010, lambda c: caption_box(c, "quase nenhuma foi identificada", 38), anim="up",
             t1=tw("Algumas", 90.9) - 0.2)
        if t > tw("Algumas", 90.9):
            rrect(c, 1340, 160, 440, 820, 12); fs(c, VELLUM, 5, (0.50, 0.40, 0.26))
            c.save(); c.translate(1560, 740); c.scale(0.95, 0.95); composite_plant(c, t, tw("Algumas", 90.9)); c.restore()
            show(c, t, tw("colado", 95), 1560, 1020, T("a raiz de uma, a flor de outra", 30, AMBER), anim="fade")
    fog(c, t, 980, 0.04)
    HIST(c, t, [(0, "present"), (77.5, "point_r"), (91.2, "think")], [(0, "neutral"), (88.5, "think")], x=220, s=0.85)


def s07(c, t):  # 98.6 - 120.2  astronomia; zodíaco; nomes dos meses em letras comuns
    night(c, t, 1080, moon_xy=None)
    months = None
    if t > tw("nomes", 109):
        months = ["abril", "may"][: 1 + int(t > tw("nomes", 109) + 0.8)]
    put(c, 1150, 560, lambda c: zodiac_wheel(c, t, 330, 0.04, months), 1.0, fade_in(t, 98.8, 0.8))
    show(c, t, 98.9, 1150, 90, lambda c: hl(c, "ASTRONOMIA", 0, 0, 46), anim="up")
    show(c, t, tw("signos", 104), 1640, 300, T("os signos do zodíaco", 30, AMBER), anim="fade", t1=tw("nomes", 109) - 0.1)
    show(c, t, tw("francês", 112), 1660, 470, lambda c: hl(c, "francês?", 0, 0, 34), anim="pop")
    show(c, t, tw("catalão", 113), 1660, 560, lambda c: hl(c, "catalão?", 0, 0, 34), anim="pop")
    show(c, t, tw("Provavelmente", 114), 1150, 990, lambda c: caption_box(c, "provavelmente outra mão, mais tarde", 36), anim="up",
         t1=tw("É", 116.5) - 0.1)
    show(c, t, tw("É", 116.5), 1150, 990, lambda c: caption_box(c, "uma das poucas coisas legíveis no livro", 36), anim="up")
    fog(c, t, 980, 0.04)
    HIST(c, t, [(0, "point_r"), (106.2, "think"), (116.8, "present")], [(0, "neutral"), (106.2, "think")], x=240, s=0.85)


def s08(c, t):  # 120.2 - 136.1  a parte mais estranha: mulheres em piscinas ligadas por canos
    shelves(c, t, 0.25)
    rrect(c, 560, 230, 1180, 760, 12); fs(c, VELLUM, 5, (0.50, 0.40, 0.26))
    put(c, 1150, 700, lambda c: bath_pool(c, t, 1000, 6, 4), 1.0, fade_in(t, tw("Dezenas", 123), 0.8))
    if t > tw("Dezenas", 123):
        vpara(c, 640, 830, 1000, 3, 24, seed=44)
    show(c, t, 120.4, 1150, 110, lambda c: stitle(c, "A PARTE MAIS ESTRANHA", 0, 0, 62, AMBER, AMBER), anim="up")
    for i, (wd, s) in enumerate((("medicina", "medicina?"), ("religião", "religião?"), ("alquimia", "alquimia?"), ("outra", "outra coisa?"))):
        show(c, t, tw(wd, 131), 720 + i * 300, 300, lambda c, s=s: hl(c, s, 0, 0, 34), anim="pop")
    fog(c, t, 1000, 0.04)
    HIST(c, t, [(0, "stand"), (123.5, "point_r"), (131.0, "shrug")], [(0, "worried"), (123.5, "shocked"), (131.0, "think")], x=240, s=0.85)


def s09(c, t):  # 136.1 - 152.6  folha dobrável de nove círculos; castelo de ameias em rabo de andorinha
    night(c, t, 1080, moon_xy=None)
    zoom = tw("castelo", 145)
    p = ease_io(prog(t, tw("desdobra", 137.5), 1.6))
    a = 1.0 if t < zoom else 0.35 + 0.65 * fade_out(t, zoom, 1.0)
    put(c, 1150, 560, lambda c: rosette_foldout(c, t, p, 1100, 700), 1.0, a)
    show(c, t, 136.4, 1150, 110, lambda c: hl(c, "uma folha que se desdobra em seis partes", 0, 0, 40), anim="up", t1=zoom - 0.2)
    show(c, t, tw("nove", 140), 1150, 990, T("nove círculos ligados por caminhos", 36, AMBER), anim="fade", t1=zoom - 0.2)
    if t > zoom:
        put(c, 1250, 820, lambda c: swallow_castle(c, 1.3), 1.0, fade_in(t, zoom, 0.8))
        show(c, t, tw("rabo", 148), 1250, 140, lambda c: hl(c, "ameias em rabo de andorinha", 0, 0, 42), anim="up")
        show(c, t, tw("norte", 150.5), 1250, 960, lambda c: date_stamp(c, "NORTE DA ITÁLIA, SÉC. XV", 42, AMBER), anim="stamp")
    fog(c, t, 1000, 0.04)
    HIST(c, t, [(0, "present"), (145.0, "point_r")], [(0, "neutral"), (145.0, "think")], x=230, s=0.85)


def s10(c, t):  # 152.6 - 165.8  farmácia; páginas só de texto com estrelas
    shelves(c, t, 0.3)
    put(c, 850, 540, lambda c: manuscript_page(c, "pharma", 520, 700, 9, t), 1.0, fade_in(t, 152.8))
    show(c, t, 153.0, 850, 120, lambda c: hl(c, "potes e frascos de farmácia", 0, 0, 36), anim="up")
    if t > tw("fim", 158.5):
        put(c, 1480, 540, lambda c: manuscript_page(c, "text", 520, 700, 10, t), 1.0, fade_in(t, tw("fim", 158.5)))
        show(c, t, tw("fim", 158.5), 1480, 120, lambda c: hl(c, "páginas só de texto", 0, 0, 36), anim="up")
        if t > tw("estrela", 164):
            for k in range(4):
                glow(c, 1480 - 260 + 46 + 2, 540 - 350 + 70 - 8 + k * 150, 50, AMBER, 0.45 * fade_in(t, tw("estrela", 164) + k * 0.15, 0.4))
    fog(c, t, 1000, 0.04)
    HIST(c, t, [(0, "point_r"), (158.5, "present")], [(0, "neutral")], x=240, s=0.85)


def s11(c, t):  # 165.8 - 172.8  ~38 mil palavras; nenhuma lida
    glyph_rain(c, t, 0.22 * fade_in(t, 165.9, 1.2))
    counter_text(c, t, 166.3, 38000, 1100, 430, 180, AMBER, 2.4, prefix="~ ")
    show(c, t, 167.0, 1100, 590, T("palavras", 54), anim="fade")
    show(c, t, tw("nenhuma", 170), 1100, 790, lambda c: stitle(c, "NENHUMA FOI LIDA", 0, 0, 80, RED, BLOOD), anim="stamp")
    HIST(c, t, [(0, "present"), (170.0, "shrug")], [(0, "neutral"), (170.0, "worried")], x=260)


# ================================================================== BLOCO 2
def s12(c, t):  # 172.8 - 181.3  voltar a 1912; Itália, perto de Roma
    itaT = tw("Itália", 178)
    if t < itaT:
        night(c, t, 1080, moon_xy=None)
        put(c, 1150, 540, lambda c: hourglass(c, t, 4), 1.1, fade_in(t, 173.0))
        show(c, t, 173.2, 1150, 180, T("de onde esse livro veio?", 42), anim="fade")
        show(c, t, tw("mil", 175.5), 1150, 860, lambda c: date_stamp(c, "1912", 80, AMBER), anim="stamp")
        HIST(c, t, [(0, "think")], [(0, "think")], x=300)
    else:
        night(c, t, 820, moon_xy=(1650, 170))
        for k, (x, hh, col) in enumerate(((500, 260, (0.12, 0.13, 0.14)), (1300, 320, (0.10, 0.11, 0.12)), (1900, 240, (0.13, 0.14, 0.15)))):
            c.move_to(x - 800, 1080); c.curve_to(x - 300, 1080 - hh, x + 300, 1080 - hh, x + 800, 1080); c.close_path(); rgb(c, col); c.fill()
        put(c, 1250, 850, lambda c: villa(c, 0.4), 1.0, fade_in(t, itaT, 1.0))
        show(c, t, itaT, 1150, 180, lambda c: stitle(c, "ITÁLIA, PERTO DE ROMA", 0, 0, 64, AMBER, AMBER), anim="up")
        show(c, t, itaT + 0.5, 1150, 300, lambda c: date_stamp(c, "1912", 50, AMBER), anim="stamp")
        fog(c, t, 960, 0.08)
        HIST(c, t, [(0, "present")], [(0, "neutral")], x=300)


def s13(c, t):  # 181.3 - 199.6  Villa Mondragone; jesuítas vendem livros; Voynich compra ~30; um deles é este
    night(c, t, 820, moon_xy=(1700, 140))
    ground(c, 900, (0.14, 0.15, 0.13))
    books_t = tw("compra", 194)
    va = 1.0 if t < books_t else 0.08 + 0.92 * fade_out(t, books_t, 0.8)
    put(c, 1150, 900, lambda c: villa(c, 0.95), 1.0, va * fade_in(t, 181.4, 1.0))
    show(c, t, tw("Villa", 193.0 - 12), 1150, 110, lambda c: hl(c, "VILLA MONDRAGONE — FRASCATI", 0, 0, 40), anim="up", t1=books_t - 0.2)
    fig(c, t, 1640, 1000, 0.8, [(0, "stand"), (184.0, "point_l")], [(0, "neutral"), (194.6, "happy")], fid=12, appear=tw("Wilfrid", 182),
        alpha=va, **VOYNICH)
    show(c, t, tw("Wilfrid", 182), 1640, 520, lambda c: hl(c, "WILFRID VOYNICH", 0, 0, 34), anim="up", t1=books_t - 0.2)
    for i, x in enumerate((760, 900)):
        fig(c, t, x, 1000, 0.72, [(0, "hold")], [(0, "worried")], fid=20 + i, appear=tw("padres", 188) + i * 0.2, alpha=va, **PADRE)
    show(c, t, tw("dinheiro", 188.5), 830, 560, lambda c: caption_box(c, "vendendo em segredo", 32), anim="fade", t1=books_t - 0.2)
    if t > books_t:
        rnd = random.Random(2)
        for k in range(30):
            r, q = divmod(k, 10)
            x, y = 640 + q * 110, 300 + r * 170
            col = rnd.choice([(0.40, 0.26, 0.16), (0.30, 0.24, 0.18), (0.50, 0.36, 0.22), (0.26, 0.20, 0.24)])
            if k == 14:
                continue
            show(c, t, books_t + k * 0.04, x, y, lambda c, col=col: (c.scale(0.45, 0.45), book(c, "", col)), anim="pop")
        show(c, t, books_t + 0.3, 1150, 130, lambda c: stitle(c, "CERCA DE 30 MANUSCRITOS", 0, 0, 52, AMBER, AMBER), anim="up")
        one = tw("Um", 197)
        if t > one:
            k = ease_out(prog(t, one, 0.8))
            put(c, 640 + 4 * 110 + (1150 - 1080) * k, 470 + 170 * (1 - k) - 0 * k, lambda c: closed_codex(c, 0.35 + 0.35 * k, True, t), 1.0)
            show(c, t, one + 0.4, 1150, 950, lambda c: hl(c, "UM DELES É ESTE", 0, 0, 42), anim="up")
        else:
            put(c, 640 + 4 * 110, 470, lambda c: closed_codex(c, 0.35, False, t), 1.0)
    fog(c, t, 980, 0.06)
    HIST(c, t, [(0, "stand"), (194.6, "present")], [(0, "neutral"), (197.5, "shocked")], x=230, s=0.85)


def s14(c, t):  # 199.6 - 216.9  Voynich: Lituânia, Sibéria, fuga para Londres, livreiro
    draw_map(c, EUR, EUROPE, grid=10)
    show(c, t, 199.8, 960, 100, lambda c: caption_box(c, "não era um livreiro qualquer", 42), anim="up", t1=202.2)
    lt = tw("nascido", 202)
    if t > lt:
        map_point(c, EUR, *VILNIUS, AMBER, 10, t)
        show(c, t, lt, *EUR(VILNIUS[0], VILNIUS[1] + 2.0), T("LITUÂNIA", 34, AMBER), anim="pop")
    sib = tw("Sibéria", 205)
    pr = tw("preso", 205)
    if t > pr:
        p = ease_io(prog(t, pr, 2.4))
        x0, y0 = EUR(*VILNIUS); x1, y1 = EUR(44, 57.5)
        c.set_dash([16, 10]); line(c, x0, y0, x0 + (x1 - x0) * p, y0 + (y1 - y0) * p, 5, RED); c.set_dash([])
        show(c, t, pr, 1400, 620, lambda c: caption_box(c, "preso: revolução contra o czar", 32), anim="fade", t1=tw("Fugiu", 209))
    if t > sib - 0.3:
        show(c, t, sib, 1700, 470, lambda c: (arrow(c, -80, 0, 80, 0, RED, 8, 0.0, 30), text(c, "SIBÉRIA", 0, 50, 34, TYPE, RED)), anim="pop")
    fu = tw("Fugiu", 209)
    if t > fu:
        p = ease_io(prog(t, fu, 3.0))
        map_path(c, EUR, [(44, 57.5), (30, 58), (18, 56), (8, 54.5), LONDRES], p, AMBER, 6, dash=[14, 10])
        if t > tw("Londres", 210):
            map_point(c, EUR, *LONDRES, AMBER, 10, t)
            map_label(c, EUR, *LONDRES, "LONDRES", 34, AMBER, dy=-44)
    show(c, t, tw("maiores", 212), 960, 990, lambda c: hl(c, "um dos maiores negociantes de livros raros do mundo", 0, 0, 36), anim="up")


def s15(c, t):  # 216.9 - 235.4  a carta de 1665: Marci (Praga) para Kircher (Roma)
    shelves(c, t, 0.3)
    put(c, 1050, 540, lambda c: letter(c, 8, 400, 520), 1.0, fade_in(t, 217.1))
    show(c, t, 217.2, 1050, 110, lambda c: stitle(c, "HAVIA UMA CARTA", 0, 0, 60, AMBER, AMBER), anim="up")
    show(c, t, tw("latim", 220), 1050, 860, T("em latim", 34), anim="fade")
    show(c, t, tw("mil", 220.5), 1320, 300, lambda c: date_stamp(c, "1665", 56, RED), anim="stamp")
    show(c, t, tw("Johannes", 224), 700, 920, lambda c: hl(c, "JOHANNES MARCUS MARCI", 0, 0, 34), anim="up")
    show(c, t, tw("médico", 223), 700, 990, T("médico de Praga", 28), anim="fade")
    kt = tw("Athanasius", 229)
    fig(c, t, 1560, 1000, 0.8, [(0, "stand"), (kt + 1.4, "present")], [(0, "neutral"), (kt + 1.6, "confident")], fid=24, appear=tw("sábio", 227),
        **KIRCHER)
    show(c, t, kt, 1560, 440, lambda c: hl(c, "ATHANASIUS KIRCHER", 0, 0, 34), anim="up")
    show(c, t, tw("hieróglifos", 233), 1560, 520, T("\"decifrei os hieróglifos\"", 28, AMBER), anim="fade")
    if t > tw("Ele", 226):
        p = ease_io(prog(t, tw("Ele", 226), 1.5))
        arrow(c, 1250, 600, 1250 + 160 * p, 640, AMBER, 6, -0.2, 22)
    fog(c, t, 1000, 0.05)
    HIST(c, t, [(0, "point_r"), (226.6, "present")], [(0, "neutral")], x=240, s=0.85)


def s16(c, t):  # 235.4 - 259.2  Rodolfo II, alquimia, 600 ducados, Roger Bacon?
    night(c, t, 820, moon_xy=(1700, 140))
    put(c, 1250, 920, lambda c: prague_castle(c, 1.0), 1.0, 0.55)
    ground(c, 1000, (0.12, 0.12, 0.13))
    rt = tw("Rodolfo", 238)
    show(c, t, 235.6, 1150, 110, T("a carta contava uma história...", 42), anim="fade", t1=rt - 0.2)
    fig(c, t, 1100, 1000, 0.95, [(0, "stand"), (250.0, "present"), (254.0, "hips")], [(0, "confident"), (250.0, "happy")],
        fid=26, appear=rt, **RODOLFO)
    show(c, t, rt, 1150, 110, lambda c: hl(c, "RODOLFO II — IMPERADOR, EM PRAGA", 0, 0, 40), anim="up")
    obs = tw("obcecado", 245)
    duc = tw("seiscentos", 250)
    if obs < t < duc + 0.2:
        a = fade_out(t, duc - 0.3)
        for i, (wd, fn, s) in enumerate((("alquimia", lambda c: flask(c, (0.40, 0.70, 0.50), 130), "alquimia"),
                                         ("astrologia", lambda c: zodiac_wheel(c, t, 80), "astrologia"),
                                         ("objetos", lambda c: (c.scale(0.6, 0.6), hourglass(c, t)), "objetos raros"))):
            tt = tw(wd, 245)
            if t > tt:
                put(c, 760 + i * 260, 360, fn, 1.0, a * fade_in(t, tt, 0.4))
                put(c, 760 + i * 260, 480, T(s, 28), 1.0, a * fade_in(t, tt, 0.4))
    if t > duc:
        show(c, t, duc, 740, 960, lambda c: (c.scale(1.4, 1.4), coins_pile(c, 9)), anim="drop")
        show(c, t, duc + 0.6, 760, 640, lambda c: date_stamp(c, "600 DUCADOS", 54, AMBER), anim="stamp")
    bt = tw("Roger", 255)
    if t > bt - 0.3:
        fig(c, t, 1700, 1000, 0.75, [(0, "hold")], [(0, "neutral")], fid=27, appear=bt - 0.2, **BACON)
        show(c, t, bt, 1700, 560, lambda c: hl(c, "ROGER BACON?", 0, 0, 34), anim="up")
        show(c, t, tw("frade", 256), 1700, 630, T("frade inglês, séc. XIII", 26), anim="fade")
    fog(c, t, 1000, 0.06)
    HIST(c, t, [(0, "stand"), (238.5, "point_r")], [(0, "neutral"), (250.0, "shocked")], x=240, s=0.85)


def coins_pile(c, n=7):
    for k in range(n):
        ellipse(c, (k % 3 - 1) * 34, -k * 9, 30, 10); fs(c, GOLD, 3)


def s17(c, t):  # 259.2 - 275.6  John Dee e Edward Kelley; Kelley fabricou o livro?
    night(c, t, 900, moon_xy=(1650, 150))
    ground(c, 1000, (0.12, 0.12, 0.13))
    fig(c, t, 980, 1000, 0.85, [(0, "stand"), (262.0, "think")], [(0, "neutral")], fid=28, appear=tw("John", 262) - 0.4, **DEE)
    show(c, t, tw("John", 262), 980, 520, lambda c: hl(c, "JOHN DEE", 0, 0, 34), anim="up")
    show(c, t, tw("matemático", 263), 980, 590, T("matemático e astrólogo", 26), anim="fade")
    kt = tw("Edward", 265)
    fig(c, t, 1380, 1000, 0.85, [(0, "stand"), (kt + 2.0, "arms_up"), (270.0, "hold")], [(0, "neutral"), (kt + 2.0, "grin")],
        fid=29, appear=kt - 0.4, **KELLEY)
    show(c, t, kt, 1380, 520, lambda c: hl(c, "EDWARD KELLEY", 0, 0, 34), anim="up")
    an = tw("anjos", 266)
    if an - 0.5 < t < 270.0:
        for k in range(6):
            a = k * math.pi / 3 + t * 0.6
            x, y = 1380 + math.cos(a) * 220, 380 + math.sin(a) * 70
            c.save(); c.translate(x, y); c.scale(1.2, 1.2); sparkle(c); c.restore()
        glow(c, 1380, 380, 260, LYELLOW, 0.16)
        show(c, t, an, 1380, 260, T("\"conversava com anjos\"", 30, AMBER), anim="fade")
    if t > 269.3:
        put(c, 1500, 780, lambda c: (c.rotate(-0.1), closed_codex(c, 0.42, True, t)), 1.0, fade_in(t, 269.4))
        show(c, t, tw("fabricado", 270), 1150, 130, lambda c: hl(c, "FABRICOU O LIVRO PARA O IMPERADOR?", 0, 0, 40), anim="up")
        show(c, t, tw("vender", 270), 1700, 640, lambda c: big_q(c, 120), anim="pop")
    fog(c, t, 1000, 0.06)
    HIST(c, t, [(0, "present"), (269.3, "think")], [(0, "neutral"), (269.3, "think")], x=240, s=0.85)


def s18(c, t):  # 275.6 - 297.5  lenda? Stefan Guzy: 1599, 600 florins, Carl Widemann; o valor bate
    shelves(c, t, 0.35)
    show(c, t, 275.8, 1150, 110, lambda c: stitle(c, "SÓ UMA LENDA?", 0, 0, 64, INK, AMBER), anim="up", t1=279.2)
    gt = tw("Stefan", 280)
    fig(c, t, 1650, 1000, 0.85, [(0, "stand"), (gt + 2.0, "point_l")], [(0, "neutral"), (gt + 2.0, "confident")], fid=31, appear=gt - 0.4,
        **GUZY)
    show(c, t, gt, 1650, 500, lambda c: hl(c, "STEFAN GUZY", 0, 0, 34), anim="up")
    show(c, t, gt + 0.6, 1650, 570, T("pesquisador alemão", 26), anim="fade")
    rt = tw("registros", 282)
    put(c, 1050, 500, lambda c: (c.rotate(0.03), letter(c, 7, 420, 470, False)), 1.0, fade_in(t, rt, 0.6))
    show(c, t, rt, 1050, 110, lambda c: hl(c, "REGISTROS DA CORTE DE RODOLFO", 0, 0, 38), anim="up")
    show(c, t, tw("mil", 284), 1250, 330, lambda c: date_stamp(c, "1599", 56, RED), anim="stamp")
    show(c, t, tw("florins", 288), 1050, 560, lambda c: caption_box(c, "600 FLORINS", 52), anim="pop")
    show(c, t, tw("Carl", 290), 1050, 785, T("livros do médico Carl Widemann", 32, AMBER), anim="fade")
    nt = tw("papéis", 293)
    if t > nt:
        show(c, t, nt, 1050, 850, lambda c: caption_box(c, "o nome do livro? não aparece", 34), anim="up", t1=tw("valor", 295.5) - 0.1)
    vt = tw("valor", 295.5)
    if t > vt:
        show(c, t, vt, 1050, 860, lambda c: (text(c, "600", -200, 0, 64, SERIF, AMBER), eq(c, 40, AMBER, 10), text(c, "600", 200, 0, 64, SERIF, AMBER)),
             anim="pop")
        show(c, t, vt + 0.2, 1050, 960, T("ducados na carta / florins nos registros", 26), anim="fade")
    fog(c, t, 1000, 0.05)
    HIST(c, t, [(0, "think"), (288.0, "point_r"), (295.8, "present")], [(0, "think"), (295.8, "happy")], x=240, s=0.85)


def s19(c, t):  # 297.5 - 314.0  primeira página: nome apagado; luz ultravioleta: Jacobus de Tepenec
    c.rectangle(0, 0, W, H); rgb(c, (0.04, 0.035, 0.05)); c.fill()
    ut = tw("ultravioleta", 303)
    rv = tw("Jacobus", 305)
    put(c, 1100, 540, lambda c: manuscript_page(c, "first", 520, 700, 1, t), 1.05)
    show(c, t, 297.8, 1100, 70, T("outra pista: a primeira página", 36), anim="fade", t1=ut - 0.2)
    at_ = tw("apagou", 300)
    if at_ < t < ut + 0.5:
        glow(c, 1100, 830, 260, AMBER, 0.25 * fade_in(t, at_, 0.6))
        show(c, t, at_, 1100, 1000, T("alguém apagou um nome", 32, AMBER), anim="fade", t1=ut)
    if t > ut:
        k = fade_in(t, ut, 1.0)
        c.rectangle(0, 0, W, H); rgb(c, UVC, 0.12 * k); c.fill()
        ang = 0.55 - 0.25 * ease_io(prog(t, ut, 2.0))
        put(c, 1560, 300, lambda c: uv_lamp(c, t, True, True, ang), 1.0, k)
        glow(c, 1100, 830, 300, UVC, 0.28 * k)
        show(c, t, ut, 1100, 70, lambda c: hl(c, "LUZ ULTRAVIOLETA", 0, 0, 38, bg=(0.30, 0.20, 0.46), col=INK), anim="up")
    if t > rv:
        a = fade_in(t, rv, 1.0)
        put(c, 1100, 828, lambda c: (c.rotate(-0.02), text(c, "Jacobj à Tepenece", 0, 0, 42, HAND, (0.92, 0.86, 1.0))), 1.05, a)
        show(c, t, tw("químico", 308), 1100, 1000, lambda c: caption_box(c, "Jacobus de Tepenec — químico do imperador Rodolfo", 32), anim="up")
    fog(c, t, 1040, 0.03)
    HIST(c, t, [(0, "point_r"), (303.4, "present"), (305.6, "point_r")], [(0, "think"), (305.6, "shocked")], x=260, s=0.85)


def s20(c, t):  # 314.0 - 336.2  Georg Baresch em Praga; 1639 carta a Kircher; medicina; cópias; sem solução
    draw_map(c, CEN, EUROPE, grid=2)
    map_point(c, CEN, *PRAGA, AMBER, 10, t)
    map_label(c, CEN, *PRAGA, "PRAGA", 34, AMBER, dy=-44)
    show(c, t, tw("Georg", 318), 960, 100, lambda c: hl(c, "GEORG BARESCH, ALQUIMISTA DE PRAGA", 0, 0, 38), anim="up", t1=tw("Diz", 325) - 0.2)
    x, y = CEN(*PRAGA)
    fig(c, t, x + 150, y + 260, 0.6, [(0, "hold")], [(0, "think")], fid=33, appear=tw("alquimista", 316), **BARESCH)
    lt = tw("mil", 320.5)
    show(c, t, lt, x + 360, y - 60, lambda c: date_stamp(c, "1639", 46, RED), anim="stamp")
    kt = tw("Kircher", 322)
    if t > kt:
        p = ease_io(prog(t, kt, 2.2))
        map_path(c, CEN, [PRAGA, (13.0, 48.0), (11.5, 45.5), (11.8, 43.5), ROMA], p, AMBER, 5, dash=[12, 10])
        xx, yy = CEN(PRAGA[0] + (ROMA[0] - PRAGA[0]) * p, PRAGA[1] + (ROMA[1] - PRAGA[1]) * p)
        if p < 1:
            put(c, xx, yy, lambda c: (c.scale(0.4, 0.4), envelope(c)), 1.0)
        map_point(c, CEN, *ROMA, AMBER, 10, t)
        map_label(c, CEN, *ROMA, "ROMA — KIRCHER", 32, AMBER, dy=50)
    show(c, t, tw("Diz", 325), 960, 100, lambda c: caption_box(c, "\"o livro inteiro deve ser sobre medicina\"", 40), anim="up", t1=333.0)
    show(c, t, tw("cópias", 331), 1500, 350, lambda c: (c.scale(0.5, 0.5), scroll(c, 4)), anim="pop")
    show(c, t, tw("cópias", 331) + 0.2, 1500, 450, T("cópias de páginas", 28), anim="fade")
    st = tw("solução", 333)
    if t > tw("nunca", 333):
        show(c, t, tw("nunca", 333), 960, 100, lambda c: caption_box(c, "Kircher nunca respondeu com uma solução", 40), anim="up")
        x2, y2 = CEN(*ROMA)
        x_over(c, t, st, x2, y2 - 90, 50)


def s21(c, t):  # 336.2 - 351.5  Marci, velho e quase cego, manda para Roma; 200 anos numa biblioteca jesuíta
    lib = tw("desaparece", 344)
    if t < lib:
        night(c, t, 1080, moon_xy=None)
        shelves(c, t, 0.25)
        fig(c, t, 900, 1000, 0.9, [(0, "hold"), (339.6, "present")], [(0, "sad")], fid=34, appear=336.4, glasses=True, **MARCI)
        show(c, t, tw("Marci", 338), 900, 480, lambda c: hl(c, "MARCI", 0, 0, 38), anim="up")
        show(c, t, tw("velho", 340), 900, 550, T("já velho e quase cego", 28), anim="fade")
        rt = tw("Roma", 342)
        p = ease_io(prog(t, tw("manda", 341), 1.6))
        put(c, 1050 + 500 * p, 720 - 200 * math.sin(p * math.pi), lambda c: (c.rotate(-0.2 + p * 0.3), closed_codex(c, 0.35, True, t)), 1.0)
        show(c, t, rt, 1600, 400, lambda c: date_stamp(c, "ROMA", 54, AMBER), anim="stamp")
    else:
        shelves(c, t, 1.0)
        glow(c, 1100, 520, 140, AMBER, 0.35)
        put(c, 1100, 540, lambda c: (c.scale(0.3, 0.3), closed_codex(c, 1.0)), 1.0)
        counter_text(c, t, lib + 0.2, 200, 1100, 160, 110, AMBER, 1.6, prefix="+ ", suffix=" ANOS", sep=False)
        show(c, t, tw("biblioteca", 345), 1100, 900, lambda c: caption_box(c, "esquecido numa biblioteca jesuíta", 40), anim="up")
        show(c, t, tw("vendido", 348), 1100, 990, T("... até ser vendido a Voynich, em 1912", 32, AMBER), anim="fade")
    fog(c, t, 1000, 0.05)
    HIST(c, t, [(0, "stand"), (344.2, "present")], [(0, "neutral"), (344.2, "think")], x=240, s=0.85)


# ================================================================== BLOCO 3
def s22(c, t):  # 351.5 - 361.4  Voynich passou a vida tentando; cópias para especialistas
    shelves(c, t, 0.35)
    put(c, 900, 760, lambda c: (c.rotate(-0.04), closed_codex(c, 0.45, True, t)), 1.0)
    fig(c, t, 760, 1000, 0.9, [(0, "think"), (355.8, "point_r")], [(0, "think"), (355.8, "confident")], fid=12, appear=351.6, **VOYNICH)
    show(c, t, 351.8, 1150, 110, lambda c: caption_box(c, "Voynich passou a vida tentando ler o livro", 40), anim="up")
    ct = tw("Mandou", 355)
    for i, (wd, s) in enumerate((("professores", "professores"), ("cientistas", "cientistas"), ("especialistas", "especialistas em códigos"))):
        tt = tw(wd, ct)
        if t > ct + i * 0.4:
            p = ease_out(prog(t, ct + i * 0.4, 1.2))
            x, y = 1000 + 600 * p, 640 - 220 * math.sin(p * math.pi * 0.9) + i * 130 - 60
            put(c, x, y, lambda c: (c.scale(0.5, 0.5), envelope(c)), 1.0)
        show(c, t, tt, 1600, 420 + i * 130, lambda c, s=s: hl(c, s, 0, 0, 30), anim="pop")
    fog(c, t, 1000, 0.05)
    HIST(c, t, [(0, "stand")], [(0, "neutral")], x=240, s=0.8)


def s23(c, t):  # 361.4 - 384.3  1921: William Newbold; traços minúsculos; grego; Bacon e o microscópio
    shelves(c, t, 0.3)
    show(c, t, tw("mil", 361.5), 1150, 110, lambda c: date_stamp(c, "1921", 56, AMBER), anim="stamp")
    nt = tw("William", 365)
    fig(c, t, 1650, 1000, 0.85, [(0, "stand"), (nt + 2.5, "arms_up"), (369.5, "point_l")], [(0, "neutral"), (nt + 2.5, "grin")],
        fid=35, appear=nt - 0.4, **NEWBOLD)
    show(c, t, nt, 1650, 500, lambda c: hl(c, "WILLIAM NEWBOLD", 0, 0, 34), anim="up")
    show(c, t, nt + 0.4, 1650, 570, T("Univ. da Pensilvânia", 26), anim="fade")
    show(c, t, tw("resolvido", 367), 1150, 230, lambda c: hl(c, "\"RESOLVI O ENIGMA\"", 0, 0, 40), anim="pop", t1=369.4)
    zt = tw("traços", 370)
    if t > tw("Segundo", 369):
        put(c, 1050, 560, lambda c: glyph_zoom(c, t, "qokedy", 120, ticks=fade_in(t, zt, 1.5)), 1.0,
            fade_in(t, 369.7) * fade_out(t, tw("Roger", 378), 0.6))
        show(c, t, zt + 0.4, 1050, 230, T("traços minúsculos, quase invisíveis", 34, AMBER), anim="fade", t1=377.7)
        show(c, t, tw("grega", 375), 1050, 820, lambda c: caption_box(c, "\"uma escrita grega abreviada\"", 36), anim="up", t1=377.7)
    mt = tw("microscópio", 380)
    if t > tw("Roger", 378):
        put(c, 1050, 860, lambda c: microscope(c), 1.4, fade_in(t, tw("Roger", 378) + 0.3, 0.6))
        show(c, t, tw("Roger", 378), 1050, 230, lambda c: hl(c, "ROGER BACON INVENTOU O MICROSCÓPIO?", 0, 0, 38), anim="up")
        show(c, t, mt, 1050, 960, T("séculos antes de todo mundo", 32), anim="fade")
    fog(c, t, 1000, 0.05)
    HIST(c, t, [(0, "point_r"), (378.0, "think")], [(0, "neutral"), (378.0, "think")], x=240, s=0.85)


def s24(c, t):  # 384.3 - 406.2  notícia; 1931 John Manly: rachaduras da tinta; Newbold morreu convencido
    shelves(c, t, 0.3)
    mt = tw("Mas", 386.5)
    na = 1.0 if t < mt else 0.35
    put(c, 760, 380, lambda c: newspaper(c, "DECIFRADO!", "o manuscrito de Roger Bacon"), 1.1, na * fade_in(t, 384.5, 0.5))
    if t > tw("rachaduras", 391):
        x_over(c, t, tw("rachaduras", 391) + 0.5, 760, 380, 110)
    show(c, t, 384.6, 1300, 110, T("a notícia correu o mundo", 40), anim="fade", t1=mt - 0.2)
    if t > mt:
        show(c, t, tw("mil", mt), 1250, 110, lambda c: date_stamp(c, "1931", 54, RED), anim="stamp")
        jt = tw("John", 389)
        fig(c, t, 1680, 1000, 0.85, [(0, "stand"), (jt + 1.0, "point_l")], [(0, "neutral"), (jt + 1.0, "confident")], fid=36, appear=jt - 0.4,
            **MANLY)
        show(c, t, jt, 1680, 500, lambda c: hl(c, "JOHN MANLY", 0, 0, 34), anim="up")
        rt = tw("rachaduras", 391)
        put(c, 1150, 620, lambda c: glyph_zoom(c, t, "daiin", 110, ticks=1.0, cracks=fade_in(t, rt, 1.0)), 1.0, fade_in(t, tw("mostrou", 389)))
        show(c, t, rt, 1150, 860, lambda c: caption_box(c, "só rachaduras da tinta seca", 36), anim="up", t1=397.4)
    show(c, t, tw("Newbold", 397), 1150, 860, lambda c: caption_box(c, "Newbold leu o que queria ler", 36), anim="up", t1=400.2)
    if t > tw("Ele", 400):
        put(c, 760, 900, lambda c: candle(c, t), 0.9, 1.0)
        show(c, t, tw("Ele", 400), 1150, 860, lambda c: caption_box(c, "morreu em 1926, ainda convencido", 36), anim="up")
    fog(c, t, 1000, 0.05)
    HIST(c, t, [(0, "present"), (397.6, "shrug")], [(0, "neutral"), (386.8, "think"), (397.6, "sad")], x=240, s=0.85)


def s25(c, t):  # 406.2 - 434.3  Voynich morre 1930; Ethel; Kraus; 24.500 / 160.000; ninguém quis; 1969 Yale
    shelves(c, t, 0.3)
    show(c, t, 406.4, 1150, 110, lambda c: date_stamp(c, "1930", 52, GRAY), anim="stamp", t1=409.7)
    put(c, 1150, 560, lambda c: (c.rotate(-0.04), closed_codex(c, 0.5, True, t)), 1.0, fade_in(t, 406.4))
    et = tw("Ethel", 409)
    kt = tw("Hans", 416)
    if et - 0.3 < t < kt + 0.5:
        a = fade_out(t, kt - 0.2, 0.6)
        fig(c, t, 760, 1000, 0.85, [(0, "hold")], [(0, "sad"), (412.0, "neutral")], fid=37, appear=et - 0.3, alpha=a, **ETHEL)
        show(c, t, et, 760, 480, lambda c: hl(c, "ETHEL VOYNICH", 0, 0, 34), anim="up", t1=kt - 0.2)
        show(c, t, tw("romance", 411), 1150, 900, lambda c: caption_box(c, "romance com milhões de exemplares na URSS", 34), anim="up",
             t1=kt - 0.2)
    if t > kt - 0.4:
        fig(c, t, 1640, 1000, 0.85, [(0, "stand"), (422.4, "present"), (428.0, "shrug")], [(0, "happy"), (427.8, "sad")], fid=38,
            appear=kt - 0.3, **KRAUS)
        show(c, t, kt, 1640, 480, lambda c: hl(c, "HANS KRAUS", 0, 0, 34), anim="up")
        show(c, t, kt + 0.5, 1640, 550, T("livros raros, Nova York", 26), anim="fade")
    pt = tw("pagou", 422)
    show(c, t, pt, 1150, 300, lambda c: price_tag(c, "US$ 24.500", GOLD_D, 42), anim="pop", t1=tw("Tentou", 425) - 0.1)
    show(c, t, tw("Tentou", 425), 1150, 300, lambda c: price_tag(c, "US$ 160.000", RED, 42), anim="pop")
    ng = tw("Ninguém", 427.5)
    show(c, t, ng, 1150, 900, lambda c: hl(c, "NINGUÉM QUIS", 0, 0, 40), anim="stamp", t1=tw("mil", 429) - 0.1)
    yt = tw("doou", 430)
    if t > tw("mil", 429):
        show(c, t, tw("mil", 429), 1150, 900, lambda c: caption_box(c, "1969: doado para Yale", 40), anim="up")
    fog(c, t, 1000, 0.05)
    HIST(c, t, [(0, "stand"), (yt, "present")], [(0, "sad"), (416.0, "neutral")], x=240, s=0.8)


def s26(c, t):  # 434.3 - 443.7  um homem muito mais perigoso para qualquer segredo: William Friedman
    c.rectangle(0, 0, W, H); rgb(c, (0.03, 0.03, 0.04)); c.fill()
    ft = tw("William", 441)
    show(c, t, 434.5, 1150, 200, T("antes disso, o livro chamou a atenção de um homem...", 38), anim="fade", t1=ft - 0.3)
    show(c, t, tw("perigoso", 437), 1150, 270, T("muito mais perigoso para qualquer segredo", 38, AMBER), anim="fade", t1=ft - 0.3)
    k = fade_in(t, ft - 0.6, 0.8)
    glow(c, 1150, 760, 420 * max(0.05, k), LYELLOW, 0.22)
    put(c, 1150, 560, lambda c: (c.rotate(-0.05), closed_codex(c, 0.7, True, t)), 1.0, fade_in(t, 434.5, 1.0) * fade_out(t, ft - 0.8, 0.6))
    if t > ft - 0.6:
        fig(c, t, 1150, 1000, 1.0, [(0, "stand"), (ft + 0.6, "hips")], [(0, "confident")], fid=39, alpha=k, **FRIEDMAN)
    show(c, t, ft, 1150, 200, lambda c: stitle(c, "WILLIAM FRIEDMAN", 0, 0, 84, AMBER, AMBER), anim="up")
    HIST(c, t, [(0, "think")], [(0, "worried")], x=300)


def s27(c, t):  # 443.7 - 461.2  maior decifrador dos EUA; cifra diplomática do Japão; grupos de estudo
    night(c, t, 1080, moon_xy=None)
    fig(c, t, 1640, 1000, 0.9, [(0, "stand"), (448.8, "point_l"), (456.3, "present")], [(0, "confident")], fid=39, **FRIEDMAN)
    show(c, t, 443.9, 1150, 110, lambda c: hl(c, "O MAIOR DECIFRADOR DE CÓDIGOS DOS EUA", 0, 0, 40), anim="up", t1=456.0)
    gt = tw("No", 456)
    if t < gt:
        put(c, 1050, 560, lambda c: cipher_machine(c, t, "CIFRA DIPLOMÁTICA DO JAPÃO"), 1.0, fade_in(t, tw("chefiava", 448)))
        show(c, t, tw("quebrou", 450), 1050, 560, lambda c: date_stamp(c, "QUEBRADA", 70, RED), anim="stamp")
        show(c, t, tw("Segunda", 453), 1050, 850, T("pouco antes da Segunda Guerra", 34), anim="fade")
    else:
        show(c, t, gt, 1150, 110, lambda c: hl(c, "GRUPOS SÓ PARA O VOYNICH", 0, 0, 40), anim="up")
        put(c, 1050, 820, lambda c: (c.rectangle(-330, -20, 660, 30), fs(c, (0.36, 0.24, 0.14), 5)), 1.0)
        put(c, 1050, 770, lambda c: manuscript_spread(c, "text", "zodiac", t, 1.0, 0.28, seed=4), 1.0)
        show(c, t, gt + 0.4, 1050, 330, lambda c: date_stamp(c, "1944", 56, AMBER), anim="stamp")
        for i, x in enumerate((640, 790, 1310, 1460)):
            fig(c, t, x, 1000, 0.6, [(0, "think" if i % 2 else "point_r")], [(0, "think")], fid=50 + i, appear=gt + i * 0.25,
                **(SABIO if i % 2 else dict(SABIO, shirt=(0.70, 0.70, 0.66), coat=(0.30, 0.28, 0.24))))
    fog(c, t, 1000, 0.05)
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=240, s=0.8)


def s28(c, t):  # 461.2 - 473.1  cartões, contagem, máquinas de calcular; o resultado foi estranho
    night(c, t, 1080, moon_xy=None)
    put(c, 1250, 920, lambda c: tabulator(c, t, 520, 360), 1.0, fade_in(t, tw("máquinas", 467) - 0.4))
    for k in range(7):
        t0 = 461.5 + k * 0.5
        if t > t0:
            p = ease_out(prog(t, t0, 1.4))
            put(c, 700 + 300 * p + k * 30, 300 + 140 * p - k * 8, lambda c, k=k: (c.rotate(-0.15 + k * 0.05), punch_card(c, k)), 0.75)
    for i, (wd, s) in enumerate((("letra", "cada letra"), ("palavra", "cada palavra"), ("repetição", "cada repetição"))):
        show(c, t, tw(wd, 462), 1600, 260 + i * 80, T(s, 34, AMBER), anim="fade", t1=470.6)
    show(c, t, tw("estranho", 470), 1150, 130, lambda c: stitle(c, "O RESULTADO FOI ESTRANHO", 0, 0, 62, AMBER, AMBER), anim="up")
    fog(c, t, 1000, 0.05)
    HIST(c, t, [(0, "point_r"), (470.8, "think")], [(0, "neutral"), (470.8, "shocked")], x=240, s=0.85)


def s29(c, t):  # 473.1 - 491.2  não é cifra comum: padrões; começo/fim de palavra; frequência como língua humana
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.055, 0.07)); c.fill()
    line(c, 1150, 230, 1150, 900, 3, LGRAY)
    show(c, t, 473.3, 830, 160, lambda c: hl(c, "CIFRA COMUM", 0, 0, 40), anim="up")
    rnd = random.Random(int(t * 4))
    if t > tw("embaralha", 476):
        for r in range(6):
            s = "".join(rnd.choice("XQZKJWVBHPMRT") for _ in range(12))
            text(c, " ".join(s[i:i + 4] for i in range(0, 12, 4)), 830, 330 + r * 80, 40, TYPE, GRAY)
        show(c, t, tw("aleatório", 478), 830, 860, T("parece aleatório", 34), anim="fade")
    vt = tw("Voynich", 480)
    show(c, t, vt, 1500, 160, lambda c: hl(c, "VOYNICH", 0, 0, 40), anim="up")
    if t > vt:
        words = ["qokedy", "daiin", "chedy", "qokain", "shedy", "otedy"]
        st, en = tw("começo", 482), tw("fim", 485.3)
        for r, wd in enumerate(words):
            y = 340 + r * 80
            x0 = 1320
            c.save(); c.translate(x0, y + 14); vword(c, wd, 46, INK); c.restore()
            if t > st:
                glow(c, x0 + 12, y, 40, AMBER, 0.5 * fade_in(t, st, 0.5))
            if t > en:
                ww = vword_w(wd, 46)
                glow(c, x0 + ww - 14, y, 40, ICE, 0.5 * fade_in(t, en, 0.5))
        show(c, t, tw("padrões", 480), 1500, 860, T("tem padrões", 34, AMBER), anim="fade", t1=st - 0.1)
        show(c, t, st, 1500, 860, T("letras só no começo...", 32, AMBER), anim="fade", t1=en - 0.1)
        show(c, t, en, 1500, 860, T("...e letras só no fim", 32, ICE), anim="fade", t1=tw("palavras", 486.5) - 0.1)
    zt = tw("palavras", 486.5)
    if t > zt:
        a = fade_in(t, zt, 0.5)
        c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.055, 0.07), a * 0.92); c.fill()
        for k in range(10):
            hh = 520 / (k + 1)
            p = ease_out(prog(t, zt + 0.2 + k * 0.08, 0.6))
            put(c, 760 + k * 80, 880, lambda c, hh=hh, p=p: (c.rectangle(-28, -hh * p, 56, hh * p), fs(c, AMBER if k == 0 else PARCH2, 3)), 1.0, a)
        put(c, 1150, 170, lambda c: caption_box(c, "as palavras se repetem como numa língua humana", 38), 1.0, a)
    fog(c, t, 1040, 0.03)


def s30(c, t):  # 491.2 - 502.8  coisas que nenhuma língua faz: palavra 2-3x seguidas; sem palavras curtas
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.055, 0.07)); c.fill()
    show(c, t, 491.4, 1150, 130, lambda c: stitle(c, "MAS...", 0, 0, 64, RED, BLOOD), anim="up", t1=494.6)
    show(c, t, 492.0, 1150, 220, T("coisas que nenhuma língua faz", 40), anim="fade", t1=494.6)
    rt = tw("mesma", 494.5)
    if t > rt:
        show(c, t, rt, 1150, 130, lambda c: hl(c, "A MESMA PALAVRA, 3 VEZES SEGUIDAS", 0, 0, 40), anim="up", t1=498.3)
        for k in range(3):
            show(c, t, rt + 0.5 + k * 0.5, 720 + k * 330, 470, lambda c: (c.translate(-150, 20), vword(c, "qokedy", 60, INK)), anim="pop")
    stt = tw("quase", 498.3)
    if t > stt:
        show(c, t, stt, 1150, 130, lambda c: hl(c, "QUASE NÃO HÁ PALAVRAS CURTAS", 0, 0, 40), anim="up")
        for k, wd in enumerate(("o", "a", "or", "y")):
            x = 760 + k * 220
            show(c, t, stt + 0.6 + k * 0.2, x, 760, lambda c, wd=wd: (c.translate(-20, 20), vword(c, wd, 60, GRAY)), anim="fade")
            x_over(c, t, stt + 1.2 + k * 0.2, x, 745, 45)
    fog(c, t, 1040, 0.03)
    HIST(c, t, [(0, "think"), (494.9, "point_r")], [(0, "think")], x=240, s=0.8)


def s31(c, t):  # 502.8 - 523.9  Friedman esconde a conclusão num anagrama: língua artificial
    night(c, t, 1080, moon_xy=None)
    fig(c, t, 1680, 1000, 0.85, [(0, "think"), (510.6, "present")], [(0, "think"), (510.6, "confident")], fid=39, **FRIEDMAN)
    show(c, t, 503.0, 1100, 110, lambda c: caption_box(c, "décadas de estudo", 40), anim="up", t1=505.4)
    show(c, t, tw("guardou", 505.5), 1100, 110, lambda c: caption_box(c, "uma conclusão escondida", 40), anim="up", t1=tw("Quando", 515.5) - 0.2)
    at_ = tw("anagrama", 510)
    rv = tw("revelada", 516)
    if at_ < t < rv + 0.6:
        a = fade_out(t, rv, 0.6)
        rnd = random.Random(1)
        letters = list("THEVOYNICHMSSWASANEARLYATTEMPTTOCONSTRUCTANARTIFICIALLANGUAGE")
        rnd.shuffle(letters)
        for i, ch in enumerate(letters[:48]):
            r, k = divmod(i, 12)
            jit = math.sin(t * 3 + i) * 6
            x, y = 640 + k * 80, 330 + r * 100 + jit
            put(c, x, y, lambda c, ch=ch: (rrect(c, -30, -36, 60, 72, 8), fs(c, PARCH, 3, DARKTXT), text(c, ch, 0, 0, 44, TYPE, DARKTXT)), 1.0,
                a * fade_in(t, at_ + i * 0.03, 0.3))
        show(c, t, tw("embaralhadas", 511), 1100, 790, T("as letras embaralhadas, num artigo", 34, AMBER), anim="fade", t1=rv)
    if t > rv:
        show(c, t, rv + 0.3, 1100, 330, T("o manuscrito seria uma tentativa antiga de criar", 38), anim="fade")
        show(c, t, tw("língua", 518), 1100, 470, lambda c: stitle(c, "UMA LÍNGUA ARTIFICIAL", 0, 0, 80, AMBER, AMBER), anim="up")
        show(c, t, tw("inventada", 520), 1100, 600, T("inventada do zero", 40, INK), anim="fade")
        show(c, t, tw("inventada", 520) + 0.4, 1100, 760, lambda c: gear_icon(c, t), anim="pop")
    fog(c, t, 1000, 0.05)
    HIST(c, t, [(0, "stand"), (518.5, "point_r")], [(0, "neutral"), (518.5, "shocked")], x=240, s=0.8)


def s32(c, t):  # 523.9 - 537.5  Friedman morre em 1969, o ano em que o livro chegou a Yale
    c.rectangle(0, 0, W, H); rgb(c, (0.04, 0.035, 0.04)); c.fill()
    lt = fade_out(t, tw("Yale", 527), 2.0) * 0.6 + 0.4
    glow(c, 900, 700, 360, AMBER, 0.16 * lt)
    put(c, 900, 760, lambda c: candle(c, t), 1.0, 1.0)
    show(c, t, 524.1, 1150, 120, lambda c: date_stamp(c, "1969", 60, GRAY), anim="stamp")
    show(c, t, tw("mesmo", 527), 1150, 230, T("o mesmo ano em que o livro chegou a Yale", 38), anim="fade")
    if t > tw("homem", 530):
        put(c, 1350, 640, lambda c: cipher_machine(c, t, "OS SEGREDOS DE UM IMPÉRIO"), 0.6, fade_in(t, tw("homem", 530)))
        show(c, t, tw("império", 531), 1350, 820, T("leu", 34, AMBER), anim="fade")
        put(c, 1700, 640, lambda c: (c.rotate(-0.05), closed_codex(c, 0.5, True, t)), 1.0, fade_in(t, tw("conseguiu", 531.5)))
        show(c, t, tw("conseguiu", 531.5), 1700, 820, T("não leu", 34, RED), anim="fade")
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=320)


# ================================================================== BLOCO 4
def s33(c, t):  # 537.5 - 544.7  então, o que é? quatro caminhos
    night(c, t, 1080, moon_xy=None)
    show(c, t, 537.7, 1150, 120, lambda c: stitle(c, "ENTÃO, O QUE É?", 0, 0, 72, AMBER, AMBER), anim="up")
    qt = tw("quatro", 541)
    show(c, t, qt, 1150, 220, T("quatro caminhos", 42), anim="fade")
    put(c, 1150, 600, lambda c: (c.rotate(-0.05), closed_codex(c, 0.8, True, t)), 1.0, fade_in(t, 537.7, 0.8) * fade_out(t, qt, 0.5))
    for i in range(4):
        show(c, t, qt + 0.2 + i * 0.25, 700 + i * 310, 600, lambda c, i=i: theory_card(c, str(i + 1), "?", None, w=260, h=340), anim="up")
    fog(c, t, 1000, 0.05)
    HIST(c, t, [(0, "think"), (541.3, "present")], [(0, "think")], x=240, s=0.85)


def s34(c, t):  # 544.7 - 565.0  1: código
    night(c, t, 1080, moon_xy=None)
    cards_row(c, t, 0, 544.9)
    show(c, t, tw("latim", 549), 1300, 600, lambda c: hl(c, "latim?", 0, 0, 34), anim="pop", t1=553.2)
    show(c, t, tw("italiano", 550), 1300, 700, lambda c: hl(c, "italiano?", 0, 0, 34), anim="pop", t1=553.2)
    show(c, t, tw("escondeu", 550), 1300, 800, T("escondido num sistema próprio", 30, AMBER), anim="fade", t1=553.2)
    show(c, t, tw("médico", 553), 1250, 620, lambda c: (flask(c, (0.70, 0.30, 0.30), 120), text(c, "receitas de médico?", 0, 60, 27, TYPE, INK)),
         anim="pop", t1=559.0)
    show(c, t, tw("alquimista", 555.5), 1600, 620, lambda c: (flask(c, (0.40, 0.70, 0.50), 120), text(c, "fórmula de alquimista?", 0, 60, 27, TYPE, INK)),
         anim="pop", t1=559.0)
    show(c, t, tw("problema", 559), 1350, 980, lambda c: caption_box(c, "nenhuma técnica da época produz esses padrões", 34), anim="up")
    fog(c, t, 1000, 0.05)
    HIST(c, t, [(0, "present"), (559.1, "shrug")], [(0, "neutral"), (559.1, "think")], x=240, s=0.8)


def s35(c, t):  # 565.0 - 590.2  2: língua de verdade num alfabeto inventado; Bax 2014
    night(c, t, 1080, moon_xy=None)
    cards_row(c, t, 1, 565.2)
    langs = (("hebraico", "hebraico"), ("latim", "latim abreviado"), ("turco", "turco antigo"), ("românica", "língua românica"),
             ("astecas", "náuatle (asteca)"))
    bt = tw("Stephen", 578)
    for i, (wd, s) in enumerate(langs):
        show(c, t, tw(wd, 570), 1560, 380 + i * 90, lambda c, s=s: hl(c, s, 0, 0, 30), anim="pop", t1=bt - 0.3)
    if t > bt - 0.3:
        show(c, t, bt, 1560, 380, lambda c: hl(c, "2014 — STEPHEN BAX", 0, 0, 34), anim="up")
        show(c, t, tw("dez", 582), 1560, 470, T("cerca de 10 palavras?", 30, AMBER), anim="fade")
        put(c, 1480, 760, lambda c: vplant(c, 3, 0.55), 1.0, fade_in(t, tw("plantas", 583)))
        put(c, 1680, 640, lambda c: star_mark(c, 26, (0.86, 0.70, 0.32)), 1.0, fade_in(t, tw("constelação", 584)))
    show(c, t, tw("convenceu", 587), 1350, 980, lambda c: date_stamp(c, "NÃO CONVENCEU OS ESPECIALISTAS", 40, RED), anim="stamp")
    fog(c, t, 1000, 0.05)
    HIST(c, t, [(0, "present"), (586.5, "shrug")], [(0, "neutral"), (586.5, "worried")], x=240, s=0.8)


def s36(c, t):  # 590.2 - 597.4  3: língua artificial (Friedman), séculos antes do esperanto
    night(c, t, 1080, moon_xy=None)
    cards_row(c, t, 2, 590.4)
    show(c, t, tw("Friedman", 591), 1560, 420, lambda c: hl(c, "a teoria de Friedman", 0, 0, 32), anim="up")
    show(c, t, tw("séculos", 594), 1560, 520, T("séculos antes do esperanto", 30, AMBER), anim="fade")
    fig(c, t, 1600, 1000, 0.6, [(0, "point_l")], [(0, "confident")], fid=39, appear=591.0, **FRIEDMAN)
    fog(c, t, 1000, 0.05)
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=240, s=0.8)


def s37(c, t):  # 597.4 - 621.1  4: farsa; Gordon Rugg 2004: tabela + grade; sem significado
    night(c, t, 1080, moon_xy=None)
    rt = tw("Gordon", 609)
    if t < rt - 1.0:
        cards_row(c, t, 3, 597.6)
        show(c, t, tw("vendido", 603), 1580, 480, lambda c: (c.scale(1.2, 1.2), coins_pile(c, 8)), anim="drop")
        show(c, t, tw("imperador", 604), 1580, 560, T("vendido caro a um imperador?", 28, AMBER), anim="fade")
    else:
        fig(c, t, 1660, 1000, 0.85, [(0, "stand"), (rt + 2.0, "point_l")], [(0, "neutral"), (rt + 2.0, "confident")], fid=41, appear=rt - 0.8,
            **RUGG)
        show(c, t, rt, 1660, 500, lambda c: hl(c, "GORDON RUGG — 2004", 0, 0, 32), anim="up")
        p = ease_io(prog(t, tw("grade", 613), 4.5))
        put(c, 1030, 520, lambda c: cardan_grille(c, t, p), 1.15, fade_in(t, tw("tabela", 612)))
        show(c, t, tw("tabela", 612), 1030, 140, T("tabela de sílabas + grade com furos", 34, AMBER), anim="fade")
        show(c, t, tw("produzir", 615), 1030, 880, lambda c: (c.translate(-260, 20), vline(c, 0, 0, 520, 40, 77, INK, ease_out(prog(t, tw("produzir", 615), 2.0)))),
             anim="fade")
        show(c, t, tw("Sem", 618.5), 1030, 990, lambda c: date_stamp(c, "SEM NENHUM SIGNIFICADO", 40, RED), anim="stamp")
    fog(c, t, 1000, 0.05)
    HIST(c, t, [(0, "present"), (618.7, "shrug")], [(0, "neutral"), (618.7, "think")], x=240, s=0.8)


def year_x(y):
    return 440 + (y - 1200) / 800 * 1240


def s38(c, t):  # 621.1 - 650.3  carbono 14 (Arizona, 2009): 1404-1438; descarta Bacon e Voynich; Kelley difícil
    night(c, t, 1080, moon_xy=None)
    show(c, t, 621.3, 1150, 110, lambda c: stitle(c, "A CIÊNCIA", 0, 0, 66, AMBER, AMBER), anim="up", t1=624.2)
    at_ = tw("Arizona", 625)
    show(c, t, tw("dois", 624), 1150, 110, lambda c: hl(c, "2009 — UNIVERSIDADE DO ARIZONA", 0, 0, 38), anim="up")
    show(c, t, tw("carbono", 627), 1150, 200, T("datação por carbono 14 do pergaminho", 34), anim="fade")
    rt = tw("entre", 630.5)
    if t > rt - 1.0:
        a = fade_in(t, rt - 1.0, 0.6)
        put(c, 0, 0, lambda c: (line(c, year_x(1200), 600, year_x(2000), 600, 5, INK),
                                [(line(c, year_x(y), 585, year_x(y), 615, 4, INK), text(c, str(y), year_x(y), 650, 26, TYPE, GRAY))
                                 for y in range(1200, 2001, 100)]), 1.0, a)
        if t > rt:
            p = ease_out(prog(t, rt, 1.0))
            x0, x1 = year_x(1404), year_x(1438)
            c.rectangle(x0, 560, (x1 - x0) * p, 80); rgb(c, AMBER, 0.85); c.fill()
            glow(c, (x0 + x1) / 2, 600, 120, AMBER, 0.35 * p)
            show(c, t, rt + 0.6, (x0 + x1) / 2, 480, lambda c: date_stamp(c, "1404 — 1438", 48, AMBER), anim="stamp")
    for wd, after, yr, s in (("Roger", 634.5, 1260, "Roger Bacon"), ("Voynich", 638, 1912, "Voynich")):
        tt = tw(wd, after)
        if t > tt:
            show(c, t, tt, year_x(yr), 760, T(s, 30), anim="fade")
            x_over(c, t, tt + 0.4, year_x(yr), 600, 40)
    kt = tw("Kelley", 641)
    if t > kt:
        show(c, t, kt, year_x(1585), 760, T("Kelley", 30, AMBER), anim="fade")
        show(c, t, kt, year_x(1585), 600, lambda c: big_q(c, 70), anim="pop")
        show(c, t, tw("couro", 644), 1150, 920, lambda c: caption_box(c, "guardar o couro de 14 bezerros por mais de 100 anos?", 34), anim="up")
    fog(c, t, 1040, 0.04)
    HIST(c, t, [(0, "present"), (634.9, "point_r"), (641.2, "think")], [(0, "neutral"), (641.2, "think")], x=220, s=0.75)


def s39(c, t):  # 650.3 - 667.4  Lisa Fagin Davis (2020): cinco escribas; farsa = equipe; texto real = grupo sabia ler
    shelves(c, t, 0.3)
    fig(c, t, 1680, 1000, 0.85, [(0, "stand"), (652.0, "point_l"), (659.8, "think")], [(0, "confident")], fid=42, appear=650.4, **DAVIS)
    show(c, t, tw("Lisa", 652), 1680, 500, lambda c: hl(c, "LISA FAGIN DAVIS", 0, 0, 32), anim="up")
    show(c, t, tw("Lisa", 652) + 0.4, 1680, 570, T("paleógrafa, 2020", 26), anim="fade")
    ct = tw("cinco", 657)
    for k in range(5):
        x = 640 + k * 190
        show(c, t, ct + k * 0.25, x, 420, lambda c, k=k: (c.translate(-60, 0), vline(c, 0, 0, 160, 28 + k * 3, 90 + k, INK)), anim="fade")
        show(c, t, ct + k * 0.25, x, 560, lambda c, k=k: (c.scale(0.55, 0.55), quill(c)), anim="pop")
        show(c, t, ct + k * 0.25, x, 640, T(str(k + 1), 34, AMBER), anim="fade")
    show(c, t, tw("Cinco", 658), 1030, 160, lambda c: stitle(c, "CINCO ESCRIBAS", 0, 0, 70, AMBER, AMBER), anim="up")
    show(c, t, tw("farsa", 660), 1030, 830, lambda c: caption_box(c, "se for farsa: trabalho de equipe", 36), anim="up", t1=tw("E", 662.3) - 0.1)
    show(c, t, tw("verdade", 663), 1030, 830, lambda c: caption_box(c, "se for real: um grupo sabia ler essa escrita", 36), anim="up")
    fog(c, t, 1000, 0.05)
    HIST(c, t, [(0, "present"), (658.2, "point_r")], [(0, "neutral"), (658.2, "shocked")], x=240, s=0.8)


def s40(c, t):  # 667.4 - 690.7  2024: imagens multiespectrais; três colunas apagadas; Marci?; também não conseguiu
    c.rectangle(0, 0, W, H); rgb(c, (0.04, 0.04, 0.05)); c.fill()
    px, py, ps = 1060, 540, 1.05
    put(c, px, py, lambda c: manuscript_page(c, "first", 520, 700, 1, t), ps)
    show(c, t, 667.6, 1060, 70, lambda c: hl(c, "2024 — LUZES DE VÁRIAS CORES", 0, 0, 38), anim="up", t1=tw("Davis", 678) - 0.2)
    st = tw("imagens", 668)
    if st < t < st + 5.5:
        p = prog(t, st, 5.0)
        for k, col in enumerate(((0.95, 0.30, 0.25), (0.35, 0.85, 0.40), (0.35, 0.50, 0.98), UVC)):
            y = 160 + ((p * 4 - k * 0.6) % 1.4) * 760
            c.rectangle(px - 300, y, 600, 46); rgb(c, col, 0.25); c.fill()
    ct = tw("três", 672)
    if t > ct:
        a = fade_in(t, ct, 1.2)
        rrect(c, px - 270, py - 330, 150, 560, 8); rgb(c, VELLUM, 0.92 * a); c.fill()
        lat = "abcdefghiklm"
        for i, ch in enumerate(lat):
            y = py - 300 + i * 44
            text(c, ch, px - 250, y, 28, HAND, (0.62, 0.20, 0.18), alpha=a)
            c.save(); c.translate(px - 212, y + 8); vword(c, "oaedyklrsqnt"[i], 26, (0.30, 0.20, 0.12)); c.restore()
            text(c, lat[(i + 1) % len(lat)], px - 150, y, 28, HAND, (0.62, 0.20, 0.18), alpha=a)
        show(c, t, ct + 0.3, 1600, 420, lambda c: hl(c, "três colunas apagadas", 0, 0, 32), anim="up")
        show(c, t, tw("alfabeto", 674), 1600, 500, T("alfabeto latino + letras do Voynich", 26, AMBER), anim="fade")
    dt = tw("Davis", 678)
    show(c, t, dt, 1060, 70, lambda c: hl(c, "UMA TENTATIVA DE DECIFRAR?", 0, 0, 38), anim="up")
    show(c, t, tw("Marci", 681), 1600, 640, lambda c: caption_box(c, "talvez Marci, séc. XVII", 30), anim="up")
    show(c, t, tw("trezentos", 686), 1060, 990, T("há mais de 300 anos...", 36, INK), anim="fade", t1=688.5)
    show(c, t, tw("também", 688.5), 1060, 990, lambda c: date_stamp(c, "TAMBÉM NÃO CONSEGUIU", 44, RED), anim="stamp")
    fog(c, t, 1040, 0.03)
    HIST(c, t, [(0, "point_r"), (674.9, "present"), (688.7, "shrug")], [(0, "neutral"), (674.9, "shocked"), (688.7, "sad")], x=240, s=0.8)


def s41(c, t):  # 690.7 - 717.3  digitalizado; IA; 2017 "hebraico"; milhares tentam; ninguém leu com certeza
    night(c, t, 1080, moon_xy=None)
    crt = tw("Milhares", 709)
    if t < crt:
        def screen(c):
            c.save(); c.translate(0, 0); manuscript_page(c, "herbal", 520, 700, 12, t); c.restore()
        put(c, 1080, 520, lambda c: monitor(c, lambda c: (c.scale(0.34, 0.34), screen(c)), 640, 420), 1.0, fade_in(t, 690.9))
        show(c, t, 691.0, 1080, 110, lambda c: hl(c, "DIGITALIZADO — DE GRAÇA NA INTERNET", 0, 0, 38), anim="up", t1=tw("Programas", 696) - 0.2)
        pt = tw("Programas", 696)
        if t > pt:
            show(c, t, pt, 1080, 110, lambda c: hl(c, "COMPUTADORES E INTELIGÊNCIA ARTIFICIAL", 0, 0, 38), anim="up")
            rnd = random.Random(int(t * 6))
            for r in range(5):
                s = "".join(rnd.choice("01") for _ in range(22))
                text(c, s, 1600, 320 + r * 50, 26, TYPE, (0.40, 0.80, 0.55), alpha=0.8)
        ht = tw("hebraico", 704)
        show(c, t, tw("dois", 700), 1080, 860, lambda c: caption_box(c, "2017: IA diz \"é hebraico\"", 40), anim="up", t1=tw("Quem", 706.5) - 0.1)
        if t > tw("Quem", 706.5):
            show(c, t, tw("Quem", 706.5), 1080, 860, lambda c: caption_box(c, "quem fala hebraico não reconheceu as frases", 36), anim="up")
            x_over(c, t, tw("reconheceu", 707), 1400, 520, 60)
    else:
        put(c, 1080, 360, lambda c: crowd(c, t, crt, 220, 22, 44, appear_d=2.5, s=0.18), 1.0)
        show(c, t, crt, 1080, 110, lambda c: hl(c, "MILHARES TENTAM, TODOS OS DIAS", 0, 0, 38), anim="up")
        show(c, t, tw("Ninguém", 713), 1080, 960, lambda c: date_stamp(c, "NINGUÉM LEU UMA FRASE COM CERTEZA", 40, RED), anim="stamp")
    fog(c, t, 1040, 0.04)
    HIST(c, t, [(0, "present"), (700.6, "think"), (713.5, "shrug")], [(0, "neutral"), (713.5, "worried")], x=240, s=0.8)


def s42(c, t):  # 717.3 - 735.0  cinco pessoas escreveram com calma; sabiam o que diziam; levaram com elas
    c.rectangle(0, 0, W, H); rgb(c, (0.04, 0.035, 0.035)); c.fill()
    out = tw("levaram", 732.5)
    for k in range(5):
        lit = 1.0 if t < out else fade_out(t, out + k * 0.35, 0.7)
        scribe_desk(c, t, 560 + k * 265, lit * fade_in(t, 717.5 + k * 0.4, 0.8), k + 1)
    show(c, t, 717.6, 1160, 110, T("norte da Itália? Europa Central? há 600 anos...", 38), anim="fade", t1=tw("sabiam", 729.5) - 0.2)
    show(c, t, tw("cinco", 721), 1160, 190, lambda c: hl(c, "cinco pessoas, linha por linha", 0, 0, 36), anim="up", t1=tw("sabiam", 729.5) - 0.2)
    show(c, t, tw("sabiam", 729.5), 1160, 150, lambda c: stitle(c, "ELAS SABIAM O QUE ESTAVAM DIZENDO", 0, 0, 52, AMBER, AMBER), anim="up",
         t1=out + 1.5)
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=230, s=0.8, appear=718.0)


def s43(c, t):  # 735.0 - 745.2  e você? código, língua perdida ou farsa?
    night(c, t, 1080, moon_xy=None)
    show(c, t, 735.1, 1150, 110, lambda c: stitle(c, "E você?", 0, 0, 72, INK, AMBER), anim="up")
    opts = (("código?", tw("código", 735.5), 0), ("língua perdida?", tw("língua", 736), 1), ("farsa?", tw("farsa", 737), 3))
    for i, (s, tt, ic) in enumerate(opts):
        show(c, t, tt, 720 + i * 400, 520, lambda c, s=s, ic=ic: theory_card(c, str(i + 1), s, card_icon(ic, t), w=320, h=400), anim="up")
    show(c, t, tw("Deixa", 741), 1150, 920, lambda c: (speech(c, 820, 130, -300, 110), text(c, "deixe sua teoria nos comentários", 0, 0, 42, HAND, INK)),
         anim="pop")
    HIST(c, t, [(0, "point_r"), (741.4, "present")], [(0, "think"), (741.4, "happy")], x=220, s=0.8)


def s44(c, t):  # 745.2 - fim  encerramento
    night(c, t, 740, moon_xy=(1640, 160))
    shelves(c, t, 0.25 * fade_in(t, 745.2, 2.0))
    put(c, 1660, 640, lambda c: (c.rotate(-0.06), closed_codex(c, 0.7, True, t)), 1.0, 0.8 * fade_in(t, 745.3, 2.0))
    HIST(c, t, [(0, "stand"), (745.6, "present"), (748.5, "wave"), (750.5, "stand")], [(0, "neutral"), (747.0, "happy")], x=420, s=1.05)
    show(c, t, 745.4, 1100, 260, T("Eu sou o Historiador.", 44, AMBER), anim="fade")
    show(c, t, 747.0, 1100, 470, sc(subscribe_btn, t > 748.5, s=0.9))
    show(c, t, 747.4, 1430, 470, sc(bell, s=0.8), rot=math.sin(t * 18) * 0.2 * max(0, 1 - (t - 747.4)))
    show(c, t, 748.0, 1100, 720, lambda c: (text(c, "PONTO CEGO", 0, 0, 84, SERIF, INK), line(c, -300, 58, 300, 58, 3, AMBER)), anim="fade", d=1.2)
    fog(c, t, 980, 0.09)


SCENES = [
    (0.0, 16.4, s01), (16.4, 37.9, s02), (37.9, 54.1, s03), (54.1, 59.9, s04), (59.9, 72.4, s05), (72.4, 98.6, s06),
    (98.6, 120.2, s07), (120.2, 136.1, s08), (136.1, 152.6, s09), (152.6, 165.8, s10), (165.8, 172.8, s11),
    (172.8, 181.3, s12), (181.3, 199.6, s13), (199.6, 216.9, s14), (216.9, 235.4, s15), (235.4, 259.2, s16),
    (259.2, 275.6, s17), (275.6, 297.5, s18), (297.5, 314.0, s19), (314.0, 336.2, s20), (336.2, 351.5, s21),
    (351.5, 361.4, s22), (361.4, 384.3, s23), (384.3, 406.2, s24), (406.2, 434.3, s25), (434.3, 443.7, s26),
    (443.7, 461.2, s27), (461.2, 473.1, s28), (473.1, 491.2, s29), (491.2, 502.8, s30), (502.8, 523.9, s31),
    (523.9, 537.5, s32),
    (537.5, 544.7, s33), (544.7, 565.0, s34), (565.0, 590.2, s35), (590.2, 597.4, s36), (597.4, 621.1, s37),
    (621.1, 650.3, s38), (650.3, 667.4, s39), (667.4, 690.7, s40), (690.7, 717.3, s41), (717.3, 735.0, s42),
    (735.0, 745.2, s43), (745.2, 999.0, s44),
]

# Sons: nada automático (sem whoosh em transição, sem som em cada ícone). Só toques sem chiado nos momentos-chave.
SFX_OFF = True
SFX = [(4.0, "tum"), (50.8, "boom"), (54.4, "boom"), (170.0, "boom"), (176.3, "tum"), (197.5, "tum"), (251.4, "bell"),
       (305.6, "boom"), (384.5, "tum"), (441.9, "boom"), (472.0, "heartbeat"), (516.6, "boom"), (618.6, "tum"), (658.2, "boom"),
       (688.7, "tum"), (733.0, "bell"), (748.0, "boom")]
