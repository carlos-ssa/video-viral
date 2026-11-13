#!/usr/bin/env node
import { copyFile, mkdir, readdir, readFile, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { bundle, nodeRootFrom, packageEntry } from './_node.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const modules = { pixi: 'pixi.js', paper: 'paper', p5: 'p5', 'gl-transitions': 'gl-transitions' };

export async function generate(options) {
  const { module: name, output } = options;
  if (!Object.hasOwn(modules, name)) throw new Error('--module must be pixi, paper, p5 or gl-transitions');
  if (!output) throw new Error('--output is required');
  const width = Number(options.width ?? 720), height = Number(options.height ?? 1280);
  const duration = Number(options.duration ?? 4), seed = Number(options.seed ?? 1);
  if (![width, height].every(n => Number.isInteger(n) && n > 0 && n <= 8192) || !Number.isFinite(duration) || duration <= 0 || !Number.isFinite(seed)) throw new Error('Invalid width, height, duration or seed');
  const images = [options['image-a'], options['image-b']];
  if (images.some(Boolean)) {
    if (name !== 'gl-transitions' || !images.every(Boolean)) throw new Error('Use both --image-a and --image-b with gl-transitions');
    for (const image of images) {
      if (!['.png', '.jpg', '.jpeg', '.webp'].includes(path.extname(image).toLowerCase()) || !(await stat(image)).isFile())
        throw new Error('Transition inputs must be PNG/JPEG/WebP files');
    }
  }
  const nodeRoot = nodeRootFrom(options['node-root']);
  for (const pkg of [modules[name], 'gsap', 'esbuild']) packageEntry(pkg, nodeRoot);
  const packageVersion = JSON.parse(await readFile(path.join(nodeRoot, 'node_modules', modules[name], 'package.json'), 'utf8')).version;
  const destination = path.resolve(output);
  try {
    const info = await stat(destination);
    if (!info.isDirectory() || (await readdir(destination)).length) throw new Error('Output must be a new or empty directory');
  } catch (error) { if (error.code !== 'ENOENT') throw error; }
  await mkdir(path.join(destination, 'assets'), { recursive: true });
  const assets = path.join(destination, 'assets');
  await copyFile(path.join(here, '..', 'assets', 'integrations', 'visuals', `${name}.js`), path.join(assets, 'adapter.js'));
  const params = { width, height, duration, seed };
  if (images.every(Boolean)) {
    for (let index = 0; index < images.length; index++) {
      const filename = `${index ? 'to' : 'from'}${path.extname(images[index]).toLowerCase()}`;
      await copyFile(images[index], path.join(assets, filename));
      params[index ? 'imageB' : 'imageA'] = `assets/${filename}`;
    }
  }
  await writeFile(path.join(assets, 'scene-entry.js'), `import { createScene } from './adapter.js';\nimport { gsap } from 'gsap';\nconst params = ${JSON.stringify(params)};\nwindow.__timelines = window.__timelines || {};\nlet currentTime = 0;\nconst clock = { get time() { return currentTime; }, set time(value) { currentTime = value; window.__moduleScene?.drawAt(value); } };\nconst timeline = gsap.timeline({ paused: true });\ntimeline.to(clock, { time: params.duration, duration: params.duration, ease: 'none' });\nwindow.__timelines.main = timeline;\nwindow.__moduleReady = createScene(document.getElementById('visual'), params).then(scene => { window.__moduleScene = scene; scene.drawAt(timeline.time()); return scene; });\nwindow.__hf = window.__hf || {}; window.__hf.buildReady = window.__moduleReady;\n`);
  await bundle(path.join(assets, 'scene-entry.js'), path.join(assets, 'scene.js'), nodeRoot);
  await writeFile(path.join(destination, 'index.html'), `<!doctype html>\n<html><head><meta charset="utf-8"><title>${name} visual smoke</title><style>html,body{margin:0;background:#101629} #main,#visual{position:relative;width:${width}px;height:${height}px;overflow:hidden} canvas{display:block}</style></head><body>\n<div id="main" data-composition-id="main" data-width="${width}" data-height="${height}" data-duration="${duration}"><div id="visual" class="clip" data-start="0" data-duration="${duration}" data-track-index="0" data-track-kind="graphics"></div></div>\n<script src="assets/scene.js"></script></body></html>\n`);
  await writeFile(path.join(destination, 'receipt.json'), JSON.stringify({ kind: 'visual-scene-smoke', module: name, parameters: params, package: modules[name], packageVersion, nodeRoot, shader: name === 'gl-transitions' ? 'CrossWarp from gl-transitions package' : null, note: 'Smoke demo; not a final video or professional visual finish. Edit assets/adapter.js and rebuild the bundle after changes.' }, null, 2) + '\n');
  return destination;
}

async function main() {
  const args = process.argv.slice(2), options = {};
  const allowed = new Set(['module', 'output', 'node-root', 'width', 'height', 'duration', 'seed', 'image-a', 'image-b']);
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i]?.startsWith('--') ? args[i].slice(2) : '';
    if (!allowed.has(key) || args[i + 1] === undefined || args[i + 1].startsWith('--') || Object.hasOwn(options, key)) throw new Error(`Invalid argument: ${args[i]}`);
    options[key] = args[i + 1];
  }
  console.log(await generate(options));
}
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) main().catch(error => { console.error(error.message); process.exitCode = 1; });
