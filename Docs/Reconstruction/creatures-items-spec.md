# Creature, item and emblem reconstruction

All eleven original PNGs were opened and inspected before these recipes were authored. These are new volumetric recipes in [creatures_items.py](../../Scripts/Reconstruction/creatures_items.py). `BUILDERS` maps each original source stem to a function returning an **unsaved** `meshkit.Mesh`; root controls serial Unreal creation and review. Intended package root: `/Game/Terrarium/Reconstruction/Meshes/`.

Front faces negative Y; coordinates are centimeters; every recipe is translated so its lowest modeled vertex is at Z=0. The specified dimensions are actual generated bounds, not dimensions recovered from a single image. Side and reverse surfaces are authored interpretations wherever the source does not show them.

## Source measurements and observed form

All originals are 1254 × 1254. Bounds below are `(left, top, right, bottom)` with exclusive right/bottom. They were measured without changing source pixels, using the complement of `R > 175 and B > 175 and G < 115` to remove the controlled magenta background. These are approximate art bounds, including detached spark cubes where present; they are not segmentation masks used to create the geometry.

| Original | Art bounds, px | Art width × height | Observed proportions and distinguishing geometry |
|---|---|---|---|
| [brambit.png](../../SourceAssets/Voxel/brambit.png) | 255,75,1003,1156 | 748 × 1081 | Broad rounded brown body, large flat tan face, short four-legged stance; foliage and shoots occupy roughly the upper half. Middle shoot is distinctly tallest; side shoots have different heights and spread. |
| [kindlehorn.png](../../SourceAssets/Voxel/kindlehorn.png) | 291,71,1090,1189 | 799 × 1118 | Broad low orange head/body, cream projecting muzzle and belly, black short toes; two large stepped ears rise far above the head. Deep brown ear recesses surround low cream lobes. A front-center golden horn rises between the ears; tail steps upward behind. |
| [rillip.png](../../SourceAssets/Voxel/rillip.png) | 140,196,1132,1071 | 992 × 875 | Almost circular but squared-off stepped blue body; total width includes separate side fin lobes. Front has black eyes with pale highlights, coral cheeks and a pale open U-shaped mouth. Fin perimeter is dark teal, inset lobe pale aqua; two low flippers and a small cream-topped teal crown. |
| [moss_tonic.png](../../SourceAssets/Voxel/moss_tonic.png) | 268,112,1031,1112 | 763 × 1000 | Thick square green bottle occupies about three-fifths of height; shoulder narrows to neck, broad lip and tiled ochre cork. Blank cream label is a raised stepped rectangle. Neck cord and an angled hanging leaf extend beyond the right shoulder. |
| [trail_prism.png](../../SourceAssets/Voxel/trail_prism.png) | 257,120,1015,1135 | 758 × 1015 | Bipolar stepped gold crystal with longer upper taper; equatorial four-sided dark brass cage and four clamped corners. Pale core is centered inside the upper cage region. |
| [grove.png](../../SourceAssets/Voxel/grove.png) | 191,207,1064,1121 | 873 × 914 | Two separate broad leaves angle outward from a forked short stem. Light raised veins split the leaf faces; the root sits on a shallow irregular moss-and-soil block mound. |
| [ember.png](../../SourceAssets/Voxel/ember.png) | 245,84,1010,1162 | 765 × 1078 | Tall asymmetric flame with one high tip, lower side tongues, coral perimeter, orange/gold interior and projecting cream core. Detached small sparks are part of the silhouette. |
| [tide.png](../../SourceAssets/Voxel/tide.png) | 246,91,1007,1149 | 761 × 1058 | Curling droplet with a high leftward stepped tail and a true central hole. Blue depth layers, aqua rim and sparse pale crest cells are distinct. |
| [storm.png](../../SourceAssets/Voxel/storm.png) | 223,98,1031,1123 | 808 × 1025 | Slanted gold lightning crystal with continuous diagonal facets and a raised cream bolt face. Sparse slate cells cluster around and behind the bolt; detached gold cubes orbit it. |
| [ember_crest.png](../../SourceAssets/Voxel/ember_crest.png) | 169,57,1080,1220 | 911 × 1163 | Pointed shield with stepped shoulders, charcoal recessed field, raised gold rim and four red jewel clasps. Interior flame relief has an outer red curl and gold/cream inner core. Source shows backing thickness at the lower edge. |
| [deep_delver_mark.png](../../SourceAssets/Voxel/deep_delver_mark.png) | 151,50,1106,1164 | 955 × 1114 | Tall hexagonal badge with continuous straight brass rails, six joined corners, top/bottom pale teal jewels and charcoal inner border. Teal cave courses descend toward a pointed central depth; pale crystal blocks form the central descending motif. |

