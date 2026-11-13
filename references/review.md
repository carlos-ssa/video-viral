# Revisão audiovisual e veredito

Revisar é examinar o arquivo que será entregue. Nota estética não mede viralidade e uma grade parada não comprova áudio, fluidez ou sincronia. Medições instrumentadas apoiam a revisão; aprovação audiovisual completa exige observação registrada por revisor independente em todas as modalidades aplicáveis. Declare método, cobertura e limitações reais.

## Ciclo

1. Aprovar internamente os quadros de estilo e um trecho representativo antes do render completo.
2. Renderizar e executar `deliver.py`; ele grava o arquivo final, o relatório e `out/delivery.json`, com hash e resultado técnico.
3. Executar `review.py <projeto> --producer-id <id-do-autor>` sobre a entrega. Cada `review/rNN/` contém `hook.jpg`, `grid.jpg`, `metrics.json`, `assessment.json`, `report.md` e o pacote `input/`. `--video` pode analisar uma prévia, mas o veredito final exige uma entrega técnica correspondente.
4. Examinar composição, enquadramento e legibilidade; inspecionar temporalmente os trechos relevantes, transições e sincronismo; ouvir o áudio quando a ferramenta permitir. Para um vídeo curto, preferir revisão integral; para longo, registrar os intervalos observados e combinar com análise instrumentada de toda a faixa.
5. Registrar `assessment.json` e preencher notas do relatório com evidência/trecho e correção quando necessária. Preserve as quatro colunas da tabela gerada (critério, definição, nota, evidência/correção): o veredito lê a coluna Nota. Critério duplicado, tabela malformada ou observação ausente tornam a avaliação incompleta (2), sem recuperar números de outra coluna. Depois executar `review.py <projeto> --verdict`.

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

## Gates instrumentados e limites

Os limiares ficam em constantes nomeadas em `scripts/review.py`. Os tempos e a correção sugerida aparecem nos alertas; são medições do render, não prova de qualidade perceptual.

- **Congelamento:** amostragem a 5 fps; pixels com diferença de luma >8 contam como mudança, mesmo localizada (≥0,02% do quadro reduzido). Aviso a partir de 1,5 s / bloqueante a partir de 2,5 s em curtos; 6 s / 12 s em longos. Um trecho até o fim usa sua duração real, com o mesmo limiar do meio. Legendas com intervalos de exibição sobrepostos tornam o trecho um aviso de leitura, não erro automático. Assistir continua obrigatório para julgar movimento significativo.
- **Longo:** 16:9 ou duração >180 s; aviso de plano >15 s e lacuna visual >8 s, em vez de 3,5 s / 3 s dos curtos. Entrada da fala até 3 s, em vez de 0,7 s. Longo não precisa imitar a cadência de um short.
- **Fala:** `voice.engine: "none"`, formato música/ASMR ou cenas com `narration` explicitamente vazia dispensam o gate de início de fala. Áudio de gravação/corte/UGC continua sendo tratado como fala. Um estalo ou pulso não é ASR nem evidência de fala atrasada.
- **Silêncio:** `silencedetect` no áudio final, −45 dB, intervalos ≥0,15 s; o relatório registra os intervalos e a proporção audível. Silêncio interior ≥0,7 s avisa nos curtos (≥2 s nos longos). Vídeo sem fala com menos de 50% do tempo audível bloqueia: o gate de LUFS sozinho ignora os vazios e não aprova um ASMR quase mudo.
- **Cauda morta:** silêncio + imagem parada/quase parada + ausência de legenda por >1 s no curto (>3 s no longo; tolerância de 0,05 s) bloqueia. Além do congelamento estrito, mede energia residual de luma (média ≤0,5 e nenhum quadro >1,5, normalizada para 10 fps), para não aceitar um fim vazio só porque há uma oscilação mínima. O limiar residual é usado somente em conjunto com silêncio e ausência de legenda, não para acusar congelamento de animação localizada.
- **Tempos de legenda:** lê `captions/captions.ass` ou os grupos `{start,end,text}` de `captions/captions.json`. `words.json` contém palavras ASR, não intervalos de exibição. Se o HTML/áudio embutido não tem tempos confiáveis, uma possível cauda só avisa; o revisor precisa confirmar o fim no render. Sem fala ou com `captions.enabled: false`, na ausência desses arquivos considera-se que não há legenda de fala. Mantenha esses metadados consistentes com o render, inclusive quando usar `--no-captions`.
- **Cama sonora:** narrados, gravações e cortes avisam quando não há música/ambiente registrado. Dispensa editorial explícita: `"music": {"bed_waiver": "Demonstração só com voz, sem cama por intenção editorial"}`. Uma justificativa não dispensa os gates de silêncio/cauda. Arquivos `audio/music.wav`, `ambient.wav`, `ambience.wav`, `ambiente.wav`, `bed.wav` ou `trilha.wav`, ou ativos com esses nomes/kinds/roles, são aceitos. O registro não prova que a cama foi mixada ou ouvida; confira o render.
- **Efeitos:** não exige `kind: "sfx"`. Aceita a saída real `audio/sound-design.wav`, conteúdo em `audio/sfx/`, ativos com nome `sound-design`/`sfx`/`foley`/`effects`/`efeitos`, ou `kind`/`role` de efeito (`sfx`, `sound-design`, `foley`, `effect`, `efeito`). Exemplo válido: `{"path":"audio/sound-design.wav","kind":"audio"}`; para nome personalizado use `{"path":"audio/transicoes.wav","kind":"audio","role":"sfx"}`. Declarações em prosa de efeitos planejados não comprovam um ativo.
- **Ocupação:** aviso quando uma faixa horizontal contígua >30% da altura tem ≥90% dos pixels quase da mesma cor RGB (tolerância 10/255), em ≥90% das amostras, até 48 amostras a 90×160. Um rodapé fino não deve mascarar uma região vazia; textura/movimento significativo e mudança de cor não devem ser confundidos com preenchimento uniforme. O alerta diz a faixa e o período amostrado; espaço negativo intencional exige julgamento, não bloqueio automático.

