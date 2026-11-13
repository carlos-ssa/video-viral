from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from voice import synth_kokoro


class VoiceTests(unittest.TestCase):
    def test_cpu_path_does_not_probe_empty_cuda_backend(self):
        cudnn = SimpleNamespace(enabled=True)
        torch = SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: False), backends=SimpleNamespace(cudnn=cudnn))
        observed = []

        def pipeline(**options):
            if options['device'] == 'cpu' and cudnn.enabled:
                raise ValueError('simulated empty CUDA device list in CPU LSTM setup')
            observed.append(options)
            return object()

        modules = {'torch': torch, 'numpy': SimpleNamespace(), 'soundfile': SimpleNamespace(),
                   'kokoro': SimpleNamespace(KPipeline=pipeline)}
        with patch.dict(sys.modules, modules):
            synth_kokoro(Path('.'), {'scenes': []}, 'pf_dora', 1.0, 'p', 'auto')
        self.assertEqual(observed[0]['device'], 'cpu')


if __name__ == '__main__':
    unittest.main()
