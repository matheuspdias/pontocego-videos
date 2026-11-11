"""
Formato "VOCÊ DECIDE" (TikTok vertical 1080x1920 do Ponto Cego): histórias de TERROR em primeira pessoa,
com várias vozes, legenda colorida por personagem e um cartão final "O QUE VOCÊ FARIA?" com opções A e B.

    from engine import *
    VERTICAL = True            # antes do import do ilustrado
    from ilustrado import *
    from pov import *
    STYLE = "ilustrado"; TOM = "sombrio"   # SEMPRE sombrio no TikTok (o render.py força); efeitos sonoros sempre ligados
    LN = linhas(__file__)       # tempos de cada fala (videos/<slug>/linhas.json, gerado pelo montar_falas.py)
    ...  LN.t0(3), LN.t1(3), LN.fim, LN.dur

Peças: carro_pov (para-brisa + painel + volante + retrovisor + celular no suporte), estrada_noite,
celular_mao (celular nas mãos, em primeira pessoa), tela_corrida (app de corrida), tela_bloqueio, tela_chat,
banco_tras (para o retrovisor), homem_poste, flores_i, portao_cemiterio, legendas (fala por fala, cor por
personagem), tag_local ("SÃO PAULO · 02:47"), selo_ep ("EP. 1"), aviso_lenda, cartao_escolha (contagem + A/B).
"""
import json
import math
import os
import random
import zlib

import cairo
from engine import *
from ilustrado import *
import ilustrado as _il

FONTE = "Montserrat ExtraBold"
CORES_FALA = {
    "voce": (0.98, 0.97, 0.94),
    "pensa": (0.72, 0.84, 1.00),
    "passageiro": (1.00, 0.80, 0.36),
    "app": (0.55, 0.92, 0.66),
}
CORES_FALA_PADRAO = [(1.00, 0.80, 0.36), (0.95, 0.45, 0.45), (0.55, 0.92, 0.66), (0.80, 0.65, 1.0)]


# ================================================================ tempos das falas
class Linhas:
    def __init__(self, data):
        self.linhas = data["linhas"]
        self.fim = data["fim_falas"]
        self.dur = data["dur"]
        self.estimado = data.get("estimado", False)

    def t0(self, i):
        return self.linhas[i]["t0"]

    def t1(self, i):
        return self.linhas[i]["t1"]

    def palavra(self, i, k):
        """início da k-ésima palavra da fala i (para sincronizar um efeito a uma palavra)"""
        return self.linhas[i]["palavras"][k]["t0"]


def linhas(scenes_file):
    vdir = os.path.dirname(os.path.abspath(scenes_file))
    return Linhas(json.load(open(os.path.join(vdir, "linhas.json"), encoding="utf-8")))


# ================================================================ textos fixos
def _txt(c, s, size, font=FONTE):
    c.select_font_face(font); c.set_font_size(size)
    return c.text_extents(s)


def _contorno(c, s, x, y, size, col, contorno=(0, 0, 0), lw=None, sombra=True, font=FONTE):
    c.select_font_face(font); c.set_font_size(size)
    if sombra:
        c.move_to(x + 3, y + 5); c.text_path(s); rgb(c, (0, 0, 0), 0.45); c.fill()
    c.move_to(x, y); c.text_path(s)
    rgb(c, contorno); c.set_line_width(lw or size * 0.16); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
    rgb(c, col); c.fill()


def tag_local(c, t, texto, y=118, t0=0.0):
    """etiqueta de lugar e hora no topo: ● SÃO PAULO · 02:47"""
    if t < t0:
        return
    a = min(1, (t - t0) / 0.4)
    e = _txt(c, texto, 30)
    w = e.x_advance + 74
    c.save(); c.translate(W / 2, y)
    c.push_group()
    rr(c, -w / 2, -30, w, 60, 30); rgb(c, (0.05, 0.05, 0.07), 0.78); c.fill()
    pul = 0.6 + 0.4 * math.sin(t * 4)
    c.new_sub_path(); c.arc(-w / 2 + 34, 0, 9, 0, 6.283); rgb(c, (0.92, 0.22, 0.20), pul); c.fill()
    c.move_to(-w / 2 + 56, 11); rgb(c, (0.96, 0.94, 0.90)); c.show_text(texto)
    c.pop_group_to_source(); c.paint_with_alpha(a)
    c.restore()


def selo_ep(c, texto="EP. 1", x=60, y=118):
    e = _txt(c, texto, 30)
    rr(c, x, y - 28, e.x_advance + 40, 56, 12); rgb(c, (0.75, 0.13, 0.12), 0.95); c.fill()
    c.move_to(x + 20, y + 11); rgb(c, (1, 1, 1)); c.show_text(texto)


def aviso_lenda(c, t, texto="INSPIRADO NUMA LENDA URBANA", t1=3.5, y=190):
    if t > t1:
        return
    a = min(1, (t1 - t) / 0.5)
    e = _txt(c, texto, 22)
    c.move_to(W / 2 - e.x_advance / 2, y); rgb(c, (0.85, 0.83, 0.78), 0.75 * a); c.show_text(texto)


# ================================================================ legendas por personagem
def _exibicao(ln):
    """palavras como aparecem no texto (com pontuação), com o tempo da 1ª palavra falada de cada uma"""
    ws = ln["palavras"]
    out, k = [], 0
    for orig in ln["texto"].split():
        n = len(tokens_fala(orig))
        if n == 0:
            continue
        seg = ws[k:k + n] or ws[-1:]
        txt = orig.rstrip(",;:")
        out.append({"w": txt, "t0": seg[0]["t0"], "t1": seg[-1]["t1"], "quebra": orig[-1] in ".?!…,;:"})
        k += n
    return out or [{"w": w["w"], "t0": w["t0"], "t1": w["t1"], "quebra": False} for w in ws]


def tokens_fala(s):
    import re
    return re.findall(r"[0-9A-Za-zÀ-ÿ]+(?:['’-][0-9A-Za-zÀ-ÿ]+)*", s)


