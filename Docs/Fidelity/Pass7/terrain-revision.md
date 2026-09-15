# Structural terrain revision after Pass 7 audit

The inspected `pass-7.png` still showed uninterrupted tall walls. The v8 terrain
therefore changes actual ground elevations and cliff cross-sections rather than
adding small decorations to the same wall.

## Implementation

Use `Scripts/Fidelity/terrain_v8.py`, retaining `build() -> cells`.

- 259 unprotected boundary cells are lowered to intermediate elevations around
  half of the original height difference. Adjacent upper cells become a recessed
  upper cliff, and the lowered row becomes a real horizontal rock shelf.
- 156 remaining exposed lip cells vary by up to 15 cm. Coherent spatial waves
  choose runs rather than alternating individual cells like battlements.
- 29 additional broad supported shelves extend 120–208 cm across, including 14
  riverbank shelves. Their tops are 30–47 percent of the parent drop above the
  lower ground. All extend to supporting ground or below the waterline.
- 356 taller exposed faces split into a broad lower stack and narrower upper
  stack. The base extends sideways and the upper stack overlaps it vertically.
  Width and split heights vary. The three existing CliffColumn_v5 variants are
  independently rotated; no new binary assets are required.
- Building, bridge and stair anchors, all path corridors, wheat and garden ground
  retain original support. A full footprint corner check keeps broad shelves
  away from protected paths and structures.

The result retains 5,841 grid cells and produces 7,200 placements including water.

## Runtime height integration

`build()` installs `height_at` as `reference.height`, retaining the original
function at `reference.fidelity_base_height`. Altered cells resolve to their new
height. Existing vegetation's ground resolver checks whether the old plate
height still exists, so it skips removed upper ground instead of placing plants
in the air. Repeated builds use the original saved height function, avoiding
cumulative erosion. New detail passes can sample `terrain_v8.height_at` directly.
The known path and building ground remains unchanged.

## Offline checks

Executed the actual module with only native placement stubbed. Assertions passed
for all protected grid cells retaining original heights, every lowered cell being
unprotected and below its previous surface, lip changes within 15 cm, broad shelf
widths within 100–220 cm, shelf tops above supporting bases, finite positive
placement transforms, exact new height lookup at every cell center, unchanged
landmark ground lookup, and deterministic repeated sampling.

No editor calls or binary changes were made by this agent. These checks establish
placement contracts and geometry intent. Rendered integration, collision and
visual fidelity acceptance remain pending root verification in Unreal.
