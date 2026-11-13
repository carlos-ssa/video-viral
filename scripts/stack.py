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
import sys

ROOT = Path(__file__).resolve().parents[1]


def catalog():
    return json.loads((ROOT / 'assets/stack.json').read_text(encoding='utf-8'))


def doctor(node_root):
    data = catalog()
    result = []
    for module in data['modules']:
        item = {'id': module['id'], 'installed': None, 'artifact_validated': False}
        if module['node_package']:
            package = node_root / 'node_modules' / module['node_package'] / 'package.json'
            item['installed'] = package.is_file()
            if item['installed']:
                try:
                    item['version'] = json.loads(package.read_text(encoding='utf-8'))['version']
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    item.update(installed=False, error=f'package.json inválido: {exc}')
        elif module['id'] == 'ffmpeg':
            item['installed'] = bool(shutil.which('ffmpeg') and shutil.which('ffprobe'))
        elif module['id'] == 'blender':
            found = shutil.which('blender')
            if not found and os.name == 'nt':
                found = next(Path(os.environ.get('ProgramFiles', 'C:/Program Files')).glob('Blender Foundation/*/blender.exe'), None)
            item.update(installed=bool(found), executable=str(found) if found else None)
        elif module['id'] in ('edge-tts', 'faster-whisper'):
            from _common import venv_python
            group, imported = ('voz', 'edge_tts') if module['id'] == 'edge-tts' else ('legendas', 'faster_whisper')
            py = venv_python(group)
            item['installed'] = False
            if py:
                item['python'] = str(py)
                try:
                    checked = subprocess.run([str(py), '-I', '-c', f'import importlib.util; raise SystemExit(0 if importlib.util.find_spec({imported!r}) else 1)'], capture_output=True, timeout=20)
                    item['installed'] = checked.returncode == 0
                except (OSError, subprocess.SubprocessError) as exc:
                    item['error'] = str(exc)
            if module['id'] == 'edge-tts':
                item['note'] = 'Síntese online; conexão e disponibilidade das vozes não verificadas pelo diagnóstico.'
        else:
            item['note'] = 'Serviço/workflow configurado separadamente; disponibilidade não inferida.'
        result.append(item)
    return {'version': data['version'], 'node_root': str(node_root), 'modules': result}


def hyperframes_command(node_root, arguments, screenshot=False):
    """Única rota de execução da CLI; nunca usa npx nem instala pacote implicitamente."""
    env = dict(os.environ)
    env.update(HYPERFRAMES_NO_UPDATE_CHECK='1', HYPERFRAMES_NO_AUTO_INSTALL='1', DO_NOT_TRACK='1')
    if env.get('VIDEO_VIRAL_NO_INSTALL'):
        # A CLI lê BROWSER_PATH/CACHE_DIR, mas não oferece trava geral de download de fontes.
        raise ValueError('VIDEO_VIRAL_NO_INSTALL: CLI HyperFrames bloqueada para impedir downloads de Chrome/fontes. '
                         'HYPERFRAMES_BROWSER_PATH seleciona Chrome local e HYPERFRAMES_CACHE_DIR define cache, '
                         'mas não impedem download de fontes. Os adaptadores Puppeteer locais continuam disponíveis.')
    cli = node_root / 'node_modules/hyperframes/bin/hyperframes.mjs'
    if not cli.is_file():
        raise ValueError('CLI HyperFrames não instalada no node-root; nenhuma instalação automática será feita.')
    if not arguments:
        raise ValueError('Informe o comando após -- (ex.: -- render -o out.mp4).')
    if screenshot:
        env['PRODUCER_FORCE_SCREENSHOT'] = 'true'
        env['PRODUCER_EXPERIMENTAL_FAST_CAPTURE'] = 'false'
    return [shutil.which('node') or 'node', str(cli), *arguments], env


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'hyperframes':
        parser = argparse.ArgumentParser(description='Executa a CLI instalada sem npx; use opções antes de --.')
        parser.add_argument('--node-root', type=Path, default=Path(os.environ.get('VIDEO_VIRAL_NODE_ROOT', str(Path.home() / '.video-viral/node-v2'))))
        parser.add_argument('--screenshot', action='store_true', help='Render: captura por screenshot em vez da rota rápida')
        parser.add_argument('arguments', nargs=argparse.REMAINDER)
        args = parser.parse_args(sys.argv[2:])
        arguments = args.arguments[1:] if args.arguments[:1] == ['--'] else args.arguments
        try:
            command, env = hyperframes_command(args.node_root, arguments, args.screenshot)
        except ValueError as exc:
            parser.exit(1, str(exc) + '\n')
        if args.screenshot:
            print('HyperFrames: reserva explícita por screenshot (PRODUCER_FORCE_SCREENSHOT=true).', flush=True)
        result = subprocess.run(command, env=env)
        if result.returncode and arguments[:1] == ['render'] and not args.screenshot:
            print('Render falhou. Tente stack.py hyperframes --screenshot -- render ... para a reserva por screenshot.', file=sys.stderr)
        return result.returncode
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['list', 'doctor'])
    parser.add_argument('--node-root', type=Path, default=Path(os.environ.get('VIDEO_VIRAL_NODE_ROOT', str(Path.home() / '.video-viral/node-v2'))))
    args = parser.parse_args()
    print(json.dumps(catalog() if args.action == 'list' else doctor(args.node_root), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    sys.exit(main())