## Geometry checklist

The three creatures use actual three-dimensional dense voxel boundary volumes. Every exposed body cell is a closed beveled solid, with cells across front, side, top, bottom and back. Fully hidden interior cells are omitted; no source image is sampled onto a mesh, and no portrait plane is included.

- **Brambit:** 6 cm body cells with layered bark chips; separate stepped tan face and belly panels; black eyes and projecting nose; four stump feet; full moss cap; three thick asymmetric leaf blades with raised veins and stalks.
- **Kindlehorn:** dense rounded orange body and broad head; actual front-facing ear recesses assembled from dark inner cells and orange back/rim cells; cream low ear lobes; cream projecting muzzle, brown nose and belly; segmented golden taper and collar; charcoal feet; modeled stepped tail and side tufts.
- **Rillip:** rounded superellipsoid body with broad face rather than a conical body; separate thick teal fin volumes with pale raised lobes; coral cheek blocks, layered eye highlights, open U smile, pale lower rim, flippers and small crown. The full rear has the same stepped construction density as the front.
- **Moss tonic:** six-sided bottle volume, thick glass-colored corner ribs and base caps, stepped shoulder/neck/lip, separately tiled cork, raised blank label, wrapping cord and thick hanging veined leaf.
- **Trail prism:** eighteen-plus horizontal crystal courses forming both upper and lower taper; full XY perimeter at each level, internal cream-colored solid core, four brass cage rails and four stepped clamps. This has crystal and cage geometry, not a flat icon.
- **Grove:** complete soil/moss volume, forked stem, two outward tilted leaves with three depth courses, raised pale veins and modeled reverse.
- **Ember:** thick flame assembled from four or more depth courses; nested warm-color layers, raised cream/gold relief, asymmetric tongues and actual floating spark solids.
- **Tide:** thick curling profile whose central missing cells continue through the whole depth, making a real hole; aqua and pale front relief sits over blue depth layers.
- **Storm:** concave bolt outline decomposed into closed triangular prisms, with a separately extruded cream face; rear gold cells, slate clusters and spark cubes. Continuous diagonal faces intentionally follow the source rather than replacing the bolt with a stepped rectangle.
- **Ember crest:** thick shield backing, gold boundary cells, raised flame relief and four faceted red gems. Backing and two rear strap loops are geometry.
- **Deep delver mark:** thick hexagonal backing, six continuous rails with corner joints, modeled descending V-shaped cave courses, central pale crystal relief, two faceted jewels and rear fastening lugs.

## Offline geometry results

These results are from executing the real `meshkit` geometry construction with only its unused `unreal` import stubbed. No saving/editor APIs were invoked. Each `Mesh.solid()` validated all faces, positive component volume, outward winding, and exactly two incident triangles per component edge. Additional checks verified finite coordinates, one color per vertex and bottom bound Z=0.

