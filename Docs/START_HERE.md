# Terrarium — compact continuation handoff

Updated 2026-09-27. Read this first; load linked evidence only when needed for the assigned task. This replaces replaying the long calibration/build conversation.

## User direction

The user likes the current homestead pilot. It is the starting home of an explorable game; later settlements will include large cities, with many cities in the open world. Establish the theme before broad expansion. The four references describe scope and art direction, not a confirmed settlement-growth mechanic.

Use human-scale architecture, mossy stone terraces, rivers, warm plaster/timber, terracotta and selective teal. Combine fine angular geometry with rich textures. Voxel/feature size varies by model and material; keep physical dimensions independent from detail size. Preserve nearby quality through LOD. Final camera and raster treatment are not locked.

Latest request: a drastic overhaul of world building using imagegen. V6 below is the current result; V5 receipts are historical.

## Current world — Valley Region V6 world-building overhaul

The latest user asked for a drastic world-building overhaul with imagegen. The current map remains `/Game/Terrarium/WorldExpansion/Maps/ValleyRegion`. V5 is archived natively as `/Game/Terrarium/WorldExpansion/Maps/ValleyRegionV5Archive`.

- Current review: `Docs/WorldExpansion/V6/review.html` at `http://127.0.0.1:8770/WorldExpansion/V6/review.html` (verified, existing server); change notes and boundaries: `V6/Review.md`; direction: `V6/WorldDirection.md`. Twelve native views include V5/V6 comparisons and three new landmark views. The existing regional review redirects to V6.
- All five settlement layouts were rebuilt: 267 settlement buildings, 277 individual structure/market/well placements, 4,001 detail instances. Added an 18m civic bell tower, raised civic terrace/ramp, gate bastions, a river mill with wheel/landing/stairs, and a ruined aqueduct with an R3 masonry descent. Machinery is static scenery.
- Regional terrain now uses 64 continuous angular meshes, 203,448 triangles, replacing V5's uniform shelves. V5 outer home apron and original homestead are retained. Do not rerun old terrain admission over V6.
- Actual imagegen sources and exact prompts: `SourceAssets/WorldExpansion/V6/`. Limestone Texture2D references in native paving/masonry materials were checked. The concept is not an engine screenshot.
- Regrounded 23,976 existing regional ecology instances, added 1,120 riverbank details, cleared only the private trees recorded in trail-clearance receipts, and corrected 261 peripheral settlement detail heights. Native counts and placement readback pass.
- Thirteen possessed CharacterMovement routes pass, including original regional connections, civic ramp, both mill stair directions, rerouted mill approach and R3 aqueduct descent. The final route receipt consolidates unchanged passing routes with focused repair retests; earlier failures are preserved. Physical held-key input and whole-world navigation remain unverified.
- Save/reopen preserves all 40,587 mesh-instance signatures (including hidden retained geometry), component assignments, camera activation settings, original home signatures, and both original map hashes. Receipts: `V6/validation.json`, `V6/reopened.json`, `V6/traversal-receipt.json`.
- Stationary city sample: 1,200 frames / 20s after 5s warmup; 16.67ms mean, 16.94ms p95, 17.57ms max. OS keyboard activity was observed outside the game; controller keys were empty and the pawn was stationary. Do not label it an input-free idle sample or a shipping budget.
- New terrain/landmark meshes have one visible LOD; spatial streaming, unique district architecture, NPC life, quests/economy and animated machinery remain future work. Scripts live in `Scripts/WorldExpansion/v6/`. Preserve all unrelated dirty/untracked work; no commit or push was requested.

## Historical V5 terrain correction

Live review for this session: `http://127.0.0.1:8770/WorldExpansion/V5/review.html`. The older 8769 server stopped responding. Both before/after controls were verified in the browser; the delivered tab is left on Current V5.

