"""Create a separate native showcase map for the complete homestead assembly."""
import unreal,sys,gc
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir());sys.path.insert(0,str(root/'Scripts/Fidelity'));import reference as ref
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert '/HomesteadFidelity.' in str(levels.get_current_level())
levels.eject_pilot_level_actor()
for a in list(actors.get_all_level_actors()):
    if a.get_actor_label()=='HouseFence_Review_Transient':actors.destroy_actor(a)
world=None;a=None;review=None;camera=None;baseline=None;gc.collect()
assert levels.save_current_level()
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
assert unreal.EditorLoadingAndSavingUtils.save_map(world,'/Game/Terrarium/Maps/HomesteadAssemblyReview')
world=None
assert levels.load_level('/Game/Terrarium/Maps/HomesteadAssemblyReview')
for a in list(actors.get_all_level_actors()):
    keep=a.get_actor_label().startswith(('Assembly_','AssemblyFence_')) or isinstance(a,(unreal.DirectionalLight,unreal.SkyLight,unreal.PostProcessVolume,unreal.CameraActor))
    if not keep:actors.destroy_actor(a)
path='/Game/Terrarium/Materials/M_AssemblyReviewGround';mat=unreal.load_asset(path)
if not mat:
    mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_AssemblyReviewGround','/Game/Terrarium/Materials',unreal.Material,unreal.MaterialFactoryNew())
    lib=unreal.MaterialEditingLibrary
    color=lib.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,0,0)
    color.set_editor_property('constant',unreal.LinearColor(.12,.135,.12,1))
    lib.connect_material_property(color,'',unreal.MaterialProperty.MP_BASE_COLOR)
    rough=lib.create_material_expression(mat,unreal.MaterialExpressionConstant,0,150);rough.set_editor_property('r',1)
    lib.connect_material_property(rough,'',unreal.MaterialProperty.MP_ROUGHNESS)
    lib.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)
floor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,568))
floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Plane.Plane'))
floor.static_mesh_component.set_material(0,mat);floor.set_actor_scale3d(unreal.Vector(80,80,1));floor.set_actor_label('Assembly_ReviewGround')
baseline=next(a for a in actors.get_all_level_actors() if a.get_actor_label()=='Baseline_Orthographic_Review')
review=actors.spawn_actor_from_class(unreal.CameraActor,baseline.get_actor_location()+unreal.Vector(*ref.world(260,316,0)),baseline.get_actor_rotation())
review.set_actor_label('Assembly_ReviewCamera');review.camera_component.set_projection_mode(unreal.CameraProjectionMode.ORTHOGRAPHIC)
review.camera_component.set_ortho_width(2200);review.camera_component.set_editor_property('aspect_ratio',1.5)
levels.pilot_level_actor(review);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
assert levels.save_current_level()
task=unreal.AutomationLibrary.take_high_res_screenshot(1500,1000,str(root/'Docs/HomesteadAssembly/assembly.png'),camera=review,delay=1)
assert task
unreal.log('ASSEMBLY_REVIEW_MAP_SAVED')
