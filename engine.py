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
def background(c, t):
    """fundo noturno com leve gradiente"""
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.055, 0.062, 0.085)
    g.add_color_stop_rgb(1, 0.095, 0.090, 0.100)
    c.set_source(g); c.paint()


def fog(c, t, y=820, alpha=0.07, n=6, col=INK):
    """névoa rasteira que se move devagar"""
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
