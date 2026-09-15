# Gap 13 — shoreline transitions

Implemented `shoreline_v7.build(cells)` and original `SM_ShoreOutcrop_v2`
recipe. The shoreline pass finds actual exposed 72 cm terrain cells and places
intermittent groups along the visible river banks. Unequal stone shelves face
the water, overlap the terrain, and have solid cores extending below water.
Their widths, depths, heights, and pocket spacing vary independently. Middle
shelves support reeds; upper moss shelves support occasional small bushes.
Open bank intervals remain between groups. A world-space clearance capsule
protects the bridge and both approaches.

Integration: generate `Scripts/Assets/shore_outcrop_v2.py` through the editor,
visually validate that asset, then call `shoreline_v7.build(cells)` after
`vegetation_v7.build(cells)` in the Pass 7 scene builder. The vegetation pass
must not also place the old shoreline loop.

Offline verification on the current `terrain_v7.sample_cells()`:

- 25 stone shelves, 20 reed groups, 9 moss bushes.
- Deterministic placement across repeated calls; finite transforms.
- All shelf centers exceed the 180 cm bridge exclusion radius; minimum is
  225.16 cm. Each shelf's submerged core intersects the adjacent bank footprint.
- All shelf bases extend below water z=0.
- Original mesh: 336 vertices, 616 triangles, 14 closed components with positive
  volume. Meshkit's construction assertions passed for face orientation,
  manifold component edges, and nondegenerate faces.
- Mesh bounds: x [-76, 107.5], y [-59.6, 85], z [-65, 105.4] cm.

Editor import, saved mesh normal checks, and final camera visual review remain
the integrating agent's validation work. No editor calls or binary assets were
modified by this subagent.


## Structural terrain follow-up

Revised shoreline placement for `terrain_v8`: accepts every positive bank
height, includes outer edges of its broad river shelves, and skips cell edges
buried inside those shelves. This resolves the previous restriction to only
280/560 cm banks, which omitted newly lowered 128/144 cm terrain. The original
smaller stacked `ShoreOutcrop` now dominates; v2 shelves are a minority, with
reduced height scaled to the actual neighboring bank. Both use varied yaw and
anisotropic scale. Root-added `RiverStones_v1` placement is preserved and now
extends from both shelf types.

Offline test with current `terrain_v8.terrain_specs()` and its runtime height
patch: 32 original outcrops, 8 v2 shelves, 28 reed groups, 19 moss bushes, and
77 shallow stone groups. Candidate detection includes 83 edges below 200 cm.
Repeated specs match; every outcrop/river-stone origin lies below water and
outside the bridge exclusion capsule (minimum center clearance 180.50 cm).
Python compilation and whitespace checks pass. Final editor appearance still
requires root validation.
