from argparse import Namespace
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import footage
from _common import ffprobe_json, file_sha256, run, save_manifest


class FootageTests(unittest.TestCase):
    def test_time_parser_rejects_nonfinite_negative_and_invalid_clock(self):
        self.assertEqual(footage.secs('1:02.5'), 62.5)
        for value in ('nan', 'inf', '-1', '1:60', '1:2:3:4', ''):
            with self.subTest(value=value), self.assertRaises(ValueError):
                footage.secs(value)

    def test_unusable_shot_target_is_rejected_without_silent_clamping(self):
        args = self.cut_args()
        for target in (.5, 1e-300):
            args.max_shot = target
            with self.subTest(target=target), patch.object(footage, 'need') as need:
                with self.assertRaisesRegex(SystemExit, '--max-shot.*1.2'):
                    footage.cmd_cut(Path('unused'), {}, args)
                need.assert_not_called()

    def project(self, folder, audio=''):
        proj = Path(folder)
        (proj / 'video.mp4').touch()
        (proj / 'audio').mkdir()
        (proj / 'audio/source.wav').write_bytes(b'stale audio')
        return proj, {'source': {'footage': 'video.mp4', 'audio': audio, 'range': [0, 2],
                                 'duration': 2, 'width': 320, 'height': 240}}

    def cut_args(self):
        return Namespace(noise=-35, min_silence=.45, pad=.12, fillers=None, max_shot=0,
                         reset=False, no_zoom=True, zoom=1.15)

    def import_fixture(self, proj):
        info = {'streams': [{'codec_type': 'video', 'width': 320, 'height': 240,
                             'avg_frame_rate': '30/1'}, {'codec_type': 'audio'}],
                'format': {'duration': '2'}}
        args = Namespace(video=str(proj / 'video.mp4'), from_=None, to=None,
                         no_clean=True, third_party=False)
        return info, args

    def test_changed_import_with_derivatives_preserves_every_file_and_manifest(self):
        for change in ('path', 'range', 'cleaning'):
            for directory in ('edit', 'captions', 'render', 'out', 'review'):
                with self.subTest(change=change, directory=directory), tempfile.TemporaryDirectory() as folder:
                    proj, m = self.project(folder, 'audio/source.wav')
                    m['source']['cleaned'] = False
                    m['source']['sha256'] = file_sha256(proj / 'video.mp4')
                    derived = proj / directory / ('edl.json' if directory == 'edit' else 'existing.bin')
                    derived.parent.mkdir()
                    derived.write_bytes(b'preserve derived bytes')
                    save_manifest(proj, m)
                    info, args = self.import_fixture(proj)
                    if change == 'path':
                        (proj / 'other.mp4').touch()
                        args.video = str(proj / 'other.mp4')
                    elif change == 'range':
                        args.from_ = '0.5'
                    else:
                        args.no_clean = False
                    before = {p.relative_to(proj): p.read_bytes() for p in proj.rglob('*') if p.is_file()}
                    before_manifest = json.loads(json.dumps(m))
                    with patch.object(footage, 'need', return_value='ffmpeg'), \
                            patch.object(footage, 'ffprobe_json', return_value=info), patch.object(footage, 'run') as execute:
                        with self.assertRaisesRegex(SystemExit, 'Crie um novo projeto'):
                            footage.cmd_import(proj, m, args)
                        execute.assert_not_called()
                    self.assertEqual(m, before_manifest)
                    self.assertEqual({p.relative_to(proj): p.read_bytes() for p in proj.rglob('*') if p.is_file()}, before)

    def test_identical_resolved_import_allowed_with_derivatives(self):
        with tempfile.TemporaryDirectory() as folder:
            proj, m = self.project(folder, 'audio/source.wav')
            m['source']['cleaned'] = False
            m['source']['sha256'] = file_sha256(proj / 'video.mp4')
            (proj / 'edit').mkdir()
            edl = proj / 'edit/edl.json'
            edl.write_bytes(b'preserve EDL')
            info, args = self.import_fixture(proj)
            with patch.object(footage, 'need', return_value='ffmpeg'), \
                    patch.object(footage, 'ffprobe_json', return_value=info), patch.object(footage, 'run') as execute, \
                    patch.object(footage, 'file_sha256', wraps=file_sha256) as digest:
                footage.cmd_import(proj, m, args)
                execute.assert_called_once()
                digest.assert_called_once_with(proj / 'video.mp4')
            self.assertEqual(edl.read_bytes(), b'preserve EDL')

    def test_in_place_replacement_and_legacy_hash_missing_preserve_derivatives(self):
        for mode in ('replaced', 'legacy'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as folder:
                proj, m = self.project(folder, 'audio/source.wav')
                m['source']['cleaned'] = False
                if mode == 'replaced':
                    m['source']['sha256'] = file_sha256(proj / 'video.mp4')
                    (proj / 'video.mp4').write_bytes(b'different content at same path')
                (proj / 'edit').mkdir()
                (proj / 'edit/edl.json').write_bytes(b'existing EDL')
                save_manifest(proj, m)
                before = {p.relative_to(proj): p.read_bytes() for p in proj.rglob('*') if p.is_file()}
                original_manifest = json.loads(json.dumps(m))
                info, args = self.import_fixture(proj)
                with patch.object(footage, 'need', return_value='ffmpeg'), \
                        patch.object(footage, 'ffprobe_json', return_value=info), patch.object(footage, 'run') as execute, \
                        patch.object(footage, 'file_sha256', wraps=file_sha256) as digest:
                    with self.assertRaisesRegex(SystemExit, 'Crie um novo projeto'):
                        footage.cmd_import(proj, m, args)
                    execute.assert_not_called()
                    digest.assert_called_once_with(proj / 'video.mp4')
                self.assertEqual(m, original_manifest)
                self.assertEqual({p.relative_to(proj): p.read_bytes() for p in proj.rglob('*') if p.is_file()}, before)

    def test_different_source_allowed_without_derivatives(self):
        with tempfile.TemporaryDirectory() as folder:
            proj, m = self.project(folder, 'audio/source.wav')
            (proj / 'other.mp4').touch()
            info, args = self.import_fixture(proj)
            args.video = str(proj / 'other.mp4')
            with patch.object(footage, 'need', return_value='ffmpeg'), \
                    patch.object(footage, 'ffprobe_json', return_value=info), patch.object(footage, 'run') as execute:
                footage.cmd_import(proj, m, args)
                execute.assert_called_once()
            self.assertEqual(m['source']['footage'], str(proj / 'other.mp4'))
            self.assertEqual(m['source']['sha256'], file_sha256(proj / 'other.mp4'))

    def test_legacy_source_without_derivatives_migrates_hash(self):
        with tempfile.TemporaryDirectory() as folder:
            proj, m = self.project(folder, 'audio/source.wav')
            m['source']['cleaned'] = False
            info, args = self.import_fixture(proj)
            with patch.object(footage, 'need', return_value='ffmpeg'), \
                    patch.object(footage, 'ffprobe_json', return_value=info), patch.object(footage, 'run'), \
                    patch.object(footage, 'file_sha256', wraps=file_sha256) as digest:
                footage.cmd_import(proj, m, args)
                digest.assert_called_once_with(proj / 'video.mp4')
            self.assertEqual(m['source']['sha256'], file_sha256(proj / 'video.mp4'))

    def test_cut_silent_source_ignores_old_extracted_audio(self):
        with tempfile.TemporaryDirectory() as folder:
            proj, m = self.project(folder)
            with patch.object(footage, 'need', return_value='ffmpeg'), patch.object(footage, 'silences') as sil:
                footage.cmd_cut(proj, m, self.cut_args())
            sil.assert_not_called()
            self.assertEqual(footage.load_edl(proj)['segments'][0]['out'], 2)

    def test_missing_extracted_audio_fails_before_silent_render_or_cut(self):
        for cmd in (footage.cmd_cut, footage.cmd_render):
            with self.subTest(cmd=cmd.__name__), tempfile.TemporaryDirectory() as folder:
                proj, m = self.project(folder, 'audio/missing.wav')
                (proj / 'edit').mkdir()
                footage.save_edl(proj, {'segments': [{'in': 0, 'out': 1}]})
                with patch.object(footage, 'need', return_value='ffmpeg'), patch.object(footage, 'run') as execute:
                    with self.assertRaisesRegex(SystemExit, 'Áudio.*não encontrado'):
                        cmd(proj, m, self.cut_args())
                    execute.assert_not_called()

    def test_zero_end_is_not_interpreted_as_full_video(self):
        with tempfile.TemporaryDirectory() as folder:
            proj, m = self.project(folder)
            info = {'streams': [{'codec_type': 'video'}], 'format': {'duration': '2'}}
            args = Namespace(video=str(proj / 'video.mp4'), from_=None, to='0')
            with patch.object(footage, 'need', return_value='ffmpeg'), patch.object(footage, 'ffprobe_json', return_value=info):
                with self.assertRaisesRegex(SystemExit, '--to'):
                    footage.cmd_import(proj, m, args)

    def test_invalid_edl_and_empty_frames_fail_before_ffmpeg(self):
        with tempfile.TemporaryDirectory() as folder:
            proj, m = self.project(folder)
            (proj / 'edit').mkdir()
            for start, end in ((1, 1), (2, 1), (-1, 2), (0, float('inf'))):
                footage.save_edl(proj, {'segments': [{'in': start, 'out': end}]})
                with self.assertRaisesRegex(SystemExit, 'EDL inválida'):
                    footage.load_edl(proj)
            footage.save_edl(proj, {'segments': []})
            with patch.object(footage, 'need', return_value='ffmpeg'), patch.object(footage, 'run') as execute:
                with self.assertRaisesRegex(SystemExit, 'Nenhum trecho'):
                    footage.cmd_frames(proj, m, Namespace())
                execute.assert_not_called()

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg não instalado')
    def test_real_import_range_extracts_expected_audio_duration(self):
        with tempfile.TemporaryDirectory() as folder:
            proj = Path(folder)
            source = proj / 'input.mp4'
            run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'color=s=64x64:r=10:d=3',
                 '-f', 'lavfi', '-i', 'sine=frequency=440:duration=3', '-c:v', 'libx264',
                 '-c:a', 'aac', '-shortest', str(source)])
            m = {}
            footage.cmd_import(proj, m, Namespace(video=str(source), from_='1', to='2', no_clean=True, third_party=False))
            self.assertAlmostEqual(float(ffprobe_json(proj / 'audio/source.wav')['format']['duration']), 1, places=2)
            self.assertEqual(m['source']['range'], [1, 2])
            m.update(size=[64, 64], fps=10)
            footage.cmd_cut(proj, m, self.cut_args())
            footage.cmd_render(proj, m, Namespace())
            result = ffprobe_json(proj / 'render/master.mp4')
            self.assertAlmostEqual(float(result['format']['duration']), 1, delta=.05)
            self.assertTrue(any(s['codec_type'] == 'audio' for s in result['streams']))


if __name__ == '__main__':
    unittest.main()
