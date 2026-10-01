"""O Desaparecimento do Voo MH370 — Ponto Cego.
Narração: Pedro Lima - Serious (HeyGen / ElevenLabs v4), 4 blocos com 1 s de silêncio entre eles (405,2 s).
Tempos absolutos tirados de videos/mh370/transcricao.txt.
"""
from engine import *

SEA = make_proj(91, 113, -2, 13)          # Sudeste Asiático
SEA2 = make_proj(93.5, 106.5, 0.5, 9.5)    # zoom na volta do avião
IO = make_proj(28, 128, -46, 22)          # Oceano Índico

KUL = (101.7, 2.75)
IGARI = (103.6, 6.9)
PENANG = (100.3, 5.4)
LAST_RADAR = (96.4, 6.7)
ROUTE_OUT = [KUL, IGARI]
ROUTE_BACK = [IGARI, (102.3, 6.2), PENANG, (98.6, 6.0), LAST_RADAR]
ARC = [(106, -8), (104, -15), (101, -22), (98, -28), (95, -33), (92, -38), (88, -43)]
SEARCH = [(90, -41.5), (95, -35.5), (101, -29.5), (103.5, -31.5), (97.5, -37.5), (92.5, -43.5)]
DEBRIS = [((35.5, -22.0), "Moçambique"), ((31.5, -29.5), "África do Sul"), ((39.5, -7.0), "Tanzânia"),
          ((57.5, -20.3), "Maurício")]
REUNION = (55.5, -21.1)


def HIST(c, t, poses, exprs, appear=None, x=300, y=1010, s=0.95, **kw):
    historiador(c, t, x, y, s, poses, exprs, appear=appear, look=1, **kw)


def ocean_bg(c, t, y=560, deep=False):
    """céu noturno + mar"""
    stars(c, t, 60, y - 40)
    g = cairo.LinearGradient(0, y, 0, H)
    g.add_color_stop_rgb(0, 0.07, 0.12, 0.18)
    g.add_color_stop_rgb(1, 0.02, 0.04, 0.07)
    c.rectangle(0, y, W, H - y); c.set_source(g); c.fill()
    for i in range(16):
        x = i * 140 + (t * 25) % 140 - 140
        c.move_to(x, y); c.curve_to(x + 35, y - 12, x + 70, y - 12, x + 105, y)
    rgb(c, BLUE); c.set_line_width(4); c.stroke()


def x_over(c, t, t0, x, y, s=70):
    show(c, t, t0, x, y, lambda c: big_x(c, s, RED, 14), anim="stamp")


# ------------------------------------------------------------------ 0:00 abertura
def s01(c, t):  # 0 - 8
    stars(c, t, 90, 900)
    c.save(); c.translate(1500, 190); moon(c, 55); c.restore()
    k = clamp01(t / 8.0)
    x, y = -200 + k * 2300, 520 - k * 160
    blink = int(t * 2) % 2 == 0
    c.save(); c.translate(x, y); c.scale(0.55, 0.55); airplane(c, (0.55, 0.58, 0.62))
    circle(c, 190, 0, 9, RED if blink else BLOOD, 0); c.restore()
    if blink:
        glow(c, x + 104, y, 60, RED, 0.5)
    show(c, t, 3.3, 1180, 820, lambda c: caption_box(c, "239 pessoas a bordo", 46), anim="up")
    fog(c, t, 980, 0.06)
    HIST(c, t, [(0, "stand")], [(0, "neutral"), (3.3, "sad")], appear=1.2)


def s02(c, t):  # 8 - 14 sem socorro / explosão / destroços
    ocean_bg(c, t, 760)
    items = [(lambda c: (speech(c, 220, 120, -60, 110), text(c, "SOS", 0, 0, 60, SERIF, RED)), "pedido de socorro", 760, 8.08),
             (lambda c: flames(c, t, 180, 150), "explosão", 1180, 9.92),
             (lambda c: (sc(flaperon, s=0.55)(c)), "destroços", 1600, 11.28)]
    for fn, lab, x, t0 in items:
        show(c, t, t0, x, 430, group(fn, at(0, 150, T(lab, 40))))
        x_over(c, t, t0 + 0.5, x, 420, 95)
    HIST(c, t, [(0, "stand"), (8.1, "shrug")], [(0, "worried")])


def s03(c, t):  # 14 - 20.3 ninguém sabe onde está
    ocean_bg(c, t, 520)
    c.save(); c.translate(1150, 520); sonar_ship(c, t); c.restore()
    sonar_beam(c, t, 1150, 560, 520)
    c.save(); c.translate(960, 1080); seabed(c, t, 0); c.restore()
    show(c, t, 17.3, 1150, 220, lambda c: stitle(c, "Onde ele está?", 0, 0, 70, INK, AMBER), anim="up", d=0.8)
    HIST(c, t, [(0, "think")], [(0, "think")])
    fog(c, t, 600, 0.05)


