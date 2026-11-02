"""Thumbnails da Praga da Dança (1280x720). Rodar da raiz do repo: python videos/praga-da-danca/thumb/thumb.py"""
import sys, os
sys.path.insert(0, os.getcwd())
from engine import *
import render

OUT = os.path.dirname(os.path.abspath(__file__))
set_theme("cidade")


def big_title(c, s, x, y, size, col=INK, glow_col=AMBER):
    glow(c, x, y, size * 3.2, glow_col, 0.22)
    text(c, s, x, y, size, SERIF, col, outline=(0, 0, 0), ow=size * 0.16)


def finish(c):
    render.overlay(c, 1.0)
    c.set_source_surface(render.make_grain()[0], 0, 0); c.paint_with_alpha(0.5)


def variant_a(c, t=1.3):
    """Frau Troffea dançando sozinha na rua + NÃO CONSEGUIAM PARAR"""
    background(c, t)
    stars(c, t, 110, 500)
    strasbourg(c, t, 900, n=7, seed=3, lit=0.9)
    c.rectangle(0, 0, W, H); rgb(c, (0.02, 0.02, 0.03), 0.35); c.fill()
    glow(c, 1150, 760, 420, RED, 0.22)
    rnd = random.Random(4)
    for i in range(10):
        x = 820 + i * 100 + rnd.uniform(-20, 20)
        c.save(); faded_alpha = 0.55
        c.push_group()
        figure(c, t + i * 0.37, x, 1000, 0.45, poses=[(0, ["dance_a", "dance_b", "dance_c", "dance_d"][i % 4])],
               exprs=[(0, "desperate")], coat=[(0.40, 0.34, 0.26), (0.32, 0.30, 0.38), (0.44, 0.30, 0.24)][i % 3],
               hat="coif" if i % 2 else "beret", hair=None, fid=i + 20)
        c.pop_group_to_source(); c.paint_with_alpha(faded_alpha); c.restore()
    figure(c, t, 1150, 1040, 1.15, poses=[(0, "dance_a")], exprs=[(0, "desperate")], coat=(0.52, 0.22, 0.20),
           hat="coif", hair="long", fid=7)
    fog(c, t, 960, 0.15)
    historiador(c, t, 250, 1070, 1.2, [(0, "head")], [(0, "shocked")], look=1)
    big_title(c, "NÃO CONSEGUIAM", 1130, 110, 104, INK, AMBER)
    big_title(c, "PARAR DE DANÇAR", 1130, 240, 104, (1, 0.35, 0.28), RED)
    c.save(); c.translate(1500, 420); c.rotate(-0.05); date_stamp(c, "1518", 64, AMBER); c.restore()
    finish(c)


def variant_b(c, t=1.0):
    """sapatos vermelhos com cruzes e São Vito ao fundo + A MALDIÇÃO DA DANÇA"""
    background(c, t)
    c.rectangle(0, 0, W, H); rgb(c, (0.05, 0.03, 0.03)); c.fill()
    glow(c, 1250, 560, 640, RED, 0.18)
    c.save(); c.translate(1580, 900); c.scale(1.1, 1.1); saint_statue(c, t, True); c.restore()
    c.save(); c.translate(1080, 820); c.scale(2.6, 2.6); red_shoes(c, True, glow_on=True); c.restore()
    smoke(c, t, 1400, 1000, 700, 0.22, 3)
    historiador(c, t, 250, 1070, 1.2, [(0, "point_r")], [(0, "worried")], look=1)
    big_title(c, "A MALDIÇÃO", 1120, 110, 120, INK, AMBER)
    big_title(c, "DA DANÇA", 1120, 245, 130, (1, 0.35, 0.28), RED)
    c.save(); c.translate(1080, 1000); date_stamp(c, "ESTRASBURGO  •  1518", 48, AMBER); c.restore()
    finish(c)


for name, fn in (("praga_danca_thumb_A", variant_a), ("praga_danca_thumb_B", variant_b)):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    fn(c)
    big = f"{OUT}/{name}_1080.png"
    surf.write_to_png(big)
    os.system(f'ffmpeg -loglevel error -y -i "{big}" -vf scale=1280:720:flags=lanczos "{OUT}/{name}.png" && rm "{big}"')
    print(name)
