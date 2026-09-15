# Voxel reconstruction library

**77 original PNGs map to 72 authored Unreal static meshes**, including all 45 surface revisions. Three subagents modeled characters, architecture and collectibles while the main agent built environment and surface pieces, compared Unreal renders, and requested targeted revisions.

[Open the source/model comparison catalog](catalog.html) · [Complete asset map](asset-map.json) · [Validation](verification.json) · [Visual review and remaining differences](visual-review.md)

The player and ranger have separate detailed geometry, complete modeled backs and corrected source-specific clothing and accessories. Every selected model has front and rear Lit renders. Older revisions remain available for comparison; the catalog and galleries select the current revision.

## Unreal gallery maps

| Map under `/Game/Terrarium/Reconstruction/Maps/` | Models | Preview |
|---|---:|---|
| `Architecture` | 7 | [Open](Galleries/Architecture.png) |
| `Characters` | 5 | [Open](Galleries/Characters.png) |
| `Collectibles` | 8 | [Open](Galleries/Collectibles.png) |
| `Environment` | 7 | [Open](Galleries/Environment.png) |
| `Surfaces` | 45 | [Open](Galleries/Surfaces.png) |

All models are at native scale, grounded, labeled, separated and checked after saving and reopening each map. `ReviewStage` is an additional single-model lighting studio. The existing homestead maps are preserved.

## Rebuild and review

Recipes are in `Scripts/Reconstruction/`. The editor build runner reads `Saved/reconstruction-build.json` with a module, source keys and explicit revision number. It refuses an existing mesh path and uses Unreal Geometry Script to create binary assets. `capture_batch.py` produces current-revision Lit comparisons. `ambient_studios.py` adds neutral cubemap lighting to the review maps; allow the editor to advance before capturing a newly loaded sky-lit map. `capture_gallery.py` deliberately separates map preparation and capture.

`python Scripts/Reconstruction/catalog.py` refreshes the offline catalog. `final_report.py` checks all original hashes, latest recipe hashes, current gallery bindings and render coverage. Generated recipe files preserve centimeters, stable ground pivots and source associations.

These are static source-guided reconstructions. Their main shapes and details were revised through visual comparison, but they are not exact copies of the prelit artwork. Rigging, animation conversion, collision tuning, PBR texture reconstruction and gameplay integration remain separate work. See the visual review for specific differences.
