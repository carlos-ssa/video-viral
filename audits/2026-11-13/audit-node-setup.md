# Auditoria Node e instalação — 2026-11-13

## Escopo e execução

Responsável: subagente node_setup, contrato faixa 2, sem subdelegação. Auditoria feita no checkout compartilhado `video-viral`; somente arquivos autorizados foram alterados. SKILL.md lido integralmente. `assets/node/package.json`, `package-lock.json` (143.307 caracteres; 324 entradas), `assets/stack.json` e todos os arquivos de `assets/python/` foram lidos/parseados integralmente. Scripts Node, Python de instalação/diagnóstico, adaptadores de áudio/visual, testes e workflow foram inspecionados.

Nenhuma instalação foi executada, nenhum modelo/browser foi baixado ou atualizado, nenhuma configuração global foi alterada. Não houve chamada cobrada, publicação ou commit. Testes usaram dependências existentes em `<runtime-root>/node-v2`. Flags de consentimento e VIDEO_VIRAL_NO_INSTALL foram preservadas e fortalecidas.

## Achados corrigidos

1. **NO_INSTALL contornável por chamadas diretas:** somente main() verificava a variável; install_hyperframes/venv/comfyui/program/uv e sh podiam instalar se importados. Agora uma guarda comum interrompe antes de mkdir, cópia, subprocesso ou instalação. Teste chama todos com flags de consentimento ligadas e confirma zero subprocessos/escritas.
2. **glTF sobrescrevia recibo existente:** a proteção cobria apenas GLB; receipt era writeFileSync sem exclusividade. Agora ambos os destinos são verificados e publicados por hard links exclusivos de temporários completos. Colisão ou corrida não substitui arquivo alheio; falha na publicação do recibo remove somente o GLB publicado por esta operação. Teste real inclui recibo órfão preservado e ausência de novo GLB.
3. **Diagnóstico falso positivo:** cmd_version retornava `ok` inclusive quando executável não iniciava, falhava ou expirava. Agora falha retorna None, inclusive GPU indisponível/timeout/saída malformada. FFmpeg quebrado não é apresentado como pronto.
4. **Versão Node mínima incorreta:** readiness aceitava Node22.0, mas pacotes do lock exigem >=22.12.0. check_env passou a comparar a versão completa e orientar setup_tools hyperframes, com node-root real. Documentação deve dizer Node22.12+; coordenador avisado.
5. **Descoberta de instalações locais incompleta:** browserPath inclui Chrome x86/per-user, Edge ProgramFiles e caminhos usuais macOS. check_env localiza Blender Windows fora do PATH, em acordo com stack doctor (Blender5.3.0 confirmado).
6. **doctor interrompia relatório por pacote corrompido:** JSON inválido, lista ou objeto sem version agora geram installed:false/error por módulo e preservam o restante do diagnóstico. Probes Python usam -I e capturam erro/timeout; catálogo é carregado uma única vez.
7. **Teste preso a caminho pessoal antigo:** sound.test.mjs agora usa nodeRootFrom() e VIDEO_VIRAL_NODE_ROOT/default dedicado.
8. **CI sem cobertura audiovisual real:** workflow agora prepara FFmpeg, Node26 e stack npm ci fixado/ignore-scripts, verifica Chrome existente do runner e executa Python + testes reais Node. Sem serviços pagos/modelos. CI não executado remotamente; configuração revisada e comandos equivalentes locais passaram.

## Otimização medida e limites

Tone retorna agora Float32Array; sound.mjs transporta bytes IEEE-754 em base64 em vez de uma lista JSON de números. Node reconstrói Float32Array e mantém validateSamples + conversão PCM16 + publicação exclusivos já existentes. Sem alteração de sample-rate, canais, bits ou síntese. O transporte preserva até -0 (o transporte JSON antigo normalizava para 0, sem diferença PCM).

Benchmark reproduzível: `node tests/node/transport.bench.mjs`, com VIDEO_VIRAL_NODE_ROOT apontando o ambiente existente. Dados brutos: `../work/benchmark-node-transport.json`.

- Máquina: Windows, Node v26.12.0, Chrome/157.0.8103.51.
- Etapa isolada: transporte browser→Node de 30 s mono 44.100 Hz (1.323.000 amostras Float32), com sinal senoidal determinístico mantido no browser. Não mede síntese, bundle, abertura do Chrome nem render total.
- Aquecimento dos dois caminhos; cinco pares alternam a ordem para reduzir viés; cada par verifica igualdade binária de TODAS as amostras.
- Antes ms: 614.3149, 662.6967, 667.2282, 665.1221, 658.6987.
- Depois ms: 193.1186, 194.4355, 205.7832, 205.1694, 199.8981.
- Medianas: 662.6967 → 199.8981 ms; **redução 69,8357% nesta etapa**.
- Primeira rodada independente: 618.5240 → 194.9042 ms (-68,4888%). Não se afirma ganho equivalente no render completo.

Teste adicional executa Tone real completo com eventos whoosh/impact e duração fracionária, compara transporte antigo e novo e exige PCM16 byte a byte idêntico. Outro preserva floats especiais e assegura que NaN/Infinity continuam rejeitados. A suíte existente também gera áudio duas vezes e exige determinismo, valida cabeçalho/amplitude/duração/hash e preserva outputs em erro.

## Cobertura e verificações

Antes: `node --test tests/node/*.test.mjs`: **12/12** passaram (Chrome real, GLB real, Tone real, shaders e quatro adaptadores).

Depois: mesma suíte, VIDEO_VIRAL_NO_INSTALL=1: **14/14** passaram. Inclui perfil temporário profundo/limpeza, browser inexistente sem download, GLB otimizado e legível, recibo existente preservado, áudio determinístico e fracionário, validação de CLI, textura fornecida, seek2→0→2 idêntico em Pixi/Paper/p5/gl-transitions, timeline GSAP, disposal e preservação de diretório. HyperFrames lint real sem erro nas quatro cenas.

Python focado: test_stack.py **10/10**, test_setup_tools.py **14/14**; repetidos após ajustes pertinentes e sem instalações reais. Testes de setup passaram também com NO_INSTALL herdado=1, pois cada teste controla explicitamente seu ambiente.

Diagnósticos reais: stack doctor completo; check_env --json completo; localização Blender5.3 confirmada após correção. `git diff --check` limpo. Não se atribui aprovação estética a testes técnicos. BeginFrame não existe no Chrome157 instalado; screenshot real funcionou, confirmando a reserva já prevista.

## Assets somente leitura e limites remanescentes

- package.json/lock: todos os 11 pins diretos concordam; entradas HTTPs têm integrity; lockfile v3. Sem correção necessária identificada nos assets auditados.
- stack.json: catálogo/entrypoints coerentes com módulos escolhidos; 16 módulos, serviços externos continuam disponibilidade não inferida.
- assets/python: pins diretos/constraints e revisão ComfyUI têm formato coerente; não se instalou nem se prometeu resolução universal de todo upstream. Ambiente atual tem torch2.11 em venvs antigas, diferente do pin2.8 de instalação; preservado.
- Edge TTS não está instalado nas venvs detectadas; ComfyUI não está rodando. São estado do ambiente, sem autorização para instalar/iniciar nesta auditoria.
- Browser macOS/Linux e CI Linux não foram executados localmente; cobertura funcional local é Windows/Chrome157.
- glTF conserva compressão sem Draco/Meshopt/KTX2 e não implica aprovação de qualidade visual.
- Proibição de instalação continua bloqueando CLI HyperFrames por downloads internos de fontes; adaptadores locais continuam utilizáveis.

Disponível para revisão e correções no escopo atribuído.
