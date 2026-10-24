// Local-only sightseeing previews. Overview changes only the QA camera, never world scale.
import { chromium, devices } from '@playwright/test';
import { spawn } from 'node:child_process';
import { mkdirSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';

const output = resolve(process.argv[2] || 'docs/previews');
mkdirSync(output, { recursive: true });
const server = spawn(process.execPath, ['node_modules/vite/bin/vite.js', 'preview', '--host', '127.0.0.1', '--port', '4186', '--strictPort'], { stdio: 'ignore' });
let browser;
try {
  let ready = false;
  for (let attempt = 0; attempt < 50; attempt++) {
    try { ready = (await fetch('http://127.0.0.1:4186')).ok; } catch { /* startup */ }
    if (ready) break;
    await new Promise((r) => setTimeout(r, 200));
  }
  if (!ready) throw new Error('Preview server did not start');
  browser = await chromium.launch(existsSync('/usr/bin/chromium') ? { executablePath: '/usr/bin/chromium', args: ['--no-sandbox', '--enable-unsafe-swiftshader'] } : {});
  for (const mobile of [false, true]) {
    const context = await browser.newContext(mobile ? { ...devices['iPhone 15 Pro Max'] } : { viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', (error) => errors.push(String(error)));
    page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
    await page.goto('http://127.0.0.1:4186');
    await page.waitForFunction(() => window.__skyisles);
    await page.locator('#title-screen .tap').click();
    if (mobile) await page.locator('#help-close').click();
    await page.waitForTimeout(1800);

    await page.screenshot({ path: resolve(output, mobile ? 'skywalk-mobile.png' : 'skywalk-desktop.png') });
    if (mobile) {
      await page.evaluate(() => {
        const w=window.__skyisles.world,p=w.bridges.plans[0],c=p.points[3],next=p.points[4];
        w.player.teleport(c.x,c.y+0.05,c.z);
        Object.assign(w.player.orbit,{yaw:Math.atan2(-(next.x-c.x),-(next.z-c.z)),pitch:0.58,dist:12});
        for(let i=0;i<60;i++)w.player.update(1/60,{x:0,z:0,jumpHeld:false,jumpPressed:false},i/60);
      });
      await page.waitForTimeout(800);
      await page.screenshot({path:resolve(output,'skywalk-mobile-path.png')});
    } else {
      // An explicitly documented QA overview, not the player's initial camera.
      await page.evaluate(() => {
        const w=window.__skyisles.world,original=w.ui.poll.bind(w.ui);
        w.ui.poll=orbit=>{const input=original(orbit);Object.assign(orbit,{dist:100,pitch:0.95,yaw:0.6});return input;};
        Object.assign(w.player.orbit,{dist:100,pitch:0.95,yaw:0.6});
        for(let i=0;i<70;i++)w.player.update(1/60,{x:0,z:0,jumpHeld:false,jumpPressed:false},i/60);
      });
      await page.waitForTimeout(800);
      await page.screenshot({path:resolve(output,'skywalk-overview.png')});
    }
    const stats = await page.evaluate(() => {
      const s = window.__skyisles.world;
      return { calls: s.renderer.info.render.calls, triangles: s.renderer.info.render.triangles, themeMeshes: s.transport.group.children.length };
    });
    console.log(JSON.stringify({ mobile, ...stats }));
    for (const path of ['/favicon.ico', '/data/policies.json', '/LICENSE']) {
      const response = await page.request.get(`http://127.0.0.1:4186${path}`);
      if (!response.ok()) throw new Error(`${path}: ${response.status()}`);
    }
    if (errors.length) throw new Error(errors.join('\n'));
    console.log(`${mobile ? 'Mobile' : 'Desktop'} built preview captured, no console errors; favicon/JSON/LICENSE HTTP 200.`);
    await context.close();
  }
} finally {
  await browser?.close();
  server.kill();
}
