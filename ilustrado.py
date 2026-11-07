"""
ESTILO ILUSTRADO do Ponto Cego (ilustração vetorial chapada, sem contorno de giz).

Use no scenes.py:
    from engine import *
    from ilustrado import *
    STYLE = "ilustrado"          # vinheta suave, sem poeira de giz
    THEME = "classico"           # o tema continua mandando no som ambiente

Cada cena começa escolhendo a LUZ (hora do dia) e um CENÁRIO:
    def s01(c, t):
        cena_vila(c, t, "tarde")                 # céu, montanhas, casas, chão (já chama luz())
        historiador_i(c, t, 330, 1000, 1.0, ...) # personagens herdam a luz da cena
Luzes: dia, tarde, crepusculo, noite, nublado, sepia, vela (interior à luz de vela), interior (interior de dia).
Os personagens usam as mesmas poses e expressões dos bonecos de giz.
"""
import cairo, math, random
from engine import *
import engine

# ================================================================ cores e luz
def mix(a, b, k):
    return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k)


def mul(a, b):
    return (a[0] * b[0], a[1] * b[1], a[2] * b[2])


def dk(col, k=0.2):
    return mix(col, (0, 0, 0), k)


def lt(col, k=0.2):
    return mix(col, (1, 1, 1), k)


# ceu=(topo, horizonte)  tinta=cor da luz ambiente  tk=força da tinta  neb=névoa de distância  nebk=força
# astro=("sol"|"lua", x, y, cor)  dir = de onde vem a luz (-1 esquerda, 1 direita)  noite = janelas acesas
LUZES = {
    "dia":        dict(ceu=((0.52, 0.71, 0.84), (0.86, 0.89, 0.84)), tinta=(1, 1, 1), tk=0.0,
                       neb=(0.80, 0.86, 0.88), nebk=0.75, astro=("sol", 1500, 210, (1.0, 0.97, 0.86)),
                       nuvem=(0.97, 0.96, 0.92), dir=-1, noite=False, estrelas=False, fora=(0.70, 0.82, 0.90)),
    "tarde":      dict(ceu=((0.86, 0.62, 0.42), (0.99, 0.86, 0.60)), tinta=(1.0, 0.86, 0.68), tk=0.85,
                       neb=(0.98, 0.84, 0.62), nebk=0.70, astro=("sol", 1480, 560, (1.0, 0.93, 0.70)),
                       nuvem=(0.99, 0.88, 0.72), dir=1, noite=False, estrelas=False, fora=(0.98, 0.80, 0.55)),
    "crepusculo": dict(ceu=((0.30, 0.25, 0.45), (0.95, 0.62, 0.46)), tinta=(0.78, 0.62, 0.72), tk=0.9,
                       neb=(0.78, 0.55, 0.58), nebk=0.70, astro=("sol", 1380, 640, (1.0, 0.80, 0.55)),
                       nuvem=(0.80, 0.55, 0.62), dir=1, noite=True, estrelas=False, fora=(0.80, 0.55, 0.55)),
    "noite":      dict(ceu=((0.05, 0.08, 0.17), (0.17, 0.22, 0.35)), tinta=(0.42, 0.50, 0.74), tk=1.0,
                       neb=(0.20, 0.26, 0.40), nebk=0.70, astro=("lua", 1500, 200, (0.95, 0.94, 0.86)),
                       nuvem=(0.22, 0.27, 0.40), dir=1, noite=True, estrelas=True, fora=(0.12, 0.17, 0.30)),
    "nublado":    dict(ceu=((0.58, 0.62, 0.66), (0.80, 0.80, 0.76)), tinta=(0.86, 0.88, 0.90), tk=1.0,
                       neb=(0.74, 0.76, 0.76), nebk=0.75, astro=None,
                       nuvem=(0.70, 0.72, 0.74), dir=-1, noite=False, estrelas=False, fora=(0.72, 0.75, 0.78)),
    "sepia":      dict(ceu=((0.85, 0.77, 0.58), (0.95, 0.89, 0.72)), tinta=(1.0, 0.90, 0.72), tk=0.8,
                       neb=(0.93, 0.86, 0.68), nebk=0.75, astro=None,
                       nuvem=(0.96, 0.90, 0.76), dir=-1, noite=False, estrelas=False, fora=(0.95, 0.88, 0.70)),
    "vela":       dict(ceu=((0.10, 0.09, 0.10), (0.16, 0.13, 0.12)), tinta=(0.80, 0.58, 0.40), tk=1.0,
                       neb=(0.20, 0.14, 0.10), nebk=0.6, astro=None,
                       nuvem=(0.2, 0.2, 0.2), dir=1, noite=True, estrelas=False, fora=(0.10, 0.14, 0.26)),
    "interior":   dict(ceu=((0.55, 0.60, 0.66), (0.70, 0.72, 0.74)), tinta=(0.86, 0.88, 0.94), tk=1.0,
                       neb=(0.70, 0.72, 0.76), nebk=0.6, astro=None,
                       nuvem=(0.9, 0.9, 0.9), dir=1, noite=False, estrelas=False, fora=(0.82, 0.88, 0.94)),
}
_L = LUZES["dia"]


def luz(nome="dia"):
    """define a luz da cena (chame no começo de cada cena; os cenários prontos já chamam)"""
    global _L
    if nome not in LUZES:
        raise ValueError(f"luz desconhecida: {nome} (opções: {', '.join(LUZES)})")
    _L = LUZES[nome]
    return _L


def P(col, depth=0.0):
    """cor iluminada pela luz da cena. depth 0 = primeiro plano, 1 = horizonte (some na névoa)"""
    tin = mix((1, 1, 1), _L["tinta"], _L["tk"])
    out = mul(col, tin)
    if depth > 0:
        out = mix(out, _L["neb"], min(1.0, depth) * _L["nebk"])
    return out


def pinta(c, col, a=1.0, depth=0.0):
    rgb(c, P(col, depth), a); c.fill()


def pg(c, pts):
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.close_path()


def rr(c, x, y, w, h, r):
    rrect(c, x, y, w, h, r)


def lgrad(c, x0, y0, x1, y1, stops):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for k, col, a in stops:
        g.add_color_stop_rgba(k, col[0], col[1], col[2], a)
    c.set_source(g)


def rglow(c, x, y, r, col, a=0.4):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, col[0], col[1], col[2], a)
    g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
    c.set_source(g); c.arc(x, y, r, 0, 2 * math.pi); c.fill()


# paleta base (antes da luz)
PEDRA = (0.72, 0.68, 0.60)
REBOCO = (0.86, 0.76, 0.60)
TELHA = (0.70, 0.38, 0.26)
MADEIRA = (0.45, 0.31, 0.20)
MADEIRA_ESC = (0.30, 0.20, 0.13)
GRAMA = (0.52, 0.62, 0.36)
TERRA = (0.62, 0.50, 0.36)
AREIA = (0.90, 0.76, 0.52)
NEVE_C = (0.92, 0.94, 0.97)
AGUA = (0.30, 0.48, 0.60)
FOLHA = (0.30, 0.48, 0.30)
JANELA_ACESA = (1.0, 0.78, 0.42)
OURO = (0.88, 0.70, 0.30)
PELES = dict(clara=(0.95, 0.80, 0.68), media=(0.85, 0.65, 0.50), morena=(0.66, 0.47, 0.34), escura=(0.44, 0.30, 0.22))
CABELOS = dict(preto=(0.14, 0.11, 0.10), castanho=(0.33, 0.22, 0.14), loiro=(0.80, 0.64, 0.38),
               ruivo=(0.66, 0.32, 0.16), grisalho=(0.62, 0.60, 0.58), branco=(0.90, 0.89, 0.86))


# ================================================================ céu e astros
def nuvem(c, x, y, w, col, seed=1, depth=0.3):
    """nuvem chapada de base reta"""
    rnd = random.Random(seed)
    c.save()
    c.rectangle(x - w, y - w, w * 2, w)  # só acima da base
    c.clip()
    n = 5
    for i in range(n):
        cx = x - w * 0.42 + i * w * 0.84 / (n - 1)
        r = w * (0.16 + 0.12 * math.sin(i / (n - 1) * math.pi)) * rnd.uniform(0.85, 1.15)
        c.new_sub_path(); c.arc(cx, y - r * 0.35, r, 0, 2 * math.pi)
    rgb(c, P(col, depth)); c.fill()
    c.restore()
    rr(c, x - w * 0.5, y - 10, w, 10, 5)
    rgb(c, dk(P(col, depth), 0.07)); c.fill()


def ceu(c, t, nuvens=True, astro=True, passaros=False, seed=1, horizonte=760):
    L = _L
    lgrad(c, 0, 0, 0, horizonte, [(0, L["ceu"][0], 1), (1, L["ceu"][1], 1)])
    c.paint()
    if L["estrelas"]:
        rnd = random.Random(seed * 7)
        for i in range(140):
            x, y, r = rnd.uniform(0, W), rnd.uniform(0, horizonte * 0.75), rnd.uniform(0.8, 2.4)
            a = 0.35 + 0.5 * (0.5 + 0.5 * math.sin(t * rnd.uniform(0.6, 2.0) + i))
            rgb(c, (0.95, 0.93, 0.85), a * (1 - y / horizonte)); c.new_sub_path(); c.arc(x, y, r, 0, 6.283); c.fill()
    if astro and L["astro"]:
        kind, ax, ay, col = L["astro"]
        if isinstance(astro, tuple):
            ax, ay = astro
        if kind == "sol":
            c.save()
            for i in range(9):
                a = i * math.pi * 2 / 9 + t * 0.02
                c.move_to(ax, ay); c.line_to(ax + math.cos(a) * 1600, ay + math.sin(a) * 1600)
                c.line_to(ax + math.cos(a + 0.09) * 1600, ay + math.sin(a + 0.09) * 1600); c.close_path()
            g = cairo.RadialGradient(ax, ay, 40, ax, ay, 1200)
            g.add_color_stop_rgba(0, col[0], col[1], col[2], 0.16)
            g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
            c.set_source(g); c.fill(); c.restore()
            rglow(c, ax, ay, 520, col, 0.45)
            rglow(c, ax, ay, 160, (1, 1, 0.95), 0.5)
            c.new_sub_path(); c.arc(ax, ay, 56, 0, 6.283); rgb(c, lt(col, 0.4)); c.fill()
        else:
            rglow(c, ax, ay, 380, (0.75, 0.80, 0.95), 0.22)
            c.new_sub_path(); c.arc(ax, ay, 58, 0, 6.283); rgb(c, col); c.fill()
            for dx, dy, r in ((-18, -10, 11), (14, 16, 8), (20, -20, 6), (-6, 24, 5)):
                c.new_sub_path(); c.arc(ax + dx, ay + dy, r, 0, 6.283); rgb(c, dk(col, 0.08)); c.fill()
    if nuvens:
        rnd = random.Random(seed)
        for i in range(nuvens if isinstance(nuvens, int) and nuvens is not True else 4):
            w = rnd.uniform(260, 460)
            y = rnd.uniform(110, horizonte * 0.5)
            x = (rnd.uniform(0, W) + t * rnd.uniform(4, 10)) % (W + 600) - 300
            nuvem(c, x, y, w, L["nuvem"], seed=seed * 13 + i, depth=0.25)
    if passaros:
        rnd = random.Random(seed + 99)
        for i in range(passaros if isinstance(passaros, int) and passaros is not True else 5):
            x = (rnd.uniform(0, W) + t * rnd.uniform(30, 60)) % (W + 200) - 100
            y = rnd.uniform(120, 360) + math.sin(t * 0.8 + i) * 12
            f = math.sin(t * 9 + i * 1.7) * 6
            c.move_to(x - 12, y - 4 - f); c.line_to(x, y); c.line_to(x + 12, y - 4 - f)
            rgb(c, dk(_L["neb"], 0.55), 0.8); c.set_line_width(2.6); c.stroke()


