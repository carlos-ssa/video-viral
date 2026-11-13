# Criaturas em vlog — cotidiano absurdo

[Índice](../virais-ia.md) · [Procedimento executável A/B](producao.md)

## Quando usar e retenção

Humor de personalidade para uma criatura original: o extraordinário trata um problema banal com seriedade. A tentativa deve piorar ou transformar o problema; aparência engraçada sozinha não sustenta a série.

## Requisitos e limite local

- **Obrigatório:** personalidade em performance, criatura estável, tentativa e reversão visíveis; ambiente e contato do vaso/tecido sincronizados. Se o alvo for vlog realista, textura e gesto precisam sustentar essa linguagem.
- **Local possível:** rig/recortes próprios com inclinação, olhar e sombra; voz off assumida. Animação 2D acabada pode cumprir uma direção cartoon aceita, mas uma pose com zoom não é performance de vlog.
- **PARE:** sem gerador de imagem/vídeo, clipes autorizados ou rig próprio com atuação suficiente, avise que o resultado será **animatic**, não o vlog viral pedido. Só siga com esse escopo aceito; não venda “musgo realista” a partir de formas vetoriais.

Aplique as [regras comuns de composição](../../composition.md#regras-de-acabamento-obrigatórias).

## Roteiro preenchível — alvo 24 s

Ganchos (acrescentar dois candidatos para o portão):

1. “Sou [criatura], e [tarefa banal] acabou de dar errado.”
2. “Me disseram que [tarefa] era simples. Olha isso.”
3. “Tenho [habilidade absurda], mas não consigo [pequena tarefa].”

| Plano / alvo | Molde | Exemplo original pt-BR |
|---|---|---|
| p01 / 0–3 | [problema à vista] | “Sou um musgo ambulante. Meu primeiro aluguel veio sem sol.” |
| p02 / 3–8 | [tentativa coerente com personalidade] | “Arrastei o vaso para perto da janela.” |
| p03 / 8–15 | [custo/reversão visual] | “Só esqueci que eu também faço sombra.” |
| p04 / 15–21 | [solução imperfeita] | “Agora revezo: cinco minutos de janela, cinco de corredor.” |
| p05 / 21–24 | [escolha concreta seguinte] | “Amanhã: cortina ou espelho?” |

Os tempos são alvos; mostrar o vaso já fora da luz no quadro inicial evita introdução lenta. Falas são da criatura criada para este piloto, não imitação de vlog/personagem conhecido.

## Ficha de consistência

“Tufo”: criatura baixa em forma de almofada de musgo, dois olhos de âmbar, dois pés curtos, sem mãos, cachecol ferrugem; vaso azul fosco é prop recorrente. Voz autorizada pt-BR curiosa e econômica, mesma voz/velocidade em todos os episódios; bordão “Devagar, que eu broto”. Paleta musgo/ferrugem/creme, apartamento simples sem marcas. Médio 32 mm fixo, janela sempre à direita, reflexos não criam personagem extra.

Salvar referência frontal/perfil, medidas e recorte/rig aprovados. Reutilizar silhueta/cachecol/olhos; seed 107 nos workflows ajuda repetibilidade, não substitui comparação visual. Manter um registro de decisões (já descobriu a sombra, então o próximo episódio não pode esquecer isso).

## Rota A — recorte/rig + cenários

1. Criar `storytelling`, 24 s; preencher ficha, cinco ganchos, cenas e tool_plan; executar `plan.py` como no procedimento comum.
2. Para cada plano da tabela abaixo, prompt de imagem = sujeito/ação/lente da linha + luz suave da janela à direita + estilo “recorte ilustrado de feltro/musgo, fundo doméstico fosco” + paleta fixa + negativos “mãos, dedos, olhos extras, letras, logos, cachecol diferente” + seed 107 no grafo real.

| Plano | Sujeito e ação da imagem | Lente/enquadramento | Movimento A |
|---|---|---|---|
| p01 | Tufo observa vaso azul em sombra | 32 mm, médio frontal | inclinar rig 4° e sustentar |
| p02 | vaso próximo da janela, Tufo atrás | 35 mm, conjunto | transladar vaso por caminho curto, sem simular mão |
| p03 | sombra de Tufo cobre o vaso | 50 mm, detalhe de sombra/vaso | máscara de sombra avança |
| p04 | Tufo no corredor, vaso iluminado | 32 mm, geral | recorte atravessa lateralmente, escala constante |
| p05 | Tufo olha para cortina e espelho neutro | 32 mm, médio igual a p01 | congelar para escolha legível |

3. Gerar/selecionar imagens com `comfy.py`; separar Tufo, vaso, sombra e fundo. Um rig simples em PixiJS adaptado a partir de `visual_scene.mjs --module pixi` ou camadas GSAP resolve inclinação/pés/olhos; construir a sombra como máscara, não pedir que uma imagem estática faça física. Recriar bundle e integrar conforme procedimento. Voz off ou boca inexistente evita fingir lip-sync.
4. Fragmento para completar:

```json
{"scenes":[{"id":"s01","narration":"Sou um musgo ambulante. Meu primeiro aluguel veio sem sol.","on_screen":"ALUGUEL SEM SOL","visual":{"engine":"hyperframes","brief":"Tufo e vaso azul em camadas próprias","shots":[{"cue":"Sou","frame":"médio","subject":"criatura e vaso na sombra","camera":"fixa, personagem inclina","in":"corte","emphasis":"vaso escuro","sfx":"pop"}],"transition_out":"corte"},"start":0,"duration":3}],"tool_plan":[{"module":"pixi","tool":"visual_scene.mjs + adaptação: rig Tufo → scenes/p01; inclinação e sombra","status":"planejado"},{"module":"hyperframes","tool":"HyperFrames: cenas e GSAP → render/master.mp4; montagem do vlog","status":"planejado"}]}
```

5. Medir `voice.py`/WAVs, revisar palavras/tempos em `captions.py`, compor todos os planos em HyperFrames + GSAP e passar entrega/revisão. Incluir `pixi` no stack somente se a adaptação for realmente usada; GSAP sozinho pode bastar.

## Rota B — clipes externos

1. Lista p01–p05 com alvos 3/5/7/6/3 s; anexar referência autorizada de Tufo, vaso e planta do apartamento. Solicitar uma ação por tomada, sem montagem automática dentro do prompt.
2. Prompt por linha = sujeito/ação da tabela + câmera/lente + duração-alvo + “mesma silhueta, olhos âmbar e cachecol ferrugem da referência; janela à direita; estilo fosco, luz suave, sem texto”. Movimentos: p01 inclinação curta, p02 vaso desliza lentamente (sem mãos), p03 sombra atravessa vaso, p04 Tufo caminha de perfil, p05 olha uma vez para cada opção.
3. Diálogo/áudio: pedir “sem diálogo; ambiente de apartamento se disponível”, depois montar o relato original. Se pedir voz integrada, usar a fala exata daquele plano e verificar sincronia/voz; descartar se não mantiver identidade vocal. Não supor suporte a áudio separado.
4. Nomear `ep001_p03_t01.mp4` etc.; documentar seleção por volume do corpo, ausência de membros novos, janela e cachecol. Registrar em assets origem/licença/IA, referências e voz autorizada. Copiar selecionados em `composition/assets/`; importador `footage.py` é para fonte-base única, não coleção de tomadas.
5. Montar os intervalos úteis em HyperFrames, retemporizar voz/legenda, sonorizar e executar os mesmos `deliver.py`/`review.py`. Não adicionar o serviço ao catálogo de módulos.

## Som e legenda

Ambiente doméstico discreto licenciado/gravado; contato do vaso com piso e tecido do cachecol como Foley separado. Spec proposta `duration:24`, `seed:107`, `events`:

```json
[{"type":"pop","at":0.3,"duration":0.15,"gainDb":-25},{"type":"whoosh","at":8.2,"duration":0.3,"gainDb":-29},{"type":"pop","at":21.2,"duration":0.15,"gainDb":-26}]
```

Sem sala/vaso/tecido autorizados, aplique a [reserva ambiente/Foley](../../modules.md#reserva-de-ambiente-e-foley-sintetizados) com **D=24 s**, **seed=107**, preset sob fala e `pop` no assentamento do vaso. Ajuste D/contatos ao render medido, registre `kind:"sfx"` e identifique a textura sintética: Tone.js não produz “musgo real”. Legendas por sentido na faixa exclusiva, sem cobrir vaso/sombra; texto de escolha separado da transcrição. Evite efeitos que mascarem a reversão verbal.

## Checklist específico

- [ ] Problema do vaso no primeiro quadro, tentativa e reversão compreensíveis sem fala.
- [ ] Olhos/cachecol/volume constantes; não surgem mãos/dedos; textos compostos, não deformados na geração.
- [ ] Fala off explícita ou lipsync conferido; ambiente doméstico presente, escuta humana ou pendência.
- [ ] Personagem próprio, sem IP de terceiros, voz/rosto real imitados ou locação identificável sem permissão.
- [ ] Rótulo de IA quando aplicável, direitos comerciais reais, sem prometer monetização; novo problema por episódio. Aplicar checklist comum; se houver tema religioso, acrescentar fonte/respeito/revisão teológica.
