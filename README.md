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

## Estilo ILUSTRADO (`ilustrado.py`)
Alternativa ao giz: ilustração vetorial chapada, com luz por hora do dia, profundidade (névoa de distância), personagens com rosto, roupa e cabelo. Modelo: `examples/ilustrado-demo/scenes.py`.
```python
from engine import *
from ilustrado import *
STYLE = "ilustrado"   # vinheta suave, sem poeira de giz
THEME = "mar"         # o tema continua mandando no som ambiente
```
- **Luz** (comece toda cena com um cenário pronto ou com `luz("...")`): `dia tarde crepusculo noite nublado sepia vela interior`. Tudo (cenário e personagens) é pintado pela luz da cena; à noite as janelas acendem sozinhas.
- **Cenários prontos**: `cena_vila(c, t, hora, estilo="medieval"|"colonial"|"pedra", igreja_x=)`, `cena_porto`, `cena_floresta`, `cena_deserto`, `cena_neve`, `cena_mar(navio="nau"|"vapor")`, `cena_campo`, `cena_interior(c, t, hora, tipo="biblioteca"|"cela"|"salao"|"escritorio")`. Varie a hora e a `seed` para não repetir o mesmo lugar.
- **Peças para montar cenários**: `ceu(nuvens, astro, passaros)`, `montanhas(y, h, depth, neve)`, `colinas`, `chao(tipo="grama"|"terra"|"pedra"|"areia"|"neve"|"madeira")`, `predio`, `casario`, `igreja`, `torre_castelo`, `piramide`, `dunas`, `arvore(tipo="redonda"|"pinheiro"|"palmeira"|"cipreste", seca)`, `floresta`, `mar_i`, `nau`, `vapor`, `cais`, `interior(parede, piso, janela)`, `estante`, `mesa_i`, `vela_i`, `livro_aberto`, `cruz_parede`, `janela_i`, `particulas(tipo="poeira"|"brasas"|"cinzas"|"vagalumes")`. `depth` de 0 (perto) a 1 (horizonte) clareia na névoa e dá profundidade.
- **O Historiador**: `historiador_i(c, t, x, y_pes, s, poses, exprs, look=)` (fedora, sobretudo, óculos redondos, barba curta, lanterna que brilha mais à noite). Mesmas poses e expressões dos bonecos de giz.
- **Personagens**: `boneco(c, t, x, y, s, poses, exprs, look, andar=True, **FIGURINO["monge"])`. Figurinos: `campones camponesa monge padre papa nobre marinheiro capitao cavalheiro dama explorador medico soldado escriba`. Ou monte: `roupa` (camisa casaco tunica batina vestido jaqueta armadura), `cabelo` (curto longo calvo careca tonsura coque cacheado), `barba` (cheia curta cavanhaque longa), `bigode`, `chapeu` (fedora cartola quepe gorro capuz tiara palha turbante solideu touca explorador boina coroa elmo), `pele` (clara media morena escura), `idade` (grisalho), `capa`, `oculos`, `mulher`.
- **Gente ao fundo**: `figurantes(c, t, y, n, s, figurinos=[...])` (andam sozinhos).
- **Textos**: `rotulo(c, t, t0, "1903 · OSWALDO CRUZ", "Rio de Janeiro")` (legenda de canto; com o Historiador à esquerda, use `x≈760` para não cobrir as pernas dele), `placa(c, "TÍTULO", "SOBRETÍTULO")` (cartão de pergaminho), `titulo_i(c, "TÍTULO", x, y, size)` (título com sombra, legível sobre céu claro). `typewrite`, `date_stamp`, mapas e o resto do motor continuam valendo.

### Tom do vídeo (`TOM = "..."` no scenes.py)
Escolha pelo assunto. O tom ajusta a cor de todos os quadros no fim (saturação, tinta fria, vinheta) e, no `sombrio`, troca sozinho `dia` por `nublado` e `tarde` por `crepusculo`.
| Tom | Use em | Luzes preferidas | Extras |
| --- | --- | --- | --- |
| `normal` | história, descobertas, curiosidades | todas | `particulas("poeira")`, raios de sol |
| `misterioso` | desaparecimentos, enigmas, casos sem solução | crepusculo, noite, nublado, vela | `nevoa_i` leve, `corvo`, lua |
| `sombrio` | terror, maldições, casas assombradas, mortes misteriosas | sombrio, tempestade, lua_sangue, noite, vela | `nevoa_i` densa, `relampago`, `silhueta`, `piscar`, `escurecer` |

