"""O desaparecimento do voo Varig 967 (1979) — Ponto Cego.
Narração: Pedro Lima - Serious (HeyGen / ElevenLabs v4), 4 blocos com 1 s de silêncio entre eles (~751,5 s).
Tempos absolutos (já com os offsets dos blocos): transcricao.txt e palavras.json (gerados por tempos.py).
tw("palavra", depois_de) devolve o início da primeira palavra que começa com esse texto depois do tempo dado.
Objetos do caso (Boeing 707 cargueiro, caça, caixotes, telas abstratas, mapa do Pacífico Norte...) ficam no engine.py
(seção VARIG 967). As telas são abstrações genéricas, não reproduções de obras reais.
"""
import json
import os
import unicodedata

from engine import *

THEME = "mar"

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


def night(c, t, horizon=700, moon_xy=(1640, 160), n=80):
    stars(c, t, n, horizon - 40)
    if moon_xy:
        c.save(); c.translate(*moon_xy); moon(c, 50); c.restore()
        glow(c, moon_xy[0], moon_xy[1], 220, ICE, 0.10)


def ocean(c, t, y=700, rough=0.0):
    g = cairo.LinearGradient(0, y, 0, H)
    g.add_color_stop_rgb(0, 0.06, 0.11, 0.17)
    g.add_color_stop_rgb(1, 0.02, 0.04, 0.07)
    c.rectangle(0, y, W, H - y); c.set_source(g); c.fill()
    for row in range(4):
        yy = y + 18 + row * 70
        off = (t * (22 + row * 8)) % 160
        for i in range(-1, 14):
            x = i * 160 + off - 160 + row * 40
            c.move_to(x, yy); c.curve_to(x + 40, yy - 10 - rough * 10, x + 80, yy - 10 - rough * 10, x + 120, yy)
        rgb(c, (0.30, 0.44, 0.60), 0.55 - row * 0.1); c.set_line_width(3); c.stroke()


def plane(c, t, x, y, s=0.6, a=1.0, ang=0.0, **kw):
    faded(c, a, lambda c: (c.save(), c.translate(x, y), c.rotate(ang), c.scale(s, s), b707(c, t, **kw), c.restore()))


def bubble(c, s, w=None, size=40, tx=-80, ty=90, col=INK):
    ww = w or text_w(c, s, size, HAND) + 80
    speech(c, ww, 110, tx, ty)
    text(c, s, 0, 0, size, HAND, col)


def label_card(c, top, name, w=None, top_col=AMBER):
    ww = w or max(text_w(c, name, 44, SERIF), text_w(c, top, 30, TYPE)) + 70
    rrect(c, -ww / 2, -62, ww, 124, 12); fs(c, (0.08, 0.10, 0.14), 4, (0.55, 0.62, 0.72))
    text(c, top, 0, -26, 30, TYPE, top_col)
    text(c, name, 0, 22, 44, SERIF, INK)


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
    full = f"{n}  ·  {title_s}"
    w = text_w(c, full, 52, SERIF) + 90
    rrect(c, -w / 2, -48, w, 96, 14); fs(c, (0.10, 0.12, 0.15), 5, ICE)
    text(c, n, -w / 2 + 50, 0, 44, TYPE, AMBER)
    text(c, title_s, 30, 0, 52, SERIF, INK)


def crew_fig(c, t, x, y, s=0.75, poses=((0, "stand"),), exprs=((0, "neutral"),), appear=None, fid=30, alpha=1.0, mustache=False):
    faded(c, alpha, lambda c: pilot(c, t, x, y, s, poses, exprs, fid=fid, appear=appear, mustache=mustache,
                                     coat=(0.14, 0.17, 0.26)))


def hold(c, t, glow_on=0.0, n_paint=3, paint_a=1.0):
    """porão de carga visto de dentro: caixotes e telas presas em paletes"""
    c.move_to(140, 980); c.line_to(420, 180); c.line_to(1500, 180); c.line_to(1780, 980); c.close_path()
    rgb(c, (0.07, 0.08, 0.10)); c.fill_preserve(); rgb(c, (0.30, 0.34, 0.40)); c.set_line_width(4); c.stroke()
    for k in range(6):
        x = 420 + k * 216
        line(c, x, 180, 140 + (x - 420) * 1640 / 1080, 980, 2, (0.18, 0.20, 0.24))
    for (x, y, lab) in ((560, 820, "PEÇAS"), (760, 860, None), (1180, 860, "FRÁGIL"), (1380, 820, None)):
        put(c, x, y, lambda c, lab=lab: cargo_crate(c, 170, 120, lab), 1.0)
    for k in range(n_paint):
        x = 820 + k * 150
        put(c, x, 600, lambda c, k=k: abstract_painting(c, seed=k + 3, w=120, h=150, alpha=1.0), 1.0, paint_a)
    if glow_on > 0:
        glow(c, 970, 600, 320, AMBER, 0.25 * glow_on)


PAC = make_proj(125, 250, 14, 66)                       # Pacífico Norte inteiro
PACJ = make_proj(128, 168, 28, 56)                      # Japão, Curilas e Kamchatka
TOKYO = (140.4, 35.8)
LAX = (241.6, 33.9)
LAST = (142.4, 36.5)                                    # ~200 km a ENE de Tóquio (aproximado)
ROUTE = [TOKYO, (150, 41), (160, 45.5), (170, 48), (180, 49), (190, 48.5), (200, 47), (210, 44.5), (220, 41.5),
         (230, 38), LAX]
ROUTE_A = [TOKYO, (145, 38.6), (150, 41)]


def pacific(c, t, proj=PAC, labels=True, ocean=True):
    draw_pacific(c, proj)
    if labels:
        if proj is PAC:
            map_label(c, proj, 195, 30, "OCEANO PACÍFICO", 40, ICE, SERIF)
            map_label(c, proj, 133, 58, "UNIÃO SOVIÉTICA", 28, (0.66, 0.72, 0.82), SERIF)
            map_label(c, proj, 225, 62, "ALASCA", 28, (0.66, 0.72, 0.82), SERIF)
            map_label(c, proj, 245, 44, "EUA", 30, (0.66, 0.72, 0.82), SERIF)
        else:
            if ocean:
                map_label(c, proj, 162, 30, "OCEANO PACÍFICO", 38, ICE, SERIF)
            map_label(c, proj, 136, 50, "UNIÃO SOVIÉTICA", 30, (0.66, 0.72, 0.82), SERIF)
            map_label(c, proj, 133.5, 36.6, "JAPÃO", 30, (0.66, 0.72, 0.82), SERIF)


# ================================================================== BLOCO 1
def s01(c, t):  # 0 - 18.0  um cargueiro decola de Tóquio; 22 min depois, tudo normal; a última vez
    night(c, t, 700)
    ocean(c, t, 700)
    vt = tw("última", 12)
    k = clamp01(t / 18.0)
    x, y = 260 + k * 1500, 420 - k * 60
    plane(c, t, x, y, 0.42, a=fade_out(t, vt + 2.5, 2.5))
    show(c, t, 1.6, 1250, 120, lambda c: caption_box(c, "Tóquio  >  Los Angeles", 44), anim="up", t1=tw("Vinte", 5) - 0.2)
    show(c, t, tw("Vinte", 5), 1250, 120, lambda c: date_stamp(c, "22 MINUTOS DEPOIS", 48, RED), anim="stamp", t1=vt - 0.3)
    ct = tw("Estava", 9)
    if t > ct and t < vt + 2:
        put(c, x + 120, y - 180, lambda c: bubble(c, "tudo normal", size=40, tx=-60, ty=80), 1.0, fade_in(t, ct, 0.4))
    show(c, t, vt, 1250, 120, lambda c: hl(c, "a última vez que alguém os ouviu", 0, 0, 44), anim="up")
    fog(c, t, 760, 0.08)
    HIST(c, t, [(0, "stand"), (vt, "think")], [(0, "neutral"), (vt, "worried")], appear=0.6)


def s02(c, t):  # 18.0 - 26.6  nunca chegou; sem socorro, destroço, óleo, corpo
    night(c, t, 600, None)
    ocean(c, t, 600)
    show(c, t, 18.1, 1150, 110, lambda c: stitle(c, "O avião nunca chegou", 0, 0, 62, INK, AMBER), anim="up")
    items = [("SOS", "pedido de socorro", tw("socorro", 19)),
             ("dest", "destroços", tw("destroço", 21)),
             ("oleo", "mancha de óleo", tw("mancha", 22)),
             ("corpo", "nenhum corpo", tw("corpo", 24))]
    for i, (kind, lab, t0) in enumerate(items):
        x = 660 + i * 330

        def ic(c, kind=kind):
            if kind == "SOS":
                speech(c, 200, 110, -50, 100); text(c, "SOS", 0, 0, 56, SERIF, RED)
            elif kind == "dest":
                poly(c, [(-80, 20), (-20, -30), (60, -20), (90, 30), (0, 40)]); fs(c, (0.70, 0.72, 0.74), 5)
            elif kind == "oleo":
                ellipse(c, 0, 0, 100, 34); fs(c, (0.10, 0.10, 0.12), 4, (0.40, 0.36, 0.46))
            else:
                life_vest(c)
        show(c, t, t0 - 0.3, x, 430, group(ic, at(0, 150, T(lab, 34))))
        x_over(c, t, t0 + 0.4, x, 420, 90)
    HIST(c, t, [(0, "stand"), (19.8, "shrug")], [(0, "worried")], x=260)


def s03(c, t):  # 26.6 - 32.4  um Boeing de mais de 40 m sumiu sobre o Pacífico
    night(c, t, 520)
    ocean(c, t, 520)
    st = tw("sumiu", 28)
    sc_ = 0.75 - 0.6 * ease_io(clamp01((t - 26.6) / 5.0))
    plane(c, t, 1150, 330, sc_, a=fade_out(t, st + 0.3, 1.4))
    show(c, t, tw("quarenta", 27), 1150, 120, lambda c: caption_box(c, "mais de 40 metros", 44), anim="up")
    show(c, t, tw("Oceano", 29), 1150, 640, lambda c: stitle(c, "OCEANO PACÍFICO", 0, 0, 64, ICE, ICE), anim="fade", d=1.0)
    fog(c, t, 560, 0.09)
    HIST(c, t, [(0, "present")], [(0, "worried"), (st, "shocked")], x=260)