def _chunks(palavras, maxw=4, maxc=21):
    out, cur = [], []
    for w in palavras:
        if cur and (len(cur) >= maxw or len(" ".join(x["w"] for x in cur + [w])) > maxc):
            out.append(cur); cur = []
        cur.append(w)
        if w.get("quebra"):
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def legendas(c, t, LN, y=1430, size=74, cores=None, tag_quem=True):
    """legenda da fala atual em blocos de até 3 palavras; a palavra falada cresce um pouco.
    Cor por personagem (CORES_FALA); pensamento (\"pensa\": true) em azul-claro e entre parênteses."""
    cores = dict(CORES_FALA, **(cores or {}))
    for ln in LN.linhas:
        if ln["t0"] - 0.05 <= t <= ln["t1"] + 0.35:
            break
    else:
        return
    ch = _chunks(_exibicao(ln))
    atual = ch[-1]
    for k, grupo in enumerate(ch):
        fim = ch[k + 1][0]["t0"] - 0.02 if k + 1 < len(ch) else ln["t1"] + 0.35
        if t < fim:
            atual = grupo
            break
    quem = ln["quem"]
    col = cores["pensa"] if ln.get("pensa") else cores.get(quem, CORES_FALA_PADRAO[zlib.crc32(quem.encode()) % len(CORES_FALA_PADRAO)])  # crc32: mesma cor em todo render
    texto = " ".join(w["w"] for w in atual)
    if ln.get("pensa"):
        texto = "(" + texto + ")"
    sz = size
    e = _txt(c, texto, sz)
    while e.x_advance > W - 140 and sz > 40:
        sz -= 4; e = _txt(c, texto, sz)
    p = ease_out_back(prog(t, atual[0]["t0"] - 0.05, 0.18))
    c.save(); c.translate(W / 2, y); c.scale(0.85 + 0.15 * p, 0.85 + 0.15 * p)
    _contorno(c, texto, -e.x_advance / 2, sz * 0.35, sz, col)
    c.restore()
    if tag_quem and quem not in ("voce",) and not ln.get("pensa"):
        nome = quem.replace("_", " ").upper()
        en = _txt(c, nome, 26)
        rr(c, W / 2 - en.x_advance / 2 - 16, y - sz * 0.95 - 34, en.x_advance + 32, 40, 10); rgb(c, col, 0.92); c.fill()
        c.move_to(W / 2 - en.x_advance / 2, y - sz * 0.95 - 5); rgb(c, (0.08, 0.06, 0.05)); c.show_text(nome)


# ================================================================ cartão final
def cartao_escolha(c, t, t0, pergunta="O QUE VOCÊ FARIA?", a="ABRIR O CARRINHO", b="VOLTAR PRA VIATURA",
                   segundos=7, nota="O mais votado vira o próximo episódio", comenta="COMENTA A OU B"):
    """escurece a cena e mostra contagem regressiva + as duas opções (A vermelho, B azul)"""
    if t < t0:
        return
    p = ease_out(prog(t, t0, 0.5))
    c.rectangle(0, 0, W, H); rgb(c, (0.02, 0.02, 0.04), 0.72 * p); c.fill()
    c.save(); c.translate(0, 40 * (1 - p))
    c.push_group()
    # contagem
    rest = max(0.0, segundos - (t - t0))
    n = max(1, math.ceil(rest))
    cx, cy, r = W / 2, 560, 74
    c.new_sub_path(); c.arc(cx, cy, r, 0, 6.283); rgb(c, (1, 1, 1), 0.15); c.set_line_width(12); c.stroke()
    c.new_sub_path(); c.arc(cx, cy, r, -math.pi / 2, -math.pi / 2 + 6.283 * rest / segundos)
    rgb(c, (0.92, 0.22, 0.20) if n <= 3 else (0.98, 0.78, 0.30)); c.stroke()
    s = str(n)
    e = _txt(c, s, 92)
    c.move_to(cx - e.x_advance / 2 - e.x_bearing, cy + 32); rgb(c, (1, 1, 1)); c.show_text(s)
    # pergunta (quebra em 2 linhas se precisar)
    palavras = pergunta.split()
    ls = [pergunta]
    if _txt(c, pergunta, 86).x_advance > W - 140:
        meio = len(palavras) // 2
        ls = [" ".join(palavras[:meio]), " ".join(palavras[meio:])]
    for k, l in enumerate(ls):
        e = _txt(c, l, 86)
        _contorno(c, l, W / 2 - e.x_advance / 2, 790 + k * 100, 86, (1, 1, 1))
    yb = 790 + len(ls) * 100 + 40
    for k, (letra, txt, col) in enumerate((("A", a, (0.80, 0.16, 0.14)), ("B", b, (0.16, 0.34, 0.74)))):
        y = yb + k * 200
        q = ease_out_back(prog(t, t0 + 0.3 + k * 0.2, 0.4))
        if q < 0.01:
            continue
        c.save(); c.translate(W / 2, y + 80); c.scale(q, q); c.translate(-W / 2, -(y + 80))
        rr(c, 110 + 8, y + 10, W - 220, 160, 26); rgb(c, (0, 0, 0), 0.4); c.fill()
        rr(c, 110, y, W - 220, 160, 26); rgb(c, col); c.fill()
        rr(c, 110, y, W - 220, 160, 26); rgb(c, (1, 1, 1), 0.85); c.set_line_width(5); c.stroke()
        c.new_sub_path(); c.arc(200, y + 80, 48, 0, 6.283); rgb(c, (1, 1, 1)); c.fill()
        e = _txt(c, letra, 56); c.move_to(200 - e.x_advance / 2 - e.x_bearing, y + 100); rgb(c, col); c.show_text(letra)
        sz = 50
        ls2 = [txt]
        if _txt(c, txt, sz).x_advance > W - 420:
            ws = txt.split(); m = (len(ws) + 1) // 2
            ls2 = [" ".join(ws[:m]), " ".join(ws[m:])]
        for j, l in enumerate(ls2):
            c.move_to(280, y + 80 + (j - (len(ls2) - 1) / 2) * 56 + 18); rgb(c, (1, 1, 1)); c.show_text(l)
        c.restore()
    yn = yb + 2 * 200 + 40
    e = _txt(c, comenta, 46)
    rr(c, W / 2 - e.x_advance / 2 - 30, yn - 10, e.x_advance + 60, 70, 35); rgb(c, (0.98, 0.95, 0.88)); c.fill()
    c.move_to(W / 2 - e.x_advance / 2, yn + 41); rgb(c, (0.08, 0.06, 0.05)); c.show_text(comenta)
    e = _txt(c, nota, 32)
    c.move_to(W / 2 - e.x_advance / 2, yn + 130); rgb(c, (0.98, 0.80, 0.36)); c.show_text(nota)
    c.pop_group_to_source(); c.paint_with_alpha(p)
    c.restore()


