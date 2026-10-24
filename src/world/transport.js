// Original procedural models, MIT. Theme illustration, not an approved project.
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { toonMaterial, canvasTexture } from './toon.js';
import plan from '../data/transport-v3.json' with { type: 'json' };
import surface from '../data/yuan-surface.json' with { type: 'json' };

export const TRANSPORT_NOTICE = '交通政策願景示意，非實際工程核定或完工資訊';
export const TRANSPORT_PLAN = plan;
const C = { cream: 0xffedcf, teal: 0x527f80, dark: 0x38555e, coral: 0xd98670, stone: 0xc7bbad, road: 0x70818a, leaf: 0x719e83, light: 0xffdca0, wood: 0xb88d64, blue: 0x82b7be };

function batchBuilder(parent) {
  const batches = new Map();
  const add = (color, geometry) => {
    // Merging indexed primitives with custom roofs: normalize to triangle lists.
    const g = geometry.index ? geometry.toNonIndexed() : geometry;
    if (g !== geometry) geometry.dispose();
    g.deleteAttribute('uv');
    if (!batches.has(color)) batches.set(color, []);
    batches.get(color).push(g);
  };
  const box = (color, size, position, rz = 0) => {
    const g = new THREE.BoxGeometry(...size); g.rotateZ(rz); g.translate(...position); add(color, g);
  };
  const beam = (color, a, b, width = .05, height = width) => {
    const start = new THREE.Vector3(...a), end = new THREE.Vector3(...b), d = end.clone().sub(start);
    const g = new THREE.BoxGeometry(width, height, d.length());
    g.applyMatrix4(new THREE.Matrix4().compose(start.lerp(end, .5), new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), d.normalize()), new THREE.Vector3(1, 1, 1)));
    add(color, g);
  };
  return { box, beam, add, finish() {
    for (const [color, parts] of batches) {
      const mesh = new THREE.Mesh(mergeGeometries(parts), toonMaterial(color));
      mesh.userData.island = 'home'; parent.add(mesh); parts.forEach(p => p.dispose());
    }
  } };
}

function textSign(text, width, height) {
  const texture = canvasTexture(512, (ctx, size) => {
    // Match the canvas aspect to the physical sign: no squashed Chinese glyphs.
    const pixelsHigh = Math.max(32, Math.round(size * height / width));
    ctx.canvas.height = pixelsHigh;
    ctx.fillStyle = '#fff3d6'; ctx.fillRect(0, 0, size, pixelsHigh);
    ctx.fillStyle = '#35585e'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    const lines = text.split('\n');
    let fontSize = pixelsHigh * .76 / lines.length;
    ctx.font = `bold ${fontSize}px sans-serif`;
    const measured = Math.max(...lines.map(line => ctx.measureText(line).width));
    fontSize *= Math.min(1, (size - 24) / measured);
    ctx.font = `bold ${fontSize}px sans-serif`;
    lines.forEach((line, i) => ctx.fillText(line, size / 2, pixelsHigh * (i + .5) / lines.length));
  });
  return new THREE.Mesh(new THREE.PlaneGeometry(width, height), new THREE.MeshBasicMaterial({ map: texture }));
}

// Exact exposed boundary from the EXISTING union: gates are already cut out and
// the nearby southern routes are a single shared open region, with no middle fence.
export function transportEdgeSegments() {
  const walls = [];
  for (const polygon of surface.domain) for (const ring of polygon) for (let i = 1; i < ring.length; i++) {
    const a = ring[i - 1], b = ring[i], mx = (a[0] + b[0]) / 2, mz = (a[1] + b[1]) / 2;
    if (Math.hypot(...a) > 9.001 || Math.hypot(...b) > 9.001 || Math.hypot(mx, mz) < 8.8) continue;
    walls.push({ a: { x: a[0], y: 0, z: a[1] }, b: { x: b[0], y: 0, z: b[1] }, height: 1.3, kind: 'island-edge' });
  }
  return walls;
}

