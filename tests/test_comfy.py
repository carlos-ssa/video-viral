import base64
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from _common import save_manifest, load_manifest
from comfy import execute, ComfyError

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+j6l8AAAAASUVORK5CYII=')


class ComfyTests(unittest.TestCase):
    def test_api_success_failure_and_source_integrity(self):
        state = {'fail': False, 'wrong_image': False}

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'prompt_id': 'test', 'node_errors': {}} if body.get('prompt') else {}).encode())

            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                if self.path.startswith('/history/'):
                    self.wfile.write(json.dumps({'test': {'status': {'status_str': 'error' if state['fail'] else 'success'},
                        'outputs': {'9': {'images': [{'filename': 'output.png', 'subfolder': '', 'type': 'output'}]}}}}).encode())
                else:
                    self.wfile.write(b'not image' if state['wrong_image'] else PNG)

        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as folder:
                proj = Path(folder)
                save_manifest(proj, {'assets': []})
                workflow = proj / 'workflow.json'
                workflow.write_text(json.dumps({'9': {'class_type': 'SaveImage', 'inputs': {}}}))
                endpoint = f'http://127.0.0.1:{server.server_port}'
                result = execute(proj, workflow, '9', 'assets/image.png', endpoint)
                self.assertTrue(result['generation_completed'])
                self.assertEqual((proj / 'assets/image.png').read_bytes(), PNG)
                self.assertIsNone(load_manifest(proj)['assets'][0]['commercial_ok'])
                before = (proj / 'video.json').read_bytes()
                for mode in ('fail', 'wrong_image'):
                    state[mode] = True
                    with self.assertRaises(ComfyError):
                        execute(proj, workflow, '9', 'assets/image.png', endpoint)
                    self.assertEqual((proj / 'assets/image.png').read_bytes(), PNG)
                    self.assertEqual((proj / 'video.json').read_bytes(), before)
                    state[mode] = False
                with self.assertRaises(ComfyError):
                    execute(proj, workflow, '9', '../outside.png', endpoint)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_ui_workflow_rejected_before_outputs(self):
        with tempfile.TemporaryDirectory() as folder:
            proj = Path(folder)
            save_manifest(proj, {})
            workflow = proj / 'ui.json'
            workflow.write_text('{"nodes": []}')
            with self.assertRaises(ComfyError):
                execute(proj, workflow, '9', 'assets/image.png')
            self.assertFalse((proj / 'assets').exists())


if __name__ == '__main__':
    unittest.main()
