# Stepped terrain source, revision 5

This replaces the broad low-poly region ground with real stepped geometry.
Mountains use 5 m modules, variable 0.45–4 m shelves, explicit vertical risers,
and broken projecting stone courses. The home apron uses 1 m modules and
0.22–0.87 m local strata outside the measured original homestead perimeter.
The materials are separate private imagegen grass and moss-stone materials.

## Source and geometry contracts

- `manifest.json`: 130 source meshes in 65 integration chunks.
- Region bounds: X/Y -800 to +800 metres, Z-up; native admission converts to cm.
- Total triangles: 1,552,357. The largest individual mesh has 66,252 triangles.
- Source UVs repeat every 2 physical metres, with dominant-plane projection on
  cliff walls. Vertex colors are modest neutral tints; image textures carry color.
- Original homestead binary assets and actors are never edited by this pipeline.
- Exact previous triangles remain beneath protected roads, settlement pads and
  river corridors. The measured original home hull, road, water and seam guards
  preserve all 6,035 protected apron cells exactly.
- Forest XY/order/scale/yaw remain identical; the manifest updates their root Z
  to the new shelves. Retained trees require those elevation updates or traces.

## Rebuild and admit

`python Scripts/WorldExpansion/voxel_terrain.py` rebuilds all regional and apron
source meshes. `python Scripts/WorldExpansion/voxel_terrain_verify.py` checks
source hashes, triangle area, UV area, protected routes and forest invariants.

The coordinator runs `Scripts/WorldExpansion/voxel_terrain_admit.py` through the
verified Terrarium editor, sequentially. Its request file is
`Docs/WorldExpansion/voxel-terrain-request.json`, for example
`{"offset": 0, "limit": 4}`. Offsets 0–63 are regional chunks; offset 64 is the
fine home apron. Each chunk admits two role meshes before disabling its previous
actor's visibility and collision. Old mesh assets and actors remain recoverable.

Native material paths:

- `/Game/Terrarium/WorldExpansion/TerrainV5/Materials/M_VoxelGrass`
- `/Game/Terrarium/WorldExpansion/TerrainV5/Materials/M_VoxelStone`

New labels are `WX_` plus each manifest asset name. New meshes use BlockAll and
complex-as-simple collision. Retired components use the explicit NoCollision
profile and are hidden. Admissions produce receipts in
`Docs/WorldExpansion/TerrainV5/`.

## Evidence and limits

`source-validation.json` records offline geometry checks and 177 protected route
cell checks. `home-apron-source-validation.json` records the measured hull and
6,035 unchanged guarded cells. `mountain-geometry-preview.svg` and `.png` show an
orthographic technical projection of the actual stepped source geometry; they do
not substitute for editor image, movement or performance validation.

This revision has one authored mesh LOD. Runtime frame cost, automatic distance
simplification, streaming and broad mountain traversal need native evaluation.
