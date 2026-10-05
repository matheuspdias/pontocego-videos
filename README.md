# pontocego-videos

Motor de vídeos do canal **Ponto Cego**, sobre histórias e mistérios antigos e atuais (Biblioteca de Alexandria, Passo Dyatlov, MH370...).
O estilo é **sombrio desenhado**: fundo noturno, traço de giz, vinheta, névoa, poeira, neve e luz de lanterna, com o narrador fixo **O Historiador**.

Entrada: **transcrição com tempos** + **áudio da narração**. Saída: **MP4 1920x1080** (~20 MB a cada 4 min).

## Instalação
```bash
./setup.sh   # pycairo, numpy e fontes (Cinzel, Special Elite, Patrick Hand). Requer ffmpeg.
```

## Fluxo de trabalho
1. Crie `videos/<slug>/` e coloque nela `transcricao.txt` (formato `(m:ss) frase...`).
2. Divida a narração em cenas de ~4 a 20 s. Vídeos de mistério pedem ritmo mais lento e atmosférico que vídeos explicativos.
3. Escreva `videos/<slug>/scenes.py` (modelo: `examples/dyatlov-demo/scenes.py`). Use uma função `sNN(c, t)` por cena, em **tempo absoluto do áudio**, e termine com
   `SCENES = [(inicio, fim, funcao), ...]`, onde a última cena termina em `999.0`.
4. Gere as prévias: `python render.py sheet videos/<slug>/scenes.py out/preview.png t1 t2 ...`
5. Gere o vídeo final: `python render.py build videos/<slug>/scenes.py audio.mp3 out/<slug>.mp4`
   (prévia muda: `silent:30` no lugar do áudio).

## Identidade visual
- **Narrador fixo**: `historiador(c, t, x, y_pes, escala, poses, exprs, look=...)`. Usa chapéu fedora, sobretudo marrom, óculos redondos e lanterna acesa na mão esquerda. A lanterna some quando a mão esquerda sobe.
  Ele aparece em quase toda cena, no canto esquerdo (x≈300-400, pés em y≈1000-1010, escala ~1.0), reagindo à narração.
- **Outros personagens**: `hiker` (gorro + casaco, cor por pessoa), `scholar` (túnica + capuz, para a antiguidade) e `person` (genérico).
- **Fontes**: `SERIF` (Cinzel, títulos antigos), `TYPE` (Special Elite, datas, documentos, legendas) e `HAND` (rótulos pequenos).
- **Cores**: `INK` (giz creme, traço padrão), `AMBER` (luz, destaque), `RED`/`BLOOD` (perigo, carimbos), `ICE` (frio), `PARCH` (pergaminho), `DARKTXT` (texto sobre pergaminho).
- Não use os glifos `≠ ≈ → ↓ ✓`, porque as fontes não têm.

## Identidade fixa x tema do vídeo
**Fixo em todo vídeo (marca do canal):** o Historiador, a voz do Pedro Lima, o traço de giz sobre fundo escuro, as fontes, o âmbar como destaque, a frase de encerramento, o cartão final "PONTO CEGO" e a **ventania como assinatura** (cheia nos primeiros e nos últimos ~25 s).

**Muda por vídeo (cenário):** declare no topo do `scenes.py`, por exemplo `THEME = "selva"`. O tema ajusta sozinho:
| Tema | Use em | Fundo / névoa | Ventania no meio | Grave |
| --- | --- | --- | --- | --- |
| `classico` (padrão) | temas sem cenário forte, antiguidade | azul-noite / creme | cheia | 55 Hz |
| `selva` | Amazônia, florestas | verde-escuro / verde | baixa (30%) | 49 Hz |
| `mar` | navios, oceano, ilhas | azul-marinho / azul | baixa (35%) | 46 Hz com ondulação lenta |
| `neve` | montanha, gelo, Dyatlov | azul-gelo / branco | cheia | 55 Hz |
| `deserto` | Egito, Oriente Médio, ruínas no deserto | ocre / areia | média (55%) | 52 Hz |
| `cidade` | casos urbanos, crimes, prédios | cinza quente / cinza | baixa (25%) | 58 Hz |

