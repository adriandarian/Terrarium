"""Stage existing review camera or a transient viewport pose for native evidence."""
import json
from pathlib import Path
import unreal
root=Path(unreal.Paths.project_dir()).resolve()
assert root==Path('C:/Users/hello/Projects/Terrarium')
out=root/'Docs/HomesteadPilot/Completion'
request_path=out/'view-request.json'
request=json.loads(request_path.read_text()) if request_path.exists() else {'camera':'HP_ExplorationView'}
L=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
E=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
A=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
assert not E.get_game_world()
assert E.get_editor_world().get_path_name().split('.')[0]=='/Game/Terrarium/HomesteadPilot/Maps/StartingHome'
if 'new_camera' in request:
    label=request['new_camera']
    assert label.startswith('HP_Completion')
    camera=next((a for a in A.get_all_level_actors() if a.get_actor_label()==label),None)
    if not camera:
        camera=A.spawn_actor_from_class(unreal.CameraActor,unreal.Vector())
        camera.set_actor_label(label)
        camera.set_folder_path('HomesteadPilot/ReviewCameras')
    p=unreal.Vector(*request['position']);r=unreal.MathLibrary.find_look_at_rotation(p,unreal.Vector(*request['target']))
    camera.set_actor_location(p,False,False);camera.set_actor_rotation(r,False)
    camera.set_editor_property('auto_activate_for_player',unreal.AutoReceiveInput.DISABLED)
    camera.camera_component.set_projection_mode(unreal.CameraProjectionMode.PERSPECTIVE)
    camera.camera_component.set_field_of_view(request.get('fov',52))
    camera.camera_component.set_editor_property('post_process_blend_weight',0.)
    L.pilot_level_actor(camera);L.set_exact_camera_view(True)
elif 'camera' in request:
    camera=next(a for a in A.get_all_level_actors() if a.get_actor_label()==request['camera'])
    assert camera.get_auto_activate_player_index()==-1
    L.pilot_level_actor(camera)
    L.set_exact_camera_view(True)
    p=camera.get_actor_location();r=camera.get_actor_rotation()
else:
    L.eject_pilot_level_actor()
    p=unreal.Vector(*request['position']);r=unreal.MathLibrary.find_look_at_rotation(p,unreal.Vector(*request['target']))
    E.set_level_viewport_camera_info(p,r)
L.editor_set_game_view(True)
A.set_selected_level_actors([])
args={'captureTransform':{'location':{'x':p.x,'y':p.y,'z':p.z},'rotation':{'pitch':r.pitch,'yaw':r.yaw,'roll':r.roll},'scale':{'x':1,'y':1,'z':1}},'annotations':{'gridSpacing':0,'gridExtent':0,'gridHeight':0,'maxLabelDistance':0,'classFilter':{'refPath':'/Script/Engine.Actor'},'maxLabels':0},'bShowUI':False}
(out/'capture-request.json').write_text(json.dumps(args))
