"""O Mistério do Mary Celeste — Ponto Cego.
Narração: Pedro Lima - Serious (HeyGen / ElevenLabs v4), 3 blocos com 1 s de silêncio entre eles (564,9 s).
Tempos: videos/mary-celeste/narracao_blocos.txt. B2(x)/B3(x) convertem o tempo local do bloco em tempo absoluto.
"""
from engine import *

O2, O3 = 160.687, 355.516


def B2(x):
    return x + O2


def B3(x):
    return x + O3


ATL = make_proj(-80, 15, 24, 56)              # Atlântico Norte
EAST = make_proj(-40, 16, 29, 47)             # Açores -> Itália
AZ = make_proj(-32, -7, 34, 42.5)            # Açores -> Portugal
GIB = make_proj(-30, 0, 31, 44)               # achado -> Gibraltar
SM = make_proj(-27.6, -23.6, 36.1, 38.5)      # Santa Maria

NY = (-74.0, 40.7)
SPENCER = (-64.7, 45.35)
GENOA = (8.9, 44.4)
GIBRALTAR = (-5.35, 36.14)
LASTLOG = (-25.02, 37.02)
FOUND = (-17.25, 38.33)
ROUTE = [NY, (-66, 39.3), (-55, 38.0), (-42, 37.2), (-32, 37.0), LASTLOG]
ROUTE_DG = [NY, (-66, 39.6), (-55, 38.6), (-42, 38.2), (-30, 38.4), FOUND]
ROUTE_PLAN = [LASTLOG, (-15, 36.6), (-7, 35.95), GIBRALTAR, (-1, 37.0), (5, 39.5), GENOA]

CAPTAIN = dict(shirt=(0.86, 0.85, 0.80), coat=(0.14, 0.18, 0.30), hat="pilot", hair=None, mustache=True)
SAILOR = dict(shirt=(0.30, 0.36, 0.52), hat="sailor", hair=None)


# ------------------------------------------------------------------ helpers
def HIST(c, t, poses, exprs, appear=None, x=300, y=1010, s=0.95, **kw):
    historiador(c, t, x, y, s, poses, exprs, appear=appear, look=1, **kw)


def faded(c, a, fn):
    """desenha fn(c) com opacidade a"""
    if a <= 0.001:
        return
    if a >= 0.999:
        fn(c); return
    c.push_group(); fn(c); c.pop_group_to_source(); c.paint_with_alpha(a)


def fig(c, t, x, y, s, poses=((0, "stand"),), exprs=((0, "neutral"),), alpha=1.0, **kw):
    faded(c, alpha, lambda c: figure(c, t, x, y, s, poses=poses, exprs=exprs, **kw))


def night(c, t, horizon=600, rough=0.25, moon_xy=(1560, 170)):
    stars(c, t, 80, horizon - 40)
    if moon_xy:
        c.save(); c.translate(*moon_xy); moon(c, 52); c.restore()
        glow(c, moon_xy[0], moon_xy[1], 200, ICE, 0.10)
    sea(c, t, horizon, rough)


def ship(c, t, x, y, s=0.6, torn=0.0, rock=1.0, name=None, alpha=1.0, sails=True, tilt=0.0):
    def f(c):
        c.save()
        c.translate(x, y + math.sin(t * 1.1) * 6 * rock)
        c.rotate(tilt + math.sin(t * 0.8) * 0.025 * rock)
        c.scale(s, s)
        brigantine(c, t, torn, name, sails=sails)
        c.restore()
    faded(c, alpha, f)


def deck(c, y=700):
    c.rectangle(0, y, W, H - y); rgb(c, (0.16, 0.12, 0.09)); c.fill()
    for k in range(9):
        yy = y + k * (18 + k * 6)
        line(c, 0, yy, W, yy, 2, (0.26, 0.20, 0.14))
    line(c, 0, y, W, y, 5, (0.40, 0.30, 0.20))


def x_over(c, t, t0, x, y, s=70):
    show(c, t, t0, x, y, lambda c: big_x(c, s, RED, 14), anim="stamp")


def labeled(fn, label, dy=130, size=36, col=INK):
    return group(fn, at(0, dy, T(label, size, col)))


def bottle(c):
    rrect(c, -30, -40, 60, 120, 12); fs(c, (0.25, 0.40, 0.30), 5)
    c.rectangle(-12, -90, 24, 52); fs(c, (0.25, 0.40, 0.30), 5)
    c.rectangle(-26, -10, 52, 40); fs(c, PARCH, 3)


def skull_flag(c):
    line(c, -110, -110, -110, 150, 6)
    c.rectangle(-110, -110, 220, 140); fs(c, (0.06, 0.06, 0.07), 5)
    circle(c, 0, -50, 26, INK, 0)
    c.rectangle(-14, -32, 28, 18); rgb(c, INK); c.fill()
    circle(c, -10, -54, 7, (0.06, 0.06, 0.07), 0); circle(c, 10, -54, 7, (0.06, 0.06, 0.07), 0)
    line(c, -40, -10, 40, 20, 7); line(c, 40, -10, -40, 20, 7)


def card(c, title_s, icon, note=None, w=360, h=430):
    rrect(c, -w / 2, -h / 2, w, h, 14); fs(c, (0.13, 0.13, 0.15), 5, PARCH2)
    text(c, title_s, 0, -h / 2 + 50, 46, SERIF, AMBER)
    c.save(); c.translate(0, 10); icon(c); c.restore()
    if note:
        text(c, note, 0, h / 2 - 40, 28, TYPE, INK)


def open_book(c, w=1100, h=560):
    for sx in (-1, 1):
        c.move_to(0, -h / 2); c.curve_to(sx * w * 0.2, -h / 2 - 30, sx * w * 0.4, -h / 2 - 20, sx * w / 2, -h / 2 + 10)
        c.line_to(sx * w / 2, h / 2); c.curve_to(sx * w * 0.4, h / 2 - 30, sx * w * 0.2, h / 2 - 40, 0, h / 2 - 10)
        c.close_path(); fs(c, PARCH, 6)
        for k in range(9):
            y = -h / 2 + 90 + k * 48
            line(c, sx * 60, y, sx * (w / 2 - 50), y, 2, (0.62, 0.52, 0.36))
    line(c, 0, -h / 2, 0, h / 2 - 10, 4, DARKTXT)


def vapor(c, t, x, y, n=5, a=0.25):
    for i in range(n):
        ph = (t * 0.35 + i / n) % 1
        xx = x + math.sin(t * 0.8 + i * 1.7) * 30 + (i - n / 2) * 30
        yy = y - ph * 260
        glow(c, xx, yy, 60 + ph * 80, (0.62, 0.78, 0.58), a * math.sin(math.pi * ph))


def mini_ship(c, proj, lonlat, s=0.13, col_alpha=1.0, t=0):
    x, y = proj(*lonlat)
    ship(c, t, x, y, s, rock=0.3, alpha=col_alpha)


def path_end(proj, pts, p):
    xy = [proj(*q) for q in pts]
    seg = [math.hypot(xy[i + 1][0] - xy[i][0], xy[i + 1][1] - xy[i][1]) for i in range(len(xy) - 1)]
    tot = sum(seg) * clamp01(p)
    for i, L in enumerate(seg):
        if tot <= L or i == len(seg) - 1:
            k = min(1, tot / L) if L else 1
            return xy[i][0] + (xy[i + 1][0] - xy[i][0]) * k, xy[i][1] + (xy[i + 1][1] - xy[i][1]) * k
        tot -= L
    return xy[-1]


def atl_map(c, proj, labels=True):
    draw_map(c, proj, ATLANTIC, grid=10)
    azores(c, proj)
    if labels:
        map_label(c, proj, -45, 29.5, "OCEANO ATLÂNTICO", 34, (0.45, 0.52, 0.62), SERIF)


# ------------------------------------------------------------------ 0:00 abertura
def s01(c, t):  # 0 - 18.78  navio estranho no horizonte
    night(c, t, 620, 0.3)
    show(c, t, 0.3, 960, 110, lambda c: date_stamp(c, "4 DE DEZEMBRO DE 1872", 46, AMBER), anim="stamp")
    show(c, t, 4.6, 960, 210, T("meio do Oceano Atlântico", 38), anim="fade")
    if t > 8.4:
        a = clamp01((t - 8.4) / 1.5)
        zig = math.sin((t - 12.2) * 1.6) * 0.06 if t > 12.2 else 0
        xx = 1250 + (t - 8.4) * 6 + (math.sin((t - 12.2) * 0.8) * 70 if t > 12.2 else 0)
        ship(c, t, xx, 650, 0.42, torn=0.8, alpha=a * 0.9, tilt=zig)
        glow(c, xx, 520, 260, ICE, 0.05 * a)
    show(c, t, 12.4, 1250, 870, lambda c: caption_box(c, "ziguezagueava", 36), anim="up", t1=15.2)
    show(c, t, 13.6, 1250, 870, lambda c: caption_box(c, "velas rasgadas", 36), anim="up", t1=15.5)
    show(c, t, 15.6, 1250, 870, lambda c: caption_box(c, "ninguém respondia", 36), anim="up")
    show(c, t, 16.3, 1290, 330, sc(qmark, 110, AMBER), anim="pop")
    fog(c, t, 700, 0.07)
    HIST(c, t, [(0, "stand"), (8.7, "point_r"), (11.5, "think")], [(0, "neutral"), (8.7, "worried")], appear=0.6)


