# Formatos virais com IA — catálogo editorial

Use como repertório de roteiro, não como promessa de viralização nem integração de ferramentas. Os nomes descrevem formatos, não novos valores de `format`: use `storytelling`, `narrado` ou o fluxo de origem. Leia [pesquisa](../research.md), [ganchos](../marketing.md), [animação](animacao.md) e [plataformas](../platforms.md) conforme o pedido.

## Limite do stack

Os originais virais da pesquisa usam geradores de vídeo externos, como Veo 3, Kling e Seedance, que **não fazem parte do stack**. Não oferecer reprodução técnica equivalente como recurso nativo. Com o stack atual, executar imagens ComfyUI + motion/paralaxe, 3D Three.js/Blender, animação 2D e narração Kokoro, com composição HyperFrames + GSAP. Para som, usar Tone.js, gravações/ativos licenciados e a mixagem existente; sem instalar nada para seguir este catálogo.

Clipes gerados fora e fornecidos pelo usuário entram como **ativos fornecidos**, do mesmo modo que WAVs externos: registrar origem, licença, consentimento quando pertinente e rótulo de IA em `assets`/`publish`. A skill não chama esses serviços. Adicionar um gerador é decisão do dono, não uma etapa implícita deste guia; `assets/stack.json` permanece inalterado.

Separe geração, seleção humana e montagem. Agrupe tomadas por cenário/identidade, confira continuidade e trate ambiente sonoro como etapa própria. As alternativas abaixo adaptam a mecânica editorial ao stack, não simulam capacidades ausentes. Sem ativos essenciais, entregar plano/animatic identificado ou pedir os ativos, sem declarar um vídeo final aprovado.

## Catálogo e pilotos

Todas as durações e sequências abaixo são **PROPOSTAS editoriais de piloto**, não cronometragem nem descrição plano a plano dos originais. Medir voz/performance antes de fechar tempos; seguir os portões normais do [pipeline](../pipeline.md).

### Bíblia em POV/selfie — piloto de 20–40 s

- **Mecânica:** personagem relata o evento como vlog, em primeira pessoa e já dentro do conflito.
- **Piloto proposto:** identificar passagem → abrir no perigo/contradição → relato de uma decisão → consequência e recompensa → pergunta ligada ao próximo episódio. Linguagem local pode aproximar a história sem alterar o sentido da passagem.
- **Som:** Kokoro para relato, ambiente próprio do cenário e efeitos pontuais; manter fala inteligível, sem usar a mix como caricatura da fé.
- **Risco:** precisão, sexualização e blasfêmia são críticas registradas no levantamento fornecido; ver os limites de confirmação na fotografia da pesquisa. Exigir passagem identificada (livro, capítulo e versículos), tom respeitoso e revisão teológica humana antes da produção; distinguir adaptação de citação literal. Não inventar fala como se constasse da Escritura.
- **Stack atual:** imagem ComfyUI com composição de selfie, recortes/paralaxe e atuação 2D/3D quando viável. Não prometer selfie falante fotorrealista ou lip-sync nativo; clipe externo só como ativo fornecido.

### Bíblia cinematográfica narrada — piloto de 25–50 s

- **Mecânica:** narração conduz uma passagem por imagens de escala, conflito e consequência.
- **Piloto proposto:** passagem identificada → imagem de conflito → decisão central → consequência → fechamento coerente com o texto, sem prometer revelação inexistente.
- **Som:** Kokoro, ambiente em camadas e contraste entre respiro e impacto; música não encobre nomes ou citações.
- **Risco:** aplicar as mesmas exigências de passagem identificada, tom respeitoso e revisão teológica humana. Rever precisão, sexualização e blasfêmia; imagem dramática não é evidência histórica nem interpretação teológica validada.
- **Stack atual:** imagens ComfyUI + câmera virtual/paralaxe, cenários 3D Three.js/Blender e composição HyperFrames; identificar limites de movimento e não vender um slideshow como cena generativa contínua.

### Criaturas/personagens fazendo vlog — piloto de 15–30 s

