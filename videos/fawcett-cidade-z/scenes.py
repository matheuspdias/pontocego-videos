"""Percy Fawcett e a Cidade de Z — Ponto Cego.
Narração: Pedro Lima - Serious (HeyGen / ElevenLabs v4), 4 blocos com 1 s de silêncio entre eles (~809 s).
Tempos: videos/fawcett-cidade-z/narracao_blocos.txt. B2(x)/B3(x)/B4(x) convertem o tempo local do bloco em tempo absoluto.
"""
from engine import *

O2, O3, O4 = 168.340, 337.908, 559.695


def B2(x):
    return x + O2


def B3(x):
    return x + O3


def B4(x):
    return x + O4


SA = make_proj(-82, -34, -36, 8)                 # América do Sul
MT = make_proj(-62.5, -49.5, -17.8, -9.5)         # Mato Grosso / Alto Xingu
BR = make_proj(-74, -34, -26, 3)                 # Brasil

CUIABA = (-56.1, -15.6)
DHC = (-54.58, -11.72)              # Acampamento do Cavalo Morto (11°43' S, 54°35' O)
RICARDO = (-60.5, -14.6)            # Serra Ricardo Franco
KUHIKUGU = (-53.1, -12.55)          # aprox.
RIO = (-43.2, -22.9)
BAHIA = (-41.5, -12.5)
ROUTE25 = [CUIABA, (-55.7, -14.6), (-55.1, -13.2), DHC]
EAST = [DHC, (-54.0, -11.9), (-53.4, -12.1)]
KULUENE = [(-53.9, -15.6), (-53.6, -14.2), (-53.3, -13.2), (-53.1, -12.3), (-52.9, -12.0)]
RIO_VERDE = [(-60.2, -15.4), (-60.7, -14.3), (-61.3, -13.6)]

FAW = dict(coat=(0.55, 0.48, 0.32), shirt=(0.80, 0.76, 0.62), hat="fedora", hat_col=(0.62, 0.55, 0.38), mustache=True, hair=None)
JACK = dict(coat=(0.62, 0.58, 0.46), shirt=(0.80, 0.78, 0.70), hat="fedora", hat_col=(0.72, 0.66, 0.50), hair=None)
RAL = dict(coat=(0.40, 0.44, 0.48), shirt=(0.70, 0.72, 0.74), hair="tuft")
DOYLE = dict(coat=(0.20, 0.20, 0.24), shirt=(0.86, 0.85, 0.82), mustache=True, hair="tuft")
HAGG = dict(coat=(0.26, 0.20, 0.16), shirt=(0.84, 0.82, 0.78), mustache=True, hat="tophat", hair=None)
NINA = dict(shirt=(0.45, 0.30, 0.38), hair="long")
DYOTT = dict(coat=(0.36, 0.38, 0.30), shirt=(0.78, 0.76, 0.66), hat="pilot", hair=None, mustache=True)
HELP = dict(shirt=(0.52, 0.44, 0.34), hair="tuft")


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


def at_(c, x, y, fn, s=1.0, a=1.0):
    def f(c):
        c.save(); c.translate(x, y); c.scale(s, s); fn(c); c.restore()
    faded(c, a, f)


def forest(c, t, y=1010, moon_xy=(1580, 160), back=True, front=True, seed=5, stars_n=70):
    stars(c, t, stars_n, 560)
    if moon_xy:
        c.save(); c.translate(*moon_xy); moon(c, 48); c.restore()
        glow(c, moon_xy[0], moon_xy[1], 200, ICE, 0.10)
    if back:
        faded(c, 0.55, lambda c: jungle(c, t, y - 150, n=16, h=(240, 380), col=(0.08, 0.12, 0.11), seed=seed + 7, edge=0.2))
    if front:
        jungle(c, t, y + 60, n=11, h=(260, 380), col=(0.09, 0.15, 0.12), seed=seed, edge=0.35)


def ground(c, y=960, col=(0.10, 0.10, 0.09)):
    c.rectangle(0, y, W, H - y); rgb(c, col); c.fill()
    line(c, 0, y, W, y, 3, (0.30, 0.28, 0.22))


def labeled(fn, label, dy=130, size=34, col=INK):
    return group(fn, at(0, dy, T(label, size, col)))


def x_over(c, t, t0, x, y, s=70):
    show(c, t, t0, x, y, lambda c: big_x(c, s, RED, 14), anim="stamp")


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


def sa_map(c, proj, rivers=True, border=True):
    draw_map(c, proj, SOUTH_AMERICA, grid=10)
    if border:
        map_path(c, proj, BR_BO_BORDER, 1, (0.55, 0.55, 0.60), 3, [8, 8])
    if rivers:
        map_path(c, proj, RIVER_AMAZONAS, 1, (0.40, 0.55, 0.66), 4)
        map_path(c, proj, RIVER_XINGU, 1, (0.40, 0.55, 0.66), 3)


def mt_map(c, t):
    draw_map(c, MT, SOUTH_AMERICA, grid=2, land_col=(0.13, 0.18, 0.15))
    map_path(c, MT, BR_BO_BORDER, 1, (0.55, 0.55, 0.60), 3, [8, 8])
    map_path(c, MT, RIVER_XINGU, 1, (0.40, 0.55, 0.66), 4)
    map_path(c, MT, KULUENE, 1, (0.40, 0.55, 0.66), 3)
    map_path(c, MT, RIO_VERDE, 1, (0.40, 0.55, 0.66), 3)
    map_label(c, MT, -52.4, -10.2, "rio Xingu", 26, (0.55, 0.68, 0.78))
    map_label(c, MT, -61.4, -11.6, "BOLÍVIA", 30, (0.55, 0.55, 0.60), SERIF)
    map_label(c, MT, -57.5, -10.6, "BRASIL", 34, (0.55, 0.55, 0.60), SERIF)
    map_point(c, MT, *CUIABA, INK, 8, t, pulse=False)
    map_label(c, MT, *CUIABA, "Cuiabá", 28, INK, dy=34)


def walker(c, t, t0, t1, x0, x1, y, s, kw, fid, alpha=1.0, expr="neutral"):
    k = ease_io(clamp01((t - t0) / max(0.01, t1 - t0)))
    x = x0 + (x1 - x0) * k
    moving = t0 < t < t1
    fig(c, t, x, y, s, poses=[(0, "run" if moving else "stand")], exprs=[(0, expr)], alpha=alpha, fid=fid, **kw)


def z_mark(c, size=260, col=AMBER):
    glow(c, 0, 0, size * 1.6, col, 0.20)
    text(c, "Z", 0, 0, size, SERIF, col)


def glyph_row(c, seed=0, n=7):
    """inscrições desconhecidas (traços)"""
    rnd = random.Random(seed + 3)
    for i in range(n):
        x = -n * 14 + i * 28
        for _ in range(2):
            line(c, x + rnd.uniform(-8, 8), rnd.uniform(-12, 0), x + rnd.uniform(-8, 8), rnd.uniform(0, 12), 3, AMBER)


def card(c, title_s, icon, note=None, w=380, h=440, col=AMBER):
    rrect(c, -w / 2, -h / 2, w, h, 14); fs(c, (0.13, 0.13, 0.15), 5, PARCH2)
    sz = 40
    while sz > 20 and text_w(c, title_s, sz, SERIF) > w - 36:
        sz -= 2
    text(c, title_s, 0, -h / 2 + 50, sz, SERIF, col)
    c.save(); c.translate(0, 20); icon(c); c.restore()
    if note:
        text(c, note, 0, h / 2 - 40, 26, TYPE, INK)


def check(c, r=40):
    circle(c, 0, 0, r, (0.20, 0.42, 0.28), 5)
    c.move_to(-r * 0.45, 0); c.line_to(-r * 0.1, r * 0.35); c.line_to(r * 0.5, -r * 0.35)
    rgb(c, INK); c.set_line_width(8); c.stroke()


# ------------------------------------------------------------------ BLOCO 1: abertura
def s01(c, t):  # 0 - 15.84  a carta na floresta
    forest(c, t)
    show(c, t, 0.3, 960, 110, lambda c: date_stamp(c, "29 DE MAIO DE 1925", 48, AMBER), anim="stamp")
    show(c, t, 4.6, 960, 205, T("Mato Grosso, Brasil", 36), anim="fade")
    glow(c, 1020, 880, 260, AMBER, 0.18 + 0.04 * math.sin(t * 9))
    show(c, t, 0.0, 1020, 960, lambda c: flames(c, t, 90, 70), anim="fade", d=1.0)
    figure(c, t, 1160, 1000, 0.9, poses=[(0, "hold")], exprs=[(0, "think")], appear=5.8, fid=40, **FAW)
    show(c, t, 8.6, 1260, 900, sc(letter, 4, 160, 200, False), anim="pop")
    show(c, t, 7.1, 1160, 540, T("57 anos", 32, AMBER), anim="fade", t1=12.0)
    if t > 12.0:
        figure(c, t, 1480, 1000, 0.82, poses=[(0, "relax")], exprs=[(0, "sad")], appear=13.4, fid=41, **JACK)
        figure(c, t, 1640, 1000, 0.82, poses=[(0, "relax")], exprs=[(0, "worried")], appear=13.6, fid=42, **RAL)
        show(c, t, 14.8, 1560, 560, lambda c: caption_box(c, "doentes", 34), anim="up")
        rnd = random.Random(int(t * 6))
        for i in range(12):
            x = 1100 + rnd.uniform(0, 650); y = 640 + rnd.uniform(0, 260)
            circle(c, x, y, 2.5, INK, 0)
    fog(c, t, 960, 0.06)
    HIST(c, t, [(0, "stand"), (5.8, "point_r"), (12.2, "think")], [(0, "neutral"), (12.2, "worried")], appear=0.6)


def s02(c, t):  # 15.84 - 22.88  a frase
    stars(c, t, 40, 400)
    glow(c, 1050, 560, 520, AMBER, 0.10)
    show(c, t, 15.9, 1050, 560, sc(letter, 8, 620, 700, True), anim="up", d=0.7)
    if t > 19.2:
        rrect(c, 760, 470, 580, 200, 10); rgb(c, (0.05, 0.05, 0.06), 0.55); c.fill()
        typewrite(c, t, 19.23, "“Você não precisa temer", 1050, 530, 44, LYELLOW, 26)
        typewrite(c, t, 20.6, "nenhum fracasso.”", 1050, 600, 44, LYELLOW, 26)
    show(c, t, 21.6, 1050, 990, T("— P. H. Fawcett, à esposa Nina", 30, AMBER), anim="fade")
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=280, s=0.9)
    fog(c, t, 1000, 0.05)


def s03(c, t):  # 22.88 - 31.51  silêncio; entram na mata
    forest(c, t, moon_xy=(1700, 150))
    k = clamp01((t - 26.3) / 4.0)
    for i, (kw, fid, dx) in enumerate([(FAW, 40, 0), (JACK, 41, -150), (RAL, 42, -290)]):
        x = 1100 + dx + k * 520
        fig(c, t, x, 1000, 0.75 - k * 0.2, poses=[(0, "run" if 26.3 < t < 30.3 else "stand")],
            exprs=[(0, "neutral")], alpha=1 - k * 0.92, fid=fid, **kw)
    faded(c, 0.9, lambda c: jungle(c, t, 1080, n=5, h=(380, 520), col=(0.07, 0.11, 0.10), seed=21, edge=0.3) if t > 0 else None)
    show(c, t, 23.9, 960, 140, lambda c: stitle(c, "silêncio", 0, 0, 72, INK, None), anim="fade", d=1.0)
    show(c, t, 28.9, 960, 250, T("nunca mais foram vistos", 40, AMBER), anim="fade")
    fog(c, t, 900, 0.09, 8)


