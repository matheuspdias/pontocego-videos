"""Thumbnails do Passo Dyatlov (1280x720). Rodar da raiz do repo: python videos/passo-dyatlov/thumb/thumb.py"""
import sys, os
sys.path.insert(0, os.getcwd())
from engine import *
import render

OUT = os.path.dirname(os.path.abspath(__file__))
set_theme("neve")


def big_title(c, s, x, y, size, col=INK, glow_col=AMBER):
    glow(c, x, y, size * 3.2, glow_col, 0.22)
    text(c, s, x, y, size, SERIF, col, outline=(0, 0, 0), ow=size * 0.16)


def finish(c):
    render.overlay(c, 1.0)
    c.set_source_surface(render.make_grain()[0], 0, 0); c.paint_with_alpha(0.5)


def snow_ground(c, y):
    c.rectangle(0, y, W, H - y)
    g = cairo.LinearGradient(0, y, 0, H); g.add_color_stop_rgb(0, 0.78, 0.82, 0.88); g.add_color_stop_rgb(1, 0.55, 0.60, 0.68)
    c.set_source(g); c.fill()


def variant_a(c, t=1.0):
    """barraca rasgada por dentro, em close, + RASGADA POR DENTRO"""
    background(c, t)
    stars(c, t, 110, 600)
    snow_ground(c, 820)
    glow(c, 1150, 640, 560, AMBER, 0.20)
    c.save(); c.translate(1150, 840); c.scale(1.9, 1.9); dyatlov_tent(c, t, cut=1.0, glow_on=True); c.restore()
    c.save(); c.translate(1150, 1000); footprints(c, 12, -70, 6, None, 0, (0.40, 0.46, 0.58)); c.restore()
    snow(c, t, 160, 80, 0.8)
    historiador(c, t, 250, 1070, 1.25, [(0, "head")], [(0, "shocked")], look=1)
    big_title(c, "RASGADA", 1150, 110, 120, INK, AMBER)
    big_title(c, "POR DENTRO", 1150, 245, 120, (1, 0.35, 0.28), RED)
    finish(c)


def variant_b(c, t=1.0):
    """encosta noturna com a barraca + 9 bandeirinhas; -30 °C e a pergunta"""
    background(c, t)
    stars(c, t, 120, 500)
    c.save(); c.translate(1640, 160); moon(c, 60); c.restore()
    c.move_to(0, 960); c.line_to(560, 960); c.line_to(W, 440); c.line_to(W, H); c.line_to(0, H); c.close_path()
    g = cairo.LinearGradient(0, 440, 0, H); g.add_color_stop_rgb(0, 0.82, 0.86, 0.92); g.add_color_stop_rgb(1, 0.55, 0.60, 0.68)
    c.set_source(g); c.fill()
    c.save(); c.translate(1620, 548); c.scale(0.8, 0.8); dyatlov_tent(c, t, cut=1.0, sag=0.4, snow_on=0.6); c.restore()
    for k in range(9):
        x = 700 + k * 100
        y = 960 - (x - 560) / (W - 560) * 520
        c.save(); c.translate(x, y + 10); line(c, 0, 0, 0, -90, 5, (0.70, 0.66, 0.60)); poly(c, [(0, -90), (46, -76), (0, -62)]); fs(c, RED, 3); c.restore()
    snow(c, t, 180, 120, 0.8)
    historiador(c, t, 240, 1070, 1.2, [(0, "point_r")], [(0, "worried")], look=1)
    big_title(c, "O QUE ACONTECEU", 1060, 110, 100, INK, AMBER)
    big_title(c, "NESTA NOITE?", 1060, 235, 120, (1, 0.35, 0.28), RED)
    c.save(); c.translate(1300, 980); date_stamp(c, "-30 °C  •  1959", 52, RED); c.restore()
    finish(c)


for name, fn in (("dyatlov_thumb_A", variant_a), ("dyatlov_thumb_B", variant_b)):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    fn(c)
    big = f"{OUT}/{name}_1080.png"
    surf.write_to_png(big)
    os.system(f'ffmpeg -loglevel error -y -i "{big}" -vf scale=1280:720:flags=lanczos "{OUT}/{name}.png" && rm "{big}"')
    print(name)
