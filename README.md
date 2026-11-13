# Vídeo viral

Skill em português para editar e produzir vídeo para TikTok, Instagram (Reels e feed), YouTube (Shorts e vídeo longo) e Kwai, com ferramentas abertas rodando na sua máquina, num pedido só.

- **Sua gravação:** tira silêncios, vícios ("ahn", "éé") e retomadas, põe a melhor frase no começo, enquadra para 9:16, 16:9, 1:1 ou 4:5, legenda palavra a palavra, insere B-roll, mede volume e escreve título, descrição e capítulos.
- **Cortes de vídeo longo:** sugere os trechos com mais chance de funcionar sozinhos e cria um projeto por corte.
- **Do zero (canal dark):** pesquisa, direção de arte, roteiro com gancho escolhido entre vários, narração, motion graphics e cenas 2D/3D em código, trilha, efeitos e legendas.
- **Marketing e formatos avançados:** brief de oferta/público, ganchos multimodais, produto/serviço, UGC, storytelling, música e avatar. Os guias distinguem scripts integrados, composição por projeto e gerações que ainda exigem adaptador/ferramenta disponível.

Vídeo sai medíocre quando ninguém decide o resultado antes e ninguém assiste antes de entregar; o usuário acaba refazendo o pedido várias vezes. Esta skill põe essas rodadas dentro do trabalho: **direção** antes, **revisão** depois (o agente registra inspeção visual, temporal e de áudio, dá nota com critérios do formato e corrige até 3 vezes). Funciona no Claude Code e no Codex com o mesmo `SKILL.md`. Combina [as ferramentas listadas em fontes](references/sources.md).

## Instalação

| CLI | Pasta pessoal | Pasta do projeto | Invocação |
|---|---|---|---|
| Claude Code | `~/.claude/skills/video-viral/` | `.claude/skills/video-viral/` | `/video-viral <pedido>` |
| Codex | `~/.agents/skills/video-viral/` | `.agents/skills/video-viral/` | `$video-viral <pedido>` |

`agents/openai.yaml` só é lido pelo Codex.

As ferramentas de cada etapa são instaladas à parte, uma venv por ferramenta em `~/.video-viral/venvs/`. Veja [instalação](references/setup.md) e confira o que já está pronto:

```sh
python scripts/check_env.py
```

## Scripts

Tudo passa por um manifesto, `video.json` (projetos antigos com `short.json` continuam funcionando), criado por `scripts/new_project.py --format <formato> --aspect <formato de tela>`.

| Script | Faz |
|---|---|
| `new_project.py` | Cria o projeto por formato (narrado, gravacao, corte, produto, ugc, storytelling, musica, avatar) e formato de tela |
| `footage.py` | Importa e limpa a gravação, corta silêncios e vícios, mostra o enquadramento, renderiza com zoom e inserções |
| `clips.py` | Sugere cortes de um vídeo longo e cria um projeto por corte |
| `captions.py` | Transcreve (WhisperX ou faster-whisper), importa `.srt`/`.vtt`, estima tempos e gera a legenda `.ass` |
| `voice.py` | Narração com Kokoro, Chatterbox ou a voz do sistema |
| `deliver.py` | Mixa, legenda, normaliza para -14 LUFS e confere tudo por plataforma: duração, formato de tela, volume, pico, quadros pretos, licenças, capítulos e miniatura |
| `review.py` | Grade de quadros, quadros do gancho, ritmo e alertas; tabela de notas com critérios do formato e `--verdict` |
| `plan.py` | Confere planejamento salvo no manifesto e distingue campo esquecido de dado pendente |
| `trends.py` | Gera pesquisa Google Trends e importa CSV oficial com filtros declarados, fonte e índices preservados |
| `check_env.py` | O que está instalado, o que falta e a VRAM livre |

## Conteúdo

