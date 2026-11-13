---
name: video-viral
description: Edita e produz vídeo para viralizar em TikTok, Instagram (Reels e feed), YouTube (Shorts e vídeo longo) e Kwai, de ponta a ponta e num único pedido, com IA local. Edita a gravação do próprio usuário (tira silêncios, vícios e retomadas, enquadra para 9:16, 16:9, 1:1 ou 4:5, põe legenda, B-roll, capítulos), tira cortes virais de vídeo longo e cria vídeo do zero para canal dark com narração, motion graphics, cenas 2D/3D, trilha e legendas palavra a palavra. Cobre também, como núcleo em construção, vídeo de produto, UGC, storytelling animado, canal de música com IA e avatar de IA. Tem direção de arte antes, exportação verificada por plataforma e rodadas de autocrítica antes de entregar. Junta FFmpeg, WhisperX, Kokoro, Chatterbox, HyperFrames ou Remotion, GSAP, Three.js, Blender, ComfyUI, ACE-Step, Exa e yt-dlp. Use sempre que o pedido envolver editar, cortar, legendar, enquadrar, roteirizar, narrar, animar, melhorar ou exportar vídeo para redes sociais, reels, TikToks, shorts, cortes, vídeo de YouTube ou uma série deles, mesmo sem citar as ferramentas. Para só converter formato ou extrair áudio de um arquivo, prefira FFmpeg direto.
---

# Vídeo para viralizar

O modelo principal decide, escreve, edita, programa cada cena e revisa o próprio trabalho; ferramentas locais fazem corte, voz, legendas, trilha, render e entrega. Todas as etapas leem e gravam o mesmo manifesto, `video.json` (projetos antigos com `short.json` continuam funcionando), para que qualquer uma possa ser refeita sozinha.

O usuário espera chegar ao vídeo com um pedido só. Vídeo sai medíocre quando ninguém decide o resultado antes e ninguém assiste antes de entregar; por isso há **direção** antes e **revisão** depois, e as rodadas de ajuste acontecem aqui, não em novos pedidos do usuário.

## Escolha o formato

| O usuário tem ou quer | Formato (`--format`) | Guia |
|---|---|---|
| Uma gravação dele para virar vídeo curto ou longo | `gravacao` | [Gravação própria](references/formats/gravacao.md) |
| Um vídeo longo (live, podcast, aula) para virar vários cortes | `corte` (o longo entra como `gravacao`) | [Cortes](references/formats/cortes.md) |
| Vídeo longo para YouTube (16:9, mais de 3 min), gravado ou narrado | `gravacao` ou `narrado` com `--aspect 16:9` | [Vídeo longo](references/formats/longo.md) junto com o guia do formato |
| Um tema ou roteiro, sem aparecer (canal dark, explicativo) | `narrado` | [Pipeline narrado](references/pipeline.md) |
| Divulgar produto, UGC, influenciador ou avatar UGC | `produto`, `ugc` | [Outros formatos](references/formats/outros.md) (núcleo, guia em construção) |
| História animada, canal de música com IA, avatar de IA | `storytelling`, `musica`, `avatar` | [Outros formatos](references/formats/outros.md) (núcleo, guia em construção) |

Formato de tela (`--aspect`): 9:16 para TikTok, Reels, Shorts e Kwai; 16:9 para YouTube; 1:1 ou 4:5 para o feed do Instagram. Uma gravação pode sair em mais de um: crie um projeto por formato de tela a partir do mesmo arquivo. Veja [plataformas](references/platforms.md).

## Antes de começar

1. Rode `python scripts/check_env.py` (só biblioteca padrão). Ele mostra quais etapas estão prontas, o que falta e a VRAM livre. **Instale sozinho, sem perguntar, o que a tarefa usa e falta**: `python scripts/setup_tools.py <grupo...>` (base, legendas, voz, chatterbox, visao, hyperframes, comfyui, blender; detalhes em [instalação](references/setup.md)). O usuário espera a skill autônoma, e `captions.py transcribe` e `voice.py` já instalam e trocam para a venv certa por conta própria. Não instale só se o usuário pedir: aí rode os scripts com `VIDEO_VIRAL_NO_INSTALL=1` e use as reservas da tabela abaixo. Se uma instalação falhar, **não pare**: siga com a reserva e relate.
2. Não pare para perguntar o que tem padrão: formato e plataformas saem do pedido e do arquivo; vertical vai para as quatro plataformas verticais; duração 30 a 45 s em vertical e o tempo que o conteúdo pedir em 16:9; idioma pt-BR; monetização sem pista conta como monetizado (a escolha mais restritiva de licença). Anote cada suposição em `research/direcao.md` e no relatório. Pergunte só o que não dá para supor sem risco, como usar a voz ou a imagem de outra pessoa.
3. Crie o projeto: `python scripts/new_project.py <slug> --title "..." --format <formato> --aspect <9:16|16:9|1:1|4:5> --dir <pasta>`. Ele monta as pastas e o `video.json` a partir de [assets/video.template.json](assets/video.template.json) e diz o próximo passo do formato.

