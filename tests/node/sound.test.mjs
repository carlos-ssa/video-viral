import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, readFile, rm, writeFile, symlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { generate } from '../../scripts/sound.mjs';

const root = process.env.VIDEO_VIRAL_NODE_ROOT || 'C:/Users/igcar/.codex/reviews/video-viral-integration-2026-11-12/node';
test('renders deterministic PCM and protects outputs on errors', async t => {
  const project = await mkdtemp(path.join(tmpdir(), 'sound-test-'));
  t.after(() => rm(project, { recursive: true, force: true }));
  await mkdir(path.join(project, 'edit'));
  const spec = { duration: 1, seed: 42, events: ['whoosh','impact','pop','riser','pulse'].map((type,i) => ({ type, at: i * .18, duration: .1, gainDb: -9 })) };
  const specPath = path.join(project, 'edit/sound.json'); await writeFile(specPath, JSON.stringify(spec));
  const opts = { spec: 'edit/sound.json', 'node-root': root };
  const a = await generate(project, opts);
  const audio = await readFile(a.output); const receipt = JSON.parse(await readFile(a.receipt, 'utf8'));
  assert.equal(audio.toString('ascii',0,4), 'RIFF'); assert.equal(audio.toString('ascii',8,12), 'WAVE');
  assert.equal(audio.readUInt16LE(20), 1); assert.equal(audio.readUInt16LE(22), 1); assert.equal(audio.readUInt32LE(24), 44100); assert.equal(audio.readUInt16LE(34), 16); assert.equal(audio.readUInt32LE(40), 88200); assert.equal(audio.length, 88244);
  assert.ok(audio.subarray(44).some(n => n !== 0)); assert.equal(receipt.toneVersion, '15.1.22'); assert.deepEqual(receipt.spec, spec);
  assert.equal(receipt.wavSha256, createHash('sha256').update(audio).digest('hex'));
  const b = await generate(project, { ...opts, output: 'audio/repeat.wav' }); assert.deepEqual(await readFile(b.output), audio);
  await assert.rejects(generate(project, opts), /already exists/); assert.deepEqual(await readFile(a.output), audio);
  await writeFile(specPath, JSON.stringify({ ...spec, events: [{ ...spec.events[0], duration: 2 }] }));
  await assert.rejects(generate(project, { ...opts, output: 'audio/invalid.wav' }), /Invalid event/);
  await assert.rejects(generate(project, { ...opts, output: '../escape.wav' }), /inside/);
});

test('CLI rejects invalid specifications without creating audio', async t => {
  const { execFile } = await import('node:child_process');
  const { promisify } = await import('node:util');
  const project = await mkdtemp(path.join(tmpdir(), 'sound-cli-'));
  t.after(() => rm(project, { recursive: true, force: true }));
  await mkdir(path.join(project, 'edit'));
  await writeFile(path.join(project, 'edit/sound.json'), JSON.stringify({ duration: 1, seed: 1, events: [{ type: 'pop', at: 0, duration: .2, gainDb: 2 }] }));
  const script = new URL('../../scripts/sound.mjs', import.meta.url);
  await assert.rejects(promisify(execFile)(process.execPath, [script.pathname.replace(/^\/(\w:)/, '$1'), project, '--spec', 'edit/sound.json', '--node-root', root]), /Invalid event/);
  await assert.rejects(readFile(path.join(project, 'audio/sound-design.wav')), { code: 'ENOENT' });
});
