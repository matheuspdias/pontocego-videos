"""VOCÊ DECIDE · A ÚLTIMA CORRIDA · EP. 1 (TikTok vertical). Tempos vêm de linhas.json (montar_falas.py)."""
from engine import *
VERTICAL = True
from ilustrado import *
from pov import *

STYLE = "ilustrado"
TOM = "misterioso"
THEME = "cidade"
SFX_OFF = True

LN = linhas(__file__)
T = LN.t0  # início da fala i


def topo(c, t, lugar):
    selo_ep(c, "EP. 1")
    tag_local(c, t, lugar)


def tela_ociosa(c, t, w, h):
    c.rectangle(0, 0, w, h); rgb(c, (0.15, 0.17, 0.21)); c.fill()
    c.select_font_face(FONTE); c.set_font_size(w * 0.09)
    c.move_to(w * 0.1, h * 0.5); rgb(c, (0.8, 0.85, 0.95)); c.show_text("Online")
    c.set_font_size(w * 0.06); c.move_to(w * 0.1, h * 0.58); rgb(c, (0.6, 0.65, 0.75)); c.show_text("procurando...")
    k = (t * 0.7) % 1
    c.new_sub_path(); c.arc(w / 2, h * 0.3, w * 0.1 + w * 0.25 * k, 0, 6.283); rgb(c, (0.3, 0.6, 1.0), 0.6 * (1 - k)); c.set_line_width(4); c.stroke()


def s01(c, t):  # dirigindo de madrugada
    carro_pov(c, t, lambda c, t: estrada_noite(c, t, 1.0), retrovisor=banco_tras(False, False), celular=tela_ociosa)
    topo(c, t, "SÃO PAULO · 02:47")
    aviso_lenda(c, t)


def s02(c, t):  # a corrida chega
    estrada_noite(c, t, 0.4)
    c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.55); c.fill()
    celular_mao(c, t, tela_corrida("pedido", t_aceite=T(2) + 1.3), y=900, s=1.12)
    topo(c, t, "SÃO PAULO · 02:47")


def s03(c, t):  # o senhor de terno no poste
    t0 = T(3) - 0.6
    def fora(c, t):
        estrada_noite(c, t, max(0.0, 0.6 - (t - t0) * 0.15))
        k = min(1.0, 0.45 + (t - t0) * 0.08)
        homem_poste(c, t, W * 0.70, 760 + 420 * k, 0.55 * k + 0.2, look=-0.6)
    carro_pov(c, t, fora, retrovisor=banco_tras(False, False), celular=tela_corrida("aceita"))
    topo(c, t, "R. DA CONSOLAÇÃO · 02:53")


def s04(c, t):  # conversa: ele aparece no retrovisor; o carro gela
    expr = "happy" if T(6) <= t < T(8) or t >= T(9) else "neutral"
    carro_pov(c, t, lambda c, t: estrada_noite(c, t, 1.0),
              retrovisor=banco_tras(True, True, expr=expr, look=0.2), celular=tela_corrida("aceita"))
    if t > T(8):  # geada nas bordas do para-brisa
        k = min(1.0, (t - T(8)) / 2.5)
        for lado in (0, 1):
            x = 0 if lado == 0 else W
            g = cairo.RadialGradient(x, 700, 50, x, 700, 520)
            g.add_color_stop_rgba(0, 0.80, 0.90, 1.0, 0.45 * k); g.add_color_stop_rgba(1, 0.80, 0.90, 1.0, 0)
            c.set_source(g); c.paint()
        c.rectangle(0, 0, W, H); rgb(c, (0.55, 0.70, 1.0), 0.08 * k); c.fill()
    topo(c, t, "R. DA CONSOLAÇÃO · 02:55")


