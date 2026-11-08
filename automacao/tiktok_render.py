"""
Produtor dos TikToks automáticos do Ponto Cego (roda no GitHub Actions, workflow "TikTok automático").
Vídeos curtos NATIVOS (roteiro próprio, não cortes do vídeo longo); o enquadramento vertical é o do tiktok.py.

Pega um vídeo de fila_tiktok/<slug>.json, baixa a narração do HeyGen, junta, renderiza o vertical,
queima as legendas, gera a capa e publica tudo numa release "tiktok-<slug>" do GitHub:
    <slug>_tiktok.mp4   vídeo final (1080x1920: cena 16:9 no meio, título no topo, legendas palavra por palavra)
    <slug>_capa.png     capa
    <slug>_post.txt     legenda do post, título do Shorts e lembretes
A tarefa agendada baixa esses arquivos da release e entrega ao Matheus no chat. Ele posta à mão.

    python automacao/tiktok_render.py fila_tiktok/<slug>.json
    python automacao/tiktok_render.py fila_tiktok/<slug>.json --sem-release   # teste: só renderiza

Formato do fila_tiktok/<slug>.json (o modo automático escreve; veja automacao/AUTOMATICO_TIKTOK.md):
{
  "slug": "cartao-rotativo",
  "data": "2026-11-08",          # dia em que o Matheus vai postar
  "horario": "10:00",            # "10:00" ou "18:00"
  "titulo": "O que ninguém te conta antes de entrar no rotativo",
  "audio_blocos": ["https://resource2.heygen.ai/...wav"],
  "duracoes": [74.2]
}
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "automacao"))
from publicar import baixar, duracao, log  # noqa: E402

REPO = os.environ.get("GITHUB_REPOSITORY", "matheuspdias/pontocego-videos")


def run(*cmd):
    subprocess.run([str(c) for c in cmd], check=True, cwd=RAIZ)


def produzir(m, audios_locais=None):
    slug = m["slug"]
    vdir = os.path.join(RAIZ, "videos", slug)
    for f in ("scenes.py", "palavras.json", "tiktok.json", "post.txt"):
        if not os.path.exists(os.path.join(vdir, f)):
            raise SystemExit(f"falta videos/{slug}/{f}")
    pasta = os.path.join(RAIZ, "out", slug)
    os.makedirs(pasta, exist_ok=True)

    blocos = list(audios_locais or [])
    for i, url in enumerate([] if audios_locais else m["audio_blocos"], 1):
        ext = os.path.splitext(url.split("?")[0])[1] or ".wav"
        destino = os.path.join(pasta, f"bloco{i}{ext}")
        log(f"baixando bloco {i}/{len(m['audio_blocos'])}")
        baixar(url, destino)
        blocos.append(destino)
    for i, b in enumerate(blocos):
        d = duracao(b)
        esp = (m.get("duracoes") or [None] * len(blocos))[i]
        log(f"bloco {i + 1}: {d:.2f}s" + (f" (esperado {esp:.2f}s)" if esp else ""))
        if esp and abs(d - esp) > 0.6:
            raise SystemExit("a duração do áudio não bate com a usada nas cenas: o vídeo sairia fora de sincronia")

    narracao = os.path.join(RAIZ, "out", f"{slug}_narracao.wav")
    run(sys.executable, "juntar_blocos.py", narracao, *blocos)
    base = os.path.join(RAIZ, "out", f"{slug}_base.mp4")
    final = os.path.join(RAIZ, "out", f"{slug}_tiktok.mp4")
    log("renderizando o vertical")
    run(sys.executable, "render.py", "build", f"videos/{slug}/scenes.py", narracao, base)
    capa = os.path.join(RAIZ, "out", f"{slug}_capa.png")
    run(sys.executable, "tiktok.py", f"videos/{slug}", base, final, "--capa", capa)
    dv, dn = duracao(final), duracao(narracao)
    if abs(dv - dn) > 1.5:
        raise SystemExit(f"o vídeo ({dv:.1f}s) não bate com a narração ({dn:.1f}s)")

    post = os.path.join(RAIZ, "out", f"{slug}_post.txt")
    shutil.copy(os.path.join(vdir, "post.txt"), post)
    log(f"pronto: {dv:.1f}s, {os.path.getsize(final) / 1e6:.1f} MB")
    return final, capa, post


def publicar_release(m, arquivos):
    tag = f"tiktok-{m['slug']}"
    titulo = f"TikTok {m.get('data', '')} {m.get('horario', '')} · {m.get('titulo', m['slug'])}".strip()
    notas = open(arquivos[-1], encoding="utf-8").read()
    subprocess.run(["gh", "release", "delete", tag, "-R", REPO, "-y", "--cleanup-tag"], cwd=RAIZ)  # refazer, se existir
    run("gh", "release", "create", tag, *arquivos, "-R", REPO, "--title", titulo, "--notes", notas[:120000])
    return f"https://github.com/{REPO}/releases/tag/{tag}"


def registrar(caminho, m, url):
    dest = os.path.join(RAIZ, "fila_tiktok", "feitos")
    os.makedirs(dest, exist_ok=True)
    m = dict(m)
    m.pop("audio_blocos", None)
    m["release"] = url
    with open(os.path.join(dest, os.path.basename(caminho)), "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)
    os.remove(caminho)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fila")
    ap.add_argument("--sem-release", action="store_true")
    ap.add_argument("--audio", nargs="+", help="teste: usa áudios locais em vez de baixar do HeyGen")
    a = ap.parse_args()
    m = json.load(open(a.fila, encoding="utf-8"))
    for k in ("slug", "data", "horario", "audio_blocos"):
        if not m.get(k):
            raise SystemExit(f"fila_tiktok: falta o campo {k}")
    arquivos = produzir(m, a.audio)
    if a.sem_release:
        return
    url = publicar_release(m, list(arquivos))
    log(f"release: {url}")
    registrar(a.fila, m, url)


if __name__ == "__main__":
    main()
