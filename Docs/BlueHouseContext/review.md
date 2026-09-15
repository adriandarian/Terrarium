# Blue-house ground and planting correction

The rotation-only change left the old ground layout and attached props facing the wrong approach. The current scene treats the blue house, doorstep, stones, trough and planting as one composition.

- Preserved the shed's roof/body design, yaw, position, scale and soft material.
- Moved the trough and its boards/water beside the left wall, clearing the doorway; tucked the barrel behind the structure.
- Replaced the obsolete broad path under the left side with a narrower worn approach to the right-facing door. The underlying terrain stays intact.
- Removed the dense shrub/flower patch beside the entrance and placed low gray stones there.
- Arranged shrubs at the rear and lawn edges, with lower grass and ferns between them. Excluded the doorway and trough footprints from planting after checking the render.

Native visual evidence: `blue-house.png`. Save/reopen, unchanged shed transform/material, preserved underlying terrain and unchanged objects outside the local region are checked by `Scripts/verify_blue_house_context.py` and recorded in `verification.json`. Geometry checks cover saved normals and closed components. Gameplay and collision were not tested.

The prior scene is preserved at `/Game/Terrarium/Maps/HomesteadBeforeBlueHouseContext`. `Scripts/dress_blue_house.py` applies this local correction; the broader courtyard builder also calls it to preserve the updated arrangement on rebuild.
