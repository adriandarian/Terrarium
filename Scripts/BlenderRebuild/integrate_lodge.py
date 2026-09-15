"""Place the Blender lodge on the verified empty upper terrace."""
import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).resolve();assert root==Path('C:/Users/hello/Projects/Terrarium')
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem);actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world_path='/Game/Terrarium/Blender/Maps/HomesteadBlender';assert world_path+'.' in str(levels.get_current_level())
scene={a.get_actor_label():a for a in actors.get_all_level_actors()};key='Lodge';folder=root/'Docs/BlenderRebuild'/key
mesh=unreal.load_asset('/Game/Terrarium/Blender/Lodge/SM_Blender_Lodge');assert mesh
body=mesh.get_editor_property('body_setup');body.set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
unreal.EditorAssetLibrary.save_loaded_asset(mesh)
pos=(-2170,-140,880);scale=.85;label='Blender_Lodge_UpperTerrace'
ob=scene.get(label) or actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*pos));ob.set_actor_label(label)
ob.static_mesh_component.set_static_mesh(mesh);ob.static_mesh_component.set_editor_property('override_materials',[])
ob.set_actor_location(unreal.Vector(*pos),False,False);ob.set_actor_scale3d(unreal.Vector(scale,scale,scale));ob.set_actor_rotation(unreal.Rotator(pitch=0,yaw=-90,roll=0),False)
ob.tags=[unreal.Name('BlenderRebuild'),unreal.Name('FidelityReviewPending')]
center,extent=ob.get_actor_bounds(False)
assert abs(center.z-extent.z-880)<.02
# Scene mesh components at this site contain terrain only; preserve all instancing.
camera=scene.get('Blender_Lodge_Review') or actors.spawn_actor_from_class(unreal.CameraActor,unreal.Vector())
camera.set_actor_label('Blender_Lodge_Review');focus=unreal.Vector(center.x,center.y,center.z)
camera.set_actor_location(focus+unreal.Vector(1850,675,880),False,False);camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),focus),False)
c=camera.get_component_by_class(unreal.CameraComponent);c.set_editor_property('projection_mode',unreal.CameraProjectionMode.PERSPECTIVE);c.set_editor_property('field_of_view',32)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True);assert levels.save_current_level()
record={'asset':key,'actor':label,'mesh':mesh.get_path_name(),'location_cm':list(pos),'scale':scale,'yaw':-90,'bounds_center':[center.x,center.y,center.z],'bounds_extent':[extent.x,extent.y,extent.z],'world':world_path,'collision':'complex_as_simple','status':'placed_pending_visual_check','site':'Empty upper terrace; existing cottage and wheat field retained'}
(folder/'world-placement.json').write_text(json.dumps(record,indent=2))
p=camera.get_actor_location();r=camera.get_actor_rotation()
args={'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll},'scale':{'x':1,'y':1,'z':1}},'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
(root/'Saved/blender-lodge-capture.json').write_text(json.dumps(args))
