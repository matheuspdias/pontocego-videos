"""Kaspar Hauser, o rapaz que saiu do escuro (Nuremberg 1828 - Ansbach 1833). Vídeo longo do Ponto Cego, estilo ilustrado.
Narração Pedro Lima - Serious (HeyGen), 4 blocos; tempos absolutos (offsets em narracao_blocos.txt:
B1=0.000  B2=199.474  B3=385.673  B4=587.328, fim ~853.94). Fontes no youtube.txt."""
from engine import *
from ilustrado import *
import cairo

STYLE = "ilustrado"
TOM = "misterioso"
THEME = "cidade"
SFX_OFF = True
SFX = [(0.3, "tum"), (61.9, "boom"), (74.1, "boom"), (115.0, "heartbeat"), (199.8, "heartbeat"), (253.2, "tum"),
       (320.4, "boom"), (351.1, "heartbeat"), (393.9, "bell"), (515.0, "heartbeat"), (543.5, "boom"),
       (584.5, "boom"), (607.4, "bell"), (796.6, "boom"), (844.4, "tum")]


# ------------------------------------------------------------------ ajudantes
def eob(p):
    return max(0.01, ease_out_back(p))


def HI(c, t, poses=((0, "stand"),), exprs=((0, "neutral"),), x=340, y=1040, s=1.0, look=0.6, **kw):
    historiador_i(c, t, x, y, s, poses=poses, exprs=exprs, look=look, **kw)


def grande(c, t, t0, s, x=1150, y=200, size=96, col=(0.98, 0.95, 0.88), t1=None):
    if t < t0 or (t1 is not None and t > t1):
        return
    p = ease_out(prog(t, t0, 0.4))
    c.save(); c.translate(0, 24 * (1 - p)); titulo_i(c, s, x, y, size, col); c.restore()


def pl(c, t, t0, x, y, tit, sub=None, size=46, t1=None, rot=0.0):
    """placa de pergaminho que entra com pop"""
    if t < t0 or (t1 is not None and t > t1):
        return
    k = eob(prog(t, t0, 0.45))
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(k, k)
    if sub:
        placa2(c, tit, sub, size)
    else:
        placa(c, tit, None, size=size)
    c.restore()


def placa2(c, l1, l2, size=46):
    """cartão de pergaminho com duas linhas lidas de cima para baixo (a segunda um pouco menor)"""
    s2 = size * 0.82
    c.select_font_face(SERIF, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(size); w1 = c.text_extents(l1).x_advance
    c.set_font_size(s2); w2 = c.text_extents(l2).x_advance
    w = max(w1, w2) + 80
    h = size * 1.6 + s2 * 1.5 + 40
    c.save(); c.rotate(-0.012)
    rr(c, -w / 2 + 6, -h / 2 + 8, w, h, 6); rgb(c, (0, 0, 0), 0.35); c.fill()
    rr(c, -w / 2, -h / 2, w, h, 6); rgb(c, (0.93, 0.88, 0.76)); c.fill()
    rr(c, -w / 2 + 10, -h / 2 + 10, w - 20, h - 20, 4); rgb(c, (0.55, 0.40, 0.22), 0.6); c.set_line_width(2); c.stroke()
    y1 = -h / 2 + 20 + size * 1.05
    c.select_font_face(SERIF, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(size)
    c.move_to(-w1 / 2, y1); rgb(c, (0.20, 0.13, 0.08)); c.show_text(l1)
    c.set_font_size(s2)
    c.move_to(-w2 / 2, y1 + s2 * 1.45); rgb(c, (0.42, 0.28, 0.14)); c.show_text(l2)
    c.restore()


def nota(c, t, t0, x, y, linhas, w=620, size=46, rot=-0.03, t1=None, font=None):
    if t < t0 or (t1 is not None and t > t1):
        return
    k = eob(prog(t, t0, 0.45))
    c.save(); c.translate(x, y); c.scale(k, k); papel_nota(c, linhas, w=w, size=size, rot=rot, font=font); c.restore()


def risca(c, t, t0, x, y, w=420):
    if t < t0:
        return
    p = ease_out(prog(t, t0, 0.35))
    c.save(); c.translate(x, y)
    line(c, -w / 2, -w * 0.18, -w / 2 + w * p, -w * 0.18 + w * 0.36 * p, 12, (0.82, 0.16, 0.12))
    c.restore()


def obj(c, t, t0, x, y, fn, s=1.0, t1=None):
    """objeto ilustrado que entra com pop (fn(c) desenha com origem no ponto)"""
    if t < t0 or (t1 is not None and t > t1):
        return
    k = eob(prog(t, t0, 0.45))
    c.save(); c.translate(x, y); c.scale(k * s, k * s); fn(c); c.restore()


def kaspar(c, t, x, y, s=0.9, poses=((0, "stand"),), exprs=((0, "neutral"),), look=-0.4, ansbach=False, cambaleia=False, **kw):
    fig = dict(KASPAR_ANSBACH if ansbach else KASPAR)
    fig.update(kw)
    if cambaleia:
        c.save(); c.translate(x, y); c.rotate(math.sin(t * 2.6) * 0.06); c.translate(-x, -y)
    boneco(c, t, x, y, s, poses=poses, exprs=exprs, look=look, fid=7, **fig)
    if cambaleia:
        c.restore()


def nuremberg(c, t, hora="tarde", seed=1, torre=True):
    cena_vila(c, t, hora, "medieval", seed=seed, igreja_x=1500)
    if torre:
        torre_castelo(c, 260, 700, 120, 330, depth=0.5)


def ansbach(c, t, hora="tarde", seed=21):
    cena_vila(c, t, hora, "colonial", seed=seed, igreja_x=1600)


def jardim(c, t, hora="crepusculo", neve=True, seed=31):
    """o jardim do palácio de Ansbach no inverno"""
    luz(hora)
    ceu(c, t, seed=seed)
    predio(c, 1450, 700, 700, 300, "colonial", col=(0.90, 0.84, 0.70), seed=4, depth=0.45)
    colinas(c, 720, 10, seed=seed, col=NEVE_C if neve else GRAMA, depth=0.4)
    for i, x in enumerate((140, 560, 980, 1400, 1800)):
        arvore(c, t, x, 800 + (i % 2) * 20, 300, "redonda", seed=seed + i, depth=0.25, seca=neve)
    chao(c, t, 860, "neve" if neve else "grama", seed=seed)


def carimbo(c, s_, size=44):
    """carimbo de data legível sobre qualquer fundo (papel claro translúcido por trás)"""
    c.select_font_face(TYPE); c.set_font_size(size)
    w = c.text_extents(s_).x_advance + 90
    c.save(); c.rotate(-0.05)
    rr(c, -w / 2, -size * 0.95, w, size * 1.9, 8); rgb(c, (0.96, 0.93, 0.85), 0.82); c.fill()
    c.restore()
    date_stamp(c, s_, size, (0.78, 0.14, 0.12))


def quarto_escuro_transicao(c, a):
    c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), a); c.fill()


# ------------------------------------------------------------------ BLOCO 1 (0 - 198.47)
def s01(c, t):  # 0 - 10.57  Nuremberg, feriado, ruas vazias
    nuremberg(c, t, "tarde", seed=2)
    particulas(c, t, "poeira", 20)
    HI(c, t, ((0, "present"),), ((0, "neutral"), (7.0, "think")))
    grande(c, t, 0.4, "26 DE MAIO DE 1828", 1100, 180, 86)
    rotulo(c, t, 4.0, "NUREMBERG", "Alemanha · um feriado", x=760, y=300, size=60)