def s04(c, t):  # 31.51 - 43.75  Percy Fawcett e a cidade impossível
    stars(c, t, 70, 600)
    figure(c, t, 760, 1000, 1.0, poses=[(0, "stand"), (33.7, "hips")], exprs=[(0, "neutral"), (33.7, "confident")], appear=31.6, fid=40, **FAW)
    show(c, t, 32.4, 760, 330, lambda c: hl(c, "Percy Fawcett", 0, 0, 52), anim="up")
    if t > 34.9:
        a = clamp01((t - 34.9) / 0.6) * (1 - clamp01((t - 41.8) / 0.6))
        at_(c, 1380, 520, lambda c: (cloud_shape(c, 560, 300), c.save(), c.translate(0, 85), c.scale(0.6, 0.6), ruined_arch(c, 160, 170), c.restore()), a=a)
        show(c, t, 35.0, 1380, 715, T("uma cidade perdida", 34), anim="fade", t1=41.6)
    if t > 37.1:
        for i in range(3):
            fig(c, t, 1180 + i * 200, 1000, 0.6, poses=[(0, "shrug" if i == 1 else "stand")], exprs=[(0, "angry" if i == 0 else "neutral")],
                alpha=clamp01((t - 37.1 - i * 0.2) / 0.4) * (1 - clamp01((t - 41.6) / 0.6)), fid=60 + i, glasses=True, hair=None,
                coat=(0.25, 0.25, 0.28))
        show(c, t, 38.4, 1380, 210, lambda c: caption_box(c, "“não pode existir”", 38), anim="up", t1=41.6)
    show(c, t, 42.5, 1380, 520, sc(z_mark, 300), anim="stamp")
    HIST(c, t, [(0, "present"), (39.9, "point_r")], [(0, "neutral"), (42.6, "shocked")], x=260, s=0.85)
    fog(c, t, 980, 0.05)


def s05(c, t):  # 43.75 - 56.79  título
    forest(c, t, moon_xy=(960, 190))
    show(c, t, 44.0, 960, 330, lambda c: stitle(c, "PERCY FAWCETT", 0, 0, 110, INK, AMBER), anim="fade", d=1.0)
    show(c, t, 45.0, 960, 450, lambda c: stitle(c, "e a Cidade de Z", 0, 0, 64, AMBER, None), anim="fade", d=1.0)
    show(c, t, 49.6, 960, 545, T("um mistério que custou outras vidas", 34), anim="fade", t1=53.6)
    show(c, t, 53.9, 960, 545, T("...e ganhou uma reviravolta", 34, AMBER), anim="fade")
    fog(c, t, 860, 0.10, 8)


def s06(c, t):  # 56.79 - 72.39  quem era
    stars(c, t, 50, 400)
    figure(c, t, 760, 1000, 1.0, poses=[(0, "stand"), (63.0, "hips")], exprs=[(0, "neutral"), (63, "confident")], fid=40, **FAW)
    show(c, t, 58.7, 1400, 150, lambda c: date_stamp(c, "1867", 60, AMBER), anim="stamp")
    show(c, t, 60.8, 1400, 250, T("Torquay, Inglaterra", 36), anim="fade")
    items = [(63.7, 380, "oficial de artilharia"), (66.1, 500, "Ceilão (Sri Lanka)"), (68.8, 620, "cartógrafo")]
    for t0, y, s in items:
        show(c, t, t0, 1400, y, lambda c, s=s: caption_box(c, s, 36), anim="left")
    show(c, t, 68.9, 1580, 830, sc(compass, t, s=0.7), anim="pop")
    show(c, t, 69.0, 1260, 840, sc(old_map, t, False, s=0.5), anim="pop")
    show(c, t, 69.8, 1400, 980, T("Real Sociedade Geográfica • Londres", 30, AMBER), anim="fade")
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=260, s=0.85)


def s07(c, t):  # 72.39 - 84.76  1906, a fronteira
    draw_map(c, SA, SOUTH_AMERICA, grid=10)
    map_path(c, SA, RIVER_AMAZONAS, 1, (0.40, 0.55, 0.66), 4)
    show(c, t, 72.5, 1500, 130, lambda c: date_stamp(c, "1906", 64, AMBER), anim="stamp")
    if t > 78.1:
        p = ease_io(prog(t, 78.1, 2.0))
        map_path(c, SA, BR_BO_BORDER, p, AMBER, 6, [12, 8])
        map_label(c, SA, -66.5, -17.5, "BOLÍVIA", 30, INK, SERIF)
        map_label(c, SA, -50.5, -11.0, "BRASIL", 36, INK, SERIF)
    if t > 81.5:
        glow(c, *SA(-63, -12.5), 230, AMBER, 0.15)
        show(c, t, 81.6, *SA(-63, -6.5), lambda c: caption_box(c, "selva que nenhum mapa mostrava", 32), anim="up")
    show(c, t, 76.9, 1500, 230, T("missão perigosa", 36, RED), anim="fade")


def s08(c, t):  # 84.76 - 93.66  a época da borracha
    stars(c, t, 50, 400)
    forest(c, t, 820, moon_xy=None, front=False)
    river(c, t, 820, 260)
    show(c, t, 85.0, 960, 120, lambda c: stitle(c, "A época da borracha", 0, 0, 60, INK, AMBER), anim="up")
    show(c, t, 87.2, 620, 930, lambda c: caption_box(c, "piranhas", 34), anim="up")
    show(c, t, 88.0, 960, 930, lambda c: caption_box(c, "cobras gigantes", 34), anim="up")
    show(c, t, 89.4, 1360, 930, lambda c: caption_box(c, "homens armados", 34, ), anim="up")
    if t > 90.3:
        show(c, t, 90.4, 960, 300, lambda c: hl(c, "indígenas escravizados nos seringais", 0, 0, 40, PARCH, BLOOD), anim="stamp")
    HIST(c, t, [(0, "stand"), (87, "point_r")], [(0, "worried")], x=240, s=0.8)


def s09(c, t):  # 93.66 - 106.40  resistente
    forest(c, t, moon_xy=(1700, 140))
    xF = 1300 + clamp01((t - 94.0) / 8) * 200
    fig(c, t, xF, 1000, 0.85, poses=[(0, "run")], exprs=[(0, "confident")], fid=40, **FAW)
    for i, (t0, lbl) in enumerate([(98.4, "febre"), (99.1, "fome"), (99.7, "picadas")]):
        x = 600 + i * 220
        fig(c, t, x, 1000, 0.7, poses=[(0, "run"), (t0, "head")], exprs=[(0, "neutral"), (t0, "desperate")], fid=50 + i, **HELP)
        show(c, t, t0, x, 520, T(lbl, 32, RED), anim="pop")
    show(c, t, 94.3, 960, 120, lambda c: hl(c, "resistente de um jeito assustador", 0, 0, 44), anim="up")
    if t > 102.0:
        n = min(7, int((t - 103.8) * 6) + 1) if t > 103.8 else 0
        rrect(c, 760, 200, 400, 120, 12); rgb(c, (0, 0, 0), 0.55); c.fill()
        text(c, f"{n} expedições" if n else "expedições", 960, 260, 50, SERIF, AMBER)
    fog(c, t, 980, 0.06)


def s10(c, t):  # 106.40 - 121.12  1908, Rio Verde
    if t < 113.8:
        mt_map(c, t)
        show(c, t, 106.6, 960, 120, lambda c: date_stamp(c, "1908", 64, AMBER), anim="stamp")
        if t > 110.8:
            p = ease_io(prog(t, 110.8, 2.4))
            map_path(c, MT, RIO_VERDE, p, AMBER, 7)
            show(c, t, 110.9, *MT(-58.6, -13.9), lambda c: caption_box(c, "Rio Verde", 34), anim="up")
        if t > 108.9:
            show(c, t, 108.96, 1500, 230, T("quase uma tragédia", 34, RED), anim="fade")
        return
    stars(c, t, 50, 500)
    forest(c, t, moon_xy=None)
    for i in range(4):
        x = 720 + i * 230
        fig(c, t, x, 1000, 0.75, poses=[(0, "relax")], exprs=[(0, "sad" if i % 2 else "desperate")], fid=50 + i, **HELP)
    fig(c, t, 1700, 1000, 0.8, poses=[(0, "stand")], exprs=[(0, "worried")], fid=40, **FAW)
    show(c, t, 114.2, 960, 130, lambda c: hl(c, "a comida acabou", 0, 0, 52, PARCH, BLOOD), anim="stamp")
    show(c, t, 116.6, 960, 250, T("fracos demais para andar", 36), anim="fade")
    if t > 119.6:
        show(c, t, 119.7, 960, 360, lambda c: caption_box(c, "ameaça de motim", 40), anim="up")
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=260, s=0.82)
    fog(c, t, 980, 0.06)


def s11(c, t):  # 121.12 - 128.80  inferno envenenado; mas chegaram
    stars(c, t, 40, 400)
    forest(c, t, 820, moon_xy=None, front=False)
    river(c, t, 820, 260, (0.10, 0.14, 0.10))
    for i in range(5):
        glow(c, 400 + i * 300, 860 + (i % 2) * 60, 140, (0.45, 0.62, 0.30), 0.10)
    show(c, t, 121.4, 960, 160, lambda c: stitle(c, "“o inferno envenenado”", 0, 0, 64, LGREEN, None), anim="fade", d=0.8)
    if t > 124.3:
        a = clamp01((t - 124.3) / 0.6)
        for i, kw in enumerate([FAW, HELP, HELP]):
            fig(c, t, 1300 + i * 140, 800, 0.6, poses=[(0, "relax" if t < 127.5 else "arms_up")],
                exprs=[(0, "sad" if t < 127.5 else "happy")], alpha=a, fid=40 + i, **kw)
        show(c, t, 124.5, 1440, 380, T("a nascente", 36, AMBER), anim="fade")
    show(c, t, 127.6, 960, 300, lambda c: stitle(c, "Mas chegaram.", 0, 0, 56, AMBER, AMBER), anim="up")
    HIST(c, t, [(0, "stand"), (127.6, "thumb")], [(0, "worried"), (127.6, "confident")], x=260, s=0.82)


def s12(c, t):  # 128.80 - 149.21  Serra Ricardo Franco
    stars(c, t, 90, 520)
    c.save(); c.translate(1600, 160); moon(c, 44); c.restore()
    k = ease_out(prog(t, 132.6, 2.2))
    at_(c, 1150, 860, lambda c: tepui(c, 1100, 380), a=k)
    glow(c, 1150, 520, 600, ICE, 0.05 * k)
    jungle(c, t, 1060, n=12, h=(220, 320), col=(0.09, 0.15, 0.12), seed=9)
    show(c, t, 133.2, 1150, 230, T("paredões verticais • topo achatado", 34), anim="fade", t1=139.5)
    show(c, t, 139.8, 1150, 220, lambda c: hl(c, "Serra Ricardo Franco", 0, 0, 52), anim="up")
    if t > 143.6:
        typewrite(c, t, 143.6, "“um mundo perdido”", 1150, 320, 46, AMBER)
    if t > 145.1:
        a = clamp01((t - 145.1) / 1.2) * 0.75
        at_(c, 1350, 470, lambda c: dinosaur(c, (0.10, 0.12, 0.13)), 0.55, a)
    fog(c, t, 820, 0.10, 8)
    HIST(c, t, [(0, "stand"), (130.2, "point_r"), (141.7, "think")], [(0, "neutral"), (132.8, "shocked"), (141.7, "think")], x=260, s=0.85)


