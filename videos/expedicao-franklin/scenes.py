"""A Expedição Franklin (1845) — Ponto Cego.
Narração: Pedro Lima - Serious (HeyGen / ElevenLabs v4), 5 blocos com 1 s de silêncio entre eles (~834,5 s).
Tempos: videos/expedicao-franklin/narracao_blocos.txt. B2(x)..B5(x) convertem o tempo local do bloco em tempo absoluto
(bloco 1 já está em tempo absoluto).
"""
from engine import *

THEME = "neve"

O2, O3, O4, O5 = 188.847, 372.234, 575.552, 712.911


def B2(x):
    return x + O2


def B3(x):
    return x + O3


def B4(x):
    return x + O4


def B5(x):
    return x + O5


# ------------------------------------------------------------------ mapas
NATL = make_proj(-100, 5, 50, 80, coslat=True, box=(120, 90, 1800, 1030))      # Inglaterra -> Ártico
NWP = make_proj(-122, -58, 64, 79, coslat=True, box=(120, 90, 1800, 1030))     # Passagem do Noroeste
KW = make_proj(-103.5, -92.5, 67.0, 71.2, coslat=True, box=(120, 80, 1800, 1040))  # Ilha do Rei Guilherme

GREENHITHE = (0.3, 51.45)
DISKO = (-53.5, 69.2)
BAFFIN_LAST = (-66.2, 74.8)
BEECHEY = (-91.85, 74.72)
BESET = (-98.4, 70.05)
VICTORY = (-98.75, 69.62)
EREBUS_BAY = (-99.4, 69.0)
EREBUS_WRECK = (-99.0, 68.2)
TERROR_WRECK = (-99.3, 68.88)
BACK_RIVER = (-96.0, 67.35)
PELLY = (-89.8, 68.6)

ROUTE_OUT = [GREENHITHE, (-1.5, 57.5), (-3.0, 59.2), (-20, 60.0), (-35, 59.4), (-44.5, 59.3), (-50.5, 62.0), (-53.5, 65.5),
             DISKO, (-58.0, 72.0), BAFFIN_LAST, (-72, 74.4), (-80, 74.25), (-86, 74.3), BEECHEY]
ROUTE_1846 = [BEECHEY, (-94.5, 74.4), (-96.2, 73.8), (-96.2, 72.6), (-96.9, 71.6), (-97.9, 70.7), BESET]
MARCH = [VICTORY, (-99.15, 69.35), EREBUS_BAY, (-99.2, 68.75), (-98.3, 68.55), (-97.4, 68.45), (-96.6, 68.0), BACK_RIVER]
WATER = [(-62, 72), (-66, 74.5), (-70, 74.6), (-75, 74.3), (-80, 74.2), (-85, 74.25), (-89, 74.3), (-93.5, 74.45),
         (-97, 74.6), (-101, 74.6), (-105, 74.5), (-110, 74.4), (-96.2, 73.2), (-98.0, 70.6), (-100.5, 68.0), (-107, 68.0),
         (-113, 67.6), (-88, 72.0), (-91.5, 71.5), (-60, 70), (-64, 76), (-72, 76), (-58, 68), (-95.5, 76.7), (-84, 77.0),
         (-118, 72.0), (-121, 74.0), (-102, 69.5), (-95, 69.7), (-90, 69.6), (-68, 72.5), (-62, 74)]
ICE_STREAM = [(-104.0, 73.5), (-101.5, 72.2), (-99.6, 71.0), (-98.6, 70.0), (-98.6, 69.2)]
EAST_PASS = [(-96.5, 71.5), (-95.6, 70.5), (-95.4, 69.6), (-95.6, 68.9), (-96.3, 68.5), (-97.6, 68.5)]
WEST_ROUTE = [(-97.9, 70.7), BESET]

# ------------------------------------------------------------------ figurinos
OFFICER = dict(shirt=(0.86, 0.85, 0.80), coat=(0.10, 0.13, 0.25), hat="pilot", hair=None)
SAILOR = dict(shirt=(0.30, 0.36, 0.52), hat="sailor", hair=None)
FRANKLIN = dict(shirt=(0.86, 0.85, 0.80), coat=(0.10, 0.13, 0.25), hat="pilot", hair=None, mustache=False)
RAE = dict(shirt=(0.45, 0.35, 0.22), coat=(0.40, 0.30, 0.20), hat="beanie", hat_col=(0.55, 0.48, 0.36), hair=None, mustache=True)
LADY = dict(shirt=(0.30, 0.20, 0.30), hair="long")
SCIENTIST = dict(col=(0.80, 0.40, 0.18))


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


def aurora(c, t, y=230, a=0.10, col=(0.45, 0.85, 0.65)):
    """aurora boreal discreta (faixas onduladas translúcidas)"""
    for k in range(3):
        c.move_to(-50, y + k * 40)
        for x in range(-50, W + 100, 60):
            c.line_to(x, y + k * 40 + math.sin(x / 210 + t * 0.35 + k) * 45)
        c.line_to(W + 100, y + k * 40 + 260); c.line_to(-50, y + k * 40 + 260); c.close_path()
        g = cairo.LinearGradient(0, y + k * 40 - 40, 0, y + k * 40 + 260)
        g.add_color_stop_rgba(0, col[0], col[1], col[2], a * (1 - k * 0.25))
        g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
        c.set_source(g); c.fill()


def sky(c, t, horizon=700, aur=True, moon_xy=(1600, 170)):
    stars(c, t, 80, horizon - 40)
    if aur:
        aurora(c, t)
    if moon_xy:
        c.save(); c.translate(*moon_xy); moon(c, 50); c.restore()
        glow(c, moon_xy[0], moon_xy[1], 220, ICE, 0.10)


def ice(c, t, y=780, seed=2):
    ice_field(c, t, y, seed=seed)


def snowland(c, y=820, col=(0.78, 0.82, 0.88)):
    """terra coberta de neve, levemente ondulada"""
    c.move_to(0, y)
    for x in range(0, W + 80, 80):
        c.line_to(x, y + math.sin(x / 260) * 18)
    c.line_to(W, H); c.line_to(0, H); c.close_path()
    g = cairo.LinearGradient(0, y, 0, H)
    g.add_color_stop_rgb(0, *col); g.add_color_stop_rgb(1, col[0] * 0.75, col[1] * 0.78, col[2] * 0.84)
    c.set_source(g); c.fill()
    for k in range(5):
        x = 140 + k * 390
        ellipse(c, x, y + 120 + (k % 2) * 60, 90, 10); rgb(c, (0.60, 0.66, 0.74), 0.5); c.fill()


def ship(c, t, x, y, s=0.6, name=None, furled=False, frost=0.0, alpha=1.0, rock=1.0, tilt=0.0, sails=True):
    def f(c):
        c.save()
        c.translate(x, y + math.sin(t * 1.1) * 5 * rock)
        c.rotate(tilt + math.sin(t * 0.8) * 0.02 * rock)
        c.scale(s, s)
        bomb_ship(c, t, name, sails=sails, furled=furled, frost=frost)
        c.restore()
    faded(c, alpha, f)


def arctic_map(c, proj, lands=None, grid=10):
    draw_map(c, proj, lands or ARCTIC, grid=grid, land_col=ICE_LAND, sea_col=ICE_SEA)


def x_over(c, t, t0, x, y, s=70):
    show(c, t, t0, x, y, lambda c: big_x(c, s, RED, 14), anim="stamp")


def boot(c, col=(0.34, 0.24, 0.16)):
    poly(c, [(-40, -120), (30, -120), (34, 30), (110, 50), (112, 90), (-44, 90)]); fs(c, col, 6)
    line(c, -40, 60, 112, 60, 3, (0.22, 0.15, 0.10))
    for y in (-90, -60, -30):
        line(c, -20, y, 14, y, 3, (0.70, 0.62, 0.46))


def theory_card(c, n, title_s, icon=None, crossed=0.0, dim=False, w=360, h=440):
    rrect(c, -w / 2, -h / 2, w, h, 14); fs(c, (0.12, 0.13, 0.16), 5, PARCH2 if not dim else LGRAY)
    text(c, n, 0, -h / 2 + 46, 34, TYPE, AMBER)
    text(c, title_s, 0, -h / 2 + 100, 40 if w < 400 else 50, SERIF, INK if not dim else GRAY)
    if icon:
        c.save(); c.translate(0, 60); icon(c); c.restore()
    if crossed > 0:
        c.save(); c.scale(crossed, crossed); big_x(c, 120, RED, 14); c.restore()


def portrait(c, who_kw, t=0, name=None, w=230, h=290, fid=40):
    """retrato estilo daguerreótipo (moldura oval escura com figura)"""
    rrect(c, -w / 2, -h / 2, w, h, 10); fs(c, (0.36, 0.26, 0.16), 6)
    c.save(); c.scale(1, 1.22); c.new_sub_path(); c.arc(0, -8, w * 0.38, 0, 6.283); c.restore()
    fs(c, (0.18, 0.17, 0.15), 4, (0.72, 0.62, 0.40))
    c.save(); c.translate(0, -8); c.scale(1, 1.22); c.new_sub_path(); c.arc(0, 0, w * 0.38, 0, 6.283); c.restore(); c.save(); c.clip()
    figure(c, t, 0, 230, 0.75, poses=[(0, "stand")], exprs=[(0, "neutral")], fid=fid, **who_kw)
    c.restore()
    if name:
        text(c, name, 0, h / 2 + 34, 30, SERIF, INK)


def labeled(fn, label, dy=130, size=34, col=INK):
    return group(fn, at(0, dy, T(label, size, col)))


def counter_text(c, t, t0, n, x, y, size=120, col=INK, d=1.2, suffix=""):
    if t < t0:
        return
    v = int(round(n * ease_out(prog(t, t0, d))))
    text(c, f"{v}{suffix}", x, y, size, SERIF, col)


# ================================================================== BLOCO 1
def s01(c, t):  # 0 - 16.7  Ilha Beechey, 1984
    sky(c, t, 700, moon_xy=(1620, 160))
    snowland(c, 720)
    show(c, t, 0.2, 960, 120, lambda c: date_stamp(c, "AGOSTO DE 1984", 48, AMBER), anim="stamp")
    typewrite(c, t, 3.2, "Ilha Beechey  -  Ártico canadense", 960, 215, 38, INK)
    for i, x in enumerate((1180, 1360, 1540)):
        show(c, t, 8.6 + i * 0.25, x, 760, sc(grave_board, "", 170, s=0.8), anim="up")
    if t > 5.5:
        a = fade_in(t, 5.5)
        for i, x in enumerate((760, 900)):
            hiker(c, t, x, 760, 0.62, [(0, "hold"), (6.0 + i * 0.4, "arms_up"), (7.0 + i * 0.4, "hold")],
                  [(0, "neutral"), (14.0, "shocked")], col=SCIENTIST["col"] if i == 0 else BLUE, fid=11 + i,
                  appear=5.6 + i * 0.3)
    if t > 11.0:
        # corte do chão mostrando a profundidade
        p = ease_out(prog(t, 11.0, 0.8))
        c.rectangle(700, 780, 460, 260 * p); rgb(c, (0.42, 0.40, 0.38)); c.fill()
        line(c, 700, 780, 1160, 780, 4)
        line(c, 1140, 790, 1140, 790 + 220 * p, 3, AMBER)
        show(c, t, 11.6, 1240, 900, T("1,5 m", 34, AMBER), anim="fade")
    if t > 14.0:
        show(c, t, 14.0, 930, 940, lambda c: (c.rotate(math.pi / 2), coffin(c, 0, w=110, h=360)), anim="fade", d=0.6)
        glow(c, 930, 940, 260, ICE, 0.12 * fade_in(t, 14.0))
    snow(c, t, 60, 30, 0.5)
    fog(c, t, 820, 0.06)
    HIST(c, t, [(0, "stand"), (8.6, "point_r"), (14.0, "think")], [(0, "neutral"), (14.0, "worried")], appear=0.6, x=260)


