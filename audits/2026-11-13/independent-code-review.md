# Revisão independente do código — 2026-11-13

Escopo: diff do branch `codex/audit-video-viral` contra `52d567d`, scripts, assets de som, testes e CI. Repositório somente leitura; nenhuma instalação, pagamento, serviço externo, commit ou alteração de arquivo do projeto. Os testes usam diretórios temporários e Python sem bytecode. Relatórios e conclusões dos autores não foram consultados antes desta avaliação.

Identidade dos arquivos na conclusão desta revisão: `independent-reviewed-files.json`, com SHA256 do diff rastreado e dos arquivos de scripts/tests/.github (incluindo testes ainda não rastreados). Alterações posteriores exigem análise proporcional ao novo diff.

## Achado acionável

**P2 — a música termina quando acaba a faixa de áudio da gravação.** `scripts/deliver.py`, novo `audio_graph`, ramo que inclui `video_audio` no sidechain (linhas 85–90 na leitura inicial). `sidechaincompress` encerra a saída ao receber EOF da entrada de controle. O `apad` aplicado depois do `amix` substitui por silêncio a música restante. Um master com vídeo longo e faixa de áudio mais curta perde a cama musical depois da fala. Antes deste diff, a combinação `video_audio + music` preservava a música até o final dela; a falha equivalente com voz externa já existia.

Reprodução independente: `python -B ../work/independent-audio-eof-repro.py`. Com FFmpeg real, fala senoidal 440 Hz de 1 s, música senoidal 1000 Hz de 3 s e saída de 3 s, os dois pipelines entregam 144000 frames. Na base, RMS em janelas de 100 ms iniciadas em 1.5 e 2.5 s é `0.08836834525177342`; no código inicialmente revisado é `0.0` em ambas. A fala foi realmente encerrada, em vez de estendida com amostras silenciosas. O teste novo existente usa 2 s de áudio com segunda metade silenciosa, por isso não cobre EOF. Correção sugerida ao autor: preencher apenas a cópia de controle antes de `sidechaincompress`; conservar a duração original do foreground e testar música após EOF.

Estado: **resolvido e retestado independentemente**. O autor adicionou `apad` somente no ramo do detector. A mesma reprodução agora produz RMS `0.04428908376038349` em 1.5 e 2.5 s, coerente com a música atenuada em -6 dB; os 144000 frames foram preservados. O teste novo cobre EOF tanto de `video_audio` quanto de `voice`. Saída após correção: `independent-audio-eof-after.json`.

## Verificação independente

- Python: `PYTHONDONTWRITEBYTECODE=1 VIDEO_VIRAL_NO_INSTALL=1 python -B -m unittest discover -s tests -v`: **171 testes, todos passaram**, 15.240 s, Python 3.14 local. A suíte verde não detectou o achado acima.
- Node: `VIDEO_VIRAL_NO_INSTALL=1 VIDEO_VIRAL_NODE_ROOT=<runtime-root>\node-v2 node --test tests/node/*.test.mjs`: **14 testes, todos passaram**, 6.908 s, Node v26.12.0, Chrome/157.0.8103.51. Inclui GLB real, Tone real e renderizações visuais locais.
- Benchmark: `node tests/node/transport.bench.mjs`: mediana **662.291 ms → 208.3399 ms**, redução de 68.5425%, cinco pares alternados. O benchmark usa a mesma Float32Array de 30 s mono a 44100 Hz, compara os bytes exatos após cada par e inclui a conversão do retorno legado. A comparação é adequada para a etapa de transporte browser→Node. Não mede renderização Tone, pipeline completo, custo de modelo, latência de serviços, nem qualidade perceptual. O teste Tone real de 1.2345 s verifica PCM equivalente em duas renderizações determinísticas, complementando o benchmark sintético.
- Depois das correções: **9 testes delivery** e **12 testes footage** passaram. Além da reprodução independente de EOF, foi gerado MP4 real 64x64/10 fps/2 s com vídeo vermelho e seno 440 Hz; a reimportação de conteúdo idêntico com derivados foi permitida. Substituído no mesmo caminho por vídeo azul/seno 880 Hz com mesmos metadados, a reimportação foi bloqueada; todos os hashes dos arquivos e o objeto do manifesto permaneceram idênticos ao estado imediatamente anterior à tentativa.

