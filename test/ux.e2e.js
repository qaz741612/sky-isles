import { test, expect } from './helpers/software-qa.js';

async function enter(page) {
  await page.goto('/'); await page.waitForFunction(() => window.__skyisles);
  await page.locator('#title-screen .tap').click();
  await page.waitForTimeout(1600);
}
const overlap = (a, b) => a.x < b.x+b.width && a.x+a.width > b.x && a.y < b.y+b.height && a.y+a.height > b.y;

test('menu collapses, exposes eight policies and avoids touch controls; home label is a HUD entry', async ({ page, isMobile }) => {
  await enter(page);
  const menu = page.locator('#policy-menu');
  await expect(menu).not.toHaveAttribute('open', '');
  const summary = menu.locator('summary');
  await expect(summary).toContainText('八大政策');
  const initial = await page.locator('#policy-nav').boundingBox();
  await summary.click();
  const buttons = page.locator('#policy-list button');
  await expect(buttons).toHaveCount(8);
  for (const name of ['交通大升級','安心生養','幸福養老','產業青年','宜居環境','智慧公所','治水防災','教育發展']) {
    await expect(buttons.filter({ hasText: name })).toBeVisible();
  }
  if (isMobile) {
    const nav = await page.locator('#policy-nav').boundingBox();
    for (const id of ['#joystick','#jump-btn']) expect(overlap(nav, await page.locator(id).boundingBox())).toBe(false);
  }
  await summary.click();
  const collapsed = await page.locator('#policy-nav').boundingBox();
  expect(collapsed.height).toBeCloseTo(initial.height, 0);
  const label = page.locator('.home-policy');
  await expect(label).toBeVisible();
  const b = await label.boundingBox(); const size = page.viewportSize();
  expect(b.y).toBeGreaterThan(size.height * 0.55);
  await label.click(); await expect(page.locator('#policy-title')).toHaveText('交通大升級');
  await page.locator('#policy-close').click();
  // Returning to the menu restores focus to its visible summary.
  await summary.click(); await buttons.nth(1).click(); await page.locator('#policy-close').click();
  await expect(summary).toBeFocused();
});

test('camera zoom remains stable, follows movement and keeps world scale intact', async ({ page, isMobile }) => {
  await enter(page);
  if (isMobile) await page.locator('#help-close').click();
  const before = await page.evaluate(() => {
    const w=window.__skyisles.world;
    return { dist:w.player.orbit.dist, x:w.player.pos.x, z:w.player.pos.z, cam:w.camera.position.toArray(), scale:w.islands.group.scale.toArray() };
  });
  expect(before.dist).toBe(isMobile ? 22 : 16);
  expect(before.scale).toEqual([1,1,1]);
  await page.waitForTimeout(800);
  expect(await page.evaluate(() => window.__skyisles.world.player.orbit.dist)).toBe(before.dist);
  await page.mouse.move(70, 350); await page.mouse.wheel(0,-160);
  await expect.poll(() => page.evaluate(() => window.__skyisles.world.player.orbit.dist)).toBeLessThan(before.dist);
  await page.waitForTimeout(1000);
  const following = await page.evaluate(() => window.__skyisles.world.camera.position.toArray());
  await page.keyboard.down('ArrowRight');
  await expect.poll(() => page.evaluate(() => window.__skyisles.world.player.move.vx)).toBeGreaterThan(1);
  await page.keyboard.up('ArrowRight');
  await expect.poll(() => page.evaluate((v) => {
    const w=window.__skyisles.world; return w.camera.position.distanceTo({x:v[0],y:v[1],z:v[2]});
  }, following)).toBeGreaterThan(0.1);
});

test('mobile instructions dismiss once; pinch zoom does not open policy', async ({ page, isMobile }) => {
  test.skip(!isMobile, 'touch introduction only');
  await enter(page);
  await expect(page.locator('#touch-help')).toBeVisible();
  await page.locator('#help-close').click();
  await expect(page.locator('#touch-help')).not.toBeVisible();
  await enter(page);
  await expect(page.locator('#touch-help')).not.toBeVisible();
  const distance = await page.evaluate(() => window.__skyisles.world.player.orbit.dist);
  const session = await page.context().newCDPSession(page);
  await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:130,y:370,id:1},{x:260,y:370,id:2}]});
  await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:100,y:370,id:1},{x:290,y:370,id:2}]});
  await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  await expect.poll(() => page.evaluate(() => window.__skyisles.world.player.orbit.dist)).toBeLessThan(distance);
  await expect(page.getByRole('dialog')).not.toBeVisible();
  await session.detach();
});
