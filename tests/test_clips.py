from argparse import Namespace
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from clips import cmd_make, cmd_suggest
from footage import remap_words


class ClipsTests(unittest.TestCase):
    def test_invalid_suggestion_limits_fail_before_reading_transcript(self):
        for minimum, maximum, top in ((0, 30, 1), (40, 30, 1), (1, float('nan'), 1), (1, 30, 0)):
            with self.subTest(minimum=minimum, maximum=maximum, top=top):
                with self.assertRaisesRegex(SystemExit, '--min'):
                    cmd_suggest(Path('unused'), {}, Namespace(min=minimum, max=maximum, top=top))

    def test_invalid_ranges_do_not_create_child_projects(self):
        for start, end in (('5', '4.9'), ('-1', '2'), ('1', '11')):
            with self.subTest(start=start, end=end), tempfile.TemporaryDirectory() as temp:
                args = Namespace(rank=None, from_=start, to=end)
                with patch('clips.subprocess.run') as execute:
                    with self.assertRaises((SystemExit, ValueError)):
                        cmd_make(Path(temp), {'source': {'footage': 'source.mp4', 'range': [0, 10]}}, args)
                    execute.assert_not_called()

    def test_make_preserves_source_license_provenance_and_ai_label(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            project, child = parent / 'long', parent / 'clip'
            project.mkdir()
            child.mkdir()
            footage = str(parent / 'synthetic.mp4')
            source_asset = {'path': footage, 'type': 'footage', 'source': 'animação sintética',
                            'license': 'autoral, gerada', 'commercial_ok': True, 'provenance': {'ai': True}}
            m = {'source': {'footage': footage, 'range': [0, 30], 'provenance': 'gerada por IA'},
                 'assets': [source_asset], 'publish': {'ai_label': True}}
            # Emula apenas subprocessos de criação/importação: não há FFmpeg nem rede neste teste.
            imported = {'source': {'footage': footage}, 'assets': [dict(source_asset, source='gravação do usuário', license='própria')], 'publish': {'ai_label': False}}
            (child / 'video.json').write_text(json.dumps(imported), encoding='utf-8')
            a = Namespace(rank=None, from_='1', to='5', dir=str(parent), slug='clip', title=None, aspect='9:16')
            with patch('clips.subprocess.run', return_value=Namespace(returncode=0)):
                cmd_make(project, m, a)
            result = json.loads((child / 'video.json').read_text(encoding='utf-8'))
            self.assertEqual(result['assets'], [source_asset])
            self.assertTrue(result['publish']['ai_label'])
            self.assertEqual(result['source']['provenance'], 'gerada por IA')

    def test_remap_keeps_audible_edges_without_duplicates(self):
        mapping = [({'in': 1, 'out': 2, '_dur': 1}, 0),
                   ({'in': 3, 'out': 4, '_dur': 1}, 1)]
        words = [{'w': 'borda', 'start': .6, 'end': 1.1},
                 {'w': 'fim', 'start': 1.9, 'end': 2.4},
                 {'w': 'fora', 'start': 2.4, 'end': 3},
                 {'w': 'salto', 'start': 3.1, 'end': 3.5}]
        result = remap_words(words, mapping)
        self.assertEqual([w['w'] for w in result], ['borda', 'fim', 'salto'])
        self.assertEqual((result[0]['start'], result[0]['end']), (0, .1))
        self.assertEqual(result[1]['end'], 1)
        self.assertTrue(result[2]['jump'])
        mapping = [({'in': 0, 'out': 1, '_dur': 1}, 0), ({'in': 1, 'out': 2, '_dur': 1}, 1)]
        result = remap_words([{'w': 'cruza', 'start': .8, 'end': 1.3}], mapping)
        self.assertEqual(len(result), 1)
        self.assertNotIn('jump', result[0])


if __name__ == '__main__':
    unittest.main()