def s02(c, t):  # 10.57 - 19.94  o sapateiro vê o rapaz
    nuremberg(c, t, "tarde", seed=3, torre=False)
    boneco(c, t, 1600, 1010, 0.92, poses=((0, "stand"), (12.5, "point_l")), exprs=((0, "neutral"), (12.5, "worried")),
           look=-0.6, fid=3, roupa="camisa", cor_roupa=(0.62, 0.52, 0.40), cor_calca=(0.32, 0.26, 0.20),
           cabelo="calvo", bigode=True, idade=0.4, cinto=(0.40, 0.28, 0.18))
    kaspar(c, t, 1180, 1010, 0.82, poses=((0, "slump"),), exprs=((0, "worried"),), look=0.5)
    HI(c, t, ((0, "point_r"),), ((0, "neutral"), (15.0, "worried")))
    rotulo(c, t, 11.0, "UM SAPATEIRO", "vê um rapaz parado na praça", x=760, y=180, size=56)
    pl(c, t, 15.2, 1180, 420, "UNS 16 ANOS", "MAL CONSEGUIA FICAR EM PÉ", 48)


def s03(c, t):  # 19.94 - 29.70  cambaleando, pés com bolhas
    nuremberg(c, t, "tarde", seed=4)
    k = prog(t, 19.94, 9.0)
    kaspar(c, t, 1500 - 300 * k, 1010, 0.82, poses=((0, "hold"),), exprs=((0, "worried"),), look=-0.6, cambaleia=True, andar=True)
    HI(c, t, ((0, "stand"),), ((0, "worried"),))
    pl(c, t, 20.2, 1150, 260, "COMO UMA CRIANÇA PEQUENA", "CAMBALEANDO", 46)
    pl(c, t, 24.7, 1150, 430, "PÉS CHEIOS DE BOLHAS", "COMO SE NUNCA TIVESSEM USADO SAPATOS", 44)


def s04(c, t):  # 29.70 - 35.92  a carta na mão
    nuremberg(c, t, "crepusculo", seed=5, torre=False)
    kaspar(c, t, 1560, 1010, 0.86, poses=((0, "present_l"),), exprs=((0, "neutral"),), look=-0.6)
    HI(c, t, ((0, "point_r"),), ((0, "think"),))
    nota(c, t, 30.0, 1020, 470, ["Ao Senhor Capitão", "da Cavalaria", "Nuremberg"], w=560, size=48, font=HAND, rot=0.04)
    rotulo(c, t, 31.5, "UMA CARTA", "para um capitão da cavalaria", x=760, y=180, size=56)


def s05(c, t):  # 35.92 - 53.41  na casa do capitão: "quero ser cavaleiro"
    cena_interior(c, t, "interior", "escritorio", seed=9)
    boneco(c, t, 1620, 1010, 0.98, poses=((0, "stand"), (48.0, "shrug")), exprs=((0, "neutral"), (48.0, "worried")), look=-0.6,
           fid=4, **FIGURINO["capitao"])
    kaspar(c, t, 1180, 1010, 0.84, poses=((0, "stand"), (44.6, "hold")), exprs=((0, "worried"), (44.6, "neutral")), look=0.5)
    HI(c, t, ((0, "stand"), (41.7, "think")), ((0, "neutral"), (41.7, "think")))
    rotulo(c, t, 36.2, "NA CASA DO CAPITÃO", "o rapaz quase não sabia falar", x=760, y=170, size=54)
    pl(c, t, 44.6, 1150, 380, "\"QUERO SER CAVALEIRO,", "COMO O MEU PAI FOI\"", 44, t1=51.8)
    grande(c, t, 52.4, "\"CAVALO.\"", 1150, 400, 110, col=(0.98, 0.82, 0.50))


def s06(c, t):  # 53.41 - 63.55  na delegacia escreve o nome
    luz("vela")
    interior(c, t, "reboco", "madeira", "reta", jx=1650, raio=False)
    mesa_i(c, 1200, 860, 760)
    c.save(); c.translate(1050, 760); vela_i(c, t, 0, 0, 0.8); c.restore()
    HI(c, t, ((0, "stand"), (58.1, "point_r")), ((0, "neutral"),))
    rotulo(c, t, 53.6, "NA DELEGACIA", "papel e caneta", x=760, y=170, size=56)
    if t > 56.0:
        k = eob(prog(t, 56.0, 0.4))
        c.save(); c.translate(1220, 520); c.scale(k, k); c.rotate(-0.03)
        rr(c, -380, -170, 760, 340, 6); rgb(c, (0.95, 0.92, 0.82)); c.fill()
        c.restore()
        typewrite(c, t, 59.6, "Kaspar Hauser", 1220, 540, 96, (0.15, 0.12, 0.30), cps=7, font=HAND)


def s07(c, t):  # 63.55 - 74.03  ninguém sabia
    nuremberg(c, t, "noite", seed=6)
    kaspar(c, t, 1300, 1010, 0.82, poses=((0, "slump"),), exprs=((0, "sad"),), look=-0.2, alpha=0.9)
    nevoa_i(c, t, 920, 0.4)
    HI(c, t, ((0, "think"),), ((0, "think"), (69.6, "worried")))
    pl(c, t, 63.8, 1150, 240, "DE ONDE ELE VEIO?", None, 46)
    pl(c, t, 66.9, 1150, 390, "QUEM ERAM OS PAIS?", None, 46)
    grande(c, t, 69.8, "QUASE 200 ANOS DEPOIS...", 1150, 560, 58, col=(0.98, 0.82, 0.50))


def s08(c, t):  # 74.03 - 79.45  título
    nuremberg(c, t, "noite", seed=7)
    nevoa_i(c, t, 880, 0.45)
    escurecer(c, 0.2, 0.5)
    if t > 74.2:
        p = ease_out(prog(t, 74.2, 1.2))
        rglow(c, 960, 420, 600, AMBER, 0.25 * p)
        c.save(); c.translate(0, 20 * (1 - p))
        titulo_i(c, "KASPAR HAUSER", 960, 400, 150, col=(1.0, 0.86, 0.55))
        titulo_i(c, "O RAPAZ QUE SAIU DO ESCURO", 960, 540, 66)
        c.restore()


def s09(c, t):  # 79.45 - 98.57  a carta: sem assinatura, trabalhador pobre, outubro de 1812
    luz("vela")
    interior(c, t, "madeira", "madeira", "reta", jx=1700, raio=False)
    mesa_i(c, 1150, 900, 900)
    HI(c, t, ((0, "stand"), (85.8, "present")), ((0, "think"),))
    nota(c, t, 79.8, 1100, 420, ["... nunca o deixei", "dar um passo", "para fora de casa ..."], w=640, size=46, font=HAND)
    pl(c, t, 83.9, 1520, 700, "SEM ASSINATURA", None, 40, rot=0.03)
    pl(c, t, 86.0, 850, 760, "TRABALHADOR POBRE, 10 FILHOS", None, 36, rot=-0.02)
    if t > 92.5:
        show(c, t, 92.5, 1450, 210, sc(carimbo, "OUTUBRO DE 1812", 44), anim="stamp")


def s10(c, t):  # 98.57 - 121.21  nunca saiu de casa; a frase fria
    ansbach(c, t, "noite", seed=12)
    HI(c, t, ((0, "stand"), (112.1, "think")), ((0, "worried"),))
    pl(c, t, 101.9, 1150, 250, "\"NUNCA DEU UM PASSO", "PARA FORA DE CASA\"", 42)
    pl(c, t, 108.4, 1150, 420, "NINGUÉM SABIA ONDE", "FOI CRIADO", 42)
    if t > 112.1:
        nota(c, t, 114.9, 1150, 700, ["Se não quiser ficar com ele,", "mate-o ou pendure-o", "na chaminé."], w=720, size=40, font=HAND, rot=0.02)
    nevoa_i(c, t, 920, 0.3)