def s02(c, t):  # 18.78 - 33.04  tudo no lugar, ninguém a bordo
    stars(c, t, 50, 500)
    deck(c, 760)
    dim = 1 - 0.65 * clamp01((t - 29.7) / 0.8)
    items = [(20.8, 640, labeled(sc(barrel, label="6 MESES", s=0.9), "comida", 140)),
             (23.2, 960, labeled(sc(barrel, label="ÁGUA", col=(0.36, 0.30, 0.24), s=0.9), "água potável", 140)),
             (24.4, 1280, labeled(group(at(-55, 20, sc(barrel, s=0.7)), at(55, 20, sc(barrel, s=0.7)), at(0, -90, sc(barrel, s=0.7))),
                                  "carga intacta", 140)),
             (26.3, 1600, labeled(group(sc(sea_chest, s=0.8), at(0, -95, sc(folded_clothes, s=0.75))), "roupas dobradas", 140))]
    c.push_group()
    for t0, x, fn in items:
        show(c, t, t0, x, 560, fn, anim="up")
    c.pop_group_to_source(); c.paint_with_alpha(dim)
    show(c, t, 29.7, 1120, 200, lambda c: stitle(c, "NINGUÉM A BORDO", 0, 0, 80, RED, BLOOD), anim="stamp")
    fog(c, t, 860, 0.06)
    HIST(c, t, [(0, "present"), (23, "point_r"), (29.7, "head")], [(0, "neutral"), (29.7, "shocked")])


def s03(c, t):  # 33.04 - 46.24  dez pessoas
    stars(c, t, 70, 700)
    fade = 1 - 0.7 * clamp01((t - 39.4) / 1.2)
    people = ["c", "w", "g", "m", "m", "k", "s", "s", "s", "s"]
    xs = [620 + i * 130 for i in range(10)]
    for i, (kind, x) in enumerate(zip(people, xs)):
        t0 = 33.1 + i * 0.14
        if t < t0:
            continue
        a = clamp01((t - t0) / 0.3) * fade
        hi = (kind == "w" and t > 36.5) or (kind == "g" and t > 37.4)
        if hi and t < 39.6:
            glow(c, x, 820, 160, AMBER, 0.25)
        kw = dict(CAPTAIN) if kind == "c" else dict(SAILOR) if kind == "s" else dict(shirt=(0.36, 0.40, 0.46))
        sz = 0.55
        if kind == "w":
            kw = dict(shirt=(0.48, 0.26, 0.36), hair="long")
        if kind == "g":
            kw = dict(shirt=PINK, hair="long"); sz = 0.32
        if kind == "k":
            kw = dict(shirt=(0.62, 0.58, 0.50), hat="sailor", hair=None)
        fig(c, t, x, 960, sz, exprs=[(0, "neutral")], alpha=a, fid=20 + i, **kw)
    show(c, t, 33.1, 1200, 150, lambda c: stitle(c, "10 pessoas desaparecidas", 0, 0, 62, INK, AMBER), anim="up")
    show(c, t, 36.6, 880, 560, T("uma mulher", 34, AMBER), anim="fade", t1=39.5)
    show(c, t, 37.5, 1010, 640, T("uma menina de 2 anos", 34, AMBER), anim="fade", t1=39.5)
    if t > 39.6:
        show(c, t, 39.6, 1200, 360, sc(hourglass, t, s=0.7), anim="fade")
        show(c, t, 40.4, 1200, 560, lambda c: caption_box(c, "mais de 150 anos sem resposta", 40), anim="up")
    fog(c, t, 980, 0.06)
    HIST(c, t, [(0, "stand"), (39.5, "think")], [(0, "sad"), (42.7, "think")], x=280)


def s04(c, t):  # 46.24 - 49.72  título
    night(c, t, 700, 0.2, (1600, 160))
    a = clamp01((t - 46.2) / 1.5)
    ship(c, t, 960, 760, 0.85, torn=0.8, alpha=0.75 * a)
    glow(c, 960, 520, 520, ICE, 0.06 * a)
    show(c, t, 46.6, 960, 190, lambda c: stitle(c, "MARY CELESTE", 0, 0, 120, INK, AMBER), anim="fade", d=0.9)
    show(c, t, 47.8, 960, 300, T("o navio fantasma do Atlântico", 40, AMBER), anim="fade", d=0.8)
    fog(c, t, 820, 0.09, 7)


def s05(c, t):  # 49.72 - 59.64  1861, Nova Escócia
    atl_map(c, ATL)
    show(c, t, 50.0, 960, 120, lambda c: stitle(c, "Antes do mistério", 0, 0, 56, INK, AMBER), anim="up")
    show(c, t, 54.9, 1150, 860, lambda c: date_stamp(c, "1861", 70, AMBER), anim="stamp")
    if t > 57.8:
        map_point(c, ATL, *SPENCER, AMBER, 11, t)
        show(c, t, 57.9, *ATL(-60, 49.6), T("estaleiro na Nova Escócia, Canadá", 32), anim="fade")


def s06(c, t):  # 59.64 - 68.55  se chamava Amazon; bergantim
    night(c, t, 760, 0.15, (1650, 140))
    ship(c, t, 1150, 780, 0.95, rock=0.6)
    show(c, t, 60.0, 1150, 120, T("mas não com esse nome...", 38), anim="fade", t1=61.7)
    show(c, t, 61.9, 1150, 120, lambda c: nameboard(c, "AMAZON", 60), anim="stamp")
    if t > 63.3:
        show(c, t, 63.3, 1650, 330, T("bergantim", 44, AMBER), anim="fade")
        show(c, t, 64.4, 1650, 400, T("veleiro de 2 mastros", 34), anim="fade")
        arrow_draw(c, t, 64.6, 1560, 410, 1225, 430)
        arrow_draw(c, t, 64.8, 1560, 430, 1080, 520)
    if t > 66.8:
        p = ease_out(prog(t, 66.8, 0.6))
        x0, x1 = 1150 - 230 * 0.95, 1150 + 320 * 0.95
        line(c, x0, 870, x0 + (x1 - x0) * p, 870, 4, AMBER)
        line(c, x0, 850, x0, 890, 4, AMBER)
        if p > 0.99:
            line(c, x1, 850, x1, 890, 4, AMBER)
        show(c, t, 67.0, 1170, 930, T("~30 metros", 36, AMBER), anim="fade")
    HIST(c, t, [(0, "present"), (63.2, "point_r")], [(0, "neutral"), (61.9, "think")])
    fog(c, t, 900, 0.06)


def s07(c, t):  # 68.55 - 81.98  fama de azarado
    stars(c, t, 60, 600)
    show(c, t, 68.6, 1100, 110, lambda c: stitle(c, "Fama de azarado", 0, 0, 62, INK, AMBER), anim="up")
    show(c, t, 71.7, 720, 520, labeled(tombstone, "1º capitão: morreu na viagem de estreia", 140, 30), anim="drop")
    if t > 75.5:
        a = clamp01((t - 75.5) / 0.6)
        c.push_group()
        c.save(); c.translate(1420, 280); storm_cloud(c, 600, 130); c.restore()
        if 76.8 < t < 77.2 or 78.6 < t < 78.8:
            c.save(); c.translate(1380, 420); lightning(c, 0.9); c.restore()
            glow(c, 1380, 420, 420, LYELLOW, 0.20)
        sea(c, t, 640, 0.8) if False else None
        c.save(); c.translate(1420, 690); reef(c, t, 640); c.restore()
        ship(c, t, 1420, 640, 0.5, torn=0.5, rock=0.2, tilt=-0.25)
        c.pop_group_to_source(); c.paint_with_alpha(a)
    show(c, t, 76.9, 1420, 790, T("encalhou numa tempestade", 34), anim="fade")
    show(c, t, 79.8, 1420, 900, lambda c: hl(c, "vendido quase como sucata", 1, 1, 40) if False else hl(c, "vendido quase como sucata", 0, 0, 40),
         anim="stamp")
    HIST(c, t, [(0, "stand"), (71.6, "point_r"), (75.5, "shrug")], [(0, "worried"), (79.8, "sad")], x=250, s=0.85)
    fog(c, t, 960, 0.06)


def s08(c, t):  # 81.98 - 88.48  novo dono, nova bandeira, novo nome
    night(c, t, 760, 0.15, None)
    ship(c, t, 1000, 800, 0.8, rock=0.6)
    show(c, t, 82.1, 760, 200, lambda c: nameboard(c, "AMAZON", 50), anim="fade")
    if t > 83.3:
        p = ease_out(prog(t, 83.3, 0.4))
        line(c, 620, 200, 620 + 280 * p, 200, 10, RED)
    if t > 84.3:
        k = clamp01((t - 84.3) / 0.6)
        c.save(); c.translate(1500, 160)
        faded(c, 1 - k, lambda c: flag(c, "ensign", t))
        faded(c, k, lambda c: flag(c, "us", t))
        c.restore()
        show(c, t, 84.5, 1610, 470, T("nova bandeira", 32), anim="fade")
    show(c, t, 86.6, 760, 340, lambda c: nameboard(c, "MARY CELESTE", 56), anim="stamp")
    HIST(c, t, [(0, "present")], [(0, "neutral"), (86.6, "think")], x=250, s=0.85)
    fog(c, t, 940, 0.06)


