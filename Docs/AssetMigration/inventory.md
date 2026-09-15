# Godot voxel asset inventory

Source: `C:/Users/hello/Projects/Pokemon/assets/voxel`

**155 files: 77 PNGs, 77 Godot `.import` sidecars, and 1 README.** PNGs total 121,848,107 bytes; all files total 121,936,882 bytes.

These are raster sprites, animation atlases, surface textures and composite references. No source mesh, rig, animation clip, or material-map bundle is present in this directory. Building a 3D model from a sprite is reconstruction; hidden surfaces require authored interpretation.

Godot main scene: `features/homestead_3d/homestead_adventure_3d.tscn`. The inventory follows literal `res://` dependencies from this scene and records all matching text references. `reachable_reference` means static dependency evidence, not a visible-in-game test. Candidate filenames may be used by the current game. Unreferenced files are retained history or references, not automatically rejected art.

## Counts

| Category | PNGs |
|---|---:|
| Buildings | 4 |
| Character animation atlases | 3 |
| Character references | 3 |
| Composite environment references | 3 |
| Contact shadow | 1 |
| Creature references | 3 |
| Items and UI icons | 8 |
| Terrain and building surfaces | 45 |
| Vegetation and props | 7 |

| Source usage evidence | PNGs |
|---|---:|
| candidate_unreferenced | 6 |
| reachable_reference | 41 |
| referenced_outside_main_dependency_graph | 4 |
| unreferenced_retained | 26 |

There are 8 candidate-named PNGs; 2 are reachable from the current main scene. The source README's final claim of 19 files / roughly 25 MB describes an earlier subset and is not the current inventory.

## Complete PNG list

Dimensions and full SHA-256 digests, every source usage with line numbers, and all candidate Unreal package mappings are in [inventory.json](inventory.json). Every PNG is listed below. Existing Unreal candidates are related model families only; none has been certified as an equivalent recreation by this inventory.

### Buildings

| File | Dimensions | Bytes | Source evidence | Existing Unreal family candidates |
|---|---:|---:|---|---|
| `civic_hall.png` | 1254 × 1254 | 1,688,958 | reachable_reference | Unmapped |
| `cottage.png` | 1254 × 1254 | 1,248,391 | reachable_reference | `SM_Cottage`, `SM_Cottage_Reference`, `SM_Cottage_Reference_v2` (+6 variants; JSON) |
| `lodge.png` | 1254 × 1254 | 1,388,815 | reachable_reference | `SM_Cottage`, `SM_Cottage_Reference`, `SM_Cottage_Reference_v2` (+6 variants; JSON) |
| `market_stall.png` | 1254 × 1254 | 1,365,612 | reachable_reference | Unmapped |

### Character animation atlases

| File | Dimensions | Bytes | Source evidence | Existing Unreal family candidates |
|---|---:|---:|---|---|
| `player_animation_atlas.png` | 1254 × 1254 | 1,673,802 | reachable_reference | `SM_Traveler`, `SM_Traveler_v2`, `SM_Traveler_v2_Detail` |
| `player_back_animation_atlas.png` | 1254 × 1254 | 1,464,219 | reachable_reference | `SM_Traveler`, `SM_Traveler_v2`, `SM_Traveler_v2_Detail` |
| `ranger_sela_animation_atlas.png` | 1254 × 1254 | 1,533,392 | reachable_reference | Unmapped |

### Character references

| File | Dimensions | Bytes | Source evidence | Existing Unreal family candidates |
|---|---:|---:|---|---|
| `player_back.png` | 1254 × 1254 | 1,242,208 | reachable_reference | `SM_Traveler`, `SM_Traveler_v2`, `SM_Traveler_v2_Detail` |
| `player_front.png` | 1254 × 1254 | 1,403,727 | reachable_reference | `SM_Traveler`, `SM_Traveler_v2`, `SM_Traveler_v2_Detail` |
| `ranger_sela.png` | 1198 × 1313 | 1,236,040 | reachable_reference | Unmapped |

