# Avaliação independente

Inicial: {'fail': 5, 'pass': 25, 'pending': 3} /33 graders; {'fail': 4, 'pending': 2, 'pass': 7} /13 casos.
Final: {'pass': 29, 'fail': 4} /33 (87.88% pass); {'pass': 10, 'fail': 3} /13 casos.
Caso pass exige todos graders pass; pending se resta evidência ausente; senão fail quando há falha.
Faixa2 sol/medium provisório, sem custo/capacidade/latência. Ensaio manual revisado após feedback; não é teste de agentes novos e não comprova aprovação audiovisual.

## initial
### animacao-personagem: fail
- 01-outcome: **fail** — História e continuidade estão propostas, mas não há plano por shot de atuação/ferramenta nem critérios concretos de acabamento e registro da função sonora conforme exigido. Menção genérica a quadros/seek não inclui tempos de estilo e protocolo completo de pixels/fronteiras. Escopo de plano respeitado.
  Evidência: response.md: Bíblia Bia, rig reutilizado, seed não prova continuidade; três quadros/seek e reserva D=30 seed191; projeto/video.json: tool_plan contém só montagem genérica; shots repetem sujeito/enquadramento por intenção; assets=[]
### avatar-ugc: fail
- 01-outcome: **fail** — Bloqueio e ausência de pago/depoimento estão corretos; porém o preparo disponível não define performance, gestos, comparação de passagem com formato-alvo, checks de boca/voz ou acabamento/fecho concretos. Honestidade não substitui todos os requisitos do plano.
  Evidência: response.md: vídeo falante/lip-sync bloqueado; robô imóvel seria animatic; início/meio/fim; projeto/video.json: s02 Entender o uso real do app; s03 Fecho que responde à pergunta; shots genéricos; direction.style=tipografia-cinetica
### composicao-hyperframes: fail
- 01-main-render: **fail** — Faltam composição principal, cena2D integrada, master e teste real três quadros/seek/pixels. Rubrica explicitamente diz bloqueio honesto não prova caminho de render concluído.
  Evidência: commands.json: stack.py hyperframes -- --version exit1 sob NO_INSTALL; response.md: Render principal não executado; voz/WAV ausente; projeto/video.json é único artefato de projeto disponível
- 02-delivery-evidence: **fail** — Não há cadeia master→deliver→review com hashes nem ficha independente em branco. Não há fabricação de escuta/render, mas isso não satisfaz artefatos exigidos.
  Evidência: response.md: Sem master não há entrega técnica aprovada, ficha gerada ou veredito0; não existem delivery.json, review, assessment ou ficha humana
### cortes-de-video-longo: pending
- 01-long-project: **pass** — Projeto longo e importações reais demonstrados.
  Evidência: commands.json: new_project --format gravacao --aspect16:9; footage.py import exit0; captions.py import --file gravacao_longa.srt exit0; projeto/video.json: source.duration197.267; captions/source_words.json301palavras
- 02-suggests-clips: **pass** — Três candidatos com tempos e justificativa editorial, incluindo limites, apresentados.
  Evidência: commands.json: clips.py suggest --top5 exit0; edit/clips.json e clips.md; response.md: rank1 1:19–1:54 pergunta contextual; rank2 0:55–1:17 assunto identificável; rank3 0:09–0:32 lista coesa
- 03-makes-best-clip: **pending** — Criação comprovada; render, legendas, acabamento e proveniência finais aguardam processamento e inspeção.
  Evidência: commands.json: clips.py make rank1 exit0; corte-selecionado/video.json source.range8.48–32.67; aspecto9:16 formato corte; render sendo executado; ainda sem final inspecionável na leitura inicial
- 04-chapters-and-publish: **pending** — Estrutura e espaçamento corretos, mas rubrica exige tempos conferidos no MP4 final; render longo não demonstrado.
  Evidência: projeto/video.json: publish.title/description; chapters00:00,00:47,02:02; response.md declara capítulos provisórios no relógio original
### editar-gravacao-propria: pending
- 01-recording-project: **pass** — Importação executada pelo script da skill.
  Evidência: commands.json: new_project gravacao9:16 --not-monetized exit0; footage.py import gravacao.mp4 exit0; projeto/video.json source aponta fixture de47.3s
- 02-uses-srt: **pass** — Tempos vieram do SRT fornecido, sem bloquear por ASR ausente.
  Evidência: commands.json: captions.py import --file gravacao.srt exit0;65palavras interpoladas; captions/source_words.json e words.json
