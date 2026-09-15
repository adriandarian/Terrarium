# Gap 11: ground plants and flowers

Implemented three original low plant recipes in `Scripts/Assets/ground_plants_v2.py`: seven-frond ferns, fine grass tufts, and small cream/gold flowers. All use the existing sculpted vertex-color material. Their 17–35 cm height sits below shrubs and supports reference-scale accents rather than another hedge layer.

`Scripts/Fidelity/ground_plants_v7.py` places 194 deterministic clusters across 36 composed patches beside terrace edges, stones and open meadow. The accepted distribution is 80 ferns, 59 grasses and 55 flower clusters. It uses `vegetation_v7.occupied` and `ground_at_pixel` for building, crop, traveler and route clearance. It intentionally performs no global random scatter. Integration must call `ground_plants_v2.build_variants()` once for native assets and `ground_plants_v7.build(cells)` during level assembly.

Offline validation on the actual recipes passed: fern 1,512 vertices / 2,772 triangles / 63 closed positive-volume components; grass 312 / 572 / 13; flowers 756 / 1,288 / 56. Meshkit checked closure and outward winding of every component. Placement generation repeated identically and every accepted placement passed occupancy clearance. Height distribution: 82 main terrace, 18 upper terrace, 94 lower/south terrain.

Editor asset creation, saved normal checks and visual acceptance remain the integration owner's work. These offline checks do not establish rendered fidelity.