def s09(c, t):  # 88.48 - 107.75  capitão Briggs
    stars(c, t, 60, 500)
    show(c, t, 88.6, 1550, 120, lambda c: date_stamp(c, "1872", 54, AMBER), anim="stamp")
    if t > 93.0:
        glow(c, 900, 700, 360, AMBER, 0.10)
    figure(c, t, 900, 1010, 1.05, poses=[(0, "stand"), (100.7, "hips"), (104.7, "present")],
           exprs=[(0, "neutral"), (100.7, "confident")], appear=93.3, fid=7, **CAPTAIN)
    show(c, t, 93.4, 900, 210, lambda c: hl(c, "Benjamin Spooner Briggs", 0, 0, 46), anim="up")
    show(c, t, 95.1, 900, 300, T("37 anos  •  capitão experiente", 36), anim="fade")
    show(c, t, 99.3, 900, 360, T("família de marinheiros de Massachusetts", 30, (0.7, 0.7, 0.75)), anim="fade")
    chips = [(102.1, 460, lambda c: caption_box(c, "sério", 38)),
             (102.7, 580, lambda c: (caption_box(c, "religioso", 38))),
             (103.9, 700, lambda c: caption_box(c, "não bebia", 38))]
    for t0, y, fn in chips:
        show(c, t, t0, 1500, y, fn, anim="left")
    show(c, t, 104.8, 1500, 860, lambda c: (donut(c, 0.125, 90, 34, AMBER), text(c, "dono de 1/8 do navio", 0, 140, 32, TYPE, INK)),
         anim="pop")
    HIST(c, t, [(0, "present"), (93.4, "point_r")], [(0, "neutral")], x=260, s=0.85)
    fog(c, t, 1000, 0.05)


def s10(c, t):  # 107.75 - 119.91  a família
    stars(c, t, 60, 500)
    show(c, t, 107.9, 960, 110, lambda c: stitle(c, "Briggs não iria sozinho", 0, 0, 58, INK, AMBER), anim="up")
    figure(c, t, 560, 1000, 0.9, poses=[(0, "stand"), (110.5, "present")], exprs=[(0, "happy")], fid=7, **CAPTAIN)
    figure(c, t, 760, 1000, 0.85, poses=[(0, "stand")], exprs=[(0, "happy")], appear=111.8, fid=8,
           shirt=(0.48, 0.26, 0.36), hair="long")
    figure(c, t, 900, 1000, 0.48, poses=[(0, "wave")], exprs=[(0, "happy")], appear=113.4, fid=9, shirt=PINK, hair="long")
    show(c, t, 111.9, 760, 540, T("Sarah", 40, AMBER), anim="fade")
    show(c, t, 113.5, 1010, 730, T("Sophia, 2 anos", 32, AMBER), anim="fade")
    if t > 115.5:
        a = clamp01((t - 115.5) / 0.6)
        c.push_group()
        line(c, 1130, 300, 1130, 1000, 3, (0.35, 0.35, 0.40))
        c.save(); c.translate(1520, 720); house(c, col=(0.45, 0.36, 0.28)); c.restore()
        glow(c, 1490, 690, 120, AMBER, 0.25)
        figure(c, t, 1700, 1000, 0.5, exprs=[(0, "sad")], fid=11, shirt=(0.40, 0.48, 0.38))
        figure(c, t, 1820, 1000, 0.72, exprs=[(0, "neutral")], fid=12, shirt=(0.40, 0.38, 0.44), hair="long")
        c.pop_group_to_source(); c.paint_with_alpha(a)
        show(c, t, 116.8, 1600, 420, T("Arthur, o filho mais velho", 34, AMBER), anim="fade")
        show(c, t, 117.6, 1600, 480, T("ficou em casa com a avó", 30), anim="fade")
    fog(c, t, 1000, 0.05)


def s11(c, t):  # 119.91 - 138.95  a tripulação
    stars(c, t, 50, 400)
    deck(c, 960)
    show(c, t, 120.0, 960, 110, lambda c: stitle(c, "Mais 7 homens", 0, 0, 60, INK, AMBER), anim="up")
    crew = [(123.96, "Albert Richardson", "1º imediato", dict(shirt=(0.30, 0.30, 0.36), hat="pilot", hair=None)),
            (126.6, "Andrew Gilling", "2º imediato", dict(shirt=(0.36, 0.34, 0.30), hair="tuft")),
            (128.6, "Edward Head", "cozinheiro", dict(shirt=(0.70, 0.68, 0.62), hair="tuft")),
            (130.1, "", "marinheiro", SAILOR), (130.25, "", "marinheiro", SAILOR),
            (130.4, "", "marinheiro", SAILOR), (130.55, "", "marinheiro", SAILOR)]
    for i, (t0, nm, role, kw) in enumerate(crew):
        x = 260 + i * 235
        figure(c, t, x, 1000, 0.6, exprs=[(0, "neutral"), (136.9, "happy")], appear=t0, fid=30 + i, **kw)
        if nm:
            show(c, t, t0 + 0.1, x, 600, T(nm, 25, AMBER), anim="fade")
        show(c, t, t0 + 0.2, x, 645, T(role, 26), anim="fade")
    if t > 131.4:
        p = ease_out(prog(t, 131.4, 0.4))
        x0, x1 = 260 + 5 * 235 - 60, 260 + 6 * 235 + 60
        c.move_to(x0, 560); c.line_to(x0, 540); c.line_to(x0 + (x1 - x0) * p, 540)
        if p > 0.99:
            c.line_to(x1, 560)
        rgb(c, AMBER); c.set_line_width(4); c.stroke()
        show(c, t, 131.5, (x0 + x1) / 2, 505, T("irmãos", 30, AMBER), anim="fade")
    show(c, t, 130.2, 1200, 470, T("4 marinheiros alemães", 30, (0.7, 0.7, 0.75)), anim="fade")
    if t > 133.2:
        show(c, t, 134.7, 960, 300, sc(envelope, s=0.8), anim="drop", t1=136.7)
        show(c, t, 136.8, 960, 310, lambda c: caption_box(c, "“uma boa tripulação”", 44), anim="up")


def s12(c, t):  # 138.95 - 147.80  a carga
    stars(c, t, 40, 300)
    rrect(c, 360, 300, 1200, 690, 16); fs(c, (0.12, 0.10, 0.09), 6, (0.40, 0.30, 0.20))
    rows = [(5, 900), (4, 760), (3, 620)]
    k = 0
    for n, y in rows:
        for j in range(n):
            x = 960 + (j - (n - 1) / 2) * 150
            show(c, t, 139.0 + k * 0.12, x, y, sc(barrel, s=0.8), anim="drop", d=0.35)
            k += 1
    show(c, t, 139.6, 1740, 420, sc(coin, s=1.0), anim="pop")
    show(c, t, 139.7, 1740, 520, T("valiosa", 32), anim="fade")
    show(c, t, 140.9, 1740, 720, lambda c: flames(c, t, 110, 110), anim="pop")
    show(c, t, 141.0, 1740, 830, T("perigosa", 32, RED), anim="fade")
    show(c, t, 141.9, 960, 140, lambda c: hl(c, "1.701 barris", 0, 0, 58), anim="stamp")
    show(c, t, 143.9, 960, 230, T("de álcool industrial", 40, AMBER), anim="fade")
    if t > 146.2:
        typewrite(c, t, 146.2, "destino: Gênova, Itália", 960, 400, 48, INK)
    fog(c, t, 980, 0.05)


def s13(c, t):  # 147.80 - 156.43  partida de Nova York
    atl_map(c, ATL)
    map_point(c, ATL, *NY, AMBER, 10, t)
    map_label(c, ATL, -74, 43.1, "Nova York", 32)
    show(c, t, 148.2, 960, 120, lambda c: date_stamp(c, "7 DE NOVEMBRO DE 1872", 46, AMBER), anim="stamp")
    if t > 152.2:
        p = 0.55 * ease_io(prog(t, 152.2, 3.6))
        map_path(c, ATL, ROUTE, p, AMBER, 5, [16, 10])
        x, y = path_end(ATL, ROUTE, p)
        ship(c, t, x, y + 6, 0.13, rock=0.3)
    map_point(c, ATL, *GENOA, INK, 7, t, pulse=False)
    map_label(c, ATL, 8.9, 47.3, "Gênova", 30)
    map_path(c, ATL, ROUTE[-1:] + ROUTE_PLAN[1:], 1.0, (0.45, 0.45, 0.50), 2, [6, 10]) if t > 153.5 else None


def s14(c, t):  # 156.43 - 160.69  a última vez
    night(c, t, 640, 0.25, (360, 170))
    k = clamp01((t - 156.0) / 4.6)
    ship(c, t, 1000 + k * 520, 680 - k * 20, 0.6 - k * 0.3, alpha=1 - k * 0.85)
    show(c, t, 156.5, 960, 170, lambda c: stitle(c, "a última vez que alguém os viu", 0, 0, 54, INK, AMBER), anim="fade", d=0.9)
    fog(c, t, 700, 0.07 + 0.08 * k, 8)


