"""Instala as ferramentas que a skill usa, sem perguntar. Idempotente: o que já existe é pulado.

Uso: python scripts/setup_tools.py <grupo> [<grupo> ...]      # ou: --list
Grupos:
  base        FFmpeg, Node 22+ (HyperFrames) e yt-dlp no sistema (winget no Windows, brew/apt nos outros)
  legendas    venv 'legendas': faster-whisper (+ bibliotecas CUDA quando há GPU NVIDIA)
  voz         venv 'voz': Kokoro (torch com CUDA quando há GPU) + espeak-ng no sistema
  chatterbox  venv 'chatterbox': Chatterbox TTS (clonagem de voz)
  visao       venv 'visao': OpenCV (rastreio de rosto para enquadrar)
  blender     Blender no sistema
  hyperframes HyperFrames, three.js, Tone.js e puppeteer-core em ~/.video-viral/node (motion, 3D, efeitos)
  comfyui     ComfyUI + torch CUDA + SDXL base em ~/.video-viral/ComfyUI (imagens locais; ~12 GB)
As venvs ficam em ~/.video-viral/venvs/<nome> (Python 3.12 gerenciado pelo uv, que é instalado via pip se faltar).
Com VIDEO_VIRAL_NO_INSTALL=1 no ambiente, não instala nada (o usuário pediu para não instalar).
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
    "chatterbox": ("chatterbox", "3.11", ["chatterbox"], ["chatterbox-tts"], None),
    "visao": ("visao", "3.12", ["cv2", "numpy"], ["opencv-python-headless", "numpy"], None),
}
# programa -> (id winget, pacote brew, pacote apt)
SYSTEM = {
    "ffmpeg": ("Gyan.FFmpeg", "ffmpeg", "ffmpeg"),
    "node": ("OpenJS.NodeJS", "node", "nodejs"),
    "yt-dlp": ("yt-dlp.yt-dlp", "yt-dlp", "yt-dlp"),
    "espeak-ng": ("eSpeak-NG.eSpeak-NG", "espeak-ng", "espeak-ng"),
    "blender": ("BlenderFoundation.Blender", "blender", "blender"),
}
SYSTEM_GROUPS = {"base": ["ffmpeg", "node", "yt-dlp"], "voz": ["espeak-ng"], "blender": ["blender"]}


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
SDXL = "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors"


def install_hyperframes():
    """HyperFrames (+ GSAP, three.js, Tone.js, puppeteer-core) em ~/.video-viral/node."""
    if not install_program("node"):
        return False
    d = ROOT / "node"
    d.mkdir(parents=True, exist_ok=True)
    npm = shutil.which("npm") or shutil.which("npm.cmd") or "npm"
    ok = sh([npm, "install", "--prefix", d, "hyperframes", "three", "tone", "puppeteer-core"])
    print(f"[{'ok' if ok else '--'}] hyperframes em {d} (npx --prefix {d} hyperframes ...)")
    return ok


def install_comfyui():
    """ComfyUI + torch CUDA + checkpoint SDXL base (~7 GB) em ~/.video-viral/ComfyUI."""
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
        sh(UV + ["pip", "install", "--python", py, "torch", "torchvision", "torchaudio",
                 "--index-url", "https://download.pytorch.org/whl/cu128"])
    if not sh(UV + ["pip", "install", "--python", py, "-r", cdir / "requirements.txt"]):
        return False
    ck = cdir / "models" / "checkpoints" / "sd_xl_base_1.0.safetensors"
    if not ck.exists():
        part = ck.with_suffix(".part")
        if not sh(["curl", "-L", "--fail", "-o", part, SDXL]):
            return False
        part.rename(ck)
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
