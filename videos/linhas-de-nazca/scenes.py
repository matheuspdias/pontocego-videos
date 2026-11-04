"""As Linhas de Nazca — Ponto Cego.
Narração: Pedro Lima - Serious (HeyGen / ElevenLabs v4), 5 blocos com 1 s de silêncio entre eles (~788,6 s).
Tempos absolutos (já com os offsets dos blocos): transcricao.txt e palavras.json (gerados por tempos.py).
tw("palavra", perto_de) devolve o início da ocorrência dessa palavra (prefixo) mais próxima do tempo dado (até 8 s).
Objetos do caso (geoglifos, chão de pedrinhas visto de cima e do chão, avião pequeno, estacas e cordas, mirante,
puquio, drone, cacos de cerâmica, rodovia, caixas de detecção da IA...) ficam no engine.py (seção LINHAS DE NAZCA).
"""
import json
import os
import unicodedata

from engine import *

THEME = "deserto"

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
        cand = [w["t0"] for w in _WORDS if _norm(w["w"]).startswith(p) and abs(w["t0"] - after) < 8.0]
        if not cand:
            raise KeyError(f"palavra não encontrada: {prefix} perto de {after}")
        _TW[key] = min(cand, key=lambda x: abs(x - after))
    return _TW[key]


# ------------------------------------------------------------------ helpers
NAZ_COATS = [(0.55, 0.26, 0.18), (0.62, 0.48, 0.30), (0.40, 0.30, 0.22), (0.70, 0.56, 0.40), (0.48, 0.20, 0.16)]
GREENISH = (0.40, 0.62, 0.42)


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


def put(c, x, y, fn, s=1.0, a=1.0, rot=0.0):
    def f(c):
        c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s); fn(c); c.restore()
    faded(c, a, f)


def glyph_at(c, t, kind, x, y, s, t0, d=3.0, lw=None, glow_a=0.0, col=GLYPH, rot=0.0, a=1.0):
    """geoglifo sendo traçado a partir de t0 (em d segundos)"""
    if t < t0:
        return
    p = ease_io(clamp01((t - t0) / d))
    put(c, x, y, lambda c: geoglyph(c, kind, p, col, (lw or 5) / s, glow_a), s, a, rot)


def native(c, t, x, y, s, poses=((0, "stand"),), exprs=((0, "neutral"),), k=0, appear=None, **kw):
    """antigo morador da região (túnica de algodão, cabelo comprido)"""
    figure(c, t, x, y, s, poses=poses, exprs=exprs, coat=NAZ_COATS[k % len(NAZ_COATS)], hair="long", hat=None,
           fid=30 + k, appear=appear, **kw)


def x_over(c, t, t0, x, y, s=70):
    show(c, t, t0, x, y, lambda c: big_x(c, s, RED, 14), anim="stamp")


def check(c, s=1.0, col=(0.45, 0.72, 0.42)):
    c.save(); c.scale(s, s)
    c.move_to(-34, 0); c.line_to(-8, 26); c.line_to(38, -30)
    rgb(c, col); c.set_line_width(12); c.stroke()
    c.restore()


def counter_lbl(c, val, label, col=AMBER, size=110):
    text(c, val, 0, 0, size, SERIF, col)
    text(c, label, 0, size * 0.78, 34, TYPE, INK)


def label_card(c, top, name, w=None):
    ww = w or max(text_w(c, name, 44, SERIF), text_w(c, top, 30, TYPE)) + 70
    rrect(c, -ww / 2, -62, ww, 124, 12); fs(c, (0.10, 0.08, 0.07), 4, (0.62, 0.56, 0.48))
    text(c, top, 0, -26, 30, TYPE, AMBER)
    text(c, name, 0, 22, 44, SERIF, INK)


def card(c, n, title_s, icon=None, crossed=0.0, w=330, h=420, sub=None, dim=False, ok=False):
    rrect(c, -w / 2, -h / 2, w, h, 14); fs(c, (0.12, 0.10, 0.09), 5, LGRAY if dim else (0.78, 0.66, 0.52))
    text(c, n, 0, -h / 2 + 44, 32, TYPE, AMBER)
    text(c, title_s, 0, -h / 2 + 96, 38 if len(title_s) < 12 else 30, SERIF, GRAY if dim else INK)
    if sub:
        text(c, sub, 0, h / 2 - 36, 26, TYPE, GRAY)
    if icon:
        c.save(); c.translate(0, 50); icon(c); c.restore()
    if crossed > 0:
        c.save(); c.scale(crossed, crossed); big_x(c, 120, RED, 14); c.restore()
    if ok:
        c.save(); c.translate(0, 50); check(c, 1.6); c.restore()


def night(c, t, ymax=520, moon_xy=(1660, 150), n=70):
    stars(c, t, n, ymax)
    if moon_xy:
        c.save(); c.translate(*moon_xy); moon(c, 44); c.restore()
        glow(c, moon_xy[0], moon_xy[1], 200, LYELLOW, 0.07)


def aerial(c, t, seed=1, lines=True, dark=0.0, n=7):
    pampa_top(c, t, seed, nazca_lines_set(seed + 2, n) if lines else None, dark)


def ground(c, t, y=760, track=False, sky=True, moon_xy=(1660, 150)):
    if sky:
        night(c, t, y - 200, moon_xy)
    pampa_side(c, t, y, track=track)


def plane_over(c, t, t0, d, y=200, x0=-200, x1=2100, s=0.8):
    if t < t0:
        return
    k = clamp01((t - t0) / d)
    put(c, x0 + (x1 - x0) * k, y + math.sin(t * 1.3) * 8, lambda c: cessna(c, t), s)


def plane_top_over(c, t, t0, d, y=520, x0=-250, x1=2200, s=0.7):
    if t < t0:
        return
    k = clamp01((t - t0) / d)
    x = x0 + (x1 - x0) * k
    put(c, x + 60, y + 90, lambda c: plane_shadow(c), s)
    put(c, x, y, lambda c: cessna_top(c, t), s)


# --- mapa do Peru
PROJ_P = make_proj(-82.5, -69.5, -18.5, -8.5)
CITY = {"Lima": (-77.04, -12.05), "Nazca": (-74.94, -14.83), "Palpa": (-75.18, -14.53), "Cusco": (-71.97, -13.53)}


def peru_map(c, t, proj=PROJ_P):
    draw_map(c, proj, SOUTH_AMERICA, land_col=(0.30, 0.22, 0.15), sea_col=(0.05, 0.08, 0.12))


def city_pt(c, t, proj, name, dx=0, dy=-38, col=AMBER, size=32, pulse=True):
    lon, lat = CITY[name]
    map_point(c, proj, lon, lat, col, 9, t, pulse)
    map_label(c, proj, lon, lat, name, size, INK, TYPE, dx, dy)


# ================================================================== CENAS — BLOCO 1
def s01(c, t):  # 0 - 13.2  um beija-flor do tamanho de um campo de futebol; macaco; aranha; condor
    aerial(c, t, 1, lines=False)
    glyph_at(c, t, "hummingbird", 1000, 520, 3.0, 0.3, 4.5, 6, glow_a=0.05)
    show(c, t, tw("campo", 3), 1000, 960, lambda c: caption_box(c, "do tamanho de um campo de futebol", 40), anim="up",
         t1=tw("macaco", 5) - 0.3)
    glyph_at(c, t, "monkey", 1560, 330, 1.1, tw("macaco", 5) - 0.2, 2.5)
    glyph_at(c, t, "spider", 1580, 800, 1.0, tw("aranha", 9) - 0.2, 1.4)
    glyph_at(c, t, "condor", 520, 300, 1.1, tw("condor", 10) - 0.2, 1.6)
    fog(c, t, 980, 0.05)
    HIST(c, t, [(0, "stand"), (tw("macaco", 5), "point_r")], [(0, "neutral"), (tw("macaco", 5), "shocked")], x=300, s=0.85,
         appear=0.6)


def s02(c, t):  # 13.2 - 31.4  milhares de linhas; retas por quilômetros, como régua; triângulos e trapézios
    pampa_top(c, t, 4)
    rnd = random.Random(9)
    t0 = 13.4
    for i, (a, b, lw) in enumerate(nazca_lines_set(21, 12)):
        tt = t0 + i * 0.45
        if t > tt:
            k = ease_out(clamp01((t - tt) / 1.4))
            line(c, a[0], a[1], a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, lw, (0.72, 0.62, 0.48))
    tr = tw("trapézios", 25)
    for i, (x, y, w0, w1, h, ang) in enumerate(((1250, 320, 60, 260, 640, 0.5), (700, 720, 40, 200, 520, -1.1),
                                                (1560, 820, 30, 150, 400, 2.2))):
        a_ = fade_in(t, tw("triângulos", 25) + i * 0.5, 0.8)
        if a_ > 0:
            trapezoid_top(c, x, y, w0 * a_, w1 * a_, h * a_, ang, a=0.8)
    show(c, t, tw("retas", 20), 1050, 110, lambda c: hl(c, "retas por quilômetros", 0, 0, 46), anim="up", t1=tw("Outras", 25) - 0.3)
    show(c, t, tw("Outras", 25), 1050, 110, lambda c: caption_box(c, "triângulos e trapézios gigantes", 42), anim="up")
    fog(c, t, 980, 0.05)
    HIST(c, t, [(0, "think"), (tw("régua", 24), "point_r")], [(0, "think"), (tr, "shocked")], x=280, s=0.85)


def s03(c, t):  # 31.4 - 42.2  quem caminha não vê desenho; do chão, trilhas rasas; precisa estar lá no alto
    ground(c, t, 700, track=True)
    pt = tw("enxergar", 38)
    show(c, t, 31.6, 1150, 120, lambda c: caption_box(c, "do chão: nenhum desenho", 44), anim="up", t1=pt - 0.3)
    show(c, t, tw("trilhas", 35), 1350, 900, lambda c: hl(c, "só trilhas rasas", 0, 0, 40), anim="up", t1=pt - 0.3)
    plane_over(c, t, pt - 1.0, 5.0, 220, 300, 1700, 0.75)
    show(c, t, tw("alto", 40), 1150, 420, lambda c: hl(c, "é preciso estar lá no alto", 0, 0, 44), anim="up")
    HIST(c, t, [(0, "think"), (pt, "point_ru")], [(0, "worried"), (pt, "think")], x=520, y=1000, s=1.0)


def s04(c, t):  # 42.2 - 53.4  feitas há mais de 1.500 anos; sem escrita, sem avião, sem subir ao céu
    ground(c, t, 760)
    show(c, t, 42.4, 1200, 120, lambda c: date_stamp(c, "MAIS DE 1.500 ANOS", 54, AMBER), anim="stamp")
    for i, xx in enumerate((900, 1060, 1500)):
        native(c, t, xx, 980, 0.8, poses=((0, "hold" if i == 1 else "stand"),), k=i, appear=tw("povo", 46) + i * 0.2)
    st, av, ce = tw("escrita", 47), tw("avião", 49), tw("céu", 51)
    show(c, t, st, 1000, 420, sc(scroll, 3, 200, 130, s=0.9), anim="pop")
    x_over(c, t, st + 0.3, 1000, 420, 55)
    show(c, t, av, 1300, 400, sc(cessna, t, s=0.55), anim="pop")
    x_over(c, t, av + 0.3, 1300, 400, 55)
    show(c, t, ce, 1600, 380, sc(big_q, 120, AMBER), anim="pop")
    fog(c, t, 900, 0.07)
    HIST(c, t, [(0, "present")], [(0, "neutral"), (st, "think")], x=300, s=0.9)


