// V4 geometry-specific scenarios were superseded by elevated-station.e2e.js.
// Retain an explicit regression for identity and retained puzzle metadata.
import {test,expect} from './helpers/software-qa.js';
test('V9 replaces legacy transport geometry without changing the policy or chime identities',async({page})=>{
 test.setTimeout(240000);await page.goto('/');await page.waitForFunction(()=>window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:150000});
 const result=await page.evaluate(()=>{const w=window.__skyisles.world;w.renderer.render=()=>{};return{source:w.transport.station.config.sourceCommit,scale:w.transport.station.config.scale,ids:w.transport.plan.gateRoutes,murals:w.islands.murals.map(m=>m.userData.chimeIndex),chimes:w.chimes.chimes.length,oldTrain:!!w.transport.group.getObjectByName('slow-train'),oldPlatform:!!w.transport.group.getObjectByName('station-platform')};});
 expect(result).toEqual({source:'ca94f48bccdc89a00e5a0688479214d6114915d6',scale:1,ids:['S09','S10','S15','S18'],murals:[2,4,0,3,1],chimes:5,oldTrain:false,oldPlatform:false});
});
