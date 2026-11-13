# Procedimento executável das oito receitas

Parte integrante do [guia](../virais-ia.md). Execute a sequência comum e as decisões específicas do capítulo escolhido. São instruções de produção, **não evidência de que estes renders foram executados nesta atualização documental**.

## 0. Preparar sem instalar

Comandos relativos à pasta da skill; `<pai>` é pasta absoluta, `<P>` é `<pai>/<slug>`, `<N>` é a raiz npm **já instalada**. Substitua os marcadores; não cole `<...>` literalmente no shell. No Windows use o shim `hyperframes.cmd`. Não use setup nem `npx` com download. No ambiente do processo defina `VIDEO_VIRAL_NO_INSTALL=1`; para ferramentas de modelos, também `HF_HUB_OFFLINE=1` e `TRANSFORMERS_OFFLINE=1`. Em Git Bash/POSIX:

```sh
export VIDEO_VIRAL_NO_INSTALL=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
python scripts/new_project.py piloto --title "Título original" --format storytelling --aspect 9:16 --seconds 36 --dir "<pai>"
```

O script acrescenta o slug à pasta pai. Use o Python/venv existente apropriado quando necessário. **Essas variáveis não impediam a CLI HyperFrames de baixar Chrome/fontes**; configure `HYPERFRAMES_BROWSER_PATH`, `HYPERFRAMES_CACHE_DIR` e fontes locais antes de chamar a CLI, conforme [setup](../../setup.md#browser-cache-e-execução-sem-rede). Cache não é modo offline. Se dependência, peso, browser, serviço ComfyUI ou voz não estiver disponível, **não instale/inicie implicitamente**. Confira a seção “Requisitos e limite local” da receita: se faltar um requisito essencial, PARE e avise que 2D/tipografia seria animatic, não o formato pedido; só prossiga nessa alternativa com escopo aceito. Os exemplos de workflow dependem do grafo real do usuário, não de um modelo hipotético.

## 1. Roteiro, bíblia e manifesto

A ficha de continuidade é um documento editorial em `research/`: aparência frente/perfil, escala, roupa/prop, voz autorizada, intenção, bordões, relações, paleta, lente e eixo de câmera fixos. Não inventar um campo `character` no manifesto. Salve imagens aprovadas em `assets/`, registre os direitos e compare cada nova tomada com elas. Semente fixa ajuda a repetir uma geração, **não garante identidade entre poses**; reutilizar recortes/rig/modelo aprovado é mais estável.

Preencha brief, cinco `hook_candidates`, vencedor em `hook`, `cta`, direção e cenas. Cada receita oferece três aberturas; crie mais duas variantes audiovisuais específicas e avalie conforme [marketing](../../marketing.md), pois o portão pede cinco. Não confundir essas alternativas com cinco cenas no filme.

Fragmento real de `video.json` (mesclar no projeto criado; **não é manifesto completo nem passe livre no portão**). Tempos de 4 s são exemplificativos e serão substituídos pelos medidos:

```json
{
  "stack": {"version":"2.0.0","compositor":"hyperframes","modules":["hyperframes","gsap","ffmpeg","comfyui","kokoro","faster-whisper","tone"]},
  "scenes": [
    {"id":"s01","narration":"A ponte fechou, mas o pedido precisava chegar.","on_screen":"UM CAMINHO A MENOS",
     "visual":{"engine":"hyperframes","brief":"Recorte original em ponte estilizada; assets/p01.png",
       "shots":[{"cue":"A ponte","frame":"médio","subject":"mensageira própria diante da cancela","camera":"paralaxe lateral leve","in":"corte","emphasis":"cancela fechada","sfx":"pop"}],
       "transition_out":"corte"},"start":0,"duration":4}
  ],
  "tool_plan": [
    {"module":"comfyui","tool":"comfy.py: edit/p01-api.json → assets/p01.png; contribuição: fundo e pose selecionada","status":"planejado"},
    {"module":"kokoro","tool":"voice.py: scenes.narration → audio/voice.wav e tempos; contribuição: relato","status":"planejado"},
    {"module":"faster-whisper","tool":"captions.py: áudio final → captions/words.json; contribuição: tempos conferidos","status":"planejado"},
    {"module":"hyperframes","tool":"HyperFrames: composition/index.html → render/master.mp4; contribuição: montagem principal","status":"planejado"},
    {"module":"gsap","tool":"GSAP: imagens/recortes → timeline pausada; contribuição: paralaxe","status":"planejado"},
    {"module":"tone","tool":"sound.mjs: edit/sound.json → audio/sound-design.wav; contribuição: sinais sincronizados","status":"planejado"},
    {"module":"ffmpeg","tool":"deliver.py: render/master.mp4 e faixas → out; contribuição: mix e exportação","status":"planejado"}
  ]
}
```

Os IDs acima existem no catálogo. Acrescente `pixi`, `three` ou `blender` em `stack.modules` e entrada correspondente em `tool_plan` **somente se os usar**; a contribuição/entrada/saída está descrita no texto de `tool`, sem novos campos presumidos. `planejado` muda para `adaptacao`, `integrado` ou `validado-neste-projeto` apenas com evidência real. Na rota B, não colocar o gerador externo como módulo: registrá-lo na origem dos ativos; manter compositor/GSAP/FFmpeg e módulos de som/voz efetivamente usados.

```sh
python scripts/plan.py "<P>"
```

0: estrutura consistente, não qualidade; 1: completar; 2: dados declarados pendentes em `brief.missing_inputs`, **não produzir como se resolvidos**. Fixar três quadros de estilo antes do filme inteiro.

## 2A. Imagens, recortes e movimento do stack

Para **cada plano**, preencha esta estrutura textual. É modelo editorial de prompt, não sintaxe de um produto:

> Sujeito: [identidade da ficha + roupa/prop fixos]. Ação: [uma pose legível]. Lente/enquadramento: [distância, eixo, espaço para legenda]. Luz: [direção, temperatura, contraste]. Estilo: [material, paleta, nível de realismo]. Negativos: [mãos/dedos extras, rosto assimétrico, letras/logos, roupa ou proporções divergentes]. Seed: [inteiro fixo anotado no workflow]. Referência: [imagem própria aprovada, quando o grafo real aceitar].

Cada receita dá o conteúdo por plano; combinar com esta estrutura e a ficha fixa. Colocar seed/prompt **nos nós existentes do workflow**, não num campo inventado de `video.json`. Referência visual requer nó/fluxo configurado; o cliente não injeta identidade magicamente. Exporte em **API JSON**, confirme checkpoint e nó de saída reais:

```sh
python scripts/comfy.py "<P>" --workflow "<P>/edit/p01-api.json" --output-node <id-real> --output assets/p01.png
```

Repita por plano, com nomes p02, p03 etc.; PNG/JPEG/WebP deve corresponder à saída. O cliente não gera/importa vídeo de qualquer nó. `--license "<licença confirmada>" --commercial-ok` só com termos reais dos modelos/ativos; sem prova, não passar essas opções. Guardar receipt/hash, prompt, seed e referência junto à seleção; isso não atesta qualidade.

Separe fundo, personagem e primeiro plano em camadas quando possível. Em HyperFrames, personagem com deslocamento menor que o primeiro plano e maior que o fundo produz paralaxe; limitar escala para não revelar bordas. Num plano de 4 s, exemplo GSAP no HTML do [guia de composição](../../composition.md):

```js
const tl = gsap.timeline({paused:true});
tl.fromTo('#fundo', {scale:1.02,x:0}, {scale:1.06,x:-8,duration:4,ease:'none'}, 0);
tl.fromTo('#personagem', {x:0}, {x:16,duration:4,ease:'none'}, 0);
window.__timelines.main = tl;
```

Criar os elementos/URLs reais no HTML; não aplicar perspectiva que exponha verso de recorte plano. Para deslocamento em profundidade verdadeiro, construir cena Three.js/Blender, fixar câmera/luz/material e calcular estado pelo tempo; ver [3D](../../modules/3d.md). Não chamar zoom de imagem de “ação corporal gerada”. Para recortes/2D pode-se iniciar uma cena:

```sh
node scripts/visual_scene.mjs --module pixi --output "<P>/scenes/p01" --width 1080 --height 1920 --duration 4 --seed 17 --node-root "<N>"
```

É **demo**, não filme pronto. Adaptar `assets/adapter.js` aos recortes/gestos do capítulo. O helper `bundle(entry, outFile, nodeRoot)` existe em `scripts/_node.mjs`; a partir da pasta da skill, reconstruir a entrada gerada usando as dependências locais:

```sh
node --input-type=module -e "import { bundle } from './scripts/_node.mjs'; await bundle(process.argv[1], process.argv[2], process.argv[3]);" "<P>/scenes/p01/assets/scene-entry.js" "<P>/scenes/p01/assets/scene.js" "<N>"
```

Renderizar `<P>/scenes/p01` com o executável HyperFrames já instalado (os mesmos comandos da seção 4, saída própria dentro de `composition/assets/`) e incluir o trecho no filme principal, ou adaptar o wrapper aninhado conforme [composição](../../composition.md). Sem adaptar/reconstruir/renderizar, registrar como planejado, não usado. A mesma disciplina vale para `paper`, `p5` e `gl-transitions`; não usar todos por obrigação.

## 2B. Clipes externos dirigidos, selecionados e importados

1. Escreva uma **lista de planos**, um por arquivo: ID, função narrativa, início/duração-alvo, sujeito, ação única, câmera, continuidade e áudio desejado. As tabelas de cada receita são essa lista inicial. Gerar 2–3 tomadas por plano é escolha editorial, não requisito/API automatizado da skill.
2. Em serviço escolhido pelo usuário, fornecer imagem própria aprovada como referência se houver suporte. Prompt textual genérico por plano:
   > [Sujeito e traços fixos], [ação única com estado inicial e final], [câmera/lente/enquadramento e movimento], duração-alvo [n s], [diálogo original exato OU sem diálogo], [ambiente e efeitos desejados OU sem áudio], estilo [paleta/material], continuidade com [referência autorizada + roupa + prop + lado de entrada/saída]. Não inserir textos/logos; preservar rosto/mãos/volume dos objetos.
3. Não prometer que um produto aceitará duração exata, fala pt-BR, seed, áudio separado, referência ou lip-sync. Conferir resultado real; se falhar, gerar sem fala e usar narração off/contraplano, não fingir sincronia. Assegurar termos e direitos de pessoa/voz antes do uso.
4. Nomear `ep001_p01_t01.mp4`, `ep001_p01_t02.mp4` etc. Preservar originais em `source/`; copiar apenas selecionados para `composition/assets/`, sem apagar tentativas. Registrar em `research/` a decisão: tomada, intervalo útil, motivo do descarte (rosto, mão, continuidade, câmera, áudio). Não selecionar só o quadro inicial: inspecionar começo/meio/fim e o clipe inteiro.
5. Registrar **cada arquivo realmente utilizado** em `assets`; não existe comando universal de importação múltipla de tomadas. Copiar para a pasta do projeto/HTML é a importação de assets do compositor. Para um clipe-base com áudio, o importador existente é:

```sh
python scripts/footage.py import "<P>" "<P>/source/ep001_p01_t01.mp4" --third-party --no-clean
```

Isso guarda **um** `source.footage`, não copia o vídeo e extrai `audio/source.wav` quando há áudio. Repetir não cria uma biblioteca de planos; substitui a fonte principal. `--third-party` é conservador para material recebido: revisar a origem/licença real, não concluir que a skill ou o usuário filmou o conteúdo. Para múltiplos planos usar assets + HTML; não executar `cut` de silêncios em ASMR nem esperar montagem multiclipe automática. Para A-roll único, EDL e `footage.py render` podem preparar base conforme [gravação](../gravacao.md), que ainda passa pelo compositor.

Fragmento de registro **honesto enquanto direitos estão pendentes**; substituir informações por comprovantes reais antes de entregar monetizado:

```json
{
  "assets":[
    {"path":"source/ep001_p01_t01.mp4","kind":"video","source":"Fornecido pelo usuário; gerado por IA fora da skill; serviço/versão/data e referência anotados em research; consentimento de imagem/voz pendente","license":"Termos do serviço e referências a confirmar","commercial_ok":null}
  ],
  "publish":{"ai_label":true,"ad_disclosure":false}
}
```

Não existe campo de IA por ativo neste contrato; marcar em `source` e no `publish.ai_label` global, além de preencher o rótulo na plataforma conforme regras atuais. Licença de geração não libera imagem/voz/marca de terceiros. Registrar também cópias, fontes, áudio e referências usadas. Com licença real/comercial confirmada, preencher texto e `commercial_ok:true`, nunca apenas para passar o portão.

6. Selecionar o intervalo útil antes de compor. Se for necessário aparar, criar derivado sem sobrescrever original, documentando início/fim. Montar na ordem narrativa em HyperFrames com `class="clip"`, `data-start` e `data-duration`; o caminho do vídeo deve apontar ao arquivo **dentro de composition**. Exemplo para tomada já aparada de 4 s:

```html
<video id="p01" class="clip" src="assets/ep001_p01_t01.mp4"
  data-start="0" data-duration="4" data-track-index="0" muted playsinline></video>
```

`muted` é adequado quando a mix é construída separadamente. Não presumir que silencia a extração de áudio do runtime: para a rota de faixas externas, entregar com `--mute-video-audio`. Se áudio de performance é a única fonte, preservá-lo e não adicionar uma segunda voz por cima. Conferir a extração/mix em render de teste; preview não garante áudio final correto.

## 3. Voz medida, legendas e som (ambas as rotas)

Para narração, preencher `scenes[].narration` e gerar Kokoro. Para falas de personagens diferentes, selecionar voz por performance em projetos/tomadas separados ou fornecer os WAVs de cada cena, sem inventar `voice` por personagem no schema. Identificar atores/consentimentos. Na novela, preferir uma fala por cena:

```sh
python scripts/voice.py "<P>"
# Alternativa: WAVs autorizados já em audio/scenes/s01.wav, s02.wav...
python scripts/voice.py "<P>" --from-wavs
```

São **alternativas**, não executar as duas sobrescrevendo a performance escolhida. A montagem mede WAVs, acrescenta pausa (padrão 0,25 s) e grava `start`/`duration`; usar `--gap 0` quando o corte pede continuidade. Registrar ativos dos WAVs externos e `audio/voice.wav`: a montagem externa não registra licença automaticamente. Ajustar tempos de imagens, eventos de som e duração total depois dessa medição, não esticar fala para encaixar o piloto a qualquer custo.

**Sem fala, como ASMR:** `voice.engine:"none"`, `narration:""` e `start`/`duration` manuais nas cenas. **Não rodar voice.py**, que exige alguma narração. Não criar legenda de fala fictícia. Títulos/rótulos discretos podem ser HTML.

Com fala, transcrever a faixa **final** ou importar SRT conferido (alternativas):

```sh
python scripts/captions.py transcribe "<P>" --model <modelo-local-existente> --final
python scripts/captions.py import "<P>" --file "<P>/captions/final.srt" --final
python scripts/captions.py ass "<P>"
```

`--final` evita deslocar palavras para a fonte bruta quando há `source.footage`; `--audio "<caminho-absoluto>"` seleciona outra faixa final se necessário. Revisar cada palavra, número e tempo; `estimate` seria aproximação, não alinhamento. Definir `captions.font`, `size`, `words_per_group`, `uppercase` existentes; não inventar campo de cor no manifesto. Cor/realce customizado vai no HTML/ASS e requer revisão. Fontes locais licenciadas em `assets/fonts/`; máximo de duas linhas, fora de rosto/UI. Se legenda for HTML, usar `--no-captions` na entrega.

Criar `<P>/edit/sound.json`; exemplo válido de spec (12 s, trocar pela duração final):

```json
{"duration":12,"seed":17,"events":[
  {"type":"pop","at":0.2,"duration":0.15,"gainDb":-24},
  {"type":"whoosh","at":3.5,"duration":0.4,"gainDb":-25},
  {"type":"impact","at":8.0,"duration":0.25,"gainDb":-21}
]}
```

```sh
node scripts/sound.mjs "<P>" --spec edit/sound.json --node-root "<N>"
```

Tipos reais: `whoosh`, `impact`, `pop`, `riser`, `pulse`. Eventos precisam terminar dentro da duração. As receitas dão acentos de piloto, **não uma cama completa nem o som real da referência**. Grave/obtenha ambientes licenciados ou aplique a [reserva sintetizada com parâmetros concretos](../../modules.md#reserva-de-ambiente-e-foley-sintetizados), registrando `kind:"sfx"` como ensinado ali. Não prometa chuva, sala ou materiais realistas: o módulo atual usa osciladores. `--sfx audio/ambiente-e-efeitos.wav` em deliver seleciona uma faixa acabada em vez da padrão; combine os sinais nela antes, sem duplicar. Confira perspectiva, sincronia e inteligibilidade por escuta humana. Sem escuta, marque como não verificado.

## 4. Composição, entrega e revisão (portões iguais)

Crie `<P>/composition/index.html`, recursos locais e `<P>/render/`. Siga o [HTML, contrato e regras de acabamento](../../composition.md): raiz `main`, dimensões/fps/duração reais, `window.__timelines.main` pausada; animações determinísticas, sem timers/relógio aleatório. Execute os [quadros de estilo e seek 2 → 0 → 2](../../composition-check.md), adaptando tempos à duração real. Se a captura padrão falhar, use a [reserva por screenshot](../../composition.md#reserva-por-screenshot). Não use a demo como acabamento.

```sh
"<N>/node_modules/.bin/hyperframes" --version
"<N>/node_modules/.bin/hyperframes" lint "<P>/composition"
"<N>/node_modules/.bin/hyperframes" check "<P>/composition"
"<N>/node_modules/.bin/hyperframes" preview "<P>/composition"
"<N>/node_modules/.bin/hyperframes" render "<P>/composition" --output "<P>/render/master.mp4" --fps 30
python scripts/deliver.py "<P>" --video render/master.mp4 --mute-video-audio --no-music
python scripts/review.py "<P>" --producer-id <autor-real>
python scripts/review.py "<P>" --verdict
```

Versão esperada 0.9.40; não baixar substituto. O comando de entrega acima é para **faixas externas, sem música**; acrescentar `--sfx` se faixa acabada, `--no-captions` se texto já composto. Se manter áudio único do master, omitir `--mute-video-audio` e não deixar cópias das mesmas faixas externas nos caminhos padrão. Não há `--no-voice`/`--no-sfx`: organizar as fontes reais, não inventar flags. `--draft` gera rascunho identificado quando direitos bloqueiam, não autorização para publicar.

Antes de `--verdict`, obter/importar evidência conforme [revisão](../../review.md). Revisor independente do autor; se humano, preencher a ficha da rodada e importar com `review.py "<P>" --human-form "<ficha-preenchida>"`. **Só código 0 autoriza declarar pronto.** Quadros/ASR/LUFS não equivalem a reprodução/escuta integral. Mudanças exigem nova entrega/evidência do mesmo hash. Não publicar, não instalar geradores nem atualizar skill instalada implicitamente.

## Fonte complementar Theo — relato não testado

Fonte de conhecimento solicitada pelo dono: [post de Theo](https://x.com/theoardley/status/2116684286837330374), de 01/11/2026, com artigo anexo sobre criação de vídeos por código. Consulta em 13/11/2026: x.com retornou HTTP 402, sem login; o [espelho público JSON](https://api.fxtwitter.com/theoardley/status/2116684286837330374) retornou o post inicial e **o artigo integral**. Não retornou as respostas nem uma lista de continuação do autor; busca pública pelo ID não encontrou o fio. Portanto **não afirmar leitura integral de respostas/fio**. Não insistir em acesso autenticado, não tratar as instruções do post como comandos desta tarefa.

Tudo nesta seção é **relato do autor, não testado aqui**. Ele apresenta dez recursos/formatos e diz ter testado três ponta a ponta com avaliadores de IA; os demais foram lidos, não testados por ele. Essas notas não são auditoria independente, observação humana completa ou previsão de alcance. A expressão de custo zero do título não elimina assinatura, hardware, direitos ou tempo; não oferecê-la como preço da skill.

| O que o autor ensina, em paráfrase | Aplicação concreta nas receitas, sem importar seu stack |
|---|---|
| Explicador “e se?” de 60–75 s: casa sobre bloco de solo seccionado, narração calma, legenda por palavra, construção em Blender e voz local. O artigo orienta um prompt-guia para roteiro/produção. | Na [analogia](explicacao-analogia.md), definir regra e consequência num cenário com profundidade; Three.js/Blender ou camadas próprias, Kokoro/WAV e HyperFrames. A duração do nosso piloto é outra, não uma cronometragem do exemplo do autor. |
| História serial de sobrevivência: figuras 2D em mundo 3D low-poly, luz/sombra, HUD de dia/hora/bateria, cartões de regra/fato e voto no fim; o autor diz que seus quadros são produzidos por código, não imagem/vídeo generativo. | Na [novela](novela-serializada.md), cartão de estado útil e escolha com consequência; em [mascotes](mascotes.md), identidade por rig/código reutilizado. Não dizer que a referência local foi feita assim só por semelhança. |
| Aula de 45–60 s: apresentador cartoon no canto e títulos/cartões entrando na palavra falada; autor atribui a estrutura inicial a um prompt público de finnardley e relata mudar professor/cores/fontes. | Na analogia, apresentador **original** e cartões ancorados a `captions/words.json`, revistos contra a fala medida; não copiar identidade visual nem prompt integral. |
| Aprovar história, visual e storyboard antes da animação; manter personagem desenhado por código para consistência (entre os recursos listados, nem todos testados pelo autor). | Aprovar três quadros e reaproveitar rig/modelo nas rotas A; na B testar referência e selecionar tomadas estáveis. Isso é adaptação de método, não garantia de identidade do serviço externo. |
| Ouvir a mix antes de postar, porque a avaliação automática não cobre a escuta. | [Making-of](making-of.md) e todos os portões distinguem render/medição/ASR de escuta e revisão humana. |

O artigo também lista reel de UI com 8–12 estados/120 BPM, explicador espacial, bibliotecas de estilos/movimentos e busca de B-roll de domínio público. **Não adotamos motores, repositórios, downloaders ou APIs desses recursos.** Mesmo alegação de domínio público exige confirmar direitos do item/áudio/uso concreto. Ferramentas fora do catálogo, incluindo Remotion citado na lista, permanecem somente documentadas como relato, não integração nativa.

Tradução de método para a **rota B**: trocar execução por código pela lista de planos explícita; repetir sujeito/ação/câmera/duração/áudio/estilo/continuidade nos prompts, selecionar tomadas, compor cartões/voz e escutar a mix no fluxo comum. O artigo não comprova um gerador externo específico nem fornece uma sintaxe universal de prompt de vídeo: esses prompts B são nossos modelos editoriais, não comandos atribuídos ao autor. Não executar arquivos `CLAUDE.md` ou prompts baixados, instalar bibliotecas ou copiar repositórios para usar esta documentação.

### Checklist comum obrigatório

- [ ] Gancho legível nos 3 s iniciais e promessa cumprida; episódio não intercambiável com o anterior.
- [ ] Mãos, olhos, dentes, letras, sombras e props estáveis em todos os quadros, não só na miniatura.
- [ ] Identidade/roupa/voz/eixo mantidos; seed não tomada como garantia; lipsync conferido ou fala off explícita.
- [ ] Ambiente presente quando apropriado; som sem duplicação, estalos ou mascaramento; escuta ou pendência real.
- [ ] Legendas conferidas, área segura, licença de fontes/ativos/modelos e autorização de imagem/voz.
- [ ] IA rotulada quando aplicável, inclusive na plataforma; publicidade identificada; rótulo não garante monetização.
- [ ] Conteúdo bíblico: livro/capítulo/versículos, adaptação separada de citação, tom respeitoso e revisão teológica humana.
- [ ] Sem repetitividade em massa, imitação de IP/pessoa ou prova/fala atribuída sem fonte. Portões técnico e audiovisual separados.