# ================================================================ cenas de rua à noite (vistas do carro)
def estrada_noite(c, t, vel=1.0, horizonte=760, seed=3, chuva=False, fim=None):
    """rua de cidade à noite em perspectiva, andando para frente (vel = velocidade). fim(c, t, s) desenha algo
    no fim da rua (um portão, uma pessoa), já escalado pela distância s (0..1)."""
    luz("noite")
    lgrad(c, 0, 0, 0, horizonte, [(0, (0.03, 0.04, 0.09), 1), (1, (0.13, 0.13, 0.20), 1)])
    c.rectangle(0, 0, W, horizonte); c.fill()
    rnd = random.Random(seed)
    # prédios dos dois lados (silhuetas com janelas)
    for lado in (-1, 1):
        x = W / 2 + lado * 60
        k = 0
        while (lado < 0 and x > -200) or (lado > 0 and x < W + 200):
            w = rnd.uniform(60, 130) * (1 + k * 0.5)
            h = rnd.uniform(140, 320) * (1 + k * 0.4)
            x0 = x if lado > 0 else x - w
            c.rectangle(x0, horizonte - h, w, h); rgb(c, mix((0.06, 0.07, 0.11), (0.14, 0.15, 0.22), rnd.random())); c.fill()
            for j in range(int(h / 34)):
                for i_ in range(max(1, int(w / 30))):
                    if rnd.random() < 0.18:
                        c.rectangle(x0 + 8 + i_ * 30, horizonte - h + 12 + j * 34, 12, 16)
                        rgb(c, (1.0, 0.80, 0.45), rnd.uniform(0.4, 0.9)); c.fill()
            x += lado * (w + 8)
            k += 1
    # rua
    c.move_to(W / 2 - 40, horizonte); c.line_to(W / 2 + 40, horizonte); c.line_to(W + 400, H); c.line_to(-400, H); c.close_path()
    lgrad(c, 0, horizonte, 0, H, [(0, (0.10, 0.10, 0.13), 1), (1, (0.16, 0.16, 0.19), 1)]); c.fill()
    # calçadas
    for lado in (-1, 1):
        c.move_to(W / 2 + lado * 40, horizonte); c.line_to(W / 2 + lado * 70, horizonte)
        c.line_to(W / 2 + lado * (W / 2 + 900), H); c.line_to(W / 2 + lado * (W / 2 + 400), H); c.close_path()
        rgb(c, (0.20, 0.20, 0.23)); c.fill()
    # faixas centrais andando
    off = (t * vel * 1.4) % 1.0
    for i in range(10):
        z0 = ((i + off) / 10) ** 2.2
        z1 = ((i + off + 0.45) / 10) ** 2.2
        y0, y1 = horizonte + (H - horizonte) * z0, horizonte + (H - horizonte) * z1
        w0, w1 = 2 + 26 * z0, 2 + 26 * z1
        pg(c, [(W / 2 - w0, y0), (W / 2 + w0, y0), (W / 2 + w1, y1), (W / 2 - w1, y1)])
        rgb(c, (0.95, 0.80, 0.35), 0.85); c.fill()
    # postes passando
    for i in range(6):
        z = ((i + (t * vel * 0.5) % 1.0) / 6) ** 2.0
        for lado in (-1, 1):
            x = W / 2 + lado * (70 + (W / 2 + 300) * z)
            yb = horizonte + (H - horizonte) * z
            hpo = 40 + 900 * z
            c.rectangle(x - 2 - 6 * z, yb - hpo, 4 + 12 * z, hpo); rgb(c, (0.05, 0.05, 0.07)); c.fill()
            lx = x - lado * (20 + 80 * z)
            rglow(c, lx, yb - hpo, 30 + 260 * z, (1.0, 0.78, 0.42), 0.35)
            c.new_sub_path(); c.arc(lx, yb - hpo, 3 + 12 * z, 0, 6.283); rgb(c, (1.0, 0.92, 0.70)); c.fill()
    if fim:
        fim(c, t, horizonte)
    if chuva:
        rnd2 = random.Random(7)
        for i in range(140):
            x0, y0 = rnd2.uniform(0, W), rnd2.uniform(0, H)
            y = (y0 + t * 1400) % H
            c.move_to(x0, y); c.line_to(x0 - 6, y + 40); rgb(c, (0.75, 0.80, 0.95), 0.25); c.set_line_width(2); c.stroke()


