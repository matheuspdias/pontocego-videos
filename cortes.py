"""Cortes verticais (1080x1920) para TikTok, YouTube Shorts e Reels, a partir do vídeo 16:9 já renderizado.

MODO PADRÃO: CORTES SELECIONADOS (quando existe videos/<slug>/cortes.json)

    python cortes.py videos/<slug> <video_16x9.mp4> [--audio <áudio final>] [--ganchos <bloco_ganchos.mp3>] [--so <id>]
    python cortes.py videos/<slug> --frases        # lista as frases com o tempo de início, para escolher os trechos

Cada corte é um vídeo independente (sem "PARTE X DE N"): um trecho escolhido do vídeo longo, que se entende
sozinho, com um gancho no começo e o cartão "VÍDEO COMPLETO NO YOUTUBE" no fim. videos/<slug>/cortes.json:
    {"cortes": [
      {"id": "radar",                         # nome curto, vira o nome do arquivo
       "inicio": 96.2, "fim": 205.4,           # trecho do vídeo 16:9 (ajustados sozinhos ao início de frase mais próximo)
       "titulo": "O MISTÉRIO DO MH370",         # texto fixo no topo (\\N quebra a linha)
       "gancho": "Um avião com duzentas e trinta e nove pessoas sumiu do radar e continuou voando.",   # frase falada antes do trecho
       "gancho_audio": [12.4, 16.1],           # onde essa frase está no áudio do bloco de ganchos (--ganchos)
       "gancho_tela": "SUMIU DO RADAR\\NE CONTINUOU VOANDO",  # texto grande na tela durante o gancho (padrão: o próprio gancho)
       "gancho_t": 96.0,                       # quadro do vídeo 16:9 que fica de fundo no gancho (padrão: inicio)
       "capa": ["SUMIU DO RADAR", "E VOOU 7 HORAS"],  # linhas da capa (capas.py); a cena da capa é gancho_t
       "post": "Texto do post + #misterio #pontocego"}
    ]}
  * Com --ganchos e "gancho_audio": o vídeo abre com o gancho falado sobre o quadro parado, e só então entra o trecho.
  * Sem áudio do gancho: o texto do gancho aparece grande nos primeiros 3,5 s do próprio trecho.
  * Saída: out/<slug>_corte_<id>.mp4 e out/<slug>_cortes.txt (duração, avisos e texto do post de cada corte).
    O TikTok só paga vídeos com mais de 1 min e o Shorts aceita até 3 min: o script avisa fora de 62 s a 2:58.

MODO ANTIGO: SEQUENCIAL (sem cortes.json, ou com --sequencial)

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


def build_ass(path, words, t0, t1, idx, n, title, label=None, card=None):
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
    ev.append(f"Dialogue: 1,{ass_time(0)},{ass_time(dur)},Part,,0,0,0,,{{\\pos(540,395)}}{label or f'PARTE {idx} DE {n}'}")
    card_t = dur - 2.6
    if card:
        pass
    elif idx < n:
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


# ------------------------------------------------------------------ modo cortes selecionados
CARD_LEN = 2.6     # cartão final
HOOK_PAD = 0.35    # respiro entre o gancho e o trecho
TEXT_HOOK = 3.5    # duração do gancho só em texto (sem áudio)


def probe_dur(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def snap(t, sents, total, end=False):
    """leva o tempo para o silêncio antes da frase mais próxima (até 2 s de distância)"""
    marks = [s["t"] - 0.2 for s in sents] + ([total + 0.6] if end else [])
    best = min(marks, key=lambda m: abs(m - t))
    return max(0.0, best) if abs(best - t) <= 2.0 else t


def ass_head():
    th = THEME
    return f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{th['cap_font']},78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,1,7,3,5,40,40,0,1
Style: Title,{th['title_font']},62,&H00{th['title_col'][2:-1]},&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,1,0,1,5,2,5,40,40,0,1
Style: Card,{th['cap_font']},64,&H00{th['title_col'][2:-1]},&H00FFFFFF,&H00000000,&HC0000000,0,0,0,0,100,100,0,0,3,24,0,5,60,60,0,1
Style: Hook,{th['cap_font']},84,&H00FFFFFF,&H00FFFFFF,&H00000000,&HB4000000,0,0,0,0,100,100,0,0,3,26,0,5,70,70,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def hook_text(txt):
    """quebra o gancho em linhas curtas (máx. ~18 caracteres) e pinta a primeira na cor de destaque"""
    if "\\N" in txt:
        lines = txt.split("\\N")
    else:
        lines, cur = [], ""
        for w in txt.split():
            if cur and len(cur) + 1 + len(w) > 18:
                lines.append(cur); cur = w
            else:
                cur = f"{cur} {w}".strip()
        if cur:
            lines.append(cur)
    lines = [esc(l.strip().upper()) for l in lines if l.strip()]
    if not lines:
        return ""
    first = f"{{\\c{THEME['hl_col']}}}{lines[0]}{{\\c&HFFFFFF&}}"
    return "\\N".join([first] + lines[1:])


def caption_events(words, t0, t1, shift=0.0):
    ev, dur = [], t1 - t0
    inside = [w for w in words if w["t0"] >= t0 - 0.05 and w["t0"] < t1]
    chs = chunks(inside)
    for ci, ch in enumerate(chs):
        nxt = chs[ci + 1][0]["t0"] if ci + 1 < len(chs) else t1
        for j, w in enumerate(ch):
            a = w["t0"] - t0
            b = (ch[j + 1]["t0"] if j + 1 < len(ch) else min(w["t1"] + 0.35, nxt)) - t0
            b = min(b, nxt - t0, dur)
            a, b = round(a + shift, 2), round(b + shift, 2)
            if b <= a:
                continue
            parts = []
            for k, x in enumerate(ch):
                s = esc(x["w"].upper())
                parts.append(f"{{\\c{THEME['hl_col']}}}{s}{{\\c&HFFFFFF&}}" if k == j else s)
            ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{{\\pos(540,{CAP_Y})}}{' '.join(parts)}")
    return ev


def build_ass_corte(path, words, t0, t1, title, hook, hook_dur):
    """hook_dur > 0: gancho falado antes do trecho (quadro parado); hook_dur == 0: gancho só em texto no começo"""
    total = hook_dur + (t1 - t0)
    ev = [f"Dialogue: 1,{ass_time(0)},{ass_time(total)},Title,,0,0,0,,{{\\pos(540,300)}}{esc(title)}"]
    ht = hook_text(hook or "")
    if ht:
        end = hook_dur - 0.05 if hook_dur > 0 else min(TEXT_HOOK, t1 - t0)
        ev.append(f"Dialogue: 3,{ass_time(0)},{ass_time(end)},Hook,,0,0,0,,"
                  f"{{\\pos(540,{VID_Y + 300})\\fad(120,150)\\t(0,180,\\fscx106\\fscy106)\\t(180,320,\\fscx100\\fscy100)}}{ht}")
    # no gancho só em texto, as legendas ficam escondidas enquanto ele está na tela
    cap_from = t0 + (0 if hook_dur > 0 or not ht else min(TEXT_HOOK, t1 - t0))
    ev += caption_events(words, cap_from, t1, shift=hook_dur + (cap_from - t0))
    ev.append(f"Dialogue: 2,{ass_time(total - CARD_LEN)},{ass_time(total)},Card,,0,0,0,,"
              f"{{\\pos(540,{VID_Y + 340})\\fad(250,0)}}VÍDEO COMPLETO NO YOUTUBE\\N{THEME['brand']}")
    open(path, "w", encoding="utf-8").write(ass_head() + "\n".join(ev) + "\n")


def render_corte(video, audio, ass, t0, t1, out, hook_src=None, hook_rng=None, hook_t=None, hook_dur=0.0, tmp=None):
    vw = int(W * ZOOM) // 2 * 2
    vh = int(vw * 9 / 16) // 2 * 2
    dark = THEME["dark"]

    def frame_chain(src, tag):
        return (f"[{src}]split[{tag}a][{tag}b];[{tag}a]scale={vw}:{vh},crop={W}:{vh}[{tag}fg];"
                f"[{tag}b]scale=-2:{H // 4},crop={W // 4}:{H // 4},boxblur=12:2,scale={W}:{H},"
                f"eq=brightness=-{dark}:saturation=0.8[{tag}bg];[{tag}bg][{tag}fg]overlay=0:{VID_Y},fps=30,setsar=1[{tag}v]")

    seg = t1 - t0
    afmt = "aresample=48000,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo"
    ins = ["-ss", f"{t0:.3f}", "-t", f"{seg:.3f}", "-i", video, "-ss", f"{t0:.3f}", "-t", f"{seg:.3f}", "-i", audio]
    main_a = f"[1:a]{afmt},afade=t=in:d=0.15,afade=t=out:st={max(0, seg - 0.4):.2f}:d=0.4[ma]"
    if hook_dur > 0:
        still = os.path.join(tmp, "gancho.png")
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{hook_t:.3f}", "-i", video,
                        "-frames:v", "1", still], check=True)
        g0, g1 = hook_rng
        ins += ["-loop", "1", "-framerate", "30", "-t", f"{hook_dur:.3f}", "-i", still,
                "-ss", f"{max(0, g0 - 0.05):.3f}", "-t", f"{g1 - g0 + 0.1:.3f}", "-i", hook_src]
        graph = ";".join([
            frame_chain("2:v", "h"), frame_chain("0:v", "m"),
            f"[3:a]{afmt},afade=t=in:d=0.05,afade=t=out:st={max(0, g1 - g0 - 0.05):.2f}:d=0.1,"
            f"apad=whole_dur={hook_dur:.3f}[ha]",
            main_a,
            f"[hv][ha][mv][ma]concat=n=2:v=1:a=1[cv][ca]",
            f"[cv]ass={ass}:fontsdir={FONTS}[v]",
        ])
        amap = "[ca]"
    else:
        graph = ";".join([frame_chain("0:v", "m"), main_a, f"[mv]ass={ass}:fontsdir={FONTS}[v]"])
        amap = "[ma]"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *ins, "-filter_complex", graph, "-map", "[v]", "-map", amap,
                    "-c:v", "libx264", "-preset", "medium", "-crf", "27", "-maxrate", "1.6M", "-bufsize", "3.2M",
                    "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
                    "-movflags", "+faststart", out], check=True)


def run_selecao(a, slug, sents, total, words, spec):
    import tempfile
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    cortes = spec["cortes"]
    notes = [f"Cortes selecionados de {slug} ({len(cortes)} cortes independentes)",
             "Lembrete: no TikTok, ativar o selo de conteúdo gerado por IA (voz). Os mesmos arquivos servem para Shorts e Reels.", ""]
    for c in cortes:
        cid = c["id"]
        t0 = snap(float(c["inicio"]), sents, total)
        t1 = min(snap(float(c["fim"]), sents, total, end=True), total + 0.6)
        rng = c.get("gancho_audio")
        spoken = bool(a.ganchos and rng)
        hook_dur = (rng[1] - rng[0]) + HOOK_PAD if spoken else 0.0
        dur = hook_dur + (t1 - t0)
        first = next((s["text"] for s in sents if s["t"] >= t0 - 0.3), "")
        warn = []
        if dur < 62:
            warn.append("AVISO: menos de 62 s, o TikTok não paga")
        if dur > 178:
            warn.append("AVISO: mais de 2:58, passa do limite do Shorts")
        if c.get("gancho") and not spoken:
            warn.append("gancho só em texto (sem --ganchos ou sem gancho_audio)")
        notes += [f"=== {cid}: {fmt(t0)} - {fmt(t1)} do vídeo | {dur:.0f} s no corte" + (" | " + "; ".join(warn) if warn else ""),
                  f"Gancho: {c.get('gancho', '(nenhum)')}",
                  f"Trecho começa em: {first}",
                  f"Post: {c.get('post', '')}", ""]
        if a.so and a.so != cid:
            continue
        title = c.get("titulo") or a.titulo or slug.replace("-", " ").upper()
        ass = os.path.join(ROOT, "out", f"{slug}_corte_{cid}.ass")
        build_ass_corte(ass, words, t0, t1, title, c.get("gancho_tela") or c.get("gancho"), hook_dur)
        out = os.path.join(ROOT, "out", f"{slug}_corte_{cid}.mp4")
        with tempfile.TemporaryDirectory() as tmp:
            render_corte(a.video, a.audio or a.video, ass, t0, t1, out, hook_src=a.ganchos, hook_rng=rng,
                         hook_t=float(c.get("gancho_t", t0 + 0.5)), hook_dur=hook_dur, tmp=tmp)
        print(out, f"{os.path.getsize(out) / 1024 / 1024:.1f} MB", f"{probe_dur(out):.1f} s")
    open(os.path.join(ROOT, "out", f"{slug}_cortes.txt"), "w", encoding="utf-8").write("\n".join(notes) + "\n")
    print("\n".join(notes))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vdir")
    ap.add_argument("video", nargs="?")
    ap.add_argument("--audio", default=None, help="arquivo com o áudio final (narração + efeitos); padrão: o próprio vídeo")
    ap.add_argument("--ganchos", default=None, help="áudio do bloco de ganchos gerado no HeyGen (modo selecionado)")
    ap.add_argument("--frases", action="store_true", help="só lista as frases com o tempo de início")
    ap.add_argument("--sequencial", action="store_true", help="usa o modo antigo (PARTE X DE N) mesmo com cortes.json")
    ap.add_argument("--titulo", default=None)
    ap.add_argument("--partes", type=int, default=None)
    ap.add_argument("--max", type=float, default=MAX_PART)
    ap.add_argument("--cortes", default=None, help="tempos de corte manuais, separados por vírgula")
    ap.add_argument("--so", default=None, help="renderiza só esta parte (número no modo sequencial, id no selecionado)")
    ap.add_argument("--trechos", default=None, help="cortes independentes (vídeos em lista): 't0-t1,t0-t1,...'")
    ap.add_argument("--titulos", default=None, help="com --trechos: um título por trecho, separados por '|'")
    ap.add_argument("--rotulos", default=None, help="com --trechos: rótulo no lugar de 'PARTE X DE N', separados por '|'")
    a = ap.parse_args()
    slug = os.path.basename(os.path.normpath(a.vdir))
    sents, total = read_blocks(a.vdir)
    if a.frases:
        paras = paragraph_starts(a.vdir)
        for s in sents:
            mark = "¶" if norm_start(s["text"]) in paras else " "
            print(f"{max(0, s['t'] - 0.2):7.1f}  {fmt(s['t'])}  b{s['block']} {mark} {s['text']}")
        print(f"{total + 0.6:7.1f}  {fmt(total)}  FIM")
        return
    if not a.video:
        ap.error("informe o vídeo 16:9")
    spec_path = os.path.join(a.vdir, "cortes.json")
    if os.path.exists(spec_path) and not a.sequencial and not a.trechos:
        words = load_words(a.vdir, sents)
        run_selecao(a, slug, sents, total, words, json.load(open(spec_path, encoding="utf-8")))
        return
    a.so = int(a.so) if a.so else None
    if a.trechos:
        return trechos(a)
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


def trechos(a):
    """cada trecho vira um corte independente (ex.: um item de uma lista), sem 'continua na parte X'"""
    slug = os.path.basename(os.path.normpath(a.vdir))
    sents, total = read_blocks(a.vdir)
    words = load_words(a.vdir, sents)
    spans = [tuple(float(x) for x in tr.split("-")) for tr in a.trechos.split(",")]
    n = len(spans)
    titles = a.titulos.split("|") if a.titulos else [slug.replace("-", " ").upper()] * n
    labels = a.rotulos.split("|") if a.rotulos else [None] * n
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    notes = [f"Cortes independentes de {slug} ({n})"]
    for i, (t0, t1) in enumerate(spans):
        first = next((s["text"] for s in sents if s["t"] >= t0 - 0.3), "")
        notes.append(f"Corte {i + 1}: {fmt(t0)} - {fmt(t1)} ({t1 - t0:.0f} s) | {titles[i]} | começa em: {first}")
        if a.so and a.so != i + 1:
            continue
        ass = os.path.join(ROOT, "out", f"{slug}_corte{i + 1}.ass")
        build_ass(ass, words, t0, t1, i + 1, n, titles[i], labels[i], f"VÍDEO COMPLETO NO YOUTUBE\\N{THEME['brand']}")
        out = os.path.join(ROOT, "out", f"{slug}_corte{i + 1}.mp4")
        render_part(a.video, a.audio or a.video, ass, t0, t1, out)
        print(out, os.path.getsize(out) // 1024 // 1024, "MB")
    open(os.path.join(ROOT, "out", f"{slug}_cortes.txt"), "w", encoding="utf-8").write("\n".join(notes) + "\n")
    print("\n".join(notes))


if __name__ == "__main__":
    main()
