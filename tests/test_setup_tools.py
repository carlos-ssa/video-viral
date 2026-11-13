import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import setup_tools as setup


class SetupConsentTests(unittest.TestCase):
    def invoke(self, args, programs=False, uv=False):
        output = io.StringIO()
        with patch.object(sys, 'argv', ['setup_tools.py', *args]), \
                patch.dict(os.environ, {'VIDEO_VIRAL_NO_INSTALL': ''}), \
                patch.object(setup, 'has_program', return_value=programs), \
                patch.object(setup, 'uv_available', return_value=uv), \
                patch.object(setup.subprocess, 'run') as run, \
                patch.object(setup.VENVS.__class__, 'mkdir') as mkdir, \
                contextlib.redirect_stdout(output):
            code = setup.main()
        return code, output.getvalue(), run, mkdir

    def test_system_missing_lists_plan_without_subprocess_or_writes(self):
        for manager, win in [('winget', True), ('brew', False), ('apt-get', False)]:
            with self.subTest(manager=manager), patch.object(setup, 'WIN', win), \
                    patch.object(setup.shutil, 'which', side_effect=lambda name: manager if name == manager else None):
                code, text, run, mkdir = self.invoke(['base'])
                self.assertEqual(code, 4)
                self.assertIn('ffmpeg', text)
                self.assertIn('node', text)
                self.assertIn(manager, text)
                run.assert_not_called()
                mkdir.assert_not_called()

    def test_missing_uv_requires_user_install_consent(self):
        code, text, run, mkdir = self.invoke(['legendas'], programs=True)
        self.assertEqual(code, 4)
        self.assertIn('pip install --user uv', text)
        run.assert_not_called()
        mkdir.assert_not_called()

    def test_comfyui_requires_large_even_with_system_consent(self):
        code, text, run, mkdir = self.invoke(['comfyui', '--allow-system'], programs=True, uv=True)
        self.assertEqual(code, 4)
        self.assertIn('--allow-large', text)
        self.assertIn('3–10 GB', text)
        run.assert_not_called()
        mkdir.assert_not_called()

    def test_partial_consent_never_installs_earlier_groups(self):
        code, text, run, mkdir = self.invoke(['base', 'comfyui', '--allow-large'])
        self.assertEqual(code, 4)
        self.assertIn('ComfyUI', text)
        run.assert_not_called()
        mkdir.assert_not_called()

    def test_direct_helpers_also_guard_system_user_and_large(self):
        with patch.object(setup, 'has_program', return_value=False), \
                patch.object(setup.shutil, 'which', return_value=None), \
                patch.object(setup, 'uv_available', return_value=False), \
                patch.object(setup.subprocess, 'run') as run:
            for call in (lambda: setup.install_program('node'), setup.uv, setup.install_comfyui):
                with self.assertRaises(PermissionError):
                    call()
            run.assert_not_called()

    def test_program_install_reports_status_and_path_hint(self):
        command = ['manager', 'install', 'node']
        for ok in (True, False):
            with self.subTest(ok=ok), patch.object(setup, 'has_program', return_value=False), \
                    patch.object(setup, 'system_command', return_value=command), \
                    patch.object(setup, 'sh', return_value=ok) as sh, \
                    contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(setup.install_program('node', allow_system=True), ok)
                sh.assert_called_once_with(command)
                self.assertIn(f"[{'ok' if ok else '--'}] node", output.getvalue())
                self.assertEqual('abra um terminal novo se o PATH ainda não o mostrar' in output.getvalue(), ok)

    def test_local_node_install_is_autonomous_when_node_present(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(setup, 'has_program', return_value=True), \
                patch.dict(os.environ, {'VIDEO_VIRAL_NODE_ROOT': folder}), \
                patch.object(setup, 'sh', return_value=True) as sh:
            self.assertTrue(setup.install_hyperframes())
            self.assertEqual(sh.call_args_list[0].args[0][1], 'ci')
            self.assertIn('--ignore-scripts', sh.call_args_list[0].args[0])

    def test_no_install_overrides_both_flags(self):
        with patch.object(sys, 'argv', ['setup_tools.py', 'comfyui', '--allow-system', '--allow-large']), \
                patch.dict(os.environ, {'VIDEO_VIRAL_NO_INSTALL': '1'}), \
                patch.object(setup, 'consent_plan') as plan, \
                patch.object(setup.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(setup.main(), 1)
            run.assert_not_called()
            plan.assert_not_called()

    def test_python_requirements_and_comfy_revision_are_data(self):
        revision = json.loads((setup.PYTHON_ASSETS / 'comfyui.json').read_text(encoding='utf-8'))
        self.assertEqual(len(revision['commit']), 40)
        for name in ('requirements-voz.txt', 'requirements-legendas.txt', 'requirements-torch.txt',
                     'requirements-comfyui-torch.txt', 'requirements-cuda.txt', 'constraints-comfyui.txt'):
            lines = (setup.PYTHON_ASSETS / name).read_text(encoding='utf-8').splitlines()
            self.assertTrue(all('==' in line or line.startswith(('#', '-r')) for line in lines if line))

    def test_flags_are_forwarded_only_after_full_consent(self):
        with patch.object(sys, 'argv', ['setup_tools.py', 'base', 'comfyui', '--allow-system', '--allow-large']), \
                patch.dict(os.environ, {'VIDEO_VIRAL_NO_INSTALL': ''}), \
                patch.object(setup, 'has_program', return_value=False), \
                patch.object(setup, 'uv_available', return_value=False), \
                patch.object(setup.VENVS.__class__, 'mkdir'), \
                patch.object(setup, 'install_program', return_value=True) as program, \
                patch.object(setup, 'install_comfyui', return_value=True) as comfy, \
                patch.object(setup.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(setup.main(), 0)
            self.assertEqual(program.call_args_list[0].args, ('ffmpeg', True))
            comfy.assert_called_once_with(True, True)
            run.assert_not_called()

    def test_local_venv_remains_autonomous_with_prerequisites(self):
        with patch.object(sys, 'argv', ['setup_tools.py', 'legendas']), \
                patch.dict(os.environ, {'VIDEO_VIRAL_NO_INSTALL': ''}), \
                patch.object(setup, 'uv_available', return_value=True), \
                patch.object(setup.VENVS.__class__, 'mkdir'), \
                patch.object(setup, 'install_venv', return_value=True) as venv, \
                patch.object(setup.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(setup.main(), 0)
            venv.assert_called_once_with('legendas', False)
            run.assert_not_called()

    def test_existing_venv_reapplies_pins(self):
        with patch.object(setup, 'uv', return_value=['uv']), \
                patch.object(setup, 'venv_python', return_value=Path('venv/python')), \
                patch.object(setup, 'has_modules', return_value=True), \
                patch.object(setup, 'NVIDIA', False), patch.object(setup, 'sh', return_value=True) as sh:
            self.assertTrue(setup.install_venv('legendas'))
            self.assertIn(setup.PYTHON_ASSETS / 'requirements-legendas.txt', sh.call_args.args[0])


if __name__ == '__main__':
    unittest.main()
