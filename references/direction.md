# Direção

Vídeo de IA fica medíocre quando cada etapa decide sozinha: a fonte é a padrão, a imagem ilustra a palavra literal, tudo entra com o mesmo fade e não há som além da voz. A direção decide o visual inteiro antes de qualquer código, para que voz, cena, movimento, legenda e trilha sigam a mesma intenção. Ela custa minutos; corrigir depois do render custa horas.

Grave o resultado em `direction` no `video.json` e o raciocínio em `research/direcao.md`.

## Sumário

- [1. Referências](#1-referências)
- [2. Estilo](#2-estilo)
- [3. Gancho](#3-gancho)
- [4. Roteiro de planos](#4-roteiro-de-planos)
- [5. Quadros de estilo](#5-quadros-de-estilo)
- [O que deixa vídeo de IA com cara de barato](#o-que-deixa-vídeo-de-ia-com-cara-de-barato)

## 1. Referências

Use o recorte de [pesquisa](research.md): nicho, plataforma, objetivo, duração, período e fontes. Examine exemplos recorrentes e seu contexto; visualizações por dia são apenas um sinal. Registre abertura visual/verbal, promessa, ritmo, enquadramento, payoff e CTA. Google Trends ajuda a escolher tema e sazonalidade, sem comprovar retenção ou conversão.

Sem pesquisa disponível, avance com hipóteses identificadas.

## 2. Estilo

Escolha um estilo e preencha `direction` com valores concretos. Misturar dois é aceitável; inventar um sem paleta e fonte definidas não é.

| Estilo | Quando | Paleta e textura | Tipografia | Movimento e câmera | Transição | Som |
|---|---|---|---|---|---|---|
| Documentário cinematográfico | História, ciência, mistério, biografia | Escura e dessaturada, 1 cor de destaque quente; grão de filme, vinheta, vazamento de luz | Serifada para título (Playfair Display, Cormorant), sem serifa condensada para legenda | Aproximação lenta e contínua (escala 1,00→1,08 por plano), paralaxe em 3 camadas, poeira no ar | Corte seco, mergulho no preto, flash branco curto | Pad grave, impacto sub-grave nas revelações, whoosh nos cortes |
| Explicativo 3D | Como funciona, tecnologia, produto | Fundo em degradê suave, 2 cores de marca, luz de recorte; sombra de contato | Sem serifa geométrica pesada (Montserrat, Space Grotesk) | Câmera orbitando 15–30°, objetos que se montam e desmontam, explosão de peças | Zoom contínuo para dentro do objeto, giro do cubo (gl-transitions) | Cliques, pops, tom ascendente na montagem |
| Tipografia cinética | Opinião, lista, frase de impacto, dica rápida | Duas cores de alto contraste (ex.: #0E0E0E e #F2E85C), sem foto | Display condensada enorme (Anton, Bebas Neue, Archivo Black) | Palavra a palavra no ritmo da fala, máscaras que revelam, escala na palavra-chave | Corte na batida, texto que vira o próximo quadro | Batida marcada, golpe seco em cada palavra-chave |
| Dados e infográfico | Números, comparação, ranking, finanças | Neutra (off-white ou grafite) e 1 destaque; grade sutil | Sem serifa com algarismos tabulares (Inter, IBM Plex Sans) | Barras e linhas que crescem, contadores, mapas que aproximam | Gráfico que se transforma no seguinte | Tique de contador, ding no número final |
| Colagem | Cultura, humor, curiosidade, lifestyle | Papel, recortes, fita, alto contraste com cor saturada | Mistura de 2 fontes no máximo (uma manuscrita) | Recortes em 12 qps com tremor, rabiscos que se desenham (Paper.js) | Rasgo de papel, deslizar de camada | Papel, tesoura, carimbo |

Campos de `direction`:

```json
"direction": {
  "style": "documentario",
  "references": ["https://youtube.com/shorts/...", "..."],
  "palette": ["#0B0D10", "#1C232B", "#E8DCC2", "#E0A030"],
  "fonts": {"title": "Playfair Display", "body": "Inter", "captions": "Anton"},
  "motion": "aproximação lenta contínua; entradas expo.out 12 quadros; paralaxe 3 camadas",
  "texture": ["grão 6%", "vinheta 25%", "poeira"],
  "transitions": "corte seco na batida; mergulho no preto entre atos",
  "music_mood": "pad cinematográfico grave, 70 bpm, impacto no payoff",
  "sfx": ["whoosh", "impacto sub-grave", "riser antes da revelação"]
}
```

Fontes: use famílias com licença aberta (SIL OFL, como as do Google Fonts), coloque os arquivos `.ttf` em `assets/fonts/` e registre em `assets`. O `deliver.py` passa essa pasta para as legendas; na composição, carregue com `@font-face`. Atualize `captions.font` para a fonte de legenda escolhida e a cor de destaque da legenda para a cor de destaque da paleta.

## 3. Gancho

Use os cinco candidatos multimodais de [marketing e ganchos](marketing.md), ligando público, promessa e payoff. Complete a avaliação audiovisual abaixo sem duplicar a pesquisa:

| Critério | Pergunta |
|---|---|
| Lacuna | A pessoa precisa ver o resto para fechar a curiosidade? |
| Especificidade | Tem número, nome, objeto ou resultado concreto? |
| Imagem no quadro 0 | Existe uma imagem forte que mostra o gancho sem depender da fala? |
| Velocidade | Cabe em até 2 s falado e até 6 palavras na tela? |
| Cumprimento | O vídeo entrega exatamente o que o gancho promete? |

Escolha pela adequação ao objetivo, pelo cumprimento da promessa e pela qualidade da execução visual. Registre candidatos e justificativas em `hook_candidates`; preserve alternativas para testes controlados.

## 4. Roteiro de planos

Cada cena vira uma lista de planos em `scenes[].visual.shots`. Em vertical dinâmico, mudanças a cada 1,5–3 s são uma referência inicial, não uma obrigação universal. Planeje contraste, respiros e evolução conforme o conteúdo. Ancore cada plano numa palavra da narração para que imagem e fala cheguem juntas.

```json
"visual": {
  "engine": "hyperframes",
  "brief": "Muralha de Constantinopla ao amanhecer; canhão gigante entra em primeiro plano",
  "shots": [
    {"cue": "Em 1453", "frame": "geral", "subject": "muralha em silhueta contra céu laranja",
     "camera": "aproximação lenta 1.00→1.06", "in": "corte", "emphasis": "1453 em display enorme, mascara de baixo para cima",
     "sfx": "impacto sub-grave"},
    {"cue": "um canhão", "frame": "close", "subject": "boca do canhão, fumaça", "camera": "paralaxe lateral",
     "in": "whip pan com desfoque", "emphasis": "", "sfx": "whoosh"}
  ],
  "transition_out": "mergulho no preto 8 quadros"
}
```

| Campo | Valores típicos |
|---|---|
| `cue` | Palavra ou trecho da narração em que o plano começa; o tempo exato vem de `captions/words.json` |
| `frame` | geral, médio, close, macro, plongée (de cima), contra-plongée, tela só de texto, gráfico |
| `camera` | estática com elemento em movimento, aproximação, afastamento, pan, órbita, paralaxe, travelling, câmera na mão sutil |
| `in` | corte, máscara, escala com mola, whip pan, morph, gl-transition (nome) |
| `emphasis` | Texto na tela, palavra-chave destacada, número que conta, seta, círculo que se desenha |
| `sfx` | Efeito sonoro alinhado com a entrada |

Prefira imagem que acrescenta à fala, não que a repete: se a narração diz "dinheiro", mostre o gráfico caindo ou a carteira vazia, não uma pilha de notas.

## 5. Quadros de estilo

Antes de animar o vídeo inteiro, faça 3 quadros parados no visual final: o quadro 0 (gancho), um quadro do meio e o quadro do payoff. Olhe os três juntos e corrija paleta, fonte, contraste e composição agora. É o ponto mais barato para mudar o visual; depois disso, cada mudança é um novo render.

No HyperFrames, renderize quadros soltos no tempo de cada plano. No Blender, `--frames` de um quadro só. No ComfyUI, gere os fundos com a semente fixa e a paleta descrita no prompt.

## O que deixa vídeo de IA com cara de barato

| Sinal | Correção |
|---|---|
| Fonte padrão (Arial, Roboto) centralizada e parada | Fonte do estilo, hierarquia de tamanhos, texto que entra com máscara e tem uma palavra destacada |
| Tudo entra com o mesmo fade linear | Curvas de [motion](motion.md#princípios), entradas diferentes por tipo de elemento |
| Imagem literal da palavra falada | Imagem que mostra consequência, contraste ou detalhe |
| Vídeo gerado por IA com rostos e mãos deformando | Imagens paradas com câmera virtual e paralaxe, 3D em código ou o próprio texto como imagem |
| Quadros mortos de 3 s ou mais | Movimento contínuo de câmera e um evento a cada 1,5–3 s |
| Só voz e música no mesmo volume o tempo todo | Efeitos nas entradas, música que abaixa sob a voz e sobe no payoff, um silêncio de 0,3 s antes da revelação |
| Paleta que muda a cada cena | 3 a 5 cores do `direction.palette` em todas as cenas |
| Legenda em cima do assunto principal | Assunto no terço de cima, legenda no terço de baixo, dentro da área segura |
| Final que só para | Última frase que liga ao gancho (loop) ou corte seco no ponto alto |
