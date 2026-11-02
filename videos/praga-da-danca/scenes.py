"""A Praga da Dança de 1518 (Estrasburgo) — Ponto Cego.
Narração: Pedro Lima - Serious (HeyGen / ElevenLabs v4), 5 blocos com 1 s de silêncio entre eles (~748,3 s).
Tempos absolutos (já com os offsets dos blocos): transcricao.txt e palavras.json (gerados por tempos.py).
tw("palavra", depois_de) devolve o início da primeira palavra que começa com esse texto depois do tempo dado.
Objetos do caso (casas de enxaimel, catedral, sapatos vermelhos, tambor, carroça, imagem de São Vito, centeio com
esporão...) ficam no engine.py (seção PRAGA DA DANÇA). Sem corpos nem sangue na tela: o clima vem da atmosfera.
"""
import json
import os
import unicodedata

from engine import *

THEME = "cidade"

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


# ------------------------------------------------------------------ helpers
TROF = (0.52, 0.22, 0.20)      # Frau Troffea
PRIEST = (0.12, 0.12, 0.14)
DOCTOR = (0.50, 0.16, 0.16)
COUNCIL = (0.18, 0.24, 0.30)
PEASANT = [(0.40, 0.34, 0.26), (0.30, 0.34, 0.30), (0.44, 0.30, 0.24), (0.32, 0.30, 0.38), (0.46, 0.40, 0.30)]


def HIST(c, t, poses, exprs, appear=None, x=290, y=1010, s=0.95, **kw):
    historiador(c, t, x, y, s, poses, exprs, appear=appear, look=1, **kw)


def faded(c, a, fn):
    if a <= 0.001:
        return
    if a >= 0.999:
        fn(c); return
    c.push_group(); fn(c); c.pop_group_to_source(); c.paint_with_alpha(a)


def fade_in(t, t0, d=0.8):
    return clamp01((t - t0) / d)


def fade_out(t, t0, d=0.8):
    return 1 - clamp01((t - t0) / d)


def put(c, x, y, fn, s=1.0, a=1.0):
    faded(c, a, lambda c: (c.save(), c.translate(x, y), c.scale(s, s), fn(c), c.restore()))


def x_over(c, t, t0, x, y, s=70):
    show(c, t, t0, x, y, lambda c: big_x(c, s, RED, 14), anim="stamp")


def check(c, s=1.0, col=(0.45, 0.72, 0.42)):
    c.save(); c.scale(s, s)
    c.move_to(-34, 0); c.line_to(-8, 26); c.line_to(38, -30)
    rgb(c, col); c.set_line_width(12); c.stroke()
    c.restore()


def bubble(c, s, w=None, size=40, tx=-80, ty=90, col=INK):
    ww = w or text_w(c, s, size, HAND) + 80
    speech(c, ww, 110, tx, ty)
    text(c, s, 0, 0, size, HAND, col)


def night(c, t, ymax=520, moon_xy=(1660, 150), n=70):
    stars(c, t, n, ymax)
    if moon_xy:
        c.save(); c.translate(*moon_xy); moon(c, 48); c.restore()
        glow(c, moon_xy[0], moon_xy[1], 200, LYELLOW, 0.08)


def street(c, t, y=880, lit=0.7, cat_x=None, seed=3, n=7, moon_xy=(1800, 250)):
    night(c, t, y - 300, moon_xy)
    strasbourg(c, t, y, n=n, seed=seed, lit=lit, cat_x=cat_x)


def woman(c, t, x, y, s, poses=((0, "stand"),), exprs=((0, "neutral"),), col=TROF, fid=40, appear=None, alpha=1.0):
    faded(c, alpha, lambda c: figure(c, t, x, y, s, poses=poses, exprs=exprs, coat=col, hat="coif", hair="long",
                                     fid=fid, appear=appear))


def man(c, t, x, y, s, poses=((0, "stand"),), exprs=((0, "neutral"),), col=PEASANT[0], fid=41, appear=None,
        hat="beret", hat_col=(0.22, 0.18, 0.15), alpha=1.0, **kw):
    faded(c, alpha, lambda c: figure(c, t, x, y, s, poses=poses, exprs=exprs, coat=col, hat=hat, hat_col=hat_col,
                                     hair=None, fid=fid, appear=appear, **kw))


def priest(c, t, x, y, s, poses=((0, "stand"),), exprs=((0, "neutral"),), fid=50, appear=None):
    figure(c, t, x, y, s, poses=poses, exprs=exprs, coat=PRIEST, hat="skullcap", hair=None, fid=fid, appear=appear)


def doctor(c, t, x, y, s, poses=((0, "stand"),), exprs=((0, "neutral"),), fid=60, appear=None):
    figure(c, t, x, y, s, poses=poses, exprs=exprs, coat=DOCTOR, hat="beret", hat_col=(0.10, 0.08, 0.08), hair=None,
           fid=fid, appear=appear, glasses=True)


def councilor(c, t, x, y, s, poses=((0, "stand"),), exprs=((0, "neutral"),), fid=70, appear=None):
    figure(c, t, x, y, s, poses=poses, exprs=exprs, coat=COUNCIL, hat="beret", hat_col=(0.08, 0.08, 0.10),
           hair=None, fid=fid, appear=appear, mustache=(fid % 2 == 0))


def troffea(c, t, x, y, s, t0=0.0, t1=9999.0, exprs=((0, "desperate"),), start="stand", end=None, appear=None, period=0.6):
    dancer(c, t, x, y, s, t0=t0, t1=t1, fid=7, col=TROF, exprs=exprs, start=start, end=end, appear=appear, period=period)


def mini_dancer(c, t, x, y, s=0.5, seed=0, col=None, on=True):
    """silhueta pequena dançando (para multidões): corpo, braços se debatendo, pulos"""
    ph = t * 6.0 + seed * 1.37
    dy = -abs(math.sin(ph)) * 14 * s if on else 0
    c.save(); c.translate(x + (math.sin(ph * 0.5) * 6 * s if on else 0), y + dy); c.scale(s, s)
    col = col or PEASANT[seed % len(PEASANT)]
    poly(c, [(-22, -150), (22, -150), (34, -70), (-34, -70)]); fs(c, col, 4)
    circle(c, 0, -178, 24, FILL, 4)
    if seed % 2 == 0:
        c.new_sub_path(); c.arc(0, -180, 26, math.pi, 2 * math.pi); rgb(c, (0.84, 0.80, 0.70)); c.set_line_width(8); c.stroke()
    a1 = math.sin(ph) * 0.9 if on else 0.0
    a2 = math.cos(ph * 1.1) * 0.9 if on else 0.0
    for sx, a in ((1, a1), (-1, a2)):
        ang = -math.pi / 2 + sx * (0.7 + a * 0.6) if on else math.pi / 2 - sx * 0.25
        line(c, sx * 14, -142, sx * 14 + math.cos(ang) * 70, -142 + math.sin(ang) * 70, 6)
    k = math.sin(ph) if on else 0
    line(c, -12, -72, -22 - k * 14, 0, 6); line(c, 12, -72, 22 + k * 10, -abs(k) * 26, 6)
    c.restore()


def dance_crowd(c, t, t0, n, y0=900, x0=760, x1=1760, rows=3, s=0.42, seed=1, d=2.0):
    rnd = random.Random(seed)
    spots = []
    for i in range(n):
        r = i % rows
        spots.append((rnd.uniform(x0, x1), max(y0, 960) - r * 34 + rnd.uniform(0, 30), s * (1 - r * 0.10), i))
    spots.sort(key=lambda p: p[1])
    for (x, y, ss, i) in spots:
        if t >= t0 + d * i / max(1, n):
            mini_dancer(c, t, x, y, ss, seed=i + seed * 7)


def counter(c, val, label, col=AMBER):
    text(c, str(val), 0, 0, 120, SERIF, col)
    text(c, label, 0, 90, 34, TYPE, INK)


def card(c, n, title_s, icon=None, crossed=0.0, w=330, h=420, sub=None, dim=False):
    rrect(c, -w / 2, -h / 2, w, h, 14); fs(c, (0.12, 0.11, 0.12), 5, LGRAY if dim else (0.78, 0.66, 0.52))
    text(c, n, 0, -h / 2 + 44, 32, TYPE, AMBER)
    text(c, title_s, 0, -h / 2 + 96, 38 if len(title_s) < 12 else 30, SERIF, GRAY if dim else INK)
    if sub:
        text(c, sub, 0, h / 2 - 36, 26, TYPE, GRAY)
    if icon:
        c.save(); c.translate(0, 50); icon(c); c.restore()
    if crossed > 0:
        c.save(); c.scale(crossed, crossed); big_x(c, 120, RED, 14); c.restore()


def label_card(c, top, name, w=None):
    ww = w or max(text_w(c, name, 44, SERIF), text_w(c, top, 30, TYPE)) + 70
    rrect(c, -ww / 2, -62, ww, 124, 12); fs(c, (0.10, 0.10, 0.11), 4, (0.62, 0.56, 0.48))
    text(c, top, 0, -26, 30, TYPE, AMBER)
    text(c, name, 0, 22, 44, SERIF, INK)


# --- mapa do Reno (lon/lat)
RHINE = [(7.59, 47.56), (7.62, 47.95), (7.75, 48.58), (8.10, 48.90), (8.40, 49.05), (8.47, 49.49), (8.27, 50.00),
         (7.85, 50.10), (7.60, 50.36), (7.10, 50.73), (6.96, 50.94), (6.77, 51.23), (6.25, 51.83), (5.90, 51.98),
         (5.10, 51.95), (4.48, 51.92)]
MOSELLE = [(6.40, 48.20), (6.18, 49.12), (6.40, 49.50), (6.64, 49.75), (7.10, 50.00), (7.60, 50.36)]
BORDER = [(7.59, 47.59), (7.55, 48.10), (7.80, 48.58), (8.23, 48.97), (7.60, 49.08), (6.90, 49.20), (6.40, 49.47), (5.80, 49.55)]
CITY = {"Estrasburgo": (7.75, 48.58), "Saverne": (7.36, 48.74), "Aachen": (6.08, 50.78), "Colônia": (6.96, 50.94),
        "Metz": (6.18, 49.12), "Utrecht": (5.12, 52.09), "Erfurt": (11.03, 50.98), "Arnstadt": (10.95, 50.83),
        "Basileia": (7.59, 47.56), "Mainz": (8.27, 50.00)}


def rhine_map(c, t, proj, p_rhine=1.0, moselle=False, border=False):
    c.rectangle(0, 0, W, H); rgb(c, (0.10, 0.11, 0.10)); c.fill()
    c.set_dash([4, 12])
    for lon in range(0, 16):
        x, _ = proj(lon, 0)
        line(c, x, 0, x, H, 1.5, (0.22, 0.24, 0.24))
    for lat in range(44, 56):
        _, y = proj(0, lat)
        line(c, 0, y, W, y, 1.5, (0.22, 0.24, 0.24))
    c.set_dash([])
    map_path(c, proj, RHINE, p_rhine, (0.42, 0.62, 0.80), 7)
    if moselle:
        map_path(c, proj, MOSELLE, 1.0, (0.42, 0.62, 0.80), 5)
    if border:
        c.set_dash([14, 10]); map_path(c, proj, BORDER, 1.0, (0.70, 0.55, 0.45), 3); c.set_dash([])


def city_pt(c, t, proj, name, dx=0, dy=-38, col=AMBER, size=32, pulse=True):
    lon, lat = CITY[name]
    map_point(c, proj, lon, lat, col, 9, t, pulse)
    map_label(c, proj, lon, lat, name, size, INK, TYPE, dx, dy)


