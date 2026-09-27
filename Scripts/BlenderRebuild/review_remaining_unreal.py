"""Stage this batch in its own saved review map; preserve the homestead map."""
import unreal,json,hashlib
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
out=root/'Docs/BlenderRebuild/RemainingBatch';out.mkdir(exist_ok=True)
original=root/'Content/Terrarium/Blender/Maps/HomesteadBlender.umap'
before=hashlib.sha256(original.read_bytes()).hexdigest()
path='/Game/Terrarium/Blender/Maps/RemainingModelsReview'
assert not unreal.EditorAssetLibrary.does_asset_exist(path),'Existing review map must be inspected, not replaced'
assert not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages(),'Unsaved map changes; leave intact'
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert levels.new_level(path)
def spawn(cls,label,loc=(0,0,0)):
    a=actors.spawn_actor_from_class(cls,unreal.Vector(*loc));a.set_actor_label(label);return a
rows=[]
for key,x in [('Kindlehorn',-510),('Rillip',-190),('Player',120),('RangerSela',410)]:
    mesh=unreal.load_asset('/Game/Terrarium/Blender/'+key+'/SM_Blender_'+key);assert mesh
    a=spawn(unreal.StaticMeshActor,'Review_'+key,(x,220,0));a.static_mesh_component.set_static_mesh(mesh)
    rows.append({'asset':key,'actor':a.get_actor_label(),'mesh':mesh.get_path_name(),'material_count':len(mesh.static_materials),'location':[x,220,0]})
mesh=unreal.load_asset('/Game/Terrarium/Blender/HomesteadCompound/SM_Blender_HomesteadCompound');assert mesh
a=spawn(unreal.StaticMeshActor,'Review_HomesteadCompound',(0,-460,0));a.static_mesh_component.set_static_mesh(mesh);a.set_actor_scale3d(unreal.Vector(.72,.72,.72))
rows.append({'asset':'HomesteadCompound','actor':a.get_actor_label(),'mesh':mesh.get_path_name(),'material_count':len(mesh.static_materials),'location':[0,-460,0],'scale':.72})
floor=spawn(unreal.StaticMeshActor,'Review_Ground',(0,-180,-12));floor.static_mesh_component.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube'));floor.set_actor_scale3d(unreal.Vector(18,16,.2))
floor.static_mesh_component.set_material(0,unreal.load_asset('/Game/Terrarium/Materials/M_Baseline_Tan'))
sun=spawn(unreal.DirectionalLight,'Review_Sun');sun.set_actor_rotation(unreal.Rotator(pitch=-48,yaw=-45,roll=0),False);sun.light_component.set_mobility(unreal.ComponentMobility.MOVABLE);sun.light_component.set_intensity(30000);sun.light_component.set_editor_property('light_source_angle',6.0);sun.light_component.set_editor_property('atmosphere_sun_light',True)
spawn(unreal.SkyAtmosphere,'Review_Atmosphere')
sky=spawn(unreal.SkyLight,'Review_Fill');sky.light_component.set_mobility(unreal.ComponentMobility.MOVABLE);sky.light_component.set_editor_property('real_time_capture',True);sky.light_component.set_intensity(2)
pp=spawn(unreal.PostProcessVolume,'Review_Exposure');pp.set_editor_property('unbound',True);settings=pp.get_editor_property('settings')
for k,v in [('auto_exposure_method',unreal.AutoExposureMethod.AEM_MANUAL),('auto_exposure_apply_physical_camera_exposure',True),('camera_iso',100.),('camera_shutter_speed',64.),('depth_of_field_fstop',8.),('auto_exposure_bias',0.),('motion_blur_amount',0.),('vignette_intensity',0.)]:
    settings.set_editor_property('override_'+k,True);settings.set_editor_property(k,v)
pp.set_editor_property('settings',settings)
cam=spawn(unreal.CameraActor,'Review_Camera',(1100,1800,1500));focus=unreal.Vector(0,-170,110);cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(cam.get_actor_location(),focus),False)
cc=cam.camera_component;cc.set_projection_mode(unreal.CameraProjectionMode.ORTHOGRAPHIC);cc.set_ortho_width(1900);cc.set_editor_property('aspect_ratio',1.5);cc.set_editor_property('constrain_aspect_ratio',True);cc.set_editor_property('post_process_blend_weight',0.)
levels.pilot_level_actor(cam);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);actors.set_selected_level_actors([])
assert levels.save_current_level();levels.eject_pilot_level_actor();assert levels.load_level(path)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
for row in rows:
    ob=scene[row['actor']];assert ob.static_mesh_component.static_mesh.get_path_name()==row['mesh']
    assert all(ob.static_mesh_component.get_material(i) for i in range(row['material_count']))
cam=scene['Review_Camera'];levels.pilot_level_actor(cam);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
p=cam.get_actor_location();r=cam.get_actor_rotation()
args={'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll},'scale':{'x':1,'y':1,'z':1}},'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
(root/'Saved/remaining-batch-capture.json').write_text(json.dumps(args))
after=hashlib.sha256(original.read_bytes()).hexdigest();assert before==after
(out/'unreal-verification.json').write_text(json.dumps({'project':str(root),'engine':unreal.SystemLibrary.get_engine_version(),'map':path,'saved_and_reopened':True,'actors':rows,'homestead_map_sha256_before':before,'homestead_map_sha256_after':after,'homestead_map_unchanged':True,'animation_tested':False},indent=2))
