import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/review.py'


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


if __name__ == '__main__':
    unittest.main()
