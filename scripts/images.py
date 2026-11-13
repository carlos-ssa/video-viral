"""Gera imagens locais com o ComfyUI (SDXL na GPU) para cenas, fundos e inserts.

Uso: python scripts/images.py <projeto> [--spec edit/images.json] [--out assets/img]
spec = [{"id": "robo", "prompt": "...", "negative": "...", "w": 832, "h": 1216, "seed": 7, "steps": 30}]
Saída: <out>/<id>.png e registro em video.json["assets"] (licença: gerada localmente, SDXL base).

Sobe o servidor do ComfyUI (127.0.0.1:8188) se ele não estiver no ar e instala o grupo 'comfyui'
com setup_tools.py se faltar (salvo VIDEO_VIRAL_NO_INSTALL=1). Pula ids que já têm arquivo (--force refaz).
"""
import argparse
import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import SKILL_DIR, load_manifest, save_manifest, venv_python  # noqa: E402

HOST = "http://127.0.0.1:8188"
ROOT = Path.home() / ".video-viral" / "ComfyUI"
CKPT = "sd_xl_base_1.0.safetensors"
NEG = "text, watermark, logo, letters, blurry, lowres, deformed, extra fingers, jpeg artifacts"


def up():
    try:
        urllib.request.urlopen(HOST + "/system_stats", timeout=3)
        return True
    except Exception:
        return False


def ensure_server():
    if up():
        return None
    import os
    py = venv_python("comfyui")
    if (not py or not (ROOT / "main.py").exists()) and not os.environ.get("VIDEO_VIRAL_NO_INSTALL"):
        subprocess.run([sys.executable, str(SKILL_DIR / "scripts" / "setup_tools.py"), "comfyui"])
        py = venv_python("comfyui")
    if not py or not (ROOT / "main.py").exists():
        sys.exit("ComfyUI indisponível: rode setup_tools.py comfyui ou use imagens de banco (references/stack.md)")
    log = open(ROOT / "server.log", "a", encoding="utf-8")
    proc = subprocess.Popen([str(py), "main.py", "--listen", "127.0.0.1", "--port", "8188",
                             "--disable-auto-launch"], cwd=ROOT, stdout=log, stderr=log)
    for _ in range(180):
        if up():
            return proc
        time.sleep(1)
    sys.exit("o ComfyUI não respondeu em 3 min; veja " + str(ROOT / "server.log"))


def graph(it):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": it.get("ckpt", CKPT)}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": it["prompt"], "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": it.get("negative", NEG), "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": it.get("w", 832), "height": it.get("h", 1216),
                                                          "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0],
            "seed": it.get("seed", 7), "steps": it.get("steps", 30), "cfg": it.get("cfg", 6.5),
            "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "vv_" + it["id"]}},
    }


def run(it, dest):
    body = json.dumps({"prompt": graph(it)}).encode()
    pid = json.load(urllib.request.urlopen(urllib.request.Request(
        HOST + "/prompt", body, {"Content-Type": "application/json"})))["prompt_id"]
    for _ in range(900):
        h = json.load(urllib.request.urlopen(f"{HOST}/history/{pid}"))
        if pid in h and h[pid].get("outputs"):
            img = h[pid]["outputs"]["7"]["images"][0]
            q = urllib.parse.urlencode({k: img[k] for k in ("filename", "subfolder", "type")})
            dest.write_bytes(urllib.request.urlopen(f"{HOST}/view?{q}").read())
            return
        if pid in h and h[pid].get("status", {}).get("status_str") == "error":
            sys.exit(f"erro no ComfyUI em {it['id']}: {h[pid]['status']}")
        time.sleep(1)
    sys.exit(f"tempo esgotado em {it['id']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--spec", default="edit/images.json")
    ap.add_argument("--out", default="assets/img")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    proj = Path(a.project)
    spec = json.loads((proj / a.spec).read_text(encoding="utf-8"))
    out = proj / a.out
    out.mkdir(parents=True, exist_ok=True)
    todo = [it for it in spec if a.force or not (out / f"{it['id']}.png").exists()]
    proc = ensure_server() if todo else None
    man = load_manifest(proj)
    for it in todo:
        t = time.time()
        run(it, out / f"{it['id']}.png")
        print(f"{out / (it['id'] + '.png')} ({time.time() - t:.0f}s)", flush=True)
        rec = {"path": str(out / f"{it['id']}.png"), "kind": "image", "source": "ComfyUI SDXL base (local)",
               "license": "gerada localmente (CreativeML Open RAIL++-M)", "commercial_ok": True, "prompt": it["prompt"]}
        man["assets"] = [x for x in man.get("assets", []) if x.get("path") != rec["path"]] + [rec]
    save_manifest(proj, man)
    if proc:
        proc.terminate()


if __name__ == "__main__":
    main()
