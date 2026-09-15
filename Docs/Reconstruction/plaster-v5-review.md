# Cottage plaster v5 - continuous sandstone, revision 2

The source shows mottled sandstone/plaster without masonry joints. Revision 1
introduced a 20 by 20 grid of separate beveled boxes, with a repeating stepped
height pattern. Those authored gaps, bevels and steps produced the unwanted lines.

Revision 2 replaces the grid with one 100 by 100 by 5 cm slab. Its main face is
planar; a 0.1 cm bevel exists only around the perimeter. The original source image,
source-color material and continuous 0..1 face UV mapping are retained.

Both front and rear-angle Lit captures were inspected: internal grid lines and
block steps are gone. The studio lighting still makes the surface lighter than
the original artwork; exact pixel/color parity is not claimed. User review is pending.

Unreal saved-mesh checks report one closed component, 44 triangles and zero saved
normal errors. The Surfaces gallery was saved and reopened with the R2 mesh,
its source material and ground contact verified. The other 44 gallery mesh
bindings were verified unchanged. Gameplay and collision were not tested.

- [Current front](Renders/SM_Recon_cottage_plaster_v5_R2-front.png)
- [Current rear angle](Renders/SM_Recon_cottage_plaster_v5_R2-back.png)
- [Build receipt](Builds/SM_Recon_cottage_plaster_v5_R2.json)
- [Validation](plaster-v5-verification.json)