## Fluxos

**Gravação do usuário** (`gravacao`, `corte`, `ugc` gravado): `footage.py import` (limpa o áudio) → `captions.py transcribe --model large-v3` ou `import --file legenda.srt` → `footage.py cut` (silêncios e vícios) → ler `edit/transcript.md` e ajustar `edit/edl.json` (retomadas, ordem, gancho primeiro) → `faces.py` (rastreia o rosto: enquadramento e onde a legenda não cobre o rosto) → **edição rica obrigatória** (abaixo) em HyperFrames sobre o A-roll → `deliver.py` → `review.py`. `footage.py render` + `captions.py ass` sozinhos geram só um rascunho de corte, nunca a entrega. Cortes de vídeo longo passam antes por `clips.py suggest` e `clips.py make`.

### Edição rica: obrigatória em todo vídeo, mesmo com pedido simples

O usuário quer um vídeo que impressione pela edição, não só pelo conteúdo. Um corte seco com legenda é reprovado. Use **todas** as skills e ferramentas de edição disponíveis, não só as já instaladas (instale o que faltar): `hyperframes`, `hyperframes-registry` (≈450 blocos: transições, legendas, títulos, 3D, overlays), `media-use` (recortes `remove-background`, grade `media-treatment`, efeitos sonoros, ícones e logos), `remotion`, `ffmpeg-skill`, `video`, `image`, three.js, ComfyUI (`scripts/images.py`) e Tone.js. Mínimo por vídeo vertical de 30–60 s:

1. **Enquadramento**: reenquadre pelo `edit/faces.json`; com rosto muito perto, use layout dividido (gráfico em cima, rosto embaixo) e alterne com tela cheia. Movimentos de câmera em um wrapper (punch-in só em palavras de ênfase, 0,5–0,7 s, expo.out), nunca zoom alternado mecânico.
2. **Cortes suaves**: pontos de corte no mínimo de energia do áudio (±0,15 s), fades de 10–20 ms nas emendas, keyframes a cada 1 s (`-g fps`), upscale lanczos + leve denoise/sharpen se a fonte for baixa.
3. **Gancho de 0–2 s**: título gigante atrás da cabeça (recorte com `remove-background`) ou revelação equivalente.
4. **Legendas animadas** de 2–3 palavras, uma por vez, palavra-chave colorida, fora do rosto e da UI das plataformas.
5. **Um evento visual a cada 2–4 s**: motion graphics (cards, listas cinéticas, logos das plataformas, contadores), imagens geradas no ComfyUI, B-roll ou cena 3D (three.js, ex.: celular mudando de quadrado para 9:16).
6. **3–5 tipos de transição** (whip, blur swap, glitch, flash, íris, shader do registry); no máximo um terço de cortes secos.
7. **Som**: whoosh em cada transição, pop em cada elemento que pousa, riser + impacto no clímax, música sob a voz (~0,14), mix −16 a −14 LUFS, pico ≤ −1 dBTP.
8. **Final** com revelação do título/marca e CTA.

Antes de entregar, rode `npx hyperframes check --json` e `snapshot`, olhe as tiras de quadros e dê nota honesta; se o resultado parecer "edição básica", refaça. Detalhes em [motion](references/motion.md) e [ferramentas](references/stack.md).

**Do zero** (`narrado` e os formatos gerados):

