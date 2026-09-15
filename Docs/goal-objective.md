Goal: Build a single static 3D exploration environment in this fresh Unreal
Engine 5 project that visually matches the attached reference image — a
stylized, low-poly fantasy homestead, isometric/oblique camera angle. This
is a world-generation-only milestone. Do not build a player character,
interaction system, inventory, dialogue, or any gameplay logic. A free-fly
camera in the editor viewport is all that's needed for review.

STYLE (use this description as ground truth, not genre labels like "voxel"):

- Isometric/oblique top-down camera angle
- Chunky, simplified geometry with soft/rounded edges — hand-sculpted
  looking, not fine architectural detail
- Warm, painterly palette: olive/moss greens, warm gold-wheat, teal-blue
  water, weathered tan stone, terracotta roof tiles
- Soft warm directional lighting with gentle ambient bounce — no hard
  specular highlights, no photoreal PBR sheen
- Content: stone perimeter wall around a raised grassy plateau; a cottage
  with a pitched terracotta roof and chimney; a smaller shed with a
  blue-green roof; a fenced garden plot; a wheat field; a winding dirt path
  with stone retaining walls and a stair descent; a river/pond with a
  wooden plank bridge; scattered trees and bushes; mossy, strata-lined
  cliff faces

All assets must be original and custom-modeled for this project. Do not
import Fab/Quixel marketplace content.

BUILD ORDER — stop at each checkpoint for review rather than continuing
unattended:

Phase 0 — Render baseline (do this before building anything else):

- Set the level camera to Orthographic, angled to roughly match the
  reference's oblique view
- Confirm Lumen is enabled for both Global Illumination and Reflections in
  Project Settings
- Add a Directional Light, Sky Atmosphere, Sky Light, and a Post Process
  Volume with manual exposure (fixed EV100 — do not rely on auto-exposure)
- Place 2-3 placeholder primitives and confirm the scene renders cleanly
  under this camera + Lumen combination: no black/unlit geometry, no
  flicker, shadows behaving correctly
- Capture a screenshot and stop here before proceeding

Phase 1 — Build modular assets (not one large procedural script):

- Model each element as its own separate static mesh: cottage, shed, fence
  posts, a repeatable cliff-wall module, a stair module, bridge, tree,
  bush, wheat-field patch, ground tiles
- Use Unreal's Geometry Script / static mesh tools to build these
- For every mesh, verify correct outward-facing triangle winding and
  normals before moving on — check under actual Lumen lighting that there
  is no unlit/black geometry from any angle. This is a hard requirement:
  meshes with backface/winding errors look fine under flat/unlit shading
  but turn solid black under real lighting, and catching this per-asset
  now avoids a much larger rework later.
- Hard cap: 3 refinement passes per individual asset. If it hasn't
  converged after 3 passes, leave it at the closest state, note it as a
  known gap, and move to the next asset. Do not loop on one object.

Phase 2 — Compose the scene:

- Arrange the modular assets to match the reference's layout: perimeter
  wall, cottage/shed cluster, garden, wheat field, path with stairs, river
  and bridge, tree/bush scatter, cliffs
- Match approximate proportions and spatial relationships, not exact pixel
  placement
- Apply materials/colors per the palette above

Phase 3 — Lighting and final pass:

- Tune Directional Light angle/color and Sky/Post Process settings as one
  whole-scene pass for the warm, soft, painterly look
- This is the only phase where broad visual-matching iteration is
  appropriate, and even here: hard cap of 5 total passes before stopping
  and presenting the result for review

Non-goals for this milestone: no player character, no gameplay collision
tuning, no interaction system, no UI, no game logic.

Referenced image files:
- [Image #1]: C:\Users\hello\.codex\attachments\e15f0cd8-70dc-4b2c-9579-42e0a1c2b7fe\image-1.png