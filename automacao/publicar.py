"""
Publicador automático do Ponto Cego (roda no GitHub Actions).

Pega um vídeo da fila (fila/<slug>.json), baixa os blocos de narração do HeyGen,
junta, renderiza e sobe no YouTube já agendado.

    python automacao/publicar.py fila/<slug>.json             # fluxo completo
    python automacao/publicar.py fila/<slug>.json --sem-upload  # só baixa, junta e renderiza (teste)
    python automacao/publicar.py fila/<slug>.json --audio a.wav b.wav --sem-upload  # usa áudios locais

Formato do fila/<slug>.json (o modo automático escreve; veja automacao/AUTOMATICO.md):
{
  "slug": "voynich",
  "publicar_em": "2026-10-20T18:00:00-03:00",
  "audio_blocos": ["https://resource2.heygen.ai/...wav", "..."],   # na ordem
  "duracoes": [107.9, 101.3],                                       # opcional, confere o download
  "titulo": "...",
  "descricao": "...",
  "tags": ["...", "..."],
  "thumbnail": "videos/voynich/thumb/voynich_thumb_A.png",
  "categoria": "27",          # 27 = Educação (padrão); 24 = Entretenimento
  "playlist": ""              # opcional: id de playlist
}

Credenciais (secrets do repositório): YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.
Gere o refresh token uma vez no seu PC com automacao/autorizar_youtube.py.
"""
import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUSO = dt.timezone(dt.timedelta(hours=-3))  # America/Sao_Paulo (sem horário de verão desde 2019)
FOLGA_MIN = 20  # se o horário marcado já passou ou está perto demais, agenda para agora + 20 min


def log(*a):
    print("[publicar]", *a, flush=True)


def duracao(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", path]).decode().strip()
    return float(out)


def baixar(url, destino, tentativas=4):
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "pontocego-publicador"})
            with urllib.request.urlopen(req, timeout=120) as r, open(destino, "wb") as f:
                shutil.copyfileobj(r, f)
            if os.path.getsize(destino) < 10_000:
                raise RuntimeError(f"arquivo pequeno demais ({os.path.getsize(destino)} bytes)")
            return
        except Exception as e:  # noqa: BLE001
            log(f"falha ao baixar ({i + 1}/{tentativas}): {e}")
            time.sleep(5 * (i + 1))
    raise SystemExit(f"não consegui baixar {url}. O link do HeyGen pode ter expirado: gere o bloco de novo.")


def validar(m):
    faltando = [k for k in ("slug", "publicar_em", "audio_blocos", "titulo", "descricao") if not m.get(k)]
    if faltando:
        raise SystemExit(f"fila: faltam campos {faltando}")
    cenas = os.path.join(RAIZ, "videos", m["slug"], "scenes.py")
    if not os.path.exists(cenas):
        raise SystemExit(f"não achei {cenas}")
    return cenas


def horario(m):
    alvo = dt.datetime.fromisoformat(m["publicar_em"])
    if alvo.tzinfo is None:
        alvo = alvo.replace(tzinfo=FUSO)
    agora = dt.datetime.now(dt.timezone.utc)
    if alvo < agora + dt.timedelta(minutes=FOLGA_MIN):
        novo = agora + dt.timedelta(minutes=FOLGA_MIN)
        log(f"horário {alvo.isoformat()} já passou ou está perto demais; agendando para {novo.astimezone(FUSO).isoformat()}")
        alvo = novo
    return alvo.astimezone(dt.timezone.utc).replace(microsecond=0)


def limpar_texto(s, limite):
    s = s.replace("<", "‹").replace(">", "›")  # o YouTube recusa < e > em título e descrição
    return s[:limite]


def limpar_tags(tags):
    saida, total = [], 0
    for t in tags or []:
        t = t.strip().replace("<", "").replace(">", "").replace(",", "")
        if not t:
            continue
        custo = len(t) + (2 if " " in t else 0) + (1 if saida else 0)  # o YouTube conta aspas e vírgulas
        if total + custo > 480:
            break
        saida.append(t)
        total += custo
    return saida


