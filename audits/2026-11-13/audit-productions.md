# Cinco produções técnicas representativas

Demos técnicas reproduzíveis, não peças acabadas. Sem aprovação audiovisual independente.
Ambiente herdado: VIDEO_VIRAL_NO_INSTALL=None
Resolução reduzida e 15 fps explícitos; fontes/Chrome/GSAP locais; nenhuma instalação solicitada.
Fixtures do repositório têm termos comerciais não verificados; entregas em rascunho. Música procedural é reserva, não ACE-Step.

| Caso | Duração | Tamanho | LUFS baseline → entrega | Distância de -14 LUFS |
|---|---:|---|---|---|
| narrated | 14.000s | [360, 640] | -23.67 → -14.24 | 9.67 → 0.24 LU |
| product | 12.000s | [360, 640] | -25.33 → -14.04 | 11.33 → 0.04 LU |
| recording | 27.671s | [360, 640] | -21.13 → -14.03 | 7.13 → 0.03 LU |
| story | 12.000s | [360, 640] | -25.33 → -14.04 | 11.33 → 0.04 LU |
| long | 183.600s | [640, 360] | -23.83 → -14.07 | 9.83 → 0.07 LU |

Baseline: cama procedural original ou mix normal voz+cama a -16 dB, sem degradar o sinal. A comparação mede normalização, não qualidade perceptual nem eficiência.
Comandos exatos, códigos de saída, tempos e logs: `video-viral-validation-run2/results.json`.
Pendências: reprodução/escuta integral e avaliação independente, licenças comerciais e qualidade criativa. Nenhuma publicação realizada.

| Caso | Master atual | Entrega revisável | Rodada | Render atual | Deliver | Seek RGBA |
|---|---|---|---|---:|---:|---|
| narrated | `<workspace>\work\video-viral-validation-run2\narrated\render\master-r03.mp4` | `<workspace>\work\video-viral-validation-run2\narrated\out\narrated_rascunho.mp4` | r03 | 15.657 s | 0 | 0 pixels diferentes |
| product | `<workspace>\work\video-viral-validation-run2\product\render\master-r03.mp4` | `<workspace>\work\video-viral-validation-run2\product\out\product_rascunho.mp4` | r03 | 15.359 s | 0 | 0 pixels diferentes |
| recording | `<workspace>\work\video-viral-validation-run2\recording\render\master-r03.mp4` | `<workspace>\work\video-viral-validation-run2\recording\out\recording_rascunho.mp4` | r03 | 33.529 s | 0 | 0 pixels diferentes |
| story | `<workspace>\work\video-viral-validation-run2\story\render\master-r02.mp4` | `<workspace>\work\video-viral-validation-run2\story\out\story_rascunho.mp4` | r02 | 14.654 s | 0 | 0 pixels diferentes |
| long | `<workspace>\work\video-viral-validation-run2\long\render\master-r03.mp4` | `<workspace>\work\video-viral-validation-run2\long\out\long_rascunho.mp4` | r03 | 191.327 s | 0 | 0 pixels diferentes |

Reprodução completa em pasta nova:
`<home>\AppData\Local\Programs\Python\Python314\python.exe tests/validation_productions.py --output <pasta-nova> --node-root "<runtime-root>\node-v2" --revision2 --revision3`
Longo: acrescente uma execução `--resume --long-style-only`, inspecione os quatro PNGs de research/style-r03 e só então execute `--resume --revision3 --long-r03`; este harness não transforma a existência dos PNGs em aprovação visual automática.

Correções reais: títulos desde quadro 0 e transições; narrativa com diagramas próprios de assinatura/extrato/embalagem; temporizador fictício reconhecível; fonte da gravação integral no foreground; legenda por sentido em duas linhas para os curtos corrigidos; longo encerra frase do SRT em 183.517 s, com margem de 0.083 s e zonas separadas.
Gravação: 47 s → 27.671 s por EDL; 15 trechos, 3 vícios isolados removidos. O crop inicial mostrava 404/1280 px da largura da fonte (31.56%); a rota fit:blur mantém 100% da fonte no primeiro plano. Isso mede enquadramento, não preservação semântica ou qualidade estética.
Falhas preservadas: captura padrão drawElementImage → fallback oficial screenshot; import de SRT no timeline longo explicitado; backup HTML fora da raiz para evitar múltiplas composições. Inputs de rodadas anteriores permanecem imutáveis. Seek pós-render é regressão técnica. O longo r03 teve também snapshots 0/90/150/183.533 e inspeção estática do autor antes de renderizar; não comprova reprodução/escuta.
Vereditos atuais: 2 (evidência independente audiovisual pendente); nenhum canal perceptual foi inventado. Os exemplos usam fixtures geométricas e áudio/SRT de teste, não material realista nem peça publicitária acabada.

Retomada real repetindo --resume --revision2 --revision3 --long-r03: exit 0, 0.677 s; 61 hashes de finais/inputs iguais; renders 19 → 19; rodadas 14 → 14. Evidência: `video-viral-validation-run2/resume-proof.json`. Mede reuso de resultados existentes, não aceleração de produção nova.