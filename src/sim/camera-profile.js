// Camera distances change framing only; world scale and movement stay untouched.
export function cameraProfile(width, height) {
  const portrait = width <= 600 && height > width;
  const compact = height <= 500;
  return portrait
    ? { yaw: 0.12, pitch: 0.67, dist: 22, fov: 58 }
    : { yaw: 0.16, pitch: 0.60, dist: compact ? 18 : 16, fov: 55 };
}
export const CAMERA_ZOOM = { min: 3.5, max: 28 };
