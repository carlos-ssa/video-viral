"""Edição da sua própria gravação: limpa o áudio, corta silêncios e vícios, reenquadra e renderiza.

Uso:
  python scripts/footage.py import <projeto> <video> [--from 0:30 --to 2:10] [--no-clean] [--third-party]
  python scripts/footage.py cut <projeto> [--min-silence 0.45] [--pad 0.12] [--noise -35]
                                          [--fillers tipo,né] [--zoom 1.15 | --no-zoom] [--max-shot 2.6]
  python scripts/footage.py frames <projeto>
  python scripts/footage.py render <projeto> [--crf 18]

Fluxo:
  1. import guarda o caminho do vídeo (não copia) e extrai audio/source.wav (48 kHz mono, com redução de
     ruído leve, filtro de graves e compressão; --no-clean desliga). Todos os tempos da edição contam a partir
     do início do trecho (--from).
  2. Transcreva para achar vícios e retomadas (opcional, mas recomendado):
     captions.py transcribe <projeto> --out captions/source_words.json   (ou captions.py import --file x.srt --out ...)
  3. cut detecta silêncios (e vícios, se houver source_words.json) e grava edit/edl.json e edit/transcript.md.
     Leia o transcript: marque "keep": false nas retomadas e trechos fracos, e mova para o começo do
     "segments" a frase que serve de gancho, se ela não estiver lá. A ordem da lista é a ordem do vídeo.
  4. frames grava edit/frames.jpg: um quadro por trecho com linhas a cada 10% da largura (linha mais grossa no
     meio) e o retângulo do enquadramento atual em vermelho. Ajuste "x" (0 a 1, centro do rosto) de cada trecho
     e, se precisar, "y" e "zoom". Rode de novo para conferir.
  5. render corta cada trecho com o enquadramento e o zoom, junta em render/master.mp4, aplica as inserções
     de "overlays" (B-roll, print, imagem) e converte captions/source_words.json para captions/words.json na
     linha do tempo nova. Depois: captions.py ass, deliver.py, review.py.

Inserções em edit/edl.json: {"file": "assets/broll1.mp4", "at": 12.5, "dur": 2.0} com "at" no tempo do vídeo
final (veja edit/timeline.md depois do primeiro render) ou {"src": 47.2, ...} no tempo da gravação.
Registre a licença de cada inserção no video.json (add_asset) como qualquer outro ativo.
"""
import argparse
import json
import math
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import add_asset, ffprobe_json, load_manifest, need, project_dir, run, save_manifest  # noqa: E402

CLEAN = ("highpass=f=70,afftdn=nf=-25:tn=1,"
         "acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2")
FILLER_RE = re.compile(r"^(a+h+n*|ahm|h+m+|hu+m+|é{2,}h*|e{2,}h*|ehm|ã{2,}|hã+|u+h+|u+m{2,}|u{2,}m+|uhm|hum)$", re.I)
FONTS = [Path("C:/Windows/Fonts/arial.ttf"), Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
         Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]


def secs(v):
    if v is None:
        return None
    t = 0.0
    for part in str(v).strip().split(":"):
        t = t * 60 + float(part)
    return t


