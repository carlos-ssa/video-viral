# Revisão audiovisual e veredito

Revisar é examinar o arquivo que será entregue. Nota estética não mede viralidade e uma grade parada não comprova áudio, fluidez ou sincronia. Medições instrumentadas apoiam a revisão; aprovação audiovisual completa exige observação registrada por revisor independente em todas as modalidades aplicáveis. Declare método, cobertura e limitações reais.

## Ciclo

1. Aprovar internamente os quadros de estilo e um trecho representativo antes do render completo.
2. Renderizar e executar `deliver.py`; ele grava o arquivo final, o relatório e `out/delivery.json`, com hash e resultado técnico.
3. Executar `review.py <projeto> --producer-id <id-do-autor>` sobre a entrega. Cada `review/rNN/` contém `hook.jpg`, `grid.jpg`, `metrics.json`, `assessment.json`, `report.md` e o pacote `input/`. `--video` pode analisar uma prévia, mas o veredito final exige uma entrega técnica correspondente.
4. Examinar composição, enquadramento e legibilidade; inspecionar temporalmente os trechos relevantes, transições e sincronismo; ouvir o áudio quando a ferramenta permitir. Para um vídeo curto, preferir revisão integral; para longo, registrar os intervalos observados e combinar com análise instrumentada de toda a faixa.
5. Registrar `assessment.json` e preencher notas do relatório com evidência/trecho e correção quando necessária. Depois executar `review.py <projeto> --verdict`.

Todos os comandos são relativos ao diretório desta skill; use caminhos absolutos ou o workdir correto.

## Rota humana (padrão sem reprodução/escuta no runtime)

Quando a entrega técnica passou e só falta inspeção perceptual, o relato normal é **entrega técnica aprovada, revisão humana pendente**. Isso não é falha que peça três renders iguais, nem aprovação audiovisual: o veredito mantém código 2 para ficha/evidência não preenchida ou 1 para inspeção parcial. Se há bloqueantes técnicos/rascunho, o script relata também essa falha, sem anunciar entrega técnica aprovada.

Cada rodada gera `ficha-humana.md` ao lado de `input/`, com hashes já preenchidos e campos humanos vazios. Entregue **somente input/ e essa ficha** a uma pessoa distinta do autor, em contexto próprio, sem report.md/assessment.json ou autocrítica. O autor não preenche confirmações/notas em nome da pessoa.

1. A pessoa abre o vídeo de `input/`, lê briefing/referências/critérios em `request.json` e assiste ao vídeo inteiro, ouvindo a faixa inteira quando houver áudio.
2. Preenche `Revisor` com identidade estável distinta do autor; confirma com `SIM` que não consultou notas do autor, que assistiu e que ouviu integralmente (`NA` para áudio só quando o vídeo não tem fluxo de áudio).
3. Registra início/fim em segundos com ponto decimal, cobrindo a duração de `request.json`, método/aparelho e observações gerais. Preenche cada critério com nota 1–5 e observação/trecho; não altera os hashes. Se não concluiu a observação, devolve a pendência sem confirmar integralidade.
4. O coordenador importa a ficha preenchida na **mesma rodada**, sem renderizar de novo apenas para ingerir evidência:

```sh
python scripts/review.py <projeto> --human-form <projeto>/review/r01/ficha-humana.md
python scripts/review.py <projeto> --verdict
```

A ingestão valida campos, hashes, separação autor/revisor e cobertura; grava preflight humano e canais `observed` em assessment.json e transfere as notas para report.md. Depois executa o mesmo veredito, incluindo hashes do pacote/imagens, recibo técnico, bloqueantes, rubrica e limite de rodadas. Ficha vazia, cobertura parcial, hash diferente ou autor=revisor não autorizam aprovação. Nota baixa continua reprovando. O registro é uma declaração verificável quanto à consistência, não autenticação nem prova automática de reprodução/escuta.

## Registro de inspeção

`assessment.json` é gerado com o hash do vídeo e três canais: `visual`, `motion` e `audio`. Cada um registra:

```json
{"status": "observed", "method": "reprodução e inspeção das transições", "ranges": [[0, 12.5], [28, 35]]}
```

- `observed`: conteúdo efetivamente visto/ouvido com ferramenta capaz; método e intervalos obrigatórios.
- `instrumented`: apoio por métricas/tempo/alinhamento; método e intervalos obrigatórios. Impede aprovação perceptual completa. Não dizer que ouviu ou assistiu.
- `unverified`: canal não pôde ser verificado; impede aprovação e deve constar da entrega com limitações.
- `pending`: registro ainda não preenchido; veredito incompleto.
- `not_applicable`: aceito somente em áudio quando o vídeo não tem fluxo de áudio.

Uma prancha serve à composição, não ao canal temporal. Loudness e alinhamento de palavras ajudam a avaliar áudio, mas não provam naturalidade de voz. Se falta evidência para uma qualidade perceptual, registrar o limite em vez de atribuir nota alta por conveniência.

## Critérios

O relatório adapta a rubrica: gravação/corte/UGC priorizam Corte de fala e Enquadramento; avatar acrescenta Sincronia labial; storytelling acrescenta Continuidade; música troca Fala e imagem por Sincronismo musical; objetivo de conversão acrescenta Mensagem e CTA. Longo também avalia Retenção por blocos.

