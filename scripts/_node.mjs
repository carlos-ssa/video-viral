import { createRequire } from 'node:module';
import { existsSync, mkdirSync } from 'node:fs';
import { mkdtemp, rm } from 'node:fs/promises';
import { homedir } from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';

export function nodeRootFrom(value) {
  return path.resolve(value || process.env.VIDEO_VIRAL_NODE_ROOT || path.join(homedir(), '.video-viral', 'node-v2'));
}

export function packageEntry(name, nodeRoot) {
  return createRequire(path.join(nodeRootFrom(nodeRoot), 'package.json')).resolve(name);
}

export async function bundle(entry, outFile, nodeRoot) {
  const esbuild = await import(pathToFileURL(packageEntry('esbuild', nodeRoot)).href);
  mkdirSync(path.dirname(outFile), { recursive: true });
  await esbuild.build({ entryPoints: [entry], outfile: outFile, bundle: true, format: 'iife',
    platform: 'browser', logLevel: 'silent', nodePaths: [path.join(nodeRootFrom(nodeRoot), 'node_modules')] });
}

export function browserPath() {
  const explicit = process.env.VIDEO_VIRAL_BROWSER_PATH || process.env.HYPERFRAMES_BROWSER_PATH;
  if (explicit) {
    if (!existsSync(explicit)) throw new Error('Browser configurado não existe; confira VIDEO_VIRAL_BROWSER_PATH/HYPERFRAMES_BROWSER_PATH.');
    return explicit;
  }
  const candidates = [
    path.join(process.env.ProgramFiles || '', 'Google', 'Chrome', 'Application', 'chrome.exe'),
    path.join(process.env['ProgramFiles(x86)'] || '', 'Microsoft', 'Edge', 'Application', 'msedge.exe')];
  for (const candidate of candidates) if (candidate && existsSync(candidate)) return candidate;
  for (const command of ['google-chrome', 'chromium', 'chromium-browser', 'microsoft-edge']) {
    try { return execFileSync('which', [command], { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim(); }
    catch { /* Try the next installed browser; never download one implicitly. */ }
  }
  throw new Error('Browser não encontrado. Defina VIDEO_VIRAL_BROWSER_PATH com um Chrome/Edge instalado.');
}

export async function launchBrowser(nodeRoot) {
  const imported = await import(pathToFileURL(packageEntry('puppeteer-core', nodeRoot)).href);
  const puppeteer = imported.default || imported;
  // Não herda TEMP/TMP de workspaces profundos: o perfil do Chrome pode exceder MAX_PATH.
  const base = path.resolve(process.env.VIDEO_VIRAL_BROWSER_TEMP_DIR || path.join(homedir(), '.video-viral', 'tmp'));
  mkdirSync(base, { recursive: true });
  const profile = await mkdtemp(path.join(base, 'vv-'));
  const cleanup = () => rm(profile, { recursive: true, force: true, maxRetries: 3 });
  try {
    const browser = await puppeteer.launch({ executablePath: browserPath(), headless: true,
      userDataDir: profile, env: { ...process.env, TEMP: profile, TMP: profile, TMPDIR: profile },
      args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required', `--disk-cache-dir=${path.join(profile, 'cache')}`] });
    const close = browser.close.bind(browser);
    browser.close = async () => { try { await close(); } finally { await cleanup(); } };
    browser.once('disconnected', () => { cleanup().catch(() => {}); });
    return browser;
  } catch (error) { await cleanup(); throw error; }
}
