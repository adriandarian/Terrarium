# Gap 16: productive garden and compact well

`Scripts/Fidelity/homestead_v7.py` keeps the cottage/shed/well/lantern ground anchors and wheat footprint, replaces the cottage with the gap 14/15 `Cottage_v5`, and reduces the well scale from 1.08 to 0.84 (22%). The main bed is now a broad 275 by 225 cm mixed garden at reference contact pixel (306, 356), with a small companion bed east of the well at (379, 348). The main bed's cultivated footprint is 94% larger than one old main bed. Its position leaves the lower garden path accessible and the well's stone ring separate. Existing fences remain open along the front.

`Scripts/Assets/garden_v3.py` builds `SM_GardenBed_v3`. It uses low split timber edging, four planted soil rows, 24 mixed cabbage/red-produce/herb plants at varied growth sizes, a small harvest crate, a hand tool, and restrained soil stones. `build_mesh()` returns geometry for offline verification; `build()` saves through Unreal meshkit.

## Offline evidence

Executed the recipe using the actual meshkit geometric primitives with an empty Unreal module stub. All primitives passed the built-in closed-component, positive-volume, and outward-triangle assertions. All coordinates are finite. Result: 323 components, 5,273 vertices, 9,254 triangles. Bounds in cm: x -161.30..171; y -120.31..120.31; z -1..53.65. The main soil footing extends 1 cm below its placement origin.

Executed the placement recipe with a placement recorder: six standalone landmark/garden placements plus inherited fences and the original wheat clipping/spacing. No binary asset or editor changes were performed by this agent.

## Integration and visual check

Build `garden_v3` / `SM_GardenBed_v3`, review it in Unreal, and register that review before calling the strict placement loader. Use `homestead_v7.build()` in the scene integration. Check the gameplay camera for well/bed separation, cottage visibility, path clearance, and planted-area fullness. The garden exclusion polygon used by vegetation is narrower than the open front of the actual fence; integration should protect the main bed footprint from plant scattering as it does other landmarks. Offline evidence does not establish editor import or visual acceptance.
