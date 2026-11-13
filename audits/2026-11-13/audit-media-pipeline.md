# Auditoria do pipeline de mídia — 2026-11-13

Escopo exclusivo: `video-viral/scripts/{_common,captions,clips,footage,voice,music,comfy,images,trends}.py` e testes correspondentes. Leitura integral do `SKILL.md` do repositório e de todos esses scripts; revisão dos testes correspondentes. Alterações Edge TTS existentes foram preservadas. Sem instalação, acesso a contas, síntese remota, modelos, publicação ou commit. Servidores HTTP dos testes são somente fixtures locais em 127.0.0.1.

## Achados corrigidos e evidência

| Severidade | Arquivo | Defeito reproduzível / efeito anterior | Correção e regressão |
|---|---|---|---|
| Alta | footage.py | Fonte sem áudio com `audio/source.wav` residual era cortada pelos silêncios da fonte anterior. | Respeita `source.audio` vazio. `test_cut_silent_source_ignores_old_extracted_audio` comprova que silencedetect não é chamado. |
| Alta | footage.py | WAV extraído removido fazia renderizar a gravação com silêncio sem avisar; cut também continuava silenciosamente. | Falha explícita antes de render/cut. `test_missing_extracted_audio_fails_before_silent_render_or_cut`. |
| Média | footage.py | `--to 0` era convertido por `or dur` para vídeo inteiro; tempos negativos/NaN/inf e relógios inválidos passavam. | Parser compartilhado finito/não negativo e distinção entre zero/None. Testes `test_zero_end_is_not_interpreted_as_full_video`, `test_time_parser_rejects_nonfinite_negative_and_invalid_clock`. |
| Média | footage.py | Fonte relativa resolvida no cwd do script, embora demais assets usem o projeto. | `source_of` resolve relativo ao projeto; exercitado pelos testes de cut/render com cwd diferente. |
| Média | footage.py | EDL com out <= in chegava ao FFmpeg; frames vazio montava tile com zero linhas. Entradas de corte NaN/negativas e alvo minúsculo podiam falhar ou gerar trabalho excessivo. | Validação de EDL/argumentos e falha explícita para frames vazio; rejeição explícita de alvo positivo abaixo do mínimo útil de 1,2 s, sem clamp silencioso. Teste `test_invalid_edl_and_empty_frames_fail_before_ffmpeg`. |
| Média | clips.py | Range invertido podia virar válido pela folga de -0,15/+0,25; folga podia sair do trecho autorizado/importado. Limites inválidos e top=0 produziam resultados incoerentes. | Valida antes de criar projeto e limita folga à duração importada. Testes `test_invalid_ranges_do_not_create_child_projects` e `test_invalid_suggestion_limits_fail_before_reading_transcript`. |
| Média | voice.py | IDs com `../` escapavam da pasta de cenas; IDs duplicados sobrescreviam WAVs; gap negativo/NaN e cenas silenciosas não finitas geravam montagem inválida. | Validação antes da síntese e antes do FFmpeg. `test_invalid_scene_paths_gap_and_durations_fail_before_ffmpeg`. Defaults pt/en, +20%, migração Kokoro, licenças e staging da síntese continuam nos testes existentes. |
| Média | captions.py | `import --final` ajustava palavras da montagem usando silêncios do áudio fonte, em outra linha do tempo. | Análise dos silêncios só na linha de tempo fonte. `test_final_subtitle_import_does_not_use_source_silence`. |
| Média | music.py | Só o magic header RIFF/WAVE (12 bytes) bastava para sobrescrever áudio anterior e registrar geração concluída; fixture de sucesso existente tinha exatamente esse formato inválido. | Verifica tamanho RIFF, limites dos chunks, formato e dados de amostras antes de publicar. Fixture agora é WAV PCM real; testes de header-only e WAV truncado preservam saída/manifesto. |
| Média | comfy.py | Workflow terminado sem imagem esperava até timeout; histórico malformado podia produzir AttributeError não tratado. | Falha imediatamente em sucesso sem imagem e valida tipos de histórico/saída. Fixtures adicionais no teste de contrato preservam arquivos anteriores. |
| Baixa | trends.py | Parser verificava somente os primeiros 10 caracteres: `2026-11-01garbage` e hora 25 eram aceitos como evidência. | Valida período integral mensal, diário ou horário ISO e hora real. `test_full_hourly_period_validation`. |