def carro_pov(c, t, fora, retrovisor=None, celular=None, vel=1.0, volante=True, painel_luz=1.0, balanco=True):
    """vista do motorista: fora(c, t) desenha o que se vê pelo para-brisa; retrovisor(c, t, w, h) o que aparece
    no espelho; celular(c, t, w, h) a tela do celular no suporte do painel."""
    dy = math.sin(t * 7.3) * 2 + math.sin(t * 2.1) * 3 if balanco else 0
    c.save(); c.translate(0, dy)
    fora(c, t)
    c.restore()
    cor_int = (0.07, 0.07, 0.08)
    # teto e colunas
    c.move_to(0, 0); c.line_to(W, 0); c.line_to(W, 230); c.curve_to(W * 0.7, 170, W * 0.3, 170, 0, 230); c.close_path()
    rgb(c, cor_int); c.fill()
    for lado in (0, 1):
        x0 = 0 if lado == 0 else W
        s = 1 if lado == 0 else -1
        pg(c, [(x0, 200), (x0 + s * 110, 220), (x0 + s * 30, 1250), (x0, 1250)]); rgb(c, cor_int); c.fill()
    # painel
    c.move_to(0, 1240); c.curve_to(W * 0.3, 1170, W * 0.7, 1170, W, 1240); c.line_to(W, H); c.line_to(0, H); c.close_path()
    lgrad(c, 0, 1170, 0, H, [(0, (0.10, 0.10, 0.11), 1), (1, (0.03, 0.03, 0.04), 1)]); c.fill()
    c.move_to(0, 1240); c.curve_to(W * 0.3, 1170, W * 0.7, 1170, W, 1240)
    rgb(c, (0.25, 0.25, 0.28)); c.set_line_width(4); c.stroke()
    # luzes do painel
    for x in (300, 780):
        rglow(c, x, 1300, 70, (0.30, 0.70, 1.0), 0.25 * painel_luz)
        c.new_sub_path(); c.arc(x, 1300, 46, math.pi, 2 * math.pi); rgb(c, (0.25, 0.65, 0.95), 0.6 * painel_luz)
        c.set_line_width(4); c.stroke()
    # retrovisor
    if retrovisor:
        rw, rh, rx, ry = 560, 190, W / 2 - 280, 250
        c.rectangle(W / 2 - 8, 170, 16, 90); rgb(c, cor_int); c.fill()
        rr(c, rx - 14, ry - 14, rw + 28, rh + 28, 30); rgb(c, (0.05, 0.05, 0.06)); c.fill()
        c.save(); rr(c, rx, ry, rw, rh, 20); c.clip(); c.translate(rx, ry)
        retrovisor(c, t, rw, rh)
        lgrad(c, 0, 0, rw, rh, [(0, (1, 1, 1), 0.10), (0.5, (1, 1, 1), 0.0), (1, (1, 1, 1), 0.05)]); c.paint()
        c.restore()
    # celular no suporte
    if celular:
        c.save(); c.translate(870, 1080); c.rotate(-0.08)
        c.rectangle(-10, 60, 20, 110); rgb(c, (0.12, 0.12, 0.13)); c.fill()
        rr(c, -95, -170, 190, 340, 22); rgb(c, (0.06, 0.06, 0.07)); c.fill()
        c.save(); rr(c, -85, -158, 170, 316, 14); c.clip(); c.translate(-85, -158)
        celular(c, t, 170, 316)
        c.restore(); c.restore()
    # volante e mãos
    if volante:
        cx, cy, r = W / 2 - 60, 1880, 420
        c.new_sub_path(); c.arc(cx, cy, r, math.pi * 1.05, math.pi * 1.95)
        rgb(c, (0.04, 0.04, 0.05)); c.set_line_width(64); c.stroke()
        c.new_sub_path(); c.arc(cx, cy, r, math.pi * 1.05, math.pi * 1.95)
        rgb(c, (0.18, 0.18, 0.20)); c.set_line_width(6); c.stroke()
        for ang in (math.pi * 1.22, math.pi * 1.78):
            hx, hy = cx + math.cos(ang) * r, cy + math.sin(ang) * r
            _mao(c, hx, hy, 1.0, ang)


def _mao(c, x, y, s=1.0, ang=0.0, pele=None, manga=(0.12, 0.16, 0.26)):
    """mão em primeira pessoa (punho fechado segurando algo), com a manga"""
    pele = pele or mix(PELES["media"], (0.35, 0.28, 0.30), 0.35)
    c.save(); c.translate(x, y); c.scale(s, s)
    side = 1 if math.cos(ang) > 0 else -1
    c.move_to(-60 * side, 60); c.line_to(side * 10 - 20 * side, 220); c.line_to(side * 120, 220); c.line_to(side * 70, 40)
    c.close_path(); rgb(c, manga); c.fill()
    ellipse(c, 0, 0, 62, 54); rgb(c, pele); c.fill()
    for k in range(4):
        ellipse(c, -side * 40 + side * k * 26, -38, 16, 20); rgb(c, dk(pele, 0.06)); c.fill()
    ellipse(c, side * 46, 10, 20, 28); rgb(c, dk(pele, 0.10)); c.fill()
    c.restore()


def celular_mao(c, t, tela, y=980, s=1.0, w=520, h=980):
    """celular grande segurado pelas duas mãos (primeira pessoa). tela(c, t, w, h) desenha o conteúdo."""
    c.save(); c.translate(W / 2, y + math.sin(t * 1.3) * 4); c.scale(s, s); c.rotate(math.sin(t * 0.7) * 0.01)
    rr(c, -w / 2 - 20 + 10, -h / 2 - 20 + 16, w + 40, h + 40, 60); rgb(c, (0, 0, 0), 0.4); c.fill()
    rr(c, -w / 2 - 20, -h / 2 - 20, w + 40, h + 40, 60); rgb(c, (0.07, 0.07, 0.08)); c.fill()
    c.save(); rr(c, -w / 2, -h / 2, w, h, 44); c.clip(); c.translate(-w / 2, -h / 2)
    tela(c, t, w, h)
    c.restore()
    rr(c, -70, -h / 2 + 14, 140, 30, 15); rgb(c, (0.03, 0.03, 0.04)); c.fill()
    pele = mix(PELES["media"], (0.35, 0.28, 0.30), 0.25)
    manga = (0.12, 0.16, 0.26)
    for side in (-1, 1):
        bx, by = side * (w / 2 + 4), h / 2 - 120
        # dedos por trás aparecendo na borda
        for k in range(3):
            rr(c, bx + side * 4 - 18, by - 150 + k * 62, 36, 54, 18); rgb(c, dk(pele, 0.08)); c.fill()
        # palma e polegar por cima da borda
        c.save(); c.translate(bx, by + 80); c.rotate(side * 0.35)
        ellipse(c, side * 30, 40, 78, 110); rgb(c, pele); c.fill()
        rr(c, -side * 40 - 26, -90, 52, 130, 26); rgb(c, lt(pele, 0.04)); c.fill()  # polegar
        ellipse(c, -side * 40, -78, 18, 14); rgb(c, lt(pele, 0.25)); c.fill()       # unha
        c.restore()
        c.move_to(bx + side * 10 - 90, by + 170); c.line_to(bx + side * 10 + 90, by + 170)
        c.line_to(bx + side * 60 + 120, by + 700); c.line_to(bx + side * 60 - 120, by + 700); c.close_path()
        rgb(c, manga); c.fill()
    c.restore()


