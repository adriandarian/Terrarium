# Reference environment

The supplied portrait reference is assembled in **`/Game/Terrarium/Maps/HomesteadReference`**, now the project startup/default map. The preceding `Homestead` and `HomesteadFidelity` levels remain available.

[Open reference comparison](comparison.html) · [Full Unreal render](assembled.png) · [Courtyard](courtyard.png) · [River crossing](crossing.png) · [Native verification](verification.json)

The composition contains the winding upper trail, raised wheat field, cottage, blue shed, fenced vegetable garden and flower border, stone beacon, lantern, rebuilt explorer, descending stairs, river, timber bridge, foreground trail and surrounding trees. The original image's inset asset-preview card is presentation outside the 3D world and is not placed in the scene.

The reconstruction library supplies the explorer, principal tree crowns, shrubs, riverbank plants and rocks. Separate courtyard meshes reuse the compound's authored components so their spacing can match the reference. Environment-specific turf, cliff and wheat modules preserve the terrain footprint and contact heights. Older irregular path, stair, bridge and fence meshes remain where their silhouettes fit this scene.

## Validation

- Saved the level, switched to a different level and reopened it. All mesh transforms and material bindings matched the recorded state exactly.
- Verified all seven courtyard/player contacts against the 560 cm terrace, with less than 0.02 cm numerical error.
- Verified the portrait camera at yaw 135 degrees, pitch -45 degrees, 2645.5 cm orthographic width and the reference aspect ratio.
- Verified the rebuilt player at reference-image ground pixel (177,394).
- Verified 5,841 terrain tiles, 2,076 cliff instances, 84 path pieces, 40 wheat patches, 14 principal rebuilt trees, the complete courtyard and the crossing. Additional groves and shoreline groups are recorded in `groves.json` and `shoreline.json`.
- Inspected native Lit full-scene and close-up captures. An independent agent reviewed required features and relative placement against the supplied image.

This is a static environment assembly. The feature/layout review passes; exact artistic parity is not claimed. Compared with the reference, the cottage is cleaner and more schematic, some cliff columns remain more regular, and foliage/water patterns differ. Rigging, player movement, collision tuning and packaged gameplay were not part of this validation.

## Reproducibility

`Scripts/Reconstruction/assemble_environment.py` creates the new level from the preceding environment. The subsequent environment refinement scripts and numbered integration receipts record the actual sequence. Environment-only geometry recipes are `environment_props.py`, `environment_ground.py`, `environment_wheat.py` and `environment_cliffs.py`; the rejected rectangular trail tile and earlier cliff revisions are not active in the final level. `verify_environment.py` independently reads the saved editor state. `scene-state.json` contains full instance transforms and material bindings.