def s05(c, t):  # 53.4 - 59.5  como eles fizeram? e para quem?
    aerial(c, t, 6, dark=0.45)
    glyph_at(c, t, "hummingbird", 1200, 560, 2.6, 0.0, 0.1, 6, glow_a=0.06, a=0.5)
    show(c, t, 53.5, 1200, 330, S("Como?", 96, INK), anim="up")
    show(c, t, tw("quem", 57), 1200, 520, lambda c: stitle(c, "Para quem?", 0, 0, 110, AMBER, AMBER), anim="up")
    HIST(c, t, [(0, "think")], [(0, "think")], x=320, s=0.95)


def s06(c, t):  # 59.5 - 62.9  título
    aerial(c, t, 8, dark=0.55)
    glyph_at(c, t, "hummingbird", 960, 560, 3.6, 0.0, 0.1, 7, glow_a=0.10, a=0.45)
    show(c, t, 59.6, 960, 450, lambda c: (text(c, "AS", 0, -110, 46, TYPE, AMBER),
                                          stitle(c, "LINHAS DE NAZCA", 0, 10, 130, INK, AMBER)), anim="fade", d=1.2)
    show(c, t, 60.6, 960, 590, lambda c: line(c, -460, 0, 460, 0, 3, AMBER), anim="fade")
    show(c, t, 61.2, 960, 650, T("Peru  ·  deserto de Nazca", 40, ICE), anim="fade", d=1.0)
    fog(c, t, 900, 0.08)


def s07(c, t):  # 62.9 - 79.1  planalto entre Nazca e Palpa, 400 km ao sul de Lima; um dos lugares mais secos
    peru_map(c, t)
    city_pt(c, t, PROJ_P, "Lima", 80, -10)
    if t > 63.5:
        city_pt(c, t, PROJ_P, "Nazca", 90, 20)
        city_pt(c, t, PROJ_P, "Palpa", 80, -30, pulse=False)
    q = tw("quatrocentos", 67)
    if t > q:
        map_path(c, PROJ_P, [CITY["Lima"], (-76.3, -13.4), CITY["Nazca"]], ease_out(clamp01((t - q) / 1.2)), AMBER, 4, )
        show(c, t, q + 0.3, 0, 0, lambda c: map_label(c, PROJ_P, -78.6, -14.2, "~400 km", 36, AMBER, TYPE), anim="fade")
    show(c, t, 63.1, 0, 0, lambda c: map_label(c, PROJ_P, -72.6, -11.0, "PERU", 72, (0.62, 0.50, 0.36), SERIF), anim="fade")
    show(c, t, 66.0, 0, 0, lambda c: map_label(c, PROJ_P, -79.0, -16.8, "Oceano Pacífico", 30, (0.50, 0.66, 0.82), TYPE), anim="fade")
    show(c, t, tw("secos", 71) - 0.3, 1280, 980, lambda c: caption_box(c, "um dos lugares mais secos do planeta", 40), anim="up",
         t1=tw("chove", 73) - 0.2)
    show(c, t, tw("chove", 73), 1280, 980, lambda c: caption_box(c, "quase não chove · pouco vento junto ao chão", 38), anim="up")
    HIST(c, t, [(0, "point_r")], [(0, "neutral")], x=260, s=0.85)


def s08(c, t):  # 79.1 - 98.7  pedrinhas avermelhadas (óxido de ferro); embaixo terra clara; tirar as pedras e empilhar
    # corte do chão (vista lateral ampliada)
    c.rectangle(0, 0, W, H); rgb(c, (0.07, 0.05, 0.04)); c.fill()
    gy = 560
    c.rectangle(560, gy, 1200, 360); rgb(c, (0.70, 0.60, 0.44)); c.fill()
    for k in range(30):
        x = 590 + k * 40
        line(c, x, gy + 40, x + 30, gy + 340, 2, (0.62, 0.52, 0.38))
    rnd = random.Random(4)
    open_t = tw("Bastava", 92)
    clear = ease_io(clamp01((t - open_t) / 3.0))
    pile_l = []
    for k in range(40):
        x = 580 + k * 29 + rnd.uniform(-4, 4)
        r = rnd.uniform(11, 16)
        inside = 920 < x < 1400
        if inside and clear > 0:
            side = -1 if x < 1160 else 1
            tx = (880 if side < 0 else 1440) + rnd.uniform(-30, 30)
            ty = gy - r - rnd.uniform(14, 40) * clear
            x = x + (tx - x) * clear
            yy = (gy - r * 0.7) + (ty - (gy - r * 0.7)) * clear
        else:
            yy = gy - r * 0.7
        circle(c, x, yy, r, (0.38, 0.18, 0.12), 3, (0.18, 0.10, 0.07))
    show(c, t, 79.4, 1160, 230, lambda c: hl(c, "pedrinhas avermelhadas", 0, 0, 46), anim="up", t1=tw("Logo", 86) - 0.3)
    show(c, t, tw("óxido", 83), 1160, 330, T("óxido de ferro + sol", 36, AMBER), anim="fade", t1=tw("Logo", 86) - 0.3)
    show(c, t, tw("Logo", 86), 1160, 230, lambda c: hl(c, "embaixo: terra clara", 0, 0, 46), anim="up", t1=open_t - 0.3)
    arrow_draw(c, t, tw("Logo", 86) + 0.3, 1520, 400, 1440, 640, col=AMBER)
    if t < open_t + 0.1:
        pass
    show(c, t, open_t + 1.0, 1160, 230, lambda c: caption_box(c, "tira as pedras escuras... surge a faixa clara", 40), anim="up")
    if clear > 0.5:
        glow(c, 1160, gy, 260, GLYPH, 0.18 * (clear - 0.5) * 2)
    native(c, t, 1180, 545, 0.55, poses=((0, "stand"), (open_t, "hold")), k=0, appear=tw("moradores", 89))
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=300, s=0.9)


def s09(c, t):  # 98.7 - 114.3  sulcos de 10 a 15 cm; somadas passam de 1.300 km; centenas de formas; 70+ figuras
    aerial(c, t, 10, dark=0.25)
    show(c, t, 99.0, 1160, 200, lambda c: counter_lbl(c, "10 a 15 cm", "de profundidade", INK, 80), anim="up",
         t1=tw("Mas", 102) - 0.2)
    show(c, t, tw("somadas", 103), 1160, 200, lambda c: counter_lbl(c, "+ de 1.300 km", "somando todas as linhas", AMBER, 90),
         anim="up", t1=tw("São", 107) - 0.2)
    kinds = [("trapezoid", "trapézios", tw("trapézios", 107)), ("spiral", "espirais", tw("espirais", 109)),
             ("hummingbird", "70+ figuras", tw("setenta", 111))]
    for i, (k, lab, tt) in enumerate(kinds):
        glyph_at(c, t, k, 760 + i * 400, 560, 1.15, tt - 0.2, 1.2)
        show(c, t, tt, 760 + i * 400, 800, T(lab, 38, AMBER), anim="fade")
    HIST(c, t, [(0, "present")], [(0, "neutral"), (tw("setenta", 111), "shocked")], x=270, s=0.85)


def s10(c, t):  # 114.3 - 130.6  números: beija-flor 93 m; macaco 93 x 58; condor 130+; até quase 400 m
    aerial(c, t, 12, dark=0.15, n=4)
    items = [("hummingbird", "93 m", tw("beija-flor", 116), 640, 1.5), ("monkey", "93 x 58 m", tw("macaco", 119), 1040, 1.2),
             ("condor", "130+ m", tw("condor", 122), 1440, 1.25)]
    for k, lab, tt, x, s in items:
        glyph_at(c, t, k, x, 470, s, tt - 0.3, 1.4)
        show(c, t, tt + 0.4, x, 760, lambda c, lab=lab: label_card(c, "cerca de", lab, 260), anim="up")
    show(c, t, 114.5, 1040, 110, lambda c: hl(c, "os números", 0, 0, 46), anim="up", t1=tw("algumas", 126) - 0.2)
    show(c, t, tw("algumas", 126), 1040, 110, lambda c: hl(c, "algumas: quase 400 metros", 0, 0, 48), anim="up")
    if t > tw("quatrocentos", 128):
        glow(c, 1040, 480, 700, GLYPH, 0.10 * fade_in(t, tw("quatrocentos", 128)))
    HIST(c, t, [(0, "point_r")], [(0, "neutral"), (tw("quatrocentos", 128), "shocked")], x=260, s=0.8)


def s11(c, t):  # 130.6 - 156.0  duas culturas: Paracas, depois Nazca (500 a.C.-500 d.C.); ceramistas; tecidos; cultivo
    ground(c, t, 780)
    pa = tw("Paracas", 136)
    na = tw("Nazca", 138)
    show(c, t, pa - 0.1, 900, 200, lambda c: date_stamp(c, "PARACAS", 54, AMBER), anim="stamp")
    show(c, t, na - 0.1, 1400, 200, lambda c: date_stamp(c, "NAZCA", 54, RED), anim="stamp")
    show(c, t, tw("quinhentos", 141), 1400, 320, T("~500 a.C. a 500 d.C.", 36, INK), anim="fade")
    arrow_draw(c, t, na - 0.3, 1060, 200, 1240, 200, col=INK)
    ce = tw("ceramistas", 146)
    show(c, t, ce, 980, 640, sc(nazca_vase, s=1.0), anim="pop")
    te = tw("tecidos", 150)
    def textile(c):
        rrect(c, -110, -80, 220, 160, 6); fs(c, NAZCA_CREAM, 5)
        for r in range(4):
            for q in range(5):
                col = NAZCA_RED if (r + q) % 2 else (0.30, 0.40, 0.55)
                c.rectangle(-96 + q * 40, -66 + r * 36, 28, 24); rgb(c, col); c.fill()
    show(c, t, te, 1260, 640, textile, anim="pop")
    cu = tw("cultivar", 152)
    if t > cu:
        a_ = fade_in(t, cu)
        for k in range(9):
            put(c, 1450 + k * 34, 900, lambda c: (line(c, 0, 0, 0, -40, 4, GREENISH), line(c, 0, -20, 14, -34, 3, GREENISH),
                                                   line(c, 0, -26, -14, -38, 3, GREENISH)), 1.0, a_)
    native(c, t, 1620, 1000, 0.8, poses=((0, "stand"),), k=1, appear=na)
    native(c, t, 760, 1000, 0.75, poses=((0, "stand"),), k=3, appear=pa)
    fog(c, t, 920, 0.07)
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=300, s=0.9)


