# Marketing, oferta e ganchos

Use em divulgação de produtos/serviços e quando o objetivo for leads, consideração ou venda. Em entretenimento, animação ou música, mantenha as partes editoriais pertinentes; não transforme todo conteúdo em anúncio.

## Brief antes da criação

Preencha `brief` no manifesto a partir do pedido e do material disponível:

| Campo | Decisão |
|---|---|
| objective | alcance, consideracao, conversao ou entretenimento; uma prioridade principal |
| audience / niche | Quem precisa se reconhecer, contexto e familiaridade com a solução |
| problem_or_desire | Problema observável, desejo ou pergunta concreta |
| offer / benefit | Produto ou serviço real, o que entrega e por que importa |
| proof | Demonstração, informação verificável, resultado documentado ou depoimento autorizado |
| objections | Dúvidas que impedem a ação: preço, confiança, necessidade, esforço |
| desired_action / cta_destination | Ação única e destino que existe na plataforma escolhida |
| success_metric | Métrica vinculada ao objetivo, com fonte e denominador quando houver dados |
| assumptions | Inferências necessárias, sem inventar preços, funcionalidades ou clientes |

Ausência de uma prova pede demonstração real ou argumento verificável. Não substitua por depoimento de avatar, número fabricado ou promessa sem fundamento. Quando o pedido já identifica a oferta, avance sem questionário. Quando nem o contexto identifica o produto/serviço, peça somente esse dado essencial.

## Estrutura editorial e comercial

Alcance: reconhecimento/curiosidade → desenvolvimento útil → recompensa → próxima ação pertinente.
Consideração: problema/objetivo → solução em uso → prova/comparação → objeção relevante → ação.
Conversão: reconhecimento do problema/desejo → benefício demonstrado → prova → oferta clara → CTA.

Essas são opções de progressão, não um roteiro imutável. A ordem muda com o nicho, o nível de consciência e o material. Anúncio, demonstração, tutorial e UGC precisam soar adequados à audiência. Preserve linguagem natural e o padrão de edição profissional.

## Gancho é uma abertura audiovisual

Em uma produção completa, crie cinco alternativas em `hook_candidates`. Para cada uma:

- `id`, `angle`, `audience`: ângulo e público que pretende atrair.
- `opening_visual`, `opening_line`, `on_screen`, `sound`: o que se vê, ouve e lê na abertura.
- `promise`, `payoff`: qual curiosidade/promessa o restante realmente resolve.
- `scores`: relevância, curiosidade, clareza, força visual e cumprimento (1–5 com justificativa curta).
- `hypothesis`: por que essa abertura pode funcionar neste nicho/plataforma; fonte observada ou hipótese.

Selecione pela adequação ao objetivo e à promessa, não só pela maior soma. Copie a frase escolhida para `hook`, mantendo os candidatos. Tipos a explorar: demonstração do resultado, problema reconhecível, contraste, descoberta, pergunta concreta ou objeção. Não aplicar culpa/medo/urgência artificial como receita universal.

Em vertical, torne a proposta compreensível nos primeiros instantes; no longo, desenvolva a promessa inicial e reabra interesse por blocos. O primeiro quadro precisa trabalhar mesmo sem som. A fala não precisa dizer tudo: imagem e texto podem completar a informação.

## Padrões de gancho relatados em formatos com IA

A [pesquisa documental](formats/virais-ia.md#fotografia-da-pesquisa-13112026) sugere padrões para testar, não resultados garantidos nem observação direta dos vídeos:

- Abrir com contradição ou perigo concreto da história, nunca com apresentação do canal. Não fabricar ameaça real, urgência ou informação factual para conseguir atenção.
- Colocar o personagem dentro do conflito, em primeira pessoa: ele relata o que está vivendo, em vez de anunciar o tema de fora.
- Serializar com personagem fixo, recompensa no episódio e gancho para o próximo. Oferecer uma decisão ao público sem fingir votação/participação que não existe.
- Usar linguagem local sobre história conhecida para criar reconhecimento, sem trocar fatos por estereótipos ou desrespeito; em temas bíblicos, seguir a revisão do catálogo.

Dos cinco candidatos já previstos, preparar **três aberturas por roteiro para teste**, mantendo o corpo e o payoff comparáveis. Registrar hipótese e variável; sem publicação/analytics, entregar variantes, não declarar uma vencedora por desempenho inexistente.

## Retenção e conversão na montagem

Planeje a função de cada batida: abrir pergunta, demonstrar, aprofundar, provar ou recompensar. A cada mudança visual, pergunte o que ela acrescenta. Use performance, enquadramento, câmera, motion, B-roll, gráficos e som para organizar atenção. Pausas e contraste também dão ritmo; efeito a cada palavra não é critério de qualidade.

`cta` deve dizer uma ação compatível com o destino: visitar link disponível, comentar, enviar mensagem ou agendar. Não prometer DM automática ou recurso inexistente. Em longo, posicionar o CTA quando houver valor entregue; em anúncio curto, deixá-lo legível no final e coerente com a oferta.

## Variações e aprendizado

Prepare variantes comparáveis: manter o corpo e variar a abertura, ou manter abertura e variar a demonstração. Não altere tudo no mesmo teste. Registre hipótese, variável, público/plataforma, período e métrica antes de comparar.

Retenção/completude/replays ajudam a avaliar atenção; contatos, cliques qualificados e vendas ajudam a avaliar ação quando esses dados existem. Não confundir visualizações públicas com retenção ou faturamento. Registrar resultado indisponível como indisponível. [Pesquisa](research.md) distingue essas fontes.

Antes de entregar o plano, salve as decisões no manifesto e execute `scripts/plan.py`. Dado essencial desconhecido fica em `brief.missing_inputs` pelo nome do campo; não substituir por valor inventado. Código 2 identifica um plano provisório com pendências explícitas.
