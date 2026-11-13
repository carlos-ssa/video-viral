import { spawnSync } from 'node:child_process';
import { readFileSync, existsSync, mkdirSync, writeFileSync, renameSync, unlinkSync } from 'node:fs';
import { createHash, randomUUID } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { nodeRootFrom } from './_node.mjs';

export function optimize(input, output, nodeRoot) {
  const source = path.resolve(input), target = path.resolve(output);
  if (source === target || path.extname(source).toLowerCase() !== '.glb' || path.extname(target).toLowerCase() !== '.glb')
    throw new Error('Use entrada e saída GLB diferentes; a fonte é preservada.');
  if (existsSync(target)) throw new Error('Saída já existe; escolha outro arquivo.');
  const data = readFileSync(source);
  if (data.subarray(0, 4).toString() !== 'glTF') throw new Error('Entrada não é GLB.');
  const require = createRequire(path.join(nodeRootFrom(nodeRoot), 'package.json'));
  let directory = path.dirname(require.resolve('@gltf-transform/cli'));
  while (directory !== path.dirname(directory)) {
    const metadata = path.join(directory, 'package.json');
    if (existsSync(metadata) && JSON.parse(readFileSync(metadata, 'utf8')).name === '@gltf-transform/cli') break;
    directory = path.dirname(directory);
  }
  const pkg = JSON.parse(readFileSync(path.join(directory, 'package.json'), 'utf8'));
  const bin = typeof pkg.bin === 'string' ? pkg.bin : Object.values(pkg.bin || {})[0];
  if (!bin) throw new Error('Binário do glTF Transform ausente.');
  const cli = path.resolve(directory, bin);
  mkdirSync(path.dirname(target), { recursive: true });
  const temporary = path.join(path.dirname(target), `${randomUUID()}.glb`);
  const hash = (buffer) => createHash('sha256').update(buffer).digest('hex');
  try {
    // Conservative optimization keeps loading independent of Draco/Meshopt/KTX2 decoders.
    const result = spawnSync(process.execPath, [cli, 'optimize', source, temporary,
      '--compress', 'false', '--texture-compress', 'false'], { encoding: 'utf8', timeout: 120000 });
    if (result.error || result.status !== 0) throw new Error(`glTF Transform falhou: ${(result.stderr || result.error?.message || '').slice(-600)}`);
    const optimized = readFileSync(temporary);
    if (optimized.subarray(0, 4).toString() !== 'glTF') throw new Error('Saída inválida.');
    renameSync(temporary, target);
    const receipt = { tool: 'glTF Transform', input_sha256: hash(data), output_sha256: hash(optimized),
      input_bytes: data.length, output_bytes: optimized.length, source_preserved: true,
      compression: 'none; no decoder required', visual_quality_verified: false };
    writeFileSync(`${target}.receipt.json`, JSON.stringify(receipt, null, 2));
    return receipt;
  } finally { if (existsSync(temporary)) unlinkSync(temporary); }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [input, output, ...rest] = process.argv.slice(2);
  const index = rest.indexOf('--node-root');
  try { if (!input || !output) throw new Error('Uso: node scripts/gltf.mjs entrada.glb saida.glb [--node-root pasta]');
    console.log(JSON.stringify(optimize(input, output, index >= 0 ? rest[index + 1] : undefined), null, 2)); }
  catch (error) { console.error(error.message); process.exitCode = 1; }
}
