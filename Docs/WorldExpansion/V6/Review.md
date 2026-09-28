# Valley Region V6 — world-building overhaul

Working map: `/Game/Terrarium/WorldExpansion/Maps/ValleyRegion`.

Open `review.html` for twelve native Unreal viewpoints, including nine V5/V6 comparisons and three new landmark views. The previous world is retained as `/Game/Terrarium/WorldExpansion/Maps/ValleyRegionV5Archive`. No commit or push was requested or performed.

## Changes

- Replaced all five repeated settlement grids with distinct plans: Alderhaven's crooked market lanes and civic precinct, Stonegate's bent gate street and irregular enclosure, Brookmere's orchard green, Reedbank's trading lanes, and Highfield's village crescent and bounded fields.
- Authored **267 settlement buildings**, with **277 individual building/market/well placements** and **4,001 instanced settlement details**. The mill and its small store are additional landmark placements.
- Added a physical civic terrace and solid ramp, an **18m bell tower**, real gate bastions, a river mill precinct with modeled wheel and timber landing/stairs, and an open-arched ruined aqueduct with a supported masonry approach. The wheel and bell are static scenery.
- Replaced the 64 coarse V5 regional terrain chunks with **64 continuous angular meshes totaling 203,448 triangles**. The protected V5 outer home apron, original homestead, river, bridges and regional road surfaces remain. The uniform five-metre staircase pattern is removed. This is a different geometry treatment, not a claimed performance improvement.
- Added **1,120 native bank-rock and planting instances**. Regrounded **23,976 regional ecology instances** to the new terrain. Trail clearance removed a small number of private regional trees; the exact before/after counts and removed coordinates are retained in the two `trail-clearance` receipts. Original home foliage was not targeted.
- Grounded **261 peripheral garden/field/boundary instances** against actual terrain. Settlement detail counts, XY, scale and rotation remain unchanged.
- Imported the actual imagegen limestone albedo into native lane and masonry materials, and adjusted the regional terrain palette and distant haze. Concept art is labelled separately from engine captures.

## Verification

`validation.json` passes native placement, retired visibility/collision, 64 terrain bindings, new foliage counts, important ground probes, generated-source hash and actual material-to-Texture2D reference checks.

**Thirteen CharacterMovement routes pass.** These use a possessed PIE character, real gravity and collision, and movement input; they do not establish physical held-key acceptance. The first eleven routes passed together. The new mill track initially crossed a cottage and was rerouted. The aqueduct approach initially hit an unwalkable slope and was replaced with masonry steps. Successful focused retests supply the final two route results. `traversal-receipt.json` consolidates those results and lists the preserved source receipts; failed earlier runs are not discarded. A later tread refinement was retested successfully in `aqueduct-retest.json`.

After switching to StartingHome and reopening ValleyRegion, `reopened.json` verifies **40,587 saved mesh-instance signatures**, component assignments and camera activation settings. This count includes retained hidden legacy geometry. Original home signatures are a preserved multiset, and the StartingHome and HomesteadBlender map file hashes are unchanged.

The stationary city observation recorded **1,200 frames over 20 seconds after 5 seconds warmup**, with **16.67ms mean, 16.94ms p95, 17.57ms max** world-frame deltas. No movement or capture was injected during the window and the pawn remained stationary. The observer detected OS keyboard activity outside the game while controller keys remained empty, so this is not labelled an input-free idle sample. These are editor world-frame deltas, not CPU/GPU attribution or a shipping performance budget.

The final twelve native captures were visually inspected. `review-build.json` gates gallery publication on successful validation, final route results, persistence, and capture presence.

## Current limits

The region still reuses a small architecture family and broad settlement bases. New terrain and landmark meshes have one visible LOD; spatial streaming and automated terrain LOD transitions are not implemented. Full-world navigation, NPC life, quests, economy, water-driven machinery and physical held-key control are outside this pass. The concept remains more architecturally varied and densely composed than the implemented world.

## Sources

- `SourceAssets/WorldExpansion/V6/ValleyDirection.png` — generated concept reference.
- `SourceAssets/WorldExpansion/V6/T_LimestonePaving.png` — generated albedo used in native materials.
- `SourceAssets/WorldExpansion/V6/ImagegenPrompts.md` — exact prompts; built-in image_gen mode.
- `SourceAssets/WorldExpansion/V6/` — editable JSON geometry sources and terrain manifest.
- `Scripts/WorldExpansion/v6/` — source generation, editor admission, corrections, capture and validation helpers.
- `WorldDirection.md` — the visual roles of each place and the intended connections between them.

Editor operations must remain sequential through the bundled MCP after verifying Terrarium. Do not run older V5 admission over these bindings. For reproduction, admit the base layout, palette and terrain, reground regional ecology, admit landmarks, apply refinements and final materials, then create the R3 aqueduct steps, clear their trail corridor and ground the peripheral details. Validate the actual final state; historical receipts are not a substitute for a fresh run.
