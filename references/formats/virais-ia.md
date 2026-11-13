# Formatos virais com IA — guia de como fazer

Receitas de produção, não promessa de viralização. Cada capítulo contém roteiro preenchível, exemplo original pt-BR, continuidade, duas rotas de produção e checklist. Os nomes editoriais **não são novos valores de `format`**: use `storytelling`, `narrado` ou o fluxo de origem.

## Limite do stack

Os geradores externos citados pela pesquisa, como Veo 3, Kling e Seedance, **não fazem parte do stack**. A rota A ensina imagens ComfyUI + motion/paralaxe, recortes/2D ou Three.js/Blender, narração Edge TTS e composição HyperFrames + GSAP. Não promete geração nativa de vídeo contínuo nem lip-sync automático. Tone.js gera efeitos; ambientes e performances podem ser ativos próprios/licenciados.

A rota B ensina a dirigir clipes em um gerador **à escolha do usuário**, fora da skill. A skill não chama esse serviço: recebe arquivos, registra origem/licença/consentimento e rótulo de IA, seleciona e compõe. **Adicionar um gerador é decisão do dono**; não alterar `assets/stack.json`, instalar motores ou simular integração. Sem recursos essenciais, registrar bloqueio; produzir animatic identificado somente se esse escopo já estiver aceito, sem anunciá-lo como final aprovado.

## Como usar as receitas

1. Leia o [procedimento executável comum](virais-ia/producao.md), parte integrante das oito receitas: comandos conferidos, manifesto, prompts, importação, composição, mix e portões.
2. Escolha um capítulo e execute sua rota A **ou** B junto com o procedimento comum. Durações são alvos de pilotos originais; medir performance antes de fechar cenas.
3. Faça três quadros de estilo, selecione tomadas e revise continuidade antes de renderizar tudo. Geração, seleção humana e montagem são etapas distintas.

| Formato | Receita | Piloto proposto |
|---|---|---|
| Bíblia em POV/selfie | [Testemunha ficcional contextualizada](virais-ia/biblia-pov.md) | 28 s |
| Bíblia cinematográfica narrada | [Passagem em imagens de escala](virais-ia/biblia-cinematografica.md) | 36 s |
| Criaturas em vlog | [Cotidiano de uma criatura original](virais-ia/criaturas-vlog.md) | 24 s |
| ASMR impossível | [Material impossível, sem fala](virais-ia/asmr-impossivel.md) | 12 s |
| Novela serializada | [Conflito e consequência recorrentes](virais-ia/novela-serializada.md) | 54 s |
| Mascotes consistentes | [Minissérie com identidade fixa](virais-ia/mascotes.md) | 36 s |
| Making-of híbrido | [Resultado e processo comprovável](virais-ia/making-of.md) | 40 s |
| **Novo: explicação por analogia encenada** | [Apresentador cartoon + mundo simbólico](virais-ia/explicacao-analogia.md) | 42 s |

### Exemplo trabalhado, não receita copiada

A [ficha por plano da referência fornecida](virais-ia/exemplo-planos.md) separa observado, inferido, evidência e confiança. Foram inspecionados quadros e medido/transcrito o arquivo local, **sem escuta nem reprodução audiovisual integral**. O exemplo descreve genericamente o vídeo; nenhum vídeo, quadro, identificação de pessoa ou fala integral é incorporado ao repositório. As receitas usam histórias e personagens próprios, não os da referência.

### ALERTA — quiz/fanfic de fé em massa

Não é um nono formato a automatizar. Remoções de canais foram reportadas em jan/2026; isso não prova que todo quiz será removido nem que rotular IA garante monetização. Reformular eventual pedido educativo como peça autoral com fonte/passagem identificada e revisão humana. Não ensinar variações vazias em escala; voz e acabamento não corrigem erro teológico ou falta de originalidade.

## Fotografia da pesquisa (13/11/2026)

Instantâneo que envelhece, não analytics próprios ou garantia de receita. **Os vídeos públicos da tabela não foram assistidos**; são relatos documentais. A inspeção do arquivo local é outro tipo de evidência, delimitado na ficha trabalhada. Números e processos abaixo são atribuídos às fontes; não deduzir retenção, qualidade ou causalidade.