# ================================================================ terreno
def montanhas(c, y=640, h=300, seed=1, depth=0.75, col=(0.42, 0.46, 0.52), neve=False, picos=7, x0=-100, x1=None):
    """cordilheira chapada com face iluminada e face na sombra"""
    x1 = x1 if x1 is not None else W + 100
    rnd = random.Random(seed)
    xs = [x0 + (x1 - x0) * i / picos + rnd.uniform(-40, 40) for i in range(picos + 1)]
    base = P(col, depth)
    for i, px in enumerate(xs):
        ph = h * rnd.uniform(0.55, 1.0)
        hw = (x1 - x0) / picos * rnd.uniform(0.75, 1.15)
        top = (px, y - ph)
        pg(c, [(px - hw, y + 4), top, (px + hw, y + 4)])
        rgb(c, base); c.fill()
        # face na sombra (do lado oposto à luz)
        side = -_L["dir"]
        pg(c, [top, (px + side * hw, y + 4), (px + side * hw * 0.15, y + 4)])
        rgb(c, dk(base, 0.12)); c.fill()
        if neve:
            k = 0.28
            sn = [(px - hw * k, y - ph * (1 - k)), top, (px + hw * k, y - ph * (1 - k)),
                  (px + hw * k * 0.4, y - ph * (1 - k) + 18), (px, y - ph * (1 - k) + 4), (px - hw * k * 0.5, y - ph * (1 - k) + 22)]
            pg(c, sn); rgb(c, P(NEVE_C, depth * 0.6)); c.fill()
    c.rectangle(x0, y, x1 - x0, 6); rgb(c, base); c.fill()


def colinas(c, y=720, amp=40, seed=1, col=GRAMA, depth=0.4, ate=H):
    rnd = random.Random(seed)
    ks = [(rnd.uniform(0.002, 0.006), rnd.uniform(0, 6.28), rnd.uniform(0.4, 1.0)) for _ in range(3)]
    c.move_to(-20, ate)
    for x in range(-20, W + 41, 20):
        yy = y - amp * sum(a * math.sin(x * f + p) for f, p, a in ks) / 2
        c.line_to(x, yy)
    c.line_to(W + 40, ate); c.close_path()
    rgb(c, P(col, depth)); c.fill()


def chao(c, t=0, y=860, tipo="grama", seed=1, ate=H):
    """faixa de chão do primeiro plano: grama, terra, pedra (calçamento), areia, neve, madeira (convés/assoalho)"""
    cols = dict(grama=GRAMA, terra=TERRA, pedra=(0.60, 0.57, 0.52), areia=AREIA, neve=NEVE_C, madeira=MADEIRA)
    base = cols.get(tipo, TERRA)
    lgrad(c, 0, y, 0, ate, [(0, P(lt(base, 0.06)), 1), (1, P(dk(base, 0.18)), 1)])
    c.rectangle(-20, y, W + 40, ate - y); c.fill()
    rnd = random.Random(seed)
    if tipo == "pedra":
        rows = 7
        for r in range(rows):
            k = r / rows
            yy = y + (ate - y) * (k ** 1.4)
            hh = (ate - y) * (((r + 1) / rows) ** 1.4 - k ** 1.4)
            sw = 60 + 120 * k
            off = (r % 2) * sw / 2
            x = -off
            while x < W + 20:
                rr(c, x + 3, yy + 2, sw - 6, hh - 4, 6 + 6 * k)
                rgb(c, P(dk(base, rnd.uniform(0.0, 0.12)))); c.fill()
                x += sw
    elif tipo == "madeira":
        for i in range(-12, 13):
            x0 = W / 2 + i * 70
            c.move_to(W / 2 + i * 36, y); c.line_to(x0 + i * 60, ate)
            rgb(c, P(dk(base, 0.25)), 0.6); c.set_line_width(3); c.stroke()
    else:
        for i in range(70):
            x = rnd.uniform(0, W)
            k = rnd.uniform(0, 1) ** 1.6
            yy = y + 8 + (ate - y - 8) * k
            sz = 6 + 22 * k
            if tipo == "grama":
                sway = math.sin(t * 1.5 + x * 0.01) * 3
                for j in (-1, 0, 1):
                    c.move_to(x + j * sz * 0.4, yy); c.line_to(x + j * sz * 0.7 + sway, yy - sz * 1.4); c.line_to(x + j * sz * 0.4 + 4, yy)
                rgb(c, P(dk(base, 0.15))); c.fill()
            elif tipo == "terra":
                ellipse(c, x, yy, sz * 0.8, sz * 0.35); rgb(c, P(dk(base, 0.12))); c.fill()
            elif tipo == "areia":
                c.move_to(x - sz * 3, yy); c.curve_to(x - sz, yy - sz * 0.4, x + sz, yy - sz * 0.4, x + sz * 3, yy)
                rgb(c, P(dk(base, 0.10)), 0.7); c.set_line_width(2.5); c.stroke()
            elif tipo == "neve":
                ellipse(c, x, yy, sz * 2, sz * 0.3); rgb(c, P(dk(base, 0.06))); c.fill()
    # borda
    c.rectangle(-20, y, W + 40, 5); rgb(c, P(dk(base, 0.22)), 0.5); c.fill()


# ================================================================ vegetação
def arvore(c, t, x, y, h=300, tipo="redonda", col=FOLHA, seed=1, depth=0.0, seca=False):
    """árvore chapada: redonda, pinheiro, palmeira, cipreste"""
    rnd = random.Random(seed)
    sway = math.sin(t * 0.9 + seed) * 0.012
    c.save(); c.translate(x, y); c.rotate(sway)
    tr = P(MADEIRA_ESC, depth)
    leaf = P(mix(col, (rnd.uniform(0.2, 0.4), rnd.uniform(0.4, 0.55), 0.25), 0.25), depth)
    if tipo == "palmeira":
        c.move_to(-12, 0); c.curve_to(-12, -h * 0.5, 6, -h * 0.8, 2, -h); c.line_to(18, -h); c.curve_to(24, -h * 0.8, 10, -h * 0.5, 14, 0)
        c.close_path(); rgb(c, P((0.50, 0.38, 0.24), depth)); c.fill()
        for i in range(9):
            a = -math.pi / 2 + (i - 4) * 0.42 + math.sin(t + i) * 0.04
            L_ = h * 0.42
            ex, ey = 10 + math.cos(a) * L_, -h + math.sin(a) * L_ + L_ * 0.35
            c.move_to(10, -h); c.curve_to(10 + math.cos(a) * L_ * 0.5, -h + math.sin(a) * L_ * 0.6 - 20, ex, ey - 10, ex, ey)
            c.curve_to(ex - 10, ey - 40, 10 + math.cos(a) * L_ * 0.4, -h + math.sin(a) * L_ * 0.4 - 46, 10, -h)
            rgb(c, leaf if i % 2 else dk(leaf, 0.12)); c.fill()
        c.restore(); return
    c.rectangle(-h * 0.035, -h * 0.45, h * 0.07, h * 0.45); rgb(c, tr); c.fill()
    if seca:
        for i in range(5):
            a = -math.pi / 2 + (i - 2) * 0.45
            c.move_to(0, -h * 0.4); c.line_to(math.cos(a) * h * 0.4, -h * 0.4 + math.sin(a) * h * 0.45)
            rgb(c, tr); c.set_line_width(h * 0.02); c.stroke()
        c.restore(); return
    if tipo == "pinheiro":
        for i in range(4):
            yy = -h * 0.25 - i * h * 0.2
            ww = h * (0.32 - i * 0.06)
            pg(c, [(-ww, yy), (0, yy - h * 0.34), (ww, yy)]); rgb(c, leaf); c.fill()
            pg(c, [(0, yy - h * 0.34), (ww * -_L["dir"], yy), (0, yy)]); rgb(c, dk(leaf, 0.14)); c.fill()
    elif tipo == "cipreste":
        ellipse(c, 0, -h * 0.55, h * 0.12, h * 0.48); rgb(c, leaf); c.fill()
    else:
        blobs = [(0, -h * 0.72, h * 0.30), (-h * 0.2, -h * 0.55, h * 0.22), (h * 0.2, -h * 0.56, h * 0.23), (0, -h * 0.5, h * 0.24)]
        for bx, by, br in blobs:
            c.new_sub_path(); c.arc(bx, by, br, 0, 6.283)
        rgb(c, leaf); c.fill()
        side = -_L["dir"]
        c.new_sub_path(); c.arc(side * h * 0.16, -h * 0.5, h * 0.2, 0, 6.283); rgb(c, dk(leaf, 0.12)); c.fill()
        c.new_sub_path(); c.arc(-side * h * 0.08, -h * 0.78, h * 0.12, 0, 6.283); rgb(c, lt(leaf, 0.10)); c.fill()
    c.restore()


def floresta(c, t, y=760, n=14, h=(220, 360), tipos=("redonda", "pinheiro"), col=FOLHA, seed=3, depth=0.4):
    rnd = random.Random(seed)
    items = []
    for i in range(n):
        x = -80 + (W + 160) * i / (n - 1) + rnd.uniform(-50, 50)
        items.append((x, rnd.uniform(*h), rnd.choice(tipos), seed * 31 + i))
    for x, hh, tp, sd in items:
        arvore(c, t, x, y, hh, tp, col, sd, depth)


# ================================================================ construções
def janela_i(c, x, y, w, h, estilo="reta", acesa=None, persiana=None, depth=0.0):
    """janela; acesa=None segue a luz da cena (acesa à noite)"""
    if acesa is None:
        acesa = _L["noite"]
    moldura = P(dk(REBOCO, 0.35), depth)
    vid = JANELA_ACESA if acesa else mix(_L["fora"], (0.2, 0.24, 0.3), 0.55)

    def forma(px, py, pw, ph):
        if estilo == "arco":
            c.move_to(px, py + ph); c.line_to(px, py + pw / 2); c.arc(px + pw / 2, py + pw / 2, pw / 2, math.pi, 2 * math.pi)
            c.line_to(px + pw, py + ph); c.close_path()
        elif estilo == "gotica":
            c.move_to(px, py + ph); c.line_to(px, py + pw * 0.6)
            c.curve_to(px, py + pw * 0.2, px + pw * 0.3, py, px + pw / 2, py - pw * 0.15)
            c.curve_to(px + pw * 0.7, py, px + pw, py + pw * 0.2, px + pw, py + pw * 0.6)
            c.line_to(px + pw, py + ph); c.close_path()
        else:
            c.rectangle(px, py, pw, ph)
    forma(x - 6, y - 6, w + 12, h + 12); rgb(c, moldura); c.fill()
    forma(x, y, w, h)
    rgb(c, P(vid, depth) if not acesa else vid); c.fill()
    if acesa:
        rglow(c, x + w / 2, y + h / 2, max(w, h) * 1.1, JANELA_ACESA, 0.22)
    c.move_to(x + w / 2, y + 4); c.line_to(x + w / 2, y + h); rgb(c, moldura); c.set_line_width(4); c.stroke()
    c.move_to(x, y + h * 0.5); c.line_to(x + w, y + h * 0.5); c.stroke()
    if persiana is not None:
        for sx in (-1, 1):
            px = x - w * 0.5 - 6 if sx < 0 else x + w + 6
            c.rectangle(px, y - 4, w * 0.5, h + 8); rgb(c, P(persiana, depth)); c.fill()
            for k in range(1, 6):
                c.move_to(px + 3, y + (h + 8) * k / 6); c.line_to(px + w * 0.5 - 3, y + (h + 8) * k / 6)
                rgb(c, P(dk(persiana, 0.2), depth)); c.set_line_width(2); c.stroke()
    c.rectangle(x - 10, y + h + 4, w + 20, 8); rgb(c, moldura); c.fill()