def s02(c, t):  # 16.7 - 32.9  dentro, preso no gelo; 138 anos
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.07, 0.10)); c.fill()
    lantern_glow_ice(c, t, 1000, 520, 620)
    op = ease_io(prog(t, 17.0, 2.4))
    c.save(); c.translate(1000, 540); c.rotate(math.pi / 2); coffin(c, op, w=210, h=640); c.restore()
    show(c, t, 17.9, 1000, 140, T("preso num bloco de gelo", 40, ICE), anim="fade", t1=20.0)
    show(c, t, 20.1, 1000, 140, lambda c: hl(c, "20 anos", 0, 0, 50), anim="up", t1=23.6)
    show(c, t, 21.7, 1520, 330, T("rosto intacto", 34), anim="fade", t1=29.0)
    show(c, t, 22.9, 1520, 390, T("cabelo comprido", 34), anim="fade", t1=29.0)
    show(c, t, 24.3, 1520, 450, T("olhos entreabertos", 34, AMBER), anim="fade", t1=29.0)
    if 24.3 < t < 29.2:
        k = fade_in(t, 24.3, 1.2) * (1 - fade_in(t, 28.2, 1.0))
        for dx in (-26, 26):
            glow(c, 740 + dx, 540, 40, ICE, 0.35 * k)
    show(c, t, 30.4, 1000, 140, lambda c: stitle(c, "MORTO HÁ 138 ANOS", 0, 0, 74, RED, BLOOD), anim="stamp")
    fog(c, t, 900, 0.05)
    HIST(c, t, [(0, "stand"), (24.0, "head")], [(0, "worried"), (24.0, "shocked"), (30.4, "sad")], x=230, s=0.9)


def s03(c, t):  # 32.9 - 46.2  John Torrington; 129 homens; nenhum voltou
    sky(c, t, 760, moon_xy=None)
    show(c, t, 33.8, 1130, 150, lambda c: hl(c, "JOHN TORRINGTON", 0, 0, 56), anim="up")
    show(c, t, 35.8, 1130, 240, T("o primeiro a morrer", 36, AMBER), anim="fade", t1=41.4)
    if 36.7 < t < 41.6:
        a = fade_in(t, 36.7) * (1 - fade_in(t, 40.8, 0.8))
        ship(c, t, 980, 640, 0.55, "EREBUS", alpha=a)
        ship(c, t, 1420, 660, 0.5, "TERROR", alpha=a)
        sea(c, t, 680, 0.1)
    if t > 41.6:
        c.save(); c.translate(1130, 470); crowd(c, t, 41.7, 129, 21, 52, s=0.2,
                                                    highlight=(lambda i: (0.45, 0.47, 0.52)) if t < 44.3 else (lambda i: (0.30, 0.20, 0.20)))
        c.restore()
        show(c, t, 41.8, 1130, 330, lambda c: stitle(c, "129 HOMENS", 0, 0, 70, INK, AMBER), anim="up", t1=44.2)
        show(c, t, 44.3, 1130, 330, lambda c: stitle(c, "NENHUM VOLTOU", 0, 0, 80, RED, BLOOD), anim="stamp")
    fog(c, t, 960, 0.07)
    HIST(c, t, [(0, "present"), (41.6, "point_r"), (44.3, "stand")], [(0, "neutral"), (44.3, "sad")], x=260)


def s04(c, t):  # 46.2 - 59.1  Torrington teve sorte; os outros não
    sky(c, t, 760, moon_xy=None)
    snowland(c, 800)
    show(c, t, 47.9, 560, 800, sc(grave_board, "1846", 230, s=1.0), anim="up")
    show(c, t, 48.6, 560, 380, T("um túmulo", 32), anim="fade")
    show(c, t, 49.4, 560, 430, T("uma lápide", 32), anim="fade")
    show(c, t, 50.4, 560, 480, lambda c: hl(c, "J. TORRINGTON", 0, 0, 30), anim="up")
    if t > 51.3:
        a = fade_in(t, 51.3)
        c.save(); c.translate(1000, 900); footprints(c, 12, 75, -12, t, 51.4, (0.50, 0.55, 0.64)); c.restore()
        show(c, t, 52.2, 1400, 420, T("os últimos sobreviventes", 36), anim="fade")
        show(c, t, 53.9, 1400, 480, T("sem túmulo, sem nome", 36, AMBER), anim="fade")
    if t > 56.6:
        show(c, t, 56.9, 1400, 230, lambda c: stitle(c, "pior do que o frio", 0, 0, 64, RED, BLOOD), anim="up")
    snow(c, t, 90, 50, 0.6)
    fog(c, t, 860, 0.07)
    HIST(c, t, [(0, "stand"), (47.9, "point_r"), (52.2, "think")], [(0, "neutral"), (52.2, "worried")], x=230, s=0.9)


def s05(c, t):  # 59.1 - 62.6  título
    sky(c, t, 760, moon_xy=(1640, 150))
    a = fade_in(t, 59.1, 1.2)
    ship(c, t, 760, 800, 0.62, furled=True, frost=0.9, alpha=0.8 * a, rock=0)
    ship(c, t, 1260, 815, 0.55, furled=True, frost=0.9, alpha=0.7 * a, rock=0, tilt=-0.04)
    ice(c, t, 830)
    glow(c, 960, 520, 520, ICE, 0.07 * a)
    show(c, t, 59.4, 960, 250, lambda c: (text(c, "A EXPEDIÇÃO", 0, -80, 50, TYPE, AMBER),
                                          stitle(c, "FRANKLIN", 0, 10, 140, INK, AMBER)), anim="fade", d=1.0)
    show(c, t, 60.6, 960, 420, T("1845  -  129 homens  -  2 navios", 38), anim="fade", d=0.8)
    snow(c, t, 110, 70, 0.7)
    fog(c, t, 860, 0.09, 7)


def s06(c, t):  # 62.6 - 73.0  voltar no tempo
    stars(c, t, 60, 600)
    show(c, t, 62.8, 960, 470, sc(hourglass, -t * 3, s=1.1), anim="fade")
    show(c, t, 63.4, 960, 160, T("voltando no tempo...", 40, AMBER), anim="fade", t1=68.6)
    if t > 63.0:
        p = ease_io(prog(t, 63.0, 6.0))
        yr = int(1984 - (1984 - 1845) * p)
        text(c, str(yr), 960, 760, 110, SERIF, INK)
    show(c, t, 69.2, 960, 170, lambda c: date_stamp(c, "INGLATERRA, MAIO DE 1845", 46, AMBER), anim="stamp")
    fog(c, t, 900, 0.06)
    HIST(c, t, [(0, "stand"), (63.0, "present")], [(0, "think")], x=300)


def s07(c, t):  # 73.0 - 89.0  Passagem do Noroeste
    arctic_map(c, NWP, ARCTIC)
    show(c, t, 73.2, 960, 70, lambda c: stitle(c, "A PASSAGEM DO NOROESTE", 0, 0, 52, INK, AMBER), anim="up")
    if t > 75.6:
        pts = [(-58, 72.5), (-66, 74.3), (-80, 74.2), (-92, 74.3), (-100, 74.5), (-110, 74.3), (-118, 73.4), (-122, 72.0)]
        map_path(c, NWP, pts, ease_io(prog(t, 75.6, 3.5)), AMBER, 6, [16, 12])
    show(c, t, 79.3, *NWP(-62, 66.5), T("ATLÂNTICO", 34, ICE), anim="fade")
    show(c, t, 80.0, *NWP(-117, 66.0), T("PACÍFICO", 34, ICE), anim="fade")
    show(c, t, 81.2, 1440, 960, lambda c: caption_box(c, "a rota mudaria o comércio do mundo", 38), anim="up", t1=84.0)
    show(c, t, 84.1, 960, 820, sc(flag, "ensign", t, s=0.8), anim="pop")
    show(c, t, 85.3, 960, 930, T("Império Britânico", 34, AMBER), anim="fade")


def s08(c, t):  # 89.0 - 112.2  Sir John Franklin
    sky(c, t, 800, aur=False)
    snowland(c, 980)
    fig(c, t, 1000, 1000, 1.05, [(0, "stand"), (91.6, "hips")], [(0, "confident")], fid=30, appear=91.4, **FRANKLIN)
    show(c, t, 91.7, 1000, 130, lambda c: hl(c, "SIR JOHN FRANKLIN", 0, 0, 56), anim="up")
    show(c, t, 93.1, 1450, 330, T("59 anos", 40, AMBER), anim="fade", t1=98.2)
    show(c, t, 94.5, 1450, 400, T("oficial respeitado", 34), anim="fade", t1=98.2)
    show(c, t, 95.8, 1450, 460, T("veterano do Ártico", 34), anim="fade", t1=98.2)
    if t > 98.3:
        show(c, t, 98.4, 1480, 330, lambda c: date_stamp(c, "DÉCADAS ANTES", 36, AMBER), anim="stamp", t1=104.5)
        show(c, t, 100.4, 1480, 520, sc(boot, s=0.9), anim="pop", t1=108.8)
        show(c, t, 102.9, 1640, 500, T("comeram o couro das botas", 30), anim="fade", t1=104.5)
        show(c, t, 105.2, 1480, 760, T("sobreviveu", 36, AMBER), anim="fade", t1=108.8)
        show(c, t, 107.3, 1480, 820, T("voltou como herói", 36), anim="fade", t1=108.8)
    show(c, t, 109.1, 1480, 420, sc(newspaper, "HERÓI", "", s=1.0), anim="drop")
    show(c, t, 109.9, 1480, 700, lambda c: hl(c, "o homem que comeu as botas", 0, 0, 38), anim="up")
    HIST(c, t, [(0, "present"), (98.4, "think"), (109.0, "point_r")], [(0, "neutral"), (100.0, "worried"), (109.0, "grin")], x=300)


def s09(c, t):  # 112.2 - 116.2  desta vez, ninguém passaria fome
    stars(c, t, 50, 500)
    for i, x in enumerate((760, 960, 1160, 1360, 1560)):
        show(c, t, 112.4 + i * 0.15, x, 800, sc(barrel, s=0.9), anim="up")
    for i, x in enumerate((860, 1060, 1260, 1460)):
        show(c, t, 112.9 + i * 0.15, x, 640, sc(tin_can, s=0.75), anim="up")
    show(c, t, 112.5, 1160, 180, lambda c: stitle(c, "ninguém ia passar fome", 0, 0, 62, INK, AMBER), anim="up")
    show(c, t, 115.0, 1160, 290, T("esse era o plano", 40, AMBER), anim="fade")
    HIST(c, t, [(0, "present")], [(0, "confident")], x=300)


