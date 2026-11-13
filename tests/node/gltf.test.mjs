import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, readFile, rm } from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { pathToFileURL } from 'node:url';
import { packageEntry, nodeRootFrom } from '../../scripts/_node.mjs';
import { optimize } from '../../scripts/gltf.mjs';

test('real GLB optimization preserves source and can be read back', async () => {
  const nodeRoot = nodeRootFrom();
  const { Document, NodeIO } = await import(pathToFileURL(packageEntry('@gltf-transform/core', nodeRoot)).href);
  const folder = await mkdtemp(path.join(os.tmpdir(), 'gltf-smoke-'));
  try {
    const doc = new Document(), buffer = doc.createBuffer();
    const positions = doc.createAccessor().setType('VEC3').setArray(new Float32Array([0, 0, 0, 1, 0, 0, 0, 1, 0])).setBuffer(buffer);
    const primitive = doc.createPrimitive().setAttribute('POSITION', positions);
    doc.createScene().addChild(doc.createNode().setMesh(doc.createMesh().addPrimitive(primitive)));
    const input = path.join(folder, 'input.glb'), output = path.join(folder, 'output.glb');
    const io = new NodeIO();
    await io.write(input, doc);
    const original = await readFile(input);
    const receipt = optimize(input, output, nodeRoot);
    assert.equal(receipt.source_preserved, true);
    assert.deepEqual(await readFile(input), original);
    const result = await io.read(output);
    assert.ok(result.getRoot().listMeshes().length > 0);
    assert.throws(() => optimize(input, output, nodeRoot), /existe/);
    assert.deepEqual(await readFile(input), original);
  } finally { await rm(folder, { recursive: true, force: true }); }
});
