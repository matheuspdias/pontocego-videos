"""O Homem de Somerton / caso Tamám Shud (1948). TikTok nativo (roteiro próprio, 74,0 s), estilo ilustrado.
Cena 16:9 que o tiktok.py enquadra no vertical: letras grandes e nada importante fora de x 140-1780.
Narração Pedro Lima - Serious (HeyGen, ElevenLabs v4), 1 bloco. Fontes no roteiro.txt.
Sem mostrar o corpo: a cena da praia usa só o chapéu e as pegadas."""
from engine import *
from ilustrado import *

STYLE = "ilustrado"
TOM = "misterioso"
THEME = "classico"
SFX_OFF = True
SFX = [(2.6, "boom"), (25.5, "impact"), (36.9, "thud"), (44.3, "impact"), (55.6, "ding"), (73.4, "boom")]

CODIGO = ["WRGOABABD", "MLIAOI", "WTBIMPANETP", "MLIABOAIAQC", "ITTMTSAMSTGAB"]


def grande(c, t, t0, s, x=960, y=200, size=110, col=(0.98, 0.95, 0.88)):
    if t < t0:
        return
    p = ease_out(prog(t, t0, 0.4))
    c.save(); c.translate(0, 24 * (1 - p)); titulo_i(c, s, x, y, size, col); c.restore()


def chapeu_areia(c, x, y, s=1.0):
    c.save(); c.translate(x, y); c.scale(s, s)
    ellipse(c, 0, 8, 120, 26); rgb(c, (0, 0, 0), 0.25); c.fill()
    ellipse(c, 0, 0, 115, 24); rgb(c, P((0.30, 0.26, 0.22))); c.fill()
    pg(c, [(-62, -2), (-50, -70), (50, -70), (62, -2)]); rgb(c, P((0.34, 0.30, 0.25))); c.fill()
    c.rectangle(-58, -24, 116, 14); rgb(c, P((0.14, 0.12, 0.10))); c.fill()
    c.restore()


