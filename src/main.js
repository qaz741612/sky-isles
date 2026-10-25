// Sky Isles — boot, game loop, interactions, debug handle.
import * as THREE from 'three';
import { Panorama } from './sim/panorama.js';
import { cameraProfile } from './sim/camera-profile.js';
import { Rng } from './sim/rng.js';
import { ChimePuzzle, CHIMES, MURAL_ORDER } from './sim/puzzle.js';
import { AudioEngine } from './sim/audio.js';
import { worldCameraConstraint } from './sim/camera-clearance.js';
import { Player } from './sim/player.js';
import { UI } from './ui.js';
import { buildSky } from './world/sky.js';
import { ISLANDS, buildIslands, updateJumpPads } from './world/islands.js';
import { buildBridges } from './world/bridges.js';
import { buildClouds } from './world/clouds.js';
import { buildPolicyScenery } from './world/policy-scenery.js';
import { guardIndex } from './sim/walkways.js';
import { buildChimes } from './world/chimes.js';
import { loadStationModel } from './world/station-model.js';
import { buildTransport, TRANSPORT_NOTICE } from './world/transport.js';
import { PolicyUI, loadPolicies } from './policies.js';

const policyData = await loadPolicies();

const canvas = document.getElementById('scene');
const isMobile = window.matchMedia('(pointer: coarse)').matches || 'ontouchstart' in window;

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, isMobile ? 1.5 : 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.12;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 900);
camera.position.set(0, 6, 12);

const rng = new Rng(20260718);

// ----- world -----
const sky = buildSky(scene);
const islands = buildIslands(scene, rng);
const bridges = buildBridges(scene, islands.islands, rng);
const clouds = buildClouds(scene, rng);

const chimes = buildChimes(islands.islands);
let stationSource;
try { stationSource=await loadStationModel(); } catch(error) { document.getElementById('loading').textContent='車站模型載入失敗，請重新整理重試'; throw error; }
const transport = buildTransport(islands.islands[0],undefined,stationSource);
scene.updateMatrixWorld(true);
const props=buildPolicyScenery(islands.islands);
const allBarriers=[...bridges.barriers,...props.barriers,...transport.barriers];

const colliders = [
  ...islands.colliders,
  ...bridges.colliders,
  ...transport.colliders,
  ...props.colliders
];

// ----- sim -----
const puzzle = new ChimePuzzle();
const audio = new AudioEngine();
const player = new Player(scene, camera, colliders);
player.ceilingConstraint=transport.station.constrainHead;
scene.updateMatrixWorld(true);
player.cameraConstraint = worldCameraConstraint([...transport.cameraObstacles,...props.cameraObstacles]);
player.navigation = { islands: ISLANDS, barriers: allBarriers, nearby: guardIndex(allBarriers) };
// Separate portrait framing; both profiles retain the same orbit controller.
const initialView = cameraProfile(innerWidth, innerHeight);
Object.assign(player.orbit, initialView);
camera.fov = initialView.fov;
camera.updateProjectionMatrix();
const ui = new UI();
const policyUI = new PolicyUI(policyData, islands.islands, camera, ui);

const panoramaButton = document.getElementById('panorama-btn');
const exploreFog = scene.fog;
const panorama = new Panorama(camera,bridges.bounds,active=>{
 document.body.classList.toggle('panorama',active);
 ui.suspended=active;
 ui.resetInput();
 scene.fog=active?null:exploreFog;sky.setOverview(active);clouds.setOverview(active);
 panoramaButton.textContent=active?'返回探索':'全景';
 panoramaButton.setAttribute('aria-pressed',String(active));
});
panoramaButton.addEventListener('click',()=>{
 if(panorama.mode==='overview')panorama.leave();
 else if(!panorama.active && player.move.grounded && !policyUI.isOpen)panorama.enter();
 else if(!panorama.active)ui.hint('請在安全路面停穩後開啟全景',1800);
 panoramaButton.blur();
});

player.onJumpPad = () => {
  audio.boing();
  ui.hint('彈跳！按住跳躍即可滑翔', 1800);
};

let started = false;

// ----- chime playing -----
function playChime(index) {
  const chime = chimes.chimes[index];
  if (!chime) return null;
  const result = puzzle.play(index);
  chime.playPulse = 1;
  if (result.type === 'correct' || result.type === 'replay') {
    audio.bell(CHIMES[index].note);
    audio.setUnlocked(puzzle.unlocked);
  } else {
    audio.lowTone();
  }
  ui.setChimes(puzzle.unlocked, MURAL_ORDER);
  if (result.type === 'wrong') {
    ui.hint('請依照壁畫順序敲響風鈴', 2600);
  } else if (result.complete && result.type === 'correct') {
    audio.portalWhoosh();
    ui.hint('五組風鈴已完成！繼續探索八座政策島。', 4200);
  } else {
    ui.hint(`風鈴響起 — ${puzzle.unlocked} / ${MURAL_ORDER.length}`, 2000);
  }
  return result;
}

