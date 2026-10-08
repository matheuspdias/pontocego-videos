"""Capas verticais (1080x1920) dos cortes para TikTok, YouTube Shorts e Reels.

    python capas.py videos/<slug> <video_16x9.mp4> [--grade]

Lê videos/<slug>/capas.json:
    {"serie": "JUNTAR R$ 100 MIL",
     "partes": [{"t": 155, "gancho": ["POR QUE", "DEMORA TANTO", "NO COMEÇO?"]}, ...]}
  * "t": segundo do vídeo 16:9 (tempo absoluto) com a cena que vai na capa; escolha uma cena com
    o personagem e um número ou imagem forte daquela parte;
  * "gancho": 1 a 3 linhas curtas; a primeira sai na cor de destaque do canal.
O número de partes (o "DE N") é o tamanho da lista, igual aos cortes.

Cada capa: nome da série, "PARTE X DE N" grande, a cena no meio e o gancho embaixo, sobre o próprio
quadro desfocado. O essencial fica entre y 240 e 1680, porque a grade do perfil do TikTok corta
o topo e o rodapé.
Saída: out/capas/<slug>_capa_parteN.png (e out/capas/<slug>_capas_grade.png com --grade, para conferir).
Tema (cores, fontes, nome do canal) do THEME do cortes.py, sobrescrito por tema_cortes.json.
"""
import argparse
import json
import os
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(ROOT, "fonts")
W, H = 1080, 1920

FONT_FILES = {
    "Permanent Marker": "permanent-marker.ttf",
    "Cinzel": "cinzel-bold.ttf",
    "Montserrat ExtraBold": "montserrat-extrabold.ttf",
    "Special Elite": "special-elite.ttf",
    "Patrick Hand": "patrick-hand.ttf",
}


def theme():
    th = dict(brand="PONTO CEGO", title_font="Cinzel", title_col="&H3DA3E0&",
              cap_font="Montserrat ExtraBold", hl_col="&H3DA3E0&", capa_bg="#100E0C")
    p = os.path.join(ROOT, "tema_cortes.json")
    if os.path.exists(p):
        th.update(json.load(open(p, encoding="utf-8")))
    return th


def ass_rgb(s):
    """&HBBGGRR& -> (r, g, b)"""
    h = s.strip("&H").strip("&").rjust(6, "0")[-6:]
    return int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)


def hex_rgb(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, FONT_FILES.get(name, "montserrat-extrabold.ttf")), size)


def fit(d, txt, name, size, maxw=940):
    f = font(name, size)
    while d.textlength(txt, font=f) > maxw and size > 30:
        size -= 4
        f = font(name, size)
    return f


def ctext(d, y, txt, f, fill, stroke=5):
    w = d.textlength(txt, font=f)
    d.text(((W - w) / 2, y), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))


def frame(video, t, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", video, "-frames:v", "1", out], check=True)
    return Image.open(out).convert("RGB").resize((1920, 1080))


def capa(fr, serie, p, n, gancho, th):
    hl, bgc, white = ass_rgb(th["hl_col"]), hex_rgb(th.get("capa_bg", "#100E0C")), (255, 255, 255)
    tf, cf = th["title_font"], th["cap_font"]
    # fundo: o próprio quadro ampliado, desfocado e tingido com a cor do canal
    bg = fr.resize((3413, 1920)).crop((1166, 0, 1166 + W, H)).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", bg.size, bgc), 0.78)
    d = ImageDraw.Draw(bg)
    ctext(d, 250, serie, fit(d, serie, tf, 70), white, 4)
    big, small = font(tf, 160), font(tf, 80)
    a, b = f"PARTE {p}", f" DE {n}"
    wa, wb = d.textlength(a, font=big), d.textlength(b, font=small)
    if wa + wb > 1000:
        big, small = font(tf, 130), font(tf, 66)
        wa, wb = d.textlength(a, font=big), d.textlength(b, font=small)
    x = (W - wa - wb) / 2
    ya = 360
    d.text((x, ya), a, font=big, fill=hl, stroke_width=6, stroke_fill=(0, 0, 0))
    # "DE N" alinhado pela base do "PARTE X"
    yb = ya + big.getbbox(a)[3] - small.getbbox(b)[3]
    d.text((x + wa, yb), b, font=small, fill=white, stroke_width=4, stroke_fill=(0, 0, 0))
    # cena: 16:9 um pouco maior que a largura (mesmo enquadramento dos cortes)
    bg.paste(fr.resize((1210, 681)).crop((65, 0, 65 + W, 681)), (0, 640))
    y = 1370
    for i, line in enumerate([l.strip() for l in gancho if l.strip()][:3]):
        ctext(d, y, line, fit(d, line, cf, 92), hl if i == 0 else white)
        y += 112
    ctext(d, 1740, th["brand"], font(tf, 60), hl, 3)
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vdir")
    ap.add_argument("video")
    ap.add_argument("--grade", action="store_true", help="salva também uma grade com todas as capas, para conferir")
    a = ap.parse_args()
    slug = os.path.basename(os.path.normpath(a.vdir))
    spec = json.load(open(os.path.join(a.vdir, "capas.json"), encoding="utf-8"))
    th = theme()
    outdir = os.path.join(ROOT, "out", "capas")
    os.makedirs(outdir, exist_ok=True)
    n = len(spec["partes"])
    imgs = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, part in enumerate(spec["partes"], 1):
            fr = frame(a.video, part["t"], os.path.join(tmp, f"f{i}.png"))
            img = capa(fr, spec["serie"], i, n, part["gancho"], th)
            out = os.path.join(outdir, f"{slug}_capa_parte{i}.png")
            img.save(out)
            imgs.append(img)
            print(out)
    if a.grade:
        g = Image.new("RGB", (360 * n, 640))
        for i, img in enumerate(imgs):
            g.paste(img.resize((360, 640)), (360 * i, 0))
        g.save(os.path.join(outdir, f"{slug}_capas_grade.png"))
        print(os.path.join(outdir, f"{slug}_capas_grade.png"))


if __name__ == "__main__":
    main()