def s11(c, t):  # 121.21 - 146.93  o segundo bilhete; a mesma mão
    luz("vela")
    interior(c, t, "madeira", "madeira", "reta", jx=1700, raio=False)
    mesa_i(c, 1150, 900, 900)
    HI(c, t, ((0, "stand"), (138.4, "think")), ((0, "neutral"), (138.4, "think")))
    nota(c, t, 121.4, 1300, 420, ["Kaspar", "nascido em 30 de abril de 1812", "o pai: da cavalaria"], w=640, size=40, font=HAND, rot=0.03)
    if t > 127.5:
        show(c, t, 127.5, 1300, 190, sc(carimbo, "30 DE ABRIL DE 1812", 42), anim="stamp", t1=138.0)
    if t > 138.4:
        nota(c, t, 138.4, 850, 640, ["... nunca o deixei", "dar um passo ..."], w=480, size=36, font=HAND, rot=-0.04)
        pl(c, t, 142.9, 1150, 860, "A MESMA MÃO?", None, 48)


def s12(c, t):  # 146.93 - 161.88  vagabundo; torre Luginsland
    luz("nublado")
    ceu(c, t, seed=13)
    montanhas(c, 620, 220, seed=13, depth=0.8)
    casario(c, t, 860, "medieval", seed=14, depth=0.35, escala=0.6)
    torre_castelo(c, 1350, 880, 240, 640, depth=0.1)
    torre_castelo(c, 1620, 880, 160, 420, depth=0.25)
    chao(c, t, 880, "pedra", seed=13)
    kaspar(c, t, 1050, 1020, 0.78, poses=((0, "slump"),), exprs=((0, "sad"),), look=0.4, andar=False)
    boneco(c, t, 860, 1020, 0.9, poses=((0, "hold"),), exprs=((0, "neutral"),), look=0.6, fid=5,
           roupa="jaqueta", cor_roupa=(0.30, 0.34, 0.30), chapeu="quepe", cor_chapeu=(0.2, 0.22, 0.2), bigode=True, idade=0.3)
    HI(c, t, ((0, "point_r"),), ((0, "neutral"),))
    pl(c, t, 147.2, 900, 220, "TRATADO COMO VAGABUNDO", None, 42, t1=153.0)
    rotulo(c, t, 153.3, "TORRE LUGINSLAND", "castelo de Nuremberg", x=700, y=180, size=58)


def s13(c, t):  # 161.88 - 182.50  pão e água; luz; cavalinho
    luz("interior")
    interior(c, t, "pedra", "madeira", "arco", jx=1650)
    kaspar(c, t, 1200, 1010, 0.82, poses=((0, "stand"), (172.9, "head"), (176.3, "stand")),
           exprs=((0, "neutral"), (172.9, "worried"), (176.3, "happy")), look=-0.3)
    HI(c, t, ((0, "stand"), (166.4, "present")), ((0, "neutral"), (172.9, "think")))
    rotulo(c, t, 162.0, "NÃO ERA UM RAPAZ COMUM", None, x=700, y=170, size=52)
    obj(c, t, 166.4, 820, 760, lambda c: pao_i(c, 1.2), t1=172.6)
    obj(c, t, 166.9, 980, 790, lambda c: jarra_i(c, 0.9), t1=172.6)
    pl(c, t, 166.5, 1500, 330, "SÓ PÃO E ÁGUA", None, 44, t1=172.6)
    if 169.6 < t < 172.6:
        pl(c, t, 169.6, 1500, 470, "CARNE OU CERVEJA", None, 38)
        risca(c, t, 170.4, 1500, 470, 380)
    pl(c, t, 172.9, 1500, 330, "A LUZ MACHUCAVA", "OS OLHOS", 42, t1=176.0)
    obj(c, t, 176.3, 1520, 1010, lambda c: cavalinho_i(c, 1.2))
    pl(c, t, 176.6, 1450, 330, "BRINCAVA POR HORAS", "COMO UMA CRIANÇA DE 3 ANOS", 42)


def s14(c, t):  # 182.50 - 199.47  gente subia a torre; começa a contar
    luz("tarde")
    ceu(c, t, seed=15)
    casario(c, t, 860, "medieval", seed=16, depth=0.4, escala=0.6)
    torre_castelo(c, 1450, 900, 260, 640, depth=0.05)
    chao(c, t, 900, "pedra", seed=15)
    figurantes(c, t, 990, n=9, s=0.42, seed=4, x0=700, x1=1380, figurinos=["campones", "camponesa", "cavalheiro", "dama"])
    HI(c, t, ((0, "present"), (190.9, "think")), ((0, "neutral"), (190.9, "think")))
    rotulo(c, t, 182.7, "A NOTÍCIA CORREU", "a cidade inteira subia a torre", x=700, y=180, size=56)
    pl(c, t, 191.2, 1050, 400, "E ELE COMEÇOU A CONTAR", "A PRÓPRIA HISTÓRIA", 44)
    if t > 196.5:
        quarto_escuro_transicao(c, 0.85 * prog(t, 196.5, 3.0))


# ------------------------------------------------------------------ BLOCO 2 (199.47 - 384.67)
def s15(c, t):  # 199.77 - 214.15  o quarto pequeno e escuro
    cela_baixa(c, t, "sombrio", feixe=0.6)
    kaspar(c, t, 1100, 960, 0.70, poses=((0, "slump"),), exprs=((0, "sad"),), look=0.2, chapeu=None)
    if t > 208.0:
        c.save(); c.translate(1320, 950); cavalinho_i(c, 0.55); c.restore()
        c.save(); c.translate(860, 950); cavalinho_i(c, 0.45, col=(0.56, 0.38, 0.22)); c.restore()
    HI(c, t, ((0, "stand"),), ((0, "worried"),), y=1060)
    rotulo(c, t, 200.0, "SEGUNDO KASPAR...", "um quarto pequeno e escuro", x=700, y=220, size=56)
    pl(c, t, 205.4, 1250, 400, "TÃO BAIXO QUE NÃO DAVA", "PARA FICAR EM PÉ", 40, t1=212.0)
    if t < 201.5:
        quarto_escuro_transicao(c, 0.85 * (1 - prog(t, 199.5, 2.0)))


def s16(c, t):  # 214.15 - 231.91  pão, jarra, água amarga, roupa trocada
    cela_baixa(c, t, "sombrio", feixe=0.3)
    kaspar(c, t, 1150, 960, 0.70, poses=((0, "slump"),), exprs=((0, "neutral"), (225.0, "sad")), look=0.2, chapeu=None)
    obj(c, t, 217.3, 900, 960, lambda c: pao_i(c, 1.0))
    obj(c, t, 217.8, 1400, 960, lambda c: jarra_i(c, 0.8))
    HI(c, t, ((0, "stand"),), ((0, "neutral"), (221.5, "worried")), y=1060)
    rotulo(c, t, 214.3, "NUNCA VIU O ROSTO", "de quem cuidava dele", x=700, y=220, size=54)
    pl(c, t, 221.5, 1300, 400, "ÀS VEZES, A ÁGUA", "TINHA GOSTO AMARGO", 40, t1=225.0)
    pl(c, t, 225.1, 1300, 400, "ROUPA TROCADA", "CABELO E UNHAS CORTADOS", 40)


