# Composição HyperFrames → master

Produção completa termina em um filme composto e renderizado por **HyperFrames 0.9.40 + GSAP**, não na base FFmpeg ou numa demo isolada. Execute primeiro `plan.py`; registre cenas, ferramentas, fontes e saídas em `tool_plan`. Render técnico e aprovação audiovisual são portões diferentes.

## Projeto e HTML

Mantenha em `<projeto>/composition/` um `index.html`, scripts/bundles locais e `assets/` com fontes, imagens, vídeos e cenas. Use URLs relativas a esse HTML e arquivos dentro da pasta servida, copiando ativos sem alterar os originais. Guarde narração/legendas originais em `audio/` e `captions/` do projeto. Crie também `<projeto>/render/` antes do render.

Exemplo mínimo de 4 segundos; ajuste dimensão, duração e fps aos valores medidos do manifesto. Copie `gsap/dist/gsap.min.js` do stack fixado para `composition/assets/gsap.min.js` (não dependa de CDN).

```html
<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><style>
html,body { margin:0; background:#101629; }
#main { position:relative; width:1080px; height:1920px; overflow:hidden; }
#titulo { position:absolute; left:90px; top:300px; width:840px;
  color:#fff; font:80px sans-serif; }
</style></head>
<body>
<div id="main" data-composition-id="main" data-start="0"
     data-width="1080" data-height="1920" data-duration="4" data-fps="30">
  <div id="titulo" class="clip" data-start="0" data-duration="4"
       data-track-index="1">Sua promessa aqui</div>
</div>
<script src="assets/gsap.min.js"></script>
<script>
window.__timelines = window.__timelines || {};
const tl = gsap.timeline({paused:true});
tl.fromTo('#titulo', {y:24},
  {y:0, duration:0.4, ease:'power2.out'}, 0);
tl.to('#titulo', {scale:1.04, duration:3.6, ease:'none'}, 0.4);
window.__timelines.main = tl;
</script>
</body></html>
```

`data-composition-id` identifica a raiz; a chave em `window.__timelines` deve ser igual. `data-width/height/duration` definem o quadro e a duração total; `data-fps` define o padrão usado pelo render quando a flag falta. `class="clip"`, `data-start` e `data-duration` delimitam a janela dos elementos; `data-track-index` organiza pistas do editor, não resolve sobreposição nem substitui CSS/z-index. Direcione fontes, hierarquia e área segura; o exemplo não é acabamento pronto.

## Tempo e módulos visuais

O runtime busca a timeline pausada em cada quadro (`t = frame / fps`); não chame `play()` para animar. Calcule todo estado pelo tempo solicitado. Evite relógio real, timers, RAF autônomo e `Math.random()` sem semente. Carregue fontes/texturas antes da captura; teste busca **2 → 0 → 2** com pixels iguais no mesmo tempo. Fontes/browser/encoder também afetam reprodutibilidade: registre versões, ambiente e parâmetros.

`visual_scene.mjs` já gera raiz `main`, clip `visual`, bundle GSAP, `drawAt(t)` e parâmetros de semente. Há duas rotas de integração:

1. **Rota simples e verificável:** adapte a cena conforme [módulos](modules.md), reconstrua seu bundle e renderize a pasta de cena com os comandos abaixo, usando saída `composition/assets/s01.mp4`. Inclua esse arquivo no filme principal como `<video id="s01" class="clip" src="assets/s01.mp4" data-start="0" data-duration="4" data-track-index="0" muted playsinline></video>`. Renderize depois a composição principal inteira; o trecho isolado não substitui esse passo.
2. **Composição editável aninhada:** o contrato oficial usa host `<div class="clip" data-composition-id="s01" data-composition-src="compositions/s01.html" data-start="0" data-duration="4" data-track-index="0"></div>`; o arquivo externo envolve conteúdo em `<template>`, usa tempos locais e registra timeline sob `s01`. Não aponte esse host diretamente ao HTML completo gerado: adapte wrapper, IDs, seletores, assets e registro `__timelines.main` para evitar colisões. Faça lint/check e inspecione cada cena montada.

O gerador também escreve `data-track-kind="graphics"` e `window.__hf.buildReady`. Eles existem no código local, mas não foram confirmados como contrato público dessa versão nas páginas consultadas. **Confirmar com `npx hyperframes --help`** e com o contrato/source de runtime 0.9.40 antes de depender desses detalhes numa composição aninhada. A rota de pré-render permite testar a cena isolada; falha de readiness deve bloquear o render, não ser anunciada como integração validada.

## Voz, legendas e ativos

A narração medida (`audio/voice.wav`) define entradas e duração das cenas. Para a rota padrão, renderize as cenas narradas **sem áudio**, deixe `deliver.py` mixar voz, música e `audio/sound-design.wav`, e mantenha legendas em ASS via `captions.py ass`. O render de A-roll pode manter seu áudio original; confira que não haja outra cópia da fala sendo mixada.