`fog(c, t, ...)` já usa a cor da névoa do tema (passe `col=` só para exceções). Sem chuva, ondas ou ruídos novos: o Matheus não gosta de sons de ruído/chiado. Vídeos antigos sem `THEME` continuam iguais (`classico`).
Thumbnails: chame `set_theme("selva")` no `thumb.py` antes de `background(c, t)`.

## Atmosfera (chame dentro da cena)
`stars(c, t)`, `moon(c, r)`, `fog(c, t, y, alpha)`, `snow(c, t, n, vento, alpha)`, `glow(c, x, y, r, cor, a)`, `flames(c, t)`.
O `overlay` (poeira, vinheta e flicker) e o fundo são aplicados automaticamente pelo renderizador.

## Textos
`stitle(c, "TÍTULO", x, y, size, cor, glow_col)`, `typewrite(c, t, t0, "texto", x, y, size)` (máquina de escrever),
`date_stamp(c, "FEVEREIRO DE 1959", size, cor)` (carimbo), `chapter(c, "CAPÍTULO I", "A expedição")`,
`caption_box(c, "fato curto")` (legenda escura), `hl(c, "texto", x, y, size)` (etiqueta de pergaminho), `title(c, t, t0, "texto", y, size)`.

## Objetos
- Mistério: `lantern candle book scroll old_map magnifier compass skull hourglass big_q newspaper folder photo pin evidence_board`
- Cenários: `mountains tent(torn) pine footprints thermometer moon stars temple column lighthouse flames ancient_ship airplane radar`
- Mar e navios (Mary Celeste): `sea(c, t, y, rough)` (mar noturno com ondas), `brigantine(c, t, torn, name)` (veleiro de 2 mastros; `torn` rasga as velas), `lifeboat(people)`, `barrel(empty, label)`, `sextant`, `chronometer(t, wrong)`, `spyglass`, `ship_wheel(t, spin)`, `sword(stains)`, `teacup(t)`, `stove(t)`, `sea_chest`, `folded_clothes`, `pump(broken)`, `sounding_rod`, `hatch`, `waterspout(t)`, `storm_cloud`, `lightning`, `flag("us"|"ensign", t)`, `tombstone(label)`, `nameboard("NOME")`, `coal`, `gavel`, `tree_rings`, `reef(t)`
- Amazônia (Fawcett): `jungle(c, t, y, n, h, col, seed, edge)` (faixa de floresta), `jungle_tree`, `palm`, `river(c, t, y, h)`, `tepui` (planalto de paredões), `dinosaur`, `idol(glow_on, t)` (ídolo de basalto), `horse`, `wood_cross`, `signet_ring`, `theodolite`, `smoke(c, t, x, y, h, a)`, `letter` (carta manuscrita), `oca`, `pot` (cerâmica), `denture`, `bone`, `lectern`, `canoe`, `pyramid`, `volcano(t)`, `ruined_arch`. Mapa: `draw_map(c, proj, SOUTH_AMERICA)` + `BR_BO_BORDER`, `RIVER_XINGU`, `RIVER_AMAZONAS`
- Chapéus extras dos bonecos: `hat="tophat"` (cartola, séc. XIX) e `hat="sailor"` (marinheiro); `hat="pilot"` serve como quepe de capitão
- Herdados do motor explicativo: `car bills coin calendar clock document house bank clipboard check_icon x_icon big_x arrow arrow_draw` etc.

## Animação
`show(c, t, t0, x, y, fn, s=1, anim="pop"|"fade"|"up"|"left"|"right"|"drop"|"stamp", d, t1)`; composição com `sc(fn, *args, s=)`, `group`, `at`, `T(...)`, `S(...)`.
Bonecos: poses `stand relax point_r point_ru point_l point_lu think think_l hips shrug arms_up head thumb finger_up present present_l wave hold run`;
expressões `happy grin neutral worried shocked desperate think confident sad angry`.