def s04(c, t):  # 32.4 - 42.5  no porão, dezenas de quadros; nenhum visto de novo
    nt = tw("Nenhum", 39)
    hold(c, t, glow_on=fade_in(t, tw("quadros", 35)), paint_a=fade_out(t, nt + 0.6, 1.4))
    show(c, t, tw("toneladas", 33), 960, 110, lambda c: caption_box(c, "toneladas de carga", 42), anim="up", t1=tw("quadros", 35) - 0.2)
    show(c, t, tw("quadros", 35), 960, 110, lambda c: hl(c, "dezenas de quadros de um pintor famoso", 0, 0, 42), anim="up", t1=nt - 0.2)
    show(c, t, nt, 960, 110, lambda c: stitle(c, "Nenhum foi visto de novo", 0, 0, 56, INK, AMBER), anim="up")
    HIST(c, t, [(0, "present"), (nt, "stand")], [(0, "think"), (nt, "sad")], x=260, s=0.85)


def s05(c, t):  # 42.5 - 50.6  o comandante já tinha sobrevivido a um desastre
    night(c, t, 800, None)
    st = tw("sobrevivido", 45)
    smoke(c, t, 1350, 760, 520, 0.18 * fade_in(t, st - 0.4, 1.2), 3)
    crew_fig(c, t, 1150, 960, 1.15, [(0, "stand"), (st, "hips")], [(0, "neutral"), (st, "sad")], appear=42.7, fid=31, mustache=True)
    show(c, t, 43.0, 1150, 120, lambda c: caption_box(c, "o homem no comando", 44), anim="up", t1=st - 0.3)
    show(c, t, st, 1150, 120, lambda c: hl(c, "sobreviveu a um dos piores desastres da aviação brasileira", 0, 0, 38), anim="up")
    fog(c, t, 980, 0.08)
    HIST(c, t, [(0, "point_r")], [(0, "neutral"), (st, "worried")], x=300)


def s06(c, t):  # 50.6 - 55.4  título
    night(c, t, 760, (1600, 170), 110)
    ocean(c, t, 760)
    plane(c, t, 1500 - (t - 50.6) * 30, 300, 0.22, a=0.6)
    show(c, t, 50.65, 960, 470, lambda c: (text(c, "O MISTÉRIO DO", 0, -100, 46, TYPE, AMBER),
                                          stitle(c, "VOO VARIG 967", 0, 10, 140, INK, AMBER)), anim="fade", d=1.2)
    show(c, t, 52.0, 960, 610, lambda c: line(c, -420, 0, 420, 0, 3, AMBER), anim="fade")
    show(c, t, 52.6, 960, 660, T("Pacífico Norte  ·  30 de janeiro de 1979", 34, ICE), anim="fade", d=1.0)
    fog(c, t, 860, 0.09)


def s07(c, t):  # 55.4 - 69.0  a Varig nos anos 70; rosa dos ventos; Europa, EUA, África, Japão
    night(c, t, 900, None)
    put(c, 1150, 520, lambda c: b707(c, t, rose=True), 1.15, fade_in(t, 55.6))
    show(c, t, 55.6, 1150, 110, lambda c: hl(c, "VARIG  ·  fim dos anos 70", 0, 0, 46), anim="up", t1=tw("Os", 62) - 0.2)
    show(c, t, tw("maior", 57), 1150, 900, T("a maior companhia aérea do Brasil", 40, INK), anim="fade", t1=tw("Os", 62) - 0.2)
    rt = tw("rosa", 62)
    if t > rt:
        glow(c, 1150 - 270 * 1.15, 520 - 110 * 1.15, 90, AMBER, 0.35 * fade_in(t, rt))
        show(c, t, rt, 1150, 110, lambda c: hl(c, "a rosa dos ventos na cauda", 0, 0, 44), anim="up")
    for i, (w, lab) in enumerate((("Europa", "EUROPA"), ("Estados", "ESTADOS UNIDOS"), ("África", "ÁFRICA"), ("Japão", "JAPÃO"))):
        tt = tw(w, 64)
        show(c, t, tt, 560 + i * 360, 880, lambda c, lab=lab: date_stamp(c, lab, 36, AMBER), anim="stamp")
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=240, s=0.85)


def s08(c, t):  # 69.0 - 80.0  frota de cargueiros: peças, máquinas, eletrônicos, obras de arte
    night(c, t, 700, None)
    ocean(c, t, 760)
    k = (t - 69.0) / 11.0
    plane(c, t, 500 + k * 1100, 300 - k * 40, 0.5)
    show(c, t, tw("cargueiros", 72), 1150, 110, lambda c: caption_box(c, "uma frota de cargueiros", 44), anim="up")
    items = (("peças", lambda c: sc(wrench, s=0.8)(c)), ("máquinas", lambda c: cargo_crate(c, 160, 110, "MÁQUINAS")),
             ("eletrônicos", lambda c: monitor(c, None, 200, 130)), ("obras", lambda c: abstract_painting(c, 5, 110, 140)))
    for i, (w, ic) in enumerate(items):
        tt = tw(w, 75)
        show(c, t, tt, 620 + i * 340, 600, ic)
    HIST(c, t, [(0, "stand"), (75.9, "present")], [(0, "neutral")], x=240, s=0.85)


def s09(c, t):  # 80.0 - 94.2  Boeing 707 PP-VLU; 1966 American Airlines; 1974 Varig
    night(c, t, 900, None)
    put(c, 1100, 480, lambda c: b707(c, t), 1.25, fade_in(t, 80.1))
    pt = tw("prefixo", 82)
    if t > pt:
        a = fade_in(t, pt, 0.5)
        put(c, 1100 - 150 * 1.25, 480 - 15 * 1.25, lambda c: (rrect(c, -70, -18, 140, 36, 6), fs(c, (0.86, 0.86, 0.84), 0), text(c, "PP-VLU", 0, 0, 30, TYPE, (0.16, 0.30, 0.58))), 1.0, a)
    show(c, t, 80.2, 1100, 110, lambda c: hl(c, "Boeing 707 cargueiro", 0, 0, 46), anim="up", t1=pt - 0.2)
    show(c, t, pt, 1100, 110, lambda c: hl(c, "prefixo PP-VLU", 0, 0, 50), anim="up")
    show(c, t, tw("fabricado", 85), 760, 830, lambda c: label_card(c, "fabricado em 1966", "American Airlines"), anim="up")
    show(c, t, tw("comprado", 90), 1440, 830, lambda c: label_card(c, "comprado em 1974", "Varig"), anim="up")
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=230, s=0.8)


def s10(c, t):  # 94.2 - 101.5  12 anos, 4 motores, porta de carga lateral
    night(c, t, 900, None)
    c.rectangle(0, 860, W, 220); rgb(c, (0.10, 0.11, 0.13)); c.fill()
    dt = tw("porta", 96)
    put(c, 1050, 750, lambda c: b707(c, t, door=prog(t, dt, 1.0), gear=True), 1.15)
    if t > dt + 0.8:
        k = clamp01((t - dt - 0.8) / 3.0)
        put(c, 1050 + 150 * 1.15 + 420 - k * 150, 815, lambda c: cargo_crate(c, 120, 90), 1.0)
    show(c, t, 94.3, 760, 120, lambda c: caption_box(c, "12 anos de uso", 40), anim="up")
    show(c, t, tw("quatro", 95), 1180, 120, lambda c: caption_box(c, "4 motores", 40), anim="up")
    show(c, t, dt, 1560, 120, lambda c: caption_box(c, "porta de carga", 40), anim="up")
    HIST(c, t, [(0, "point_r")], [(0, "neutral")], x=230, s=0.8)


def narita(c, t, lights=True):
    night(c, t, 760)
    c.rectangle(0, 780, W, 300); rgb(c, (0.08, 0.09, 0.11)); c.fill()
    c.set_dash([50, 34]); line(c, 0, 900, W, 900, 5, LYELLOW); c.set_dash([])
    if lights:
        for i in range(14):
            circle(c, 60 + i * 140, 800, 5, AMBER if i % 2 else ICE, 0)
    # torre de controle
    c.save(); c.translate(1660, 780)
    c.rectangle(-30, -300, 60, 300); fs(c, (0.22, 0.23, 0.26), 4)
    poly(c, [(-80, -300), (80, -300), (60, -370), (-60, -370)]); fs(c, (0.16, 0.30, 0.34), 4)
    glow(c, 0, -335, 90, ICE, 0.18)
    c.restore()


def s11(c, t):  # 101.5 - 113.5  30 de janeiro de 1979, terça; Narita, aeroporto novo
    narita(c, t)
    put(c, 900, 780, lambda c: b707(c, t, gear=True), 0.85, fade_in(t, 101.6))
    show(c, t, 101.6, 960, 110, lambda c: date_stamp(c, "30 DE JANEIRO DE 1979", 54, RED), anim="stamp")
    show(c, t, tw("terça", 104), 960, 200, T("terça-feira, à noite", 38, INK), anim="fade")
    show(c, t, tw("Aeroporto", 106), 960, 300, lambda c: hl(c, "Aeroporto de Narita · Tóquio", 0, 0, 44), anim="up")
    show(c, t, tw("novo", 110), 1450, 420, lambda c: caption_box(c, "inaugurado em 1978", 36), anim="up")
    HIST(c, t, [(0, "stand"), (106.2, "point_r")], [(0, "neutral")], x=240, s=0.85)


def s12(c, t):  # 113.5 - 121.3  o plano: Pacífico até Los Angeles, Lima, Rio
    pacific(c, t)
    p = ease_io(clamp01((t - tw("atravessar", 114)) / 2.6))
    map_path(c, PAC, ROUTE, p, AMBER, 5, dash=[14, 10])
    map_point(c, PAC, *TOKYO, t=t); map_label(c, PAC, *TOKYO, "Tóquio", 30, dx=-20, dy=48)
    if p > 0.98:
        map_point(c, PAC, *LAX, t=t); map_label(c, PAC, *LAX, "Los Angeles", 30, dx=-100, dy=44)
    show(c, t, tw("Lima", 117), 1240, 920, lambda c: caption_box(c, "depois: Lima (Peru)  >  Rio de Janeiro", 38), anim="up")
    show(c, t, 113.6, 960, 80, lambda c: hl(c, "O PLANO", 0, 0, 44), anim="up")


def s13(c, t):  # 121.3 - 140.5  sem passageiros, seis tripulantes
    night(c, t, 600, None)
    show(c, t, 121.4, 1100, 90, lambda c: caption_box(c, "sem passageiros  ·  6 tripulantes", 44), anim="up")
    crew = [("Comandante", "Gilberto Araújo da Silva", tw("comandante", 124.5), True),
            ("1º oficial", "Erni Peixoto Mylius", tw("primeiro", 127.5), False),
            ("2º oficial", "Antonio Brasileiro da Silva Neto", tw("Antonio", 131), False),
            ("2º oficial", "Evan Braga Saunders", tw("Evan", 133.5), False),
            ("Mecânico de voo", "José Severino Gusmão de Araújo", tw("José", 136.5), False),
            ("Mecânico de voo", "Nicola Exposito", tw("Nicola", 139), False)]
    xs = [440, 700, 960, 1220, 1480, 1740 - 40]
    for i, (role, name, t0, mus) in enumerate(crew):
        x = xs[i]
        crew_fig(c, t, x, 700, 0.62, appear=t0 - 0.5, fid=31 + i, mustache=mus)
        show(c, t, t0, x, 790 + (i % 2) * 120, lambda c, role=role, name=name:
             (text(c, role, 0, -22, 24, TYPE, AMBER), text(c, name, 0, 14, 26 if len(name) > 22 else 30, SERIF, INK)), anim="up")


