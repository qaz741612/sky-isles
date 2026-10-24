import { test, expect } from '@playwright/test';

test('transport scene preserves policy picking, jumping, orbit and bounded train animation', async ({ page }) => {
  await page.goto('/');
  await page.waitForFunction(() => window.__skyisles);
  await page.locator('#title-screen .tap').click();
  await page.waitForTimeout(1500);
  const before = await page.evaluate(() => {
    const w = window.__skyisles.world;
    return { train: w.transport.train.position.x, yaw: w.player.orbit.yaw,
      notice: w.transport.group.userData.notice,
      colliders: w.transport.colliders.map((c) => c.name),
      owners: w.islands.islands.filter((i) => i.group.getObjectByName('transport-theme')).map((i) => i.name) };
  });
  expect(before.owners).toEqual(['home']);
  expect(before.colliders).toEqual(['station-platform', 'road-viaduct']);
  expect(before.notice).toContain('非實際工程');
  await expect.poll(() => page.evaluate(() => window.__skyisles.world.transport.train.position.x)).not.toBe(before.train);
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
    const p = w.islands.islands[0].pos.clone().set(-1.4, 1.1, -3.2).project(w.camera);
    return { x: (p.x + 1) * innerWidth / 2, y: (1 - p.y) * innerHeight / 2 };
  });
  await page.mouse.click(xy.x, xy.y);
  await expect(page.locator('#policy-title')).toHaveText('交通大升級');
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.locator('#policy-content')).toContainText('不代表實際工程已核定或完成');
});