def s17(c, t):  # 231.91 - 255.99  o homem entra, ensina o nome, leva para fora
    if t < 244.9:
        cela_baixa(c, t, "sombrio", feixe=1.0)
        a = prog(t, 232.0, 1.5)
        silhueta(c, t, 1560, 960, 0.75, alpha=0.9 * a, olhos=False)
        kaspar(c, t, 1100, 960, 0.70, poses=((0, "slump"), (236.6, "hold")), exprs=((0, "worried"),), look=0.6, chapeu=None)
        HI(c, t, ((0, "stand"),), ((0, "worried"),), y=1060)
        rotulo(c, t, 232.1, "UM DIA...", "o homem entrou no quarto", x=700, y=220, size=56)
        nota(c, t, 236.6, 1250, 400, ["Kaspar Hauser"], w=420, size=52, font=HAND, rot=0.03, t1=241.8)
        pl(c, t, 242.0, 1250, 400, "\"QUERO SER CAVALEIRO...\"", None, 40)
    else:
        luz("crepusculo")
        ceu(c, t, seed=17)
        montanhas(c, 620, 200, seed=17, depth=0.8)
        colinas(c, 760, 30, seed=17, depth=0.5)
        torre_castelo(c, 1700, 760, 80, 200, depth=0.6)
        casario(c, t, 770, "medieval", seed=18, depth=0.6, escala=0.35, x0=1500, x1=1950)
        chao(c, t, 880, "terra", seed=17)
        k = prog(t, 245.0, 9.0)
        al = 1 - prog(t, 253.2, 1.5)
        if al > 0.02:
            silhueta(c, t, 900 + 380 * k, 990, 0.62, alpha=0.85 * al, olhos=False)
        kaspar(c, t, 800 + 380 * k, 990, 0.66, poses=((0, "hold"),), exprs=((0, "worried"),), look=0.6, andar=True, cambaleia=True)
        HI(c, t, ((0, "point_r"),), ((0, "neutral"), (253.2, "worried")))
        pl(c, t, 245.3, 1250, 250, "PELA PRIMEIRA VEZ,", "DO LADO DE FORA", 44)
        rotulo(c, t, 253.3, "E O HOMEM SUMIU", None, x=700, y=420, size=56)


def s18(c, t):  # 255.99 - 273.96  aviso do prefeito; a criança da Europa
    nuremberg(c, t, "dia", seed=19)
    particulas(c, t, "poeira", 16)
    figurantes(c, t, 1000, n=6, s=0.38, seed=6, x0=900, x1=1700, figurinos=["campones", "camponesa", "cavalheiro", "dama"])
    HI(c, t, ((0, "present"),), ((0, "neutral"), (263.9, "happy")))
    show(c, t, 256.2, 1300, 230, sc(carimbo, "JULHO DE 1828", 42), anim="stamp")
    pl(c, t, 257.6, 1300, 420, "AVISO OFICIAL", "O PREFEITO TORNA A HISTÓRIA PÚBLICA", 46, t1=263.6)
    pl(c, t, 263.9, 1300, 420, "ASSUNTO EM TODA A EUROPA", None, 44)
    grande(c, t, 268.7, "\"A CRIANÇA DA EUROPA\"", 1250, 620, 72, col=(0.98, 0.82, 0.50))


def s19(c, t):  # 273.96 - 299.53  Daumer: ler, escrever, desenhar
    cena_interior(c, t, "interior", "escritorio", seed=20)
    boneco(c, t, 1620, 1010, 0.98, poses=((0, "present_l"),), exprs=((0, "happy"),), look=-0.6, fid=8,
           roupa="casaco", cor_roupa=(0.28, 0.22, 0.18), cabelo="curto", cor_cabelo=(0.30, 0.22, 0.16), oculos=True,
           gravata=(0.9, 0.9, 0.86), idade=0.2)
    kaspar(c, t, 1200, 1010, 0.84, poses=((0, "stand"), (284.1, "hold")), exprs=((0, "neutral"), (289.3, "happy")), look=0.6)
    HI(c, t, ((0, "stand"),), ((0, "neutral"), (289.3, "happy")))
    rotulo(c, t, 274.2, "NUREMBERG ADOTA O RAPAZ", None, x=700, y=150, size=50)
    rotulo(c, t, 277.4, "GEORG FRIEDRICH DAUMER", "professor", x=700, y=245, size=46)
    pl(c, t, 284.2, 1050, 440, "LER · ESCREVER · DESENHAR", None, 40, t1=291.5)
    if t > 292.0:
        def flor(c):
            rr(c, -170, -130, 340, 260, 4); rgb(c, (0.96, 0.94, 0.86)); c.fill()
            line(c, 0, 100, 0, -20, 4, (0.30, 0.50, 0.30))
            for a in range(6):
                ang = a * math.pi / 3
                ellipse(c, math.cos(ang) * 30, -50 + math.sin(ang) * 30, 22, 22); rgb(c, (0.85, 0.40, 0.45)); c.fill()
            c.new_sub_path(); c.arc(0, -50, 16, 0, 6.283); rgb(c, (0.95, 0.80, 0.30)); c.fill()
            ellipse(c, 30, 40, 30, 12); rgb(c, (0.40, 0.62, 0.38)); c.fill()
        obj(c, t, 292.0, 1480, 370, flor, 0.8)
        pl(c, t, 293.0, 1000, 430, "EM POUCOS MESES", "DESENHOS DELICADOS", 38)


def s20(c, t):  # 299.53 - 320.35  sentidos fora do comum; desconfiança
    cena_interior(c, t, "vela", "biblioteca", seed=21)
    HI(c, t, ((0, "stand"), (312.1, "think")), ((0, "happy"), (312.1, "think")))
    pl(c, t, 299.8, 1150, 220, "DAUMER FICOU FASCINADO", None, 44)
    pl(c, t, 306.5, 980, 400, "ENXERGAVA NO ESCURO?", None, 40, rot=-0.02)
    pl(c, t, 309.0, 1400, 520, "SENTIA METAL ESCONDIDO?", None, 40, rot=0.02)
    if t > 312.1:
        c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.35 * prog(t, 312.1, 1.0)); c.fill()
        pl(c, t, 312.3, 1150, 720, "OUTROS DESCONFIAVAM", "SABIA O QUE AS PESSOAS QUERIAM OUVIR", 42)


def s21(c, t):  # 320.35 - 334.62  17 de outubro de 1829, o porão
    luz("noite")
    interior(c, t, "pedra", "pedra", "arco", jx=1650, raio=False)
    c.save(); c.translate(1500, 720); vela_i(c, t, 0, 0, 0.9); c.restore()
    rglow(c, 1500, 640, 300, (1.0, 0.75, 0.4), 0.2 * piscar(t, 3))
    kaspar(c, t, 1150, 1010, 0.82, poses=((0, "slump"), (330.0, "head")), exprs=((0, "shocked"),), look=0.4)
    HI(c, t, ((0, "stand"),), ((0, "worried"), (329.4, "shocked")))
    show(c, t, 320.6, 1150, 230, sc(carimbo, "17 DE OUTUBRO DE 1829", 46), anim="stamp")
    pl(c, t, 329.5, 1150, 420, "NO PORÃO DE DAUMER", "UM CORTE NA TESTA", 42)
    nevoa_i(c, t, 960, 0.25)


def s22(c, t):  # 334.62 - 355.19  o homem encapuzado; a ameaça
    luz("noite")
    interior(c, t, "pedra", "pedra", None, raio=False)
    a = prog(t, 334.8, 2.0)
    silhueta(c, t, 1550, 1010, 1.0, alpha=0.85 * a, olhos=True)
    c.save(); c.translate(1550, 640); c.scale(1.2, 1.2)
    pg(c, [(-70, 30), (0, -110), (70, 30)]); rgb(c, (0.02, 0.02, 0.03), 0.85 * a); c.fill()  # capuz
    c.restore()
    escurecer(c, 0.15, 0.6)
    HI(c, t, ((0, "stand"), (340.8, "think")), ((0, "worried"), (343.3, "shocked")))
    rotulo(c, t, 334.8, "UM HOMEM ENCAPUZADO", None, x=700, y=170, size=56)
    pl(c, t, 340.8, 1050, 330, "RECONHECEU A VOZ", None, 44, t1=348.2)
    pl(c, t, 343.4, 1050, 470, "O MESMO HOMEM DO", "QUARTO ESCURO", 42, t1=348.2)
    nota(c, t, 351.1, 1020, 420, ["\"Você ainda vai morrer", "antes de sair", "de Nuremberg.\""], w=640, size=46, font=HAND, rot=0.02)


