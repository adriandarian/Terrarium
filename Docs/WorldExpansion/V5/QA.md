# V5 terrain style acceptance

This folder contains a new validation run. Historical WorldExpansion receipts and the original homestead baseline remain unchanged. The current regional review opens V5, with the previous review and native captures preserved under `Before/`.

## Visual acceptance

- At player height, meadow surfaces should have small, irregular grass/moss detail that belongs beside the approved home. Large smooth olive lawns or visible evenly repeated square motifs fail this comparison.
- From HomeInValley, ground color, detail scale and local vegetation should continue beyond the original homestead. Preserve its fine stone terraces, architecture, internal river and path; avoid an isolated miniature sitting on an unrelated smooth landscape.
- Mountain sides should read as angular mossy limestone with fine material detail, irregular green coverage and understandable rock ledges. The old continuous beige bands and blunt extruded river slot should not dominate.
- At CityStreet, texture features should remain human scale, with grounded grass edges and a useful walking corridor. Added ecology should soften bare ground without hiding doors, covering roads or intersecting building fronts.
- At region distance, the mountains, riverbanks and settlements should form one palette. Inspect repeat patterns, flicker, stretched texture axes and transitions between ground and rock meshes.
- Native editor screenshots are the visual result. Imagegen albedos are actual source assets only after their imported Texture2D objects are referenced by the materials on the actual terrain. A generated scene or concept image does not count as an Unreal screenshot or a passed visual check.

## Coordinator commands

Filesystem preparation, already run:

```powershell
python Scripts/WorldExpansion/validation_v5/prepare.py
```

Run `Scripts/WorldExpansion/validation_v5/snapshot.py` in the verified editor while `V5/snapshot-request.json` contains `{"name":"before"}`. This is read-only and refuses to replace the V5 before snapshot. The original baseline copy is checked by SHA-256.

After materials, geometry and ecology are admitted:

```powershell
python Scripts/WorldExpansion/validation_v5/prepare_contract.py
```

Then execute these Python files sequentially through the verified Terrarium editor:

1. `Scripts/WorldExpansion/validation_v5/validate.py` with Play stopped. Reads geometry/material/collision bindings, source texture hashes, actual material-to-texture references, ecology counts and the inherited ground checkpoints.
2. `Scripts/WorldExpansion/validation_v5/traversal.py`, then start Play. Uses the preserved eight-route request including home-to-hub and both banks of the full city bridge. It teleports only to each initial route start, then drives real CharacterMovement.
3. `Scripts/WorldExpansion/validation_v5/forest.py` during Play. Uses actual V5 root heights; foliage collision acceptance must happen in PIE. Its diagnostic queries are excluded from clean performance samples.
4. Stop Play. Set `V5/snapshot-request.json` to `{"name":"admitted"}`, execute `snapshot.py`, save, switch maps, reopen ValleyRegion, set the request to `{"name":"reopened"}` and execute it again. All V5 instance signatures, effective materials, visibility/collision settings and cameras must survive reload. Original home signatures and original map file hashes must remain unchanged.
5. Use `observe.py` for separate passive samples after five seconds warmup. `V5/observation-request.json` accepts `idle`, `city` or `input`; avoid imports, captures and diagnostic queries during its 20-second measurement window.

Generic editor execution expression:

```python
exec(compile(open(r"C:/Users/hello/Projects/Terrarium/Scripts/WorldExpansion/validation_v5/validate.py", encoding="utf-8").read(), "v5_validation", "exec"))
```

Capture the same nine named native viewpoints into `Docs/WorldExpansion/V5/Captures/`. `review-request.json` records those native files, optional separately labelled concept images, and the coordinator's actual visual acceptance. Run `python Scripts/WorldExpansion/validation_v5/build_review.py` to publish the current V5 review and redirect the existing regional review URL. The authorized publication preserves the previous review under `Before/`; missing or failed evidence remains explicitly visible rather than being presented as accepted. The gallery buttons switch between exact previous and current native captures.

## Current boundaries

The source textures supplied for this run are 1254 × 1254 PNGs. The coordinator enabled native `STRETCH_TO_POWER_OF_TWO` resampling with texture-group mip generation, leaving the original generated PNG bytes intact. Validation checks those actual native settings and records native size where exposed; a configured mip policy is distinct from a GPU mip residency measurement. Simple and complex ground queries do not establish complete character access across the entire world. Single-LOD geometry inventories do not prove automatic distance transitions. A capped editor frame sample does not establish a shipping or populated-city performance budget.