## Limites de garantia e cobertura

- A limitação inicialmente apontada da guarda de reimportação foi resolvida pelo armazenamento/comparação de SHA256 do conteúdo. Projetos legados com derivados e sem hash são bloqueados de forma conservadora; sem derivados, o hash é migrado na próxima importação. A verificação se aplica à operação de reimportação. Mutação externa da mídia durante ou depois de uma operação não é impedida pelo script.
- Publicação GLB agora requer hard links no filesystem do destino. A suíte local cobre NTFS; FAT/exFAT, shares ou filesystems sem hard links não foram testados. O comportamento falha de forma explícita, mas restringe destinos antes aceitos pelo rename.
- O CI novo foi lido; não foi executado no runner Ubuntu nesta revisão. Sucesso local Windows não é evidência de execução do workflow no GitHub.
- Não houve mídia externa, TTS online, modelo real ACE-Step/ComfyUI, licença comercial, publicação ou aprovação audiovisual perceptual nesta revisão. Testes simulados de API verificam protocolo/preservação de arquivo, sem validar gerações reais.

O P2 novo reproduzido no pipeline core foi corrigido. Nenhuma aprovação audiovisual ou afirmação irrestrita de ausência de regressões é emitida; as evidências cobrem os caminhos locais descritos.

## Revisão adicional delimitada do harness de produções

Leitura de `tests/validation_productions.py` ampliado para revisões r02/r03, sem repetir a suíte verde ou automação de render. O teste é demonstrativo e não um helper de produção. Nenhuma nota, assessment ou relatório de scores do autor foi consultado.

**P2 — retomada de falha não idempotente**, comunicado ao coordenador e ao autor; **resolvido, com correções de código verificadas por execução independente delimitada e reprise real final conferida**:

1. O ramo r02 só ignorava `revision == 2`; na retomada do mesmo comando com `--revision2 --revision3`, casos já concluídos em r03 eram rebaixados para r02 e podiam tentar criar r04.
2. `run()` retorna stdout/stderr concatenados no stdout ao reutilizar comando do cache; a primeira leitura loudness usava exclusivamente stderr, produzindo `blocks=[]` numa retomada legítima depois da medição baseline concluída.
3. O ramo recording r03 sempre movia `master.mp4` para `aroll-r03.mp4`, mesmo quando o comando de base já concluído vinha do cache. Depois da restauração de master r01 na primeira tentativa, uma retomada movia esse master restaurado sobre a base A-roll r03 correta.
4. R03 transformava o HTML já modificado depois de falha antes do checkpoint `case.revision=3`. No product, isso reinjetava uma segunda declaração `const timer`, quebrando o JavaScript; backups r02 também eram sobrescritos. Solução sugerida: backup único de r02 e transformação sempre a partir dele, com base A-roll em destino estável.

Reprodução delimitada das operações de cache/movimento/substituição, sem renderizar nem alterar artefatos legítimos: `independent-harness-resume-repro.json`. Os casos são retomadas do mesmo comando após falha, sem alteração arbitrária de inputs.

Verificação da correção: `python -B ../work/independent-harness-resume-check.py` executa os próprios blocos AST de r02/r03 do harness sobre fixtures em diretório temporário, substituindo apenas comandos de render por stubs e induzindo uma falha depois da preparação. Em segunda tentativa, HTML product permanece byte-idêntico, contém uma só declaração timer e preserva backup r02; recording mantém base r03 correta e master r01 original, executa a geração de base uma única vez e preserva o backup; bloco r02 não executa comandos nem rebaixa casos r03. A atribuição real que extrai loudness também processa corretamente stdout do cache. Todos passaram; saída em `independent-harness-resume-check.json`. Não se trata de teste de regex do formato do código nem de nova execução dos renders.

