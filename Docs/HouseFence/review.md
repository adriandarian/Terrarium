# House and fence reference correction

Updated `/Game/Terrarium/Maps/HomesteadFidelity` to bring the cottage and yard enclosure closer to the supplied concept while retaining the softer scene treatment.

- Cottage: compact footprint, five broad overlapping roof courses, shorter chimney, narrow front window left of the door, and the original timber framing, footing and steps. Removed the previous detail pass's extra planters and slatted shutters.
- Fence: low rustic two-rail construction, uneven post caps, bindings and restrained wood detail. Thirteen posts and eleven rail sections follow the back and right perimeter, return toward the cottage, and leave the courtyard entrance open.
- Preserved the house actor anchor and all surrounding scenery assets, materials and transforms.

The previous scene is retained at `/Game/Terrarium/Maps/HomesteadBeforeHouseFence`. New mesh recipes are `Scripts/Assets/cottage_reference.py` and `Scripts/Assets/fence_reference.py`; integration is in `Scripts/align_house_fence.py`.

## Validation

Inspected the final native Unreal editor render in `house-fence.png`. Saved and reopened the working map, then compared persisted assets and transforms with the pre-save state and backup. All assertions passed; `verification.json` records the results. All three new meshes have zero saved normal errors. Python syntax checks passed for the five new implementation and capture/verification scripts.

This was an editor visual and persistence check. Packaged gameplay and collision behavior were not tested.