def s04(c, t):  # 20.3 - 25 título
    stars(c, t, 110, 1080)
    c.save(); c.translate(960, 1150); mountains(c, 2400, 180, False, (0.08, 0.10, 0.14)); c.restore()
    show(c, t, 20.32, 960, 470, lambda c: (text(c, "O DESAPARECIMENTO DO", 0, -95, 46, TYPE, AMBER),
                                           stitle(c, "VOO MH370", 0, 10, 150, INK, AMBER)), anim="fade", d=1.2)
    show(c, t, 21.6, 960, 640, lambda c: (line(c, -380, 0, 380, 0, 3, AMBER)), anim="fade")
    fog(c, t, 900, 0.08)


# ------------------------------------------------------------------ 0:25 a noite do voo
def s05(c, t):  # 25 - 38.7
    stars(c, t, 70, 600)
    c.rectangle(0, 860, W, 220); rgb(c, (0.10, 0.11, 0.13)); c.fill()
    c.set_dash([40, 30]); line(c, 0, 930, W, 930, 6, LYELLOW); c.set_dash([])
    for i in range(12):
        circle(c, 80 + i * 160, 875, 5, AMBER, 0)
    show(c, t, 25.0, 960, 120, lambda c: date_stamp(c, "8 DE MARÇO DE 2014", 54, RED), anim="stamp")
    typewrite(c, t, 27.4, "Kuala Lumpur, Malásia", 960, 215, 44, INK)
    if t > 29.4:
        k = ease_io(clamp01((t - 29.4) / 6.0))
        x = 650 + k * 1250
        y = 830 - max(0, k - 0.25) * 680
        ang = -0.28 if k > 0.25 else 0
        c.save(); c.translate(x, y); c.rotate(ang); c.scale(0.7, 0.7); airplane(c); c.restore()
    show(c, t, 29.6, 1580, 420, sc(clock, 0.7, s=0.9))
    show(c, t, 30.2, 1580, 540, T("00h42", 44, AMBER))
    show(c, t, 33.4, 1100, 330, lambda c: caption_box(c, "Kuala Lumpur  >  Pequim", 44), anim="up")
    show(c, t, 36.3, 1550, 690, group(sc(hourglass, t, s=0.7), at(0, 120, T("6 horas de voo", 40))))
    HIST(c, t, [(0, "stand"), (29.4, "point_ru")], [(0, "neutral")], appear=25.2)


def s06(c, t):  # 38.7 - 50.2 passageiros
    chinese = lambda i: RED if (i % 24) < 13 and i >= 12 else (AMBER if i < 12 else LGRAY)
    hi = (lambda i: chinese(i)) if t > 43.0 else (lambda i: AMBER if i < 12 else LGRAY)
    c.save(); c.translate(1080, 300); crowd(c, t, 38.8, 239, 24, 50, hi, 2.4, 0.2); c.restore()
    show(c, t, 39.2, 520, 170, lambda c: caption_box(c, "227 passageiros", 42), anim="up")
    show(c, t, 41.4, 960, 170, lambda c: caption_box(c, "12 tripulantes", 42, None), anim="up")
    show(c, t, 43.2, 1450, 170, lambda c: (caption_box(c, "mais da metade: China", 42)), anim="up")
    show(c, t, 45.8, 1080, 960, lambda c: text(c, "famílias  •  empresários  •  artistas", 0, 0, 44, TYPE, INK), anim="fade")
    HIST(c, t, [(0, "stand"), (45.8, "present")], [(0, "neutral"), (43.2, "sad")], x=230)


def s07(c, t):  # 50.2 - 58.9 tripulação
    pilot(c, t, 620, 940, 1.15, [(0, "stand"), (50.4, "hips")], [(0, "neutral")], appear=50.2)
    show(c, t, 50.6, 620, 170, lambda c: (text(c, "Capitão", 0, -40, 40, TYPE, AMBER), text(c, "Zaharie Ahmad Shah", 0, 15, 54, SERIF, INK)), anim="up")
    show(c, t, 53.2, 620, 300, lambda c: caption_box(c, "mais de 18 mil horas de voo", 38), anim="up")
    pilot(c, t, 1300, 940, 1.1, [(0, "stand")], [(0, "neutral")], appear=55.7, fid=7)
    show(c, t, 55.9, 1300, 170, lambda c: (text(c, "Copiloto", 0, -40, 40, TYPE, AMBER), text(c, "Fariq Abdul Hamid", 0, 15, 54, SERIF, INK)), anim="up")
    fog(c, t, 1000, 0.05)


