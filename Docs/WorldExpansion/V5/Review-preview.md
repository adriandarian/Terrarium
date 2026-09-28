# V5 terrain correction review

**Native correction accepted**

Actual geometry, imagegen albedos and ecology are evaluated in native Unreal screenshots. Concepts and albedo source images do not count as completed world renders.

## Validation

- **Surface bindings:** Passed
- **Geometry and ground:** Passed
- **Preservation and persistence:** Passed
- **Real character routes:** 8/8 passed
- **Forest runtime contacts:** 12 sampled roots and isolated trunk bodies passed; full-world occlusion rays retained
- **New grove runtime contacts:** 12 sampled roots and trunks passed

## Native visual review

Inspected all nine native Unreal views after save/reopen. Smooth mountain silhouettes are replaced by physical stepped shelves and stone risers, the home outer terrain is terraced, and meadow/gravel/limestone detail now uses generated albedo assets with working mipmaps. Woodland groves and groundcover fill route and settlement edges. Original home remains intact. Large settlement pads and repeated street plans remain visibly regular; this terrain correction is not a claim that every district is individually finished.

## Source and evidence

- [Surface/material/texture contract](surface-validation.json)
- [Geometry and ground inventory](validation.json)
- [Original preservation and final reopen](reopened.json)
- [Eight real movement routes](traversal-receipt.json)
- [Forest contacts in Play](forest-contact-play.json)
- Geometry source: `SourceAssets/WorldExpansion/TerrainV5/manifest.json`.
- Actual generated albedos: `SourceAssets/WorldExpansion/ArtDirection/`; original source bytes compared with the specified imagegen outputs.
- Ecology source and admission: `Docs/WorldExpansion/ecology-v5-layout.json` and `ecology-v5-integration.json`.

## Passive performance

City viewpoint: 1,200 editor world-frame samples; mean 16.67 ms, p95 16.88 ms, max 17.53 ms.

Diagnostics run during traversal are excluded from performance interpretation. Passive measurements represent their recorded editor viewpoint and include editor overhead.

## Preservation and scope

The original homestead baseline is never overwritten. V5 before/admitted/reopened snapshots live in this folder. Retiring coarse regional meshes or moving regional forest roots is allowed; original pilot mesh-instance signatures and original map bytes remain protected. Historical receipts remain intact; the previous review/captures are backed up under `Before/`, and the current WorldExpansion review URL opens this V5 result.

The changed terrain uses its actual visible LOD inventory; no unobserved LOD transitions or world streaming are implied. Full regional navigation, NPC simulation and physical hardware input acceptance remain separate work.
