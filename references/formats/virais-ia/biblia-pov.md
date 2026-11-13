# Bíblia em POV/selfie — testemunha ficcional

[Índice](../virais-ia.md) · [Procedimento executável A/B](producao.md)

## Quando usar e retenção

Para aproximar uma passagem de quem acompanha relatos pessoais. Abrir já diante de uma decisão; a perspectiva cria proximidade, mas nunca transforma invenção de roteiro em fala bíblica literal.

## Roteiro preenchível — alvo 28 s

Escolha uma abertura; crie mais duas para os cinco candidatos do portão:

1. “Este [obstáculo] parecia maior que a nossa coragem.”
2. “Eu ia desistir de [tarefa]. Então [decisão concreta].”
3. “Como começar [missão] quando só vemos [problema]?”

| Plano / alvo | Batida preenchível | Exemplo original pt-BR, adaptação livre |
|---|---|---|
| p01 / 0–3 | selfie diante de [obstáculo] | “A rua estava em ruínas. Por onde começar?” |
| p02 / 3–9 | mostrar [contexto] e identificar passagem | “Esta cena imaginada acompanha uma moradora, inspirada em Neemias dois, dezessete e dezoito.” |
| p03 / 9–16 | [ação pequena] muda a disposição | “Em vez de esperar tudo ficar fácil, ela separa as primeiras pedras.” |
| p04 / 16–24 | [decisão coletiva] e consequência | “Outras mãos chegam. O trabalho deixa de ser de uma pessoa só.” |
| p05 / 24–28 | recompensa + próximo problema | “O começo aconteceu. No próximo: como continuar juntos?” |

Exemplo é narração autoral, **não citação nem registro histórico**. Não atribuir a personagem canônica uma fala inventada. Ajustar texto após medição; se não couber, cortar contexto redundante, não acelerar excessivamente. Identificar a passagem na publicação e submeter a interpretação à revisão teológica antes de gerar.

## Ficha de personagem/mundo

Testemunha ficcional adulta, rosto oval, cabelo castanho preso, túnica areia sem adornos modernos, faixa verde-oliva e cesta sem marca. Voz feminina autorizada, pt-BR calma (Kokoro `pf_dora` como opção, não imitação de pessoa). Bordão autoral: “Uma pedra de cada vez”; usar só quando acrescentar sentido. Paleta areia/oliva/âmbar. Selfie médio em equivalente 28 mm, rosto no terço superior, mão fora do quadro; contraplano sempre do mesmo lado da rua. Mundo ilustrativo, não reconstrução arqueológica certificada.

Manter ficha, pose frontal/perfil e roupa aprovadas; reaproveitar o mesmo recorte/rig e fundo. Fixar seed 41 nos workflows reais e comparar cada pose com a referência; rejeitar deriva. Guardar qual passagem e tom cada episódio adapta; não trocar apenas a legenda da mesma cena.

## Rota A — stack atual

