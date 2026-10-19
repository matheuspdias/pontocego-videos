"""Thumbnails do Túmulo Perdido de Alexandre (1280x720). Rodar da raiz do repo: python videos/tumulo-alexandre/thumb/thumb.py"""
import sys, os
sys.path.insert(0, os.getcwd())
from engine import *
import render

OUT = os.path.dirname(os.path.abspath(__file__))
set_theme("deserto")


def big_title(c, s, x, y, size, col=INK, glow_col=AMBER):
    glow(c, x, y, size * 3.2, glow_col, 0.22)
    text(c, s, x, y, size, SERIF, col, outline=(0, 0, 0), ow=size * 0.16)


def finish(c):
    render.overlay(c, 1.0)
    c.set_source_surface(render.make_grain()[0], 0, 0); c.paint_with_alpha(0.5)


def variant_a(c, t=1.0):
    """caixão de ouro brilhando no deserto + O CORPO SUMIU"""
    background(c, t)
    stars(c, t, 110, 600)
    c.save(); c.translate(1720, 140); moon(c, 56); c.restore()
    glow(c, 1720, 140, 260, LYELLOW, 0.12)
    dunes(c, t, 820)
    for x, s in ((1500, 0.9), (1780, 0.6)):
        c.save(); c.translate(x, 860); c.scale(s, s); pyramid(c, 420, 260); c.restore()
    glow(c, 1080, 720, 520, AMBER, 0.35)
    c.save(); c.translate(1080, 830); c.scale(1.9, 1.9); royal_coffin(c, "gold"); c.restore()
    c.save(); c.translate(1080, 470); big_q(c, 200); c.restore()
    fog(c, t, 900, 0.10, 8)
    historiador(c, t, 280, 1060, 1.25, [(0, "head")], [(0, "shocked")], look=1)
    big_title(c, "ALEXANDRE, O GRANDE", 1000, 150, 96, INK, AMBER)
    big_title(c, "O CORPO SUMIU", 1000, 290, 130, (1, 0.35, 0.28), RED)
    finish(c)


def variant_b(c, t=1.0):
    """caixão de vidro com diadema + ONDE ESTÁ ALEXANDRE?"""
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.04, 0.03)); c.fill()
    for k in range(3):
        x = 760 + k * 440
        c.move_to(x - 180, 1080); c.line_to(x - 180, 420); c.curve_to(x - 180, 220, x + 180, 220, x + 180, 420); c.line_to(x + 180, 1080)
        rgb(c, (0.40, 0.28, 0.18), 0.7); c.set_line_width(10); c.stroke()
    glow(c, 1200, 760, 620, AMBER, 0.25)
    c.save(); c.translate(1200, 900); c.scale(2.1, 2.1); royal_coffin(c, "glass"); c.restore()
    fog(c, t, 980, 0.07, 7)
    historiador(c, t, 280, 1060, 1.2, [(0, "point_r")], [(0, "shocked")], look=1)
    big_title(c, "ONDE ESTÁ", 1080, 170, 140, INK, AMBER)
    big_title(c, "ALEXANDRE?", 1080, 330, 150, (1, 0.35, 0.28), RED)
    c.save(); c.translate(1600, 470); date_stamp(c, "PERDIDO HÁ 1.600 ANOS", 40, AMBER); c.restore()
    finish(c)


for name, fn in (("alexandre_thumb_A", variant_a), ("alexandre_thumb_B", variant_b)):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    fn(c)
    big = f"{OUT}/{name}_1080.png"
    surf.write_to_png(big)
    os.system(f'ffmpeg -loglevel error -y -i "{big}" -vf scale=1280:720:flags=lanczos "{OUT}/{name}.png" && rm "{big}"')
    print(name)
