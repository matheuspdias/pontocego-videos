"""Thumbnails do Manuscrito Voynich (1280x720). Rodar da raiz do repo: python videos/manuscrito-voynich/thumb/thumb.py"""
import sys, os
sys.path.insert(0, os.getcwd())
from engine import *
import render

OUT = os.path.dirname(os.path.abspath(__file__))
set_theme("classico")


def big_title(c, s, x, y, size, col=INK, glow_col=AMBER):
    glow(c, x, y, size * 3.2, glow_col, 0.22)
    text(c, s, x, y, size, SERIF, col, outline=(0, 0, 0), ow=size * 0.16)


def finish(c):
    render.overlay(c, 1.0)
    c.set_source_surface(render.make_grain()[0], 0, 0); c.paint_with_alpha(0.5)


def variant_a(c, t=1.0):
    """livro aberto (planta + piscinas) brilhando + NINGUÉM CONSEGUE LER"""
    background(c, t)
    stars(c, t, 110, 600)
    glow(c, 1180, 700, 640, AMBER, 0.32)
    c.save(); c.translate(1180, 720); c.rotate(-0.04); manuscript_spread(c, "herbal", "bath", t, 1.0, 0.95, seed=5); c.restore()
    fog(c, t, 1000, 0.08, 8)
    historiador(c, t, 250, 1070, 1.25, [(0, "head")], [(0, "shocked")], look=1)
    big_title(c, "NINGUÉM CONSEGUE", 1080, 110, 100, INK, AMBER)
    big_title(c, "LER ESTE LIVRO", 1080, 240, 124, (1, 0.35, 0.28), RED)
    finish(c)


def variant_b(c, t=1.0):
    """palavras do manuscrito em close + 600 ANOS SEM TRADUÇÃO"""
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.045, 0.04)); c.fill()
    glow(c, 1150, 560, 700, AMBER, 0.22)
    c.save(); c.translate(1150, 600); c.rotate(-0.03)
    rrect(c, -640, -300, 1280, 600, 18); fs(c, VELLUM, 6, (0.50, 0.40, 0.26))
    for r, wd in enumerate((("qokedy", "daiin", "chedy"), ("shedy", "qokain", "otedy"))):
        x = -560
        for w_ in wd:
            c.save(); c.translate(x, -60 + r * 230); vword(c, w_, 120, VINK, lw=9); c.restore()
            x += vword_w(w_, 120) + 70
    c.restore()
    c.save(); c.translate(1660, 860); star_mark(c, 50); c.restore()
    fog(c, t, 1000, 0.06, 7)
    historiador(c, t, 230, 1070, 1.2, [(0, "point_r")], [(0, "shocked")], look=1)
    big_title(c, "O QUE ESTÁ ESCRITO?", 1100, 130, 108, INK, AMBER)
    c.save(); c.translate(1380, 980); date_stamp(c, "600 ANOS SEM TRADUÇÃO", 52, RED); c.restore()
    finish(c)


for name, fn in (("voynich_thumb_A", variant_a), ("voynich_thumb_B", variant_b)):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    fn(c)
    big = f"{OUT}/{name}_1080.png"
    surf.write_to_png(big)
    os.system(f'ffmpeg -loglevel error -y -i "{big}" -vf scale=1280:720:flags=lanczos "{OUT}/{name}.png" && rm "{big}"')
    print(name)
