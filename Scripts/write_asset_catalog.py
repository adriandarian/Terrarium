"""Summarize the saved per-asset validation records after visual review."""
import json
from pathlib import Path
root=Path('Docs/Phase1')
records=[json.loads(p.read_text()) for p in sorted((root/'Validation').glob('*.json'))]
assert len(records)==15,len(records)
assert all(r['visual_review'].startswith('passed') and r['saved_normal_errors']==0 for r in records)
summary={'asset_count':len(records),'total_triangles':sum(r['triangles'] for r in records),'all_assets_reviewed_in_six_lit_views':True,'saved_normal_errors':sum(r['saved_normal_errors'] for r in records),'assets':records}
(root/'manifest.json').write_text(json.dumps(summary,indent=2))
intro='''# Phase 1 — modular asset review

Status: complete and awaiting user review before Phase 2 composition.

![Modular asset gallery](asset-gallery.png)

The editor is open on `/Game/Terrarium/Maps/ModularGallery`, a display of the separate modules. This is a review layout, not the final homestead scene. Phase 0 remains saved in `RenderBaseline`.

## Original assets

All meshes were custom modeled in this project through Unreal Geometry Script. Each has a separate Python recipe in `Scripts/Assets`; `meshkit.py` supplies small shared solid-modeling helpers, and `build_one_asset.py` executes only one recipe per invocation. There is no all-in-one scene generation script. No Fab, Quixel, or other marketplace assets were imported.

Every asset uses a single-sided matte vertex-color material with warm, restrained palette variation. The terrain tiles and water are closed opaque solids. Water uses a stylized surface, with no simulation or animation.

| Mesh | Triangles | Lumen review |
|---|---:|---|
'''
for r in records:
 name=r['asset'].split('/')[-1]
 intro+=f"| {name} | {r['triangles']:,} | [Six angles](Captures/{name}/contact-sheet.jpg) |\n"
intro+='''
## Validation performed

- Checked every source component for closed edge topology, positive geometric volume, and outward orientation. Explicitly converted winding to Unreal's clockwise convention, then checked every Geometry Script face normal against its expected outward direction.
- Baked each DynamicMesh to a separate StaticMesh asset using Geometry Script, loaded it back, checked its triangle count, and verified every saved normal against its face orientation. All saved normal-error counts are zero.
- Inspected each asset under the approved Phase 0 Lumen rig from four quarter views, an overhead view, and a low oblique view before moving to the next asset. The ground-tile inspection floor was lowered so it did not conceal side faces.
- All 15 assets are at artistic pass 1. None reached the three-pass refinement cap.
- Kept the Phase 0 orthographic camera, fixed EV100 12, warm directional light, Sky Atmosphere, and Sky Light. This phase did not perform the final broad lighting match.

See [machine-readable manifest](manifest.json) and the individual `Validation` records for counts and results. Captures and contact sheets are actual Unreal viewport renders; contact sheets only arrange and label those captures.

## Limits and resolved tool issues

These are modular source pieces. The winding path, raised terraces, cottage/garden layout, riverbanks, and planted fields still need to be composed in Phase 2. The water module is an opaque art surface. Fine stochastic noise in the baseline shadows remains visible at close inspection; final whole-scene lighting and render polish are reserved for Phase 3.

During initial tooling setup, missing UV data caused a static-mesh build assertion, and the generic asset-duplication path failed on a level. Mesh export was corrected to provide UVs, the level was created using Unreal's map-saving API, and the editor was restarted. A disconnected vertex-color material input was also corrected before accepting the first asset. All listed assets subsequently completed their normal checks and Lit captures. No global MCP configuration or GPU driver changes were made.

No player, gameplay Blueprint, interaction system, inventory, dialogue, UI, or game logic was added. Engine-generated caches remain excluded from source control.

## Checkpoint

The objective requires a review at the end of each phase. Phase 2 has not started. After approval, arrange these modules into the raised homestead, terraces, garden, wheat field, winding path, stairs, and river/bridge layout from the reference. Stop again for composition review before the final lighting phase.
'''
(root/'review.md').write_text(intro,encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='assets'},indent=2))
