# Voxel asset migration — historical prototypes

The current models are in the [72-model reconstruction catalog](../Reconstruction/catalog.html), with the [current asset map](../Reconstruction/asset-map.json) and [visual review](../Reconstruction/visual-review.md). The records below preserve the earlier migration pass.

[Open the searchable visual catalog](catalog.html) · [Every source file](inventory.md) · [Source-to-Unreal asset map](asset-map.json) · [Editor validation](verification.json)

The Godot folder contains **77 PNGs, 77 `.import` sidecars and one README**. The PNGs are images rather than recoverable meshes or rigs. All 77 original PNGs have verified byte-for-byte project-local copies in `SourceAssets/Voxel`, imported Unreal textures, and reference material instances. The source README is preserved as `SourceAssets/Voxel/PROVENANCE.md`. No paid generation provider was used.

Three subagents performed inventory/mapping, architectural modeling, and character/creature modeling. Their source-guided recipes produced **12 new static prototypes**, totaling **94,040 triangles**, under `/Game/Terrarium/Migration/Meshes`. These are original geometry reconstructions from the rendered artwork; hidden sides and physical scale are interpretations. Existing environmental meshes were reused in their own gallery.

## Saved Unreal maps

All five maps live under `/Game/Terrarium/Migration/Maps`.

| Map | Contents | Verified entries |
|---|---|---:|
| Architecture | Lodge, civic hall, market stall, sign, hanging lantern | 5 |
| Characters | Brambit, Kindlehorn, Rillip, player, Ranger Sela, Moss Tonic, Trail Prism | 7 |
| Environment | Existing cottage, vegetation, wheat, bridge, rocks, meadow, path, cliff, stairs, water, moss, plants, garden, well and reeds | 16 |
| References | Every original PNG, including historical candidates, UI icons, atlases and composite environment references | 77 |
| Surfaces | Terrain/building source-color material studies | 45 |

The reference boards preserve original proportions and backgrounds. The HTML catalog is the most convenient way to search filenames and inspect original artwork. Existing counterpart mappings are semantic candidates and should not be read as exact visual equivalence. `homestead_compound`, `homestead_riverbank_v2`, and `river_crossing` remain composition references; they are not three newly rebuilt gameplay worlds.

## New meshes and visual checks

The engine's normal asset thumbnails show mostly rear views. Separate front images were rendered with Unreal SceneCapture2D **BaseColor**, then reviewed against source identifiers. These diagnostic images establish visible geometry and pigment, not final Lit appearance. Gallery `*-layout.png` files use the same BaseColor mode.

| Mesh | Triangles | Front diagnostic | Lit asset thumbnail |
|---|---:|---|---|
| SM_Migration_Lodge | 22,236 | [Front](Models/SM_Migration_Lodge-front.png) | [Thumbnail](Models/SM_Migration_Lodge.png) |
| SM_Migration_CivicHall | 45,560 | [Front](Models/SM_Migration_CivicHall-front.png) | [Thumbnail](Models/SM_Migration_CivicHall.png) |
| SM_Migration_MarketStall | 10,560 | [Front](Models/SM_Migration_MarketStall-front.png) | [Thumbnail](Models/SM_Migration_MarketStall.png) |
| SM_Migration_Sign | 1,364 | [Front](Models/SM_Migration_Sign-front.png) | [Thumbnail](Models/SM_Migration_Sign.png) |
| SM_Migration_Lantern | 1,672 | [Front](Models/SM_Migration_Lantern-front.png) | [Thumbnail](Models/SM_Migration_Lantern.png) |
| SM_Brambit | 1,716 | [Front](Models/SM_Brambit-front.png) | [Thumbnail](Models/SM_Brambit.png) |
| SM_Kindlehorn | 1,640 | [Front](Models/SM_Kindlehorn-front.png) | [Thumbnail](Models/SM_Kindlehorn.png) |
| SM_Rillip | 1,672 | [Front](Models/SM_Rillip-front.png) | [Thumbnail](Models/SM_Rillip.png) |
| SM_PlayerExplorer | 3,080 | [Front](Models/SM_PlayerExplorer-front.png) | [Thumbnail](Models/SM_PlayerExplorer.png) |
| SM_RangerSela | 2,904 | [Front](Models/SM_RangerSela-front.png) | [Thumbnail](Models/SM_RangerSela.png) |
| SM_MossTonic | 792 | [Front](Models/SM_MossTonic-front.png) | [Thumbnail](Models/SM_MossTonic.png) |
| SM_TrailPrism | 844 | [Front](Models/SM_TrailPrism-front.png) | [Thumbnail](Models/SM_TrailPrism.png) |


Review confirmed the lodge's dormer/windows/entry, civic clock/belfry/bell, striped market canopy and produce, sign and hanging lantern structure. Creature faces, Ranger Sela's silver hair/scarf/satchel, the player's clothing and backpack, and both item silhouettes are present. These are visibly simpler than the source art: creature contours, clothing/hair, weathering, brick relief and side-wall detail need refinement.

## Validation and remaining production work

- Verified all 77 copied PNG hashes and all imported Texture2D assets; checked every reference/surface instance points to the correct texture and parent, with sRGB color enabled.
- All 12 models passed component closure, positive-volume, outward-winding and actual saved-mesh normal checks; saved-normal errors are zero. Model pivots were checked at ground level in the galleries.
- Reopened every gallery and checked exact mesh/material paths for all expected entries. No transient capture actors are saved in these maps.
- All surface studies use source color plus a scalar roughness value. They are **not authored PBR map sets**. The source images contain painted lighting; no normal/ORM/height maps, texture-atlas unwrap or production lightmap UVs were created. Meshes use the existing vertex-color material workflow.
- Characters are static: no skeletons, skin weights, locomotion, atlas conversion or gameplay collision. Buildings have no interiors. Lantern, tonic and prism are opaque prototypes without final glass/emission. LODs, optimization, packaging and gameplay were not tested.
- UI symbols, badges, atlases and the lodge contact-shadow image remain references. Magenta backgrounds were preserved; no production UI masking was added.

Final Lit art acceptance is still pending. The source catalog and editor structure are complete; this is a reviewable modeling foundation, not a claim that every original image has become a finished game-ready 3D asset.

## Preservation and repeatability

The initial open editor state was preserved in `/Game/Terrarium/Maps/BeforeAssetMigration`. Homestead world work belongs to a separate active task; migration content stays in its own namespace. An early map-copy/save issue was corrected by explicitly loading the copied map before edits, and the baseline was restored from the untouched bootstrap copy. Unreliable viewport captures were discarded; successful native thumbnails and BaseColor captures are retained. The editor was released to the courtyard task after final validation.

Source and build scripts are in `Scripts/Migration`. `prepare_sources.py` and `inventory.py` run locally; import, model, gallery and verification scripts run inside the verified Terrarium editor through `Scripts/run_editor.py`. Builds preserve existing named assets, and completed gallery builds refuse replacement. Engine caches remain ignored. No commit or PR was created.
# Current reconstruction library

The models below are the historical migration prototypes. Use the [current source/model catalog](../Reconstruction/catalog.html), [current asset map](../Reconstruction/asset-map.json), and [reconstruction review](../Reconstruction/visual-review.md) for the 72-model library covering all 77 original images.
