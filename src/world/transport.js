// MIT. Locked open-platform V9 asset plus retained policy and mural interaction.
import * as THREE from 'three';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';
import {canvasTexture} from './toon.js';
import {placeMaterial,PALETTE} from './place-kit.js';
import authoredPlan from '../data/transport.json' with {type:'json'};
import surface from '../data/yuan-surface.json' with {type:'json'};
import {buildElevatedStation,ELEVATED_STATION} from './elevated-station.js';
const plan={...authoredPlan,station:{...authoredPlan.station,entrance:ELEVATED_STATION.entrance,entryRecess:ELEVATED_STATION.entryRecess}};
export const TRANSPORT_NOTICE='交通政策願景示意，非實際工程核定或完工資訊';
export const TRANSPORT_PLAN=plan;
const C=PALETTE;
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
      const mesh = new THREE.Mesh(mergeGeometries(parts), placeMaterial(color));
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


export function transportEdgeSegments(){return surface.barriers.filter(w=>w.island==='home');}
export function buildTransport(home,makeSign=textSign,source){
 if(home.name!=='home')throw new Error('Transport scene belongs only to home');
 const group=new THREE.Group();group.name='transport-theme';group.userData.notice=TRANSPORT_NOTICE;group.userData.plan=plan;
 const station=buildElevatedStation(source);group.add(station.group);
 const foundation=home.group.getObjectByName('transport-foundation');if(foundation)foundation.visible=false; // remains a reliable physics floor
 const b=batchBuilder(group);
 function sign(text,w,h,x,y,z){const mesh=makeSign(text,w,h);mesh.position.set(x,y,z);mesh.userData.island='home';group.add(mesh);}
 // Existing five clues are mounted on the west facade, away from the four gates.
 b.box(C.wood,[3.10,.82,.055],[-5,1.02,-2.965]);
 for(const y of[.62,1.47])b.box(C.teal,[3.18,.045,.045],[-5,y,-2.91]);
 sign('五音線索・點選閱讀',2.1,.18,-5,.52,-2.81);
 sign('月台展示・暫不開放',.99,.2,-8.6,.82,-3.035);
 sign('電梯展示・暫不開放',1.38,.18,7.7,.7,-3.36);
 sign('交通政策願景示意',1.15,.16,5.5,1.75,-2.55);
 b.finish();
 const interactives=[];
 for(const[kind,size,pos]of[['vision',[.72,1.72],[5.5,1.05,-2.555]],['mural',[3.3,1.04],[-5,1,-2.79]]]){
  const hit=new THREE.Mesh(new THREE.PlaneGeometry(...size),new THREE.MeshBasicMaterial({visible:false,side:THREE.DoubleSide}));hit.position.set(...pos);hit.userData.transportInfo=kind;group.add(hit);interactives.push(hit);
 }
 home.group.add(group);group.updateMatrixWorld(true);
 const pickMeshes=[];group.traverse(m=>{if(m.isMesh&&m.visible&&m.material.visible!==false)pickMeshes.push(m);});
 return {group,station,train:source,colliders:station.colliders,barriers:station.barriers,edgeBarriers:[],cameraObstacles:station.cameraObstacles,pickMeshes,plan,interactives,stats:station.stats,update(){}};
}