def s23(c, t):  # 355.19 - 371.63  ninguém encontrado; os céticos
    nuremberg(c, t, "noite", seed=22)
    for i, x in enumerate((900, 1300)):
        boneco(c, t, x, 1010, 0.8, poses=((0, "hold"),), exprs=((0, "neutral"),), look=0.6 if i == 0 else -0.6, fid=20 + i,
               roupa="jaqueta", cor_roupa=(0.20, 0.24, 0.36), chapeu="quepe", cor_chapeu=(0.16, 0.18, 0.26), bigode=True,
               prop=("r", lambda c, tt: lanterna_i(c, tt, 0.5)))
    HI(c, t, ((0, "stand"), (360.2, "think")), ((0, "neutral"), (360.2, "think")))
    pl(c, t, 355.4, 1100, 230, "NINGUÉM FOI ENCONTRADO", None, 44, t1=360.0)
    pl(c, t, 360.2, 1100, 230, "FEITO PELO PRÓPRIO KASPAR?", "OS CÉTICOS", 44)
    pl(c, t, 365.2, 1100, 420, "DIAS ANTES:", "PEGO NUMA MENTIRA", 42)
    nevoa_i(c, t, 940, 0.3)


def s24(c, t):  # 371.63 - 385.67  guardas; outras casas; incidentes continuam
    nuremberg(c, t, "crepusculo", seed=23, torre=False)
    boneco(c, t, 1550, 1010, 0.9, poses=((0, "stand"),), exprs=((0, "neutral"),), look=-0.6, fid=22,
           roupa="jaqueta", cor_roupa=(0.20, 0.24, 0.36), chapeu="quepe", cor_chapeu=(0.16, 0.18, 0.26), bigode=True)
    kaspar(c, t, 1250, 1010, 0.84, poses=((0, "stand"),), exprs=((0, "neutral"), (380.0, "worried")), look=0.6)
    HI(c, t, ((0, "present"),), ((0, "neutral"), (380.0, "worried")))
    pl(c, t, 371.9, 1150, 240, "GUARDAS PARA PROTEGÊ-LO", None, 42)
    pl(c, t, 376.9, 1150, 390, "OUTRAS CASAS", None, 40)
    grande(c, t, 380.5, "E OS INCIDENTES CONTINUARAM", 1150, 580, 56, col=(0.98, 0.82, 0.50))


# ------------------------------------------------------------------ BLOCO 3 (385.67 - 586.33)
def s25(c, t):  # 385.67 - 396.04  o boato: um príncipe
    ansbach(c, t, "crepusculo", seed=24)
    figurantes(c, t, 1000, n=7, s=0.4, seed=8, x0=800, x1=1700, andando=False, figurinos=["cavalheiro", "dama", "campones"])
    HI(c, t, ((0, "stand"), (393.9, "point_ru")), ((0, "think"), (393.9, "shocked")))
    pl(c, t, 386.0, 1150, 220, "UM BOATO", "SE ESPALHAVA PELA ALEMANHA", 44)
    if t > 393.9:
        k = eob(prog(t, 393.9, 0.5))
        c.save(); c.translate(1150, 470); c.scale(k * 2.2, k * 2.2)
        pg(c, [(-60, 20), (-60, -20), (-30, 0), (0, -40), (30, 0), (60, -20), (60, 20)]); rgb(c, OURO); c.fill()
        c.restore()
        grande(c, t, 394.0, "UM PRÍNCIPE?", 1150, 640, 96, col=(0.98, 0.82, 0.50))


def s26(c, t):  # 396.04 - 414.20  Baden, 29 de setembro de 1812
    luz("interior")
    interior(c, t, "reboco", "madeira", "gotica", jx=1650, cor=(0.86, 0.80, 0.70))
    obj(c, t, 398.5, 1200, 1000, lambda c: berco_i(c, 1.2))
    HI(c, t, ((0, "present"),), ((0, "neutral"), (410.2, "sad")))
    show(c, t, 398.5, 1200, 190, sc(carimbo, "29 DE SETEMBRO DE 1812", 42), anim="stamp")
    rotulo(c, t, 404.0, "BADEN", "um dos estados alemães", x=700, y=330, size=58)
    pl(c, t, 408.0, 1250, 520, "O HERDEIRO DO TRONO", None, 44, t1=410.0)
    pl(c, t, 410.2, 1250, 520, "MORREU 2 SEMANAS", "E MEIA DEPOIS", 44)


def s27(c, t):  # 414.20 - 436.23  a lenda da troca; o filho da condessa
    cena_interior(c, t, "vela", "salao", seed=25)
    boneco(c, t, 1550, 1010, 0.95, poses=((0, "hold"),), exprs=((0, "sinistro"),), look=-0.6, fid=9,
           roupa="vestido", cor_roupa=(0.30, 0.12, 0.20), cabelo="coque", mulher=True, idade=0.3)
    HI(c, t, ((0, "stand"), (425.3, "finger_up")), ((0, "think"), (425.3, "neutral")))
    pl(c, t, 414.4, 1100, 230, "SEGUNDO A LENDA...", "ELE NÃO MORREU", 44, t1=425.0)
    pl(c, t, 418.2, 1100, 420, "TROCADO POR UM BEBÊ DOENTE", "A MANDO DE UMA CONDESSA", 40, t1=425.0)
    pl(c, t, 425.3, 1100, 230, "UM DETALHE REAL", None, 44)
    show(c, t, 429.0, 1100, 420, sc(carimbo, "1830", 60), anim="stamp")
    pl(c, t, 429.6, 1100, 600, "UM FILHO DA CONDESSA", "VIRA GRÃO-DUQUE DE BADEN", 40)


def s28(c, t):  # 436.23 - 448.25  a idade certa
    cela_baixa(c, t, "noite", feixe=0.4)
    HI(c, t, ((0, "finger_up"),), ((0, "think"),), y=1060)
    pl(c, t, 436.4, 1150, 230, "KASPAR: NASCIDO EM 1812", "A IDADE CERTA", 42)
    for i, (tt, s_) in enumerate(((442.3, "O QUARTO ESCURO"), (443.8, "O SEGREDO"), (445.2, "ALGUÉM QUE O QUERIA MORTO"))):
        pl(c, t, tt, 1150 + (i - 1) * 60, 400 + i * 110, s_, None, 38, rot=0.02 * (-1) ** i)


def s29(c, t):  # 448.25 - 473.93  Stanhope; Ansbach; Meyer; copista
    ansbach(c, t, "dia", seed=26)
    particulas(c, t, "poeira", 16)
    boneco(c, t, 1600, 1010, 1.0, poses=((0, "present_l"),), exprs=((0, "confident"),), look=-0.6, fid=10, **FIGURINO["cavalheiro"])
    kaspar(c, t, 1230, 1010, 0.86, poses=((0, "stand"),), exprs=((0, "happy"),), look=0.6, ansbach=True)
    HI(c, t, ((0, "point_r"),), ((0, "neutral"),))
    rotulo(c, t, 448.6, "LORDE STANHOPE", "fim de 1831 · um nobre inglês", x=700, y=170, size=56)
    pl(c, t, 456.5, 1150, 400, "\"VOU LEVÁ-LO PARA A INGLATERRA\"", None, 38, t1=462.5)
    rotulo(c, t, 462.6, "ANSBACH", "a nova casa de Kaspar", x=700, y=330, size=54)
    pl(c, t, 464.4, 1150, 470, "PROFESSOR JOHANN GEORG MEYER", "E UM EMPREGO DE COPISTA", 38)