def s13(c, t):  # 149.21 - B2(0.16)  Londres, Conan Doyle, O Mundo Perdido
    stars(c, t, 30, 300)
    if t < 157.9:
        show(c, t, 149.3, 960, 110, T("Londres", 44, AMBER), anim="fade")
        c.save(); c.translate(560, 1000); lectern(c); c.restore()
        fig(c, t, 560, 860, 0.8, poses=[(0, "present"), (151, "point_r")], exprs=[(0, "confident")], fid=40, **FAW)
        for i in range(7):
            x = 900 + i * 140
            kw = DOYLE if i == 3 else dict(coat=(0.22, 0.22, 0.25), hair=None if i % 2 else "tuft")
            fig(c, t, x, 1010, 0.62, exprs=[(0, "neutral"), (152.6, "shocked" if i == 3 else "neutral")], fid=70 + i,
                alpha=clamp01((t - 149.4 - i * 0.1) / 0.4), **kw)
        if t > 154.5:
            glow(c, 900 + 3 * 140, 820, 160, AMBER, 0.25)
            show(c, t, 154.6, 1320, 560, lambda c: hl(c, "Arthur Conan Doyle", 0, 0, 42), anim="up")
            show(c, t, 156.6, 1320, 640, T("criador de Sherlock Holmes", 30), anim="fade")
        return
    show(c, t, 158.0, 760, 560, sc(book, "", BLOOD, s=1.6), anim="drop")
    show(c, t, 160.5, 766, 490, lambda c: (text(c, "O MUNDO", 0, 0, 34, SERIF, LYELLOW), text(c, "PERDIDO", 0, 46, 34, SERIF, LYELLOW)), anim="fade")
    show(c, t, 159.7, 760, 820, lambda c: date_stamp(c, "1912", 48, AMBER), anim="stamp")
    at_(c, 1350, 880, lambda c: tepui(c, 700, 300), a=clamp01((t - 162.6) / 0.8))
    at_(c, 1400, 560, lambda c: dinosaur(c, (0.16, 0.20, 0.18)), 0.7, clamp01((t - 165.0) / 0.8))
    show(c, t, 162.8, 1350, 200, T("planalto isolado onde dinossauros sobrevivem", 32), anim="fade")
    HIST(c, t, [(0, "present")], [(0, "happy")], x=260, s=0.82)
    fog(c, t, 980, 0.05)


# ------------------------------------------------------------------ BLOCO 2: a obsessão
def s14(c, t):  # B2 0.16 - 6.40  não os monstros, as pessoas
    stars(c, t, 60, 500)
    k = clamp01((t - B2(3.6)) / 0.8)
    at_(c, 1150, 800, lambda c: dinosaur(c, (0.16, 0.20, 0.18)), 1.1, 1 - k)
    if t > B2(3.6):
        x_over(c, t, B2(3.2), 1150, 600, 110)
    if t > B2(4.2):
        for i in range(9):
            x = 760 + i * 120
            fig(c, t, x, 1000, 0.55, exprs=[(0, "neutral")], fid=80 + i, alpha=clamp01((t - B2(4.3) - i * 0.08) / 0.4),
                shirt=(0.45 + (i % 3) * 0.08, 0.36, 0.28), hair="long" if i % 3 == 1 else "tuft")
        show(c, t, B2(4.7), 1240, 260, lambda c: stitle(c, "as pessoas", 0, 0, 70, AMBER, AMBER), anim="up")
    HIST(c, t, [(0, "think"), (B2(4.2), "finger_up")], [(0, "think"), (B2(4.2), "confident")], x=280, s=0.88)


def s15(c, t):  # B2 6.40 - 20.40  o deserto verde
    forest(c, t, moon_xy=(1700, 140))
    show(c, t, B2(6.5), 1100, 130, T("a ideia dominante na época:", 34), anim="fade")
    show(c, t, B2(10.2), 1100, 230, lambda c: stitle(c, "“DESERTO VERDE”", 0, 0, 76, LGREEN, None), anim="stamp")
    show(c, t, B2(11.6), 1100, 340, T("pobre demais para uma civilização grande", 34), anim="fade")
    if t > B2(15.6):
        for i, x in enumerate((700, 1250, 1650)):
            show(c, t, B2(16.1) + i * 0.25, x, 990, sc(oca, 150, 100), anim="pop")
        show(c, t, B2(16.3), 1100, 460, lambda c: caption_box(c, "só pequenas aldeias espalhadas", 36), anim="up")
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=280, s=0.88)
    fog(c, t, 980, 0.06)


def s16(c, t):  # B2 20.40 - 39.27  Fawcett não acreditava
    stars(c, t, 60, 500)
    fig(c, t, 640, 1000, 0.95, poses=[(0, "stand"), (B2(20.4), "shrug"), (B2(22.5), "think")], exprs=[(0, "confident")], fid=40, **FAW)
    show(c, t, B2(23.6), 1060, 520, labeled(sc(pot, s=0.9), "cerâmica trabalhada", 70, 30), anim="pop")
    show(c, t, B2(25.4), 1340, 520, labeled(lambda c: (rrect(c, -90, -120, 180, 120, 10), fs(c, (0.12, 0.09, 0.07), 5)),
                                             "terra preta fértil", 70, 30), anim="pop")
    show(c, t, B2(27.5), 1620, 520, labeled(sc(speech, 180, 110, -50, 70), "relatos indígenas", 70, 30), anim="pop")
    if t > B2(31.4):
        a = clamp01((t - B2(31.4)) / 0.6)
        at_(c, 1380, 860, lambda c: (cloud_shape(c, 900, 260),), a=a * 0.9)
        for i in range(5):
            at_(c, 1060 + i * 160, 900, lambda c: oca(c, 140, 95), a=a)
        show(c, t, B2(36.0), 1380, 220, lambda c: hl(c, "uma civilização perdida no tempo", 0, 0, 44), anim="up")
    HIST(c, t, [(0, "stand")], [(0, "think")], x=260, s=0.82)


def s17(c, t):  # B2 39.27 - 67.32  o Manuscrito 512
    stars(c, t, 50, 400)
    if t < B2(51.2):
        show(c, t, B2(39.4), 960, 120, lambda c: stitle(c, "Uma pista", 0, 0, 60, INK, AMBER), anim="up")
        for i in range(5):
            at_(c, 1120 + i * 110, 900, lambda c: book(c, "", (0.30 + i * 0.05, 0.16, 0.12)), 0.8, clamp01((t - B2(42.4)) / 0.5))
        show(c, t, B2(42.5), 1350, 620, T("Biblioteca Nacional • Rio de Janeiro", 32, AMBER), anim="fade")
        show(c, t, B2(46.3), 1100, 400, sc(scroll, 4, 420, 240, "MANUSCRITO 512"), anim="drop")
        show(c, t, B2(48.4), 1100, 260, lambda c: date_stamp(c, "1753", 50, BLOOD), anim="stamp")
        HIST(c, t, [(0, "present"), (B2(46.3), "point_r")], [(0, "neutral"), (B2(46.4), "think")], x=280, s=0.88)
        return
    ground(c, 900, (0.12, 0.11, 0.10))
    show(c, t, B2(51.3), 960, 110, T("bandeirantes • sertão da Bahia", 36, AMBER), anim="fade")
    show(c, t, B2(55.6), 960, 200, lambda c: caption_box(c, "ruínas de uma cidade de pedra", 38), anim="up", t1=B2(62.0))
    if t < B2(63.6):
        k = clamp01((t - B2(51.3)) / 4.0)
        for i in range(3):
            fig(c, t, 1640 - k * 300 + i * 110, 900, 0.6, poses=[(0, "run" if k < 1 else "stand")], exprs=[(0, "neutral" if k < 1 else "shocked")],
                alpha=1 - clamp01((t - B2(63.0)) / 0.6), fid=95 + i, hat="fedora", hat_col=(0.30, 0.24, 0.16), coat=(0.42, 0.34, 0.24), hair=None)
    for i, x in enumerate((560, 820, 1080)):
        show(c, t, B2(55.7) + i * 0.2, x, 900, sc(ruined_arch, 230, 280), anim="up")
    if t > B2(59.6):
        ellipse(c, 1450, 905, 300, 40); fs(c, (0.30, 0.29, 0.27), 4)
    if t > B2(60.4):
        for j in range(3):
            at_(c, 820, 470 + j * 30, lambda c, j=j: glyph_row(c, j), a=clamp01((t - B2(60.4)) / 0.6) * 0.8)
        show(c, t, B2(61.0), 820, 400, T("inscrições desconhecidas", 28, AMBER), anim="fade")
    if t > B2(63.8):
        a = clamp01((t - B2(63.8)) / 0.6)
        at_(c, 1450, 900, lambda c: column(c, 260), a=a)
        fig(c, t, 1450, 640, 0.55, poses=[(0, "point_ru")], exprs=[(0, "neutral")], alpha=a, fid=90, shirt=(0.55, 0.52, 0.46),
            hair=None)
        show(c, t, B2(65.8), 1620, 300, T("norte", 30, AMBER), anim="fade")
    fog(c, t, 900, 0.07)


def s18(c, t):  # B2 67.32 - 74.64  verdadeiro ou fantasia?
    stars(c, t, 40, 400)
    show(c, t, B2(67.4), 960, 450, sc(scroll, 4, 360, 200, "MANUSCRITO 512"), anim="fade")
    show(c, t, B2(70.3), 600, 450, lambda c: caption_box(c, "verdadeiro?", 40), anim="left")
    show(c, t, B2(71.4), 1320, 450, lambda c: caption_box(c, "fantasia?", 40), anim="right")
    for i in range(3):
        fig(c, t, 760 + i * 200, 1000, 0.6, poses=[(0, "think" if i != 1 else "shrug")], exprs=[(0, "think")],
            fid=60 + i, glasses=True, hair=None, coat=(0.25, 0.25, 0.28), alpha=clamp01((t - B2(68.2)) / 0.5))
    show(c, t, B2(72.5), 960, 180, lambda c: hl(c, "Fawcett acreditou", 0, 0, 52), anim="stamp")
    HIST(c, t, [(0, "think")], [(0, "think")], x=260, s=0.82)


def s19(c, t):  # B2 74.64 - 100.21  o ídolo de basalto e o vidente
    stars(c, t, 40, 400)
    if t < B2(89.6):
        fig(c, t, 760, 1000, 0.95, poses=[(0, "stand"), (B2(78.8), "present")], exprs=[(0, "happy")], fid=91, appear=B2(75.7), **HAGG)
        show(c, t, B2(76.9), 760, 360, lambda c: hl(c, "H. Rider Haggard", 0, 0, 44), anim="up")
        show(c, t, B2(77.6), 760, 430, T("escritor, amigo de Fawcett", 28), anim="fade")
        fig(c, t, 1500, 1000, 0.95, poses=[(0, "stand"), (B2(80.2), "hold")], exprs=[(0, "neutral"), (B2(80), "shocked")], fid=40, **FAW)
        if t > B2(79.4):
            k = ease_io(prog(t, B2(79.4), 1.0))
            x = 900 + 450 * k
            at_(c, x, 880, lambda c: idol(c, True, t), 0.7)
        show(c, t, B2(80.4), 1150, 230, lambda c: caption_box(c, "ídolo de basalto negro", 36), anim="up")
        show(c, t, B2(82.2), 1150, 300, T("~25 cm • teria vindo do Brasil", 30, AMBER), anim="fade")
        show(c, t, B2(86.3), 1150, 100, T("Fawcett e o espiritualismo", 34, (0.75, 0.70, 0.85)), anim="fade")
        return
    c.rectangle(0, 0, W, H); rgb(c, (0.03, 0.03, 0.04), 0.7); c.fill()
    show(c, t, B2(89.6), 560, 900, sc(candle, t), anim="fade")
    fig(c, t, 560, 1000, 0.85, poses=[(0, "hold")], exprs=[(0, "think")], fid=92, hat="hood", hat_col=(0.22, 0.18, 0.28),
        coat=(0.22, 0.18, 0.28), hair=None)
    at_(c, 560, 920, lambda c: idol(c, True, t), 0.45)
    if t > B2(91.5):
        a = clamp01((t - B2(91.5)) / 1.0)
        at_(c, 1280, 560, lambda c: (cloud_shape(c, 980, 560),), a=a * 0.9)
    show(c, t, B2(92.4), 1280, 360, T("um continente antigo", 34, AMBER), anim="fade")
    show(c, t, B2(93.9), 1080, 690, sc(temple, 300, 180), anim="pop")
    show(c, t, B2(94.5), 1480, 690, sc(volcano, t, 300, 190), anim="pop")
    show(c, t, B2(96.9), 1280, 920, lambda c: hl(c, "destruída antes do Egito existir", 0, 0, 38, PARCH, BLOOD), anim="stamp")
    fog(c, t, 900, 0.06)