def s14(c, t):  # 140.5 - 150.7  tripulação experiente; o nome mais conhecido: o comandante
    night(c, t, 800, None)
    ct = tw("comandante", 147)
    for i in range(6):
        x = 700 + i * 190
        hi = (i == 0 and t > ct)
        a = 1.0 if (t < ct or i == 0) else 0.35
        crew_fig(c, t, x, 900, 0.8 if not hi else 0.95, fid=31 + i, alpha=a, mustache=(i == 0))
    if t > ct:
        glow(c, 700, 700, 260, AMBER, 0.22 * fade_in(t, ct))
    show(c, t, 140.7, 1180, 120, lambda c: caption_box(c, "uma tripulação experiente", 42), anim="up", t1=tw("E", 146) - 0.2)
    show(c, t, ct - 0.3, 1180, 120, lambda c: hl(c, "o nome mais conhecido: o comandante", 0, 0, 44), anim="up")
    HIST(c, t, [(0, "stand"), (ct, "point_r")], [(0, "neutral")], x=240, s=0.85)


# ================================================================== BLOCO 2
def s15(c, t):  # 150.7 - 165.4  Gilberto: 55 anos, 23 mil horas; seis anos antes, perto de Paris
    night(c, t, 800, None)
    pt = tw("Paris", 161)
    crew_fig(c, t, 1150, 960, 1.2, [(0, "stand"), (152, "hips")], [(0, "neutral")], appear=150.8, fid=31, mustache=True,
             alpha=fade_out(t, pt - 0.6, 1.0))
    show(c, t, 150.8, 1150, 110, lambda c: hl(c, "GILBERTO ARAÚJO DA SILVA", 0, 0, 48), anim="up")
    show(c, t, tw("cinquenta", 152), 820, 300, lambda c: caption_box(c, "55 anos", 40), anim="up", t1=pt - 0.6)
    show(c, t, tw("vinte", 154), 1480, 300, lambda c: caption_box(c, "+ de 23 mil horas de voo", 40), anim="up", t1=pt - 0.6)
    if t > pt - 0.6:
        a = fade_in(t, pt - 0.6, 1.0)
        for k in range(7):
            put(c, 700 + k * 110 + (k > 3) * 420, 860, lambda c, k=k: townhouse(c, 100, 120 + (k % 3) * 30, lit=0.25, seed=k), 1.0, a)
        put(c, 1150, 860, lambda c: eiffel(c, 460, (0.26, 0.27, 0.32)), 1.0, a)
        show(c, t, pt - 0.2, 1150, 300, lambda c: date_stamp(c, "PARIS  ·  SEIS ANOS ANTES", 46, RED), anim="stamp")
    fog(c, t, 900, 0.08)
    HIST(c, t, [(0, "present")], [(0, "neutral"), (pt, "worried")], x=240, s=0.85)


def s16(c, t):  # 165.4 - 181.3  11 de julho de 1973, voo Varig 820 Rio > Orly, 134 a bordo, comandante Gilberto
    night(c, t, 900, None)
    k = clamp01((t - 165.4) / 15.9)
    plane(c, t, 520 + k * 900, 520 - k * 60, 0.75)
    show(c, t, 165.5, 1100, 110, lambda c: date_stamp(c, "11 DE JULHO DE 1973", 54, RED), anim="stamp")
    show(c, t, tw("oitocentos", 168), 1100, 210, lambda c: hl(c, "voo Varig 820  ·  Rio de Janeiro  >  Paris (Orly)", 0, 0, 38), anim="up")
    show(c, t, tw("cento", 175), 1100, 830, lambda c: caption_box(c, "134 pessoas a bordo", 44), anim="up")
    gt = tw("comandante", 178)
    if t > gt:
        crew_fig(c, t, 1660, 1000, 0.75, [(0, "hips")], [(0, "neutral")], appear=gt, fid=31, mustache=True)
        show(c, t, gt, 1600, 590, T("comandante: Gilberto", 30, AMBER), anim="fade")
    HIST(c, t, [(0, "stand")], [(0, "neutral")], x=240, s=0.85)


def s17(c, t):  # 181.3 - 196.2  incêndio no banheiro traseiro; cigarro; fumaça até a cabine
    night(c, t, 900, None)
    put(c, 1100, 520, lambda c: b707(c, t, rose=True), 1.25)
    ft = tw("incêndio", 182)
    if t > ft:
        a = fade_in(t, ft, 1.0)
        glow(c, 1100 - 230 * 1.25, 520, 120, ORANGE, 0.45 * a)
        spread = clamp01((t - ft) / 12.0)
        smoke(c, t, 1100 - 230 * 1.25, 480, 260, 0.22 * a, 1)
        for k in range(int(1 + spread * 6)):
            smoke(c, t, 1100 - 230 * 1.25 + k * 90 * 1.25, 470, 200, 0.16 * a, 5 + k)
    show(c, t, ft, 1100, 110, lambda c: caption_box(c, "incêndio num banheiro do fundo", 42), anim="up", t1=tw("investigação", 185) - 0.2)
    ct = tw("cigarro", 187)
    show(c, t, tw("investigação", 185), 1100, 110, lambda c: hl(c, "causa provável: um cigarro jogado no lixo", 0, 0, 40), anim="up",
         t1=tw("fumaça", 190) - 0.2)
    show(c, t, ct, 1100, 840, lambda c: (line(c, -70, 0, 50, 0, 18, (0.92, 0.90, 0.84)), line(c, 50, 0, 70, 0, 18, ORANGE),
                                         smoke(c, t, 70, -10, 80, 0.3, 4)), anim="pop", t1=tw("fumaça", 190) - 0.2)
    show(c, t, tw("fumaça", 190), 1100, 110, lambda c: hl(c, "a fumaça chegou até a cabine de comando", 0, 0, 40), anim="up")
    HIST(c, t, [(0, "point_r")], [(0, "worried")], x=230, s=0.8)


def s18(c, t):  # 196.2 - 211.2  pouso num campo de cebolas a 5 km de Orly; só 11 sobreviveram
    night(c, t, 700, None)
    put(c, 1560, 760, lambda c: eiffel(c, 200, (0.22, 0.23, 0.28)), 1.0, 0.7)
    onion_field(c, 760)
    lt = tw("pousou", 197)
    k = ease_out(clamp01((t - lt + 1.5) / 3.0))
    put(c, 300 + k * 700, 520 + k * 290, lambda c: b707(c, t, rose=True), 0.8, fade_in(t, 196.3))
    if t > lt + 1.5:
        smoke(c, t, 900, 700, 420, 0.18, 2)
    show(c, t, tw("cebolas", 198), 1000, 110, lambda c: caption_box(c, "um campo de cebolas, a ~5 km de Orly", 42), anim="up",
         t1=tw("Mas", 203.5) - 0.2)
    show(c, t, tw("Mas", 203.5), 1000, 110, lambda c: hl(c, "mas a fumaça já tinha feito o pior", 0, 0, 42), anim="up",
         t1=tw("Das", 206) - 0.2)
    if t > tw("Das", 206):
        show(c, t, tw("Das", 206), 1000, 110, lambda c: (text(c, "134 a bordo", -230, 0, 52, SERIF, INK), text(c, ">", 0, 0, 52, SERIF, AMBER),
                                                        text(c, "11 sobreviventes", 270, 0, 52, SERIF, AMBER)), anim="up")
    HIST(c, t, [(0, "stand")], [(0, "worried"), (206.5, "sad")], x=230, s=0.85)


def s19(c, t):  # 211.2 - 222.4  mortos: Filinto Müller, Agostinho dos Santos; sobreviventes: quase todos tripulantes
    c.rectangle(0, 0, W, H); rgb(c, (0.04, 0.05, 0.07)); c.fill()
    glow(c, 1150, 560, 520, LYELLOW, 0.08)
    for i, x in enumerate((900, 1150, 1400)):
        put(c, x, 760, lambda c: candle(c, t + i), 0.9, fade_in(t, 211.3 + i * 0.4))
    show(c, t, tw("senador", 212), 1150, 200, lambda c: hl(c, "senador Filinto Müller", 0, 0, 42), anim="up")
    show(c, t, tw("cantor", 213.5), 1150, 320, lambda c: hl(c, "cantor Agostinho dos Santos", 0, 0, 42), anim="up")
    st = tw("sobreviventes", 216)
    show(c, t, st, 1100, 960, lambda c: caption_box(c, "sobreviventes: 10 tripulantes e 1 passageiro", 38), anim="up")
    gt = tw("comandante", 219)
    if t > gt:
        crew_fig(c, t, 1700, 900, 0.7, [(0, "stand")], [(0, "sad")], appear=gt, fid=31, mustache=True)
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=240, s=0.85)


def medal(c, col=AMBER):
    poly(c, [(-30, -120), (-8, -40), (8, -40), (30, -120)]); fs(c, (0.20, 0.30, 0.58), 4)
    circle(c, 0, 0, 46, col, 5)
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5
        line(c, 0, 0, 30 * math.cos(a), 30 * math.sin(a), 4, (0.62, 0.45, 0.16))


def no_smoking(c):
    circle(c, 0, 0, 90, (0.86, 0.84, 0.78), 7, RED)
    line(c, -50, 10, 40, 10, 18, (0.30, 0.30, 0.32)); line(c, 40, 10, 54, 10, 18, ORANGE)
    line(c, -64, -64, 64, 64, 14, RED)


def s20(c, t):  # 222.4 - 239.0  herói na França e no Brasil; voltou a voar; proibição do cigarro
    night(c, t, 900, None)
    crew_fig(c, t, 900, 980, 1.05, [(0, "stand"), (223.5, "hips")], [(0, "happy")], fid=31, mustache=True)
    show(c, t, 222.6, 1200, 110, lambda c: stitle(c, "tratado como herói", 0, 0, 56, INK, AMBER), anim="up")
    show(c, t, tw("homenagens", 224), 1060, 760, lambda c: medal(c), anim="drop")
    show(c, t, tw("França", 224.5), 1300, 420, lambda c: caption_box(c, "homenagens na França e no Brasil", 36), anim="up", t1=tw("Depois", 233) - 0.2)
    show(c, t, tw("voltou", 231), 1300, 560, lambda c: caption_box(c, "meses depois, voltou a voar", 36), anim="up", t1=tw("Depois", 233) - 0.2)
    show(c, t, tw("Depois", 233), 1420, 560, lambda c: no_smoking(c), anim="stamp")
    show(c, t, tw("proibir", 234), 1460, 760, T("proibido fumar nos banheiros", 32, INK), anim="fade")
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=240, s=0.85)


