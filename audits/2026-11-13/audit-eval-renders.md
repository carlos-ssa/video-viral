# Renders reais dos evals — 2026-11-13

## Resultado e alcance

Os dois cenários autorizados foram executados até master HyperFrames + GSAP, exportação com ASS, receipt técnico aprovado e rodada independente preparada. **Entrega técnica aprovada; revisão humana pendente (verdict 2)** nos dois projetos. Não há aprovação audiovisual/profissional, publicação ou inferência de audiência.

Coordenado com instructions_evals: o corte é `cortes-de-video-longo/corte-selecionado`, rank3 coeso, não `melhor-corte` rank1 rejeitado. A gravação usa seu EDL existente. O corte recebeu EDL editorial explícito com promessa + três gastos completos; filler éé e a primeira retomada incompleta foram descartados. Fonte24,19s torna-se14s; não se promete que esse timing seja ideal editorialmente.

## Pipeline realmente executado

Auxiliares reproduzíveis em work: `render-real-evals.py`, `fix-eval-manifest-utf8.py`, `repair-eval-fullstage.py`, `verify-eval-renders.py` e `eval-composition-proof.mjs`.

Comandos completos, códigos, duração e logs: `work/eval-render-commands.json`. Evidências estruturadas, hashes e comandos de extração de quadros: `work/eval-render-evidence.json`.

1. `plan.py`: código0 nos dois planos antes da composição; manifesto completo e tool_plan das etapas reais. Suposições dizem que a distribuição das palavras fornecidas é estimada; não houve alinhamento forçado ou transcrição nova.
2. `footage.py render`: código0, EDL + source_words remapeadas em words.json; áudio limpo fornecido pelo projeto preservado no A-roll. Versão final usa `fit:blur` na dimensão1080×1920: primeiro plano integral sem cortar o rosto geométrico, com cenário derivado desfocado até as quatro bordas.
3. `captions.py ass --words 5`: código0; ASS real em1080×1920, Arial64, margens90/150/520, até duas linhas; mantido fora do HTML e queimado uma única vez no deliver.
4. Composição principal1080×1920/30fps com GSAP local e fonte Inter local/OFL. Vídeo ocupa1920px de altura; título/assunto está presente e opaco desde quadro0. Títulos mudam conforme as palavras remapeadas; progresso é dirigido pela timeline pausada.
5. `stack.py hyperframes -- check ... --json`: código0 e ok:true nos dois. Sem erros de lint/layout/runtime/áudio; avisos estruturais de cenas aninhadas/densidade permanecem (7 na gravação,5 no corte). Não são aprovação estética.
6. `stack.py hyperframes --screenshot -- render ... --fps 30 --workers 1 --quality looks`: código0 nos dois; logs confirmam captureMode screenshot, hardware GPU, composição integral, videoCount1/audioCount1.
7. `deliver.py --video render/master.mp4 --no-music`: código0, approved:true/draft:false. Fonte fixture explicitamente própria no cenário; sem ativos de terceiros não autorizados. `data-has-audio=true` extrai única fala do A-roll; não existe audio/voice.wav na mix; sem voz externa, sem duplicatevoz. Ausência de cama tem dispensa editorial explícita em music.bed_waiver.
8. `review.py --producer-id node_setup:eval`: código0; `--verdict`: código2, sem notas ou evidência humana inventadas. Rodada atual é r03; input/video.mp4 tem o mesmo SHA256 do out atual, request e delivery usam o mesmo hash canônico do manifesto.

## Correções e preservação de evidência

- Primeira passagem usou foreground contain num palco930px. Revisão independente identificou ocupação insuficiente. A versão final refaz A-roll fit:blur/full-frame, mantendo o original nítido integral, e corrige no corte o título final para **Delivery no fim / de semana**, com duas palavras na última linha.
- Houve erro meu no auxiliar inicial por read_text sem encoding em Windows/cp1252. Alguns textos dos manifests ficaram corrompidos; HTML/ASS/vídeos estavam corretos. Auxiliares agora usam UTF-8 explícito; manifests foram corrigidos e receipt/review refeitos.
- r01/input e r02/input foram preservados integralmente. r03 é a revisão vigente após mudanças verificáveis. Masters/aroll/out anteriores foram preservados como `*.before-fullstage.*`; versão anterior ao ajuste UTF-8 em out usa `*.before-encoding-fix.*`. Nenhuma fonte original foi escrita.
- Limitação visual remanescente vista na gravação: CTA final quebra **Qual pesa no seu / orçamento?**, com última palavra órfã. Relatado ao coordenador após r03; não foi ocultado nem se declarou acabamento profissional. Corrigir exigiria novo render e evidência atualizada, preservando o limite de rodadas.

## Verificação visual e limites de modalidade

Foram extraídos e inspecionados **três quadros decodificados do arquivo final de cada projeto**: quadro0, meio e0,2s antes do fim (`render/fullstage-frame0.png`, `fullstage-framemid.png`, `fullstage-frameend.png`). Confirmam título inicial, rosto geométrico integral, fonte fixture real, ASS legível separado do rosto e título final corrigido no corte. É inspeção de seis quadros, não reprodução integral/movimento ou escuta.

`render/composition-proof.json` em cada projeto confirma fonte @font-face carregada, título opacidade1 no0, timeline pausada e vídeo1080×1920/contain. A captura desse auxiliar aplica somente na página de prova a visibilidade dos clips no tempo0; não altera o HTML nem substitui o master renderizado. `render/fullstage-ffprobe.json` registra streams e dimensões reais.