| Exemplo | Relato datado | Fonte / limite |
|---|---|---|
| holyvlogsz — Daniel | 6,1 mi de views em 3 dias, jun/2025; Veo 3 atribuído pela fonte | [Know Your Meme](https://knowyourmeme.com/memes/ai-bible-influencer-videos-ai-bible-stories) |
| The AI Bible / Pray.com | ≈1,3 mi de seguidores no levantamento; entrevista set/2025; processo declarado LLM → roteiro humano → Midjourney → animação | [Christianity Today](https://www.christianitytoday.com/?p=361821); cifra diverge da entrevista, não confirmada; processo não é integração da skill |
| Vlog Bíblico BR | ≈46 mi de views no TikTok, jul/2025; fluxo declarado Veo 3 → Premiere → ambiente | [Folhapress / Diário do Pará](https://diariodopara.com.br/noticias/brasil/videos-de-ia-sobre-a-biblia-viralizam-e-viram-tema-de-mentoria/) |
| Bíblia Carioca | Matéria de 02/06/2025 relata vídeos que ultrapassaram 4 mi de views; não informa seguidores nem identifica gerador | [Hardware.com.br](https://www.hardware.com.br/tecnologia/perfil-do-tiktok-usa-ia-para-recriar-momentos-biblicos-com-humor-e-divide-opinioes/amp/), aberta em 13/11/2026; não ler como média de todos os vídeos |
| Bigfoot vlogs | 6,3 mi de plays, jun/2025, conforme levantamento | [Know Your Meme](https://knowyourmeme.com/memes/ai-bigfoot-and-yeti-vlogs) |
| ASMR de vidro | 67,4 mi de views, jun/2025, conforme levantamento | [Fast Company](https://www.fastcompany.com/91353440/ai-generated-asmr-is-taking-over-tiktok) |
| Fruit Love Island / novelas de frutas | Levantamento generalizava 27 mi por episódio; KYM atribui a um episódio específico. Complex (23/03/2026) relata **outro vídeo específico**, de trombonechef, com mais de 26 mi | [KYM](https://knowyourmeme.com/memes/ai-fruit-love-island) e [Complex](https://www.complex.com/pop-culture/a/backwoodsaltar/ai-cheating-fruit-videos), esta aberta em 13/11/2026; não são uma média nem necessariamente a mesma série; gerador não nomeado pela Complex |
| Mascotes chineses | Xinhua (10/11/2026): Maoziqi com ≈1,8 mi de seguidores **somando plataformas**, ≈670 mil no Bilibili; 92 vídeos ali com mais de 92 mi de views acumuladas | [Xinhua](https://english.news.cn/20261110/930fe7b7745f48ce9422ff73e67db6bd/c.html), aberta em 13/11/2026; atribui Seedance ao criador, não a todo o gênero nem à referência local |

Fonte complementar: [post/artigo de Theo](https://x.com/theoardley/status/2116684286837330374), consultado inicialmente via [espelho público](https://api.fxtwitter.com/theoardley/status/2116684286837330374) e depois diretamente no Chrome autorizado. **Relato do autor, não testado aqui**: fluxo por código, 2D em 3D, HUD/decisão episódica, cartões sincronizados e escuta da mix. Escopo/datas e limites de leitura estão no [procedimento comum](virais-ia/producao.md#fonte-complementar-theo--relato-não-testado); a biblioteca de movimentos citada também orienta o novo [pacote de câmera/referências](../camera-references.md). Leitura do artigo não equivale a assistir/escutar os vídeos ou testar receitas. Não importamos seu código, configurações, motores ou pontuações como validação.

As três URLs antes pendentes foram abertas; isso confirma o conteúdo das reportagens, não auditoria independente das métricas. Xinhua descreve tentativas, seleção/correções e roteiros próprios de Maoziqi; outros entrevistados usam IA para ideias. Complex não documenta pipeline reproduzível e discute conteúdo violento/potencialmente racista: não copiar esse conteúdo para obter a mecânica serial.

Hardware.com.br registra críticas de desrespeito religioso e palavrões. Christianity Today discute precisão e sexualização. A palavra/atribuição específica de **blasfêmia** do levantamento permanece sem confirmação literal: não converter as críticas em diagnóstico próprio dos vídeos. O alerta de jan/2026 tem [cobertura jornalística](https://www.gizchina.com/youtube/youtube-removes-major-ai-slop-channels-after-study-reveals-billions-of-views), não substitui regras oficiais de [plataforma](../platforms.md).

Ao atualizar, guardar fonte/data, tipo de evidência e incerteza na [ficha de referência por plano](../research.md#ficha-de-referência-por-plano). Estudar exemplos não concede direitos de reutilização, imagem/voz, marca ou personagens. Consulte também [pesquisa](../research.md), [direção](../direction.md), [composição](../composition.md) e [revisão](../review.md).
