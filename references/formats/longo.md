# Vídeo longo (YouTube 16:9)

Vale para gravação própria e para vídeo narrado do zero com mais de 3 minutos. Use junto com o guia do formato ([gravação](gravacao.md) ou [pipeline narrado](../pipeline.md)); aqui está só o que muda.

## O que muda em relação ao vertical

| | Vertical curto | 16:9 longo |
|---|---|---|
| Tamanho | 1080×1920 | 1920×1080 (4K se a fonte for 4K e o usuário pedir) |
| Decide a retenção | 2 primeiros segundos | 30 primeiros segundos e cada transição de assunto |
| Evento visual | a cada 1,5–3 s | a cada 5–8 s (corte, zoom, B-roll, gráfico, texto) |
| Legenda | queimada, palavra a palavra | opcional; prefira subir o `.srt` na plataforma |
| Capa | primeiro quadro | miniatura 1280×720 obrigatória |
| Extra | — | capítulos, descrição, cortes verticais derivados |

## Estrutura que segura

1. **0–30 s: promessa.** Diga o que a pessoa vai ganhar e por que ficar até o fim; mostre um pedaço do resultado. Sem vinheta, sem "fala, pessoal" de 15 s, sem pedir inscrição antes de entregar algo.
2. **A cada 60–90 s: virada.** Nova pergunta, mudança de cenário, B-roll, gráfico, história. Cada seção abre com um mini-gancho ("e o terceiro é o que mais custa caro").
3. **Payoff antes do fim.** Entregue o prometido e encerre rápido. CTA no meio (depois de uma entrega) rende mais que no fim; não anuncie "pra finalizar" antes da hora, porque o público sai.

Em gravação, `footage.py cut` tira os silêncios; em vídeo longo use `--min-silence 0.6` e `--pad 0.15` para não ficar atropelado.

## Capítulos

Em `publish.chapters`, uma lista `[{"start": "00:00", "title": "Introdução"}, ...]`. O YouTube exige: primeiro em 00:00, pelo menos 3, cada um com 10 s ou mais, em ordem. `deliver.py` confere e escreve o bloco pronto para colar na descrição. Marque capítulo onde muda o assunto e escreva títulos que prometem ("Por que a poupança perde"), não rótulos ("Parte 2").

Os tempos são do vídeo final: depois do `render`, use `edit/timeline.md` para achar onde cada trecho caiu.

## Miniatura

1280×720, menos de 2 MB, em `publish.thumbnail`. Rosto com expressão forte (quadro da própria gravação, de `edit/frames.jpg` ou exportado do vídeo), até 4 palavras grandes que completam o título sem repetir, alto contraste, legível em tamanho de celular. Pode ser feita em código (HTML renderizado ou FFmpeg `drawtext` sobre um quadro) ou ComfyUI; registre fonte e imagem em `assets`.

## Título e descrição

Título com até ~60 caracteres visíveis, promessa ou curiosidade clara, sem caixa alta inteira. Descrição: 2 linhas que resumem a promessa (aparecem antes do "mostrar mais"), capítulos, links. Grave em `publish.title` e `publish.description`.

## Cortes derivados

Todo longo rende cortes verticais: depois de entregar, rode `clips.py suggest` no projeto do longo e ofereça os 3 melhores ao usuário ([cortes](cortes.md)).
