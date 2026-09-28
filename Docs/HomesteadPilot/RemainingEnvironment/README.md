# Remaining homestead environment

The river pass replaces the inherited dense prism water surfaces with one closed, 12-triangle tile and a world-continuous current material. All 190 tile envelopes, rotations, depth memberships and top elevations are retained. The stepped shoreline remains in place. Subtle triangular pigment keeps the angular visual language; restrained current streaks and small normal changes provide motion. Water stays opaque, with no displacement, transparency, new shoreline actors or collision.

The three depth materials share the same world coordinates and time. Medium, shallow and deep water differ by a modest palette bias. Fine ripple detail fades with screen derivatives. At twelve triangles per tile, redundant mesh LODs would not help; the whole river contains 2,280 triangles after import. No performance improvement is claimed until the editor is measured.

## Files and coordinator operation

- `SourceAssets/Blender/HomesteadPilot/RemainingEnvironment/RiverSurface3m.blend`: editable normal Blender project, Terrarium scene marker, metres and Z-up.
- Adjacent `SM_HP_RiverSurface3m.fbx`: 3.02 × 3.02 × 0.316 m, eight vertices and twelve triangles.
- `manifest.json`: dimensions, source hash, expected counts and preservation contract.
- `source-validation.json`: separate source reopen and FBX reimport, both closed manifold with positive volume and matching dimensions.
- `river-source-preview.png`: inspected geometry and palette preview. Blender's preview material is an approximation; it does not validate the Unreal HLSL animation.
- `Scripts/HomesteadPilot/RemainingEnvironment/integrate_water.py`: run only through the verified Terrarium Unreal editor with StartingHome open and PIE stopped.

The integration script imports into `/Game/Terrarium/HomesteadPilot/RemainingEnvironment`, duplicates each source FoliageType and migrates only its water instances. Full local-bound fitting includes rotating the pivot offset, so unchanged XY and height envelopes do not depend on an assumed centred pivot. It sets NoCollision on the new types, saves only new assets and the working map, reopens the map, checks all water instances, and compares the protected nonwater transform inventory including all 5,841 grass tiles. Shared FoliageType files and the baseline map are hash checked. Shared Bark, Wheat and Soil materials are not saved or modified.

If migration fails before the first save, the exception handler restores the original water memberships and saves the restored working map. New import assets may remain. The script intentionally refuses a second migration if its final receipt or partial destination FoliageTypes exist; inspect those before retrying. A failed shader compile or visual rejection remains an editor acceptance issue, even when source geometry passed validation.

Coordinator native river close-up and overview review passed: teal color and restrained ripples remain cohesive with the angular banks, successive captures show the current advancing, no bank-boundary gaps were observed, and bridge and grass remain intact. No new shader compilation errors were observed. `unreal-validation.json` confirms all 190 tiles survived save/reopen. The old placed LOD0 water inventory was 1,444,672 triangles; the replacement is 2,280. This is a geometry inventory reduction, not a measured frame-rate claim. Runtime profiling and automatic LOD-transition visual evidence belong to the coordinator's completion/runtime receipts.

## Inherited environment retained

Fourteen other inherited variants total 1,753 instances in `Completion/before.json`: TrailPatch 88, MeadowGrass 569, GroundPlants 498, RockCluster 61, MeadowFlowers 136, ShoreOutcrop 40 across two versions, RiverStones 41, Riverbank 35, MossFringe 209, Bush 67, MossRock 7, AncientTree 1 and FlowerBorder 1. The eleven approved pilot families and grass terrain remain unchanged.

The coordinator's fresh `Completion/collision-before.json` subsequently confirmed every inherited variant had one LOD. `inherited-lod-plan.json` records that measured inventory. `Scripts/HomesteadPilot/RemainingEnvironment/admit_inherited_lods.py` duplicates these meshes into pilot-owned assets and attempts conservative real lower LODs on the twelve substantial meshes. Thin plants/tree/reed meshes initially target 75% and 50% geometry at 0.18 and 0.06 screen sizes; rocks/path initially target 60% and 32% at 0.24 and 0.08. The existing 496-triangle RockCluster and 398-triangle RiverStones stay minimal single-LOD meshes.

