"""Five offline representative technical productions, not finished creative work.

Run with --output NEW_DIRECTORY --node-root EXISTING_NODE_ROOT. Inherits and
never removes VIDEO_VIRAL_NO_INSTALL. No installers, TTS service or publication.
"""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--node-root', type=Path, required=True)
    ap.add_argument('--resume', action='store_true', help='Continue failed run, preserving successful commands and failure logs')
    ap.add_argument('--revision2', action='store_true', help='Apply independently requested title/framing/illustration corrections')
    ap.add_argument('--revision3', action='store_true', help='Add reviewer-requested recognizable product and narration diagrams')
    ap.add_argument('--long-style-only', action='store_true', help='Prepare and snapshot long r03 before rendering')
    ap.add_argument('--long-r03', action='store_true', help='Render prepared long r03 after inspecting its style snapshots')
    args = ap.parse_args()
    out = args.output.resolve()
    if out.exists() and not args.resume:
        ap.error('Use a new output directory; evidence is never overwritten.')
    out.mkdir(parents=True, exist_ok=args.resume)
    env = dict(os.environ)
    browser = env.get('VIDEO_VIRAL_BROWSER_PATH') or r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    if not Path(browser).is_file():
        ap.error('Existing local Chrome required; no download is allowed.')
    env.update(HYPERFRAMES_BROWSER_PATH=browser, VIDEO_VIRAL_BROWSER_PATH=browser,
               HYPERFRAMES_CACHE_DIR=str(out / 'hf-cache'), DO_NOT_TRACK='1',
               HYPERFRAMES_NO_UPDATE_CHECK='1', HYPERFRAMES_NO_AUTO_INSTALL='1')
    previous=json.loads((out/'results.json').read_text(encoding='utf-8')) if args.resume else {}
    rows, cases = previous.get('commands',[]), previous.get('cases',[])

    def save():
        (out / 'results.json').write_text(json.dumps({'commands': rows, 'cases': cases,
            'no_install_inherited': os.environ.get('VIDEO_VIRAL_NO_INSTALL'),
            'perceptual_approval': False}, ensure_ascii=False, indent=2), encoding='utf-8')

    def run(name, cmd, allowed=(0,), timeout=900):
        command=list(map(str,cmd))
        for old in rows:
            if args.resume and old['step']==name and old['exit_code']==0 and old['command']==command:
                return subprocess.CompletedProcess(command,0,Path(old['log']).read_text(encoding='utf-8'),'')
        started = time.perf_counter()
        p = subprocess.run(list(map(str, cmd)), cwd=ROOT, env=env, capture_output=True,
                           text=True, encoding='utf-8', errors='replace', timeout=timeout)
        log = out / (name + '.log')
        if log.exists():
            log=out/(name+f'-attempt{1+sum(x["step"]==name for x in rows)}.log')
        log.write_text(p.stdout + p.stderr, encoding='utf-8')
        rows.append({'step': name, 'command': list(map(str, cmd)), 'exit_code': p.returncode,
                     'seconds': round(time.perf_counter()-started, 3), 'log': str(log)})
        save()
        if re.search(r'Downloading (?:Chrome|browser|font)|Fetching browser', p.stdout+p.stderr, re.I):
            raise RuntimeError('Unexpected download attempt; stop, do not retry: ' + str(log))
        if p.returncode not in allowed:
            raise RuntimeError(f'{name} returned {p.returncode}: {log}')
        return p

    def script(name, *tail, allowed=(0,)):
        return run(name, [PY, ROOT / 'scripts' / (tail[0]+'.py'), *tail[1:]], allowed)

    def hf(name, *tail, allowed=(0,)):
        return script(name, 'stack', 'hyperframes', '--node-root', args.node_root, '--', *tail, allowed=allowed)

    def probe(path):
        p = subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],
                           capture_output=True, text=True, check=True)
        return json.loads(p.stdout)

    fontdir = args.node_root / 'node_modules/hyperframes/dist/skills/hyperframes/assets/frame-presets/code-editorial/fonts'
    fixture = ROOT / 'evals/editar-gravacao-propria/files'
    longfixture = ROOT / 'evals/cortes-de-video-longo/files'
    hf('hyperframes-version', '--version')
    run('ffmpeg-version', ['ffmpeg', '-version'])
    specs = [
        ('narrated','narrado',14,(360,640),['Gastos invisíveis','Revise suas assinaturas','Observe o seu extrato']),
        ('product','produto',12,(360,640),['Foco em uma tarefa','Organize o próximo passo','Conceito de temporizador']),
        ('recording','gravacao',47,(360,640),['Três gastos invisíveis','Assinaturas e taxas','Revise o seu orçamento']),
        ('story','storytelling',12,(360,640),['Uma ideia começa pequena','Cada passo abre um caminho','O próximo passo é seu']),
        ('long','gravacao',181,(640,360),['01 · A pergunta','02 · A demonstração','03 · A conclusão'])]
    for slug, kind, duration, size, titles in specs:
        if any(c['slug']==slug for c in cases):
            continue
        script(slug+'-create','new_project',slug,'--format',kind,'--seconds',duration,
               '--aspect','16:9' if slug=='long' else '9:16','--dir',out)
        p = out / slug
        manifest_path = p / 'video.json'
        m = json.loads(manifest_path.read_text(encoding='utf-8'))
        m.update(title='Validação técnica: '+slug, size=list(size), fps=15, platforms=['youtube'] if slug=='long' else ['reels'])
        m['brief'].update(objective='entretenimento', audience='Revisores técnicos da skill',
            problem_or_desire='Validar o fluxo local de composição', benefit='Artefatos reais reproduzíveis',
            desired_action='Inspecionar e registrar limites', offer='Conceito fictício sem venda',
            assumptions=['Demonstração técnica; sem alegação de acabamento profissional ou performance',
                         'Resolução reduzida explícita para limitar tempo/custo; 15 fps'], missing_inputs=[])
        m['hook_candidates']=[{'text':t, 'visual':'Composição original local', 'hypothesis':True} for t in titles+['Veja o processo','Uma pequena mudança']]
        m['hook']=titles[0]
        m['cta']='Inspecione o projeto e as evidências'
        m['direction'].update(style='Demonstração técnica editorial', palette=['#101629','#f4f7ff','#63e6b0'],
            fonts={'title':'ValidationInter','body':'ValidationInter','captions':'Arial'},
            motion='GSAP determinístico; mudanças de cena e progressão contínua')
        m['tool_plan']=[{'tool':tool,'module':mod,'status':'planejado','input':inp,'output':output}
            for tool,mod,inp,output in [('HyperFrames','hyperframes','composition/index.html','render/master.mp4'),
            ('GSAP','gsap','timeline','HTML determinístico'),('FFmpeg','ffmpeg','master + áudio + ASS','out/'),
            ('Música procedural','ace-step','seed 7','audio/music.wav')]]
        m['scenes']=[{'id':f's{i+1:02}', 'narration':'', 'on_screen':t,
            'visual':{'engine':'hyperframes','brief':t,'shots':[],'transition_out':'cut'},
            'start':round(i*duration/3,3),'duration':round(duration/3,3)} for i,t in enumerate(titles)]
        m['captions'].update(size=22 if slug!='long' else 16, words_per_group=6, max_cps=30)
        retained=[a for a in m.get('assets',[]) if a.get('kind')!='font'] if args.resume else []
        m['assets']=retained+[{'path':'composition/assets/Inter-700.woff2','kind':'font','source':str(fontdir),
            'license':'Bundled font; OFL file copied for review, terms not independently verified','commercial_ok':False}]
        manifest_path.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
        script(slug+'-plan','plan',p)
        media = slug in ('recording','long')
        if media:
            src = (longfixture/'gravacao_longa.mp4') if slug=='long' else (fixture/'gravacao.mp4')
            srt = (longfixture/'gravacao_longa.srt') if slug=='long' else (fixture/'gravacao.srt')
            script(slug+'-import','footage','import',p,src,'--to',duration)
            script(slug+'-captions-import','captions','import',p,'--file',srt)
            if slug=='long':
                # Unedited source timeline: explicit target avoids source/EDL remap mode.
                script(slug+'-captions-timeline','captions','import',p,'--file',srt,
                       '--out','captions/words.json')
            if slug=='recording':
                script(slug+'-cut','footage','cut',p,'--no-zoom')
                script(slug+'-base','footage','render',p)
                shutil.move(p/'render/master.mp4',p/'render/aroll.mp4')
                duration=float(probe(p/'render/aroll.mp4')['format']['duration'])
            else:
                run(slug+'-base',['ffmpeg','-y','-v','error','-i',src,'-t',duration,'-vf',f'scale={size[0]}:{size[1]},fps=15',
                    '-c:v','libx264','-preset','fast','-c:a','aac',p/'render/aroll.mp4'])
        if slug=='narrated':
            # Supplied fixture audio, not synthesized speech and not a new narration claim.
            run(slug+'-wav',['ffmpeg','-y','-v','error','-i',fixture/'gravacao.mp4','-t',duration,
                '-vn','-ar','48000','-ac','1',p/'audio/voice.wav'])
            script(slug+'-captions-import','captions','import',p,'--file',fixture/'gravacao.srt')
        m=json.loads(manifest_path.read_text(encoding='utf-8'))
        m['target_seconds']=duration
        for i,sc in enumerate(m['scenes']):
            sc.update(start=round(i*duration/3,3),duration=round(duration/3,3))
        if media or slug=='narrated':
            for a in m['assets']:
                if a.get('kind')!='font':
                    a.update(license='Repository test fixture; independent commercial terms not verified',commercial_ok=False)
            if slug=='narrated':
                m['assets'].append({'path':'audio/voice.wav','kind':'voice','source':'Repository recording fixture, first 14 s',
                    'license':'Test fixture; commercial terms not verified','commercial_ok':False})
        manifest_path.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
        if media or slug=='narrated':
            script(slug+'-ass','captions','ass',p)
        script(slug+'-music','music',p,'--backend','procedural','--duration',max(10,duration),'--seed',7)
        comp=p/'composition'; assets=comp/'assets'; assets.mkdir(parents=True,exist_ok=True)
        shutil.copy2(args.node_root/'node_modules/gsap/dist/gsap.min.js',assets/'gsap.min.js')
        shutil.copy2(fontdir/'Inter-700.woff2',assets/'Inter-700.woff2')
        shutil.copy2(fontdir/'OFL-inter.txt',assets/'OFL-inter.txt')
        if media: shutil.copy2(p/'render/aroll.mp4',assets/'aroll.mp4')
        w,h=size
        stage = f'<video id="aroll" class="clip" src="assets/aroll.mp4" data-start="0" data-duration="{duration}" data-track-index="0" muted playsinline></video>' if media else '<div id="orb"></div><div id="path"></div>'
        scene_html=''.join(f'<div id="scene{i}" class="clip scene" data-start="{i*duration/3}" data-duration="{duration/3}" data-track-index="1"><div class="title">{html.escape(t)}</div></div>' for i,t in enumerate(titles))
        css=f'''@font-face{{font-family:ValidationInter;src:url(assets/Inter-700.woff2);font-weight:700}}html,body{{margin:0;background:#101629}}#main{{width:{w}px;height:{h}px;position:relative;overflow:hidden;background:radial-gradient(ellipse at 70% 40%,#225c61,#101629 70%);color:#f4f7ff;font-family:ValidationInter}}video{{width:100%;height:100%;object-fit:cover}}.scene{{position:absolute;left:9%;top:12%;width:76%}}.title{{font-size:{26 if h>w else 28}px;line-height:1.2;background:#101629e8;padding:12px;border-left:4px solid #63e6b0}}#orb{{position:absolute;width:{w*.55}px;height:{w*.55}px;border-radius:{'16%' if slug=='product' else '50%'};background:linear-gradient(135deg,#63e6b0,#258cb0);top:36%;left:20%;box-shadow:0 0 80px #63e6b044}}#path{{position:absolute;left:15%;top:35%;width:65%;height:38%;border:3px solid #63e6b077;border-radius:50%}}#progress{{position:absolute;bottom:10%;left:9%;height:4px;width:76%;background:#63e6b0;transform-origin:left}}#label{{position:absolute;left:9%;bottom:15%;font-size:11px}}'''
        js=f'''window.__timelines={{}};const tl=gsap.timeline({{paused:true}});tl.fromTo('#progress',{{scaleX:0}},{{scaleX:1,duration:{duration},ease:'none'}},0);'''
        if not media: js+=f"tl.fromTo('#orb',{{x:-20,rotation:0}},{{x:30,rotation:160,duration:{duration},ease:'none'}},0);"
        for i in range(3): js+=f"tl.fromTo('#scene{i} .title',{{y:18,opacity:0}},{{y:0,opacity:1,duration:.5}}, {i*duration/3});"
        js+='window.__timelines.main=tl;'
        (comp/'index.html').write_text(f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{css}</style></head><body><div id="main" data-composition-id="main" data-start="0" data-width="{w}" data-height="{h}" data-duration="{duration}" data-fps="15">{stage}{scene_html}<div id="progress"></div><div id="label">DEMONSTRAÇÃO TÉCNICA · {slug.upper()}</div></div><script src="assets/gsap.min.js"></script><script>{js}</script></body></html>',encoding='utf-8')
        hf(slug+'-lint','lint',comp,allowed=(0,1))
        hf(slug+'-check','check',comp,allowed=(0,1))
        r=hf(slug+'-render','render',comp,'--output',p/'render/master.mp4','--fps','15','--workers','1','--quality','draft',allowed=(0,1))
        if r.returncode:
            script(slug+'-render-screenshot','stack','hyperframes','--node-root',args.node_root,
                '--screenshot','--','render',comp,'--output',p/'render/master.mp4',
                '--fps','15','--workers','1','--quality','draft')
        info=probe(p/'render/master.mp4')
        (p/'render/ffprobe.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
        # Preserve ordinary default mix as baseline, then compare actual delivered loudness.
        baseline=p/'audio/baseline-mix.wav'
        dry_voice=(p/'render/aroll.mp4') if media else (p/'audio/voice.wav')
        if dry_voice.exists():
            run(slug+'-baseline',['ffmpeg','-y','-v','error','-i',dry_voice,'-i',p/'audio/music.wav',
                '-filter_complex','[1:a]volume=-16dB[m];[0:a][m]amix=inputs=2:normalize=0[a]', '-map','[a]','-t',duration,baseline])
        else: shutil.copy2(p/'audio/music.wav',baseline)
        delivery=script(slug+'-deliver','deliver',p,'--video','render/master.mp4','--draft',
            *(['--voice',p/'render/aroll.mp4'] if media else []), allowed=(0,1))
        script(slug+'-review','review',p,'--producer-id','validation:productions',allowed=(0,1))
        script(slug+'-verdict','review',p,'--verdict',allowed=(1,2))
        final=next((p/'out').glob('*.mp4'))
        measures={}
        for label,path in [('baseline',baseline),('delivered',final)]:
            r=run(slug+'-loudness-'+label,['ffmpeg','-hide_banner','-nostats','-i',path,'-af','loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
            blocks=re.findall(r'\{[^{}]*\}',r.stderr or r.stdout,re.S)
            measures[label]=json.loads(blocks[-1])
        cases.append({'slug':slug,'duration':duration,'size':size,'fps':15,'master':str(p/'render/master.mp4'),
            'final':str(final),'sha256':hashlib.sha256(final.read_bytes()).hexdigest(),
            'loudness':measures,'delivery_exit':delivery.returncode,'independent_review':'pending'})
        save()
    if args.long_style_only:
        p=out/'long'; page=p/'composition/index.html'; backup=p/'research/index-r02.html'
        if not backup.exists():
            shutil.copy2(page,backup)
        source=backup.read_text(encoding='utf-8')
        style='.scene{left:5%;top:18%;width:36%}.title{font-size:20px;line-height:1.2;padding:10px}#label{left:5%;top:52%;bottom:auto;width:34%;font-size:9px}'
        if style not in source:
            source=source.replace('</style>',style+'</style>')
        source=source.replace('Resultado: o valor dobra · exemplo ilustrativo','Exemplo didático<br>resultado em dobro')
        page.write_text(source,encoding='utf-8')
        (p/'research/index-r03-prepared.html').write_text(source,encoding='utf-8')
        mpath=p/'video.json'; m=json.loads(mpath.read_text(encoding='utf-8'))
        m['direction']['style']='R03 longo: título na coluna livre esquerda x32–262, y65–157; label x32–249/y187; rosto fonte à direita e timecode topo livres'
        m['scenes'][-1]['on_screen']='Exemplo didático / resultado em dobro'
        mpath.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
        hf('long-r03-style-check','check',p/'composition')
        hf('long-r03-style-snapshots','snapshot',p/'composition','--at','0,90,150,183.533','--no-end',
           '--output',p/'research/style-r03')
        return
    if args.revision2:
        for c in cases:
            if c.get('revision',1)>=2:
                continue
            p=out/c['slug']; comp=p/'composition'; page=comp/'index.html'
            if (comp/'index-r01.html').exists():
                shutil.move(comp/'index-r01.html',p/'research/index-r01-legacy.html')
            source=page.read_text(encoding='utf-8')
            if c['slug']=='long':
                # End at the supplied SRT sentence boundary (183.517), not mid-speech at 181.
                extended=183.6
                replacement=p/'render/aroll-r02.mp4'
                run('long-r02-source-sentence',['ffmpeg','-y','-v','error','-i',longfixture/'gravacao_longa.mp4',
                    '-t',extended,'-vf','scale=640:360,fps=15','-c:v','libx264','-preset','fast','-c:a','aac',replacement])
                shutil.copy2(replacement,comp/'assets/aroll-r02.mp4')
                source=source.replace('assets/aroll.mp4','assets/aroll-r02.mp4')
                source=re.sub(r'data-duration="181(?:\.0)?"',f'data-duration="{extended}"',source)
                source=source.replace('duration:181,',f'duration:{extended},')
                source=re.sub(r'(id="scene2"[^>]*data-duration=")[^"]+',r'\g<1>62.934',source)
                source=source.replace('03 · A conclusão','Resultado: o valor dobra · exemplo ilustrativo')
                source=source.replace('bottom:15%;font-size:11px','top:4%;font-size:10px')
                source=source.replace('bottom:10%;left:9%;height:4px','bottom:3%;left:9%;height:4px')
                c['duration']=extended
                mpath=p/'video.json'; ml=json.loads(mpath.read_text(encoding='utf-8'))
                ml['source'].update(range=[0,extended],duration=extended)
                ml['target_seconds']=extended
                ml['scenes'][-1].update(duration=62.934,on_screen='Resultado: o valor dobra · exemplo ilustrativo')
                mpath.write_text(json.dumps(ml,ensure_ascii=False,indent=2),encoding='utf-8')
                script('long-r02-captions-import','captions','import',p,'--file',longfixture/'gravacao_longa.srt','--out','captions/words.json')
                script('long-r02-ass','captions','ass',p)
            source=re.sub(r"tl\.fromTo\('#scene\d \.title'.*?\);",'',source)
            source=source.replace('object-fit:cover','object-fit:contain')
            if c['slug']=='narrated':
                source=source.replace('Observe o seu extrato','Assinaturas · taxas · delivery')
            (p/'research/index-r01.html').write_text(page.read_text(encoding='utf-8'),encoding='utf-8')
            page.write_text(source,encoding='utf-8')
            mpath=p/'video.json'; m=json.loads(mpath.read_text(encoding='utf-8'))
            m['direction']['motion']='Revisão 2: títulos visíveis desde quadro 0 e nas fronteiras; mídia contain; progressão GSAP determinística'
            if c['slug']=='narrated':
                m['scenes'][-1]['on_screen']='Assinaturas · taxas · delivery'
            mpath.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
            script(c['slug']+'-r02-plan','plan',p)
            hf(c['slug']+'-r02-check','check',comp)
            master=p/'render/master-r02.mp4'
            script(c['slug']+'-r02-render','stack','hyperframes','--node-root',args.node_root,
                '--screenshot','--','render',comp,'--output',master,'--fps','15','--workers','1','--quality','draft')
            voice_source=p/'render/aroll-r02.mp4' if c['slug']=='long' else p/'render/aroll.mp4'
            r=script(c['slug']+'-r02-deliver','deliver',p,'--video',master,'--draft',
                *(['--voice',voice_source] if c['slug'] in ('recording','long') else []),allowed=(0,1))
            script(c['slug']+'-r02-review','review',p,'--producer-id','validation:productions',allowed=(0,1))
            script(c['slug']+'-r02-verdict','review',p,'--verdict',allowed=(1,2))
            c.update(revision=2,master=str(master),delivery_exit=r.returncode,
                sha256=hashlib.sha256(Path(c['final']).read_bytes()).hexdigest())
            save()
    if args.revision3:
        for c in cases:
            eligible=('narrated','product','recording','long') if args.long_r03 else ('narrated','product','recording')
            if c['slug'] not in eligible or c.get('revision')==3:
                continue
            if c.get('revision')!=2:
                raise RuntimeError('Revision 3 requires completed revision 2 evidence')
            p=out/c['slug']; comp=p/'composition'; page=comp/'index.html'
            backup=p/'research/index-r02.html'
            if not backup.exists():
                shutil.copy2(page,backup)
            stable=p/'research/index-r03-prepared.html' if c['slug']=='long' else backup
            if not stable.is_file():
                raise RuntimeError('Long r03 requires the inspected prepared HTML')
            source=stable.read_text(encoding='utf-8')
            extra_css='#orb,#path{display:none}.diagram{position:absolute;left:9%;width:76%;box-sizing:border-box;color:#f4f7ff}.demo-card{height:50px;background:#183c48;border:1px solid #63e6b0;border-radius:10px;display:flex;align-items:center;padding:8px;gap:10px}.demo-card svg{width:34px;height:34px;flex:none;stroke:#63e6b0;fill:none;stroke-width:2}.demo-card strong{display:block;font-size:17px}.demo-card small{font-size:10px;color:#d3e5e8}'
            if c['slug']=='long':
                if not (p/'research/style-r03').is_dir():
                    raise RuntimeError('Run --long-style-only and inspect its images before long r03 render')
                extra_css=''; diagrams=''
            elif c['slug']=='recording':
                edlpath=p/'edit/edl.json'; edlbackup=p/'research/edl-r02.json'
                if not edlbackup.exists():
                    shutil.copy2(edlpath,edlbackup)
                edl=json.loads(edlbackup.read_text(encoding='utf-8'))
                edl['fit']='blur'
                edlpath.write_text(json.dumps(edl,ensure_ascii=False,indent=2),encoding='utf-8')
                saved=p/'render/master-r01-preserved.mp4'
                base=p/'render/aroll-r03.mp4'
                if not saved.exists():
                    shutil.copy2(p/'render/master.mp4',saved)
                if not base.exists():
                    # A stable output is the cache key; never move a restored r01 master over it.
                    attempt=sum(r['step'].startswith('recording-r03-base') for r in rows)
                    try:
                        script('recording-r03-base'+(f'-recovery{attempt}' if attempt else ''),'footage','render',p)
                        shutil.move(p/'render/master.mp4',base)
                    finally:
                        shutil.copy2(saved,p/'render/master.mp4')
                shutil.copy2(base,comp/'assets/aroll-r03.mp4')
                source=source.replace('assets/aroll.mp4','assets/aroll-r03.mp4')
                diagrams=''
                mpath=p/'video.json'; m=json.loads(mpath.read_text(encoding='utf-8'))
                m['captions'].update(max_chars_per_line=22,max_lines=2,size=22)
                m['direction']['style']='Fixture completa no primeiro plano; fundo expandido pela rota oficial A-roll blur; sem reconstruir pixels ausentes'
                mpath.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
                script('recording-r03-ass','captions','ass',p)
            elif c['slug']=='narrated':
                diagrams=''
                icons=['<path d="M8 10a12 12 0 1 1-3 14M8 3v9H0"/>',
                       '<rect x="5" y="2" width="24" height="30" rx="2"/><path d="M10 9h14M10 16h14M10 23h10"/>',
                       '<path d="M3 10 17 3l14 7v19H3zM3 10h28M17 3v7M11 23l4 4 8-9"/>']
                for i,(name,hint) in enumerate([('Assinaturas','renovação recorrente'),('Taxas','movimentação do extrato'),('Delivery','pedido e comprovante')]):
                    at=8.4+i*.65
                    diagrams+=f'<div id="example{i}" class="clip diagram" data-start="{at}" data-duration="{14-at}" data-track-index="2" style="top:{30+i*9}%"><div class="demo-card"><svg viewBox="0 0 34 34">{icons[i]}</svg><div><strong>{name}</strong><small>{hint}</small></div></div></div>'
                mpath=p/'video.json'; m=json.loads(mpath.read_text(encoding='utf-8'))
                m['captions'].update(max_chars_per_line=22,max_lines=2,size=22)
                m['direction']['style']='Diagramas originais: recorrência, extrato e embalagem; demonstração técnica'
                mpath.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
                script('narrated-r03-ass','captions','ass',p)
            else:
                extra_css+='#timer-demo{text-align:center;top:31%;height:250px}#timer-demo svg{width:220px;height:220px;position:absolute;left:27px;top:0;transform:rotate(-90deg)}#clock{position:relative;display:block;font-size:50px;margin-top:65px}#timer-demo p{font-size:12px;margin:4px}#timer-demo button{background:#63e6b0;color:#101629;border:0;border-radius:8px;padding:7px 20px;font:700 14px ValidationInter}.timer-state{position:absolute;left:0;top:218px;width:100%;font-size:14px;color:#63e6b0}'
                diagrams='<div id="timer-demo" class="clip diagram" data-start="0" data-duration="12" data-track-index="2"><svg viewBox="0 0 220 220"><circle cx="110" cy="110" r="100" fill="none" stroke="#244751" stroke-width="7"/><circle id="timer-ring" cx="110" cy="110" r="100" fill="none" stroke="#63e6b0" stroke-width="7" stroke-dasharray="628.318"/></svg><strong id="clock">00:25</strong><p>Escrever o próximo parágrafo</p><button>Iniciar</button><p>Ilustração · tempo acelerado</p><div id="timer-ready" class="clip timer-state" data-start="0" data-duration="1" data-track-index="3">Pronto para começar</div><div id="timer-focus" class="clip timer-state" data-start="1" data-duration="10" data-track-index="3">Em foco</div><div id="timer-done" class="clip timer-state" data-start="11" data-duration="1" data-track-index="3">Tarefa concluída · exemplo</div></div>'
                timerjs="const timer={seconds:25};tl.to(timer,{seconds:0,duration:10,ease:'none',onUpdate:()=>{document.getElementById('clock').textContent='00:'+String(Math.ceil(timer.seconds)).padStart(2,'0');}},1);tl.fromTo('#timer-ring',{strokeDashoffset:0},{strokeDashoffset:628.318,duration:10,ease:'none'},1);"
                source=source.replace('window.__timelines.main=tl;',timerjs+'window.__timelines.main=tl;')
                mpath=p/'video.json'; m=json.loads(mpath.read_text(encoding='utf-8'))
                m['direction']['style']='Interface original fictícia de temporizador, anel, botão, tarefa e conclusão ilustrativos'
                mpath.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
            source=source.replace('</style>',extra_css+'</style>')
            source=source.replace('<div id="progress">',diagrams+'<div id="progress">')
            page.write_text(source,encoding='utf-8')
            hf(c['slug']+'-r03-check','check',comp)
            master=p/'render/master-r03.mp4'
            script(c['slug']+'-r03-render','stack','hyperframes','--node-root',args.node_root,
                '--screenshot','--','render',comp,'--output',master,'--fps','15','--workers','1','--quality','draft')
            r=script(c['slug']+'-r03-deliver','deliver',p,'--video',master,'--draft',
                *(['--voice',p/'render/aroll-r03.mp4'] if c['slug']=='recording' else ['--voice',p/'render/aroll-r02.mp4'] if c['slug']=='long' else []),allowed=(0,1))
            script(c['slug']+'-r03-review','review',p,'--producer-id','validation:productions',allowed=(0,1))
            script(c['slug']+'-r03-verdict','review',p,'--verdict',allowed=(1,2,3))
            c.update(revision=3,master=str(master),delivery_exit=r.returncode,
                sha256=hashlib.sha256(Path(c['final']).read_bytes()).hexdigest())
            save()
    # Compare the same source stems for footage, including on resumed older runs.
    for c in cases:
        if c['slug'] not in ('recording','long'):
            continue
        p=out/c['slug']; baseline=p/'audio/baseline-fullmix.wav'
        source=next((x for x in [p/'render/aroll-r03.mp4',p/'render/aroll-r02.mp4'] if x.exists()),p/'render/aroll.mp4')
        run(c['slug']+'-baseline-fullmix',['ffmpeg','-y','-v','error','-i',source,
            '-i',p/'audio/music.wav','-filter_complex',
            '[1:a]volume=-16dB[m];[0:a][m]amix=inputs=2:normalize=0[a]',
            '-map','[a]','-t',c['duration'],baseline])
        r=run(c['slug']+'-loudness-baseline-fullmix',['ffmpeg','-hide_banner','-nostats','-i',baseline,
            '-af','loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
        c['loudness']['baseline']=json.loads(re.findall(r'\{[^{}]*\}',r.stderr or r.stdout,re.S)[-1])
        c['baseline_reference']='aroll source audio + procedural bed -16dB, no normalization'
        save()
    for c in cases:
        p=out/c['slug']; revision=c.get('revision',1); stills=p/f'research/seek-r{revision:02}'
        old_entry=p/'composition/index-r01.html'
        if old_entry.exists():
            shutil.move(old_entry,p/'research/index-r01.html')
        if revision==2:
            hf(c['slug']+'-r02-final-check','check',p/'composition')
        hf(c['slug']+f'-seek-r{revision:02}','snapshot',p/'composition','--at','2,0,2','--no-end','--output',stills)
        decoded=[]
        for name in ('frame-00-at-2s.png','frame-02-at-2s.png'):
            decoded.append(subprocess.run(['ffmpeg','-v','error','-i',str(stills/name),
                '-frames:v','1','-f','rawvideo','-pix_fmt','rgba','pipe:1'],check=True,
                stdout=subprocess.PIPE).stdout)
        a,b=decoded
        c['seek_2_0_2']={'same_session':True,'decoded_pixels_equal':bool(a) and a==b,
            'changed_pixels':sum(a[i:i+4]!=b[i:i+4] for i in range(0,min(len(a),len(b)),4)),
            'rgba_sha256':[hashlib.sha256(x).hexdigest() for x in decoded],
            'scope':'Post-render technical regression, not perceptual approval or pre-render style approval'}
        measured=run(c['slug']+f'-loudness-final-r{revision:02}',['ffmpeg','-hide_banner','-nostats',
            '-i',c['final'],'-af','loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json','-f','null','-'])
        c['loudness']['delivered']=json.loads(re.findall(r'\{[^{}]*\}',measured.stderr or measured.stdout,re.S)[-1])
        save()
    report=['# Cinco produções técnicas representativas','',
        'Demos técnicas reproduzíveis, não peças acabadas. Sem aprovação audiovisual independente.',
        'Ambiente herdado: VIDEO_VIRAL_NO_INSTALL='+repr(os.environ.get('VIDEO_VIRAL_NO_INSTALL')),
        'Resolução reduzida e 15 fps explícitos; fontes/Chrome/GSAP locais; nenhuma instalação solicitada.',
        'Fixtures do repositório têm termos comerciais não verificados; entregas em rascunho. Música procedural é reserva, não ACE-Step.',
        '', '| Caso | Duração | Tamanho | LUFS baseline → entrega | Distância de -14 LUFS |',
        '|---|---:|---|---|---|']
    for c in cases:
        b=float(c['loudness']['baseline']['input_i']); d=float(c['loudness']['delivered']['input_i'])
        report.append(f"| {c['slug']} | {c['duration']:.3f}s | {c['size']} | {b:.2f} → {d:.2f} | {abs(b+14):.2f} → {abs(d+14):.2f} LU |")
    report += ['', 'Baseline: cama procedural original ou mix normal voz+cama a -16 dB, sem degradar o sinal. A comparação mede normalização, não qualidade perceptual nem eficiência.',
        f'Comandos exatos, códigos de saída, tempos e logs: `{out.name}/results.json`.',
        'Pendências: reprodução/escuta integral e avaliação independente, licenças comerciais e qualidade criativa. Nenhuma publicação realizada.']
    report += ['', '| Caso | Master atual | Entrega revisável | Rodada | Render atual | Deliver | Seek RGBA |',
        '|---|---|---|---|---:|---:|---|']
    for c in cases:
        revision=c.get('revision',1)
        render=next((r for r in reversed(rows) if r['step']==c['slug']+f'-r{revision:02}-render'),None)
        report.append(f"| {c['slug']} | `{c['master']}` | `{c['final']}` | r{revision:02} | {render['seconds'] if render else 'ver results.json'} s | {c['delivery_exit']} | {c.get('seek_2_0_2',{}).get('changed_pixels','pendente')} pixels diferentes |")
    report += ['', 'Reprodução completa em pasta nova:',
        f'`{PY} tests/validation_productions.py --output <pasta-nova> --node-root "{args.node_root}" --revision2 --revision3`',
        'Longo: acrescente uma execução `--resume --long-style-only`, inspecione os quatro PNGs de research/style-r03 e só então execute `--resume --revision3 --long-r03`; este harness não transforma a existência dos PNGs em aprovação visual automática.',
        '', 'Correções reais: títulos desde quadro 0 e transições; narrativa com diagramas próprios de assinatura/extrato/embalagem; temporizador fictício reconhecível; fonte da gravação integral no foreground; legenda por sentido em duas linhas para os curtos corrigidos; longo encerra frase do SRT em 183.517 s, com margem de 0.083 s e zonas separadas.',
        'Gravação: 47 s → 27.671 s por EDL; 15 trechos, 3 vícios isolados removidos. O crop inicial mostrava 404/1280 px da largura da fonte (31.56%); a rota fit:blur mantém 100% da fonte no primeiro plano. Isso mede enquadramento, não preservação semântica ou qualidade estética.',
        'Falhas preservadas: captura padrão drawElementImage → fallback oficial screenshot; import de SRT no timeline longo explicitado; backup HTML fora da raiz para evitar múltiplas composições. Inputs de rodadas anteriores permanecem imutáveis. Seek pós-render é regressão técnica. O longo r03 teve também snapshots 0/90/150/183.533 e inspeção estática do autor antes de renderizar; não comprova reprodução/escuta.',
        'Vereditos atuais: 2 (evidência independente audiovisual pendente); nenhum canal perceptual foi inventado. Os exemplos usam fixtures geométricas e áudio/SRT de teste, não material realista nem peça publicitária acabada.']
    proof_path=out/'resume-proof.json'
    if proof_path.is_file():
        proof=json.loads(proof_path.read_text(encoding='utf-8'))
        report+=['',f"Retomada real repetindo --resume --revision2 --revision3 --long-r03: exit {proof['exit_code']}, {proof['seconds']:.3f} s; {len(proof['before']['hashes'])} hashes de finais/inputs iguais; renders {proof['before']['render_commands']} → {proof['after']['render_commands']}; rodadas {len(proof['before']['rounds'])} → {len(proof['after']['rounds'])}. Evidência: `{out.name}/resume-proof.json`. Mede reuso de resultados existentes, não aceleração de produção nova."]
    (out.parent/'audit-productions.md').write_text('\n'.join(report),encoding='utf-8')


if __name__=='__main__':
    main()
