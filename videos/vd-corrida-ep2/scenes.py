"""VOCÊ DECIDE · A ÚLTIMA CORRIDA · EP. 2 (TikTok vertical). Vocês escolheram B no ep. 1."""
from engine import *
VERTICAL = True
from ilustrado import *
from pov import *
import ilustrado

STYLE = "ilustrado"
TOM = "sombrio"
THEME = "cidade"
AMBIENCE = "terror"

LN = linhas(__file__)
T = LN.t0
LUGAR = "CEMITÉRIO DA CONSOLAÇÃO · 03:03"


def topo(c, t, lugar=LUGAR):
    selo_ep(c, "EP. 2")
    tag_local(c, t, lugar)


def abertura(t):
    return ease_io(prog(t, T(1) + 0.4, 2.6))


def antonio_entrando(t0, t1):
    """Seu Antônio passa pelo vão do portão e some na névoa"""
    def f(c, t):
        if t < t0:
            return
        k = min(1.0, (t - t0) / (t1 - t0))
        a = 1.0 - max(0.0, (k - 0.6) / 0.4)
        if a <= 0.02:
            return
        old = ilustrado._L
        ilustrado._L = LUZES["nublado"]
        boneco(c, t, 20 - 40 * k, -10 - 60 * k, 0.75 - 0.35 * k, look=0.0, andar=True, alpha=a,
               prop=("r", lambda c, tt: flores_i(c, 0.9)), **SENHOR)
        ilustrado._L = old
        nevoa_i(c, t, -120, 0.5, n=4, seed=5)
    return f


def gate_scene(c, t, dentro=None, aberto=None, retro=None, cel=None):
    ab = abertura(t) if aberto is None else aberto

    def fora(c, t):
        estrada_noite(c, t, 0.0, fim=lambda c, t, hz: portao_cemiterio(c, t, W / 2, hz + 420, 0.95, abertura=ab, dentro=dentro))
        nevoa_i(c, t, 980, 0.45, seed=2)
    carro_pov(c, t, fora, retrovisor=retro or banco_tras(False, False), celular=cel, painel_luz=piscar(t, 3))


def s01(c, t):  # parados no portão fechado
    gate_scene(c, t, aberto=0.0, cel=tela_corrida("aguardando", espera="09:40", hora="03:03"))
    resultado_voto(c, t, "B", "LEVAR ATÉ O PORTÃO", t1=3.4)
    topo(c, t)


def s02(c, t):  # o portão abre sozinho
    gate_scene(c, t, cel=tela_corrida("aguardando", espera="09:52", hora="03:03"))
    topo(c, t)


def s03(c, t):  # retrovisor: as flores sumiram, banco gelado
    k = ease_io(prog(t, T(2) - 0.2, 0.8))
    z = 1 + 0.75 * k
    c.save(); c.translate(W / 2, 345 + (760 - 345) * k); c.scale(z, z); c.translate(-W / 2, -345)
    gate_scene(c, t, aberto=1.0, retro=banco_tras(False, False))
    c.restore()
    if t > T(3):
        kk = min(1.0, (t - T(3)) / 1.5)
        c.rectangle(0, 0, W, H); rgb(c, (0.55, 0.70, 1.0), 0.12 * kk); c.fill()
        for lado in (0, 1):
            g = cairo.RadialGradient(lado * W, 760, 60, lado * W, 760, 560)
            g.add_color_stop_rgba(0, 0.85, 0.92, 1.0, 0.5 * kk); g.add_color_stop_rgba(1, 0.85, 0.92, 1.0, 0)
            c.set_source(g); c.paint()
    topo(c, t)


SUSTO1 = T(6) + 0.75   # logo depois do "Tô em casa": ele está no banco de trás


def s04(c, t):  # a voz dele vem de fora: ele entra no cemitério... e aparece atrás de você
    if t >= SUSTO1:
        close_terror(c, t, SUSTO1, olhos_="vazios")
        return
    gate_scene(c, t, aberto=1.0, dentro=antonio_entrando(T(4) - 0.4, T(6) - 0.1))
    topo(c, t)


def s05(c, t):  # o Pix
    gate_scene(c, t, aberto=1.0)
    c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.6); c.fill()
    tela = tela_pix(aviso="Conta encerrada em 2006", t_aviso=T(9) + 1.0) if t >= T(8) - 0.3 else tela_bloqueio(
        "03:04", "terça-feira, 10 de novembro", (("Banco", "Pix recebido · R$ 40,00"),))
    celular_mao(c, t, tela, y=900, s=1.12)
    topo(c, t)


