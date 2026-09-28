# Valley Region review

Working map: `/Game/Terrarium/WorldExpansion/Maps/ValleyRegion`.

Alderhaven is the regional city, Stonegate the upland town; Brookmere, Reedbank and Highfield form three village destinations. The original home remains the starting point. The expansion reuses approved building families and adds connected terrain, road surfaces, water and mountain slopes.

The authored settlement manifest contains **235 buildings**, 252 individual placements and 3148 detail instances. These authored counts are separate from the scene readback below.

Private forest groups contain **2,200 trees and 734 undergrowth instances**. The effective terrain source is `SourceAssets/WorldExpansion/Terrain/manifest.json`, currently listing **76 mesh sources** across terrain, roads, water, bridges and transitions. The region spans 1.6 × 1.6 km.

Open [the visual review](../../review.html) for the native capture gallery.

## Evidence

- **Preservation: Verified.** 17,056 total mesh instances inspected after reopen; original placements and protected map bytes compared. [Receipt](../../reopened.json).
- **Persistence: Verified.** Mesh transforms, effective materials, visibility, component collision modes and camera activation checked across reopening. [Receipt](../../reopened.json).
- **Editor inventory: Passed.** 338 expansion actors, 92 mesh families and 17 ground checkpoints inspected; 2 warnings. [Receipt](../../validation.json).
- **Settlement collision: Recorded.** 225 settlement actors use private mesh copies with the authored third LOD for complex collision. Their triangle-placement proxy changes from 30,703,652 to 3,695,418 (about 30.7M → 3.7M). Original render geometry, materials and source files were checked. This proxy is not memory usage or a measured physics speedup. [Receipt](../../settlement-collision.json).
- **Forest contacts: Recorded.** 12 tree samples checked in Play against terrain with foliage ignored; separate simple trunk rays identify the expected instance. The region uses a private tree mesh with a 30cm-radius, 260cm-tall simple trunk capsule; original tree assets stay unchanged. 0 review warnings. This does not establish capsule traversal through the forest. [Receipt](../../forest-contact-play.json).
- **Collision traversal: Passed.** 8/8 routes passed using possessed CharacterMovement, including the home-to-hub connection and both bank transitions across the full city river bridge. Initial position is teleported per route; segments use AddMovementInput. [Receipt](../../traversal-receipt.json).
- **Final homestead transition: Passed.** The home approach was walked again after the final apron terrain change. This supplements the eight-route receipt and checks the edited connection with real CharacterMovement. [Receipt](../../home-apron-traversal.json).
- **Fresh default Play: Recorded.** 1,200 editor world-frame samples; mean 16.67 ms, p95 16.93 ms, max 51.56 ms. Includes editor overhead and is limited to this camera and scene state. [Receipt](../../idle-observation.json).
- **City-view passive sample: Recorded.** 1,201 editor world-frame samples at a selected city viewpoint; mean 16.66 ms, p95 16.96 ms, max 49.95 ms. Separate from traversal and collision-query runs; not a shipping CPU/GPU profile. [Receipt](../../city-observation.json).

## Acceptance limits

Ground probes check sampled simple/complex Visibility hits and expected elevations. Traversal uses the possessed explorer with real gravity and collision, but teleports to the start of each short route. Neither covers every path between settlements or proves physical keyboard input.

The passive profile records editor world-frame deltas for one fresh default Play viewpoint. It is not a shipping GPU/CPU profile or a city simulation budget. Automatic LOD screen thresholds are inventoried; a full continuous visual transition review remains separate.

Traversal frame deltas are excluded from the passive performance claims because diagnostic collision queries ran during that traversal session. Use the separate idle and city observation receipts for their stated viewpoints.

Native visual review: the final city avenue has grounded architecture, coherent materials and a civic focal point. The river-gorge extrusion and exposed black water underside were repaired. The broad mineral terrain remains visibly simpler than the homestead’s rich groundcover and stone detail, including around the new apron. Village street layouts are repeated; more local identity and edge dressing remain worthwhile visual follow-up.