# ================================================================== CENAS — BLOCO 2
SPAN = (0.30, 0.22, 0.30)
KOSOK = (0.36, 0.32, 0.26)
REICHE = (0.50, 0.46, 0.40)


def s12(c, t):  # 156.0 - 171.6  séculos sem atenção; 1553, Pedro Cieza de León, sinais no chão; marcas de caminho
    ground(c, t, 760, track=True)
    show(c, t, tw("mil", 160) - 0.1, 1180, 120, lambda c: date_stamp(c, "1553", 60, AMBER), anim="stamp")
    ci = tw("Cieza", 164)
    figure(c, t, 1000, 990, 0.85, poses=((0, "stand"), (tw("anotou", 166), "hold")), exprs=((0, "think"),), coat=SPAN,
           hat="beret", hat_col=(0.10, 0.08, 0.08), hair=None, mustache=True, fid=11, appear=ci - 0.6)
    show(c, t, ci, 1000, 360, lambda c: label_card(c, "cronista espanhol", "Pedro Cieza de León"), anim="up")
    show(c, t, tw("sinais", 167), 1420, 420, sc(chronicle, 230, 300, "", 3, s=0.8) if "chronicle" in globals() else sc(scroll, 3),
         anim="pop")
    show(c, t, tw("marcas", 169), 1420, 640, lambda c: hl(c, "marcas de caminho?", 0, 0, 40), anim="up")
    fog(c, t, 900, 0.07)
    HIST(c, t, [(0, "stand")], [(0, "neutral")], x=300, s=0.9)


def s13(c, t):  # 171.6 - 193.2  século XX; 1927, Toribio Mejía Xesspe, a pé; pilotos: lá de cima, desenhos
    pl = tw("pilotos", 183)
    if t < pl - 0.4:
        ground(c, t, 760)
        show(c, t, 171.8, 1180, 120, lambda c: hl(c, "século XX", 0, 0, 48), anim="up", t1=tw("mil", 175) - 0.2)
        show(c, t, tw("mil", 175) - 0.1, 1180, 120, lambda c: date_stamp(c, "1927", 60, AMBER), anim="stamp")
        to = tw("Toribio", 176)
        walk = clamp01((t - to) / 7.0)
        figure(c, t, 900 + 600 * walk, 990, 0.85, poses=((0, "run" if 0 < walk < 1 else "stand"),), exprs=((0, "think"),),
               coat=(0.40, 0.36, 0.30), hat="fedora", hat_col=(0.70, 0.64, 0.52), hair=None, mustache=True, fid=12, appear=to - 0.4)
        show(c, t, to, 1180, 300, lambda c: label_card(c, "arqueólogo peruano", "Toribio Mejía Xesspe"), anim="up")
        HIST(c, t, [(0, "present")], [(0, "neutral")], x=300, s=0.9)
    else:
        aerial(c, t, 14, n=8)
        glyph_at(c, t, "hummingbird", 1100, 560, 2.6, tw("desenhos", 188) - 1.6, 2.5, 6)
        plane_top_over(c, t, pl - 0.4, 9.0, 330, -250, 2200, 0.8)
        show(c, t, tw("relatar", 186), 1100, 110, lambda c: caption_box(c, "pilotos começaram a relatar...", 42), anim="up",
             t1=tw("desenhos", 188) - 0.3)
        show(c, t, tw("desenhos", 188), 1100, 110, lambda c: hl(c, "lá de cima, as trilhas formavam desenhos", 0, 0, 44), anim="up")
        HIST(c, t, [(0, "point_r")], [(0, "shocked")], x=270, s=0.85)


def s14(c, t):  # 193.2 - 207.7  1941, Paul Kosok; irrigação; achou que fossem canais de água; mas aí aconteceu
    ground(c, t, 760, track=True)
    show(c, t, 193.4, 1180, 120, lambda c: date_stamp(c, "1941", 60, AMBER), anim="stamp")
    ko = tw("Paul", 197)
    figure(c, t, 1000, 990, 0.9, poses=((0, "stand"), (tw("achou", 201), "think")), exprs=((0, "neutral"),), coat=KOSOK,
           hat="fedora", hat_col=(0.72, 0.66, 0.54), hair=None, glasses=True, fid=13, appear=ko - 0.5)
    show(c, t, ko, 1000, 360, lambda c: label_card(c, "historiador americano", "Paul Kosok"), anim="up")
    ca = tw("canais", 202)
    if t > ca:
        a_ = fade_in(t, ca)
        put(c, 1440, 420, lambda c: (rrect(c, -170, -60, 340, 120, 12), fs(c, (0.10, 0.08, 0.07), 4, (0.62, 0.56, 0.48)),
                                     line(c, -130, 10, 130, 10, 14, (0.40, 0.62, 0.82)),
                                     text(c, "canais de água?", 0, -32, 30, TYPE, INK)), 1.0, a_)
    show(c, t, tw("aconteceu", 205), 1180, 228, lambda c: caption_box(c, "mas aí aconteceu uma coisa", 40), anim="up")
    fog(c, t, 900, 0.07)
    HIST(c, t, [(0, "stand"), (tw("aconteceu", 205), "finger_up")], [(0, "neutral"), (tw("aconteceu", 205), "think")], x=300, s=0.9)


def s15(c, t):  # 207.7 - 222.9  junho, solstício; fim da tarde; o sol se punha na direção de uma das linhas
    y = 700
    k = clamp01((t - 208) / 12.0)
    c.rectangle(0, 0, W, y); g = cairo.LinearGradient(0, 0, 0, y)
    g.add_color_stop_rgb(0, 0.10, 0.06, 0.06); g.add_color_stop_rgb(1, 0.40 + 0.1 * k, 0.20, 0.10)
    c.set_source(g); c.fill()
    sx = W * 0.62
    put(c, sx, y + 30 * k, lambda c: setting_sun(c, 110), 1.0)
    pampa_side(c, t, y, track=True)
    show(c, t, 207.9, 1180, 110, lambda c: date_stamp(c, "JUNHO · SOLSTÍCIO", 48, AMBER), anim="stamp", t1=tw("Kosok", 211) - 0.2)
    di = tw("direção", 216)
    if t > di:
        glow(c, sx, y, 500, (0.95, 0.60, 0.25), 0.18 * fade_in(t, di))
        c.save(); c.set_dash([18, 14]); line(c, sx, y - 10, sx, 240, 4, AMBER); c.restore()
    show(c, t, tw("Como", 218), 1180, 110, lambda c: hl(c, "como se apontasse aquele momento do ano", 0, 0, 42), anim="up")
    figure(c, t, 760, 1000, 0.95, poses=((0, "stand"), (di, "point_r")), exprs=((0, "neutral"), (di, "shocked")), coat=KOSOK,
           hat="fedora", hat_col=(0.72, 0.66, 0.54), hair=None, glasses=True, fid=13)
    HIST(c, t, [(0, "think")], [(0, "think")], x=280, s=0.85)


def s16(c, t):  # 222.9 - 231.2  Kosok fascinado; "o maior livro de astronomia do mundo"
    aerial(c, t, 16, dark=0.35, n=10)
    stars(c, t, 120, 1080)
    show(c, t, 223.1, 1150, 470, sc(book, "", (0.30, 0.22, 0.40), s=1.5), anim="pop")
    if t > 223.5:
        for k in range(6):
            a = t * 0.3 + k * 1.05
            circle(c, 1150 + math.cos(a) * 200, 470 + math.sin(a) * 120, 5, LYELLOW, 0)
    show(c, t, tw("chamou", 225), 1150, 860, lambda c: stitle(c, "\"o maior livro de astronomia do mundo\"", 0, 0, 46, INK, AMBER),
         anim="fade")
    show(c, t, tw("Segundo", 225), 1150, 940, T("segundo se conta", 30, GRAY), anim="fade")
    HIST(c, t, [(0, "present")], [(0, "happy")], x=280, s=0.85)


def reiche(c, t, x, y, s, poses=((0, "stand"),), exprs=((0, "neutral"),), appear=None, **kw):
    figure(c, t, x, y, s, poses=poses, exprs=exprs, coat=REICHE, hair="long", hat=None, glasses=True, fid=14,
           appear=appear, **kw)


def s17(c, t):  # 231.2 - 246.4  Maria Reiche, matemática alemã; Dresden 1903; Peru anos 30; ficou; dedicou a vida
    ground(c, t, 760)
    mr = tw("Maria", 234)
    reiche(c, t, 1050, 990, 0.95, appear=mr - 0.6, exprs=((0, "neutral"), (tw("ficou", 241), "happy")))
    show(c, t, mr, 1050, 340, lambda c: label_card(c, "matemática alemã", "Maria Reiche"), anim="up", t1=tw("Ela", 235) - 0.2)
    show(c, t, tw("Dresden", 236), 1050, 340, lambda c: label_card(c, "nasceu em Dresden", "1903"), anim="up",
         t1=tw("chegado", 238) - 0.1)
    show(c, t, tw("chegado", 238), 1050, 340, lambda c: label_card(c, "chegou ao Peru", "anos 1930"), anim="up",
         t1=tw("Depois", 240) - 0.2)
    show(c, t, tw("Depois", 240), 1050, 340, lambda c: hl(c, "Kosok foi embora. Ela ficou.", 0, 0, 44), anim="up",
         t1=tw("dedicou", 243) - 0.2)
    show(c, t, tw("dedicou", 243), 1050, 340, lambda c: hl(c, "o resto da vida às linhas", 0, 0, 44), anim="up")
    glyph_at(c, t, "spider", 1550, 880, 0.8, tw("linhas", 244) - 0.4, 1.0, a=0.9)
    fog(c, t, 900, 0.07)
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=300, s=0.9)


def s18(c, t):  # 246.4 - 262.5  décadas medindo; fita, bússola, paciência; vivia com pouco; vigias; brigou com o governo
    aerial(c, t, 18, dark=0.1, n=5)
    glyph_at(c, t, "monkey", 1250, 520, 2.4, 246.5, 0.1, 6)
    me = tw("medindo", 247)
    if t > me:
        k = ease_out(clamp01((t - me) / 3))
        c.save(); c.set_dash([10, 8]); line(c, 850, 830, 850 + 800 * k, 830, 4, AMBER); c.restore()
        text(c, "fita métrica", 850 + 400, 870, 30, TYPE, AMBER)
    show(c, t, tw("bússola", 250), 1680, 240, sc(compass, t, s=0.6), anim="pop")
    reiche(c, t, 850, 990, 0.9, poses=((0, "hold"),), exprs=((0, "think"),))
    show(c, t, tw("Morava", 252), 1250, 110, lambda c: caption_box(c, "vivia com muito pouco", 42), anim="up", t1=tw("Usou", 255) - 0.2)
    show(c, t, tw("Usou", 255), 1250, 110, lambda c: caption_box(c, "pagava vigias com o dinheiro dos livros", 42), anim="up",
         t1=tw("brigou", 258) - 0.2)
    show(c, t, tw("brigou", 258), 1250, 110, lambda c: hl(c, "protegeu aquele chão", 0, 0, 46), anim="up")
    HIST(c, t, [(0, "stand")], [(0, "neutral")], x=280, s=0.85)