Kit de terror (`examples/terror-demo/scenes.py`): luzes `sombrio`, `tempestade`, `lua_sangue`; cenários `cena_cemiterio`, `cena_casa_abandonada(raios=(t,))`, `cena_floresta_sombria`; peças `casa_abandonada`, `arvore_morta`, `lapide(tipo="arco"|"cruz"|"obelisco", texto=)`, `cerca_ferro`, `corvo(voando=)`, `corredor` (lâmpada que falha), `silhueta` (vulto de olhos acesos), `nevoa_i`, `relampago(c, t, vezes)` (chame por último; já toca `boom`), `piscar(t)` (intensidade de luz que falha) e `escurecer(c, a, borda)`. O medo vem da luz, da névoa e do que quase não se vê: nada de sangue, corpos ou violência gráfica.

### Thumbnails no estilo ilustrado
Modelo: `examples/thumb-demo/thumb.py` (uma por tom). Fórmula: o Historiador em close com emoção forte (`thumb_close(c, t, x, y, s, expr, pose)`, já iluminado de frente e com contorno claro), 2 a 4 palavras enormes (`thumb_texto(c, ["ONDE ESTÁ", "A TRIPULAÇÃO?"], x, y, size, cores)`), um selo curto opcional (`thumb_selo(c, "1959", x, y)`) e um cenário pronto com o objeto da história bem visível, sem texto em cima dele. `salvar_thumb(fn, caminho, tom="<tom do vídeo>")` aplica o tom e salva em 1280x720 com contraste extra.

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
Objetos do vídeo 5 mistérios: `rank_card(n, título, sub)` (cartão de item de lista), `axe chisel door(panel_out) trumpet music_notes townhouse gas_lamp big_ear printout(wow, highlight) signal_wave hydrogen sagittarius magnetar h_cloud b727(stair) parachute briefcase clip_tie money_bag bill_stack(rotten) farmhouse(attic, smoke_on) morro lead_mask kite raincoat water_bottle notebook lit_window_lights old_key mattock bread`.
Vídeo com vários blocos de narração: veja `videos/5-misterios/tempos.py` (gera narracao_blocos, transcricao e palavras.json a partir dos tempos de palavra) e a classe `Cx` no scenes.py (cenas em tempo local do bloco).
Objetos do MH370 que servem para outros vídeos: `satellite ping radio_tower sonar_ship seabed sonar_beam flaperon auv black_box monitor cockpit_door oxygen_mask crowd pilot`.

## Cortes verticais (TikTok, YouTube Shorts, Reels)
O padrão são **cortes selecionados e independentes**: 3 a 5 trechos fortes da história, cada um entendido sozinho,
com um gancho no começo. Nada de "PARTE X DE N": quem chega pelo Para Você no meio de uma série pula o vídeo.

1. **Escolher os trechos** (já no roteiro): partes que se entendem sem o resto, com começo forte e um fecho
   (uma revelação, uma pergunta sem resposta) e de 1 a 3 min. Critério: alguém que nunca viu o canal entende a
   situação nos primeiros 5 s? O trecho fecha com algo? Tem mais de 1 min? Os melhores costumam ser a abertura,
   a virada e as teorias.
2. **Gancho de cada corte**: uma frase de 4 a 7 s com o fato mais estranho daquele trecho, escrita para quem não
   viu o vídeo ("Um avião com duzentas e trinta e nove pessoas sumiu do radar e continuou voando."). Todos os
   ganchos vão num **bloco extra no HeyGen** (mesma voz), um depois do outro com `[long pause]` entre eles; guarde
   os `word_timestamps` para saber onde cada um começa e termina.
