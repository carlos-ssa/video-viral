"""Read-only repository review: compare baseline/current audio after dialogue EOF."""
import array
import json
import math
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / 'scripts'))
import deliver

baseline = {'__name__': 'baseline_deliver', '__file__': str(REPO / 'scripts/deliver.py')}
source = subprocess.check_output(['git', 'show', '52d567d:scripts/deliver.py'], cwd=REPO).decode('utf-8')
exec(compile(source, 'baseline-deliver.py', 'exec'), baseline)
results = {}
for version, function in [('baseline', baseline['audio_graph']), ('current', deliver.audio_graph)]:
    graph, label = function({'video_audio': 0, 'music': 1}, -6)
    command = ['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
               'sine=frequency=440:sample_rate=48000:duration=1', '-f', 'lavfi', '-i',
               'sine=frequency=1000:sample_rate=48000:duration=3',
               '-filter_complex', ';'.join(graph), '-map', label, '-t', '3',
               '-ar', '48000', '-ac', '1', '-f', 'f32le', '-']
    result = subprocess.run(command, capture_output=True, check=True)
    pcm = array.array('f')
    pcm.frombytes(result.stdout)
    if sys.byteorder != 'little':
        pcm.byteswap()
    rms = {}
    for start in (.5, 1.5, 2.5):
        segment = pcm[int(start * 48000):int((start + .1) * 48000)]
        rms[str(start)] = math.sqrt(sum(value * value for value in segment) / len(segment))
    results[version] = {'frames': len(pcm), 'rms_100ms': rms, 'graph': graph, 'command': command}
print(json.dumps(results, indent=2))
