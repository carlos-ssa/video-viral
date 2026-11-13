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


def script_spelling(words, text):
    """Fonte explícita de grafia; conserva tempos reconhecidos, não é alinhamento forçado."""
    from difflib import SequenceMatcher
    tokens = text.split()
    key = lambda s: re.sub(r"\W", "", s).casefold()
    matcher = SequenceMatcher(None, [key(w["w"]) for w in words], [key(t) for t in tokens], autojunk=False)
    out = []
    for tag, i, j, a, b in matcher.get_opcodes():
        if tag == "equal":
            out.extend({**w, "w": t} for w, t in zip(words[i:j], tokens[a:b]))
        elif (tag == "replace" and j - i <= 12 and b - a <= 4
              and all(re.fullmatch(r"[\d:.,–—/\-]+", t) for t in tokens[a:b])
              and any(re.search(r"\d", t) for t in tokens[a:b])
              and not any(w.get("jump") for w in words[i + 1:j])):
            # Somente numerais entre âncoras textuais: não inventa palavras omitidas pelo ASR.
            if (i == 0 or key(words[i - 1]["w"]) == key(tokens[a - 1])) and (j == len(words) or (b < len(tokens) and key(words[j]["w"]) == key(tokens[b]))):
                start, end = words[i]["start"], words[j - 1]["end"]
                for k, token in enumerate(tokens[a:b]):
                    out.append({**words[i], "w": token, "start": start + (end - start) * k / (b - a),
                                "end": start + (end - start) * (k + 1) / (b - a), "script_spelling": True})
            else:
                out.extend(words[i:j])
        else:
            out.extend(words[i:j])
    return out


def caption_lines(words, max_chars=32, max_lines=2):
    """Quebra equilibrada sem linha de uma palavra quando há outra distribuição possível."""
    tokens = [w["w"] for w in words]
    if len(" ".join(tokens)) <= max_chars:
        return [" ".join(tokens)]
    if max_lines == 1:
        return None
    choices = []
    for k in range(1, len(tokens)):
        left, right = " ".join(tokens[:k]), " ".join(tokens[k:])
        if max(len(left), len(right)) <= max_chars:
            penalty = (1000 if min(k, len(tokens) - k) == 1 and len(tokens) > 3 else 0)
            choices.append((penalty + abs(len(left) - len(right)), [left, right]))
    return min(choices, key=lambda x: x[0])[1] if choices else None


# Evita separar palavras funcionais do complemento; pontuação pode fechar o trecho legitimamente.
FUNCTION_WORDS = set("o a os as um uma uns umas de do da dos das em no na nos nas por pelo pela pelos pelas "
                     "para com sem sob sobre entre até e ou mas que se só seu sua seus suas meu minha meus minhas "
                     "teu tua teus tuas nosso nossa nossos nossas vosso vossa vossos vossas "
                     "me te lhe lhes vos lo la los las ao aos à às num numa nuns numas dum duma".split())


def functional_tail(word):
    return not re.search(r'[,;:.!?…]["”\')]*$', word) and word.casefold() in FUNCTION_WORDS


