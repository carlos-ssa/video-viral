# Revisão

As rodadas de "assiste, critica, corrige" que normalmente o usuário faz pedindo de novo acontecem aqui, antes da entrega. O objetivo é que o primeiro vídeo que o usuário vê já tenha passado por elas.

## O ciclo

1. **Quadros de estilo** ([direção](direction.md#5-quadros-de-estilo)): 3 quadros parados antes de animar tudo. Corrija o visual aqui, onde é barato.
2. **Render e entrega:** `render/master.mp4`, depois `scripts/deliver.py`. A revisão olha o arquivo entregue, com legenda e som, porque é ele que o público vê.
3. **Rodada de revisão:** `python scripts/review.py <projeto>`. Gera `review/rNN/` com `grid.jpg`, `hook.jpg`, `report.md` e `metrics.json`.
4. **Olhe as imagens** `hook.jpg` e `grid.jpg` (leia os arquivos de imagem; não julgue só pelas métricas) e preencha a tabela de notas do `report.md` com nota e correção por critério.
5. **Veredito:** `python scripts/review.py <projeto> --verdict` lê a tabela da última rodada. Sai com 0 quando todas as notas são 4 ou mais e não há bloqueante; só então o vídeo está pronto. Com 1, escolha as 3 correções de maior efeito, aplique, renderize, entregue e volte ao passo 3, sem perguntar ao usuário. Com 2, falta preencher nota.
6. **Pare em 3 rodadas.** Na terceira sem aprovar, o veredito sai com 3: entregue o melhor resultado e diga no relatório final o que ficou abaixo de 4 e por quê.

Seja honesto na nota: dê 3 quando o critério da coluna 3 descreve o vídeo, mesmo que a causa seja uma ferramenta que falta (voz do sistema, por exemplo). Aí a rodada seguinte corrige o que dá sem instalar nada (mixagem, efeitos, pausa antes da revelação), e o relatório final diz o que instalar.

Se houver subagentes, a nota fica mais honesta quando quem revisa não foi quem fez: entregue a outro agente as imagens, o `report.md`, o roteiro e a direção, e peça só as notas e as correções. A skill `adaptive-orchestration` organiza isso, se instalada.

## Notas

| Critério | 5 | 3 | 1 |
|---|---|---|---|
| Gancho | Quadro 0 sozinho já dá vontade de ver; texto curto e grande; fala imediata | Gancho bom, mas a imagem só ilustra a fala | Logo, título genérico ou tela vazia no início |
| Ritmo | Evento visual a cada 1,5–3 s, cortes na palavra, nenhum trecho parado | Algum trecho de 3–4 s sem novidade | Slides: imagem parada enquanto a voz fala |
| Direção de arte | Parece uma peça de um mesmo autor: paleta, fontes e textura constantes | Coerente, mas com cara de template | Cores e fontes mudando sem motivo; fonte padrão |
| Motion | Curvas e durações do [motion](motion.md#princípios), foco único, câmera viva | Animação correta mas uniforme (tudo com o mesmo movimento) | Fades lineares, elementos surgindo sem movimento |
| Fala e imagem | Cada imagem acrescenta à frase falada naquele instante | Imagem literal da palavra falada | Imagem sem relação ou fora de tempo |
| Legibilidade | Tudo lido de primeira no celular, dentro da área segura | Algum texto pequeno ou com pouco contraste | Texto cortado, coberto pela interface ou ilegível |
| Som | Efeitos nas entradas, música que respira com a voz, ponto alto no payoff | Música e voz corretas, sem efeitos | Música competindo com a voz ou silêncio |
| Payoff | Entrega exatamente o que o gancho prometeu e fecha em loop ou no ponto alto | Entrega, mas o final arrasta | Não entrega a promessa |

Os critérios mudam com o formato, e `report.md` já traz a tabela certa:

- **Gravação, corte e UGC:** saem Direção de arte, Motion e Fala e imagem; entram **Corte de fala** (5: nenhuma palavra comida, nenhuma retomada, respiro natural; 3: algum corte seco demais ou pausa longa; 1: palavra cortada ou frase repetida) e **Enquadramento** (5: rosto no terço superior, dentro da área segura, zoom alternado; 3: enquadramento fixo correto; 1: rosto cortado ou coberto pela legenda).
- **Vídeo longo (16:9 ou mais de 3 min):** entra **Retenção** (5: promessa nos 30 s e virada a cada 60–90 s; 3: promessa clara, mas algum trecho de mais de 2 min sem virada; 1: introdução longa ou sem promessa), e o Payoff passa a valer para o vídeo inteiro.

A grade tem um quadro por segundo até 48 s; acima disso, `--every` vira `duração/48` (o tempo de cada quadro está escrito nele). Para julgar "Fala e imagem", compare esses tempos com `scenes[].start` e o texto da narração.

## Alertas automáticos

`review.py` sai com código 1 quando há bloqueante:

- primeiro quadro quase preto;
- imagem congelada por 2,5 s ou mais;
- fala começando depois de 0,7 s.

E avisa (sem bloquear) sobre: trechos sem evento visual (mais de 3 s no vertical, 8 s no longo) (corte ou pico de movimento), nada mudando nos 2 primeiros segundos, direção incompleta, cenas sem roteiro de planos ou com mais de 3,5 s por plano, texto do gancho com mais de 6 palavras, legenda na fonte padrão, falta de efeitos sonoros ou de trilha e fala rápida ou lenta demais.

A linha "Movimento por segundo" do relatório mostra a energia de movimento de cada segundo. Vale baixo e plano por vários segundos é o trecho que o público pula.

## Correções que mais rendem

| Problema | Correção |
|---|---|
| Gancho fraco | Troque pelo segundo gancho da lista de `research/direcao.md`; ponha a imagem mais forte do vídeo no quadro 0 |
| Trecho parado | Divida o plano em dois, acrescente aproximação de câmera, texto de ênfase ou um elemento entrando na palavra-chave |
| Cara de template | Aplique textura (grão, vinheta), troque fades por máscaras e curvas `expo`, tire cores fora da paleta |
| Imagem literal | Troque por consequência, contraste ou detalhe do assunto |
| Som chapado | Efeito em cada transição, silêncio curto antes da revelação, ponto alto da música no payoff |
| Final arrastado | Corte as 2 últimas frases ou feche com a frase que liga ao gancho |
