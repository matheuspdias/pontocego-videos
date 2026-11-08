"""Os faroleiros que sumiram das Ilhas Flannan (1900). TikTok nativo (roteiro próprio, 70,2 s), estilo ilustrado.
Cena 16:9 que o tiktok.py enquadra no vertical: letras grandes e nada importante fora de x 140-1780.
Narração Pedro Lima - Serious (HeyGen, ElevenLabs v4), 1 bloco. Fontes no roteiro.txt."""
from engine import *
from ilustrado import *

STYLE = "ilustrado"
TOM = "misterioso"
THEME = "mar"
SFX_OFF = True
SFX = [(5.3, "boom"), (16.5, "thud"), (22.9, "impact"), (43.6, "boom"), (48.8, "whoosh"), (62.7, "impact")]


def grande(c, t, t0, s, x=960, y=200, size=110, col=(0.98, 0.95, 0.88)):
    if t < t0:
        return
    p = ease_out(prog(t, t0, 0.4))
    c.save(); c.translate(0, 24 * (1 - p)); titulo_i(c, s, x, y, size, col); c.restore()


def sala_farol(c, t, hora="vela"):
    """sala de pedra dos faroleiros (sem estante): parede de pedra, piso de pedra, janela para o mar"""
    luz(hora)
    interior(c, t, "pedra", "pedra", janela="reta", jx=1560)


def cabide(c, t, x, y, casacos=(False, False, True)):
    """três ganchos na parede; casacos=True onde ainda há casaco pendurado"""
    rr(c, x - 330, y - 20, 660, 40, 6); rgb(c, P(MADEIRA_ESC)); c.fill()
    for i, tem in enumerate(casacos):
        xx = x - 220 + i * 220
        c.new_sub_path(); c.arc(xx, y + 30, 16, 0, math.pi); rgb(c, P((0.30, 0.30, 0.32))); c.set_line_width(8); c.stroke()
        if tem:
            col = P((0.86, 0.68, 0.22))
            pg(c, [(xx - 40, y + 44), (xx + 40, y + 44), (xx + 95, y + 400), (xx - 95, y + 400)]); rgb(c, col); c.fill()
            pg(c, [(xx - 40, y + 44), (xx - 95, y + 250), (xx - 70, y + 260), (xx - 20, y + 90)]); rgb(c, dk(col, 0.18)); c.fill()
            line(c, xx, y + 60, xx, y + 400, 4, dk(col, 0.35))
        else:
            ellipse(c, xx, y + 230, 70, 150); rgb(c, (0, 0, 0), 0.10); c.fill()


def s01(c, t):  # 0 - 7.8  gancho: farol apagado no meio do mar
    cena_ilha_farol(c, t, "noite", aceso=False)
    nevoa_i(c, t, 760, 0.35)
    historiador_i(c, t, 380, 1040, 1.0, poses=((0, "point_r"),), exprs=((0, "worried"),), look=0.6)
    grande(c, t, 0.1, "DEZEMBRO DE 1900", 820, 150, 104)
    rotulo(c, t, 2.6, "ILHAS FLANNAN", "Escócia", x=200, y=300, size=70)
    if t > 5.2:
        c.save(); c.translate(1250, 960); placa(c, "10 NOITES APAGADO", size=64); c.restore()


def s02(c, t):  # 7.8 - 16.3  o Hesperus chega; ninguém no cais
    cena_ilha_farol(c, t, "nublado", aceso=False, x=1420)
    k = ease_out(prog(t, 8.6, 4.0))
    c.save(); c.translate(1500 - 600 * k, 860); vapor(c, t, 0.75); c.restore()
    historiador_i(c, t, 360, 1040, 1.0, poses=((0, "present"), (13.0, "shrug")), exprs=((0, "neutral"), (13.0, "worried")), look=0.6)
    rotulo(c, t, 8.6, "26 DE DEZEMBRO", "o navio Hesperus", x=200, y=230, size=70)
    if t > 13.0:
        c.save(); c.translate(1150, 990); placa(c, "NINGUÉM NO CAIS", size=64); c.restore()


def s03(c, t):  # 16.3 - 24.9  dentro do farol: tudo em ordem, ninguém
    sala_farol(c, t, "interior")
    mesa_i(c, 1250, 860, 560)
    c.save(); c.translate(1100, 846); lanterna_i(c, t, 1.3, acesa=False); c.restore()
    historiador_i(c, t, 380, 1050, 1.05, poses=((0, "point_r"), (22.9, "hold")), exprs=((0, "think"), (22.9, "shocked")), look=0.6, lanterna=False)
    itens = ((16.5, "PORTÃO FECHADO"), (18.2, "LÂMPADAS PRONTAS"), (21.0, "COZINHA ARRUMADA"))
    for i, (t0, s) in enumerate(itens):
        if t0 < t < 22.9:
            c.save(); c.translate(1220, 200 + i * 130); placa(c, s, w=760, size=54); c.restore()
    if t > 22.9:
        c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.6 * ease_out(prog(t, 22.9, 0.4))); c.fill()
        grande(c, t, 22.9, "E OS 3 FAROLEIROS?", 960, 560, 120, (0.95, 0.70, 0.30))


def s04(c, t):  # 24.9 - 35.0  dois casacos sumiram, um ficou
    sala_farol(c, t, "vela")
    cabide(c, t, 1150, 230)
    if t > 25.3:
        for i in range(2):
            c.save(); c.translate(930 + i * 220, 470); big_x(c, 70, RED, 16); c.restore()
    historiador_i(c, t, 380, 1050, 1.05, poses=((0, "point_r"), (30.0, "think")), exprs=((0, "worried"), (30.0, "think")), look=0.6, lanterna=False)
    if t > 30.0:
        c.save(); c.translate(1150, 820); placa(c, "UM SAIU SEM CASACO", size=64); c.restore()