def produzir(m, cenas, audios_locais=None):
    slug = m["slug"]
    pasta = os.path.join(RAIZ, "out", slug)
    os.makedirs(pasta, exist_ok=True)

    if audios_locais:
        blocos = audios_locais
    else:
        blocos = []
        for i, url in enumerate(m["audio_blocos"], 1):
            ext = os.path.splitext(url.split("?")[0])[1] or ".wav"
            destino = os.path.join(pasta, f"bloco{i}{ext}")
            log(f"baixando bloco {i}/{len(m['audio_blocos'])}")
            baixar(url, destino)
            blocos.append(destino)

    esperadas = m.get("duracoes") or []
    for i, b in enumerate(blocos):
        d = duracao(b)
        esperado = esperadas[i] if i < len(esperadas) else None
        aviso = "" if esperado is None or abs(d - esperado) < 0.6 else f"  ATENÇÃO: esperado {esperado:.1f}s"
        log(f"bloco {i + 1}: {d:.2f}s{aviso}")
        if aviso:
            raise SystemExit("a duração de um bloco não bate com a usada nas cenas: o vídeo sairia fora de sincronia")

    narracao = os.path.join(RAIZ, "out", f"{slug}_narracao.wav")
    subprocess.run([sys.executable, os.path.join(RAIZ, "juntar_blocos.py"), narracao, *blocos], check=True, cwd=RAIZ)

    video = os.path.join(RAIZ, "out", f"{slug}.mp4")
    log("renderizando (pode levar de 15 a 40 min)")
    t0 = time.time()
    subprocess.run([sys.executable, os.path.join(RAIZ, "render.py"), "build", cenas, narracao, video], check=True, cwd=RAIZ)
    log(f"render pronto em {(time.time() - t0) / 60:.1f} min")

    dv, dn = duracao(video), duracao(narracao)
    if abs(dv - dn) > 2:
        raise SystemExit(f"o vídeo ({dv:.1f}s) não bate com a narração ({dn:.1f}s)")
    log(f"vídeo: {dv / 60:.1f} min, {os.path.getsize(video) // 1024 // 1024} MB")
    return video


def youtube():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    faltando = [k for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN") if not os.environ.get(k)]
    if faltando:
        raise SystemExit(f"faltam os secrets {faltando} (veja automacao/README.md)")
    cred = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], token_uri="https://oauth2.googleapis.com/token",
                       client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"],
                       scopes=["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"])
    return build("youtube", "v3", credentials=cred, cache_discovery=False)


def thumb_jpeg(path):
    """o YouTube aceita até 2 MB; converte para JPEG 1280x720 se precisar"""
    if os.path.getsize(path) <= 2_000_000:
        return path
    saida = os.path.splitext(path)[0] + "_yt.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", "scale=1280:720", "-q:v", "3", saida], check=True)
    return saida


def subir(yt, arquivo, titulo, descricao, tags, quando, categoria="27"):
    """envia um vídeo agendado (privado até publishAt) e devolve a resposta da API"""
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    corpo = {
        "snippet": {
            "title": limpar_texto(titulo, 100),
            "description": limpar_texto(descricao, 5000),
            "tags": limpar_tags(tags),
            "categoryId": str(categoria),
            "defaultLanguage": "pt-BR",
            "defaultAudioLanguage": "pt-BR",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": quando.isoformat().replace("+00:00", "Z"),
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,  # narração com voz de IA
            "embeddable": True,
        },
    }
    media = MediaFileUpload(arquivo, mimetype="video/mp4", chunksize=16 * 1024 * 1024, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=corpo, media_body=media, notifySubscribers=True)
    resp, tentativa = None, 0
    while resp is None:
        try:
            status, resp = req.next_chunk()
            if status:
                log(f"enviando {os.path.basename(arquivo)}: {int(status.progress() * 100)}%")
        except HttpError as e:
            if e.resp.status in (500, 502, 503, 504) and tentativa < 6:
                tentativa += 1
                time.sleep(2 ** tentativa)
                continue
            raise
    return resp


def travado(resp):
    st = resp.get("status", {})
    return st.get("privacyStatus") == "private" and not st.get("publishAt")


