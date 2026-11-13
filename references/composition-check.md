# Quadros de estilo e teste de seek — HyperFrames 0.9.40

Execute a partir da pasta da skill, com browser/cache/fontes locais preparados conforme [setup](setup.md#browser-cache-e-execução-sem-rede). Use somente `stack.py hyperframes --node-root <pasta> -- <comando>`. Com `VIDEO_VIRAL_NO_INSTALL` não vazio, a CLI fica bloqueada (inclusive snapshot/screenshot); não contorne a proibição. Os adaptadores Puppeteer locais continuam disponíveis, mas não substituem os testes do runtime completo descritos aqui. Não instale dependências para este teste. Use diretórios novos por rodada: `snapshot --output` limpa os stills anteriores daquela pasta.

## Aprovar três quadros antes do filme inteiro

Escolha início com gancho, maior carga de texto/ação e payoff. No exemplo de 12 s, capture 0, 5 e 10 s; substitua pelos tempos reais, sempre menores que a duração:

```sh
python scripts/stack.py hyperframes --node-root "<node-root>" -- snapshot "<projeto>/composition" \
  --at 0,5,10 --no-end --output "<projeto>/research/style-r01"
```

Abra os três PNGs e a prancha gerada. Compare com referências autorizadas do formato; confira as [regras de acabamento](composition.md#regras-de-acabamento-obrigatórias), inclusive fonte efetiva, quadro inteiro, duas linhas de legenda e colisões. Capture também a legenda mais longa se ela não estiver nesses tempos. Só prossiga após resolver diferenças essenciais; uma prancha estática não prova movimento, áudio ou lip-sync.

## Buscar 2 → 0 → 2 na mesma sessão

A implementação de `snapshot` 0.9.40 preserva a ordem e as repetições de `--at`. Não use `--keep`: ele não aceita instantes repetidos. `--no-end` impede acrescentar outro tempo. Para filme com menos de 2 s, use um instante interno nas duas posições correspondentes e ajuste os nomes abaixo.

```sh
python scripts/stack.py hyperframes --node-root "<node-root>" -- snapshot "<projeto>/composition" \
  --at 2,0,2 --no-end --output "<projeto>/research/seek-r01"
```

Confira no log que houve seek, sem “No player API”, timeout, fontes falhas ou mídia preta/stale. A sequência deve gerar `frame-00-at-2s.png`, `frame-01-at-0s.png` e `frame-02-at-2s.png`. Compare **pixels decodificados**, não só tamanho/hash do PNG. Este pequeno harness usa apenas Python e FFmpeg existentes (Git Bash/POSIX):

```sh
python - "<projeto>/research/seek-r01" <<'PY'
from pathlib import Path
import hashlib
import subprocess
import sys

folder = Path(sys.argv[1])
def pixels(name):
    return subprocess.run([
        "ffmpeg", "-v", "error", "-i", str(folder / name),
        "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgba", "pipe:1"
    ], check=True, stdout=subprocess.PIPE).stdout

a = pixels("frame-00-at-2s.png")
b = pixels("frame-02-at-2s.png")
if not a or len(a) != len(b):
    raise SystemExit("FALHOU: captura vazia ou dimensões diferentes")
changed = sum(a[i:i+4] != b[i:i+4] for i in range(0, len(a), 4))
print("Pixels diferentes:", changed)
print("SHA256 RGBA:", hashlib.sha256(a).hexdigest(), hashlib.sha256(b).hexdigest())
raise SystemExit(1 if changed else 0)
PY
```

Exija **0 pixels diferentes** no mesmo ambiente. Repita para fronteiras de cena e efeitos que começam depois de 2 s (por exemplo 7 → 0 → 7). Se falhar, corrija estado inicial/final, seed, callbacks dependentes do histórico, máscara/rig, carregamento de fontes/texturas e visibilidade; não aumente a tolerância para esconder deriva.

Registre comando, tempos, hashes, browser, versão e resultado real em `research/`. Vídeos e composições aninhadas exigem mídia pronta e seek do runtime completo: não substitua por `totalTime()` numa página bruta sem controlar esses recursos. Compare ainda os mesmos instantes **decodificados do MP4 renderizado**; o snapshot pode injetar quadros de vídeo por outra rota e não valida sozinho o encoder. Na falta de frame de mídia legível, marque o teste como incompleto, não aprovado.