- 03-retake-and-fillers: **pass** — EDL remove vícios, pausas e primeira retomada, conservando uma tomada completa. transcript.md anterior ainda lista c07 sim, mas EDL atual é determinante.
  Evidência: commands.json: footage.py cut --fillers ahn,éé,hum exit0;41%cortado; edit/edl.json c07 keep=false21.002–22.37; c08/c09 mantêm tomada posterior23.896–26.929; intervalos dos três vícios omitidos comparados ao SRT
- 04-delivered-and-reviewed: **pending** — Aguardar final e review; HTML aponta risco real de ocupação insuficiente e falta de variação. Não conceder aprovação por check/lint.
  Evidência: render/render-hyperframes.log em execução; sem entrega/verdict final na leitura inicial; composition/index.html data-has-audio=true; arroll top300 height930 contain; EDL zoom1.0
- 05-autonomous-tools: **pass** — Prossegue com ferramentas e SRT disponíveis, respeita no-install; render atual não é repetição inalterada demonstrada.
  Evidência: commands.json: import, SRT e cut reais, sem instalação; work/manual-evals.py:4,7 define VIDEO_VIRAL_NO_INSTALL=1 e passa env a subprocess.run
### licenca-nao-comercial: pass
- 01-explains-nc-license: **pass** — Não inventa CC-BY-NC, pesos ou termos.
  Evidência: response.md: restrição não comercial não permite presumir autorização para canal monetizado; licença exata não fornecida
- 02-offers-alternatives: **pass** — Alternativas adequadas com direitos reais condicionais.
  Evidência: response.md: faixa própria/licenciada ou permissão comercial expressa; Tone.js/ACE-Step não autorizam faixa automaticamente
- 03-no-gate-bypass: **pass** — Nenhum bypass recomendado.
  Evidência: response.md: não marcar commercial_ok true sem prova nem usar draft como licença
### marketing-e-trends: pass
- 01-outcome: **pass** — Planejamento contextual salvo; URL sem métricas coletadas, indisponibilidade declarada; sem prova/destino inventado, instalação ou publicação.
  Evidência: projeto/video.json: brief oferta limpeza SP, objetivo conversao, CTA WhatsApp, faltas proof/cta_destination; cinco hooks audiovisuais específicos; hook selecionado igual s01; commands.json: plan.py exit2 errors=[]; trends.py BR-SP today3-m exit0 fornece URL oficial; response.md: interesse de busca relativo não é retenção/conversão/vendas
### musica-instrumental: fail
- 01-outcome: **fail** — Respeita plano/ausência de fala e não inventa geração. Porém não desenvolve estrutura musical e sincronismo por elementos medidos/a medir, nem acabamento e fecho exigidos; blocos arbitrários10s não bastam.
  Evidência: response.md: sem arquivo/beat grid; sincronizar três blocos por energia após medir/escutar; voz none, música uma vez; music.py clienteACE-Step; projeto/video.json: três blocos idênticos10s com cue início do bloco musical; sem plano de fecho ou acabamento específico
### pedido-unico-cinematografico: pass
- 01-direction-filled: **pass** — Direção documental, cores, fontes e escolhas de movimento/transição/som preenchidas.
  Evidência: projeto/video.json: direction.style=documentario esquematico; palette3; fonts title/captions Inter; motion13planos; transitions corte/máscara; sfx pulso/impacto
- 02-five-hooks-scored: **pass** — Cinco hipóteses audiovisuais pontuadas; selecionada aparece na primeira cena.
  Evidência: projeto/video.json: h1–h5 scores com razões; h1 Como Constantinopla caiu?; hook e s01 usam mesma pergunta
- 03-shot-list: **pass** — Progressão e escolhas sonoras concretas; rota diagramática honesta adequada ao documentário solicitado sem inventar exigência de realismo não explícita. Sem crédito de execução perceptual ou áudio gerado.
  Evidência: projeto/video.json: seis cenas com1/2/3/3/3/2shots: mapa→muralha/artilharia→calendário→entrada→consequência; sfx por reveal/transição; direção identifica esquema, não filmagem histórica; direction.music_mood: cama licenciada ou reserva sintetizada identificada; tool_plan master + voz única; response render bloqueado
- 04-no-unneeded-questions: **pass** — Assume padrões e segue sem perguntas redundantes.
  Evidência: response.md sem perguntas; video.json pt-BR,35s9:16 e pressupostos históricos/temporais registrados; commands.json executa new_project/plan sem pausa
