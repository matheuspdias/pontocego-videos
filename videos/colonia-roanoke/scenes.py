"""A Colônia Perdida de Roanoke (1587-1590). Vídeo longo do Ponto Cego, estilo ilustrado.
Narração Pedro Lima - Serious (HeyGen), 5 blocos; tempos absolutos (offsets em narracao_blocos.txt).
Fontes e fatos no roteiro.txt / youtube.txt."""
from engine import *
from ilustrado import *

STYLE = "ilustrado"
TOM = "misterioso"
THEME = "selva"
SFX_OFF = True
SFX = [(0.3, "tum"), (63.6, "boom"), (72.4, "boom"), (85.2, "tum"), (244.6, "heartbeat"), (333.9, "heartbeat"),
       (378.0, "bell"), (470.9, "boom"), (538.9, "heartbeat"), (573.2, "boom"), (613.6, "boom"),
       (748.4, "boom"), (807.1, "heartbeat"), (860.6, "tum"), (958.1, "tum"), (1100.3, "boom")]


# ------------------------------------------------------------------ ajudantes
def eob(p):
    return max(0.01, ease_out_back(p))


def HI(c, t, poses=((0, "stand"),), exprs=((0, "neutral"),), x=360, y=1040, s=1.0, look=0.6, **kw):
    historiador_i(c, t, x, y, s, poses=poses, exprs=exprs, look=look, **kw)


def grande(c, t, t0, s, x=960, y=200, size=100, col=(0.98, 0.95, 0.88), t1=None):
    if t < t0 or (t1 is not None and t > t1):
        return
    p = ease_out(prog(t, t0, 0.4))
    c.save(); c.translate(0, 24 * (1 - p)); titulo_i(c, s, x, y, size, col); c.restore()


def pl(c, t, t0, x, y, tit, sub=None, size=48, t1=None, rot=0.0):
    """placa de pergaminho que entra com pop"""
    if t < t0 or (t1 is not None and t > t1):
        return
    k = eob(prog(t, t0, 0.45))
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(k, k); placa(c, tit, sub, size=size); c.restore()


def risca(c, t, t0, x, y, w=420):
    """X vermelho riscando algo"""
    if t < t0:
        return
    p = ease_out(prog(t, t0, 0.35))
    c.save(); c.translate(x, y)
    line(c, -w / 2, -w * 0.18, -w / 2 + w * p, -w * 0.18 + w * 0.36 * p, 12, (0.82, 0.16, 0.12))
    c.restore()


def nau_em(c, t, x, y, s=0.6, depth=0.0, **kw):
    c.save(); c.translate(x, y); nau(c, t, s, depth=depth, **kw); c.restore()


def conves(c, t):
    """convés de madeira em primeiro plano (o Historiador fica a bordo nas cenas de mar)"""
    chao(c, t, 960, "madeira", seed=5)
    c.rectangle(-20, 905, W + 40, 14); rgb(c, P(MADEIRA_ESC)); c.fill()
    for x in range(0, W + 60, 90):
        c.rectangle(x, 905, 10, 60); rgb(c, P(MADEIRA_ESC)); c.fill()


def mapa(c, t, x=1080, y=520, w=1240, h=720, **kw):
    c.save(); c.translate(x, y); mapa_white(c, t, w, h, **kw); c.restore()


def mesa_mapa(c, t, hora="vela"):
    luz(hora)
    interior(c, t, "madeira", "madeira", janela="reta", jx=1650, raio=False)


def colonos(c, t, x0, x1, y, n=6, s=0.55, seed=1, andar=False, mulheres=(1, 4), crianca=(2,), look=0.0, alpha=1.0):
    rnd = random.Random(seed)
    for i in range(n):
        xx = x0 + (x1 - x0) * i / max(1, n - 1) + rnd.uniform(-20, 20)
        ss = s * (0.62 if i in crianca else 1.0) * rnd.uniform(0.95, 1.05)
        fig = COLONO(i + seed, mulher=i in mulheres)
        boneco(c, t, xx, y + rnd.uniform(-6, 6), ss, look=look if look else rnd.uniform(-0.6, 0.6), fid=40 + i + seed,
               andar=andar, alpha=alpha, **fig)


def nativos(c, t, x0, x1, y, n=3, s=0.6, seed=2, look=0.0, andar=False):
    rnd = random.Random(seed)
    for i in range(n):
        xx = x0 + (x1 - x0) * i / max(1, n - 1)
        boneco(c, t, xx, y + rnd.uniform(-6, 6), s * rnd.uniform(0.95, 1.05), look=look or rnd.uniform(-0.6, 0.6),
               fid=60 + i + seed, andar=andar, **NATIVO(i + seed))


def ruinas(c, t, y=900, depth=0.0):
    """o lugar da vila em 1590: troncos e tábuas empilhados (casas desmontadas)"""
    rnd = random.Random(9)
    for i in range(5):
        x = 760 + i * 220 + rnd.uniform(-30, 30)
        for k in range(4):
            rr(c, x - 90 + k * 8, y - 18 - k * 16, 180 - k * 14, 16, 6)
            rgb(c, P((0.44, 0.31, 0.20) if k % 2 else (0.38, 0.27, 0.18), depth)); c.fill()


def fumaca_coluna(c, t, x, y, h=520, a=0.35):
    smoke(c, t, x, y, h, a, seed=3)


# ------------------------------------------------------------------ BLOCO 1 (0 - 192.9)
def s01(c, t):  # 0 - 9.25  o navio chega à ilha em 1590
    cena_praia_ilha(c, t, "crepusculo")
    k = ease_out(prog(t, 0.0, 8.0))
    nau_em(c, t, 1700 - 380 * k, 880, 0.4)
    HI(c, t, ((0, "point_r"),), ((0, "neutral"), (6.0, "worried")), look=0.6)
    grande(c, t, 0.4, "18 DE AGOSTO DE 1590", 1060, 170, 92)
    rotulo(c, t, 4.4, "JOHN WHITE", "desembarca numa ilha da América do Norte", x=760, y=300, size=60)


def s02(c, t):  # 9.25 - 18.36  aniversário da neta
    cena_ilha(c, t, "crepusculo", agua=True, chao_tipo="areia", seed=53)
    boneco(c, t, 1240, 1000, 1.0, poses=((0, "stand"), (13.4, "think")), exprs=((0, "happy"), (13.4, "sad")), look=-0.3, fid=5, **JOHN_WHITE)
    HI(c, t, ((0, "present"),), ((0, "neutral"),), look=0.6)
    pl(c, t, 9.6, 1100, 250, "3 ANOS", "ANIVERSÁRIO DA NETA", 64)
    if t > 13.4:
        k = eob(prog(t, 13.6, 0.4))
        c.save(); c.translate(1600, 500); c.scale(k, k)
        c.new_sub_path(); c.arc(0, 0, 120, 0, 6.283); rgb(c, (0.95, 0.90, 0.78), 0.92); c.fill()
        c.new_sub_path(); c.arc(0, 0, 120, 0, 6.283); rgb(c, AMBER); c.set_line_width(5); c.stroke()
        c.translate(20, 0); bebe_i(c, 1.1); c.restore()
        rotulo(c, t, 14.2, "A ÚLTIMA VEZ", "ela tinha 9 dias de vida", x=1440, y=700, size=46)
    particulas(c, t, "poeira", 18)


def s03(c, t):  # 18.36 - 38.24  três anos antes: mais de cem pessoas na praia
    cena_ilha(c, t, "sepia", agua=True, chao_tipo="areia", seed=54)
    k = ease_out(prog(t, 33.2, 4.5))
    nau_em(c, t, 1500 + 500 * k, 680, 0.32, depth=0.4)
    colonos(c, t, 720, 1700, 960, n=8, s=0.62, seed=3, mulheres=(1, 4, 6), crianca=(2, 5))
    HI(c, t, ((0, "stand"), (25.0, "present")), ((0, "think"), (25.0, "neutral")), look=0.6)
    grande(c, t, 18.5, "1587", 1200, 180, 120)
    pl(c, t, 22.0, 1200, 330, "MAIS DE 100 PESSOAS", "HOMENS, MULHERES E CRIANÇAS", 52, t1=33.0)
    pl(c, t, 33.2, 1200, 330, "\"VOLTO EM POUCOS MESES\"", "A PROMESSA", 52)


