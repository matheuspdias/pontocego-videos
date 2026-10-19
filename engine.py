import cairo, math, random

W, H, FPS = 1920, 1080, 30

BG = (0.075, 0.080, 0.098)          # fundo noturno
INK = (0.91, 0.87, 0.77)            # traço de giz (creme)
PAPER = BG                          # recortes usam a cor do fundo
FILL = (0.17, 0.18, 0.21)           # preenchimento neutro (ardósia)
SHADOW = (0, 0, 0)
DARKTXT = (0.13, 0.10, 0.07)        # texto escuro sobre pergaminho
PARCH = (0.80, 0.71, 0.52)          # pergaminho
PARCH2 = (0.66, 0.56, 0.38)
GREEN = (0.32, 0.56, 0.40)
LGREEN = (0.55, 0.72, 0.58)
RED = (0.74, 0.20, 0.18)
BLOOD = (0.55, 0.10, 0.10)
YELLOW = (0.88, 0.64, 0.24)         # âmbar
AMBER = YELLOW
LYELLOW = (0.95, 0.80, 0.45)
BLUE = (0.30, 0.46, 0.66)
ICE = (0.62, 0.78, 0.92)
LBLUE = (0.40, 0.52, 0.64)
ORANGE = (0.86, 0.48, 0.20)
PINK = (0.70, 0.45, 0.50)
PURPLE = (0.45, 0.35, 0.62)
GRAY = (0.48, 0.48, 0.52)
LGRAY = (0.30, 0.31, 0.35)
DGRAY = (0.22, 0.22, 0.25)
BROWN = (0.45, 0.31, 0.20)
COAT = (0.42, 0.30, 0.20)

SERIF = "Cinzel"          # títulos (antigo)
TYPE = "Special Elite"    # máquina de escrever (datas, documentos)
HAND = "Patrick Hand"     # rótulos
MARKER = SERIF


# ---------------------------------------------------------------- easing
def clamp01(x):
    return 0.0 if x < 0 else 1.0 if x > 1 else x


def ease_out(p):
    return 1 - (1 - p) ** 3


def ease_io(p):
    return p * p * (3 - 2 * p)


def ease_out_back(p, s=1.9):
    p = p - 1
    return p * p * ((s + 1) * p + s) + 1


def prog(t, t0, d=0.4):
    return clamp01((t - t0) / d)


# ---------------------------------------------------------------- eventos sonoros
_CUES = None  # quando é uma lista, os eventos visuais são registrados aqui (ver sfx.py)


def cue(t0, kind):
    if _CUES is not None:
        _CUES.append((round(float(t0), 3), kind))


def rgb(c, col, a=1.0):
    c.set_source_rgba(col[0], col[1], col[2], a)


# ---------------------------------------------------------------- basic helpers
def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()


def fs(c, fill, lw=6, stroke=INK):
    """fill + stroke current path"""
    if fill is not None:
        rgb(c, fill)
        c.fill_preserve()
    rgb(c, stroke)
    c.set_line_width(lw)
    c.stroke()


def poly(c, pts):
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.close_path()


def line(c, x1, y1, x2, y2, lw=6, col=INK):
    c.move_to(x1, y1)
    c.line_to(x2, y2)
    rgb(c, col)
    c.set_line_width(lw)
    c.stroke()


def circle(c, x, y, r, fill=None, lw=6, stroke=INK):
    c.new_sub_path()
    c.arc(x, y, r, 0, 2 * math.pi)
    if lw == 0:
        rgb(c, fill)
        c.fill()
    else:
        fs(c, fill, lw, stroke)


def ellipse(c, x, y, rx, ry):
    c.save()
    c.translate(x, y)
    c.scale(rx, ry)
    c.new_sub_path()
    c.arc(0, 0, 1, 0, 2 * math.pi)
    c.restore()


def _font(c, font):
    if font == SERIF:
        c.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    else:
        c.select_font_face(font)


def text_w(c, s, size, font=MARKER):
    _font(c, font)
    c.set_font_size(size)
    return c.text_extents(s).x_advance


def text(c, s, x=0, y=0, size=60, font=MARKER, col=INK, align="c", outline=None, ow=10, alpha=1.0):
    _font(c, font)
    c.set_font_size(size)
    e = c.text_extents(s)
    if align == "c":
        tx = x - e.x_advance / 2
    elif align == "r":
        tx = x - e.x_advance
    else:
        tx = x
    ty = y + size * 0.36
    c.move_to(tx, ty)
    if outline is not None:
        c.text_path(s)
        rgb(c, outline, alpha)
        c.set_line_width(ow)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.stroke_preserve()
        rgb(c, col, alpha)
        c.fill()
    else:
        rgb(c, col, alpha)
        c.show_text(s)
    return e.x_advance


def hl(c, s, x, y, size=56, bg=PARCH, col=DARKTXT, font=TYPE, pad=24, rot=-0.015, lw=0):
    """text with marker-highlight background"""
    w = text_w(c, s, size, font)
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    rrect(c, -w / 2 - pad, -size * 0.62, w + 2 * pad, size * 1.24, 14)
    if lw:
        fs(c, bg, lw)
    else:
        rgb(c, bg)
        c.fill()
    text(c, s, 0, 0, size, font, col)
    c.restore()


def show(c, t, t0, x, y, fn, s=1.0, anim="pop", d=0.45, t1=None, rot=0.0):
    """draw fn at (x,y) with an entrance animation starting at t0 (and optional fade-out at t1)"""
    cue(t0, "anim:" + anim)
    if t < t0:
        return
    p = prog(t, t0, d)
    alpha = 1.0
    if t1 is not None and t > t1:
        alpha = 1 - prog(t, t1, 0.3)
        if alpha <= 0:
            return
    c.save()
    c.translate(x, y)
    sc = s
    if anim == "pop":
        k = ease_out_back(p)
        if k < 0.02:
            c.restore()
            return
        sc = s * k
    elif anim == "fade":
        alpha *= ease_out(p)
    elif anim == "up":
        c.translate(0, (1 - ease_out(p)) * 70)
        alpha *= ease_out(p)
    elif anim == "left":
        c.translate(-(1 - ease_out(p)) * 260, 0)
        alpha *= ease_out(p)
    elif anim == "right":
        c.translate((1 - ease_out(p)) * 260, 0)
        alpha *= ease_out(p)
    elif anim == "drop":
        c.translate(0, -(1 - ease_out_back(p, 1.4)) * 500)
        alpha *= clamp01(p * 3)
    elif anim == "stamp":
        k = 1 + (1 - ease_out(p)) * 1.6
        sc = s * k
        alpha *= clamp01(p * 2.5)
    c.scale(sc, sc)
    if rot:
        c.rotate(rot)
    if alpha < 0.999:
        c.push_group()
        fn(c)
        c.pop_group_to_source()
        c.paint_with_alpha(alpha)
    else:
        fn(c)
    c.restore()


def arrow(c, x1, y1, x2, y2, col=INK, lw=7, bend=0.15, head=26):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    cx, cy = mx - dy * bend, my + dx * bend
    c.move_to(x1, y1)
    c.curve_to(cx, cy, cx, cy, x2, y2)
    rgb(c, col)
    c.set_line_width(lw)
    c.stroke()
    a = math.atan2(y2 - cy, x2 - cx)
    for s in (-1, 1):
        c.move_to(x2, y2)
        c.line_to(x2 - head * math.cos(a + s * 0.45), y2 - head * math.sin(a + s * 0.45))
    c.stroke()


def arrow_draw(c, t, t0, x1, y1, x2, y2, d=0.5, **kw):
    """arrow that grows from start"""
    cue(t0, "arrow")
    if t < t0:
        return
    p = ease_out(prog(t, t0, d))
    if p < 0.05:
        return
    arrow(c, x1, y1, x1 + (x2 - x1) * p, y1 + (y2 - y1) * p, **kw)


# ---------------------------------------------------------------- OBJECTS (drawn centered at 0,0)
def car(c, color=BLUE, ghost=False):
    body = [(-158, 26), (-158, -24), (-124, -40), (-78, -44), (-46, -92), (56, -92), (98, -44), (146, -36), (160, -10), (160, 26)]
    poly(c, body)
    if ghost:
        c.set_dash([18, 14])
        fs(c, None, 6, GRAY)
    else:
        fs(c, color, 6)
    wins = [[(-36, -80), (-3, -80), (-3, -48), (-62, -48)], [(8, -80), (50, -80), (82, -48), (8, -48)]]
    for w in wins:
        poly(c, w)
        if ghost:
            fs(c, None, 4, GRAY)
        else:
            fs(c, LBLUE, 4)
    if not ghost:
        line(c, 2, -44, 2, 18, 4)
        line(c, 18, -26, 34, -26, 5)
        circle(c, 149, -16, 9, YELLOW, 4)
        rrect(c, -160, -22, 12, 18, 3)
        fs(c, RED, 3)
    for wx in (-96, 96):
        if ghost:
            circle(c, wx, 28, 34, None, 6, GRAY)
        else:
            circle(c, wx, 28, 34, INK, 0)
            circle(c, wx, 28, 15, (0.78, 0.78, 0.8), 0)
    c.set_dash([])


def price_tag(c, s, col=YELLOW, size=46, tcol=INK):
    w = text_w(c, s, size) + 70
    h = size * 1.55
    c.save()
    c.rotate(-0.06)
    poly(c, [(-w / 2, 0), (-w / 2 + 30, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2 + 30, h / 2)])
    fs(c, col, 5)
    circle(c, -w / 2 + 28, 0, 7, PAPER, 4)
    text(c, s, 14, 0, size, MARKER, tcol)
    c.restore()


def bill(c):
    rrect(c, -90, -46, 180, 92, 8)
    fs(c, GREEN, 5)
    rrect(c, -78, -35, 156, 70, 6)
    rgb(c, LGREEN)
    c.set_line_width(3)
    c.stroke()
    circle(c, 0, 0, 25, LGREEN, 3, (0.1, 0.4, 0.2))
    text(c, "R$", 0, -2, 26, MARKER, (0.1, 0.4, 0.2))


def bills(c, n=3):
    for i in range(n):
        c.save()
        c.translate(-i * 12 + (n - 1) * 6, -i * 13 + (n - 1) * 6)
        c.rotate(-0.12 + i * 0.09)
        bill(c)
        c.restore()


def coin(c):
    circle(c, 0, 0, 40, YELLOW, 5)
    circle(c, 0, 0, 29, None, 3, (0.8, 0.55, 0.08))
    text(c, "$", 0, -2, 38, MARKER, (0.7, 0.45, 0.05))


def gas_pump(c):
    rrect(c, -60, -85, 90, 165, 12)
    fs(c, RED, 6)
    rrect(c, -46, -70, 62, 42, 6)
    fs(c, FILL, 4)
    rrect(c, -72, 76, 114, 16, 4)
    fs(c, INK, 4)
    c.move_to(30, -40)
    c.curve_to(80, -40, 80, 30, 62, 50)
    rgb(c, INK)
    c.set_line_width(9)
    c.stroke()
    rrect(c, 50, -78, 22, 40, 5)
    fs(c, DGRAY, 4)
    c.move_to(-15, -5)
    c.curve_to(-30, 20, -28, 35, -15, 38)
    c.curve_to(-2, 35, 0, 20, -15, -5)
    fs(c, YELLOW, 3)


def shield(c, col=BLUE):
    c.move_to(0, -80)
    c.line_to(66, -56)
    c.curve_to(66, 12, 42, 55, 0, 80)
    c.curve_to(-42, 55, -66, 12, -66, -56)
    c.close_path()
    fs(c, col, 6)
    c.move_to(-26, 2)
    c.line_to(-6, 24)
    c.line_to(30, -24)
    rgb(c, INK)
    c.set_line_width(13)
    c.stroke()


def document(c, title="IPVA", tcol=RED, tsize=34):
    poly(c, [(-62, -82), (36, -82), (62, -56), (62, 82), (-62, 82)])
    fs(c, FILL, 6)
    poly(c, [(36, -82), (36, -56), (62, -56)])
    fs(c, LGRAY, 4)
    text(c, title, -4, -32, tsize, MARKER, tcol)
    for y in (8, 32, 56):
        line(c, -40, y, 40, y, 5, GRAY)


def wrench(c):
    c.save()
    c.rotate(-0.75)
    line(c, 0, -20, 0, 100, 34, INK)
    line(c, 0, -20, 0, 100, 22, GRAY)
    circle(c, 0, -52, 40, GRAY, 6)
    rgb(c, PAPER)
    c.rectangle(-14, -100, 28, 48)
    c.fill()
    line(c, -14, -88, -14, -55, 6)
    line(c, 14, -88, 14, -55, 6)
    line(c, -14, -55, 14, -55, 6)
    circle(c, 0, 86, 7, PAPER, 4)
    c.restore()


def tire(c):
    circle(c, 0, 0, 60, INK, 0)
    for i in range(12):
        a = i * math.pi / 6
        line(c, 50 * math.cos(a), 50 * math.sin(a), 60 * math.cos(a), 60 * math.sin(a), 4, DGRAY)
    circle(c, 0, 0, 32, (0.75, 0.75, 0.78), 0)
    circle(c, 0, 0, 11, DGRAY, 0)


def wrench_tire(c):
    c.save(); c.translate(-30, 10); tire(c); c.restore()
    c.save(); c.translate(40, -10); c.scale(0.8, 0.8); wrench(c); c.restore()


def parking(c):
    rrect(c, -58, -58, 116, 116, 18)
    fs(c, BLUE, 6)
    text(c, "P", 0, 0, 92, MARKER, INK)


def toll(c):
    rrect(c, -86, -20, 22, 110, 4)
    fs(c, GRAY, 5)
    c.rectangle(-70, -18, 170, 26)
    fs(c, FILL, 5)
    for i in range(5):
        if i % 2 == 0:
            c.rectangle(-64 + i * 33, -15, 30, 20)
            rgb(c, RED)
            c.fill()
    c.rectangle(-70, -18, 170, 26)
    rgb(c, INK); c.set_line_width(5); c.stroke()
    rrect(c, -95, -100, 170, 56, 10)
    fs(c, YELLOW, 5)
    text(c, "PEDÁGIO", -10, -72, 30, MARKER)


def house(c, big=False, col=LYELLOW):
    w = 190 if big else 120
    h = w * 0.72
    c.rectangle(-w / 2, -h * 0.35, w, h)
    fs(c, col, 6)
    poly(c, [(-w / 2 - 18, -h * 0.35), (0, -h * 1.05), (w / 2 + 18, -h * 0.35)])
    fs(c, RED, 6)
    dw = w * 0.22
    c.rectangle(-dw / 2 - w * 0.18, h * 0.65 - dw * 1.6, dw, dw * 1.6)
    fs(c, BROWN, 5)
    c.rectangle(w * 0.08, -h * 0.12, w * 0.26, w * 0.24)
    fs(c, LBLUE, 5)


def card(c, col=PURPLE):
    rrect(c, -95, -60, 190, 120, 14)
    fs(c, col, 6)
    c.rectangle(-95, -34, 190, 20)
    rgb(c, INK); c.fill()
    rrect(c, -70, 0, 38, 28, 5)
    fs(c, YELLOW, 4)
    circle(c, 46, 30, 17, RED, 0)
    circle(c, 66, 30, 17, ORANGE, 0)


def bank(c):
    poly(c, [(-95, -42), (0, -100), (95, -42)])
    fs(c, LGRAY, 6)
    text(c, "$", 0, -62, 34, MARKER, GREEN)
    c.rectangle(-95, -42, 190, 18)
    fs(c, LGRAY, 6)
    for x in (-72, -30, 12, 54):
        c.rectangle(x, -22, 20, 80)
        fs(c, FILL, 5)
    c.rectangle(-105, 58, 210, 20)
    fs(c, LGRAY, 6)


def percent(c):
    circle(c, 0, 0, 72, ORANGE, 6)
    text(c, "%", 0, -2, 100, MARKER, INK)


def clock(c, t=0):
    circle(c, 0, 0, 72, FILL, 7)
    for i in range(12):
        a = i * math.pi / 6
        line(c, 56 * math.cos(a), 56 * math.sin(a), 64 * math.cos(a), 64 * math.sin(a), 5)
    a = t * 2.5
    line(c, 0, 0, 45 * math.sin(a), -45 * math.cos(a), 7)
    line(c, 0, 0, 28 * math.sin(a / 12 + 1), -28 * math.cos(a / 12 + 1), 8)
    circle(c, 0, 0, 7, INK, 0)


def calendar(c, num="30", top=RED, size=72):
    rrect(c, -78, -72, 156, 156, 14)
    fs(c, FILL, 6)
    c.save()
    rrect(c, -78, -72, 156, 156, 14)
    c.clip()
    c.rectangle(-78, -72, 156, 44)
    rgb(c, top); c.fill()
    c.restore()
    rrect(c, -78, -72, 156, 156, 14)
    rgb(c, INK); c.set_line_width(6); c.stroke()
    for x in (-38, 38):
        rrect(c, x - 6, -86, 12, 30, 5)
        fs(c, DGRAY, 3)
    text(c, num, 0, 28, size, MARKER)


def piggy(c, col=PINK, slot=True):
    for lx in (-50, -15, 30, 60):
        rrect(c, lx - 12, 40, 24, 42, 6)
        fs(c, col, 5)
    c.move_to(-96, -5)
    c.curve_to(-125, -25, -120, 15, -108, 5)
    rgb(c, INK); c.set_line_width(5); c.stroke()
    ellipse(c, 0, 0, 100, 74)
    fs(c, col, 6)
    poly(c, [(22, -62), (40, -100), (60, -55)])
    fs(c, col, 5)
    ellipse(c, 98, 8, 18, 24)
    fs(c, (0.93, 0.5, 0.6), 5)
    circle(c, 93, 2, 3.5, INK, 0)
    circle(c, 103, 2, 3.5, INK, 0)
    circle(c, 55, -18, 7, INK, 0)
    if slot:
        rrect(c, -30, -78, 50, 9, 4)
        rgb(c, INK); c.fill()


def calculator(c, disp="R$ ?"):
    rrect(c, -85, -115, 170, 230, 18)
    fs(c, DGRAY, 6)
    rrect(c, -64, -94, 128, 54, 8)
    fs(c, (0.80, 0.92, 0.76), 4)
    text(c, disp, 0, -68, 30, MARKER)
    for r in range(4):
        for k in range(4):
            col = ORANGE if k == 3 else LGRAY
            rrect(c, -64 + k * 33, -22 + r * 32, 26, 24, 5)
            fs(c, col, 3)


def check_icon(c, r=42):
    circle(c, 0, 0, r, GREEN, 6)
    c.move_to(-r * 0.45, 0)
    c.line_to(-r * 0.1, r * 0.35)
    c.line_to(r * 0.5, -r * 0.35)
    rgb(c, INK); c.set_line_width(r * 0.25); c.stroke()


def x_icon(c, r=42):
    circle(c, 0, 0, r, RED, 6)
    k = r * 0.38
    line(c, -k, -k, k, k, r * 0.25, INK)
    line(c, -k, k, k, -k, r * 0.25, INK)


def big_x(c, s=90, col=RED, lw=20):
    line(c, -s, -s * 0.8, s, s * 0.8, lw, col)
    line(c, -s, s * 0.8, s, -s * 0.8, lw, col)


def qmark(c, size=120, col=INK):
    text(c, "?", 0, 0, size, MARKER, col)


def exclaim(c, size=120, col=RED):
    text(c, "!", 0, 0, size, MARKER, col)


def bulb(c):
    for i in range(7):
        a = -math.pi / 2 + (i - 3) * 0.45
        line(c, 70 * math.cos(a), -20 + 70 * math.sin(a), 92 * math.cos(a), -20 + 92 * math.sin(a), 6, ORANGE)
    circle(c, 0, -20, 46, YELLOW, 6)
    rrect(c, -22, 22, 44, 34, 6)
    fs(c, GRAY, 5)
    line(c, -22, 34, 22, 34, 4)
    line(c, -22, 45, 22, 45, 4)


def sparkle(c, r=30, col=YELLOW):
    k = r * 0.25
    poly(c, [(0, -r), (k, -k), (r, 0), (k, k), (0, r), (-k, k), (-r, 0), (-k, -k)])
    fs(c, col, 4)


def sweat(c, r=12):
    c.move_to(0, -r * 1.8)
    c.curve_to(r * 0.6, -r * 0.6, r, 0, 0, r)
    c.curve_to(-r, 0, -r * 0.6, -r * 0.6, 0, -r * 1.8)
    fs(c, LBLUE, 3)


def cloud_shape(c, w, h, fill=FILL, lw=7, seed=3):
    rnd = random.Random(seed)
    circles = [(0, 0, None)]
    n = max(10, int((w + h) / 45))
    for i in range(n):
        a = 2 * math.pi * i / n
        r = min(w, h) * (0.16 + 0.04 * rnd.random())
        circles.append((math.cos(a) * (w / 2 - r * 0.7), math.sin(a) * (h / 2 - r * 0.7), r))
    for x, y, r in circles:
        if r is None:
            ellipse(c, 0, 0, w / 2 - 20, h / 2 - 20)
        else:
            c.new_sub_path(); c.arc(x, y, r, 0, 2 * math.pi)
        rgb(c, INK); c.set_line_width(lw * 2); c.stroke()
    for x, y, r in circles:
        if r is None:
            ellipse(c, 0, 0, w / 2 - 20, h / 2 - 20)
        else:
            c.new_sub_path(); c.arc(x, y, r, 0, 2 * math.pi)
        rgb(c, fill); c.fill()


def thought(c, w, h, tx, ty):
    """cloud centered at 0,0 with trailing dots toward (tx,ty) (relative)"""
    for i, k in enumerate((0.55, 0.75, 0.9)):
        r = 22 - i * 6
        x = tx * k
        y = ty * k
        circle(c, x, y, r, FILL, 6)
    cloud_shape(c, w, h)


def speech(c, w, h, tx, ty, fill=FILL):
    bx = max(-w / 2 + 40, min(w / 2 - 40, tx * 0.4))
    for pass_ in (0, 1):
        rrect(c, -w / 2, -h / 2, w, h, 36)
        poly(c, [(bx - 50, h / 2 - 6), (tx, ty), (bx + 20, h / 2 - 6)])
        if pass_ == 0:
            rgb(c, INK); c.set_line_width(14); c.stroke()
        else:
            rgb(c, fill); c.fill()


def ribbon(c, s, col=RED, size=58, tcol=INK):
    w = text_w(c, s, size) + 80
    h = size * 1.5
    for sx in (-1, 1):
        x0 = sx * (w / 2 - 10)
        poly(c, [(x0, -h / 2 + 18), (x0 + sx * 70, -h / 2 + 18), (x0 + sx * 50, 18), (x0 + sx * 70, h / 2 + 18), (x0, h / 2 + 18)])
        fs(c, tuple(v * 0.75 for v in col), 5)
    rrect(c, -w / 2, -h / 2, w, h, 6)
    fs(c, col, 6)
    text(c, s, 0, 0, size, MARKER, tcol)


def clipboard(c, title="ORÇAMENTO", items=3, checks=True):
    rrect(c, -115, -150, 230, 300, 16)
    fs(c, BROWN, 6)
    c.rectangle(-95, -118, 190, 252)
    fs(c, FILL, 5)
    rrect(c, -45, -165, 90, 36, 8)
    fs(c, GRAY, 5)
    text(c, title, 0, -84, 30, MARKER)
    for i in range(items):
        y = -30 + i * 55
        c.rectangle(-75, y - 14, 28, 28)
        fs(c, FILL, 4)
        if checks:
            c.move_to(-70, y)
            c.line_to(-62, y + 9)
            c.line_to(-44, y - 14)
            rgb(c, GREEN); c.set_line_width(6); c.stroke()
        line(c, -30, y, 70, y, 6, GRAY)


def subscribe_btn(c, done=False):
    rrect(c, -230, -62, 460, 124, 22)
    fs(c, GRAY if done else RED, 7)
    text(c, "INSCRITO" if done else "INSCREVA-SE", 0, -2, 54, MARKER, INK)


def bell(c):
    c.move_to(-55, 40)
    c.curve_to(-40, 25, -45, -50, 0, -58)
    c.curve_to(45, -50, 40, 25, 55, 40)
    c.close_path()
    fs(c, YELLOW, 6)
    circle(c, 0, 52, 13, YELLOW, 5)
    circle(c, 0, -64, 8, YELLOW, 5)


def cursor(c):
    poly(c, [(0, 0), (0, 70), (17, 54), (30, 82), (42, 76), (29, 49), (52, 48)])
    fs(c, FILL, 5)


def envelope(c):
    c.rectangle(-90, -55, 180, 110)
    fs(c, FILL, 6)
    c.move_to(-90, -55)
    c.line_to(0, 10)
    c.line_to(90, -55)
    rgb(c, INK); c.set_line_width(5); c.stroke()


def iceberg(c, t):
    pass


def donut(c, pct, r=230, lw=80, col=RED):
    c.new_sub_path(); c.arc(0, 0, r, 0, 2 * math.pi)
    rgb(c, LGRAY); c.set_line_width(lw); c.stroke()
    if pct > 0.001:
        c.new_sub_path()
        c.arc(0, 0, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * pct)
        rgb(c, col); c.set_line_width(lw); c.set_line_cap(cairo.LINE_CAP_BUTT); c.stroke()
        c.set_line_cap(cairo.LINE_CAP_ROUND)
    for rr in (r - lw / 2, r + lw / 2):
        c.new_sub_path(); c.arc(0, 0, rr, 0, 2 * math.pi)
        rgb(c, INK); c.set_line_width(6); c.stroke()


def speed_lines(c, t, n=5, length=140):
    for i in range(n):
        y = -120 + i * 60
        off = ((t * 900 + i * 137) % 260)
        x = -off
        line(c, x - length, y, x, y, 6, GRAY)


def neq(c, s=60, col=RED, lw=14):
    line(c, -s, -s * 0.3, s, -s * 0.3, lw, col)
    line(c, -s, s * 0.3, s, s * 0.3, lw, col)
    line(c, s * 0.45, -s * 0.85, -s * 0.45, s * 0.85, lw, col)


def eq(c, s=60, col=INK, lw=14):
    line(c, -s, -s * 0.3, s, -s * 0.3, lw, col)
    line(c, -s, s * 0.3, s, s * 0.3, lw, col)


def icon_label(fn, label, size=44, dy=120, col=INK, s=1.0):
    def f(c):
        c.save(); c.scale(s, s); fn(c); c.restore()
        text(c, label, 0, dy, size, HAND, col)
    return f


# ---------------------------------------------------------------- STICK FIGURE
LEN = dict(torso=145, head=52, ua=80, fa=76, th=96, sh=94)

POSES = {
    "stand": dict(rh=(34, 138), lh=(-34, 138)),
    "relax": dict(rh=(42, 118), lh=(-42, 118)),
    "point_r": dict(rh=(156, -10), lh=(-34, 138), rf_="point"),
    "point_ru": dict(rh=(128, -92), lh=(-34, 138), rf_="point"),
    "point_l": dict(lh=(-156, -10), rh=(34, 138), lf_="point"),
    "point_lu": dict(lh=(-128, -92), rh=(34, 138), lf_="point"),
    "think": dict(rh=(-12, -40), rb=1, lh=(-26, 112)),
    "think_l": dict(lh=(12, -40), lb=-1, rh=(26, 112)),
    "hips": dict(rh=(26, 112), lh=(-26, 112)),
    "shrug": dict(rh=(92, -34), rb=1, lh=(-92, -34), lb=-1),
    "arms_up": dict(rh=(64, -140), rb=1, lh=(-64, -140), lb=-1),
    "head": dict(rh=(26, -98), rb=1, lh=(-26, -98), lb=-1),
    "thumb": dict(rh=(96, -40), rb=1, lh=(-34, 138), rf_="thumb"),
    "finger_up": dict(rh=(66, -110), rb=1, lh=(-26, 112), rf_="point_up"),
    "present": dict(rh=(140, 36), rb=1, lh=(-34, 138)),
    "present_l": dict(lh=(-140, 36), lb=-1, rh=(34, 138)),
    "wave": dict(rh=(88, -120), rb=1, lh=(-34, 138), wave=True),
    "hold": dict(rh=(48, 50), lh=(-48, 50)),
    "run": dict(rh=(34, 138), lh=(-34, 138), run=True),
}
LEGS = dict(rf=(30, 186), lf=(-30, 186))


