# Outros formatos (núcleo, guia em construção)

Estes formatos já têm projeto (`new_project.py --format ...`), entrega e revisão, mas ainda não têm script nem guia próprio. Monte-os com as peças existentes, como descrito abaixo, e diga no relatório que o formato está em construção.

## Produto (`produto`)

Divulgação de produto ou serviço do usuário. Narrado (voz sintética é o padrão) ou com gravação.

- Estrutura: problema que o público sente (0–3 s) → produto resolvendo, mostrado em uso → prova (número, antes e depois real, demonstração) → oferta e CTA. Até 30 s para anúncio, até 60 s orgânico.
- Visual: imagens e vídeos do produto fornecidos pelo usuário como B-roll; motion em código para preço, benefícios e comparação ([motion](../motion.md)). Sem imagem do produto, peça; não gere imagem de produto que finja ser o real.
- `publish.ad_disclosure`: `true` quando é publicidade (própria ou paga). O `deliver.py` avisa se ficar vazio.

## UGC (`ugc`)

Vídeo no estilo de cliente ou criador falando para a câmera: gravação do usuário, de influenciador contratado ou avatar.

- Edite como [gravação própria](gravacao.md): cortes secos, zoom alternado, legenda grande, gancho em primeira pessoa ("Eu não acreditava que...").
- Formatos que funcionam: reação, antes e depois, "3 coisas que", unboxing, tutorial rápido, objeção respondida.
- Influenciador: registre a autorização de uso da imagem e o prazo em `assets`. Publi sempre com `ad_disclosure` e marcação de parceria paga.
- **Avatar UGC de IA:** pode apresentar o produto, mas não pode se passar por cliente real nem dar depoimento de resultado ("perdi 10 kg"). Marque `publish.ai_label`.

## Storytelling animado (`storytelling`)

História narrada com cenas ilustradas ou animadas (fábula, caso real, mistério, curiosidade histórica).

- Use o [pipeline narrado](../pipeline.md) com [direção](../direction.md) de estilo de ilustração consistente: mesma paleta, personagens com folha de referência (mesma descrição e semente no ComfyUI) para não mudarem de cena para cena.
- Estrutura: gancho no conflito (não no "era uma vez") → escalada → reviravolta → final que pede comentário ou parte 2. Série com "parte 1, 2, 3" segura seguidores.
- Câmera sempre viva sobre as ilustrações (Ken Burns, paralaxe em camadas); efeitos sonoros de ambiente.

## Canal de música com IA (`musica`)

Visualizer, lyric video, clipe animado ou loop para música gerada.

- Música: ACE-Step (1.5 sob MIT) para uso comercial; MusicGen só sem monetização. Música de serviço (Suno, Udio) só com plano que dá direito comercial; registre o plano em `assets`.
- Visual: o tempo vem da batida, não de narração. Extraia o andamento e os ataques do áudio (FFmpeg `astats` ou `ebur128` por janela) e sincronize cortes e pulsos a eles. Lyric video usa `captions.py transcribe` na faixa com voz.
- Vertical: o trecho mais forte (refrão ou drop) nos primeiros 2 s; 15–30 s para usar como som em outros vídeos.
- Plataformas exigem declarar música gerada por IA em alguns casos; marque `publish.ai_label`.

## Avatar de IA (`avatar`)

Apresentador digital falando um roteiro (canal dark com rosto, explicativo, divulgação).

- Avatar só da imagem e voz do próprio usuário ou de quem consentiu por escrito, ou de personagem claramente fictício. Nunca de pessoa pública ou conhecida sem autorização.
- Fluxo: roteiro e voz como no [pipeline narrado](../pipeline.md); o vídeo do avatar (ferramenta local ou serviço escolhido pelo usuário, nunca instalada sem aprovação) entra como gravação em `footage.py import`; daí em diante é edição de gravação com B-roll a cada 3–5 s para não ficar só no rosto sintético.
- Sempre `publish.ai_label: true` quando o avatar parece uma pessoa real.
