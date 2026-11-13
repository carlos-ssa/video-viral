# Receitas de prompt: ideia única e explicador por batidas

Use estas receitas opcionais para estruturar o brief e dirigir o vídeo. São métodos adaptáveis, não um pacote de regras universais nem autorização para produzir durante um estudo. Preserve o [roteiro](writing.md), a [composição](composition.md), o [motion](motion.md) e os portões da skill.

Se o usuário escolher parâmetros exatos ou exigir aprovação, respeite-os; adapte somente o que o pedido deixou aberto. Exemplos enviados para estudo não são, por si só, um pedido para iniciar aquela produção ou trocar o stack.

## Brief em quatro entradas

Aproveite tudo que o usuário já informou; não reapresente um questionário completo. Pergunte somente faltas essenciais que não possam ser inferidas e registre suposições no manifesto.

| Entrada | Definição útil |
|---|---|
| Tema | Assunto ou pergunta concreta; para ciência, pode ser um “e se…?”. |
| Público | Quem assiste, conhecimento prévio e contexto de uso. |
| Mensagem central (`brief.core_message`) | Uma frase que a pessoa deve lembrar; conecte objetivo e recompensa. |
| Duração | Faixa desejada, por exemplo 15–60 s; distinguir meta de duração final medida. |

Plataforma, aspecto, idioma, fontes, oferta e CTA vêm do contexto e do brief existente. Só peça um dado adicional quando sua ausência impedir uma decisão essencial. Não solicite chave de serviço externo para aplicar estas receitas.

## Método comum

1. Escreva primeiro o fecho: resposta, consequência ou recompensa que cumpre a mensagem central.
2. Volte do fecho às batidas necessárias e então escreva o gancho. Elimine desvios que disputem a mesma mensagem.
3. Una fala, texto e visual na mesma promessa. “Você”, contraste e frase curta são opções de gancho; limites como 12 palavras dependem de idioma e leitura.
4. Organize pares **CLAIM → PROOF**: afirmação → evidência disponível ou demonstração visual planejada. Nomeie qual delas existe.
5. Marque o tempo inicial como estimativa. Depois de gerar/receber e medir a voz, reancore cenas e eventos nos cues de palavras conferidos.
6. Mantenha uma bíblia visual curta: linguagem, formas, paleta, tipografia, luz, escala e identidade. Repita esse núcleo nos prompts de cena.

**Prova e ilustração:** filmagem, dado ou documento verificável pode sustentar uma afirmação factual; uma animação conceitual apenas explica um mecanismo ou hipótese. Escreva essa distinção no plano e sinalize na peça quando houver risco de confusão. Sem evidência, pesquise, qualifique ou retire a afirmação; desenhar um gráfico não cria evidência.

Use logos/UI autênticos quando representar um produto real, com fonte e direitos adequados. Uma reconstrução deve reproduzir fielmente o que se conhece, sem inventar resultados, depoimentos, métricas ou funcionalidades. Para explicadores autorais, prefira cartoon original e referências de linguagem, sem copiar personagens ou identidade de outro canal.

## Receita A — reel de uma ideia, 15–60 s

Boa para uma transformação, demonstração de produto, argumento curto ou descoberta. Não acrescente várias teses só para preencher a duração.

| Batida | Direção |
|---|---|
| Gancho | Entregar assunto e tensão cedo; testar clareza dos primeiros 1–3 s com fala, visual e texto coordenados. |
| Desenvolvimento | Encadear poucos pares CLAIM → PROOF; cada plano muda o que se entende. |
| Recompensa | Mostrar a transformação, resposta ou comparação prometida. |
| Fecho | Retomar o início ou oferecer CTA coerente com o objetivo e destino real. |

Quando adequado, o quadro inicial já contém ação e poucos elementos para ler. Isso não proíbe um início estático deliberado que funcione no formato. Um objeto que evolui entre cenas pode dar continuidade melhor que cartões desconectados.

Escolha 1080×1920 para destino vertical; 60 fps pode favorecer movimento rápido, mas não é obrigatório. Compare necessidade, fonte, custo e entrega; 30 fps continua válido. Justifique o estilo em uma linha. Fundo escuro, uma cor de destaque e 2–5 acentos fortes são opções editoriais, não quotas.

Use o teste de reprodução a 1,5× como heurística subjetiva de ritmo. Se parecer melhor, investigue pausas, redundância e duração dos planos; não acelere a fala ou corte compreensão automaticamente. Ajuste cortes à música quando isso preservar sentido, respiração e prova.

## Receita B — explicador científico por batidas e palavras

Boa para hipótese, causa/consequência ou mudança de escala. Defina o que é observado, modelo aceito e suposição contrafactual antes de construir a metáfora visual.

| Batida adaptável | Cue e função visual |
|---|---|
| Evento | Uma palavra-chave dispara a transformação que apresenta a hipótese. |
| Escala | Abrir o enquadramento para revelar relações espaciais ou temporais. |
| Proximidade | Aproximar uma consequência concreta para o espectador. |
| Consequência | Demonstrar o mecanismo, com contador somente quando houver modelo válido. |
| Escalada | Revelar uma consequência adicional que faça avançar a mesma ideia. |
| Respiro | Humor ou reação breve, se combinar com público e assunto. |
| Retorno e título | Recuperar um elemento inicial e concluir a mensagem. |

Essa forma não fixa segundos ou exige um movimento em cada frase. 1920×1080 a 30 fps é uma opção para explicação horizontal; adapte ao destino e à leitura. Mascote, shader, planetas, paleta espacial e proibição de pontos finais pertencem a escolhas de um projeto, não à receita.