def _ik(sx, sy, tx, ty, l1, l2, bend):
    dx, dy = tx - sx, ty - sy
    d = math.hypot(dx, dy)
    d = max(abs(l1 - l2) + 1, min(d, l1 + l2 - 0.5))
    a = math.atan2(dy, dx)
    cosv = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    al = math.acos(max(-1, min(1, cosv)))
    ex = sx + l1 * math.cos(a + bend * al)
    ey = sy + l1 * math.sin(a + bend * al)
    hx = sx + d * math.cos(a)
    hy = sy + d * math.sin(a)
    return (ex, ey), (hx, hy)


def _pose(name):
    p = dict(rb=-1, lb=1)
    p.update(LEGS)
    p.update(POSES[name])
    return p


def pose_at(t, keys, blend=0.32):
    """keys: list of (time, posename). returns interpolated pose dict"""
    cur = keys[0]
    prev = None
    for k in keys:
        if t >= k[0]:
            prev = cur if k is not keys[0] else None
            cur = k
    # find previous key
    idx = keys.index(cur)
    pc = _pose(cur[1])
    if idx == 0:
        return pc
    pp = _pose(keys[idx - 1][1])
    p = ease_io(prog(t, cur[0], blend))
    if p >= 1:
        return pc
    out = dict(pc)
    for k in ("rh", "lh", "rf", "lf"):
        a, b = pp[k], pc[k]
        out[k] = (a[0] + (b[0] - a[0]) * p, a[1] + (b[1] - a[1]) * p)
    if p < 0.5:
        for k in ("rb", "lb", "rf_", "lf_"):
            out[k] = pp.get(k)
    return out


def val_at(t, keys):
    v = keys[0][1]
    for k in keys:
        if t >= k[0]:
            v = k[1]
    return v


def face(c, expr, t, fid, look=0.0, r=52):
    ink = INK
    lx = look * 6
    blink = ((t * 1000 + fid * 1777) % 4100) < 130
    ey = -6
    big = expr in ("shocked", "desperate")
    # eyes
    for sx in (-1, 1):
        x = sx * 17 + lx
        if blink:
            line(c, x - 7, ey, x + 7, ey, 4.5)
        else:
            ellipse(c, x, ey + (-3 if expr == "think" else 0), 7.5 if big else 6.5, 11 if big else 9.5)
            rgb(c, ink); c.fill()
    c.set_line_width(5)
    rgb(c, ink)
    # brows
    if expr in ("worried", "desperate", "sad"):
        for sx in (-1, 1):
            c.move_to(sx * 30 + lx, -22)
            c.line_to(sx * 9 + lx, -31)
        c.stroke()
    elif expr == "shocked":
        for sx in (-1, 1):
            c.new_sub_path()
            c.arc(sx * 17 + lx, -16, 13, math.pi * 1.2, math.pi * 1.8)
        c.stroke()
    elif expr == "think":
        c.move_to(-28 + lx, -26); c.line_to(-8 + lx, -24)
        c.stroke()
        c.new_sub_path(); c.arc(17 + lx, -22, 12, math.pi * 1.15, math.pi * 1.85)
        c.stroke()
    elif expr == "angry":
        for sx in (-1, 1):
            c.move_to(sx * 30 + lx, -30)
            c.line_to(sx * 8 + lx, -21)
        c.stroke()
    elif expr == "confident":
        c.move_to(-28 + lx, -24); c.line_to(-8 + lx, -26)
        c.stroke()
        c.new_sub_path(); c.arc(17 + lx, -24, 12, math.pi * 1.15, math.pi * 1.85)
        c.stroke()
    # mouth
    mx = lx * 0.6
    if expr in ("happy", "confident"):
        c.new_sub_path(); c.arc(mx, 8, 21, math.radians(25), math.radians(155)); c.stroke()
    elif expr == "grin":
        c.new_sub_path()
        c.arc(mx, 12, 22, 0, math.pi)
        c.close_path()
        rgb(c, ink); c.fill()
    elif expr == "neutral":
        line(c, mx - 12, 24, mx + 12, 24, 5)
    elif expr in ("worried", "sad"):
        c.new_sub_path(); c.arc(mx, 40, 17, math.radians(205), math.radians(335)); c.stroke()
    elif expr == "shocked":
        ellipse(c, mx, 25, 10, 14); rgb(c, ink); c.fill()
    elif expr == "desperate":
        poly(c, [(mx - 20, 30), (mx - 12, 14), (mx + 12, 14), (mx + 20, 30)])
        rgb(c, ink); c.fill()
    elif expr == "think":
        line(c, mx - 4, 26, mx + 16, 20, 5)
    elif expr == "angry":
        line(c, mx - 14, 26, mx + 14, 26, 5)
    # sweat
    if expr in ("desperate", "shocked"):
        ph = (t * 0.9 + fid * 0.3) % 1.0
        c.save()
        c.translate(-r - 8, -10 + ph * 40)
        c.push_group()
        sweat(c, 11)
        c.pop_group_to_source()
        c.paint_with_alpha(1 - ph)
        c.restore()


def figure(c, t, x, y, s=1.0, poses=((0, "stand"),), exprs=((0, "happy"),), look=0.0, shirt=YELLOW,
           hair="tuft", fid=0, appear=None, flip_look=None, hat=None, hat_col=None, coat=None,
           glasses=False, mustache=False, prop=None, alpha=1.0):
    """draw stick figure with feet on ground y. poses/exprs are keyframe lists of (time, name)."""
    a_scale = 1.0
    if appear is not None:
        cue(appear, "appear")
        if t < appear:
            return
        a_scale = ease_out_back(prog(t, appear, 0.45))
        if a_scale < 0.02:
            return
    P = pose_at(t, list(poses))
    expr = val_at(t, list(exprs))
    if callable(look):
        look = look(t)
    c.save()
    c.translate(x, y)
    c.scale(s * a_scale, s * a_scale)
    rnd = random.Random(int(t * 8) * 31 + fid * 977)
    J = lambda: (rnd.uniform(-1.4, 1.4), rnd.uniform(-1.4, 1.4))
    bob = math.sin(t * 2.3 + fid) * 2.2
    run = P.get("run")
    # shadow
    ellipse(c, 0, 4, 85, 12)
    rgb(c, SHADOW, 0.35); c.fill()

    hip = (0, -(LEN["th"] + LEN["sh"] - 4) + bob)
    rf, lf = P["rf"], P["lf"]
    rh, lh = P["rh"], P["lh"]
    lean = 0
    if run:
        ph = t * 11 + fid * 1.3
        hip = (0, hip[1] + abs(math.sin(ph)) * -10)
        rf = (30 + 70 * math.sin(ph), 186 - 40 * max(0, math.cos(ph)))
        lf = (-30 - 70 * math.sin(ph), 186 - 40 * max(0, -math.cos(ph)))
        rh = (-20 + 70 * math.sin(ph), 96)
        lh = (20 - 70 * math.sin(ph), 96)
        lean = 0.12
    if P.get("wave"):
        rh = (rh[0] + math.sin(t * 9) * 26, rh[1])
    neck = (hip[0] + math.sin(lean) * LEN["torso"], hip[1] - math.cos(lean) * LEN["torso"])
    sh = (neck[0] - math.sin(lean) * 16, neck[1] + 16)
    head = (neck[0] + math.sin(lean) * (LEN["head"] + 12), neck[1] - (LEN["head"] + 12))

    lw = 9
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.set_line_join(cairo.LINE_JOIN_ROUND)

    def limb(origin, tgt, l1, l2, bend, foot=None, fing=None, side=1):
        j1, j2 = J(), J()
        (ex, ey), (hx, hy) = _ik(origin[0], origin[1], origin[0] + tgt[0], origin[1] + tgt[1], l1, l2, bend)
        ex += j1[0]; ey += j1[1]; hx += j2[0]; hy += j2[1]
        c.move_to(*origin); c.line_to(ex, ey); c.line_to(hx, hy)
        rgb(c, INK); c.set_line_width(lw); c.stroke()
        if foot:
            ellipse(c, hx + side * 14, hy + 2, 22, 9)
            rgb(c, INK); c.fill()
        else:
            circle(c, hx, hy, 9.5, INK, 0)
            a = math.atan2(hy - ey, hx - ex)
            if fing == "point":
                line(c, hx, hy, hx + 26 * math.cos(a), hy + 26 * math.sin(a), 6)
            elif fing == "thumb":
                line(c, hx, hy, hx, hy - 26, 7)
            elif fing == "point_up":
                line(c, hx, hy, hx, hy - 28, 6)
        return hx, hy

    # legs
    limb(hip, rf, LEN["th"], LEN["sh"], -1, foot=True, side=1)
    limb(hip, lf, LEN["th"], LEN["sh"], 1, foot=True, side=-1)
    # torso / shirt
    if coat is not None:
        perp = (math.cos(lean), math.sin(lean))
        top = (neck[0] - math.sin(lean) * 8, neck[1] + 8)
        bot = (hip[0] + math.sin(lean) * 70, hip[1] + 70)
        pts = [(top[0] - perp[0] * 34, top[1] - perp[1] * 34), (top[0] + perp[0] * 34, top[1] + perp[1] * 34),
               (bot[0] + perp[0] * 58, bot[1] + perp[1] * 58), (bot[0] - perp[0] * 58, bot[1] - perp[1] * 58)]
        poly(c, pts)
        fs(c, coat, 7)
        # lapels + buttons
        c.move_to(top[0] - 22, top[1]); c.line_to(top[0], top[1] + 46); c.line_to(top[0] + 22, top[1])
        rgb(c, INK); c.set_line_width(5); c.stroke()
        line(c, top[0], top[1] + 46, (top[0] + bot[0]) / 2 + 2, bot[1], 4)
        for k in (0.45, 0.65, 0.85):
            circle(c, top[0] + (bot[0] - top[0]) * k + 9, top[1] + (bot[1] - top[1]) * k, 4, INK, 0)
    elif shirt is not None:
        perp = (math.cos(lean), math.sin(lean))
        top = (neck[0] - math.sin(lean) * 8, neck[1] + 8)
        bot = (hip[0] - math.sin(lean) * -16, hip[1] + 16)
        pts = [(top[0] - perp[0] * 32, top[1] - perp[1] * 32), (top[0] + perp[0] * 32, top[1] + perp[1] * 32),
               (bot[0] + perp[0] * 44, bot[1] + perp[1] * 44), (bot[0] - perp[0] * 44, bot[1] - perp[1] * 44)]
        c.move_to(*pts[0])
        c.line_to(*pts[1])
        c.line_to(*pts[2])
        c.line_to(*pts[3])
        c.close_path()
        fs(c, shirt, 7)
    else:
        c.move_to(*hip); c.line_to(*neck)
        rgb(c, INK); c.set_line_width(lw); c.stroke()
    # neck
    line(c, neck[0], neck[1], head[0], head[1] + LEN["head"] - 2, lw)
    # head
    hj = J()
    c.save()
    c.translate(head[0] + hj[0], head[1] + hj[1])
    c.rotate(lean * 0.6)
    circle(c, 0, 0, LEN["head"], FILL, lw)
    if hair == "tuft":
        c.set_line_width(5); rgb(c, INK)
        for i in range(3):
            c.move_to(-4 + i * 13, -LEN["head"] + 2)
            c.curve_to(-2 + i * 13, -LEN["head"] - 14, 6 + i * 13, -LEN["head"] - 18, 14 + i * 13, -LEN["head"] - 14)
        c.stroke()
    elif hair == "spiky":
        c.set_line_width(5); rgb(c, INK)
        for i in range(5):
            a = -math.pi / 2 + (i - 2) * 0.28
            c.move_to(math.cos(a) * 50, math.sin(a) * 50)
            c.line_to(math.cos(a) * 68, math.sin(a) * 68)
        c.stroke()
    elif hair == "long":
        c.new_sub_path()
        c.arc(0, -4, LEN["head"] + 6, math.pi * 0.95, math.pi * 2.05)
        rgb(c, INK); c.set_line_width(14); c.stroke()
    face(c, expr, t, fid, look)
    hr = LEN["head"]
    if glasses:
        for sx in (-1, 1):
            circle(c, sx * 17 + look * 6, -6, 14, None, 4)
        line(c, -3 + look * 6, -8, 3 + look * 6, -8, 4)
    if mustache:
        c.move_to(-16, 14); c.curve_to(-8, 8, -2, 10, 0, 13); c.curve_to(2, 10, 8, 8, 16, 14)
        rgb(c, INK); c.set_line_width(6); c.stroke()
    if hat == "fedora":
        hc = hat_col or (0.30, 0.22, 0.15)
        rrect(c, -46, -hr - 44, 92, 50, 18)
        fs(c, hc, 6)
        c.rectangle(-46, -hr - 4, 92, 12)
        rgb(c, BLOOD); c.fill()
        ellipse(c, 0, -hr + 10, 82, 13)
        fs(c, hc, 6)
    elif hat == "beanie":
        hc = hat_col or RED
        c.new_sub_path(); c.arc(0, -hr + 18, hr - 2, math.pi, 2 * math.pi); c.close_path()
        fs(c, hc, 6)
        rrect(c, -hr - 4, -hr + 8, 2 * hr + 8, 20, 6)
        fs(c, hc, 5)
        circle(c, 0, -2 * hr + 12, 11, hc, 5)
    elif hat == "pilot":
        pilot_cap(c, hr)
    elif hat == "tophat":
        hc = hat_col or (0.10, 0.10, 0.12)
        rrect(c, -36, -hr - 78, 72, 84, 6); fs(c, hc, 6)
        c.rectangle(-36, -hr - 8, 72, 10); rgb(c, BLOOD); c.fill()
        ellipse(c, 0, -hr + 6, 66, 11); fs(c, hc, 6)
    elif hat == "sailor":
        hc = hat_col or (0.85, 0.84, 0.80)
        c.new_sub_path(); c.arc(0, -hr + 12, hr - 6, math.pi, 2 * math.pi); c.close_path(); fs(c, hc, 5)
        rrect(c, -hr - 2, -hr + 4, 2 * hr + 4, 16, 6); fs(c, (0.16, 0.20, 0.32), 4)
    elif hat == "helmet":
        # elmo grego/romano de bronze com crista
        hc = hat_col or (0.72, 0.55, 0.28)
        c.move_to(-hr * 0.9, -hr * 0.62); c.curve_to(-hr * 0.4, -2.05 * hr, hr * 0.4, -2.05 * hr, hr * 0.9, -hr * 0.62)
        c.line_to(hr * 1.04, -hr * 0.62); c.curve_to(hr * 1.05, -hr * 0.2, hr * 0.98, hr * 0.2, hr * 0.85, hr * 0.32)
        c.line_to(hr * 0.70, -hr * 0.30); c.line_to(-hr * 0.70, -hr * 0.30); c.line_to(-hr * 0.85, hr * 0.32)
        c.curve_to(-hr * 0.98, hr * 0.2, -hr * 1.05, -hr * 0.2, -hr * 1.04, -hr * 0.62); c.close_path()
        fs(c, hc, 5)
        c.move_to(-hr * 0.95, -1.52 * hr); c.curve_to(-hr * 0.3, -2.75 * hr, hr * 0.6, -2.6 * hr, hr * 1.05, -1.55 * hr)
        c.curve_to(hr * 0.5, -2.05 * hr, -hr * 0.3, -2.1 * hr, -hr * 0.95, -1.52 * hr); c.close_path()
        fs(c, (0.66, 0.14, 0.12), 4)
    elif hat == "laurel":
        # coroa de louros dourada
        hc = hat_col or (0.86, 0.68, 0.26)
        for sx in (-1, 1):
            for k in range(5):
                a = math.pi * (1.05 + 0.09 * k) if sx < 0 else math.pi * (1.95 - 0.09 * k)
                px, py = math.cos(a) * (hr + 2), math.sin(a) * (hr + 2) + 4
                c.save(); c.translate(px, py); c.rotate(a + sx * 0.9)
                ellipse(c, 0, 0, 13, 6); fs(c, hc, 3)
                c.restore()
    elif hat == "mitre":
        # mitra de bispo
        hc = hat_col or (0.86, 0.84, 0.78)
        poly(c, [(-hr * 0.8, -hr + 8), (-hr * 0.7, -hr - 52), (0, -hr - 86), (hr * 0.7, -hr - 52), (hr * 0.8, -hr + 8)]); fs(c, hc, 5)
        line(c, 0, -hr - 70, 0, -hr + 4, 5, (0.80, 0.62, 0.24)); line(c, -22, -hr - 40, 22, -hr - 40, 5, (0.80, 0.62, 0.24))
    elif hat == "hood":
        hc = hat_col or COAT
        c.new_sub_path(); c.arc(0, 0, hr + 14, math.pi * 0.85, math.pi * 2.15)
        rgb(c, hc); c.set_line_width(22); c.stroke()
        c.new_sub_path(); c.arc(0, 0, hr + 25, math.pi * 0.85, math.pi * 2.15)
        rgb(c, INK); c.set_line_width(5); c.stroke()
    c.restore()
    # arms
    perp = (math.cos(lean), math.sin(lean))
    rsh = (sh[0] + perp[0] * 26, sh[1] + perp[1] * 26)
    lsh = (sh[0] - perp[0] * 26, sh[1] - perp[1] * 26)
    rhand = limb(rsh, rh, LEN["ua"], LEN["fa"], P.get("rb", -1) or -1, fing=P.get("rf_"))
    lhand = limb(lsh, lh, LEN["ua"], LEN["fa"], P.get("lb", 1) or 1, fing=P.get("lf_"))
    if prop:
        side, fn = prop
        hx, hy = lhand if side == "l" else rhand
        c.save(); c.translate(hx, hy); fn(c, t); c.restore()
    c.restore()


def head_top(y, s):
    """approx y of top of head for a figure with feet at y"""
    return y - s * (LEN["th"] + LEN["sh"] + LEN["torso"] + 2 * LEN["head"] + 12)




# ================================================================ PONTO CEGO — KIT DE MISTÉRIO
# ---------------------------------------------------------------- atmosfera
# ---------------------------------------------------------------- temas por vídeo
# A identidade do canal (Historiador, voz, giz, âmbar, fontes, cartão final) é fixa.
# O tema muda só o "cenário": tom do fundo, cor da névoa e o ambiente sonoro do meio do vídeo.
#   wind  = nível da ventania no meio do vídeo (abertura e fechamento sempre têm a ventania cheia, é a assinatura)
#   drone = frequência base do grave contínuo (Hz); swell = ondulação lenta do grave (mar)
THEMES = {
    "classico": dict(top=(0.055, 0.062, 0.085), bot=(0.095, 0.090, 0.100), fog=INK,                wind=1.00, drone=55.0, swell=0.0),
    "selva":    dict(top=(0.035, 0.068, 0.056), bot=(0.072, 0.098, 0.082), fog=(0.70, 0.86, 0.72), wind=0.30, drone=49.0, swell=0.0),
    "mar":      dict(top=(0.032, 0.055, 0.092), bot=(0.058, 0.086, 0.118), fog=(0.72, 0.83, 0.94), wind=0.35, drone=46.2, swell=0.09),
    "neve":     dict(top=(0.062, 0.078, 0.104), bot=(0.112, 0.122, 0.142), fog=(0.88, 0.92, 1.00), wind=1.00, drone=55.0, swell=0.0),
    "deserto":  dict(top=(0.082, 0.060, 0.042), bot=(0.124, 0.092, 0.064), fog=(0.96, 0.82, 0.60), wind=0.55, drone=51.9, swell=0.0),
    "cidade":   dict(top=(0.058, 0.058, 0.072), bot=(0.096, 0.090, 0.094), fog=(0.82, 0.79, 0.74), wind=0.25, drone=58.3, swell=0.0),
}
THEME = THEMES["classico"]
THEME_NAME = "classico"


def set_theme(name):
    """define o tema do vídeo (chamado pelo render a partir de THEME = "..." no scenes.py)"""
    global THEME, THEME_NAME
    if name not in THEMES:
        raise ValueError(f"tema desconhecido: {name} (opções: {', '.join(THEMES)})")
    THEME, THEME_NAME = THEMES[name], name


def background(c, t):
    """fundo noturno com leve gradiente (tom do tema)"""
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *THEME["top"])
    g.add_color_stop_rgb(1, *THEME["bot"])
    c.set_source(g); c.paint()


def fog(c, t, y=820, alpha=0.07, n=6, col=None):
    """névoa rasteira que se move devagar (cor do tema se col não for passada)"""
    col = col or THEME["fog"]
    for i in range(n):
        x = ((t * (14 + i * 5) + i * 420) % (W + 900)) - 450
        yy = y + math.sin(t * 0.3 + i) * 25 + (i % 3) * 60
        rx, ry = 520 + i * 40, 90 + (i % 2) * 40
        g = cairo.RadialGradient(x, yy, 0, x, yy, rx)
        g.add_color_stop_rgba(0, col[0], col[1], col[2], alpha)
        g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
        c.save(); c.translate(x, yy); c.scale(1, ry / rx); c.translate(-x, -yy)
        c.set_source(g); c.arc(x, yy, rx, 0, 2 * math.pi); c.fill()
        c.restore()


def dust(c, t, n=40, alpha=0.35):
    """partículas de poeira flutuando"""
    rnd = random.Random(7)
    for i in range(n):
        x0, y0, sp, ph = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(6, 22), rnd.uniform(0, 6.28)
        x = (x0 + math.sin(t * 0.4 + ph) * 40) % W
        y = (y0 - t * sp) % H
        a = alpha * (0.5 + 0.5 * math.sin(t * 1.3 + ph))
        rgb(c, INK, a); c.new_sub_path(); c.arc(x, y, rnd.uniform(1.2, 2.6), 0, 6.283); c.fill()


def snow(c, t, n=140, wind=40, alpha=0.8):
    rnd = random.Random(11)
    for i in range(n):
        x0, y0 = rnd.uniform(0, W), rnd.uniform(0, H)
        sp, r = rnd.uniform(60, 160), rnd.uniform(2, 5)
        y = (y0 + t * sp) % (H + 20) - 10
        x = (x0 + t * wind + math.sin(t * 1.5 + i) * 15) % W
        rgb(c, (0.92, 0.94, 0.98), alpha * (r / 5)); c.new_sub_path(); c.arc(x, y, r, 0, 6.283); c.fill()


def glow(c, x, y, r, col=AMBER, a=0.35):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, col[0], col[1], col[2], a)
    g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
    c.set_source(g); c.arc(x, y, r, 0, 2 * math.pi); c.fill()


_VIG = None


def vignette_surface():
    global _VIG
    if _VIG is None:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        c = cairo.Context(surf)
        g = cairo.RadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, W * 0.72)
        g.add_color_stop_rgba(0, 0, 0, 0, 0)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.85)
        c.set_source(g); c.paint()
        _VIG = surf
    return _VIG


def overlay(c, t):
    """aplicado por cima de tudo em todo quadro: poeira + vinheta + leve flicker"""
    dust(c, t)
    c.set_source_surface(vignette_surface(), 0, 0)
    flick = 0.92 + 0.08 * math.sin(t * 7.3) * math.sin(t * 3.1)
    c.paint_with_alpha(flick)


# ---------------------------------------------------------------- textos
def stitle(c, s, x=0, y=0, size=72, col=INK, glow_col=None):
    """título serifado antigo (Cinzel)"""
    if glow_col:
        glow(c, x, y, size * 4, glow_col, 0.18)
    return text(c, s, x, y, size, SERIF, col)


def typewrite(c, t, t0, s, x, y, size=46, col=INK, cps=22, align="c", font=None):
    """texto aparecendo letra a letra (máquina de escrever)"""
    for i, ch in enumerate(s):
        if ch != " ":
            cue(t0 + i / cps, "key")
    if t < t0:
        return
    n = int((t - t0) * cps)
    shown = s[:n]
    font = font or TYPE
    if align == "c":
        w = text_w(c, s, size, font)
        text(c, shown, x - w / 2, y, size, font, col, align="l")
    else:
        text(c, shown, x, y, size, font, col, align=align)
    if n < len(s) and int(t * 4) % 2 == 0:
        w2 = text_w(c, shown, size, font)
        base = x - text_w(c, s, size, font) / 2 if align == "c" else x
        line(c, base + w2 + 6, y - size * 0.4, base + w2 + 6, y + size * 0.4, 3, col)


def date_stamp(c, s, size=48, col=RED):
    """carimbo de data/local estilo arquivo"""
    w = text_w(c, s, size, TYPE) + 50
    c.save(); c.rotate(-0.05)
    rrect(c, -w / 2, -size * 0.75, w, size * 1.5, 6)
    rgb(c, col); c.set_line_width(6); c.stroke()
    rrect(c, -w / 2 + 9, -size * 0.75 + 9, w - 18, size * 1.5 - 18, 4)
    c.set_line_width(2); c.stroke()
    text(c, s, 0, 0, size, TYPE, col)
    c.restore()


def chapter(c, num, title, w=1000):
    """cartão de capítulo"""
    line(c, -w / 2, -60, w / 2, -60, 3, AMBER)
    line(c, -w / 2, 75, w / 2, 75, 3, AMBER)
    text(c, num, 0, -20, 34, TYPE, AMBER)
    text(c, title, 0, 30, 70, SERIF, INK)


def caption_box(c, s, size=44, w=None):
    """faixa escura translúcida com texto (legenda/fato)"""
    tw = text_w(c, s, size, TYPE)
    w = w or tw + 70
    rrect(c, -w / 2, -size * 0.85, w, size * 1.7, 10)
    rgb(c, (0, 0, 0), 0.55); c.fill_preserve()
    rgb(c, INK, 0.5); c.set_line_width(2); c.stroke()
    text(c, s, 0, 0, size, TYPE, INK)


# ---------------------------------------------------------------- objetos de mistério
def lantern(c, t=0, s=1.0, lit=True):
    """lanterna a óleo; origem = argola de cima (para segurar na mão)"""
    c.save(); c.scale(s, s)
    fl = 0.85 + 0.15 * math.sin(t * 13) * math.sin(t * 7)
    if lit:
        glow(c, 0, 70, 260, AMBER, 0.28 * fl)
    c.new_sub_path(); c.arc(0, 8, 12, math.pi, 2 * math.pi)
    rgb(c, INK); c.set_line_width(5); c.stroke()
    poly(c, [(-26, 22), (26, 22), (20, 36), (-20, 36)])
    fs(c, DGRAY, 5)
    rrect(c, -24, 36, 48, 62, 6)
    fs(c, (0.98, 0.78, 0.38) if lit else DGRAY, 5)
    if lit:
        c.move_to(0, 50); c.curve_to(12, 68, 8, 84, 0, 86); c.curve_to(-8, 84, -12, 68, 0, 50)
        rgb(c, (1, 0.95, 0.7)); c.fill()
    line(c, -24, 67, 24, 67, 3)
    rrect(c, -30, 98, 60, 12, 4)
    fs(c, DGRAY, 5)
    c.restore()


def candle(c, t=0):
    fl = math.sin(t * 11) * 3
    glow(c, 0, -80, 200, AMBER, 0.3)
    rrect(c, -22, -50, 44, 110, 6)
    fs(c, (0.86, 0.80, 0.66), 5)
    line(c, 0, -50, 0, -64, 4)
    c.move_to(0, -66); c.curve_to(14 + fl, -82, 6, -104, fl, -112); c.curve_to(-6, -104, -14 + fl, -82, 0, -66)
    fs(c, (1, 0.8, 0.35), 3, AMBER)
    ellipse(c, 0, 64, 50, 12); fs(c, DGRAY, 5)


def book(c, title="", col=BLOOD):
    poly(c, [(-80, -100), (70, -100), (80, -90), (80, 100), (-70, 100), (-80, 90)])
    fs(c, PARCH2, 5)
    rrect(c, -86, -106, 156, 200, 8)
    fs(c, col, 6)
    line(c, -66, -106, -66, 94, 5)
    if title:
        text(c, title, 4, -30, 26, SERIF, LYELLOW)
    c.rectangle(-40, 20, 90, 4); rgb(c, LYELLOW); c.fill()


