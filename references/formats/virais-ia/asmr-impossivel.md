# ASMR impossível — uma transformação legível, sem fala

[Índice](../virais-ia.md) · [Procedimento executável A/B](producao.md)

## Quando usar e retenção

Peça sensorial curta para uma transformação de material imaginário. A antecipação do contato e sua consequência sincronizada seguram a atenção; música ou corte não devem esconder que a ação não aconteceu.

## Requisitos e limite local

- **Obrigatório:** transformação tátil completa, contato/sombra/volume coerentes e som contínuo/denso ligado à ação, escutado em fones. Quatro estalos sobre imagens paradas não são ASMR.
- **Local possível:** geometria própria Three.js/Blender com duas metades, lâmina e filamentos animados; Foley autorizado ou textura sintética de reserva. Isso exige construir e revisar a cena, não só executar a demo visual.
- **PARE:** sem 3D equivalente construído ou gerador de imagem/vídeo validado para a ação, avise que cartões/zoom serão **animatic**, não ASMR impossível. Se o áudio sintetizado não sustentar a sensação, pare também: só ofereça demonstração sintética identificada com escopo aceito, não o formato pronto.

Aplique as [regras comuns de composição e densidade sonora](../../composition.md#regras-de-acabamento-obrigatórias).

## Roteiro preenchível — alvo 12 s

Ganchos **visuais**, não narração (completar mais dois candidatos no portão):

1. [Objeto macio] projeta sombra de [material rígido], ferramenta já quase tocando.
2. [Superfície lisa] abre uma pequena fenda que revela [interior impossível].
3. [Objeto] parece comum; no quadro 0, um fragmento [flutua/vibra] de modo impossível.

| Plano / alvo | Molde | Exemplo original sem fala |
|---|---|---|
| p01 / 0–2 | antecipação de [contato] | esfera de “névoa sólida” sobre bancada; lâmina abstrata a milímetros |
| p02 / 2–7 | uma transformação completa | lâmina atravessa; duas metades separam com interior de filamentos luminosos |
| p03 / 7–10 | consequência tátil visível | filamentos vibram, um fragmento assenta na bancada |
| p04 / 10–12 | fechar/gancho seguinte | sustentar metades e preparar corte para futuro objeto; loop só se geometria realmente fechar |

Texto opcional original: “Matéria imaginária”. Não inserir CTA falado ou promessa de propriedade física real; próximo episódio pode mudar a ação/material, não só a cor.

## Ficha do mundo/objeto

Esfera com três filamentos âmbar, exterior branco fosco, bancada grafite e lâmina geométrica sem marca. Sem personagem humano; “voz” = **nenhuma** e bordão falado = **nenhum**. Assinatura editorial discreta “Matéria imaginária”, composta fora da geração. Paleta branco/grafite/âmbar; macro equivalente 85 mm, eixo de corte esquerda→direita, câmera fixa e luz lateral grande à esquerda.

Guardar mesh/material/luz aprovados e dimensões; mesmo objeto em todos os planos, seed 131 para texturas/workflows. Não confiar em geração independente para reconstruir o interior. Reutilizar geometria e posição de câmera resolve a continuidade melhor que a seed sozinha.

## Rota A — 3D controlável, não morph de imagem

1. Criar `storytelling`, alvo 12; `voice.engine:"none"`, cenas sem narração e durações manuais; brief/ganchos e tool_plan completos, `plan.py`. **Não rodar voice.py/captions de fala**.
2. Fazer quatro imagens de storyboard: para cada linha do roteiro, sujeito/ação acima + macro 85 mm e câmera fixa + luz lateral esquerda + materiais foscos branco/grafite/âmbar + negativos “mãos, dedos, texto, logos, múltiplas lâminas, interiores inconsistentes” + seed 131 fixa em workflow real se usar `comfy.py`. Essas imagens aprovam estilo/estados, não executam o corte.
3. Construir esfera como duas metades em Blender/Three.js; criar filamentos como curvas próprias e lâmina como objeto separado. Animar deslocamento da lâmina de 2–5 s, separação das metades de 5–7 s e vibração amortecida de 7–10 s, calculada pelo tempo. Manter mesa/câmera/luz fixas, testar contato e sombras em busca arbitrária. Ver [3D](../../modules/3d.md). É a rota indicada quando geometria precisa permanecer contínua.
4. Exemplo de manifesto, a completar com as outras cenas e núcleo HyperFrames/GSAP/FFmpeg:

```json
{"voice":{"engine":"none"},"scenes":[{"id":"s01","narration":"","on_screen":"MATÉRIA IMAGINÁRIA","visual":{"engine":"hyperframes","brief":"Render 3D próprio: esfera e lâmina antes do contato","shots":[{"cue":"início","frame":"macro","subject":"esfera com três filamentos âmbar","camera":"fixa 85 mm","in":"corte","emphasis":"distância mínima da lâmina","sfx":"pulse"}],"transition_out":"continuidade de eixo"},"start":0,"duration":2}],"tool_plan":[{"module":"three","tool":"Three.js: geometria/material próprios → cena determinística; corte entre duas metades","status":"planejado"},{"module":"tone","tool":"sound.mjs: edit/sound.json → audio/sound-design.wav; sinais de contato e ressonância","status":"planejado"}]}
```

Se usar Blender em vez de Three.js, trocar módulo pela contribuição real; não declarar ambos por prestígio. Renderizar trecho e montar filme completo em HyperFrames+GSAP, não chamar um quadro com zoom de “corte da esfera”.
5. Foley/ambiente separado, render principal, `deliver.py` e `review.py` conforme comum. Sem fala, não gerar legenda inventada; rótulo de cena sintética discreto em HTML.

## Rota B — clipes externos

1. Lista: p01 2 s, p02 5 s, p03 3 s, p04 2 s. Priorizar **uma tomada contínua p01–p03**, se o gerador permitir, e selecionar os trechos; não prometer duração/suporte. Se tomadas independentes não preservarem corte/filamentos, descartar e voltar ao 3D controlável.
2. Prompt p02 preenchido: “Esfera branca fosca com três filamentos âmbar da referência própria sobre bancada grafite; uma única lâmina atravessa da esquerda para a direita, as duas metades se afastam sem mudar de volume; macro 85 mm estático, luz grande à esquerda, alvo cinco segundos, sem fala/música/texto; contato seco e ressonância breve se houver áudio; preservar bancada, tamanho e posição inicial da referência.” É descrição genérica, não sintaxe de produto.
3. Para p01 pedir aproximação mínima da lâmina; p03 pedir só vibração/assentamento; p04 só sustentação. Em todos: sujeito/material da ficha, câmera fixa, duração da lista, “sem diálogo”, áudio desejado e continuidade com frame próprio autorizado. Não pedir mãos para operar a lâmina nem copiar vídeo/objeto de outro criador.
4. Nomear `ep001_p02_t01.mp4`; registrar serviço/termos/modelo se conhecido, referências e IA em assets/publish. Selecionar olhando o clipe inteiro, especialmente o instante de contato: lâmina não atravessa matéria sem reação; não surgem filamentos extras; bancada não “respira”. Importar selecionados em `composition/assets/`; não aplicar corte de silêncios de `footage.py` ao gesto sensorial.
5. Montar em HyperFrames preservando o tempo real do contato. Se o áudio gerado falhar, descartar **essa faixa**, sonorizar por Foley e sinais; usar `--mute-video-audio` na rota de mix externa. Mesmos portões técnicos e de revisão humana; serviço fora do stack permanece fora.

## Som proposto (não medição de referência)

Gravar ambiente de sala muito discreto e contato seguro com objetos inofensivos, sem tentar “cortar névoa” ou material perigoso real. Sinais de Tone.js são estilizados, não ASMR materialmente comprovado. Spec `duration:12`, `seed:131`, `events`:

```json
[{"type":"pulse","at":1.6,"duration":0.25,"gainDb":-34},{"type":"impact","at":2.2,"duration":0.12,"gainDb":-28},{"type":"whoosh","at":4.7,"duration":0.5,"gainDb":-32},{"type":"pop","at":8.4,"duration":0.12,"gainDb":-30}]
```

Os quatro sinais acima são **acentos, não faixa ASMR completa**. Sem sala/Foley autorizados, acrescente a [reserva ambiente/Foley](../../modules.md#reserva-de-ambiente-e-foley-sintetizados) com **D=12 s**, **seed=131** e preset sem fala; sobreponha a textura durante a travessia/vibração e reancore os contatos ao render escolhido. Registre `kind:"sfx"` e identifique a síntese. Cumpra a densidade/limites de silêncio da composição; não use loudness como prova de relaxamento. Se os osciladores soarem ásperos/tonais em vez de táteis, PARE e peça Foley adequado. Sem narração e, por padrão, sem música. Escute em fones/alto-falante e evite agudos/picos desagradáveis; sem escuta, a revisão sensorial fica pendente.

## Checklist específico

- [ ] Contato começa cedo; ação termina visivelmente, sem corte disfarçando defeito.
- [ ] Volumes, interior, sombra e eixo contínuos; lâmina/objeto sem deformação e sem mãos/texto gerados.
- [ ] Não há fala, lip-sync nem legenda de fala; ambiente/contato sincronizados e realmente escutados por revisor.
- [ ] Loop não teletransporta metades; se não fecha, usar final honesto.
- [ ] Rótulo de material sintético/IA quando aplicável; não apresentar teste físico real nem instrução perigosa.
- [ ] Termos/licenças/direitos de áudio e imagem; variar ação/substância, não produzir cópias cromáticas em massa. Monetização não garantida; checklist comum mantido.