| Destination mesh | Measured bounds X × Y × Z, cm | Closed components | Triangles |
|---|---:|---:|---:|
| `SM_Recon_Brambit` | 92.000 × 81.500 × 169.835 | 1,237 | 54,428 |
| `SM_Recon_Kindlehorn` | 91.000 × 131.020 × 175.346 | 1,983 | 87,252 |
| `SM_Recon_Rillip` | 149.040 × 82.174 × 141.520 | 1,546 | 68,024 |
| `SM_Recon_MossTonic` | 57.267 × 46.750 × 89.333 | 1,006 | 44,264 |
| `SM_Recon_TrailPrism` | 73.000 × 77.000 × 114.050 | 376 | 16,544 |
| `SM_Recon_Grove` | 100.968 × 42.048 × 99.395 | 420 | 18,480 |
| `SM_Recon_Ember` | 91.042 × 30.681 × 127.021 | 562 | 24,728 |
| `SM_Recon_Tide` | 91.042 × 30.681 × 119.042 | 572 | 25,168 |
| `SM_Recon_Storm` | 93.000 × 36.500 × 138.000 | 49 | 1,796 |
| `SM_Recon_EmberCrest` | 107.000 × 31.600 × 126.000 | 653 | 28,604 |
| `SM_Recon_DeepDelverMark` | 108.000 × 31.310 × 133.000 | 495 | 21,716 |

Component closure does not mean this is a single welded watertight manifold: these are deliberately assembled closed voxel components with internal shared/overlapping boundaries. Geometry complexity is recorded honestly; LODs and runtime collision are separate production work.

## Editor acceptance still required

No visual acceptance is asserted by these CPU checks. Compare saved meshes in Lit mode against the original images from front quarter, opposite quarter, side, back and low ground-contact views. Check body silhouette, ratio of head/limbs, fin/ear/leaf thickness, feature placement, color family and whether the hidden-side interpretation stays consistent with the visible reference.

The recipe uses the existing matte vertex-palette material contract. Bottle glass, crystal transmission and luminous cores are **not** physically reproduced by that material. The modeled core/cage/bottle structure is present; assigning suitable translucent or emissive material regions needs a separate editor material pass. Characters remain static geometry with no rig or animation. None of those limitations is hidden by a billboard or baked background.


## R2 after independent R1 Lit comparisons

All eleven R1 front and back renders were inspected against the original images before this refinement. The R1 measurements above are retained as history; the table below describes the current recipes. This is an authored refinement, not a claim that R2 has passed editor comparison.

The revision fixes the heavy black seam pattern and floating face relief seen in R1. Exposed volume cells now overlap slightly with much smaller bevels. Character face surfaces use continuous extruded stepped outlines instead of a grid of disconnected tiles. Emissive-color components omit random vertex-color variation for reliable explicit material matching.

- Brambit is 15% wider, with a broad uninterrupted tan face and belly, a shorter subtle mouth line, larger moss cells and much larger leaf cells with fewer narrow courses.
- Kindlehorn is 15% wider, with a broad clean orange face, substantially wider joined cream muzzle, a tiny warm mouth, wider and shorter ear loops, and a properly joined cream belly. The horn remains distinct geometry.
- Rillip has a lighter and less saturated blue palette, a broad uninterrupted blue face, single coral cheek panels, continuous U-shaped smile, fewer larger body/fin cells, joined pale fin lobes and shallower feet.
- Moss Tonic's label is now one clean stepped surface connected to the bottle body. The label color is deliberately excluded from emission.
- Trail Prism's crystal courses overlap with lower bevels and reserve exact core colors for an explicit emission material pass.
- Grove's leaves use a filled global voxel grid. R1 rotated cell centers without rotating the cubes, leaving unintended holes; those holes are removed while retaining modeled front, back and leaf depth.
- Ember and Tide use joined lower-bevel depth courses and less detached front relief. Tide retains its intentional central hole.
- Storm's upper bolt now has stepped square rises rather than the previous large unbroken triangular spike; the cream bolt remains a continuous faceted extrusion.
- Ember Crest now has its own relief pattern: a red outer curl around the narrower gold and cream flame, matching the source structure more closely than reusing the free-standing Ember silhouette.
- Deep Delver Mark's nested cave courses are wider, joined to the backing, and lighter teal; the floating checker pattern of R1 is removed.

