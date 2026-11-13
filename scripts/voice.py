"""Narração online com Edge TTS ou montagem dos WAVs fornecidos.

python scripts/voice.py <projeto> [--voice pt-BR-ThalitaMultilingualNeural] [--speed 1.2] [--gap 0.25]
python scripts/voice.py <projeto> --from-wavs
Saídas: audio/voice.wav e tempos em scenes[]. Inglês usa en-US-AvaMultilingualNeural.
Speed 1.2 corresponde a rate +20%. A síntese envia a narração ao serviço Microsoft Edge.
"""
import argparse
import asyncio
import importlib.util
import math
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import add_asset, ffprobe_json, load_manifest, need, project_dir, run, save_manifest, use_venv  # noqa: E402

DEFAULT_SPEED = 1.2
DEFAULT_VOICES = {"pt": "pt-BR-ThalitaMultilingualNeural", "en": "en-US-AvaMultilingualNeural"}


def default_voice(lang="pt-BR"):
    language = lang.replace("_", "-").lower().split("-")[0]
    if language not in DEFAULT_VOICES:
        raise ValueError(f"Sem voz padrão para {lang}; informe --voice com um nome de edge-tts --list-voices.")
    return DEFAULT_VOICES[language]


def speed_to_rate(speed):
    if not math.isfinite(speed) or speed <= 0:
        raise ValueError("--speed deve ser um número positivo e finito (1.2 = +20%).")
    percent = round((speed - 1) * 100)
    if percent <= -100:
        raise ValueError("--speed deve resultar em uma taxa maior que -100%.")
    return f"{percent:+d}%"


def voice_settings(m, voice=None, speed=None):
    settings = m.get("voice") or {}
    # Configurações Kokoro são incompatíveis com Edge; migre para os novos padrões.
    legacy = settings.get("engine") == "kokoro"
    selected_voice = voice or (None if legacy else settings.get("voice")) or default_voice(m.get("lang", "pt-BR"))
    selected_speed = float(speed if speed is not None else
                           DEFAULT_SPEED if legacy else settings.get("speed", DEFAULT_SPEED))
    speed_to_rate(selected_speed)
    return selected_voice, selected_speed


def synth_edge(proj, m, voice, speed):
    try:
        import edge_tts
    except ImportError as e:
        sys.exit(f"Falta {e.name} neste Python ({sys.executable}). Rode: python scripts/setup_tools.py voz")
    ff = need("ffmpeg")
    rate = speed_to_rate(speed)
    scenes = proj / "audio" / "scenes"
    scenes.mkdir(parents=True, exist_ok=True)

    async def generate(staging):
        ready = []
        for sc in m["scenes"]:
            text = (sc.get("narration") or "").strip()
            if not text:
                continue
            mp3 = staging / f"{sc['id']}.mp3"
            wav = staging / f"{sc['id']}.wav"
            try:
                await edge_tts.Communicate(text, voice=voice, rate=rate).save(str(mp3))
            except Exception as exc:
                sys.exit(f"Edge TTS falhou na cena {sc['id']}: {exc}. Confira internet/voz; "
                         "sem serviço, forneça WAVs com --from-wavs.")
            run([ff, "-y", "-hide_banner", "-i", str(mp3), "-ar", "48000", "-ac", "1",
                 "-c:a", "pcm_s16le", str(wav)])
            ready.append((wav, scenes / wav.name))
            print(f"  {sc['id']}: ok")
        # Só substitui as cenas anteriores quando toda a síntese/conversão terminou.
        for wav, destination in ready:
            wav.replace(destination)

    with tempfile.TemporaryDirectory(prefix="edge-tts-", dir=scenes) as staging:
        asyncio.run(generate(Path(staging)))


def edge_available():
    return importlib.util.find_spec("edge_tts") is not None


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
    ap.add_argument("--speed", type=float, help="multiplicador de velocidade (padrão 1.2 = +20%%)")
    ap.add_argument("--gap", type=float, default=0.25, help="pausa após cada cena, em segundos")
    ap.add_argument("--from-wavs", action="store_true", help="não sintetiza; usa os WAV de audio/scenes")
    ap.add_argument("--engine", choices=["auto", "edge-tts"], default="edge-tts", help="auto é alias de edge-tts; sem fallback para outro motor")
    ap.add_argument("--license", default="", help="termos/licença aplicáveis ao áudio gerado")
    ap.add_argument("--commercial-ok", action="store_true", help="confirma uso comercial permitido pela licença informada")
    a = ap.parse_args()
    if a.commercial_ok and not a.license.strip():
        ap.error("Uso comercial exige --license com os termos aplicáveis ao áudio.")

    proj = project_dir(a.project)
    m = load_manifest(proj)
    if not m.get("scenes") or not any((s.get("narration") or "").strip() for s in m["scenes"]):
        sys.exit("Nenhuma cena com narração no video.json. Escreva o roteiro primeiro.")
    (proj / "audio" / "scenes").mkdir(parents=True, exist_ok=True)

    if not a.from_wavs:
        try:
            voice, speed = voice_settings(m, a.voice, a.speed)
        except (TypeError, ValueError) as exc:
            ap.error(str(exc))
        v = m.setdefault("voice", {})
        if not edge_available():
            use_venv("voz", ["edge_tts"])
        if not edge_available():
            sys.exit("Edge TTS indisponível; forneça WAVs com --from-wavs ou instale apenas o grupo voz.")
        print(f"Edge TTS: voz {voice}, velocidade {speed_to_rate(speed)} (online)")
        synth_edge(proj, m, voice, speed)
        v.update(engine="edge-tts", voice=voice, speed=speed)
        if "modules" in m.get("stack", {}):
            m["stack"]["modules"] = list(dict.fromkeys("edge-tts" if x == "kokoro" else x for x in m["stack"]["modules"]))
        for entry in m.get("tool_plan", []):
            if entry.get("module") == "kokoro":
                entry["module"] = "edge-tts"

    total = assemble(proj, m, a.gap)
    if not a.from_wavs:
        # A licença LGPL do cliente não define os direitos sobre a fala do serviço Microsoft.
        add_asset(m, "audio/voice.wav", "voice", f"Microsoft Edge TTS / edge-tts ({voice}, {speed_to_rate(speed)})",
                  a.license.strip() or "Termos do serviço Microsoft Edge TTS: não verificados", bool(a.commercial_ok))
    save_manifest(proj, m)
    target = m.get("target_seconds")
    print(f"audio/voice.wav: {total:.1f} s" + (f" (alvo {target} s)" if target else ""))
    for sc in m["scenes"]:
        print(f"  {sc['id']}: {sc['start']:6.2f} s  +{sc['duration']:.2f} s")
    if target and total > target * 1.15:
        print("Passou do alvo em mais de 15%: corte texto no roteiro em vez de acelerar a voz.")


if __name__ == "__main__":
    main()