# ================================================================== CENAS
def s01(c, t):  # 0 - 12.1  dia quente de julho; uma mulher para na rua e começa a dançar; sem música, sem festa
    street(c, t, 880, 0.3)
    dt = tw("dançar", 5)
    troffea(c, t, 1150, 960, 0.9, t0=dt, exprs=((0, "neutral"), (dt, "worried")), appear=1.6)
    show(c, t, 0.3, 1150, 110, lambda c: date_stamp(c, "JULHO", 52, AMBER), anim="stamp", t1=7.0)
    m = tw("música", 7)
    show(c, t, m - 0.2, 1500, 300, lambda c: (sc(music_notes, t, 0, 0, 3, INK, 90)(c)), anim="fade")
    x_over(c, t, m + 0.3, 1500, 300, 60)
    f = tw("festa", 8)
    show(c, t, f - 0.2, 800, 300, T("festa", 44, INK, HAND), anim="fade")
    x_over(c, t, f + 0.3, 800, 300, 60)
    show(c, t, tw("Ninguém", 9), 1150, 110, lambda c: hl(c, "ninguém sabia por quê", 0, 0, 48), anim="up")
    fog(c, t, 900, 0.07)
    HIST(c, t, [(0, "stand"), (dt, "think")], [(0, "neutral"), (dt, "worried")], appear=0.4)


def s02(c, t):  # 12.1 - 22.3  dançou a tarde inteira, até a noite; no dia seguinte e no outro
    k = clamp01((t - 12.2) / 3.8)
    street(c, t, 880, 0.3 + 0.7 * k)
    c.rectangle(0, 0, W, H); rgb(c, (0.02, 0.02, 0.05), 0.30 * k); c.fill()
    troffea(c, t, 1150, 960, 0.9, t0=0)
    show(c, t, 12.3, 1150, 110, lambda c: caption_box(c, "a tarde inteira", 44), anim="up", t1=tw("seguinte", 16) - 0.4)
    show(c, t, tw("seguinte", 16) - 0.3, 1000, 110, lambda c: date_stamp(c, "DIA 2", 52, AMBER), anim="stamp")
    show(c, t, tw("outro", 20) - 0.1, 1320, 110, lambda c: date_stamp(c, "DIA 3", 52, RED), anim="stamp")
    fog(c, t, 900, 0.07)
    HIST(c, t, [(0, "think")], [(0, "worried")])


def s03(c, t):  # 22.3 - 39.6  em uma semana, mais de 30; em um mês, centenas; homens, mulheres...; pés sangrando
    street(c, t, 880, 0.9, n=8, seed=5)
    c0 = tw("trinta", 22)
    troffea(c, t, 1000, 960, 0.75, t0=0)
    dance_crowd(c, t, c0 - 0.5, 14, 950, 650, 1800, 2, 0.48, seed=2, d=1.6)
    show(c, t, 22.5, 1250, 110, lambda c: hl(c, "em uma semana: mais de 30", 0, 0, 46), anim="up", t1=tw("mês", 26) - 0.3)
    ct = tw("centenas", 27)
    show(c, t, tw("mês", 26), 1250, 110, lambda c: hl(c, "em um mês: centenas", 0, 0, 46), anim="up")
    dance_crowd(c, t, ct, 30, 800, 600, 1820, 3, 0.30, seed=9, d=2.5)
    labs = [("homens", "Homens"), ("mulheres", "mulheres"), ("mendigos", "mendigos"), ("peregrinos", "peregrinos"),
            ("padres e freiras", "padres")]
    for i, (s, w) in enumerate(labs):
        show(c, t, tw(w, 30), 760 + i * 250, 220, T(s, 34, INK, HAND), anim="pop", t1=36.0)
    show(c, t, tw("sangrando", 36) - 0.2, 1250, 230, lambda c: caption_box(c, "sem conseguir parar", 42), anim="up")
    fog(c, t, 920, 0.08)
    HIST(c, t, [(0, "stand"), (ct, "head")], [(0, "worried"), (ct, "shocked")], x=260, s=0.9)


def s04(c, t):  # 39.6 - 52.2  as autoridades: contrataram músicos, montaram palcos, mandaram dançar mais
    street(c, t, 880, 0.9, n=6, seed=8)
    mt = tw("contrataram", 45)
    pt = tw("palcos", 46)
    dt = tw("dançarem", 48)
    show(c, t, 39.8, 1200, 110, lambda c: hl(c, "a decisão das autoridades", 0, 0, 46), anim="up")
    put(c, 1250, 930, lambda c: stage(c, 700, 100), 1.0, fade_in(t, pt - 0.2, 0.5))
    man(c, t, 1010, 830, 0.55, poses=((0, "hold"),), col=PEASANT[1], fid=81, appear=mt, prop=None)
    show(c, t, mt + 0.1, 1010, 690, sc(drum, t, s=0.5), anim="pop")
    man(c, t, 1490, 830, 0.55, poses=((0, "hold"),), col=PEASANT[3], fid=82, appear=mt + 0.4)
    show(c, t, mt + 0.5, 1540, 640, sc(trumpet, s=0.55), anim="pop")
    if t > mt:
        music_notes(c, t, 1250, 560, 5, AMBER, 220)
    for i in range(3):
        dancer(c, t, 1150 + i * 120, 830, 0.5, t0=dt - 0.3, fid=90 + i, col=PEASANT[(i + 2) % 5], woman=(i != 1), appear=dt - 0.3 + i * 0.2)
    fog(c, t, 940, 0.07)
    HIST(c, t, [(0, "stand"), (mt, "shrug")], [(0, "neutral"), (mt, "shocked")])


def s05(c, t):  # 52.2 - 57.1  título
    night(c, t, 600, (1680, 150), 110)
    c.save(); c.translate(1640, 1040); cathedral(c, 560, lit=0.7); c.restore()
    c.save(); c.translate(300, 1040); half_timber(c, 220, 260, seed=2, lit=0.6); c.restore()
    c.rectangle(0, 0, W, H); rgb(c, (0.02, 0.02, 0.03), 0.60); c.fill()
    show(c, t, 52.3, 960, 420, lambda c: (text(c, "A", 0, -110, 46, TYPE, AMBER),
                                          stitle(c, "PRAGA DA DANÇA", 0, 10, 130, INK, AMBER)), anim="fade", d=1.2)
    show(c, t, 53.6, 960, 560, lambda c: line(c, -440, 0, 440, 0, 3, AMBER), anim="fade")
    show(c, t, 54.4, 960, 620, T("Estrasburgo  ·  1518", 40, ICE), anim="fade", d=1.0)
    fog(c, t, 900, 0.10)


PROJ_R = make_proj(3.0, 12.6, 46.9, 52.6)


def s06(c, t):  # 57.1 - 68.5  voltar 500 anos, Estrasburgo; hoje França, Alsácia, fronteira com a Alemanha
    rhine_map(c, t, PROJ_R, 1.0, border=t > tw("fronteira", 65) - 0.3)
    city_pt(c, t, PROJ_R, "Estrasburgo", 0, -40)
    show(c, t, 57.3, 1300, 110, lambda c: hl(c, "mais de 500 anos atrás", 0, 0, 46), anim="up")
    show(c, t, tw("França", 63), 0, 0, lambda c: map_label(c, PROJ_R, 5.0, 48.3, "FRANÇA", 56, LGRAY, SERIF), anim="fade")
    show(c, t, tw("Alsácia", 65), 0, 0, lambda c: map_label(c, PROJ_R, 7.0, 48.1, "Alsácia", 34, AMBER, TYPE), anim="fade")
    show(c, t, tw("Alemanha", 66), 0, 0, lambda c: map_label(c, PROJ_R, 10.0, 49.4, "ALEMANHA", 56, LGRAY, SERIF), anim="fade")
    show(c, t, 60.0, 0, 0, lambda c: map_label(c, PROJ_R, 6.4, 51.6, "rio Reno", 30, (0.55, 0.72, 0.88), TYPE), anim="fade")
    HIST(c, t, [(0, "point_r")], [(0, "neutral")], x=260, s=0.85)


def s07(c, t):  # 68.5 - 84.7  1518: cidade livre do Sacro Império; 20 mil; ruas estreitas, enxaimel, catedral
    street(c, t, 900, 0.8, cat_x=1250, seed=11, n=8)
    show(c, t, 68.7, 1250, 100, lambda c: date_stamp(c, "1518", 60, AMBER), anim="stamp", t1=tw("Tinha", 74) - 0.3)
    show(c, t, tw("livre", 71), 1250, 190, lambda c: caption_box(c, "cidade livre do Sacro Império", 40), anim="up", t1=tw("Tinha", 74) - 0.3)
    show(c, t, tw("vinte", 75), 1250, 100, lambda c: hl(c, "~20 mil habitantes", 0, 0, 46), anim="up")
    show(c, t, tw("catedral", 78), 1640, 330, lambda c: (text(c, "catedral de", 0, -22, 30, TYPE, INK),
                                                         text(c, "arenito vermelho", 0, 18, 30, TYPE, AMBER)), anim="fade")
    if t > tw("torre", 80):
        glow(c, 1250 - 135, 900 - 700, 160, AMBER, 0.18 * fade_in(t, tw("torre", 80)))
    fog(c, t, 940, 0.08)
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=270, s=0.9)


def s08(c, t):  # 84.7 - 96.7  cidade rica: mercadores, artesãos, corporações; riqueza não chegava a todos
    street(c, t, 900, 0.8, seed=13)
    pt = tw("riqueza", 89)
    for i in range(3):
        man(c, t, 820 + i * 170, 960, 0.6, poses=((0, "present" if i == 1 else "hips"),), exprs=((0, "happy"),),
            col=[(0.30, 0.20, 0.36), COUNCIL, (0.42, 0.22, 0.16)][i], fid=100 + i, appear=85.0 + i * 0.6,
            alpha=fade_out(t, pt + 0.8, 1.2) * 0.5 + 0.5)
    show(c, t, tw("mercadores", 86), 990, 500, sc(money_bag, "", s=0.6), anim="pop")
    show(c, t, tw("corporações", 88), 1250, 100, lambda c: hl(c, "mercadores, artesãos, corporações", 0, 0, 42), anim="up", t1=pt - 0.2)
    pp = tw("pobres", 95)
    for i in range(3):
        woman(c, t, 1400 + i * 140, 960, 0.6, exprs=((0, "sad"),), col=PEASANT[i + 1], fid=110 + i, appear=tw("todo", 91) + i * 0.3)
    show(c, t, pt, 1250, 100, lambda c: hl(c, "mas não para todos", 0, 0, 46), anim="up")
    show(c, t, pp, 1540, 650, lambda c: caption_box(c, "os mais pobres", 38), anim="up")
    fog(c, t, 940, 0.08)
    HIST(c, t, [(0, "stand"), (pt, "think")], [(0, "neutral"), (pt, "sad")], x=260, s=0.85)


def s09(c, t):  # 96.7 - 116.9  invernos e colheitas ruins, pão caro; fome; varíola, lepra, sífilis
    night(c, t, 600, None)
    cobbles(c, 900)
    dt = tw("Doenças", 105)
    show(c, t, 97.0, 1250, 100, lambda c: hl(c, "invernos rigorosos, colheitas ruins", 0, 0, 42), anim="up", t1=dt - 0.3)
    if t < dt:
        snow(c, t, 70, 30, 0.5 * fade_in(t, 97.0))
        for i in range(5):
            put(c, 760 + i * 110, 900, lambda c, i=i: (c.rotate(0.35 + i * 0.05), rye(c, False, 200, i)), 1.0, fade_in(t, 98.5 + i * 0.15))
        bt = tw("pão", 100)
        show(c, t, bt, 1450, 700, sc(bread, s=1.2), anim="pop")
        show(c, t, bt + 0.4, 1600, 560, lambda c: (rrect(c, -70, -36, 140, 72, 10), fs(c, PARCH, 4),
                                                   text(c, "$$$", 0, 2, 40, SERIF, RED)), anim="stamp")
        show(c, t, tw("fome", 102), 1250, 230, lambda c: caption_box(c, "fome nas ruas e nos campos", 40), anim="up")
    else:
        items = [("varíola", tw("varíola", 107)), ("lepra", tw("lepra", 108)), ("sífilis", tw("sífilis", 114))]
        for i, (s, tt) in enumerate(items):
            show(c, t, tt - 0.2, 760 + i * 380, 540, lambda c, s=s, i=i: card(c, "", s, lambda c: sc(skull, s=0.6)(c) if i == 0 else
                 (sc(bell, s=0.8)(c) if i == 1 else text(c, "?", 0, 20, 120, SERIF, RED)), w=320, h=380), anim="up")
        show(c, t, tw("nova", 110), 1520, 800, T("doença nova, sem cura", 32, AMBER), anim="fade")
        show(c, t, dt, 1150, 100, lambda c: hl(c, "doenças", 0, 0, 48), anim="up")
    fog(c, t, 940, 0.07)
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=250, s=0.85)


