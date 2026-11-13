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
import os
import re
import shutil
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import file_sha256, manifest_sha256, ffprobe_json, load_manifest, need, project_dir, run, save_manifest  # noqa: E402

BARS = "▁▂▃▄▅▆▇█"
RUBRIC = [
    ("Gancho", "Quadro 0 legível e intrigante, até 6 palavras na tela, fala em até 0,5 s, imagem forte sem depender do som"),
    ("Ritmo", "Evento visual a cada 1,5–3 s, nenhum trecho parado, cortes na palavra"),
    ("Direção de arte", "Paleta, fontes e textura do direction em todas as cenas; nada com cara de padrão"),
    ("Motion", "Curvas e durações do motion.md, um foco por vez, câmera sempre viva"),
    ("Fala e imagem", "Cada plano mostra o que a narração diz naquele instante, acrescentando em vez de repetir"),
    ("Legibilidade", "Contraste, tamanho, área segura, legenda fora do assunto principal"),
    ("Som", "Efeitos nas entradas, música que abaixa sob a voz e sobe no payoff, voz clara"),
    ("Payoff", "Entrega a promessa do gancho; final em loop ou corte no ponto alto"),
]
RECORDED = {"gravacao", "corte", "ugc"}
RECORDED_RUBRIC = [
    ("Corte de fala", "Sem silêncio, vício ou retomada sobrando; corte no fim da palavra, sem estalo nem respiração cortada"),
    ("Enquadramento", "Rosto no terço superior, nada cortado na cabeça; zoom alterna para esconder o jump cut; B-roll quando a fala cita algo"),
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
    if is_long(m, dur):
        r.insert(2, LONG_RUBRIC[0])
        r = [(k, "Entrega a promessa do título; CTA sem anunciar o fim antes da hora") if k == "Payoff" else (k, v)
             for k, v in r]
    return r


def tile_size(m):
    w, h = (m.get("size") or [1080, 1920])[:2]
    k = 320 / max(w, h)
    return int(w * k) // 2 * 2, int(h * k) // 2 * 2


def next_round(proj):
    base = proj / "review"
    base.mkdir(exist_ok=True)
    nums = [int(p.name[1:]) for p in base.glob("r[0-9][0-9]") if p.is_dir()]
    d = base / f"r{(max(nums) + 1 if nums else 1):02d}"
    d.mkdir()
    return d


def frames(ff, video, out_dir, dur, fps, every, tw, th):
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
    """Cortes (scdet), congelamentos (freezedetect) e energia de movimento por quadro (tblend)."""
    graph = (f"[0:v]scale={tw}:{th},fps={fps},split=3[a][b][c];"
             "[a]scdet=threshold=10,metadata=select:key=lavfi.scd.time,"
             "metadata=print:key=lavfi.scd.time:file=cuts.txt,nullsink;"
             "[b]freezedetect=n=-50dB:d=1.5,nullsink;"
             "[c]tblend=all_mode=difference,signalstats,"
             "metadata=print:key=lavfi.signalstats.YAVG:file=energy.txt[out]")
    r = run([ff, "-hide_banner", "-nostats", "-i", str(video), "-filter_complex", graph, "-map", "[out]",
             "-f", "null", "-"], cwd=out_dir)
    cuts = [float(x) for x in re.findall(r"lavfi\.scd\.time=([\d.]+)", (out_dir / "cuts.txt").read_text())]
    energy = [(float(t), float(v)) for t, v in re.findall(
        r"pts_time:([\d.]+)\s*\n\s*lavfi\.signalstats\.YAVG=([\d.]+)", (out_dir / "energy.txt").read_text())]
    starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", r.stderr)]
    durs = [float(x) for x in re.findall(r"freeze_duration: ([\d.]+)", r.stderr)]
    freezes = [(s, d) for s, d in zip(starts, durs)]
    if len(starts) > len(durs):  # congelado até o fim
        freezes.append((starts[-1], None))
    for f in ("cuts.txt", "energy.txt"):
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


def manifest_checks(proj, m, long_):
    warn = []
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
        if shots and dur / shots > 3.5:
            warn.append(f"{s['id']}: {shots} plano(s) em {dur:.1f} s, mais de 3,5 s por plano.")
    if m.get("scenes"):
        os0 = (m["scenes"][0].get("on_screen") or "").split()
        if not os0:
            warn.append("Primeira cena sem texto na tela para o gancho.")
        elif len(os0) > 6:
            warn.append(f"Texto do gancho na tela com {len(os0)} palavras (máximo 6).")
    kinds = {a.get("kind") for a in m.get("assets", [])}
    sfx_dir = proj / "audio" / "sfx"
    if "sfx" not in kinds and not (sfx_dir.is_dir() and any(sfx_dir.iterdir())):
        warn.append("Nenhum efeito sonoro registrado: transições e revelações ficam mudas.")
    if not (proj / "audio" / "music.wav").exists() and "music" not in kinds:
        warn.append("Sem trilha musical.")
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
    if not isinstance(capabilities, dict) or capabilities.get("schema") != 1:
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
    try:
        os.link(video, clip)
    except OSError:
        shutil.copyfile(video, clip)
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


def verdict(proj):
    """Lê as notas da última rodada e decide: 0 aprovado, 1 outra rodada, 2 notas faltando, 3 limite atingido."""
    rounds = sorted(p for p in (proj / "review").glob("r[0-9][0-9]") if p.is_dir()) if (proj / "review").is_dir() else []
    if not rounds:
        print("Nenhuma rodada de revisão. Rode review.py primeiro.")
        return 2
    last = rounds[-1]
    n = int(last.name[1:])
    report = (last / "report.md").read_text(encoding="utf-8") if (last / "report.md").exists() else ""
    mpath = last / "metrics.json"
    try:
        met = json.loads(mpath.read_text(encoding="utf-8"))
        if met["schema"] != 2:
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
        if keys != met["rubric"] or not isinstance(met["blockers"], list):
            raise ValueError("métricas ou critérios inconsistentes")
        for name in ("hook.jpg", "grid.jpg"):
            if file_sha256(last / name) != met["frame_sha256"][name]:
                raise ValueError(f"{name} mudou depois da análise")
        receipt = json.loads((proj / "out" / "delivery.json").read_text(encoding="utf-8"))
        if receipt["schema"] != 1 or receipt["manifest_sha256"] != met["manifest_sha256"]:
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
        if request["schema"] != 1 or request["video_sha256"] != digest or request["manifest_sha256"] != met["manifest_sha256"]:
            raise ValueError("pacote de revisão incompatível com o render/manifesto")
        clip_name = request["artifacts"]["video"]
        if not isinstance(clip_name, str) or Path(clip_name).name != clip_name or file_sha256(last / "input" / clip_name) != digest:
            raise ValueError("vídeo do pacote independente ausente ou alterado")
        if {path.name for path in (last / "input").iterdir()} != {clip_name, "request.json", "hook.jpg", "grid.jpg"}:
            raise ValueError("o pacote independente contém arquivos não previstos; não inclua notas do autor")
        if request["technical"]["has_audio"] is not met["has_audio"] or request["technical"]["duration"] != met["duration"]:
            raise ValueError("modalidades/duração divergem do pacote de revisão")
        for name in ("hook.jpg", "grid.jpg"):
            if file_sha256(last / "input" / name) != met["frame_sha256"][name]:
                raise ValueError("imagens do pacote independente foram alteradas")
        required = ("visual", "motion", "audio") if met["has_audio"] else ("visual", "motion")
        capabilities = assessment["reviewer_preflight"]
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
            if not ranges or any(len(r) != 2 or not 0 <= r[0] < r[1] <= met["duration"] + 0.05 for r in ranges):
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
        nota = next((c for c in cells[1:] if re.fullmatch(r"(?:[1-4]([.,]\d)?|5([.,]0)?)", c)), None)
        if nota:
            scores[names[cells[0].lower()]] = float(nota.replace(",", "."))
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
    ap.add_argument("--check-reviewer", type=Path, help="confere o preflight antes de delegar; não gera revisão")
    ap.add_argument("--channels", nargs="+", choices=CHANNELS, default=list(CHANNELS),
                    help="escopo solicitado em --check-reviewer; o veredito completo exige todas as modalidades aplicáveis")
    ap.add_argument("--video", help="padrão: out/<slug>.mp4, senão out/<slug>_rascunho.mp4, senão render/master.mp4")
    ap.add_argument("--every", type=float, help="intervalo entre quadros da grade, em segundos (padrão: 1, ou dur/48)")
    ap.add_argument("--verdict", action="store_true",
                    help="não gera rodada; lê as notas da última e diz se o vídeo pode ser declarado pronto")
    a = ap.parse_args()

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
    a.every = a.every or (1.0 if dur <= 48 else round(dur / 48, 1))
    afps = min(fps, 10) if dur > 180 else fps  # análise mais leve em vídeo longo
    tw, th = tile_size(m)
    out_dir = next_round(proj)
    print(f"Revisão {out_dir.name}: {video.name}, {dur:.1f} s")
    n_frames = frames(ff, video, out_dir, dur, fps, a.every, tw, th)
    cuts, energy, freezes = analyze(ff, video, out_dir, afps, tw, th)
    luma0 = first_luma(ff, video)
    voice = proj / "audio" / "voice.wav"
    speech = speech_start(ff, voice if voice.exists() else video) if (voice.exists() or has_audio) else None

    secs = per_second(energy, dur)
    events = visual_events(cuts, energy)
    gap_max = 8.0 if long_ else 3.0
    gaps, prev = [], 0.0
    for t in events + [dur]:
        if t - prev > gap_max:
            gaps.append((prev, t))
        prev = t
    shot_lens = [b - a_ for a_, b in zip([0.0] + cuts, cuts + [dur])]

    block, warn = [], []
    if luma0 is not None and luma0 < 20:
        block.append(f"Primeiro quadro quase preto (luma {luma0:.0f}): o gancho precisa aparecer no quadro 0.")
    for s, d in freezes:
        d_txt = f"{d:.1f} s" if d else "até o fim"
        if d is None or d >= 2.5:
            block.append(f"Imagem congelada em {s:.1f} s por {d_txt}.")
        else:
            warn.append(f"Imagem quase parada em {s:.1f} s por {d_txt}.")
    if m.get("format") == "musica":
        pass  # Music/lyric videos need musical timing, not immediate speech.
    elif speech is None:
        warn.append("Não achei fala no áudio.")
    elif speech > 0.7:
        block.append(f"A fala começa em {speech:.2f} s: comece em até 0,5 s.")
    first_event = next((t for t in events if t > 0.05), None)
    if first_event is None or first_event > 2.0:
        warn.append("Nenhuma mudança visual forte nos 2 primeiros segundos.")
    for g0, g1 in gaps:
        warn.append(f"{g1 - g0:.1f} s sem evento visual ({g0:.1f}–{g1:.1f} s).")
    warn += manifest_checks(proj, m, long_)

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
        "blockers": block, "warnings": warn, "format": m.get("format", "narrado"), "long": long_,
        "rubric": [k for k, _ in rubric],
    }
    metrics["review_request_sha256"] = prepare_review_input(out_dir, video, m, metrics, a.producer_id)
    (out_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=1), encoding="utf-8")
    assessment = {"video_sha256": digest, "reviewer_preflight": {
        "schema": 1, "reviewer_id": "", "author_scores_exposed": None,
        "channels": {channel: {"available": None, "method": "", "evidence": ""} for channel in CHANNELS}}}
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
    sys.exit(1 if block else 0)


if __name__ == "__main__":
    main()
