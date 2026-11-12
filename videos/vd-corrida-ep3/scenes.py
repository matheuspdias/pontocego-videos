"""VOCÊ DECIDE · A ÚLTIMA CORRIDA · PARTE 3 "Ele veio a pé" (TikTok vertical). Vocês escolheram A no ep. 2."""
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
VIBRA = T(3) + 1.65          # "...o celular vibrou"
ELE = T(10) + 2.95           # "...embaixo do poste... ELE"
PISCA = T(12) + 0.5          # "Eu pisquei"
BATE = T(13) + 1.2           # três batidas
SUSTO = T(16) + 0.05         # "Abre a porta": o rosto colado no olho mágico


def topo(c, t, lugar):
    selo_ep(c, "PARTE 3")
    tag_local(c, t, lugar)


def tela_recusada(c, t, w, h):
    c.rectangle(0, 0, w, h); rgb(c, (0.12, 0.13, 0.16)); c.fill()
    c.new_sub_path(); c.arc(w / 2, h * 0.36, w * 0.13, 0, 6.283); rgb(c, (0.85, 0.25, 0.22)); c.fill()
    c.move_to(w / 2 - w * 0.05, h * 0.36 - w * 0.05); c.line_to(w / 2 + w * 0.05, h * 0.36 + w * 0.05)
    c.move_to(w / 2 + w * 0.05, h * 0.36 - w * 0.05); c.line_to(w / 2 - w * 0.05, h * 0.36 + w * 0.05)
    rgb(c, (1, 1, 1)); c.set_line_width(w * 0.025); c.stroke()
    c.select_font_face(FONTE); c.set_font_size(w * 0.075); e = c.text_extents("Corrida recusada")
    c.move_to(w / 2 - e.x_advance / 2, h * 0.52); c.show_text("Corrida recusada")
    c.set_font_size(w * 0.05); s = "Você está offline"; e = c.text_extents(s)
    c.move_to(w / 2 - e.x_advance / 2, h * 0.58); rgb(c, (0.65, 0.65, 0.7)); c.show_text(s)


def s01(c, t):  # recusa e vai embora
    tela = (tela_corrida("pedido", passageiro="Seu Antônio", destino="Minha casa", recusar=True, hora="03:06")
            if t < T(0) + 1.0 else tela_recusada)
    carro_pov(c, t, lambda c, t: (estrada_noite(c, t, 1.0), nevoa_i(c, t, 980, 0.35, seed=2)),
              retrovisor=banco_tras(False, False), celular=tela, painel_luz=piscar(t, 3))
    resultado_voto(c, t, "A", "RECUSAR A CORRIDA", t1=3.4, cor=(0.80, 0.16, 0.14))
    topo(c, t, "SÃO PAULO · 03:06")


def s02(c, t):  # em casa: porta trancada, luz da sala acesa
    k = ease_io(prog(t, T(1) - 0.2, T(3) - T(1)))
    z = 1 + 0.12 * k
    c.save(); c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2, -H / 2)
    sala_noite(c, t, abajur=1.0)
    c.restore()
    topo(c, t, "MINHA CASA · 03:14")


def s03(c, t):  # 3h33: o celular vibra no escuro
    sala_noite(c, t, abajur=0.0)
    c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), 0.7); c.fill()
    if t >= VIBRA:
        notif = (("Corrida · agora", "Passageiro chegou ao destino"),)
    else:
        notif = ()
    vib = 8 if VIBRA <= t < VIBRA + 1.4 and int(t * 30) % 2 else 0
    c.save(); c.translate(vib, 0)
    celular_mao(c, t, tela_bloqueio(hora="03:33", data="sexta-feira, 13 de novembro", notificacoes=notif), y=1000, s=0.95)
    c.restore()
    if t >= VIBRA:
        rglow(c, W / 2, 1000, 700, (0.6, 0.65, 1.0), 0.18)
    topo(c, t, "MINHA CASA · 03:33")


def s04(c, t):  # o cheiro de flor: a sala no escuro, a fresta acende
    sala_noite(c, t, abajur=0.25 * piscar(t, 5), porta_luz=min(1.0, (t - T(7)) / 1.5))
    nevoa_i(c, t, 1300, 0.35, seed=7)
    if t > T(7) + 2.4:  # flores aparecem no escuro, perto da porta
        a = min(1.0, (t - T(7) - 2.4) / 0.8)
        c.push_group(); c.save(); c.translate(860, 1230); c.rotate(-1.4); flores_i(c, 1.6); c.restore(); c.pop_group_to_source(); c.paint_with_alpha(a)
    escurecer(c, 0.25)
    topo(c, t, "MINHA CASA · 03:34")