- Working map: `/Game/Terrarium/WorldExpansion/Maps/ValleyRegion`; configured editor startup and game default. The 1.6 × 1.6 km region retains Alderhaven city, Stonegate town and three villages: 235 buildings, 252 structure/market actors and 3,148 settlement detail instances. StartingHome and HomesteadBlender remain preserved originals.
- Current review destination: `Docs/WorldExpansion/V5/review.html` / `Review.md`. The existing `Docs/WorldExpansion/review.html` URL redirects to V5; historical captures/review are retained under `V5/Before/`. All nine final native viewpoints were inspected and accepted for this terrain correction. Gallery buttons compare the previous and current native views. Regular settlement pads and repeated street plans remain visible; acceptance does not imply each district is individually finished. `V5/review-build.json` records the actual gates.
- Effective physical terrain: `SourceAssets/WorldExpansion/TerrainV5/manifest.json`, **130 ground/rock mesh parts, 65 chunks, 1,552,357 triangles**. It replaces the 64 broad terrain tiles and outer HomeApron with physical stepped surfaces. Retired regional components remain hidden and named `NoCollision`; original homestead geometry, roads, settlement pads and protected river/bridge connections are retained. Do not blindly rerun the older terrain admission over V5 bindings.
- Actual imagegen albedos: `SourceAssets/WorldExpansion/ArtDirection/T_VoxelMeadow.png`, `T_MossLimestone.png`, `T_OchreGravel.png`. The three 1254 × 1254 source PNGs match the original generated output bytes. Private TerrainV5 Texture2D/material references are independently checked; native `STRETCH_TO_POWER_OF_TWO` plus texture-group mip generation handles the non-power-of-two source sizes without changing their bytes. Generated texture sources are not scene screenshots.
- V5 ecology: **17,776 admitted groundcover/detail instances**, **3,266 additional grove trees**, and **2,934 existing regional tree/undergrowth instances regrounded** on actual native terrain. Source/admission receipts are `ecology-v5-layout.json`, `ecology-v5-integration.json`, `forest-groves-v5-integration.json`, and `TerrainV5/forest-reground.json` in `Docs/WorldExpansion`. New and existing forest use private FoliageTypes; approved home foliage remains protected.
- Validation: `Docs/WorldExpansion/V5/validation.json` and `surface-validation.json` pass, including 17 real ground probes, new/retired material/collision bindings, generated-source hashes, native texture references and foliage counts. **Eight CharacterMovement routes pass**, including home-to-hub and full city bridge with both bank transitions. Twelve existing forest roots/trunks and twelve new grove roots/trunks pass in PIE. Forest reports preserve full-world X/Y occlusion rays separately from terrain-ignored trunk-body identification; a terrain ledge is not silently treated as a missing tree body.
- Persistence: `V5/reopened.json` verifies **38,228 mesh instances**, effective materials, visibility/collision modes, camera settings, all original pilot signatures and unchanged original map bytes after reload. `V5/before.json` is the pre-correction regional snapshot. `Docs/WorldExpansion/original-baseline.json` remains immutable; the V5 copy is SHA-256 checked. Named `NoCollision` water/retired profiles are required; raw collision-enabled overrides previously failed to persist.
- Reproduction helpers: `Scripts/WorldExpansion/validation_v5/`; `V5/QA.md` gives the exact sequence. `prepare_contract.py` refreshes current private foliage component paths from native replacement receipts, while requiring their existing counts/transforms to stay preserved.
- V5 passive city sample: **16.67 ms mean, 16.88 ms p95, 17.53 ms max**, 1,200 frames over 20 seconds after five seconds warmup, with no injected input or concurrent captures/diagnostic queries (`V5/city-observation.json`). This is editor world-frame timing at one city viewpoint, not a shipping or populated-world budget. Earlier WorldExpansion samples predate this correction. Never use traversal timing as a clean profile when diagnostic forest queries run during it.
- Limits: V5 terrain currently has **one visible LOD per mesh**; no automatic terrain LOD transitions or spatial streaming are implemented. Runtime budget and native visual acceptance must use this revision. Whole-region navigation, NPC life, quests/economy, unique village layout refinement and physical held-key input acceptance remain separate work. One detailed garden well retains a single 6,132-triangle LOD.
- Three workers supplied source geometry, ecology and validation; the coordinator integrated through the verified Terrarium editor sequentially. Preserve prior dirty/untracked work. No commit/push was requested. Generated Binaries/Intermediate/Saved/DerivedDataCache remain ignored.

## Preserved homestead deliverable

- Project: `C:/Users/hello/Projects/Terrarium`, UE 5.8.2, `Terrarium.uproject`.
- Working map: `/Game/Terrarium/HomesteadPilot/Maps/StartingHome`.
- Baseline: `/Game/Terrarium/Blender/Maps/HomesteadBlender`; preserved unchanged.
- Latest review: `Docs/HomesteadPilot/Completion/review.html`; local URL `http://127.0.0.1:8769/HomesteadPilot/Completion/review.html`. Server availability must be checked in a new session. The original review remains historical.
- Original eleven approved families remain unchanged. Added 17 building/prop families with three actual LODs, 14 retained environment variants (12 three-LOD, two minimal stones), and animated water on 190 fitted tiles. Total 43 pilot mesh families: 40 three-LOD and three minimal single-LOD. Existing character figures remain inherited.
- Enterable cottage; walking explorer with WASD/mouse, real collision and a map-specific GameMode. Spawn `[650,-150,672]` cm; camera follows the explorer. Review cameras must have player auto-activation disabled.
- Preserve all current checkout changes. Pilot/calibration/source directories are untracked and input/plan files modified; no commit or push was requested.

## Effective sources and evidence