def s08(c, t):  # 58.9 - 67.0 tudo normal, rumo norte
    draw_map(c, SEA, grid=5)
    map_label(c, SEA, 110.5, 9.5, "Mar da China", 34, ICE)
    map_label(c, SEA, 110.5, 8.7, "Meridional", 34, ICE)
    map_label(c, SEA, 101.4, 4.0, "MALÁSIA", 30, LGREEN)
    map_label(c, SEA, 106.0, 12.8, "VIETNÃ", 30, LGREEN)
    map_point(c, SEA, *KUL, t=t)
    map_label(c, SEA, *KUL, "Kuala Lumpur", 28, dy=40)
    p = clamp01((t - 59.5) / 7.0)
    ext = [KUL, IGARI, (106.5, 11.5)]
    map_path(c, SEA, ext, p, AMBER, 4, [10, 8])
    plane_on_path(c, SEA, ext, max(0.001, p))
    show(c, t, 59.0, 1450, 960, lambda c: caption_box(c, "tudo normal", 40), anim="up")
    x, y = SEA(108.5, 13.5)
    arrow_draw(c, t, 63.9, x - 40, y + 40, x + 60, y - 70, col=AMBER)
    show(c, t, 63.9, x + 120, y - 90, T("rumo a Pequim", 34, AMBER), anim="fade")


# ------------------------------------------------------------------ 1:07 boa noite
def s09(c, t):  # 67.0 - 86.4
    stars(c, t, 60, 500)
    c.save(); c.translate(1500, 760); radio_tower(c, t); c.restore()
    show(c, t, 67.2, 1500, 1000, T("controle de tráfego aéreo", 38), anim="fade")
    typewrite(c, t, 67.3, "01h19  •  entrando no espaço aéreo do Vietnã", 960, 120, 40, AMBER)
    show(c, t, 74.4, 860, 400, lambda c: (speech(c, 900, 230, 400, 210)), anim="pop")
    typewrite(c, t, 76.37, "\"Good night, Malaysian three seven zero.\"", 860, 380, 40, INK, cps=24)
    show(c, t, 78.9, 860, 450, T("Boa noite, Malaysian três sete zero.", 36, (0.72, 0.72, 0.72)), anim="fade")
    show(c, t, 81.4, 960, 700, lambda c: stitle(c, "As últimas palavras do MH370", 0, 0, 58, INK, AMBER), anim="up", d=0.8)
    HIST(c, t, [(0, "stand"), (74.4, "think"), (81.4, "stand")], [(0, "neutral"), (81.4, "sad")])
    fog(c, t, 980, 0.05)


def s10(c, t):  # 86.4 - 98.1 transponder some
    c.save(); c.translate(1150, 540); c.scale(1.7, 1.7); radar(c, t, blip=False)
    if t < 92.84:
        circle(c, 60, -50, 10, (0.5, 1, 0.6), 0)
        text(c, "MH370", 125, -50, 26, TYPE, (0.5, 1, 0.6))
    else:
        a = 1 - prog(t, 92.84, 1.2)
        if a > 0:
            rgb(c, (0.5, 1, 0.6), a); c.new_sub_path(); c.arc(60, -50, 10, 0, 6.3); c.fill()
    c.restore()
    show(c, t, 87.8, 960, 120, lambda c: caption_box(c, "01h21  •  o transponder para de funcionar", 42), anim="up")
    show(c, t, 92.9, 1150, 960, lambda c: stitle(c, "sumiu da tela", 0, 0, 64, RED), anim="up")
    HIST(c, t, [(0, "stand"), (92.9, "head")], [(0, "neutral"), (92.9, "shocked")])


def s11(c, t):  # 98.1 - 109.1 Malásia x Vietnã, horas passam
    stars(c, t, 50, 400)
    for x, lab, t0 in ((620, "Vietnã: esperando o avião", 98.12), (1300, "Malásia: \"já está com o Vietnã\"", 100.36)):
        show(c, t, t0, x, 640, lambda c, lab=lab: (radio_tower(c, t, waves=True), text(c, lab, 0, 250, 36, TYPE, INK)), s=0.9)
        show(c, t, t0 + 0.5, x + 80, 420, M_q := (lambda c: big_q(c, 90, AMBER)))
    show(c, t, 103.3, 960, 180, group(sc(clock, (t - 103.3) * 6 if t > 103.3 else 0, s=1.0)), anim="pop")
    show(c, t, 104.6, 960, 320, T("horas se passaram", 42, AMBER), anim="fade")
    fog(c, t, 980, 0.06)


# ------------------------------------------------------------------ 1:49 o radar militar
def s12(c, t):  # 109.1 - 119.4
    c.save(); c.translate(1100, 540); c.scale(1.6, 1.6); radar(c, t, blip=t > 113.0); c.restore()
    show(c, t, 109.3, 1100, 100, lambda c: stitle(c, "Só que o avião não tinha sumido", 0, 0, 56, INK, AMBER), anim="up")
    show(c, t, 113.1, 1100, 990, T("radar militar da Malásia", 40, (0.5, 1, 0.6)), anim="fade")
    show(c, t, 116.6, 1600, 360, sc(big_q, 130, AMBER))
    HIST(c, t, [(0, "stand"), (113.0, "point_r"), (116.6, "think")], [(0, "neutral"), (113.0, "shocked"), (116.6, "think")])