def s10(c, t):  # 116.9 - 132.3  o medo; religiosos; santos protegem e castigam; temido no Reno: São Vito
    night(c, t, 600, None)
    c.save(); c.translate(1250, 1000); cathedral(c, 760, lit=0.8); c.restore()
    c.rectangle(0, 0, W, H); rgb(c, (0.02, 0.02, 0.03), 0.35); c.fill()
    show(c, t, 117.0, 1250, 90, lambda c: stitle(c, "O medo", 0, 0, 66, INK, AMBER), anim="up", t1=tw("Um", 126) - 0.3)
    for i in range(4):
        man(c, t, 700 + i * 130 + (i > 1) * 680, 1000, 0.55, poses=((0, "think"),), exprs=((0, "worried"),),
            col=PEASANT[i], fid=120 + i, appear=tw("religiosos", 120) + i * 0.2) if i % 2 else \
            woman(c, t, 700 + i * 130 + (i > 1) * 680, 1000, 0.55, poses=((0, "think"),), exprs=((0, "worried"),),
                  col=PEASANT[i], fid=120 + i, appear=tw("religiosos", 120) + i * 0.2)
    show(c, t, tw("proteger", 123), 780, 330, lambda c: (check(c, 1.0), text(c, "proteger", 0, 70, 34, TYPE, INK)), anim="pop", t1=tw("Um", 126) - 0.3)
    show(c, t, tw("castigar", 125), 1720, 330, lambda c: (big_x(c, 40, RED, 12), text(c, "castigar", 0, 70, 34, TYPE, RED)), anim="pop", t1=tw("Um", 126) - 0.3)
    vt = tw("São", 130)
    show(c, t, vt, 1250, 120, lambda c: hl(c, "São Vito", 0, 0, 64), anim="stamp")
    fog(c, t, 960, 0.08)
    HIST(c, t, [(0, "stand"), (vt, "point_r")], [(0, "worried")], x=250, s=0.9)


def s11(c, t):  # 132.3 - 153.8  Vito: Sicília, mártir; protetor de dançarinos, atores, epilepsia; festa em junho
    c.rectangle(0, 0, W, H); rgb(c, (0.06, 0.05, 0.05)); c.fill()
    glow(c, 1150, 540, 520, AMBER, 0.10)
    for x in (1000, 1300):
        put(c, x, 880, lambda c: candle(c, t), 1.0)
    put(c, 1150, 900, lambda c: saint_statue(c, t, True), 1.25, fade_in(t, 132.4))
    show(c, t, 132.5, 1150, 100, lambda c: hl(c, "Sicília · mártir, séc. IV (tradição)", 0, 0, 40), anim="up", t1=tw("tempo", 138) - 0.2)
    pt = [("dançarinos", tw("dançarinos", 140)), ("atores", tw("atores", 141)), ("epilepsia", tw("epilepsia", 143))]
    for i, (s, tt) in enumerate(pt):
        show(c, t, tt - 0.2, 1580, 390 + i * 90, T(s, 46, INK, HAND), anim="left", t1=tw("festa", 144) - 0.2)
    show(c, t, tw("tempo", 138), 1580, 300, T("protetor dos", 38, AMBER), anim="fade", t1=tw("festa", 144) - 0.2)
    ft = tw("festa", 144)
    show(c, t, ft, 1150, 100, lambda c: hl(c, "festa em junho", 0, 0, 46), anim="up")
    dt = tw("dançavam", 148)
    for i in range(4):
        x = [700, 840, 1460, 1600][i]
        dancer(c, t, x, 1010, 0.55, t0=dt, fid=130 + i, col=PEASANT[i], woman=bool(i % 2), exprs=((0, "happy"),),
               appear=dt - 0.4 + i * 0.15, period=0.8)
    fog(c, t, 960, 0.07)
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=260, s=0.85)


def s12(c, t):  # 153.8 - 166.0  crença: São Vito lançava maldição sobre pecadores: dançar sem parar
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.03, 0.03)); c.fill()
    k = fade_in(t, tw("maldição", 157), 1.5)
    glow(c, 1150, 520, 560, RED, 0.08 + 0.10 * k)
    put(c, 1150, 900, lambda c: saint_statue(c, t, False), 1.25)
    show(c, t, 154.0, 1150, 100, lambda c: hl(c, "crença popular", 0, 0, 46), anim="up", t1=tw("essa", 161) - 0.3)
    show(c, t, tw("maldição", 157), 1150, 210, lambda c: stitle(c, "a maldição de São Vito", 0, 0, 56, INK, RED), anim="fade", t1=tw("essa", 161) - 0.3)
    dt = tw("dançar", 162)
    show(c, t, dt - 0.2, 1150, 110, lambda c: date_stamp(c, "DANÇAR SEM PARAR", 60, RED), anim="stamp")
    for i in range(2):
        dancer(c, t, [820, 1480][i], 1010, 0.6, t0=dt, fid=140 + i, col=PEASANT[i + 2], woman=bool(i), appear=dt - 0.2)
    fog(c, t, 960, 0.09)
    HIST(c, t, [(0, "stand"), (dt, "head")], [(0, "worried"), (dt, "shocked")], x=260, s=0.85)


def s13(c, t):  # 166.0 - 185.6  14 de julho de 1518, Frau Troffea; 6 crônicas, 4 dão o nome; nada sobre ela
    street(c, t, 880, 0.3, seed=21)
    troffea(c, t, 1250, 960, 0.9, t0=tw("dançar", 170), appear=167.5)
    show(c, t, 166.1, 1250, 100, lambda c: date_stamp(c, "14 DE JULHO DE 1518", 52, AMBER), anim="stamp", t1=tw("Das", 173) - 0.3)
    show(c, t, tw("Frau", 169), 1250, 300, lambda c: hl(c, "Frau Troffea", 0, 0, 52), anim="stamp", t1=tw("Das", 173) - 0.3)
    dt = tw("Das", 173)
    if t > dt - 0.3 and t < tw("Não", 178) + 0.1:
        c.rectangle(0, 0, W, H); rgb(c, (0.03, 0.03, 0.04), 0.75 * fade_in(t, dt - 0.3, 0.5)); c.fill()
        for i in range(6):
            hi = i < 4 and t > tw("quatro", 174)
            show(c, t, dt + i * 0.2, 640 + i * 230, 500, lambda c, hi=hi, i=i: (chronicle(c, 190, 250, "", i + 3),
                 hi and text(c, "Troffea", 0, 0, 30, TYPE, RED)), anim="up")
        show(c, t, dt, 1210, 160, lambda c: caption_box(c, "6 crônicas · 4 dão o nome dela", 40), anim="up")
    nt = tw("Não", 178)
    if t >= nt:
        show(c, t, nt, 1250, 100, lambda c: hl(c, "quase nada se sabe sobre ela", 0, 0, 44), anim="up")
        show(c, t, tw("idade", 181), 1600, 300, T("idade?", 36, INK, HAND), anim="pop")
        show(c, t, tw("rosto", 182), 1600, 380, T("rosto?", 36, INK, HAND), anim="pop")
        show(c, t, tw("nome", 183), 1600, 470, T("só o nome", 36, AMBER, HAND), anim="pop")
    fog(c, t, 920, 0.07)
    HIST(c, t, [(0, "present")], [(0, "neutral"), (nt, "think")], x=270, s=0.9)


def s14(c, t):  # 185.6 - 202.1  dançou 4 a 6 dias; dormia quando desabava; marido envergonhado; multidão olhava
    pt = tw("Parava", 189)
    at_ = tw("Acordava", 193)
    lit = 0.9 if (pt - 0.3 < t < at_) else 0.4
    street(c, t, 880, lit, seed=21)
    if pt - 0.3 < t < at_:
        c.rectangle(0, 0, W, H); rgb(c, (0.02, 0.02, 0.05), 0.4); c.fill()
        troffea(c, t, 1250, 960, 0.9, t0=0, t1=pt + 0.4, end="slump", exprs=((0, "desperate"), (pt + 0.4, "sad")))
        show(c, t, pt + 0.8, 1380, 720, T("z z z", 40, INK, HAND), anim="fade")
    else:
        troffea(c, t, 1250, 960, 0.9, t0=at_)
    show(c, t, 185.8, 1250, 100, lambda c: hl(c, "de 4 a 6 dias", 0, 0, 52), anim="up")
    mt = tw("marido", 195)
    man(c, t, 1560, 960, 0.75, poses=((0, "head"),), exprs=((0, "worried"),), col=PEASANT[1], fid=150, appear=mt - 0.2)
    show(c, t, mt + 0.6, 1560, 560, T("o marido", 34, AMBER, HAND), anim="fade")
    ct = tw("multidão", 199)
    for i in range(6):
        mini = lambda c, i=i: None
        x = 700 + i * 110 if i < 3 else 1700 + (i - 3) * 60
        if t > ct + i * 0.15:
            c.save(); faded(c, 0.85, lambda c, x=x, i=i: mini_dancer(c, t, x, 1000 - (i % 2) * 20, 0.42, seed=i + 3, on=False)); c.restore()
    fog(c, t, 920, 0.07)
    HIST(c, t, [(0, "think")], [(0, "worried")], x=260, s=0.85)


PROJ_S = make_proj(6.6, 8.6, 48.2, 49.2)


def s15(c, t):  # 202.1 - 215.9  carroça para o santuário de São Vito, perto de Saverne, ~50 km; tarde demais
    mt = tw("mandaram", 206)
    st = tw("santuário", 208)
    if t < st + 0.8:
        street(c, t, 880, 0.4, seed=23)
        k = clamp01((t - mt) / 6)
        put(c, 1150 + k * 900, 1000, lambda c: (horse(c), None), 0.9)
        put(c, 860 + k * 900, 1000, lambda c: cart(c, t, 300, moving=t > mt), 1.0)
        woman(c, t, 860 + k * 900, 880, 0.55, poses=((0, "think"),), exprs=((0, "sad"),), col=TROF, fid=7)
        show(c, t, tw("carroça", 205), 1200, 100, lambda c: caption_box(c, "numa carroça, para fora da cidade", 42), anim="up")
    else:
        rhine_map(c, t, PROJ_S, 1.0)
        city_pt(c, t, PROJ_S, "Estrasburgo", 0, 46)
        city_pt(c, t, PROJ_S, "Saverne", 0, -46)
        p = clamp01((t - st - 0.8) / 3)
        map_path(c, PROJ_S, [CITY["Estrasburgo"], (7.55, 48.68), CITY["Saverne"]], p, AMBER, 6, [16, 10])
        show(c, t, tw("cinquenta", 211), 1200, 110, lambda c: hl(c, "~50 km", 0, 0, 52), anim="stamp")
        show(c, t, tw("tarde", 213), 1200, 900, lambda c: stitle(c, "mas era tarde demais", 0, 0, 52, INK, RED), anim="fade")
    HIST(c, t, [(0, "stand"), (st + 1, "point_r")], [(0, "worried")], x=250, s=0.85)