NPC life, economy, quests, navigation across every district, spatial streaming and a complete terrain/settlement walk-through remain future work.

## Reproducing the receipts

Only the coordinator uses the connected Terrarium editor. End Play before `validate_world.py` or `snapshot_world.py`. The snapshot request names are `original-baseline`, `admitted` and `reopened`; the baseline refuses overwrite. After the admitted snapshot, save, switch to another map, reopen ValleyRegion and run the reopened snapshot.

Run `validate_traversal.py` with `traversal-request.json`, then start Play. Stop that Play session after its receipt. For the idle profile, arm `observe_play.py` with `observation-request.json` and start a fresh Play session; perform no imports or captures during the five-second warmup and 20-second sample. Regenerate this review with `python Scripts/WorldExpansion/build_review.py` after captures and receipts.

## Effective terrain replacements

The initial admission receipts are historical for replaced chunks. The current stack is the source manifest plus `_GorgeV2` valley replacements, `_HomeApronV3` replacements/addition, and the tributary `_SeamV4` replacement. Later entries override earlier mesh bindings; `validation.json` and the reopened snapshot are authoritative.

- [terrain-gorge-000.json](../../terrain-gorge-000.json)
- [terrain-apron-000.json](../../terrain-apron-000.json)
- [tributary-seam-repair.json](../../tributary-seam-repair.json)

| Actor | Effective mesh |
| --- | --- |
| `WX_HomeApron` | `SM_HomeApron_HomeApronV3` |
| `WX_HomeTributary` | `SM_HomeTributary_SeamV4` |
| `WX_Terrain_3_3` | `SM_Terrain_3_3_HomeApronV3` |
| `WX_Terrain_3_4` | `SM_Terrain_3_4_HomeApronV3` |
| `WX_Terrain_3_7` | `SM_Terrain_3_7_GorgeV2` |
| `WX_Terrain_4_3` | `SM_Terrain_4_3_HomeApronV3` |
| `WX_Terrain_4_4` | `SM_Terrain_4_4_HomeApronV3` |
| `WX_Terrain_4_6` | `SM_Terrain_4_6_GorgeV2` |
| `WX_Terrain_4_7` | `SM_Terrain_4_7_GorgeV2` |
| `WX_Terrain_6_7` | `SM_Terrain_6_7_GorgeV2` |

## Source handoff

- Working map: `/Game/Terrarium/WorldExpansion/Maps/ValleyRegion`; original StartingHome and HomesteadBlender map files remain protected by the baseline hash receipt.
- Terrain source and geometry: `Scripts/WorldExpansion/terrain_source.py` and `SourceAssets/WorldExpansion/Terrain/manifest.json`. Apply source revisions through the coordinator’s native mesh admission/replacement scripts; existing admitted assets with different source hashes must receive explicit replacement handling.
- Settlement placement sources: `settlement-layout.json` and additive `settlement-dressing-layout.json`. Their integration receipts record final mesh assignments, counts and native FoliageTypes.
- Building collision copies: `/Game/Terrarium/WorldExpansion/Architecture/Meshes`; effective bindings are recorded in `settlement-collision-assets.json`. Render LODs and materials match the protected approved sources; authored LOD2 supplies complex collision.
- Forest source placement list is in the terrain manifest. Private `/Game/Terrarium/WorldExpansion/Forest/SM_WX_BroadTree5m` carries the simple trunk capsule. `forest-contact-play.json` supersedes editor-world trunk misses for runtime query acceptance.
- `reopened.json` is the final scene persistence authority when its passed flag is true. Named water NoCollision profiles are required for persistence; do not infer success from the earlier custom-profile state.
- The nine PNGs in `Captures/` are native editor views. Rebuild this review after replacing captures or receipts with `python Scripts/WorldExpansion/build_review.py`.