def s13(c, t):  # 119.4 - 137.7 a volta
    draw_map(c, SEA2, grid=5)
    map_label(c, SEA2, 102.3, 3.9, "MALÁSIA", 30, LGREEN)
    map_label(c, SEA2, 98.0, 1.6, "SUMATRA", 30, LGREEN)
    map_label(c, SEA2, 95.2, 9.5, "Mar de Andamã", 32, ICE)
    map_label(c, SEA2, 99.3, 3.4, "Estreito de Malaca", 26, ICE)
    map_path(c, SEA2, ROUTE_OUT, 1.0, (0.55, 0.45, 0.25), 4, [10, 8])
    map_point(c, SEA2, *KUL, t=t, pulse=False)
    map_point(c, SEA2, *IGARI, col=RED, t=t)
    map_label(c, SEA2, *IGARI, "último contato civil", 24, RED, dy=-36)
    p = ease_io(clamp01((t - 119.6) / 12.5))
    map_path(c, SEA2, ROUTE_BACK, p, (0.5, 1, 0.6), 5)
    if t < 133.5:
        plane_on_path(c, SEA2, ROUTE_BACK, max(0.001, p))
    show(c, t, 122.9, *[v for v in SEA2(*PENANG)], lambda c: (circle(c, 0, 0, 9, AMBER, 3), text(c, "Penang", -70, 30, 28, TYPE, INK)))
    show(c, t, 129.7, 1400, 960, lambda c: caption_box(c, "sem falar com ninguém", 42), anim="up")
    if t > 132.1:
        x, y = SEA2(*LAST_RADAR)
        map_point(c, SEA2, *LAST_RADAR, col=RED, t=t)
        show(c, t, 132.3, x, y - 60, lambda c: date_stamp(c, "02h22", 40, RED), anim="stamp")
        show(c, t, 133.4, x, y - 125, T("fim do radar militar", 28, RED), anim="fade")


def s14(c, t):  # 137.7 - 150.1 satélite religa
    stars(c, t, 120, 1080)
    c.save(); c.translate(1300, 300); c.rotate(math.sin(t * 0.4) * 0.05); satellite(c, t); c.restore()
    c.save(); c.translate(1500, 820); c.rotate(-0.4); c.scale(0.5, 0.5); airplane(c, (0.5, 0.52, 0.56)); c.restore()
    show(c, t, 140.4, 760, 160, lambda c: date_stamp(c, "02h25", 52, AMBER), anim="stamp")
    if t > 141.5:
        ping(c, t, 141.5, 1500, 800, 1300, 380, ICE, 1.2)
        ping(c, t, 143.5, 1500, 800, 1300, 380, ICE, 1.2)
    show(c, t, 142.0, 700, 420, T("o sistema de satélite volta a se conectar", 36, ICE), anim="fade")
    show(c, t, 147.0, 860, 560, sc(big_q, 150, AMBER))
    HIST(c, t, [(0, "stand"), (140.4, "point_ru"), (147.0, "think")], [(0, "neutral"), (140.4, "shocked"), (147.0, "think")])


def s15(c, t):  # 150.1 - 167.8 handshakes "estou aqui"
    stars(c, t, 120, 1080)
    c.save(); c.translate(960, 230); c.scale(0.8, 0.8); satellite(c, t); c.restore()
    show(c, t, 150.2, 960, 70, lambda c: stitle(c, "a única pista", 0, 0, 52, INK, AMBER), anim="up")
    show(c, t, 160.0, 1400, 230, T("Inmarsat", 40, AMBER), anim="fade")
    k = clamp01((t - 150.0) / 17.8)
    px, py = 400 + k * 1100, 860 - math.sin(k * 3) * 30
    c.save(); c.translate(px, py); c.scale(0.5, 0.5); airplane(c, (0.5, 0.52, 0.56)); c.restore()
    for t0 in (155.0, 158.6, 162.2, 165.8):
        ping(c, t, t0, px, py - 20, 960, 300, ICE, 1.1)
    show(c, t, 155.4, 700, 560, lambda c: caption_box(c, "uma \"chamada\" automática a cada hora", 38), anim="up")
    show(c, t, 165.8, px + 40, py - 180, lambda c: (speech(c, 300, 100, -40, 90), text(c, "estou aqui", 0, 0, 40, HAND, INK)), d=0.4)


