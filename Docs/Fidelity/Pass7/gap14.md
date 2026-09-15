# Gap 14: finer terracotta cottage roof

The supplied reference uses many small, uneven tiles and layered eaves. The
current scene's roof reads as large orange courses. This recipe replaces the
main roof's 70 tiles with 208 staggered tiles, reducing each tile from roughly
55 x 68 x 31 to 36 x 39 x 16.5 Unreal units. Fourteen smaller ridge caps, thin
weathered fascia, rafter ends, restrained clay variation and sparse worn accents
preserve the warm silhouette without adding a new roof design.

The existing camera-facing projecting gable is preserved. Its roof changes from
24 large tiles to 48 smaller tiles with six caps, matching the original plaster
prism, timber frame and window coordinates.

## Integration

In the next cottage recipe, import `add_main_roof` and
`add_projecting_gable_roof` from `cottage_roof_v5`.

- Replace the main structural roof, tile loops and ridge loop in `cottage_v4`
  with `add_main_roof(m)`; retain the chimney following it.
- Retain the projecting gable's solid, beams and window. Replace its tile and
  ridge loops with `add_projecting_gable_roof(m)`.
- Both helpers optionally accept `origin=(0,0,0)` and `z_scale=1.0`. The latter
  scales all generated vertex heights, including rotated underlay geometry,
  around local z=0. Use only if the surrounding cottage is scaled equivalently.
- The caller owns the combined mesh name, save and material assignment.

## Validation

Local recipe validation checks Python syntax and runs both helpers through the
actual meshkit primitives with Unreal stubbed solely for import. Meshkit checks
closed edges, outward winding and positive component volumes. This is geometry
construction validation, not an editor import or visual acceptance claim.
The local run passed for both z scales 1.0 and 0.88: 320 closed positive-volume
components, 14,080 triangles and 7,680 vertices for both roof helpers combined.
Unscaled bounds are x=-228.27..200, y=-234.54..231.79, z=281..490.
Editor integration, saved mesh normal checks and a matching camera capture are
required before gap 14 can be considered visually resolved.
