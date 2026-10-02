"""Banner do canal Ponto Cego (2560x1440). Rodar da raiz: python marca/banner.py"""
import sys, os
sys.path.insert(0, os.getcwd())
import engine
engine.W, engine.H = 2560, 1440
from engine import *
WB, HB = 2560, 1440
OUT = os.path.dirname(os.path.abspath(__file__))

s = cairo.ImageSurface(cairo.FORMAT_RGB24, WB, HB); c = cairo.Context(s)
c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
t = 2.0
background(c, t)
stars(c, t, 220, HB)
c.save(); c.translate(2180, 300); moon(c, 80); c.restore()
c.save(); c.translate(1280, 1460); mountains(c, 3400, 420, True, (0.12, 0.14, 0.19)); c.restore()
fog(c, t, 1150, 0.10)
# área segura: x 507..2053, y 508..931
glow(c, 1400, 700, 900, AMBER, 0.12)
text(c, "PONTO CEGO", 1450, 645, 150, SERIF, INK, outline=(0, 0, 0), ow=14)
line(c, 960, 745, 1940, 745, 4, AMBER)
text(c, "histórias e mistérios que ninguém conseguiu explicar", 1450, 805, 42, TYPE, AMBER)
text(c, "novos vídeos  •  terça e quinta, 19h", 1450, 870, 36, TYPE, LGRAY if False else (0.72, 0.70, 0.64))
historiador(c, t, 690, 915, 0.72, [(0, "stand")], [(0, "neutral")], look=1)
# vinheta
v = cairo.RadialGradient(WB / 2, HB / 2, HB * 0.35, WB / 2, HB / 2, WB * 0.7)
v.add_color_stop_rgba(0, 0, 0, 0, 0); v.add_color_stop_rgba(1, 0, 0, 0, 0.75)
c.set_source(v); c.paint()
s.write_to_png(f"{OUT}/banner_pontocego.png")
print("ok")