def s21(c, t):  # 239.0 - 258.7  seis anos depois, no comando do 967; dois desastres: um sobreviveu, outro ninguém voltou
    night(c, t, 900, None)
    show(c, t, 239.1, 1150, 110, lambda c: hl(c, "seis anos depois: comandante do voo 967", 0, 0, 44), anim="up", t1=tw("coincidência", 244) - 0.2)
    show(c, t, tw("coincidência", 244), 1150, 110, lambda c: caption_box(c, "um dos raríssimos pilotos em dois desastres com mortes", 38), anim="up")
    ut = tw("Um", 253.5)
    ot = tw("outro", 255)
    if t < tw("dois", 251):
        crew_fig(c, t, 1150, 980, 1.1, [(0, "stand"), (244, "hips")], [(0, "neutral")], fid=31, mustache=True, alpha=fade_out(t, tw("dois", 251) - 0.6, 0.6))

    def card(c, yr, voo, txt, col):
        rrect(c, -280, -220, 560, 440, 16); fs(c, (0.09, 0.11, 0.15), 5, col)
        text(c, yr, 0, -160, 60, SERIF, col)
        text(c, voo, 0, -90, 36, TYPE, INK)
        text(c, txt, 0, 150, 36, SERIF, col)
    show(c, t, tw("dois", 251), 860, 560, lambda c: (card(c, "1973", "voo Varig 820", "ele sobreviveu" if t > ut else "", AMBER),
                                                    c.save(), c.translate(0, 20), c.scale(0.28, 0.28), b707(c, t, lights=False), c.restore()), anim="up")
    show(c, t, tw("dois", 251) + 0.4, 1460, 560, lambda c: (card(c, "1979", "voo Varig 967", "ninguém voltou" if t > ot else "", RED),
                                                           big_q(c, 120, RED)), anim="up")
    HIST(c, t, [(0, "think"), (ut, "present")], [(0, "think"), (ot, "sad")], x=240, s=0.85)


def s22(c, t):  # 258.7 - 265.1  o que chamava atenção era a carga
    hold(c, t, glow_on=fade_in(t, tw("carga", 263)))
    show(c, t, 258.8, 960, 110, lambda c: caption_box(c, "naquela noite em Tóquio...", 42), anim="up", t1=tw("Era", 262.5) - 0.2)
    show(c, t, tw("Era", 262.5), 960, 110, lambda c: stitle(c, "...era a carga", 0, 0, 64, INK, AMBER), anim="up")
    HIST(c, t, [(0, "stand"), (262.6, "point_r")], [(0, "think")], x=260, s=0.85)


def s23(c, t):  # 265.1 - 284.9  20 t de carga; quadros de Manabu Mabe; 153 ou 53; mais de 1 milhão de dólares
    night(c, t, 700, None)
    show(c, t, 265.2, 1150, 100, lambda c: caption_box(c, "cerca de 20 toneladas de carga", 42), anim="up", t1=tw("Manabu", 270) - 0.2)
    mt = tw("Manabu", 270)
    show(c, t, mt, 1150, 100, lambda c: hl(c, "quadros de MANABU MABE", 0, 0, 48), anim="up")
    for k in range(5):
        show(c, t, mt + 0.3 + k * 0.3, 620 + k * 270, 430, lambda c, k=k: abstract_painting(c, seed=10 + k, w=200, h=250), anim="up")
    rt = tw("registros", 273.5)
    show(c, t, rt, 820, 760, lambda c: label_card(c, "registros mais citados", "153 quadros", 420), anim="up")
    show(c, t, tw("Outras", 276), 1480, 760, lambda c: label_card(c, "outras fontes", "53 quadros", 420, GRAY), anim="up")
    show(c, t, tw("Juntos", 279.5), 1150, 930, lambda c: hl(c, "mais de US$ 1 milhão (da época)", 0, 0, 44), anim="up")
    HIST(c, t, [(0, "present")], [(0, "neutral"), (rt, "think")], x=230, s=0.8)


def s24(c, t):  # 284.9 - 297.7  Mabe: nasceu no Japão em 1924; chegou menino; café; gravatas
    night(c, t, 820, None)
    c.rectangle(0, 840, W, 240); rgb(c, (0.10, 0.12, 0.09)); c.fill()
    show(c, t, 285.0, 1150, 100, lambda c: hl(c, "MANABU MABE (1924-1997)", 0, 0, 48), anim="up")
    show(c, t, tw("Japão", 285.5), 760, 220, lambda c: caption_box(c, "nasceu no Japão", 36), anim="up", t1=tw("Pintou", 295) - 0.3)
    bt = tw("Brasil", 289)
    show(c, t, bt, 1460, 220, lambda c: caption_box(c, "chegou ao Brasil ainda menino", 36), anim="up", t1=tw("Pintou", 295) - 0.3)
    ft = tw("fazenda", 292)
    for k in range(6):
        put(c, 760 + k * 190, 860, lambda c, k=k: coffee_bush(c, k), 1.1, fade_in(t, ft + k * 0.12))
    if t > ft:
        show(c, t, ft, 1150, 340, lambda c: caption_box(c, "fazenda de café · interior de São Paulo", 36), anim="up", t1=tw("Pintou", 295) - 0.3)
    fam = t < tw("Pintou", 295)
    if fam:
        figure(c, t, 1180, 840, 0.55, [(0, "stand")], [(0, "neutral")], shirt=(0.62, 0.56, 0.44), hair="tuft", fid=50, appear=bt)
        figure(c, t, 1300, 840, 0.62, [(0, "stand")], [(0, "neutral")], shirt=(0.45, 0.40, 0.34), hat="fedora",
               hat_col=(0.50, 0.42, 0.30), hair=None, fid=51, appear=bt + 0.2)
        figure(c, t, 1080, 840, 0.38, [(0, "stand")], [(0, "happy")], shirt=(0.80, 0.70, 0.50), hair="tuft", fid=52, appear=bt + 0.4)
    else:
        pt = tw("Pintou", 295)
        for k in range(4):
            show(c, t, pt + k * 0.2, 820 + k * 210, 500, lambda c, k=k: necktie(c, ((0.70, 0.24, 0.20), (0.20, 0.34, 0.60), (0.80, 0.60, 0.20), (0.30, 0.52, 0.36))[k], k), anim="drop")
        show(c, t, pt, 1150, 220, lambda c: hl(c, "pintou gravatas para sobreviver", 0, 0, 42), anim="up")
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=230, s=0.8)


def s25(c, t):  # 297.7 - 310.2  1959: melhor pintor nacional da Bienal; "o ano de Manabu Mabe"
    night(c, t, 900, None)
    show(c, t, 297.8, 1150, 100, lambda c: date_stamp(c, "1959", 70, RED), anim="stamp")
    show(c, t, tw("premiado", 299), 1150, 230, lambda c: hl(c, "melhor pintor nacional · Bienal de São Paulo", 0, 0, 40), anim="up")
    put(c, 1150, 560, lambda c: abstract_painting(c, seed=21, w=320, h=240), 1.0, fade_in(t, 299.5))
    show(c, t, 299.8, 1450, 560, lambda c: medal(c), anim="drop")
    tt = tw("revista", 303.5)
    show(c, t, tt, 1150, 860, lambda c: newspaper(c, "O ANO DE", "MANABU MABE (1959)"), anim="up")
    HIST(c, t, [(0, "present")], [(0, "happy")], x=230, s=0.85)


def s26(c, t):  # 310.2 - 319.5  as obras voltavam para casa num avião brasileiro; nunca chegaram
    nt = tw("nunca", 316.5)
    hold(c, t, glow_on=1.0, n_paint=3, paint_a=fade_out(t, nt, 2.0))
    show(c, t, 310.3, 960, 110, lambda c: caption_box(c, "voltando para casa, no porão de um avião brasileiro", 38), anim="up", t1=nt - 0.3)
    show(c, t, nt - 0.3, 960, 110, lambda c: stitle(c, "Elas nunca chegaram", 0, 0, 60, INK, AMBER), anim="up")
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=260, s=0.85)


# ================================================================== BLOCO 3
def s27(c, t):  # 319.5 - 331.9  decolou às 20h23; subiu, virou para leste, mar escuro
    narita(c, t)
    dt = tw("decolou", 320)
    k = clamp01((t - dt) / 9.0)
    x = 500 + k * 1500
    y = 820 - max(0, k - 0.15) * 700
    ang = -0.22 if k > 0.15 else 0
    plane(c, t, x, y, 0.6, ang=ang, gear=k < 0.3)
    show(c, t, 319.6, 960, 110, lambda c: caption_box(c, "decolagem de Narita", 44), anim="up")
    show(c, t, tw("oito", 322), 700, 260, group(sc(clock, 0.0, s=0.8), at(0, 100, T("20h23", 44, AMBER))), anim="pop")
    show(c, t, tw("leste", 325.5), 1300, 260, lambda c: hl(c, "rumo leste, sobre o mar escuro", 0, 0, 40), anim="up")
    fog(c, t, 820, 0.07)


def s28(c, t):  # 331.9 - 345.8  20h45, 22 min depois: contato de rotina; tudo normal
    pacific(c, t, PACJ)
    p = ease_io(clamp01((t - 332.0) / 3.0))
    plane_on_path(c, PACJ, [TOKYO, LAST], p, 0.5)
    map_point(c, PACJ, *TOKYO, t=t); map_label(c, PACJ, *TOKYO, "Tóquio", 28, dx=-80, dy=30)
    show(c, t, 332.0, 1150, 110, lambda c: hl(c, "20h45  ·  22 minutos depois", 0, 0, 46), anim="up")
    rt = tw("contato", 334)
    if t > rt:
        x, y = PACJ(*LAST)
        ping(c, t, rt, x, y, *PACJ(*TOKYO))
        show(c, t, tw("Estava", 341), x + 230, y - 170, lambda c: bubble(c, "tudo normal", size=40, tx=-120, ty=80), anim="pop")
        show(c, t, tw("Nenhum", 342.5), x + 230, y + 120, T("nenhum problema a bordo", 32, INK), anim="fade")
    HIST(c, t, [(0, "stand")], [(0, "neutral")], x=240, s=0.8)


