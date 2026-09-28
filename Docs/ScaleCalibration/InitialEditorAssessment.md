# Initial blockout editor assessment

The native Unreal capture and successful build receipt were inspected. The initial saved level contains 98 actors. Its principal landmarks occupy the intended regions of the fixed concept frame, but it is not visually approved.

| Landmark | Annotated width | Initial generated width | Assessment |
| --- | ---: | ---: | --- |
| Cottage | 117 px | 101.7 px | 13.1% too narrow; needs horizontal correction |
| Shed | 58 px | 55.4 px | Envelope edges within annotation uncertainty |
| Person | 18 px | 10 px | Too narrow as a comparison marker, despite edges individually landing on the ±4 px tolerance |
| Garden | 80 px | 77 px | Envelope edges within annotation uncertainty |
| Bridge and rails | 128 px | 116.8 px | 8.8% narrower; left edge exceeds annotation tolerance by about 0.6 px, a minor remaining gap |
| Stairs | 60 px | 59 px | Whole-mesh bounds agree, but upper treads are hidden by the main terrace |

The wheat patch extends beyond the crop, as the source does. Its generated right edge at x494 is not an on-screen discrepancy; the visible right edge is x481. The visible clipped bounds fit the annotation uncertainty. Tree clusters remain coarse envelope markers, not representative crowns.

The staircase is the blocking geometry issue: a mesh can have correct projected bounds while its important surfaces remain occluded. The continuous main terrace needs a small corridor removed around the stair ground footprint. The prepared single correction pass also stretches cottage geometry to 117 projected pixels about its x251 anchor and the figure to 18 projected pixels about x177. This changes only horizontal camera-space coordinates. Heights, ground contacts, camera and vertical projected bounds remain fixed. The figure stays 180 Unreal centimetres tall.

`projected-bounds-assessment.json` retains the actual initial receipt values, annotation errors and crop handling. `patch_stair_notch.py` creates dedicated replacement meshes and retains the original assets. Successful save and a new native capture are required before calling the correction verified. No fine-detail, lighting, material or whole-scene fidelity approval follows from these measurements.
