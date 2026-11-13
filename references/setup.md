# Instalação (Windows, GPU NVIDIA)

Os comandos desta página são relativos à pasta da skill; use seu workdir ou caminhos absolutos. A skill instala autonomamente apenas as etapas necessárias ao plano, respeitando permissões do ambiente e restrições do usuário: `python scripts/setup_tools.py <grupo...>` (base, legendas, voz, chatterbox, blender) faz os blocos abaixo e pula o que já existe; `captions.py transcribe` e `voice.py` o chamam por conta própria e trocam para a venv certa. Os comandos abaixo servem para conferir ou instalar à mão. Se o usuário pedir para não instalar, rode os scripts com `VIDEO_VIRAL_NO_INSTALL=1` e entregue com as reservas (tabela de reservas abaixo); se uma instalação falhar, faça o mesmo e relate. `python scripts/check_env.py` mostra o que já existe. Cada ferramenta Python fica numa venv própria em `~/.video-viral/venvs/<nome>`, que o `check_env.py` encontra sozinho; torch e dependências conflitam entre ferramentas.

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

Google Trends: não requer instalação para URL/CSV oficial; veja [pesquisa](research.md). Não instalar clientes de endpoints internos como dependência obrigatória.

## Reservas por etapa

| Etapa indisponível | Reserva | Declaração necessária |
|---|---|---|
| Transcrição/alinhamento | Importar SRT/VTT; em narrado usar estimate; sem texto da gravação, cortar só silêncio | Tempos estimados ou cortes de vícios/retomadas não verificados precisam ser revisados |
| Kokoro/Chatterbox | Voz do sistema, quando disponível | Sem licença comercial verificada, monetizado continua rascunho; não chamar voz instrumental de escuta |
| HyperFrames/Remotion | Composição FFmpeg implementada conforme direção | Validar o acabamento real; identificar limitações de motion em vez de dar nota alta automaticamente |
| Música/efeitos gerados | Ativos permitidos do usuário ou síntese local disponível | Registrar fonte/licença e diferenças da direção; não inventar uma geração que não ocorreu |
| Avatar/lip-sync/vídeo generativo | Planejar e preparar ativos ou importar render autorizado disponível | Sem gerador validado, a geração permanece bloqueada; uma imagem estática não é avatar final |

Reavaliar a ferramenta apenas quando houver uma mudança de condição ou alternativa concreta. Não repetir instalações/renders idênticos em todas as rodadas.
