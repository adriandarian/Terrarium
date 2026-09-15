# Gap 07: quieter ground surfaces

Implemented `Scripts/Assets/meadow_v5.py`, producing unique asset
`/Game/Terrarium/Meshes/SM_MeadowTile_v5` when its `build()` runs in Unreal.

The prior recipe used 43 randomly overlapping small rectangles plus the
high-frequency `M_WeatheredDetails` material. This version uses six much broader
uneven convex moss/grass polygons over a quiet olive-earth substrate. The muted
adjacent colors are carried by vertices with only 0.8 percent component color
variation. Polygon tops stay between z=5.9 and z=6.075. Two small subdued stones
form one sparse accent. No dense raised grass or pebble surface is added.

The ground remains 206 by 206 units with a 320-unit solid substrate and the same
cap dimensions as v4. All generated geometry stays within the XY tile footprint.
The recipe uses the default meshkit vertex material and does not assign
`M_WeatheredDetails`; the parent scene pass can apply its coherent surface material.

## Offline verification

Executed the actual `build()` with only Unreal imported as a stub and `Mesh.save`
replaced by a mesh return. Meshkit's actual geometry construction asserted
outward faces, closed component edge incidence, and positive component volumes.

- Python AST syntax: passed.
- 168 vertices, 296 triangles, 10 closed positive-volume components.
- Bounds: X [-103, 103], Y [-103, 103], Z [-320, 9].
- Six moss polygons span 3,146 to 6,263.5 square units each before overlap.
- All vertex coordinates finite; repeated builds produce identical vertices.

Editor import, saved-mesh validation, placement, and visual comparison remain
for the parent agent's sequential Unreal integration. Offline construction alone
does not establish a resolved visual gap in the rendered scene.
