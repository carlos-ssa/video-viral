import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from plan import plan_problems


class StackTests(unittest.TestCase):
    def test_hyperframes_no_install_blocks_before_launch(self):
        import os
        from unittest.mock import patch
        from stack import hyperframes_command
        with patch.dict(os.environ, {'VIDEO_VIRAL_NO_INSTALL': '1', 'HYPERFRAMES_BROWSER_PATH': 'local-chrome'}):
            with self.assertRaisesRegex(ValueError, 'download.*fontes'):
                hyperframes_command(ROOT, ['render'])

    def test_hyperframes_screenshot_and_cache_are_forwarded(self):
        import os
        import tempfile
        from unittest.mock import patch
        from stack import hyperframes_command
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cli = root / 'node_modules/hyperframes/bin/hyperframes.mjs'
            cli.parent.mkdir(parents=True)
            cli.write_text('// stub', encoding='utf-8')
            with patch.dict(os.environ, {'HYPERFRAMES_CACHE_DIR': 'chosen-cache', 'HYPERFRAMES_BROWSER_PATH': 'chosen-chrome'}, clear=True):
                command, env = hyperframes_command(root, ['render', '-o', 'out.mp4'], True)
            self.assertEqual(command[1:], [str(cli), 'render', '-o', 'out.mp4'])
            self.assertEqual(env['PRODUCER_FORCE_SCREENSHOT'], 'true')
            self.assertEqual(env['PRODUCER_EXPERIMENTAL_FAST_CAPTURE'], 'false')
            self.assertEqual(env['HYPERFRAMES_CACHE_DIR'], 'chosen-cache')
            self.assertEqual(env['HYPERFRAMES_BROWSER_PATH'], 'chosen-chrome')
            self.assertEqual(env['HYPERFRAMES_NO_AUTO_INSTALL'], '1')

    def test_plan_supports_isolated_python(self):
        import subprocess
        import sys
        result = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts/plan.py'), '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_check_env_probes_python_in_isolation(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        import check_env
        with patch('check_env.subprocess.run', return_value=SimpleNamespace(stdout='{}')) as run:
            check_env.pythons(None)
        self.assertTrue(run.call_args_list)
        self.assertTrue(all(call.args[0][1:3] == ['-I', '-c'] for call in run.call_args_list))

    def test_check_env_broken_executables_are_not_ready(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        import subprocess
        import check_env
        with patch.object(check_env.shutil, 'which', return_value='broken'):
            for failure in (SimpleNamespace(returncode=1, stdout='', stderr='failed'),
                            OSError('cannot execute'), subprocess.TimeoutExpired('broken', 20)):
                with self.subTest(failure=failure):
                    args = {'side_effect': failure} if isinstance(failure, Exception) else {'return_value': failure}
                    with patch.object(check_env.subprocess, 'run', **args):
                        self.assertIsNone(check_env.cmd_version('ffmpeg'))

    def test_doctor_reports_corrupt_package_and_continues(self):
        import tempfile
        from stack import doctor
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / 'node_modules/hyperframes/package.json'
            package.parent.mkdir(parents=True)
            for contents in ('{broken', '[]', '{}'):
                package.write_text(contents, encoding='utf-8')
                report = doctor(root)
                first = report['modules'][0]
                self.assertFalse(first['installed'])
                self.assertIn('package.json', first['error'])
                self.assertEqual(len(report['modules']), 16)

    def test_catalog_matches_chosen_stack(self):
        data = json.loads((ROOT / 'assets/stack.json').read_text(encoding='utf-8'))
        self.assertEqual(data['version'], '2.0.0')
        self.assertEqual({x['id'] for x in data['modules']}, {'hyperframes', 'gsap', 'ffmpeg', 'three', 'blender',
            'tone', 'gl-transitions', 'comfyui', 'pixi', 'paper', 'p5', 'blender-mcp', 'gltf', 'ace-step', 'edge-tts', 'faster-whisper'})
        for module in data['modules']:
            self.assertTrue((ROOT / module['entrypoint']).exists(), module['id'])

    def test_installer_does_not_offer_removed_engines(self):
        spec = importlib.util.spec_from_file_location('setup_under_test', ROOT / 'scripts/setup_tools.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        groups = set(module.VENV_GROUPS) | set(module.SYSTEM_GROUPS) | set(module.CUSTOM_GROUPS)
        self.assertEqual(groups, {'base', 'voz', 'legendas', 'blender', 'hyperframes', 'comfyui'})

    def test_v2_plan_rejects_unknown_modules(self):
        manifest = json.loads((ROOT / 'assets/video.template.json').read_text(encoding='utf-8'))
        manifest['stack']['modules'].append('outside-engine')
        errors, _ = plan_problems(manifest)
        self.assertTrue(any('catálogo' in error for error in errors))

    def test_v2_tool_plan_requires_module_id(self):
        manifest = json.loads((ROOT / 'assets/video.template.json').read_text(encoding='utf-8'))
        manifest['tool_plan'] = [{'tool': 'arbitrary renderer', 'status': 'planejado'}]
        errors, _ = plan_problems(manifest)
        self.assertTrue(any('module' in error for error in errors))


if __name__ == '__main__':
    unittest.main()