def s19(c, t):  # 262.5 - 274.8  o deserto já tinha sido ferido: a Pan-Americana cortou o lagarto ao meio
    aerial(c, t, 20, n=4)
    glyph_at(c, t, "lizard", 1150, 540, 2.7, 262.6, 2.0, 6, rot=-0.15)
    hw = tw("rodovia", 265)
    if t > hw:
        k = ease_out(clamp01((t - hw) / 2.0))
        highway_top(c, -50, 520, -50 + (W + 100) * k, 520 + 80 * k, 64)
    show(c, t, tw("Pan-Americana", 265), 1150, 110, lambda c: hl(c, "Rodovia Pan-Americana", 0, 0, 46), anim="up",
         t1=tw("lagarto", 270) - 0.2)
    show(c, t, tw("lagarto", 270), 1150, 110, lambda c: caption_box(c, "o lagarto, cortado ao meio", 44), anim="up")
    HIST(c, t, [(0, "stand")], [(0, "sad"), (tw("cortou", 271), "worried")], x=270, s=0.85)


def s20(c, t):  # 274.8 - 297.5  acesso restrito; torre de observação; Unesco 1994; morreu aos 95; enterrada perto de Nazca
    ground(c, t, 780)
    show(c, t, tw("torre", 277), 1500, 1000, sc(mirador, 440), anim="up")
    if t > tw("visitantes", 280):
        for i in range(3):
            figure(c, t, 1440 + i * 50, 563, 0.35, poses=((0, "point_l" if i == 1 else "stand"),), exprs=((0, "happy"),),
                   shirt=[BLUE, RED, GREEN][i], fid=60 + i, appear=tw("visitantes", 280) + i * 0.2)
    show(c, t, 275.0, 1000, 120, lambda c: caption_box(c, "acesso restrito", 42), anim="up", t1=tw("Em", 284) - 0.3)
    un = tw("Unesco", 286)
    show(c, t, tw("mil", 284.4), 1000, 120, lambda c: date_stamp(c, "1994 · PATRIMÔNIO MUNDIAL", 46, AMBER), anim="stamp",
         t1=tw("Ela", 289.8) - 0.2)
    mo = tw("morreu", 290)
    show(c, t, mo, 1000, 120, lambda c: hl(c, "Maria Reiche  ·  1903 - 1998", 0, 0, 44), anim="up")
    reiche(c, t, 1000, 1000, 0.9, exprs=((0, "happy"), (mo, "sad")), alpha=1.0 - 0.6 * fade_in(t, mo, 2.0))
    en = tw("enterrada", 294)
    if t > en:
        put(c, 1150, 1010, lambda c: tombstone(c, ""), 0.5, fade_in(t, en))
    fog(c, t, 920, 0.07)
    HIST(c, t, [(0, "present"), (mo, "stand")], [(0, "neutral"), (mo, "sad")], x=300, s=0.9)


def s21(c, t):  # 297.5 - 324.6  a ideia do calendário não resistiu; Hawkins e Aveni testaram; algumas sim, a maioria não
    aerial(c, t, 22, lines=False, dark=0.3)
    cx, cy = 1150, 640
    rnd = random.Random(5)
    te = tw("testaram", 304)
    al = tw("Algumas", 310)
    ma = tw("maioria", 315)
    for k in range(16):
        a = rnd.uniform(0, 2 * math.pi)
        L = rnd.uniform(260, 520)
        hit = k in (2, 9, 13)
        col = (0.70, 0.60, 0.46)
        if t > al and hit:
            col = AMBER
        elif t > ma and not hit:
            col = (0.38, 0.32, 0.28)
        p = ease_out(clamp01((t - (te - 0.5 + k * 0.12)) / 1.0)) if t > te - 0.5 else 1.0
        line(c, cx, cy, cx + math.cos(a) * L * p, cy + math.sin(a) * L * p * 0.7, 7, col)
        if hit and t > al:
            circle(c, cx + math.cos(a) * L, cy + math.sin(a) * L * 0.7, 18, (0.95, 0.62, 0.25), 3)
    show(c, t, 297.7, 1150, 110, lambda c: hl(c, "um calendário gigante no chão?", 0, 0, 46), anim="up", t1=te - 0.5)
    show(c, t, tw("Gerald", 304), 1150, 110, lambda c: label_card(c, "astrônomos", "Gerald Hawkins  ·  Anthony Aveni", 700),
         anim="up", t1=al - 0.2)
    show(c, t, al, 1150, 110, lambda c: caption_box(c, "algumas apontam para o sol", 42), anim="up", t1=ma - 0.2)
    show(c, t, ma, 1150, 110, lambda c: caption_box(c, "a maioria não aponta para nada", 42), anim="up", t1=tw("Com", 318) - 0.1)
    show(c, t, tw("acaso", 321), 1150, 110, lambda c: hl(c, "algumas acertariam por acaso", 0, 0, 46), anim="up")
    HIST(c, t, [(0, "think"), (ma, "shrug")], [(0, "think"), (ma, "neutral")], x=270, s=0.85)


# ================================================================== CENAS — BLOCO 3
DANIKEN = (0.24, 0.26, 0.32)
NICKELL = (0.30, 0.42, 0.56)


def s22(c, t):  # 324.6 - 329.2  então, se não era um calendário, o que era?
    aerial(c, t, 24, dark=0.5)
    show(c, t, 324.8, 1150, 420, sc(big_q, 220, AMBER), anim="pop")
    show(c, t, 325.3, 1150, 700, S("se não era um calendário...", 56, INK), anim="up")
    HIST(c, t, [(0, "think")], [(0, "think")], x=300, s=0.95)


def s23(c, t):  # 329.2 - 347.0  1968, Erich von Däniken; "Eram os Deuses Astronautas?"; milhões; ideia sobre Nazca
    night(c, t, 700, (1700, 140), 110)
    pampa_side(c, t, 820)
    show(c, t, 329.4, 1180, 110, lambda c: date_stamp(c, "1968", 60, AMBER), anim="stamp")
    ed = tw("Erich", 337)
    figure(c, t, 920, 1010, 0.9, poses=((0, "stand"), (tw("livro", 339), "present")), exprs=((0, "confident"),), coat=DANIKEN,
           hair="tuft", hat=None, fid=21, appear=ed - 0.5)
    show(c, t, ed, 920, 400, lambda c: label_card(c, "escritor suíço", "Erich von Däniken"), anim="up", t1=tw("Eram", 341) - 0.2)
    er = tw("Eram", 341)
    show(c, t, er, 1350, 480, sc(book, "", (0.20, 0.30, 0.50), s=1.4), anim="pop")
    show(c, t, er, 1350, 720, lambda c: hl(c, "Eram os Deuses Astronautas?", 0, 0, 38), anim="up")
    show(c, t, tw("milhões", 340), 1350, 230, T("milhões de exemplares", 36, AMBER), anim="fade")
    show(c, t, tw("Nazca", 342), 1700, 400, sc(ufo_disc, t, s=0.45), anim="fade")
    HIST(c, t, [(0, "stand")], [(0, "neutral")], x=290, s=0.9)


def s24(c, t):  # 347.0 - 363.2  pistas de pouso; desenhos só para quem voa; alguém de cima teria orientado; visitantes
    aerial(c, t, 26, lines=False)
    trapezoid_top(c, 1150, 560, 120, 300, 900, 1.35, a=0.85)
    pi_ = tw("pistas", 347)
    show(c, t, pi_, 1150, 110, lambda c: hl(c, "pistas de pouso?", 0, 0, 48), anim="up", t1=tw("Ou", 355) - 0.2)
    vo = tw("voando", 352)
    if t > tw("desenhos", 351):
        glyph_at(c, t, "condor", 1550, 300, 0.9, tw("desenhos", 351), 1.2, a=0.9)
    if t > tw("alguém", 356):
        k = ease_out(clamp01((t - tw("alguém", 356)) / 3.0))
        put(c, 1150 - 500 + 500 * k, 560 - 380 + 380 * k * 0.4, lambda c: ufo_disc(c, t), 0.7)
    show(c, t, tw("Visitantes", 360), 1150, 110, lambda c: caption_box(c, "visitantes vindos de outro lugar", 44), anim="up")
    HIST(c, t, [(0, "point_r"), (tw("alguém", 356), "shrug")], [(0, "neutral"), (tw("alguém", 356), "think")], x=270, s=0.85)


def hillside(c, t, y0=980, col=(0.30, 0.19, 0.13)):
    """encosta de morro (para geoglifos em encosta)"""
    c.move_to(560, H); c.curve_to(760, 520, 1100, 260, 1460, 250); c.curve_to(1660, 250, 1800, 420, 1950, 620)
    c.line_to(W, H); c.close_path(); rgb(c, col); c.fill_preserve(); rgb(c, (0.48, 0.34, 0.24)); c.set_line_width(4); c.stroke()


def s25(c, t):  # 363.2 - 380.5  a ideia pegou; figura na encosta, olhos grandes, mão levantada: O Astronauta; ~30 m
    night(c, t, 600, (1700, 130), 90)
    pampa_side(c, t, 860, hills=False)
    hillside(c, t)
    glyph_at(c, t, "astronaut", 1240, 560, 2.6, tw("figura", 364) - 0.2, 2.4, 6, glow_a=0.05)
    show(c, t, tw("Astronauta", 366), 1240, 110, lambda c: hl(c, "\"O Astronauta\"", 0, 0, 50), anim="up")
    show(c, t, tw("trinta", 372), 1650, 860, lambda c: label_card(c, "cerca de", "30 m", 200), anim="up")
    ca = tw("capacete", 375)
    show(c, t, ca, 1240, 220, T("homem de capacete?", 36, INK), anim="fade", t1=tw("Para", 376.5) - 0.1)
    show(c, t, tw("coruja", 377), 1240, 220, T("ou uma coruja com corpo de gente?", 36, AMBER), anim="fade")
    HIST(c, t, [(0, "stand"), (tw("figura", 364), "point_r")], [(0, "neutral"), (tw("Astronauta", 366), "shocked")], x=300, s=0.95)


