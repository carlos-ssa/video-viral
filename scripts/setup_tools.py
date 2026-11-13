"""Instala seletivamente o stack v2 em ~/.video-viral.

Sistema e pip --user exigem --allow-system; ComfyUI exige --allow-large.
Sem consentimento, lista o plano inteiro e sai com 4 antes de qualquer instalação.
VIDEO_VIRAL_NO_INSTALL impede tudo. Não baixa checkpoints nem inicia serviços.
"""
import argparse
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import VENVS, venv_python  # noqa: E402

WIN = os.name == "nt"
NVIDIA = bool(shutil.which("nvidia-smi")) and platform.system() != "Darwin"
ROOT = Path.home() / ".video-viral"
PYTHON_ASSETS = Path(__file__).resolve().parents[1] / "assets" / "python"
CONSENT_REQUIRED = 4

# grupo -> (venv, Python, módulos de diagnóstico, requirements)
VENV_GROUPS = {
    "legendas": ("legendas", "3.12", ["faster_whisper"], "requirements-legendas.txt"),
    "voz": ("voz", "3.12", ["edge_tts"], "requirements-voz.txt"),
}
SYSTEM = {
    "ffmpeg": ("Gyan.FFmpeg", "ffmpeg", "ffmpeg"),
    "node": ("OpenJS.NodeJS", "node", "nodejs"),
    "blender": ("BlenderFoundation.Blender", "blender", "blender"),
}
SYSTEM_GROUPS = {"base": ["ffmpeg", "node"], "blender": ["blender"],
                 "hyperframes": ["node"]}


def sh(args, **kw):
    print("  $", " ".join(map(str, args)), flush=True)
    # Caches e Python gerenciado pelo uv ficam no ambiente dedicado, não no sistema.
    env = {**os.environ, "UV_CACHE_DIR": str(ROOT / "cache" / "uv"),
           "UV_PYTHON_INSTALL_DIR": str(ROOT / "python"), "npm_config_cache": str(ROOT / "cache" / "npm")}
    kw.setdefault("env", env)
    return subprocess.run(list(map(str, args)), **kw).returncode == 0


def has_program(name):
    if shutil.which(name):
        return True
    if WIN and name == "blender":
        return any(Path(os.environ.get("ProgramFiles", ""), "Blender Foundation").glob("*/blender.exe"))
    return False


def system_command(name):
    win_id, brew, apt = SYSTEM[name]
    if WIN and shutil.which("winget"):
        return ["winget", "install", "--id", win_id, "-e", "--silent",
                "--accept-source-agreements", "--accept-package-agreements"]
    if shutil.which("brew"):
        return ["brew", "install", brew]
    if shutil.which("apt-get"):
        return ["sudo", "-n", "apt-get", "install", "-y", apt]
    return None


def install_program(name, allow_system=False):
    if has_program(name):
        print(f"[ok] {name} já instalado")
        return True
    if not allow_system:
        raise PermissionError(f"{name}: confirme o plano e use --allow-system")
    command = system_command(name)
    if not command:
        print(f"[--] {name}: sem winget, brew ou apt-get; instale manualmente.")
        return False
    ok = sh(command)
    print(f"[{'ok' if ok else '--'}] {name}" + (" (abra um terminal novo se o PATH ainda não o mostrar)" if ok else ""))
    return ok


def uv_available():
    return bool(shutil.which("uv")) or importlib.util.find_spec("uv") is not None


def uv(allow_system=False):
    if shutil.which("uv"):
        return ["uv"]
    if not uv_available():
        if not allow_system:
            raise PermissionError("uv via pip --user exige --allow-system")
        if not sh([sys.executable, "-m", "pip", "install", "--user", "uv"]):
            raise RuntimeError("não foi possível instalar uv")
    return [sys.executable, "-m", "uv"]


def has_modules(py, mods):
    code = "import importlib.util,sys; sys.exit(0 if all(importlib.util.find_spec(m) for m in %r) else 1)" % mods
    return subprocess.run([str(py), "-c", code], capture_output=True).returncode == 0


def consent_plan(groups):
    """Diagnóstico sem subprocessos/alterações; lista também operações já autorizadas."""
    plan = []
    programs = dict.fromkeys(p for g in groups for p in SYSTEM_GROUPS.get(g, []))
    for name in programs:
        if not has_program(name):
            command = system_command(name)
            manager = " ".join(command) if command else "gerenciador indisponível (instalação manual)"
            plan.append(("--allow-system", f"{name}: {manager}; tamanho depende do pacote/SO"))
    if (set(groups) & (set(VENV_GROUPS) | {"comfyui"})) and not uv_available():
        plan.append(("--allow-system", "uv: python -m pip install --user uv; tamanho depende da plataforma"))
    if "comfyui" in groups:
        plan.append(("--allow-large", "ComfyUI + torch/torchvision/torchaudio: git + uv/pip em ~/.video-viral; "
                     "vários GB (aprox. 3–10 GB com CUDA, sem checkpoints; estimativa, não download medido)"))
    return plan


def install_venv(group, allow_system=False):
    name, pyver, mods, requirements = VENV_GROUPS[group]
    UV = uv(allow_system)
    root = VENVS / name
    py = venv_python(name)
    if not py and not sh(UV + ["venv", root, "--python", pyver]):
        return False
    py = venv_python(name)
    if not py:
        return False
    # Reaplica os requisitos fixados mesmo quando os módulos já existem.
    reqs = ["-r", PYTHON_ASSETS / requirements]
    if group == "legendas" and NVIDIA:
        reqs += ["-r", PYTHON_ASSETS / "requirements-cuda.txt"]
    ok = sh(UV + ["pip", "install", "--python", py, *reqs]) and has_modules(py, mods)
    print(f"[{'ok' if ok else '--'}] venv '{name}': {py}")
    return ok


