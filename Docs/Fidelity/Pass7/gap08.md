# Gap 08: earthy paths and broken edges

## Implementation

- `Scripts/Assets/path_v4.py` creates the new, unique `SM_PathTile_v4` asset via the existing `build()` API. It replaces the rectangular transverse mosaic with five broad overlapping polygonal soil patches over a continuous base. Color variation is muted and baked into geometry, with no noisy material changes.
- Irregular soil lobes, six low moss patches, and two small embedded stones soften the banks. All components are convex closed solids using the existing meshkit validation. Maximum local height is 2.5 cm, avoiding paving-like relief and plank shadows.
- `Scripts/Fidelity/paths_v7.py` retains `build()`. `sample_track()` samples each complete path at uniform arc distances around 155 cm, regardless of input vertex density. It prevents dense smoothed traces from compressing the repeated asset into thin transverse strips. Tiles overlap along the track and vary their asymmetrical orientation and width slightly.
- Original route data and exact bridge/stair anchor transforms are retained. The integration owner can replace the two prop mesh names for gap 17 without moving the anchors.

## Integration

1. Build `path_v4` through the connected Terrarium editor's existing asset pipeline.
2. Complete the required asset preview and saved-mesh validation, recording the actual visual-review result before placement (the existing `placement.mesh()` gate requires it).
3. Replace the old paths module with `paths_v7` in the scene orchestration, then rebuild the scene using its normal lifecycle so old path instances do not remain.
4. Preview bends, intersections, cottage entrance, stair landing, and bridge approaches at the final camera and close range. Check that overlapping track tiles read as continuous soil with no exposed seams or depth flicker.

## Offline validation performed

Executed Python against the real meshkit geometry generation with only `unreal` and the save operation stubbed. Its outward-winding, closed-edge, and positive-volume assertions passed for all 22 components (480 triangles). All vertices are finite and surface relief remains at or below 2.5 cm.

Executed the placement code with a recording placement adapter. A 1,000 cm line with two vertices and the same line with 1,001 vertices both produce the same seven placements. Duplicate points, an entirely degenerate path, and invalid zero spacing were exercised. The final two placements compare exactly to the original module, proving unchanged bridge/stair anchors. Current reference traces produce 64 track instances instead of 124; longitudinal scales range from 0.781 to 0.805, avoiding compressed slivers.

No editor/MCP operations or binary assets were changed by this subagent. The offline checks establish geometry and placement behavior; final image fidelity is pending editor inspection.