def s26(c, t):  # 380.5 - 399.6  problemas: chão macio, areia e cascalho; afundaria; Maria Reiche: "teriam ficado atolados"
    night(c, t, 640, (1700, 130), 80)
    pampa_side(c, t, 760)
    show(c, t, 380.7, 1150, 110, lambda c: caption_box(c, "só que a teoria tem problemas", 44), anim="up", t1=tw("O", 383) - 0.1)
    show(c, t, tw("macio", 383), 1150, 110, lambda c: hl(c, "chão macio: areia e cascalho", 0, 0, 46), anim="up",
         t1=tw("Conta-se", 392) - 0.2)
    af = tw("afundaria", 388)
    sink = ease_io(clamp01((t - af) / 2.5)) if t > af else 0
    c.save(); c.rectangle(0, 0, W, 800); c.clip()
    put(c, 1250, 640 + 120 * sink, lambda c: ufo_disc(c, t), 0.75)
    c.restore()
    if sink > 0:
        ellipse(c, 1250, 790, 200 * sink + 20, 24); rgb(c, (0.18, 0.10, 0.07)); c.fill()
    mr = tw("Maria", 392)
    reiche(c, t, 1650, 1000, 0.8, appear=mr - 0.4, exprs=((0, "happy"),), poses=((0, "point_l"),))
    show(c, t, tw("se", 395), 1250, 330, lambda c: (speech(c, 640, 150, 300, 150),
                                                     text(c, "teriam ficado atolados!", 0, 0, 40, HAND, INK)), anim="pop")
    HIST(c, t, [(0, "stand"), (af, "shrug")], [(0, "neutral"), (tw("atolados", 398), "happy")], x=300, s=0.9)


def s27(c, t):  # 399.6 - 406.5  pergunta mais simples: impossível fazer sem ver de cima?
    ground(c, t, 780)
    show(c, t, 399.8, 1150, 300, S("uma pergunta mais simples", 56, INK), anim="up")
    show(c, t, tw("Seria", 402), 1150, 470, lambda c: hl(c, "dá para desenhar sem ver de cima?", 0, 0, 48), anim="up")
    HIST(c, t, [(0, "think")], [(0, "think")], x=520, s=1.0)


def s28(c, t):  # 406.5 - 427.6  Joe Nickell testou: pessoas, estacas e cordas; condor em tamanho real; poucos dias; foto do alto
    ph = tw("fotografaram", 423) - 0.4
    if t < ph:
        ground(c, t, 700, moon_xy=None)
        show(c, t, 406.7, 1150, 110, lambda c: hl(c, "começo dos anos 1980", 0, 0, 44), anim="up", t1=tw("Joe", 410) - 0.2)
        jn = tw("Joe", 410)
        show(c, t, jn, 1150, 110, lambda c: label_card(c, "pesquisador americano", "Joe Nickell"), anim="up")
        st = tw("estacas", 413)
        xs = [700, 900, 1100, 1300, 1500]
        for i, x in enumerate(xs):
            if t > st + i * 0.25:
                put(c, x, 900 - (i % 2) * 60, lambda c: stake(c, 80), 1.0, fade_in(t, st + i * 0.25, 0.3))
        co = tw("cordas", 414)
        if t > co:
            k = ease_out(clamp01((t - co) / 1.5))
            for i in range(len(xs) - 1):
                if k * (len(xs) - 1) > i:
                    cord(c, xs[i], 900 - (i % 2) * 60 - 70, xs[i + 1], 900 - ((i + 1) % 2) * 60 - 70, 10)
        for i, x in enumerate((780, 1220, 1600)):
            figure(c, t, x, 1000, 0.75, poses=((0, "hold"),), exprs=((0, "neutral"),), shirt=[NICKELL, RED, GREEN][i],
                   hat="beanie" if i == 2 else None, hat_col=(0.3, 0.3, 0.3), fid=70 + i, appear=tw("pessoas", 412) + i * 0.2)
        show(c, t, tw("condor", 417), 1150, 300, lambda c: caption_box(c, "o condor, em tamanho real", 42), anim="up",
             t1=tw("Levou", 421) - 0.2)
        show(c, t, tw("Levou", 421), 1150, 300, lambda c: hl(c, "poucos dias", 0, 0, 48), anim="up")
        HIST(c, t, [(0, "stand")], [(0, "neutral")], x=300, s=0.9)
    else:
        c.rectangle(0, 0, W, H); rgb(c, (0.20, 0.24, 0.16)); c.fill()   # campo nos EUA visto do alto
        rnd = random.Random(3)
        for _ in range(500):
            rgb(c, (0.28, 0.32, 0.20), 0.6); c.new_sub_path(); c.arc(rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(1, 3), 0, 6.28); c.fill()
        glyph_at(c, t, "condor", 1150, 540, 3.4, ph, 0.6, 9, glow_a=0.06)
        # moldura de foto
        rrect(c, 520, 120, 1260, 860, 6); rgb(c, INK); c.set_line_width(10); c.stroke()
        show(c, t, tw("perfeita", 425), 1150, 1030, lambda c: hl(c, "quase perfeita", 0, 0, 44), anim="up")
        HIST(c, t, [(0, "point_r")], [(0, "shocked")], x=270, s=0.85)


def s29(c, t):  # 427.6 - 446.9  método antigo: figura pequena, dividida em partes, ampliada; estacas nas pontas; datação
    ground(c, t, 820, moon_xy=None)
    # figura pequena com grade
    dz = tw("Desenha-se", 430)
    def small(c):
        rrect(c, -160, -130, 320, 260, 8); fs(c, PARCH, 5)
        geoglyph(c, "hummingbird", 1.0, DARKTXT, 5)
    def grid(c):
        for k in range(-3, 4):
            line(c, k * 45, -125, k * 45, 125, 2, RED)
            line(c, -155, k * 40, 155, k * 40, 2, RED)
    show(c, t, dz, 820, 450, lambda c: (small(c), grid(c) if t > tw("divide-se", 431) else None), s=0.85, anim="pop")
    am = tw("ampliada", 433)
    if t > am:
        arrow_draw(c, t, am, 1000, 450, 1180, 450, col=AMBER)
        glyph_at(c, t, "hummingbird", 1480, 560, 2.6, am + 0.2, 2.2, 6)
    pa = tw("palpite", 437)
    show(c, t, pa, 1150, 110, lambda c: caption_box(c, "e não é só um palpite", 42), anim="up", t1=tw("Nas", 438) - 0.1)
    es = tw("estacas", 441)
    show(c, t, es - 0.2, 1150, 110, lambda c: hl(c, "restos de estacas nas pontas das linhas", 0, 0, 42), anim="up",
         t1=tw("Foi", 443) - 0.1)
    show(c, t, es, 1160, 860, sc(stake, 90), anim="pop")
    show(c, t, tw("datar", 445), 1150, 110, lambda c: date_stamp(c, "DATAÇÃO", 52, AMBER), anim="stamp")
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=300, s=0.9)


