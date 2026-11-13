# Módulos executáveis e contratos

`assets/stack.json` é o catálogo v2; `stack.py list` mostra IDs e entrypoints. O stack é exclusivo. O agente seleciona contribuições por cena e registra entrada, saída, versões e evidências em tool_plan.

## Som — Tone.js

```sh
node scripts/sound.mjs <projeto> --spec edit/sound.json --node-root <raiz-npm>
```

A spec contém duration (segundos), seed e events: [{"type":"whoosh","at":1,"duration":0.4,"gainDb":-18}]. Tipos: whoosh, impact, pop, riser e pulse. A saída padrão é audio/sound-design.wav com receipt JSON. A geração é offline, não reprodução ao vivo; não sobrescreve resultado existente. deliver.py inclui essa faixa automaticamente; --sfx seleciona outra faixa. Não duplique efeitos já mixados no master.

Registre efeitos e ambientes sintetizados em `video.json.assets` com **`kind:"sfx"`**, não apenas `kind:"audio"`/`"sound"`. O review reconhece `sfx` (ou arquivos em `audio/sfx/`); esse registro declara a função, não comprova qualidade nem mix. Exemplo para som próprio realmente gerado:

```json
{"path":"audio/sound-design.wav","kind":"sfx","source":"Tone.js local; edit/sound.json; textura e contatos sintetizados, não gravação de ambiente real","license":"Síntese original deste projeto; sem amostras externas","commercial_ok":true}
```

### Reserva de ambiente e Foley sintetizados

Sem gravação/ativo autorizado, crie uma **textura estilizada de reserva**, nunca anuncie chuva, rua, madeira ou musgo realista. Em `edit/sound.json`, use a duração medida `D`, uma seed fixa da receita e eventos `whoosh` sobrepostos: início a cada **1,5 s**, duração **min(3, D − at) s**, `gainDb:-24` sob fala ou `-18` sem fala. Comece em 0, termine em D e omita eventos com duração ≤0. Acrescente `pop` de **0,12 s / −28 dB** no contato leve, `impact` de **0,18 s / −26 dB** no contato grave e `whoosh` de **0,4 s / −29 dB** no deslocamento, sempre ancorados à imagem e contidos em D. São parâmetros de síntese, não LUFS finais; os tipos atuais usam osciladores e não modelam ambientes físicos.

Gere pela CLI acima, registre `kind:"sfx"` e escute a mix; ajuste ganho/densidade conforme [composição](composition.md#regras-de-acabamento-obrigatórias). A textura pode soar tonal: se não cumprir a função sensorial/realista, PARE e solicite áudio adequado, ou ofereça demonstração sintética identificada. Não preencha falta de Foley com quatro estalos separados por silêncio.

## Cenas — PixiJS, Paper.js, p5.js e gl-transitions

```sh
node scripts/visual_scene.mjs --module pixi --output <nova-pasta> --width 1080 --height 1920 --duration 4 --seed 7 --node-root <raiz-npm>
```

IDs: pixi, paper, p5 e gl-transitions. O gerador cria um projeto de cena HyperFrames com index.html, fonte do adaptador, entrada JS, bundle local e parâmetros. A cena é um smoke técnico que precisa ser dirigida/adaptada ao roteiro; não é template de acabamento final. drawAt(t) precisa funcionar em ordem arbitrária; o teste 2→0→2 não deve mudar pixels.

Adapte a fonte e reconstrua o bundle antes de renderizar. Integre no filme como uma composição com caminhos/assets resolvidos, ou renderize o trecho e leve o arquivo ao compositor principal. No segundo caso, os pixels internos só mudam ao refazer a cena de origem. Não declarar que um módulo foi usado apenas porque sua demo existe na pasta.

## Modelos 3D

`node scripts/gltf.mjs entrada.glb saida.glb --node-root <raiz-npm>` preserva a fonte e otimiza para carregamento sem exigir um decoder adicional. O receipt não aprova qualidade visual; confira materiais, geometria e animação no destino. Para criação/câmera/iluminação, use Blender/Three.js. [Fluxo 3D](modules/3d.md).

## ComfyUI

```sh
python scripts/comfy.py <projeto> --workflow <workflow-api.json> --output-node 9 --output assets/imagem.png
```

Workflow exportado em formato API, nós e checkpoints reais já disponíveis no servidor. Não aceita JSON da interface como se fosse um grafo de API. Registra hash, prompt_id e origem; não instala modelos nem inicia serviços. A extensão deve corresponder à imagem retornada. --license e --commercial-ok exigem informação real dos modelos/ativos; sem confirmação, não marcar uso comercial automaticamente. images.py é alias desse cliente. A integração atual baixa imagens; vídeo/áudio por outros nós não é anunciado como geração universal nativa.

## Música — ACE-Step 1.5

```sh
python scripts/music.py <projeto> --endpoint http://127.0.0.1:8001 --prompt "..." --duration 30 --seed 7
```

O cliente usa release_task, query_result e o endpoint de áudio da mesma origem. Opcional ACE_STEP_API_KEY por ambiente, sem gravar o segredo. Timeout/falha/resposta incompleta não geram sucesso fictício; arquivo anterior é preservado. O serviço e os pesos precisam ser configurados à parte. Sem serviço, siga a distinção entre reserva procedural identificada e falha orientada em [música](formats/musica.md), sem prometer geração ACE-Step. Registre a licença real antes de --commercial-ok. O contrato de API foi testado com servidor simulado; isso não comprova uma geração musical local.

## Voz e legendas

voice.py usa Kokoro ou WAVs fornecidos. captions.py transcribe usa faster-whisper; import lê SRT/VTT, estimate marca aproximação e ass gera a camada de legenda. align é um comando legado que explica a migração, sem instalar outro motor. Scripts de apoio não autorizam adicionar novos provedores ao stack.

## IDs no planejamento

Projetos v2 mantêm `stack.compositor: hyperframes` e `stack.modules` com os IDs usados (incluindo hyperframes, gsap e ffmpeg). Cada entrada de tool_plan informa `module` com ID do catálogo, além de ferramenta, contribuição, status, entrada e saída. plan.py rejeita motores fora desse catálogo; projetos anteriores sem essa marcação continuam legíveis.

Para transição entre imagens reais, use visual_scene.mjs --module gl-transitions com --image-a <arquivo> --image-b <arquivo>. Os arquivos são copiados à cena e ajustados sem distorção; sem essas entradas, a saída é só a demo de cores.