def s16(c, t):  # 215.9 - 228.0  na mesma rua, outras pessoas: uma, depois outra; mais de 30; espalhou pela cidade
    et = tw("espalhou", 225)
    street(c, t, 880, 0.6, seed=21)
    ft = tw("Primeiro", 220)
    dancer(c, t, 1000, 960, 0.75, t0=ft, fid=161, col=PEASANT[2], woman=False, appear=ft - 0.3)
    ot = tw("outra", 221)
    dancer(c, t, 1300, 960, 0.75, t0=ot, fid=162, col=PEASANT[3], appear=ot - 0.3)
    tt = tw("trinta", 222)
    dance_crowd(c, t, tt, 16, 960, 700, 1800, 2, 0.42, seed=4, d=1.2)
    show(c, t, 216.0, 1250, 100, lambda c: caption_box(c, "na mesma rua", 44), anim="up", t1=tt - 0.3)
    show(c, t, tt, 1250, 100, lambda c: hl(c, "mais de 30", 0, 0, 52), anim="stamp", t1=et - 0.3)
    if t > et:
        c.rectangle(0, 0, W, H); rgb(c, (0.03, 0.03, 0.04), 0.6 * fade_in(t, et, 0.5)); c.fill()
        rnd = random.Random(5)
        for i in range(24):
            x, y = rnd.uniform(700, 1800), rnd.uniform(250, 850)
            if t > et + i * 0.08:
                circle(c, x, y, 10, RED, 0); circle(c, x, y, 10 + ((t * 0.8 + i * 0.1) % 1) * 30, None, 2, RED)
        show(c, t, et, 1250, 100, lambda c: hl(c, "a dança se espalhou pela cidade", 0, 0, 44), anim="up")
    HIST(c, t, [(0, "stand"), (ot, "head")], [(0, "worried"), (ot, "shocked")], x=260, s=0.85)


def s17(c, t):  # 228.0 - 247.2  não era alegre: pulando, girando, braços para cima, socorro, olhos perdidos; pés
    street(c, t, 880, 0.5, seed=31)
    c.rectangle(0, 0, W, H); rgb(c, (0.03, 0.02, 0.03), 0.3); c.fill()
    show(c, t, 228.1, 1250, 100, lambda c: stitle(c, "não era uma dança alegre", 0, 0, 54, INK, RED), anim="up")
    for i in range(4):
        dancer(c, t, 820 + i * 260, 960, 0.75, t0=228.0, fid=170 + i, col=PEASANT[i], woman=bool(i % 2),
               exprs=((0, "desperate"),), period=0.45)
    so = tw("socorro", 235)
    show(c, t, so - 0.3, 1150, 460, lambda c: bubble(c, "socorro!", size=40, tx=-60, ty=80), anim="pop", t1=so + 3.0)
    show(c, t, tw("olhos", 236), 1500, 300, T("os olhos perdidos", 34, AMBER, HAND), anim="fade", t1=tw("Os", 240) - 0.2)
    show(c, t, tw("pareciam", 238), 1250, 210, T("pareciam não estar ali", 36, INK), anim="fade", t1=tw("Os", 240) - 0.2)
    pt = tw("Os", 240)
    show(c, t, pt, 1250, 210, lambda c: caption_box(c, "pés em carne viva... e não paravam", 40), anim="up")
    fog(c, t, 920, 0.08)
    HIST(c, t, [(0, "stand")], [(0, "shocked"), (pt, "sad")], x=250, s=0.85)


def council_room(c, t, lit=0.8):
    c.rectangle(0, 0, W, H); rgb(c, (0.08, 0.07, 0.07)); c.fill()
    for x in (700, 1800):
        c.rectangle(x - 30, 0, 60, 900); fs(c, (0.14, 0.12, 0.11), 4, (0.30, 0.26, 0.22))
    for k in range(3):
        x = 960 + k * 260
        c.move_to(x - 60, 520); c.line_to(x - 60, 260); c.curve_to(x - 60, 180, x + 60, 180, x + 60, 260)
        c.line_to(x + 60, 520); c.close_path(); fs(c, (0.10, 0.12, 0.18), 4, (0.36, 0.30, 0.26))
    glow(c, 1250, 400, 500, AMBER, 0.08 * lit)


def council_table(c):
    c.rectangle(860, 900, 760, 34); fs(c, WOOD, 5)
    c.rectangle(880, 934, 720, 90); fs(c, (0.20, 0.14, 0.10), 4, WOOD_D)
    c.rectangle(1180, 950, 120, 50); fs(c, (0.62, 0.12, 0.10), 3)


def s18(c, t):  # 247.2 - 261.5  diante de dezenas, o conselho precisava agir; ouviu os religiosos: vingança de S. Vito
    council_room(c, t)
    for i in range(3):
        councilor(c, t, 1040 + i * 200, 1000, 0.72, poses=((0, "think" if i == 1 else "stand"),),
                  exprs=((0, "worried"),), fid=180 + i, appear=247.5 + i * 0.25)
    council_table(c)
    show(c, t, tw("conselho", 248), 1250, 100, lambda c: hl(c, "o conselho de Estrasburgo", 0, 0, 46), anim="up", t1=tw("primeiro", 254) - 0.2)
    rt = tw("religiosos", 255)
    priest(c, t, 1730, 1000, 0.7, poses=((0, "stand"), (tw("vingança", 258), "point_lu")), exprs=((0, "angry"),), fid=185, appear=rt - 0.3)
    show(c, t, rt, 1250, 100, lambda c: hl(c, "primeiro, os religiosos", 0, 0, 46), anim="up")
    show(c, t, tw("vingança", 258) - 0.2, 1500, 330, lambda c: bubble(c, "vingança de São Vito!", size=36, tx=80, ty=90), anim="pop")
    HIST(c, t, [(0, "stand")], [(0, "neutral")], x=260, s=0.85)


def s19(c, t):  # 261.5 - 280.3  médicos discordaram: doença natural, sangue quente demais; dançar até o mal sair
    council_room(c, t)
    dt = tw("médicos", 261)
    doctor(c, t, 1100, 1000, 0.75, poses=((0, "stand"), (tw("disseram", 263), "present")), exprs=((0, "confident"),), fid=190, appear=dt - 0.2)
    doctor(c, t, 1300, 1000, 0.7, poses=((0, "think"),), exprs=((0, "neutral"),), fid=191, appear=dt + 0.2)
    council_table(c)
    show(c, t, dt, 1250, 100, lambda c: hl(c, "os médicos discordaram", 0, 0, 46), anim="up", t1=tw("propuseram", 270) - 0.2)
    show(c, t, tw("maldição", 264), 1600, 300, lambda c: (text(c, "maldição", 0, 0, 38, TYPE, INK), big_x(c, 50, RED, 10)), anim="pop", t1=tw("propuseram", 270) - 0.2)
    qt = tw("quente", 267)
    show(c, t, tw("natural", 266) - 0.2, 1600, 450, T("doença natural", 38, AMBER, HAND), anim="fade", t1=tw("propuseram", 270) - 0.2)
    if t > qt - 0.3:
        put(c, 1640, 640, lambda c: (c.scale(0.7, 0.7), flames(c, t, 160, 140)), 1.0, fade_in(t, qt - 0.3) * fade_out(t, 279.5))
        show(c, t, qt, 1640, 720, T("sangue quente", 38, RED, TYPE), anim="fade", t1=279.5)
    pt = tw("propuseram", 270)
    show(c, t, pt, 1250, 100, lambda c: hl(c, "o tratamento", 0, 0, 48), anim="up")
    tt = tw("deixar", 276)
    show(c, t, tt, 1250, 220, lambda c: caption_box(c, "dançar até o mal sair do corpo", 42), anim="up")
    HIST(c, t, [(0, "stand"), (tt, "shrug")], [(0, "neutral"), (tt, "shocked")], x=260, s=0.85)


def s20(c, t):  # 280.3 - 304.0  conselho concordou: salões das corporações, palcos nos mercados, músicos, homens fortes
    gt = tw("corporações", 281)
    pt = tw("Montaram", 288)
    mt = tw("pagou", 292)
    ht = tw("contratou", 298)
    street(c, t, 900, 0.9, seed=41, n=6)
    show(c, t, 280.4, 1250, 100, lambda c: hl(c, "e o conselho concordou", 0, 0, 46), anim="up", t1=gt - 0.2)
    if t < pt - 0.2:
        put(c, 1250, 900, lambda c: half_timber(c, 520, 380, seed=4, lit=1.0), 1.0, fade_in(t, gt - 0.3))
        show(c, t, gt, 1250, 100, lambda c: hl(c, "salões dos carpinteiros e curtidores", 0, 0, 42), anim="up")
        show(c, t, tw("pistas", 285), 1250, 360, T("viraram pistas de dança", 36, AMBER, HAND), anim="fade")
        music_notes(c, t, 1250, 420, 3, AMBER, 160) if t > tw("pistas", 285) else None
    else:
        put(c, 1050, 960, lambda c: stage(c, 520, 100), 1.0, fade_in(t, pt - 0.2, 0.4))
        put(c, 1600, 960, lambda c: stage(c, 360, 80), 1.0, fade_in(t, tw("outro", 289) - 0.2, 0.4))
        show(c, t, tw("cavalos", 289), 1050, 1020, T("mercado de cavalos", 30, INK), anim="fade")
        show(c, t, tw("grãos", 290), 1600, 1020, T("mercado de grãos", 30, INK), anim="fade")
        show(c, t, pt, 1250, 100, lambda c: hl(c, "palcos nas praças", 0, 0, 46), anim="up", t1=mt - 0.2)
        if t > mt - 0.3:
            show(c, t, mt, 1250, 100, lambda c: hl(c, "músicos dia e noite", 0, 0, 46), anim="up", t1=ht - 0.2)
            for i, (fn, tt) in enumerate(((sc(drum, t, s=0.45), tw("tambores", 292)), (sc(flute, s=0.6), tw("flautas", 293)),
                                          (sc(trumpet, s=0.5), tw("cornetas", 293)))):
                show(c, t, tt - 0.2, 1500 + i * 120, 520 + (i % 2) * 60, fn, anim="pop")
            music_notes(c, t, 1300, 450, 5, AMBER, 220)
        for i in range(3):
            dancer(c, t, 900 + i * 150, 860, 0.5, t0=pt, fid=200 + i, col=PEASANT[i + 1], woman=bool(i % 2), appear=pt + i * 0.2)
        if t > ht - 0.3:
            show(c, t, ht, 1250, 100, lambda c: hl(c, "e homens fortes para segurá-los", 0, 0, 44), anim="up")
            man(c, t, 1560, 860, 0.6, poses=((0, "hold"),), exprs=((0, "neutral"),), col=(0.24, 0.22, 0.20), fid=210, appear=ht)
            dancer(c, t, 1680, 860, 0.5, t0=ht, fid=211, col=PEASANT[4], appear=ht + 0.2, exprs=((0, "desperate"),))
    fog(c, t, 960, 0.07)
    HIST(c, t, [(0, "stand"), (mt, "head")], [(0, "worried"), (mt, "shocked")], x=250, s=0.85)


def s21(c, t):  # 304.0 - 321.2  foi um desastre: atraiu mais gente; mais viam, mais dançavam; agosto: ~400
    street(c, t, 880, 0.9, seed=43, n=8)
    show(c, t, 304.1, 1250, 100, lambda c: stitle(c, "foi um desastre", 0, 0, 62, INK, RED), anim="stamp", t1=tw("Em", 313) - 0.3)
    dance_crowd(c, t, 305.5, 46, 960, 640, 1820, 4, 0.42, seed=12, d=8.0)
    at_ = tw("agosto", 313)
    show(c, t, at_, 1250, 100, lambda c: date_stamp(c, "AGOSTO DE 1518", 52, AMBER), anim="stamp")
    nt = tw("quatrocentas", 315)
    show(c, t, nt - 0.2, 1250, 300, lambda c: (rrect(c, -230, -110, 460, 220, 18), fs(c, (0.08, 0.07, 0.08), 5, AMBER),
                                               counter(c, "~400", "pessoas, segundo uma crônica")), anim="pop")
    fog(c, t, 960, 0.08)
    HIST(c, t, [(0, "head")], [(0, "shocked")], x=250, s=0.85)


