# Voz oficial do canal Ponto Cego: "O Historiador"

| Item | Valor |
| --- | --- |
| Voz | **Pedro Lima - Serious** (catálogo público do HeyGen, português, masculina) |
| voice_id | `0d0e23e8170446e38b18a7380b2d30a8` |
| Motor | HeyGen `create_speech`, `engine: "elevenlabs"`, `settings: {"model_id": "eleven_v4"}` |
| Idioma | `language: "pt"` |
| Velocidade | 1.0 (padrão) |

## Como gerar a narração
1. Roteiro com tags do ElevenLabs v4: `[serious]`, `[sad]`, `[thoughtful]`, `[mysterious]`, `[whispers]`, `[curious]`, `[calm]` e as pausas `[short pause]` / `[long pause]`. Números escritos por extenso.
2. Divida em blocos de até ~4.500 caracteres, cortando nas mudanças de assunto. Cada bloco começa com uma tag.
3. Gere cada bloco com `create_speech` e guarde os `word_timestamps` que vêm na resposta. Eles substituem a transcrição.
4. O ambiente de render não baixa arquivos do HeyGen: passe os links dos `.wav` ao Matheus, que baixa e anexa.
5. Junte os blocos em ordem, com **1,0 s de silêncio** entre eles, e calcule os tempos absolutos (offset de cada bloco = soma das durações anteriores + 1 s por bloco).
   Modelo: `videos/mh370/narracao_blocos.txt` → `transcricao.txt`.

Referência de qualidade: `videos/mh370/` (primeiro vídeo com esta voz).
