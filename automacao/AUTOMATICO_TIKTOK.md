# Modo automático do TikTok do Ponto Cego

Roteiro da tarefa agendada **"Ponto Cego TikTok automático"**, que roda todo dia por volta das **19h** e deixa prontos os **2 vídeos curtos do dia seguinte** (o Matheus revisa à noite e posta à mão às **12h** e às **20h**).
Decisão de 07/11/2026: no TikTok o Ponto Cego usa **vídeos curtos nativos** (roteiro escrito só para o TikTok), não cortes do vídeo longo. Os cortes continuam indo para o YouTube Shorts pelo publicador do vídeo longo.
O Matheus não acompanha a produção: ninguém responde perguntas. Nunca tente postar (o agendamento do TikTok trava as views).

Siga a skill `pontocego-video` (ou `README.md` + `VOZ.md` deste repo) para pesquisa, voz e estilo ilustrado, com as diferenças abaixo. Onde conflitarem, vale este arquivo.

## Como o vídeo chega ao Matheus

```
tarefa agendada (Claude)                         GitHub Actions (.github/workflows/tiktok.yml)
temas, pesquisa, roteiros, narração no HeyGen,   baixa a narração, renderiza a cena 16:9, monta o
cenas (16:9), prévias, tiktok.json, post.txt,    vertical com o tiktok.py (título, cena, legendas),
commit de fila_tiktok/<slug>.json + push   -->   gera a capa e publica a release "tiktok-<slug>"
        |                                                         |
        +---- espera a release, baixa os arquivos e manda no chat <+
```
O ambiente da tarefa **não baixa** o áudio do HeyGen (quem baixa é o Actions), mas baixa da release (repositório público):
`curl -sSL -o <arquivo> https://github.com/matheuspdias/pontocego-videos/releases/download/tiktok-<slug>/<arquivo>`.

## Regras
- **Nunca pare para perguntar.** Decida e anote na mensagem final.
- **Erro do HeyGen** (créditos, timeout): não tente de novo. Entregue o que der (se um dos dois saiu, entregue esse) e avise.
- Prefira **não entregar** a entregar com fato errado, legenda errada ou cena vazia.
- Entregue o quanto antes (o ideal é até umas **21h**). Limite absoluto: **11h30** do dia da postagem. Entregue primeiro o das 12h e depois o das 20h.
- Se o Matheus responder pedindo ajuste numa cena, corrija o `scenes.py`, rode o workflow de novo para aquele slug (aba Actions, `workflow_dispatch` com o slug, ou recoloque o JSON em `fila_tiktok/`) e reenvie.

## Passo a passo

### 1. Data e checagem
1. Data alvo (horário de Brasília): se a execução começou depois das 11h30, é **amanhã** (caso normal, rodando às 19h); antes disso, **hoje**.
2. Veja `fila_tiktok/` e `fila_tiktok/feitos/` (campos `data` e `horario`). Para cada horário (12:00 e 20:00) da data alvo:
   - já existe em `feitos/` com `release`: só baixe e entregue de novo (passo 8), sem produzir;
   - está em `fila_tiktok/` (Actions rodando ou falhou): veja `fila_tiktok/ultimo_log.txt`; espere ou explique o erro;
   - não existe: produza.

### 2. Temas (2 por dia)
- Leia `automacao/temas_tiktok.md` (Fila do Matheus primeiro, depois as ideias) e `automacao/temas.md` (casos do YouTube).
- Dois casos diferentes e **dois formatos diferentes** no dia (lista de formatos no `temas_tiktok.md`). Varie época, lugar e tom; de vez em quando um caso brasileiro.
- Não repita caso de "Já feitos". Respeite "Não fazer". Acrescente os dois em "Já feitos" com o slug e o formato.

