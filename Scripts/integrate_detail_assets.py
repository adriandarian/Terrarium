"""Replace all 32 scene asset types while keeping soft materials and placements."""
import unreal,json
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/DetailPass'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
camera=None;world=None
levels.eject_pilot_level_actor()
if '/HomesteadFidelity.' not in str(levels.get_current_level()):
    assert levels.load_level('/Game/Terrarium/Maps/HomesteadFidelity')
assert '/HomesteadFidelity.' in str(levels.get_current_level())
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
manifest=json.loads((out/'assets.json').read_text())
assert len(manifest)==32
mapping={r['original']:r['asset'] for r in manifest}
baseline=json.loads((out/'restored.json').read_text())
ground_path='/Game/Terrarium/Materials/M_DetailGround'
ground=unreal.load_asset(ground_path)
if not ground:
    ground=unreal.EditorAssetLibrary.duplicate_asset('/Game/Terrarium/Materials/M_Pass7_Ground',ground_path)
if not isinstance(unreal.MaterialEditingLibrary.get_material_property_input_node(ground,unreal.MaterialProperty.MP_BASE_COLOR),unreal.MaterialExpressionLinearInterpolate):
    lib=unreal.MaterialEditingLibrary
    source=lib.get_material_property_input_node(ground,unreal.MaterialProperty.MP_BASE_COLOR)
    source_output=lib.get_material_property_input_node_output_name(ground,unreal.MaterialProperty.MP_BASE_COLOR)
    vertex=lib.create_material_expression(ground,unreal.MaterialExpressionVertexColor,640,-750)
    blend=lib.create_material_expression(ground,unreal.MaterialExpressionLinearInterpolate,850,-400)
    blend.set_editor_property('const_alpha',.32)
    assert lib.connect_material_expressions(source,source_output,blend,'A')
    assert lib.connect_material_expressions(vertex,'',blend,'B')
    assert lib.connect_material_property(blend,'',unreal.MaterialProperty.MP_BASE_COLOR)
    ground.set_editor_property('used_with_instanced_static_meshes',True)
    lib.recompile_material(ground)
    assert unreal.EditorAssetLibrary.save_loaded_asset(ground)
jobs=[];report={}
for a in actors.get_all_level_actors():
    for c in a.get_components_by_class(unreal.StaticMeshComponent):
        if not c.static_mesh:continue
        old=c.static_mesh.get_name()
        if old not in mapping:continue
        n=c.get_instance_count() if isinstance(c,unreal.InstancedStaticMeshComponent) else 1
        if not n:continue
        material=ground if 'MeadowTile' in old else unreal.load_asset(baseline['materials'][old])
        mesh=unreal.load_asset('/Game/Terrarium/Meshes/'+mapping[old]);assert mesh
        if isinstance(c,unreal.FoliageInstancedStaticMeshComponent):
            jobs.append((old,mesh,material,[c.get_instance_transform(i,world_space=True) for i in range(n)]))
        else:
            c.set_static_mesh(mesh);c.set_material(0,material)
        report[old]={'mesh':mapping[old],'instances':n,'material':material.get_path_name()}
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
for old,mesh,material,transforms in jobs:
    source=unreal.load_asset('/Game/Terrarium/Foliage/FT_'+old[3:]);assert source
    target='/Game/Terrarium/Foliage/FT_'+mesh.get_name()[3:]
    ft=unreal.load_asset(target)
    if not ft:ft=unreal.EditorAssetLibrary.duplicate_asset(source.get_path_name(),target)
    ft.set_editor_property('mesh',mesh)
    ft.set_editor_property('override_materials',[material])
    assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
    unreal.InstancedFoliageActor.remove_all_instances(world,source)
    unreal.InstancedFoliageActor.add_instances(world,ft,transforms)
world=None
assert set(report)==set(mapping),(set(mapping)-set(report))
assert all(report[k]['instances']==baseline['counts'][k] for k in mapping)
assert levels.save_current_level()
(out/'integration.json').write_text(json.dumps(report,indent=2))
unreal.log('ALL_32_DETAIL_ASSETS_INTEGRATED')