def s30(c, t):  # 473.93 - 490.89  Feuerbach e o livro
    cena_interior(c, t, "vela", "biblioteca", seed=27)
    boneco(c, t, 1600, 1010, 1.0, poses=((0, "hold"),), exprs=((0, "neutral"),), look=-0.6, fid=11,
           roupa="tunica", cor_roupa=(0.12, 0.12, 0.14), cabelo="calvo", idade=0.6, gravata=(0.92, 0.92, 0.9),
           prop=("r", lambda c, tt: livro_aberto(c, 120)))
    HI(c, t, ((0, "present"),), ((0, "neutral"),))
    rotulo(c, t, 474.1, "ANSELM VON FEUERBACH", "juiz, um dos maiores juristas alemães", x=700, y=170, size=50)
    show(c, t, 481.7, 1150, 400, sc(carimbo, "1832", 56), anim="stamp")
    pl(c, t, 486.6, 1100, 600, "\"UM CRIME CONTRA A ALMA", "DE UM SER HUMANO\"", 42)


def s31(c, t):  # 490.89 - 514.99  promessa não cumprida; Feuerbach morre; briga com Meyer
    cena_interior(c, t, "interior", "escritorio", seed=28)
    boneco(c, t, 1600, 1010, 1.0, poses=((0, "stand"), (510.2, "point_l")), exprs=((0, "angry"),), look=-0.6, fid=12,
           roupa="casaco", cor_roupa=(0.14, 0.14, 0.16), cabelo="calvo", oculos=True, idade=0.4, gravata=(0.9, 0.9, 0.86))
    kaspar(c, t, 1230, 1010, 0.86, poses=((0, "stand"), (510.2, "shrug")), exprs=((0, "sad"), (510.2, "angry")), look=0.6, ansbach=True)
    HI(c, t, ((0, "stand"),), ((0, "neutral"), (495.1, "sad")))
    pl(c, t, 491.1, 1100, 200, "A PROMESSA NUNCA SE CUMPRIU", None, 40, t1=500.2)
    pl(c, t, 495.2, 1100, 330, "STANHOPE SE AFASTA", None, 38, t1=500.2)
    pl(c, t, 500.4, 1100, 200, "MAIO DE 1833", "FEUERBACH MORRE", 40, t1=504.6)
    pl(c, t, 504.8, 1100, 200, "MEYER: RÍGIDO", "VIVIA EM ATRITO COM KASPAR", 40)
    if t > 510.2:
        show(c, t, 510.2, 1100, 420, sc(carimbo, "9 DE DEZEMBRO", 44), anim="stamp")


def s32(c, t):  # 514.99 - 530.12  14 de dezembro de 1833
    ansbach(c, t, "crepusculo", seed=29)
    snow(c, t, 90, 30, 0.6)
    k = prog(t, 520.5, 3.0)
    kaspar(c, t, 1700 - 400 * k, 1010, 0.86, poses=((0, "run"), (524.0, "hold")), exprs=((0, "shocked"), (524.0, "desperate")),
           look=-0.6, ansbach=True, andar=True)
    HI(c, t, ((0, "stand"),), ((0, "worried"), (524.0, "shocked")))
    show(c, t, 515.2, 1150, 220, sc(carimbo, "SÁBADO, 14 DE DEZEMBRO DE 1833", 40), anim="stamp")
    pl(c, t, 524.1, 1100, 420, "PÁLIDO", "UM FERIMENTO FUNDO NO PEITO", 42)


def s33(c, t):  # 530.12 - 549.28  o jardim do palácio; a bolsa; o golpe
    jardim(c, t, "crepusculo")
    snow(c, t, 70, 20, 0.5)
    al = 1 - prog(t, 544.2, 1.5)
    if al > 0.02:
        silhueta(c, t, 1520 + 200 * prog(t, 544.2, 1.5), 1010, 0.9, alpha=0.9 * al, olhos=False)
    kaspar(c, t, 1200, 1010, 0.86, poses=((0, "stand"), (539.7, "hold"), (543.6, "slump")),
           exprs=((0, "neutral"), (543.6, "shocked")), look=0.6, ansbach=True)
    if 539.7 < t < 545.0:
        c.save(); c.translate(1260, 870); bolsa_seda(c, 0.5); c.restore()
    if 543.5 < t < 543.9:
        c.rectangle(0, 0, W, H); rgb(c, (1, 1, 1), 0.35); c.fill()
    HI(c, t, ((0, "stand"),), ((0, "neutral"), (543.6, "shocked")))
    rotulo(c, t, 530.3, "O JARDIM DO PALÁCIO", "Ansbach · \"notícias sobre a sua mãe\"", x=700, y=170, size=54)
    pl(c, t, 539.8, 1150, 400, "UMA PEQUENA BOLSA", None, 42, t1=543.4)
    nevoa_i(c, t, 920, 0.3)


def s34(c, t):  # 549.28 - 562.57  o policial acha a bolsa roxa
    jardim(c, t, "nublado", seed=32)
    boneco(c, t, 1500, 1010, 0.95, poses=((0, "point_l"), (554.5, "hold")), exprs=((0, "neutral"), (554.5, "shocked")), look=-0.6, fid=23,
           roupa="jaqueta", cor_roupa=(0.20, 0.24, 0.36), chapeu="quepe", cor_chapeu=(0.16, 0.18, 0.26), bigode=True)
    if t < 554.5:
        c.save(); c.translate(1260, 1000); bolsa_seda(c, 0.6); c.restore()
    else:
        obj(c, t, 554.5, 1150, 520, lambda c: bolsa_seda(c, 1.6))
    HI(c, t, ((0, "point_r"),), ((0, "neutral"), (554.5, "think")))
    rotulo(c, t, 549.5, "UM POLICIAL", "volta ao jardim", x=700, y=170, size=56)
    pl(c, t, 551.4, 1150, 260, "SEDA ROXA", None, 40, t1=554.4)
    pl(c, t, 557.2, 1150, 780, "ESCRITO A LÁPIS... AO CONTRÁRIO", None, 40)


NOTA_LINHAS = ["Hauser vai poder contar", "como eu sou e de onde venho.", "Eu mesmo digo:",
               "venho da fronteira da Baviera,", "perto de um rio.", "Meu nome:  M. L. Ö."]


def s35(c, t):  # 562.57 - 587.33  o bilhete em escrita de espelho
    luz("vela")
    interior(c, t, "madeira", "madeira", "reta", jx=1750, raio=False)
    mesa_i(c, 1150, 940, 1100)
    HI(c, t, ((0, "point_r"), (575.0, "think"), (584.4, "point_r")), ((0, "think"), (584.4, "shocked")))
    esp = 1.0 - prog(t, 566.0, 1.2)
    p = 0.34 + 0.66 * prog(t, 566.6, 12.0)
    if t > 562.7:
        k = eob(prog(t, 562.7, 0.45))
        c.save(); c.translate(1160, 540); c.scale(k, k)
        bilhete_espelho(c, t, NOTA_LINHAS, w=860, size=50, espelho=esp, p=p if t > 566.6 else 1.0)
        c.restore()
    rotulo(c, t, 562.8, "ESCRITA DE ESPELHO", "escrito a lápis, ao contrário", x=760, y=150, size=50)
    if t > 584.4:
        grande(c, t, 584.5, "M. L. Ö.", 1160, 960, 120, col=(0.98, 0.82, 0.50))


# ------------------------------------------------------------------ BLOCO 4 (587.33 - 853.94)
def s36(c, t):  # 587.58 - 607.41  o problema do bilhete; as pegadas na neve
    if t < 600.9:
        luz("vela")
        interior(c, t, "madeira", "madeira", "reta", jx=1750, raio=False)
        mesa_i(c, 1150, 940, 1100)
        HI(c, t, ((0, "finger_up"),), ((0, "think"),))
        pl(c, t, 587.8, 1150, 200, "O BILHETE TINHA UM PROBLEMA", None, 42)
        obj(c, t, 590.3, 950, 520, lambda c: triangulo_dobrado(c, 1.3))
        pl(c, t, 590.5, 1450, 450, "DOBRADO EM TRIÂNGULO", "COMO KASPAR DOBRAVA", 36)
        pl(c, t, 597.2, 1450, 640, "OS MESMOS ERROS", "DE ESCRITA DELE", 36)
    else:
        jardim(c, t, "nublado", seed=33)
        pegadas_i(c, t, 1750, 1060, 820, 900, n=16, p=prog(t, 601.2, 4.0))
        HI(c, t, ((0, "point_r"),), ((0, "think"), (604.0, "worried")))
        rotulo(c, t, 601.1, "SEGUNDO ALGUNS RELATOS", "neve no jardim... e as pegadas de uma pessoa só", x=700, y=170, size=50)


