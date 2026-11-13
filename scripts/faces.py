"""Rastreia o rosto na gravação para enquadrar (YuNet do OpenCV, roda na CPU).

Uso: python scripts/faces.py <projeto> [--step 0.2]
Saída: edit/faces.json = {"w","h","step","track":[{"t","cx","cy","fw","fh","eye_y","ok"}]}
Coordenadas normalizadas (0-1) no quadro da gravação; trilha suavizada e sem buracos.
Use cx/cy para centralizar recortes e fw/fh para decidir zoom e onde a legenda não cobre o rosto.
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_manifest, use_venv  # noqa: E402

MODEL_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
MODEL = Path.home() / ".video-viral" / "models" / "face_detection_yunet_2023mar.onnx"


def smooth(vals, ok, win):
    """Preenche buracos com o último valor bom e aplica média móvel centrada."""
    filled, last = [], None
    first = next((v for v, k in zip(vals, ok) if k), 0.5)
    for v, k in zip(vals, ok):
        last = v if k else (last if last is not None else first)
        filled.append(last)
    out = []
    for i in range(len(filled)):
        a, b = max(0, i - win), min(len(filled), i + win + 1)
        out.append(sum(filled[a:b]) / (b - a))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--step", type=float, default=0.2, help="segundos entre amostras")
    ap.add_argument("--smooth", type=float, default=0.8, help="janela de suavização em segundos")
    a = ap.parse_args()
    use_venv("visao", ["cv2", "numpy"])
    import cv2

    proj = Path(a.project)
    man = load_manifest(proj)
    src = man["source"]["footage"]
    if not MODEL.exists():
        MODEL.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(MODEL_URL, MODEL)
    cap = cv2.VideoCapture(src)
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    det = cv2.FaceDetectorYN.create(str(MODEL), "", (w, h), 0.7)
    every = max(1, round(a.step * fps))
    rows = []
    for i in range(0, n, every):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        okf, frame = cap.read()
        if not okf:
            break
        _, faces = det.detect(frame)
        if faces is None or len(faces) == 0:
            rows.append({"t": i / fps, "ok": False})
            continue
        f = max(faces, key=lambda r: r[2] * r[3])  # maior rosto
        x, y, fw, fh = map(float, f[:4])
        eye_y = (f[5] + f[7]) / 2
        rows.append({"t": round(i / fps, 3), "ok": True, "cx": (x + fw / 2) / w, "cy": (y + fh / 2) / h,
                     "fw": fw / w, "fh": fh / h, "eye_y": float(eye_y) / h})
    ok = [r["ok"] for r in rows]
    win = max(1, round(a.smooth / a.step / 2))
    for k in ("cx", "cy", "fw", "fh", "eye_y"):
        for r, v in zip(rows, smooth([r.get(k, 0.5) for r in rows], ok, win)):
            r[k] = round(v, 4)
    out = proj / "edit" / "faces.json"
    out.write_text(json.dumps({"w": w, "h": h, "step": a.step, "track": rows}), encoding="utf-8")
    hit = sum(ok)
    print(f"{out}: {len(rows)} amostras, rosto em {hit} ({100 * hit // max(1, len(rows))}%)")
    if rows:
        import statistics as st
        print("mediana cx=%.2f cy=%.2f fw=%.2f fh=%.2f eye_y=%.2f" % tuple(
            st.median(r[k] for r in rows) for k in ("cx", "cy", "fw", "fh", "eye_y")))


if __name__ == "__main__":
    main()
