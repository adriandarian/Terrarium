# Homestead architecture pilot

The pilot supplies a complete cottage, a reusable fence span and a bridge module. It replaces neither the canonical Blender assets nor the original homestead map. These are source assets for an explorable starting home; they are not a fixed-camera diorama or a finished city kit.

## Deliverables

- Editable normal project: `SourceAssets/Blender/HomesteadPilot/Architecture/HomesteadArchitecture.blend`.
- Nine FBXs: `SM_HP_Cottage_LOD0/1/2`, `SM_HP_Fence_LOD0/1/2`, `SM_HP_Bridge_LOD0/1/2`.
- Four packed and external base-color textures, copied byte-identically from the existing project surface artwork.
- Eight named material slots, full UV coverage and an explicit manifest containing source bounds, dimensions, material colors, roughness, texture paths and traversal notes.
- Textured front, rear, roof, entrance, fence, bridge and cottage LOD previews. `Cottage_interior-lit-QA.png` uses a temporary review-only interior light; it is not baked into a texture, saved into the source or exported as a gameplay light.

The saved source initially displays the cottage at LOD0. Other family/LOD collections are retained and can be enabled in the Outliner. Geometry remains separated into editable parts: roof courses, fascia, frames, posts, interior structure, floorboards, door, stonework and trim.

## Scale and navigation contract

All source units are **metres**, with **Z up** and the cottage **front facing -Y**. Pivots are at the ground base and centered around the main footprint. Import into Unreal at scale **1** with unit conversion enabled; a metre must become 100 cm. The cottage has a 5.0 × 4.4 m main wall footprint; its complete bounds including sills and entrance steps are approximately 5.76 × 5.76 × 5.395 m.

The cottage floor is 24 cm above the base, reached by two 12 cm entrance rises. The door is modeled open at 105 degrees. Its unobstructed frame opening is 128 cm wide and 218 cm above the floor. The shell includes a real interior, ceiling/roof undersides, rafters, bench, shelf and hearth. Opaque teal panes retain the reference character; they do not admit exterior illumination, so the explorable interior needs a modest local light or another deliberate game-lighting treatment.

The bridge module is 3.6 m long on local Y, with a 2.04 m deck and deck top at Z=0.32 m. Two modules can cover a 7.2 m crossing. Side rails leave both ends open. To match a path surface at elevation H centimetres, set the module actor base to **H - 32 cm**. Supporting piles and bank interfaces belong to the level assembly. Fine 12 mm deck joints are modeled; capsule support is different from testing a point exactly in a joint.

Do not generate a single convex collision hull for the cottage: that would seal its doorway and interior. Use an appropriate static complex surface or separate wall/floor/step collision bodies. Blender does not establish Unreal collision or controller behavior.

## Geometry and distance representations

| Asset | LOD0 triangles | LOD1 triangles | LOD2 triangles |
| --- | ---: | ---: | ---: |
| Cottage | 43,496 | 12,516 | 6,876 |
| Fence | 376 | 216 | 120 |
| Bridge | 2,188 | 780 | 420 |

The LODs are authored alternatives: roof course counts, plank counts, small chamfers, pins and trim are reduced by family. Doorway, floor and bridge route dimensions are retained. This is not a blanket voxel size or a uniform decimation pass. Screen thresholds, transition appearance, runtime memory and performance must be assessed in Unreal; source triangle counts alone are not a performance result.

## Materials and texture use

The palette follows all four settlement references: terracotta, cream plaster, weathered timber, pale/olive stone and selective teal. The large roof silhouette is stepped; nearby detail comes from smaller physical courses, clipped tile corners, irregular tile heights, painted wear, joints and framed openings. Timber UVs align grain along each member.

Existing source artwork is reused as surfaces, not as object billboards:

| Material | Existing source | UV treatment |
| --- | --- | --- |
| Roof | `cottage_roof_tile_v6_candidate.png` | Select tile-region crops per modeled tile, approximately 170 texture pixels across a near-detail tile |
| Timber | `terrain_wood_3d.png` | Grain-region crops per member; longest physical face axis follows grain |
| Plaster | `cottage_plaster_v5.png` | 2 m repeat scale, approximately 627 pixels per metre |
| Stone | `terrain_cliff_face_v7.png` | Selected stone-surface crops per modeled block |
| Teal / iron / moss / brass | Recipe-derived flat colors | Values and roughness recorded in the manifest |

Base-color images use sRGB, linear filtering and normal mipmaps. No global pixelation effect is imposed. Timber and masonry crops are normalized per member rather than maintaining one uniform texture density across every face; long beams consequently have lower longitudinal texture density than short trim. This is an explicit remaining art consideration, not a claim that texture density is finalized for the eventual city library. Normal maps, authored roughness maps and complete interior furnishing are not supplied in this pilot.

## What was verified

`verification.json` records the packaged source and UV checks. `reopen-verification.json` records an independent normal-project reopen and all nine FBX round trips. Every imported test mesh matched its measured source dimensions, retained UVs and retained all eight material slots. All four textures match their original source bytes and are packed in the editable project.

The cottage route received 30 static point-support/vertical-clearance samples. Twenty-seven hit supported surfaces and had at least 1.8 m of clear vertical space above the sample. Three exact centerline points passed through the 7 mm modeled entrance-stone joints. These are visual joints rather than character-sized holes, but a character/capsule traversal test remains necessary. Fifteen samples at bridge plank centers verified the 0.32 m deck surface.

Front, rear, roof, entrance and lit-interior views were inspected. The focused revision corrected timber grain direction, exposed the cream front gable, added its upright, and closed/reoriented the thin roof underside shell. Exterior geometry and UVs were frozen before the final Unreal import. Source correctness, static sampled clearance, runtime movement, LOD transitions and visual approval remain separate claims.

## Reproduction

Run `Scripts/HomesteadPilot/Architecture/build.py` through the verified Terrarium Blender Lab MCP session. It creates a new dedicated scene and refuses to overwrite an existing pilot scene. It copies source textures only to the pilot folder, exports the nine FBXs and restores the prior active scene. `package_review.py` runs in a fresh background Blender, packages a normal project and renders the previews. `verify_reopen.py` independently reopens that file, checks UVs/textures/bounds and round-trips each FBX. `render_interior.py` produces the explicitly lit QA view without saving its temporary light.
