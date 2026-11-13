# Pipeline narrado

Fluxo do vídeo feito do zero, sem gravação: canal dark, explicativo, e a base de produto, storytelling, música e avatar ([outros formatos](formats/outros.md)). Para editar uma gravação, veja [gravação própria](formats/gravacao.md); para vídeo longo em 16:9, some o guia de [vídeo longo](formats/longo.md).

## Sumário

- [Projeto e manifesto](#projeto-e-manifesto)
- [1. Encontrar](#1-encontrar)
- [2. Dirigir](#2-dirigir)
- [3. Escrever](#3-escrever)
- [4. Voz](#4-voz)
- [5. Legendas](#5-legendas)
- [6. Visual](#6-visual)
- [7. Trilha e efeitos](#7-trilha-e-efeitos)
- [8. Entregar](#8-entregar)
- [9. Revisar](#9-revisar)
- [Série de shorts](#série-de-shorts)

## Projeto e manifesto

```
<slug>/
  video.json        manifesto: única fonte de verdade entre etapas
  research/         notas, metadados e legendas estudadas
  audio/            voice.wav, scenes/sNN.wav, music.wav, sfx/
  captions/         words.json, captions.json, captions.ass
  scenes/           código das cenas (HTML, bpy, workflows do ComfyUI)
  assets/           imagens, modelos 3D, fontes, gravações
  render/           master.mp4 e clipes intermediários
  out/              entrega final, prancha e relatório
  review/           rodadas de revisão (rNN/: grade, gancho, notas, métricas)
```

Campos do `video.json` que as etapas usam:

| Campo | Quem escreve | Quem lê |
|---|---|---|
| `direction` (estilo, paleta, fontes, movimento, transições, sons) | Direção | Roteiro, visual, trilha, revisão |
| `hook`, `scenes[].narration`, `scenes[].on_screen`, `scenes[].visual` (`brief`, `shots`, `transition_out`) | Roteiro | Voz, visual, revisão |
| `scenes[].start`, `scenes[].duration` | `voice.py` (ou à mão para cena muda) | Legendas, visual |
| `voice`, `music`, `captions` | Usuário ou roteiro | Scripts das etapas |
| `assets[]` (`path`, `kind`, `source`, `license`, `commercial_ok`) | Cada etapa que cria ou traz um ativo | `deliver.py` |
| `monetized`, `platforms`, `fps`, `size` | Criação do projeto | `deliver.py` |
| `publish` (`caption`, `hashtags`, `ai_label`) | Roteiro | Usuário, na hora de postar |
| `review[]` (rodada, alertas) | `review.py` | Você, para comparar rodadas |

Ao refazer uma etapa, refaça também as que dependem dela: mudou a narração, rode voz, legendas e visual de novo.

## 1. Encontrar

Tendência com o Exa MCP (se configurado): procure o que publicaram no nicho nos últimos 7 dias, com títulos e links. Sem Exa, use a busca web.

Estude os shorts que performam sem baixar vídeo:

```sh
# 30 resultados de uma busca, com visualizações e duração
yt-dlp "ytsearch30:<tema> #shorts" --flat-playlist --print "%(view_count)s\t%(duration)s\t%(title)s\t%(url)s" > research/busca.tsv

# metadados e legendas automáticas dos melhores (sem o vídeo)
yt-dlp --skip-download --write-info-json --write-auto-subs --sub-langs "pt.*,en.*" --sub-format vtt -o "research/yt/%(id)s.%(ext)s" <urls>
```

Em `research/notas.md`, registre por vídeo: gancho (primeira frase e primeiro texto na tela), duração, estrutura em batidas, chamada final e o que se repete entre os melhores. A leitura de muitas legendas é trabalho para um modelo leve, se houver delegação. Use só como referência de padrão; não copie roteiro.

## 2. Dirigir

Siga [direction.md](direction.md): referências dos melhores shorts do nicho, um estilo com valores concretos em `direction`, 5 ganchos com nota e as suposições do pedido, tudo registrado em `research/direcao.md`. Baixe as fontes escolhidas (licença aberta) para `assets/fonts/` e registre-as em `assets`.

## 3. Escrever

Siga [writing.md](writing.md) com o gancho vencedor da direção. Preencha `hook`, `title`, `cta`, `publish` e as cenas. Cada cena tem uma ideia, uma frase falada (ou duas curtas) e um `visual.brief` e a lista `visual.shots` do [roteiro de planos](direction.md#4-roteiro-de-planos), com um evento visual a cada 1,5–3 s. Escolha `visual.engine` por cena: `hyperframes` (padrão), `blender`, `comfyui` (imagem animada no HyperFrames), `footage` (gravação do usuário).

Releia o roteiro antes de gerar voz e visual: refazer roteiro custa pouco, refazer render custa muito. Só pare para o usuário aprovar se ele pediu para ver o roteiro antes.

## 4. Voz

```sh
python scripts/voice.py <projeto>                 # Kokoro, voz e velocidade do video.json
python scripts/voice.py <projeto> --voice pm_alex --speed 1.1
python scripts/voice.py <projeto> --engine system # reserva: voz do sistema operacional
```

O padrão `--engine auto` usa o Kokoro se estiver instalado e, senão, a voz do sistema (Windows System.Speech com a voz pt-BR instalada, `say` no macOS, espeak-ng no Linux). A reserva soa robótica e entra em `assets` com `commercial_ok: null`, então um vídeo monetizado sai só com `deliver.py --draft`. Não pare para instalar: siga e proponha o Kokoro no relatório.

Grava `audio/scenes/sNN.wav`, `audio/voice.wav` e os tempos de cada cena no manifesto, e informa a duração total contra `target_seconds`. Passou do alvo: corte texto no roteiro em vez de acelerar além de 1.15.

Chatterbox (voz clonada, emoção, dublagem): gere um WAV por cena com o mesmo nome (`audio/scenes/sNN.wav`), depois rode `python scripts/voice.py <projeto> --from-wavs` para concatenar e medir os tempos sem regerar. Registre a voz de referência em `assets` com o consentimento.

## 5. Legendas

```sh
python scripts/captions.py align <projeto>        # WhisperX alinha o texto do roteiro ao áudio
python scripts/captions.py transcribe <projeto>   # sem roteiro: transcreve (WhisperX ou faster-whisper)
python scripts/captions.py estimate <projeto>     # reserva sem modelo: tempos estimados pelo texto
python scripts/captions.py ass <projeto>          # words.json -> captions.ass e captions.json
```

Sem WhisperX nem faster-whisper, use `estimate`: distribui as palavras de cada cena dentro do trecho falado do WAV da cena, pelo tamanho das palavras e pelas pausas da pontuação. As palavras saem com `"estimated": true`; ancore os planos nos `start` das cenas, não em palavras soltas.

`align` usa o texto exato do roteiro, sem erro de transcrição. `captions.json` traz grupos de palavras com tempos para legendas animadas em HTML; `captions.ass` é para queimar com FFmpeg. Use um dos dois, não ambos. Confira nomes próprios e números no `words.json`.

## 6. Visual

### HyperFrames (padrão)

Instale as skills oficiais no projeto (`npx skills add heygen-com/hyperframes`) e siga-as para escrever a composição e renderizar; elas trazem a sintaxe e os comandos atuais da CLI. Nesta skill:

- Uma composição 1080×1920 no `fps` do manifesto, com duração igual à soma das cenas.
- Cada cena começa em `scenes[].start`; o texto `on_screen` aparece junto com a fala correspondente.
- Legendas animadas em HTML a partir de `captions/captions.json`, ou deixe para o `deliver.py` queimar o `.ass`.
- Renderize sem áudio ou só com efeitos; voz e trilha entram no `deliver.py`.
- Saída em `render/master.mp4`. Renders longos vão para segundo plano.

Anime seguindo [motion.md](motion.md). Antes do render completo, gere os [quadros de estilo](direction.md#5-quadros-de-estilo) e quadros soltos das cenas novas (início, meio e fim) e confira texto, área segura e enquadramento.

### Remotion

Mesmas regras, com `useCurrentFrame()`, `interpolate()` e `spring()`. Se o usuário tem as skills `remotion:*`, siga-as. Lembre a licença (até 3 pessoas grátis).

### Blender (3D)

Prefira script `bpy` em modo headless para render reproduzível; use o Blender MCP para montar a cena interativamente e depois salve o script.

```sh
blender -b -P scenes/s03.py -- --out render/s03_ --frames 120
```

No script: resolução 1080×1920, `fps` do manifesto, Eevee, saída em sequência PNG ou MP4, `bpy.ops.render.render(animation=True)`. O clipe entra na composição do HyperFrames como vídeo da cena.

### Hunyuan3D-2mini (prop 3D a partir de imagem)

Na venv própria e com a GPU livre. Confira o README para a API atual; a forma geral é:

```python
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
pipe = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
    "tencent/Hunyuan3D-2mini", subfolder="hunyuan3d-dit-v2-mini", use_safetensors=True)
pipe(image="assets/prop.png")[0].export("assets/prop.glb")
```

Depois `npx @gltf-transform/cli optimize assets/prop.glb assets/prop.opt.glb` antes do Three.js. Registre o modelo em `assets` com a licença Tencent.

### ComfyUI (imagens)

Exporte o workflow em formato API, fixe a semente e envie para a API local: `POST http://127.0.0.1:8188/prompt` com `{"prompt": <workflow>}`, acompanhe em `/history/<prompt_id>` e baixe por `/view?filename=...`. Gere em 1080×1920 ou maior. Registre o checkpoint usado e a licença dele em `assets`.

## 7. Trilha e efeitos

- Efeitos em cada transição e revelação, do `direction.sfx` (whoosh na troca de cena, impacto na revelação, pop no texto): Tone.js renderizado com `Tone.Offline` numa página no Chrome headless, salvo como WAV em `audio/sfx/`, ou já dentro da composição.
- Música: ACE-Step, instrumental, duração da narração + 1 s, estilo coerente com o nicho. Salve em `audio/music.wav`.
- Sem voz por cima, a trilha pode subir; com voz, `deliver.py` abaixa a música sob a fala.

## 8. Entregar

```sh
python scripts/deliver.py <projeto> --video render/master.mp4
python scripts/deliver.py <projeto> --video render/master.mp4 --no-captions   # legendas já no HTML
python scripts/deliver.py <projeto> --video render/master.mp4 --music-db -20
python scripts/deliver.py <projeto> --video render/master.mp4 --draft         # ativo sem licença comercial confirmada
```

Usa `audio/voice.wav`, `audio/music.wav` e `captions/captions.ass` quando existirem. Sai com 1 se alguma checagem falhar e 2 se a licença bloquear; leia `out/report.md`. Em vídeo monetizado, bloqueia ativo com licença não comercial, com `commercial_ok` diferente de `true` ou com licença "não verificada". `--draft` entrega mesmo assim em `out/<slug>_rascunho.mp4`, marcado para não publicar.

## 9. Revisar

```sh
python scripts/review.py <projeto>                         # usa a entrega mais recente em out/
python scripts/review.py <projeto> --video render/master.mp4 --every 0.5
python scripts/review.py <projeto> --verdict               # depois de preencher as notas
```

Siga [review.md](review.md): olhe `review/rNN/hook.jpg` e `grid.jpg`, preencha as notas do `report.md` e rode `--verdict`. Código 1: corrija e faça outra rodada; 0: pronto; 3: terceira rodada sem aprovar, relate o que ficou abaixo de 4. Cada rodada fica em `review/` para comparar.

## Série de shorts

Para vários shorts do mesmo tema: um projeto por short, pesquisa compartilhada, voz e `direction` iguais em todos (mesmo `voice`, fontes, paleta, movimento e sons) e um gancho diferente por episódio, cenas reaproveitadas como componentes. Gere todos os roteiros primeiro e aprove em lote; depois rode voz e legendas de todos (CPU/GPU leve) e só então os renders, um de cada vez por causa da VRAM.
