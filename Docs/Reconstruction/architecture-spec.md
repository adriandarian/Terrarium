# Architecture reconstruction, source comparison specification

`Scripts/Reconstruction/architecture.py` returns six unsaved `meshkit.Mesh`
objects through `BUILDERS`. The coordinating process owns Unreal baking and
validation. Names are unique `SM_Recon_*` assets; no migration asset is overwritten.
All six local PNG references were visually reviewed again before this rewrite.

| Source | Asset | Geometry bounds size, cm (X/Y/Z) | Triangles |
| --- | --- | --- | ---: |
| lodge.png | SM_Recon_Lodge | 593 / 456 / 640.5 | 64,432 |
| cottage.png | SM_Recon_Cottage | 558.7 / 429.5 / 552.5 | 59,108 |
| civic_hall.png | SM_Recon_CivicHall | 1023 / 560.5 / 1121 | 150,672 |
| market_stall.png | SM_Recon_MarketStall | 570.875 / 401.5 / 314.4 | 40,744 |
| lantern.png | SM_Recon_Lantern | 170.15 / 89.3 / 316.5 | 10,516 |
| sign.png | SM_Recon_Sign | 175 / 82.375 / 232.78 | 3,784 |

Front is negative Y. Final meshes reflect authored X once to match the source
image handedness in the shared front comparison camera; the final arrow extends
toward negative X. Every reflected triangle reverses winding and every component
center reflects with its vertices. World dimensions are inferred from the
single images; the source contains no metric survey or hidden-side reference.

## Source-specific shape requirements

**Lodge.** Tall, compact timber/plaster structure with broad terracotta courses,
a raised centered dormer bearing one teal window, two lower teal windows, a
central plank door with square gold latch, and a masonry chimney toward the
left roof end. Corner moss must climb against a tight stone footing rather than
sit on a generic pedestal. New mesh has narrower depth than the rejected model,
seven roof courses, independently divided roof tiles, clay end-face courses,
individual plaster and stone courses, recessed window panes, deep timber sills,
three stone entry steps and planted broken footing corners.

**Cottage.** A separate lower building. Its front roof has a broad low gable with
cream infill and an exposed central timber, without a dormer window. The facade
has the same family of teal crossbar windows and a planked door, but a shorter
wall and roof profile. This recipe is independently assembled with a six-course
main roof, five-course forward gable, stone chimney and distinct dimensions.

**Civic hall.** Broad two-storey facade with four narrow window bays per storey,
a centered projecting front gable and a narrow stepped stone entrance arch.
The clock tower rises through the roof, with teal/dark clock surround, vertical
hands, four masonry belfry piers surrounding an open chamber, a flared gold bell,
and a four-tier clay cap. The tower and facade are masonry-coursed on all sides.
Paired wall lanterns, timber floor bands, corbels and two low planted entrance
stones carry source details. Overall width was enlarged relative to the rejected
prototype to better reflect the broad source silhouette.

**Market stall.** Seven alternating teal and cream stripes across a shallow
sloped awning, divided into individual small surface blocks. The front apron has
short centered drops. Four substantial timber posts and knee braces support it.
Two plank counters frame a center opening; each has stacked produce, slatted
crates and open bins. A stoppered blue bottle, teal cloth, and framed hanging shop
token preserve the visible asymmetry. The floor and tight footing use individual
planks and stone blocks; moss wraps the corners.

**Lantern.** A timber post and diagonal brace hold a substantial hanging lamp
beside the post. Alternating chain links have empty centers. The lamp has a
three-tier iron cap, corner cage bars, and amber-to-cream block gradients on all
four pane faces. Its base is an irregular stepped stone-and-moss mound rather
than a stack of uniform slabs. Bands have front/back and side bolts.

**Sign.** Thick arrow with a three-plank blank recessed face, jointed golden
border, stepped arrowhead and substantial post. Iron bands, bolt heads, visible
post end grain and top-band moss reproduce the source motifs. Its footing uses
irregular stones and attached moss blocks, not a uniform plinth.

## Continuity and validation boundaries

House side and rear elevations are authored interpretations, with framed inset
windows, wall courses, continuous timber floor bands and corner posts. No broad
blank side-wall planes remain. Roof ends also receive visible clay courses.
The buildings remain static exterior meshes; no gameplay interior, opening doors
or optimized LODs are claimed. Source-style bevels are geometric, so the meshes
contain numerous closed overlapping components and hidden internal faces.

Offline construction passed for every builder. `meshkit` checked each component
for closed edge incidence, outward triangulation and positive volume. Placement
groups update both vertices and component centers. The civic hall's width
adjustment also scales component volume; final ground normalization updates
centers. All six have exact minimum Z = 0. Reported dimensions/counts above were
measured from generated geometry, not guessed metadata.

The existing vertex palette material and UV workflow remain subject to the root
baker. There is no dedicated unwrapped texture atlas or lightmap channel in this
module. Amber pane colors are not themselves an emissive material. Offline
geometry success is not source-fidelity acceptance: real Lit front/side renders,
consistent camera comparisons and any resulting revisions remain required.

## Revision after the first Lit comparison

All twelve front/back saved Lit architecture captures were inspected against the
source PNGs. They exposed excessive plaster joints, too-short roof tile lengths,
buried chimneys and open lodge dormer cheeks. The second geometry revision uses
approximately 60 cm clay tile lengths, larger nearly seamless ivory panels,
closed dormer sides, and chimney stacks moved onto the visible roof slope with
32 cm additional masonry height. The latter exposes roughly four to five stone
courses rather than just raising a buried cap. Sign border lengths are longer
and its post cap has concentric end-grain color rings. Lantern pane color cells
overlap slightly to eliminate the dark lattice that appeared in Lit rendering.

The shared helper API remains compatible with `compound.py`; its independent
homestead builder was rebuilt offline successfully after these revisions
(80,816 triangles). Updated architecture counts and bounds appear above. The
second bake and corrected-camera Lit comparison are the coordinator's next step;
these edits are not a visual acceptance claim.

## Revision after the corrected-camera Lit comparison

The corrected comparison exposed a consistent source-handedness mismatch. The
final builder now reflects X across all six architectural meshes and the compound,
with explicit triangle-winding reversal and component-center updates. A separate
offline traversal verified every transformed triangle still faces outward against
its own component center, in addition to the construction checks.

The market token bracket now extends from its front upright past the canopy edge
to keep the token visible outside the front-right silhouette after reflection.
The lantern has a three-tier individually jointed stone footing, approximately
20 percent broader/taller than the sparse previous mound, with moss bands around
the upper post contact. Sign footing moss now climbs around the stump and spills
over the outer stone faces. The gallery script was not changed. Third-bake Lit
comparison remains pending; no source-match acceptance is asserted here.