### Composite environment references

| File | Dimensions | Bytes | Source evidence | Existing Unreal family candidates |
|---|---:|---:|---|---|
| `homestead_compound.png` | 1340 × 1174 | 1,496,669 | reachable_reference | `SM_Cottage`, `SM_Cottage_Reference`, `SM_Cottage_Reference_v2` (+18 variants; JSON) |
| `homestead_riverbank_v2.png` | 1402 × 1122 | 1,294,817 | unreferenced_retained | `SM_Reeds`, `SM_Reeds_Detail`, `SM_RiverStones_v1` (+11 variants; JSON) |
| `river_crossing.png` | 972 × 1619 | 1,296,043 | reachable_reference | `SM_PlankBridge`, `SM_PlankBridge_v2`, `SM_PlankBridge_v3` (+11 variants; JSON) |

### Contact shadow

| File | Dimensions | Bytes | Source evidence | Existing Unreal family candidates |
|---|---:|---:|---|---|
| `lodge_contact_shadow_v3.png` | 1254 × 1254 | 952,325 | referenced_outside_main_dependency_graph | Unmapped |

### Creature references

| File | Dimensions | Bytes | Source evidence | Existing Unreal family candidates |
|---|---:|---:|---|---|
| `brambit.png` | 1254 × 1254 | 1,294,543 | reachable_reference | Unmapped |
| `kindlehorn.png` | 1254 × 1254 | 1,467,573 | reachable_reference | Unmapped |
| `rillip.png` | 1254 × 1254 | 1,325,502 | reachable_reference | Unmapped |

### Items and UI icons

| File | Dimensions | Bytes | Source evidence | Existing Unreal family candidates |
|---|---:|---:|---|---|
| `deep_delver_mark.png` | 1254 × 1254 | 1,527,824 | reachable_reference | Unmapped |
| `ember.png` | 1254 × 1254 | 1,256,910 | reachable_reference | Unmapped |
| `ember_crest.png` | 1254 × 1254 | 1,692,285 | reachable_reference | Unmapped |
| `grove.png` | 1254 × 1254 | 1,273,581 | reachable_reference | Unmapped |
| `moss_tonic.png` | 1254 × 1254 | 1,334,606 | reachable_reference | Unmapped |
| `storm.png` | 1254 × 1254 | 1,176,335 | reachable_reference | Unmapped |
| `tide.png` | 1254 × 1254 | 1,200,736 | reachable_reference | Unmapped |
| `trail_prism.png` | 1254 × 1254 | 1,290,810 | reachable_reference | Unmapped |

### Terrain and building surfaces

