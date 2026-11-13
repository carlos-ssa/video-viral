import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from captions import caption_lines, functional_tail, group_words, script_spelling, write_ass
import captions


def timed(text, step=0.5):
    return [{'w': w, 'start': i * step, 'end': (i + 1) * step - .05}
            for i, w in enumerate(text.split())]


class CaptionTests(unittest.TestCase):
    def test_final_subtitle_import_does_not_use_source_silence(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / 'audio').mkdir()
            (project / 'audio/source.wav').touch()
            source = project / 'final.srt'
            source.write_text('1\n00:00:00,000 --> 00:00:01,000\nOlá\n', encoding='utf-8')
            with patch.object(captions, 'run') as execute:
                words = captions.cmd_import(project, {'source': {'footage': 'x', 'range': [10, 20]}},
                                            Namespace(file=str(source), final=True))
                execute.assert_not_called()
            self.assertEqual((words[0]['start'], words[0]['end']), (0, 1))

    def test_silent_source_import_ignores_stale_source_wav(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / 'audio').mkdir()
            (project / 'audio/source.wav').write_bytes(b'stale')
            source = project / 'source.srt'
            source.write_text('1\n00:00:00,000 --> 00:00:01,000\nOlá\n', encoding='utf-8')
            with patch.object(captions, 'run') as execute:
                words = captions.cmd_import(project, {'source': {'footage': 'x', 'audio': '', 'range': [0, 2]}},
                                            Namespace(file=str(source), final=False))
                execute.assert_not_called()
            self.assertEqual((words[0]['start'], words[0]['end']), (0, 1))

    def test_sentences_never_share_a_block_and_no_orphan_tail(self):
        for text in ('Isso facilita o acesso. Recorte só o necessário.',
                     'Nina trouxe a semente,', 'DOIS CARRINHOS AUMENTAM CAIXAS.',
                     'chegaram e prepare o primeiro gesto do dia seguinte.',
                     'de uma caixa. Achava que um gesto bastava.'):
            groups = group_words(timed(text), 3)
            self.assertEqual(' '.join(g['text'] for g in groups), text[0].upper() + text[1:])
            self.assertTrue(all(len(g['words']) > 1 for g in groups), groups)
            self.assertTrue(all(not re.search(r'[.!?] .', g['text']) for g in groups))

    def test_real_mascotes_prefers_clauses_without_functional_tails(self):
        rows = [('Nina', 5.68, 5.94), ('tentou', 5.94, 6.36), ('uma', 6.36, 6.54),
                ('folha,', 6.54, 6.94), ('só', 7.16, 7.34), ('a', 7.34, 7.46),
                ('folha', 7.46, 7.76), ('foi', 7.76, 7.9), ('embora.', 7.9, 8.24),
                ('Lia', 8.96, 9.1), ('ofereceu', 9.1, 9.58), ('o', 9.58, 9.72),
                ('barco,', 9.72, 10.1), ('juntas', 10.3, 10.7), ('atravessaram.', 10.7, 11.36)]
        words = [{'w': w, 'start': start, 'end': end} for w, start, end in rows]
        groups = group_words(words, 3)
        self.assertEqual([g['text'] for g in groups], ['Nina tentou uma folha,', 'só a folha foi embora.',
                                                    'Lia ofereceu o barco,', 'juntas atravessaram.'])
        self.assertTrue(all(not functional_tail(g['words'][-1]['w']) for g in groups))
        self.assertTrue(all(g['end'] - g['start'] + .001 >= max(.6, len(g['text']) / 24) for g in groups))

    def test_real_explanation_keeps_short_clause_and_capitalizes_after_period(self):
        rows = [('Nesta', 2.52, 2.78), ('oficina,', 2.78, 3.38), ('passa', 3.52, 3.72),
                ('uma', 3.72, 3.9), ('caixa', 3.9, 4.26), ('por', 4.26, 4.5), ('vez.', 4.5, 4.74),
                ('a', 10.2, 10.22), ('fila', 10.22, 10.48), ('cresce.', 10.48, 10.98)]
        words = [{'w': w, 'start': start, 'end': end} for w, start, end in rows]
        groups = group_words(words, 3)
        self.assertEqual([g['text'] for g in groups], ['Nesta oficina,', 'passa uma caixa por vez.', 'A fila cresce.'])
        self.assertEqual(words[-3]['w'], 'a', 'a normalização não altera a transcrição de entrada')

    def test_functional_word_categories_stay_with_the_complement(self):
        for word in ('o', 'a', 'os', 'as', 'um', 'uma', 'de', 'do', 'da', 'em', 'no', 'na',
                     'por', 'para', 'com', 'e', 'que', 'se', 'só', 'seu', 'sua', 'me', 'te', 'lhe'):
            with self.subTest(word=word):
                groups = group_words(timed(f'Faça algo {word} cuidado agora.'), 3)
                self.assertTrue(all(not functional_tail(g['words'][-1]['w']) for g in groups[:-1]), groups)
        words = timed('Nina tentou uma folha azul.')
        for w in words[3:]:
            w['start'] += .7
            w['end'] += .7
        self.assertTrue(all(not functional_tail(g['words'][-1]['w']) for g in group_words(words, 3)[:-1]))

    def test_hard_reading_and_line_limits_override_linguistic_preferences(self):
        groups = group_words(timed('Ela me viu.', 1), 3, max_chars=6, max_lines=1)
        self.assertEqual([g['text'] for g in groups], ['Ela me', 'viu.'])
        self.assertTrue(all(len(g['lines']) == 1 and len(g['lines'][0]) <= 6 for g in groups))
        groups = group_words(timed('Uma caixa, outra caixa.', .1), 3)
        self.assertEqual([g['text'] for g in groups], ['Uma caixa, outra caixa.'])
        self.assertGreaterEqual(groups[0]['end'] - groups[0]['start'] + .001, len(groups[0]['text']) / 24)

    def test_sentence_capitalization_preserves_timing_and_input(self):
        words = timed('a fila parou. a fila cresce. “outra frase.”')
        before = json.loads(json.dumps(words))
        groups = group_words(words, 3)
        self.assertEqual([g['text'] for g in groups], ['A fila parou.', 'A fila cresce.', '“Outra frase.”'])
        self.assertEqual(words, before)
        self.assertEqual([(w['start'], w['end']) for g in groups for w in g['words']],
                         [(w['start'], w['end']) for w in before])

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
