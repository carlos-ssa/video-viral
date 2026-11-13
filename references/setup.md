# Instalação seletiva do stack v2

Execute comandos com caminhos absolutos ou a partir da pasta desta skill. `VIDEO_VIRAL_NO_INSTALL=1` impede instalar. Não reative skills arquivadas ou instale motores fora de `assets/stack.json`.

- `python scripts/setup_tools.py base`: FFmpeg/ffprobe e Node.
- `python scripts/setup_tools.py hyperframes`: stack Node v2 com package.json/package-lock fixados, em ~/.video-viral/node-v2. Inclui o compositor e os módulos JS selecionados, mais infraestrutura de build/browser. Não sobrescreve um package.json estranho.
- `python scripts/setup_tools.py voz`: Kokoro e dependências próprias, inclusive espeak-ng usado pela fonetização; ele não é um segundo TTS de reserva.
- `python scripts/setup_tools.py legendas`: faster-whisper; não instala outro transcritor/alinhador.
- `python scripts/setup_tools.py blender`: Blender.
- `python scripts/setup_tools.py comfyui`: runtime ComfyUI em ambiente próprio, sem checkpoints. Adicionar somente os modelos/nós necessários ao workflow e registrar as versões/licenças.

`VIDEO_VIRAL_NODE_ROOT` aponta à raiz npm. `VIDEO_VIRAL_BROWSER_PATH` aponta a um Chrome/Edge instalado; os adaptadores não baixam um navegador. Não misturar pacotes Node v1 e v2 silenciosamente. Para um projeto isolado, copiar assets/node/package.json e package-lock.json e executar npm ci --ignore-scripts --no-audit --no-fund nessa pasta.

Kokoro e faster-whisper usam venvs separadas sob ~/.video-viral/venvs. ACE-Step 1.5 deve ser configurado conforme o perfil real de hardware e expor sua API; music.py é cliente, não instalador de pesos. Blender MCP é configurado no cliente do agente separadamente, com o addon ativo. Não inventar disponibilidade com base no catálogo.

Diagnóstico: `python scripts/check_env.py` e `python scripts/stack.py doctor --node-root <pasta>`. Detectado não significa testado. CPU/GPU, tempo e memória dependem do módulo; apenas um modelo pesado de GPU por vez no perfil de 8 GB.

## Quando faltar algo

Voz: fornecer WAVs e usar voice.py --from-wavs. Legendas: importar SRT/VTT ou usar estimate com tempos declarados aproximados. Sem HyperFrames, pode haver base/rascunho FFmpeg, nunca declará-lo acabamento profissional aprovado. Sem workflow ComfyUI ou API musical, entregar o plano/ativos disponíveis e relatar a etapa bloqueada. Não baixar modelos repetidamente para tentar mudar a nota.

Com VIDEO_VIRAL_NO_INSTALL, voz/transcrição usam somente pesos já em cache. Para CPU explícita em narração: voice.py <projeto> --device cpu. Isso não troca o motor de voz.
