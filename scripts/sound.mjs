#!/usr/bin/env node
import { mkdtemp, readFile, realpath, lstat, mkdir, writeFile, rename, unlink, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash, randomUUID } from 'node:crypto';
import { bundle, launchBrowser, packageEntry, nodeRootFrom } from './_node.mjs';

const hash = data => createHash('sha256').update(data).digest('hex');
const inside = (root, target) => { const r = path.relative(root, target); return r && !r.startsWith(`..${path.sep}`) && r !== '..' && !path.isAbsolute(r); };
async function safePath(root, name) {
  if (typeof name !== 'string' || !name || path.isAbsolute(name)) throw new Error('Paths must be relative to the project');
  const target = path.resolve(root, name);
  if (!inside(root, target)) throw new Error('Path must remain inside the project');
  let current = root;
  for (const part of path.relative(root, target).split(path.sep)) {
    current = path.join(current, part);
    try { const info = await lstat(current); if (info.isSymbolicLink()) throw new Error('Symbolic links are not allowed in project paths'); }
    catch (e) { if (e.code !== 'ENOENT') throw e; }
  }
  return target;
}
function validate(spec) {
  if (!spec || typeof spec !== 'object' || !Number.isFinite(spec.duration) || spec.duration <= 0 || spec.duration > 600 || !Number.isInteger(spec.seed) || spec.seed < 0 || spec.seed > 4294967295 || !Array.isArray(spec.events) || spec.events.length > 1000) throw new Error('Invalid duration, seed or events');
  for (const e of spec.events) {
    if (!e || !['whoosh','impact','pop','riser','pulse'].includes(e.type) || !Number.isFinite(e.at) || e.at < 0 || !Number.isFinite(e.duration) || e.duration <= 0 || e.at + e.duration > spec.duration || !Number.isFinite(e.gainDb) || e.gainDb < -96 || e.gainDb > 0) throw new Error('Invalid event: check type, timing and gainDb (-96..0)');
  }
}
function wav(samples) {
  const b = Buffer.alloc(44 + samples.length * 2);
  b.write('RIFF',0); b.writeUInt32LE(b.length-8,4); b.write('WAVEfmt ',8); b.writeUInt32LE(16,16); b.writeUInt16LE(1,20); b.writeUInt16LE(1,22); b.writeUInt32LE(44100,24); b.writeUInt32LE(88200,28); b.writeUInt16LE(2,32); b.writeUInt16LE(16,34); b.write('data',36); b.writeUInt32LE(samples.length*2,40);
  samples.forEach((n,i) => b.writeInt16LE(Math.round(n < 0 ? n * 32768 : n * 32767),44+i*2));
  return b;
}
export async function generate(project, options = {}) {
  const root = await realpath(project);
  const specPath = await safePath(root, options.spec || 'edit/sound.json');
  const output = await safePath(root, options.output || 'audio/sound-design.wav');
  const receiptPath = await safePath(root, `${path.relative(root, output)}.json`);
  if (specPath === output || specPath === receiptPath) throw new Error('Output conflicts with spec');
  const source = await readFile(specPath); const spec = JSON.parse(source.toString('utf8')); validate(spec);
  for (const dest of [output, receiptPath]) { try { await lstat(dest); throw new Error(`Output already exists: ${dest}`); } catch (e) { if (e.code !== 'ENOENT') throw e; } }
  const nodeRoot = nodeRootFrom(options['node-root']);
  const toneEntry = packageEntry('tone', nodeRoot);
  const tonePackage = JSON.parse(await readFile(path.resolve(path.dirname(toneEntry), '../../package.json'), 'utf8'));
  const temp = await mkdtemp(path.join(tmpdir(), 'sound-render-')); let browser;
  try {
    const script = path.join(temp, 'renderer.js');
    await bundle(path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../assets/integrations/sound/renderer.js'), script, nodeRoot);
    browser = await launchBrowser(nodeRoot);
    const page = await browser.newPage();
    await page.setRequestInterception(true); page.on('request', req => req.url().startsWith('file:') || req.url() === 'about:blank' ? req.continue() : req.abort());
    await page.goto('about:blank'); await page.addScriptTag({ content: await readFile(script, 'utf8') });
    const samples = await page.evaluate(s => window.renderSound(s), spec);
    if (samples.length !== Math.ceil(spec.duration * 44100) || samples.some(n => !Number.isFinite(n) || Math.abs(n) > 1)) throw new Error('Rendered audio has invalid duration, samples or amplitude');
    const audio = wav(samples);
    const receipt = { kind: 'sound-design-smoke', toneVersion: tonePackage.version, sampleRate: 44100, channels: 1, bitsPerSample: 16, duration: spec.duration, frames: samples.length, spec, specSha256: hash(source), wavSha256: hash(audio), note: 'Technical smoke; not aesthetic approval. Oscillator rendering can vary across browser versions and platforms.' };
    // Publish only after successful rendering and validation. Exclusive writes prevent overwriting.
    await safePath(root, path.relative(root, output)); await safePath(root, path.relative(root, receiptPath));
    await mkdir(path.dirname(output), { recursive: true });
    const suffix = `.tmp-${randomUUID()}`; const a = output + suffix, b = receiptPath + suffix;
    let published = false;
    try {
      await writeFile(a, audio, { flag: 'wx' }); await writeFile(b, JSON.stringify(receipt, null, 2) + '\n', { flag: 'wx' });
      // link is atomic and fails if another process has created the destination.
      const { link } = await import('node:fs/promises');
      await link(a, output); published = true; await link(b, receiptPath);
    } catch (e) { if (published) await unlink(output).catch(() => {}); throw e; }
    finally { await unlink(a).catch(() => {}); await unlink(b).catch(() => {}); }
    return { output, receipt: receiptPath };
  } finally { if (browser) await browser.close(); await rm(temp, { recursive: true, force: true }); }
}
async function main() {
  const args = process.argv.slice(2); const project = args.shift(); const opts = {};
  if (!project || project.startsWith('--')) throw new Error('Usage: sound.mjs <project> --spec edit/sound.json --node-root <npm-root> [--output audio/sound-design.wav]');
  while (args.length) { const k = args.shift(); const v = args.shift(); if (!['--spec','--node-root','--output'].includes(k) || !v || v.startsWith('--') || Object.hasOwn(opts,k.slice(2))) throw new Error(`Invalid argument: ${k}`); opts[k.slice(2)] = v; }
  if (!opts.spec || !opts['node-root']) throw new Error('--spec and --node-root are required');
  console.log(JSON.stringify(await generate(project, opts)));
}
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) main().catch(e => { console.error(e.message); process.exitCode = 1; });
