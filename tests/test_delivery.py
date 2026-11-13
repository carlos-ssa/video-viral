import contextlib
import io
import array
import math
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
    def test_invalid_chapter_times_cannot_pass_as_valid_chapters(self):
        for time in (float('nan'), float('inf'), -10, None, 'bad', ''):
            with self.subTest(time=time):
                self.assertTrue(deliver.chapter_problems([{'start': 0}, {'start': 10}, {'start': time}], 60))

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
class AudioMixTests(unittest.TestCase):
    def mix(self, sources, indices, gain):
        graph, label = deliver.audio_graph(indices, gain)
        command = ['ffmpeg', '-v', 'error']
        for source in sources:
            command += ['-f', 'lavfi', '-i', source]
        result = subprocess.run(command + ['-filter_complex', ';'.join(graph), '-map', label,
                                          '-t', '2', '-ar', '48000', '-ac', '2', '-f', 'f32le', '-'],
                                capture_output=True, check=True)
        pcm = array.array('f')
        pcm.frombytes(result.stdout)
        if sys.byteorder != 'little':
            pcm.byteswap()
        return pcm[::2]

    def test_music_gain_is_applied_without_separate_narration(self):
        source = ['sine=frequency=1000:sample_rate=48000:duration=2']
        loud = self.mix(source, {'music': 0}, 0)
        quiet = self.mix(source, {'music': 0}, -20)
        energy = lambda samples: math.sqrt(sum(v * v for v in samples) / len(samples))
        self.assertAlmostEqual(energy(quiet) / energy(loud), 0.1, places=4)

    def test_recorded_speech_ducks_music_without_external_voice_file(self):
        samples = self.mix([
            "aevalsrc='if(lt(t,1),0.5*sin(2*PI*440*t),0)':s=48000:d=2",
            'sine=frequency=1000:sample_rate=48000:duration=2'],
            {'video_audio': 0, 'music': 1}, -6)
        def music_amplitude(start):
            segment = samples[int(start * 48000):int((start + 0.1) * 48000)]
            return abs(sum(v * math.sin(2 * math.pi * 1000 * i / 48000)
                           for i, v in enumerate(segment))) * 2 / len(segment)
        self.assertLess(music_amplitude(0.5), music_amplitude(1.8) * 0.8)

    def test_music_continues_after_recorded_or_external_speech_eof(self):
        for key in ('video_audio', 'voice'):
            with self.subTest(speech=key):
                samples = self.mix(['sine=frequency=440:sample_rate=48000:duration=0.5',
                                    'sine=frequency=1000:sample_rate=48000:duration=2'],
                                   {key: 0, 'music': 1}, -6)
                tail = samples[int(1.5 * 48000):int(1.9 * 48000)]
                self.assertGreater(math.sqrt(sum(v * v for v in tail) / len(tail)), 0.02)

    def test_explicit_draft_never_receives_publishable_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'render').mkdir()
            source = root / 'render/master.mp4'
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=s=180x320:d=2:r=10',
                            '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000:duration=2',
                            '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(source)],
                           check=True, capture_output=True)
            save_manifest(root, {'slug': 'draft', 'size': [180, 320], 'fps': 10,
                                 'aspect': '9:16', 'platforms': [], 'monetized': False, 'assets': []})
            result = subprocess.run([sys.executable, str(Path(deliver.__file__)), str(root),
                                     '--video', 'render/master.mp4', '--no-captions', '--draft'],
                                    capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            import json
            receipt = json.loads((root / 'out/delivery.json').read_text(encoding='utf-8'))
            self.assertTrue(receipt['draft'])
            self.assertFalse(receipt['approved'])
            self.assertEqual(Path(receipt['video']).name, 'draft_rascunho.mp4')


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
