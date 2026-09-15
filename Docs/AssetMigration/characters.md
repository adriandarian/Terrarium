# Character, creature, and item references

The source PNGs were individually inspected. These are rendered images, not model files. Their visible silhouettes and palette guide seven new static maquettes in `/Game/Terrarium/Migration/Meshes`. Backside geometry is an interpretation except where the player back reference supplies evidence. Existing traveler models remain intact.

| Source | New mesh | Distinctive geometry |
| --- | --- | --- |
| `brambit.png` | `SM_Brambit` | Warm brown block body, tan face, tiny legs, three asymmetrical leafy crown shoots |
| `kindlehorn.png` | `SM_Kindlehorn` | Orange quadruped, tall triangular ears, cream muzzle/belly, single golden crystal horn, curled tail |
| `rillip.png` | `SM_Rillip` | Stepped round blue body, teal side fins, small flipper feet, coral cheeks and pale smiling mouth |
| `player_front.png`, `player_back.png` | `SM_PlayerExplorer` | Dark hair, coral jacket, golden scarf, green backpack with pockets and clasps, dark trousers and brown boots |
| `ranger_sela.png` | `SM_RangerSela` | Silver bob, teal long coat, cream scarf, bent arm and ochre cross-body satchel |
| `moss_tonic.png` | `SM_MossTonic` | Squat teal bottle, cork, blank cream label, tied leaf; physical prop interpretation of a UI item icon |
| `trail_prism.png` | `SM_TrailPrism` | Faceted golden diamond within a brass/green equatorial frame; physical prop interpretation of a UI item icon |

`grove.png`, `ember.png`, `tide.png`, and `storm.png` are elemental UI symbols. `ember_crest.png` and `deep_delver_mark.png` are UI badges. Keep these as source references: a 3D-looking icon does not define a full 3D object. Animation atlases are also retained as references; the static player/ranger meshes do not reproduce those animations.

Recipes use centimetres, a ground-level pivot and -Y forward. Characters are approximately 160 cm tall, creatures approximately 100–120 cm tall, and props 46–60 cm tall for inspectable gallery use. These dimensions are authored guesses, not measurements recoverable from the PNGs.

These are static meshes with baked vertex colors and opaque rough materials. They have no skeleton, skin weights, locomotion, facial animation, glass transmission, emissive horn/core, authored UV texture maps, or gameplay collision. The source imagery contains details beyond this first maquette pass. Each recipe uses the existing meshkit closure, volume, winding, and saved-normal checks when baked in Unreal. Merely generating the Python recipe does not constitute an editor validation or visual approval; the coordinating editor run must report those separately.

Entrypoint: `Scripts/Migration/characters.py:build_all()`. It scopes meshkit output to the migration folder, restores the previous output namespace, and loads any existing named mesh without overwriting it.

Offline recipe construction passed on 2026-09-12 with Unreal stubbed only for importing the geometry library. All seven recipes completed meshkit's component closure and positive-volume assertions and had minimum Z exactly zero. Triangle counts: Brambit 1,716; Kindlehorn 1,640; Rillip 1,672; Player 3,080; Sela 2,904; Moss Tonic 792; Trail Prism 844. This check does not exercise Unreal baking or saved-mesh normals.
