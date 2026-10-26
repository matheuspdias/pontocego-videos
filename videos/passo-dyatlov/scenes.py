"""O Passo Dyatlov (1959) — Ponto Cego.
Narração: Pedro Lima - Serious (HeyGen / ElevenLabs v4), 4 blocos com 1 s de silêncio entre eles (~881,3 s).
Tempos absolutos (já com os offsets dos blocos): transcricao.txt e palavras.json (gerados por tempos.py).
tw("palavra", depois_de) devolve o início da primeira palavra que começa com esse texto depois do tempo dado.
Objetos do caso (barraca comprida, cedro, fogueira, trem, caminhão, Geiger, esferas, placa...) ficam no engine.py
(seção PASSO DYATLOV). Ninguém aparece morto: os lugares onde o grupo foi encontrado são marcados com bandeirinhas.
"""
import json
import os
import unicodedata

from engine import *

THEME = "neve"

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


# ------------------------------------------------------------------ o grupo (cor do casaco de cada um)
GRUPO = [  # (nome curto, cor, cabelo comprido?)
    ("Igor Dyatlov", (0.74, 0.22, 0.20), False),
    ("Zinaida Kolmogorova", (0.86, 0.50, 0.22), True),
    ("Lyudmila Dubinina", (0.50, 0.38, 0.64), True),
    ("Yuri Doroshenko", (0.30, 0.46, 0.66), False),
    ("Yuri Krivonischenko", (0.32, 0.56, 0.40), False),
    ("Rustem Slobodin", (0.82, 0.62, 0.26), False),
    ("Nikolai Thibeaux-Brignolle", (0.40, 0.60, 0.70), False),
    ("Alexander Kolevatov", (0.52, 0.36, 0.24), False),
    ("Semyon Zolotaryov", (0.46, 0.48, 0.44), False),
]
YUDIN = ("Yuri Yudin", (0.68, 0.44, 0.50), False)
NOMES = ["IGOR DYATLOV", "ZINAIDA KOLMOGOROVA", "LYUDMILA DUBININA", "YURI DOROSHENKO", "YURI KRIVONISCHENKO",
         "RUSTEM SLOBODIN", "NIKOLAI THIBEAUX-BRIGNOLLE", "ALEXANDER KOLEVATOV", "SEMYON ZOLOTARYOV"]

IVANOV = dict(shirt=(0.86, 0.86, 0.82), coat=(0.22, 0.24, 0.30), hat="fedora", hat_col=(0.20, 0.20, 0.24), hair=None, mustache=False)
SOLDADO = dict(shirt=(0.36, 0.40, 0.28), coat=(0.32, 0.36, 0.24), hat="pilot", hat_col=(0.30, 0.34, 0.22), hair=None)
CIENTISTA = dict(shirt=(0.86, 0.86, 0.82), coat=(0.30, 0.34, 0.42), glasses=True, hair="tuft")
CIENTISTA2 = dict(shirt=(0.86, 0.86, 0.82), coat=(0.24, 0.26, 0.30), glasses=True, hair=None, mustache=True)
PROMOTOR = dict(shirt=(0.86, 0.86, 0.82), coat=(0.14, 0.16, 0.22), hair="tuft", glasses=False)


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


def x_over(c, t, t0, x, y, s=70):
    show(c, t, t0, x, y, lambda c: big_x(c, s, RED, 14), anim="stamp")


def member(c, t, i, x, y, s=0.7, poses=((0, "stand"),), exprs=((0, "neutral"),), appear=None, alpha=1.0, who=None):
    """um integrante do grupo (gorro e casaco na cor dele)"""
    nome, col, longo = who or (YUDIN if i == 9 else GRUPO[i])
    faded(c, alpha, lambda c: figure(c, t, x, y, s, poses=poses, exprs=exprs, shirt=col, hat="beanie", hat_col=col,
                                     hair="long" if longo else None, fid=20 + i, appear=appear))


def sky(c, t, horizon=700, moon_xy=(1640, 160)):
    stars(c, t, 80, horizon - 40)
    if moon_xy:
        c.save(); c.translate(*moon_xy); moon(c, 50); c.restore()
        glow(c, moon_xy[0], moon_xy[1], 220, ICE, 0.10)


def snowland(c, y=860, col=(0.78, 0.82, 0.88)):
    c.move_to(0, y)
    for x in range(0, W + 80, 80):
        c.line_to(x, y + math.sin(x / 260) * 16)
    c.line_to(W, H); c.line_to(0, H); c.close_path()
    g = cairo.LinearGradient(0, y, 0, H)
    g.add_color_stop_rgb(0, *col); g.add_color_stop_rgb(1, col[0] * 0.75, col[1] * 0.78, col[2] * 0.84)
    c.set_source(g); c.fill()


def slope_y(x, x0=560, ybot=900, ytop=360):
    """encosta: sobe da esquerda (baixo, floresta) para a direita (alto, barraca)"""
    if x <= x0:
        return ybot
    return ybot - (x - x0) / (W - x0) * (ybot - ytop)


def slope(c, x0=560, ybot=900, ytop=360, col=(0.80, 0.84, 0.90)):
    c.move_to(0, ybot); c.line_to(x0, ybot)
    for x in range(x0, W + 40, 40):
        c.line_to(x, slope_y(x, x0, ybot, ytop) + math.sin(x / 90) * 4)
    c.line_to(W, H); c.line_to(0, H); c.close_path()
    g = cairo.LinearGradient(0, ytop, 0, H)
    g.add_color_stop_rgb(0, *col); g.add_color_stop_rgb(1, col[0] * 0.72, col[1] * 0.76, col[2] * 0.84)
    c.set_source(g); c.fill()


def forest(c, y=900, x0=-40, x1=620, n=9, seed=3, h=(200, 320), col=(0.12, 0.20, 0.17)):
    rnd = random.Random(seed)
    for k in range(n):
        x = x0 + (x1 - x0) * (k + rnd.uniform(-0.2, 0.2)) / max(1, n - 1)
        c.save(); c.translate(x, y + rnd.uniform(-8, 8)); pine(c, rnd.uniform(*h), col); c.restore()


def far_mountains(c, y=760, a=1.0):
    faded(c, a, lambda c: (c.save(), c.translate(960, y), mountains(c, 2300, 360, col=(0.17, 0.20, 0.27)), c.restore()))


def flag(c, col=RED, label=None, size=28):
    """bandeirinha de marcação (base em 0,0)"""
    line(c, 0, 0, 0, -90, 5, (0.70, 0.66, 0.60))
    poly(c, [(0, -90), (46, -76), (0, -62)]); fs(c, col, 3)
    if label:
        text(c, label, 0, 30, size, HAND, DARKTXT)


def theory_card(c, n, title_s, icon=None, crossed=0.0, dim=False, w=330, h=420, sub=None):
    rrect(c, -w / 2, -h / 2, w, h, 14); fs(c, (0.10, 0.12, 0.15), 5, ICE if not dim else LGRAY)
    text(c, n, 0, -h / 2 + 44, 32, TYPE, AMBER)
    text(c, title_s, 0, -h / 2 + 96, 38 if len(title_s) < 12 else 30, SERIF, INK if not dim else GRAY)
    if sub:
        text(c, sub, 0, h / 2 - 36, 26, TYPE, GRAY)
    if icon:
        c.save(); c.translate(0, 60); icon(c); c.restore()
    if crossed > 0:
        c.save(); c.scale(crossed, crossed); big_x(c, 120, RED, 14); c.restore()


def tag_header(c, n, title_s):
    """faixa de título de teoria (número + nome)"""
    full = f"{n}  ·  {title_s}"
    w = text_w(c, full, 52, SERIF) + 90
    rrect(c, -w / 2, -48, w, 96, 14); fs(c, (0.10, 0.12, 0.15), 5, ICE)
    text(c, n, -w / 2 + 50, 0, 44, TYPE, AMBER)
    text(c, title_s, 30, 0, 52, SERIF, INK)


def wind_lines(c, t, n=10, y0=200, y1=800, a=0.35, speed=900):
    rnd = random.Random(7)
    for k in range(n):
        y = rnd.uniform(y0, y1)
        x = ((t * speed * rnd.uniform(0.7, 1.3) + rnd.uniform(0, W)) % (W + 600)) - 300
        line(c, x, y, x + 220, y - 20, 3, (0.90, 0.94, 1.0))


# ------------------------------------------------------------------ mapa estilizado dos Urais (lon, lat)
URAL = make_proj(54.5, 66.5, 56.2, 62.4, box=(560, 90, 1780, 1010))
SVERD = (60.6, 56.84)
IVDEL = (60.42, 60.69)
VIZHAI = (60.22, 61.22)
SEGUNDO_N = (59.95, 61.50)
KHOLAT = (59.45, 61.75)
OTORTEN = (59.40, 61.88)
ROTA = [SVERD, (60.3, 58.0), (60.0, 59.4), IVDEL, VIZHAI, SEGUNDO_N, KHOLAT, OTORTEN]
RIDGE = [(59.0, 56.2), (59.3, 57.2), (59.2, 58.2), (59.0, 59.0), (59.2, 59.8), (59.35, 60.6), (59.3, 61.3), (59.4, 61.9), (59.5, 62.4)]


def ural_map(c, t, p=1.0, show_route=True, labels=True, upto=None):
    c.rectangle(500, 60, 1340, 980); rgb(c, (0.07, 0.09, 0.13)); c.fill_preserve(); rgb(c, ICE, 0.35); c.set_line_width(3); c.stroke()
    for lat in range(57, 63):
        x0, y = URAL(54.5, lat); x1, _ = URAL(66.5, lat)
        line(c, max(x0, 500), y, min(x1, 1840), y, 1, (0.20, 0.26, 0.34))
    for k in range(len(RIDGE) - 1):
        (xa, ya), (xb, yb) = URAL(*RIDGE[k]), URAL(*RIDGE[k + 1])
        for j in range(2):
            u = j / 2
            x, y = xa + (xb - xa) * u, ya + (yb - ya) * u
            poly(c, [(x - 26, y + 16), (x, y - 24), (x + 26, y + 16)]); fs(c, (0.30, 0.34, 0.42), 3, (0.66, 0.72, 0.82))
    text(c, "MONTES URAIS", *URAL(57.4, 58.6), 30, SERIF, (0.66, 0.74, 0.86))
    if show_route:
        map_path(c, URAL, ROTA, p, AMBER, 6, dash=[14, 10])
    if labels:
        for (lon, lat), s, dx in ((SVERD, "Sverdlovsk", 90), (IVDEL, "Ivdel", 70), (VIZHAI, "Vizhai", 80)):
            map_point(c, URAL, lon, lat, AMBER, 9, t)
            map_label(c, URAL, lon, lat, s, 30, INK, dx=dx)
        map_point(c, URAL, *OTORTEN, RED, 9, t)
        map_label(c, URAL, *OTORTEN, "Otorten", 30, INK, dx=-90, dy=-24)


# ================================================================== BLOCO 1
def s01(c, t):  # 0 - 8.0  noite de fevereiro; nove jovens saem correndo da barraca
    sky(c, t, 640)
    far_mountains(c, 910)
    slope(c)
    tx = 1500
    put(c, tx, slope_y(tx) + 6, lambda c: dyatlov_tent(c, t, glow_on=True), 0.8)
    st = tw("saíram", 4)
    for k in range(9):
        t0 = st + k * 0.22
        if t > t0:
            d = (t - t0) * 120
            x = tx - 160 - d
            member(c, t, k, x, slope_y(x) + 4, 0.42, [(0, "run")], [(0, "shocked")])
    show(c, t, 0.3, 1150, 150, T("fevereiro de 1959", 44, ICE), anim="fade", t1=7.4)
    show(c, t, tw("União", 2.5), 1150, 220, T("Montes Urais, União Soviética", 34, INK), anim="fade", t1=7.4)
    snow(c, t, 120, 70, 0.6)
    fog(c, t, 900, 0.07)
    HIST(c, t, [(0, "stand"), (4.6, "point_r")], [(0, "neutral"), (4.6, "worried")], appear=0.4, x=260)


def s02(c, t):  # 8.0 - 14.9  trinta graus negativos; sem botas, sem casacos
    sky(c, t, 700, moon_xy=(1700, 150))
    snowland(c, 860)
    show(c, t, 8.3, 1100, 420, sc(thermometer, "-30 °C", 0.08, s=1.4), anim="pop")
    bt, ct = tw("botas", 12), tw("casacos", 13.5)
    show(c, t, bt - 0.5, 1500, 300, lambda c: (felt_boot(c), text(c, "botas", 0, 160, 32, HAND, INK)), anim="up")
    x_over(c, t, bt + 0.1, 1500, 300, 80)
    show(c, t, ct - 0.5, 1500, 600, lambda c: (winter_coat(c), text(c, "casacos", 0, 160, 32, HAND, INK)), anim="up")
    x_over(c, t, ct + 0.1, 1500, 600, 80)
    snow(c, t, 220, 160, 0.85)
    fog(c, t, 880, 0.08)
    HIST(c, t, [(0, "stand"), (8.4, "hips")], [(0, "worried")])


