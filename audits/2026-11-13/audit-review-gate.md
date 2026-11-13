# Auditoria do portão de revisão

Escopo exclusivo de implementação: `video-viral/scripts/review.py`, `tests/test_review.py` e `tests/test_review_cli.py`. Leitura integral do SKILL.md, references/review.md e arquivos auditados. Contrato faixa 2: sem benchmark de qualidade, custo ou latência disponível; sem subdelegação. Não houve instalações, downloads, publicação ou commits; stack e Edge TTS preservados.

## scripts/review.py

Correções verificadas:

- Parser procurava qualquer número entre 1 e 5 nas colunas e aceitava sobrescrita por critério duplicado. Agora lê exclusivamente Nota na tabela gerada, exige evidência e rejeita duplicatas/estrutura malformada com código 2. Uma definição ou observação numérica não substitui nota ausente.
- Era possível remover um bloqueante somente de metrics.json e obter 0, embora o request.json já vinculado ao hash ainda registrasse a falha. Agora compara os bloqueantes do pacote e das métricas e valida lista de textos.
- Booleanos eram aceitos como segundos e schema 1. Agora valida tipos numéricos reais finitos nos intervalos e schema inteiro nos registros versionados.
- Um hard link em input/video.* podia passar; agora rejeita identidade de arquivo com a entrega original, preservando a exigência de cópia independente.
- report.md com UTF-8 inválido escapava do tratamento de erros; agora retorna revisão incompleta/código 2.
- Tempos de legendas infinitos, booleanos, negativos, invertidos ou sem texto podiam reduzir congelamento bloqueante a aviso de leitura. Agora devolve timing desconhecido, sem presumir legenda válida.
- --every zero, negativo ou não finito não era rejeitado corretamente. Agora falha por argumento inválido antes da análise; grades impossíveis são recusadas antes de criar uma rodada. O orçamento deriva do limite real JPEG de 65.500 px por dimensão, não de contagem arbitrária de tiles. Confirmado no FFmpeg instalado: uma imagem 65.502×2 falha com `JPEG does not support resolutions above 65500x65500`.
- next_round permitia r04 indefinidamente apesar de MAX_ROUNDS=3. Agora código 3 com orientação; rodadas, manifesto e evidências anteriores são preservados.

Verificações preservadas: correspondência hashes vídeo/manifesto/imagens/pacote/recibo; independência de IDs e não exposição às notas; união de intervalos sobrepostos; modalidades parciais/instrumentadas não aprovam; ausência real de áudio permite NA; ingestão humana reaproveita a rodada e mantém notas baixas/falha técnica; histórico review não altera hash criativo.

Limites: o código verifica consistência, não autentica identidades nem comprova reprodução/escuta. Não afirma capacidade perceptual. Mudança concreta ou nova evidência entre r01–r03 ainda depende do processo registrado: não se bloqueou simplesmente por hash idêntico, pois nova evidência legítima pode se referir ao mesmo vídeo. A geração bloqueia r04; não cria um novo mecanismo de autenticação do conteúdo dos registros.

## tests/test_review.py

Fixture de notas agora usa a tabela real de quatro colunas com evidência sintética explicitamente identificada. Regressões para coluna de nota/duplicatas/evidência, bool em intervalos/schema, bloqueantes removidos só das métricas, hard link, UTF-8 inválido, legendas malformadas e limite r04 com imutabilidade das três rodadas. Nenhuma fixture é apresentada como vídeo assistido.

## tests/test_review_cli.py

Regressões CLI para --every malformado antes de projeto/FFmpeg, grade acima do limite JPEG sem criar rodada e r04 com código 3 mantendo byte a byte manifesto e evidências. Mantidos testes reais FFmpeg de movimento localizado, legendas mudando, silêncio, cauda morta, banda uniforme e pulsos com LUFS normalizado.

## Execução

- Antes: 59 testes relevantes passaram. Novas regressões executadas contra o código original produziram sete falhas e um erro (incluindo três subcasos do parser), demonstrando bugs antes das correções.
- Depois: `python -m unittest discover -s tests -p 'test_review*.py'` → 71 testes passaram, incluindo FFmpeg/ffprobe reais; nenhuma marcação skip neste ambiente.
- `git diff --check -- scripts/review.py tests/test_review.py tests/test_review_cli.py` → sem erros.
- Nenhuma alegação de ganho >20%: não foi realizado benchmark comparativo de performance/qualidade. As guardas evitam trabalho inválido; não constituem evidência de aceleração geral.

Alterações de contrato comunicadas diretamente a `/root/instructions_evals` para alinhamento documental. Sem pendência bloqueante nos arquivos de escopo; limite processual de nova evidência explicitado acima.
