# Motion no stack v2

HyperFrames + GSAP é o compositor. Escolha a linguagem pela cena; o arsenal é exclusivo e os módulos não precisam aparecer todos no mesmo vídeo. [Direção](direction.md) e [módulos](modules.md) definem a função de cada recurso.

## Tempo determinístico

Toda animação é função do tempo/quadro pedido. Não usar relógio real, aleatório sem semente ou uma física que muda ao buscar para trás. Os adaptadores retornam createScene(host,params) e drawAt(t); carregamento assíncrono termina antes de capturar. Testar busca 2→0→2 e conferir o mesmo quadro.

GSAP usa uma timeline pausada registrada no compositor. PixiJS, Paper.js e p5.js desenham a partir desse tempo. gl-transitions recebe texturas e progresso explícitos. Three.js renderiza câmera/objetos no tempo solicitado; o Blender pode entregar vídeo/frames ou GLB preparado com glTF Transform. Não duplicar motores sem contribuição concreta.

## Linguagens

| Necessidade | Recurso |
|---|---|
| Tipografia, layouts, recortes, máscaras e UI real | HyperFrames/GSAP |
| Muitos elementos e sprites 2D | PixiJS |
| Vetores, traços e geometria ilustrada | Paper.js |
| Arte procedural, ondas e visualizers | p5.js |
| Transição por shader | gl-transitions no compositor |
| Geometria/câmera/material 3D | Three.js ou Blender |
| Imagens e ativos gerados | Workflow ComfyUI validado |
| Efeitos e pontuação sonora | Tone.js offline |
| Música gerada | ACE-Step 1.5 configurado |

## Acabamento

Planejar um foco por vez, antecipação, timing de entrada/saída, contraste e continuidade. Curvas, duração e escala precisam servir ao conteúdo. Não transformar ritmo em zoom alternado mecânico; uma pausa precisa de intenção. Câmera, tipografia e som podem criar progressão sem impor uma quantidade universal de efeitos.

A fala/música mede o tempo das cenas. Sincronizar entradas por palavras/batidas verificadas; estimativas precisam estar identificadas. Não sobrepor legenda à informação essencial do produto e manter a área segura.

A demo de um módulo prova integração técnica, não direção cinematográfica. Inspecionar trechos e transições reais, som e legibilidade no arquivo final; notas autodeclaradas não substituem a evidência.
