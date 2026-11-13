# Avatares e UGC

UGC é uma linguagem de performance e demonstração; pode usar gravação real ou apresentador sintético identificado. Use o [brief de marketing](../marketing.md) em divulgação de produtos e serviços.

## Escolha e capacidade real

- UGC real: entra pelo fluxo de [gravação](gravacao.md), preservando naturalidade e demonstração.
- Avatar: criar identidade/performance → voz → render falante → composição e B-roll → entrega/revisão.
- Os scripts atuais importam e editam o vídeo do avatar; não incluem um gerador de avatar/lip-sync. A geração precisa de workflow ComfyUI realmente disponível e validado. Registrar em `tool_plan` como `adaptacao` até testar uma saída; não afirmar suporte nativo por apenas listar um repositório.

Escolha o gerador conforme identidade, expressão, enquadramento, idioma, qualidade e recursos disponíveis. Se o usuário já usa um serviço, preserve essa escolha. Não iniciar cobranças, enviar material privado ou usar conta sem a autorização pertinente. Sem gerador disponível, PARE, entregue roteiro/performance/voz e indique o bloqueio; rosto estático/robô com zoom seria **animatic**, não avatar falante final. Só produza essa alternativa com escopo aceito e identificação explícita. Aplique as [regras de composição](../composition.md#regras-de-acabamento-obrigatórias).

## Produção

1. Definir personagem, objetivo, aparência, referência de identidade, plano, olhar e estilo de performance. Imagem/voz real de terceiro exige consentimento; personagem fictício precisa ser apresentado com transparência.
2. Roteirizar para fala natural: frases pronunciáveis, pausas e gestos com intenção. Em marketing: demonstração, prova real e CTA. Avatar pode apresentar; não deve fingir ser cliente com experiência real.
3. Produzir a voz e medir sua duração; manter o mesmo arquivo como referência de lip-sync. Use Kokoro conforme a escolha de voz disponível; não comprimir o vídeo para disfarçar fala fora de tempo.
4. Gerar o apresentador na ferramenta escolhida, registrando versão, entradas, parâmetros, saída e direitos dos ativos. Avaliar um trecho curto antes do vídeo completo.
5. Importar com `footage.py import` e seguir seleção, enquadramento e composição. Cobrir com produto real/B-roll onde acrescentar informação; preservar tomadas de rosto suficientes para a performance fazer sentido.
6. Tratar cor, ruído e luz para integrar avatar, demonstração e elementos gráficos. Legendas fora da boca/rosto. Exportar por `deliver.py` e revisar o mesmo arquivo final.

## Revisão específica

Inspecionar temporalmente o início e passagens com consoantes, viradas de cabeça, gestos e cortes. Conferir boca/voz, olhos/dentes/mãos, estabilidade de identidade, expressão, pausas, transição para B-roll e enquadramento. Uma grade parada não comprova lip-sync. Registrar método e intervalos em `assessment.json`; áudio não ouvido deve ser descrito como inspeção instrumentada, com limites explícitos.

O formato `avatar` acrescenta Sincronia labial à rubrica; conversão acrescenta Mensagem e CTA. Para UGC real, Corte de fala e Enquadramento continuam centrais. Não publicar nem gerar depoimentos fictícios. Marcar `publish.ai_label` e divulgação comercial quando aplicável.
