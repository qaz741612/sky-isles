// Original procedural models, MIT. Theme illustration, not an approved project.
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { toonMaterial, canvasTexture } from './toon.js';
import plan from '../data/transport.json' with { type: 'json' };
import surface from '../data/yuan-surface.json' with { type: 'json' };

export const TRANSPORT_NOTICE = '交通政策願景示意，非實際工程核定或完工資訊';
export const TRANSPORT_PLAN = plan;
const C = { cream: 0xffedcf, teal: 0x527f80, dark: 0x38555e, coral: 0xd98670, stone: 0xc7bbad, road: 0x70818a, leaf: 0x719e83, light: 0xffdca0, wood: 0xb88d64, rush: 0xd7bd91, blue: 0x82b7be };

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
  // West-set compact station leaves a real view corridor to the northern train.
  // Solids and all freestanding elements share explicit horizontal collision.
  for (const solid of plan.stationSolids) {
    const [x0,z0,x1,z1]=solid.bounds;
    box(C.cream,[x1-x0,solid.height,z1-z0],[(x0+x1)/2,solid.height/2,(z0+z1)/2]);
    boundary(solid.collisionBounds||solid.bounds,solid.height,solid.name);
  }
  deck('station-platform',plan.platform.size,plan.platform.center,C.cream);
  deck('entrance-floor',[1.7,.04,2.15],[-1.8,.02,-4.35],C.wood);
  const roof=plan.station.roofProfile;
  for(let i=1;i<roof.length;i++){
    const [x,y]=roof[i-1],[xx,yy]=roof[i],angle=Math.atan2(yy-y,xx-x);
    box(C.teal,[Math.hypot(xx-x,yy-y)+.025,.16,plan.station.roofDepth],[(x+xx)/2,(y+yy)/2,plan.station.roofZ],angle);
    for(const z of [-5.93,-3.36])beam(C.wood,[x,y-.12,z],[xx,yy-.12,z],.1,.14);
  }
  // A restrained folded fascia, supported at two real columns, no second roof.
  for(const [x,z]of plan.station.columns){
    box(C.teal,[.1,2.52,.1],[x,1.26,z]);
    boundary([x-.05,z-.05,x+.05,z+.05],2.52,'canopy-column');
  }
  for(const x of [-2.61,-.99])box(C.wood,[.09,2.25,.18],[x,1.125,-3.58]);
  box(C.coral,[1.7,.14,.23],[-1.8,2.28,-3.55]);
  box(C.dark,[1.58,1.9,.035],[-1.8,1.0,-4.77]);
  // Front, west, east and rear receive layered apertures and trim.
  box(C.dark,[1.7,1.2,.055],[-3.7,1.35,-3.61]);
  box(C.blue,[1.5,.95,.06],[-3.7,1.4,-3.57]);
  box(C.blue,[.05,1.03,.95],[-4.825,1.4,-4.35]);
  box(C.blue,[.055,1.02,.95],[-.72,1.4,-4.35]);
  box(C.dark,[3.7,.7,.055],[-2.8,1.4,-5.09]);
  box(C.blue,[3.5,.52,.06],[-2.8,1.42,-5.09]);
  for(const x of [-4.4,-3.65,-2.9,-2.15,-1.4]){
    box(C.wood,[.065,.68,.1],[x,1.4,-5.08]);
  }
  for(const z of [-4.8,-4.35,-3.9])box(C.wood,[.1,1.12,.055],[-.73,1.4,z]);
  box(C.stone,[plan.station.size[0],.18,plan.station.size[1]],[plan.station.center[0],.09,plan.station.center[2]]);
  // Two sides of one corner screen. Alternating normal offsets make an actual
  // over/under weave with thick, coarse strips rather than repeated triangles.
  function weave(spec,west=false){
    const {origin,span,height}=spec,pitch=plan.weave.pitch;
    const point=(u,y,depth)=>west?[origin[0]-depth,origin[1]+y,origin[2]+u]:[origin[0]+u,origin[1]+y,origin[2]+depth];
    const cols=Math.round(span/pitch),rows=Math.round(height/pitch),du=span/cols,dy=height/rows;
    for(let j=0;j<=rows;j++)for(let i=0;i<cols;i++){
      const d=((i+j)%2?1:-1)*plan.weave.depthOffset;
      beam(C.wood,point(i*du,j*dy,d),point((i+1)*du,j*dy,d),.05,plan.weave.stripWidth);
    }
    for(let i=0;i<=cols;i++)for(let j=0;j<rows;j++){
      const d=((i+j)%2?-1:1)*plan.weave.depthOffset;
      beam(C.rush,point(i*du,j*dy,d),point(i*du,(j+1)*dy,d),west?.05:plan.weave.stripWidth,west?plan.weave.stripWidth:.05);
    }
  }
  weave(plan.weave.front);weave(plan.weave.west,true);
  sign('苑裡交通願景',1.65,.24,-1.8,2.64,-3.23);
  // Unified arrival court: all four gates remain direct, open grass/deck links.
  const court=new THREE.Shape();plan.plazaOutline.forEach(([x,z],i)=>i?court.lineTo(x,-z):court.moveTo(x,-z));court.closePath();
  const paving=new THREE.ShapeGeometry(court);paving.rotateX(-Math.PI/2);paving.translate(0,.012,0);b.add(C.stone,paving);
  // Broad stone bands guide the eye to the recessed entrance, not arrow decals.
  for(const z of [-2.5,-1.7,-.9])box(C.cream,[8.2,.006,.035],[-.3,.016,z]);
  for(const x of [-2.7,-.8])box(C.wood,[.1,.008,3.4],[x,.018,-1.7]);
  // Lower independent culture wall is a place to pause, separate from the door.
  const mb=plan.murals.baseBounds;boundary(mb,1.6,'culture-wall');
  box(C.cream,[mb[2]-mb[0],.55,mb[3]-mb[1]],[(mb[0]+mb[2])/2,.275,(mb[1]+mb[3])/2]);
  // Blank wooden backs prevent the original box texture showing the clue order in reverse.
  for(const x of plan.murals.x)box(C.wood,[.73,.87,.035],[x,plan.murals.y,plan.murals.z-.08]);
  for(const y of [.62,1.66])beam(C.wood,[mb[0],y,-4.28],[mb[2],y,-4.28],.08);
  for(const x of [mb[0],mb[2]])box(C.teal,[.07,1.68,.07],[x,.84,-4.28]);
  sign('五音線索・點選閱讀',2.2,.21,2.25,.35,-4.14);
  // Short titles and geometric transport icons; long topics are read in the
  // existing responsive modal, never tiny paragraphs on a 3D board.
  const vb=plan.visionDisplay.bounds,[vx,,vz]=plan.visionDisplay.position;
  const displayBox=(color,size,p)=>box(color,size,[p[0]+vx-2,p[1],p[2]+vz+3.25]);
  const displaySign=(text,w,h,x,y,z)=>sign(text,w,h,x+vx-2,y,z+vz+3.25);boundary(vb,1.42,'vision-display');
  displayBox(C.teal,[1.9,1.28,.33],[2,.64,-3.285]);
  displayBox(C.cream,[1.98,.12,.43],[2,1.31,-3.285]);
  displaySign('交通政策願景示意',1.8,.23,2,1.3,-3.045);
  displaySign('點選閱讀・非核定或完工工程',1.8,.15,2,.15,-3.045);
  // Four simple icon tiles: rail, platform, parking and coastal-road link.
  for(const x of [1.34,1.78,2.22,2.66]){
    displayBox(C.cream,[.35,.56,.025],[x,.75,-3.105]);
    displayBox(C.coral,[.2,.04,.03],[x,.54,-3.08]);
  }
  for(const x of [1.29,1.39])displayBox(C.teal,[.045,.3,.03],[x,.78,-3.075]);
  displayBox(C.teal,[.26,.06,.03],[1.78,.7,-3.075]);displayBox(C.teal,[.26,.06,.03],[1.78,.86,-3.075]);
  displayBox(C.teal,[.045,.3,.03],[2.16,.78,-3.075]);displayBox(C.teal,[.14,.05,.03],[2.23,.9,-3.075]);displayBox(C.teal,[.14,.05,.03],[2.23,.77,-3.075]);displayBox(C.teal,[.045,.15,.03],[2.28,.84,-3.075]);
  for(const x of [2.59,2.73])displayBox(C.teal,[.04,.33,.03],[x,.78,-3.075]);
  // North display railway. Moving car envelope is entirely inside the barrier.
  const [rx,,rz]=plan.rail.center;
  box(C.road,[plan.rail.length,.055,1.06],[rx,.04,rz]);
  for(let i=0;i<25;i++)box(C.wood,[.11,.055,.93],[rx-3.15+i*.263,.1,rz]);
  for(const z of [rz-.32,rz+.32])box(C.light,[plan.rail.length,.065,.065],[rx,.155,z]);
  for(const x of [rx-3.28,rx+3.28])box(C.coral,[.12,.3,1],[x,.22,rz]);
  boundary(plan.rail.exclusion,1.25,'rail-exclusion');
  for(const w of barriers.filter(w=>w.kind==='rail-exclusion')){
    beam(C.stone,[w.a.x,.13,w.a.z],[w.b.x,.13,w.b.z],.14,.26);
    beam(C.teal,[w.a.x,1.17,w.a.z],[w.b.x,1.17,w.b.z],.045);
    const n=Math.ceil(Math.hypot(w.b.x-w.a.x,w.b.z-w.a.z)/1.45);
    for(let i=0;i<=n;i++){const t=i/n;box(C.teal,[.045,1.24,.045],[w.a.x+(w.b.x-w.a.x)*t,.62,w.a.z+(w.b.z-w.a.z)*t]);}
  }
  for(let i=0;i<25;i++)box(C.light,[.14,.008,.065],[-2.3+i*.28,.125,-6.22]);
  // A single east-side viewing seat, facing west: off the continuous platform access lane.
  const eb=plan.bench.bounds;boundary(eb,plan.bench.height,'viewing-seat');
  box(C.wood,[.5,.12,1.3],[5.7,.47,-5.55]);box(C.wood,[.07,.46,1.3],[5.93,.73,-5.55]);
  for(const z of [-6,-5.1])box(C.teal,[.4,.38,.07],[5.7,.2,z]);
  // Exact V3 island boundary retained, with fewer, lighter lines and posts.
  const edgeBarriers=transportEdgeSegments();barriers.push(...edgeBarriers);
  const posts=new Set();
  for(const w of edgeBarriers){
    const north=(w.a.z+w.b.z)/2 < -2.5;
    beam(C.cream,[w.a.x,.3,w.a.z],[w.b.x,.3,w.b.z],.21,.6);
    beam(C.wood,[w.a.x,.62,w.a.z],[w.b.x,.62,w.b.z],.22,.055);
    beam(C.teal,[w.a.x,1.2,w.a.z],[w.b.x,1.2,w.b.z],.04);
    // Green is grouped in a few rim patches; never scattered through the court.
    if(!north&&(w.a.x+w.b.x)/2>3.7)beam(C.leaf,[w.a.x,.79,w.a.z],[w.b.x,.79,w.b.z],.21,.3);
    for(const p of [w.a,w.b]){const key=`${p.x.toFixed(4)},${p.z.toFixed(4)}`;if(posts.has(key))continue;posts.add(key);box(C.teal,[.045,1.27,.045],[p.x,.635,p.z]);}
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
  t.finish();train.position.set(plan.rail.center[0],.1,plan.rail.center[2]);group.add(train);home.group.add(group);
  // All solid roofs can support a deliberate jump; lower geometry remains ground
  // picking. Horizontal walls are explicit, never inferred from raycast meshes.
  const staticMeshes=group.children.filter(o=>o.isMesh);
  for(const mesh of staticMeshes)if(!colliders.includes(mesh) && mesh.material.type==='MeshToonMaterial')colliders.push(mesh);
  const interactives=[];
  for(const [kind,size,pos]of [['vision',[2,1.5],[plan.visionDisplay.position[0],.8,plan.visionDisplay.position[2]+.215]],['mural',[4.35,1.5],[2.25,.95,-4.08]]]){
    const hit=new THREE.Mesh(new THREE.PlaneGeometry(...size),new THREE.MeshBasicMaterial({visible:false,side:THREE.DoubleSide}));hit.position.set(...pos);hit.userData.transportInfo=kind;group.add(hit);interactives.push(hit);
  }
  return {group,train,colliders,barriers,edgeBarriers,plan,interactives,update(time){train.position.x=plan.rail.center[0]+Math.sin(time*plan.rail.speed)*plan.rail.travel;}};
}
