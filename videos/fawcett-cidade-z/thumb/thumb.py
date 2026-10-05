"""Thumbnails do vídeo Percy Fawcett e a Cidade de Z (1280x720). Rodar da raiz do repo: python videos/fawcett-cidade-z/thumb/thumb.py"""
import sys, os
sys.path.insert(0, os.getcwd())
from engine import *
import render

OUT = os.path.dirname(os.path.abspath(__file__))
FAW = dict(coat=(0.55, 0.48, 0.32), shirt=(0.80, 0.76, 0.62), hat="fedora", hat_col=(0.62, 0.55, 0.38), mustache=True, hair=None)


def big_title(c, s, x, y, size, col=INK, glow_col=AMBER):
    glow(c, x, y, size * 3.2, glow_col, 0.22)
    text(c, s, x, y, size, SERIF, col, outline=(0, 0, 0), ow=size * 0.16)


def finish(c):
    render.overlay(c, 1.0)
    c.set_source_surface(render.make_grain()[0], 0, 0); c.paint_with_alpha(0.5)


def variant_a(c, t=1.0):
    """Z gigante brilhando na selva + SUMIU NA AMAZÔNIA"""
    background(c, t)
    stars(c, t, 110, 560)
    c.push_group(); jungle(c, t, 760, n=16, h=(220, 340), col=(0.07, 0.11, 0.10), seed=12, edge=0.2); c.pop_group_to_source(); c.paint_with_alpha(0.7)
    glow(c, 1380, 430, 600, AMBER, 0.22)
    text(c, "Z", 1380, 430, 520, SERIF, AMBER, outline=(0, 0, 0), ow=40)
    jungle(c, t, 1120, n=10, h=(300, 440), col=(0.09, 0.15, 0.12), seed=5, edge=0.4)
    fog(c, t, 900, 0.10, 8)
    figure(c, t, 560, 1050, 1.25, poses=[(0, "point_r")], exprs=[(0, "shocked")], fid=40, **FAW)
    big_title(c, "SUMIU NA", 600, 190, 120, INK, AMBER)
    big_title(c, "AMAZÔNIA", 600, 320, 120, LYELLOW, RED)
    c.save(); c.translate(1640, 110); date_stamp(c, "1925", 64, (1, 0.28, 0.22)); c.restore()
    finish(c)


def variant_b(c, t=1.0):
    """3 vultos entrando na mata + A CIDADE DE Z"""
    background(c, t)
    stars(c, t, 100, 600)
    c.save(); c.translate(1600, 160); moon(c, 60); c.restore()
    glow(c, 1600, 160, 260, ICE, 0.15)
    jungle(c, t, 1100, n=12, h=(380, 560), col=(0.08, 0.13, 0.11), seed=21, edge=0.3)
    glow(c, 1150, 860, 360, AMBER, 0.16)
    for i, (dx, s) in enumerate([(0, 0.95), (150, 0.88), (290, 0.88)]):
        c.push_group(); figure(c, t, 1000 + dx, 1050, s, poses=[(0, "run")], exprs=[(0, "neutral")], fid=40 + i, **FAW)
        c.pop_group_to_source(); c.paint_with_alpha(0.75 - i * 0.15)
    fog(c, t, 920, 0.12, 9)
    big_title(c, "A CIDADE DE Z", 960, 170, 130, LYELLOW, AMBER)
    c.save(); c.translate(960, 320); date_stamp(c, "NUNCA VOLTARAM", 62, (1, 0.28, 0.22)); c.restore()
    historiador(c, t, 260, 1060, 1.15, [(0, "head")], [(0, "desperate")], look=1)
    finish(c)


for name, fn in (("fawcett_thumb_A", variant_a), ("fawcett_thumb_B", variant_b)):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    fn(c)
    big = f"{OUT}/{name}_1080.png"
    surf.write_to_png(big)
    os.system(f'ffmpeg -loglevel error -y -i "{big}" -vf scale=1280:720:flags=lanczos "{OUT}/{name}.png" && rm "{big}"')
    print(name)
