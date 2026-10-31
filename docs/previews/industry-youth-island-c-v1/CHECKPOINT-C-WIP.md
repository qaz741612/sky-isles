# Checkpoint C — final validation in progress

Saved C-only porch camera fallback (orbit state unchanged), exact deck/wall/roof proxies, NPC 3x3/1.4-unit player stop, and collision coordinates quantized to the same 1e-5 precision as the surface generator. Visible GLB geometry unchanged by proxy quantization. Protected models, all centres/Bezier controls, lamp anchors and 19 non-C route cores verified unchanged/non-overlapping.

The inherited continuous rendering test run timed out under SwiftShader. Optional SKY_SOFTWARE_QA=1 now submits first/explicit real frames while preserving native rAF, controls, physics, UI and camera. No hardware/FPS/thermal claim. Visual samples are separately captured real Three.js frames.

Broad engineering regression: 41 passed, 3 intentionally skipped, 2 initial failures (C edge probe used radial rather than segment-normal push near route openings; panorama position exact equality differed by ~1e-16). Guard probe corrected to perpendicular motion, panorama position tolerance quantified at 1e-10, with exact orbit/progress checks retained. Final targeted reruns and final-proxy route/capture regeneration are still in progress at this checkpoint. Do not interpret WIP as complete acceptance.