def s22(c, t):  # 321.2 - 325.1  a cura tinha virado combustível
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.03, 0.02)); c.fill()
    glow(c, 1150, 760, 520, ORANGE, 0.18)
    put(c, 1150, 900, lambda c: (c.scale(1.3, 1.3), flames(c, t, 220, 200)), 1.0, fade_in(t, 321.3))
    for i in range(5):
        mini_dancer(c, t, 860 + i * 140, 1000, 0.4, seed=i + 30)
    show(c, t, 321.3, 1150, 220, lambda c: stitle(c, "a cura virou combustível", 0, 0, 62, INK, ORANGE), anim="fade")
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=260, s=0.85)


def s23(c, t):  # 325.1 - 336.5  meio de agosto: desmontar palcos; proibir dança e música até o fim de setembro
    council_room(c, t)
    show(c, t, 325.2, 1250, 100, lambda c: hl(c, "meados de agosto: o conselho volta atrás", 0, 0, 42), anim="up")
    dt = tw("desmontar", 328)
    show(c, t, dt - 0.3, 900, 500, sc(stage, 300, 70), anim="pop")
    x_over(c, t, dt + 0.4, 900, 470, 70)
    pt = tw("Proibiu", 330)
    show(c, t, pt, 1250, 470, sc(drum, t, False, s=0.6), anim="pop")
    show(c, t, pt + 0.3, 1550, 470, sc(trumpet, s=0.6), anim="pop")
    x_over(c, t, tw("música", 332), 1250, 470, 70)
    x_over(c, t, tw("música", 332) + 0.2, 1550, 470, 70)
    show(c, t, tw("setembro", 334), 1250, 760, lambda c: date_stamp(c, "PROIBIDO ATÉ O FIM DE SETEMBRO", 44, RED), anim="stamp")
    HIST(c, t, [(0, "point_r")], [(0, "neutral")], x=260, s=0.85)


def s24(c, t):  # 336.5 - 359.9  Sebastian Brant, A Nau dos Insensatos; exceção: cordas em casamentos e missas novas
    council_room(c, t, 0.6)
    bt = tw("Sebastian", 340)
    man(c, t, 1000, 1000, 0.8, poses=((0, "stand"), (bt + 1, "present")), exprs=((0, "confident"),), col=COUNCIL,
        fid=220, appear=bt - 0.3, hat_col=(0.10, 0.08, 0.10))
    show(c, t, bt, 1000, 470, lambda c: label_card(c, "chanceler da cidade", "Sebastian Brant"), anim="up", t1=tw("exceção", 349) - 0.2)
    nt = tw("Nau", 341)
    show(c, t, nt - 0.2, 1450, 600, lambda c: (book(c, "", (0.30, 0.22, 0.14)), c.save(), c.translate(0, -10), c.scale(0.22, 0.22),
                                               brigantine(c, 0, 0.0, None), c.restore()), anim="pop", t1=tw("exceção", 349) - 0.2)
    show(c, t, nt + 0.6, 1450, 820, T("A Nau dos Insensatos (1494)", 32, AMBER), anim="fade", t1=tw("exceção", 349) - 0.2)
    et = tw("exceção", 349)
    show(c, t, et, 1300, 100, lambda c: hl(c, "a exceção", 0, 0, 48), anim="up")
    show(c, t, tw("casamentos", 352), 1350, 330, T("casamentos e missas novas", 34, INK, HAND), anim="fade")
    ct = tw("corda", 355)
    show(c, t, ct - 0.4, 1250, 590, sc(fiddle, s=0.9), anim="pop")
    show(c, t, ct, 1250, 760, lambda c: check(c, 1.2), anim="pop")
    tt = tw("tambores", 357)
    show(c, t, tt - 0.2, 1600, 600, sc(drum, t, False, s=0.6), anim="pop")
    x_over(c, t, tt + 0.3, 1600, 600, 70)
    HIST(c, t, [(0, "stand")], [(0, "neutral"), (tt, "think")], x=250, s=0.85)


def s25(c, t):  # 359.9 - 376.6  os religiosos tinham razão; só São Vito podia acabar; proibiu jogo, prostituição; missas
    c.rectangle(0, 0, W, H); rgb(c, (0.06, 0.05, 0.05)); c.fill()
    glow(c, 1250, 520, 520, AMBER, 0.10)
    put(c, 1250, 920, lambda c: saint_statue(c, t, True), 1.0, fade_in(t, 360.0))
    show(c, t, 360.1, 1250, 100, lambda c: hl(c, "afinal, os religiosos tinham razão?", 0, 0, 44), anim="up", t1=tw("Se", 365) - 0.2)
    show(c, t, tw("Se", 365), 1250, 100, lambda c: hl(c, "só São Vito podia acabar com aquilo", 0, 0, 44), anim="up", t1=tw("proibiu", 370) - 0.2)
    pt = tw("proibiu", 370)
    labs = (("jogo", tw("jogo", 370)), ("prostituição", tw("prostituição", 370)), ("outros pecados", tw("pecados", 370)))
    for i, (s, tt) in enumerate(labs):
        show(c, t, tt - 0.1, 1640, 300 + i * 100, T(s, 46, INK, HAND), anim="left")
        show(c, t, tt + 0.3, 1640, 300 + i * 100, lambda c, s=s: line(c, -text_w(c, s, 46, HAND) / 2 - 10, 0, text_w(c, s, 46, HAND) / 2 + 10, 0, 6, RED), anim="fade")
    show(c, t, pt, 1250, 100, lambda c: hl(c, "a cidade proibiu", 0, 0, 46), anim="up", t1=tw("missas", 374) - 0.2)
    mt = tw("missas", 374)
    for i in range(5):
        show(c, t, mt + i * 0.12, 880 + i * 90 + (i > 2) * 440, 900, sc(candle, t, s=0.8), anim="pop")
    show(c, t, mt, 1250, 100, lambda c: hl(c, "missas pelos dançarinos", 0, 0, 46), anim="up")
    HIST(c, t, [(0, "think")], [(0, "neutral")], x=250, s=0.85)


def s26(c, t):  # 376.6 - 387.7  os casos mais graves em carroças até o santuário de S. Vito perto de Saverne; até 3 dias
    night(c, t, 600, (1680, 140))
    put(c, 1500, 900, lambda c: mountains(c, 1300, 220, False, (0.16, 0.18, 0.17)), 1.0)
    put(c, 1560, 690, lambda c: (c.scale(0.5, 0.5), cathedral(c, 300, (0.36, 0.30, 0.26), lit=1.0)), 1.0)
    c.rectangle(0, 900, W, H - 900); rgb(c, (0.10, 0.10, 0.09)); c.fill()
    line(c, 0, 960, W, 940, 4, (0.30, 0.28, 0.24))
    k = (t - 376.6) / 11
    for j in range(2):
        x = 560 + k * 600 + j * 520
        put(c, x + 290, 960, lambda c: horse(c), 0.85)
        put(c, x, 960, lambda c: cart(c, t, 300, True, cover=True), 0.9)
    show(c, t, 376.8, 1150, 100, lambda c: hl(c, "os casos mais graves: carroças até Saverne", 0, 0, 42), anim="up")
    show(c, t, tw("santuário", 378), 1560, 520, T("santuário de São Vito", 32, AMBER), anim="fade")
    show(c, t, tw("três", 385) - 0.2, 1150, 220, lambda c: date_stamp(c, "ATÉ 3 DIAS DE VIAGEM", 44, AMBER), anim="stamp")
    fog(c, t, 960, 0.09)
    HIST(c, t, [(0, "stand")], [(0, "neutral")], x=240, s=0.8)


def chapel(c, t):
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.04, 0.04)); c.fill()
    for x in (720, 1780):
        c.move_to(x - 70, 1000); c.line_to(x - 70, 300); c.curve_to(x - 70, 160, x + 70, 160, x + 70, 300); c.line_to(x + 70, 1000)
        rgb(c, (0.22, 0.20, 0.18)); c.set_line_width(6); c.stroke()
    glow(c, 1250, 500, 520, AMBER, 0.12)
    smoke(c, t, 1430, 900, 520, 0.18, 2)


def s27(c, t):  # 387.7 - 399.9  o ritual: diante da imagem; pequenas cruzes nas mãos; sapatos vermelhos
    chapel(c, t)
    put(c, 1250, 860, lambda c: saint_statue(c, t, True), 0.95)
    show(c, t, 387.8, 1250, 100, lambda c: hl(c, "o ritual", 0, 0, 50), anim="up")
    priest(c, t, 1560, 1000, 0.7, poses=((0, "present_l"),), exprs=((0, "neutral"),), fid=230, appear=tw("padres", 390))
    woman(c, t, 980, 1000, 0.65, poses=((0, "hold"),), exprs=((0, "sad"),), col=PEASANT[2], fid=231, appear=tw("diante", 391))
    ct = tw("cruzes", 394)
    show(c, t, ct - 0.2, 980, 820, sc(wood_cross, 70), anim="pop")
    show(c, t, ct, 1250, 220, T("pequenas cruzes nas mãos", 34, INK, HAND), anim="fade", t1=tw("calçavam", 397) - 0.2)
    rt = tw("vermelhos", 398)
    show(c, t, rt - 0.4, 1250, 980, lambda c: red_shoes(c, False, glow_on=True), anim="pop")
    show(c, t, rt, 1250, 220, lambda c: stitle(c, "sapatos vermelhos", 0, 0, 56, INK, RED), anim="fade")
    HIST(c, t, [(0, "stand")], [(0, "neutral")], x=240, s=0.8)


def s28(c, t):  # 399.9 - 411.2  água benta, cruzes de óleo, em cima e embaixo; incenso; orações em latim
    chapel(c, t)
    ct = tw("marcados", 401)
    put(c, 1150, 640, lambda c: red_shoes(c, t > ct + 0.6, glow_on=True), 2.2)
    at_ = tw("água", 400)
    if t > at_:
        for i in range(10):
            ph = ((t - at_) * 1.4 + i * 0.13) % 1
            if t < at_ + 5:
                circle(c, 1050 + i * 22, 300 + ph * 280, 6, (0.60, 0.78, 0.95), 0)
    show(c, t, at_ - 0.2, 1150, 100, lambda c: hl(c, "água benta", 0, 0, 46), anim="up", t1=ct - 0.2)
    show(c, t, ct, 1150, 100, lambda c: hl(c, "cruzes de óleo consagrado", 0, 0, 46), anim="up", t1=tw("Tudo", 407) - 0.2)
    show(c, t, tw("cima", 404), 1150, 900, T("em cima e embaixo", 36, AMBER, HAND), anim="fade", t1=tw("Tudo", 407) - 0.2)
    it = tw("incenso", 407)
    if t > it - 0.5:
        smoke(c, t, 900, 900, 600, 0.22 * fade_in(t, it - 0.5), 5)
        smoke(c, t, 1450, 900, 600, 0.22 * fade_in(t, it - 0.5), 7)
    show(c, t, tw("Tudo", 407), 1150, 100, lambda c: hl(c, "incenso e orações em latim", 0, 0, 46), anim="up")
    show(c, t, tw("latim", 409), 1150, 900, T("Sancte Vite, ora pro nobis", 36, INK, SERIF), anim="fade")
    HIST(c, t, [(0, "stand")], [(0, "neutral")], x=240, s=0.8)


def s29(c, t):  # 411.2 - 428.6  a coisa mais estranha: funcionou (ou parecia); dançarinos caíram; começo de setembro, acabou
    street(c, t, 880, 0.5, seed=51)
    ft = tw("Funcionou", 414)
    show(c, t, 411.3, 1250, 100, lambda c: hl(c, "a coisa mais estranha", 0, 0, 46), anim="up", t1=ft - 0.2)
    show(c, t, ft, 1250, 100, lambda c: stitle(c, "funcionou", 0, 0, 72, INK, AMBER), anim="stamp", t1=tw("Nas", 418) - 0.2)
    show(c, t, tw("menos", 416), 1250, 210, T("(ou pelo menos parecia)", 36, LGRAY), anim="fade", t1=tw("Nas", 418) - 0.2)
    nt = tw("Nas", 418)
    n = 30 if t < nt else max(1, int(30 - (t - nt) * 4.5))
    dance_crowd(c, t, 0, n, 960, 700, 1820, 3, 0.42, seed=12, d=0.01)
    st = tw("setembro", 422)
    show(c, t, nt, 1250, 100, lambda c: hl(c, "nas semanas seguintes, menos dançarinos", 0, 0, 42), anim="up", t1=st - 0.4)
    show(c, t, st - 0.3, 1250, 100, lambda c: date_stamp(c, "COMEÇO DE SETEMBRO", 52, AMBER), anim="stamp")
    show(c, t, tw("repente", 426), 1250, 210, T("tão de repente quanto começou", 36, INK), anim="fade")
    fog(c, t, 940, 0.08)
    HIST(c, t, [(0, "stand"), (ft, "shrug")], [(0, "neutral"), (ft, "shocked"), (st, "think")], x=250, s=0.85)


