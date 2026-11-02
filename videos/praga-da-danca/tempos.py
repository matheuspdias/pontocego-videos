"""Gera narracao_blocos.txt, transcricao.txt e palavras.json a partir de ts/bN.txt
(linhas "palavra tempo|palavra tempo|...", tempos de palavra do HeyGen) e do roteiro.
Uso: python videos/praga-da-danca/tempos.py
"""
import json, os, re

D = os.path.dirname(os.path.abspath(__file__))
BASE = "https://resource2.heygen.ai/text_to_speech/cdea5e656a244864a1032edcb4fae01d/0d0e23e8170446e38b18a7380b2d30a8/id="
BLOCOS = {
    1: (164.963, "b98d6830-d43b-4091-91be-8cc0b526fc20"),
    2: (158.093, "ac0ccfb6-7db6-44ae-a71e-c105be08c170"),
    3: (177.032, "e23b0bd7-f682-4dc5-aa04-b52b850cb3e1"),
    4: (177.110, "ad85a63f-56ee-48af-a616-1663ad33f6ce"),
    5: (67.082, "1c1997fb-3842-436a-a0a8-85c936457edf"),
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
    lines = ["# A Praga da Dança de 1518 — voz \"Pedro Lima - Serious\" (HeyGen, ElevenLabs v4), sem [whispers]",
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
