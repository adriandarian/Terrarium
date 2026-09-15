# Gap 15: cottage proportions and architectural detail

Implemented in `Scripts/Assets/cottage_v5.py`, producing `SM_Cottage_v5` through `build()`. The pure geometry entry point `build_mesh()` also supports offline inspection with the real meshkit geometry code.

- Compresses the wall zone z=60..306 by 17%, lowering the eaves and all roof/chimney geometry by 41.82 cm. Keeps the original footprint, footing, three entrance steps, and roof pitch. The shorter wall-to-roof proportion creates a more compact cottage without flattening the gables.
- Applies the transform to every finished vertex, including windows, doorway, chimney, projecting gable and roof helpers, then recalculates component center/volume metadata.
- Replaces broad foundation stones with two small staggered courses; adds pegged timber joints, short corner braces, sill brackets and a threshold.
- Integrates gap 14 `add_main_roof` and `add_projecting_gable_roof` helpers in place of both old coarse tile loops. Retains the chimney, projecting gable solid, window and frame.
- Does not assign the old high-frequency M_WeatheredDetails material. Shared material treatment remains owned by the integration pass.

## Offline evidence

Ran `build_mesh()` with the actual meshkit primitives and only an empty `unreal` module stub (no geometry implementation was mocked). Verified all 602 components have closed two-use edges, positive volume, finite vertices and nondegenerate outward-facing triangles after compression. Result: 14,402 vertices; 26,396 triangles. Bounds in cm: x -228.27..200; y -298..231.79; z -12..545.18. Below-ground step supports retain their original elevations.

## Remaining editor verification

The root integration must build the asset in the verified Terrarium editor, replace the cottage actor mesh, apply the shared material, save, and inspect the gameplay camera capture. Confirm the compact silhouette, fine roof tiles, doorway visibility, foundation contact and projecting gable junction. Offline geometry checks do not prove visual fidelity or editor import success.
