import { test, expect } from '@playwright/test';

test('transport scene preserves policy picking, jumping, orbit and locked elevated train display', async ({ page }) => {
  await page.goto('/');
  await page.waitForFunction(() => window.__skyisles&&document.querySelector('#loading').classList.contains('hidden'),null,{timeout:150000});await page.evaluate(()=>{window.__skyisles.world.renderer.render=()=>{};});
  await page.locator('#title-screen .tap').click();
  if (await page.locator('#touch-help').isVisible()) await page.locator('#help-close').click();
  await page.waitForTimeout(1500);
  const before = await page.evaluate(() => {
    const w = window.__skyisles.world;
    return { train: w.transport.train.position.x, yaw: w.player.orbit.yaw,
      notice: w.transport.group.userData.notice,
      colliders: w.transport.colliders.map((c) => c.name),
      owners: w.islands.islands.filter((i) => i.group.getObjectByName('transport-theme')).map((i) => i.name) };
  });
  expect(before.owners).toEqual(['home']);
  expect(before.colliders).toEqual(expect.arrayContaining(['station-upper-support']));
  expect(before.notice).toContain('非實際工程');
  expect(await page.evaluate(() => window.__skyisles.world.transport.train.position.x)).toBe(before.train); // locked GLB display, no synthetic old train animation
  await page.keyboard.down('Space');
  await expect.poll(() => page.evaluate(() => window.__skyisles.getState().playerPos.y)).toBeGreaterThan(0.4);
  await page.keyboard.up('Space');
  // Canvas drag rotates the original orbit controller without opening a policy.
  await page.mouse.move(160, 420); await page.mouse.down();
  await page.mouse.move(230, 450, { steps: 4 }); await page.mouse.up();
  await expect.poll(() => page.evaluate(() => window.__skyisles.world.player.orbit.yaw)).not.toBe(before.yaw);
  await expect(page.getByRole('dialog')).not.toBeVisible();
  // Click station geometry's screen position. Existing ground picking still works underneath.
  await page.evaluate(() => {
    const w = window.__skyisles.world;
    w.player.teleport(0, 0.5, 3.5);
    w.player.orbit.yaw = 0.1;
  });
  await page.waitForTimeout(1800);
  const xy = await page.evaluate(() => {
    const w = window.__skyisles.world;
    const p = w.islands.islands[0].pos.clone().set(0, 1.3, -3.0).project(w.camera);
    return { x: (p.x + 1) * innerWidth / 2, y: (1 - p.y) * innerHeight / 2 };
  });
  await page.mouse.click(xy.x, xy.y);
  await expect(page.locator('#policy-title')).toHaveText('交通大升級');
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.locator('#policy-content')).toContainText('不代表實際工程已核定或完成');
});
