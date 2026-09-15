# Gap 09: vegetation distribution

Implemented `Scripts/Fidelity/vegetation_v7.py` with the existing `build(cells)` API. Uses traced reference grouping anchors but contracts each patch to 68% of its former radius, halves each cluster budget, reduces shrubs to 0.35¨C0.70 scale, and removes the 250-candidate linking scatter. This exposes larger patches of open ground and separates neighboring plant groups instead of drawing continuous shrub borders.

A 3.4-pixel center-separation check prevents shrub stacking. Cottage protection now includes the projected roof silhouette rather than only its foundation. Enlarged shed and traveler masks keep their silhouettes readable. Existing wheat, garden, stairs, and path masks remain active.

All 14 reference tree anchors now use `Tree_v3` at the prior reference-scaled height factor (1.12). Its narrower tiered crown changes the width while preserving placement and intended height. All eight valid landmark stone accents remain. This module deliberately delegates flowers and ground plants to gap 11 and shoreline plants/rocks to gap 13; the corresponding modules must run during final scene assembly.

## Offline validation

Executed both the old and new build functions against the actual reference geometry, replacing only editor placement with a recording stub:

- Old vegetation: 742 shrubs, 14 OrchardTree_v2 trees, 211 flowers, eight feature stones (excluding shoreline, because cells was empty).
- New vegetation: 314 shrubs, 14 Tree_v3 trees, eight feature stones.
- Shrub count decreased 57.68%; average scale decreased from 0.9224 to 0.5238 (43.21%).
- Every accepted shrub passes the occupied mask and the 0.35¨C0.70 scale limits.
- Two independent builds with different supplied cell dictionaries produced identical placements. Randomness is module-local and reseeded per build.
- No legacy tree, flower, reed, or shore-outcrop placements remain in this module.
- Python AST parsed successfully.

Unreal placement, saved scene verification, and visual comparison remain root integration work. Offline placement evidence alone does not establish that the rendered scene now matches the reference.
