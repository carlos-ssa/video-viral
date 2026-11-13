---
name: video-viral
metadata:
  version: "2.0.1"
description: Direção, produção e edição audiovisual profissional com IA para vídeos curtos e longos, TikTok, Reels, Shorts, YouTube e Kwai. Use para pesquisar nichos, planejar marketing e ganchos, roteirizar, editar gravações, produzir vídeos de produtos/serviços, UGC, avatares, canais dark, animação e música. Entrega arquivos revisados e material de publicação. Para apenas converter arquivo ou extrair áudio, use FFmpeg diretamente.
---

# Vídeo viral

Atue como diretor audiovisual e editor com estratégia de marketing. A entrega deve combinar uma ideia relevante, gancho cumprido, progressão que sustente atenção e acabamento visual/sonoro profissional. Em divulgação de produtos e serviços, conecte isso à oferta, à prova e à ação desejada. Alcance, conclusão e conversão são objetivos a testar; não prometa viralização nem invente métricas de audiência.

## Ambiente e caminhos

`<skill-dir>` é a pasta deste SKILL.md; `<projeto>` é uma pasta absoluta escolhida para o vídeo. Nos guias, `scripts/...` é relativo a `<skill-dir>`, nunca ao repositório atual do usuário. Execute com esse workdir ou use `python "<skill-dir>/scripts/<script>.py"`. Saídas devem ir para `<projeto>`. Não altere os arquivos originais da gravação.

1. Rode `python scripts/check_env.py`. Instale autonomamente apenas componentes necessários ao plano (`scripts/setup_tools.py <grupos>`), respeitando as permissões do ambiente e as restrições do usuário. Não instale todo o catálogo nem reative skills removidas só por constarem nele. Com instalação proibida, use `VIDEO_VIRAL_NO_INSTALL=1`; com falha, escolha uma reserva documentada e registre o impacto. Veja [setup](references/setup.md).
2. Inferir idioma, formato e plataforma do pedido/material evita perguntas desnecessárias. Sem pista: pt-BR, vertical 30–45 s; em longo, duração ditada pelo conteúdo; licença comercial é exigida por padrão. Registre suposições. Pergunte apenas informação essencial que não pode ser inferida, como qual produto está sendo oferecido quando não há contexto.
3. Crie com `python scripts/new_project.py <slug> --format <formato> --aspect <aspect> --dir <pasta-absoluta>`. O manifesto é `video.json`; `short.json` legado continua aceito. `--objective`, `--audience` e `--offer` iniciam o brief. Reexecute somente etapas afetadas por alterações.

## Escolha o fluxo

| Pedido | Formato | Ler quando aplicável |
|---|---|---|
| Gravação própria ou tutorial | `gravacao` | [Gravação](references/formats/gravacao.md) |
| Trechos de um vídeo longo | `corte` | [Cortes](references/formats/cortes.md) |
| Narrado/canal dark sem aparecer | `narrado` | [Pipeline](references/pipeline.md) |
| Divulgação de produto ou serviço | `produto` | [Marketing](references/marketing.md) + [produto/UGC](references/formats/outros.md) |
| UGC real ou avatar apresentador | `ugc`, `avatar` | [Avatares/UGC](references/formats/avatares.md) + gravação |
| Animação/storytelling | `storytelling` | [Animação](references/formats/animacao.md) + pipeline |
| Música, lyric video ou visualizer | `musica` | [Música](references/formats/musica.md) |
| YouTube longo | formato de origem, `--aspect 16:9` | Acrescentar [longo](references/formats/longo.md) |

Para uma correção pontual, preserve conteúdo e direção que não foram pedidos para mudar. Para uma produção completa, execute o fluxo editorial e audiovisual abaixo. Leia somente os guias relevantes, não todos por padrão.

## Planejamento, ganchos e retenção

