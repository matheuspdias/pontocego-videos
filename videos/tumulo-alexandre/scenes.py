"""O Túmulo Perdido de Alexandre, o Grande — Ponto Cego.
Narração: Pedro Lima - Serious (HeyGen / ElevenLabs v4), 4 blocos com 1 s de silêncio entre eles (~778,3 s).
Tempos absolutos (já com os offsets dos blocos): transcricao.txt e palavras.json.
tw("palavra", depois_de) devolve o início da primeira palavra que começa com esse texto depois do tempo dado.
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
        _TW[key] = _tw(prefix, after)
    return _TW[key]


def _tw(prefix, after):
    p = _norm(prefix)
    for w in _WORDS:
        if w["t0"] >= after - 0.01 and _norm(w["w"]).startswith(p):
            return w["t0"]
    raise KeyError(f"palavra não encontrada: {prefix} depois de {after}")


# ------------------------------------------------------------------ mapas e lugares (lon, lat)
EMP = make_proj(17, 76, 20, 46, box=(120, 80, 1800, 1040))       # império: Grécia -> Índia
MED = make_proj(17, 47, 26, 42, box=(140, 90, 1780, 1030))       # Babilônia, Síria, Egito, Macedônia
EGY = make_proj(24.5, 33.5, 28.6, 32.0, box=(140, 90, 1780, 1030))  # Delta do Nilo, Mênfis, Alexandria, Siwa
WORLD = make_proj(9, 47, 24, 47, box=(140, 90, 1780, 1030))      # Veneza, Grécia, Egito

PELLA = (22.52, 40.76)
BABYLON = (44.42, 32.54)
ALEX = (29.92, 31.20)
MEMPHIS = (31.25, 29.85)
SIWA = (25.52, 29.20)
DAMASCUS = (36.30, 33.50)
GAZA = (34.45, 31.50)
PELUSIUM = (32.55, 31.04)
AMPHIPOLIS = (23.84, 40.82)
VENICE = (12.33, 45.44)
PERSEPOLIS = (52.89, 29.93)
INDUS = (71.5, 32.0)

CONQUEST = [PELLA, (26.4, 40.1), (27.3, 39.2), (30.5, 38.3), (36.2, 36.8), (35.2, 33.3), (34.4, 31.5), (32.5, 31.0),
            ALEX, MEMPHIS, (33.5, 31.6), (36.3, 34.2), (40.0, 35.8), (43.5, 36.4), BABYLON, (48.0, 31.5), PERSEPOLIS,
            (56.0, 31.5), (60.0, 34.5), (66.9, 36.7), (69.2, 34.5), INDUS]
CORTEGE = [BABYLON, (43.3, 33.4), (41.5, 34.4), (40.0, 35.3), (38.3, 35.6), (37.2, 34.6), DAMASCUS]
TO_MACEDONIA = [DAMASCUS, (36.2, 36.0), (34.0, 37.0), (30.5, 38.5), (27.3, 40.0), (25.0, 40.9), PELLA]
TO_EGYPT = [DAMASCUS, (35.4, 32.6), GAZA, (33.6, 31.1), PELUSIUM, (31.9, 30.6), MEMPHIS]
MEM_ALEX = [MEMPHIS, (31.1, 30.5), (30.7, 30.9), (30.2, 31.1), ALEX]
VENICE_ROUTE = [ALEX, (27.0, 33.0), (23.0, 35.5), (20.0, 37.5), (18.5, 40.0), (16.0, 42.2), (13.8, 44.2), VENICE]

# ------------------------------------------------------------------ figurinos
GENERAL = dict(shirt=(0.56, 0.20, 0.16), hat="helmet", hair=None)
PTOLOMEU = dict(shirt=(0.70, 0.52, 0.22), hat="helmet", hair=None, mustache=False)
PERDICAS = dict(shirt=(0.30, 0.34, 0.50), hat="helmet", hat_col=(0.60, 0.60, 0.64), hair=None)
ROMANO = dict(shirt=(0.52, 0.14, 0.30), hat="laurel", hair=None)
BISPO = dict(coat=(0.82, 0.80, 0.72), hat="mitre", hair=None, shirt=None)
EGIPCIO = dict(coat=(0.86, 0.84, 0.78), hat="hood", hat_col=(0.86, 0.84, 0.78), hair=None, shirt=None)
CLEOPATRA = dict(shirt=(0.80, 0.62, 0.24), hair="long")
ERUDITO = dict(coat=PARCH2, hat="hood", hat_col=PARCH2, hair=None, shirt=None)
SECXIX = dict(shirt=(0.30, 0.30, 0.34), coat=(0.14, 0.14, 0.17), hat="tophat", hair=None, mustache=True)
ARQUEOLOGA = dict(shirt=(0.62, 0.52, 0.34), hair="long", hat="fedora", hat_col=(0.70, 0.62, 0.46))
MERCADOR = dict(shirt=(0.42, 0.22, 0.30), hat="beanie", hat_col=(0.55, 0.18, 0.20), hair=None)
TRAB = dict(shirt=(0.62, 0.56, 0.44), hair=None, hat="beanie", hat_col=(0.80, 0.78, 0.70))


# ------------------------------------------------------------------ helpers
def HIST(c, t, poses, exprs, appear=None, x=300, y=1010, s=0.95, **kw):
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


def labeled(fn, label, dy=130, size=34, col=INK):
    return group(fn, at(0, dy, T(label, size, col)))


def x_over(c, t, t0, x, y, s=70):
    show(c, t, t0, x, y, lambda c: big_x(c, s, RED, 14), anim="stamp")


def night(c, t, horizon=760, moon_xy=(1620, 170)):
    stars(c, t, 80, horizon - 60)
    if moon_xy:
        c.save(); c.translate(*moon_xy); moon(c, 50); c.restore()
        glow(c, moon_xy[0], moon_xy[1], 220, LYELLOW, 0.10)


def ground(c, y=860, col=(0.30, 0.23, 0.15)):
    c.rectangle(0, y, W, H - y); rgb(c, col); c.fill()
    line(c, 0, y, W, y, 4, (0.55, 0.45, 0.30))


def theory_card(c, n, title_s, icon=None, crossed=0.0, dim=False, w=330, h=420, sub=None):
    rrect(c, -w / 2, -h / 2, w, h, 14); fs(c, (0.13, 0.11, 0.09), 5, PARCH2 if not dim else LGRAY)
    text(c, n, 0, -h / 2 + 44, 32, TYPE, AMBER)
    text(c, title_s, 0, -h / 2 + 96, 40, SERIF, INK if not dim else GRAY)
    if sub:
        text(c, sub, 0, h / 2 - 36, 26, TYPE, GRAY)
    if icon:
        c.save(); c.translate(0, 70); icon(c); c.restore()
    if crossed > 0:
        c.save(); c.scale(crossed, crossed); big_x(c, 120, RED, 14); c.restore()


def counter_text(c, t, t0, n, x, y, size=120, col=INK, d=1.4, prefix="", suffix=""):
    if t < t0:
        return
    v = int(round(n * ease_out(prog(t, t0, d))))
    text(c, f"{prefix}{v}{suffix}", x, y, size, SERIF, col)


def ziggurat(c, w=520, h=300, col=SANDSTONE):
    for k in range(4):
        ww = w * (1 - k * 0.22)
        c.rectangle(-ww / 2, -(k + 1) * h / 4, ww, h / 4); fs(c, (col[0] * (1 - k * 0.05), col[1] * (1 - k * 0.05), col[2]), 5)
    c.rectangle(-18, -h / 4, 36, h / 4); fs(c, (0.10, 0.08, 0.06), 3)


def church_arches(c, t):
    """interior escuro de igreja antiga: arcos e velas"""
    for k in range(5):
        x = 260 + k * 350
        c.move_to(x - 120, 900); c.line_to(x - 120, 380); c.curve_to(x - 120, 210, x + 120, 210, x + 120, 380); c.line_to(x + 120, 900)
        rgb(c, (0.55, 0.45, 0.32), 0.55); c.set_line_width(6); c.stroke()
    for x in (700, 1500):
        c.save(); c.translate(x, 860); candle(c, t); c.restore()
        glow(c, x, 800, 160, AMBER, 0.18)


def egypt_map(c, t, proj=EGY, labels=True):
    draw_med_map(c, proj, grid=1)
    if labels:
        map_label(c, proj, 28.0, 31.85, "MAR MEDITERRÂNEO", 30, (0.55, 0.62, 0.70))


def med_map(c, t, proj=MED, grid=5):
    draw_med_map(c, proj, grid=grid)


def cup(c, col=GOLD):
    c.move_to(-40, -80); c.curve_to(-40, -20, 40, -20, 40, -80); c.close_path(); fs(c, col, 5)
    line(c, 0, -30, 0, 0, 8, INK); line(c, 0, -30, 0, -2, 4, col)
    ellipse(c, 0, 0, 30, 8); fs(c, col, 4)


def bed(c, w=420):
    c.rectangle(-w / 2, -70, w, 40); fs(c, (0.40, 0.28, 0.18), 5)
    c.rectangle(-w / 2 - 10, -140, 26, 140); fs(c, (0.40, 0.28, 0.18), 5)
    c.rectangle(w / 2 - 16, -110, 26, 110); fs(c, (0.40, 0.28, 0.18), 5)
    rrect(c, -w / 2 + 20, -100, w - 40, 34, 12); fs(c, (0.76, 0.72, 0.62), 4)
    rrect(c, -w / 2 + 24, -118, 80, 26, 10); fs(c, (0.86, 0.84, 0.78), 4)


def coins_pile(c, n=7):
    for k in range(n):
        ellipse(c, (k % 3 - 1) * 34, -k * 9, 30, 10); fs(c, GOLD, 3)


def ring(c):
    c.new_sub_path(); c.arc(0, 0, 26, 0, 2 * math.pi); rgb(c, INK); c.set_line_width(14); c.stroke_preserve()
    rgb(c, GOLD); c.set_line_width(8); c.stroke()
    circle(c, 0, -28, 9, RED, 3)


def belt(c):
    rrect(c, -110, -16, 220, 32, 10); fs(c, (0.40, 0.26, 0.16), 4)
    rrect(c, -22, -24, 44, 48, 8); fs(c, GOLD, 4)


def cloak(c, col=(0.55, 0.14, 0.26)):
    poly(c, [(-60, -120), (60, -120), (100, 100), (-100, 100)]); fs(c, col, 5)
    line(c, -20, -110, -40, 90, 2, (0.35, 0.08, 0.16)); line(c, 20, -110, 40, 90, 2, (0.35, 0.08, 0.16))
    circle(c, 0, -112, 12, GOLD, 3)


def street_grid(c, t, w=1300, h=760, p=1.0):
    """mapa de ruas antigas (el Falaki): grade com as duas avenidas principais"""
    rrect(c, -w / 2, -h / 2, w, h, 10); fs(c, (0.80, 0.71, 0.52), 5)
    for k in range(-5, 6):
        x = k * w / 12
        line(c, x, -h / 2 + 20, x, -h / 2 + 20 + (h - 40) * p, 2, (0.55, 0.45, 0.30))
    for k in range(-3, 4):
        y = k * h / 8
        line(c, -w / 2 + 20, y, -w / 2 + 20 + (w - 40) * p, y, 2, (0.55, 0.45, 0.30))
    line(c, -w / 2 + 20, 0, -w / 2 + 20 + (w - 40) * p, 0, 8, (0.45, 0.30, 0.16))       # Via Canópica
    line(c, w / 12, -h / 2 + 20, w / 12, -h / 2 + 20 + (h - 40) * p, 8, (0.45, 0.30, 0.16))  # rua R5


def lantern_beam(c, x, y, r=380):
    glow(c, x, y, r, AMBER, 0.14)


# ================================================================== BLOCO 1
def s01(c, t):  # 0.0 - 11.8  por volta do ano 400, João Crisóstomo pergunta
    church_arches(c, t)
    show(c, t, 0.2, 1100, 120, lambda c: date_stamp(c, "POR VOLTA DO ANO 400", 46, AMBER), anim="stamp")
    fig(c, t, 1180, 900, 0.85, [(0, "stand"), (6.2, "present"), (8.9, "point_lu")], [(0, "neutral"), (8.9, "think")],
        fid=21, appear=3.8, **BISPO)
    c.save(); c.translate(1380, 900); lectern(c); c.restore()
    show(c, t, 4.6, 1180, 300, lambda c: hl(c, "JOÃO CRISÓSTOMO", 0, 0, 40), anim="up", t1=8.6)
    if t > 8.85:
        show(c, t, 8.9, 1100, 270, lambda c: (speech(c, 1100, 170, -200, 140),
                                              text(c, "Onde está o túmulo de Alexandre?", 0, 0, 52, SERIF, INK)), anim="pop")
    fog(c, t, 900, 0.05)
    HIST(c, t, [(0, "stand"), (8.9, "think")], [(0, "neutral"), (8.9, "think")], appear=0.6, x=280)


def s02(c, t):  # 11.8 - 27.4  ninguém soube; +500 anos famoso; reis, imperadores viram o rosto
    night(c, t, 760)
    dunes(c, t, 880)
    k = 0.4 + 0.6 * fade_in(t, 14.0, 2.0)
    faded(c, k, lambda c: (c.save(), c.translate(1150, 870), c.scale(0.95, 0.95), mausoleum(c), c.restore()))
    show(c, t, 12.0, 1150, 110, lambda c: stitle(c, "Ninguém soube responder.", 0, 0, 56, INK), anim="fade", t1=17.0)
    show(c, t, tw("quinhentos", 14) - 0.2, 1150, 110, lambda c: hl(c, "+ de 500 anos", 0, 0, 52), anim="up")
    show(c, t, tw("famosos", 17), 1150, 200, T("um dos lugares mais famosos do mundo", 36, AMBER), anim="fade")
    for i, (x, kw) in enumerate(((620, GENERAL), (760, ROMANO))):
        tt = 21.4 if i == 0 else 23.1
        fig(c, t, x + 0 * i, 880, 0.55, [(0, "stand"), (tt + 1.2, "point_r")], [(0, "neutral")], fid=30 + i, appear=tt, **kw)
    if t > 24.0:
        glow(c, 1150, 700, 200, ICE, 0.15 * fade_in(t, 24.0))
        show(c, t, 24.2, 1560, 520, lambda c: (c.scale(0.8, 0.8), royal_coffin(c, "glass")), anim="fade")
    fog(c, t, 900, 0.07)
    HIST(c, t, [(0, "stand"), (14.0, "present")], [(0, "worried"), (21.0, "neutral")], x=250)


def s03(c, t):  # 27.4 - 43.1  sumiu do mapa; 140 buscas; nenhuma achou o corpo
    night(c, t, 760, moon_xy=(1640, 160))
    dunes(c, t, 880)
    vanish = fade_out(t, tw("sumiu", 30), 1.6)
    faded(c, vanish * 0.95, lambda c: (c.save(), c.translate(1150, 870), c.scale(0.95, 0.95), mausoleum(c), c.restore()))
    show(c, t, 27.6, 1150, 110, T("entre um imperador e um bispo...", 40), anim="fade", t1=tw("sumiu", 30) - 0.3)
    if t > tw("sumiu", 30):
        show(c, t, tw("sumiu", 30), 1150, 600, lambda c: big_q(c, 200), anim="pop", t1=36.0)
        show(c, t, tw("sumiu", 30) + 0.3, 1150, 110, lambda c: stitle(c, "SUMIU DO MAPA", 0, 0, 74, RED, BLOOD), anim="stamp", t1=36.0)
    if t > 36.1:
        counter_text(c, t, 37.5, 140, 1150, 330, 150, AMBER, prefix="+")
        show(c, t, 38.3, 1150, 450, T("buscas oficiais registradas", 40), anim="fade")
        for i in range(7):
            x = 820 + i * 110
            show(c, t, 38.0 + i * 0.12, x, 830, sc(lambda c: (c.rotate(-0.5), mattock(c)), s=0.35), anim="drop")
        show(c, t, 40.8, 1150, 640, lambda c: stitle(c, "NENHUMA ACHOU O CORPO", 0, 0, 60, RED, BLOOD), anim="stamp")
    fog(c, t, 900, 0.08)
    HIST(c, t, [(0, "think"), (36.2, "present"), (40.8, "shrug")], [(0, "think"), (40.8, "worried")], x=260)


def s04(c, t):  # 43.1 - 47.5  título
    night(c, t, 760, moon_xy=(1600, 160))
    dunes(c, t, 860)
    for x, s in ((520, 0.9), (800, 0.6)):
        c.save(); c.translate(x, 880); c.scale(s, s); pyramid(c, 420, 260); c.restore()
    c.save(); c.translate(1720, 900); palm_oasis(c, t); c.restore()
    show(c, t, 43.3, 1100, 330, T("a história do", 44, INK), anim="fade")
    show(c, t, 43.9, 1100, 450, lambda c: stitle(c, "TÚMULO PERDIDO", 0, 0, 104, AMBER, AMBER), anim="up")
    show(c, t, 44.9, 1100, 570, lambda c: stitle(c, "de Alexandre, o Grande", 0, 0, 66, INK), anim="up")
    fog(c, t, 900, 0.09)


def s05(c, t):  # 47.5 - 58.4  voltar ao dia; Babilônia, junho de 323 a.C.
    night(c, t, 760, moon_xy=(1640, 150))
    ground(c, 880, (0.28, 0.21, 0.13))
    if t < 53.8:
        show(c, t, 47.8, 1100, 520, sc(hourglass, t, s=1.1), anim="pop")
        show(c, t, 49.6, 1100, 180, T("como um túmulo desse tamanho desaparece?", 40), anim="fade")
    else:
        show(c, t, 53.9, 1150, 880, sc(ziggurat, s=1.2), anim="up", d=0.8)
        show(c, t, 53.9, 1150, 160, lambda c: stitle(c, "BABILÔNIA", 0, 0, 84, INK, AMBER), anim="fade")
        show(c, t, 54.9, 1150, 270, lambda c: date_stamp(c, "JUNHO DE 323 a.C.", 48, AMBER), anim="stamp")
        c.save(); c.translate(1500, 880); palm_oasis(c, t); c.restore()
    fog(c, t, 900, 0.07)
    HIST(c, t, [(0, "stand"), (47.8, "point_r"), (53.9, "present")], [(0, "think"), (53.9, "neutral")], x=280)


def s06(c, t):  # 58.4 - 73.5  32 anos, maior império, Grécia -> Índia, nunca perdeu
    draw_med_map(c, EMP, grid=10)
    p = ease_io(prog(t, tw("saído", 60), 8.0))
    map_path(c, EMP, CONQUEST, p, AMBER, 6)
    for lon, lat, s, w in ((21.3, 37.6, "GRÉCIA", "Grécia"), (30.5, 27.5, "EGITO", "Egito"), (53.0, 32.5, "PÉRSIA", "Pérsia"),
                           (73.0, 26.0, "ÍNDIA", "Índia")):
        if t > tw(w, 60):
            show(c, t, tw(w, 60), *EMP(lon, lat), T(s, 36, INK), anim="pop")
    map_point(c, EMP, *PELLA, AMBER, 9, t)
    map_label(c, EMP, *PELLA, "Macedônia", 28, AMBER, dy=-32)
    map_point(c, EMP, *BABYLON, RED, 9, t)
    show(c, t, 58.5, 960, 120, lambda c: caption_box(c, "Alexandre: 32 anos", 46), anim="up", t1=64.2)
    show(c, t, 64.4, 960, 120, lambda c: caption_box(c, "o maior império que o mundo já tinha visto", 42), anim="up")
    show(c, t, 71.1, 960, 980, lambda c: hl(c, "NUNCA PERDEU UMA BATALHA", 0, 0, 50), anim="stamp")


def s07(c, t):  # 73.5 - 92.3  banquete, doente, 2 semanas, causas
    night(c, t, 700, moon_xy=None)
    if t < 80.1:
        show(c, t, 73.7, 1100, 640, sc(cup, s=1.4), anim="pop", t1=76.0)
        show(c, t, 74.4, 1100, 320, T("depois de um banquete...", 44), anim="fade", t1=76.0)
        if t > 76.0:
            show(c, t, 76.1, 1100, 860, sc(bed, s=1.2), anim="up")
            for i, (s, tt) in enumerate((("febre alta", 77.0), ("dores", tw("dores", 77)), ("fraqueza", tw("fraqueza", 78)))):
                show(c, t, tt, 820 + i * 280, 300 + (i % 2) * 70, T(s, 42, AMBER if i == 0 else INK), anim="pop")
    else:
        if t < 83.2:
            c.save(); c.translate(1150, 860); c.scale(1.2, 1.2); bed(c); c.restore()
            show(c, t, 80.2, 1150, 600, sc(calendar, "14", s=1.2), anim="pop")
        show(c, t, 80.2, 1150, 150, lambda c: hl(c, "cerca de 2 semanas", 0, 0, 50), anim="up", t1=83.1)
        show(c, t, 82.2, 1150, 330, lambda c: stitle(c, "MORTO", 0, 0, 96, RED, BLOOD), anim="stamp", t1=83.1)
        if t > 83.2:
            show(c, t, 83.3, 1150, 140, T("a causa até hoje é discutida", 40), anim="fade")
            for i, (s, w) in enumerate((("MALÁRIA", "Malária"), ("FEBRE TIFOIDE", "tifoide"), ("INFECÇÃO", "infecção"),
                                        ("VENENO?", "veneno"))):
                tt = tw(w, 85)
                show(c, t, tt, 620 + i * 330, 520, lambda c, s=s, i=i: theory_card(c, str(i + 1), "", w=300, h=300,
                                                                                    icon=lambda c, s=s: text(c, s, 0, -80, 38 if len(s) < 10 else 32, SERIF, RED if i == 3 else INK)),
                     anim="up")
            show(c, t, tw("como", 89), 1150, 820, T("alguns autores antigos falaram em veneno", 36, GRAY), anim="fade")
    fog(c, t, 900, 0.06)
    HIST(c, t, [(0, "stand"), (76.1, "think"), (83.3, "present")], [(0, "neutral"), (82.2, "sad"), (86.0, "think")], x=240)


def s08(c, t):  # 92.3 - 101.5  "a quem deixa o império?" "Ao mais forte."
    night(c, t, 760, moon_xy=None)
    ground(c, 900)
    for i, x in enumerate((900, 1120, 1340, 1560)):
        fig(c, t, x, 900, 0.62, [(0, "stand"), (tw("perguntaram", 92) + 0.1 * i, "point_l" if i % 2 else "think")],
            [(0, "worried"), (100.0, "shocked")], fid=40 + i, appear=92.6 + i * 0.25, **GENERAL)
    show(c, t, tw("perguntaram", 92), 1230, 260, lambda c: (speech(c, 760, 130, 120, 110),
                                                            text(c, "A quem fica o império?", 0, 0, 44, SERIF, INK)), anim="pop", t1=99.8)
    show(c, t, 98.5, 1230, 420, T("três palavras", 40, AMBER), anim="fade", t1=99.8)
    if t > 99.9:
        glow(c, 1230, 330, 420, AMBER, 0.15)
        show(c, t, 99.98, 1230, 330, lambda c: stitle(c, "“AO MAIS FORTE.”", 0, 0, 110, AMBER, AMBER), anim="stamp")
    fog(c, t, 920, 0.07)
    HIST(c, t, [(0, "stand"), (99.9, "head")], [(0, "neutral"), (99.9, "shocked")], x=260)


def s09(c, t):  # 101.5 - 111.6  guerra de 40 anos; prêmio = o corpo
    night(c, t, 760, moon_xy=None)
    ground(c, 900)
    if t < tw("Foi", 108.8):
        show(c, t, 101.6, 1150, 130, lambda c: hl(c, "uma guerra de 40 anos", 0, 0, 52), anim="up")
        for i, x in enumerate((850, 1050)):
            fig(c, t, x, 900, 0.6, [(0, "point_r")], [(0, "angry")], fid=50 + i, **GENERAL)
        for i, x in enumerate((1300, 1500)):
            fig(c, t, x, 900, 0.6, [(0, "point_l")], [(0, "angry")], fid=52 + i, **PERDICAS)
        show(c, t, tw("prêmio", 104), 1150, 300, T("o primeiro prêmio...", 40, AMBER), anim="fade")
        show(c, t, tw("cidade", 106), 900, 470, labeled(sc(temple, 260, 160, s=0.6), "uma cidade", 60, 32), anim="pop")
        x_over(c, t, tw("cidade", 106) + 0.4, 900, 430, 60)
        show(c, t, tw("exército", 107), 1400, 470, labeled(sc(sword, s=0.6), "um exército", 60, 32), anim="pop")
        x_over(c, t, tw("exército", 107) + 0.4, 1400, 430, 60)
    else:
        glow(c, 1150, 640, 420, AMBER, 0.22 * fade_in(t, 109.1))
        show(c, t, 109.1, 1150, 720, sc(royal_coffin, "gold", s=1.1), anim="pop")
        show(c, t, 109.6, 1150, 260, lambda c: stitle(c, "O CORPO DE ALEXANDRE", 0, 0, 78, AMBER, AMBER), anim="stamp")
    fog(c, t, 920, 0.07)
    HIST(c, t, [(0, "stand"), (109.1, "point_r")], [(0, "worried"), (109.1, "shocked")], x=260)


def s10(c, t):  # 111.6 - 121.5  quem enterra o rei é o herdeiro; símbolo de poder
    night(c, t, 760, moon_xy=None)
    show(c, t, 111.8, 1150, 130, T("na Antiguidade...", 42), anim="fade")
    show(c, t, tw("enterrava", 112), 760, 560, sc(royal_coffin, "gold", s=0.8), anim="pop")
    show(c, t, tw("enterrava", 112) + 0.3, 760, 680, T("quem enterrava o rei", 34), anim="fade")
    if t > tw("visto", 113):
        arrow_draw(c, t, tw("visto", 113), 960, 520, 1240, 520, 0.6, col=AMBER)
    show(c, t, tw("herdeiro", 114), 1480, 500, sc(laurel_crown, 70, s=1.0), anim="pop")
    show(c, t, tw("herdeiro", 114) + 0.2, 1480, 680, lambda c: hl(c, "era o herdeiro", 0, 0, 40), anim="up")
    show(c, t, tw("símbolo", 115), 1150, 260, lambda c: stitle(c, "um símbolo de poder", 0, 0, 62, AMBER, AMBER), anim="up")
    show(c, t, tw("Quem", 117.6), 1150, 880, lambda c: caption_box(c, "quem tivesse Alexandre, tinha um pedaço da autoridade dele", 34), anim="up")
    fog(c, t, 940, 0.06)
    HIST(c, t, [(0, "stand"), (114.5, "point_r")], [(0, "think")], x=260, s=0.85)


def s11(c, t):  # 121.5 - 133.8  embalsamadores, caixão de ouro batido; 2 anos construindo o carro
    night(c, t, 760, moon_xy=None)
    lantern_beam(c, 1150, 640)
    if t < 129.4:
        for i, x in enumerate((880, 1420)):
            fig(c, t, x, 900, 0.65, [(0, "hold" if i == 0 else "present")], [(0, "neutral")], fid=60 + i, appear=tw("embalsamadores", 121) + i * 0.3,
                **EGIPCIO)
        show(c, t, tw("embalsamadores", 121), 1150, 150, T("embalsamadores egípcios e caldeus", 40), anim="fade")
        show(c, t, tw("colocado", 126), 1150, 760, sc(royal_coffin, "gold", s=1.0), anim="up")
        show(c, t, tw("ouro", 127), 1150, 300, lambda c: hl(c, "caixão de ouro batido", 0, 0, 48), anim="up")
    else:
        show(c, t, 129.5, 1150, 150, lambda c: hl(c, "quase 2 anos", 0, 0, 52), anim="up")
        show(c, t, 130.2, 1150, 250, T("construindo o carro fúnebre", 40), anim="fade")
        p = ease_io(prog(t, 130.5, 3.0))
        c.save(); c.translate(1150, 900); c.scale(0.95, 0.95)
        c.rectangle(-260, -460 + 460 * (1 - p), 520, 470 * p); c.clip()
        funeral_cart(c, t, glow_on=False)
        c.restore()
        for i, x in enumerate((780, 1520)):
            fig(c, t, x, 900, 0.55, [(0, "hold"), (130.0 + i * 0.6, "arms_up"), (131.0 + i * 0.6, "hold")], [(0, "neutral")], fid=62 + i,
                shirt=(0.50, 0.42, 0.30), hair=None)
    fog(c, t, 920, 0.06)
    HIST(c, t, [(0, "stand"), (126.0, "point_r")], [(0, "neutral")], x=250, s=0.85)


def s12(c, t):  # 133.8 - 153.3  o carro segundo Diodoro; 64 mulas
    night(c, t, 740, moon_xy=(1700, 140))
    ground(c, 900)
    if t < 147.8:
        c.save(); c.translate(1120, 910); c.scale(1.15, 1.15); funeral_cart(c, t); c.restore()
        show(c, t, 134.0, 1120, 110, lambda c: hl(c, "segundo o historiador Diodoro", 0, 0, 40), anim="up")
        tags = (("colunas", tw("colunas", 137), 1560, 560, 1300, 620), ("pedras preciosas", tw("pedras", 140), 1560, 340, 1240, 440),
                ("sinos", tw("sinos", 142), 640, 520, 900, 560), ("vitórias aladas", tw("vitórias", 145), 620, 340, 860, 470))
        show(c, t, tw("templo", 136), 1120, 200, T("um templo dourado sobre rodas", 38, AMBER), anim="fade")
        for s, tt, x, y, ax, ay in tags:
            if t > tt:
                show(c, t, tt, x, y, T(s, 34, INK), anim="pop")
                arrow_draw(c, t, tt + 0.2, x + (-40 if x > 1000 else 40), y + 24, ax, ay, 0.4, col=AMBER, lw=4)
    else:
        for i in range(4):
            c.save(); c.translate(520 + i * 250, 900); c.scale(0.8, 0.8); mule(c, t + i * 0.4); c.restore()
        c.save(); c.translate(1560, 910); c.scale(0.7, 0.7); funeral_cart(c, t); c.restore()
        counter_text(c, t, 148.2, 64, 960, 260, 150, AMBER)
        show(c, t, 149.2, 960, 380, T("mulas", 46), anim="fade")
        show(c, t, tw("coroa", 150), 960, 470, T("cada uma com uma coroa de ouro", 38, AMBER), anim="fade")
    fog(c, t, 930, 0.07)


def s13(c, t):  # 153.3 - 170.5  destino Macedônia; Siwa / templo de Amon; não chegou a nenhum
    med_map(c, t, MED)
    map_point(c, MED, *BABYLON, RED, 10, t)
    map_label(c, MED, *BABYLON, "Babilônia", 30, INK, dy=34)
    if t > tw("Macedônia", 153):
        p = ease_io(prog(t, tw("Macedônia", 153), 2.0))
        map_path(c, MED, CORTEGE + TO_MACEDONIA[1:], p, AMBER, 5, dash=[14, 10])
        map_point(c, MED, *PELLA, AMBER, 10, t)
        show(c, t, tw("Macedônia", 153) + 0.3, *(lambda p: (p[0], p[1] - 40))(MED(*PELLA)), T("Macedônia", 34, AMBER), anim="pop")
    show(c, t, 153.5, 960, 1000, lambda c: caption_box(c, "o destino oficial: a Macedônia", 40), anim="up", t1=157.9)
    if t > tw("Siwa", 160):
        show(c, t, tw("Egito", 161), *MED(30.5, 27.4), T("EGITO", 34, INK), anim="pop")
        map_point(c, MED, *SIWA, LYELLOW, 10, t)
        show(c, t, tw("Siwa", 160), *(lambda p: (p[0] - 10, p[1] + 44))(MED(*SIWA)), T("oásis de Siwa", 32, LYELLOW), anim="pop")
        show(c, t, tw("Amon", 163), *(lambda p: (p[0] - 10, p[1] + 86))(MED(*SIWA)), T("templo de Amon", 28, INK), anim="fade")
    show(c, t, 158.0, 960, 1000, lambda c: caption_box(c, "há quem diga que ele pediu o Egito", 40), anim="up", t1=166.0)
    if t > 166.2:
        show(c, t, 166.3, 960, 540, lambda c: big_q(c, 220), anim="pop")
        show(c, t, 166.3, 960, 1000, lambda c: caption_box(c, "não chegou nem a um, nem ao outro", 42), anim="up")


# ================================================================== BLOCO 2 (começa em 170.509)
def s14(c, t):  # 170.5 - 181.4  321 a.C.; o carro atravessa a Síria; interceptado
    med_map(c, t, MED)
    show(c, t, 170.6, 960, 110, lambda c: date_stamp(c, "321 a.C.", 50, AMBER), anim="stamp")
    map_point(c, MED, *BABYLON, RED, 9, t)
    map_label(c, MED, *BABYLON, "Babilônia", 28, INK, dy=34)
    show(c, t, tw("Síria", 172), *MED(38.8, 34.8), T("SÍRIA", 34, INK), anim="pop")
    p = ease_io(prog(t, 173.0, 4.4))
    map_path(c, MED, CORTEGE, p, AMBER, 6)
    if t > 173.0:
        pts = [MED(*q) for q in CORTEGE]
        # posição do carro ao longo da rota
        seg = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
        d = sum(seg) * p
        x, y = pts[0]
        for i, L in enumerate(seg):
            if d <= L:
                f = d / L if L else 0
                x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f; y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f
                break
            d -= L
            x, y = pts[i + 1]
        c.save(); c.translate(x, y - 6); c.scale(0.22, 0.22); funeral_cart(c, t); c.restore()
    if t > tw("interceptado", 177):
        show(c, t, tw("interceptado", 177), *(lambda p: (p[0], p[1] + 70))(MED(*DAMASCUS)), lambda c: big_x(c, 46, RED, 12), anim="stamp")
        show(c, t, tw("interceptado", 177), 960, 1000, lambda c: caption_box(c, "interceptado no meio da estrada", 42), anim="up")


def s15(c, t):  # 181.4 - 188.3  Ptolomeu
    night(c, t, 760, moon_xy=None)
    ground(c, 900)
    fig(c, t, 1150, 900, 0.8, [(0, "stand"), (182.6, "hips")], [(0, "confident")], fid=70, appear=181.8, **PTOLOMEU)
    show(c, t, tw("Ptolomeu", 181), 1150, 200, lambda c: hl(c, "PTOLOMEU", 0, 0, 60), anim="up")
    show(c, t, tw("generais", 183), 1150, 290, T("general próximo de Alexandre", 38), anim="fade")
    show(c, t, tw("governo", 186), 1150, 345, T("governador do Egito", 38, AMBER), anim="fade")
    c.save(); c.translate(1600, 900); c.scale(0.6, 0.6); pyramid(c); c.restore()
    fog(c, t, 920, 0.07)
    HIST(c, t, [(0, "point_r")], [(0, "neutral")], x=280)


def s16(c, t):  # 188.3 - 197.8  não atacou, convenceu a escolta; rumo ao Egito
    if t < tw("corpo", 192):
        night(c, t, 760, moon_xy=None)
        ground(c, 900)
        c.save(); c.translate(1450, 910); c.scale(0.8, 0.8); funeral_cart(c, t); c.restore()
        fig(c, t, 800, 900, 0.75, [(0, "present")], [(0, "confident")], fid=70, **PTOLOMEU)
        fig(c, t, 1100, 900, 0.7, [(0, "stand"), (191.6, "thumb")], [(0, "worried"), (191.6, "happy")], fid=71, **GENERAL)
        show(c, t, tw("atacou", 189), 960, 140, T("Ptolomeu não atacou.", 44), anim="fade")
        show(c, t, tw("convenceu", 190), 960, 220, lambda c: hl(c, "convenceu a escolta", 0, 0, 48), anim="up")
    else:
        med_map(c, t, MED)
        map_path(c, MED, CORTEGE, 1.0, (0.55, 0.45, 0.30), 4)
        p = ease_io(prog(t, tw("corpo", 192), 4.5))
        map_path(c, MED, TO_EGYPT, p, AMBER, 7)
        map_point(c, MED, *MEMPHIS, AMBER, 10, t)
        show(c, t, tw("sul", 194), *MED(30.3, 27.3), T("EGITO", 40, AMBER), anim="pop")
        show(c, t, tw("Rumo", 195.5), 960, 1000, lambda c: caption_box(c, "rumo ao Egito", 44), anim="up")


def s17(c, t):  # 197.8 - 208.5  foi um sequestro; Perdicas entendeu
    night(c, t, 760, moon_xy=None)
    ground(c, 900)
    show(c, t, 198.0, 1150, 160, lambda c: stitle(c, "UM SEQUESTRO", 0, 0, 92, RED, BLOOD), anim="stamp")
    fig(c, t, 1150, 900, 0.8, [(0, "stand"), (tw("entendeu", 203), "hips")], [(0, "neutral"), (tw("entendeu", 203), "angry")],
        fid=72, appear=tw("regente", 202) - 0.4, **PERDICAS)
    show(c, t, tw("Perdicas", 203), 1150, 290, lambda c: hl(c, "PERDICAS, o regente", 0, 0, 48), anim="up")
    show(c, t, tw("significava", 205), 1150, 370, T("quem tem o corpo, tem o poder", 36, AMBER), anim="fade")
    fog(c, t, 920, 0.07)
    HIST(c, t, [(0, "point_r"), (203.0, "think")], [(0, "shocked"), (203.0, "worried")], x=280)


def s18(c, t):  # 208.5 - 229.2  Perdicas marcha; Nilo; 2 mil mortos; revolta; Perdicas morto
    night(c, t, 700, moon_xy=None)
    if t < tw("Nilo", 212):
        ground(c, 900)
        show(c, t, 208.8, 1150, 140, T("Perdicas marcha contra o Egito", 42), anim="fade")
        for i in range(6):
            x = 560 + i * 170 + (t - 208.6) * 30
            fig(c, t, x, 900, 0.5, [(0, "run")], [(0, "angry")], fid=80 + i, **(PERDICAS if i == 5 else GENERAL))
    elif t < tw("próprios", 222):
        river(c, t, 700, 260, (0.10, 0.18, 0.22))
        show(c, t, tw("Nilo", 212), 960, 120, lambda c: hl(c, "a travessia do Nilo", 0, 0, 48), anim="up")
        for i in range(3):
            c.save(); c.translate(560 + i * 420 + math.sin(t + i) * 30, 860); c.scale(0.7, 0.7); crocodile(c); c.restore()
        if t > tw("dois", 216):
            counter_text(c, t, tw("dois", 216), 2000, 960, 330, 120, RED, prefix="~")
            show(c, t, tw("soldados", 217), 960, 440, T("soldados mortos (segundo Diodoro)", 36), anim="fade")
        show(c, t, tw("correnteza", 219), 640, 600, T("correnteza", 34, ICE), anim="pop")
        show(c, t, tw("crocodilos", 220), 1300, 600, T("crocodilos", 34, (0.60, 0.80, 0.50)), anim="pop")
    else:
        ground(c, 900)
        fig(c, t, 1300, 900, 0.85, [(0, "stand"), (225.7, "shrug")], [(0, "worried"), (225.7, "shocked")], fid=72, **PERDICAS)
        for i, x in enumerate((840, 1020, 1580)):
            fig(c, t, x, 900, 0.7, [(0, "point_r" if x < 1300 else "point_l")], [(0, "angry")], fid=90 + i, appear=222.6 + i * 0.3, **GENERAL)
        show(c, t, 222.6, 1150, 140, T("os próprios oficiais se revoltaram", 40), anim="fade")
        if t > tw("morto", 225):
            show(c, t, tw("morto", 225), 1150, 260, lambda c: hl(c, "Perdicas é morto no acampamento", 0, 0, 44), anim="up")
            x_over(c, t, tw("morto", 225) + 0.5, 1300, 640, 90)
    fog(c, t, 920, 0.07)


def s19(c, t):  # 229.2 - 239.2  Ptolomeu fica com o corpo; dinastia de quase 300 anos; Cleópatra
    night(c, t, 760, moon_xy=None)
    ground(c, 900)
    fig(c, t, 760, 900, 0.85, [(0, "present")], [(0, "confident")], fid=70, **PTOLOMEU)
    show(c, t, 228.8, 1060, 760, sc(royal_coffin, "gold", s=0.6), anim="pop")
    show(c, t, 228.9, 1150, 140, lambda c: hl(c, "Ptolomeu ficou com o corpo", 0, 0, 46), anim="up")
    if t > tw("dinastia", 231):
        p = ease_out(prog(t, tw("dinastia", 231), 2.5))
        line(c, 600, 300, 600 + 1100 * p, 300, 5, AMBER)
        for k in range(9):
            if p > k / 8:
                c.save(); c.translate(600 + k * 1100 / 8, 300); laurel_crown(c, 24); c.restore()
        show(c, t, tw("trezentos", 233), 1150, 390, T("quase 300 anos de Ptolomeus", 38, AMBER), anim="fade")
    if t > tw("Cleópatra", 236):
        fig(c, t, 1520, 900, 0.8, [(0, "hips")], [(0, "confident")], fid=95, appear=tw("Cleópatra", 236) - 0.2, **CLEOPATRA)
        show(c, t, tw("Cleópatra", 236), 1520, 440, lambda c: hl(c, "CLEÓPATRA", 0, 0, 40), anim="up")
    fog(c, t, 920, 0.06)


def s20(c, t):  # 239.2 - 253.5  Mênfis, depois Alexandria
    egypt_map(c, t)
    map_point(c, EGY, *MEMPHIS, AMBER, 11, t)
    show(c, t, 240.0, *(lambda p: (p[0] + 120, p[1]))(EGY(*MEMPHIS)), T("Mênfis", 36, AMBER), anim="pop")
    show(c, t, tw("faraós", 241), *(lambda p: (p[0] + 150, p[1] + 50))(EGY(*MEMPHIS)), T("capital dos faraós", 28, INK), anim="fade")
    c.save(); c.translate(EGY(*MEMPHIS)[0] - 60, EGY(*MEMPHIS)[1] + 120); c.scale(0.35, 0.35); pyramid(c); c.restore()
    if t > tw("Anos", 243):
        show(c, t, tw("Anos", 243), 960, 1000, lambda c: caption_box(c, "anos depois, provavelmente com Ptolomeu II", 38), anim="up")
        p = ease_io(prog(t, tw("levado", 247), 3.0))
        map_path(c, EGY, MEM_ALEX, p, AMBER, 6)
    if t > tw("Alexandria", 251):
        map_point(c, EGY, *ALEX, AMBER, 12, t)
        show(c, t, tw("Alexandria", 251), *(lambda p: (p[0] - 20, p[1] - 60))(EGY(*ALEX)), lambda c: stitle(c, "ALEXANDRIA", 0, 0, 56, AMBER, AMBER), anim="stamp")


def s21(c, t):  # 253.5 - 272.1  o Soma no centro, perto do palácio; Soma/Sema; Ptolomeus ao redor
    night(c, t, 700, moon_xy=(1700, 140))
    c.save(); c.translate(960, 980); alexandria_skyline(c, t, 1800); c.restore()
    if t > tw("construíram", 257):
        show(c, t, tw("construíram", 257), 960, 860, sc(mausoleum, s=1.0), anim="up", d=0.8)
        show(c, t, tw("palácio", 260), 960, 140, T("no centro da cidade, perto do palácio real", 38), anim="fade", t1=262.2)
    if t > tw("Soma", 262):
        show(c, t, tw("Soma", 262), 620, 230, lambda c: (stitle(c, "SOMA", 0, 0, 72, AMBER, AMBER), text(c, "= corpo", 0, 70, 34, TYPE, INK)), anim="pop")
    if t > tw("Sema", 265):
        show(c, t, tw("Sema", 265), 1300, 230, lambda c: (stitle(c, "SEMA", 0, 0, 72, AMBER, AMBER), text(c, "= túmulo", 0, 70, 34, TYPE, INK)), anim="pop")
    if t > tw("Ptolomeus", 268):
        for i, x in enumerate((420, 560, 1360, 1500)):
            show(c, t, tw("enterrados", 269) + i * 0.25, x, 880, sc(lambda c: (c.rectangle(-40, -90, 80, 90), fs(c, MARBLE, 4),
                                                                                poly(c, [(-50, -90), (0, -130), (50, -90)]), fs(c, MARBLE, 4)), s=0.9),
                 anim="up")
        show(c, t, tw("enterrados", 269), 960, 1010, lambda c: caption_box(c, "os Ptolomeus enterrados ao redor dele", 36), anim="up")
    fog(c, t, 960, 0.06)


def s22(c, t):  # 272.1 - 289.5  Estrabão; ouro derretido; caixão de vidro
    night(c, t, 760, moon_xy=None)
    fig(c, t, 640, 900, 0.75, [(0, "present"), (279.4, "shrug")], [(0, "neutral")], fid=96, appear=272.9, **ERUDITO)
    show(c, t, 273.0, 640, 430, lambda c: hl(c, "ESTRABÃO", 0, 0, 40), anim="up", t1=289.0)
    show(c, t, tw("trezentos", 273), 640, 490, T("~300 anos depois", 30, AMBER), anim="fade", t1=289.0)
    if t < tw("derreter", 284):
        show(c, t, 273.5, 1250, 700, sc(royal_coffin, "gold", s=1.0), anim="pop")
        show(c, t, tw("caixão", 278.5), 1250, 220, T("o caixão de ouro já não estava lá", 40), anim="fade")
        x_over(c, t, tw("lá", 280.5) + 0.2, 1250, 640, 90)
    elif t < tw("corpo", 285.5):
        c.save(); c.translate(1250, 760); flames(c, t, 260, 200); c.restore()
        show(c, t, tw("derreter", 284), 1250, 220, lambda c: hl(c, "o ouro foi derretido", 0, 0, 46), anim="up")
        show(c, t, tw("dinheiro", 283), 1250, 320, T("(um dos últimos Ptolomeus, sem dinheiro)", 30, GRAY), anim="fade")
        show(c, t, tw("derreter", 284) + 0.3, 1250, 560, sc(coins_pile, s=1.2), anim="drop")
    else:
        glow(c, 1250, 640, 340, ICE, 0.14)
        show(c, t, tw("corpo", 285.5), 1250, 720, sc(royal_coffin, "glass", s=1.1), anim="fade", d=0.8)
        show(c, t, tw("vidro", 287), 1250, 220, lambda c: hl(c, "caixão de vidro ou de cristal", 0, 0, 44), anim="up")
    fog(c, t, 930, 0.06)


def s23(c, t):  # 289.5 - 295.3  quem entrava podia ver Alexandre
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.04, 0.03)); c.fill()
    lantern_beam(c, 1150, 620, 560)
    c.save(); c.translate(1150, 760); c.scale(1.5, 1.5); royal_coffin(c, "glass", t=t); c.restore()
    show(c, t, tw("séculos", 290), 1150, 200, T("durante séculos...", 42), anim="fade")
    show(c, t, tw("ver", 293), 1150, 300, lambda c: stitle(c, "dava para ver Alexandre", 0, 0, 60, AMBER, AMBER), anim="up")
    HIST(c, t, [(0, "stand"), (293.0, "point_r")], [(0, "worried"), (293.0, "shocked")], x=320)


def s24(c, t):  # 295.3 - 305.3  Júlio César 48 a.C.; Cleópatra tira ouro
    night(c, t, 760, moon_xy=None)
    c.save(); c.translate(1500, 900); c.scale(0.75, 0.75); mausoleum(c); c.restore()
    show(c, t, 295.5, 960, 120, T("e muita gente entrou", 42), anim="fade", t1=300.3)
    if t < 300.4:
        show(c, t, tw("quarenta", 297), 960, 200, lambda c: date_stamp(c, "48 a.C.", 46, AMBER), anim="stamp")
        fig(c, t, 900, 900, 0.85, [(0, "stand"), (299.0, "present")], [(0, "neutral")], fid=97, appear=tw("Júlio", 298) - 0.3, **ROMANO)
        show(c, t, tw("Júlio", 298), 900, 430, lambda c: hl(c, "JÚLIO CÉSAR", 0, 0, 44), anim="up")
    else:
        fig(c, t, 900, 900, 0.85, [(0, "hold"), (302.4, "present")], [(0, "confident")], fid=95, appear=300.5, **CLEOPATRA)
        show(c, t, 300.6, 900, 430, lambda c: hl(c, "CLEÓPATRA", 0, 0, 44), anim="up")
        show(c, t, tw("ouro", 302), 1150, 760, sc(coins_pile, s=1.0), anim="drop")
        show(c, t, tw("guerra", 304), 960, 200, T("para pagar a guerra contra Roma", 40, AMBER), anim="fade")
    fog(c, t, 930, 0.06)
    HIST(c, t, [(0, "stand")], [(0, "neutral")], x=260, s=0.85)


def s25(c, t):  # 305.3 - 324.3  Augusto abre, coroa, flores; o nariz
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.04, 0.03)); c.fill()
    lantern_beam(c, 1250, 620, 560)
    nose = t > tw("nariz", 322) - 0.1
    c.save(); c.translate(1250, 820); c.scale(1.3, 1.3); royal_coffin(c, "glass", t=t, nose_chip=nose); c.restore()
    fig(c, t, 640, 960, 0.9, [(0, "stand"), (tw("coroa", 312), "present"), (tw("flores", 315), "point_r"), (tw("tocar", 318), "present"),
                              (tw("nariz", 322), "head")],
        [(0, "confident"), (tw("nariz", 322), "shocked")], fid=98, appear=305.9, **ROMANO)
    show(c, t, tw("Otávio", 307), 640, 470, lambda c: hl(c, "OTÁVIO (AUGUSTO)", 0, 0, 40), anim="up", t1=316.0)
    show(c, t, tw("coroa", 312), 1150, 520, sc(laurel_crown, 50), anim="drop")
    if t > tw("flores", 315):
        for i in range(5):
            show(c, t, tw("flores", 315) + i * 0.15, 1240 + i * 70, 640 + (i % 2) * 20, sc(flower, s=0.9), anim="drop")
    show(c, t, tw("Cássio", 316), 1250, 200, lambda c: hl(c, "segundo Cássio Dio...", 0, 0, 44), anim="up")
    if nose:
        show(c, t, tw("nariz", 322), 1250, 320, lambda c: stitle(c, "quebrou um pedaço do nariz", 0, 0, 56, RED, BLOOD), anim="stamp")


def s26(c, t):  # 324.3 - 332.5  "vim ver um rei, não cadáveres"
    night(c, t, 760, moon_xy=None)
    ground(c, 900)
    fig(c, t, 760, 900, 0.95, [(0, "stand"), (tw("respondeu", 328), "finger_up")], [(0, "neutral"), (tw("respondeu", 328), "confident")],
        fid=98, **ROMANO)
    show(c, t, 324.5, 1250, 230, T("e os túmulos dos Ptolomeus?", 40), anim="fade", t1=327.6)
    if t > 327.7:
        show(c, t, 327.8, 1250, 400, lambda c: (speech(c, 880, 220, -380, 160),
                                                text(c, "Vim ver um rei.", 0, -40, 56, SERIF, INK),
                                                text(c, "Não cadáveres.", 0, 40, 56, SERIF, AMBER)), anim="pop")
    fog(c, t, 930, 0.06)
    HIST(c, t, [(0, "think")], [(0, "think")], x=1650, s=0.75)


def s27(c, t):  # 332.5 - 347.0  Calígula leva a couraça; 199: Septímio Severo fecha o túmulo
    night(c, t, 760, moon_xy=None)
    ground(c, 900)
    if t < tw("cento", 339):
        fig(c, t, 760, 900, 0.85, [(0, "stand"), (tw("levou", 335), "hold")], [(0, "grin")], fid=99, appear=333.0, **ROMANO)
        show(c, t, tw("Calígula", 334), 760, 430, lambda c: hl(c, "CALÍGULA", 0, 0, 44), anim="up")
        show(c, t, tw("couraça", 335), 1250, 600, sc(cuirass, s=1.5), anim="pop")
        show(c, t, tw("couraça", 335) + 0.3, 1250, 300, T("a couraça de Alexandre", 40, AMBER), anim="fade")
        show(c, t, tw("público", 338), 1250, 860, T("e a usava em público", 34), anim="fade")
    else:
        c.save(); c.translate(1250, 900); c.scale(0.9, 0.9); mausoleum(c); c.restore()
        show(c, t, tw("cento", 339), 960, 120, lambda c: date_stamp(c, "199 d.C.", 46, AMBER), anim="stamp")
        fig(c, t, 680, 900, 0.85, [(0, "stand"), (tw("fechá", 343), "point_r")], [(0, "confident")], fid=100, appear=341.4, **ROMANO)
        show(c, t, tw("Septímio", 341), 680, 430, lambda c: hl(c, "SEPTÍMIO SEVERO", 0, 0, 40), anim="up")
        if t > tw("fechá", 343):
            p = ease_out(prog(t, tw("fechá", 343), 1.2))
            c.save(); c.translate(1250, 900 - 90 * 0.9); c.scale(0.9, 0.9)
            c.rectangle(-46, -150 + 110 * (1 - p), 92, 110 * p); fs(c, (0.62, 0.58, 0.50), 4)
            c.restore()
            show(c, t, tw("ninguém", 344.5), 1250, 230, lambda c: hl(c, "FECHADO", 0, 0, 56, bg=RED, col=INK), anim="stamp")
    fog(c, t, 930, 0.06)


def s28(c, t):  # 347.0 - 355.9  Caracala 215: entra mesmo assim; manto, anéis, cinto
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.04, 0.03)); c.fill()
    lantern_beam(c, 1250, 640, 560)
    c.save(); c.translate(1250, 860); c.scale(1.3, 1.3); royal_coffin(c, "glass", t=t, nose_chip=True); c.restore()
    show(c, t, 347.2, 960, 120, lambda c: date_stamp(c, "215 d.C.", 46, AMBER), anim="stamp")
    fig(c, t, 600, 960, 0.9, [(0, "stand"), (tw("deixou", 350), "present")], [(0, "grin")], fid=101, appear=347.6, **ROMANO)
    show(c, t, tw("Caracala", 348), 600, 480, lambda c: hl(c, "CARACALA", 0, 0, 40), anim="up")
    show(c, t, tw("assim", 349), 1250, 230, T("entrou mesmo assim", 40, AMBER), anim="fade")
    for (tt, x, fn) in ((tw("manto", 352), 1080, sc(cloak, s=0.6)), (tw("anéis", 353), 1260, sc(ring, s=1.0)), (tw("cinto", 354), 1440, sc(belt, s=0.7))):
        show(c, t, tt, x, 610, fn, anim="drop")


def s29(c, t):  # 355.9 - 364.1  última visita registrada; desaparece das fontes
    night(c, t, 760, moon_xy=None)
    y = 520
    line(c, 260, y, 1660, y, 5, INK)
    marks = (("48 a.C.", "César"), ("30 a.C.", "Augusto"), ("~40 d.C.", "Calígula"), ("199", "Severo"), ("215", "Caracala"))
    for i, (d, n) in enumerate(marks):
        x = 360 + i * 300
        show(c, t, 355.9 + i * 0.3, x, y, lambda c, d=d, n=n: (circle(c, 0, 0, 14, AMBER, 4), text(c, d, 0, -60, 32, TYPE, AMBER),
                                                                text(c, n, 0, 60, 32, TYPE, INK)), anim="pop")
    show(c, t, 356.6, 960, 180, lambda c: stitle(c, "a última visita registrada", 0, 0, 60, INK, AMBER), anim="up")
    if t > tw("Depois", 358.9):
        p = ease_out(prog(t, tw("Depois", 358.9), 2.0))
        c.set_dash([10, 14]); line(c, 1560, y, 1560 + 200 * p, y, 4, GRAY); c.set_dash([])
        show(c, t, tw("desaparece", 360), 960, 800, lambda c: (scroll(c, 0, 420, 260), text(c, "?", 0, 0, 120, SERIF, RED)), anim="pop")
        show(c, t, tw("fontes", 362), 960, 980, lambda c: caption_box(c, "o túmulo desaparece das fontes", 40), anim="up")
    fog(c, t, 930, 0.06)


# ================================================================== BLOCO 3 (começa em 364.162)
def s30(c, t):  # 364.1 - 372.2  200 anos sem notícia; o que aconteceu com Alexandria
    night(c, t, 700, moon_xy=(1700, 140))
    c.save(); c.translate(960, 980); alexandria_skyline(c, t, 1800); c.restore()
    show(c, t, 364.3, 960, 360, sc(hourglass, t, s=0.9), anim="pop", t1=368.2)
    show(c, t, 364.4, 960, 140, T("os 200 anos seguintes: ninguém sabe ao certo", 40), anim="fade", t1=368.2)
    show(c, t, 368.5, 960, 160, lambda c: stitle(c, "o que aconteceu com Alexandria", 0, 0, 60, AMBER, AMBER), anim="up")
    fog(c, t, 960, 0.06)


def s31(c, t):  # 372.2 - 388.6  revoltas e guerras; 272: Aureliano x Zenóbia; bairro real devastado
    night(c, t, 700, moon_xy=None)
    c.save(); c.translate(960, 980); alexandria_skyline(c, t, 1800); c.restore()
    show(c, t, 372.4, 960, 120, T("revoltas e guerras", 42), anim="fade", t1=376.7)
    show(c, t, tw("duzentos", 376.5), 960, 120, lambda c: date_stamp(c, "~272 d.C.", 46, AMBER), anim="stamp")
    show(c, t, tw("Aureliano", 379), 620, 260, lambda c: hl(c, "imperador Aureliano", 0, 0, 38), anim="up")
    show(c, t, tw("Zenóbia", 380), 1300, 260, lambda c: hl(c, "rainha Zenóbia", 0, 0, 38), anim="up")
    if t > tw("devastado", 383):
        for i, x in enumerate((640, 900, 1160)):
            c.save(); c.translate(x, 880); flames(c, t + i, 220, 200 * fade_in(t, tw("devastado", 383) - 0.6 + i * 0.2)); c.restore()
        show(c, t, tw("devastado", 383), 960, 400, lambda c: stitle(c, "o bairro real devastado", 0, 0, 58, RED, BLOOD), anim="stamp")
    if t > tw("Justamente", 384):
        show(c, t, tw("túmulo", 386), 960, 500, T("onde ficava o túmulo", 40, AMBER), anim="fade")
    smoke(c, t, 900, 800, 420, 0.18 * fade_in(t, 383))
    fog(c, t, 960, 0.06)


def s32(c, t):  # 388.6 - 409.7  365: terremoto, tsunami; parte do bairro real hoje debaixo d'água
    night(c, t, 700, moon_xy=None)
    if t < tw("Com", 403):
        show(c, t, 388.8, 960, 120, lambda c: date_stamp(c, "21 DE JULHO DE 365", 46, AMBER), anim="stamp")
        show(c, t, tw("terremoto", 391.5), 960, 210, T("terremoto no Mediterrâneo  >  tsunami", 40), anim="fade")
        recede = ease_io(prog(t, tw("recuando", 396), 2.0))
        sea_y = 760 + 160 * recede
        c.save(); c.translate(960, 980); c.scale(0.9, 0.9); alexandria_skyline(c, t, 1800); c.restore()
        sea(c, t, sea_y, 0.2)
        if t > tw("navios", 397):
            for i, x in enumerate((520, 980, 1420)):
                c.save(); c.translate(x, 940); c.rotate(0.12 * (1 if i % 2 else -1)); c.scale(0.5, 0.5); ancient_ship(c); c.restore()
            show(c, t, tw("navios", 397), 960, 300, T("o mar recua; os navios encalham na lama", 36), anim="fade")
        if t > tw("onda", 399):
            p = ease_in = ease_io(prog(t, tw("onda", 399), 2.2))
            c.save(); c.translate(-400 + 1500 * p, 1080); c.scale(1.1, 1.1); tsunami_wave(c, t); c.restore()
    else:
        c.rectangle(0, 0, W, H)
        g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 0.04, 0.10, 0.14); g.add_color_stop_rgb(1, 0.02, 0.04, 0.06)
        c.set_source(g); c.fill()
        for i, (x, h, rot) in enumerate(((480, 260, 0.0), (700, 180, 1.4), (1300, 300, 0.0), (1520, 160, 1.5))):
            c.save(); c.translate(x, 960); c.rotate(rot); c.scale(0.7, h / 300); column(c); c.restore()
        c.save(); c.translate(1000, 980); c.scale(0.6, 0.6); sphinx(c, (0.45, 0.50, 0.48), head=True); c.restore()
        for k in range(14):
            yy = (900 - (t * 60 + k * 70) % 900)
            circle(c, 300 + k * 110, yy, 5, None, 2, (0.6, 0.8, 0.9))
        show(c, t, tw("Com", 403), 960, 140, lambda c: hl(c, "hoje: debaixo d'água", 0, 0, 50), anim="up")
        show(c, t, tw("porto", 407), 960, 240, T("no porto de Alexandria", 40, ICE), anim="fade")


def s33(c, t):  # 409.7 - 428.5  Império cristão; templos fechados; Teodósio (sem confirmação)
    night(c, t, 760, moon_xy=None)
    ground(c, 900)
    c.save(); c.translate(1150, 900); temple(c, 620, 380); c.restore()
    show(c, t, 409.9, 960, 120, T("uma terceira mudança, mais lenta", 42), anim="fade", t1=412.5)
    show(c, t, tw("cristão", 412.5), 960, 120, lambda c: hl(c, "o Império Romano se torna cristão", 0, 0, 44), anim="up")
    if t > tw("fechados", 415):
        k = fade_in(t, tw("saqueados", 416), 1.0)
        c.save(); c.translate(1150, 640); c.rotate(0.15)
        c.rectangle(-360, -20, 720, 40); rgb(c, (0.35, 0.22, 0.14), 0.9 * fade_in(t, tw("fechados", 415))); c.fill(); c.restore()
        if k > 0:
            c.save(); c.translate(1150, 880); flames(c, t, 260, 180 * k); c.restore()
        show(c, t, tw("fechados", 415), 1150, 230, T("templos fechados, saqueados, destruídos", 36, AMBER), anim="fade")
    if t > tw("Teodósio", 421):
        fig(c, t, 620, 900, 0.8, [(0, "point_r")], [(0, "angry")], fid=102, **ROMANO)
        show(c, t, tw("Teodósio", 421), 620, 520, lambda c: hl(c, "TEODÓSIO?", 0, 0, 40), anim="up")
        show(c, t, tw("confirmar", 426), 1150, 1000, lambda c: caption_box(c, "não há como confirmar", 40), anim="up")
    fog(c, t, 930, 0.06)


def s34(c, t):  # 428.5 - 442.1  e então, por volta de 400, a pergunta; ninguém sabe; fica mais estranha
    church_arches(c, t)
    fig(c, t, 1180, 900, 0.85, [(0, "present"), (tw("Onde", 433), "point_lu")], [(0, "neutral"), (tw("Onde", 433), "think")], fid=21, **BISPO)
    show(c, t, 428.7, 1100, 120, lambda c: date_stamp(c, "POR VOLTA DO ANO 400", 44, AMBER), anim="stamp", t1=437.9)
    show(c, t, tw("Onde", 433), 1100, 280, lambda c: (speech(c, 1080, 160, -200, 130),
                                                       text(c, "Onde está o túmulo de Alexandre?", 0, 0, 50, SERIF, INK)), anim="pop", t1=437.9)
    show(c, t, tw("Ninguém", 436), 1100, 460, lambda c: stitle(c, "Ninguém sabe.", 0, 0, 70, RED, BLOOD), anim="stamp", t1=437.9)
    if t > 438.0:
        show(c, t, 438.1, 1100, 250, T("a história não termina aí...", 44), anim="fade")
        show(c, t, tw("estranha", 439.5), 1100, 360, lambda c: stitle(c, "ela fica mais estranha", 0, 0, 62, AMBER, AMBER), anim="up")
    fog(c, t, 900, 0.05)
    HIST(c, t, [(0, "think"), (438.1, "point_r")], [(0, "think"), (438.1, "neutral")], x=280)


def s35(c, t):  # 442.1 - 462.6  santuário de Iskandar; Leão, o Africano (séc. XVI)
    night(c, t, 760, moon_xy=(1700, 150))
    ground(c, 900)
    c.save(); c.translate(1200, 900); mosque(c, 300, 230, minaret=False); c.restore()
    glow(c, 1200, 820, 200, AMBER, 0.2)
    show(c, t, 442.3, 960, 120, T("séculos depois, viajantes árabes e europeus...", 40), anim="fade", t1=454.3)
    for i, x in enumerate((700, 880)):
        fig(c, t, x, 900, 0.6, [(0, "stand"), (446.0, "point_r")], [(0, "neutral")], fid=103 + i, appear=443.0 + i * 0.4, **MERCADOR)
    show(c, t, tw("santuário", 444), 1200, 520, T("um pequeno santuário", 34, AMBER), anim="fade")
    show(c, t, tw("Iskandar", 447), 1200, 260, lambda c: hl(c, "ISKANDAR", 0, 0, 56), anim="up", t1=454.3)
    show(c, t, tw("árabe", 448.5), 1200, 350, T("o nome árabe de Alexandre", 34), anim="fade", t1=454.3)
    if t > tw("século", 454.3):
        show(c, t, tw("século", 454.3), 960, 120, lambda c: date_stamp(c, "SÉCULO XVI", 44, AMBER), anim="stamp")
        show(c, t, tw("Leão", 455), 1200, 350, lambda c: hl(c, "LEÃO, O AFRICANO", 0, 0, 36), anim="up")
        show(c, t, tw("capela", 458), 1580, 620, T("uma pequena 'capela'", 32, INK), anim="fade")
    fog(c, t, 930, 0.06)


def s36(c, t):  # 462.6 - 488.6  mesquita, sarcófago verde com hieróglifos; 1801 ingleses levam a Londres; Museu Britânico
    if t < tw("mil", 475.3):
        night(c, t, 760, moon_xy=None)
        ground(c, 900)
        show(c, t, 462.8, 960, 120, lambda c: date_stamp(c, "SÉCULO XVIII", 44, AMBER), anim="stamp")
        c.save(); c.translate(560, 900); c.scale(0.8, 0.8); mosque(c); c.restore()
        show(c, t, tw("sarcófago", 466), 1250, 860, sc(sarcophagus, s=1.2), anim="up")
        show(c, t, tw("verde", 466), 1250, 560, T("pedra verde-escura, coberta de hieróglifos", 34, (0.60, 0.80, 0.66)), anim="fade")
        show(c, t, tw("fonte", 471), 1250, 300, lambda c: hl(c, "a \"fonte de Alexandre\"", 0, 0, 44), anim="up")
    elif t < tw("Ele", 486):
        sea(c, t, 760, 0.15)
        night(c, t, 700, moon_xy=None)
        show(c, t, tw("mil", 475.3), 960, 120, lambda c: date_stamp(c, "1801", 52, AMBER), anim="stamp")
        show(c, t, tw("ingleses", 476), 960, 210, T("os ingleses levam o sarcófago para Londres", 38), anim="fade")
        x = 600 + (t - 476.0) * 60
        c.save(); c.translate(x, 770 + math.sin(t) * 6); c.scale(0.7, 0.7); brigantine(c, t, 0, None); c.restore()
        c.save(); c.translate(x + 10, 715); c.scale(0.25, 0.25); sarcophagus(c); c.restore()
        if t > tw("convencidos", 482):
            show(c, t, tw("convencidos", 482), 1250, 400, lambda c: hl(c, "\"o caixão de Alexandre!\"", 0, 0, 44), anim="up")
    else:
        night(c, t, 760, moon_xy=None)
        ground(c, 900)
        c.save(); c.translate(960, 900); temple(c, 820, 420); c.restore()
        show(c, t, tw("Ele", 486), 960, 120, lambda c: hl(c, "MUSEU BRITÂNICO, LONDRES", 0, 0, 46), anim="up")
        c.save(); c.translate(960, 890); c.scale(0.55, 0.55); sarcophagus(c); c.restore()
    fog(c, t, 930, 0.06)


def s37(c, t):  # 488.6 - 505.3  hieróglifos decifrados: Nectanebo II; nunca usado
    c.rectangle(0, 0, W, H); rgb(c, (0.06, 0.05, 0.04)); c.fill()
    lantern_beam(c, 1150, 620, 560)
    c.save(); c.translate(1150, 820); c.scale(1.9, 1.9); sarcophagus(c); c.restore()
    if t > tw("decifrados", 490):
        c.save(); c.translate(1150 + math.sin(t * 0.8) * 160, 640); magnifier(c); c.restore()
    show(c, t, 489.0, 1150, 140, T("os hieróglifos são decifrados", 42), anim="fade", t1=493.3)
    show(c, t, tw("decepção", 491), 1150, 230, lambda c: stitle(c, "a decepção", 0, 0, 60, RED, BLOOD), anim="stamp", t1=493.3)
    if t > tw("Nectanebo", 494):
        show(c, t, tw("Nectanebo", 494), 1150, 150, lambda c: hl(c, "NECTANEBO II", 0, 0, 62), anim="up")
        show(c, t, tw("último", 496), 1150, 250, T("o último faraó egípcio nativo", 38, AMBER), anim="fade")
        show(c, t, tw("fugiu", 498), 1150, 320, T("fugiu ~11 anos antes de Alexandre chegar", 34), anim="fade")
        show(c, t, tw("nunca", 503), 1150, 1000, lambda c: caption_box(c, "e nunca chegou a ser usado por ele", 40), anim="up")
    HIST(c, t, [(0, "stand"), (494.0, "point_r")], [(0, "think"), (491.0, "sad")], x=300)


def s38(c, t):  # 505.3 - 525.1  por que venerado? o corpo em Mênfis dentro dele? não há prova
    night(c, t, 760, moon_xy=None)
    ground(c, 900)
    c.save(); c.translate(1200, 900); c.scale(1.2, 1.2); sarcophagus(c, lid=0.4 * fade_in(t, tw("Será", 515), 1.4)); c.restore()
    show(c, t, tw("detalhe", 506), 1150, 120, T("um detalhe que intriga pesquisadores", 40), anim="fade", t1=510.3)
    show(c, t, tw("Por", 510), 1150, 120, lambda c: hl(c, "por que um sarcófago VAZIO era venerado?", 0, 0, 42), anim="up", t1=516.0)
    if t > tw("Será", 515):
        glow(c, 1200, 720, 300, AMBER, 0.14 * fade_in(t, tw("Será", 515)))
        show(c, t, tw("Será", 515), 1150, 120, lambda c: hl(c, "o corpo de Alexandre esteve nele, em Mênfis?", 0, 0, 40), anim="up")
        show(c, t, tw("Mênfis", 518), 1250, 380, sc(big_q, 160), anim="pop")
    if t > tw("prova", 520):
        show(c, t, tw("prova", 520), 1150, 220, lambda c: stitle(c, "NÃO HÁ PROVA", 0, 0, 64, RED, BLOOD), anim="stamp")
    fog(c, t, 930, 0.06)
    HIST(c, t, [(0, "think"), (515.0, "point_r"), (520.5, "shrug")], [(0, "think"), (520.5, "worried")], x=300)


def s39(c, t):  # 525.1 - 544.3  Mesquita do Profeta Daniel; 1850: corpo com diadema numa caixa de vidro
    if t < tw("porão", 535):
        night(c, t, 760, moon_xy=(1680, 150))
        ground(c, 900)
        c.save(); c.translate(1150, 900); mosque(c, 460, 320); c.restore()
        show(c, t, 525.3, 1150, 120, lambda c: hl(c, "MESQUITA DO PROFETA DANIEL", 0, 0, 46), anim="up")
        show(c, t, tw("centro", 525.3), 1150, 210, T("no centro de Alexandria", 36, AMBER), anim="fade")
        show(c, t, tw("mil", 531), 520, 340, lambda c: date_stamp(c, "1850", 48, AMBER), anim="stamp")
        fig(c, t, 560, 900, 0.75, [(0, "stand"), (tw("visto", 535), "point_r")], [(0, "neutral")], fid=104, appear=tw("funcionário", 532), **SECXIX)
        show(c, t, tw("russo", 534), 560, 440, T("funcionário do consulado russo", 30), anim="fade")
    else:
        c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.04, 0.03)); c.fill()
        # porão: arcos de tijolo
        for k in range(3):
            x = 520 + k * 440
            c.move_to(x - 180, 1080); c.line_to(x - 180, 420); c.curve_to(x - 180, 220, x + 180, 220, x + 180, 420); c.line_to(x + 180, 1080)
            rgb(c, (0.40, 0.28, 0.18), 0.7); c.set_line_width(10); c.stroke()
        lantern_beam(c, 1150, 700, 500)
        show(c, t, tw("porão", 535), 1150, 820, sc(royal_coffin, "glass", s=1.3), anim="fade", d=1.0)
        show(c, t, tw("diadema", 537), 1150, 160, lambda c: hl(c, "um corpo com diadema, numa caixa de vidro", 0, 0, 40), anim="up")
        show(c, t, tw("confirmar", 542), 1150, 990, lambda c: caption_box(c, "ninguém conseguiu confirmar", 42), anim="up")
        HIST(c, t, [(0, "stand"), (537.0, "head")], [(0, "shocked")], x=300)
    fog(c, t, 930, 0.06)


def s40(c, t):  # 544.3 - 566.3  1879: câmara abobadada fechada com tijolos; 1888: Schliemann, pedido negado
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.04, 0.03)); c.fill()
    if t < tw("mil", 556.9):
        show(c, t, 544.5, 960, 120, lambda c: date_stamp(c, "1879", 48, AMBER), anim="stamp")
        # passagem para a câmara
        c.move_to(1000, 900); c.line_to(1000, 560); c.curve_to(1000, 440, 1300, 440, 1300, 560); c.line_to(1300, 900); c.close_path()
        fs(c, (0.02, 0.02, 0.02), 6, (0.55, 0.40, 0.26))
        glow(c, 1150, 700, 160 * fade_in(t, 547.0), AMBER, 0.12)
        fig(c, t, 740, 900, 0.75, [(0, "hold"), (tw("passagem", 546), "arms_up")], [(0, "neutral"), (tw("passagem", 546), "shocked")],
            fid=105, prop=("r", lambda c, tt: (c.rotate(-0.6), mattock(c))), **TRAB)
        show(c, t, tw("câmara", 547), 1150, 330, T("uma câmara abobadada", 38, AMBER), anim="fade")
        if t > tw("fechada", 552):
            c.save(); c.translate(1150, 900); brick_wall(c, 300, 340, prog(t, tw("fechada", 552), 2.0)); c.restore()
            show(c, t, tw("orientado", 553), 960, 1000, lambda c: caption_box(c, "e ele foi orientado a não falar sobre aquilo", 38), anim="up")
    else:
        night(c, t, 760, moon_xy=None)
        ground(c, 900)
        c.save(); c.translate(1300, 900); mosque(c, 420, 300); c.restore()
        show(c, t, tw("mil", 556.9), 960, 120, lambda c: date_stamp(c, "1888", 48, AMBER), anim="stamp")
        fig(c, t, 640, 900, 0.85, [(0, "stand"), (tw("pediu", 560), "present"), (tw("negado", 563.5), "shrug")],
            [(0, "confident"), (tw("negado", 563.5), "sad")], fid=106, appear=557.5, **SECXIX)
        show(c, t, tw("Troia", 558), 640, 400, T("o homem que encontrou Troia", 30, AMBER), anim="fade")
        show(c, t, tw("Heinrich", 559), 640, 340, lambda c: hl(c, "HEINRICH SCHLIEMANN", 0, 0, 36), anim="up")
        show(c, t, tw("negado", 563.5), 1300, 300, lambda c: hl(c, "NEGADO", 0, 0, 70, bg=RED, col=INK), anim="stamp")
    fog(c, t, 930, 0.06)


# ================================================================== BLOCO 4 (começa em 566.357)
CARDS = (("1", "ALEXANDRIA", "debaixo da cidade"), ("2", "SIWA", "no deserto"), ("3", "VENEZA", "outro nome"), ("4", "GRÉCIA", "Anfípolis"))


def card_icon(i):
    if i == 0:
        return lambda c: (c.translate(0, 50), c.scale(0.28, 0.28), modern_city(c, 0, 900))
    if i == 1:
        return lambda c: (c.translate(-10, 70), c.scale(0.55, 0.55), palm_oasis(c, 0))
    if i == 2:
        return lambda c: (c.translate(0, 60), c.scale(0.38, 0.38), basilica(c))
    return lambda c: (c.translate(0, 60), c.scale(0.3, 0.3), tumulus(c))


def s41(c, t):  # 566.3 - 580.7  século XX: obsessão; +140 tentativas; algumas sérias, outras nem tanto
    night(c, t, 700, moon_xy=None)
    c.save(); c.translate(1060, 760); street_grid(c, t, 1100, 520, 1.0); c.restore()
    c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.25); c.fill()
    show(c, t, 566.5, 960, 120, lambda c: date_stamp(c, "SÉCULO XX", 46, AMBER), anim="stamp")
    show(c, t, tw("obsessão", 566.5), 960, 210, T("a busca vira quase uma obsessão", 40), anim="fade")
    if t > tw("reconhece", 570.5):
        rnd = random.Random(3)
        n = int(140 * ease_out(prog(t, tw("cento", 571), 3.0)))
        for k in range(n):
            x, y = rnd.uniform(560, 1560), rnd.uniform(560, 980)
            c.save(); c.translate(x, y); c.scale(0.5, 0.5); pin(c, RED if k % 5 else AMBER); c.restore()
        counter_text(c, t, tw("cento", 571), 140, 960, 360, 120, AMBER, prefix="+", d=3.0)
        show(c, t, tw("tentativas", 572), 960, 460, T("tentativas reconhecidas pelo Egito", 34), anim="fade")
    show(c, t, tw("sérias", 576.9), 600, 1010, lambda c: caption_box(c, "algumas sérias", 34), anim="up")
    show(c, t, tw("tanto", 578.0), 1320, 1010, lambda c: caption_box(c, "outras, nem tanto", 34), anim="up")


def s42(c, t):  # 580.7 - 585.4  as teorias: quatro caminhos
    night(c, t, 760, moon_xy=None)
    show(c, t, 580.9, 1100, 140, lambda c: stitle(c, "QUATRO CAMINHOS", 0, 0, 74, AMBER, AMBER), anim="up")
    for i, (n, ttl, sub) in enumerate(CARDS):
        show(c, t, tw("quatro", 581) + i * 0.3, 560 + i * 345, 580, lambda c, n=n, ttl=ttl, sub=sub, i=i: theory_card(c, n, ttl, card_icon(i), sub=sub),
             anim="up")
    fog(c, t, 960, 0.05)
    HIST(c, t, [(0, "present")], [(0, "think")], x=200, s=0.8)


def s43(c, t):  # 585.4 - 608.7  1: nunca saiu de Alexandria; cidade moderna em cima; mapa de el Falaki
    if t < tw("Um", 595.9):
        night(c, t, 700, moon_xy=None)
        show(c, t, 585.6, 960, 120, lambda c: hl(c, "1 - ele nunca saiu de Alexandria", 0, 0, 46), anim="up")
        c.save(); c.translate(960, 760); modern_city(c, t, 1920); c.restore()
        c.rectangle(0, 760, W, 320); rgb(c, (0.22, 0.17, 0.11)); c.fill()
        line(c, 0, 760, W, 760, 4, (0.55, 0.45, 0.30))
        k = fade_in(t, tw("debaixo", 588.6), 1.2)
        faded(c, k, lambda c: (c.save(), c.translate(1100, 1010), c.scale(0.45, 0.45), mausoleum(c), c.restore()))
        show(c, t, tw("debaixo", 588.6), 1500, 900, T("a cidade antiga", 34, AMBER), anim="fade")
        show(c, t, tw("cresceu", 590), 960, 210, T("a cidade moderna cresceu em cima da antiga", 36), anim="fade")
    else:
        night(c, t, 760, moon_xy=None)
        c.save(); c.translate(1100, 560); street_grid(c, t, 1300, 760, ease_out(prog(t, tw("mapa", 596), 2.0))); c.restore()
        show(c, t, tw("Mahmud", 597), 1100, 120, lambda c: hl(c, "o mapa de Mahmud el Falaki", 0, 0, 42), anim="up")
        show(c, t, tw("ruas", 600), 1100, 980, T("as ruas da Alexandria antiga", 34), anim="fade", t1=602.0)
        if t > tw("cruzamento", 603):
            x, y = 1100 + 1300 / 12, 560
            glow(c, x, y, 120, AMBER, 0.4)
            circle(c, x, y, 34 + 6 * math.sin(t * 4), None, 6, RED)
            show(c, t, tw("cruzamento", 603), 1100, 980, lambda c: caption_box(c, "o cruzamento das duas avenidas principais", 36), anim="up")
        HIST(c, t, [(0, "point_r")], [(0, "think")], x=240, s=0.85)


def s44(c, t):  # 608.7 - 616.4  o problema: ruas, prédios, mesquita; escavar é quase impossível
    night(c, t, 700, moon_xy=None)
    c.save(); c.translate(960, 860); modern_city(c, t, 1920, seed=8); c.restore()
    c.save(); c.translate(1200, 860); mosque(c, 320, 240); c.restore()
    c.rectangle(0, 860, W, 220); rgb(c, (0.20, 0.16, 0.11)); c.fill()
    show(c, t, 608.9, 960, 120, T("o problema:", 44), anim="fade")
    for i, (s, w) in enumerate((("ruas", "ruas"), ("prédios", "prédios"), ("uma mesquita", "mesquita"))):
        show(c, t, tw(w, 608.8), 560 + i * 400, 220, lambda c, s=s: hl(c, s, 0, 0, 40), anim="pop")
    show(c, t, tw("Escavar", 613), 960, 980, lambda c: stitle(c, "escavar é quase impossível", 0, 0, 56, RED, BLOOD), anim="stamp")


def s45(c, t):  # 616.4 - 633.6  Calíope Papakosta, Jardins de Shallalat; estátua de mármore; caminho certo
    night(c, t, 760, moon_xy=(1700, 150))
    ground(c, 900, (0.20, 0.22, 0.14))
    for x in (1500, 1700):
        c.save(); c.translate(x, 900); palm_oasis(c, t); c.restore()
    fig(c, t, 760, 900, 0.85, [(0, "stand"), (tw("encontrou", 623), "present"), (tw("acredita", 630), "thumb")],
        [(0, "neutral"), (tw("acredita", 630), "confident")], fid=107, appear=616.8, **ARQUEOLOGA)
    show(c, t, tw("Calíope", 618), 760, 420, lambda c: hl(c, "CALÍOPE PAPAKOSTA", 0, 0, 36), anim="up")
    show(c, t, tw("Shallalat", 620), 960, 120, T("Jardins de Shallalat, o antigo bairro real", 38), anim="fade")
    show(c, t, tw("estátua", 624), 1200, 900, sc(marble_bust, s=1.1), anim="up")
    show(c, t, tw("mármore", 624), 1200, 560, T("estátua de mármore", 32, AMBER), anim="fade")
    show(c, t, tw("túmulo", 629), 960, 210, lambda c: hl(c, "o túmulo? ainda não.", 0, 0, 42), anim="up")
    fog(c, t, 930, 0.06)


def s46(c, t):  # 633.6 - 659.7  2: Siwa; Liana Suvaltzi 1995; comissão discorda; licença cancelada
    night(c, t, 740, moon_xy=(1680, 150))
    dunes(c, t, 860)
    for x in (1280, 1420, 1620):
        c.save(); c.translate(x, 880); c.scale(0.9, 0.9); palm_oasis(c, t + x); c.restore()
    show(c, t, 633.8, 960, 120, lambda c: hl(c, "2 - o deserto: o oásis de Siwa", 0, 0, 46), anim="up", t1=646.8)
    if t < tw("comissão", 649):
        show(c, t, tw("mil", 635), 960, 210, lambda c: date_stamp(c, "1995", 46, AMBER), anim="stamp")
        fig(c, t, 680, 900, 0.85, [(0, "stand"), (tw("anunciou", 640), "arms_up")], [(0, "happy")], fid=108, appear=638.5, **ARQUEOLOGA)
        show(c, t, tw("Liana", 638), 680, 420, lambda c: hl(c, "LIANA SUVALTZI", 0, 0, 36), anim="up")
        if t > tw("notícia", 646):
            show(c, t, tw("notícia", 646), 1150, 420, sc(newspaper, "TÚMULO DE ALEXANDRE ACHADO?", "Siwa, Egito", s=0.9), anim="drop")
    else:
        c.save(); c.translate(1000, 880); c.scale(0.8, 0.8); temple(c, 520, 300); c.restore()
        for i, x in enumerate((500, 650)):
            fig(c, t, x, 900, 0.7, [(0, "think"), (tw("discordou", 651), "shrug")], [(0, "think")], fid=109 + i, **SECXIX)
        show(c, t, tw("comissão", 649), 960, 120, T("uma comissão de especialistas foi até lá", 38), anim="fade")
        show(c, t, tw("templo", 653), 1000, 330, lambda c: hl(c, "um templo, não um túmulo", 0, 0, 44), anim="up")
        show(c, t, tw("licença", 656), 1000, 990, lambda c: hl(c, "LICENÇA CANCELADA", 0, 0, 52, bg=RED, col=INK), anim="stamp")
    fog(c, t, 930, 0.08)


def s47(c, t):  # 659.7 - 683.7  3: Veneza; 828, roubo do corpo de São Marcos (sob carne de porco); a basílica
    if t < tw("Em", 665.7):
        draw_med_map(c, WORLD, grid=5)
        show(c, t, 660.0, 960, 120, lambda c: hl(c, "3 - o mais estranho de todos", 0, 0, 46), anim="up")
        map_point(c, WORLD, *ALEX, AMBER, 10, t)
        map_label(c, WORLD, *ALEX, "Alexandria", 30, AMBER, dy=36)
        if t > tw("Veneza", 663):
            p = ease_io(prog(t, tw("Veneza", 663), 1.6))
            map_path(c, WORLD, VENICE_ROUTE, p, AMBER, 6, dash=[14, 10])
            map_point(c, WORLD, *VENICE, AMBER, 10, t)
            show(c, t, tw("Veneza", 663) + 1.0, *(lambda p: (p[0] + 90, p[1] + 10))(WORLD(*VENICE)), T("VENEZA", 40, AMBER), anim="pop")
    elif t < tw("É", 679.4):
        sea(c, t, 760, 0.15)
        night(c, t, 700, moon_xy=(1680, 150))
        show(c, t, tw("Em", 665.7), 960, 110, lambda c: date_stamp(c, "828", 52, AMBER), anim="stamp")
        x = 520 + (t - 666.0) * 40
        c.save(); c.translate(x, 770 + math.sin(t) * 6); c.scale(0.65, 0.65); ancient_ship(c); c.restore()
        for i in range(2):
            fig(c, t, x - 40 + i * 70, 740, 0.4, [(0, "hold")], [(0, "worried")], fid=110 + i, **MERCADOR)
        show(c, t, tw("mercadores", 666), 1250, 260, T("dois mercadores venezianos", 38), anim="fade")
        show(c, t, tw("São", 668), 1250, 340, lambda c: hl(c, "o corpo de São Marcos", 0, 0, 44), anim="up")
        if t > tw("porco", 672):
            show(c, t, tw("porco", 672), 1350, 560, sc(barrel, False, BROWN, "PORCO", s=0.7), anim="drop")
            show(c, t, tw("guardas", 673), 1250, 980, lambda c: caption_box(c, "escondido sob carne de porco", 38), anim="up")
    else:
        night(c, t, 760, moon_xy=(1680, 150))
        sea(c, t, 940, 0.05)
        c.save(); c.translate(960, 930); basilica(c, 760, 420); c.restore()
        show(c, t, tw("É", 679.4), 960, 120, lambda c: hl(c, "BASÍLICA DE SÃO MARCOS", 0, 0, 48), anim="up")
    fog(c, t, 960, 0.06)


def s48(c, t):  # 683.7 - 708.0  Andrew Chugg: e se Alexandre virou São Marcos? maioria não aceita; nunca testada
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.04, 0.03)); c.fill()
    lantern_beam(c, 1200, 640, 560)
    fig(c, t, 640, 960, 0.85, [(0, "present"), (tw("hipótese", 684), "finger_up")], [(0, "think")], fid=112, appear=684.0,
        shirt=(0.36, 0.40, 0.46), hair="tuft", glasses=True)
    show(c, t, tw("Andrew", 684), 640, 560, lambda c: hl(c, "ANDREW CHUGG", 0, 0, 36), anim="up", t1=700.6)
    show(c, t, tw("hipótese", 684), 1200, 120, T("uma hipótese ousada", 40, AMBER), anim="fade", t1=688.2)
    c.save(); c.translate(1200, 840); c.scale(1.3, 1.3); royal_coffin(c, "glass", t=t); c.restore()
    if t > tw("salvar", 688.3):
        a = fade_in(t, tw("Alexandre", 688.3)) * (1 - fade_in(t, tw("identificado", 689), 0.6))
        b = fade_in(t, tw("Marcos", 690), 0.6)
        if a > 0:
            faded(c, a, lambda c: hl(c, "ALEXANDRE", 1200, 300, 50))
        if b > 0:
            faded(c, b, lambda c: hl(c, "\"SÃO MARCOS\"", 1200, 300, 50, bg=ICE))
        show(c, t, tw("identificado", 689), 1200, 200, T("rebatizado para ser salvo?", 36), anim="fade", t1=700.6)
    show(c, t, tw("conquistador", 696), 1200, 1000, lambda c: caption_box(c, "o corpo em Veneza seria o do conquistador", 36), anim="up", t1=700.6)
    if t > 700.7:
        show(c, t, 700.8, 1200, 200, T("a maioria dos historiadores não aceita", 36), anim="fade")
        show(c, t, tw("testada", 703.5), 1200, 1000, lambda c: caption_box(c, "a hipótese nunca foi testada", 36), anim="up")
    HIST(c, t, [(0, "think")], [(0, "think")], x=1720, s=0.7)


def s49(c, t):  # 708.0 - 727.3  4: Grécia; Anfípolis 2014; esfinges, cariátides, mosaico, ossos; Heféstion
    night(c, t, 760, moon_xy=(1680, 150))
    ground(c, 900, (0.22, 0.20, 0.14))
    show(c, t, 708.2, 960, 110, lambda c: hl(c, "4 - de volta para a Grécia", 0, 0, 46), anim="up", t1=711.1)
    show(c, t, tw("dois", 711), 960, 110, lambda c: date_stamp(c, "2014  -  ANFÍPOLIS", 46, AMBER), anim="stamp")
    if t < tw("Esfinges", 719):
        show(c, t, 708.4, 1050, 900, sc(tumulus, 1100, 300, s=1.0), anim="up", d=0.8)
        show(c, t, tw("maior", 715), 1050, 210, T("o maior túmulo antigo já achado na Grécia", 38), anim="fade")
    else:
        for i, (fn, x, s) in enumerate(((sc(sphinx, s=1.0), 640, "esfinges"), (sc(caryatid, s=1.0), 960, "cariátides"),
                                        (lambda c: (rrect(c, -110, -170, 220, 170, 6), fs(c, (0.40, 0.30, 0.22), 5),
                                                    circle(c, 0, -85, 50, (0.70, 0.55, 0.30), 4), circle(c, 0, -85, 22, (0.30, 0.40, 0.55), 3)), 1280, "mosaico"),
                                        (sc(bone, 200, s=0.9), 1600, "ossos humanos"))):
            tt = tw(s.split()[0][:5], 719)
            show(c, t, tt, x, 760, fn, anim="up")
            show(c, t, tt + 0.2, x, 820, T(s, 32, AMBER), anim="fade")
        show(c, t, tw("meses", 723.9), 1100, 260, lambda c: hl(c, "o mundo achou que era Alexandre", 0, 0, 44), anim="up", t1=727.2)
    HIST(c, t, [(0, "point_r")], [(0, "neutral")], x=240, s=0.85)
    fog(c, t, 930, 0.06)


def s49b(c, t):  # 727.3 - 733.7  hoje: Heféstion
    night(c, t, 760, moon_xy=(1680, 150))
    ground(c, 900, (0.22, 0.20, 0.14))
    c.save(); c.translate(1150, 900); tumulus(c, 1000, 280); c.restore()
    show(c, t, 727.5, 1150, 160, T("hoje, a equipe que escavou acredita:", 40), anim="fade")
    show(c, t, tw("Heféstion", 727.4), 1150, 270, lambda c: hl(c, "HEFÉSTION", 0, 0, 60), anim="up")
    show(c, t, tw("amigo", 728), 1150, 370, T("o amigo mais próximo do rei", 38, AMBER), anim="fade")
    HIST(c, t, [(0, "think")], [(0, "think")], x=300, s=0.9)
    fog(c, t, 930, 0.06)


def s50(c, t):  # 733.7 - 751.8  sobram as perguntas
    night(c, t, 760, moon_xy=None)
    show(c, t, 733.9, 1100, 120, lambda c: stitle(c, "sobram as perguntas", 0, 0, 66, AMBER, AMBER), anim="up")
    qs = (("destruído nas guerras?", tw("destruído", 736), lambda c: (c.translate(0, 70), flames(c, t, 160, 120))),
          ("debaixo d'água?", tw("debaixo", 740.5), lambda c: (c.translate(0, 80), c.scale(0.4, 0.4), column(c))),
          ("atrás de tijolos?", tw("Debaixo", 743), lambda c: (c.translate(0, 110), brick_wall(c, 180, 150))),
          ("em Veneza?", tw("Ou", 747.6), lambda c: (c.translate(0, 80), c.scale(0.3, 0.3), basilica(c))))
    for i, (s, tt, icon) in enumerate(qs):
        show(c, t, tt, 520 + i * 360, 520, lambda c, s=s, icon=icon, i=i: theory_card(c, str(i + 1), "", icon, w=320, h=360,
                                                                                     sub=None) or text(c, s, 0, 230, 32, TYPE, AMBER), anim="up")
    HIST(c, t, [(0, "think")], [(0, "think")], x=200, s=0.75)
    fog(c, t, 960, 0.05)


def s51(c, t):  # 751.8 - 765.5  o homem que conquistou o mundo... esquecido
    c.rectangle(0, 0, W, H); rgb(c, (0.04, 0.03, 0.03)); c.fill()
    k = 1 - fade_in(t, tw("Esquecido", 760) - 0.3, 1.6)
    lantern_beam(c, 1150, 640, 520 * max(0.2, k))
    faded(c, max(0.15, k), lambda c: (c.save(), c.translate(1150, 760), c.scale(1.3, 1.3), royal_coffin(c, "gold"), c.restore()))
    show(c, t, 752.0, 1150, 180, T("conquistou o mundo antes dos 33 anos", 40), anim="fade", t1=tw("Esquecido", 760) - 0.4)
    show(c, t, tw("troféu", 755), 1150, 250, T("disputado como um troféu", 36, AMBER), anim="fade", t1=tw("Esquecido", 760) - 0.4)
    show(c, t, tw("visitado", 757), 1150, 310, T("visitado por César e Augusto", 36), anim="fade", t1=tw("Esquecido", 760) - 0.4)
    show(c, t, tw("Esquecido", 760), 1150, 330, lambda c: stitle(c, "ESQUECIDO", 0, 0, 120, INK, None), anim="fade", d=1.2)
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=320)


def s52(c, t):  # 765.5 - 772.6  e você? onde está? deixe sua teoria
    night(c, t, 760, moon_xy=None)
    show(c, t, 765.6, 1100, 110, lambda c: stitle(c, "E você?", 0, 0, 72, INK, AMBER), anim="up")
    show(c, t, tw("Onde", 766), 1100, 200, T("onde está o corpo de Alexandre?", 40), anim="fade")
    for i, (n, ttl, sub) in enumerate(CARDS):
        show(c, t, 767.0 + i * 0.3, 600 + i * 340, 560, lambda c, n=n, ttl=ttl, i=i: theory_card(c, n, ttl, card_icon(i), w=300, h=380),
             anim="up")
    show(c, t, tw("Deixa", 768), 1100, 920, lambda c: (speech(c, 820, 130, -300, 110), text(c, "deixe sua teoria nos comentários", 0, 0, 42, HAND, INK)),
         anim="pop")
    HIST(c, t, [(0, "point_r"), (769.0, "present")], [(0, "think"), (769.0, "happy")], x=200, s=0.8)


def s53(c, t):  # 772.6 - fim  encerramento
    night(c, t, 740, moon_xy=(1640, 160))
    dunes(c, t, 900)
    k = fade_in(t, 772.6, 2.0)
    for x, s in ((1500, 0.7), (1700, 0.45)):
        faded(c, 0.6 * k, lambda c, x=x, s=s: (c.save(), c.translate(x, 920), c.scale(s, s), pyramid(c), c.restore()))
    HIST(c, t, [(0, "stand"), (773.0, "present"), (775.8, "wave"), (777.8, "stand")], [(0, "neutral"), (774.5, "happy")], x=420, s=1.05)
    show(c, t, 773.1, 1100, 260, T("Eu sou o Historiador.", 44, AMBER), anim="fade")
    show(c, t, 774.6, 1100, 470, sc(subscribe_btn, t > 776.0, s=0.9))
    show(c, t, 775.0, 1430, 470, sc(bell, s=0.8), rot=math.sin(t * 18) * 0.2 * max(0, 1 - (t - 775.0)))
    show(c, t, 775.6, 1100, 720, lambda c: (text(c, "PONTO CEGO", 0, 0, 84, SERIF, INK), line(c, -300, 58, 300, 58, 3, AMBER)), anim="fade", d=1.2)
    fog(c, t, 980, 0.09)


SCENES = [
    (0.0, 11.8, s01), (11.8, 27.4, s02), (27.4, 43.1, s03), (43.1, 47.5, s04), (47.5, 58.4, s05), (58.4, 73.5, s06),
    (73.5, 92.3, s07), (92.3, 101.5, s08), (101.5, 111.6, s09), (111.6, 121.5, s10), (121.5, 133.8, s11),
    (133.8, 153.3, s12), (153.3, 170.5, s13),
    (170.5, 181.4, s14), (181.4, 188.3, s15), (188.3, 197.8, s16), (197.8, 208.5, s17), (208.5, 229.2, s18),
    (229.2, 239.2, s19), (239.2, 253.5, s20), (253.5, 272.1, s21), (272.1, 289.5, s22), (289.5, 295.3, s23),
    (295.3, 305.3, s24), (305.3, 324.3, s25), (324.3, 332.5, s26), (332.5, 347.0, s27), (347.0, 355.9, s28),
    (355.9, 364.1, s29),
    (364.1, 372.2, s30), (372.2, 388.6, s31), (388.6, 409.7, s32), (409.7, 428.5, s33), (428.5, 442.1, s34),
    (442.1, 462.6, s35), (462.6, 488.6, s36), (488.6, 505.3, s37), (505.3, 525.1, s38), (525.1, 544.3, s39),
    (544.3, 566.3, s40),
    (566.3, 580.7, s41), (580.7, 585.4, s42), (585.4, 608.7, s43), (608.7, 616.4, s44), (616.4, 633.6, s45),
    (633.6, 659.7, s46), (659.7, 683.7, s47), (683.7, 708.0, s48), (708.0, 727.3, s49), (727.3, 733.7, s49b),
    (733.7, 751.8, s50), (751.8, 765.5, s51), (765.5, 772.6, s52), (772.6, 999.0, s53),
]

# Sons: nada automático (sem whoosh em transição, sem som em cada ícone). Só toques sem chiado nos momentos-chave.
SFX_OFF = True
SFX = [(8.9, "tum"), (40.8, "boom"), (43.9, "boom"), (100.0, "heartbeat"), (109.6, "tum"), (177.9, "boom"), (198.0, "tum"),
       (322.4, "heartbeat"), (345.0, "bell"), (384.4, "boom"), (400.8, "boom"), (436.3, "bell"), (495.3, "tum"), (563.7, "tum"),
       (657.0, "tum"), (764.4, "bell"), (775.6, "boom")]
