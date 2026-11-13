# Revisão audiovisual e veredito

Revisar é examinar o arquivo que será entregue. Nota estética não mede viralidade e uma grade parada não comprova áudio, fluidez ou sincronia. A revisão pode ser observada ou instrumentada; declare o método e as limitações reais.

## Ciclo

1. Aprovar internamente os quadros de estilo e um trecho representativo antes do render completo.
2. Renderizar e executar `deliver.py`; ele grava o arquivo final, o relatório e `out/delivery.json`, com hash e resultado técnico.
3. Executar `review.py <projeto>` sobre a entrega. Cada `review/rNN/` contém `hook.jpg`, `grid.jpg`, `metrics.json`, `assessment.json` e `report.md`. `--video` pode analisar uma prévia, mas o veredito final exige uma entrega técnica correspondente.
4. Examinar composição, enquadramento e legibilidade; inspecionar temporalmente os trechos relevantes, transições e sincronismo; ouvir o áudio quando a ferramenta permitir. Para um vídeo curto, preferir revisão integral; para longo, registrar os intervalos observados e combinar com análise instrumentada de toda a faixa.
5. Registrar `assessment.json` e preencher notas do relatório com evidência/trecho e correção quando necessária. Depois executar `review.py <projeto> --verdict`.

Todos os comandos são relativos ao diretório desta skill; use caminhos absolutos ou o workdir correto.

## Registro de inspeção

`assessment.json` é gerado com o hash do vídeo e três canais: `visual`, `motion` e `audio`. Cada um registra:

```json
{"status": "observed", "method": "reprodução e inspeção das transições", "ranges": [[0, 12.5], [28, 35]]}
```

- `observed`: conteúdo efetivamente visto/ouvido com ferramenta capaz; método e intervalos obrigatórios.
- `instrumented`: verificação por métricas/tempo/alinhamento, descrita como tal; método e intervalos obrigatórios. Não dizer que ouviu ou assistiu se só fez análise instrumentada.
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

- Código 0: notas >=4, nenhum bloqueante, vídeo e manifesto consistentes, imagens de análise intactas, avaliação registrada e entrega técnica aprovada/publicável.
- Código 1: correções ou verificação pendente; escolher as mudanças de maior efeito.
- Código 2: notas/evidências ausentes, malformadas ou desatualizadas. Completar a avaliação ou regenerar a análise; executar o comando não equivale a aprovação.
- Código 3: terceira rodada sem aprovar; entregar o melhor com limitações explícitas, nunca como vídeo aprovado/pronto para publicar.

O hash vincula notas, vídeo, manifesto e imagens. Trocar o render/brief invalida a avaliação; acrescentar o histórico de revisão não a invalida. Rodadas antigas sem esse registro precisam de nova análise. O script checa consistência e resultados registrados, não comprova sozinho que uma pessoa/modelo realmente assistiu nem substitui julgamento audiovisual.

Cada nova rodada precisa de uma alteração concreta ou nova evidência. Mudar somente uma nota não corrige o vídeo. Se uma dependência impede a inspeção, instalar somente quando necessária e permitida; aplicar uma reserva documentada quando indisponível e registrar a limitação. Não fazer três renders idênticos esperando mudar o resultado.

## Aprendizado

Qualidade técnica/estética e desempenho de publicação são medidas diferentes. Depois, com analytics reais, revisar hipóteses de abertura, retenção e CTA. Não preencher taxa de conclusão, vendas ou conhecimento do algoritmo a partir da nota interna.
