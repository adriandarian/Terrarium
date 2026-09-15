# Gap 05 - Broken terrace silhouettes

Implemented `Scripts/Fidelity/terrain_v7.py`, retaining `build() -> cells`.

The grid changes from 90 to 72 cm so the reference-traced outlines resolve into
smaller steps. The new asymmetric `CliffColumn_v4` columns receive independent
quarter-turn rotations. Fourteen additional intermittent rock shelves extend
from upper/main terrace faces into lower terrain, 76, 108, or 144 cm below the
parent surface. Each shelf extends all the way to its lower supporting ground
and carries a thin grassy top. Their distribution follows two spatial waves
and a fixed random seed, rather than a repeated edge border.

Every original reference height and landmark coordinate stays unchanged.
Path corridors and building/bridge/stair anchors are protected. The 280 cm
river-facing terraces are reserved for the separate shoreline pass.
The continuous 84 cm rock core determines instance width, with 2.5 percent
overlap so rotating fractured exterior geometry cannot reveal holes.

## Integration

Import `terrain_v7` instead of `terrain`; its build call is unchanged.
Requires the separately generated `CliffColumn_v4` asset. MeadowTile_v4 and
WaterTile_v3 remain named explicitly to avoid assuming future assets exist;
the ground/water integration passes should replace those two names as needed.

## Offline evidence

Executed the actual build with only `placement.place_xyz` replaced by a recording
stub. Results: 5,841 terrain cells; 14 shelves; 6,759 total placements, comprising
5,855 meadow tiles, 714 cliff segments and 190 retained water tiles.

Assertions passed for every cell matching `reference.height`, positive finite
transforms, deterministic shelf placement, shelves rising above supporting
terrain, and shelf clearance from paths and anchors. Cottage, shed, well,
lantern and stair-top anchors each lie within 45 cm of a matching-height terrain
cell center (grid spacing 72 cm). The bridge deck intentionally spans water.

No editor or binary changes were made here. Saved mesh validation, rendered
seams, collision behavior and visual acceptance require root integration in
the connected Terrarium editor.
