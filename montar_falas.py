"""
Monta a narração de várias vozes do formato "Você decide" (TikTok vertical do Ponto Cego).

Cada personagem é gerado num bloco único do HeyGen com todas as falas dele, na ordem da história.
Este script recorta cada fala pelo tempo das palavras e monta tudo na ordem do roteiro.

    python montar_falas.py videos/<slug> --audio voce=bloco_voce.mp3 passageiro=bloco_pass.mp3
    python montar_falas.py videos/<slug> --estimar        # sem áudio: tempos estimados para a prévia

Entradas em videos/<slug>/:
  falas.json            {"vozes": {"voce": {"voice_id": "..."}, ...},
                         "falas": [{"quem": "voce", "texto": "...", "pensa": true, "pausa": 0.35}, ...],
                         "cauda": 7.0}                     # segundos sem fala no fim (cartão de escolha)
  palavras_<quem>.json  "original_words" da resposta do HeyGen ([{"text", "start_time", "end_time"}])
Saídas:
  out/<slug>_narracao.wav   (com --audio)
  videos/<slug>/linhas.json {"linhas": [{"i", "quem", "pensa", "texto", "t0", "t1", "palavras": [{"w", "t0", "t1"}]}],
                             "fim_falas": s, "dur": s, "estimado": bool}
"""
import argparse
import json
import os
import re
import subprocess

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
SR = 48000
PALAVRA = re.compile(r"[0-9A-Za-zÀ-ÿ]+(?:['’-][0-9A-Za-zÀ-ÿ]+)*")


def tokens(texto):
    return PALAVRA.findall(re.sub(r"\[[^\]]*\]", " ", texto))


def norm(w):
    return re.sub(r"[^0-9a-zà-ÿ]", "", w.lower())


def carregar_palavras(path):
    raw = json.load(open(path, encoding="utf-8"))
    if isinstance(raw, dict):
        raw = raw.get("original_words") or raw.get("words") or raw.get("palavras")
    out = []
    for w in raw:
        txt = w.get("text", w.get("w", ""))
        t0 = w.get("start_time", w.get("t0"))
        t1 = w.get("end_time", w.get("t1"))
        if txt.startswith("<") or not tokens(txt):
            continue
        for tok in tokens(txt):  # "meia-noite" pode vir junto ou separado
            out.append({"w": tok, "t0": float(t0), "t1": float(t1)})
    return out


def decodificar(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, dtype=np.float32).copy()


