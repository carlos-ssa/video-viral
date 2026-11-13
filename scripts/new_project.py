"""Cria a pasta de um vídeo e o video.json a partir do modelo.

Uso: python scripts/new_project.py <slug> --title "Título" [--format narrado] [--aspect 9:16]
     [--dir pasta] [--platforms tiktok,reels,shorts,kwai] [--not-monetized] [--seconds 40]
     [--voice pt-BR-ThalitaMultilingualNeural] [--fps 30]

Formatos: narrado (canal dark, narração + visual gerado), gravacao (sua gravação editada),
corte (trecho de vídeo longo), produto, ugc, storytelling, musica, avatar.
Sem --platforms, o formato de tela escolhe: 9:16 -> tiktok,reels,shorts,kwai; 16:9 -> youtube;
1:1 e 4:5 -> feed.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import ASPECTS, FORMATS, MANIFEST, PLATFORMS, TEMPLATE, manifest_path, save_manifest  # noqa: E402
from voice import default_voice  # noqa: E402

FOLDERS = ["research", "source", "edit", "audio/scenes", "audio/sfx", "captions", "scenes", "assets", "render", "out"]
DEFAULT_PLATFORMS = {"9:16": "tiktok,reels,shorts,kwai", "16:9": "youtube", "1:1": "feed", "4:5": "feed"}
CAPTION_SIZE = {"9:16": 88, "16:9": 64}
VOICE_FORMATS = {"narrado", "storytelling", "produto"}  # formatos em que a voz sintética é o padrão


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--title", default="")
    ap.add_argument("--format", default="narrado", choices=FORMATS)
    ap.add_argument("--aspect", default="9:16", choices=list(ASPECTS))
    ap.add_argument("--dir", default=".", help="pasta onde o projeto será criado")
    ap.add_argument("--platforms", default=None)
    ap.add_argument("--not-monetized", action="store_true")
    ap.add_argument("--seconds", type=int, default=None, help="duração alvo (padrão: 40 em vertical, 480 em 16:9)")
    ap.add_argument("--voice", default=None)
    ap.add_argument("--fps", type=int, default=30, choices=[24, 25, 30, 50, 60])
    ap.add_argument("--lang", default="pt-BR")
    ap.add_argument("--objective", choices=["alcance", "consideracao", "conversao", "entretenimento"])
    ap.add_argument("--audience", default="")
    ap.add_argument("--offer", default="")
    a = ap.parse_args()

    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", a.slug):
        sys.exit("Use um slug com letras minúsculas, números e hífens (ex.: cubo-em-codigo).")
    plats = [p.strip() for p in (a.platforms or DEFAULT_PLATFORMS[a.aspect]).split(",") if p.strip()]
    bad = set(plats) - set(PLATFORMS)
    if bad:
        sys.exit(f"Plataformas desconhecidas: {', '.join(sorted(bad))}. Use: {', '.join(PLATFORMS)}.")
    for p in plats:
        if a.aspect not in PLATFORMS[p]["aspects"]:
            print(f"Aviso: {p} espera {' ou '.join(PLATFORMS[p]['aspects'])}, e o projeto é {a.aspect}.")

    try:
        selected_voice = a.voice or default_voice(a.lang)
    except ValueError as exc:
        if a.format in ("gravacao", "corte", "ugc", "musica"):
            selected_voice = None
        else:
            ap.error(str(exc))

    proj = Path(a.dir).expanduser().resolve() / a.slug
    if manifest_path(proj).exists():
        sys.exit(f"Já existe {manifest_path(proj)}; não sobrescrevo.")
    for f in FOLDERS:
        (proj / f).mkdir(parents=True, exist_ok=True)

    m = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    seconds = a.seconds or (480 if a.aspect == "16:9" else 40)
    m.update(slug=a.slug, title=a.title, format=a.format, aspect=a.aspect, lang=a.lang, platforms=plats,
             monetized=not a.not_monetized, target_seconds=seconds, fps=a.fps, size=list(ASPECTS[a.aspect]))
    m["captions"]["size"] = CAPTION_SIZE.get(a.aspect, 72)
    m["brief"].update(objective=a.objective or ("conversao" if a.format in ("produto", "ugc")
                                              else "entretenimento" if a.format == "musica" else "alcance"),
                      audience=a.audience, offer=a.offer)
    if selected_voice:
        m["voice"]["voice"] = selected_voice
    if a.format not in VOICE_FORMATS:
        m["voice"]["engine"] = "gravacao" if a.format in ("gravacao", "corte", "ugc") else m["voice"]["engine"]
    if a.format in ("gravacao", "corte", "ugc", "musica"):
        m["scenes"] = []
    if a.format == "musica":
        m["voice"]["engine"] = "none"
    if a.format == "musica":
        m["music"]["engine"] = "ace-step-1.5"
    save_manifest(proj, m)
    print(f"Projeto criado: {proj} ({a.format}, {a.aspect}, {', '.join(plats)})")
    if a.format in ("gravacao", "corte", "ugc"):
        print(f"Próximo passo: python scripts/footage.py import {proj} <seu-video.mp4> (references/formats/gravacao.md).")
    else:
        print(f"Próximo passo: escreva hook e scenes no {MANIFEST} (references/writing.md).")


if __name__ == "__main__":
    main()
