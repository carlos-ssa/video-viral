# Stack exclusivo — versão 2.0.0

O compositor final de produções completas é HyperFrames + GSAP. FFmpeg/ffprobe prepara, mixa, exporta e mede. Use módulos de cena/áudio quando contribuírem à direção; uma demo ou pacote instalado não equivale a um vídeo profissional validado.

| Componente | Papel | Entrada executável/documentação |
|---|---|---|
| [HyperFrames](https://github.com/heygen-com/hyperframes) | composition | `assets/node/package.json` |
| [GSAP](https://github.com/greensock/GSAP) | motion | `assets/node/package.json` |
| [FFmpeg + ffprobe](https://github.com/FFmpeg/FFmpeg) | delivery | `scripts/deliver.py` |
| [Three.js](https://github.com/mrdoob/three.js) | 3d | `assets/node/package.json` |
| [Blender](https://github.com/blender/blender) | 3d | `references/modules/3d.md` |
| [Tone.js](https://github.com/Tonejs/Tone.js) | sound | `scripts/sound.mjs` |
| [gl-transitions](https://github.com/gl-transitions/gl-transitions) | transitions | `scripts/visual_scene.mjs` |
| [ComfyUI](https://github.com/Comfy-Org/ComfyUI) | images | `scripts/comfy.py` |
| [PixiJS](https://github.com/pixijs/pixijs) | 2d | `scripts/visual_scene.mjs` |
| [Paper.js](https://github.com/paperjs/paper.js) | vector | `scripts/visual_scene.mjs` |
| [p5.js](https://github.com/processing/p5.js) | generative | `scripts/visual_scene.mjs` |
| [MCP for Blender](https://github.com/ahujasid/mcp-for-blender) | automation-3d | `references/modules/3d.md` |
| [glTF Transform](https://github.com/donmccurdy/glTF-Transform) | optimization-3d | `scripts/gltf.mjs` |
| [ACE-Step 1.5](https://github.com/ace-step/ACE-Step-1.5) | music | `scripts/music.py` |
| [Edge TTS](https://github.com/rany2/edge-tts) | voice | `scripts/voice.py` |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | captions | `scripts/captions.py` |

PixiJS, Paper.js e p5.js são alternativas por linguagem, não três dependências criativas obrigatórias em cada cena. Blender MCP é ponte para um Blender configurado; também é possível produzir em Blender headless. glTF Transform otimiza GLB para a cena Three.js. O ACE-Step usado é o 1.5, com serviço/modelo configurado separadamente.

## Status honesto

`stack.py doctor` informa detecção de pacote/programa, sem declarar render validado. Cada execução gera artefatos/receipts; só registrar validado-neste-projeto após conferir a saída. O gerador visual cria cenas de smoke editáveis, não resolve a direção do filme inteiro. Os clientes ComfyUI/ACE-Step não instalam modelos nem garantem que qualquer workflow/geração esteja disponível.

## Pesquisa e ativos

Pesquisa usa a ferramenta web já disponível e fontes como Google Trends; não adiciona um motor de produção nem instala outro repositório. Não há downloader dedicado no stack. Ativos fornecidos entram por arquivos, voz pode vir pronta ou por Edge TTS, e legendas por faster-whisper/importação. Modelos/checkpoints de workflows têm termos próprios; registrar os reais.

Veja [módulos](modules.md), [instalação](setup.md), [pipeline](pipeline.md) e [fontes](sources.md).