def s20(c, t):  # B2 100.21 - 117.78  mais antigas que o Egito; Z
    stars(c, t, 70, 520)
    show(c, t, B2(100.3), 960, 120, T("hoje, soa como fantasia", 36), anim="fade", t1=B2(105.3))
    if t < B2(110.9):
        show(c, t, B2(105.6), 700, 860, sc(ruined_arch, 240, 300, s=1.2), anim="up")
        show(c, t, B2(106.0), 1250, 860, sc(pyramid, 360, 230), anim="up")
        show(c, t, B2(106.4), 970, 760, lambda c: text(c, ">", 0, 0, 120, SERIF, AMBER), anim="pop")
        show(c, t, B2(107.4), 960, 250, lambda c: caption_box(c, "ruínas mais antigas que as do Egito", 40), anim="up")
        show(c, t, B2(102.4), 960, 250, T("mais uma peça do quebra-cabeça", 34, AMBER), anim="fade", t1=B2(107.2))
    else:
        jungle(c, t, 1060, n=12, h=(260, 380), col=(0.09, 0.15, 0.12), seed=3)
        show(c, t, B2(111.0), 1100, 160, T("um nome de código", 40), anim="fade")
        show(c, t, B2(114.0), 1100, 240, T("uma única letra", 34, AMBER), anim="fade")
        show(c, t, B2(115.9), 1100, 560, sc(z_mark, 340), anim="stamp", d=0.6)
        fog(c, t, 960, 0.08)
    HIST(c, t, [(0, "present"), (B2(116.0), "point_r")], [(0, "neutral"), (B2(116), "shocked")], x=260, s=0.85)


def s21(c, t):  # B2 117.78 - 129.65  a guerra; pressa
    stars(c, t, 40, 400)
    ground(c, 900, (0.12, 0.10, 0.09))
    for i in range(12):
        line(c, i * 170, 900, i * 170 + 90, 860, 4, (0.35, 0.30, 0.24))
    show(c, t, B2(117.9), 960, 130, lambda c: stitle(c, "Primeira Guerra Mundial", 0, 0, 60, INK, BLOOD), anim="up")
    fig(c, t, 960, 990, 0.95, poses=[(0, "stand"), (B2(123.4), "hips")], exprs=[(0, "neutral"), (B2(123.4), "confident")], fid=40,
        coat=(0.36, 0.36, 0.26), shirt=(0.62, 0.60, 0.48), hat="pilot", mustache=True, hair=None)
    show(c, t, B2(122.4), 1400, 450, T("França", 36), anim="fade")
    show(c, t, B2(123.5), 1400, 540, lambda c: hl(c, "tenente-coronel", 0, 0, 42), anim="up")
    if t > B2(124.7):
        show(c, t, B2(126.7), 560, 520, T("mais de 50 anos...", 34), anim="fade")
        show(c, t, B2(128.2), 560, 640, sc(hourglass, t, 3, s=0.6), anim="pop")
        show(c, t, B2(128.3), 560, 780, T("e pressa", 36, RED), anim="fade")


def s22(c, t):  # B2 129.65 - 146.13  1920: a primeira tentativa e o cavalo
    forest(c, t, moon_xy=(1700, 140))
    show(c, t, B2(129.8), 960, 120, lambda c: date_stamp(c, "1920", 60, AMBER), anim="stamp")
    show(c, t, B2(131.9), 960, 220, T("primeira busca por Z", 36), anim="fade")
    show(c, t, B2(134.5), 960, 300, lambda c: caption_box(c, "deu tudo errado", 40), anim="up", t1=B2(139.0))
    for i in range(2):
        a = 1 - clamp01((t - B2(136.0)) / 1.5)
        fig(c, t, 560 - clamp01((t - B2(136.0)) / 3) * 300 + i * 140, 1000, 0.7, poses=[(0, "stand" if t < B2(136) else "run")],
            exprs=[(0, "sad")], alpha=a, fid=50 + i, **HELP)
    fig(c, t, 960, 1000, 0.85, poses=[(0, "stand"), (B2(137.7), "head")], exprs=[(0, "worried"), (B2(137.7), "desperate")], fid=40, **FAW)
    show(c, t, B2(137.8), 960, 600, T("febre", 32, RED), anim="pop", t1=B2(140))
    if t < B2(141.5):
        at_(c, 1400, 1000, lambda c: horse(c), 0.9, 1 - clamp01((t - B2(140.2)) / 1.2) * 0.6)
    else:
        a = clamp01((t - B2(141.5)) / 0.8)
        at_(c, 1400, 1010, lambda c: wood_cross(c, 150), 1.0, a)
        glow(c, 1400, 930, 220, AMBER, 0.18 * a)
        show(c, t, B2(142.4), 1400, 640, lambda c: caption_box(c, "numa clareira", 34), anim="up")
    if t > B2(143.5):
        show(c, t, B2(143.6), 1400, 500, lambda c: hl(c, "guarde esse lugar", 0, 0, 44, PARCH, BLOOD), anim="stamp")
    fog(c, t, 980, 0.07)


def s23(c, t):  # B2 146.13 - 156.02  sozinho na Bahia
    sa_map(c, BR, rivers=False, border=False)
    map_point(c, BR, *BAHIA, AMBER, 10, t)
    map_label(c, BR, *BAHIA, "sertão da Bahia", 30, AMBER, dy=-36)
    map_point(c, BR, *RIO, INK, 7, t, pulse=False)
    map_label(c, BR, *RIO, "Rio", 26, INK, dy=30)
    show(c, t, B2(146.3), 960, 110, lambda c: date_stamp(c, "1921", 56, AMBER), anim="stamp")
    show(c, t, B2(147.7), 560, 260, lambda c: caption_box(c, "sozinho", 38), anim="up")
    show(c, t, B2(151.9), 560, 360, sc(calendar, "3", s=0.8), anim="pop")
    show(c, t, B2(152.4), 560, 470, T("três meses", 32), anim="fade")
    show(c, t, B2(154.4), 560, 570, lambda c: hl(c, "mãos vazias", 0, 0, 42, PARCH, BLOOD), anim="stamp")


def s24(c, t):  # B2 156.02 - B3(0.13)  riam dele; uma última vez
    stars(c, t, 70, 520)
    if t < B2(162.9):
        for i in range(3):
            fig(c, t, 1100 + i * 200, 1000, 0.65, poses=[(0, "point_l" if i == 0 else "shrug")], exprs=[(0, "grin")], fid=60 + i,
                glasses=True, hair=None, coat=(0.25, 0.25, 0.28))
        fig(c, t, 640, 1000, 0.9, poses=[(0, "stand")], exprs=[(0, "sad")], fid=40, **FAW)
        show(c, t, B2(156.2), 1300, 300, lambda c: caption_box(c, "os cientistas riam dele", 36), anim="up")
        show(c, t, B2(158.0), 1300, 400, labeled(sc(bills, 1, s=0.6), "dinheiro acabou", 70, 30), anim="pop")
        x_over(c, t, B2(158.6), 1300, 400, 60)
        show(c, t, B2(160.9), 1300, 560, T("“perdeu o juízo”", 34, AMBER), anim="fade")
        HIST(c, t, [(0, "stand")], [(0, "sad")], x=240, s=0.8)
        return
    forest(c, t, moon_xy=(1640, 150))
    fig(c, t, 760, 1000, 1.0, poses=[(0, "stand"), (B2(165.4), "point_r")], exprs=[(0, "think"), (B2(165.4), "confident")], fid=40, **FAW)
    glow(c, 1300, 760, 420, AMBER, 0.06)
    show(c, t, B2(165.5), 1300, 200, lambda c: stitle(c, "uma última vez", 0, 0, 66, AMBER, AMBER), anim="fade", d=0.9)
    fog(c, t, 900, 0.09, 8)


# ------------------------------------------------------------------ BLOCO 3: a última expedição
def s25(c, t):  # B3 0.13 - 13.60  1925: dinheiro e jornais
    stars(c, t, 50, 400)
    show(c, t, B3(0.2), 960, 120, lambda c: date_stamp(c, "1925", 64, AMBER), anim="stamp")
    show(c, t, B3(4.6), 960, 230, T("Fawcett conseguiu", 40), anim="fade")
    show(c, t, B3(6.5), 620, 560, labeled(group(at(-50, 0, sc(coin, s=1.1)), at(40, -20, sc(coin, s=1.1)), at(0, 30, sc(coin, s=1.1))), "financiadores de Londres", 120, 30), anim="pop")
    for i in range(4):
        show(c, t, B3(9.0) + i * 0.35, 1150 + i * 130, 520 + (i % 2) * 70,
             sc(newspaper, "FAWCETT", "rumo à selva", s=0.55), anim="drop", rot=(i - 1.5) * 0.06)
    show(c, t, B3(11.0), 1340, 860, T("jornais do mundo inteiro", 32, AMBER), anim="fade")
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=240, s=0.8)


def s26(c, t):  # B3 13.60 - 30.72  o grupo pequeno
    forest(c, t, moon_xy=(1700, 140), front=False)
    ground(c, 1000, (0.09, 0.10, 0.09))
    show(c, t, B3(13.7), 1150, 120, lambda c: stitle(c, "um grupo pequeno", 0, 0, 60, INK, AMBER), anim="up")
    show(c, t, B3(16.3), 1150, 210, T("muito pequeno", 34, AMBER), anim="fade")
    if t > B3(17.4) and t < B3(22.5):
        for i in range(10):
            fig(c, t, 700 + i * 110, 1000, 0.45, exprs=[(0, "neutral")], fid=100 + i, alpha=0.5, **HELP)
        x_over(c, t, B3(20.4), 1200, 820, 120)
        show(c, t, B3(19.5), 1200, 420, T("expedição grande = comida demais", 30), anim="fade")
    if t > B3(22.5):
        figure(c, t, 900, 1000, 1.0, poses=[(0, "hips")], exprs=[(0, "confident")], fid=40, appear=B3(22.6), **FAW)
        figure(c, t, 1200, 1000, 0.92, poses=[(0, "stand"), (B3(26), "wave")], exprs=[(0, "happy")], fid=41, appear=B3(25.9), **JACK)
        figure(c, t, 1470, 1000, 0.92, poses=[(0, "stand")], exprs=[(0, "happy")], fid=42, appear=B3(29.4), **RAL)
        show(c, t, B3(22.8), 900, 470, T("Percy, 57", 32, AMBER), anim="fade")
        show(c, t, B3(26.0), 1200, 430, T("Jack, o filho", 32, AMBER), anim="fade")
        show(c, t, B3(27.3), 1200, 475, T("pouco mais de 20 anos", 26), anim="fade")
        show(c, t, B3(29.5), 1500, 360, T("Raleigh Rimell", 32, AMBER), anim="fade")
        show(c, t, B3(29.7), 1500, 405, T("o melhor amigo", 26), anim="fade")
    HIST(c, t, [(0, "present")], [(0, "neutral")], x=260, s=0.82)


