# Cortes de vídeo longo

Live, podcast, aula ou vídeo do YouTube vira vários vídeos curtos. Cada corte precisa funcionar sozinho para quem nunca viu o original: começar com gancho, ter uma ideia completa e terminar num ponto alto.

## Comandos

```bash
python scripts/new_project.py live-maio --format gravacao --aspect 16:9 --dir <pasta>    # o longo
python scripts/footage.py import <longo> live.mp4
python scripts/captions.py transcribe <longo>                         # ou import --file live.srt
python scripts/clips.py suggest <longo> [--min 20 --max 60 --top 10]  # edit/clips.md e edit/clips.json
python scripts/clips.py make <longo> --rank 1 --slug corte-gasto-invisivel [--aspect 9:16]
python scripts/clips.py make <longo> --from 12:40 --to 13:25 --slug corte-manual
```

Cada `make` cria um projeto irmão com formato `corte`, importa só o trecho (com folga de 0,15 s no início e 0,25 s no fim) e leva as palavras junto, sem transcrever de novo. Daí em diante é o fluxo da [gravação própria](gravacao.md): `cut`, ajustar `edl.json`, `frames`, `render`, `ass`, `deliver`, `review`.

## Escolher os cortes

`suggest` monta janelas de frases inteiras e dá nota por gancho na primeira frase (pergunta, número, palavra de impacto), começo que não depende do que veio antes, densidade de fala e fechamento. A nota é um filtro, não a decisão: leia os 5 primeiros em `edit/clips.md` e escolha pelo conteúdo.

Um bom corte tem:

- **Gancho que se entende sozinho.** "Por que isso acontece?" depende de contexto; "Por que 90% perde dinheiro na poupança?" não. Se a melhor frase de abertura está no meio do trecho, mova-a para o topo no `edl.json` do corte.
- **Uma ideia só**, com começo, virada e fecho. Corte que termina em "e aí..." ou pergunta sem resposta frustra.
- **Emoção ou opinião forte**: discordância, número surpreendente, história pessoal, erro comum, previsão. Explicação neutra rende menos.
- **20–45 s** para alcance; até 90 s se a história segura.

Não use dois cortes que contam a mesma coisa na mesma semana. Se o longo repete um tema, escolha a melhor versão.

## Para cada corte

- Texto do gancho na tela no quadro 0 (até 6 palavras), com a mesma promessa/pergunta da fala; siga as [regras de composição](../composition.md#regras-de-acabamento-obrigatórias).
- Use o trecho real do original e a variação de título/moldura exigida em [gravação](gravacao.md#camada-de-acabamento), com a [cadência daquele fluxo](gravacao.md#ritmo-e-cortes). Preserve nome/fonte/marca d'água fora da faixa exclusiva da legenda.
- Legenda palavra a palavra; muita gente assiste sem som.
- Se o original tem duas pessoas, enquadre quem fala em cada trecho (`x` por trecho) ou use 16:9 com `fit` padrão.
- Título e descrição próprios em `publish`, com o link ou nome do vídeo completo na descrição.

## Direitos

Cortes do próprio usuário são livres. Cortes de podcast, live ou vídeo de outra pessoa só com autorização escrita (importe com `--third-party` e registre a licença no ativo); sem isso, o `deliver.py` monetizado bloqueia e o corte sai como rascunho. "Uso justo" não protege corte viral de conteúdo alheio.
