# Voxel world direction pass

Status: reverted at the user's request. The working scene now retains the
original soft treatment with the separate collection-wide detail refinement
documented in `../DetailPass/review.md`. This file records the rejected pass.

User concern: the current world lacks the concept's voxel feel.

The native HomesteadFidelity map now uses sharp square cliff blocks with shallow
face offsets, square turf caps, larger axis-aligned leaf clusters, and discrete
world-space grass color patches. The existing cottage, bridge, paths, camera,
lighting, and other static landmarks retain their transforms.

Replaced 2,076 cliff instances, 14 trees, and 620 shrubs. New foliage types own
the replacement meshes so they persist across map loads. The new materials have
the InstancedStaticMeshes usage flag saved. Existing shared assets were retained.

## Evidence

- `before.png`: native capture before this pass.
- `voxel-world.png`: final native 962 x 1618 render, visually inspected.
- `verification.json`: identical instance counts and material assignments before
  and after save/reopen; static landmark transforms match the comparison map.
- Meshkit's saved-mesh round trips report zero normal errors for all five final
  replacement mesh types. All five added Python scripts parse.
- Comparison map: `/Game/Terrarium/Maps/HomesteadBeforeVoxelPass`.
- Working map: `/Game/Terrarium/Maps/HomesteadFidelity`.

The first reload attempt crashed Unreal with a world-cleanup error after an
unsaved map duplication. The editor was restarted and the comparison map was
persisted using the native save_map operation. This also exposed transient
component-only mesh swaps; the final implementation uses separate foliage types
and passes save/reopen verification. No packaged-game, collision, or gameplay
testing was performed.

The voxel silhouettes and stone courses are more explicit. This is a focused
art-direction change, not a claim of matching the entire concept. Fine flowers,
wheat, and water still use their earlier treatment; the new ground pattern also
has a more regular grid than the reference.

To reproduce from the comparison scene saved as HomesteadFidelity, run
`voxel_world_pass.py`, then `refine_voxel_cliffs.py` through the verified editor
MCP console. Validate with `verify_voxel_world.py` and capture using
`capture_voxel_world.py`. Capture completion requires a drawing editor viewport.
