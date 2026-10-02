"""Thumbnails do vídeo MH370 (1280x720). Rodar da raiz do repo: python videos/mh370/thumb/thumb.py"""
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


def variant_a(c, t=1.0):
    """avião sumindo sobre o oceano + ONDE ESTÁ O MH370?"""
    background(c, t)
    stars(c, t, 120, 700)
    g = cairo.LinearGradient(0, 640, 0, H)
    g.add_color_stop_rgb(0, 0.07, 0.13, 0.20); g.add_color_stop_rgb(1, 0.01, 0.03, 0.06)
    c.rectangle(0, 640, W, H - 640); c.set_source(g); c.fill()
    for i in range(16):
        x = i * 140 - 40
        c.move_to(x, 640); c.curve_to(x + 35, 628, x + 70, 628, x + 105, 640)
    rgb(c, BLUE); c.set_line_width(4); c.stroke()
    # avião "desmanchando"
    glow(c, 1260, 330, 420, ICE, 0.18)
    c.save(); c.translate(1260, 330); c.rotate(-0.12); c.scale(1.5, 1.5)
    c.push_group(); airplane(c, (0.80, 0.82, 0.86)); c.pop_group_to_source(); c.paint_with_alpha(0.9)
    c.restore()
    rnd = random.Random(2)
    for i in range(70):  # partículas se desfazendo à direita
        x = 1480 + rnd.uniform(0, 420); y = 300 + rnd.uniform(-90, 110)
        r = rnd.uniform(2, 7) * (1 - (x - 1480) / 480)
        rgb(c, (0.8, 0.82, 0.86), 0.8 * (1 - (x - 1480) / 480)); c.new_sub_path(); c.arc(x, y, max(r, 0.5), 0, 6.283); c.fill()
    # Historiador com lanterna
    historiador(c, t, 330, 1040, 1.25, [(0, "point_ru")], [(0, "shocked")], look=1)
    big_title(c, "ONDE ESTÁ", 1150, 690, 120)
    big_title(c, "O MH370?", 1150, 840, 170, LYELLOW)
    c.save(); c.translate(1250, 975); date_stamp(c, "239 PESSOAS A BORDO", 62, (1, 0.28, 0.22)); c.restore()
    fog(c, t, 980, 0.07)
    finish(c)


def variant_b(c, t=1.0):
    """radar com o ponto sumindo + SUMIU"""
    background(c, t)
    stars(c, t, 60, 1080)
    c.save(); c.translate(1380, 470); c.scale(2.4, 2.4); radar(c, 0.6, blip=False); c.restore()
    x, y = 1380 + 60 * 2.4, 470 - 50 * 2.4
    glow(c, x, y, 120, RED, 0.6)
    circle(c, x, y, 18, RED, 5)
    c.save(); c.translate(x, y); big_x(c, 46, RED, 12); c.restore()
    text(c, "MH370", x + 50, y - 50, 44, TYPE, (0.6, 1, 0.7), align="l", outline=(0, 0, 0), ow=6)
    historiador(c, t, 220, 1040, 1.2, [(0, "head")], [(0, "desperate")], look=1)
    big_title(c, "SUMIU", 900, 810, 230, LYELLOW, RED)
    c.save(); c.translate(900, 975); date_stamp(c, "COM 239 PESSOAS", 62, (1, 0.28, 0.22)); c.restore()
    fog(c, t, 1000, 0.07)
    finish(c)


for name, fn in (("mh370_thumb_A", variant_a), ("mh370_thumb_B", variant_b)):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    fn(c)
    big = f"{OUT}/{name}_1080.png"
    surf.write_to_png(big)
    os.system(f'ffmpeg -loglevel error -y -i "{big}" -vf scale=1280:720:flags=lanczos "{OUT}/{name}.png" && rm "{big}"')
    print(name)
