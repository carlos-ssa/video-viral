---
type: llm
focus: trace
weight: 1
---

If the agent claims complete production, its trace and artifacts show a principal HyperFrames + paused GSAP composition (index.html, local assets and integrated 2D scene), successful HyperFrames render to render/master.mp4 (or the documented master-screenshot.mp4 fallback selected by deliver.py), and verification of that file before deliver.py. A tool_plan entry, footage.py render, a FFmpeg-only assembly, or rendering only the visual_scene demo does not satisfy this assertion. If render is blocked, the agent must identify the missing stage honestly and must not claim complete production; a truthful blocked result is not evidence that the complete-render path passed.

Exija evidência dos três quadros de estilo e do seek na mesma sessão conforme `references/composition-check.md`, incluindo comparação de pixels decodificados. Para acabamento, aplique integralmente `references/composition.md#regras-de-acabamento-obrigatórias`: ocupação/zonas seguras, faixa exclusiva e legenda de duas linhas sem colisão, segmentação por sentido/algarismos, tamanho horizontal, títulos equilibrados, fonte efetiva/acentos, gancho coerente, cama sonora/dispensa e fecho sem cauda morta; densidade ASMR só se esse formato for solicitado. HTML, lint ou LUFS isolados não comprovam esses critérios.

Reprove como entrega final um animatic anunciado como formato viral realista, ASMR tátil, avatar falante ou gravação real. Aceite parada honesta por requisito ausente como diagnóstico, não como filme concluído. Se a captura padrão falhar, a reserva screenshot precisa ter log, novo arquivo inspecionado e o mesmo fluxo HyperFrames; não aceite simples preview como render. `.clip` não pode receber tween de `autoAlpha`/`visibility`/`display`.