1. **Brief.** Preencha `brief`: objetivo (`alcance`, `consideracao`, `conversao`, `entretenimento`), público/nicho, problema ou desejo, benefício, provas disponíveis, objeções e ação. Em marketing, registre oferta e destino real do CTA. Veja [marketing e ganchos](references/marketing.md).
2. **Pesquisa.** Use [pesquisa](references/research.md): referências recentes do nicho e plataforma, Google Trends e, quando fornecidos, analytics reais. Registre fonte, data, filtros e natureza da evidência em `research`; não deduza retenção ou conversão de visualizações públicas. Sem acesso, siga com hipóteses identificadas.
3. **Ganchos.** Desenvolva cinco candidatos quando criar uma peça completa: abertura visual, fala, texto e som, promessa, público e payoff. Avalie relevância, curiosidade, clareza, execução visual e cumprimento. Registre em `hook_candidates`; `hook` mantém o vencedor. Preserve alternativas para testes comparáveis. Um ajuste de legenda não exige refazer os cinco.
4. **Roteiro.** Construa a progressão por batidas, prova/demonstração quando pertinente, recompensa e CTA contextual. Use [writing](references/writing.md); em longo, blocos e reaberturas. O áudio determina o tempo: cenas e entradas se apoiam na narração, performance ou música medida, não em duração inventada.
5. **Direção.** Defina paleta, fontes, enquadramento, performance, luz, câmera, movimento e som em `direction`. Planeje cenas e três quadros de estilo antes do render completo. Veja [direction](references/direction.md).

Antes de entregar um planejamento completo ou começar a produção, salve essas decisões no `video.json` e rode `python scripts/plan.py <projeto>`. Um relatório em Markdown não substitui `brief`, `hook_candidates`, `hook`, `research` e `tool_plan`. Código 1 pede completar campos; código 2 permite entregar um plano provisório, identificando os dados em `brief.missing_inputs`, sem declarar produção liberada. Código 0 confirma consistência estrutural, não qualidade criativa. Em projetos v2, stack.modules e cada tool_plan[].module usam IDs do catálogo; o compositor é hyperframes. Não invente informação para fazer a checagem passar. Essa checagem não se aplica a uma correção pontual em vídeo existente.

## Produção e edição profissional

A versão 2.0.0 limita o catálogo a `assets/stack.json`. Use `scripts/stack.py list` e `doctor`: detectado não significa validado. Os [módulos executáveis](references/modules.md) geram arquivos de cena, WAV, imagens ou GLB para a composição. Escolha PixiJS, Paper.js ou p5.js pela linguagem visual; não carregar todos por obrigação. Não instalar motores fora do catálogo por conveniência.

Use somente o stack v2: [stack](references/stack.md) descreve pesquisa, voz, imagens, animação 2D/3D, avatares, música, composição e acabamento. Selecione e combine ferramentas pelo resultado da cena. Registre em `tool_plan`: etapa/cena, ferramenta, contribuição esperada, entrada/saída e status (`integrado`, `validado-neste-projeto`, `adaptacao`, `planejado`). Uma ferramenta citada não é automaticamente integrada ou testada.

O padrão é edição rica e intencional: composição e hierarquia, enquadramento que valoriza o assunto, cortes naturais, animação com bom timing, continuidade, integração de B-roll/IA, correção de cor e desenho de som. [Motion](references/motion.md) traz receitas. Varie planos e recursos para sustentar a narrativa; não existe cota universal de transições, zooms ou efeitos. UGC, anúncio, documentário, aula e música precisam de direções próprias. Preserve o pedido de acabamento sofisticado e justifique escolhas pela peça, não pela quantidade de ferramentas.

- HyperFrames + GSAP é o compositor principal obrigatório para produção completa. Three.js/Blender e ComfyUI entram conforme a cena; não substituir o motor por um compositor externo. FFmpeg prepara/mixa/exporta, e uma base FFmpeg não é edição rica aprovada. Uma composição deve ser determinística por tempo/quadro; sem relógio real nem aleatório sem semente.
- Gravação: importar → transcrever/importar SRT → selecionar/cortar e reordenar EDL → enquadrar → compor edição rica → entregar. `footage.py render` gera o A-roll/base; a camada de acabamento segue o guia de gravação. Não corte palavras nem altere o sentido da fala.
- Narração: roteiro/tempos → voz → alinhamento → cenas/ativos → composição → trilha/efeitos → entrega. Kokoro é o único TTS; faster-whisper fornece transcrição e tempos, com conferência humana/modelo e sem alinhador forçado adicional.
- Legendas devem ser legíveis, sincronizadas e fora do rosto/UI; enquadramento e [área segura](references/platforms.md) dependem do destino. Um vertical pode compartilhar o master, mas confirme capa, CTA e enquadramento por plataforma.
- Um modelo pesado de GPU por vez no perfil local de 8 GB. Mantenha projetos e caches para refazer somente a etapa alterada. Uma limitação de ferramenta pede alternativa concreta, não renderizações idênticas repetidas.