def s03(c, t):  # 14.9 - 23.5  rasgaram a lona por dentro e fugiram no escuro
    c.rectangle(0, 0, W, H); rgb(c, (0.03, 0.035, 0.05)); c.fill()
    snowland(c, 820, (0.60, 0.64, 0.72))
    rt = tw("Rasgaram", 16)
    put(c, 1150, 760, lambda c: dyatlov_tent(c, t, cut=prog(t, rt + 0.2, 2.2), glow_on=t < rt + 4.5), 1.3)
    if rt - 0.3 < t < rt + 2.6:
        p = prog(t, rt + 0.2, 2.2)
        put(c, 1000 + p * 260, 560 + p * 80, knife, 0.7, fade_out(t, rt + 2.3, 0.3))
    show(c, t, tw("porta", 15.5), 1150, 170, lambda c: hl(c, "não saíram pela porta", 0, 0, 46), anim="up", t1=rt + 1.5)
    show(c, t, rt + 1.6, 1150, 170, lambda c: hl(c, "rasgaram a lona por DENTRO", 0, 0, 50), anim="up")
    ft = tw("fugiram", 18.5)
    c.save(); c.translate(1000, 900); footprints(c, 12, -60, 6, t, ft); c.restore()
    c.save(); c.translate(1040, 940); footprints(c, 12, -62, 8, t, ft + 0.2); c.restore()
    show(c, t, tw("escuro", 21), 1150, 1000, T("montanha abaixo, no escuro", 36, ICE), anim="fade")
    snow(c, t, 90, 40, 0.5)
    HIST(c, t, [(0, "point_r"), (rt + 1.6, "present")], [(0, "worried"), (rt + 1.6, "shocked")], x=260)


def s04(c, t):  # 23.5 - 33.6  semanas depois: fogueira apagada; outros no meio da encosta
    sky(c, t, 500, moon_xy=None)
    slope(c)
    forest(c, 900, 360, 700, 5, 4)
    tx = 1640
    put(c, tx, slope_y(tx) + 6, lambda c: dyatlov_tent(c, t, cut=1, sag=0.6, snow_on=1), 0.6)
    show(c, t, 23.7, 1150, 140, lambda c: date_stamp(c, "SEMANAS DEPOIS", 44, RED), anim="stamp")
    ft = tw("fogueira", 28)
    show(c, t, ft - 0.4, 640, 905, lambda c: campfire_out(c, t), anim="fade")
    show(c, t, ft, 640, 1010, T("fogueira apagada", 30, DARKTXT), anim="fade")
    et = tw("encosta", 30)
    for k, x in enumerate((960, 1150, 1360)):
        show(c, t, et - 0.6 + k * 0.35, x, slope_y(x) + 10, lambda c: flag(c, RED), anim="drop")
    show(c, t, et + 0.6, 1170, 300, lambda c: caption_box(c, "como se tentassem voltar", 38), anim="up")
    if t > tw("voltar", 32):
        arrow(c, 980, slope_y(980) - 60, 1500, slope_y(1500) - 80, AMBER, 5, 0.1)
    snow(c, t, 80, 30, 0.5)
    fog(c, t, 930, 0.06)
    HIST(c, t, [(0, "present"), (et, "point_r")], [(0, "sad")], x=250)


def s05(c, t):  # 33.6 - 42.3  os últimos quatro: três meses depois, na ravina, ossos quebrados
    sky(c, t, 420, moon_xy=None)
    snowland(c, 520, (0.72, 0.76, 0.84))
    c.move_to(700, 520); c.curve_to(860, 760, 1060, 900, 1180, 1080); c.line_to(1500, 1080); c.curve_to(1440, 860, 1520, 660, 1640, 520)
    c.close_path(); rgb(c, (0.16, 0.18, 0.24)); c.fill()
    forest(c, 540, 1500, 1900, 4, 9, (180, 260))
    show(c, t, 33.9, 1150, 130, lambda c: date_stamp(c, "TRÊS MESES DEPOIS", 46, RED), anim="stamp")
    rt = tw("ravina", 37)
    show(c, t, rt - 0.3, 1290, 600, T("a ravina", 34, INK), anim="fade")
    for k in range(4):
        show(c, t, rt + 0.2 + k * 0.25, 1180 + k * 70, 880 + (k % 2) * 30, lambda c: flag(c, AMBER), anim="drop")
    show(c, t, tw("ossos", 38.5), 1150, 300, lambda c: hl(c, "ossos quebrados", 0, 0, 46), anim="up")
    show(c, t, tw("acidente", 40.8), 1150, 390, lambda c: caption_box(c, "como num acidente de carro", 36), anim="up")
    fog(c, t, 900, 0.07)
    HIST(c, t, [(0, "stand"), (38.7, "point_r")], [(0, "worried"), (38.7, "shocked")], x=260)


def s06(c, t):  # 42.3 - 58.4  "força natural irresistível"; arquivo secreto; sessenta anos
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.05, 0.06)); c.fill()
    glow(c, 1100, 520, 700, LYELLOW, 0.08)
    a = fade_out(t, tw("papéis", 49.8) + 0.4, 0.6)
    put(c, 1100, 520, lambda c: soviet_doc(c, "CONCLUSÃO", 6, 620, 640), 1.0, a * fade_in(t, 42.5))
    if a > 0:
        typewrite(c, t, tw("eles", 45.5), "força natural", 1100, 560, 52, DARKTXT, 14)
        typewrite(c, t, tw("natural", 47.5), "irresistível", 1100, 630, 52, BLOOD, 14)
    pt = tw("papéis", 49.8)
    show(c, t, pt, 1100, 520, lambda c: folder(c, "SECRETO", True), s=1.6, anim="drop")
    st = tw("sessenta", 53.5)
    show(c, t, st, 1100, 880, lambda c: caption_box(c, "mais de 60 anos sem explicação", 40), anim="up")
    show(c, t, tw("noite", 57.3), 1600, 300, sc(big_q, 140, AMBER), anim="pop")
    HIST(c, t, [(0, "think"), (pt, "present")], [(0, "think"), (st, "worried")])


def s07(c, t):  # 58.4 - 61.9  título
    sky(c, t, 700)
    far_mountains(c, 910)
    snowland(c, 900)
    put(c, 1480, 900, lambda c: dyatlov_tent(c, t, cut=1, sag=0.4, snow_on=0.6), 0.7)
    show(c, t, 58.6, 1100, 300, lambda c: (text(c, "O MISTÉRIO DO", 0, -80, 44, TYPE, AMBER),
                                          stitle(c, "PASSO DYATLOV", 0, 10, 120, INK, AMBER)), anim="fade", d=1.0)
    snow(c, t, 140, 80, 0.7)
    fog(c, t, 900, 0.09)
    HIST(c, t, [(0, "stand"), (59.0, "present")], [(0, "neutral"), (59.0, "think")], appear=58.5, x=280)


def s08(c, t):  # 61.9 - 73.4  Sverdlovsk, janeiro de 1959, centro industrial, Urais
    sky(c, t, 600, moon_xy=(1700, 140))
    far_mountains(c, 830, 0.9 * fade_in(t, tw("Montes", 71.5)))
    c.rectangle(0, 820, W, H - 820); rgb(c, (0.70, 0.74, 0.80)); c.fill()
    for k, x in enumerate((760, 1150, 1540)):
        show(c, t, tw("centros", 68.5) - 0.3 + k * 0.3, x, 830, lambda c, k=k: factory(c, t, 380 if k != 1 else 460, 200 + k * 20), anim="up")
    show(c, t, 62.1, 1150, 140, lambda c: date_stamp(c, "JANEIRO DE 1959", 50, RED), anim="stamp")
    typewrite(c, t, tw("Sverdlovsk", 64.8), "Sverdlovsk  (hoje Ecaterimburgo)", 1150, 240, 40, INK)
    show(c, t, tw("Urais", 72.0), 1150, 960, T("aos pés dos Montes Urais", 34, DARKTXT), anim="fade")
    snow(c, t, 70, 30, 0.45)
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=250)


def politecnico(c):
    c.rectangle(-420, -300, 840, 300); fs(c, (0.30, 0.30, 0.34), 6)
    poly(c, [(-460, -300), (0, -420), (460, -300)]); fs(c, (0.36, 0.36, 0.40), 6)
    for k in range(8):
        x = -350 + k * 100
        c.rectangle(x - 18, -280, 36, 280); fs(c, (0.62, 0.62, 0.64), 4)
    for r in range(2):
        for k in range(7):
            c.rectangle(-320 + k * 100, -250 + r * 120, 40, 70); rgb(c, (0.88, 0.70, 0.36), 0.55 + 0.25 * ((k + r) % 2)); c.fill()


def s09(c, t):  # 73.4 - 87.7  Instituto Politécnico dos Urais; estudantes planejam a travessia
    sky(c, t, 600, moon_xy=None)
    c.rectangle(0, 860, W, H - 860); rgb(c, (0.72, 0.76, 0.82)); c.fill()
    gt = tw("grupo", 80.5)
    put(c, 1150, 860, politecnico, 0.95 * (1 - 0.35 * prog(t, gt, 1.0)), fade_in(t, 73.6))
    show(c, t, tw("Instituto", 74), 1150, 140, lambda c: hl(c, "Instituto Politécnico dos Urais", 0, 0, 44), anim="up")
    for k in range(5):
        member(c, t, k + 3, 820 + k * 150, 1010, 0.55, [(0, "stand"), (gt + 2.5, "think" if k % 2 else "point_r")],
               [(0, "happy")], appear=gt + k * 0.15)
    show(c, t, tw("travessias", 84), 1150, 300, lambda c: caption_box(c, "uma das travessias mais difíceis da época", 38), anim="up")
    snow(c, t, 50, 20, 0.35)
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=250)


def s10(c, t):  # 87.7 - 97.2  Igor Dyatlov, 23 anos, engenharia de rádio; metódico
    sky(c, t, 640, moon_xy=(1700, 160))
    snowland(c, 900)
    member(c, t, 0, 1150, 960, 1.15, [(0, "stand"), (93.4, "hips")], [(0, "confident")], appear=88.8)
    show(c, t, tw("Igor", 88.5), 1150, 130, lambda c: hl(c, "IGOR DYATLOV", 0, 0, 50), anim="up")
    show(c, t, tw("vinte", 89.8), 1550, 380, T("23 anos", 44, AMBER), anim="pop")
    show(c, t, tw("rádio", 92), 1580, 480, lambda c: (signal_wave(c, t, 240, 16, 0, 0.5, 0.1, ICE, 4, 3),
                                                     text(c, "engenharia de rádio", 0, 50, 30, HAND, INK)), anim="fade")
    for k, s in enumerate(("metódico", "experiente", "não arriscava à toa")):
        show(c, t, tw(("metódico", "experiente", "conhecido")[k], 93) , 1580, 620 + k * 70, T(s, 34, INK), anim="left")
    snow(c, t, 60, 30, 0.4)
    HIST(c, t, [(0, "point_r")], [(0, "neutral")], x=260)


def s11(c, t):  # 97.2 - 113.0  plano: 300 km de esqui até Otorten; terceiro grau; mestre em esporte
    ural_map(c, t, prog(t, tw("percorrer", 97.5), 4.5))
    show(c, t, tw("trezentos", 99), 1450, 760, lambda c: caption_box(c, "~300 km de esqui", 40), anim="up")
    show(c, t, tw("Otorten", 103), 1200, 230, lambda c: hl(c, "monte Otorten", 0, 0, 36), anim="up", t1=tw("travessia", 105) - 0.2)
    gt = tw("terceiro", 106.5)
    show(c, t, gt, 1450, 400, lambda c: (circle(c, 0, 0, 90, (0.10, 0.12, 0.16), 6, AMBER), text(c, "III", 0, -12, 64, SERIF, AMBER),
                                       text(c, "grau", 0, 46, 26, TYPE, INK)), anim="stamp")
    show(c, t, tw("mestre", 111), 1450, 900, T("prêmio: título de mestre em esporte", 32, AMBER), anim="fade")
    HIST(c, t, [(0, "present"), (gt, "point_r")], [(0, "neutral"), (gt, "confident")], x=260)