def s37(c, t):  # 607.41 - 618.52  a morte de Kaspar
    luz("vela")
    interior(c, t, "reboco", "madeira", "reta", jx=1700, raio=False, cor=(0.70, 0.62, 0.52))
    c.save(); c.translate(1250, 760); vela_i(c, t, 0, 0, 1.1); c.restore()
    rglow(c, 1250, 640, 340, (1.0, 0.78, 0.45), 0.22)
    HI(c, t, ((0, "stand"),), ((0, "sad"),))
    show(c, t, 607.6, 1150, 230, sc(carimbo, "17 DE DEZEMBRO DE 1833", 46), anim="stamp")
    pl(c, t, 608.6, 1150, 420, "KASPAR HAUSER MORRE", "TRÊS DIAS DEPOIS DO GOLPE", 44)
    pl(c, t, 615.8, 1150, 590, "TINHA UNS 21 ANOS", None, 44)
    escurecer(c, 0.15, 0.5)


def s38(c, t):  # 618.52 - 633.52  o túmulo em Ansbach
    cena_cemiterio(c, t, "crepusculo", seed=14)
    pedra_memorial(c, 1450, 1060, ["HIC JACET", "CASPARUS HAUSER", "AENIGMA", "SUI TEMPORIS", "", "MDCCCXXXIII"], s=1.15, size=30)
    HI(c, t, ((0, "stand"), (621.5, "present")), ((0, "sad"),))
    rotulo(c, t, 618.7, "CEMITÉRIO DE ANSBACH", None, x=700, y=170, size=54)
    pl(c, t, 624.7, 1000, 330, "\"AQUI JAZ KASPAR HAUSER,", "ENIGMA DO SEU TEMPO\"", 40)
    pl(c, t, 629.0, 1000, 500, "NASCIMENTO DESCONHECIDO,", "MORTE MISTERIOSA", 38)
    nevoa_i(c, t, 980, 0.35)


def s39(c, t):  # 633.52 - 658.64  a investigação e o estudo de 2005
    cena_interior(c, t, "interior", "escritorio", seed=34)
    HI(c, t, ((0, "stand"), (646.0, "shrug"), (649.7, "think")), ((0, "neutral"), (646.0, "worried"), (649.7, "think")))
    pl(c, t, 633.8, 1150, 220, "A INVESTIGAÇÃO DA ÉPOCA", "FERIDO POR SI MESMO?", 42)
    pl(c, t, 640.0, 1150, 390, "UM GOLPE MAIS FUNDO", "DO QUE PRETENDIA?", 38)
    pl(c, t, 646.1, 1150, 560, "OS MÉDICOS NUNCA", "CHEGARAM A UM ACORDO", 38)
    show(c, t, 649.8, 1500, 730, sc(carimbo, "2005", 52), anim="stamp")
    pl(c, t, 651.0, 1050, 760, "IMPROVÁVEL...", "MAS NÃO DESCARTADO", 38)


def s40(c, t):  # 658.64 - 664.87  três explicações
    nuremberg(c, t, "noite", seed=35)
    nevoa_i(c, t, 920, 0.35)
    HI(c, t, ((0, "think"), (661.9, "finger_up")), ((0, "think"),))
    grande(c, t, 658.8, "O QUE ACONTECEU DE VERDADE?", 1150, 250, 62)
    grande(c, t, 662.0, "3 EXPLICAÇÕES", 1150, 450, 100, col=(0.98, 0.82, 0.50))


def s41(c, t):  # 664.87 - 691.09  teoria 1: o príncipe
    luz("interior")
    interior(c, t, "reboco", "madeira", "gotica", jx=1650, cor=(0.86, 0.80, 0.70))
    HI(c, t, ((0, "present"), (671.6, "finger_up")), ((0, "neutral"), (671.6, "think")))
    pl(c, t, 665.0, 1150, 190, "1 · O PRÍNCIPE DE BADEN", None, 44)
    pl(c, t, 667.9, 1150, 330, "2 SÉCULOS DE LIVROS E FILMES", None, 36, t1=674.0)
    if t > 674.3:
        show(c, t, 674.3, 1150, 330, sc(carimbo, "1876", 54), anim="stamp")
        for i, (tt, s_) in enumerate(((678.5, "BATISMO"), (679.8, "AUTÓPSIA"), (681.2, "ENTERRO"))):
            nota(c, t, tt, 870 + i * 290, 560, [s_], w=250, size=34, rot=0.03 * (-1) ** i)
    pl(c, t, 684.4, 1150, 800, "CARTAS DA AVÓ DO BEBÊ", "A DOENÇA, DIA APÓS DIA", 38)


def s42(c, t):  # 691.09 - 720.18  teoria 2: impostor; a marca de vacina
    nuremberg(c, t, "nublado", seed=36)
    kaspar(c, t, 1550, 1010, 0.86, poses=((0, "stand"), (705.3, "shrug")), exprs=((0, "neutral"), (705.3, "grin")), look=-0.5, ansbach=True)
    HI(c, t, ((0, "stand"), (695.8, "think")), ((0, "neutral"), (695.8, "think")))
    pl(c, t, 691.3, 1050, 190, "2 · UM IMPOSTOR?", None, 46)
    pl(c, t, 695.9, 1050, 340, "UM RAPAZ FUGIDO", "QUE INVENTOU A HISTÓRIA", 38, t1=705.0)
    pl(c, t, 705.3, 1050, 340, "MEYER, STANHOPE", "E VÁRIOS MÉDICOS", 38, t1=710.4)
    if t > 710.6:
        def braco(c):
            rr(c, -230, -60, 460, 120, 60); rgb(c, P(PELES["clara"])); c.fill()
            for dx in (-24, 0, 24):
                c.new_sub_path(); c.arc(dx, 0, 10, 0, 6.283); rgb(c, (0.78, 0.55, 0.50)); c.fill()
            c.new_sub_path(); c.arc(0, 0, 50, 0, 6.283); rgb(c, AMBER); c.set_line_width(5); c.stroke()
        obj(c, t, 710.6, 1050, 400, braco)
        pl(c, t, 711.4, 1050, 570, "A MARCA DE UMA VACINA", "DE QUEM \"NUNCA VIU NINGUÉM\"?", 36)


def s43(c, t):  # 720.18 - 742.58  teoria 3: no meio do caminho
    cela_baixa(c, t, "noite", feixe=0.8)
    kaspar(c, t, 1350, 960, 0.70, poses=((0, "slump"),), exprs=((0, "sad"),), look=-0.2, chapeu=None,
           alpha=0.4 + 0.6 * (1 - prog(t, 737.4, 3.0)))
    HI(c, t, ((0, "stand"), (732.6, "think")), ((0, "neutral"), (732.6, "think")), y=1060)
    pl(c, t, 720.4, 1100, 230, "3 · NO MEIO DO CAMINHO", None, 44)
    pl(c, t, 723.8, 1100, 390, "UMA CRIANÇA ESCONDIDA DE VERDADE", "TALVEZ POR VERGONHA, TALVEZ POR DINHEIRO", 34, t1=732.4)
    pl(c, t, 732.6, 1100, 390, "QUE DEPOIS EXAGEROU", "A PRÓPRIA HISTÓRIA", 38, t1=737.2)
    pl(c, t, 737.4, 1100, 390, "O QUARTO PODE TER EXISTIDO...", "SÓ QUE NÃO DO JEITO QUE ELE CONTOU", 34)


