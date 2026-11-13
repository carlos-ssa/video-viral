import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import path from 'node:path';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { bundle, launchBrowser, nodeRootFrom } from '../../scripts/_node.mjs';
import { renderSamples, validateSamples } from '../../scripts/sound.mjs';

test('binary browser transport preserves every rendered Float32 sample', async () => {
  const browser = await launchBrowser(nodeRootFrom());
  try {
    const page = await browser.newPage();
    await page.evaluate(() => { window.renderSound = () => Float32Array.from([0, -0, .1, -.1, 1, -1]); });
    const expected = Array.from(new Float32Array([0, -0, .1, -.1, 1, -1]));
    assert.deepEqual(Array.from(await renderSamples(page, {})), expected);
    await page.evaluate(() => { window.renderSound = () => new Float32Array([NaN, Infinity]); });
    const corrupt = await renderSamples(page, {});
    assert.throws(() => validateSamples(corrupt, 2 / 44100), /samples/);
  } finally { await browser.close(); }
});


test('Tone real rendering is PCM-equivalent through old and binary transports', async () => {
  const root = nodeRootFrom(), temp = await mkdtemp(path.join(tmpdir(), 'tone-transport-'));
  const browser = await launchBrowser(root);
  try {
    const script = path.join(temp, 'renderer.js');
    await bundle(fileURLToPath(new URL('../../assets/integrations/sound/renderer.js', import.meta.url)), script, root);
    const page = await browser.newPage();
    await page.addScriptTag({ content: await readFile(script, 'utf8') });
    const spec = { duration: 1.2345, seed: 42, events: [
      { type: 'whoosh', at: 0, duration: .7, gainDb: -12 },
      { type: 'impact', at: .6, duration: .5, gainDb: -9 }
    ] };
    const old = await page.evaluate(async s => Array.from(await window.renderSound(s)), spec);
    const current = await renderSamples(page, spec);
    validateSamples(old, spec.duration); validateSamples(current, spec.duration);
    const pcm = samples => {
      const bytes = Buffer.alloc(samples.length * 2);
      samples.forEach((n, i) => bytes.writeInt16LE(Math.round(n < 0 ? n * 32768 : n * 32767), i * 2));
      return bytes;
    };
    assert.deepEqual(pcm(current), pcm(old));
  } finally { await browser.close(); await rm(temp, { recursive: true, force: true }); }
});