3. `python cortes.py videos/<slug> --frases` lista as frases com o tempo (¶ = começo de parágrafo).
4. Crie `videos/<slug>/cortes.json` (formato completo no topo do `cortes.py`):
```json
{"serie": "O VOO MH370", "cortes": [
 {"id": "radar", "inicio": 0, "fim": 96.3, "titulo": "O MISTÉRIO\\NDO MH370",
  "gancho": "Um avião com duzentas e trinta e nove pessoas sumiu do radar e continuou voando.",
  "gancho_audio": [0.0, 5.2], "gancho_tela": "SUMIU DO RADAR\\NE CONTINUOU VOANDO", "gancho_t": 30.0,
  "titulo_post": "Título curto do Shorts/Reels",
  "capa": ["SUMIU DO RADAR", "E CONTINUOU", "VOANDO"], "post": "Gancho do post... #misterio #historia #pontocego"}
]}
```
5. Gere:
```bash
python cortes.py videos/<slug> out/<slug>.mp4 --audio <mp4 com o áudio final> --ganchos <bloco_ganchos.mp3>
python capas.py videos/<slug> out/<slug>.mp4 --grade
```
- Cada corte (1080x1920): fundo desfocado, título do corte no topo, o vídeo no meio, legendas palavra por palavra.
  Abre com o gancho falado sobre o quadro `gancho_t` parado, com `gancho_tela` grande na tela; depois entra o
  trecho e, no fim, "VÍDEO COMPLETO NO YOUTUBE". Sem `--ganchos`, o texto do gancho fica nos primeiros 3,5 s.
- `inicio` e `fim` são ajustados sozinhos para o silêncio antes da frase mais próxima (até 2 s).
- Saída: `out/<slug>_corte_<id>.mp4` e `out/<slug>_cortes.txt` (duração, avisos fora de 62 s a 2:58, título do Shorts e descrição).
  `--so <id>` gera só um corte.
- Tempos das palavras: `videos/<slug>/palavras.json` se existir; senão são estimados pelas frases e marcas `[palavra@t]` do `narracao_blocos.txt` (quanto mais marcas, melhor a sincronia).
- **Modo antigo** (partes em sequência, "PARTE X DE N"): sem `cortes.json`, ou com `--sequencial`. Opções:
  `--titulo`, `--partes N`, `--max 170`, `--cortes 160.5,308.2`, `--so 1`.
- **Vídeos em lista (cortes independentes):** `--trechos "46.2-202.1,202.7-367.6" --titulos "TÍTULO 1|TÍTULO 2" --rotulos "Nº 5 DE 5|Nº 4 DE 5"`. Cada trecho vira `out/<slug>_corteN.mp4`, com o rótulo no lugar de "PARTE X DE N" e o cartão final "VÍDEO COMPLETO NO YOUTUBE" (nada de "continua na parte"). Shorts aceita até 3 min por trecho.
- Tema (cores, fontes, nome do canal) em `THEME` no `cortes.py`, sobrescrito por `tema_cortes.json` quando existir.

## Capas dos cortes
Com `cortes.json`, as capas saem dele (chave `capa` de cada corte; a cena é `gancho_t`): primeira linha grande no
topo, a cena no meio e as outras linhas embaixo, sem "PARTE X DE N". Saída `out/capas/<slug>_capa_<id>.png`.

Modo antigo: depois dos cortes, crie `videos/<slug>/capas.json` (uma entrada por parte, na mesma ordem dos cortes):
```json
{"serie": "NOME CURTO DA SÉRIE", "partes": [{"t": 155, "gancho": ["LINHA 1", "LINHA 2", "LINHA 3"]}]}
```
e rode `python capas.py videos/<slug> out/<slug>.mp4 --grade`.
- `"rotulo": "Nº 5"` (opcional) troca o "PARTE X DE N" da capa, para cortes independentes de vídeos em lista.
- `t` é o segundo do vídeo 16:9 com a cena da capa (personagem + número ou imagem forte daquela parte); `gancho` tem 1 a 3 linhas curtas (a primeira sai na cor de destaque).
- Cada capa (1080x1920): série, "PARTE X DE N" grande, a cena e o gancho, sobre o quadro desfocado. O essencial fica entre y 240 e 1680 (a grade do TikTok corta topo e rodapé).
- Saída: `out/capas/<slug>_capa_parteN.png` e `out/capas/<slug>_capas_grade.png` (para conferir). Cores e fontes vêm do tema (`tema_cortes.json`, chave extra `capa_bg` para a cor do fundo).

