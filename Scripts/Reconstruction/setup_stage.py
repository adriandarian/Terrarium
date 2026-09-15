"""Create an isolated neutral studio for source-accuracy checks, in Terrarium."""
import json
from pathlib import Path
import unreal
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
root=Path(unreal.Paths.project_dir()); out=root/'Docs/Reconstruction';out.mkdir(parents=True,exist_ok=True)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
path='/Game/Terrarium/Reconstruction/Maps/ReviewStage'
assert not unreal.EditorAssetLibrary.does_asset_exist(path)
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages(), 'Save editor work before stage creation'
levels.eject_pilot_level_actor();assert levels.new_level(path)
def spawn(cls,label,pos=(0,0,0),rot=(0,0,0)):
    a=actors.spawn_actor_from_class(cls,unreal.Vector(*pos),unreal.Rotator(pitch=rot[0],yaw=rot[1],roll=rot[2]));a.set_actor_label(label);return a
tools=unreal.AssetToolsHelpers.get_asset_tools();lib=unreal.MaterialEditingLibrary
mat=tools.create_asset('M_StudioFloor','/Game/Terrarium/Reconstruction/Materials',unreal.Material,unreal.MaterialFactoryNew())
node=lib.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector,-200,0);node.set_editor_property('constant',unreal.LinearColor(.11,.12,.13,1));lib.connect_material_property(node,'',unreal.MaterialProperty.MP_BASE_COLOR)
n=lib.create_material_expression(mat,unreal.MaterialExpressionConstant,-200,150);n.set_editor_property('r',.85);lib.connect_material_property(n,'',unreal.MaterialProperty.MP_ROUGHNESS);lib.recompile_material(mat);unreal.EditorAssetLibrary.save_loaded_asset(mat)
floor=spawn(unreal.StaticMeshActor,'StudioFloor',(0,0,-12));floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.static_mesh_component.set_material(0,mat);floor.set_actor_scale3d(unreal.Vector(150,150,.2))
for name,intensity,rot,rgb in [('Key',4.0,(-42,115,0),(1,.91,.78)),('Fill',1.0,(-25,-55,0),(.74,.86,1)),('Rim',2.0,(-50,-145,0),(1,.98,.90))]:
    a=spawn(unreal.DirectionalLight,'Studio'+name,(0,0,700),rot);a.light_component.set_mobility(unreal.ComponentMobility.MOVABLE);a.light_component.set_intensity(intensity);a.light_component.set_light_color(unreal.LinearColor(*rgb,1));a.light_component.set_editor_property('light_source_angle',4.0)
pp=spawn(unreal.PostProcessVolume,'StudioExposure');pp.set_editor_property('unbound',True)
s=pp.get_editor_property('settings')
for key,value in [('auto_exposure_method',unreal.AutoExposureMethod.AEM_MANUAL),('auto_exposure_apply_physical_camera_exposure',False),('auto_exposure_bias',0.0),('motion_blur_amount',0.0),('bloom_intensity',0.0),('vignette_intensity',0.0),('ambient_occlusion_intensity',.6),('ambient_occlusion_radius',20.0)]:
    s.set_editor_property('override_'+key,True);s.set_editor_property(key,value)
pp.set_editor_property('settings',s)
a=spawn(unreal.StaticMeshActor,'ReviewModel');a.static_mesh_component.set_static_mesh(unreal.load_asset('/Game/Terrarium/Migration/Meshes/SM_PlayerExplorer'))
assert levels.save_current_level()
(out/'stage.json').write_text(json.dumps({'map':path,'project':unreal.Paths.get_project_file_path(),'render':'deferred studio lights; fixed nonphysical manual exposure'},indent=2))