- 05-review-before-done: **pass** — Aplica alternativa explicitamente aceita pela rubrica: informa etapas incompletas e não declara filme profissional aprovado. Este pass não equivale a filme concluído.
  Evidência: response.md: Render principal não executado; Sem master não há entrega técnica aprovada, ficha gerada ou veredito0; commands.json: plan exit2 missing voice_wavs; wrapper HyperFrames exit1 bloqueado
### revisao-sem-evidencia: pass
- 01-outcome: **pass** — Rejeita aprovação sem inventar evidência.
  Evidência: response.md: Só notas4 não aprovam; código2 incompleto; código3 nunca aprovação; não rodei review nem assisti/ouvi mídia ausente
### revisor-apenas-quadros: pass
- 01-modality-gate: **pass** — Distingue capacidade/observação e recusa inferir modalidades ou aprovação.
  Evidência: capabilities.json: visual available; motion/audio false; commands.json: review.py --check-reviewer exit1 statuspartial unavailable motion/audio; response.md: quadros não provam movimento, LUFS não prova escuta; aprovação audiovisual pendente
### serie-tres-shorts: pass
- 01-three-projects: **pass** — Três projetos separados conforme escopo estrutural do grader.
  Evidência: episodio-1/2/3/video.json: três manifestos target_seconds30
- 02-shared-identity: **pass** — Identidade/voz/legendas compartilhadas documentadas.
  Evidência: Três video.json compartilham ThalitaMultilingual speed1.2 e captions Inter88; response descreve componentes/fontes compartilhados
- 03-not-monetized: **pass** — Não monetizados.
  Evidência: episodio-1/2/3/video.json: monetized=false
- 04-distinct-hooks: **pass** — Aberturas distintas; não prova conclusão da série.
  Evidência: s01: Buracos negros não são aspiradores / Luz também tem um limite / Como enxergar o invisível
### short-monetizado-ptbr: pass
- 01-creates-manifest: **pass** — Manifesto real com valores exigidos.
  Evidência: projeto/video.json: format narrado9:16 monetizedtrue target40; platforms tiktok/reels/shorts/kwai; commands.json new_project exit0
- 02-hook-and-length: **pass** — Gancho proposto para0–2s e92palavras dentro80–120; tempos são alvo, sem falsa medição.
  Evidência: projeto/video.json: s01 Por que o céu é azul? start0 duration2; seis cenas com98? palavras; contagem independente por separação whitespace:92palavras totais; suposição de reancorar áudio medida registrada
- 03-commercial-music: **pass** — Direitos pendentes explicitamente; não exige geração neste plano.
  Evidência: response.md: Música própria/licenciada ou termos reais dos pesos/áudio ainda a verificar; licença motor não é da faixa
- 04-no-silent-install: **pass** — Constraint de instalação respeitado; não houve necessidade de executar HyperFrames para montar projeto/roteiro.
  Evidência: work/manual-evals.py:4,7 env VIDEO_VIRAL_NO_INSTALL=1 passado a subprocess.run; commands.json só new_project/plan; response informa setup_tools.py voz sem executar; nenhum CLI direto/pagamento
## reassessment
### animacao-personagem: pass
- 01-outcome: **pass** — Agora há história/ação/continuidade e plano concreto por shot. Quadros, seek e inspeção integral são metas honestas de planejamento, não execução. Critérios de caixa/fonte/área útil e fecho estão previstos; reserva sonora parametrizada registra função futura sem fingir ativo. Realismo não foi solicitado; capacidade local identificada como animatic determinístico.
  Evidência: response-r03.md: p01–p07 entrar/frear/olhar/testar folha/pedir ajuda/travessia/entrega/favor; ferramentas por plano; projeto/research/continuity-plan.md: mesmo rig, referências de pose, orelha/bolso, escala1:0.35 e eixo; seed não prova identidade; projeto/research/sound-plan.json: planned_only; caminho futuro audio/sound-design.wav; papéis bed/sfx, receita30s seed191 whooshes1.5s, contatos, direitos e escuta pendentes; não cria asset concluído; response-r03.md: quadros0/12/24, seek2→0→2 e17→0→17; response.md exige comparar pixels e quadrosMP4
### avatar-ugc: pass
- 01-outcome: **pass** — Avança no preparo disponível e preserva avatar falante solicitado, sem gerar substituto inferior. Início/meio/fim, passagem de performance, acabamento/cama discreta e fecho têm plano; não inventa produto, cliente, render ou escuta. Pass é de preparo/bloqueio, não geração.
  Evidência: response-r03.md: performance0–5/5–26/26–35 com olhar/pausa/gesto, demonstração estado-inicial→ação→resultado e hierarquia produto70–80%; source-in/out pendente; projeto/research/performance-and-sync.md: boca/WAV, bilabiais, dentes/língua/olhos/cabeça/mãos nos intervalos0–5/10–13/21–23/29–33 e integral; sem retimar produto para disfarçar erro; projeto/video.json: pendências reais e roteiros por plano; response-r03+response original bloqueiam gerador/serviço pago e robô imóvel como final
