import { test, expect } from '@playwright/test';

test('compact portrait and landscape menu remain usable with first-visit help', async ({ page, isMobile }) => {
  test.skip(!isMobile, 'touch layouts');
  // Two full scene loads plus viewport/scroll assertions on software WebGL.
  test.setTimeout(360_000);
  for (const viewport of [{width:320,height:568},{width:844,height:390}]) {
    await page.setViewportSize(viewport);
    await page.goto('/'); await page.waitForFunction(() => window.__skyisles);
    // This case measures DOM layout only. Full-resolution WebGL capture and FPS
    // are separate; avoid redundant software-GPU frames between DOM assertions.
    await page.evaluate(() => { window.__skyisles.world.renderer.render = () => {}; });
    await page.locator('#title-screen .tap').click({force:true});
    await expect(page.locator('#touch-help')).toBeVisible();
    await page.locator('#policy-menu summary').click();
    await expect(page.locator('#touch-help')).not.toBeVisible();
    for (const button of await page.locator('#policy-list button').all()) {
      await button.scrollIntoViewIfNeeded();
      await expect(button).toBeInViewport();
    }
    const nav = await page.locator('#policy-nav').boundingBox();
    expect(nav.x).toBeGreaterThanOrEqual(0);
    expect(nav.x+nav.width).toBeLessThanOrEqual(viewport.width);
    for (const id of ['#joystick','#jump-btn']) {
      const c = await page.locator(id).boundingBox();
      const overlap = nav.x<c.x+c.width && nav.x+nav.width>c.x && nav.y<c.y+c.height && nav.y+nav.height>c.y;
      expect(overlap).toBe(false);
    }
    await page.locator('#policy-menu summary').click();
    await expect(page.locator('#touch-help')).toBeVisible();
    await page.locator('#help-close').click();
    await expect(page.locator('#touch-help')).not.toBeVisible();
    await page.evaluate(() => {
      sessionStorage.removeItem('yuanli-help-dismissed');
      window.__skyisles.world.renderer.dispose();
      window.__skyisles.world.renderer.forceContextLoss();
    });
  }
});