def even(v):
    return max(2, int(v) // 2 * 2)


def norm(w):
    return re.sub(r"[^\wáàâãéêíóôõúç]", "", w.lower())


def load_edl(proj):
    p = proj / "edit" / "edl.json"
    if not p.exists():
        sys.exit("Falta edit/edl.json. Rode 'footage.py cut' antes.")
    return json.loads(p.read_text(encoding="utf-8"))


def save_edl(proj, edl):
    (proj / "edit" / "edl.json").write_text(json.dumps(edl, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def source_of(proj, m):
    src = m.get("source") or {}
    if not src.get("footage"):
        sys.exit("O projeto não tem gravação. Rode 'footage.py import' antes.")
    path = Path(src["footage"])
    if not path.exists():
        sys.exit(f"Gravação não encontrada: {path}")
    return path, src


def source_words(proj):
    p = proj / "captions" / "source_words.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


# ---------------------------------------------------------------- import

def cmd_import(proj, m, a):
    ff = need("ffmpeg")
    path = Path(a.video).expanduser().resolve()
    if not path.exists():
        sys.exit(f"Vídeo não encontrado: {path}")
    info = ffprobe_json(path)
    vs = next((s for s in info["streams"] if s.get("codec_type") == "video"), None)
    has_audio = any(s.get("codec_type") == "audio" for s in info["streams"])
    if not vs:
        sys.exit(f"{path.name} não tem faixa de vídeo.")
    dur = float(info["format"]["duration"])
    t0 = secs(a.from_) or 0.0
    t1 = min(secs(a.to) or dur, dur)
    if t1 <= t0:
        sys.exit("--to precisa ser depois de --from.")
    w, h = int(vs["width"]), int(vs["height"])
    rot = int(float((vs.get("tags") or {}).get("rotate", 0) or 0))
    for sd in vs.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(float(sd["rotation"]))
    if abs(rot) in (90, 270):
        w, h = h, w
    num, den = (vs.get("avg_frame_rate") or "30/1").split("/")
    fps = float(num) / float(den) if float(den) else 30.0

    (proj / "audio").mkdir(exist_ok=True)
    wav = proj / "audio" / "source.wav"
    if has_audio:
        af = ["-af", CLEAN] if not a.no_clean else []
        run([ff, "-y", "-hide_banner", "-nostats", "-ss", f"{t0:.3f}", "-to", f"{t1:.3f}", "-i", str(path),
             "-vn", "-ac", "1", "-ar", "48000", *af, "-c:a", "pcm_s16le", str(wav)])
    else:
        print("Aviso: a gravação não tem áudio; cortes por silêncio não vão funcionar.")

    m["source"] = {"footage": str(path), "range": [round(t0, 3), round(t1, 3)],
                   "audio": "audio/source.wav" if has_audio else "", "width": w, "height": h,
                   "fps": round(fps, 3), "duration": round(t1 - t0, 3), "cleaned": has_audio and not a.no_clean}
    if m.get("format") in (None, "narrado"):
        m["format"] = "gravacao"
    m.setdefault("voice", {})["engine"] = "gravacao"
    if a.third_party:
        add_asset(m, str(path), "footage", "vídeo de terceiro", "terceiro, autorização a confirmar", None)
    else:
        add_asset(m, str(path), "footage", "gravação do usuário", "própria", True)
    save_manifest(proj, m)
    print(f"Gravação: {path.name} {w}x{h} {fps:.2f} fps, trecho {t0:.1f}–{t1:.1f} s ({t1 - t0:.1f} s)")
    if has_audio:
        print(f"audio/source.wav {'limpo' if not a.no_clean else 'sem limpeza'}.")
    print("Próximo: captions.py transcribe <projeto> --out captions/source_words.json (ou import --file x.srt), "
          "depois footage.py cut.")


# ---------------------------------------------------------------- cut

def silences(ff, wav, noise, min_sil):
    r = run([ff, "-hide_banner", "-nostats", "-i", str(wav), "-af",
             f"silencedetect=n={noise}dB:d={min_sil}", "-f", "null", "-"])
    st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return [(max(s, 0.0), en[i] if i < len(en) else None) for i, s in enumerate(st)]


def subtract(keep, holes):
    out = []
    for s, e in keep:
        cur = [(s, e)]
        for hs, he in holes:
            nxt = []
            for cs, ce in cur:
                if he <= cs or hs >= ce:
                    nxt.append((cs, ce))
                    continue
                if hs > cs:
                    nxt.append((cs, hs))
                if he < ce:
                    nxt.append((he, ce))
            cur = nxt
        out += cur
    return out


def cmd_cut(proj, m, a):
    ff = need("ffmpeg")
    _, src = source_of(proj, m)
    dur = float(src["duration"])
    wav = proj / (src.get("audio") or "audio/source.wav")
    holes = []
    if wav.exists():
        for s, e in silences(ff, wav, a.noise, a.min_silence):
            e = dur if e is None else e
            if e - s > 2 * a.pad:
                holes.append((s + a.pad, e - a.pad))
    words = source_words(proj)
    extra = {norm(x) for x in (a.fillers or "").split(",") if x.strip()}
    removed_fillers = []
    for i, w in enumerate(words):
        n = norm(w["w"])
        if (FILLER_RE.match(n) or n in extra) and w.get("end") is not None and w["end"] - w["start"] >= 0.12:
            prev_end = words[i - 1]["end"] if i else 0.0
            nxt_start = words[i + 1]["start"] if i + 1 < len(words) else dur
            hs, he = max(w["start"] - 0.03, prev_end), min(w["end"] + 0.03, nxt_start)
            if he - hs >= 0.12:
                holes.append((hs, he))
                removed_fillers.append(w["w"])
    holes.sort()
    keep = [(s, e) for s, e in subtract([(0.0, dur)], holes) if e - s >= 0.3]
    merged = []
    for s, e in keep:
        if merged and s - merged[-1][1] < 0.08:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))

    # trecho longo sem pausa fica parado na tela: divide em planos com zoom alternado (punch-in).
    # O corte cai num intervalo entre palavras (se houver transcrição) e na grade de quadros, para o
    # áudio seguir contínuo entre as partes.
    W, H = m.get("size", [1080, 1920])
    fps = int(m.get("fps", 30))
    target = a.max_shot if a.max_shot is not None else (2.6 if H > W else 6.0)
    gaps = [((w["end"] + n["start"]) / 2) for w, n in zip(words, words[1:])
            if w.get("end") is not None and n.get("start") is not None]
    pieces = []
    for s, e in merged:
        L = e - s
        k = math.ceil(L / (target * 1.15)) if target > 0 else 1  # nenhum plano acima de ~1,15 × alvo
        cuts = [s]
        for j in range(1, k):
            t = s + L * j / k
            near = [g for g in gaps if abs(g - t) <= 0.5 and cuts[-1] + 1.2 < g < e - 1.2]
            if near:
                t = min(near, key=lambda g: abs(g - t))
            t = s + round((t - s) * fps) / fps
            if t - cuts[-1] >= 1.2 and e - t >= 1.2:
                cuts.append(t)
        pieces += [(c, n) for c, n in zip(cuts, cuts[1:] + [e])]
    merged = pieces

    old = {}
    if (proj / "edit" / "edl.json").exists() and not a.reset:
        prev = load_edl(proj)
        old = {"overlays": prev.get("overlays", []), "fit": prev.get("fit"), "segments": prev.get("segments", [])}
    vertical_src = src["height"] > src["width"]
    fit = old.get("fit") or ("blur" if vertical_src and W > H else "crop")
    segs = []
    for i, (s, e) in enumerate(merged):
        text = " ".join(w["w"] for w in words if s <= (w["start"] + w["end"]) / 2 < e)
        segs.append({"id": f"c{i + 1:02d}", "in": round(s, 3), "out": round(e, 3), "keep": True,
                     "zoom": 1.0 if (a.no_zoom or i % 2 == 0) else a.zoom, "x": 0.5, "y": 0.5, "text": text})
    framed = 0
    for sg in segs:  # leva enquadramento e descarte do corte anterior para o trecho que mais se sobrepõe
        best, ov = None, 0.0
        for o in old.get("segments", []):
            v = min(sg["out"], o["out"]) - max(sg["in"], o["in"])
            if v > ov:
                best, ov = o, v
        if best and ov >= 0.5 * (sg["out"] - sg["in"]):
            sg.update({k: best[k] for k in ("x", "y") if k in best})
            if best.get("keep") is False:
                sg["keep"] = False
            framed += 1
    edl = {"fit": fit, "segments": segs, "overlays": old.get("overlays", [])}
    (proj / "edit").mkdir(exist_ok=True)
    save_edl(proj, edl)
    m.setdefault("edit", {})["edl"] = "edit/edl.json"
    save_manifest(proj, m)
    write_transcript(proj, edl)
    kept = sum(s["out"] - s["in"] for s in segs)
    print(f"{len(segs)} trechos; {kept:.1f} s de {dur:.1f} s ({100 * (1 - kept / dur):.0f}% cortado)")
    if removed_fillers:
        print(f"Vícios removidos ({len(removed_fillers)}): {', '.join(removed_fillers[:15])}")
    if not words:
        print("Sem captions/source_words.json: só silêncios foram cortados e o transcript não tem texto. "
              "Transcreva para cortar vícios e achar retomadas.")
    print("Leia edit/transcript.md, ajuste edit/edl.json (keep, ordem, x) e rode 'frames' e 'render'.")


def write_transcript(proj, edl):
    segs = edl["segments"]
    lines = ["# Transcrição por trecho", "",
             "Marque \"keep\": false no edit/edl.json para tirar um trecho; mova o gancho para o topo da lista.", "",
             "| Trecho | Gravação (s) | Dur. | Mantém | Texto | Obs. |", "|---|---|---|---|---|---|"]
    for i, s in enumerate(segs):
        ws = [norm(w) for w in s["text"].split()]
        obs = []
        for t in segs[i + 1:i + 3]:
            tw = [norm(w) for w in t["text"].split()]
            k = min(len(ws), 3)
            if k >= 2 and ws[:k] == tw[:k]:
                obs.append(f"retomada? {t['id']} começa igual; mantenha só a melhor")
                break
        if s["out"] - s["in"] < 0.8 and not s["text"]:
            obs.append("curto e sem fala")
        lines.append(f"| {s['id']} | {s['in']:.2f}–{s['out']:.2f} | {s['out'] - s['in']:.1f} | "
                     f"{'sim' if s.get('keep', True) else 'não'} | {s['text'] or '-'} | {'; '.join(obs)} |")
    (proj / "edit" / "transcript.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- frames / crop

def crop_box(sw, sh, W, H, seg, fit):
    """Retângulo (x, y, w, h) da gravação que vira o quadro final."""
    z = max(1.0, float(seg.get("zoom", 1.0)))
    ar = W / H
    if fit == "blur":
        cw, ch = sw / z, sh / z
    elif sw / sh > ar:
        ch = sh / z
        cw = ch * ar
    else:
        cw = sw / z
        ch = cw / ar
    cw, ch = min(even(cw), even(sw)), min(even(ch), even(sh))
    cx = min(max(float(seg.get("x", 0.5)) * sw - cw / 2, 0), sw - cw)
    cy = min(max(float(seg.get("y", 0.5)) * sh - ch / 2, 0), sh - ch)
    return int(cx), int(cy), cw, ch


def font():
    return next((f for f in FONTS if f.exists()), None)


def cmd_frames(proj, m, a):
    ff = need("ffmpeg")
    path, src = source_of(proj, m)
    edl = load_edl(proj)
    W, H = m.get("size", [1080, 1920])
    sw, sh = src["width"], src["height"]
    t_off = src["range"][0]
    th = 300
    tw = even(sw * th / sh)
    k = th / sh
    fdir = proj / "edit" / "frames"
    if fdir.exists():
        shutil.rmtree(fdir)
    fdir.mkdir(parents=True)
    fnt = font()
    segs = [s for s in edl["segments"] if s.get("keep", True)]
    for i, s in enumerate(segs):
        x, y, cw, ch = crop_box(sw, sh, W, H, s, edl.get("fit", "crop"))
        grid = ",".join(f"drawbox=x={int(tw * g / 10)}:y=0:w={3 if g == 5 else 1}:h={th}:color=white@0.6:t=fill"
                        for g in range(1, 10))
        vf = (f"scale={tw}:{th},setsar=1,{grid},"
              f"drawbox=x={int(x * k)}:y={int(y * k)}:w={int(cw * k)}:h={int(ch * k)}:color=red:t=3")
        if fnt:
            vf += (f",drawtext=fontfile={fnt.name}:text='{s['id']} x={s.get('x', 0.5)}':x=6:y=6:fontsize=20:"
                   "fontcolor=yellow:box=1:boxcolor=black@0.6")
        t = t_off + (s["in"] + s["out"]) / 2
        r = run([ff, "-y", "-hide_banner", "-ss", f"{t:.3f}", "-i", str(path), "-frames:v", "1", "-vf", vf,
                 "-q:v", "4", str(fdir / f"f{i + 1:03d}.jpg")], cwd=str(fnt.parent) if fnt else None, check=False)
        if r.returncode != 0 and fnt:
            fnt = None  # fonte não carregou: segue sem rótulo
            vf = vf.rsplit(",drawtext", 1)[0]
            run([ff, "-y", "-hide_banner", "-ss", f"{t:.3f}", "-i", str(path), "-frames:v", "1", "-vf", vf,
                 "-q:v", "4", str(fdir / f"f{i + 1:03d}.jpg")])
    cols = 4 if tw < th else 3
    rows = -(-len(segs) // cols)
    out = proj / "edit" / "frames.jpg"
    run([ff, "-y", "-hide_banner", "-framerate", "1", "-i", str(fdir / "f%03d.jpg"),
         "-vf", f"tile={cols}x{rows}:padding=4:color=gray", "-frames:v", "1", "-q:v", "3", str(out)])
    print(f"edit/frames.jpg: {len(segs)} trechos em ordem ({cols} por linha); linhas brancas a cada 10% da largura, "
          "retângulo vermelho = enquadramento. Ajuste 'x' no edit/edl.json.")


# ---------------------------------------------------------------- render

def out_map(segs):
    """Lista (seg, início no vídeo final)."""
    t, out = 0.0, []
    for s in segs:
        out.append((s, t))
        t += s["_dur"]
    return out


def src_to_out(mapping, t):
    for s, o in mapping:
        if s["in"] <= t < s["out"]:
            return o + (t - s["in"])
    return None


def cmd_render(proj, m, a):
    ff = need("ffmpeg")
    path, src = source_of(proj, m)
    edl = load_edl(proj)
    W, H = m.get("size", [1080, 1920])
    fps = int(m.get("fps", 30))
    sw, sh = src["width"], src["height"]
    t_off = src["range"][0]
    fit = edl.get("fit", "crop")
    wav = proj / (src.get("audio") or "")
    use_wav = bool(src.get("audio")) and wav.is_file()
    segs = [s for s in edl["segments"] if s.get("keep", True)]
    if not segs:
        sys.exit("Nenhum trecho com keep=true no edit/edl.json.")
    tmp = proj / "render" / "segs"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    listing = []
    print(f"Renderizando {len(segs)} trechos...")
    for i, s in enumerate(segs):
        n = max(1, round((s["out"] - s["in"]) * fps))
        s["_dur"] = n / fps
        x, y, cw, ch = crop_box(sw, sh, W, H, s, fit)
        if fit == "blur":
            vf = (f"[0:v]crop={cw}:{ch}:{x}:{y},split[a][b];"
                  f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,eq=brightness=-0.08[bg];"
                  f"[b]scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos[fg];"
                  f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps={fps},format=yuv420p[v]")
        else:
            vf = f"[0:v]crop={cw}:{ch}:{x}:{y},scale={W}:{H}:flags=lanczos,setsar=1,fps={fps},format=yuv420p[v]"
        d = s["_dur"]
        # sem fade onde o trecho continua direto do anterior ou no seguinte (plano dividido por --max-shot)
        cont_in = i > 0 and abs(segs[i - 1]["out"] - s["in"]) < 0.002
        cont_out = i + 1 < len(segs) and abs(segs[i + 1]["in"] - s["out"]) < 0.002
        fades = ([] if cont_in else ["afade=t=in:d=0.012"]) +                 ([] if cont_out else [f"afade=t=out:st={max(d - 0.012, 0):.3f}:d=0.012"])
        af = ",".join(["aresample=48000"] + fades) + "[aout]"
        inputs = ["-ss", f"{t_off + s['in']:.3f}", "-i", str(path)]
        if use_wav:
            inputs += ["-ss", f"{s['in']:.3f}", "-i", str(wav)]
            af = "[1:a]" + af
        else:
            inputs += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono"]
            af = "[1:a]" + af
        out = tmp / f"{i + 1:04d}.mkv"
        run([ff, "-y", "-hide_banner", "-nostats", *inputs, "-filter_complex", f"{vf};{af}",
             "-map", "[v]", "-map", "[aout]", "-frames:v", str(n), "-t", f"{d:.4f}",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-g", str(fps),
             "-c:a", "pcm_s16le", "-ac", "1", str(out)])
        listing.append(f"file '{out.name}'")
    (tmp / "list.txt").write_text("\n".join(listing) + "\n", encoding="utf-8")
    joined = proj / "render" / "joined.mp4"
    run([ff, "-y", "-hide_banner", "-f", "concat", "-safe", "0", "-i", "list.txt", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(joined)], cwd=str(tmp))

    mapping = out_map(segs)
    total = sum(s["_dur"] for s in segs)
    master = proj / "render" / "master.mp4"
    ovs = []
    for o in edl.get("overlays", []):
        at = o.get("at")
        if at is None and o.get("src") is not None:
            at = src_to_out(mapping, float(o["src"]))
        f = Path(o["file"]) if Path(o["file"]).is_absolute() else proj / o["file"]
        if at is None or not f.exists():
            print(f"Aviso: inserção ignorada ({o.get('file')}): {'arquivo não existe' if not f.exists() else 'tempo fora dos trechos mantidos'}")
            continue
        ovs.append((f, float(at), float(o.get("dur", 2.0))))
    if ovs:
        args, fc, last = [ff, "-y", "-hide_banner", "-nostats", "-i", str(joined)], [], "[0:v]"
        for k, (f, at, d) in enumerate(ovs, start=1):
            img = f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")
            args += (["-loop", "1", "-t", f"{d:.3f}", "-i", str(f)] if img else ["-t", f"{d:.3f}", "-i", str(f)])
            fc.append(f"[{k}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={fps},"
                      f"setpts=PTS-STARTPTS+{at:.3f}/TB[o{k}]")
            fc.append(f"{last}[o{k}]overlay=enable='between(t,{at:.3f},{at + d:.3f})':eof_action=pass[v{k}]")
            last = f"[v{k}]"
        run(args + ["-filter_complex", ";".join(fc), "-map", last, "-map", "0:a", "-c:v", "libx264", "-preset",
                    "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "copy", str(master)])
        joined.unlink()
    else:
        joined.replace(master)
    shutil.rmtree(tmp)

    words = source_words(proj)
    if words:
        out_words = []
        for w in words:
            mid = (w["start"] + w["end"]) / 2
            for k, (s, o) in enumerate(mapping):
                if s["in"] <= mid < s["out"]:
                    st = o + max(w["start"] - s["in"], 0)
                    en = o + min(w["end"] - s["in"], s["_dur"])
                    nw = {**w, "start": round(st, 3), "end": round(max(en, st + 0.05), 3)}
                    nw.pop("jump", None)
                    # salto na gravação: a legenda não junta palavras de frases que não eram vizinhas
                    nw["_seg"], nw["_cont"] = k, k > 0 and abs(mapping[k - 1][0]["out"] - s["in"]) < 0.05
                    out_words.append(nw)
                    break
        out_words.sort(key=lambda w: w["start"])
        for prev, w in zip([None] + out_words, out_words):
            if prev is not None and w["_seg"] != prev["_seg"] and not w["_cont"]:
                w["jump"] = True
        for w in out_words:
            del w["_seg"], w["_cont"]
        (proj / "captions" / "words.json").write_text(json.dumps(out_words, ensure_ascii=False, indent=1),
                                                       encoding="utf-8")
        print(f"captions/words.json: {len(out_words)} de {len(words)} palavras na linha do tempo nova")
    tl = ["# Linha do tempo do vídeo editado", "", "| Trecho | Vídeo final (s) | Gravação (s) | Texto |", "|---|---|---|---|"]
    for s, o in mapping:
        tl.append(f"| {s['id']} | {o:.2f}–{o + s['_dur']:.2f} | {s['in']:.2f}–{s['out']:.2f} | {s.get('text') or '-'} |")
    (proj / "edit" / "timeline.md").write_text("\n".join(tl) + "\n", encoding="utf-8")
    print(f"render/master.mp4: {total:.1f} s, {len(segs)} trechos, {len(ovs)} inserção(ões); edit/timeline.md")
    print("Próximo: revisar a base, compor acabamento conforme direção (references/formats/gravacao.md), captions.py ass, deliver.py e review.py.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["import", "cut", "frames", "render"])
    ap.add_argument("project")
    ap.add_argument("video", nargs="?")
    ap.add_argument("--from", dest="from_", help="import: início do trecho (s ou mm:ss)")
    ap.add_argument("--to", help="import: fim do trecho")
    ap.add_argument("--no-clean", action="store_true", help="import: não tratar o áudio")
    ap.add_argument("--third-party", action="store_true", help="import: vídeo de outra pessoa (licença a confirmar)")
    ap.add_argument("--min-silence", type=float, default=0.45)
    ap.add_argument("--pad", type=float, default=0.12, help="cut: folga mantida em volta da fala (s)")
    ap.add_argument("--noise", type=float, default=-35, help="cut: limiar de silêncio em dB")
    ap.add_argument("--fillers", help="cut: palavras extras a cortar quando isoladas (ex.: tipo,né)")
    ap.add_argument("--zoom", type=float, default=1.15, help="cut: zoom alternado entre trechos (punch-in)")
    ap.add_argument("--no-zoom", action="store_true")
    ap.add_argument("--max-shot", type=float, default=None,
                    help="cut: divide trechos sem pausa em planos de ~N s com zoom alternado "
                         "(padrão 2.6 no vertical, 6 no 16:9; 0 desliga)")
    ap.add_argument("--reset", action="store_true", help="cut: descarta inserções, enquadramento e descartes do corte anterior")
    ap.add_argument("--crf", type=int, default=18)
    a = ap.parse_args()
    proj = project_dir(a.project)
    m = load_manifest(proj)
    if a.cmd == "import":
        if not a.video:
            sys.exit("Informe o arquivo de vídeo: footage.py import <projeto> <video>")
        cmd_import(proj, m, a)
    else:
        {"cut": cmd_cut, "frames": cmd_frames, "render": cmd_render}[a.cmd](proj, m, a)


if __name__ == "__main__":
    main()
