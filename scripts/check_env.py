"""Mostra quais etapas do pipeline estão prontas nesta máquina. Só diagnostica: quem instala é setup_tools.py.

Uso: python scripts/check_env.py [--python caminho/para/python] [--json]
Procura também as venvs em ~/.video-viral/venvs/<nome> (e na pasta antiga ~/.ai-shorts/venvs).
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

PROBE = r"""
import importlib.util, json
mods = ["kokoro", "soundfile", "numpy", "faster_whisper", "torch"]
out = {m: importlib.util.find_spec(m) is not None for m in mods}
if out["torch"]:
    try:
        import torch
        out["cuda"] = bool(torch.cuda.is_available())
        out["torch_version"] = torch.__version__
    except Exception as e:
        out["cuda"] = False
        out["torch_error"] = str(e)[:200]
print(json.dumps(out))
"""


def cmd_version(cmd, args=("-version",)):
    exe = shutil.which(cmd)
    if not exe:
        return None
    try:
        r = subprocess.run([exe, *args], capture_output=True, text=True, timeout=20, errors="replace")
        return (r.stdout or r.stderr).strip().splitlines()[0] if (r.stdout or r.stderr) else "ok"
    except Exception:
        return "ok"


def espeak():
    if shutil.which("espeak-ng"):
        return True
    for base in (os.environ.get("ProgramFiles", ""), os.environ.get("ProgramFiles(x86)", "")):
        if base and Path(base, "eSpeak NG", "espeak-ng.exe").exists():
            return True
    return False


def gpu():
    exe = shutil.which("nvidia-smi")
    if not exe:
        return None
    r = subprocess.run([exe, "--query-gpu=name,memory.total,memory.used", "--format=csv,noheader,nounits"],
                       capture_output=True, text=True, errors="replace")
    if r.returncode != 0 or not r.stdout.strip():
        return None
    name, total, used = [x.strip() for x in r.stdout.strip().splitlines()[0].split(",")]
    return {"name": name, "vram_mb": int(total), "free_mb": int(total) - int(used)}


def pythons(extra):
    cands = [Path(sys.executable)]
    if extra:
        cands.insert(0, Path(extra))
    for root in (Path.home() / ".video-viral" / "venvs", Path.home() / ".ai-shorts" / "venvs"):
        if not root.is_dir():
            continue
        for v in sorted(root.iterdir()):
            for rel in ("Scripts/python.exe", "bin/python"):
                if (v / rel).exists():
                    cands.append(v / rel)
    seen, out = set(), []
    for c in cands:
        k = str(c.resolve()) if c.exists() else str(c)
        if k in seen or not c.exists():
            continue
        seen.add(k)
        try:
            r = subprocess.run([str(c), "-c", PROBE], capture_output=True, text=True, timeout=180, errors="replace")
            info = json.loads(r.stdout.strip().splitlines()[-1])
        except Exception as e:
            info = {"error": str(e)[:200]}
        out.append({"python": str(c), **info})
    return out


def comfyui():
    try:
        with urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=1.5) as r:
            return r.status == 200
    except Exception:
        return False


def major(v, pat):
    m = re.search(pat, v or "")
    return int(m.group(1)) if m else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--python", help="Python de uma venv com as ferramentas de voz/legenda")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    tools = {
        "ffmpeg": cmd_version("ffmpeg"),
        "ffprobe": cmd_version("ffprobe"),
        "node": cmd_version("node", ("--version",)),
        "npx": bool(shutil.which("npx")),
        "blender": cmd_version("blender", ("--version",)),
        "uv": cmd_version("uv", ("--version",)),
        "espeak-ng": espeak(),
    }
    g = gpu()
    pys = pythons(a.python)
    comfy = comfyui()

    def py_with(*mods):
        return next((p["python"] for p in pys if all(p.get(m) for m in mods)), None)

    ff_ok = bool(tools["ffmpeg"]) and bool(tools["ffprobe"])
    node_major = major(tools["node"], r"v(\d+)")
    voice_py = py_with("kokoro", "soundfile", "numpy")
    cap_py = py_with("faster_whisper")
    node_root = Path(os.environ.get("VIDEO_VIRAL_NODE_ROOT", str(Path.home() / ".video-viral/node-v2")))
    hf_package = node_root / "node_modules/hyperframes/package.json"
    stages = [
        ("3 Voz (Kokoro)", bool(voice_py) and tools["espeak-ng"],
         voice_py or "setup_tools.py voz"),
        ("4 Legendas (faster-whisper)", bool(cap_py), cap_py or "setup_tools.py legendas"),
        ("5 Visual (HyperFrames)", node_major >= 22 and ff_ok and hf_package.is_file(), f"node {tools['node'] or 'ausente'}; precisa 22+ (setup_tools.py base)"),
        ("5 Visual (Blender, opcional)", bool(tools["blender"]), tools["blender"] or "setup_tools.py blender"),
        ("5 Visual (ComfyUI, opcional)", comfy, "rodando em 127.0.0.1:8188" if comfy else "não está rodando"),
        ("7 Entregar (FFmpeg)", ff_ok, tools["ffmpeg"] or "ffmpeg ausente"),
    ]

    if a.json:
        print(json.dumps({"tools": tools, "gpu": g, "pythons": pys, "comfyui": comfy,
                          "stages": [{"stage": s, "ready": r, "detail": d} for s, r, d in stages]},
                         ensure_ascii=False, indent=2))
        return

    print("GPU:", f"{g['name']}, {g['vram_mb']} MB ({g['free_mb']} MB livres)" if g else "nenhuma NVIDIA detectada")
    if g and g["vram_mb"] < 10000:
        print("  VRAM até ~8 GB: um modelo pesado de GPU por vez; selecione o perfil ACE-Step/ComfyUI.")
    for p in pys:
        flags = [m for m in ("kokoro", "faster_whisper", "torch") if p.get(m)]
        cuda = " cuda" if p.get("cuda") else ""
        print(f"Python {p['python']}: {', '.join(flags) or 'nenhuma ferramenta de IA'}{cuda}")
    print()
    for s, ready, detail in stages:
        print(f"[{'ok' if ready else '--'}] {s}: {detail if not ready or s.startswith(('3', '4')) else 'pronto'}")
    print("\nPara módulos JS, execute stack.py doctor --node-root <pasta>; Node instalado não comprova pacote nem render validado.")
    fallbacks = []
    if not (voice_py and tools["espeak-ng"]):
        fallbacks.append("voz: forneça WAVs e use voice.py --from-wavs; não há outro motor automático")
    if not cap_py:
        fallbacks.append("legendas: captions.py estimate (tempos aproximados)")
    if node_major < 22:
        fallbacks.append("visual: ambiente HyperFrames indisponível; base FFmpeg é rascunho, não acabamento aprovado")
    if fallbacks and ff_ok:
        print("\nInstale somente o que a tarefa usa e é permitido: python scripts/setup_tools.py <grupo...>. "
              "Se falhar ou o usuário pediu para não instalar, siga com as reservas:")
        for f in fallbacks:
            print(f"  reserva {f}")


if __name__ == "__main__":
    main()