def s05(c, t):  # vai até a porta e chega no olho mágico
    k = ease_io(prog(t, T(8) - 0.2, T(9) - T(8)))
    z = 1 + 4.0 * k
    c.save(); c.translate(W / 2, 560); c.scale(z, z); c.translate(-W / 2, -560)
    porta_dentro(c, t, fresta=0.7)
    c.restore()
    if k > 0.85:
        c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), (k - 0.85) / 0.15); c.fill()
    topo(c, t, "MINHA CASA · 03:34")


def s06(c, t):  # pelo olho mágico: o buquê no tapete... e ele no poste
    vazio = t >= PISCA + 0.12
    quem = dict(SENHOR); quem["olhos"] = lambda tt: "normal" if tt < ELE else "brancos"
    k = ease_io(prog(t, ELE - 1.6, 1.4))
    foco = (540 + (650 - 540) * k, 1600 + (520 - 1600) * k)
    zoom = 1.6 - 0.6 * k + 0.9 * ease_io(prog(t, ELE - 0.2, 4.0))
    olho_magico(c, t, lambda c, tt: rua_fora(c, tt, poste=not vazio, quem=quem, olhar=0.0), foco=foco, zoom=zoom)
    if PISCA <= t < PISCA + 0.25:  # piscou
        c.set_source_rgb(0, 0, 0); c.paint()
    topo(c, t, "OLHO MÁGICO · 03:35")


def s07(c, t):  # as batidas. ele está do outro lado da porta
    tremor = 0.0
    for kk in range(3):
        d = t - (BATE + kk * 0.32)
        if 0 <= d < 0.18:
            tremor = 1.0 - d / 0.18
    k = ease_io(prog(t, T(15) + 0.3, SUSTO - T(15) - 0.3))  # volta a olhar pelo olho mágico
    z = 1 + 4.0 * k
    c.save(); c.translate(W / 2, 560); c.scale(z, z); c.translate(-W / 2, -560)
    porta_dentro(c, t, tremor=tremor, fresta=0.8, pes=t >= BATE - 0.4)
    c.restore()
    if k > 0.85:
        c.rectangle(0, 0, W, H); rgb(c, (0, 0, 0), (k - 0.85) / 0.15); c.fill()
    topo(c, t, "MINHA CASA · 03:36")


def s08(c, t):  # o susto: o rosto dele colado no olho mágico
    olho_magico(c, t, lambda c, tt: close_terror(c, tt, SUSTO, olhos_="vazios", expr="sinistro",
                                                    fundo=lambda c, tt: rua_fora(c, tt, poste=False, flores_tapete=False)),
                foco=(540, 760), zoom=1.25)
    if SUSTO <= t < SUSTO + 0.15:
        c.set_source_rgba(1, 1, 1, 0.75 * (1 - (t - SUSTO) / 0.15)); c.paint()
    topo(c, t, "OLHO MÁGICO · 03:36")
    cartao_escolha(c, t, T(17) - 0.2, "ABRE OU FINGE?", "ABRIR A PORTA", "FINGIR QUE NÃO TEM NINGUÉM",
                   segundos=LN.dur - T(17) - 0.4, nota="O mais votado vira a Parte 4")


def _com_legenda(fn):
    def g(c, t):
        fn(c, t)
        legendas(c, t, LN, y=1500 if t < T(17) - 0.2 else 1720)
    return g


SCENES = [(0, T(1) - 0.2, _com_legenda(s01)),
          (T(1) - 0.2, T(3) - 0.2, _com_legenda(s02)),
          (T(3) - 0.2, T(7) - 0.2, _com_legenda(s03)),
          (T(7) - 0.2, T(8) - 0.2, _com_legenda(s04)),
          (T(8) - 0.2, T(9) - 0.3, _com_legenda(s05)),
          (T(9) - 0.3, T(13) - 0.2, _com_legenda(s06)),
          (T(13) - 0.2, SUSTO, _com_legenda(s07)),
          (SUSTO, 999.0, _com_legenda(s08))]

# sons de terror (tonais, sem ruído). Cama: AMBIENCE = "terror". 1 susto grande (SUSTO) + revelação no poste (ELE).
SFX = [(VIBRA - 0.05, "vibra_celular"),
       (T(7) + 0.4, "sino_funebre"),                     # o cheiro de flor
       (T(9) + 0.3, "tum"),                              # o buquê no tapete
       (ELE - 0.05, "tum"), (ELE + 0.1, "sino_funebre"), # ELE embaixo do poste, olhos brancos
       (PISCA + 0.1, "tum"),                             # o poste vazio
       (BATE, "batidas_porta"),
       (BATE + 0.6, "coracao_acelerando:%.2f" % (SUSTO - BATE - 0.6)),
       (SUSTO - 3.0, "cordas_subindo"), (SUSTO, "susto"),
       (T(17) - 0.2, "sino_funebre")]