def s30(c, t):  # 446.9 - 465.9  o como já tem resposta; povo organizado; o mistério de verdade: por quê?
    aerial(c, t, 28, dark=0.35)
    glyph_at(c, t, "hummingbird", 1200, 560, 2.6, 446.9, 0.1, 6, a=0.55)
    show(c, t, 447.1, 1200, 110, lambda c: hl(c, "o COMO: cordas, estacas e tempo", 0, 0, 46), anim="up", t1=tw("mistério", 458) - 0.3)
    for i in range(4):
        native(c, t, 1500 + (i % 2) * 120, 1000 - (i // 2) * 30, 0.6, poses=((0, "hold"),), k=i, appear=tw("povo", 450) + i * 0.2)
    ms = tw("mistério", 458)
    if t > ms:
        c.rectangle(0, 0, W, H); rgb(c, (0.02, 0.01, 0.01), 0.5 * fade_in(t, ms)); c.fill()
    show(c, t, ms, 1150, 420, S("o mistério de verdade é outro", 52, INK), anim="up")
    show(c, t, tw("Por", 461), 1150, 560, lambda c: stitle(c, "POR QUÊ?", 0, 0, 120, AMBER, AMBER), anim="stamp")
    HIST(c, t, [(0, "present"), (ms, "think")], [(0, "neutral"), (ms, "think")], x=300, s=0.95)


# ================================================================== CENAS — BLOCO 4
def s31(c, t):  # 465.9 - 487.7  água: rios secos boa parte do ano; puquios (galerias, aberturas em espiral); funcionam até hoje
    pu = tw("puquios", 477)
    if t < pu - 0.3:
        ground(c, t, 760, moon_xy=(1700, 140))
        # leito de rio seco
        c.move_to(700, H); c.curve_to(900, 900, 1300, 860, 1500, 770); c.curve_to(1600, 770, 1700, 790, W, 780)
        rgb(c, (0.50, 0.40, 0.30)); c.set_line_width(40); c.stroke()
        show(c, t, 466.1, 1200, 110, lambda c: hl(c, "a resposta tem a ver com água", 0, 0, 46), anim="up", t1=tw("rios", 473) - 0.2)
        show(c, t, tw("rios", 473), 1200, 110, lambda c: caption_box(c, "rios secos boa parte do ano", 42), anim="up")
        HIST(c, t, [(0, "stand")], [(0, "neutral")], x=300, s=0.9)
    else:
        pampa_top(c, t, 30)
        put(c, 1150, 560, lambda c: puquio(c, t, 220), 1.0, fade_in(t, pu - 0.3, 0.6))
        show(c, t, pu, 1150, 110, lambda c: hl(c, "puquios", 0, 0, 52), anim="up")
        show(c, t, tw("galerias", 478), 1150, 960, lambda c: caption_box(c, "galerias subterrâneas · aberturas em espiral", 40),
             anim="up", t1=tw("Algumas", 485) - 0.2)
        show(c, t, tw("Algumas", 485), 1150, 960, lambda c: hl(c, "alguns funcionam até hoje", 0, 0, 44), anim="up")
        HIST(c, t, [(0, "point_r")], [(0, "happy")], x=280, s=0.85)


def s32(c, t):  # 487.7 - 508.9  Reinhard: culto às montanhas e à água; linhas apontam para montanhas e rios; Johnson: água subterrânea
    c.rectangle(0, 0, W, H); rgb(c, (0.08, 0.06, 0.05)); c.fill()
    put(c, 1150, 520, lambda c: mountains(c, 1500, 380, False, (0.26, 0.20, 0.16)), 1.0)
    jr = tw("Johan", 490)
    show(c, t, jr, 1150, 110, lambda c: label_card(c, "antropólogo, anos 1980", "Johan Reinhard", 520), anim="up",
         t1=tw("Outro", 501) - 0.2)
    c.rectangle(0, 520, W, H - 520); rgb(c, PAMPA); c.fill()
    ap = tw("apontam", 495)
    for i, (x0, x1) in enumerate(((700, 900), (1150, 1150), (1600, 1350))):
        if t > ap + i * 0.3:
            k = ease_out(clamp01((t - ap - i * 0.3) / 1.2))
            line(c, x0, 1000, x0 + (x1 - x0) * k, 1000 - 460 * k, 8, GLYPH)
    if t > tw("chuva", 497):
        for k in range(14):
            yy = 200 + ((t * 300 + k * 37) % 220)
            line(c, 900 + k * 40, yy, 896 + k * 40, yy + 16, 3, (0.55, 0.70, 0.86))
    dj = tw("David", 501)
    show(c, t, dj, 1150, 110, lambda c: label_card(c, "pesquisador", "David Johnson", 400), anim="up")
    if t > tw("água", 505):
        a_ = fade_in(t, tw("água", 505))
        put(c, 1150, 900, lambda c: (c.set_dash([16, 12]), line(c, -600, 0, 600, -40, 10, (0.40, 0.62, 0.82)), c.set_dash([])), 1.0, a_)
        show(c, t, tw("água", 505), 1150, 960, T("água correndo por baixo da terra", 34, (0.60, 0.78, 0.92)), anim="fade")
    HIST(c, t, [(0, "point_r")], [(0, "neutral"), (dj, "think")], x=280, y=1010, s=0.85)


def s33(c, t):  # 508.9 - 522.5  um detalhe: figuras feitas com uma única linha contínua; entra, percorre e sai: um caminho
    aerial(c, t, 32, lines=False, n=0)
    un = tw("única", 511)
    glyph_at(c, t, "monkey", 1150, 560, 2.8, 509.0, 0.1, 6, a=0.55)
    en = tw("entra", 515)
    if t > en:
        p = clamp01((t - en) / 6.0)
        put(c, 1150, 560, lambda c: geoglyph(c, "monkey", p, AMBER, 8 / 2.8), 2.8)
        hx, hy = glyph_head_pos("monkey", p)
        native(c, t, 1150 + hx * 2.8, 560 + hy * 2.8 + 30, 0.22, poses=((0, "run"),), k=2)
    show(c, t, 509.1, 1150, 110, lambda c: hl(c, "um detalhe que muda tudo", 0, 0, 46), anim="up", t1=un - 0.2)
    show(c, t, un, 1150, 110, lambda c: caption_box(c, "uma única linha contínua", 44), anim="up", t1=tw("Como", 520) - 0.2)
    show(c, t, tw("Como", 520), 1150, 110, lambda c: stitle(c, "como um caminho", 0, 0, 60, AMBER, AMBER), anim="up")
    HIST(c, t, [(0, "point_r")], [(0, "think"), (tw("Como", 520), "shocked")], x=260, s=0.8)


def s34(c, t):  # 522.5 - 544.9  percorridas a pé, em procissão, música e oferendas; cerâmica quebrada; Cahuachi, pirâmides de adobe
    ground(c, t, 740)
    pr = tw("procissão", 527)
    show(c, t, tw("Cahuachi", 538) - 0.2, 1640, 760, sc(pyramid, 300, 150), anim="fade")
    for i in range(6):
        x = 700 + ((t - pr) * 40 + i * 140) % 840 if t > pr else 700 + i * 140
        native(c, t, x, 960 - (i % 2) * 14, 0.6, poses=((0, "run" if t > pr else "stand"),), k=i, appear=522.6 + i * 0.15)
    show(c, t, 522.7, 1250, 110, lambda c: hl(c, "linhas para serem percorridas a pé", 0, 0, 44), anim="up", t1=pr - 0.2)
    show(c, t, pr, 1250, 110, lambda c: caption_box(c, "procissão · música · oferendas", 42), anim="up", t1=tw("Ao", 533) - 0.2)
    if t > tw("música", 528):
        music_notes(c, t, 1100, 600, 4, AMBER, 200) if "music_notes" in globals() else None
    ce = tw("cerâmica", 534)
    show(c, t, ce, 1150, 1010, sc(shards, 2, 7, 160), anim="pop")
    show(c, t, ce, 1250, 110, lambda c: caption_box(c, "cerâmica quebrada de propósito", 42), anim="up", t1=tw("Cahuachi", 538) - 0.4)
    ca = tw("Cahuachi", 538)
    show(c, t, ca, 1250, 110, lambda c: label_card(c, "centro cerimonial", "Cahuachi", 420), anim="up")
    fog(c, t, 900, 0.07)
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=300, s=0.9)


def s35(c, t):  # 544.9 - 554.3  ninguém precisava ver de cima; bastava caminhar; talvez quem tinha que ver eram os deuses
    aerial(c, t, 34, dark=0.3, n=5)
    glyph_at(c, t, "hummingbird", 1150, 600, 2.6, 545.0, 0.1, 6)
    ca = tw("caminhar", 548)
    if t > ca:
        p = clamp01((t - ca) / 5)
        hx, hy = glyph_head_pos("hummingbird", p)
        native(c, t, 1150 + hx * 2.6, 600 + hy * 2.6 + 26, 0.22, poses=((0, "run"),), k=1)
    de = tw("deuses", 551)
    if t > de - 0.5:
        glow(c, 1150, 0, 700, LYELLOW, 0.22 * fade_in(t, de - 0.5, 1.5))
    show(c, t, 545.1, 1150, 110, lambda c: caption_box(c, "bastava caminhar por ele", 42), anim="up", t1=tw("Ou", 550) - 0.2)
    show(c, t, tw("deuses", 551), 1150, 110, lambda c: hl(c, "ou quem via eram os deuses?", 0, 0, 46), anim="up")
    HIST(c, t, [(0, "stand"), (de, "point_ru")], [(0, "think"), (de, "think")], x=270, s=0.85)


def s36(c, t):  # 554.3 - 559.6  quase um século depois de Mejía Xesspe, uma surpresa
    aerial(c, t, 36, dark=0.5)
    show(c, t, 554.5, 1150, 420, S("quase um século depois...", 60, INK), anim="up")
    show(c, t, tw("surpresa", 556), 1150, 580, lambda c: stitle(c, "uma surpresa", 0, 0, 90, AMBER, AMBER), anim="stamp")
    HIST(c, t, [(0, "finger_up")], [(0, "think")], x=300, s=0.95)


def ai_screen(c, t, t0, n_boxes=9, w=960, h=600, seed=5, hits=(1, 4, 7)):
    """tela: imagem aérea com caixas de detecção aparecendo"""
    rrect(c, -w / 2 - 20, -h / 2 - 20, w + 40, h + 40, 16); fs(c, (0.12, 0.13, 0.15), 6)
    c.save(); c.rectangle(-w / 2, -h / 2, w, h); c.clip()
    c.translate(-w / 2, -h / 2); c.scale(w / W, h / H)
    pampa_top(c, t, seed, nazca_lines_set(seed, 5))
    c.restore()
    rnd = random.Random(seed)
    for k in range(n_boxes):
        x, y = rnd.uniform(-w / 2 + 70, w / 2 - 70), rnd.uniform(-h / 2 + 70, h / 2 - 70)
        if t > t0 + k * 0.5:
            hit = k in hits
            if hit:
                put(c, x, y, lambda c: geoglyph(c, ["head", "llama", "orca"][k % 3], 1.0, GLYPH, 6), 0.35)
            col = (0.30, 0.90, 0.70) if hit else (0.90, 0.80, 0.40)
            put(c, x, y, lambda c: scan_box(c, 110, 90, t, col), 1.0)


def s37(c, t):  # 559.6 - 579.2  Yamagata (Japão) estuda Nazca; com a IBM, uma IA em imagens de altíssima resolução; 1.300 lugares
    c.rectangle(0, 0, W, H); rgb(c, (0.06, 0.06, 0.07)); c.fill()
    ya = tw("Yamagata", 563)
    show(c, t, ya, 1150, 110, lambda c: label_card(c, "Japão", "Universidade de Yamagata", 620), anim="up", t1=tw("Em", 564) - 0.1)
    ib = tw("IBM", 565)
    show(c, t, ib, 1150, 110, lambda c: hl(c, "+ IBM: inteligência artificial", 0, 0, 46), anim="up", t1=tw("máquina", 572) - 0.2)
    ia = tw("inteligência", 566)
    show(c, t, ia, 1150, 560, lambda c: ai_screen(c, t, ia + 1.0, 14, 960, 600, 5, ()), anim="up")
    mq = tw("máquina", 572)
    show(c, t, mq, 1150, 110, lambda c: counter_lbl(c, "+ de 1.300", "lugares suspeitos", AMBER, 70), anim="up")
    show(c, t, tw("campo", 577), 1150, 960, lambda c: caption_box(c, "e a equipe foi a campo conferir", 40), anim="up")
    HIST(c, t, [(0, "point_r")], [(0, "neutral")], x=260, s=0.8)


def s38(c, t):  # 579.2 - 595.9  em seis meses (2022-2023), 303 figuras novas; antes ~430; estudo de 2024: salto enorme
    aerial(c, t, 38, dark=0.35, n=6)
    show(c, t, 579.4, 1150, 110, lambda c: date_stamp(c, "6 MESES · 2022-2023", 48, AMBER), anim="stamp")
    tr = tw("trezentas", 583)
    show(c, t, tr, 1350, 420, lambda c: counter_lbl(c, "303", "figuras novas", AMBER, 140), anim="pop")
    qa = tw("quatrocentas", 588)
    show(c, t, qa - 0.3, 900, 420, lambda c: counter_lbl(c, "~430", "conhecidas antes", GRAY, 100), anim="up")
    es = tw("estudo", 590)
    if t > es:
        h1 = 430 * 0.55; h2 = (430 + 303) * 0.55 * ease_out(clamp01((t - es) / 2.0))
        c.rectangle(860, 900 - h1 * 0.6, 80, h1 * 0.6); rgb(c, GRAY); c.fill()
        c.rectangle(1310, 900 - h2 * 0.6, 80, h2 * 0.6); rgb(c, AMBER); c.fill()
        line(c, 760, 900, 1500, 900, 4)
        text(c, "antes", 900, 940, 30, TYPE, INK); text(c, "depois", 1350, 940, 30, TYPE, INK)
    show(c, t, es, 1150, 1020, T("estudo publicado em 2024", 32, INK), anim="fade")
    HIST(c, t, [(0, "present")], [(0, "neutral"), (tr, "shocked")], x=270, s=0.85)


def s39(c, t):  # 595.9 - 615.3  figuras novas diferentes: pequenas, quase invisíveis; pessoas, cabeças, lhamas, aves, orcas; trilhas
    aerial(c, t, 40, lines=False)
    # trilha antiga sinuosa
    c.move_to(150, 900); c.curve_to(600, 700, 900, 980, 1300, 760); c.curve_to(1600, 600, 1750, 700, 1850, 560)
    rgb(c, (0.66, 0.56, 0.42), 0.8); c.set_line_width(14); c.stroke()
    pe = tw("pequenas", 598)
    show(c, t, 596.1, 1150, 110, lambda c: hl(c, "as figuras novas são diferentes", 0, 0, 46), anim="up", t1=pe - 0.2)
    show(c, t, pe, 1150, 110, lambda c: caption_box(c, "pequenas · poucos metros · quase invisíveis", 40), anim="up",
         t1=tw("Mostram", 604) - 0.2)
    items = [("head", tw("pessoas", 604), 600, 560), ("head", tw("cabeças", 605), 820, 470), ("llama", tw("lhamas", 605), 1040, 600),
             ("condor", tw("aves", 607), 1300, 470), ("orca", tw("orcas", 608), 1560, 430)]
    for k, tt, x, y in items:
        glyph_at(c, t, k, x, y, 0.75, tt - 0.2, 0.8)
        if t > tt:
            put(c, x, y, lambda c: scan_box(c, 190, 170, t, (0.30, 0.90, 0.70)), 1.0, fade_in(t, tt, 0.3))
    show(c, t, tw("Mostram", 604), 1150, 110, lambda c: caption_box(c, "pessoas, cabeças, lhamas, aves, orcas", 40), anim="up",
         t1=tw("espalhadas", 612) - 0.3)
    show(c, t, tw("espalhadas", 612), 1150, 110, lambda c: hl(c, "ao longo de antigas trilhas", 0, 0, 46), anim="up")
    HIST(c, t, [(0, "point_r")], [(0, "neutral"), (tw("orcas", 608), "shocked")], x=260, s=0.8)


def s40(c, t):  # 615.3 - 638.3  murais para quem caminhava; figuras de linha para rituais; talvez não para o céu: para os pés
    ground(c, t, 720, moon_xy=None)
    mu = tw("murais", 621)
    if t > mu - 0.3:
        glyph_at(c, t, "llama", 1150, 860, 1.0, mu - 0.3, 1.0)
        glyph_at(c, t, "head", 1400, 870, 0.7, mu, 1.0)
    for i in range(3):
        native(c, t, 820 + i * 110, 1010, 0.7, poses=((0, "point_r" if i == 0 else "stand"),), k=i + 2, appear=615.5 + i * 0.2)
    show(c, t, 615.5, 1200, 110, lambda c: caption_box(c, "para os pesquisadores...", 42), anim="up", t1=mu - 0.2)
    show(c, t, mu, 1200, 110, lambda c: hl(c, "murais para quem caminhava", 0, 0, 46), anim="up", t1=tw("Já", 623) - 0.2)
    show(c, t, tw("Já", 623), 1200, 110, lambda c: caption_box(c, "grandes figuras: rituais da comunidade", 42), anim="up",
         t1=tw("Ou", 629) - 0.2)
    ce = tw("céu", 632)
    show(c, t, tw("talvez", 630), 1200, 110, lambda c: hl(c, "talvez nunca tenham sido feitas para o céu", 0, 0, 42), anim="up",
         t1=tw("Talvez", 634) - 0.2)
    pe = tw("pés", 636)
    show(c, t, tw("Talvez", 634), 1200, 110, lambda c: stitle(c, "talvez tenham sido feitas para os pés", 0, 0, 52, AMBER, AMBER),
         anim="up")
    if t > tw("Talvez", 634):
        put(c, 900, 1050, lambda c: footprints(c, 8, 80, -10, t, tw("Talvez", 634), (0.80, 0.70, 0.52)), 1.0)
    HIST(c, t, [(0, "stand"), (pe, "present")], [(0, "neutral"), (ce, "think"), (pe, "happy")], x=300, s=0.9)


# ================================================================== CENAS — BLOCO 5
def s41(c, t):  # 638.3 - 647.4  o deserto que guardou os desenhos por 2.000 anos é frágil; uma pegada pode durar séculos
    aerial(c, t, 42, n=4)
    glyph_at(c, t, "hummingbird", 1150, 540, 2.4, 638.4, 0.1, 6, a=0.8)
    pg = tw("pegada", 643)
    if t > pg:
        put(c, 1500, 860, lambda c: footprints(c, 5, 70, -16, t, pg, (0.62, 0.50, 0.36)), 1.6)
    show(c, t, 638.6, 1150, 110, lambda c: hl(c, "um deserto frágil", 0, 0, 48), anim="up", t1=pg - 0.2)
    show(c, t, pg, 1150, 110, lambda c: caption_box(c, "uma pegada pode durar séculos", 44), anim="up")
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=270, s=0.85)


