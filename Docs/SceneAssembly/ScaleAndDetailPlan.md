# Terrarium: homestead art direction and open-world foundation

Updated 2026-09-27 from the user's four settlement references and review comments. This replaces the earlier single-frame calibration framing. World intent is confirmed by the user; implementation choices and visual results still require validation.

## Intended game and current milestone

The homestead is the starting home in an explorable video game. The references progress from homestead to village, town and a large city. That city is only one settlement among many in the eventual open world. These images establish increasing scope and a shared theme; they do not by themselves specify a runtime settlement-growth mechanic.

The immediate work is to establish the theme through a complete, explorable homestead. Later work expands that foundation into larger settlements and the world between them. Do not build the entire city now or treat the homestead as a self-contained miniature diorama. Preserve useful scale studies, but a fixed concept crop is one art comparison, not the final gameplay camera or the definition of world scale.

## Visual direction from all four references

- Terraced, moss-covered stone terrain; rivers, waterfalls, crossings and paths organize settlements.
- Warm plaster and timber walls, terracotta roofs, weathered masonry and selective teal roofs or accents.
- Rich variation within restrained earthy colors: worn edges, joints, moss, roof tiles, foliage clusters and ground cover.
- Angular, stepped forms with finer local detail. Chunk size varies with the object, material and intended shape.
- Human-scale homes and paths remain recognizable as settlement complexity grows. Larger towns add streets, plazas, retaining walls, bridges, civic buildings and landmarks.
- Architecture follows elevation and water. Expansion adds connected places and neighborhoods rather than uniformly enlarging the starter house or repeating it everywhere.

Reference copies are in `../CalibrationIntegration/References/`. Originals were supplied from the Pokemon project's `output/imagegen` folder; these are art references for Terrarium, not a change of project.

## Separate the controls

1. **Playable dimensions:** choose consistent character, doorway, floor, stair, path, bridge and building dimensions. Calibrate through movement and traversal alongside the image comparison. Concept images cannot determine exact real-world sizes; the existing 180 cm marker is a working convention.
2. **Geometric feature size:** use smaller voxels or construction features where shape requires them. A cliff mass, leaf cluster, roof edge and window detail can use different scales, including within one model. Existing half/third examples are experiments, not mandatory presets, final LODs or an upper limit on detail.
3. **Surface detail:** combine geometric form with authored or baked texture detail, palette variation, material response and wear. More roof rows alone will not reproduce the reference. Texture sampling and raster presentation must preserve the desired fine detail instead of imposing oversized screen pixels.
4. **Distance representation:** create detailed nearby assets and appropriate simpler representations for greater distances. LOD is part of the next asset pilot, not a reason to cap close-up quality. Check silhouette, material stability, thin features and transitions during camera movement; distance reduction does not by itself prove the artwork or texture sampling is correct.

“Smaller voxels and rasterizing” is recorded as a desired detailed, raster-rendered visual result. The images alone do not settle texture filtering, output pixel size, final camera projection or a specific voxel authoring method. Compare those in-engine before freezing the rendering recipe; do not silently turn the world into prerendered sprites or impose a global pixelation effect.

## Next implementation milestone: a finished homestead art pilot

1. **Establish traversal scale.** Retain the blockout for comparison, correct remaining obvious mismatches, and test a character moving through the home surroundings, paths, stairs and bridge. Choose representative close, normal exploration and distant views. Keep the original concept camera as an additional reference view.
2. **Finish one cohesive group.** Build a complete cottage beside a cliff/grass section, tree, fence, path and bridge section. Preserve overall dimensions while improving actual silhouettes, small features and surfaces. Use model-specific feature sizes; the target is reference character and nearby quality, not a common voxel dimension. Compare shape, material and lighting together once individual controls are understood.
3. **Prototype textures and raster presentation.** Compare detail carried in geometry against detail baked or painted into textures. Inspect roof irregularity, wall surfaces, wood, masonry, moss and foliage. Verify texture detail remains coherent at exploration distance and in motion. Record the chosen texture density and sampling rules with the geometry recipe.
4. **Implement and inspect distance detail.** Add an initial LOD chain to representative assets, with thresholds chosen from observed screen size. Preserve the forms and colors that identify each asset. Test transitions, texture stability and shadows while approaching and retreating. Record actual frame-time, memory and asset-cost measurements on the test setup before setting wider budgets. Select the exact Unreal mechanism through this pilot rather than asserting it is already implemented.
5. **Complete the starting home.** Apply the proven recipe across the required homestead models, terrain, vegetation and props. All 31 existing model families remain candidates for the collection; model presence alone is not completion. Place assets according to their role in the world and retain a separate collection review where useful.
6. **Validate and document.** Inspect the complete homestead from multiple exploration angles and the concept view; test traversal, ground contact, dimensions and distance transitions. Save and reopen editable sources and Unreal assets. Record visual gaps separately from import correctness and performance results.

## Foundation for later settlement and world expansion

Use reusable architectural parts, terrain connections, roads, bridges and material families, while preserving distinct buildings and landmarks. Keep physical dimensions independent from voxel detail and camera distance. Retain editable high-detail sources and derive runtime representations from them; omit hidden internal faces where possible.

After the homestead establishes the art recipe, build a small connected neighborhood to test repetition, elevation, street widths and accumulated rendering cost. Then expand to districts and a full city. The eventual multi-city world will need spatial streaming, distant settlement representations, collision and navigation planning, and budgets measured at district scale. These are future implementation requirements, not features delivered by the calibration maps.

## Current evidence and acceptance

The separate scale blockout and 16-mesh detail study have been imported, saved and reopened. Their technical receipts remain valid; their flat-color specimen renders are not accepted final art. The bridge retains a documented projected-width difference of about 8.8% from the manually annotated homestead reference.

The next result succeeds when the starting home has the reference's material richness and stepped visual character at explorable scale, looks coherent across several views, and demonstrates working distance detail on the pilot assets. No LOD, gameplay, navigation or performance validation is claimed by the earlier calibration work. The original homestead map remains the baseline for comparison.

## Homestead pilot implementation

The subsequent build-out lives in `/Game/Terrarium/HomesteadPilot/Maps/StartingHome`, with editable sources under `SourceAssets/Blender/HomesteadPilot`. Its [visual review](../HomesteadPilot/review.html) and [runtime validation](../HomesteadPilot/Runtime/Validation.md) supersede the calibration specimens as evidence of this implementation pass.

Three parallel workstreams delivered a complete enterable cottage, modular fence and bridge; eight finer landscape families; and a walking explorer with actual three-level LOD chains on all eleven new mesh families. The original world layout and remaining collection assets are retained. This is a representative pilot, not a claim that all 31 original families have been rebuilt or that the theme has received final user approval.

Possessed-character movement passed cottage entry/exit, terrace stairs in both directions and the two-span river crossing out and back with gravity and collision. A local twenty-second PIE sample measured 23.58 ms mean, 52.40 ms p95 and a 117.17 ms maximum; this is editor evidence, not a shipping-game or multi-city performance budget. Physical held-key input and automatic LOD transition smoothness in motion remain separate acceptance checks.

Next, extend the proven asset recipe across the remaining homestead props and character presentation, then build a connected neighborhood. District-scale profiling, simplified structural collision, navigation, spatial streaming and distant settlement representations still need implementation and validation before broad city expansion.
