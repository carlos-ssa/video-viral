# Pipeline narrado / produção completa — v2

O manifesto coordena brief, roteiro, voz, ativos e composição. Todos os comandos são relativos à pasta da skill; saídas ficam na pasta absoluta do projeto. Veja [marketing](marketing.md), [pesquisa](research.md), [direção](direction.md) e [módulos](modules.md).

1. Definir público, objetivo, oferta, prova e CTA. Pesquisar com os recursos web disponíveis e Google Trends, preservando fontes e hipóteses. Não adicionar downloader/provedor fora do stack.
2. Criar cinco ganchos audiovisuais quando a peça é completa e escolher pela promessa cumprida e adequação ao público.
3. Escrever cenas e planos, direção visual/sonora e tool_plan. `plan.py` confere que as decisões estão no manifesto; dados pendentes não devem ser inventados.
4. `voice.py <projeto>` gera narração Kokoro. `--from-wavs` monta as cenas fornecidas. Medir duração antes de temporizar o vídeo.
5. `captions.py transcribe <projeto>` usa faster-whisper; `import --file legenda.srt` ou `estimate` são alternativas sem novo motor. Conferir tempos, palavras e números. Tempos estimados não são alinhamento preciso.
6. Gerar imagens com workflow ComfyUI real; cenas 2D com PixiJS/Paper.js/p5.js conforme linguagem; 3D com Blender/Three.js; preparar GLB com glTF Transform. Todo recurso deve produzir um artefato verificável.
7. Compor o filme principal em HyperFrames + GSAP, com cenas/ativos e animação determinísticos. gl-transitions fornece efeitos específicos quando necessários, não uma cota de transições.
8. Gerar efeitos com Tone.js e trilha com ACE-Step 1.5 quando pertinente. Guardar tempos e licença. Não duplicar áudio já composto; o master pode ser entregue sem faixa e a mixagem ocorrer em deliver.py.
9. `deliver.py <projeto> --video render/master.mp4` exporta e mede, incluindo audio/sound-design.wav quando existir. `--no-music` e `--no-captions` evitam camadas duplicadas. A saída precisa corresponder ao render revisado.
10. `review.py` e o método de [revisão](review.md) verificam o arquivo final. O hash e a nota não substituem inspeção audiovisual. Corrigir só etapas afetadas, preservando primeiro render e fontes.

Para séries: reutilizar ativos e componentes aprovados, mantendo a direção de cada episódio. Processos pesados de GPU são sequenciais; não iniciar dois geradores grandes sem memória disponível. Uma composição editável não equivale a qualidade estética validada.