## Ártico (A Expedição Franklin)
- Mapas: `make_proj(..., coslat=True)` encolhe a longitude em altas latitudes. Regiões em `LAND`: `canada_n`, `king_william`, `victoria_is`, `prince_wales`, `somerset`, `devon`, `cornwallis`, `bathurst`, `baffin`, `ellesmere`, `greenland`, `iceland`, `scandinavia`. Listas `ARCTIC` e `NORTH_ATLANTIC`; cores `ICE_LAND` / `ICE_SEA` (`draw_map(c, proj, ARCTIC, land_col=ICE_LAND, sea_col=ICE_SEA)`).
- Objetos: `bomb_ship(t, name, sails, furled, funnel, frost)` (navio de 3 mastros, Erebus/Terror), `ice_field(t, y)`, `ice_ridge`, `coffin(open_)`, `grave_board(label)`, `cairn`, `tin_can(label, seam, open_)`, `navy_form(t, margin)` (bilhete com rabisco na margem), `sledge_boat(people, cargo)`, `inuk(...)` (caçador inuíte de parka), `silver_fork`, `silver_spoon`, `silver_plate(label)`, `cook_pot`, `lemon`, `lime_bottle(level)`, `dna(t)`, `lead_chart(t, p)`, `locomotive_engine`, `propeller(t)`, `mast_stub`, `camera_compact`, `cabin_corridor(t, n, closed)`, `shelf_plates`, `slipper`, `soap_bar`, `lantern_glow_ice`.

## Egito e Mediterrâneo (O Túmulo de Alexandre)
- Mapa: `draw_med_map(c, proj)` desenha a terra ocre e os mares por cima (Mediterrâneo, Negro, Vermelho, Golfo Pérsico, Mar da Arábia, Cáspio), ilhas (Creta, Chipre, Sicília, Rodes) e os rios `NILE`, `EUPHRATES`, `TIGRIS`. Cores `MED_LAND` / `MED_SEA`.
- Objetos: `funeral_cart(t)` (carro fúnebre dourado), `mule(t, crown)`, `sarcophagus(lid)` (pedra verde com hieróglifos), `royal_coffin("gold"|"glass", nose_chip)`, `mausoleum` (o Soma), `mosque(minaret)`, `basilica` (cinco cúpulas), `tumulus` (Anfípolis), `sphinx(head)`, `caryatid`, `cuirass`, `laurel_crown`, `flower`, `marble_bust`, `tsunami_wave(t)`, `crocodile`, `brick_wall(p)` (sobe com p), `modern_city(t)`, `palm_oasis(t)`, `dunes(t, y)`, `alexandria_skyline(t)` (com o farol). Cores `GOLD`, `GOLD_D`, `MARBLE`, `SANDSTONE`, `BASALT`.
- Chapéus novos dos bonecos: `hat="helmet"` (elmo grego/romano com crista), `hat="laurel"` (coroa de louros) e `hat="mitre"` (mitra de bispo).
- `videos/tumulo-alexandre/scenes.py` tem `tw("palavra", depois_de)`: busca o tempo da palavra no `palavras.json` (evita errar a conversão m:ss).

