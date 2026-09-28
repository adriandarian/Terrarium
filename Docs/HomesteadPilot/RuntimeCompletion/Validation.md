# Runtime completion evidence

## Executed editor checks

The coordinator verified the connected Unreal editor is Terrarium, opened the
StartingHome working map, and executed the read-only collision inventory. The
before-integration receipt is preserved at `../Completion/collision-before.json`.
It found 8,521 query/physics-enabled instances and 15,157,950 visual triangle-
instances across their selected collision LODs. This broad proxy includes meshes
whose default collision policy does not imply per-triangle simple collision; it
is not a physics budget or measured cost. The updated audit separates the known
complex-as-simple subtotal on subsequent runs.

The first post-integration inventory reads 52 distinct meshes and 589 static-mesh
components. All pilot components have forced LOD zero. There are 8,513 query-and-
physics instances and 2,124 NoCollision instances. The broad visual-triangle proxy
is 14,865,132 for enabled instances, while the known complex-as-simple subtotal is
12,258,412. Recomputing that same definite subtotal from the preserved before
receipt gives 11,876,134: it increased by 382,278 as collision policies changed,
including the compound becoming complex-as-simple. The lower broad proxy is not
evidence of a physics optimization. The 2,076 approved cliff columns contribute
8,470,080, about 69.1% of the final definite subtotal. Instanced geometry is shared;
these multiplied counts are not cooked data size or memory consumption. This
intermediate inventory is preserved as
`collision-post-import-before-policy-restoration.json`.

That audit exposed unintended art collision changes: BlueShed, Tower, Lantern,
Sign and HomesteadCompound gained complex-as-simple flags; Tide, Ember and Storm
lost them; all eight market collectibles changed from BlockAll/query-and-physics
to NoCollision. These were import-policy changes, not required LOD changes.
`art-collision-policy-diff.json` records every affected actor and exact prior/new
setting. The coordinator ran `restore_art_collision.py`, which restored all 17
private art placements to inherited body flags and component policies, and
verified every source package hash unchanged. The saved map was reopened and the
inventory rerun. Its final values are 8,521 query/physics instances, 2,116
NoCollision instances, broad triangle exposure 15,157,947 and definite
complex-as-simple exposure 11,876,131. Both triangle totals differ from the original
baseline by only three triangles, attributable to Storm's actual imported LOD0
changing from 8,794 to 8,791. The inherited collision restoration is verified; this
is not a collision-performance optimization. `art-collision-restoration.json`
records exact body/component before and after fields for every placement.
The art importer was subsequently made baseline-aware, and its actual-editor
verifier passed all 17 families after the repair. Future imports preserve source
body settings and the existing component profile/enabled/overlap state rather
than reapplying the original family-based policy.

The cottage approach/retreat sweep completed without an error and recorded 206
camera samples. All 42 pilot components stayed in automatic mode, and the prior
viewport camera and background-throttle preference were restored. Five actual
1280 x 720 PNGs and the unchanged original receipt are preserved in `Cottage/`.
The coordinator inspected near, middle and return-near images: the closed cottage
roof, structure and surrounding grass were intact. The runtime worker also
inspected the near image and confirmed the open doorway and complete visible roof.

This sweep demonstrates automatic component settings with a moving camera and
sampled output. It did not query the actual rendered LOD index or visually inspect
every intermediate frame. Continuous transition smoothness remains unverified.
The first cottage sweep predates the added global `r.ForceLOD` and
`foliage.ForceLOD` guard; later sweeps also record those CVars and require -1.

The final `FinalBuildings/automatic-lod-sweep.json` covers the cottage, Lodge,
CivicHall and HomesteadCompound in 64 seconds, with 543 samples and 20 actual
capture files. All 535 pilot components remained automatic. `r.ForceLOD` and
`foliage.ForceLOD` were both -1; static-mesh LOD distance scale and view-distance
scale were both 1. The camera and background throttle were restored. The
coordinator inspected the four near views, Lodge's middle view and CivicHall's
return-near view: visible structures were intact. Nearby terrain/vegetation partly
occludes the compound in its capture. This is sampled automatic-LOD visual
evidence, and does not upgrade continuous smoothness or every authored family to
a complete visual acceptance pass.

## Final traversal and collision query timing

After restoring collision and reopening the saved map, the coordinator reran the
walking harness. `../Completion/traversal-receipt.json` reports all three routes
passed: cottage enter/exit, terrace stairs up/down, and both bridge spans with the
return trip. The possessed Character used AddMovementInput with actual gravity
and collision, and only each route's initial position was teleported. This checks
traversal; it is not physical keyboard evidence.

The separate query benchmark completed without error. After two warmup batches,
it measured 11 batches and 484 Visibility traces for each mode. Mean synchronous
latency was 33.48 microseconds per simple query and 35.18 microseconds per complex
query. The p95 batch-average latencies were 40.95 and 38.64 microseconds,
respectively. Each mode returned 440 hit results out of 484 queries. These are
repeatable route-checkpoint vertical probes, including Python vector construction
and Python-to-engine call overhead. They are not total collision-frame cost,
CharacterMovement timing, or a game-thread/GPU profile, and no before/after speedup
is claimed. The benchmark ran separately from the idle frame sample.

## Input boundary

Physical held-key movement remains unverified. The available Slate PressKey tool
sends an immediate down/up pair, and the documented computer-use API does not
provide a separate key-down/up or hold duration. No synthetic movement has been
relabeled physical input. The new passive observer is ready for a future actual
held-key test and separately records OS key state, controller key state, walking
mode, position and control rotation. Even matching OS/controller key states cannot
distinguish a hardware keyboard from software-generated OS events.

## Final idle gameplay profile

The unobscured final `idle-observation.json` completed without error: 1,800 samples
over 30 seconds after 5 seconds of warmup, at a 1,526 x 910 editor viewport. Mean
world-frame delta was **16.67 ms**, median **16.66 ms**, p95 **16.91 ms**, and maximum
**54.98 ms**. The maximum records an actual slow frame; this is not a guarantee of
continuous 60 fps. The possessed explorer remained at `[650, -150, 657.15]` cm,
facing yaw 180 degrees, throughout the sample. No OS or controller WASD activity
was observed. The recorder injected no motion and restored background throttling.

Asset imports, automatic-LOD capture sweeps, traversal, query benchmarking and
background Blender exports had finished. The existing interactive Blender MCP
window remained open, with no background Blender process. The editor Message Log
popup was closed before the final run and no captures occurred during measurement.
An earlier run with that popup visible is preserved separately as
`idle-message-log-visible.json` and excluded from the final gameplay result.

These deltas include the editor and recorder overhead. They do not separate game
thread, rendering thread or GPU time, or predict a packaged game's performance.
The earlier 23.58 ms gameplay mean had concurrent Blender rendering and is not a
controlled before/after comparison. No causal optimization, city-scale budget or
continuous-transition smoothness claim follows from this stationary homestead
sample. All five source scripts also pass local Python AST parsing; actual editor
receipts, rather than that parsing, establish the runtime results above.