def s04(c, t):  # 38.24 - 55.84  ninguém
    cena_ilha(c, t, "nublado", agua=False, seed=55)
    palicada_i(c, t, 600, 1900, 880, 260, depth=0.15, portao=1250)
    if t > 47.2:
        ruinas(c, t, 960)
    nevoa_i(c, t, 860, 0.35)
    HI(c, t, ((0, "stand"), (42.4, "shrug")), ((0, "worried"), (50.2, "shocked")), look=0.6)
    grande(c, t, 38.5, "NINGUÉM", 1200, 220, 130)
    lines = [(42.4, "nenhuma voz"), (44.6, "nenhum fogo"), (46.0, "nenhum barco"), (50.2, "nenhum túmulo")]
    for i, (tt, s_) in enumerate(lines):
        if t > tt:
            p = ease_out(prog(t, tt, 0.4))
            c.save(); c.translate(1500 - 30 * (1 - p), 340 + i * 62)
            c.select_font_face(TYPE); c.set_font_size(44)
            c.move_to(2, 3); rgb(c, (0, 0, 0), 0.5 * p); c.show_text(s_)
            c.move_to(0, 0); rgb(c, (0.97, 0.94, 0.86), p); c.show_text(s_); c.restore()


def s05(c, t):  # 55.84 - 66.09  a árvore com CRO
    cena_ilha(c, t, "nublado", agua=False, seed=56, arvores=False)
    tronco_entalhado(c, t, 1300, 1100, 1000, 230, "CRO", p=prog(t, 63.4, 2.0))
    HI(c, t, ((0, "think"), (63.6, "point_r")), ((0, "think"), (63.6, "shocked")), look=0.6)
    grande(c, t, 56.0, "SÓ UMA PISTA", 760, 200, 84)
    nevoa_i(c, t, 940, 0.3)


def s06(c, t):  # 66.09 - 74.07  CROATOAN no poste
    cena_ilha(c, t, "crepusculo", agua=False, seed=57)
    palicada_i(c, t, 500, 1950, 900, 330, portao=1240, seed=7)
    poste_entalhado(c, t, 1330, 980, 640, 160, "CROATOAN", p=prog(t, 72.2, 1.4))
    HI(c, t, ((0, "point_r"),), ((0, "worried"), (72.4, "shocked")), look=0.6)
    nevoa_i(c, t, 940, 0.3)
    if t > 72.6:
        rglow(c, 1330, 640, 300, (1.0, 0.85, 0.5), 0.25 * prog(t, 72.6, 0.8))


def s07(c, t):  # 74.07 - 85.10  115 pessoas sumiram
    cena_ilha(c, t, "noite", agua=True, seed=58)
    a = 1 - prog(t, 75.0, 3.0)
    if a > 0.02:
        colonos(c, t, 700, 1700, 960, n=8, s=0.6, seed=3, mulheres=(1, 4, 6), crianca=(2, 5), alpha=a)
    HI(c, t, ((0, "stand"), (78.1, "shrug")), ((0, "worried"), (78.1, "sad")), look=0.6)
    grande(c, t, 74.3, "115 PESSOAS", 1000, 300, 120)
    grande(c, t, 78.2, "MAIS DE 400 ANOS DEPOIS...", 1000, 440, 60, col=(0.98, 0.82, 0.50))
    if t > 80.5:
        show(c, t, 80.5, 1000, 680, sc(big_q, 160))
    nevoa_i(c, t, 900, 0.3)


def s08(c, t):  # 85.10 - 89.34  título
    cena_ilha(c, t, "noite", agua=False, seed=59)
    palicada_i(c, t, 300, 1700, 900, 300, depth=0.3, portao=1000, seed=11)
    poste_entalhado(c, t, 1640, 960, 440, 100, "CROATOAN", depth=0.3)
    nevoa_i(c, t, 880, 0.45)
    if t > 85.3:
        p = ease_out(prog(t, 85.3, 1.2))
        rglow(c, 960, 420, 600, AMBER, 0.25 * p)
        c.save(); c.translate(0, 20 * (1 - p))
        titulo_i(c, "A COLÔNIA PERDIDA", 900, 380, 120, col=(1.0, 0.86, 0.55))
        titulo_i(c, "DE ROANOKE", 900, 520, 140)
        c.restore()


def s09(c, t):  # 89.34 - 108.78  Inglaterra, década de 1580
    cena_vila(c, t, "dia", estilo="pedra", seed=12, igreja_x=1500)
    figurantes(c, t, 930, n=6, s=0.32, seed=4, x0=700, x1=1800, figurinos=["campones", "camponesa", "cavalheiro"])
    boneco(c, t, 1250, 1040, 1.0, poses=((0, "present_l"),), exprs=((0, "confident"),), look=-0.4, fid=7,
           roupa="vestido", cor_roupa=(0.86, 0.84, 0.80), capa=(0.60, 0.12, 0.14), cabelo="cacheado", cor_cabelo=(0.72, 0.36, 0.18),
           chapeu="coroa", mulher=True)
    HI(c, t, ((0, "stand"), (94.2, "present")), ((0, "neutral"),), look=0.6)
    rotulo(c, t, 89.8, "INGLATERRA, DÉCADA DE 1580", "a rainha Elizabeth I", x=760, y=180, size=58)
    pl(c, t, 101.7, 1560, 420, "A ESPANHA NA FRENTE", "E OS INGLESES FICANDO PARA TRÁS", 40)


def s10(c, t):  # 108.78 - 131.59  1584: Walter Raleigh
    cena_interior(c, t, "interior", "salao", seed=13)
    boneco(c, t, 1500, 1040, 1.0, poses=((0, "present_l"),), exprs=((0, "confident"),), look=-0.6, fid=7,
           roupa="vestido", cor_roupa=(0.86, 0.84, 0.80), capa=(0.60, 0.12, 0.14), cabelo="cacheado", cor_cabelo=(0.72, 0.36, 0.18),
           chapeu="coroa", mulher=True)
    boneco(c, t, 1100, 1040, 1.0, poses=((0, "stand"), (117.0, "hold")), exprs=((0, "happy"),), look=0.6, fid=8,
           roupa="jaqueta", cor_roupa=(0.82, 0.78, 0.66), cor_calca=(0.30, 0.22, 0.16), barba="cavanhaque", bigode=True,
           chapeu="boina", cor_chapeu=(0.16, 0.14, 0.14), capa=(0.30, 0.20, 0.42))
    HI(c, t, ((0, "think"), (121.9, "finger_up")), ((0, "think"), (121.9, "confident")), look=0.6)
    rotulo(c, t, 109.0, "1584 · WALTER RALEIGH", "autorização da rainha", x=700, y=180, size=58)
    pl(c, t, 121.9, 960, 360, "NUNCA PISOU NA COLÔNIA", None, 42, t1=125.0)
    pl(c, t, 125.1, 960, 360, "2 NAVIOS PARA A AMÉRICA", "CAROLINA DO NORTE", 42)


def s11(c, t):  # 131.59 - 146.50  geografia: ilhas-barreira e Roanoke
    luz("sepia")
    lgrad(c, 0, 0, 0, H, [(0, P((0.36, 0.28, 0.20)), 1), (1, P((0.20, 0.15, 0.11)), 1)]); c.rectangle(0, 0, W, H); c.fill()
    mapa(c, t, 1100, 520, 1300, 760)
    HI(c, t, ((0, "point_r"),), ((0, "neutral"), (139.2, "confident")), look=0.6, s=0.95)
    if t > 139.2:
        k = eob(prog(t, 139.2, 0.5))
        c.save(); c.translate(1160, 510); c.scale(k, k)
        c.new_sub_path(); c.arc(0, 0, 70, 0, 6.283); rgb(c, (0.85, 0.20, 0.14)); c.set_line_width(7); c.stroke(); c.restore()
        pl(c, t, 139.6, 1500, 860, "ILHA DE ROANOKE", "UNS 12 KM, COBERTA DE FLORESTA", 40)


def s12(c, t):  # 146.50 - 157.35  povos algonquinos
    cena_ilha(c, t, "dia", agua=True, seed=60, arvores=False)
    aldeia_i(c, t, 900, seed=41, depth=0.15)
    nativos(c, t, 820, 1650, 1010, n=4, s=0.66, seed=1)
    HI(c, t, ((0, "present"),), ((0, "happy"),), look=0.6)
    rotulo(c, t, 147.0, "POVOS ALGONQUINOS", "milho, pesca e aldeias com paliçada", x=760, y=180, size=58)
    particulas(c, t, "poeira", 20)


def s13(c, t):  # 157.35 - 178.39  Manteo e Wanchese vão à Inglaterra
    cena_porto(c, t, "tarde", seed=14)
    boneco(c, t, 1150, 1040, 0.95, poses=((0, "stand"), (165.7, "wave")), exprs=((0, "happy"),), look=-0.3, fid=61, **NATIVO(0))
    boneco(c, t, 1550, 1040, 0.95, poses=((0, "stand"),), exprs=((0, "neutral"), (173.4, "think")), look=-0.5, fid=62, **NATIVO(1))
    HI(c, t, ((0, "stand"), (161.9, "present")), ((0, "neutral"),), look=0.6)
    rotulo(c, t, 157.6, "DOIS HOMENS DA TERRA", "levados para a Inglaterra", x=700, y=180, size=56)
    if t > 165.7:
        c.save(); c.translate(1150, 470); placa(c, "MANTEO", "DE CROATOAN", size=40); c.restore()
    if t > 173.4:
        c.save(); c.translate(1560, 470); placa(c, "WANCHESE", "DE ROANOKE", size=40); c.restore()


