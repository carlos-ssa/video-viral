# Novela serializada — conflito com consequência

[Índice](../virais-ia.md) · [Procedimento executável A/B](producao.md)

## Quando usar e retenção

Séries com personagens recorrentes, escolhas incompatíveis e consequência persistente. Entregar uma resposta parcial no episódio; a próxima pergunta deve nascer da ação, não de interromper arbitrariamente uma fala.

## Roteiro preenchível — alvo 54 s

Três ganchos, mais dois candidatos para o portão:

1. “[Personagem] prometeu [coisa]. Agora só resta [recurso].”
2. “Se eu abrir [porta], vou perder [algo importante].”
3. “Dois pedidos. Um [objeto]. Quem fica esperando?”

| Plano / alvo | Molde | Exemplo original: a oficina das lanternas |
|---|---|---|
| p01 / 0–3 | [recurso escasso] já visível | Narrador: “Duas encomendas. Uma única lâmpada.” |
| p02 / 3–11 | objetivo de A | Lume: “Prometi iluminar a praça hoje.” |
| p03 / 11–20 | objetivo incompatível de B | Bruma: “E o caminho do abrigo continua escuro.” |
| p04 / 20–31 | tentativa/decisão concreta | Narrador: “Eles montam um refletor para dividir o feixe. O teste ilumina só metade do caminho.” |
| p05 / 31–43 | custo e recompensa parcial | Lume: “A praça pode esperar. Hoje levamos a lâmpada ao abrigo.” |
| p06 / 43–54 | novo problema + escolha específica | Bruma: “Resolvido por hoje. Amanhã, buscamos outra lâmpada ou construímos um refletor melhor?” |

Medir cada performance; se houver pausas de reação, não preencher tudo com fala. O próximo episódio deve honrar ou justificar a escolha do público sem prometer que uma votação ainda inexistente aconteceu.

## Ficha de personagens e mundo

Lume: lanterna antropomórfica cúbica cobre, dois olhos pretos, alça quadrada, postura impulsiva. Bruma: lanterna cilíndrica azul fosca, alça redonda, postura metódica. Pernas simples, **sem mãos realistas**. Vozes autorizadas contrastantes (A mais rápida, B mais pausada), preset e velocidade anotados por performance; bordões “Vamos acender isso” e “Primeiro, o caminho”, usados com parcimônia. Não são personagens/frutas de reality conhecido.

Oficina creme com bancada escura; praça e caminho vistos sempre no mesmo eixo; quadro médio 40 mm por personagem, geral 28 mm. Guardar modelos/rigs, paleta, escala relativa e mapa de relações. Seed 163 nos workflows; validar identidade, não apenas cor. Registro de continuidade: onde ficou a lâmpada, promessa ainda pendente e resultado real de eventual votação.

## Rota A — personagens reutilizáveis e montagem de falas

1. Criar `storytelling`, 54 s; roteiro com uma voz por cena, ficha/ganchos/brief, `plan.py`. Não há campo de voz por personagem presumido: gerar performances separadas com voz selecionada ou receber WAVs autorizados em `audio/scenes/sXX.wav`; montar com `voice.py --from-wavs`.
2. Prompt por plano = sujeito/ação/lente da linha + luz de oficina suave à esquerda/noite azul no exterior + estilo 2D fosco com props 3D simples + paleta cobre/azul/creme + negativos “mãos humanas, membros extras, letras/logos, troca de alças” + seed 163 no workflow real.

| Plano | Imagem dirigida | Enquadramento | Movimento A |
|---|---|---|---|
| p01 | duas lanternas diante de uma lâmpada | 28 mm, geral da bancada | pequeno avanço até o recurso |
| p02 | Lume aponta o corpo para mapa sem texto da praça | 40 mm, médio de A | inclinação do rig |
| p03 | Bruma junto à janela escura | 40 mm, médio de B | contraplano no mesmo eixo |
| p04 | refletor dividido e feixe parcial | 50 mm, detalhe sem mãos | máscara de luz revela falha |
| p05 | Lume e Bruma junto à saída com lâmpada | 28 mm, conjunto | deslocar recortes/rigs para a porta |
| p06 | duas opções desenhadas, personagens aguardam | 40 mm, médio | pausa, cartões compostos legíveis |

3. `comfy.py` para fundos/poses; preferir mesmo modelo/rig 2D ou 3D para personagens. GSAP/PixiJS adaptado move corpo/alça; Three.js/Blender se luz/refletor precisar de volume. O diálogo pode ser off com reações, sem boca realista nem promessa de lip-sync nativo. Montar por fala/reação, não alternar zoom mecanicamente.
4. Fragmento a completar:

