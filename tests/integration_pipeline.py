"""Smoke test com FFmpeg real e sem modelos/rede. Não avalia qualidade estética.

python tests/integration_pipeline.py --output <pasta-nova-de-validacao>
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--node-root", type=Path, help="ativa integração real Tone.js → mix de entrega")
    args = ap.parse_args()
    output = args.output.resolve()
    if output.exists():
        ap.error("Use uma pasta nova para não sobrescrever validações.")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        ap.error("FFmpeg e ffprobe precisam estar instalados; este teste não instala nada.")
    output.mkdir(parents=True)
    env = {**os.environ, "VIDEO_VIRAL_NO_INSTALL": "1"}
    results = []

    def run(name, command, expected=0):
        result = subprocess.run(list(map(str, command)), cwd=ROOT, env=env, capture_output=True,
                                text=True, encoding="utf-8", errors="replace", timeout=180)
        (output / (name + ".log")).write_text(result.stdout + result.stderr, encoding="utf-8")
        results.append({"step": name, "exit_code": result.returncode, "expected": expected})
        (output / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
        if result.returncode != expected:
            raise RuntimeError(f"{name}: código {result.returncode}, esperado {expected}; veja {output / (name + '.log')}")

    py = sys.executable
    scripts = ROOT / "scripts"
    run("create", [py, scripts / "new_project.py", "recording", "--format", "gravacao", "--seconds", 14,
                   "--dir", output])
    proj = output / "recording"
    manifest = json.loads((proj / "video.json").read_text(encoding="utf-8"))
    manifest.update(size=[360, 640])
    manifest["captions"]["size"] = 28
    manifest["title"] = "Validação técnica sintética — não é peça final"
    (proj / "video.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    sample = ROOT / "evals/editar-gravacao-propria/files"
    run("import", [py, scripts / "footage.py", "import", proj, sample / "gravacao.mp4", "--to", "14"])
    run("captions_import", [py, scripts / "captions.py", "import", proj, "--file", sample / "gravacao.srt"])
    run("cut", [py, scripts / "footage.py", "cut", proj, "--no-zoom"])
    run("render", [py, scripts / "footage.py", "render", proj])
    # A small moving composition exercises the final-render path; it is not a cinematic quality sample.
    run("compose", ["ffmpeg", "-y", "-v", "error", "-i", proj / "render/master.mp4",
                    "-vf", "scale=380:676,crop=360:640:x='10+8*sin(t)':y=18", "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", proj / "render/final.mp4"])
    run("captions_ass", [py, scripts / "captions.py", "ass", proj])
    if args.node_root:
        spec = {"duration": 14, "seed": 7, "events": [
            {"type": "whoosh", "at": 1, "duration": 0.4, "gainDb": -18},
            {"type": "pop", "at": 3, "duration": 0.2, "gainDb": -22}]}
        (proj / "edit/sound.json").write_text(json.dumps(spec), encoding="utf-8")
        run("tone_sound", ["node", scripts / "sound.mjs", proj, "--spec", "edit/sound.json",
                           "--node-root", args.node_root])
        m = json.loads((proj / "video.json").read_text(encoding="utf-8"))
        m["assets"].append({"path": "audio/sound-design.wav", "kind": "sfx",
                            "source": "procedural Tone.js test signal", "license": "original test signal", "commercial_ok": True})
        (proj / "video.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
    run("deliver", [py, scripts / "deliver.py", proj, "--video", "render/final.mp4"])
    # review may find a real blocker in the fixture; allow it and inspect its recorded metrics.
    result = subprocess.run([py, str(scripts / "review.py"), str(proj)], cwd=ROOT, env=env,
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    (output / "review.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode not in (0, 1):
        raise RuntimeError("Análise do vídeo falhou; veja review.log")
    metrics = json.loads((proj / "review/r01/metrics.json").read_text(encoding="utf-8"))
    results.append({"step": "review", "exit_code": result.returncode, "blockers": metrics["blockers"]})
    run("pending_evidence_rejected", [py, scripts / "review.py", proj, "--verdict"], expected=2)
    receipt = json.loads((proj / "out/delivery.json").read_text(encoding="utf-8"))
    assert receipt["approved"] is True and receipt["draft"] is False
    assert receipt["video_sha256"] == metrics["video_sha256"]
    if args.node_root:
        assert 'sound-design.wav' in (proj / "out/report.md").read_text(encoding="utf-8")

    csv_path = output / "synthetic-trends.csv"
    csv_path.write_text("Week,barbearia: (Brasil)\n2026-11-01,100\n2026-11-08,<1\n", encoding="utf-8")
    run("trends_import", [py, scripts / "trends.py", proj, "--terms", "barbearia", "--csv", csv_path])
    run("changed_brief_rejected", [py, scripts / "review.py", proj, "--verdict"], expected=2)

    run("create_music", [py, scripts / "new_project.py", "instrumental", "--format", "musica",
                         "--seconds", 4, "--dir", output])
    musical = output / "instrumental"
    musical_manifest = json.loads((musical / "video.json").read_text(encoding="utf-8"))
    musical_manifest["size"] = [360, 640]
    (musical / "video.json").write_text(json.dumps(musical_manifest), encoding="utf-8")
    run("generate_music_fixture", ["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i",
                                  "testsrc2=size=360x640:rate=30:duration=4", "-f", "lavfi", "-i",
                                  "sine=frequency=440:sample_rate=48000:duration=3,adelay=1000",
                                  "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                                  "-shortest", musical / "render/master.mp4"])
    run("deliver_music", [py, scripts / "deliver.py", musical, "--video", "render/master.mp4",
                          "--no-captions", "--no-music"])
    run("review_music", [py, scripts / "review.py", musical])
    musical_metrics = json.loads((musical / "review/r01/metrics.json").read_text(encoding="utf-8"))
    assert "Sincronismo musical" in musical_metrics["rubric"]
    assert not any("fala" in problem.casefold() for problem in musical_metrics["blockers"])

    (output / "results.json").write_text(json.dumps({"steps": results, "technical_smoke_passed": True,
        "aesthetic_quality_assessed": False, "live_trends_data_fetched": False,
        "models_installed": False}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Smoke técnico aprovado; não é aprovação estética. Resultados: {output / 'results.json'}")


if __name__ == "__main__":
    main()
