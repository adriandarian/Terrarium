# Gap 03 - Distant aerial perspective

`Scripts/Fidelity/atmosphere_v7.py` adds one native ExponentialHeightFog actor
through `apply()` after the final camera and lighting are established. It
reuses its actor on subsequent runs and checks the project and map identity.

The fog starts 6800 cm from the camera, uses density 0.05 and height falloff
0.001, and caps its opacity at 0.04. Its daylight radiance is a muted green-gold
(1000, 1150, 780), calibrated as an initial value for the existing manual
daylight exposure. Directional inscattering and sky-atmosphere color injection
are zero to keep this restrained effect predictable. Volumetric fog is disabled
because the native engine explicitly says it does not support start distance
or maximum opacity. There is no depth-of-field blur or material replacement.

The implementation was checked against the installed UE 5.8 source:
`Engine/Source/Runtime/Engine/Classes/Components/ExponentialHeightFogComponent.h`
for setters, reflected properties, and non-volumetric restrictions, and
`Engine/Shaders/Private/HeightFogCommon.ush` for distance exclusion and fog
integration. The reference camera's visible upper terrain is nearer than
8000 cm; starting fog there would miss most of the visible background.

The return report reads the actual editor property values and measures both
Euclidean camera distance and forward depth at the cottage, bridge, wheat,
and upper background. It also lists any other fog actors for the coordinator
to inspect. Orthographic render-origin correction means those geometric
measurements alone do not prove the effect's visible extent.

Offline Python compilation passed. Editor execution, saved/reopened readback,
and a direct render comparison remain integration checks. Acceptance requires
subtle reduction of distant upper-landscape contrast with a sharp cottage and
river; if the render shows a wash over those focal areas, tune the start
distance or disable the actor until corrected. This note does not claim that
the visual gap is resolved before that review.

## Render-driven revision: upper-background softness

The first integrated `pass-7.png` and `atmosphere.json` proved native fog
properties were applied, but the upper landscape and wheat still retained
strong fine detail. Fog attenuates contrast; it does not remove those frequencies.
The installed `DiaphragmDOFUtils.cpp` derives physical focal length from the
projection matrix. The orthographic matrix produces negligible physical lens
blur, while its separate depth-blur radius would also soften the foreground.

The revised module therefore creates a native postprocess material on this
specific camera. A five-sample filter has a 0.70 pixel sampling radius at the
481 pixel reference width, scaled to the current viewport width. It mixes at
most 72 percent at the top of the frame and eases to zero at 30 percent frame
height, above the cottage. The original color receives 40 percent of the filter
weight and the four neighboring samples receive 15 percent each. This is a
subtle upper-background softness effect for the fixed composition, not a
physical depth-of-field simulation. It must be reconsidered if the camera moves.
The effect adds no color tint or luminance. Existing four-percent capped fog
remains independent.

Native shader helper signatures were checked in `MaterialTemplate.ush`.
`GetDefaultSceneTextureUV`, `GetSceneTextureBufferSize`, and
`ClampSceneTextureUV` keep sampling inside the postprocess input viewport.
The material executes after tonemapping and uses the actual rendered scene;
it contains no reference-image texture or image overlay.

## Integration A/B checks

1. Reload the module and call `apply()` after the final camera and lighting.
   Confirm no shader compile errors for `M_Pass7_DistantSoftness` in the editor
   log. Save the map and its material.
2. Call `set_softness_enabled(False)`, let temporal rendering settle, and capture
   `atmosphere-A-off.png`. Call `set_softness_enabled(True)`, settle for the same
   duration, and capture `atmosphere-B-on.png`. Keep camera, viewport resolution,
   exposure, fog, lighting, and geometry identical.
3. Compare upper trees (reference y=0..90) and wheat (y=80..170): small canopy
   edges and distant stalk contrast should soften modestly without merging the
   entire crop into a smear. The off/on difference should fade continuously
   before reference y=243.
4. Compare cottage (y=243..360), traveler, bridge, and water: no systematic
   off/on detail or brightness change is acceptable there. Temporal noise may
   differ, so inspect multiple matched captures if the difference is ambiguous.
5. View both complete images at equal size against `reference.png`; reject any
   obvious blur boundary, milky tint, or loss of the miniature's structure.
6. Reopen the saved map and verify this camera still has the material at weight
   1.0, then recapture. A saved shader/material binding is structural evidence;
   acceptance still requires the visual comparisons above.

Revised Python source compilation passed offline. Material compilation and
render acceptance remain unverified until the coordinator runs these checks.
