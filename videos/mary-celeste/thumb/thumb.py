"""Thumbnails do vídeo Mary Celeste (1280x720). Rodar da raiz do repo: python videos/mary-celeste/thumb/thumb.py"""
import sys, os
sys.path.insert(0, os.getcwd())
from engine import *
import render

OUT = os.path.dirname(os.path.abspath(__file__))


def big_title(c, s, x, y, size, col=INK, glow_col=AMBER):
    glow(c, x, y, size * 3.2, glow_col, 0.22)
    text(c, s, x, y, size, SERIF, col, outline=(0, 0, 0), ow=size * 0.16)


def finish(c):
    render.overlay(c, 1.0)
    c.set_source_surface(render.make_grain()[0], 0, 0); c.paint_with_alpha(0.5)


def ghost_ship(c, t, x, y, s, a=0.92):
    glow(c, x, y - 220 * s, 520 * s, ICE, 0.20)
    c.push_group()
    c.save(); c.translate(x, y); c.rotate(-0.04); c.scale(s, s); brigantine(c, t, 0.8); c.restore()
    c.pop_group_to_source(); c.paint_with_alpha(a)


def variant_a(c, t=1.0):
    """navio fantasma na névoa + NINGUÉM A BORDO"""
    background(c, t)
    stars(c, t, 110, 640)
    c.save(); c.translate(1700, 150); moon(c, 60); c.restore()
    glow(c, 1700, 150, 260, ICE, 0.15)
    sea(c, t, 660, 0.3)
    ghost_ship(c, t, 1300, 700, 1.15)
    fog(c, t, 700, 0.10, 8)
    historiador(c, t, 300, 1040, 1.25, [(0, "point_r")], [(0, "shocked")], look=1)
    big_title(c, "NINGUÉM", 980, 760, 150, LYELLOW, RED)
    big_title(c, "A BORDO", 980, 910, 150, INK, AMBER)
    c.save(); c.translate(1500, 120); date_stamp(c, "1872", 64, (1, 0.28, 0.22)); c.restore()
    finish(c)


def variant_b(c, t=1.0):
    """navio + bote vazio + O NAVIO FANTASMA"""
    background(c, t)
    stars(c, t, 90, 600)
    sea(c, t, 600, 0.35)
    ghost_ship(c, t, 1420, 660, 0.95)
    c.save(); c.translate(720, 800); c.scale(1.2, 1.2); lifeboat(c, 0); c.restore()
    c.save(); c.translate(720, 690); qmark(c, 150, AMBER); c.restore()
    fog(c, t, 760, 0.09, 8)
    big_title(c, "MARY CELESTE", 960, 150, 130, LYELLOW, AMBER)
    c.save(); c.translate(720, 300); date_stamp(c, "10 PESSOAS SUMIRAM", 60, (1, 0.28, 0.22)); c.restore()
    historiador(c, t, 230, 1060, 1.15, [(0, "head")], [(0, "desperate")], look=1)
    finish(c)


for name, fn in (("mary_celeste_thumb_A", variant_a), ("mary_celeste_thumb_B", variant_b)):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    fn(c)
    big = f"{OUT}/{name}_1080.png"
    surf.write_to_png(big)
    os.system(f'ffmpeg -loglevel error -y -i "{big}" -vf scale=1280:720:flags=lanczos "{OUT}/{name}.png" && rm "{big}"')
    print(name)