Verificação técnica do material já gerado: os **10 pacotes input de r01/r02** dos cinco casos ainda correspondem aos hashes de request, vídeo e quadros registrados nas métricas. Evidência: `independent-round-input-integrity.json`. Isso verifica integridade interna atual; não substitui comparação com snapshot externo anterior. O harness não grava nesses input nas revisões, e a política de `review.py` usa cópias independentes.

Os casos recording e long selecionam `--voice` da A-roll com áudio, sobre masters HyperFrames sem fluxo de áudio, evitando soma duplicada do áudio de gravação. FFprobe independente confirmou recording master 27.733333 s sem áudio, A-roll com áudio 27.626333 s e final AAC stereo 27.733 s; long r02 master 183.6 s sem áudio, A-roll/final com áudio de 183.6 s. Evidência: `independent-production-audio-paths.json`. A correção EOF de ducking foi confirmada antes com áudio real FFmpeg; isso não é aprovação de mixagem perceptual.

`results.json` declara `perceptual_approval: false`, casos `independent_review: pending`, e os comandos de entrega passam `--draft`; não foi encontrado caminho que invente aprovação perceptual. Os scripts de revisão mantêm a aprovação dependente de evidência externa.

Limitação explícita do cache: a reutilização confia no nome, comando e exit code, sem hash dos inputs/outputs ou identidade da versão do script; ela serve para continuar falhas com os mesmos inputs. Não é evidência de reprodutibilidade após mudança arbitrária de arquivos. O relatório do harness deve manter essa distinção.

Leitura adicional final de `review.py`: descrições de RUBRIC/RECORDED_RUBRIC passaram a exigir ritmo/pausas/motion/som/fechamento por função, eliminando quotas universais de efeitos, zoom obrigatório, seis palavras para todos os textos e loop obrigatório. IDs dos critérios, lógica de seleção `rubric_for`, limites instrumentais, parsing de notas, validações de hash e limite de rodadas não foram afrouxados por essa edição. É alinhamento descritivo; pacotes input antigos mantêm os critérios originalmente enviados e não foram reescritos para produzir aprovação.

## Fechamento da revisão focal

O executor repetiu o comando real `--resume --revision2 --revision3 --long-r03` após concluir long r03: exit 0 em 0.6204559 s. Li o script de captura antes/depois e a prova completa; recalculei independentemente os hashes dos arquivos atuais e conferi **61/61 iguais aos mapas before/after**, **19 → 19 comandos de render**, **14 → 14 rodadas**, nenhuma r04. Não repeti o render nem a automação já concluída. Evidências do executor: `video-viral-validation-run2/resume-proof.json`; conferência independente: `independent-final-resume-integrity.json`.

Os cinco recibos finais continuam `draft: true`, `approved: false`, vinculados ao SHA256 do vídeo atual. `results.json` mantém `perceptual_approval: false` e todos os casos com revisão independente pending. Isso confirma que o harness não transformou reuso de cache ou êxito técnico em aprovação perceptual.

Nenhum P1/P2 novo permanece aberto no escopo revisto. Limites continuam explícitos: cache não invalida mudanças arbitrárias de inputs; CI Ubuntu/serviços/modelos reais não executados nesta revisão; nenhuma aprovação audiovisual é emitida.

Snapshot final regenerado após o core ser declarado congelado e o harness concluído: `independent-reviewed-files.json`, preservando snapshot anterior em `independent-reviewed-files-before-final.json`. SHA256 do diff rastreado de scripts/tests/.github/renderer: `b0b431f94f277821280d6e5701b1dd28d096f494429cdf2703625d8cedf6dbc0`; harness final: `edb8da2ef3f7cfbd5f7801a5fa317d716ea7176be6df1a9b512f08afe204f884`. `git diff --check` sem erros.