def install_hyperframes(allow_system=False):
    if not install_program("node", allow_system):
        return False
    d = Path(os.environ.get("VIDEO_VIRAL_NODE_ROOT", str(ROOT / "node-v2")))
    d.mkdir(parents=True, exist_ok=True)
    npm = shutil.which("npm") or shutil.which("npm.cmd") or "npm"
    template = Path(__file__).resolve().parents[1] / "assets" / "node"
    if (d / "package.json").exists():
        current = json.loads((d / "package.json").read_text(encoding="utf-8"))
        if current.get("name") != "video-viral-stack":
            print("Use pasta dedicada; package.json desconhecido não será sobrescrito.")
            return False
    shutil.copy2(template / "package.json", d / "package.json")
    shutil.copy2(template / "package-lock.json", d / "package-lock.json")
    ok = sh([npm, "ci", "--prefix", d, "--ignore-scripts", "--no-audit", "--no-fund"])
    if ok:
        ok = sh([d / "node_modules" / ".bin" / ("esbuild.cmd" if WIN else "esbuild"), "--version"])
    print(f"[{'ok' if ok else '--'}] stack Node v2 em {d}")
    return ok


def install_comfyui(allow_system=False, allow_large=False):
    if not allow_large:
        raise PermissionError("ComfyUI exige --allow-large, inclusive sem checkpoints")
    revision = json.loads((PYTHON_ASSETS / "comfyui.json").read_text(encoding="utf-8"))
    cdir = ROOT / "ComfyUI"
    if cdir.exists():
        # Preserva instalações existentes; não faz checkout/reset sobre mudanças do usuário.
        result = subprocess.run(["git", "-C", str(cdir), "rev-parse", "HEAD"], capture_output=True, text=True)
        dirty = subprocess.run(["git", "-C", str(cdir), "status", "--porcelain"], capture_output=True, text=True)
        if result.returncode or dirty.returncode or result.stdout.strip() != revision["commit"] or dirty.stdout.strip():
            print("ComfyUI existente difere do commit fixado ou tem alterações; preserve/migre manualmente.")
            return False
    else:
        if not sh(["git", "clone", "--depth", "1", "--branch", revision["tag"], revision["repository"], cdir]):
            return False
        result = subprocess.run(["git", "-C", str(cdir), "rev-parse", "HEAD"], capture_output=True, text=True)
        if result.returncode or result.stdout.strip() != revision["commit"]:
            print("Tag ComfyUI não corresponde ao commit fixado; instalação interrompida.")
            return False
    UV = uv(allow_system)
    py = venv_python("comfyui")
    if not py and not sh(UV + ["venv", VENVS / "comfyui", "--python", "3.12"]):
        return False
    py = venv_python("comfyui")
    if not py:
        return False
    index = ["--index-url", "https://download.pytorch.org/whl/cu128"] if NVIDIA else []
    if not sh(UV + ["pip", "install", "--python", py, "-r", PYTHON_ASSETS / "requirements-comfyui-torch.txt", *index]):
        return False
    # Constraints impedem que requirements.txt upstream desfaça nossos pins diretos.
    return sh(UV + ["pip", "install", "--python", py, "-r", cdir / "requirements.txt",
                    "-c", PYTHON_ASSETS / "constraints-comfyui.txt"])


CUSTOM_GROUPS = {"hyperframes": install_hyperframes, "comfyui": install_comfyui}


def main():
    groups = sorted(set(VENV_GROUPS) | set(SYSTEM_GROUPS) | set(CUSTOM_GROUPS))
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("groups", nargs="*", metavar="grupo")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--allow-system", action="store_true", help="consentimento para sistema e pip --user")
    ap.add_argument("--allow-large", action="store_true", help="consentimento para ComfyUI e dependências grandes")
    a = ap.parse_args()
    if a.list or not a.groups or set(a.groups) - set(groups):
        print("Grupos:", ", ".join(groups))
        return 0 if a.list else 2
    if os.environ.get("VIDEO_VIRAL_NO_INSTALL"):
        print("VIDEO_VIRAL_NO_INSTALL definido: nada instalado. Siga com as reservas.")
        return 1
    plan = consent_plan(a.groups)
    for flag, description in plan:
        print(f"[plano {flag}] {description}")
    if any(not (a.allow_system if flag == "--allow-system" else a.allow_large) for flag, _ in plan):
        print("CONSENTIMENTO PENDENTE: nada instalado. Peça confirmação única desta lista antes de usar as flags.")
        return CONSENT_REQUIRED
    VENVS.mkdir(parents=True, exist_ok=True)
    fails = []
    for g in dict.fromkeys(a.groups):
        print(f"== {g}")
        try:
            ok = all([install_program(p, a.allow_system) for p in SYSTEM_GROUPS.get(g, [])])
            if ok and g in VENV_GROUPS:
                ok = install_venv(g, a.allow_system)
            if ok and g == "hyperframes":
                ok = install_hyperframes(a.allow_system)
            if ok and g == "comfyui":
                ok = install_comfyui(a.allow_system, a.allow_large)
        except (OSError, RuntimeError) as exc:
            print(f"[--] {g}: {exc}")
            ok = False
        if not ok:
            fails.append(g)
    if fails:
        print(f"Não ficou pronto: {', '.join(fails)}. Siga com as reservas e cite no relatório.")
        return 1
    print("Tudo pronto.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