def s12(c, t):  # 113.0 - 136.4  mais nove pessoas (apresentação do grupo)
    sky(c, t, 600, moon_xy=None)
    snowland(c, 900)
    show(c, t, 113.3, 1150, 110, T("com ele, mais nove", 44, AMBER), anim="fade")
    keys = [("Zinaida", 1), ("Lyudmila", 2), ("Doroshenko", 3), ("Krivonischenko", 4), ("Slobodin", 5), ("Nikolai", 6),
            ("Kolevatov", 7), ("Yudin", 9)]
    member(c, t, 0, 470, 960, 0.6, [(0, "present")], [(0, "happy")], appear=113.4)
    text(c, "Dyatlov", 470, 1010, 28, HAND, DARKTXT)
    for j, (w, i) in enumerate(keys):
        tt = tw(w, 115)
        x = 640 + j * 150
        member(c, t, i, x, 960, 0.6, [(0, "stand")], [(0, "happy")], appear=tt)
        nome = (YUDIN if i == 9 else GRUPO[i])[0]
        show(c, t, tt, x, 1010 + (j % 2) * 34, T(nome.split()[-1] if i != 6 else "Thibeaux", 28, DARKTXT, HAND), anim="fade")
    show(c, t, tw("Zinaida", 115), 1150, 300, lambda c: caption_box(c, "Zina (22) e Lyuda (20): as duas mulheres", 34), anim="up",
         t1=tw("Yuri", 122) - 0.2)
    show(c, t, tw("Yuri", 122), 1150, 300, lambda c: caption_box(c, "estudantes e engenheiros recém-formados", 34), anim="up",
         t1=tw("Yudin", 134) - 0.2)
    show(c, t, tw("Yudin", 134), 1150, 300, lambda c: caption_box(c, "Yuri Yudin, 21", 36), anim="up")
    snow(c, t, 40, 20, 0.3)
    HIST(c, t, [(0, "stand")], [(0, "neutral")], x=200, s=0.8)


def s13(c, t):  # 136.4 - 147.5  Semyon Zolotaryov, 38, veterano de guerra
    sky(c, t, 600, moon_xy=(1700, 170))
    snowland(c, 900)
    for k in range(4):
        member(c, t, k + 1, 1450 + k * 90, 960, 0.5, alpha=0.35)
    zt = tw("Semyon", 139.5)
    member(c, t, 8, 1100, 960, 1.05, [(0, "stand"), (zt + 2, "hips")], [(0, "neutral")], appear=137.0)
    if t > tw("veterano", 142.5):
        for k in range(2):
            circle(c, 1070 + k * 34, 720, 13, GOLD, 3)
    show(c, t, tw("homem", 136.6), 1100, 120, T("um homem que quase ninguém conhecia", 38, INK), anim="fade", t1=zt - 0.2)
    show(c, t, zt, 1100, 120, lambda c: hl(c, "SEMYON ZOLOTARYOV", 0, 0, 48), anim="up")
    show(c, t, tw("trinta", 141.5), 1500, 360, T("38 anos", 44, AMBER), anim="pop")
    show(c, t, tw("veterano", 142.5), 1500, 450, T("veterano da 2ª Guerra", 32, INK), anim="left")
    show(c, t, tw("instrutor", 144.8), 1500, 510, T("instrutor de turismo", 32, INK), anim="left")
    HIST(c, t, [(0, "think"), (zt, "point_r")], [(0, "think"), (zt, "neutral")], x=260)


def s14(c, t):  # 147.5 - 162.6  23 de janeiro: trem, Ivdel, caminhão até Vizhai; depois só esqui
    ural_map(c, t, 0.0 if t < 148 else 0.42 * prog(t, 148.4, 3.5) + 0.20 * prog(t, tw("caminhão", 153.5), 2.0), labels=True)
    show(c, t, 147.8, 1450, 140, lambda c: date_stamp(c, "23 DE JANEIRO", 44, RED), anim="stamp")
    tt = tw("trem", 150.8)
    show(c, t, tt - 0.2, 1500, 760, lambda c: steam_train(c, t, 1), s=0.6, anim="right", t1=tw("caminhão", 153.5) - 0.3)
    show(c, t, tw("caminhão", 153.5), 1500, 760, lambda c: old_truck(c, t), s=0.75, anim="right", t1=tw("Dali", 158) - 0.3)
    dt = tw("Dali", 158)
    show(c, t, dt, 1250, 640, lambda c: (skis(c), text(c, "esqui", 0, 220, 30, HAND, INK)), s=0.7, anim="pop")
    show(c, t, tw("mochilas", 160), 1520, 680, lambda c: backpack(c), s=0.8, anim="pop")
    show(c, t, tw("Vizhai", 154.5), 1150, 900, T("Vizhai: o último povoado antes da floresta", 30, INK), anim="fade", t1=dt - 0.2)
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=260)


def s15(c, t):  # 162.6 - 170.5  diários e fotos: grupo animado
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.05, 0.06)); c.fill()
    glow(c, 1100, 540, 760, LYELLOW, 0.07)
    def snap(i, j, pose, expr):
        def f(c):
            snowland(c, 9999)
            c.rectangle(-110, -100, 220, 200); rgb(c, (0.62, 0.64, 0.68)); c.fill()
            member(c, t, i, -40, 80, 0.38, [(0, pose)], [(0, expr)])
            member(c, t, j, 50, 80, 0.38, [(0, "wave")], [(0, "grin")])
        return f
    for k, (x, y, i, j, pose, ex) in enumerate(((780, 420, 1, 2, "arms_up", "happy"), (1120, 520, 3, 4, "thumb", "grin"),
                                                 (1460, 420, 5, 0, "present", "happy"))):
        show(c, t, 162.9 + k * 0.6, x, y, sc(photo, snap(i, j, pose, ex), 260, 300, ("rindo", "cantando", "na neve")[k], s=1.0),
             anim="drop", rot=(-0.06, 0.04, -0.03)[k])
    show(c, t, tw("diários", 162.8), 1120, 860, lambda c: caption_box(c, "diários e fotos: um grupo animado", 38), anim="up")
    HIST(c, t, [(0, "present")], [(0, "happy")], x=250)


def s16(c, t):  # 170.5 - 190.1  28 de janeiro: Yudin volta para casa; última pessoa a vê-los
    sky(c, t, 600, moon_xy=None)
    snowland(c, 880)
    forest(c, 880, 1600, 1960, 4, 2)
    put(c, 980, 880, lambda c: hut(c), 0.9, fade_in(t, tw("acampamento", 183)))
    show(c, t, 170.8, 1150, 130, lambda c: date_stamp(c, "28 DE JANEIRO", 46, RED), anim="stamp")
    dt = tw("despediu", 181.9)
    for k in range(9):
        x = 1320 + k * 60 + (max(0, t - dt - 2.5) * 40)
        member(c, t, k, x, 950, 0.48, [(0, "stand"), (dt, "wave"), (dt + 2.5, "stand")], [(0, "neutral"), (dt, "sad")], appear=171.0)
    yx = 1170 - max(0, t - dt - 1.5) * 60
    member(c, t, 9, yx, 950, 0.52, [(0, "stand"), (tw("dores", 176.5), "hold"), (dt, "wave")], [(0, "neutral"), (tw("dores", 176.5), "sad")], appear=171.0)
    show(c, t, tw("dores", 176.5), 1150, 260, lambda c: caption_box(c, "Yudin: dores fortes na perna", 36), anim="up", t1=dt - 0.2)
    show(c, t, dt, 1150, 260, lambda c: caption_box(c, "um acampamento abandonado de geólogos", 36), anim="up", t1=tw("Foi", 187) - 0.2)
    show(c, t, tw("Foi", 187), 1150, 260, lambda c: hl(c, "o último a vê-los com vida", 0, 0, 44), anim="up")
    snow(c, t, 60, 30, 0.4)
    fog(c, t, 900, 0.06)
    HIST(c, t, [(0, "present"), (tw("Foi", 187), "stand")], [(0, "neutral"), (tw("Foi", 187), "sad")], x=250, s=0.85)


def s17(c, t):  # 190.1 - 201.5  agora eram nove; rumo ao norte; "Montanha Morta"
    sky(c, t, 640)
    far_mountains(c, 890)
    snowland(c, 880)
    put(c, 1550, 760, lambda c: mountains(c, 700, 320, col=(0.26, 0.29, 0.36)), 1.0, fade_in(t, tw("montanha", 194.5)))
    show(c, t, 190.4, 1150, 130, lambda c: stitle(c, "AGORA ERAM NOVE", 0, 0, 64, INK, AMBER), anim="up", t1=tw("língua", 195.8))
    for k in range(9):
        x = 700 + k * 70 + (t - 190.1) * 22
        member(c, t, k, x, 950, 0.42, [(0, "stand")], [(0, "neutral")])
    show(c, t, tw("Montanha", 199), 1500, 380, lambda c: hl(c, "\"Montanha Morta\"", 0, 0, 46), anim="up")
    show(c, t, tw("mansi", 196.5), 1150, 130, T("na língua do povo mansi", 36, ICE), anim="fade")
    snow(c, t, 90, 60, 0.5)
    fog(c, t, 900, 0.07)
    HIST(c, t, [(0, "stand"), (199.0, "point_r")], [(0, "neutral"), (199.0, "worried")], x=250)


# ================================================================== BLOCO 2
def s18(c, t):  # 201.5 - 215.3  Kholat Syakhl: lugar sem caça
    sky(c, t, 600, moon_xy=(1700, 150))
    put(c, 1150, 900, lambda c: mountains(c, 1500, 480, col=(0.24, 0.27, 0.34)), 1.0)
    snowland(c, 900)
    show(c, t, 201.7, 1150, 140, lambda c: stitle(c, "KHOLAT SYAKHL", 0, 0, 80, INK, ICE), anim="fade", d=0.9)
    show(c, t, tw("Provavelmente", 203.5), 1150, 240, T("provavelmente: um lugar sem caça, onde nada cresce", 32, ICE), anim="fade",
         t1=tw("Mas", 208.5) - 0.2)
    mt = tw("Mas", 208.5)
    show(c, t, mt + 1.2, 1150, 240, lambda c: date_stamp(c, "1959", 48, RED), anim="stamp")
    snow(c, t, 140, 120, 0.7)
    fog(c, t, 880, 0.08)
    HIST(c, t, [(0, "present"), (mt, "think")], [(0, "neutral"), (mt, "worried")], x=260)


def s19(c, t):  # 215.3 - 235.4  31/jan borda da floresta, depósito; 1/fev subida; vento e visibilidade
    sky(c, t, 560, moon_xy=None)
    pt = tw("No", 226.4)  # "No dia seguinte"
    if t < pt:
        snowland(c, 880)
        forest(c, 880, 1350, 1960, 6, 5)
        show(c, t, 215.5, 1150, 130, lambda c: date_stamp(c, "31 DE JANEIRO", 46, RED), anim="stamp")
        show(c, t, tw("depósito", 222), 1050, 880, cache_platform, anim="up")
        show(c, t, tw("depósito", 222), 1080, 1010, T("depósito para a volta", 30, DARKTXT), anim="fade")
        for k in range(5):
            member(c, t, k, 560 + k * 80, 950, 0.45, [(0, "hold")], [(0, "neutral")], appear=216.0 + k * 0.1)
    else:
        slope(c)
        show(c, t, pt, 1150, 130, lambda c: date_stamp(c, "1º DE FEVEREIRO", 46, RED), anim="stamp")
        for k in range(9):
            x = 820 + k * 70 + (t - pt) * 26
            member(c, t, k, x, slope_y(x) + 4, 0.38, [(0, "stand")], [(0, "worried")])
        wt = tw("vento", 231)
        if t > wt:
            wind_lines(c, t, 14, 200, 900)
        show(c, t, tw("visibilidade", 233), 1150, 240, lambda c: caption_box(c, "vento forte, visibilidade baixa", 36), anim="up")
    snow(c, t, 260 if t > pt + 4 else 90, 240 if t > pt + 4 else 40, 0.85)
    fog(c, t, 900, 0.10 if t > pt + 4 else 0.06)
    HIST(c, t, [(0, "present")], [(0, "neutral"), (pt + 4, "worried")], x=250)


def s20(c, t):  # 235.4 - 259.7  a decisão: montar a barraca na encosta aberta; degrau na neve; ninguém sabe
    sky(c, t, 500, moon_xy=None)
    slope(c)
    forest(c, 900, -20, 620, 7, 3)
    tx = 1460
    show(c, t, 235.6, 1150, 120, lambda c: hl(c, "uma decisão até hoje discutida", 0, 0, 42), anim="up", t1=tw("Eles", 246) - 0.2)
    ft = tw("floresta", 240)
    if t > ft:
        arrow_draw(c, t, ft, 1350, slope_y(1350) - 120, 640, 720, 0.6, col=GREEN, lw=6)
        show(c, t, ft + 0.3, 880, 650, T("abrigo e lenha", 30, LGREEN), anim="fade")
    mt = tw("montar", 243)
    x0, x1 = tx - 250, tx + 250
    if t > tw("cavaram", 246.5):
        p = prog(t, tw("cavaram", 246.5), 1.0)
        poly(c, [(x0, slope_y(x0)), (x0 + (x1 - x0) * p, slope_y(x0)), (x0 + (x1 - x0) * p, slope_y(x0 + (x1 - x0) * p))])
        rgb(c, (0.52, 0.58, 0.68)); c.fill()
        show(c, t, tw("degrau", 248), 1600, 760, T("degrau cavado na neve", 30, DARKTXT), anim="fade")
    show(c, t, mt, tx, slope_y(x0) + 6, lambda c: dyatlov_tent(c, t), s=0.75, anim="drop")
    show(c, t, tw("Talvez", 252.8), 1150, 220, T("para não perder altura?", 36, ICE), anim="fade", t1=tw("Talvez", 255.5) - 0.1)
    show(c, t, tw("Talvez", 255.5), 1150, 220, T("para treinar no frio?", 36, ICE), anim="fade", t1=tw("Ninguém", 258) - 0.1)
    show(c, t, tw("Ninguém", 258), 1150, 220, lambda c: stitle(c, "Ninguém sabe.", 0, 0, 56, AMBER, AMBER), anim="up")
    snow(c, t, 120, 90, 0.6)
    fog(c, t, 900, 0.07)
    HIST(c, t, [(0, "think"), (ft, "point_l"), (mt, "point_r"), (252.8, "think")], [(0, "think")], x=240)