def s30(c, t):  # 428.6 - 443.5  as fontes: conselho, sermões, crônicas de famílias, Daniel Specklin
    c.rectangle(0, 0, W, H); rgb(c, (0.07, 0.06, 0.06)); c.fill()
    glow(c, 1250, 540, 600, AMBER, 0.08)
    show(c, t, 428.7, 1250, 100, lambda c: hl(c, "como a gente sabe disso?", 0, 0, 48), anim="up")
    docs = [("anotações do conselho", tw("anotações", 430), lambda c: (chronicle(c, 200, 260, "", 31), sc(council_seal, 30, s=1)(c))),
            ("sermões da catedral", tw("sermões", 432), lambda c: chronicle(c, 200, 260, "", 32)),
            ("crônicas de famílias", tw("crônicas", 434), lambda c: chronicle(c, 200, 260, "", 33)),
            ("Daniel Specklin", tw("Daniel", 436), lambda c: (chronicle(c, 200, 260, "", 34), c.save(), c.translate(60, 60), quill(c), c.restore()))]
    for i, (s, tt, fn) in enumerate(docs):
        x = 760 + i * 300
        show(c, t, tt - 0.2, x, 480, fn, anim="up")
        show(c, t, tt, x, 680, T(s, 28, INK, HAND), anim="fade")
    show(c, t, tw("décadas", 436), 1210, 850, T("arquiteto que copiou os registros do conselho", 32, AMBER), anim="fade")
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=250, s=0.85)


def s31(c, t):  # 443.5 - 451.4  quantas pessoas morreram? separar fato da lenda
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.04, 0.05)); c.fill()
    show(c, t, 443.6, 1250, 450, sc(big_q, 260, AMBER), anim="pop", t1=tw("separar", 448) - 0.3)
    show(c, t, tw("quantas", 446), 1250, 820, lambda c: stitle(c, "quantas pessoas morreram?", 0, 0, 56, INK, RED), anim="fade")
    st = tw("separar", 448)
    show(c, t, st, 1000, 430, lambda c: (rrect(c, -170, -70, 340, 140, 14), fs(c, (0.12, 0.12, 0.13), 5, (0.45, 0.72, 0.42)),
                                         text(c, "FATO", 0, 0, 60, SERIF, INK)), anim="left")
    show(c, t, st + 0.5, 1500, 430, lambda c: (rrect(c, -170, -70, 340, 140, 14), fs(c, (0.12, 0.12, 0.13), 5, RED),
                                               text(c, "LENDA", 0, 0, 60, SERIF, INK)), anim="right")
    HIST(c, t, [(0, "think")], [(0, "think")], x=260, s=0.9)


def s32(c, t):  # 451.4 - 473.4  internet: 15 por dia, mais de 100; vem de relatos posteriores; registros não falam de mortes
    c.rectangle(0, 0, W, H); rgb(c, (0.06, 0.05, 0.06)); c.fill()
    mt = tw("Mas", 457)
    def screen(c):
        text(c, "\"15 mortes por dia\"", 0, -50, 36, TYPE, INK)
        text(c, "\"mais de 100 mortos\"", 0, 20, 36, TYPE, INK)
    show(c, t, 451.5, 900, 470, sc(monitor, screen, 520, 300), anim="pop")
    show(c, t, 451.6, 900, 200, T("na internet", 36, AMBER), anim="fade")
    show(c, t, mt + 0.3, 900, 720, lambda c: date_stamp(c, "RELATOS POSTERIORES", 40, RED), anim="stamp")
    rt = tw("registros", 461)
    show(c, t, rt - 0.2, 1500, 520, lambda c: (chronicle(c, 340, 470, "Registros de 1518", 61)), anim="up")
    items = [("dança", tw("dança", 462)), ("música", tw("música", 462)), ("palcos", tw("palcos", 462)), ("Saverne", tw("Saverne", 462))]
    for i, (s, tt) in enumerate(items):
        show(c, t, tt - 0.1, 1460, 400 + i * 70, lambda c, s=s: (rrect(c, -150, -28, 300, 56, 8), fs(c, PARCH, 0),
                                                              text(c, s, 20, 0, 32, TYPE, DARKTXT), c.save(), c.translate(-110, 0), check(c, 0.5), c.restore()), anim="pop")
    ft = tw("mortes", 470)
    show(c, t, ft - 0.2, 1460, 700, lambda c: (rrect(c, -150, -28, 300, 56, 8), fs(c, PARCH, 0),
                                               text(c, "mortes: --", 20, 0, 32, TYPE, RED)), anim="stamp")
    HIST(c, t, [(0, "point_r"), (rt, "present")], [(0, "neutral"), (ft, "think")], x=250, s=0.85)


def s33(c, t):  # 473.4 - 487.8  possível: exaustão, infarto, derrame; quantas ninguém sabe; poucas ou nenhuma
    street(c, t, 880, 0.3, seed=61)
    c.rectangle(0, 0, W, H); rgb(c, (0.02, 0.02, 0.03), 0.35); c.fill()
    man(c, t, 1250, 960, 0.8, poses=((0, "slump"),), exprs=((0, "sad"),), col=PEASANT[2], fid=240)
    show(c, t, 473.5, 1250, 100, lambda c: hl(c, "é possível que alguns tenham morrido", 0, 0, 42), anim="up", t1=tw("quantas", 481) - 0.2)
    for i, (s, w) in enumerate((("exaustão", "exaustão"), ("infarto", "infarto"), ("derrame", "derrame"))):
        show(c, t, tw(w, 474), 850 + i * 400, 330, lambda c, s=s: caption_box(c, s, 40), anim="pop")
    show(c, t, tw("calor", 479), 1250, 440, T("no calor do verão", 38, AMBER), anim="fade", t1=tw("quantas", 481) - 0.2)
    qt = tw("quantas", 481)
    show(c, t, qt, 1250, 100, lambda c: stitle(c, "quantas? ninguém sabe", 0, 0, 58, INK, AMBER), anim="up")
    show(c, t, tw("poucas", 483), 1250, 220, T("talvez poucas, ou nenhuma", 38, INK), anim="fade")
    fog(c, t, 940, 0.08)
    HIST(c, t, [(0, "stand"), (qt, "shrug")], [(0, "sad"), (qt, "think")], x=250, s=0.85)


def s34(c, t):  # 487.8 - 503.1  o certo: quase dois meses, centenas dançaram contra a vontade; ninguém soube dizer por quê
    street(c, t, 880, 0.7, seed=71, n=6)
    c.rectangle(0, 0, W, H); rgb(c, (0.02, 0.02, 0.03), 0.45); c.fill()
    show(c, t, 487.9, 1150, 100, lambda c: hl(c, "o que é certo", 0, 0, 48), anim="up", t1=tw("durante", 489) - 0.2)
    dt = tw("durante", 489)
    show(c, t, dt, 900, 300, sc(calendar, "JUL", s=0.9), anim="pop")
    show(c, t, dt + 0.3, 1150, 300, sc(calendar, "AGO", s=0.9), anim="pop")
    show(c, t, dt + 0.6, 1400, 300, sc(calendar, "SET", s=0.9), anim="pop")
    show(c, t, dt, 1150, 100, lambda c: hl(c, "quase dois meses", 0, 0, 48), anim="up", t1=tw("nem", 497) - 0.2)
    dance_crowd(c, t, tw("centenas", 489), 26, 960, 640, 1500, 3, 0.42, seed=17, d=2.0)
    nt = tw("nem", 497)
    for i, (who, w) in enumerate((("médicos", "médicos"), ("padres", "padres"), ("conselho", "conselho"))):
        show(c, t, tw(w, 497), 850 + i * 400, 520, lambda c, who=who: (caption_box(c, who, 40), c.translate(0, -50), big_x(c, 26, RED, 8)), anim="pop")
    show(c, t, tw("dizer", 500), 1150, 100, lambda c: stitle(c, "ninguém soube dizer por quê", 0, 0, 52, INK, AMBER), anim="up")
    fog(c, t, 940, 0.08)
    HIST(c, t, [(0, "present"), (nt, "shrug")], [(0, "neutral"), (nt, "think")], x=250, s=0.85)


PROJ_W = make_proj(3.0, 12.6, 46.9, 52.9)


def s35(c, t):  # 503.1 - 529.4  Estrasburgo não foi a primeira; 1374 Aachen, vale do Reno: Colônia, Metz, Utrecht, Estrasburgo
    if t < tw("Em", 507):
        c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.04, 0.05)); c.fill()
        show(c, t, 503.2, 1150, 470, lambda c: stitle(c, "não foi a primeira", 0, 0, 80, INK, AMBER), anim="fade")
        HIST(c, t, [(0, "finger_up")], [(0, "think")], x=260, s=0.9)
        return
    rhine_map(c, t, PROJ_W, 1.0, moselle=True)
    show(c, t, 507.8, 1300, 100, lambda c: date_stamp(c, "1374", 64, AMBER), anim="stamp")
    at_ = tw("Aachen", 509)
    city_pt(c, t, PROJ_W, "Aachen", -10, -40) if t > at_ else None
    order = [("Colônia", tw("Colônia", 516), 0, -40), ("Metz", tw("Metz", 516), 0, 44), ("Utrecht", tw("Utrecht", 516), 0, -40),
             ("Estrasburgo", tw("Estrasburgo", 518), 0, 44)]
    for name, tt, dx, dy in order:
        if t > tt - 0.2:
            map_path(c, PROJ_W, [CITY["Aachen"], CITY[name]], clamp01((t - tt + 0.2) / 0.8), RED, 4, [12, 8])
            city_pt(c, t, PROJ_W, name, dx, dy, RED)
    show(c, t, tw("desceu", 511), 0, 0, lambda c: map_label(c, PROJ_W, 9.3, 50.6, "vale do Reno", 32, (0.55, 0.72, 0.88)), anim="fade")
    show(c, t, tw("Os", 521), 1300, 960, lambda c: caption_box(c, "grupos dançando de cidade em cidade", 40), anim="up")
    HIST(c, t, [(0, "point_r")], [(0, "neutral")], x=240, s=0.8)


