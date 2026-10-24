// Launches only local sandbox servers; never publishes a Site or modifies src/.
import { chromium } from '@playwright/test';
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
const root=process.cwd(),out=path.join(root,'docs/design/yuan-size-comparison-v1');
const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--enable-unsafe-swiftshader']});
try {for(const [id,port] of [['a',4286],['b',4287]]){
 const server=spawn(process.execPath,[path.join(root,'node_modules/vite/bin/vite.js'),'--host','127.0.0.1','--port',String(port),'--strictPort'],{cwd:path.join(root,'work/yuan-size',id),stdio:'ignore'});
 try{
  const url=`http://127.0.0.1:${port}`;let ready=false;for(let i=0;i<100;i++){try{await fetch(url);ready=true;break;}catch{await new Promise(r=>setTimeout(r,100));}}if(!ready)throw Error('Sandbox server failed');
  const page=await browser.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1});const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(url);await page.waitForFunction(()=>window.__skyisles);await page.locator('#title-screen .tap').click();
  await page.waitForFunction(()=>window.__skyisles.world.player.move.grounded);
  await page.locator('#panorama-btn').click();await page.waitForFunction(()=>window.__skyisles.world.panorama.mode==='overview',null,{timeout:60000});
  await page.screenshot({path:path.join(out,id,'panorama-pure.png')});
  const baseline=JSON.parse(fs.readFileSync(path.join(root,'src/data/yuan-layout.json')));
  await page.evaluate(bounds=>{const w=window.__skyisles.world;w.panorama.bounds=bounds;w.panorama.fit(innerWidth,innerHeight);},baseline.bounds);
  await page.waitForTimeout(250);await page.screenshot({path:path.join(out,id,'shared-scale-pure.png')});
  await page.evaluate(()=>{const w=window.__skyisles.world;w.panorama.bounds=w.bridges.bounds;w.panorama.fit(innerWidth,innerHeight);});
  await page.evaluate(()=>window.__skyisles.world.panorama.labelled=true);
  await page.waitForFunction(()=>[...document.querySelectorAll('.island-label')].filter(e=>!e.hidden).length===8);
  await page.screenshot({path:path.join(out,id,'panorama-labelled.png')});
  // Additional oblique photograph makes the retained island rocks/models visible.
  await page.evaluate(()=>{const w=window.__skyisles.world,c=w.panorama.ortho,b=w.bridges.bounds;w.panorama.labelled=false;c.position.set((b.minX+b.maxX)/2,220,(b.minZ+b.maxZ)/2+100);c.up.set(0,1,0);c.lookAt((b.minX+b.maxX)/2,0,(b.minZ+b.maxZ)/2);});
  await page.waitForTimeout(300);await page.screenshot({path:path.join(out,id,'panorama-oblique.png')});
  if(errors.length)throw Error(errors.join('\n'));fs.writeFileSync(path.join(out,id,'browser.json'),JSON.stringify({viewport:[1440,1100],pageErrors:errors,renderer:'actual Three.js scene with sandbox candidate geometry',screenshots:['panorama-pure.png','panorama-labelled.png','panorama-oblique.png','shared-scale-pure.png']},null,2));
  await page.close();console.log(id,'four actual 3D screenshots captured');
 }finally{server.kill('SIGTERM');}
}}finally{await browser.close();}
