import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { generate } from '../../scripts/visual_scene.mjs';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { launchBrowser, nodeRootFrom } from '../../scripts/_node.mjs';

const nodeRoot = nodeRootFrom(process.env.VIDEO_VIRAL_NODE_ROOT);
test('visual scenes seek deterministically in a browser and preserve output', async t => {
  const temp = await mkdtemp(path.join(tmpdir(), 'visual-scenes-'));
  t.after(() => rm(temp, { recursive: true, force: true }));
  const browser = await launchBrowser(nodeRoot);
  t.after(() => browser.close());
  for (const name of ['pixi', 'paper', 'p5', 'gl-transitions']) {
    await t.test(name, async () => {
      const output = path.join(temp, name);
      await generate({ module: name, output, 'node-root': nodeRoot, width: 240, height: 160, duration: 4, seed: 17 });
      // lint é estático: não lança Chrome, não localiza fontes nem baixa dependências.
      const { stdout } = await promisify(execFile)(process.execPath,
        [path.join(nodeRoot, 'node_modules/hyperframes/bin/hyperframes.mjs'), 'lint', output, '--json'],
        { env: { ...process.env, DO_NOT_TRACK: '1', HYPERFRAMES_NO_UPDATE_CHECK: '1', HYPERFRAMES_NO_AUTO_INSTALL: '1' } });
      assert.equal(JSON.parse(stdout).errorCount, 0, stdout);
      const page = await browser.newPage();
      try {
        await page.setViewport({ width: 240, height: 160, deviceScaleFactor: 1 });
        await page.goto(pathToFileURL(path.join(output, 'index.html')).href);
        await page.evaluate(() => Promise.race([window.__moduleReady.then(() => true), new Promise((_, reject) => setTimeout(() => reject(new Error('scene initialization timed out')), 10000))]));
        assert.equal(await page.evaluate(() => window.__timelines.main.paused()), true);
        const frame = async time => { await page.evaluate(time => window.__moduleScene.drawAt(time), time); return page.screenshot(); };
        const first = await frame(2), zero = await frame(0), again = await frame(2);
        assert.deepEqual(first, again, '2 → 0 → 2 returns to identical pixels');
        assert.notDeepEqual(first, zero, 'the demo changes with time');
        await frame(0);
        await page.evaluate(() => { window.__timelines.main.seek(2); });
        assert.deepEqual(await page.screenshot(), first, 'timeline drives the adapter');
        await page.evaluate(() => window.__moduleScene.dispose());
        assert.equal(await page.$('canvas'), null);
      } finally { await page.close(); }
      const sentinel = path.join(output, 'sentinel'); await writeFile(sentinel, 'keep');
      await assert.rejects(generate({ module: name, output, 'node-root': nodeRoot }), /new or empty/);
      assert.equal(await readFile(sentinel, 'utf8'), 'keep');
    });
  }
});
