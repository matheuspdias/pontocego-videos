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


def enviar(m, video):
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    yt = youtube()
    quando = horario(m)
    corpo = {
        "snippet": {
            "title": limpar_texto(m["titulo"], 100),
            "description": limpar_texto(m["descricao"], 5000),
            "tags": limpar_tags(m.get("tags")),
            "categoryId": str(m.get("categoria", "27")),
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
    media = MediaFileUpload(video, mimetype="video/mp4", chunksize=16 * 1024 * 1024, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=corpo, media_body=media, notifySubscribers=True)
    resp, tentativa = None, 0
    while resp is None:
        try:
            status, resp = req.next_chunk()
            if status:
                log(f"enviando: {int(status.progress() * 100)}%")
        except HttpError as e:
            if e.resp.status in (500, 502, 503, 504) and tentativa < 6:
                tentativa += 1
                time.sleep(2 ** tentativa)
                continue
            raise
    vid = resp["id"]
    log(f"enviado: https://youtu.be/{vid}  (publica em {quando.astimezone(FUSO).isoformat()})")

    avisos = []
    if resp.get("status", {}).get("privacyStatus") == "private" and not resp.get("status", {}).get("publishAt"):
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


def registrar(caminho, m, vid, quando, avisos):
    """tira o vídeo da fila e guarda em fila/publicados/ (o workflow faz o commit)"""
    destino_dir = os.path.join(RAIZ, "fila", "publicados")
    os.makedirs(destino_dir, exist_ok=True)
    m = dict(m)
    m.pop("audio_blocos", None)  # links temporários, não precisam ficar no histórico
    m.update({
        "video_id": vid,
        "url": f"https://youtu.be/{vid}",
        "agendado_para": quando.astimezone(FUSO).isoformat(),
        "enviado_em": dt.datetime.now(FUSO).replace(microsecond=0).isoformat(),
        "avisos": avisos,
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
    vid, quando, avisos = enviar(m, video)
    registrar(a.fila, m, vid, quando, avisos)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(f"### {m['titulo']}\n\nhttps://youtu.be/{vid}\n\nAgendado para {quando.astimezone(FUSO):%d/%m %H:%M}\n\n")
            for av in avisos:
                f.write(f"- ⚠️ {av}\n")


if __name__ == "__main__":
    main()
