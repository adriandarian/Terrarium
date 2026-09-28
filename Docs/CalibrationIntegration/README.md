# Scale and detail review — first milestone

Two parallel subagents produced separate scale and construction-density studies. The parent integrated and inspected both in Unreal Engine 5.8.2. These are review candidates, not final replacements or accepted concept fidelity.

Open `review.html` for the concept overlay and same-camera family comparisons. The local preview is http://127.0.0.1:8769/CalibrationIntegration/review.html while this session's documentation server is running. The HTML also works directly from disk.

## Scale study

Level: `/Game/Terrarium/Calibration/Maps/ConceptScaleBlockout`.

Manual measurements, uncertainty and construction conventions are in `../ScaleCalibration/targets.json` and `../ScaleCalibration/README.md`. The first editor capture revealed stair occlusion and undersized projected cottage/person widths. One focused correction opened the terrace stair corridor and adjusted only the two horizontal silhouettes. The original camera, ground anchors and 180 cm person convention remain fixed. Corrected projected widths are 117 px for the cottage and 18 px for the person. A projected bridge-width difference of about 8.8% remains disclosed; this is not blanket visual approval.

## Detail study

Level: `/Game/Terrarium/Calibration/Maps/DetailDensityReview`.

Five specimen families each have coarse, half-size and third-size construction controls, plus one scale person: 16 imported meshes. The controls preserve each family's outside dimensions. Roof sections compare 6, 12 and 18 actual rises. These change geometry and construction counts; they are not subdivisions of unchanged large blocks. The tree envelope is provisional and broader than the existing skinny source. The cottage specimen is a section, not a full replacement cottage.

Editable source: `../../SourceAssets/Blender/DetailCalibration/DetailCalibration.blend`. Detailed source checks and preview gallery are in `../DetailCalibration/`.

## Actual validation

- Original HomesteadBlender map SHA-256 is unchanged.
- Both new levels were saved and reopened. Patched scale actors, materials, the fixed camera, eight stair actors and 180 cm person height were verified after reload.
- All 16 Unreal mesh dimensions match Blender metre dimensions converted to centimetres within 0.1 cm. All imported material slots were explicitly assigned and verified after map reload.
- The saved Blender source independently reopened; all 16 exports passed a Blender FBX roundtrip dimension check.
- Native Unreal blockout, corrected stairs and detail overview were visually inspected. Same-camera Blender specimen previews are provided separately.
- The review page loaded and its overlay and family-switch controls were checked through keyboard activation. Click automation in the embedded browser did not activate the buttons reliably; no browser script error was reported.
- No gameplay, animation, navigation or performance-budget validation was performed. Coarse controls are source-informed approximations, not exact copies of the current assets.

Evidence: `final-verification.json`, `detail-import.json`, `../ScaleCalibration/stair-notch-receipt.json`, `../DetailCalibration/verification.json`, and `../DetailCalibration/reopen-verification.json`.

## Next checkpoint

The user's four settlement references clarify that the homestead establishes the theme for an explorable open world containing many cities. The review page now includes all four images and the revised direction in `../SceneAssembly/ScaleAndDetailPlan.md`.

Next, finish a cohesive homestead asset group with model-specific fine geometry, richer textures and raster presentation, playable dimensions, and an actual distance-detail pilot. The three specimen options are exploratory controls, not final LOD meshes, fixed choices or a detail ceiling. Validate close, exploration and distant views before rolling the recipe across the collection. Settlement-growth gameplay is not implied by the concept progression.

This clarification updates documentation and the review page only. No new Unreal or Blender edits, LOD implementation or gameplay/performance tests were performed during this update.

No canonical models or the original homestead map were overwritten. No commit or PR was created.
