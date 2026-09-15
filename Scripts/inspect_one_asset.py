"""Place just one saved mesh under the Phase 0 rig for a requested review angle."""
import unreal,json,math
from pathlib import Path
assert 'Terrarium.uproject' in unreal.Paths.get_project_file_path()
assert '/ModularGallery.' in str(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level())
request=json.loads(Path(unreal.Paths.project_saved_dir(),'inspect-request.json').read_text())
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).eject_pilot_level_actor()
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
scene={a.get_actor_label():a for a in actors.get_all_level_actors()}
name=request['asset'];sm=unreal.load_asset('/Game/Terrarium/Meshes/'+name)
assert sm
actor=scene.get('Asset_Inspection')
if not actor:
 actor=actors.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector())
 actor.set_actor_label('Asset_Inspection')
actor.static_mesh_component.set_static_mesh(sm)
actor.set_actor_location(unreal.Vector(),False,False)
actor.set_actor_rotation(unreal.Rotator(),False)
actor.set_actor_hidden_in_game(False)
actor.set_is_temporarily_hidden_in_editor(False)
origin,extent=actor.get_actor_bounds(False)
scene['Baseline_Ground'].set_actor_location(unreal.Vector(0,0,min(0,origin.z-extent.z)-50),False,False)
radius=max(extent.x,extent.y,extent.z)
pitch=request.get('pitch',-32);yaw=request.get('yaw',135)
r=math.radians(yaw);p=math.radians(pitch);distance=radius*5+500
direction=unreal.Vector(math.cos(p)*math.cos(r),math.cos(p)*math.sin(r),math.sin(p))
camera=scene['Baseline_Orthographic_Review']
camera.set_actor_location(origin-direction*distance,False,False)
camera.set_actor_rotation(unreal.Rotator(pitch=pitch,yaw=yaw,roll=0),False)
camera.camera_component.set_ortho_width(radius*3.6+120)
camera.camera_component.set_editor_property('aspect_ratio',1.25)
levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
levels.pilot_level_actor(camera);levels.set_exact_camera_view(True);levels.editor_set_game_view(True)
actors.set_selected_level_actors([])
levels.editor_invalidate_viewports()
unreal.log('ASSET_REVIEW_POSE '+str(request)+' '+str(camera.get_actor_rotation()))
if request.get('output'):
    filename=str(Path(request['output']).resolve())
    task=unreal.AutomationLibrary.take_high_res_screenshot(800,640,filename,camera=camera,delay=0.5)
    assert task