def s42(c, t):  # 647.4 - 663.5  dezembro de 2014: ativistas do Greenpeace ao lado do beija-flor; pegadas marcadas; indignação
    aerial(c, t, 44, n=3)
    glyph_at(c, t, "hummingbird", 1000, 540, 2.4, 647.5, 0.1, 6)
    show(c, t, 647.6, 1250, 110, lambda c: date_stamp(c, "DEZEMBRO DE 2014", 52, AMBER), anim="stamp", t1=tw("pegadas", 657) - 0.3)
    at_ = tw("ativistas", 650)
    for i in range(4):
        if t > at_ + i * 0.3:
            figure(c, t, 1420 + i * 70, 640 + (i % 2) * 30, 0.32, poses=((0, "hold"),), exprs=((0, "neutral"),),
                   shirt=(0.30, 0.55, 0.30), fid=80 + i, appear=at_ + i * 0.3)
    show(c, t, tw("mensagem", 652), 1500, 820, lambda c: (rrect(c, -220, -40, 440, 80, 6), fs(c, (0.80, 0.78, 0.70), 3),
                                                          text(c, "mensagem sobre energia", 0, 0, 26, TYPE, DARKTXT)), anim="fade",
         t1=tw("pegadas", 657))
    pg = tw("pegadas", 657)
    if t > pg:
        put(c, 1300, 720, lambda c: footprints(c, 7, 50, -20, t, pg, (0.92, 0.84, 0.66)), 1.4)
        put(c, 1360, 800, lambda c: footprints(c, 6, 50, -12, t, pg + 0.3, (0.92, 0.84, 0.66)), 1.4)
    show(c, t, pg, 1250, 110, lambda c: caption_box(c, "as pegadas ficaram marcadas no chão", 42), anim="up", t1=tw("governo", 659) - 0.2)
    show(c, t, tw("governo", 659), 1250, 110, lambda c: hl(c, "o governo do Peru reagiu com indignação", 0, 0, 42), anim="up")
    HIST(c, t, [(0, "stand"), (pg, "head")], [(0, "neutral"), (pg, "worried")], x=270, s=0.85)


def s43(c, t):  # 663.5 - 681.3  2018: caminhoneiro passou por cima de três geoglifos; 2025: reserva reduzida em 42%; voltou atrás
    re = tw("reduzir", 670) - 1.5
    if t < re:
        aerial(c, t, 46, n=5)
        for i, (k, x, y) in enumerate((("trapezoid", 700, 520), ("spiral", 1150, 560), ("trapezoid", 1550, 500))):
            put(c, x, y, lambda c, k=k: geoglyph(c, k, 1.0, GLYPH, 6), 1.3)
        cm = tw("caminhoneiro", 666)
        if t > cm:
            k = clamp01((t - cm) / 3.5)
            # marcas de pneu atravessando
            line(c, 520, 900, 520 + 1300 * k, 900 - 600 * k, 10, (0.12, 0.08, 0.06))
            line(c, 560, 930, 560 + 1300 * k, 930 - 600 * k, 10, (0.12, 0.08, 0.06))
            put(c, 540 + 1300 * k, 915 - 600 * k, lambda c: (rrect(c, -70, -36, 140, 72, 10), fs(c, (0.40, 0.42, 0.46), 5),
                                                              rrect(c, 20, -30, 44, 60, 6), fs(c, LBLUE, 3)), 1.0,
                rot=-math.atan2(600, 1300))
        show(c, t, 663.7, 1150, 110, lambda c: date_stamp(c, "2018", 60, AMBER), anim="stamp", t1=tw("três", 668) - 0.2)
        show(c, t, tw("três", 668), 1150, 110, lambda c: caption_box(c, "três geoglifos danificados", 44), anim="up")
        HIST(c, t, [(0, "head")], [(0, "worried")], x=270, s=0.85)
    else:
        peru = make_proj(-76.2, -74.2, -15.6, -14.0)
        c.rectangle(0, 0, W, H); rgb(c, PAMPA_D); c.fill()
        a_ = clamp01((t - (re + 1.5)) / 1.5)
        vt = tw("voltou", 678)
        cut = a_ if t < vt else max(0, 1 - (t - vt) / 1.0)
        # área da reserva (retângulo) com 42% cortado e depois de volta
        rrect(c, 640, 260, 1000, 600, 10); rgb(c, (0.42, 0.30, 0.20)); c.fill_preserve(); rgb(c, AMBER); c.set_line_width(5); c.stroke()
        if cut > 0:
            c.rectangle(640 + 1000 * (1 - 0.42 * cut), 260, 1000 * 0.42 * cut, 600); rgb(c, (0.10, 0.06, 0.05), 0.85); c.fill()
            c.save(); c.set_dash([16, 10]); line(c, 640 + 1000 * (1 - 0.42 * cut), 250, 640 + 1000 * (1 - 0.42 * cut), 870, 5, RED); c.restore()
        put(c, 1000, 560, lambda c: geoglyph(c, "hummingbird", 1.0, GLYPH, 6), 1.6)
        show(c, t, re + 0.2, 1140, 120, lambda c: date_stamp(c, "2025", 56, AMBER), anim="stamp")
        show(c, t, re + 1.6, 1460, 560, lambda c: counter_lbl(c, "-42%", "área da reserva", RED, 90), anim="pop", t1=vt)
        show(c, t, tw("garimpo", 677), 1140, 960, lambda c: caption_box(c, "região com garimpo ilegal", 40), anim="up", t1=vt - 0.2)
        show(c, t, vt, 1140, 960, lambda c: hl(c, "depois das críticas, voltou atrás", 0, 0, 44), anim="up")
        HIST(c, t, [(0, "think"), (vt, "present")], [(0, "worried"), (vt, "neutral")], x=270, s=0.85)


def s44(c, t):  # 681.3 - 702.2  o deserto revela segredos; 2020, obra num mirante: o gato na encosta, ~37 m; Paracas; escondido
    night(c, t, 600, (1700, 130), 90)
    pampa_side(c, t, 860, hills=False)
    hillside(c, t)
    show(c, t, 681.5, 1240, 110, lambda c: caption_box(c, "o deserto continua revelando segredos", 42), anim="up",
         t1=tw("dois", 685) - 0.2)
    show(c, t, tw("dois", 685), 1240, 110, lambda c: date_stamp(c, "2020", 60, AMBER), anim="stamp", t1=tw("Ele", 693) - 0.2)
    mi = tw("mirante", 689)
    show(c, t, mi - 0.3, 1720, 1000, sc(mirador, 300, s=0.9), anim="up")
    gt = tw("gato", 691)
    glyph_at(c, t, "cat", 1250, 520, 2.4, gt - 0.4, 1.8, 6, glow_a=0.05)
    show(c, t, tw("trinta", 693), 1250, 760, lambda c: label_card(c, "cerca de", "37 m", 200), anim="up")
    show(c, t, tw("Paracas", 694), 1240, 110, lambda c: hl(c, "provavelmente do povo Paracas", 0, 0, 44), anim="up", t1=tw("E", 698) - 0.1)
    show(c, t, tw("escondido", 699), 1240, 110, lambda c: caption_box(c, "escondido ali o tempo todo", 44), anim="up")
    HIST(c, t, [(0, "stand"), (gt, "point_r")], [(0, "neutral"), (gt, "shocked")], x=300, s=0.9)