def s10(c, t):  # 116.2 - 141.5  Erebus e Terror, tecnologia
    sky(c, t, 660, aur=False, moon_xy=(1680, 140))
    sea(c, t, 660, 0.15)
    ship(c, t, 1180, 690, 0.72, "EREBUS", alpha=fade_in(t, 117.0))
    ship(c, t, 1640, 700, 0.55, "TERROR", alpha=fade_in(t, 118.8))
    show(c, t, 117.1, 1180, 90, T("HMS EREBUS", 38, AMBER), anim="fade", t1=123.0)
    show(c, t, 118.9, 1640, 150, T("HMS TERROR", 38, AMBER), anim="fade", t1=123.0)
    if 120.5 < t < 126.4:
        show(c, t, 121.3, 980, 900, lambda c: caption_box(c, "cascos reforçados para o gelo", 38), anim="up")
        arrow_draw(c, t, 121.6, 980, 860, 1300, 740)
    if t > 126.4:
        show(c, t, 126.6, 700, 220, labeled(sc(locomotive_engine, s=0.8), "motor de locomotiva", 140, 30), anim="pop", t1=131.0)
        show(c, t, 129.4, 1060, 220, labeled(sc(propeller, t, s=1.1), "hélice recolhível", 140, 30), anim="pop", t1=131.0)
    if t > 131.1:
        show(c, t, 131.4, 600, 200, labeled(sc(stove, t, s=0.7), "aquecimento", 120, 28), anim="pop")
        show(c, t, 133.6, 900, 200, labeled(sc(barrel, label="ÁGUA", col=(0.30, 0.36, 0.44), s=0.7), "água potável", 120, 28), anim="pop")
        show(c, t, 137.2, 1240, 200, labeled(group(at(-50, 0, sc(book, "", BLOOD, s=0.55)), at(10, -10, sc(book, "", BLUE, s=0.55)),
                                                   at(70, 0, sc(book, "", GREEN, s=0.55))), "1.200 livros por navio", 120, 28),
             anim="pop")
    HIST(c, t, [(0, "stand"), (117.0, "point_r"), (126.6, "present")], [(0, "neutral"), (121.0, "confident")], x=260)


def s11(c, t):  # 141.5 - 159.3  comida para 3 anos; latas
    stars(c, t, 50, 400)
    show(c, t, 141.9, 1100, 120, lambda c: stitle(c, "nos porões", 0, 0, 58, INK, AMBER), anim="up")
    show(c, t, 143.5, 640, 420, labeled(sc(barrel, label="3 ANOS", s=1.0), "comida", 150, 28), anim="up")
    show(c, t, 145.2, 960, 420, labeled(sc(barrel, label="CARNE", col=(0.50, 0.24, 0.20), s=1.0), "+15 t de carne", 150, 28), anim="up")
    show(c, t, 147.0, 1280, 420, labeled(sc(barrel, label="FARINHA", col=(0.62, 0.55, 0.42), s=1.0), "toneladas de farinha", 150, 28),
         anim="up")
    if t > 149.1:
        for r in range(3):
            for k in range(9 - r):
                x = 660 + k * 90 + r * 45
                y = 900 - r * 110
                show(c, t, 149.2 + (r * 9 + k) * 0.05, x, y, sc(tin_can, s=0.55), anim="drop")
        show(c, t, 151.6, 1560, 840, T("milhares de latas", 36, AMBER), anim="fade")
        show(c, t, 152.4, 1560, 900, T("tecnologia nova", 30), anim="fade")
    show(c, t, 157.6, 1580, 380, sc(calendar, "5", AMBER, 80, s=0.9), anim="pop")
    show(c, t, 157.8, 1580, 520, T("até 5 anos", 36, AMBER), anim="fade")
    HIST(c, t, [(0, "present"), (149.0, "point_r"), (154.2, "think")], [(0, "confident"), (154.2, "neutral")], x=280)


def s12(c, t):  # 159.3 - 176.9  partida; Groenlândia; cinco voltam
    arctic_map(c, NATL, NORTH_ATLANTIC)
    show(c, t, 159.4, 960, 70, lambda c: date_stamp(c, "19 DE MAIO DE 1845", 44, AMBER), anim="stamp")
    map_point(c, NATL, *GREENHITHE, AMBER, 9, t)
    show(c, t, 163.4, *NATL(-6, 53.5), T("rio Tâmisa", 28), anim="fade")
    p = ease_io(prog(t, 163.0, 4.6)) * 0.55
    end, _ = map_path(c, NATL, ROUTE_OUT, p, AMBER, 5)
    show(c, t, 164.9, 640, 900, lambda c: caption_box(c, "134 homens", 40), anim="up", t1=167.1)
    if t > 167.2:
        map_point(c, NATL, *DISKO, ICE, 9, t)
        show(c, t, 167.4, *NATL(-46, 70.0), T("Groenlândia", 30, ICE), anim="fade")
        show(c, t, 168.2, 640, 900, lambda c: caption_box(c, "5 mandados de volta", 40), anim="up")
        for i in range(5):
            show(c, t, 168.4 + i * 0.12, 520 + i * 60, 800, lambda c: (circle(c, 0, -22, 10, FILL, 3), line(c, 0, -12, 0, 12, 3),
                                                                        line(c, 0, 12, -8, 26, 3), line(c, 0, 12, 8, 26, 3)), anim="pop")
    show(c, t, 173.7, 640, 990, T("e ganharam a vida", 34, AMBER), anim="fade")


def s13(c, t):  # 176.9 - 188.8  baleeiros; última vez
    sky(c, t, 660, moon_xy=None)
    sea(c, t, 660, 0.2)
    show(c, t, 177.3, 960, 110, lambda c: date_stamp(c, "FIM DE JULHO DE 1845", 40, AMBER), anim="stamp")
    show(c, t, 177.9, 960, 200, T("Baía de Baffin", 36), anim="fade")
    if t > 178.3:
        a = fade_in(t, 178.3)
        for i, x in enumerate((520, 760)):
            faded(c, a, lambda c, x=x: (c.save(), c.translate(x, 690 + math.sin(t + x) * 4), c.scale(0.34, 0.34),
                                        brigantine(c, t, 0, None), c.restore()))
        show(c, t, 178.6, 640, 880, T("baleeiros", 32), anim="fade")
    fade_out = 1 - fade_in(t, 184.6, 3.0)
    ship(c, t, 1260, 700, 0.42, alpha=0.95 * fade_out * fade_in(t, 179.8))
    ship(c, t, 1560, 712, 0.38, alpha=0.95 * fade_out * fade_in(t, 180.5))
    show(c, t, 184.0, 1400, 300, lambda c: stitle(c, "a última vez", 0, 0, 62, INK, AMBER), anim="fade", d=0.8)
    fog(c, t, 660, 0.06 + 0.10 * fade_in(t, 184.0, 2.5), 8)
    HIST(c, t, [(0, "stand"), (179.8, "point_r"), (185.0, "stand")], [(0, "neutral"), (184.0, "sad")], x=240, s=0.9)


# ================================================================== BLOCO 2
def s14(c, t):  # B2 0 - 10.8  dois anos sem notícia
    stars(c, t, 60, 500)
    for i, yr in enumerate(("1845", "1846", "1847")):
        show(c, t, B2(0.2 + i * 0.6), 820 + i * 260, 420, sc(calendar, yr, RED, 48, s=0.8), anim="drop")
    show(c, t, B2(1.4), 1080, 170, lambda c: stitle(c, "nenhuma notícia", 0, 0, 60, INK, AMBER), anim="up")
    show(c, t, B2(3.7), 1080, 660, T("Londres: ninguém se preocupou", 36), anim="fade")
    show(c, t, B2(6.7), 1080, 740, T("comida de sobra", 32, AMBER), anim="fade")
    show(c, t, B2(8.9), 1080, 800, T("no Ártico, o silêncio era normal", 32), anim="fade")
    HIST(c, t, [(0, "stand"), (B2(3.6), "shrug")], [(0, "neutral")], x=300)


def s15(c, t):  # B2 10.8 - 29.8  as buscas; Lady Jane Franklin
    arctic_map(c, NWP, ARCTIC)
    show(c, t, B2(11.2), 960, 70, lambda c: date_stamp(c, "1848: COMEÇAM AS BUSCAS", 44, AMBER), anim="stamp")
    rnd = random.Random(9)
    if t > B2(16.7):
        for i in range(32):
            t0 = B2(16.8) + i * 0.12
            if t < t0:
                break
            lon, lat = WATER[i % len(WATER)]
            lon += rnd.uniform(-1.2, 1.2); lat += rnd.uniform(-0.3, 0.3)
            x, y = NWP(lon, lat)
            a = fade_in(t, t0, 0.3)
            faded(c, a, lambda c, x=x, y=y: (c.save(), c.translate(x, y), c.scale(0.09, 0.09), brigantine(c, t, 0, None, rigging=False),
                                             c.restore()))
    show(c, t, B2(18.4), 1530, 900, lambda c: caption_box(c, "mais de 30 expedições", 42), anim="up")
    if t > B2(27.6):
        c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.55 * fade_in(t, B2(27.6))); c.fill()
        fig(c, t, 960, 900, 1.0, [(0, "stand")], [(0, "worried")], fid=31, appear=B2(27.7), **LADY)
        show(c, t, B2(27.9), 960, 200, lambda c: hl(c, "LADY JANE FRANKLIN", 0, 0, 52), anim="up")


def s16(c, t):  # B2 29.8 - 42.3  Ilha Beechey, 1850
    sky(c, t, 760)
    snowland(c, 780)
    show(c, t, B2(30.0), 960, 110, lambda c: date_stamp(c, "1850  -  ILHA BEECHEY", 46, AMBER), anim="stamp")
    show(c, t, B2(34.6), 760, 760, sc(tent, True, s=0.8), anim="fade")
    show(c, t, B2(35.4), 760, 590, T("acampamento de inverno", 30), anim="fade")
    if t > B2(37.2):
        for r in range(3):
            for k in range(5 - r):
                show(c, t, B2(37.3) + (r * 5 + k) * 0.04, 1050 + k * 52 + r * 26, 850 - r * 70,
                     sc(tin_can, open_=True, s=0.38), anim="drop")
        show(c, t, B2(38.6), 1150, 640, T("latas vazias", 30), anim="fade")
    for i, x in enumerate((1440, 1580, 1720)):
        show(c, t, B2(39.8) + i * 0.2, x, 830, sc(grave_board, "", 200, s=0.85), anim="up")
    show(c, t, B2(40.4), 1580, 560, T("três túmulos", 34, AMBER), anim="fade")
    snow(c, t, 60, 30, 0.5)
    fog(c, t, 860, 0.06)
    HIST(c, t, [(0, "stand"), (B2(34.6), "point_r")], [(0, "neutral"), (B2(39.8), "worried")], x=260, s=0.9)


def s17(c, t):  # B2 42.3 - 59.8  os três nomes
    sky(c, t, 800, aur=False)
    snowland(c, 860)
    rows = [(B2(42.5), 640, "J. TORRINGTON", ["foguista do Terror", "20 anos", "1º de janeiro de 1846"]),
            (B2(49.8), 1080, "J. HARTNELL", ["marinheiro do Erebus", "25 anos", "4 dias depois"]),
            (B2(55.8), 1520, "W. BRAINE", ["fuzileiro naval", "abril de 1846"])]
    for t0, x, name, info in rows:
        show(c, t, t0, x, 880, sc(grave_board, "", 230, s=1.0), anim="up")
        show(c, t, t0 + 0.1, x, 600, lambda c, name=name: hl(c, name, 0, 0, 36), anim="up")
        for j, s_ in enumerate(info):
            show(c, t, t0 + 0.9 + j * 1.3, x, 330 + j * 56, T(s_, 30, AMBER if j == 0 else INK), anim="fade")
    snow(c, t, 50, 20, 0.45)
    fog(c, t, 900, 0.06)