def s27(c, t):  # B3 30.72 - 44.16  "não mandem resgate"
    stars(c, t, 50, 400)
    show(c, t, B3(30.8), 1150, 440, sc(letter, 5, 400, 460, True), anim="up")
    if t > B3(35.6):
        rrect(c, 900, 360, 500, 150, 10); rgb(c, (0.05, 0.05, 0.06), 0.6); c.fill()
        typewrite(c, t, B3(35.6), "se não voltarmos,", 1150, 410, 38, LYELLOW)
        typewrite(c, t, B3(37.2), "não mandem ninguém", 1150, 465, 38, LYELLOW)
    if t > B3(39.1):
        for i in range(5):
            fig(c, t, 900 + i * 120, 1000, 0.5, exprs=[(0, "neutral")], fid=110 + i, alpha=0.6, hat="pilot", hair=None,
                coat=(0.30, 0.34, 0.30))
        show(c, t, B3(39.2), 1150, 740, lambda c: caption_box(c, "nenhuma equipe de resgate", 34), anim="up")
        x_over(c, t, B3(40.1), 1150, 900, 140)
    show(c, t, B3(42.4), 1150, 100, T("para que ninguém morresse por causa dele", 32, AMBER), anim="fade")
    HIST(c, t, [(0, "present"), (B3(35.6), "point_r")], [(0, "neutral"), (B3(35.6), "worried")], x=280, s=0.88)


def s28(c, t):  # B3 44.16 - 68.16  saída de Cuiabá; cartas e jornais
    mt_map(c, t)
    show(c, t, B3(44.3), 960, 110, lambda c: date_stamp(c, "20 DE ABRIL DE 1925", 46, AMBER), anim="stamp")
    if t > B3(48.2):
        map_point(c, MT, *CUIABA, AMBER, 11, t)
    show(c, t, B3(49.2), 1500, 260, T("2 ajudantes • cavalos • mulas • 2 cães", 28), anim="fade")
    if t > B3(53.4):
        p = ease_io(prog(t, B3(53.4), 3.5))
        map_path(c, MT, ROUTE25, p * 0.85, AMBER, 6, [14, 9])
        x, y = path_end(MT, ROUTE25, p * 0.85)
        circle(c, x, y, 9, AMBER, 3)
    show(c, t, B3(55.2), *MT(-52.0, -12.6), lambda c: caption_box(c, "Alto Xingu", 34), anim="up")
    if t > B3(56.8):
        k = (t - B3(56.8)) % 2.6 / 2.6
        x0, y0 = MT(-55.3, -13.6); x1, y1 = MT(*CUIABA)
        at_(c, x0 + (x1 - x0) * k, y0 + (y1 - y0) * k, lambda c: envelope(c), 0.5, math.sin(math.pi * k))
    if t > B3(59.7):
        rrect(c, 1180, 560, 560, 420, 14); rgb(c, (0.05, 0.05, 0.06), 0.7); c.fill()
        show(c, t, B3(60.5), 1460, 700, lambda c: text(c, "cartas atravessam o oceano", 0, 0, 30, TYPE, INK), anim="fade")
        for i in range(3):
            show(c, t, B3(62.6) + i * 0.4, 1330 + i * 130, 850, sc(newspaper, "FAWCETT", "", s=0.4), anim="drop", rot=(i - 1) * 0.08)


def s29(c, t):  # B3 68.16 - 84.88  a jornada dura
    forest(c, t, moon_xy=None)
    rnd = random.Random(int(t * 7))
    for i in range(26):
        circle(c, rnd.uniform(500, 1900), rnd.uniform(500, 950), 2.6, INK, 0)
    show(c, t, B3(68.3), 1150, 120, lambda c: stitle(c, "a jornada estava sendo dura", 0, 0, 52, INK, AMBER), anim="up")
    show(c, t, B3(70.4), 1600, 260, T("insetos sem trégua", 30), anim="fade")
    if t > B3(72.3):
        at_(c, 1700, 1000, lambda c: horse(c, (0.32, 0.25, 0.20)), 0.6, 0.8)
        show(c, t, B3(72.5), 1700, 760, T("animais doentes", 28), anim="fade")
    xF = 900 + clamp01((t - B3(79.2)) / 4.5) * 380
    fig(c, t, xF, 1000, 0.85, poses=[(0, "stand"), (B3(79.2), "run")], exprs=[(0, "confident")], fid=40, **FAW)
    fig(c, t, 760, 1000, 0.8, poses=[(0, "relax")], exprs=[(0, "sad")], fid=41, **JACK)
    fig(c, t, 600, 1000, 0.8, poses=[(0, "relax"), (B3(74.0), "head")], exprs=[(0, "desperate")], fid=42, **RAL)
    show(c, t, B3(74.6), 560, 560, lambda c: caption_box(c, "pé infeccionado", 30), anim="up")
    show(c, t, B3(77.3), 850, 520, lambda c: caption_box(c, "abatido", 30), anim="up")
    show(c, t, B3(81.3), 1300, 360, T("57 anos • na frente de todos", 30, AMBER), anim="fade")
    fog(c, t, 980, 0.06)


def s30(c, t):  # B3 84.88 - 95.84  a mesma clareira
    forest(c, t, moon_xy=(1660, 150))
    a = clamp01((t - B3(86.0)) / 1.0)
    at_(c, 1150, 1010, lambda c: wood_cross(c, 160), 1.0, a)
    glow(c, 1150, 930, 260, AMBER, 0.18 * a)
    show(c, t, B3(87.4), 1150, 560, T("a mesma clareira", 36), anim="fade", t1=B3(92.0))
    show(c, t, B3(90.3), 1150, 640, T("onde o cavalo morreu, 5 anos antes", 30, AMBER), anim="fade", t1=B3(92.0))
    show(c, t, B3(93.6), 1150, 220, lambda c: stitle(c, "ACAMPAMENTO DO", 0, 0, 56, INK, AMBER), anim="stamp")
    show(c, t, B3(94.6), 1150, 300, lambda c: stitle(c, "CAVALO MORTO", 0, 0, 72, AMBER, AMBER), anim="stamp")
    HIST(c, t, [(0, "stand"), (B3(87), "point_r")], [(0, "think"), (B3(93.6), "worried")], x=300, s=0.9)
    fog(c, t, 960, 0.08)


def s31(c, t):  # B3 95.84 - 109.75  só os três
    forest(c, t, moon_xy=(1660, 150))
    at_(c, 1550, 1010, lambda c: wood_cross(c, 140), 0.9)
    k = clamp01((t - B3(97.2)) / 4)
    for i in range(2):
        fig(c, t, 620 - k * 500 + i * 140, 1000, 0.7, poses=[(0, "run" if 0 < k < 1 else "stand")], exprs=[(0, "neutral")],
            alpha=1 - k, fid=50 + i, **HELP)
    if t > B3(97.2):
        at_(c, 900 - k * 600, 1000, lambda c: horse(c), 0.6, 1 - k)
    show(c, t, B3(99.0), 700, 520, T("ajudantes, animais e cartas voltam", 28), anim="fade", t1=B3(101.3))
    for i, (kw, fid, t0) in enumerate([(FAW, 40, B3(103.9)), (JACK, 41, B3(104.5)), (RAL, 42, B3(105.1))]):
        figure(c, t, 1050 + i * 160, 1000, 0.85, poses=[(0, "stand")], exprs=[(0, "neutral")], fid=fid, appear=B3(101.4), **kw)
        show(c, t, t0, 1050 + i * 160, 520, T(["pai", "filho", "amigo"][i], 30, AMBER), anim="fade")
    show(c, t, B3(103.2), 1210, 160, lambda c: stitle(c, "só os três", 0, 0, 66, INK, AMBER), anim="up")
    show(c, t, B3(107.2), 1210, 260, T("território que nenhum mapa mostrava", 32), anim="fade")
    fog(c, t, 960, 0.08)


def s32(c, t):  # B3 109.75 - 128.24  a carta a Nina
    stars(c, t, 40, 300)
    glow(c, 1100, 540, 560, AMBER, 0.08)
    show(c, t, B3(109.8), 1100, 540, sc(letter, 9, 640, 760, True), anim="up", d=0.7)
    show(c, t, B3(110.9), 1100, 120, T("para Nina", 38, AMBER), anim="fade")
    if t > B3(113.3):
        rrect(c, 800, 290, 600, 110, 10); rgb(c, (0.05, 0.05, 0.06), 0.6); c.fill()
        typewrite(c, t, B3(113.4), "11° 43' S  •  54° 35' O", 1100, 345, 42, LYELLOW)
    if t > B3(124.4):
        rrect(c, 790, 560, 620, 190, 10); rgb(c, (0.05, 0.05, 0.06), 0.65); c.fill()
        typewrite(c, t, B3(124.48), "“Você não precisa temer", 1100, 620, 42, LYELLOW, 26)
        typewrite(c, t, B3(125.9), "nenhum fracasso.”", 1100, 690, 42, LYELLOW, 26)
    HIST(c, t, [(0, "present"), (B3(113.4), "point_r")], [(0, "neutral"), (B3(117), "think")], x=280, s=0.88)


def s33(c, t):  # B3 128.24 - 149.30  a última notícia; Nina espera
    stars(c, t, 60, 500)
    if t < B3(136.3):
        show(c, t, B3(128.3), 960, 330, lambda c: date_stamp(c, "29 DE MAIO DE 1925", 58, AMBER), anim="stamp")
        show(c, t, B3(132.4), 960, 480, lambda c: stitle(c, "a última notícia", 0, 0, 70, INK, BLOOD), anim="fade", d=0.8)
        fog(c, t, 900, 0.09, 8)
        return
    c.rectangle(1160, 260, 420, 380); fs(c, (0.06, 0.08, 0.12), 8, (0.45, 0.33, 0.20))
    line(c, 1370, 260, 1370, 640, 6, (0.45, 0.33, 0.20)); line(c, 1160, 450, 1580, 450, 6, (0.45, 0.33, 0.20))
    glow(c, 1370, 450, 260, ICE, 0.06)
    fig(c, t, 1370, 1000, 0.95, poses=[(0, "stand")], exprs=[(0, "sad")], fid=120, **NINA)
    show(c, t, B3(136.5), 1370, 180, lambda c: hl(c, "Nina Fawcett", 0, 0, 40), anim="fade")
    labels = [(B3(136.5), "meses"), (B3(138.7), "1 ano"), (B3(140.2), "2 anos")]
    for i, (t0, s) in enumerate(labels):
        show(c, t, t0, 620, 360 + i * 120, lambda c, s=s: caption_box(c, s, 36), anim="left")
    show(c, t, B3(144.6), 900, 820, T("acreditou até o fim que eles voltariam", 30, AMBER), anim="fade")
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=260, s=0.82)


