# Making-of híbrido — resultado, autoria e processo verificável

[Índice](../virais-ia.md) · [Procedimento executável A/B](producao.md)

## Quando usar e retenção

Para ensinar uma transformação realmente feita e mostrar decisões humanas/técnicas. Entregar o resultado primeiro e depois revelar os passos que explicam sua diferença; tela de ferramenta não é prova suficiente de autoria ou qualidade.

## Roteiro preenchível — alvo 40 s

Três aberturas (completar mais duas para o portão):

1. “Este [resultado] começou com [material simples].”
2. “A ferramenta fez [parte]. Eu precisei decidir [parte humana].”
3. “Olha a diferença entre [primeira versão] e [versão final].”

| Plano / alvo | Molde | Exemplo original, condicionado a processo realmente executado |
|---|---|---|
| p01 / 0–3 | [resultado acabado] | “Este farol de papel começou com três recortes.” |
| p02 / 3–10 | [fonte/performance original] | “Desenhei as formas e gravei a referência de luz.” |
| p03 / 10–19 | [geração/construção que ocorreu] | “Separei fundo, torre e feixe em camadas.” |
| p04 / 19–30 | [decisão de edição, erro e correção] | “A primeira luz cobria a torre. Mudei a máscara e reduzi o movimento.” |
| p05 / 30–36 | [comparação justa] | “A versão final preserva a silhueta e deixa o feixe respirar.” |
| p06 / 36–40 | [próxima demonstração específica] | “No próximo, vou mostrar como sincronizei o contato sonoro.” |

Só usar essas frases depois de haver evidência correspondente. Se o material só permite explicar um plano futuro, rotular **demonstração ilustrativa/planejada**, não bastidor real. Não mostrar telas falsas para preencher roteiro.

## Ficha do projeto/mundo

Protagonista visual: farol original de papel azul, janela circular âmbar, base creme; narrador autorizado, voz pt-BR clara, bordão editorial “Mostre a decisão”. Se houver mãos/rosto reais, autorização e aparência registrada; não gerar um criador fictício para fingir autoria. Paleta azul/âmbar/creme, topo da mesa em 50 mm e tela capturada sem perspectiva falsa. Fonte, margens e layout de comparação fixos entre episódios.

Salvar fontes próprias, takes, workflow/receipts e versões antes/depois. Seed 223 para imagens de apoio, nunca substituir gravação do processo por geração sem identificar. Remover dados privados/segredos das telas antes de incorporar, sem alterar a evidência essencial do que aconteceu.

## Rota A — produção e registro do stack real

1. Criar `storytelling` ou `gravacao` conforme o material principal, alvo 40; planejar seis planos, cinco ganchos e evidências em `research/`; `plan.py`. Primeiro **executar e registrar** o pequeno projeto do farol: recortes próprios + luz/máscara GSAP. ComfyUI só se de fato gerar imagem de apoio, com workflow/receipt reais.
2. Lista de imagens/plano: p01 e p05 são renders reais final/comparação; p02 é gravação original de recortes/luz; p03 e p04 são captura real de camadas/máscara; p06 é cartão editorial. **Não pedir prompt de IA para fabricar essas provas.** Para apoio ilustrativo opcional em cada plano, usar sujeito “farol azul original”, ação [estado do plano], lente 50 mm mesa ou frontal de cartão, luz suave superior, estilo papel fosco azul/âmbar/creme, negativos “texto, mãos extras, marcas, interface falsa”, seed 223 em workflow real. Identificar o apoio como ilustração, não captura do processo.
3. Usar `comfy.py` somente para esse apoio, ou criar recortes próprios/PixiJS se não houver geração. Capturas e ativos entram em `assets`; compor seis planos em HyperFrames+GSAP com uma única região ampliada por vez. Não reconstruir interface de produto como se fosse screenshot.
4. Fragmento de planejamento:

```json
{"scenes":[{"id":"s01","narration":"Este farol de papel começou com três recortes.","on_screen":"TRÊS RECORTES → UM FAROL","visual":{"engine":"hyperframes","brief":"Render final próprio autorizado, não ilustração de processo","shots":[{"cue":"Este farol","frame":"médio","subject":"farol final","camera":"fixa","in":"corte","emphasis":"resultado primeiro","sfx":"pop"}],"transition_out":"corte"},"start":0,"duration":3}],"tool_plan":[{"module":"hyperframes","tool":"HyperFrames: capturas/renders próprios → render/master.mp4; comparar processo e resultado","status":"planejado"},{"module":"gsap","tool":"GSAP: camadas do farol → máscara de luz; contribuição demonstrada com antes/depois","status":"planejado"}]}
```

