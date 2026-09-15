# Environment reference discrepancy audit

Read-only visual inspection of the user reference `C:/Users/hello/.codex/attachments/1ccf9c86-0559-4bb2-8197-f3f4da9c0f7f/image-1.png`, `Docs/Environment/before.png`, and `Scripts/Fidelity/reference.py`. No editor calls or scene changes were made.

The reference is **481 × 809**; `before.png` is **962 × 1618**. All coordinates below use the **481 × 809 reference grid**: divide before-image coordinates by two. Visual readings are approximate, normally ±4 pixels; named recipe anchors are exact inputs and are not automatically visible silhouette extrema.

The broad composition is already close. The largest discrepancies are the oversized terrain blocks, the cottage's larger silhouette, vegetation granularity and river treatment. Preserve the established winding path, cottage area, player contact and bridge crossing while replacing geometry; correct scale/style before moving every anchor.

| Feature | Reference-grid evidence | Concrete correction |
|---|---|---|
| Terrain block size | Reference cliff faces read as roughly 9–13 px wide blocks with 7–10 px courses. Before has broad roughly 20–30 px modules and thick horizontal ledges. The left/front plateau edge around x=0–145, y=420–500 makes this especially obvious. | Reduce visible cliff module width/height to approximately 45–60% of the current large modules; compose more small courses within the existing plateau outline. Avoid scaling the whole landscape to achieve this. Keep irregular offsets and moss caps instead of repeating a few giant stacked slabs. |
| Cottage | Source roof/house silhouette occupies approximately x=202–312, y=220–334. Before is roughly x=198–323, y=203–344 after normalization. The roof rises too high and the front steps extend too low. Exact recipe ground anchor is (260,308) at Z=560. | Begin near 0.82–0.88 of current cottage scale around its ground contact, then compare. Retain warm plaster, dark structural timbers and irregular orange tile courses. Use the rebuilt cottage with its proper foundation; do not add a generic platform. Recheck roof ridge and front-step extrema after swapping, since equal mesh scale factors do not imply equal projected silhouettes. |
| Player | The source figure is near x=177, with feet around y=394 and head around y=370. Before is already near the same contact, with approximately 24–27 px total screen height. The player stands left of the lantern, below-left of the cottage. | Preserve feet near (177,394). Substitute the rebuilt explorer and match this small scene-level height, rather than enlarging the detailed character to showcase it. Ensure the scarf/jacket silhouette stays readable without dominating the cottage. |
| Vegetation | Source groups distinct blocky shrubs around paths, fences and cliff breaks, leaving legible grass/trail patches. Before covers most ground with very fine mottled grass and numerous tiny white flowers. Trees read as rounded low-poly clumps in before, versus layered cube clusters in the source. | Reduce uniform micro-grass/flower coverage and organize denser tufts into discrete 8–20 px patches. Place dark shrubs at cliff corners and path shoulders, with quieter ground between them. Use rebuilt voxel tree canopies; match source canopy footprints rather than retaining thin trunks topped by rounded lumps. |
| Bridge | Source crossing runs approximately (255,550) to (355,607); before approximately (251,553) to (366,613). Exact recipe deck-center anchor is (307,579) at Z=280. Source has thin frequent boards and low sparse wooden rails. Before boards and supports read broad/heavy. | Shorten projected bridge length roughly 8–10%, shift the crossing a few pixels upward after matching endpoints, and use more/thinner plank courses. Preserve bank-to-bank contact and path continuation. Reduce massive visible under-deck piers and continuous rail dominance; retain physically plausible supports. |
| Water | Reference channel carries broken turquoise/blue facets, short pale glints, emergent small blocks and reed clusters. Before is an almost uniform smooth saturated teal sheet with fine sparkle, especially in the broad channel below the bridge. | Introduce broad irregular color/facet patches and short discrete highlights at the scene's voxel scale. Scatter partly submerged bank stones/cubes and reeds in small groups. Preserve the channel's open-water silhouette; do not fill it with evenly spaced vegetation or a uniform pattern. |
| Cottage garden / utility area | Recipe contacts are shed (132,351), well (351,352), lantern (273,369). These spatial relationships are recognizable in before, but the well/lantern assembly and thick rails compete with the cottage. | Preserve the contact anchors, then tune rebuilt prop scales to the source's subordinate silhouettes. Keep the garden bed low and its rows/individual crops visible. Use the source's simple fence rhythm rather than heavy uninterrupted rails. |

