# Homestead pilot runtime

These scripts are editor-authoring and validation tools for the separate StartingHome map. Root runs them sequentially through the verified Terrarium Unreal MCP connection. They never modify a binary asset directly on disk.

## Run order

The original component-only foliage integration requires `Scripts/HomesteadPilot/persist_pilot_foliage.py` before final acceptance. It creates pilot-owned FoliageTypes and preserves current converted instance transforms unchanged; the completed migration receipt verifies all 2,748 instances after reopening. Do not re-run the original scale conversion on these instances.

`fix_play_view.py` disables the inherited concept camera's automatic Player0 activation on StartingHome. After starting PIE, `inspect_play_view.py` must report `view_target_is_pawn: true`. The default PlayerStart is now [650, -150, 672], clear of the old reference-player mesh; `verify_fresh_spawn.py` verifies a new default PIE session for three seconds without moving or teleporting the pawn. Traversal and performance measurements now reject a camera override.

1. `probe_runtime.py` records the actual editor's reflected APIs. The initial probe confirmed the native ArchVisCharacter class is loaded.
2. Set `runtime-config.json` spawn and selected baseline collision meshes from the assembled world. `prepare_baseline_collision.py` duplicates only those retained meshes into the pilot before changing their collision; baseline source assets remain untouched.
3. `setup_explorer.py` creates BP_HomesteadExplorer and BP_HomesteadGameMode and sets the game mode only on StartingHome. It adds six uniquely named input mappings in the editor. Then run `persist_input_config.py` with ordinary Python: observed `SaveKeyMappings()` did not update project DefaultInput.ini, so this writes only the six additive axis lines and preserves other settings. Press Play, focus the viewport, use WASD to walk and mouse to look. Shift+F1 releases the mouse; Escape ends Play.
4. After importing new meshes, `configure_meshes.py` builds `mesh-plan.json` from the import receipt if no plan exists. Review it before a later reconfiguration: the persisted plan is authoritative. Custom LOD FBXs are preferred; otherwise Unreal's mesh reduction creates LOD1/2. It writes actual Unreal triangle counts and actual screen thresholds. Nanite is disabled only on these pilot meshes so the three conventional LODs can be checked directly.

   Optional `configure-only.json` limits rebuilding to its listed asset paths and writes a partial receipt. It currently targets the revised tree and stairs. Remove this filter for a full rebuild. `finalize_meshes.py` validates the complete existing mesh plan and applies component collision without rebuilding; use it after a filtered rebuild to produce the full receipt.
5. Add `test_routes` to the runtime config and run `validate_traversal.py`, then start PIE. Each route has `name`, `start_cm` and `waypoints_cm`, all measured at capsule center (floor elevation + 90 cm, plus normal Character floor separation). Optional `xy_tolerance_cm`, `z_tolerance_cm` and `segment_timeout_s` control acceptance. It positions the pawn only at a route's start, then drives CharacterMovement with collision/gravity through every waypoint. It verifies arrival elevation and walking mode. This is real gameplay movement, but it does not prove keyboard input.
6. In a separate PIE run, execute `record_manual_control.py` and walk with WASD during its 30-second window. It records real PlayerController key state alongside actual pawn displacement; it never injects movement. If no key input is observed, keyboard control remains unverified.

7. `set_lod_review.py` selects actual pilot component LODs for fixed-camera screenshot comparisons. Restore automatic LOD0 selection (`lod_review_forced: 0`), save and reopen the map, then run `verify_saved_runtime.py` to confirm saved pawn defaults, project input lines, actual LOD triangle counts and thresholds, materials, collision flags and automatic LOD settings.

## Evidence received so far

The root editor run passed the initial courtyard route in `initial-courtyard-traversal.json`: the possessed explorer reached two requested points with the expected heights and walking mode. Only seven frame samples were captured, near 333 ms each because the editor was background-throttled. That run validates initial collision traversal, not rendering performance. The initial setup receipt confirms the native character Blueprint compiled and the six live input mappings were installed; source DefaultInput.ini now contains the same six entries. The later final bridge, stair and doorway routes all passed; see Validation.md and traversal-receipt.json. Visual LOD and physical keyboard acceptance remain separate checks.

The full editor readback in `mesh-runtime-receipt.json` confirms all eleven new mesh assets have three strictly decreasing LOD triangle counts, explicit screen thresholds, Nanite disabled and material references present. Actual counts include cottage 43,496 / 12,516 / 6,876; fence 376 / 216 / 120; bridge 2,188 / 780 / 420; revised tree 11,584 / 8,688 / 5,792; and revised stairs 4,532 / 2,492 / 1,132. Architecture uses imported authored chains; landscape uses Unreal reduction. This confirms implemented distance representations, while their appearance and transitions still require visual inspection.

## Movement and collision

The player capsule is 180 cm tall and 68 cm wide, with a 165 cm eye height and 2.8 m/s walking speed. The initial 37 cm step allowance accommodates the existing 35 cm stairs with small clearance. New stairs should use smaller human-scale risers; the movement allowance is not a claim that 35 cm risers are final art or ergonomic design. Gravity is enabled; there is no flying/spectator substitution and no automatic jumping.

Static traversal meshes use LOD0 complex-as-simple triangle collision. This preserves doorway openings, bridge decks and individual stair surfaces; an enclosing box would seal the cottage doorway. It is suitable for static prototype geometry, not simulated moving bodies. This is a correctness-first pilot choice with collision cost to be measured before district-scale reuse. Water/flowers/ground cover should have NoCollision on their components. Baseline instances require pilot duplicates before a changed collision policy.

## LOD and performance evidence limits

Default test thresholds are screen fractions 1.0 / .30 / .10 for solid architecture and terrain, and 1.0 / .18 / .06 for thin fence/tree silhouettes. They are explicit starting values that require close/normal/far visual review in motion. An imported 3-LOD count does not prove silhouette continuity or material stability. Compare forced LOD0/1/2 captures at the same camera, then return the component's forced LOD to 0 (automatic) and approach/retreat through transitions. Component forced values 1/2/3 select actual LOD0/1/2.

Traversal receipts sample PIE world frame delta after settling and record the entire editor process's working-set and private bytes through Windows process counters. These are actual local measurements, but include editor overhead and do not isolate GPU time, draw-call cost, texture residency or a shipping build. Use Unreal `stat unit`, `stat RHI`, `stat scenerendering`, `memreport -full` or a CSV profiler capture for those extra measurements. Do not turn this single homestead measurement into a multi-city budget.

`measure_performance.py` provides a longer measurement: five seconds of PIE warmup followed by twenty seconds of frame and process-memory samples. It temporarily disables the editor's background CPU throttle and restores its prior value automatically without saving that setting. Keep the intended gameplay camera active and wait for shader compilation before starting. The earlier courtyard sample was throttled and cannot be used as a rendering budget.

All setup scripts write receipts only after successful readback/save checks. Reopen and recheck the map, pawn defaults, triangle counts and collision; inspect viewport motion and screenshots before claiming acceptance. Script syntax checks and source manifests alone are not gameplay or visual validation.

The latest eye-view performance sample and fresh-spawn evidence are summarized in `Validation.md`. The eye-view sample averaged 23.58 ms with p95 52.40 ms and maximum 117.17 ms; it is variable local PIE performance, not a 60 fps guarantee. The earlier concept-view sample is retained separately.
