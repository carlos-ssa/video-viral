"""Execute the actual harness revision blocks on isolated files and stubbed render commands."""
import ast
from argparse import Namespace
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

REPO = Path(__file__).resolve().parents[2]
tree = ast.parse((REPO / 'tests/validation_productions.py').read_text(encoding='utf-8'))
main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')

def revision_block(name):
    node = next(n for n in main.body if isinstance(n, ast.If)
                and isinstance(n.test, ast.Attribute) and n.test.attr == name)
    return compile(ast.fix_missing_locations(ast.Module(body=[copy.deepcopy(node)], type_ignores=[])),
                   'actual-harness-' + name, 'exec')

results = {}
with tempfile.TemporaryDirectory(prefix='independent-harness-final-') as temp:
    root = Path(temp)
    for slug in ('product', 'recording'):
        p = root / slug
        for folder in ('composition/assets', 'research', 'render', 'edit'):
            (p / folder).mkdir(parents=True, exist_ok=True)
        source = '<style>initial</style><div id="progress"></div><script>window.__timelines.main=tl;</script>'
        if slug == 'recording':
            source += '<video src="assets/aroll.mp4"></video>'
        (p / 'composition/index.html').write_text(source, encoding='utf-8')
        (p / 'video.json').write_text(json.dumps({'direction': {}, 'captions': {}}), encoding='utf-8')
        (p / 'edit/edl.json').write_text('{"fit":"crop"}', encoding='utf-8')
        (p / 'render/master.mp4').write_bytes(b'original-r01-master')
        final = p / 'final.mp4'
        final.write_bytes(b'draft-final-fixture')
        case = {'slug': slug, 'revision': 2, 'final': str(final)}
        calls = []
        fail = [True]

        def script(name, *args, **kw):
            calls.append(name)
            if name.startswith('recording-r03-base'):
                (p / 'render/master.mp4').write_bytes(b'correct-r03-aroll-with-audio')
            if name == slug + '-r03-render' and fail[0]:
                fail[0] = False
                raise RuntimeError('simulated render failure after preparation')
            return subprocess.CompletedProcess([], 0, '', '')

        env = dict(args=Namespace(revision3=True, long_r03=False, node_root=root), cases=[case],
                   out=root, rows=[], shutil=shutil, json=json, hashlib=hashlib, Path=Path,
                   script=script, hf=lambda *a, **kw: None, save=lambda: None)
        block = revision_block('revision3')
        try:
            exec(block, env)
        except RuntimeError as exc:
            assert 'simulated render' in str(exc)
        else:
            raise AssertionError('fixture did not reach simulated failure')
        first_html = (p / 'composition/index.html').read_bytes()
        first_backup = (p / 'research/index-r02.html').read_bytes()
        first_base = (p / 'render/aroll-r03.mp4').read_bytes() if slug == 'recording' else None
        exec(block, env)
        assert (p / 'composition/index.html').read_bytes() == first_html
        assert (p / 'research/index-r02.html').read_bytes() == first_backup
        assert case['revision'] == 3
        item = {'retry_html_identical': True, 'r02_backup_preserved': True, 'completed_revision': 3}
        if slug == 'product':
            assert first_html.count(b'const timer=') == 1
            item['timer_declarations'] = 1
        else:
            assert (p / 'render/aroll-r03.mp4').read_bytes() == first_base == b'correct-r03-aroll-with-audio'
            assert (p / 'render/master.mp4').read_bytes() == b'original-r01-master'
            assert sum(n.startswith('recording-r03-base') for n in calls) == 1
            item.update(aroll_preserved=True, original_master_preserved=True, base_calls=1)
        results[slug] = item
        # Execute the real r02 block on completed r03. No command or file operation may occur.
        before = list(calls)
        env['args'].revision2 = True
        exec(revision_block('revision2'), env)
        assert calls == before and case['revision'] == 3
        item['r02_skips_completed_r03'] = True

# Execute the actual first loudness parsing assignment with a cached run result.
parse = next(n for n in ast.walk(main) if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == 'blocks' for t in n.targets))
env = {'re': re, 'r': subprocess.CompletedProcess([], 0, '{"input_i":"-14.0"}', '')}
exec(compile(ast.fix_missing_locations(ast.Module(body=[copy.deepcopy(parse)], type_ignores=[])),
             'actual-harness-loudness', 'exec'), env)
assert json.loads(env['blocks'][-1])['input_i'] == '-14.0'
results['cached_loudness_stdout_parsed'] = True
print(json.dumps(results, indent=2))