def livro_capa(c, titulo="RUBAIYAT", w=360, h=500, rasgado=False):
    """livro fechado de capa dura (centrado na origem)"""
    rr(c, -w / 2 + 12, -h / 2 + 14, w, h, 10); rgb(c, (0, 0, 0), 0.3); c.fill()
    rr(c, -w / 2, -h / 2, w, h, 10); rgb(c, P((0.40, 0.16, 0.14))); c.fill()
    rr(c, -w / 2 + 24, -h / 2 + 24, w - 48, h - 48, 6); rgb(c, P((0.86, 0.70, 0.36)), 0.8); c.set_line_width(4); c.stroke()
    c.select_font_face(SERIF, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(54)
    e = c.text_extents(titulo); c.move_to(-e.x_advance / 2, -40); rgb(c, P((0.92, 0.78, 0.44))); c.show_text(titulo)
    c.set_font_size(30); e = c.text_extents("Omar Khayyám"); c.move_to(-e.x_advance / 2, 20); c.show_text("Omar Khayyám")


def s01(c, t):  # 0 - 8.1  gancho
    cena_praia(c, t, "crepusculo")
    for i in range(7):  # pegadas
        ellipse(c, 1400 - i * 70, 1000 - i * 18 + (i % 2) * 20, 18, 9); rgb(c, (0, 0, 0), 0.18); c.fill()
    chapeu_areia(c, 1050, 930, 1.1)
    historiador_i(c, t, 380, 1050, 1.05, poses=((0, "point_r"), (5.8, "think")), exprs=((0, "worried"), (5.8, "think")), look=0.6)
    grande(c, t, 0.1, "1948", 960, 170, 130, (0.95, 0.70, 0.30))
    if t > 2.6:
        c.save(); c.translate(1200, 340); placa(c, "UM HOMEM SEM NOME", size=64); c.restore()
    if t > 5.8:
        c.save(); c.translate(1200, 500); placa(c, "SEM NENHUM DOCUMENTO", size=54); c.restore()


def s02(c, t):  # 8.1 - 17.9  Somerton, Adelaide
    cena_praia(c, t, "dia")
    boneco(c, t, 1320, 1040, 1.0, poses=((0, "think_l"),), exprs=((0, "think"),), look=-0.5, fid=12, **FIGURINO["cavalheiro"])
    historiador_i(c, t, 380, 1050, 1.05, poses=((0, "present"), (14.8, "shrug")), exprs=((0, "neutral"), (14.8, "worried")), look=0.6)
    rotulo(c, t, 8.6, "1º DE DEZEMBRO", "Somerton, Adelaide · Austrália", x=200, y=200, size=70)
    if t > 12.7:
        c.save(); c.translate(1250, 300); placa(c, "QUEM ERA ELE?", size=60); c.restore()
    if t > 15.0:
        c.save(); c.translate(1250, 440); placa(c, "DO QUE MORREU?", size=60); c.restore()


def s03(c, t):  # 17.9 - 29.4  o papel no bolso escondido
    luz("vela")
    interior(c, t, "madeira", "madeira", janela=None)
    mesa_i(c, 960, 900, 1100)
    historiador_i(c, t, 330, 1050, 1.0, poses=((0, "hold"), (25.5, "point_r")), exprs=((0, "think"), (25.5, "shocked")), look=0.6, lanterna=False)
    rotulo(c, t, 18.2, "MESES DEPOIS", "um bolsinho escondido na calça", x=200, y=200, size=66)
    if t > 22.4:
        p = ease_out_back(prog(t, 22.4, 0.5))
        c.save(); c.translate(1150, 560); c.scale(p, p); papel_nota(c, ["TAMÁM SHUD"], 700, 200, 96, rasgado=True); c.restore()
    if t > 27.9:
        c.save(); c.translate(1150, 800); placa(c, "= TERMINADO", size=64); c.restore()


def s04(c, t):  # 29.4 - 37.8  o livro de poemas
    cena_interior(c, t, "vela", "biblioteca")
    c.save(); c.translate(1250, 560); livro_capa(c); c.restore()
    if t > 30.4:  # página arrancada
        c.save(); c.translate(1520, 760); c.rotate(0.2); papel_nota(c, ["última página"], 300, 140, 40, rasgado=True); c.restore()
    historiador_i(c, t, 380, 1050, 1.05, poses=((0, "point_r"), (36.9, "arms_up")), exprs=((0, "think"), (36.9, "shocked")), look=0.6, lanterna=False)
    grande(c, t, 29.6, "O LIVRO DE POEMAS", 1150, 190, 90)
    if t > 36.9:
        c.save(); c.translate(1250, 960); placa(c, "O LIVRO APARECEU", size=60); c.restore()


def s05(c, t):  # 37.8 - 45.4  o código
    luz("vela")
    interior(c, t, "madeira", "madeira", janela=None)
    c.save(); c.translate(1150, 540)
    w, h = 900, 680
    rr(c, -w / 2 + 12, -h / 2 + 14, w, h, 10); rgb(c, (0, 0, 0), 0.3); c.fill()
    rr(c, -w / 2, -h / 2, w, h, 10); rgb(c, (0.95, 0.91, 0.80)); c.fill()
    c.select_font_face(TYPE); c.set_font_size(46)
    if t > 40.3:
        c.move_to(-400, -260); rgb(c, (0.35, 0.30, 0.25), 0.8); c.show_text("telefone: ••••••")
    for i, s_ in enumerate(CODIGO):
        if t > 41.9 + i * 0.35:
            c.set_font_size(66); e = c.text_extents(s_)
            c.move_to(-e.x_advance / 2, -140 + i * 100); rgb(c, (0.20, 0.17, 0.15), 0.85); c.show_text(s_)
            if i == 1:
                line(c, -e.x_advance / 2, -160 + i * 100, e.x_advance / 2, -160 + i * 100, 5, (0.20, 0.17, 0.15))
    c.restore()
    historiador_i(c, t, 330, 1050, 1.0, poses=((0, "point_r"), (44.3, "think")), exprs=((0, "think"), (44.3, "shocked")), look=0.6, lanterna=False)
    if t > 44.3:
        grande(c, t, 44.3, "UM CÓDIGO", 1150, 1000, 100, (0.95, 0.70, 0.30))


def s06(c, t):  # 45.4 - 60.9  70 anos depois: DNA
    luz("interior")
    interior(c, t, "reboco", "madeira", janela="reta", jx=1600)
    k = ease_out(prog(t, 46.0, 2.5))
    titulo_i(c, str(int(1948 + (2022 - 1948) * k)), 1150, 260, 150, (0.95, 0.70, 0.30))
    if t > 50.8:
        c.save(); c.translate(900, 600); dna_i(c, t, 420, 130); c.restore()
    if t > 55.6:
        c.save(); c.translate(1350, 560); placa(c, "CARL WEBB?", "ENGENHEIRO DE MELBOURNE", size=70); c.restore()
    if t > 58.3:
        c.save(); c.translate(1300, 900); placa(c, "SEM CONFIRMAÇÃO DA POLÍCIA", size=46); c.restore()
    historiador_i(c, t, 330, 1050, 1.0, poses=((0, "stand"), (51.0, "point_r")), exprs=((0, "neutral"), (51.0, "confident"), (58.3, "think")), look=0.6, lanterna=False)


def s07(c, t):  # 60.9 - 68.4  as perguntas que sobram
    cena_praia(c, t, "noite")
    nevoa_i(c, t, 860, 0.35)
    chapeu_areia(c, 1450, 960, 0.9)
    historiador_i(c, t, 380, 1050, 1.05, poses=((0, "finger_up"), (66.2, "shrug")), exprs=((0, "think"), (66.2, "worried")), look=0.6)
    if t > 63.4:
        c.save(); c.translate(1150, 230); placa(c, "DO QUE ELE MORREU?", size=64); c.restore()
    if t > 64.8:
        c.save(); c.translate(1150, 390); placa(c, "O QUE DIZ O CÓDIGO?", size=64); c.restore()
    if t > 66.4:
        grande(c, t, 66.4, "NINGUÉM DECIFROU", 1150, 620, 92, (0.95, 0.70, 0.30))


def s08(c, t):  # 68.4 - fim  espião, crime ou outra coisa?
    cena_praia(c, t, "noite")
    historiador_i(c, t, 380, 1050, 1.05, poses=((0, "present"), (73.4, "point_r")), exprs=((0, "think"), (73.4, "confident")), look=0.6)
    grande(c, t, 68.6, "E VOCÊ, O QUE ACHA?", 980, 170, 92)
    for i, (t0, s_) in enumerate(((70.6, "ESPIÃO"), (71.7, "CRIME"), (72.3, "OUTRA COISA"))):
        if t > t0:
            c.save(); c.translate(1200, 340 + i * 150); placa(c, s_, w=560, size=66); c.restore()
    if t > 73.4:
        grande(c, t, 73.4, "COMENTA", 1200, 900, 110, (0.95, 0.70, 0.30))


SCENES = [(0, 8.1, s01), (8.1, 17.9, s02), (17.9, 29.4, s03), (29.4, 37.8, s04), (37.8, 45.4, s05),
          (45.4, 60.9, s06), (60.9, 68.4, s07), (68.4, 999.0, s08)]