| File | Dimensions | Bytes | Source evidence | Existing Unreal family candidates |
|---|---:|---:|---|---|
| `cottage_plaster_v5.png` | 1254 × 1254 | 2,853,974 | reachable_reference | `SM_Cottage`, `SM_Cottage_Reference`, `SM_Cottage_Reference_v2` (+6 variants; JSON) |
| `cottage_roof_tile_v5.png` | 1254 × 1254 | 1,561,426 | reachable_reference | `SM_Cottage`, `SM_Cottage_Reference`, `SM_Cottage_Reference_v2` (+6 variants; JSON) |
| `cottage_roof_tile_v6_candidate.png` | 1254 × 1254 | 1,722,239 | candidate_unreferenced | `SM_Cottage`, `SM_Cottage_Reference`, `SM_Cottage_Reference_v2` (+6 variants; JSON) |
| `terrain_cliff_3d.png` | 1254 × 1254 | 1,646,804 | reachable_reference | `SM_CliffColumn_v2`, `SM_CliffColumn_v3`, `SM_CliffColumn_v4` (+18 variants; JSON) |
| `terrain_cliff_face_v2.png` | 1254 × 1254 | 2,194,615 | referenced_outside_main_dependency_graph | `SM_CliffColumn_v2`, `SM_CliffColumn_v3`, `SM_CliffColumn_v4` (+18 variants; JSON) |
| `terrain_cliff_face_v4.png` | 1254 × 1254 | 1,302,119 | unreferenced_retained | `SM_CliffColumn_v2`, `SM_CliffColumn_v3`, `SM_CliffColumn_v4` (+18 variants; JSON) |
| `terrain_cliff_face_v5.png` | 1254 × 1254 | 1,499,355 | unreferenced_retained | `SM_CliffColumn_v2`, `SM_CliffColumn_v3`, `SM_CliffColumn_v4` (+18 variants; JSON) |
| `terrain_cliff_face_v6.png` | 1254 × 1254 | 1,480,761 | unreferenced_retained | `SM_CliffColumn_v2`, `SM_CliffColumn_v3`, `SM_CliffColumn_v4` (+18 variants; JSON) |
| `terrain_cliff_face_v7.png` | 1254 × 1254 | 1,723,422 | reachable_reference | `SM_CliffColumn_v2`, `SM_CliffColumn_v3`, `SM_CliffColumn_v4` (+18 variants; JSON) |
| `terrain_cliff_face_v8_candidate.png` | 1254 × 1254 | 1,547,509 | candidate_unreferenced | `SM_CliffColumn_v2`, `SM_CliffColumn_v3`, `SM_CliffColumn_v4` (+18 variants; JSON) |
| `terrain_cliff_face_v9_candidate.png` | 1254 × 1254 | 1,902,694 | candidate_unreferenced | `SM_CliffColumn_v2`, `SM_CliffColumn_v3`, `SM_CliffColumn_v4` (+18 variants; JSON) |
| `terrain_foliage_v4.png` | 1254 × 1254 | 1,247,927 | unreferenced_retained | `SM_Bush`, `SM_Bush_v2`, `SM_Bush_v2_Detail` (+5 variants; JSON) |
| `terrain_foliage_v5.png` | 1254 × 1254 | 1,583,319 | unreferenced_retained | `SM_Bush`, `SM_Bush_v2`, `SM_Bush_v2_Detail` (+5 variants; JSON) |
| `terrain_foliage_v6.png` | 1254 × 1254 | 1,488,051 | reachable_reference | `SM_Bush`, `SM_Bush_v2`, `SM_Bush_v2_Detail` (+5 variants; JSON) |
| `terrain_foliage_v7_candidate.png` | 1254 × 1254 | 1,257,382 | candidate_unreferenced | `SM_Bush`, `SM_Bush_v2`, `SM_Bush_v2_Detail` (+5 variants; JSON) |
| `terrain_grass.png` | 1254 × 1254 | 2,017,242 | reachable_reference | `SM_GrassTile`, `SM_MeadowTile_Edge_v6`, `SM_MeadowTile_Edge_v6_Detail` (+7 variants; JSON) |
| `terrain_grass_3d.png` | 1254 × 1254 | 1,746,453 | unreferenced_retained | `SM_GrassTile`, `SM_MeadowTile_Edge_v6`, `SM_MeadowTile_Edge_v6_Detail` (+7 variants; JSON) |
| `terrain_grass_top_v2.png` | 1254 × 1254 | 1,836,199 | unreferenced_retained | `SM_GrassTile`, `SM_MeadowTile_Edge_v6`, `SM_MeadowTile_Edge_v6_Detail` (+7 variants; JSON) |
| `terrain_grass_top_v3.png` | 1254 × 1254 | 1,873,312 | referenced_outside_main_dependency_graph | `SM_GrassTile`, `SM_MeadowTile_Edge_v6`, `SM_MeadowTile_Edge_v6_Detail` (+7 variants; JSON) |
| `terrain_grass_top_v4.png` | 1254 × 1254 | 1,790,670 | unreferenced_retained | `SM_GrassTile`, `SM_MeadowTile_Edge_v6`, `SM_MeadowTile_Edge_v6_Detail` (+7 variants; JSON) |
| `terrain_grass_top_v5.png` | 1254 × 1254 | 1,381,244 | unreferenced_retained | `SM_GrassTile`, `SM_MeadowTile_Edge_v6`, `SM_MeadowTile_Edge_v6_Detail` (+7 variants; JSON) |
| `terrain_grass_top_v6.png` | 1254 × 1254 | 1,737,241 | unreferenced_retained | `SM_GrassTile`, `SM_MeadowTile_Edge_v6`, `SM_MeadowTile_Edge_v6_Detail` (+7 variants; JSON) |
| `terrain_grass_top_v7.png` | 1254 × 1254 | 2,463,277 | unreferenced_retained | `SM_GrassTile`, `SM_MeadowTile_Edge_v6`, `SM_MeadowTile_Edge_v6_Detail` (+7 variants; JSON) |
| `terrain_grass_top_v8.png` | 1254 × 1254 | 2,168,048 | unreferenced_retained | `SM_GrassTile`, `SM_MeadowTile_Edge_v6`, `SM_MeadowTile_Edge_v6_Detail` (+7 variants; JSON) |
| `terrain_grass_top_v9.png` | 1254 × 1254 | 1,655,404 | reachable_reference | `SM_GrassTile`, `SM_MeadowTile_Edge_v6`, `SM_MeadowTile_Edge_v6_Detail` (+7 variants; JSON) |
| `terrain_moss_cap_v1.png` | 1254 × 1254 | 1,950,844 | reachable_reference | `SM_CliffMoss_v1`, `SM_CliffMoss_v1_Detail` |
| `terrain_stair_paver_v1.png` | 1254 × 1254 | 1,120,243 | unreferenced_retained | `SM_StoneStairs`, `SM_StoneStairs_v2`, `SM_StoneStairs_v3` (+1 variants; JSON) |
| `terrain_stair_paver_v2_candidate.png` | 1254 × 1254 | 1,292,115 | reachable_reference | `SM_StoneStairs`, `SM_StoneStairs_v2`, `SM_StoneStairs_v3` (+1 variants; JSON) |
| `terrain_trail_3d.png` | 1254 × 1254 | 2,116,432 | unreferenced_retained | `SM_PathTile`, `SM_PathTile_v2`, `SM_PathTile_v3` (+2 variants; JSON) |
| `terrain_trail_top_v10_candidate.png` | 1254 × 1254 | 2,904,915 | reachable_reference | `SM_PathTile`, `SM_PathTile_v2`, `SM_PathTile_v3` (+2 variants; JSON) |
| `terrain_trail_top_v11_candidate.png` | 1254 × 1254 | 2,567,312 | candidate_unreferenced | `SM_PathTile`, `SM_PathTile_v2`, `SM_PathTile_v3` (+2 variants; JSON) |
| `terrain_trail_top_v5.png` | 1254 × 1254 | 2,355,326 | unreferenced_retained | `SM_PathTile`, `SM_PathTile_v2`, `SM_PathTile_v3` (+2 variants; JSON) |
| `terrain_trail_top_v6.png` | 1254 × 1254 | 2,273,145 | unreferenced_retained | `SM_PathTile`, `SM_PathTile_v2`, `SM_PathTile_v3` (+2 variants; JSON) |
| `terrain_trail_top_v7.png` | 1254 × 1254 | 2,060,381 | unreferenced_retained | `SM_PathTile`, `SM_PathTile_v2`, `SM_PathTile_v3` (+2 variants; JSON) |
| `terrain_trail_top_v8.png` | 1254 × 1254 | 1,994,885 | unreferenced_retained | `SM_PathTile`, `SM_PathTile_v2`, `SM_PathTile_v3` (+2 variants; JSON) |
| `terrain_trail_top_v9_candidate.png` | 1254 × 1254 | 2,192,679 | candidate_unreferenced | `SM_PathTile`, `SM_PathTile_v2`, `SM_PathTile_v3` (+2 variants; JSON) |
| `terrain_water.png` | 1254 × 1254 | 1,895,641 | referenced_outside_main_dependency_graph | `SM_WaterDeep_v4`, `SM_WaterDeep_v4_Detail`, `SM_WaterShallow_v4` (+6 variants; JSON) |
| `terrain_water_3d.png` | 1254 × 1254 | 1,642,089 | unreferenced_retained | `SM_WaterDeep_v4`, `SM_WaterDeep_v4_Detail`, `SM_WaterShallow_v4` (+6 variants; JSON) |
| `terrain_water_v4.png` | 1254 × 1254 | 1,082,877 | unreferenced_retained | `SM_WaterDeep_v4`, `SM_WaterDeep_v4_Detail`, `SM_WaterShallow_v4` (+6 variants; JSON) |
| `terrain_water_v5.png` | 1254 × 1254 | 1,029,815 | unreferenced_retained | `SM_WaterDeep_v4`, `SM_WaterDeep_v4_Detail`, `SM_WaterShallow_v4` (+6 variants; JSON) |
| `terrain_water_v6.png` | 1254 × 1254 | 1,480,000 | unreferenced_retained | `SM_WaterDeep_v4`, `SM_WaterDeep_v4_Detail`, `SM_WaterShallow_v4` (+6 variants; JSON) |
| `terrain_water_v7.png` | 1254 × 1254 | 1,009,006 | unreferenced_retained | `SM_WaterDeep_v4`, `SM_WaterDeep_v4_Detail`, `SM_WaterShallow_v4` (+6 variants; JSON) |
| `terrain_water_v8.png` | 1254 × 1254 | 1,197,481 | unreferenced_retained | `SM_WaterDeep_v4`, `SM_WaterDeep_v4_Detail`, `SM_WaterShallow_v4` (+6 variants; JSON) |
| `terrain_water_v9.png` | 1254 × 1254 | 948,432 | reachable_reference | `SM_WaterDeep_v4`, `SM_WaterDeep_v4_Detail`, `SM_WaterShallow_v4` (+6 variants; JSON) |
| `terrain_wood_3d.png` | 1254 × 1254 | 1,228,148 | reachable_reference | `SM_FencePost`, `SM_FencePost_Detail`, `SM_FencePost_Reference` (+7 variants; JSON) |