def s05(c, t):  # 35.0 - 39.6  o quadro de giz
    sala_farol(c, t, "vela")
    c.save(); c.translate(1200, 450); quadro_giz(c, ["15 DE DEZEMBRO", "9 DA MANHÃ"], 760, 380, 76); c.restore()
    historiador_i(c, t, 380, 1050, 1.05, poses=((0, "point_r"),), exprs=((0, "think"),), look=0.6, lanterna=False)
    rotulo(c, t, 35.5, "O ÚLTIMO REGISTRO", None, x=760, y=820, size=64)


def s06(c, t):  # 39.6 - 47.0  o desembarque oeste destruído
    luz("nublado")
    ceu(c, t, seed=5)
    mar_i(c, t, 760)
    ilha_rochosa(c, 1100, 900, 1600, 360, seed=31, grama=False)
    for i in range(9):  # grade torcida
        xx = 820 + i * 70
        dy = math.sin(i * 1.3) * 40 if i > 3 else 0
        line(c, xx, 600, xx + dy, 690, 7, P((0.25, 0.25, 0.27)))
    c.move_to(820, 600)
    for i in range(9):
        c.line_to(820 + i * 70, 600 + (math.sin(i * 1.7) * 50 if i > 3 else 0))
    rgb(c, P((0.25, 0.25, 0.27))); c.set_line_width(8); c.stroke()
    if t > 43.6:
        p = ease_out(prog(t, 43.6, 0.5))
        c.save(); c.translate(1500, 560 - 40 * (1 - p)); ellipse(c, 0, 0, 110, 80); rgb(c, P((0.48, 0.46, 0.44))); c.fill(); c.restore()
        c.save(); c.translate(1500, 380); placa(c, "+ 1 TONELADA", size=60); c.restore()
    historiador_i(c, t, 340, 1050, 1.0, poses=((0, "point_r"),), exprs=((0, "shocked"),), look=0.6)
    rotulo(c, t, 40.0, "O LADO OESTE", "grade de ferro torcida", x=200, y=220, size=70)
    relampago(c, t, (40.4,), raio_x=1500)
    escurecer(c, 0.12, 0.4)


def s07(c, t):  # 47.0 - 53.0  a onda gigante; corpos nunca achados
    luz("nublado")
    ceu(c, t, seed=6)
    mar_i(c, t, 760)
    ilha_rochosa(c, 1300, 900, 1300, 300, seed=32, grama=False)
    onda_gigante(c, t, 48.6, 900, 980, 1500, 640)
    historiador_i(c, t, 300, 1050, 1.0, poses=((0, "stand"), (48.8, "head")), exprs=((0, "worried"), (48.8, "shocked")), look=0.6)
    grande(c, t, 47.4, "UMA ONDA GIGANTE?", 1050, 200, 104)
    if t > 50.7:
        c.save(); c.translate(1150, 360); placa(c, "CORPOS NUNCA ENCONTRADOS", size=56); c.restore()


def s08(c, t):  # 53.0 - 64.4  o diário dramático é invenção
    sala_farol(c, t, "vela")
    mesa_i(c, 1200, 880, 640)
    c.save(); c.translate(1200, 520)
    papel_nota(c, ["ventos nunca vistos...", "McArthur chorando", "os três rezando"], 780, 380, 56, font=TYPE, rasgado=False)
    c.restore()
    if t > 62.7:
        p = ease_out_back(prog(t, 62.7, 0.4))
        c.save(); c.translate(1200, 540); c.rotate(-0.12); c.scale(p, p)
        rr(c, -330, -70, 660, 140, 14); rgb(c, (0.80, 0.14, 0.12)); c.set_line_width(12); c.stroke()
        c.select_font_face(SERIF, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(96)
        e = c.text_extents("INVENTADO"); c.move_to(-e.x_advance / 2, 34); rgb(c, (0.80, 0.14, 0.12)); c.show_text("INVENTADO")
        c.restore()
    historiador_i(c, t, 360, 1050, 1.05, poses=((0, "finger_up"), (60.3, "point_r")), exprs=((0, "think"), (60.3, "confident")), look=0.6, lanterna=False)
    grande(c, t, 53.4, "O DIÁRIO FAMOSO", 1200, 200, 96)


def s09(c, t):  # 64.4 - fim  a pergunta
    cena_ilha_farol(c, t, "noite", aceso=True)
    nevoa_i(c, t, 800, 0.3)
    silhueta(c, t, 1470, 575, 0.22, alpha=0.85)
    historiador_i(c, t, 380, 1040, 1.0, poses=((0, "present"), (69.0, "point_r")), exprs=((0, "think"), (69.0, "confident")), look=0.6)
    grande(c, t, 64.6, "POR QUE SEM CASACO?", 800, 160, 96)
    if t > 69.0:
        c.save(); c.translate(1150, 980); placa(c, "QUAL É A SUA TEORIA?", size=64); c.restore()


SCENES = [(0, 7.8, s01), (7.8, 16.3, s02), (16.3, 24.9, s03), (24.9, 35.0, s04), (35.0, 39.6, s05),
          (39.6, 47.0, s06), (47.0, 53.0, s07), (53.0, 64.4, s08), (64.4, 999.0, s09)]