def predio(c, x, y, w, h, estilo="medieval", col=None, seed=1, depth=0.0, telhado=True, porta=True):
    """fachada: medieval (enxaimel + telhado íngreme), pedra, colonial (pastel, sacadas), moderno"""
    rnd = random.Random(seed)
    if col is None:
        col = {"medieval": rnd.choice([(0.90, 0.84, 0.70), (0.86, 0.78, 0.62), (0.80, 0.74, 0.64)]),
               "pedra": rnd.choice([(0.70, 0.66, 0.58), (0.64, 0.60, 0.54)]),
               "colonial": rnd.choice([(0.92, 0.80, 0.62), (0.86, 0.66, 0.58), (0.70, 0.78, 0.74), (0.90, 0.86, 0.72), (0.66, 0.72, 0.80)]),
               "moderno": rnd.choice([(0.62, 0.62, 0.64), (0.70, 0.66, 0.60)])}[estilo]
    base = P(col, depth)
    top = y - h
    # telhado
    if telhado and estilo == "medieval":
        rh = w * rnd.uniform(0.45, 0.65)
        pg(c, [(x - 14, top + 6), (x + w / 2, top - rh), (x + w + 14, top + 6)])
        rgb(c, P(TELHA, depth)); c.fill()
        for k in range(1, 6):
            yy = top - rh + rh * k / 6 + 6
            hw = (w / 2 + 14) * k / 6
            c.move_to(x + w / 2 - hw, yy); c.line_to(x + w / 2 + hw, yy)
            rgb(c, P(dk(TELHA, 0.18), depth)); c.set_line_width(3); c.stroke()
    elif telhado and estilo in ("colonial", "pedra"):
        c.rectangle(x - 10, top - 26, w + 20, 26); rgb(c, P(TELHA, depth)); c.fill()
        for k in range(0, int(w / 18) + 2):
            c.move_to(x - 10 + k * 18, top - 26); c.line_to(x - 10 + k * 18, top)
            rgb(c, P(dk(TELHA, 0.2), depth)); c.set_line_width(2); c.stroke()
    c.rectangle(x, top, w, h); rgb(c, base); c.fill()
    if estilo == "pedra":
        rows = int(h / 34)
        for r in range(rows):
            yy = top + r * 34
            off = (r % 2) * 30
            xx = x - off
            while xx < x + w:
                c.rectangle(max(x, xx) + 2, yy + 2, min(60, x + w - xx) - 4, 30)
                rgb(c, dk(base, rnd.uniform(0.0, 0.10))); c.fill()
                xx += 60
    if estilo == "colonial":
        c.rectangle(x - 6, top, w + 12, 16); rgb(c, lt(base, 0.25)); c.fill()  # cornija
        c.rectangle(x - 4, y - 70, w + 8, 70); rgb(c, dk(base, 0.10)); c.fill()  # barrado
    floors = max(1, int((h - 60) / 150))
    fh = (h - 30) / floors
    cols_ = max(1, int(w / 110))
    for f in range(floors):
        fy = top + 30 + f * fh
        if estilo == "medieval" and f < floors:
            c.rectangle(x, fy - 8, w, 9); rgb(c, P(MADEIRA_ESC, depth)); c.fill()
            if f > 0 or rnd.random() < 0.5:
                for k in range(cols_ + 1):
                    xx = x + w * k / cols_
                    c.rectangle(xx - 4, fy - 8, 8, fh); rgb(c, P(MADEIRA_ESC, depth)); c.fill()
                    if k < cols_ and rnd.random() < 0.5:
                        c.move_to(xx + 4, fy + fh - 8); c.line_to(xx + w / cols_ * 0.28, fy)
                        rgb(c, P(MADEIRA_ESC, depth)); c.set_line_width(7); c.stroke()
        is_ground = f == floors - 1
        for k in range(cols_):
            cx = x + w * (k + 0.5) / cols_
            if is_ground and porta and k == cols_ // 2:
                continue
            ww, wh = min(46, w / cols_ * 0.42), fh * 0.45
            est = {"colonial": "arco", "pedra": "reta", "medieval": "reta", "moderno": "reta"}[estilo]
            pers = (0.24, 0.38, 0.30) if estilo == "colonial" else (MADEIRA if estilo == "medieval" and rnd.random() < 0.4 else None)
            acesa = None if rnd.random() < 0.6 else False
            janela_i(c, cx - ww / 2, fy + fh * 0.22, ww, wh, est, acesa, pers, depth)
            if estilo == "colonial" and not is_ground:
                c.rectangle(cx - ww, fy + fh * 0.22 + wh + 6, ww * 2, 6); rgb(c, P((0.18, 0.18, 0.2), depth)); c.fill()
                for b in range(7):
                    c.rectangle(cx - ww + b * ww * 2 / 6 - 1, fy + fh * 0.22 + wh + 12, 3, 26); c.fill()
    if porta:
        pw, ph = min(70, w * 0.3), min(130, fh * 0.8)
        px = x + w * ((cols_ // 2) + 0.5) / cols_ - pw / 2
        c.move_to(px, y); c.line_to(px, y - ph + pw / 2); c.arc(px + pw / 2, y - ph + pw / 2, pw / 2, math.pi, 2 * math.pi)
        c.line_to(px + pw, y); c.close_path()
        rgb(c, P(MADEIRA_ESC, depth)); c.fill()
        c.move_to(px + pw / 2, y - ph); c.line_to(px + pw / 2, y); rgb(c, P(dk(MADEIRA_ESC, 0.3), depth)); c.set_line_width(3); c.stroke()
    # sombra lateral (volume)
    side = -_L["dir"]
    sx = x + w - 22 if side > 0 else x
    c.rectangle(sx, top, 22, h); rgb(c, (0, 0, 0), 0.10); c.fill()


def casario(c, t, y=820, estilo="medieval", seed=3, depth=0.0, h=(320, 520), w=(220, 330), escala=1.0, x0=-60, x1=None):
    x1 = x1 if x1 is not None else W + 60
    rnd = random.Random(seed)
    x = x0
    i = 0
    while x < x1:
        ww = rnd.uniform(*w) * escala
        hh = rnd.uniform(*h) * escala
        predio(c, x, y, ww, hh, estilo, seed=seed * 17 + i, depth=depth)
        x += ww + rnd.choice([0, 0, 10]) * escala
        i += 1


def igreja(c, x, y, s=1.0, depth=0.0, col=(0.62, 0.62, 0.66), porta_acesa=None):
    """fachada gótica com torre central (origem = centro da base)"""
    c.save(); c.translate(x, y); c.scale(s, s)
    base = P(col, depth)
    pg(c, [(-260, 0), (-260, -420), (0, -620), (260, -420), (260, 0)]); rgb(c, base); c.fill()
    pg(c, [(0, -620), (260, -420), (260, 0), (0, 0)]); rgb(c, dk(base, 0.08)); c.fill()
    c.rectangle(-70, -760, 140, 400); rgb(c, lt(base, 0.04)); c.fill()
    pg(c, [(-80, -760), (0, -980), (80, -760)]); rgb(c, dk(base, 0.15)); c.fill()
    c.rectangle(-3, -1040, 6, 70); rgb(c, P(OURO, depth)); c.fill(); c.rectangle(-22, -1020, 44, 6); c.fill()
    acesa = _L["noite"] if porta_acesa is None else porta_acesa
    janela_i(c, -24, -720, 48, 110, "gotica", acesa, None, depth)
    c.new_sub_path(); c.arc(0, -470, 56, 0, 6.283); rgb(c, dk(base, 0.25)); c.fill()
    c.new_sub_path(); c.arc(0, -470, 44, 0, 6.283); rgb(c, JANELA_ACESA if acesa else P(_L["fora"], depth)); c.fill()
    for i in range(8):
        a = i * math.pi / 4
        c.move_to(0, -470); c.line_to(math.cos(a) * 44, -470 + math.sin(a) * 44)
        rgb(c, dk(base, 0.25)); c.set_line_width(4); c.stroke()
    for sx in (-170, 130):
        janela_i(c, sx, -330, 40, 150, "gotica", acesa, None, depth)
    c.move_to(-70, 0); c.line_to(-70, -150); c.curve_to(-70, -210, -30, -240, 0, -260); c.curve_to(30, -240, 70, -210, 70, -150)
    c.line_to(70, 0); c.close_path(); rgb(c, dk(base, 0.3)); c.fill()
    c.move_to(-54, 0); c.line_to(-54, -146); c.curve_to(-54, -196, -24, -222, 0, -238); c.curve_to(24, -222, 54, -196, 54, -146)
    c.line_to(54, 0); c.close_path()
    if acesa:
        lgrad(c, 0, -238, 0, 0, [(0, (1.0, 0.80, 0.45), 1), (1, (0.98, 0.62, 0.30), 1)]); c.fill()
        rglow(c, 0, -60, 300, JANELA_ACESA, 0.25)
    else:
        rgb(c, P(MADEIRA_ESC, depth)); c.fill()
    c.restore()


def torre_castelo(c, x, y, w=160, h=420, depth=0.0, col=PEDRA):
    base = P(col, depth)
    c.rectangle(x - w / 2, y - h, w, h); rgb(c, base); c.fill()
    for k in range(4):
        c.rectangle(x - w / 2 + k * w / 3.5 - 4, y - h - 30, w / 7, 32); c.fill()
    c.rectangle(x + w / 2 - 26, y - h, 26, h); rgb(c, dk(base, 0.1)); c.fill()
    janela_i(c, x - 12, y - h * 0.7, 24, 60, "arco", None, None, depth)


def piramide(c, x, y, w=420, h=280, depth=0.3):
    base = P(AREIA, depth)
    pg(c, [(x - w / 2, y), (x, y - h), (x + w / 2, y)]); rgb(c, base); c.fill()
    side = -_L["dir"]
    pg(c, [(x, y - h), (x + side * w / 2, y), (x + side * w * 0.08, y)]); rgb(c, dk(base, 0.2)); c.fill()
    for k in range(1, 9):
        yy = y - h * k / 9
        hw = w / 2 * (1 - k / 9)
        c.move_to(x - hw, yy); c.line_to(x + hw, yy); rgb(c, dk(base, 0.08), 0.6); c.set_line_width(2); c.stroke()


def dunas(c, y=780, seed=1, depth=0.3, col=AREIA, amp=60):
    rnd = random.Random(seed)
    pts = []
    x = -100
    while x < W + 200:
        pts.append((x, y - rnd.uniform(0.2, 1.0) * amp))
        x += rnd.uniform(240, 420)
    base = P(col, depth)
    c.move_to(-100, H)
    for i, (px, py) in enumerate(pts):
        if i == 0:
            c.line_to(px, py)
        else:
            qx, qy = pts[i - 1]
            c.curve_to(qx + (px - qx) * 0.5, qy, qx + (px - qx) * 0.5, py, px, py)
    c.line_to(W + 200, H); c.close_path(); rgb(c, base); c.fill()
    for i in range(1, len(pts)):
        px, py = pts[i]
        pg(c, [(px, py), (px + 140 * -_L["dir"], py + 60), (px + 10, py + 80)]); rgb(c, dk(base, 0.10), 0.7); c.fill()


# ================================================================ água e navios
def mar_i(c, t, y=700, col=AGUA, reflexo=True):
    L = _L
    top = mix(P(col), L["ceu"][1], 0.35)
    lgrad(c, 0, y, 0, H, [(0, top, 1), (1, dk(P(col), 0.35), 1)])
    c.rectangle(-20, y, W + 40, H - y); c.fill()
    rnd = random.Random(5)
    for i in range(60):
        k = rnd.uniform(0, 1) ** 1.7
        yy = y + 6 + (H - y) * k
        x = (rnd.uniform(0, W) + math.sin(t * 0.6 + i) * 30)
        w_ = 20 + 90 * k
        rr(c, x, yy, w_, 3 + 3 * k, 2); rgb(c, lt(top, 0.25), 0.45); c.fill()
    if reflexo and L["astro"]:
        kind, ax, ay, acol = L["astro"]
        for i in range(14):
            yy = y + 10 + i * (H - y) / 14
            ww = 30 + i * 9 + math.sin(t * 2 + i) * 12
            rr(c, ax - ww / 2 + math.sin(t * 1.3 + i * 0.7) * 10, yy, ww, 4 + i * 0.3, 2)
            rgb(c, lt(acol, 0.1), 0.5 * (1 - i / 16)); c.fill()


def nau(c, t, s=1.0, vela=(0.92, 0.88, 0.78), casco=(0.38, 0.25, 0.16), cruz=True, depth=0.0, balanco=True):
    """veleiro antigo (galé/nau medieval ou do séc. XIX); origem = linha d'água no centro"""
    c.save(); c.scale(s, s)
    if balanco:
        c.rotate(math.sin(t * 0.8) * 0.02); c.translate(0, math.sin(t * 1.1) * 3)
    hc = P(casco, depth)
    c.move_to(-260, -70); c.line_to(250, -80); c.curve_to(230, -20, 180, 10, 120, 12); c.line_to(-180, 12)
    c.curve_to(-230, 0, -255, -40, -260, -70); c.close_path(); rgb(c, hc); c.fill()
    c.rectangle(-240, -70, 480, 12); rgb(c, dk(hc, 0.3)); c.fill()
    c.rectangle(-200, -40, 400, 8); rgb(c, lt(hc, 0.15)); c.fill()
    for mx, mh, sw in ((-90, 360, 170), (80, 400, 190)):
        c.rectangle(mx - 5, -70 - mh, 10, mh); rgb(c, P(MADEIRA_ESC, depth)); c.fill()
        for k, (yy, ww) in enumerate(((-70 - mh + 40, sw * 0.8), (-70 - mh * 0.55, sw))):
            hh = mh * 0.36
            c.move_to(mx - ww / 2, yy); c.line_to(mx + ww / 2, yy)
            c.curve_to(mx + ww / 2 + 10, yy + hh * 0.5, mx + ww / 2 + 6, yy + hh, mx + ww / 2, yy + hh)
            c.curve_to(mx, yy + hh + 18, mx, yy + hh + 18, mx - ww / 2, yy + hh)
            c.curve_to(mx - ww / 2 + 6, yy + hh * 0.5, mx - ww / 2 + 2, yy + hh * 0.3, mx - ww / 2, yy)
            c.close_path(); rgb(c, P(vela, depth)); c.fill()
            c.move_to(mx + ww * 0.1, yy); c.curve_to(mx + ww * 0.3, yy + hh * 0.5, mx + ww * 0.3, yy + hh * 0.7, mx + ww * 0.2, yy + hh + 10)
            c.line_to(mx + ww / 2, yy + hh); c.curve_to(mx + ww / 2 + 6, yy + hh * 0.5, mx + ww / 2 + 10, yy + hh * 0.3, mx + ww / 2, yy)
            c.close_path(); rgb(c, P(dk(vela, 0.10), depth)); c.fill()
            if cruz and k == 1:
                c.rectangle(mx - 8, yy + hh * 0.2, 16, hh * 0.6); rgb(c, P((0.70, 0.16, 0.14), depth)); c.fill()
                c.rectangle(mx - ww * 0.22, yy + hh * 0.42, ww * 0.44, 16); c.fill()
        wav = math.sin(t * 3 + mx) * 6
        pg(c, [(mx, -70 - mh), (mx + 50, -70 - mh + 10 + wav), (mx, -70 - mh + 22)]); rgb(c, P((0.75, 0.16, 0.14), depth)); c.fill()
    for a, b in (((-90, -430), (-250, -72)), ((80, -470), (248, -82)), ((-90, -430), (80, -470))):
        c.move_to(*a); c.line_to(*b); rgb(c, P(MADEIRA_ESC, depth), 0.8); c.set_line_width(2); c.stroke()
    c.restore()


def vapor(c, t, s=1.0, casco=(0.12, 0.12, 0.13), depth=0.0, fumaca=True):
    """navio a vapor (séc. XIX/XX); origem = linha d'água no centro"""
    c.save(); c.scale(s, s); c.translate(0, math.sin(t * 1.1) * 2)
    hc = P(casco, depth)
    c.move_to(-340, -90); c.line_to(360, -100); c.line_to(320, 6); c.line_to(-300, 6); c.close_path(); rgb(c, hc); c.fill()
    c.rectangle(-310, -8, 640, 14); rgb(c, P((0.62, 0.16, 0.14), depth)); c.fill()
    for i in range(16):
        c.new_sub_path(); c.arc(-260 + i * 36, -52, 5, 0, 6.283); rgb(c, P((0.85, 0.82, 0.7), depth)); c.fill()
    c.rectangle(-180, -160, 300, 70); rgb(c, P((0.92, 0.90, 0.84), depth)); c.fill()
    c.rectangle(-120, -200, 180, 40); c.fill()
    for i in range(10):
        c.rectangle(-170 + i * 29, -140, 16, 16); rgb(c, JANELA_ACESA if _L["noite"] else P((0.25, 0.3, 0.35), depth)); c.fill()
    c.rectangle(-20, -330, 56, 140); rgb(c, hc); c.fill()
    c.rectangle(-20, -300, 56, 22); rgb(c, P((0.62, 0.16, 0.14), depth)); c.fill()
    for mx in (-250, 250):
        c.rectangle(mx - 3, -400, 6, 310); rgb(c, hc); c.fill()
        c.move_to(mx, -400); c.line_to(-330 if mx < 0 else 350, -95); rgb(c, hc, 0.7); c.set_line_width(2); c.stroke()
    if fumaca:
        for i in range(6):
            k = ((t * 0.25 + i / 6) % 1)
            c.new_sub_path(); c.arc(8 - k * 220, -350 - k * 200, 22 + k * 50, 0, 6.283)
            rgb(c, P((0.35, 0.33, 0.32), depth), 0.55 * (1 - k)); c.fill()
    c.restore()


def cais(c, y=860, x0=-20, x1=None, depth=0.0):
    x1 = x1 if x1 is not None else W + 20
    c.rectangle(x0, y, x1 - x0, 40); rgb(c, P(MADEIRA, depth)); c.fill()
    c.rectangle(x0, y + 40, x1 - x0, 10); rgb(c, P(dk(MADEIRA, 0.4), depth)); c.fill()
    x = x0 + 40
    while x < x1:
        c.rectangle(x, y + 30, 22, 120); rgb(c, P(MADEIRA_ESC, depth)); c.fill()
        x += 180


# ================================================================ interiores
def interior(c, t, parede="pedra", piso="madeira", janela="gotica", jx=1380, piso_y=820, cor=None, raio=True):
    """sala: parede (pedra, reboco, madeira, tijolo), piso e uma janela com feixe de luz"""
    cols = dict(pedra=(0.66, 0.66, 0.68), reboco=(0.84, 0.76, 0.64), madeira=(0.48, 0.34, 0.22), tijolo=(0.66, 0.40, 0.30))
    base = P(cor or cols[parede])
    c.rectangle(0, 0, W, piso_y); rgb(c, base); c.fill()
    rnd = random.Random(4)
    if parede in ("pedra", "tijolo"):
        bh = 46 if parede == "pedra" else 26
        bw = 120 if parede == "pedra" else 64
        for r in range(int(piso_y / bh) + 1):
            off = (r % 2) * bw / 2
            for k in range(-1, int(W / bw) + 2):
                rr(c, k * bw - off + 3, r * bh + 3, bw - 6, bh - 6, 3)
                rgb(c, dk(base, rnd.uniform(0.02, 0.10))); c.fill()
    elif parede == "madeira":
        for k in range(0, W, 64):
            c.rectangle(k, 0, 3, piso_y); rgb(c, dk(base, 0.25)); c.fill()
    else:
        for i in range(8):
            ellipse(c, rnd.uniform(0, W), rnd.uniform(0, piso_y), rnd.uniform(80, 200), rnd.uniform(40, 90))
            rgb(c, dk(base, 0.05), 0.5); c.fill()
    c.rectangle(0, piso_y - 30, W, 30); rgb(c, dk(base, 0.25)); c.fill()
    pcol = P(dict(madeira=MADEIRA, pedra=(0.56, 0.54, 0.52), terra=TERRA).get(piso, MADEIRA))
    lgrad(c, 0, piso_y, 0, H, [(0, dk(pcol, 0.1), 1), (1, dk(pcol, 0.35), 1)])
    c.rectangle(0, piso_y, W, H - piso_y); c.fill()
    for i in range(-14, 15):
        c.move_to(W / 2 + i * 60, piso_y); c.line_to(W / 2 + i * 150, H)
        rgb(c, dk(pcol, 0.4), 0.5); c.set_line_width(2.5); c.stroke()
    if janela:
        jw, jh, jy = 170, 300, 170
        dia = not _L["noite"]
        c.save()
        janela_i(c, jx - jw / 2, jy, jw, jh, janela, False, None)
        c.restore()
        if dia:
            c.move_to(jx - jw / 2, jy + 60); c.line_to(jx + jw / 2, jy + 60); c.line_to(jx + jw / 2 - 420, H); c.line_to(jx - jw / 2 - 700, H)
            c.close_path()
            lgrad(c, jx, jy, jx - 500, H, [(0, (1, 0.98, 0.9), 0.30), (1, (1, 0.98, 0.9), 0.0)]); c.fill()
            if raio:
                rnd2 = random.Random(9)
                for i in range(26):
                    k = rnd2.uniform(0, 1)
                    px = jx - k * 500 + rnd2.uniform(-120, 120) + math.sin(t * 0.5 + i) * 20
                    py = jy + 80 + k * (H - jy - 100) + math.cos(t * 0.4 + i) * 20
                    c.new_sub_path(); c.arc(px, py, rnd2.uniform(1.2, 2.6), 0, 6.283); rgb(c, (1, 0.97, 0.85), 0.5); c.fill()
        else:
            rglow(c, jx, jy + jh / 2, 260, (0.5, 0.6, 0.9), 0.10)


def estante(c, x, y, w=520, h=560, seed=2, depth=0.0):
    """estante de livros; origem = canto inferior esquerdo"""
    rnd = random.Random(seed)
    mc = P(MADEIRA_ESC, depth)
    c.rectangle(x, y - h, w, h); rgb(c, dk(mc, 0.35)); c.fill()
    shelves = 4
    sh = h / shelves
    cores = [(0.55, 0.18, 0.16), (0.24, 0.36, 0.28), (0.26, 0.30, 0.46), (0.62, 0.46, 0.22), (0.45, 0.28, 0.38), (0.36, 0.24, 0.16)]
    for s_ in range(shelves):
        by = y - s_ * sh - 14
        bx = x + 14
        while bx < x + w - 40:
            bw = rnd.uniform(18, 34)
            bh = sh * rnd.uniform(0.55, 0.85)
            col = P(rnd.choice(cores), depth)
            if rnd.random() < 0.12:
                bx += bw; continue
            c.rectangle(bx, by - bh, bw - 2, bh); rgb(c, col); c.fill()
            c.rectangle(bx + 3, by - bh * 0.7, bw - 8, bh * 0.22); rgb(c, P((0.86, 0.80, 0.64), depth)); c.fill()
            bx += bw
        c.rectangle(x, by, w, 14); rgb(c, mc); c.fill()
    c.rectangle(x - 10, y - h - 16, w + 20, 18); rgb(c, mc); c.fill()
    c.rectangle(x - 10, y - h, 14, h); c.fill(); c.rectangle(x + w - 4, y - h, 14, h); c.fill()


def mesa_i(c, x, y, w=520, toalha=None, depth=0.0):
    """mesa; origem = centro do tampo (y = altura do tampo)"""
    mc = P(MADEIRA, depth)
    for lx in (-w / 2 + 30, w / 2 - 50):
        c.rectangle(x + lx, y, 20, 170); rgb(c, dk(mc, 0.25)); c.fill()
    c.rectangle(x - w / 2, y - 16, w, 22); rgb(c, mc); c.fill()
    if toalha:
        c.rectangle(x - w / 2 - 6, y - 18, w + 12, 90); rgb(c, P(toalha, depth)); c.fill()
        c.rectangle(x - w / 2 - 6, y + 64, w + 12, 8); rgb(c, P(dk(toalha, 0.2), depth)); c.fill()


def vela_i(c, t, x, y, s=1.0):
    """vela acesa com brilho; origem = base"""
    c.save(); c.translate(x, y); c.scale(s, s)
    rglow(c, 0, -110, 420, (1.0, 0.75, 0.40), 0.22)
    ellipse(c, 0, 0, 30, 8); rgb(c, P((0.55, 0.45, 0.3))); c.fill()
    c.rectangle(-9, -80, 18, 80); rgb(c, (0.95, 0.92, 0.82)); c.fill()
    c.rectangle(3, -80, 6, 80); rgb(c, (0.85, 0.80, 0.68)); c.fill()
    fl = 1 + 0.12 * math.sin(t * 13) * math.sin(t * 7.1)
    c.save(); c.translate(0, -84); c.scale(1, fl)
    c.move_to(0, 0); c.curve_to(-9, -8, -5, -26, 0, -36); c.curve_to(5, -26, 9, -8, 0, 0)
    rgb(c, (1.0, 0.82, 0.40)); c.fill()
    ellipse(c, 0, -8, 3, 7); rgb(c, (1, 0.97, 0.85)); c.fill()
    c.restore()
    rglow(c, 0, -100, 60, (1, 0.9, 0.6), 0.5)
    c.restore()


def livro_aberto(c, w=260, depth=0.0):
    pg(c, [(-w / 2, 0), (0, 8), (w / 2, 0), (w / 2 - 10, -40), (0, -34), (-w / 2 + 10, -40)])
    rgb(c, P((0.93, 0.89, 0.78), depth)); c.fill()
    for k in range(4):
        for sx in (-1, 1):
            c.move_to(sx * 20, -28 + k * 7); c.line_to(sx * (w / 2 - 22), -32 + k * 7)
            rgb(c, P((0.4, 0.3, 0.2), depth), 0.6); c.set_line_width(1.5); c.stroke()


def cruz_parede(c, s=1.0):
    c.save(); c.scale(s, s)
    c.rectangle(-8, -70, 16, 140); rgb(c, P(MADEIRA_ESC)); c.fill()
    c.rectangle(-42, -40, 84, 16); c.fill()
    c.restore()


# ================================================================ personagens
def lanterna_i(c, t=0, s=0.9, acesa=True):
    """lanterna a óleo chapada; origem = argola (na mão)"""
    c.save(); c.scale(s, s)
    if acesa:
        noite = _L["noite"]
        rglow(c, 0, 90, 460 if noite else 330, (1.0, 0.72, 0.36), 0.42 if noite else 0.30)
    metal = P((0.24, 0.20, 0.17))
    c.arc(0, 14, 16, math.pi, 2 * math.pi); rgb(c, metal); c.set_line_width(5); c.stroke()
    pg(c, [(-26, 34), (0, 14), (26, 34)]); rgb(c, metal); c.fill()
    c.rectangle(-28, 34, 56, 10); c.fill()
    c.rectangle(-22, 44, 44, 70)
    rgb(c, (1.0, 0.80, 0.45) if acesa else P((0.4, 0.42, 0.45))); c.fill()
    if acesa:
        fl = 1 + 0.15 * math.sin(t * 11) * math.sin(t * 6.3)
        c.save(); c.translate(0, 98); c.scale(1, fl)
        c.move_to(0, 0); c.curve_to(-8, -8, -4, -22, 0, -30); c.curve_to(4, -22, 8, -8, 0, 0)
        rgb(c, (1.0, 0.97, 0.80)); c.fill(); c.restore()
    for xx in (-22, 0, 20):
        c.rectangle(xx - 1, 44, 3, 70); rgb(c, metal); c.fill()
    c.rectangle(-28, 112, 56, 12); rgb(c, metal); c.fill()
    c.restore()


HIST = dict(pele="clara", cabelo="curto", cor_cabelo=(0.42, 0.34, 0.27), idade=0.25, chapeu="fedora",
            cor_chapeu=(0.36, 0.25, 0.17), roupa="casaco", cor_roupa=(0.58, 0.42, 0.27), cor_calca=(0.22, 0.20, 0.19),
            camisa=(0.92, 0.89, 0.80), gravata=(0.48, 0.14, 0.12), oculos=True, barba="curta", fid=0)


def _limb(c, o, tgt, l1, l2, bend, w1, w2, col):
    (ex, ey), (hx, hy) = engine._ik(o[0], o[1], tgt[0], tgt[1], l1, l2, bend)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.move_to(*o); c.line_to(ex, ey); rgb(c, col); c.set_line_width(w1); c.stroke()
    c.move_to(ex, ey); c.line_to(hx, hy); c.set_line_width(w2); c.stroke()
    c.new_sub_path(); c.arc(ex, ey, (w1 + w2) / 4, 0, 6.283); c.fill()
    return (ex, ey), (hx, hy)


def boneco(c, t, x, y, s=1.0, poses=((0, "stand"),), exprs=((0, "neutral"),), look=0.0,
           pele="clara", cabelo="curto", cor_cabelo=None, barba=None, bigode=False, idade=0.0,
           chapeu=None, cor_chapeu=None, roupa="camisa", cor_roupa=(0.30, 0.40, 0.55), cor_calca=(0.28, 0.24, 0.20),
           cor_sapato=(0.16, 0.11, 0.08), camisa=(0.92, 0.90, 0.84), gravata=None, oculos=False, cinto=None,
           capa=None, prop=None, fid=0, appear=None, alpha=1.0, andar=False, mulher=False, largura=1.0):
    """
    Personagem ilustrado (chapado, sem contorno), pés em (x, y), altura ~470 px em s=1.
    poses / exprs: as mesmas do boneco de giz (stand, point_r, think, shocked...).
    roupa: camisa | casaco (sobretudo até o joelho) | tunica (até o pé) | batina | vestido | jaqueta | armadura
    cabelo: curto | longo | calvo | careca | tonsura | coque | cacheado | None
    barba: cheia | curta | cavanhaque | longa | None    chapeu: fedora cartola quepe gorro capuz tiara palha
    turbante solideu touca explorador boina coroa elmo
    prop: ("r"|"l", fn(c, t)) desenha algo preso à mão (origem = mão).
    """
    a_scale = 1.0
    if appear is not None:
        if t < appear:
            return
        a_scale = ease_out_back(prog(t, appear, 0.45))
        if a_scale < 0.02:
            return
    Pz = engine.pose_at(t, list(poses))
    expr = engine.val_at(t, list(exprs))
    if callable(look):
        look = look(t)
    skin = P(PELES.get(pele, pele) if isinstance(pele, str) else pele)
    hcol = cor_cabelo if cor_cabelo is not None else CABELOS["castanho"]
    if isinstance(hcol, str):
        hcol = CABELOS[hcol]
    hcol = P(mix(hcol, CABELOS["grisalho"], idade))
    roupa_c = P(cor_roupa)
    calca = P(cor_calca)
    shade = lambda col, k=0.16: dk(col, k)
    ld = _L["dir"]  # luz vem deste lado; sombra no oposto

    c.save()
    c.translate(x, y)
    c.scale(s * a_scale, s * a_scale)
    if alpha < 1:
        c.push_group()
    bob = math.sin(t * 2.0 + fid) * 1.8
    # sombra no chão
    ellipse(c, -ld * 14, 2, 78, 11); rgb(c, (0, 0, 0), 0.20); c.fill()

    hipy = -190
    shy = -326 + bob
    rf, lf = Pz["rf"], Pz["lf"]
    running = Pz.get("run")
    if andar or running:
        sp = 11 if running else 6.5
        ph = t * sp + fid * 1.3
        amp = 60 if running else 34
        rf = (16 + amp * math.sin(ph), 186 - 22 * max(0, math.cos(ph)))
        lf = (-16 - amp * math.sin(ph), 186 - 22 * max(0, -math.cos(ph)))
        hipy -= abs(math.sin(ph)) * 5
        shy -= abs(math.sin(ph)) * 5
    longa = roupa in ("tunica", "batina", "vestido")
    # pernas
    feet = []
    for side, tgt, bend in ((-1, lf, 1), (1, rf, -1)):
        o = (side * 20, hipy)
        (kx, ky), (fx_, fy_) = engine._ik(o[0], o[1], tgt[0], hipy + tgt[1] + 4, 96, 94, bend)
        col = calca if side == ld else shade(calca, 0.12)
        if not longa:
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            c.move_to(*o); c.line_to(kx, ky); c.line_to(fx_, fy_); rgb(c, col); c.set_line_width(36); c.stroke()
        feet.append((side, fx_, fy_))
    for side, fx_, fy_ in feet:
        c.save(); c.translate(fx_ + side * 10, fy_ - 4)
        c.move_to(-22, 6); c.curve_to(-22, -14, 22, -14, 26 * (1 if side > 0 else 1), 2); c.line_to(26, 8); c.line_to(-22, 8); c.close_path()
        c.restore()
        rgb(c, P(cor_sapato)); c.fill()
    # capa (atrás do corpo)
    if capa:
        pg(c, [(-50, shy - 4), (50, shy - 4), (86, -20), (-86, -20)]); rgb(c, shade(P(capa), 0.2)); c.fill()
    # tronco
    sw = 48 * largura
    if roupa == "casaco":
        hem, hw = -96, 66
    elif longa:
        hem, hw = -14, 74 if roupa != "vestido" else 84
    elif roupa == "armadura":
        hem, hw = hipy + 30, 54
    else:
        hem, hw = hipy + 24, 52
    hw *= largura

    def tronco_path():
        c.move_to(-sw, shy + 16)
        c.curve_to(-sw, shy - 6, -sw + 16, shy - 10, -20, shy - 10)
        c.line_to(20, shy - 10)
        c.curve_to(sw - 16, shy - 10, sw, shy - 6, sw, shy + 16)
        c.line_to(hw, hem); c.curve_to(hw * 0.4, hem + 6, -hw * 0.4, hem + 6, -hw, hem)
        c.close_path()
    if not longa and roupa != "casaco":
        # calça até a cintura
        c.rectangle(-46, hipy - 12, 92, 30); rgb(c, calca); c.fill()
    tronco_path(); rgb(c, roupa_c); c.fill()
    c.save(); tronco_path(); c.clip()
    if ld < 0:
        c.rectangle(16, shy - 20, 200, 600)
    else:
        c.rectangle(-216, shy - 20, 200, 600)
    rgb(c, (0, 0, 0), 0.13); c.fill()
    if roupa == "casaco":
        # camisa + gravata no V
        pg(c, [(-20, shy - 10), (20, shy - 10), (0, shy + 70)]); rgb(c, P(camisa)); c.fill()
        if gravata:
            pg(c, [(-6, shy - 4), (6, shy - 4), (8, shy + 50), (0, shy + 64), (-8, shy + 50)]); rgb(c, P(gravata)); c.fill()
        pg(c, [(-22, shy - 10), (-4, shy + 74), (-24, shy + 40), (-36, shy + 4)]); rgb(c, shade(roupa_c, 0.12)); c.fill()
        pg(c, [(22, shy - 10), (4, shy + 74), (24, shy + 40), (36, shy + 4)]); c.fill()
        c.move_to(0, shy + 74); c.line_to(4, hem); rgb(c, shade(roupa_c, 0.3)); c.set_line_width(3); c.stroke()
        c.rectangle(-80, -226, 160, 16); rgb(c, shade(roupa_c, 0.22)); c.fill()
        rr(c, -12, -230, 24, 24, 4); rgb(c, P((0.70, 0.58, 0.32))); c.fill()
        for by in (shy + 100, shy + 160):
            c.new_sub_path(); c.arc(-14, by, 4.5, 0, 6.283); rgb(c, shade(roupa_c, 0.45)); c.fill()
    elif roupa in ("tunica", "batina", "vestido"):
        if roupa == "batina":
            c.rectangle(-10, shy - 10, 20, 12); rgb(c, (0.95, 0.95, 0.92)); c.fill()
            for k in range(9):
                c.new_sub_path(); c.arc(0, shy + 14 + k * 30, 3.5, 0, 6.283); rgb(c, shade(roupa_c, 0.4)); c.fill()
        else:
            c.new_sub_path(); c.arc(0, shy - 8, 20, 0, math.pi); rgb(c, shade(roupa_c, 0.25)); c.fill()
            c.rectangle(-80, -214, 160, 12); rgb(c, P(cinto or (0.55, 0.42, 0.26))); c.fill()
            if roupa == "vestido":
                rr(c, -44, -200, 88, 170, 10); rgb(c, P((0.90, 0.87, 0.78))); c.fill()
    elif roupa == "jaqueta":
        c.rectangle(-4, shy, 8, hem - shy); rgb(c, shade(roupa_c, 0.3)); c.fill()
        for k in range(5):
            c.new_sub_path(); c.arc(-14, shy + 24 + k * 30, 4, 0, 6.283); c.new_sub_path(); c.arc(14, shy + 24 + k * 30, 4, 0, 6.283)
            rgb(c, P(OURO)); c.fill()
        pg(c, [(-20, shy - 10), (0, shy + 20), (20, shy - 10)]); rgb(c, P(camisa)); c.fill()
    elif roupa == "armadura":
        for k in range(4):
            c.rectangle(-60, shy + 20 + k * 30, 120, 3); rgb(c, lt(roupa_c, 0.3)); c.fill()
    else:  # camisa
        pg(c, [(-18, shy - 10), (0, shy + 14), (18, shy - 10)]); rgb(c, shade(roupa_c, 0.2)); c.fill()
        c.rectangle(-2, shy + 10, 4, hem - shy - 14); rgb(c, shade(roupa_c, 0.18)); c.fill()
        c.rectangle(-60, hem - 10, 120, 10); rgb(c, P(cinto or (0.30, 0.20, 0.13))); c.fill()
    c.restore()
    # pescoço
    rr(c, -13, shy - 30, 26, 26, 6); rgb(c, dk(skin, 0.12)); c.fill()
    # braços
    for side, key, bk, fk in ((-1, "lh", "lb", "lf_"), (1, "rh", "rb", "rf_")):
        o = (side * (sw - 10), shy + 10)
        tgt = (Pz[key][0], shy + Pz[key][1])
        if andar and Pz[key][1] > 100:
            tgt = (tgt[0] + math.sin(t * 6.5 + fid * 1.3 + (math.pi if side > 0 else 0)) * 26, tgt[1])
        col = roupa_c if side == ld else shade(roupa_c, 0.12)
        (ex, ey), (hx, hy) = _limb(c, o, tgt, 74, 70, Pz.get(bk, -side), 32, 27, col)
        a = math.atan2(hy - ey, hx - ex)
        cx_, cy_ = hx - math.cos(a) * 6, hy - math.sin(a) * 6
        c.move_to(ex + (cx_ - ex) * 0.85, ey + (cy_ - ey) * 0.85); c.line_to(cx_, cy_)
        rgb(c, shade(col, 0.25)); c.set_line_width(29); c.stroke()  # punho
        c.new_sub_path(); c.arc(hx, hy, 13.5, 0, 6.283); rgb(c, skin); c.fill()
        fing = Pz.get(fk)
        if fing == "point":
            c.move_to(hx, hy); c.line_to(hx + 24 * math.cos(a), hy + 24 * math.sin(a)); rgb(c, skin); c.set_line_width(8); c.stroke()
        elif fing == "thumb":
            c.move_to(hx, hy); c.line_to(hx, hy - 24); rgb(c, skin); c.set_line_width(9); c.stroke()
        elif fing == "point_up":
            c.move_to(hx, hy); c.line_to(hx, hy - 26); rgb(c, skin); c.set_line_width(8); c.stroke()
        if prop and prop[0] == ("l" if side < 0 else "r"):
            c.save(); c.translate(hx, hy); prop[1](c, t); c.restore()
    # cabeça
    _cabeca(c, t, expr, look, fid, skin, hcol, cabelo, barba, bigode, chapeu, cor_chapeu, oculos, shy, ld,
            roupa_c, mulher)
    if alpha < 1:
        c.pop_group_to_source(); c.paint_with_alpha(alpha)
    c.restore()


def _cabeca(c, t, expr, look, fid, skin, hcol, cabelo, barba, bigode, chapeu, cor_chapeu, oculos, shy, ld, roupa_c, mulher):
    hy = shy - 82
    c.save()
    c.translate(look * 5, hy)
    c.rotate(math.sin(t * 0.8 + fid) * 0.025 + look * 0.03)
    fx = look * 9
    sg = 1 if look >= 0 else -1
    ink = (0.16, 0.11, 0.09)
    chap = P(cor_chapeu) if cor_chapeu else None
    # capuz/cabelo de trás
    if chapeu == "capuz":
        ellipse(c, 0, 8, 70, 82); rgb(c, dk(roupa_c, 0.18)); c.fill()
    if cabelo in ("longo",) or (mulher and cabelo not in ("coque", None, "careca")):
        c.move_to(-52, -10); c.curve_to(-62, 40, -60, 80, -40, 96); c.line_to(40, 96); c.curve_to(60, 80, 62, 40, 52, -10); c.close_path()
        rgb(c, dk(hcol, 0.12)); c.fill()
    # orelhas
    for sx in (-1, 1):
        ellipse(c, sx * 46 + fx * 0.3, 6, 9, 14); rgb(c, dk(skin, 0.10)); c.fill()
    # rosto
    ellipse(c, 0, 0, 47, 57); rgb(c, skin); c.fill()
    c.save(); ellipse(c, 0, 0, 47, 57); c.clip()
    ellipse(c, -ld * 52, 6, 34, 70); rgb(c, (0, 0, 0), 0.08); c.fill()
    c.restore()
    # bochechas
    for sx in (-1, 1):
        c.new_sub_path(); c.arc(sx * 25 + fx, 20, 9, 0, 6.283); rgb(c, (0.85, 0.35, 0.30), 0.16); c.fill()
    # barba (antes da boca)
    if barba in ("cheia", "longa"):
        L_ = 78 if barba == "longa" else 64
        c.move_to(-47, 2); c.curve_to(-46, 40, -28, L_, fx * 0.5, L_ + 4); c.curve_to(28, L_, 46, 40, 47, 2)
        c.curve_to(36, 18, 28, 22, 18 + fx, 20); c.curve_to(10, 34, -10, 34, -18 + fx, 20); c.curve_to(-28, 22, -36, 18, -47, 2)
        c.close_path(); rgb(c, hcol); c.fill()
    elif barba == "curta":
        c.move_to(-46, 4); c.curve_to(-44, 40, -26, 58, fx * 0.5, 60); c.curve_to(26, 58, 44, 40, 46, 4)
        c.curve_to(30, 30, -30, 30, -46, 4); c.close_path(); rgb(c, hcol, 0.45); c.fill()
    elif barba == "cavanhaque":
        ellipse(c, fx * 0.6, 48, 16, 12); rgb(c, hcol); c.fill()
    # olhos
    blink = ((t * 1000 + fid * 1777) % 4300) < 120
    ey_ = -2
    big = expr in ("shocked", "desperate")
    for sx in (-1, 1):
        ex = sx * 17 + fx
        if blink:
            c.move_to(ex - 6, ey_); c.line_to(ex + 6, ey_); rgb(c, ink); c.set_line_width(3); c.stroke()
        elif big:
            c.new_sub_path(); c.arc(ex, ey_, 9, 0, 6.283); rgb(c, (0.98, 0.97, 0.94)); c.fill()
            c.new_sub_path(); c.arc(ex + look * 2, ey_, 4.5, 0, 6.283); rgb(c, ink); c.fill()
        else:
            ellipse(c, ex + look * 1.5, ey_, 4.6, 6.2); rgb(c, ink); c.fill()
            c.new_sub_path(); c.arc(ex + look * 1.5 + 1.5, ey_ - 2, 1.4, 0, 6.283); rgb(c, (1, 1, 1), 0.8); c.fill()
    # sobrancelhas
    by = -20 if not big else -27
    ang = dict(worried=0.32, sad=0.32, desperate=0.35, angry=-0.38, shocked=0.0, think=0.18, confident=-0.08)
    a = ang.get(expr, 0.0)
    bc = dk(hcol, 0.2) if cabelo not in ("careca",) else dk(skin, 0.45)
    for sx in (-1, 1):
        aa = a if sx < 0 else -a
        if expr == "think" and sx > 0:
            aa, yy = -0.2, by - 6
        else:
            yy = by
        cx_ = sx * 18 + fx
        c.move_to(cx_ - 9 * math.cos(aa), yy + sx * 9 * math.sin(aa) * -1)
        c.line_to(cx_ + 9 * math.cos(aa), yy - sx * 9 * math.sin(aa) * -1)
        rgb(c, bc); c.set_line_width(5); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke()
    # nariz
    nx = fx * 1.4
    c.move_to(nx - 2, 0); c.curve_to(nx + sg * 4, 10, nx + sg * 9, 16, nx + sg * 4, 19); c.curve_to(nx, 21, nx - 4, 19, nx - 4, 16)
    c.close_path(); rgb(c, dk(skin, 0.16)); c.fill()
    # bigode
    if bigode or barba in ("cheia", "longa"):
        c.move_to(fx, 24); c.curve_to(fx - 10, 18, fx - 24, 22, fx - 26, 32); c.curve_to(fx - 14, 28, fx - 6, 30, fx, 28)
        c.curve_to(fx + 6, 30, fx + 14, 28, fx + 26, 32); c.curve_to(fx + 24, 22, fx + 10, 18, fx, 24); c.close_path()
        rgb(c, dk(hcol, 0.1)); c.fill()
    # boca
    mx, my = fx * 1.1, 34
    mc_ = (0.45, 0.20, 0.18)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    if expr in ("happy", "confident"):
        c.move_to(mx - 10, my - 2); c.curve_to(mx - 4, my + 6, mx + 4, my + 6, mx + 10, my - 2 - (4 if expr == "confident" else 0))
        rgb(c, mc_); c.set_line_width(4); c.stroke()
    elif expr == "grin":
        c.move_to(mx - 13, my - 3); c.curve_to(mx - 8, my + 12, mx + 8, my + 12, mx + 13, my - 3); c.close_path()
        rgb(c, (0.35, 0.12, 0.12)); c.fill()
        c.rectangle(mx - 10, my - 3, 20, 4); rgb(c, (0.98, 0.97, 0.94)); c.fill()
    elif expr in ("shocked", "desperate"):
        ellipse(c, mx, my + 2, 7 if expr == "shocked" else 10, 9 if expr == "shocked" else 12); rgb(c, (0.30, 0.10, 0.10)); c.fill()
    elif expr in ("sad", "worried"):
        c.move_to(mx - 9, my + 4); c.curve_to(mx - 4, my - 2, mx + 4, my - 2, mx + 9, my + 4)
        rgb(c, mc_); c.set_line_width(4); c.stroke()
    elif expr == "angry":
        c.move_to(mx - 10, my + 3); c.line_to(mx - 4, my); c.line_to(mx + 4, my); c.line_to(mx + 10, my + 3)
        rgb(c, mc_); c.set_line_width(4); c.stroke()
    elif expr == "think":
        c.move_to(mx - 2, my + 1); c.line_to(mx + 10, my - 2); rgb(c, mc_); c.set_line_width(4); c.stroke()
    else:
        c.move_to(mx - 8, my); c.line_to(mx + 8, my); rgb(c, mc_); c.set_line_width(4); c.stroke()
    # óculos
    if oculos:
        gc = (0.30, 0.22, 0.14)
        for sx in (-1, 1):
            ex = sx * 17 + fx
            c.new_sub_path(); c.arc(ex, -2, 13, 0, 6.283); rgb(c, (1, 1, 1), 0.12); c.fill_preserve()
            rgb(c, gc); c.set_line_width(3.2); c.stroke()
        c.move_to(-4 + fx, -4); c.curve_to(-2 + fx, -8, 2 + fx, -8, 4 + fx, -4); c.stroke()
        for sx in (-1, 1):
            c.move_to(sx * 30 + fx, -4); c.line_to(sx * 46 + fx * 0.3, -6); c.stroke()
    # cabelo (frente)
    if cabelo in ("curto", "longo", "cacheado", "coque") or (cabelo and mulher):
        c.move_to(-49, 8); c.curve_to(-54, -40, -30, -64, 0, -63); c.curve_to(32, -64, 54, -40, 49, 8)
        c.curve_to(46, -10, 42, -20, 34, -28)
        c.curve_to(14, -20, -10 + fx, -34, -20 + fx, -40) if sg > 0 else c.curve_to(10 + fx, -34, -14, -20, -34, -28)
        c.curve_to(-30, -30, -42, -20, -49, 8) if sg > 0 else c.curve_to(-42, -20, -46, -10, -49, 8)
        c.close_path(); rgb(c, hcol); c.fill()
        if cabelo == "cacheado":
            for k in range(9):
                a_ = math.pi + k * math.pi / 8
                c.new_sub_path(); c.arc(math.cos(a_) * 46, -10 + math.sin(a_) * 54, 12, 0, 6.283)
            rgb(c, hcol); c.fill()
        if cabelo == "coque":
            c.new_sub_path(); c.arc(0, -70, 20, 0, 6.283); rgb(c, hcol); c.fill()
    elif cabelo in ("calvo", "tonsura"):
        for sx in (-1, 1):
            c.move_to(sx * 49, 8); c.curve_to(sx * 52, -20, sx * 44, -40, sx * 30, -46); c.line_to(sx * 40, -10); c.close_path()
            rgb(c, hcol); c.fill()
        if cabelo == "tonsura":
            c.move_to(-46, -24); c.curve_to(-30, -40, 30, -40, 46, -24); c.curve_to(30, -32, -30, -32, -46, -24)
            rgb(c, hcol); c.fill()
    # chapéus
    if chapeu:
        _chapeu(c, t, chapeu, chap, roupa_c, hcol)
    c.restore()


def _chapeu(c, t, kind, col, roupa_c, hcol):
    col = col or P((0.30, 0.22, 0.16))
    if kind in ("fedora", "explorador", "palha"):
        if kind == "palha":
            col = P((0.86, 0.74, 0.46)) if col is None else col
        bw = {"fedora": 82, "explorador": 78, "palha": 104}[kind]
        ellipse(c, 0, -40, bw, 14); rgb(c, dk(col, 0.12)); c.fill()
        if kind == "explorador":
            c.move_to(-50, -40); c.curve_to(-50, -96, 50, -96, 50, -40); c.close_path()
        else:
            c.move_to(-44, -40); c.curve_to(-46, -70, -40, -94, -20, -94); c.curve_to(-8, -94, -6, -86, 0, -86)
            c.curve_to(6, -86, 8, -94, 20, -94); c.curve_to(40, -94, 46, -70, 44, -40); c.close_path()
        rgb(c, col); c.fill()
        c.rectangle(-46, -56, 92, 14); rgb(c, dk(col, 0.45) if kind != "palha" else P((0.55, 0.20, 0.16))); c.fill()
        c.move_to(-bw, -40); c.curve_to(-bw + 10, -26, bw - 10, -26, bw, -40); c.curve_to(bw - 20, -34, -bw + 20, -34, -bw, -40)
        rgb(c, col); c.fill()
    elif kind == "cartola":
        ellipse(c, 0, -44, 66, 11); rgb(c, col); c.fill()
        c.rectangle(-38, -150, 76, 106); c.fill()
        c.rectangle(-38, -66, 76, 14); rgb(c, lt(col, 0.15)); c.fill()
    elif kind == "quepe":
        c.move_to(-50, -30); c.curve_to(-54, -70, 54, -70, 50, -30); c.close_path(); rgb(c, col); c.fill()
        ellipse(c, 0, -74, 58, 14); rgb(c, lt(col, 0.05)); c.fill()
        c.rectangle(-50, -44, 100, 12); rgb(c, dk(col, 0.4)); c.fill()
        c.move_to(-46, -32); c.curve_to(-20, -18, 30, -18, 52, -30); c.line_to(48, -36); c.close_path(); rgb(c, (0.1, 0.1, 0.1)); c.fill()
        c.new_sub_path(); c.arc(0, -50, 8, 0, 6.283); rgb(c, P(OURO)); c.fill()
    elif kind == "gorro":
        c.move_to(-50, -18); c.curve_to(-58, -70, -20, -96, 10, -90); c.curve_to(48, -84, 58, -50, 50, -18); c.close_path()
        rgb(c, col); c.fill()
        rr(c, -54, -34, 108, 22, 10); rgb(c, dk(col, 0.15)); c.fill()
    elif kind == "boina":
        ellipse(c, 6, -50, 60, 22); rgb(c, col); c.fill()
    elif kind == "solideu":
        c.move_to(-34, -44); c.curve_to(-30, -66, 30, -66, 34, -44); c.close_path(); rgb(c, col); c.fill()
    elif kind == "capuz":
        c.move_to(-62, 40); c.curve_to(-70, -70, 70, -70, 62, 40); c.curve_to(54, -20, 30, -52, 0, -52)
        c.curve_to(-30, -52, -54, -20, -62, 40); c.close_path(); rgb(c, roupa_c); c.fill()
    elif kind == "touca":
        c.move_to(-60, 60); c.curve_to(-68, -76, 68, -76, 60, 60); c.curve_to(52, -10, 40, -50, 0, -52)
        c.curve_to(-40, -50, -52, -10, -60, 60); c.close_path(); rgb(c, P((0.95, 0.94, 0.90))); c.fill()
    elif kind == "tiara":
        c.move_to(-40, -40); c.curve_to(-46, -120, -20, -150, 0, -150); c.curve_to(20, -150, 46, -120, 40, -40); c.close_path()
        rgb(c, P((0.96, 0.94, 0.88))); c.fill()
        for yy in (-50, -84, -114):
            c.rectangle(-46, yy, 92, 10); rgb(c, P(OURO)); c.fill()
        c.new_sub_path(); c.arc(0, -156, 8, 0, 6.283); c.fill()
    elif kind == "turbante":
        ellipse(c, 0, -52, 58, 32); rgb(c, col); c.fill()
        for k in range(3):
            c.move_to(-54, -40 - k * 14); c.curve_to(-20, -60 - k * 14, 20, -36 - k * 14, 54, -54 - k * 10)
            rgb(c, dk(col, 0.15)); c.set_line_width(3); c.stroke()
    elif kind == "coroa":
        pg(c, [(-40, -40), (-44, -90), (-22, -66), (0, -96), (22, -66), (44, -90), (40, -40)]); rgb(c, P(OURO)); c.fill()
    elif kind == "elmo":
        c.move_to(-52, 10); c.curve_to(-56, -70, 56, -70, 52, 10); c.line_to(40, 10); c.line_to(40, -14); c.line_to(-40, -14)
        c.line_to(-40, 10); c.close_path(); rgb(c, P((0.62, 0.64, 0.68))); c.fill()
        c.rectangle(-4, -14, 8, 40); c.fill()


def historiador_i(c, t, x, y, s=1.0, poses=((0, "stand"),), exprs=((0, "neutral"),), lanterna=True, **kw):
    """O Historiador no estilo ilustrado: fedora, sobretudo, óculos redondos, barba curta e lanterna."""
    o = dict(HIST)
    o.update(kw)
    if lanterna and "prop" not in kw:
        o["prop"] = ("l", lambda c, tt: lanterna_i(c, tt, 0.62) if engine.pose_at(tt, list(poses))["lh"][1] > 40 else None)
    boneco(c, t, x, y, s, poses=poses, exprs=exprs, **o)


# figurinos prontos (passe com **)
FIGURINO = dict(
    campones=dict(roupa="tunica", cor_roupa=(0.42, 0.50, 0.40), cabelo="curto", barba="cheia", chapeu="gorro", cor_chapeu=(0.55, 0.20, 0.16)),
    camponesa=dict(roupa="vestido", cor_roupa=(0.55, 0.30, 0.26), cabelo="longo", mulher=True, chapeu="touca"),
    monge=dict(roupa="tunica", cor_roupa=(0.34, 0.25, 0.18), cabelo="tonsura", cinto=(0.80, 0.72, 0.52)),
    padre=dict(roupa="batina", cor_roupa=(0.12, 0.12, 0.14), cabelo="calvo", idade=0.5),
    papa=dict(roupa="tunica", cor_roupa=(0.82, 0.24, 0.20), chapeu="tiara", cabelo="calvo", idade=0.7, capa=(0.86, 0.68, 0.28)),
    nobre=dict(roupa="tunica", cor_roupa=(0.30, 0.20, 0.42), capa=(0.62, 0.14, 0.14), chapeu="coroa", barba="cheia"),
    marinheiro=dict(roupa="camisa", cor_roupa=(0.86, 0.84, 0.78), cor_calca=(0.22, 0.28, 0.42), chapeu="gorro", cor_chapeu=(0.24, 0.30, 0.46), barba="curta"),
    capitao=dict(roupa="jaqueta", cor_roupa=(0.14, 0.18, 0.30), cor_calca=(0.14, 0.18, 0.30), chapeu="quepe", cor_chapeu=(0.14, 0.18, 0.30), barba="cheia"),
    cavalheiro=dict(roupa="casaco", cor_roupa=(0.16, 0.16, 0.18), chapeu="cartola", cor_chapeu=(0.12, 0.12, 0.13), bigode=True, gravata=(0.15, 0.15, 0.15)),
    dama=dict(roupa="vestido", cor_roupa=(0.30, 0.36, 0.54), cabelo="coque", mulher=True),
    explorador=dict(roupa="camisa", cor_roupa=(0.76, 0.68, 0.50), cor_calca=(0.50, 0.42, 0.30), chapeu="explorador", cor_chapeu=(0.82, 0.76, 0.60), bigode=True),
    medico=dict(roupa="casaco", cor_roupa=(0.95, 0.94, 0.90), cabelo="curto", bigode=True, gravata=(0.15, 0.15, 0.2)),
    soldado=dict(roupa="armadura", cor_roupa=(0.58, 0.60, 0.64), chapeu="elmo", barba="curta"),
    escriba=dict(roupa="tunica", cor_roupa=(0.86, 0.82, 0.70), chapeu="turbante", cor_chapeu=(0.92, 0.90, 0.84), pele="morena", barba="longa"),
)


def figurantes(c, t, y=900, n=8, s=0.32, seed=1, x0=200, x1=1700, andando=True, figurinos=None, depth=0.0):
    """gente pequena no fundo andando (ou parada)"""
    rnd = random.Random(seed)
    figs = figurinos or ["campones", "camponesa", "monge", "marinheiro"]
    for i in range(n):
        fig = dict(FIGURINO[rnd.choice(figs)])
        fig["pele"] = rnd.choice(list(PELES))
        fig["cor_cabelo"] = rnd.choice(list(CABELOS)[:4])
        vel = rnd.uniform(30, 60) * rnd.choice([-1, 1]) if andando else 0
        x = x0 + ((rnd.uniform(0, 1) * (x1 - x0) + t * vel) % (x1 - x0))
        boneco(c, t, x, y + rnd.uniform(-10, 10), s * rnd.uniform(0.9, 1.08), look=0.8 if vel > 0 else -0.8,
               andar=andando, fid=10 + i, **fig)


# ================================================================ textos do estilo
def _bold(c, font):
    c.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)


def rotulo(c, t, t0, titulo, sub=None, x=150, y=950, size=54, d=0.5):
    """legenda de canto (como "1903 · OSWALDO CRUZ"): título forte + linha âmbar + subtítulo"""
    if t < t0:
        return
    p = ease_out(prog(t, t0, d))
    c.save(); c.translate(x - 30 * (1 - p), y)
    _bold(c, SERIF); c.set_font_size(size)
    w = c.text_extents(titulo).x_advance
    for dx, dy, col, a in ((3, 4, (0, 0, 0), 0.55), (0, 0, (0.98, 0.96, 0.90), 1)):
        c.move_to(dx, dy); rgb(c, col, a * p); c.show_text(titulo)
    c.rectangle(0, 18, w * p, 4); rgb(c, AMBER, p); c.fill()
    if sub:
        c.select_font_face(TYPE); c.set_font_size(size * 0.48)
        for dx, dy, col, a in ((2, 3, (0, 0, 0), 0.6), (0, 0, (0.95, 0.92, 0.84), 1)):
            c.move_to(dx, 56 + dy); rgb(c, col, a * p); c.show_text(sub)
    c.restore()


def placa(c, titulo, sub=None, w=None, size=40):
    """cartão de pergaminho com título e sobretítulo (centrado na origem)"""
    _bold(c, SERIF); c.set_font_size(size)
    tw = c.text_extents(titulo).x_advance
    w = w or tw + 80
    h = size * 2.4 + (size * 0.8 if sub else 0)
    c.save(); c.rotate(-0.012)
    rr(c, -w / 2 + 6, -h / 2 + 8, w, h, 6); rgb(c, (0, 0, 0), 0.35); c.fill()
    rr(c, -w / 2, -h / 2, w, h, 6); rgb(c, (0.93, 0.88, 0.76)); c.fill()
    rr(c, -w / 2 + 10, -h / 2 + 10, w - 20, h - 20, 4); rgb(c, (0.55, 0.40, 0.22), 0.6); c.set_line_width(2); c.stroke()
    yy = -h / 2 + size * 1.25
    if sub:
        c.select_font_face(TYPE); c.set_font_size(size * 0.5)
        sw_ = c.text_extents(sub).x_advance
        c.move_to(-sw_ / 2, yy - size * 0.2); rgb(c, (0.55, 0.40, 0.22)); c.show_text(sub)
        yy += size * 0.9
    _bold(c, SERIF); c.set_font_size(size)
    c.move_to(-tw / 2, yy + size * 0.2); rgb(c, (0.20, 0.13, 0.08)); c.show_text(titulo)
    c.restore()


def titulo_i(c, s, x=960, y=200, size=96, col=(0.98, 0.95, 0.88), sombra=0.6):
    """título grande com sombra (legível sobre céu claro)"""
    _bold(c, SERIF); c.set_font_size(size)
    w = c.text_extents(s).x_advance
    for k in range(6, 0, -1):
        c.move_to(x - w / 2 + k * 0.8, y + k); rgb(c, (0, 0, 0), sombra / 6); c.show_text(s)
    c.move_to(x - w / 2, y); rgb(c, col); c.show_text(s)


# ================================================================ cenários prontos
def cena_vila(c, t, hora="tarde", estilo="medieval", seed=1, chao_y=880, igreja_x=None, passaros=True):
    """rua de vila/cidade: céu, montanhas, casario de fundo, casario da frente e calçamento"""
    luz(hora)
    ceu(c, t, passaros=passaros and not _L["noite"], seed=seed)
    montanhas(c, 560, 260, seed=seed, depth=0.8, neve=True)
    colinas(c, 650, 40, seed=seed, col=GRAMA, depth=0.55)
    casario(c, t, 690, estilo, seed=seed + 5, depth=0.45, escala=0.55)
    if igreja_x is not None:
        igreja(c, igreja_x, 700, 0.55, depth=0.35)
    casario(c, t, chao_y, estilo, seed=seed + 1, depth=0.0, h=(300, 430))
    chao(c, t, chao_y, "pedra", seed=seed)


def cena_porto(c, t, hora="dia", seed=2):
    luz(hora)
    ceu(c, t, passaros=True, seed=seed)
    montanhas(c, 520, 200, seed=seed, depth=0.85, col=(0.45, 0.52, 0.50))
    mar_i(c, t, 520)
    casario(c, t, 600, "pedra", seed=seed + 3, depth=0.5, escala=0.42, x0=-60, x1=700)
    igreja(c, 330, 600, 0.32, depth=0.5)
    for i, (xx, yy, ss) in enumerate(((900, 640, 0.42), (1250, 610, 0.32), (1560, 660, 0.48))):
        c.save(); c.translate(xx, yy); nau(c, t + i * 2, ss, depth=0.25); c.restore()
    cais(c, 860)
    chao(c, t, 900, "pedra", seed=seed)


def cena_floresta(c, t, hora="dia", seed=3, densa=True):
    luz(hora)
    ceu(c, t, seed=seed)
    montanhas(c, 600, 220, seed=seed, depth=0.85, col=(0.36, 0.48, 0.44))
    colinas(c, 650, 30, seed=seed, col=(0.28, 0.44, 0.30), depth=0.6)
    floresta(c, t, 680, 22, (180, 280), ("redonda",), seed=seed, depth=0.6)
    colinas(c, 740, 20, seed=seed + 2, col=(0.30, 0.46, 0.28), depth=0.35)
    floresta(c, t, 760, 14, (260, 400), ("redonda", "palmeira"), seed=seed + 1, depth=0.3)
    chao(c, t, 860, "grama", seed=seed)
    if densa:
        for i, xx in enumerate((-40, 1880)):
            arvore(c, t, xx, 1080, 900, "redonda", (0.22, 0.36, 0.24), seed + 50 + i)


def cena_deserto(c, t, hora="tarde", seed=4, piramides=True):
    luz(hora)
    ceu(c, t, nuvens=2, seed=seed)
    dunas(c, 700, seed=seed, depth=0.6, amp=50)
    if piramides:
        piramide(c, 1250, 720, 520, 340, depth=0.45)
        piramide(c, 1620, 730, 340, 220, depth=0.5)
    dunas(c, 840, seed=seed + 1, depth=0.15, amp=70)
    arvore(c, t, 1780, 900, 360, "palmeira", seed=seed)
    chao(c, t, 930, "areia", seed=seed)


def cena_neve(c, t, hora="noite", seed=5, nevando=True):
    luz(hora)
    ceu(c, t, nuvens=2, seed=seed)
    montanhas(c, 700, 460, seed=seed, depth=0.6, neve=True, col=(0.44, 0.48, 0.56))
    montanhas(c, 800, 260, seed=seed + 1, depth=0.3, neve=True, col=(0.40, 0.44, 0.52), picos=5)
    floresta(c, t, 840, 12, (160, 260), ("pinheiro",), (0.20, 0.32, 0.30), seed=seed, depth=0.35)
    chao(c, t, 860, "neve", seed=seed)
    if nevando:
        snow(c, t, 160, 50, 0.7)


def cena_mar(c, t, hora="noite", seed=6, navio="nau"):
    luz(hora)
    ceu(c, t, seed=seed)
    mar_i(c, t, 640)
    c.save(); c.translate(1150, 760)
    (vapor if navio == "vapor" else nau)(c, t, 0.9)
    c.restore()


def cena_campo(c, t, hora="dia", seed=7):
    luz(hora)
    ceu(c, t, passaros=True, seed=seed)
    montanhas(c, 620, 280, seed=seed, depth=0.8, neve=True)
    colinas(c, 700, 50, seed=seed, depth=0.45)
    floresta(c, t, 720, 9, (120, 200), ("redonda", "cipreste"), seed=seed, depth=0.4)
    colinas(c, 830, 30, seed=seed + 1, depth=0.1)
    chao(c, t, 880, "grama", seed=seed)


def cena_interior(c, t, hora="vela", tipo="biblioteca", seed=8):
    """interiores: biblioteca, cela (monge escrevendo), salao (mesa posta), escritorio"""
    luz(hora)
    if tipo == "biblioteca":
        interior(c, t, "madeira", "madeira", None, piso_y=860)
        estante(c, 60, 860, 560, 620, seed)
        estante(c, 700, 860, 560, 620, seed + 1)
        estante(c, 1340, 860, 560, 620, seed + 2)
    elif tipo == "cela":
        interior(c, t, "pedra", "pedra", "gotica", jx=1450)
        c.save(); c.translate(1000, 300); cruz_parede(c, 0.9); c.restore()
    elif tipo == "salao":
        interior(c, t, "reboco", "pedra", "gotica", jx=1500)
        mesa_i(c, 960, 800, 1200, toalha=(0.92, 0.90, 0.84))
    else:
        interior(c, t, "reboco", "madeira", "retangular", jx=1500)
        mesa_i(c, 1250, 790, 560)
    if _L["noite"]:
        c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.03, 0.02), 0.25); c.fill()