def s21(c, t):  # 259.7 - 279.0  últimas fotos; jornalzinho "O Vespertino Otorten"; homem das neves
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.05, 0.06)); c.fill()
    glow(c, 1100, 540, 700, LYELLOW, 0.08)
    jt = tw("jornalzinho", 265)
    def dig(c):
        c.rectangle(-110, -100, 220, 200); rgb(c, (0.70, 0.72, 0.76)); c.fill()
        circle(c, 80, -60, 20, (0.95, 0.80, 0.50), 0)
        member(c, t, 3, -30, 80, 0.36, [(0, "hold")], [(0, "neutral")])
        member(c, t, 5, 50, 80, 0.36, [(0, "point_r")], [(0, "happy")])
    show(c, t, 259.9, 1100, 520, sc(photo, dig, 300, 340, "cavando a neve, sol baixo", s=1.2), anim="drop", t1=jt - 0.3, rot=-0.04)
    def jornal(c):
        c.save(); c.rotate(-0.03)
        c.rectangle(-300, -230, 600, 460); fs(c, (0.86, 0.84, 0.76), 6)
        text(c, "O VESPERTINO OTORTEN", 0, -185, 36, SERIF, DARKTXT)
        line(c, -270, -155, 270, -155, 3, DARKTXT)
        text(c, "1º de fevereiro de 1959", 0, -128, 22, TYPE, DARKTXT)
        for i in range(6):
            line(c, -260, -80 + i * 34, 260, -80 + i * 34, 4, (0.52, 0.50, 0.44))
        c.restore()
    show(c, t, jt, 1100, 520, jornal, anim="drop")
    nt = tw("Numa", 270.5)
    if t > nt:
        show(c, t, nt + 0.6, 1100, 640, lambda c: hl(c, "\"o homem das neves existe\"", 0, 0, 40), anim="up")
        show(c, t, tw("Urais", 277.5), 1560, 820, big_footprint, s=0.8, anim="stamp")
    show(c, t, jt + 0.4, 1100, 900, T("um jornalzinho de brincadeira", 34, AMBER), anim="fade", t1=nt)
    HIST(c, t, [(0, "present"), (nt, "point_r")], [(0, "neutral"), (jt, "happy"), (277.5, "think")], x=250)


def s22(c, t):  # 279.0 - 281.9  foi o último registro
    c.rectangle(0, 0, W, H); rgb(c, (0.03, 0.03, 0.04)); c.fill()
    a = fade_out(t, 280.4, 1.4)
    glow(c, 1100, 540, 600, LYELLOW, 0.08 * a)
    put(c, 1100, 520, lambda c: (c.rotate(-0.03), c.rectangle(-300, -230, 600, 460), fs(c, (0.86, 0.84, 0.76), 6),
                                 text(c, "O VESPERTINO OTORTEN", 0, -185, 36, SERIF, DARKTXT)), 0.9, a)
    show(c, t, 279.2, 1100, 900, lambda c: hl(c, "o último registro", 0, 0, 46), anim="up")
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=250)


def s23(c, t):  # 281.9 - 299.9  o telegrama de 12 de fevereiro não chegou; famílias pressionam
    sky(c, t, 600, moon_xy=None)
    show(c, t, 282.1, 1100, 420, lambda c: telegram_form(c, ("VIZHAI ... 12 DE FEVEREIRO", "")), s=1.3, anim="drop")
    nt = tw("telegrama", 288.5)
    show(c, t, nt + 0.6, 1100, 420, lambda c: date_stamp(c, "NÃO CHEGOU", 56, RED), anim="stamp")
    show(c, t, tw("Atrasos", 292.5), 1100, 760, lambda c: caption_box(c, "atrasos eram comuns", 38), anim="up", t1=tw("Mas", 295.3) - 0.1)
    ft = tw("famílias", 297)
    if t > ft:
        for k in range(6):
            fig(c, t, 900 + k * 120, 1000, 0.45, [(0, "stand"), (ft + 0.6, "finger_up" if k % 2 else "hips")], [(0, "worried")],
                shirt=(0.40 + 0.06 * k, 0.36, 0.34), hair="long" if k % 2 else "tuft", fid=60 + k, appear=ft + k * 0.12)
        show(c, t, ft + 0.3, 1100, 760, lambda c: caption_box(c, "as famílias pressionam o instituto", 38), anim="up")
    HIST(c, t, [(0, "present"), (nt, "shrug")], [(0, "neutral"), (nt, "worried")], x=250)


def s24(c, t):  # 299.9 - 309.0  20 de fevereiro: começam as buscas
    sky(c, t, 500, moon_xy=None)
    snowland(c, 860)
    forest(c, 860, 1500, 1960, 5, 6)
    show(c, t, 300.1, 1150, 130, lambda c: date_stamp(c, "20 DE FEVEREIRO", 46, RED), anim="stamp")
    show(c, t, 300.3, 1150, 220, T("as buscas começam", 38, INK), anim="fade")
    vt = tw("voluntários", 302)
    for k in range(4):
        member(c, t, 0, 720 + k * 110, 960, 0.45, [(0, "stand")], [(0, "neutral")], appear=vt - 0.4 + k * 0.1,
               who=("x", (0.28 + 0.1 * k, 0.32, 0.40), False))
    st = tw("militares", 303)
    for k in range(2):
        fig(c, t, 1180 + k * 110, 960, 0.45, [(0, "stand")], [(0, "neutral")], appear=st + k * 0.1, fid=70 + k, **SOLDADO)
    at_ = tw("aviões", 304)
    if t > at_:
        x = 2100 - (t - at_) * 260
        put(c, x, 360, lambda c: airplane(c), 0.6)
    mt = tw("caçadores", 305)
    for k in range(2):
        fig(c, t, 1420 + k * 110, 960, 0.45, [(0, "stand")], [(0, "neutral")], appear=mt + k * 0.1, fid=80 + k,
            shirt=(0.50, 0.38, 0.26), hat="hood", hat_col=(0.56, 0.44, 0.30), hair=None)
    show(c, t, mt + 0.6, 1150, 680, lambda c: caption_box(c, "voluntários, militares, aviões e caçadores mansi", 34), anim="up")
    snow(c, t, 50, 20, 0.35)
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=250)


def s25(c, t):  # 309.0 - 323.5  26 de fevereiro: Sharavin avista a barraca; caída, com cortes
    sky(c, t, 450, moon_xy=None)
    slope(c)
    show(c, t, 309.2, 1150, 120, lambda c: date_stamp(c, "26 DE FEVEREIRO", 46, RED), anim="stamp")
    tx = 1480
    ct = tw("cortes", 320.5)
    put(c, tx, slope_y(tx) + 8, lambda c: dyatlov_tent(c, t, cut=1.0 if t > ct else 0.0, sag=0.7, snow_on=1.0), 0.95,
        fade_in(t, tw("barraca", 316.8)))
    fig(c, t, 860, slope_y(860) + 4, 0.55, [(0, "stand"), (tw("avistou", 312), "point_r")], [(0, "neutral"), (tw("avistou", 312), "shocked")],
        appear=309.6, shirt=(0.30, 0.40, 0.56), hat="beanie", hat_col=(0.30, 0.40, 0.56), hair=None, fid=90)
    show(c, t, tw("Mikhail", 311.5), 860, 520, T("Mikhail Sharavin", 30, INK, HAND), anim="fade")
    show(c, t, tw("barraca", 316.8), 1150, 220, lambda c: hl(c, "A BARRACA", 0, 0, 48), anim="up", t1=ct - 0.2)
    show(c, t, ct, 1150, 220, lambda c: hl(c, "cortes enormes num dos lados", 0, 0, 44), anim="up")
    snow(c, t, 80, 40, 0.5)
    fog(c, t, 900, 0.06)
    HIST(c, t, [(0, "present"), (ct, "point_r")], [(0, "neutral"), (ct, "shocked")], x=240, s=0.85)


def s26(c, t):  # 323.5 - 336.2  cortada por dentro; lá dentro estava quase tudo
    c.rectangle(0, 0, W, H); rgb(c, (0.04, 0.045, 0.06)); c.fill()
    snowland(c, 860, (0.62, 0.66, 0.74))
    put(c, 1150, 840, lambda c: dyatlov_tent(c, t, cut=1.0, sag=0.5), 1.25)
    show(c, t, 323.7, 1150, 130, lambda c: hl(c, "cortada POR DENTRO", 0, 0, 50), anim="up", t1=tw("Lá", 328.4) - 0.2)
    show(c, t, tw("Lá", 328.4), 1150, 130, T("lá dentro, quase tudo:", 42, AMBER), anim="fade")
    items = (("botas", 330.6, felt_boot, 0.55), ("casacos", 331.6, winter_coat, 0.55), ("comida", 332.6, None, 0.6),
             ("mochilas", 333.4, backpack, 0.55), ("lanternas", 334.6, None, 0.7))
    for k, (s, aft, fn, scl) in enumerate(items):
        tt = tw(s, aft - 0.4)
        x = 720 + k * 210
        if s == "comida":
            draw = lambda c: tin_can(c, "")
        elif s == "lanternas":
            draw = lambda c: lantern(c, t, 1.0, False)
        else:
            draw = fn
        show(c, t, tt, x, 380, lambda c, d=draw, scl=scl: (c.save(), c.scale(scl, scl), d(c), c.restore()), anim="pop")
        show(c, t, tt, x, 500, T(s, 28, INK, HAND), anim="fade")
    HIST(c, t, [(0, "point_r"), (328.6, "present")], [(0, "shocked"), (328.6, "worried")], x=230, s=0.85)


def s27(c, t):  # 336.2 - 352.5  pegadas de oito ou nove pessoas, em fila; meia, descalços, uma bota
    sky(c, t, 420, moon_xy=None)
    slope(c)
    tx = 1640
    put(c, tx, slope_y(tx) + 6, lambda c: dyatlov_tent(c, t, cut=1, sag=0.6, snow_on=1), 0.55)
    pt = tw("pegadas", 337)
    for r in range(8):
        c.save()
        x0 = 1500 + r * 14
        c.translate(x0, slope_y(x0) + 18 + r * 9)
        k = (slope_y(1000) - slope_y(1500)) / 500
        footprints(c, 9, -60, k * 60, t, pt + r * 0.15, (0.46, 0.52, 0.64))
        c.restore()
    show(c, t, tw("Oito", 337.5), 1100, 200, lambda c: caption_box(c, "8 ou 9 pessoas, lado a lado, em fila", 38), anim="up",
         t1=tw("Algumas", 344.5) - 0.2)
    for k, (w, s) in enumerate((("meia", "só de meia"), ("descalços", "descalços"), ("bota", "uma bota só"))):
        show(c, t, tw(w, 344), 900 + k * 330, 200, lambda c, s=s: hl(c, s, 0, 0, 36), anim="up")
    snow(c, t, 60, 30, 0.4)
    HIST(c, t, [(0, "present"), (pt, "point_r")], [(0, "worried")], x=240, s=0.85)


def s28(c, t):  # 352.5 - 365.0  passos normais, não de pânico; 500 m e depois somem
    sky(c, t, 420, moon_xy=None)
    slope(c)
    k = (slope_y(1000) - slope_y(1500)) / 500
    for r in range(6):
        c.save(); x0 = 1700 + r * 14; c.translate(x0, slope_y(x0) + 18 + r * 9)
        footprints(c, 14, -60, k * 60, None, 0, (0.46, 0.52, 0.64)); c.restore()
    st = tw("sumiam", 361.5)
    if t > st:
        a = clamp01((t - st) / 1.0)
        c.save(); c.rectangle(560, 0, 520, H); c.clip()
        slope(c); c.restore()
        _ = a
    show(c, t, 352.7, 1150, 160, lambda c: hl(c, "não parecia pânico", 0, 0, 44), anim="up", t1=tw("Pareciam", 355.5) - 0.1)
    show(c, t, tw("Pareciam", 355.5), 1150, 160, lambda c: hl(c, "passos normais", 0, 0, 44), anim="up", t1=tw("As", 357) - 0.1)
    qt = tw("quinhentos", 358.5)
    show(c, t, qt, 1350, 240, lambda c: caption_box(c, "~500 metros... e somem", 38), anim="up")
    if t > st:
        wind_lines(c, t, 10, 500, 900)
    snow(c, t, 140 if t > st else 60, 120 if t > st else 30, 0.6)
    fog(c, t, 900, 0.07)
    HIST(c, t, [(0, "think"), (qt, "point_r")], [(0, "think"), (qt, "worried")], x=240, s=0.85)