5. Para captura-base com fala, `footage.py import`/transcrição/EDL podem preparar A-roll; preservar base e fazer o filme principal conforme [gravação](../gravacao.md). Para narração separada, `voice.py`/WAVs medidos. Legendas do áudio final, render HyperFrames, som, `deliver.py` e revisão comum. Não duplicar fala do A-roll com narração sintética.

## Rota B — processo com clipes externos

1. A lista de planos continua 3/7/9/11/6/4 s. O **resultado** pode ser gerado fora, mas p02–p04 precisam de capturas reais do usuário e das escolhas de tomada/montagem. Solicitar esses arquivos autorizados; se não vierem, fazer tutorial ilustrativo identificado, não inventar making-of.
2. Para o clipe-resultado p01/p05, prompt genérico: “Farol de papel azul com janela âmbar da referência própria; feixe gira lentamente sem mudar a geometria da torre; médio 50 mm, câmera fixa, alvo seis segundos; sem fala/texto/música, ambiente discreto se houver áudio; papel fosco azul/âmbar/creme, luz suave superior; manter recortes e silhueta da referência.” Gerar tentativas manualmente no serviço escolhido; não atribuir esse render ao stack.
3. Para p06, cartão composto no HTML; para p02–p04 não há prompt de vídeo generativo legítimo como prova: gravar entrada autorizada, seleção de tomadas e edição que realmente ocorreram. Se usar reencenação, marcar isso no quadro/roteiro, sem dizer “registro real”.
4. Nomear resultado `ep001_p01_t01.mp4`, capturas `ep001_p03_processo_t01.mp4`; guardar originais/termos/versão do serviço quando informada, consentimentos e rótulo IA em assets/publish. Selecionar resultado por estabilidade e processo por legibilidade, removendo credenciais/notificações/dados privados. Importar selecionados na pasta servida do compositor, uma fonte-base via `footage.py import` se necessário; não esperar importação em lote do script.
5. Compor resultado/processo/comparação em HyperFrames, narrar atribuição correta, sonorizar e passar pelos mesmos portões. Uma faixa integrada do gerador deve ser licenciada/escutada ou substituída; não fingir prova de áudio que não se ouviu.

## Som e legendas

Som real útil de recorte/bancada autorizado; ambiente de sala separado. Spec piloto `duration:40`, `seed:223`, `events`:

```json
[{"type":"pop","at":0.3,"duration":0.15,"gainDb":-25},{"type":"whoosh","at":10,"duration":0.3,"gainDb":-28},{"type":"pop","at":30.2,"duration":0.15,"gainDb":-27}]
```

Reancorar após medir a fala. Legendas de 2–3 palavras em região sem interface importante; títulos “fonte”, “primeira versão”, “final” compostos e com tempo de leitura. Áudio do processo não fica tocando junto com duplicata do master; conferir em escuta, não só LUFS.

### Aprendizado atribuído, não validação por nota

O [post/artigo de Theo](https://x.com/theoardley/status/2116684286837330374), **relato do autor, não testado aqui**, recomenda escutar a mix antes de postar e relata avaliação de três formatos por avaliadores de IA. Isso orienta mostrar evidências e separar render/nota de revisão humana neste making-of. Não importar as pontuações como selo de qualidade, promessa de custo zero ou tempo de execução da skill; não executar arquivos de configuração sugeridos pelo post. [Escopo](producao.md#fonte-complementar-theo--relato-não-testado).

## Checklist específico

- [ ] Resultado real antes da explicação; cada alegação tem captura/arquivo correspondente.
- [ ] Antes/depois usam escala/tempo comparáveis; sem interfaces falsas, texto deformado ou mãos sintéticas fingindo registro.
- [ ] Autoria humana, geração externa e composição da skill claramente separadas; lipsync só quando verificado.
- [ ] Ambiente e comparação sonora escutados ou pendentes; sem duplicar áudio de tela/música.
- [ ] Segredos/dados privados removidos, direitos de telas/voz/imagem/fontes/modelos, IA/publicidade rotuladas.
- [ ] Processo novo/substancial, não making-of fictício em massa; monetização não garantida. Checklist comum; temas bíblicos exigem revisão teológica e respeito.