Architecture: `Docs/HomesteadPilot/Architecture/manifest.json`. Override cottage LOD1/2 with `Architecture/RoofRepairV2/manifest.json`; original LOD0 and authored fence/bridge chains remain. The repair closes roof gaps. Editable sources: `SourceAssets/Blender/HomesteadPilot/Architecture/`.

Landscape: `SourceAssets/Blender/HomesteadPilot/Landscape/manifest.json`, overridden for tree/stairs by adjacent `revised-manifest.json` (`BroadTree5mV2`, `StoneStairs2mRiseV2`). Source files use metres, Z-up and stable material slots; Unreal imports use centimetres.

Continuation evidence: [completion review](HomesteadPilot/Completion/Review.md), [runtime validation](HomesteadPilot/RuntimeCompletion/Validation.md), [persistence](HomesteadPilot/Completion/persistence.json). All assignments, effective materials, visibility, instance counts and transforms survived another map switch/reopen. Cottage entry/exit, stairs up/down and both bridge spans passed eight CharacterMovement checkpoints after collision restoration. Fresh default Play was profiled without movement injection. Physical held-key input and continuous automatic LOD transition smoothness remain unverified; the four-building sweep supplies 543 camera samples and 20 PNGs, not a complete motion acceptance pass.

Remaining art: `SourceAssets/Blender/HomesteadPilot/RemainingArt/`; source/native manifests and verification in `Docs/HomesteadPilot/RemainingArt/`. Fifteen editable Blender packages and 45 authored FBXs, plus native BlueShed/Tower copies. Native degenerate-filter exceptions are hash-bound and backed by A/B imports. Material slots and per-face assignments were repaired from exact matching editable source geometry.

Environment: `Docs/HomesteadPilot/RemainingEnvironment/README.md` and `inherited-lod-validation.json`. Exact retained render-LOD0 hashes, material/collision contracts and transforms verified for 1,753 instances. Private FoliageTypes persist; shared sources are unchanged. Water has 2,280 placed triangles versus 1,444,672 inherited LOD0 triangles, with animated world-space currents; this is not an attributed performance speedup.

Collision: `RuntimeCompletion/art-collision-restoration.json` is authoritative. The initial art import changed several collision policies; all 17 placements now match inherited settings, the importer is baseline-aware, and native verification passed. Complexity is still inherited. Unreal still warns about dense navigation-export geometry on Lodge, CivicHall and Compound; simpler structural collision remains future work.

Grass: all **5,841** retained tiles survive reopening with visibility and transform checks. A faulty LOD0 export omitted grass; replaced with a verified native capture. Exact renderer timing cause remains unisolated. Inspect final images themselves, not only object counts.

Latest gameplay-view PIE sample: **16.67 ms mean, 16.91 ms p95, 54.98 ms max**, 1,800 frames over 30 seconds after 5 seconds warmup. No imports, captures, sweeps, query benchmark or background Blender export during measurement; live Blender GUI remained open. Editor world-frame deltas, not a shipping or city-scale budget. One frame exceeded 50 ms. `RuntimeCompletion/idle-observation.json` supersedes earlier samples; `idle-message-log-visible.json` is excluded. Separate query timing: 33.48 µs simple / 35.18 µs complex mean including Python/engine overhead, not total physics cost.

## Efficient next-agent workflow

Use one coordinator plus up to three fresh workers, each given this handoff and a narrow assignment. Avoid full-history forks. Workers return changed files, validation evidence and unresolved issues in short reports; coordinator consolidates once.

| Owner | Independent scope | Boundary |
| --- | --- | --- |
| Art worker | Remaining buildings and small props | Own source/export/script folder; preserve approved pilot |
| Environment worker | Remaining terrain, planting and water treatment | Separate source/export/script folder |
| Runtime worker | LOD transitions, collision costs, input checks and profiling | Runtime scripts/receipts; queue editor operations |
| Coordinator | Asset admission, scene integration, visual acceptance and handoff | Sole Unreal editor operator |

Next acceptance: actual held WASD/mouse input and continuous automatic-LOD approach/retreat review. Character presentation needs a separately scoped follow-up. Simpler structural collision, navigation, a connected neighborhood, district profiling, spatial streaming and distant cities are later requirements, not implemented features.

Follow `AGENTS.md`. Discover Unreal MCP tools, verify Terrarium, and call editor tools sequentially. Use the editor for binary assets. Serialize live Blender access; follow `Docs/BlenderMCP.md` and verify the project marker. Duplicate shared FoliageTypes for pilot changes: component mesh overrides alone reverted on reload. Restore forced LOD to zero before saving. `Runtime/configure-only.json` currently filters mesh rebuilds to the cottage; inspect it before a new rebuild.

Keep subsequent updates here concise. Do not load historical logs, every receipt, or all source manifests into the coordinator unless needed.


