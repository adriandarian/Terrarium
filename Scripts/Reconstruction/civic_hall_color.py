"""Civic hall only: preserve R3 geometry and give R4 a warmer material palette.

Execute through the verified Terrarium editor. Original vertex colors remain
intact, so the material adjustment is reversible without rebuilding geometry.
"""
import hashlib
import json
from pathlib import Path
import unreal

assert Path(unreal.Paths.get_project_file_path()).name == 'Terrarium.uproject'
ROOT = Path(unreal.Paths.project_dir())
PKG = '/Game/Terrarium/Reconstruction'
NAME = 'SM_Recon_CivicHall_R4'
MATERIAL = PKG + '/Materials/M_CivicHall_Warm_R4'

# Inputs are linear vertex colors. Each original material family has a distinct
# hue/value range; retain its per-block variation rather than flattening it.
PALETTE_CODE = '''
float3 c = Color;
if (c.g > c.r * 1.45 && c.b > c.g * 0.45)
    return c * float3(0.75, 0.55, 0.50); // deep green teal glass and door
if (c.r > 0.58 && c.g > 0.42 && c.b > 0.22)
    return c * float3(1.00, 0.96, 0.88); // warm ivory plaster and arch
if (c.r > 0.15 && c.b > 0.13 && c.g > c.r * 0.80)
    return c * float3(0.70, 0.69, 0.66); // warm gray limestone
if (c.g > c.r * 0.95 && c.b < c.g * 0.35)
    return c * float3(0.70, 0.65, 0.48); // muted olive moss
if (c.r > 0.50 && c.g > c.r * 0.40 && c.b < c.r * 0.12)
    return c; // preserve brass and amber accents
if (c.r > 0.28 && c.g < c.r * 0.60 && c.b < c.r * 0.30)
    return c * float3(0.86, 0.66, 0.53); // richer red terracotta
if (c.r < 0.28 && c.r > c.g * 1.20)
    return c * float3(0.55, 0.52, 0.48); // dark chestnut framing
return c;
'''


def apply():
    lib = unreal.MaterialEditingLibrary
    mat = unreal.load_asset(MATERIAL) if unreal.EditorAssetLibrary.does_asset_exist(MATERIAL) else None
    if mat is None:
        mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            'M_CivicHall_Warm_R4', PKG + '/Materials', unreal.Material, unreal.MaterialFactoryNew())
    lib.delete_all_material_expressions(mat)
    vc = lib.create_material_expression(mat, unreal.MaterialExpressionVertexColor, -500, 0)
    custom = lib.create_material_expression(mat, unreal.MaterialExpressionCustom, -250, 0)
    custom.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)
    pin = unreal.CustomInput()
    pin.set_editor_property('input_name', 'Color')
    custom.set_editor_property('inputs', [pin])
    custom.set_editor_property('code', PALETTE_CODE)
    assert lib.connect_material_expressions(vc, '', custom, 'Color')
    assert lib.connect_material_property(custom, '', unreal.MaterialProperty.MP_BASE_COLOR)
    for prop, value, y in [(unreal.MaterialProperty.MP_ROUGHNESS, .93, 150),
                           (unreal.MaterialProperty.MP_SPECULAR, .1, 260)]:
        n = lib.create_material_expression(mat, unreal.MaterialExpressionConstant, -250, y)
        n.set_editor_property('r', value)
        assert lib.connect_material_property(n, '', prop)
    lib.recompile_material(mat)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
    source = PKG + '/Meshes/SM_Recon_CivicHall_R3'
    target = PKG + '/Meshes/' + NAME
    mesh = unreal.load_asset(target) if unreal.EditorAssetLibrary.does_asset_exist(target) else unreal.EditorAssetLibrary.duplicate_asset(source, target)
    assert mesh
    mesh.set_material(0, mat)
    assert unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    receipt = json.loads((ROOT / 'Docs/Reconstruction/Builds/SM_Recon_CivicHall_R3.json').read_text())
    receipt.update(name=NAME, asset=target, revision=4, source_geometry_asset=source,
                   geometry_change='none; editor duplicate of R3 with dedicated material',
                   material=MATERIAL, color_recipe='Scripts/Reconstruction/civic_hall_color.py',
                   color_recipe_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   visual_acceptance='pending_user_review_warm_palette',
                   visual_review_document='Docs/Reconstruction/civic-hall-color-review.md')
    receipt.pop('seconds', None)
    (ROOT / 'Docs/Reconstruction/Builds' / (NAME + '.json')).write_text(json.dumps(receipt, indent=2))
    unreal.log('CIVIC_HALL_WARM_MATERIAL_SAVED ' + target)


if __name__ == '__main__':
    apply()
