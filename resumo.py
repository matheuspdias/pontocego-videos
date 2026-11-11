"""
Resumo rápido do episódio anterior ("Você decide", TikTok vertical): 4 a 6 cortes acelerados do episódio
anterior, cada um com uma frase grande, colados ANTES do episódio atual.

    python resumo.py videos/<slug-atual>            # usa videos/<slug-atual>/resumo.json
    python resumo.py videos/<slug-atual> --so-resumo # gera só o resumo (out/<slug>_resumo.mp4) para conferir

videos/<slug>/resumo.json:
{
  "anterior": "out/vd-corrida-ep1.mp4",      # MP4 final do episódio anterior
  "atual": "out/vd-corrida-ep2.mp4",         # MP4 final deste episódio (sem resumo)
  "saida": "out/vd-corrida-ep2_final.mp4",
  "selo": "NO EP. 1",
  "velocidade": 2.3,                          # quanto acelera cada corte
  "cortes": [{"t": 8.5, "dur": 2.2, "texto": "2H47: CORRIDA PRO CEMITÉRIO"}, ...]
}
O áudio do episódio anterior entra acelerado e baixo (efeito de "avançar"); a voz do episódio atual começa limpa.
Regra de ouro: o resumo inteiro fica entre 4 e 6 s. Escolha os momentos com imagem forte (a corrida, o rosto,
a virada, a escolha), não os de explicação.
"""
import argparse
import json
import os
import subprocess
import sys

import cairo

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
FONTE = "Montserrat ExtraBold"


def overlay_png(path, texto, selo, k, n):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    # cobre a legenda queimada do episódio anterior
    g = cairo.LinearGradient(0, 1220, 0, 1720)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(0.22, 0, 0, 0, 0.96)
    g.add_color_stop_rgba(0.82, 0, 0, 0, 0.96); g.add_color_stop_rgba(1, 0, 0, 0, 0)
    c.set_source(g); c.rectangle(0, 1220, W, 500); c.fill()
    # selo "NO EP. 1" com barrinhas de progresso
    c.select_font_face(FONTE); c.set_font_size(40)
    e = c.text_extents(selo)
    bw = e.x_advance + 60
    c.set_source_rgba(0.80, 0.13, 0.12, 0.95)
    _rr(c, W / 2 - bw / 2, 1290, bw, 70, 16); c.fill()
    c.set_source_rgb(1, 1, 1); c.move_to(W / 2 - e.x_advance / 2, 1340); c.show_text(selo)
    for i in range(n):
        c.set_source_rgba(1, 1, 1, 0.95 if i <= k else 0.3)
        _rr(c, W / 2 - n * 40 + i * 80 + 6, 1640, 68, 8, 4); c.fill()
    # frase grande
    sz = 84
    linhas = [texto]
    c.set_font_size(sz)
    if c.text_extents(texto).x_advance > W - 120:
        ws = texto.split(); m = (len(ws) + 1) // 2
        linhas = [" ".join(ws[:m]), " ".join(ws[m:])]
    for j, l in enumerate(linhas):
        c.set_font_size(sz); e = c.text_extents(l)
        while e.x_advance > W - 100 and sz > 50:
            sz -= 4; c.set_font_size(sz); e = c.text_extents(l)
        x, y = W / 2 - e.x_advance / 2, 1500 + j * (sz + 14) - (len(linhas) - 1) * (sz + 14) / 2
        c.move_to(x, y); c.text_path(l)
        c.set_source_rgb(0, 0, 0); c.set_line_width(sz * 0.16); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
        c.set_source_rgb(1.0, 0.80, 0.36) if j == len(linhas) - 1 else c.set_source_rgb(1, 1, 1)
        c.fill()
    s.write_to_png(path)


def _rr(c, x, y, w, h, r):
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -1.5708, 0); c.arc(x + w - r, y + h - r, r, 0, 1.5708)
    c.arc(x + r, y + h - r, r, 1.5708, 3.1416); c.arc(x + r, y + r, r, 3.1416, 4.7124); c.close_path()


def atempo(v):
    parts = []
    while v > 2.0:
        parts.append("atempo=2.0"); v /= 2.0
    parts.append(f"atempo={v:.4f}")
    return ",".join(parts)


def gerar_resumo(cfg, saida):
    tmp = os.path.join(ROOT, "out", "_resumo")
    os.makedirs(tmp, exist_ok=True)
    v = cfg.get("velocidade", 2.3)
    n = len(cfg["cortes"])
    ins, filt = [], []
    for k, ct in enumerate(cfg["cortes"]):
        png = os.path.join(tmp, f"o{k}.png")
        overlay_png(png, ct["texto"], cfg.get("selo", "NO EPISÓDIO ANTERIOR"), k, n)
        ins += ["-ss", str(ct["t"]), "-t", str(ct.get("dur", 2.2)), "-i", cfg["anterior"], "-i", png]
        a, b = 2 * k, 2 * k + 1
        # acelera, dá um leve zoom e põe a frase
        filt.append(f"[{a}:v]setpts=(PTS-STARTPTS)/{v},scale={int(W * 1.06)}:{int(H * 1.06)},crop={W}:{H},fps=30[v{k}a];"
                    f"[v{k}a][{b}:v]overlay=0:0,format=yuv420p[v{k}]")
        filt.append(f"[{a}:a]asetpts=PTS-STARTPTS,{atempo(v)},volume=0.30[a{k}]")
    cat = "".join(f"[v{k}][a{k}]" for k in range(n))
    filt.append(f"{cat}concat=n={n}:v=1:a=1[v][a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(filt), "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", saida], check=True)
    return saida


def juntar(resumo, atual, saida):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", resumo, "-i", atual, "-filter_complex",
                    "[0:v]fps=30,format=yuv420p,setsar=1[v0];[1:v]fps=30,format=yuv420p,setsar=1[v1];"
                    "[0:a]aresample=48000[a0];[1:a]aresample=48000[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", saida], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vdir")
    ap.add_argument("--so-resumo", action="store_true")
    a = ap.parse_args()
    cfg = json.load(open(os.path.join(a.vdir, "resumo.json"), encoding="utf-8"))
    slug = os.path.basename(os.path.normpath(a.vdir))
    r = gerar_resumo(cfg, os.path.join(ROOT, "out", f"{slug}_resumo.mp4"))
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", r]))
    print(f"resumo: {dur:.1f}s")
    if dur > 6.5:
        print("  ATENÇÃO: resumo passou de 6 s; tire um corte ou aumente a velocidade", file=sys.stderr)
    if a.so_resumo:
        return
    juntar(r, cfg["atual"], cfg["saida"])
    print(cfg["saida"])


if __name__ == "__main__":
    main()
