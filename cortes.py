"""Cortes verticais (1080x1920) para TikTok, YouTube Shorts e Reels, a partir do vídeo 16:9 já renderizado.

    python cortes.py videos/<slug> <video_16x9.mp4> [--audio <arquivo com o áudio final>] [--titulo "..."] [--partes N]
                     [--max 170] [--cortes 150.2,300.5]

O que faz:
  * divide a história em partes de 1 a ~2:50 (TikTok só paga vídeos com mais de 1 min; Shorts aceita até 3 min),
    cortando sempre no início de uma frase (no silêncio antes dela), perto das mudanças de assunto;
  * monta cada parte em 1080x1920: fundo com o próprio vídeo desfocado e escurecido, título + "PARTE X DE N" no topo,
    o vídeo 16:9 no meio e legendas grandes palavra por palavra embaixo (a palavra falada fica destacada);
  * no fim de cada parte entra o cartão "CONTINUA NA PARTE X" e, na última, "HISTÓRIA COMPLETA NO YOUTUBE".

Tempos das palavras: usa videos/<slug>/palavras.json (word_timestamps do HeyGen em tempo absoluto: [{"w": "...", "t0": s, "t1": s}, ...]).
Se não existir, estima a partir de narracao_blocos.txt (início de cada frase + marcas [palavra@t]).
Saída: out/<slug>_parte1.mp4 ... e out/<slug>_cortes.txt (tempos de cada parte e legenda sugerida para o post).
"""
import argparse
import json
import math
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(ROOT, "fonts")

# tema do canal (cores em ASS: &HBBGGRR&)
THEME = dict(
    brand="PONTO CEGO",
    title_font="Cinzel", title_col="&H3DA3E0&",      # âmbar
    cap_font="Montserrat ExtraBold", hl_col="&H3DA3E0&",
    dark=0.18,                                        # escurecimento do fundo desfocado
)
# cada repositório pode sobrescrever o tema em tema_cortes.json (ex.: Faz a Conta)
if os.path.exists(os.path.join(ROOT, "tema_cortes.json")):
    THEME.update(json.load(open(os.path.join(ROOT, "tema_cortes.json"), encoding="utf-8")))

W, H = 1080, 1920
VID_Y = 470            # topo do vídeo 16:9 no quadro vertical
ZOOM = 1.12            # vídeo um pouco maior que a largura (corta ~7% de cada lado do 16:9)
CAP_Y = 1330           # centro da legenda
MAX_PART = 170.0       # 2:50


# ------------------------------------------------------------------ leitura de tempos
def read_blocks(vdir):
    """frases com início absoluto, a partir de narracao_blocos.txt"""
    path = os.path.join(vdir, "narracao_blocos.txt")
    durs, rows = {}, []
    for ln in open(path, encoding="utf-8"):
        m = re.match(r"#\s*bloco(\d+)\s+([\d.]+)s", ln)
        if m:
            durs[int(m[1])] = float(m[2])
            continue
        if ln.startswith("#") or "|" not in ln:
            continue
        b, t, txt = ln.rstrip("\n").split("|", 2)
        rows.append((int(b), float(t), txt))
    off, acc = {}, 0.0
    for b in sorted(durs):
        off[b] = acc
        acc += durs[b] + 1.0
    total = acc - 1.0
    sents = []
    for b, t, txt in rows:
        anchors = [(w, float(x) + off[b]) for w, x in re.findall(r"(\S+?)@([\d.]+)", " ".join(re.findall(r"\[([^\]]*@[^\]]*)\]", txt)))]
        clean = re.sub(r"\s*\[[^\]]*@[^\]]*\]", "", txt).strip()
        sents.append(dict(t=t + off[b], text=clean, anchors=anchors, block=b))
    for i, s in enumerate(sents):
        nxt = sents[i + 1]["t"] if i + 1 < len(sents) else total
        s["next"] = nxt
    return sents, total


def estimate_words(sents):
    """distribui as palavras de cada frase no tempo (proporcional ao tamanho), presas às marcas [palavra@t]"""
    words = []
    for s in sents:
        toks = s["text"].split()
        if not toks:
            continue
        span = min(s["next"] - s["t"] - 0.3, 0.068 * len(s["text"]) + 0.3)
        span = max(span, 0.25 * len(toks))
        span = min(span, s["next"] - s["t"] - 0.05)
        w = [len(x) + 2 for x in toks]
        tot = sum(w)
        times, acc = [], 0
        for x in w:
            times.append(s["t"] + span * acc / tot)
            acc += x
        # prende nas marcas conhecidas (ajuste linear por trechos)
        pins = [(0, s["t"])]
        for aw, at in s["anchors"]:
            key = re.sub(r"\W", "", aw.lower())
            for j, tok in enumerate(toks):
                if j > pins[-1][0] and re.sub(r"\W", "", tok.lower()).startswith(key[:5]) and key:
                    pins.append((j, at))
                    break
        pins.append((len(toks), s["t"] + span))
        for (j0, t0), (j1, t1) in zip(pins, pins[1:]):
            if j1 <= j0:
                continue
            e0, e1 = times[j0], (times[j1] if j1 < len(toks) else s["t"] + span)
            for j in range(j0, min(j1, len(toks))):
                k = (times[j] - e0) / (e1 - e0) if e1 > e0 else 0
                times[j] = t0 + k * (t1 - t0)
        for j, tok in enumerate(toks):
            t1 = times[j + 1] if j + 1 < len(toks) else s["t"] + span
            words.append(dict(w=tok, t0=times[j], t1=t1))
    return words