| Etapa | Como | Grava |
|---|---|---|
| 1. Encontrar | Exa MCP para tendências; `yt-dlp` só com metadados e legendas | `research/notas.md` |
| 2. Dirigir | [Direção](references/direction.md): referências, estilo com paleta, fontes, textura, movimento e som; 5 ganchos com nota | `direction`, `research/direcao.md` |
| 3. Escrever | [Roteiro](references/writing.md) com o gancho vencedor e roteiro de planos por cena (um evento visual a cada 1,5–3 s em vertical) | `hook`, `scenes[]` |
| 4. Voz | Kokoro via `scripts/voice.py`; Chatterbox para mais expressão ou voz clonada com consentimento | `audio/voice.wav`, tempos das cenas |
| 5. Legendas | WhisperX via `scripts/captions.py`; faster-whisper como reserva | `captions/words.json`, `captions.ass` |
| 6. Visual | [Motion graphics](references/motion.md) em HyperFrames (padrão) ou Remotion; Blender com Hunyuan3D-2mini para 3D; ComfyUI para imagens. Quadros de estilo antes do render completo | `render/master.mp4` |
| 7. Trilha e efeitos | Efeitos em cada transição e revelação; música com ACE-Step; MusicGen só sem monetização | `audio/music.wav`, `audio/sfx/` |
| 8. Entregar | `scripts/deliver.py` | `out/<slug>.mp4`, relatório e prancha |
| 9. Revisar | [Revisão](references/review.md): `scripts/review.py`, olhar, dar nota, corrigir; até 3 rodadas | `review/rNN/` |

Comandos e o papel de cada repositório: [pipeline](references/pipeline.md) e [ferramentas](references/stack.md).

### Quando falta ferramenta

| Falta (instalação falhou ou proibida) | Reserva | Efeito na entrega |
|---|---|---|
| faster-whisper/WhisperX | Com legenda do usuário ou da plataforma: `captions.py import --file x.srt`. Sem ela, em vídeo narrado: `captions.py estimate`. Em gravação sem legenda: `footage.py cut` corta só silêncio (vícios e retomadas ficam para você marcar ouvindo) | Legenda pode adiantar ou atrasar um pouco; diga no relatório |
| Kokoro | `voice.py --engine system`: voz do Windows, `say` no macOS, espeak-ng no Linux | Licença "uso comercial não verificado": monetizado sai só como rascunho (`deliver.py --draft`) |
| HyperFrames/Remotion | Composição em FFmpeg puro (`drawtext`, `xfade`, `zoompan`) ou HTML de quadros pelo navegador disponível | Motion mais simples; diga isso na nota de Motion |
| ACE-Step | Trilha sintetizada em FFmpeg ou só efeitos | Nota de Som mais baixa |
| Fonte da direção | Fonte de licença aberta já instalada no sistema | Registre a fonte usada em `assets` |

## Regras que evitam retrabalho