1. Criar `storytelling` com alvo 28; preencher brief/ganchos/ficha, cinco cenas e o plano técnico, depois `plan.py` conforme [procedimento](producao.md#1-roteiro-bíblia-e-manifesto).
2. Gerar primeiro a identidade e o cenário. Para **cada linha abaixo**, prompt = sujeito/ação/enquadramento da linha + luz lateral quente de manhã + ilustração de recortes em cenário de pedra + paleta fixa + negativos “dedos extras, escrita, logos, roupa divergente” + seed 41. Isso fornece um prompt de imagem por plano, não um pedido de vídeo.

| Plano | Sujeito e ação da imagem | Lente/enquadramento | Motion da composição |
|---|---|---|---|
| p01 | testemunha segura cesta diante de muro baixo incompleto | 28 mm, médio frontal tipo selfie | oscilação mínima da camada, não câmera frenética |
| p02 | rua de pedra e área de trabalho vazia | 35 mm, geral | pan 20 px no fundo |
| p03 | cesta e três pedras já separadas, sem mãos em close | 50 mm, detalhe | aproximação 1,00→1,05 |
| p04 | testemunha e vizinhos ficcionais em poses distintas | 35 mm, conjunto | revelar recortes um a um, sem fingir levantar peso |
| p05 | testemunha olha para área ainda incompleta | 28 mm, médio igual a p01 | parar o movimento para a pergunta |

3. Executar `comfy.py` por workflow real/nó real; selecionar cinco imagens e registrar licenças. Recortar personagem e criar paralaxe em HyperFrames + GSAP; para gesto preciso, rig 2D/PixiJS adaptado, não “selfie generativa falante”. Manter boca neutra e relato off; sem lip-sync nativo prometido.
4. Exemplo a mesclar, com os demais planos equivalentes e módulos realmente usados:

```json
{"scenes":[{"id":"s01","narration":"A rua estava em ruínas. Por onde começar?","on_screen":"POR ONDE COMEÇAR?","visual":{"engine":"hyperframes","brief":"assets/p01.png e recorte da testemunha; faixa oliva fixa","shots":[{"cue":"A rua","frame":"médio","subject":"testemunha e ruínas","camera":"selfie simulada com paralaxe leve","in":"corte","emphasis":"obstáculo visível","sfx":""}],"transition_out":"corte"},"start":0,"duration":3}],"tool_plan":[{"module":"comfyui","tool":"comfy.py: edit/p01-api.json → assets/p01.png; cenário/pose","status":"planejado"},{"module":"gsap","tool":"GSAP: recortes → composição selfie em composition/index.html","status":"planejado"}]}
```

5. Gerar/montar voz medida (`voice.py` ou `--from-wavs`), atualizar tempos, legendas conferidas, render principal HyperFrames, `deliver.py` e `review.py` pelos comandos comuns. Não tratar os 28 s como medição feita.

## Rota B — clipes gerados fora

1. Usar p01–p05 como lista de planos de 3/6/7/8/4 s; se o serviço não aceitar esses tempos, selecionar intervalos úteis e remontar. Produzir tomadas independentes, não um prompt longo com cinco ações.
2. Prompt por plano = personagem da ficha + ação da tabela + lente/câmera da tabela + duração-alvo + “ilustração estilizada, luz quente, sem textos; manter roupa e cesta da imagem autorizada”. No p03, pedir **uma pedra já sendo colocada** somente se puder verificar mãos/contato; alternativa segura é cesta estática. No p04, pedir duas pessoas se aproximando sem objetos atravessando corpos.
3. Áudio/diálogo: preferir “sem diálogo; ambiente leve de rua” e narrar depois; se quiser fala síncrona no p01, usar a frase original exata, testar uma tomada e descartar se português/lipsync falhar. Não clonar líder religioso nem pessoa real.
4. Nomear `ep001_p01_t01.mp4` etc.; registrar origem, termos, consentimento e `publish.ai_label` como no [registro B](producao.md#2b-clipes-externos-dirigidos-selecionados-e-importados). Selecionar pela roupa, eixo e mãos ao longo de todo clipe. Importar arquivos selecionados em `composition/assets/`; `footage.py import` só para uma eventual fonte-base, não lote.
5. Montar p01→p05 em HyperFrames, medir narração/legendas e aplicar a mesma spec sonora e os mesmos portões A. A skill não enviou prompts ao serviço e não deve ser creditada como geradora desses clipes.

## Som e legenda do piloto (ambas as rotas)

Ambiente de rua discreto gravado/licenciado, sem vozes identificáveis não autorizadas. Não transformar fé em efeito cômico. Exemplo de `sound.json`: `duration:28`, `seed:41`, `events` abaixo; ajustar ao áudio medido:

```json
[{"type":"pop","at":9.5,"duration":0.15,"gainDb":-28},{"type":"pulse","at":17,"duration":0.5,"gainDb":-30}]
```

Esses sinais não substituem o ruído de pedra/rua, obtido à parte. Legenda de 2–3 palavras por grupo, sem serifa pesada licenciada, fora da cesta/rosto; mostrar “adaptação ilustrativa” e referência da passagem como texto editorial, separado da fala.

## Checklist específico

- [ ] Pergunta/obstáculo no quadro 0; não gastar três segundos com saudação ou logo.
- [ ] Mãos fora do close quando não confiáveis; cesta/faixa/rosto constantes; não sugerir lip-sync onde há off.
- [ ] Ambiente e palavra final não truncados; legenda não simula citação canônica.
- [ ] Passagem identificada; fatos separados de invenção; revisão teológica humana e respeito religioso.
- [ ] Direitos de voz/imagem e termos do gerador/modelo; IA rotulada quando aplicável, sem promessa de monetização.
- [ ] Episódio tem decisão e consequência novas, não produção em massa de testemunhos falsos. Aplicar também o checklist comum.
