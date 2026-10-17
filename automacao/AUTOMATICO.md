# Modo automático do Ponto Cego

Este é o roteiro que a **tarefa agendada** segue toda segunda e quarta à noite para deixar pronto o vídeo de terça e de quinta (18h).
O Matheus está cuidando do outro canal e **não vai acompanhar**: ninguém responde perguntas durante a execução.

Siga a skill `pontocego-video` (ou o `README.md` + `VOZ.md` deste repo) com as diferenças abaixo. Onde as duas conflitarem, vale este arquivo.

## Como o vídeo chega ao YouTube

```
tarefa agendada (Claude)                     GitHub Actions (.github/workflows/publicar.yml)
pesquisa, roteiro, narração no HeyGen,  -->  baixa os áudios do HeyGen, junta os blocos,
cenas, prévias, thumbnail, textos,           renderiza o MP4, envia ao YouTube agendado
commit de fila/<slug>.json + push            para as 18h e move a fila para fila/publicados/
```

O ambiente da tarefa **não consegue baixar** os áudios do HeyGen. Não tente, e não peça ao Matheus: quem baixa é o GitHub Actions.

## Regras do modo automático

- **Nunca pare para perguntar.** Tome a decisão mais razoável e anote no resumo final.
- **Erro do HeyGen** (créditos, timeout, recusa): não tente de novo nem gere a narração por outro caminho. Não coloque nada na fila. Mande o resumo com o erro e pare.
- Se faltar algo para o vídeo ficar bom, prefira **não publicar** (não criar `fila/<slug>.json`) a publicar algo quebrado. Nesse caso, faça commit do que existe em `videos/<slug>/` e explique no resumo.
- Pule os **cortes verticais** e o **bloco de ganchos** (o Matheus decidiu não automatizar o TikTok). Isso economiza créditos do HeyGen.

## Passo a passo

### 1. Data e tema
1. Data alvo: o próximo dia de postagem (**terça ou quinta, 18:00, horário de Brasília**) depois de hoje. Se já houver um vídeo para essa data em `fila/` ou `fila/publicados/` (campo `publicar_em`), pare: não é para gerar dois.
2. Leia `automacao/temas.md`, liste `videos/` e os títulos em `fila/publicados/`. **Não repita** história já feita.
3. Escolha uma história forte, com fatos verificáveis e um mistério real. Use a seção "Ideias" se houver algo lá. Varie em relação aos dois últimos vídeos:
   - o **tipo** (desaparecimento, expedição perdida, enigma arqueológico, fenômeno sem explicação, caso histórico, documento ou objeto misterioso, formato lista "5 mistérios");
   - o **tema visual** (`THEME`): não use o mesmo dos dois últimos se der.
   - De vez em quando (1 a cada 4 ou 5), um caso brasileiro.
4. Acrescente o tema em "Já feitos" no `temas.md`.

### 2. Pesquisa e roteiro
- Pesquise na web e confira datas, nomes e números. Separe mito de fato. Nada de acusar pessoas reais ou povos.
- 12 a 15 min (~1.900 a 2.200 palavras), estrutura e fechamento da skill, tags do ElevenLabs v4, **sem `[whispers]`**, números por extenso.
- Salve `videos/<slug>/roteiro.txt`.

### 3. Narração
- `create_speech` com a voz oficial (VOZ.md), um bloco por chamada, até ~4.500 caracteres, em paralelo.
- De cada resposta guarde: o **link do áudio**, a **duração** (`duration`) e os `word_timestamps`.
- `narracao_blocos.txt` e `transcricao.txt` como na skill. Offset de cada bloco = soma das durações anteriores + 1,0 s por bloco (é exatamente o que o `juntar_blocos.py` faz no Actions).

### 4. Cenas e revisão
- `videos/<slug>/scenes.py` com `THEME = "<tema>"`, `SFX_OFF = True` e 10 a 15 toques em `SFX`.
- A revisão das prévias é **obrigatória e é só sua**: `python render.py sheet ...` com tempos no fim e no meio de todas as cenas. Olhe cada grade, corrija sobreposições, textos cortados, telas vazias e elementos escuros demais, e gere de novo até ficar limpo. Pelo menos duas rodadas.
- Confira que o `scenes.py` carrega sem erro e que a última cena termina em `999.0`.
- Um teste mudo curto pega erro de código: `python render.py build videos/<slug>/scenes.py silent:20 out/teste.mp4`.

### 5. Thumbnail e textos
- Duas thumbnails (`videos/<slug>/thumb/thumb.py`), escolha a melhor.
- `videos/<slug>/youtube.txt` no formato dos vídeos anteriores (título, alternativas, descrição com capítulos pelos tempos reais das cenas, tags). Mantenha a linha "Narração gerada com voz de IA."

### 6. Colocar na fila
Escreva `fila/<slug>.json`:

```json
{
  "slug": "<slug>",
  "publicar_em": "2026-10-20T18:00:00-03:00",
  "audio_blocos": ["<link do bloco 1>", "<link do bloco 2>"],
  "duracoes": [107.886, 101.329],
  "titulo": "<título escolhido>",
  "descricao": "<descrição completa com capítulos e hashtags>",
  "tags": ["tag 1", "tag 2"],
  "thumbnail": "videos/<slug>/thumb/<arquivo escolhido>.png",
  "categoria": "27"
}
```

- `audio_blocos` e `duracoes` na **mesma ordem** dos blocos. O publicador confere cada duração e recusa se não bater (o vídeo sairia fora de sincronia).
- Valide o JSON (`python -m json.tool fila/<slug>.json`).

### 7. Commit e push
- Commit de `videos/<slug>/` (sem áudio), `automacao/temas.md` e `fila/<slug>.json` na `main`, e push. Se recusar por mudança de outra sessão: `git pull --rebase` e push de novo.
- O push dispara o workflow "Publicar no YouTube". Daqui em diante é com ele (leva ~30 a 60 min).

### 8. Resumo final (SendUserMessage)
Curto, em português:
- título, história e tema visual escolhidos, e duração;
- quando vai ao ar (dia e 18h);
- como vetar: até o horário, no YouTube Studio > Conteúdo, o vídeo aparece como "Programado"; dá para editar, deixar privado ou excluir;
- qualquer decisão tomada sozinho ou problema encontrado.