def group_words(words, n, max_chars=32, max_lines=2, min_duration=0.6, max_cps=24, pause=0.45):
    if n < 1 or max_chars < 1 or max_lines not in (1, 2) or min_duration <= 0 or max_cps <= 0 or pause <= 0:
        raise ValueError("Limites de legenda inválidos (linhas: 1 ou 2).")
    # Frases e cortes são fronteiras duras; palavras por grupo são uma meta, não uma guilhotina.
    phrases, cur = [], []
    sentence_end = lambda w: bool(re.search(r'[.!?…]["”\')]*$', w["w"]))
    # Não altera as palavras/tempos de entrada; só normaliza a grafia usada na legenda.
    words = [dict(w) for w in words]
    new_sentence = True
    for index, w in enumerate(words):
        if new_sentence:
            w["w"] = re.sub(r'^(\W*)([^\W\d_])', lambda match: match[1] + match[2].upper(), w["w"], count=1)
        new_sentence = sentence_end(w)
        # Uma pausa é fronteira preferida, mas não isola a última palavra da frase.
        pause_break = (cur and len(cur) > 1 and not functional_tail(cur[-1]["w"])
                       and w["start"] - cur[-1]["end"] >= pause
                       and not sentence_end(w) and index + 1 < len(words)
                       and not words[index + 1].get("jump")
                       and words[index + 1]["start"] - w["end"] < pause)
        if cur and (w.get("jump") or pause_break):
            phrases.append(cur)
            cur = []
        cur.append(w)
        if sentence_end(w):
            phrases.append(cur)
            cur = []
    if cur:
        phrases.append(cur)
    groups = []
    for phrase_index, phrase in enumerate(phrases):
        count = len(phrase)
        phrase_end = phrases[phrase_index + 1][0]["start"] if phrase_index + 1 < len(phrases) else float('inf')
        best = {count: ((0, 0, 0, 0), [])}
        for i in range(count - 1, -1, -1):
            candidates = []
            for j in range(i + 1, count + 1):
                lines = caption_lines(phrase[i:j], max_chars, max_lines)
                if lines is None:
                    break
                if j not in best:
                    continue
                start = 0.0 if phrase_index == 0 and i == 0 and phrase[i]["start"] < 0.6 else phrase[i]["start"]
                limit = phrase[j]["start"] if j < count else phrase_end
                required = max(min_duration, len(" ".join(w["w"] for w in phrase[i:j])) / max_cps)
                if limit - start + 0.001 < required:
                    continue
                # Entre soluções legíveis: evita órfãs, depois caudas funcionais e vírgulas internas.
                # O custo por bloco evita dividir unidades curtas como "passa uma caixa por vez".
                cost = (int(j - i == 1 and count > 1),
                        int(j < count and functional_tail(phrase[j - 1]["w"])),
                        sum(bool(re.search(r'[,;:]["”\')]*$', w["w"])) for w in phrase[i:j - 1]),
                        4 + (j - i - n) ** 2)
                total = tuple(a + b for a, b in zip(cost, best[j][0]))
                candidates.append((total, [phrase[i:j]] + best[j][1]))
            if candidates:
                best[i] = min(candidates, key=lambda x: x[0])
        if 0 not in best:
            raise ValueError(f"Legenda rápida ou limite de caracteres em {phrase[0]['start']:.2f}s; revise tempos/texto ou limites de leitura e max_chars_per_line.")
        groups.extend(best[0][1])
    out = []
    for i, g in enumerate(groups):
        start = 0.0 if i == 0 and g[0]["start"] < 0.6 else g[0]["start"]
        text = " ".join(w["w"] for w in g)
        required = max(min_duration, len(text) / max_cps)
        end = max(g[-1]["end"] + 0.15, start + required)
        if i + 1 < len(groups):
            end = min(end, groups[i + 1][0]["start"])
        if end - start + 0.001 < required:
            raise ValueError(f"Legenda rápida em {start:.2f}s: precisa {required:.2f}s de leitura; revise os tempos/texto ou os limites de leitura.")
        out.append({"start": round(start, 3), "end": round(end, 3), "text": text,
                    "lines": caption_lines(g, max_chars, max_lines), "words": g})
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
        split_at = len(g.get("lines", [g["text"]])[0].split())
        body = "".join(("\\N" if i == split_at and split_at < len(ws) else " " if i else "") + part
                       for i, part in enumerate(parts))
        lines.append(f"Dialogue: 0,{ts(g['start'])},{ts(g['end'])},Short,,0,0,0,,{body}")
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
    ap.add_argument("--script-text", help="TXT UTF-8: fonte explícita de grafia/pontuação e numerais (não alinha áudio)")
    a = ap.parse_args()
    script = Path(a.script_text).read_text(encoding="utf-8-sig") if a.script_text else None

    proj = project_dir(a.project)
    m = load_manifest(proj)
    cap_dir = proj / "captions"
    cap_dir.mkdir(exist_ok=True)
    words_path = cap_dir / "words.json"

    if a.cmd in ("align", "transcribe", "import", "estimate"):
        fn = {"align": cmd_align, "transcribe": cmd_transcribe, "import": cmd_import, "estimate": cmd_estimate}
        words = fn[a.cmd](proj, m, a)
        if script:
            words = script_spelling(words, script)
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
    if script:
        words = script_spelling(words, script)
    try:
        groups = group_words(words, a.words if a.words is not None else int(cfg.get("words_per_group", 3)),
                             int(cfg.get("max_chars_per_line", 32)), int(cfg.get("max_lines", 2)),
                             float(cfg.get("min_duration", 0.6)), float(cfg.get("max_cps", 24)),
                             float(cfg.get("pause_threshold", 0.45)))
    except ValueError as exc:
        sys.exit(str(exc))
    size = tuple(m.get("size", [1080, 1920]))
    write_ass(groups, cap_dir / "captions.ass", cfg, size)
    (cap_dir / "captions.json").write_text(json.dumps(groups, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"captions/captions.ass e captions.json: {len(groups)} grupos")


if __name__ == "__main__":
    main()