# ------------------------------------------------------------------ bloco 2: a descoberta
def s15(c, t):  # B2 0 - 13.57  o Dei Gratia
    atl_map(c, ATL)
    map_path(c, ATL, ROUTE, 1.0, (0.55, 0.50, 0.40), 3, [8, 10])
    map_label(c, ATL, -45, 35.6, "Mary Celeste", 26, (0.7, 0.66, 0.56))
    map_point(c, ATL, *NY, AMBER, 9, t)
    map_label(c, ATL, -74, 43.1, "Nova York", 30)
    show(c, t, B2(0.1), 960, 110, lambda c: date_stamp(c, "8 DIAS DEPOIS", 46, AMBER), anim="stamp")
    if t > B2(4.6):
        p = 0.6 * ease_io(prog(t, B2(4.6), 7.0))
        map_path(c, ATL, ROUTE_DG, p, ICE, 5, [16, 10])
        x, y = path_end(ATL, ROUTE_DG, p)
        ship(c, t, x, y + 6, 0.13, rock=0.3)
        show(c, t, B2(4.9), *ATL(-48, 43.5), lambda c: caption_box(c, "Dei Gratia", 36), anim="up")
    show(c, t, B2(8.4), *ATL(-48, 46.5), T("cap. David Morehouse", 32, ICE), anim="fade")
    show(c, t, B2(10.0), *ATL(-30, 34.0), T("carga: petróleo", 30), anim="fade")
    if t > B2(11.1):
        map_point(c, ATL, *GIBRALTAR, ICE, 10, t)
        map_label(c, ATL, -5.35, 33.4, "Gibraltar", 30, ICE)


def s16(c, t):  # B2 13.57 - 29.42  avistam um veleiro à deriva
    night(c, t, 600, 0.35, (1620, 150))
    show(c, t, B2(13.7), 960, 110, lambda c: caption_box(c, "entre os Açores e a costa de Portugal", 40), anim="up")
    if t > B2(19.2):
        a = clamp01((t - B2(19.2)) / 1.2)
        k = t - B2(19.2)
        ship(c, t, 1300 + math.sin(k * 0.7) * 60, 640, 0.36, torn=0.8, alpha=a, tilt=math.sin(k * 1.3) * 0.05)
    deck(c, 940)
    line(c, 0, 900, W, 900, 8, (0.40, 0.30, 0.20))
    for x in range(40, W, 120):
        line(c, x, 900, x, 940, 6, (0.40, 0.30, 0.20))
    spy = lambda c, tt: (c.save(), c.rotate(-0.9), c.translate(60, 0), c.scale(0.55, 0.55), spyglass(c), c.restore()) if tt > B2(21.9) else None
    figure(c, t, 480, 1010, 0.95, poses=[(0, "stand"), (B2(21.9), "point_ru")], exprs=[(0, "neutral"), (B2(25.2), "worried")],
           fid=10, prop=("r", spy), shirt=(0.80, 0.78, 0.72), coat=(0.22, 0.26, 0.24), hat="pilot", hair=None)
    show(c, t, B2(21.1), 480, 420, T("cap. Morehouse", 32, ICE), anim="fade")
    show(c, t, B2(23.7), 1650, 330, group(sc(hourglass, t, s=0.55), at(0, 110, T("quase 2 horas", 30))), anim="pop")
    if t > B2(27.3):
        show(c, t, B2(27.3), 1650, 330, lambda c: (circle(c, 0, 0, 160, (0.08, 0.09, 0.11), 4), sc(ship_wheel, t, 1.4, s=0.95)(c)),
             anim="pop")
        show(c, t, B2(27.6), 1650, 530, T("ninguém no leme", 32, AMBER), anim="fade")
    fog(c, t, 760, 0.06)


def s17(c, t):  # B2 29.42 - 39.35  era o Mary Celeste
    atl_map(c, EAST, False)
    show(c, t, B2(30.9), 960, 130, lambda c: nameboard(c, "MARY CELESTE", 60), anim="stamp")
    map_point(c, EAST, *FOUND, RED, 11, t)
    map_label(c, EAST, -17.25, 36.3, "onde foi encontrado", 28, RED)
    map_point(c, EAST, *GENOA, INK, 8, t, pulse=False)
    map_label(c, EAST, 8.9, 46.0, "Gênova", 28)
    show(c, t, B2(33.4), 960, 900, lambda c: caption_box(c, "tinha saído 8 dias antes", 40), anim="up")
    if t > B2(36.9):
        p = ease_io(prog(t, B2(36.9), 1.4))
        map_path(c, EAST, [FOUND, (-8, 36.4), GIBRALTAR, (0, 37.5), (4.5, 40.6)], p, (0.6, 0.6, 0.65), 3, [8, 10])
        if p > 0.95:
            ship(c, t, *EAST(4.5, 40.4), 0.14, alpha=0.5, rock=0.3)
            map_label(c, EAST, 4.0, 38.6, "onde deveria estar", 28, (0.75, 0.75, 0.8))


def s18(c, t):  # B2 39.35 - 56.24  Deveau sobe a bordo
    night(c, t, 620, 0.35, None)
    ship(c, t, 1250, 760, 0.95, torn=0.8, rock=0.7)
    k = ease_io(prog(t, B2(40.5), 4.0))
    c.save(); c.translate(260 + k * 560, 900 + math.sin(t * 1.6) * 6); c.scale(0.8, 0.8); lifeboat(c, 3, True); c.restore()
    show(c, t, B2(40.7), 700, 790, T("Oliver Deveau, 1º imediato", 32, ICE), anim="fade", t1=B2(47.5))
    show(c, t, B2(44.6), 210, 230, sc(folder, "INQUÉRITO", s=0.8), anim="drop")
    if t > B2(47.9):
        cx, cy = 660, 300
        show(c, t, B2(47.9), cx, cy, lambda c: None, anim="fade")
        a = clamp01((t - B2(47.9)) / 0.5)
        def box(c):
            rrect(c, cx - 230, cy - 190, 460, 400, 14); fs(c, (0.08, 0.10, 0.13), 5)
            c.move_to(cx - 170, cy - 100); c.line_to(cx + 170, cy - 100); c.curve_to(cx + 160, cy + 80, cx + 80, cy + 150, cx, cy + 160)
            c.curve_to(cx - 80, cy + 150, cx - 160, cy + 80, cx - 170, cy - 100); c.close_path()
            fs(c, HULL, 6)
            lvl = clamp01((t - B2(49.8)) / 1.2)
            c.save()
            c.move_to(cx - 170, cy - 100); c.line_to(cx + 170, cy - 100); c.curve_to(cx + 160, cy + 80, cx + 80, cy + 150, cx, cy + 160)
            c.curve_to(cx - 80, cy + 150, cx - 160, cy + 80, cx - 170, cy - 100); c.close_path(); c.clip()
            wy = cy + 160 - 110 * lvl
            c.rectangle(cx - 200, wy, 400, 200); rgb(c, BLUE, 0.75); c.fill()
            c.restore()
            text(c, "porão", cx, cy - 150, 28, TYPE, INK)
            if lvl > 0.9:
                text(c, "~1 metro de água", cx, cy + 190, 30, TYPE, ICE)
        faded(c, a, box)
    show(c, t, B2(52.4), 980, 470, group(check_icon, at(0, 80, T("casco firme", 30, LGREEN))), anim="pop")
    fog(c, t, 860, 0.06)


def s19(c, t):  # B2 56.24 - 70.55  a bordo: bomba, vara, escotilhas, cozinha
    stars(c, t, 40, 260)
    deck(c, 300)
    show(c, t, B2(56.3), 960, 110, lambda c: stitle(c, "A bordo", 0, 0, 58, INK, AMBER), anim="up")
    items = [(B2(56.3), 560, 480, labeled(sc(pump, True, s=0.9), "bomba d'água desmontada", 150)),
             (B2(60.6), 1360, 480, labeled(sc(sounding_rod, s=0.9), "vara de sondagem largada", 110)),
             (B2(65.6), 560, 910, labeled(sc(hatch, True, s=0.6), "escotilhas abertas", 110)),
             (B2(67.7), 1360, 910, labeled(group(sc(stove, t, s=0.7), at(0, 40, lambda c: (rgb(c, BLUE, 0.4), c.rectangle(-110, 0, 220, 40), c.fill()))),
                                          "cozinha alagada", 110))]
    for t0, x, y, fn in items:
        show(c, t, t0, x, y, fn, anim="up")
    if t > B2(61.8):
        show(c, t, B2(61.8), 1360, 360, T("mede a água dentro do navio", 28, (0.75, 0.75, 0.8)), anim="fade")


def s20(c, t):  # B2 70.55 - 86.0  o que faltava
    stars(c, t, 60, 600)
    show(c, t, B2(70.6), 960, 110, lambda c: stitle(c, "O que faltava", 0, 0, 62, INK, AMBER), anim="up")
    missing = [(B2(73.8), 440, sc(lifeboat, s=0.9), "bote salva-vidas"),
               (B2(76.3), 820, sc(sextant, s=0.7), "sextante"),
               (B2(77.2), 1180, sc(chronometer, t, s=0.7), "cronômetro"),
               (B2(80.8), 1540, sc(folder, "PAPÉIS", False, s=0.7), "documentos")]
    for t0, x, fn, lab in missing:
        if t < t0:
            continue
        a = clamp01((t - t0) / 0.4)
        faded(c, 0.35 * a, lambda c, x=x, fn=fn: (c.save(), c.translate(x, 430), fn(c), c.restore()))
        c.save(); c.translate(x, 430); c.set_dash([12, 10]); rrect(c, -150, -150, 300, 300, 18)
        rgb(c, INK, 0.5 * a); c.set_line_width(3); c.stroke(); c.set_dash([]); c.restore()
        show(c, t, t0, x, 620, T(lab, 32), anim="fade")
        show(c, t, t0 + 0.3, x, 285, lambda c: date_stamp(c, "SUMIU", 34, RED), anim="stamp")
    if t > B2(83.2):
        glow(c, 960, 850, 260, AMBER, 0.25 * clamp01((t - B2(83.2)) / 0.6))
        show(c, t, B2(83.3), 960, 840, group(sc(book, "DIÁRIO", s=1.1), at(0, 150, T("só o diário de bordo ficou", 34, AMBER))), anim="up")


