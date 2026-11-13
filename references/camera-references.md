# Pesquisa de câmera e pacote de referências

Use para dirigir câmera, composição e linguagem visual de cenas novas ou de uma sequência, especialmente no Blender. Faça a pesquisa antes de construir a cena. Edição pontual de legenda/áudio não pede refazer direção; preserve referências já válidas. Não basta escrever «cinematográfico», o nome de um filme ou um estilo: transforme exemplos em decisões executáveis.

## Encontrar e observar referências

1. Defina a intenção do plano: acompanhar uma ação, revelar espaço, aproximar emocionalmente, comparar objetos ou criar a presença de um vlog. Use o estilo pedido; sem indicação, escolha referências coerentes com o assunto, sem interromper o trabalho por preferências inferíveis.
2. Pesquise filmes, séries, vlogs e exemplos técnicos pela função do movimento. Combine obra/cena + `camera movement`, `tracking shot`, `behind the scenes`, `cinematography` ou termos em português; para vlog, procure acompanhamento, câmera de mão, gimbal, POV e transições motivadas. Prefira trecho oficial, material do realizador/fotógrafo e mídia fornecida pelo usuário. O número de visualizações não comprova qualidade nem técnica.
3. Examine o trecho com a capacidade disponível. Registre obra/episódio/criador, URL, data de consulta, intervalo na fonte e o que realmente foi observado. Um vídeo acessível não foi necessariamente assistido; reproduzir no navegador sem capacidade de percepção temporal também não prova observação integral.
4. Fotos/frames mostram composição, luz, cor, materiais e perspectiva. Não comprovam trajetória, duração, aceleração ou sincronismo. Com apenas imagem, registre movimento como hipótese e proponha um teste próprio. Lente exata, equipamento e intenção do realizador também são inferências sem evidência específica.