# ================================================================ telas de celular
def _status(c, w, hora="02:47", bateria=0.38, escuro=False):
    col = (1, 1, 1) if escuro else (0.1, 0.1, 0.12)
    c.select_font_face(FONTE); c.set_font_size(w * 0.05)
    c.move_to(w * 0.08, w * 0.11); rgb(c, col); c.show_text(hora)
    rr(c, w * 0.78, w * 0.075, w * 0.12, w * 0.045, 4); rgb(c, col); c.set_line_width(2); c.stroke()
    c.rectangle(w * 0.785, w * 0.08, w * 0.11 * bateria, w * 0.035)
    rgb(c, (0.9, 0.25, 0.2) if bateria < 0.2 else col); c.fill()


def tela_bloqueio(hora="23:58", data="domingo, 8 de novembro", notificacoes=(("Mãe", "Cadê tu? Já é quase meia-noite."),)):
    def f(c, t, w, h):
        lgrad(c, 0, 0, 0, h, [(0, (0.20, 0.16, 0.38), 1), (1, (0.55, 0.28, 0.42), 1)]); c.paint()
        _status(c, w, hora, escuro=True)
        e = _txt(c, hora, w * 0.26)
        c.move_to(w / 2 - e.x_advance / 2, h * 0.26); rgb(c, (1, 1, 1)); c.show_text(hora)
        e = _txt(c, data, w * 0.05); c.move_to(w / 2 - e.x_advance / 2, h * 0.32); rgb(c, (1, 1, 1), 0.8); c.show_text(data)
        for k, (de, msg) in enumerate(notificacoes):
            y = h * 0.42 + k * 150
            rr(c, w * 0.06, y, w * 0.88, 130, 22); rgb(c, (1, 1, 1), 0.88); c.fill()
            c.select_font_face(FONTE); c.set_font_size(w * 0.05); c.move_to(w * 0.11, y + 46); rgb(c, (0.1, 0.1, 0.12)); c.show_text(de)
            c.select_font_face(HAND if "HAND" in globals() else FONTE); c.set_font_size(w * 0.055)
            c.move_to(w * 0.11, y + 96); rgb(c, (0.25, 0.25, 0.3)); c.show_text(msg[:34])
    return f


def tela_chat(contato="Mãe", mensagens=(("ela", "Cadê tu?"), ("eu", "Tô chegando"))):
    def f(c, t, w, h):
        c.rectangle(0, 0, w, h); rgb(c, (0.92, 0.89, 0.84)); c.fill()
        c.rectangle(0, 0, w, h * 0.13); rgb(c, (0.07, 0.37, 0.33)); c.fill()
        _status(c, w, escuro=True)
        c.new_sub_path(); c.arc(w * 0.13, h * 0.09, w * 0.05, 0, 6.283); rgb(c, (0.8, 0.85, 0.9)); c.fill()
        c.select_font_face(FONTE); c.set_font_size(w * 0.06); c.move_to(w * 0.22, h * 0.105); rgb(c, (1, 1, 1)); c.show_text(contato)
        y = h * 0.18
        for quem, msg in mensagens:
            c.select_font_face(FONTE); c.set_font_size(w * 0.05)
            e = c.text_extents(msg); bw = min(w * 0.75, e.x_advance + 50)
            x = w * 0.05 if quem == "ela" else w * 0.95 - bw
            rr(c, x, y, bw, 80, 18); rgb(c, (1, 1, 1) if quem == "ela" else (0.85, 0.97, 0.80)); c.fill()
            c.move_to(x + 25, y + 52); rgb(c, (0.1, 0.1, 0.12)); c.show_text(msg)
            y += 100
    return f