def s18(c, t):  # B2 59.8 - 76.9  algo estranho: nenhum bilhete
    sky(c, t, 780, aur=False)
    snowland(c, 820)
    show(c, t, B2(60.1), 1100, 130, lambda c: stitle(c, "3 mortes no primeiro inverno", 0, 0, 54, INK, AMBER), anim="up", t1=B2(65.3))
    show(c, t, B2(62.3), 1100, 230, T("não era absurdo", 36), anim="fade", t1=B2(65.3))
    show(c, t, B2(65.6), 1100, 130, lambda c: stitle(c, "algo estranho", 0, 0, 64, RED, BLOOD), anim="up")
    show(c, t, B2(68.1), 1100, 230, T("meses acampados ali", 36), anim="fade")
    show(c, t, B2(70.2), 1000, 520, sc(letter, 6, 300, 360, False, s=0.75), anim="pop")
    x_over(c, t, B2(71.0), 1000, 520, 100)
    show(c, t, B2(71.1), 1000, 760, T("nenhum bilhete", 38, AMBER), anim="fade")
    show(c, t, B2(71.9), 1400, 520, sc(big_q, 180, s=0.9), anim="pop")
    show(c, t, B2(72.3), 1400, 760, T("para onde iam?", 36), anim="fade")
    HIST(c, t, [(0, "stand"), (B2(65.6), "think"), (B2(70.2), "point_r")], [(0, "neutral"), (B2(65.6), "worried")], x=280)


def s19(c, t):  # B2 76.9 - 80.7  micro-gancho
    stars(c, t, 40, 400)
    glow(c, 960, 600, 700, BLOOD, 0.10)
    show(c, t, B2(77.1), 1150, 420, lambda c: stitle(c, "mas essa nem é", 0, -50, 56, INK),
         anim="fade", d=0.6)
    show(c, t, B2(78.4), 1150, 420, lambda c: stitle(c, "a parte mais perturbadora", 0, 40, 64, RED, BLOOD), anim="fade", d=0.6)
    fog(c, t, 860, 0.09, 7)
    HIST(c, t, [(0, "think")], [(0, "worried")], x=360, s=1.1)


def s20(c, t):  # B2 80.7 - 97.9  1859, Victory Point, a lata
    arctic_map(c, KW, ARCTIC, grid=2)
    show(c, t, B2(80.9), 960, 70, lambda c: date_stamp(c, "1859", 54, AMBER), anim="stamp")
    show(c, t, B2(84.2), 960, 150, T("14 anos depois da partida", 34), anim="fade")
    show(c, t, B2(87.7), *KW(-97.4, 68.35), T("Ilha do Rei Guilherme", 30, ICE), anim="fade")
    if t > B2(91.2):
        map_point(c, KW, *VICTORY, AMBER, 10, t)
        show(c, t, B2(91.3), *KW(-101.0, 69.75), T("Victory Point", 32, AMBER), anim="fade")
    if t > B2(89.1):
        x, y = 430, 760
        c.rectangle(x - 240, y - 230, 480, 420); rgb(c, (0.06, 0.08, 0.10), 0.85); c.fill()
        line(c, x - 240, y - 230, x + 240, y - 230, 3, AMBER)
        show(c, t, B2(89.3), x - 80, y + 160, sc(cairn, s=0.75), anim="up")
        fig(c, t, x + 140, y + 170, 0.6, [(0, "stand"), (B2(93.6), "point_l")], [(0, "neutral"), (B2(94.3), "shocked")],
            fid=32, appear=B2(92.4), **OFFICER)
        show(c, t, B2(92.5), x + 140, y - 180, T("ten. William Hobson", 26), anim="fade")
        show(c, t, B2(94.3), x - 80, y - 40, sc(tin_can, s=0.45), anim="pop")
        show(c, t, B2(96.2), x - 80, y - 110, T("um formulário da Marinha", 24, AMBER), anim="fade")


def s21(c, t):  # B2 97.9 - 112.0  a primeira mensagem: "tudo bem"
    stars(c, t, 40, 300)
    show(c, t, B2(98.1), 1100, 540, sc(navy_form, t, 0.0, s=1.25), anim="up")
    show(c, t, B2(99.6), 1100, 80, lambda c: date_stamp(c, "MAIO DE 1847", 44, AMBER), anim="stamp")
    show(c, t, B2(102.3), 1600, 300, T("navios presos no gelo", 30), anim="fade")
    show(c, t, B2(106.0), 1600, 360, T("Franklin no comando", 30), anim="fade")
    show(c, t, B2(110.8), 1100, 900, lambda c: hl(c, "TUDO BEM.", 0, 0, 70), anim="stamp")
    HIST(c, t, [(0, "present"), (B2(110.8), "think")], [(0, "neutral"), (B2(110.8), "think")], x=280)


def s22(c, t):  # B2 112.0 - 122.5  a segunda mensagem na margem
    stars(c, t, 40, 300)
    p = clamp01((t - B2(112.6)) / 7.5)
    c.save(); c.translate(1100, 540); c.scale(1.25, 1.25); navy_form(c, t, p); c.restore()
    if 112.4 < t - O2 < 121.0:
        glow(c, 1100, 540, 520, AMBER, 0.06 + 0.04 * math.sin(t * 3))
    show(c, t, B2(116.7), 1620, 300, T("11 meses depois", 34, AMBER), anim="fade")
    show(c, t, B2(118.3), 1620, 360, T("letra apressada", 30), anim="fade")
    show(c, t, B2(120.9), 1100, 80, lambda c: stitle(c, "isso mudou tudo", 0, 0, 58, RED, BLOOD), anim="up")
    HIST(c, t, [(0, "point_r"), (B2(120.9), "head")], [(0, "worried"), (B2(120.9), "shocked")], x=280)


def s23(c, t):  # B2 122.5 - 141.5  o que dizia a margem
    stars(c, t, 40, 300)
    show(c, t, B2(122.7), 1120, 520, lambda c: (rrect(c, -560, -400, 1120, 800, 10), fs(c, PARCH, 6)), anim="fade")
    items = [(B2(123.4), "presos no gelo desde set/1846"), (B2(127.8), "mais de 1 ano e meio parados"),
             (B2(130.7), "Franklin morreu em 11/06/1847"), (B2(136.7), "+ 9 oficiais e 15 marinheiros mortos")]
    for i, (t0, s_) in enumerate(items):
        typewrite(c, t, t0, s_, 1120, 250 + i * 150, 44, DARKTXT if i != 2 else BLOOD, cps=30)
    if t > B2(131.4):
        show(c, t, B2(131.6), 1580, 920, sc(wood_cross, 120, s=0.8), anim="up")
    HIST(c, t, [(0, "stand"), (B2(130.7), "head")], [(0, "worried"), (B2(130.7), "sad")], x=260, s=0.9)


def s24(c, t):  # B2 141.5 - 162.0  abandono; 105 homens rumo ao sul
    sky(c, t, 700, moon_xy=(1700, 140))
    ship(c, t, 1550, 720, 0.42, furled=True, frost=1.0, rock=0, alpha=0.9)
    ship(c, t, 1780, 735, 0.36, furled=True, frost=1.0, rock=0, alpha=0.8, tilt=-0.05)
    ice(c, t, 740)
    show(c, t, B2(141.7), 960, 100, lambda c: date_stamp(c, "22 DE ABRIL DE 1848", 46, AMBER), anim="stamp")
    show(c, t, B2(145.2), 960, 190, T("os navios são abandonados", 36), anim="fade")
    if t > B2(148.6):
        walk = (t - B2(148.6)) * 22
        for i in range(6):
            fig(c, t, 1180 - i * 120 - walk, 940, 0.5, [(0, "run")], [(0, "worried")], fid=40 + i,
                alpha=fade_in(t, B2(148.6) + i * 0.15), **(OFFICER if i == 0 else SAILOR))
        c.save(); c.translate(1300 - walk, 950); c.scale(0.55, 0.55); sledge_boat(c); c.restore()
        show(c, t, B2(148.8), 1500, 330, lambda c: stitle(c, "105 homens", 0, 0, 62, INK, AMBER), anim="up")
    show(c, t, B2(151.9), 1500, 430, lambda c: hl(c, "cap. Francis Crozier", 0, 0, 40), anim="up")
    show(c, t, B2(153.4), 520, 330, labeled(lambda c: arrow(c, 120, -40, -120, -40, AMBER, 8, 0), "rumo ao Rio Back", 20, 32),
         anim="fade")
    show(c, t, B2(157.2), 520, 450, T("centenas de km de gelo", 32), anim="fade")
    snow(c, t, 120, 80, 0.7)
    fog(c, t, 860, 0.08)


def s25(c, t):  # B2 162.0 - 170.3  assinaturas; "partimos amanhã"
    stars(c, t, 40, 300)
    c.save(); c.translate(1100, 520); c.scale(1.15, 1.15); navy_form(c, t, 1.0); c.restore()
    show(c, t, B2(163.5), 1100, 960, T("F. R. M. Crozier", 36, AMBER, HAND), anim="fade")
    show(c, t, B2(165.2), 1100, 1020, T("James Fitzjames", 36, AMBER, HAND), anim="fade")
    if t > B2(168.6):
        c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.45); c.fill()
        typewrite(c, t, B2(168.7), "\"partimos amanhã\"", 1100, 520, 74, INK, cps=14)
    HIST(c, t, [(0, "stand"), (B2(168.6), "think")], [(0, "neutral"), (B2(168.6), "sad")], x=260, s=0.9)


def s26(c, t):  # B2 170.3 - 182.4  24 mortos: alto demais
    stars(c, t, 40, 400)
    glow(c, 1100, 450, 600, BLOOD, 0.08)
    counter_text(c, t, B2(170.5), 24, 1100, 360, 200, RED, 1.0)
    show(c, t, B2(171.4), 1100, 520, T("mortos em menos de 3 anos", 40), anim="fade")
    show(c, t, B2(173.5), 1100, 600, T("em navios cheios de comida", 36, AMBER), anim="fade")
    show(c, t, B2(175.6), 1100, 720, T("alto demais", 40, RED), anim="fade")
    show(c, t, B2(177.5), 1100, 880, lambda c: caption_box(c, "algo matava aqueles homens a bordo", 40), anim="up")
    fog(c, t, 900, 0.08)
    HIST(c, t, [(0, "think"), (B2(177.5), "head")], [(0, "worried"), (B2(177.5), "shocked")], x=280)


# ================================================================== BLOCO 3
def s27(c, t):  # B3 0 - 8.6  seguindo a pista pela costa
    arctic_map(c, KW, ARCTIC, grid=2)
    show(c, t, B3(0.1), 960, 70, T("1859: seguindo a trilha", 40, AMBER), anim="fade")
    map_path(c, KW, MARCH, ease_io(prog(t, B3(1.0), 4.8)) * 0.42, AMBER, 6, [14, 10])
    map_point(c, KW, *VICTORY, AMBER, 8, t, False)
    if t > B3(6.3):
        map_point(c, KW, *EREBUS_BAY, RED, 10, t)
        show(c, t, B3(6.4), *KW(-101.6, 69.0), T("um dos barcos", 32, AMBER), anim="fade")


def s28(c, t):  # B3 8.6 - 28.8  o barco no trenó; carga inútil
    sky(c, t, 760, aur=False, moon_xy=None)
    snowland(c, 800)
    c.save(); c.translate(1080, 860); c.scale(1.3, 1.3); sledge_boat(c, 0, False); c.restore()
    show(c, t, B3(9.5), 1080, 990, lambda c: caption_box(c, "trenó de madeira e ferro", 34), anim="up", t1=B3(13.4))
    show(c, t, B3(13.6), 1080, 990, lambda c: caption_box(c, "dentro: dois esqueletos", 36), anim="up")
    items = [(B3(17.6), 640, "livros", group(at(-30, 0, sc(book, "", BLOOD, s=0.5)), at(30, -6, sc(book, "", BLUE, s=0.5)))),
             (B3(18.3), 900, "prata", group(at(-26, 0, sc(silver_fork, s=0.5)), at(26, 0, sc(silver_spoon, s=0.5)))),
             (B3(19.5), 1160, "sabonetes", sc(soap_bar, s=0.9)),
             (B3(20.6), 1420, "chinelos", sc(slipper, s=0.9)),
             (B3(21.5), 1680, "lenços de seda", lambda c: (poly(c, [(-60, -40), (60, -50), (50, 40), (-50, 50)]), fs(c, (0.70, 0.30, 0.38), 4)))]
    for t0, x, lab, fn in items:
        show(c, t, t0, x, 380, labeled(fn, lab, 110, 30), anim="drop")
    show(c, t, B3(22.9), 1160, 150, lambda c: stitle(c, "coisas inúteis no gelo", 0, 0, 58, INK, AMBER), anim="up")
    snow(c, t, 60, 30, 0.5)
    fog(c, t, 880, 0.07)
    HIST(c, t, [(0, "stand"), (B3(13.6), "head"), (B3(17.6), "point_ru"), (B3(23.2), "shrug")],
         [(0, "neutral"), (B3(13.6), "shocked"), (B3(23.2), "worried")], x=230, s=0.85)