def scroll(c, lines=4, w=260, h=180, title=None):
    c.rectangle(-w / 2, -h / 2, w, h)
    fs(c, PARCH, 5)
    for sx in (-1, 1):
        ellipse(c, sx * w / 2, 0, 18, h / 2 + 14)
        fs(c, PARCH2, 5)
    y0 = -h / 2 + 34
    if title:
        text(c, title, 0, y0, 30, SERIF, DARKTXT); y0 += 40
    for i in range(lines):
        y = y0 + i * 28
        if y > h / 2 - 20:
            break
        line(c, -w / 2 + 30, y, w / 2 - 30 - (i % 2) * 40, y, 4, (0.45, 0.36, 0.24))


def old_map(c, t=0, route=True):
    poly(c, [(-200, -140), (190, -150), (205, 135), (-195, 145)])
    fs(c, PARCH, 6)
    for x, y, r in ((-120, -60, 50), (60, 40, 70), (130, -90, 30)):
        ellipse(c, x, y, r, r * 0.6)
        rgb(c, (0.55, 0.45, 0.28)); c.set_line_width(3); c.stroke()
    if route:
        c.set_dash([14, 10])
        c.move_to(-160, 100); c.curve_to(-80, 20, 0, 110, 60, 20); c.curve_to(100, -40, 120, -80, 140, -100)
        rgb(c, BLOOD); c.set_line_width(5); c.stroke(); c.set_dash([])
        line(c, 125, -115, 155, -85, 7, BLOOD); line(c, 125, -85, 155, -115, 7, BLOOD)


def magnifier(c):
    line(c, 40, 40, 110, 110, 22, INK)
    line(c, 40, 40, 110, 110, 12, BROWN)
    circle(c, 0, 0, 62, (0.35, 0.45, 0.55), 8)
    c.new_sub_path(); c.arc(-14, -14, 34, math.pi * 1.05, math.pi * 1.45)
    rgb(c, INK, 0.7); c.set_line_width(6); c.stroke()


def mountains(c, w=1400, h=420, snowcap=True, col=(0.22, 0.25, 0.32)):
    pts = [(-w / 2, 0)]
    peaks = [(-0.42, 0.55), (-0.25, 0.95), (-0.08, 0.62), (0.1, 1.0), (0.28, 0.7), (0.43, 0.82)]
    for i, (px, ph) in enumerate(peaks):
        pts.append((px * w, -ph * h))
        if i < len(peaks) - 1:
            pts.append(((px + peaks[i + 1][0]) / 2 * w, -min(ph, peaks[i + 1][1]) * h * 0.55))
    pts.append((w / 2, -0.3 * h))
    pts.append((w / 2, 0))
    poly(c, pts)
    fs(c, col, 6)
    if snowcap:
        for px, ph in peaks:
            x, y = px * w, -ph * h
            d = h * 0.18
            poly(c, [(x, y), (x + d * 0.55, y + d), (x + d * 0.2, y + d * 0.8), (x, y + d * 1.05), (x - d * 0.25, y + d * 0.8), (x - d * 0.55, y + d)])
            fs(c, (0.88, 0.90, 0.94), 4)


def tent(c, torn=False, col=(0.50, 0.42, 0.25)):
    poly(c, [(-160, 60), (-110, -70), (120, -70), (170, 60)])
    fs(c, col, 6)
    poly(c, [(-160, 60), (-110, -70), (-60, 60)])
    fs(c, tuple(v * 0.75 for v in col), 6)
    line(c, -110, -70, -110, -95, 6)
    line(c, 120, -70, 120, -95, 6)
    if torn:
        c.move_to(20, -55); c.line_to(35, -20); c.line_to(18, 5); c.line_to(40, 45)
        rgb(c, BG); c.set_line_width(16); c.stroke_preserve()
        rgb(c, INK); c.set_line_width(3); c.stroke()
        c.move_to(80, -50); c.line_to(70, -10); c.line_to(90, 30)
        rgb(c, BG); c.set_line_width(12); c.stroke_preserve()
        rgb(c, INK); c.set_line_width(3); c.stroke()
    ellipse(c, 0, 70, 200, 14)
    rgb(c, (0.85, 0.88, 0.94), 0.8); c.fill()


def pine(c, h=260, col=(0.16, 0.26, 0.22)):
    line(c, 0, 0, 0, -30, 14, BROWN)
    for i in range(3):
        y = -30 - i * h * 0.26
        wd = h * (0.42 - i * 0.1)
        poly(c, [(-wd, y), (0, y - h * 0.42), (wd, y)])
        fs(c, col, 5)


def footprints(c, n=6, dx=70, dy=-14, t=None, t0=0, col=(0.45, 0.50, 0.60)):
    for i in range(n):
        if t is not None and t < t0 + i * 0.18:
            break
        x, y = i * dx, i * dy + (14 if i % 2 else -14)
        ellipse(c, x, y, 13, 7)
        rgb(c, col, 0.8); c.fill()


def compass(c, t=0):
    circle(c, 0, 0, 70, (0.62, 0.48, 0.24), 6)
    circle(c, 0, 0, 54, PARCH, 4)
    a = math.sin(t * 2.5) * 0.6
    c.save(); c.rotate(a)
    poly(c, [(0, -46), (10, 0), (-10, 0)]); fs(c, RED, 3)
    poly(c, [(0, 46), (10, 0), (-10, 0)]); fs(c, GRAY, 3)
    c.restore()
    circle(c, 0, 0, 6, DARKTXT, 0)


def thermometer(c, val="-30 °C", level=0.12):
    rrect(c, -22, -150, 44, 230, 22)
    fs(c, FILL, 6)
    rrect(c, -10, -135 + 200 * (1 - level), 20, 200 * level, 8)
    rgb(c, ICE); c.fill()
    circle(c, 0, 100, 38, ICE, 6)
    for i in range(6):
        line(c, 22, -120 + i * 36, 38, -120 + i * 36, 4)
    text(c, val, 70, -20, 52, TYPE, ICE, align="l")


def skull(c):
    c.new_sub_path(); c.arc(0, -15, 62, math.pi * 0.85, math.pi * 2.15)
    c.line_to(38, 40); c.line_to(-38, 40); c.close_path()
    fs(c, (0.86, 0.83, 0.74), 6)
    for sx in (-1, 1):
        ellipse(c, sx * 24, -10, 15, 18); rgb(c, BG); c.fill()
    poly(c, [(0, 12), (8, 26), (-8, 26)]); rgb(c, BG); c.fill()
    for x in (-18, -6, 6, 18):
        line(c, x, 40, x, 54, 4)
    line(c, -30, 54, 30, 54, 5)


def moon(c, r=70):
    glow(c, 0, 0, r * 4, (0.85, 0.88, 0.95), 0.12)
    circle(c, 0, 0, r, (0.90, 0.89, 0.82), 5)
    for x, y, rr in ((-20, -15, 14), (22, 10, 10), (-5, 30, 8)):
        circle(c, x, y, rr, (0.80, 0.79, 0.72), 0)


def stars(c, t, n=70, ymax=500):
    rnd = random.Random(5)
    for i in range(n):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, ymax), rnd.uniform(1, 2.6)
        a = 0.4 + 0.6 * abs(math.sin(t * rnd.uniform(0.5, 2) + i))
        rgb(c, INK, a); c.new_sub_path(); c.arc(x, y, r, 0, 6.283); c.fill()


def column(c, h=300):
    c.rectangle(-45, -h, 90, 22); fs(c, (0.62, 0.58, 0.50), 5)
    c.rectangle(-32, -h + 22, 64, h - 44); fs(c, (0.70, 0.66, 0.57), 5)
    for x in (-16, 0, 16):
        line(c, x, -h + 30, x, -30, 3, (0.45, 0.42, 0.36))
    c.rectangle(-45, -22, 90, 22); fs(c, (0.62, 0.58, 0.50), 5)


def temple(c, w=560, h=330):
    poly(c, [(-w / 2 - 20, -h + 60), (0, -h - 30), (w / 2 + 20, -h + 60)]); fs(c, (0.66, 0.62, 0.53), 6)
    c.rectangle(-w / 2 - 20, -h + 60, w + 40, 30); fs(c, (0.62, 0.58, 0.50), 6)
    n = 6
    for i in range(n):
        x = -w / 2 + 20 + i * (w - 40) / (n - 1)
        c.save(); c.translate(x, -30); c.scale(0.55, (h - 120) / 300); column(c); c.restore()
    c.rectangle(-w / 2 - 40, -30, w + 80, 30); fs(c, (0.58, 0.54, 0.46), 6)


def lighthouse(c, t=0):
    a = t * 1.2
    for sx in (-1, 1):
        ang = a if sx > 0 else a + math.pi
        dx = math.cos(ang)
        if dx * sx > 0:
            poly(c, [(0, -330), (sx * 700, -330 - 120), (sx * 700, -330 + 120)])
            g = cairo.LinearGradient(0, 0, sx * 700, 0)
            g.add_color_stop_rgba(0, 1, 0.88, 0.55, 0.35 * abs(dx))
            g.add_color_stop_rgba(1, 1, 0.88, 0.55, 0)
            c.set_source(g); c.fill()
    poly(c, [(-70, 0), (-45, -300), (45, -300), (70, 0)]); fs(c, (0.70, 0.66, 0.57), 6)
    for y in (-100, -200):
        line(c, -60 + (-y) * 0.08, y, 60 - (-y) * 0.08, y, 4)
    rrect(c, -40, -360, 80, 60, 8); fs(c, (1, 0.85, 0.5), 6)
    glow(c, 0, -330, 160, AMBER, 0.4)
    poly(c, [(-50, -360), (0, -400), (50, -360)]); fs(c, BLOOD, 6)


def flames(c, t, w=200, h=160):
    glow(c, 0, -h * 0.4, w * 1.6, ORANGE, 0.3)
    for i, (col, k) in enumerate(((RED, 1.0), (ORANGE, 0.75), (LYELLOW, 0.45))):
        c.move_to(-w / 2 * k, 0)
        n = 5
        for j in range(n):
            x = -w / 2 * k + (j + 0.5) * w * k / n
            hh = h * k * (0.7 + 0.3 * math.sin(t * 9 + j * 1.7 + i))
            c.line_to(x, -hh)
            c.line_to(x + w * k / n / 2, -hh * 0.45)
        c.line_to(w / 2 * k, 0)
        c.close_path()
        fs(c, col, 4 if i == 0 else 0.1, col if i else INK)


def ancient_ship(c):
    c.move_to(-170, 0); c.curve_to(-120, 60, 120, 60, 170, 0); c.line_to(150, -15); c.line_to(-150, -15); c.close_path()
    fs(c, BROWN, 6)
    line(c, 0, -15, 0, -230, 7)
    c.move_to(-5, -215); c.curve_to(90, -180, 90, -70, -5, -40); c.close_path()
    fs(c, PARCH, 5)
    for x in (-110, -60, -10, 40, 90):
        line(c, x, 25, x - 20, 60, 4)


def airplane(c, col=(0.75, 0.77, 0.80)):
    rrect(c, -190, -22, 380, 44, 22); fs(c, col, 6)
    poly(c, [(-30, 0), (60, 0), (-40, 120), (-80, 120)]); fs(c, col, 6)
    poly(c, [(-30, 0), (60, 0), (-40, -110), (-80, -110)]); fs(c, col, 6)
    poly(c, [(-150, -10), (-185, -80), (-160, -80), (-125, -10)]); fs(c, col, 6)
    for x in range(-120, 150, 32):
        circle(c, x, -4, 5, LBLUE, 0)


def radar(c, t=0, blip=True):
    circle(c, 0, 0, 150, (0.06, 0.16, 0.10), 6)
    for r in (50, 100):
        circle(c, 0, 0, r, None, 2, (0.3, 0.7, 0.4))
    line(c, -150, 0, 150, 0, 2, (0.3, 0.7, 0.4)); line(c, 0, -150, 0, 150, 2, (0.3, 0.7, 0.4))
    a = t * 2.2
    c.move_to(0, 0); c.arc(0, 0, 148, a - 0.6, a); c.close_path()
    rgb(c, (0.3, 0.9, 0.5), 0.25); c.fill()
    line(c, 0, 0, 148 * math.cos(a), 148 * math.sin(a), 4, (0.4, 1, 0.6))
    if blip:
        k = ((a - 0.8) % (2 * math.pi))
        al = max(0, 1 - k / 3)
        rgb(c, (0.5, 1, 0.6), al); c.new_sub_path(); c.arc(80 * math.cos(0.8), 80 * math.sin(0.8), 9, 0, 6.283); c.fill()


def newspaper(c, headline="MISTÉRIO", sub=""):
    c.save(); c.rotate(-0.04)
    c.rectangle(-180, -130, 360, 260); fs(c, (0.82, 0.79, 0.70), 6)
    text(c, "JORNAL", 0, -100, 24, SERIF, DARKTXT)
    line(c, -160, -82, 160, -82, 3, DARKTXT)
    text(c, headline, 0, -45, 40, SERIF, DARKTXT)
    if sub:
        text(c, sub, 0, -5, 22, TYPE, DARKTXT)
    c.rectangle(-160, 20, 130, 90); rgb(c, (0.55, 0.52, 0.46)); c.fill()
    for i in range(5):
        line(c, -10, 30 + i * 18, 160, 30 + i * 18, 4, (0.5, 0.47, 0.42))
    c.restore()


def folder(c, label="CONFIDENCIAL", stamp=True):
    poly(c, [(-170, -110), (-80, -110), (-60, -90), (170, -90), (170, 120), (-170, 120)])
    fs(c, (0.62, 0.50, 0.30), 6)
    c.rectangle(-150, -70, 300, 170); fs(c, PARCH, 4)
    for i in range(4):
        line(c, -120, -30 + i * 30, 110, -30 + i * 30, 4, (0.55, 0.47, 0.32))
    if stamp:
        c.save(); c.translate(10, 30); c.rotate(-0.18)
        date_stamp(c, label, 34, BLOOD)
        c.restore()


def photo(c, fn=None, w=220, h=240, caption=None):
    """polaroid; fn desenha o conteúdo (centrado) dentro da foto"""
    rrect(c, -w / 2, -h / 2, w, h, 4); fs(c, (0.88, 0.86, 0.80), 5)
    c.save()
    c.rectangle(-w / 2 + 14, -h / 2 + 14, w - 28, h - 70); c.clip_preserve()
    rgb(c, (0.25, 0.24, 0.22)); c.fill()
    if fn:
        c.translate(0, -h / 2 + 14 + (h - 70) / 2); fn(c)
    c.restore()
    if caption:
        text(c, caption, 0, h / 2 - 28, 24, HAND, DARKTXT)


def pin(c, col=RED):
    circle(c, 0, 0, 11, col, 4)
    circle(c, -3, -3, 3, (1, 1, 1), 0)


def evidence_board(c, t=0, t0=0, items=None, w=900, h=520):
    """quadro de cortiça com fotos/notas ligadas por fio vermelho.
    items: lista de (x, y, fn) relativos ao centro; os fios ligam os itens em sequência"""
    rrect(c, -w / 2, -h / 2, w, h, 10); fs(c, (0.50, 0.36, 0.22), 8)
    rnd = random.Random(3)
    for _ in range(120):
        x, y = rnd.uniform(-w / 2 + 10, w / 2 - 10), rnd.uniform(-h / 2 + 10, h / 2 - 10)
        rgb(c, (0.38, 0.27, 0.16)); c.new_sub_path(); c.arc(x, y, rnd.uniform(1, 3), 0, 6.283); c.fill()
    items = items or []
    for i, (x, y, fn) in enumerate(items):
        c.save(); c.translate(x, y); c.rotate(rnd.uniform(-0.08, 0.08)); fn(c); c.restore()
    for i in range(len(items) - 1):
        if t >= t0 + i * 0.4:
            p = ease_out(prog(t, t0 + i * 0.4, 0.4))
            (x1, y1, _), (x2, y2, _) = items[i], items[i + 1]
            line(c, x1, y1 - 90, x1 + (x2 - x1) * p, y1 - 90 + (y2 - y1) * p, 4, RED)
    for x, y, _ in items:
        c.save(); c.translate(x, y - 90); pin(c); c.restore()


def hourglass(c, t=0, period=6):
    p = (t % period) / period
    poly(c, [(-60, -110), (60, -110), (8, 0), (60, 110), (-60, 110), (-8, 0)])
    fs(c, (0.30, 0.34, 0.40), 5)
    top = 1 - p
    poly(c, [(-50 * top, -10 - 90 * top), (50 * top, -10 - 90 * top), (0, -6)]); rgb(c, LYELLOW); c.fill()
    poly(c, [(-50 * p, 100), (50 * p, 100), (0, 100 - 80 * p)]); rgb(c, LYELLOW); c.fill()
    line(c, 0, -4, 0, 100, 2, LYELLOW)
    for y in (-118, 118):
        rrect(c, -78, y - 8, 156, 16, 6); fs(c, BROWN, 5)


def big_q(c, size=260, col=AMBER):
    glow(c, 0, 0, size * 1.4, col, 0.22)
    text(c, "?", 0, 0, size, SERIF, col)


# ---------------------------------------------------------------- personagens
NARRATOR = dict(coat=COAT, hat="fedora", glasses=True, mustache=False, hair=None, shirt=None, fid=0)


def historiador(c, t, x, y, s, poses, exprs, lantern_on=True, **kw):
    """O narrador fixo do canal: chapéu, sobretudo, óculos, bigode e lanterna."""
    o = dict(NARRATOR)
    o.update(kw)
    if lantern_on and "prop" not in kw:
        # a lanterna fica na mão esquerda quando ela está abaixada; senão some (pousada)
        o["prop"] = ("l", lambda c, tt: lantern(c, tt, 0.55) if pose_at(tt, list(poses))["lh"][1] > 40 else None)
    figure(c, t, x, y, s, poses=poses, exprs=exprs, **o)


def hiker(c, t, x, y, s, poses=((0, "stand"),), exprs=((0, "neutral"),), col=RED, fid=3, **kw):
    """excursionista de inverno (gorro + casaco)"""
    figure(c, t, x, y, s, poses=poses, exprs=exprs, shirt=col, hat="beanie", hat_col=col, hair=None, fid=fid, **kw)


def scholar(c, t, x, y, s, poses=((0, "stand"),), exprs=((0, "neutral"),), col=PARCH2, fid=4, **kw):
    """estudioso antigo (túnica + capuz)"""
    figure(c, t, x, y, s, poses=poses, exprs=exprs, coat=col, hat="hood", hat_col=col, hair=None, fid=fid, **kw)


def person(c, t, x, y, s, poses=((0, "stand"),), exprs=((0, "neutral"),), col=BLUE, fid=5, hair="tuft", **kw):
    figure(c, t, x, y, s, poses=poses, exprs=exprs, shirt=col, hair=hair, fid=fid, **kw)


# ---------------------------------------------------------------- helpers de cena
def title(c, t, t0, s, y=120, size=64, col=INK, anim="up", font=SERIF):
    show(c, t, t0, 960, y, lambda c: text(c, s, 0, 0, size, font, col), anim=anim)


def T(s, size=44, col=INK, font=TYPE):
    return lambda c: text(c, s, 0, 0, size, font, col)


def S(s, size=60, col=INK):
    return lambda c: text(c, s, 0, 0, size, SERIF, col)


def sc(fn, *a, s=1.0, **kw):
    def f(c):
        c.save(); c.scale(s, s); fn(c, *a, **kw); c.restore()
    return f


def group(*fns):
    def f(c):
        for fn in fns:
            fn(c)
    return f


def at(x, y, fn):
    def f(c):
        c.save(); c.translate(x, y); fn(c); c.restore()
    return f


# ================================================================ MAPAS ESTILIZADOS (lon/lat -> tela)
def make_proj(lon0, lon1, lat0, lat1, box=(160, 110, 1760, 1010), coslat=False):
    """projeção equiretangular simples centrada na caixa (x0,y0,x1,y1); retorna f(lon,lat)->(x,y).
    coslat=True encolhe a longitude pelo cosseno da latitude média (mapas de altas latitudes, como o Ártico)."""
    x0, y0, x1, y1 = box
    mlon, mlat = (lon0 + lon1) / 2, (lat0 + lat1) / 2
    fx = math.cos(math.radians(mlat)) if coslat else 1.0
    k = min((x1 - x0) / ((lon1 - lon0) * fx), (y1 - y0) / (lat1 - lat0))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    def f(lon, lat):
        return cx + (lon - mlon) * k * fx, cy - (lat - mlat) * k
    f.k = k
    return f


LAND = {
    "indochina_malaya": [(98.3, 8.0), (98.5, 7.8), (99.0, 7.0), (100.1, 6.4), (100.3, 5.4), (100.6, 4.2), (101.3, 2.8),
                         (102.5, 1.9), (103.4, 1.3), (104.3, 1.4), (103.9, 2.6), (103.4, 3.9), (103.4, 4.9), (102.3, 6.2),
                         (101.4, 6.9), (100.3, 7.4), (100.0, 8.5), (99.3, 9.5), (99.2, 10.6), (99.6, 11.8), (100.0, 12.5),
                         (100.9, 13.4), (102.3, 12.2), (103.0, 11.0), (104.5, 10.4), (104.8, 8.6), (106.5, 9.5), (107.0, 10.5),
                         (109.0, 11.3), (109.3, 12.5), (109.2, 13.8), (108.8, 15.3), (108.2, 16.5), (107.0, 17.5), (106.0, 19.0),
                         (106.5, 20.5), (108.0, 21.5), (110.0, 21.5), (112.0, 21.8), (116.0, 22.8), (120.0, 24.5), (122.0, 30.0), (125.0, 50.0),
                         (100.0, 50.0), (90.0, 50.0), (90.0, 30.0), (89.0, 22.0), (91.5, 22.5), (92.5, 20.5), (94.0, 18.5), (94.5, 16.0),
                         (97.0, 16.5), (97.7, 16.0), (97.8, 14.5), (98.5, 12.5), (98.6, 10.5), (98.3, 8.0)],
    "sumatra": [(95.3, 5.6), (97.5, 5.2), (98.7, 3.8), (100.4, 2.2), (101.4, 1.6), (102.8, 0.7), (103.8, -1.0), (104.6, -2.4),
                (105.9, -4.0), (105.8, -5.8), (104.6, -5.9), (102.3, -4.0), (100.9, -2.0), (99.4, 0.2), (98.6, 1.7), (97.3, 2.9),
                (96.0, 4.3), (95.3, 5.6)],
    "borneo": [(109.0, 1.5), (109.6, 2.0), (111.0, 2.6), (113.0, 3.2), (114.5, 4.6), (115.5, 5.3), (116.5, 6.5), (117.5, 6.8),
               (119.0, 5.2), (118.0, 4.3), (117.8, 1.0), (116.5, -1.0), (116.0, -3.5), (114.5, -3.8), (113.0, -3.2),
               (111.0, -3.0), (110.0, -1.8), (109.0, -0.5), (109.0, 1.5)],
    "java": [(105.2, -6.8), (106.5, -6.0), (108.3, -6.3), (110.5, -6.9), (112.6, -6.9), (114.5, -7.7), (114.4, -8.7),
             (112.0, -8.4), (110.0, -8.1), (108.0, -7.8), (106.4, -7.4), (105.2, -6.8)],
    "india": [(72.8, 24.0), (72.8, 20.0), (73.0, 17.0), (74.0, 14.5), (75.0, 12.0), (76.3, 9.5), (77.5, 8.1), (78.2, 8.9),
              (79.3, 10.3), (80.2, 13.0), (80.3, 15.7), (82.2, 17.0), (84.5, 19.0), (86.5, 20.5), (89.0, 22.0), (90.0, 50.0),
              (60.0, 50.0), (66.0, 25.0), (68.0, 24.0)],
    "srilanka": [(79.9, 7.0), (80.0, 9.6), (80.9, 9.0), (81.9, 7.0), (80.6, 5.9)],
    "australia": [(113.5, -22.0), (114.0, -26.0), (115.0, -30.0), (115.7, -33.5), (117.5, -35.0), (123.0, -34.0),
                  (130.0, -32.0), (140.0, -38.0), (160.0, -45.0), (160.0, -8.0), (140.0, -10.0), (130.0, -11.0), (125.0, -14.0), (122.0, -17.0),
                  (119.0, -20.0), (116.0, -20.5), (114.0, -21.8)],
    "africa": [(-10.0, 50.0), (20.0, 50.0), (32.0, 31.0), (34.0, 28.0), (39.0, 15.0), (43.0, 12.0), (51.0, 11.8), (51.0, 10.4), (49.0, 6.0),
               (46.0, 2.0), (42.0, -1.0), (40.0, -3.0), (39.3, -6.0), (39.5, -10.0), (40.5, -11.0), (40.6, -15.0), (37.0, -18.0),
               (35.5, -21.0), (35.5, -24.0), (33.0, -26.0), (32.6, -28.5), (31.0, -30.0), (28.0, -33.0), (20.0, -35.0), (-10.0, -40.0)],
    "arabia": [(34.5, 50.0), (34.5, 30.0), (36.0, 26.0), (39.0, 21.0), (43.0, 12.6), (45.0, 13.0), (52.0, 15.5), (55.5, 17.5),
               (57.8, 20.5), (59.8, 22.5), (57.0, 25.0), (55.0, 50.0)],
    "madagascar": [(49.3, -12.0), (50.4, -15.5), (49.5, -17.5), (48.7, -20.5), (47.2, -24.8), (45.2, -25.5), (43.7, -23.0),
                   (43.5, -21.5), (44.3, -18.5), (44.0, -17.0), (46.5, -15.7), (48.0, -13.6), (49.3, -12.0)],
}


def draw_map(c, proj, lands=None, grid=10, land_col=(0.19, 0.21, 0.26), sea_col=(0.06, 0.09, 0.14), lw=3):
    """mapa noturno estilizado: mar escuro, grade tracejada, terra em ardósia com contorno de giz"""
    c.rectangle(0, 0, W, H); rgb(c, sea_col); c.fill()
    if grid:
        c.set_dash([4, 12])
        for lon in range(-180, 181, grid):
            x, _ = proj(lon, 0)
            if 0 <= x <= W:
                line(c, x, 0, x, H, 1.5, (0.25, 0.30, 0.38))
        for lat in range(-90, 91, grid):
            _, y = proj(0, lat)
            if 0 <= y <= H:
                line(c, 0, y, W, y, 1.5, (0.25, 0.30, 0.38))
        c.set_dash([])
    for name in (lands or LAND):
        pts = [proj(*p) for p in LAND[name]]
        poly(c, pts)
        fs(c, land_col, lw)


def map_label(c, proj, lon, lat, s, size=30, col=INK, font=TYPE, dx=0, dy=0):
    x, y = proj(lon, lat)
    text(c, s, x + dx, y + dy, size, font, col)


def map_point(c, proj, lon, lat, col=AMBER, r=9, t=0, pulse=True):
    x, y = proj(lon, lat)
    if pulse:
        ph = (t * 0.8) % 1.0
        circle(c, x, y, r + ph * 30, None, 3 * (1 - ph) + 0.1, col)
    circle(c, x, y, r, col, 3, INK)


def map_path(c, proj, pts, p=1.0, col=AMBER, lw=5, dash=None):
    """desenha a fração p (0..1) do caminho (lista de lon/lat)"""
    xy = [proj(*q) for q in pts]
    seg = [math.hypot(xy[i + 1][0] - xy[i][0], xy[i + 1][1] - xy[i][1]) for i in range(len(xy) - 1)]
    tot = sum(seg) * clamp01(p)
    c.move_to(*xy[0])
    end = xy[0]
    for i, L in enumerate(seg):
        if tot <= 0:
            break
        k = min(1, tot / L) if L else 1
        end = (xy[i][0] + (xy[i + 1][0] - xy[i][0]) * k, xy[i][1] + (xy[i + 1][1] - xy[i][1]) * k)
        c.line_to(*end)
        tot -= L
    if dash:
        c.set_dash(dash)
    rgb(c, col); c.set_line_width(lw); c.stroke(); c.set_dash([])
    # direção final
    return end, (xy[min(len(xy) - 1, max(1, i + 1))] if len(xy) > 1 else end)