- **Mecânica:** criatura absurda trata seu cotidiano/conflito como um vlog pessoal.
- **Piloto proposto:** problema concreto em primeira pessoa → tentativa que revela a personalidade → reversão → convite para escolher a próxima situação.
- **Som:** voz Kokoro, ambiente coerente e efeitos de interação sincronizados; não depender só de música.
- **Risco:** identidade instável entre planos, confusão com registro real e imitação de personagem protegido. Criar personagem próprio e rotular IA realista quando aplicável.
- **Stack atual:** modelo/personagem 3D ou recortes 2D com referência fixa; ComfyUI para fundos e poses selecionadas, sem prometer continuidade automática ou lip-sync.

### ASMR impossível — piloto de 8–15 s

- **Mecânica:** macro de uma ação/material impossível, **sem fala**, com som sincronizado ao contato visual.
- **Piloto proposto:** apresentar textura/objeto → uma transformação legível → detalhe da reação → fechamento ou loop que não esconda defeitos.
- **Som:** desenhar contato, corte e ressonância com Tone.js ou ativos licenciados; sincronizar cada gesto e conferir em escuta. Não há narração Kokoro neste formato.
- **Risco:** som fora de sincronia, textura incoerente ou ação que pareça instrução real perigosa. Não apresentar objeto sintético como material real testado.
- **Stack atual:** macro 3D em Three.js/Blender para ação e materiais; imagens ComfyUI + motion apenas quando a ação puder ser representada sem deformação contínua. Relatar que a sensação tátil depende de revisão audiovisual.

### Novela/reality serializada com personagens absurdos — piloto de 45–75 s

- **Mecânica:** personagens recorrentes disputam relações/objetivos; consequência e decisão do público sustentam episódios, não apenas a troca de aparência.
- **Piloto proposto:** conflito já em andamento → posições dos personagens → escolha/reversão → recompensa parcial → pergunta concreta para o próximo episódio.
- **Som:** vozes Kokoro selecionadas de modo consistente, ambientes por cenário e sinais de reação; conferir separação e inteligibilidade.
- **Risco:** repetição em massa, relações que mudam sem causa, sexualização e cópia de marca/formato protegido. Criar universo próprio e variar a substância narrativa; ver regras de monetização/distribuição em plataformas.
- **Stack atual:** personagens 2D/3D reutilizáveis, cenários agrupados e montagem HyperFrames. Para múltiplas falas, medir cada performance; não prometer diálogo generativo contínuo.

### Mascotes consistentes em minissérie — piloto de 30–60 s

- **Mecânica:** reconhecimento de uma identidade estável em situações com evolução.
- **Piloto proposto:** apresentar desejo pelo conflito, não por ficha do personagem → obstáculo → decisão com consequência → gancho da relação para o próximo episódio.
- **Som:** fixar voz Kokoro, intenção/performance e assinatura sonora; ambientes variam com o cenário.
- **Risco:** deriva visual/vocal e episódios intercambiáveis. Fixar **aparência, voz, personalidade e relações** numa bíblia da série; conferir cada tomada e não tratar semente fixa como garantia de identidade.
- **Stack atual:** modelos Three.js/Blender ou rig/recortes 2D consistentes; ComfyUI para referências selecionadas. Reutilizar ativos aprovados, não repetir o mesmo episódio com outra legenda.

### Making-of híbrido — piloto de 30–60 s

- **Mecânica:** resultado primeiro, depois demonstrar a contribuição humana e técnica.
- **Piloto proposto:** resultado → performance → geração → edição → comparação final. Registrar o processo realmente executado, com trechos de tela/arquivos autorizados.
- **Som:** performance/voz original autorizada ou Kokoro, áudio de bastidor útil e ambiente como camada separada; evitar duplicar música na mix.
- **Risco:** encenar processo inexistente, esconder origem externa ou sugerir autoria/licença que não existe. Diferenciar demonstração ilustrativa de registro real.
- **Stack atual:** gravações fornecidas + imagens ComfyUI, cena 2D/3D e timeline HyperFrames. Se o resultado for clipe externo fornecido, atribuir sua origem; não atribuir geração a esta skill.

### ALERTA — quiz/fanfic de fé em massa

