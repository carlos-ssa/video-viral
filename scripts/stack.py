"""Catálogo e diagnóstico do stack v2. Instalado/disponível não significa render validado.

python scripts/stack.py list
python scripts/stack.py doctor [--node-root pasta]
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def catalog():
    return json.loads((ROOT / 'assets/stack.json').read_text(encoding='utf-8'))


def doctor(node_root):
    result = []
    for module in catalog()['modules']:
        item = {'id': module['id'], 'installed': None, 'artifact_validated': False}
        if module['node_package']:
            package = node_root / 'node_modules' / module['node_package'] / 'package.json'
            item['installed'] = package.is_file()
            if item['installed']:
                item['version'] = json.loads(package.read_text(encoding='utf-8'))['version']
        elif module['id'] == 'ffmpeg':
            item['installed'] = bool(shutil.which('ffmpeg') and shutil.which('ffprobe'))
        elif module['id'] == 'blender':
            found = shutil.which('blender')
            if not found and os.name == 'nt':
                found = next(Path(os.environ.get('ProgramFiles', 'C:/Program Files')).glob('Blender Foundation/*/blender.exe'), None)
            item.update(installed=bool(found), executable=str(found) if found else None)
        elif module['id'] in ('kokoro', 'faster-whisper'):
            from _common import venv_python
            group, imported = ('voz', 'kokoro') if module['id'] == 'kokoro' else ('legendas', 'faster_whisper')
            py = venv_python(group)
            item['installed'] = False
            if py:
                checked = subprocess.run([str(py), '-c', f'import importlib.util; raise SystemExit(0 if importlib.util.find_spec({imported!r}) else 1)'], capture_output=True, timeout=20)
                item.update(installed=checked.returncode == 0, python=str(py))
        else:
            item['note'] = 'Serviço/workflow configurado separadamente; disponibilidade não inferida.'
        result.append(item)
    return {'version': catalog()['version'], 'node_root': str(node_root), 'modules': result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['list', 'doctor'])
    parser.add_argument('--node-root', type=Path, default=Path(os.environ.get('VIDEO_VIRAL_NODE_ROOT', str(Path.home() / '.video-viral/node-v2'))))
    args = parser.parse_args()
    print(json.dumps(catalog() if args.action == 'list' else doctor(args.node_root), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
