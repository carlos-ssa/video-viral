import { performance } from 'node:perf_hooks';
import assert from 'node:assert/strict';
import { launchBrowser, nodeRootFrom } from '../../scripts/_node.mjs';
import { renderSamples } from '../../scripts/sound.mjs';
const browser = await launchBrowser(nodeRootFrom());
try {
  const page = await browser.newPage();
  await page.evaluate(() => {
    const samples = Float32Array.from({ length: 30 * 44100 }, (_, i) => .25 * Math.sin(i * .07));
    window.renderSound = () => samples;
  });
  const old = async () => Float32Array.from(await page.evaluate(async () => Array.from(await window.renderSound({}))));
  const current = () => renderSamples(page, {});
  await old(); await current();
  const before = [], after = [];
  for (let i = 0; i < 5; i++) {
    let a, b;
    for (const [fn, times, save] of (i % 2 ? [[current, after, x => b = x], [old, before, x => a = x]] : [[old, before, x => a = x], [current, after, x => b = x]])) {
      const start = performance.now(); const result = await fn(); times.push(performance.now() - start); save(result);
    }
    assert.deepEqual(Buffer.from(a.buffer), Buffer.from(b.buffer));
  }
  const median = a => [...a].sort((a,b) => a-b)[2];
  console.log(JSON.stringify({ stage: '30s mono 44100Hz browser-to-Node Float32 transport', pairs: 5, before_ms: before, after_ms: after, median_before_ms: median(before), median_after_ms: median(after), reduction_percent: 100 * (1 - median(after) / median(before)), exact_samples: true, browser: await browser.version(), node: process.version }, null, 2));
} finally { await browser.close(); }
