"""Thumbnails do voo Varig 967 (1280x720). Rodar da raiz do repo: python videos/varig-967/thumb/thumb.py"""
import sys, os
sys.path.insert(0, os.getcwd())
from engine import *
import render

OUT = os.path.dirname(os.path.abspath(__file__))
set_theme("mar")


def big_title(c, s, x, y, size, col=INK, glow_col=AMBER):
    glow(c, x, y, size * 3.2, glow_col, 0.22)
    text(c, s, x, y, size, SERIF, col, outline=(0, 0, 0), ow=size * 0.16)


def finish(c):
    render.overlay(c, 1.0)
    c.set_source_surface(render.make_grain()[0], 0, 0); c.paint_with_alpha(0.5)


def sea_bg(c, t, y=760):
    g = cairo.LinearGradient(0, y, 0, H); g.add_color_stop_rgb(0, 0.06, 0.11, 0.17); g.add_color_stop_rgb(1, 0.02, 0.04, 0.07)
    c.rectangle(0, y, W, H - y); c.set_source(g); c.fill()
    for row in range(4):
        yy = y + 20 + row * 75
        for i in range(-1, 14):
            x = i * 160 + row * 40
            c.move_to(x, yy); c.curve_to(x + 40, yy - 12, x + 80, yy - 12, x + 120, yy)
        rgb(c, (0.30, 0.44, 0.60), 0.6 - row * 0.1); c.set_line_width(4); c.stroke()


def variant_a(c, t=1.0):
    """o 707 sumindo na névoa sobre o mar + SUMIU EM 22 MINUTOS"""
    background(c, t)
    stars(c, t, 120, 700)
    c.save(); c.translate(1660, 330); moon(c, 60); c.restore()
    sea_bg(c, t, 780)
    glow(c, 1180, 560, 520, AMBER, 0.16)
    c.push_group()
    c.save(); c.translate(1180, 560); c.rotate(-0.05); c.scale(1.35, 1.35); b707(c, t); c.restore()
    c.pop_group_to_source()
    m = cairo.LinearGradient(700, 0, 1700, 0); m.add_color_stop_rgba(0, 0, 0, 0, 0.15); m.add_color_stop_rgba(0.55, 0, 0, 0, 1.0); m.add_color_stop_rgba(1, 0, 0, 0, 1.0)
    c.mask(m)
    fog(c, t, 620, 0.25); fog(c, t, 820, 0.2)
    historiador(c, t, 250, 1070, 1.25, [(0, "head")], [(0, "shocked")], look=1)
    big_title(c, "22 MINUTOS", 1100, 110, 120, INK, AMBER)
    big_title(c, "E O SILÊNCIO", 1100, 245, 120, (1, 0.35, 0.28), RED)
    c.save(); c.translate(1320, 990); date_stamp(c, "VOO VARIG 967  •  1979", 52, RED); c.restore()
    finish(c)


def variant_b(c, t=1.0):
    """mapa do Pacífico com o ponto do último contato e a pergunta"""
    proj = make_proj(128, 168, 28, 56)
    draw_pacific(c, proj)
    x0, y0 = proj(140.4, 35.8); x1, y1 = proj(142.4, 36.5)
    line(c, x0, y0, x1, y1, 6, AMBER)
    for k, r in enumerate((60, 110, 170)):
        circle(c, x1, y1, r, None, 5 - k, RED)
    c.save(); c.translate(x1 + 40, y1); c.rotate(-0.4); plane_top(c, (0.92, 0.92, 0.94), 1.4); c.restore()
    c.save(); c.translate(1400, 660); big_q(c, 300, AMBER); c.restore()
    historiador(c, t, 250, 1070, 1.2, [(0, "point_r")], [(0, "worried")], look=1)
    big_title(c, "ONDE ESTÁ", 1150, 110, 120, INK, AMBER)
    big_title(c, "O VOO 967?", 1150, 245, 130, (1, 0.35, 0.28), RED)
    finish(c)


for name, fn in (("varig967_thumb_A", variant_a), ("varig967_thumb_B", variant_b)):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    fn(c)
    big = f"{OUT}/{name}_1080.png"
    surf.write_to_png(big)
    os.system(f'ffmpeg -loglevel error -y -i "{big}" -vf scale=1280:720:flags=lanczos "{OUT}/{name}.png" && rm "{big}"')
    print(name)
