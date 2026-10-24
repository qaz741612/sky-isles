// Capture the built first edition locally; no publication.
import { chromium, devices } from '@playwright/test';
import { spawn } from 'node:child_process';
import { mkdirSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';

const output = resolve(process.argv[2] || 'shots');
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
    await page.waitForTimeout(1800);
    await page.locator('#policy-menu summary').click();
    await page.screenshot({ path: resolve(output, mobile ? 'mobile-preview.png' : 'desktop-preview.png') });
    await page.locator('#policy-list').getByRole('button', { name: '交通大升級', exact: true }).click();
    await page.screenshot({ path: resolve(output, mobile ? 'mobile-policy.png' : 'desktop-policy.png') });
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