def plane_top(c, col=(0.86, 0.86, 0.88), s=1.0):
    """avião visto de cima apontando para a direita (gire com c.rotate)"""
    c.save(); c.scale(s, s)
    rrect(c, -46, -7, 92, 14, 7); fs(c, col, 3)
    poly(c, [(8, 0), (-14, -40), (-24, -40), (-10, 0), (-24, 40), (-14, 40)]); fs(c, col, 3)
    poly(c, [(-34, 0), (-44, -15), (-50, -15), (-44, 0), (-50, 15), (-44, 15)]); fs(c, col, 3)
    c.restore()


def plane_on_path(c, proj, pts, p, s=0.6, col=(0.92, 0.92, 0.94)):
    end, nxt = map_path(c, proj, pts, p, (0, 0, 0), 0.01)
    # recalcula direção pelo segmento atual
    xy = [proj(*q) for q in pts]
    seg = [math.hypot(xy[i + 1][0] - xy[i][0], xy[i + 1][1] - xy[i][1]) for i in range(len(xy) - 1)]
    tot = sum(seg) * clamp01(p)
    i = 0
    while i < len(seg) - 1 and tot > seg[i]:
        tot -= seg[i]; i += 1
    a = math.atan2(xy[i + 1][1] - xy[i][1], xy[i + 1][0] - xy[i][0])
    k = min(1, tot / seg[i]) if seg[i] else 1
    x = xy[i][0] + (xy[i + 1][0] - xy[i][0]) * k
    y = xy[i][1] + (xy[i + 1][1] - xy[i][1]) * k
    glow(c, x, y, 70, (1, 1, 1), 0.10)
    c.save(); c.translate(x, y); c.rotate(a); plane_top(c, col, s); c.restore()
    return x, y


# ================================================================ OBJETOS MH370
def satellite(c, t=0):
    for sx in (-1, 1):
        c.save(); c.translate(sx * 95, 0)
        rrect(c, -60, -28, 120, 56, 4); fs(c, (0.20, 0.30, 0.55), 4)
        for k in (-30, 0, 30):
            line(c, k, -28, k, 28, 2, INK)
        line(c, -60, 0, 60, 0, 2, INK)
        c.restore()
        line(c, sx * 35, 0, sx * 35 * 1, 0, 4)
    rrect(c, -35, -40, 70, 80, 8); fs(c, (0.75, 0.62, 0.30), 5)
    line(c, 0, 40, 0, 70, 5)
    c.new_sub_path(); c.arc(0, 85, 22, math.pi * 1.1, math.pi * 1.9)
    rgb(c, INK); c.set_line_width(5); c.stroke()
    circle(c, 0, -20, 6, (1, 0.3, 0.3) if int(t * 2) % 2 == 0 else DGRAY, 0)


def ping(c, t, t0, x1, y1, x2, y2, col=ICE, d=0.9):
    """pulso viajando de (x1,y1) até (x2,y2)"""
    if t < t0 or t > t0 + d + 0.5:
        return
    p = clamp01((t - t0) / d)
    x = x1 + (x2 - x1) * p; y = y1 + (y2 - y1) * p
    c.set_dash([6, 10])
    line(c, x1, y1, x, y, 2, col)
    c.set_dash([])
    glow(c, x, y, 40, col, 0.6 * (1 - prog(t, t0 + d, 0.5)))
    circle(c, x, y, 7, col, 0)


def radio_tower(c, t=0, waves=True):
    poly(c, [(-40, 160), (0, -120), (40, 160)]); fs(c, DGRAY, 5)
    for y in (0, 60, 120):
        w = 40 * (y + 120) / 280
        line(c, -w, y, w, y, 4)
    circle(c, 0, -125, 10, RED if int(t * 1.5) % 2 == 0 else BLOOD, 3)
    if waves:
        for i in range(3):
            ph = ((t * 0.7) + i / 3) % 1.0
            r = 30 + ph * 110
            for sx in (-1, 1):
                c.new_sub_path()
                a0 = -0.6 if sx > 0 else math.pi - 0.6
                c.arc(0, -125, r, a0, a0 + 1.2)
                rgb(c, ICE, 1 - ph); c.set_line_width(4); c.stroke()


def sonar_ship(c, t=0):
    c.move_to(-200, -10); c.line_to(200, -10); c.line_to(170, 40); c.line_to(-180, 40); c.close_path()
    fs(c, (0.62, 0.20, 0.18), 6)
    rrect(c, -60, -80, 140, 70, 6); fs(c, (0.85, 0.83, 0.76), 5)
    for x in (-40, -5, 30):
        c.rectangle(x, -65, 22, 18); fs(c, LYELLOW, 3)
    line(c, 40, -80, 40, -140, 5)
    line(c, 20, -120, 60, -120, 4)
    circle(c, 40, -142, 6, RED if int(t * 2) % 2 == 0 else BLOOD, 0)


def seabed(c, t=0, y=0, w=2200, seed=4, col=(0.13, 0.15, 0.18)):
    """perfil de montanhas submarinas (desenhado a partir de y para baixo)"""
    rnd = random.Random(seed)
    c.move_to(-w / 2, y + 400)
    x = -w / 2
    pts = []
    while x <= w / 2:
        h = 60 + 120 * abs(math.sin(x / 210 + seed)) + rnd.uniform(0, 70)
        pts.append((x, y - h))
        x += 70
    c.line_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.line_to(w / 2, y + 400)
    c.close_path()
    fs(c, col, 5)


def sonar_beam(c, t, x, y, depth=520, spread=0.55, col=ICE):
    a = math.pi / 2 + math.sin(t * 1.4) * 0.35
    g = cairo.RadialGradient(x, y, 0, x, y, depth)
    g.add_color_stop_rgba(0, col[0], col[1], col[2], 0.35)
    g.add_color_stop_rgba(1, col[0], col[1], col[2], 0.0)
    c.move_to(x, y)
    c.arc(x, y, depth, a - spread / 2, a + spread / 2)
    c.close_path()
    c.set_source(g); c.fill()
    for i in range(3):
        ph = ((t * 0.9) + i / 3) % 1
        c.new_sub_path(); c.arc(x, y, ph * depth, a - spread / 2, a + spread / 2)
        rgb(c, col, 0.5 * (1 - ph)); c.set_line_width(3); c.stroke()


def flaperon(c):
    poly(c, [(-170, -30), (150, -45), (175, -20), (160, 25), (-160, 35), (-180, 10)])
    fs(c, (0.80, 0.80, 0.76), 6)
    for x in (-110, -40, 30, 100):
        line(c, x, -36, x + 4, 30, 3, (0.55, 0.55, 0.52))
    for x, y, r in ((-120, 0, 9), (60, -10, 7), (130, 5, 6)):
        circle(c, x, y, r, (0.45, 0.50, 0.40), 0)


def auv(c, t=0):
    """robô submarino autônomo"""
    rrect(c, -150, -32, 300, 64, 32); fs(c, LYELLOW, 6)
    poly(c, [(-150, 0), (-195, -40), (-195, 40)]); fs(c, ORANGE, 5)
    circle(c, 120, 0, 14, ICE, 4)
    line(c, -20, -32, -20, -60, 5)
    g = 0.5 + 0.5 * math.sin(t * 5)
    glow(c, 160, 0, 120 * g + 40, ICE, 0.35)


def black_box(c):
    rrect(c, -110, -75, 220, 150, 10); fs(c, ORANGE, 6)
    for y in (-40, 40):
        c.rectangle(-110, y - 8, 220, 16); rgb(c, (0.9, 0.9, 0.85)); c.fill()
    rrect(c, -110, -75, 220, 150, 10); rgb(c, INK); c.set_line_width(6); c.stroke()
    text(c, "FLIGHT RECORDER", 0, 0, 22, TYPE, DARKTXT)


def monitor(c, fn=None, w=420, h=270):
    rrect(c, -w / 2, -h / 2, w, h, 12); fs(c, DGRAY, 6)
    c.save()
    c.rectangle(-w / 2 + 18, -h / 2 + 18, w - 36, h - 36); c.clip_preserve()
    rgb(c, (0.04, 0.08, 0.10)); c.fill()
    if fn:
        fn(c)
    c.restore()
    poly(c, [(-30, h / 2), (30, h / 2), (50, h / 2 + 50), (-50, h / 2 + 50)]); fs(c, DGRAY, 5)


def cockpit_door(c):
    rrect(c, -110, -170, 220, 340, 8); fs(c, (0.30, 0.32, 0.36), 6)
    rrect(c, -70, -130, 140, 90, 8); fs(c, (0.12, 0.14, 0.18), 4)
    rrect(c, -18, -10, 36, 50, 6); fs(c, DGRAY, 4)
    circle(c, 0, 10, 8, RED, 3)
    circle(c, 70, 40, 12, (0.6, 0.6, 0.62), 4)


def oxygen_mask(c, t=0):
    sw = math.sin(t * 2.2) * 8
    line(c, 0, -160, sw, -40, 3)
    ellipse(c, sw, 0, 40, 46); fs(c, (0.86, 0.80, 0.70), 5)
    rrect(c, sw - 22, -10, 44, 30, 10); fs(c, (0.70, 0.66, 0.58), 4)


def crowd(c, t, t0, n=239, cols=24, sp=46, highlight=None, appear_d=2.2, s=0.18):
    """grade de bonequinhos minúsculos; highlight(i)->cor opcional"""
    for i in range(n):
        if t < t0 + (i / n) * appear_d:
            break
        r, k = divmod(i, cols)
        x = (k - (cols - 1) / 2) * sp
        y = r * sp * 1.25
        col = highlight(i) if highlight else LGRAY
        c.save(); c.translate(x, y); c.scale(s * 5, s * 5)
        circle(c, 0, -14, 6, FILL, 2.2)
        line(c, 0, -8, 0, 4, 2.2); line(c, -6, -3, 6, -3, 2.2)
        line(c, 0, 4, -4, 12, 2.2); line(c, 0, 4, 4, 12, 2.2)
        if col:
            circle(c, 0, -14, 6, col, 0)
        c.restore()


def pilot(c, t, x, y, s, poses=((0, "stand"),), exprs=((0, "neutral"),), fid=6, stripes=4, **kw):
    """piloto: camisa branca, quepe"""
    figure(c, t, x, y, s, poses=poses, exprs=exprs, shirt=(0.88, 0.88, 0.86), hair=None, fid=fid, hat="pilot", **kw)


def pilot_cap(c, hr):
    rrect(c, -50, -hr - 30, 100, 34, 10); fs(c, (0.12, 0.14, 0.22), 5)
    ellipse(c, 6, -hr + 6, 56, 10); fs(c, (0.08, 0.08, 0.10), 4)
    circle(c, 0, -hr - 14, 8, AMBER, 2)


# ================================================================ OBJETOS MARÍTIMOS (Mary Celeste)
SAIL = (0.80, 0.76, 0.66)
HULL = (0.30, 0.21, 0.14)


def sea(c, t, y=620, rough=0.0, col_top=(0.07, 0.12, 0.18), col_bot=(0.02, 0.04, 0.07), lines=True):
    """mar noturno a partir de y até o fim da tela, com ondas que se movem (rough 0..1 = mar agitado)"""
    g = cairo.LinearGradient(0, y, 0, H)
    g.add_color_stop_rgb(0, *col_top)
    g.add_color_stop_rgb(1, *col_bot)
    c.rectangle(0, y, W, H - y); c.set_source(g); c.fill()
    if not lines:
        return
    amp = 10 + 26 * rough
    for row in range(4):
        yy = y + 20 + row * (60 + row * 30)
        if yy > H:
            break
        step = 140 + row * 60
        sp = (25 + 30 * rough) * (1 + row * 0.6)
        off = (t * sp + row * 57) % step
        a = 0.9 - row * 0.15
        for i in range(-1, int(W / step) + 2):
            x = i * step + off - step
            c.move_to(x, yy); c.curve_to(x + step * 0.25, yy - amp, x + step * 0.5, yy - amp, x + step * 0.75, yy)
        rgb(c, BLUE, a); c.set_line_width(4 - row * 0.6); c.stroke()


def _jag(c, x0, x1, y, n, seed, depth):
    rnd = random.Random(seed)
    for k in range(n + 1):
        x = x1 + (x0 - x1) * k / n
        c.line_to(x, y - (rnd.uniform(0.2, 1.0) * depth if 0 < k < n else 0))


def brigantine(c, t=0, torn=0.0, name=None, sail=SAIL, hull=HULL, sails=True, rigging=True):
    """bergantim (veleiro de dois mastros) visto de lado, proa para a direita; origem = linha d'água.
    torn 0..1 rasga as velas (bordas irregulares e velas faltando)."""
    sail_lw = 4
    # mastros e gurupés
    line(c, 175, -38, 330, -92, 7)
    line(c, 70, -30, 70, -410, 8)
    line(c, -80, -30, -80, -430, 8)
    if rigging:
        for a, b in (((-80, -430), (-228, -42)), ((70, -410), (215, -40)), ((70, -410), (-80, -400)),
                     ((-80, -430), (60, -60)), ((70, -410), (330, -92))):
            line(c, a[0], a[1], b[0], b[1], 2, (0.6, 0.57, 0.5))
    if sails:
        # velas redondas no mastro de vante (3 panos)
        rows = [(-392, -305, 62, 78), (-298, -205, 80, 100), (-198, -84, 102, 120)]
        for i, (y0, y1, w0, w1) in enumerate(rows):
            line(c, 70 - w0 - 8, y0, 70 + w0 + 8, y0, 6)
            if torn > 0.5 and i == 1:
                # pano arrancado: só uma tira presa na verga
                c.move_to(70 - w0, y0); c.line_to(70 + w0, y0)
                _jag(c, 70 - w0, 70 + w0, y0 + 26, 7, 11, 18)
                c.close_path(); fs(c, sail, sail_lw)
                continue
            c.move_to(70 - w0, y0); c.line_to(70 + w0, y0)
            c.line_to(70 + w1, y1)
            if torn > 0:
                _jag(c, 70 - w1, 70 + w1, y1, 8, 20 + i, 40 * torn)
            else:
                c.curve_to(70 + w1 * 0.4, y1 - 14, 70 - w1 * 0.4, y1 - 14, 70 - w1, y1)
            c.close_path(); fs(c, sail, sail_lw)
        # vela grande latina no mastro principal (carangueja + retranca)
        line(c, -80, -372, -232, -404, 6)
        line(c, -80, -76, -262, -66, 6)
        c.move_to(-86, -368); c.line_to(-226, -396)
        if torn > 0:
            c.line_to(-255, -72)
            _jag(c, -255, -86, -80, 6, 31, 30 * torn) if False else None
            c.line_to(-86, -82)
        else:
            c.curve_to(-262, -280, -270, -150, -255, -72); c.line_to(-86, -82)
        c.close_path(); fs(c, sail, sail_lw)
        if torn > 0:
            # rasgo em diagonal
            c.move_to(-120, -300); c.line_to(-160, -250); c.line_to(-140, -240); c.line_to(-190, -180)
            rgb(c, (0.07, 0.08, 0.10)); c.set_line_width(10 * torn); c.stroke()
        # bujarrona (triângulo na proa)
        if torn < 0.8:
            poly(c, [(76, -380), (318, -96), (170, -60)]); fs(c, sail, sail_lw)
    # casco
    c.move_to(-238, -46); c.line_to(228, -46)
    c.curve_to(214, 0, 180, 34, 120, 44); c.line_to(-190, 44)
    c.curve_to(-218, 30, -232, 0, -238, -46); c.close_path()
    fs(c, hull, 6)
    line(c, -232, -18, 214, -18, 3, (0.55, 0.42, 0.28))
    line(c, -242, -56, 232, -56, 5)
    for x in range(-220, 230, 34):
        line(c, x, -56, x, -46, 3)
    if name:
        text(c, name, -40, 10, 24, TYPE, PARCH)


def barrel(c, empty=False, col=BROWN, label=None):
    """barril de madeira (~120 x 170)"""
    c.move_to(-48, -82); c.curve_to(-70, -40, -70, 40, -48, 82); c.line_to(48, 82)
    c.curve_to(70, 40, 70, -40, 48, -82); c.close_path()
    fs(c, (0.15, 0.12, 0.10) if empty else col, 6)
    for x in (-24, 0, 24):
        line(c, x, -80, x, 80, 2, (0.30, 0.20, 0.12))
    for y in (-52, 52):
        c.move_to(-62, y); c.curve_to(-30, y + 6, 30, y + 6, 62, y)
        rgb(c, (0.20, 0.20, 0.22)); c.set_line_width(9); c.stroke()
    ellipse(c, 0, -82, 48, 12); fs(c, (0.52, 0.38, 0.24) if not empty else (0.12, 0.10, 0.09), 5)
    if label:
        text(c, label, 0, 4, 30, TYPE, DARKTXT if not empty else INK)


def lifeboat(c, people=0, oars=False, col=(0.55, 0.40, 0.26)):
    """bote salva-vidas (escaler) de lado; origem = linha d'água; people = cabeças a bordo"""
    rnd = random.Random(5)
    for i in range(people):
        x = -95 + i * (190 / max(1, people - 1)) if people > 1 else 0
        y = -48 - rnd.uniform(0, 8)
        line(c, x, -18, x, y + 14, 5)
        circle(c, x, y, 13, FILL, 4)
    if oars:
        line(c, -40, -30, -120, 30, 5); line(c, 40, -30, 120, 30, 5)
    c.move_to(-140, -26); c.line_to(140, -26); c.curve_to(120, 12, 80, 22, 40, 24); c.line_to(-60, 24)
    c.curve_to(-110, 20, -132, 4, -140, -26); c.close_path()
    fs(c, col, 6)
    line(c, -136, -14, 130, -14, 3, (0.35, 0.25, 0.16))


def sextant(c):
    br = (0.72, 0.58, 0.30)
    poly(c, [(0, -110), (-92, 70), (92, 70)]); rgb(c, INK); c.set_line_width(7); c.stroke()
    c.new_sub_path(); c.arc(0, -110, 190, math.pi * 0.36, math.pi * 0.64)
    rgb(c, br); c.set_line_width(22); c.stroke()
    for k in range(9):
        a = math.pi * (0.37 + k * 0.03)
        line(c, 180 * math.cos(a), -110 + 180 * math.sin(a), 198 * math.cos(a), -110 + 198 * math.sin(a), 2, DARKTXT)
    line(c, 0, -110, 40, 76, 6, br)
    c.rectangle(-14, -128, 28, 34); fs(c, ICE, 4)
    rrect(c, -110, -40, 70, 26, 10); fs(c, (0.25, 0.25, 0.28), 4)
    circle(c, 0, -110, 10, br, 4)


def chronometer(c, t=0, wrong=False):
    rrect(c, -120, -100, 240, 200, 14); fs(c, (0.42, 0.28, 0.17), 6)
    circle(c, 0, 0, 74, (0.85, 0.82, 0.72), 6)
    for k in range(12):
        a = k * math.pi / 6
        line(c, 60 * math.cos(a), 60 * math.sin(a), 68 * math.cos(a), 68 * math.sin(a), 3, DARKTXT)
    a1 = t * (0.9 if wrong else 0.05) - math.pi / 2
    a2 = t * (0.12 if wrong else 0.004) + 0.6
    line(c, 0, 0, 52 * math.cos(a1), 52 * math.sin(a1), 4, DARKTXT)
    line(c, 0, 0, 34 * math.cos(a2), 34 * math.sin(a2), 6, DARKTXT)
    circle(c, 0, 0, 6, BLOOD, 0)


def spyglass(c):
    c.save(); c.rotate(-0.25)
    for x0, x1, r, col in ((-150, -40, 22, (0.40, 0.28, 0.18)), (-40, 60, 18, (0.72, 0.58, 0.30)), (60, 150, 14, (0.72, 0.58, 0.30))):
        c.rectangle(x0, -r, x1 - x0, 2 * r); fs(c, col, 5)
    ellipse(c, -150, 0, 8, 24); fs(c, ICE, 4)
    c.restore()


def ship_wheel(c, t=0, spin=0.0):
    c.save(); c.rotate(t * spin)
    for k in range(8):
        a = k * math.pi / 4
        line(c, 0, 0, 125 * math.cos(a), 125 * math.sin(a), 9, (0.50, 0.36, 0.22))
        circle(c, 125 * math.cos(a), 125 * math.sin(a), 10, (0.50, 0.36, 0.22), 4)
    circle(c, 0, 0, 92, None, 16, (0.50, 0.36, 0.22))
    circle(c, 0, 0, 100, None, 3, INK); circle(c, 0, 0, 84, None, 3, INK)
    circle(c, 0, 0, 22, AMBER, 5)
    c.restore()


def sword(c, stains=False):
    poly(c, [(-60, -9), (190, -6), (220, 0), (190, 6), (-60, 9)]); fs(c, (0.78, 0.80, 0.84), 4)
    line(c, -50, 0, 180, 0, 2, (0.55, 0.57, 0.62))
    rrect(c, -72, -46, 16, 92, 6); fs(c, AMBER, 4)
    rrect(c, -150, -11, 80, 22, 8); fs(c, (0.30, 0.20, 0.14), 4)
    circle(c, -156, 0, 14, AMBER, 4)
    if stains:
        rnd = random.Random(9)
        for _ in range(7):
            circle(c, rnd.uniform(20, 140), rnd.uniform(-5, 5), rnd.uniform(3, 7), (0.45, 0.28, 0.16), 0)


def teacup(c, t=0, steam=True):
    ellipse(c, 0, 40, 120, 18); fs(c, (0.85, 0.83, 0.78), 5)
    c.move_to(-75, -30); c.curve_to(-70, 40, 70, 40, 75, -30); c.close_path(); fs(c, (0.90, 0.88, 0.82), 5)
    c.new_sub_path(); c.arc(86, 0, 22, -math.pi / 2, math.pi / 2); rgb(c, INK); c.set_line_width(7); c.stroke()
    ellipse(c, 0, -30, 75, 12); fs(c, (0.45, 0.28, 0.14), 4)
    if steam:
        for i, x in enumerate((-30, 0, 30)):
            ph = t * 1.4 + i
            c.move_to(x, -50)
            for k in range(1, 5):
                c.line_to(x + 12 * math.sin(ph + k), -50 - k * 28)
            rgb(c, INK, 0.45); c.set_line_width(4); c.stroke()


def stove(c, t=0):
    rrect(c, -90, -60, 180, 140, 8); fs(c, (0.22, 0.22, 0.25), 6)
    c.rectangle(-50, -10, 100, 60); fs(c, (0.12, 0.12, 0.14), 4)
    glow(c, 0, 20, 60, ORANGE, 0.35 + 0.1 * math.sin(t * 5))
    line(c, -70, 80, -70, 110, 8); line(c, 70, 80, 70, 110, 8)
    rrect(c, -50, -110, 100, 50, 10); fs(c, (0.40, 0.40, 0.44), 5)
    line(c, 50, -95, 90, -105, 6)


def sea_chest(c):
    rrect(c, -110, -50, 220, 110, 8); fs(c, (0.45, 0.31, 0.19), 6)
    poly(c, [(-110, -50), (110, -50), (95, -100), (-95, -100)]); fs(c, (0.52, 0.37, 0.23), 6)
    for x in (-70, 70):
        c.rectangle(x - 8, -100, 16, 160); fs(c, (0.25, 0.25, 0.28), 3)
    c.rectangle(-14, -30, 28, 30); fs(c, AMBER, 3)


def folded_clothes(c):
    for i, col in enumerate(((0.30, 0.36, 0.52), (0.62, 0.58, 0.50), (0.48, 0.24, 0.20))):
        rrect(c, -90, -20 - i * 34, 180, 32, 8); fs(c, col, 5)


def pump(c, broken=True):
    rrect(c, -30, -120, 60, 200, 10); fs(c, (0.40, 0.42, 0.46), 6)
    line(c, 0, -120, 0, -170, 8)
    if broken:
        c.save(); c.translate(120, 70); c.rotate(0.3)
        line(c, -70, 0, 70, 0, 9); circle(c, -70, 0, 10, AMBER, 4)
        c.restore()
        for x, y in ((90, 10), (150, 30)):
            circle(c, x, y, 14, (0.40, 0.42, 0.46), 4)
    else:
        line(c, 0, -170, 90, -200, 9)
    rrect(c, -55, 70, 110, 22, 6); fs(c, (0.30, 0.31, 0.35), 5)


def sounding_rod(c):
    c.save(); c.rotate(-0.08)
    rrect(c, -220, -9, 440, 18, 6); fs(c, (0.62, 0.48, 0.30), 4)
    for k in range(1, 12):
        x = -220 + k * 36
        line(c, x, -9, x, 9 if k % 3 else 14, 3, DARKTXT)
    line(c, 220, 0, 300, -40, 3, (0.7, 0.66, 0.56))
    c.restore()


def hatch(c, open_=True):
    rrect(c, -130, -60, 260, 120, 6); fs(c, (0.05, 0.05, 0.06), 6)
    if open_:
        c.save(); c.translate(-130, -60); c.rotate(-0.5)
        rrect(c, 0, -110, 260, 110, 6); fs(c, (0.50, 0.36, 0.22), 6)
        c.restore()


def waterspout(c, t=0, h=620):
    """tromba d'água: funil do céu (y=-h) até o mar (y=0)"""
    for i in range(3):
        a = 0.18 - i * 0.05
        c.move_to(-220 + i * 40, -h); c.curve_to(-60, -h * 0.55, -26, -h * 0.25, -18 - i * 4, 0)
        c.line_to(18 + i * 4, 0); c.curve_to(26, -h * 0.25, 60, -h * 0.55, 220 - i * 40, -h); c.close_path()
        rgb(c, (0.62, 0.66, 0.72), a); c.fill()
    for k in range(9):
        p = ((t * 0.6 + k / 9) % 1)
        y = -h * p
        w = 18 + 200 * p ** 2
        c.save(); c.translate(0, y); c.scale(1, 0.18)
        c.new_sub_path(); c.arc(0, 0, w, 0.2 + t * 3, 2.6 + t * 3)
        c.restore(); rgb(c, INK, 0.35); c.set_line_width(3); c.stroke()
    for k in range(10):
        ph = (t * 1.3 + k * 0.37) % 1
        x = (k - 4.5) * 22 * (1 + ph)
        circle(c, x, -ph * 60, 4, None, 2, (0.75, 0.85, 0.95))
    cloud_shape(c, 620, 140, (0.16, 0.17, 0.20), 6, 5) if False else None


def storm_cloud(c, w=700, h=150):
    cloud_shape(c, w, h, (0.16, 0.17, 0.20), 6, 5)


def lightning(c, s=1.0):
    c.save(); c.scale(s, s)
    poly(c, [(0, -160), (-40, -10), (-6, -10), (-34, 150), (50, -40), (12, -40), (40, -160)])
    fs(c, LYELLOW, 4)
    c.restore()


def flag(c, kind="us", t=0):
    """bandeira num mastro (origem = topo do mastro). kind: us | ensign (red ensign britânico/canadense)"""
    line(c, 0, -10, 0, 260, 6)
    wv = lambda x: 6 * math.sin(t * 3 + x / 30)
    w, h = 220, 140
    def path():
        c.move_to(0, 0)
        for x in range(0, w + 1, 20):
            c.line_to(x, wv(x))
        for x in range(w, -1, -20):
            c.line_to(x, h + wv(x))
        c.close_path()
    if kind == "us":
        path(); fs(c, (0.88, 0.86, 0.80), 5)
        for i in range(0, 7, 2):
            y0 = i * h / 7
            c.move_to(0, y0 + wv(0))
            for x in range(0, w + 1, 20):
                c.line_to(x, y0 + wv(x))
            for x in range(w, -1, -20):
                c.line_to(x, y0 + h / 7 + wv(x))
            c.close_path(); rgb(c, RED); c.fill()
        c.rectangle(2, 2 + wv(40), 92, 74); rgb(c, (0.18, 0.24, 0.45)); c.fill()
        for i in range(3):
            for j in range(4):
                circle(c, 14 + j * 22, 16 + wv(40) + i * 22, 3.5, INK, 0)
    else:
        path(); fs(c, RED, 5)
        c.rectangle(2, 2 + wv(40), 100, 66); rgb(c, (0.18, 0.24, 0.45)); c.fill()
        line(c, 2, 2 + wv(40), 102, 68 + wv(40), 6, INK); line(c, 102, 2 + wv(40), 2, 68 + wv(40), 6, INK)
        line(c, 52, 2 + wv(40), 52, 68 + wv(40), 10, INK); line(c, 2, 35 + wv(40), 102, 35 + wv(40), 10, INK)
        line(c, 52, 2 + wv(40), 52, 68 + wv(40), 5, RED); line(c, 2, 35 + wv(40), 102, 35 + wv(40), 5, RED)


