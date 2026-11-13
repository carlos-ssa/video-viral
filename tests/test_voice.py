import contextlib
import io
import os
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import wave

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import voice
from _common import load_manifest, save_manifest
from deliver import license_blockers


class VoiceTests(unittest.TestCase):
    def test_language_defaults_and_rate(self):
        for lang in ('pt', 'pt-BR', 'pt_BR'):
            self.assertEqual(voice.voice_settings({'lang': lang}), ('pt-BR-ThalitaMultilingualNeural', 1.2))
        for lang in ('en', 'en-US', 'en-GB'):
            self.assertEqual(voice.voice_settings({'lang': lang}), ('en-US-AvaMultilingualNeural', 1.2))
        self.assertEqual(voice.speed_to_rate(1.2), '+20%')
        self.assertEqual(voice.speed_to_rate(1), '+0%')
        self.assertEqual(voice.speed_to_rate(0.8), '-20%')

    def test_invalid_speeds_are_rejected(self):
        for speed in (0, -1, float('nan'), float('inf')):
            with self.subTest(speed=speed), self.assertRaises(ValueError):
                voice.speed_to_rate(speed)

    def test_kokoro_settings_migrate_and_explicit_overrides_win(self):
        for lang, expected in (('pt-BR', 'pt-BR-ThalitaMultilingualNeural'), ('en-US', 'en-US-AvaMultilingualNeural')):
            m = {'lang': lang, 'voice': {'engine': 'kokoro', 'voice': 'pf_dora', 'speed': 1.0}}
            self.assertEqual(voice.voice_settings(m), (expected, 1.2))
            self.assertEqual(voice.voice_settings(m, 'en-US-GuyNeural', 0.9), ('en-US-GuyNeural', 0.9))

    def test_existing_edge_settings_are_preserved(self):
        m = {'lang': 'en-US', 'voice': {'engine': 'edge-tts', 'voice': 'en-US-GuyNeural', 'speed': 1.1}}
        self.assertEqual(voice.voice_settings(m), ('en-US-GuyNeural', 1.1))

    def test_other_languages_require_an_explicit_voice(self):
        with self.assertRaisesRegex(ValueError, '--voice'):
            voice.voice_settings({'lang': 'es'})
        self.assertEqual(voice.voice_settings({'lang': 'es'}, 'es-ES-ElviraNeural'), ('es-ES-ElviraNeural', 1.2))

    def fake_edge(self, fail_text=None):
        async def save(path, text):
            if text == fail_text:
                raise ConnectionError('serviço indisponível')
            Path(path).write_bytes(b'mp3 fixture')

        communicate = Mock(side_effect=lambda text, **kw: SimpleNamespace(save=lambda path: save(path, text)))
        return SimpleNamespace(Communicate=communicate)

    def test_synthesis_uses_requested_voice_rate_and_skips_silent_scenes(self):
        edge = self.fake_edge()
        m = {'scenes': [{'id': 's1', 'narration': ' Olá! '}, {'id': 's2', 'narration': ''}]}
        with tempfile.TemporaryDirectory() as folder, patch.dict(sys.modules, {'edge_tts': edge}), \
                patch.object(voice, 'need', return_value='ffmpeg'), \
                patch.object(voice, 'run', side_effect=lambda args: Path(args[-1]).write_bytes(b'wav fixture')) as run, \
                contextlib.redirect_stdout(io.StringIO()):
            proj = Path(folder)
            voice.synth_edge(proj, m, 'pt-BR-ThalitaMultilingualNeural', 1.2)
            edge.Communicate.assert_called_once_with('Olá!', voice='pt-BR-ThalitaMultilingualNeural', rate='+20%')
            self.assertEqual((proj / 'audio/scenes/s1.wav').read_bytes(), b'wav fixture')
            self.assertFalse((proj / 'audio/scenes/s2.wav').exists())
            self.assertEqual(list((proj / 'audio/scenes').iterdir()), [proj / 'audio/scenes/s1.wav'])
            args = run.call_args.args[0]
            self.assertIn('pcm_s16le', args)
            self.assertEqual(args[args.index('-ar') + 1], '48000')

    def test_service_failure_preserves_existing_scene_audio(self):
        edge = self.fake_edge(fail_text='Falha')
        m = {'scenes': [{'id': 's1', 'narration': 'Olá'}, {'id': 's2', 'narration': 'Falha'}]}
        with tempfile.TemporaryDirectory() as folder, patch.dict(sys.modules, {'edge_tts': edge}), \
                patch.object(voice, 'need', return_value='ffmpeg'), \
                patch.object(voice, 'run', side_effect=lambda args: Path(args[-1]).write_bytes(b'new')), \
                contextlib.redirect_stdout(io.StringIO()):
            proj = Path(folder)
            scenes = proj / 'audio/scenes'
            scenes.mkdir(parents=True)
            for scene in m['scenes']:
                (scenes / f"{scene['id']}.wav").write_bytes(b'previous')
            with self.assertRaisesRegex(SystemExit, 's2.*--from-wavs'):
                voice.synth_edge(proj, m, 'en-US-AvaMultilingualNeural', 1.2)
            self.assertEqual({p.name: p.read_bytes() for p in scenes.iterdir()},
                             {'s1.wav': b'previous', 's2.wav': b'previous'})

    def test_cli_migrates_catalog_ids_and_records_actual_source(self):
        for options, approved in (([], False), (['--license', 'Termos aplicáveis confirmados', '--commercial-ok'], True)):
            with self.subTest(approved=approved), tempfile.TemporaryDirectory() as folder:
                proj = Path(folder)
                m = {'lang': 'en-US', 'voice': {'engine': 'kokoro', 'voice': 'af_heart', 'speed': 1},
                     'stack': {'modules': ['ffmpeg', 'kokoro']}, 'tool_plan': [{'module': 'kokoro'}],
                     'assets': [{'path': 'audio/voice.wav', 'license': 'Apache-2.0', 'commercial_ok': True}],
                     'scenes': [{'id': 's1', 'narration': 'Hello', 'start': 0, 'duration': 1}]}
                save_manifest(proj, m)
                with patch.object(sys, 'argv', ['voice.py', str(proj), *options]), \
                        patch.object(voice, 'edge_available', return_value=True), \
                        patch.object(voice, 'synth_edge') as synth, \
                        patch.object(voice, 'assemble', return_value=1), contextlib.redirect_stdout(io.StringIO()):
                    voice.main()
                updated = load_manifest(proj)
                self.assertEqual(updated['voice'], {'engine': 'edge-tts', 'voice': 'en-US-AvaMultilingualNeural', 'speed': 1.2})
                self.assertEqual(updated['stack']['modules'], ['ffmpeg', 'edge-tts'])
                self.assertEqual(updated['tool_plan'][0]['module'], 'edge-tts')
                self.assertEqual(synth.call_args.args[2:], ('en-US-AvaMultilingualNeural', 1.2))
                asset = updated['assets'][0]
                self.assertEqual(len(updated['assets']), 1)
                self.assertIn('+20%', asset['source'])
                self.assertNotIn('Apache', asset['license'])
                self.assertEqual(asset['commercial_ok'], approved)
                self.assertEqual(bool(license_blockers(updated)), not approved)

    def test_commercial_confirmation_requires_license_before_synthesis(self):
        with patch.object(sys, 'argv', ['voice.py', 'unused', '--commercial-ok']), \
                patch.object(voice, 'synth_edge') as synth, contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as result:
                voice.main()
            self.assertEqual(result.exception.code, 2)
            synth.assert_not_called()

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg não instalado')
    def test_from_wavs_works_offline_and_measures_scene_timings(self):
        with tempfile.TemporaryDirectory() as folder:
            proj = Path(folder)
            scenes = proj / 'audio/scenes'
            scenes.mkdir(parents=True)
            with wave.open(str(scenes / 's1.wav'), 'wb') as audio:
                audio.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
                audio.writeframes(b'\0\0' * 24000)
            m = {'voice': {'engine': 'external'}, 'assets': [], 'scenes': [
                {'id': 's1', 'narration': 'Teste'}, {'id': 's2', 'narration': '', 'duration': 0.5}]}
            save_manifest(proj, m)
            with patch.object(sys, 'argv', ['voice.py', str(proj), '--from-wavs']), \
                    patch.dict(os.environ, {'VIDEO_VIRAL_NO_INSTALL': '1'}), \
                    patch.object(voice, 'synth_edge') as synth, patch.object(voice, 'use_venv') as venv, \
                    contextlib.redirect_stdout(io.StringIO()):
                voice.main()
            synth.assert_not_called()
            venv.assert_not_called()
            updated = load_manifest(proj)
            self.assertEqual(updated['voice'], m['voice'])
            self.assertEqual(updated['assets'], [])
            self.assertEqual(updated['scenes'][0]['duration'], 1.25)
            self.assertEqual(updated['scenes'][1]['start'], 1.25)
            self.assertAlmostEqual(voice.duration(proj / 'audio/voice.wav'), 1.75, places=2)


if __name__ == '__main__':
    unittest.main()