def s05(c, t):  # o app: passageiro não embarcou
    estrada_noite(c, t, 0.8)
    c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.6); c.fill()
    celular_mao(c, t, tela_corrida("aguardando", espera=f"07:{12 + int(t - T(10)):02d}"), y=900, s=1.12)
    topo(c, t, "R. DA CONSOLAÇÃO · 02:58")


def s06(c, t):  # close no retrovisor: o banco fica vazio
    vazio = t >= T(13) - 0.3
    k = ease_io(prog(t, T(12) - 0.1, 0.8))
    z = 1 + 0.75 * k
    c.save(); c.translate(W / 2, 345 + (760 - 345) * k); c.scale(z, z); c.translate(-W / 2, -345)
    carro_pov(c, t, lambda c, t: estrada_noite(c, t, 0.9), retrovisor=banco_tras(not vazio, True), balanco=False)
    c.restore()
    if abs(t - (T(13) - 0.3)) < 0.25:  # piscada no momento em que some
        c.rectangle(0, 0, W, H); rgb(c, (1, 1, 1), 0.35 * (1 - abs(t - (T(13) - 0.3)) / 0.25)); c.fill()
    topo(c, t, "R. DA CONSOLAÇÃO · 03:00")


def s07(c, t):  # o portão aparece no fim da rua
    t0 = T(14)
    def fora(c, t):
        def portao(c, t, hz):
            k = min(1.0, 0.25 + (t - t0) * 0.07)
            portao_cemiterio(c, t, W / 2, hz + 40 + 260 * k, 0.25 + 0.55 * k)
        estrada_noite(c, t, 0.7, fim=portao)
        nevoa_i(c, t, 900, 0.5, seed=2)
    luz_p = piscar(t, 2)
    carro_pov(c, t, fora, retrovisor=banco_tras(False, True, olhos=t > T(16)), celular=tela_corrida("aguardando", espera="09:40"),
              painel_luz=luz_p)
    topo(c, t, "CEMITÉRIO DA CONSOLAÇÃO · 03:01")


def s08(c, t):  # escolha
    def fora(c, t):
        estrada_noite(c, t, 0.15, fim=lambda c, t, hz: portao_cemiterio(c, t, W / 2, hz + 300, 0.8))
        nevoa_i(c, t, 900, 0.55, seed=2)
    carro_pov(c, t, fora, retrovisor=banco_tras(False, True, olhos=True), painel_luz=piscar(t, 5))
    topo(c, t, "CEMITÉRIO DA CONSOLAÇÃO · 03:01")
    cartao_escolha(c, t, T(17) - 0.2, "O QUE VOCÊ FARIA?", "PARAR O CARRO AGORA", "LEVAR ATÉ O PORTÃO",
                   segundos=LN.dur - T(17) - 0.4, nota="O mais votado vira o Ep. 2")


def legenda(c, t):
    legendas(c, t, LN, y=1500 if t < T(17) - 0.2 else 1720)


def _com_legenda(fn):
    def g(c, t):
        fn(c, t)
        legenda(c, t)
    return g


SCENES = [(0, T(1) - 0.2, _com_legenda(s01)),
          (T(1) - 0.2, T(3) - 0.5, _com_legenda(s02)),
          (T(3) - 0.5, T(5) - 0.2, _com_legenda(s03)),
          (T(5) - 0.2, T(10) - 0.2, _com_legenda(s04)),
          (T(10) - 0.2, T(12) - 0.1, _com_legenda(s05)),
          (T(12) - 0.1, T(14) - 0.2, _com_legenda(s06)),
          (T(14) - 0.2, T(17) - 0.2, _com_legenda(s07)),
          (T(17) - 0.2, 999.0, _com_legenda(s08))]

SFX = [(T(1) - 0.2, "ding"), (T(8) + 0.3, "heartbeat"), (T(10) + 0.5, "heartbeat"), (T(11) + 0.4, "tum"),
       (T(13) - 0.3, "boom"), (T(16) + 1.0, "heartbeat"), (T(17) - 0.2, "tum")]