### composicao-hyperframes: fail
- 01-main-render: **fail** — Faltam composição principal, cena2D integrada, master e teste real três quadros/seek/pixels. Rubrica explicitamente diz bloqueio honesto não prova caminho de render concluído.
  Evidência: commands.json: stack.py hyperframes -- --version exit1 sob NO_INSTALL; response.md: Render principal não executado; voz/WAV ausente; projeto/video.json é único artefato de projeto disponível
- 02-delivery-evidence: **fail** — Não há cadeia master→deliver→review com hashes nem ficha independente em branco. Não há fabricação de escuta/render, mas isso não satisfaz artefatos exigidos.
  Evidência: response.md: Sem master não há entrega técnica aprovada, ficha gerada ou veredito0; não existem delivery.json, review, assessment ou ficha humana
### cortes-de-video-longo: fail
- 01-long-project: **pass** — Projeto longo e importações reais demonstrados.
  Evidência: commands.json: new_project --format gravacao --aspect16:9; footage.py import exit0; captions.py import --file gravacao_longa.srt exit0; projeto/video.json: source.duration197.267; captions/source_words.json301palavras
- 02-suggests-clips: **pass** — Três candidatos com tempos e justificativa editorial, incluindo limites, apresentados.
  Evidência: commands.json: clips.py suggest --top5 exit0; edit/clips.json e clips.md; response.md: rank1 1:19–1:54 pergunta contextual; rank2 0:55–1:17 assunto identificável; rank3 0:09–0:32 lista coesa
- 03-makes-best-clip: **fail** — Corte real, legendado e renderizado, com proveniência de origem registrada; fundo derivado da fonte ocupa quadro todo e título órfão anterior foi corrigido. Ainda falha exigência explícita de variação de enquadramento/moldura e fonte/elementos essenciais na zona segura. Não reprovo pelo verdict2 isolado nem aprovo áudio/movimento por prancha.
  Evidência: corte-selecionado/out/delivery.json: approved=true,draft=false,14s,1080x1920; r03 metrics/assessment/input hash coincide com MP4; corte-selecionado/review/r03/grid.jpg e hook.jpg: original fixture reconhecível, títulos por argumento, legenda duas linhas sem colisão aparente; Delivery no fim / de semana corrigido; composition/index.html: label top1530 fora y250–1500; review grid confirma posição da fonte; edit/edl.json todos zoom1/x.5/y.5 e composição mantém mesma moldura; corte-selecionado/render/verdict-fullstage.log: revisão humana pendente; r03 assessment canais pending
- 04-chapters-and-publish: **pass** — Longo final definido e inalterado, com identidade binária e duração conferidas. Capítulos no mesmo relógio estão em ordem, primeiro00:00, espaçamento47/75s; metadados presentes. Não é necessário fingir escuta nem render novo do longo para o pedido de subir gravação inteira.
  Evidência: response.md final adota cópia integral sem cortes como longo YouTube, título/descrição e capítulos00:00/00:47/02:02; long-final-proof.json + verificação independente: source/output SHA256 e9c534aa2d4087a2320c8640373ed413951f0a25f9bd66d6a1ad7fdd724c04c0; ffprobe197.266667s; SRT original:00:47.315 e02:02.283 iniciam Agora vamos falar de investimento; relógio permanece idêntico no MP4 final
### editar-gravacao-propria: fail
- 01-recording-project: **pass** — Importação executada pelo script da skill.
  Evidência: commands.json: new_project gravacao9:16 --not-monetized exit0; footage.py import gravacao.mp4 exit0; projeto/video.json source aponta fixture de47.3s
- 02-uses-srt: **pass** — Tempos vieram do SRT fornecido, sem bloquear por ASR ausente.
  Evidência: commands.json: captions.py import --file gravacao.srt exit0;65palavras interpoladas; captions/source_words.json e words.json
- 03-retake-and-fillers: **pass** — EDL remove vícios, pausas e primeira retomada, conservando uma tomada completa. transcript.md anterior ainda lista c07 sim, mas EDL atual é determinante.
  Evidência: commands.json: footage.py cut --fillers ahn,éé,hum exit0;41%cortado; edit/edl.json c07 keep=false21.002–22.37; c08/c09 mantêm tomada posterior23.896–26.929; intervalos dos três vícios omitidos comparados ao SRT
