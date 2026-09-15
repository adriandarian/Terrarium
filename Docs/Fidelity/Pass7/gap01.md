# Gap 01 - Coherent native surface treatment

Implemented in `Scripts/Fidelity/materials_v7.py`. The coordinator calls
`materials_v7.apply()` after all instances are flushed, then saves the map.

The pass creates three dedicated native Unreal materials. The first integrated
render exposed repeating meadow polygons and insufficient visible grain. The
revised ground material completely excludes meadow vertex color from its base
color, replacing it with continuous world-space earth, moss and dry olive pigment.
Two-octave 111 cm islands provide the broad earth/moss shape; 38 cm dry accents
and 24 cm grain provide detail visible at the reference camera. Narrow clamped
transitions break up the patch boundaries. A separate 154 cm intensity variation
keeps larger areas from becoming a uniform carpet.

Stone retains authored vertex colors but now adds stronger weathered 53 cm
patches and secondary 20 cm grain, sized to remain visible in the final frame.
Architecture retains the quieter original treatment. All three materials have
0.97 roughness and 0.055 specular, with no normal,
displacement, emissive, image overlay, UV tiling, or silhouette effects.

Materials are assigned to current HomesteadFidelity components only, including
instanced components. Shared static meshes and foliage types are not edited, so
saved scene backups retain their previous material bindings. Trees, bushes,
flowers, wheat, garden beds, water and the traveler keep their dedicated palettes.

The apply function checks project/map identity, verifies assignments, and returns
material paths plus affected component, instance and mesh counts for integration
evidence. Only the new M_Pass7 materials are rebuilt on a repeat call.

Offline validation: Python source compilation completed successfully. The initial
pass-7 render was inspected and rejected for visible ground repetition. Editor
compilation, revised render review and saved/reopened assignment checks remain
the coordinator's integration work; this document does not claim visual parity.