- [SKILL.md](SKILL.md): ponto de entrada, escolha do formato, fluxos e regras.
- Formatos: [gravação própria](references/formats/gravacao.md), [cortes](references/formats/cortes.md), [vídeo longo](references/formats/longo.md), [outros](references/formats/outros.md).
- [Marketing e ganchos](references/marketing.md) e [pesquisa com Google Trends](references/research.md).
- [Avatares/UGC](references/formats/avatares.md), [animação](references/formats/animacao.md), [música](references/formats/musica.md).
- [Pipeline narrado](references/pipeline.md), [direção](references/direction.md), [motion graphics](references/motion.md), [roteiro](references/writing.md) e [revisão](references/review.md).
- [Plataformas](references/platforms.md), [ferramentas](references/stack.md), [instalação](references/setup.md), [fontes](references/sources.md) e [casos de teste](evals/).

## Limites e licença

Pensada para GPU de 8 GB: um modelo por vez, Hunyuan3D só na versão mini. A skill instala sozinha o que a tarefa usa (`scripts/setup_tools.py`: winget ou brew, e venvs em `~/.video-viral/venvs`), salvo se você pedir para não instalar; não publica nem agenda posts, usa yt-dlp só para pesquisa (sem reaproveitar vídeo alheio) e clona voz ou rosto só com consentimento. Ativos com licença não comercial ou não verificada (pesos do MusicGen, voz do sistema, gravação de terceiros sem autorização) bloqueiam a entrega de vídeos monetizados; `deliver.py --draft` gera um rascunho marcado para não publicar. Se uma instalação falhar, a skill usa a reserva da etapa e entrega mesmo assim, dizendo o que faltou. O vídeo só é declarado pronto quando `review.py --verdict` aprova.

Testado de ponta a ponta com gravações sintéticas (voz do Windows, 720p, com vícios e uma retomada): edição em 9:16 e 16:9 com B-roll, cortes de um vídeo de 3 min, entrega e revisão. Depois, com uma gravação real de celular (480p, 2 min): transcrição com faster-whisper na GPU, corte com gancho no topo, legendas e revisão aprovada; e voz Kokoro em pt-BR, ambas instaladas pelo `setup_tools.py`. WhisperX ainda não foi validado. A revisão automática mede ritmo e erros objetivos; a nota estética depende do modelo olhar as imagens.

Distribuída sob a [licença MIT](LICENSE). Cada ferramenta e modelo segue a própria licença.

## Pendências (próximas melhorias)

- Script de A-roll que encaixa os cortes no mínimo de energia do áudio, aplica fades nas emendas, keyframes a cada 1 s e upscale/denoise.
- Script que monta o projeto HyperFrames vertical a partir do EDL, `faces.json` e `words.json` (layout dividido/tela cheia, legendas animadas, gancho com recorte, transições e efeitos sonoros).
- Adaptar as transições com shader do registry (whip-pan, glitch, light-leak) para quadros de vídeo real.
- Efeitos sonoros com Tone.js renderizados offline; trilha com ACE-Step.
- Refazer o vídeo de teste com a edição rica e atualizar os evals com critérios visuais (transições com função, progressão narrativa, legibilidade e gancho multimodal).
- Integrar e validar geradores de avatar/lip-sync e música conforme os guias; manter o status de adaptador até existir uma saída real verificada.

## Planejamento e validação

O manifesto schema 3 acrescenta `brief`, `research`, `hook_candidates` e `tool_plan`; os scripts continuam lendo projetos antigos. Exemplo: `new_project.py campanha --format produto --objective conversao --audience "donos de salao" --offer "servico de agendamento" --dir <pasta>`.

`deliver.py` grava `out/delivery.json`. A revisão vincula vídeo, manifesto e imagens por SHA-256 e exige `assessment.json` com método/intervalos de inspeção; notas isoladas ou um comando executado não aprovam a entrega. Código 3 é resultado com limitações, nunca aprovação. Não há garantia de viralização ou previsão de vendas.

Google Trends entra por URL e CSV oficial; a API alpha não é requisito. O interesse de busca do site é relativo, não volume absoluto ou retenção. Ver [pesquisa](references/research.md).

Testes de regressão: `python -m unittest discover -s tests -v`. Os casos em `evals/` também verificam comportamento editorial e integração; seus graders precisam ser executados por um avaliador compatível. O status de cada validação deve distinguir testes automatizados de avaliação estética e de métricas após publicação.

Smoke técnico com FFmpeg e fixtures sintéticas: `python tests/integration_pipeline.py --output <pasta-nova>`. Exercita gravação e música e rejeita evidência pendente; não dá nota estética nem baixa modelos.
