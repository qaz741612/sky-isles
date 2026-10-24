import { test } from 'node:test';
import assert from 'node:assert/strict';
import { cameraProfile, CAMERA_ZOOM } from '../src/sim/camera-profile.js';
test('portrait camera has its own framing within controller zoom limits', () => {
  const desktop = cameraProfile(1440, 900), phone = cameraProfile(430, 739);
  assert.ok(phone.dist > desktop.dist);
  assert.notEqual(phone.fov, desktop.fov);
  for (const size of [[1440,900],[430,739],[320,568],[844,390]]) {
    const p = cameraProfile(...size);
    assert.ok(p.dist >= CAMERA_ZOOM.min && p.dist <= CAMERA_ZOOM.max);
    assert.ok(p.pitch > 0.05 && p.pitch < 1.25);
  }
});