| Current mesh | Bounds X × Y × Z, cm | Closed components | Triangles |
|---|---:|---:|---:|
| `SM_Recon_Brambit` | 105.800 × 81.500 × 174.485 | 565 | 24,140 |
| `SM_Recon_Kindlehorn` | 107.180 × 129.088 × 167.356 | 1,387 | 59,228 |
| `SM_Recon_Rillip` | 149.245 × 78.740 × 141.000 | 743 | 31,612 |
| `SM_Recon_MossTonic` | 57.323 × 46.400 × 89.444 | 984 | 42,936 |
| `SM_Recon_TrailPrism` | 73.000 × 77.000 × 114.180 | 376 | 16,544 |
| `SM_Recon_Grove` | 111.250 × 42.210 × 103.730 | 328 | 14,432 |
| `SM_Recon_Ember` | 91.196 × 29.568 × 127.098 | 562 | 24,728 |
| `SM_Recon_Tide` | 91.196 × 29.568 × 119.196 | 572 | 25,168 |
| `SM_Recon_Storm` | 93.000 × 36.500 × 136.000 | 71 | 1,972 |
| `SM_Recon_EmberCrest` | 107.000 × 31.600 × 126.000 | 600 | 26,272 |
| `SM_Recon_DeepDelverMark` | 108.000 × 31.310 × 133.000 | 495 | 21,716 |

### Explicit emissive-color contract

`EMISSIVE_COLORS` is keyed per source/mesh. The unsaved mesh also exposes `m.emissive_colors`. Only these exact sRGB hex colors are opt-in energy regions; pass each through `meshkit.color(hex)` when comparing to linear vertex colors. These components now use zero random color variation. Do not apply a global white/yellow threshold: that would incorrectly light skin, labels or Rillip's crown.

- `kindlehorn`: `#ffd73b`, `#ffe66a`, `#ffdb43`, `#ffc72b`.
- `trail_prism`: `#fff1ad`, `#ffe681`, `#fff4b5`, `#fff0a1`.
- `ember`: `#ffedc2`, `#ffe9b4`, `#ffc448`.
- `storm`: `#ffe6a1`, `#ffe078`.
- `ember_crest`: `#ffea83`, `#ffe480`, `#ffcb32`.

No emission is requested for Brambit, Rillip, Moss Tonic, Grove, Tide or Deep Delver Mark. Their pale features are reflective color, not energy sources. Root owns the material assignment and the saved R2 Lit verification.

## R3 targeted solid-connection repair

The latest saved R2 front and back PNGs for Rillip and Moss Tonic were inspected at full resolution. Rillip still showed deep black cavities at its stepped upper/body edge, while the bottle shoulder and neck collars appeared partially disconnected. The repair affects **only `rillip` and `moss_tonic`**; the nine other builders and the existing shared helpers are unchanged.

The new `filled_volume` helper first reproduces each existing exterior cell, then places tightly inset, overlapping solid X-course runs throughout its occupied interior lattice. This fills the shaped volume behind the exterior skin without adding a generic outer bounding box. It restores the exterior RNG state so subsequent modeled features retain their original palette variation sequence. Rillip additionally receives internal crown connections, and the bottle receives overlapping inner shoulder/neck connectors below its existing collars. Features, source palette and overall dimensions remain intact.

| R3 mesh | Unchanged bounds X × Y × Z, cm | Closed components | Triangles |
|---|---:|---:|---:|
| `SM_Recon_Rillip` | 149.245 × 78.740 × 141.000 | 928 | 39,752 |
| `SM_Recon_MossTonic` | 57.3235 × 46.400 × 89.4435 | 1,178 | 51,472 |

Both builders pass the real `meshkit` CPU closure/winding/positive-volume assertions, have ground bound Z=0 and preserve their R2 measured outer bounds. Their `refinement_pass` is 3. No material or emission changes were made. Saved R3 front/back rendering and visual acceptance remain the parent's editor verification step.
