# Runtime validation — 2026-09-27

The root agent ran these checks through the verified Terrarium Unreal editor. The source scripts and source-model manifests were not used as substitutes for runtime evidence.

## Playable traversal

`traversal-receipt.json` records successful movement of the possessed BP_HomesteadExplorer through all three final routes:

- Cottage: enter through the open doorway, walk into the interior and exit again; three checkpoints.
- Terrace stairs: walk up and back down the new stair flight; two destination checkpoints.
- River bridge: cross both spans and return to the start; three checkpoints.

Each checkpoint required the expected elevation and CharacterMovement walking mode. Gravity and static collision remained active. The harness teleported only to each route's initial setup position, then used AddMovementInput for the route. It slowed the live character near checkpoints to prevent numerical overshoot and restored the original speed afterward. Background CPU throttling was temporarily disabled and restored. A short landing grace period allowed gravity to settle descending steps.

The first low-frequency trial incorrectly reported the cottage exit as blocked: its positions alternated across the narrow target circle. Inspecting the trace identified overshoot, not a collision defect. The corrected test passed without weakening collision or changing geometry. An earlier stair checkpoint had also been placed partway up the flight with the bottom-floor elevation; that incorrect checkpoint was removed before testing the actual destinations.

Six persistent HP_ axis entries in DefaultInput.ini implement WASD and mouse look, with a map-only game mode override. Physical held-key input has not been verified through the available Slate tool: PressKey sends a synchronous down/up pair. The gameplay movement and collision tests above are verified independently of that tool limitation.

## Implemented LOD geometry

`mesh-runtime-receipt.json` reads these triangle counts from Unreal's actual static meshes. All have three LODs, explicit screen thresholds, assigned materials and Nanite disabled for the conventional LOD pilot.

| Mesh | LOD0 | LOD1 | LOD2 |
| --- | ---: | ---: | ---: |
| Cottage | 43,496 | 12,516 | 6,876 |
| Fence | 376 | 216 | 120 |
| Bridge | 2,188 | 780 | 420 |
| Moss cliff | 23,276 | 12,802 | 5,818 |
| Fine cliff column | 4,080 | 2,244 | 1,020 |
| Broad tree | 11,584 | 8,688 | 5,792 |
| Shrub ground cover | 3,284 | 1,806 | 820 |
| Worn path | 616 | 338 | 154 |
| Stone stairs | 4,532 | 2,492 | 1,132 |
| Wheat patch | 32,444 | 17,844 | 8,110 |
| Garden patch | 7,700 | 4,234 | 1,924 |

Architecture uses authored FBX chains. Landscape uses Unreal mesh reduction. Most thresholds are 1.0 / 0.30 / 0.10 screen fraction; fence and tree use 1.0 / 0.18 / 0.06 to retain thin silhouettes longer. These technical checks do not certify every transition's appearance; fixed-camera LOD captures and approach/retreat review are separate visual evidence.

## Measured local performance

`performance-receipt.json` contains 848 actual PIE frame-delta samples from the verified explorer eye view over twenty seconds after five seconds of warmup. The viewport was 1,526 x 910. Mean frame delta was 23.58 ms, median 16.75 ms, p95 52.40 ms and maximum 117.17 ms. The slow tail and maximum show substantial frame-time variation; this result is not a stable 60 fps claim. The earlier concept-camera sample is retained separately as `performance-concept-view.json`.

The editor's working set ended at 4,086,931,456 bytes (3.81 GiB); private committed memory ended at 14,551,134,208 bytes (13.55 GiB). These figures cover the whole editor process with PIE and loaded assets, not just this level or a packaged game. They are not GPU memory measurements. A Blender roof-render worker was active concurrently; its contribution to frame-time variation has not been isolated.

The running editor log identifies Unreal 5.8.2, Windows 11, AMD Ryzen 9 5950X, Radeon RX 6950 XT, D3D12/SM6, and AMD driver 26.8.1. Background CPU throttling was disabled only for the measurement and restored afterward. The reported frame data includes editor overhead and does not split game-thread, render-thread and GPU time. This single-view homestead sample establishes local evidence, not a district or multi-city budget.

## Persistence and remaining acceptance

Reopening exposed a real foliage persistence defect: direct component mesh overrides reverted to the shared FoliageType meshes. Converted instance transforms had survived. `persist_pilot_foliage.py` therefore duplicated the used FoliageTypes into the pilot and migrated their authoritative instances while copying the current transforms without further scale conversion.

`foliage-migration-receipt.json` verifies another save/reopen with all 2,748 intended instances: 2,076 cliff columns, 618 shrubs, 14 foliage trees and 40 wheat patches. Translation error was exactly zero; maximum scale error was below 0.00000006, consistent with float storage. Source foliage assets retained their original mesh assignments and identical file hashes. Pilot cliffs/trees use BlockAll; shrubs/wheat use NoCollision through the saved FoliageType body settings.

The inherited Baseline_Orthographic_Review camera was also configured to auto-activate for Player0, overriding the possessed pawn view. `fix_play_view.py` disabled that activation on StartingHome only. A fresh PIE inspection now confirms that the controller's view target is the explorer; traversal/performance scripts enforce this. The original PlayerStart was obstructed at the reference-player mesh location; native GameMode rejected it and fell back to the world origin. Moving the saved start to [650, -150, 672] fixed default spawning without a runtime teleport. `fresh-spawn-verification.json` observed three seconds of a new default PIE session: the pawn settled at [650, -150, 657.15], remained grounded, and its actual eye camera remained at [650, -150, 732.15]. No movement or position changes were injected by that verifier.

`saved-runtime-verification.json` records the reopened map's correct game mode, explorer class/capsule, persistent input mappings, all LOD chains/materials/collision flags and automatic LOD settings. Visual approval, automatic LOD transitions in motion, and physical keyboard control must not be inferred from triangle counts or source manifests.
