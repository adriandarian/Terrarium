# Kindlehorn - revision 6

The horn has a luminous gold lower crystal and a tapered amber tip, with a restrained warm local light. A looping Niagara system emits small square sparks around it; particles rise, fade and die. The emission mask is authored only on the horn, so cream fur and eyes remain ordinary lit surfaces.

The belly is now five overlapping, tapered courses of tan fur blocks with varying projection. The rear tail is an upright, broad stepped tuft that sweeps out beside the body, with red-orange blocks and amber accents. It replaces the narrow central rear strip.

Both current images are native 1254 by 1254 Unreal Lit renders. The saved mesh has 55,972 triangles and zero saved normal errors. The reusable actor is `/Game/Terrarium/Reconstruction/Blueprints/BP_Kindlehorn_R6`; it combines the static mesh, Niagara component and horn light. Use that Blueprint to retain the sparks when placing the creature.

A native simulation-cache check on the Blueprint verified live particles at three simulation times (6, 12 and 15 particles), changed positions, fading alpha and replaced particle IDs after expiration. The Niagara system compiles without errors or warnings. This checks editor simulation, not a packaged game or creature animation.

The Characters gallery was saved and reopened with the updated mesh and attached effects. Its other four mesh bindings remain unchanged. The gallery overview was recaptured and HomesteadReference restored without altering default maps.

Pending user review. Exact pixel parity is not claimed; proportions, small block placement and material detail can still be refined against the concept.

- [Current front](Renders/SM_Recon_Kindlehorn_R6-front.png)
- [Current back](Renders/SM_Recon_Kindlehorn_R6-back.png)
- [Build receipt](Builds/SM_Recon_Kindlehorn_R6.json)
- [Particle simulation verification](kindlehorn-fx-verification.json)
- [Gallery verification](kindlehorn-verification.json)