def s36(c, t):  # 529.4 - 545.0  1237: crianças dançando de Erfurt a Arnstadt, 20 km; flautista de Hamelin
    ht = tw("flautista", 540)
    if t < ht - 0.4:
        c.rectangle(0, 0, W, H); rgb(c, (0.08, 0.09, 0.08)); c.fill()
        night(c, t, 500, (1700, 140), 60)
        c.rectangle(0, 860, W, H - 860); rgb(c, (0.10, 0.11, 0.09)); c.fill()
        line(c, 0, 900, W, 880, 4, (0.32, 0.30, 0.26))
        show(c, t, 529.6, 1200, 100, lambda c: date_stamp(c, "1237", 64, AMBER), anim="stamp")
        show(c, t, tw("crônica", 530), 1200, 200, T("segundo uma crônica", 34, LGRAY), anim="fade")
        k = (t - 530) / 10
        for i in range(9):
            mini_dancer(c, t, 700 + i * 90 + k * 260, 940 + (i % 2) * 14, 0.30, seed=i + 50,
                        col=[(0.62, 0.42, 0.30), (0.40, 0.52, 0.40), (0.52, 0.40, 0.56)][i % 3])
        show(c, t, tw("Erfurt", 532), 760, 760, T("Erfurt", 38, INK, TYPE), anim="fade")
        show(c, t, tw("Arnstadt", 535), 1700, 760, T("Arnstadt", 38, INK, TYPE), anim="fade")
        show(c, t, tw("vinte", 536), 1230, 760, lambda c: (line(c, -300, 0, 300, 0, 3, AMBER), text(c, "~20 km", 0, -34, 34, TYPE, AMBER)), anim="fade")
    else:
        c.rectangle(0, 0, W, H); rgb(c, (0.06, 0.05, 0.06)); c.fill()
        glow(c, 1250, 520, 400, AMBER, 0.12)
        man(c, t, 1150, 960, 0.9, poses=((0, "hold"),), exprs=((0, "happy"),), col=(0.62, 0.22, 0.18), fid=250, hat="beret",
            hat_col=(0.30, 0.50, 0.30))
        put(c, 1150, 760, lambda c: flute(c), 0.8)
        music_notes(c, t, 1250, 560, 4, AMBER, 140)
        for i in range(5):
            mini_dancer(c, t, 1350 + i * 90, 990, 0.3, seed=i + 60, col=[(0.62, 0.42, 0.30), (0.40, 0.52, 0.40)][i % 2])
        show(c, t, ht, 1250, 120, lambda c: hl(c, "a lenda do flautista de Hamelin", 0, 0, 46), anim="up")
    HIST(c, t, [(0, "stand")], [(0, "neutral")], x=250, s=0.85)


def s37(c, t):  # 545.0 - 562.1  entre 1374 e 1518, mais de 10 surtos; quase todos no Reno e no Mosela; maldição de S. Vito
    rhine_map(c, t, PROJ_W, 1.0, moselle=True)
    show(c, t, 545.1, 1300, 100, lambda c: hl(c, "1374-1518: mais de 10 surtos", 0, 0, 46), anim="up")
    pts = [(6.08, 50.78), (6.96, 50.94), (6.18, 49.12), (5.12, 52.09), (7.75, 48.58), (7.59, 47.56), (8.27, 50.00),
           (6.64, 49.75), (7.60, 50.36), (6.77, 51.23), (7.10, 50.73)]
    st = tw("surtos", 546)
    for i, (lo, la) in enumerate(pts):
        if t > st + i * 0.25:
            map_point(c, PROJ_W, lo, la, RED, 9, t + i * 0.3)
    rt = tw("rios", 552)
    show(c, t, rt, 0, 0, lambda c: (map_label(c, PROJ_W, 9.0, 50.8, "Reno", 40, (0.55, 0.72, 0.88), SERIF),
                                    map_label(c, PROJ_W, 5.7, 49.6, "Mosela", 36, (0.55, 0.72, 0.88), SERIF)), anim="fade")
    if t > rt:
        glow(c, *PROJ_W(7.0, 50.0), 420, (0.55, 0.72, 0.88), 0.10 * fade_in(t, rt))
    show(c, t, tw("Justamente", 557), 1300, 960, lambda c: caption_box(c, "onde temiam a maldição de São Vito", 40), anim="up")
    HIST(c, t, [(0, "point_r")], [(0, "neutral")], x=240, s=0.8)


def s38(c, t):  # 562.1 - 566.6  então, o que fez centenas dançarem até cair?
    street(c, t, 880, 0.3, seed=81)
    c.rectangle(0, 0, W, H); rgb(c, (0.02, 0.02, 0.03), 0.45); c.fill()
    dance_crowd(c, t, 0, 18, 960, 700, 1800, 2, 0.42, seed=19, d=0.01)
    show(c, t, 562.2, 1250, 120, lambda c: stitle(c, "o que fez centenas dançarem até cair?", 0, 0, 50, INK, AMBER), anim="fade")
    show(c, t, 562.8, 1250, 470, sc(big_q, 200, AMBER), anim="pop")
    HIST(c, t, [(0, "think")], [(0, "think")], x=260, s=0.9)


def s39(c, t):  # 566.6 - 587.4  teoria 1: veneno; esporão do centeio; parecido com LSD; convulsões...; Fogo de Santo Antônio
    c.rectangle(0, 0, W, H); rgb(c, (0.07, 0.06, 0.05)); c.fill()
    show(c, t, 566.7, 1250, 100, lambda c: hl(c, "teoria 1: veneno", 0, 0, 50), anim="up")
    et = tw("esporão", 568)
    for i in range(3):
        put(c, 860 + i * 120, 920, lambda c, i=i: (c.rotate(-0.1 + i * 0.1), rye(c, True, 380, i + 2)), 1.0, fade_in(t, et - 0.3 + i * 0.15))
    show(c, t, et, 980, 300, T("esporão do centeio (fungo)", 34, AMBER), anim="fade")
    show(c, t, tw("pão", 570), 1250, 820, sc(bread, (0.40, 0.32, 0.26), s=1.0), anim="pop")
    st = tw("substâncias", 574)
    show(c, t, st, 1580, 330, lambda c: caption_box(c, "parecido com o LSD", 38), anim="up")
    for i, w in enumerate(("convulsões", "alucinações", "espasmos")):
        show(c, t, tw(w, 575), 1580, 460 + i * 80, T(w, 44, INK, HAND), anim="left")
    ft = tw("Fogo", 582)
    if t > ft - 0.3:
        put(c, 1580, 840, lambda c: flames(c, t, 200, 150), 1.0, fade_in(t, ft - 0.3))
        show(c, t, ft, 1580, 920, T("Fogo de Santo Antônio", 34, ORANGE), anim="fade")
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=250, s=0.85)


def s40(c, t):  # 587.4 - 611.8  John Waller descarta: fungo corta a circulação; não dançariam por dias; não explica o mesmo
    c.rectangle(0, 0, W, H); rgb(c, (0.07, 0.06, 0.06)); c.fill()
    wt = tw("John", 587)
    show(c, t, wt, 1250, 120, lambda c: label_card(c, "historiador", "John Waller"), anim="up", t1=tw("fungo", 593) - 0.2)
    show(c, t, tw("livro", 588), 1250, 420, lambda c: (book(c, "1518", (0.30, 0.18, 0.14))), anim="pop", t1=tw("fungo", 593) - 0.2)
    show(c, t, tw("descarta", 588), 1250, 640, lambda c: card(c, "1", "veneno", lambda c: rye(c, True, 160, 3), w=260, h=300), anim="pop", t1=tw("fungo", 593) - 0.2)
    if t < tw("fungo", 593) - 0.2:
        x_over(c, t, tw("descarta", 588) + 0.4, 1250, 640, 90)
    ft = tw("fungo", 593)
    if t > ft - 0.2:
        show(c, t, ft, 1250, 100, lambda c: hl(c, "o fungo corta a circulação", 0, 0, 46), anim="up", t1=tw("um", 603) - 0.2)
        man(c, t, 1100, 960, 0.85, poses=((0, "slump"),), exprs=((0, "desperate"),), col=PEASANT[1], fid=260)
        show(c, t, tw("Uma", 598), 1550, 520, T("convulsões: sim", 38, INK, HAND), anim="pop")
        show(c, t, tw("dançar", 599), 1550, 620, lambda c: (text(c, "dançar por dias: não", 0, 0, 38, HAND, RED)), anim="pop")
        ut = tw("um", 603)
        if t > ut:
            for i in range(5):
                mini_dancer(c, t, 1400 + i * 80, 990, 0.32, seed=i + 70)
            show(c, t, ut, 1250, 100, lambda c: hl(c, "e por que todos fariam a mesma coisa?", 0, 0, 42), anim="up")
    HIST(c, t, [(0, "stand"), (ft, "think")], [(0, "neutral")], x=250, s=0.85)


def s41(c, t):  # 611.8 - 626.1  teoria 2: encenação; grupos religiosos, rituais proibidos; mas gente apavorada
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.05, 0.06)); c.fill()
    show(c, t, 611.9, 1250, 100, lambda c: hl(c, "teoria 2: tudo encenado", 0, 0, 50), anim="up")
    gt = tw("grupos", 614)
    for i in range(4):
        scholar(c, t, 900 + i * 180, 980, 0.62, poses=((0, "arms_up" if i % 2 else "hold"),), exprs=((0, "neutral"),),
                col=(0.20, 0.18, 0.22), fid=270 + i, appear=gt + i * 0.2)
    if t > gt:
        put(c, 1170, 560, lambda c: candle(c, t), 1.0)
    show(c, t, tw("rituais", 615), 1250, 260, T("rituais proibidos disfarçados de dança", 36, AMBER), anim="fade", t1=tw("Mas", 620) - 0.2)
    mt = tw("Mas", 620)
    if t > mt:
        c.rectangle(0, 0, W, H); rgb(c, (0.03, 0.03, 0.04), 0.65 * fade_in(t, mt, 0.4)); c.fill()
        dancer(c, t, 1250, 960, 0.85, t0=mt, fid=275, col=PEASANT[2], exprs=((0, "desperate"),))
        show(c, t, tw("apavorada", 620), 1250, 260, lambda c: caption_box(c, "os relatos: gente apavorada, pedindo ajuda", 40), anim="up")
        x_over(c, t, tw("culto", 621), 1620, 520, 80)
    HIST(c, t, [(0, "stand"), (mt, "shrug")], [(0, "think")], x=250, s=0.85)


def s42(c, t):  # 626.1 - 653.3  Paracelso: irritar o marido; outras imitaram; preconceito; mas: causa na mente
    c.rectangle(0, 0, W, H); rgb(c, (0.07, 0.06, 0.06)); c.fill()
    pt = tw("Paracelso", 627)
    mt = tw("Mas", 646)
    if t < mt - 0.3:
        doctor(c, t, 1000, 1000, 0.85, poses=((0, "stand"), (tw("Para", 633), "point_r")), exprs=((0, "confident"),), fid=280, appear=pt - 0.3)
        show(c, t, pt, 1000, 380, lambda c: label_card(c, "médico suíço", "Paracelso"), anim="up", t1=tw("Para", 633) - 0.2)
        it = tw("irritar", 633)
        if t > tw("Para", 633):
            troffea(c, t, 1450, 980, 0.75, t0=tw("Para", 633))
            man(c, t, 1680, 980, 0.7, poses=((0, "hips"),), exprs=((0, "angry"),), col=PEASANT[1], fid=281)
            show(c, t, it, 1100, 330, lambda c: bubble(c, "só para irritar o marido", size=36, tx=80, ty=90), anim="pop")
        show(c, t, tw("preconceituosa", 642) - 0.2, 1250, 120, lambda c: date_stamp(c, "PRECONCEITO", 56, RED), anim="stamp")
    else:
        show(c, t, mt, 1250, 100, lambda c: hl(c, "mas ele acertou em um ponto", 0, 0, 46), anim="up")
        ht = tw("mente", 647)
        c.save(); c.translate(1250, 560)
        circle(c, 0, 0, 170, (0.12, 0.11, 0.12), 6)
        c.restore()
        if t > ht - 0.2:
            glow(c, 1250, 560, 220, AMBER, 0.30 * fade_in(t, ht - 0.2))
            text(c, "mente", 1250, 560, 60, SERIF, AMBER)
        show(c, t, tw("corpo", 648), 1250, 860, T("e não no corpo", 40, INK, HAND), anim="fade")
    HIST(c, t, [(0, "stand"), (mt, "finger_up")], [(0, "neutral"), (tw("preconceituosa", 642), "think")], x=250, s=0.85)


