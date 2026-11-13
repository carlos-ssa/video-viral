# Ferramentas

Cada repositório tem um papel. Use o padrão da etapa e só traga uma alternativa quando o pedido precisar dela; cada ferramenta a mais é instalação, VRAM e ponto de falha. Licenças e requisitos foram conferidos em 12/11/2026; confira o LICENSE do repositório antes de uso comercial.

## Encontrar

| Repositório | Papel | Licença e requisitos | Use quando |
|---|---|---|---|
| [exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server) | Busca o que está em alta no nicho na semana | Servidor MCP; exige chave da Exa (serviço remoto, tem plano gratuito) | Pesquisa de tendência. Sem chave, use a busca web da CLI |
| [yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) | Metadados e legendas dos shorts que performam | Unlicense | Estudar ganchos, duração e estrutura. Use `--skip-download`; ver [pipeline](pipeline.md#1-encontrar) |

## Escrever

| Repositório | Papel | Use quando |
|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | Skills oficiais de exemplo; esta skill segue o mesmo formato | Sempre que quiser outra skill de apoio (por exemplo, `skill-creator` para evoluir esta). O roteiro em si segue [writing.md](writing.md) |

## Voz

| Repositório | Papel | Licença e requisitos | Use quando |
|---|---|---|---|
| [hexgrad/kokoro](https://github.com/hexgrad/kokoro) | Narração local, padrão | Apache-2.0; 82M parâmetros, roda até em CPU; pt-BR com `lang_code="p"` e vozes `pf_dora`, `pm_alex`, `pm_santa`; exige `espeak-ng` | Padrão para narração |
| [resemble-ai/chatterbox](https://github.com/resemble-ai/chatterbox) | Voz expressiva, clonagem e dublagem | MIT; modelo multilíngue com pt-BR; mais pesado que o Kokoro (conte com ~6 GB de VRAM); saída com marca d'água PerTh | Emoção controlada, voz do próprio usuário (com consentimento) ou versão do short em outro idioma |
| [m-bain/whisperX](https://github.com/m-bain/whisperX) | Tempo de cada palavra para as legendas | BSD-2; alinhamento wav2vec2 com modelo de português | Padrão para legendas: alinha o roteiro conhecido ao áudio |
| [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Transcrição com tempo por palavra | MIT; leve, CUDA ou CPU | Quando o WhisperX não instalar, ou para áudio sem roteiro (gravação própria) |

## Trilha e efeitos

| Repositório | Papel | Licença e requisitos | Use quando |
|---|---|---|---|
| [Tonejs/Tone.js](https://github.com/Tonejs/Tone.js) | Sintetizadores, batidas e efeitos sonoros gerados em código | MIT; roda no navegador, inclusive renderização offline | Padrão para efeitos (whoosh, pop, tique) e bases simples; o resultado é todo seu |
| [ace-step/ACE-Step](https://github.com/ace-step/ACE-Step) | Música gerada por IA | Versão 1.5 sob MIT (a original era Apache-2.0); relatos de 4 a 8 GB de VRAM | Trilha musical em vídeo monetizado |
| [facebookresearch/audiocraft](https://github.com/facebookresearch/audiocraft) (MusicGen) | Música gerada por IA | Código MIT, **pesos CC-BY-NC 4.0** | Só em vídeo não monetizado; marque `commercial_ok: false` |

## Construir (visual)

| Repositório | Papel | Licença e requisitos | Use quando |
|---|---|---|---|
| [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | Compõe e renderiza o vídeo a partir de HTML, determinístico (Chrome headless + FFmpeg) | Apache-2.0; Node 22+ e FFmpeg; tem skills próprias (`npx skills add heygen-com/hyperframes`) | **Motor padrão.** Títulos, legendas animadas, gráficos, cenas 2D e 3D web |
| [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | Motor de vídeo em React | Licença própria: grátis para indivíduos e empresas de até 3 pessoas; acima disso, licença paga | Quando o usuário já usa React/Remotion. Há template `remotion-to-hyperframes` para migrar |
| [blender/blender](https://github.com/blender/blender) | Cenas 3D completas, render em Eevee | GPL (o vídeo renderizado é seu) | Personagens, objetos e câmera 3D que o Three.js não resolve bem |
| [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp) | O modelo monta e anima a cena no Blender aberto | MIT; addon no Blender + `uvx blender-mcp` | Montagem interativa. Para render reproduzível, prefira script `bpy` em modo headless |
| [Tencent-Hunyuan/Hunyuan3D-2](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) | Imagem vira objeto 3D | Licença comunitária Tencent: **exclui UE, Reino Unido e Coreia do Sul**; limite de usuários para uso comercial. Em 8 GB, só `Hunyuan3D-2mini`, forma sem textura | Props 3D sob medida a partir de uma imagem do ComfyUI |
| [donmccurdy/glTF-Transform](https://github.com/donmccurdy/glTF-Transform) | Otimiza GLB (malha, texturas) | MIT; Node | Antes de levar um modelo do Hunyuan3D/Blender para o Three.js |
| [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI) | Imagens, fundos e capas | GPL-3.0; API local em `127.0.0.1:8188`. Em 8 GB, modelos SDXL ou quantizados. A licença de cada checkpoint é separada | Fundos, ilustrações, imagem de entrada do Hunyuan3D e capa |
| [obsproject/obs-studio](https://github.com/obsproject/obs-studio) | Gravação de tela | GPL; operação manual | Tutoriais e demonstrações de software; o usuário grava, a skill edita |

### Bibliotecas dentro da composição (HyperFrames ou Remotion)

Escolha a menor que resolve a cena. Todas precisam respeitar a regra de animação determinística do SKILL.md. Princípios de animação, receitas e a ponte `drawAt(t)` estão em [motion graphics](motion.md).

| Repositório | Para quê | Cuidado no render |
|---|---|---|
| [juliangarnier/anime.js](https://github.com/juliangarnier/anime.js) | Linha do tempo de animações | Crie a linha do tempo pausada e posicione pelo tempo do quadro |
| [pmndrs/react-spring](https://github.com/pmndrs/react-spring) | Molas em React | Depende do relógio real; no Remotion use `spring()` |
| [pixijs/pixijs](https://github.com/pixijs/pixijs) | 2D acelerado por GPU, muitos sprites | Desligue o ticker automático e renderize por quadro |
| [processing/p5.js](https://github.com/processing/p5.js) | Efeitos generativos | `noLoop()` e `randomSeed()`; desenhe a partir do tempo |
| [paperjs/paper.js](https://github.com/paperjs/paper.js) | Caminhos vetoriais, traços que se desenham | Calcule o progresso pelo tempo, não por `onFrame` |
| [liabru/matter-js](https://github.com/liabru/matter-js) | Física 2D | `Engine.update(engine, 1000/fps)` uma vez por quadro, nunca o `Runner` |
| [mrdoob/three.js](https://github.com/mrdoob/three.js) | Cenas 3D no navegador | Sem `setAnimationLoop`; renderize a cena no tempo pedido |
| [dimforge/rapier](https://github.com/dimforge/rapier) | Colisões e física 3D | Passo fixo por quadro; pré-simule se precisar posicionar no meio |
| [oframe/ogl](https://github.com/oframe/ogl) | Shaders leves | Passe o tempo do quadro como uniform |
| [tsparticles/tsparticles](https://github.com/tsparticles/tsparticles) | Partículas (confete, poeira, faíscas) | Fixe a semente; o motor é baseado em relógio, então prefira em trechos curtos e confira o render |
| [gl-transitions/gl-transitions](https://github.com/gl-transitions/gl-transitions) | Transições entre cenas em shader | Progresso da transição vem do tempo do quadro |

## Editar e entregar

| Repositório | Papel | Use quando |
|---|---|---|
| [FFmpeg/FFmpeg](https://github.com/FFmpeg/FFmpeg) | Mixagem, legendas queimadas, volume, codificação e checagens | Sempre, via `scripts/deliver.py`. Para outras edições, a skill `ffmpeg-skill`, se instalada |
| [OpenCut-app/OpenCut](https://github.com/OpenCut-app/OpenCut) | Editor de linha do tempo com interface | Quando o usuário quiser retocar à mão; a skill entrega `render/master.mp4` e o áudio separado |
