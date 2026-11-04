"""Thumbnails das Linhas de Nazca (1280x720). Rodar da raiz do repo: python videos/linhas-de-nazca/thumb/thumb.py"""
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
    """beija-flor gigante visto de cima, avião pequeno passando + SÓ SE VÊ DO CÉU"""
    pampa_top(c, t, 3, nazca_lines_set(5, 6))
    c.save(); c.translate(1120, 760); c.scale(3.1, 3.1); geoglyph(c, "hummingbird", 1.0, (0.96, 0.90, 0.72), 9 / 3.1, 0.10); c.restore()
    c.save(); c.translate(1760, 640); c.scale(0.7, 0.7); plane_shadow(c); c.restore()
    c.save(); c.translate(1700, 570); c.scale(0.7, 0.7); cessna_top(c, t); c.restore()
    c.rectangle(0, 0, W, 330); g = cairo.LinearGradient(0, 0, 0, 330)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.75); g.add_color_stop_rgba(1, 0, 0, 0, 0); c.set_source(g); c.fill()
    historiador(c, t, 250, 1070, 1.2, [(0, "point_ru")], [(0, "shocked")], look=1)
    big_title(c, "SÓ SE VÊ", 1150, 110, 120, INK, AMBER)
    big_title(c, "DO CÉU", 1150, 245, 130, (1, 0.72, 0.30), AMBER)
    c.save(); c.translate(1620, 1010); c.rotate(-0.05); date_stamp(c, "NAZCA  •  PERU", 48, AMBER); c.restore()
    finish(c)


def variant_b(c, t=1.0):
    """o Astronauta na encosta + disco + QUEM DESENHOU ISSO?"""
    background(c, t)
    stars(c, t, 120, 600)
    pampa_side(c, t, 860, hills=False)
    c.move_to(560, H); c.curve_to(760, 520, 1100, 260, 1460, 250); c.curve_to(1660, 250, 1800, 420, 1950, 620)
    c.line_to(W, H); c.close_path(); rgb(c, (0.30, 0.19, 0.13)); c.fill()
    c.save(); c.translate(1250, 620); c.scale(3.0, 3.0); geoglyph(c, "astronaut", 1.0, (0.96, 0.90, 0.72), 9 / 3.0, 0.12); c.restore()
    c.save(); c.translate(1650, 420); c.scale(0.55, 0.55); ufo_disc(c, t); c.restore()
    historiador(c, t, 250, 1070, 1.2, [(0, "point_r")], [(0, "worried")], look=1)
    big_title(c, "QUEM DESENHOU", 1100, 110, 110, INK, AMBER)
    big_title(c, "ISSO?", 1100, 240, 130, (1, 0.72, 0.30), AMBER)
    finish(c)


for name, fn in (("nazca_thumb_A", variant_a), ("nazca_thumb_B", variant_b)):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    fn(c)
    big = f"{OUT}/{name}_1080.png"
    surf.write_to_png(big)
    os.system(f'ffmpeg -loglevel error -y -i "{big}" -vf scale=1280:720:flags=lanczos "{OUT}/{name}.png" && rm "{big}"')
    print(name)
