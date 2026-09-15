# Complete homestead assembly

Built from the isolated assembly reference supplied as `codex-clipboard-9fcedba1-2186-4ac3-9363-19e0ee7d4446.png`. The magenta field is reference background, not world content.

The final family contains eight mesh types: cottage, blue shed, tower, lantern, vegetable bed, flower border, fence post and fence rails. The scene uses six individual structures/props plus twelve fence posts and ten rail sections.

The cottage has thicker roof courses and ridge caps, visible clay chips, a porch railing beside the steps, darker corner plinths, moss blocks and stored timber. The shed retains its right-facing entrance and relocated trough, adds its side window, and uses the same surface treatment. The tower and lamp have amber panes and irregular stone crowns. A fuller vegetable bed and narrow flower strip replace the prior garden forms. The fence has thicker posts and rails on continuous perimeter runs.

Buildings and beds were sized together against the reference. The cottage-side path was moved outward to maintain clearance; plants within the enlarged building, trough and garden footprints were cleared. The surrounding terrain, river, stairs and other unaffected asset types remain unchanged.

## Saved deliverables

- `/Game/Terrarium/Maps/HomesteadFidelity`: integrated game-world assembly.
- `/Game/Terrarium/Maps/HomesteadAssemblyReview`: isolated native review level with the same assembly transforms and materials.
- `/Game/Terrarium/Maps/HomesteadBeforeAssemblyReference`: prior scene backup.
- `assembly.png`: native isolated review render.
- `in-world.png`: native render of the assembly with the corrected ground context.

## Validation

`verification.json` records successful save/reopen comparison, matching asset transforms and material references across the game and review levels, exact counts for all eight mesh types, preserved unaffected scenery, and zero saved-normal errors for every mesh. All modeled components passed closed-volume checks. Both final captures were visually inspected as complete compositions.

The geometry, materials, placement and editor rendering were checked. Packaged gameplay, collision and runtime performance were not tested. This is a modeled interpretation of the reference, not a pixel-identical rendering of the source artwork.

## Reproduction

Run `python Scripts/run_editor.py Scripts/build_homestead_assembly.py` with HomesteadFidelity open. This builds the family, applies the materials, fits the proportions and updates ground clearance. `Scripts/review_homestead_assembly.py` creates the review level; `Scripts/verify_homestead_assembly.py` validates both saved levels. These are the current assembly-level entry points; older courtyard and blue-house scripts document preceding stages.
