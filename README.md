# Vídeo viral — 2.0.0

Skill em português para direção, produção e edição audiovisual com IA, marketing, ganchos, retenção e conversão. Produz vídeos curtos/longos, gravações editadas, demonstrações de produto, UGC, animações e peças musicais com planejamento e revisão. Não promete viralização nem valida estética apenas porque o render passou.

## Stack escolhido

- HyperFrames + GSAP: composição principal, motion, tipografia, camadas e transições.
- FFmpeg + ffprobe: preparação, mixagem, exportação e medições.
- Three.js e Blender: cenas e ativos 3D.
- Tone.js: desenho de som offline sincronizado.
- gl-transitions: transições por shaders.
- ComfyUI: geração de imagens por workflows concretos.
- PixiJS, Paper.js ou p5.js: linguagem visual por cena.
- Blender MCP + glTF Transform: automação e preparação do 3D.
- Kokoro: narração.
- faster-whisper: transcrição/tempos de legenda.
- ACE-Step 1.5: geração musical por serviço configurado.

`assets/stack.json` é o catálogo exclusivo. Dependências indiretas de build, fonetização, browser e modelos não são motores criativos alternativos. Não instalar outros provedores automaticamente. Google Trends permanece como fonte de pesquisa/CSV, não como motor audiovisual.

## Instalação da skill

Copie esta pasta para ~/.agents/skills/video-viral ou .agents/skills/video-viral. No Codex, use `$video-viral <pedido>`; no Claude Code, a pasta equivalente de skills e `/video-viral <pedido>`. A atualização do repositório não reinstala uma skill local removida.

Ferramentas são instaladas seletivamente em ambientes dedicados: [setup](references/setup.md). O grupo Node v2 usa package.json e lockfile fixados em assets/node; não sobrescreve um ambiente desconhecido. Não há download automático de checkpoints ComfyUI ou pesos ACE-Step.

```sh
python scripts/check_env.py
python scripts/stack.py list
python scripts/stack.py doctor --node-root <raiz-npm>
```

## Fluxo

Brief de público/oferta → pesquisa → ganchos audiovisuais → roteiro → direção e plano técnico → módulos/ativos → composição HyperFrames → mix/export → revisão do mesmo arquivo final. Leia [SKILL.md](SKILL.md), [marketing](references/marketing.md), [pipeline](references/pipeline.md) e os guias do formato.

## Entradas executáveis

| Script | Função |
|---|---|
| new_project.py / plan.py | Projeto schema 3, brief, ganchos e consistência do planejamento |
| footage.py / clips.py | Importar/cortar/enquadrar gravação e selecionar cortes |
| voice.py | Kokoro ou montagem de WAVs fornecidos |
| captions.py | faster-whisper, importação SRT/VTT, estimativa identificada e legenda ASS |
| visual_scene.mjs | Projetos de cena determinísticos PixiJS, Paper.js, p5.js e gl-transitions |
| sound.mjs | Tone.js offline → WAV e receipt; mix por deliver.py |
| gltf.mjs | Otimização GLB, preservando fonte |
| comfy.py / images.py | Workflow ComfyUI API → imagem, com proveniência |
| music.py | Cliente REST ACE-Step 1.5 → WAV, sem instalar/iniciar o serviço |
| deliver.py / review.py | Mix, exportação e revisão vinculada por hashes e evidências |
| trends.py | URL/CSV oficial do Google Trends, com filtros e índices preservados |

Exemplos, contratos e limites em [módulos](references/modules.md). Os projetos de cena são demos técnicas editáveis; a direção e a integração no filme continuam necessárias. Scripts antigos de rastreamento externo e alinhamento forçado não instalam alternativas: explicam a migração.

## Validação

```sh
python -m unittest discover -s tests -v
node --test tests/node/*.test.mjs
python tests/integration_pipeline.py --output <pasta-nova>
```

Testes Node precisam das dependências fixadas e de Chrome/Edge instalado. Defina VIDEO_VIRAL_NODE_ROOT e, se necessário, VIDEO_VIRAL_BROWSER_PATH. Os testes verificam determinismo, arquivos, APIs e falhas; não medem retenção real ou qualidade artística. Clientes de geração podem ser testados com servidores simulados sem validar os modelos reais.

## Entrega e licenças

A entrega monetizada exige licenças/ativos confirmados; --draft gera rascunho identificado. `out/delivery.json`, métricas, imagens e assessment.json ligam revisão ao mesmo render/manifesto. Código 3 é limite com deficiências, não aprovação. Não publicar ou acessar contas sem pedido explícito.

Distribuição da skill: MIT. Ferramentas, pesos e ativos têm termos próprios; registre os reais. Sem provas, datas, preços ou analytics fornecidos, não inventar informação para passar num teste.

## Migração para 2.0.0

- Projetos novos registram o compositor HyperFrames e IDs de módulos no manifesto/tool_plan. Projetos legados continuam legíveis, mas novas revisões exigem as evidências atuais.
- Kokoro é o único TTS; não há troca automática para voz do sistema. faster-whisper é o transcritor; importação SRT/VTT e estimativa permanecem.
- images.py agora é alias do cliente por workflow API ComfyUI: migrar specs antigas para um grafo exportado e informar o nó de saída.
- O runtime Node v2 usa pasta/lockfile próprios; não atualiza silenciosamente o cache v1 ou reativa skills removidas.
