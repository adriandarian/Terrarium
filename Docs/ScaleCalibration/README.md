# Concept scale calibration

This is the first scale milestone: a separate, simple-color composition for reviewing relative silhouettes and spacing. It is not a replacement environment or approved reconstruction. The current world and model sources are the baseline.

`targets.json` records manual observations from the full 481 × 809 concept. `measurement-sheet.html` displays those annotations over the reference. Pixel tolerances describe annotation uncertainty, not an achieved match. Small/occluded forms warrant wider tolerance than the proposed 5–10% review threshold.

## What the picture supports

| Form | Approximate visible envelope | Ground/contact observation |
| --- | --- | --- |
| Cottage, roof and chimney | 117 × 120 px | Front foundation near (251,333); hidden back corners inferred |
| Shed | 58 × 51 px | Front corner near (132,355) |
| Main-scene person | 18 × 29 px | Feet near (177,394); inset person excluded |
| Planted garden bed | 80 × 52 px | Bed occupies only part of the much larger fenced yard |
| Wheat | 249+ × 112 px | Right edge cropped by the image; field not a small garden-sized patch |
| Bridge | 128 × 76 px | Deck spans roughly (267,552) to (354,606) |
| Stairs | 60 × 57 px | Upper edge (145,430)–(175,417), lower edge (174,471)–(204,456) |

The cottage envelope is about 4.1 person envelopes tall, but that is **not** a ratio of real vertical building and human heights: the building's projected ground depth contributes to the envelope. Shed width is about half cottage width. Most tree crowns are closer to shed width than cottage width; their obscured ground anchors have low confidence. The full scene contains substantial quiet ground between these shapes.

## Construction conventions, separated from observations

The existing camera has yaw 135°, pitch −45°, and ortho width 2645.5. The existing reference model uses 5.5 Unreal units per source pixel and terrace tops 880 / 560 / 280. These settings are retained to make comparisons reproducible, **not because the picture establishes metric dimensions or a uniquely correct camera**. At this camera, the 320 / 280 unit terrace drops project to about 41 / 36 vertical pixels, approximately compatible with visible cliff bands.

The shared person marker is 180 Unreal centimetres tall. Its vertical axis projects to 23.14 px; projected head/body depth adds several pixels, consistent with the observed ~29 px envelope within uncertainty. This convention aligns the scale blockout with the separate detail specimens. It is not evidence that the illustrated person is exactly 1.8 metres tall.

Silhouettes and ground polygons were re-read from the image. Old placement-script coordinates provided a cross-check; they were not taken as measurements of the existing rendered scene. In particular, the garden annotation distinguishes the actual planted bed from the entire fenced courtyard. Shadows and the lower-left reference inset are excluded.

## Isolated implementation

Run `Scripts/ScaleCalibration/build_blockout.py` in the verified Terrarium editor through Unreal MCP. It creates `/Game/Terrarium/Calibration/Maps/ConceptScaleBlockout` with dedicated assets under `/Game/Terrarium/Calibration/ScaleBlockout`. The script aborts before mutation if any map or content package is dirty, or if the destination map/assets already exist. It does not automatically save, duplicate, or modify the baseline map. A partial failed build deliberately requires inspection before another run.

The blockout contains continuous terrace volumes with grass caps, flat path ribbons, a gabled cottage and shed, a person marker, tree crown clusters, field and garden patches, a fence boundary, a bridge deck/rails and eight stair masses. These are scale landmarks, not construction-detail exemplars. Using continuous terrace solids avoids treating large cliff modules as the desired surface detail size.

After successful save only, the script writes `blockout-receipt.json` with analytically projected mesh bounds and `capture-args.json` for the existing native capture helper. Pilot `Scale_ConceptCamera`; retain its constrained 481:809 aspect ratio and full crop. Capture to `Docs/ScaleCalibration/Unreal/unreal-viewport.png`. When comparing, crop only the viewport's black side bars and resize the **content rectangle** to the reference dimensions; do not stretch the full wide screenshot.

## Validation and remaining uncertainty

Before editor execution, the Python source parsed successfully, targets JSON loaded, all four concave terrace polygons triangulated, and the projection/inverse projection round trips passed. This is source-level validation only. The script checks closed generated meshes, asset saves and level save during execution. It does not claim lighting, silhouette similarity, successful reopen, or visual approval before native editor evidence exists.

Review the cottage/person and shed/cottage envelopes first, then bridge/path width, tree crowns and terrace edges. Do not tune individual existing assets to compensate for any mismatch. Roof back edges, tree anchors, far-field extent and actual elevations remain inferred. The fixed camera may still need a single explicit calibration decision if a comparison demonstrates systematic perspective disagreement; do not silently move it between evidence captures.