## Manuscritos e códigos (O Manuscrito Voynich)
- Escrita inventada: `vword(c, "qokedy", h)` desenha uma palavra em "voynichês" (glifos à mão, sem fonte), `vword_w`, `vline(c, x, y, w, h, seed)` e `vpara(..., star=True)` (parágrafo com estrela na margem).
- Páginas: `manuscript_page(c, kind, w, h, seed, t)` com `kind` = `text herbal zodiac bath rosette pharma first`; `manuscript_spread(c, esquerda, direita, t, p, s)` (livro aberto) e `closed_codex(c, s, glow_on, t)`.
- Ilustrações: `vplant(seed)` (planta inventada), `zodiac_wheel(t, r, spin, months)`, `bath_pool(t, w, n)`, `rosette`, `rosette_foldout(t, p)` (folha que se desdobra), `swallow_castle` (ameias em rabo de andorinha), `pharma_jar(kind)`, `star_mark`.
- Investigação: `uv_lamp(t, on, beam, ang)` (luz ultravioleta, cor `UVC`), `quill`, `punch_card`, `tabulator(t)` (máquina de cartões dos anos 1940), `cipher_machine(t, label)`, `cardan_grille(t, p)` (tabela + grade furada), `flask`, `handbag`, `ruler_cm`.
- Cenários: `villa` (casarão italiano), `prague_castle`, `beinecke` (biblioteca de mármore). Cores `VINK VGREEN VBLUE VRED VBROWN VSKIN VELLUM`.
- Chapéus novos: `hat="crown"` (coroa imperial) e `hat="skullcap"` (solidéu/barrete escuro de sábios e padres).

## Montes Urais (O Passo Dyatlov)
- Objetos (seção PASSO DYATLOV do engine): `dyatlov_tent(t, cut, sag, snow_on, glow_on)` (barraca comprida de lona; `cut` abre os rasgos), `cedar(h, broken)` (pinheiro siberiano com galhos quebrados), `campfire_out(t)`, `steam_train(t, cars)`, `old_truck(t)`, `skis`, `backpack`, `felt_boot`, `winter_coat(col)`, `knife`, `geiger(t, level)`, `radiation_sign(r)`, `orange_orb(t, r)`, `rocket(t)`, `probe_pole(h)`, `memorial_plaque(names)`, `ufo_disc(t)`, `factory(t, w, h)`, `snow_slab(w, h, crack)`, `big_footprint`, `telegram_form(lines)`, `soviet_doc(title, lines, stamp=)`, `hut`, `cache_platform`.
- `videos/passo-dyatlov/scenes.py` tem `slope()`/`slope_y()` (encosta com a barraca no alto e a floresta embaixo), `ural_map()` (mapa estilizado Sverdlovsk → Otorten), `flag()` (bandeirinha que marca onde alguém foi encontrado, sem mostrar corpos) e `slope_section()` (corte da encosta para explicar a placa de neve).
- `tempos.py` desse vídeo lê `ts/sN.txt` (só os tempos de início de cada palavra, na ordem do roteiro).

## Publicação automática
Terças e quintas o canal pode rodar sozinho: uma tarefa agendada do Claude faz o vídeo e coloca em `fila/`, e o GitHub Actions renderiza e envia ao YouTube agendado para as 18h. Configuração e uso em `automacao/README.md`; instruções da tarefa em `automacao/AUTOMATICO.md`.

## Pacífico Norte e aviação de carga (O voo Varig 967)
- Mapa (seção VARIG 967 do engine): `draw_pacific(c, proj)` desenha Japão, Sakhalin, Ásia/Kamchatka e Alasca/costa oeste dos EUA, com as Curilas e as Aleutas em pontinhos. Use longitudes de 0 a 360 (Los Angeles = 241.6), por exemplo `make_proj(125, 250, 14, 66)` (Pacífico inteiro) ou `make_proj(128, 168, 28, 56)` (Japão e Kamchatka).
- Objetos: `b707(t, door, gear, rose, stripe, lights)` (Boeing 707 cargueiro de perfil, 4 motores, porta de carga que abre, rosa dos ventos genérica na deriva), `fighter_jet(col, star)`, `cargo_crate(w, h, label)`, `abstract_painting(seed, w, h)` (tela abstrata genérica, não reproduz obra real), `necktie(col)`, `onion_field(y)`, `eiffel(h)`, `coffee_bush(seed)`, `headset_mic`, `life_vest`, `frozen_lake(w, h)`.

