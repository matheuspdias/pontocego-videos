"""Foto de perfil do canal (800x800, recorte circular do YouTube). Rodar da raiz: python marca/avatar.py"""
import sys, os
sys.path.insert(0, os.getcwd())
import engine
from engine import *

OUT = os.path.dirname(os.path.abspath(__file__))
S = 1600


def draw(c, variant):
    t = 1.3
    # fundo
    g = cairo.RadialGradient(S / 2, S * 0.48, 0, S / 2, S / 2, S * 0.75)
    g.add_color_stop_rgb(0, 0.16, 0.12, 0.08) if variant == "A" else g.add_color_stop_rgb(0, 0.09, 0.11, 0.16)
    g.add_color_stop_rgb(1, 0.03, 0.03, 0.05)
    c.set_source(g); c.paint()
    rnd = random.Random(8)
    for _ in range(90):
        x, y = rnd.uniform(0, S), rnd.uniform(0, S * 0.6)
        rgb(c, INK, rnd.uniform(0.2, 0.7)); c.new_sub_path(); c.arc(x, y, rnd.uniform(1.5, 3.5), 0, 6.283); c.fill()
    # luz da lanterna por baixo
    glow(c, S * 0.62, S * 0.95, S * 0.65, AMBER, 0.35)
    # Historiador em close (busto): figura grande, pés fora do quadro
    pose = "stand" if variant == "A" else "think"
    expr = "confident" if variant == "A" else "think"
    historiador(c, t, S * 0.5, S * 1.45, 4.1, [(0, pose)], [(0, expr)], look=0.0 if variant == "A" else 0.6,
                lantern_on=False)
    if variant == "B":
        c.save(); c.translate(S * 0.80, S * 0.30); big_q(c, 260, AMBER); c.restore()
    # vinheta circular
    v = cairo.RadialGradient(S / 2, S / 2, S * 0.30, S / 2, S / 2, S * 0.72)
    v.add_color_stop_rgba(0, 0, 0, 0, 0); v.add_color_stop_rgba(1, 0, 0, 0, 0.8)
    c.set_source(v); c.paint()


for variant in ("A", "B"):
    engine.W, engine.H = S, S
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, S, S); c = cairo.Context(surf)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    draw(c, variant)
    big = f"{OUT}/avatar_{variant}_big.png"
    surf.write_to_png(big)
    os.system(f'ffmpeg -loglevel error -y -i "{big}" -vf scale=800:800:flags=lanczos "{OUT}/avatar_{variant}.png" && rm "{big}"')
    # prévia: como fica no círculo, em tamanho grande e pequeno
    os.system(f'ffmpeg -loglevel error -y -i "{OUT}/avatar_{variant}.png" -vf "format=rgba,geq=r=\'r(X,Y)\':g=\'g(X,Y)\':b=\'b(X,Y)\':a=\'if(lte(hypot(X-400,Y-400),400),255,0)\'" "{OUT}/preview_circulo_{variant}.png"')
    print(variant)
