"""ACE-Step 1.5 ou --backend procedural (cama instrumental simples de reserva, sem modelo/prompt)."""
import argparse
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import add_asset, load_manifest, project_dir, save_manifest

MAX_DOWNLOAD = 100 * 1024 * 1024
MAX_JSON = 1024 * 1024


class MusicError(Exception):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def origin(url):
    p = urllib.parse.urlsplit(url)
    if p.scheme not in ('http', 'https') or not p.hostname or p.username is not None or p.password is not None:
        raise MusicError('URL HTTP(S) inválida')
    try:
        return p.scheme, p.hostname.lower(), p.port or (443 if p.scheme == 'https' else 80)
    except ValueError as exc:
        raise MusicError('Porta inválida') from exc


def procedural_audio(duration, seed):
    """Cama tonal simples de reserva, sem voz/modelo nem interpretação do prompt."""
    import array
    import io
    import wave
    rate = 22050
    frames = round(duration * rate)
    root = 45 + seed % 7
    samples = array.array('h')
    chords = [[440 * 2 ** ((root + chord + interval - 69) / 12) for interval in (0, 12, 15, 19)]
              for chord in (0, 5, 3, 7)]
    for i in range(frames):
        t = i / rate
        freqs = chords[int(t / 4) % 4]
        envelope = min(t / 0.3, (duration - t) / 0.5, 1) * (0.8 + 0.2 * math.cos(2 * math.pi * t / 2))
        # Transição suave entre acordes; pico sempre abaixo de -12 dBFS.
        envelope *= min((t % 4) / 0.08, (4 - t % 4) / 0.08, 1)
        value = sum(math.sin(2 * math.pi * f * t) for f in freqs) * 0.055 * envelope
        samples.append(round(32767 * value))
    if sys.byteorder != 'little':
        samples.byteswap()
    stream = io.BytesIO()
    with wave.open(stream, 'wb') as wav:
        wav.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        wav.writeframes(samples.tobytes())
    return stream.getvalue()


