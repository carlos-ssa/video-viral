# Bíblia cinematográfica narrada

[Índice](../virais-ia.md) · [Procedimento executável A/B](producao.md)

## Quando usar e retenção

Para uma passagem cuja escala/conflito precise de contexto visual, sem depender de diálogo labial. Contrastar ameaça, decisão e consequência; a imagem oferece progressão, a narração mantém a precisão da adaptação.

## Requisitos e limite local

- **Obrigatório:** escala da ameaça, reação humana e mudança visível de estado; barco/água/luz coerentes, narração fiel e ambiente aquático. Realismo pedido exige ativos e movimento compatíveis, não bonecos-palito.
- **Local possível:** imagens fornecidas/aprovadas com câmera limitada ou cena Three.js/Blender realmente construída. Sem gerador e sem modelos/cenas prontos, recortes 2D servem para storyboard; não prometem tempestade física ou cinematografia realista.
- **PARE:** se faltar imagem/vídeo capaz de sustentar o realismo e não houver 3D próprio equivalente, avise que a composição vetorial será **animatic**, não o formato viral cinematográfico. Só siga nessa alternativa com escopo aceito.

Aplique as [regras comuns de composição](../../composition.md#regras-de-acabamento-obrigatórias); a referência bíblica fixa fica fora da faixa da legenda, não sob ela.

## Roteiro preenchível — alvo 36 s

Três aberturas para completar com mais duas no portão:

1. “O que [ameaça] revela quando [segurança] desaparece?”
2. “Tudo parecia [estado]. Até [mudança].”
3. “Antes de [desfecho], houve [conflito concreto].”

| Plano / alvo | Molde | Exemplo original pt-BR, paráfrase autoral |
|---|---|---|
| p01 / 0–3 | [ameaça já no quadro] | “O barco parecia pequeno demais para aquela noite.” |
| p02 / 3–9 | [fonte e situação] | “Em Marcos quatro, do trinta e cinco ao quarenta e um, a travessia encontra uma tempestade.” |
| p03 / 9–17 | [reação humana] | “Os discípulos sentem medo. A cena não esconde sua fragilidade.” |
| p04 / 17–25 | [mudança central fiel à passagem] | “Jesus intervém, e o vento e o mar se aquietam.” |
| p05 / 25–32 | [consequência sem invenção] | “A surpresa deles abre uma pergunta sobre quem está no barco.” |
| p06 / 32–36 | [convite honesto ao texto] | “Leia a passagem. Depois, vamos olhar a reação dos discípulos.” |

Texto curto original, não falas retiradas de viral nem citação de tradução específica. Identificar livro/capítulo/versículos, distinguir paráfrase e interpretação e revisar teologicamente antes da produção. O gancho seguinte só pode anunciar um episódio realmente planejado.

## Ficha de mundo e continuidade

Barco ilustrativo de madeira escura, uma vela bege recolhida, corda à esquerda, mar azul-petróleo; figurantes adultos anônimos com túnicas simples, sem copiar rostos/figurinos de filmes. Luz fria no conflito e prata suave na resolução; não mudar para pôr do sol sem passagem de tempo. Narrador autorizado, pt-BR contido, mesmo preset de voz/velocidade entre episódios; sem bordão de personagem canônico, assinatura editorial “Volte ao texto”. Geral equivalente 35 mm e detalhes 70 mm; manter direção do vento e eixo esquerda→direita.

Salvar referências aprovadas do barco, paleta e mapa de posições. Reutilizar modelo/camadas; seed 73 nos workflows, sem garantia automática de rosto. Conferir velas, cordas, número de pessoas e estado da água no corte.

## Rota A — imagens + câmera virtual/3D

1. Criar projeto `narrado`, alvo 36. Preencher roteiro, cinco candidatos, direção/fonte e tool_plan; passar `plan.py` antes de produzir.
2. Prompt por plano = linha abaixo + luz/paleta da ficha + estilo “ilustração cinematográfica de materiais foscos, sem alegação de reconstituição histórica” + negativos “mãos extras, letras, logos, cordas fundidas, barco duplicado” + seed 73 fixa no workflow API real.

| Plano | Sujeito/ação para imagem | Lente/enquadramento | Movimento A |
|---|---|---|---|
| p01 | barco inclinado numa onda, vela recolhida | 35 mm, geral baixo | aproximação 1,00→1,04 |
| p02 | mesma embarcação com margem distante | 35 mm, geral lateral | paralaxe água/barco/céu |
| p03 | duas figuras anônimas seguram borda, mãos simplificadas | 70 mm, médio | recorte estável, pequena inclinação do conjunto |
| p04 | barco nivelado e água agora calma | 35 mm, geral igual a p01 | corte entre estados, não morph de corpos |
| p05 | figuras em silhueta voltadas para o centro | 70 mm, conjunto | avanço lento sem revelar rostos novos |
| p06 | detalhe da corda e horizonte quieto | 70 mm, detalhe | desacelerar e sustentar para leitura |

3. Gerar imagens com `comfy.py`/nó real e selecionar. Ondas estáticas + paralaxe não são água simulada: quando a ação exigir balanço físico, construir barco/água em Three.js ou Blender e animar câmera/rotação pelo tempo conforme [3D](../../modules/3d.md). Não afirmar que demo PixiJS fornece tempestade pronta.
4. Fragmento de planejamento, para completar com os demais planos/módulos:

```json
{"scenes":[{"id":"s01","narration":"O barco parecia pequeno demais para aquela noite.","on_screen":"UMA TRAVESSIA, UMA PERGUNTA","visual":{"engine":"hyperframes","brief":"assets/p01.png; barco aprovado com vela recolhida","shots":[{"cue":"O barco","frame":"geral","subject":"barco contra onda","camera":"aproximação lenta","in":"corte","emphasis":"escala da onda","sfx":"pulse"}],"transition_out":"corte"},"start":0,"duration":3}],"tool_plan":[{"module":"comfyui","tool":"comfy.py: workflow p01 → assets/p01.png; quadro de ameaça","status":"planejado"},{"module":"hyperframes","tool":"HyperFrames: seis planos e GSAP → render/master.mp4; progressão narrativa","status":"planejado"}]}
```

5. Medir voz com `voice.py` (ou WAVs autorizados), ajustar a duração de cada cena, `captions.py transcribe/import` e `ass`. Compor o filme inteiro em HyperFrames+GSAP, aplicar som e os portões de entrega/revisão do procedimento comum. Não renderizar apenas uma sequência de fundos sem direção e chamá-la de cena generativa contínua.

## Rota B — clipes de vídeo externos

1. Lista p01–p06: alvos 3/6/8/8/7/4 s. Um prompt/arquivo por plano. Usar referência do **mesmo barco** e mapa dos figurantes em todas as tomadas.
2. Construir cada prompt com sujeito/ação da tabela, lente, luz/estilo fixos, duração, “sem diálogo e sem texto; ambiente de água/vento se disponível”. Movimento de vídeo: p01 balanço curto visto de câmera baixa; p02 travelling lateral suave; p03 câmera estável com reação única; p04 água se acalma sem teletransportar barco; p05 figuras viram para o centro; p06 corda parada com água suave. Não pedir seis eventos em um único clipe.
3. Prompt-modelo preenchido p04: “Mesmo barco de madeira escura e vela recolhida da referência própria; embarcação nivela enquanto as ondas diminuem; geral 35 mm no eixo aprovado, câmera avança lentamente; alvo oito segundos, sem diálogo, água e vento decrescentes se houver áudio; materiais foscos azul-petróleo/prata; preservar cordas, roupas e posições; sem letras ou logotipos.” Não é sintaxe garantida de um produto.
4. Nomear `ep001_p04_t01.mp4` e equivalentes; registrar origem/termos/IA/direitos de referências em assets. Selecionar por continuidade de água, corda e pessoas em toda duração. Descartar “água borracha”, membros duplicados ou rostos herdados de filmes. Importar selecionados em `composition/assets/`; fonte-base única, se necessária, via `footage.py import`, não importação em lote fictícia.
5. Montar e narrar em off, sem usar suposta voz de figura histórica. Mesmo HyperFrames, mix e `deliver.py`/`review.py`; gerador não integra o stack e licença pendente bloqueia entrega monetizada.

## Som e legendas

Água, vento e madeira precisam de gravação/ativos licenciados com perspectiva coerente; Tone.js fornece só sinais. Spec proposta: `duration:36`, `seed:73`, `events`:

```json
[{"type":"pulse","at":0.2,"duration":0.6,"gainDb":-27},{"type":"riser","at":15,"duration":1.5,"gainDb":-30},{"type":"pop","at":25.2,"duration":0.15,"gainDb":-32}]
```

Sem água/vento/madeira autorizados, aplique a [reserva ambiente/Foley](../../modules.md#reserva-de-ambiente-e-foley-sintetizados) com **D=36 s**, **seed=73**, preset sob fala e impacto no balanço do barco. Identifique-a como textura sintética; ela não reproduz tempestade real. Recalcule pelos tempos medidos e registre `kind:"sfx"`. Reduza ambiente sob nomes/passagem sem prometer ducking automático. Legenda só da narração, segmentada por sentido; componha **“Marcos 4:35–41”** como cartão legível separado, sem cobrir barco nem legenda; não ponha versículo inventado numa imagem gerada.

## Checklist específico

- [ ] Ameaça visível antes da contextualização; fecho responde à promessa sem “revelação secreta”.
- [ ] Barco/vela/pessoas/vento contínuos; mãos, cordas e textos sem deformação; off dispensa lip-sync, não o finge.
- [ ] Mudança de luz justificada; sem cortes que alterem o sentido da passagem.
- [ ] Ambiente aquático presente, fala inteligível, escuta humana ou pendência explícita.
- [ ] Fonte/passagem e adaptação identificadas; revisão teológica respeitosa; sem copiar traduções/filmes protegidos.
- [ ] Voz/imagem autorizadas, IA rotulada quando aplicável, termos comerciais comprovados e episódio autoral, sem repetição em massa. Checklist comum e portões mantidos.
