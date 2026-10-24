// Procedural theme illustration only; not a model of an approved real project.
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { toonMaterial, canvasTexture } from './toon.js';

export const TRANSPORT_NOTICE = '政策主題示意，非實際工程核定或完工資訊';

// Material batches keep hundreds of small voxel details to a few draw calls.
function batchBuilder(parent) {
  const batches = new Map();
  return {
    box(color, size, position, rotation = 0) {
      const geometry = new THREE.BoxGeometry(...size);
      geometry.rotateZ(rotation);
      geometry.translate(...position);
      if (!batches.has(color)) batches.set(color, []);
      batches.get(color).push(geometry);
    },
    finish() {
      for (const [color, parts] of batches) {
        const geometry = mergeGeometries(parts);
        const mesh = new THREE.Mesh(geometry, toonMaterial(color));
        parent.add(mesh);
        for (const part of parts) part.dispose();
      }
    }
  };
}

function textSign(text, width, height) {
  const texture = canvasTexture(512, (ctx, size) => {
    ctx.fillStyle = '#fff3d6'; ctx.fillRect(0, 0, size, size);
    ctx.fillStyle = '#35585e'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.font = `bold ${text.length > 10 ? 220 : 260}px sans-serif`;
    ctx.fillText(text, size / 2, size / 2, size - 24);
  });
  const sign = new THREE.Mesh(new THREE.PlaneGeometry(width, height), new THREE.MeshBasicMaterial({ map: texture }));
  return sign;
}