- **Gancho no quadro 0.** Fala e texto na tela desde o início, sem logo nem introdução. Numa gravação, a melhor frase vai para o topo do `edl.json` mesmo que tenha sido dita no meio.
- **O áudio manda no tempo.** Cenas com `start` e `duration` medidos por `voice.py`; cortes de gravação no silêncio entre palavras, que é onde `footage.py cut` corta. Nunca corte no meio de uma palavra para "ganhar ritmo".
- **Direção antes de código.** Paleta, fontes, movimento e sons em `direction` antes da primeira cena gerada; numa gravação, ao menos fonte e cor de legenda e o tratamento de B-roll.
- **Animação determinística.** O visual depende só do tempo ou do quadro atual ([ponte](references/motion.md#ponte-determinística)). Nada de `Date.now()`, `setTimeout` ou aleatório sem semente.
- **Nunca parado.** Em vertical, evento visual a cada 1,5–3 s (corte, zoom, texto, B-roll); em 16:9 longo, a cada 5–8 s e uma virada de assunto a cada 60–90 s.
- **Texto na área segura** do formato de tela ([área segura](references/platforms.md#área-segura)).
- **8 GB de VRAM.** Um modelo de GPU por vez; cada ferramenta Python na própria venv.
- **Processos longos em segundo plano.** Enquanto um render, transcrição ou modelo roda, adiante etapas independentes.

## Licenças e conduta

- Registre cada ativo (gravação, voz, música, efeito, imagem, B-roll, modelo 3D, fonte) em `assets` com origem, licença e `commercial_ok`. `true` só quando a licença permite uso comercial por escrito (Apache-2.0, MIT, CC0, CC-BY, SIL OFL, termos do serviço) ou a gravação é do próprio usuário; senão `null` e "uso comercial não verificado". Na dúvida, não é true.
- `deliver.py` bloqueia (código 2) vídeo monetizado com ativo não comercial ou não verificado. Para o usuário ver o resultado, entregue `--draft` (`out/<slug>_rascunho.mp4`, marcado para não publicar). `--allow-noncommercial` é só para `monetized: false`.
- Gravação de terceiros (`footage.py import --third-party`): só com autorização escrita do dono; cortes de podcast, live ou vídeo alheio sem isso não são publicáveis.
- Pontos que mudam a escolha: MusicGen é CC-BY-NC; Hunyuan3D-2 exclui UE, Reino Unido e Coreia do Sul; Remotion é gratuito só para indivíduos e empresas de até 3 pessoas; Chatterbox marca o áudio com marca d'água inaudível. Veja [ferramentas](references/stack.md).
- `yt-dlp` serve para estudar o nicho (títulos, duração, legendas). Não baixe nem reutilize vídeo de outros criadores.
- Voz ou rosto clonado só do próprio usuário ou de quem consentiu por escrito. Conteúdo sintético realista (avatar, voz de pessoa real, cena que parece filmada) pede o rótulo de IA da plataforma: marque `publish.ai_label`.
- Produto, UGC e publi: marque `publish.ad_disclosure` e use a marcação de parceria paga da plataforma; nunca invente depoimento, resultado ou cliente, nem faça avatar de IA se passar por cliente real.
- A skill entrega arquivos e o texto da publicação. Postar, agendar ou usar contas é do usuário, salvo pedido explícito.

## Entrega e verificação

`python scripts/deliver.py <projeto> --video render/master.mp4` mixa o áudio (voz ou gravação, trilha abaixando sob a fala, efeitos), queima as legendas, normaliza para -14 LUFS e exporta no tamanho do formato de tela. Confere resolução, duração e formato por plataforma, volume, pico, quadros pretos, licenças e, em vídeo longo do YouTube, capítulos e miniatura; grava `out/report.md` (com título, descrição e capítulos prontos para colar) e uma prancha.

Depois rode `python scripts/review.py <projeto>`: os critérios mudam com o formato (gravação troca direção e motion por corte de fala e enquadramento; vídeo longo ganha Retenção). Olhe `hook.jpg` e `grid.jpg`, preencha as notas e rode `python scripts/review.py <projeto> --verdict`. Ele decide, não você:

| Código | Significa | O que fazer |
|---|---|---|
| 0 | Todas as notas 4 ou mais, sem bloqueante | Pode declarar pronto |
| 1 | Nota abaixo de 4 ou bloqueante, antes da 3ª rodada | Corrija, entregue de novo e faça outra rodada. Não declare pronto nem pare para perguntar |
| 2 | Notas não preenchidas | Olhe as imagens e preencha |
| 3 | 3ª rodada sem aprovar | Entregue o melhor e relate o que ficou abaixo de 4 e por quê |

Se a nota baixa vem de ferramenta faltando, instale-a (`setup_tools.py`) e refaça a etapa. Se não der para instalar, a nota continua valendo: faça a rodada com o que dá para corrigir e, se chegar à 3ª, relate o limite.

Relate: arquivo final (e se é rascunho), duração, formato de tela e plataformas, volume medido, notas da última rodada e o código do `--verdict`, suposições, licenças, o que foi instalado e as reservas usadas (com o motivo).

## Recursos

- Formatos: [gravação própria](references/formats/gravacao.md), [cortes de vídeo longo](references/formats/cortes.md), [vídeo longo](references/formats/longo.md), [outros formatos](references/formats/outros.md).
- [Pipeline narrado](references/pipeline.md): manifesto, comandos e código de cada etapa do vídeo feito do zero.
- [Direção](references/direction.md), [motion graphics](references/motion.md), [roteiro](references/writing.md) e [revisão](references/review.md).
- [Plataformas](references/platforms.md), [ferramentas](references/stack.md), [instalação](references/setup.md) e [fontes](references/sources.md).

Trabalhos com vários vídeos ou etapas delegáveis combinam com a skill `adaptive-orchestration`, se instalada: transcrição, pesquisa e triagem de cortes vão para um modelo leve; direção, edição, integração e revisão final ficam com o principal.
