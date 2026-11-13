# Explicação por analogia encenada — cartoon em mundo simbólico

[Índice](../virais-ia.md) · [Procedimento executável A/B](producao.md) · [Ficha da referência](exemplo-planos.md)

## Quando usar e retenção

Para explicar uma pergunta abstrata por um pequeno mundo com regras visíveis: pergunta → hipótese → consequência → limite/reformulação → resposta → convite. A referência local usa tema de fé; esta receita nova usa **uma oficina ficcional**, sem copiar pessoas, personagens, argumentos ou falas do vídeo.

## Requisitos e limite local

- **Obrigatório:** pergunta única, regra visível, teste de condição e resposta encenada; contagem/fluxo de caixas precisam mudar de verdade.
- **Local possível:** construir oficina/carrinhos/porta por geometria e rig próprios, com estado determinístico. Uma direção cartoon 2D/2.5D aceita pode cumprir a explicação sem gerador de imagem/vídeo.
- **PARE:** se só houver cartões estáticos, ou se o pedido exigir realismo/performance indisponíveis sem gerador ou ativos equivalentes, avise que a alternativa será **animatic**, não o formato viral encenado. Só siga com esse escopo aceito; não substitua mecanismo visual por títulos sucessivos.

Aplique as [regras comuns de composição](../../composition.md#regras-de-acabamento-obrigatórias), inclusive coerência e entonação do gancho.

## Roteiro preenchível — alvo 42 s

Ganchos (criar outros dois audiovisuais para o portão):

1. “Por que mais [recurso] não resolveu [problema visível]?”
2. “Parece que basta [solução intuitiva]. Vamos testar neste mundo.”
3. “Se [regra simples], o que acontece com [consequência]?”

| Plano / alvo | Molde | Exemplo original pt-BR: a oficina das caixas |
|---|---|---|
| p01 / 0–3 | apresentador e pergunta já explícita | “Mais carrinhos. Por que a fila não anda?” |
| p02 / 3–10 | definir uma regra da analogia | “Nesta oficina imaginária, a saída libera uma caixa por vez.” |
| p03 / 10–19 | testar solução intuitiva | “Chegam dois carrinhos novos. Agora trazemos mais caixas, mas a porta continua igual.” |
| p04 / 19–28 | consequência e ponto limitante | “A fila cresce antes da saída. Aumentamos a chegada, não a passagem.” |
| p05 / 28–37 | mudar a condição e mostrar resposta | “Ao mudar a etapa mais lenta, a fila diminui. Aqui, o problema não era falta de carrinho.” |
| p06 / 37–42 | limite da analogia + próxima pergunta | “É um modelo simples, não toda fábrica. No próximo: quando a solução muda o problema de lugar?” |

Não usar a analogia como prova universal: declarar suas regras, limites e fonte quando a aplicação real exigir conhecimento técnico. Abertura antecipa a pergunta nos 3 s, ao contrário da referência analisada, que contextualiza antes de expô-la integralmente.

## Ficha de apresentador/mundo

Apresentador original “Nilo”: figura 2D geométrica, cabeça arredondada pequena, olhos em pontos, jaqueta azul-petróleo e prancheta bege; não copiar olhos/roupa/silhueta da referência. Voz autorizada pt-BR clara, mesma seleção e velocidade; bordão editorial “Vamos mudar uma condição”. Paleta petróleo/areia/coral, mundo de blocos foscos sem marcas. Apresentador médio em 45 mm equivalente; geral de oficina 35 mm; porta sempre à direita, fluxo esquerda→direita, uma caixa coral como referência de escala.

Guardar rig/modelo/recortes e mapa da oficina; posição/cor da porta e estado da fila por plano. Seed 257 nos workflows para fundos, não como garantia de personagem. Reutilizar o rig e a voz, atualizar o estado da fila por tempo; não regenerar toda a cena de forma incompatível.

## Rota A — recortes 2D + cenário 3D/2.5D do stack

1. Criar `narrado` ou `storytelling`, alvo 42; cinco candidatos, ficha, roteiro de seis planos, direção e tool_plan; `plan.py`. Fazer quadro inicial, fila e payoff antes de produzir tudo.
2. Prompt de imagem por plano = sujeito/ação/lente da linha + luz suave superior à esquerda + estilo “figura 2D geométrica em cenário de blocos 3D foscos” + paleta petróleo/areia/coral + negativos “mãos extras, escrita/logos, rosto detalhado, porta/roupa divergentes” + seed 257 no workflow real. Para fila/caixas exatas, preferir geometria/camadas próprias, não contar objetos por geração de imagem.

| Plano | Sujeito/ação para imagem | Lente/enquadramento | Movimento A |
|---|---|---|---|
| p01 | Nilo ao lado de fila parada, porta à direita | 45 mm, médio | gesto do rig + avanço curto |
| p02 | oficina com uma abertura e caixa coral | 35 mm, geral | travelling suave/paralaxe em profundidade |
| p03 | dois carrinhos novos entram pela esquerda | 35 mm, mesmo geral | caminhos GSAP ou posições 3D pelo tempo |
| p04 | fila acumulada antes da porta | 50 mm, detalhe amplo | elevar câmera virtual para revelar acúmulo |
| p05 | passagem alterada e fila menor | 35 mm, mesmo eixo | corte entre condições explicitamente rotuladas |
| p06 | Nilo no cenário inicial com quadro de limite | 45 mm, médio | sustentar e encerrar, sem fade longo |

3. Usar `comfy.py` para fundos/estilo se disponível; para movimento espacial real, construir caixas/carrinhos/porta em Three.js/Blender e usar personagem billboard/recorte. Alternativa 2.5D: camadas com perspectiva fixa, sem órbita que exponha costas planas. PixiJS adaptado pode animar pose/olhar; estado calculado por `t`, não relógio real. HyperFrames+GSAP monta os planos e os cartões.
4. Fragmento a completar:

```json
{"scenes":[{"id":"s01","narration":"Mais carrinhos. Por que a fila não anda?","on_screen":"Mais carrinhos. Por que a fila não anda?","visual":{"engine":"hyperframes","brief":"Apresentador geométrico próprio e oficina; sem reutilizar referência","shots":[{"cue":"Mais carrinhos","frame":"médio","subject":"Nilo e fila parada","camera":"avanço curto","in":"corte","emphasis":"porta única à direita","sfx":"pop"}],"transition_out":"corte"},"start":0,"duration":3}],"tool_plan":[{"module":"three","tool":"Three.js: geometria própria de oficina → cena determinística; fluxo de caixas","status":"planejado"},{"module":"gsap","tool":"GSAP: recorte Nilo e cartões → timeline HyperFrames; entradas por palavra medida","status":"planejado"}]}
```

5. Gerar/montar voz (`voice.py` ou WAVs), medir, conferir `captions/words.json` e ancorar os cartões “chegada”, “passagem” e “limite do modelo” às palavras respectivas. Sem boca detalhada, relato off/atuação de rig; não fingir lip-sync fotorrealista. Renderizar composição principal, som e os portões comuns.

## Rota B — clipes externos + cartões compostos

1. Lista p01–p06 de 3/7/9/9/9/5 s, dividida em subplanos se o produto não sustentar ações/tempo. Usar referências próprias de Nilo/oficina; não anexar quadros do vídeo estudado sem direitos.
2. Prompt por plano = identidade/ação da tabela + câmera/lente + duração + diálogo/áudio desejado + estilo/luz/paleta + estado da fila e referência autorizada. Preferir gerar cenário/movimento **sem textos e sem diálogo** e compor apresentador/voz/cartões na skill; assim a contagem de caixas e a explicação ficam auditáveis.
3. Exemplo p03: “Oficina de blocos foscos da referência própria, porta única à direita e fila já presente; dois carrinhos entram da esquerda e param antes da fila, sem atravessar caixas; geral 35 mm fixo, alvo nove segundos, sem fala/música/texto, rodas suaves se houver áudio; petróleo/areia/coral e luz superior esquerda; preservar dimensões e estado inicial da referência.” Para p04 pedir só revelação do acúmulo; para p05 uma nova condição claramente separada, não uma porta que derrete durante a explicação.
4. Se quiser Nilo falante externo, fornecer apenas a fala original do plano e testar voz/lipsync; se falhar, voltar à figura 2D/voz off. Não prometer que referência/diálogo/duração serão aceitos por qualquer serviço.
5. Nomear `ep001_p03_t01.mp4` e equivalentes, registrar origem/licença/rótulo/consentimentos, escolher por continuidade de fila/porta/roupa, não só beleza. Copiar selecionados para `composition/assets/`; `footage.py import` para fonte-base única se necessário. Montar HyperFrames, cartões/legendas finais, mix e os mesmos `deliver.py`/`review.py`; gerador permanece fora do stack.

## Som e tipografia

Ambiente de oficina ficcional discreto e rodas/caixas em Foley próprio/licenciado; sinais marcam mudança de condição, não cada palavra. Spec proposta `duration:42`, `seed:257`, `events`:

```json
[{"type":"pop","at":0.3,"duration":0.15,"gainDb":-25},{"type":"whoosh","at":10.2,"duration":0.35,"gainDb":-29},{"type":"pulse","at":19.2,"duration":0.6,"gainDb":-30},{"type":"pop","at":28.2,"duration":0.15,"gainDb":-26}]
```

Sem oficina/rodas/caixas autorizadas, aplique a [reserva ambiente/Foley](../../modules.md#reserva-de-ambiente-e-foley-sintetizados) com **D=42 s**, **seed=257**, preset sob fala e contatos na parada dos carrinhos. Reancore aos tempos reais, identifique textura sintética e registre `kind:"sfx"`. Segmente legendas por sentido, com fonte licenciada; cartões maiores, um conceito por vez, sem encobrir porta/personagem. Realce no HTML/ASS, não campo inventado. Use a mesma pergunta **“Mais carrinhos. Por que a fila não anda?”** na abertura falada, no título e na legenda correspondente; confira a entonação em escuta ou registre pendência.

### O que vem do relato de Theo

[Theo](https://x.com/theoardley/status/2116684286837330374) descreve no artigo anexo: bonecos 2D em cenários 3D com luz/sombra; explicador com apresentador e cartões que entram na palavra falada; cena 3D de “e se?”; necessidade de ouvir a mix antes de postar. **Relato do autor, não testado aqui.** Na A, traduzimos isso em rig/cenário do stack e cartões ancorados à voz medida. Na B, preservamos a mesma estrutura como briefing/seleção e montamos cartões fora da geração. Nenhuma dessas semelhanças prova a origem do vídeo local; não afirmar que ele usou o projeto ou ferramenta do autor. Não importar bibliotecas/prompts/configurações; [escopo da leitura](producao.md#fonte-complementar-theo--relato-não-testado).

## Checklist específico

- [ ] Pergunta nos primeiros 3 s e resposta visual no payoff; analogia tem regras/limites declarados.
- [ ] Contagem/estado da fila e eixo permanecem coerentes; mãos/textos sem deformação, personagem/voz consistentes.
- [ ] Cartões entram na palavra certa, legenda não compete com diagrama; off ou lipsync realmente conferido.
- [ ] Ambiente e contatos presentes, sem duplicar voz; revisão humana integral ou pendência explícita.
- [ ] Não copiar vídeo, pessoas, identidade visual/IP ou argumentos de terceiros; licenças e voz/imagem autorizadas, IA rotulada quando aplicável.
- [ ] Se tratar de fé, não reduzir doutrina a uma analogia não revisada: identificar passagem, separar interpretação/citação, tom respeitoso e revisão teológica humana.
- [ ] Explicação substancial por episódio, não variações vazias; monetização não garantida. Aplicar também o checklist comum.
