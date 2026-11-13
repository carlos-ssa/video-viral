"""Uma rodada de revisão do vídeo: quadros para olhar, métricas de ritmo e checagens de direção.

Uso:
  python scripts/review.py <projeto> [--video out/<slug>.mp4] [--every N]   # padrão: a entrega mais recente
  python scripts/review.py <projeto> --verdict

--verdict lê a tabela de notas da última rodada e sai com 0 (aprovado: pode declarar pronto), 1 (nota abaixo de 4
ou bloqueante antes da 3ª rodada: faça outra), 2 (notas não preenchidas) ou 3 (3ª rodada sem aprovar: entregue e
relate o que ficou abaixo de 4).

Grava review/rNN/ com:
  grid.jpg     um quadro a cada --every segundos (padrão: 1 s, ou duração/48 em vídeo longo) (da esquerda para a direita, de cima para baixo)
  hook.jpg     quadros em 0; 0,5; 1; 1,5 e 2 s, maiores, para julgar o gancho
  report.md    métricas, alertas e a tabela de notas para preencher (references/review.md); os critérios
               mudam com o formato (gravação/corte/UGC trocam direção e motion por corte de fala e
               enquadramento) e o vídeo longo (16:9 ou mais de 3 min) ganha o critério Retenção
  metrics.json os mesmos dados para comparar rodadas
Sai com código 1 se houver alerta bloqueante. Só biblioteca padrão e FFmpeg.
"""
import argparse
import json
import math
import subprocess
import re
import shutil
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import file_sha256, manifest_sha256, ffprobe_json, load_manifest, need, project_dir, run, save_manifest  # noqa: E402

# Segundos, proporções e níveis são separados por tipo de vídeo (references/review.md).
FREEZE_SAMPLE_FPS = 5
FREEZE_PIXEL_DELTA = 8
FREEZE_CHANGED_FRACTION = 0.0002
FREEZE_MIN_SECONDS = 0.4
SHORT_FREEZE_WARN_SECONDS, LONG_FREEZE_WARN_SECONDS = 1.5, 6.0
DEAD_TAIL_ENERGY_REFERENCE_FPS = 10
DEAD_TAIL_MAX_MEAN_ENERGY, DEAD_TAIL_MAX_FRAME_ENERGY = 0.5, 1.5
UNIFORM_PIXEL_FRACTION = 0.9
SHORT_FREEZE_ERROR_SECONDS, LONG_FREEZE_ERROR_SECONDS = 2.5, 12.0
SHORT_SHOT_SECONDS, LONG_SHOT_SECONDS = 3.5, 15.0
SHORT_EVENT_GAP_SECONDS, LONG_EVENT_GAP_SECONDS = 3.0, 8.0
SHORT_SPEECH_START_SECONDS, LONG_SPEECH_START_SECONDS = 0.7, 3.0
SHORT_DEAD_TAIL_SECONDS, LONG_DEAD_TAIL_SECONDS = 1.0, 3.0
SILENCE_DB = -45
SILENCE_MIN_SECONDS = 0.15
SHORT_MIDDLE_SILENCE_SECONDS, LONG_MIDDLE_SILENCE_SECONDS = 0.7, 2.0
MIN_AUDIBLE_FRACTION = 0.5
TIMING_TOLERANCE_SECONDS = 0.05
OCCUPANCY_WIDTH, OCCUPANCY_HEIGHT = 90, 160
OCCUPANCY_MAX_SAMPLES = 48
JPEG_MAX_DIMENSION = 65500  # FFmpeg's MJPEG encoder limit for each image dimension.
UNIFORM_COLOR_DELTA = 10
UNIFORM_PERSISTENCE = 0.9
UNIFORM_BAND_FRACTION = 0.3

BARS = "▁▂▃▄▅▆▇█"
RUBRIC = [
    ("Gancho", "Quadro 0 legível e assunto/promessa reconhecíveis sem som; mensagem principal curta, com entrada de fala/som adequada ao formato"),
    ("Ritmo", "Progressão adequada à narrativa; cortes preservam palavras/sentido e pausas intencionais; mudanças visuais cumprem função, sem quota de efeitos"),
    ("Direção de arte", "Paleta, fontes e textura do direction em todas as cenas; nada com cara de padrão"),
    ("Motion", "Curvas e durações do motion.md, foco claro e movimento por intenção; planos estáticos e pausas podem cumprir função"),
    ("Fala e imagem", "Cada plano mostra o que a narração diz naquele instante, acrescentando em vez de repetir"),
    ("Legibilidade", "Contraste, tamanho, área segura, legenda fora do assunto principal"),
    ("Som", "Voz inteligível quando presente; música/ambiente/efeitos sustentam a intenção sem mascarar fala, ruído ou silêncio não intencional"),
    ("Payoff", "Entrega a promessa do gancho com fechamento coerente; loop ou corte só quando adequados ao conteúdo"),
]
RECORDED = {"gravacao", "corte", "ugc"}
RECORDED_RUBRIC = [
    ("Corte de fala", "Remove sobras e retomadas sem alterar sentido; preserva palavras, respiração e pausas intencionais, sem estalos"),
    ("Enquadramento", "Assunto/rosto enquadrados sem cortes involuntários; recorte, moldura e B-roll por função, preservando continuidade sem zoom obrigatório"),
]
LONG_RUBRIC = [
    ("Retenção", "Promessa clara nos 30 s iniciais, virada ou novo gancho a cada 60–90 s, capítulos no ponto de mudança de assunto"),
]


def is_long(m, dur):
    return m.get("aspect") == "16:9" or dur > 180


def rubric_for(m, dur):
    """Critérios da rodada conforme o formato e a duração."""
    r = list(RUBRIC)
    if m.get("format") in RECORDED:
        drop = {"Direção de arte", "Motion", "Fala e imagem"}
        r = [c for c in r if c[0] not in drop]
        r[2:2] = RECORDED_RUBRIC
    if m.get("format") == "musica":
        r = [("Sincronismo musical", "Cortes, texto e movimento acompanham as batidas e a estrutura musical")
             if k == "Fala e imagem" else (k, v) for k, v in r]
    if m.get("format") == "avatar":
        r.append(("Sincronia labial", "Boca e voz alinhadas; identidade, olhar e performance consistentes"))
    if m.get("format") == "storytelling":
        r.append(("Continuidade", "Personagens, cenário e ação mantêm identidade e continuidade entre planos"))
    if m.get("brief", {}).get("objective") == "conversao":
        r.append(("Mensagem e CTA", "Público, benefício, prova e ação estão claros; a promessa é cumprida"))
    if not expects_speech(m):
        r = [(k, "Quadro 0 legível e intrigante; imagem e som apresentam a ação, sem exigir fala")
             if k == "Gancho" else (k, v) for k, v in r]
    if is_long(m, dur):
        r = [(k, "Quadro 0 forte e promessa clara; em vídeo narrado, fala em até 3 s")
             if k == "Gancho" else (k, v) for k, v in r]
        r = [(k, "Progressão visual adequada ao assunto; investigar pausas acima de 8 s e planos acima de 15 s")
             if k == "Ritmo" else (k, v) for k, v in r]
        r.insert(2, LONG_RUBRIC[0])
        r = [(k, "Entrega a promessa do título; CTA sem anunciar o fim antes da hora") if k == "Payoff" else (k, v)
             for k, v in r]
    return r


