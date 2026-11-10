"""Gera narracao_blocos.txt, transcricao.txt, palavras.json e ganchos.txt a partir de
ts/bN.json e ts/ganchos.json (respostas do HeyGen: audio_url, duration, words [texto, ini, fim])
e do roteiro. Uso: python videos/colonia-roanoke/tempos.py
"""
import json, os, re, unicodedata

D = os.path.dirname(os.path.abspath(__file__))
N_BLOCOS = 5


def norm(w):
    w = unicodedata.normalize("NFC", w).lower()
    return re.sub(r"[^\wà-ÿ]", "", w)


def alinhar(words_txt, api):
    """Casa cada palavra do roteiro (sem tags) com a palavra do HeyGen, pulando as tags faladas."""
    out, j = [], 0
    for w in words_txt:
        nw = norm(w)
        partes = [norm(x) for x in w.split("-") if norm(x)]
        k = j
        while k < len(api) and norm(api[k][0]) not in (nw, partes[0]):
            k += 1
        if k >= len(api) or k - j > 4:
            raise SystemExit(f"não alinhou {w!r} perto de {api[j:j+6]}")
        fim = k
        if norm(api[k][0]) != nw and len(partes) > 1:
            fim = k + len(partes) - 1
        out.append((w, api[k][1], api[fim][2]))
        j = fim + 1
    return out


def blocos_roteiro():
    rot = open(os.path.join(D, "roteiro.txt"), encoding="utf-8").read()
    partes = re.split(r"=== (?:BLOCO \d+|GANCHOS) ===\n", rot)[1:]
    return [re.sub(r"\[[^\]]+\]", "", p).split() for p in partes]


def main():
    bl = blocos_roteiro()
    meta = [json.load(open(os.path.join(D, "ts", f"b{n}.json"))) for n in range(1, N_BLOCOS + 1)]
    off, acc = [], 0.0
    for m in meta:
        off.append(acc)
        acc += m["duration"] + 1.0
    lines = ["# A Colônia Perdida de Roanoke — voz \"Pedro Lima - Serious\" (HeyGen), sem [whispers]",
             "# Áudios (baixar e juntar nesta ordem com juntar_blocos.py, 1,0 s de silêncio entre blocos):"]
    for n, m in enumerate(meta, 1):
        lines.append(f"# bloco{n} {m['duration']:8.3f}s {m['audio_url']}")
    lines.append("# Offsets absolutos: " + "  ".join(f"B{n}={o:.3f}" for n, o in enumerate(off, 1))
                 + f"  (fim ~{off[-1] + meta[-1]['duration']:.2f})")
    lines.append("# Formato: bloco | início local (s) | frase [palavra@t local]")
    trans, palavras = [], []
    for n, (m, words) in enumerate(zip(meta, bl), 1):
        pares = alinhar(words, m["words"])
        o = off[n - 1]
        for w, a, b in pares:
            palavras.append({"w": w, "t0": round(a + o, 3), "t1": round(min(b, a + 1.2) + o, 3)})
        sent = []
        for i, (w, a, b) in enumerate(pares):
            sent.append(i)
            if re.search(r"[.?!:]\"?$", w) or i == len(pares) - 1:
                ws = [pares[k][0] for k in sent]
                ts = [pares[k][1] for k in sent]
                marks = " ".join(f"[{re.sub(r'[^\wÀ-ÿ-]', '', ws[j])}@{ts[j]:.2f}]"
                                 for j in range(1, len(ws)) if j % 6 == 0)
                lines.append(f"{n}|{ts[0]:.2f}|{' '.join(ws)}" + (f" {marks}" if marks else ""))
                tt = ts[0] + o
                trans.append(f"({int(tt // 60)}:{tt % 60:05.2f}) {' '.join(ws)}")
                sent = []
    open(os.path.join(D, "narracao_blocos.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    open(os.path.join(D, "transcricao.txt"), "w", encoding="utf-8").write("\n".join(trans) + "\n")
    json.dump(palavras, open(os.path.join(D, "palavras.json"), "w", encoding="utf-8"), ensure_ascii=False)

    # ganchos: cada linha do bloco extra
    g = json.load(open(os.path.join(D, "ts", "ganchos.json")))
    api = [[w["text"], w["start_time"], w["end_time"]] for w in g["original_words"]]
    rot = open(os.path.join(D, "roteiro.txt"), encoding="utf-8").read().split("=== GANCHOS ===\n")[1]
    ids = ["abertura", "mapa", "forja"]
    gl = [f"# Ganchos dos cortes — bloco extra HeyGen (Pedro Lima - Serious), {g['duration']:.3f} s", f"# {g['audio_url']}"]
    j = 0
    for gid, linha in zip(ids, [l for l in rot.strip().split("\n") if l.strip()]):
        ws = re.sub(r"\[[^\]]+\]", "", linha).split()
        pares = alinhar(ws, api[j:])
        j += [norm(x[0]) for x in api[j:]].index(norm(ws[-1])) + 1
        a, b = max(0.0, pares[0][1] - 0.1), min(g["duration"], pares[-1][2] + 0.1)
        gl.append(f"{gid:12s} {a:.2f}-{b:.2f}  {' '.join(ws)}")
    open(os.path.join(D, "ganchos.txt"), "w", encoding="utf-8").write("\n".join(gl) + "\n")
    print("offsets:", [round(o, 3) for o in off], "fim:", round(off[-1] + meta[-1]["duration"], 2))


if __name__ == "__main__":
    main()
