"""Vídeo curto NATIVO do TikTok (1080x1920), a partir de uma cena 16:9 renderizada com a narração.

    python tiktok.py videos/<slug> out/<slug>_base.mp4 out/<slug>_tiktok.mp4
    python tiktok.py videos/<slug> out/<slug>_base.mp4 --capa out/<slug>_capa.png

Não é corte do vídeo longo: o roteiro é escrito só para o TikTok (60 a 90 s, gancho no 1º segundo, revelação no
fim e pergunta para comentário). O enquadramento é o mesmo dos cortes (cortes.py): título fixo no topo, a cena
16:9 no meio (um pouco ampliada, corta ~5% de cada lado) sobre o próprio quadro desfocado, legendas palavra por
palavra embaixo e um cartão no fim. Por isso as cenas usam letras grandes (no celular saem a ~63%) e deixam a
informação entre x 140 e x 1780.

videos/<slug>/tiktok.json:
    {"titulo": "O FAROL QUE APAGOU",            # texto fixo no topo (\\N quebra a linha)
     "card": "SIGA O PONTO CEGO\\Npara mais mistérios",   # cartão dos últimos 2,6 s (opcional)
     "capa": ["SUMIRAM", "DO FAROL", "EM 1900"],  # linhas da capa: a 1ª grande no topo, as outras embaixo
     "capa_t": 20.0,                             # segundo da cena que vai na capa
     "serie": ""}                                # opcional, aparece em cima da capa
Legendas: videos/<slug>/palavras.json (word_timestamps do HeyGen, sem as tags [..]).
"""
import argparse
import json
import os
import subprocess
import tempfile

import cortes
import capas

ROOT = os.path.dirname(os.path.abspath(__file__))


def build_ass(path, words, dur, titulo, card):
    ev = [f"Dialogue: 1,{cortes.ass_time(0)},{cortes.ass_time(dur)},Title,,0,0,0,,{{\\pos(540,300)}}{cortes.esc(titulo)}"]
    ev += cortes.caption_events(words, 0, dur)
    if card:
        ev.append(f"Dialogue: 2,{cortes.ass_time(dur - cortes.CARD_LEN)},{cortes.ass_time(dur)},Card,,0,0,0,,"
                  f"{{\\pos(540,{cortes.VID_Y + 340})\\fad(250,0)}}{card}")
    open(path, "w", encoding="utf-8").write(cortes.ass_head() + "\n".join(ev) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vdir")
    ap.add_argument("base")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--capa")
    a = ap.parse_args()
    spec = json.load(open(os.path.join(a.vdir, "tiktok.json"), encoding="utf-8"))
    if a.capa:
        with tempfile.TemporaryDirectory() as tmp:
            fr = capas.frame(a.base, float(spec.get("capa_t", 2.0)), os.path.join(tmp, "f.png"))
            capas.capa(fr, spec.get("serie", ""), None, None, spec["capa"], capas.theme()).save(a.capa)
        print(a.capa)
    if not a.out:
        return
    words = json.load(open(os.path.join(a.vdir, "palavras.json"), encoding="utf-8"))
    dur = cortes.probe_dur(a.base)
    card = spec.get("card", "SIGA O PONTO CEGO\\Npara mais mistérios")
    with tempfile.TemporaryDirectory() as tmp:
        ass = os.path.join(tmp, "legendas.ass")
        build_ass(ass, words, dur, spec["titulo"], card)
        cortes.render_corte(a.base, a.base, ass, 0, dur, a.out, tmp=tmp)
    print(a.out, f"{os.path.getsize(a.out) / 1e6:.1f} MB", f"{cortes.probe_dur(a.out):.1f} s")


if __name__ == "__main__":
    main()