Para ouvir no preview, é possível copiar a voz para `composition/assets/voice.wav` e declarar `<audio src="assets/voice.wav" data-start="0" data-duration="4" data-volume="1"></audio>`. Áudio é extraído pelo runtime, não tocado por callbacks GSAP. Se essa faixa também estiver no master e `deliver.py` for remixar as mesmas fontes externas, use `--mute-video-audio` para descartar o áudio do master. Em gravação, preserve o áudio A-roll quando ele é a fonte única. Evite mix duplicada: `--no-music` só desativa a trilha externa, não voz/efeitos.

Legendas HTML são elementos `clip` com tempos conferidos de `captions/words.json`, dentro da área segura e fora do rosto/UI. Com elas já queimadas no master, passe `--no-captions` ao entregar. Com ASS externo, deixe a legenda fora do HTML. Registre origem/licença de imagens, fontes e áudio no manifesto; fontes locais usam `@font-face` e precisam estar carregadas no primeiro quadro.

## Checar, visualizar e renderizar (0.9.40)

Use o executável **já instalado** pelo lockfile de `assets/node`, evitando `npx` baixar uma versão atual. `<node-root>` normalmente é `~/.video-viral/node-v2`; no Windows o shim é `hyperframes.cmd`. Os diretórios de projeto são argumentos posicionais; use saída absoluta para eliminar ambiguidade de resolução.

```sh
"<node-root>/node_modules/.bin/hyperframes" --version
"<node-root>/node_modules/.bin/hyperframes" lint "<projeto>/composition"
"<node-root>/node_modules/.bin/hyperframes" check "<projeto>/composition"
"<node-root>/node_modules/.bin/hyperframes" preview "<projeto>/composition"
"<node-root>/node_modules/.bin/hyperframes" render "<projeto>/composition" --output "<projeto>/render/master.mp4" --fps 30
```

Se o pacote fixado estiver resolvível localmente, o equivalente na pasta da composição é `npx --no-install hyperframes render --output "<projeto>/render/master.mp4" --fps 30`; confirme `--version` = 0.9.40. `render`, `--output`, `--fps`, `lint`, `check` e `preview` foram conferidos no código da tag. Preview não comprova render, e check não comprova escuta humana. O runtime pode precisar de browser/FFmpeg: qualquer instalação/download de sistema requer o consentimento descrito em [setup](setup.md); um comando que tenta baixar dependência deve ser interrompido até essa confirmação.

Confira arquivo não vazio, dimensão, fps e duração com `ffprobe`; examine quadros decodificados e transições. Preserve o render anterior em vez de sobrescrever evidência já revisada. Atualize o manifesto/tool_plan antes de entregar e revisar.

```sh
python "<skill-dir>/scripts/captions.py" ass "<projeto>"
python "<skill-dir>/scripts/deliver.py" "<projeto>" --video render/master.mp4
python "<skill-dir>/scripts/review.py" "<projeto>" --producer-id <id-do-autor>
python "<skill-dir>/scripts/review.py" "<projeto>" --verdict
```

Acrescente as opções de mix/legendas descritas acima conforme as camadas reais. `deliver.py` gera `out/<slug>.mp4` e `delivery.json`; é **esse arquivo final** que `review.py` usa por padrão. Alterar composição/render depois exige nova entrega e evidência vinculada por hash. Sem áudio/vídeo perceptual no runtime, entregue tecnicamente e encaminhe a ficha humana, conforme [revisão](review.md).

## Fontes conferidas

Documentação oficial vinculada pelo [repositório](https://github.com/heygen-com/hyperframes), consultada no snapshot [v0.9.40](https://github.com/heygen-com/hyperframes/tree/v0.9.40) (`f5476851dd8c4da75bb56eeffad4b37beeba44e8`):
- [Composições, template e timeline](https://github.com/heygen-com/hyperframes/blob/v0.9.40/docs/concepts/compositions.mdx).
- [Schema HTML, duração e áudio](https://github.com/heygen-com/hyperframes/blob/v0.9.40/docs/reference/html-schema.mdx) e [determinismo](https://github.com/heygen-com/hyperframes/blob/v0.9.40/docs/concepts/determinism.mdx).
- [Render](https://github.com/heygen-com/hyperframes/blob/v0.9.40/packages/cli/src/commands/render.ts), [lint](https://github.com/heygen-com/hyperframes/blob/v0.9.40/packages/cli/src/commands/lint.ts), [check](https://github.com/heygen-com/hyperframes/blob/v0.9.40/packages/cli/src/commands/check.ts), [preview](https://github.com/heygen-com/hyperframes/blob/v0.9.40/packages/cli/src/commands/preview.ts).

Não foram executados comandos Node/render nesta revisão documental. Flags adicionais, qualidade, codecs ou hooks fora dos contratos citados: **confirmar com `npx hyperframes --help`** (e `<comando> --help`) na versão instalada antes de usar.
