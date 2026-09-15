# Source reconstruction review

The main agent inspected all 72 source/model pairs on labeled comparison sheets, the front and rear views of all 27 object models, and full-size captures of the player, ranger, buildings, creatures, vegetation and final repairs. All 45 surface variants retain their corresponding original color image on authored relief geometry.

This review establishes collection coverage and records visual corrections. **The new models are reconstructions, with visible differences from the original images. Exact source parity is not claimed.** The original files are prelit 2D references; unseen geometry is authored interpretation. Character atlases are linked references, not converted skeletal animations.

## Corrections made after actual Unreal renders

| Models | Changes made after comparison | Remaining interpretation |
|---|---|---|
| Player | Larger clean face and clothing blocks, separated eyebrows and eye whites, small cuboid nose, irregular dark hair, full green backpack, wrapped ochre scarf and visible side tail; corrected handedness. | Hair silhouette, facial expression, cloth folds and source surface texture remain approximate. Static pose only. |
| Ranger Sela | Separate silver bob, smaller adult head proportions, tapered jaw, longer body, teal coat, sleeve badge, pale scarf, satchel and bent arm; corrected handedness. | Face and coat remain more angular than the source. Static pose only. |
| Lodge and cottage | Distinct upper dormer versus plain timber gable, longer tile courses, cleaner plaster panels, exposed masonry chimneys, windows, stairs and planted footing; corrected sides. | Masonry weathering, roof irregularity and small planting differ; rear elevations are authored. |
| Civic hall | Two window storeys, central arched door, clock, open belfry and shaped bell; cleaner plaster and roof courses. | Bell, facade proportions and foundation planting are interpretations. |
| Market, lantern and sign | Open market counters and crates, correct forward projecting token, handedness, lamp chain and pane construction, thicker lamp footing, sign arrow and timber end grain. | Produce variety, moss density and fine grain differ. Lantern panes use localized emission. |
| Homestead compound | Complete cottage/shed/garden/beacon/lamps/flowers/fence composition in its own mesh. | Building spacing, wall detailing and rear layout are interpreted; it does not replace the separate existing homestead scene. |
| Brambit and Kindlehorn | Wider bodies, cleaner face volumes, distinct foliage/ears/muzzles, four feet, back and tail geometry; reserved horn emission. | Anatomical rounding, leaf silhouette and palette shading differ. |
| Rillip and Moss Tonic | Clean connected front features; overlapping internal courses beneath body, crown, shoulder and neck; Rillip lightened blue palette. | Stepped corner shapes remain more regular than the sources. Bottle is opaque sculpted glass-colored geometry. |
| Trail Prism and six symbols/emblems | Real depth, complete backs, framed relief, reserved energy colors, Tide's intentional open center; repaired unintended Grove leaf gaps. | Physical interpretations of item/UI art; decorative pattern spacing and glow differ. |
| Trees and shrub | Irregular projecting foliage clusters, broader tree proportions, bark burls, roots, moss, hanging vines and flowers. | Cluster placement, trunk silhouette and foliage color remain approximate. |
| Rock, wheat, riverbank and crossing | Broad ledged stone mound; denser fine wheat stalks; reed/moss/stone patch; bridge with four post pairs and far stone steps. | Weathering and exact small-scale patterning differ. |
| 45 surface variants | Correct source texture bound to each 1 m relief module, including all revisions and candidates. | Relief heights are authored by material use, not measured from the prelit image. No full normal/roughness/ORM reconstruction or animated water. |

## Lighting investigation

The direct-only studio produced dark triangular patches in recessed voxel areas. A controlled Rillip comparison with direct shadows disabled showed a continuous lit surface. Disabling global illumination alone retained the patches. Neutral cubemap ambient illumination restored color in the recesses while preserving direct key-light and ground shadows. The final six review maps use this ambient fill; final comparisons are actual Lit Unreal captures.

A Nanite experiment on Rillip produced visible rendering corruption and was reverted. Final models use the verified non-Nanite static-mesh path. This is not a performance acceptance test.

## Validation boundary

Saved geometry, normal orientation, native-scale gallery placement, materials, source hashes and front/back render coverage are verified in `verification.json` and the gallery receipts. The models are static and unrigged. Collision, animation, navigation, packaged gameplay and performance acceptance have not been established. Mesh existence or a successful save is never treated as artistic approval.
