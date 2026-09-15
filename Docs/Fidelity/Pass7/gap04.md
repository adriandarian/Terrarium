# Gap 04 - Natural cliff block construction

Implemented source recipe: `Scripts/Assets/cliff_column_v4.py`.

The previous v3 column used four almost full-width stone courses, which made
neighbouring columns look like a masonry wall. The new column uses four corner
stacks with different fracture heights, mixed tall and short stones, variable
widths and depths, softened corners, and four asymmetrical projecting shelves.
A recessed continuous rock core prevents holes through the landscape. Moss is
restricted to the upper cap and sparse descending patches, leaving broad stone
faces visible. This change addresses the block construction; terrace layout
and instance distribution remain separate integration work.

## Integration

- Import `cliff_column_v4` with `Scripts/Assets` on the editor Python path.
- Call `cliff_column_v4.build()` once. The API is unchanged and returns the saved
  Unreal StaticMesh.
- Unique output: `/Game/Terrarium/Meshes/SM_CliffColumn_v4`.
- Replace existing cliff column mesh references while retaining transforms.
  Vary existing instances' Z rotation in 90-degree increments where practical
  so the asymmetric fractures do not repeat along the entire cliff.
- Nominal footprint stays 100 cm. Exact geometry bounds are
  X [-57.674, 55.916], Y [-57.000, 57.454], Z [-1.582, 323.500] cm.
  These small protrusions are intentional, and the cap height matches v3.
- 31 closed components, 744 vertices, 1,364 triangles.

## Validation

AST parsing passed. Executed the actual generator with the real meshkit
construction functions and only `Mesh.save` stubbed. All component closure,
outward triangle winding, nondegenerate-face and positive-volume assertions
passed. No Unreal/editor calls or binary files were modified by this agent.
Editor asset creation, saved mesh round-trip validation and visual acceptance
remain pending the root agent's sequential integration.

## Follow-up after pass-7 visual review: v5 variants

The composed pass-7 capture still reads as clean repeated masonry. Added
`Scripts/Assets/cliff_column_v5.py`: `build('A')`, `build('B')`, `build('C')`
return individual meshes; `build_variants()` returns an A/B/C keyed dictionary
of saved meshes. Unique outputs are `SM_CliffColumn_v5A`, `SM_CliffColumn_v5B`,
and `SM_CliffColumn_v5C` in `/Game/Terrarium/Meshes`.

Unlike v4's identical box bevels, stones now use convex eight-sided profiles
with independently clipped corners and unequal top/bottom bevels. Four corner
stacks have independent fracture heights, with four or five differently sized
stones each. Shallow face fragments add limited weathering relief. Nine smaller
unequal cap patches and clustered descending moss chunks replace the uniform
four-part cap. Three deterministic variants support mixed placement per cell.

All variants have an 84 cm core, z bounds [0, 323.5] cm and outer XY bounds
within roughly [-56.2, 56.4] cm. A/B each contain 73 closed solids and 3,500
triangles; C contains 68 closed solids and 3,280 triangles. Local AST and actual
meshkit closure/winding/nondegenerate-face/positive-volume assertions passed
again with only save mocked. Editor and visual acceptance remain pending.

Integration finding: terrain_v7 places the meadow surface at approximately
h+6 while the cliff's top is h, masking the uneven moss cap behind a continuous
meadow lip. The meadow substrate is 74.54 cm wide at placement scale, slightly
larger than the 73.8 cm cliff core. Root should consider a surface-only edge
meadow asset and lift the cliff cap toward the surface height so its irregular
edge can be seen. No shared terrain script was changed by this agent.
