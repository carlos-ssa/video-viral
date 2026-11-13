import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from captions import caption_lines, group_words, script_spelling, write_ass


def timed(text, step=0.5):
    return [{'w': w, 'start': i * step, 'end': (i + 1) * step - .05}
            for i, w in enumerate(text.split())]


class CaptionTests(unittest.TestCase):
    def test_sentences_never_share_a_block_and_no_orphan_tail(self):
        for text in ('Isso facilita o acesso. Recorte só o necessário.',
                     'Nina trouxe a semente,', 'DOIS CARRINHOS AUMENTAM CAIXAS.',
                     'chegaram e prepare o primeiro gesto do dia seguinte.',
                     'de uma caixa. Achava que um gesto bastava.'):
            groups = group_words(timed(text), 3)
            self.assertEqual(' '.join(g['text'] for g in groups), text)
            self.assertTrue(all(len(g['words']) > 1 for g in groups), groups)
            self.assertTrue(all(not re.search(r'[.!?] .', g['text']) for g in groups))

    def test_pause_and_jump_are_hard_boundaries(self):
        words = timed('Uma frase outra frase')
        for w in words[2:]:
            w['start'] += 1
            w['end'] += 1
        self.assertEqual([g['text'] for g in group_words(words, 8)], ['Uma frase', 'outra frase'])
        words = timed('Uma frase outra frase')
        words[2]['jump'] = True
        self.assertEqual(len(group_words(words, 8)), 2)

    def test_pause_does_not_isolate_last_word(self):
        words = timed('Nina trouxe a semente,')
        words[-1]['start'] += .7
        words[-1]['end'] += .7
        self.assertTrue(all(len(g['words']) > 1 for g in group_words(words, 3)))

    def test_reading_time_changes_word_count_instead_of_emitting_fast_blocks(self):
        words = [{'w': w, 'start': start, 'end': end} for w, start, end in
                 [('Por', .94, 1.11), ('que', 1.11, 1.28), ('a', 1.28, 1.44),
                  ('fila', 1.44, 1.64), ('parou?', 1.64, 2.04)]]
        groups = group_words(words, 3)
        self.assertTrue(all(g['end'] - g['start'] >= .6 for g in groups))
        self.assertTrue(all(len(g['words']) > 1 for g in groups))

    def test_limits_reading_time_and_explicit_ass_line_break(self):
        words = timed('Uma tarefa pequena de cada vez', 1)
        groups = group_words(words, 6, max_chars=18)
        self.assertTrue(all(len(line) <= 18 for g in groups for line in g['lines']))
        self.assertTrue(all(g['end'] - g['start'] >= .6 for g in groups))
        self.assertTrue(all(len(line.split()) > 1 for line in groups[0]['lines']))
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'captions.ass'
            write_ass(groups, out, {}, (1080, 1920))
            self.assertIn(r'\N', out.read_text(encoding='utf-8'))
        with self.assertRaisesRegex(ValueError, 'rápida'):
            group_words(timed('Uma frase. Outra frase.', .03), 3)
        with self.assertRaisesRegex(ValueError, 'caracteres'):
            group_words(timed('extraordinariamente'), 3, max_chars=4)

    def test_source_spelling_restores_numerals_and_punctuation(self):
        words = timed('Em Neemias dois, dezessete, temos um convite.')
        result = script_spelling(words, 'Em Neemias 2:17 temos um convite.')
        self.assertEqual(' '.join(w['w'] for w in result), 'Em Neemias 2:17 temos um convite.')
        number = result[2]
        self.assertEqual((number['start'], number['end']), (words[2]['start'], words[3]['end']))
        self.assertEqual(words[0]['start'], result[0]['start'])
        self.assertEqual(script_spelling(timed('Outro assunto.'), 'Neemias 2:17'), timed('Outro assunto.'))

    def test_ass_cli_preserves_existing_options(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / 'captions').mkdir()
            (project / 'video.json').write_text(json.dumps({'captions': {'uppercase': False}}), encoding='utf-8')
            (project / 'captions/words.json').write_text(json.dumps(timed('Leia Neemias dois, dezessete.')), encoding='utf-8')
            script = project / 'script.txt'
            script.write_text('Leia Neemias 2:17.', encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/captions.py'), 'ass', temp,
                                     '--words', '3', '--script-text', str(script)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads((project / 'captions/captions.json').read_text(encoding='utf-8'))
            self.assertIn('2:17.', ' '.join(g['text'] for g in data))


if __name__ == '__main__':
    unittest.main()
