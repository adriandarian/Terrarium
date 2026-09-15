# Humanoid reconstruction specification

The earlier migration maquettes were rejected as insufficiently faithful. They are not reused by these recipes. The three original copied PNGs were reopened for this pass: `SourceAssets/Voxel/player_front.png`, `player_back.png`, and `ranger_sela.png`.

`Scripts/Reconstruction/humanoids.py` exports `BUILDERS` and `SPECS`. Builders return unsaved `meshkit.Mesh` objects named `SM_Recon_Player` and `SM_Recon_RangerSela`. Root owns the editor save, material, actual Lit capture, and comparison. No editor tools are called by this module.

## Player

The new construction addresses proportions first: approximately 160 cm overall, approximately 45 cm wide irregular hair/head, and approximately 46 cm from chin/neck transition to hair crown. The body has a broad padded open jacket, articulated slanted sleeves, separated leg silhouettes and tall, layered boots. Fine bevelled blocks are usually 2.5–3.2 cm, with smaller facial/buckle details.

Source correspondences:

- Dark layered hair has a jagged front fringe, unequal temple locks, offset crown tufts and full back coverage.
- A broad tan face has shaped cheeks/chin, ears with inset inner blocks, large cream/dark eyes with highlights, separate angled eyebrows, nose and a shallow smile.
- The coral jacket opens over a cream segmented shirt. Ochre chest bands, side seams, front padded panels, cuffs and sleeve patch are separate geometry.
- The gold scarf has layered open-centered cloth wraps, a broad gathered front and a long asymmetric tail with fringed ends. R2 prioritizes the front reference's visible swept tail over the back image's settled tail position.
- The green backpack has volume behind the shoulders, a stepped lid, coral tab, clasp, two lower pockets, side pockets and buckled shoulder straps routed across the shoulders in 3D.
- Hands have individual block fingers and thumbs. Dark trousers have angled thighs/calves, knee contours, cargo seams and cuffs. Boots have thicker soles, toes, heel, tall shafts, tongues and multiple straps.

## Ranger Sela

Sela has her own fitted/long silhouette, rather than a recolor of the explorer: silver center-part bob with face-framing locks, warmer tan face and teal eyes, a narrower fitted long teal coat with split/flared hem, opening trim and lapels, pale wrapped scarf and hanging end, raised padded collar, sleeve badge, one relaxed arm and one arm bent toward the scarf. Her ochre satchel has a front flap and buckle, with the strap crossing the chest and continuing across the back.

## Modeling and acceptance boundaries

Rounded voxel volume occupancy is evaluated in local 3D, with exposed closed bevelled cells retained. Articulated limbs use their own rotated voxel grids. This gives actual contoured geometry on front, side and rear; it does not merely subdivide/recolor a large box. Component closure, positive volume and bounds are checked offline. They establish geometric validity, **not visual fidelity**.

These remain static reconstructions from 2D references. Hidden forms are inferred. There are no skeletons, skin weights, animation curves, locomotion, facial animation or gameplay collision. Back/front scarf differences are reconciled to one swept front-reference pose, rather than claiming both states occur in one static sculpture. Final acceptance requires actual Lit front/back views at source-comparable angles and a source comparison; triangle counts or BaseColor images alone are insufficient.

Offline construction on 2026-09-12 completed the existing meshkit closed-component and positive-volume assertions for both models. Player: 7,715 closed components and 339,460 triangles; bounds (-46.531, -22.750, 0.000) to (46.531, 38.600, 160.000) cm. Sela: 7,622 components and 335,368 triangles; bounds (-39.193, -29.500, 0.000) to (34.535, 19.467, 160.000) cm. Both have an exact ground-level pivot. These fairly dense meshes are visual reconstruction candidates, not optimized gameplay assets; none of these numbers establish art acceptance.

## R2 following actual Lit comparison

R1 was rejected on visual comparison: dense tiny cuboids produced harsh brick seams, the hair formed a square helmet covering the forehead, layered eyes cast oversized dark borders, the fragmented nose looked jagged, and the scarf tail did not appear outside the front silhouette. R2 uses garment/hair cells 1.5 times larger and caps voxel bevels at 0.07 cm. Facial skin has a clean contiguous front plane with broad blocks. Eyes are flush, wide whites with shallow pupils and no raised outline. The nose is one small cuboid. Player hair is rebuilt as a higher rounded cap with independent large tufts and an exposed forehead. The single scarf tail sweeps beyond the arm to reproduce the front image.

R2 offline checks passed component closure/positive volume and Z=0 pivots. Player: 2,800 components, 123,200 triangles, bounds (-46.657, -22.750, 0) to (57.426, 38.600, 160) cm. Sela: 2,927 components, 128,788 triangles, bounds (-39.280, -29.500, 0) to (35.092, 19.569, 160) cm. Both builders now report `refinement_pass=2`. These figures supersede the R1 candidate figures above; actual Lit R2 comparison is still required.

## R3 following front/back Lit comparison

The actual R2 front/back renders were opened alongside Sela's source. R2 improved the player, but the scarf tail, Sela satchel and bent arm appeared on the opposite screen side from the sources. R3 mirrors each completed sculpture across X, reverses every triangle's winding and reflects all validation component centers. Additional large offset tufts make the player's upper/side hair silhouette fuller.

Sela now has a distinct adult proportion: her entire face/hair/head group is scaled to 82% about the neck, and the body is lengthened in Z by 1.077142857 to preserve 160 cm overall height. The lower jaw tapers toward the chin; whites and lids are shorter than the player's. Her bob uses a rounded upper volume and separate broad side/back locks, replacing the flat square helmet seen in R2.

R3 offline checks passed closed-component construction and positive volumes. Every triangle was additionally checked for outward orientation against its transformed component center after scaling, jaw taper and reflection. Player: 2,809 components, 123,596 triangles, bounds (-57.426, -22.750, 0) to (46.657, 38.600, 160) cm. Sela: 2,617 components, 115,148 triangles, bounds (-35.092, -29.500, 0) to (39.280, 19.569, 160) cm. Both builders now report `refinement_pass=3`. Actual R3 Lit source comparison remains the visual acceptance requirement.
