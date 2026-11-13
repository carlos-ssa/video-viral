"""Gera a narração por cena com Kokoro e grava os tempos de cada cena no video.json.

Uso:
  python scripts/voice.py <projeto> [--voice pf_dora] [--speed 1.0] [--gap 0.25]
  python scripts/voice.py <projeto> --engine system [--voice Maria]   # reserva sem instalar nada
  python scripts/voice.py <projeto> --from-wavs      # usa audio/scenes/sNN.wav já existentes (Chatterbox etc.)

Saídas: audio/scenes/<id>.wav, audio/voice.wav (48 kHz mono) e scenes[].start/duration.
Kokoro precisa de: kokoro>=0.9.4, soundfile, numpy e espeak-ng (references/setup.md).
--engine auto (padrão) usa Kokoro se estiver instalado e, senão, a voz do sistema: Windows (System.Speech),
macOS (say) ou Linux (espeak-ng). A voz do sistema soa robótica e entra com licença "uso comercial não
verificado", o que bloqueia a entrega monetizada; use deliver.py --draft e proponha instalar o Kokoro.
"""
import argparse
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import add_asset, ffprobe_json, load_manifest, need, project_dir, run, save_manifest, use_venv  # noqa: E402

KOKORO_LANG = {"pt-BR": "p", "en-US": "a", "en-GB": "b", "es": "e", "fr": "f", "it": "i", "ja": "j", "zh": "z", "hi": "h"}


def synth_kokoro(proj, m, voice, speed, lang_code):
    try:
        import numpy as np
        import soundfile as sf
        from kokoro import KPipeline
    except ImportError as e:
        sys.exit(f"Falta {e.name} neste Python ({sys.executable}). Rode: python scripts/setup_tools.py voz")
    pipe = KPipeline(lang_code=lang_code)
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


WIN_TTS = r"""
param([string]$Jobs, [string]$Culture, [string]$Voice, [int]$Rate)
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$vs = @($s.GetInstalledVoices() | Where-Object { $_.Enabled } | ForEach-Object { $_.VoiceInfo })
$pick = $null
if ($Voice) { $pick = $vs | Where-Object { $_.Name -like "*$Voice*" } | Select-Object -First 1 }
if (-not $pick) { $pick = $vs | Where-Object { $_.Culture.Name -eq $Culture } | Select-Object -First 1 }
if (-not $pick) { $l = $Culture.Split('-')[0]; $pick = $vs | Where-Object { $_.Culture.TwoLetterISOLanguageName -eq $l } | Select-Object -First 1 }
if (-not $pick) { [Console]::Error.WriteLine("Nenhuma voz instalada para $Culture. Vozes: " + (($vs | ForEach-Object { $_.Name + ' (' + $_.Culture.Name + ')' }) -join ', ')); exit 3 }
$s.SelectVoice($pick.Name)
$s.Rate = $Rate
foreach ($j in (Get-Content -Raw -Encoding UTF8 $Jobs | ConvertFrom-Json)) {
  $s.SetOutputToWaveFile($j.out)
  $s.Speak([IO.File]::ReadAllText($j.txt, [Text.Encoding]::UTF8))
}
$s.SetOutputToNull()
$s.Dispose()
Write-Output $pick.Name
"""


def synth_system(proj, m, voice, speed):
    """Voz do sistema operacional. Devolve a descrição da voz usada."""
    lang = m.get("lang", "pt-BR")
    scenes = [sc for sc in m["scenes"] if (sc.get("narration") or "").strip()]
    out_dir = proj / "audio" / "scenes"
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        jobs = []
        for sc in scenes:
            txt = td / f"{sc['id']}.txt"
            txt.write_text(sc["narration"].strip(), encoding="utf-8")
            jobs.append({"id": sc["id"], "txt": str(txt), "out": str(out_dir / f"{sc['id']}.wav")})
        system = platform.system()
        if system == "Windows":
            ps = shutil.which("powershell") or shutil.which("pwsh")
            if not ps:
                sys.exit("PowerShell não encontrado para a voz do sistema.")
            script = td / "tts.ps1"
            script.write_text(WIN_TTS, encoding="utf-8-sig")
            (td / "jobs.json").write_text(json.dumps(jobs, ensure_ascii=False), encoding="utf-8")
            rate = max(-10, min(10, round((speed - 1.0) * 10)))
            r = subprocess.run([ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
                                "-Jobs", str(td / "jobs.json"), "-Culture", lang, "-Voice", voice or "",
                                "-Rate", str(rate)], capture_output=True, text=True, encoding="utf-8", errors="replace")
            if r.returncode != 0:
                sys.exit(f"Voz do sistema falhou: {r.stderr.strip()[-600:]}")
            name = (r.stdout.strip().splitlines() or ["?"])[-1]
            desc = f"Windows System.Speech ({name})"
        elif system == "Darwin":
            ff = need("ffmpeg")
            for j in jobs:
                aiff = td / f"{j['id']}.aiff"
                cmd = ["say", "-o", str(aiff), "-f", j["txt"], "-r", str(int(180 * speed))]
                run(cmd + (["-v", voice] if voice else []))
                run([ff, "-y", "-hide_banner", "-i", str(aiff), j["out"]])
            desc = f"macOS say ({voice or 'voz padrão'})"
        else:
            es = shutil.which("espeak-ng") or shutil.which("espeak")
            if not es:
                sys.exit("Nenhuma voz do sistema: instale espeak-ng ou o Kokoro (references/setup.md).")
            v = voice or lang.lower()
            for j in jobs:
                run([es, "-v", v, "-s", str(int(165 * speed)), "-w", j["out"], "-f", j["txt"]])
            desc = f"espeak-ng ({v})"
    for sc in scenes:
        print(f"  {sc['id']}: ok")
    return desc


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
    ap.add_argument("--engine", choices=["auto", "kokoro", "system"], default="auto",
                    help="auto: Kokoro se instalado, senão a voz do sistema")
    a = ap.parse_args()

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
        if engine == "auto":
            engine = "kokoro" if kokoro_available() else "system"
            if engine == "system":
                print("Kokoro indisponível (instalação falhou ou VIDEO_VIRAL_NO_INSTALL): usando a voz do sistema como reserva.")
        if engine == "kokoro":
            voice = a.voice or v.get("voice", "pf_dora")
            lang = KOKORO_LANG.get(m.get("lang", "pt-BR"), "p")
            print(f"Kokoro: voz {voice}, velocidade {speed}, idioma {lang}")
            synth_kokoro(proj, m, voice, speed, lang)
            v.update(engine="kokoro", voice=voice, speed=speed)
            add_asset(m, "audio/voice.wav", "voice", f"Kokoro-82M ({voice})", "Apache-2.0", True)
        else:
            desc = synth_system(proj, m, a.voice, speed)
            print(f"Voz do sistema: {desc}")
            v.update(engine="system", voice=desc, speed=speed)
            add_asset(m, "audio/voice.wav", "voice", desc,
                      "voz do sistema operacional; uso comercial não verificado", None)
            print("Aviso: voz robótica e sem licença comercial confirmada. A entrega monetizada só sai com "
                  "deliver.py --draft; proponha instalar o Kokoro (references/setup.md) no relatório final.")

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
