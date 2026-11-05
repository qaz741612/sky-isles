// Geometry-only Node fixtures use the exact generated game colliders. Separate
// GLTFLoader tests inspect real final GLBs; browsers load all actual materials.
import * as THREE from 'three';
import {buildR21Places}from'../../src/world/bdeh-r21.js';
export function r21Replacements(islands){const built=buildR21Places(Object.fromEntries([...'BDEH'].map(c=>[c,new THREE.Group()])),islands);return Object.fromEntries(Object.values(built).map(p=>[p.config.name,p]));}