- 04-delivered-and-reviewed: **fail** — Crédito à entrega técnica e revisão vinculada; bloqueio perceptual declarado honestamente satisfaz a cláusula de não chamar pronto e não é motivo isolado de fail. Persistem falhas concretas nas regras de acabamento obrigatórias: título CTA órfão, fonte fora da área segura e nenhuma variação intencional de recorte/moldura. Não há aprovação audiovisual.
  Evidência: projeto/out/delivery.json: approved=true,draft=false,26.467s; hash9277f8ec...; r03 metrics/assessment/input/review se referem ao mesmo arquivo; projeto/composition/index.html data-has-audio=true; render/master.mp4 áudio preservado na fonte única; legenda aplicada uma vez; projeto/review/r03/grid.jpg: mesmo recorte/moldura em toda peça; CTA Qual pesa no seu / orçamento? deixa última linha uma palavra; composition/index.html: fonte/label top1530 fora zona segura; edit/edl.json todos zoom1/x.5/y.5; fundo fullstage corrige ocupação anterior; render/verdict-fullstage.log: entrega técnica aprovada, revisão humana pendente; assessment canais pending e ficha humana em branco
- 05-autonomous-tools: **pass** — Prossegue com ferramentas e SRT disponíveis, respeita no-install; render atual não é repetição inalterada demonstrada.
  Evidência: commands.json: import, SRT e cut reais, sem instalação; work/manual-evals.py:4,7 define VIDEO_VIRAL_NO_INSTALL=1 e passa env a subprocess.run
### licenca-nao-comercial: pass
- 01-explains-nc-license: **pass** — Não inventa CC-BY-NC, pesos ou termos.
  Evidência: response.md: restrição não comercial não permite presumir autorização para canal monetizado; licença exata não fornecida
- 02-offers-alternatives: **pass** — Alternativas adequadas com direitos reais condicionais.
  Evidência: response.md: faixa própria/licenciada ou permissão comercial expressa; Tone.js/ACE-Step não autorizam faixa automaticamente
- 03-no-gate-bypass: **pass** — Nenhum bypass recomendado.
  Evidência: response.md: não marcar commercial_ok true sem prova nem usar draft como licença
### marketing-e-trends: pass
- 01-outcome: **pass** — Planejamento contextual salvo; URL sem métricas coletadas, indisponibilidade declarada; sem prova/destino inventado, instalação ou publicação.
  Evidência: projeto/video.json: brief oferta limpeza SP, objetivo conversao, CTA WhatsApp, faltas proof/cta_destination; cinco hooks audiovisuais específicos; hook selecionado igual s01; commands.json: plan.py exit2 errors=[]; trends.py BR-SP today3-m exit0 fornece URL oficial; response.md: interesse de busca relativo não é retenção/conversão/vendas
### musica-instrumental: pass
- 01-outcome: **pass** — Plano usa identidade e progressão próprias de instrumental, com sincronismo a ser medido sem fingir beatgrid. Preserva faixa/direitos, não impõe fala, não gera nem duplica música. Fecho respeita frase e cauda; escuta integral fica pendente como apropriado ao plano.
  Evidência: response-r03.md: anel/traço→arcos→expansão→retorno→fecho; janelas0–3/3–10/10–19/19–26/26–30 explicitamente provisórias; projeto/research/music-timing-plan.json: BPM/onsets=null; ouvir/medir frases/transientes e registrar método/confiança; trecho fecha frase musical; projeto/video.json: voice.engine none; music.engine none; tool_plan faixa uma vez/master sem áudio; response original reconhece music.py clienteACE-Step
### pedido-unico-cinematografico: pass
- 01-direction-filled: **pass** — Direção documental, cores, fontes e escolhas de movimento/transição/som preenchidas.
  Evidência: projeto/video.json: direction.style=documentario esquematico; palette3; fonts title/captions Inter; motion13planos; transitions corte/máscara; sfx pulso/impacto
- 02-five-hooks-scored: **pass** — Cinco hipóteses audiovisuais pontuadas; selecionada aparece na primeira cena.
  Evidência: projeto/video.json: h1–h5 scores com razões; h1 Como Constantinopla caiu?; hook e s01 usam mesma pergunta
