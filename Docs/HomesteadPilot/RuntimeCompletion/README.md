# Runtime completion checks

These scripts are queued for the coordinator, the only Unreal editor operator.
They assert the Terrarium project and StartingHome map and write receipts here.
The four observation scripts do not rebuild assets, consume the old
`configure-only.json` filter, save the map, modify collision or force LODs. The
separate coordinator-only `restore_art_collision.py` restores inherited collision
policies on the newly imported private art copies and saves that focused repair.
Source parsing alone is not editor validation.

1. With PIE stopped, execute `audit_collision.py`. It reads actual components,
   instance counts, collision policies and imported LOD geometry. Its definite
   complex-as-simple subtotal is separate from visual triangle exposure on meshes
   with other collision policies. Neither number is a measured physics cost.
2. End camera piloting and set the level viewport to perspective/lit. Execute
   `sweep_automatic_lod.py`. The default request reviews the cottage for 24 seconds;
   `lod-sweep-request.json` may select exact actor labels after integration. It
   accepts an optional `output_tag` such as `RemainingBuildings` to preserve each
   run in its own child directory. The script verifies both global force-LOD CVars
   are disabled as well as every pilot component's automatic setting. It
   continuously retreats and approaches, requests five native screenshots per
   actor and restores the original viewport camera and background throttle. All
   pilot components must already have `forced_lod_model=0`. Readback verifies they
   remain zero. Check images exist and inspect them; screenshot requests alone do
   not prove images were saved. The receipt deliberately does not claim an actual
   rendered LOD index or visual smoothness.
3. Start a fresh default PIE session with the explorer as its actual view target.
   Execute `benchmark_collision_queries.py`. It waits 3 seconds then alternates
   24 bounded batches of simple/complex Visibility traces at route checkpoints.
   First two batches are warmup. This isolates a repeatable query microbenchmark,
   including Python/engine call overhead; it does not measure total physics cost.
4. After that benchmark has finished, use a separate fresh PIE and execute
   `observe_play.py` with request name `idle`. Leave it idle for 35 seconds: 5
   warmup and 30 recording. Record concurrent Blender/asset-import work accurately
   in `observation-request.json`. This measures actual gameplay-view frame deltas
   with editor overhead. Do not overlap it with captures, traces or imports.
5. A future real held-key run can set request name `input`, arm the same observer,
   focus the gameplay viewport, then hold W/A/S/D separately. The recorder samples
   both OS key-down states and the possessed controller. Sustained matching keys
   plus walking displacement are stronger evidence than injected AddMovementInput.
   Software-generated OS keys still cannot establish a physical hardware source;
   report the input provider separately. The available synchronous Slate PressKey
   and computer-use APIs do not support separate down/up, so they do not establish
   held-key acceptance. Do not relabel a synthetic or absent hold as physical.

Every tick harness is finite, unregisters its callback on completion/error, and
writes an explicit error field. `observe_play.py` and the sweep temporarily disable
background CPU throttling and restore the prior unsaved preference. Ending PIE
early creates a failed receipt rather than a partial success. Rerunning replaces a
previous active instance of the same harness.

## Collision conclusions before integration

The initial actual-editor inventory identifies the existing 2,076 pilot cliff
columns as 8,470,080 triangle-instances of complex-as-simple geometry exposure.
Lodge and CivicHall together are 951,804. Shared instanced collision geometry means
these figures are not cooked bytes, RAM, or linearly proportional runtime cost.
Changing visual LOD does not automatically change static collision LOD.

No collision geometry reduction is justified by those counts alone. Preserve LOD0
collision for approved cottage/bridge/stair walking surfaces. Reducing cliff or
building collision needs a dedicated contact/traversal comparison so simplified
geometry does not seal an opening, introduce invisible steps, or shift walkable
edges. Decorative meshes may use NoCollision when their authored role and scene
policy explicitly establish that they should never block gameplay.

## Validation status

All five scripts parse with Python AST locally. The coordinator executed the final
collision inventory after reopening, the inherited art collision restoration,
automatic cottage/building sweeps, three walking traversal routes, the independent
query benchmark, and an unobscured idle gameplay profile. See `Validation.md` for
actual results and receipt locations. Physical held-key input and continuous LOD
transition smoothness remain unverified; no shader/game-thread/GPU timing or
city-scale performance budget is inferred.