def tela_corrida(estado="pedido", passageiro="Seu Antônio", nota="5,0", destino="Cemitério da Consolação",
                 valor="R$ 40,00", espera="07:12", t_aceite=None, hora="02:47", embarque=None, recusar=False,
                 destaque=None):
    """app de corrida: "pedido" (nova corrida com botão ACEITAR), "aceita", "aguardando" (passageiro não embarcou)"""
    def f(c, t, w, h):
        # mapa
        c.rectangle(0, 0, w, h); rgb(c, (0.15, 0.17, 0.21)); c.fill()
        rnd = random.Random(4)
        for i in range(14):
            x = rnd.uniform(0, w)
            c.move_to(x, 0); c.line_to(x + rnd.uniform(-w * 0.3, w * 0.3), h); rgb(c, (0.24, 0.27, 0.32)); c.set_line_width(w * 0.02); c.stroke()
        for i in range(10):
            y = rnd.uniform(0, h)
            c.move_to(0, y); c.line_to(w, y + rnd.uniform(-h * 0.1, h * 0.1)); c.stroke()
        c.move_to(w * 0.3, h * 0.48); c.curve_to(w * 0.5, h * 0.40, w * 0.4, h * 0.25, w * 0.72, h * 0.18)
        rgb(c, (0.25, 0.60, 1.0)); c.set_line_width(w * 0.025); c.stroke()
        c.new_sub_path(); c.arc(w * 0.3, h * 0.48, w * 0.035, 0, 6.283); rgb(c, (1, 1, 1)); c.fill()
        c.new_sub_path(); c.arc(w * 0.72, h * 0.18, w * 0.04, 0, 6.283); rgb(c, (0.92, 0.22, 0.20)); c.fill()
        _status(c, w, hora, escuro=True)
        # cartão
        y0 = h * 0.52
        rr(c, 0, y0, w, h - y0 + 40, 30); rgb(c, (0.98, 0.98, 0.97)); c.fill()
        c.select_font_face(FONTE)
        if estado == "aguardando":
            c.set_font_size(w * 0.065); c.move_to(w * 0.08, y0 + h * 0.07); rgb(c, (0.85, 0.25, 0.2)); c.show_text("Aguardando passageiro")
            c.set_font_size(w * 0.05); c.move_to(w * 0.08, y0 + h * 0.13); rgb(c, (0.3, 0.3, 0.35))
            c.show_text("O passageiro ainda não embarcou")
            c.set_font_size(w * 0.16); c.move_to(w * 0.08, y0 + h * 0.29); rgb(c, (0.1, 0.1, 0.12)); c.show_text(espera)
            c.set_font_size(w * 0.05); c.move_to(w * 0.08, y0 + h * 0.36); rgb(c, (0.45, 0.45, 0.5)); c.show_text(passageiro + " · nota " + nota)
            return
        tag = "NOVA CORRIDA" if estado == "pedido" else "CORRIDA ACEITA"
        c.set_font_size(w * 0.05); c.move_to(w * 0.08, y0 + h * 0.06)
        rgb(c, (0.20, 0.55, 0.30) if estado != "pedido" else (0.25, 0.45, 0.9)); c.show_text(tag)
        c.set_font_size(w * 0.075); c.move_to(w * 0.08, y0 + h * 0.12); rgb(c, (0.1, 0.1, 0.12)); c.show_text(passageiro)
        c.set_font_size(w * 0.045); c.move_to(w * 0.08, y0 + h * 0.165); rgb(c, (0.45, 0.45, 0.5)); c.show_text("nota " + nota + " · 1 passageiro")
        if embarque:
            c.new_sub_path(); c.arc(w * 0.1, y0 + h * 0.195, w * 0.02, 0, 6.283); rgb(c, (0.25, 0.45, 0.9)); c.fill()
            c.set_font_size(w * 0.045); c.move_to(w * 0.16, y0 + h * 0.207); rgb(c, (0.3, 0.3, 0.35)); c.show_text(embarque[:28])
            yd = y0 + h * 0.245
        else:
            yd = y0 + h * 0.215
        if destaque is not None and t >= destaque:
            rr(c, w * 0.05, yd - h * 0.03, w * 0.9, h * 0.05, 10); rgb(c, (1.0, 0.85, 0.85)); c.fill()
        c.new_sub_path(); c.arc(w * 0.1, yd, w * 0.02, 0, 6.283); rgb(c, (0.92, 0.22, 0.20)); c.fill()
        c.set_font_size(w * 0.052); c.move_to(w * 0.16, yd + h * 0.013); rgb(c, (0.1, 0.1, 0.12)); c.show_text(destino[:26])
        c.set_font_size(w * 0.09); c.move_to(w * 0.08, y0 + h * 0.31); rgb(c, (0.1, 0.1, 0.12)); c.show_text(valor)
        if recusar:
            for k, (lab_, col_) in enumerate((("RECUSAR", (0.85, 0.25, 0.22)), ("ACEITAR", (0.10, 0.10, 0.12)))):
                bx = w * 0.08 + k * w * 0.43
                rr(c, bx, y0 + h * 0.35, w * 0.41, h * 0.08, 18); rgb(c, col_); c.fill()
                c.set_font_size(w * 0.05); e = c.text_extents(lab_)
                c.move_to(bx + w * 0.205 - e.x_advance / 2, y0 + h * 0.40); rgb(c, (1, 1, 1)); c.show_text(lab_)
            return
        bc = (0.10, 0.10, 0.12) if estado == "pedido" else (0.20, 0.55, 0.30)
        apert = t_aceite is not None and t >= t_aceite
        rr(c, w * 0.08, y0 + h * 0.35, w * 0.84, h * 0.08, 18); rgb(c, (0.20, 0.55, 0.30) if apert else bc); c.fill()
        lab = "ACEITO" if apert or estado != "pedido" else "ACEITAR"
        c.set_font_size(w * 0.06); e = c.text_extents(lab)
        c.move_to(w / 2 - e.x_advance / 2, y0 + h * 0.402); rgb(c, (1, 1, 1)); c.show_text(lab)
        if estado == "pedido" and t_aceite is not None and t_aceite - 0.3 <= t <= t_aceite + 0.5:
            k = (t - t_aceite + 0.3) / 0.8
            c.new_sub_path(); c.arc(w / 2, y0 + h * 0.39, w * 0.05 + w * 0.15 * k, 0, 6.283)
            rgb(c, (1, 1, 1), 0.5 * (1 - k)); c.fill()
    return f


# ================================================================ pessoas e lugares
def flores_i(c, s=1.0):
    """buquê de crisântemos (origem = mão)"""
    c.save(); c.scale(s, s)
    c.move_to(-6, 0); c.line_to(-30, -90); c.move_to(0, 0); c.line_to(0, -100); c.move_to(6, 0); c.line_to(30, -90)
    rgb(c, P((0.25, 0.45, 0.25))); c.set_line_width(5); c.stroke()
    for x, y in ((-30, -96), (0, -110), (30, -96), (-14, -120), (16, -122)):
        for k in range(8):
            a = k * math.pi / 4
            ellipse(c, x + math.cos(a) * 10, y + math.sin(a) * 10, 8, 8); rgb(c, P((0.96, 0.94, 0.86))); c.fill()
        c.new_sub_path(); c.arc(x, y, 6, 0, 6.283); rgb(c, P((0.95, 0.80, 0.30))); c.fill()
    pg(c, [(-22, -50), (22, -50), (10, 10), (-10, 10)]); rgb(c, P((0.55, 0.22, 0.20))); c.fill()
    c.restore()


SENHOR = dict(roupa="casaco", cor_roupa=(0.16, 0.16, 0.18), gravata=(0.16, 0.16, 0.18), camisa=(0.92, 0.92, 0.9),
              cabelo="calvo", cor_cabelo="branco", idade=0.9, bigode=True, pele="clara", fid=12)