def s16(c, t):  # 167.8 - 179.3 seis horas e silêncio
    stars(c, t, 60, 1080)
    show(c, t, 167.9, 960, 150, lambda c: stitle(c, "e o avião continuou respondendo", 0, 0, 54, INK, AMBER), anim="up")
    times = ["02h25", "03h41", "04h41", "05h41", "06h41", "08h10", "08h19"]
    for i, s in enumerate(times):
        x = 300 + i * 220
        t0 = 168.6 + i * 0.75
        col = RED if i == 6 else ICE
        show(c, t, t0, x, 520, lambda c, s=s, col=col: (circle(c, 0, 0, 26, col, 5), text(c, s, 0, 70, 34, TYPE, INK)))
        if i < 6:
            show(c, t, t0 + 0.3, x + 110, 520, lambda c: line(c, -70, 0, 70, 0, 3, LGRAY), anim="fade")
    show(c, t, 170.5, 960, 720, lambda c: caption_box(c, "quase 6 horas depois de sair do radar", 40), anim="up")
    show(c, t, 173.6, 1620, 400, T("último sinal", 36, RED), anim="fade")
    show(c, t, 176.8, 960, 900, lambda c: stitle(c, "silêncio.", 0, 0, 80, LGRAY), anim="fade", d=1.2)


# ------------------------------------------------------------------ 2:59 o arco
def io_base(c, t, arc_p=1.0, sat=True):
    draw_map(c, IO, grid=10)
    if sat:
        x, y = IO(64.5, 9)
        c.save(); c.translate(x, y); c.scale(0.38, 0.38); satellite(c, t); c.restore()
    if arc_p > 0:
        map_path(c, IO, ARC, arc_p, AMBER, 7)


def s17(c, t):  # 179.3 - 198.8
    io_base(c, t, ease_io(clamp01((t - 183.9) / 5.0)))
    map_point(c, IO, *KUL, t=t, pulse=False)
    map_label(c, IO, 77.0, -12.0, "Oceano Índico", 40, ICE, font=SERIF)
    show(c, t, 179.4, 960, 90, lambda c: caption_box(c, "engenheiros analisam o tempo e a frequência dos sinais", 38), anim="up")
    if t > 189.0:
        show(c, t, 189.0, *IO(112, -12), T("o arco", 38, AMBER), anim="fade")
    if t > 192.1:
        poly(c, [IO(*p) for p in SEARCH])
        rgb(c, RED, 0.25 + 0.1 * math.sin(t * 3)); c.fill()
    show(c, t, 196.6, *[v for v in IO(66, -34)], lambda c: stitle(c, "sul do Oceano Índico", 0, 0, 50, INK, RED), anim="up")


def s18(c, t):  # 198.8 - 211.2 anúncio / sem sobreviventes
    stars(c, t, 40, 400)
    show(c, t, 198.9, 900, 480, sc(newspaper, "FIM NO ÍNDICO", "MH370  •  24 de março de 2014", s=1.6), anim="drop")
    show(c, t, 209.0, 960, 930, lambda c: stitle(c, "Sem sobreviventes.", 0, 0, 62, INK), anim="fade", d=1.0)
    show(c, t, 209.2, 1560, 640, lambda c: candle(c, t))
    HIST(c, t, [(0, "stand"), (209.0, "relax")], [(0, "sad")])


# ------------------------------------------------------------------ 3:31 a busca
def s19(c, t):  # 211.2 - 231.2
    ocean_bg(c, t, 330)
    c.save(); c.translate(1000, 330); c.scale(0.9, 0.9); sonar_ship(c, t); c.restore()
    sonar_beam(c, t, 1000, 370, 640, 0.7)
    c.save(); c.translate(960, 1090); seabed(c, t, 0, seed=7, col=(0.11, 0.13, 0.17)); c.restore()
    show(c, t, 211.3, 960, 90, lambda c: stitle(c, "A maior busca da história da aviação", 0, 0, 54, INK, AMBER), anim="up")
    show(c, t, 216.4, 1550, 520, T("sonar", 40, ICE), anim="fade")
    show(c, t, 219.5, 1520, 640, T("montanhas submarinas nunca mapeadas", 34, INK), anim="fade")
    show(c, t, 225.0, 420, 560, lambda c: (caption_box(c, "3 anos", 40), text(c, "~120.000 km²", 0, 90, 56, SERIF, AMBER)), anim="up")
    show(c, t, 229.5, 420, 760, T("maior que Pernambuco", 38, INK), anim="fade")


def s20(c, t):  # 231.2 - 238.7 nada / suspensa
    ocean_bg(c, t, 330)
    c.save(); c.translate(1000, 330); c.scale(0.9, 0.9); sonar_ship(c, t); c.restore()
    sonar_beam(c, t, 1000, 370, 640, 0.7, (0.6, 0.6, 0.65))
    c.save(); c.translate(960, 1090); seabed(c, t, 0, seed=7, col=(0.11, 0.13, 0.17)); c.restore()
    show(c, t, 232.9, 960, 560, lambda c: stitle(c, "Nada.", 0, 0, 120, LGRAY), anim="fade", d=0.8)
    show(c, t, 234.2, 960, 130, lambda c: date_stamp(c, "JANEIRO DE 2017  •  BUSCA SUSPENSA", 46, RED), anim="stamp")


