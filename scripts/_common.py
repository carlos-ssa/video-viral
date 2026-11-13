"""Funções compartilhadas pelos scripts da skill video-viral (só biblioteca padrão)."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

SKILL_DIR = Path(__file__).resolve().parent.parent
VENVS = Path.home() / ".video-viral" / "venvs"


def venv_python(name: str):
    """Python da venv ~/.video-viral/venvs/<name> (ou da pasta antiga ~/.ai-shorts), ou None."""
    for root in (VENVS, Path.home() / ".ai-shorts" / "venvs"):
        for rel in ("Scripts/python.exe", "bin/python"):
            if (root / name / rel).exists():
                return root / name / rel
    return None


def use_venv(group: str, modules: list) -> None:
    """Se faltam `modules` neste Python, roda o mesmo comando com o Python da venv do grupo.

    Instala a venv com setup_tools.py se ela não existir (a skill instala sozinha o que precisa, salvo
    VIDEO_VIRAL_NO_INSTALL=1). Volta sem fazer nada se não conseguir: quem chamou segue com a reserva.
    """
    import importlib.util
    import os
    if all(importlib.util.find_spec(m) for m in modules) or os.environ.get("VIDEO_VIRAL_IN_VENV"):
        return
    probe = "import importlib.util,sys; sys.exit(0 if all(importlib.util.find_spec(m) for m in %r) else 1)" % modules
    ok = lambda py: py and subprocess.run([str(py), "-c", probe], capture_output=True).returncode == 0  # noqa: E731
    py = venv_python(group)
    if not ok(py) and not os.environ.get("VIDEO_VIRAL_NO_INSTALL"):
        print(f"Faltam {', '.join(modules)}: instalando o grupo '{group}' (scripts/setup_tools.py)...", flush=True)
        subprocess.run([sys.executable, str(SKILL_DIR / "scripts" / "setup_tools.py"), group])
        py = venv_python(group)
    if ok(py):
        print(f"Usando o Python da venv '{group}': {py}", flush=True)
        env = {**os.environ, "VIDEO_VIRAL_IN_VENV": "1"}
        sys.exit(subprocess.run([str(py), *sys.argv], env=env).returncode)
TEMPLATE = SKILL_DIR / "assets" / "video.template.json"
MANIFEST, LEGACY_MANIFEST = "video.json", "short.json"

ASPECTS = {"9:16": (1080, 1920), "16:9": (1920, 1080), "1:1": (1080, 1080), "4:5": (1080, 1350)}

# Limites usados nas checagens (segundos) e formatos de tela aceitos. Confira references/platforms.md.
PLATFORMS = {
    "tiktok": {"aspects": ["9:16"], "limit": 600},
    "reels": {"aspects": ["9:16"], "limit": 180},
    "shorts": {"aspects": ["9:16", "1:1"], "limit": 180},
    "kwai": {"aspects": ["9:16"], "limit": 600},
    "youtube": {"aspects": ["16:9"], "limit": 12 * 3600},
    "feed": {"aspects": ["4:5", "1:1"], "limit": 3600},
}

FORMATS = ["narrado", "gravacao", "corte", "produto", "ugc", "storytelling", "musica", "avatar"]


def safe_area(w: int, h: int) -> dict:
    """Margens que a interface das plataformas cobre e a linha de base da legenda (y em pixels)."""
    if h > w * 1.5:  # 9:16: Instagram é o mais restritivo (references/platforms.md)
        sx, sy = w / 1080, h / 1920
        m = {"top": 250 * sy, "bottom": 420 * sy, "left": 90 * sx, "right": 150 * sx}
        m["caption_y"] = 1400 * sy
    else:  # 16:9, 1:1, 4:5: margem de título de 5% e barra de progresso embaixo
        m = {"top": 0.05 * h, "bottom": 0.08 * h, "left": 0.05 * w, "right": 0.05 * w}
        m["caption_y"] = h - 0.1 * h
    return {k: int(round(v)) for k, v in m.items()}


def manifest_path(proj: Path) -> Path:
    if not (proj / MANIFEST).exists() and (proj / LEGACY_MANIFEST).exists():
        return proj / LEGACY_MANIFEST
    return proj / MANIFEST


def project_dir(arg: str) -> Path:
    p = Path(arg).expanduser().resolve()
    if p.is_file() and p.name in (MANIFEST, LEGACY_MANIFEST):
        p = p.parent
    if not manifest_path(p).exists():
        sys.exit(f"Não achei {MANIFEST} em {p}. Crie o projeto com scripts/new_project.py.")
    return p


def load_manifest(proj: Path) -> dict:
    return json.loads(manifest_path(proj).read_text(encoding="utf-8"))


def save_manifest(proj: Path, m: dict) -> None:
    path = manifest_path(proj)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def add_asset(m: dict, path: str, kind: str, source: str, license_: str, commercial_ok) -> None:
    """Registra ou atualiza um ativo pelo caminho. commercial_ok: True só com licença comercial confirmada."""
    entry = {"path": path, "kind": kind, "source": source, "license": license_, "commercial_ok": commercial_ok}
    assets = m.setdefault("assets", [])
    for i, a in enumerate(assets):
        if a.get("path") == path:
            assets[i] = entry
            return
    assets.append(entry)


def need(cmd: str) -> str:
    exe = shutil.which(cmd)
    if not exe:
        sys.exit(f"'{cmd}' não encontrado no PATH. Veja references/setup.md.")
    return exe


def run(args: list, cwd=None, check=True) -> subprocess.CompletedProcess:
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode != 0:
        tail = "\n".join(r.stderr.strip().splitlines()[-15:])
        sys.exit(f"Falhou ({r.returncode}): {' '.join(map(str, args[:4]))} ...\n{tail}")
    return r


def ffprobe_json(path: Path) -> dict:
    r = run([need("ffprobe"), "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)])
    return json.loads(r.stdout)
