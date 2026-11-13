# Auditoria integral de instruções, referências e evals — 13/11/2026

Escopo: repo video-viral2.4.0, fonte atual Edge TTS7.3.1/Thalita/Ava +20%; skill instalada antiga não consultada. Contrato faixa2 sol/medium provisório, sem métricas medidas de custo/capacidade/latência. Não subdeleguei. Escrita apenas em docs/references/evals e work externo; nenhuma instalação, download de pesos, chamada paga ou publicação.

## Atualização r03 — planos criticados pelo juiz independente

A decisão independente final deve ser consultada no relatório consolidado `video-viral/audits/2026-11-13/report.md` quando publicado pelo coordenador; os scores deste arquivo são históricos/preliminares do ensaio manual e não prevalecem sobre aquela decisão.

O juiz independente considerou os planos de animação/avatar/música genéricos, apesar do pass preliminar deste auditor. Isso expõe excesso de confiança do julgamento inicial: o27/27 decidido relatado emr02 deve ser lido como **julgamento manual preliminar**, não aprovação independente nem taxa causal da skill. Os três planos foram reescritos em resposta à crítica, sem mudar qualquer grader, gerar mídia ou publicar. O coordenador depois informou que o juiz considerou os três planos reescritos substanciais/corretos e pediu apenas explicitar o registro da função sonora na animação. Essa complementação r03a está em research/sound-plan.json: saída futura, rolesbed/sfx, função por evento, origem procedural ou realautorizada pendente, license/commercial_ok:false até verificação. Nenhum áudio/asset concluído foi criado. A decisão independente consolidada continua um registro separado; corrigir exemplos manualmente não demonstra que novos agentes terão o mesmo resultado.

| Caso | Antes r01/r02 | Artefato concreto r03 | Estado comprovado |
|---|---|---|---|
| animacao-personagem | Três narrações curtas e descrição genérica, plano técnico só por módulo | Três cenas com sete planos: chegar/frear/olhar; testar folha sem soltar pacote; sinalizar/responder; atravessar; contato de entrega; favor com consequência. Bíblia propõe frente/perfil/poses e rig único deBia, referência distinta da barqueira, pacote/eixo/escala invariantes. Toolplan associa cada plano a entrada/saída e critério de continuidade/contato/acabamento | `response-r03.md`, `projeto/video.json`, `research/continuity-plan.md`; plan2 sem erros, arquivos de referência/voz/Foley ainda ausentes |
| avatar-ugc | Bloqueio correto, porém performance e demonstração pouco especificadas |35s-alvo: olhar câmera, frase e pausa, gesto para tela;5–10estado inicial,10–21ação,21–26resultado da gravação real;26–35retorno/convite/pausaCTA/fecho. Nenhuma tela/função/in-out de fonte fabricados. Voz externa autorizada ainda não recebida; gerador ausente. Checks de boca/voz e gestos em janelas específicas e depois integralmente | `response-r03.md`, `projeto/video.json`, `research/performance-and-sync.md`; plan2 sem erros; avatar/gravação/voz/oferta/destino pendentes |
| musica-instrumental | Indicação geral de energia e mix, sem arco visual concreto | Identidadeanel/traço:0–3assinatura,3–10arcos,10–19expansão de caminhos,19–26retorno,26–30fechamento. As fronteiras são storyboard provisório, sem alegar seções/onsets reais. Arquivo musical ausente, BPM/onsets null; plano descreve medição/escuta futura e alinhamento a frases, faixa única, nenhuma fala e fecho que preserve nota/cauda | `response-r03.md`, `projeto/video.json`, `research/music-timing-plan.json`; plan2 sem erros, faixa/marca/tempos musicais pendentes |

Baselines r03 foram preservadas antes da escrita em `work/eval-runs/revision-r03/baseline/`, com `baseline-results.json` e `checks.json` registrando comandos reais e hashes antes/depois. Não alterei scripts do repo. O runner manual continua um ensaio controlado não cego; `VIDEO_VIRAL_NO_INSTALL=1`, `HF_HUB_OFFLINE=1` e `TRANSFORMERS_OFFLINE=1` estão no ambiente dos subprocessos em `work/manual-evals.py`. Os comandos estão nos traces, não presumidos a partir da resposta. O coordenador informou ter compartilhado esse harness com o juiz para conferir a proibição de instalar.

Quanto aos dois renders de gravação/corte, Node_setup concluiu a versão r03 e documentou o pipeline em work/audit-eval-renders.md, com comandos e evidência estruturada em work/eval-render-commands.json e work/eval-render-evidence.json. Este auditor conferiu por leitura e SHA256 a igualdade entre out/receipt/input/request/assessment e hash canônico do manifesto; registro em revision-r03a/render-linkage-check.json. Os receipts são approved:true/draft:false e as modalidades continuam pending, com ficha humana vazia e verdict2. Isso resolve ausência de artefatos técnicos, mas não equivale à aprovação audiovisual nem à decisão independente final dos graders. A gravação ainda tem limitação de quebra órfã no CTA final relatada pelo produtor; não foi ocultada. As fontes são fixtures do caso, não pessoa real filmada. Nenhuma alegação de reprodução/escuta foi feita por este auditor.

## Atualização comparativa r02 — falhas corrigidas em artefatos