## Entrega e revisão

`python scripts/deliver.py <projeto> --video render/master.mp4` exporta, mede áudio e formato, confere licenças e grava `out/report.md` e `out/delivery.json`. Trilha e legenda usam as opções do formato; legendas já compostas pedem `--no-captions`.

Antes de delegar a revisão, confira as modalidades reais do revisor com `review.py --check-reviewer <capacidades.json> --producer-id <id-do-autor>`. Registre ferramenta/método e evidência da capacidade; não inferir vídeo/áudio apenas pelo nome do modelo. Um revisor limitado a quadros pode avaliar aspectos visuais, mas não aprovar movimento e som.

Depois, `python scripts/review.py <projeto> --producer-id <id-do-autor>` gera métricas, imagens, `assessment.json` e um pacote `review/rNN/input/` com vídeo, briefing, referências e critérios, sem o relatório de notas do autor. Use um revisor distinto (subagente quando disponível e autorizado, ou pessoa independente), com contexto próprio e acesso somente ao pacote e às referências pertinentes. Não enviar notas/conclusões do autor; o principal continua responsável por conferir a entrega. O revisor registra identidade, capacidades, método, intervalos e suas próprias notas. Se não houver revisão independente possível, registre autoverificação e mantenha a aprovação independente pendente.

Siga a [revisão visual, temporal e de áudio](references/review.md). Aprovação completa exige observação registrada e cobertura de todas as modalidades aplicáveis; métricas instrumentadas, quadros isolados ou inspeção parcial não a substituem. Não simular reprodução/escuta nem preencher capacidades inexistentes para aprovar.

`python scripts/review.py <projeto> --verdict` exige o mesmo vídeo/manifesto, artefatos consistentes, entrega técnica publicável e avaliação registrada. A nota estética continua sendo julgamento, não medição de viralidade.

| Código | Ação |
|---|---|
| 0 | Critérios aprovados e evidências completas: pode declarar pronto |
| 1 | Falha/bloqueante: escolha correções de maior efeito e refaça as etapas afetadas |
| 2 | Evidência/nota ausente ou desatualizada: complete ou gere revisão válida |
| 3 | Limite de três rodadas: entregue o melhor como resultado com limitações, nunca como aprovado |

Se um canal não pôde ser inspecionado, registre `unverified` e relate o limite. Não aumente notas para aprovar. Não repita uma rodada sem mudança verificável ou nova evidência. Instale um componente faltante só se necessário e permitido; se indisponível, aplique a reserva uma vez e explique o que permanece limitado.

## Ativos, publicação e aprendizado

Registre origem, licença e `commercial_ok` dos ativos. `deliver.py` bloqueia publicação monetizada sem licença confirmada; `--draft` permite mostrar um rascunho identificado. Confira licenças/termos atuais em [stack](references/stack.md); modelos e pesos podem ter licenças diferentes do código.

Voz/rosto de outra pessoa requerem consentimento. Avatares não devem fingir depoimentos reais; demonstre o produto/serviço com prova existente. Marque `publish.ai_label` e `ad_disclosure` quando aplicáveis. Estudar referências não autoriza reutilizar vídeos de terceiros. A skill prepara arquivos e textos; só publica ou agenda com pedido explícito.

Entregue arquivo e status, formato/plataformas, medições, método/alcance da revisão, notas e veredito, suposições, licenças, instalações e reservas. Para marketing, inclua CTA e destino. Quando houver analytics, proponha variações controladas de gancho/montagem e registre a hipótese e a métrica; não invente resultados nem declare conhecer pesos internos dos algoritmos.