def load_words(vdir, sents):
    p = os.path.join(vdir, "palavras.json")
    if os.path.exists(p):
        return [w for w in json.load(open(p, encoding="utf-8")) if not re.match(r"^\[.*\]$|^<", w["w"])]
    return estimate_words(sents)


# ------------------------------------------------------------------ escolha dos cortes
def paragraph_starts(vdir):
    """primeiras palavras de cada parágrafo do roteiro (mudanças de assunto)"""
    p = os.path.join(vdir, "roteiro.txt")
    keys = set()
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            ln = re.sub(r"\[[^\]]*\]", "", ln).strip()
            if ln and not ln.startswith("==="):
                keys.add(norm_start(ln))
    return keys


def norm_start(txt, n=4):
    return " ".join(re.sub(r"[^\w ]", "", txt.lower()).split()[:n])


def choose_cuts(sents, total, max_len=MAX_PART, n=None, paras=()):
    """escolhe os cortes (inícios de frase) para que todas as partes fiquem entre 62 s e max_len,
    perto do tamanho ideal, preferindo começo de bloco e de parágrafo (mudança de assunto)"""
    cands = [(0.0, 0)]
    for i, s in enumerate(sents[1:], 1):
        bonus = (25 if norm_start(s["text"]) in paras else 0) + (40 if s["block"] != sents[i - 1]["block"] else 0)
        cands.append((s["t"] - 0.2, bonus))
    cands.append((total + 0.6, 0))
    best_plan = None
    for parts in ([n] if n else range(math.ceil(total / max_len), math.ceil(total / max_len) + 3)):
        ideal = total / parts
        INF = float("inf")
        # dp[k][i] = menor custo para terminar a parte k no candidato i
        dp = [[INF] * len(cands) for _ in range(parts + 1)]
        prev = [[-1] * len(cands) for _ in range(parts + 1)]
        dp[0][0] = 0
        for k in range(1, parts + 1):
            for i in range(1, len(cands)):
                ti, bi = cands[i]
                for j in range(i):
                    if dp[k - 1][j] == INF:
                        continue
                    L = ti - cands[j][0]
                    if L < 62 or L > max_len:
                        continue
                    c = dp[k - 1][j] + 100 * abs(L - ideal) / ideal - (bi if i < len(cands) - 1 else 0)
                    if c < dp[k][i]:
                        dp[k][i], prev[k][i] = c, j
        last = len(cands) - 1
        if dp[parts][last] < INF and (best_plan is None or dp[parts][last] < best_plan[0]):
            cuts, i, k = [], last, parts
            while k > 0:
                i = prev[k][i]; k -= 1
                if i > 0:
                    cuts.append(cands[i][0])
            best_plan = (dp[parts][last], sorted(cuts))
        if best_plan:
            break
    return best_plan[1] if best_plan else []


# ------------------------------------------------------------------ legendas (ASS)
def ass_time(t):
    t = max(0, t)
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def esc(s):
    return s.replace("{", "(").replace("}", ")").replace("\n", " ")