def s29(c, t):  # 365.0 - 384.8  o cedro a 1,5 km; restos de fogueira; Doroshenko e Krivonischenko
    sky(c, t, 500, moon_xy=(1700, 150))
    snowland(c, 900)
    forest(c, 900, 1350, 1960, 5, 8, (220, 320))
    show(c, t, 365.2, 1150, 120, lambda c: caption_box(c, "a 1,5 km da barraca, na beira da floresta", 38), anim="up",
         t1=tw("Embaixo", 375.5) - 0.2)
    ct = tw("pinheiro", 371)
    show(c, t, ct, 1000, 905, lambda c: cedar(c, 620), anim="up")
    show(c, t, tw("cedro", 373.5), 1000, 230, lambda c: hl(c, "o \"cedro\"", 0, 0, 44), anim="up", t1=tw("Embaixo", 375.5) - 0.2)
    ft = tw("fogueira", 377)
    show(c, t, ft - 0.4, 1220, 905, lambda c: campfire_out(c, t), anim="fade")
    show(c, t, ft, 1220, 990, T("restos de uma fogueira", 28, DARKTXT), anim="fade")
    nt = tw("Doroshenko", 380)
    show(c, t, nt, 1520, 860, lambda c: flag(c, RED, "Doroshenko"), anim="drop")
    show(c, t, tw("Krivonischenko", 381.5), 1660, 880, lambda c: flag(c, RED, "Krivonischenko"), anim="drop")
    show(c, t, tw("roupas", 383), 1150, 120, lambda c: hl(c, "só com roupas de baixo", 0, 0, 44), anim="up")
    snow(c, t, 50, 20, 0.35)
    fog(c, t, 930, 0.06)
    HIST(c, t, [(0, "present"), (nt, "point_r")], [(0, "neutral"), (nt, "sad")], x=250)


def s30(c, t):  # 384.8 - 393.8  galhos quebrados até 5 m: alguém subiu para olhar a barraca
    sky(c, t, 420, moon_xy=None)
    slope(c, 700, 960, 420)
    put(c, 1700, slope_y(1700, 700, 960, 420) + 6, lambda c: dyatlov_tent(c, t, cut=1, sag=0.5, snow_on=1), 0.45)
    put(c, 700, 965, lambda c: cedar(c, 720, prog(t, tw("galhos", 385), 1.5)), 1.0)
    show(c, t, tw("cinco", 385.5), 420, 620, lambda c: (line(c, 0, 0, 0, 340, 3, AMBER), text(c, "5 m", -50, 170, 34, TYPE, AMBER)),
         anim="fade")
    st = tw("subido", 389.5)
    if t > st:
        member(c, t, 3, 760, 640, 0.42, [(0, "point_r")], [(0, "worried")], appear=st)
    bt = tw("barraca", 392)
    if t > bt:
        line(c, 800, 520, 1650, slope_y(1650, 700, 960, 420) - 60, 3, AMBER)
        show(c, t, bt, 1250, 300, lambda c: caption_box(c, "para olhar a barraca?", 38), anim="up")
    snow(c, t, 50, 20, 0.35)
    HIST(c, t, [(0, "think")], [(0, "think")], x=230, s=0.8)


def s31(c, t):  # 393.8 - 410.7  entre o cedro e a barraca: Dyatlov, Kolmogorova, Slobodin; como se tentassem voltar
    sky(c, t, 420, moon_xy=None)
    slope(c)
    forest(c, 900, -20, 520, 6, 3)
    put(c, 560, 905, lambda c: cedar(c, 480), 1.0)
    tx = 1680
    put(c, tx, slope_y(tx) + 6, lambda c: dyatlov_tent(c, t, cut=1, sag=0.6, snow_on=1), 0.5)
    show(c, t, 394.0, 1150, 120, lambda c: caption_box(c, "entre o cedro e a barraca: mais três", 38), anim="up")
    for k, (w, nome, x) in enumerate((("Igor", "Dyatlov", 900), ("Zinaida", "Kolmogorova", 1130), ("Rustem", "Slobodin", 1360))):
        show(c, t, tw(w, 395), x, slope_y(x) + 10, lambda c, n=nome: flag(c, RED, n), anim="drop")
    show(c, t, tw("dias", 398.5), 1360, slope_y(1360) - 140, T("dias depois", 26, AMBER, HAND), anim="fade")
    vt = tw("virados", 405)
    if t > vt:
        for x in (900, 1130, 1360):
            arrow(c, x + 20, slope_y(x) - 110, x + 170, slope_y(x + 170) - 130, AMBER, 4, 0.05, 18)
    show(c, t, tw("Como", 408), 1150, 220, lambda c: hl(c, "como se tentassem voltar", 0, 0, 44), anim="up")
    snow(c, t, 50, 20, 0.35)
    HIST(c, t, [(0, "present"), (vt, "point_r")], [(0, "sad")], x=240, s=0.85)


def s32(c, t):  # 410.7 - 422.7  hipotermia; faltavam quatro; a neve guardaria a resposta
    sky(c, t, 600, moon_xy=(1700, 150))
    snowland(c, 900)
    show(c, t, 410.9, 1050, 430, sc(thermometer, "hipotermia", 0.06, s=1.2), anim="pop", t1=tw("Mas", 415) - 0.2)
    ft = tw("faltavam", 414)
    if t > ft:
        for k in range(4):
            x = 900 + k * 190
            faded(c, 0.35 + 0.15 * math.sin(t * 2 + k), lambda c, x=x: figure(c, t, x, 960, 0.7, poses=[(0, "stand")],
                  exprs=[(0, "neutral")], shirt=(0.5, 0.55, 0.62), hat="beanie", hat_col=(0.5, 0.55, 0.62), hair=None, fid=100 + k))
            show(c, t, ft + k * 0.2, x, 560, T("?", 60, AMBER, SERIF), anim="pop")
        show(c, t, ft + 0.3, 1180, 220, lambda c: hl(c, "faltavam quatro", 0, 0, 48), anim="up")
    show(c, t, tw("dois", 419), 1180, 320, T("mais dois meses sob a neve", 36, ICE), anim="fade")
    snow(c, t, 120, 60, 0.6)
    HIST(c, t, [(0, "present"), (ft, "think")], [(0, "sad"), (ft, "worried")], x=250)


# ================================================================== BLOCO 3
def s33(c, t):  # 422.7 - 434.0  março e abril: varas compridas na neve
    sky(c, t, 500, moon_xy=None)
    snowland(c, 820)
    forest(c, 820, 1500, 1960, 5, 11)
    show(c, t, 423.0, 1150, 130, lambda c: date_stamp(c, "MARÇO E ABRIL", 46, RED), anim="stamp")
    vt = tw("varas", 426.5)
    for k in range(5):
        x = 700 + k * 170
        if t > vt + k * 0.2:
            d = 40 + 30 * abs(math.sin(t * 1.4 + k))
            put(c, x + 50, 900 + d, lambda c: probe_pole(c, 300), 1.0)
            member(c, t, 0, x, 930, 0.45, [(0, "hold")], [(0, "neutral")], who=("x", (0.30 + 0.08 * k, 0.34, 0.42), False))
    show(c, t, tw("metro", 428.5), 1150, 240, T("metro por metro", 38, ICE), anim="fade")
    snow(c, t, 60, 30, 0.4)
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=250)


def s34(c, t):  # 434.0 - 454.9  4 de maio: a ravina, 75 m do cedro, 4 m de neve; os quatro nomes
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.06, 0.08)); c.fill()
    # corte da ravina: camadas de neve sobre o riacho
    c.move_to(560, 300); c.line_to(900, 300); c.curve_to(980, 520, 1040, 760, 1080, 900); c.line_to(1400, 900)
    c.curve_to(1440, 760, 1500, 520, 1580, 300); c.line_to(1860, 300); c.line_to(1860, 1040); c.line_to(560, 1040); c.close_path()
    rgb(c, (0.28, 0.24, 0.20)); c.fill()
    snt = tw("debaixo", 444)
    a = fade_in(t, snt, 1.0)
    if a > 0:
        c.move_to(910, 300); c.curve_to(985, 520, 1045, 760, 1085, 880); c.line_to(1395, 880); c.curve_to(1440, 760, 1495, 520, 1570, 300)
        c.close_path(); rgb(c, (0.84, 0.88, 0.94), 0.9 * a); c.fill()
        show(c, t, snt, 1700, 600, lambda c: (line(c, 0, -300, 0, 280, 4, AMBER), text(c, "~4 m", 70, 0, 40, TYPE, AMBER)), anim="fade")
    c.rectangle(1080, 880, 320, 40); rgb(c, (0.20, 0.32, 0.42)); c.fill()
    put(c, 700, 300, lambda c: cedar(c, 260), 1.0)
    show(c, t, 434.2, 1400, 110, lambda c: date_stamp(c, "4 DE MAIO", 46, RED), anim="stamp")
    show(c, t, tw("setenta", 442), 960, 250, T("75 m do cedro", 30, INK), anim="fade")
    ns = [("Lyudmila", "Dubinina"), ("Semyon", "Zolotaryov"), ("Alexander", "Kolevatov"), ("Nikolai", "Thibeaux-Brignolle")]
    for k, (w, n) in enumerate(ns):
        show(c, t, tw(w, 446), 1140 + k * 70, 870, lambda c: flag(c, AMBER), anim="drop")
    if t > tw("Lyudmila", 446):
        for k, (w, n) in enumerate(ns):
            show(c, t, tw(w, 446), 860 + k * 300 if k < 3 else 1760, 1010 if k < 3 else 1010, T(n, 28, INK, HAND), anim="fade")
    HIST(c, t, [(0, "present"), (446.5, "point_r")], [(0, "sad")], x=240, s=0.85)


def s35(c, t):  # 454.9 - 471.0  mais vestidos; roupas dos rapazes do cedro, cortadas com faca
    sky(c, t, 500, moon_xy=None)
    snowland(c, 900)
    show(c, t, 455.1, 1150, 120, lambda c: caption_box(c, "os quatro estavam mais vestidos", 38), anim="up", t1=tw("Parecia", 463.5) - 0.2)
    pt = tw("peças", 457.5)
    show(c, t, pt, 900, 450, sc(winter_coat, (0.32, 0.56, 0.40), s=0.9), anim="pop")
    show(c, t, pt + 0.4, 1150, 470, sc(winter_coat, (0.30, 0.46, 0.66), s=0.9), anim="pop")
    show(c, t, tw("cortadas", 461.5), 1430, 450, sc(knife, s=1.0), anim="left")
    show(c, t, tw("rapazes", 459.5), 1050, 650, T("roupas dos dois rapazes do cedro", 32, INK), anim="fade", t1=tw("Parecia", 463.5) - 0.2)
    rt = tw("Parecia", 463.5)
    if t > rt:
        put(c, 1700, 905, lambda c: cedar(c, 420), 1.0, fade_in(t, rt))
        show(c, t, rt + 0.3, 1000, 760, lambda c: caption_box(c, "voltaram à árvore para tentar sobreviver?", 36), anim="up")
    snow(c, t, 50, 20, 0.35)
    HIST(c, t, [(0, "present"), (rt, "think")], [(0, "sad")], x=250)


def s36(c, t):  # 471.0 - 485.6  autópsia: crânio, costelas, acidente de carro
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.05, 0.06)); c.fill()
    glow(c, 1100, 520, 700, LYELLOW, 0.07)
    put(c, 1100, 520, lambda c: soviet_doc(c, "LAUDO DA AUTÓPSIA", 0, 760, 700), 1.0, fade_in(t, 471.2))
    rows = (("Thibeaux-Brignolle", "fratura grave no crânio", tw("Thibeaux", 473)),
            ("Dubinina e Zolotaryov", "várias costelas quebradas", tw("Dubinina", 477)))
    for k, (n, s, tt) in enumerate(rows):
        typewrite(c, t, tt, n, 760, 320 + k * 110, 34, DARKTXT, 26, align="l")
        typewrite(c, t, tt + 0.8, s, 760, 360 + k * 110, 30, BLOOD, 26, align="l")
    ct = tw("acidente", 481)
    show(c, t, ct, 1100, 690, lambda c: (car(c, (0.50, 0.52, 0.56)), text(c, "força de um acidente de carro", 0, 130, 32, TYPE, DARKTXT)),
         s=0.85, anim="pop")
    HIST(c, t, [(0, "present"), (ct, "shrug")], [(0, "neutral"), (ct, "shocked")], x=250)


