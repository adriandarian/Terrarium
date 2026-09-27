# Remaining model batch — 2026-09-27

Five missing primary models were authored and imported: Kindlehorn, Rillip, Player, Ranger Sela and Homestead Compound. The compound reuses the existing detailed Cottage and adds its outbuildings, fence, garden and lighting structures. Sources, FBX/GLB exports, packed textures, recipes and verification receipts are retained.

The full inventory now covers 77 PNGs: 31 primary model sources, 41 additional surface-only sources, and five associated references. The surface library contains 45 materials because four surface sources also already have physical models. Seven prior placement variants remain separately tracked. These are coverage counts, not fidelity approvals.

All five new saved Blender projects were independently reopened. Export validation checked closed positive-volume component solids, UVs and material slots. Unreal imports verified centimetre scale and material assignments. A separate `RemainingModelsReview` map was saved, reopened and captured. The original `HomesteadBlender.umap` hash is unchanged. Three representative Unreal surface materials were visually checked; all 45 imported sample meshes have their corresponding material assigned.

The single collection comparison shows recognizable source identities but substantial remaining fidelity differences. The new characters have simplified proportions, hair, tailoring and stances. Kindlehorn's head/ears/horn and Rillip's rounded silhouette need a targeted future art pass. The compound's cottage footprint and arrangement differ from the reference. Earlier collection assets also retain their previously documented fidelity limitations. No model is marked user-approved.

Fixed during the bounded pass: Rillip's separated body layers, missing horn emission, coincident-face black artifacts, compound material-slot preservation, and the review camera's clipped orthographic capture. Current native review uses a perspective camera. Dense voxel seams show aliasing in the wide Unreal overview; this is not a performance or game-readiness acceptance.

Animation atlases are explicitly associated pose references; no rigs or playable animations were created. Water revisions are opaque material appearance alternatives, without flow, buoyancy, refraction or water gameplay. Surface alternatives were not substituted into the existing world. Collision/navigation and gameplay were not tested.

At connection time the pre-existing unsaved Blender window was not reachable through MCP. It was left untouched; a separate project-launched session performed this work. Both initial Blender windows later exited. The available `quit.blend` was copied into `Saved/BlenderRebuild/recovery/session-before-remaining-models.blend` before relaunch, but its contents were not verified as the prior Brambit experiment. Canonical Brambit source/import files were not edited.

Open `review.html` for original/new image pairs and the collection contact sheet. Machine-readable evidence is in `batch-validation.json`, each asset's receipts, and `SurfaceLibrary/unreal-import.json`. No commit or PR was created.
