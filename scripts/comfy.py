"""Executa workflow ComfyUI API JSON existente; não instala nós/modelos nem inicia o servidor.

python scripts/comfy.py <projeto> --workflow edit/workflow.json --output-node 9 --output assets/image.png
O workflow deve estar exportado no formato API e conter os checkpoints/nós realmente instalados.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile
import time
import urllib.parse
import urllib.request

from _common import add_asset, load_manifest, project_dir, save_manifest


class ComfyError(ValueError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def execute(proj, workflow_path, output_node, output, endpoint='http://127.0.0.1:8188',
            timeout=600, license_='', commercial_ok=False):
    proj = proj.resolve()
    parsed = urllib.parse.urlsplit(endpoint)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password or parsed.path not in ('', '/') or parsed.query or parsed.fragment:
        raise ComfyError('Endpoint precisa ser uma origem HTTP(S).')
    if not math.isfinite(timeout) or not 0 < timeout <= 3600:
        raise ComfyError('Timeout deve ser positivo, até 3600 s.')
    dest = (proj / output).resolve()
    if Path(output).is_absolute() or not dest.is_relative_to(proj) or dest.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
        raise ComfyError('Saída deve ser uma imagem relativa dentro do projeto.')
    if commercial_ok and not license_.strip():
        raise ComfyError('Confirmação comercial exige licença dos modelos/ativos.')
    raw = workflow_path.read_bytes()
    workflow = json.loads(raw)
    if not isinstance(workflow, dict) or not workflow or any(not isinstance(node, dict) or not isinstance(node.get('class_type'), str) or not isinstance(node.get('inputs'), dict) for node in workflow.values()):
        raise ComfyError('Use workflow exportado no formato API, não o JSON da interface.')
    if output_node not in workflow:
        raise ComfyError('Nó de saída ausente do workflow.')
    manifest = load_manifest(proj)
    add_asset(manifest, dest.relative_to(proj).as_posix(), 'image', 'ComfyUI workflow fornecido',
              license_.strip() or 'modelos/workflow: uso comercial não verificado', True if commercial_ok else None)
    endpoint = endpoint.rstrip('/')
    opener = urllib.request.build_opener(NoRedirect())
    deadline = time.monotonic() + timeout

    def request(route, body=None, limit=1024 * 1024):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ComfyError('Tempo limite excedido.')
        data = json.dumps(body).encode() if body is not None else None
        with opener.open(urllib.request.Request(endpoint + route, data, {'Content-Type': 'application/json'}), timeout=min(remaining, 30)) as response:
            chunks, total = [], 0
            while True:
                if time.monotonic() >= deadline:
                    raise ComfyError('Tempo limite excedido.')
                chunk = response.read(min(65536, limit + 1 - total))
                if not chunk:
                    break
                total += len(chunk)
                if total > limit:
                    raise ComfyError('Resposta maior que o limite.')
                chunks.append(chunk)
            return b''.join(chunks)

    submitted = json.loads(request('/prompt', {'prompt': workflow}))
    prompt_id = submitted.get('prompt_id') if isinstance(submitted, dict) else None
    if not isinstance(prompt_id, str) or not prompt_id or submitted.get('node_errors'):
        raise ComfyError('Workflow rejeitado ou resposta sem prompt_id.')
    for _ in range(900):
        history = json.loads(request('/history/' + urllib.parse.quote(prompt_id, safe='')))
        item = history.get(prompt_id) if isinstance(history, dict) else None
        if item:
            if item.get('status', {}).get('status_str') == 'error':
                raise ComfyError('Workflow falhou no servidor; confira o histórico do ComfyUI.')
            images = item.get('outputs', {}).get(output_node, {}).get('images')
            if images:
                selected = images[0]
                if not isinstance(selected, dict) or not selected.get('filename'):
                    raise ComfyError('Nó de saída não contém uma imagem válida.')
                payload = request('/view?' + urllib.parse.urlencode({k: selected.get(k, '') for k in ('filename', 'subfolder', 'type')}), limit=50 * 1024 * 1024)
                if payload.startswith(b'\x89PNG\r\n\x1a\n'):
                    extension = '.png'
                elif payload.startswith(b'\xff\xd8\xff'):
                    extension = '.jpg'
                elif payload[:4] == b'RIFF' and payload[8:12] == b'WEBP':
                    extension = '.webp'
                else:
                    raise ComfyError('Resposta não é PNG/JPEG/WebP.')
                expected = '.jpg' if dest.suffix.lower() == '.jpeg' else dest.suffix.lower()
                if extension != expected:
                    raise ComfyError('Extensão de saída não corresponde à imagem retornada.')
                break
        time.sleep(min(1, max(0, deadline - time.monotonic())))
    else:
        raise ComfyError('Limite de consultas excedido.')
    dest.parent.mkdir(parents=True, exist_ok=True)
    previous = dest.read_bytes() if dest.exists() else None
    with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False) as stream:
        temp = Path(stream.name)
        stream.write(payload)
    try:
        temp.replace(dest)
        try:
            save_manifest(proj, manifest)
        except Exception:
            if previous is None:
                dest.unlink(missing_ok=True)
            else:
                dest.write_bytes(previous)
            raise
    finally:
        temp.unlink(missing_ok=True)
    receipt = {'tool': 'ComfyUI', 'workflow_sha256': hashlib.sha256(raw).hexdigest(),
               'output_sha256': hashlib.sha256(payload).hexdigest(), 'prompt_id': prompt_id,
               'output_node': output_node, 'generation_completed': True, 'visual_quality_verified': False}
    dest.with_suffix(dest.suffix + '.receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project')
    parser.add_argument('--workflow', type=Path, required=True)
    parser.add_argument('--output-node', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--endpoint', default='http://127.0.0.1:8188')
    parser.add_argument('--timeout', type=float, default=600)
    parser.add_argument('--license', default='')
    parser.add_argument('--commercial-ok', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(execute(project_dir(args.project), args.workflow, args.output_node, args.output,
                                 args.endpoint, args.timeout, args.license, args.commercial_ok), indent=2))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Falha ComfyUI: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