def tombstone(c, label=""):
    c.move_to(-80, 110); c.line_to(-80, -40); c.arc(0, -40, 80, math.pi, 2 * math.pi); c.line_to(80, 110); c.close_path()
    fs(c, (0.32, 0.33, 0.36), 6)
    line(c, 0, -60, 0, 10, 6); line(c, -24, -36, 24, -36, 6)
    if label:
        text(c, label, 0, 55, 26, TYPE, INK)


def nameboard(c, s, size=46, w=None):
    """placa de nome do navio (madeira com letras douradas)"""
    w = w or text_w(c, s, size, SERIF) + 80
    rrect(c, -w / 2, -size * 0.8, w, size * 1.6, 12); fs(c, (0.34, 0.23, 0.14), 6)
    text(c, s, 0, 0, size, SERIF, AMBER)


def coal(c):
    rnd = random.Random(4)
    for _ in range(26):
        x, y = rnd.gauss(0, 60), -abs(rnd.gauss(0, 30))
        r = rnd.uniform(14, 26)
        poly(c, [(x + r * math.cos(a + 0.3), y + r * math.sin(a + 0.3) * 0.8) for a in [k * 1.2 for k in range(6)]])
        fs(c, (0.10, 0.10, 0.11), 3)


def gavel(c):
    c.save(); c.rotate(-0.5)
    rrect(c, -10, -20, 20, 180, 8); fs(c, (0.45, 0.30, 0.18), 4)
    rrect(c, -70, -60, 140, 60, 14); fs(c, (0.40, 0.26, 0.15), 5)
    c.restore()
    rrect(c, -40, 150, 160, 30, 8); fs(c, (0.40, 0.26, 0.15), 5)


def tree_rings(c, n=12, r=150):
    rnd = random.Random(2)
    circle(c, 0, 0, r + 14, (0.36, 0.25, 0.16), 6)
    circle(c, 0, 0, r, (0.72, 0.58, 0.40), 3)
    for k in range(1, n):
        rr = r * k / n
        c.new_sub_path()
        for a in range(0, 361, 15):
            q = rr + rnd.uniform(-3, 3)
            x, y = q * math.cos(math.radians(a)), q * math.sin(math.radians(a))
            (c.move_to if a == 0 else c.line_to)(x, y)
        c.close_path(); rgb(c, (0.45, 0.32, 0.20)); c.set_line_width(2.5); c.stroke()


def reef(c, t=0, w=700):
    rnd = random.Random(6)
    pts = [(-w / 2, 40)]
    x = -w / 2
    while x < w / 2:
        x += rnd.uniform(40, 80)
        pts.append((min(x, w / 2), -rnd.uniform(10, 70)))
    pts.append((w / 2, 40))
    poly(c, pts); fs(c, (0.20, 0.21, 0.23), 5)
    for k in range(6):
        ph = (t * 0.7 + k / 6) % 1
        xx = -w / 2 + k * w / 6 + 40
        circle(c, xx, -10 - ph * 40, 6 + ph * 12, None, 3 * (1 - ph) + 0.1, INK)


def azores(c, proj, labels=False, col=(0.22, 0.25, 0.30), only=None):
    """ilhas dos Açores (elipses estilizadas)"""
    isl = {"Flores": (-31.2, 39.45, 0.35, 0.18), "Faial": (-28.7, 38.58, 0.25, 0.12), "Pico": (-28.3, 38.47, 0.45, 0.12),
           "São Jorge": (-28.0, 38.65, 0.55, 0.08), "Terceira": (-27.2, 38.72, 0.32, 0.14),
           "São Miguel": (-25.5, 37.78, 0.70, 0.15), "Santa Maria": (-25.1, 36.97, 0.18, 0.12)}
    for nm, (lon, lat, rx, ry) in isl.items():
        if only and nm not in only:
            continue
        x, y = proj(lon, lat)
        ellipse(c, x, y, max(5, rx * proj.k), max(4, ry * proj.k)); fs(c, col, 3)
        if labels:
            text(c, nm, x, y + max(4, ry * proj.k) + 26, 24, TYPE, INK)


LAND.update({
    "n_america": [(-100, 62), (-64, 60), (-61, 56), (-56, 52), (-55.5, 49.5), (-59.5, 47.6), (-61, 45.6), (-60, 46.2), (-62.5, 45.6),
                  (-66, 43.5), (-66.2, 45.1), (-67.5, 44.5), (-70, 43.8), (-70.6, 42.6), (-70, 41.7), (-72, 41.1), (-74, 40.6),
                  (-74, 39.5), (-75.5, 37.5), (-76, 35), (-78, 33.8), (-81, 31.5), (-81.2, 29.5), (-80, 26.5), (-80.3, 25.2),
                  (-81.5, 25.5), (-83, 28), (-85, 30), (-90, 30), (-100, 28)],
    "newfoundland": [(-59.4, 47.6), (-56, 51.6), (-55.5, 49.6), (-53, 48.6), (-52.6, 47.5), (-53.6, 46.6), (-55.8, 47.0), (-59.4, 47.6)],
    "europe": [(-5.6, 36.0), (-6.3, 36.8), (-7.4, 37.2), (-8.8, 37.0), (-8.8, 38.5), (-9.5, 38.8), (-8.8, 40.5), (-8.9, 42.0),
               (-9.3, 43.0), (-8.0, 43.7), (-1.8, 43.4), (-1.2, 46.0), (-2.5, 47.3), (-4.7, 48.4), (-1.5, 48.8), (1.5, 50.1),
               (3.0, 51.2), (5.0, 53.4), (8.0, 54.0), (9, 57), (10.5, 59), (12, 62), (40, 62), (40, 41), (29, 41), (26, 40.5),
               (24, 38), (22.5, 36.5), (21, 38.5), (19.5, 41), (19.5, 42.2), (15.5, 44.5), (13.8, 45.6), (12.3, 45.4), (12.5, 44),
               (14, 42), (16, 41.5), (18.5, 40.2), (16.5, 38.9), (15.7, 38), (15.6, 40), (12.3, 41.7), (10.5, 43), (8.9, 44.4),
               (6, 43.1), (3.2, 43.3), (3.2, 42), (0.5, 40.5), (-0.3, 39.5), (-0.5, 38.3), (-2, 36.7), (-4.5, 36.7), (-5.6, 36.0)],
    "britain": [(-5.7, 50.0), (1.4, 51.2), (1.7, 52.7), (0, 53.5), (-1.6, 55.6), (-2, 57.6), (-3.3, 58.6), (-5, 58.6), (-6.2, 56.8),
                (-5.4, 55.0), (-3, 54.5), (-3.2, 53.4), (-4.6, 53.2), (-4.2, 52.2), (-5.2, 51.7), (-3.4, 51.4), (-5.7, 50.0)],
    "ireland": [(-6, 52.2), (-6, 54), (-7.4, 55.3), (-10, 54.2), (-10.3, 51.7), (-8.2, 51.6), (-6, 52.2)],
    "nw_africa": [(-5.9, 35.8), (-6.8, 34.0), (-9.6, 30.4), (-9.8, 29.0), (-13, 27.7), (-16, 23.5), (-17, 21), (-16.5, 19),
                  (-17.5, 14.7), (-16.7, 12), (-15, 5), (20, 5), (20, 33), (11, 37), (10, 37.3), (3, 36.8), (-2, 35.1), (-5.3, 35.9)],
    "sardinia_sicily": [(8.4, 39.0), (9.8, 39.2), (9.8, 41.0), (9.2, 41.2), (8.2, 40.9), (8.4, 39.0)],
})
ATLANTIC = ["n_america", "newfoundland", "europe", "britain", "ireland", "nw_africa", "sardinia_sicily"]


# ================================================================ América do Sul / Amazônia (Fawcett e a Cidade de Z)
LAND.update({
    "s_america": [(-77.3, 8.6), (-75.5, 10.5), (-72.0, 11.8), (-71.3, 12.4), (-70.0, 12.0), (-68.0, 10.6), (-64.0, 10.6),
                  (-61.5, 10.7), (-60.0, 8.5), (-57.0, 6.0), (-54.0, 5.7), (-51.5, 4.4), (-50.0, 1.8), (-50.5, 0.0),
                  (-48.5, -1.0), (-44.5, -2.5), (-41.0, -3.0), (-38.5, -3.7), (-35.3, -5.2), (-34.9, -8.0), (-35.6, -9.7),
                  (-37.5, -12.0), (-38.9, -13.5), (-39.0, -17.5), (-40.0, -20.0), (-41.0, -22.0), (-43.2, -23.0),
                  (-45.5, -23.8), (-48.5, -26.0), (-48.7, -28.5), (-50.5, -31.0), (-52.5, -33.5), (-54.0, -34.8),
                  (-56.5, -34.9), (-58.4, -34.5), (-57.5, -36.5), (-57.6, -38.2), (-62.0, -39.0), (-62.3, -40.8),
                  (-65.0, -41.0), (-65.0, -42.5), (-64.5, -43.0), (-65.5, -45.0), (-67.5, -46.5), (-66.0, -48.0),
                  (-68.5, -50.5), (-69.0, -52.5), (-68.5, -54.5), (-70.5, -55.0), (-73.0, -53.0), (-75.0, -50.0),
                  (-74.5, -46.0), (-73.5, -43.0), (-73.5, -38.0), (-71.5, -33.0), (-71.4, -29.0), (-70.4, -23.5),
                  (-70.2, -18.3), (-71.5, -17.0), (-75.0, -15.5), (-76.3, -13.5), (-77.2, -12.0), (-79.0, -8.5),
                  (-81.2, -6.0), (-81.0, -4.0), (-80.0, -2.5), (-80.9, -1.0), (-80.0, 1.0), (-78.9, 1.5), (-77.5, 4.0),
                  (-77.3, 7.0), (-79.5, 9.0), (-83.0, 9.5), (-90.0, 15.0), (-100.0, 20.0), (-100.0, 30.0), (-60, 30)],
})
SOUTH_AMERICA = ["s_america"]
# fronteira Brasil x Bolívia (aprox.), rios principais (aprox., lon/lat)
BR_BO_BORDER = [(-69.6, -11.0), (-68.7, -11.0), (-66.0, -9.8), (-65.3, -10.9), (-63.0, -12.6), (-61.5, -13.5), (-60.3, -15.0),
                (-60.2, -16.3), (-58.4, -16.3), (-58.0, -17.5), (-57.6, -19.0)]
RIVER_XINGU = [(-53.3, -14.6), (-53.2, -13.2), (-52.9, -12.0), (-53.0, -10.5), (-52.6, -8.5), (-52.0, -6.5), (-52.3, -4.5),
               (-52.2, -3.2), (-52.0, -1.6)]
RIVER_AMAZONAS = [(-70.0, -4.2), (-65.0, -3.5), (-60.0, -3.1), (-56.0, -2.5), (-52.0, -1.6), (-50.5, -0.8)]


def jungle_tree(c, h=320, col=(0.12, 0.20, 0.16), seed=1, edge=0.55):
    """árvore de floresta tropical: tronco fino e copa em nuvem (base em 0,0)"""
    rnd = random.Random(seed)
    tw = h * 0.05
    poly(c, [(-tw, 0), (-tw * 0.6, -h * 0.62), (tw * 0.6, -h * 0.62), (tw, 0)])
    fs(c, (0.10, 0.09, 0.08), 4, (0.30, 0.28, 0.24))
    cx, cy, R = 0, -h * 0.72, h * 0.30
    for i in range(7):
        a = i / 7 * 2 * math.pi + rnd.uniform(-0.3, 0.3)
        r = R * rnd.uniform(0.45, 0.70)
        x, y = cx + math.cos(a) * R * 0.75, cy + math.sin(a) * R * 0.45
        circle(c, x, y, r, col, 4, (0.30 + edge * 0.25, 0.36 + edge * 0.25, 0.31 + edge * 0.2))
    circle(c, cx, cy, R * 0.75, col, 0)
    c.save(); c.translate(cx, cy)
    rgb(c, INK, edge * 0.25)
    for i in range(5):
        a = rnd.uniform(3.4, 6.0)
        c.new_sub_path(); c.arc(rnd.uniform(-R * 0.5, R * 0.5), rnd.uniform(-R * 0.3, R * 0.2), R * 0.25, a, a + 1.1)
        c.set_line_width(3); c.stroke()
    c.restore()


def palm(c, h=300, col=(0.14, 0.24, 0.18), t=0):
    """palmeira (base em 0,0)"""
    c.move_to(-8, 0); c.curve_to(-10, -h * 0.4, 6, -h * 0.7, 14, -h)
    rgb(c, (0.30, 0.26, 0.20)); c.set_line_width(14); c.stroke()
    sw = math.sin(t * 0.7) * 6
    for k in range(7):
        a = -math.pi / 2 + (k - 3) * 0.45
        ex, ey = 14 + math.cos(a) * h * 0.38 + sw, -h + math.sin(a) * h * 0.22 + h * 0.12
        c.move_to(14, -h); c.curve_to(14 + math.cos(a) * h * 0.2, -h - 40, ex - 10, ey - 30, ex, ey)
        rgb(c, col); c.set_line_width(16); c.stroke()


def jungle(c, t, y=1000, w=W, n=12, h=(260, 420), col=(0.10, 0.17, 0.14), seed=5, palms=True, edge=0.5):
    """faixa de floresta (silhuetas) com base em y"""
    rnd = random.Random(seed)
    for i in range(n):
        x = (i + rnd.uniform(-0.3, 0.3)) * w / (n - 1) + (W - w) / 2
        hh = rnd.uniform(*h)
        c.save(); c.translate(x, y + rnd.uniform(0, 30))
        if palms and rnd.random() < 0.28:
            palm(c, hh * 0.9, col, t + i)
        else:
            jungle_tree(c, hh, col, seed * 31 + i, edge)
        c.restore()


def river(c, t, y=820, h=120, col=(0.08, 0.14, 0.16)):
    """rio escuro horizontal com reflexos"""
    c.rectangle(0, y, W, h); rgb(c, col); c.fill()
    line(c, 0, y, W, y, 3, (0.30, 0.36, 0.34))
    for i in range(14):
        x = ((t * 30 + i * 170) % (W + 200)) - 100
        yy = y + 18 + (i % 4) * (h - 30) / 4
        line(c, x, yy, x + 60 + (i % 3) * 30, yy, 2, (0.40, 0.48, 0.50))


def tepui(c, w=900, h=360, col=(0.20, 0.22, 0.24), forest=(0.12, 0.20, 0.16)):
    """planalto de paredões verticais e topo achatado coberto de mata (base em 0,0)"""
    pts = [(-w / 2 - 60, 0), (-w / 2, -h * 0.25), (-w / 2 + 10, -h * 0.85), (-w / 2 + 60, -h), (w / 2 - 40, -h),
           (w / 2, -h * 0.9), (w / 2 + 10, -h * 0.3), (w / 2 + 80, 0)]
    poly(c, pts); fs(c, col, 6)
    for i in range(9):
        x = -w / 2 + 70 + i * (w - 120) / 8
        line(c, x, -h + 30, x + (i % 2) * 14 - 7, -h * 0.25, 2, (0.32, 0.33, 0.35))
    rnd = random.Random(3)
    for i in range(16):
        x = -w / 2 + 70 + i * (w - 110) / 15
        circle(c, x, -h - 8 - rnd.uniform(0, 14), rnd.uniform(26, 40), forest, 3)


def dinosaur(c, col=(0.16, 0.18, 0.20)):
    """saurópode em silhueta (pés em y=0, ~400 de largura)"""
    for x in (-110, -60, 30, 80):
        c.rectangle(x - 14, -80, 28, 80); fs(c, col, 5)
    c.move_to(-200, -70)
    c.curve_to(-150, -95, -90, -150, 0, -150)
    c.curve_to(70, -150, 100, -130, 120, -170)
    c.curve_to(140, -230, 150, -290, 175, -300)
    c.curve_to(200, -305, 210, -290, 196, -284)
    c.curve_to(178, -276, 168, -230, 158, -160)
    c.curve_to(150, -100, 120, -70, 80, -60)
    c.line_to(-120, -55); c.close_path()
    fs(c, col, 5)


def idol(c, glow_on=False, t=0):
    """ídolo de basalto negro com placa no peito (base em 0,0)"""
    if glow_on:
        glow(c, 0, -120, 220, AMBER, 0.22 + 0.06 * math.sin(t * 3))
    blk = (0.10, 0.10, 0.11)
    rrect(c, -48, -40, 96, 40, 8); fs(c, blk, 5)
    rrect(c, -40, -170, 80, 132, 18); fs(c, blk, 5)
    circle(c, 0, -205, 36, blk, 5)
    line(c, -14, -210, -4, -210, 3); line(c, 4, -210, 14, -210, 3)
    rrect(c, -24, -150, 48, 50, 4); fs(c, (0.16, 0.16, 0.17), 3)
    for i in range(3):
        y = -140 + i * 14
        line(c, -16, y, -6 + (i % 2) * 6, y, 2); line(c, 2, y, 14, y, 2)
    line(c, -40, -120, -62, -70, 6); line(c, 40, -120, 62, -70, 6)


def horse(c, col=(0.38, 0.28, 0.20)):
    """cavalo/mula em pé, perfil para a direita (cascos em y=0)"""
    rrect(c, -110, -190, 200, 80, 40); fs(c, col, 5)
    for x in (-90, -60, 50, 74):
        line(c, x, -120, x + (4 if x > 0 else -4), 0, 12, INK)
        line(c, x, -120, x + (4 if x > 0 else -4), -4, 7, col)
    poly(c, [(60, -185), (100, -240), (176, -214), (170, -190), (110, -200), (90, -160)]); fs(c, col, 5)
    poly(c, [(102, -240), (108, -268), (118, -236)]); fs(c, col, 4)
    c.move_to(-108, -170); c.curve_to(-140, -150, -150, -110, -138, -80)
    rgb(c, INK); c.set_line_width(8); c.stroke()
    circle(c, 128, -220, 4, INK, 0)


def wood_cross(c, h=160):
    """cruz de madeira de marcação (base em 0,0)"""
    c.rectangle(-9, -h, 18, h); fs(c, (0.40, 0.29, 0.18), 4)
    c.rectangle(-46, -h + 34, 92, 16); fs(c, (0.40, 0.29, 0.18), 4)
    ellipse(c, 0, 0, 60, 12); fs(c, (0.20, 0.16, 0.12), 3)


def signet_ring(c):
    """anel de sinete"""
    c.new_sub_path(); c.arc(0, 30, 56, 0, 2 * math.pi)
    rgb(c, INK); c.set_line_width(22); c.stroke_preserve()
    rgb(c, AMBER); c.set_line_width(14); c.stroke()
    rrect(c, -42, -60, 84, 64, 14); fs(c, AMBER, 6)
    rrect(c, -30, -50, 60, 44, 10); fs(c, (0.65, 0.46, 0.18), 3)
    text(c, "F", 0, -28, 32, SERIF, DARKTXT)


def theodolite(c):
    """teodolito (instrumento de medição) num tripé, base em 0,0"""
    for dx in (-90, 0, 90):
        line(c, 0, -170, dx, 0, 8, (0.45, 0.33, 0.20))
    rrect(c, -36, -200, 72, 34, 6); fs(c, (0.62, 0.54, 0.34), 5)
    rrect(c, -18, -250, 36, 50, 6); fs(c, (0.55, 0.47, 0.30), 5)
    rrect(c, -70, -270, 140, 30, 12); fs(c, (0.70, 0.62, 0.40), 5)
    circle(c, 70, -255, 14, (0.30, 0.40, 0.50), 4)


def smoke(c, t, x, y, h=420, a=0.22, seed=0):
    """coluna de fumaça subindo (base em x,y)"""
    for i in range(9):
        ph = (t * 0.25 + i / 9 + seed * 0.13) % 1
        xx = x + math.sin(t * 0.6 + i * 1.3 + seed) * (10 + ph * 40) + ph * 30
        yy = y - ph * h
        glow(c, xx, yy, 30 + ph * 70, (0.62, 0.62, 0.60), a * math.sin(math.pi * ph))


def letter(c, lines=7, w=360, h=470, sign=True, col=PARCH):
    """folha de carta manuscrita"""
    c.save(); c.rotate(-0.03)
    rrect(c, -w / 2, -h / 2, w, h, 6); fs(c, col, 5)
    for i in range(lines):
        y = -h / 2 + 70 + i * 46
        xs = -w / 2 + 34
        xe = w / 2 - 34 - (i * 37 % 60)
        c.move_to(xs, y)
        k = 0
        while xs + k * 18 < xe:
            c.line_to(xs + k * 18 + 9, y - 5 + (k % 3) * 3)
            k += 1
        rgb(c, (0.30, 0.22, 0.14)); c.set_line_width(3); c.stroke()
    if sign:
        c.move_to(w / 2 - 150, h / 2 - 50); c.curve_to(w / 2 - 120, h / 2 - 80, w / 2 - 90, h / 2 - 20, w / 2 - 50, h / 2 - 60)
        rgb(c, (0.30, 0.22, 0.14)); c.set_line_width(3); c.stroke()
    c.restore()


def oca(c, w=220, h=150, col=(0.46, 0.38, 0.22)):
    """casa indígena de palha (base em 0,0)"""
    c.move_to(-w / 2, 0); c.curve_to(-w / 2, -h * 1.1, w / 2, -h * 1.1, w / 2, 0); c.close_path()
    fs(c, col, 5)
    for i in range(1, 6):
        k = i / 6
        c.move_to(-w / 2 * (1 - k * 0.15), -h * k * 0.8); c.line_to(w / 2 * (1 - k * 0.15), -h * k * 0.8)
        rgb(c, (0.32, 0.26, 0.15)); c.set_line_width(2); c.stroke()
    rrect(c, -20, -50, 40, 50, 6); fs(c, (0.10, 0.09, 0.08), 3)


def pot(c, col=(0.62, 0.36, 0.22)):
    """vaso de cerâmica com desenho geométrico (base em 0,0)"""
    c.move_to(-40, -160); c.curve_to(-100, -120, -100, -10, -40, 0); c.line_to(40, 0)
    c.curve_to(100, -10, 100, -120, 40, -160); c.close_path(); fs(c, col, 5)
    rrect(c, -48, -178, 96, 22, 6); fs(c, col, 5)
    c.move_to(-76, -90)
    for k in range(8):
        c.line_to(-76 + (k + 0.5) * 19, -90 + (16 if k % 2 == 0 else 0))
    rgb(c, DARKTXT); c.set_line_width(4); c.stroke()
    line(c, -84, -60, 84, -60, 3, DARKTXT)


def denture(c, col=(0.92, 0.90, 0.84)):
    """arcada dentária (vista de cima)"""
    c.new_sub_path(); c.arc(0, 0, 80, math.pi * 1.05, math.pi * 1.95)
    rgb(c, (0.74, 0.40, 0.40)); c.set_line_width(26); c.stroke()
    for k in range(10):
        a = math.pi * (1.1 + k * 0.08)
        circle(c, math.cos(a) * 80, math.sin(a) * 80, 11, col, 3)


def bone(c, L=260, col=(0.86, 0.83, 0.74)):
    """osso longo (horizontal, centrado)"""
    c.rectangle(-L / 2, -12, L, 24); fs(c, col, 4)
    for sx in (-1, 1):
        circle(c, sx * L / 2, -14, 20, col, 4); circle(c, sx * L / 2, 14, 20, col, 4)
    c.rectangle(-L / 2 + 4, -10, L - 8, 20); rgb(c, col); c.fill()


def lectern(c):
    """púlpito de palestra (base em 0,0)"""
    poly(c, [(-70, 0), (-50, -200), (50, -200), (70, 0)]); fs(c, (0.36, 0.25, 0.16), 5)
    poly(c, [(-80, -200), (80, -200), (70, -240), (-70, -240)]); fs(c, (0.42, 0.30, 0.19), 5)


def canoe(c, col=(0.40, 0.28, 0.18)):
    """canoa vista de lado"""
    c.move_to(-220, -40); c.curve_to(-140, 40, 140, 40, 220, -40)
    c.curve_to(120, -20, -120, -20, -220, -40); c.close_path(); fs(c, col, 5)


def pyramid(c, w=380, h=240):
    """pirâmide (base em 0,0)"""
    poly(c, [(-w / 2, 0), (0, -h), (w / 2, 0)]); fs(c, (0.62, 0.54, 0.38), 6)
    for k in range(1, 6):
        y = -h * k / 6
        line(c, -w / 2 * (1 - k / 6), y, w / 2 * (1 - k / 6), y, 2, (0.45, 0.38, 0.26))


def volcano(c, t=0, w=360, h=220):
    poly(c, [(-w / 2, 0), (-50, -h), (50, -h), (w / 2, 0)]); fs(c, (0.25, 0.22, 0.22), 6)
    glow(c, 0, -h, 160, ORANGE, 0.35 + 0.1 * math.sin(t * 5))
    for k in range(3):
        c.move_to(-20 + k * 20, -h); c.line_to(-40 + k * 30 + math.sin(t * 2 + k) * 8, -h * 0.4)
        rgb(c, ORANGE); c.set_line_width(7); c.stroke()


def ruined_arch(c, w=220, h=260, col=(0.52, 0.50, 0.46)):
    """arco de pedra em ruína (base em 0,0)"""
    R, r = w / 2, w / 2 - 44
    c.new_sub_path(); c.arc(0, -h, R, math.pi, 1.82 * math.pi); c.arc_negative(0, -h, r, 1.82 * math.pi, math.pi); c.close_path()
    fs(c, col, 5)
    c.rectangle(-R, -h, 44, h); fs(c, col, 5)
    c.rectangle(R - 44, -h * 0.80, 44, h * 0.80); fs(c, col, 5)
    for k in range(4):
        line(c, -R + 6, -h + 40 + k * 50, -R + 38, -h + 40 + k * 50, 2, (0.38, 0.36, 0.33))


# ================================================================ 5 MISTÉRIOS (lista em contagem regressiva)
def rank_card(c, n, title_, sub="", glow_col=AMBER):
    """cartão de item de lista: número grande (contagem regressiva), título e local/ano"""
    glow(c, 0, -60, 420, glow_col, 0.16)
    text(c, "Nº", -150, -150, 64, SERIF, glow_col)
    text(c, str(n), 40, -90, 300, SERIF, INK)
    line(c, -420, 120, 420, 120, 3, glow_col)
    text(c, title_, 0, 190, 70, SERIF, INK)
    if sub:
        text(c, sub, 0, 270, 40, TYPE, glow_col)


def axe(c, col=(0.62, 0.64, 0.68), handle=(0.48, 0.33, 0.20)):
    """machado (cabo vertical, lâmina à direita, centro no meio do cabo)"""
    rrect(c, -11, -170, 22, 340, 10); fs(c, handle, 5)
    c.move_to(8, -160); c.line_to(80, -190); c.curve_to(110, -140, 110, -80, 80, -40); c.line_to(8, -80); c.close_path()
    fs(c, col, 6)
    line(c, 78, -182, 80, -48, 3, (0.85, 0.86, 0.90))


def chisel(c):
    rrect(c, -14, -90, 28, 90, 8); fs(c, (0.50, 0.34, 0.20), 5)
    poly(c, [(-9, 0), (9, 0), (7, 110), (0, 124), (-7, 110)]); fs(c, (0.66, 0.68, 0.72), 5)


