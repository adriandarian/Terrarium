# Meadow and path ground recipes

The supplied environment reference and `before.png` were inspected. The reference reads as broad, coarse square turf facets and restrained warm path blocks. The current ground has excessive small detail and the trail appears smooth. These two unsaved `meshkit.Mesh` recipes address those surface qualities without changing scene layout.

Source: [environment_ground.py](../../Scripts/Reconstruction/environment_ground.py). No editor calls or shared meshkit changes.

| Builder | Asset name | Exact local bounds, cm | Construction |
|---|---|---|---|
| `meadow_tile` | `SM_Env_MeadowTile` | X/Y −100…100; Z −12…0 | 4×4 primary turf grid; only the four interior cells dip by 0.35–1.05 cm; two small bare earth patches; continuous buried support. |
| `path_tile` | `SM_Env_PathTile` | X/Y −100…100; Z −6…0 | Four coarse rows of 14 total rectangular dirt/paver facets with restrained tan variation and a continuous support slab. |

Both use **top surface Z=0 as the placement pivot**. Do not bottom-ground them during integration. The meadow actor’s existing XY scale of 0.36 yields a 72 cm tile with 18 cm primary turf cells. Path actors can retain their existing X scaling; irregular path shape remains the map’s responsibility. Nothing extends outside the 200×200 cm footprint.

The entire perimeter of both surfaces stays at Z=0 for continuous neighboring tiles. Exact shared top edges avoid dark bevel gaps, and the upper courses overlap the closed support underneath. There are no loose grass grains, glittering microgeometry, isolated islands or source-image billboards. All face colors are deterministic with no random per-component variation.

Palette families: olive/moss greens around `#687130`–`#737a37`, quiet earth `#827342`/`#79713d`, and warm path tans around `#b09b65`–`#baa56f`. The existing meshkit palette material remains responsible for shading.

Offline validation checks the real meshkit closure/winding/positive-volume assertions, exact bounds and perimeter surface height. Editor appearance at the actual gameplay scale remains the integration validation step; no rendered acceptance is asserted here.