function tryInteract() {
  if(panorama.active)return;
  const near = chimes.nearest(player.pos);
  if (near) playChime(near.index);
}

// tap a chime directly (mobile friendly)
const tapRay = new THREE.Raycaster();
const tapNdc = new THREE.Vector2();
ui.onTap = (nx, ny) => {
  if (!started || policyUI.isOpen || panorama.active) return;
  tapNdc.set(nx, ny);
  tapRay.setFromCamera(tapNdc, camera);
  const hits = tapRay.intersectObjects(chimes.hitMeshes, false);
  if (hits.length) {
    const idx = hits[0].object.userData.chimeIndex;
    const c = chimes.chimes[idx];
    if (c.worldPos.distanceTo(player.pos) < 5.5) playChime(idx);
    else ui.hint('靠近一點即可敲響風鈴', 1800);
    return;
  }
  const islandHits = tapRay.intersectObjects([...islands.colliders,...props.pickMeshes,...transport.pickMeshes], false);
  const info = tapRay.intersectObjects(transport.interactives, false)[0];
  if (info && (!islandHits.length || info.distance <= islandHits[0].distance + .12)) {
    if (info.object.userData.transportInfo === 'vision') {
      policyUI.openSupplement('home', '交通政策願景', transport.plan.visionDisplay.topics, TRANSPORT_NOTICE);
    } else {
      const names = ['月', '星', '日', '浪', '葉'];
      policyUI.openSupplement('home', '風鈴文化牆', MURAL_ORDER.map(i => names[i]), '依文化牆由左至右的順序，尋找並敲響原有五座風鈴。');
    }
    return;
  }
  if (islandHits.length && islandHits[0].object.userData.island) {
    policyUI.open(islandHits[0].object.userData.island);
    return;
  }

};
ui.onInteract = tryInteract;
ui.bindCanvas(canvas);

// ----- start flow -----
ui.onStart(() => {
  ui.hideTitle();
  audio.ensure();
  audio.startAmbient();
  started = true;
  if (ui.isTouch) ui.showInstructions();
  else ui.hint('拖曳旋轉・滾輪縮放・點選政策入口', 3200);
});

// ----- resize -----
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.fov = cameraProfile(innerWidth, innerHeight).fov;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  panorama.fit(innerWidth,innerHeight);
});

// ----- debug handle for e2e / QA -----
window.__skyisles = {
  getState() {
    return {
      chimesUnlocked: puzzle.unlocked,
      islandCount: islands.islands.length,
      respawnCount: player.respawnCount,
      checkpoint: player.lastGrounded.toArray(),
      playerPos: { x: player.pos.x, y: player.pos.y, z: player.pos.z },
      panoramaMode: panorama.mode,
      started,
      muralOrder: [...MURAL_ORDER]
    };
  },
  teleport(x, y, z) {
    player.teleport(x, y, z);
  },
  playChime(index) {
    return playChime(index);
  },
  setOrbit(yaw, pitch, dist) {
    player.orbit.yaw = yaw;
    player.orbit.pitch = pitch;
    player.orbit.dist = dist;
  },
  start() {
    if (!started) {
      ui.hideTitle();
      started = true;
    }
  },
  world: { props, panorama, policyUI, scene, camera, renderer, islands, bridges, chimes, player, puzzle, transport, ui }
};

// ----- main loop -----
const clock = new THREE.Clock();
let firstFrame = true;
const playerCenter = new THREE.Vector3();

function frame() {
  requestAnimationFrame(frame);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  const input = started && !policyUI.isOpen && !panorama.active
    ? ui.poll(player.orbit)
    : { x: 0, z: 0, jumpPressed: false, jumpHeld: false };

  if(!panorama.active)player.update(dt, input, t);
  panorama.update(dt);
  panoramaButton.hidden=!started;

  playerCenter.copy(player.pos);
  playerCenter.y += 1.2;
  chimes.update(t, dt, started ? playerCenter : null);
  sky.update(t, dt);
  clouds.update(t, dt, panorama.camera);
  bridges.update(t);
  props.update(t, dt);
  transport.update(t);
  updateJumpPads(islands.jumpPads, t, dt);

  renderer.render(scene, panorama.camera);
  policyUI.camera=panorama.camera;
  policyUI.update(started, player.pos, panorama.active, panorama.labelled === true);

  if (firstFrame) {
    firstFrame = false;
    ui.hideLoading();
  }
}
frame();