def s29(c, t):  # 345.8 - 365.2  sobre o oceano: pontos fixos e horários combinados; próximo contato às 21h23
    pacific(c, t, PAC)
    map_path(c, PAC, ROUTE, 1.0, (0.55, 0.62, 0.72), 3, dash=[10, 10])
    map_point(c, PAC, *TOKYO, t=t, pulse=False)
    pts = ROUTE[1:-1]
    ft = tw("pontos", 351)
    for i, (lon, lat) in enumerate(pts):
        if t > ft + i * 0.25:
            x, y = PAC(lon, lat)
            poly(c, [(x, y - 14), (x + 12, y + 8), (x - 12, y + 8)]); fs(c, AMBER, 3)
    show(c, t, tw("radares", 347), 1150, 110, lambda c: caption_box(c, "longe dos radares de terra", 42), anim="up", t1=ft - 0.2)
    show(c, t, ft, 1150, 110, lambda c: hl(c, "pontos fixos no mapa · horários combinados", 0, 0, 40), anim="up", t1=tw("próximo", 358) - 0.2)
    nt = tw("próximo", 358)
    show(c, t, nt, 1150, 110, lambda c: hl(c, "próximo contato: 21h23", 0, 0, 48), anim="up")
    show(c, t, nt + 0.4, 1150, 860, group(sc(clock, t, s=0.8), at(0, 110, T("21h23", 44, AMBER))), anim="pop")
    if t > ft:
        plane_on_path(c, PAC, ROUTE, 0.06 + 0.06 * clamp01((t - ft) / 12), 0.4)


def s30(c, t):  # 365.2 - 369.4  21h23: silêncio
    c.rectangle(0, 0, W, H); rgb(c, (0.03, 0.04, 0.06)); c.fill()
    put(c, 960, 520, lambda c: radio_tower(c, t, waves=False), 1.1)
    show(c, t, 365.3, 960, 170, lambda c: date_stamp(c, "21h23", 70, RED), anim="stamp")
    show(c, t, tw("silêncio", 366.5), 960, 840, lambda c: stitle(c, "silêncio", 0, 0, 90, INK, AMBER), anim="fade", d=1.0)
    line(c, 360, 960, 1560, 960, 3, (0.4, 1.0, 0.6))


def s31(c, t):  # 369.4 - 380.3  os controladores chamaram de novo e de novo; nada; 1 hora depois, o alarme
    c.rectangle(0, 0, W, H); rgb(c, (0.04, 0.06, 0.08)); c.fill()
    c.rectangle(0, 820, W, 260); rgb(c, (0.12, 0.12, 0.14)); c.fill()
    put(c, 1250, 640, lambda c: monitor(c, lambda c: (c.save(), c.scale(0.7, 0.7), radar(c, t, blip=False), c.restore()), 460, 300), 1.0)
    figure(c, t, 900, 1000, 0.95, [(0, "stand"), (369.6, "point_r")], [(0, "worried")], shirt=(0.80, 0.80, 0.76), hair="tuft", fid=60)
    put(c, 900, 1000 - 0.95 * 320, lambda c: headset_mic(c), 0.55)
    for i, w in enumerate(("chamaram", "Chamaram", "E")):
        tt = tw(w, 369.4 + i * 1.5)
        show(c, t, tt, 700 + i * 360, 230, lambda c, i=i: bubble(c, "Varig 967?", size=38, tx=-60, ty=90), anim="pop", t1=tw("Nada", 374) - 0.1)
    show(c, t, tw("Nada", 374), 1150, 420, lambda c: stitle(c, "Nada.", 0, 0, 72, INK, AMBER), anim="up", t1=tw("Depois", 375) - 0.1)
    show(c, t, tw("Depois", 375), 1150, 420, lambda c: hl(c, "cerca de 1 hora depois: o alarme", 0, 0, 44), anim="up")
    if t > tw("alarme", 377):
        glow(c, 1250, 640, 400, RED, 0.18 * (0.5 + 0.5 * math.sin(t * 8)))


def s32(c, t):  # 380.3 - 396.6  buscas à noite com aviões e navios do Japão; suspensa no escuro; recomeça de manhã
    night(c, t, 620, None)
    ocean(c, t, 620, 0.5)
    put(c, 1000, 640, lambda c: sonar_ship(c, t), 1.0)
    if t < tw("suspensa", 388):
        for k, (x0, y0) in enumerate(((1040, 560),)):
            a = math.sin(t * 0.8) * 0.4
            c.move_to(x0, y0); c.line_to(x0 + 700 * math.cos(a), y0 + 120 + 200 * math.sin(a)); c.line_to(x0 + 700 * math.cos(a - 0.12), y0 + 60 + 200 * math.sin(a - 0.12))
            c.close_path(); rgb(c, LYELLOW, 0.12); c.fill()
    plane(c, t, 400 + (t - 380) * 70, 240, 0.25, lights=True)
    show(c, t, 380.4, 1150, 110, lambda c: caption_box(c, "aviões e navios do Japão, ainda naquela noite", 40), anim="up", t1=tw("Mas", 385) - 0.2)
    show(c, t, tw("Mas", 385), 1150, 110, lambda c: caption_box(c, "noite · inverno · oceano aberto", 42), anim="up", t1=tw("suspensa", 388) - 0.2)
    show(c, t, tw("suspensa", 388), 1150, 110, lambda c: hl(c, "busca suspensa no escuro", 0, 0, 44), anim="up", t1=tw("manhã", 391) - 0.2)
    show(c, t, tw("manhã", 391), 1150, 110, lambda c: hl(c, "recomeça de manhã: + de 12 horas depois", 0, 0, 42), anim="up")
    fog(c, t, 700, 0.09)
    HIST(c, t, [(0, "stand")], [(0, "worried")], x=240, s=0.85)


def s33(c, t):  # 396.6 - 406.8  Japão e EUA varrem o Pacífico a leste de Tóquio; mais de 8 dias
    pacific(c, t, PACJ)
    x0, y0 = PACJ(142.5, 33.5); x1, y1 = PACJ(154, 40.5)
    a = fade_in(t, 397.0)
    c.rectangle(x0, y1, x1 - x0, y0 - y1); rgb(c, AMBER, 0.12 * a); c.fill_preserve(); rgb(c, AMBER, 0.6 * a); c.set_dash([12, 8]); c.set_line_width(3); c.stroke(); c.set_dash([])
    for k in range(4):
        ph = (t * 0.12 + k * 0.25) % 1.0
        xx = x0 + ph * (x1 - x0); yy = y1 + (k + 0.5) * (y0 - y1) / 4
        c.save(); c.translate(xx, yy); plane_top(c, (0.86, 0.86, 0.88), 0.5); c.restore()
    map_point(c, PACJ, *TOKYO, t=t); map_label(c, PACJ, *TOKYO, "Tóquio", 28, dx=-80, dy=30)
    show(c, t, 396.7, 1150, 110, lambda c: hl(c, "Japão e Estados Unidos", 0, 0, 46), anim="up")
    show(c, t, tw("oito", 403), 820, 990, lambda c: date_stamp(c, "+ DE 8 DIAS DE BUSCA", 46, RED), anim="stamp")


def s34(c, t):  # 406.8 - 421.2  e não encontraram nada
    night(c, t, 820, None)
    ocean(c, t, 820)
    show(c, t, 406.9, 1150, 110, lambda c: stitle(c, "E não encontraram nada", 0, 0, 62, INK, AMBER), anim="up")
    items = [("fuselagem", "fuselagem", lambda c: poly(c, [(-80, 20), (-20, -30), (60, -20), (90, 30), (0, 40)]) or fs(c, (0.70, 0.72, 0.74), 5)),
             ("caixa", "carga", lambda c: cargo_crate(c, 130, 90)),
             ("mancha", "combustível", lambda c: (ellipse(c, 0, 0, 90, 30), fs(c, (0.10, 0.10, 0.12), 4, (0.40, 0.36, 0.46)))),
             ("colete", "colete", lambda c: sc(life_vest, s=0.8)(c)),
             ("corpo", "nenhum corpo", lambda c: (circle(c, 0, -50, 24, None, 6), line(c, 0, -26, 0, 30, 6), line(c, 0, -10, -30, 20, 6), line(c, 0, -10, 30, 20, 6), line(c, 0, 30, -20, 70, 6), line(c, 0, 30, 20, 70, 6))),
             ("quadro", "nem um quadro", lambda c: abstract_painting(c, 30, 100, 120))]
    for i, (w, lab, ic) in enumerate(items):
        t0 = tw(w, 407)
        x = 560 + (i % 3) * 400
        y = 360 + (i // 3) * 300
        show(c, t, t0, x, y, group(ic, at(0, 110, T(lab, 30))))
        x_over(c, t, t0 + 0.35, x, y, 80)
    HIST(c, t, [(0, "stand"), (407.5, "shrug")], [(0, "worried")], x=200, s=0.8)


def s35(c, t):  # 421.2 - 438.9  quase sempre algo sobe à superfície; um cargueiro deixaria um rastro enorme; nenhum rastro
    night(c, t, 600, None)
    ocean(c, t, 600)
    pt = tw("Pedaços", 425)
    mt = tw("Mas", 433.5)
    a = fade_in(t, pt, 0.8) * fade_out(t, mt, 1.2)
    rnd = random.Random(4)
    for k in range(14):
        x = 600 + rnd.uniform(0, 1100); y = 660 + rnd.uniform(0, 300)
        kind = k % 3
        bob = math.sin(t * 1.5 + k) * 5
        if kind == 0:
            put(c, x, y + bob, lambda c: (rrect(c, -30, -10, 60, 20, 6), fs(c, (0.86, 0.84, 0.76), 3)), 1.0, a)
        elif kind == 1:
            put(c, x, y + bob, lambda c: (rrect(c, -40, -8, 80, 16, 3), fs(c, (0.50, 0.38, 0.24), 3)), 1.0, a)
        else:
            put(c, x, y + bob, lambda c: (ellipse(c, 0, 0, 26, 12), fs(c, (0.40, 0.56, 0.76), 3)), 1.0, a)
    show(c, t, 421.3, 1150, 110, lambda c: caption_box(c, "quando um avião cai no mar, algo sobe", 40), anim="up", t1=tw("cargueiro", 429) - 0.2)
    show(c, t, tw("cargueiro", 429), 1150, 110, lambda c: caption_box(c, "20 toneladas deixariam um rastro enorme", 40), anim="up", t1=mt - 0.2)
    show(c, t, mt, 1150, 110, lambda c: stitle(c, "nenhum rastro", 0, 0, 72, INK, AMBER), anim="up")
    fog(c, t, 700, 0.08)
    HIST(c, t, [(0, "present"), (mt, "shrug")], [(0, "think"), (mt, "worried")], x=240, s=0.85)


def s36(c, t):  # 438.9 - 451.8  as caixas-pretas resistem ao impacto; mas precisam ser encontradas
    c.rectangle(0, 0, W, H)
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 0.05, 0.10, 0.16); g.add_color_stop_rgb(1, 0.01, 0.02, 0.04)
    c.set_source(g); c.fill()
    put(c, 960, 1000, lambda c: seabed(c, t, 0), 1.0)
    k = ease_out(clamp01((t - 439.0) / 9.0))
    put(c, 1150, 260 + k * 520, lambda c: black_box(c), 0.8 * (1 - 0.3 * k), 1.0)
    show(c, t, 439.0, 1150, 110, lambda c: caption_box(c, "as caixas-pretas: feitas para resistir", 40), anim="up", t1=tw("Mas", 445) - 0.2)
    show(c, t, tw("Mas", 445), 1150, 110, lambda c: hl(c, "mas precisam ser encontradas", 0, 0, 44), anim="up", t1=tw("ninguém", 448.5) - 0.2)
    show(c, t, tw("ninguém", 448.5), 1150, 110, lambda c: stitle(c, "onde procurar?", 0, 0, 64, INK, AMBER), anim="up")
    HIST(c, t, [(0, "point_r"), (448.6, "think")], [(0, "neutral"), (448.6, "think")], x=240, s=0.85)