def door(c, panel_out=False, w=220, h=400, col=(0.36, 0.25, 0.16)):
    """porta dos fundos de madeira (base em y=0); panel_out deixa o buraco do painel arrancado"""
    c.rectangle(-w / 2 - 18, -h - 18, w + 36, h + 18); fs(c, (0.24, 0.17, 0.11), 6)
    c.rectangle(-w / 2, -h, w, h); fs(c, col, 6)
    for (x, y, pw, ph) in ((-w / 2 + 24, -h + 28, w - 48, h * 0.38), (-w / 2 + 24, -h * 0.5, w - 48, h * 0.38)):
        c.rectangle(x, y, pw, ph); rgb(c, (0.20, 0.14, 0.09)); c.set_line_width(4); c.stroke()
    if panel_out:
        c.rectangle(-w / 2 + 24, -h * 0.5, w - 48, h * 0.38); fs(c, (0.02, 0.02, 0.03), 4)
        for k in range(5):
            x = -w / 2 + 30 + k * (w - 60) / 4
            line(c, x, -h * 0.5, x + 6, -h * 0.5 + 14, 3, (0.55, 0.42, 0.28))
    circle(c, w / 2 - 28, -h * 0.52, 9, AMBER, 3)


def trumpet(c, col=AMBER):
    """trompete (bocal à esquerda, campana à direita)"""
    rrect(c, -150, -10, 220, 20, 8); fs(c, col, 4)
    poly(c, [(60, -10), (150, -55), (150, 55), (60, 10)]); fs(c, col, 5)
    for k in range(3):
        rrect(c, -50 + k * 30, -42, 16, 34, 4); fs(c, col, 3)
    rrect(c, -110, 10, 140, 28, 12); rgb(c, col); c.set_line_width(5); c.stroke()
    circle(c, -160, 0, 10, col, 4)


def note_glyph(c, col=AMBER, s=1.0):
    c.save(); c.scale(s, s)
    ellipse(c, 0, 0, 18, 13); rgb(c, col); c.fill()
    line(c, 16, 0, 16, -70, 6, col); line(c, 16, -70, 42, -50, 6, col)
    c.restore()


def music_notes(c, t, x, y, n=5, col=AMBER, spread=160):
    """notas musicais subindo a partir de (x, y)"""
    for i in range(n):
        k = (t * 0.45 + i / n) % 1.0
        xx = x + math.sin(t * 1.5 + i * 2) * spread * 0.4 + (i - n / 2) * spread / n
        yy = y - k * 300
        a = math.sin(k * math.pi)
        c.save(); c.translate(xx, yy); c.rotate(math.sin(t + i) * 0.2)
        c.push_group(); note_glyph(c, col, 0.8); c.pop_group_to_source(); c.paint_with_alpha(a)
        c.restore()


def townhouse(c, w=230, h=300, col=(0.26, 0.24, 0.26), lit=0.0, seed=1, balcony=True):
    """sobrado estreito de Nova Orleans (base em y=0); lit = janelas acesas (0..1)"""
    rnd = random.Random(seed)
    c.rectangle(-w / 2, -h, w, h); fs(c, col, 5)
    poly(c, [(-w / 2 - 14, -h), (w / 2 + 14, -h), (w / 2, -h - 30), (-w / 2, -h - 30)]); fs(c, (0.18, 0.17, 0.19), 5)
    for row in range(2):
        for k in range(2):
            x = -w / 2 + 30 + k * (w - 90)
            y = -h + 40 + row * h * 0.48
            on = lit > 0 and rnd.random() < 0.35 + lit * 0.65
            if on:
                glow(c, x + 15, y + 40, 90, AMBER, 0.25 * lit)
            c.rectangle(x, y, 32, 80); fs(c, AMBER if on else (0.08, 0.08, 0.10), 4)
    if balcony:
        line(c, -w / 2 - 10, -h * 0.52, w / 2 + 10, -h * 0.52, 6)
        for k in range(9):
            x = -w / 2 - 6 + k * (w + 12) / 8
            line(c, x, -h * 0.52, x, -h * 0.52 + 34, 3)
        line(c, -w / 2 - 10, -h * 0.52 + 34, w / 2 + 10, -h * 0.52 + 34, 4)


def gas_lamp(c, t=0, h=260):
    line(c, 0, 0, 0, -h, 8, (0.30, 0.30, 0.32))
    poly(c, [(-22, -h), (22, -h), (14, -h - 50), (-14, -h - 50)]); fs(c, AMBER, 4)
    glow(c, 0, -h - 25, 160, AMBER, 0.25 + 0.05 * math.sin(t * 9))


def big_ear(c, w=1300):
    """radiotelescópio Big Ear (vista lateral): refletor plano inclinável, plano de terra e refletor parabólico fixo"""
    gp = (0.36, 0.38, 0.42)
    c.rectangle(-w / 2, -16, w, 16); fs(c, gp, 4)                                  # plano de terra (alumínio)
    for k in range(14):
        line(c, -w / 2 + k * w / 13, -16, -w / 2 + k * w / 13, 0, 2, (0.24, 0.25, 0.28))
    x0 = -w / 2 + 40                                                                 # refletor plano inclinado (esq.)
    poly(c, [(x0, -16), (x0 + 120, -16), (x0 + 210, -330), (x0 + 150, -340)]); fs(c, (0.44, 0.46, 0.50), 5)
    for k in range(6):
        y = -40 - k * 50
        line(c, x0 + 12 - y * 0.27, y, x0 + 110 - y * 0.29, y, 2, (0.30, 0.31, 0.35))
    for k in range(3):
        line(c, x0 + 160 + k * 25, -16, x0 + 180 - k * 10, -230 + k * 60, 4, (0.30, 0.31, 0.35))
    x1 = w / 2 - 40                                                                  # refletor parabólico (dir.)
    c.move_to(x1, -16); c.curve_to(x1 - 40, -120, x1 - 40, -260, x1 - 20, -380)
    c.line_to(x1 + 30, -380); c.line_to(x1 + 30, -16); c.close_path(); fs(c, (0.44, 0.46, 0.50), 5)
    for k in range(7):
        line(c, x1 - 30 + k * 2, -40 - k * 50, x1 + 30, -40 - k * 50, 2, (0.30, 0.31, 0.35))
    c.rectangle(-30, -70, 60, 54); fs(c, (0.30, 0.30, 0.34), 4)                      # casinha do receptor (foco)
    line(c, -30, -70, 30, -70, 4, AMBER)


PRINT_CHARS = "1  1 1   12 1  1    1 1  2   1 1    11  1 2 1   1  "


def printout(c, t=0, w=520, h=640, scroll=0.0, wow=None, cols=10, rows=18, size=26, highlight=False, seed=3):
    """papel contínuo de impressora com colunas de caracteres (intensidade do sinal).
    wow = coluna onde aparece 6EQUJ5 (lista de quantos caracteres já aparecem: int 0..6)"""
    c.save()
    c.rectangle(-w / 2, -h / 2, w, h); fs(c, (0.86, 0.85, 0.78), 5)
    for side in (-1, 1):
        x = side * (w / 2 - 20)
        line(c, x - side * 18, -h / 2, x - side * 18, h / 2, 2, (0.70, 0.68, 0.60))
        for k in range(14):
            y = -h / 2 + 24 + ((k * 48 + scroll) % (h - 30))
            circle(c, x, y, 8, (0.62, 0.60, 0.54), 0)
    c.rectangle(-w / 2 + 44, -h / 2 + 6, w - 88, h - 12); c.clip()
    rnd = random.Random(seed)
    dx = (w - 120) / cols
    seq = "6EQUJ5"
    for r in range(rows + 2):
        y = -h / 2 + 30 + r * (h - 40) / rows + (scroll % ((h - 40) / rows))
        for k in range(cols):
            x = -w / 2 + 70 + k * dx
            ch = rnd.choice(PRINT_CHARS)
            col = (0.30, 0.28, 0.25)
            if wow is not None and k == 2 and 6 <= r < 12:
                i = r - 6
                ch = seq[i] if i < wow else " "
                col = BLOOD if highlight else (0.12, 0.10, 0.08)
            if ch.strip():
                text(c, ch, x, y, size, TYPE, col)
    c.restore()


def signal_wave(c, t, w=900, amp=24, peak=0.0, px=0.5, pw=0.08, col=ICE, lw=4, seed=1, flat=False):
    """linha de ruído com um pico gaussiano (peak = altura do pico em px, px = posição 0..1)"""
    rnd = random.Random(seed + int(t * 12))
    n = 160
    for i in range(n + 1):
        u = i / n
        x = -w / 2 + u * w
        noise = 0 if flat else rnd.uniform(-1, 1) * amp
        y = noise - peak * math.exp(-((u - px) / pw) ** 2)
        (c.move_to if i == 0 else c.line_to)(x, y)
    rgb(c, col); c.set_line_width(lw); c.stroke()


def hydrogen(c, t=0, col=ICE):
    """átomo de hidrogênio: 1 próton + 1 elétron orbitando"""
    circle(c, 0, 0, 34, RED, 5); text(c, "+", 0, -2, 40, TYPE, INK)
    ellipse(c, 0, 0, 150, 60); rgb(c, col, 0.8); c.set_line_width(3); c.stroke()
    a = t * 2.2
    circle(c, 150 * math.cos(a), 60 * math.sin(a), 14, col, 4)


SAGITTARIUS = [(-160, 40), (-80, 70), (0, 30), (60, 90), (140, 40), (100, -40), (20, -60), (-60, -20), (-150, -40)]


def sagittarius(c, t=0, lines=True):
    """constelação de Sagitário (o 'bule')"""
    pts = SAGITTARIUS
    if lines:
        for (a, b) in ((0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 2), (6, 7), (7, 0), (7, 8), (8, 0)):
            line(c, *pts[a], *pts[b], 2, (0.55, 0.62, 0.75))
    for i, (x, y) in enumerate(pts):
        r = 6 + (i % 3)
        glow(c, x, y, 30, ICE, 0.35 + 0.15 * math.sin(t * 2 + i))
        circle(c, x, y, r, (0.92, 0.94, 1.0), 0)


def magnetar(c, t=0, flare=0.0):
    """estrela de nêutrons magnética com linhas de campo; flare 0..1 = clarão"""
    if flare > 0:
        glow(c, 0, 0, 260 + flare * 300, (0.70, 0.60, 1.0), 0.45 * flare)
    for k in range(4):
        r = 70 + k * 45
        for s in (-1, 1):
            c.save(); c.scale(s, 1)
            c.move_to(0, -18); c.curve_to(r, -r * 1.1, r, r * 1.1, 0, 18)
            rgb(c, (0.60, 0.55, 0.95), 0.6 - k * 0.1); c.set_line_width(3); c.stroke()
            c.restore()
    glow(c, 0, 0, 80, (0.85, 0.85, 1.0), 0.6)
    circle(c, 0, 0, 22, (0.95, 0.95, 1.0), 4)


def h_cloud(c, t=0, bright=0.0, w=360, h=180):
    """nuvem fria de hidrogênio; bright 0..1 faz ela brilhar"""
    rnd = random.Random(9)
    for i in range(16):
        x, y = rnd.uniform(-w / 2, w / 2), rnd.uniform(-h / 2, h / 2)
        r = rnd.uniform(60, 120)
        glow(c, x + math.sin(t * 0.3 + i) * 8, y, r, ICE if bright < 0.5 else (0.75, 0.90, 1.0), 0.10 + 0.25 * bright)


def b727(c, t=0, stair=0.0, col=(0.80, 0.81, 0.84), stripe=RED, windows=True):
    """Boeing 727 (vista lateral, nariz à direita); stair 0..1 baixa a escada traseira sob a cauda"""
    if stair > 0:                                                      # escada traseira (airstair)
        a = stair * 0.95
        c.save(); c.translate(-250, 26); c.rotate(a)
        c.rectangle(-150, -10, 150, 20); fs(c, (0.55, 0.56, 0.60), 4)
        for k in range(6):
            line(c, -140 + k * 25, -10, -140 + k * 25, 10, 2, (0.35, 0.36, 0.40))
        c.restore()
        glow(c, -255, 30, 90, AMBER, 0.25 * stair)
    c.move_to(330, 0); c.curve_to(330, -30, 300, -40, 260, -40)        # fuselagem
    c.line_to(-260, -40); c.line_to(-330, -20); c.line_to(-330, 10); c.line_to(-250, 40)
    c.line_to(260, 40); c.curve_to(300, 40, 330, 30, 330, 0); c.close_path(); fs(c, col, 6)
    poly(c, [(-200, -40), (-300, -190), (-250, -190), (-130, -40)]); fs(c, col, 6)   # deriva em T
    poly(c, [(-330, -190), (-210, -190), (-200, -176), (-330, -176)]); fs(c, col, 5)
    rrect(c, -250, -78, 110, 30, 12); fs(c, (0.62, 0.63, 0.67), 5)                     # motores traseiros
    rrect(c, -250, -30, 100, 28, 12); fs(c, (0.62, 0.63, 0.67), 5)
    poly(c, [(20, 18), (120, 18), (-20, 90), (-70, 90)]); fs(c, (0.70, 0.71, 0.74), 5)  # asa
    line(c, -240, 4, 300, 4, 6, stripe)
    if windows:
        for x in range(-180, 240, 26):
            circle(c, x, -16, 5, (0.25, 0.32, 0.42), 0)
    poly(c, [(280, -30), (312, -26), (318, -12), (284, -12)]); fs(c, (0.25, 0.32, 0.42), 3)


def parachute(c, t=0, col=(0.82, 0.80, 0.74), open_=1.0):
    """paraquedas com cordas até a origem (onde fica a pessoa)"""
    w = 60 + 150 * open_
    top = -260
    sway = math.sin(t * 1.4) * 6
    c.move_to(-w, top + 40)
    c.curve_to(-w, top - 90 * open_, w, top - 90 * open_, w, top + 40)
    for k in range(4):
        x0 = w - k * w / 2
        c.curve_to(x0 - w / 8, top + 18, x0 - 3 * w / 8, top + 18, x0 - w / 2, top + 40)
    c.close_path(); fs(c, col, 5)
    for k in range(5):
        x = -w + k * w / 2
        line(c, x, top + 40, sway, -10, 2, (0.70, 0.68, 0.62))


def briefcase(c, open_=False, bomb=False):
    """maleta; aberta mostra cilindros vermelhos e fios (estilizado)"""
    if open_:
        poly(c, [(-170, -10), (170, -10), (150, -150), (-150, -150)]); fs(c, (0.28, 0.20, 0.14), 6)
    rrect(c, -170, -10, 340, 170, 12); fs(c, (0.34, 0.24, 0.16), 6)
    rrect(c, -40, -36, 80, 30, 10); rgb(c, INK); c.set_line_width(6); c.stroke()
    if open_ and bomb:
        for k in range(4):
            rrect(c, -130 + k * 52, 20, 40, 110, 8); fs(c, RED, 4)
        rrect(c, 80, 40, 60, 80, 6); fs(c, (0.30, 0.30, 0.34), 4)
        for k, col in enumerate((RED, YELLOW, BLUE)):
            c.move_to(-110 + k * 52, 20); c.curve_to(-60, -30, 60, -20, 100 + k * 8, 40)
            rgb(c, col); c.set_line_width(4); c.stroke()


def clip_tie(c, col=(0.10, 0.10, 0.12)):
    """gravata preta de prender com prendedor"""
    poly(c, [(-24, -150), (24, -150), (16, -110), (-16, -110)]); fs(c, col, 5)
    poly(c, [(-16, -110), (16, -110), (40, 120), (0, 160), (-40, 120)]); fs(c, col, 5)
    rrect(c, -50, -20, 100, 14, 6); fs(c, (0.78, 0.74, 0.60), 3)


def money_bag(c, label="$"):
    c.move_to(-30, -120); c.curve_to(-140, -60, -150, 120, 0, 120); c.curve_to(150, 120, 140, -60, 30, -120); c.close_path()
    fs(c, (0.62, 0.52, 0.34), 6)
    line(c, -36, -112, 36, -112, 8, (0.40, 0.30, 0.20))
    text(c, label, 0, 20, 70, SERIF, (0.25, 0.30, 0.18))


def bill_stack(c, rotten=0.0, label="20"):
    """maço de notas de dólar (rotten 0..1 = apodrecido)"""
    col = (0.50 - 0.18 * rotten, 0.62 - 0.25 * rotten, 0.46 - 0.18 * rotten)
    for k in range(4):
        rrect(c, -110 + k * 3, -50 - k * 8, 220, 100, 6); fs(c, col, 4)
    circle(c, 9, -24, 26, None, 3, (0.30, 0.38, 0.28))
    text(c, label, -70, -64, 26, TYPE, (0.20, 0.26, 0.18))
    if rotten > 0:
        rnd = random.Random(4)
        for _ in range(int(14 * rotten)):
            x, y = rnd.uniform(-100, 110), rnd.uniform(-70, 40)
            circle(c, x, y, rnd.uniform(5, 14), (0.22, 0.20, 0.14), 0)
    rrect(c, -14, -84, 28, 112, 4); fs(c, (0.62, 0.30, 0.22), 3)


def farmhouse(c, t=0, attic=0.0, snow_roof=True, w=760, smoke_on=False):
    """fazenda bávara (casa + celeiro sob o mesmo telhado; base em y=0); attic 0..1 = luz no sótão"""
    house_w = w * 0.42
    c.rectangle(-w / 2, -220, w, 220); fs(c, (0.30, 0.27, 0.24), 6)                       # paredes
    poly(c, [(-w / 2 - 30, -220), (-w / 2 + house_w / 2, -400), (-w / 2 + house_w + 30, -220)]); fs(c, (0.22, 0.17, 0.14), 6)
    poly(c, [(-w / 2 + house_w - 30, -220), (-w / 2 + house_w + 60, -330), (w / 2 + 30, -330), (w / 2 + 40, -220)]); fs(c, (0.22, 0.17, 0.14), 6)
    if snow_roof:
        poly(c, [(-w / 2 - 30, -220), (-w / 2 + house_w / 2, -400), (-w / 2 + house_w / 2 + 14, -392), (-w / 2 - 6, -222)])
        rgb(c, (0.88, 0.90, 0.94), 0.8); c.fill()
        c.rectangle(-w / 2 + house_w + 60, -336, w / 2 - house_w - 20, 10); rgb(c, (0.88, 0.90, 0.94), 0.8); c.fill()
    ax = -w / 2 + house_w / 2                                                                   # janela do sótão
    c.rectangle(ax - 22, -330, 44, 50)
    fs(c, AMBER if attic > 0.05 else (0.06, 0.06, 0.08), 4)
    if attic > 0.05:
        glow(c, ax, -305, 150, AMBER, 0.30 * attic)
    for k in range(2):                                                                          # janelas da casa
        c.rectangle(-w / 2 + 40 + k * (house_w - 130), -170, 50, 60); fs(c, (0.06, 0.06, 0.08), 4)
    c.rectangle(-w / 2 + house_w * 0.42, -110, 60, 110); fs(c, (0.20, 0.14, 0.10), 4)             # porta
    bx = -w / 2 + house_w + 60                                                                  # portão do celeiro
    c.rectangle(bx + 60, -170, 200, 170); fs(c, (0.26, 0.19, 0.13), 5)
    line(c, bx + 60, -170, bx + 260, 0, 4, (0.36, 0.27, 0.18)); line(c, bx + 260, -170, bx + 60, 0, 4, (0.36, 0.27, 0.18))
    c.rectangle(-w / 2 + 70, -400, 30, 80); fs(c, (0.26, 0.22, 0.20), 4)                         # chaminé
    if smoke_on:
        smoke(c, t, -w / 2 + 85, -400, 260, 0.25)


def morro(c, w=1600, h=420, col=(0.10, 0.15, 0.12), grass=True, seed=2):
    """morro (base em y=0, topo em y=-h) com capim"""
    c.move_to(-w / 2, 0)
    c.curve_to(-w * 0.30, -h * 0.35, -w * 0.18, -h, 0, -h)
    c.curve_to(w * 0.20, -h, w * 0.30, -h * 0.45, w / 2, 0); c.close_path()
    fs(c, col, 5)
    if grass:
        rnd = random.Random(seed)
        for _ in range(70):
            u = rnd.uniform(-0.42, 0.42)
            x = u * w
            yt = -h * (1 - (abs(u) / 0.5) ** 2) + rnd.uniform(0, 18)
            line(c, x, yt, x + rnd.uniform(-8, 8), yt - rnd.uniform(14, 30), 3, (0.30, 0.42, 0.28))


def lead_mask(c, col=(0.52, 0.54, 0.56)):
    """máscara de chumbo feita à mão (cobre os olhos), com cordão"""
    c.move_to(-150, -10); c.curve_to(-150, -60, -40, -60, 0, -40); c.curve_to(40, -60, 150, -60, 150, -10)
    c.curve_to(150, 40, 60, 50, 0, 30); c.curve_to(-60, 50, -150, 40, -150, -10); c.close_path()
    fs(c, col, 6)
    for x in (-75, 75):
        ellipse(c, x, -6, 42, 24); rgb(c, (0.40, 0.42, 0.44)); c.set_line_width(3); c.stroke()
    rnd = random.Random(2)
    for _ in range(18):
        circle(c, rnd.uniform(-130, 130), rnd.uniform(-35, 25), rnd.uniform(2, 5), (0.44, 0.46, 0.48), 0)
    c.move_to(-150, -10); c.curve_to(-200, 0, -210, 60, -190, 90); rgb(c, (0.60, 0.50, 0.36)); c.set_line_width(4); c.stroke()
    c.move_to(150, -10); c.curve_to(200, 0, 210, 60, 190, 90); c.stroke()


def kite(c, t=0, col=RED):
    c.save(); c.rotate(math.sin(t * 1.3) * 0.12)
    poly(c, [(0, -70), (50, 0), (0, 90), (-50, 0)]); fs(c, col, 5)
    line(c, 0, -70, 0, 90, 3); line(c, -50, 0, 50, 0, 3)
    for k in range(4):
        y = 90 + k * 40
        line(c, math.sin(t * 3 + k) * 14, y, math.sin(t * 3 + k + 1) * 14, y + 40, 3)
    c.restore()


def raincoat(c, col=(0.70, 0.62, 0.36)):
    poly(c, [(-40, -150), (40, -150), (90, -120), (120, 140), (-120, 140), (-90, -120)]); fs(c, col, 6)
    line(c, 0, -150, 0, 140, 3, (0.45, 0.40, 0.24))
    poly(c, [(-90, -120), (-150, 60), (-120, 70), (-70, -60)]); fs(c, col, 5)
    poly(c, [(90, -120), (150, 60), (120, 70), (70, -60)]); fs(c, col, 5)
    for y in (-90, -30, 30, 90):
        circle(c, 12, y, 6, (0.30, 0.26, 0.16), 0)


def water_bottle(c, empty=False):
    rrect(c, -40, -110, 80, 220, 18); fs(c, (0.55, 0.70, 0.72), 5)
    if not empty:
        c.rectangle(-36, -40, 72, 146); rgb(c, (0.35, 0.55, 0.70), 0.7); c.fill()
    rrect(c, -18, -150, 36, 44, 6); fs(c, (0.40, 0.40, 0.44), 4)
    c.rectangle(-40, -20, 80, 50); fs(c, PARCH, 3)


def notebook(c, w=300, h=380):
    rrect(c, -w / 2, -h / 2, w, h, 8); fs(c, (0.84, 0.82, 0.74), 5)
    for k in range(9):
        circle(c, -w / 2 + 2, -h / 2 + 30 + k * 40, 9, None, 3)
    for k in range(9):
        line(c, -w / 2 + 30, -h / 2 + 50 + k * 38, w / 2 - 20, -h / 2 + 50 + k * 38, 2, (0.55, 0.65, 0.80))


def lit_window_lights(c, t, x, y, n=3):
    """luzes vermelhas e alaranjadas pairando no céu"""
    for i in range(n):
        xx = x + i * 90 + math.sin(t * 0.7 + i) * 20
        yy = y + math.cos(t * 0.5 + i * 2) * 15
        col = RED if i % 2 else ORANGE
        glow(c, xx, yy, 120, col, 0.35 + 0.15 * math.sin(t * 3 + i))
        circle(c, xx, yy, 10, col, 0)


def old_key(c, col=AMBER):
    """chave antiga de ferro"""
    c.new_sub_path(); c.arc(-90, 0, 40, 0, 2 * math.pi); rgb(c, col); c.set_line_width(12); c.stroke()
    line(c, -50, 0, 110, 0, 14, col)
    line(c, 80, 0, 80, 34, 12, col); line(c, 104, 0, 104, 26, 12, col)


def mattock(c, handle=(0.48, 0.33, 0.20), col=(0.55, 0.57, 0.60)):
    """enxadão (cabo vertical, lâmina larga na ponta de cima)"""
    rrect(c, -10, -150, 20, 320, 9); fs(c, handle, 5)
    poly(c, [(-20, -175), (20, -175), (24, -145), (-24, -145)]); fs(c, col, 5)
    poly(c, [(20, -170), (130, -150), (130, -120), (20, -150)]); fs(c, col, 5)
    poly(c, [(-20, -170), (-90, -190), (-95, -170), (-20, -150)]); fs(c, col, 5)


def bread(c, col=(0.72, 0.52, 0.30)):
    c.move_to(-110, 30); c.curve_to(-120, -60, 120, -60, 110, 30); c.close_path(); fs(c, col, 5)
    for x in (-50, 0, 50):
        line(c, x - 15, -10, x + 15, -30, 4, (0.50, 0.34, 0.18))


