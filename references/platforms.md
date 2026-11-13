# Plataformas

`deliver.py` exporta no tamanho do formato de tela do projeto: H.264 High, `yuv420p`, 30 fps (ou 60 se a animação pedir), AAC 48 kHz, `+faststart`, -14 LUFS. Um vertical serve às quatro plataformas verticais; para 16:9 e feed, crie outro projeto a partir da mesma gravação ou roteiro.

## Formato de tela e duração

| Plataforma (`platforms`) | Formato de tela | Limite usado nas checagens | Observação |
|---|---|---|---|
| TikTok (`tiktok`) | 9:16 | 600 s | Envio pelo app; vídeo curto continua rendendo mais |
| Instagram Reels (`reels`) | 9:16 | 180 s | A grade do perfil mostra um recorte 3:4 do centro |
| YouTube Shorts (`shorts`) | 9:16 (ou 1:1) | 180 s | Acima disso vira vídeo comum |
| Kwai (`kwai`) | 9:16 | 600 s | Público forte em humor, novela, curiosidade e "dicas"; legenda grande e texto direto |
| YouTube (`youtube`) | 16:9 | 12 h | Capítulos e miniatura; veja [vídeo longo](formats/longo.md) |
| Feed do Instagram (`feed`) | 4:5 ou 1:1 | 60 min | 4:5 ocupa mais tela no feed; carrossel de vídeo aceita 1:1 |

| Formato de tela | Tamanho |
|---|---|
| 9:16 | 1080×1920 |
| 16:9 | 1920×1080 |
| 1:1 | 1080×1080 |
| 4:5 | 1080×1350 |

Os limites mudam; confira a central de ajuda de cada plataforma se o vídeo passar de 60 s em vertical. Para alcance em vertical, mire 20–45 s.

## Área segura

**Vertical (9:16).** A interface cobre o topo (abas, perfil), a lateral direita (curtir, comentar, compartilhar) e a base (legenda da publicação, música). O Instagram é o mais restritivo, por isso serve de referência comum:

| Margem em 1080×1920 | Pixels |
|---|---|
| Topo | 250 |
| Base | 420 |
| Esquerda | 90 |
| Direita | 150 |

Área útil: x de 90 a 930, y de 250 a 1500. Legenda com base em y ≈ 1400; títulos no terço superior. Nada essencial fora dela.

**16:9, 1:1 e 4:5.** 5% de margem no topo e nas laterais e 8% na base (barra de progresso e controles). Legenda com base em 90% da altura. No YouTube, o canto inferior direito some sob a marca d'água e os cartões finais nos últimos 5–20 s.

## Volume

Alvo -14 LUFS integrado e pico real até -1 dBTP; as plataformas normalizam perto disso, e áudio mais baixo soa fraco ao lado dos outros vídeos. Fala sempre inteligível sobre a trilha.

## Capa e miniatura

- TikTok, Reels e Kwai: escolha um quadro ou suba uma imagem no tamanho do vídeo; mantenha o texto da capa no centro, porque a grade do perfil recorta.
- Shorts: escolha de miniatura limitada; faça o primeiro segundo funcionar como capa.
- YouTube: miniatura 1280×720 em `publish.thumbnail` ([vídeo longo](formats/longo.md#miniatura)).

## Publicação

`deliver.py` escreve em `out/report.md` o título, a descrição, os capítulos e a marcação de publicidade a partir de `publish`. Hashtags: 3–5 específicas do nicho, não genéricas. A skill não posta; o usuário publica.

## Rótulos de IA e de publicidade

- YouTube, TikTok, Instagram e Kwai pedem que o criador sinalize conteúdo sintético realista (pessoa real dizendo o que não disse, voz clonada, avatar realista, cena que parece filmada). Animação claramente gráfica e narração sintética genérica costumam não exigir, mas as regras mudam: na dúvida, marque `publish.ai_label` e diga ao usuário para ativar o rótulo ao postar.
- Publicidade (produto próprio, publi paga, permuta): marque `publish.ad_disclosure` e use a ferramenta de parceria paga da plataforma. No Brasil, o CONAR exige que a publicidade seja identificável como tal.
