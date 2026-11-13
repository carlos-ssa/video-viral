import json
import re
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/review.py'
sys.path.insert(0, str(SCRIPT.parent))
import review
from _common import save_manifest


class ReviewerPreflightCLITests(unittest.TestCase):
    def test_limited_modalities_and_separation_are_checked_before_delegation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'capabilities.json'
            cap = {'schema': 1, 'reviewer_id': 'reviewer:fixture', 'author_scores_exposed': False,
                   'channels': {name: {'available': name == 'visual', 'method': 'synthetic policy fixture',
                                      'evidence': 'test record'} for name in ('visual', 'motion', 'audio')}}
            path.write_text(json.dumps(cap), encoding='utf-8')
            command = [sys.executable, str(SCRIPT), '--check-reviewer', str(path), '--producer-id', 'producer:fixture']
            full = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(full.returncode, 1)
            self.assertEqual(json.loads(full.stdout)['unavailable'], ['motion', 'audio'])
            partial = subprocess.run(command + ['--channels', 'visual'], capture_output=True, text=True)
            self.assertEqual(partial.returncode, 0)
            self.assertEqual(json.loads(partial.stdout)['requested_channels'], ['visual'])
            cap['reviewer_id'] = 'producer:fixture'
            path.write_text(json.dumps(cap), encoding='utf-8')
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            self.assertEqual({p.name for p in Path(folder).iterdir()}, {'capabilities.json'})


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'requer FFmpeg e ffprobe')
class RenderGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.video = self.root / 'fixture.mp4'

    def render(self, inputs, extra=()):
        command = ['ffmpeg', '-v', 'error', '-y']
        for source in inputs:
            command += ['-f', 'lavfi', '-i', source]
        subprocess.run(command + list(extra) + ['-c:v', 'libx264', '-preset', 'ultrafast',
                                              '-pix_fmt', 'yuv420p', str(self.video)],
                       cwd=self.root, capture_output=True, check=True)

    def test_localized_motion_is_not_a_frozen_frame(self):
        self.render(['color=blue:s=180x320:r=10:d=4', 'testsrc2=s=24x24:r=10:d=4'],
                    ['-filter_complex', '[0:v][1:v]overlay=80:110:shortest=1'])
        _, _, freezes = review.analyze('ffmpeg', self.video, self.root, 10, 180, 320)
        self.assertEqual(review.freeze_checks(freezes, 4, False, []), ([], []))

    def test_changing_subtitles_break_freezes(self):
        (self.root / 'captions.ass').write_text(
            '[Script Info]\nScriptType: v4.00+\nPlayResX: 180\nPlayResY: 320\n'
            '[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, '
            'Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, '
            'Alignment, MarginL, MarginR, MarginV, Encoding\n'
            'Style: Default,Arial,24,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,2,10,10,20,1\n'
            '[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
            'Dialogue: 0,0:00:00.00,0:00:01.00,Default,,0,0,0,,UM\n'
            'Dialogue: 0,0:00:01.00,0:00:02.00,Default,,0,0,0,,DOIS\n'
            'Dialogue: 0,0:00:02.00,0:00:03.00,Default,,0,0,0,,TRES\n'
            'Dialogue: 0,0:00:03.00,0:00:04.00,Default,,0,0,0,,QUATRO\n', encoding='utf-8')
        self.render(['color=blue:s=180x320:r=10:d=4'], ['-vf', 'subtitles=captions.ass'])
        _, _, freezes = review.analyze('ffmpeg', self.video, self.root, 10, 180, 320)
        self.assertFalse(any((4 - s if d is None else d) >= review.SHORT_FREEZE_ERROR_SECONDS for s, d in freezes))

    def test_pulses_have_low_audible_ratio_and_cli_does_not_call_them_speech(self):
        self.render(['testsrc2=s=180x320:r=10:d=4', 'sine=frequency=440:sample_rate=48000:duration=4'],
                    ['-af', "volume=0:enable='gte(t,0.8)'", '-c:a', 'aac'])
        def lufs():
            measured = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(self.video),
                                       '-af', 'ebur128', '-vn', '-f', 'null', '-'], capture_output=True, text=True, check=True)
            return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', measured.stderr)[-1])
        normalized = self.root / 'normalized.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(self.video), '-c:v', 'copy',
                        '-af', f'volume={-14 - lufs():.1f}dB', '-c:a', 'aac', str(normalized)],
                       capture_output=True, check=True)
        normalized.replace(self.video)
        self.assertAlmostEqual(lufs(), -14, delta=1)
        activity = review.audio_activity('ffmpeg', self.video, 4)
        self.assertLess(activity['audible_fraction'], 0.25)
        save_manifest(self.root, {'slug': 'fixture', 'format': 'storytelling', 'size': [180, 320],
                                  'voice': {'engine': 'none'}, 'scenes': [{'id': 's1', 'narration': ''}]})
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root), '--video', str(self.video),
                                 '--producer-id', 'producer:fixture'], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        metrics = json.loads((self.root / 'review/r01/metrics.json').read_text(encoding='utf-8'))
        self.assertIsNone(metrics['speech_start_s'])
        self.assertTrue(any('Áudio audível' in b for b in metrics['blockers']))
        self.assertFalse(any('fala começa' in b for b in metrics['blockers']))

    def test_dead_tail_uses_render_silence_and_stillness(self):
        self.render(['color=blue:s=180x320:r=10:d=4', 'sine=frequency=440:sample_rate=48000:duration=4'],
                    ['-af', "volume=0:enable='gte(t,2)'", '-c:a', 'aac'])
        _, _, freezes = review.analyze('ffmpeg', self.video, self.root, 10, 180, 320)
        activity = review.audio_activity('ffmpeg', self.video, 4)
        block, _ = review.audio_checks({}, 4, False, activity, freezes, [(0, 2)])
        self.assertTrue(any('Cauda morta' in b for b in block), block)
        self.assertFalse(review.audio_checks({}, 4, False, activity, freezes, [(0, 4)])[0])

    def test_internal_silence_is_measured_at_minus_45_db(self):
        self.render(['testsrc2=s=180x320:r=10:d=4', 'sine=frequency=440:sample_rate=48000:duration=4'],
                    ['-af', "volume=0:enable='between(t,1,2.2)'", '-c:a', 'aac'])
        activity = review.audio_activity('ffmpeg', self.video, 4)
        _, warn = review.audio_checks({}, 4, False, activity, [], [])
        self.assertTrue(any('Silêncio no meio' in w for w in warn), warn)
        self.assertAlmostEqual(activity['audible_fraction'], 0.7, delta=0.05)



if __name__ == '__main__':
    unittest.main()
