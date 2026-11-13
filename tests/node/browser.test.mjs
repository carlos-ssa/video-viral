import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, rm, stat } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { launchBrowser, nodeRootFrom, browserPath } from '../../scripts/_node.mjs';

test('local Chrome uses a dedicated profile despite a deep TEMP and cleans it', async t => {
  const temp = await mkdtemp(path.join(tmpdir(), 'browser-test-'));
  const deep = path.join(temp, 'deep-workspace-'.repeat(10));
  await mkdir(deep);
  const old = { TEMP: process.env.TEMP, TMP: process.env.TMP, TMPDIR: process.env.TMPDIR };
  Object.assign(process.env, { TEMP: deep, TMP: deep, TMPDIR: deep });
  t.after(async () => {
    for (const [key, value] of Object.entries(old)) {
      if (value === undefined) delete process.env[key]; else process.env[key] = value;
    }
    await rm(temp, { recursive: true, force: true });
  });
  const browser = await launchBrowser(nodeRootFrom());
  const profileArg = browser.process().spawnargs.find(a => a.startsWith('--user-data-dir='));
  assert.ok(profileArg);
  const profile = profileArg.split('=').slice(1).join('=');
  assert.ok(!profile.startsWith(deep));
  assert.ok((await stat(profile)).isDirectory());
  try {
    const page = await browser.newPage();
    await page.goto('about:blank');
    assert.equal(await page.evaluate(() => 2 + 2), 4);
    const cdp = await page.createCDPSession();
    try {
      await cdp.send('HeadlessExperimental.beginFrame', { screenshot: { format: 'png' } });
      t.diagnostic(`${await browser.version()}: BeginFrame disponível`);
    } catch (error) {
      t.diagnostic(`${await browser.version()}: BeginFrame indisponível; screenshot é a reserva (${error.message})`);
    }
    assert.ok((await page.screenshot()).length > 0, 'captura screenshot real funciona no mesmo Chrome');
  } finally { await browser.close(); }
  await assert.rejects(stat(profile), { code: 'ENOENT' });
});

test('explicit missing local browser fails rather than downloading or switching silently', () => {
  const before = process.env.VIDEO_VIRAL_BROWSER_PATH;
  process.env.VIDEO_VIRAL_BROWSER_PATH = 'nonexistent-video-viral-browser';
  try { assert.throws(browserPath, /configurado não existe/); }
  finally { if (before === undefined) delete process.env.VIDEO_VIRAL_BROWSER_PATH; else process.env.VIDEO_VIRAL_BROWSER_PATH = before; }
});