def s34(c, t):  # B3 149.30 - 166.96  as buscas; Dyott 1928
    stars(c, t, 50, 400)
    ground(c, 990, (0.10, 0.10, 0.09))
    show(c, t, B3(149.4), 960, 110, T("apesar do pedido de Fawcett...", 36), anim="fade", t1=B3(152.6))
    show(c, t, B3(151.4), 960, 190, lambda c: stitle(c, "as buscas começaram", 0, 0, 58, AMBER, None), anim="up", t1=B3(152.6))
    if t > B3(152.7):
        show(c, t, B3(152.8), 1500, 120, lambda c: date_stamp(c, "1928", 56, AMBER), anim="stamp")
        figure(c, t, 560, 1000, 1.0, poses=[(0, "hips"), (B3(159.6), "present")], exprs=[(0, "confident")], fid=130,
               appear=B3(158.3), **DYOTT)
        show(c, t, B3(158.4), 560, 360, lambda c: hl(c, "George Dyott", 0, 0, 44), anim="up")
        show(c, t, B3(154.9), 1050, 220, T("apoio da Real Sociedade Geográfica", 30), anim="fade")
    if t > B3(161.4):
        for i in range(8):
            fig(c, t, 880 + i * 110, 1000, 0.45, exprs=[(0, "neutral")], fid=131 + i, alpha=clamp01((t - B3(161.5) - i * 0.06) / 0.3),
                hat="pilot" if i % 2 else None, hair=None if i % 2 else "tuft", coat=(0.34, 0.36, 0.30))
        show(c, t, B3(162.8), 1300, 640, sc(horse, (0.42, 0.36, 0.30), s=0.5), anim="pop")
        show(c, t, B3(163.8), 1600, 720, sc(radio_tower, t, s=0.35), anim="pop")
        show(c, t, B3(164.8), 1780, 820, labeled(lambda c: (rrect(c, -50, -40, 100, 70, 8), fs(c, DGRAY, 5), circle(c, 0, -5, 22, (0.3, 0.4, 0.5), 4)),
                                                 "câmera", 60, 24), anim="pop")
        show(c, t, B3(159.9), 1300, 360, T("o oposto de Fawcett", 34, AMBER), anim="fade")


def s35(c, t):  # B3 166.96 - 182.67  a placa de metal; rio Kuluene
    if t < B3(179.2):
        stars(c, t, 40, 400)
        forest(c, t, moon_xy=None, front=False)
        show(c, t, B3(167.1), 960, 120, T("numa aldeia da região...", 36), anim="fade")
        glow(c, 960, 560, 300, AMBER, 0.14)
        show(c, t, B3(171.4), 960, 560, lambda c: (rrect(c, -160, -70, 320, 140, 14), fs(c, (0.72, 0.56, 0.26), 6),
                                                   text(c, "LONDRES", 0, 0, 40, SERIF, DARKTXT)), anim="pop")
        show(c, t, B3(170.0), 960, 760, T("uma pequena placa de metal", 34), anim="fade")
        show(c, t, B3(174.5), 960, 840, T("do mesmo fornecedor das caixas de Fawcett", 32, AMBER), anim="fade")
        show(c, t, B3(178.1), 960, 300, lambda c: hl(c, "uma pista", 0, 0, 48), anim="stamp")
        HIST(c, t, [(0, "stand"), (B3(171.5), "point_r")], [(0, "think"), (B3(174.6), "shocked")], x=280, s=0.85)
        return
    mt_map(c, t)
    map_point(c, MT, *DHC, AMBER, 9, t, pulse=False)
    map_label(c, MT, *DHC, "Cavalo Morto", 26, AMBER, dy=-30)
    p = ease_io(prog(t, B3(179.3), 1.6))
    map_path(c, MT, EAST, p, AMBER, 6, [14, 9])
    if t > B3(180.6):
        glow(c, *MT(-53.25, -13.2), 200, ICE, 0.22)
        show(c, t, B3(180.7), *MT(-55.5, -14.3), lambda c: caption_box(c, "rio Kuluene", 34), anim="up")


def s36(c, t):  # B3 182.67 - 202.35  contradições, boatos, fuga noturna
    stars(c, t, 80, 520)
    c.save(); c.translate(1640, 150); moon(c, 44); c.restore()
    if t < B3(193.6):
        forest(c, t, moon_xy=None)
        show(c, t, B3(182.8), 960, 120, T("quanto mais Dyott perguntava...", 36), anim="fade")
        show(c, t, B3(186.2), 960, 210, lambda c: caption_box(c, "histórias contraditórias", 38), anim="up")
        show(c, t, B3(187.9), 960, 300, T("cada povo culpava outro", 32, AMBER), anim="fade")
        if t > B3(190.1):
            show(c, t, B3(191.4), 1200, 520, sc(tombstone, "?"), anim="drop")
            show(c, t, B3(190.2), 1200, 760, T("boatos: a próxima cova seria a dele", 30, RED), anim="fade")
        fig(c, t, 640, 1000, 0.95, poses=[(0, "think"), (B3(190.1), "stand")], exprs=[(0, "think"), (B3(190.1), "worried")], fid=130, **DYOTT)
        return
    forest(c, t, 840, moon_xy=None, front=False)
    river(c, t, 840, 240)
    k = clamp01((t - B3(194.0)) / 7.0)
    at_(c, 600 + k * 900, 880, lambda c: canoe(c), 1.0)
    for i in range(3):
        fig(c, t, 520 + k * 900 + i * 80, 870, 0.38, poses=[(0, "hold")], exprs=[(0, "worried")], fid=131 + i, **DYOTT)
    for i in range(3):
        at_(c, 360 + i * 90, 830, lambda c: (rrect(c, -36, -50, 72, 50, 6), fs(c, (0.40, 0.31, 0.20), 4)), 1.0)
    show(c, t, B3(194.0), 960, 160, lambda c: stitle(c, "fuga à noite", 0, 0, 62, INK, BLOOD), anim="up")
    show(c, t, B3(198.3), 400, 680, T("equipamento abandonado", 26), anim="fade")
    show(c, t, B3(199.6), 960, 260, T("voltaram sem respostas", 34, AMBER), anim="fade")


def s37(c, t):  # B3 202.35 - B4(0.08)  outros vieram; até 100 mortes
    forest(c, t, moon_xy=(1700, 140), front=False)
    ground(c, 1000, (0.08, 0.09, 0.08))
    tags = [(B3(204.3), "aventureiros"), (B3(205.4), "jornalistas"), (B3(206.6), "místicos"), (B3(207.6), "curiosos")]
    for i, (t0, s) in enumerate(tags):
        x = 660 + i * 300
        a = 1 - 0.75 * clamp01((t - B3(209.0) - i * 0.25) / 1.0)
        fig(c, t, x, 1000, 0.7, exprs=[(0, "neutral")], fid=140 + i, alpha=a * clamp01((t - t0) / 0.3),
            hat=["fedora", "tophat", "hood", None][i], hair=None if i < 3 else "tuft", coat=(0.30 + i * 0.05, 0.28, 0.24))
        show(c, t, t0, x, 600, T(s, 28, AMBER), anim="fade")
    show(c, t, B3(209.6), 1100, 150, lambda c: caption_box(c, "alguns também desapareceram", 38), anim="up")
    if t > B3(210.8):
        show(c, t, B3(212.0), 1100, 290, lambda c: hl(c, "até 100 mortes?", 0, 0, 52, PARCH, BLOOD), anim="stamp")
        show(c, t, B3(216.4), 1100, 380, T("o número exato ninguém sabe", 30), anim="fade")
    fog(c, t, 960, 0.08, 8)
    HIST(c, t, [(0, "stand"), (B3(217.7), "finger_up")], [(0, "sad"), (B3(217.7), "think")], x=260, s=0.82)


# ------------------------------------------------------------------ BLOCO 4: pistas, teorias e a cidade
def s38(c, t):  # B4 0.08 - 18.40  1951: os ossos
    stars(c, t, 50, 400)
    show(c, t, B4(0.2), 960, 110, lambda c: date_stamp(c, "1951", 60, AMBER), anim="stamp")
    show(c, t, B4(5.4), 960, 210, T("uma notícia que parecia encerrar o caso", 34), anim="fade")
    figure(c, t, 700, 1000, 0.95, poses=[(0, "stand"), (B4(13.4), "present")], exprs=[(0, "confident")], fid=150, appear=B4(8.5),
           glasses=True, hair="tuft", shirt=(0.72, 0.66, 0.52), coat=(0.50, 0.44, 0.32))
    show(c, t, B4(8.7), 700, 360, lambda c: hl(c, "Orlando Villas-Bôas", 0, 0, 42), anim="up")
    show(c, t, B4(11.0), 700, 430, T("sertanista e defensor indígena", 28), anim="fade")
    if t > B4(14.7):
        rrect(c, 1080, 560, 600, 300, 14); fs(c, (0.20, 0.15, 0.10), 6, (0.50, 0.38, 0.24))
        show(c, t, B4(14.8), 1380, 700, sc(bone, 380), anim="pop")
        show(c, t, B4(15.2), 1380, 470, T("“os ossos de Fawcett”", 36, AMBER), anim="fade")
        show(c, t, B4(17.4), 1380, 920, T("território Kalapalo", 30), anim="fade")


def s39(c, t):  # B4 18.40 - 38.04  a análise em Londres: não era ele
    stars(c, t, 40, 300)
    show(c, t, B4(18.5), 960, 110, T("Real Instituto Antropológico • Londres", 34, AMBER), anim="fade")
    show(c, t, B4(20.4), 1600, 300, sc(magnifier, s=0.9), anim="pop")
    if t > B4(25.8):
        base = 900
        hF, hB = 520, 520 * (1 - 0.15 / 1.85)
        k1 = ease_out(prog(t, B4(25.9), 0.8)); k2 = ease_out(prog(t, B4(28.4), 0.8))
        c.rectangle(560, base - hF * k1, 120, hF * k1); fs(c, AMBER, 5)
        text(c, "Fawcett", 620, base + 40, 30, TYPE, AMBER)
        text(c, "> 1,80 m", 620, base - hF * k1 - 30, 28, TYPE, INK) if k1 > 0.9 else None
        if t > B4(28.4):
            c.rectangle(780, base - hB * k2, 120, hB * k2); fs(c, (0.62, 0.60, 0.56), 5)
            text(c, "esqueleto", 840, base + 40, 30, TYPE, INK)
            show(c, t, B4(30.0), 1000, base - hF + 20, T("15 cm mais baixo", 28, RED), anim="fade")
            line(c, 760, base - hF, 1000, base - hF, 2, RED)
    if t > B4(31.8):
        show(c, t, B4(31.9), 1300, 760, sc(denture), anim="pop")
        show(c, t, B4(33.5), 1560, 760, sc(denture, (0.80, 0.78, 0.70)), anim="pop")
        show(c, t, B4(33.9), 1430, 760, lambda c: neq(c, 40, RED, 10), anim="pop")
        show(c, t, B4(34.0), 1430, 880, T("a arcada não batia", 28), anim="fade")
    show(c, t, B4(36.8), 1150, 300, lambda c: stitle(c, "NÃO ERA ELE", 0, 0, 84, RED, BLOOD), anim="stamp")


def s40(c, t):  # B4 38.04 - 49.03  1998, Benedict Allen
    forest(c, t, moon_xy=(1700, 140))
    show(c, t, B4(39.3), 960, 110, lambda c: date_stamp(c, "1998", 56, AMBER), anim="stamp")
    figure(c, t, 700, 1000, 0.9, poses=[(0, "stand"), (B4(44.5), "think")], exprs=[(0, "neutral")], fid=160, appear=B4(41.0),
           shirt=(0.40, 0.50, 0.44), hair="tuft")
    show(c, t, B4(42.2), 700, 380, lambda c: hl(c, "Benedict Allen", 0, 0, 40), anim="up")
    show(c, t, B4(42.9), 700, 450, T("explorador inglês", 28), anim="fade")
    figure(c, t, 1250, 1000, 0.9, poses=[(0, "stand"), (B4(45.4), "present_l")], exprs=[(0, "neutral")], fid=161, appear=B4(43.8),
           shirt=(0.55, 0.42, 0.30), hair="long")
    show(c, t, B4(44.8), 1250, 400, T("um ancião Kalapalo", 30, AMBER), anim="fade")
    if t > B4(46.0):
        show(c, t, B4(46.1), 1500, 560, lambda c: (speech(c, 420, 150, -150, 110), text(c, "eram do meu avô", 0, 0, 36, HAND, INK)), anim="pop")
    fog(c, t, 980, 0.06)


