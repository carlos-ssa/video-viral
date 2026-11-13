# Auditoria de entrega, projeto e integração

Base: 52d567d, branch codex/audit-video-viral. A atualização Edge TTS 2.4.0 foi preservada.

## Escopo integral

- `scripts/deliver.py`, `scripts/new_project.py`, `scripts/plan.py`: leitura integral e revisão dos contratos. `plan.py` permanece estrutural: não comprova mérito editorial, criatividade, originalidade nem qualidade dos cinco candidatos; exemplos reais com plano válido e falha editorial estão preservados no ensaio de avaliação.
- `tests/test_delivery.py`, `tests/test_project.py`, `tests/test_plan.py`, `tests/integration_pipeline.py`: leitura e execução. O smoke usa FFmpeg, Tone e fixtures, sem se apresentar como produção principal HyperFrames. As cinco produções adicionais usam o compositor real.
- `assets/video.template.json`, `assets/reviewer.example.json`, `agents/openai.yaml`, `LICENSE`, `.gitignore` e workflow de CI: contratos, consentimento/licenças, frontmatter, roteamento, defaults e escopo inspecionados. Pins/lock/catalogue e demais assets têm relatório específico.

## Correções e demonstração

| Defeito | Efeito e correção | Evidência |
|---|---|---|
| `--draft` ignorado em projeto não monetizado ou sem bloqueio | Agora rascunho sempre tem nome próprio, `draft:true`, `approved:false` | MP4 real em `test_explicit_draft_never_receives_publishable_receipt` |
| Ganho de música ignorado sem WAV de voz externa | O ganho declarado atua também em música isolada e na gravação | Teste FFmpeg PCM demonstra ganho -20 dB como RMS multiplicado por 0,1 |
| Música não abaixava sob fala embutida | Detector considera áudio da gravação e voz externa; efeitos não acionam detector | Teste real compara componente de 1000 Hz com/sem fala de 440 Hz |
| EOF da fala encerrava a cama musical | Detector preenchido com silêncio após fim da fala; ramo de foreground mantém duração original | Nova regressão de voz/gravação e reprodução independente resolvida, registrada em independent-code-review.md |
| Arquivos explicitamente solicitados ausentes eram ignorados | Falha clara antes da codificação; fontes de áudio exigem stream de áudio | Inspeção e fluxo de entrega real; fontes explícitas válidas continuam cobertas |
| Slug de manifesto podia escapar do destino, ganho não finito e CRF fora de faixa | Validações antecipadas de slug/gain/CRF | Revisão do diff e suítes de entrega; sem alegação de fuzzing exaustivo |
| Capítulos com NaN/infinito/None/negativo ou fora da duração | Rejeição antes de formatar relatório | Teste de regressão por valores inválidos |
| Duração zero/negativa de projeto | Rejeita antes de criar diretórios; zero não vira default silencioso | CLI real, preservando diretório vazio |

Os testes verdes iniciais não cobriam esses comportamentos. Uma regressão encontrada pela revisão independente foi corrigida e retestada, sem retirar o teste que a detectou.

Uma leitura cruzada final encontrou descrições geradas em `review.py` ainda exigindo zoom alternado, efeito por intervalo, câmera sempre em movimento, até seis palavras em todo o quadro e final em loop. As definições de Gancho/Ritmo/Motion/Som/Payoff/Corte/Enquadramento foram alinhadas às referências já corrigidas: ritmo, pausa, recorte e som por função, sem quotas universais. Não mudaram IDs da rubrica, gates instrumentados, notas mínimas, hashes ou independência. Os inputs anteriores permanecem imutáveis, com seus critérios originais; os resultados dos cenários não foram promovidos por essa mudança. Após o ajuste descritivo, a suíte Python inteira passou novamente: 174/174 em 13,511 s.

## Evidências automatizadas

Baseline: 135 testes Python aprovados e 12 Node. Final: ver logs integrais anexos e summary.json (contagem extraída automaticamente). Sem skips nos conjuntos finais. `tests/integration_pipeline.py --node-root <runtime existente>` concluiu com `technical_smoke_passed:true`, incluindo mix de efeitos, deliver, revisão parcial, rejeição de evidência pendente e de manifesto alterado. Não representa validação de API/modelo real ou aprovação estética.

O workflow GitHub foi ampliado para FFmpeg/Python/Node/Chrome, mas não foi executado no runner remoto. Instalações locais, downloads de modelos/browsers, serviços pagos, publicação e alteração da skill instalada não fazem parte das ações realizadas.