- 03-shot-list: **pass** — Progressão e escolhas sonoras concretas; rota diagramática honesta adequada ao documentário solicitado sem inventar exigência de realismo não explícita. Sem crédito de execução perceptual ou áudio gerado.
  Evidência: projeto/video.json: seis cenas com1/2/3/3/3/2shots: mapa→muralha/artilharia→calendário→entrada→consequência; sfx por reveal/transição; direção identifica esquema, não filmagem histórica; direction.music_mood: cama licenciada ou reserva sintetizada identificada; tool_plan master + voz única; response render bloqueado
- 04-no-unneeded-questions: **pass** — Assume padrões e segue sem perguntas redundantes.
  Evidência: response.md sem perguntas; video.json pt-BR,35s9:16 e pressupostos históricos/temporais registrados; commands.json executa new_project/plan sem pausa
- 05-review-before-done: **pass** — Aplica alternativa explicitamente aceita pela rubrica: informa etapas incompletas e não declara filme profissional aprovado. Este pass não equivale a filme concluído.
  Evidência: response.md: Render principal não executado; Sem master não há entrega técnica aprovada, ficha gerada ou veredito0; commands.json: plan exit2 missing voice_wavs; wrapper HyperFrames exit1 bloqueado
### revisao-sem-evidencia: pass
- 01-outcome: **pass** — Rejeita aprovação sem inventar evidência.
  Evidência: response.md: Só notas4 não aprovam; código2 incompleto; código3 nunca aprovação; não rodei review nem assisti/ouvi mídia ausente
### revisor-apenas-quadros: pass
- 01-modality-gate: **pass** — Distingue capacidade/observação e recusa inferir modalidades ou aprovação.
  Evidência: capabilities.json: visual available; motion/audio false; commands.json: review.py --check-reviewer exit1 statuspartial unavailable motion/audio; response.md: quadros não provam movimento, LUFS não prova escuta; aprovação audiovisual pendente
### serie-tres-shorts: pass
- 01-three-projects: **pass** — Três projetos separados conforme escopo estrutural do grader.
  Evidência: episodio-1/2/3/video.json: três manifestos target_seconds30
- 02-shared-identity: **pass** — Identidade/voz/legendas compartilhadas documentadas.
  Evidência: Três video.json compartilham ThalitaMultilingual speed1.2 e captions Inter88; response descreve componentes/fontes compartilhados
- 03-not-monetized: **pass** — Não monetizados.
  Evidência: episodio-1/2/3/video.json: monetized=false
- 04-distinct-hooks: **pass** — Aberturas distintas; não prova conclusão da série.
  Evidência: s01: Buracos negros não são aspiradores / Luz também tem um limite / Como enxergar o invisível
### short-monetizado-ptbr: pass
- 01-creates-manifest: **pass** — Manifesto real com valores exigidos.
  Evidência: projeto/video.json: format narrado9:16 monetizedtrue target40; platforms tiktok/reels/shorts/kwai; commands.json new_project exit0
- 02-hook-and-length: **pass** — Gancho proposto para0–2s e92palavras dentro80–120; tempos são alvo, sem falsa medição.
  Evidência: projeto/video.json: s01 Por que o céu é azul? start0 duration2; seis cenas com92 palavras; contagem independente por separação whitespace:92palavras totais; suposição de reancorar áudio medida registrada
- 03-commercial-music: **pass** — Direitos pendentes explicitamente; não exige geração neste plano.
  Evidência: response.md: Música própria/licenciada ou termos reais dos pesos/áudio ainda a verificar; licença motor não é da faixa
- 04-no-silent-install: **pass** — Constraint de instalação respeitado; não houve necessidade de executar HyperFrames para montar projeto/roteiro.
  Evidência: work/manual-evals.py:4,7 env VIDEO_VIRAL_NO_INSTALL=1 passado a subprocess.run; commands.json só new_project/plan; response informa setup_tools.py voz sem executar; nenhum CLI direto/pagamento

## Falhas residuais
- composicao-hyperframes/01: no principal composition/render/style+seek proof
- composicao-hyperframes/02: no master/delivery/review hash chain or blank independent human form
- cortes-de-video-longo/03: same framing/layout throughout; source label top1530 outside essential-safe y<=1500
- editar-gravacao-propria/04: unchanged framing/layout; label top1530; final CTA last line one word orçamento?

