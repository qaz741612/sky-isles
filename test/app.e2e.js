import { test, expect } from '@playwright/test';

async function waitForWorld(page) {
  await page.goto('/');
  await page.waitForFunction(() => window.__skyisles && window.__skyisles.getState, null, { timeout: 60_000 });
  // skip the title screen (audio stays off; no gesture needed for rendering)
  await page.evaluate(() => window.__skyisles.start());
  await page.waitForTimeout(1500);
}

test.describe('苑裡政策島', () => {
  test('loads without console errors and renders non-uniform pixels', async ({ page }) => {
    const errors = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    page.on('pageerror', (err) => errors.push(String(err)));
    await waitForWorld(page);

    const canvas = page.locator('canvas#scene');
    await expect(canvas).toBeVisible();

    // a rich pastel scene compresses poorly: screenshot must be sizable
    const shotA = await page.screenshot();
    expect(shotA.length).toBeGreaterThan(30_000);

    // the world is alive: two frames apart must differ (clouds drift, leaves fall)
    await page.waitForTimeout(800);
    const shotB = await page.screenshot();
    expect(shotB.equals(shotA)).toBeFalsy();

    // non-uniform pixels straight from the canvas (render + readback in one
    // synchronous task, so no preserveDrawingBuffer is needed)
    const varied = await page.evaluate(() => {
      const { renderer, scene, camera } = window.__skyisles.world;
      renderer.render(scene, camera);
      const c = renderer.domElement;
      const g = document.createElement('canvas');
      g.width = 64;
      g.height = 64;
      const ctx = g.getContext('2d');
      ctx.drawImage(c, 0, 0, 64, 64);
      const data = ctx.getImageData(0, 0, 64, 64).data;
      const first = `${data[0]},${data[1]},${data[2]}`;
      let different = 0;
      for (let i = 4; i < data.length; i += 4) {
        if (`${data[i]},${data[i + 1]},${data[i + 2]}` !== first) different++;
      }
      return different;
    });
    expect(varied).toBeGreaterThan(200);
    expect(errors).toEqual([]);
  });

  test('getState exposes the core game state', async ({ page }) => {
    await waitForWorld(page);
    const state = await page.evaluate(() => window.__skyisles.getState());
    expect(state.chimesUnlocked).toBe(0);
    expect(state.islandCount).toBe(8);
    expect(typeof state.playerPos.x).toBe('number');
    expect(state.playerPos.y).toBeGreaterThan(-40);
    expect(state.muralOrder).toHaveLength(5);
  });

  test('all eight policies open from the menu and have no invented content', async ({ page }) => {
    await waitForWorld(page);
    const names = ['交通大升級','安心生養','幸福養老','產業青年','宜居環境','智慧公所','治水防災','教育發展'];
    for (const name of names) {
      await page.locator('#policy-menu summary').click();
      await page.locator('#policy-list').getByRole('button', { name, exact: true }).click();
      await expect(page.getByRole('dialog')).toBeVisible();
      await expect(page.locator('#policy-title')).toHaveText(name);
      await expect(page.locator('#policy-content')).toContainText('政策內容尚未提供，待補充。');
      await page.getByRole('button', { name: '關閉政策介紹' }).click();
      await expect(page.getByRole('dialog')).not.toBeVisible();
    }
    const response = await page.request.get('/favicon.ico');
    expect(response.status()).toBe(200);
    expect(response.headers()['content-type']).toMatch(/image/);
    const icon = await response.body();
    expect([...icon.subarray(0, 4)]).toEqual([0, 0, 1, 0]);
  });

  test('world label opens matching policy and Escape closes the dialog', async ({ page }) => {
    await waitForWorld(page);
    const label = page.locator('.island-label:visible').first();
    const name = await label.textContent();
    await label.click();
    await expect(page.locator('#policy-title')).toHaveText(name);
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('teleport moves the player and fall respawns at last ground', async ({ page }) => {
    await waitForWorld(page);
    await page.evaluate(() => window.__skyisles.teleport(26, 6.5, -14)); // tree isle
    await page.waitForTimeout(400);
    let state = await page.evaluate(() => window.__skyisles.getState());
    expect(Math.abs(state.playerPos.x - 26)).toBeLessThan(1.5);
    expect(Math.abs(state.playerPos.z - -14)).toBeLessThan(1.5);

    await expect.poll(() => page.evaluate(() => window.__skyisles.world.player.move.grounded)).toBe(true);

    // drop into the void -> respawn back near the tree isle (last grounded)
    await page.evaluate(() => window.__skyisles.teleport(0, -50, 0));
    await expect
      .poll(async () => page.evaluate(() => window.__skyisles.getState().playerPos.y), { timeout: 10_000 })
      .toBeGreaterThan(-40);
    state = await page.evaluate(() => window.__skyisles.getState());
    expect(Math.abs(state.playerPos.x - 26)).toBeLessThan(3);
  });
});