def s29(c, t):  # B3 28.8 - 40.0  apontava de volta para o norte
    sky(c, t, 760, aur=False, moon_xy=None)
    snowland(c, 800)
    show(c, t, B3(29.0), 1500, 300, sc(compass, t, s=0.9), anim="pop")
    text(c, "N", 1500, 160, 40, SERIF, AMBER)
    rot = 0.0
    if t > B3(33.9):
        rot = math.pi * ease_io(prog(t, B3(33.9), 1.6))
    c.save(); c.translate(960, 820); c.scale(-1 if t > B3(34.7) else 1, 1); c.scale(1.0, 1.0); sledge_boat(c, 0, False); c.restore()
    if t < B3(33.9):
        show(c, t, B3(31.2), 960, 520, labeled(lambda c: arrow(c, 0, -60, 0, 80, GRAY, 8, 0), "sul: continente", -110, 30), anim="fade")
    else:
        show(c, t, B3(34.0), 960, 520, labeled(lambda c: arrow(c, 0, 80, 0, -80, AMBER, 9, 0), "norte: os navios", -120, 32, AMBER),
             anim="fade")
    show(c, t, B3(37.3), 960, 150, lambda c: stitle(c, "desistiram da marcha?", 0, 0, 58, INK, AMBER), anim="up")
    fog(c, t, 860, 0.07)
    HIST(c, t, [(0, "think"), (B3(33.9), "point_r")], [(0, "think"), (B3(34.0), "worried")], x=260, s=0.9)


def s30(c, t):  # B3 40.0 - 48.2  micro-gancho: contada pelos inuítes
    stars(c, t, 50, 500)
    snowland(c, 860)
    glow(c, 1300, 700, 500, ICE, 0.06)
    show(c, t, B3(40.3), 1100, 200, lambda c: stitle(c, "a parte mais sombria", 0, 0, 62, RED, BLOOD), anim="fade", d=0.7)
    show(c, t, B3(42.7), 1100, 300, T("não foi achada por nenhum oficial", 36), anim="fade")
    if t > B3(45.8):
        a = fade_in(t, B3(45.8), 1.4)
        faded(c, a, lambda c: inuk(c, t, 1300, 880, 0.95, [(0, "stand")], [(0, "neutral")]))
        show(c, t, B3(46.2), 1100, 380, T("foi contada pelos inuítes", 38, AMBER), anim="fade")
    fog(c, t, 880, 0.10, 7)
    HIST(c, t, [(0, "stand"), (B3(46.0), "point_r")], [(0, "worried"), (B3(46.0), "think")], x=330)


def s31(c, t):  # B3 48.2 - 66.2  John Rae
    arctic_map(c, NWP, ARCTIC)
    show(c, t, B3(48.4), 960, 70, lambda c: date_stamp(c, "1854", 54, AMBER), anim="stamp")
    if t > B3(53.9):
        c.rectangle(1160, 260, 560, 700); rgb(c, (0.05, 0.07, 0.10), 0.88); c.fill()
        line(c, 1160, 260, 1720, 260, 3, AMBER)
        fig(c, t, 1440, 900, 0.95, [(0, "stand"), (B3(60.4), "hold")], [(0, "confident")], fid=33, appear=B3(54.0), **RAE)
        show(c, t, B3(54.2), 1440, 320, lambda c: hl(c, "JOHN RAE", 0, 0, 44), anim="up")
        show(c, t, B3(56.4), 1440, 400, T("explorador escocês", 28), anim="fade")
    if t > B3(55.8):
        map_path(c, NWP, [(-92, 66.5), (-91, 67.6), PELLY], ease_io(prog(t, B3(55.8), 1.5)), AMBER, 5, [12, 10])
    show(c, t, B3(60.4), 600, 820, lambda c: caption_box(c, "viajava leve, caçava", 36), anim="up", t1=B3(63.5))
    show(c, t, B3(63.6), 600, 820, lambda c: caption_box(c, "aprendeu com os inuítes", 36), anim="up")


def s32(c, t):  # B3 66.2 - 88.3  o relato dos caçadores
    stars(c, t, 50, 400)
    snowland(c, 880)
    show(c, t, B3(66.3), 360, 110, T("Baía de Pelly", 36, AMBER), anim="fade")
    fig(c, t, 330, 960, 0.85, [(0, "stand"), (B3(70.0), "think")], [(0, "neutral"), (B3(80.0), "worried")], fid=33, **RAE)
    inuk(c, t, 560, 960, 0.85, [(0, "stand"), (B3(70.0), "present")], [(0, "neutral")], fid=34)
    inuk(c, t, 730, 960, 0.8, [(0, "stand"), (B3(73.2), "point_r")], [(0, "neutral")], fid=35, col=(0.44, 0.36, 0.28))
    show(c, t, B3(70.0), 1260, 470, lambda c: (cloud_shape(c, 1000, 640, (0.10, 0.12, 0.16), 5),), anim="fade", d=0.6)
    if t > B3(73.3):
        walk = (t - B3(73.3)) * 18
        for i in range(8):
            fig(c, t, 1560 - i * 70 - walk * 0.4, 640, 0.32, [(0, "run")], [(0, "worried")], fid=50 + i,
                alpha=fade_in(t, B3(73.3) + i * 0.1) * 0.9, **SAILOR)
        c.save(); c.translate(1500 - walk * 0.4, 646); c.scale(0.3, 0.3); sledge_boat(c, 0, False); c.restore()
        show(c, t, B3(75.4), 1260, 310, T("cerca de 40 homens brancos", 32, AMBER), anim="fade")
    show(c, t, B3(81.3), 1260, 760, T("magros", 34), anim="fade", t1=B3(85.0))
    show(c, t, B3(82.2), 1260, 820, T("trocaram comida", 30), anim="fade", t1=B3(85.0))
    show(c, t, B3(85.2), 1260, 790, T("\"os navios foram esmagados pelo gelo\"", 30, AMBER), anim="fade")


def s33(c, t):  # B3 88.3 - 100.5  cerca de 30 corpos
    stars(c, t, 50, 500)
    c.rectangle(0, 0, W, H); rgb(c, (0.0, 0.0, 0.02), 0.3); c.fill()
    snowland(c, 800, (0.62, 0.66, 0.72))
    show(c, t, B3(90.6), 960, 140, lambda c: stitle(c, "cerca de 30 corpos", 0, 0, 62, INK, AMBER), anim="fade", d=0.8)
    show(c, t, B3(93.1), 960, 240, T("perto da foz de um grande rio", 34), anim="fade")
    show(c, t, B3(92.6), 720, 800, sc(tent, True, s=0.85), anim="fade", d=1.2)
    show(c, t, B3(96.6), 720, 600, T("em barracas", 30), anim="fade")
    if t > B3(97.8):
        a = fade_in(t, B3(97.8))
        faded(c, a, lambda c: (c.save(), c.translate(1260, 820), c.rotate(math.pi), c.scale(1.1, 1.1), lifeboat(c, 0, False),
                               c.restore()))
        show(c, t, B3(98.0), 1260, 640, T("sob um barco virado", 30), anim="fade")
    snow(c, t, 80, 50, 0.6)
    fog(c, t, 820, 0.11, 8)


def s34(c, t):  # B3 100.5 - 114.7  o que Rae hesitou em escrever
    stars(c, t, 40, 300)
    show(c, t, B3(100.6), 1080, 480, sc(letter, 8, 420, 520, False, s=1.0), anim="up")
    if B3(102.0) < t < B3(104.4):
        line(c, 1180, 560, 1240, 470, 6, AMBER)
    show(c, t, B3(100.8), 1080, 120, T("a parte que Rae hesitou em escrever", 38, AMBER), anim="fade")
    show(c, t, B3(107.6), 1580, 520, labeled(sc(cook_pot, s=0.8), "as panelas", 120, 30), anim="pop")
    show(c, t, B3(111.9), 1080, 900, lambda c: caption_box(c, "canibalismo para sobreviver", 46), anim="stamp")
    glow(c, 1080, 900, 400, BLOOD, 0.08 * fade_in(t, B3(111.9)))
    HIST(c, t, [(0, "stand"), (B3(111.9), "head")], [(0, "worried"), (B3(111.9), "sad")], x=280)


def s35(c, t):  # B3 114.7 - 127.3  os objetos comprados
    stars(c, t, 40, 400)
    show(c, t, B3(114.9), 1100, 110, T("as provas de Rae", 40, AMBER), anim="fade")
    show(c, t, B3(119.4), 740, 480, sc(silver_fork, s=1.4), anim="pop", rot=-0.2)
    show(c, t, B3(120.0), 900, 480, sc(silver_spoon, s=1.4), anim="pop", rot=0.15)
    show(c, t, B3(121.2), 820, 760, T("brasões de oficiais", 32), anim="fade")
    show(c, t, B3(122.8), 1350, 470, sc(silver_plate, "SIR JOHN FRANKLIN", 210, s=1.0), anim="pop")
    if t > B3(125.3):
        glow(c, 1350, 470, 340, AMBER, 0.10 * fade_in(t, B3(125.3)))
    HIST(c, t, [(0, "present"), (B3(122.8), "point_r")], [(0, "neutral"), (B3(125.3), "shocked")], x=260, s=0.9)


def s36(c, t):  # B3 127.3 - 151.2  fúria em Londres
    stars(c, t, 40, 300)
    show(c, t, B3(127.4), 1100, 330, sc(newspaper, "O RELATÓRIO DE RAE", "Londres, 1854", s=1.1), anim="drop", t1=B3(135.1))
    show(c, t, B3(130.2), 1100, 640, lambda c: stitle(c, "fúria", 0, 0, 80, RED, BLOOD), anim="stamp", t1=B3(135.1))
    show(c, t, B3(131.1), 1100, 760, T("contra quem contou", 36), anim="fade", t1=B3(135.1))
    if B3(135.1) < t <= B3(147.0):
        fig(c, t, 780, 980, 0.9, [(0, "stand"), (B3(136.1), "hips")], [(0, "angry")], fid=31, **LADY)
        show(c, t, B3(135.3), 780, 420, lambda c: hl(c, "Lady Franklin", 0, 0, 38), anim="up")
        show(c, t, B3(136.2), 780, 500, T("recusou a versão", 30), anim="fade")
        fig(c, t, 1300, 980, 0.9, [(0, "stand"), (B3(139.1), "point_r")], [(0, "angry")], fid=36, appear=B3(137.6),
            shirt=(0.86, 0.85, 0.80), coat=(0.22, 0.20, 0.26), hair="tuft", mustache=True)
        show(c, t, B3(138.1), 1300, 420, lambda c: hl(c, "Charles Dickens", 0, 0, 38), anim="up")
        show(c, t, B3(139.2), 1300, 500, T("culpou os próprios inuítes", 30), anim="fade")
    if t > B3(147.0):
        fig(c, t, 1060, 980, 1.0, [(0, "stand")], [(0, "sad")], fid=33, **RAE)
        show(c, t, B3(149.4), 1060, 300, lambda c: date_stamp(c, "TRAIDOR?", 64, RED), anim="stamp")


