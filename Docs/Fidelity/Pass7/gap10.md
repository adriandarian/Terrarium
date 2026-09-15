# Gap 10: tree shape and scale

Implemented `Scripts/Assets/tree_v3.py`, creating `/Game/Terrarium/Meshes/SM_Tree_v3` through the existing `build()` -> `Mesh.save()` API. This replaces the broad overlapping canopy recipe with eight asymmetrical tiers of smaller leaf sprays, a tapered bent trunk, individually connected branches, and three roots. Separate tier positions leave visible branch and trunk windows; foliage color varies within a restrained green palette.

The reference uses more slender, varied silhouettes than the round block canopies in the supplied current screenshot. This recipe therefore concentrates on silhouette and fine foliage scale rather than adding another large canopy mass. Instance yaw and scale should vary during integration; recommended uniform scales are 0.72–1.02, with taller instances concentrated toward the background and isolated smaller trees near the clearing. The 383.7 cm mesh height must be considered against current actor scales when swapping it in.

## Validation

- Python AST parsed successfully.
- Executed the real meshkit geometry construction with only the Unreal module stubbed and `Mesh.save` replaced by an in-memory return. All existing meshkit positive-volume, nondegenerate-face, outward-winding, and closed-component assertions passed.
- Geometry: 4,968 vertices; 9,108 triangles; 207 closed components.
- Bounds in cm: minimum (-95.684, -75.300, -0.251), maximum (86.396, 82.588, 383.450); total size 182.080 × 157.889 × 383.701.
- Editor asset creation, saved mesh round trip, actor replacement, and visual validation remain root integration responsibilities. This subtask did not call editor tools or modify binary assets.