export function buildTransport(home, makeSign = textSign) {
  if (home.name !== 'home') throw new Error('Transport scene belongs only to the home policy island');
  const group = new THREE.Group(); group.name = 'transport-theme';
  group.userData.notice = TRANSPORT_NOTICE;
  const b = batchBuilder(group);
  const C = { cream: 0xffedcf, teal: 0x527f80, dark: 0x38555e, coral: 0xd98670, stone: 0xc7bbad, road: 0x70818a, leaf: 0x719e83, light: 0xffdca0 };
  const box = (color, size, pos, rot) => b.box(color, size, pos, rot);
  // A low station with a stepped gable silhouette, ticket windows and canopy.
  box(C.cream, [4.8, 2.05, 1.9], [-1.4, 1.2, -4.2]);
  for (const side of [-1, 1]) box(C.teal, [2.9, 0.24, 2.65], [-1.4 + side * 1.3, 2.55, -4.2], side * -0.27);
  box(C.cream, [1.35, 2.9, 1.95], [-1.4, 1.65, -4.2]);
  box(C.coral, [1.7, 0.24, 2.3], [-1.4, 3.2, -4.2]);
  box(C.dark, [0.7, 1.25, 0.04], [-1.4, 0.8, -3.23]);
  for (const x of [-3, 0.2]) {
    box(C.dark, [1.05, 0.8, 0.06], [x, 1.25, -3.23]);
    box(C.cream, [0.06, 0.8, 0.08], [x, 1.25, -3.18]);
  }
  box(C.teal, [6.5, 0.16, 1.55], [-1.3, 2.05, -2.8]);
  for (const x of [-4.25, 1.65]) box(C.coral, [0.15, 1.9, 0.15], [x, 1, -2.3]);
  for (const x of [-3.8, 1.2]) {
    box(C.coral, [1, 0.12, 0.35], [x, 0.48, -2.65]);
    box(C.dark, [0.1, 0.4, 0.25], [x - 0.3, 0.24, -2.65]);
    box(C.dark, [0.1, 0.4, 0.25], [x + 0.3, 0.24, -2.65]);
  }
  const stationSign = makeSign('交通主題車站', 2.8, 0.52);
  stationSign.position.set(-1.4, 2.35, -3.18); group.add(stationSign);
  // Ballast, sleepers and twin rails in front of the platform.
  box(C.stone, [11.5, 0.11, 1.25], [-0.8, 0.07, -1.1]);
  for (let i = 0; i < 26; i++) box(C.dark, [0.14, 0.09, 1.05], [-6.3 + i * 0.44, 0.16, -1.1]);
  for (const z of [-1.46, -0.74]) box(C.road, [11.6, 0.12, 0.07], [-0.8, 0.22, z]);
  for (const x of [-6.6, 5]) box(C.coral, [0.12, 0.4, 1.1], [x, 0.35, -1.1]);
  // Paved arrival plaza. The central spawn and both bridge exits stay clear.
  box(C.stone, [5.5, 0.035, 3], [0, 0.025, 2]);
  box(C.stone, [2.6, 0.03, 3.1], [0, 0.02, 5.05]);
  for (let i = 0; i < 6; i++) box(C.cream, [0.65, 0.025, 0.2], [-2.1 + i * 0.84, 0.055, 0.8]);
  // A road viaduct across a shallow, rocky drainage landscape at the west edge.
  box(0x778e92, [2.65, 0.03, 4.6], [-5.8, 0.025, 2.3]);
  for (const z of [0.4, 4.2]) for (const x of [-6.5, -5.1]) box(C.stone, [0.3, 0.55, 0.4], [x, 0.29, z]);
  for (const x of [-6.65, -4.95]) {
    box(C.cream, [0.08, 0.12, 5.5], [x, 1.05, 2.2]);
    for (let i = 0; i < 9; i++) box(C.cream, [0.08, 0.5, 0.08], [x, 0.8, -0.4 + i * 0.65]);
  }
  for (let i = 0; i < 8; i++) box(C.light, [0.08, 0.025, 0.35], [-5.8, 0.585, -0.2 + i * 0.65]);
  // Lamps use coloured geometry rather than costly extra light sources.
  for (const [x, z] of [[-4.6, -2.4], [2.6, -2.4], [-4.4, 4.4], [3.7, 0.4]]) {
    box(C.dark, [0.09, 2.25, 0.09], [x, 1.15, z]);
    box(C.teal, [0.55, 0.13, 0.4], [x + 0.18, 2.3, z]);
    box(C.light, [0.4, 0.07, 0.28], [x + 0.18, 2.2, z]);
  }
  for (const [x, z] of [[-3.8, 3.6], [2.8, 3.7], [3.8, -3.8], [-5.6, -3.9]]) {
    box(C.cream, [0.9, 0.25, 0.9], [x, 0.15, z]);
    box(C.coral, [0.16, 0.7, 0.16], [x, 0.6, z]);
    box(C.leaf, [0.85, 0.75, 0.85], [x, 1.25, z]);
    box(0x9ab78f, [0.6, 0.45, 0.6], [x + 0.12, 1.75, z]);
  }
  box(C.dark, [0.09, 1.5, 0.09], [2.9, 0.75, 1]);
  const wayfinding = makeSign('車站 ←', 1.1, 0.38); wayfinding.position.set(2.9, 1.6, 1.06); group.add(wayfinding);
  const notice = makeSign('交通場景示意・非核定工程', 4, 0.35); notice.position.set(-1.4, 0.5, 4.05); group.add(notice);
  b.finish();
  // Walkable decks remain separate, explicit collision meshes.
  const colliders = [];
  for (const [name, size, pos, color] of [
    ['station-platform', [7.2, 0.16, 1.35], [-1.3, 0.08, -2.5], C.cream],
    ['road-viaduct', [1.8, 0.18, 5.7], [-5.8, 0.46, 2.2], C.road]
  ]) {
    const deck = new THREE.Mesh(new THREE.BoxGeometry(...size), toonMaterial(color));
    deck.name = name; deck.position.set(...pos); group.add(deck); colliders.push(deck);
  }
  const train = new THREE.Group(); train.name = 'slow-train';
  const t = batchBuilder(train);
  for (const x of [-0.9, 0.9]) {
    t.box(C.cream, [1.65, 0.7, 0.85], [x, 0.7, 0]);
    t.box(C.teal, [1.7, 0.14, 0.9], [x, 1.13, 0]);
    t.box(C.coral, [1.65, 0.17, 0.87], [x, 0.46, 0]);
    for (const dx of [-0.45, 0, 0.45]) for (const z of [-0.435, 0.435]) t.box(C.dark, [0.29, 0.28, 0.025], [x + dx, 0.82, z]);
    for (const dx of [-0.5, 0.5]) t.box(C.dark, [0.25, 0.25, 1], [x + dx, 0.28, 0]);
  }
  t.finish(); train.position.set(-0.7, 0.18, -1.1); group.add(train);
  home.group.add(group);
  return { group, train, colliders, update(time) { train.position.x = -0.7 + Math.sin(time * 0.16) * 3.5; } };
}
