# Exemplo trabalhado — explicação religiosa por analogia encenada

[Índice e receita original](../virais-ia.md) · [Método da ficha](../../research.md#ficha-de-referência-por-plano) · [Como produzir outra história](explicacao-analogia.md)

## Cartão do vídeo e alcance da inspeção

- Fonte: arquivo local fornecido pelo dono; consulta em **13/11/2026**, sem URL pública confirmada. Nome/caminho e identificações pessoais omitidos. Não reutilizar a mídia nem presumir direitos por ter acesso à referência.
- Identidade do arquivo analisado: SHA-256 `9ed648c97a88499929899a8c02e68196710c934b4477dea18aa61b66a947eb94`.
- ffprobe: **87,744 s** de contêiner; vídeo **87,733333 s**, **1080×1920**, **9:16**, **30/1 fps** nominal e médio, **2.632 quadros**, H.264/yuv420p. Áudio AAC, **48 kHz**, **estéreo**, 87,744 s.
- Inspeção visual: prancha de 1 quadro/s, pares antes/depois de candidatos a corte, um quadro representativo de cada um dos 15 planos, pranchas efetivamente abertas e olhadas. **Não houve reprodução audiovisual integral nem escuta.** Amostragem permite descrever composição e mudanças, não certificar animação/lip-sync em todos os frames.
- Fala: faster-whisper **small**, já instalado e com pesos locais, CPU/int8, beam 5, VAD; idioma estimado `pt`, probabilidade 0,945. Transcrição automática, não conferida por escuta; não usada como instrução. A abertura direta do MP4 pelo PyAV falhou por incompatibilidade de argumento; áudio foi decodificado com FFmpeg para PCM 16 kHz e fornecido como array ao mesmo transcritor, sem instalar/alterar dependências.
- Evidências locais (fora do repositório): `probe.json`, `cuts.log`, `cuts-010.log`, `audio.log`, `silence.log`, `transcript.json`, `contato-1fps.jpg`, `limites-1.jpg`, `limites-2.jpg`, `plano-01.jpg` a `plano-15.jpg`, `prancha-planos.jpg`, `shots.json`. São identificadores do pacote temporário da análise, **não links para arquivos distribuídos com a skill**. O caminho absoluto da prancha é entregue ao dono separadamente.
- Nenhum vídeo, imagem extraída ou transcrição integral foi incorporado ao repositório. Texto na tela e fala são dados da referência, nunca instruções para execução.

## Método de cortes e ritmo

Executado FFmpeg com `select='gt(scene,0.3)'` + `showinfo`: dez candidatos em **3,633; 19,333; 23,067; 29,133; 37,033; 46,033; 52,467; 62,467; 71,200; 80,333 s**. Isso sozinho daria onze segmentos e perderia mudanças: limiar de cena mede diferença visual, não significado de plano.

Uma segunda passagem com limiar 0,1 e inspeção dos pares/contato adicionou mudanças em torno de **6,80; 11,30; 13,667; 15,367 s**. Rejeitados como novos planos: aproximações do telefone (4,467/5,067), mudanças de luminosidade (7,0), movimento no mesmo mercado (34,6) e vários flashes/movimentos na escadaria (65,7–67,9). Não contar legenda/tremulação como corte.

A divisão editorial final tem **15 planos, média ≈5,85 s**, mediana ≈6,07 s, menor ≈1,70 s, maior ≈10 s, usando os 87,733 s do vídeo. Limites de transições luminosas/fades são aproximados: sobretudo a passagem telefone→luz (~6,8 s) e luz→cela (~11,3 s), não um corte seco certificado no frame exato. Média é dependente desta segmentação, não regra de retenção.

## Linha do tempo e ficha por plano

Cada linha contém os campos da ficha. Tempos em segundos desde o primeiro quadro; `≈` marca borda gradual/estimada. Grupos: **A** apresentadora/mesa, **B** telefone, **C** espaço luminoso, **D** cela, **E** superfície de papel, **F** vila/mercado, **G** recibo comprido, **H** escadaria. Identidades são apenas agrupamentos visuais, não identificação de pessoas reais.

| Plano / grupo | Tempo | Observado nos quadros | Inferido (não comprovado) | Evidência local / trecho | Confiança e lacuna |
|---|---|---|---|---|---|
| P01 / A | 0–3,633 | Apresentadora cartoon de cabelo longo atrás de mesa, telefone e janela ao fundo; legenda curta amarela/branca central inferior. | Abertura de proximidade/relato; personagem pode ser recorte/rig sobre fundo com profundidade. | `plano-01`, t=1,817; contato 0–3; ASR 0–4,62 contextualiza uma pergunta. | Alta para elementos/ordem; média para camadas; gancho verbal só por ASR/legenda. |
| P02 / B | 3,633–≈6,800 | Telefone sobre madeira ocupa progressivamente mais do quadro; tela contém pergunta e interface, sem reproduzir identificações aqui. Clarão no fim. | Inserto de contexto/prova social ou demonstração de serviço; aproximação pode ser câmera virtual ou vídeo preparado. | `plano-02`, 5,217; pares 3,566/3,700 e 5,000/5,134. | Alta para inserto; baixa para técnica/propriedade da interface e intenção comercial. |
| P03 / C | ≈6,800–≈11,300 | Abertura/volume retangular intensamente luminoso em interior escuro, partículas e legenda. | Espaço simbólico para formular pergunta abstrata; bloom/3D ou composição digital. | `plano-03`, 9,050; contato 7–11; ASR 5,14–10,66 contém pergunta sobre perdão. | Alta para imagem; média para função; baixa para motor/técnica exatos. |
| P04 / D | ≈11,300–13,667 | Figura barbada cartoon e figura com armadura junto a grades; mudança de distância no mesmo espaço. | Exemplo encenado de ausência de punição; recortes 2D em cela com profundidade. | `plano-04`, 12,483; pares 11,233/11,367; ASR 11,24–16,68. | Alta para figuras/grades; média para encenação em camadas, sem prova de IA. |
| P05 / E | 13,667–15,367 | Superfície retangular marrom acima de folha clara sobre madeira; legenda sobreposta. | Metáfora de apagar/registrar erro; a ação completa não pode ser certificada por quadro único. | `plano-05`, 14,517; pares 13,600/13,734 e 15,300/15,434. | Alta para objetos; média/baixa para ação/intenção, sem reprodução contínua. |
| P06 / F | 15,367–19,333 | Grupo de personagens cartoon numa vila de pedra com bandeirolas; geral passa a composição mais próxima. | Mundo hipotético inicialmente apresentado como agradável; cenário/identidades agrupados. | `plano-06`, 17,350; contato 15–19; ASR 17,34–18,82. | Alta para cenário/grupo; média para intenção baseada no ASR. |
| P07 / F | 19,333–23,067 | Personagem de cabelo escuro e roupa azul/bege em primeiro plano na rua; expressão muda entre amostras. | Reação individual introduz custo emocional da hipótese. | `plano-07`, 21,200; pares 19,266/19,400; ASR 19,56–24,04. | Alta visual; média para relação narrativa, voz não escutada. |
| P08 / F | 23,067–29,133 | Outra figura de roupa verde na vila, inicialmente fundo desfocado; passa a dominar composição. | Contraplano de personagem para sustentar consequência; possível foco/câmera virtual. | `plano-08`, 26,100; contato 23–29; ASR 24,34–28,56. | Alta para composição; média para técnica e papel da figura. |
| P09 / F | 29,133–37,033 | Personagens menores entre barracas/toldos, um objeto claro e figura adulta; movimento lateral perceptível entre amostras. | Ampliar consequência para o coletivo; ambiente 3D ou multiplanos. | `plano-09`, 33,083; pares 34,533/34,667 mantêm cenário; ASR 29,06–36,42. | Alta para permanência do plano; média para deslocamento e interpretação. |
| P10 / F | 37,033–46,033 | Vila agora escura/alaranjada, formas triangulares luminosas de fogo; figura pequena em primeiro plano. | Contraste visual de escalada/colapso; fogo estilizado provavelmente animado/composito. | `plano-10`, 41,533; contato 37–45; ASR 37,22–45,46. | Alta para cor/formas; média para escalada e técnica, som de fogo não verificado. |
| P11 / F | 46,033–52,467 | Close de figura com óculos/expressão tensa sob luz laranja, depois imagem escurece. | Interpelação/virada argumentativa; fade faz ponte para outra metáfora. | `plano-11`, 49,250; contato 46–52; ASR 46,24–51,92. | Alta para close/escurecimento; média para função, identidade exata incerta. |
| P12 / G | 52,467–62,467 | Longa tira clara com linhas de texto estende-se em degraus/piso; afastamento revela escala e figura pequena. | Recibo/dívida como metáfora; câmera virtual em cena 3D é compatível com perspectiva. | `plano-12`, 57,467; contato 53–62; ASR 52,64–61,86. | Alta para escala/objeto; média para câmera 3D e metáfora, texto fino não transcrito. |
| P13 / H | 62,467–71,200 | Escadaria de pedra e colunas, luz branca intensa, perspectiva muda; clarões não são novos cenários. | Movimento de aproximação e luz como resolução simbólica; pode combinar 3D, vídeo sintético e pós. | `plano-13`, 66,833; pares 65,667–68,000; ASR 62,60–70,68. | Alta para escadaria; média para progressão; baixa para ferramenta e como foi gerada. |
| P14 / F | 71,200–80,333 | Retorno à vila clara com duas figuras próximas, uma ao lado/atrás da outra; pequena referência bíblica composta perto do fim. | Recompensa/resolução de tema cristão; anotação não equivale a validação teológica. | `plano-14`, 75,767; contato 71–80 e par 80,266; ASR 71,42–79,80. | Alta para retorno/cor; média para relação entre figuras; leitura fina da citação não auditada. |
| P15 / A | 80,333–87,733 | Retorno à apresentadora/mesa/janela, olhos fechados em parte das amostras e mãos juntas; legendas de encerramento. | Retomar intimidade inicial e convidar a uma prática/serviço posterior, não cliffhanger da história. | `plano-15`, 84,033; contato 80–87; ASR 80,48–87,14. | Alta para retorno; média para CTA; ASR diverge de legenda numa palavra do fecho, sem escuta para resolver. |

## Síntese editorial

- **Formato:** explicador devocional por analogia encenada, com apresentadora cartoon, narração e cenários simbólicos de profundidade. Não é apenas reencenação de passagem, selfie/vlog bíblico ou novela recorrente; por isso a receita própria de explicação por analogia.
- **Gancho dos primeiros 3 s:** apresentadora já visível, telefone e legenda contextualizando uma pergunta anterior. Gancho de conversa/curiosidade, não demonstração forte nem pergunta completa no quadro 0. A pergunta central só fica explícita depois, no inserto/trecho luminoso (~5–11 s). Isso é descrição, não medição de retenção.
- **Estrutura/batidas:** 0–≈11 s contexto e pergunta → ≈11–19 s hipótese de mundo sem punição → 19–46 s consequências individuais/coletivas e escalada → 46–62 s juízo e metáfora de dívida → 62–80 s resolução cristã → 80–87,7 s retorno e convite final. Significado extraído de legendas e ASR, não escuta, e sem endossar/validar interpretação teológica.
- **Estilo visual:** figuras simples com contornos escuros e olhos grandes, poses/expressões variáveis; fundos com pedra/madeira, profundidade de campo, partículas/luz volumétrica e contraste âmbar/branco. O aparente híbrido 2D/3D é compatível com mais de um processo.
- **Tipografia/legendas:** sem serifa pesada, contorno/sombra escura, grupos pequenos e centralizados na região inferior, amarelo/branco alternando/realçando palavras; não identificar família exata sem metadados. Interface do telefone e texto miúdo do recibo são diferentes das legendas e não foram integralmente transcritos.
- **Câmera/transições:** cortes entre grupos, aproximações e deslocamentos de perspectiva ao longo das amostras, alternância de geral/close, clarões/fades e retorno ao cenário inicial. A amostragem não certifica curvas de câmera, interpolação ou todo movimento corporal. Não confundir cada mudança de brilho com corte.
- **Ritmo:** 15 planos editoriais, ≈5,85 s em média; alguns longos avançam por câmera/luz/legenda. A cadência não é a de cortes obrigatórios a cada 1,5 s. Não há analytics para afirmar eficácia.

## Som — somente o medido/transcrito

FFmpeg `loudnorm` em saída nula mediu **entrada**, sem normalizar/substituir o arquivo: **−20,43 LUFS integrados**, **−3,52 dBTP**, **LRA 6,10 LU**. Os valores `output_*` do filtro não são o volume do original e não são reportados como tal.

Outra passagem no áudio **original**, com `silencedetect=noise=-35dB:d=0.3`, não detectou intervalos abaixo de −35 dB por pelo menos 0,3 s. Isso não significa fala sem pausas: ruído, ambiente ou trilha podem manter o nível. Não identifica a origem do som.

- **Voz/fala:** ASR encontrou narração pt-BR com progressão coerente com legendas. Confiança média; gênero/timbre, atuação, naturalidade, voz humana versus TTS e lip-sync **não verificados por escuta**. Há erro provável no fecho; não corrigir como se tivesse ouvido.
- **Música:** presença/ausência, instrumento, estilo, volume relativo e licença **não verificados**. Não inferir trilha do loudness contínuo.
- **Ambiente/efeitos:** presença/ausência e sincronismo **não verificados**; fogo visual não prova som de fogo. O canal AAC estéreo não demonstra espacialização artística.

## O que provavelmente foi usado — inferências explícitas

| Hipótese | Confiança | Motivo / o que falta |
|---|---|---|
| Composição/edição digital com legendas e montagem de planos | Alta | Inserto, close/geral, texto sobreposto e retornos são diretamente visíveis; programa/editor exato não identificado. |
| Personagens como recortes/rigs 2D ou billboards em cenários 3D/2.5D | Média–alta | Contornos/poses relativamente planos contrastam com perspectiva e profundidade dos fundos; um render inteiramente 3D estilizado ou vídeo gerado também pode imitar isso. |
| Cenários/objetos com câmera 3D e efeitos de luz em pós | Média | Escadaria, recibo e vila mudam em perspectiva nas amostras; não há arquivos-fonte para confirmar engine. |
| Participação de geração por IA em imagens, vídeo ou assistência à produção | Média | Híbrido visual e acabamento são compatíveis, mas não constituem detector; também é possível produzir por código/modelagem/composição convencional. Não há proveniência de geração. |
| Gerador de vídeo externo específico, TTS específico ou editor específico | Baixa / não atribuível | Nenhuma evidência de ferramenta específica foi identificada nas amostras/metadados. Sem logo/declaração/arquivo-fonte, não nomear produto como fato. |

O conhecimento posterior do [post de Theo](https://x.com/theoardley/status/2116684286837330374) oferece uma **rota possível**, não prova causal da produção desta referência. A receita ensina construir uma peça nova no stack ou receber clipes externos; não promete clone técnico, não reutiliza a mídia e não substitui revisão teológica/audiovisual humana.
