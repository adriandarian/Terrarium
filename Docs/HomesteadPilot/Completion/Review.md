# Homestead continuation review

Completed 2026-09-27 in `/Game/Terrarium/HomesteadPilot/Maps/StartingHome`, Unreal Engine 5.8.2. Three fresh workers owned art, environment and runtime independently; the coordinator performed every Unreal operation sequentially.

Open the [visual review](review.html). All images are native Unreal captures. The [original pilot review](../FinalReview.md) remains historical evidence; this review supersedes its remaining-collection and latest-performance status.

## Delivered

- **17 building and prop families** now have three actual LODs. Fifteen have editable Blender packages and 45 FBX exports; BlueShed and Tower use private native copies with generated lower LODs. Lodge, civic hall, compound, market stall, lantern, sign and the collectible collection retain their authored design and material assignments. See [art admission](../RemainingArt/unreal-verification.json) and [source notes](../RemainingArt/README.md).
- **14 retained environment variants / 1,753 instances** use private assets. Twelve received conservative lower LODs, with exact render-LOD0 geometry preserved; the two small stone meshes remain single LOD. Original materials, collision and transforms survive reopening. See [native environment validation](../RemainingEnvironment/inherited-lod-validation.json).
- **190 water tiles** now use a world-continuous animated teal current material and closed 12-triangle geometry. Their fitted envelopes, top elevations and stepped shoreline are preserved. Placed LOD0 geometry fell from 1,444,672 to 2,280 triangles; this is a geometry count, not an attributed speedup. Successive native river captures show ripple motion. See [water validation](../RemainingEnvironment/unreal-validation.json).
- The approved **eleven pilot families and all 5,841 grass tiles** remain unchanged. There are now 43 pilot mesh families: 40 with three LODs and three intentionally minimal single-LOD meshes. Shared sources and the HomesteadBlender baseline remain unchanged.

## Verified in the editor

The coordinator saved StartingHome, switched maps and reopened it. Mesh assignments, effective materials, visibility, instance counts and transforms persisted; forced LODs remain automatic and review-camera auto-activation is disabled. [Persistence receipt](persistence.json).

The art collision audit found import-policy drift. The coordinator restored all 17 placements to the inherited settings and reran verification and traversal. The importer and verifier now enforce that baseline. Collision complexity remains essentially inherited; no physics optimization is claimed. [Restoration receipt](../RuntimeCompletion/art-collision-restoration.json).

All eight traversal checkpoints passed across cottage entry/exit, stairs up/down and both bridge spans out/back. This used CharacterMovement, gravity and collision, with AddMovementInput and an initial teleport per route. [Traversal receipt](traversal-receipt.json).

The final automatic-LOD camera sweep covered cottage, Lodge, CivicHall and HomesteadCompound: 543 camera samples and 20 PNGs, 535 components in automatic mode, global force-LOD disabled. Inspected samples retain closed roofs and visible structures. Trees partly obscure the compound. This does not certify every intermediate frame or actual rendered LOD indices. [Sweep receipt](../RuntimeCompletion/FinalBuildings/automatic-lod-sweep.json).

A separate fresh default gameplay-view idle profile recorded **1,800 frames over 30 seconds**, after five seconds of warmup: **16.67 ms mean, 16.91 ms p95, 54.98 ms maximum**. One frame exceeded 50 ms. No movement or keyboard input was injected or observed. No imports, sweeps, captures, query benchmark or background Blender exports ran during sampling; the existing live Blender window remained open. The earlier Message Log-obscured sample is excluded. These editor world-frame deltas do not establish shipping or city-scale performance. [Final sample](../RuntimeCompletion/idle-observation.json).

Separate vertical-probe query timing measured 484 traces per mode: **33.48 µs simple / 35.18 µs complex mean**, including Python/engine overhead. This is not total physics-frame cost. [Runtime validation and limits](../RuntimeCompletion/Validation.md).

## Remaining acceptance and later scope

Physical held-key WASD/mouse behavior and continuous LOD transition smoothness remain unverified. Available synchronous key tooling cannot establish a held-key test. Sampled screenshots do not prove invisible transitions. Inspect those interactively before treating runtime acceptance as complete.

Character presentation, simpler structural collision, navigation, a connected neighborhood, district budgets, spatial streaming and distant cities remain separately scoped follow-ups. The homestead continuation does not implement settlement-growth gameplay or a finished open world.

Unreal still reports dense navigation-export collision geometry for Lodge, CivicHall and Compound. Their inherited collision behavior is preserved; that warning is an actual remaining optimization concern.

The editor is left on StartingHome with PIE stopped. Existing checkout changes and three preexisting dirty shared material packages are preserved. No commit or push was made.

Final local checks: 26 continuation Python sources parsed; all 17 local review link/image targets returned HTTP 200; the review was opened and its layout visually inspected. `git diff --check` passed. The HomesteadBlender baseline SHA-256 remains `c536336787fa342e656c196ce05c32690af279d94437e12431002a3fb207c74c`.