def fade(x, ms=12):
    n = min(len(x) // 2, int(SR * ms / 1000))
    if n > 0:
        r = np.linspace(0, 1, n, dtype=np.float32)
        x[:n] *= r
        x[-n:] *= r[::-1]
    return x


def atribuir(falas, quem, palavras):
    """distribui as palavras do bloco de uma voz entre as falas dela (na ordem)"""
    idx = [i for i, f in enumerate(falas) if f["quem"] == quem]
    pos = 0
    res = {}
    for i in idx:
        toks = tokens(falas[i]["texto"])
        seg = palavras[pos:pos + len(toks)]
        if len(seg) < len(toks):
            raise SystemExit(f"o bloco de '{quem}' acabou antes da fala {i}: confira o texto gerado")
        dif = sum(1 for a, b in zip(toks, seg) if norm(a) != norm(b["w"]))
        if dif > max(1, len(toks) // 4):
            print(f"  ATENÇÃO fala {i} ({quem}): {dif} palavras diferentes do roteiro")
            print("    roteiro:", " ".join(toks))
            print("    áudio:  ", " ".join(w["w"] for w in seg))
        res[i] = [dict(w, w=t) for w, t in zip(seg, toks)]
        pos += len(toks)
    if pos != len(palavras):
        print(f"  ATENÇÃO: sobraram {len(palavras) - pos} palavras no bloco de '{quem}'")
    return res


def montar(vdir, audios, gap, cauda, saida):
    cfg = json.load(open(os.path.join(vdir, "falas.json"), encoding="utf-8"))
    falas = cfg["falas"]
    cauda = cfg.get("cauda", 7.0) if cauda is None else cauda
    palavras_de = {}
    sinais = {}
    for quem in sorted({f["quem"] for f in falas}):
        palavras_de[quem] = atribuir(falas, quem, carregar_palavras(os.path.join(vdir, f"palavras_{quem}.json")))
        sinais[quem] = decodificar(audios[quem]) if audios else None

    pedacos, linhas, t = [], [], 0.0
    for i, f in enumerate(falas):
        quem = f["quem"]
        ws = palavras_de[quem][i]
        a, b = ws[0]["t0"] - 0.06, ws[-1]["t1"] + 0.16
        # não invadir a fala vizinha do mesmo bloco
        viz = [j for j in palavras_de[quem] if j != i]
        ant = max([palavras_de[quem][j][-1]["t1"] for j in viz if j < i] or [0.0])
        prox = min([palavras_de[quem][j][0]["t0"] for j in viz if j > i] or [1e9])
        a = max(a, (ant + ws[0]["t0"]) / 2, 0.0)
        b = min(b, (ws[-1]["t1"] + prox) / 2)
        pausa = f.get("pausa", gap) if i else 0.25
        t += pausa
        pedacos.append(np.zeros(int(pausa * SR), dtype=np.float32))
        if sinais[quem] is not None:
            seg = fade(sinais[quem][int(a * SR):int(b * SR)].copy())
            pedacos.append(seg)
            dur = len(seg) / SR
        else:
            dur = b - a
        off = t - a
        linhas.append({"i": i, "quem": quem, "pensa": bool(f.get("pensa")), "texto": f["texto"],
                       "t0": round(ws[0]["t0"] + off, 3), "t1": round(ws[-1]["t1"] + off, 3),
                       "palavras": [{"w": w["w"], "t0": round(w["t0"] + off, 3), "t1": round(w["t1"] + off, 3)} for w in ws]})
        t += dur
    fim = t
    pedacos.append(np.zeros(int(cauda * SR), dtype=np.float32))
    t += cauda
    out = {"linhas": linhas, "fim_falas": round(fim, 3), "dur": round(t, 3), "estimado": False}
    json.dump(out, open(os.path.join(vdir, "linhas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if audios:
        x = np.concatenate(pedacos)
        pico = float(np.max(np.abs(x))) or 1.0
        x = x / pico * 0.89
        os.makedirs(os.path.dirname(saida) or ".", exist_ok=True)
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                              "-c:a", "pcm_f32le", saida], stdin=subprocess.PIPE)
        p.communicate(x.astype(np.float32).tobytes())
        print(saida, f"{t:.2f}s (falas até {fim:.2f}s)")
    print(os.path.join(vdir, "linhas.json"), f"{len(linhas)} falas")


def estimar(vdir, gap, cauda):
    """tempos estimados (2,7 palavras/s) para montar as cenas antes do áudio chegar"""
    cfg = json.load(open(os.path.join(vdir, "falas.json"), encoding="utf-8"))
    cauda = cfg.get("cauda", 7.0) if cauda is None else cauda
    t, linhas = 0.0, []
    for i, f in enumerate(cfg["falas"]):
        t += f.get("pausa", gap) if i else 0.25
        ws = []
        for tok in tokens(f["texto"]):
            d = 0.16 + 0.055 * len(tok)
            ws.append({"w": tok, "t0": round(t, 3), "t1": round(t + d, 3)})
            t += d + 0.06
            if tok and f["texto"].find(tok + ",") >= 0:
                t += 0.15
        linhas.append({"i": i, "quem": f["quem"], "pensa": bool(f.get("pensa")), "texto": f["texto"],
                       "t0": ws[0]["t0"], "t1": ws[-1]["t1"], "palavras": ws})
        t += 0.2
    out = {"linhas": linhas, "fim_falas": round(t, 3), "dur": round(t + cauda, 3), "estimado": True}
    json.dump(out, open(os.path.join(vdir, "linhas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"estimado: falas até {t:.1f}s, total {t + cauda:.1f}s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vdir")
    ap.add_argument("--audio", nargs="*", default=[], help="quem=arquivo (um por voz)")
    ap.add_argument("--estimar", action="store_true")
    ap.add_argument("--gap", type=float, default=0.35, help="silêncio padrão entre falas")
    ap.add_argument("--cauda", type=float, default=None)
    ap.add_argument("--saida", default=None)
    a = ap.parse_args()
    if a.estimar:
        return estimar(a.vdir, a.gap, a.cauda)
    audios = dict(x.split("=", 1) for x in a.audio)
    slug = os.path.basename(os.path.normpath(a.vdir))
    montar(a.vdir, audios, a.gap, a.cauda, a.saida or os.path.join(ROOT, "out", f"{slug}_narracao.wav"))


if __name__ == "__main__":
    main()
