import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { buildTransport } from '../src/world/transport.js';

test('transport theme stays in home, batches geometry and leaves movement physics separate', () => {
  const home = { name: 'home', group: new THREE.Group() };
  const scene = buildTransport(home, () => new THREE.Group());
  assert.equal(home.group.children.length, 1);
  assert.equal(scene.colliders.length, 2);
  let meshes = 0, triangles = 0, lights = 0;
  scene.group.traverse((obj) => {
    if (obj.isMesh) { meshes++; triangles += obj.geometry.index.count / 3; }
    if (obj.isLight) lights++;
  });
  assert.ok(meshes <= 18, `theme geometry draw calls: ${meshes}`);
  assert.ok(triangles < 5000, `theme triangles: ${triangles}`);
  assert.equal(lights, 0);
  scene.update(0); const x = scene.train.position.x;
  scene.update(2); assert.notEqual(scene.train.position.x, x);
  for (let time = 0; time < 100; time++) {
    scene.update(time);
    assert.ok(scene.train.position.x >= -4.2 && scene.train.position.x <= 2.8);
  }
  assert.throws(() => buildTransport({ name: 'tree' }), /only/);
});
