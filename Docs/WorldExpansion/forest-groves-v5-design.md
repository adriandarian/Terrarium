# Additive woodland groves

The V5 grove layout adds 3,755 planned trees in 18 irregular woodland masses across the valley flanks and between settlements. Each grove uses a lobed elliptical boundary and three offset small clearings. Placement is deterministic and does not follow a grid. Most groves contain 215 trees; two constrained sites contain 195 and 120.

Measured nearest-neighbour distances in the generated plan are 3.494 m minimum, 4.317 m mean and 5.236 m at the 90th percentile. The actual source canopy measures 3.68 by 3.91 m; scales from 0.9 to 1.3 preserve tree heights near 4.5–6.5 m and allow crowns to form groups. Spacing also excludes the original 2,200 forest instances.

The plan protects settlement pads plus 14 m, the home, road widths plus 7 m and river margins. Analytical source elevation and slope filters avoid high and steep terrain. The native integrator then reads the final V5 terrain labels, traces the actual ground, checks four additional root-support points and skips trees across sharp terrace edges. Final accepted counts can be lower than the planned count and are reported explicitly.

Only `/Game/Terrarium/WorldExpansion/V5Forest/FT_WX_V5ForestGroves` is added or replaced. It references the existing private region tree mesh, whose three visual LODs and simple trunk capsule are verified without modification. The capsule has a 30 cm radius, 200 cm cylinder length and centre at Z=130 cm before per-tree scaling. The foliage uses BlockAll with this existing simple collision. Existing forest instance transforms are captured and verified after the additive operation. Automatic source LODs remain in use; default distance visibility preserves woodland masses in full-region views.

Files: `forest_groves_v5.py`, `forest_groves_v5_integrate.py`, `forest-groves-v5-layout.json` and the generated native `forest-groves-v5-integration.json` receipt. Source generation, spacing measurements and compilation were completed without editor calls. Native placement, visual quality, persistence and collision acceptance belong to the coordinator.
