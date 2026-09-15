# Independent reconstruction completeness audit

Audit snapshot: **2026-09-12T21:37:25.673586+00:00**. Read-only inspection of source PNGs, recipe files, build receipts, package files and catalog selection. No Unreal editor or MCP calls were made. Only this audit document was written.

**Source preservation and geometry coverage pass at this snapshot. Visual acceptance is not established by this audit.** All 77 source PNGs are accounted for by 72 distinct reconstruction targets; 45 of those targets are surface relief tiles.

## Evidence summary

| Check | Result |
|---|---|
| Original and copied PNG filename sets | Exact match: 77 each, no missing or extra PNGs |
| Original versus copied PNG SHA-256 | All 77 byte-identical |
| Fresh catalog source hashes | All 77 match independently calculated hashes |
| Build receipts / distinct module+key identities | 105 receipts / 72 keys |
| Expected source associations versus receipts | All 72 keys present, no unmapped or extra key |
| Latest revision policy | Independent numeric maximum per module+key agrees with fresh catalog selection for all 72 |
| Latest package files on disk | 72 of 72 present |
| Latest receipt saved-normal errors | 0 for every selected mesh |
| Latest receipt recipe hashes | All 72 equal current defining module bytes |
| Surface dataset | 45 entries, exact match to the 45 expected source stems |
| Exact selected revision front/back captures | 6 front / 5 back at snapshot |

## Scope and aliases

| Module | Distinct targets | Selected revisions |
|---|---:|---|
| architecture | 6 | R3: 6 |
| compound | 1 | R1: 1 |
| creatures_items | 11 | R2: 11 |
| environment | 7 | R2: 7 |
| humanoids | 2 | R3: 2 |
| surfaces | 45 | R1: 45 |

The five shared associations account for the difference between 77 sources and 72 targets:

- `player_back.png`, `player_animation_atlas.png` and `player_back_animation_atlas.png` share `humanoids/player_front` with `player_front.png`.
- `ranger_sela_animation_atlas.png` shares `humanoids/ranger_sela` with `ranger_sela.png`.
- `lodge_contact_shadow_v3.png` shares `architecture/lodge` as legacy grounding/shadow context; it is not presented as a separate volumetric object.

These are explicit source associations, not evidence that sprite atlas motion was converted to skeletal animation. All 45 terrain/plaster/roof source versions, including candidate revisions, remain separate surface targets. Surface relief is authored geometry carrying source color; it is not a recovered normal/roughness/ORM material set.

## Catalog freshness

The on-disk `asset-map.json` inspected here was generated at 2026-09-12T21:21:01.064994+00:00. It reported 40 completed targets and 32 pending targets. **57 selected records were stale** relative to the latest receipts at this snapshot. The generator was called in read-only collect mode for the fresh comparison; no catalog files were changed by this audit.

Root should regenerate the catalog after the final builds/captures. The generator correctly chooses the highest numeric revision and requires exact selected mesh-name front/back filenames; older pictures do not silently substitute for newer revisions. The pending capture count is a timestamped observation of an ongoing capture batch, not a claim that captures cannot or will not be completed.

## Latest module hash evidence

Each receipt hashes its defining Python module. Historical lower revision receipts can legitimately carry older hashes; the audit compares the selected latest revision. All selected latest module hashes match. These receipt hashes do not cover transitive helpers, material edits or external data, so they do not prove the complete dependency graph or final shader configuration.

| Module | Current SHA-256, also matched by every selected receipt for that module |
|---|---|
| `architecture.py` | `4e6a471e33bd9d670c3287cb8c70ea5ae454ab61a6cc4bc1739c986a15ead54b` |
| `compound.py` | `4329b15610001f50dceb2fe52d549144c1a74cf013a7b300310278e0ce18d804` |
| `creatures_items.py` | `1cb0c02ab75cb9ce924b48d6573d9da05b2a3fcb70d61bfcbd630b1282299ccc` |
| `environment.py` | `da46e6acfeb0ddfb851a20b448c26e9caf77081429930589f19429f2ad0edf8e` |
| `humanoids.py` | `988bfdc06b88a1d3502f79a6d5d12206461eb196514a9162a2292e56d5261b36` |
| `surfaces.py` | `660db6f77f2d9ef3f4f4cc74a55ae5d706ba9e02a6bc10cbe2eb6b712531d6da` |

Copied-source sorted filename/hash manifest SHA-256: `3b9b758bda420accd8f075ac4c7d98e46fa74616f5cec7ceb395eb495d75097b`. Each of the 77 individual hashes was checked against the original folder, not inferred from this aggregate.

## Complete selected target ledger