def homem_poste(c, t, x, y, s=1.0, quem=None, flores=True, luz_poste=True, look=0.0):
    """pessoa parada sob um poste aceso (vista de longe); y = chão"""
    if luz_poste:
        c.move_to(x - 30 * s, y - 520 * s); c.line_to(x + 30 * s, y - 520 * s); c.line_to(x + 240 * s, y + 10); c.line_to(x - 240 * s, y + 10)
        c.close_path(); lgrad(c, x, y - 520 * s, x, y, [(0, (1.0, 0.85, 0.55), 0.35), (1, (1.0, 0.85, 0.55), 0.06)]); c.fill()
        c.rectangle(x - 140 * s, y - 560 * s, 10 * s, 560 * s); rgb(c, (0.05, 0.05, 0.06)); c.fill()
        c.move_to(x - 135 * s, y - 560 * s); c.line_to(x, y - 540 * s); rgb(c, (0.05, 0.05, 0.06)); c.set_line_width(8 * s); c.stroke()
        rglow(c, x, y - 530 * s, 120 * s, (1.0, 0.85, 0.55), 0.6)
    o = dict(quem or SENHOR)
    if flores:
        o["prop"] = ("r", lambda c, tt: flores_i(c, 0.9))
    old = _il._L
    _il._L = LUZES["tarde"]  # o poste ilumina a pessoa com luz quente
    boneco(c, t, x, y, s, poses=((0, "hold"),), exprs=((0, "neutral"),), look=look, **o)
    _il._L = old


def close_terror(c, t, t0, quem=None, olhos_="vazios", expr="sinistro", fundo=None):
    """o susto: close em tela cheia no rosto (olhos estranhos), com flash branco curto, tremida e vermelho.
    Use num trecho curto (0,8 a 2 s) começando em t0, com sfx "susto" em t0 e "cordas_subindo" 3 s antes."""
    k = max(0.0, t - t0)
    shake = 14 * max(0, 1 - k / 0.5)
    c.save(); c.translate(math.sin(t * 90) * shake, math.cos(t * 77) * shake)
    if fundo:
        fundo(c, t)
    else:
        lgrad(c, 0, 0, 0, H, [(0, (0.10, 0.11, 0.16), 1), (1, (0.02, 0.02, 0.03), 1)]); c.paint()
        for k2 in range(3):  # encosto do banco de trás atrás dele
            rr(c, -100 + k2 * 460, 520, 420, 1100, 60); rgb(c, (0.13, 0.10, 0.09)); c.fill()
    o = dict(quem or SENHOR); o["olhos"] = olhos_
    old = _il._L; _il._L = LUZES["sombrio"]
    s = 7.0 + 0.3 * k
    boneco(c, t, W / 2, 820 + 403 * s, s, exprs=((0, expr),), look=0.0, **o)
    _il._L = old
    c.restore()
    if k < 0.18:
        c.set_source_rgba(1, 1, 1, 0.85 * (1 - k / 0.18)); c.paint()
    c.set_source_rgba(0.6, 0, 0, 0.18 * max(0, 1 - k / 1.2)); c.paint()


def banco_tras(passageiro=True, flores=True, olhos=False, quem=None, expr="neutral", look=0.0):
    """o que aparece no retrovisor: banco de trás, com ou sem o passageiro"""
    def f(c, t, w, h):
        lgrad(c, 0, 0, 0, h, [(0, (0.10, 0.11, 0.16), 1), (1, (0.05, 0.05, 0.08), 1)]); c.paint()
        c.rectangle(0, 0, w, h * 0.45); rgb(c, (0.08, 0.09, 0.14)); c.fill()
        for x in (w * 0.1, w * 0.7):  # janelas traseiras com luz de rua passando
            rr(c, x, h * 0.08, w * 0.2, h * 0.35, 8); rgb(c, (0.18, 0.20, 0.30)); c.fill()
            k = (t * 0.8 + x) % 1
            c.rectangle(x + w * 0.2 * k, h * 0.08, 10, h * 0.35); rgb(c, (1, 0.85, 0.5), 0.35); c.fill()
        rr(c, w * 0.05, h * 0.5, w * 0.9, h * 0.6, 20); rgb(c, (0.16, 0.13, 0.12)); c.fill()
        for k in range(3):
            rr(c, w * 0.07 + k * w * 0.29, h * 0.2, w * 0.27, h * 0.45, 16); rgb(c, (0.20, 0.16, 0.14)); c.fill()
        if flores and not passageiro:
            c.save(); c.translate(w * 0.62, h * 0.95); c.rotate(-1.2); flores_i(c, 0.55); c.restore()
        if passageiro:
            o = dict(quem or SENHOR)
            s_ = h / 210
            c.save(); c.translate(w * 0.62, h * 0.10 + 470 * s_)
            boneco(c, t, 0, 0, s_, poses=((0, "stand"),), exprs=((0, expr(t) if callable(expr) else expr),), look=look, **o)
            c.restore()
        if olhos:
            silhueta(c, t, w * 0.62, h * 1.25, h / 420, 0.75, olhos=True)
    return f