export function buildTransport(home, makeSign = textSign) {
  if (home.name !== 'home') throw new Error('Transport scene belongs only to the home policy island');
  const group = new THREE.Group(); group.name = 'transport-theme';
  group.userData.notice = TRANSPORT_NOTICE; group.userData.plan = plan;
  const b = batchBuilder(group), { box, beam } = b, barriers = [], colliders = [];
  const wall = (a, z, c, d, height, kind, base = 0) => barriers.push({ a: { x: a, y: base, z }, b: { x: c, y: base, z: d }, height, kind });
  const boundary = (bounds, height, kind) => {
    const [x0, z0, x1, z1] = bounds;
    wall(x0,z0,x1,z0,height,kind); wall(x1,z0,x1,z1,height,kind); wall(x1,z1,x0,z1,height,kind); wall(x0,z1,x0,z0,height,kind);
  };
  function deck(name, size, pos, color) {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size), toonMaterial(color));
    mesh.name = name; mesh.position.set(...pos); mesh.userData.island = 'home'; group.add(mesh); colliders.push(mesh);
    return mesh;
  }
  function sign(text, w, h, x, y, z) {
    const mesh = makeSign(text, w, h); mesh.position.set(x,y,z); mesh.userData.island = 'home'; group.add(mesh);
  }
  // Solid volumes have matching swept horizontal collision walls. The recessed
  // entrance is genuinely open (1.2 wide), with a continuous ground-level floor.
  for (const s of plan.stationSolids) {
    const [x0,z0,x1,z1] = s.bounds;
    box(C.cream,[x1-x0,s.height,z1-z0],[(x0+x1)/2,s.height/2,(z0+z1)/2]);
    boundary(s.bounds,s.height,s.name);
  }
  deck('station-platform',plan.platform.size,plan.platform.center,C.cream);
  deck('entrance-floor',[1.2,.05,1.95],[.1,.025,-4.12],C.stone);
  // Asymmetric folded roof: three different planes; restrained raised east tip.
  const roof = [[-3.95,2.37],[-1.65,2.9],[-.65,2.54],[1.05,2.7]];
  for (let i=1;i<roof.length;i++) {
    const [x,y]=roof[i-1],[xx,yy]=roof[i],len=Math.hypot(xx-x,yy-y);
    box(C.teal,[len+.025,.15,2.55],[(x+xx)/2,(y+yy)/2,-4.38],Math.atan2(yy-y,xx-x));
    beam(C.wood,[x,y-.1,-3.08],[xx,yy-.1,-3.08],.09);
  }
  // Layered window reveals, cream mullions and warm recessed portal.
  box(C.dark,[2.8,.72,.06],[-2.05,1.02,-3.51]);
  box(C.blue,[2.85,.25,.07],[-2.05,1.76,-3.5]);
  box(C.blue,[.035,.65,1.15],[-3.625,1.35,-4.42]);
  for(const x of [-3.32,-2.7,-2.08,-1.46,-.84])box(C.wood,[.055,1.34,.12],[x,1.22,-3.44]);
  box(C.dark,[1.16,1.85,.04],[.1,.94,-5.05]);
  for(const x of [-.46,.66])box(C.wood,[.06,2,.16],[x,1,-3.48]);
  box(C.coral,[1.23,.12,.21],[.1,2.05,-3.43]);
  // Abstract triangular rush-weave lattice, an original geometric cultural motif.
  // No external texture/font outline or claims of architectural reconstruction.
  for(let i=0;i<11;i++) {
    const x=-3.65+i*.36;
    beam(C.wood,[x,1.93,-3.03],[x+.28,2.32,-3.03],.035);
    beam(C.wood,[x+.28,2.32,-3.03],[x+.36,1.93,-3.03],.035);
    beam(C.wood,[x,1.93,-3.03],[x+.36,1.93,-3.03],.035);
  }
  box(C.teal,[4.35,.1,.65],[-1.4,2.4,-3.02]);
  for(const x of [-3.48,.68]) {
    box(C.dark,[.07,2.35,.07],[x,1.17,-2.89]);
    boundary([x-.035,-2.925,x+.035,-2.855],2.35,'canopy-column');
  }
  sign('苑裡・藺編文化車站',2.65,.28,-1.5,2.57,-2.68);
  sign('交通政策願景示意',2.55,.25,-1.55,.44,-3.42);
  // North display railway, isolated from the central pedestrian plaza.
  box(C.stone,[6.6,.06,1.06],[0,.045,-7]);
  for(let i=0;i<25;i++)box(C.wood,[.1,.07,.93],[-3.15+i*.263,.11,-7]);
  for(const z of [-7.32,-6.68])box(C.road,[6.6,.08,.065],[0,.18,z]);
  for(const x of [-3.28,3.28]) {
    box(C.coral,[.12,.36,1],[x,.28,-7]);
    beam(C.cream,[x-.2,.15,-7.45],[x+.2,.6,-6.55],.07);
  }
  // Railing has exactly the same coordinates as the train exclusion collision.
  const railBounds=plan.rail.exclusion; boundary(railBounds,1.25,'rail-exclusion');
  for(const w of barriers.filter(w=>w.kind==='rail-exclusion')) {
    for(const y of [.48,.97])beam(C.dark,[w.a.x,y,w.a.z],[w.b.x,y,w.b.z],.045);
    const n=Math.ceil(Math.hypot(w.b.x-w.a.x,w.b.z-w.a.z)/.65);
    for(let i=0;i<=n;i++){const t=i/n;box(C.teal,[.055,1.05,.055],[w.a.x+(w.b.x-w.a.x)*t,.525,w.a.z+(w.b.z-w.a.z)*t]);}
  }
  for(let i=0;i<22;i++)box(C.light,[.18,.012,.07],[-3.45+i*.28,.126,-6.22]);
  // Ramp-free, shallow platform step of .12, with open access at both ends.
  for(const x of [-3.25,1.85]) {
    box(C.wood,[.85,.1,.3],[x,.49,-5.76]);
    for(const dx of [-.3,.3])box(C.dark,[.06,.4,.2],[x+dx,.24,-5.76]);
  }
  // Open arrival square. Surface details remain below the ground-step threshold.
  deck('arrival-plaza',[8.8,.014,3.9],[0,.007,.1],C.stone);
  box(C.stone,[4.5,.012,1.7],[-1.4,.006,-2.7]);
  for(let x=-4;x<=4;x+=.8)for(let z=-1.5;z<=1.5;z+=.75)box(C.cream,[.015,.006,.65],[x,.019,z]);
  for(const x of [-2.1,2.1])box(C.wood,[.08,.006,3.65],[x,.02,.1]);
  // Four user-supplied policy themes, explicitly marked as vision, no invented
  // budget, timetable or approval status; formal policies.json is untouched.
  sign('交通政策願景示意\n非核定或完工工程',1.8,.45,-5.6,1.28,-4.075);
  sign(plan.visionDisplay.topics.slice(0,2).join('\n'),1.8,.42,-5.6,.8,-4.075);
  sign(plan.visionDisplay.topics.slice(2).join('\n'),1.8,.42,-5.6,.35,-4.075);
  // Compact road bridge exhibit, safely west of the real southern walking gates.
  deck('road-viaduct',plan.roadExhibit.size,plan.roadExhibit.center,C.road);
  for(const x of [-6.5,-5.1]) {
    wall(x,3.1,x,5.9,1.25,'road-exhibit');
    for(const y of [.45,1])beam(C.cream,[x,y,3.1],[x,y,5.9],.06);
    for(let z=3.1;z<=5.91;z+=.56)box(C.teal,[.07,1.05,.07],[x,.525,z]);
  }
  for(let z=3.35;z<5.8;z+=.45)box(C.light,[.06,.008,.23],[-5.8,.124,z]);
  // Low landscape walls / planting and airy metal rails use the very same
  // physical island-edge lines. Existing bridge rails end at these exact points.
  const edgeBarriers=transportEdgeSegments(); barriers.push(...edgeBarriers);
  for(const w of edgeBarriers) {
    const north=(w.a.z+w.b.z)/2 < -2.5;
    const n=Math.ceil(Math.hypot(w.b.x-w.a.x,w.b.z-w.a.z)/.8);
    if(north) {
      for(const y of [.4,.84,1.18])beam(C.teal,[w.a.x,y,w.a.z],[w.b.x,y,w.b.z],.05);
    } else {
      beam(C.cream,[w.a.x,.33,w.a.z],[w.b.x,.33,w.b.z],.23,.66);
      beam(C.wood,[w.a.x,.68,w.a.z],[w.b.x,.68,w.b.z],.25,.07);
      beam(C.leaf,[w.a.x,.91,w.a.z],[w.b.x,.91,w.b.z],.23,.42);
    }
    for(let i=0;i<=n;i++) {
      const t=i/n,x=w.a.x+(w.b.x-w.a.x)*t,z=w.a.z+(w.b.z-w.a.z)*t;
      box(north?C.dark:C.teal,[.065,1.26,.065],[x,.63,z]);
    }
  }
  // Two small planted seats behind the west/north zones, never in the NPC disk.
  for(const [x,z] of [[-6.8,-3.25],[5.7,-5.4]]) {
    box(C.cream,[.7,.35,.6],[x,.175,z]);
    for(const dx of [-.18,.18])box(C.leaf,[.28,.55,.35],[x+dx,.58,z]);
    boundary([x-.35,z-.3,x+.35,z+.3],.9,'planter');
  }
  b.finish();
  // Rounded chamfered car ends rather than stacked box-shaped carriages.
  const train=new THREE.Group();train.name='slow-train';const t=batchBuilder(train);
  for(const x of [-.64,.64]) {
    const shape=new THREE.Shape();
    shape.moveTo(-.57,.29);shape.lineTo(.57,.29);shape.lineTo(.57,.77);shape.lineTo(.42,1.02);shape.lineTo(-.42,1.02);shape.lineTo(-.57,.77);shape.closePath();
    const g=new THREE.ExtrudeGeometry(shape,{depth:.7,bevelEnabled:false});g.translate(x,0,-.35);t.add(C.cream,g);
    t.box(C.teal,[1.08,.11,.7],[x,1.02,0]);t.box(C.coral,[1.13,.1,.72],[x,.42,0]);
    for(const dx of [-.3,0,.3])for(const z of [-.36,.36])t.box(C.dark,[.2,.24,.018],[x+dx,.77,z]);
    for(const dx of [-.35,.35])t.box(C.dark,[.18,.2,.78],[x+dx,.25,0]);
  }
  for(const x of [-1.22,1.22]){t.box(C.dark,[.025,.26,.45],[x,.7,0]);for(const z of [-.25,.25])t.box(C.light,[.03,.08,.09],[x,.46,z]);}
  t.finish();train.position.set(0,.1,-7);group.add(train);home.group.add(group);
  // All solid roofs can support a deliberate jump; lower geometry remains ground
  // picking. Horizontal walls are explicit, never inferred from raycast meshes.
  const staticMeshes=group.children.filter(o=>o.isMesh);
  for(const mesh of staticMeshes)if(!colliders.includes(mesh) && mesh.material.type==='MeshToonMaterial')colliders.push(mesh);
  return {group,train,colliders,barriers,edgeBarriers,plan,update(time){train.position.x=Math.sin(time*plan.rail.speed)*plan.rail.travel;}};
}
