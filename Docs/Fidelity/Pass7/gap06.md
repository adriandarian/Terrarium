# Gap 06: irregular grass-to-rock transitions

Implemented `Scripts/Assets/cliff_moss_v1.py` and
`Scripts/Fidelity/moss_v7.py`. The original `SM_CliffMoss_v1` recipe adds an
asymmetric moss cushion with three descending fingers of different lengths.
Placement selects intermittent exposed terrace edges on the 72 cm terrain grid,
with variable fringe width and trailing length. Most stone remains uncovered.
Roots extend into the continuous column core so the mesh stays attached across
the rock's recessed cracks; the lip cushion overlaps the meadow surface.

Integration: build `cliff_moss_v1` through the editor mesh pipeline, perform the
asset visual review required by placement, and call `moss_v7.build(cells)` after
`terrain_v7.build()`, before the shared placement flush. This creates 22 patches
on the current reference terrain. No existing asset or map was edited by this
subtask.

Offline verification passed using the real meshkit with only Unreal and the
save/placement boundary stubbed: 31 closed positive-volume solid components,
744 vertices, 1,364 nondegenerate outward-wound triangles. Bounds are
X -26..19.43, Y -21.5..20.68, Z -114.5..5 cm. Placement is deterministic even
when cell insertion order is reversed; all 22 anchors pass the path/building
protection mask and trailing geometry remains above river level. Full native
mesh round-trip and scene appearance still require the parent editor pass.
