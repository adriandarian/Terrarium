# Terrarium — starting home pilot

Open [the visual review](review.html) for the matching close-view before/after comparison, final world view, LOD tabs and the four supplied settlement references.

The pilot establishes a complete, explorable homestead as the starting home for a larger world. It includes eleven finer model families with textured materials and three implemented LODs per family:

- Architecture: complete cottage, fence and modular bridge.
- Ground and connections: moss cliff, fine cliff column, worn path and stone stairs.
- Planting: broad tree, shrub ground cover, wheat and garden patches.

The cottage has a real doorway and interior. Its warm plaster, weathered terracotta and timber connect to earthy retaining stone, paths and clustered planting. Architecture uses authored FBX LOD chains; landscape uses Unreal mesh reduction. Material assignments and screen-size thresholds are present in the actual Unreal meshes. Fixed-camera LOD captures compare representations, but do not alone prove every automatic transition looks correct during motion.

## Verified traversal

The possessed explorer passed all three tested routes with gravity and collision active:

| Route | Result |
| --- | --- |
| Cottage: enter, walk inside and exit | Passed |
| Terrace stairs: climb and descend | Passed |
| River bridge: cross both spans and return | Passed |

The harness used movement input and checked destination, expected elevation and CharacterMovement walking mode. Teleportation was limited to each route's initial setup. WASD and mouse-look controls are implemented, but physical held-key input has not been manually verified through the available editor tool.

## Local performance evidence

A twenty-second PIE sample after five seconds of warmup recorded 848 frames at a 1,526 × 910 viewport:

| Measurement | Frame delta |
| --- | ---: |
| Mean | 23.58 ms |
| 95th percentile | 52.40 ms |
| Maximum | 117.17 ms |

The maximum includes a hitch. This is a local Unreal editor measurement on a Ryzen 9 5950X and Radeon RX 6950 XT, including editor overhead. It does not separate CPU and GPU time and is not a packaged-game benchmark, a district budget or a multi-city performance claim. Hardware, settings, memory and methodological limits are recorded in [Runtime/Validation.md](Runtime/Validation.md).

## Validation receipts

- [Final integrated review and remaining scope](FinalReview.md)
- [Saved and reopened map](reopen-verification.json)
- [Saved runtime verification](Runtime/saved-runtime-verification.json)
- [Fresh default Play spawn and camera](Runtime/fresh-spawn-verification.json)
- [Runtime validation and remaining acceptance](Runtime/Validation.md)
- [Movement trace](Runtime/traversal-receipt.json)
- [Actual Unreal mesh LODs](Runtime/mesh-runtime-receipt.json)
- [Performance samples](Runtime/performance-receipt.json)
- [Architecture source, UV and FBX checks](Architecture/reopen-verification.json)
- [Landscape source checks](Landscape/reopen-validation.json)
- [Architecture notes](Architecture/README.md)
- [Landscape notes](Landscape/README.md)

Saved-source verification, saved-map persistence, implemented controls, automatic LOD transitions and visual approval are separate claims. Consult the corresponding receipts rather than treating successful import or a screenshot as proof of every stage.

## Scope

The four supplied references progress from homestead to village, town and city while retaining a shared material and terrain language. They establish art direction and future scale; they do not by themselves specify settlement-growth gameplay. The eventual city is one settlement among many.

This deliverable is the starting home's art and traversal foundation. It is not a finished open world, completed city, spatial-streaming system or approved budget for all future settlements. The existing baseline and editable sources are retained for comparison. Broader visual acceptance, physical input testing and distance behavior in motion remain distinct review work.

The review page uses local images and no external dependencies. Its before/after divider supports pointer and arrow-key input; its LOD tabs support arrow, Home and End keys. Reference and review images open in a dismissible full-size viewer.
