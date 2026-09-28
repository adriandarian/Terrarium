# Remaining homestead architecture and props

This batch preserves the inherited collection's authored appearance, footprint,
pivot, UVs and placement scale. It adds private pilot meshes and real LOD coverage
without changing the approved cottage, fence, bridge, environment kit or characters.
It is a fidelity-preserving collection completion, not an architectural redesign.

**Editor completion, 2026-09-27:** all seventeen families were imported, placed and
saved in StartingHome by the coordinator. `unreal-verification.json` passed all
seventeen families. The coordinator's alternate-level reopen check passed in
[`Completion/persistence.json`](../Completion/persistence.json): mesh assignments,
materials, visibility, counts and transforms persisted; the approved eleven pilot
families and all 5,841 grass placements remained unchanged. Automatic LOD selection
was restored, and the baseline map/assets remained unchanged.

## Source deliverable

Fifteen editable Blender projects, packed material images, and 45 separate FBX
meshes live in `SourceAssets/Blender/HomesteadPilot/RemainingArt/`. The
`manifest.json` in this folder records hashes, bounds, material slots and counts.
The following table contains **Blender/FBX source counts**. Four native normalized
counts differ as documented in the validation section below.

| Family | LOD0 triangles | LOD1 | LOD2 |
| --- | ---: | ---: | ---: |
| Lodge | 327,564 | 133,452 | 36,396 |
| CivicHall | 624,240 | 254,448 | 69,552 |
| HomesteadCompound | 436,212 | 177,716 | 48,468 |
| MarketStall | 68,472 | 27,896 | 7,608 |
| Sign | 8,208 | 3,344 | 912 |
| Lantern | 10,260 | 4,180 | 1,140 |
| MossTonic | 47,396 | 21,684 | 7,940 |
| TrailPrism | 17,432 | 7,816 | 2,584 |
| EmberCrest | 65,624 | 26,820 | 7,400 |
| DeepDelverMark | 64,948 | 26,532 | 7,304 |
| Grove | 11,772 | 4,796 | 1,308 |
| Tide | 16,740 | 6,820 | 1,860 |
| Ember | 60,156 | 24,508 | 6,684 |
| Storm | 8,796 | 4,002 | 1,338 |
| BridgeThreshold | 1,512 | 616 | 168 |

LOD0 retains the cached exported source geometry. LOD1 reduces bevel segments to
one; LOD2 removes bevel modifiers. All authored mesh parts remain. The largest
axis-aligned bound change anywhere in the complete chain is 0.001054 metres.
The authored shapes, openings and supporting structure are retained instead of
decimating away small disconnected pieces.

Several inherited Blender cached export meshes aliased multiple material slots
and their polygon assignments to one material. The new packages recover distinct
materials and face assignments from the editable authoring parts, in the original
export order. Vertex-for-vertex coordinates and complete polygon topology are
checked against the cached meshes before using the recovered LOD0. Independent
FBX roundtrips confirm every slot survives and has assigned polygons. The original
Blender files remain byte-identical.

## Coordinator integration

Run `Scripts/HomesteadPilot/RemainingArt/integrate_remaining_art.py` only in the
verified Terrarium Unreal editor, with StartingHome loaded and PIE stopped. The
script imports the manifest into `/Game/Terrarium/HomesteadPilot/RemainingArt`,
duplicates reviewed Unreal material shaders, imports each real LOD, reads back
triangle counts and bounds, and swaps only matching inherited static mesh
components. Existing actor transforms and component material overrides survive.
Forced LOD is returned to zero. It saves only its new private assets and current
working map, never all dirty packages.

BlueShed and Tower have Unreal recipe meshes instead of Blender authoring sources.
The same integration script privately duplicates these two meshes and generates
three Unreal LODs with retained triangle targets 100%, 72%, 42%. Their runtime
counts were verified as **BlueShed 8,140 / 5,860 / 3,418** and **Tower 5,148 / 3,706 /
2,162**. Native coverage is seventeen families. FlowerBorder belongs to the
separate environment batch; characters are outside this assignment.