def s14(c, t):  # 178.39 - 193.9  aliado x desconfiança
    cena_ilha(c, t, "tarde", agua=True, seed=61)
    boneco(c, t, 920, 1030, 0.95, poses=((0, "stand"), (183.6, "present")), exprs=((0, "happy"),), look=0.6, fid=61, **NATIVO(0))
    boneco(c, t, 1150, 1030, 0.95, poses=((0, "stand"),), exprs=((0, "happy"),), look=-0.6, fid=41, **COLONO(2))
    boneco(c, t, 1620, 1030, 0.95, poses=((0, "stand"), (188.0, "hips")), exprs=((0, "neutral"), (188.0, "angry")), look=-0.7, fid=62, **NATIVO(1))
    HI(c, t, ((0, "stand"), (183.6, "think")), ((0, "neutral"), (188.0, "worried")), look=0.6, x=330)
    pl(c, t, 183.6, 1040, 300, "MANTEO: ALIADO", None, 40)
    pl(c, t, 188.0, 1560, 440, "WANCHESE: DESCONFIANÇA", None, 34)


# ------------------------------------------------------------------ BLOCO 2 (193.9 - 397.1)
def s15(c, t):  # 193.9 - 206.2  1585: a colônia de Ralph Lane
    cena_praia_ilha(c, t, "dia", seed=62)
    nau_em(c, t, 1600, 800, 0.5)
    for i in range(5):
        boneco(c, t, 780 + i * 170, 1040 - (i % 2) * 20, 0.7, look=0.4, fid=70 + i, andar=t < 199, **FIGURINO["soldado"])
    HI(c, t, ((0, "present"),), ((0, "neutral"),), look=0.6)
    rotulo(c, t, 194.3, "1585 · RALPH LANE", "a primeira tentativa", x=760, y=180, size=58)
    pl(c, t, 199.0, 1450, 400, "CERCA DE 108 HOMENS", "QUASE TODOS SOLDADOS", 44)


def s16(c, t):  # 206.2 - 226.9  Thomas Harriot e John White
    cena_ilha(c, t, "tarde", agua=True, seed=63)
    # cavalete com a pintura de uma aldeia
    c.save(); c.translate(1500, 980)
    line(c, -90, 0, -40, -460, 10, P(MADEIRA)); line(c, 90, 0, 40, -460, 10, P(MADEIRA))
    rr(c, -170, -520, 340, 260, 6); rgb(c, (0.95, 0.92, 0.84)); c.fill()
    c.rectangle(-150, -500, 300, 120); rgb(c, (0.66, 0.80, 0.86)); c.fill()
    c.rectangle(-150, -380, 300, 100); rgb(c, (0.62, 0.72, 0.42)); c.fill()
    pk = prog(t, 218.0, 4.0)
    for i in range(int(4 * pk) + 1 if t > 218 else 0):
        casa_arco(c, -110 + i * 72, -300, 60, 40)
    c.restore()
    boneco(c, t, 1260, 1040, 0.95, poses=((0, "hold"),), exprs=((0, "think"),), look=0.7, fid=5, **JOHN_WHITE)
    boneco(c, t, 900, 1040, 0.95, poses=((0, "think"), (212.0, "present")), exprs=((0, "think"), (212.0, "happy")), look=0.5, fid=9,
           roupa="jaqueta", cor_roupa=(0.30, 0.36, 0.30), chapeu="boina", cor_chapeu=(0.12, 0.12, 0.12), barba="curta")
    HI(c, t, ((0, "stand"),), ((0, "neutral"),), look=0.6, x=330)
    pl(c, t, 211.9, 900, 380, "THOMAS HARRIOT", "CIENTISTA", 38)
    pl(c, t, 218.0, 1500, 300, "JOHN WHITE", "ARTISTA", 38)


def s17(c, t):  # 226.9 - 252.3  o fracasso de Lane
    cena_ilha(c, t, "crepusculo", agua=False, seed=64)
    palicada_i(c, t, 1150, 1950, 900, 260, depth=0.2, seed=13)
    for i in range(3):
        boneco(c, t, 820 + i * 170, 1030, 0.72, poses=((0, "slump" if False else "stand"),), exprs=((0, "sad"),), look=0.3, fid=70 + i, **FIGURINO["soldado"])
    HI(c, t, ((0, "stand"), (240.2, "shrug")), ((0, "worried"), (244.6, "sad")), look=0.6)
    pl(c, t, 227.2, 1450, 260, "UM FRACASSO", None, 52)
    if t > 231.2:
        c.save(); c.translate(1450, 400); c.select_font_face(TYPE); c.set_font_size(38)
        for i, (tt, s_) in enumerate(((231.2, "não sabiam plantar"), (233.5, "dependiam das aldeias"), (240.2, "ataques dos dois lados"))):
            if t > tt:
                e = c.text_extents(s_); c.move_to(-e.x_advance / 2 + 2, i * 56 + 3); rgb(c, (0, 0, 0), 0.5); c.show_text(s_)
                c.move_to(-e.x_advance / 2, i * 56); rgb(c, (0.97, 0.94, 0.86)); c.show_text(s_)
        c.restore()
    rotulo(c, t, 244.8, "1586", "os ingleses matam Wingina, líder de Roanoke", x=1150, y=620, size=54)
    if t > 244.6:
        escurecer(c, 0.25 * prog(t, 244.6, 1.5))


def s18(c, t):  # 252.3 - 274.3  Drake leva os colonos; ficam 15 homens
    if t < 263.3:
        cena_mar(c, t, "tarde", seed=15)
        for i, (xx, yy, ss) in enumerate(((600, 700, 0.28), (900, 690, 0.24), (1700, 720, 0.34))):
            nau_em(c, t + i, xx, yy, ss, depth=0.3)
        conves(c, t)
        HI(c, t, ((0, "point_r"),), ((0, "neutral"),), look=0.6)
        rotulo(c, t, 252.6, "FRANCIS DRAKE", "e os colonos vão embora com ele", x=700, y=180, size=58)
    else:
        cena_ilha(c, t, "nublado", agua=True, seed=65)
        palicada_i(c, t, 1100, 1900, 900, 240, depth=0.2, seed=14)
        for i in range(5):
            boneco(c, t, 860 + i * 120, 1010, 0.5, look=0.2, fid=80 + i, **FIGURINO["soldado"])
        HI(c, t, ((0, "present"),), ((0, "worried"),), look=0.6)
        pl(c, t, 266.9, 1400, 330, "15 HOMENS FICAM", "PARA GUARDAR A POSSE", 46)


def s19(c, t):  # 274.3 - 297.7  a segunda tentativa: famílias
    cena_porto(c, t, "dia", seed=16)
    colonos(c, t, 760, 1700, 1020, n=9, s=0.62, seed=5, andar=False, mulheres=(1, 3, 6), crianca=(2, 7))
    HI(c, t, ((0, "stand"), (283.3, "present")), ((0, "neutral"), (283.3, "happy")), look=0.6)
    rotulo(c, t, 274.5, "1587 · A SEGUNDA TENTATIVA", "famílias inteiras", x=700, y=180, size=56)
    if t > 292.4:
        c.save(); c.translate(1300, 400); c.scale(eob(prog(t, 292.4, 0.5)), eob(prog(t, 292.4, 0.5)))
        placa(c, "JOHN WHITE", "O GOVERNADOR", size=46); c.restore()


def s20(c, t):  # 297.7 - 314.8  o plano: Chesapeake
    mesa_mapa(c, t, "vela")
    mapa(c, t, 1100, 520, 1240, 720, rota=[("roanoke", "chesapeake", prog(t, 304.5, 4.0))])
    HI(c, t, ((0, "think"), (304.5, "point_r")), ((0, "think"), (304.5, "neutral")), look=0.6, s=0.95)
    pl(c, t, 300.0, 1100, 940, "NÃO ERA PARA FICAR EM ROANOKE", None, 40)


def s21(c, t):  # 314.8 - 333.9  Simão Fernandes recusa
    cena_praia_ilha(c, t, "tarde", seed=66)
    k = ease_out(prog(t, 326.0, 7.0))
    nau_em(c, t, 1450 + 300 * k, 820, 0.5)
    boneco(c, t, 1120, 1040, 0.95, poses=((0, "point_r"), (325.6, "hips")), exprs=((0, "angry"), (325.6, "confident")), look=0.5, fid=11,
           **FIGURINO["capitao"])
    colonos(c, t, 620, 900, 1030, n=3, s=0.6, seed=7, mulheres=(1,), crianca=(), look=0.6)
    HI(c, t, ((0, "stand"),), ((0, "worried"),), x=280, look=0.6)
    rotulo(c, t, 315.0, "JULHO DE 1587", "o piloto se recusa a seguir viagem", x=700, y=180, size=58)
    pl(c, t, 318.0, 1150, 360, "SIMÃO FERNANDES", "PILOTO PORTUGUÊS", 40)


