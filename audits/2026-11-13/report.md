# Auditoria Video Viral — 13/11/2026

Código e instruções corrigidos na branch `codex/audit-video-viral`, preservando o Edge TTS 2.4.0 da base `52d567d`. Esse é o estado ao encerramento dos testes; a publicação e instalação posteriores são rastreadas pelos PRs e pelo histórico Git.

| Meta | Evidência e resultado |
|---|---|
| Auditar 100% | 158/158 arquivos da base e 162 arquivos de execução no total; responsáveis, método e hashes em [coverage.csv](coverage.csv). Leitura/parse integral e testes locais pertinentes; serviços externos não executados. |
| Corrigir críticos | Nenhum crítico confirmado permaneceu aberto; defeitos altos/médios e regressões reproduzidas foram corrigidos. A revisão independente não encontrou P1/P2 aberto no código final que revisou. Isso não prova inexistência de bugs desconhecidos. |
| Aprovação ≥90% | 31/33 rubricas (93.9%); 12/13 casos completos (92.3%). Julgamento independente de artefatos/trace: 11 cenários manuais e 2 reexecutados em contexto separado, após correções. Não é estimativa estatística de agentes novos nem aprovação audiovisual. As notas anteriores permanecem no relatório independente. |
| Testes automatizados 100% | 174/174 Python + 14/14 Node, sem skips/falhas; smoke FFmpeg/Tone e validação estrutural da skill também passaram. |
| Validar pelo menos 5 produções | 5 demos técnicas reais HyperFrames+GSAP, curtas e longa. Mais dois cenários reais de edição em 1080×1920. Não representam cinco peças profissionais aprovadas. |
| Melhorar audiovisual | Comparação independente r01→r02/r03 confirma títulos no quadro zero, diagramas de gastos, temporizador reconhecível, enquadramento da fonte e correções de colisões. Medições de áudio e limites constam dos relatórios. Escuta/movimento integral e avaliação criativa final continuam pendentes. |
| Reduzir tempo/custo ≥20% | Transporte browser→Node: mediana 662.70→199.90 ms, redução 69.84% em cinco pares, amostras idênticas. Revisor independente mediu 68,54%. Não mede tempo/custo total do vídeo. |
| Sem regressões críticas + revisão independente | Suítes locais completas e revisão independente de código; revisão visual independente amostrada. Revisão audiovisual perceptual integral permanece pendente. CI remoto e modelos/serviços reais não foram validados. |

## Correções principais

Foram corrigidos áudio residual/perdido, troca de fonte com derivados antigos (com SHA256), intervalos/EDLs inválidos, legendas da linha do tempo errada, WAVs truncados, estados ComfyUI malformados, instalações que contornavam NO_INSTALL, sobrescrita de recibo glTF, diagnósticos falsos, aprovação de revisão por campos/colunas inválidos, mistura da fala gravada e preservação da música após EOF. `--draft` sempre gera rascunho sem aprovação para publicação.

As instruções passaram a respeitar pedidos apenas de plano, licenças reais, segmentação de legendas por sentido, áreas seguras consistentes, disponibilidade efetiva de avatar e critérios de avaliação pertinentes ao formato. `plan.py` continua validando estrutura; criatividade e adequação exigem julgamento.

## Pacote público e evidências locais

Esta pasta é uma exportação pública dos resultados. Prefixos pessoais foram substituídos por `<repo>`, `<workspace>`, `<runtime-root>` e `<home>`; vídeos, caches e pacotes humanos de revisão não são distribuídos. Seus hashes e resultados permanecem nos registros. Os registros brutos locais foram preservados antes da exportação. Essa normalização de caminhos não altera as amostras do benchmark nem os hashes dos vídeos. `coverage.csv` identifica os arquivos empacotados na publicação; os snapshots independentes históricos identificam a revisão anterior.

## Produções e comparação

Os arquivos abaixo são demos/fixtures em resolução reduzida a 15 fps. Música procedural é reserva identificada. Direitos comerciais das fixtures/fontes permanecem não confirmados; entregas são rascunhos. Hashes, comandos, falhas preservadas, durações, parâmetros e seeks estão em [production-results.json](production-results.json).