def s37(c, t):  # B3 151.2 - 160.2  até que os ossos começaram a falar
    stars(c, t, 50, 500)
    show(c, t, B3(151.4), 1000, 420, sc(hourglass, t, s=0.9), anim="fade", t1=B3(156.8))
    show(c, t, B3(151.6), 1000, 150, T("por mais de 100 anos...", 40, AMBER), anim="fade", t1=B3(156.8))
    show(c, t, B3(153.0), 1000, 700, T("\"os inuítes estavam errados\"", 36), anim="fade", t1=B3(156.8))
    if t > B3(157.0):
        show(c, t, B3(157.1), 1000, 480, sc(bone, 300, s=1.2), anim="pop")
        glow(c, 1000, 480, 300, ICE, 0.14 * fade_in(t, B3(157.1)))
        show(c, t, B3(157.9), 1000, 200, lambda c: stitle(c, "os ossos começaram a falar", 0, 0, 58, INK, AMBER), anim="up")
    HIST(c, t, [(0, "stand"), (B3(157.0), "point_r")], [(0, "think"), (B3(157.0), "worried")], x=280)


def s38(c, t):  # B3 160.2 - 181.6  Anne Keenleyside, 1997
    stars(c, t, 40, 300)
    show(c, t, B3(160.4), 960, 80, lambda c: date_stamp(c, "1997", 50, AMBER), anim="stamp")
    show(c, t, B3(162.5), 600, 190, lambda c: hl(c, "Anne Keenleyside", 0, 0, 40), anim="up")
    show(c, t, B3(162.8), 600, 260, T("antropóloga", 28), anim="fade")
    fig(c, t, 600, 900, 0.9, [(0, "stand"), (B3(165.0), "hold")], [(0, "think")], fid=37, appear=B3(162.5),
        shirt=(0.86, 0.86, 0.84), hair="long")
    if t > B3(166.0):
        x0, y0 = 1080, 260
        c.save(); c.rectangle(x0, y0, 700, 460); rgb(c, ICE_SEA); c.fill(); c.rectangle(x0, y0, 700, 460); c.clip()
        sub = make_proj(-101.5, -96.5, 68.2, 70.2, coslat=True, box=(x0, y0, x0 + 700, y0 + 460))
        draw_map(c, sub, ARCTIC, grid=1, land_col=ICE_LAND, sea_col=ICE_SEA)
        map_point(c, sub, *EREBUS_BAY, RED, 10, t)
        text(c, "Baía Erebus", *(lambda p: (p[0] - 110, p[1] + 50))(sub(*EREBUS_BAY)), 28, TYPE, AMBER)
        c.restore()
        rrect(c, x0, y0, 700, 460, 6); rgb(c, INK); c.set_line_width(3); c.stroke()
    if t > B3(173.6):
        c.rectangle(1040, 240, 780, 820); rgb(c, (0.05, 0.06, 0.08), 0.92); c.fill()
        show(c, t, B3(173.7), 1240, 480, sc(donut, 0.25, 140, 50, RED), anim="pop")
        show(c, t, B3(174.0), 1240, 480, T("1/4", 46, INK), anim="fade")
        show(c, t, B3(175.3), 1600, 480, sc(bone, 260, s=0.9), anim="pop")
        if t > B3(176.0):
            for k in range(5):
                line(c, 1540 + k * 22, 462, 1552 + k * 22, 498, 3, RED)
        show(c, t, B3(175.5), 1420, 760, T("marcas de corte feitas por lâminas", 32, AMBER), anim="fade")
        show(c, t, B3(178.0), 1420, 830, T("compatíveis com retirada de carne", 30), anim="fade")


def s39(c, t):  # B3 181.6 - 196.2  Fitzjames identificado (2024)
    stars(c, t, 40, 300)
    show(c, t, B3(181.6), 960, 80, lambda c: date_stamp(c, "2024", 50, AMBER), anim="stamp")
    show(c, t, B3(183.5), 560, 520, sc(dna, t, s=1.0), anim="fade")
    show(c, t, B3(183.8), 560, 820, T("teste de DNA", 32), anim="fade")
    show(c, t, B3(187.2), 1080, 470, sc(portrait, OFFICER, t, "James Fitzjames", s=1.25), anim="pop")
    show(c, t, B3(189.0), 1550, 420, sc(navy_form, t, 1.0, s=0.45), anim="pop")
    show(c, t, B3(189.6), 1550, 620, T("assinou o bilhete", 30, AMBER), anim="fade")
    show(c, t, B3(192.3), 1080, 920, lambda c: caption_box(c, "marcas de corte também na mandíbula", 38), anim="up")


def s40(c, t):  # B3 196.2 - 202.4  os inuítes estavam certos
    sky(c, t, 800, moon_xy=None)
    snowland(c, 860)
    inuk(c, t, 1150, 960, 1.05, [(0, "stand")], [(0, "neutral")], fid=34)
    glow(c, 1150, 760, 360, AMBER, 0.10)
    show(c, t, B3(196.3), 1150, 220, lambda c: stitle(c, "os inuítes estavam certos", 0, 0, 62, INK, AMBER), anim="up")
    show(c, t, B3(198.3), 1150, 310, T("desde o começo", 40, AMBER), anim="fade")
    if t > B3(199.7):
        p = ease_out(prog(t, B3(199.7), 1.2))
        c.save(); c.translate(1560, 600 + 280 * p); c.rotate(p * 0.6)
        c.rectangle(-60, -22, 120, 30); fs(c, (0.10, 0.13, 0.25), 5); c.rectangle(-70, 8, 140, 12); fs(c, (0.08, 0.08, 0.10), 4)
        c.restore()
        show(c, t, B3(200.2), 1560, 480, T("a patente não salvou ninguém", 30), anim="fade")
    snow(c, t, 70, 40, 0.5)
    fog(c, t, 900, 0.07)
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=300, s=0.9)


# ================================================================== BLOCO 4
CARD_X = (620, 1020, 1420)



def s41(c, t):  # B4 0 - 12.0  como morreram todos?
    stars(c, t, 50, 400)
    show(c, t, B4(0.2), 1020, 110, lambda c: stitle(c, "a pergunta de quase 2 séculos", 0, 0, 52, INK, AMBER), anim="up")
    show(c, t, B4(4.6), 1020, 210, T("129 homens, navios modernos, comida para anos", 34), anim="fade")
    for i, (n, ttl) in enumerate((("1", "O GELO"), ("2", "O CHUMBO"), ("3", "O COMANDO"))):
        show(c, t, B4(4.9) + i * 0.6, CARD_X[i], 620, lambda c, n=n, ttl=ttl: theory_card(c, n, ttl, lambda c: big_q(c, 120)), anim="up")
    show(c, t, B4(10.2), 1020, 960, T("morreram todos?", 40, RED), anim="fade")


def s42(c, t):  # B4 12.0 - 44.4  teoria 1: o gelo e o escorbuto
    if t < B4(23.3):
        arctic_map(c, KW, ARCTIC, grid=2)
        map_path(c, KW, ICE_STREAM, ease_io(prog(t, B4(18.0), 3.0)), ICE, 14, None)
        if t > B4(18.1):
            show(c, t, B4(18.4), *KW(-101.8, 71.1), T("corrente de gelo", 32, ICE), anim="fade")
            map_point(c, KW, *BESET, RED, 10, t)
            show(c, t, B4(19.3), *KW(-96.5, 70.4), T("navios presos", 30, AMBER), anim="fade")
        c.rectangle(80, 40, 560, 140); rgb(c, (0.05, 0.07, 0.10), 0.85); c.fill()
        show(c, t, B4(12.3), 360, 110, lambda c: theory_card(c, "1", "O GELO", w=520, h=130) if False else
             (text(c, "1  -  O GELO", 0, 0, 56, SERIF, AMBER)), anim="up")
        show(c, t, B4(15.9), 1500, 960, lambda c: date_stamp(c, "SETEMBRO DE 1846", 36, AMBER), anim="stamp")
        return
    sky(c, t, 760, aur=False, moon_xy=None)
    ice(c, t, 780)
    ship(c, t, 1520, 800, 0.45, furled=True, frost=1.0, rock=0)
    text(c, "1  -  O GELO", 360, 110, 56, SERIF, AMBER)
    show(c, t, B4(23.4), 1520, 380, sc(thermometer, "-40 °C", 0.05, s=1.0), anim="pop", t1=B4(28.6))
    show(c, t, B4(24.0), 1520, 580, T("verões frios demais", 32), anim="fade", t1=B4(28.6))
    show(c, t, B4(28.8), 1000, 230, lambda c: hl(c, "ESCORBUTO", 0, 0, 60, bg=(0.55, 0.18, 0.18), col=INK), anim="stamp")
    show(c, t, B4(29.9), 1000, 320, T("falta de vitamina C", 34), anim="fade")
    show(c, t, B4(32.3), 1000, 420, T("gengivas sangram", 30), anim="fade", t1=B4(37.0))
    show(c, t, B4(33.6), 1000, 470, T("dentes caem", 30), anim="fade", t1=B4(37.0))
    show(c, t, B4(34.8), 1000, 520, T("feridas antigas reabrem", 30), anim="fade", t1=B4(37.0))
    if t > B4(37.0):
        lvl = 1 - 0.85 * ease_io(prog(t, B4(38.8), 4.5))
        show(c, t, B4(37.1), 860, 520, sc(lemon, s=1.0), anim="pop")
        show(c, t, B4(37.4), 1100, 520, lambda c: lime_bottle(c, lvl), anim="pop")
        show(c, t, B4(38.8), 980, 700, T("perdia a força com o tempo", 32, AMBER), anim="fade")
    HIST(c, t, [(0, "stand"), (B4(28.8), "point_r")], [(0, "neutral"), (B4(32.3), "worried")], x=260, s=0.9)


def s43(c, t):  # B4 44.4 - 74.4  teoria 2: o chumbo
    stars(c, t, 40, 300)
    text(c, "2  -  O CHUMBO", 360, 110, 56, SERIF, AMBER)
    show(c, t, B4(45.0), 1150, 240, lambda c: date_stamp(c, "EXUMAÇÃO DE 1984", 40, AMBER), anim="stamp", t1=B4(57.5))
    show(c, t, B4(51.6), 1150, 360, lambda c: hl(c, "Owen Beattie", 0, 0, 40), anim="up", t1=B4(57.5))
    show(c, t, B4(54.0), 1150, 520, labeled(lambda c: (circle(c, 0, 0, 80, (0.45, 0.47, 0.52), 6), text(c, "Pb", 0, 0, 70, SERIF, INK)),
                                            "chumbo altíssimo no cabelo e no corpo", 140, 30, AMBER), anim="pop", t1=B4(57.5))
    if t > B4(57.7):
        for i, x in enumerate((900, 1060, 1220, 1380)):
            show(c, t, B4(59.2) + i * 0.12, x, 470, sc(tin_can, "" if i else "", True, s=0.85), anim="drop")
        glow(c, 1140, 470, 360, (0.6, 0.6, 0.7), 0.10 * fade_in(t, B4(61.8)))
        show(c, t, B4(60.4), 1140, 650, T("fechadas às pressas", 32), anim="fade")
        show(c, t, B4(61.8), 1140, 700, T("solda de chumbo", 32, AMBER), anim="fade")
        show(c, t, B4(63.2), 1140, 750, T("fornecedor atrasado", 30), anim="fade", t1=B4(65.9))
    if t > B4(66.0):
        c.rectangle(0, 790, W, 290); rgb(c, (0.03, 0.04, 0.06), 0.9); c.fill()
        show(c, t, B4(66.2), 1140, 840, T("enfraquece o corpo e confunde a mente", 34, AMBER), anim="fade")
        show(c, t, B4(69.6), 1140, 920, T("decisões estranhas?", 34), anim="fade")
        show(c, t, B4(71.8), 1600, 900, sc(silver_fork, s=0.7), anim="pop", rot=0.4)
    HIST(c, t, [(0, "stand"), (B4(59.2), "point_r"), (B4(66.0), "think")], [(0, "neutral"), (B4(66.0), "think")], x=260, s=0.9)


