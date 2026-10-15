"""Thumbnails da Expedição Franklin (1280x720). Rodar da raiz do repo: python videos/expedicao-franklin/thumb/thumb.py"""
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


def frozen_ship(c, t, x, y, s, a=0.95, tilt=-0.04):
    glow(c, x, y - 240 * s, 560 * s, ICE, 0.22)
    c.push_group()
    c.save(); c.translate(x, y); c.rotate(tilt); c.scale(s, s); bomb_ship(c, t, None, furled=True, frost=1.0); c.restore()
    c.pop_group_to_source(); c.paint_with_alpha(a)


def variant_a(c, t=1.0):
    """navios presos no gelo + 129 HOMENS / NENHUM VOLTOU"""
    background(c, t)
    stars(c, t, 110, 600)
    c.save(); c.translate(1720, 140); moon(c, 56); c.restore()
    glow(c, 1720, 140, 260, ICE, 0.15)
    frozen_ship(c, t, 1360, 760, 1.15)
    frozen_ship(c, t, 1760, 770, 0.75, 0.7, -0.08)
    ice_field(c, t, 770)
    fog(c, t, 760, 0.10, 8)
    snow(c, t, 120, 60, 0.7)
    historiador(c, t, 290, 1050, 1.25, [(0, "head")], [(0, "shocked")], look=1)
    big_title(c, "129 HOMENS", 900, 200, 140, INK, AMBER)
    big_title(c, "NENHUM VOLTOU", 900, 360, 120, (1, 0.35, 0.28), RED)
    c.save(); c.translate(900, 500); date_stamp(c, "1845", 60, AMBER); c.restore()
    finish(c)


def variant_b(c, t=1.0):
    """o Terror no fundo do mar + O GELO ESCONDEU"""
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.06, 0.14, 0.20); g.add_color_stop_rgb(1, 0.01, 0.03, 0.05)
    c.rectangle(0, 0, W, H); c.set_source(g); c.fill()
    for i in range(5):
        x = 300 + i * 360
        poly(c, [(x, 0), (x + 70, 0), (x + 230, H), (x + 140, H)]); rgb(c, ICE, 0.05); c.fill()
    c.save(); c.translate(960, 980); seabed(c, t, 120, 2400, 6, (0.10, 0.12, 0.13)); c.restore()
    glow(c, 1250, 640, 620, ICE, 0.22)
    c.save(); c.translate(1250, 900); c.rotate(0.05); c.scale(1.35, 1.35); bomb_ship(c, t, "TERROR", sails=False); c.restore()
    glow(c, 1250, 820, 90, AMBER, 0.55)
    fog(c, t, 960, 0.07, 7)
    historiador(c, t, 280, 1060, 1.2, [(0, "point_r")], [(0, "shocked")], look=1)
    big_title(c, "O GELO", 720, 170, 150, INK, ICE)
    big_title(c, "ESCONDEU", 720, 330, 150, (1, 0.35, 0.28), RED)
    c.save(); c.translate(1500, 120); date_stamp(c, "129 MORTOS", 54, AMBER); c.restore()
    finish(c)


for name, fn in (("franklin_thumb_A", variant_a), ("franklin_thumb_B", variant_b)):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    fn(c)
    big = f"{OUT}/{name}_1080.png"
    surf.write_to_png(big)
    os.system(f'ffmpeg -loglevel error -y -i "{big}" -vf scale=1280:720:flags=lanczos "{OUT}/{name}.png" && rm "{big}"')
    print(name)
