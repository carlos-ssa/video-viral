---
name: video-viral
metadata:
  version: "2.3.0"
description: Direção, produção e edição audiovisual profissional com IA para vídeos curtos e longos, TikTok, Reels, Shorts, YouTube e Kwai. Use para pesquisar nichos, planejar marketing e ganchos, roteirizar, editar gravações, produzir vídeos de produtos/serviços, UGC, avatares, canais dark, animação e música. Entrega arquivos revisados e material de publicação. Para apenas converter arquivo ou extrair áudio, use FFmpeg diretamente.
---

# Vídeo viral

Dirija e edite com estratégia: ideia relevante, gancho cumprido, progressão e acabamento profissional. Em divulgação, conecte oferta, prova e ação. Alcance, conclusão e conversão são objetivos a testar, sem prometer viralização ou inventar métricas.

## Ambiente e caminhos

`<skill-dir>` contém este SKILL.md; `<projeto>` é a pasta absoluta do vídeo. `scripts/...` é relativo à skill: use esse workdir ou caminhos absolutos. Saídas no projeto; preserve originais.

1. Rode `python scripts/check_env.py`. Instale grupos necessários com `setup_tools.py <grupos>`: venvs/npm dedicados quando permitido; sistema, `pip --user` e ComfyUI só após **confirmação única da lista**, com `--allow-system`/`--allow-large`. Código 4: consentimento pendente, nada instalado. Proibição usa `VIDEO_VIRAL_NO_INSTALL=1`. Siga [setup](references/setup.md), inclusive reservas.
2. Infira idioma, formato e plataforma. Sem pista: pt-BR, vertical 30–45 s; longo conforme conteúdo; licença comercial por padrão. Registre suposições; pergunte apenas dados essenciais impossíveis de inferir.
3. Crie com `python scripts/new_project.py <slug> --format <formato> --aspect <aspect> --dir <pasta-absoluta>`. Use `video.json` (legado: `short.json`); opções de brief em [pipeline](references/pipeline.md). Refaça só etapas afetadas.

## Escolha o fluxo

| Pedido | Formato | Ler quando aplicável |
|---|---|---|
| Gravação própria ou tutorial | `gravacao` | [Gravação](references/formats/gravacao.md) |
| Trechos de um vídeo longo | `corte` | [Cortes](references/formats/cortes.md) |
| Narrado/canal dark sem aparecer | `narrado` | [Pipeline](references/pipeline.md) |
| Divulgação de produto ou serviço | `produto` | [Marketing](references/marketing.md) + [produto/UGC](references/formats/outros.md) |
| UGC real ou avatar apresentador | `ugc`, `avatar` | [Avatares/UGC](references/formats/avatares.md) + gravação |
| Animação/storytelling | `storytelling` | [Animação](references/formats/animacao.md) + pipeline |
| POV, criaturas, ASMR ou séries com IA | `storytelling`, `narrado` | [Guia de produção e limites](references/formats/virais-ia.md) |
| Música, lyric video ou visualizer | `musica` | [Música](references/formats/musica.md) |
| YouTube longo | formato de origem, `--aspect 16:9` | Acrescentar [longo](references/formats/longo.md) |

O guia de virais com IA ensina a produzir pelas rotas do stack ou de clipes externos fornecidos.

Preserve conteúdo/direção fora de correções pontuais. Na produção completa, siga o fluxo; leia referências pertinentes, composição antes de produzir e revisão antes de avaliar.

## Planejamento, ganchos e retenção

1. **Brief:** objetivo (`alcance`, `consideracao`, `conversao`, `entretenimento`), público/nicho, problema/desejo, benefício, provas, objeções e ação. Marketing inclui oferta e destino real do CTA. [Marketing e ganchos](references/marketing.md).
2. **Pesquisa:** referências recentes, Trends e analytics fornecidos, com fonte/data/filtros/tipo em `research`. Sem acesso, identifique hipóteses. Siga os limites de evidência e inferência em [pesquisa](references/research.md).
3. **Ganchos:** cinco candidatos audiovisuais conforme [marketing](references/marketing.md), avaliados por relevância, curiosidade, clareza, execução e cumprimento. Salve `hook_candidates`, vencedor em `hook` e alternativas para testes; ajuste pontual dispensa refazê-los.
4. **Roteiro:** batidas, prova, recompensa e CTA contextual. Use [writing](references/writing.md); longo pede blocos e reaberturas. Meça áudio/performance/música antes de temporizar cenas.
5. **Direção:** registre visual, performance, luz, câmera, movimento e som em `direction`; planeje cenas e três quadros de estilo antes do render. [Direção](references/direction.md).

**Portão de planejamento:** salve o manifesto e rode `python scripts/plan.py <projeto>` antes de entregar plano completo ou produzir. Código 0 confirma estrutura, não criatividade; 1 pede completar; 2 permite plano provisório, sem liberar produção. Desconhecidos ficam em `brief.missing_inputs`. Correção pontual dispensa o portão.