def s06(c, t):  # "eu sempre paguei" — o vulto parado na névoa, olhando
    def dentro(c, t):
        silhueta(c, t, 0, -40, 0.42, 0.85, olhos=True)
        nevoa_i(c, t, -120, 0.45, n=4, seed=5)
    gate_scene(c, t, aberto=1.0, dentro=dentro)
    topo(c, t)


def s07(c, t):  # nova corrida: destino a sua casa
    gate_scene(c, t, aberto=1.0)
    c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.6); c.fill()
    celular_mao(c, t, tela_corrida("pedido", passageiro="Seu Antônio", embarque="Cemitério da Consolação",
                                   destino="Minha casa", valor="R$ 40,00", hora="03:05", recusar=True,
                                   destaque=T(13) + 2.4), y=900, s=1.12)
    topo(c, t, "CEMITÉRIO DA CONSOLAÇÃO · 03:05")


SUSTO2 = T(15) + 1.25  # "...conhecer a SUA CASA": os olhos ficam pretos


def s08(c, t):  # ele está de volta no banco de trás; a câmera vai até o retrovisor
    quem = dict(SENHOR); quem["olhos"] = lambda tt: "normal" if tt < SUSTO2 else "pretos"
    expr = lambda tt: "happy" if tt < SUSTO2 else "sinistro"
    k = ease_io(prog(t, T(15) - 0.6, SUSTO2 - T(15) + 0.6)) * (1 - ease_io(prog(t, T(16) - 0.6, 0.6)))
    z = 1 + 2.0 * k
    sh = 10 * max(0, 1 - (t - SUSTO2) / 0.4) if t >= SUSTO2 else 0
    c.save(); c.translate(math.sin(t * 90) * sh, 0)
    c.translate(W / 2, 345 + (900 - 345) * k); c.scale(z, z); c.translate(-W / 2, -345)
    gate_scene(c, t, aberto=1.0, retro=banco_tras(True, True, quem=quem, expr=expr, look=0.0),
               cel=tela_corrida("pedido", passageiro="Seu Antônio", destino="Minha casa", recusar=True, hora="03:05"))
    c.restore()
    if SUSTO2 <= t < SUSTO2 + 0.15:
        c.set_source_rgba(1, 1, 1, 0.7 * (1 - (t - SUSTO2) / 0.15)); c.paint()
    topo(c, t, "CEMITÉRIO DA CONSOLAÇÃO · 03:05")
    cartao_escolha(c, t, T(16) - 0.2, "ACEITA OU RECUSA?", "RECUSAR A CORRIDA", "ACEITAR E LEVAR ELE",
                   segundos=LN.dur - T(16) - 0.4, nota="O mais votado vira o Ep. 3")


def _com_legenda(fn):
    def g(c, t):
        fn(c, t)
        legendas(c, t, LN, y=1500 if t < T(16) - 0.2 else 1720)
    return g


SCENES = [(0, T(1) - 0.2, _com_legenda(s01)),
          (T(1) - 0.2, T(2) - 0.2, _com_legenda(s02)),
          (T(2) - 0.2, T(4) - 0.3, _com_legenda(s03)),
          (T(4) - 0.3, T(7) - 0.2, _com_legenda(s04)),
          (T(7) - 0.2, T(11) - 0.2, _com_legenda(s05)),
          (T(11) - 0.2, T(12) - 0.2, _com_legenda(s06)),
          (T(12) - 0.2, T(15) - 0.2, _com_legenda(s07)),
          (T(15) - 0.2, 999.0, _com_legenda(s08))]

# sons de terror (tonais, sem ruído). Cama: AMBIENCE = "terror". 2 sustos: SUSTO1 e SUSTO2.
SFX = [(T(1) + 0.3, "sino_funebre"),                      # o portão abre sozinho
       (T(2) + 1.4, "tum"),                               # as flores sumiram
       (T(4) - 0.2, "coracao_acelerando:%.2f" % (SUSTO1 - T(4) + 0.2)),
       (SUSTO1 - 3.0, "cordas_subindo"), (SUSTO1, "susto"),
       (T(7) + 0.05, "vibra_celular"),                    # aí o celular vibrou
       (T(9) + 1.2, "tum"),                               # conta encerrada em 2006
       (T(12) + 0.25, "vibra_celular"),                   # vibrou de novo
       (T(14) + 0.2, "coracao_acelerando:%.2f" % (SUSTO2 - T(14) - 0.2)),
       (SUSTO2 - 3.0, "cordas_subindo"), (SUSTO2, "susto"),
       (T(16) - 0.2, "sino_funebre")]                     # cartão da escolha
