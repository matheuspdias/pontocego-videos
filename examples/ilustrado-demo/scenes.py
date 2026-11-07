"""Demo do estilo ILUSTRADO: um cenário diferente por cena (silencioso, ~56 s)."""
from engine import *
from ilustrado import *

STYLE = "ilustrado"
THEME = "classico"
SFX_OFF = True


def s01(c, t):  # vila medieval ao entardecer: abertura com título
    cena_vila(c, t, "tarde", igreja_x=1560)
    figurantes(c, t, 905, n=6, s=0.36, seed=2, x0=700, x1=1800)
    historiador_i(c, t, 330, 1010, 1.05, poses=((0, "stand"), (1.2, "present")), exprs=((0, "neutral"), (1.2, "confident")), look=0.4)
    if t > 1.0:
        c.save(); p = ease_out(prog(t, 1.0, 0.8)); c.translate(0, 20 * (1 - p))
        titulo_i(c, "A PESTE NEGRA", 1100, 200, 110); c.restore()
    particulas(c, t, "poeira", 30)
    rotulo(c, t, 2.0, "OUTUBRO DE 1347", "Messina, Sicília", x=150, y=950)


def s02(c, t):  # porto de dia com naus e gente andando
    t0 = 7
    cena_porto(c, t, "dia")
    figurantes(c, t, 905, n=9, s=0.30, seed=5, x0=500, x1=1850, figurinos=["marinheiro", "campones", "camponesa", "monge"])
    historiador_i(c, t, 300, 1010, 1.0, poses=((0, "point_r"),), exprs=((0, "neutral"), (t0 + 2.5, "worried")), look=0.6)
    rotulo(c, t, t0 + 0.6, "O PORTO DE MESSINA", "doze galés chegam do Mar Negro")


def s03(c, t):  # biblioteca à luz de vela
    t0 = 14
    cena_interior(c, t, "vela", "biblioteca")
    mesa_i(c, 1180, 860, 620)
    c.save(); c.translate(1120, 846); livro_aberto(c, 240); c.restore()
    vela_i(c, t, 1380, 846, 1.0)
    boneco(c, t, 1030, 1060, 0.95, poses=((0, "hold"),), exprs=((0, "think"),), look=0.7, fid=4, **FIGURINO["monge"])
    historiador_i(c, t, 360, 1050, 1.05, poses=((0, "think"),), exprs=((0, "think"),), look=0.5, lanterna=False)
    c.save(); c.translate(1500, 330); placa(c, "O MELHOR REMÉDIO: FUGIR", "GUY DE CHAULIAC", size=38); c.restore()


def s04(c, t):  # floresta tropical de dia com explorador
    t0 = 21
    cena_floresta(c, t, "dia")
    boneco(c, t, 1300, 1000, 1.0, poses=((0, "point_ru"),), exprs=((0, "confident"),), look=0.4, fid=6, andar=False, **FIGURINO["explorador"])
    historiador_i(c, t, 420, 1010, 1.0, poses=((0, "stand"), (t0 + 2, "hips")), exprs=((0, "happy"),), look=0.6)
    rotulo(c, t, t0 + 0.8, "1925 · PERCY FAWCETT", "Mato Grosso, Brasil")


def s05(c, t):  # deserto ao entardecer
    t0 = 28
    cena_deserto(c, t, "tarde")
    x = 1500 - (t - t0) * 60
    boneco(c, t, x, 1020, 0.85, look=-0.8, andar=True, fid=8, **FIGURINO["escriba"])
    historiador_i(c, t, 360, 1020, 1.0, poses=((0, "shrug"),), exprs=((0, "worried"),), look=0.4)
    rotulo(c, t, t0 + 0.6, "ALEXANDRIA", "o túmulo perdido", x=800, y=180)


def s06(c, t):  # montanha nevada à noite
    t0 = 35
    cena_neve(c, t, "noite")
    historiador_i(c, t, 380, 1010, 1.05, poses=((0, "stand"),), exprs=((0, "shocked"),), look=0.7)
    for i, xx in enumerate((1050, 1230, 1400)):
        boneco(c, t, xx, 980 + i * 6, 0.62, look=0.8, andar=True, fid=20 + i, roupa="casaco",
               cor_roupa=[(0.62, 0.18, 0.16), (0.24, 0.34, 0.52), (0.36, 0.42, 0.30)][i], chapeu="gorro",
               cor_chapeu=(0.30, 0.30, 0.34), cabelo=None)
    rotulo(c, t, t0 + 0.8, "PASSO DYATLOV", "2 de fevereiro de 1959")


def s07(c, t):  # cidade colonial de dia
    t0 = 42
    luz("dia")
    ceu(c, t, passaros=True, seed=11)
    colinas(c, 640, 90, seed=3, col=(0.40, 0.56, 0.36), depth=0.4)
    casario(c, t, 880, "colonial", seed=12, h=(360, 460), w=(260, 360))
    chao(c, t, 880, "pedra", seed=3)
    figurantes(c, t, 930, n=7, s=0.34, seed=9, x0=600, x1=1850, figurinos=["cavalheiro", "dama", "medico"])
    boneco(c, t, 1180, 1040, 1.0, poses=((0, "present_l"),), exprs=((0, "confident"),), look=-0.5, fid=9,
           **FIGURINO["medico"])
    historiador_i(c, t, 360, 1040, 1.0, poses=((0, "stand"),), exprs=((0, "happy"),), look=0.6)
    rotulo(c, t, t0 + 0.6, "1903 · OSWALDO CRUZ", "Rio de Janeiro")


def s08(c, t):  # mar à noite com vapor
    t0 = 49
    cena_mar(c, t, "noite", navio="vapor")
    c.save(); c.translate(0, 0); c.restore()
    historiador_i(c, t, 330, 1040, 1.05, poses=((0, "point_r"), (t0 + 3, "think")), exprs=((0, "worried"), (t0 + 3, "think")), look=0.7)
    rotulo(c, t, t0 + 0.8, "MAR DO NORTE, 1899", "o navio que voltou sozinho", x=820, y=200)


def s09(c, t):  # a mesma vila à noite: janelas acesas, lanterna, vagalumes
    t0 = 56
    cena_vila(c, t, "noite", igreja_x=1560, seed=1)
    particulas(c, t, "vagalumes", 18)
    boneco(c, t, 1180 + (t - t0) * 45, 960, 0.6, look=0.8, andar=True, fid=31, **FIGURINO["monge"])
    historiador_i(c, t, 360, 1010, 1.05, poses=((0, "stand"), (t0 + 2, "finger_up")), exprs=((0, "neutral"), (t0 + 2, "think")), look=0.5)
    rotulo(c, t, t0 + 0.6, "A MESMA RUA, À NOITE", "a luz muda o clima da cena")


SCENES = [(0, 7, s01), (7, 14, s02), (14, 21, s03), (21, 28, s04), (28, 35, s05), (35, 42, s06), (42, 49, s07), (49, 56, s08), (56, 999.0, s09)]