### Vegetation and props

| File | Dimensions | Bytes | Source evidence | Existing Unreal family candidates |
|---|---:|---:|---|---|
| `homestead_tree_v2.png` | 1254 × 1254 | 1,295,254 | unreferenced_retained | `SM_Bush`, `SM_Bush_v2`, `SM_Bush_v2_Detail` (+5 variants; JSON) |
| `lantern.png` | 1133 × 1388 | 1,224,824 | reachable_reference | `SM_LanternPost`, `SM_LanternPost_Detail` |
| `meadow_shrub.png` | 1254 × 1254 | 1,230,737 | reachable_reference | `SM_Bush`, `SM_Bush_v2`, `SM_Bush_v2_Detail` (+2 variants; JSON) |
| `rock.png` | 1315 × 1197 | 1,389,594 | reachable_reference | `SM_RiverStones_v1`, `SM_RiverStones_v2`, `SM_RiverStones_v2_Detail` (+6 variants; JSON) |
| `sign.png` | 1254 × 1254 | 1,183,618 | reachable_reference | Unmapped |
| `tree.png` | 1254 × 1254 | 1,657,280 | reachable_reference | `SM_Bush`, `SM_Bush_v2`, `SM_Bush_v2_Detail` (+5 variants; JSON) |
| `wheat_field.png` | 1536 × 1024 | 1,718,624 | reachable_reference | `SM_WheatPatch`, `SM_WheatPatch_v2`, `SM_WheatPatch_v2_Detail` |

