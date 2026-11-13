"""Cortes de vídeo longo: sugere os trechos com mais chance de funcionar sozinhos e cria um projeto por corte.

Uso:
  python scripts/clips.py suggest <projeto-longo> [--min 20] [--max 60] [--top 10]
  python scripts/clips.py make <projeto-longo> (--rank 1 | --from 1:23 --to 2:05) --slug nome
                          [--aspect 9:16] [--dir pasta]

O projeto longo precisa de footage.py import e de captions/source_words.json (captions.py transcribe ou import).
'suggest' monta janelas de frases inteiras e dá nota pelo gancho da primeira frase (pergunta, número, palavra
de impacto, começo que não depende do contexto), pela densidade de fala e pelo fechamento. Grava edit/clips.md
e edit/clips.json. A nota é um filtro: leia os 3–5 primeiros e escolha pelo conteúdo.
'make' cria um projeto irmão com formato "corte", importa só o trecho da gravação e leva as palavras junto (sem
transcrever de novo). Depois siga o fluxo da gravação: footage.py cut, frames, render.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_manifest, project_dir, save_manifest  # noqa: E402
from footage import FILLER_RE, norm  # noqa: E402

HERE = Path(__file__).resolve().parent
HOOK_WORDS = ["por que", "porque ninguém", "como", "segredo", "erro", "errado", "ninguém", "nunca", "pare", "cuidado",
              "verdade", "mito", "descobri", "o que", "sabia", "mais importante", "o problema", "ninguém te",
              "pior", "melhor", "dica", "truque", "atenção", "olha", "imagina"]
WEAK_START = {"e", "mas", "então", "porque", "isso", "aí", "também", "daí", "ou", "né", "que", "ele", "ela", "eles",
              "elas", "esse", "essa", "isso", "lá", "depois"}
NUM = re.compile(r"\d|\b(um|dois|três|quatro|cinco|seis|sete|oito|nove|dez|cem|mil|milhão|milhões|metade|dobro)\b",
                 re.I)


def fmt(t):
    t = int(round(t))
    return f"{t // 3600}:{t % 3600 // 60:02d}:{t % 60:02d}" if t >= 3600 else f"{t // 60}:{t % 60:02d}"


def secs(v):
    t = 0.0
    for part in str(v).strip().split(":"):
        t = t * 60 + float(part)
    return t


def sentences(words):
    out, cur = [], []
    for w in words:
        if FILLER_RE.match(norm(w["w"])):
            continue  # vício não abre nem fecha frase; o cut remove depois
        cur.append(w)
        if re.search(r"[.!?…]$", w["w"]):
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return [{"start": s[0]["start"], "end": s[-1]["end"], "text": " ".join(w["w"] for w in s), "n": len(s)}
            for s in out]


def score(win):
    first, last = win[0]["text"], win[-1]["text"]
    fl = first.lower()
    dur = win[-1]["end"] - win[0]["start"]
    words = sum(s["n"] for s in win)
    speech = sum(s["end"] - s["start"] for s in win)  # pausas entre frases saem no cut
    wps = words / max(speech, 0.1)
    pts, why = 0.0, []
    if "?" in first:
        pts += 2
        why.append("abre com pergunta")
    hw = [h for h in HOOK_WORDS if re.search(rf"\b{re.escape(h)}\b", fl)]
    if hw:
        pts += 1.5
        why.append(f"gancho: {', '.join(hw[:2])}")
    if NUM.search(first):
        pts += 1
        why.append("número no início")
    first_word = re.sub(r"[^\wáàâãéêíóôõúç]", "", fl.split()[0]) if fl.split() else ""
    if first_word in WEAK_START:
        pts -= 2
        why.append(f"começa com '{first_word}' (depende do contexto)")
    if re.search(r"[.!]$", last):
        pts += 0.5
    if "?" in last:
        pts -= 0.5
        why.append("termina em pergunta (sem fechamento)")
    if 2.3 <= wps <= 3.8:
        pts += 1
    elif wps < 1.8:
        pts -= 1
        why.append(f"fala lenta ({wps:.1f} palavras/s)")
    pts += min(sum(1 for s in win if NUM.search(s["text"])), 3) * 0.3
    if len(win[0]["text"].split()) <= 12:
        pts += 0.5
    return round(pts, 2), why, dur


def cmd_suggest(proj, m, a):
    p = proj / "captions" / "source_words.json"
    if not p.exists():
        sys.exit("Falta captions/source_words.json. Rode captions.py transcribe (ou import --file legenda.srt).")
    sents = sentences(json.loads(p.read_text(encoding="utf-8")))
    cands = []
    for i in range(len(sents)):
        for j in range(i, len(sents)):
            dur = sents[j]["end"] - sents[i]["start"]
            if dur > a.max:
                break
            if dur >= a.min:
                pts, why, d = score(sents[i:j + 1])
                cands.append({"from": round(sents[i]["start"], 2), "to": round(sents[j]["end"], 2),
                              "dur": round(d, 1), "score": pts, "why": why,
                              "hook": sents[i]["text"], "end": sents[j]["text"],
                              "_w": set(re.findall(r"\w{4,}", " ".join(x["text"] for x in sents[i:j + 1]).lower()))})
    cands.sort(key=lambda c: (-c["score"], c["dur"]))
    chosen = []
    for c in cands:
        # sem sobreposição e sem repetir o conteúdo de um corte já escolhido
        if all((c["to"] <= o["from"] or c["from"] >= o["to"])
               and len(c["_w"] & o["_w"]) < 0.6 * min(len(c["_w"]), len(o["_w"]) or 1) for o in chosen):
            chosen.append(c)
        if len(chosen) >= a.top:
            break
    off = float(((m.get("source") or {}).get("range") or [0])[0])
    for k, c in enumerate(chosen, 1):
        del c["_w"]
        c["rank"] = k
        c["file_from"], c["file_to"] = round(c["from"] + off, 2), round(c["to"] + off, 2)
    (proj / "edit").mkdir(exist_ok=True)
    (proj / "edit" / "clips.json").write_text(json.dumps(chosen, ensure_ascii=False, indent=1), encoding="utf-8")
    lines = [f"# Cortes sugeridos: {m.get('title') or proj.name}", "",
             f"{len(chosen)} trechos de {a.min}–{a.max} s sem sobreposição, por nota. Tempos no vídeo original.", "",
             "| # | Trecho | Dur. | Nota | Primeira frase | Última frase | Observações |", "|---|---|---|---|---|---|---|"]
    for c in chosen:
        lines.append(f"| {c['rank']} | {fmt(c['file_from'])}–{fmt(c['file_to'])} | {c['dur']} s | {c['score']} | "
                     f"{c['hook']} | {c['end']} | {'; '.join(c['why']) or '-'} |")
    lines += ["", "Crie um corte: `python scripts/clips.py make <projeto> --rank 1 --slug nome-do-corte`"]
    (proj / "edit" / "clips.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[4:4 + 2 + min(len(chosen), 5)]))
    print(f"\nedit/clips.md e edit/clips.json: {len(chosen)} sugestões")


def cmd_make(proj, m, a):
    src = m.get("source") or {}
    if not src.get("footage"):
        sys.exit("O projeto longo não tem gravação importada (footage.py import).")
    if a.rank:
        cj = proj / "edit" / "clips.json"
        if not cj.exists():
            sys.exit("Rode 'clips.py suggest' antes de usar --rank.")
        c = next((x for x in json.loads(cj.read_text(encoding="utf-8")) if x["rank"] == a.rank), None)
        if not c:
            sys.exit(f"Não há sugestão #{a.rank}.")
        t0, t1 = c["from"], c["to"]
    elif a.from_ and a.to:
        off = float((src.get("range") or [0])[0])
        t0, t1 = secs(a.from_) - off, secs(a.to) - off  # --from/--to no tempo do vídeo original
    else:
        sys.exit("Use --rank N ou --from/--to.")
    t0, t1 = max(t0 - 0.15, 0.0), t1 + 0.25  # folga para não cortar a primeira e a última sílaba
    off = float((src.get("range") or [0])[0])
    parent = Path(a.dir).resolve() if a.dir else proj.parent
    py = sys.executable
    r = subprocess.run([py, str(HERE / "new_project.py"), a.slug, "--title", a.title or a.slug, "--format", "corte",
                        "--aspect", a.aspect, "--dir", str(parent), "--lang", m.get("lang", "pt-BR"),
                        "--seconds", str(int(t1 - t0) + 1)] + ([] if m.get("monetized", True) else ["--not-monetized"]),
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        sys.exit(r.stderr or r.stdout)
    child = parent / a.slug
    own = next((x.get("commercial_ok") for x in m.get("assets", []) if x.get("path") == src["footage"]), True)
    r = subprocess.run([py, str(HERE / "footage.py"), "import", str(child), src["footage"],
                        "--from", f"{off + t0:.3f}", "--to", f"{off + t1:.3f}"]
                       + ([] if src.get("cleaned", True) else ["--no-clean"])
                       + ([] if own is True else ["--third-party"]),
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode:
        sys.exit(r.stderr or r.stdout)
    words = json.loads((proj / "captions" / "source_words.json").read_text(encoding="utf-8")) \
        if (proj / "captions" / "source_words.json").exists() else []
    sub = [{**w, "start": round(w["start"] - t0, 3), "end": round(w["end"] - t0, 3)}
           for w in words if w["start"] >= t0 and w["end"] <= t1]
    if sub:
        (child / "captions").mkdir(exist_ok=True)
        (child / "captions" / "source_words.json").write_text(json.dumps(sub, ensure_ascii=False, indent=1),
                                                              encoding="utf-8")
    cm = load_manifest(child)
    cm["source"]["parent"] = str(proj)
    if m.get("direction", {}).get("style"):
        cm["direction"] = m["direction"]
    save_manifest(child, cm)
    print(f"Corte criado: {child} ({fmt(off + t0)}–{fmt(off + t1)}, {t1 - t0:.1f} s, {len(sub)} palavras)")
    print(f"Próximo: footage.py cut {child}, depois frames e render.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["suggest", "make"])
    ap.add_argument("project")
    ap.add_argument("--min", type=float, default=20)
    ap.add_argument("--max", type=float, default=60)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--rank", type=int)
    ap.add_argument("--from", dest="from_")
    ap.add_argument("--to")
    ap.add_argument("--slug")
    ap.add_argument("--title")
    ap.add_argument("--aspect", default="9:16")
    ap.add_argument("--dir")
    a = ap.parse_args()
    proj = project_dir(a.project)
    m = load_manifest(proj)
    if a.cmd == "make" and not a.slug:
        sys.exit("Informe --slug para o projeto do corte.")
    (cmd_suggest if a.cmd == "suggest" else cmd_make)(proj, m, a)


if __name__ == "__main__":
    main()