def s41(c, t):  # B4 49.03 - 65.57  outras pistas: instrumento e anel
    stars(c, t, 60, 500)
    show(c, t, B4(49.1), 960, 110, T("outras pistas apareceram", 38), anim="fade")
    show(c, t, B4(51.7), 640, 820, labeled(theodolite, "instrumento de medição • anos 30", 70, 28), anim="up")
    show(c, t, B4(55.4), 1320, 620, sc(signet_ring, s=1.4), anim="pop")
    show(c, t, B4(55.5), 1320, 420, lambda c: date_stamp(c, "1979", 46, AMBER), anim="stamp", t1=B4(60.9))
    show(c, t, B4(58.5), 1320, 820, T("anel reconhecido pela família", 30), anim="fade")
    if t > B4(61.1):
        c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.45 * clamp01((t - B4(61.1)) / 0.8)); c.fill()
        show(c, t, B4(61.2), 960, 330, T("objetos saíram da floresta...", 40), anim="fade")
        show(c, t, B4(63.7), 960, 430, lambda c: stitle(c, "mas nunca os homens", 0, 0, 64, AMBER, AMBER), anim="up")


def s42(c, t):  # B4 65.57 - 87.52  teoria 1: a floresta
    stars(c, t, 50, 400)
    show(c, t, B4(65.6), 1100, 120, lambda c: stitle(c, "O que aconteceu com os três?", 0, 0, 56, INK, AMBER), anim="up")
    if t > B4(69.9):
        show(c, t, B4(70.0), 1100, 520, lambda c: card(c, "TEORIA 1", lambda c: (c.save(), c.translate(0, 120), jungle_tree(c, 260), c.restore()),
                                                      "a floresta", 420, 480), anim="pop")
        show(c, t, B4(71.0), 1100, 830, T("a mais provável para a maioria", 30, AMBER), anim="fade")
        for i, (t0, s) in enumerate([(B4(76.08), "fome"), (B4(76.72), "doença"), (B4(77.44), "exaustão")]):
            show(c, t, t0, 1560, 360 + i * 110, lambda c, s=s: caption_box(c, s, 36), anim="left")
        show(c, t, B4(80.2), 1560, 720, T("2 doentes • a pé • sem guias", 28), anim="fade")
        show(c, t, B4(84.3), 1100, 960, T("a selva não precisava de vilões", 34), anim="fade")
    HIST(c, t, [(0, "think"), (B4(70), "present")], [(0, "think"), (B4(70), "neutral")], x=300, s=0.9)


def s43(c, t):  # B4 87.52 - 109.59  teoria 2: a história dos Kalapalo
    forest(c, t, moon_xy=(1700, 140), front=False)
    ground(c, 1000, (0.08, 0.09, 0.08))
    show(c, t, B4(87.6), 960, 110, lambda c: hl(c, "TEORIA 2 • a memória dos Kalapalo", 0, 0, 40), anim="up")
    show(c, t, B4(91.1), 960, 190, T("passada de geração em geração", 30), anim="fade", t1=B4(96.0))
    for i, x in enumerate((420, 640)):
        at_(c, x, 1000, lambda c: oca(c, 220, 150), 1.0, clamp01((t - B4(92.8)) / 0.5))
    if t > B4(93.6):
        for i, kw in enumerate([FAW, JACK, RAL]):
            k = clamp01((t - B4(100.7)) / 2.0)
            fig(c, t, 900 + i * 120 + k * 260, 1000, 0.62, poses=[(0, "run" if 0 < k < 1 else "stand")], exprs=[(0, "neutral")],
                alpha=1 - k * 0.9, fid=40 + i, **kw)
    show(c, t, B4(96.1), 760, 560, lambda c: caption_box(c, "avisados: o leste é perigoso", 34), anim="up")
    if t > B4(97.6):
        arrow_draw(c, t, B4(97.6), 1200, 760, 1700, 760, d=0.6, col=AMBER)
        show(c, t, B4(97.7), 1450, 700, T("leste", 30, AMBER), anim="fade")
    if t > B4(102.6):
        days = min(5, int((t - B4(102.6)) / 0.5) + 1)
        fade = 1 - clamp01((t - B4(108.6)) / 0.6)
        for d in range(days):
            smoke(c, t, 1300 + d * 110, 760, 360, 0.24 * fade, d)
        show(c, t, B4(102.7), 1520, 300, T("5 dias de fumaça", 32, AMBER), anim="fade", t1=B4(108.4))
    if t > B4(108.7):
        show(c, t, B4(108.76), 1520, 300, lambda c: stitle(c, "a fumaça sumiu", 0, 0, 52, INK, BLOOD), anim="fade")
    fog(c, t, 980, 0.07)


def s44(c, t):  # B4 109.59 - 125.28  teoria 3: nunca quis voltar
    stars(c, t, 60, 500)
    show(c, t, B4(109.7), 1100, 520, lambda c: card(c, "TEORIA 3", lambda c: (c.save(), c.translate(0, 70), idol(c, True, t), c.restore()),
                                                  "não quis voltar?", 420, 480, (0.75, 0.70, 0.85)), anim="pop")
    show(c, t, B4(112.2), 1100, 120, T("o lado místico de Fawcett", 36, (0.75, 0.70, 0.85)), anim="fade")
    show(c, t, B4(117.8), 1100, 840, lambda c: caption_box(c, "fundar uma comunidade na selva", 32), anim="up")
    if t > B4(120.7):
        show(c, t, B4(120.8), 1600, 520, lambda c: hl(c, "nenhuma prova", 0, 0, 44, PARCH, BLOOD), anim="stamp")
        show(c, t, B4(123.0), 1100, 960, T("um boato que atravessou o século", 28), anim="fade")
    HIST(c, t, [(0, "shrug"), (B4(113.6), "think")], [(0, "think")], x=300, s=0.9)


def s45(c, t):  # B4 125.28 - 141.07  a reviravolta; Heckenberger e os Kuikuro
    stars(c, t, 70, 500)
    if t < B4(128.3):
        show(c, t, B4(125.4), 960, 480, lambda c: stitle(c, "a parte que ninguém esperava", 0, 0, 64, AMBER, AMBER), anim="fade", d=0.9)
        fog(c, t, 900, 0.10, 8)
        return
    forest(c, t, moon_xy=None)
    figure(c, t, 760, 1000, 0.95, poses=[(0, "stand"), (B4(134.7), "point_r")], exprs=[(0, "confident")], fid=170, appear=B4(130.0),
           glasses=True, hat="fedora", hat_col=(0.55, 0.52, 0.42), shirt=(0.62, 0.66, 0.60), hair=None)
    show(c, t, B4(131.4), 760, 360, lambda c: hl(c, "Michael Heckenberger", 0, 0, 40), anim="up")
    show(c, t, B4(132.3), 760, 430, T("arqueólogo • Univ. da Flórida", 28), anim="fade")
    show(c, t, B4(128.5), 1450, 150, T("a partir dos anos 90", 32, AMBER), anim="fade")
    for i in range(3):
        fig(c, t, 1220 + i * 150, 1000, 0.75, exprs=[(0, "neutral")], fid=171 + i, appear=B4(136.3) + i * 0.15,
            shirt=(0.55, 0.40 + i * 0.03, 0.28), hair="long" if i == 1 else "tuft")
    show(c, t, B4(136.5), 1370, 520, T("com o povo Kuikuro", 32, AMBER), anim="fade")
    show(c, t, B4(137.5), 1370, 300, lambda c: caption_box(c, "a região para onde Fawcett ia", 34), anim="up")


def plaza_village(c, t, k=1.0, r=120):
    """aldeia circular vista de cima: vala, paliçada, praça e casas"""
    c.new_sub_path(); c.arc(0, 0, r + 40, 0, 2 * math.pi); rgb(c, (0.20, 0.16, 0.10), 0.9 * k); c.set_line_width(14); c.stroke()
    c.new_sub_path(); c.arc(0, 0, r + 22, 0, 2 * math.pi); rgb(c, AMBER, 0.8 * k); c.set_line_width(3); c.set_dash([6, 6]); c.stroke(); c.set_dash([])
    circle(c, 0, 0, r * 0.55, (0.32, 0.28, 0.20), 3)
    for i in range(12):
        a = i / 12 * 2 * math.pi
        circle(c, math.cos(a) * r * 0.82, math.sin(a) * r * 0.82, 13, (0.46, 0.38, 0.22), 3)


def s46(c, t):  # B4 141.07 - 166.11  o que eles encontraram
    c.rectangle(0, 0, W, H); rgb(c, (0.07, 0.11, 0.08)); c.fill()
    rnd = random.Random(4)
    for i in range(90):
        circle(c, rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(18, 38), (0.09, 0.15, 0.11), 0)
    show(c, t, B4(141.2), 960, 90, T("escondido debaixo da vegetação...", 34), anim="fade", t1=B4(145.6))
    show(c, t, B4(145.3), 960, 90, lambda c: stitle(c, "algo enorme", 0, 0, 60, AMBER, AMBER), anim="fade")
    V = [(520, 420), (1420, 380), (980, 760), (1640, 820), (360, 860)]
    if t > B4(152.4):
        p = ease_io(prog(t, B4(152.4), 2.4))
        for (x1, y1), (x2, y2) in [(V[0], V[1]), (V[0], V[2]), (V[2], V[3]), (V[2], V[4]), (V[1], V[3])]:
            line(c, x1, y1, x1 + (x2 - x1) * p, y1 + (y2 - y1) * p, 16, (0.36, 0.30, 0.20))
            line(c, x1, y1, x1 + (x2 - x1) * p, y1 + (y2 - y1) * p, 3, AMBER)
        show(c, t, B4(154.6), 960, 1010, lambda c: caption_box(c, "estradas de até 50 m de largura", 32), anim="up", t1=B4(158.1))
    for i, (x, y) in enumerate(V):
        t0 = B4(146.2) + i * 0.3
        if t > t0:
            c.save(); c.translate(x, y); plaza_village(c, t, clamp01((t - t0) / 0.5), 110 if i else 140); c.restore()
    show(c, t, B4(146.3), 960, 1010, lambda c: caption_box(c, "aldeias com valas e paliçadas", 32), anim="up", t1=B4(149.9))
    if t > B4(149.2):
        glow(c, 980, 760, 120, AMBER, 0.2)
        show(c, t, B4(150.1), 960, 1010, lambda c: caption_box(c, "praças de até 150 m", 32), anim="up", t1=B4(152.3))
    if t > B4(158.3):
        line(c, 1000, 820, 1600, 840, 6, (0.40, 0.55, 0.66))
        show(c, t, B4(158.4), 960, 1010, lambda c: caption_box(c, "canais • áreas de cultivo • terra preta fértil", 32), anim="up")
    show(c, t, B4(163.7), 960, 180, T("onde muita gente viveu por muito tempo", 32), anim="fade")