## Estrasburgo, 1518 (A Praga da Dança)
- Cenário urbano medieval (seção PRAGA DA DANÇA do engine): `half_timber(w, h, seed, lit)` (casa de enxaimel), `cathedral(h, lit)` (catedral gótica de arenito vermelho com uma torre só), `strasbourg(c, t, y, n, seed, lit, cat_x)` (fileira de casas + rua de pedra, catedral opcional), `cobbles(c, y)`.
- Dança: poses novas `dance_a dance_b dance_c dance_d` (braços e uma perna levantados) e `slump` (exausto); `dancer(c, t, x, y, s, t0, t1, fid, col, woman)` alterna as poses com pulos (`dance_keys`, `dance_bob`). No `scenes.py` do vídeo há `mini_dancer`/`dance_crowd` para multidões pequenas.
- Objetos: `red_shoes(crosses)` (ritual de São Vito), `saint_statue(t, glow_on)` (imagem de madeira com auréola e palma), `drum(t, beat)`, `flute`, `fiddle`, `stage(w, h)` (palco de madeira), `cart(t, w, moving, cover)` (carroça de duas rodas), `rye(ergot, h)` (centeio com esporão), `chronicle(w, h, title)` (página de crônica), `council_seal`, `laugh_marks(t)`.
- Chapéus novos: `hat="coif"` (touca de linho das mulheres) e `hat="beret"` (barrete de mercador/médico/conselheiro).
- Cores `WOOD WOOD_D RSAND PLASTER SHOE_RED`.

## Deserto do Peru (As Linhas de Nazca)
- Geoglifos (seção LINHAS DE NAZCA do engine): `geoglyph(c, kind, p, col, lw, glow_a)` desenha a figura como trilha clara contínua, com `p` (0..1) para o efeito de traçar; `kind` = `hummingbird monkey spider condor astronaut cat lizard orca llama trapezoid spiral head`. `glyph_head_pos(kind, p)` dá a ponta do traço (para um caminhante seguir a linha).
- Chão: `pampa_top(c, t, seed, lines, dark)` (deserto de pedrinhas visto de cima, em cache), `nazca_lines_set(seed, n)` (linhas retas aleatórias), `trapezoid_top`, `pampa_side(c, t, y, hills, track)` (deserto visto do chão), `stone_piles`, `highway_top`.
- Objetos: `cessna(t)` (avião pequeno de perfil), `cessna_top(t)` + `plane_shadow` (visto de cima), `stake(h)` + `cord(...)`, `mirador(h)` (torre de observação), `puquio(t, r)` (aqueduto em espiral visto de cima), `drone(t)`, `setting_sun(r)`, `shards(seed)` (cacos de cerâmica), `nazca_vase(s)`, `scan_box(w, h, t, col, label)` (caixa de detecção da IA). Cores `GLYPH PAMPA PAMPA_D PAMPA_L NAZCA_RED NAZCA_CREAM`.
- `videos/linhas-de-nazca/scenes.py` tem `glyph_at` (geoglifo sendo traçado a partir de um tempo), `native` (antigo morador), `hillside` (encosta para geoglifos) e `ai_screen` (tela com detecções). O `tw()` desse vídeo procura a ocorrência mais próxima do tempo dado.

## TikTok nativo (vídeos curtos próprios, desde 07/11/2026)
No TikTok o canal usa vídeos curtos com roteiro próprio (60-80 s), não cortes do vídeo longo. A cena é desenhada em 16:9 e o
`tiktok.py` monta o vertical no mesmo enquadramento dos cortes (título no topo, cena no meio, legendas palavra por palavra e capa):
`python tiktok.py videos/<slug> out/<slug>_base.mp4 out/<slug>_tiktok.mp4 --capa out/<slug>_capa.png` (lê `tiktok.json` e `palavras.json`).
Produção automática: `automacao/AUTOMATICO_TIKTOK.md`, temas em `automacao/temas_tiktok.md`, render e release no workflow `tiktok.yml`.
Novos no `ilustrado.py`: `farol_i(c, t, x, y, s, aceso)`, `ilha_rochosa`, `cena_ilha_farol(c, t, hora, aceso)`, `cena_praia(c, t, hora)`,
`papel_nota(c, linhas, w, h, size)` (papel rasgado com texto), `quadro_giz(c, linhas)`, `dna_i(c, t)` e `onda_gigante(c, t, t0, x, y, w, h)`.