def s37(c, t):  # 451.8 - 463.9  a investigação não chegou a lugar nenhum; o relatório
    night(c, t, 900, None)
    put(c, 1150, 560, lambda c: folder(c, "RELATÓRIO", True), 1.3, fade_in(t, 452.0))
    show(c, t, 451.9, 1150, 110, lambda c: caption_box(c, "a investigação não chegou a lugar nenhum", 40), anim="up", t1=tw("relatório", 456) - 0.2)
    show(c, t, tw("relatório", 456), 1150, 870, lambda c: (rrect(c, -720, -80, 1440, 160, 12), fs(c, PARCH, 4),
                                                          text(c, "\"não foi possível encontrar nenhum indício que lançasse", 0, -26, 32, TYPE, DARKTXT),
                                                          text(c, "qualquer luz sobre as causas do desaparecimento\"", 0, 22, 32, TYPE, DARKTXT)), anim="up")
    HIST(c, t, [(0, "stand")], [(0, "think")], x=240, s=0.85)


def s38(c, t):  # 463.9 - 477.6  seis famílias esperaram; sem explicação; nascem as teorias
    c.rectangle(0, 0, W, H); rgb(c, (0.04, 0.05, 0.07)); c.fill()
    glow(c, 1150, 620, 560, LYELLOW, 0.08)
    for i in range(6):
        x = 700 + i * 190
        put(c, x, 820, lambda c, i=i: candle(c, t + i * 0.7), 0.8, fade_in(t, 464.2 + i * 0.3))
    show(c, t, 464.0, 1150, 110, lambda c: hl(c, "seis famílias", 0, 0, 48), anim="up", t1=tw("teorias", 475) - 0.3)
    show(c, t, tw("Sem", 468.5), 1150, 300, T("sem destroços  ·  sem corpos  ·  sem explicação", 36, INK), anim="fade", t1=tw("teorias", 475) - 0.3)
    tt = tw("teorias", 475)
    show(c, t, tt - 0.3, 1150, 110, lambda c: stitle(c, "as teorias", 0, 0, 72, INK, AMBER), anim="up")
    show(c, t, tt, 1150, 420, lambda c: big_q(c, 200, AMBER), anim="pop")
    HIST(c, t, [(0, "stand"), (tt, "think")], [(0, "sad"), (tt, "think")], x=240, s=0.85)


def s39(c, t):  # 477.6 - 497.4  teoria 1: o roubo; atraso por manutenção, alguém se escondendo a bordo
    hold(c, t, glow_on=0.6)
    show(c, t, 477.7, 960, 110, lambda c: tag_header(c, "1", "O ROUBO"), anim="up")
    pt = tw("perfeito", 486)
    show(c, t, tw("desaparece", 482), 960, 230, T("obras de arte somem sem deixar nada para trás", 34, INK), anim="fade", t1=tw("Jornais", 489) - 0.2)
    show(c, t, pt, 960, 300, lambda c: hl(c, "o plano perfeito?", 0, 0, 42), anim="up", t1=tw("Jornais", 489) - 0.2)
    jt = tw("Jornais", 489)
    show(c, t, jt, 1450, 360, lambda c: newspaper(c, "ATRASO?", "manutenção antes da decolagem"), anim="up")
    et = tw("esconder", 495)
    if t > tw("alguém", 494.5):
        figure(c, t, 975, 930, 0.6, [(0, "stand")], [(0, "neutral")], shirt=(0.14, 0.14, 0.16), hat="beanie",
               hat_col=(0.12, 0.12, 0.14), hair=None, fid=70, appear=tw("alguém", 494.5), alpha=0.75)
        show(c, t, et, 975, 620, lambda c: big_q(c, 80, AMBER), anim="pop")
    HIST(c, t, [(0, "present")], [(0, "think")], x=240, s=0.8)


def s40(c, t):  # 497.4 - 515.0  nenhum quadro apareceu: nenhum leilão, coleção, pista
    night(c, t, 900, None)
    show(c, t, 497.5, 1150, 110, lambda c: hl(c, "+ de 40 anos: nenhum quadro apareceu", 0, 0, 44), anim="up")
    items = (("leilão", "leilão", lambda c: gavel(c)), ("coleção", "coleção particular", lambda c: abstract_painting(c, 41, 140, 170)),
             ("pista", "pista", lambda c: magnifier(c)))
    for i, (w, lab, ic) in enumerate(items):
        t0 = tw(w, 503)
        x = 760 + i * 400
        show(c, t, t0, x, 480, group(ic, at(0, 175, T(lab, 32))))
        x_over(c, t, t0 + 0.35, x, 470, 85)
    show(c, t, tw("Quem", 507.5), 1150, 760, lambda c: caption_box(c, "quem rouba, cedo ou tarde, tenta vender", 40), anim="up", t1=tw("simplesmente", 511) - 0.2)
    show(c, t, tw("simplesmente", 511), 1150, 760, lambda c: stitle(c, "simplesmente sumiram", 0, 0, 60, INK, AMBER), anim="up")
    HIST(c, t, [(0, "stand"), (503.5, "shrug")], [(0, "think")], x=240, s=0.85)


# ================================================================== BLOCO 4
def ussr_zone(c, proj, a=1.0):
    """faixa vermelha ao longo da costa soviética (Curilas, Sakhalin, Kamchatka)"""
    for pts in ([(142.6, 54.0), (142.3, 50.0), (142.2, 46.2)],
                [(146.2, 43.9), (150.4, 46.1), (156.2, 50.6), (158.6, 52.9), (161.0, 55.2), (163.3, 57.8), (166, 60.3)]):
        xy = [proj(*p) for p in pts]
        c.move_to(*xy[0])
        for p in xy[1:]:
            c.line_to(*p)
        rgb(c, RED, 0.55 * a); c.set_line_width(22); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    c.set_line_cap(cairo.LINE_CAP_BUTT)


def s41(c, t):  # 515.0 - 534.2  teoria 2: o mapa; perto da URSS, Curilas, Kamchatka; Guerra Fria
    pacific(c, t, PACJ, ocean=False)
    show(c, t, 515.1, 1150, 100, lambda c: tag_header(c, "2", "A GUERRA FRIA"), anim="up")
    rt = tw("rota", 518)
    p = ease_io(clamp01((t - rt) / 3.0))
    map_path(c, PACJ, ROUTE, p * 0.35, AMBER, 5, dash=[14, 10])
    map_point(c, PACJ, *TOKYO, t=t, pulse=False)
    ut = tw("União", 522)
    if t > ut:
        ussr_zone(c, PACJ, fade_in(t, ut))
    show(c, t, tw("Curilas", 524), *[v + d for v, d in zip(PACJ(151, 46.2), (130, 20))], T("Ilhas Curilas", 30, LYELLOW), anim="fade")
    show(c, t, tw("Kamchatka", 525), *[v + d for v, d in zip(PACJ(161, 53.5), (150, 0))], T("Kamchatka", 30, LYELLOW), anim="fade")
    show(c, t, tw("Guerra", 527), 1250, 950, lambda c: hl(c, "Guerra Fria: espaço aéreo soviético", 0, 0, 42), anim="up")
    HIST(c, t, [(0, "point_r")], [(0, "think")], x=240, s=0.8)


def s42(c, t):  # 534.2 - 557.7  abril 1978: Korean Air Lines 902 atingido, pouso num lago congelado, 2 mortos; e o 967?
    night(c, t, 700, None)
    put(c, 1150, 860, lambda c: frozen_lake(c, 1500, 220), 1.0)
    for k in range(9):
        put(c, 300 + k * 200, 760, lambda c, k=k: pine(c, 160 + (k % 3) * 40, (0.14, 0.22, 0.20)), 1.0)
    show(c, t, 534.3, 1150, 100, lambda c: date_stamp(c, "ABRIL DE 1978", 52, RED), anim="stamp")
    show(c, t, tw("Korean", 538), 1150, 190, lambda c: hl(c, "um Boeing 707 da Korean Air Lines", 0, 0, 42), anim="up", t1=tw("Será", 544) - 0.2)
    at_ = tw("atingido", 542)
    lt = tw("lago", 545)
    if t < lt:
        k = clamp01((t - 536) / 9)
        plane(c, t, 500 + k * 700, 380 + k * 150, 0.5, rose=False, stripe=(0.20, 0.40, 0.70))
        if t > at_ - 1.5:
            kk = clamp01((t - at_ + 1.5) / 2.0)
            put(c, 200 + kk * 900, 300 + kk * 150, lambda c: fighter_jet(c), 0.5)
    else:
        plane(c, t, 1250, 830, 0.5, ang=0.04, rose=False, stripe=(0.20, 0.40, 0.70), lights=False)
    show(c, t, at_, 1550, 330, lambda c: caption_box(c, "atingido por um caça soviético", 34), anim="up", t1=tw("Será", 544) - 0.2)
    show(c, t, lt, 1550, 430, lambda c: caption_box(c, "pouso forçado num lago congelado", 34), anim="up", t1=tw("Será", 544) - 0.2)
    show(c, t, tw("Dois", 547), 1550, 530, lambda c: caption_box(c, "2 passageiros morreram", 34), anim="up", t1=tw("Será", 544) - 0.2)
    show(c, t, tw("Será", 544), 1150, 190, lambda c: hl(c, "e o voo 967? derrubado em segredo?", 0, 0, 44), anim="up")
    snow(c, t, 60, 30, 0.4)
    HIST(c, t, [(0, "stand"), (tw("Será", 544), "think")], [(0, "worried"), (tw("Será", 544), "think")], x=240, s=0.85)