| Produção | Duração | Resolução | Revisão | Vídeo local |
|---|---:|---|---|---|
| Narrado/tutorial | 14.000 s | 360×640 | r03 | MP4 (artefato local não incluído) |
| Produto: temporizador conceitual | 12.000 s | 360×640 | r03 | MP4 (artefato local não incluído) |
| Gravação editada | 27.671 s | 360×640 | r03 | MP4 (artefato local não incluído) |
| Storytelling/animatic | 12.000 s | 360×640 | r02 | MP4 (artefato local não incluído) |
| Vídeo longo 16:9 | 183.600 s | 640×360 | r03 | MP4 (artefato local não incluído) |

A normalização comparada usa a mesma cama/voz sem normalização como baseline, sem degradação artificial. Não é prova de qualidade perceptual nem de ganho sobre uma versão antiga da skill, pois normalizar já fazia parte do fluxo. As melhorias de conteúdo/layout vêm da comparação visual independente; o transporte otimizado tem equivalência binária.

## Teste isolado de edição

Os dois pedidos de edição foram reexecutados em pastas novas por agente com contexto separado, sem acesso a notas/graders/produções anteriores. Recebeu somente skill, pedidos e fontes. Após identificar a fonte como sintética, recebeu esclarecimento para editar o próprio input, preservando o estilo e sem alegar filmagem real. Esse esclarecimento também corrigiu a instrução de fidelidade. As tentativas antigas e suas reprovações foram preservadas; não foram rodadas r04 nelas.

- Gravação atual (artefato local não incluído): [resposta e limites](forward-recording-response.md).
- Corte atual (artefato local não incluído): [resposta e limites](forward-clip-response.md); [dados do YouTube](forward-youtube-publication.md).
- [Trace do teste isolado](forward-commands.log) e [registro do executor](forward-run-notes.md). Receipts técnicos e fichas humanas ficam nos projetos locais; a classificação depende da revisão independente, não da autoavaliação do autor.

## Evidências e reprodução

- [Revisão independente do código](independent-code-review.md), [revisão visual](independent-visual-review.md) e [avaliação independente dos cenários](independent-eval-results.md).
- [Auditoria de mídia](audit-media-pipeline.md), [Node/setup](audit-node-setup.md), [portão de revisão](audit-review-gate.md), [instruções/evals](audit-instructions-evals.md) e [entrega/planejamento](root-review.md).
- [Cinco produções](audit-productions.md), [dois cenários de edição](audit-eval-renders.md), [benchmark bruto](benchmark-node-transport.json), [Python](final-python.log), [Node](final-node.log) e [smoke](integration-results.json).

Comandos no repositório (runtimes já instalados):

```powershell
python -m unittest discover -s tests -v
$env:VIDEO_VIRAL_NODE_ROOT="$HOME/.video-viral/node-v2"
node --test tests/node/*.test.mjs
node tests/node/transport.bench.mjs
python tests/integration_pipeline.py --output <pasta-nova> --node-root <runtime>
python tests/validation_productions.py --output <pasta-nova> --node-root <runtime> --revision2 --revision3
```

## Pendências para aprovação profissional

É necessária reprodução e escuta integrais por pessoa independente, com ficha em branco de cada última rodada e os pacotes `input/` correspondentes. Nesta sessão, imagens e métricas não foram convertidas em alegações de escuta ou observação temporal. Não há vídeo autorizado como pronto para publicar por essa revisão parcial.

O caso específico de composição de 12 s não obteve voz autorizada/render no ambiente NO_INSTALL do ensaio. Demos de outros conteúdos não foram usadas para fingir cumprimento desse prompt. Roteiro cinematográfico/avatares e modelos externos continuam limitados às evidências descritas.

A publicação desta atualização executa a CI no GitHub antes do merge. O estado remoto fica nos checks do PR; as medições e observações acima continuam sendo os resultados locais da auditoria.
