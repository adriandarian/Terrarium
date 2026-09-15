# Courtyard reference check

The preceding house/fence pass did not check the complete courtyard composition. It retained the wrong circulation, an open well, a broad fence enclosure and foliage exclusion masks. This correction uses the supplied concept as a spatial reference for all five concerns together.

| Reference feature | Implemented correction | Evidence |
| --- | --- | --- |
| Blue shed has a short approach | Spur connects the shared approach to the front doorstep | Native courtyard render, lower left |
| Passage lies between cottage and planted area | Replaced the old front/right garden loop with a route along the cottage side | Native render, center |
| Stone and timber tower | Replaced the open well with masonry steps, closed timber housing, inset warm panes and crown | Native render, right of house |
| Fence follows garden perimeter | Retraced rear, right and front garden runs; kept the cottage and shed approach open | Native render, rear and right |
| Yard contains foliage and mixed planting | Planted shrub groups, low grass, ferns and flowers around routes and footings; made a taller flower bed beside the tower | Native render throughout courtyard |

Ground-contact traces are recorded in `Scripts/Fidelity/courtyard_layout.py` using the original 481 x 809 image coordinate system. Native visual evidence is `courtyard.png`. The screenshot was inspected after correcting the initially unclear shed connection. These checks establish the listed spatial corrections, not pixel-identical reproduction of the painting's lighting or surface weathering.

`verification.json` records save/reopen checks and preserved scenery. New tower and flower-bed geometry passed closed-component and saved-normal checks. Terrain, soft scene materials, existing cottage and shed meshes/transforms, river and stairs were preserved. Packaged gameplay and collision were not tested.

The pre-correction map is saved at `/Game/Terrarium/Maps/HomesteadBeforeCourtyardParity`.

Follow-up: rotated the blue shed 90 degrees (yaw 90 to 0), so its front faces the screen-right approach as in the supplied close-up. Location, scale, mesh and material are retained. `shed-rotation.json` records this change and `shed-rotated.png` is the native editor close-up. The earlier statement about unchanged shed rotation applies to the initial courtyard pass; the verification script now checks this intentional rotation.