def s21(c, t):  # B2 86.0 - 94.63  a última anotação
    stars(c, t, 40, 260)
    glow(c, 960, 560, 700, AMBER, 0.10)
    c.save(); c.translate(960, 580); open_book(c); c.restore()
    show(c, t, B2(86.1), 960, 140, lambda c: stitle(c, "A última anotação", 0, 0, 56, INK, AMBER), anim="up")
    if t > B2(87.8):
        typewrite(c, t, B2(87.8), "25 de novembro de 1872", 700, 460, 40, DARKTXT, 18)
    if t > B2(89.4):
        typewrite(c, t, B2(89.4), "8h da manhã", 700, 560, 40, DARKTXT, 16)
    if t > B2(92.5):
        typewrite(c, t, B2(92.5), "perto da ilha", 1230, 460, 36, DARKTXT, 20)
        typewrite(c, t, B2(92.9), "de Santa Maria", 1230, 520, 36, DARKTXT, 20)
        typewrite(c, t, B2(93.4), "(Açores)", 1230, 580, 36, DARKTXT, 20)


def s22(c, t):  # B2 94.63 - 106.06  nove dias depois, 740 km
    draw_map(c, AZ, ATLANTIC, grid=2)
    azores(c, AZ)
    map_label(c, AZ, -28, 40.3, "AÇORES", 34, (0.6, 0.65, 0.72), SERIF)
    map_label(c, AZ, -8.0, 41.9, "PORTUGAL", 30, (0.6, 0.65, 0.72), SERIF)
    map_point(c, AZ, *LASTLOG, AMBER, 11, t)
    map_label(c, AZ, -25.02, 35.9, "25 nov: último registro", 28, AMBER)
    msgs = [(B2(94.7), "nenhum sinal de problema"), (B2(96.3), "nenhum pedido de socorro"), (B2(98.2), "nenhuma explicação")]
    for i, (t0, s) in enumerate(msgs):
        show(c, t, t0, 420, 850 + i * 75, lambda c, s=s: caption_box(c, s, 32), anim="left")
    if t > B2(101.6):
        map_point(c, AZ, *FOUND, RED, 11, t)
        map_label(c, AZ, -17.25, 39.4, "4 dez: encontrado", 28, RED)
    if t > B2(103.2):
        p = ease_io(prog(t, B2(103.2), 1.2))
        map_path(c, AZ, [LASTLOG, FOUND], p, INK, 4, [10, 10])
        show(c, t, B2(103.6), *AZ(-21.1, 38.1), lambda c: hl(c, "~740 km", 0, 0, 40), anim="stamp")
    show(c, t, B2(101.7), 1500, 860, lambda c: caption_box(c, "9 dias depois", 38), anim="up")


def s23(c, t):  # B2 106.06 - 117.92  rebocado a Gibraltar; recompensa
    draw_map(c, GIB, ATLANTIC, grid=5)
    azores(c, GIB)
    map_point(c, GIB, *FOUND, RED, 9, t, pulse=False)
    p = ease_io(prog(t, B2(106.1), 3.2))
    pts = [FOUND, (-12, 36.6), (-8, 36.0), GIBRALTAR]
    map_path(c, GIB, pts, p, ICE, 5, [14, 10])
    x, y = path_end(GIB, pts, p)
    ship(c, t, x - 30, y + 6, 0.12, rock=0.3)
    ship(c, t, x + 30, y + 6, 0.12, rock=0.3, torn=0.6)
    if t > B2(109.2):
        map_point(c, GIB, *GIBRALTAR, ICE, 10, t)
        map_label(c, GIB, -5.35, 34.4, "Gibraltar", 32, ICE)
    show(c, t, B2(110.1), 960, 140, lambda c: caption_box(c, "lei do mar: quem resgata tem direito a recompensa", 38), anim="up")
    show(c, t, B2(113.7), 560, 780, group(at(-50, 0, coin), at(40, 20, coin), at(0, -40, coin)), anim="pop")
    if t > B2(114.6):
        a = clamp01((t - B2(114.6)) / 0.5)
        c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.78 * a); c.fill()
        show(c, t, B2(114.7), 960, 540, lambda c: chapter(c, "PARTE 2", "O INQUÉRITO"), anim="fade", d=0.7)


def s24(c, t):  # B2 117.92 - 132.70  Solly-Flood e a tese do crime
    stars(c, t, 40, 300)
    c.rectangle(0, 720, W, H - 720); rgb(c, (0.12, 0.10, 0.09)); c.fill()
    for x in (200, 1720):
        c.save(); c.translate(x, 700); column(c, 560); c.restore()
    figure(c, t, 620, 1010, 0.95, poses=[(0, "stand"), (B2(122.9), "finger_up"), (B2(126.3), "point_r")],
           exprs=[(0, "neutral"), (B2(122.9), "angry")], appear=B2(118.0), fid=13, shirt=(0.85, 0.84, 0.80),
           coat=(0.16, 0.16, 0.18), hat="tophat", hair=None, mustache=True, glasses=True)
    show(c, t, B2(119.5), 620, 160, lambda c: hl(c, "Frederick Solly-Flood", 0, 0, 44), anim="up")
    show(c, t, B2(121.0), 620, 250, T("procurador-geral de Gibraltar", 32), anim="fade")
    show(c, t, B2(125.4), 1350, 200, lambda c: date_stamp(c, "CRIME?", 64, RED), anim="stamp")
    cards = [(B2(127.8), 1060, "bebedeira", bottle), (B2(129.4), 1350, "assassinato", lambda c: text(c, "?", 0, 0, 110, SERIF, RED)),
             (B2(131.3), 1640, "fuga no bote", sc(lifeboat, s=0.6))]
    for t0, x, lab, fn in cards:
        show(c, t, t0, x, 560, lambda c, lab=lab, fn=fn: card(c, lab, fn, None, 260, 300) if False else
             (rrect(c, -135, -150, 270, 300, 12), fs(c, (0.13, 0.13, 0.15), 4, PARCH2), text(c, lab, 0, -110, 32, TYPE, AMBER),
              c.save(), c.translate(0, 30), fn(c), c.restore()), anim="drop")
        if t0 > B2(127) and t > t0:
            pass
    if t > B2(128.1):
        for i in range(2):
            x0 = 1060 + i * 290
            arrow_draw(c, t, B2(129.0) + i * 1.8, x0 + 140, 560, x0 + 150, 560)


def s25(c, t):  # B2 132.70 - 147.63  as provas caem
    stars(c, t, 40, 300)
    show(c, t, B2(134.2), 1050, 330, sc(sword, True, s=1.4), anim="left")
    show(c, t, B2(134.4), 1050, 220, T("manchas na espada", 32), anim="fade")
    if t > B2(136.2):
        show(c, t, B2(136.2), 1050, 620, lambda c: (rrect(c, -260, -60, 520, 120, 10), fs(c, HULL, 5),
                                                    [line(c, -150 + k * 60, -30, -120 + k * 60, 30, 4, (0.65, 0.55, 0.40)) for k in range(5)]),
             anim="up")
        show(c, t, B2(136.4), 1050, 720, T("marcas no casco", 32), anim="fade")
    if t > B2(138.4):
        k = ease_io(prog(t, B2(138.4), 1.6))
        c.save(); c.translate(1500 - 300 * k, 260 + 60 * k); c.rotate(0.5); magnifier(c); c.restore()
    show(c, t, B2(140.8), 1050, 480, lambda c: date_stamp(c, "NÃO ERA SANGUE", 50, LGREEN), anim="stamp")
    show(c, t, B2(142.1), 1620, 820, group(sc(barrel, label="ÁLCOOL", s=0.85), at(0, 140, T("impossível de beber", 30, AMBER))), anim="up")
    figure(c, t, 380, 1010, 0.9, poses=[(0, "point_r"), (B2(140.8), "shrug")], exprs=[(0, "angry"), (B2(140.8), "worried")],
           fid=13, shirt=(0.85, 0.84, 0.80), coat=(0.16, 0.16, 0.18), hat="tophat", hair=None, mustache=True, glasses=True)


