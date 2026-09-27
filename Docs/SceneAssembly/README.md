# Concept scene assembly — 2026-09-27

Saved level: `/Game/Terrarium/Blender/Maps/HomesteadBlender`.

The editor is left on `Baseline_Orthographic_Review`, preserving the original concept framing. `SceneAssembly_WholeWorld_Review` shows the outlying buildings, and `SceneAssembly_Courtyard_Review` shows the character scale near the cottage.

## Changes

- Replaced the previous player reconstruction with the Blender Player, fitted to 160 cm. Added Ranger Sela at 160 cm, Kindlehorn at 125 cm and Rillip at 80 cm. Placement heights use live terrain traces.
- Added the Homestead Compound at 0.90 scale in the western clearing. Kept the central cottage, shed, garden, fence and established paths intact.
- Moved the civic hall to the northern clearing and reduced its scale from 0.85 to 0.72. Added four trail sections connecting its approach to the northern path.
- Narrowed the river bridge from approximately 309 cm to 193 cm. Its 719 cm span, 280 cm deck elevation and riverbed pile depth remain intact.
- Enlarged 14 landmark trees by 40 percent around their existing root contacts. Rechecked Brambit's courtyard contact.

## Coverage

All **31 primary model families** are represented in the scene: **26 canonical models plus five families represented by fitted placement variants**. Those five are CliffFace via CliffColumn, MossCap via MossFringe, TrailTerrain via TrailPatch, WheatField via WheatPatch, and RiverCrossing via RiverBridge, StoneStairs and BridgeThreshold. The canonical alternatives were not stacked on top of their fitted variants. All 45 surface alternatives remain available in the material library.

## Validation

Reloaded the saved level and verified changed actor meshes, material assignments and transforms. Verified all 14 adjusted tree instances after reload, all 31 family bindings, new approach ground samples, bridge dimensions and pile depth. Inspected native editor captures of the concept view, expanded world and courtyard. No dirty map packages remained at completion. Whitespace check passed.

This is a static composition pass. Model geometry, terrain block shapes, foliage and palette still differ from the original concept. Characters remain static; animation, navigation, gameplay and performance were not tested. The editor continues to report pre-existing high-triangle collision warnings for two meshes.

## Evidence

- [Before](Before/unreal-viewport.png)
- [After, concept framing](After/unreal-viewport.png)
- [Expanded world](WholeWorld/unreal-viewport.png)
- [Courtyard scale](Courtyard/unreal-viewport.png)
- [Coverage and saved-map checks](verification.json)
- [Placement changes](changes.json)

A pre-edit map backup is retained at `Saved/HomesteadBlender-before-scene-assembly.umap`. The initially open review map's unsaved state was saved before switching; its preceding on-disk copy is retained at `Saved/RemainingModelsReview-before-scene-assembly.umap`. Source Blender models, exports, existing uncommitted model work and original reference maps were preserved. No commit or PR was created.
