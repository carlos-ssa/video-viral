import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdtemp, readFile, writeFile, rm } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { generate } from '../../scripts/visual_scene.mjs';
import { launchBrowser, nodeRootFrom } from '../../scripts/_node.mjs';

test('shader transition loads provided image assets, not placeholder colors', async () => {
  const folder = await mkdtemp(path.join(os.tmpdir(), 'transition-images-'));
  const nodeRoot = nodeRootFrom();
  const browser = await launchBrowser(nodeRoot);
  let server;
  try {
    const page = await browser.newPage();
    const pngs = await page.evaluate(() => ['#ee1122', '#1144ee'].map(color => {
      const canvas = document.createElement('canvas'); canvas.width = 16; canvas.height = 16;
      const context = canvas.getContext('2d'); context.fillStyle = color; context.fillRect(0, 0, 16, 16);
      return canvas.toDataURL().split(',')[1];
    }));
    const a = path.join(folder, 'a.png'), b = path.join(folder, 'b.png');
    await writeFile(a, Buffer.from(pngs[0], 'base64')); await writeFile(b, Buffer.from(pngs[1], 'base64'));
    const output = path.join(folder, 'scene');
    await generate({ module: 'gl-transitions', output, width: 64, height: 64, duration: 2,
      'image-a': a, 'image-b': b, 'node-root': nodeRoot });
    server = createServer(async (req, response) => {
      try {
        const file = path.join(output, decodeURIComponent(new URL(req.url, 'http://localhost').pathname).replace(/^\//, '') || 'index.html');
        response.setHeader('Content-Type', file.endsWith('.js') ? 'application/javascript' : file.endsWith('.png') ? 'image/png' : 'text/html');
        response.end(await readFile(file));
      } catch { response.statusCode = 404; response.end(); }
    });
    await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
    await page.goto(`http://127.0.0.1:${server.address().port}/`);
    await page.evaluate(() => window.__moduleReady);
    const colors = await page.evaluate(() => [0, 2].map(time => {
      window.__moduleScene.drawAt(time);
      const gl = document.querySelector('canvas').getContext('webgl');
      const value = new Uint8Array(4); gl.readPixels(32, 32, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, value);
      return [...value];
    }));
    assert.ok(colors[0][0] > 200 && colors[0][2] < 100, colors[0]);
    assert.ok(colors[1][2] > 200 && colors[1][0] < 100, colors[1]);
    await assert.rejects(generate({ module: 'gl-transitions', output: path.join(folder, 'bad'), 'image-a': a, 'node-root': nodeRoot }), /both/);
  } finally {
    if (server) await new Promise(resolve => server.close(resolve));
    await browser.close(); await rm(folder, { recursive: true, force: true });
  }
});