## Produção e edição profissional

Use exclusivamente `assets/stack.json` conforme [stack](references/stack.md). `stack.py list`/`doctor` detectam, sem validar resultado. Registre `tool_plan` com etapa, contribuição, entrada/saída e IDs/status reais do contrato de [módulos](references/modules.md); compositor `hyperframes`.

- **Composição obrigatória:** HyperFrames + GSAP. CLI só por `python scripts/stack.py hyperframes [--node-root <pasta>] [--screenshot] -- <comando>`; `VIDEO_VIRAL_NO_INSTALL` bloqueia a CLI, não os adaptadores Puppeteer locais. Siga [composição → render/master.mp4](references/composition.md) para HTML, cenas, preview, checagem e render. FFmpeg prepara/mixa/exporta; base/demo não é acabamento aprovado. Determinismo por tempo/quadro: [motion](references/motion.md).
- **Gravação:** importar → transcrever/SRT → selecionar/reordenar EDL → enquadrar → compor → entregar. `footage.py render` gera A-roll/base; preserve palavras/sentido e siga o acabamento do guia.
- **Narração:** roteiro → voz medida → tempos conferidos → cenas → composição → som → entrega. Kokoro é o único TTS; WAVs externos são entrada oficial. faster-whisper transcreve/temporiza com conferência. Reservas sem outro motor/alinhador: [pipeline](references/pipeline.md).
- **Acabamento:** hierarquia, enquadramento, cortes naturais, continuidade, cor, B-roll e som. Preserve sofisticação; escolha recursos pela função, não quantidade. Legendas sincronizadas fora do rosto/UI; confira capa, CTA, recorte e [área segura](references/platforms.md) por destino.
- **Música de reserva:** `python scripts/music.py <projeto> --backend procedural --duration 30 --seed 7`, sem endpoint/prompt; cama instrumental simples com `fallback:true`, nunca geração ACE-Step equivalente.
- **Recursos:** um modelo pesado de GPU por vez no perfil de 8 GB. Preserve projetos/caches; [setup](references/setup.md) orienta reservas concretas sem repetir operações idênticas.

## Entrega e revisão

**Portão técnico:** `python scripts/deliver.py <projeto> --video render/master.mp4` exporta, mede, confere licenças e grava `out/report.md`/`delivery.json`. Evite camadas duplicadas; legenda composta usa `--no-captions`.

**Portão audiovisual:** siga [revisão](references/review.md), incluindo separação autor/revisor, preflight, modalidades, hashes e cobertura integral. `review.py <projeto> --producer-id <id-do-autor>` gera rodada e `input/`. Revisor distinto usa capacidades reais e contexto próprio, sem notas do autor. Métricas/quadros limitam o escopo; o coordenador mantém responsabilidade.

Sem reprodução/escuta, quando o técnico passou, o normal é **entrega técnica aprovada, revisão humana pendente**. Encaminhe `input/` e `review/rNN/ficha-humana.md` a pessoa independente; ela registra identidade, observação integral, notas e trechos. Importe com `review.py <projeto> --human-form <ficha>`. O autor não responde pela pessoa.

`review.py <projeto> --verdict` exige o mesmo vídeo/manifesto, evidências e entrega técnica. Só código 0 permite declarar pronto; gerar rodada não é aprovação. Notas estéticas são julgamento, não previsão de audiência.

| Código | Ação |
|---|---|
| 0 | Critérios aprovados e evidências completas: pode declarar pronto |
| 1 | Falha/bloqueante ou inspeção parcial: corrigir ou completar observação |
| 2 | Evidência/nota ausente ou desatualizada: completar ou gerar revisão válida |
| 3 | Limite de três rodadas: entregar o melhor com limitações, sem aprovação |

Pendência humana mantém 1/2, nunca 0. Registre canais indisponíveis como `unverified`, sem simular reprodução/escuta ou inflar notas. Nova rodada exige mudança verificável ou nova evidência. Detalhes antifraude e reservas permanecem obrigatórios em [revisão](references/review.md).

## Ativos, publicação e aprendizado

Registre origem, licença e `commercial_ok`; modelos/pesos têm termos próprios. `deliver.py` bloqueia monetização sem licença confirmada; `--draft` mostra rascunho identificado. Voz/rosto de terceiros exigem consentimento; avatar não é depoimento real. Use provas existentes, `publish.ai_label` e `ad_disclosure` quando aplicáveis. Estudar referência não autoriza reutilização. Publicar/agendar exige pedido explícito.

Entregue arquivo/status, formatos/plataformas, medições, método/alcance da revisão, notas/veredito, suposições, licenças, instalações e reservas; marketing inclui CTA/destino. Com analytics reais, proponha variações controladas com hipótese/métrica, mantendo resultados indisponíveis como tais.
