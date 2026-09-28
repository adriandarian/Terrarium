# Landscape pilot candidates

These new sources follow the four settlement references: mossy stone terraces, earthy paths, broad layered tree crowns and concentrated planting. They preserve the existing landscape sources and belong to the playable homestead pilot, not the earlier flat-color scale study.

The authoring script creates eight reusable assets in metres with Z up and a base-center origin. The cliff is nominally 4 × 4 × 2 m, with small edge irregularities. A separate lightweight 1 × 1 × 3.2 m cliff column fits the existing boundary module footprint. The broad tree is roughly 5 m high. The stair is 2 m wide, rises 2 m over twelve 0.167 m risers, and uses 0.30 m treads. The runtime pass must choose suitable collision proxies and verify traversal.

Stone courses vary between approximately 0.18–0.27 m vertically and 0.24–0.48 m horizontally. Leaf surface steps are approximately 0.115 m on the tree, 0.065 m on the shrub and 0.045 m on crops. These are material-specific construction choices, not a global voxel size. The canopy builder emits only exposed cell faces; it does not export hidden internal voxel faces. Chamfered stones retain closed separate pieces for editable surface character.

Authored surface maps carry restrained mineral staining, bark grain and small foliage color variation at a consistent 512 texels per metre. They repeat at one metre using ordinary linear texture filtering. Geometry defines the stepped outline, while textures carry finer marks. This does not impose a global screen pixelation filter.

`source-preflight.json` records pure geometry checks before Blender execution. Final per-asset manifests and previews are written only after export, preview rendering and packaging the isolated scene as an independently openable Blender project. The combined manifest follows the shared pilot schema. Source LOD0 is delivered here; runtime LOD, collision, traversal and Unreal appearance remain separate integration checks. Technical file validity does not establish visual acceptance.

## Delivered and inspected

All eight original candidates have an editable, independently openable `.blend`, FBX, authored textures, manifest and rendered preview. The original manifest and exports were frozen while Unreal imported them. A separate `revised-manifest.json` replaces only the tree and stairs with `BroadTree5mV2` and `StoneStairs2mRiseV2` for final integration.

The V2 tree embeds bark accents in the actual tapered trunk and resolves ten diagonal voxel edge contacts. The V2 stair lowers the hidden step core beneath its stone caps, eliminating coplanar black tread faces. Their new previews were inspected and both saved sources independently reopened with zero boundary or nonmanifold edges, positive signed volume, UVs and packed textures. Receipts are `reopen-validation.json` and `v2-reopen-validation.json`; the original tree's ten nonmanifold contacts remain honestly recorded in its superseded receipt.

| Effective candidate | Triangles | Dimensions / intended use |
| --- | ---: | --- |
| MossCliff4m | 23,276 | Approximately 4.04 × 4.04 × 2.01 m; standalone secondary terrace section |
| FineCliffColumn1m | 4,080 | Approximately 1.01 × 1.01 × 3.21 m; existing cliff boundary replacement |
| BroadTree5mV2 | 11,584 | Approximately 3.68 × 3.91 × 4.99 m; broad canopy with finer exterior steps |
| ShrubGroundcover | 3,284 | Approximately 1.70 × 1.62 × 0.85 m |
| WornPath2m | 616 | Approximately 2 × 2 m; flat earthy path tile with small edge stones |
| StoneStairs2mRiseV2 | 4,532 | 2 m width, 3.6 m run, 2 m structural rise |
| WheatPatch2m | 32,444 | 2 × 2 m, approximately 0.92 m high; source geometry is intentionally dense and needs runtime distance treatment |
| GardenPatch2m | 7,700 | 2 × 2 m, 0.27 m high; compact planted bed |

All final effective source meshes have zero nonmanifold edges in reopen checks. Materials retain muted olive, tan and warm earth textures. The individual Blender studios vary in apparent brightness with asset framing; judge palette cohesion in the shared Unreal lighting, not by treating the separate preview exposures as a color match. Tree silhouette remains a broad dense crown and cliff courses remain comparatively regular: both are art candidates requiring whole-scene review, not a fidelity guarantee.