## Integridade dos renders
Hashes de vídeo, manifesto semântico, delivery, metrics, assessment, request e cópia input coincidem nos dois r03. SHA bruto do JSON é distinto por formatação/review; segue registrado separadamente.
```json
[
  {
    "project": "editar-gravacao-propria/projeto",
    "actual_video_sha256": "9277f8ec75881fa762109df1d219f0f3a9e25ef9ae9cab611a207b470a185ddd",
    "delivery_matches": true,
    "metrics_matches": true,
    "assessment_matches": true,
    "request_matches": true,
    "input_matches": true,
    "technical_approved": true,
    "draft": false,
    "audiovisual_approved": false,
    "raw_manifest_sha256": "62abd08f49e10f8ca21135292a4fd4581354ba3f2a486a630a2c9550c0ff6e8d",
    "semantic_manifest_sha256": "6e7003493c35ceba25c56e3fa51f6cc8549c50f8ea9bdfe69e8bb43ab686ed6a",
    "manifest_hash_contract": "_common.py110–113: sorted ensure_ascii=False JSON excluding review"
  },
  {
    "project": "cortes-de-video-longo/corte-selecionado",
    "actual_video_sha256": "c518fdf7e05be88c949ae9964bff0097ac95ed412e7c9d4faa90c7067dfd0b56",
    "delivery_matches": true,
    "metrics_matches": true,
    "assessment_matches": true,
    "request_matches": true,
    "input_matches": true,
    "technical_approved": true,
    "draft": false,
    "audiovisual_approved": false,
    "raw_manifest_sha256": "188b0fd01ddabd6b0b1e607aa9fe9f605f182d7f8b5d6dd1e5cb4a28b73c2ed6",
    "semantic_manifest_sha256": "7fff4635087be512b1bff6f1ee7000e6f872d1cc2cf975bf85d22942aee58ed0",
    "manifest_hash_contract": "_common.py110–113: sorted ensure_ascii=False JSON excluding review"
  }
]
```
Hashes SHA256 dos artefatos brutos estão no JSON. Baseline inicial preservada; hashes finais não são hashes retroativos da baseline. Nenhuma reprodução temporal/escuta foi alegada.

## Forward reassessment — nova execução

Agregado:31/33 pass (93,94%),2fail,0pending;12/13 casos pass. Somente os dois casos de edição usam forward-eval-r01 r02; os outros11 mantêm integralmente a reavaliação anterior29/33.

Teste isolado novo:9/9 graders e2/2 casos pass, sem aprovação audiovisual. Uma execução de um autor em dois fixtures relacionados não estima taxa geral de sucesso.

### editar-gravacao-propria — pass

- 01-recording-project: **pass** — Projeto real e importação pelo script da skill; edição do próprio input sintético foi expressamente autorizada, sem alegar filmagem real.
  Evidência: work/forward-eval-r01/pedido1/video.json:format gravacao,aspect9:16,source gravacao.mp4 SHA2e0e813...; commands.log footage.py import pedido1 fonte original EXIT0;47.3s1280x720

- 02-uses-srt: **pass** — SRT fornecido realmente importado e tempos remapeados após corte; não bloqueia por modelo ausente.
  Evidência: commands.log captions.py import --file gravacao.srt EXIT0;65palavras; pedido1/captions/source_words.json e words.json; palavra estimated=true informa interpolação do SRT, não ASR/alinhamento

- 03-retake-and-fillers: **pass** — Silêncios/vícios e retomada inicial removidos no EDL final, mantendo a tomada completa posterior. Verificação factual por tempos/texto, sem fingir escuta.
  Evidência: commands.log footage.py cut --fillers ahn,éé,hum EXIT0;3vícios removidos; pedido1/edit/edl.json c07keep=false21.002–22.37; c08/c09 mantêm repetição posterior23.896–26.929; intervalos dos vícios6.145–7.896,19.163–20.496,33.956–35.226 omitidos; pedido1/captions/words.json59de65palavras;14trechos finais

- 04-delivered-and-reviewed: **pass** — Entrega técnica vinculada por hashes ao pacote r02. Defeitos específicos da execução anterior foram corrigidos nesta nova execução: recorte varia, textos ficam na área segura, CTA não tem órfã. Rubrica permite bloqueio perceptual identificado sem chamar pronto; aplica-se essa cláusula, portanto não exijo verdict0 onde a resposta declara explicitamente revisão audiovisual pendente. Pass deste grader não é aprovação audiovisual; fonte efetiva não foi confirmada em painelGUI e sincronia/áudio ainda exigem revisão humana.
  Evidência: pedido1/out/pedido1.mp4;delivery.json approved=true,draft=false26.467s;commands.log deliver --video render/master.mp4 --no-captions EXIT0;review r02 e verdict EXIT2; pedido1/review/r02/grid.jpg observado: ator sintético original ocupa quadro; títulos por assunto e CTA de uma linha; legenda de duas linhas em área própria; acentos legíveis; sem rodapé inseguro; pedido1/edit/edl.json zoom1.00→1.06→1.00 em mudanças de assunto; x.645 preserva cabeça; composition/index.html data-has-audio=true,localInter54/52px,caption1280–1500,label275; commands.log HyperFrames audioCount1; captions já no HTML, deliver --no-captions; response-final.md explicita revisão independente pendente sem escuta/playback; ficha humana vazia; pedido1/research/seek-result.json2→0→2=0pixels diferentes;decoded-comparison.json compara snapshot1s com MP4 final sem alegar playback

