# Gap 02: lighting and color separation

`Scripts/Fidelity/lighting_v7.py` supplies an idempotent `apply()` function for
the existing lights and post-process volume in `HomesteadFidelity`.

The previous pass used 20,500 lux, a strongly amber `(1, .87, .68)` sun,
a 16-degree source angle, sky intensity 5, exposure compensation -0.65,
and global saturation 0.95. The new pass uses 22,500 lux with a less amber
`(1, .93, .81)` sun, a 10-degree source angle, sky intensity 4.7 with a subtle
cool `( .87, .94, 1)` tint, exposure compensation -0.70, and saturation 1.
RGB values here are the linear color inputs to Unreal's light setters.

The existing sun direction, pitch -50 and yaw 145, is preserved because the
previous 220-degree yaw trial obscured both the cottage and wheat. The intent
is more readable golden direct light, cooler ambient shadows, and clearer
material colors without sacrificing the visible cottage walls. Water color
is affected by illumination only; this module does not modify water materials.

The function checks the editor project and map before mutation, returns and
logs JSON read back from the actual components, and leaves map saving to the
integrator. Light colors in that report use Unreal's stored sRGB byte values,
so they should not be compared directly to the linear inputs above.

Validation: source syntax checked offline. Existing local editor scripts verify
the actor labels, rotation, light intensity/color/source-angle setters, sky
recapture, and post-process override patterns. Native execution, saved map
validation, and comparison of lit cottage walls, grass, wheat, stone, and
turquoise water remain integration checks. Visual completion is not claimed.
