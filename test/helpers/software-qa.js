import {test as base,expect} from '@playwright/test';
// Opt-in software-GPU engineering mode. Keep the native rAF, input, physics,
// animation, UI and camera. Submit the first real frame and explicit visual
// samples only; do not build an unbounded SwiftShader command queue.
// Hardware performance and continuous visual smoothness are not proved here.
export const test=base.extend({
 page:async({page},use)=>{
  if(process.env.SKY_SOFTWARE_QA==='1')await page.addInitScript(()=>{
   let api;
   Object.defineProperty(window,'__skyisles',{configurable:true,get:()=>api,set:value=>{
    api=value;const renderer=value.world.renderer,native=renderer.render.bind(renderer);let first=true;
    renderer.qaDraw=native;renderer.render=(...args)=>{if(first){first=false;return native(...args);}};
   }});
  });
  await use(page);
 }
});
export {expect};