## Landmarks to keep stable during integration

`reference.py` explicitly encodes the following ground/contact anchors and elevations:

| Anchor | Pixel coordinate | Elevation |
|---|---|---:|
| Cottage | (260,308) | 560 cm |
| Shed | (132,351) | 560 cm |
| Well | (351,352) | 560 cm |
| Lantern | (273,369) | 560 cm |
| Stair top | (157,429) | 560 cm |
| Bridge deck | (307,579) | 280 cm |

The reference projection is orthographic: yaw 135°, pitch −45°, 5.5 cm per reference pixel. The code's pixel→world→pixel round trip was checked for all six building/contact anchors; numerical error was below 0.000001 px. This establishes consistency of the helper, not agreement between any mesh silhouette and the picture.

The code's plateau elevations are 880 / 560 / 280 cm, with the lower landing and south bank both at 280 cm. Its `MAIN_EDGE`, `UPPER_EDGE`, `LANDING`, `SOUTH_EDGE` and path polylines encode the composition. Distinguish these ground anchors from asset tops: a roof that is too tall can move in image space while its ground anchor is correct. Correct local asset dimensions/pivots before changing camera projection or all plateau landmarks.

## Review order

1. Hold the existing portrait camera and reference-grid mapping steady. Verify cottage, player and bridge ground contacts first.
2. Match terrain block size and cottage silhouette. These dominate the image and establish the size of neighboring props.
3. Match tree/shrub cluster footprints, sparse grass/flower distribution, crop-bed height and fence thickness.
4. Match bridge board frequency and river facets/bank detail. Recheck path continuity across both bridge endpoints.
5. Capture the whole scene again at the same framing and compare silhouette landmarks before accepting details. The source's bottom-left inset is a presentation reference, not a world-space building/character cluster to duplicate in the scene.

This is an independent discrepancy audit, not visual acceptance of the before scene or any rebuilt asset. Scale suggestions are starting adjustments grounded in the shown frames; the integrated render must determine the final values.

## Stage 2 review

`Docs/Environment/stage2.png` was opened beside the original. The three highest-priority remaining visible corrections are:

1. **Ground shape and block language.** The new path is a constant-width pale ribbon with sharp mitred bends and cut-looking ends. Around reference-grid (145,70), (35,180), (125,245) and the lower bank bend near (380,640), those angular joins diverge from the original's irregular worn trail. Restore the prior organic edge geometry and apply coarse dirt/stone pigment as planned. Cliff faces also retain tall striped-column silhouettes: the left foreground at x=0–130, y=420–515 and the upper retaining face below the wheat make this visible. Keep the traced plateau edges; use smaller interlocking block courses and less continuous broad vertical striping.

2. **Tree orientation and grouped vegetation.** The rebuilt canopy has different extents along its local horizontal axes. In Stage 2 several trees read as narrow oblique capsules or flattened crowns, rather than the source's broad branching clusters. `assemble_environment.py` preserves old instance transforms and random yaw, so an anisotropic new mesh can be presented edge-on even when the old canopy looked acceptable. With the reference camera yaw 135°, a local-X broad crown projects horizontally near actor yaw 45° or 225°; try a limited variation of roughly ±15°, with pitch/roll zero. Inspect the major upper tree near source-grid (295,63), right/lower tree near (448,720), and foreground tree near (340,788). This is a orientation/footprint correction to test, not a claim that those unseen instance Euler angles were measured from the image. Maintain clustered shrubs and quiet ground between them.

3. **Cottage silhouette and surface character.** Stage 2 is much closer in size than the before scene: its approximate reference-grid silhouette is x=215–312, y=230–339 versus source roughly x=202–312, y=220–334. **Do not repeat the earlier global shrink suggestion.** Trial a slightly fuller roof/upper footprint, roughly 8–12% in XY, while holding height/contact close and checking the reference. The stronger discrepancy is now the neat long roof strips, uniformly clean timber/plaster planes and bright saturated orange. Match distinct uneven tile ends/course overhangs, more restrained warm pigment and small grounding stones/plant interruptions. The original has accumulated small forms, not simply a larger roof.

The player still lands close to source feet (177,394) and scene-level height; enlarging it would reduce fidelity. Water facets and rebuilt wheat are being handled by the main integration pass and were not accepted from this Stage 2 image. Restoring a path or improving a mesh is not sufficient by itself: the next whole-scene capture must be compared against the original at the same framing.
