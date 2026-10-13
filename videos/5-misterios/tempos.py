"""Gera narracao_blocos.txt, transcricao.txt e palavras.json a partir do roteiro + tempos de palavra do HeyGen.

ts/bN.txt = início (s) de cada palavra do bloco N (sem as tags [..]), na ordem do roteiro.
Uso: python videos/5-misterios/tempos.py
"""
import json, os, re

D = os.path.dirname(os.path.abspath(__file__))
BASE = "https://resource2.heygen.ai/text_to_speech/cdea5e656a244864a1032edcb4fae01d/0d0e23e8170446e38b18a7380b2d30a8/id="
# bloco: (duração em s, id do áudio)
BLOCOS = {
    1: (45.244, "e1f136f4-1c09-48f4-b1e2-b9d87c1b5305"),
    2: (155.507, "f9e90052-dc85-46c7-9088-6c44f082a484"),
    3: (164.467, "6859b2b1-4ee3-4336-bcf4-bda61c861de1"),
    4: (181.185, "82d01eff-5de5-4417-817c-2b8175bf3e10"),
    5: (163.265, "b96212c7-ea08-4686-b026-c12199e02268"),
    6: (175.987, "711ea355-ba9a-44b6-aff0-5b5358963975"),
    7: (41.874, "eb6d5bd9-de72-4f54-989c-f69e8cdfd7e6"),
}
EST5 = 172.0  # estimativa do bloco 5 enquanto o áudio não existe


def offsets():
    off, acc = {}, 0.0
    for n in sorted(BLOCOS):
        off[n] = acc
        acc += (BLOCOS[n][0] or EST5) + 1.0
    return off


def main():
    rot = open(os.path.join(D, "roteiro.txt"), encoding="utf-8").read()
    blocos = re.split(r"=== BLOCO \d+ ===\n", rot)[1:]
    off = offsets()
    lines = ["# 5 mistérios que nunca foram resolvidos — voz \"Pedro Lima - Serious\" (HeyGen, ElevenLabs v4)",
             "# Áudios (baixar e juntar nesta ordem com juntar_blocos.py, 1,0 s de silêncio entre blocos):"]
    for n in sorted(BLOCOS):
        dur, aid = BLOCOS[n]
        lines.append(f"# bloco{n} {dur or 0:8.3f}s {BASE + aid + '.wav' if aid else 'PENDENTE'}")
    lines.append("# Formato: bloco | início local (s) | frase [palavra@t local]")
    trans, palavras = [], []
    for n in sorted(BLOCOS):
        p = os.path.join(D, "ts", f"b{n}.txt")
        if not os.path.exists(p):
            print(f"bloco {n}: sem tempos (pendente)")
            continue
        words = re.sub(r"\[[^\]]+\]", "", blocos[n - 1]).split()
        ts = [float(x) for x in open(p).read().split()]
        assert len(words) == len(ts), (n, len(words), len(ts))
        ends = ts[1:] + [BLOCOS[n][0]]
        for w, a, b in zip(words, ts, ends):
            palavras.append({"w": w, "t0": round(a + off[n], 3), "t1": round(min(b, a + 1.2) + off[n], 3)})
        sent = []
        for i, w in enumerate(words):
            sent.append(i)
            if (re.search(r"[.?!:]\"?$", w) and not re.fullmatch(r"[A-Z]\.", w)) or i == len(words) - 1:
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