def s43(c, t):  # 557.7 - 579.9  Oswaldo Profeta, livro "O Mistério do 707"; erro de navegação; nenhuma prova
    night(c, t, 900, None)
    ot = tw("Oswaldo", 562)
    figure(c, t, 1500, 980, 0.95, [(0, "stand"), (ot + 1.5, "present_l")], [(0, "neutral")], shirt=(0.62, 0.66, 0.70),
           coat=(0.28, 0.34, 0.44), hair=None, mustache=True, fid=80, appear=559.2)
    show(c, t, ot, 1500, 500, lambda c: label_card(c, "ex-copiloto da FAB", "Oswaldo Profeta"), anim="up")
    bt = tw("livro", 563)
    show(c, t, bt, 1000, 560, lambda c: (c.save(), c.scale(1.4, 1.4), book(c, "", (0.18, 0.28, 0.52)), c.restore(), text(c, "\"O Mistério do 707\"", 0, 150, 34, TYPE, AMBER)), anim="pop", t1=tw("Mas", 573) - 0.2)
    show(c, t, tw("erro", 568), 1100, 110, lambda c: caption_box(c, "um erro de navegação até o espaço soviético?", 40), anim="up", t1=tw("Mas", 573) - 0.2)
    mt = tw("Mas", 573)
    items = (("documento", "documento", lambda c: document(c, "?", RED)), ("radar", "radar", lambda c: sc(radar, t, False, s=0.6)(c)),
             ("prova", "prova", lambda c: magnifier(c)))
    for i, (w, lab, ic) in enumerate(items):
        t0 = tw(w, mt)
        x = 560 + i * 260
        show(c, t, t0, x, 560, group(ic, at(0, 130, T(lab, 30))))
        x_over(c, t, t0 + 0.3, x, 550, 75)
    show(c, t, mt, 1100, 110, lambda c: hl(c, "nenhuma prova", 0, 0, 48), anim="up")
    HIST(c, t, [(0, "stand"), (mt, "shrug")], [(0, "think")], x=240, s=0.8)


def s44(c, t):  # 579.9 - 610.6  1976: Belenko foge para o Japão no MiG-25; desmontado e devolvido em caixotes; teoria das peças
    night(c, t, 760, None)
    c.rectangle(0, 800, W, 280); rgb(c, (0.08, 0.09, 0.11)); c.fill()
    c.set_dash([50, 34]); line(c, 0, 900, W, 900, 5, LYELLOW); c.set_dash([])
    show(c, t, 580.0, 1150, 100, lambda c: hl(c, "a versão mais rocambolesca", 0, 0, 42), anim="up", t1=tw("setembro", 582) - 0.2)
    show(c, t, tw("setembro", 582), 1150, 100, lambda c: date_stamp(c, "SETEMBRO DE 1976", 50, RED), anim="stamp", t1=tw("Segundo", 600) - 0.2)
    bt = tw("Belenko", 586)
    show(c, t, bt, 1150, 200, lambda c: hl(c, "Viktor Belenko foge para o Japão", 0, 0, 40), anim="up", t1=tw("japoneses", 593) - 0.2)
    dt = tw("desmontaram", 594)
    if t < dt + 0.5:
        k = ease_out(clamp01((t - bt) / 4.0))
        put(c, 300 + k * 800, 380 + k * 420, lambda c: fighter_jet(c), 0.9)
        show(c, t, tw("MiG", 591), 1500, 560, lambda c: caption_box(c, "MiG-25: o caça mais secreto da época", 34), anim="up")
    else:
        for k in range(5):
            show(c, t, dt + 0.5 + k * 0.3, 760 + k * 200, 820, lambda c, k=k: cargo_crate(c, 170, 120, "MiG-25" if k == 2 else None), anim="drop")
    show(c, t, tw("japoneses", 593), 1150, 200, lambda c: caption_box(c, "desmontado peça por peça e devolvido em caixotes", 38), anim="up",
         t1=tw("Segundo", 600) - 0.2)
    st = tw("Segundo", 600)
    if t > st:
        put(c, 1150, 470, lambda c: b707(c, t, door=1.0), 0.75, fade_in(t, st))
        show(c, t, st, 1150, 100, lambda c: hl(c, "a teoria: peças escondidas na carga da Varig?", 0, 0, 40), anim="up")
        show(c, t, tw("derrubado", 606), 1150, 200, T("e o avião derrubado para recuperá-las", 34, AMBER), anim="fade")
    HIST(c, t, [(0, "stand"), (st, "think")], [(0, "neutral"), (st, "think")], x=240, s=0.85)


def s45(c, t):  # 610.6 - 622.5  boa história de espionagem, mas: 2 anos depois? nenhuma prova
    night(c, t, 900, None)
    show(c, t, 610.7, 1150, 110, lambda c: caption_box(c, "uma boa história de espionagem...", 42), anim="up")
    show(c, t, tw("dois", 615), 1150, 420, group(sc(hourglass, t, s=0.9), at(0, 150, T("mais de 2 anos depois?", 36, AMBER))), anim="pop")
    show(c, t, tw("cargueiro", 618), 1150, 690, T("logo num cargueiro comercial?", 36, INK), anim="fade")
    show(c, t, tw("nenhuma", 620), 1150, 860, lambda c: hl(c, "nenhuma prova", 0, 0, 48), anim="up")
    HIST(c, t, [(0, "think"), (612.8, "shrug")], [(0, "think")], x=260, s=0.9)


def s46(c, t):  # 622.5 - 632.3  a mais provável, a mais silenciosa: despressurização lenta
    night(c, t, 760)
    ocean(c, t, 760)
    plane(c, t, 900 + (t - 622.5) * 40, 360, 0.55)
    show(c, t, 622.6, 1150, 100, lambda c: tag_header(c, "3", "A MAIS SILENCIOSA"), anim="up")
    show(c, t, tw("Uma", 629), 1150, 640, lambda c: stitle(c, "despressurização lenta", 0, 0, 64, INK, AMBER), anim="up")
    HIST(c, t, [(0, "stand"), (629, "point_r")], [(0, "neutral")], x=240, s=0.85)


def cockpit(c, t, slump=0.0, mask=0.0, fuel=1.0):
    c.rectangle(0, 0, W, H); rgb(c, (0.03, 0.04, 0.06)); c.fill()
    poly(c, [(300, 120), (1620, 120), (1780, 520), (140, 520)]); fs(c, (0.05, 0.08, 0.14), 6)       # para-brisa
    line(c, 960, 120, 960, 520, 8)
    stars(c, t, 40, 500)
    c.rectangle(140, 560, 1640, 300); fs(c, (0.16, 0.17, 0.20), 6)                                  # painel
    for k in range(7):
        x = 300 + k * 220
        if k == 6:
            continue
        circle(c, x, 700, 56, (0.06, 0.08, 0.10), 5)
        a = -2.2 + (k * 0.7 + math.sin(t * 0.3 + k) * 0.05)
        line(c, x, 700, x + 40 * math.cos(a), 700 + 40 * math.sin(a), 4, (0.86, 0.86, 0.80))
    # combustível
    x = 1560
    rrect(c, x - 90, 760, 180, 60, 6); fs(c, (0.06, 0.08, 0.10), 4)
    c.rectangle(x - 82, 768, 164 * clamp01(fuel), 44); rgb(c, AMBER if fuel > 0.2 else RED); c.fill()
    text(c, "COMBUSTÍVEL", x, 600, 24, TYPE, INK)
    text(c, "PILOTO AUTOMÁTICO: LIGADO", 760, 600, 26, TYPE, (0.4, 1.0, 0.6))
    for sx in (560, 1360):
        pilot(c, t, sx, 1330, 1.25, [(0, "stand")], [(0, "neutral" if slump < 0.5 else "sad")], fid=90 + sx // 400,
              coat=(0.14, 0.17, 0.26), mustache=sx == 560)
    if slump > 0:
        c.rectangle(0, 0, W, H); rgb(c, (0.0, 0.0, 0.0), 0.45 * slump); c.fill()
    if mask > 0:
        for sx in (760, 1160):
            put(c, sx, 340, lambda c: oxygen_mask(c, t), 1.0, mask)


def s47(c, t):  # 632.3 - 652.0  o ar escapa aos poucos; confusão, sono; ninguém pede socorro; piloto automático até o combustível acabar
    ct = tw("confusa", 638)
    pt = tw("piloto", 646)
    slump = clamp01((t - ct) / 5.0)
    fuel = 1.0 - 0.95 * clamp01((t - pt) / 5.5)
    cockpit(c, t, slump=slump, fuel=fuel)
    show(c, t, 632.4, 960, 70, lambda c: caption_box(c, "o ar escapa aos poucos · sem explosão · sem barulho", 36), anim="up", t1=ct - 0.2)
    show(c, t, ct, 960, 70, lambda c: hl(c, "confusão · sono · inconsciência", 0, 0, 42), anim="up", t1=tw("Ninguém", 642) - 0.2)
    show(c, t, tw("Ninguém", 642), 960, 70, lambda c: hl(c, "ninguém pede socorro", 0, 0, 44), anim="up", t1=pt - 0.2)
    show(c, t, pt, 960, 70, lambda c: hl(c, "o piloto automático segue... até o combustível acabar", 0, 0, 38), anim="up")