O resultado atual do ensaio manual é **27/33 pass, 0 fail, 6 pending**:81,8% do denominador total. Entre rubricas decididas, **27/27=100%**. A taxa de rubricas decididas excede90%, mas **não equivale a conclusão global, execução cega de agentes ou aprovação audiovisual**. A seção baseline r01 abaixo foi preservada como histórico, sem apagar seus23pass/4fail/6pending.

As quatro falhas foram corrigidas na execução manual, sem afrouxar os graders. Cópias anteriores e hashes ficam em `work/eval-runs/revision-r02/baseline/` e `baseline-results.json`; diferenças observáveis e decisões de regrade ficam em `checks.json`, `final-plan-checks.json` e `regrade.json`. `work/eval-runs/results.json` agora contém a classificação corrente. As notas1–5 dos ganchos são justificativas editoriais para planejamento, não notas de render ou métricas de audiência.

| Rubrica antes fail | Evidência anterior | Correção concreta r02 | Regrade |
|---|---|---|---|
| marketing-e-trends/01 | Quatro ganchos genéricos que serviam a qualquer assunto | Cinco aberturas específicas: avaliação do sofá, processo de limpeza, limite de remoção de manchas, preparo e serviço emSão Paulo. Cada uma inclui fala/visual/tela/som/promessa/payoff/notas justificadas. Nenhum preço, bairro, prova ou WhatsApp inventado. CTA/demonstração/limites ficam em missing_inputs; Trends permanece URL sem dado coletado | pass no escopo de plano provisório; plan2 sem erros |
| pedido-unico-cinematografico/02 | Ganchos sem episódio histórico concreto | Cinco ganchos sobre queda, muralhas, data29maio1453, pressão terra/mar e consequência imperial. H1«Como Constantinopla caiu?» consta no manifesto e na primeira cena. Cada dimensão tem nota e motivo próprios | pass de planejamento |
| pedido-unico-cinematografico/03 | Cenas com benefício/fecho genéricos | Roteiro original de100palavras,6cenas/14planos/35s-alvo: mapa, muralhas, artilharia, pressão terrestre/naval, calendário, entrada e consequência. Cada plano tem cue/janela-alvo, ação, quadro, câmera, ênfase e som. Não inclui contagem de tropas/vítimas, fala atribuída ou encenação da morte sem prova; diagramas próprios são identificados | pass da lista de planos; render continua pending |
| short-monetizado-ptbr/02 | Primeiro plano durava6,667s apesar da meta~2s | Mesmo roteiro de92palavras; primeira janela0–2s e demais2–10/10–17/17–25/25–36/36–40. Alvo40s mantido. É tempo planejado, sem voz medida; produção deve reancorar/encurtar se não couber | pass da intenção de roteiro; plan0 |

Não acrescentei regra universal nem teste por regex para esconder a falha do ensaio. As instruções já exigiam ganchos ligados ao público/promessa e voz medida antes de fechar cenas; a correção necessária foi escrever planos realmente específicos. Apenas reparei uma sequência de codificação UTF-8 mal exibida em `03-shot-list.md` («1.5–3»), preservando exatamente o critério. Nenhuma nota estética de filme foi preenchida.

O roteiro histórico antecedeu a conferência de fonte. Depois foi aberto o artigo de Mark Cartwright, World History Encyclopedia,23/01/2018, URL `https://www.worldhistory.org/article/1180/1453-the-fall-of-constantinople/`, para conferir fatos gerais. Fonte documental secundária; não é vídeo assistido nem estudo de retenção. Notas e limites ficam em `pedido-unico-cinematografico/projeto/research/factual-check.md`. Nenhuma imagem/mapa/texto do artigo foi incorporado; a licençaNC do artigo não foi tratada como licença de ativos para monetização. Acesso direto às duas páginas Britannica tentadas falhou e não foi contado como leitura.

### As seis rubricas ainda pendentes e seus artefatos exatos

| Rubrica pending | Caminho do projeto/artefato que falta | Condição para decidir |
|---|---|---|
| composicao-hyperframes/01-main-render | `work/eval-runs/composicao-hyperframes/projeto/composition/index.html`, cena2D realmente integrada, vozWAV autorizada, logs wrapperHF, três quadros/seek e `render/master*.mp4` de12s | Rodar o caso exato com autorização/recursos reais; quatro demos diferentes do agente productions não comprovam esse prompt. Confirmar pixels decodificados e arquivo de saída; sem removerNO_INSTALL em execução cujo prompt proíbe instalação |
| composicao-hyperframes/02-delivery-evidence | Mesmo projeto: `out/<slug>.mp4`, `delivery.json`, `review/rNN/input/`, `assessment.json` e ficha humana vazia | Entrega técnica e hashes precisam corresponder ao master real, sem camadas duplicadas; não pedir nem criar aprovação perceptual falsa |
| cortes-de-video-longo/03-makes-best-clip | `work/eval-runs/cortes-de-video-longo/corte-selecionado/`: EDL, composiçãoHF, master9:16 e export com legenda | Node_setup assumiu a produção deste projeto. Foi escolhido rank3 coeso, não o diretório `melhor-corte` de rank1 que começa sem contexto. Verificar fonte real, três gastos completos, legenda/faixa segura e proveniência no render efetivo |
| cortes-de-video-longo/04-chapters-and-publish | `work/eval-runs/cortes-de-video-longo/projeto/video.json` e versão longa final identificada porhash | Capítulos atuais00:00/00:47/02:02 são provisórios. O prompt pede subir o longo inteiro, sem exigir edição desse longo: o MP4 fonte inalterado pode ser adotado explicitamente como versão final longa e ter tempos conferidos nele, sem render redundante. Se a montagem longa mudar, conferir no novo MP4 e atualizar capítulos |
| editar-gravacao-propria/04-delivered-and-reviewed | `work/eval-runs/editar-gravacao-propria/projeto/`: composiçãoA-roll real, masterHF, export legendado, receipt e revisão ligados porhash | Node_setup assumiu render/export. EDL real já descarta retomada21,002–22,370s. Exigir fonte original, fala única e inspeção de quadros; ficha humana/revisão audiovisual podem continuar pendentes com relato honesto. Um receipt técnico não autoriza dizer pronto |
| pedido-unico-cinematografico/05-review-before-done | `work/eval-runs/pedido-unico-cinematografico/projeto/`: voz autorizada, ativos próprios, masterHF de35s, delivery/review | Roteiro r02 está corrigido, mas não foi produzido/renderizado; render storytelling de outro conteúdo não cobre este caso. Sem reprodução/escuta real, deixar status humano pendente, sem criar notas/veredito0 |

