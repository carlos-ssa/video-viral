"""Narração com Kokoro ou montagem dos WAVs fornecidos.

python scripts/voice.py <projeto> [--voice pf_dora] [--speed 1.0] [--gap 0.25]
python scripts/voice.py <projeto> --from-wavs
Saídas: audio/voice.wav e tempos em scenes[]. Somente Kokoro sintetiza voz.
"""
import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import add_asset, ffprobe_json, load_manifest, need, project_dir, run, save_manifest, use_venv  # noqa: E402

KOKORO_LANG = {"pt-BR": "p", "en-US": "a", "en-GB": "b", "es": "e", "fr": "f", "it": "i", "ja": "j", "zh": "z", "hi": "h"}


def synth_kokoro(proj, m, voice, speed, lang_code, device="auto"):
    try:
        import numpy as np
        import soundfile as sf
        import torch
        from kokoro import KPipeline
    except ImportError as e:
        sys.exit(f"Falta {e.name} neste Python ({sys.executable}). Rode: python scripts/setup_tools.py voz")
    selected_device = ("cuda" if torch.cuda.is_available() else "cpu") if device == "auto" else device
    if selected_device == "cpu":
        # Some CUDA wheels probe an empty GPU list from LSTM.flatten_parameters on CPU.
        torch.backends.cudnn.enabled = False
    pipe = KPipeline(lang_code=lang_code, device=selected_device)
    for sc in m["scenes"]:
        text = (sc.get("narration") or "").strip()
        if not text:
            continue
        chunks = []
        for _, _, audio in pipe(text, voice=voice, speed=speed):
            if audio is None:
                continue
            a = audio.detach().cpu().numpy() if hasattr(audio, "detach") else np.asarray(audio)
            chunks.append(a.astype("float32").reshape(-1))
        if not chunks:
            sys.exit(f"Kokoro não gerou áudio para a cena {sc['id']}.")
        sf.write(proj / "audio" / "scenes" / f"{sc['id']}.wav", np.concatenate(chunks), 24000)
        print(f"  {sc['id']}: ok")


def kokoro_available():
    return all(importlib.util.find_spec(p) for p in ("kokoro", "soundfile", "numpy"))


def duration(path):
    return float(ffprobe_json(path)["format"]["duration"])


def assemble(proj, m, gap):
    """Concatena as cenas (com pausa) em audio/voice.wav e grava start/duration."""
    ff = need("ffmpeg")
    args, filters, labels, t = [ff, "-y", "-hide_banner"], [], [], 0.0
    for i, sc in enumerate(m["scenes"]):
        wav = proj / "audio" / "scenes" / f"{sc['id']}.wav"
        if (sc.get("narration") or "").strip():
            if not wav.exists():
                sys.exit(f"Falta {wav}. Gere a voz da cena ou rode sem --from-wavs.")
            dur = duration(wav) + gap
            args += ["-i", str(wav)]
            filters.append(f"[{i}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=mono,"
                           f"apad=whole_dur={dur:.3f}[a{i}]")
        else:
            dur = sc.get("duration")
            if not dur:
                sys.exit(f"A cena {sc['id']} não tem narração nem 'duration'. Defina a duração dela no video.json.")
            dur = float(dur)
            args += ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=mono"]
            filters.append(f"[{i}:a]aformat=sample_fmts=fltp:channel_layouts=mono[a{i}]")
        labels.append(f"[a{i}]")
        sc["start"], sc["duration"] = round(t, 3), round(dur, 3)
        t += dur
    filters.append(f"{''.join(labels)}concat=n={len(labels)}:v=0:a=1[out]")
    out = proj / "audio" / "voice.wav"
    run(args + ["-filter_complex", ";".join(filters), "-map", "[out]", "-c:a", "pcm_s16le", str(out)])
    return t


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--voice")
    ap.add_argument("--speed", type=float)
    ap.add_argument("--gap", type=float, default=0.25, help="pausa após cada cena, em segundos")
    ap.add_argument("--from-wavs", action="store_true", help="não sintetiza; usa os WAV de audio/scenes")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    ap.add_argument("--engine", choices=["auto", "kokoro"], default="kokoro", help="auto é alias legado de kokoro; sem fallback para outro motor")
    a = ap.parse_args()
    if os.environ.get("VIDEO_VIRAL_NO_INSTALL"):
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

    proj = project_dir(a.project)
    m = load_manifest(proj)
    if not m.get("scenes") or not any((s.get("narration") or "").strip() for s in m["scenes"]):
        sys.exit("Nenhuma cena com narração no video.json. Escreva o roteiro primeiro.")
    (proj / "audio" / "scenes").mkdir(parents=True, exist_ok=True)

    if not a.from_wavs:
        v = m.setdefault("voice", {})
        speed = a.speed or float(v.get("speed", 1.0))
        engine = a.engine
        if engine in ("auto", "kokoro") and not kokoro_available():
            use_venv("voz", ["kokoro", "soundfile", "numpy"])  # reexecuta na venv 'voz', instalando-a se preciso
        if not kokoro_available():
            sys.exit("Kokoro indisponível; forneça WAVs com --from-wavs ou instale apenas o grupo voz.")
        voice = a.voice or v.get("voice", "pf_dora")
        lang = KOKORO_LANG.get(m.get("lang", "pt-BR"), "p")
        print(f"Kokoro: voz {voice}, velocidade {speed}, idioma {lang}")
        synth_kokoro(proj, m, voice, speed, lang, a.device)
        v.update(engine="kokoro", voice=voice, speed=speed)
        add_asset(m, "audio/voice.wav", "voice", f"Kokoro-82M ({voice})", "Apache-2.0", True)

    total = assemble(proj, m, a.gap)
    save_manifest(proj, m)
    target = m.get("target_seconds")
    print(f"audio/voice.wav: {total:.1f} s" + (f" (alvo {target} s)" if target else ""))
    for sc in m["scenes"]:
        print(f"  {sc['id']}: {sc['start']:6.2f} s  +{sc['duration']:.2f} s")
    if target and total > target * 1.15:
        print("Passou do alvo em mais de 15%: corte texto no roteiro em vez de acelerar a voz.")


if __name__ == "__main__":
    main()