Não houve escuta ou avaliação perceptual completa. Legendas derivam de source_words com estimated:true; remapear não converte essa estimativa em alinhamento medido. As fichas humanas permanecem em branco para pessoa independente. As fontes são fixtures do cenário, não uma pessoa real filmada ou acabamento cinematográfico.

## Ambiente e limites operacionais

Node v26.12.0; HyperFrames0.9.40; Chrome157 instalado; FFmpeg9.0.2. Browser explícito `C:/Program Files/Google/Chrome/Application/chrome.exe`, cache existente `<home>/.cache/hyperframes`, dependências existentes `<runtime-root>/node-v2`; fontes/GSAP copiados localmente do material de validação autorizado. Proibição NO_INSTALL estava ausente no ambiente original e não foi removida; código herda o ambiente. Nenhum download/modelo/instalação, chamada cobrada, publicação ou commit foi feito. Logs não apresentaram tentativa de download.

## Artefatos atuais e hashes

### editar-gravacao-propria/projeto

- Final: `<workspace>\work\eval-runs\editar-gravacao-propria\projeto\out\projeto.mp4`
- Duração: 26.467s;1080×1920/30fps;-14.0LUFS; pico-1.9dBTP.
- Última palavra termina em 26.293s; cauda até final 0.174s.
- SHA256 final: `9277f8ec75881fa762109df1d219f0f3a9e25ef9ae9cab611a207b470a185ddd`.
- SHA256 canônico manifesto/receipt/request: `6e7003493c35ceba25c56e3fa51f6cc8549c50f8ea9bdfe69e8bb43ab686ed6a`.
- Fonte preservada: `<repo>\evals\editar-gravacao-propria\files\gravacao.mp4`; SHA256 `2e0e813b0a4ba94595b0728a54a55d314cb01b10173ea3c92d57e34f16338f54`.
- Manifesto: `<workspace>\work\eval-runs\editar-gravacao-propria\projeto\video.json`. EDL: `<workspace>\work\eval-runs\editar-gravacao-propria\projeto\edit\edl.json`; timeline: `<workspace>\work\eval-runs\editar-gravacao-propria\projeto\edit\timeline.md`.
- Legendas: `<workspace>\work\eval-runs\editar-gravacao-propria\projeto\captions\words.json` e `<workspace>\work\eval-runs\editar-gravacao-propria\projeto\captions\captions.ass`.
- Composição: `<workspace>\work\eval-runs\editar-gravacao-propria\projeto\composition\index.html`; master: `<workspace>\work\eval-runs\editar-gravacao-propria\projeto\render\master.mp4`.
- Receipt: `<workspace>\work\eval-runs\editar-gravacao-propria\projeto\out\delivery.json`; approved:true/draft:false.
- Revisão vinculada: `<workspace>\work\eval-runs\editar-gravacao-propria\projeto\review\r03\input\request.json` e `input/video.mp4`; ficha: `<workspace>\work\eval-runs\editar-gravacao-propria\projeto\review\r03\ficha-humana.md`.

### cortes-de-video-longo/corte-selecionado

- Final: `<workspace>\work\eval-runs\cortes-de-video-longo\corte-selecionado\out\corte-selecionado.mp4`
- Duração: 14.0s;1080×1920/30fps;-14.0LUFS; pico-2.2dBTP.
- Última palavra termina em 13.844s; cauda até final 0.156s.
- SHA256 final: `c518fdf7e05be88c949ae9964bff0097ac95ed412e7c9d4faa90c7067dfd0b56`.
- SHA256 canônico manifesto/receipt/request: `7fff4635087be512b1bff6f1ee7000e6f872d1cc2cf975bf85d22942aee58ed0`.
- Fonte preservada: `<repo>\evals\cortes-de-video-longo\files\gravacao_longa.mp4`; SHA256 `e9c534aa2d4087a2320c8640373ed413951f0a25f9bd66d6a1ad7fdd724c04c0`.
- Manifesto: `<workspace>\work\eval-runs\cortes-de-video-longo\corte-selecionado\video.json`. EDL: `<workspace>\work\eval-runs\cortes-de-video-longo\corte-selecionado\edit\edl.json`; timeline: `<workspace>\work\eval-runs\cortes-de-video-longo\corte-selecionado\edit\timeline.md`.
- Legendas: `<workspace>\work\eval-runs\cortes-de-video-longo\corte-selecionado\captions\words.json` e `<workspace>\work\eval-runs\cortes-de-video-longo\corte-selecionado\captions\captions.ass`.
- Composição: `<workspace>\work\eval-runs\cortes-de-video-longo\corte-selecionado\composition\index.html`; master: `<workspace>\work\eval-runs\cortes-de-video-longo\corte-selecionado\render\master.mp4`.
- Receipt: `<workspace>\work\eval-runs\cortes-de-video-longo\corte-selecionado\out\delivery.json`; approved:true/draft:false.
- Revisão vinculada: `<workspace>\work\eval-runs\cortes-de-video-longo\corte-selecionado\review\r03\input\request.json` e `input/video.mp4`; ficha: `<workspace>\work\eval-runs\cortes-de-video-longo\corte-selecionado\review\r03\ficha-humana.md`.

## Códigos finais por projeto

| Projeto | A-roll | Plano | Check | HF render | Deliver | Review | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|
| editar-gravacao-propria | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| cortes-de-video-longo | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