A coordenação foi informada dos caminhos e da escolha correta do corte; nenhum manifesto de gravação/corte foi alterado por mim durante a produção do agente Node_setup. A classificação pending só será promovida depois da inspeção dos artefatos reais pertinentes; não foi usada promessa de render como sucesso.

## Método e limites
Li integralmente SKILL.md skill-creator do ambiente, SKILL/README/agents e todos os textos de references/evals, incluindo ambos SRTs. Saídas truncadas do terminal foram relidas em blocos menores. Assets de manifesto/catálogo/reviewer/package direto e requisitos Python foram lidos somente como contratos; lock Node e código de integração pertencem à auditoria dos agentes especialistas, não foram tratados como instruções nem alterados por mim.
Executei um ensaio manual controlado com13prompts e32comandos registrados em eval-runs/*/commands.json, além da escolha editorial complementar de clips make rank3. Este subagente é independente do autor/coordenador, mas NÃO é forward-test cego: leu graders e corrigiu instruções antes do ensaio, e escreveu respostas/manifestos deliberadamente. Não mede taxa de sucesso de agentes novos, generalização ou qualidade audiovisual. O harness externo não pontua por regex; results.json contém julgamento semântico explícito por grader. Comandos passaram pelo Python real e originais foram preservados.
Não executei reprodução temporal nem escuta perceptual. Nenhuma nota estética4/5 foi atribuída ao vídeo ausente. Plan0/2 valida estrutura ou pendência, não criatividade. O check_env real detectou FFmpeg/HyperFrames e faster-whisper, ausência de Edge TTS na venv, Blender e servidor ComfyUI; detecção não comprova geração. Não removi NO_INSTALL para contornar o bloqueio HyperFrames.

## Achados e correções
1. SKILL esclarece proporcionalidade: consulta de licença/diagnóstico não força criação de projeto/ganhos/render; planejamento apenas não autoriza gerar mídia. Licença genérica era transformada em CC-BY-NC/pesos sem fonte; Tone/ACE eram tratados como liberação automática de faixa. Corrigidos caso e graders para direitos reais de pesos/inputs/serviço/áudio, permissão específica e nenhum bypass. Edge TTS mantém commercial_ok:false por padrão.
2. Cadência fixa/palavra-a-palavra contradizia segmentação por sentido e pausa intencional. Corrigidos direção/gravação/cortes/longo e eval gravação/cinematográfico. Títulos/efeitos não viram nota por contagem.
3. Composição autorizava conteúdo essencial atéy1580/base340 contra plataforma y1500/base420. Unificada região conservadora x90–930,y250–1500; legenda exclusiva y1280–1500. Destino real ainda requer inspeção de UI.
4. Avatar sugeria workflow ComfyUI como se cliente baixasse vídeo. Explicado que comfy.py importa imagens e não inclui render falante/lip-sync; vídeo externo autorizado ou execução própria realmente verificada permanecem entradas possíveis, sem adicionar motor.
5. Música dizia compositor HyperFrames/Blender; explicitado HyperFrames+GSAP final, Blender como cena. Índice de virais permitia animatic sem escopo aceito; alinhado à regra de preservar pedido.
6. Grader de Constantinopla exigia POV bíblico/novela/making-of/ASMR e kind:sfx obrigatório sem relação ao caso. Removidos requisitos estranhos e mantido acabamento pertinente. Outros graders também deixaram de exigir kind exclusivo ou densidade ASMR em peça narrada.
7. Expected de gravação proibia instalar sem prompt correspondente; corrigido expected para respeitar autorização real. Expected de short agora acompanha explícito não instalar. README atribuía claude plugin eval a skill-creator sem evidência: corrigido; compatibilidade de runner não validada.
8. Link motion#princípios inexistente corrigido; cor de legenda não é campo de manifesto, explicitado HTML/ASS. Autoria declarada de cortes não prova direitos de músicas/imagens incorporadas. Node.js22.12+ documentado conforme auditoria de lock. Instalação já autorizada no mesmo escopo não exige pergunta repetida.
9. Contrato review atualizado conforme agente especialista: tabela com quatro colunas, nota somente na coluna correta, duplicação/observação ausente tornam2; every finito positivo e limite de65.500px por eixo. r04 preservada e mudança concreta entre rodadas não é provada por hash. Contrato mix atualizado: ganho da música também sem voz externa e ducking com fala embutida; sem inferir qualidade da mix por parâmetros. Changes de scripts correspondentes são responsabilidade do coordenador.

## Baseline r01 — score por caso e denominadores
Rubrica: cada grader existente vale1. pass exige evidência pertinente ao escopo; fail é falha observável deste ensaio; pending indica ramo de render/entrega/inspeção não exercitado e não conta como sucesso. Dentro de um grader conjuntivo, não fraciono pontos. Um diagnóstico honesto de bloqueio pode satisfazer honestidade, mas não prova o render completo.
Total: 23/33 pass (69.7%), 4 fail, 6 pending. Entre decididos: 23/27 (85.2%); esse denominador exclui pendências e NÃO pode ser vendido como conclusão global.

| Caso | Graders pass/fail/pending | Evidência e limite |
|---|---|---|
| animacao-personagem | 1/0/0 de1 | Plano3cenas com obstáculo/tentativa/entrega; bíblia de Bia/rig reutilizado, seed não prova identidade; som parametrizado e seek/quadros/revisor previstos. Não foi gerada animação. |
| avatar-ugc | 1/0/0 de1 | Bloqueio de avatar/lip-sync reconhecido; sem depoimento fictício/cobrança. Preparação provisória não apresentada como filme. Gravação mencionada não anexada; app/oferta/destino/gerador continuam pendentes. |
| composicao-hyperframes | 0/0/2 de2 | plan2 (voice_wavs pendente); stack hyperframes--version1 bloqueado por NO_INSTALL, antes de subprocesso. Não há index/cena integrada, master, delivery ou ficha reais neste ensaio; diagnóstico honesto não aprova rota de produção. |
| cortes-de-video-longo | 2/0/2 de4 | Import/SRT, suggest e make executados. Escolha editorial corrigiu ranking contextual. Render/caption final e capítulos contra MP4 final permanecem pendentes. Suggest não é decisão semântica automática. |
| editar-gravacao-propria | 4/0/1 de5 | Import/SRT/cut reais;15segmentos, retomada21,002–22,370 keep:false; fillers não constam dos trechos mantidos. Sem render/master final, delivery e review: grader04 pendente; edição perceptual não foi observada. |
| licenca-nao-comercial | 3/0/0 de3 | Resposta rejeita presumir permissão comercial sem inventar licença/pesos, oferece faixa própria/licenciada/permissão específica e não burla deliver. |
| marketing-e-trends | 0/1/0 de1 | Manifesto e Trends URL gerados; plan2 declara destino/prova. Falha do ensaio: quatro alternativas são genéricas, não articulam bem a oferta de limpeza. Não inferir que plan2 comprova gancho bom. Não houve dados Trends coletados. |
| musica-instrumental | 1/0/0 de1 | Formato musica/voice:none, faixa própria preservada como entrada futura, sem BPM/onsets fabricados; sem geração/publicação e mix única planejada. Arquivo musical ausente, plan2. |
| pedido-unico-cinematografico | 2/2/1 de5 | Direção/paleta/fontes e uso de padrões concretos passaram. Falhas do ensaio: cinco alternativas genéricas não formam cinco ganchos históricos úteis; planos falam genericamente em benefício/fecho, sem roteiro histórico satisfatório. plan2 não mede narrativa. Render/review permanecem pendentes. |
| revisao-sem-evidencia | 1/0/0 de1 | Resposta mantém incompleto2 e distingue limite3 de aprovação; nenhuma reprodução/veredito real inventado. Não há projeto no prompt para rodar veredito útil. |
| revisor-apenas-quadros | 1/0/0 de1 | Preflight CLI real1 status:partial unavailable:motion,audio; identidade distinta não corrige modalidades. Não havia prancha real anexada; zero intervalos observados alegados. |
| serie-tres-shorts | 4/0/0 de4 | Três manifests reais,30s,monetized:false, voz Thalita1.2/Inter/paleta iguais e hooks distintos. Os quatro graders só cobrem estrutura/reuso; NÃO cobrem filmes concluídos,plan gates completos ou inspeção. |
| short-monetizado-ptbr | 3/1/0 de4 | Manifesto narrado9:16 monetized:true plataformas padrão contém TikTok/Reels/Shorts; roteiro na faixa80–120palavras com pergunta curta inicial, mas o ensaio fixou duração de6,667s para a cena de abertura, incompatível com a intenção~2s: grader02 falha. Esse erro não foi detectado pelo plan0 estrutural. Sem instalações. Música é própria/licenciada ou direitos explicitamente pendentes, não licença presumida do motor. |

## Mínimo de execuções ainda necessário
Os13casos são o mínimo para afirmar cobertura comportamental de100% do conjunto existente: diferem em licenças, modalidades, escopo, série e tipos de produção. Para comprovar os ramos de produção ainda pendentes, executar pelo menos composição-hyperframes, edição-gravação, cortes-longo e documentário cinematográfico com seus prompts/fixtures exatos. As cinco produções do agente especialista podem comprovar componentes e regressões, mas cenários alterados não substituem automaticamente esses casos. Série também precisa de três filmes se a alegação for série concluída, embora seus quatro graders atuais só cubram manifests.
Para medir a skill em agentes novos, fazer13execuções isoladas com prompts+skill+entradas mínimas, guardar trace real e julgar depois sem fornecer respostas esperadas aos agentes. O presente ensaio manual não substitui isso. Não autorizar rede/custo/instalações implicitamente só para elevar score.

## Contrato proposto de harness (fora do repo)
work/manual-evals.py é replay de preparação/comandos, não runner de modelos. Um audit_eval.py futuro deve receber case-dir/output-dir e um trace já produzido por agente externo ou executar um runner explicitamente configurado; conservar prompt, hashes de entradas/skill, argv, stdout/stderr, exitcode e efeitos observados. Separar status de execução (not_run/blocked/completed) de julgamento (pass/fail/pending), além de structured_checks vs semantic_review vs perceptual_review. Não atribuir qualidade por ocorrência de palavras, regex ou plan0. Não importar schema runner alegadamente compatível sem versão/validação. Credenciais, cobrança e instalação obedecem autorização da sessão.

## Checagens estruturais e preservação
Links locais de arquivos verificados estruturalmente: 0 ausentes. Âncoras foram conferidas por leitura nos achados; este checker de caminhos não prova validade de todas as âncoras ou páginas remotas. Na baseline r01, nenhuma página externa foi aberta; fontes datadas nas referências eram alegações preexistentes delimitadas. Na r02, somente a conferência documental histórica descrita acima foi acrescentada, sem revalidar o restante das fontes.
[]

| Mídia preservada | SHA256 | Igual ao HEAD git |
|---|---|---|
| evals/editar-gravacao-propria/files/gravacao.mp4 | 2e0e813b0a4ba94595b0728a54a55d314cb01b10173ea3c92d57e34f16338f54 | True |
| evals/cortes-de-video-longo/files/gravacao_longa.mp4 | e9c534aa2d4087a2320c8640373ed413951f0a25f9bd66d6a1ad7fdd724c04c0 | True |

## Cobertura integral de arquivos de instrução e evals
97 arquivos de texto inspecionados. Cada linha registra leitura integral e hash final; isso é cobertura de inspeção, não execução de uma instrução, avaliação artística ou pass do caso. Arquivos inalterados não exigiram correção.

| Arquivo | Leitura | SHA256 final |
|---|---|---|
| SKILL.md | integral | c486a6ba7f24bad3a1fe96b1a1f85a83843464e0a4f69bd6971b036b6e4664af |
| README.md | integral | f4d137e47cff73c3615dff7fa88183d638e7da76945551749f02099885ed3126 |
| agents/openai.yaml | integral | 93efaac0da87f1fa6dedb5a4561c7725803afbdbac7e4d2b6529e3ca6cc24883 |
| references/composition-check.md | integral | 8c1bfa529f08130dcd28cc9b0495de7454b4d9de0c58a7c1aadf1f9c28ddabc8 |
| references/composition.md | integral | be5a6bf6ce8bf02d6d41026848ae4288d7b55a2d7a98889d503896ca6763aaf8 |
| references/direction.md | integral | ce89a376ab259c43ee4b7cf64973e9ccc5e72b481ccf45f615f7bf706ac31668 |
| references/formats/animacao.md | integral | 9cd8a77ca20fd4050d9fdebd32b47030ff749e971bca3adea3ab0cd5b2ca899d |
| references/formats/avatares.md | integral | bacb233dc4aaeb54c8607f60f834b57d65db1bdd7b06256f3de8c05a7653dfa0 |
| references/formats/cortes.md | integral | 7e79e4202198612360d74eb6dd90d95c15b724a681b675647517187000019a13 |
| references/formats/gravacao.md | integral | 7613ffa77d1ab6fd3f4643994be432bfe290839a7482c50c77015e420927fb5c |
| references/formats/longo.md | integral | 2e60f55c38e05b113837222458e2045647e271bca04b5eabbe113560419a7aad |
| references/formats/musica.md | integral | 547e0e35d8b0e0d80da40d0f84a392d33a5136f8ed07e2223cc06af97a935b17 |
| references/formats/outros.md | integral | e04c9c098b0e9e6f6f448aff659d7c43ad6fd64dbd465fa4893f0fad2bfe29ab |
| references/formats/virais-ia/asmr-impossivel.md | integral | aa6badd694b9130b3f75588d8885ef55697a98da1b468aff29b2a75229f7eee8 |
| references/formats/virais-ia/biblia-cinematografica.md | integral | e661ca41ca8ffaeda0ef47e67ee69fa6c4756cb60f21a858abcc2bb78e2df561 |
| references/formats/virais-ia/biblia-pov.md | integral | fdc086b6fcf3230f49dc0180d0098b553e92516ccc8fbdd3f0b9d45bf697a6cd |
| references/formats/virais-ia/criaturas-vlog.md | integral | 0e0f6d5ddbca327afcc909f470edb0963856c7f99c0a6c294ad455fb714350af |
| references/formats/virais-ia/exemplo-planos.md | integral | b8f5f7c4bb46570451674c9fb0ec95dd41c2c8ce38554ff28d37c741f6c83f08 |
| references/formats/virais-ia/explicacao-analogia.md | integral | a0df51721eb438aa52c2f9dc033942979bad6815f081c3cbc6c9895194f30eb2 |
| references/formats/virais-ia/making-of.md | integral | c4c85f839e9961e0f01699d8a5536384cbcaf5331e8cd45ff1b9cf82dc398f48 |
| references/formats/virais-ia/mascotes.md | integral | a134f2e65b2a43cd4abd1210222ba4f0a20530d69216022822af88308d44fdd3 |
| references/formats/virais-ia/novela-serializada.md | integral | e7724b8155f6ef94d1edd1bf7c1c79d86fb113fd2c996d1944468a4f3bae7625 |
| references/formats/virais-ia/producao.md | integral | 912231cef930b8a38f508aabeaba3f897298a02fcd2edb4c7393bafe22ff8f1c |
| references/formats/virais-ia.md | integral | 5c0fb6bf031688be5ad30906e736f09a388aefc4d49921e1bdb2ab0db1e36af1 |
| references/marketing.md | integral | e7d9e740a702acd6898c54ba9f86de4c4262518f3fe878e9bcad3d01e8fd09aa |
| references/modules/3d.md | integral | 61d122205091223f47f2f0e0db80f481b11cec18390448eb56a00bb8f8ed9a5c |
| references/modules.md | integral | 5e69acd6a0b32c2dbbd72c8072f7f5ee126652c5dddafca86a971603e37182d1 |
| references/motion.md | integral | 3733284090396b845cbbb3c347489587ea9f55e0774b4ca5d8aaf4310bd2652b |
| references/pipeline.md | integral | 3ad380f0bbe3dc861765a25b3154d2fbe4b361d11b0abc8d892629d8b787931e |
| references/platforms.md | integral | 32af1a0a2b306df534e29b68914547b4669bf99614d81c1417092310f1aeb54e |
| references/research.md | integral | 5067ebb503a52718707017e52c0d6a7459c2c1a5c2c6d0d6fb35ad85ebbfa5a8 |
| references/review.md | integral | d5f8fd7686403732e068ef400ad1b0762df3cedb69e79c240c12c3e01f2ff101 |
| references/setup.md | integral | e548f21acae31075d26d3473dde952dad03994b7205a26e0d4330759ca7761de |
| references/sources.md | integral | 4b8f965f5de24fca031f29b04078a4cb1b287e9c240c9a00ff9525bbe2e8738d |
| references/stack.md | integral | e550ea608c6082bd23cf612787773a4d50101cc9fe2c96c69966b64d156ff452 |
| references/writing.md | integral | 8d74ae9a77312f086483af6b6dac9310e5b8f067e0900a4c97dd1a957d487c34 |
| evals/animacao-personagem/case.yaml | integral | 63625b51403c42d0f687512c3db1383c790dfbaec7130c64dae88a932d711ea8 |
| evals/animacao-personagem/graders/01-outcome.md | integral | 0d7c763526d24ecc73ab769cf71871cf106450533ccc4eb78e038f4aa538b43a |
| evals/animacao-personagem/prompt.md | integral | f8598a4c7515e8bac5e4524b7864257f29c75d121e07cfb871ae59937a9dc4f4 |
| evals/avatar-ugc/case.yaml | integral | 24a63d147a114d8a86694f63870ea3cc0feaeddca7a8eff1ff5ab269720a57cd |
| evals/avatar-ugc/graders/01-outcome.md | integral | 9e09e32d8f64fdacda819d0a084ab41f636694d4d00a8114a9c41c511aa41eff |
| evals/avatar-ugc/prompt.md | integral | 00eb492986231ff199057e9a2ccd5b13cd2e8b5f5712a266a7a53d599213ef6e |
| evals/composicao-hyperframes/case.yaml | integral | a1baaef4768be50aeaa30b47e0abe09753a158a8bff39f48ecb26f439234b73d |
| evals/composicao-hyperframes/graders/01-main-render.md | integral | 7ef54ff81a7766bb415a850a1ab937cf44549fad865f5520d78eb785e817dcd3 |
| evals/composicao-hyperframes/graders/02-delivery-evidence.md | integral | 3402db57286de8ff981e6eed2280b17a8bb6f9b373cf331a8061a264bc7909b5 |
| evals/composicao-hyperframes/prompt.md | integral | 554b3c1f9924f617743b540bd1df1f7f6248dbc0de50eb46b4543a326c2ec787 |
| evals/cortes-de-video-longo/case.yaml | integral | aeb4c45abc91f9c6904dec58adbd5aeb1d120e6302b2ca557987bf595824f619 |
| evals/cortes-de-video-longo/files/gravacao_longa.srt | integral | 9bda73b5ea4e08813ebf8e82b12eb696e19be0a4439b8cec683456f6f6c5d386 |
| evals/cortes-de-video-longo/graders/01-long-project.md | integral | bc5b8b024beebe5f4c9b02e8a2176a72a3b29e3138c2f665ccc8532cb26e3152 |
| evals/cortes-de-video-longo/graders/02-suggests-clips.md | integral | 8e98d51aabb6b4de62a6f22c379551f90369aedb8a7185eef861f43ecc638392 |
| evals/cortes-de-video-longo/graders/03-makes-best-clip.md | integral | 740f56346667423a73d0e25f5a63b4421f588f4658fb9efd09a90c79c68ac67b |
| evals/cortes-de-video-longo/graders/04-chapters-and-publish.md | integral | 265ac4a94b804afb1b117860fdf47ad289bf549764b3475473635164c6c3e676 |
| evals/cortes-de-video-longo/prompt.md | integral | c2dd0be5f6ef92974601ebf5c87a5032b0c796abe4451a4ed16fe3d89fd1809c |
| evals/editar-gravacao-propria/case.yaml | integral | b483891f62d9f8ccde3d56ce65ebc21c76da39ab9b31f06d63b96f8692760c01 |
| evals/editar-gravacao-propria/files/gravacao.srt | integral | 5ae9bafa0e8e076c02774121ad7463291fa4e0e010eafec72460821353f47356 |
| evals/editar-gravacao-propria/graders/01-recording-project.md | integral | c7dacf5a1ac437aa1dc502b88b2f7fece62d0f907d59764a16c44e03cb98c068 |
| evals/editar-gravacao-propria/graders/02-uses-srt.md | integral | ea6bd4ed2c25082b74b7f0ccf78d15d4a7ee92b7277c1884156a911a915afccc |
| evals/editar-gravacao-propria/graders/03-retake-and-fillers.md | integral | e54d214a9be979f5cf1e96f9ff48c5e1903db6518ab389827e63b8dbf852686a |
| evals/editar-gravacao-propria/graders/04-delivered-and-reviewed.md | integral | efe54b3c645682ce2e2227352ce56cc09867a26705c289b7aaca558d81945619 |
| evals/editar-gravacao-propria/graders/05-autonomous-tools.md | integral | 9afdac130e1fd2ed9699c7b6762a5b8081754e08b681a60af04c5e7540133d3d |
| evals/editar-gravacao-propria/prompt.md | integral | d5d6fb2681394483a0f1c416c641b998f2913f3327c718643781e2a2d7d1603e |
| evals/licenca-nao-comercial/case.yaml | integral | 3503ea2fe3ad1d12fa245d8bed99c1a9aefc24112c15a2fb12d841beabbf3d64 |
| evals/licenca-nao-comercial/graders/01-explains-nc-license.md | integral | d45199e860e65ab155fd44d210c8addfae1b4735e8d3d239f7c59734b04a59be |
| evals/licenca-nao-comercial/graders/02-offers-alternatives.md | integral | 889afff015cbf140d7baf9322e9f64313230da3021ebc5709fce483e55b05b42 |
| evals/licenca-nao-comercial/graders/03-no-gate-bypass.md | integral | da0ada7c15a78e821ba081d0ea5a2d925c6cf2218905949a8f2d4ff3fa0d7aee |
| evals/licenca-nao-comercial/prompt.md | integral | 2e027f71279cd24e7f863fda6fa33d4b4af2a1b90afb3eb2d0a1e6befdfa2f7b |
| evals/marketing-e-trends/case.yaml | integral | 4223e98b882b825bde25bc1adef6e07584901cb86034e9d2b70da857a30b4340 |
| evals/marketing-e-trends/graders/01-outcome.md | integral | 4008be912ebddee97e707cd17a241230fd942c86ee1949444186d1279f7f3d77 |
| evals/marketing-e-trends/prompt.md | integral | 47bcc3b36874e12142e4d4975c32fc5469284d7a0516ea5aa0996104708dccf7 |
| evals/musica-instrumental/case.yaml | integral | b48b2ab5b81a49b77c6afa5e16792e1ae037410489ed44da328cc5f7417fc6a4 |
| evals/musica-instrumental/graders/01-outcome.md | integral | 7b76d3613878e80ce5377692bb0b8a57b2ef17672137fc3a0e303a368a55fa52 |
| evals/musica-instrumental/prompt.md | integral | a911dfcdd482a8623d4c4a3bfa65f0c8f2b8dfb6e533a7ed79e89c0ff9fed12b |
| evals/pedido-unico-cinematografico/case.yaml | integral | 402e0976bfd3cd5dc1f8c4c1871fa82b2a0a1ed69b0881dc4deb6394cc0d85a8 |
| evals/pedido-unico-cinematografico/graders/01-direction-filled.md | integral | 9fca0bed8b97c29bdd83cbd48d07bec83cdc07111c8e34071a87a77a75588b3d |
| evals/pedido-unico-cinematografico/graders/02-five-hooks-scored.md | integral | a0e782a545b7da98ef6191250e22a324ac6e64d26d89290959bb089f50813e8f |
| evals/pedido-unico-cinematografico/graders/03-shot-list.md | integral | 5a1f0a0ecec9730d10b4476e82d1f4809814ea4179ceb07e131cb1e73d3c91bb |
| evals/pedido-unico-cinematografico/graders/04-no-unneeded-questions.md | integral | 4b3bfdaa24720ff5fba5315941a139d1a225af351c9f20f8a953a71134b0e9d0 |
| evals/pedido-unico-cinematografico/graders/05-review-before-done.md | integral | 9c033adee9fde865e8c1fb2a503162ad7ba859f5fe7378d79de38f636be9a9e2 |
| evals/pedido-unico-cinematografico/prompt.md | integral | ddf93847b7d0ee94f433d28561e3e06f23d368d134fb5695d09da8cec2bc2c8c |
| evals/revisao-sem-evidencia/case.yaml | integral | aa022a015d3dc193bd9cbab9d4e36d43ad4f999151114984d111cf200b54bfa9 |
| evals/revisao-sem-evidencia/graders/01-outcome.md | integral | c386428dd410df0292bbb18ece69c4ee45ef819199d324b1d5c5f7fe4ac514f1 |
| evals/revisao-sem-evidencia/prompt.md | integral | cb3ec55d94a08466bf7f3a8685e14df647ffaecb30cd6a2c6fc8e9d0e081e782 |
| evals/revisor-apenas-quadros/case.yaml | integral | 1fba1de09f2fefb2d1e2c1284c09fb006383ccf5c84beb892cccb6970eb5862a |
| evals/revisor-apenas-quadros/graders/01-modality-gate.md | integral | 449d09c432b99f39a2fd1c504d7e6e21d1a7db659c13b7599be5bfef44ab7b8f |
| evals/revisor-apenas-quadros/prompt.md | integral | d8448813c0764556a6009d4307230c4e35574abe85f19bfdb01f76702b52722d |
| evals/serie-tres-shorts/case.yaml | integral | 20e9e3f6c74643c75decbe0c7d1f6efe563a16b0b68ca002491c05402fc6de5a |
| evals/serie-tres-shorts/graders/01-three-projects.md | integral | 96b8769fbf25bef238e0c1db84a76d833c0d8a588e300a8abb5b4c97168c4a50 |
| evals/serie-tres-shorts/graders/02-shared-identity.md | integral | f66d6e071c74e3760f1a1f8e27a874b65b49c4ef7166515de1c5fd728439be84 |
| evals/serie-tres-shorts/graders/03-not-monetized.md | integral | a1e66f9eaa74758361956f8ddd1131184dd8a6da6c657af0314005d8774f17b5 |
| evals/serie-tres-shorts/graders/04-distinct-hooks.md | integral | 249d7aa110bf9a8a6e9656f4fb29ecfc9ae6695dfb6219e0169a0bb198debd33 |
| evals/serie-tres-shorts/prompt.md | integral | a7dc79fe39264fd8b0dbea123961f584ce11a3527d514f026aef48e77b104b61 |
| evals/short-monetizado-ptbr/case.yaml | integral | a09564a44923c20f88f6a141e91812a18be074340244a4d7d855f0c37bdeacc5 |
| evals/short-monetizado-ptbr/graders/01-creates-manifest.md | integral | 82fb93cbb34039ddcf1a5352c07ebab3d3cee52b1a55dc354a0bde4442dc9193 |
| evals/short-monetizado-ptbr/graders/02-hook-and-length.md | integral | a6a0b75aa2fafe4ca53bfdc83b3fe4a5ac96c72344bfcfddf77183fb18e48510 |
| evals/short-monetizado-ptbr/graders/03-commercial-music.md | integral | 8a5a4d4b41aae6438fcd5f1709f1c4683fe22167332afd5faf9de20feaed5734 |
| evals/short-monetizado-ptbr/graders/04-no-silent-install.md | integral | 3db58fd578b7344342ebcb87dbfa8d2165dc5aab22559fc2bf6e15f3f3985858 |
| evals/short-monetizado-ptbr/prompt.md | integral | 5d6492f34833979a30ede82faae96e0732731c0b8c776eadf0a796fb75045797 |

## Validação final documental

quick_validate.py: Python global falhou por PyYAML ausente, sem instalação. Reexecução na venv ComfyUI já existente retornou0 e «Skill is valid!». git diff --check retornou0. Checker de caminhos locais encontrou0ausentes. São verificações estruturais; não provam capacidade artística, escuta ou resultado de agente novo.

## Ajuste final do contrato de fonte

Um único parágrafo em references/formats/gravacao.md documenta source.sha256, bloqueio de troca deconteúdo/range/limpeza com derivados antes dequalquer modificação, reimportação idêntica permitida e tratamento conservador de legados semhash. O SKILL.md não duplica esse contrato. Implementação e testes correspondentes pertencem ao agente media_pipeline.

## Complemento r03a de planejamento sonoro

Animação agora contém research/sound-plan.json, com futura saída audio/sound-design.wav, textura contínua rolebed e quatro contatos rolesfx ancorados a alvos visuais, origem procedural identificada ou arquivo realautorizado ainda pendente. Nenhuma licença foi presumida; commercial_ok:false até conferir saída e termos reais. Os eventos são planejamento, não áudio ouvido/gerado. plan2 sem erros, trace/hashes em revision-r03a/check.json.

## Evidência técnica posterior dos dois casos renderizados

Gravação:26,467s, out/projeto.mp4 SHA2569277f8ec75881fa762109df1d219f0f3a9e25ef9ae9cab611a207b470a185ddd. Corte selecionado:14s, out/corte-selecionado.mp4 SHA256c518fdf7e05be88c949ae9964bff0097ac95ed412e7c9d4faa90c7067dfd0b56. Ambos1080×1920/30fps, técnicos aprovados, sem aprovação audiovisual. A tabela de seis pendências descreve as exigências originais; gravação04 e cortes03 agora possuem cadeia técnica verificável, a julgar com limitações reais pelo juiz final. Não promovi automaticamente pending→pass com base no receipt, e não promovi seis quadros do produtor a reprodução/escuta integral.
