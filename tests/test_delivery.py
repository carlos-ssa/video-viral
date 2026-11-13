import contextlib
import io
from pathlib import Path
import sys
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from _common import save_manifest
import deliver


class DeliveryTests(unittest.TestCase):
    def test_sound_design_track_is_mixed_with_voice(self):
        graph, label = deliver.audio_graph({'voice': 1, 'sfx': 2}, -16)
        self.assertEqual(label, '[mix]')
        self.assertTrue(any('[2:a]' in entry and '[sfx]' in entry for entry in graph))
        self.assertTrue(any('[vo][sfx]amix' in entry for entry in graph))

    def test_noncommercial_flag_cannot_bypass_monetized_project(self):
        with tempfile.TemporaryDirectory() as folder:
            proj = Path(folder)
            save_manifest(proj, {"monetized": True, "assets": []})
            with patch.object(sys, "argv", ["deliver.py", str(proj), "--video", "unused.mp4", "--allow-noncommercial"]), \
                    patch.object(deliver, "need", return_value="ffmpeg"), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                deliver.main()
            self.assertEqual(raised.exception.code, 2)

    def test_missing_unknown_or_noncommercial_license_blocks(self):
        for license_ in ("", "CC-BY-NC 4.0", "uso comercial não verificado"):
            with self.subTest(license=license_):
                self.assertEqual(len(deliver.license_blockers({"assets": [{"license": license_, "commercial_ok": True}]})), 1)
        self.assertEqual(deliver.license_blockers({"assets": [{"license": "MIT", "commercial_ok": True}]}), [])


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'requer FFmpeg e ffprobe')
class ThumbnailTests(unittest.TestCase):
    def test_thumbnail_must_decode_as_one_image_with_expected_dimensions(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fake = root / 'fake.png'
            fake.write_text('1280x720 não é imagem', encoding='utf-8')
            self.assertIsNotNone(deliver.thumbnail_problem(fake))
            for name, size in [('valid.png', '1280x720'), ('wrong.jpg', '640x360')]:
                path = root / name
                subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', f'color=blue:s={size}',
                                '-frames:v', '1', str(path)], check=True, capture_output=True)
                problem = deliver.thumbnail_problem(path)
                if name == 'valid.png':
                    self.assertIsNone(problem)
                else:
                    self.assertIn('640x360', problem)
            movie = root / 'movie.mp4'
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=blue:s=1280x720:d=0.2',
                            '-c:v', 'libx264', str(movie)], check=True, capture_output=True)
            renamed = root / 'movie.jpg'
            movie.rename(renamed)
            self.assertIsNotNone(deliver.thumbnail_problem(renamed))


if __name__ == "__main__":
    unittest.main()