## Cobertura arquivo por arquivo

- `_common.py`: leitura de configuração/venvs, resolução de projeto, gravação temporária de manifesto, hashes, registro de assets, execução de subprocessos e ffprobe. Nenhuma alteração necessária nesta faixa. Funções de manifesto/ffprobe/asset foram exercitadas pelas suítes.
- `captions.py`: leitura integral de transcrição, interpolation, SRT/VTT, fonte/final, estimativa, grafia, grupos e ASS. 13 testes aprovados. Transcrição Whisper/GPU não foi executada nem modelo baixado.
- `clips.py`: leitura de score, seleção de candidatos, deduplicação, offsets e criação de corte/proveniência. 4 testes aprovados; preservação de licença/proveniência/ai_label mantida.
- `footage.py`: leitura de importação/rotação/range/áudio, silêncios/fillers/subtração, continuidade e EDL, crop/frames, concatenação/overlays/remapeamento. 7 testes aprovados, incluindo FFmpeg real import→cut→render de MP4 sintético: origem 3 s, trecho 1–2 s, WAV e master medidos em 1 s, faixa de áudio presente.
- `voice.py`: leitura integral e preservação da migração Edge TTS previamente existente. 11 testes aprovados, incluindo WAV offline real de 1 s + pausa 0,25 s + cena silenciosa 0,5 s = voice.wav medido em 1,75 s. Chamadas Microsoft em produção não exercitadas; cliente é fixture nos testes de síntese.
- `music.py`: leitura das validações de endpoint/origem/redirect/auth/deadline/tamanho, task/status, download e rollback, síntese procedural. 6 testes aprovados; várias condições por teste. API é fixture HTTP local; procedural foi executado de verdade e determinismo/amostras audíveis verificados.
- `comfy.py`: leitura completa, workflow/API, histórico, imagem, rollback e recibo. 2 testes aprovados com múltiplos modos HTTP locais; nenhum servidor ComfyUI real ou modelo iniciado.
- `images.py`: leitura integral (alias de main do comfy). Fluxo subjacente coberto por testes comfy; nenhuma lógica própria adicional.
- `trends.py`: leitura completa de URL, CSV, índices censurados, importação/arquivos de evidência e manifestação de filtros. 10 testes aprovados. Não houve consulta Google.

## Comandos e resultados finais

Workdir: `<repo>`.

```
python -m unittest discover -s tests -p test_captions.py  # 13 OK, 0.096 s
python -m unittest discover -s tests -p test_clips.py     # 4 OK, 0.007 s
python -m unittest discover -s tests -p test_comfy.py     # 2 OK, 0.564 s
python -m unittest discover -s tests -p test_footage.py   # 7 OK, 0.448 s (reexecução após ajuste max-shot)
python -m unittest discover -s tests -p test_music.py     # 6 OK, 4.706 s
python -m unittest discover -s tests -p test_trends.py    # 10 OK, 0.015 s
python -m unittest discover -s tests -p test_voice.py     # 11 OK, 0.139 s
git diff --check                                       # exit 0, sem saída
```

Total: **53 testes aprovados, zero skips, zero falhas** nesta execução. Tempo de testes reportado pelo unittest: aproximadamente 5,98 s somando últimas execuções por arquivo; comando agrupado anterior: 7,01 s (52 testes antes de adicionar a regressão max-shot). Não houve benchmark do desempenho anterior: esses tempos são observação desta máquina, não prova de ganho de performance. Nenhum achado crítico confirmado neste escopo; não é prova de inexistência de bugs.

## Limites e observações

- Não foi feita escuta/revisão estética, validação de licenças de terceiros, teste de serviço Edge/ACE-Step/ComfyUI real, GPU ou download de modelos. Limites explícitos evitam alegação de produção aprovada.
- Pendência de reimportação resolvida: mudança de caminho resolvido, range ou limpeza é recusada antes de modificar áudio/manifesto quando há derivados em captions/edit/render/out/review. A orientação é criar novo projeto, preservando o atual. Reimportação idêntica continua possível e fonte nova sem derivados também; nenhum arquivo é apagado ou movido.
- Validação WAV confere estrutura e amostras não vazias, não qualidade musical/perceptual nem duração de direção criativa. Imagens ComfyUI mantêm verificação de assinatura/formato existente, sem avaliação estética.
- Escrita restrita aos arquivos autorizados e a este relatório; diff global também contém alterações de outros executores e não foi revertido.

