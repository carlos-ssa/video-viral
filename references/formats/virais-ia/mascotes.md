# Mascotes consistentes em minissérie

[Índice](../virais-ia.md) · [Procedimento executável A/B](producao.md)

## Quando usar e retenção

Para criar reconhecimento e vínculo com um personagem próprio ao longo de episódios. O público reconhece quem age, mas fica pela mudança de objetivo/relação; consistência não significa repetir a mesma história.

## Requisitos e limite local

- **Obrigatório:** mascote reconhecível em poses/ações distintas, objetivo, tentativa e consequência; identidade e contatos sonoros contínuos. Não basta repetir a mesma figura com títulos novos.
- **Local possível:** rig 2D/3D original reutilizado, cenários próprios e performance animada por tempo; imagens fornecidas ou ComfyUI validado podem apoiar poses/fundos. Uma direção cartoon aceita não exige fotorrealismo nem gerador de vídeo.
- **PARE:** se o pedido exigir atuação/realismo que os ativos ou rig não entregam e não houver gerador de imagem/vídeo validado, avise que poses vetoriais com zoom serão **animatic**, não a minissérie viral solicitada. Só produza essa alternativa com escopo aceito.

Aplique as [regras comuns de composição](../../composition.md#regras-de-acabamento-obrigatórias); mantenha o cartão final fora do rodapé e confirme a fonte carregada.

## Roteiro preenchível — alvo 36 s

Ganchos (completar mais dois candidatos audiovisuais):

1. “[Mascote] trouxe [objeto], mas encontrou [obstáculo].”
2. “Hoje eu só precisava [tarefa]. Aconteceu isto.”
3. “O menor [personagem] ficou com a maior [responsabilidade].”

| Plano / alvo | Molde | Exemplo original pt-BR |
|---|---|---|
| p01 / 0–3 | [desejo/obstáculo] | “Bia trouxe o pacote. A ponte estava fechada.” |
| p02 / 3–10 | [regra do mundo] | “A oficina do outro lado esperava a peça antes da chuva.” |
| p03 / 10–19 | [tentativa característica] | “Ela tentou equilibrar o pacote numa folha. A corrente levou a folha, não a encomenda.” |
| p04 / 19–29 | [decisão com consequência] | “Bia pediu ajuda à barqueira. As duas levaram a peça pelo caminho mais longo.” |
| p05 / 29–36 | [payoff e próxima relação] | “A entrega chegou. Amanhã, Bia vai ajudar a consertar o barco.” |

Não é necessário alongar narração para preencher os alvos: reservar silêncio/ação. Fecho paga a entrega e cria dívida de ajuda, não apenas “parte dois”.

## Ficha da série

Bia: capivara ilustrada de focinho retangular, pelo castanho uniforme, colete lilás com bolso quadrado, orelha direita com pequena dobra **desenhada**, pacote amarelo sem letras. Voz autorizada pt-BR acolhedora, mesma seleção Kokoro/ator e velocidade; bordão “A gente acha um caminho”. Barqueira é personagem própria secundária com referência separada, nunca introduzida por geração aleatória.

Paleta castanho/lilás/amarelo/azul-rio, vila fosca estilizada; câmera 40 mm na altura dos olhos, travessia esquerda→direita. Guardar frente/perfil/costas, escala e rig/modelo aprovados, voz de amostra e relações. Seed 191 nos workflows não garante dobra/bolso: conferir os dois a cada tomada, reutilizar assets sempre que possível. Registrar pacote entregue e favor pendente no mapa da série.

## Rota A — ativos reutilizados, não identidade regenerada a cada plano

1. Criar `storytelling`, alvo 36; cinco candidatos, roteiro, direção/ficha e tool_plan, depois `plan.py`.
2. Prompt por plano = sujeito/ação/lente da tabela + luz nublada suave à esquerda + estilo “mascote ilustrado fosco, volume simples e vila sem marcas” + paleta da ficha + negativos “dedos extras, texto, logotipo, colete/dobra/bolso divergentes” + seed 191 no workflow real. Usar referência autorizada apenas se o grafo aceitar.

| Plano | Sujeito/ação para imagem | Lente/enquadramento | Movimento A |
|---|---|---|---|
| p01 | Bia segura pacote diante de cancela fechada | 40 mm, médio | avanço curto ao obstáculo |
| p02 | oficina além do rio e nuvens | 35 mm, geral | paralaxe rio/ponte/oficina |
| p03 | folha vazia se afasta; Bia mantém pacote | 50 mm, detalhe amplo | folha em trajetória, pacote fixo no rig |
| p04 | Bia e barqueira ao lado do barco com pacote | 40 mm, conjunto | troca de poses selecionadas ou rig; sem morph |
| p05 | pacote sobre bancada, Bia e barqueira juntas | 40 mm, médio | sustentar a nova relação |

3. Gerar fundos/poses com `comfy.py`, mas preferir modelo Three.js/Blender ou rig/recortes 2D aprovados para a personagem. Não variar a espécie/volume só para caber no enquadramento. Ação de barco exige cena 3D ou recortes com limite explícito, não promessa de física na imagem.
4. Fragmento a completar com demais cenas/módulos reais:

```json
{"scenes":[{"id":"s01","narration":"Bia trouxe o pacote. A ponte estava fechada.","on_screen":"A PONTE FECHOU","visual":{"engine":"hyperframes","brief":"Bia aprovada, pacote amarelo e ponte em camadas","shots":[{"cue":"Bia","frame":"médio","subject":"mascote própria e cancela","camera":"avanço curto","in":"corte","emphasis":"obstáculo","sfx":"pop"}],"transition_out":"corte"},"start":0,"duration":3}],"tool_plan":[{"module":"gsap","tool":"GSAP: rig/recortes Bia → composition/index.html; gesto e paralaxe","status":"planejado"},{"module":"comfyui","tool":"comfy.py: workflows de cenário → assets/p01.png; vila consistente","status":"planejado"}]}
```

5. Medir narração com `voice.py`/WAVs, atualizar cenas, transcrever/importar legenda final; compor/renderizar HyperFrames + GSAP, mix e portões comuns. Para reuso entre episódios, copiar ativos aprovados com registro de licença, não copiar um `review` antigo para o novo vídeo.

## Rota B — geração externa com seleção por identidade

1. Lista p01–p05 com alvos 3/7/9/10/7 s; dividir p03/p04 se o serviço não sustentar ação/tempo. Antes do episódio inteiro, testar uma tomada frontal e uma de perfil com a referência própria. Sem estabilidade, não gastar o restante em tentativas incompatíveis: voltar ao rig A.
2. Prompt de cada plano: descrição fixa de Bia + ação da tabela + câmera 40/35/50 mm indicada + duração-alvo + fala/áudio + estilo/paleta/luz + continuidade com referência autorizada, lado da dobra/bolso/pacote. P01 olha para cancela; p02 só paisagem; p03 folha se afasta e pacote permanece; p04 personagens embarcam uma de cada vez ou já aparecem sentadas; p05 pacote é colocado na bancada sem mudar de tamanho.
3. Preferir “sem diálogo; água/ambiente suave se disponível” e narração off original. Exemplo p03: “Bia da referência, colete lilás com bolso quadrado, segura pacote amarelo enquanto uma folha vazia desce o rio; detalhe amplo 50 mm, câmera fixa, alvo nove segundos; sem fala/texto, água suave, materiais foscos e luz nublada; conservar mãos/patas, pacote e lado da orelha.” Se pedir fala integrada, testar voz/lipsync; não prometer que o produto fará isso.
4. Nomear `ep001_p01_t01.mp4` etc.; registrar origem/licença/IA/consentimentos e selecionar o clipe inteiro por focinho, dobra, colete, pacote e eixo. Importar selecionados na pasta da composição; não repetir `footage.py import` como se cadastrasse lote de personagens.
5. Montar em HyperFrames com intervalos úteis, mesma narração/legenda/som e `deliver.py`/`review.py`. Se usar áudio gerado, garantir direitos e remover duplicações na mix; gerador continua fora da skill.

## Som e legendas

Ambiente de rio/vila autorizado separado, madeira do barco e pacote na bancada em Foley. Spec de piloto `duration:36`, `seed:191`, `events`:

```json
[{"type":"pop","at":0.4,"duration":0.15,"gainDb":-25},{"type":"whoosh","at":12,"duration":0.4,"gainDb":-29},{"type":"pop","at":29.4,"duration":0.15,"gainDb":-26}]
```

Sem rio/vila/madeira autorizados, aplique a [reserva ambiente/Foley](../../modules.md#reserva-de-ambiente-e-foley-sintetizados) com **D=36 s**, **seed=191**, preset sob fala e `pop` na entrega do pacote. Ajuste D/contatos ao áudio medido, registre `kind:"sfx"` e identifique a textura como sintética, não rio real. Use assinatura breve sem cobrir palavras e legenda por sentido fora do colete/pacote; componha os textos da oficina, não os gere na imagem.

### Conhecimento de Theo, adaptado ao stack

O [post/artigo de Theo](https://x.com/theoardley/status/2116684286837330374) apresenta personagens 2D desenhados por código como caminho de consistência e aprovação de história/visual/storyboard antes de animar: **relato do autor, não testado aqui**. A aplicação A é reutilizar rig/recortes e aprovar três quadros; não importar Remotion nem outros motores/repositórios mencionados. Na rota B isso vira teste de continuidade/seleção, não promessa de que gerador manterá identidade. [Limites da fonte](producao.md#fonte-complementar-theo--relato-não-testado).

## Checklist específico

- [ ] Reconhecer Bia sem depender do nome; desejo/obstáculo visíveis nos primeiros três segundos.
- [ ] Focinho, dobra, bolso, escala e voz constantes; mãos/patas e letras sem deformações.
- [ ] Lipsync validado ou off; água/ambiente e contato presentes, escuta humana ou pendência explícita.
- [ ] Pacote não troca de mão/lado/tamanho sem ação; episódio seguinte lembra o favor prometido.
- [ ] Personagem própria e voz autorizada; modelos/gerador/ativos licenciados, IA rotulada quando aplicável.
- [ ] Relação/decisão evoluem, não catálogo de poses repetidas; monetização não garantida. Checklist comum; conteúdo religioso exige fonte/respeito/revisão teológica.
