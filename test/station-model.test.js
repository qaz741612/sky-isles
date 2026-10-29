import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {URL} from 'node:url';
import {createHash} from 'node:crypto';
import * as THREE from 'three';
import {source} from './helpers/station-fixture.js';
import {buildStationModel,STATION_MODEL} from '../src/world/station-model.js';

test('supplied GLB is unchanged; full station architecture, canopy and lettering retain original materials',()=>{
 const data=fs.readFileSync(new URL('../public/prototypes/transport-station/transport-station.glb',import.meta.url));
 assert.equal(createHash('sha256').update(data).digest('hex'),STATION_MODEL.sha256);
 const station=buildStationModel(source),names=new Set(station.included);
 source.traverse(o=>{if(o.isMesh&&o.name.startsWith('Architecture__'))assert.ok(names.has(o.name),o.name);});
 for(const name of ['Attached_platform_roof','Platform__Woven_timber','Platform__Oiled_oak','Station_interior_floor','Wayfinding__Train_blue_stripe'])assert.ok(names.has(name));
 assert.equal(station.meshes.length,16);assert.equal(station.triangles,5368);
 assert.ok(station.included.every(n=>!/^Train__|^Scale__|^Landscape__/.test(n)));
 for(const mesh of station.meshes){assert.equal(mesh.material,source.getObjectByName(mesh.name).material);assert.ok(mesh.material.isMeshStandardMaterial);assert.ok(mesh.geometry.attributes.normal);}
 const size=station.bounds.getSize(new THREE.Vector3());assert.ok(size.x>10&&size.x<10.3);assert.ok(size.y>3.8&&size.y<4);assert.ok(size.z>5&&size.z<5.3);assert.ok(Math.abs(station.bounds.min.y)<1e-6);
});

test('station fits radius 9 without changing source proportions; original doorway clears the unchanged player',()=>{
 const station=buildStationModel(source),scale=STATION_MODEL.scale;let radius=0;
 for(const mesh of station.meshes){const p=mesh.geometry.attributes.position;for(let i=0;i<p.count;i++)radius=Math.max(radius,Math.hypot(p.getX(i),p.getZ(i)));}
 assert.ok(radius<9,`furthest original vertex ${radius}`);
 // Original GLB lintel bottom 2.645, original floor top .37: no edits to either.
 const clearHeight=(2.645-.37)*scale;assert.ok(clearHeight>1.65);assert.ok(clearHeight>STATION_MODEL.capsuleHeight+.05);
 const transform=new THREE.Matrix4().compose(new THREE.Vector3(...STATION_MODEL.position),new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),STATION_MODEL.yaw),new THREE.Vector3().setScalar(scale));
 const scales=new THREE.Vector3().setFromMatrixScale(transform);assert.ok(scales.distanceTo(new THREE.Vector3(scale,scale,scale))<1e-9);
 assert.ok(station.barriers.length>200);assert.ok(station.barriers.every(w=>w.height>0&&Number.isFinite(w.a.x)&&w.source));
});

test('actual GLB lintel and canopy undersides stop rising heads without changing movement outside the station',()=>{
 const station=buildStationModel(source),p=new THREE.Vector3(-1.277,.7,-3.8),move={vy:7};station.group.updateMatrixWorld(true);
 assert.equal(station.constrainHead(p,.2479,move),true);assert.equal(move.vy,0);assert.ok(p.y<.4,`lintel head clearance ${p.y}`);
 const canopy=new THREE.Vector3(3.3,1.2,-6.35),canopyMove={vy:7};assert.equal(station.constrainHead(canopy,.12,canopyMove),true);assert.ok(canopy.y<.7);
 const outside=new THREE.Vector3(0,1,3.5),outMove={vy:7};assert.equal(station.constrainHead(outside,0,outMove),false);assert.equal(outMove.vy,7);assert.equal(outside.y,1);
 const falling=new THREE.Vector3(-1.277,.2,-3.95),fallMove={vy:-3};assert.equal(station.constrainHead(falling,.3,fallMove),false);assert.equal(fallMove.vy,-3);
});
