import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from plan import plan_problems


class StackTests(unittest.TestCase):
    def test_catalog_matches_chosen_stack(self):
        data = json.loads((ROOT / 'assets/stack.json').read_text(encoding='utf-8'))
        self.assertEqual(data['version'], '2.0.0')
        self.assertEqual({x['id'] for x in data['modules']}, {'hyperframes', 'gsap', 'ffmpeg', 'three', 'blender',
            'tone', 'gl-transitions', 'comfyui', 'pixi', 'paper', 'p5', 'blender-mcp', 'gltf', 'ace-step', 'kokoro', 'faster-whisper'})
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