# ------------------------------------------------------------------ 3:58 os destroços
def s21(c, t):  # 238.7 - 257.3
    stars(c, t, 50, 500)
    c.save(); c.translate(1500, 200); moon(c, 50); c.restore()
    g = cairo.LinearGradient(0, 520, 0, 760)
    g.add_color_stop_rgb(0, 0.06, 0.11, 0.18); g.add_color_stop_rgb(1, 0.10, 0.16, 0.22)
    c.rectangle(0, 520, W, 260); c.set_source(g); c.fill()
    c.move_to(0, 760)
    for i in range(0, W + 60, 60):
        c.line_to(i, 760 + math.sin(i / 90 + t * 1.5) * 10)
    c.line_to(W, H); c.line_to(0, H); c.close_path()
    fs(c, (0.45, 0.40, 0.30), 0.1, (0.45, 0.40, 0.30))
    c.move_to(0, 760)
    for i in range(0, W + 60, 60):
        c.line_to(i, 760 + math.sin(i / 90 + t * 1.5) * 10)
    rgb(c, INK, 0.8); c.set_line_width(4); c.stroke()
    show(c, t, 238.8, 960, 110, lambda c: stitle(c, "Mas o oceano ainda tinha algo a dizer", 0, 0, 52, INK, AMBER), anim="up")
    show(c, t, 242.0, 960, 220, lambda c: date_stamp(c, "JULHO DE 2015  •  ILHA DA REUNIÃO", 40, AMBER), anim="stamp")
    show(c, t, 245.2, 1180, 860, sc(flaperon, s=1.1), anim="up", d=0.8, rot=-0.08)
    show(c, t, 250.6, 1180, 1000, T("flaperon: uma peça móvel da asa", 38, INK), anim="fade")
    show(c, t, 253.6, 1520, 700, lambda c: date_stamp(c, "MH370 CONFIRMADO", 40, RED), anim="stamp")
    HIST(c, t, [(0, "stand"), (245.2, "point_r")], [(0, "think"), (253.6, "shocked")], x=330)


def s22(c, t):  # 257.3 - 278.9
    io_base(c, t, 1.0)
    map_point(c, IO, *REUNION, col=RED, t=t)
    map_label(c, IO, *REUNION, "Reunião", 24, dy=34)
    for i, (pt, lab) in enumerate(DEBRIS):
        t0 = 257.6 + i * 1.3
        if t > t0:
            map_point(c, IO, *pt, col=AMBER, t=t)
            x, y = IO(*pt)
            dx = 75 if lab == "Maurício" else -95
            show(c, t, t0, x + dx, y - (22 if lab == "Maurício" else 0), T(lab, 24, INK), anim="fade")
    show(c, t, 264.5, 960, 90, lambda c: caption_box(c, "caiu mesmo no Oceano Índico", 40), anim="up")
    if t > 269.6:
        for i in range(5):
            ph = ((t - 269.6) * 0.25 + i * 0.2) % 1
            lon = 98 - ph * 45
            lat = -30 + i * 3 + math.sin(ph * 6) * 2
            x, y = IO(lon, lat)
            c.save(); c.translate(x, y); c.rotate(-0.1)
            rgb(c, ICE, 0.7 * (1 - ph)); c.set_line_width(4)
            c.move_to(0, 0); c.line_to(40, 0); c.move_to(0, 0); c.line_to(12, -10); c.move_to(0, 0); c.line_to(12, 10); c.stroke()
            c.restore()
        show(c, t, 269.8, *IO(75, -40), T("correntes marítimas", 32, ICE), anim="fade")
    show(c, t, 276.4, *IO(97, -36), sc(big_q, 110, AMBER))


# ------------------------------------------------------------------ 4:38 o relatório e as teorias
def s23(c, t):  # 278.9 - 299.3
    show(c, t, 279.0, 1180, 470, sc(folder, "RELATÓRIO FINAL • 2018", s=1.6), anim="drop")
    show(c, t, 283.4, 1180, 760, T("quase 500 páginas", 40, LGRAY), anim="fade")
    typewrite(c, t, 287.5, "Causa: não determinada.", 1180, 860, 50, RED, cps=18)
    show(c, t, 291.1, 960, 110, lambda c: caption_box(c, "a volta foi feita, muito provavelmente, com controle manual", 36), anim="up")
    show(c, t, 296.5, 960, 200, lambda c: caption_box(c, "interferência de alguém: não descartada", 36), anim="up")
    HIST(c, t, [(0, "stand"), (287.5, "think")], [(0, "neutral"), (287.5, "think")])


def theory_card(c, num, title):
    rrect(c, -420, -60, 840, 120, 12)
    rgb(c, (0, 0, 0), 0.5); c.fill_preserve(); rgb(c, AMBER); c.set_line_width(3); c.stroke()
    text(c, num, -390, 0, 30, TYPE, AMBER, align="l")
    text(c, title, 70, 0, 44, SERIF, INK)


