"""Integrate rebuilt assets in a new reference map; preserve the preceding map."""
import unreal,json,sys
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());out=root/'Docs/Environment';out.mkdir(exist_ok=True)
sys.path.insert(0,str(root/'Scripts/Fidelity'));import reference as ref
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
target='/Game/Terrarium/Maps/HomesteadReference'
assert not unreal.EditorAssetLibrary.does_asset_exist(target),'Use a refinement script for an existing assembly'
levels.eject_pilot_level_actor();assert '/HomesteadFidelity.' in str(levels.get_current_level())
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world,target)
world=None;assert levels.load_level(target)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
lib=unreal.MaterialEditingLibrary;at=unreal.AssetToolsHelpers.get_asset_tools()
mat=at.create_asset('M_EnvironmentPigment','/Game/Terrarium/Environment/Materials',unreal.Material,unreal.MaterialFactoryNew());assert mat
mat.set_editor_property('used_with_instanced_static_meshes',True)
v=lib.create_material_expression(mat,unreal.MaterialExpressionVertexColor,-200,0)
assert lib.connect_material_property(v,'',unreal.MaterialProperty.MP_BASE_COLOR)
for prop,value,y in [(unreal.MaterialProperty.MP_ROUGHNESS,.98,140),(unreal.MaterialProperty.MP_SPECULAR,.06,260)]:
    c=lib.create_material_expression(mat,unreal.MaterialExpressionConstant,-200,y);c.set_editor_property('r',value);lib.connect_material_property(c,'',prop)
lib.recompile_material(mat);assert unreal.EditorAssetLibrary.save_loaded_asset(mat)
changes=[]
def replace_instances(old,new,fit_height=False):
    jobs=[];oldmesh=unreal.load_asset('/Game/Terrarium/Meshes/'+old);mesh=unreal.load_asset(new);assert mesh
    factor=oldmesh.get_bounds().box_extent.z/mesh.get_bounds().box_extent.z if fit_height else 1.0
    for a in actors.get_all_level_actors():
        for c in a.get_components_by_class(unreal.FoliageInstancedStaticMeshComponent):
            if c.static_mesh and c.static_mesh.get_name()==old:
                for i in range(c.get_instance_count()):
                    t=c.get_instance_transform(i,world_space=True)
                    if fit_height:t.scale3d=t.scale3d*factor
                    jobs.append(t)
    assert jobs,old
    oldft=unreal.load_asset('/Game/Terrarium/Foliage/FT_'+old.removeprefix('SM_'));assert oldft,old
    label='FT_Env_'+old.removeprefix('SM_')
    ft=at.create_asset(label,'/Game/Terrarium/Environment/Foliage',unreal.FoliageType_InstancedStaticMesh,unreal.FoliageType_InstancedStaticMeshFactory());assert ft
    ft.set_editor_property('mesh',mesh);ft.set_editor_property('override_materials',[mat]);assert unreal.EditorAssetLibrary.save_loaded_asset(ft)
    unreal.InstancedFoliageActor.remove_all_instances(world,oldft)
    unreal.InstancedFoliageActor.add_instances(world,ft,jobs)
    changes.append({'old':old,'new':new,'instances':len(jobs),'height_fit_factor':factor,'foliage_type':ft.get_path_name()})
for variant in 'ABC':replace_instances('SM_CliffColumn_v6'+variant+'_Detail','/Game/Terrarium/Meshes/SM_VoxelCliffStepped_'+variant)
replace_instances('SM_Tree_v3_Detail','/Game/Terrarium/Reconstruction/Meshes/SM_Recon_HomesteadTree_R3',True)
replace_instances('SM_Bush_v2_Detail','/Game/Terrarium/Reconstruction/Meshes/SM_Recon_MeadowShrub_R3',True)
for a in actors.get_all_level_actors():
    if isinstance(a,unreal.StaticMeshActor) and a.static_mesh_component.static_mesh and a.static_mesh_component.static_mesh.get_name()=='SM_Traveler_v2_Detail':
        a.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/Terrarium/Reconstruction/Meshes/SM_Recon_Player_R3'))
        a.static_mesh_component.set_material(0,mat);a.set_actor_scale3d(unreal.Vector(1,1,1));a.set_actor_rotation(unreal.Rotator(pitch=0,yaw=60,roll=0),False)
        a.set_actor_location(unreal.Vector(*ref.world(177,394,564)),False,False);a.set_actor_label('Reference_Player');a.set_folder_path('Reference/Characters')
        changes.append({'old':'SM_Traveler_v2_Detail','new':'SM_Recon_Player_R3','reference_feet_px':[177,394]})
camera=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([]);assert levels.save_current_level()
(out/'integration-stage1.json').write_text(json.dumps({'map':target,'prior_map':'/Game/Terrarium/Maps/HomesteadFidelity','changes':changes},indent=2))
unreal.log('REFERENCE_ENVIRONMENT_STAGE1_SAVED')