def s36b(c, t):  # 485.6 - 498.9  quase sem ferimentos por fora; uma pressão enorme
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.05, 0.06)); c.fill()
    show(c, t, 485.8, 1150, 130, lambda c: hl(c, "um detalhe que ninguém explicava", 0, 0, 42), anim="up", t1=tw("quase", 488.5) - 0.2)
    qt = tw("quase", 488.5)
    if t > qt:
        fig(c, t, 1150, 960, 1.0, [(0, "stand")], [(0, "neutral")], shirt=(0.55, 0.58, 0.64), hair=None, fid=110, alpha=0.55)
        show(c, t, qt, 1150, 130, lambda c: hl(c, "quase nenhum ferimento por fora", 0, 0, 44), anim="up")
    pt = tw("pressão", 491.5)
    if t > pt:
        p = prog(t, pt, 1.2)
        for k in range(-3, 4):
            x = 1150 + k * 90
            arrow(c, x, 220 + 60 * p, x, 330 + 80 * p, ICE, 6, 0.0, 24)
        show(c, t, pt + 0.4, 1150, 1030, T("uma pressão enorme... sem deixar marca", 34, ICE), anim="fade")
    HIST(c, t, [(0, "think")], [(0, "think"), (pt, "worried")], x=250)


def s37(c, t):  # 498.9 - 513.8  danos do tempo, água e animais; versões assustadoras
    sky(c, t, 500, moon_xy=None)
    snowland(c, 760, (0.70, 0.74, 0.82))
    c.rectangle(0, 900, W, 60); rgb(c, (0.20, 0.32, 0.42)); c.fill()
    show(c, t, 499.1, 1150, 120, T("o tempo, a água do riacho sob a neve, os animais", 34, ICE), anim="fade", t1=tw("Mas", 506.2) - 0.2)
    vt = tw("versões", 508)
    for k in range(4):
        show(c, t, vt - 1.2 + k * 0.45, 820 + k * 250, 520 + (k % 2) * 60,
             lambda c, k=k: newspaper(c, ("MISTÉRIO", "TERROR", "SEGREDO", "MONSTRO?")[k], "Urais, 1959"), s=0.8, anim="drop",
             rot=(-0.08, 0.05, -0.03, 0.07)[k])
    show(c, t, tw("contadas", 510), 1150, 900, lambda c: caption_box(c, "versões cada vez mais assustadoras", 38), anim="up")
    HIST(c, t, [(0, "present"), (vt, "shrug")], [(0, "neutral"), (vt, "worried")], x=250)


def s38(c, t):  # 513.8 - 537.9  radioatividade nas roupas; complexo nuclear secreto; ninguém provou
    c.rectangle(0, 0, W, H); rgb(c, (0.04, 0.05, 0.05)); c.fill()
    show(c, t, 514.0, 1150, 130, lambda c: stitle(c, "E havia mais.", 0, 0, 60, AMBER, AMBER), anim="up", t1=tw("Algumas", 515) - 0.1)
    gt = tw("radioatividade", 519)
    show(c, t, tw("Algumas", 515), 900, 520, sc(winter_coat, (0.50, 0.38, 0.64), s=1.1), anim="pop", t1=tw("Segundo", 525) - 0.2)
    show(c, t, gt - 1.0, 1350, 540, lambda c: geiger(c, t, 0.15 + 0.4 * prog(t, gt, 1.5)), anim="pop", t1=tw("Segundo", 525) - 0.2)
    show(c, t, gt, 1150, 130, lambda c: hl(c, "traços de radioatividade", 0, 0, 46), anim="up", t1=tw("Segundo", 525) - 0.2)
    show(c, t, tw("dose", 522), 1150, 860, lambda c: caption_box(c, "não era dose mortal, mas acima do normal", 36), anim="up",
         t1=tw("Segundo", 525) - 0.2)
    st = tw("Segundo", 525)
    if t > st:
        put(c, 1150, 760, lambda c: factory(c, t, 600, 240), 1.0, fade_in(t, st + 1.2))
        show(c, t, st, 1150, 130, lambda c: hl(c, "segundo vários relatos", 0, 0, 40), anim="up", t1=tw("acidente", 530) - 0.2)
        show(c, t, tw("Krivonischenko", 526), 1150, 230, T("Krivonischenko trabalhou num complexo nuclear secreto", 32, INK), anim="fade")
        show(c, t, tw("acidente", 530), 1150, 130, lambda c: date_stamp(c, "ACIDENTE EM 1957", 44, RED), anim="stamp")
        show(c, t, tw("radiação", 535.5), 1600, 420, sc(radiation_sign, 80), anim="pop")
        show(c, t, tw("Ninguém", 534), 1150, 960, lambda c: caption_box(c, "ninguém provou como a radiação foi parar ali", 36), anim="up")
    HIST(c, t, [(0, "present"), (gt, "point_r"), (st, "think")], [(0, "neutral"), (gt, "shocked"), (st, "think")], x=240, s=0.85)


def s39(c, t):  # 537.9 - 556.5  esferas de luz alaranjada no céu; relatos fora da conclusão
    sky(c, t, 700, moon_xy=None)
    far_mountains(c, 905)
    snowland(c, 900)
    et = tw("esferas", 545)
    if t > et:
        for k, (x, y, r) in enumerate(((1250, 260, 36), (1450, 200, 26), (1620, 300, 20))):
            put(c, x + math.sin(t * 0.5 + k) * 14, y - prog(t, et + k * 0.4, 6) * 60, lambda c, r=r: orange_orb(c, t, r), 1.0,
                fade_in(t, et + k * 0.4, 1.2))
    gt = tw("Outro", 540)
    for k in range(4):
        member(c, t, 0, 900 + k * 110, 960, 0.48, [(0, "stand"), (et + 0.3, "point_ru" if k == 1 else "stand")], [(0, "neutral"), (et, "shocked")],
               appear=gt + k * 0.1, who=("x", (0.36, 0.40 + 0.05 * k, 0.48), False))
    show(c, t, gt, 1100, 620, T("outro grupo, ~50 km ao sul", 32, INK), anim="fade", t1=tw("Esses", 551) - 0.2)
    show(c, t, tw("Nas", 547.5), 1100, 690, T("depois: moradores e até militares", 30, ICE), anim="fade", t1=tw("Esses", 551) - 0.2)
    show(c, t, tw("Esses", 551), 1100, 660, lambda c: caption_box(c, "não entraram na conclusão oficial", 38), anim="up")
    HIST(c, t, [(0, "present"), (et, "point_ru")], [(0, "neutral"), (et, "shocked")], x=250)


def s40(c, t):  # 556.5 - 579.7  Lev Ivanov; maio de 1959: caso encerrado; força natural irresistível; lacrado
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.05, 0.06)); c.fill()
    glow(c, 1150, 540, 700, LYELLOW, 0.07)
    lt = tw("Lev", 558.5)
    mt = tw("maio", 559.8)
    if t < mt + 1.5:
        fig(c, t, 1150, 960, 1.0, [(0, "stand")], [(0, "neutral")], appear=556.8, fid=120, **IVANOV)
        show(c, t, lt, 1150, 130, lambda c: hl(c, "LEV IVANOV, investigador", 0, 0, 44), anim="up", t1=mt)
    else:
        a = fade_out(t, tw("arquivos", 573) + 0.3, 0.5)
        put(c, 1150, 520, lambda c: soviet_doc(c, "CASO ENCERRADO", 5, 620, 660), 1.0, a)
        if a > 0:
            typewrite(c, t, tw("culpados", 562.5), "sem culpados", 1150, 380, 38, DARKTXT, 16)
            typewrite(c, t, tw("força", 568), "força natural irresistível", 1150, 470, 38, BLOOD, 18)
        show(c, t, tw("arquivos", 573), 1150, 520, lambda c: folder(c, "LACRADO", True), s=1.6, anim="drop")
        show(c, t, tw("região", 575), 1150, 920, lambda c: caption_box(c, "região fechada a excursionistas por alguns anos", 34), anim="up")
    show(c, t, mt, 1150, 120, lambda c: date_stamp(c, "MAIO DE 1959", 44, RED), anim="stamp")
    HIST(c, t, [(0, "present"), (mt + 2, "think")], [(0, "neutral"), (mt + 2, "worried")], x=250)


def s41(c, t):  # 579.7 - 598.9  fim dos anos 80: documentos aparecem; 1990: o artigo de Ivanov
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.05, 0.06)); c.fill()
    at_ = tw("Em", 585.5)
    if t < at_:
        show(c, t, 579.9, 1150, 130, lambda c: date_stamp(c, "FIM DOS ANOS 80", 44, RED), anim="stamp")
        for k in range(3):
            show(c, t, tw("documentos", 583) - 0.6 + k * 0.4, 860 + k * 300, 560, lambda c, k=k: soviet_doc(c, ("PROCESSO", "FOTOS", "DEPOIMENTOS")[k], 6, 300, 400),
                 anim="drop", rot=(-0.06, 0.03, 0.07)[k])
    else:
        show(c, t, at_, 1150, 130, lambda c: date_stamp(c, "1990", 50, RED), anim="stamp")
        show(c, t, tw("artigo", 588), 1150, 520, lambda c: newspaper(c, "DYATLOV", "por Lev Ivanov"), s=1.4, anim="drop")
        show(c, t, tw("ordens", 590.5), 1150, 860, lambda c: hl(c, "\"recebi ordens para não investigar as luzes\"", 0, 0, 36), anim="up")
        show(c, t, tw("aumentou", 595), 1650, 420, sc(big_q, 120, AMBER), anim="pop")
    HIST(c, t, [(0, "present"), (at_, "point_r")], [(0, "neutral"), (at_, "shocked")], x=240, s=0.85)


def s42(c, t):  # 598.9 - 611.5  hoje: Passo Dyatlov; muitas teorias
    sky(c, t, 640)
    put(c, 1150, 900, lambda c: mountains(c, 1700, 420, col=(0.24, 0.27, 0.34)), 1.0)
    snowland(c, 900)
    pt = tw("Passo", 600.5)
    def placa(c):
        line(c, 0, 0, 0, -220, 10, (0.40, 0.30, 0.20))
        rrect(c, -230, -320, 460, 110, 8); fs(c, (0.32, 0.26, 0.18), 5)
        text(c, "PASSO DYATLOV", 0, -265, 46, SERIF, INK)
    show(c, t, pt, 1150, 940, placa, anim="up")
    show(c, t, tw("homenagem", 602), 1150, 520, T("em homenagem ao líder do grupo", 32, ICE), anim="fade")
    tt = tw("teorias", 609)
    show(c, t, tt - 0.5, 1150, 200, lambda c: stitle(c, "MUITAS TEORIAS", 0, 0, 64, AMBER, AMBER), anim="up")
    snow(c, t, 100, 60, 0.5)
    fog(c, t, 900, 0.08)
    HIST(c, t, [(0, "present"), (tt, "think")], [(0, "neutral"), (tt, "think")], x=250)


def s43(c, t):  # 611.5 - 629.1  teoria 1: o povo mansi — descartada pela própria investigação
    sky(c, t, 500, moon_xy=None)
    show(c, t, 611.7, 900, 520, lambda c: theory_card(c, "1", "OS MANSI", lambda c: (c.scale(0.6, 0.6), footprints(c, 5, 50, -10)),
                                                    crossed=prog(t, tw("descartou", 618.5), 0.4)), anim="up")
    rows = (("outras", "nenhuma outra pegada além das do grupo"), ("sinal", "nenhum sinal de luta"), ("ajudado", "os mansi ajudaram nas buscas"))
    for k, (w, s) in enumerate(rows):
        show(c, t, tw(w, 620), 1420, 400 + k * 110, T(s, 30, INK), anim="left")
    show(c, t, tw("descartou", 618.5), 900, 840, lambda c: date_stamp(c, "DESCARTADA", 40, RED), anim="stamp")
    HIST(c, t, [(0, "present"), (618.6, "shrug")], [(0, "neutral")], x=250)


