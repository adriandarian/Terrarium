# Gap 17: bridge and stairs

Implemented source recipes in `Scripts/Assets/bridge_v3.py` and `Scripts/Assets/stairs_v3.py`. Each exposes `build()` and uses the existing Mesh editor baking path, producing `SM_PlankBridge_v3` and `SM_StoneStairs_v3`. No editor changes were performed by this agent.

## Visible changes

- Bridge: thirteen individually colored broad planks, embedded end splits and wear, three lighter posts per side, slimmer rails with slightly unequal middle-post locations. Rails terminate inside their posts. Half-transoms connect the posts to the stringers. Six piles and three braced trestles remain, with modestly slimmer timber dimensions. Small moss patches sit on the abutment shoulders.
- Stairs: alternating tread joints, variable stone colors and worn bevels, embedded front-edge chips, lower irregular side caps, and fine tufts rooted into moss on those caps. The primary walking surface remains open.

## Placement contract

- Bridge retains v2 X/Y bounds exactly: X ±114.5, Y ±291.5. The nominal plank center remains z58; support piles reach z-240. Existing bridge placement z222 therefore places the pile bottoms at world z-18. Keep existing x/y scaling .9/1.4 and rotation. Stringer tops z50 overlap every deck board bottom; transoms intersect both posts and stringers.
- Stairs retain eight 30cm rises and center positions y=-147 through y147. The three upper walking slabs all end at local z249. Width bounds remain X ±125 including side stones. Caps intersect their supporting masonry courses; tufts start inside the cap surfaces.

## Offline verification

Executed both recipes with only `unreal` stubbed and `Mesh.save` replaced by an identity return, so all original Mesh solid construction assertions ran. Both passed closed-component topology, positive volume, outward winding, finite vertex, valid triangle index, deterministic vertex/color generation, and placement assertions.

| Mesh | Vertices | Triangles | Closed positive-volume components |
|---|---:|---:|---:|
| SM_PlankBridge_v3 | 3,408 | 6,248 | 142 |
| SM_StoneStairs_v3 | 4,416 | 8,096 | 184 |

Editor baking, StaticMesh round-trip verification, replacement of the scene actors, and rendered review are pending parent integration. These source checks do not establish that the visual gap is resolved in the running scene.