def s24(c, t):  # 299.3 - 321.2 teoria 1
    show(c, t, 299.4, 960, 90, lambda c: stitle(c, "As teorias", 0, 0, 64, INK, AMBER), anim="up")
    show(c, t, 302.0, 960, 230, lambda c: theory_card(c, "TEORIA 1", "alguém dentro da cabine"), anim="left")

    def route(c):
        c.set_dash([8, 8]); c.move_to(-150, -80); c.curve_to(-60, -100, 0, 40, 150, 90)
        rgb(c, RED); c.set_line_width(4); c.stroke(); c.set_dash([])
        circle(c, 150, 90, 8, RED, 0)
        text(c, "simulador", 0, -100, 22, TYPE, (0.5, 1, 0.6))
    show(c, t, 306.3, 1250, 560, sc(monitor, route, s=1.15))
    show(c, t, 313.4, 1250, 560, lambda c: date_stamp(c, "NÃO É PROVA", 54, RED), anim="stamp")
    show(c, t, 315.6, 1250, 880, lambda c: caption_box(c, "família e colegas sempre o defenderam", 38), anim="up")
    show(c, t, 318.6, 1250, 970, T("nenhum motivo foi encontrado", 36, LGRAY), anim="fade")
    HIST(c, t, [(0, "stand"), (306.3, "point_r"), (313.4, "hips")], [(0, "think"), (313.4, "neutral")])


def s25(c, t):  # 321.2 - 329.7 teoria 2
    show(c, t, 321.3, 960, 230, lambda c: theory_card(c, "TEORIA 2", "um sequestro"), anim="left")
    show(c, t, 323.5, 1250, 640, sc(cockpit_door, s=1.1))
    show(c, t, 324.5, 1430, 470, sc(big_q, 90, AMBER))
    show(c, t, 327.0, 1250, 930, lambda c: caption_box(c, "ninguém jamais assumiu a autoria", 38), anim="up")
    HIST(c, t, [(0, "think")], [(0, "think")])


def s26(c, t):  # 329.7 - 342.4 teoria 3
    show(c, t, 329.8, 960, 230, lambda c: theory_card(c, "TEORIA 3", "uma emergência"), anim="left")
    show(c, t, 332.0, 1000, 640, lambda c: flames(c, t, 220, 170))
    show(c, t, 333.4, 1450, 560, lambda c: oxygen_mask(c, t))
    if t > 340.7:
        a = 0.35 + 0.25 * math.sin(t * 5)
        glow(c, 1200, 820, 380, ICE, 0.25)
        c.save(); c.translate(1200 + (t - 340.7) * 40, 820); c.scale(0.8, 0.8)
        c.push_group(); airplane(c, (0.7, 0.8, 0.9)); c.pop_group_to_source(); c.paint_with_alpha(a); c.restore()
        show(c, t, 340.8, 1200, 990, lambda c: stitle(c, "um voo fantasma", 0, 0, 56, ICE), anim="fade")
    HIST(c, t, [(0, "stand"), (332.0, "head")], [(0, "worried"), (340.8, "shocked")])
    fog(c, t, 900, 0.07)


def s27(c, t):  # 342.4 - 351.6 nenhuma explica tudo
    for i, (n, ttl) in enumerate((("1", "cabine"), ("2", "sequestro"), ("3", "emergência"))):
        show(c, t, 342.5 + i * 0.25, 560 + i * 400, 300, lambda c, n=n, ttl=ttl: (rrect(c, -170, -90, 340, 180, 12), fs(c, FILL, 4),
                                                                                       text(c, "TEORIA " + n, 0, -40, 28, TYPE, AMBER),
                                                                                       text(c, ttl, 0, 20, 44, SERIF, INK)))
    show(c, t, 344.0, 960, 300, lambda c: (line(c, -600, -100, 600, 100, 10, RED), line(c, -600, 100, 600, -100, 10, RED)), anim="stamp")
    items = [("o silêncio", 346.3), ("a curva", 348.5), ("o satélite", 350.0)]
    for i, (s, t0) in enumerate(items):
        show(c, t, t0, 560 + i * 400, 620, lambda c, s=s: (big_q(c, 80, AMBER), text(c, s, 0, 110, 40, TYPE, INK)))
    show(c, t, 342.6, 960, 930, lambda c: caption_box(c, "nenhuma teoria explica tudo", 42), anim="up")


