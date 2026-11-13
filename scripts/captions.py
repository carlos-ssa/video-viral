"""Legendas no stack v2: faster-whisper, arquivos SRT/VTT, estimativa e ASS.

python scripts/captions.py transcribe <projeto> [--audio arquivo] [--model large-v3]
python scripts/captions.py import <projeto> --file legenda.srt
python scripts/captions.py estimate <projeto>
python scripts/captions.py ass <projeto> [--words 3]

Importação/estimativa não são alinhamento forçado. Projetos de gravação usam
source_words.json e footage.py render ajusta os tempos à montagem.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ffprobe_json, load_manifest, need, project_dir, run, safe_area, use_venv  # noqa: E402


def lang2(m):
    return (m.get("lang") or "pt-BR").split("-")[0].lower()


def fill_missing(words):
    """Palavras sem tempo (números, símbolos) recebem tempo interpolado entre as vizinhas."""
    for i, w in enumerate(words):
        if w.get("start") is None:
            prev_end = next((words[j]["end"] for j in range(i - 1, -1, -1) if words[j].get("end") is not None), 0.0)
            nxt = next((words[j]["start"] for j in range(i + 1, len(words)) if words[j].get("start") is not None), prev_end + 0.3)
            w["start"], w["end"] = prev_end, max(prev_end + 0.05, min(nxt, prev_end + 0.4))
        elif w.get("end") is None:
            w["end"] = w["start"] + 0.3
    return words


def cmd_align(proj, m, a):
    sys.exit("Alinhamento forçado não faz parte do stack atual. Use transcribe com faster-whisper ou import/estimate; revise os tempos.")


def cmd_transcribe(proj, m, a):
    audio_path = Path(a.audio).resolve() if a.audio else proj / "audio" / "voice.wav"
    if not a.audio and not audio_path.exists() and (proj / "audio" / "source.wav").exists():
        audio_path = proj / "audio" / "source.wav"
    if not audio_path.exists():
        sys.exit(f"Áudio não encontrado: {audio_path}")
    import importlib.util
    if not importlib.util.find_spec("faster_whisper"):
        use_venv("legendas", ["faster_whisper"])
    try:
        from faster_whisper import WhisperModel
        import ctranslate2
    except ImportError:
        sys.exit("faster-whisper indisponível: instale o grupo legendas ou importe SRT/VTT.")
    cuda_dlls()
    try:
        dev = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
    except Exception:
        dev = "cpu"
    import subprocess
    import numpy as np
    pcm = subprocess.run([need("ffmpeg"), "-v", "error", "-i", str(audio_path), "-f", "s16le", "-ac", "1",
                          "-ar", "16000", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
    for d in ([dev, "cpu"] if dev == "cuda" else [dev]):
        try:
            model = WhisperModel(a.model, device=d, compute_type="float16" if d == "cuda" else "int8",
                                 local_files_only=bool(os.environ.get("VIDEO_VIRAL_NO_INSTALL")))
            segments, _ = model.transcribe(audio, language=lang2(m), word_timestamps=True,
                                           vad_filter=False, condition_on_previous_text=False)
            words = [{"w": w.word.strip(), "start": w.start, "end": w.end}
                     for segment in segments for w in (segment.words or []) if w.word.strip()]
            print(f"faster-whisper {a.model} em {d}: {len(words)} palavras")
            return fill_missing(words)
        except (RuntimeError, OSError) as exc:
            if d == "cpu":
                raise
            print(f"GPU indisponível ({str(exc)[:120]}); usando CPU.")


def cuda_dlls():
    """No Windows, as DLLs de CUDA dos pacotes nvidia-* da venv não estão no PATH: registra-as."""
    if os.name != "nt":
        return
    import site
    for base in site.getsitepackages():
        for bin_dir in Path(base).glob("nvidia/*/bin"):
            os.add_dll_directory(str(bin_dir))
            os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ.get("PATH", "")


CUE_TIME = re.compile(r"(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{1,3})")


def cue_secs(txt):
    h, mnt, sec, frac = CUE_TIME.match(txt.strip()).groups()
    return int(h or 0) * 3600 + int(mnt) * 60 + int(sec) + int(frac.ljust(3, "0")) / 1000


def source_timeline(m, a):
    """True quando as palavras vão para a linha do tempo da gravação (projeto com footage.py import)."""
    return bool((m.get("source") or {}).get("footage")) and not a.final


def cmd_import(proj, m, a):
    if not a.file:
        sys.exit("Use --file com o caminho da legenda .srt ou .vtt.")
    src = Path(a.file).expanduser().resolve()
    if not src.exists():
        sys.exit(f"Legenda não encontrada: {src}")
    text = src.read_text(encoding="utf-8-sig", errors="replace").replace("\r", "")
    # Blocos de legenda costumam incluir silêncio nas pontas; com o áudio da gravação, aperta cada bloco na fala.
    sil = []
    rng = (m.get("source") or {}).get("range") or [0.0, 1e9]
    off, span = (float(rng[0]), float(rng[1]) - float(rng[0])) if source_timeline(m, a) else (0.0, 1e9)
    wav = proj / ((m.get("source") or {}).get("audio") or "audio/source.wav")
    if wav.is_file():
        r = run([need("ffmpeg"), "-hide_banner", "-nostats", "-i", str(wav), "-af",
                 "silencedetect=n=-35dB:d=0.15", "-f", "null", "-"])
        st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
        en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
        sil = [(s, en[i] if i < len(en) else 1e9) for i, s in enumerate(st)]

    def tighten(t0, t1):
        for s, e in sil:
            if s <= t0 < e:
                t0 = min(e, t1)
            if s < t1 <= e:
                t1 = max(s, t0)
        return (t0, t1) if t1 - t0 >= 0.1 else None

    out = []
    for block in re.split(r"\n\s*\n", text):
        lines = [ln for ln in block.strip().split("\n") if ln.strip()]
        i = next((k for k, ln in enumerate(lines) if "-->" in ln), None)
        if i is None:
            continue
        t0, t1 = (cue_secs(x.split()[0]) for x in lines[i].split("-->"))
        body = " ".join(lines[i + 1:])
        body = re.sub(r"<[^>]+>|\{[^}]*\}", "", body)  # tags de estilo VTT/SRT/ASS
        toks = body.split()
        t0, t1 = max(t0 - off, 0.0), min(t1 - off, span)  # legenda no tempo do arquivo; edição no tempo do trecho
        if not toks or t1 <= t0:
            continue
        if sil:
            t0, t1 = tighten(t0, t1) or (t0, t1)
        weights = [max(len(re.sub(r"\W", "", w)), 2) + 1 for w in toks]
        total, acc = sum(weights), 0.0
        for w, wt in zip(toks, weights):
            s = t0 + (t1 - t0) * acc / total
            acc += wt
            out.append({"w": w, "start": round(s, 3), "end": round(t0 + (t1 - t0) * acc / total, 3), "estimated": True})
    return out


def speech_span(ff, wav):
    """Início e fim da fala no arquivo, sem os silêncios das pontas."""
    dur = float(ffprobe_json(wav)["format"]["duration"])
    r = run([ff, "-hide_banner", "-nostats", "-i", str(wav), "-af", "silencedetect=n=-40dB:d=0.1",
             "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    t0 = ends[0] if starts and starts[0] <= 0.05 and ends else 0.0
    t1 = starts[-1] if starts and starts[-1] > t0 and (len(ends) < len(starts) or ends[-1] >= dur - 0.05) else dur
    return t0, t1


def cmd_estimate(proj, m, a):
    ff = need("ffmpeg")
    out = []
    for sc in m["scenes"]:
        text = (sc.get("narration") or "").strip()
        if not text:
            continue
        if sc.get("start") is None:
            sys.exit(f"A cena {sc['id']} não tem start. Rode scripts/voice.py antes.")
        wav = proj / "audio" / "scenes" / f"{sc['id']}.wav"
        if wav.exists():
            t0, t1 = speech_span(ff, wav)
        else:
            t0, t1 = 0.0, float(sc["duration"])
        toks = text.split()
        weights = []
        for w in toks:
            core = re.sub(r"\W", "", w)
            wt = max(len(core), 2) + 1
            if re.search(r"[.!?]$", w):
                wt += 6
            elif re.search(r"[,;:]$", w):
                wt += 3
            weights.append(wt)
        span, total, acc = max(t1 - t0, 0.1), sum(weights), 0.0
        base = float(sc["start"]) + t0
        for w, wt in zip(toks, weights):
            s = base + span * acc / total
            acc += wt
            pause = 6 if re.search(r"[.!?]$", w) else 3 if re.search(r"[,;:]$", w) else 0
            e = base + span * (acc - pause * 0.8) / total
            out.append({"w": w, "start": round(s, 3), "end": round(max(e, s + 0.08), 3), "estimated": True})
    return out


def group_words(words, n):
    groups, cur = [], []
    for w in words:
        if cur and w.get("jump"):  # corte que junta frases distantes da gravação: começa outro grupo
            groups.append(cur)
            cur = []
        cur.append(w)
        if len(cur) >= n or re.search(r"[.!?;:]$", w["w"]):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    out = []
    for i, g in enumerate(groups):
        start = 0.0 if i == 0 and g[0]["start"] < 0.6 else g[0]["start"]  # texto já no quadro 0 (gancho)
        end = g[-1]["end"] + 0.15
        if i + 1 < len(groups):
            nxt = groups[i + 1][0]["start"]
            end = nxt if nxt - g[-1]["end"] < 0.6 else min(end, nxt)
        out.append({"start": round(start, 3), "end": round(max(end, start + 0.2), 3),
                    "text": " ".join(w["w"] for w in g), "words": g})
    return out


def ts(t):
    cs = int(round(max(t, 0) * 100))
    h, cs = divmod(cs, 360000)
    mnt, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{mnt:02d}:{s:02d}.{cs:02d}"


def ass_escape(s):
    return s.replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def write_ass(groups, path, cfg, size):
    w, h = size
    safe = safe_area(w, h)
    margin_v = h - safe["caption_y"]
    up = cfg.get("uppercase", True)
    font, fsize = cfg.get("font", "Arial"), int(cfg.get("size", 88))
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Short,{font},{fsize},&H0000FFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,6,0,2,{safe['left']},{safe['right']},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for g in groups:
        parts, ws = [], g["words"]
        for i, wd in enumerate(ws):
            nxt = ws[i + 1]["start"] if i + 1 < len(ws) else g["end"]
            k = max(1, int(round((nxt - wd["start"]) * 100)))
            txt = ass_escape(wd["w"].upper() if up else wd["w"])
            parts.append(f"{{\\k{k}}}{txt}")
        lines.append(f"Dialogue: 0,{ts(g['start'])},{ts(g['end'])},Short,,0,0,0,,{' '.join(parts)}")
    path.write_text(head + "\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["align", "transcribe", "import", "estimate", "ass"])
    ap.add_argument("project")
    ap.add_argument("--audio", help="transcribe: outro áudio ou vídeo (gravação própria)")
    ap.add_argument("--model", default="large-v3", help="transcribe: modelo Whisper")
    ap.add_argument("--file", help="import: legenda .srt ou .vtt")
    ap.add_argument("--out", help="arquivo de palavras (padrão captions/words.json, ou captions/source_words.json "
                    "em projeto com gravação)")
    ap.add_argument("--final", action="store_true", help="transcribe/import: tempos já no vídeo editado")
    ap.add_argument("--words", type=int, help="ass: palavras por grupo (padrão do video.json)")
    a = ap.parse_args()

    proj = project_dir(a.project)
    m = load_manifest(proj)
    cap_dir = proj / "captions"
    cap_dir.mkdir(exist_ok=True)
    words_path = cap_dir / "words.json"

    if a.cmd in ("align", "transcribe", "import", "estimate"):
        fn = {"align": cmd_align, "transcribe": cmd_transcribe, "import": cmd_import, "estimate": cmd_estimate}
        words = fn[a.cmd](proj, m, a)
        if not words:
            sys.exit("Nenhuma palavra reconhecida. Confira o áudio (ou a legenda) e o idioma do video.json.")
        to_source = a.cmd in ("transcribe", "import") and source_timeline(m, a)
        default = cap_dir / "source_words.json" if to_source else words_path
        dest = (proj / a.out) if a.out else default
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{dest.relative_to(proj).as_posix()}: {len(words)} palavras, {words[0]['start']:.2f}–{words[-1]['end']:.2f} s")
        if a.cmd == "import":
            print("Tempos por palavra interpolados dentro de cada bloco da legenda.")
        elif a.cmd == "estimate":
            print("Tempos ESTIMADOS (sem alinhamento): a legenda pode adiantar ou atrasar um pouco. "
                  "Use transcribe com faster-whisper e confira os tempos antes de cortes finos.")
        else:
            print("Confira nomes próprios e números; depois rode: captions.py ass")
        return

    if not words_path.exists():
        sys.exit("Falta captions/words.json. Rode 'align', 'transcribe' ou 'estimate' antes.")
    words = fill_missing(json.loads(words_path.read_text(encoding="utf-8")))
    cfg = m.get("captions", {})
    groups = group_words(words, a.words or int(cfg.get("words_per_group", 3)))
    size = tuple(m.get("size", [1080, 1920]))
    write_ass(groups, cap_dir / "captions.ass", cfg, size)
    (cap_dir / "captions.json").write_text(json.dumps(groups, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"captions/captions.ass e captions.json: {len(groups)} grupos")


if __name__ == "__main__":
    main()