- **Mecânica descrita:** variações de perguntas e histórias de fé produzidas em escala; registrar como alerta, **não como modelo a replicar**.
- **Piloto:** não propor piloto de produção em massa. Se o pedido for educativo, reformular como peça autoral com passagem/fonte identificada e revisão humana, sem automatizar variações vazias.
- **Som:** voz/ambiente não corrigem falta de originalidade ou erro teológico; não escolher um pacote sonoro como justificativa para escala.
- **Risco:** remoções de canais foram reportadas no YouTube em **jan/2026**. O relato não prova que todo quiz de fé será removido nem que o rótulo de IA resolve monetização; separar notícia de regra oficial.
- **Stack atual:** nenhuma automação adicional nem motor novo. Uma eventual peça educativa individual segue o pipeline narrado e as mesmas exigências de fontes, direitos e revisão.

## Fotografia da pesquisa (13/11/2026)

Instantâneo que envelhece, não métrica atual ou garantida. **Os vídeos não foram assistidos**; os números abaixo são das fontes, conforme o levantamento fornecido, não de analytics próprios ou contagem independente. Não inferir retenção, receita, qualidade audiovisual ou causalidade a partir deles. Técnicas são atribuídas às fontes, não detectadas por inspeção dos vídeos.

| Exemplo | Relato datado do levantamento | Fonte / limite |
|---|---|---|
| holyvlogsz — Daniel | 6,1 mi de views em 3 dias, jun/2025; Veo 3 | [Know Your Meme — AI Bible influencer videos](https://knowyourmeme.com/memes/ai-bible-influencer-videos-ai-bible-stories) |
| The AI Bible / Pray.com | ≈1,3 mi de seguidores no Instagram no levantamento; entrevista de set/2025; fluxo declarado LLM → roteiro humano → Midjourney → animação | [Christianity Today — entrevista AI Bible](https://www.christianitytoday.com/?p=361821); a cifra do levantamento diverge da entrevista e não foi confirmada; processo declarado não é integração da skill |
| Vlog Bíblico BR | ≈46 mi de views no TikTok, jul/2025; Veo 3 → Premiere → ambiente sonoro | [Folhapress / Diário do Pará](https://diariodopara.com.br/noticias/brasil/videos-de-ia-sobre-a-biblia-viralizam-e-viram-tema-de-mentoria/) |
| Bíblia Carioca | Vídeos com 4 mi+ de views, jun/2025, conforme levantamento | Fonte específica pendente; o registro de Know Your Meme citado para o gênero não confirma este exemplo |
| Bigfoot vlogs | 6,3 mi de plays, jun/2025 | [Know Your Meme — AI Bigfoot and Yeti vlogs](https://knowyourmeme.com/memes/ai-bigfoot-and-yeti-vlogs) |
| ASMR de vidro | 67,4 mi de views, jun/2025 | [Fast Company](https://www.fastcompany.com/91353440/ai-generated-asmr-is-taking-over-tiktok) |
| Fruit Love Island | 27 mi de views por episódio, mar/2026, no levantamento; generalização não confirmada, não usar como média | [Know Your Meme — AI Fruit Love Island](https://knowyourmeme.com/memes/ai-fruit-love-island) atribui 27 mi a um episódio específico, não a todos; Complex (mar/2026; URL específica não localizada nesta atualização) |
| Mascotes chineses | ≈1,8 mi de seguidores, nov/2026 | Xinhua (10/11/2026; URL específica não localizada nesta atualização) |

A bibliografia fornecida inclui [Complex](https://www.complex.com/) e [Xinhua](https://www.news.cn/); os links gerais não comprovam os números. Preservar essas duas atribuições como relatos do levantamento com conferência pendente, sem inventar URLs de matérias. A entrevista de Christianity Today documenta questões de precisão e sexualização. A crítica de blasfêmia consta no levantamento fornecido, mas não foi localizada nos textos consultados; manter atribuição e conferência pendente, sem tratar como avaliação dos vídeos feita aqui. O alerta de remoções tem cobertura sobre a ação reportada em janeiro, por exemplo [YouTube Removes Major “AI Slop” Channels](https://www.gizchina.com/youtube/youtube-removes-major-ai-slop-channels-after-study-reveals-billions-of-views); não usar notícia como diagnóstico de um canal específico sem evidência.

Ao atualizar, guardar fonte/data, tipo de evidência e incerteza na [ficha de referência por plano](../research.md#ficha-de-referência-por-plano). Estudar exemplos não concede direitos de reutilização, de voz/imagem ou de marca.
