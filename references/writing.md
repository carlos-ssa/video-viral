# Roteiro

O vídeo compete com o próximo do feed. Cada segundo precisa dar um motivo para ver o seguinte.

Antes do roteiro, use o brief e os candidatos de [marketing e ganchos](marketing.md). Escolha a progressão pelo público e objetivo; para longo, veja [longo](formats/longo.md).

## Exemplo de estrutura de 40 segundos

| Tempo | Batida | O que fazer |
|---|---|---|
| 0–2 s | Gancho | A frase mais forte primeiro: resultado, contradição, pergunta concreta ou número. Texto na tela repete a ideia em até 6 palavras |
| 2–8 s | Promessa | O que a pessoa vai saber ou ver até o fim |
| 8–32 s | Conteúdo | 3 batidas, uma por cena ou par de cenas, cada uma com uma virada visual |
| 32–40 s | Recompensa | Entregue a promessa. Feche com uma frase que ligue de volta ao começo (incentiva rever) ou uma chamada curta |

Em pt-BR a narração fica perto de 2,5 palavras por segundo: 40 s ≈ 100 palavras. Escreva para o ouvido: frases curtas, ordem direta, números por extenso quando a voz tropeçar neles.

## Ganchos que funcionam

- Resultado antes do método: "Este cubo foi feito só com código."
- Contradição: "Todo mundo grava assim, e é por isso que ninguém assiste."
- Número específico: "3 erros que derrubam a retenção nos 2 primeiros segundos."
- Pergunta com aposta: "Você consegue achar o erro antes de mim?"

Evite gancho que o vídeo não cumpre; a queda logo após o gancho derruba a distribuição.

## Visual que segura

- Mudanças visuais com função narrativa: corte, zoom, texto, objeto ou mudança de performance; a cadência depende do formato, não de uma cota de efeitos.
- Texto na tela curto e diferente da legenda: a legenda transcreve, o texto destaca.
- Um ponto de foco por vez, perto do centro.

## Formato das cenas

Escreva direto no `video.json`:

```json
{"id": "s02", "narration": "Primeiro, o gancho precisa aparecer antes de qualquer logo.",
 "on_screen": "GANCHO NO QUADRO 0",
 "visual": {"engine": "hyperframes", "brief": "Linha do tempo horizontal; um bloco 'LOGO' é empurrado para fora por um bloco 'GANCHO' que cresce com mola"}}
```

## Publicação

Preencha `publish`:

- `caption`: primeira linha repete o gancho por escrito; depois 1–2 frases de contexto.
- `hashtags`: 3–5 específicas do nicho, não genéricas.
- `title` (YouTube Shorts): até ~60 caracteres, com a palavra que as pessoas buscam.
- `ai_label`: verdadeiro quando houver voz clonada de pessoa real ou cena realista gerada.