- 05-autonomous-tools: **pass** — Usa ferramentas disponíveis e SRT autonomamente. Escopo autorizado para editar inputs sintéticos preservado; sem catálogo instalado ou serviço pago. No-install de outro caso não foi transplantado como bloqueio à CLI deste cenário.
  Evidência: commands.log import/SRT/cut/frames/render/captions/HyperFrames wrapper/deliver/review realmente executados; sem instalação/downloads; execute.py/compose.py selecionam ferramentas locais, Chrome existente e cache local; response-final.md relata sem instalação/publicação; segunda renderização altera títulos, visível no HTML e r02; não é repetição sem mudança

### cortes-de-video-longo — pass

- 01-long-project: **pass** — Projeto longo com fonte e SRT reais importados. Fonte sintética declarada e autorizada.
  Evidência: pedido2-longo/video.json formatgravacao16:9;source197.267s SHAe9c534aa...; commands.log footage.py import gravacao_longa.mp4 EXIT0 e captions.py import gravacao_longa.srt EXIT0;301palavras

- 02-suggests-clips: **pass** — Apresenta pelo menos três candidatos com intervalos e justificativa; decisão editorial lê conteúdo e supera rank1 dependente de contexto, sem converter nota heurística em audiência.
  Evidência: commands.log clips.py suggest --min20 --max45 --top5 EXIT0; três candidatos automáticos com tempos/razões; pedido2-longo/edit/selecao-editorial.md:00:00.500–00:46.515 lista completa/CTA;00:54.939–01:18.309 reserva/risco;01:29.234–01:55.152 constância; razões e limites factuais; pedido2-corte/out/resposta-final.md aponta arquivo editorial para usuário

- 03-makes-best-clip: **pass** — Corte coeso do próprio original, com fala única, variação de enquadramento e títulos por argumento. Proveniência/IA preservadas no projeto e resposta; fonte visual não foi substituída por placeholder. Acabamento estático observado corrige falhas anteriores. Não credita performance de avatar nem filmagem real; audio/movimento permanecem sem aprovação perceptual.
  Evidência: commands.log clips.py make --from0:00.5 --to0:46.515 --slug pedido2-corte EXIT0; formato corte9:16;cut/render/deliver reais; pedido2-corte/out/pedido2-corte.mp4:26.633333s1080x1920/30,H264/AAC;legenda integrada no HTML e export --no-captions; pedido2-corte/review/r02/grid.jpg observado: zoom1→1.06→1real; títulos argumentais1/2/3,headline e CTA seguros; legenda2linhas sem crédito sobreposto, acentos/numeral400 legíveis; pedido2-corte/video.json publish.ai_label=true;source original hash preservado;brief registra autoria declarada não prova terceiros;research/editorial.md e response-final identificam fonte sintética autorizada; r02 receipt/metrics/assessment/request/input têm hashes coerentes; verdict2 é explicitamente pendente sem alegar profissionalmente aprovado

- 04-chapters-and-publish: **pass** — Longo final adotado é o próprio MP4 original inalterado indicado pelo projeto, não o master do corte; não existe cópia nova em out e ela não é necessária para preservar o arquivo inteiro. Tempos conferem com duração/hash e SRT, sem escuta inventada. Não há composição longa ou rota narrada a exigir master intermediário separado.
  Evidência: pedido2-longo/out/youtube-publicacao.md e video.json: título,descrição e capítulos00:00/00:47/01:29/02:02/02:44; commands.log import relata MP4 original197.3s;source.sha256=e9c534aa... confirmado independentemente contra arquivo; notas declaram longo sem edição e preservado para subir inteiro; SRT do mesmo relógio:47.315investimento,89.234constância,122.283retomada,164.202constância; capítulos em ordem e intervalos47/42/33/42s

Restam falhas de composição-hyperframes01/02 da execução antiga. Nos dois novos filmes, permanecem limites de inspeção: nenhuma escuta/reprodução temporal, tempos por palavra interpolados e fonte efetiva não observada em painelGUI; isso impede declarar aprovação audiovisual. Hashes de receipt/manifesto semântico/metrics/assessment/request/input conferem nos r02.