## Mapping gaps and source handling

- 60 PNGs have related existing mesh-family candidates; 17 have none. These counts cover individual image revisions, not unique subjects.
- Existing traveler meshes are static authored characters and do not establish equivalence with the coral-jacket player or ranger. Sprite atlases do not provide skeletons or animation clips.
- Surface images are generally lit color artwork, not authored normal, roughness, metallic, AO or height maps. Do not treat painted shadows as physically meaningful height. Review tiling, scale, color space and alpha per intended material.
- Chroma-key backgrounds and the lodge contact-shadow sprite require special treatment. The README describes magenta removal in Godot; rebuilding full geometry should use actual contact and lighting rather than adding a rectangular sprite foundation.
- Composite homestead and river images must map to compositions of reusable meshes, not be counted as a single completed mesh.
- This inventory establishes no editor-verified equivalent migration. Existing semantic candidates require source-by-source visual comparison; missing categories need new models or UI imports.

## Other files

| File | Kind | Bytes |
|---|---|---:|
| `brambit.png.import` | godot_import_metadata | 938 |
| `civic_hall.png.import` | godot_import_metadata | 947 |
| `cottage.png.import` | godot_import_metadata | 938 |
| `cottage_plaster_v5.png.import` | godot_import_metadata | 971 |
| `cottage_roof_tile_v5.png.import` | godot_import_metadata | 976 |
| `cottage_roof_tile_v6_candidate.png.import` | godot_import_metadata | 1,007 |
| `deep_delver_mark.png.import` | godot_import_metadata | 967 |
| `ember.png.import` | godot_import_metadata | 933 |
| `ember_crest.png.import` | godot_import_metadata | 952 |
| `grove.png.import` | godot_import_metadata | 934 |
| `homestead_compound.png.import` | godot_import_metadata | 971 |
| `homestead_riverbank_v2.png.import` | godot_import_metadata | 983 |
| `homestead_tree_v2.png.import` | godot_import_metadata | 967 |
| `kindlehorn.png.import` | godot_import_metadata | 948 |
| `lantern.png.import` | godot_import_metadata | 939 |
| `lodge.png.import` | godot_import_metadata | 933 |
| `lodge_contact_shadow_v3.png.import` | godot_import_metadata | 986 |
| `market_stall.png.import` | godot_import_metadata | 953 |
| `meadow_shrub.png.import` | godot_import_metadata | 953 |
| `moss_tonic.png.import` | godot_import_metadata | 948 |
| `player_animation_atlas.png.import` | godot_import_metadata | 985 |
| `player_back.png.import` | godot_import_metadata | 952 |
| `player_back_animation_atlas.png.import` | godot_import_metadata | 999 |
| `player_front.png.import` | godot_import_metadata | 955 |
| `ranger_sela.png.import` | godot_import_metadata | 951 |
| `ranger_sela_animation_atlas.png.import` | godot_import_metadata | 1,000 |
| `README.md` | documentation | 14,253 |
| `rillip.png.import` | godot_import_metadata | 937 |
| `river_crossing.png.import` | godot_import_metadata | 959 |
| `rock.png.import` | godot_import_metadata | 931 |
| `sign.png.import` | godot_import_metadata | 930 |
| `storm.png.import` | godot_import_metadata | 934 |
| `terrain_cliff_3d.png.import` | godot_import_metadata | 965 |
| `terrain_cliff_face_v2.png.import` | godot_import_metadata | 982 |
| `terrain_cliff_face_v4.png.import` | godot_import_metadata | 979 |
| `terrain_cliff_face_v5.png.import` | godot_import_metadata | 980 |
| `terrain_cliff_face_v6.png.import` | godot_import_metadata | 980 |
| `terrain_cliff_face_v7.png.import` | godot_import_metadata | 980 |
| `terrain_cliff_face_v8_candidate.png.import` | godot_import_metadata | 1,009 |
| `terrain_cliff_face_v9_candidate.png.import` | godot_import_metadata | 1,010 |
| `terrain_foliage_v4.png.import` | godot_import_metadata | 970 |
| `terrain_foliage_v5.png.import` | godot_import_metadata | 971 |
| `terrain_foliage_v6.png.import` | godot_import_metadata | 971 |
| `terrain_foliage_v7_candidate.png.import` | godot_import_metadata | 1,001 |
| `terrain_grass.png.import` | godot_import_metadata | 959 |
| `terrain_grass_3d.png.import` | godot_import_metadata | 965 |
| `terrain_grass_top_v2.png.import` | godot_import_metadata | 980 |
| `terrain_grass_top_v3.png.import` | godot_import_metadata | 980 |
| `terrain_grass_top_v4.png.import` | godot_import_metadata | 977 |
| `terrain_grass_top_v5.png.import` | godot_import_metadata | 976 |
| `terrain_grass_top_v6.png.import` | godot_import_metadata | 977 |
| `terrain_grass_top_v7.png.import` | godot_import_metadata | 977 |
| `terrain_grass_top_v8.png.import` | godot_import_metadata | 977 |
| `terrain_grass_top_v9.png.import` | godot_import_metadata | 976 |
| `terrain_moss_cap_v1.png.import` | godot_import_metadata | 974 |
| `terrain_stair_paver_v1.png.import` | godot_import_metadata | 983 |
| `terrain_stair_paver_v2_candidate.png.import` | godot_import_metadata | 1,013 |
| `terrain_trail_3d.png.import` | godot_import_metadata | 964 |
| `terrain_trail_top_v10_candidate.png.import` | godot_import_metadata | 1,010 |
| `terrain_trail_top_v11_candidate.png.import` | godot_import_metadata | 1,010 |
| `terrain_trail_top_v5.png.import` | godot_import_metadata | 977 |
| `terrain_trail_top_v6.png.import` | godot_import_metadata | 977 |
| `terrain_trail_top_v7.png.import` | godot_import_metadata | 977 |
| `terrain_trail_top_v8.png.import` | godot_import_metadata | 977 |
| `terrain_trail_top_v9_candidate.png.import` | godot_import_metadata | 1,007 |
| `terrain_water.png.import` | godot_import_metadata | 959 |
| `terrain_water_3d.png.import` | godot_import_metadata | 964 |
| `terrain_water_v4.png.import` | godot_import_metadata | 964 |
| `terrain_water_v5.png.import` | godot_import_metadata | 965 |
| `terrain_water_v6.png.import` | godot_import_metadata | 964 |
| `terrain_water_v7.png.import` | godot_import_metadata | 964 |
| `terrain_water_v8.png.import` | godot_import_metadata | 965 |
| `terrain_water_v9.png.import` | godot_import_metadata | 965 |
| `terrain_wood_3d.png.import` | godot_import_metadata | 961 |
| `tide.png.import` | godot_import_metadata | 931 |
| `trail_prism.png.import` | godot_import_metadata | 952 |
| `tree.png.import` | godot_import_metadata | 930 |
| `wheat_field.png.import` | godot_import_metadata | 950 |

## Existing Unreal maps

- `Content/Terrarium/Maps/AssetWorkshop.umap`
- `Content/Terrarium/Maps/BeforeAssetMigration.umap`
- `Content/Terrarium/Maps/Homestead.umap`
- `Content/Terrarium/Maps/HomesteadBeforeHouseFence.umap`
- `Content/Terrarium/Maps/HomesteadBeforePass6.umap`
- `Content/Terrarium/Maps/HomesteadBeforePass7.umap`
- `Content/Terrarium/Maps/HomesteadBeforeVoxelPass.umap`
- `Content/Terrarium/Maps/HomesteadFidelity.umap`
- `Content/Terrarium/Maps/HomesteadFidelityPass4.umap`
- `Content/Terrarium/Maps/ModularGallery.umap`
- `Content/Terrarium/Maps/RenderBaseline.umap`

Map presence is verified from files only; it does not prove current editor contents, navigation, collision, or source-asset coverage.

## Reproduce

Run `python Scripts/Migration/inventory.py` from Terrarium. The script uses only the Python standard library, reads the Godot project without modifying it, and replaces this Markdown and JSON inventory. PNG dimensions are validated from the PNG signature and IHDR header; full raster decoding and rendered visual review are separate checks.