Use a [ficha por plano](research.md#ficha-de-referência-por-plano). Separe imagem observada, trecho temporal observado, descrição do autor e inferência. Se uma fonte não abrir, tente uma alternativa pertinente, sem contornar restrições. Na falta de mídia, entregue direção provisória com lacunas declaradas; não diga que alimentou a IA ou o Blender com arquivos que não existem.

## Traduzir linguagem em câmera

| Movimento | Decisão a registrar e aplicar |
|---|---|
| Plano fixo | Posição e lente estáveis; ação, luz ou composição sustentam a intenção. Não acrescentar movimento só por obrigação. |
| Pan / tilt | Rotação horizontal/vertical a partir da posição definida; começo, alvo e limite do enquadramento. |
| Dolly / travelling | Deslocamento físico da câmera; caminho, distância e paralaxe entre primeiro plano, sujeito e fundo. Ampliar uma imagem 2D não é a mesma câmera 3D. |
| Tracking / acompanhamento | Relação câmera–sujeito durante a ação: lateral/frontal/traseira, distância, altura e velocidade relativa. |
| Órbita / arco | Centro/alvo, raio, altura e arco percorrido; não exigir uma volta completa. |
| Crane / pedestal | Variação de altura e eventual rotação para revelar ou manter o sujeito. |
| Zoom / dolly zoom | Zoom altera a lente com câmera parada; dolly zoom combina deslocamento e lente para controlar o tamanho do sujeito e mudar a relação com o fundo. Distinguir de crop digital. |
| Handheld / vlog / gimbal | Estabilização, presença do operador, deslocamento e irregularidade deliberada. No 3D, usar variação limitada e reproduzível, sem tremor arbitrário que prejudique leitura. |
| Rack focus | Troca de foco entre alvos; registrar foco inicial/final e tempo. É foco, não deslocamento da câmera. |

Para cada `scenes[].visual.shots`, mantenha `camera` legível e acrescente, quando útil, `reference_ids` e `camera_plan`: intenção, enquadramento inicial/final, sujeito/alvo, posição/altura/distância, caminho ou arco, orientação, lente/FOV e sensor/aspecto, foco/DOF, duração, velocidade/aceleração e transição. Valores estimados devem estar identificados. São detalhes opcionais de direção, não novos campos validados por `plan.py`.

Exemplo **autoral hipotético**, sem atribuição a um filme ou observação de mídia:

```json
{
  "cue": "revele o detalhe",
  "frame": "médio para close",
  "camera": "Dolly frontal curto, mantendo o detalhe no terço direito",
  "reference_ids": ["ref-produto-01"],
  "camera_plan": {
    "intent": "revelar a textura sem esconder a ação",
    "duration_s": 3.0,
    "path": "aproximação de 0,6 m; alvo fixo; altura constante",
    "lens": "50 mm / sensor 36 mm, escolha de teste, não medição da referência",
    "timing": "partida e chegada suaves; sem trocar a lente",
    "continuity": "preservar eixo, direção de luz e espaço para legenda"
  }
}
```

## Alimentar a IA e o Blender com mídia real

Monte um pacote enxuto em `research/references/`, organizado por IDs e cenas: fotos/frames de composição, trechos de vídeo relevantes quando obtidos de modo autorizado, ficha de observação e contato entre imagem → decisão → plano. Guarde o arquivo original; extrações identificam o arquivo e timecode de origem. Para estudar movimento, selecione início/meio/fim e um trecho temporal, não só um moodboard de pôsteres. Não fixe uma quantidade universal: cubra as decisões relevantes sem acumular referências incompatíveis.

Em `research/reference-pack.json`, registre o que existe e foi inspecionado. O modelo abaixo descreve a forma; preencha caminhos, hashes e estados reais, sem copiar placeholders para uma produção:

```json
{
  "schema": 1,
  "references": [{
    "id": "ref-produto-01",
    "source": {"title": "Título e criador", "url": "URL da fonte ou arquivo fornecido", "accessed_on": "AAAA-MM-DD"},
    "source_range_s": null,
    "observation": {"visual": "unverified", "motion": "unverified", "method": "Preencher somente após inspeção real"},
    "use": "study_only",
    "rights": "Condição real de acesso/uso; referência não libera reutilização no filme",
    "applies_to": ["s01/p01"],
    "media": [{"kind": "image", "path": "research/references/ref-produto-01/frame.png", "sha256": "SHA256 real do arquivo"}],
    "decisions": ["Composição/luz/câmera que serão adaptadas, com evidência ou hipótese indicada"]
  }]
}
```

Para vídeo use `kind:"video"` e o caminho real do trecho; para frames extraídos acrescente `source_time_s`. Tempos da fonte e frames do projeto são relógios diferentes. Inclua o caminho do pacote em `direction.references` e a origem em `research.sources`. Referências apenas estudadas ficam na pesquisa; arquivos efetivamente incorporados ao vídeo ou ao projeto entregue também entram em `assets[]` com direitos confirmados conforme o fluxo comum.

- **Contexto multimodal:** a IA que dirige/modela precisa abrir as imagens, e observar o trecho temporal se tiver capacidade; listar URLs ou nomes de arquivos não é alimentar visualmente o modelo. Quando outra IA/agente executar o Blender, entregue pacote, mídias/caminhos acessíveis, observações e decisões por plano; ela confirma leitura e capacidades, sem presumir que recebeu a memória do autor.
- **Entrada no Blender:** siga o [carregamento de imagens e vídeo](modules/3d.md#referências-no-arquivo-de-trabalho). Carregue referências em coleção de estudo/viewport e vídeo no Movie Clip Editor, ou frames do trecho como fallback visual. Confira no processo real que os arquivos abriram. Isso é apoio de modelagem/direção, não um motor automático image-to-3D ou um condicionamento garantido de geração.
- **Uma ou várias cenas:** reaproveite o pacote e mantenha uma bíblia de escala, lente/altura de referência, eixo, paleta, luz e identidade. Associe cada plano às referências pertinentes e registre variações intencionais; não reinvente o estilo em cada cena. Procure [itens 3D gratuitos](free-3d-assets.md) coerentes com essa direção antes de modelar tudo.
- **Limites:** não baixar mídia por métodos não autorizados ou instalar gerador/addon só para obter referências. Sem acesso ao vídeo, avance com imagens e câmera proposta, deixando a temporalidade não verificada. Se o pedido depende de reproduzir fielmente uma referência inacessível, registre a entrada essencial faltante antes de declarar fidelidade concluída.

## Testar antes da sequência inteira

Faça um blockout com geometria simples, câmera/lente e escala propostas. Compare três posições relevantes com as referências: silhueta, tamanho do sujeito, horizonte, paralaxe, luz, foco e espaços de legenda. Ajuste a câmera antes de detalhar/modelar ativos caros. Gere preview curto do movimento, verifique atravessamentos/oclusões, aceleração e passagem entre cenas; quadros isolados não aprovam trajetória ou estabilidade.

Converta duração medida em frames do projeto; use rig/alvo, keyframes/curvas e efeitos com seed/cache quando necessário. Verifique o mesmo frame após busca fora de ordem, conforme [motion](motion.md). Anote aproximações e desvios deliberados, sem fingir réplica técnica do original. O compositor final continua HyperFrames + GSAP e a aprovação audiovisual segue [revisão](review.md).

## Fontes e bibliotecas de consulta

- [Motion Prompt — camera](https://github.com/showheyohtaki/motion-prompt/blob/main/packs/camera/README.md), [camera2](https://github.com/showheyohtaki/motion-prompt/tree/main/packs/camera2) e [galeria](https://showheyohtaki.github.io/motion-prompt/): consulte nomes/demonstrações e registre URL/ID/versão do item escolhido. Traduza a intenção para bpy/GSAP do projeto; números sozinhos não são um plano. Não precisa instalar a skill externa para ler a biblioteca. Se reutilizar código/ativos, confira a licença e preserve os avisos exigidos; MIT do repositório não licencia filmes externos estudados.
- [Adobe: dolly zoom](https://www.adobe.com/creativecloud/video/production/cinematography/camera-shots-and-angles/dolly-zoom-shot.html): distinção entre movimento e lente. [Biblioteca autoral de câmera de Walid Riachy](https://www.walidriachy.com/lab/fashion-camera-movements): exemplos documentais de movimento/ritmo/alvo; ler a página não significa assistir às demonstrações.
- [Artigo de Theo indicado pelo usuário](https://x.com/theoardley/status/2116684286837330374): fonte de descoberta de bibliotecas e métodos, consultada diretamente no Chrome autorizado em 13/11/2026. [Escopo e limites da leitura](formats/virais-ia/producao.md#fonte-complementar-theo--relato-não-testado). Não importar promessas de audiência, custo zero ou pontuações de outros avaliadores como resultados desta skill.
