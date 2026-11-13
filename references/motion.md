# Motion graphics

Movimento é o que separa um vídeo de uma apresentação de slides. Este guia diz como animar cada elemento do roteiro de planos ([direção](direction.md#4-roteiro-de-planos)) e qual biblioteca usar em cada caso. A regra de animação determinística do SKILL.md vale para tudo aqui.

## Sumário

- [Princípios](#princípios)
- [Ponte determinística](#ponte-determinística)
- [Ritmo amarrado ao áudio](#ritmo-amarrado-ao-áudio)
- [Receitas](#receitas)
- [Qual biblioteca](#qual-biblioteca)

## Princípios

Valores em quadros a 30 qps; em 60 qps, dobre.

| Princípio | Como aplicar |
|---|---|
| Curva, nunca linear | Entrada: `expo.out` ou `quint.out`. Saída: `expo.in`, mais rápida que a entrada. Deslocamento: `power3.inOut`. Linear só em movimento contínuo (rotação lenta, câmera derivando) |
| Duração | Entrada de texto 8–14 quadros; objeto grande 14–20; saída 6–10; troca de cena 6–12. Segure o texto pelo menos 0,6 s depois de completo, mais 0,3 s por palavra além de 3 |
| Escalonamento | Letras 1–2 quadros entre si, palavras 3–4, itens de lista 4–6. Nada de tudo entrando junto |
| Antecipação e sobra | Um recuo de 3–5% antes do movimento grande; mola com pouca sobra (`back.out(1.4)`, `elastic` só em humor). Sobra exagerada em tudo parece template |
| Um foco por vez | Um elemento principal se move; o resto respira (escala 1–2%) ou fica parado. Dois movimentos fortes ao mesmo tempo disputam o olhar |
| Nunca parado | Câmera virtual sempre derivando: aproximação de 2–8% por plano, paralaxe ou partículas lentas. Quadro sem nenhum movimento por mais de 1,5 s parece travado |
| Profundidade | Três camadas: fundo lento e desfocado (blur 4–12 px), meio, frente rápida. A diferença de velocidade cria o 3D sem 3D |
| Desfoque de movimento | Em movimentos rápidos (whip pan, entrada grande), aplique blur direcional proporcional à velocidade no meio do movimento; sem ele o movimento rápido parece engasgado |
| Textura e cor | Grão 4–8% por cima de tudo (ruído com semente, mudando por quadro), vinheta, leve aberração cromática só em impactos. Gradação de cor por camada de ajuste (CSS `filter` ou shader), igual em todas as cenas |
| Tipografia | Máscara (`clip-path: inset()`) revelando de baixo para cima é mais elegante que fade. Palavra-chave: cor de destaque, escala 1,1–1,2 e peso maior. Kerning apertado em display grande |

## Ponte determinística

O renderizador do HyperFrames e o Remotion pedem um quadro de cada vez, fora de ordem e sem relógio real. Por isso, toda biblioteca que tem laço próprio (PixiJS, p5.js, Three.js, Matter.js, tsParticles) deve desenhar a partir de uma função do tempo, `drawAt(t)`, chamada pela linha do tempo que o renderizador controla.

No HyperFrames (linha do tempo GSAP; confira a forma exata de registrar a linha do tempo na skill oficial):

```js
const state = { t: 0 };
tl.to(state, { t: DURATION, duration: DURATION, ease: "none", onUpdate: () => drawAt(state.t) }, 0);

function drawAt(t) {
  // nada de Date.now, requestAnimationFrame ou Math.random sem semente
  camera.position.z = 6 - 0.4 * gsap.parseEase("power2.inOut")(Math.min(t / 4, 1));
  renderer.render(scene, camera);
}
```

No Remotion: `const t = useCurrentFrame() / fps;` e desenhe em `useEffect` dependente do quadro, ou use as integrações oficiais (`@remotion/three`).

Aleatório com semente (para partículas, grão, tremor):

```js
function rng(seed) { return () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296); }
```

Física (Matter.js, Rapier): simule o trecho inteiro uma vez no carregamento, com passo fixo `1000/fps`, guarde as posições por quadro num array e, em `drawAt(t)`, leia o quadro `Math.round(t * fps)`. Assim o renderizador pode pedir qualquer quadro em qualquer ordem.

## Ritmo amarrado ao áudio

- Cortes e entradas começam no início de uma palavra: pegue os tempos de `captions/words.json` pelo `cue` de cada plano. Adiantar a imagem 2–3 quadros em relação à palavra faz o corte parecer intencional.
- Cada transição e cada revelação tem um efeito sonoro (whoosh, impacto, pop, tique). Gere com Tone.js ou use bibliotecas CC0, registre em `assets` e ponha o áudio na própria composição ou em `audio/sfx/`.
- A música abaixa sob a voz (o `deliver.py` faz isso) e o ponto alto dela cai no payoff. Um silêncio de 0,2–0,4 s antes da revelação principal aumenta o impacto.
- Legenda animada em HTML (de `captions/captions.json`) permite destacar a palavra falada e as palavras-chave da direção. Nesse caso entregue com `deliver.py --no-captions`.

## Receitas

| Efeito | Como | Biblioteca |
|---|---|---|
| Tipografia cinética | Cada palavra de `captions.json` entra com máscara no seu tempo; palavra-chave muda de cor e escala; a frase sai inteira antes da próxima | GSAP ou Anime.js |
| Contador de número | Interpole um objeto `{v: 0}` até o valor, formate com `Intl.NumberFormat("pt-BR")`, algarismos tabulares, `expo.out` em 1–1,5 s, tique sonoro acompanhando | Anime.js ou GSAP |
| Traço que se desenha | SVG com `stroke-dasharray` igual ao comprimento e `stroke-dashoffset` indo a 0; para formas orgânicas, Paper.js com `path.length * progresso` | SVG ou Paper.js |
| 2.5D a partir de imagem | Gere fundo, assunto (fundo transparente) e frente separados no ComfyUI; anime escala e posição em velocidades diferentes; desfoque o fundo | CSS e GSAP |
| Objeto 3D herói | GLB do Hunyuan3D-2mini otimizado com glTF Transform; luz de recorte e luz ambiente fraca; órbita de 20–30° no plano; sombra de contato no chão | Three.js |
| Montagem e explosão | Peças do modelo com deslocamento ao longo da normal, escalonadas, voltando com `expo.out` | Three.js |
| Física de impacto | Letras ou objetos caindo e empilhando, pré-simulados com passo fixo | Matter.js (2D), Rapier (3D) |
| Partículas | Poeira, faíscas, confete com sistema próprio e semente fixa; tsParticles só se a semente e o tempo puderem ser controlados, e confira o render | Canvas, PixiJS ou tsParticles |
| Muitos elementos | Mapas de pontos, multidões, grades de ícones com milhares de sprites | PixiJS |
| Fundo generativo | Campo de ruído ou degradê em shader, recebendo `t` como uniform | OGL ou p5.js com `randomSeed` |
| Transição em shader | `crosszoom`, `directionalwarp`, `cube`, `wind` em 8–12 quadros, progresso vindo de `t` | gl-transitions sobre OGL ou Three.js |
| Whip pan | Deslocamento horizontal de 120% da largura em 6–8 quadros com blur direcional no meio, a próxima cena chegando do outro lado | CSS e GSAP |
| Grão e vinheta | Canvas de ruído com semente diferente por quadro, `mix-blend-mode: overlay`, opacidade 4–8%; vinheta com degradê radial | Canvas e CSS |
| Gravação de tela (OBS) | Moldura de aparelho, zoom suave no ponto da ação, cursor destacado, desfoque do resto | CSS e GSAP |

## Qual biblioteca

Use a menor que resolve. Cada uma a mais é peso na página e mais um ponto onde o render pode diferir da prévia.

| Precisa de | Use |
|---|---|
| Texto, formas, imagens, SVG, linha do tempo | GSAP (vem com o HyperFrames) ou Anime.js |
| Componentes React e molas | Remotion com `spring()`; React Spring só fora do render |
| Muitos sprites 2D | PixiJS |
| Desenho generativo | p5.js |
| Caminhos vetoriais e traços | Paper.js |
| Física | Matter.js (2D) ou Rapier (3D) |
| 3D | Three.js; OGL para shader leve; Blender para cena 3D complexa ou realista |
| Partículas | Sistema próprio com semente; tsParticles com cuidado |
| Transições | gl-transitions |
| Modelos 3D | Hunyuan3D-2mini gera, glTF Transform otimiza, Three.js ou Blender anima |
