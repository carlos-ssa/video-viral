"""Mixa, legenda, normaliza e exporta o vídeo no tamanho do projeto (9:16, 16:9, 1:1 ou 4:5); depois verifica.

Uso:
  python scripts/deliver.py <projeto> --video render/master.mp4
      [--voice audio/voice.wav] [--music audio/music.wav] [--music-db -16]
      [--captions captions/captions.ass | --no-captions] [--no-music] [--mute-video-audio]
      [--allow-noncommercial | --draft] [--crf 18]

Por padrão usa audio/voice.wav, audio/music.wav e captions/captions.ass quando existem; o áudio do próprio
vídeo (sua gravação) entra na mixagem, a não ser com --mute-video-audio.
Confere duração e formato de tela por plataforma (tiktok, reels, shorts, kwai, youtube, feed) e, para YouTube,
capítulos em publish.chapters ([{"start": "00:00", "title": "..."}]) e a miniatura em publish.thumbnail.
Grava out/<slug>.mp4, out/<slug>_prancha.jpg (quadros com a área segura) e out/report.md.
Em vídeo monetizado, um ativo bloqueia a entrega se a licença for não comercial, se 'commercial_ok' não for true
(licença desconhecida também bloqueia) ou se a licença disser que o uso comercial não foi verificado.
--draft entrega mesmo assim como out/<slug>_rascunho.mp4, marcado para não publicar, para o usuário ver o resultado
enquanto o ativo é trocado.
Sai com código 1 se alguma checagem falhar e 2 se uma licença bloquear a entrega.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import PLATFORMS, ffprobe_json, load_manifest, need, project_dir, run, safe_area  # noqa: E402

TARGET_LUFS, LUFS_TOL, MAX_TP = -14.0, 1.0, -1.0
THUMBNAIL_SIZE = (1280, 720)
THUMBNAIL_CODECS = {"png", "mjpeg", "webp", "bmp", "tiff"}
THUMBNAIL_FORMATS = {"image2", "png_pipe", "jpeg_pipe", "webp_pipe", "bmp_pipe", "tiff_pipe"}
NONCOMMERCIAL = re.compile(r"\bNC\b|non-?commercial|não comercial|nao comercial", re.I)
UNVERIFIED = re.compile(r"n[ãa]o verificad|unverified|unknown|desconhecid|a confirmar|\?", re.I)


def rel(proj, p):
    if p is None:
        return None
    q = Path(p)
    return q if q.is_absolute() else (proj / q)


def license_blockers(m):
    bad = []
    for a in m.get("assets", []):
        lic = str(a.get("license", ""))
        if not lic.strip() or a.get("commercial_ok") is not True or NONCOMMERCIAL.search(lic) or UNVERIFIED.search(lic):
            bad.append(a)
    return bad


def stream(info, kind):
    return next((s for s in info["streams"] if s.get("codec_type") == kind), None)


def fps_of(s):
    num, den = (s.get("avg_frame_rate") or s.get("r_frame_rate") or "0/1").split("/")
    return float(num) / float(den) if float(den) else 0.0


def audio_graph(inputs, music_db):
    """inputs: dict com índices de 'voice', 'music', 'video_audio' (ou None). Devolve (filtros, rótulo)."""
    fmt = "aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo"
    f, mix = [], []
    v, mu, va, sfx = inputs.get("voice"), inputs.get("music"), inputs.get("video_audio"), inputs.get("sfx")
    if v is not None and mu is not None:
        f.append(f"[{v}:a]{fmt},asplit=2[vo][sc]")
        f.append(f"[{mu}:a]{fmt},volume={music_db}dB[mu]")
        f.append("[mu][sc]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[duck]")
        mix += ["[vo]", "[duck]"]
    elif v is not None:
        f.append(f"[{v}:a]{fmt}[vo]")
        mix.append("[vo]")
    elif mu is not None:
        f.append(f"[{mu}:a]{fmt}[mu]")
        mix.append("[mu]")
    if va is not None:
        f.append(f"[{va}:a]{fmt}[va]")
        mix.append("[va]")
    if sfx is not None:
        f.append(f"[{sfx}:a]{fmt}[sfx]")
        mix.append("[sfx]")
    if not mix:
        return f, None
    if len(mix) == 1:
        f.append(f"{mix[0]}apad[mix]")
    else:
        f.append(f"{''.join(mix)}amix=inputs={len(mix)}:duration=longest:normalize=0,apad[mix]")
    return f, "[mix]"


def secs(v):
    """'1:02:03', '02:03' ou número -> segundos."""
    if isinstance(v, (int, float)):
        return float(v)
    t = 0.0
    for part in str(v).strip().split(":"):
        t = t * 60 + float(part)
    return t


def chapter_problems(chapters, dur):
    """Regras do YouTube para capítulos: o primeiro em 00:00, pelo menos 3, cada um com 10 s ou mais."""
    try:
        starts = [secs(c.get("start") if isinstance(c, dict) else str(c).split()[0]) for c in chapters]
    except ValueError:
        return ["tempo de capítulo ilegível"]
    probs = []
    if len(starts) < 3:
        probs.append(f"{len(starts)} capítulo(s); o YouTube exige 3 ou mais")
    if starts and starts[0] != 0:
        probs.append("o primeiro capítulo precisa começar em 00:00")
    bounds = starts + [dur]
    short = [i + 1 for i in range(len(starts)) if bounds[i + 1] - bounds[i] < 10]
    if short:
        probs.append(f"capítulo(s) {short} com menos de 10 s")
    if starts != sorted(starts):
        probs.append("capítulos fora de ordem")
    return probs


def fmt_t(t):
    t = int(round(t))
    return f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60:02d}:{t % 60:02d}"


def last_json(text):
    blocks = re.findall(r"\{[^{}]*\}", text, re.S)
    for b in reversed(blocks):
        try:
            return json.loads(b)
        except json.JSONDecodeError:
            continue
    return None


def thumbnail_problem(path):
    """Decodifica a imagem com ffprobe; extensão e existência não bastam."""
    result = run([need("ffprobe"), "-v", "error", "-count_frames", "-show_streams", "-show_format",
                  "-of", "json", str(path)], check=False)
    try:
        info = json.loads(result.stdout)
        video = stream(info, "video")
        formats = set(info.get("format", {}).get("format_name", "").split(","))
        if (result.returncode or result.stderr.strip() or not video
                or video.get("codec_name") not in THUMBNAIL_CODECS
                or not formats.intersection(THUMBNAIL_FORMATS)
                or video.get("nb_read_frames") != "1"):
            return "não é imagem estática decodificável; substitua por PNG/JPEG/WebP 1280x720"
        size = (video.get("width"), video.get("height"))
        if size != THUMBNAIL_SIZE:
            return f"dimensões {size[0]}x{size[1]}; exporte a miniatura em 1280x720"
    except (ValueError, KeyError, TypeError):
        return "imagem ilegível; substitua por PNG/JPEG/WebP 1280x720"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--video", required=True)
    ap.add_argument("--voice")
    ap.add_argument("--music")
    ap.add_argument("--sfx", help="faixa de efeitos; padrão audio/sound-design.wav")
    ap.add_argument("--music-db", type=float)
    ap.add_argument("--captions")
    ap.add_argument("--no-captions", action="store_true")
    ap.add_argument("--no-music", action="store_true")
    ap.add_argument("--mute-video-audio", action="store_true")
    ap.add_argument("--allow-noncommercial", action="store_true", help="só para vídeo não monetizado")
    ap.add_argument("--draft", action="store_true", help="gera rascunho mesmo com licença bloqueando; não publicar")
    ap.add_argument("--crf", type=int, default=18)
    a = ap.parse_args()

    ff = need("ffmpeg")
    proj = project_dir(a.project)
    m = load_manifest(proj)
    slug = m.get("slug") or proj.name
    W, H = m.get("size", [1080, 1920])
    SAFE = safe_area(W, H)
    aspect = m.get("aspect") or ("9:16" if H > W * 1.5 else "16:9" if W > H * 1.5 else "1:1" if W == H else "4:5")
    fps = int(m.get("fps", 30))
    out_dir = proj / "out"
    out_dir.mkdir(exist_ok=True)

    blockers = license_blockers(m)
    if a.allow_noncommercial and m.get("monetized", True):
        ap.error("--allow-noncommercial só é permitido em projeto com monetized: false; use --draft para prévia.")
    draft = a.draft and m.get("monetized", True) and bool(blockers)
    if m.get("monetized", True) and blockers and not (a.allow_noncommercial or a.draft):
        print("Entrega bloqueada: vídeo monetizado com ativos sem licença comercial confirmada:")
        for b in blockers:
            print(f"  - {b.get('path')} ({b.get('source')}, {b.get('license')}, commercial_ok={b.get('commercial_ok')})")
        print("Troque os ativos. Para o usuário ver o resultado antes disso, use --draft (rascunho que não deve ser publicado).")
        sys.exit(2)

    video = rel(proj, a.video)
    if not video.exists():
        sys.exit(f"Vídeo não encontrado: {video}")
    vinfo = ffprobe_json(video)
    if not stream(vinfo, "video"):
        sys.exit(f"{video} não tem faixa de vídeo.")
    vdur = float(vinfo["format"]["duration"])

    voice = rel(proj, a.voice) if a.voice else (proj / "audio" / "voice.wav")
    voice = voice if voice.exists() else None
    music = None
    if not a.no_music:
        music = rel(proj, a.music) if a.music else (proj / "audio" / "music.wav")
        music = music if music.exists() else None
    caps = None
    sfx = rel(proj, a.sfx) if a.sfx else proj / "audio" / "sound-design.wav"
    sfx = sfx if sfx.exists() else None
    if not a.no_captions:
        caps = rel(proj, a.captions) if a.captions else (proj / "captions" / "captions.ass")
        caps = caps if caps.exists() else None
    music_db = a.music_db if a.music_db is not None else float(m.get("music", {}).get("gain_db", -16))

    in_args, idx = ["-i", str(video)], {}
    n = 1
    for key, path in (("voice", voice), ("music", music), ("sfx", sfx)):
        if path:
            in_args += ["-i", str(path)]
            idx[key] = n
            n += 1
    if stream(vinfo, "audio") and not a.mute_video_audio:
        idx["video_audio"] = 0
    afilters, alabel = audio_graph(idx, music_db)
    if alabel is None:
        in_args += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        afilters, alabel = [f"[{n}:a]anull[mix]"], "[mix]"

    vf = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps={fps}")
    if caps:
        vf += f",subtitles={caps.name}"
        fonts = proj / "assets" / "fonts"
        if fonts.is_dir():  # fontes do estilo (direction.md); caminho relativo evita escapar "C:" no Windows
            vf += f":fontsdir={os.path.relpath(fonts, caps.parent).replace(os.sep, '/')}"
    vf += "[v]"
    cwd = str(caps.parent) if caps else None

    # Passo 1: medir volume da mixagem
    print("Medindo volume...")
    g1 = ";".join(afilters + [f"{alabel}loudnorm=I={TARGET_LUFS}:TP=-1.5:LRA=11:print_format=json[ln]"])
    r1 = run([ff, "-hide_banner", "-nostats", *in_args, "-filter_complex", g1, "-map", "[ln]",
              "-t", f"{vdur:.3f}", "-f", "null", "-"], cwd=cwd)
    meas = last_json(r1.stderr)
    if not meas or "input_i" not in meas:
        sys.exit("Não consegui ler a medição do loudnorm.")
    if float(meas["input_i"]) < -60:
        ln = "anull"  # áudio silencioso: nada a normalizar
    else:
        ln = (f"loudnorm=I={TARGET_LUFS}:TP=-1.5:LRA=11:measured_I={meas['input_i']}:"
              f"measured_TP={meas['input_tp']}:measured_LRA={meas['input_lra']}:"
              f"measured_thresh={meas['input_thresh']}:offset={meas['target_offset']}:linear=true")

    # Passo 2: codificar
    out = out_dir / (f"{slug}_rascunho.mp4" if draft else f"{slug}.mp4")
    print(f"Codificando {out.name}...")
    g2 = ";".join([vf] + afilters + [f"{alabel}{ln},aresample=48000[a]"])
    run([ff, "-y", "-hide_banner", "-nostats", *in_args, "-filter_complex", g2, "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-preset", "medium",
         "-crf", str(a.crf), "-maxrate", "15M", "-bufsize", "30M", "-g", str(fps * 2),
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart",
         "-t", f"{vdur:.3f}", str(out)], cwd=cwd)

    # Verificação
    info = ffprobe_json(out)
    vs, as_ = stream(info, "video"), stream(info, "audio")
    dur = float(info["format"]["duration"])
    r3 = run([ff, "-hide_banner", "-nostats", "-i", str(out), "-vf", "blackdetect=d=0.25:pix_th=0.10",
              "-af", "ebur128=peak=true", "-f", "null", "-"])
    err = r3.stderr
    lufs = re.findall(r"I:\s+(-?[\d.]+|-inf) LUFS", err)
    peak = re.findall(r"True peak:\s+Peak:\s+(-?[\d.]+|-inf) dBFS", err, re.S)
    lufs = float(lufs[-1]) if lufs and lufs[-1] != "-inf" else None
    peak = float(peak[-1]) if peak and peak[-1] != "-inf" else None
    blacks = [(float(s), float(e)) for s, e in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", err)]

    checks = []  # (ok, nível, texto)

    def chk(ok, text, level="falha"):
        checks.append((bool(ok), level, text))

    chk(vs and vs.get("width") == W and vs.get("height") == H, f"Resolução {vs.get('width')}x{vs.get('height')} (esperado {W}x{H})")
    chk(vs and abs(fps_of(vs) - fps) < 0.05, f"Quadros por segundo {fps_of(vs):.2f} (esperado {fps})")
    chk(vs and vs.get("codec_name") == "h264" and vs.get("pix_fmt") == "yuv420p", f"Vídeo {vs.get('codec_name')} {vs.get('pix_fmt')}")
    chk(as_ and as_.get("codec_name") == "aac" and as_.get("sample_rate") == "48000", "Áudio AAC 48 kHz")
    for p in m.get("platforms", ["tiktok", "reels", "shorts"]):
        spec = PLATFORMS.get(p)
        if not spec:
            continue
        chk(dur <= spec["limit"], f"Duração {dur:.1f} s (limite de {p}: {spec['limit']} s)")
        chk(aspect in spec["aspects"], f"Formato {aspect} adequado a {p} ({' ou '.join(spec['aspects'])})", "aviso")
    tgt = m.get("target_seconds")
    if tgt:
        chk(dur <= tgt * 1.25, f"Duração {dur:.1f} s " + ("perto do" if dur <= tgt * 1.25 else "bem acima do") + f" alvo de {tgt} s", "aviso")
    chk(lufs is not None and abs(lufs - TARGET_LUFS) <= LUFS_TOL, f"Volume {lufs} LUFS (alvo {TARGET_LUFS} ± {LUFS_TOL})")
    chk(peak is not None and peak <= MAX_TP, f"Pico real {peak} dBTP (máximo {MAX_TP})")
    chk(not any(s < 0.05 for s, _ in blacks), "Primeiro quadro não é preto (gancho visível)")
    long_black = [(s, e) for s, e in blacks if s >= 0.05 and e - s > 0.5]
    chk(not long_black, "Sem trechos pretos acima de 0,5 s" + (f": {long_black}" if long_black else ""), "aviso")
    rec_audio = bool(stream(vinfo, "audio")) and not a.mute_video_audio
    if voice:
        vdur_voice = float(ffprobe_json(voice)["format"]["duration"])
        chk(vdur_voice <= dur + 0.3, f"Narração ({vdur_voice:.1f} s) cabe no vídeo ({dur:.1f} s)")
        chk(dur - vdur_voice <= 2.0, f"Sem silêncio longo no fim (vídeo {dur - vdur_voice:.1f} s mais longo que a voz)", "aviso")
    elif rec_audio:
        chk(True, "Áudio da gravação (sem narração separada)")
    else:
        chk(False, "Sem narração (audio/voice.wav ausente) nem áudio no vídeo", "aviso")
    chk(caps is not None or a.no_captions, "Legendas queimadas" if caps else "Sem arquivo de legendas", "aviso")
    if draft:
        chk(False, f"RASCUNHO: {len(blockers)} ativo(s) sem licença comercial confirmada; não publicar antes de trocar", "aviso")
    elif blockers:
        chk(not m.get("monetized", True), f"{len(blockers)} ativo(s) não comercial(is) liberado(s) com --allow-noncommercial", "aviso")
    pub = m.get("publish", {})
    if "youtube" in m.get("platforms", []):
        chaps = pub.get("chapters") or []
        if dur >= 180:
            probs = chapter_problems(chaps, dur) if chaps else ["sem capítulos em publish.chapters"]
            chk(not probs, "Capítulos do YouTube" + (f": {'; '.join(probs)}" if probs else " válidos"), "aviso")
        thumb = rel(proj, pub["thumbnail"]) if pub.get("thumbnail") else None
        if thumb is None or not thumb.is_file():
            chk(False, "Miniatura ausente: exporte imagem 1280x720 e registre em publish.thumbnail", "aviso")
        else:
            problem = thumbnail_problem(thumb)
            chk(problem is None, "Miniatura 1280x720 em publish.thumbnail" + (f": {problem}" if problem else " válida"))
    if m.get("format") in ("produto", "ugc") or pub.get("ad_disclosure"):
        chk(bool(pub.get("ad_disclosure")), "Publicidade sinalizada (publish.ad_disclosure)", "aviso")
    unl = [x.get("path") for x in m.get("assets", []) if not x.get("license")]
    chk(not unl, "Todos os ativos têm licença registrada" + (f" (faltam: {', '.join(unl)})" if unl else ""), "aviso")

    # Prancha: início, 1 s, meio, fim, com a área segura marcada
    sheet = out_dir / f"{slug}_prancha.jpg"
    times = [0.0, min(1.0, dur / 4), dur / 2, max(dur - 0.5, 0.0)]
    s = 0.25 if H > W else 0.2
    box = (f"drawbox=x={SAFE['left'] * s:.0f}:y={SAFE['top'] * s:.0f}:"
           f"w={(W - SAFE['left'] - SAFE['right']) * s:.0f}:h={(H - SAFE['top'] - SAFE['bottom']) * s:.0f}:color=red@0.7:t=2")
    sargs, sf = [ff, "-y", "-hide_banner"], []
    for i, t in enumerate(times):
        sargs += ["-ss", f"{t:.3f}", "-i", str(out)]
        sf.append(f"[{i}:v]scale={int(W * s)}:{int(H * s)},setsar=1,{box}[f{i}]")
    sf.append("".join(f"[f{i}]" for i in range(len(times))) + f"hstack=inputs={len(times)}[o]")
    run(sargs + ["-filter_complex", ";".join(sf), "-map", "[o]", "-frames:v", "1", "-q:v", "3", str(sheet)])

    fails = [c for c in checks if not c[0] and c[1] == "falha"]
    warns = [c for c in checks if not c[0] and c[1] == "aviso"]
    lines = [f"# {'RASCUNHO, não publicar' if draft else 'Entrega'}: {m.get('title') or slug}", "",
             f"- Arquivo: `out/{out.name}` ({out.stat().st_size / 1e6:.1f} MB, {dur:.1f} s)",
             f"- Prancha: `out/{sheet.name}` (início, 1 s, meio, fim; retângulo vermelho = área segura)",
             f"- Fontes: vídeo `{video.name}`, voz `{voice.name if voice else '-'}`, "
             f"trilha `{music.name if music else '-'}` ({music_db} dB), legendas `{caps.name if caps else '-'}`",
             f"- Efeitos: `{sfx.name if sfx else '-'}`",
             f"- Resultado: {'APROVADO' if not fails else 'REPROVADO'} ({len(fails)} falha(s), {len(warns)} aviso(s))",
             "", "| Checagem | Resultado |", "|---|---|"]
    for ok, level, text in checks:
        lines.append(f"| {text} | {'ok' if ok else level} |")
    lines += ["", "## Ativos", "", "| Caminho | Origem | Licença | Comercial |", "|---|---|---|---|"]
    for x in m.get("assets", []):
        lines.append(f"| {x.get('path')} | {x.get('source')} | {x.get('license')} | {'sim' if x.get('commercial_ok') else 'não'} |")
    lines += ["", "## Publicação", ""]
    if pub.get("title"):
        lines.append(f"- Título: {pub['title']}")
    lines.append(f"- Legenda: {pub.get('caption', '')}")
    if pub.get("description"):
        lines.append(f"- Descrição: {pub['description']}")
    lines += [
              f"- Hashtags: {' '.join(pub.get('hashtags', []))}",
              f"- Rótulo de IA: {'ativar ao postar' if pub.get('ai_label') else 'não necessário (confira references/platforms.md)'}",
              f"- Publicidade: {'marcar como conteúdo pago/parceria ao postar' if pub.get('ad_disclosure') else 'não'}"]
    if pub.get("chapters"):
        lines += ["", "Capítulos (cole na descrição do YouTube):", ""]
        for c in pub["chapters"]:
            if isinstance(c, dict):
                lines.append(f"    {fmt_t(secs(c.get('start', 0)))} {c.get('title', '')}")
            else:
                lines.append(f"    {c}")
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    from _common import file_sha256, manifest_sha256
    receipt = {"schema": 1, "video": str(out.resolve()), "video_sha256": file_sha256(out),
               "manifest_sha256": manifest_sha256(m),
               "approved": not fails and not draft, "draft": draft, "duration": dur,
               "lufs": lufs, "true_peak_dbtp": peak,
               "checks": [{"ok": ok, "level": level, "message": text} for ok, level, text in checks]}
    receipt_path = out_dir / "delivery.json"
    temporary = receipt_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(receipt_path)

    for ok, level, text in checks:
        print(f"[{'ok' if ok else level}] {text}")
    print(f"\n{out}\n{sheet}\n{out_dir / 'report.md'}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
