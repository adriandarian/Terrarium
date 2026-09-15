# Soft world: detail refinement

The user rejected the sharp voxel change and requested the softer original
treatment restored, then more detail on every object. HomesteadFidelity was
restored from HomesteadBeforeVoxelPass before any detail integration. No voxel
meshes or voxel materials remain referenced by the visible scene.

## Coverage

All 32 original visible project mesh types have detailed versions; this excludes
the editor's camera visualization mesh. `assets.json` lists every original,
replacement, concrete detail specification, and before/after triangle count.

- Meadow and path: overlapping low turf leaves, embedded pebbles and gravel,
  subtle soft pigment variation. Upright additions were removed from terrain
  tiles after visual review revealed dots and plants poking through paths.
- Cottage: slatted shutters, planted sill boxes, plaster repair details,
  stacked firewood, a stave barrel and surface wear.
- Shed, well and lantern: barrels, trough boards and water, hinge pins, open
  bucket, rope strands, pane mullions and post collars.
- Bridge and fences: rope lashings, embedded wood knots, grain, pegs, nails,
  board wear, split fibers and small rooted tufts.
- Gardens, wheat and traveler: soil clods, plant labels, young leaves, fallen
  straw, satchel strap, clothing fasteners, belt pouch and boot laces.
- Trees, shrubs, grasses, flowers, ferns and reeds: smaller overlapping leaf
  tips, bark ridges, berries, basal leaves, buds, growing fronds and leaf ribs.
- Cliffs, moss, stairs, outcrops and stones: lichen, mineral speckling, small
  moss colonies, worn tread surfaces and attached surface chips.
- All three water variants: additional short paired glints on the original
  continuous surface.

Crafted surfaces use a new matte material with subdued wood fibers, clay pigment
variation and mineral grain. The original camera, light, atmosphere and soft
edge treatment remain. Existing assets are retained alongside new versions.

## Validation and evidence

`verification.json` records all 32 replacements after saving and reopening,
unchanged instance transforms and counts, unchanged static landmark transforms,
material assignments, and zero saved normal errors for the replacement meshes.
The temporary close-up review camera was removed before final validation.

Native Unreal renders were visually inspected:

- `detailed-world.png`: original view, 962 x 1618.
- `village-closeup.png`: cottage, shed, garden, well, lantern, fences, traveler.
- `river-closeup.png`: bridge, cliff, shoreline, water and vegetation.
- `grass-closeup.png`: low turf, planted grass, flowers, shrubs and path.

Two editor processes had the same map open during the initial revert. The newer
duplicate was closed normally and the map was then saved successfully. During
implementation, a material output-pin error was corrected before integration.
Final checks pass; earlier error entries remain in the editor session log.

This validates native editor geometry, persistence, placement and reviewed
views. It does not claim packaged-game, collision, frame-time, or gameplay
testing, nor user acceptance of exact reference fidelity. The sum of mesh
triangles multiplied by all instances grows from 13,348,662 to 25,403,182;
this is an uncropped geometry inventory, not a measurement of rendered triangles
or runtime cost. Performance has not been profiled.

## Reproduction

Through the verified project-local Unreal MCP console: `restore_soft_world.py`,
`build_detail_assets.py`, `integrate_detail_assets.py`,
`refine_detail_ground.py`, `refine_detail_materials.py`, then
`verify_detail_world.py`. Capture with `capture_detail_world.py`.

The working map remains `/Game/Terrarium/Maps/HomesteadFidelity` and the soft
comparison remains `/Game/Terrarium/Maps/HomesteadBeforeVoxelPass`.