def tile_size(m):
    w, h = (m.get("size") or [1080, 1920])[:2]
    k = 320 / max(w, h)
    return int(w * k) // 2 * 2, int(h * k) // 2 * 2


class RoundLimitError(ValueError):
    pass


def next_round(proj):
    base = proj / "review"
    base.mkdir(exist_ok=True)
    nums = [int(p.name[1:]) for p in base.glob("r[0-9][0-9]") if p.is_dir()]
    if nums and max(nums) >= MAX_ROUNDS:
        raise RoundLimitError("LIMITE de três rodadas; preserve a revisão existente e entregue o melhor com limitações, sem declarar aprovação")
    d = base / f"r{(max(nums) + 1 if nums else 1):02d}"
    d.mkdir()
    return d


def validate_grid(dur, every, tw, th):
    """Reject impossible JPEG tiles before FFmpeg or a round directory is created."""
    cols, padding = 8, 4
    max_rows = (JPEG_MAX_DIMENSION + padding) // (th + padding)
    if (not math.isfinite(every) or every <= 0 or max_rows < 1
            or cols * tw + (cols - 1) * padding > JPEG_MAX_DIMENSION
            or dur / every >= cols * max_rows):
        raise ValueError(f"grade excede o limite JPEG de {JPEG_MAX_DIMENSION} pixels por dimensão; aumente --every")


