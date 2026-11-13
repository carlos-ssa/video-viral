# Instalação (Windows, GPU NVIDIA)

A skill instala sozinha, sem perguntar, as etapas que o pedido usa: `python scripts/setup_tools.py <grupo...>` (base, legendas, voz, chatterbox, blender) faz os blocos abaixo e pula o que já existe; `captions.py transcribe` e `voice.py` o chamam por conta própria e trocam para a venv certa. Os comandos abaixo servem para conferir ou instalar à mão. Se o usuário pedir para não instalar, rode os scripts com `VIDEO_VIRAL_NO_INSTALL=1` e entregue com as reservas (tabela "Quando falta ferramenta" no SKILL.md); se uma instalação falhar, faça o mesmo e relate. `python scripts/check_env.py` mostra o que já existe. Cada ferramenta Python fica numa venv própria em `~/.video-viral/venvs/<nome>`, que o `check_env.py` encontra sozinho; torch e dependências conflitam entre ferramentas.

Use Python 3.11 ou 3.12 nas venvs: bibliotecas de IA costumam demorar a suportar a versão mais nova do Python.

## Base

```powershell
winget install --id Gyan.FFmpeg          # se ainda não houver ffmpeg 6.1+
winget install --id OpenJS.NodeJS        # Node 22+ para HyperFrames
winget install --id astral-sh.uv
winget install --id yt-dlp.yt-dlp
```

## Voz e legendas (venv `voz`)

```powershell
winget install --id eSpeak-NG.eSpeak-NG   # Kokoro precisa para pt-BR
uv venv $HOME\.video-viral\venvs\voz --python 3.12
& $HOME\.video-viral\venvs\voz\Scripts\Activate.ps1
uv pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128
uv pip install "kokoro>=0.9.4" soundfile numpy whisperx faster-whisper
```

Rode `voice.py` e `captions.py align` com o Python desta venv; com outro Python, `voice.py` não acha o Kokoro e cai na voz do sistema.

Rode os scripts com o Python da venv: `& $HOME\.video-viral\venvs\voz\Scripts\python.exe scripts\voice.py <projeto>`. Se o `whisperx` exigir outra versão de torch, deixe-o numa venv `legendas` separada.

## Chatterbox (venv `chatterbox`, opcional)

```powershell
uv venv $HOME\.video-viral\venvs\chatterbox --python 3.11
& $HOME\.video-viral\venvs\chatterbox\Scripts\Activate.ps1
uv pip install chatterbox-tts
```

Siga o README para o modelo multilíngue e o finetune pt-BR.

## Visual

```powershell
npx skills add heygen-com/hyperframes     # no projeto do vídeo; traz as instruções do HyperFrames
winget install --id BlenderFoundation.Blender
```

- Blender MCP: instale o addon `addon.py` no Blender e configure o servidor `uvx blender-mcp` na CLI (README do repositório).
- ComfyUI: versão portátil para Windows/NVIDIA na página de releases do repositório; baixe checkpoints compatíveis com 8 GB (SDXL ou quantizados) e confira a licença de cada um.
- Hunyuan3D-2mini: siga o README oficial ou a distribuição portátil para Windows; use o modo de pouca VRAM e só a geração de forma.
- glTF Transform: `npx @gltf-transform/cli --help` (sem instalação global).

## Trilha

- Tone.js: `npm install tone` no projeto da composição.
- ACE-Step: siga o README do repositório (tem interface local); venv própria.
- MusicGen: só para vídeos não monetizados.

## Pesquisa

- Exa MCP: precisa de chave da Exa; configure o servidor na CLI conforme o README. Sem chave, a etapa usa a busca web.