def s44(c, t):  # 629.1 - 649.0  teoria 2: militar — míssil, explosão, arma secreta; nunca houve prova
    sky(c, t, 700, moon_xy=None)
    far_mountains(c, 925)
    snowland(c, 920)
    show(c, t, 629.3, 1150, 110, lambda c: tag_header(c, "2", "MILITAR"), anim="up")
    mt = tw("míssil", 636)
    if t > mt - 0.5:
        p = prog(t, mt - 0.5, 4.0)
        put(c, 1350, 820 - p * 560, lambda c: rocket(c, t), 0.6)
    show(c, t, tw("explosão", 637), 950, 420, lambda c: (glow(c, 0, 0, 300, ORANGE, 0.35), circle(c, 0, 0, 60, (1.0, 0.8, 0.5), 0)), anim="pop",
         t1=tw("Isso", 639.5))
    show(c, t, tw("arma", 638.2), 1600, 420, lambda c: parachute(c, t), s=0.6, anim="drop", t1=tw("Isso", 639.5))
    it = tw("Isso", 639.5)
    for k, s in enumerate(("as luzes", "a radiação", "o segredo")):
        show(c, t, it + 0.4 + k * 0.7, 900 + k * 330, 620, lambda c, s=s: hl(c, s, 0, 0, 38), anim="up", t1=tw("Mas", 643.9))
    nt = tw("nunca", 643)
    show(c, t, nt, 1150, 620, lambda c: date_stamp(c, "NENHUMA PROVA", 50, RED), anim="stamp")
    HIST(c, t, [(0, "present"), (it, "think"), (nt, "shrug")], [(0, "neutral"), (nt, "neutral")], x=240, s=0.85)


# ================================================================== BLOCO 4
def s45(c, t):  # 649.0 - 664.6  teoria 3: infrassom
    sky(c, t, 600, moon_xy=None)
    put(c, 1250, 900, lambda c: mountains(c, 1400, 420, col=(0.24, 0.27, 0.34)), 1.0)
    snowland(c, 900)
    show(c, t, 649.2, 1150, 110, lambda c: tag_header(c, "3", "INFRASSOM"), anim="up")
    st = tw("som", 651.5)
    if t > st:
        for k in range(5):
            r = ((t - st) * 120 + k * 120) % 600
            c.new_sub_path(); c.arc(1250, 560, r, math.pi * 1.05, math.pi * 1.95)
            rgb(c, ICE, 0.35 * (1 - r / 600)); c.set_line_width(4); c.stroke()
    show(c, t, tw("ninguém", 652.5), 1150, 250, T("um som grave demais para ouvir", 34, ICE), anim="fade")
    show(c, t, tw("medo", 657.5), 1150, 320, T("medo e pânico sem motivo?", 34, INK), anim="fade")
    show(c, t, tw("difícil", 662), 1150, 1000, lambda c: date_stamp(c, "DIFÍCIL DE PROVAR", 40, RED), anim="stamp")
    HIST(c, t, [(0, "present"), (st, "think")], [(0, "neutral"), (st, "think")], x=250)


def s46(c, t):  # 664.6 - 678.8  as teorias mais estranhas: homem das neves; discos voadores
    sky(c, t, 700, moon_xy=(1700, 140))
    snowland(c, 900)
    show(c, t, 664.8, 1150, 110, T("as teorias mais estranhas", 40, AMBER), anim="fade")
    yt = tw("homem", 668.5)
    show(c, t, yt, 900, 700, big_footprint, s=1.2, anim="stamp")
    show(c, t, yt, 900, 920, T("homem das neves", 32, DARKTXT), anim="fade")
    show(c, t, tw("piada", 670), 900, 360, T("(a piada do jornalzinho)", 28, ICE, HAND), anim="fade")
    ut = tw("discos", 676.5)
    show(c, t, tw("esferas", 673.5), 1500, 400, lambda c: orange_orb(c, t, 30), anim="fade", t1=ut)
    show(c, t, ut, 1500, 400, lambda c: ufo_disc(c, t), s=0.9, anim="pop")
    show(c, t, ut + 0.3, 1500, 560, T("discos voadores?", 32, INK), anim="fade")
    HIST(c, t, [(0, "shrug"), (yt, "point_r")], [(0, "neutral"), (yt, "think")], x=250)


def s47(c, t):  # 678.8 - 700.4  a explicação mais simples: avalanche — e seus problemas
    sky(c, t, 420, moon_xy=None)
    slope(c)
    tx = 1500
    put(c, tx, slope_y(tx) + 6, lambda c: dyatlov_tent(c, t, cut=1, sag=0.4), 0.7)
    show(c, t, 679.0, 1150, 110, lambda c: tag_header(c, "4", "AVALANCHE"), anim="up")
    mt = tw("massa", 682)
    if mt < t < mt + 4.5:
        p = prog(t, mt, 2.5)
        c.move_to(W, 200 + 260 * p)
        for x in range(W, 1100, -60):
            c.line_to(x, slope_y(x) - 140 * (1 - abs(x - (W - 500 * p)) / 600) - 20)
        c.line_to(1100, slope_y(1100)); c.line_to(W, slope_y(W)); c.close_path()
        rgb(c, (0.94, 0.96, 1.0), 0.75 * fade_out(t, mt + 3.5, 1.0)); c.fill()
    pt = tw("problemas", 686.5)
    rows = (("encosta", "encosta pouco inclinada"), ("sinais", "sem sinais claros de avalanche"), ("barraca", "barraca ainda em pé, em parte"),
            ("pegadas", "pegadas intactas semanas depois"))
    for k, (w, s) in enumerate(rows):
        tt = tw(w, 688 if k == 0 else 689)
        show(c, t, tt, 900, 300 + k * 80, lambda c, s=s: caption_box(c, s, 32), anim="left")
    show(c, t, pt, 1150, 200, T("mas ela tinha problemas sérios", 32, AMBER), anim="fade")
    HIST(c, t, [(0, "present"), (pt, "shrug")], [(0, "neutral"), (pt, "think")], x=240, s=0.85)


def s48(c, t):  # 700.4 - 724.7  2019: caso reaberto; julho de 2020: promotor Kuryakov — avalanche; famílias não aceitam
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.05, 0.06)); c.fill()
    glow(c, 1150, 540, 700, LYELLOW, 0.07)
    show(c, t, 700.6, 1150, 120, lambda c: date_stamp(c, "2019: CASO REABERTO", 44, RED), anim="stamp", t1=tw("julho", 706) - 0.2)
    show(c, t, 700.8, 1150, 520, lambda c: folder(c, "REABERTO", True), s=1.3, anim="drop", t1=tw("julho", 706) - 0.2)
    jt = tw("julho", 706)
    if t > jt:
        show(c, t, jt, 1150, 120, lambda c: date_stamp(c, "JULHO DE 2020", 44, RED), anim="stamp")
        fig(c, t, 1500, 980, 0.9, [(0, "stand"), (tw("anunciou", 709.5), "present")], [(0, "confident")], appear=jt + 0.2, fid=130, **PROMOTOR)
        show(c, t, tw("Andrei", 708.5), 1500, 560, T("promotor Andrei Kuryakov", 30, INK, HAND), anim="fade")
        show(c, t, tw("pequena", 712.5), 980, 380, lambda c: caption_box(c, "uma pequena avalanche", 36), anim="left")
        show(c, t, tw("fugiu", 715), 980, 470, lambda c: caption_box(c, "fuga para a floresta, sem enxergar", 34), anim="left")
        show(c, t, tw("morreu", 718.5), 980, 560, lambda c: caption_box(c, "mortes pelo frio", 34), anim="left")
        show(c, t, tw("Parte", 721.2), 980, 760, lambda c: hl(c, "parte das famílias não aceitou", 0, 0, 38), anim="up")
    HIST(c, t, [(0, "present")], [(0, "neutral"), (tw("Parte", 721.2), "sad")], x=240, s=0.85)


def s49(c, t):  # 724.7 - 747.1  Gaume (EPFL) e Puzrin (ETH Zurique); o filme Frozen
    sky(c, t, 600, moon_xy=None)
    show(c, t, 724.9, 1150, 110, T("alguns meses depois, um reforço inesperado", 36, AMBER), anim="fade", t1=tw("Dois", 729.5) - 0.2)
    gt = tw("Johan", 730.5)
    fig(c, t, 950, 980, 0.85, [(0, "stand"), (gt + 1, "present")], [(0, "happy")], appear=gt - 0.2, fid=140, **CIENTISTA)
    pz = tw("Puzrin", 734.5)
    fig(c, t, 1400, 980, 0.85, [(0, "stand"), (pz + 1, "think")], [(0, "neutral")], appear=pz - 0.6, fid=141, **CIENTISTA2)
    show(c, t, gt, 950, 520, T("Johan Gaume", 32, INK, HAND), anim="fade")
    show(c, t, tw("Lausanne", 732.5), 950, 570, T("EPFL, Lausanne (Suíça)", 26, ICE), anim="fade")
    show(c, t, pz, 1400, 520, T("Alexander Puzrin", 32, INK, HAND), anim="fade")
    show(c, t, tw("Zurique", 737.5), 1400, 570, T("ETH Zurique", 26, ICE), anim="fade")
    show(c, t, tw("estudo", 739), 1150, 200, lambda c: hl(c, "um estudo sobre o caso (2021)", 0, 0, 40), anim="up", t1=tw("Frozen", 744.5) - 0.2)
    ft = tw("Frozen", 744.5)
    show(c, t, ft, 1150, 200, lambda c: (glow(c, 0, 0, 260, ICE, 0.25), stitle(c, "FROZEN", 0, 0, 80, ICE, ICE),
                                        text(c, "o filme da Disney", 0, 64, 28, TYPE, INK)), anim="pop")
    snow(c, t, 60, 10, 0.5)
    HIST(c, t, [(0, "present"), (ft, "point_r")], [(0, "neutral"), (ft, "shocked")], x=240, s=0.8)


def s49b(c, t):  # 747.1 - 760.5  o programa que simulava a neve; bloco de neve x corpo
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.05, 0.07)); c.fill()
    def tela(c):
        rnd = random.Random(int(t * 10))
        for k in range(160):
            x = rnd.uniform(-300, 300); y = (rnd.uniform(-200, 200) + t * 80) % 400 - 200
            circle(c, x, y, rnd.uniform(1.5, 4), (0.90, 0.94, 1.0), 0)
        for gx in range(-300, 301, 60):
            line(c, gx, -200, gx, 200, 1, (0.20, 0.40, 0.50))
    put(c, 1150, 480, lambda c: monitor(c, tela, 720, 460), 1.0, fade_in(t, 747.3))
    show(c, t, tw("impressionado", 749), 1150, 130, T("Gaume ficou impressionado com a neve da animação", 34, INK), anim="fade",
         t1=tw("Ele", 751.5) - 0.2)
    show(c, t, tw("criadores", 752.5), 1150, 130, T("procurou os criadores do programa", 34, INK), anim="fade", t1=tw("calcular", 756.5) - 0.2)
    ct = tw("calcular", 756.5)
    if t > ct:
        put(c, 1050, 420 + 120 * prog(t, ct + 0.5, 1.0), lambda c: snow_slab(c, 260, 70), 1.0)
        fig(c, t, 1260, 650, 0.45, [(0, "stand")], [(0, "worried")], shirt=(0.5, 0.55, 0.62), hair=None, fid=150)
        show(c, t, ct, 1150, 130, lambda c: hl(c, "o que um bloco de neve faz com um corpo?", 0, 0, 38), anim="up")
    HIST(c, t, [(0, "present"), (ct, "think")], [(0, "neutral"), (ct, "think")], x=240, s=0.85)


def slope_section(c, t, cut=0.0, pile=0.0, slab=0.0, slab_fall=0.0, crack=0.0):
    """corte da encosta (28°) com a barraca no degrau cavado"""
    x0, y0, x1, y1 = 560, 1000, 1880, 320
    k = (y0 - y1) / (x1 - x0)
    def sy(x):
        return y0 - (x - x0) * k
    tx = 1180
    c.move_to(x0, y0); c.line_to(x1, y1); c.line_to(x1, H); c.line_to(x0, H); c.close_path()
    rgb(c, (0.78, 0.82, 0.90)); c.fill()
    line(c, x0, y0, x1, y1, 4, (0.60, 0.66, 0.76))
    if cut > 0:
        poly(c, [(tx - 160, sy(tx - 160)), (tx + 160, sy(tx - 160)), (tx + 160, sy(tx + 160))]); rgb(c, (0.06, 0.07, 0.10)); c.fill()
        poly(c, [(tx - 160, sy(tx - 160)), (tx + 160, sy(tx - 160)), (tx + 160, sy(tx + 160))]); rgb(c, (0.06, 0.07, 0.10)); c.fill()
        put(c, tx + 10, sy(tx - 160) + 2, lambda c: dyatlov_tent(c, t, sag=slab_fall), 0.42, cut)
    if pile > 0:
        c.move_to(tx + 170, sy(tx + 170)); c.line_to(tx + 620, sy(tx + 620))
        c.curve_to(tx + 450, sy(tx + 450) - 60 * pile, tx + 300, sy(tx + 300) - 80 * pile, tx + 170, sy(tx + 170) - 40 * pile); c.close_path()
        rgb(c, (0.92, 0.95, 1.0)); c.fill()
    if slab > 0:
        p = slab_fall
        sx = tx + 360 - p * 230
        put(c, sx, sy(sx) - 60 + p * 10, lambda c: (c.rotate(-math.atan(k)), snow_slab(c, 300, 70, crack)), 0.9, slab)