def frames(ff, video, out_dir, dur, fps, every, tw, th):
    validate_grid(dur, every, tw, th)
    n = max(1, int(dur // every) + 1)
    cols = 8
    rows = math.ceil(n / cols)
    run([ff, "-y", "-hide_banner", "-i", str(video), "-vf",
         f"fps=1/{every}:start_time=0,scale={tw}:{th},tile={cols}x{rows}:padding=4:color=0x202020",
         "-frames:v", "1", "-q:v", "3", str(out_dir / "grid.jpg")])
    picks = "+".join(f"eq(n,{round(t * fps)})" for t in (0, 0.5, 1.0, 1.5, 2.0) if t < dur)
    k = picks.count("eq(")
    run([ff, "-y", "-hide_banner", "-i", str(video), "-vf",
         f"select='{picks}',scale={tw * 3 // 4 * 2}:{th * 3 // 4 * 2},tile={k}x1:padding=6:color=0x202020",
         "-frames:v", "1", "-q:v", "3", str(out_dir / "hook.jpg")])
    return n


def analyze(ff, video, out_dir, fps, tw, th):
    """Cortes, energia e pixels que mudam: movimento local não se dilui na média do quadro."""
    graph = (f"[0:v]scale={tw}:{th},fps={fps},split=3[a][b][c];"
             "[a]scdet=threshold=10,metadata=select:key=lavfi.scd.time,"
             "metadata=print:key=lavfi.scd.time:file=cuts.txt,nullsink;"
             f"[b]fps={FREEZE_SAMPLE_FPS},tblend=all_mode=difference,"
             f"lut=y='if(gt(val,{FREEZE_PIXEL_DELTA}),255,0)',signalstats,"
             "metadata=print:key=lavfi.signalstats.YAVG:file=changed.txt,nullsink;"
             "[c]tblend=all_mode=difference,signalstats,"
             "metadata=print:key=lavfi.signalstats.YAVG:file=energy.txt[out]")
    run([ff, "-hide_banner", "-nostats", "-i", str(video), "-filter_complex", graph, "-map", "[out]",
         "-f", "null", "-"], cwd=out_dir)
    cuts = [float(x) for x in re.findall(r"lavfi\.scd\.time=([\d.]+)", (out_dir / "cuts.txt").read_text())]
    energy = [(float(t), float(v)) for t, v in re.findall(
        r"pts_time:([\d.]+)\s*\n\s*lavfi\.signalstats\.YAVG=([\d.]+)", (out_dir / "energy.txt").read_text())]
    changed = [(float(t), float(v) / 255) for t, v in re.findall(
        r"pts_time:([\d.]+)\s*\n\s*lavfi\.signalstats\.YAVG=([\d.]+)", (out_dir / "changed.txt").read_text())]
    freezes, start = [], None
    step = 1 / FREEZE_SAMPLE_FPS
    for t, fraction in changed:
        if fraction < FREEZE_CHANGED_FRACTION:
            if start is None:
                start = max(0.0, t - step)
        elif start is not None:
            duration = max(0.0, t - step - start)
            if duration >= FREEZE_MIN_SECONDS:
                freezes.append((start, duration))
            start = None
    if start is not None and changed[-1][0] + step - start >= FREEZE_MIN_SECONDS:
        freezes.append((start, None))
    for f in ("cuts.txt", "energy.txt", "changed.txt"):
        (out_dir / f).unlink(missing_ok=True)
    return cuts, energy, freezes


def first_luma(ff, video):
    r = run([ff, "-hide_banner", "-nostats", "-i", str(video), "-frames:v", "1", "-vf",
             "signalstats,metadata=print:key=lavfi.signalstats.YAVG", "-f", "null", "-"])
    m = re.search(r"YAVG=([\d.]+)", r.stderr)
    return float(m.group(1)) if m else None


def speech_start(ff, audio):
    r = run([ff, "-hide_banner", "-nostats", "-i", str(audio), "-af", "silencedetect=n=-40dB:d=0.15",
             "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    if starts and starts[0] <= 0.05:
        return ends[0] if ends else None
    return 0.0


def expects_speech(m):
    """Não confundir qualquer som com voz. Gravações mantêm fala do áudio original."""
    if m.get("format") in RECORDED:
        return True
    if m.get("format") in {"musica", "asmr", "asmr-impossivel"} or (m.get("voice") or {}).get("engine") == "none":
        return False
    scenes = m.get("scenes") or []
    if scenes and all("narration" in scene for scene in scenes):
        return any(str(scene.get("narration") or "").strip() for scene in scenes)
    return True


def audio_activity(ff, video, dur, has_audio=True):
    """Mede silêncio absoluto no render, inclusive o que o gate de LUFS ignora."""
    if not has_audio:
        return {"silences": [(0.0, dur)], "audible_fraction": 0.0}
    result = run([ff, "-hide_banner", "-nostats", "-i", str(video), "-vn", "-af",
                  f"silencedetect=n={SILENCE_DB}dB:d={SILENCE_MIN_SECONDS}", "-f", "null", "-"])
    silences, start = [], None
    for kind, value in re.findall(r"silence_(start|end): (-?[\d.]+)", result.stderr):
        t = max(0.0, min(dur, float(value)))
        if kind == "start":
            start = t
        elif start is not None:
            silences.append((start, t))
            start = None
    if start is not None:
        silences.append((start, dur))
    return {"silences": silences, "audible_fraction": max(0.0, 1 - covered_seconds(silences) / dur)}


def caption_ranges(proj, m):
    """ASS ou grupos JSON são intervalos de exibição; palavras ASR não são caixas de legenda."""
    def valid(start, end):
        return (type(start) in (int, float) and type(end) in (int, float)
                and math.isfinite(start) and math.isfinite(end) and 0 <= start < end)

    ass = proj / "captions" / "captions.ass"
    if ass.exists():
        ranges = []
        for line in ass.read_text(encoding="utf-8-sig").splitlines():
            if line.startswith("Dialogue:"):
                fields = line.split(",", 9)
                if len(fields) != 10:
                    return None
                def seconds(value):
                    h, minute, sec = value.strip().split(":")
                    return int(h) * 3600 + int(minute) * 60 + float(sec)
                try:
                    if fields[9].strip():
                        start, end = seconds(fields[1]), seconds(fields[2])
                        if not valid(start, end):
                            return None
                        ranges.append((start, end))
                except ValueError:
                    return None
        return ranges
    groups = proj / "captions" / "captions.json"
    if groups.exists():
        try:
            cues = json.loads(groups.read_text(encoding="utf-8"))
            if (not isinstance(cues, list) or any(not isinstance(g, dict)
                    or not valid(g.get("start"), g.get("end"))
                    or not isinstance(g.get("text"), str) or not g["text"].strip() for g in cues)):
                return None
            return [(g["start"], g["end"]) for g in cues]
        except (ValueError, KeyError, TypeError):
            return None
    if (m.get("captions") or {}).get("enabled") is False or not expects_speech(m):
        return []
    return None  # HTML/legenda embutida sem tempos de exibição: não presumir ausência.


def freeze_checks(freezes, dur, long_, captions):
    block, warn = [], []
    limit = LONG_FREEZE_ERROR_SECONDS if long_ else SHORT_FREEZE_ERROR_SECONDS
    for start, duration in freezes:
        stop = dur if duration is None else min(dur, start + duration)
        span = stop - start
        if span < (LONG_FREEZE_WARN_SECONDS if long_ else SHORT_FREEZE_WARN_SECONDS):
            continue
        reading = captions is not None and any(a < stop and b > start for a, b in captions)
        message = (f"Imagem quase parada em {start:.1f}–{stop:.1f} s ({span:.1f} s): "
                   "confira a reprodução; encurte a pausa ou mantenha movimento significativo.")
        # Um None significa somente fim do arquivo, não duração infinita nem falha mais grave.
        (block if span >= limit and not reading else warn).append(message)
    return block, warn


def low_motion_tail(energy, dur):
    """Cauda sem progressão: tolera só movimento residual, não substitui o gate de congelamento."""
    if len(energy) < 2:
        return None
    step = (energy[-1][0] - energy[0][0]) / (len(energy) - 1)
    if step <= 0:
        return None
    scale = 1 / (step * DEAD_TAIL_ENERGY_REFERENCE_FPS)
    tail = []
    for time, value in reversed(energy):
        if value * scale > DEAD_TAIL_MAX_FRAME_ENERGY:
            break
        tail.append((time, value * scale))
    if not tail or statistics.fmean(value for _, value in tail) > DEAD_TAIL_MAX_MEAN_ENERGY:
        return None
    return max(0.0, tail[-1][0] - step)


def audio_checks(m, dur, long_, activity, freezes, captions, energy=()):
    block, warn = [], []
    fraction = activity["audible_fraction"]
    if not expects_speech(m) and fraction < MIN_AUDIBLE_FRACTION:
        block.append(f"Áudio audível em apenas {fraction:.0%} de 0.0–{dur:.1f} s "
                     f"(mínimo {MIN_AUDIBLE_FRACTION:.0%}, silêncio abaixo de {SILENCE_DB} dB): "
                     "preencha a ação com Foley/ambiente/música pertinente; normalizar LUFS não remove silêncio.")
    middle_limit = LONG_MIDDLE_SILENCE_SECONDS if long_ else SHORT_MIDDLE_SILENCE_SECONDS
    for start, stop in activity["silences"]:
        if start > TIMING_TOLERANCE_SECONDS and stop < dur - TIMING_TOLERANCE_SECONDS and stop - start >= middle_limit:
            warn.append(f"Silêncio no meio em {start:.1f}–{stop:.1f} s ({stop - start:.1f} s, "
                        f"abaixo de {SILENCE_DB} dB): encurte a pausa ou acrescente cama sonora pertinente.")
    tail_limit = LONG_DEAD_TAIL_SECONDS if long_ else SHORT_DEAD_TAIL_SECONDS
    silent_tail = next((s for s, e in activity["silences"] if e >= dur - TIMING_TOLERANCE_SECONDS), None)
    frozen_tail = next((s for s, d in freezes if d is None or s + d >= dur - TIMING_TOLERANCE_SECONDS), None)
    if frozen_tail is None:
        frozen_tail = low_motion_tail(energy, dur)
    if silent_tail is not None and frozen_tail is not None:
        start = max(silent_tail, frozen_tail)
        if captions is not None:
            start = max([start] + [min(dur, b) for a, b in captions if b > start and a < dur])
        if dur - start > tail_limit + TIMING_TOLERANCE_SECONDS:
            message = (f"Cauda {'morta' if captions is not None else 'possivelmente morta'} em {start:.1f}–{dur:.1f} s "
                       f"({dur - start:.1f} s): corte o fim ou sustente ação, som ou legenda útil.")
            if captions is None:
                warn.append(message + " Confirme as legendas HTML/embutidas; faltam tempos de exibição confiáveis.")
            else:
                block.append(message)
    return block, warn


def uniform_band(ff, video, dur):
    """Amostra RGB: mesma faixa contígua, quase uniforme espacial e temporalmente."""
    w, h = OCCUPANCY_WIDTH, OCCUPANCY_HEIGHT
    every = max(1.0, dur / OCCUPANCY_MAX_SAMPLES)
    result = subprocess.run([ff, "-v", "error", "-i", str(video), "-an", "-vf",
                             f"fps=1/{every},scale={w}:{h}", "-pix_fmt", "rgb24", "-f", "rawvideo", "-"],
                            capture_output=True, check=True)
    frame_size = w * h * 3
    samples = len(result.stdout) // frame_size
    if not samples:
        return None
    colors, coverage = [[] for _ in range(h)], [[] for _ in range(h)]
    for offset in range(0, samples * frame_size, frame_size):
        for y in range(h):
            row = result.stdout[offset + y * w * 3:offset + (y + 1) * w * 3]
            color = [statistics.median(row[c::3]) for c in range(3)]
            colors[y].append(color)
            coverage[y].append(sum(all(abs(row[x * 3 + c] - color[c]) <= UNIFORM_COLOR_DELTA
                                       for c in range(3)) for x in range(w)) / w)
    # Um rodapé/legenda pequeno não divide artificialmente uma grande região vazia.
    # Exigimos 90% dos pixels da faixa da mesma cor em pelo menos 90% das amostras.
    stable = [[statistics.median(v[c] for v in values) for c in range(3)] for values in colors]
    best = (0, 0)
    for start, color in enumerate(stable):
        totals = [0.0] * samples
        for stop in range(start, h):
            if any(abs(stable[stop][c] - color[c]) > UNIFORM_COLOR_DELTA for c in range(3)):
                break
            for i in range(samples):
                if all(abs(colors[stop][i][c] - color[c]) <= UNIFORM_COLOR_DELTA for c in range(3)):
                    totals[i] += coverage[stop][i]
            height = stop - start + 1
            persistent = sum(total / height >= UNIFORM_PIXEL_FRACTION for total in totals) / samples
            if persistent >= UNIFORM_PERSISTENCE and height > best[1] - best[0]:
                best = (start, stop + 1)
    fraction = (best[1] - best[0]) / h
    if fraction <= UNIFORM_BAND_FRACTION:
        return None
    return {"top_fraction": best[0] / h, "bottom_fraction": best[1] / h,
            "height_fraction": fraction, "start": 0.0, "end": dur, "samples": samples}


def per_second(energy, dur):
    buckets = [[] for _ in range(max(1, math.ceil(dur)))]
    for t, v in energy:
        i = min(int(t), len(buckets) - 1)
        buckets[i].append(v)
    return [statistics.fmean(b) if b else 0.0 for b in buckets]


def visual_events(cuts, energy):
    """Cortes e picos de movimento (entrada de texto, objeto, transição)."""
    vals = [v for _, v in energy]
    if not vals:
        return sorted(cuts)
    base = statistics.median(vals)
    thr = max(1.5, base * 2.5)
    peaks, last = [], -9.0
    for i in range(1, len(energy) - 1):
        t, v = energy[i]
        if v >= thr and v >= energy[i - 1][1] and v >= energy[i + 1][1] and t - last >= 0.4:
            peaks.append(t)
            last = t
    ev = sorted(set(round(x, 2) for x in cuts + peaks))
    merged = []
    for t in ev:
        if not merged or t - merged[-1] >= 0.4:
            merged.append(t)
    return merged


def sparkline(vals):
    if not vals:
        return ""
    top = max(vals) or 1.0
    return "".join(BARS[min(len(BARS) - 1, int(v / top * (len(BARS) - 1) + 0.5))] for v in vals)


def has_audio_role(proj, m, role):
    kinds = {"sfx", "sound-design", "foley", "effect", "efeito"} if role == "sfx" else {
        "music", "ambience", "ambient", "ambiente", "bed", "trilha"}
    names = {"sound-design", "sfx", "foley", "effects", "efeitos"} if role == "sfx" else {
        "music", "ambience", "ambient", "ambiente", "bed", "trilha"}
    if any((proj / "audio" / f"{name}.wav").is_file() for name in names):
        return True
    if role == "sfx" and (proj / "audio/sfx").is_dir() and any((proj / "audio/sfx").iterdir()):
        return True
    for asset in m.get("assets", []):
        path = Path(str(asset.get("path", "")).replace("\\", "/"))
        tokens = set(re.split(r"[^\w-]+|_", path.stem.lower()))
        if asset.get("kind") in kinds or asset.get("role") in kinds or tokens.intersection(names):
            return True
    return False


def manifest_checks(proj, m, long_, duration=None):
    warn = []
    waiver = (m.get("music") or {}).get("bed_waiver")
    if (expects_speech(m) and not has_audio_role(proj, m, "bed")
            and not (isinstance(waiver, str) and waiver.strip())):
        interval = f"em 0.0–{duration:.1f} s" if duration is not None else "durante a fala"
        warn.append(f"Sem cama sonora declarada {interval}: acrescente música/ambiente ou registre "
                    "a justificativa editorial em music.bed_waiver; confira as pausas nos tempos de silêncio.")
    if m.get("format") in RECORDED:
        edl = proj / "edit" / "edl.json"
        if not edl.exists():
            warn.append("Sem edit/edl.json: a gravação não passou pelo footage.py cut.")
        tr = proj / "edit" / "transcript.md"
        if tr.exists() and edl.exists():
            kept = {s["id"] for s in json.loads(edl.read_text(encoding="utf-8")).get("segments", []) if s.get("keep", True)}
            left = []
            for ln in tr.read_text(encoding="utf-8").splitlines():
                mm = re.search(r"retomada\? (\S+)", ln)
                if mm and ln.count("|") > 2:
                    first = ln.split("|")[1].strip()
                    if first in kept and mm.group(1) in kept:
                        left.append(f"{first}/{mm.group(1)}")
            if left:
                warn.append(f"Retomada marcada e mantida: {', '.join(left)} (veja edit/transcript.md).")
        return warn + pace_checks(proj, long_)
    d = m.get("direction") or {}
    if not d.get("style"):
        warn.append("Sem `direction.style`: o visual não tem direção definida (references/direction.md).")
    if len(d.get("palette") or []) < 3:
        warn.append("`direction.palette` com menos de 3 cores.")
    fonts = d.get("fonts") or {}
    if not fonts.get("title") or not fonts.get("captions"):
        warn.append("`direction.fonts` sem fonte de título ou de legenda.")
    cap_font = (m.get("captions") or {}).get("font", "Arial")
    if cap_font.lower() in ("arial", "roboto", "helvetica") and not (m.get("captions") or {}).get("html"):
        warn.append(f"Legenda em {cap_font}: troque pela fonte de legenda da direção.")
    no_shots = [s["id"] for s in m.get("scenes", []) if not (s.get("visual") or {}).get("shots")]
    if no_shots:
        warn.append(f"Cenas sem roteiro de planos (`visual.shots`): {', '.join(no_shots)}.")
    for s in m.get("scenes", []):
        dur = s.get("duration") or 0
        shots = len((s.get("visual") or {}).get("shots") or [])
        shot_limit = LONG_SHOT_SECONDS if long_ else SHORT_SHOT_SECONDS
        if shots and dur / shots > shot_limit:
            start = float(s.get("start") or 0)
            warn.append(f"{s['id']}: {shots} plano(s) em {start:.1f}–{start + dur:.1f} s, "
                        f"mais de {shot_limit:g} s por plano; varie o enquadramento ou encurte a cena.")
    if m.get("scenes"):
        os0 = (m["scenes"][0].get("on_screen") or "").split()
        if not os0:
            warn.append("Primeira cena sem texto na tela para o gancho.")
        elif len(os0) > 6:
            warn.append(f"Texto do gancho na tela com {len(os0)} palavras (máximo 6).")
    if not has_audio_role(proj, m, "sfx"):
        warn.append("Nenhum efeito sonoro registrado: confira transições/revelações e registre "
                    "a faixa de efeitos (audio/sound-design.wav ou ativo com role=sfx).")
    return warn + pace_checks(proj, long_)


def pace_checks(proj, long_):
    warn = []
    words = proj / "captions" / "words.json"
    if words.exists():
        w = json.loads(words.read_text(encoding="utf-8"))
        if len(w) > 2:
            span = w[-1]["end"] - w[0]["start"]
            wps = len(w) / span if span > 0 else 0
            if wps > 3.3:
                warn.append(f"Fala a {wps:.1f} palavras/s: rápida demais para acompanhar.")
            elif wps < (1.5 if long_ else 1.8):
                warn.append(f"Fala a {wps:.1f} palavras/s: lenta{'' if long_ else ' para vídeo curto'}.")
    return warn


MAX_ROUNDS = 3
CHANNELS = ("visual", "motion", "audio")


def reviewer_preflight(capabilities, producer_id, required=CHANNELS):
    """Validate the recorded capability check; this does not authenticate tools or people."""
    if not isinstance(producer_id, str) or not producer_id.strip():
        raise ValueError("informe o ID do autor com --producer-id")
    if not isinstance(capabilities, dict) or type(capabilities.get("schema")) is not int or capabilities["schema"] != 1:
        raise ValueError("preflight do revisor ausente ou inválido")
    reviewer = capabilities.get("reviewer_id")
    if not isinstance(reviewer, str) or not reviewer.strip() or reviewer.strip().casefold() == producer_id.strip().casefold():
        raise ValueError("revisor precisa ter ID próprio, diferente do autor")
    if capabilities.get("author_scores_exposed") is not False:
        raise ValueError("o revisor não pode receber as notas/conclusões do autor")
    channels = capabilities.get("channels")
    if not isinstance(channels, dict):
        raise ValueError("registre as capacidades reais por modalidade")
    missing = []
    for channel in required:
        item = channels.get(channel)
        if not isinstance(item, dict) or type(item.get("available")) is not bool:
            raise ValueError(f"capacidade {channel} não foi conferida")
        if not item["available"]:
            missing.append(channel)
        elif any(not isinstance(item.get(key), str) or not item[key].strip() for key in ("method", "evidence")):
            raise ValueError(f"registre método e evidência da capacidade {channel}")
    return missing


def covered_seconds(ranges):
    total, end = 0.0, 0.0
    for start, stop in sorted(ranges):
        total += max(0, stop - max(start, end))
        end = max(end, stop)
    return total


def prepare_review_input(out_dir, video, manifest, metrics, producer_id):
    """Give the reviewer artifacts and criteria, without the author's score report."""
    target = out_dir / "input"
    target.mkdir()
    clip = target / ("video" + video.suffix)
    shutil.copyfile(video, clip)
    if file_sha256(clip) != metrics["video_sha256"]:
        raise ValueError("o vídeo mudou ao copiar a evidência; refaça a rodada")
    for name in ("hook.jpg", "grid.jpg"):
        shutil.copyfile(out_dir / name, target / name)
    direction = manifest.get("direction") or {}
    request = {
        "schema": 1, "producer_id": producer_id,
        "video_sha256": metrics["video_sha256"], "manifest_sha256": metrics["manifest_sha256"],
        "title": manifest.get("title", ""), "brief": manifest.get("brief", {}),
        "direction": direction,
        "references": direction.get("references", []),
        "criteria": [{"name": key, "definition": text} for key, text in rubric_for(manifest, metrics["duration"])],
        "artifacts": {"video": clip.name, "hook": "hook.jpg", "grid": "grid.jpg"},
        "technical": {key: metrics.get(key) for key in ("duration", "fps", "has_audio", "blockers", "warnings")},
        "instructions": "Avalie os artefatos e o briefing. Não leia report.md, assessment.json ou notas/conclusões do autor. Registre capacidades, método e intervalos reais; não invente reprodução ou escuta."
    }
    path = target / "request.json"
    path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return file_sha256(path)


def empty_preflight():
    return {"schema": 1, "reviewer_id": "", "author_scores_exposed": None,
            "channels": {ch: {"available": None, "method": "", "evidence": ""} for ch in CHANNELS}}


def human_form(out_dir, metrics):
    """Ficha sem notas do autor; entregue junto de input/, não do relatório."""
    lines = ["# Ficha de revisão humana", "",
             "Preencha pessoalmente após abrir input/video.*. Use SIM apenas para o que fez.",
             "Informe segundos decimais (ponto); intervalo integral em cada modalidade aplicável.",
             "Não consulte notas/conclusões do autor. O registro não autentica a identidade.", "",
             f"Video SHA256: {metrics['video_sha256']}",
             f"Manifesto SHA256: {metrics['manifest_sha256']}",
             f"Pacote SHA256: {metrics['review_request_sha256']}",
             "Revisor: ", "Notas do autor não consultadas: ",
             "Assisti ao vídeo inteiro: ",
             "Ouvi o áudio inteiro: " + ("" if metrics['has_audio'] else "NA"),
             "Início observado: ", "Fim observado: ", "Método e aparelho: ",
             "Observações gerais: ", "", "| Critério | Nota (1–5) | Observação/trecho |", "|---|---|---|"]
    lines += [f"| {key} |  |  |" for key in metrics['rubric']]
    (out_dir / "ficha-humana.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def ingest_human_form(proj, path):
    """Valida a declaração antes de gravar; o veredito conserva todos os portões."""
    rounds = sorted((proj / "review").glob("r[0-9][0-9]"))
    if not rounds:
        raise ValueError("gere uma rodada antes de preencher a ficha")
    last = rounds[-1]
    met = json.loads((last / "metrics.json").read_text(encoding="utf-8"))
    text = path.read_text(encoding="utf-8")

    def field(label):
        values = re.findall(r"^" + re.escape(label) + r":[ \t]*(.*)$", text, re.M)
        if len(values) != 1 or not values[0].strip():
            raise ValueError(f"preencha uma vez o campo {label}")
        return values[0].strip()

    for label, key in (("Video SHA256", "video_sha256"), ("Manifesto SHA256", "manifest_sha256"),
                       ("Pacote SHA256", "review_request_sha256")):
        if field(label) != met[key]:
            raise ValueError(f"{label} diverge da rodada")
    request_path = last / "input" / "request.json"
    if file_sha256(request_path) != met["review_request_sha256"]:
        raise ValueError("pacote alterado")
    request = json.loads(request_path.read_text(encoding="utf-8"))
    video = Path(met["video"])
    video = video if video.is_absolute() else proj / video
    if file_sha256(video) != met["video_sha256"] or manifest_sha256(load_manifest(proj)) != met["manifest_sha256"]:
        raise ValueError("vídeo/manifesto mudou; regenere a revisão")
    required = CHANNELS if met["has_audio"] else ("visual", "motion")
    if field("Assisti ao vídeo inteiro") != "SIM" or field("Notas do autor não consultadas") != "SIM":
        raise ValueError("confirme observação integral e independência com SIM")
    if field("Ouvi o áudio inteiro") != ("SIM" if met["has_audio"] else "NA"):
        raise ValueError("confirme escuta integral com SIM (NA somente sem fluxo de áudio)")
    start, stop = float(field("Início observado")), float(field("Fim observado"))
    if (not all(math.isfinite(x) for x in (start, stop)) or not 0 <= start < stop <= met["duration"] + 0.05
            or covered_seconds([[start, stop]]) < met["duration"] - 0.05):
        raise ValueError("intervalo observado não cobre a duração integral")
    method, notes = field("Método e aparelho"), field("Observações gerais")
    cap = {"schema": 1, "reviewer_id": field("Revisor"), "reviewer_type": "human",
           "author_scores_exposed": False, "channels": {
               ch: {"available": ch in required, "method": method,
                    "evidence": f"Ficha humana {path.name}; declaração de observação integral"} for ch in CHANNELS}}
    reviewer_preflight(cap, request["producer_id"], required)
    scores = {}
    for line in text.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) == 3 and cells[0] in met["rubric"]:
            key, score, observation = cells
            if key in scores or not re.fullmatch(r"(?:[1-4](?:[.,]\d)?|5(?:[.,]0)?)", score) or not observation:
                raise ValueError(f"preencha nota 1–5 e observação única para {key}")
            scores[key] = (score.replace(",", "."), observation)
    if set(scores) != set(met["rubric"]):
        raise ValueError("preencha todos os critérios da ficha")
    assessment = {"video_sha256": met["video_sha256"], "reviewer_preflight": cap,
                  "human_form_sha256": file_sha256(path), "human_notes": notes}
    for ch in CHANNELS:
        assessment[ch] = {"status": "observed" if ch in required else "not_applicable",
                          "method": method, "ranges": [[start, stop]] if ch in required else []}
    # Substitui somente as linhas de notas; preserva métricas/alertas da rodada.
    report_path = last / "report.md"
    report = report_path.read_text(encoding="utf-8")
    definitions = dict(rubric_for(load_manifest(proj), met["duration"]))
    for key, (score, observation) in scores.items():
        pattern = r"^\|\s*" + re.escape(key) + r"\s*\|.*$"
        row = f"| {key} | {definitions[key]} | {score} | {observation} |"
        report, count = re.subn(pattern, lambda match: row, report, flags=re.M)
        if count != 1:
            raise ValueError(f"critério {key} ausente/duplicado no relatório")
    (last / "assessment.json").write_text(json.dumps(assessment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(report, encoding="utf-8")
    return verdict(proj)


def pending_human(last, met, receipt):
    if not met["blockers"] and receipt.get("approved") is True and receipt.get("draft") is False:
        print("ENTREGA TÉCNICA APROVADA, REVISÃO HUMANA PENDENTE.")
        print(f"Próximo passo: pessoa independente preenche {last / 'ficha-humana.md'}; "
              "importe com --human-form. A aprovação audiovisual continua pendente.")
    else:
        print("Entrega técnica com falhas/rascunho; revisão perceptual também pendente.")


def verdict(proj):
    """Lê as notas da última rodada e decide: 0 aprovado, 1 outra rodada, 2 notas faltando, 3 limite atingido."""
    rounds = sorted(p for p in (proj / "review").glob("r[0-9][0-9]") if p.is_dir()) if (proj / "review").is_dir() else []
    if not rounds:
        print("Nenhuma rodada de revisão. Rode review.py primeiro.")
        return 2
    last = rounds[-1]
    n = int(last.name[1:])
    mpath = last / "metrics.json"
    try:
        report = (last / "report.md").read_text(encoding="utf-8") if (last / "report.md").exists() else ""
        met = json.loads(mpath.read_text(encoding="utf-8"))
        if type(met["schema"]) is not int or met["schema"] != 2:
            raise ValueError("métricas antigas; gere uma nova revisão")
        if type(met.get("has_audio")) is not bool or type(met.get("duration")) not in (int, float) or not math.isfinite(met["duration"]) or met["duration"] <= 0:
            raise ValueError("duração/modalidade de áudio inválida")
        video = Path(met["video"])
        if not video.is_absolute():
            video = proj / video
        digest = file_sha256(video)
        if digest != met["video_sha256"]:
            raise ValueError("o vídeo mudou depois da revisão")
        manifest = load_manifest(proj)
        if manifest_sha256(manifest) != met["manifest_sha256"]:
            raise ValueError("o manifesto mudou depois da revisão")
        keys = [k for k, _ in rubric_for(manifest, met["duration"])]
        if (keys != met["rubric"] or not isinstance(met["blockers"], list)
                or any(not isinstance(b, str) or not b.strip() for b in met["blockers"])):
            raise ValueError("métricas ou critérios inconsistentes")
        for name in ("hook.jpg", "grid.jpg"):
            if file_sha256(last / name) != met["frame_sha256"][name]:
                raise ValueError(f"{name} mudou depois da análise")
        receipt = json.loads((proj / "out" / "delivery.json").read_text(encoding="utf-8"))
        if type(receipt["schema"]) is not int or receipt["schema"] != 1 or receipt["manifest_sha256"] != met["manifest_sha256"]:
            raise ValueError("a entrega técnica pertence a outro manifesto; rode deliver.py novamente")
        if receipt["video_sha256"] != digest or Path(receipt["video"]).resolve() != video.resolve():
            raise ValueError("a entrega técnica pertence a outro vídeo")
        assessment = json.loads((last / "assessment.json").read_text(encoding="utf-8"))
        if assessment["video_sha256"] != digest:
            raise ValueError("a avaliação pertence a outro vídeo")
        request_path = last / "input" / "request.json"
        if file_sha256(request_path) != met["review_request_sha256"]:
            raise ValueError("o pacote de revisão mudou; gere uma nova revisão")
        request = json.loads(request_path.read_text(encoding="utf-8"))
        if type(request["schema"]) is not int or request["schema"] != 1 or request["video_sha256"] != digest or request["manifest_sha256"] != met["manifest_sha256"]:
            raise ValueError("pacote de revisão incompatível com o render/manifesto")
        clip_name = request["artifacts"]["video"]
        if not isinstance(clip_name, str) or Path(clip_name).name != clip_name or file_sha256(last / "input" / clip_name) != digest:
            raise ValueError("vídeo do pacote independente ausente ou alterado")
        if (last / "input" / clip_name).samefile(video):
            raise ValueError("vídeo do pacote precisa ser uma cópia independente, sem hard link")
        if {path.name for path in (last / "input").iterdir()} != {clip_name, "request.json", "hook.jpg", "grid.jpg"}:
            raise ValueError("o pacote independente contém arquivos não previstos; não inclua notas do autor")
        if request["technical"]["has_audio"] is not met["has_audio"] or request["technical"]["duration"] != met["duration"]:
            raise ValueError("modalidades/duração divergem do pacote de revisão")
        if request["technical"]["blockers"] != met["blockers"]:
            raise ValueError("bloqueantes divergem do pacote de revisão")
        for name in ("hook.jpg", "grid.jpg"):
            if file_sha256(last / "input" / name) != met["frame_sha256"][name]:
                raise ValueError("imagens do pacote independente foram alteradas")
        required = ("visual", "motion", "audio") if met["has_audio"] else ("visual", "motion")
        capabilities = assessment["reviewer_preflight"]
        if (capabilities == empty_preflight() and isinstance(request.get("producer_id"), str)
                and request["producer_id"].strip()
                and all(assessment[ch] == {"status": "pending", "method": "", "ranges": []} for ch in required)):
            pending_human(last, met, receipt)
            return 2
        missing_capabilities = reviewer_preflight(capabilities, request["producer_id"], required)
        unverified = [f"{channel}: revisor sem capacidade verificada" for channel in missing_capabilities]
        for channel in ("visual", "motion", "audio"):
            item = assessment[channel]
            status = item["status"]
            if status == "not_applicable" and channel == "audio" and not met["has_audio"]:
                continue
            if status == "unverified":
                unverified.append(f"{channel}: não verificado")
                continue
            if status not in ("observed", "instrumented") or not isinstance(item["method"], str) or not item["method"].strip():
                raise ValueError(f"registre como {channel} foi inspecionado em assessment.json")
            ranges = item["ranges"]
            if (not isinstance(ranges, list) or not ranges
                    or any(not isinstance(r, (list, tuple)) or len(r) != 2
                           or any(type(value) not in (int, float) or not math.isfinite(value) for value in r)
                           or not 0 <= r[0] < r[1] <= met["duration"] + 0.05 for r in ranges)):
                raise ValueError(f"registre os intervalos inspecionados de {channel}")
            if status == "observed" and not capabilities["channels"][channel]["available"]:
                raise ValueError(f"observação de {channel} contradiz o preflight do revisor")
            if status == "instrumented":
                unverified.append(f"{channel}: somente análise instrumentada, sem aprovação perceptual")
            elif covered_seconds(ranges) < met["duration"] - 0.05:
                unverified.append(f"{channel}: inspeção parcial, não cobre o vídeo completo")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"REVISÃO INCOMPLETA OU DESATUALIZADA: {exc}. Rode deliver/review e registre a evidência.")
        return 2
    if unverified:
        pending_human(last, met, receipt)
        print("REVISÃO AUDIOVISUAL PARCIAL: " + "; ".join(unverified))
        print("Não declare aprovação completa nem invente notas. Complete a inspeção com capacidade adequada; "
              "a ausência de modalidade não exige nova renderização por si só. Confira também as falhas técnicas registradas.")
        return 1
    names = {k.lower(): k for k in keys}
    scores = {}
    for line in report.splitlines():
        cells = [c.strip().strip("*") for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0].lower() not in names:
            continue
        key = names[cells[0].lower()]
        # The generated table has exactly: criterion, definition, score, evidence.
        # Numbers in definitions/observations must never stand in for a missing score.
        if (key in scores or len(cells) != 4 or not cells[3]
                or not re.fullmatch(r"(?:[1-4]([.,]\d)?|5([.,]0)?)", cells[2])):
            print(f"REVISÃO INCOMPLETA: nota/evidência ausente, inválida ou duplicada para {key}.")
            return 2
        scores[key] = float(cells[2].replace(",", "."))
    missing = [k for k in keys if k not in scores]
    if missing:
        print(f"{last.name}: preencha a nota (1 a 5) de {', '.join(missing)} em {last.name}/report.md "
              "depois de olhar hook.jpg e grid.jpg.")
        return 2
    block = list(met["blockers"])
    if receipt.get("approved") is not True or receipt.get("draft") is not False:
        block.append("entrega técnica reprovada ou rascunho; não publicar")
    low = [f"{k}={scores[k]:g}" for k in keys if scores[k] < 4]
    print(f"{last.name} (rodada {n} de {MAX_ROUNDS}): " + ", ".join(f"{k}={v:g}" for k, v in scores.items()))
    if not low and not block:
        print("APROVADO: todas as notas 4 ou mais e nenhum bloqueante.")
        return 0
    falhas = low + [f"bloqueante: {b}" for b in block]
    if n < MAX_ROUNDS:
        print("NÃO APROVADO: " + "; ".join(falhas))
        print("Faça outra rodada: aplique as 3 correções de maior efeito, renderize, entregue e rode review.py. "
              "Não declare o vídeo pronto.")
        return 1
    print("LIMITE de rodadas: entregue o melhor resultado e relate o que ficou abaixo de 4 e por quê: "
          + "; ".join(falhas))
    return 3


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", nargs="?")
    ap.add_argument("--producer-id", help="ID estável do autor; necessário à aprovação independente")
    ap.add_argument("--human-form", type=Path, help="importa ficha humana preenchida na última rodada e executa o veredito")
    ap.add_argument("--check-reviewer", type=Path, help="confere o preflight antes de delegar; não gera revisão")
    ap.add_argument("--channels", nargs="+", choices=CHANNELS, default=list(CHANNELS),
                    help="escopo solicitado em --check-reviewer; o veredito completo exige todas as modalidades aplicáveis")
    ap.add_argument("--video", help="padrão: out/<slug>.mp4, senão out/<slug>_rascunho.mp4, senão render/master.mp4")
    ap.add_argument("--every", type=float, help="intervalo entre quadros da grade, em segundos (padrão: 1, ou dur/48)")
    ap.add_argument("--verdict", action="store_true",
                    help="não gera rodada; lê as notas da última e diz se o vídeo pode ser declarado pronto")
    a = ap.parse_args()
    if a.every is not None and (not math.isfinite(a.every) or a.every <= 0):
        ap.error("--every precisa ser um número finito maior que zero")

    if a.check_reviewer:
        try:
            capabilities = json.loads(a.check_reviewer.read_text(encoding="utf-8"))
            missing = reviewer_preflight(capabilities, a.producer_id, a.channels)
            print(json.dumps({"status": "partial" if missing else "eligible-for-requested-scope",
                              "requested_channels": a.channels, "unavailable": missing,
                              "note": "Registro de capacidades; não comprova sozinho ferramentas, identidade ou observação."},
                             ensure_ascii=False))
            sys.exit(1 if missing else 0)
        except (OSError, ValueError, TypeError) as exc:
            print(f"PREFLIGHT INCOMPLETO: {exc}")
            sys.exit(2)
    if not a.project:
        ap.error("informe o projeto ou use --check-reviewer")

    proj = project_dir(a.project)
    if a.human_form:
        try:
            code = ingest_human_form(proj, a.human_form)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(f"FICHA HUMANA INVÁLIDA: {exc}")
            code = 2
        sys.exit(code)
    if a.verdict:
        sys.exit(verdict(proj))
    m = load_manifest(proj)
    ff = need("ffmpeg")
    if a.video:
        video = Path(a.video)
        video = video if video.is_absolute() else (proj / video)
    else:
        slug = m.get("slug")
        delivered = [p for p in (proj / "out" / f"{slug}.mp4", proj / "out" / f"{slug}_rascunho.mp4") if p.exists()]
        master = proj / "render" / "master.mp4"
        video = (max(delivered, key=lambda p: p.stat().st_mtime) if delivered
                 else master if master.exists() else None)
    if not video or not video.exists():
        sys.exit("Vídeo não encontrado. Rode deliver.py antes ou passe --video.")
    video = video.resolve()
    digest = file_sha256(video)

    info = ffprobe_json(video)
    vs = next(s for s in info["streams"] if s["codec_type"] == "video")
    num, den = (vs.get("avg_frame_rate") or "30/1").split("/")
    fps = round(float(num) / float(den or 1)) or int(m.get("fps", 30))
    dur = float(info["format"]["duration"])
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])

    long_ = is_long(m, dur)
    rubric = rubric_for(m, dur)
    a.every = a.every if a.every is not None else (1.0 if dur <= 48 else round(dur / 48, 1))
    afps = min(fps, 10) if dur > 180 else fps  # análise mais leve em vídeo longo
    tw, th = tile_size(m)
    try:
        validate_grid(dur, a.every, tw, th)
    except ValueError as exc:
        ap.error(str(exc))
    try:
        out_dir = next_round(proj)
    except RoundLimitError as exc:
        print(exc)
        sys.exit(3)
    print(f"Revisão {out_dir.name}: {video.name}, {dur:.1f} s")
    n_frames = frames(ff, video, out_dir, dur, fps, a.every, tw, th)
    cuts, energy, freezes = analyze(ff, video, out_dir, afps, tw, th)
    luma0 = first_luma(ff, video)
    voice = proj / "audio" / "voice.wav"
    speech = (speech_start(ff, voice if voice.exists() else video)
              if expects_speech(m) and (voice.exists() or has_audio) else None)
    activity = audio_activity(ff, video, dur, has_audio)
    captions = caption_ranges(proj, m)
    band = uniform_band(ff, video, dur)

    secs = per_second(energy, dur)
    events = visual_events(cuts, energy)
    gap_max = LONG_EVENT_GAP_SECONDS if long_ else SHORT_EVENT_GAP_SECONDS
    gaps, prev = [], 0.0
    for t in events + [dur]:
        if t - prev > gap_max:
            gaps.append((prev, t))
        prev = t
    shot_lens = [b - a_ for a_, b in zip([0.0] + cuts, cuts + [dur])]

    block, warn = [], []
    if luma0 is not None and luma0 < 20:
        block.append(f"Primeiro quadro quase preto (luma {luma0:.0f}): o gancho precisa aparecer no quadro 0.")
    freeze_block, freeze_warn = freeze_checks(freezes, dur, long_, captions)
    audio_block, audio_warn = audio_checks(m, dur, long_, activity, freezes, captions, energy)
    block += freeze_block + audio_block
    warn += freeze_warn + audio_warn
    if band:
        warn.append(f"Ocupação do quadro em 0.0–{dur:.1f} s: faixa quase uniforme de "
                    f"{band['top_fraction']:.0%} a {band['bottom_fraction']:.0%} da altura "
                    f"({band['height_fraction']:.0%} do quadro, persistência ≥{UNIFORM_PERSISTENCE:.0%}). "
                    "Confira o render e amplie/reposicione o assunto se esse vazio não for intencional.")
    speech_limit = LONG_SPEECH_START_SECONDS if long_ else SHORT_SPEECH_START_SECONDS
    if expects_speech(m):
        if speech is None:
            warn.append(f"Não achei fala em 0.0–{dur:.1f} s; confira a faixa de voz ou declare voice.engine=none se não há fala.")
        elif speech > speech_limit:
            block.append(f"A fala começa em {speech:.2f} s: antecipe a entrada para até {speech_limit:g} s.")
    first_event = next((t for t in events if t > 0.05), None)
    if first_event is None or first_event > 2.0:
        warn.append("Nenhuma mudança visual forte nos 2 primeiros segundos.")
    for g0, g1 in gaps:
        warn.append(f"{g1 - g0:.1f} s sem evento visual ({g0:.1f}–{g1:.1f} s).")
    warn += manifest_checks(proj, m, long_, dur)

    if file_sha256(video) != digest:
        sys.exit("O vídeo mudou durante a análise; refaça a revisão do render final.")

    metrics = {
        "schema": 2, "video_sha256": digest, "manifest_sha256": manifest_sha256(m),
        "has_audio": has_audio,
        "frame_sha256": {name: file_sha256(out_dir / name) for name in ("hook.jpg", "grid.jpg")},
        "round": out_dir.name, "video": str(video), "duration": round(dur, 2), "fps": fps,
        "cuts": [round(c, 2) for c in cuts], "visual_events": events,
        "mean_shot_s": round(statistics.fmean(shot_lens), 2) if shot_lens else None,
        "longest_shot_s": round(max(shot_lens), 2) if shot_lens else None,
        "events_per_10s": round(len(events) / dur * 10, 1) if dur else 0,
        "energy_per_second": [round(v, 2) for v in secs],
        "freezes": freezes, "first_frame_luma": luma0, "speech_start_s": speech,
        "audio_activity": activity, "uniform_band": band, "caption_timing_known": captions is not None,
        "blockers": block, "warnings": warn, "format": m.get("format", "narrado"), "long": long_,
        "rubric": [k for k, _ in rubric],
    }
    metrics["review_request_sha256"] = prepare_review_input(out_dir, video, m, metrics, a.producer_id)
    (out_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=1), encoding="utf-8")
    human_form(out_dir, metrics)
    assessment = {"video_sha256": digest, "reviewer_preflight": empty_preflight()}
    for channel in ("visual", "motion", "audio"):
        assessment[channel] = {"status": "not_applicable" if channel == "audio" and not has_audio else "pending",
                               "method": "", "ranges": []}
    (out_dir / "assessment.json").write_text(json.dumps(assessment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    rel = out_dir.relative_to(proj).as_posix()
    lines = [
        f"# Revisão {out_dir.name}", "",
        f"Vídeo: `{video.name}`, {dur:.1f} s, {fps} qps. Grade: `{rel}/grid.jpg` "
        f"({n_frames} quadros, um a cada {a.every:g} s). Gancho: `{rel}/hook.jpg` (0; 0,5; 1; 1,5; 2 s).", "",
        "## Métricas", "",
        "| Métrica | Valor |", "|---|---|",
        f"| Cortes | {len(cuts)} |",
        f"| Eventos visuais | {len(events)} ({metrics['events_per_10s']} a cada 10 s; alvo {'1–3' if long_ else '4–7'}) |",
        f"| Plano médio / mais longo | {metrics['mean_shot_s']} s / {metrics['longest_shot_s']} s |",
        f"| Início da fala | {'—' if speech is None else f'{speech:.2f} s'} |",
        f"| Tempo audível (silêncio <{SILENCE_DB} dB) | {activity['audible_fraction']:.1%} |",
        f"| Faixa uniforme persistente | {band['height_fraction']:.0%} da altura |" if band else "| Faixa uniforme persistente | não detectada |",
        f"| Luma do quadro 0 | {'—' if luma0 is None else f'{luma0:.0f}'} |", "",
        "Movimento por segundo:", "", "```", sparkline(secs),
        "".join(str(i % 10) for i in range(len(secs))), "```", "",
        "## Alertas", "",
    ]
    lines += [f"- **Bloqueante:** {b}" for b in block] + [f"- {w}" for w in warn] or ["- Nenhum."]
    lines += ["", "## Notas do revisor independente (1 a 5, depois de inspecionar as modalidades reais)", "",
              "| Critério | O que olhar | Nota | Correção |", "|---|---|---|---|"]
    lines += [f"| {k} | {v} |  |  |" for k, v in rubric]
    lines += ["", "Passa com todas as notas 4 ou mais e nenhum bloqueante. Senão, aplique as 3 correções de "
              "maior efeito, renderize de novo e rode outra rodada (máximo 3). Depois de preencher, rode "
              "`python scripts/review.py <projeto> --verdict`; só declare pronto se ele sair com 0. "
              "Código 3 entrega apenas o melhor resultado com limitações, nunca aprovação. "
              "Preencha assessment.json com método e intervalos reais de inspeção visual, temporal e de áudio; "
              "não descreva uma grade de imagens como reprodução ou escuta do vídeo. "
              "Envie somente input/ e os critérios ao revisor, sem notas/conclusões do autor. "
              "A aprovação completa exige observação por revisor distinto e cobertura de todas as modalidades aplicáveis."]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    m.setdefault("review", []).append({"round": out_dir.name, "video": video.name,
                                       "blockers": len(block), "warnings": len(warn)})
    save_manifest(proj, m)

    print(f"  eventos visuais: {len(events)} ({metrics['events_per_10s']}/10 s), cortes: {len(cuts)}, "
          f"fala em: {'—' if speech is None else f'{speech:.2f} s'}")
    print(f"  movimento: {sparkline(secs)}")
    for b in block:
        print(f"  BLOQUEANTE: {b}")
    for w in warn:
        print(f"  alerta: {w}")
    print(f"Pacote para revisor independente: {rel}/input/. Confira capacidades antes de delegar; "
          f"depois registre a avaliação em {rel}/assessment.json, notas em report.md e rode --verdict.")
    print(f"Rota humana: entregue input/ e {rel}/ficha-humana.md a uma pessoa independente; "
          "após preenchimento, use --human-form <ficha> (sem gerar nova rodada).")
    verdict(proj)  # Relata a pendência; o código da geração continua indicando apenas a análise técnica.
    sys.exit(1 if block else 0)


if __name__ == "__main__":
    main()