| Nota | Interpretação |
|---|---|
| 1 | Quebra o objetivo: ilegível, promessa descumprida, artefato grave ou áudio ininteligível |
| 3 | Correto em parte, com falha perceptível ou evidência insuficiente para o padrão pedido |
| 4 | Cumpre o objetivo com acabamento consistente, sustentado por evidência descrita |
| 5 | Execução excelente e deliberada, sem falhas relevantes no material inspecionado |

Avaliar gancho e payoff, progressão/clareza, direção e motion, legibilidade, som e os critérios do formato. Efeitos/transições precisam contribuir à narrativa. Uma boa pausa não deve ser trocada por ruído visual apenas para atingir uma contagem. Consulte os alertas automáticos e investigue qualquer bloqueante; não apague métricas nem infle notas para aprovar.

## Contrato de aprovação

- Código 0: notas >=4, nenhum bloqueante, artefatos consistentes, entrega técnica publicável e revisão independente com capacidades registradas e observação cobrindo todas as modalidades aplicáveis.
- Código 1: correções ou verificação pendente; escolher as mudanças de maior efeito.
- Código 2: notas/evidências ausentes, malformadas ou desatualizadas. Completar a avaliação ou regenerar a análise; executar o comando não equivale a aprovação.
- Código 3: terceira rodada sem aprovar; entregar o melhor com limitações explícitas, nunca como vídeo aprovado/pronto para publicar.

O hash vincula notas, vídeo, manifesto e imagens. Trocar o render/brief invalida a avaliação; acrescentar o histórico de revisão não a invalida. Rodadas antigas sem esse registro precisam de nova análise. O script checa consistência e resultados registrados, não comprova sozinho que uma pessoa/modelo realmente assistiu nem substitui julgamento audiovisual.

Cada nova rodada precisa de uma alteração concreta ou nova evidência. Mudar somente uma nota não corrige o vídeo. Se uma dependência impede a inspeção, instalar somente quando necessária e permitida; aplicar uma reserva documentada quando indisponível e registrar a limitação. Não fazer três renders idênticos esperando mudar o resultado.

## Aprendizado

Qualidade técnica/estética e desempenho de publicação são medidas diferentes. Depois, com analytics reais, revisar hipóteses de abertura, retenção e CTA. Não preencher taxa de conclusão, vendas ou conhecimento do algoritmo a partir da nota interna.

## Conferir capacidades antes de delegar

Copie assets/reviewer.example.json e preencha com a identidade real do revisor e as ferramentas efetivamente disponíveis. IDs são estáveis por execução; não use apenas nomes genéricos de papel para representar a mesma pessoa/agente. Não presumir capacidades por ranking, família ou nome do modelo.

```sh
python scripts/review.py --check-reviewer capacidades.json --producer-id <id-do-autor>
```

Retorna 0 quando atende ao escopo solicitado; 1 quando só parte é possível; 2 para informação ausente/inválida, autor=revisor ou exposição às notas do autor. `--channels visual` permite conferir um escopo visual limitado, mas não reduz os requisitos do veredito audiovisual.

Para uma capacidade disponível, `method` descreve ferramenta/modalidade e `evidence` aponta documentação ou uma verificação real que a sustente. Quando precisar confirmar uma capacidade, o coordenador verifica uma amostra adequada pela ferramenta nativa antes da delegação. ASR, waveform e LUFS não comprovam escuta perceptual; extrair frames não comprova reprodução temporal. Se só imagens forem possíveis, o trabalho segue como revisão visual parcial, com áudio/movimento pendentes. Não abrir agentes adicionais com as mesmas limitações para simular cobertura.

## Entrada do revisor e devolutiva

O pacote input/ contém somente vídeo, hook.jpg, grid.jpg e request.json com briefing/direção/referências, critérios e dados técnicos. Ele não copia report.md, assessment.json nem notas/conclusões do autor. O vídeo usa hard link quando possível ou cópia; o hash é conferido. Mantenha input/ imutável e não acrescente o relatório do autor.

Dê esse pacote ao revisor em contexto próprio e somente leitura, conforme o isolamento que o runtime realmente suportar. Sem suporte técnico, isso é um contrato de escopo, não uma barreira de segurança; informe a limitação. O revisor deve devolver sua avaliação sem consultar o restante do projeto ou a autocrítica do autor.

Transfira o preflight para assessment.json.reviewer_preflight. O revisor registra observed/instrumented/unverified por canal, método e intervalos efetivamente inspecionados e escreve suas próprias notas em report.md. Um revisor humano também pode cumprir esse papel, com identidade distinta e evidências honestas. O autor não substitui essa aprovação preenchendo a própria ficha. Sem revisor independente disponível, registre autoverificação como tal e mantenha a aprovação independente pendente.

A aprovação completa exige que a união dos intervalos observados cubra a duração em cada modalidade aplicável; amostragem permanece parcial, inclusive em vídeo longo. Áudio só pode ser not_applicable se a análise técnica registrar ausência de fluxo de áudio. Um limite de modalidade ou de cobertura deve aparecer no relatório, não virar nota alta. Revisões legadas sem input/ e identidades ficam incompletas até nova análise.

Os campos e hashes detectam registros incompletos/inconsistentes, não autenticam pessoas, ferramentas ou relatos. O coordenador verifica evidências críticas e não descreve a checagem estrutural como prova automática de que o vídeo foi assistido/ouvido.