def s43(c, t):  # 653.3 - 681.2  doença psicogênica em massa: fome, doenças, medo; bastou uma; transe; crença virou realidade
    ft = tw("fome", 657)
    bt = tw("bastou", 666)
    c.rectangle(0, 0, W, H); rgb(c, (0.06, 0.05, 0.06)); c.fill()
    show(c, t, 653.4, 1250, 100, lambda c: hl(c, "a teoria mais aceita", 0, 0, 46), anim="up", t1=tw("Para", 657) - 0.2)
    show(c, t, tw("doença", 656), 1250, 230, lambda c: stitle(c, "doença psicogênica em massa", 0, 0, 56, INK, AMBER), anim="fade", t1=bt - 0.3)
    if t < bt - 0.3:
        for i, (s, w, fn) in enumerate((("fome", "fome", sc(bread, (0.40, 0.32, 0.26), s=0.7)),
                                        ("doenças", "doenças", sc(skull, s=0.5)),
                                        ("medo", "medo", lambda c: saint_statue(c, t, False) if False else sc(big_q, 90, RED)(c)))):
            x = 830 + i * 420
            show(c, t, tw(w, 657) - 0.1, x, 520, lambda c, s=s, fn=fn: card(c, "", s, fn, w=300, h=320), anim="up")
        dt = tw("desespero", 661)
        if t > dt:
            for i in range(3):
                arrow(c, 830 + i * 420, 700, 1250, 860, AMBER, 5, 0.1)
            show(c, t, dt, 1250, 900, T("desespero extremo", 40, RED, SERIF), anim="fade")
    else:
        street(c, t, 880, 0.4, seed=91)
        dancer(c, t, 1250, 960, 0.8, t0=tw("começar", 668), fid=290, col=TROF)
        show(c, t, bt, 1250, 100, lambda c: hl(c, "bastou uma pessoa começar", 0, 0, 46), anim="up", t1=tw("O", 673) - 0.2)
        tr = tw("transe", 673)
        dance_crowd(c, t, tw("medo", 673), 22, 960, 640, 1820, 3, 0.40, seed=23, d=3.0)
        show(c, t, tr, 1250, 100, lambda c: hl(c, "um estado parecido com um transe", 0, 0, 44), anim="up", t1=tw("crença", 677) - 0.2)
        show(c, t, tw("crença", 677), 1250, 100, lambda c: stitle(c, "e a crença virou realidade", 0, 0, 56, INK, RED), anim="fade")
        fog(c, t, 940, 0.08)
    HIST(c, t, [(0, "present"), (bt, "stand")], [(0, "neutral"), (bt, "worried")], x=250, s=0.85)


PROJ_A = make_proj(-22, 62, -38, 30)


def s44(c, t):  # 681.2 - 702.2  1962, Tanganica: crise de riso num internato, se espalhou; escolas fecharam; só o riso
    it = tw("internato", 690)
    if t < it - 0.3:
        draw_map(c, PROJ_A, ["africa", "arabia", "madagascar"], 10, (0.20, 0.20, 0.18), (0.06, 0.07, 0.08))
        show(c, t, 681.3, 1300, 100, lambda c: hl(c, "pode parecer coisa do passado...", 0, 0, 44), anim="up", t1=tw("mil", 684) - 0.2)
        show(c, t, tw("mil", 684), 1300, 100, lambda c: date_stamp(c, "1962", 64, AMBER), anim="stamp")
        if t > tw("Tanganica", 685):
            map_point(c, PROJ_A, 31.6, -1.2, AMBER, 11, t)
            map_label(c, PROJ_A, 31.6, -1.2, "Tanganica (hoje Tanzânia)", 32, INK, TYPE, 220, 0)
    else:
        c.rectangle(0, 0, W, H); rgb(c, (0.08, 0.08, 0.07)); c.fill()
        c.rectangle(0, 880, W, H - 880); rgb(c, (0.14, 0.12, 0.10)); c.fill()
        put(c, 1250, 880, lambda c: hut(c, 600, 260, True, t), 1.0)
        show(c, t, it, 1250, 100, lambda c: hl(c, "uma crise de riso num internato de meninas", 0, 0, 42), anim="up", t1=tw("Escolas", 694) - 0.2)
        for i in range(5):
            x = 850 + i * 200
            figure(c, t, x, 1000, 0.45, poses=((0, "hips" if i % 2 else "head"),), exprs=((0, "grin" if i % 2 else "happy"),),
                   coat=[(0.30, 0.50, 0.62), (0.62, 0.40, 0.30)][i % 2], hair="tuft", fid=300 + i, appear=it + 0.3 + i * 0.3)
            if t > it + 0.6 + i * 0.3:
                put(c, x, 700, lambda c, i=i: laugh_marks(c, t + i * 0.7, 2), 1.0)
        et = tw("Escolas", 694)
        show(c, t, et, 1250, 100, lambda c: date_stamp(c, "ESCOLAS FECHADAS", 52, RED), anim="stamp", t1=tw("Não", 696) - 0.2)
        show(c, t, tw("Não", 696), 1250, 100, lambda c: hl(c, "sem vírus, sem veneno", 0, 0, 46), anim="up")
        show(c, t, tw("riso", 698), 1250, 220, T("só o riso, de pessoa para pessoa", 38, AMBER), anim="fade")
    HIST(c, t, [(0, "stand"), (it, "think")], [(0, "neutral"), (it, "think")], x=250, s=0.85)


def s45(c, t):  # 702.2 - 718.6  perguntas sem resposta: por que ali e naquele verão? por que dança? como o ritual funcionou?
    street(c, t, 880, 0.4, seed=95, n=6)
    c.rectangle(0, 0, W, H); rgb(c, (0.02, 0.02, 0.03), 0.6); c.fill()
    show(c, t, 702.3, 1150, 100, lambda c: stitle(c, "perguntas sem resposta", 0, 0, 58, INK, AMBER), anim="up")
    qs = (("Por que em Estrasburgo, naquele verão?", tw("Por", 706)), ("Por que a dança?", tw("Por", 709)),
          ("Como um ritual acabou com aquilo?", tw("como", 712)))
    for i, (s, tt) in enumerate(qs):
        show(c, t, tt, 1150, 330 + i * 130, lambda c, s=s: hl(c, s, 0, 0, 42, rot=0.01 * (i - 1)), anim="up")
    rt = tw("sapatos", 713)
    show(c, t, rt - 0.2, 1500, 860, sc(red_shoes, False, s=0.8), anim="pop")
    HIST(c, t, [(0, "think")], [(0, "think")], x=250, s=0.85)


def s46(c, t):  # 718.6 - 733.4  500 anos depois, o nome; ninguém sabe o que ela sentiu; ela começou; a cidade foi atrás
    street(c, t, 880, 0.3, seed=21)
    ct = tw("começou", 728)
    troffea(c, t, 1250, 960, 0.9, t0=ct, exprs=((0, "sad"), (ct, "desperate")))
    show(c, t, 718.7, 1250, 100, lambda c: hl(c, "Frau Troffea", 0, 0, 52), anim="up", t1=tw("Ninguém", 723) - 0.2)
    show(c, t, tw("Ninguém", 723), 1250, 100, lambda c: caption_box(c, "ninguém sabe o que ela sentiu", 44), anim="up", t1=ct - 0.2)
    show(c, t, ct, 1250, 100, lambda c: hl(c, "ela começou a dançar", 0, 0, 48), anim="up", t1=tw("cidade", 730) - 0.2)
    at_ = tw("cidade", 730)
    dance_crowd(c, t, at_, 26, 960, 650, 1820, 3, 0.40, seed=29, d=2.0)
    show(c, t, at_, 1250, 100, lambda c: stitle(c, "e uma cidade inteira foi atrás", 0, 0, 52, INK, AMBER), anim="fade")
    fog(c, t, 930, 0.08)
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=250, s=0.85)


def s47(c, t):  # 733.4 - 742.7  e você? veneno, medo ou algo que não entendemos; deixa sua teoria
    c.rectangle(0, 0, W, H); rgb(c, (0.06, 0.05, 0.06)); c.fill()
    show(c, t, 733.5, 1150, 100, lambda c: stitle(c, "E você?", 0, 0, 72, INK, AMBER), anim="up")
    opts = (("veneno?", tw("veneno", 736), lambda c: (c.translate(0, 90), rye(c, True, 150, 3))),
            ("medo?", tw("medo", 736), lambda c: sc(big_q, 90, RED)(c)),
            ("outra coisa?", tw("alguma", 736), lambda c: mini_dancer(c, t, 0, 110, 0.5, 3)))
    for i, (s, tt, ic) in enumerate(opts):
        show(c, t, tt, 760 + i * 400, 520, lambda c, s=s, ic=ic, i=i: card(c, str(i + 1), s, ic, w=340, h=400), anim="up")
    show(c, t, tw("Deixa", 740), 1150, 920, lambda c: (speech(c, 820, 130, -300, 110), text(c, "deixe sua teoria nos comentários", 0, 0, 42, HAND, INK)),
         anim="pop")
    HIST(c, t, [(0, "point_r"), (740.5, "present")], [(0, "think"), (740.5, "happy")], x=220, s=0.8)


def s48(c, t):  # 742.7 - fim  encerramento
    night(c, t, 700, (1720, 150), 100)
    c.save(); c.translate(1720, 1000); cathedral(c, 560, lit=0.6); c.restore()
    c.rectangle(0, 0, W, H); rgb(c, (0.02, 0.02, 0.03), 0.55); c.fill()
    cobbles(c, 1000)
    HIST(c, t, [(0, "stand"), (742.9, "present"), (745.6, "wave"), (747.6, "stand")], [(0, "neutral"), (744.0, "happy")], x=420, s=1.05)
    show(c, t, 742.8, 1100, 260, T("Eu sou o Historiador.", 44, AMBER), anim="fade")
    show(c, t, 744.2, 1100, 470, sc(subscribe_btn, t > 745.6, s=0.9))
    show(c, t, 744.6, 1430, 470, sc(bell, s=0.8), rot=math.sin(t * 18) * 0.2 * max(0, 1 - (t - 744.6)))
    show(c, t, 745.2, 1100, 720, lambda c: (text(c, "PONTO CEGO", 0, 0, 84, SERIF, INK), line(c, -300, 58, 300, 58, 3, AMBER)), anim="fade", d=1.2)
    fog(c, t, 980, 0.09)


SCENES = [
    (0.0, 12.1, s01), (12.1, 22.3, s02), (22.3, 39.6, s03), (39.6, 52.2, s04), (52.2, 57.1, s05), (57.1, 68.5, s06),
    (68.5, 84.7, s07), (84.7, 96.7, s08), (96.7, 116.9, s09), (116.9, 132.3, s10), (132.3, 153.8, s11), (153.8, 166.0, s12),
    (166.0, 185.6, s13), (185.6, 202.1, s14), (202.1, 215.9, s15), (215.9, 228.0, s16), (228.0, 247.2, s17),
    (247.2, 261.5, s18), (261.5, 280.3, s19), (280.3, 304.0, s20), (304.0, 321.2, s21), (321.2, 325.1, s22),
    (325.1, 336.5, s23), (336.5, 359.9, s24), (359.9, 376.6, s25), (376.6, 387.7, s26), (387.7, 399.9, s27),
    (399.9, 411.2, s28), (411.2, 428.6, s29), (428.6, 443.5, s30), (443.5, 451.4, s31), (451.4, 473.4, s32),
    (473.4, 487.8, s33), (487.8, 503.1, s34), (503.1, 529.4, s35), (529.4, 545.0, s36), (545.0, 562.1, s37),
    (562.1, 566.6, s38), (566.6, 587.4, s39), (587.4, 611.8, s40), (611.8, 626.1, s41), (626.1, 653.3, s42),
    (653.3, 681.2, s43), (681.2, 702.2, s44), (702.2, 718.6, s45), (718.6, 733.4, s46), (733.4, 742.7, s47),
    (742.7, 999.0, s48),
]

SFX_OFF = True
SFX = [(6.1, "tum"), (52.3, "boom"), (130.7, "bell"), (162.1, "heartbeat"), (166.1, "tum"), (213.8, "boom"),
       (225.3, "heartbeat"), (304.1, "boom"), (321.3, "tum"), (397.1, "bell"), (415.0, "boom"), (446.6, "heartbeat"),
       (503.2, "tum"), (656.1, "boom"), (677.9, "heartbeat"), (730.7, "boom"), (745.2, "boom")]
