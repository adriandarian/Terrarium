# Source-led architecture and prop recipes

The five PNG concepts were visually inspected before modeling: `lodge.png`,
`civic_hall.png`, `market_stall.png`, `sign.png`, and `lantern.png`. New recipes
live in `Scripts/Migration/structures.py`; they create unique assets under
`/Game/Terrarium/Migration/Meshes` and do not replace the earlier cottage or
lantern assets. All use centimeters, a ground-level pivot, and front negative Y.

| Source | New asset | Features preserved |
| --- | --- | --- |
| lodge.png | SM_Migration_Lodge | Clay block roof, central dormer, stone chimney, cream timber walls, teal crossbar windows, wooden door, stone steps, moss |
| civic_hall.png | SM_Migration_CivicHall | Wide two-storey hall, paired window bays, central clock tower, open belfry and gold bell, pyramidal cap, stepped entry arch |
| market_stall.png | SM_Migration_MarketStall | Teal and cream striped canopy, four posts, two produce counters around an opening, open bins, bottle, hanging shop token |
| sign.png | SM_Migration_Sign | Blank recessed timber arrow pointing right, iron post bands, bolts, weathered mossy stone footing |
| lantern.png | SM_Migration_Lantern | Side-hanging bracket lantern, diagonal brace, square chain links, iron frame, stepped cap, amber panes and stone footing |

These are static geometric reconstructions from single rendered references.
Hidden sides, depths and world scale are inferred. Architecture has no usable
interior; doors, clock hands and bell are static. Produce is simplified block
geometry. The lantern's golden panes are colored opaque geometry and do not emit
light. Magenta PNG backgrounds and painted shadows are not modeled as geometry.

The existing `meshkit` creates closed convex components, checks winding and
positive volume, saves through Geometry Script, checks the static-mesh round
trip, and assigns its vertex-color palette material. UV0 is meshkit's XY planar
projection: it is sufficient for the vertex-color workflow but is not an
unwrapped texture atlas or a dedicated lightmap UV channel. Collision remains
disabled as in the existing pipeline. These limitations need a later production
pass before gameplay collision, baked lighting or texture painting.

`BUILDERS` allows pure geometry validation without editor mutation. `build_all()`
saves sequentially, restores the prior meshkit root, and skips existing names
on rerun. Editor baking and visual review are the coordinating agent's steps;
recipe creation alone does not prove editor acceptance.

Pure geometry validation passed for all five recipes: every component is closed,
outward-facing and has positive volume, and every asset has minimum Z exactly 0.
Triangle counts are lodge 22,236; civic hall 45,560; market stall 10,560; sign
1,364; lantern 1,672. Counts reflect individually beveled voxel components and
include hidden/intersecting internal faces; no optimization or LOD pass is claimed.