# ================================================================ Ártico (A Expedição Franklin)
# Mapas do Ártico canadense (contornos estilizados, aprox. lon/lat). Use make_proj(..., coslat=True).
LAND.update({
    "canada_n": [(-135, 69.0), (-130, 69.8), (-125, 69.6), (-120, 69.0), (-115, 68.0), (-110, 68.0), (-106, 68.4),
                 (-102, 68.0), (-100.5, 67.8), (-99.2, 67.7), (-98.7, 68.0), (-98.6, 68.45), (-97.5, 68.5), (-96.9, 68.3),
                 (-96.6, 67.9), (-96.0, 67.3), (-95.2, 67.6), (-94.6, 68.4), (-95.0, 69.3), (-95.2, 70.5), (-95.8, 71.4),
                 (-95.4, 72.0), (-94.0, 71.6), (-92.2, 70.6), (-91.6, 69.6), (-90.6, 68.8), (-89.0, 68.2), (-87.0, 67.6),
                 (-85.5, 68.6), (-84.0, 69.6), (-82.0, 69.6), (-81.5, 68.5), (-83.0, 66.5), (-86.0, 66.2), (-88.0, 64.0),
                 (-94.0, 61.0), (-94.0, 58.0), (-90.0, 57.0), (-82.0, 55.0), (-78.0, 58.0), (-78.0, 62.0), (-72.0, 62.0),
                 (-64.0, 60.0), (-61.0, 56.0), (-56.0, 52.0), (-60.0, 45.0), (-60.0, 35.0), (-140.0, 35.0)],
    "king_william": [(-97.8, 69.95), (-98.4, 69.75), (-98.75, 69.6), (-99.2, 69.3), (-99.5, 69.05), (-99.1, 68.85),
                     (-98.6, 68.7), (-97.8, 68.62), (-97.0, 68.6), (-96.2, 68.6), (-95.7, 68.8), (-95.6, 69.2),
                     (-96.1, 69.55), (-97.0, 69.85)],
    "victoria_is": [(-119, 71.5), (-117, 73.0), (-112, 73.2), (-106, 73.3), (-104.5, 72.0), (-102, 70.5), (-100.8, 69.5),
                    (-101.5, 68.9), (-104, 68.8), (-108, 68.7), (-113, 68.4), (-117, 69.0), (-118.5, 70.3)],
    "prince_wales": [(-101.5, 71.7), (-98.5, 71.6), (-97.2, 72.3), (-96.8, 73.2), (-97.5, 74.0), (-99.5, 74.0),
                     (-101.2, 73.4), (-102.5, 72.5)],
    "somerset": [(-95.0, 72.2), (-93.0, 72.0), (-91.0, 72.5), (-90.5, 73.5), (-91.5, 74.1), (-94.0, 74.1), (-95.3, 73.7),
                 (-95.4, 72.8)],
    "devon": [(-91.9, 74.65), (-88, 74.45), (-84, 74.45), (-80.2, 74.9), (-79.8, 75.8), (-83, 76.4), (-89, 76.4),
              (-93, 76.0), (-95.5, 75.5), (-93.5, 75.0)],
    "cornwallis": [(-96.5, 74.9), (-93.8, 74.75), (-93.4, 75.5), (-95.0, 75.9), (-96.5, 75.5)],
    "bathurst": [(-101, 75.4), (-97.5, 75.2), (-97, 76.3), (-99.5, 76.6), (-101.5, 76.0)],
    "baffin": [(-89.5, 73.3), (-85, 73.7), (-80, 73.6), (-77, 72.5), (-72, 71.2), (-68.5, 70.2), (-67, 69), (-64, 67.2),
               (-62, 66.6), (-64.5, 65), (-65, 63), (-66, 61.9), (-70, 62.6), (-72, 63.8), (-75, 64.5), (-78, 64.4),
               (-74.5, 66), (-73, 67.2), (-75, 68.4), (-78.5, 69.8), (-82, 69.8), (-85, 69.9), (-88.5, 70.5), (-89.8, 71.6)],
    "ellesmere": [(-90, 76.8), (-80, 76.3), (-76, 77.5), (-74, 79), (-70, 81), (-62, 82.5), (-90, 82.5)],
    "greenland": [(-73, 78.0), (-68, 76.2), (-60, 75.8), (-57, 74.5), (-55.5, 72.5), (-54, 70.5), (-52.5, 69), (-53.5, 67),
                  (-52, 65), (-50.5, 63), (-48.5, 61.5), (-44.5, 60), (-43, 60.2), (-41, 62.5), (-39.8, 65.3), (-35, 66.5),
                  (-30, 68.3), (-24, 70.2), (-22, 72), (-20, 75), (-18.5, 77.5), (-20, 80), (-40, 83), (-62, 83), (-70, 80)],
    "iceland": [(-24, 65.5), (-22.5, 66.4), (-18, 66.2), (-14.5, 65.5), (-13.5, 64.8), (-17.5, 63.6), (-21, 63.8), (-22.8, 64.1)],
    "scandinavia": [(5, 58), (5.5, 60), (5, 62), (8, 63.5), (12, 66), (15, 68.5), (20, 70), (28, 71), (40, 70), (40, 50), (10, 50),
                    (8, 54), (8.5, 57), (10.5, 57.7), (12, 56), (11, 59)],
})
ARCTIC = ["canada_n", "king_william", "victoria_is", "prince_wales", "somerset", "devon", "cornwallis", "bathurst",
          "baffin", "ellesmere", "greenland"]
NORTH_ATLANTIC = ARCTIC + ["iceland", "britain", "ireland", "scandinavia"]
ICE_LAND = (0.30, 0.34, 0.40)      # terra coberta de neve (mapas do Ártico)
ICE_SEA = (0.05, 0.08, 0.13)


def bomb_ship(c, t=0, name=None, sails=True, furled=False, funnel=True, frost=0.0, hull=(0.11, 0.11, 0.13),
              band=(0.78, 0.66, 0.40), sail=(0.80, 0.77, 0.70)):
    """navio-bombarda de três mastros (Erebus/Terror) visto de lado, proa à direita; origem = linha d'água.
    furled=True recolhe as velas (navio parado no gelo); frost 0..1 cobre o navio de gelo e neve."""
    # gurupés e mastros
    line(c, 210, -60, 380, -120, 7)
    masts = [(150, -380), (10, -440), (-150, -360)]
    for x, h in masts:
        line(c, x, -55, x, h, 8)
    rig = (0.58, 0.56, 0.52)
    for (x, h) in masts:
        line(c, x, h, x - 95, -60, 2, rig); line(c, x, h, x + 95, -60, 2, rig)
    line(c, 150, -380, 380, -120, 2, rig); line(c, 10, -440, 150, -380, 2, rig); line(c, -150, -360, 10, -440, 2, rig)
    for x, h in masts:
        rows = [(h + 20, h + 95, 46, 58), (h + 102, h + 190, 62, 78), (h + 197, -110, 80, 96)] if h < -400 else \
               [(h + 20, h + 90, 42, 52), (h + 96, h + 175, 56, 70), (h + 182, -110, 70, 86)]
        for i, (y0, y1, w0, w1) in enumerate(rows):
            line(c, x - w0 - 10, y0, x + w0 + 10, y0, 6)
            if not sails:
                continue
            if furled:
                rrect(c, x - w0 - 4, y0 - 4, 2 * w0 + 8, 16, 8); fs(c, sail, 3)
                continue
            c.move_to(x - w0, y0); c.line_to(x + w0, y0); c.line_to(x + w1, y1)
            c.curve_to(x + w1 * 0.4, y1 - 12, x - w1 * 0.4, y1 - 12, x - w1, y1); c.close_path()
            fs(c, sail, 4)
    if sails and not furled:
        poly(c, [(156, -360), (372, -126), (230, -70)]); fs(c, sail, 4)
    if funnel:
        rrect(c, 52, -150, 34, 100, 4); fs(c, (0.20, 0.19, 0.20), 5)
        line(c, 48, -150, 90, -150, 6)
    # casco (proa reforçada)
    c.move_to(-262, -60); c.line_to(232, -60)
    c.curve_to(226, -10, 196, 30, 140, 46); c.line_to(-210, 46)
    c.curve_to(-240, 30, -256, 0, -262, -60); c.close_path()
    fs(c, hull, 6)
    c.rectangle(-256, -40, 478, 16); rgb(c, band); c.fill()
    for x in range(-220, 200, 46):
        c.rectangle(x, -38, 18, 12); rgb(c, hull); c.fill()
    line(c, -268, -70, 238, -70, 5)
    if frost > 0:
        a = clamp01(frost)
        for x, h in masts:
            line(c, x - 3, -60, x - 3, h, 4, (0.92, 0.95, 1.0))
        c.move_to(-262, -66); c.line_to(232, -66)
        _jag(c, -262, 232, -82, 14, 9, 14)
        c.close_path(); rgb(c, (0.92, 0.95, 1.0), 0.85 * a); c.fill()
        rnd = random.Random(4)
        for _ in range(int(18 * a)):
            x = rnd.uniform(-240, 200)
            poly(c, [(x, -60), (x + 5, -60), (x + 2, -60 + rnd.uniform(12, 34))]); rgb(c, (0.85, 0.92, 1.0), 0.9); c.fill()
    if name:
        text(c, name, -60, 12, 26, TYPE, band)


def ice_field(c, t, y=760, w=None, seed=2, col=(0.80, 0.85, 0.92), crack=(0.48, 0.56, 0.66), ridges=True):
    """campo de gelo marinho de y até o fim da tela, com placas, rachaduras e cristas de pressão"""
    w = w or W
    g = cairo.LinearGradient(0, y, 0, H)
    g.add_color_stop_rgb(0, *col)
    g.add_color_stop_rgb(1, col[0] * 0.72, col[1] * 0.74, col[2] * 0.80)
    c.rectangle(0, y, w, H - y); c.set_source(g); c.fill()
    rnd = random.Random(seed)
    for _ in range(14):
        x0 = rnd.uniform(-100, w)
        yy = y + rnd.uniform(20, H - y)
        c.move_to(x0, yy)
        for k in range(5):
            x0 += rnd.uniform(60, 160); yy += rnd.uniform(-25, 25)
            c.line_to(x0, yy)
        rgb(c, crack, 0.8); c.set_line_width(2.5); c.stroke()
    if ridges:
        for i in range(7):
            x = rnd.uniform(0, w); sz = rnd.uniform(30, 70)
            poly(c, [(x - sz, y + 6), (x - sz * 0.3, y - sz * 0.7), (x, y - sz * 0.35), (x + sz * 0.45, y - sz * 0.9), (x + sz, y + 6)])
            fs(c, (0.86, 0.90, 0.96), 3, crack)
    line(c, 0, y, w, y, 4, (0.92, 0.95, 1.0))


def ice_ridge(c, w=300, h=90, seed=1, col=(0.86, 0.90, 0.96)):
    """bloco/crista de gelo de pressão (origem = base central)"""
    rnd = random.Random(seed)
    pts = [(-w / 2, 0)]
    n = 6
    for k in range(1, n):
        pts.append((-w / 2 + w * k / n, -h * rnd.uniform(0.4, 1.0)))
    pts.append((w / 2, 0))
    poly(c, pts); fs(c, col, 4, (0.48, 0.56, 0.66))


def coffin(c, open_=0.0, cloth=(0.17, 0.22, 0.40), w=150, h=420):
    """caixão visto de cima, coberto de pano azul; open_ 0..1 desliza a tampa revelando gelo azulado"""
    shape = [(-w * 0.32, -h / 2), (w * 0.32, -h / 2), (w / 2, -h * 0.22), (w * 0.36, h / 2), (-w * 0.36, h / 2), (-w / 2, -h * 0.22)]
    poly(c, shape); fs(c, (0.10, 0.10, 0.12), 6)
    if open_ > 0:
        c.save(); poly(c, shape); c.clip()
        g = cairo.RadialGradient(0, -h * 0.1, 10, 0, -h * 0.1, h * 0.6)
        g.add_color_stop_rgba(0, 0.70, 0.85, 1.0, 0.55 * open_)
        g.add_color_stop_rgba(1, 0.20, 0.30, 0.45, 0.15)
        c.set_source(g); c.paint()
        # silhueta discreta sob o gelo (sem detalhes)
        ellipse(c, 0, -h * 0.30, 30, 38); rgb(c, (0.55, 0.62, 0.70), 0.35 * open_); c.fill()
        c.restore()
    dy = -open_ * h * 0.75
    c.save(); c.translate(open_ * w * 0.55, dy)
    poly(c, shape); fs(c, cloth, 6)
    for k in range(1, 4):
        line(c, -w * 0.3, -h / 2 + k * h / 4, w * 0.3, -h / 2 + k * h / 4, 2, (0.28, 0.34, 0.55))
    c.restore()


def grave_board(c, label="", h=220, col=(0.40, 0.32, 0.22)):
    """lápide de madeira (tábua) cravada no chão; origem = base"""
    c.move_to(-55, 0); c.line_to(-55, -h + 40); c.curve_to(-55, -h - 6, 55, -h - 6, 55, -h + 40); c.line_to(55, 0); c.close_path()
    fs(c, col, 5)
    for k in range(3):
        line(c, -38, -h + 70 + k * 30, 38, -h + 70 + k * 30, 2, (0.25, 0.20, 0.14))
    if label:
        text(c, label, 0, -h + 40, 22, TYPE, DARKTXT)


def cairn(c, w=240, h=200, col=(0.36, 0.36, 0.38)):
    """monte de pedras (marco); origem = base"""
    rnd = random.Random(8)
    rows = 5
    for r in range(rows):
        n = rows - r + 1
        ww = w * (1 - r / (rows + 1))
        for k in range(n):
            x = -ww / 2 + ww * (k + 0.5) / n + rnd.uniform(-6, 6)
            y = -h * (r + 0.5) / rows
            rx, ry = ww / n / 2 + 4, h / rows / 2 + 4
            c.save(); c.translate(x, y); c.scale(1, ry / rx); c.new_sub_path(); c.arc(0, 0, rx, 0, 6.283); c.restore()
            fs(c, tuple(v + rnd.uniform(-0.04, 0.04) for v in col), 4)


def tin_can(c, label="", seam=True, open_=False, col=(0.62, 0.64, 0.66)):
    """lata de conserva do séc. XIX (cilindro); seam mostra a solda de chumbo"""
    c.rectangle(-60, -75, 120, 150); fs(c, col, 5)
    ellipse(c, 0, 75, 60, 14); fs(c, col, 5)
    c.rectangle(-58, -70, 116, 140); rgb(c, col); c.fill()
    ellipse(c, 0, -75, 60, 14); fs(c, (0.20, 0.20, 0.22) if open_ else (0.70, 0.72, 0.74), 5)
    for y in (-40, 40):
        line(c, -60, y, 60, y, 2, (0.48, 0.50, 0.52))
    if seam:
        line(c, 22, -72, 22, 72, 6, (0.36, 0.38, 0.42))
        rnd = random.Random(2)
        for k in range(7):
            circle(c, 22 + rnd.uniform(-4, 4), -60 + k * 20, 5, (0.38, 0.40, 0.44), 0)
    if label:
        c.rectangle(-60, -28, 120, 56); rgb(c, PARCH); c.fill()
        text(c, label, -10, 0, 24, TYPE, DARKTXT)


def navy_form(c, t=0, margin=0.0, w=520, h=680, col=(0.86, 0.82, 0.70)):
    """formulário da Marinha (bilhete de Victory Point): texto impresso e, com margin 0..1,
    a segunda mensagem rabiscada em volta da margem"""
    rrect(c, -w / 2, -h / 2, w, h, 6); fs(c, col, 5)
    rnd = random.Random(6)
    line(c, -w / 2 + 50, -h / 2 + 70, w / 2 - 50, -h / 2 + 70, 5, DARKTXT)
    for k in range(9):
        y = -h / 2 + 120 + k * 34
        line(c, -w / 2 + 70, y, -w / 2 + 70 + rnd.uniform(0.5, 1.0) * (w - 140), y, 3, (0.45, 0.40, 0.32))
    # mensagem de 1847 (manuscrita, curta) no centro
    for k in range(4):
        y = 70 + k * 30
        c.move_to(-w / 2 + 80, y)
        for x in range(int(-w / 2 + 80), int(w / 2 - 120), 18):
            c.line_to(x, y + rnd.uniform(-5, 5))
        rgb(c, (0.20, 0.22, 0.40)); c.set_line_width(2.5); c.stroke()
    if margin > 0:
        # rabiscos ao redor das bordas (percorre o contorno até a fração margin)
        path = [(-w / 2 + 18, h / 2 - 20), (-w / 2 + 18, -h / 2 + 20), (w / 2 - 18, -h / 2 + 20), (w / 2 - 18, h / 2 - 20),
                (-w / 2 + 40, h / 2 - 20)]
        segs = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        tot = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs) * clamp01(margin)
        c.move_to(*path[0])
        for (a, b) in segs:
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            if tot <= 0:
                break
            k = min(1, tot / L)
            n = max(2, int(L * k / 9))
            for j in range(1, n + 1):
                f = j / n * k
                x = a[0] + (b[0] - a[0]) * f; y = a[1] + (b[1] - a[1]) * f
                ox = rnd.uniform(-6, 6)
                c.line_to(x + (ox if a[0] == b[0] else 0), y + (ox if a[1] == b[1] else 0))
            tot -= L
        rgb(c, (0.30, 0.18, 0.12)); c.set_line_width(3); c.stroke()


def sledge_boat(c, people=0, cargo=True, col=(0.50, 0.38, 0.26)):
    """barco montado sobre um trenó pesado (madeira e ferro); origem = chão"""
    line(c, -230, 0, 210, 0, 9, (0.40, 0.40, 0.44))
    c.move_to(210, 0); c.curve_to(250, 0, 260, -30, 240, -46); rgb(c, (0.40, 0.40, 0.44)); c.set_line_width(9); c.stroke()
    for x in (-180, -60, 60, 170):
        line(c, x, 0, x, -40, 7, (0.36, 0.28, 0.20))
    line(c, -220, -40, 220, -40, 8, (0.36, 0.28, 0.20))
    c.save(); c.translate(0, -76); lifeboat(c, people, False, col); c.restore()
    if cargo:
        for x, h, cc in ((-90, 26, (0.40, 0.20, 0.18)), (-40, 34, (0.25, 0.30, 0.45)), (30, 22, PARCH)):
            c.rectangle(x, -102 - h, 46, h); fs(c, cc, 3)
    line(c, 240, -46, 330, -30, 3, (0.70, 0.66, 0.58))


def inuk(c, t, x, y, s, poses=((0, "stand"),), exprs=((0, "neutral"),), col=(0.52, 0.42, 0.30), fid=7, **kw):
    """caçador inuíte com parka de capuz de pele"""
    figure(c, t, x, y, s, poses=poses, exprs=exprs, coat=col, shirt=col, hat="hood", hat_col=(0.70, 0.62, 0.50),
           hair=None, fid=fid, **kw)


def silver_fork(c, col=(0.80, 0.82, 0.86)):
    rrect(c, -10, -20, 20, 150, 8); fs(c, col, 4)
    c.rectangle(-26, -70, 52, 54); fs(c, col, 4)
    for x in (-18, -6, 6, 18):
        line(c, x, -70, x, -120, 7, col)
    circle(c, 0, 100, 10, None, 3, (0.55, 0.50, 0.30))


def silver_spoon(c, col=(0.80, 0.82, 0.86)):
    rrect(c, -10, -20, 20, 150, 8); fs(c, col, 4)
    ellipse(c, 0, -70, 34, 52); fs(c, col, 4)
    circle(c, 0, 100, 10, None, 3, (0.55, 0.50, 0.30))


def silver_plate(c, label="SIR JOHN FRANKLIN", r=150, col=(0.78, 0.80, 0.84)):
    circle(c, 0, 0, r, col, 6)
    circle(c, 0, 0, r * 0.72, None, 3, (0.58, 0.60, 0.64))
    if label:
        text(c, label, 0, 0, int(r * 0.15), SERIF, (0.30, 0.30, 0.34))


def cook_pot(c, col=(0.32, 0.32, 0.34)):
    """panela de ferro"""
    c.move_to(-110, -60); c.line_to(110, -60); c.curve_to(110, 40, 80, 70, 0, 70); c.curve_to(-80, 70, -110, 40, -110, -60)
    c.close_path(); fs(c, col, 6)
    ellipse(c, 0, -60, 110, 18); fs(c, (0.12, 0.12, 0.13), 5)
    c.new_sub_path(); c.arc(0, -60, 130, math.pi * 1.1, math.pi * 1.9); rgb(c, INK); c.set_line_width(4); c.stroke()


def lemon(c, col=(0.92, 0.80, 0.24)):
    c.save(); c.scale(1, 0.75); c.new_sub_path(); c.arc(0, 0, 70, 0, 6.283); c.restore(); fs(c, col, 5)
    circle(c, 74, 0, 10, col, 4); circle(c, -74, 0, 8, col, 4)


def lime_bottle(c, level=1.0):
    """garrafa de suco de limão (concentrado)"""
    rrect(c, -40, -60, 80, 170, 14); fs(c, (0.30, 0.36, 0.30), 5)
    c.rectangle(-14, -110, 28, 52); fs(c, (0.30, 0.36, 0.30), 5)
    if level > 0:
        hh = 150 * level
        c.rectangle(-34, 104 - hh, 68, hh); rgb(c, (0.85, 0.78, 0.30), 0.7); c.fill()
    c.rectangle(-36, -10, 72, 50); fs(c, PARCH, 3)


def dna(c, t=0, h=420, col=ICE, col2=AMBER):
    """dupla hélice de DNA girando"""
    n = 28
    for i in range(n):
        y = -h / 2 + h * i / (n - 1)
        a = t * 1.6 + i * 0.45
        x1, x2 = math.sin(a) * 70, -math.sin(a) * 70
        if i % 2 == 0:
            line(c, x1, y, x2, y, 3, (0.55, 0.58, 0.64))
        circle(c, x1, y, 9, col if math.cos(a) > 0 else (0.35, 0.45, 0.55), 0)
        circle(c, x2, y, 9, col2 if math.cos(a) < 0 else (0.50, 0.40, 0.20), 0)


def lead_chart(c, t=0, p=1.0, w=560, h=300, spike=True):
    """gráfico simples: chumbo estável e subida no fim (p 0..1 desenha a curva)"""
    rrect(c, -w / 2, -h / 2, w, h, 8); fs(c, (0.10, 0.11, 0.13), 4)
    line(c, -w / 2 + 40, h / 2 - 40, w / 2 - 30, h / 2 - 40, 3)
    line(c, -w / 2 + 40, h / 2 - 40, -w / 2 + 40, -h / 2 + 30, 3)
    c.set_dash([8, 8]); line(c, -w / 2 + 40, -10, w / 2 - 30, -10, 2, RED); c.set_dash([])
    pts = []
    N = 40
    for i in range(N + 1):
        f = i / N
        x = -w / 2 + 40 + f * (w - 80)
        v = 0.25 + 0.03 * math.sin(i * 1.7)
        if spike and f > 0.85:
            v += (f - 0.85) / 0.15 * 0.6
        pts.append((x, h / 2 - 40 - v * (h - 80)))
    k = max(2, int(len(pts) * clamp01(p)))
    c.move_to(*pts[0])
    for q in pts[1:k]:
        c.line_to(*q)
    rgb(c, AMBER); c.set_line_width(5); c.stroke()


def locomotive_engine(c, col=(0.24, 0.24, 0.26)):
    """motor a vapor de locomotiva (caldeira, cilindro e volante)"""
    rrect(c, -170, -70, 260, 120, 50); fs(c, col, 6)
    for x in (-110, -40, 30):
        line(c, x, -70, x, 50, 3, (0.40, 0.40, 0.44))
    c.rectangle(90, -40, 70, 60); fs(c, (0.30, 0.30, 0.32), 5)
    rrect(c, -120, -130, 40, 60, 6); fs(c, (0.20, 0.20, 0.22), 5)
    circle(c, 60, 90, 60, None, 7)
    for k in range(6):
        a = k * math.pi / 3
        line(c, 60, 90, 60 + math.cos(a) * 58, 90 + math.sin(a) * 58, 4)
    line(c, 125, -10, 60, 90, 6, AMBER)


def propeller(c, t=0, spin=1.0, col=(0.72, 0.58, 0.32)):
    a0 = t * 6 * spin
    for k in range(2):
        a = a0 + k * math.pi
        c.save(); c.rotate(a); c.save(); c.scale(1, 0.38); c.new_sub_path(); c.arc(55, 0, 55, 0, 6.283); c.restore()
        fs(c, col, 4); c.restore()
    circle(c, 0, 0, 16, (0.40, 0.34, 0.24), 4)


def mast_stub(c, h=170, col=(0.36, 0.28, 0.20)):
    """pedaço de mastro de madeira saindo do gelo; origem = superfície"""
    poly(c, [(-14, 0), (-12, -h), (-2, -h - 14), (12, -h + 4), (14, 0)]); fs(c, col, 5)
    for y in (-h * 0.3, -h * 0.65):
        line(c, -14, y, 14, y, 3, (0.25, 0.20, 0.14))
    ellipse(c, 0, 4, 60, 12); rgb(c, (0.92, 0.95, 1.0), 0.9); c.fill()


def camera_compact(c, col=(0.24, 0.25, 0.28)):
    """câmera digital compacta"""
    rrect(c, -90, -55, 180, 110, 14); fs(c, col, 5)
    circle(c, 15, 0, 38, (0.12, 0.12, 0.14), 5); circle(c, 15, 0, 18, ICE, 3)
    rrect(c, -78, -46, 30, 18, 4); fs(c, (0.80, 0.80, 0.78), 3)


def cabin_corridor(c, t=0, n=6, closed=None, w=1300, h=420):
    """corredor de cabines do navio afundado: portas abertas (escuras), uma fechada"""
    rrect(c, -w / 2, -h / 2, w, h, 6); fs(c, (0.10, 0.13, 0.16), 5)
    for i in range(n):
        x = -w / 2 + (i + 0.5) * w / n
        dw, dh = w / n * 0.62, h * 0.74
        if i == closed:
            rrect(c, x - dw / 2, -dh / 2, dw, dh, 4); fs(c, (0.36, 0.25, 0.16), 5)
            line(c, x - dw / 2 + 12, -dh / 2 + 16, x + dw / 2 - 12, -dh / 2 + 16, 2, (0.25, 0.18, 0.12))
            circle(c, x + dw / 2 - 22, 10, 7, AMBER, 2)
        else:
            rrect(c, x - dw / 2, -dh / 2, dw, dh, 4); fs(c, (0.02, 0.03, 0.04), 4)
            poly(c, [(x + dw / 2, -dh / 2), (x + dw / 2 + 22, -dh / 2 + 18), (x + dw / 2 + 22, dh / 2 - 6), (x + dw / 2, dh / 2)])
            fs(c, (0.30, 0.22, 0.14), 3)
    c.rectangle(-w / 2, h / 2 - 50, w, 50); rgb(c, (0.24, 0.22, 0.18), 0.85); c.fill()


def shelf_plates(c, w=460):
    """prateleira com pratos empilhados"""
    line(c, -w / 2, 0, w / 2, 0, 8, (0.36, 0.25, 0.16))
    for i, n in enumerate((5, 7, 4, 6)):
        x = -w / 2 + 60 + i * (w - 120) / 3
        for k in range(n):
            ellipse(c, x, -10 - k * 9, 46, 8); fs(c, (0.80, 0.80, 0.76), 3)


def slipper(c, col=(0.45, 0.20, 0.24)):
    c.move_to(-80, 20); c.curve_to(-80, -30, 40, -40, 80, 0); c.curve_to(90, 20, 60, 28, 0, 28); c.close_path(); fs(c, col, 5)
    ellipse(c, -20, -6, 40, 10); rgb(c, (0.20, 0.10, 0.12)); c.fill()


def soap_bar(c, col=(0.86, 0.80, 0.66)):
    rrect(c, -60, -30, 120, 60, 20); fs(c, col, 5)
    text(c, "SOAP", 0, 0, 22, SERIF, (0.55, 0.48, 0.36))


def lantern_glow_ice(c, t, x, y, r=420):
    """brilho azulado de gelo (para cenas internas/submersas)"""
    glow(c, x, y, r, ICE, 0.12 + 0.03 * math.sin(t * 1.3))


# ================================================================== O Túmulo de Alexandre (Egito, Mediterrâneo)
GOLD = (0.86, 0.66, 0.26)
GOLD_D = (0.62, 0.45, 0.16)
MARBLE = (0.80, 0.78, 0.72)
SANDSTONE = (0.66, 0.56, 0.40)
BASALT = (0.20, 0.27, 0.24)      # pedra verde-escura do sarcófago de Nectanebo II
MED_LAND = (0.30, 0.25, 0.17)    # terra ocre dos mapas do Mediterrâneo
MED_SEA = (0.05, 0.08, 0.13)