def s45(c, t):  # 702.2 - 722.9  não foi o único: 2018, drones, dezenas de figuras perto de Palpa; Paracas; encostas viradas para o vale
    night(c, t, 600, (1720, 130), 90)
    pampa_side(c, t, 900, hills=False)
    # encosta à direita, vale à esquerda
    c.move_to(900, H); c.curve_to(1100, 640, 1350, 330, 1700, 300); c.line_to(W, 300); c.line_to(W, H); c.close_path()
    rgb(c, (0.30, 0.19, 0.13)); c.fill_preserve(); rgb(c, (0.48, 0.34, 0.24)); c.set_line_width(4); c.stroke()
    dr = tw("drones", 706)
    if t > dr:
        put(c, 1000 + 300 * math.sin((t - dr) * 0.5), 260 + 20 * math.sin(t * 2), lambda c: drone(c, t), 0.8, fade_in(t, dr - 0.3))
    show(c, t, 702.4, 1050, 110, lambda c: date_stamp(c, "2018 · PALPA", 52, AMBER), anim="stamp", t1=tw("Muitas", 709) - 0.2)
    show(c, t, dr, 1050, 200, T("dezenas de figuras novas", 36, INK), anim="fade", t1=tw("Muitas", 709) - 0.2)
    glyph_at(c, t, "head", 1420, 520, 1.0, tw("figuras", 708), 1.0)
    glyph_at(c, t, "astronaut", 1620, 470, 0.8, tw("figuras", 708) + 0.6, 1.0)
    show(c, t, tw("Muitas", 709), 1050, 110, lambda c: hl(c, "também dos Paracas, séculos antes", 0, 0, 44), anim="up",
         t1=tw("detalhe", 714) - 0.2)
    show(c, t, tw("encostas", 717), 1050, 110, lambda c: caption_box(c, "desenhadas em encostas, viradas para o vale", 40),
         anim="up", t1=tw("Quem", 720) - 0.2)
    vi = tw("Quem", 720)
    for i in range(3):
        native(c, t, 640 + i * 90, 1000, 0.65, poses=((0, "point_r" if i == 1 else "stand"),), k=i, appear=vi - 0.3 + i * 0.15)
    show(c, t, vi, 1050, 110, lambda c: hl(c, "quem vivia lá embaixo conseguia ver", 0, 0, 44), anim="up")
    HIST(c, t, [(0, "stand"), (vi, "present")], [(0, "neutral"), (vi, "happy")], x=280, s=0.85)


def s46(c, t):  # 722.9 - 735.6  o que a gente sabe: quem fez; como; nenhuma evidência de extraterrestres
    c.rectangle(0, 0, W, H); rgb(c, (0.07, 0.05, 0.04)); c.fill()
    show(c, t, 723.0, 1150, 110, lambda c: stitle(c, "o que a gente sabe", 0, 0, 64, INK, AMBER), anim="up")
    qf = tw("quem", 725)
    co = tw("como", 728)
    et = tw("extraterrestres", 733)
    show(c, t, qf, 760, 540, lambda c: card(c, "QUEM", "Paracas e Nazca", lambda c: nazca_vase(c, 0.8), w=340, h=420), anim="up")
    show(c, t, co, 1150, 540, lambda c: card(c, "COMO", "estacas e cordas", lambda c: (stake(c, 90), cord(c, 0, -80, 80, -60)), w=340, h=420),
         anim="up")
    show(c, t, tw("evidência", 732), 1540, 540, lambda c: card(c, "ETs?", "nenhuma evidência", lambda c: sc(ufo_disc, t, s=0.5)(c),
                                                               crossed=clamp01((t - et) / 0.4), w=340, h=420), anim="up")
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=260, s=0.8)


def s47(c, t):  # 735.6 - 755.2  o porquê continua aberto: procissão? chuva? água escondida? murais? deuses? Não deixaram nada escrito
    aerial(c, t, 48, dark=0.45)
    show(c, t, 735.8, 1150, 110, lambda c: stitle(c, "mas o PORQUÊ continua aberto", 0, 0, 56, INK, AMBER), anim="up")
    opts = [("caminhos de procissão?", tw("caminhos", 738)), ("pedidos de chuva?", tw("Pedidos", 739)),
            ("mapas da água escondida?", tw("Mapas", 741)), ("murais para quem passava?", tw("Murais", 742)),
            ("mensagens para os deuses?", tw("mensagens", 744))]
    for i, (s, tt) in enumerate(opts):
        show(c, t, tt, 1150, 260 + i * 92, lambda c, s=s: hl(c, s, 0, 0, 40), anim="left", t1=tw("Os", 750) - 0.2)
    show(c, t, tw("Talvez", 747), 1150, 760, T("talvez tudo isso, em épocas diferentes", 36, AMBER), anim="fade", t1=tw("Os", 750) - 0.2)
    ne = tw("Os", 750)
    show(c, t, ne, 1150, 480, S("não deixaram nada escrito", 60, INK), anim="up")
    de = tw("desenho", 754)
    show(c, t, tw("Deixaram", 752), 1150, 620, lambda c: stitle(c, "só o desenho", 0, 0, 80, AMBER, AMBER), anim="up")
    if t > ne:
        glyph_at(c, t, "hummingbird", 1150, 820, 1.2, ne + 0.5, 2.0, 5)
    HIST(c, t, [(0, "think")], [(0, "think")], x=270, s=0.85)


def s48(c, t):  # 755.2 - 771.5  ainda hoje, um avião pequeno sobrevoa e o beija-flor aparece; feito para ser visto de onde nunca estiveram
    aerial(c, t, 50, n=6)
    glyph_at(c, t, "hummingbird", 1150, 560, 3.0, tw("beija-flor", 761) - 1.0, 2.5, 7, glow_a=0.05)
    plane_top_over(c, t, 755.3, 14.0, 300, -250, 2200, 0.75)
    show(c, t, tw("sensação", 762), 1150, 960, lambda c: caption_box(c, "a mesma sensação dos primeiros pilotos", 40), anim="up",
         t1=tw("De", 764) - 0.2)
    show(c, t, tw("lugar", 766), 1150, 960, lambda c: hl(c, "visto de onde nenhum deles jamais esteve", 0, 0, 42), anim="up")
    HIST(c, t, [(0, "stand"), (tw("lugar", 766), "point_ru")], [(0, "neutral"), (tw("lugar", 766), "think")], x=270, s=0.85)


def s49(c, t):  # 771.5 - 782.0  e você? para quem desenharam? deuses, água, quem caminhava? deixa sua teoria
    c.rectangle(0, 0, W, H); rgb(c, (0.07, 0.05, 0.04)); c.fill()
    show(c, t, 771.6, 1150, 100, lambda c: stitle(c, "E você?", 0, 0, 72, INK, AMBER), anim="up")
    opts = (("para os deuses?", tw("deuses", 775), lambda c: (glow(c, 0, 0, 120, LYELLOW, 0.3), sc(big_q, 90, AMBER)(c))),
            ("para a água?", tw("água", 776), lambda c: puquio(c, t, 70)),
            ("quem caminhava?", tw("caminhava", 777), lambda c: footprints(c, 4, 40, -10, None, 0, GLYPH)))
    for i, (s, tt, ic) in enumerate(opts):
        show(c, t, tt, 740 + i * 410, 500, lambda c, s=s, ic=ic, i=i: card(c, str(i + 1), s, ic, w=380, h=400), anim="up")
    show(c, t, tw("Deixa", 779), 1150, 900, lambda c: (speech(c, 820, 130, -300, 110), text(c, "deixe sua teoria nos comentários", 0, 0, 42, HAND, INK)),
         anim="pop")
    HIST(c, t, [(0, "point_r"), (779.5, "present")], [(0, "think"), (779.5, "happy")], x=240, s=0.8)


def s50(c, t):  # 782.0 - fim  encerramento
    aerial(c, t, 52, dark=0.55)
    glyph_at(c, t, "hummingbird", 1690, 800, 1.5, 782.0, 0.1, 5, a=0.35)
    HIST(c, t, [(0, "stand"), (782.2, "present"), (784.8, "wave"), (786.8, "stand")], [(0, "neutral"), (783.4, "happy")], x=420, s=1.05)
    show(c, t, 782.1, 1100, 260, T("Eu sou o Historiador.", 44, AMBER), anim="fade")
    show(c, t, 783.6, 1100, 470, sc(subscribe_btn, t > 785.0, s=0.9))
    show(c, t, 784.0, 1430, 470, sc(bell, s=0.8), rot=math.sin(t * 18) * 0.2 * max(0, 1 - (t - 784.0)))
    show(c, t, 784.6, 1100, 720, lambda c: (text(c, "PONTO CEGO", 0, 0, 84, SERIF, INK), line(c, -300, 58, 300, 58, 3, AMBER)), anim="fade", d=1.2)
    fog(c, t, 980, 0.09)


SCENES = [
    (0.0, 13.2, s01), (13.2, 31.4, s02), (31.4, 42.2, s03), (42.2, 53.4, s04), (53.4, 59.5, s05), (59.5, 62.9, s06),
    (62.9, 79.1, s07), (79.1, 98.7, s08), (98.7, 114.3, s09), (114.3, 130.6, s10), (130.6, 156.0, s11),
    (156.0, 171.6, s12), (171.6, 193.2, s13), (193.2, 207.7, s14), (207.7, 222.9, s15), (222.9, 231.2, s16),
    (231.2, 246.4, s17), (246.4, 262.5, s18), (262.5, 274.8, s19), (274.8, 297.5, s20), (297.5, 324.6, s21),
    (324.6, 329.2, s22), (329.2, 347.0, s23), (347.0, 363.2, s24), (363.2, 380.5, s25), (380.5, 399.6, s26),
    (399.6, 406.5, s27), (406.5, 427.6, s28), (427.6, 446.9, s29), (446.9, 465.9, s30),
    (465.9, 487.7, s31), (487.7, 508.9, s32), (508.9, 522.5, s33), (522.5, 544.9, s34), (544.9, 554.3, s35),
    (554.3, 559.6, s36), (559.6, 579.2, s37), (579.2, 595.9, s38), (595.9, 615.3, s39), (615.3, 638.3, s40),
    (638.3, 647.4, s41), (647.4, 663.5, s42), (663.5, 681.3, s43), (681.3, 702.2, s44), (702.2, 722.9, s45),
    (722.9, 735.6, s46), (735.6, 755.2, s47), (755.2, 771.5, s48), (771.5, 782.0, s49), (782.0, 999.0, s50),
]

SFX_OFF = True
SFX = [(0.4, "tum"), (59.6, "boom"), (98.9, "tum"), (216.0, "heartbeat"), (225.3, "boom"), (270.2, "tum"),
       (329.3, "boom"), (366.4, "heartbeat"), (423.5, "boom"), (461.2, "heartbeat"), (511.4, "tum"), (583.0, "boom"),
       (634.5, "boom"), (691.5, "heartbeat"), (733.0, "tum"), (752.8, "boom"), (784.6, "boom")]