def s22(c, t):  # 333.9 - 352.1  os 15 homens tinham sumido
    cena_ilha(c, t, "noite", agua=True, seed=67)
    palicada_i(c, t, 900, 1700, 900, 220, depth=0.25, portao=1300, seed=15)
    nevoa_i(c, t, 880, 0.45)
    HI(c, t, ((0, "stand"), (340.5, "point_r")), ((0, "shocked"), (340.5, "worried")), look=0.6)
    grande(c, t, 334.1, "DOS 15 HOMENS, NINGUÉM", 1020, 300, 72)
    pl(c, t, 338.4, 1250, 380, "SÓ OS OSSOS DE UM DELES", None, 40, t1=340.4)
    if t > 340.5:
        k = ease_out(prog(t, 340.5, 8.0))
        c.save(); c.translate(1700 - 400 * k, 640)
        c.move_to(-60, 0); c.line_to(60, 0); c.line_to(40, 16); c.line_to(-40, 16); c.close_path(); rgb(c, P(MADEIRA_ESC)); c.fill()
        c.restore()
        pl(c, t, 342.0, 1250, 380, "FUGIRAM DE BARCO", "SEGUNDO OS ALIADOS DE CROATOAN", 40)
    grande(c, t, 349.6, "NUNCA MAIS FORAM VISTOS", 1200, 960, 58, col=(0.98, 0.82, 0.50))


def s23(c, t):  # 352.1 - 367.3  George Howe; o medo
    cena_ilha(c, t, "crepusculo", agua=True, chao_tipo="areia", seed=68)
    c.save(); c.translate(1350, 650); c.rotate(math.sin(t) * 0.03)
    c.move_to(-90, 0); c.line_to(90, 0); c.line_to(60, 22); c.line_to(-60, 22); c.close_path(); rgb(c, P(MADEIRA_ESC)); c.fill()
    c.restore()
    c.save(); c.translate(-3000, 900)
    for k in range(6):
        c.move_to(-120 + k * 40, -60); c.curve_to(-100 + k * 40, -20, -130 + k * 40, 10, -110 + k * 40, 40)
        rgb(c, P((0.70, 0.62, 0.46)), 0.8); c.set_line_width(3); c.stroke()
    for k in range(4):
        c.move_to(-130, -50 + k * 28); c.curve_to(-40, -40 + k * 28, 40, -60 + k * 28, 120, -50 + k * 28)
        c.stroke()
    c.restore()
    HI(c, t, ((0, "stand"),), ((0, "worried"), (362.6, "sad")), look=0.6)
    rotulo(c, t, 354.9, "GEORGE HOWE", "morto enquanto pescava sozinho", x=700, y=180, size=58)
    grande(c, t, 362.6, "O MEDO TOMA CONTA DA ILHA", 1150, 420, 64, col=(0.98, 0.82, 0.50))
    nevoa_i(c, t, 900, 0.25)


def s24(c, t):  # 367.3 - 378.0  Manteo batizado
    cena_ilha(c, t, "dia", agua=True, seed=69)
    boneco(c, t, 1150, 1030, 0.95, poses=((0, "stand"),), exprs=((0, "happy"),), look=0.5, fid=61, **NATIVO(0))
    boneco(c, t, 1420, 1030, 0.95, poses=((0, "present_l"),), exprs=((0, "happy"),), look=-0.5, fid=12, **FIGURINO["padre"])
    HI(c, t, ((0, "stand"), (371.2, "present")), ((0, "neutral"), (371.2, "happy")), look=0.6)
    rotulo(c, t, 367.6, "MOMENTOS DE ESPERANÇA", None, x=700, y=180, size=58)
    pl(c, t, 371.3, 1290, 380, "MANTEO É BATIZADO", "\"SENHOR DE ROANOKE\"", 42)
    particulas(c, t, "poeira", 20)


def s25(c, t):  # 378.0 - 397.1  Virginia Dare
    cena_interior(c, t, "vela", "cela", seed=17)
    boneco(c, t, 1250, 1040, 0.95, poses=((0, "hold"),), exprs=((0, "happy"),), look=0.3, fid=42, **COLONO(1, True))
    c.save(); c.translate(1290, 790); bebe_i(c, 0.9); c.restore()
    vela_i(c, t, 1560, 900, 1.0)
    HI(c, t, ((0, "stand"), (387.9, "present")), ((0, "neutral"), (387.9, "happy")), look=0.6)
    rotulo(c, t, 378.3, "18 DE AGOSTO DE 1587", "Eleanor Dare, filha de John White", x=700, y=180, size=56)
    pl(c, t, 387.9, 1250, 470, "VIRGINIA DARE", "PRIMEIRA CRIANÇA INGLESA NAS AMÉRICAS", 50)


# ------------------------------------------------------------------ BLOCO 3 (397.1 - 656.0)
def s26(c, t):  # 397.1 - 417.3  falta comida; alguém precisa voltar
    cena_ilha(c, t, "nublado", agua=False, seed=70, chao_tipo="terra")
    c.save(); c.translate(1150, 960); bau_i(c, 0, 0, 0.6, aberto=True); c.restore()
    colonos(c, t, 820, 1200, 1030, n=3, s=0.66, seed=9, mulheres=(1,), crianca=())
    boneco(c, t, 1550, 1040, 0.9, poses=((0, "stand"), (410.4, "think")), exprs=((0, "worried"),), look=-0.5, fid=5, **JOHN_WHITE)
    HI(c, t, ((0, "stand"),), ((0, "worried"),), look=0.6, x=330)
    pl(c, t, 397.6, 1300, 300, "TARDE DEMAIS PARA PLANTAR", "E O INVERNO CHEGANDO", 42, t1=405.6)
    pl(c, t, 405.9, 1300, 300, "ALGUÉM PRECISA VOLTAR", "E TRAZER AJUDA", 42)


def s27(c, t):  # 417.3 - 427.0  White não queria ir
    cena_interior(c, t, "vela", "escritorio", seed=18)
    vela_i(c, t, 1600, 860, 1.0)
    boneco(c, t, 1250, 1040, 1.0, poses=((0, "think"), (425.0, "stand")), exprs=((0, "worried"), (425.0, "sad")), look=-0.4, fid=5, **JOHN_WHITE)
    HI(c, t, ((0, "think"),), ((0, "think"),), look=0.6)
    pl(c, t, 420.2, 1250, 300, "\"VÃO DIZER QUE EU ABANDONEI A COLÔNIA\"", None, 34)


def s28(c, t):  # 427.0 - 447.0  o sinal combinado
    cena_ilha(c, t, "tarde", agua=False, seed=71)
    poste_entalhado(c, t, 1150, 990, 560, 150, "?", p=1.0 if t > 432.0 else 0.0)
    if t > 439.8:
        k = eob(prog(t, 439.8, 0.5))
        c.save(); c.translate(1560, 620); c.scale(k, k)
        line(c, -70, 0, 70, 0, 22, (0.82, 0.16, 0.12)); line(c, 0, -90, 0, 90, 22, (0.82, 0.16, 0.12)); c.restore()
    HI(c, t, ((0, "stand"), (432.0, "point_r")), ((0, "neutral"), (439.8, "worried")), look=0.6)
    rotulo(c, t, 427.3, "O SINAL COMBINADO", None, x=700, y=180, size=60)
    pl(c, t, 432.0, 1150, 320, "O NOME DO LUGAR", "SE SAÍSSEM DA ILHA", 40)
    pl(c, t, 441.0, 1560, 840, "+ CRUZ = PERIGO", None, 40)


def s29(c, t):  # 447.0 - 456.7  White embarca
    cena_praia_ilha(c, t, "tarde", seed=72)
    k = ease_out(prog(t, 447.0, 9.0))
    nau_em(c, t, 1300 + 450 * k, 820, 0.5)
    colonos(c, t, 600, 1100, 1040, n=4, s=0.62, seed=11, mulheres=(1, 2), crianca=(), look=0.7)
    HI(c, t, ((0, "stand"),), ((0, "sad"),), x=300, look=0.6)
    rotulo(c, t, 447.3, "AGOSTO DE 1587", "John White embarca para a Inglaterra", x=700, y=180, size=58)
    pl(c, t, 453.1, 1300, 380, "A NETA TINHA 9 DIAS", None, 46)


def s30(c, t):  # 456.7 - 470.9  Inglaterra à beira da guerra
    cena_porto(c, t, "nublado", seed=19)
    HI(c, t, ((0, "stand"), (460.6, "point_r")), ((0, "worried"),), look=0.6)
    grande(c, t, 457.0, "INGLATERRA X ESPANHA", 1150, 200, 84)
    pl(c, t, 465.5, 1150, 380, "NENHUM NAVIO GRANDE SAI", "ORDEM DA RAINHA", 44)