def s26(c, t):  # B2 147.63 - 159.62  o tribunal
    stars(c, t, 40, 300)
    show(c, t, B2(147.7), 620, 520, sc(gavel, s=1.1), anim="drop")
    show(c, t, B2(148.1), 1000, 260, sc(calendar, "3", RED, s=0.9), anim="pop")
    show(c, t, B2(148.3), 1000, 400, T("meses de julgamento", 32), anim="fade")
    show(c, t, B2(150.4), 860, 730, lambda c: date_stamp(c, "NENHUM CRIME", 56, LGREEN), anim="stamp")
    if t > B2(152.9):
        n = 6 if t < B2(154.9) else max(2, 6 - int((t - B2(154.9)) * 6))
        for i in range(n):
            c.save(); c.translate(1500 + (i % 3) * 70 - 70, 620 - (i // 3) * 60); coin(c); c.restore()
        show(c, t, B2(153.3), 1500, 420, T("recompensa", 36, AMBER), anim="fade")
        show(c, t, B2(155.0), 1500, 760, T("bem menor do que esperavam", 30), anim="fade")
    if t > B2(156.3):
        show(c, t, B2(156.3), 1500, 250, sc(qmark, 120, (0.6, 0.6, 0.66)), anim="fade", d=1.0)
        show(c, t, B2(156.6), 1500, 900, T("uma suspeita no ar", 32, (0.7, 0.7, 0.75)), anim="fade")


def s27(c, t):  # B2 159.62 - 176.51  Arthur Conan Doyle
    stars(c, t, 60, 400)
    show(c, t, B2(159.7), 960, 120, lambda c: stitle(c, "Um personagem inesperado", 0, 0, 56, INK, AMBER), anim="up")
    show(c, t, B2(162.7), 1450, 250, lambda c: date_stamp(c, "1884", 56, AMBER), anim="stamp")
    figure(c, t, 640, 1010, 1.0, poses=[(0, "stand"), (B2(166.6), "present"), (B2(173.4), "point_r")],
           exprs=[(0, "neutral"), (B2(169.3), "grin")], appear=B2(164.5), fid=14, shirt=(0.85, 0.84, 0.80),
           coat=(0.36, 0.36, 0.40), hair="tuft", mustache=True)
    show(c, t, B2(164.6), 640, 330, T("um jovem médico escocês", 32), anim="fade")
    show(c, t, B2(166.6), 1450, 500, group(sc(book, "CONTO", PURPLE, s=1.2), at(0, 165, T("(ficção, 1884)", 28))), anim="up")
    show(c, t, B2(169.3), 640, 240, lambda c: hl(c, "Arthur Conan Doyle", 0, 0, 46), anim="up")
    show(c, t, B2(171.9), 640, 420, T("futuro criador de Sherlock Holmes", 30, AMBER), anim="fade")
    if t > B2(173.4):
        show(c, t, B2(173.4), 1450, 820, lambda c: nameboard(c, "MARIE CELESTE", 48), anim="stamp")
        show(c, t, B2(175.3), 1450, 920, T("o nome trocado no conto", 30, (0.75, 0.75, 0.8)), anim="fade")


def s28(c, t):  # B2 176.51 - B3 0  detalhes inventados
    stars(c, t, 50, 300)
    show(c, t, B2(176.6), 1100, 120, lambda c: stitle(c, "Detalhes que nunca existiram", 0, 0, 54, INK, AMBER), anim="up")
    myths = [(B2(179.8), 760, labeled(sc(teacup, t, s=0.9), "chá ainda morno", 140)),
             (B2(182.3), 1160, labeled(sc(stove, t, s=0.9), "comida no fogão", 150)),
             (B2(183.6), 1560, labeled(sc(lifeboat, s=0.75), "o bote a bordo", 110))]
    for i, (t0, x, fn) in enumerate(myths):
        show(c, t, t0, x, 480, fn, anim="up")
        show(c, t, B2(186.4) + i * 0.25, x, 330, lambda c: date_stamp(c, "FICÇÃO", 46, RED), anim="stamp")
    show(c, t, B2(189.0), 1160, 860, lambda c: caption_box(c, "boa parte da lenda vem de um conto", 40), anim="up")
    HIST(c, t, [(0, "stand"), (B2(179.8), "present"), (B2(186.4), "shrug")], [(0, "neutral"), (B2(186.4), "worried")], x=290)
    fog(c, t, 1000, 0.05)


# ------------------------------------------------------------------ bloco 3: as teorias
def s29(c, t):  # B3 0 - 5.02  o que aconteceu?
    night(c, t, 760, 0.2, (1600, 150))
    show(c, t, B3(0.2), 1150, 400, sc(big_q, 300), anim="fade", d=0.8)
    show(c, t, B3(1.1), 1150, 700, T("o que aconteceu de verdade?", 44), anim="fade")
    HIST(c, t, [(0, "think")], [(0, "think")])
    fog(c, t, 860, 0.07)


def s30(c, t):  # B3 5.02 - 29.87  piratas, motim, fraude
    stars(c, t, 50, 300)
    show(c, t, B3(5.1), 1180, 110, lambda c: stitle(c, "As primeiras teorias", 0, 0, 56, INK, AMBER), anim="up")
    two_caps = lambda c: (c.save(), c.translate(-60, 40), pilot_cap(c, 0), c.restore(), c.save(), c.translate(60, 40), pilot_cap(c, 0),
                          c.restore(), circle(c, 0, -70, 30, AMBER, 5))
    cards = [(B3(6.5), 760, "PIRATAS", sc(skull_flag, s=0.7), "carga intacta", B3(11.7)),
             (B3(14.9), 1180, "MOTIM", lambda c: (fig(c, t, -50, 120, 0.42, [(0, "arms_up")], [(0, "angry")], fid=40, **SAILOR),
                                                fig(c, t, 50, 120, 0.42, [(0, "arms_up")], [(0, "angry")], fid=41, **SAILOR)),
              "sem sinal de luta", B3(16.4)),
             (B3(21.8), 1600, "FRAUDE", two_caps, "nenhuma prova", B3(26.6))]
    for t0, x, ttl, icon, note, tx in cards:
        show(c, t, t0, x, 560, lambda c, ttl=ttl, icon=icon: card(c, ttl, icon), anim="up")
        if t > tx:
            x_over(c, t, tx, x, 540, 120)
            show(c, t, tx + 0.2, x, 830, T(note, 30, RED), anim="fade")
    HIST(c, t, [(0, "present"), (B3(11.7), "shrug"), (B3(21.8), "think"), (B3(26.6), "shrug")], [(0, "neutral"), (B3(21.8), "think")],
         x=260, s=0.85)


def s31(c, t):  # B3 29.87 - 51.84  tromba d'água, terremoto
    night(c, t, 640, 0.6, None)
    shake = math.sin(t * 40) * 10 if B3(47.6) < t < B3(50.5) else 0
    if B3(36.5) < t < B3(47.0):
        a = clamp01((t - B3(36.5)) / 1.0) * (1 - clamp01((t - B3(46.0)) / 1.0))
        faded(c, a, lambda c: (c.save(), c.translate(1550, 660), waterspout(c, t, 600), c.restore()))
    ship(c, t, 1050 + shake, 720, 0.75, rock=1.6)
    show(c, t, B3(30.0), 960, 110, lambda c: caption_box(c, "por que abandonar um navio que não afundava?", 40), anim="up")
    show(c, t, B3(36.6), 1550, 220, T("tromba d'água", 40, AMBER), anim="fade", t1=B3(46.6))
    if t > B3(42.4):
        def inset(c):
            rrect(c, -170, -200, 340, 400, 14); fs(c, (0.08, 0.10, 0.13), 5)
            pump(c, False)
            lvl = clamp01((t - B3(42.6)) / 2)
            c.rectangle(-22, 60 - 170 * lvl, 44, 170 * lvl); rgb(c, BLUE, 0.7); c.fill()
            text(c, "a água sobe", 0, 175, 28, TYPE, ICE)
        show(c, t, B3(42.4), 320, 520, inset, anim="pop", t1=B3(46.6))
    if t > B3(47.0):
        c.save(); c.translate(960 + shake, 1180); seabed(c, t, 0, seed=8, col=(0.10, 0.12, 0.15)); c.restore()
        show(c, t, B3(47.6), 400, 300, lambda c: caption_box(c, "terremoto no fundo do mar", 38), anim="up")
    fog(c, t, 820, 0.05)


def s32(c, t):  # B3 51.84 - 75.99  a carga e o vapor de álcool
    stars(c, t, 40, 260)
    show(c, t, B3(52.0), 1150, 110, lambda c: stitle(c, "A teoria da carga", 0, 0, 58, INK, AMBER), anim="up")
    rrect(c, 640, 320, 1100, 560, 16); fs(c, (0.12, 0.10, 0.09), 6, (0.40, 0.30, 0.20))
    empty = {0, 2, 3, 5, 6, 8, 9, 10, 11}
    for i in range(12):
        x = 760 + (i % 6) * 172
        y = 500 + (i // 6) * 220
        e = i in empty and t > B3(57.3)
        c.save(); c.translate(x, y); c.scale(0.75, 0.75); barrel(c, empty=e); c.restore()
        if e and t < B3(66.0):
            glow(c, x, y, 70, AMBER, 0.15)
    show(c, t, B3(57.4), 1190, 950, lambda c: hl(c, "9 barris vazios", 0, 0, 44), anim="stamp")
    show(c, t, B3(59.4), 1190, 255, T("carvalho vermelho: madeira mais porosa", 32, AMBER), anim="fade", t1=B3(62.4))
    if t > B3(62.6):
        vapor(c, t, 1190, 640, 7, 0.30 * clamp01((t - B3(62.6)) / 1.5))
        show(c, t, B3(63.0), 1190, 255, T("vapor de álcool", 36, LGREEN), anim="fade")
    if B3(69.1) < t < B3(70.6):
        k = (t - B3(69.1)) / 1.5
        glow(c, 1190, 600, 400 + 300 * k, ICE, 0.45 * (1 - k))
        glow(c, 1190, 600, 200, LYELLOW, 0.4 * (1 - k))
    show(c, t, B3(66.3), 1600, 760, T("um estalo?", 32), anim="fade", t1=B3(71.5))
    show(c, t, B3(72.3), 1190, 255, lambda c: caption_box(c, "sair dali o mais rápido possível", 36), anim="up")
    HIST(c, t, [(0, "present"), (B3(57.3), "point_r"), (B3(69.2), "head"), (B3(71.0), "think")],
         [(0, "neutral"), (B3(69.2), "shocked"), (B3(71.0), "worried")], x=300, s=0.9)


def s33(c, t):  # B3 75.99 - 98.96  o experimento de 2006
    stars(c, t, 40, 300)
    show(c, t, B3(76.0), 1500, 120, lambda c: date_stamp(c, "2006", 56, AMBER), anim="stamp")
    show(c, t, B3(77.8), 1000, 120, T("University College de Londres", 36), anim="fade")
    figure(c, t, 520, 1010, 0.95, poses=[(0, "stand"), (B3(81.9), "present"), (B3(87.3), "head"), (B3(90.2), "thumb")],
           exprs=[(0, "neutral"), (B3(87.3), "shocked"), (B3(90.2), "confident")], appear=B3(79.6), fid=15,
           shirt=(0.30, 0.42, 0.56), coat=(0.88, 0.88, 0.86), glasses=True, hair="tuft")
    show(c, t, B3(79.7), 520, 330, lambda c: hl(c, "Andrea Sella, químico", 0, 0, 38), anim="up")
    bx, by = 1250, 620
    show(c, t, B3(82.0), bx, by, lambda c: (rrect(c, -330, -200, 660, 400, 10), fs(c, (0.30, 0.22, 0.15), 6),
                                            c.rectangle(-300, -170, 600, 340), fs(c, (0.06, 0.06, 0.07), 3)), anim="pop")
    show(c, t, B3(82.3), bx, by + 250, T("réplica do porão", 30), anim="fade")
    if t > B3(83.7):
        vapor(c, t, bx, by + 120, 5, 0.25 * (1 - clamp01((t - B3(86.6)) / 0.8)))
    if B3(86.6) < t < B3(90.0):
        k = (t - B3(86.6)) / 3.4
        x = bx - 280 + 560 * min(1, k * 1.6)
        g = cairo.LinearGradient(x - 200, 0, x, 0)
        g.add_color_stop_rgba(0, 0.4, 0.6, 1.0, 0)
        g.add_color_stop_rgba(1, 0.5, 0.75, 1.0, 0.7 * (1 - k))
        c.rectangle(bx - 300, by - 170, x - (bx - 300), 340); c.set_source(g); c.fill()
        glow(c, x, by, 220, ICE, 0.5 * (1 - k))
    show(c, t, B3(87.4), bx, 330, T("onda de chamas...", 36, ICE), anim="fade")
    show(c, t, B3(89.4), bx + 220, 330, T("fria", 40, ICE), anim="pop")
    show(c, t, B3(90.2), 1700, 470, group(check_icon, at(0, 70, T("sem fuligem", 28))), anim="pop")
    show(c, t, B3(91.6), 1700, 680, group(check_icon, at(0, 70, T("nada queimado", 28))), anim="pop")
    show(c, t, B3(93.1), bx, 960, lambda c: caption_box(c, "susto sem deixar marcas", 38), anim="up")


def s34(c, t):  # B3 98.96 - 116.38  Anne MacGregor
    stars(c, t, 40, 300)
    figure(c, t, 470, 1010, 0.95, poses=[(0, "stand"), (B3(104.9), "present"), (B3(110.6), "point_r")],
           exprs=[(0, "neutral"), (B3(104.9), "think")], appear=B3(100.6), fid=16, shirt=(0.30, 0.42, 0.56), hair="long")
    show(c, t, B3(100.7), 470, 330, lambda c: hl(c, "Anne MacGregor", 0, 0, 40), anim="up")
    show(c, t, B3(102.0), 470, 410, T("reconstruiu a viagem", 30), anim="fade")
    show(c, t, B3(104.4), 1250, 110, lambda c: stitle(c, "Um conjunto de problemas", 0, 0, 52, INK, AMBER), anim="up")
    items = [(B3(105.3), 940, labeled(sc(chronometer, t, True, s=0.8), "cronômetro errado?", 150, 30)),
             (B3(110.7), 1340, labeled(sc(coal, s=1.1), "resto de carvão", 150, 30)),
             (B3(114.5), 1740, labeled(sc(pump, False, s=0.7), "bombas entupidas?", 150, 30))]
    for t0, x, fn in items:
        show(c, t, t0, x, 560, fn, anim="up")
    if t > B3(108.0):
        show(c, t, B3(108.0), 960, 860, T("achava estar longe das ilhas", 28, (0.75, 0.75, 0.8)), anim="fade")
    if t > B3(113.5):
        for i in range(10):
            ph = (t * 0.5 + i / 10) % 1
            circle(c, 1340 + (i - 5) * 30 + math.sin(t + i) * 20, 520 - ph * 160, 4, None, 2, (0.5, 0.5, 0.55))
        arrow_draw(c, t, B3(114.3), 1450, 520, 1630, 520)


def s35(c, t):  # B3 116.38 - 128.31  terra à vista: Santa Maria
    draw_map(c, SM, [], grid=1)
    azores(c, SM, only=("Santa Maria", "São Miguel"))
    sea_lines = lambda: None
    for i in range(14):
        x = (i * 160 + t * 30) % (W + 160) - 80
        for j in range(6):
            y = 160 + j * 170 + (i % 2) * 60
            c.move_to(x, y); c.curve_to(x + 30, y - 14, x + 60, y - 14, x + 90, y)
    rgb(c, BLUE, 0.6); c.set_line_width(3); c.stroke()
    shipxy = SM(-24.65, 37.45)
    ship(c, t, shipxy[0], shipxy[1], 0.22, rock=1.5)
    show(c, t, B3(116.5), 960, 110, lambda c: caption_box(c, "mar agitado", 38), anim="up", t1=B3(119.6))
    show(c, t, B3(117.6), shipxy[0] + 180, shipxy[1] - 120, T("água no porão: ?", 30, AMBER), anim="fade")
    if t > B3(119.8):
        x, y = SM(-25.1, 36.97)
        glow(c, x, y, 160, AMBER, 0.2)
        show(c, t, B3(119.9), x, y + 90, T("Santa Maria", 34, AMBER), anim="fade")
        show(c, t, B3(120.2), 960, 110, lambda c: caption_box(c, "terra à vista", 38), anim="up")
    map_label(c, SM, -25.5, 37.55, "São Miguel", 26, (0.7, 0.7, 0.75))
    if t > B3(124.6):
        p = ease_io(prog(t, B3(124.6), 3.2))
        x0, y0 = shipxy[0] - 60, shipxy[1] + 40
        x1, y1 = SM(-24.95, 37.06)
        c.set_dash([10, 10]); line(c, x0, y0, x0 + (x1 - x0) * p, y0 + (y1 - y0) * p, 3, INK); c.set_dash([])
        c.save(); c.translate(x0 + (x1 - x0) * p, y0 + (y1 - y0) * p); c.scale(0.3, 0.3); lifeboat(c, 4); c.restore()


def s36(c, t):  # B3 128.31 - 143.96  a corda se rompe
    night(c, t, 600, 0.45, (1650, 150))
    snap = B3(134.96)
    if t < snap:
        sx = 1150 + (t - B3(128.3)) * 6
    else:
        sx = 1150 + (snap - B3(128.3)) * 6 + (t - snap) ** 1.6 * 55
    ss = 0.7
    ship(c, t, sx, 700, ss, rock=0.8)
    bx = 520 + (min(t, snap) - B3(128.3)) * 6
    by = 760 + math.sin(t * 1.5) * 8
    c.save(); c.translate(bx, by); c.scale(0.7, 0.7); lifeboat(c, 6); c.restore()
    if t > B3(139.0):
        # dez cabeças no bote
        pass
    stern = (sx - 238 * ss, 700 - 40 * ss)
    bow = (bx + 95, by - 18)
    if t < snap:
        c.move_to(*stern); c.curve_to(stern[0] - 120, stern[1] + 80, bow[0] + 140, bow[1] + 30, *bow)
        rgb(c, (0.75, 0.70, 0.58)); c.set_line_width(4); c.stroke()
    else:
        k = clamp01((t - snap) / 0.8)
        mid = ((stern[0] + bow[0]) / 2, (stern[1] + bow[1]) / 2 + 60)
        c.move_to(*stern); c.line_to(stern[0] - 120, stern[1] + 60 + 80 * k)
        c.move_to(*bow); c.line_to(bow[0] + 120, bow[1] + 50 + 60 * k)
        rgb(c, (0.75, 0.70, 0.58)); c.set_line_width(4); c.stroke()
    show(c, t, B3(128.4), 960, 110, lambda c: caption_box(c, "o bote preso ao navio por uma corda", 38), anim="up", t1=B3(134.6))
    show(c, t, snap, 960, 110, lambda c: stitle(c, "a corda se rompeu", 0, 0, 58, RED, BLOOD), anim="stamp")
    show(c, t, B3(139.1), 960, 980, lambda c: caption_box(c, "10 pessoas num bote, no meio do Atlântico", 38), anim="up")
    fog(c, t, 760, 0.05 + 0.08 * clamp01((t - B3(139)) / 3), 8)


def s37(c, t):  # B3 143.96 - 169.38  o fim do navio
    night(c, t, 680, 0.25, None)
    if t < B3(151.8):
        ship(c, t, 1150, 760, 0.7)
        show(c, t, B3(146.8), 1150, 200, lambda c: caption_box(c, "mais 12 anos navegando", 40), anim="up")
        show(c, t, B3(149.2), 1150, 310, lambda c: hl(c, "navio amaldiçoado", 0, 0, 44), anim="stamp")
        HIST(c, t, [(0, "present")], [(0, "neutral"), (B3(149.2), "worried")])
    else:
        show(c, t, B3(151.9), 960, 110, lambda c: date_stamp(c, "HAITI, 1885", 54, AMBER), anim="stamp")
        crash = B3(157.9)
        k = ease_out(prog(t, crash, 1.0))
        tilt = -0.18 * k
        c.save(); c.translate(1300, 800); reef(c, t, 820); c.restore()
        ship(c, t, 1000 + 300 * k, 760 + 20 * k, 0.62, torn=0.3 * k, rock=1 - k, tilt=tilt)
        figure(c, t, 380, 1010, 0.9, poses=[(0, "stand"), (B3(157.9), "point_r"), (B3(162.0), "shrug")],
               exprs=[(0, "neutral"), (B3(157.9), "grin"), (B3(162.0), "worried")], appear=B3(154.9), fid=17, **CAPTAIN)
        show(c, t, B3(155.0), 380, 400, lambda c: hl(c, "Gilman Parker", 0, 0, 40), anim="up")
        show(c, t, B3(156.2), 380, 480, T("o último capitão", 30), anim="fade")
        show(c, t, B3(158.4), 1300, 940, T("recife, de propósito", 32, AMBER), anim="fade")
        show(c, t, B3(160.9), 1600, 330, sc(document, "SEGURO", s=0.9) if False else sc(folder, "SEGURO", False, s=0.8), anim="drop")
        show(c, t, B3(162.0), 1600, 340, lambda c: date_stamp(c, "FRAUDE", 54, RED), anim="stamp")
    fog(c, t, 900, 0.05)


def s38(c, t):  # B3 169.38 - 183.31  os destroços de 2001
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.04, 0.08, 0.13); g.add_color_stop_rgb(1, 0.01, 0.02, 0.04)
    c.rectangle(0, 0, W, H); c.set_source(g); c.fill()
    sea(c, t, 260, 0.2)
    c.save(); c.translate(760, 250); sonar_ship(c, t); c.restore()
    sonar_beam(c, t, 760, 290, 620)
    c.save(); c.translate(960, 1160); seabed(c, t, 0, seed=12, col=(0.10, 0.12, 0.15)); c.restore()
    for i in range(6):
        c.save(); c.translate(620 + i * 55, 960 - (i % 2) * 18); c.rotate(0.3 + i * 0.4)
        rrect(c, -40, -8, 80, 16, 4); fs(c, HULL, 3); c.restore()
    show(c, t, B3(169.4), 1500, 110, lambda c: date_stamp(c, "2001", 54, AMBER), anim="stamp")
    show(c, t, B3(171.0), 760, 790, T("destroços encontrados?", 32, AMBER), anim="fade")
    show(c, t, B3(173.5), 1480, 540, sc(tree_rings, s=1.0), anim="pop")
    show(c, t, B3(174.4), 1480, 740, T("análise da madeira", 32), anim="fade")
    show(c, t, B3(175.6), 1480, 800, T("árvores vivas anos depois de 1885", 28, AMBER), anim="fade")
    if t > B3(179.2):
        x_over(c, t, B3(179.2), 760, 950, 120)
        show(c, t, B3(179.5), 960, 400, lambda c: caption_box(c, "não era o Mary Celeste", 42), anim="up")


def s39(c, t):  # B3 183.31 - 195.23  ninguém voltou
    night(c, t, 700, 0.15, (1600, 160))
    show(c, t, B3(183.4), 960, 150, lambda c: stitle(c, "O bote nunca apareceu", 0, 0, 58, INK, AMBER), anim="fade", d=0.8)
    if t > B3(190.5):
        a = clamp01((t - B3(190.5)) / 1.4) * 0.75
        fig(c, t, 760, 1000, 0.85, exprs=[(0, "neutral")], alpha=a, fid=7, **CAPTAIN)
        fig(c, t, 960, 1000, 0.8, exprs=[(0, "neutral")], alpha=a, fid=8, shirt=(0.48, 0.26, 0.36), hair="long")
        fig(c, t, 1110, 1000, 0.46, exprs=[(0, "neutral")], alpha=a, fid=9, shirt=PINK, hair="long")
        glow(c, 940, 760, 360, ICE, 0.08 * a)
        show(c, t, B3(190.7), 1480, 520, lambda c: (scroll(c, 0, 380, 230),
                                                   text(c, "Benjamin", 0, -55, 38, SERIF, DARKTXT),
                                                   text(c, "Sarah", 0, 0, 38, SERIF, DARKTXT),
                                                   text(c, "Sophia", 0, 55, 38, SERIF, DARKTXT)), anim="fade", d=0.8)
        show(c, t, B3(193.0), 1480, 720, T("nunca chegaram à Itália", 32, AMBER), anim="fade")
    else:
        show(c, t, B3(185.2), 960, 330, T("nenhum corpo", 38), anim="fade")
        show(c, t, B3(187.0), 960, 400, T("nenhuma testemunha", 38), anim="fade")
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=280, s=0.9)
    fog(c, t, 900, 0.08, 7)


def s40(c, t):  # B3 195.23 - fim
    stars(c, t, 80, 700)
    k = clamp01((t - B3(195.2)) / 2)
    ship(c, t, 1740, 900, 0.42, torn=0.8, alpha=0.35 * k)
    HIST(c, t, [(0, "stand"), (B3(195.3), "point_r"), (B3(201.2), "present"), (B3(203.5), "wave"), (B3(206.5), "stand")],
         [(0, "think"), (B3(201.2), "happy")], x=380, s=1.05)
    show(c, t, B3(195.3), 1150, 190, lambda c: stitle(c, "E você?", 0, 0, 70, INK, AMBER), anim="up")
    show(c, t, B3(196.3), 1150, 320, T("por que abandonar um navio que ainda flutuava?", 38), anim="fade")
    show(c, t, B3(201.2), 1150, 500, lambda c: (speech(c, 720, 150, -260, 140), text(c, "deixe sua teoria nos comentários", 0, 0, 40, HAND, INK)))
    show(c, t, B3(203.6), 1150, 720, sc(subscribe_btn, t > B3(205.0), s=0.9))
    show(c, t, B3(204.0), 1480, 720, sc(bell, s=0.8), rot=math.sin(t * 18) * 0.2 * max(0, 1 - (t - B3(204.0))))
    show(c, t, B3(205.5), 1150, 920, lambda c: (text(c, "PONTO CEGO", 0, 0, 80, SERIF, INK), line(c, -300, 55, 300, 55, 3, AMBER)),
         anim="fade", d=1.2)
    fog(c, t, 1000, 0.07)


SCENES = [
    (0.0, 18.78, s01), (18.78, 33.04, s02), (33.04, 46.24, s03), (46.24, 49.72, s04), (49.72, 59.64, s05),
    (59.64, 68.55, s06), (68.55, 81.98, s07), (81.98, 88.48, s08), (88.48, 107.75, s09), (107.75, 119.91, s10),
    (119.91, 138.95, s11), (138.95, 147.80, s12), (147.80, 156.43, s13), (156.43, B2(0.0), s14),
    (B2(0.0), B2(13.57), s15), (B2(13.57), B2(29.42), s16), (B2(29.42), B2(39.35), s17), (B2(39.35), B2(56.24), s18),
    (B2(56.24), B2(70.55), s19), (B2(70.55), B2(86.0), s20), (B2(86.0), B2(94.63), s21), (B2(94.63), B2(106.06), s22),
    (B2(106.06), B2(117.92), s23), (B2(117.92), B2(132.70), s24), (B2(132.70), B2(147.63), s25), (B2(147.63), B2(159.62), s26),
    (B2(159.62), B2(176.51), s27), (B2(176.51), B3(0.0), s28),
    (B3(0.0), B3(5.02), s29), (B3(5.02), B3(29.87), s30), (B3(29.87), B3(51.84), s31), (B3(51.84), B3(75.99), s32),
    (B3(75.99), B3(98.96), s33), (B3(98.96), B3(116.38), s34), (B3(116.38), B3(128.31), s35), (B3(128.31), B3(143.96), s36),
    (B3(143.96), B3(169.38), s37), (B3(169.38), B3(183.31), s38), (B3(183.31), B3(195.23), s39), (B3(195.23), 999.0, s40),
]

# Sons: nada automático (sem whoosh em transição, sem som em cada ícone). Só alguns toques sem chiado nos momentos-chave.
SFX_OFF = True
SFX = [(8.7, "bell"), (29.7, "heartbeat"), (46.3, "boom"), (156.5, "tum"), (B2(30.9), "tum"), (B2(86.0), "tum"),
       (B2(125.4), "tum"), (B2(150.4), "tum"), (B3(69.1), "boom"), (B3(134.96), "tum"), (B3(139.3), "bell"),
       (B3(162.0), "tum"), (B3(190.6), "heartbeat"), (B3(205.5), "boom")]