Admission checks the duplicate's original LOD0 triangle/vertex/section counts, bounds, material slots and material references, collision flag, collision LOD, simple-collision primitive count and Nanite state against the original. It changes no collision policy or shared material. It duplicates source FoliageTypes, preserves their settings, retains every instance transform and static actor, and verifies a full scene state hash including effective materials, collision and visibility. It restores scene memberships on a migration failure. Source mesh and FoliageType file hashes plus the baseline map hash are checked after save/reopen. Progress receipts and `inherited-lod-validation.json` distinguish asset building from successful admission. These are conservative runtime improvements to existing art, not newly redesigned planting or terrain; final automatic LOD transition quality still requires native review.

Native asset-building stopped before scene migration when generated lower LODs expanded FlowerBorder's aggregate bounds by 0.0564 cm and TrailPatch's by 0.6165 cm. Aggregate bounds cover all LODs, so they are not an exact LOD0 geometry test. The admission independently hashes every actual render-LOD0 triangle's exact positions and connectivity, preserving winding while ignoring triangle ordering. It requires that hash to match the source before saving and after reopening; this check passed natively on both attempted assets.

The aggregate lower-LOD envelope budget is **1% of the original longest local dimension**, recorded with each actual absolute and relative difference. This uses the object's overall size because LOD screen thresholds use projected object size; using the height of a thin path or a fixed tolerance for both tiny foliage and a large tree is not comparable. TrailPatch is 232 cm long, so its 0.6165 cm expansion is about 0.266%, within a 2.32 cm budget. This is an envelope diagnostic, not a guarantee of maximum per-vertex simplification error. Near geometry, LOD0 collision, materials and transforms still must match exactly. Lower-LOD visual transitions require native review.

MeadowFlowers' first reduction exceeded that fixed budget (1.2990 cm versus its 0.5298 cm limit). The script now adapts its reduction settings instead of increasing the tolerance: after the initial target it tries 85%/70%, then 94%/88%. It records every attempt's actual triangle counts and bound change. If none satisfies the original budget and produces decreasing triangle counts, it removes the generated lower LODs and records a single-LOD exemption. Exact render LOD0, materials and collision still must pass. This fallback applies to every remaining candidate and keeps the same envelope policy for the collection.

Completed duplicates listed in this operation's build receipt can resume only when the source identity and render-LOD0 digest match; they are not rebuilt unnecessarily. The known partial FlowerBorder, TrailPatch and MeadowFlowers destinations can also be reused after source contract and digest checks. Resumption stops if any scene-migration progress exists. Unknown partial destinations still stop admission.

## Final native admission results

The adaptive native run succeeded. `inherited-lod-validation.json` records **14 pilot-owned meshes and 1,753 instances**, with twelve actual three-LOD chains and the two intentionally small single-LOD stone meshes. No substantial mesh required the single-LOD fallback. MeadowFlowers and MossFringe passed at 85%/70%; Bush passed at 94%/88%. All other substantial meshes passed their original targets. The envelope budget remained 1% of original longest dimension throughout.

| Retained family | Actual LOD0 / LOD1 / LOD2 triangles |
| --- | --- |
| FlowerBorder | 2,376 / 1,782 / 1,188 |
| TrailPatch | 5,554 / 3,332 / 1,778 |
| MeadowGrass | 1,532 / 1,148 / 766 |
| GroundPlants | 3,092 / 2,318 / 1,546 |
| RockCluster | 496 — minimal single LOD |
| MeadowFlowers | 1,708 / 1,452 / 1,196 |
| ShoreOutcrop | 1,646 / 988 / 526 |
| ShoreOutcrop v2 | 1,118 / 670 / 358 |
| RiverStones | 398 — minimal single LOD |
| Riverbank | 59,508 / 44,630 / 29,754 |
| MossFringe | 92,016 / 78,214 / 64,412 |
| Bush | 2,832 / 2,662 / 2,492 |
| MossRock | 78,300 / 46,980 / 25,056 |
| AncientTree | 250,668 / 188,000 / 125,334 |

The native admission verified exact render-LOD0 geometry digests, the original material/collision contracts, shared mesh and FoliageType file hashes, and the baseline map hash. Save/reopen retained the full protected scene state hash. The coordinator additionally switched to a different map and reopened StartingHome; `Docs/HomesteadPilot/Completion/persistence.json` records stable assignments, effective materials, visibility, counts and transforms. The eleven approved pilot families and all 5,841 grass tiles remain unchanged. These receipts establish admission and persistence; they do not independently establish the visual quality of every automatic LOD transition.