### Sobreposição de textos no render (obrigatório ao revisor)

O review atual não recebe caixas do DOM sincronizadas com o MP4, e ASS/tempos ASR não dizem onde ficam títulos, rótulos e rodapés no render. Não há gate automático confiável de colisão; lint HTML não substitui esta inspeção. **Em Legibilidade, verificar e registrar os instantes de maior ocupação**, incluindo entrada/saída, legenda de duas linhas, título/rótulo fixo, fonte/crédito, CTA/cartão final e rodapé. Confirmar ausência de interseção, corte da caixa ou vazamento fora da área segura no arquivo final. Se houver colisão, mover/redimensionar uma zona e rever o trecho. Não dar nota ≥4 sem essa checagem; grade amostrada pode perder uma colisão transitória. Automação futura exige caixas reais por instante e vínculo com o hash do render, não uma heurística de OCR/contagem de palavras.

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

Cada nova rodada precisa de uma alteração concreta ou nova evidência. A CLI não consegue provar por hash, sozinha, que a mudança foi significativa; o coordenador verifica esse requisito. A tentativa de gerar r04 retorna 3 e preserva as rodadas existentes. `--every` deve ser finito e positivo; a grade deve respeitar o limite JPEG/FFmpeg de65.500pixels por eixo, sem presumir que maior quantidade de quadros comprova inspeção temporal. Mudar somente uma nota não corrige o vídeo. Se uma dependência impede a inspeção, instalar somente quando necessária e permitida; aplicar uma reserva documentada quando indisponível e registrar a limitação. Não fazer três renders idênticos esperando mudar o resultado.

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

O pacote input/ contém somente vídeo, hook.jpg, grid.jpg e request.json com briefing/direção/referências, critérios e dados técnicos. Ele não copia report.md, assessment.json nem notas/conclusões do autor. O vídeo é uma cópia independente (nunca hard link); o hash é conferido na cópia e no veredito. Sobrescrever a entrega não altera a evidência das rodadas antigas, mas invalida a aprovação correspondente. Mantenha input/ imutável e não acrescente o relatório do autor.

Dê esse pacote ao revisor em contexto próprio e somente leitura, conforme o isolamento que o runtime realmente suportar. Sem suporte técnico, isso é um contrato de escopo, não uma barreira de segurança; informe a limitação. O revisor deve devolver sua avaliação sem consultar o restante do projeto ou a autocrítica do autor.

Transfira o preflight para assessment.json.reviewer_preflight. O revisor registra observed/instrumented/unverified por canal, método e intervalos efetivamente inspecionados e escreve suas próprias notas em report.md. Um revisor humano também pode cumprir esse papel, com identidade distinta e evidências honestas. O autor não substitui essa aprovação preenchendo a própria ficha. Sem revisor independente disponível, registre autoverificação como tal e mantenha a aprovação independente pendente.

### Exemplo de autoverificação sem revisor independente

Preserve `reviewer_preflight` vazio e os canais principais `pending` gerados pelo script. Acrescente **somente** um campo `self_check` ao `assessment.json` da rodada (exemplo parcial para vídeo de 18 s; ajuste método/intervalos ao que realmente fez):

```json
"self_check": {
  "producer_id": "autor-da-rodada",
  "independent": false,
  "visual": {"status": "instrumented", "method": "Inspeção de hook.jpg e grid.jpg; não reproduzi o vídeo", "ranges": [[0, 18]]},
  "motion": {"status": "instrumented", "method": "Cortes e energia de movimento medidos por FFmpeg", "ranges": [[0, 18]]},
  "audio": {"status": "instrumented", "method": "silencedetect e LUFS; sem escuta perceptual", "ranges": [[0, 18]]},
  "limitations": "Autoverificação do autor; revisão audiovisual independente pendente"
}
```

Os intervalos instrumentados descrevem o material coberto pelas métricas, não reprodução/escuta integral. Se não mediu uma modalidade, use `unverified` com método/limite honesto e `ranges: []`. Registre autocrítica em seção própria do report.md, sem preencher a ficha humana nem as notas do revisor; não envie essa seção no pacote input/. O veredito permanece **2 (independente pendente)** com o preflight e canais principais ainda vazios; `self_check` nunca concede aprovação. Se a entrega técnica falhou, relate também os bloqueantes, sem dizer “entrega técnica aprovada”.

A aprovação completa exige que a união dos intervalos observados cubra a duração em cada modalidade aplicável; amostragem permanece parcial, inclusive em vídeo longo. Áudio só pode ser not_applicable se a análise técnica registrar ausência de fluxo de áudio. Um limite de modalidade ou de cobertura deve aparecer no relatório, não virar nota alta. Revisões legadas sem input/ e identidades ficam incompletas até nova análise.

Os campos e hashes detectam registros incompletos/inconsistentes, não autenticam pessoas, ferramentas ou relatos. O coordenador verifica evidências críticas e não descreve a checagem estrutural como prova automática de que o vídeo foi assistido/ouvido.
