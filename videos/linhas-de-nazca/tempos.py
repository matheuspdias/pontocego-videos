"""Gera narracao_blocos.txt, transcricao.txt e palavras.json a partir de ts/bN.txt
(linhas "palavra tempo|palavra tempo|...", tempos de palavra do HeyGen) e do roteiro.
Uso: python videos/linhas-de-nazca/tempos.py
"""
import json, os, re

D = os.path.dirname(os.path.abspath(__file__))
BASE = "https://resource2.heygen.ai/text_to_speech/cdea5e656a244864a1032edcb4fae01d/0d0e23e8170446e38b18a7380b2d30a8/id="
BLOCOS = {
    1: (155.115, "554a72dc-7694-4780-ad3e-eb128e5601fa"),
    2: (167.523, "2d0f2f32-ffe9-428b-a164-3c9e5c462e71"),
    3: (140.382, "b0a1276a-af8d-4171-a8d3-954cc7c9d979"),
    4: (171.442, "72962839-d33c-4db8-b330-57791f11dd73"),
    5: (150.152, "34e45b7f-3fd8-4cd9-a2c9-78e18e2cacf9"),
}


def offsets():
    off, acc = {}, 0.0
    for n in sorted(BLOCOS):
        off[n] = acc
        acc += BLOCOS[n][0] + 1.0
    return off


def ler_ts(n, words):
    """ts/sN.txt: tempos de início (HeyGen) de cada palavra do bloco, na ordem do roteiro."""
    ts = [float(x) for x in open(os.path.join(D, "ts", f"s{n}.txt")).read().split()]
    assert len(ts) == len(words), (n, len(ts), len(words))
    assert all(b >= a for a, b in zip(ts, ts[1:])), n
    return list(zip(words, ts))


def main():
    rot = open(os.path.join(D, "roteiro.txt"), encoding="utf-8").read()
    blocos = re.split(r"=== BLOCO \d+ ===\n", rot)[1:]
    off = offsets()
    lines = ["# As Linhas de Nazca — voz \"Pedro Lima - Serious\" (HeyGen, ElevenLabs v4), sem [whispers]",
             "# Áudios (baixar e juntar nesta ordem com juntar_blocos.py, 1,0 s de silêncio entre blocos):"]
    for n in sorted(BLOCOS):
        dur, aid = BLOCOS[n]
        lines.append(f"# bloco{n} {dur:8.3f}s {BASE + aid + '.wav'}")
    lines.append("# Offsets absolutos: " + "  ".join(f"B{n}={off[n]:.3f}" for n in sorted(off))
                 + f"  (fim ~{off[max(off)] + BLOCOS[max(off)][0]:.2f})")
    lines.append("# Formato: bloco | início local (s) | frase [palavra@t local]")
    trans, palavras = [], []
    for n in sorted(BLOCOS):
        words = re.sub(r"\[[^\]]+\]", "", blocos[n - 1]).split()
        pares = ler_ts(n, words)
        assert [w for w, _ in pares] == words, (n, len(words), len(pares),
               next((i, a, b) for i, (a, (b, _)) in enumerate(zip(words, pares)) if a != b))
        ts = [t for _, t in pares]
        ends = ts[1:] + [BLOCOS[n][0]]
        for w, a, b in zip(words, ts, ends):
            palavras.append({"w": w, "t0": round(a + off[n], 3), "t1": round(min(b, a + 1.2) + off[n], 3)})
        sent = []
        for i, w in enumerate(words):
            sent.append(i)
            if re.search(r"[.?!:]\"?$", w) or i == len(words) - 1:
                ws = [words[k] for k in sent]
                marks = " ".join(f"[{re.sub(r'[^\wÀ-ÿ-]', '', words[k])}@{ts[k]:.2f}]"
                                 for j, k in enumerate(sent) if j > 0 and j % 6 == 0)
                lines.append(f"{n}|{ts[sent[0]]:.2f}|{' '.join(ws)}" + (f" {marks}" if marks else ""))
                tt = ts[sent[0]] + off[n]
                trans.append(f"({int(tt // 60)}:{tt % 60:05.2f}) {' '.join(ws)}")
                sent = []
    open(os.path.join(D, "narracao_blocos.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    open(os.path.join(D, "transcricao.txt"), "w", encoding="utf-8").write("\n".join(trans) + "\n")
    json.dump(palavras, open(os.path.join(D, "palavras.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("offsets:", {k: round(v, 3) for k, v in off.items()})


if __name__ == "__main__":
    main()