def laboratorio(c, t):
    luz("interior")
    interior(c, t, "reboco", "pedra", "reta", jx=1700, cor=(0.80, 0.84, 0.86))


def s44(c, t):  # 742.58 - 769.67  1996 e 2002
    laboratorio(c, t)
    HI(c, t, ((0, "stand"), (758.7, "shrug")), ((0, "neutral"), (758.7, "shocked"), (765.0, "think")))
    grande(c, t, 742.8, "A CIÊNCIA ENTRA NO CASO", 1150, 170, 60)
    show(c, t, 746.7, 900, 320, sc(carimbo, "1996", 50), anim="stamp")
    pl(c, t, 747.6, 900, 470, "MANCHA DE SANGUE", "MUSEU DE ANSBACH", 34)
    pl(c, t, 758.7, 900, 640, "NÃO BATEU", None, 40)
    show(c, t, 760.1, 1450, 320, sc(carimbo, "2002", 50), anim="stamp")
    obj(c, t, 761.5, 1450, 520, lambda c: mecha_i(c, 0.9))
    pl(c, t, 763.0, 1450, 720, "\"PARECIDO\"", "COM A FAMÍLIA", 36)
    if t > 767.3:
        grande(c, t, 767.3, "A DISCUSSÃO RECOMEÇA", 1150, 900, 52, col=(0.98, 0.82, 0.50))


def s45(c, t):  # 769.67 - 798.81  2024: Walther Parson
    laboratorio(c, t)
    c.save(); c.translate(1640, 500); dna_i(c, t, 440, 140); c.restore()
    HI(c, t, ((0, "present"), (796.5, "point_r")), ((0, "neutral"), (789.4, "think"), (796.5, "shocked")))
    show(c, t, 769.9, 1000, 200, sc(carimbo, "2024", 56), anim="stamp")
    rotulo(c, t, 773.0, "WALTHER PARSON", "Universidade de Innsbruck", x=700, y=330, size=52)
    for i, x in enumerate((850, 1000, 1150)):
        obj(c, t, 778.0 + i * 0.4, x, 560, lambda c: mecha_i(c, 0.6))
    pl(c, t, 783.2, 1000, 760, "AS AMOSTRAS COMBINAM", "ENTRE SI E COM A DE 1996", 34, t1=789.2)
    pl(c, t, 789.4, 1000, 760, "LINHAGEM MATERNA", "BEM DIFERENTE DA DE BADEN", 36, t1=796.3)
    grande(c, t, 796.6, "ELE NÃO ERA O PRÍNCIPE", 1050, 880, 64, col=(0.98, 0.82, 0.50))


def s46(c, t):  # 798.81 - 817.50  não prova que era impostor; identidade desconhecida
    laboratorio(c, t)
    HI(c, t, ((0, "finger_up"), (813.6, "shrug")), ((0, "think"), (813.6, "sad")))
    pl(c, t, 799.0, 1150, 220, "OS CIENTISTAS AVISAM:", None, 42)
    pl(c, t, 803.5, 1150, 370, "ISSO NÃO PROVA", "QUE ELE ERA UM IMPOSTOR", 38)
    pl(c, t, 806.3, 1150, 540, "PODE TER SIDO", "VÍTIMA DE UM CRIME", 38, t1=813.4)
    grande(c, t, 813.6, "IDENTIDADE: DESCONHECIDA", 1150, 620, 62, col=(0.98, 0.82, 0.50))


def s47(c, t):  # 817.50 - 828.65  a pedra no jardim
    jardim(c, t, "crepusculo", neve=False, seed=37)
    pedra_memorial(c, 1300, 1000, ["HIC OCCULTUS", "OCCULTO", "OCCISUS EST", "", "XIV DEC", "MDCCCXXXIII"], s=1.15, size=28)
    HI(c, t, ((0, "present"),), ((0, "neutral"), (824.4, "sad")))
    rotulo(c, t, 817.7, "JARDIM DO PALÁCIO", "Ansbach", x=700, y=170, size=54)
    pl(c, t, 824.5, 1050, 330, "\"AQUI, UM DESCONHECIDO", "FOI MORTO POR UM DESCONHECIDO\"", 36)
    nevoa_i(c, t, 950, 0.3)


def s48(c, t):  # 828.65 - 846.20  e você?
    nuremberg(c, t, "crepusculo", seed=38)
    HI(c, t, ((0, "present"), (830.5, "think"), (843.0, "point_r")), ((0, "happy"), (830.5, "think"), (843.0, "happy")))
    grande(c, t, 828.8, "E VOCÊ?", 1150, 190, 110)
    qs = [(833.5, "UMA CRIANÇA ESCONDIDA?"), (836.3, "UM RAPAZ QUE INVENTOU A LENDA?"), (839.4, "ALGUÉM QUE PRECISAVAM ESCONDER?")]
    for i, (tt, s_) in enumerate(qs):
        pl(c, t, tt, 1150 + (i - 1) * 50, 360 + i * 120, s_, None, 36, rot=0.02 * (-1) ** i)
    pl(c, t, 843.1, 1150, 760, "DEIXE SUA TEORIA NOS COMENTÁRIOS", None, 38)


def s49(c, t):  # 846.20 - fim  encerramento
    nuremberg(c, t, "noite", seed=39)
    nevoa_i(c, t, 900, 0.4)
    HI(c, t, ((0, "stand"), (846.4, "present"), (849.0, "wave"), (851.6, "stand")), ((0, "neutral"), (847.8, "happy")))
    grande(c, t, 846.4, "Eu sou o Historiador.", 1000, 300, 56, col=(0.98, 0.82, 0.50))
    show(c, t, 848.0, 1000, 470, sc(subscribe_btn, t > 849.5, s=0.9))
    show(c, t, 848.4, 1330, 470, sc(bell, s=0.8), rot=math.sin(t * 18) * 0.2 * max(0, 1 - (t - 848.4)))
    if t > 849.0:
        p = ease_out(prog(t, 849.0, 1.2))
        rglow(c, 1100, 700, 420, AMBER, 0.2 * p)
        titulo_i(c, "PONTO CEGO", 1100, 740, 110)
        c.rectangle(1100 - 300 * p, 770, 600 * p, 4); rgb(c, AMBER); c.fill()


SCENES = [
    (0.0, 10.57, s01), (10.57, 19.94, s02), (19.94, 29.70, s03), (29.70, 35.92, s04), (35.92, 53.41, s05),
    (53.41, 63.55, s06), (63.55, 74.03, s07), (74.03, 79.45, s08), (79.45, 98.57, s09), (98.57, 121.21, s10),
    (121.21, 146.93, s11), (146.93, 161.88, s12), (161.88, 182.50, s13), (182.50, 199.6, s14),
    (199.6, 214.15, s15), (214.15, 231.91, s16), (231.91, 255.99, s17), (255.99, 273.96, s18), (273.96, 299.53, s19),
    (299.53, 320.35, s20), (320.35, 334.62, s21), (334.62, 355.19, s22), (355.19, 371.63, s23), (371.63, 385.67, s24),
    (385.67, 396.04, s25), (396.04, 414.20, s26), (414.20, 436.23, s27), (436.23, 448.25, s28), (448.25, 473.93, s29),
    (473.93, 490.89, s30), (490.89, 514.99, s31), (514.99, 530.12, s32), (530.12, 549.28, s33), (549.28, 562.57, s34),
    (562.57, 587.45, s35),
    (587.45, 607.41, s36), (607.41, 618.52, s37), (618.52, 633.52, s38), (633.52, 658.64, s39), (658.64, 664.87, s40),
    (664.87, 691.09, s41), (691.09, 720.18, s42), (720.18, 742.58, s43), (742.58, 769.67, s44), (769.67, 798.81, s45),
    (798.81, 817.50, s46), (817.50, 828.65, s47), (828.65, 846.20, s48), (846.20, 999.0, s49),
]