def s50(c, t):  # 760.5 - 775.1  degrau na encosta; vento empilha neve
    sky(c, t, 400, moon_xy=None)
    show(c, t, 760.7, 1150, 110, lambda c: hl(c, "a conclusão do estudo", 0, 0, 44), anim="up", t1=tw("Para", 762.5) - 0.1)
    ct = tw("degrau", 764.5)
    wt = tw("vento", 769.5)
    slope_section(c, t, cut=fade_in(t, ct - 0.4, 0.8), pile=prog(t, wt + 1, 4.0))
    show(c, t, ct, 820, 640, T("degrau cavado", 32, INK, HAND), anim="fade")
    show(c, t, tw("enfraqueceu", 766), 1150, 200, T("a neve logo acima fica mais fraca", 34, ICE), anim="fade", t1=wt - 0.2)
    if t > wt:
        wind_lines(c, t, 12, 200, 520, speed=-700)
        show(c, t, wt, 1150, 200, T("o vento que desce a montanha empilha neve", 34, ICE), anim="fade")
    HIST(c, t, [(0, "present"), (ct, "point_r")], [(0, "neutral"), (ct, "think")], x=240, s=0.85)


def s50b(c, t):  # 775.1 - 795.2  horas depois a placa se solta; bloco pequeno; fraturas
    sky(c, t, 400, moon_xy=None)
    ht = tw("placa", 776)
    ft = tw("cair", 783)
    slope_section(c, t, cut=1.0, pile=1.0, slab=1.0, slab_fall=prog(t, ft - 0.3, 1.0), crack=prog(t, ht, 1.0))
    show(c, t, 775.3, 1150, 110, lambda c: date_stamp(c, "HORAS DEPOIS", 44, RED), anim="stamp", t1=tw("Não", 777.5) - 0.1)
    show(c, t, tw("Não", 777.5), 1150, 110, lambda c: hl(c, "não uma avalanche gigante", 0, 0, 42), anim="up", t1=tw("Um", 779) - 0.1)
    show(c, t, tw("Um", 779), 1150, 110, lambda c: hl(c, "um bloco pequeno e pesado", 0, 0, 42), anim="up", t1=tw("segundo", 785) - 0.2)
    show(c, t, tw("segundo", 785), 1150, 110, lambda c: hl(c, "fraturas sem grandes ferimentos por fora", 0, 0, 40), anim="up")
    if t > ft:
        for k in range(3):
            ex = 1180 + k * 50
            show(c, t, ft + 0.3, ex, 560, lambda c: (line(c, -14, -14, 14, 14, 6, RED), line(c, -14, 14, 14, -14, 6, RED)), anim="pop")
    HIST(c, t, [(0, "present"), (ft, "point_r")], [(0, "neutral"), (ft, "shocked")], x=240, s=0.85)


def s51(c, t):  # 795.2 - 807.7  explicaria o corte na lona e as pegadas
    sky(c, t, 420, moon_xy=None)
    slope(c)
    tx = 1500
    put(c, tx, slope_y(tx) + 6, lambda c: dyatlov_tent(c, t, cut=prog(t, tw("cortaram", 796), 1.0)), 0.7)
    show(c, t, 795.4, 1150, 120, lambda c: caption_box(c, "cortaram a lona: medo de mais neve", 38), anim="up", t1=tw("E", 802.3) - 0.1)
    rt = tw("correndo", 797.5)
    for k in range(5):
        t0 = rt + k * 0.2
        if t > t0:
            x = tx - 160 - (t - t0) * 120
            if x > 640:
                member(c, t, k, x, slope_y(x) + 4, 0.36, [(0, "run")], [(0, "shocked")])
    pt = tw("pegadas", 803.5)
    if t > pt:
        k = (slope_y(1000) - slope_y(1500)) / 500
        for r in range(5):
            c.save(); x0 = 1330 + r * 14; c.translate(x0, slope_y(x0) + 18 + r * 9)
            footprints(c, 10, -60, k * 60, t, pt + r * 0.1, (0.46, 0.52, 0.64)); c.restore()
        show(c, t, pt, 1150, 120, lambda c: caption_box(c, "um bloco pequeno não apaga as pegadas", 38), anim="up")
    HIST(c, t, [(0, "present")], [(0, "think")], x=240, s=0.85)


def s52(c, t):  # 807.7 - 828.7  o estudo não fecha todas as portas: as perguntas
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.05, 0.07)); c.fill()
    show(c, t, 807.9, 1150, 120, lambda c: stitle(c, "Mas o estudo não fecha todas as portas", 0, 0, 46, INK, AMBER), anim="up")
    show(c, t, tw("autores", 811), 1150, 220, T("\"ninguém sabe de verdade o que aconteceu\" — os autores", 30, ICE), anim="fade")
    qs = (("Se", "feridos, desceram 1,5 km no escuro?"), ("radiação", "por que a radiação nas roupas?"), ("luzes", "e as luzes no céu?"))
    for k, (w, s) in enumerate(qs):
        tt = tw(w, 815)
        show(c, t, tt, 1150, 420 + k * 150, lambda c, s=s, k=k: (rrect(c, -480, -55, 960, 110, 12), fs(c, (0.10, 0.12, 0.15), 4, ICE),
                                                             text(c, s, 30, 0, 36, TYPE, INK), text(c, "?", -430, 0, 60, SERIF, AMBER)), anim="left")
    HIST(c, t, [(0, "think"), (816, "shrug")], [(0, "think")], x=230, s=0.8)


def s53(c, t):  # 828.7 - 847.0  Yuri Yudin viveu até 2013; uma pergunta a Deus
    c.rectangle(0, 0, W, H); rgb(c, (0.04, 0.04, 0.05)); c.fill()
    glow(c, 1150, 620, 600, LYELLOW, 0.10)
    put(c, 1360, 760, lambda c: candle(c, t), 1.0, fade_in(t, 829))
    fig(c, t, 1100, 980, 1.0, [(0, "stand"), (tw("pergunta", 841.5), "think")], [(0, "sad")], appear=829.0, fid=160,
        shirt=(0.55, 0.40, 0.44), hair="tuft", glasses=True, coat=(0.30, 0.26, 0.28))
    show(c, t, 829.0, 1150, 120, lambda c: hl(c, "YURI YUDIN (1937-2013)", 0, 0, 44), anim="up")
    show(c, t, tw("vida", 835), 1150, 220, T("a vida inteira tentando entender", 34, ICE), anim="fade", t1=tw("costumava", 839) - 0.2)
    show(c, t, tw("pergunta", 841.5), 1150, 220, lambda c: hl(c, "\"uma única pergunta a Deus\"", 0, 0, 40), anim="up")
    show(c, t, tw("aconteceu", 844), 1150, 320, T("o que aconteceu com eles naquela noite?", 34, AMBER), anim="fade")
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=250, s=0.85)


def s54(c, t):  # 847.0 - 863.6  a placa com os nove nomes; correr para o escuro
    sky(c, t, 600)
    put(c, 1150, 900, lambda c: mountains(c, 1700, 400, col=(0.22, 0.25, 0.32)), 1.0)
    snowland(c, 900)
    pt = tw("placa", 849.5)
    show(c, t, pt - 0.6, 1150, 940, lambda c: memorial_plaque(c, NOMES, 620, 420), anim="up")
    show(c, t, tw("jovens", 852.5), 1150, 120, T("jovens, experientes e cuidadosos", 38, INK), anim="fade", t1=tw("alguma", 855.5) - 0.2)
    show(c, t, tw("alguma", 855.5), 1150, 120, lambda c: hl(c, "algo forte o bastante para fazê-los correr para o escuro", 0, 0, 34), anim="up")
    snow(c, t, 120, 80, 0.6)
    fog(c, t, 900, 0.08)
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=250)


def s55(c, t):  # 863.6 - 875.1  e você? avalanche, teste militar, ou algo que não entendemos?
    sky(c, t, 700, moon_xy=None)
    show(c, t, 863.8, 1150, 110, lambda c: stitle(c, "E você?", 0, 0, 72, INK, AMBER), anim="up")
    opts = (("avalanche?", tw("avalanche", 866)), ("teste militar?", tw("teste", 867)), ("o desconhecido?", tw("alguma", 868)))
    for i, (s, tt) in enumerate(opts):
        icon = (lambda c: snow_slab(c, 180, 50), lambda c: (c.scale(0.4, 0.4), rocket(c, t)), lambda c: big_q(c, 90, AMBER))[i]
        show(c, t, tt, 760 + i * 400, 530, lambda c, s=s, ic=icon, i=i: theory_card(c, str(i + 1), s, ic, w=340, h=400), anim="up")
    show(c, t, tw("Deixa", 870), 1150, 920, lambda c: (speech(c, 820, 130, -300, 110), text(c, "deixe sua teoria nos comentários", 0, 0, 42, HAND, INK)),
         anim="pop")
    HIST(c, t, [(0, "point_r"), (870.4, "present")], [(0, "think"), (870.4, "happy")], x=220, s=0.8)


def s56(c, t):  # 875.1 - fim  encerramento
    sky(c, t, 740, moon_xy=(1640, 160))
    far_mountains(c, 945, 0.3)
    snowland(c, 940)
    put(c, 1650, 940, lambda c: dyatlov_tent(c, t, glow_on=True), 0.5, 0.8 * fade_in(t, 875.3, 2.0))
    HIST(c, t, [(0, "stand"), (875.6, "present"), (878.5, "wave"), (880.5, "stand")], [(0, "neutral"), (877.0, "happy")], x=420, s=1.05)
    show(c, t, 875.4, 1100, 260, T("Eu sou o Historiador.", 44, AMBER), anim="fade")
    show(c, t, 877.0, 1100, 470, sc(subscribe_btn, t > 878.5, s=0.9))
    show(c, t, 877.4, 1430, 470, sc(bell, s=0.8), rot=math.sin(t * 18) * 0.2 * max(0, 1 - (t - 877.4)))
    show(c, t, 878.0, 1100, 720, lambda c: (text(c, "PONTO CEGO", 0, 0, 84, SERIF, INK), line(c, -300, 58, 300, 58, 3, AMBER)), anim="fade", d=1.2)
    snow(c, t, 100, 70, 0.5)
    fog(c, t, 980, 0.09)


SCENES = [
    (0.0, 8.0, s01), (8.0, 14.9, s02), (14.9, 23.5, s03), (23.5, 33.6, s04), (33.6, 42.3, s05), (42.3, 58.4, s06),
    (58.4, 61.9, s07), (61.9, 73.4, s08), (73.4, 87.7, s09), (87.7, 97.2, s10), (97.2, 113.0, s11), (113.0, 136.4, s12),
    (136.4, 147.5, s13), (147.5, 162.6, s14), (162.6, 170.5, s15), (170.5, 190.1, s16), (190.1, 201.5, s17),
    (201.5, 215.3, s18), (215.3, 235.4, s19), (235.4, 259.7, s20), (259.7, 279.0, s21), (279.0, 281.9, s22),
    (281.9, 299.9, s23), (299.9, 309.0, s24), (309.0, 323.5, s25), (323.5, 336.2, s26), (336.2, 352.5, s27),
    (352.5, 365.0, s28), (365.0, 384.8, s29), (384.8, 393.8, s30), (393.8, 410.7, s31), (410.7, 422.7, s32),
    (422.7, 434.0, s33), (434.0, 454.9, s34), (454.9, 471.0, s35), (471.0, 485.6, s36), (485.6, 498.9, s36b),
    (498.9, 513.8, s37), (513.8, 537.9, s38), (537.9, 556.5, s39), (556.5, 579.7, s40), (579.7, 598.9, s41),
    (598.9, 611.5, s42), (611.5, 629.1, s43), (629.1, 649.0, s44),
    (649.0, 664.6, s45), (664.6, 678.8, s46), (678.8, 700.4, s47), (700.4, 724.7, s48), (724.7, 747.1, s49),
    (747.1, 760.5, s49b), (760.5, 775.1, s50), (775.1, 795.2, s50b), (795.2, 807.7, s51), (807.7, 828.7, s52),
    (828.7, 847.0, s53), (847.0, 863.6, s54), (863.6, 875.1, s55), (875.1, 999.0, s56),
]

# Sons: nada automático (sem whoosh em transição, sem som em cada ícone). Só toques sem chiado nos momentos-chave.
SFX_OFF = True
SFX = [(4.6, "tum"), (17.0, "boom"), (38.6, "heartbeat"), (48.6, "tum"), (58.7, "boom"), (187.1, "bell"), (279.3, "tum"),
       (288.4, "tum"), (316.0, "boom"), (325.6, "heartbeat"), (380.0, "bell"), (434.4, "boom"), (481.6, "tum"),
       (520.3, "heartbeat"), (545.2, "boom"), (568.0, "tum"), (744.6, "tum"), (783.5, "boom"), (858.0, "bell"), (878.0, "boom")]