def s47(c, t):  # B4 166.11 - 183.80  Science 2008; 50 mil pessoas
    stars(c, t, 40, 300)
    show(c, t, B4(166.2), 620, 140, lambda c: date_stamp(c, "2008", 56, AMBER), anim="stamp")
    show(c, t, B4(167.7), 620, 420, lambda c: (rrect(c, -150, -190, 300, 380, 8), fs(c, (0.86, 0.84, 0.78), 5),
                                               text(c, "Science", 0, -130, 44, SERIF, BLOOD), line(c, -120, -90, 120, -90, 3, DARKTXT),
                                               [line(c, -120, -60 + i * 30, 110 - (i % 3) * 30, -60 + i * 30, 4, (0.5, 0.48, 0.44)) for i in range(8)]),
         anim="drop")
    show(c, t, B4(171.8), 1300, 180, T("Kuhikugu e outros sítios", 34, AMBER), anim="fade")
    if t > B4(173.5):
        n = min(50, int((t - B4(173.5)) * 30))
        for i in range(n):
            x = 1020 + (i % 10) * 60; y = 330 + (i // 10) * 90
            circle(c, x, y - 22, 12, INK, 0); line(c, x, y - 10, x, y + 20, 6)
        text(c, "50 mil pessoas ou mais", 1290, 820, 44, SERIF, AMBER) if t > B4(174.3) else None
    if t > B4(178.1):
        show(c, t, B4(179.9), 1290, 920, lambda c: caption_box(c, "esvaziada após a chegada dos europeus e suas doenças", 30), anim="up")


def s48(c, t):  # B4 183.80 - 195.87  cidades-jardim
    stars(c, t, 40, 300)
    show(c, t, B4(183.9), 560, 560, labeled(group(at(-110, 0, sc(ruined_arch, 160, 200)), at(90, 0, sc(column, 200))), "cidade de pedra", 70, 30),
         anim="pop")
    x_over(c, t, B4(187.2), 560, 460, 120)
    if t > B4(188.8):
        a = clamp01((t - B4(188.8)) / 0.8)
        at_(c, 1350, 640, lambda c: (jungle(c, t, 0, 700, 6, (180, 260), (0.12, 0.20, 0.15), 8),), a=a)
        for i in range(4):
            at_(c, 1150 + i * 140, 700, lambda c: oca(c, 120, 80), a=a)
        show(c, t, B4(190.8), 1350, 220, lambda c: hl(c, "cidades-jardim", 0, 0, 56), anim="stamp")
        show(c, t, B4(192.9), 1350, 820, T("terra e madeira", 32, AMBER), anim="fade")
    if t > B4(194.9):
        faded(c, clamp01((t - B4(194.9)) / 0.9), lambda c: jungle(c, t, 1080, n=12, h=(300, 440), col=(0.09, 0.15, 0.12), seed=12))
    HIST(c, t, [(0, "present")], [(0, "neutral"), (B4(190.8), "happy")], x=260, s=0.8) if t < B4(194.9) else None


def s49(c, t):  # B4 195.87 - 209.24  lidar; Bolívia e Equador
    if t < B4(199.6):
        stars(c, t, 60, 400)
        jungle(c, t, 1040, n=13, h=(260, 380), col=(0.10, 0.17, 0.14), seed=6)
        x = 300 + (t - B4(195.9)) * 300
        c.save(); c.translate(x, 260); airplane(c); c.restore()
        sonar_beam(c, t, x, 300, 640, 0.35, ICE)
        show(c, t, B4(197.8), 960, 110, T("scanners a laser em aviões", 36, ICE), anim="fade")
        return
    sa_map(c, SA)
    for i, (lon, lat, s, t0) in enumerate([(-64.9, -14.8, "Bolívia", B4(202.1)), (-78.1, -2.3, "Equador", B4(202.8)),
                                           (-53.1, -12.55, "Alto Xingu", B4(200.0))]):
        if t > t0:
            map_point(c, SA, lon, lat, AMBER, 11, t)
            map_label(c, SA, lon, lat, s, 30, AMBER, dy=-34)
    if t > B4(203.6):
        rnd = random.Random(2)
        a = clamp01((t - B4(203.6)) / 2)
        for i in range(70):
            lon, lat = rnd.uniform(-75, -48), rnd.uniform(-16, -1)
            x, y = SA(lon, lat)
            circle(c, x, y, 4, AMBER, 0) if rnd.random() < a else None
        show(c, t, B4(206.0), 1450, 900, lambda c: caption_box(c, "estava lá o tempo todo", 36), anim="up")


def s50(c, t):  # B4 209.24 - 220.99  errado sobre..., certo sobre a ideia
    stars(c, t, 50, 400)
    rows = [(B4(210.36), "a cidade de pedra", False), (B4(211.88), "a Atlântida", False), (B4(213.3), "o caminho", None),
            (B4(215.4), "a ideia principal", True)]
    for i, (t0, s, ok) in enumerate(rows):
        y = 270 + i * 150
        show(c, t, t0, 1100, y, lambda c, s=s: text(c, s, 0, 0, 44, SERIF, INK if ok is not True else AMBER), anim="left")
        if ok is False:
            show(c, t, t0 + 0.3, 1520, y, sc(x_icon, 34), anim="pop")
        elif ok is None:
            show(c, t, t0 + 0.3, 1520, y, sc(qmark, 70, AMBER), anim="pop")
        else:
            show(c, t, t0 + 0.3, 1520, y, sc(check, 36), anim="pop")
    show(c, t, B4(217.3), 1100, 900, T("e foi ela que o levou para dentro da floresta", 32, AMBER), anim="fade")
    HIST(c, t, [(0, "think"), (B4(215.4), "finger_up")], [(0, "think"), (B4(215.4), "confident")], x=300, s=0.9)


def s51(c, t):  # B4 220.99 - 233.00  nunca encontrados
    forest(c, t, moon_xy=(1640, 150))
    at_(c, 1150, 1010, lambda c: wood_cross(c, 150), 1.0, 0.8)
    for i, (kw, fid, t0) in enumerate([(FAW, 40, B4(221.5)), (JACK, 41, B4(224.5)), (RAL, 42, B4(225.7))]):
        a = 0.55 * clamp01((t - t0) / 0.5) * (1 - clamp01((t - t0 - 1.2) / 1.6))
        fig(c, t, 1350 + i * 160, 1000, 0.8, exprs=[(0, "neutral")], alpha=a, fid=fid, **kw)
    show(c, t, B4(222.6), 960, 140, lambda c: stitle(c, "nunca foram encontrados", 0, 0, 60, INK, None), anim="fade", d=0.9)
    show(c, t, B4(229.4), 960, 240, T("a floresta guardou o último capítulo", 34, AMBER), anim="fade")
    fog(c, t, 900, 0.12, 9)
    HIST(c, t, [(0, "stand")], [(0, "sad")], x=280, s=0.88)


def s52(c, t):  # B4 233.00 - 243.64  e você?
    stars(c, t, 50, 400)
    show(c, t, B4(233.0), 1150, 120, lambda c: stitle(c, "E você?", 0, 0, 70, INK, AMBER), anim="up")
    opts = [(B4(235.88), "a floresta", lambda c: (c.save(), c.translate(0, 120), jungle_tree(c, 230), c.restore())),
            (B4(236.84), "um encontro", lambda c: (c.save(), c.translate(0, 60), smoke(c, t, 0, 60, 200, 0.4), c.restore())),
            (B4(238.84), "não quis voltar", lambda c: (c.save(), c.translate(0, 30), z_mark(c, 140), c.restore()))]
    for i, (t0, s, ic) in enumerate(opts):
        show(c, t, t0, 760 + i * 380, 520, lambda c, s=s, ic=ic: card(c, s.upper(), ic, None, 330, 380), anim="pop")
    show(c, t, B4(241.4), 1140, 880, lambda c: (speech(c, 760, 140, -260, 120), text(c, "deixe sua teoria nos comentários", 0, 0, 40, HAND, INK)),
         anim="pop")
    HIST(c, t, [(0, "point_r"), (B4(241.4), "present")], [(0, "think"), (B4(241.4), "happy")], x=280, s=0.9)


def s53(c, t):  # B4 243.64 - fim  encerramento
    stars(c, t, 80, 700)
    HIST(c, t, [(0, "stand"), (B4(243.7), "present"), (B4(246.4), "wave"), (B4(248.6), "stand")], [(0, "happy")], x=400, s=1.05)
    show(c, t, B4(244.3), 1150, 220, lambda c: stitle(c, "o Historiador", 0, 0, 56, AMBER, None), anim="fade")
    show(c, t, B4(246.3), 1150, 520, sc(subscribe_btn, t > B4(247.6), s=0.9))
    show(c, t, B4(246.7), 1480, 520, sc(bell, s=0.8), rot=math.sin(t * 18) * 0.2 * max(0, 1 - (t - B4(246.7))))
    show(c, t, B4(245.5), 1150, 760, lambda c: (text(c, "PONTO CEGO", 0, 0, 88, SERIF, INK), line(c, -320, 60, 320, 60, 3, AMBER)),
         anim="fade", d=1.2)
    fog(c, t, 1000, 0.07)


SCENES = [
    (0.0, 15.84, s01), (15.84, 22.88, s02), (22.88, 31.51, s03), (31.51, 43.75, s04), (43.75, 56.79, s05),
    (56.79, 72.39, s06), (72.39, 84.76, s07), (84.76, 93.66, s08), (93.66, 106.40, s09), (106.40, 121.12, s10),
    (121.12, 128.80, s11), (128.80, 149.21, s12), (149.21, B2(0.16), s13),
    (B2(0.16), B2(6.40), s14), (B2(6.40), B2(20.40), s15), (B2(20.40), B2(39.27), s16), (B2(39.27), B2(67.32), s17),
    (B2(67.32), B2(74.64), s18), (B2(74.64), B2(100.21), s19), (B2(100.21), B2(117.78), s20), (B2(117.78), B2(129.65), s21),
    (B2(129.65), B2(146.13), s22), (B2(146.13), B2(156.02), s23), (B2(156.02), B3(0.13), s24),
    (B3(0.13), B3(13.60), s25), (B3(13.60), B3(30.72), s26), (B3(30.72), B3(44.16), s27), (B3(44.16), B3(68.16), s28),
    (B3(68.16), B3(84.88), s29), (B3(84.88), B3(95.84), s30), (B3(95.84), B3(109.75), s31), (B3(109.75), B3(128.24), s32),
    (B3(128.24), B3(149.30), s33), (B3(149.30), B3(166.96), s34), (B3(166.96), B3(182.67), s35), (B3(182.67), B3(202.35), s36),
    (B3(202.35), B4(0.08), s37),
    (B4(0.08), B4(18.40), s38), (B4(18.40), B4(38.04), s39), (B4(38.04), B4(49.03), s40), (B4(49.03), B4(65.57), s41),
    (B4(65.57), B4(87.52), s42), (B4(87.52), B4(109.59), s43), (B4(109.59), B4(125.28), s44), (B4(125.28), B4(141.07), s45),
    (B4(141.07), B4(166.11), s46), (B4(166.11), B4(183.80), s47), (B4(183.80), B4(195.87), s48), (B4(195.87), B4(209.24), s49),
    (B4(209.24), B4(220.99), s50), (B4(220.99), B4(233.00), s51), (B4(233.00), B4(243.64), s52), (B4(243.64), 999.0, s53),
]

# Sons: nada automático (sem whoosh em transição, sem som em cada ícone). Só alguns toques sem chiado nos momentos-chave.
SFX_OFF = True
SFX = [(24.0, "heartbeat"), (42.6, "boom"), (108.96, "tum"), (139.9, "tum"), (B2(116.0), "boom"), (B2(141.5), "heartbeat"),
       (B3(93.6), "tum"), (B3(132.4), "boom"), (B3(193.9), "heartbeat"), (B4(36.8), "tum"), (B4(108.76), "heartbeat"),
       (B4(125.3), "boom"), (B4(221.0), "bell"), (B4(245.5), "tum")]
