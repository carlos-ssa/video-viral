# Animação e storytelling com IA

Escolha a linguagem pela história: animação 2D, 2.5D, personagens 3D, tipografia ou combinação. O pipeline narrado fornece manifesto, voz, composição e entrega; a direção precisa garantir continuidade e atuação entre planos.

## Pré-produção

Definir público, tom, arco, gancho, conflito/pergunta, progressão e recompensa. Se for marketing, conectar a história ao benefício e à prova, sem inserir um CTA desconectado. Para canal/série, manter uma bíblia enxuta de personagens, cenários, paleta, fontes e linguagem de movimento.

Planejar storyboard com ações e enquadramentos por plano. Registrar identidade/aparência, escala, roupas, adereços e relações espaciais; gerar imagens de referência e três quadros de estilo. Semente fixa ajuda na repetição, mas não garante identidade entre cenas; conferir referências e corrigir inconsistências antes de animar.

## Ferramentas e produção

- HyperFrames + GSAP: composição, tipografia, gráficos, recortes e transições.
- Three.js/Blender: personagens/objetos, câmera, luz e atuação que precisem de geometria.
- ComfyUI ou gerador disponível: referências, fundos e ativos; um gerador imagem-para-vídeo exige workflow/modelo específico, saída de teste e registro em `tool_plan`. `images.py` não deve ser anunciado como gerador de vídeo universal.

Mapear ferramenta e contribuição por plano. Preferir continuidade de identidade e intenção a uma sequência de efeitos desconexos. Medir voz antes de temporizar as cenas; em ação sem fala, trabalhar os tempos e a música. Usar [motion](../motion.md) e animação determinística no compositor, com ativos gerados fixados e versionados.

Montar cenas, voz, ambientes e efeitos; conferir direção de olhar, continuidade de ação, orientação espacial, mãos/rostos e estabilidade temporal. Em série, reutilizar componentes/ativos aprovados sem repetir o mesmo gancho.

## Revisão e entrega

Renderizar um trecho representativo antes da sequência completa. Inspecionar movimento e transições, não só quadros isolados. O formato `storytelling` acrescenta Continuidade à rubrica. Referenciar personagens/planos observados em `assessment.json` e nas notas. Conferir se o payoff resolve a promessa; efeitos e movimento precisam sustentar a leitura.

Entregar master pelo pipeline padrão, registrar limitações de animação e o status das integrações. Um storyboard ou animatic deve ser identificado como tal, não como vídeo final profissional aprovado.