Associe cada evento a `cue`, palavra/trecho e transformação; após medir o áudio, registre o tempo real correspondente. Mudou a voz? Refaça a ancoragem. Batidas da música complementam esse mapa sem deslocar a palavra que dá sentido ao evento.

Todo número científico precisa de fonte, unidade, hipótese relevante e escala de tempo. Diferencie valor aproximado, faixa e simulação. Temperatura, propagação, velocidade e efeitos gravitacionais não podem virar números decorativos. Não trate uma frente visual acelerada para legibilidade como simulação física em escala.

Se condensar minutos ou anos em segundos, explicite a compressão temporal. Contadores como “você apertou play há…” devem derivar do tempo de reprodução e do evento definido, coerentes com o instante exibido; não cole um valor fixo de outro roteiro. Contadores científicos derivam do relógio/modelo da história, com rótulos de unidade e escala.

## Tempo, câmera e execução no stack

O compositor continua **HyperFrames + GSAP**, com timeline pausada e estado calculado no tempo solicitado. Use apenas módulos pertinentes do stack; esta receita não instala nem troca o compositor. Voz segue Edge TTS ou WAV externo, com faster-whisper e conferência dos tempos, conforme [voz e legendas](modules.md#voz-e-legendas). Não introduza Kokoro, ElevenLabs ou renderizador Playwright alternativo.

Quando houver rewind ou salto narrativo, mantenha dois relógios explícitos:

- `t_ambient`: tempo de reprodução para ambiente, cintilação e movimentos contínuos.
- `t_story = warp(t_ambient)`: função determinística por trechos para eventos da história, incluindo avanço, pausa ou retrocesso intencionais.

Calcule poses, contadores e consequências no relógio apropriado; não acumule estado por chamadas. Grain/noise usa seed estável por frame ou bucket temporal calculado, nunca novo aleatório a cada seek. Teste busca fora de ordem, como 2→0→2, com o mesmo resultado no mesmo tempo. Não acrescente um loop autônomo para simular esses relógios.

Câmera deve revelar, acompanhar ou comparar; plano fixo também serve. Movimentos, easing e blur são escolhidos por intenção, escala e legibilidade. Não aplique tremor, movimento ou blur a tudo: textos, números e interfaces precisam continuar legíveis. Zoom digital não equivale a deslocamento 3D.

Antes de compor/modelar no Blender, reúna e inspecione fotos/frames e trechos autorizados conforme [câmera e referências](camera-references.md). Entregue mídia acessível e decisões por plano ao executor e carregue o pacote no arquivo de trabalho; URL ou nome de filme não substitui entrada visual. Pesquise [itens 3D gratuitos](free-3d-assets.md) coerentes com essa direção, verificando licença por item antes de usar.

## Texto e som: parâmetros para testar

Para cartões curtos, `máx(1,5 s; 0,4 s + caracteres/15)` pode iniciar uma estimativa de leitura. Valide no tamanho e contexto reais; reduza texto quando necessário. Essa fórmula não cria timestamps de fala, não substitui alinhamento de legendas e não garante compreensão de números complexos.

Hierarquia, área segura e pausas de leitura seguem a composição. Tipografia contida e destaque recorrente ajudam a guiar o olhar; quantidade de palavras grandes depende do conteúdo. Confira a passagem em movimento, não apenas um frame.

Valores como −20 dB ou −7 dB podem iniciar o ajuste de ganho da pista de música em contextos distintos. A relação audível com a voz depende dos níveis das fontes; ganho de pista não garante relação sinal/ruído, loudness relativo ou inteligibilidade. Meça e escute a mix. Efeitos pontuam ações e transições pertinentes, sem obrigação de um efeito por objeto ou de som somente em aparições.

Em peça musical, a duração pode seguir a faixa medida. Em narrado, concilie voz medida, mensagem e duração pedida e escolha um fecho musical coerente; não estique a fala para caber numa animação ou numa duração copiada do exemplo.

Se a entrega pedir −14 LUFS integrados, meça após mix/master e ajuste ao destino. Pico verdadeiro é medido em **dBTP**; pico de amostra em **dBFS** não é equivalente. Defina e confira o teto de true peak apropriado, em vez de prometer que um limiter ou valor de ganho sozinho resolve loudness e picos.

## Entregas e checklist

Entregue em ordem, mantendo estimativas claramente identificadas até existir áudio medido:

1. Roteiro CLAIM → PROOF, fontes/hipóteses e tempos ou cues; uma mensagem e um fecho que cumpre o gancho.
2. Tabela por cena: intervalo, fala/cue, texto, evidência ou ilustração, visual, câmera e som.
3. Prompts executáveis por cena quando pertinentes ao motor escolhido; repetir o núcleo de estilo e especificar sujeito, ação, composição, continuidade e limites. Para Blender/código, fornecer parâmetros e referências além do texto descritivo.
4. Quadros de estilo/contact sheet e preview das batidas relevantes antes do render completo, conforme o escopo; frame isolado não comprova movimento ou sincronismo.
5. Checklist: gancho claro; promessa cumprida; provas qualificadas; ritmo e leitura; consistência visual; cues medidos; câmera e som funcionais; direitos; revisão e limitações reais.

Aprovação de roteiro é uma pausa quando expressamente exigida no escopo. Fora disso, prossiga no trabalho autorizado, cumprindo os portões de planejamento, entrega e revisão da skill. Estas receitas não alteram consentimento para instalação, publicação ou revisão humana nem transformam estudo de prompt em pedido de produção.