def chunks(words, maxw=3, maxc=20):
    out, cur = [], []
    for w in words:
        cur.append(w)
        txt = " ".join(x["w"] for x in cur)
        if len(cur) >= maxw or len(txt) >= maxc or re.search(r"[.!?,:;]$", w["w"]):
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def build_ass(path, words, t0, t1, idx, n, title):
    th = THEME
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{th['cap_font']},78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,1,7,3,5,40,40,0,1
Style: Title,{th['title_font']},62,&H00{th['title_col'][2:-1]},&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,1,0,1,5,2,5,40,40,0,1
Style: Part,{th['cap_font']},40,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,4,0,1,4,0,5,40,40,0,1
Style: Card,{th['cap_font']},64,&H00{th['title_col'][2:-1]},&H00FFFFFF,&H00000000,&HC0000000,0,0,0,0,100,100,0,0,3,24,0,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    dur = t1 - t0
    ev = []
    ev.append(f"Dialogue: 1,{ass_time(0)},{ass_time(dur)},Title,,0,0,0,,{{\\pos(540,270)}}{esc(title)}")
    ev.append(f"Dialogue: 1,{ass_time(0)},{ass_time(dur)},Part,,0,0,0,,{{\\pos(540,395)}}PARTE {idx} DE {n}")
    card_t = dur - 2.6
    if idx < n:
        card = f"CONTINUA NA PARTE {idx + 1}"
    else:
        card = f"HISTÓRIA COMPLETA NO YOUTUBE\\N{th['brand']}"
    ev.append(f"Dialogue: 2,{ass_time(card_t)},{ass_time(dur)},Card,,0,0,0,,{{\\pos(540,{VID_Y + 340})\\fad(250,0)}}{card}")
    inside = [w for w in words if w["t0"] >= t0 - 0.05 and w["t0"] < t1]
    chs = chunks(inside)
    for ci, ch in enumerate(chs):
        nxt = chs[ci + 1][0]["t0"] if ci + 1 < len(chs) else t1
        for j, w in enumerate(ch):
            a = w["t0"] - t0
            b = (ch[j + 1]["t0"] if j + 1 < len(ch) else min(w["t1"] + 0.35, nxt)) - t0
            b = min(b, nxt - t0, dur)
            a, b = round(a, 2), round(b, 2)
            if b <= a:
                continue
            parts = []
            for k, x in enumerate(ch):
                s = esc(x["w"].upper())
                parts.append(f"{{\\c{THEME['hl_col']}}}{s}{{\\c&HFFFFFF&}}" if k == j else s)
            ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{{\\pos(540,{CAP_Y})}}{' '.join(parts)}")
    open(path, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")


# ------------------------------------------------------------------ render
def render_part(video, audio, ass, t0, t1, out):
    vw = int(W * ZOOM) // 2 * 2
    vh = int(vw * 9 / 16) // 2 * 2
    dark = THEME["dark"]
    fg = f"[0:v]scale={vw}:{vh},crop={W}:{vh}[fg]"
    bg = (f"[0:v]scale=-2:{H // 4},crop={W // 4}:{H // 4},boxblur=12:2,scale={W}:{H},"
          f"eq=brightness=-{dark}:saturation=0.8[bg]")
    graph = f"{fg};{bg};[bg][fg]overlay=0:{VID_Y},ass={ass}:fontsdir={FONTS}[v]"
    a_in = ["-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", audio]
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", video, *a_in,
                    "-filter_complex", graph, "-map", "[v]", "-map", "1:a",
                    "-af", f"afade=t=in:d=0.15,afade=t=out:st={max(0, t1 - t0 - 0.4):.2f}:d=0.4",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "27", "-maxrate", "1.6M", "-bufsize", "3.2M",
                    "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
                    "-movflags", "+faststart", out], check=True)


def fmt(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vdir")
    ap.add_argument("video")
    ap.add_argument("--audio", default=None, help="arquivo com o áudio final (narração + efeitos); padrão: o próprio vídeo")
    ap.add_argument("--titulo", default=None)
    ap.add_argument("--partes", type=int, default=None)
    ap.add_argument("--max", type=float, default=MAX_PART)
    ap.add_argument("--cortes", default=None, help="tempos de corte manuais, separados por vírgula")
    ap.add_argument("--so", type=int, default=None, help="renderiza só esta parte (prévia)")
    a = ap.parse_args()
    slug = os.path.basename(os.path.normpath(a.vdir))
    sents, total = read_blocks(a.vdir)
    words = load_words(a.vdir, sents)
    cuts = [float(x) for x in a.cortes.split(",")] if a.cortes else choose_cuts(sents, total, a.max, a.partes, paragraph_starts(a.vdir))
    bounds = [0.0] + cuts + [total + 0.6]
    n = len(bounds) - 1
    title = a.titulo or slug.replace("-", " ").upper()
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    notes = [f"Cortes de {slug} ({n} partes)"]
    for i in range(n):
        t0, t1 = bounds[i], bounds[i + 1]
        first = next((s["text"] for s in sents if s["t"] >= t0 - 0.3), "")
        notes.append(f"Parte {i + 1}: {fmt(t0)} - {fmt(t1)} ({t1 - t0:.0f} s) | começa em: {first}")
        if a.so and a.so != i + 1:
            continue
        ass = os.path.join(ROOT, "out", f"{slug}_parte{i + 1}.ass")
        build_ass(ass, words, t0, t1, i + 1, n, title)
        out = os.path.join(ROOT, "out", f"{slug}_parte{i + 1}.mp4")
        render_part(a.video, a.audio or a.video, ass, t0, t1, out)
        print(out, os.path.getsize(out) // 1024 // 1024, "MB")
    open(os.path.join(ROOT, "out", f"{slug}_cortes.txt"), "w", encoding="utf-8").write("\n".join(notes) + "\n")
    print("\n".join(notes))


if __name__ == "__main__":
    main()