```json
{"scenes":[{"id":"s01","narration":"Duas encomendas. Uma única lâmpada.","on_screen":"UMA LÂMPADA","visual":{"engine":"hyperframes","brief":"Lanternas originais e lâmpada na bancada","shots":[{"cue":"Duas","frame":"geral","subject":"Lume, Bruma e recurso escasso","camera":"avanço lento","in":"corte","emphasis":"uma lâmpada","sfx":"pop"}],"transition_out":"corte"},"start":0,"duration":3}],"tool_plan":[{"module":"gsap","tool":"GSAP: rigs aprovados → composition/index.html; falas e reações","status":"planejado"},{"module":"ffmpeg","tool":"voice.py --from-wavs: performances autorizadas → audio/voice.wav; montagem medida","status":"planejado"}]}
```

5. Montar voz medida, conferir legendas pelo áudio final, renderizar filme principal HyperFrames, sonorizar e executar entrega/revisão comum. `ffmpeg` descreve aqui a montagem de WAVs, não um TTS novo.

## Rota B — tomadas externas com continuidade

1. Pedir p01–p06 separados, alvos 3/8/9/11/12/11 s; para p04/p05 longos, dividir a ação em detalhes e reação **se a ferramenta só gerar clipes curtos**, registrando subplanos na lista, sem fingir suporte a onze segundos exatos.
2. Prompt por plano combina sujeito/ação/lente da tabela, câmera/estilo da ficha, duração-alvo, diálogo exato de **um único falante** ou “sem diálogo” e ambiente de oficina/noite. Anexar referência própria de ambos os personagens; repetir formato de alça, tamanho e prop. Para p04 pedir apenas refletor e mudança de feixe, sem mãos nem diálogo; para p05 só saída com a lâmpada, mantendo o lado de saída.
3. Exemplo p03: “Bruma, lanterna cilíndrica azul com alça redonda da referência autorizada, vira o corpo para janela escura; médio 40 mm no eixo da oficina, câmera fixa, alvo nove segundos; fala original ‘E o caminho do abrigo continua escuro’, voz autorizada conforme referência apenas se disponível; ambiente leve de oficina, sem música; estilo fosco creme/azul, manter proporções e cenário; sem letras.” Se voz/lipsync não funcionar, gerar sem fala e usar off, não aceitar boca dessincronizada.
4. Nomear `ep001_p03_t01.mp4`; registrar origem/termos/IA/consentimentos, selecionar pelo clipe inteiro e pelo raccord de olhar/posição/prop. Guardar rejeições e intervalo útil. Importar selecionados na pasta do compositor; `footage.py import` só registra uma fonte-base, não sequencia a novela automaticamente.
5. Montar em HyperFrames, performances/ambiente em faixas sem duplicação, legendas do final e mesmos portões. Não chamar API externa nem adicionar gerador ao stack.

## Som e legendas

Oficina com ruído baixo de bancada e exterior noturno licenciado; mesmo ambiente nos contraplanos. Spec proposta `duration:54`, `seed:163`, `events`:

```json
[{"type":"pop","at":0.4,"duration":0.15,"gainDb":-26},{"type":"pulse","at":26,"duration":0.7,"gainDb":-29},{"type":"whoosh","at":43,"duration":0.3,"gainDb":-28}]
```

Sincronizar o teste de luz e os cartões após medir performances. Legendas de 2–3 palavras, identificar o falante por rótulo editorial/posição consistente (não só cor), sem cobrir alças/rosto.

### Contribuição documental de Theo

No [post/artigo de Theo](https://x.com/theoardley/status/2116684286837330374), **relato do autor, não testado aqui**, o formato de sobrevivência combina bonecos 2D com mundo 3D, HUD de estado e escolha final. Adaptamos a mecânica, não personagens nem o prompt: manter no episódio um cartão autoral “lâmpadas disponíveis: 1”, atualizado para a localização real, e oferecer escolha com consequência. HUD é opcional; não importar repositório, motor nem `CLAUDE.md` do autor. [Escopo da leitura](producao.md#fonte-complementar-theo--relato-não-testado).

## Checklist específico

- [ ] Conflito/recurso já no início; recompensa parcial antes da pergunta, sem cliffhanger vazio.
- [ ] Alças, volume, olhos e prop constantes; mãos/textos sem deformação; não trocar vozes nos contraplanos.
- [ ] Lip-sync validado ou off explícito; mesmo ambiente entre cortes; revisor escuta todo diálogo.
- [ ] Raccord de eixo/olhar/lâmpada e histórico de promessas preservados; voto não fabricado.
- [ ] Personagens próprios, direitos de voz/imagem/modelos; sem violência, sexualização ou estereótipo copiados dos virais.
- [ ] Rótulo de IA/publicidade e termos comerciais; sem episódios intercambiáveis em massa ou garantia de monetização. Checklist comum; se abordar religião, fonte/respeito/revisão teológica.
