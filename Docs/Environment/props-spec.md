# Reusable homestead props

`Scripts/Reconstruction/environment_props.py` wraps six existing `compound.py`
functions as independent unsaved meshes. It does not include the compound layout,
perimeter fence or shared ground. Shared recipes remain unchanged. Each wrapper
reflects X exactly once with winding reversal, then grounds minimum Z at zero.

| Builder | Mesh | Dimensions X / Y / Z, cm | Triangles |
| --- | --- | --- | ---: |
| house | SM_Env_Cottage | 405.7 / 447.85 / 477 | 42,404 |
| shed | SM_Env_BlueShed | 191 / 184 / 215 | 8,140 |
| garden | SM_Env_VegetableBed | 262 / 217.85 / 57 | 9,900 |
| tower | SM_Env_Tower | 109.0375 / 100.2 / 263.5 | 5,148 |
| small_lantern | SM_Env_Lantern | 41 / 41 / 185 | 880 |
| flower_row | SM_Env_FlowerBorder | 249.5 / 34.5 / 128 | 2,376 |

`SPECS` receives actual min/max bounds after each build. Cottage bounds are
X `[-232.35, 173.35]`, Y `[-250.5, 197.35]`, Z `[0, 477]`. These include its
projecting dormer, roof, planted footing and entrance steps. The underlying wall
plan is 254 by 302 cm; the body runs from Z 45 to 248 cm. Place using measured
bounds rather than assuming its pivot is the footprint center.

The supplied environment attachment `image-1.png` was visually checked against
the separate compound illustration. Both show a narrow doorway elevation beside
a deeper windowed side, a tall open chimney, and a much smaller teal-roof shed.
The reusable cottage preserves that compound geometry instead of substituting
the wider standalone `cottage.png` building. Fine proportions remain dependent
on the final scene camera and require an actual render comparison.

All local fronts remain negative Y after reflection. For the requested camera
yaw **135 degrees**, use cottage actor yaw **+90 degrees**: its doorway normal
becomes positive X, placing the narrow door elevation on image-left, while its
reflected dormer/window side faces negative Y on image-right. Start the shed at
yaw **0 degrees**, matching its different visible face balance in the reference.
Tower and lantern can start at yaw 0; rotate the garden and flower border to follow
the scene's garden/fence directions. The flower border's long axis is local X.

Offline checks passed for every component and every triangle after reflection:
closed construction, positive component volumes, outward winding and exact
minimum Z=0. No editor calls or scene placement were performed. These are static
props; scene lighting, scale relationships and final visual matching remain the
integrating process's responsibility.