def s31(c, t):  # 470.9 - 479.6  a Invencível Armada
    luz("tempestade")
    ceu(c, t, seed=20)
    mar_i(c, t, 600)
    for i in range(9):
        xx = 400 + (i % 5) * 320 + (i // 5) * 160
        yy = 680 + (i // 5) * 120
        nau_em(c, t + i, xx, yy, 0.22 + 0.08 * (i // 5), depth=0.5 - 0.2 * (i // 5), cruz=False, vela=(0.80, 0.72, 0.58))
    conves(c, t)
    HI(c, t, ((0, "point_r"),), ((0, "shocked"),), look=0.6)
    grande(c, t, 471.2, "A INVENCÍVEL ARMADA", 1150, 200, 84, col=(0.98, 0.82, 0.50))
    relampago(c, t, (473.0,))


def s32(c, t):  # 479.6 - 505.8  1588: piratas; mais dois anos
    if t < 495.6:
        luz("nublado"); ceu(c, t, seed=21); mar_i(c, t, 640)
        nau_em(c, t, 1400, 780, 0.36, depth=0.2)
        if t > 486.5:
            nau_em(c, t, 900, 760, 0.32, depth=0.2, vela=(0.30, 0.28, 0.28), cruz=False)
        conves(c, t)
        HI(c, t, ((0, "stand"), (486.5, "point_r")), ((0, "neutral"), (486.5, "shocked")), look=0.6)
        rotulo(c, t, 479.8, "1588", "dois navios pequenos", x=700, y=180, size=64)
        pl(c, t, 486.6, 1200, 360, "ATACADOS POR PIRATAS FRANCESES", None, 40, t1=492.9)
        pl(c, t, 493.0, 1200, 360, "OS DOIS VOLTAM", None, 44)
    else:
        cena_vila(c, t, "nublado", estilo="pedra", seed=22)
        boneco(c, t, 1250, 1040, 0.95, poses=((0, "think"),), exprs=((0, "sad"),), look=-0.4, fid=5, **JOHN_WHITE)
        HI(c, t, ((0, "stand"),), ((0, "sad"),), look=0.6)
        pl(c, t, 495.8, 1250, 300, "A ARMADA É DERROTADA", "MAS A GUERRA CONTINUA", 42, t1=501.2)
        pl(c, t, 501.4, 1250, 300, "+ 2 ANOS PRESO NA INGLATERRA", None, 40)


def s33(c, t):  # 505.8 - 520.3  1590: expedição de corsários
    luz("dia"); ceu(c, t, seed=23); mar_i(c, t, 640)
    nau_em(c, t, 1350, 800, 0.42, depth=0.1)
    nau_em(c, t + 1, 1750, 720, 0.24, depth=0.4)
    conves(c, t)
    HI(c, t, ((0, "present"),), ((0, "neutral"),), look=0.6)
    rotulo(c, t, 506.0, "1590", "uma expedição de corsários a caminho do Caribe", x=700, y=180, size=64)
    pl(c, t, 515.0, 1300, 400, "ROANOKE ERA UM DESVIO", None, 44)


def s34(c, t):  # 520.3 - 541.9  noite: fumaça, trombeta, ninguém responde
    cena_ilha(c, t, "noite", agua=True, chao_tipo="areia", seed=73)
    fumaca_coluna(c, t, 1350, 700, 520, 0.3)
    nau_em(c, t, 1720, 700, 0.3, depth=0.3)
    HI(c, t, ((0, "point_r"),), ((0, "neutral"), (531.0, "think"), (538.9, "worried")), look=0.6)
    rotulo(c, t, 520.5, "17 DE AGOSTO DE 1590", "os navios ancoram perto da ilha", x=700, y=180, size=56)
    if t > 531.0:
        show(c, t, 531.0, 1050, 560, sc(trumpet, s=0.8))
        for k in range(3):
            ph = ((t - 531.0) * 0.8 + k / 3) % 1
            c.save(); c.translate(1150 + ph * 300, 520 - ph * 80)
            c.select_font_face(SERIF); c.set_font_size(60); c.move_to(0, 0); rgb(c, (1, 0.9, 0.6), 0.8 * (1 - ph)); c.show_text("♪" if False else "~")
            c.restore()
    grande(c, t, 538.9, "NINGUÉM RESPONDEU", 1150, 420, 80, col=(0.98, 0.82, 0.50))
    nevoa_i(c, t, 880, 0.3)


def s35(c, t):  # 541.9 - 549.3  de manhã: pegadas na areia
    cena_ilha(c, t, "nublado", agua=True, chao_tipo="areia", seed=74)
    for i in range(10):
        if t > 545.0 + i * 0.25:
            x = 760 + i * 110; y = 990 + (12 if i % 2 else -12)
            ellipse(c, x, y, 22, 10); rgb(c, P(dk(AREIA, 0.35))); c.fill()
    HI(c, t, ((0, "stand"), (545.0, "point_r")), ((0, "neutral"),), look=0.6)
    rotulo(c, t, 542.1, "18 DE AGOSTO DE 1590", "o desembarque", x=700, y=180, size=56)
    pl(c, t, 545.2, 1300, 400, "PEGADAS DE GENTE DA REGIÃO", None, 40)


def s36(c, t):  # 549.3 - 556.3  a árvore: C R O
    cena_ilha(c, t, "nublado", agua=False, seed=75, arvores=False)
    tronco_entalhado(c, t, 1250, 1100, 1000, 230, "CRO", p=prog(t, 553.0, 1.5))
    HI(c, t, ((0, "point_r"),), ((0, "shocked"),), look=0.6)
    nevoa_i(c, t, 950, 0.25)


def s37(c, t):  # 556.3 - 567.4  a vila desmontada; a paliçada
    cena_ilha(c, t, "nublado", agua=False, seed=76)
    palicada_i(c, t, 650, 1950, 920, 380, portao=1300, seed=17)
    ruinas(c, t, 990)
    HI(c, t, ((0, "stand"), (559.2, "present")), ((0, "worried"),), look=0.6)
    pl(c, t, 559.3, 1300, 300, "CASAS DESMONTADAS", "NO LUGAR, UMA PALIÇADA DE TRONCOS", 42)


def s38(c, t):  # 567.4 - 574.8  CROATOAN
    cena_ilha(c, t, "nublado", agua=False, seed=77, arvores=False)
    palicada_i(c, t, 500, 1950, 920, 360, portao=1270, seed=18)
    poste_entalhado(c, t, 1360, 1000, 700, 170, "CROATOAN", p=prog(t, 572.6, 1.2))
    HI(c, t, ((0, "point_r"),), ((0, "worried"), (573.2, "shocked")), look=0.6)
    if t > 573.3:
        rglow(c, 1360, 650, 320, (1.0, 0.85, 0.5), 0.3 * prog(t, 573.3, 0.8))


def s39(c, t):  # 574.8 - 592.4  sem cruz: alívio. Croatoan, 80 km ao sul
    if t < 580.8:
        cena_ilha(c, t, "nublado", agua=False, seed=77, arvores=False)
        poste_entalhado(c, t, 1300, 1000, 700, 170, "CROATOAN")
        risca(c, t, 575.2, 1600, 620, 220)
        pl(c, t, 575.0, 1650, 380, "SEM CRUZ", None, 50)
        HI(c, t, ((0, "stand"), (577.3, "finger_up")), ((0, "think"), (577.3, "happy")), look=0.6)
    else:
        mesa_mapa(c, t, "vela")
        mapa(c, t, 1100, 520, 1240, 720, rota=[("roanoke", "croatoan", prog(t, 581.0, 4.0))])
        HI(c, t, ((0, "point_r"),), ((0, "confident"),), look=0.6, s=0.95)
        pl(c, t, 583.5, 1100, 950, "CROATOAN: A ILHA DE MANTEO, 80 KM AO SUL", None, 36)


def s40(c, t):  # 592.4 - 613.6  os baús revirados
    cena_ilha(c, t, "crepusculo", agua=False, seed=78, chao_tipo="terra")
    bau_i(c, 1050, 990, 1.0, aberto=True, revirado=t > 599.9)
    if t > 609.4:
        armadura_i(c, 1450, 1010, 0.8, ferrugem=min(1.0, prog(t, 609.4, 2.0)))
    HI(c, t, ((0, "stand"), (596.0, "point_r")), ((0, "neutral"), (599.9, "sad")), look=0.6)
    lines = [(603.1, "livros rasgados"), (605.6, "quadros e mapas estragados"), (609.4, "armadura enferrujada")]
    for i, (tt, s_) in enumerate(lines):
        if t > tt:
            p = ease_out(prog(t, tt, 0.4))
            c.save(); c.translate(1150 - 30 * (1 - p), 260 + i * 66); c.select_font_face(TYPE); c.set_font_size(46)
            c.move_to(2, 3); rgb(c, (0, 0, 0), 0.5 * p); c.show_text(s_)
            c.move_to(0, 0); rgb(c, (0.97, 0.94, 0.86), p); c.show_text(s_); c.restore()
    grande(c, t, 592.6, "UM DETALHE TRISTE", 1150, 170, 70, col=(0.98, 0.82, 0.50), t1=603.0)


def s41(c, t):  # 613.6 - 636.9  a tempestade; nunca chegou a Croatoan
    luz("tempestade")
    ceu(c, t, seed=24)
    mar_i(c, t, 640)
    c.save(); c.translate(1300, 780); c.rotate(math.sin(t * 1.7) * 0.06); nau(c, t, 0.5); c.restore()
    conves(c, t)
    HI(c, t, ((0, "stand"),), ((0, "worried"), (632.8, "sad")), look=0.6)
    relampago(c, t, (618.6, 622.0, 627.0))
    pl(c, t, 621.9, 1250, 260, "CABOS ARREBENTAM, ÂNCORAS PERDIDAS", None, 38, t1=632.7)
    grande(c, t, 632.8, "NUNCA CHEGOU A CROATOAN", 1150, 260, 74, col=(0.98, 0.82, 0.50))


def s42(c, t):  # 636.9 - 656.0  a carta de 1593
    cena_interior(c, t, "vela", "escritorio", seed=25)
    vela_i(c, t, 1550, 880, 1.0)
    c.save(); c.translate(1150, 640); c.rotate(-0.04); papel_nota(c, ["Irlanda, 1593", "...entrego a colônia", "à vontade de Deus."], 620, size=46, rasgado=False); c.restore()
    HI(c, t, ((0, "stand"), (650.7, "think")), ((0, "sad"),), look=0.6)
    rotulo(c, t, 637.2, "1593 · A CARTA", "John White nunca mais voltou", x=700, y=180, size=56)
    grande(c, t, 650.8, "E SOME DOS REGISTROS", 1150, 960, 60, col=(0.98, 0.82, 0.50))


# ------------------------------------------------------------------ BLOCO 4 (656.0 - 893.8)
def s43(c, t):  # 656.0 - 667.6  o que aconteceu?
    cena_ilha(c, t, "noite", agua=True, seed=79)
    poste_entalhado(c, t, 1700, 960, 520, 130, "CROATOAN", depth=0.15)
    show(c, t, 656.4, 1100, 520, sc(big_q, 200))
    HI(c, t, ((0, "think"),), ((0, "think"),), look=0.6)
    grande(c, t, 656.4, "O QUE ACONTECEU?", 960, 300, 90)
    pl(c, t, 661.1, 1100, 900, "VÁRIAS TEORIAS · NENHUMA PROVADA", None, 40)
    nevoa_i(c, t, 900, 0.35)


def s44(c, t):  # 667.6 - 689.8  teoria 1: foram para Croatoan
    cena_ilha(c, t, "dia", agua=True, seed=80, arvores=False)
    aldeia_i(c, t, 900, seed=43, depth=0.15)
    nativos(c, t, 900, 1300, 1010, n=2, s=0.66, seed=3)
    colonos(c, t, 1450, 1750, 1010, n=2, s=0.66, seed=13, mulheres=(1,), crianca=())
    HI(c, t, ((0, "present"),), ((0, "confident"),), look=0.6)
    if t < 674.1:
        c.save(); c.translate(1150, 300); placa(c, "TEORIA 1", "A MAIS SIMPLES", size=58); c.restore()
    else:
        rotulo(c, t, 674.2, "CROATOAN = HATTERAS", "viver com o povo de Manteo", x=700, y=180, size=58)
        pl(c, t, 681.2, 1300, 400, "MISTURADOS À COMUNIDADE", None, 40)


def s45(c, t):  # 689.8 - 715.7  John Lawson, 1709
    cena_interior(c, t, "vela", "escritorio", seed=26)
    vela_i(c, t, 1600, 880, 1.0)
    boneco(c, t, 1250, 1040, 0.95, poses=((0, "hold"),), exprs=((0, "think"),), look=0.5, fid=14,
           roupa="casaco", cor_roupa=(0.40, 0.28, 0.20), cabelo="longo", cor_cabelo="grisalho")
    HI(c, t, ((0, "stand"), (707.3, "finger_up")), ((0, "neutral"), (707.3, "think")), look=0.6)
    rotulo(c, t, 690.0, "1709 · JOHN LAWSON", "explorador inglês", x=700, y=180, size=56)
    pl(c, t, 696.0, 1300, 360, "\"ANTEPASSADOS BRANCOS QUE LIAM LIVROS\"", None, 34, t1=702.9)
    pl(c, t, 703.0, 1300, 360, "ALGUNS DE OLHOS CLAROS", None, 42, t1=707.2)
    pl(c, t, 707.3, 1300, 360, "RELATO DE SEGUNDA MÃO", None, 42)


def s46(c, t):  # 715.7 - 735.0  teoria 2: o mapa (Museu Britânico)
    luz("interior")
    interior(c, t, "pedra", "pedra", janela="gotica", jx=1700)
    mapa(c, t, 1100, 500, 1100, 640, remendo=1.0, estrela=0.0, rotulos=False)
    if t > 725.9:
        k = eob(prog(t, 725.9, 0.5))
        c.save(); c.translate(1100 - 550 + 630 * 1100 / 1300 * 0 + (-470) * 1100 / 1300 + 550, 500 + (-125) * 640 / 760); c.scale(k, k)
        c.new_sub_path(); c.arc(0, 0, 80, 0, 6.283); rgb(c, (0.85, 0.20, 0.14)); c.set_line_width(7); c.stroke(); c.restore()
    HI(c, t, ((0, "stand"), (719.4, "point_r")), ((0, "neutral"),), look=0.6)
    if t < 719.4:
        c.save(); c.translate(1100, 930); placa(c, "TEORIA 2", "UM MAPA", size=50); c.restore()
    else:
        pl(c, t, 719.5, 1100, 930, "MUSEU BRITÂNICO, LONDRES", "O MAPA DE JOHN WHITE", 40, t1=725.8)
        pl(c, t, 726.0, 1100, 930, "DOIS REMENDOS DE PAPEL", None, 42)


def s47(c, t):  # 735.0 - 764.4  2012: debaixo do remendo, um forte
    luz("vela")
    lgrad(c, 0, 0, 0, H, [(0, (0.10, 0.08, 0.07), 1), (1, (0.04, 0.03, 0.03), 1)]); c.rectangle(0, 0, W, H); c.fill()
    luzk = prog(t, 736.0, 3.0)
    rglow(c, 1100, 500, 900, (1.0, 0.92, 0.7), 0.35 * luzk)
    rem = 1.0 - 0.75 * prog(t, 742.5, 4.0)
    mapa(c, t, 1100, 500, 1100, 640, remendo=rem, estrela=prog(t, 748.4, 1.0), rotulos=t > 755.4,
         rota=[("roanoke", "sitiox", prog(t, 755.6, 3.0))])
    HI(c, t, ((0, "stand"), (742.4, "point_r")), ((0, "think"), (748.4, "shocked")), look=0.6)
    rotulo(c, t, 735.2, "2012", "o mapa examinado contra a luz", x=150, y=110, size=60)
    pl(c, t, 749.0, 1100, 940, "UM FORTE ESCONDIDO", "ESTRELA VERMELHA E AZUL", 44, t1=755.3)
    pl(c, t, 755.6, 1100, 940, "NO INTERIOR, A 80 KM DE ROANOKE", None, 40)


def s48(c, t):  # 764.4 - 789.2  por que esconder? Sítio X
    mesa_mapa(c, t, "vela")
    mapa(c, t, 1100, 500, 1100, 640, remendo=0.0, estrela=1.0, rota=[("roanoke", "sitiox", 1.0)])
    HI(c, t, ((0, "think"), (777.5, "finger_up")), ((0, "think"), (777.5, "neutral")), look=0.6)
    pl(c, t, 764.6, 1100, 940, "POR QUE ESCONDER O FORTE?", None, 42, t1=768.3)
    pl(c, t, 768.4, 1100, 940, "SEGREDO? OU UM PLANO QUE MUDOU?", None, 40, t1=777.4)
    pl(c, t, 777.5, 1100, 940, "\"MUDAR 80 KM PARA O INTERIOR\"", None, 40, t1=784.4)
    if t > 784.5:
        grande(c, t, 784.5, "SÍTIO X", 1100, 960, 110, col=(0.98, 0.82, 0.50))


def s49(c, t):  # 789.2 - 807.1  escavações no Sítio X
    cena_campo(c, t, "tarde", seed=27)
    c.rectangle(1000, 950, 600, 70); rgb(c, P((0.42, 0.30, 0.20))); c.fill()
    for i in range(3):
        c.save(); c.translate(1150 + i * 160, 990); shards(c, seed=i + 2, n=3, spread=40); c.restore()
    boneco(c, t, 1700, 1040, 0.85, poses=((0, "point_l"),), exprs=((0, "think"),), look=-0.6, fid=15, **FIGURINO["explorador"])
    HI(c, t, ((0, "stand"), (796.5, "shrug")), ((0, "neutral"), (796.5, "think")), look=0.6)
    rotulo(c, t, 789.4, "SÍTIO X", "cacos de cerâmica inglesa da época", x=700, y=180, size=60)
    pl(c, t, 796.5, 1300, 420, "PODIA VIR DO COMÉRCIO", None, 42, t1=800.1)
    pl(c, t, 800.2, 1300, 420, "NENHUMA PROVA DEFINITIVA", None, 42)


def s50(c, t):  # 807.1 - 822.6  teoria 3: Jamestown, 1607
    cena_ilha(c, t, "crepusculo", agua=True, seed=81)
    palicada_i(c, t, 950, 1800, 900, 260, depth=0.25, seed=19)
    for i, xx in enumerate((1100, 1300, 1550)):
        c.save(); c.translate(xx, 880); predio(c, -60, 0, 120, 120, estilo="medieval", depth=0.3, porta=False); c.restore()
    HI(c, t, ((0, "stand"), (811.1, "present")), ((0, "worried"),), look=0.6)
    if t < 811.1:
        c.save(); c.translate(1150, 300); placa(c, "TEORIA 3", "A MAIS SOMBRIA", size=58); c.restore()
    else:
        rotulo(c, t, 811.2, "1607 · JAMESTOWN", "relatos de colonos vivendo mais ao norte", x=700, y=180, size=58)


def s51(c, t):  # 822.6 - 840.4  Strachey e Powhatan: relatos de terceiros
    cena_interior(c, t, "vela", "escritorio", seed=28)
    vela_i(c, t, 1600, 880, 1.0)
    boneco(c, t, 1250, 1040, 0.95, poses=((0, "hold"),), exprs=((0, "think"),), look=0.5, fid=16,
           roupa="jaqueta", cor_roupa=(0.20, 0.22, 0.20), chapeu="boina", cor_chapeu=(0.1, 0.1, 0.1), barba="cavanhaque")
    HI(c, t, ((0, "stand"), (831.7, "finger_up")), ((0, "worried"), (831.7, "think")), look=0.6)
    rotulo(c, t, 822.8, "WILLIAM STRACHEY", "cronista inglês", x=700, y=180, size=58)
    pl(c, t, 825.5, 1250, 360, "\"POWHATAN DISSE QUE OS MANDOU MATAR\"", None, 32, t1=831.6)
    pl(c, t, 831.7, 1250, 360, "RELATOS DE TERCEIROS", "ESCRITOS ANOS DEPOIS · MUITO DISCUTIDOS", 40)


def s52(c, t):  # 840.4 - 869.0  teoria 4: os anéis dos ciprestes
    cena_ilha(c, t, "tarde", agua=True, seed=82, arvores=False)
    for i, xx in enumerate((1500, 1700, 1850)):
        arvore(c, t, xx, 900, 520, "cipreste", seed=i, depth=0.1)
    c.save(); c.translate(1080, 560); aneis_i(c, 280, hl=prog(t, 860.6, 1.0)); c.restore()
    HI(c, t, ((0, "stand"), (845.3, "point_r")), ((0, "think"), (860.6, "shocked")), look=0.6)
    if t < 845.3:
        c.save(); c.translate(1150, 300); placa(c, "A QUARTA PISTA", "VEM DAS ÁRVORES", size=58); c.restore()
    else:
        rotulo(c, t, 845.4, "1998", "os anéis de ciprestes muito antigos", x=700, y=150, size=60)
    if t > 860.6:
        pl(c, t, 860.8, 1150, 950, "1587 A 1589: A PIOR SECA EM 800 ANOS", None, 40)


def s53(c, t):  # 869.0 - 893.8  a seca: sem comida para dividir
    luz("tarde")
    ceu(c, t, nuvens=False, seed=29)
    colinas(c, 700, 30, seed=3, col=(0.62, 0.56, 0.36), depth=0.4)
    chao(c, t, 860, "terra", seed=4)
    for i in range(16):  # milharal seco
        x = 760 + i * 70
        c.move_to(x, 900); c.curve_to(x + 6, 820, x + 18, 780, x + 30 + 10 * math.sin(i), 760)
        rgb(c, P((0.62, 0.52, 0.30))); c.set_line_width(6); c.stroke()
    HI(c, t, ((0, "stand"), (877.7, "shrug")), ((0, "worried"),), look=0.6)
    grande(c, t, 869.2, "O PIOR MOMENTO POSSÍVEL", 1200, 200, 74, col=(0.98, 0.82, 0.50))
    pl(c, t, 874.6, 1250, 380, "AS PLANTAÇÕES FALHAVAM", None, 42, t1=877.6)
    pl(c, t, 877.7, 1250, 380, "NINGUÉM TINHA COMIDA PARA DIVIDIR", None, 38)
    if t > 884.4:
        grande(c, t, 884.4, "TALVEZ NÃO TIVESSEM COMO FICAR", 1150, 600, 54, col=(0.98, 0.82, 0.50))
    particulas(c, t, "poeira", 30)


# ------------------------------------------------------------------ BLOCO 5 (893.8 - fim)
def s54(c, t):  # 893.8 - 919.7  escavações em Hatteras (Mark Horton)
    cena_ilha(c, t, "dia", agua=True, chao_tipo="areia", seed=83)
    c.rectangle(900, 940, 700, 80); rgb(c, P((0.55, 0.42, 0.28))); c.fill()
    boneco(c, t, 1700, 1040, 0.9, poses=((0, "point_l"),), exprs=((0, "happy"),), look=-0.6, fid=17,
           roupa="camisa", cor_roupa=(0.62, 0.66, 0.70), cor_calca=(0.30, 0.30, 0.34), chapeu="explorador", cabelo="curto", idade=0.6)
    HI(c, t, ((0, "stand"), (911.4, "present")), ((0, "neutral"), (911.4, "happy")), look=0.6)
    rotulo(c, t, 894.2, "HATTERAS, A ANTIGA CROATOAN", "a equipe de Mark Horton", x=700, y=180, size=56)
    if t > 911.4:
        show(c, t, 911.4, 1000, 560, sc(espada_i, 1.0, s=1.0))
        show(c, t, 913.0, 1250, 600, sc(ardosia_i, 1.0, s=1.0))
    pl(c, t, 905.4, 1250, 360, "OBJETOS EUROPEUS DO FIM DO SÉC. XVI", None, 36, t1=911.3)


def s55(c, t):  # 919.7 - 944.1  o anel do leão: ouro? não, latão
    luz("interior")
    interior(c, t, "madeira", "madeira", janela="reta", jx=1680)
    show(c, t, 920.0, 1150, 520, sc(anel_leao, 1.5, s=1.0))
    HI(c, t, ((0, "stand"), (926.5, "think"), (932.8, "finger_up")), ((0, "neutral"), (926.5, "think"), (932.8, "confident")), look=0.6)
    rotulo(c, t, 920.0, "1998 · UM ANEL COM UM LEÃO", None, x=700, y=170, size=56)
    pl(c, t, 926.5, 1550, 380, "OURO?", None, 52)
    risca(c, t, 932.8, 1550, 380, 200)
    pl(c, t, 933.3, 1550, 560, "LATÃO", "COMUM NO COMÉRCIO", 48)
    if t > 940.8:
        grande(c, t, 940.8, "PODIA TER CHEGADO POR TROCA", 1150, 960, 56)


def s56(c, t):  # 944.1 - 969.2  2025: as lascas de ferro
    cena_ilha(c, t, "tarde", agua=True, chao_tipo="areia", seed=84, arvores=False)
    c.save(); c.translate(1100, 900); lascas_ferro(c, t, 520, 220, p=prog(t, 950.7, 3.0)); c.restore()
    if t > 958.1:
        c.save(); c.translate(1560, 1000); bigorna_i(c, t, 0.9); c.restore()
    HI(c, t, ((0, "stand"), (950.7, "point_r")), ((0, "neutral"), (950.7, "shocked")), look=0.6)
    rotulo(c, t, 944.3, "2025", "uma descoberta diferente", x=700, y=170, size=64)
    pl(c, t, 951.0, 1100, 420, "LASCAS MINÚSCULAS DE FERRO", None, 42, t1=958.0)
    pl(c, t, 958.1, 1100, 420, "RESÍDUO DE FERREIRO", "JUNTO COM OBJETOS INGLESES", 42)


def s57(c, t):  # 969.2 - 992.2  "ninguém troca lixo de forja"
    cena_ilha(c, t, "tarde", agua=True, seed=85, arvores=False)
    aldeia_i(c, t, 900, seed=45, depth=0.2, fogueira=False)
    c.save(); c.translate(1250, 1010); bigorna_i(c, t, 0.75); c.restore()
    boneco(c, t, 1060, 1030, 0.8, poses=((0, "hold"),), exprs=((0, "neutral"),), look=0.6, fid=18, **COLONO(3))
    if t > 986.5:
        poste_entalhado(c, t, 1720, 1000, 480, 110, "CROATOAN", depth=0.1)
    HI(c, t, ((0, "stand"), (973.1, "finger_up")), ((0, "confident"),), look=0.6)
    pl(c, t, 973.2, 1250, 300, "\"NINGUÉM TROCA LIXO DE FORJA\"", "MARK HORTON", 40, t1=983.3)
    pl(c, t, 983.4, 1250, 300, "\"A COLÔNIA NUNCA ESTEVE PERDIDA\"", None, 38)


def s58(c, t):  # 992.2 - 1020.7  os céticos
    luz("interior")
    interior(c, t, "madeira", "madeira", janela="reta", jx=1700)
    HI(c, t, ((0, "stand"), (995.6, "finger_up")), ((0, "neutral"), (995.6, "think")), look=0.6)
    grande(c, t, 992.4, "NEM TODO MUNDO CONCORDA", 1150, 170, 70)
    items = [(995.6, "AINDA NÃO PUBLICADO EM REVISTA"), (1001.9, "CADÊ A FORNALHA?"), (1005.5, "OUTROS EUROPEUS PASSAVAM ALI"),
             (1011.4, "FALTA UM TÚMULO OU O DNA")]
    for i, (tt, s_) in enumerate(items):
        pl(c, t, tt, 1150, 330 + i * 160, s_, None, 40, rot=0.01 * (-1) ** i)


def s59(c, t):  # 1020.7 - 1045.4  talvez tenham se dividido
    mesa_mapa(c, t, "vela")
    mapa(c, t, 1100, 500, 1100, 640, remendo=0.0, estrela=1.0,
         rota=[("roanoke", "croatoan", prog(t, 1029.3, 2.5)), ("roanoke", "sitiox", prog(t, 1032.9, 2.5))])
    HI(c, t, ((0, "think"), (1029.3, "point_r")), ((0, "think"), (1037.1, "sad")), look=0.6)
    pl(c, t, 1021.0, 1100, 940, "TALVEZ A RESPOSTA NÃO SEJA UMA SÓ", None, 40, t1=1037.0)
    pl(c, t, 1037.2, 1100, 940, "FOME, DOENÇA, CONFLITOS... SEM REGISTRO", None, 36)


def s60(c, t):  # 1045.4 - 1058.5  a lenda da corça branca
    cena_ilha(c, t, "noite", agua=False, seed=86)
    corca_i(c, t, 1300, 980, 1.0, branca=True, alpha=min(1.0, prog(t, 1049.5, 2.0)), look=-1)
    particulas(c, t, "vagalumes", 26)
    nevoa_i(c, t, 920, 0.4)
    HI(c, t, ((0, "stand"),), ((0, "neutral"), (1049.5, "think")), look=0.6)
    rotulo(c, t, 1045.6, "A LENDA", "Virginia Dare, a corça branca", x=700, y=180, size=60)


def s61(c, t):  # 1058.5 - 1080.2  ainda desaparecidos
    cena_ilha(c, t, "noite", agua=True, seed=87)
    poste_entalhado(c, t, 1700, 980, 560, 140, "CROATOAN")
    nevoa_i(c, t, 900, 0.45)
    HI(c, t, ((0, "stand"), (1073.1, "present")), ((0, "neutral"), (1066.8, "sad")), look=0.6)
    rotulo(c, t, 1058.7, "1607 · JAMESTOWN", "a primeira colônia inglesa permanente", x=700, y=180, size=58)
    grande(c, t, 1066.9, "CONTINUAM DESAPARECIDOS", 1100, 400, 66, col=(0.98, 0.82, 0.50))
    if t > 1073.1:
        c.save(); c.translate(950, 560); c.select_font_face(TYPE); c.set_font_size(46)
        for i, (tt, s_) in enumerate(((1073.1, "115 pessoas"), (1075.2, "1 menina de 9 dias"), (1077.4, "1 palavra"))):
            if t > tt:
                c.move_to(2, i * 58 + 3); rgb(c, (0, 0, 0), 0.5); c.show_text(s_)
                c.move_to(0, i * 58); rgb(c, (0.97, 0.94, 0.86)); c.show_text(s_)
        c.restore()


def s62(c, t):  # 1080.2 - 1100.25  e você?
    cena_ilha(c, t, "crepusculo", agua=True, seed=88)
    HI(c, t, ((0, "present"), (1082.0, "think"), (1096.8, "point_r")), ((0, "happy"), (1082.0, "think"), (1096.8, "happy")), look=0.6)
    grande(c, t, 1080.4, "E VOCÊ?", 1150, 190, 110)
    qs = [(1085.7, "CROATOAN?"), (1089.5, "O INTERIOR?"), (1091.6, "OUTRO LUGAR?")]
    for i, (tt, s_) in enumerate(qs):
        pl(c, t, tt, 1150 + (i - 1) * 60, 360 + i * 110, s_, None, 40, rot=0.02 * (-1) ** i)
    if t > 1096.8:
        pl(c, t, 1096.8, 1150, 760, "DEIXE SUA TEORIA NOS COMENTÁRIOS", None, 40)


def s63(c, t):  # 1100.25 - fim  encerramento
    cena_ilha(c, t, "noite", agua=True, seed=89)
    poste_entalhado(c, t, 1700, 960, 440, 100, "CROATOAN", depth=0.3)
    nevoa_i(c, t, 900, 0.4)
    HI(c, t, ((0, "stand"), (1100.4, "present"), (1103.2, "wave"), (1105.6, "stand")), ((0, "neutral"), (1101.8, "happy")), look=0.6)
    grande(c, t, 1100.4, "Eu sou o Historiador.", 1000, 300, 56, col=(0.98, 0.82, 0.50))
    show(c, t, 1102.0, 1000, 470, sc(subscribe_btn, t > 1103.5, s=0.9))
    show(c, t, 1102.4, 1330, 470, sc(bell, s=0.8), rot=math.sin(t * 18) * 0.2 * max(0, 1 - (t - 1102.4)))
    if t > 1103.0:
        p = ease_out(prog(t, 1103.0, 1.2))
        rglow(c, 1100, 700, 420, AMBER, 0.2 * p)
        titulo_i(c, "PONTO CEGO", 1100, 740, 110)
        c.rectangle(1100 - 300 * p, 770, 600 * p, 4); rgb(c, AMBER); c.fill()


SCENES = [
    (0.0, 9.25, s01), (9.25, 18.36, s02), (18.36, 38.24, s03), (38.24, 55.84, s04), (55.84, 66.09, s05),
    (66.09, 74.07, s06), (74.07, 85.10, s07), (85.10, 89.34, s08), (89.34, 108.78, s09), (108.78, 131.59, s10),
    (131.59, 146.50, s11), (146.50, 157.35, s12), (157.35, 178.39, s13), (178.39, 193.9, s14),
    (193.9, 206.2, s15), (206.2, 226.9, s16), (226.9, 252.3, s17), (252.3, 274.3, s18), (274.3, 297.7, s19),
    (297.7, 314.8, s20), (314.8, 333.9, s21), (333.9, 352.1, s22), (352.1, 367.3, s23), (367.3, 378.0, s24),
    (378.0, 397.1, s25),
    (397.1, 417.3, s26), (417.3, 427.0, s27), (427.0, 447.0, s28), (447.0, 456.7, s29), (456.7, 470.9, s30),
    (470.9, 479.6, s31), (479.6, 505.8, s32), (505.8, 520.3, s33), (520.3, 541.9, s34), (541.9, 549.3, s35),
    (549.3, 556.3, s36), (556.3, 567.4, s37), (567.4, 574.8, s38), (574.8, 592.4, s39), (592.4, 613.6, s40),
    (613.6, 636.9, s41), (636.9, 656.0, s42),
    (656.0, 667.6, s43), (667.6, 689.8, s44), (689.8, 715.7, s45), (715.7, 735.0, s46), (735.0, 764.4, s47),
    (764.4, 789.2, s48), (789.2, 807.1, s49), (807.1, 822.6, s50), (822.6, 840.4, s51), (840.4, 869.0, s52),
    (869.0, 893.8, s53),
    (893.8, 919.7, s54), (919.7, 944.1, s55), (944.1, 969.2, s56), (969.2, 992.2, s57), (992.2, 1020.7, s58),
    (1020.7, 1045.4, s59), (1045.4, 1058.5, s60), (1058.5, 1080.2, s61), (1080.2, 1100.25, s62), (1100.25, 9999.0, s63),
]
