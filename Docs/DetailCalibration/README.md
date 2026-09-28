# Detail calibration review

This is the first bounded construction study, not a replacement asset collection or an approved visual specification. Open `review.html` for the same-camera comparison and roof close-up. Open `SourceAssets/Blender/DetailCalibration/DetailCalibration.blend` for editable category meshes and all sixteen specimens.

The left column is a **source-informed coarse control**, not a copy of the current imported asset. The middle and right columns test half-size and roughly third-size construction features. Structural members that should remain readable are not universally reduced. Existing canonical Blender files, FBXs, Unreal maps, and the live Blender scene were preserved.

| Family | Fixed outer dimensions, metres | Actual construction change |
| --- | --- | --- |
| Cliff corner and grass cap | 3.0 × 1.5 × 2.4 | 5 / 10 / 15 stone rows, staggered joints, clipped stone corners, finer grass lip breaks |
| Cottage roof and wall **section** | 2.4 × 1.65 × 3.4 | 6 / 12 / 18 actual roof rises; staggered tile joints; finer foundation courses; posts and window stay readable |
| Tree | 3.3 × 2.2 × 3.5 | Coarse crown scaffold from the existing tree recipe; finer clustered crowns have different exposed silhouettes and omitted internal voxel faces |
| Fence span | 2.8 × 0.22 × 1.24 | Smaller post/rail cross-sections and exposed joinery; three posts remain structural |
| Bridge section | 1.42 × 2.1 × 1.29 | 7 / 14 / 21 actual deck planks and smaller spacing/fasteners; supporting beams and rail heights remain fixed |
| Shared scale person | 0.75 × 0.31 × 1.8 | Identical scale figure in every family preview |

All dimensions are provisional until the separate scale blockout is reviewed. The broader tree envelope was chosen from the main concept: a 3.3 × 2.2 m rectangle projects to about 70.7 pixels at yaw 135 degrees and 5.5 cm per pixel. The actual irregular crown does not fill that whole rectangle. This is an explicit construction choice, not a measured real-world tree. The cottage object is a section and must not be interpreted as the full house size.

Flat palette materials deliberately isolate geometry. The colors derive from the existing recipe palettes. No new texture noise or downloaded/generated art has been introduced. Tree leaf cell size begins at the existing recipe's 0.235 m, then uses half/third construction steps; fitting the shared crown envelope rescales the local axes. These labels describe relative construction density, not one universal final world-space cube size.

## Validation and review

`manifest.json` records all sixteen FBX paths, part/triangle counts, source bounds, layout positions and the sixteen stable material slots with linear RGBA colors. The whole study is 60,028 triangles. `verification.json` records measured source bounds and independent FBX import bounds. Every variant in a family must have matching outside dimensions within 0.01 mm in source and 0.1 mm in the FBX round trip. `reopen-verification.json` records independently reopening the normal Blender source.

The first visual pass confirmed that finer roof variants change the stair-step silhouette instead of subdividing the old six courses. It also caught a trunk made too thick by the broader tree envelope; the final revision narrows the trunk while keeping crown dimensions fixed. The study received one initial build and two bounded revisions: a concept-based tree envelope adjustment and its trunk correction. No collection-wide rebuilding or open-ended polishing was performed.

The studio images use one orthographic camera direction, the same framing and 1.8 m person in all fifteen family views. The roof close-ups also share one direction and crop size. These images establish the construction comparison; they do not prove a match to the full concept camera or establish an approved detail density. Finer cliff courses become visibly busier; that is an option to evaluate in the wider scene, not an automatic quality improvement.

## Unreal import contract

- Target only `/Game/Terrarium/Calibration` or another explicitly isolated review folder.
- Import each `SM_DC_*.fbx` at scale **1**, with scene-unit conversion enabled. FBX files declare metres; a 1.8 m person must become **180 cm** high.
- Preserve the sixteen stable material slots. Create flat materials from the manifest's linear RGBA values and roughness 0.88; no automatic texture conversion is needed.
- Use each specimen's `placement_m × 100` for the optional compact comparison grid. Source pivots are centered in X/Y at the ground base Z=0. Grid placement is not concept-scene placement.
- Imported mesh dimensions must equal `dimensions_m × 100`. The tree must be 330 × 220 × 350 cm and all three variants must match.
- UVs are intentionally absent because this is a flat-material silhouette study. No collision or gameplay suitability is claimed by the Blender verification. Unreal material binding, centimetre bounds, saved-map reopening and any collision checks belong to the separate integration report.

## Reproduction

In the verified Terrarium Blender Lab session, execute `Scripts/DetailCalibration/build_calibration.py`. It refuses to overwrite an existing calibration scene, creates new scene/datablocks only, writes an isolated scene library plus sixteen exports, and restores the previously active scene. The background `Scripts/DetailCalibration/package_review.py` then appends only that calibration library into a fresh Blender process, creates the same-camera images, saves a normal editable project, and round-trips all sixteen FBXs. It does not open or modify the user's live Blender file.
