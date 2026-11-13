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

`data-composition-id` identifica a raiz; a chave em `window.__timelines` deve ser igual. `data-width/height/duration` definem o quadro e a duração total; `data-fps` define o padrão usado pelo render quando a flag falta. `class="clip"`, `data-start` e `data-duration` delimitam a janela dos elementos; `data-track-index` organiza pistas do editor, não resolve sobreposição nem substitui CSS/z-index. **Não anime `autoAlpha`, `visibility` ou `display` na própria `.clip`**: o runtime controla sua visibilidade. Anime `opacity`/transformação num filho, com estado inicial/final explícito. Direcione fontes, hierarquia e área segura; o exemplo não é acabamento pronto.

## Regras de acabamento obrigatórias

Aplique ao render final; lint/check não medem fidelidade ao formato nem substituem inspeção audiovisual.

- **Quadro vertical:** fundo/cenário até as quatro bordas. Em 1080×1920, faça palco/imagem principal ocupar **≥70% da altura (1344 px)**, inclusive atrás das camadas editoriais; não comprima a ação num cartão superior deixando 30–55% inferior vazio. Preserve detalhes essenciais entre **x=90–930 e y=250–1500** (evite os 150 px da direita e 420 px inferiores da UI). Cenário pode sangrar; rosto, ação, números e CTA não. Verifique a UI real do destino.
- **Caixas sem colisão:** reserve para legenda uma faixa exclusiva, por exemplo **x=90–930, y=1280–1500**, com **220 px** de altura para duas linhas, padding e contorno. Coloque rótulos fixos, referência bíblica, rodapé, fonte e CTA fora dela, com **≥24 px** entre caixas visíveis. Nenhum texto pode sair de sua caixa nem cruzar outro; confira o quadro com a legenda mais longa de duas linhas, não só a curta.
- **Legenda por sentido:** quebre por frase/pontuação e unidade sintática, não só por contagem de palavras. Use no máximo duas linhas; não deixe palavra órfã nem artigo/preposição desligados do complemento. Corrija a transcrição visual de numerais/referências para algarismos: **“Neemias 2:17–18”**, não “Neemias dois, dezessete”. Preserve a fala original e os tempos medidos; agrupar/corrigir texto não autoriza inventar fala. `words_per_group`/`--words` são uma meta, não um corte rígido. O segmentador considera frases, pausas, cortes e limites de leitura; veja os campos reais e `--script-text` em [voz e legendas](modules.md#voz-e-legendas). A fonte textual corrige grafia/numerais, não alinha áudio nem recupera fala omitida; revise os blocos no HTML/ASS gerado antes da entrega.
- **Tamanho e títulos:** em 1080×1920 use legenda **≥48 px**; em 1920×1080, **≥42 px**, entrelinha **≥1,15**. Escale proporcionalmente em outras resoluções. Equilibre títulos: a última linha deve ter **≥2 palavras e ≥35% da largura da maior linha**; reescreva ou refaça a quebra, sem reduzir abaixo do tamanho legível para encaixar.
- **Fonte e escrita:** forneça `@font-face` local para família/peso usados; aguarde `document.fonts.ready`, confira `document.fonts.check('700 48px "NomeDaFonte"', 'ÁÉÍÓÚãç')` e o status `loaded` da face declarada. `check()` sozinho pode aceitar uma substituta se a face não existir: confirme também a declaração/arquivo e a fonte efetivamente renderizada no painel de fontes do browser. Inspecione títulos/marca d'água com acentos (“IDEIAS PRÁTICAS”), sem texto-fantasma ou linha atravessando letras.
- **Um único gancho:** título, legenda e fala devem formular a mesma pergunta/promessa. Se houver pergunta, escute a entonação interrogativa; um “?” no texto não corrige voz afirmativa. Regrave ou reescreva antes de compor.
- **Cama e pausas:** mantenha música ou ambiente durante a peça, inclusive entre frases; quando a ausência de cama for decisão editorial, declare uma justificativa não vazia em `music.bed_waiver` no manifesto (ex.: `"Demonstração só com voz por intenção editorial"`) e detalhe intervalos/motivo em `research/`. O review avisa sobre cama ausente e mede silêncio interior, proporção audível, cauda morta e ocupação do quadro; a dispensa elimina só o aviso de cama, não esses gates. Limiares automáticos e limites em [revisão](review.md#gates-instrumentados-e-limites). Sem essa dispensa, não aceite silêncio total entre frases; investigue intervalos **≥0,3 s abaixo de −45 dB** na mix. Use a [reserva sonora](modules.md#reserva-de-ambiente-e-foley-sintetizados) quando adequada, sem fingir ambiente real.
- **ASMR:** mantenha ambiente/textura e fricção/ressonância audíveis em **≥80% do tempo**; não entregue estalos isolados com o resto mudo. Procure lacunas de **≥0,3 s abaixo de −45 dB** e confirme por escuta se são intencionais. Loudness com gate ignora silêncio e não comprova densidade nem qualidade sensorial.
- **Fecho sem cauda morta:** encerre junto do último som/legenda/ação, com margem **≤0,5 s**. Não prolongue música artificialmente para justificar quadro parado. Ajuste duração do HTML, cenas e mix depois de medir; confira os últimos 3 s do MP4.
- **Fidelidade:** compare três quadros e uma passagem em movimento com o formato-alvo antes do filme inteiro. Se realismo, performance, gravação ou contato essenciais faltarem, PARE e avise; uma demo vetorial/zoom pode ser **animatic**, não entrega equivalente. Só produza essa alternativa com escopo aceito e identificação explícita. Ao editar a fonte fornecida, preserve seu estilo: ser ilustração ou material sintético não impede cortes/legendas solicitados sobre esse mesmo arquivo. Registre essa natureza, sem chamá-la de filmagem real; o bloqueio se aplica à substituição por material que não cumpre o pedido.

## Tempo e módulos visuais

O runtime busca a timeline pausada em cada quadro (`t = frame / fps`); não chame `play()` para animar. Calcule todo estado pelo tempo solicitado. Evite relógio real, timers, RAF autônomo e `Math.random()` sem semente. Carregue fontes/texturas antes da captura; teste busca **2 → 0 → 2** com pixels iguais no mesmo tempo. Execute o [procedimento de quadros de estilo e seek](composition-check.md) antes do filme inteiro: ele usa `snapshot --at` e inclui comparação local de pixels e limites para vídeo/cenas aninhadas. Fontes/browser/encoder também afetam reprodutibilidade: registre versões, ambiente e parâmetros.

`visual_scene.mjs` já gera raiz `main`, clip `visual`, bundle GSAP, `drawAt(t)` e parâmetros de semente. Há duas rotas de integração:

1. **Rota simples e verificável:** adapte a cena conforme [módulos](modules.md), reconstrua seu bundle e renderize a pasta de cena com os comandos abaixo, usando saída `composition/assets/s01.mp4`. Inclua esse arquivo no filme principal como `<video id="s01" class="clip" src="assets/s01.mp4" data-start="0" data-duration="4" data-track-index="0" muted playsinline></video>`. Renderize depois a composição principal inteira; o trecho isolado não substitui esse passo.
2. **Composição editável aninhada:** o contrato oficial usa host `<div class="clip" data-composition-id="s01" data-composition-src="compositions/s01.html" data-start="0" data-duration="4" data-track-index="0"></div>`; o arquivo externo envolve conteúdo em `<template>`, usa tempos locais e registra timeline sob `s01`. Não aponte esse host diretamente ao HTML completo gerado: adapte wrapper, IDs, seletores, assets e registro `__timelines.main` para evitar colisões. Faça lint/check e inspecione cada cena montada.

O gerador também escreve `data-track-kind="graphics"` e `window.__hf.buildReady`. Eles existem no código local, mas não foram confirmados como contrato público dessa versão nas páginas consultadas. **Confirme com `python scripts/stack.py hyperframes --node-root "<node-root>" -- --help`, somente com execução da CLI permitida** e com o contrato/source de runtime 0.9.40 antes de depender desses detalhes numa composição aninhada. A rota de pré-render permite testar a cena isolada; falha de readiness deve bloquear o render, não ser anunciada como integração validada.

## Voz, legendas e ativos

A narração medida (`audio/voice.wav`) define entradas e duração das cenas. Para a rota padrão, renderize as cenas narradas **sem áudio**, deixe `deliver.py` mixar voz, música e `audio/sound-design.wav`, e mantenha legendas em ASS via `captions.py ass`. O render de A-roll pode manter seu áudio original; confira que não haja outra cópia da fala sendo mixada.

Para ouvir no preview, é possível copiar a voz para `composition/assets/voice.wav` e declarar `<audio src="assets/voice.wav" data-start="0" data-duration="4" data-volume="1"></audio>`. Áudio é extraído pelo runtime, não tocado por callbacks GSAP. Se essa faixa também estiver no master e `deliver.py` for remixar as mesmas fontes externas, use `--mute-video-audio` para descartar o áudio do master. Em gravação, preserve o áudio A-roll quando ele é a fonte única. Evite mix duplicada: `--no-music` só desativa a trilha externa, não voz/efeitos. `music.gain_db` ajusta a trilha também sem voz externa; em gravação, o ducking usa a fala embutida preservada quando não há voz externa. Confira a mix real, não deduza inteligibilidade dos parâmetros.

Legendas HTML são elementos `clip` com tempos conferidos de `captions/words.json`, dentro da área segura e fora do rosto/UI. Com elas já queimadas no master, passe `--no-captions` ao entregar. Com ASS externo, deixe a legenda fora do HTML. Registre origem/licença de imagens, fontes e áudio no manifesto; fontes locais usam `@font-face` e precisam estar carregadas no primeiro quadro.

## Checar, visualizar e renderizar (0.9.40)

Use somente o wrapper `stack.py hyperframes [--node-root <pasta>] [--screenshot] -- <comando>`, que resolve o pacote **já instalado** pelo lockfile de `assets/node` sem `npx` nem shim dependente de plataforma. `<node-root>` normalmente é `~/.video-viral/node-v2`; pode vir de `VIDEO_VIRAL_NODE_ROOT`. **Com `VIDEO_VIRAL_NO_INSTALL` não vazio, a CLI fica BLOQUEADA**, inclusive help/version e screenshot, para impedir downloads internos de Chrome/fontes. Os adaptadores Puppeteer locais continuam disponíveis, mas não substituem o render principal. Não remova a proibição nem chame a CLI diretamente para contorná-la; relate a etapa bloqueada.

Somente com execução da CLI permitida, browser/cache/fontes locais preparados conforme [setup](setup.md):

```sh
python scripts/stack.py hyperframes --node-root "<node-root>" -- --version
python scripts/stack.py hyperframes --node-root "<node-root>" -- lint "<projeto>/composition"
python scripts/stack.py hyperframes --node-root "<node-root>" -- check "<projeto>/composition"
python scripts/stack.py hyperframes --node-root "<node-root>" -- preview "<projeto>/composition"
python scripts/stack.py hyperframes --node-root "<node-root>" -- render "<projeto>/composition" --output "<projeto>/render/master.mp4" --fps 30
```

Confirme versão 0.9.40. Diretórios de projeto são posicionais; use saída absoluta. `render`, `--output`, `--fps`, `lint`, `check` e `preview` foram conferidos no código da tag. Preview não comprova render, e check não comprova escuta humana. Browser/cache local e flags de auto-instalação não garantem modo offline da CLI; qualquer tentativa de download sem permissão exige parada, conforme [setup](setup.md).

### Reserva por screenshot

Se a captura padrão falhar com o Chrome existente (incluindo o caso observado com Chrome 157), preserve o log e tente o mesmo compositor com **Page.captureScreenshot**, sem atualizar/baixar browser. A flag `--screenshot` do wrapper define `PRODUCER_FORCE_SCREENSHOT=true` e `PRODUCER_EXPERIMENTAL_FAST_CAPTURE=false`, lidas pelo engine distribuído no HyperFrames 0.9.40. Ela **não libera a CLI sob `VIDEO_VIRAL_NO_INSTALL`**; use somente com execução permitida:

```sh
python scripts/stack.py hyperframes --node-root "<node-root>" --screenshot -- \
  render "<projeto>/composition" --output "<projeto>/render/master-screenshot.mp4" --fps 30
```

Use o browser/cache previamente definidos conforme [setup](setup.md#browser-cache-e-execução-sem-rede). Registre a reserva e o motivo em tool_plan; confirme no log o caminho screenshot e inspecione os quadros do arquivo novo. Se ainda falhar, PARE com o diagnóstico; não declare render a partir de preview nem substitua silenciosamente por slideshow FFmpeg. Essa reserva muda a captura, não dispensa o render HyperFrames integral nem a revisão.

Confira arquivo não vazio, dimensão, fps e duração com `ffprobe`; examine quadros decodificados e transições. Preserve o render anterior em vez de sobrescrever evidência já revisada. Atualize o manifesto/tool_plan antes de entregar e revisar. Se usou a reserva, selecione `render/master-screenshot.mp4` em `--video` na entrega.

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

Os contratos upstream citados não equivalem a validação de um render neste ambiente. Flags adicionais, qualidade, codecs ou hooks: **confirmar com `python scripts/stack.py hyperframes -- --help`** (e `-- <comando> --help`) na versão instalada, somente quando a execução da CLI estiver permitida. Sob `VIDEO_VIRAL_NO_INSTALL`, consultar o código local em vez de contornar o bloqueio.