def s44(c, t):  # B4 74.4 - 105.0  estudos recentes
    stars(c, t, 40, 300)
    text(c, "2  -  O CHUMBO", 360, 110, 56, SERIF, AMBER)
    if t < B4(92.0):
        show(c, t, B4(74.6), 1150, 220, lambda c: stitle(c, "estudos recentes", 0, 0, 54, INK, AMBER), anim="up")
        show(c, t, B4(77.9), 1150, 310, T("2016: a unha de John Hartnell", 34), anim="fade")
        show(c, t, B4(79.3), 1150, 580, lambda c: lead_chart(c, t, clamp01((t - B4(82.5)) / 4.5), 760, 380), anim="fade")
        show(c, t, B4(82.9), 900, 820, T("normal quase a viagem toda", 28), anim="fade")
        show(c, t, B4(85.4), 1440, 820, T("subiu no fim (fome e doença)", 28, RED), anim="fade")
    elif t < B4(97.6):
        c.save(); c.translate(1150, 560); crowd(c, t, B4(92.1), 40, 10, 70, s=0.3, highlight=lambda i: (0.45, 0.47, 0.55)); c.restore()
        show(c, t, B4(92.3), 1150, 380, T("marinheiros da época: chumbo parecido", 36, AMBER), anim="fade")
    else:
        show(c, t, B4(97.7), 1150, 600, lambda c: theory_card(c, "2", "O CHUMBO", lambda c: text(c, "Pb", 0, 0, 90, SERIF, GRAY),
                                                              dim=t > B4(102.2)), anim="pop")
        show(c, t, B4(100.6), 1560, 520, T("piorou as coisas...", 30), anim="fade")
        show(c, t, B4(102.3), 1560, 580, T("mas não foi o assassino", 30, AMBER), anim="fade")
    HIST(c, t, [(0, "stand"), (B4(79.3), "point_r"), (B4(97.7), "think")], [(0, "neutral"), (B4(97.7), "think")], x=260, s=0.9)


def s45(c, t):  # B4 105.0 - 136.5  teoria 3: o comando
    if t < B4(122.4):
        arctic_map(c, KW, ARCTIC, grid=2)
        c.rectangle(60, 30, 680, 140); rgb(c, (0.05, 0.07, 0.10), 0.85); c.fill()
        show(c, t, B4(105.2), 400, 100, lambda c: text(c, "3  -  O COMANDO", 0, 0, 56, SERIF, AMBER), anim="up")
        if t > B4(108.9):
            map_path(c, KW, ICE_STREAM, 1.0, ICE, 10)
            map_path(c, KW, ROUTE_1846[-3:], ease_io(prog(t, B4(109.0), 1.6)), RED, 7)
            show(c, t, B4(110.6), *KW(-101.4, 70.15), T("estreito com gelo acumulado", 28, AMBER), anim="fade")
        if t > B4(113.4):
            map_path(c, KW, EAST_PASS, ease_io(prog(t, B4(113.5), 2.4)), GREEN, 7, [14, 10])
            show(c, t, B4(114.4), *KW(-93.6, 70.9), T("passagem protegida", 28, LGREEN), anim="fade")
        if t > B4(118.3):
            x, y = KW(-97.4, 69.25)
            show(c, t, B4(119.2), x, y, sc(big_q, 110, s=0.8), anim="pop")
            show(c, t, B4(120.4), 1300, 990, lambda c: caption_box(c, "os mapas não mostravam que era uma ilha", 32), anim="up")
    else:
        sky(c, t, 760, aur=False, moon_xy=None)
        ice(c, t, 820)
        text(c, "3  -  O COMANDO", 400, 100, 56, SERIF, AMBER)
        c.save(); c.translate(1150, 900); c.scale(0.9, 0.9); sledge_boat(c, 0, True); c.restore()
        fig(c, t, 1500, 930, 0.55, [(0, "run")], [(0, "desperate")], fid=60, **SAILOR)
        show(c, t, B4(122.6), 1150, 600, T("barcos pesados, objetos inúteis", 34, AMBER), anim="fade")
        show(c, t, B4(128.9), 1150, 660, T("em vez de viajar leve como os inuítes", 32), anim="fade")
        show(c, t, B4(130.9), 1150, 260, lambda c: hl(c, "mas é preciso ser justo", 0, 0, 44), anim="up")
        show(c, t, B4(133.0), 1150, 360, T("seguiam o que a Marinha ensinava", 32, AMBER), anim="fade")
    HIST(c, t, [(0, "stand"), (B4(109.0), "point_r"), (B4(130.9), "present")], [(0, "neutral"), (B4(122.4), "worried"),
                                                                                (B4(130.9), "think")], x=240, s=0.85)


# ================================================================== BLOCO 5
def s46(c, t):  # B5 0 - 9.6  150 anos desaparecidos
    stars(c, t, 50, 500)
    sea(c, t, 760, 0.1)
    show(c, t, B5(0.1), 1100, 200, lambda c: stitle(c, "mais de 150 anos", 0, 0, 62, INK, AMBER), anim="up")
    show(c, t, B5(3.0), 1100, 300, T("os navios continuavam desaparecidos", 36), anim="fade")
    if t > B5(5.6):
        inuk(c, t, 1100, 900, 0.9, [(0, "stand"), (B5(7.5), "point_r")], [(0, "neutral")], fid=34, appear=B5(5.7))
        show(c, t, B5(6.2), 1100, 380, T("as histórias dos inuítes apontaram o caminho", 32, AMBER), anim="fade")
    fog(c, t, 820, 0.07)
    HIST(c, t, [(0, "stand")], [(0, "think")], x=300, s=0.9)


def underwater(c, t, depth_label=None, seabed_y=900):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.05, 0.12, 0.17); g.add_color_stop_rgb(1, 0.01, 0.03, 0.05)
    c.rectangle(0, 0, W, H); c.set_source(g); c.fill()
    for i in range(5):
        x = 200 + i * 380 + math.sin(t * 0.3 + i) * 40
        poly(c, [(x, 0), (x + 60, 0), (x + 200, H), (x + 120, H)])
        rgb(c, ICE, 0.035); c.fill()
    c.save(); c.translate(960, seabed_y); seabed(c, t, 120, 2400, 6, (0.10, 0.12, 0.13)); c.restore()
    rnd = random.Random(3)
    for i in range(40):
        x0, y0 = rnd.uniform(0, W), rnd.uniform(0, H)
        y = (y0 - t * rnd.uniform(4, 12)) % H
        circle(c, (x0 + math.sin(t + i) * 8) % W, y, rnd.uniform(1.5, 3), (0.6, 0.75, 0.85), 0)


def s47(c, t):  # B5 9.6 - 28.9  o Erebus (2014)
    underwater(c, t)
    show(c, t, B5(10.0), 960, 90, lambda c: date_stamp(c, "SETEMBRO DE 2014", 44, AMBER), anim="stamp")
    show(c, t, B5(12.0), 960, 180, T("guiados por relatos orais inuítes", 34), anim="fade")
    if t > B5(15.6):
        a = fade_in(t, B5(15.6), 1.5)
        ship(c, t, 1100, 860, 0.85, "EREBUS", sails=False, alpha=0.85 * a, rock=0, tilt=0.06)
        glow(c, 1100, 760, 500, ICE, 0.08 * a)
    if t > B5(18.5):
        line(c, 1760, 230, 1760, 760, 3, AMBER)
        show(c, t, B5(18.6), 1760, 800, T("11 m", 40, AMBER), anim="fade")
    if t > B5(20.4):
        x0, y0 = 120, 260
        c.save(); c.rectangle(x0, y0, 560, 470); c.clip()
        sub = make_proj(-102.0, -95.5, 67.6, 70.4, coslat=True, box=(x0, y0, x0 + 560, y0 + 470))
        draw_map(c, sub, ARCTIC, grid=1, land_col=ICE_LAND, sea_col=ICE_SEA)
        map_point(c, sub, *BESET, AMBER, 8, t, False)
        p = ease_io(prog(t, B5(20.6), 2.0))
        map_path(c, sub, [BESET, (-98.9, 69.3), (-99.6, 68.7), EREBUS_WRECK], p, RED, 5, [10, 8])
        if p > 0.98:
            map_point(c, sub, *EREBUS_WRECK, RED, 9, t)
        c.restore()
        rrect(c, x0, y0, 560, 470, 6); rgb(c, INK); c.set_line_width(3); c.stroke()
        show(c, t, B5(21.0), x0 + 280, y0 + 510, T("+100 km ao sul", 32, AMBER), anim="fade")
    if t > B5(24.6):
        a = fade_in(t, B5(24.6), 1.5)
        for i, x in enumerate((980, 1160)):
            fig(c, t, x, 805, 0.35, [(0, "stand")], [(0, "neutral")], alpha=0.35 * a, fid=70 + i, **SAILOR)
        show(c, t, B5(25.3), 1200, 300, T("alguém voltou a bordo?", 36, ICE), anim="fade")


def s48(c, t):  # B5 28.9 - 49.8  Sammy Kogvik e o mastro
    sky(c, t, 760)
    ice(c, t, 780, seed=5)
    show(c, t, B5(29.1), 1150, 120, lambda c: stitle(c, "a descoberta mais assustadora", 0, 0, 56, INK, AMBER), anim="up", t1=B5(33.6))
    show(c, t, B5(33.7), 1150, 120, T("anos antes...", 40, AMBER), anim="fade")
    inuk(c, t, 980, 960, 0.9, [(0, "stand"), (B5(39.8), "point_r"), (B5(43.6), "hold")], [(0, "neutral"), (B5(39.8), "shocked"),
                                                                                           (B5(43.6), "happy")], fid=38, appear=B5(34.6))
    show(c, t, B5(36.1), 980, 330, lambda c: hl(c, "Sammy Kogvik", 0, 0, 44), anim="up")
    show(c, t, B5(34.8), 980, 400, T("caçador inuíte", 28), anim="fade")
    show(c, t, B5(39.8), 1180, 880, sc(mast_stub, 230, s=1.0), anim="up")
    show(c, t, B5(40.6), 1500, 540, T("um \"mastro\" saindo do gelo", 32, AMBER), anim="fade")
    if B5(43.5) < t < B5(44.4):
        c.rectangle(0, 0, W, H); rgb(c, (1, 1, 1), 0.6 * (1 - fade_in(t, B5(43.5), 0.9))); c.fill()
    if t > B5(45.3):
        p = ease_io(prog(t, B5(45.4), 1.4))
        faded(c, 1 - p, lambda c: (c.save(), c.translate(1180, 720 + 120 * p), c.rotate(p * 1.2), camera_compact(c), c.restore()))
        show(c, t, B5(45.5), 1500, 610, T("a câmera se perdeu", 30), anim="fade")
    show(c, t, B5(47.6), 1500, 680, T("e ele guardou a história", 30, AMBER), anim="fade")
    snow(c, t, 80, 50, 0.6)
    fog(c, t, 860, 0.07)


