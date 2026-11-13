"""Instala somente componentes do stack v2, de forma seletiva.

Grupos: base (FFmpeg/Node), voz (Kokoro), legendas (faster-whisper), blender,
hyperframes (stack Node com lockfile), comfyui (runtime sem checkpoints).
VIDEO_VIRAL_NO_INSTALL=1 impede instalação. ACE-Step e MCP são serviços configurados à parte.
"""
import argparse
import importlib.util
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

# grupo -> (venv, versão do Python, módulos que provam a instalação, pacotes, índice extra)
VENV_GROUPS = {
    "legendas": ("legendas", "3.12", ["faster_whisper"],
                 ["faster-whisper", "numpy"] + (["nvidia-cublas-cu12", "nvidia-cudnn-cu12==9.*"] if NVIDIA else []), None),
    "voz": ("voz", "3.12", ["kokoro", "soundfile", "numpy"], ["kokoro>=0.9.4", "soundfile", "numpy"],
            "https://download.pytorch.org/whl/cu128" if NVIDIA else None),
}
# programa -> (id winget, pacote brew, pacote apt)
SYSTEM = {
    "ffmpeg": ("Gyan.FFmpeg", "ffmpeg", "ffmpeg"),
    "node": ("OpenJS.NodeJS", "node", "nodejs"),
    "espeak-ng": ("eSpeak-NG.eSpeak-NG", "espeak-ng", "espeak-ng"),
    "blender": ("BlenderFoundation.Blender", "blender", "blender"),
}
SYSTEM_GROUPS = {"base": ["ffmpeg", "node"], "voz": ["espeak-ng"], "blender": ["blender"]}


def sh(args, **kw):
    print("  $", " ".join(map(str, args)), flush=True)
    return subprocess.run(list(map(str, args)), **kw).returncode == 0


def has_program(name):
    if shutil.which(name):
        return True
    if WIN and name == "espeak-ng":
        return any(Path(b, "eSpeak NG", "espeak-ng.exe").exists()
                   for b in (os.environ.get("ProgramFiles", ""), os.environ.get("ProgramFiles(x86)", "")) if b)
    if WIN and name == "blender":
        return any(Path(os.environ.get("ProgramFiles", ""), "Blender Foundation").glob("*/blender.exe"))
    return False


def install_program(name):
    if has_program(name):
        print(f"[ok] {name} já instalado")
        return True
    win_id, brew, apt = SYSTEM[name]
    if WIN and shutil.which("winget"):
        ok = sh(["winget", "install", "--id", win_id, "-e", "--silent",
                 "--accept-source-agreements", "--accept-package-agreements"])
    elif shutil.which("brew"):
        ok = sh(["brew", "install", brew])
    elif shutil.which("apt-get"):
        ok = sh(["sudo", "-n", "apt-get", "install", "-y", apt])
    else:
        print(f"[--] {name}: sem winget, brew ou apt-get nesta máquina; instale manualmente.")
        return False
    print(f"[{'ok' if ok else '--'}] {name}" + (" (abra um terminal novo se o PATH ainda não o mostrar)" if ok else ""))
    return ok


def uv():
    """Comando do uv: o do PATH, ou `python -m uv` (instala via pip se faltar)."""
    if shutil.which("uv"):
        return ["uv"]
    if importlib.util.find_spec("uv") is None:
        sh([sys.executable, "-m", "pip", "install", "--user", "--quiet", "uv"])
    if importlib.util.find_spec("uv") is None and WIN and shutil.which("winget"):
        sh(["winget", "install", "--id", "astral-sh.uv", "-e", "--silent",
            "--accept-source-agreements", "--accept-package-agreements"])
        if shutil.which("uv"):
            return ["uv"]
    return [sys.executable, "-m", "uv"]


def has_modules(py, mods):
    code = "import importlib.util,sys; sys.exit(0 if all(importlib.util.find_spec(m) for m in %r) else 1)" % mods
    return subprocess.run([str(py), "-c", code], capture_output=True).returncode == 0


