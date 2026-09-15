"""Run in the verified Unreal editor; keep rendered references separate from materials."""
import json
from pathlib import Path
import unreal

assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
ROOT = Path(unreal.Paths.project_dir())
PACKAGE = '/Game/Terrarium/Migration'
LIB = unreal.MaterialEditingLibrary
ASSETS = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()

def master(reference):
    name = 'M_Reference' if reference else 'M_Surface'
    path = PACKAGE + '/Materials/' + name
    if ASSETS.does_asset_exist(path):
        return unreal.load_asset(path)
    mat = TOOLS.create_asset(name, PACKAGE + '/Materials', unreal.Material, unreal.MaterialFactoryNew())
    tex = LIB.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -350, 0)
    tex.set_editor_property('parameter_name', 'SourceColor')
    tex.set_editor_property('texture', unreal.load_asset('/Engine/EngineResources/DefaultTexture'))
    if reference:
        mat.set_editor_property('shading_model', unreal.MaterialShadingModel.MSM_UNLIT)
        mat.set_editor_property('two_sided', True)
    assert LIB.connect_material_property(tex, 'RGB', unreal.MaterialProperty.MP_EMISSIVE_COLOR if reference else unreal.MaterialProperty.MP_BASE_COLOR)
    if not reference:
        value = LIB.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -350, 200)
        value.set_editor_property('parameter_name', 'Roughness')
        value.set_editor_property('default_value', .88)
        assert LIB.connect_material_property(value, '', unreal.MaterialProperty.MP_ROUGHNESS)
    LIB.recompile_material(mat)
    ASSETS.save_loaded_asset(mat)
    return mat

def instance(name, texture, parent):
    path = PACKAGE + '/Materials/' + name
    if ASSETS.does_asset_exist(path):
        return path
    mat = TOOLS.create_asset(name, PACKAGE + '/Materials', unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    LIB.set_material_instance_parent(mat, parent)
    LIB.set_material_instance_texture_parameter_value(mat, 'SourceColor', texture)
    ASSETS.save_loaded_asset(mat)
    return path

report = []
for source in sorted((ROOT / 'SourceAssets/Voxel').glob('*.png')):
    name = 'T_' + source.stem
    path = PACKAGE + '/References/' + name
    if not ASSETS.does_asset_exist(path):
        task = unreal.AssetImportTask()
        for key, value in [('filename', str(source)), ('destination_path', PACKAGE + '/References'), ('destination_name', name), ('automated', True), ('replace_existing', False), ('save', True)]:
            task.set_editor_property(key, value)
        TOOLS.import_asset_tasks([task])
        assert task.get_editor_property('imported_object_paths'), str(source)
    texture = unreal.load_asset(path)
    assert isinstance(texture, unreal.Texture2D), path
    texture.set_editor_property('srgb', True)
    ASSETS.save_loaded_asset(texture)
    ref = instance('MI_Reference_' + source.stem, texture, master(True))
    surface = None
    if source.stem.startswith(('terrain_', 'cottage_plaster_', 'cottage_roof_tile_')):
        surface = instance('MI_Surface_' + source.stem, texture, master(False))
    report.append({'source': source.name, 'texture': path, 'reference_material': ref, 'surface_material': surface,
                   'material_status': 'source-color study; baked source lighting; no authored normal/ORM maps' if surface else 'original 2D reference only'})
(ROOT / 'Docs/AssetMigration/imported.json').write_text(json.dumps(report, indent=2))
unreal.log('MIGRATION_IMPORTED ' + str(len(report)))
