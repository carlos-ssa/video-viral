import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from _common import FORMATS, load_manifest, save_manifest


class ProjectTests(unittest.TestCase):
    def test_narration_defaults_follow_language_and_allow_voice_override(self):
        with tempfile.TemporaryDirectory() as folder:
            for lang, override, expected in (('pt-BR', None, 'pt-BR-ThalitaMultilingualNeural'),
                                              ('en-US', None, 'en-US-AvaMultilingualNeural'),
                                              ('en-GB', None, 'en-US-AvaMultilingualNeural'),
                                              ('en-US', 'en-US-GuyNeural', 'en-US-GuyNeural')):
                with self.subTest(lang=lang, override=override):
                    slug = 'voice-' + lang.lower() + ('-override' if override else '')
                    command = [sys.executable, str(ROOT / 'scripts/new_project.py'), slug,
                               '--dir', folder, '--lang', lang]
                    if override:
                        command += ['--voice', override]
                    result = subprocess.run(command, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(load_manifest(Path(folder) / slug)['voice'],
                                     {'engine': 'edge-tts', 'voice': expected, 'speed': 1.2})

    def test_all_formats_create_planning_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            for format_ in FORMATS:
                with self.subTest(format=format_):
                    result = subprocess.run([sys.executable, str(ROOT / "scripts/new_project.py"), format_,
                                             "--format", format_, "--dir", folder], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    m = load_manifest(Path(folder) / format_)
                    self.assertEqual(m["schema"], 3)
                    self.assertIn("proof", m["brief"])
                    self.assertEqual(m["research"]["sources"], [])
                    self.assertEqual(m["hook_candidates"], [])
                    self.assertEqual(m["tool_plan"], [])
                    if format_ == "musica":
                        self.assertEqual(m["voice"]["engine"], "none")

    def test_marketing_options_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            args = [sys.executable, str(ROOT / "scripts/new_project.py"), "campanha", "--format", "produto",
                    "--dir", folder, "--audience", "salões", "--offer", "agendamento", "--objective", "consideracao"]
            first = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            p = Path(folder) / "campanha"
            original = (p / "video.json").read_bytes()
            self.assertEqual(load_manifest(p)["brief"]["objective"], "consideracao")
            self.assertEqual(load_manifest(p)["brief"]["audience"], "salões")
            self.assertNotEqual(subprocess.run(args, capture_output=True).returncode, 0)
            self.assertEqual((p / "video.json").read_bytes(), original)

    def test_legacy_manifest_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            proj = Path(folder)
            (proj / "short.json").write_text(json.dumps({"schema": 1, "slug": "legacy"}), encoding="utf-8")
            m = load_manifest(proj)
            m["hook"] = "Preservado"
            save_manifest(proj, m)
            self.assertEqual(load_manifest(proj)["schema"], 1)
            self.assertFalse((proj / "video.json").exists())


if __name__ == "__main__":
    unittest.main()