| Module / builder key | Selected mesh | Revision | Receipt |
|---|---|---:|---|
| `architecture/civic_hall` | `SM_Recon_CivicHall_R3` | 3 | [receipt](Builds/SM_Recon_CivicHall_R3.json) |
| `architecture/cottage` | `SM_Recon_Cottage_R3` | 3 | [receipt](Builds/SM_Recon_Cottage_R3.json) |
| `architecture/lantern` | `SM_Recon_Lantern_R3` | 3 | [receipt](Builds/SM_Recon_Lantern_R3.json) |
| `architecture/lodge` | `SM_Recon_Lodge_R3` | 3 | [receipt](Builds/SM_Recon_Lodge_R3.json) |
| `architecture/market_stall` | `SM_Recon_MarketStall_R3` | 3 | [receipt](Builds/SM_Recon_MarketStall_R3.json) |
| `architecture/sign` | `SM_Recon_Sign_R3` | 3 | [receipt](Builds/SM_Recon_Sign_R3.json) |
| `compound/homestead_compound` | `SM_Recon_HomesteadCompound` | 1 | [receipt](Builds/SM_Recon_HomesteadCompound.json) |
| `creatures_items/brambit` | `SM_Recon_Brambit_R2` | 2 | [receipt](Builds/SM_Recon_Brambit_R2.json) |
| `creatures_items/deep_delver_mark` | `SM_Recon_DeepDelverMark_R2` | 2 | [receipt](Builds/SM_Recon_DeepDelverMark_R2.json) |
| `creatures_items/ember` | `SM_Recon_Ember_R2` | 2 | [receipt](Builds/SM_Recon_Ember_R2.json) |
| `creatures_items/ember_crest` | `SM_Recon_EmberCrest_R2` | 2 | [receipt](Builds/SM_Recon_EmberCrest_R2.json) |
| `creatures_items/grove` | `SM_Recon_Grove_R2` | 2 | [receipt](Builds/SM_Recon_Grove_R2.json) |
| `creatures_items/kindlehorn` | `SM_Recon_Kindlehorn_R2` | 2 | [receipt](Builds/SM_Recon_Kindlehorn_R2.json) |
| `creatures_items/moss_tonic` | `SM_Recon_MossTonic_R2` | 2 | [receipt](Builds/SM_Recon_MossTonic_R2.json) |
| `creatures_items/rillip` | `SM_Recon_Rillip_R2` | 2 | [receipt](Builds/SM_Recon_Rillip_R2.json) |
| `creatures_items/storm` | `SM_Recon_Storm_R2` | 2 | [receipt](Builds/SM_Recon_Storm_R2.json) |
| `creatures_items/tide` | `SM_Recon_Tide_R2` | 2 | [receipt](Builds/SM_Recon_Tide_R2.json) |
| `creatures_items/trail_prism` | `SM_Recon_TrailPrism_R2` | 2 | [receipt](Builds/SM_Recon_TrailPrism_R2.json) |
| `environment/homestead_riverbank_v2` | `SM_Recon_Riverbank_R2` | 2 | [receipt](Builds/SM_Recon_Riverbank_R2.json) |
| `environment/homestead_tree_v2` | `SM_Recon_HomesteadTree_R2` | 2 | [receipt](Builds/SM_Recon_HomesteadTree_R2.json) |
| `environment/meadow_shrub` | `SM_Recon_MeadowShrub_R2` | 2 | [receipt](Builds/SM_Recon_MeadowShrub_R2.json) |
| `environment/river_crossing` | `SM_Recon_RiverCrossing_R2` | 2 | [receipt](Builds/SM_Recon_RiverCrossing_R2.json) |
| `environment/rock` | `SM_Recon_MossRock_R2` | 2 | [receipt](Builds/SM_Recon_MossRock_R2.json) |
| `environment/tree` | `SM_Recon_AncientTree_R2` | 2 | [receipt](Builds/SM_Recon_AncientTree_R2.json) |
| `environment/wheat_field` | `SM_Recon_WheatField_R2` | 2 | [receipt](Builds/SM_Recon_WheatField_R2.json) |
| `humanoids/player_front` | `SM_Recon_Player_R3` | 3 | [receipt](Builds/SM_Recon_Player_R3.json) |
| `humanoids/ranger_sela` | `SM_Recon_RangerSela_R3` | 3 | [receipt](Builds/SM_Recon_RangerSela_R3.json) |
| `surfaces/cottage_plaster_v5` | `SM_Recon_cottage_plaster_v5` | 1 | [receipt](Builds/SM_Recon_cottage_plaster_v5.json) |
| `surfaces/cottage_roof_tile_v5` | `SM_Recon_cottage_roof_tile_v5` | 1 | [receipt](Builds/SM_Recon_cottage_roof_tile_v5.json) |
| `surfaces/cottage_roof_tile_v6_candidate` | `SM_Recon_cottage_roof_tile_v6_candidate` | 1 | [receipt](Builds/SM_Recon_cottage_roof_tile_v6_candidate.json) |
| `surfaces/terrain_cliff_3d` | `SM_Recon_terrain_cliff_3d` | 1 | [receipt](Builds/SM_Recon_terrain_cliff_3d.json) |
| `surfaces/terrain_cliff_face_v2` | `SM_Recon_terrain_cliff_face_v2` | 1 | [receipt](Builds/SM_Recon_terrain_cliff_face_v2.json) |
| `surfaces/terrain_cliff_face_v4` | `SM_Recon_terrain_cliff_face_v4` | 1 | [receipt](Builds/SM_Recon_terrain_cliff_face_v4.json) |
| `surfaces/terrain_cliff_face_v5` | `SM_Recon_terrain_cliff_face_v5` | 1 | [receipt](Builds/SM_Recon_terrain_cliff_face_v5.json) |
| `surfaces/terrain_cliff_face_v6` | `SM_Recon_terrain_cliff_face_v6` | 1 | [receipt](Builds/SM_Recon_terrain_cliff_face_v6.json) |
| `surfaces/terrain_cliff_face_v7` | `SM_Recon_terrain_cliff_face_v7` | 1 | [receipt](Builds/SM_Recon_terrain_cliff_face_v7.json) |
| `surfaces/terrain_cliff_face_v8_candidate` | `SM_Recon_terrain_cliff_face_v8_candidate` | 1 | [receipt](Builds/SM_Recon_terrain_cliff_face_v8_candidate.json) |
| `surfaces/terrain_cliff_face_v9_candidate` | `SM_Recon_terrain_cliff_face_v9_candidate` | 1 | [receipt](Builds/SM_Recon_terrain_cliff_face_v9_candidate.json) |
| `surfaces/terrain_foliage_v4` | `SM_Recon_terrain_foliage_v4` | 1 | [receipt](Builds/SM_Recon_terrain_foliage_v4.json) |
| `surfaces/terrain_foliage_v5` | `SM_Recon_terrain_foliage_v5` | 1 | [receipt](Builds/SM_Recon_terrain_foliage_v5.json) |
| `surfaces/terrain_foliage_v6` | `SM_Recon_terrain_foliage_v6` | 1 | [receipt](Builds/SM_Recon_terrain_foliage_v6.json) |
| `surfaces/terrain_foliage_v7_candidate` | `SM_Recon_terrain_foliage_v7_candidate` | 1 | [receipt](Builds/SM_Recon_terrain_foliage_v7_candidate.json) |
| `surfaces/terrain_grass` | `SM_Recon_terrain_grass` | 1 | [receipt](Builds/SM_Recon_terrain_grass.json) |
| `surfaces/terrain_grass_3d` | `SM_Recon_terrain_grass_3d` | 1 | [receipt](Builds/SM_Recon_terrain_grass_3d.json) |
| `surfaces/terrain_grass_top_v2` | `SM_Recon_terrain_grass_top_v2` | 1 | [receipt](Builds/SM_Recon_terrain_grass_top_v2.json) |
| `surfaces/terrain_grass_top_v3` | `SM_Recon_terrain_grass_top_v3` | 1 | [receipt](Builds/SM_Recon_terrain_grass_top_v3.json) |
| `surfaces/terrain_grass_top_v4` | `SM_Recon_terrain_grass_top_v4` | 1 | [receipt](Builds/SM_Recon_terrain_grass_top_v4.json) |
| `surfaces/terrain_grass_top_v5` | `SM_Recon_terrain_grass_top_v5` | 1 | [receipt](Builds/SM_Recon_terrain_grass_top_v5.json) |
| `surfaces/terrain_grass_top_v6` | `SM_Recon_terrain_grass_top_v6` | 1 | [receipt](Builds/SM_Recon_terrain_grass_top_v6.json) |
| `surfaces/terrain_grass_top_v7` | `SM_Recon_terrain_grass_top_v7` | 1 | [receipt](Builds/SM_Recon_terrain_grass_top_v7.json) |
| `surfaces/terrain_grass_top_v8` | `SM_Recon_terrain_grass_top_v8` | 1 | [receipt](Builds/SM_Recon_terrain_grass_top_v8.json) |
| `surfaces/terrain_grass_top_v9` | `SM_Recon_terrain_grass_top_v9` | 1 | [receipt](Builds/SM_Recon_terrain_grass_top_v9.json) |
| `surfaces/terrain_moss_cap_v1` | `SM_Recon_terrain_moss_cap_v1` | 1 | [receipt](Builds/SM_Recon_terrain_moss_cap_v1.json) |
| `surfaces/terrain_stair_paver_v1` | `SM_Recon_terrain_stair_paver_v1` | 1 | [receipt](Builds/SM_Recon_terrain_stair_paver_v1.json) |
| `surfaces/terrain_stair_paver_v2_candidate` | `SM_Recon_terrain_stair_paver_v2_candidate` | 1 | [receipt](Builds/SM_Recon_terrain_stair_paver_v2_candidate.json) |
| `surfaces/terrain_trail_3d` | `SM_Recon_terrain_trail_3d` | 1 | [receipt](Builds/SM_Recon_terrain_trail_3d.json) |
| `surfaces/terrain_trail_top_v10_candidate` | `SM_Recon_terrain_trail_top_v10_candidate` | 1 | [receipt](Builds/SM_Recon_terrain_trail_top_v10_candidate.json) |
| `surfaces/terrain_trail_top_v11_candidate` | `SM_Recon_terrain_trail_top_v11_candidate` | 1 | [receipt](Builds/SM_Recon_terrain_trail_top_v11_candidate.json) |
| `surfaces/terrain_trail_top_v5` | `SM_Recon_terrain_trail_top_v5` | 1 | [receipt](Builds/SM_Recon_terrain_trail_top_v5.json) |
| `surfaces/terrain_trail_top_v6` | `SM_Recon_terrain_trail_top_v6` | 1 | [receipt](Builds/SM_Recon_terrain_trail_top_v6.json) |
| `surfaces/terrain_trail_top_v7` | `SM_Recon_terrain_trail_top_v7` | 1 | [receipt](Builds/SM_Recon_terrain_trail_top_v7.json) |
| `surfaces/terrain_trail_top_v8` | `SM_Recon_terrain_trail_top_v8` | 1 | [receipt](Builds/SM_Recon_terrain_trail_top_v8.json) |
| `surfaces/terrain_trail_top_v9_candidate` | `SM_Recon_terrain_trail_top_v9_candidate` | 1 | [receipt](Builds/SM_Recon_terrain_trail_top_v9_candidate.json) |
| `surfaces/terrain_water` | `SM_Recon_terrain_water` | 1 | [receipt](Builds/SM_Recon_terrain_water.json) |
| `surfaces/terrain_water_3d` | `SM_Recon_terrain_water_3d` | 1 | [receipt](Builds/SM_Recon_terrain_water_3d.json) |
| `surfaces/terrain_water_v4` | `SM_Recon_terrain_water_v4` | 1 | [receipt](Builds/SM_Recon_terrain_water_v4.json) |
| `surfaces/terrain_water_v5` | `SM_Recon_terrain_water_v5` | 1 | [receipt](Builds/SM_Recon_terrain_water_v5.json) |
| `surfaces/terrain_water_v6` | `SM_Recon_terrain_water_v6` | 1 | [receipt](Builds/SM_Recon_terrain_water_v6.json) |
| `surfaces/terrain_water_v7` | `SM_Recon_terrain_water_v7` | 1 | [receipt](Builds/SM_Recon_terrain_water_v7.json) |
| `surfaces/terrain_water_v8` | `SM_Recon_terrain_water_v8` | 1 | [receipt](Builds/SM_Recon_terrain_water_v8.json) |
| `surfaces/terrain_water_v9` | `SM_Recon_terrain_water_v9` | 1 | [receipt](Builds/SM_Recon_terrain_water_v9.json) |
| `surfaces/terrain_wood_3d` | `SM_Recon_terrain_wood_3d` | 1 | [receipt](Builds/SM_Recon_terrain_wood_3d.json) |

## Verification boundary

Final main-agent verification after this independent audit is recorded in [verification.json](verification.json) and [visual-review.md](visual-review.md): all 72 current models have front/back Lit captures, and all five galleries were saved and reopened with current bindings. This audit remains an existence and coverage check; the separate visual review records the remaining differences from the source art.

The receipts report completed editor saves and zero saved-normal errors, and the corresponding binary package files exist. This read-only audit did not independently open those packages in Unreal or visually approve the meshes. Source fidelity, final Lit front/back comparisons, collision, rigs, animation, optimization and gameplay integration require their own evidence. Earlier humanoid passes were explicitly rejected and refined through R3; this audit selects R3 but does not grant it acceptance based on existence.