def particulas(c, t, tipo="poeira", n=40, seed=1):
    """partículas no ar: poeira (luz quente), brasas (incêndio, sobem), cinzas (caem), vagalumes (noite)"""
    rnd = random.Random(seed)
    for i in range(n):
        x0, y0, sp, ph = rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(10, 40), rnd.uniform(0, 6.28)
        if tipo == "brasas":
            x = (x0 + math.sin(t * 1.3 + ph) * 40) % W; y = (y0 - t * sp * 3) % H
            col, r, a = (1.0, 0.55, 0.20), rnd.uniform(2, 4), 0.8
        elif tipo == "cinzas":
            x = (x0 + t * 20 + math.sin(t + ph) * 30) % W; y = (y0 + t * sp) % H
            col, r, a = (0.55, 0.52, 0.50), rnd.uniform(2, 4), 0.6
        elif tipo == "vagalumes":
            x = (x0 + math.sin(t * 0.4 + ph) * 60) % W; y = 500 + (y0 % 500) + math.cos(t * 0.5 + ph) * 30
            col, r, a = (0.95, 1.0, 0.55), 3, 0.5 + 0.5 * math.sin(t * 3 + ph)
            rglow(c, x, y, 16, col, 0.35 * a)
        else:
            x = (x0 + math.sin(t * 0.3 + ph) * 50) % W; y = (y0 - t * sp * 0.4) % H
            col, r, a = (1.0, 0.95, 0.80), rnd.uniform(1.2, 2.8), 0.35 + 0.3 * math.sin(t * 1.5 + ph)
        c.new_sub_path(); c.arc(x, y, r, 0, 6.283); rgb(c, col, max(0, a)); c.fill()
