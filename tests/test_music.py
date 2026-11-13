import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'music.py'
WAV = b'RIFF\x04\x00\x00\x00WAVE'


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, obj):
        body = json.dumps({'code': 200, 'error': None, 'data': obj}).encode()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.server.requests.append((self.path, body, self.headers.get('Authorization')))
        if self.path == '/release_task':
            self.reply({'task_id': 'job'})
        elif self.server.mode == 'failure':
            self.reply([{'task_id': 'job', 'status': 2}])
        elif self.server.mode == 'timeout':
            self.reply([{'task_id': 'job', 'status': 0}])
        else:
            file = 'http://127.0.0.1:1/v1/audio?path=x' if self.server.mode == 'foreign' else '/v1/audio?path=%2Ftmp%2Fx.wav'
            result = [] if self.server.mode == 'incomplete' else [{'status': 1, 'file': file}]
            self.reply([{'task_id': 'job', 'status': 1, 'result': json.dumps(result)}])

    def do_GET(self):
        self.server.requests.append((self.path, None, self.headers.get('Authorization')))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(WAV)


class MusicTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.proj = Path(self.temp.name)
        self.manifest = self.proj / 'video.json'
        self.manifest.write_text('{"assets": []}\n', encoding='utf-8')
        self.output = self.proj / 'audio' / 'music.wav'
        self.output.parent.mkdir()
        self.output.write_bytes(b'previous')
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.server.requests = []
        self.server.mode = 'success'
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def invoke(self, *extra):
        env = dict(os.environ, ACE_STEP_API_KEY='test-secret')
        return subprocess.run([sys.executable, str(SCRIPT), str(self.proj), '--endpoint', f'http://127.0.0.1:{self.server.server_port}', '--prompt', 'jazz', '--duration', '30', '--seed', '42', *extra], capture_output=True, text=True, encoding="utf-8", env=env)

    def test_success_contract(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.output.read_bytes(), WAV)
        self.assertEqual(self.server.requests[0], ('/release_task', {'prompt': 'jazz', 'audio_duration': 30.0, 'seed': 42, 'use_random_seed': False, 'audio_format': 'wav', 'batch_size': 1}, 'Bearer test-secret'))
        self.assertEqual(self.server.requests[1][1], {'task_id_list': ['job']})
        self.assertTrue(self.server.requests[2][0].startswith('/v1/audio?path='))
        asset = json.loads(self.manifest.read_text(encoding='utf-8'))['assets'][0]
        self.assertFalse(asset['commercial_ok'])
        self.assertNotIn('test-secret', self.manifest.read_text(encoding='utf-8') + result.stdout + result.stderr)

    def test_failures_preserve_files(self):
        for mode in ('failure', 'timeout', 'foreign', 'incomplete'):
            with self.subTest(mode=mode):
                self.server.mode = mode
                before = self.manifest.read_bytes()
                result = self.invoke('--timeout', '0.2' if mode == 'timeout' else '5')
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertEqual(self.manifest.read_bytes(), before)
                self.assertEqual(self.output.read_bytes(), b'previous')

    def test_invalid_inputs_do_not_contact_server(self):
        for extra in (('--output', '../escape.wav'), ('--duration', 'nan'), ('--commercial-ok',)):
            with self.subTest(extra=extra):
                result = self.invoke(*extra)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.server.requests, [])

    def test_explicit_license(self):
        result = self.invoke('--license', 'Licença comercial confirmada', '--commercial-ok')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(self.manifest.read_text(encoding='utf-8'))['assets'][0]['commercial_ok'])


if __name__ == '__main__':
    unittest.main()