# Mapas: aqui o mar é que é desenhado por cima da terra (litoral mais fácil de acertar).
MED_SEAS = {
    "mediterraneo": [(5, 43.3), (8.9, 44.4), (10.5, 43), (12.3, 41.7), (15.6, 40), (15.7, 38), (16.5, 38.9), (18.5, 40.2),
                     (16, 41.5), (14, 42), (12.5, 44), (12.3, 45.4), (13.8, 45.6), (15.5, 44.5), (19.5, 42.2), (19.5, 41),
                     (21, 38.5), (22.5, 36.5), (23.2, 37.4), (24, 38), (23, 39.5), (22.6, 40.5), (23.8, 40.75), (26, 40.7),
                     (26.4, 40.0), (26.6, 39.0), (27.2, 37.8), (27.6, 36.9), (28.2, 36.7), (30.5, 36.3), (32.5, 36.1),
                     (34.5, 36.8), (36.0, 36.8), (36.0, 35.5), (35.9, 34.5), (35.5, 33.5), (35.0, 32.6), (34.5, 31.5),
                     (33.4, 31.15), (32.3, 31.25), (31.4, 31.55), (30.4, 31.5), (29.9, 31.2), (29, 30.9), (25, 31.6),
                     (23, 32.6), (21.5, 32.9), (20, 30.9), (19, 30.3), (17, 31.0), (15.5, 31.5), (13, 32.9), (11, 33.2),
                     (10, 34.5), (11, 37), (9.8, 37.3), (3, 36.8), (0, 35.8), (-2, 35.1), (-5.3, 35.9), (-5.6, 36),
                     (-2, 36.7), (0.5, 40.5), (3.2, 42), (3.2, 43.3)],
    "mar_negro": [(28, 41.3), (29, 41.2), (31, 41.1), (34, 42), (36, 41.6), (38, 41), (41.5, 41.5), (41.6, 42.6), (40, 43.5),
                  (37.5, 44.7), (36.5, 45.3), (33.5, 44.5), (32.5, 45.4), (30, 45.8), (30.5, 46.6), (29.6, 45.2),
                  (28.6, 44), (28, 42)],
    "mar_vermelho": [(32.5, 29.9), (32.6, 29.5), (33.5, 28), (35, 25), (37.2, 21), (38.5, 18), (40, 16), (43.3, 12.7),
                     (43.6, 12.6), (42.7, 15), (41, 18), (39, 21.5), (37, 25), (35, 28), (34.4, 29.0), (34.9, 29.5),
                     (34.2, 28.0), (33.4, 28.8), (32.7, 30.0)],
    "golfo_persico": [(48, 30), (50, 29.5), (52, 27.5), (56, 27), (56.5, 26), (55, 25.5), (52, 24.2), (51, 26), (50, 26),
                      (48.5, 28.5)],
    "mar_arabia": [(56.4, 26.3), (57.0, 25.0), (58.5, 23.6), (59.8, 22.5), (57.8, 20.5), (55.5, 17.5), (52, 15.5),
                   (45, 13), (43.6, 12.6), (43.4, 11.5), (51, 11.8), (51, 4), (80, 4), (77.5, 8.1), (76.3, 9.5), (75, 12),
                   (74, 14.5), (73, 17), (72.8, 20), (72.6, 21.6), (70.2, 22.4), (68.6, 23.6), (67.2, 24.8), (66.5, 25.4),
                   (62, 25.2), (58, 25.6)],
    "caspio": [(49, 46.5), (51, 45.5), (50.5, 44.5), (51.5, 43), (53, 41.5), (54, 40), (53.5, 38), (51, 36.8),
               (49.5, 37.5), (49.2, 40), (48.5, 41.8), (47.5, 43), (47.5, 45.5)],
}
MED_ISLANDS = {
    "creta": [(23.5, 35.3), (24.5, 35.45), (26.3, 35.25), (26.0, 35.0), (24.5, 34.95), (23.5, 35.2)],
    "chipre": [(32.3, 35.0), (33.0, 35.4), (34.6, 35.7), (34.0, 34.9), (33.0, 34.6), (32.3, 34.8)],
    "sicilia": [(12.4, 38.1), (15.6, 38.3), (15.1, 36.7), (12.4, 37.7)],
    "rodes": [(27.7, 36.1), (28.2, 36.45), (28.25, 36.0), (27.8, 35.9)],
}
NILE = [(31.1, 31.45), (31.05, 30.6), (31.25, 30.05), (31.25, 29.85), (31.0, 28.6), (30.85, 27.6), (31.2, 27.0),
        (32.0, 26.1), (32.7, 25.7), (32.9, 24.1)]
EUPHRATES = [(38.5, 37.0), (38.3, 36.0), (40.0, 35.3), (41.5, 34.4), (43.3, 33.4), (44.4, 32.5), (46.0, 31.2), (47.6, 30.5)]
TIGRIS = [(41.0, 37.6), (42.6, 36.4), (43.2, 35.0), (44.4, 33.3), (46.3, 32.0), (47.6, 30.5)]


def draw_med_map(c, proj, grid=5, land_col=MED_LAND, sea_col=MED_SEA, rivers=True, lw=3):
    """mapa do Mediterrâneo oriental / Oriente Médio: terra ocre, mares desenhados por cima, Nilo, Eufrates e Tigre"""
    c.rectangle(0, 0, W, H); rgb(c, land_col); c.fill()
    for name, pts in MED_SEAS.items():
        poly(c, [proj(*p) for p in pts]); fs(c, sea_col, lw)
    if grid:
        c.set_dash([4, 12])
        for lon in range(-180, 181, grid):
            x, _ = proj(lon, 0)
            if 0 <= x <= W:
                line(c, x, 0, x, H, 1.5, (0.38, 0.34, 0.28))
        for lat in range(-90, 91, grid):
            _, y = proj(0, lat)
            if 0 <= y <= H:
                line(c, 0, y, W, y, 1.5, (0.38, 0.34, 0.28))
        c.set_dash([])
    for name, pts in MED_ISLANDS.items():
        poly(c, [proj(*p) for p in pts]); fs(c, land_col, lw)
    if rivers:
        for r in (NILE, EUPHRATES, TIGRIS):
            xy = [proj(*p) for p in r]
            c.move_to(*xy[0])
            for p in xy[1:]:
                c.line_to(*p)
            rgb(c, (0.30, 0.48, 0.62)); c.set_line_width(4); c.stroke()


def funeral_cart(c, t=0, glow_on=True, w=440):
    """carro fúnebre de Alexandre (Diodoro): templo dourado sobre rodas, colunas, teto com pedras, sinos e vitórias aladas"""
    if glow_on:
        glow(c, 0, -230, 380, AMBER, 0.20)
    # plataforma e rodas
    c.rectangle(-w / 2, -120, w, 34); fs(c, GOLD_D, 6)
    for x in (-w / 2 + 70, w / 2 - 70):
        circle(c, x, -50, 52, (0.30, 0.22, 0.14), 6)
        for k in range(6):
            a = k * math.pi / 3 + t * 0.0
            line(c, x, -50, x + math.cos(a) * 46, -50 + math.sin(a) * 46, 4)
        circle(c, x, -50, 12, GOLD, 4)
    # colunas
    n = 4
    for i in range(n):
        x = -w / 2 + 40 + i * (w - 80) / (n - 1)
        c.rectangle(x - 12, -300, 24, 180); fs(c, GOLD, 5)
        c.rectangle(x - 20, -312, 40, 14); fs(c, GOLD_D, 4)
    # caixão dentro (vulto)
    rrect(c, -90, -190, 180, 70, 10); fs(c, GOLD, 5)
    # teto abobadado com pedras preciosas
    c.rectangle(-w / 2 - 14, -332, w + 28, 22); fs(c, GOLD_D, 5)
    c.move_to(-w / 2 - 6, -332); c.curve_to(-w / 3, -440, w / 3, -440, w / 2 + 6, -332); c.close_path(); fs(c, GOLD, 6)
    for k, col in enumerate((RED, (0.30, 0.55, 0.40), (0.35, 0.45, 0.80), RED, (0.30, 0.55, 0.40))):
        x = -w / 3 + k * w / 6
        y = -360 - 40 * math.sin(math.pi * (k + 0.5) / 5)
        circle(c, x, y, 9, col, 3)
    # sinos (balançam)
    for i in range(5):
        x = -w / 2 + 20 + i * (w - 40) / 4
        a = math.sin(t * 3 + i) * 0.25
        c.save(); c.translate(x, -310); c.rotate(a)
        line(c, 0, 0, 0, 22, 3, GOLD_D)
        c.move_to(-10, 34); c.curve_to(-10, 18, 10, 18, 10, 34); c.close_path(); fs(c, GOLD, 3)
        c.restore()
    # vitórias aladas nos cantos
    for sx in (-1, 1):
        c.save(); c.translate(sx * (w / 2 + 2), -350)
        circle(c, 0, -28, 9, GOLD, 3)
        poly(c, [(-8, -18), (8, -18), (12, 20), (-12, 20)]); fs(c, GOLD, 3)
        c.move_to(0, -14); c.curve_to(sx * -40, -50, sx * -50, -10, sx * -30, 6); c.close_path(); fs(c, GOLD_D, 3)
        c.restore()


def mule(c, t=0, crown=True, col=(0.42, 0.38, 0.34)):
    """mula de perfil para a direita, com coroa de ouro (cascos em y=0)"""
    bob = math.sin(t * 6) * 3
    rrect(c, -95, -160 + bob, 170, 66, 30); fs(c, col, 5)
    ph = t * 6
    for i, x in enumerate((-78, -54, 44, 64)):
        sw = math.sin(ph + (i % 2) * math.pi) * 10
        line(c, x, -104 + bob, x + sw, 0, 12, INK)
        line(c, x, -104 + bob, x + sw, -4, 7, col)
    poly(c, [(50, -156 + bob), (84, -206 + bob), (148, -186 + bob), (144, -164 + bob), (96, -170 + bob), (78, -134 + bob)]); fs(c, col, 5)
    for dx in (0, 14):
        poly(c, [(84 + dx, -204 + bob), (78 + dx, -250 + bob), (96 + dx, -206 + bob)]); fs(c, col, 4)
    circle(c, 112, -190 + bob, 3.5, INK, 0)
    c.move_to(-92, -146 + bob); c.curve_to(-118, -128, -122, -96, -114, -74)
    rgb(c, INK); c.set_line_width(6); c.stroke()
    if crown:
        poly(c, [(76, -214 + bob), (82, -232 + bob), (90, -218 + bob), (98, -234 + bob), (104, -216 + bob)]); fs(c, GOLD, 3)
        glow(c, 90, -222 + bob, 40, AMBER, 0.25)


def sarcophagus(c, w=420, h=170, col=BASALT, glyphs=True, lid=0.0, seed=7):
    """sarcófago de pedra visto de lado, coberto de hieróglifos (lid: 0 fechado .. 1 tampa deslocada)"""
    rrect(c, -w / 2, -h, w, h, 12); fs(c, col, 6)
    if glyphs:
        rnd = random.Random(seed)
        gc = (col[0] + 0.28, col[1] + 0.30, col[2] + 0.26)
        for row in range(3):
            y = -h + 34 + row * (h - 50) / 3
            x = -w / 2 + 26
            while x < w / 2 - 30:
                k = rnd.randint(0, 5)
                if k == 0:
                    circle(c, x + 8, y, 7, None, 2.5, gc)
                elif k == 1:
                    line(c, x, y + 8, x + 16, y - 8, 2.5, gc)
                elif k == 2:
                    ellipse(c, x + 8, y - 3, 8, 5); rgb(c, gc); c.set_line_width(2.5); c.stroke()
                    line(c, x + 8, y + 2, x + 8, y + 10, 2.5, gc); line(c, x + 2, y + 5, x + 14, y + 5, 2.5, gc)
                elif k == 3:
                    line(c, x, y, x + 16, y, 2.5, gc); line(c, x + 4, y - 7, x + 4, y + 7, 2.5, gc)
                elif k == 4:
                    poly(c, [(x, y + 8), (x + 8, y - 8), (x + 16, y + 8)]); rgb(c, gc); c.set_line_width(2.5); c.stroke()
                else:
                    c.move_to(x, y); c.curve_to(x + 5, y - 10, x + 11, y + 10, x + 16, y); rgb(c, gc); c.set_line_width(2.5); c.stroke()
                x += 24
            line(c, -w / 2 + 16, y + 18, w / 2 - 16, y + 18, 1.5, gc)
    c.save(); c.translate(lid * 120, -lid * 30); c.rotate(-lid * 0.12)
    rrect(c, -w / 2 - 10, -h - 34, w + 20, 34, 10); fs(c, (col[0] * 0.9, col[1] * 0.9, col[2] * 0.9), 6)
    c.restore()


def royal_coffin(c, kind="gold", w=380, h=120, body=True, diadem=True, t=0, nose_chip=False):
    """caixão do rei visto de lado/cima: kind 'gold' (ouro batido) ou 'glass' (vidro/cristal, deixa ver o vulto)"""
    if kind == "gold":
        glow(c, 0, -h / 2, w * 0.7, AMBER, 0.18)
        rrect(c, -w / 2, -h, w, h, 18); fs(c, GOLD, 6)
        for k in range(1, 5):
            x = -w / 2 + k * w / 5
            line(c, x, -h + 14, x, -14, 3, GOLD_D)
        rrect(c, -w / 2 - 10, -h - 26, w + 20, 30, 12); fs(c, GOLD_D, 6)
        for k in range(6):
            circle(c, -w / 2 + 30 + k * (w - 60) / 5, -h - 11, 5, LYELLOW, 2)
        return
    # vidro: vulto deitado com diadema
    rrect(c, -w / 2, -h, w, h, 14); fs(c, (0.10, 0.12, 0.14), 6)
    if body:
        c.save(); c.translate(-w / 2 + 60, -h / 2)
        circle(c, 0, 0, 30, (0.66, 0.58, 0.44), 4)
        if diadem:
            c.new_sub_path(); c.arc(0, 0, 32, math.pi * 0.6, math.pi * 1.4); rgb(c, GOLD); c.set_line_width(7); c.stroke()
        if nose_chip:
            circle(c, 30, 4, 4, (0.10, 0.12, 0.14), 0)
        poly(c, [(28, -26), (w - 130, -30), (w - 110, 0), (w - 130, 30), (28, 26)]); fs(c, (0.52, 0.40, 0.30), 4)
        c.restore()
    g = cairo.LinearGradient(-w / 2, -h, w / 2, 0)
    g.add_color_stop_rgba(0, 0.75, 0.88, 0.95, 0.22)
    g.add_color_stop_rgba(0.5, 0.75, 0.88, 0.95, 0.06)
    g.add_color_stop_rgba(1, 0.75, 0.88, 0.95, 0.20)
    rrect(c, -w / 2, -h, w, h, 14); c.set_source(g); c.fill()
    rrect(c, -w / 2, -h, w, h, 14); rgb(c, ICE); c.set_line_width(5); c.stroke()
    for k in range(3):
        line(c, -w / 2 + 40 + k * 30, -h + 14, -w / 2 + 10 + k * 30, -h + 50, 3, (0.85, 0.94, 1.0))


def mausoleum(c, w=520, h=420, col=MARBLE):
    """o Soma: mausoléu helenístico de base escalonada, colunata e teto em pirâmide (base em 0,0)"""
    for k in range(3):
        ww = w + 60 - k * 30
        c.rectangle(-ww / 2, -30 - k * 30, ww, 30); fs(c, (col[0] * 0.85, col[1] * 0.85, col[2] * 0.85), 5)
    base = -90
    c.rectangle(-w / 2, base - 40, w, 40); fs(c, col, 5)
    n = 6
    for i in range(n):
        x = -w / 2 + 34 + i * (w - 68) / (n - 1)
        c.rectangle(x - 14, base - 200, 28, 160); fs(c, col, 4)
        line(c, x, base - 190, x, base - 50, 2, (0.55, 0.53, 0.48))
    c.rectangle(-w / 2 - 10, base - 236, w + 20, 36); fs(c, col, 5)
    poly(c, [(-w / 2 + 10, base - 236), (0, -h), (w / 2 - 10, base - 236)]); fs(c, (col[0] * 0.92, col[1] * 0.9, col[2] * 0.85), 6)
    c.rectangle(-46, base - 150, 92, 110); fs(c, (0.08, 0.07, 0.06), 4)
    glow(c, 0, base - 100, 90, AMBER, 0.30)


def mosque(c, w=420, h=300, col=(0.62, 0.56, 0.46), minaret=True):
    """mesquita: corpo, cúpula e minarete (base em 0,0)"""
    c.rectangle(-w / 2, -h * 0.5, w, h * 0.5); fs(c, col, 5)
    c.new_sub_path(); c.arc(0, -h * 0.5, w * 0.26, math.pi, 2 * math.pi); c.close_path(); fs(c, col, 5)
    line(c, 0, -h * 0.5 - w * 0.26, 0, -h * 0.5 - w * 0.26 - 30, 4)
    c.new_sub_path(); c.arc(0, -h * 0.5 - w * 0.26 - 36, 7, math.pi * 0.3, math.pi * 1.7); rgb(c, INK); c.set_line_width(3); c.stroke()
    for k in range(3):
        x = -w / 2 + 70 + k * (w - 140) / 2
        c.move_to(x - 22, -20); c.line_to(x - 22, -90); c.curve_to(x - 22, -120, x + 22, -120, x + 22, -90); c.line_to(x + 22, -20)
        c.close_path(); fs(c, (0.10, 0.09, 0.08), 3)
    if minaret:
        mx = w / 2 + 40
        c.rectangle(mx - 22, -h - 60, 44, h + 60); fs(c, col, 5)
        c.rectangle(mx - 34, -h * 0.75, 68, 14); fs(c, col, 4)
        c.rectangle(mx - 30, -h - 74, 60, 14); fs(c, col, 4)
        poly(c, [(mx - 22, -h - 74), (mx, -h - 130), (mx + 22, -h - 74)]); fs(c, col, 5)


def basilica(c, w=640, h=380, col=(0.66, 0.60, 0.50)):
    """basílica de cinco cúpulas e arcos (base em 0,0)"""
    c.rectangle(-w / 2, -h * 0.55, w, h * 0.55); fs(c, col, 5)
    for k in range(5):
        x = -w / 2 + 64 + k * (w - 128) / 4
        c.move_to(x - 40, 0); c.line_to(x - 40, -h * 0.30); c.curve_to(x - 40, -h * 0.48, x + 40, -h * 0.48, x + 40, -h * 0.30)
        c.line_to(x + 40, 0); c.close_path(); fs(c, (0.12, 0.10, 0.08) if k != 2 else (0.20, 0.16, 0.10), 4)
    for k, (x, r) in enumerate(((-w * 0.36, 52), (-w * 0.18, 60), (0, 78), (w * 0.18, 60), (w * 0.36, 52))):
        y = -h * 0.55
        c.rectangle(x - r * 0.8, y - 34, r * 1.6, 34); fs(c, col, 4)
        c.new_sub_path(); c.arc(x, y - 34, r, math.pi, 2 * math.pi); c.close_path(); fs(c, (0.40, 0.42, 0.40), 5)
        line(c, x, y - 34 - r, x, y - 34 - r - 26, 4)
        line(c, x - 9, y - 34 - r - 16, x + 9, y - 34 - r - 16, 4)


def tumulus(c, w=900, h=230, col=(0.36, 0.33, 0.24), wall=True):
    """grande túmulo macedônio (monte de terra com muro circular de mármore) - base em 0,0"""
    c.move_to(-w / 2, 0); c.curve_to(-w / 3, -h, w / 3, -h, w / 2, 0); c.close_path(); fs(c, col, 6)
    if wall:
        c.rectangle(-w / 2 + 20, -60, w - 40, 60); fs(c, MARBLE, 5)
        for k in range(1, 12):
            x = -w / 2 + 20 + k * (w - 40) / 12
            line(c, x, -58, x, -2, 2, (0.55, 0.53, 0.48))
    c.rectangle(-50, -150, 100, 90); fs(c, (0.08, 0.07, 0.06), 4)


def sphinx(c, col=MARBLE, head=False):
    """esfinge grega sentada (Anfípolis: sem cabeça) - base em 0,0"""
    c.rectangle(-70, -24, 140, 24); fs(c, (col[0] * 0.8, col[1] * 0.8, col[2] * 0.8), 4)
    c.move_to(-60, -24); c.curve_to(-62, -90, -10, -110, 20, -100); c.line_to(40, -150); c.line_to(52, -96)
    c.line_to(60, -24); c.close_path(); fs(c, col, 5)
    c.move_to(-10, -100); c.curve_to(-50, -150, -60, -120, -70, -160); c.curve_to(-30, -150, -10, -130, 4, -104); fs(c, col, 4)
    if head:
        circle(c, 46, -168, 20, col, 4)


def caryatid(c, col=MARBLE):
    """cariátide (mulher-coluna) - base em 0,0"""
    c.rectangle(-36, -20, 72, 20); fs(c, col, 4)
    poly(c, [(-30, -20), (-22, -200), (22, -200), (30, -20)]); fs(c, col, 5)
    for x in (-14, 0, 14):
        line(c, x, -190, x * 1.3, -26, 2, (0.55, 0.53, 0.48))
    circle(c, 0, -226, 24, col, 5)
    c.rectangle(-30, -270, 60, 20); fs(c, col, 4)


def cuirass(c, col=(0.74, 0.58, 0.30)):
    """couraça (peitoral) de bronze"""
    c.move_to(-90, -110); c.curve_to(-40, -130, 40, -130, 90, -110); c.line_to(80, 40); c.curve_to(40, 70, -40, 70, -80, 40)
    c.close_path(); fs(c, col, 6)
    for sx in (-1, 1):
        c.move_to(sx * 70, -100); c.curve_to(sx * 50, -60, sx * 30, -60, sx * 10, -80); rgb(c, GOLD_D); c.set_line_width(4); c.stroke()
    c.move_to(-50, -10); c.curve_to(-20, 10, 20, 10, 50, -10); rgb(c, GOLD_D); c.set_line_width(4); c.stroke()
    for x in range(-60, 70, 24):
        rrect(c, x - 9, 48, 18, 44, 4); fs(c, (0.50, 0.22, 0.16), 3)
    circle(c, 0, -50, 16, GOLD, 3)


def laurel_crown(c, r=90, col=GOLD):
    """coroa/diadema de louros de ouro"""
    glow(c, 0, 0, r * 1.6, AMBER, 0.2)
    for sx in (-1, 1):
        for k in range(9):
            a = math.pi * (0.62 + 0.085 * k) if sx < 0 else math.pi * (0.38 - 0.085 * k)
            px, py = math.cos(a) * r, math.sin(a) * r
            c.save(); c.translate(px, py); c.rotate(a + sx * 1.2)
            ellipse(c, 0, 0, 22, 9); fs(c, col, 3)
            c.restore()


def flower(c, col=(0.78, 0.30, 0.32)):
    for k in range(5):
        a = k * 2 * math.pi / 5
        circle(c, math.cos(a) * 12, math.sin(a) * 12, 10, col, 3)
    circle(c, 0, 0, 7, LYELLOW, 2)


def marble_bust(c, col=MARBLE, nose=True):
    """busto de mármore helenístico (cabelo cacheado) - base em 0,0"""
    rrect(c, -70, -40, 140, 40, 6); fs(c, (col[0] * 0.8, col[1] * 0.8, col[2] * 0.8), 5)
    c.move_to(-90, -40); c.curve_to(-90, -120, 90, -120, 90, -40); c.close_path(); fs(c, col, 5)
    rrect(c, -22, -150, 44, 50, 10); fs(c, col, 4)
    ellipse(c, 0, -205, 58, 70); fs(c, col, 5)
    for k in range(9):
        a = math.pi * (1.0 + k / 8)
        circle(c, math.cos(a) * 54, -215 + math.sin(a) * 62, 14, col, 3)
    if nose:
        poly(c, [(4, -214), (14, -186), (2, -184)]); rgb(c, INK); c.set_line_width(3); c.stroke()
    line(c, -24, -222, -8, -220, 3); line(c, 14, -220, 30, -222, 3)
    line(c, -8, -168, 12, -168, 3)


def tsunami_wave(c, t=0, w=1400, h=520, col=(0.20, 0.32, 0.42)):
    """onda gigante quebrando, da esquerda para a direita (base em 0,0)"""
    c.move_to(-w / 2, 0); c.line_to(-w / 2, -h * 0.55)
    c.curve_to(-w * 0.2, -h * 0.8, w * 0.15, -h * 1.05, w * 0.32, -h * 0.9)
    c.curve_to(w * 0.45, -h * 0.8, w * 0.42, -h * 0.55, w * 0.30, -h * 0.58)
    c.curve_to(w * 0.25, -h * 0.4, w * 0.35, -h * 0.15, w / 2, 0); c.close_path(); fs(c, col, 6)
    for k in range(4):
        y = -h * (0.2 + 0.14 * k)
        c.move_to(-w / 2 + 40, y); c.curve_to(-w * 0.1, y - 30 + math.sin(t * 2 + k) * 8, w * 0.1, y + 10, w * 0.25, y - 20)
        rgb(c, (0.55, 0.70, 0.80)); c.set_line_width(3); c.stroke()
    for k in range(10):
        x = w * 0.2 + k * 14 + math.sin(t * 4 + k) * 6
        circle(c, x, -h * 0.85 + k * 10, 6, (0.85, 0.92, 0.96), 2)


def crocodile(c, col=(0.24, 0.32, 0.22)):
    """crocodilo de perfil, nadando (linha d'água em 0)"""
    c.move_to(-200, -6); c.curve_to(-120, -40, 60, -46, 120, -26); c.line_to(220, -20); c.line_to(220, -6); c.line_to(120, 0)
    c.close_path(); fs(c, col, 5)
    for k in range(7):
        x = -140 + k * 34
        poly(c, [(x, -34), (x + 10, -48), (x + 20, -36)]); fs(c, col, 3)
    circle(c, 138, -32, 6, LYELLOW, 3)
    for k in range(5):
        line(c, 160 + k * 12, -20, 164 + k * 12, -12, 2)


def brick_wall(c, w=300, h=260, p=1.0, col=(0.52, 0.32, 0.22)):
    """parede de tijolos subindo de baixo para cima (p 0..1); base em 0,0"""
    rows = int(h / 30)
    shown = int(math.ceil(rows * clamp01(p)))
    for r in range(shown):
        y = -(r + 1) * 30
        off = 0 if r % 2 == 0 else 30
        x = -w / 2 - off
        while x < w / 2:
            x0, x1 = max(x, -w / 2), min(x + 60, w / 2)
            if x1 > x0:
                c.rectangle(x0, y, x1 - x0, 30); fs(c, col, 3)
            x += 60


def modern_city(c, t=0, w=1920, seed=5, col=(0.17, 0.16, 0.15)):
    """prédios da cidade moderna (base em 0,0, de -w/2 a w/2) com janelas acesas"""
    rnd = random.Random(seed)
    x = -w / 2
    while x < w / 2:
        bw = rnd.randint(90, 170)
        bh = rnd.randint(180, 420)
        c.rectangle(x, -bh, bw - 8, bh); fs(c, col, 4)
        for yy in range(-bh + 26, -20, 44):
            for xx in range(int(x) + 16, int(x + bw - 30), 34):
                if rnd.random() < 0.35:
                    c.rectangle(xx, yy, 14, 18); rgb(c, (0.95, 0.78, 0.42), 0.7 + 0.2 * math.sin(t + xx)); c.fill()
        x += bw


def palm_oasis(c, t=0):
    """palmeira de oásis curvada (base em 0,0)"""
    c.move_to(-10, 0); c.curve_to(-14, -120, 10, -220, 40, -300); c.line_to(54, -296); c.curve_to(26, -220, 6, -120, 10, 0)
    c.close_path(); fs(c, (0.42, 0.32, 0.20), 4)
    for k in range(7):
        a = math.pi * (1.05 + k * 0.15) + math.sin(t * 0.8 + k) * 0.04
        c.move_to(47, -298); c.curve_to(47 + math.cos(a) * 60, -298 + math.sin(a) * 60 - 20,
                                      47 + math.cos(a) * 130, -298 + math.sin(a) * 110, 47 + math.cos(a) * 150, -298 + math.sin(a) * 150 + 40)
        rgb(c, (0.24, 0.36, 0.20)); c.set_line_width(14); c.stroke_preserve(); rgb(c, INK); c.set_line_width(3); c.stroke()


def dunes(c, t=0, y=820, col=(0.42, 0.33, 0.20)):
    """dunas no horizonte (de y até o fim da tela)"""
    for k, (yy, cc) in enumerate(((y, col), (y + 80, (col[0] * 0.8, col[1] * 0.8, col[2] * 0.8)))):
        c.move_to(0, yy)
        for x in range(0, W + 120, 120):
            c.line_to(x, yy + math.sin(x / (230 + k * 80) + k) * 34)
        c.line_to(W, H); c.line_to(0, H); c.close_path(); fs(c, cc, 4)


def alexandria_skyline(c, t=0, w=1600):
    """Alexandria antiga vista do mar: farol, muralha, colunatas e o palácio (base em 0,0)"""
    c.rectangle(-w / 2, -60, w, 60); fs(c, (0.46, 0.40, 0.30), 4)
    for k in range(9):
        x = -w / 2 + 140 + k * (w - 300) / 8
        hh = 90 + (k * 37 % 70)
        c.rectangle(x - 50, -60 - hh, 100, hh); fs(c, (0.56, 0.50, 0.40), 4)
        for j in range(4):
            line(c, x - 36 + j * 24, -60 - hh + 14, x - 36 + j * 24, -66, 2, (0.40, 0.35, 0.28))
    c.save(); c.translate(w / 2 - 80, -50); c.scale(0.8, 0.8); lighthouse(c, t); c.restore()