Collision follows each inherited mesh and original component, independently of
visual LOD or prop role. The final audit caught an initial family-based guess that
changed several body policies and disabled collectible collision. The coordinator
restoration uses untouched baseline BodySetup flags, collision LOD and original
component profile/enabled/overlap settings. Its explicit evidence is
[`art-collision-restoration.json`](../RuntimeCompletion/art-collision-restoration.json).
The verifier now requires that receipt and independently compares actual private
mesh/component state with the baseline and the restored settings. All seventeen
original components use BlockAll with QueryAndPhysics; all source and target
meshes have zero simple collision primitives. No lower-LOD collision optimization
is claimed.

The importer source was corrected for future replay: it copies baseline collision
flags, collision LOD and aggregate primitives, and preserves each component's
profile, enabled mode and overlap flag. The old `collision` annotations in the
source manifest and initial import receipts describe the superseded guess and
must not be used as runtime policy. Current verification/restoration receipts are
authoritative. The revised importer was syntax-checked; the coordinator's repair
script performed the actual current-asset restoration.

## Validation boundary

`source-verification.json` confirms all 15 projects open independently and all 45
FBXs roundtrip with expected triangle counts, one UV layer and material slots.
Twelve `*-LOD0.png` / `*-LOD2.png` images show actual exported meshes for the six
architecture/street-prop families. Lodge, CivicHall, HomesteadCompound and
MarketStall LOD2 previews were inspected and retained complete visible structural
silhouettes. These source previews do not establish Unreal visual acceptance.

`unreal-integration.json` records successful editor admission and placement.
`unreal-verification.json` passed all seventeen native meshes, each with three
decreasing LOD triangle counts, matching LOD material section mappings, correct
assigned materials and collision policy, unchanged placement transforms, matching
bounds and forced LOD zero. The separate persistence receipt confirms the saved
map survives leaving and reopening it.

Native captures were reviewed for retained roof/window/door design, material
identity and local placement: [Lodge](../Completion/Lodge/unreal-viewport.png),
[HomesteadCompound](../Completion/Compound/unreal-viewport.png),
[CivicHall](../Completion/CivicHall/unreal-viewport.png), and
[MarketStall](../Completion/Market/unreal-viewport.png). Existing trees partially
occlude the lodge and compound, and the civic hall close view crops its upper
extremity; these captures do not establish every hidden surface. The market view
shows its striped awning, counter structure and retained collectible arrangement.

The coordinator's final automatic LOD sweep includes four major buildings and is
tracked separately by the runtime worker. This source/admission receipt makes no
claim of completed transition smoothness or additional gameplay contact tests.

`resume_remaining_art.py` resumes a failed coordinator import using the progressive
receipt. It first verifies completed families against actual editor geometry,
LOD section/material mappings, bounds, collision, transforms and source hashes.
Verified rows are checkpointed with input and saved-package fingerprints and are
skipped during the resumed import. It leaves the original importer file untouched.
The initial source fingerprint explicitly records the later material-face repair
to seven unfinished families; already imported Lodge/CivicHall inputs did not
change. Unexpected verification API errors stop instead of silently rebuilding.

`verify_unreal_remaining_art.py` verifies all seventeen families and produces
`unreal-verification.json`. Run after saved-map reopening for persistence evidence.
It also refreshes the resumable fingerprint checkpoint and never saves assets/map.

Four source/native triangle-count differences were diagnosed with temporary native
FBX imports with `remove_degenerates=False`. All four temporary packages were
deleted, and admitted meshes were unchanged. DeepDelverMark LOD0/1 each contain
eight exact-zero-area source triangles rejected regardless of the optional filter;
the enabled filter removes another 36/8 triangles. Storm LOD0 normalizes two
triangles even with the filter disabled (matching its existing native baseline
count), then loses three more with the filter enabled. Storm LOD1 normalizes one
triangle with no additional filter removal. The exact per-triangle cause of the
Storm unconditional normalization is not isolated, so it is not described as
proven zero-area removal. Native A/B evidence accounts for the complete count
differences. Verification permits only these exact FBX hashes and measured native
counts; it does not use a general count tolerance. See
`native-degenerate-filter-probe.json`, `degenerate-source-diagnostic.json` and
`native-normalization-allowances.json`.

Background reproduction:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python-exit-code 1 --python Scripts/HomesteadPilot/RemainingArt/build_remaining_art.py
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python-exit-code 1 --python Scripts/HomesteadPilot/RemainingArt/verify_remaining_art.py
```

Both commands use isolated background Blender and never connect to the live Blender
MCP session. The build checks the scene project marker before reading asset data.