def s48(c, t):  # 652.0 - 675.0  Helios 2005; o 967 pode ter voado horas, longe das buscas; fundo do Pacífico
    gt = tw("Se", 663)
    if t < gt:
        night(c, t, 900, None)
        put(c, 1150, 860, lambda c: mountains(c, 1700, 260, False, (0.16, 0.18, 0.22)), 1.0)
        k = (t - 652) / 11
        plane(c, t, 500 + k * 1000, 400 + k * 60, 0.5, rose=False, stripe=(0.30, 0.50, 0.70))
        show(c, t, 652.1, 1150, 100, lambda c: hl(c, "isso já aconteceu", 0, 0, 44), anim="up", t1=tw("dois", 653) - 0.2)
        show(c, t, tw("dois", 653), 1150, 100, lambda c: date_stamp(c, "GRÉCIA · 2005 · HELIOS AIRWAYS", 44, RED), anim="stamp")
        show(c, t, tw("quase", 657.5), 1150, 220, lambda c: caption_box(c, "quase 3 horas com a tripulação desacordada", 38), anim="up")
        HIST(c, t, [(0, "present")], [(0, "worried")], x=240, s=0.85)
    else:
        pacific(c, t, PAC)
        x0, y0 = PAC(140.5, 33.5); x1, y1 = PAC(152, 40.5)
        c.rectangle(x0, y1, x1 - x0, y0 - y1); rgb(c, AMBER, 0.12); c.fill_preserve(); rgb(c, AMBER, 0.6); c.set_dash([12, 8]); c.set_line_width(3); c.stroke(); c.set_dash([])
        map_label(c, PAC, 146, 31.5, "área das buscas", 26, AMBER)
        p = ease_io(clamp01((t - gt - 1.0) / 6.0))
        path = [TOKYO, LAST, (155, 41), (170, 44), (185, 45)]
        map_path(c, PAC, path, p, (0.86, 0.86, 0.88), 3, dash=[6, 8])
        plane_on_path(c, PAC, path, p, 0.45)
        show(c, t, gt, 1150, 100, lambda c: hl(c, "e se o 967 seguiu por horas, sozinho?", 0, 0, 42), anim="up", t1=tw("pode", 670) - 0.2)
        show(c, t, tw("pode", 670), 1150, 100, lambda c: hl(c, "no fundo do Pacífico, a milhares de metros", 0, 0, 40), anim="up")


def s49(c, t):  # 675.0 - 696.1  nem essa teoria explica tudo; nada numa praia; a única testemunha: o avião
    pt = tw("praia", 688)
    tt = tw("testemunha", 692)
    c.rectangle(0, 0, W, H)
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 0.04, 0.08, 0.13); g.add_color_stop_rgb(1, 0.01, 0.02, 0.04)
    c.set_source(g); c.fill()
    if t < tw("E", 690):
        night(c, t, 600, None)
        ocean(c, t, 600)
        c.move_to(0, 900); c.curve_to(600, 840, 1300, 860, W, 820); c.line_to(W, H); c.line_to(0, H); c.close_path()
        rgb(c, (0.42, 0.36, 0.26)); c.fill()
        show(c, t, 675.1, 1150, 100, lambda c: caption_box(c, "nem essa teoria explica tudo", 42), anim="up", t1=tw("Ela", 683) - 0.2)
        show(c, t, tw("Ela", 683), 1150, 100, lambda c: hl(c, "nada nunca apareceu em nenhuma praia", 0, 0, 42), anim="up")
        x_over(c, t, pt + 0.2, 1300, 880, 70)
        HIST(c, t, [(0, "stand"), (pt, "shrug")], [(0, "think")], x=240, s=0.85)
    else:
        put(c, 960, 1000, lambda c: seabed(c, t, 0), 1.0)
        plane(c, t, 1150, 820, 0.55, ang=0.12, lights=False, col=(0.40, 0.44, 0.48), stripe=(0.16, 0.22, 0.34), a=0.85)
        glow(c, 1150, 820, 300, ICE, 0.05)
        show(c, t, tt - 0.4, 1150, 140, lambda c: stitle(c, "a única testemunha: o próprio avião", 0, 0, 50, INK, AMBER), anim="up")
        HIST(c, t, [(0, "stand")], [(0, "sad")], x=240, s=0.85)


def s50(c, t):  # 696.1 - 716.7  hoje, 47 anos depois; seis homens, o Boeing e as obras sumiram na primeira hora
    night(c, t, 720, None)
    ocean(c, t, 720)
    show(c, t, 696.2, 1150, 100, lambda c: hl(c, "47 anos depois", 0, 0, 50), anim="up")
    show(c, t, tw("raros", 702), 1150, 200, T("um dos raros aviões comerciais sumidos sem vestígio", 34, INK), anim="fade")
    st = tw("Seis", 708)
    for i in range(6):
        crew_fig(c, t, 800 + i * 140, 660, 0.5, appear=st + i * 0.15, fid=31 + i, mustache=(i == 0), alpha=0.85)
    plane(c, t, 1150 + (t - 696) * 8, 330, 0.35, a=0.8 * fade_in(t, 696.5, 1.5))
    for k in range(3):
        show(c, t, tw("obras", 710) + k * 0.2, 840 + k * 220, 900, lambda c, k=k: abstract_painting(c, 60 + k, 150, 180), anim="up")
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=240, s=0.85)


def s51(c, t):  # 716.7 - 732.1  Mabe pintou até 1997; as telas no fundo do oceano, ou num lugar que ninguém imagina
    ft = tw("fundo", 723)
    if t < ft - 0.5:
        c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.05, 0.06)); c.fill()
        glow(c, 1150, 520, 500, LYELLOW, 0.10)
        put(c, 1150, 560, lambda c: abstract_painting(c, 77, 360, 440), 1.0, fade_in(t, 716.8))
        show(c, t, 716.8, 1150, 100, lambda c: hl(c, "Manabu Mabe pintou até 1997", 0, 0, 46), anim="up")
        HIST(c, t, [(0, "present")], [(0, "sad")], x=240, s=0.85)
    else:
        c.rectangle(0, 0, W, H)
        g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 0.04, 0.08, 0.13); g.add_color_stop_rgb(1, 0.01, 0.02, 0.04)
        c.set_source(g); c.fill()
        put(c, 960, 1000, lambda c: seabed(c, t, 0), 1.0)
        for k in range(3):
            put(c, 900 + k * 260, 760 + (k % 2) * 40, lambda c, k=k: (c.rotate(-0.2 + k * 0.2), abstract_painting(c, 80 + k, 150, 190)), 1.0,
                0.7 * fade_in(t, ft + k * 0.4, 1.2))
        show(c, t, tw("talvez", 725), 1150, 120, lambda c: hl(c, "ou num lugar que ninguém imagina", 0, 0, 42), anim="up")
        show(c, t, tw("estão", 727), 1150, 230, T("as telas que ele nunca mais viu", 36, AMBER), anim="fade")
        HIST(c, t, [(0, "stand")], [(0, "sad")], x=240, s=0.85)


def s52(c, t):  # 732.1 - 745.5  e você? falha silenciosa, roubo perfeito ou segredo da Guerra Fria?
    night(c, t, 700, None)
    show(c, t, 732.2, 1150, 100, lambda c: stitle(c, "E você?", 0, 0, 72, INK, AMBER), anim="up")
    opts = (("falha silenciosa?", tw("falha", 735), lambda c: (c.translate(0, 40), sc(oxygen_mask, t, s=0.8)(c))),
            ("roubo perfeito?", tw("roubo", 736), lambda c: abstract_painting(c, 90, 110, 140)),
            ("Guerra Fria?", tw("segredo", 738), lambda c: (c.scale(0.4, 0.4), fighter_jet(c))))
    for i, (s, tt, ic) in enumerate(opts):
        show(c, t, tt, 760 + i * 400, 520, lambda c, s=s, ic=ic, i=i: theory_card(c, str(i + 1), s, ic, w=340, h=400), anim="up")
    show(c, t, tw("Deixa", 740), 1150, 920, lambda c: (speech(c, 820, 130, -300, 110), text(c, "deixe sua teoria nos comentários", 0, 0, 42, HAND, INK)),
         anim="pop")
    HIST(c, t, [(0, "point_r"), (740.5, "present")], [(0, "think"), (740.5, "happy")], x=220, s=0.8)


def s53(c, t):  # 745.5 - fim  encerramento
    night(c, t, 760, (1640, 160), 100)
    ocean(c, t, 760)
    plane(c, t, 1500 + (t - 745.5) * 25, 300, 0.25, a=0.6 * fade_in(t, 745.7, 2.0))
    HIST(c, t, [(0, "stand"), (745.8, "present"), (748.5, "wave"), (750.5, "stand")], [(0, "neutral"), (747.0, "happy")], x=420, s=1.05)
    show(c, t, 745.6, 1100, 260, T("Eu sou o Historiador.", 44, AMBER), anim="fade")
    show(c, t, 747.0, 1100, 470, sc(subscribe_btn, t > 748.5, s=0.9))
    show(c, t, 747.4, 1430, 470, sc(bell, s=0.8), rot=math.sin(t * 18) * 0.2 * max(0, 1 - (t - 747.4)))
    show(c, t, 748.0, 1100, 720, lambda c: (text(c, "PONTO CEGO", 0, 0, 84, SERIF, INK), line(c, -300, 58, 300, 58, 3, AMBER)), anim="fade", d=1.2)
    fog(c, t, 980, 0.09)


SCENES = [
    (0.0, 18.0, s01), (18.0, 26.6, s02), (26.6, 32.4, s03), (32.4, 42.5, s04), (42.5, 50.6, s05), (50.6, 55.4, s06),
    (55.4, 69.0, s07), (69.0, 80.0, s08), (80.0, 94.2, s09), (94.2, 101.5, s10), (101.5, 113.5, s11), (113.5, 121.3, s12),
    (121.3, 140.5, s13), (140.5, 150.7, s14),
    (150.7, 165.4, s15), (165.4, 181.3, s16), (181.3, 196.2, s17), (196.2, 211.2, s18), (211.2, 222.4, s19),
    (222.4, 239.0, s20), (239.0, 258.7, s21), (258.7, 265.1, s22), (265.1, 284.9, s23), (284.9, 297.7, s24),
    (297.7, 310.2, s25), (310.2, 319.5, s26),
    (319.5, 331.9, s27), (331.9, 345.8, s28), (345.8, 365.2, s29), (365.2, 369.4, s30), (369.4, 380.3, s31),
    (380.3, 396.6, s32), (396.6, 406.8, s33), (406.8, 421.2, s34), (421.2, 438.9, s35), (438.9, 451.8, s36),
    (451.8, 463.9, s37), (463.9, 477.6, s38), (477.6, 497.4, s39), (497.4, 515.0, s40),
    (515.0, 534.2, s41), (534.2, 557.7, s42), (557.7, 579.9, s43), (579.9, 610.6, s44), (610.6, 622.5, s45),
    (622.5, 632.3, s46), (632.3, 652.0, s47), (652.0, 675.0, s48), (675.0, 696.1, s49), (696.1, 716.7, s50),
    (716.7, 732.1, s51), (732.1, 745.5, s52), (745.5, 999.0, s53),
]

# Sons: nada automático (sem whoosh em transição, sem som em cada ícone). Só toques sem chiado nos momentos-chave.
SFX_OFF = True
SFX = [(12.0, "tum"), (18.1, "boom"), (40.2, "heartbeat"), (50.7, "boom"), (101.6, "tum"), (165.5, "tum"), (206.9, "heartbeat"),
       (255.1, "boom"), (316.9, "tum"), (365.3, "boom"), (374.7, "heartbeat"), (406.9, "tum"), (433.9, "boom"), (534.3, "tum"),
       (629.5, "heartbeat"), (692.0, "bell"), (748.0, "boom")]