def enviar(m, video, yt):
    from googleapiclient.http import MediaFileUpload

    quando = horario(m)
    resp = subir(yt, video, m["titulo"], m["descricao"], m.get("tags"), quando, m.get("categoria", "27"))
    vid = resp["id"]
    log(f"enviado: https://youtu.be/{vid}  (publica em {quando.astimezone(FUSO).isoformat()})")

    avisos = []
    if travado(resp):
        avisos.append("o YouTube travou o vídeo como privado (projeto não verificado?): publique à mão no Studio")

    if m.get("thumbnail"):
        tp = os.path.join(RAIZ, m["thumbnail"])
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(thumb_jpeg(tp))).execute()
            log("thumbnail definida")
        except Exception as e:  # noqa: BLE001
            avisos.append(f"thumbnail não foi aceita ({e}). Canal precisa estar verificado por telefone para thumbnail personalizada.")

    if m.get("playlist"):
        try:
            yt.playlistItems().insert(part="snippet", body={"snippet": {
                "playlistId": m["playlist"], "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
        except Exception as e:  # noqa: BLE001
            avisos.append(f"não entrou na playlist: {e}")

    for a in avisos:
        log("AVISO:", a)
    return vid, quando, avisos


# ------------------------------------------------------------------ Shorts
SHORT_HORA = 12          # horário dos Shorts (Brasília)
SHORT_MAX = 3            # cortes por vídeo longo
SHORT_LIMITE = 179.0     # o YouTube só trata como Short até 3 min


def dias_ocupados():
    """datas (Brasília) que já têm Short agendado, lidas de fila/publicados/"""
    ocupados = set()
    pasta = os.path.join(RAIZ, "fila", "publicados")
    for nome in os.listdir(pasta) if os.path.isdir(pasta) else []:
        if not nome.endswith(".json"):
            continue
        try:
            with open(os.path.join(pasta, nome), encoding="utf-8") as f:
                for s in json.load(f).get("shorts", []):
                    ocupados.add(dt.datetime.fromisoformat(s["agendado_para"]).astimezone(FUSO).date())
        except Exception:  # noqa: BLE001
            continue
    return ocupados


def horarios_shorts(quando_longo, n, ocupados=None):
    """um Short por dia às 12h, a partir do dia seguinte ao vídeo longo, pulando dias que já têm Short.
    Com o longo na terça e na quinta: cortes de terça em qua/qui/sex, cortes de quinta em sáb/dom/seg."""
    ocupados = set(ocupados if ocupados is not None else dias_ocupados())
    dia = quando_longo.astimezone(FUSO).date() + dt.timedelta(days=1)
    minimo = dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=FOLGA_MIN)
    saida = []
    while len(saida) < n:
        alvo = dt.datetime(dia.year, dia.month, dia.day, SHORT_HORA, tzinfo=FUSO)
        if dia not in ocupados and alvo > minimo:
            saida.append(alvo.astimezone(dt.timezone.utc))
            ocupados.add(dia)
        dia += dt.timedelta(days=1)
    return saida


def renderizar_cortes(m, video):
    """roda o cortes.py com o áudio dos ganchos (se houver) e devolve [(corte, mp4)]"""
    slug = m["slug"]
    cj = os.path.join(RAIZ, "videos", slug, "cortes.json")
    with open(cj, encoding="utf-8") as f:
        cortes = json.load(f)["cortes"][:SHORT_MAX]
    cmd = [sys.executable, os.path.join(RAIZ, "cortes.py"), os.path.join("videos", slug), video]
    if m.get("ganchos_audio"):
        url = m["ganchos_audio"]
        destino = os.path.join(RAIZ, "out", slug, "ganchos" + (os.path.splitext(url.split("?")[0])[1] or ".wav"))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        log("baixando o bloco de ganchos")
        baixar(url, destino)
        if m.get("ganchos_duracao") and abs(duracao(destino) - m["ganchos_duracao"]) > 0.6:
            raise RuntimeError("a duração do bloco de ganchos não bate com o ganchos.txt")
        cmd += ["--ganchos", destino]
    log(f"renderizando {len(cortes)} cortes verticais")
    t0 = time.time()
    for c in cortes:
        subprocess.run(cmd + ["--so", c["id"]], check=True, cwd=RAIZ)
    log(f"cortes prontos em {(time.time() - t0) / 60:.1f} min")
    return [(c, os.path.join(RAIZ, "out", f"{slug}_corte_{c['id']}.mp4")) for c in cortes]


def enviar_shorts(m, video, yt, vid_longo, quando_longo):
    shorts, avisos = [], []
    if m.get("shorts") is False:
        return shorts, avisos
    if not os.path.exists(os.path.join(RAIZ, "videos", m["slug"], "cortes.json")):
        avisos.append("sem cortes.json: nenhum Short foi gerado")
        return shorts, avisos
    try:
        prontos = renderizar_cortes(m, video)
    except Exception as e:  # noqa: BLE001
        avisos.append(f"os cortes não foram gerados ({e}); o vídeo longo seguiu normal")
        return shorts, avisos

    validos = []
    for c, mp4 in prontos:
        if not os.path.exists(mp4):
            avisos.append(f"corte {c['id']} não foi gerado")
            continue
        d = duracao(mp4)
        if d > SHORT_LIMITE:
            avisos.append(f"corte {c['id']} tem {d:.0f}s (acima de 3 min, não vira Short): ficou de fora")
            continue
        validos.append((c, mp4, d))

    for (c, mp4, d), quando in zip(validos, horarios_shorts(quando_longo, len(validos))):
        titulo = c.get("titulo_post") or c.get("titulo", "").replace("\\N", " ").title()
        if "#shorts" not in titulo.lower() and len(titulo) <= 91:
            titulo += " #Shorts"
        descricao = (f"{c.get('post', '').strip()}\n\nHistória completa: https://youtu.be/{vid_longo}\n\n"
                     "Narração gerada com voz de IA.")
        try:
            resp = subir(yt, mp4, titulo, descricao, m.get("tags"), quando, m.get("categoria", "27"))
        except Exception as e:  # noqa: BLE001
            avisos.append(f"Short {c['id']} não foi enviado: {e}")
            continue
        sid = resp["id"]
        log(f"Short {c['id']} ({d:.0f}s): https://youtu.be/{sid}  (publica em {quando.astimezone(FUSO):%d/%m %H:%M})")
        if travado(resp):
            avisos.append(f"o YouTube travou o Short {c['id']} como privado: publique à mão no Studio")
        shorts.append({"id": c["id"], "video_id": sid, "url": f"https://youtu.be/{sid}", "titulo": titulo,
                       "duracao": round(d, 1), "agendado_para": quando.astimezone(FUSO).isoformat()})
    for a in avisos:
        log("AVISO:", a)
    return shorts, avisos


def registrar(caminho, m, vid, quando, avisos, shorts=()):
    """tira o vídeo da fila e guarda em fila/publicados/ (o workflow faz o commit)"""
    destino_dir = os.path.join(RAIZ, "fila", "publicados")
    os.makedirs(destino_dir, exist_ok=True)
    m = dict(m)
    m.pop("audio_blocos", None)  # links temporários, não precisam ficar no histórico
    m.pop("ganchos_audio", None)
    m.update({
        "video_id": vid,
        "url": f"https://youtu.be/{vid}",
        "agendado_para": quando.astimezone(FUSO).isoformat(),
        "enviado_em": dt.datetime.now(FUSO).replace(microsecond=0).isoformat(),
        "avisos": avisos,
        "shorts": list(shorts),
    })
    with open(os.path.join(destino_dir, os.path.basename(caminho)), "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.remove(caminho)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fila", nargs="?")
    ap.add_argument("--sem-upload", action="store_true")
    ap.add_argument("--audio", nargs="+")
    ap.add_argument("--testar-credenciais", action="store_true")
    a = ap.parse_args()

    if a.testar_credenciais:
        r = youtube().channels().list(part="snippet", mine=True).execute()
        nomes = [c["snippet"]["title"] for c in r.get("items", [])]
        log("credenciais ok. Canal:", ", ".join(nomes) or "(nenhum canal encontrado)")
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
                f.write(f"### Credenciais ok\n\nCanal: **{', '.join(nomes) or 'nenhum'}**\n")
        return
    if not a.fila:
        ap.error("informe o arquivo da fila")

    with open(a.fila, encoding="utf-8") as f:
        m = json.load(f)
    cenas = validar(m)
    video = produzir(m, cenas, a.audio)
    if a.sem_upload:
        log("modo teste: sem upload", video)
        return
    yt = youtube()
    if m.get("video_id"):
        # o vídeo longo já foi enviado numa execução anterior: só registra e faz os Shorts
        vid, quando, avisos = m["video_id"], horario(m), ["vídeo longo já tinha sido enviado; esta execução só fez os Shorts"]
        log(f"vídeo longo já enviado: https://youtu.be/{vid}")
    else:
        vid, quando, avisos = enviar(m, video, yt)
    # o vídeo longo já subiu: registra antes dos Shorts, para nunca reenviar o longo se algo falhar depois
    registrar(a.fila, m, vid, quando, avisos)
    caminho_pub = os.path.join(RAIZ, "fila", "publicados", os.path.basename(a.fila))
    shorts, avisos_s = enviar_shorts(m, video, yt, vid, quando)
    with open(caminho_pub, encoding="utf-8") as f:
        reg = json.load(f)
    reg["shorts"], reg["avisos"] = shorts, avisos + avisos_s
    with open(caminho_pub, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
        f.write("\n")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(f"### {m['titulo']}\n\nhttps://youtu.be/{vid}\n\nAgendado para {quando.astimezone(FUSO):%d/%m %H:%M}\n\n")
            for sh in shorts:
                f.write(f"- Short **{sh['titulo']}**: {sh['url']} ({sh['agendado_para'][8:10]}/{sh['agendado_para'][5:7]} às {SHORT_HORA}h)\n")
            for av in avisos + avisos_s:
                f.write(f"- ⚠️ {av}\n")


if __name__ == "__main__":
    main()
