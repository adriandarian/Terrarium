# Proposed scale and detail correction plan

Status: proposed plan for review, not an approved visual specification. No scene or model changes were made while preparing this plan.

## Problem

The existing scene mixes incorrect relative object sizes, overly coarse geometric steps, and inconsistent surface detail. These are separate controls. Actor scaling cannot correct all three. Smaller triangles or larger textures alone will not change a chunky silhouette.

Current source evidence: HomesteadTree uses canopy blocks around 0.235 m before placement scaling. Cottage splits roof steps into smaller tiles while explicitly retaining the larger stepped courses. Asset helpers map the same atlas patch over faces of different physical sizes. CliffColumn is a 1 x 1 x 3.235 m placement module; its module dimensions are distinct from its smaller surface stones.

## Reference and measurement rules

- Use the full homestead concept as the authority for composition, relative scale, and visible detail density. Individual asset references guide identity without overriding the scene composition.
- Use one fixed camera and matching image crop for comparisons. Check the existing projection once; freeze it after calibration.
- Record projected footprint, visible height, ground contact, and spacing for the cottage, person, shed, fence, trees, cliffs, wheat, stairs, path, and bridge.
- World dimensions are chosen consistently from those relationships; a single concept image cannot establish exact real-world dimensions.
- Keep overall asset dimensions, construction-feature sizes, and texture detail independently adjustable.

## Work sequence and review gates

1. **Scale blockout.** In a separate revision level, replace the principal silhouettes temporarily with simple shapes. Match terrace heights, house/person ratio, canopy width, field area, path width, bridge width and span. Produce an overlay plus a measurement sheet. Review this before detailed rebuilding. As an initial tolerance, aim for major projected sizes within about 5–10% of the agreed reference measurements; this is a proposed check, not a current result.

2. **Detail calibration group.** Build one cliff corner with a grass cap, one cottage roof-and-wall section, one fence span, one bridge section, and one tree, alongside a person for scale. Keep outside dimensions fixed. Compare the current feature size with half-size and roughly third-size construction features where appropriate. Change the actual form, spacing, joints and silhouette; do not just subdivide the same blocks. Review at the full concept framing and a consistent close-up. Select the coarsest construction that reproduces the reference's visible shapes without losing required details.

3. **Authoring rules.** Record chosen feature sizes by material/asset family, surface texture density, edge treatment, and export units. Avoid imposing one identical cube size on leaves, masonry, roof tiles and small props. Merge hidden internal geometry and use repeated modules where useful. Keep the editable Blender sources and stable base pivots. Increasing detail must not mean emitting every hidden voxel face.

4. **Rebuild by visual impact.** Correct terrain silhouettes and cliff courses; cottage, shed and fences; bridge and stairs; tree crowns and shrub groups; wheat and garden; then characters and small props. Preserve approved overall dimensions when refining detail. Test each useful batch in Unreal with adjacent assets. Limit individual asset refinement to three passes and record unresolved issues rather than repeatedly polishing a single model.

5. **Compose and finish.** Rebuild foliage distribution around deliberate clusters and quiet ground. Fit the wheat footprint and worn path edges. Keep additional collection models in the wider world where they do not intrude into the concept view. Tune olive greens, weathered stone, terracotta, water and soft lighting after geometry and scale hold together. Cap broad scene refinement at five passes.

6. **Validate.** Compare the complete frame and fixed crops against the original at the same framing. Check projected dimensions and feature counts, materials, normals, ground support and contacts. Save and reopen Blender sources and the Unreal level. Inspect detail stability while moving the editor camera and record representative performance before/after. Separate visual approval from technical validation and model coverage.

## First implementation milestone

Deliver the measured blockout and the small detail calibration group, with side-by-side evidence. Do not rebuild all 31 model families until the scale relationships and construction density have been reviewed. Preserve the current scene and existing model sources as the baseline.

## Completion criteria

The result must match the concept's relative silhouettes, spacing, visible construction scale and material character from the agreed camera. Asset presence, valid imports, high polygon counts and successful saves are necessary checks but do not establish visual similarity.
