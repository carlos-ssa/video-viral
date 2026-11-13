# Instalação seletiva do stack v2

Execute comandos com caminhos absolutos ou a partir da pasta desta skill. `VIDEO_VIRAL_NO_INSTALL=1` bloqueia instalações pelos scripts da skill, **não os downloads da CLI HyperFrames**. Não reative skills arquivadas ou instale motores fora de `assets/stack.json`.

## Consentimento antes da instalação

Rode o grupo necessário **sem flags de consentimento** primeiro. O script diagnostica sem subprocessos de instalação e lista programa, gerenciador e tamanho aproximado quando conhecido. Havendo ações protegidas, sai com **4 antes de instalar qualquer grupo**. Apresente essa lista inteira ao usuário e peça uma confirmação única; só depois use as flags correspondentes ao escopo aceito. Pedido explícito para não instalar prevalece: apenas informe a lista, sem tentar obter exceção.

- `--allow-system`: programas via winget (inclui modo silencioso e aceite de termos), brew ou sudo apt-get, além do bootstrap `pip install --user uv`. A flag documenta consentimento, não concede privilégios nem substitui permissões do ambiente.
- `--allow-large`: ComfyUI e torch/torchvision/torchaudio, inclusive sem checkpoints; estimativa CUDA de vários GB (3–10 GB, variável por SO/cache). Pode precisar também de `--allow-system` se faltar uv.
- Venvs e `npm ci` dedicados em `~/.video-viral` permanecem autônomos quando os pré-requisitos já existem e o usuário permite instalar. Não instalar todo o catálogo nem reativar skills removidas. Falha/recusa pede reserva documentada uma vez, com impacto informado, em vez de repetir downloads.

Exemplo, somente **após** consentimento da lista: `python scripts/setup_tools.py base comfyui --allow-system --allow-large`. Sem instalação permitida, `VIDEO_VIRAL_NO_INSTALL=1` bloqueia mesmo com ambas as flags. Códigos do instalador: 0 concluído/lista de grupos; 1 falha/proibição; 2 uso inválido; 4 consentimento pendente. Eles são separados dos códigos 0–3 de revisão.

## Grupos

- `python scripts/setup_tools.py base`: FFmpeg/ffprobe e Node.
- `python scripts/setup_tools.py hyperframes`: stack Node v2 com package.json/package-lock fixados, em ~/.video-viral/node-v2. Inclui o compositor e os módulos JS selecionados, mais infraestrutura de build/browser. Não sobrescreve um package.json estranho.
- `python scripts/setup_tools.py voz`: Kokoro e dependências próprias, inclusive espeak-ng usado pela fonetização; ele não é um segundo TTS de reserva.
- `python scripts/setup_tools.py legendas`: faster-whisper; não instala outro transcritor/alinhador.
- `python scripts/setup_tools.py blender`: Blender.
- `python scripts/setup_tools.py comfyui`: runtime ComfyUI em ambiente próprio, sem checkpoints. Adicionar somente os modelos/nós necessários ao workflow e registrar as versões/licenças.

`VIDEO_VIRAL_NODE_ROOT` aponta à raiz npm. Não misture pacotes Node v1 e v2 silenciosamente. Para um projeto isolado, copie assets/node/package.json e package-lock.json e execute npm ci --ignore-scripts --no-audit --no-fund nessa pasta **somente com instalação permitida**.

### Browser, cache e execução sem rede

- `VIDEO_VIRAL_BROWSER_PATH`: Chrome/Edge existente usado pelos adaptadores da skill; eles não baixam browser.
- `HYPERFRAMES_BROWSER_PATH`: caminho absoluto do executável usado pela **CLI HyperFrames**. A CLI não lê `VIDEO_VIRAL_BROWSER_PATH`; defina as duas quando usar ambas as rotas.
- `HYPERFRAMES_CACHE_DIR`: raiz de cache da CLI, incluindo fontes, histórico e lock de render. Use pasta curta, gravável e exclusiva do trabalho; não compartilhe lock/cache entre testes sem intenção. Isso **não desativa downloads**.

No HyperFrames 0.9.40 instalado, a CLI pode baixar Chrome e fontes mesmo com `VIDEO_VIRAL_NO_INSTALL=1`, `HF_HUB_OFFLINE=1` e `TRANSFORMERS_OFFLINE=1`. Essas variáveis não são um bloqueio de rede da CLI. Antes de lint/check/preview/render, selecione o browser existente e forneça cada fonte com `@font-face` e arquivo local (sem Google Fonts/CDN). Em Git Bash/POSIX, com caminhos reais:

```sh
export VIDEO_VIRAL_BROWSER_PATH="<Chrome-ou-Edge-existente>"
export HYPERFRAMES_BROWSER_PATH="$VIDEO_VIRAL_BROWSER_PATH"
export HYPERFRAMES_CACHE_DIR="<pasta-curta-gravavel>"
```

