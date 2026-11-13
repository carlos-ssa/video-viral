# Música, lyric video e visualizer

A estrutura vem da faixa musical. Não impor roteiro de narração ou fala nos primeiros 0,5 s a uma peça instrumental. O formato `musica` inicia sem narração sintética e usa Sincronismo musical na revisão.

## Brief e música

Definir público/nicho, gênero, emoção, duração, trecho principal e linguagem visual. Para canal, registrar identidade de série. Se a faixa já existe, preservar o arquivo e verificar os direitos. Se precisar gerar, selecionar ferramenta disponível (ACE-Step ou serviço autorizado), registrar parâmetros/versão e revisar uma amostra antes da faixa completa. A integração atual não inclui CLI próprio de geração musical; usar o fornecedor disponível e registrar `adaptacao` até validar a saída.

Guardar o master em `audio/music.wav` com proveniência em `assets`. MusicGen só cabe em projeto compatível com a licença dos pesos; verificar os termos atuais. Não atribuir uma licença de software automaticamente à faixa ou aos modelos usados.

## Planejamento audiovisual

Identificar intro, versos, refrão, drop, respiros e final. Medir batidas/onsets com uma ferramenta realmente capaz de extraí-los ou marcar ouvindo; guardar timestamps em `research/music-timing.json`, método e confiança. `astats`/`ebur128` medem características e volume, não fornecem sozinhos um beat grid pronto.

- Visualizer: movimento, partículas, câmera e cor respondem à estrutura/energia, evitando um loop genérico sem progressão.
- Lyric video: transcrever/alinha a letra cantada, corrigir palavras e ajustar tempos; não tratar canto como narração já perfeitamente alinhada.
- Clipe animado: usar [animação](animacao.md), personagens/cenários consistentes e um arco visual.

Compor em HyperFrames/Remotion/Blender conforme a direção; sincronizar cortes e revelações em momentos musicais relevantes, sem obrigar corte a cada batida. Preservar contraste e respiros. Para vertical, escolher o trecho que funciona sozinho e abrir com sua força musical/visual. Para longo, planejar evolução e retornos temáticos.

## Mix e revisão

Evitar som duplicado: se a música já está no master, usar `--no-music`; se `deliver.py` vai mixá-la, manter o master sem essa faixa. Não aplicar ducking de narração quando não existe fala. Legendas de letra podem ser compostas ou queimadas, nunca duplicadas.

Checar sincronismo, cortes, continuidade, legibilidade da letra, distorção, volume/pico e final. Conferir temporalmente passagens representativas e registrar método/intervalos em `assessment.json`. Notas de Som e Sincronismo musical devem citar evidências. Sem possibilidade de ouvir, declarar análise instrumentada e limitar o julgamento perceptual.

Render de exemplo sem qualidade estética revisada é validação técnica, não demonstração de que o canal vai performar. Preparar capa, título e rótulo de IA conforme o destino; publicar somente com pedido explícito.