### 3. Pesquisa e roteiro
- Pesquise na web e confira datas, nomes e números em fontes confiáveis. Separe mito de fato (isso costuma ser a melhor virada).
- **60 a 80 s** (~170 a 220 palavras): gancho no 1º segundo (data + fato estranho, nada de "neste vídeo"), frases curtas, uma revelação perto do fim e **pergunta de teoria** no fechamento.
- Tags do ElevenLabs v4 (`[mysterious]`, `[serious]`, `[thoughtful]`, `[curious]`, `[short pause]`), **sem `[whispers]`**, números por extenso. Nomes estrangeiros difíceis: escreva como se pronuncia no texto do HeyGen e use a grafia certa nas legendas.
- Salve `videos/<slug>/roteiro.txt` com as fontes.

### 4. Narração
- Um bloco por vídeo no HeyGen (`create_speech_without_player`), voz oficial (VOZ.md: Pedro Lima - Serious, ElevenLabs v4, pt, 1.0). Gere os dois em paralelo.
- Guarde o link, a duração e os `word_timestamps` → `videos/<slug>/palavras.json` (`[{"w", "t0", "t1"}]`), **sem** `<start>`, `<end>` e sem as tags `[...]`, corrigindo a grafia das palavras escritas "como se pronuncia".

### 5. Cenas, tiktok.json e post
- `videos/<slug>/scenes.py` **em 16:9**, estilo ilustrado (`STYLE = "ilustrado"`, `TOM`, `THEME`, `SFX_OFF = True` e 4 a 6 toques em `SFX` com nomes do `sfx.py`). Modelos: `videos/flannan-isles/` e `videos/homem-de-somerton/`.
- O `tiktok.py` coloca a cena no meio do quadro vertical (aparece a ~56%): **letras grandes** (títulos 90-130, placas 54-70), nada importante fora de x 140-1780, algo novo na tela a cada 2-3 s, o Historiador reagindo em quase todas as cenas. O título fixo do topo e as legendas vêm de fora (não repita na cena).
- Nada de corpo, sangue ou violência explícita: sugira com objetos.
- Revisão obrigatória: `python render.py sheet ...` (pelo menos duas rodadas) e um teste completo mudo: `python render.py build videos/<slug>/scenes.py silent:<duração> out/b.mp4 && python tiktok.py videos/<slug> out/b.mp4 out/t.mp4 --capa out/c.png`; confira 3 ou 4 quadros e a capa.
- `videos/<slug>/tiktok.json`: `titulo` (topo, até ~22 caracteres), `card` (normalmente `""`: a pergunta final já é o CTA), `capa` (1ª linha grande + 2 ou 3 linhas), `capa_t` (segundo da cena da capa).
- `videos/<slug>/post.txt`: legenda (gancho na 1ª linha, 3 ou 4 linhas, pergunta de teoria, 3 a 5 hashtags como #misterio #historia #pontocego) e título do Shorts.

### 6. Fila
`fila_tiktok/<slug>.json`:
```json
{"slug": "<slug>", "data": "2026-11-09", "horario": "12:00", "titulo": "<título curto>",
 "audio_blocos": ["<link do HeyGen>"], "duracoes": [70.2]}
```
Valide com `python -m json.tool`.

### 7. Commit e push
Commit de `videos/<slug>/`, `automacao/temas_tiktok.md`, melhorias do `ilustrado.py` e `fila_tiktok/*.json` na `main` e push (se recusar: `git pull --rebase` e push). O push dispara o workflow "TikTok automático" (~5 a 10 min por vídeo).

### 8. Esperar, baixar e entregar
- A cada 60 s, por até 50 min: `curl -s -o /dev/null -w '%{http_code}' https://api.github.com/repos/matheuspdias/pontocego-videos/releases/tags/tiktok-<slug>`. Se o workflow falhar, `git pull` e leia `fila_tiktok/ultimo_log.txt`, corrija e faça push de novo.
- Baixe `<slug>_tiktok.mp4`, `<slug>_capa.png` e `<slug>_post.txt`, confira 2 ou 3 quadros.
- **SendUserFile** (status `proactive`): vídeo e capa das 12h, depois os das 20h.
- **SendUserMessage** curto: data de postagem; para cada vídeo, título e legenda pronta para copiar; lembrete do selo de IA (voz) e de postar à mão; decisões tomadas sozinho (caso, formato, fontes) ou problemas; e que ele pode pedir ajuste respondendo na conversa.