Se não houver permissão de rede, execute sob bloqueio de saída do ambiente, sem alterar políticas para contorná-lo. Cache vazio não é autorização para baixar; tentativa de download ou dependência ausente exige PARAR e avisar. Não há flag offline universal documentada aqui. Para falha de captura com browser existente, use a [reserva por screenshot](composition.md#reserva-por-screenshot).

Kokoro e faster-whisper usam venvs separadas sob ~/.video-viral/venvs. ACE-Step 1.5 deve ser configurado conforme o perfil real de hardware e expor sua API; music.py é cliente, não instalador de pesos. Blender MCP é configurado no cliente do agente separadamente, com o addon ativo. Não inventar disponibilidade com base no catálogo.

Diagnóstico: `python scripts/check_env.py` e `python scripts/stack.py doctor --node-root <pasta>`. Detectado não significa testado. CPU/GPU, tempo e memória dependem do módulo; apenas um modelo pesado de GPU por vez no perfil de 8 GB.

## Quando faltar algo

Se a voz pt-BR do Kokoro não atender, a rota oficial é fornecer narração gravada ou gerada fora em `audio/scenes/<id>.wav` e executar `voice.py <projeto> --from-wavs`. Registre origem/licença/consentimento; isso importa áudio, sem adicionar TTS ao catálogo.
No narrado sem ComfyUI configurado, tente na ordem: ativos fornecidos → cenas 2D/tipografia/3D do stack → relatar a etapa bloqueada se a necessidade essencial continuar. Preserve a direção sem inventar disponibilidade de imagem.

Legendas: importe SRT/VTT ou use estimate com tempos declarados aproximados. Sem HyperFrames, pode haver base/rascunho FFmpeg, nunca acabamento profissional aprovado. Sem API musical, aceite somente reserva procedural **identificada como reserva**, quando disponível e adequada ao pedido, ou falha com orientação para configurar ACE-Step/fornecer faixa autorizada; veja [música](formats/musica.md). Não anuncie geração ACE-Step nem música equivalente ao pedido sem ela. Não baixe modelos repetidamente para tentar mudar a nota.

Com VIDEO_VIRAL_NO_INSTALL, voz/transcrição usam somente pesos já em cache. Para CPU explícita em narração: voice.py <projeto> --device cpu. Isso não troca o motor de voz.

## Versões Python e ComfyUI

`setup_tools.py` lê `assets/python/requirements-*.txt`, `constraints-comfyui.txt` e `comfyui.json`. Python alvo: 3.12. As versões diretas foram confirmadas como existentes, não instaladas/testadas em GPU nesta mudança:

| Pacote | Pin | Fonte consultada |
|---|---|---|
| faster-whisper | 1.2.1 | [PyPI](https://pypi.org/pypi/faster-whisper/1.2.1/json) |
| kokoro | 0.9.4 | [PyPI](https://pypi.org/pypi/kokoro/0.9.4/json) |
| soundfile | 0.13.1 | [PyPI](https://pypi.org/pypi/soundfile/0.13.1/json) |
| numpy | 1.26.4 | [PyPI](https://pypi.org/pypi/numpy/1.26.4/json) |
| torch / torchaudio | 2.8.0 / 2.8.0 | [torch](https://pypi.org/pypi/torch/2.8.0/json), [torchaudio](https://pypi.org/pypi/torchaudio/2.8.0/json) |
| torchvision (ComfyUI) | 0.23.0 | [PyPI](https://pypi.org/pypi/torchvision/0.23.0/json), requer torch 2.8.0 |
| nvidia-cublas-cu12 | 12.8.4.1 | [PyPI](https://pypi.org/pypi/nvidia-cublas-cu12/12.8.4.1/json) |
| nvidia-cudnn-cu12 | 9.10.2.21 | [PyPI](https://pypi.org/pypi/nvidia-cudnn-cu12/9.10.2.21/json) |
| ComfyUI | v0.3.60, b8730510db30c8858e1e5d8e126ef19eac395560 | [Ref oficial](https://api.github.com/repos/Comfy-Org/ComfyUI/git/ref/tags/v0.3.60) |

Torch CUDA usa o índice cu128 já previsto pelo script; disponibilidade de wheel para cada SO/hardware deve ser conferida na instalação consentida. Requirements ComfyUI são lidos do commit fixado com constraints dos pins diretos; checkout existente divergente/sujo é preservado e pede migração manual. Venvs existentes recebem os pins de novo, em vez de tratar import bem-sucedido como versão validada.

Isto não é lock completo das dependências transitivas: uv bootstrap, misaki/transformers e demais requisitos upstream conservam suas restrições originais; não foi verificada uma resolução completa nem versões de modelos/checkpoints. Conserve esses limites no relato, sem anunciar reprodutibilidade binária de Python/GPU.
