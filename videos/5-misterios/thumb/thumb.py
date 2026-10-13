"""Thumbnails do vídeo 5 mistérios (1280x720). Rodar da raiz do repo: python videos/5-misterios/thumb/thumb.py"""
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
    """máscara de chumbo gigante no morro + 5 MISTÉRIOS SEM SOLUÇÃO"""
    background(c, t)
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.05, 0.06, 0.10); g.add_color_stop_rgb(1, 0.25, 0.10, 0.08)
    c.rectangle(0, 0, W, H); c.set_source(g); c.fill()
    stars(c, t, 80, 500)
    c.save(); c.translate(1300, 1100); morro(c, 1600, 520, (0.08, 0.12, 0.10)); c.restore()
    glow(c, 1320, 470, 520, RED, 0.25)
    c.save(); c.translate(1320, 470); c.scale(2.6, 2.6); lead_mask(c); c.restore()
    historiador(c, t, 170, 1040, 1.1, [(0, "think")], [(0, "shocked")], look=1)
    big_title(c, "5 MISTÉRIOS", 820, 720, 130, LYELLOW, RED)
    big_title(c, "SEM SOLUÇÃO", 820, 870, 120, INK, RED)
    c.save(); c.translate(1320, 990); date_stamp(c, "O Nº 1 É NO BRASIL", 60, (1, 0.28, 0.22)); c.restore()
    fog(c, t, 980, 0.07)
    finish(c)


def variant_b(c, t=1.0):
    """grade de 5 casos com o último destacado"""
    background(c, t)
    stars(c, t, 90, 1080)
    icons = [lambda c: sc(axe, s=0.9)(c), lambda c: signal_wave(c, 0, 260, 6, 120, 0.5, 0.1, ICE, 6),
             lambda c: at(0, 60, sc(parachute, 0, s=0.6))(c), lambda c: sc(farmhouse, 0, 1.0, s=0.3)(c), lambda c: sc(lead_mask, s=0.72)(c)]
    for i, fn in enumerate(icons):
        x = 220 + i * 370
        hot = i == 4
        if hot:
            glow(c, x, 380, 360, RED, 0.35)
        c.save(); c.translate(x, 380); c.scale(1.12 if hot else 1.0, 1.12 if hot else 1.0)
        rrect(c, -165, -230, 330, 460, 14); fs(c, (0.13, 0.12, 0.13), 6, RED if hot else INK)
        at(0, -20, fn)(c)
        text(c, str(5 - i), 0, 170, 70, SERIF, RED if hot else AMBER, outline=(0, 0, 0), ow=8)
        c.restore()
    big_title(c, "NINGUÉM EXPLICOU", 960, 790, 120, LYELLOW, RED)
    c.save(); c.translate(960, 950); date_stamp(c, "ATÉ HOJE", 70, (1, 0.28, 0.22)); c.restore()
    fog(c, t, 1000, 0.07)
    finish(c)


for name, fn in (("5misterios_thumb_A", variant_a), ("5misterios_thumb_B", variant_b)):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    fn(c)
    big = f"{OUT}/{name}_1080.png"
    surf.write_to_png(big)
    os.system(f'ffmpeg -loglevel error -y -i "{big}" -vf scale=1280:720:flags=lanczos "{OUT}/{name}.png" && rm "{big}"')
    print(name)