def run(args):
    backend = getattr(args, 'backend', 'ace-step')
    if backend == 'ace-step' and not args.endpoint:
        raise MusicError('Sem ACE-Step: use --backend procedural para uma cama instrumental simples de reserva (não interpreta o prompt).')
    base = (args.endpoint or 'http://127.0.0.1').rstrip('/')
    parsed = urllib.parse.urlsplit(base)
    base_origin = origin(base)
    if parsed.path not in ('', '/') or parsed.query or parsed.fragment:
        raise MusicError('Endpoint deve conter apenas a origem')
    if (backend == 'ace-step' and not args.prompt.strip()) or not math.isfinite(args.duration) or not 10 <= args.duration <= 600:
        raise MusicError('Prompt obrigatório para ACE-Step; duração deve estar entre 10 e 600 segundos')
    if not 0 <= args.seed <= 2**32 - 1:
        raise MusicError('Seed deve estar entre 0 e 4294967295')
    if not math.isfinite(args.timeout) or not 0 < args.timeout <= 3600:
        raise MusicError('Timeout deve estar entre 0 e 3600 segundos')
    if backend == 'ace-step' and args.commercial_ok and not args.license.strip():
        raise MusicError('Uso comercial exige licença informada')
    proj = project_dir(args.projeto)
    rel = Path(args.output)
    if rel.is_absolute() or not rel.parts or rel.suffix.lower() != '.wav':
        raise MusicError('Saída deve ser um caminho WAV relativo ao projeto')
    out = (proj / rel).resolve()
    if not out.is_relative_to(proj) or out == proj or out == (proj / 'video.json').resolve() or out == (proj / 'short.json').resolve():
        raise MusicError('Saída fora do projeto')
    m = load_manifest(proj)
    if not isinstance(m, dict) or not isinstance(m.get('assets', []), list) or any(not isinstance(x, dict) for x in m.get('assets', [])):
        raise MusicError('Manifesto inválido')
    asset_path = out.relative_to(proj).as_posix()
    add_asset(m, asset_path, 'audio', 'ACE-Step 1.5 API (gerado; serviço informado pelo usuário)', args.license.strip() or 'não informada', bool(args.commercial_ok))
    if backend == 'procedural':
        asset = next(x for x in m['assets'] if x['path'] == asset_path)
        asset.update(source='síntese procedural simples (reserva; não é ACE-Step)',
                     license='síntese original sem samples externos', commercial_ok=True,
                     fallback=True, backend='procedural', seed=args.seed, duration=args.duration,
                     note='Cama instrumental tonal; prompt não interpretado; sem aprovação estética.')
        publish_audio(out, proj, m, procedural_audio(args.duration, args.seed))
        print('RESERVA procedural: cama instrumental simples; não interpreta o prompt e não substitui música dirigida.')
        return
    opener = urllib.request.build_opener(NoRedirect())
    headers = {'Accept': 'application/json'}
    key = os.environ.get('ACE_STEP_API_KEY')
    if key:
        headers['Authorization'] = 'Bearer ' + key
    deadline = time.monotonic() + args.timeout

    def request(url, body=None, limit=MAX_JSON):
        if origin(url) != base_origin:
            raise MusicError('Download fora da origem configurada')
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise MusicError('Tempo limite excedido')
        h = dict(headers)
        data = None
        if body is not None:
            data = json.dumps(body).encode('utf-8')
            h['Content-Type'] = 'application/json'
        try:
            with opener.open(urllib.request.Request(url, data=data, headers=h), timeout=min(remaining, 30)) as response:
                chunks = []
                size = 0
                while True:
                    if time.monotonic() >= deadline:
                        raise MusicError('Tempo limite excedido')
                    chunk = response.read(min(65536, limit + 1 - size))
                    if not chunk:
                        break
                    size += len(chunk)
                    if size > limit:
                        raise MusicError('Resposta excede o limite')
                    chunks.append(chunk)
                return b''.join(chunks)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            raise MusicError('Falha de rede ou timeout na API') from exc

    def post(path, body):
        try:
            result = json.loads(request(base + path, body))
            if not isinstance(result, dict) or result.get('code') != 200 or result.get('error') is not None or 'data' not in result:
                raise MusicError('Resposta de erro ou incompleta da API')
            return result['data']
        except (ValueError, UnicodeError) as exc:
            raise MusicError('JSON inválido da API') from exc

    submitted = post('/release_task', {'prompt': args.prompt, 'audio_duration': args.duration, 'seed': args.seed, 'use_random_seed': False, 'audio_format': 'wav', 'batch_size': 1})
    if not isinstance(submitted, dict) or not isinstance(submitted.get('task_id'), str) or not submitted['task_id'].strip():
        raise MusicError('Resposta de criação sem task_id')
    task = submitted['task_id']
    file_url = None
    for _ in range(600):
        data = post('/query_result', {'task_id_list': [task]})
        if not isinstance(data, list) or len(data) != 1 or not isinstance(data[0], dict) or data[0].get('task_id') != task:
            raise MusicError('Resposta de consulta incompleta')
        item = data[0]
        status = item.get('status')
        if type(status) is not int or status not in (0, 1, 2):
            raise MusicError('Status inválido')
        if status == 2:
            raise MusicError('Geração falhou no servidor')
        if status == 1:
            try:
                results = json.loads(item['result'])
                first = results[0]
                if not isinstance(first, dict) or type(first.get('status')) is not int or first['status'] != 1 or not isinstance(first.get('file'), str) or not first['file'].strip():
                    raise ValueError()
                file_url = first['file']
            except (KeyError, TypeError, ValueError, IndexError) as exc:
                raise MusicError('Resultado de sucesso incompleto') from exc
            break
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise MusicError('Tempo limite excedido')
        time.sleep(min(1, remaining))
    if file_url is None:
        raise MusicError('Limite de consultas excedido')
    # Apenas URLs do endpoint de áudio; um caminho do servidor nunca é aberto localmente.
    url = urllib.parse.urljoin(base + '/', file_url)
    p = urllib.parse.urlsplit(url)
    if origin(url) != base_origin or p.path != '/v1/audio' or not p.query or p.fragment:
        raise MusicError('URL de áudio inválida ou fora da origem')
    audio = request(url, limit=MAX_DOWNLOAD)
    if len(audio) < 12 or audio[:4] != b'RIFF' or audio[8:12] != b'WAVE':
        raise MusicError('Download não é WAV válido')
    publish_audio(out, proj, m, audio)


def publish_audio(out, proj, m, audio):
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    previous = out.read_bytes() if out.exists() else None
    try:
        with tempfile.NamedTemporaryFile(dir=out.parent, delete=False) as f:
            tmp = Path(f.name)
            f.write(audio)
        tmp.replace(out)
        tmp = None
        try:
            save_manifest(proj, m)
        except Exception:
            if previous is None:
                out.unlink(missing_ok=True)
            else:
                out.write_bytes(previous)
            raise
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)
    print(f'Áudio salvo em {out}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('projeto')
    parser.add_argument('--backend', choices=['ace-step', 'procedural'], default='ace-step',
                        help='procedural: cama instrumental simples de reserva, sem interpretar prompt')
    parser.add_argument('--endpoint', help='Origem da API ACE-Step; dispensada com --backend procedural')
    parser.add_argument('--prompt', default='', help='Direção musical para ACE-Step; não interpretada pela reserva procedural')
    parser.add_argument('--duration', required=True, type=float)
    parser.add_argument('--seed', required=True, type=int)
    parser.add_argument('--output', default='audio/music.wav')
    parser.add_argument('--timeout', type=float, default=600)
    parser.add_argument('--license', default='')
    parser.add_argument('--commercial-ok', action='store_true', help='Confirma que a licença informada permite uso comercial')
    args = parser.parse_args()
    try:
        run(args)
    except (MusicError, OSError, ValueError) as exc:
        print(f'Erro: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
