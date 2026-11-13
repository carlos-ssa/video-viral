# Módulos executáveis e contratos

`assets/stack.json` é o catálogo v2; `stack.py list` mostra IDs e entrypoints. O stack é exclusivo. O agente seleciona contribuições por cena e registra entrada, saída, versões e evidências em tool_plan.

## Som — Tone.js

```sh
node scripts/sound.mjs <projeto> --spec edit/sound.json --node-root <raiz-npm>
```

A spec contém duration (segundos), seed e events: [{"type":"whoosh","at":1,"duration":0.4,"gainDb":-18}]. Tipos: whoosh, impact, pop, riser e pulse. A saída padrão é audio/sound-design.wav com receipt JSON. A geração é offline, não reprodução ao vivo; não sobrescreve resultado existente. deliver.py inclui essa faixa automaticamente; --sfx seleciona outra faixa. Não duplique efeitos já mixados no master.

O review não exige `kind:"sfx"`: reconhece `audio/sound-design.wav`, conteúdo em `audio/sfx/` e ativos por nome (`sound-design`, `sfx`, `foley`, `effects`, `efeitos`) ou `kind`/`role` de efeito (`sfx`, `sound-design`, `foley`, `effect`, `efeito`). Para nome personalizado, use por exemplo `{"path":"audio/transicoes.wav","kind":"audio","role":"sfx"}`. Esse registro declara a função, não comprova qualidade nem mix; efeitos planejados em prosa não comprovam ativo. Exemplo para som próprio realmente gerado:

```json
{"path":"audio/sound-design.wav","kind":"sfx","source":"Tone.js local; edit/sound.json; textura e contatos sintetizados, não gravação de ambiente real","license":"Síntese original deste projeto; sem amostras externas","commercial_ok":true}
```

### Reserva de ambiente e Foley sintetizados

Sem gravação/ativo autorizado, crie uma **textura estilizada de reserva**, nunca anuncie chuva, rua, madeira ou musgo realista. Em `edit/sound.json`, use a duração medida `D`, uma seed fixa da receita e eventos `whoosh` sobrepostos: início a cada **1,5 s**, duração **min(3, D − at) s**, `gainDb:-24` sob fala ou `-18` sem fala. Comece em 0, termine em D e omita eventos com duração ≤0. Acrescente `pop` de **0,12 s / −28 dB** no contato leve, `impact` de **0,18 s / −26 dB** no contato grave e `whoosh` de **0,4 s / −29 dB** no deslocamento, sempre ancorados à imagem e contidos em D. São parâmetros de síntese, não LUFS finais; os tipos atuais usam osciladores e não modelam ambientes físicos.