def s49(c, t):  # B5 49.8 - 62.2  o desvio e o Terror
    if t < B5(58.3):
        arctic_map(c, KW, ARCTIC, grid=2)
        show(c, t, B5(50.0), 960, 70, lambda c: date_stamp(c, "SETEMBRO DE 2016", 44, AMBER), anim="stamp")
        show(c, t, B5(52.1), 1450, 960, lambda c: caption_box(c, "ele contou tudo à tripulação", 34), anim="up", t1=B5(55.1))
        p = ease_io(prog(t, B5(55.4), 2.4))
        path = [(-96.0, 68.62), (-97.3, 68.45), (-98.6, 68.55), (-99.4, 68.7), TERROR_WRECK]
        end, _ = map_path(c, KW, path, p, AMBER, 6, [14, 10])
        c.save(); c.translate(*end); c.scale(0.08, 0.08); sonar_ship(c, t); c.restore()
        show(c, t, B5(55.2), 1450, 960, lambda c: caption_box(c, "desviaram a rota até a baía", 34), anim="up")
        return
    underwater(c, t)
    a = fade_in(t, B5(58.3), 1.2)
    ship(c, t, 1000, 860, 0.85, "TERROR", sails=False, alpha=0.9 * a, rock=0)
    glow(c, 1000, 740, 520, ICE, 0.10 * a)
    show(c, t, B5(58.6), 1000, 150, lambda c: stitle(c, "o Terror estava lá", 0, 0, 66, INK, AMBER), anim="fade", d=0.8)
    show(c, t, B5(60.1), 1000, 250, T("exatamente onde ele disse", 38, AMBER), anim="fade")


def s50(c, t):  # B5 62.2 - 66.8  Baía do Terror
    arctic_map(c, KW, ARCTIC, grid=2)
    map_point(c, KW, *TERROR_WRECK, RED, 12, t)
    show(c, t, B5(62.4), 960, 90, T("o nome do lugar nos mapas:", 40), anim="fade")
    show(c, t, B5(64.6), *(lambda p: (p[0] - 330, p[1] - 20))(KW(*TERROR_WRECK)), lambda c: nameboard(c, "BAÍA DO TERROR", 54), anim="stamp")


def s51(c, t):  # B5 66.8 - 89.1  intacto; as portas
    if t < B5(78.6):
        underwater(c, t)
        ship(c, t, 1100, 860, 0.95, "TERROR", sails=False, rock=0)
        line(c, 1780, 160, 1780, 760, 3, AMBER)
        show(c, t, B5(69.6), 1780, 800, T("24 m", 40, AMBER), anim="fade")
        show(c, t, B5(68.0), 600, 160, T("de pé no fundo do mar", 36), anim="fade")
        show(c, t, B5(71.0), 600, 230, T("quase intacto", 36, AMBER), anim="fade")
        show(c, t, B5(72.4), 600, 300, T("escotilhas fechadas", 32), anim="fade")
        show(c, t, B5(73.9), 600, 360, T("vidros nas claraboias", 32), anim="fade")
        show(c, t, B5(75.9), 1100, 380, sc(shelf_plates, s=0.9), anim="pop")
        show(c, t, B5(76.2), 1100, 300, T("pratos nas prateleiras", 30, AMBER), anim="fade")
        return
    c.rectangle(0, 0, W, H); rgb(c, (0.02, 0.04, 0.06)); c.fill()
    c.save(); c.translate(1020, 560); cabin_corridor(c, t, 6, 3, 1500, 520); c.restore()
    beam = 0.5 + 0.5 * math.sin(t * 0.7)
    glow(c, 300 + (t - B5(78.6)) * 40, 560, 420, ICE, 0.10)
    c.save(); c.translate(260 + (t - B5(78.6)) * 40, 900); c.scale(0.55, 0.55); auv(c, t); c.restore()
    show(c, t, B5(78.8), 1020, 140, T("um robô submarino entrou nos corredores", 36), anim="fade", t1=B5(85.3))
    show(c, t, B5(82.3), 1020, 960, T("todas as portas abertas", 36), anim="fade", t1=B5(85.3))
    if t > B5(85.4):
        dx = 1020 - 750 + 3.5 * 250
        glow(c, dx, 560, 260, AMBER, 0.18 + 0.05 * beam)
        show(c, t, B5(85.5), 1020, 140, lambda c: stitle(c, "menos uma", 0, 0, 66, RED, BLOOD), anim="stamp")
        show(c, t, B5(86.3), 1020, 960, lambda c: hl(c, "a cabine do capitão Crozier", 0, 0, 44), anim="up")


def s52(c, t):  # B5 89.1 - 103.6  diários nas gavetas
    c.rectangle(0, 0, W, H); rgb(c, (0.03, 0.05, 0.07)); c.fill()
    lantern_glow_ice(c, t, 1100, 600, 600)
    # mesa com gaveta
    c.rectangle(760, 620, 680, 40); fs(c, (0.36, 0.25, 0.16), 5)
    c.rectangle(800, 660, 600, 220); fs(c, (0.30, 0.21, 0.13), 5)
    op = ease_io(prog(t, B5(90.9), 1.4))
    c.rectangle(860 + 0, 700 + 0, 480, 120); fs(c, (0.40, 0.28, 0.18), 5)
    if op > 0:
        c.rectangle(860 - 40 * op, 700 + 140 * op, 480 + 80 * op, 110); fs(c, (0.40, 0.28, 0.18), 5)
        for k in range(3):
            c.save(); c.translate(960 + k * 130, 740 + 140 * op); c.rotate(-0.05 + k * 0.05); scroll(c, 2, 110, 70); c.restore()
        glow(c, 1100, 780, 300, AMBER, 0.15 * op)
    show(c, t, B5(89.4), 1100, 160, T("protegidos pelo frio e pela lama", 36), anim="fade")
    show(c, t, B5(95.2), 1100, 240, T("diários e mapas legíveis?", 40, AMBER), anim="fade")
    show(c, t, B5(97.8), 1100, 1000, lambda c: caption_box(c, "as últimas palavras daqueles homens", 38), anim="up")
    HIST(c, t, [(0, "stand"), (B5(95.2), "point_r")], [(0, "think")], x=300, s=0.9)
    fog(c, t, 980, 0.06)


def s53(c, t):  # B5 103.6 - 115.4  pergunta ao espectador
    stars(c, t, 60, 500)
    show(c, t, B5(103.9), 1100, 110, lambda c: stitle(c, "E você?", 0, 0, 70, INK, AMBER), anim="up")
    show(c, t, B5(106.1), 1100, 200, T("o que matou a tripulação de Franklin?", 38), anim="fade")
    xs = (720, 1100, 1480)
    for i, (n, ttl, tt0) in enumerate((("1", "O GELO", B5(108.5)), ("2", "O CHUMBO", B5(109.3)), ("3", "O COMANDO", B5(110.3)))):
        show(c, t, tt0, xs[i], 560, lambda c, n=n, ttl=ttl: theory_card(c, n, ttl, lambda c: big_q(c, 110), w=320, h=400), anim="up")
    show(c, t, B5(111.8), 1100, 900, lambda c: (speech(c, 780, 130, -280, 120), text(c, "deixe sua teoria nos comentários", 0, 0, 40, HAND, INK)),
         anim="pop")
    HIST(c, t, [(0, "stand"), (B5(103.9), "point_r"), (B5(111.8), "present")], [(0, "think"), (B5(111.8), "happy")], x=280)


def s54(c, t):  # B5 115.4 - fim  encerramento
    sky(c, t, 760, moon_xy=(1640, 160))
    ice(c, t, 950)
    k = fade_in(t, B5(115.4), 2.0)
    ship(c, t, 1640, 965, 0.38, furled=True, frost=1.0, rock=0, alpha=0.4 * k)
    HIST(c, t, [(0, "stand"), (B5(115.9), "present"), (B5(118.6), "wave"), (B5(121.0), "stand")], [(0, "neutral"), (B5(117.5), "happy")],
         x=420, s=1.05)
    show(c, t, B5(116.4), 1100, 260, T("Eu sou o Historiador.", 44, AMBER), anim="fade")
    show(c, t, B5(117.6), 1100, 470, sc(subscribe_btn, t > B5(119.0), s=0.9))
    show(c, t, B5(118.0), 1430, 470, sc(bell, s=0.8), rot=math.sin(t * 18) * 0.2 * max(0, 1 - (t - B5(118.0))))
    show(c, t, B5(118.6), 1100, 720, lambda c: (text(c, "PONTO CEGO", 0, 0, 84, SERIF, INK), line(c, -300, 58, 300, 58, 3, AMBER)),
         anim="fade", d=1.2)
    snow(c, t, 90, 50, 0.6)
    fog(c, t, 980, 0.08)


SCENES = [
    (0.0, 16.7, s01), (16.7, 32.9, s02), (32.9, 46.2, s03), (46.2, 59.1, s04), (59.1, 62.6, s05),
    (62.6, 73.0, s06), (73.0, 89.0, s07), (89.0, 112.2, s08), (112.2, 116.2, s09), (116.2, 141.5, s10),
    (141.5, 159.3, s11), (159.3, 176.9, s12), (176.9, B2(0.0), s13),
    (B2(0.0), B2(10.8), s14), (B2(10.8), B2(29.8), s15), (B2(29.8), B2(42.3), s16), (B2(42.3), B2(59.8), s17),
    (B2(59.8), B2(76.9), s18), (B2(76.9), B2(80.7), s19), (B2(80.7), B2(97.9), s20), (B2(97.9), B2(112.0), s21),
    (B2(112.0), B2(122.5), s22), (B2(122.5), B2(141.5), s23), (B2(141.5), B2(162.0), s24), (B2(162.0), B2(170.3), s25),
    (B2(170.3), B3(0.0), s26),
    (B3(0.0), B3(8.6), s27), (B3(8.6), B3(28.8), s28), (B3(28.8), B3(40.0), s29), (B3(40.0), B3(48.2), s30),
    (B3(48.2), B3(66.2), s31), (B3(66.2), B3(88.3), s32), (B3(88.3), B3(100.5), s33), (B3(100.5), B3(114.7), s34),
    (B3(114.7), B3(127.3), s35), (B3(127.3), B3(151.2), s36), (B3(151.2), B3(160.2), s37), (B3(160.2), B3(181.6), s38),
    (B3(181.6), B3(196.2), s39), (B3(196.2), B4(0.0), s40),
    (B4(0.0), B4(12.0), s41), (B4(12.0), B4(44.4), s42), (B4(44.4), B4(74.4), s43), (B4(74.4), B4(105.0), s44),
    (B4(105.0), B5(0.0), s45),
    (B5(0.0), B5(9.6), s46), (B5(9.6), B5(28.9), s47), (B5(28.9), B5(49.8), s48), (B5(49.8), B5(62.2), s49),
    (B5(62.2), B5(66.8), s50), (B5(66.8), B5(89.1), s51), (B5(89.1), B5(103.6), s52), (B5(103.6), B5(115.4), s53),
    (B5(115.4), 999.0, s54),
]

# Sons: nada automático (sem whoosh em transição, sem som em cada ícone). Só toques sem chiado nos momentos-chave.
SFX_OFF = True
SFX = [(14.0, "tum"), (30.4, "boom"), (44.3, "bell"), (59.4, "boom"), (B2(41.0), "bell"), (B2(77.1), "heartbeat"),
       (B2(110.8), "tum"), (B2(120.9), "boom"), (B2(131.0), "bell"), (B2(177.5), "heartbeat"), (B3(40.3), "heartbeat"),
       (B3(111.9), "boom"), (B3(157.1), "tum"), (B3(192.3), "heartbeat"), (B5(58.6), "boom"), (B5(85.5), "tum"),
       (B5(118.6), "boom")]