def install_venv(group):
    name, pyver, mods, pkgs, torch_index = VENV_GROUPS[group]
    py = venv_python(name)
    if py and has_modules(py, mods):
        print(f"[ok] venv '{name}' pronta: {py}")
        return True
    UV = uv()
    root = VENVS / name
    if not py and not sh(UV + ["venv", root, "--python", pyver]):
        return False
    py = venv_python(name)
    if torch_index:
        sh(UV + ["pip", "install", "--python", py, "torch", "torchaudio", "--index-url", torch_index])
    ok = sh(UV + ["pip", "install", "--python", py, *pkgs]) and has_modules(py, mods)
    print(f"[{'ok' if ok else '--'}] venv '{name}': {py}")
    return ok


ROOT = Path.home() / ".video-viral"


def install_hyperframes():
    """HyperFrames (+ GSAP, three.js, Tone.js, puppeteer-core) em ~/.video-viral/node."""
    if not install_program("node"):
        return False
    d = Path(os.environ.get("VIDEO_VIRAL_NODE_ROOT", str(ROOT / "node-v2")))
    d.mkdir(parents=True, exist_ok=True)
    npm = shutil.which("npm") or shutil.which("npm.cmd") or "npm"
    import json
    template = Path(__file__).resolve().parents[1] / "assets" / "node"
    if (d / "package.json").exists():
        current = json.loads((d / "package.json").read_text(encoding="utf-8"))
        if current.get("name") != "video-viral-stack":
            print("Use uma pasta dedicada para o stack v2; package.json existente não será sobrescrito.")
            return False
    shutil.copy2(template / "package.json", d / "package.json")
    shutil.copy2(template / "package-lock.json", d / "package-lock.json")
    ok = sh([npm, "ci", "--prefix", d, "--ignore-scripts", "--no-audit", "--no-fund"])
    if ok:
        ok = sh([d / "node_modules" / ".bin" / ("esbuild.cmd" if WIN else "esbuild"), "--version"])
    print(f"[{'ok' if ok else '--'}] stack Node v2 em {d}")
    return ok


def install_comfyui():
    """Runtime ComfyUI sem download automático de modelos."""
    cdir = ROOT / "ComfyUI"
    if not (cdir / "main.py").exists() and not sh(["git", "clone", "--depth", "1",
                                                     "https://github.com/Comfy-Org/ComfyUI", cdir]):
        return False
    UV = uv()
    py = venv_python("comfyui")
    if not py and not sh(UV + ["venv", VENVS / "comfyui", "--python", "3.12"]):
        return False
    py = venv_python("comfyui")
    if not has_modules(py, ["torch"]):
        torch_args = ["--index-url", "https://download.pytorch.org/whl/cu128"] if NVIDIA else []
        sh(UV + ["pip", "install", "--python", py, "torch", "torchvision", "torchaudio", *torch_args])
    if not sh(UV + ["pip", "install", "--python", py, "-r", cdir / "requirements.txt"]):
        return False
    print(f"[ok] ComfyUI em {cdir}")
    return True


CUSTOM_GROUPS = {"hyperframes": install_hyperframes, "comfyui": install_comfyui}


def main():
    groups = sorted(set(VENV_GROUPS) | set(SYSTEM_GROUPS) | set(CUSTOM_GROUPS))
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("groups", nargs="*", metavar="grupo")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list or not a.groups or set(a.groups) - set(groups):
        print("Grupos:", ", ".join(groups))
        sys.exit(0 if a.list else 2)
    if os.environ.get("VIDEO_VIRAL_NO_INSTALL"):
        sys.exit("VIDEO_VIRAL_NO_INSTALL definido: nada instalado. Siga com as reservas do SKILL.md.")
    VENVS.mkdir(parents=True, exist_ok=True)
    fails = []
    for g in a.groups:
        print(f"== {g}")
        ok = all([install_program(p) for p in SYSTEM_GROUPS.get(g, [])])
        if g in VENV_GROUPS:
            ok = install_venv(g) and ok
        if g in CUSTOM_GROUPS:
            ok = CUSTOM_GROUPS[g]() and ok
        if not ok:
            fails.append(g)
    if fails:
        sys.exit(f"Não ficou pronto: {', '.join(fails)}. Siga com as reservas e cite isso no relatório.")
    print("Tudo pronto.")


if __name__ == "__main__":
    main()
