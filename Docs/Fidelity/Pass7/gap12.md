# Gap 12 - river appearance

Implemented `Scripts/Assets/water_v4.py` and `Scripts/Fidelity/water_v7.py`.
The opaque native river uses finer 16.8 cm surface tessellation with continuous
vertex-color pools, turquoise shallows, blue-teal deeper water, and small broken
glints. Neighboring depth variants share edge colors and the 302 cm footprint
overlaps the placement grid by 2 cm. All visible detail is lit closed geometry.

Integration: build all three assets with `water_v4.build_variants()`, validate
their editor round trips and appearance, and replace the old terrain water loop
with `water_v7.build(cells)`. Preserve `M_SculptedPalette`; the old
`M_QuietRiverPalette` override would suppress the intended colors.

Offline validation uses the actual meshkit solid builder with only Unreal and
save stubbed. Editor rendering, final scene integration, and screenshot review
remain required before calling this visual gap resolved. Glints are modeled
still-water detail; this change does not introduce animated flow.

Offline checks passed: medium/deep each have 4,560 vertices, 6,416 triangles,
and 676 closed positive-volume components; shallow has 4,752 vertices, 6,768
triangles, and 684 components. All positions are finite. Every variant spans
exactly -151 to 151 cm on X/Y and reaches Z=2.1 cm. Boundary colors match
between depth variants. Placement generates 190 tiles: 165 shallow (including
tiles hidden underneath land), 12 medium, and 13 deep.

## Render-driven correction

Review of `pass-7.png` found unacceptable repeated diamond gradients. Matching
edge colors alone did not prevent each tile center from repeating visibly.
`water_material_v7.apply()` replaces the component surface material with
`M_Pass7_ContinuousRiver`. Its base pigment uses absolute world-position noise
only, with no vertex color or tile-local coordinate input. This removes the
source of the per-tile gradient rather than disguising the seam. The fine mesh
and raised glints remain native geometry; a world-height mask preserves the
glints above the Z=1 cm river surface. Call after `placement.flush()` and save
the map. This supersedes the earlier instruction to keep M_SculptedPalette.
Editor compilation and a fresh render are still required for this correction.
