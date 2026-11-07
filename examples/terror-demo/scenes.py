"""Demo do kit de terror (TOM = "sombrio"): casa abandonada com relâmpago, cemitério com vulto, floresta sob lua de sangue, corredor com luz que falha."""
from engine import *
from ilustrado import *
STYLE = "ilustrado"
TOM = "sombrio"
THEME = "classico"
SFX_OFF = True
def a(c, t):
    cena_casa_abandonada(c, t, "tempestade", raios=(1.95,))
    historiador_i(c, t, 330, 1010, 1.0, poses=((0, "stand"),), exprs=((0, "worried"),), look=0.6)
    rotulo(c, t, 0, "A CASA DOS ESPÍRITOS", "Amityville, 1974", x=700, y=960)
def b(c, t):
    cena_cemiterio(c, t)
    historiador_i(c, t, 360, 1030, 1.0, poses=((0, "point_r"),), exprs=((0, "shocked"),), look=0.6)
    silhueta(c, t, 1350, 900, 0.55, 0.85)
def d(c, t):
    cena_floresta_sombria(c, t, "lua_sangue")
    historiador_i(c, t, 360, 1030, 1.0, poses=((0, "think"),), exprs=((0, "think"),), look=0.5)
    escurecer(c, 0.1, 0.5)
def e(c, t):
    luz("vela"); corredor(c, t)
    historiador_i(c, t, 600, 1060, 1.1, poses=((0, "stand"),), exprs=((0, "worried"),), look=0.3)
    silhueta(c, t, 960, 640, 0.32, 0.8)
SCENES=[(0,10,a),(10,20,b),(20,30,d),(30,999,e)]
