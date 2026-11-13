# Gravação própria

O usuário gravou (celular, câmera, tela com webcam) e quer o vídeo editado para postar. O trabalho é tirar o que não prende, deixar o começo forte, enquadrar para cada plataforma e dar legenda e ritmo, sem mudar o que a pessoa disse.

## Comandos

```bash
python scripts/new_project.py meu-video --title "..." --format gravacao --aspect 9:16 --dir <pasta>
python scripts/footage.py import <projeto> gravacao.mp4 [--from 0:12 --to 3:40]   # áudio limpo em audio/source.wav
python scripts/captions.py transcribe <projeto>          # ou: captions.py import <projeto> --file legenda.srt
python scripts/footage.py cut <projeto>                  # silêncios + vícios -> edit/edl.json e edit/transcript.md
python scripts/footage.py frames <projeto>               # edit/frames.jpg para conferir o enquadramento
python scripts/footage.py render <projeto>               # base A-roll em render/master.mp4
# Componha o acabamento em HyperFrames/Remotion/FFmpeg, conforme tool_plan, em render/final.mp4
python scripts/captions.py ass <projeto>
python scripts/deliver.py <projeto> --video render/final.mp4
python scripts/review.py <projeto>
```

O A-roll renderizado é uma base, não uma prova automática de acabamento. Use direção, B-roll, composição, animação e som conforme a peça; não é necessário misturar motores redundantes. Para um pedido pontual, preserve o resto da edição. Se as legendas já estiverem na composição, entregue com `--no-captions`.

`--from/--to` no import serve para gravações com sobra no começo e no fim. A gravação não é copiada; o projeto guarda o caminho, então não mova o arquivo até entregar. `--third-party` registra que a gravação não é do usuário (e o `deliver.py` passa a exigir a licença).

Sem WhisperX, a legenda pode vir de um `.srt` que o usuário tenha (CapCut, YouTube, editor do celular): `captions.py import` desloca pelo `--from`, aperta cada bloco na fala real e distribui as palavras. Sem transcrição nenhuma, `cut` corta só silêncios; avise que vícios e retomadas ficam para marcar ouvindo.

## Editar o `edl.json`

Leia `edit/transcript.md` inteiro antes de mexer. Cada trecho tem `id`, `in`/`out` (segundos da gravação), `keep`, `zoom`, `x`, `y` e o texto falado.

1. **Retomadas.** O transcript marca "retomada?" quando dois trechos próximos começam igual. Fique com a versão mais fluida (geralmente a última) e marque `"keep": false` na outra. Tire também frases repetidas, desculpas ("deixa eu falar de novo"), "então, é isso" e despedidas longas.
2. **Gancho primeiro.** Os 2 primeiros segundos decidem a retenção. Se a frase mais forte (promessa, número, conflito, pergunta) foi dita no meio, mova o trecho dela para o topo de `segments`; a ordem da lista é a ordem do vídeo. Não invente frase: só reordene o que foi dito, e só se o sentido continuar certo.
3. **Duração.** Vertical: mire 20–45 s, corte o que repete ou explica demais. Longo: veja [vídeo longo](longo.md).
4. **Enquadramento.** Rode `frames`, olhe `edit/frames.jpg` e ajuste `x` (0 a 1, centro do rosto) em cada trecho; as linhas brancas marcam cada 10% da largura e o retângulo vermelho é o recorte atual. Rosto no terço superior; se a cabeça for cortada, baixe `y` ou o `zoom`. Rode `frames` de novo até todos os quadros estarem certos.
5. **Zoom.** `cut` sugere 1,0/1,15; revise esses valores no EDL, evitando alternância mecânica. Use punch-in com intenção ou B-roll para disfarçar a emenda. Em fala emocional ou revelação, use 1,25–1,35 no trecho; não passe de 1,15 se a fonte for 720p em vertical (a imagem já é ampliada ~2,7×).

`cut` de novo (com outros `--min-silence`, `--pad`, `--fillers tipo,né`) refaz os trechos e leva `x`, `y` e os descartes para o trecho novo que mais se sobrepõe; `--reset` descarta tudo isso e as inserções.

## Ritmo e cortes

- Pausa natural de respiração fica (0,12 s de folga de cada lado é o padrão de `--pad`); silêncio de pensar sai. Fala corrida demais (acima de ~3,3 palavras/s) cansa: aumente `--pad` para 0,18.
- Em vertical dinâmico, 1,5–3 s pode orientar a cadência, mas ajuste ao conteúdo e à intenção. Numa gravação isso vem de corte com zoom alternado, texto na tela, B-roll ou print. Se um trecho passa de 4 s sem nada, quebre com zoom ou inserção.
- `--fillers tipo,né,assim` corta palavras extras quando isoladas; confira no transcript se não sumiu alguma que dava sentido.

## B-roll, prints e imagens

Inserções vão em `overlays` no `edl.json`: `{"file": "assets/broll1.mp4", "at": 12.5, "dur": 2.0}` com `at` no tempo do vídeo final (veja `edit/timeline.md` depois do primeiro render) ou `{"src": 47.2, ...}` no tempo da gravação, que sobrevive a um novo `cut`. Uma inserção cobre a imagem e mantém o áudio da fala.

Use quando a fala cita algo que dá para mostrar (app, produto, número, lugar), para esconder um corte feio e para quebrar trecho longo. Fonte do B-roll: do próprio usuário, gerado (ComfyUI, motion em código) ou banco com licença comercial. Registre cada uma em `assets`. `src` que cai num silêncio cortado é ignorado; escolha um tempo dentro da fala.

## Qualidade da fonte

- Peça a gravação original, não a baixada da rede (que já vem comprimida). 1080p é o mínimo para cortar em 9:16 de uma gravação horizontal; 4K deixa folga para zoom. Gravação já vertical evita recorte.
- Fonte vertical em projeto 16:9 sai com fundo desfocado da própria imagem (`"fit": "blur"`, automático).
- Áudio ruim derruba mais retenção do que imagem ruim. A limpeza padrão (graves, ruído leve, compressão) resolve ventilador e eco leve; se o áudio vier com clipping ou eco forte, diga no relatório e sugira regravar com microfone de lapela.

## Texto na tela e legenda

- Legenda palavra a palavra (`captions.py ass`) em todo vídeo vertical; em 16:9 longo, legenda opcional (o usuário pode subir o `.srt` na plataforma).
- Texto do gancho (até 6 palavras) no quadro 0, no terço superior da área segura, sem cobrir o rosto.
- Fonte e cor da legenda saem de `direction`; sem direção definida, uma fonte sem serifa pesada com contorno escuro.

## O que costuma dar errado

| Sintoma | Causa | Correção |
|---|---|---|
| Última palavra de cada frase some | Legenda importada com blocos longos | `captions.py import` já aperta na fala; se persistir, `--pad 0.18` |
| Palavras da legenda fora de sincronia | `.srt` do vídeo inteiro com import de um trecho | O import desloca pelo `--from`; se o `.srt` já é do trecho, use `--final` |
| Rosto cortado em algum trecho | `x` padrão 0,5 | Ajuste `x` por trecho com `frames` |
| Jump cut evidente | Dois trechos seguidos com o mesmo zoom | Alterne `zoom` ou cubra o corte com B-roll |
| Estalo nos cortes | Corte no meio de som | O render faz fade de 12 ms; se persistir, aumente `--pad` |
