# Vídeo viral — 2.2.0

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

Copie esta pasta inteira (incluindo scripts, assets e references):

- Claude Code, pessoal: `~/.claude/skills/video-viral/`; por projeto: `.claude/skills/video-viral/`. Use `/video-viral <pedido>`.
- Codex, pessoal: `~/.agents/skills/video-viral/`; por projeto: `.agents/skills/video-viral/`. Use `$video-viral <pedido>`.

A atualização do repositório não reinstala uma skill local removida.

Ferramentas são instaladas seletivamente em ambientes dedicados: [setup](references/setup.md). Rode `setup_tools.py <grupos>` sem flags primeiro: sistema, `pip --user uv` e ComfyUI pendentes produzem lista e código 4, sem instalar nada. O agente pede confirmação única dessa lista antes de `--allow-system`/`--allow-large`. Venvs/npm locais permanecem autônomos quando permitidos; `VIDEO_VIRAL_NO_INSTALL=1` bloqueia tudo.

Node v2 usa package.json/lockfile em assets/node; Python usa requisitos diretos fixados em assets/python e ComfyUI tem commit fixado. Dependências transitivas/modelos não constituem um lock completo. Não sobrescreve ambiente Node desconhecido nem checkout ComfyUI divergente/sujo. Não há download automático de checkpoints ComfyUI ou pesos ACE-Step.

```sh
python scripts/check_env.py
python scripts/stack.py list
python scripts/stack.py doctor --node-root <raiz-npm>
```

## Fluxo

Brief de público/oferta → pesquisa → ganchos audiovisuais → roteiro → direção e plano técnico → módulos/ativos → composição HyperFrames → mix/export → revisão do mesmo arquivo final. Leia [SKILL.md](SKILL.md), [marketing](references/marketing.md), [pipeline](references/pipeline.md) e os guias do formato.

O guia de [composição](references/composition.md) liga HTML/GSAP e cenas geradas ao render `render/master.mp4`, com comandos conferidos na tag HyperFrames 0.9.40. FFmpeg prepara e entrega, mas não substitui o compositor numa produção completa.

Sem reprodução/escuta no runtime, o resultado esperado é **entrega técnica aprovada, revisão humana pendente**, quando as checagens técnicas passaram. `review.py` gera `review/rNN/ficha-humana.md`; uma pessoa independente preenche identidade, confirmação integral, notas e evidências. Importe com `review.py <projeto> --human-form <ficha>`. O mesmo portão de hashes/independência/cobertura continua valendo: pendência não é código 0. Veja [revisão](references/review.md).

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

Exemplos, contratos e limites em [módulos](references/modules.md). Os projetos de cena são demos técnicas editáveis; a direção e a integração no filme continuam necessárias. O comando legado de alinhamento explica a migração sem instalar alternativas; o stub de rastreamento sem referências foi removido.

## Validação

```sh
python -m unittest discover -s tests -v
node --test tests/node/*.test.mjs
python tests/integration_pipeline.py --output <pasta-nova>
```

Testes Node precisam das dependências fixadas e de Chrome/Edge instalado. Defina VIDEO_VIRAL_NODE_ROOT e, se necessário, VIDEO_VIRAL_BROWSER_PATH. Os testes verificam determinismo, arquivos, APIs e falhas; não medem retenção real ou qualidade artística. Clientes de geração podem ser testados com servidores simulados sem validar os modelos reais.

## Casos em evals/

São cenários de comportamento do agente, não testes unitários Python nem métricas de audiência. Cada pasta tem `case.yaml` (schema_version `"1.1"`, nome e expected_outcome), `prompt.md` (pedido, às vezes com limites/ferramentas no frontmatter), `graders/` (critérios LLM, foco no trace) e, quando necessário, `files/` (entradas preservadas).

A documentação skill-creator do ambiente identifica `claude plugin eval` como leitor desse layout/schema. O repositório não inclui um harness próprio nem fixa uma versão desse CLI; a compatibilidade/execução dos casos não foi validada aqui. Também podem ser aplicados manualmente com registro do trace, sem confundir isso com resultado automatizado. A CI abaixo só roda unittest; não dispara agentes, renders ou evals cobrados.

O caso `composicao-hyperframes` exige evidência do render da composição principal antes de deliver/review, e rejeita base FFmpeg ou demo isolada como produção completa. Os casos de revisão continuam exigindo evidência real, inclusive quando o resultado correto é pendência humana.

## Entrega e licenças

A entrega monetizada exige licenças/ativos confirmados; --draft gera rascunho identificado. `out/delivery.json`, métricas, imagens e assessment.json ligam revisão ao mesmo render/manifesto. Código 3 é limite com deficiências, não aprovação. Não publicar ou acessar contas sem pedido explícito.

Distribuição da skill: MIT. Ferramentas, pesos e ativos têm termos próprios; registre os reais. Sem provas, datas, preços ou analytics fornecidos, não inventar informação para passar num teste.

## Referências e roteiros com IA — 2.2.0

Ficha de pesquisa por plano, ganchos e [catálogo de formatos](references/formats/virais-ia.md), com pilotos editoriais, fontes datadas e regras de plataforma. Pesquisa não assistida e números de terceiros, sem garantia de alcance. Atualização apenas documental e de versão: nenhum motor, instalação ou mudança no stack.

## Composição e revisão humana — 2.1.0

Guia de composição HyperFrames 0.9.40 até o master, ficha humana importável com o mesmo contrato de aprovação, instalação de sistema/grande porte com consentimento explícito, pins diretos Python/ComfyUI e CI Python em push/PR. O SKILL.md concentra o fluxo e remete detalhes às referências. Voz externa por WAV e ordem de fontes visuais sem ComfyUI estão documentadas. Os códigos de revisão 0–3 e os formatos existentes permanecem compatíveis.

## Migração para 2.0.0

- Projetos novos registram o compositor HyperFrames e IDs de módulos no manifesto/tool_plan. Projetos legados continuam legíveis, mas novas revisões exigem as evidências atuais.
- Kokoro é o único TTS; não há troca automática para voz do sistema. faster-whisper é o transcritor; importação SRT/VTT e estimativa permanecem.
- images.py agora é alias do cliente por workflow API ComfyUI: migrar specs antigas para um grafo exportado e informar o nó de saída.
- O runtime Node v2 usa pasta/lockfile próprios; não atualiza silenciosamente o cache v1 ou reativa skills removidas.

## Revisão independente — 2.0.1

Única mudança de fluxo nesta atualização: a aprovação audiovisual completa exige revisor distinto do autor, capacidades conferidas por modalidade e observação registrada do vídeo inteiro. O novo preflight é executado antes da delegação; o pacote input/ não inclui notas/conclusões do autor. Métricas de áudio, pranchas ou amostragem podem apoiar uma avaliação parcial, mas não promovem sozinhas o vídeo a aprovado.

Use `review.py --check-reviewer capacidades.json --producer-id <id-do-autor>` e depois `review.py <projeto> --producer-id <id-do-autor>`. O modelo em assets/reviewer.example.json começa vazio para evitar disponibilidade presumida. O script valida o registro e a consistência, não autentica ferramentas/identidades nem prova por si que houve reprodução/escuta. Revisões antigas precisam ser regeneradas com o novo pacote. O stack e os demais fluxos continuam os mesmos.
