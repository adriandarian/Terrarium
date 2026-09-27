# Remaining model work — fresh chat handoff

## Completed continuation batch (2026-09-27)

Read `RemainingBatch/review.md`, `RemainingBatch/batch-validation.json` and the current `inventory.json` before using the older baseline below. Kindlehorn, Rillip, Player, Ranger Sela and Homestead Compound now have saved/reopened Blender sources, FBX/GLB exports and verified Unreal imports. `SourceAssets/Blender/SurfaceLibrary/SurfaceLibrary.blend` contains 45 packed material alternatives, also imported into Unreal with sample meshes.

Current coverage: **31 primary models, 45 surface materials, 7 prior placement variants, 5 associated references, 0 unassigned sources and 0 fidelity approvals**. Counts overlap for four surface sources that also have physical models. Animation atlases remain reference-only; no rig or animations were delivered. Water is an appearance-material alternative, not a simulation.

Review map: `/Game/Terrarium/Blender/Maps/RemainingModelsReview`. The original HomesteadBlender map hash is unchanged. New assets are staged in the review map, not integrated into the homestead world. `RemainingBatch/review.html` pairs original references with the models and includes a bounded collection overview. Remaining fidelity issues are explicitly documented per model. Do not interpret source coverage as final fidelity approval.

The old unsaved Blender window was unreachable through MCP and was left alone. It and the separately launched session subsequently exited; the available quit recovery was copied to `Saved/BlenderRebuild/recovery/session-before-remaining-models.blend`, but it was not verified as R21. A fresh project session performed the batch. Canonical Brambit was not edited. Use the current live state rather than assuming the R21 scene below is still running.

## Older baseline (before the continuation batch)

Updated 2026-09-27. The user requested a fresh chat and substantially lower usage after excessive repeated refinement consumed their weekly allowance. Continue implementation, prioritizing missing models.

## Goal and scope

Rebuild the assets represented by all 77 PNGs in `SourceAssets/Voxel/` as physical Blender models and textures faithful to the references, then import them into Unreal. Prior Unreal reconstructions were rejected. Cover every source explicitly, but group alternate views, animation atlases, and surface revisions with their corresponding model/material rather than inventing 77 separate objects.

Live inventory: `Docs/BlenderRebuild/inventory.json` reports 26 primary Blender models, 7 placement variants, and 0 fidelity approvals. Existing models are authored, not user-approved as visually complete. 51 source entries remain pending, including many surface revisions and alternate views.

Prioritize missing primary assets: Kindlehorn, Rillip, player (front/back and animation atlases belong together), Ranger Sela, and homestead compound. Inspect the inventory and relevant references to confirm this grouping. Then cover remaining surface/material variants and perform a bounded collection review.

## Efficiency requirements

- Read this handoff, project instructions, inventory, and only relevant recipes/references. Do not retrieve the old chat or read all historical revision records.
- Reuse the existing pipeline. Work in small useful batches. No subagents.
- One initial build and focused visual review per model; fix major structural or fidelity problems. Record minor refinements for the collection review instead of repeatedly polishing one model while others are missing.
- Validate source save/export, important geometry/material behavior, and editor import. Repeat checks only after relevant changes or failures. Avoid mass image output and redundant full-collection checks.
- Report actual coverage, validation, and limitations honestly. Do not start an unbounded refinement loop or create an automatic goal from this handoff.

## Project and connections

Workspace: `C:\Users\hello\Projects\Terrarium`. Follow `AGENTS.md` and `Docs/BlenderMCP.md`. Unreal baseline 5.8.2, `Terrarium.uproject`; Blender Lab MCP 1.0.3 with matching extension. Launch project Blender sessions using `Scripts/Open-Blender.ps1`. Discover Unreal toolsets first and call MCP tools sequentially. Verify editor project and Blender scene `terrarium_project` marker before edits. Keep MCP config project-local. Use editor tools for binary Unreal assets.

Existing world: `/Game/Terrarium/Blender/Maps/HomesteadBlender`. Preserve its terrain migration, placements, lighting, and advanced existing assets. Do not rerun world migration wholesale. Preserve unrelated and untracked work. No commit or PR was requested.

## Existing pipeline

- `Scripts/BlenderRebuild/`: `assetkit.py`, `palette_asset.py`, model recipes, `export_asset.py`, `package_blend.py`, `verify_blend.py`, import/place/capture/record scripts, `catalog.py`, `review_catalog.py`.
- Canonical assets: `SourceAssets/Blender/<Asset>/<Asset>.blend`, FBX/GLB and packed textures.
- Records: `Docs/BlenderRebuild/<Asset>/` comparison pages, mesh validation, source adaptation, visual review, saved-world verification, and placement receipts. Read targeted sections of the large README only as needed.
- `Scripts/run_editor.py` submits Python through Unreal MCP. A successful submission is not proof of completion: inspect fresh receipts. Use `python -X utf8` on Windows.
- Native Unreal captures: `Scripts/BlenderRebuild/capture_viewport.py` with capture JSON and output directory.
- Avoid `bpy.data.user_map` and Unreal map duplicate API: previous crashes. Clear relevant cached Python helper modules after editing helpers.

## Preserve Brambit R20; leave polishing for later

Canonical saved/imported Brambit revision is `r20_raised_crown_terraces`: 5 connected closed solids, 185 hidden editable construction blocks, 24,723 vertices / 49,430 triangles, one material and three 1024-square maps. Source/export/import, material, support, and multi-angle visual checks passed; fidelity still has documented differences. It is not rigged or animation-tested.

The prior chat left an UNSAVED R21 experiment in live Blender: smooth polygons, bevel width .0025 with 3 segments/harden normals, weighted-normal modifiers, scene `preserve_corner_normals=True`. It was not saved, exported, validated, or visually reviewed. Inspect live state before switching files; preserve any current unsaved user work. Do not accidentally overwrite canonical R20. R20 archives exist in source and docs `Revisions/R20` or `R20` directories. The R21 experiment can be deferred.

`export_asset.py` currently copies evaluated positions, faces, UVs and material slots but not custom corner normals/smooth flags. A possible opt-in fix was discussed but not implemented; do not derail remaining-model work to pursue it unnecessarily.

Saved Brambit actor: `Blender_Brambit_Courtyard`, location [500,-12,550.3681987190246], scale .8. Existing recipes and records are authoritative; do not reconstruct detailed geometry from chat history.