Gere pela CLI acima, registre a origem/licença do áudio (o caminho padrão é reconhecido mesmo com `kind:"audio"`) e escute a mix; ajuste ganho/densidade conforme [composição](composition.md#regras-de-acabamento-obrigatórias). A textura pode soar tonal: se não cumprir a função sensorial/realista, PARE e solicite áudio adequado, ou ofereça demonstração sintética identificada. Não preencha falta de Foley com quatro estalos separados por silêncio.

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

O cliente usa release_task, query_result e o endpoint de áudio da mesma origem. Opcional ACE_STEP_API_KEY por ambiente, sem gravar o segredo. Timeout/falha/resposta incompleta não geram sucesso fictício; arquivo anterior é preservado. O serviço e os pesos precisam ser configurados à parte. Sem serviço, a reserva real é `python scripts/music.py <projeto> --backend procedural --duration 30 --seed 7`: dispensa `--endpoint`/`--prompt`, sintetiza cama instrumental tonal sem interpretar prompt e registra `fallback:true`, `backend:"procedural"`, seed e duração no ativo (padrão `audio/music.wav`). Aceita 10–600 s; não oferece canto nem geração ACE-Step. Se inadequada, siga a falha orientada em [música](formats/musica.md). Registre a licença real antes de --commercial-ok. O contrato de API foi testado com servidor simulado; isso não comprova uma geração musical local.

## Voz e legendas

`voice.py` usa Edge TTS online ou WAVs fornecidos. Padrões: português `pt-BR-ThalitaMultilingualNeural`, inglês `en-US-AvaMultilingualNeural`, ambas com `speed: 1.2` → `rate: +20%`. `new_project.py --lang en-US` escolhe Ava; `--voice` substitui a escolha, inclusive para outros idiomas (consulte `python -m edge_tts --list-voices`). O manifesto guarda `voice.engine: "edge-tts"`, `voice.voice` e `voice.speed`. A síntese envia o roteiro ao serviço Microsoft; o MP3 recebido vira WAV mono PCM 48 kHz e os tempos medidos alimentam cenas/legendas. Não acelere o áudio de novo na entrega.

```sh
python scripts/voice.py <projeto>
python scripts/voice.py <projeto> --voice en-US-AvaMultilingualNeural --speed 1.2
python scripts/voice.py <projeto> --from-wavs
```

`--from-wavs` monta `audio/scenes/<id>.wav` sem chamar o serviço ou instalar TTS e preserva os registros de origem/licença fornecidos. Em falha de rede/voz, não troca de motor; preserva os WAVs anteriores se a síntese/conversão de alguma cena falhar. `VIDEO_VIRAL_NO_INSTALL` bloqueia instalações, não a síntese online com pacote existente; para trabalho sem rede use WAVs externos. Configurações antigas `voice.engine: "kokoro"` são migradas aos padrões do idioma e +20% ao regenerar; opções explícitas prevalecem. IDs antigos de módulo são atualizados, mas descrições livres do `tool_plan` devem ser conferidas.

A licença LGPL-3.0 do cliente não licencia automaticamente a saída do serviço Microsoft. `voice.py` registra a fonte e deixa `commercial_ok: false` por padrão; confirme os termos reais com `--license "<termos aplicáveis ao áudio>" --commercial-ok` quando verificados. A entrega monetizada mantém o portão de licenças; `--draft` em `deliver.py` permite a prévia identificada.

`captions.py transcribe` usa faster-whisper; import lê SRT/VTT, estimate marca aproximação e ass gera a camada de legenda. align é um comando legado que explica a migração, sem instalar outro motor. Scripts de apoio não autorizam adicionar novos provedores ao stack.

```sh
python scripts/captions.py ass <projeto> --words 3 --script-text <roteiro.txt>
```

`--script-text` lê TXT UTF-8 como fonte explícita de grafia/pontuação e numerais; também vale em transcribe/import/estimate. Conserva os tempos reconhecidos, recupera grafia de palavras correspondentes e pode trocar numerais falados por algarismos entre âncoras; não alinha áudio nem insere fala omitida pelo ASR. Em `ass`, não regrava `words.json`: salva os grupos em `captions/captions.json` e o ASS em `captions/captions.ass`.

A segmentação lê `video.json.captions`: `words_per_group` (padrão 3, meta, não corte rígido), `max_chars_per_line` (32), `max_lines` (2, aceita 1 ou 2), `min_duration` (0,6 s), `max_cps` (24 caracteres/s) e `pause_threshold` (0,45 s). `--words` substitui somente a meta de palavras, não esses limites. Frases/pontuação final e `jump` separam blocos; pausas são fronteiras preferidas, sem isolar a última palavra. Equilibra linhas e penaliza órfãs, mas não é análise sintática: revise cada quebra. Se texto/tempos não comportarem os limites, falha pedindo revisão, em vez de produzir legenda rápida demais.

O review já mede cauda morta, silêncio interior, proporção audível e ocupação do quadro e avisa sobre ausência de cama sonora. Dispensa de cama: `"music":{"bed_waiver":"Justificativa editorial não vazia"}`; não dispensa silêncio/cauda. Veja [gates e limiares reais](review.md#gates-instrumentados-e-limites). Colisão de textos continua sendo checagem obrigatória do revisor, sem gate automático confiável.

## IDs no planejamento

Projetos v2 mantêm `stack.compositor: hyperframes` e `stack.modules` com os IDs usados (incluindo hyperframes, gsap e ffmpeg). Cada entrada de tool_plan informa `module` com ID do catálogo, além de ferramenta, contribuição, status, entrada e saída. plan.py rejeita motores fora desse catálogo; projetos anteriores sem essa marcação continuam legíveis.

Para transição entre imagens reais, use visual_scene.mjs --module gl-transitions com --image-a <arquivo> --image-b <arquivo>. Os arquivos são copiados à cena e ajustados sem distorção; sem essas entradas, a saída é só a demo de cores.