## Complemento — fonte e derivados resolvidos

- **Alta: troca de fonte/range/limpeza com derivados antigos.** `footage.cmd_import` agora compara caminho absoluto resolvido (inclusive origem relativa ao projeto), range efetivo arredondado conforme o manifesto e limpeza efetivamente aplicada. Se houver diferença e arquivos em captions/edit/render/out/review, falha com orientação para criar novo projeto antes de criar pastas, extrair WAV ou atualizar manifesto. Não existem flags novas, deleção, movimentação ou invalidação destrutiva.
- `test_changed_import_with_derivatives_preserves_every_file_and_manifest`: 15 combinações (3 mudanças × 5 pastas), preservação byte-a-byte de todos os arquivos, incluindo WAV/manifesto/EDL, e igualdade do manifesto em memória. FFmpeg não é chamado nas rejeições.
- `test_identical_resolved_import_allowed_with_derivatives`: origem relativa e absoluta equivalentes, range/limpeza iguais, reimportação permitida e EDL preservada.
- `test_different_source_allowed_without_derivatives`: outra fonte é aceita quando apenas o áudio extraído da importação anterior existe.
- **Média: captions import em fonte sem áudio usava WAV antigo.** Reproduzido com source.audio vazio e audio/source.wav residual. Removido fallback implícito; silêncio só é analisado para o caminho explicitamente manifestado. `test_silent_source_import_ignores_stale_source_wav` exige zero chamadas FFmpeg e preserva tempos 0–1 s.
- Reexecução: `python -m unittest discover -s tests -p test_footage.py`: **10 OK, 0.536 s**; `python -m unittest discover -s tests -p test_captions.py`: **14 OK, 0.122 s**; `git diff --check`: exit 0. As outras 5 suítes permanecem aprovadas na execução anterior, pois não houve mudanças nelas após a rodada anterior. Total delimitado atualizado: **57 testes**, sem skips ou falhas nas últimas execuções de cada arquivo.
- Criticidade consolidada atualizada: **3 altas, 9 médias, 1 baixa; nenhuma crítica confirmada**. Grupos distintos de defeitos, sem contabilizar subcasos como novos achados.

## Complemento — identidade por conteúdo da fonte

A revisão independente identificou uma lacuna na guarda da mesma falha alta de fonte/derivados: substituir bytes do vídeo no mesmo caminho mantinha path/range/cleaned iguais. A importação agora calcula `file_sha256` uma única vez por invocação válida e persiste `source.sha256`. A guarda também compara esse hash, antes de extrair WAV, modificar manifesto ou qualquer derivado. Testes contam a chamada de hashing para evitar dupla leitura do arquivo pesado.

`test_in_place_replacement_and_legacy_hash_missing_preserve_derivatives` cobre substituição in-place e manifesto legado sem hash: ambos recusam a reimportação quando há derivados, preservando byte-a-byte arquivos e manifesto em memória. A comparação por hash já exige igualdade nas 15 combinações anteriores, isolando corretamente diferenças de path/range/cleaning. `test_identical_resolved_import_allowed_with_derivatives` continua passando com sha256 presente e caminho relativo/absoluto equivalente. `test_legacy_source_without_derivatives_migrates_hash` comprova que projeto antigo sem derivados pode ser reimportado e recebe o campo, com uma única medição do hash.

Limite legado explícito: não há prova retrospectiva dos bytes usados para gerar derivados em manifestos sem `source.sha256`; por isso esses projetos continuam utilizáveis para suas outras operações, mas a reimportação com derivados é recusada com orientação para criar novo projeto. Não se inventa hash histórico, não se apagam arquivos e não se força migração destrutiva. Alteração concorrente do arquivo entre hash/probe/extrator não é mecanismo de sincronização de filesystem; preserve o original estável durante importação.

Última execução: `python -m unittest discover -s tests -p test_footage.py`: **12 OK, 0.515 s**; clips reexecutado após adição do hash: **4 OK, 0.006 s**; `git diff --check`: exit 0. Total delimitado atualizado: **59 testes**, zero skips/falhas nas últimas execuções por arquivo. Esta correção fecha a falha alta de identidade da fonte já contabilizada; não acrescenta novo grupo à contagem consolidada.