def portao_cemiterio(c, t, x, y, s=1.0, nome="CEMITÉRIO", depth=0.0, abertura=0.0, dentro=None):
    """portão de ferro com arco de pedra (origem = base no centro). abertura 0..1 abre as duas folhas;
    dentro(c, t) desenha o que aparece pelo vão (névoa, alguém entrando), em coordenadas do portão."""
    c.save(); c.translate(x, y); c.scale(s, s)
    pedra = P((0.50, 0.50, 0.52), depth)
    for sx in (-1, 1):
        c.rectangle(sx * 300 - 60, -620, 120, 620); rgb(c, pedra); c.fill()
        c.rectangle(sx * 300 - 72, -650, 144, 40); rgb(c, dk(pedra, 0.15)); c.fill()
        c.rectangle(sx * 300 + (30 if sx > 0 else -60), -620, 30, 620); rgb(c, (0, 0, 0), 0.15); c.fill()
    c.move_to(-360, -650); c.curve_to(-300, -900, 300, -900, 360, -650); c.line_to(360, -600); c.curve_to(300, -830, -300, -830, -360, -600)
    c.close_path(); rgb(c, pedra); c.fill()
    e = _txt(c, nome, 52, SERIF)
    c.move_to(-e.x_advance / 2, -720); rgb(c, dk(pedra, 0.5)); c.show_text(nome)
    ferro = (0.04, 0.04, 0.05)
    if abertura > 0 or dentro:
        c.save(); c.rectangle(-240, -600, 480, 600); c.clip()
        lgrad(c, 0, -600, 0, 0, [(0, (0.22, 0.26, 0.30), 1), (1, (0.42, 0.46, 0.50), 1)]); c.paint()
        # o cemitério lá dentro: caminho, árvores secas e túmulos na névoa
        for xx, hh in ((-170, 330), (150, 380), (-60, 260)):
            arvore_morta(c, t, xx, -250, hh, depth=0.0, seed=int(abs(xx)), col=(0.16, 0.18, 0.21))
        pg(c, [(-26, -250), (26, -250), (150, 0), (-150, 0)]); rgb(c, (0.50, 0.52, 0.54)); c.fill()
        for i, (xx, yy, ss, tp) in enumerate(((-200, -170, 0.5, "cruz"), (-140, -110, 0.6, "arco"), (-210, -40, 0.75, "arco"),
                                              (190, -150, 0.5, "arco"), (150, -80, 0.65, "cruz"), (215, -10, 0.8, "obelisco"))):
            lapide(c, xx, yy, ss, tp, (i % 3 - 1) * 0.06)
        lgrad(c, 0, -600, 0, 0, [(0, (0.60, 0.65, 0.70), 0.0), (0.55, (0.60, 0.65, 0.70), 0.35), (1, (0.70, 0.74, 0.78), 0.55)])
        c.paint()
        if dentro:
            dentro(c, t)
        c.restore()
    for lado in (-1, 1):
        w_ = 240 * (1 - 0.85 * abertura)  # a folha "gira" e fica estreita
        c.save(); c.translate(lado * 240, 0); c.scale(-lado * w_ / 240, 1)
        for k in range(0, 11):
            x_ = k * 24
            c.rectangle(x_ - 3, -560, 6, 560); rgb(c, ferro); c.fill()
            pg(c, [(x_ - 8, -560), (x_, -584), (x_ + 8, -560)]); c.fill()
        for yy in (-500, -260, -40):
            c.rectangle(0, yy, 240, 8); rgb(c, ferro); c.fill()
        c.restore()
    c.restore()


def tela_pix(valor="R$ 40,00", de="Antônio Carlos Ferreira", banco="Banco", aviso=None, t_aviso=None, hora="03:03"):
    """app de banco: Pix recebido; aviso (ex.: "Conta encerrada em 2006") aparece em vermelho a partir de t_aviso"""
    def f(c, t, w, h):
        c.rectangle(0, 0, w, h); rgb(c, (0.97, 0.97, 0.96)); c.fill()
        c.rectangle(0, 0, w, h * 0.30); rgb(c, (0.42, 0.18, 0.62)); c.fill()
        _status(c, w, hora, escuro=True)
        c.select_font_face(FONTE); c.set_font_size(w * 0.06); c.move_to(w * 0.08, h * 0.13); rgb(c, (1, 1, 1), 0.85); c.show_text(banco)
        c.new_sub_path(); c.arc(w / 2, h * 0.30, w * 0.12, 0, 6.283); rgb(c, (0.20, 0.70, 0.45)); c.fill()
        c.move_to(w / 2 - w * 0.05, h * 0.30); c.line_to(w / 2 - w * 0.01, h * 0.325); c.line_to(w / 2 + w * 0.06, h * 0.28)
        rgb(c, (1, 1, 1)); c.set_line_width(w * 0.022); c.stroke()
        c.set_font_size(w * 0.065); e = c.text_extents("Pix recebido")
        c.move_to(w / 2 - e.x_advance / 2, h * 0.45); rgb(c, (0.1, 0.1, 0.12)); c.show_text("Pix recebido")
        c.set_font_size(w * 0.14); e = c.text_extents(valor)
        c.move_to(w / 2 - e.x_advance / 2, h * 0.56); rgb(c, (0.1, 0.1, 0.12)); c.show_text(valor)
        c.set_font_size(w * 0.045); e = c.text_extents("de"); c.move_to(w / 2 - e.x_advance / 2, h * 0.63); rgb(c, (0.45, 0.45, 0.5)); c.show_text("de")
        c.set_font_size(w * 0.058); e = c.text_extents(de)
        c.move_to(w / 2 - e.x_advance / 2, h * 0.68); rgb(c, (0.1, 0.1, 0.12)); c.show_text(de)
        if aviso and (t_aviso is None or t >= t_aviso):
            k = min(1.0, (t - (t_aviso or 0)) / 0.3)
            rr(c, w * 0.06, h * 0.74, w * 0.88, h * 0.10, 14); rgb(c, (1.0, 0.90, 0.88), k); c.fill()
            c.set_font_size(w * 0.052); e = c.text_extents(aviso)
            c.move_to(w / 2 - e.x_advance / 2, h * 0.80); rgb(c, (0.80, 0.15, 0.12), k); c.show_text(aviso)
    return f


def resultado_voto(c, t, letra="B", texto="LEVAR ATÉ O PORTÃO", t1=3.2, y=300, cor=(0.16, 0.34, 0.74)):
    """faixa "VOCÊS ESCOLHERAM: B" no começo do episódio (recompensa quem votou)"""
    if t > t1:
        return
    a = min(1.0, t / 0.3, (t1 - t) / 0.4)
    c.save(); c.push_group()
    tit = "VOCÊS ESCOLHERAM"
    e = _txt(c, tit, 34)
    c.move_to(W / 2 - e.x_advance / 2, y); rgb(c, (0.98, 0.95, 0.88)); c.show_text(tit)
    s_ = letra + " · " + texto
    e = _txt(c, s_, 46)
    rr(c, W / 2 - e.x_advance / 2 - 30, y + 24, e.x_advance + 60, 80, 20); rgb(c, cor); c.fill()
    c.move_to(W / 2 - e.x_advance / 2, y + 80); rgb(c, (1, 1, 1)); c.show_text(s_)
    c.pop_group_to_source(); c.paint_with_alpha(a); c.restore()