# ------------------------------------------------------------------ 5:51 Ocean Infinity
def s28(c, t):  # 351.6 - 373.5
    ocean_bg(c, t, 380)
    c.save(); c.translate(960, 1120); seabed(c, t, 0, seed=9, col=(0.10, 0.12, 0.16)); c.restore()
    c.save(); c.translate(600, 380); c.scale(0.8, 0.8); sonar_ship(c, t); c.restore()
    show(c, t, 351.8, 960, 90, lambda c: date_stamp(c, "2018  •  OCEAN INFINITY", 46, AMBER), anim="stamp")
    show(c, t, 355.0, 1350, 250, lambda c: caption_box(c, "só receberia se encontrasse o avião", 38), anim="up")
    x_over(c, t, 361.1, 600, 300, 160)
    show(c, t, 361.2, 600, 520, T("não encontrou", 40, RED), anim="fade")
    if t > 362.2:
        show(c, t, 362.2, 1300, 560, lambda c: date_stamp(c, "2025", 52, AMBER), anim="stamp")
        k = (t - 362.2)
        c.save(); c.translate(1300 - k * 25, 720 + math.sin(t) * 10); c.scale(0.9, 0.9); auv(c, t); c.restore()
        show(c, t, 363.6, 1350, 880, T("robôs submarinos", 38, ICE), anim="fade")
    show(c, t, 367.4, 1350, 1010, lambda c: caption_box(c, "fim da busca: janeiro de 2026", 40), anim="up")
    show(c, t, 370.6, 1700, 720, sc(x_icon, 46))


# ------------------------------------------------------------------ 6:13 fechamento
def s29(c, t):  # 373.5 - 390.9
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.04, 0.08, 0.13); g.add_color_stop_rgb(1, 0.01, 0.02, 0.04)
    c.rectangle(0, 0, W, H); c.set_source(g); c.fill()
    dust(c, t, 60, 0.5)
    c.save(); c.translate(960, 1100); seabed(c, t, 0, seed=11, col=(0.08, 0.10, 0.13)); c.restore()
    show(c, t, 373.6, 960, 110, lambda c: stitle(c, "Mais de uma década depois...", 0, 0, 56, INK, AMBER), anim="up")
    if t > 379.5:
        p = ease_io(prog(t, 379.5, 3.0))
        c.move_to(0, 600); c.curve_to(600, 520, 1300, 700, 1920 * p + 0.01, 560)
        c.set_dash([14, 12]); rgb(c, AMBER, 0.8); c.set_line_width(5); c.stroke(); c.set_dash([])
        show(c, t, 380.0, 1500, 500, T("uma linha invisível", 36, AMBER), anim="fade")
    show(c, t, 384.1, 760, 800, sc(black_box, s=0.9), anim="fade", d=1.0)
    show(c, t, 386.8, 1250, 780, lambda c: (candle(c, t), text(c, "239", 0, 140, 64, SERIF, INK)), anim="fade", d=1.0)


def s30(c, t):  # 390.9 - fim
    stars(c, t, 80, 700)
    HIST(c, t, [(0, "stand"), (390.9, "present"), (395.8, "wave"), (399.9, "stand")], [(0, "think"), (393.9, "happy")], x=380, s=1.05)
    show(c, t, 391.0, 1150, 200, lambda c: stitle(c, "O que aconteceu naquela noite?", 0, 0, 58, INK, AMBER), anim="up")
    show(c, t, 393.9, 1150, 420, lambda c: (speech(c, 700, 150, -260, 140), text(c, "deixe sua teoria nos comentários", 0, 0, 40, HAND, INK)))
    show(c, t, 395.8, 1150, 640, sc(subscribe_btn, t > 397.5, s=0.9))
    show(c, t, 397.6, 1480, 640, sc(bell, s=0.8), rot=math.sin(t * 18) * 0.2 * max(0, 1 - (t - 397.6)))
    show(c, t, 401.2, 1150, 880, lambda c: (text(c, "PONTO CEGO", 0, 0, 80, SERIF, INK), line(c, -300, 55, 300, 55, 3, AMBER)), anim="fade", d=1.2)
    fog(c, t, 1000, 0.07)


SCENES = [
    (0.0, 8.0, s01), (8.0, 14.0, s02), (14.0, 20.3, s03), (20.3, 25.0, s04), (25.0, 38.7, s05), (38.7, 50.2, s06),
    (50.2, 58.9, s07), (58.9, 67.0, s08), (67.0, 86.4, s09), (86.4, 98.1, s10), (98.1, 109.1, s11), (109.1, 119.4, s12),
    (119.4, 137.7, s13), (137.7, 150.1, s14), (150.1, 167.8, s15), (167.8, 179.3, s16), (179.3, 198.8, s17),
    (198.8, 211.2, s18), (211.2, 231.2, s19), (231.2, 238.7, s20), (238.7, 257.3, s21), (257.3, 278.9, s22),
    (278.9, 299.3, s23), (299.3, 321.2, s24), (321.2, 329.7, s25), (329.7, 342.4, s26), (342.4, 351.6, s27),
    (351.6, 373.5, s28), (373.5, 390.9, s29), (390.9, 999.0, s30),
]

SFX = [(20.3, "boom"), (92.84, "impact"), (114.5, "riser"), (146.9, "heartbeat"), (147.9, "heartbeat"),
       (196.5, "boom"), (209.0, "bell"), (232.9, "gust"), (253.5, "impact"), (285.5, "riser"), (287.5, "boom"),
       (340.7, "heartbeat"), (341.7, "heartbeat"), (361.0, "impact"), (384.0, "bell"), (401.2, "boom")]