Precisa de algo novo (castelo, navio, símbolo)? Crie a função no `engine.py`, centrada em (0,0) e com contorno `INK` de 5-6 px, e documente aqui. Assim o motor cresce a cada vídeo.

## Efeitos sonoros e ambiente
Os efeitos são sintetizados por código (`sfx.py`), sem bancos de som, e entram **automaticamente** no `build`, no estilo sombrio:
- Uma **cama ambiente** (grave contínuo + vento suave) toca baixinho o vídeo inteiro (`AMBIENCE = None` no scenes.py desliga).
- **Teclas de máquina de escrever** em cada letra de `typewrite`, **impacto** grave nos carimbos (`anim="stamp"`), **whoosh escuro** na troca de cena e um tum suave nos `pop`.
- O volume é ajustado sozinho para ficar 12 dB abaixo do pico da narração (`SFX_DB=8 python render.py build ...` deixa mais alto).
- **Preferência do Matheus:** sem som em toda transição e sem som em cada ícone ("fica chato"). Desde o Mary Celeste o padrão é `SFX_OFF = True` (desliga os sons automáticos) + 10 a 15 toques à mão nos momentos-chave, com sons sem chiado (`tum boom heartbeat bell`). Evite `whoosh swish gust`, que são feitos de ruído.
- **Sons dramáticos** vão à mão, nos momentos certos da narração: `SFX = [(t, "boom"), (t, "heartbeat"), (t, "gust"), (t, "impact"), (t, "riser"), (t, "bell")]`.
  Use `boom` na abertura e em revelações, `riser` antes de uma revelação, `heartbeat` no suspense, `gust` em cenas de frio/montanha e `bell` em igrejas/mortes antigas.

## Mapas
`make_proj(lon0, lon1, lat0, lat1)` cria uma projeção lon/lat → tela. `draw_map(c, proj)` desenha o mar noturno com grade e os continentes estilizados de `LAND` (Sudeste Asiático, Índia, África, Arábia, Madagascar, Austrália e o Atlântico Norte: `draw_map(c, proj, ATLANTIC)` com América do Norte, Europa, Ilhas Britânicas e noroeste da África; `azores(c, proj)` desenha os Açores). Adicione regiões novas quando precisar.
Também há `map_point`, `map_label`, `map_path` (rota desenhada até a fração p) e `plane_on_path` (avião seguindo a rota).
Objetos do MH370 que servem para outros vídeos: `satellite ping radio_tower sonar_ship seabed sonar_beam flaperon auv black_box monitor cockpit_door oxygen_mask crowd pilot`.

## Cortes verticais (TikTok, YouTube Shorts, Reels)
Depois do vídeo 16:9 pronto:
```bash
python cortes.py videos/<slug> out/<slug>.mp4 --audio <mp4 com o áudio final> --titulo "LINHA 1\NLINHA 2"
```
- Divide a história em partes de 62 s a 2:50 (o TikTok só paga vídeo com mais de 1 min; o Shorts aceita até 3 min), cortando no início de uma frase e preferindo começo de bloco ou de parágrafo do `roteiro.txt`.
- Cada parte sai em 1080x1920: fundo com o próprio vídeo desfocado, título e "PARTE X DE N" no topo, o vídeo no meio e legendas grandes palavra por palavra (Montserrat ExtraBold, palavra falada em destaque). No fim entra "CONTINUA NA PARTE X" ou, na última, "HISTÓRIA COMPLETA NO YOUTUBE".
- Tempos das palavras: `videos/<slug>/palavras.json` se existir; senão são estimados pelas frases e marcas `[palavra@t]` do `narracao_blocos.txt` (quanto mais marcas, melhor a sincronia).
- Opções: `--partes N`, `--max 170`, `--cortes 160.5,308.2` (manual), `--so 1` (só uma parte, para prévia).
- Saída: `out/<slug>_parteN.mp4` (~10 MB cada) e `out/<slug>_cortes.txt` com os tempos.
- Tema (cores, fontes, nome do canal) em `THEME` no `cortes.py`, sobrescrito por `tema_cortes.json` quando existir.
